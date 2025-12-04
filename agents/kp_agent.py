from typing import Dict, List, Any, TypedDict, Annotated, Literal
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
import os
import random
import json
import re
from dotenv import load_dotenv
from agents.scenes import SCENES, get_scene_prompt, get_available_transitions, get_story_overview
from agents.memory import compress_chat_history

# Load environment variables from .env file
load_dotenv()


class AgentState(TypedDict, total=False):
	messages: Annotated[List[BaseMessage], "Chat history"]
	character: Dict[str, Any]
	api_key: str
	current_scene: str  # Current scene ID
	scene_history: Annotated[List[str], "History of visited scenes"]
	dice_results: Annotated[List[Dict[str, Any]], "History of dice rolls"]
	next_action: str  # Keeper's decision: "continue", "roll_dice", "san_check", "change_scene"
	next_scene: str  # Target scene if changing scenes
	san_loss: int  # SAN loss from san_check
	pending_dice_result: str  # Pending dice result to include in response
	pending_san_result: str  # Pending SAN check result to include in response


# ==================== DICE TOOL ====================

def process_dice_result(d100: int, skill_name: str, difficulty: str, skill_value: int) -> str:
	"""
	Process a dice roll result and return formatted result string.
	
	Args:
		d100: The actual dice roll result (1-100)
		skill_name: Name of the skill being tested
		difficulty: Difficulty level
		skill_value: The character's skill or attribute value
	
	Returns:
		Formatted result string
	"""
	# Calculate difficulty thresholds
	if difficulty == "easy":
		threshold = skill_value // 2
		diff_name = "Easy"
	elif difficulty == "hard":
		threshold = skill_value // 2
		diff_name = "Hard"
	elif difficulty == "extreme":
		threshold = skill_value // 5
		diff_name = "Extreme"
	else:  # normal
		threshold = skill_value
		diff_name = "Normal"
	
	# Determine result
	if d100 == 1:
		result_type = "Critical Success"
		success = True
	elif d100 == 100:
		result_type = "Fumble"
		success = False
	elif d100 <= threshold:
		result_type = "Success"
		success = True
	else:
		result_type = "Failure"
		success = False
	
	# Special: Extreme success if roll <= 1/5th of threshold
	if success and d100 <= (threshold // 5):
		result_type = "Extreme Success"
	
	result_str = f"[{skill_name} Check - {diff_name}]\n"
	result_str += f"Roll: {d100}/{threshold}\n"
	result_str += f"Result: **{result_type}**\n\n"
	
	if success:
		result_str += "You succeed in your attempt."
	else:
		result_str += "You fail in your attempt."
	
	return result_str


def process_san_check_result(d100: int, current_san: int, san_loss: int) -> tuple[str, int]:
	"""
	Process a SAN check result and return formatted result string and actual SAN loss.
	
	Args:
		d100: The actual dice roll result (1-100)
		current_san: The character's current Sanity value
		san_loss: Amount of SAN to lose if the check fails
	
	Returns:
		Tuple of (formatted result string, actual SAN loss)
	"""
	# SAN check: roll under current SAN to succeed (avoid loss)
	success = d100 <= current_san
	
	# Determine result type
	if d100 == 1:
		result_type = "Critical Success"
		actual_loss = 0  # No loss on critical success
	elif d100 == 100:
		result_type = "Fumble"
		actual_loss = san_loss * 2  # Double loss on fumble
	elif success:
		result_type = "Success"
		actual_loss = 0  # No loss on success
	else:
		result_type = "Failure"
		actual_loss = san_loss
	
	result_str = f"[Sanity Check]\n"
	result_str += f"Roll: {d100}/{current_san}\n"
	result_str += f"Result: **{result_type}**\n\n"
	
	if actual_loss > 0:
		new_san = current_san - actual_loss
		result_str += f"Your sanity crumbles. You lose {actual_loss} SAN."
		if new_san <= 0:
			result_str += f" Your SAN reaches 0—you have gone permanently insane."
		else:
			result_str += f" Your SAN is now {new_san}."
	else:
		result_str += f"You maintain your composure. No SAN loss."
	
	return result_str, actual_loss


@tool
def roll_dice(skill_name: str, difficulty: str = "normal", skill_value: int = 50) -> str:
	"""
	Request a skill check or attribute test. This tool returns a special marker
	that tells the frontend to display a dice roll button. The actual dice roll
	will be performed by the user on the frontend.
	
	Args:
		skill_name: Name of the skill being tested (e.g., "Spot Hidden", "Dodge", "Strength")
		difficulty: Difficulty level - "easy" (half value), "normal" (full value), "hard" (half value), "extreme" (fifth value)
		skill_value: The character's skill or attribute value
	
	Returns:
		Special marker string that triggers frontend dice roll UI
	"""
	# Return a special marker that the frontend will detect
	# Format: [DICE_REQUEST:skill_name:difficulty:skill_value]
	return f"[DICE_REQUEST:{skill_name}:{difficulty}:{skill_value}]"


@tool
def san_check(current_san: int, san_loss: int) -> str:
	"""
	Request a Sanity (SAN) check. This tool returns a special marker
	that tells the frontend to display a dice roll button. The actual dice roll
	will be performed by the user on the frontend.
	
	Args:
		current_san: The character's current Sanity value
		san_loss: Amount of SAN to lose if the check fails (typically 1-5, can be more for major horrors)
	
	Returns:
		Special marker string that triggers frontend dice roll UI
	"""
	# Return a special marker that the frontend will detect
	# Format: [SAN_CHECK_REQUEST:current_san:san_loss]
	return f"[SAN_CHECK_REQUEST:{current_san}:{san_loss}]"


@tool
def change_scene(target_scene_id: str, current_scene_id: str) -> str:
	"""
	Transition to a different scene in the story.
	
	Args:
		target_scene_id: The ID of the scene to transition to (e.g., "exploration_inn", "exploration_village", "exploration_church", "final_ritual", "ending")
		current_scene_id: The current scene ID
	
	Returns:
		Confirmation message about the scene transition
	"""
	from agents.scenes import SCENES, get_available_transitions
	
	# Validate transition
	available = get_available_transitions(current_scene_id)
	if target_scene_id not in available:
		return f"⚠️ Invalid scene transition: '{target_scene_id}' is not available from current scene '{current_scene_id}'. Available scenes: {', '.join(available) if available else 'none'}"
	
	if target_scene_id == current_scene_id:
		return f"ℹ️ Already in scene '{target_scene_id}'"
	
	# Get scene info
	scene_info = SCENES.get(target_scene_id, {})
	scene_name = scene_info.get("name", target_scene_id)
	
	return f"✓ Scene transition initiated: Moving from '{current_scene_id}' to '{target_scene_id}' ({scene_name})"


# ==================== GLOBAL SYSTEM PROMPT ====================

def build_global_system_prompt(character: Dict[str, Any], current_scene: str) -> str:
	"""Build the global system prompt for the Keeper"""
	name = character.get("name", "Investigator")
	background = character.get("background_story", "")
	str_val = character.get("str", 50)
	int_val = character.get("int", 50)
	pow_val = character.get("pow", 50)
	spot = character.get("spot", 50)
	listen = character.get("listen", 50)
	stealth = character.get("stealth", 50)
	charm = character.get("charm", 50)
	luck = character.get("luck", 50)
	san = character.get("san", 60)
	
	# Get story overview
	story_overview = get_story_overview()
	
	# Get current scene info
	scene_info = SCENES.get(current_scene, {})
	scene_name = scene_info.get("name", "Unknown Location")
	scene_description = scene_info.get("description", "")
	
	global_prompt = f"""You are the Keeper (KP) for a solo Call of Cthulhu role-playing game scenario.

{story_overview}

**Player Character:**
- Name: {name}
- Background: {background if background else "No specific background provided"}
- Core Attributes: STR {str_val}, INT {int_val}, POW {pow_val}
- Skills: SPOT {spot}, LISTEN {listen}, STEALTH {stealth}, CHARM {charm}, LUCK {luck}
- SAN: {san}

**Current Scene: {scene_name}**
{scene_description}

**Your Role as Keeper:**
- Narrate the story as the Keeper, responding directly to the investigator's actions
- Be concise and direct—avoid excessive atmospheric description
- Focus on what happens, not lengthy environmental details
- **When a skill check is needed, IMMEDIATELY call the roll_dice tool - do NOT announce or describe the check**
- Advance the story based on player actions
- Keep responses brief (1-3 sentences typically, only expand for crucial moments)
- Show, don't over-describe. Let actions and dialogue carry the atmosphere
- Avoid repetitive sensory details or purple prose
- **CRITICAL: Do NOT say "I will roll" or "Let me check" - just call the tool directly**

**Player Action Handling (Critical):**
- Never invent or describe the player's words or actions.
- Do not elaborate on, embellish, or expand the player's replies, nor add any internal thoughts or psychological descriptions for the player character.
- Only narrate NPC reactions, environment, and consequences.
- **If instructions are vague or unclear, ask for clarification (e.g., "What do you say?" "How do you do it?"). Otherwise, simply narrate what happens without ending with a question. Trust the player will respond with their next action.**

**Tool Usage Workflow:**
When player action requires a check:
1. **IMMEDIATELY and SILENTLY call the roll_dice or san_check tool** (do not announce it)
2. The tool will execute and return a result
3. Use that result in your narration without mentioning the tool call
4. Continue narrating based on the result


**Do:**
- Call the tool directly when needed
- Incorporate results naturally into narration
- Let tools work in the background

**When to use san_check:**
- Witness something horrifying or disturbing
- Encounter cosmic horror or supernatural phenomena
- See Cthulhu-related runes, symbols, or forbidden clues
- Discover disturbing truths or things that shouldn't exist
- Exposed to madness-inducing knowledge
- Typical SAN loss: 1 (minor), 1d3/1d4 (moderate), 1d6+ (major)

**Scene Transitions (CRITICAL):**
- Available transitions from current scene: {', '.join(get_available_transitions(current_scene))}
- You must treat scene changes as soon as the player clearly moves to a new location or starts interacting mainly in that new location.

**Skill Check Guidelines:**
- SPOT: Finding clues, noticing details, observing surroundings
- LISTEN: Hearing distant sounds, overhearing conversations, detecting threats
- STEALTH: Sneaking, hiding, moving quietly
- CHARM: Persuasion, negotiation, social interaction
- LUCK: Random events, chance encounters, fortunate coincidences
- STR: Physical actions, breaking objects, combat
- INT: Reasoning, remembering information, understanding clues
- POW: Resisting mental influence, magical resistance, willpower

**Critical Tool Usage Rules:**
- **NEVER describe or announce that you will perform a check - ALWAYS call the roll_dice tool directly**
- **DO NOT say "I will roll dice" or "I need to check" - just call the tool immediately**
- **When a skill check is needed, call roll_dice tool BEFORE responding - do not ask permission or describe the action**
- Use the correct skill name when calling roll_dice (e.g., "Spot Hidden" for SPOT checks, "Strength" for STR checks)
- After calling roll_dice, incorporate the result naturally into your narration without mentioning "I rolled" or "the dice show"

**Scene Transition Rules (for change_scene tool):**
- **CRITICAL:** When the player's actions clearly indicate moving to a new location or entering a different scene, you MUST call the change_scene tool BEFORE continuing narration.
- Only move to scenes that appear in the "Available scene transitions" list for the current scene.
- Treat "walking to / going to / entering / heading for / returning to" a place as a scene change intent, not just flavor.
- The player does **not** need to say the exact scene ID. You should map natural language places to scene IDs using your knowledge of the story.

**Concrete triggers (when to call change_scene immediately):**
- Player accepts May Ledbetter's offer and goes to or stays at May's house ⇒ call change_scene("leddbetter_house").
- Player says they go to or enter the village hall / town office / town hall ⇒ call change_scene("village_hall").
- Player says they go to or enter the ruined / abandoned church ⇒ call change_scene("ruined_church").
- Player says they go to the Beacon / festival / ritual location at night for the ceremony ⇒ call change_scene("ritual").
- From the ritual, when the story clearly reaches an epilogue / aftermath, you may move to "ending" ⇒ call change_scene("ending").

**Negative examples (DO NOT change scene):**
- Player only looks at a distant building, tower, or church from afar without going there.
- Player asks about a place in conversation but does not go there.
- Player remembers or dreams about another place.

**Execution rules:**
- Call change_scene as soon as you infer the scene change, then let the tools and system prompt update the context.
- After a successful change_scene, you must narrate from the new scene's perspective and tone.
- Do **not** ask the player "Do you want to go to X?" if they already clearly stated they go there—just change the scene.


**General Rules:**
- Stay in character as the KP and guide the story forward
- Be creative but stay within the CoC horror atmosphere
- Follow the scene-specific prompts provided to you for guidance on style and key elements
- Remember: You have tools available. Use them directly, don't describe using them.
"""

	return global_prompt


# ==================== NODES ====================

def keeper_node(state: AgentState) -> AgentState:
	"""Main Keeper node with LLM and tools"""
	messages: List[BaseMessage] = state["messages"]
	character: Dict[str, Any] = state["character"]
	api_key: str = state.get("api_key", "")
	current_scene: str = state.get("current_scene", "arrival_village")
	
	# Check if the last user message contains a DiceResult
	# Format: "DiceResult: 73" or "DiceResult: 73:skill_name:difficulty:skill_value" or "SANResult: 73:current_san:san_loss"
	pending_dice_result = None
	pending_san_result = None
	san_loss_amount = 0
	
	if messages and isinstance(messages[-1], HumanMessage):
		last_user_msg = messages[-1].content
		
		# Check for DiceResult pattern
		dice_result_match = re.match(r'DiceResult:\s*(\d{1,3})(?::(.+?):(.+?):(\d+))?', last_user_msg, re.IGNORECASE)
		if dice_result_match:
			d100 = int(dice_result_match.group(1))
			# If full parameters provided, use them; otherwise search backwards for the request
			if dice_result_match.group(2):
				skill_name = dice_result_match.group(2)
				difficulty = dice_result_match.group(3)
				skill_value = int(dice_result_match.group(4))
			else:
				# Search backwards for DICE_REQUEST marker
				skill_name = "Unknown"
				difficulty = "normal"
				skill_value = 50
				for msg in reversed(messages):
					if isinstance(msg, ToolMessage):
						content = msg.content
						request_match = re.match(r'\[DICE_REQUEST:(.+?):(.+?):(\d+)\]', content)
						if request_match:
							skill_name = request_match.group(1)
							difficulty = request_match.group(2)
							skill_value = int(request_match.group(3))
							break
			
			# Process the dice result
			dice_result = process_dice_result(d100, skill_name, difficulty, skill_value)
			print(f"    🎲 [DICE_RESULT] Processed result: {d100} for {skill_name} check")
			
			# Replace the user message with a formatted version
			messages = messages[:-1] + [HumanMessage(content=f"Dice roll result: {d100}")]
			
			# Store for later use in response
			pending_dice_result = dice_result
			
			# Update dice_results in state
			dice_results = state.get("dice_results", []) + [{
				"skill": skill_name,
				"difficulty": difficulty,
				"roll": d100,
				"result": dice_result
			}]
			state = {**state, "dice_results": dice_results}
		
		# Check for SANResult pattern
		san_result_match = re.match(r'SANResult:\s*(\d{1,3})(?::(\d+):(\d+))?', last_user_msg, re.IGNORECASE)
		if san_result_match:
			d100 = int(san_result_match.group(1))
			# If full parameters provided, use them; otherwise search backwards for the request
			if san_result_match.group(2):
				current_san = int(san_result_match.group(2))
				san_loss = int(san_result_match.group(3))
			else:
				# Search backwards for SAN_CHECK_REQUEST marker
				current_san = character.get("san", 60)
				san_loss = 1
				for msg in reversed(messages):
					if isinstance(msg, ToolMessage):
						content = msg.content
						request_match = re.match(r'\[SAN_CHECK_REQUEST:(\d+):(\d+)\]', content)
						if request_match:
							current_san = int(request_match.group(1))
							san_loss = int(request_match.group(2))
							break
			
			# Process the SAN check result
			san_result, actual_loss = process_san_check_result(d100, current_san, san_loss)
			print(f"    🧠 [SAN_RESULT] Processed result: {d100}, SAN loss: {actual_loss}")
			
			# Update character SAN
			if actual_loss > 0:
				new_san = max(0, current_san - actual_loss)
				character = character.copy()
				character["san"] = new_san
			
			# Replace the user message with a formatted version
			messages = messages[:-1] + [HumanMessage(content=f"SAN check result: {d100}")]
			
			# Store for later use in response
			pending_san_result = san_result
			san_loss_amount = actual_loss
	
	# Fallback to environment variable if not provided in state
	if not api_key:
		api_key = os.getenv("OPENAI_API_KEY")
	
	if not api_key:
		fallback_msg = AIMessage(
			content="⚠️ Please enter your OpenAI API Key in the sidebar configuration to use the LLM agent."
		)
		return {
			"messages": messages + [fallback_msg],
			"next_action": "continue",
			"next_scene": current_scene
		}
	
	# Initialize LLM with tools
	llm = ChatOpenAI(
		model="gpt-4o-mini",
		temperature=0.7,
		api_key=api_key
	).bind_tools([roll_dice, san_check, change_scene])
	
	# Build global system prompt
	system_prompt = build_global_system_prompt(character, current_scene)
	
	# Add scene-specific prompt template (this is the main scene guidance)
	scene_prompt = get_scene_prompt(current_scene, character)
	if scene_prompt:
		system_prompt += f"\n\n**=== SCENE PROMPT TEMPLATE ===**\n{scene_prompt}"
	
	system_msg = SystemMessage(content=system_prompt)
	
	# Combine system message with conversation history
	prompt_messages = [system_msg] + messages
	
	# Generate response with tool calling capability
	print(f"\n🤖 [LLM INVOKE] Calling LLM with {len(prompt_messages)} messages (scene: {current_scene})")
	response = llm.invoke(prompt_messages)
	
	# Check if tools were called
	print(f"📥 [LLM RESPONSE] Received response, has tool_calls: {bool(response.tool_calls)}")
	new_messages = messages + [response]
	next_action = "continue"
	next_scene = current_scene
	
	# Process tool calls if any
	# Note: san_loss_amount may already be set from DiceResult processing above
	
	if response.tool_calls:
		print(f"\n🔧 [TOOL CALLS] Detected {len(response.tool_calls)} tool call(s)")
		for tool_call in response.tool_calls:
			tool_name = tool_call["name"]
			tool_args = tool_call["args"]
			
			print(f"  📌 [TOOL] {tool_name} called with args: {tool_args}")
			
			if tool_name == "roll_dice":
				# Request dice roll from frontend (returns special marker)
				skill_name = tool_args.get("skill_name", "Unknown")
				difficulty = tool_args.get("difficulty", "normal")
				skill_value = tool_args.get("skill_value", 50)
				print(f"    🎲 [ROLL_DICE] Requesting dice roll: Skill: {skill_name}, Difficulty: {difficulty}, Value: {skill_value}")
				dice_request = roll_dice.invoke(tool_args)
				print(f"    🎲 [ROLL_DICE] Request marker: {dice_request}")
				
				# Add tool message with the request marker (frontend will detect this)
				tool_msg = ToolMessage(
					content=dice_request,
					tool_call_id=tool_call["id"]
				)
				new_messages.append(tool_msg)
				
				next_action = "roll_dice"
			
			elif tool_name == "san_check":
				# Request SAN check from frontend (returns special marker)
				current_san = character.get("san", 60)
				san_loss = tool_args.get("san_loss", 1)
				
				print(f"    🧠 [SAN_CHECK] Requesting SAN check: Current SAN: {current_san}, SAN Loss: {san_loss}")
				san_request = san_check.invoke({
					"current_san": current_san,
					"san_loss": san_loss
				})
				print(f"    🧠 [SAN_CHECK] Request marker: {san_request}")
				
				# Add tool message with the request marker (frontend will detect this)
				tool_msg = ToolMessage(
					content=san_request,
					tool_call_id=tool_call["id"]
				)
				new_messages.append(tool_msg)
				
				next_action = "san_check"
			
			elif tool_name == "change_scene":
				# Execute scene change
				target_scene = tool_args.get("target_scene_id", current_scene)
				
				print(f"    🔄 [CHANGE_SCENE] Transitioning from '{current_scene}' to '{target_scene}'")
				scene_result = change_scene.invoke({
					"target_scene_id": target_scene,
					"current_scene_id": current_scene
				})
				print(f"    🔄 [CHANGE_SCENE] Result: {scene_result}")
				
				# Check if scene change was successful (starts with ✓)
				if scene_result.startswith("✓"):
					# Update current scene
					current_scene = target_scene
					next_scene = target_scene
					next_action = "change_scene"
					print(f"    ✅ [CHANGE_SCENE] Scene successfully changed to '{target_scene}'")
					
					# Update system prompt with new scene information
					# Rebuild system prompt with new scene
					system_prompt = build_global_system_prompt(character, current_scene)
					scene_prompt = get_scene_prompt(current_scene, character)
					if scene_prompt:
						system_prompt += f"\n\n**=== SCENE PROMPT TEMPLATE ===**\n{scene_prompt}"
					
					# Update system message in new_messages
					system_msg = SystemMessage(content=system_prompt)
				
				# Add tool message to conversation
				tool_msg = ToolMessage(
					content=scene_result,
					tool_call_id=tool_call["id"]
				)
				new_messages.append(tool_msg)
	
	# Get final response after tool calls
	if response.tool_calls:
		# Check if we only have dice/SAN check requests (no need to re-invoke LLM)
		only_dice_requests = True
		for tool_call in response.tool_calls:
			tool_name = tool_call["name"]
			if tool_name not in ["roll_dice", "san_check"]:
				only_dice_requests = False
				break
		
		if only_dice_requests:
			# For dice/SAN check requests, don't generate additional response
			# The tool message with the request marker is enough
			# Create a minimal response that will be replaced by the request marker
			print(f"\n🎲 [DICE/SAN REQUEST] Skipping LLM re-invoke for dice/SAN check request")
			final_response = AIMessage(content="")  # Empty content, frontend will detect the marker
			new_messages.append(final_response)
		else:
			# Re-invoke to get response after tool execution
			# If scene was changed via change_scene tool, system_msg already updated with new scene info
			# Otherwise use original system_msg
			print(f"\n🔄 [LLM RE-INVOKE] Getting final response after tool execution (scene: {current_scene})")
			final_response = llm.invoke([system_msg] + new_messages)
			new_messages.append(final_response)
			print(f"✅ [FINAL RESPONSE] Generated final response")

	return {
		"messages": new_messages,
		"character": character,  # Updated character with new SAN if applicable
		"current_scene": current_scene,  # Updated scene if change_scene was called
		"next_action": next_action,
		"next_scene": next_scene,
		"dice_results": state.get("dice_results", []),
		"san_loss": san_loss_amount,
		"pending_dice_result": pending_dice_result,
		"pending_san_result": pending_san_result
	}


def scene_node(state: AgentState) -> AgentState:
	"""Handle scene transition logic"""
	current_scene = state.get("current_scene", "arrival_village")
	next_scene = state.get("next_scene", current_scene)
	scene_history = state.get("scene_history", [])
	
	print(f"\n🎬 [SCENE_NODE] Processing scene transition")
	print(f"    Current scene: {current_scene}")
	print(f"    Next scene: {next_scene}")
	
	if next_scene != current_scene:
		# Update scene
		scene_history = scene_history + [current_scene]
		
		# Add scene transition message
		scene_info = SCENES.get(next_scene, {})
		scene_name = scene_info.get("name", next_scene)
		
		print(f"    ✅ [SCENE_NODE] Scene transition confirmed: {current_scene} → {next_scene} ({scene_name})")
		
		transition_msg = AIMessage(
			content=f"\n\n*[Scene Transition: You have entered {scene_name}]*\n"
		)
		
		messages = state["messages"] + [transition_msg]
		
		return {
			"messages": messages,
			"current_scene": next_scene,
			"scene_history": scene_history,
			"next_action": "continue",
			"next_scene": next_scene
		}
	else:
		print(f"    ℹ️ [SCENE_NODE] No scene change (already in {current_scene})")
	
	return state


# ==================== ROUTING ====================

def route_after_keeper(state: AgentState) -> str:
	"""Route decision after keeper node"""
	next_action = state.get("next_action", "continue")
	
	print(f"\n🔀 [ROUTE] Routing after keeper, next_action: {next_action}")
	
	if next_action == "change_scene":
		print(f"    → Routing to scene_transition node")
		return "scene_transition"
	else:
		# After tool execution (roll_dice, san_check) or continue, end
		print(f"    → Routing to END")
		return END


# ==================== GRAPH BUILDER ====================

def build_kp_graph() -> StateGraph:
	"""Build and compile the LangGraph for KP agent with scenes and tools"""
	graph = StateGraph(AgentState)
	
	# Add nodes
	graph.add_node("keeper", keeper_node)
	graph.add_node("scene_transition", scene_node)
	
	# Define flow
	graph.add_edge(START, "keeper")
	graph.add_conditional_edges(
		"keeper",
		route_after_keeper,
		{
			"scene_transition": "scene_transition",
			END: END
		}
	)
	graph.add_edge("scene_transition", "keeper")  # Return to keeper after scene change
	
	# Compile
	return graph.compile()


# ==================== PUBLIC API ====================

def get_kp_response(
	user_input: str,
	character: Dict[str, Any],
	chat_history: List[Dict[str, str]],
	api_key: str = "",
	current_scene: str = "arrival_village"
) -> Dict[str, Any]:
	"""
	Main function to get KP response using LangGraph with scenes and tools
	
	Args:
		user_input: User's message
		character: Character dictionary
		chat_history: List of previous messages
		api_key: OpenAI API key
		current_scene: Current scene ID
	
	Returns:
		KP's response as string
	"""
	print(f"\n🚀 [GET_KP_RESPONSE] Starting KP response generation")
	print(f"    User input: {user_input[:100]}...")
	print(f"    Current scene: {current_scene}")
	print(f"    Character: {character.get('name', 'Unknown')}")
	
	# Count user messages to determine if we should compress
	# Count only non-summary messages (summary messages start with "**Summary of earlier events:**")
	user_message_count = sum(
		1 for msg in chat_history 
		if msg.get("role") == "user" and not msg.get("content", "").startswith("**Summary of earlier events:**")
	)
	
	# Compress chat history every 3 rounds (every 3 user messages)
	# We compress when we have 3, 6, 9, etc. user messages (before adding the current one)
	compressed_history = chat_history
	if user_message_count > 0 and user_message_count % 3 == 0:
		print(f"\n [COMPRESSION] Compressing chat history (round {user_message_count})")
		try:
			compressed_history = compress_chat_history(
				chat_history=chat_history,
				character=character,
				current_scene=current_scene,
				api_key=api_key,
				min_messages_before_compress=6,  # Lower threshold for more frequent compression
				keep_recent_messages=6,  # Keep last 6 messages (3 rounds) uncompressed
			)
			if len(compressed_history) < len(chat_history):
				print(f"    ✅ Compressed from {len(chat_history)} to {len(compressed_history)} messages")
			else:
				print("Compression skipped (history too short or no API key)")
		except Exception as e:
			print(f"    ⚠️ Compression failed: {e}, using original history")
			compressed_history = chat_history
	
	# Convert chat history to LangChain messages
	lc_messages = []
	for msg in compressed_history:
		if msg["role"] == "user":
			lc_messages.append(HumanMessage(content=msg["content"]))
		elif msg["role"] == "assistant":
			lc_messages.append(AIMessage(content=msg["content"]))
	
	# Add current user input
	lc_messages.append(HumanMessage(content=user_input))
	
	# Build graph
	graph = build_kp_graph()
	
	# Invoke graph
	state = {
		"messages": lc_messages,
		"character": character,
		"api_key": api_key,
		"current_scene": current_scene,
		"scene_history": [],
		"dice_results": [],
		"next_action": "continue",
		"next_scene": current_scene
	}
	
	print(f"\n📊 [GRAPH] Invoking LangGraph with state")
	print(f"    Initial scene: {state['current_scene']}")
	
	result = graph.invoke(state)
	
	print(f"\n📊 [GRAPH] Graph execution completed")
	print(f"    Final scene: {result.get('current_scene', 'N/A')}")
	print(f"    Next action: {result.get('next_action', 'N/A')}")
	
	# Extract the last assistant message(s)
	messages = result.get("messages", [])
	
	# Extract the final assistant response
	final_response = "I'm not sure how to respond to that."
	
	# Look backwards for the final assistant message (after tool execution if any)
	for msg in reversed(messages):
		if isinstance(msg, AIMessage):
			# Check if content exists and is a string
			if msg.content and isinstance(msg.content, str) and msg.content.strip():
				if not msg.tool_calls:
					final_response = msg.content
					break
				else:
					# Even if it has tool_calls, use it as fallback
					final_response = msg.content
					break
	
	# Check for pending results from state first (these are from user dice rolls)
	# If we have pending results, user has already rolled dice, so we should show results
	pending_dice_result = result.get("pending_dice_result")
	pending_san_result = result.get("pending_san_result")
	
	dice_request_found = False
	san_request_found = False
	
	if pending_dice_result or pending_san_result:
		# User has rolled dice, show the result and LLM response
		tool_results_text = pending_dice_result or pending_san_result
		if tool_results_text:
			final_response = tool_results_text + "\n---\n\n" + final_response
	else:
		# No pending results, check for dice/SAN check request markers
		# If found, return only the marker (no LLM response yet)
		for msg in messages:
			if isinstance(msg, ToolMessage):
				content = msg.content.strip()
				
				# Check for dice request marker
				dice_request_match = re.match(r'\[DICE_REQUEST:(.+?):(.+?):(\d+)\]', content)
				if dice_request_match:
					# Found dice request - return only the marker, skip LLM response
					final_response = content
					dice_request_found = True
					break
				
				# Check for SAN check request marker
				san_request_match = re.match(r'\[SAN_CHECK_REQUEST:(\d+):(\d+)\]', content)
				if san_request_match:
					# Found SAN check request - return only the marker, skip LLM response
					final_response = content
					san_request_found = True
					break
	
	# Get updated character from result (with SAN changes if any)
	updated_character = result.get("character", character)
	
	# Return response with scene info and updated character
	# Include compressed_history if compression occurred (so frontend can update its state)
	return_dict = {
		"response": final_response,
		"current_scene": result.get("current_scene", current_scene),
		"next_action": result.get("next_action", "continue"),
		"character": updated_character  # Include updated character with new SAN value
	}
	
	# If compression occurred, include the compressed history
	if len(compressed_history) < len(chat_history):
		return_dict["compressed_history"] = compressed_history
	
	return return_dict
