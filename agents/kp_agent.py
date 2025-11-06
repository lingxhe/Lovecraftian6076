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

# Load environment variables from .env file
load_dotenv()


class AgentState(TypedDict):
	messages: Annotated[List[BaseMessage], "Chat history"]
	character: Dict[str, Any]
	api_key: str
	current_scene: str  # Current scene ID
	scene_history: Annotated[List[str], "History of visited scenes"]
	dice_results: Annotated[List[Dict[str, Any]], "History of dice rolls"]
	next_action: str  # Keeper's decision: "continue", "roll_dice", "san_check", "change_scene"
	next_scene: str  # Target scene if changing scenes
	san_loss: int  # SAN loss from san_check


# ==================== DICE TOOL ====================

@tool
def roll_dice(skill_name: str, difficulty: str = "normal", skill_value: int = 50) -> str:
	"""
	Roll a skill check or attribute test.
	
	Args:
		skill_name: Name of the skill being tested (e.g., "Spot Hidden", "Dodge", "Strength")
		difficulty: Difficulty level - "easy" (half value), "normal" (full value), "hard" (half value), "extreme" (fifth value)
		skill_value: The character's skill or attribute value
	
	Returns:
		Result string describing the dice roll outcome
	"""
	d100 = random.randint(1, 100)
	
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


@tool
def san_check(current_san: int, san_loss: int) -> str:
	"""
	Perform a Sanity (SAN) check. Player rolls against current SAN value.
	If they fail, they lose SAN equal to san_loss amount.
	
	Args:
		current_san: The character's current Sanity value
		san_loss: Amount of SAN to lose if the check fails (typically 1-5, can be more for major horrors)
	
	Returns:
		Result string describing the SAN check outcome and any SAN loss
	"""
	d100 = random.randint(1, 100)
	
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
	
	return result_str


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

**Scene Transitions:**
Available transitions from current scene: {', '.join(get_available_transitions(current_scene))}
Common scene IDs: arrival_village, leddbetter_house, village_hall, ruined_church, ritual, ending

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

**Scene Transition Rules:**
- **CRITICAL:** When the player's actions clearly indicate moving to a new location or entering a different scene, you MUST call the change_scene tool BEFORE continuing narration
- Examples: Player accepts invitation to stay at May's house → call change_scene("leddbetter_house") immediately
- Player enters village hall → call change_scene("village_hall") immediately
- Player goes to ruined church → call change_scene("ruined_church") immediately
- The change_scene tool will automatically update the scene context and prompt for you
- After calling change_scene, continue narrating from the new scene's perspective
- **Do NOT wait for the player to explicitly ask for a scene change - if their actions clearly indicate entering a new location, call the tool immediately**

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
	san_loss_amount = 0
	
	if response.tool_calls:
		print(f"\n🔧 [TOOL CALLS] Detected {len(response.tool_calls)} tool call(s)")
		for tool_call in response.tool_calls:
			tool_name = tool_call["name"]
			tool_args = tool_call["args"]
			
			print(f"  📌 [TOOL] {tool_name} called with args: {tool_args}")
			
			if tool_name == "roll_dice":
				# Execute dice roll
				skill_name = tool_args.get("skill_name", "Unknown")
				difficulty = tool_args.get("difficulty", "normal")
				skill_value = tool_args.get("skill_value", 50)
				print(f"    🎲 [ROLL_DICE] Skill: {skill_name}, Difficulty: {difficulty}, Value: {skill_value}")
				dice_result = roll_dice.invoke(tool_args)
				print(f"    🎲 [ROLL_DICE] Result: {dice_result[:150]}...")  # Print first 150 chars
				
				# Store dice result in state
				dice_results = state.get("dice_results", [])
				dice_results.append({
					"skill": tool_args.get("skill_name", "Unknown"),
					"difficulty": tool_args.get("difficulty", "normal"),
					"result": dice_result
				})
				
				# Add tool message to conversation
				tool_msg = ToolMessage(
					content=dice_result,
					tool_call_id=tool_call["id"]
				)
				new_messages.append(tool_msg)
				
				next_action = "roll_dice"
			
			elif tool_name == "san_check":
				# Execute SAN check
				current_san = character.get("san", 60)
				san_loss = tool_args.get("san_loss", 1)
				
				print(f"    🧠 [SAN_CHECK] Current SAN: {current_san}, SAN Loss: {san_loss}")
				san_result = san_check.invoke({
					"current_san": current_san,
					"san_loss": san_loss
				})
				print(f"    🧠 [SAN_CHECK] Result: {san_result[:150]}...")  # Print first 150 chars
				
				# Calculate actual SAN loss from result
				# Parse the result to get actual loss
				# Look for "lose X SAN" pattern
				loss_pattern = r'lose\s+(\d+)\s+SAN'
				match = re.search(loss_pattern, san_result, re.IGNORECASE)
				if match:
					san_loss_amount = int(match.group(1))
					
					# Update character SAN
					new_san = max(0, current_san - san_loss_amount)
					character = character.copy()  # Create a copy to avoid mutating original
					character["san"] = new_san
				
				# Add tool message to conversation
				tool_msg = ToolMessage(
					content=san_result,
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
		"san_loss": san_loss_amount
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
	
	# Convert chat history to LangChain messages
	lc_messages = []
	for msg in chat_history:
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
	messages = result["messages"]
	
	# Extract the final assistant response
	final_response = "I'm not sure how to respond to that."
	
	# Look backwards for the final assistant message (after tool execution if any)
	for msg in reversed(messages):
		if isinstance(msg, AIMessage) and msg.content and not msg.tool_calls:
			final_response = msg.content
			break
		elif isinstance(msg, AIMessage) and msg.content:
			# Even if it has tool_calls, use it as fallback
			final_response = msg.content
			break
	
	# Extract tool results (dice rolls and SAN checks) from ToolMessages and format them
	tool_results_text = ""
	for msg in messages:
		if isinstance(msg, ToolMessage):
			# Parse the tool result from tool message
			content = msg.content.strip()
			
			# Check if it's a SAN check
			if "Sanity Check" in content or "[Sanity Check]" in content:
				# Format SAN check result
				lines = content.split("\n")
				sanity_check = ""
				roll_info = ""
				result_info = ""
				outcome = ""
				
				for line in lines:
					line = line.strip()
					if not line:
						continue
					if "Sanity Check" in line or line.startswith("[Sanity"):
						sanity_check = line
					elif line.startswith("Roll:"):
						roll_info = line
					elif line.startswith("Result:"):
						result_info = line
					elif ("lose" in line.lower() or "maintain" in line.lower() or "composure" in line.lower()) and not outcome:
						outcome = line
				
				# Format SAN check result nicely
				if sanity_check or roll_info or result_info:
					if tool_results_text:  # If multiple tool results, add separator
						tool_results_text += "\n"
					tool_results_text += "**🎲 Sanity Check Result**\n"
					if sanity_check:
						tool_results_text += f"{sanity_check}\n"
					if roll_info:
						tool_results_text += f"{roll_info}\n"
					if result_info:
						tool_results_text += f"{result_info}\n"
					if outcome:
						tool_results_text += f"{outcome}\n"
			
			# Check if it's a regular dice roll
			elif "Check" in content and "Roll:" in content:
				# Extract the key information from dice result
				lines = content.split("\n")
				skill_check = ""
				roll_info = ""
				result_info = ""
				outcome = ""
				
				for line in lines:
					line = line.strip()
					if not line:
						continue
					if "Check -" in line or line.startswith("["):
						skill_check = line
					elif line.startswith("Roll:"):
						roll_info = line
					elif line.startswith("Result:"):
						result_info = line
					elif ("succeed" in line.lower() or "fail" in line.lower()) and not outcome:
						outcome = line
				
				# Format dice result nicely
				if skill_check or roll_info or result_info:
					if tool_results_text:  # If multiple tool results, add separator
						tool_results_text += "\n"
					tool_results_text += "**🎲 Dice Roll Result**\n"
					if skill_check:
						tool_results_text += f"{skill_check}\n"
					if roll_info:
						tool_results_text += f"{roll_info}\n"
					if result_info:
						tool_results_text += f"{result_info}\n"
					if outcome:
						tool_results_text += f"{outcome}\n"
	
	# Combine: tool results (dice/SAN checks) first, then Keeper response
	if tool_results_text:
		final_response = tool_results_text + "\n---\n\n" + final_response
	
	# Get updated character from result (with SAN changes if any)
	updated_character = result.get("character", character)
	
	# Return response with scene info and updated character
	return {
		"response": final_response,
		"current_scene": result.get("current_scene", current_scene),
		"next_action": result.get("next_action", "continue"),
		"character": updated_character  # Include updated character with new SAN value
	}
