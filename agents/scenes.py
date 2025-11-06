"""Scene definitions based on 'Alone Against the Flames' - Semi-open prompt templates"""
from typing import List, Dict, Any

# Story Overview for Global Keeper Prompt
STORY_OVERVIEW = """
**Story Overview: Alone Against the Flames (Keeper Reference)**

You are the Keeper guiding a lone investigator whose taxi breaks down on the mountain road to Arkham. The driver, Silas, leaves to find a mechanic, leaving the player alone to enter the remote hilltop village of Emberhead. The village is quiet, remote, and the air carries the smell of charcoal. A massive iron tower—the Beacon—dominates the skyline.

As dusk falls, the investigator discovers the villagers are preparing for a "festival" centered around the Beacon. The ritual's true purpose involves human sacrifice—travelers are kept and burned during the festival.

**Core Themes:**
- Isolation and subtle dread in a closed community
- The illusion of hospitality masking a hidden horror
- Gradual discovery of an impending ritual and its true meaning
- Psychological tension between curiosity, fear, and survival

**Arc Summary:**
1. Arrival — The taxi breaks down; Silas leaves; player enters Emberhead at dusk
2. Lodging — May Ledbetter offers accommodation; Ruth warns at night
3. Investigation — Exploring village, discovering clues about the ritual
4. The Festival — The ritual reaches its terrible climax at the Beacon
5. Aftermath — The consequences of choice and sanity
"""


# Scene Templates with semi-open prompt structure
SCENES: Dict[str, Dict[str, Any]] = {
	"arrival_village": {
		"name": "Arrival at Emberhead",
		"description": "The player's taxi breaks down on the mountain road to Arkham. After the driver leaves, the player walks alone into the hilltop village of Emberhead. It is quiet, remote, and the air is filled with the smell of charcoal.",
		"key_clues": """
🔑 **Key Clues and Rules:**
- The taxi breaks down on the hilltop; all communication signals and transport are cut off.
- Silas makes an excuse to leave, appears anxious; hints he knows dangerous things but won't elaborate.
- The village is unusually quiet; the air carries the smell of charcoal and smoke.
- A giant iron tower (The Beacon) is visible on a distant hilltop; villagers call it the "Festival Lighthouse."
- Some villagers watch outsiders from a distance with empty expressions; don't talk to them.
- May Ledbetter appears proactively, acts friendly, claims the inn is closed, suggests the player rest at her house.
- It's almost dusk; the weather is getting cold; the air is filled with fine sparks and ashes. Many locations (such as the iron tower, church ruins) cannot be explored temporarily due to the late hour.
- When looking around the village: a narrow main road runs through the town, with a general store, ruined church, town hall, blacksmith, and an old inn along the roadside; most buildings have closed doors and windows, occasionally someone can be seen moving inside.
		""",
		"creative_space": """
🧩 **Creative Space for Keeper:**
- Stage brief exchanges with Silas (vague mentions of "their customs" or "the festival here"; seems to want to say something but holds back)
- Show May Ledbetter's proactive approach (appears and offers help)
- Describe villagers watching with empty expressions
- Set dusk atmosphere limiting exploration
		""",
		"prompt_template": """
{key_clues}

{npcs}

{transitions}

{creative_space}

**Player Context:**
{character_name} | STR {str}, INT {int_val}, POW {pow}, SPOT {spot}, LISTEN {listen}, STEALTH {stealth}, CHARM {charm}, LUCK {luck}, SAN {san}

**Important:** When the player accepts May Ledbetter's invitation to stay at her house or enters her home, you MUST immediately call the change_scene tool with target_scene_id="leddbetter_house" before continuing narration.

Respond concisely. Integrate anchors naturally. Use roll_dice where checks are implied.
		""",
		"transitions": ["leddbetter_house"],
		"npcs": [
			{"name": "Silas", "role": "Taxi Driver", "personality": "Silent, anxious, superstitious; clearly unwilling to stay longer.", "plot_behaviors": "After the vehicle breaks down, makes an excuse to find a mechanic and leaves quickly; when talking to the player, words are vague, occasionally mentions 'the festival here' or 'their customs'; before leaving, seems to want to say something but forces himself to hold back.", "keeper_intent": "Silas had heard of Emberhead's fire ritual and does not want to get involved. He will not reappear after leaving."},
			{"name": "May Ledbetter", "role": "Villager offering lodging", "personality": "Gentle, polite, maternal, slightly nervous; calm tone but avoids deep topics.", "plot_behaviors": "Proactively appears and initiates conversation with player; shows kindness and curiosity; when player mentions looking for accommodation, states village inn is closed; then invites player to stay at her house for one night.", "keeper_intent": "Is a cult member, responsible for taking in outsiders 'before the festival.' She is conflicted—both obedient and fearful, but will gently guide the player to stay in the village."}
		]
	},

	"leddbetter_house": {
		"name": "Lodging with May Ledbetter",
		"description": "Due to the inn being closed, the player is taken in by the village woman May Ledbetter to spend the night at her home. The surface appears warm and peaceful, but subtle disharmony and strange occurrences at night hint at impending danger.",
		"key_clues": """
🔑 **Key Clues and Rules:**
- May claims the inn is temporarily closed; actively offers accommodation; advises player to rest assured.
- The house is warm but permeated with a faint scent of incense; flame-shaped metal ornaments hang above the fireplace.
- Whispers and metallic sounds can be heard from outside at night; if observed closely through the window, figures can be seen moving wood in the street.
- Ruth appears at night, frantically warns the player to "leave here before the festival," and shows the flame symbols she drew.
- If the player searches the room, they may find luggage or clothes belonging to previous travelers piled in the closet (hinting that others have been there before).
- In the early morning, May appears calm but tired; if asked about the night's activities, she will deny everything.
		""",
		"creative_space": """
🧩 **Creative Space:**
- Shape May's duality (kind yet withholding; thoughtfulness and caution masking fear)
- Stage Ruth's nighttime approach (sensitive, timid, sincere; whispers urgently; shows drawings)
- Describe night sounds and movements outside (villagers preparing for ritual)
- Decide if player searches room and finds evidence of previous travelers
- Handle morning conversation if player asks about night activities
		""",
		"prompt_template": """
{key_clues}

{npcs}

{transitions}

{creative_space}

**Player Context:**
{character_name} | STR {str}, INT {int_val}, POW {pow}, SPOT {spot}, LISTEN {listen}, STEALTH {stealth}, CHARM {charm}, LUCK {luck}, SAN {san}

Stay concise. Only ask for specifics if the player's intent is genuinely unclear; otherwise, narrate what happens and let the player decide their next action. Use roll_dice for checks.
		""",
		"transitions": ["village_hall", "ruined_church", "ritual"],
		"npcs": [
			{"name": "May Ledbetter", "role": "Host", "personality": "Thoughtful, cautious, maternal, melancholic.", "plot_behaviors": "Actively invites player to stay, states inn is closed; prepares meals and bedroom for player; friendly but clearly masks tension; avoids discussing village's 'festival,' changes subject when asked; may burn incense and pray softly in front of fireplace at night.", "keeper_intent": "May is one of the participants in the ritual, responsible for 'caring for' outsiders. She is inwardly fearful but unable to resist. Although she shows kindness to the player, it is actually to keep the player in the village until the day of the ritual."},
			{"name": "Ruth Ledbetter", "role": "May's daughter", "personality": "Sensitive, timid, innocent, sincere.", "plot_behaviors": "Quiet during the day, secretly approaches player at night; whispers warning: 'Leave here before the festival'; if player talks to her, reveals mother is 'preparing for guests for the festival'; often draws strange patterns (flames and human figures).", "keeper_intent": "Ruth secretly witnessed the ritual preparations and knows that the 'festival' will involve sacrificing living people. She genuinely wants to help the player escape, but being young and powerless, she can only express her fear through warnings."}
		]
	},

	"village_hall": {
		"name": "Village Hall / Town Office",
		"description": "Town office where player attempts to contact outside world; Clyde Winters evades questions.",
		"key_clues": """
🔑 **Key Clues and Rules:**
- No telephone/telegraph available; Clyde claims equipment is down
- Clyde evades questions about communications; becomes defensive when pressed
- Records and files seem incomplete or missing
- Village appears deliberately isolated from outside world
		""",
		"creative_space": """
🧩 **Creative Space:**
- Shape Clyde's evasiveness and nervousness
- Place clues in files or records (if player searches)
- Hint at connections to the ritual or missing travelers
		""",
		"prompt_template": """
{key_clues}

{npcs}

{transitions}

{creative_space}

**Player Context:**
{character_name} | STR {str}, INT {int_val}, POW {pow}, SPOT {spot}, LISTEN {listen}, STEALTH {stealth}, CHARM {charm}, LUCK {luck}, SAN {san}

Narrate succinctly. Use roll_dice for social checks and searches.
		""",
		"transitions": ["leddbetter_house", "ruined_church", "ritual"],
		"npcs": [
			{"name": "Clyde Winters", "role": "Town office clerk", "personality": "", "plot_behaviors": "Claims telegraph is down/being repaired; avoids questions about communications; shifts uncomfortably when pressed; becomes defensive; nervous about player's presence; may hint at knowing more but won't say", "keeper_intent": ""}
		]
	},

	"ruined_church": {
		"name": "Ruined Church",
		"description": "Abandoned church ruins where an old caretaker mutters cryptic phrases about the Beacon.",
		"key_clues": """
🔑 **Key Clues and Rules:**
- Old priest/caretaker mutters cryptic phrases like "The Beacon protects us"
- Church in ruins; symbols and markings suggest ritual connections
- Caretaker avoids direct answers; speaks in riddles
- Beacon visible from this location; sense of being watched
		""",
		"creative_space": """
🧩 **Creative Space:**
- Define caretaker's cryptic speech patterns
- Place symbols connecting to other scenes (Ledbetter house, Beacon)
- Create atmosphere of abandonment and hidden purpose
		""",
		"prompt_template": """
{key_clues}

{npcs}

{transitions}

{creative_space}

**Player Context:**
{character_name} | STR {str}, INT {int_val}, POW {pow}, SPOT {spot}, LISTEN {listen}, STEALTH {stealth}, CHARM {charm}, LUCK {luck}, SAN {san}

Narrate succinctly. Use roll_dice for social checks and investigations.
		""",
		"transitions": ["leddbetter_house", "village_hall", "ritual"],
		"npcs": [
			{"name": "Old Priest/Caretaker", "role": "Church caretaker", "personality": "", "plot_behaviors": "Found near church ruins; mutters cryptic phrases like 'The Beacon protects us'; avoids direct answers; speaks in riddles; may have deeper knowledge but won't reveal it directly", "keeper_intent": ""}
		]
	},

	"ritual": {
		"name": "The Festival Ritual",
		"description": "Night ritual at the Beacon; the terrible climax where travelers are sacrificed.",
		"key_clues": """
🔑 **Key Clues and Rules:**
- Forced approach to the Beacon top
- Masked leader presides; villagers chant "The flame will purify all"
- Chant and wind create oppressive rhythm
- Flame displays intention (SAN checks required)
- May entranced; Ruth terrified in crowd
- Clear choice structure determines ending: escape, resist, or accept
		""",
		"creative_space": """
🧩 **Creative Space:**
- Define the masked leader's voice and gestures
- Stage crowd reactions to each player path
- Tune SAN costs to the exposure level
- Create urgency and horror without over-description
		""",
		"prompt_template": """
{key_clues}

{npcs}

{transitions}

{creative_space}

**Player Context:**
{character_name} | STR {str}, INT {int_val}, POW {pow}, SPOT {spot}, LISTEN {listen}, STEALTH {stealth}, CHARM {charm}, LUCK {luck}, SAN {san}

Drive toward a resolution. Use roll_dice for all contested actions and SAN. Choices here determine the ending.
		""",
		"transitions": ["ending"],
		"npcs": [
			{"name": "Masked Leader/High Priest", "role": "Ritual master", "personality": "", "plot_behaviors": "Presides before Beacon; leads chanting 'The flame will purify all'; invites or forces player toward Beacon top; voice and gestures command attention", "keeper_intent": ""},
			{"name": "May Ledbetter", "role": "Controlled participant", "personality": "", "plot_behaviors": "Stands glassy-eyed, entranced; no longer the warm host; appears under ritual's influence; cannot help player", "keeper_intent": ""},
			{"name": "Ruth Ledbetter", "role": "In crowd, terrified", "personality": "", "plot_behaviors": "Watches in terror from the crowd; cannot act; represents innocence witnessing horror", "keeper_intent": ""},
			{"name": "Villagers", "role": "Chanting crowd, hundreds", "personality": "", "plot_behaviors": "File in with blank faces; take positions around Beacon; chant in unison; move to intercept if player tries to escape; surge if player resists", "keeper_intent": ""}
		]
	},

	"ending": {
		"name": "After the Flames",
		"description": "Epilogue shaped by outcome: Escape, Corruption, or Madness.",
		"key_clues": """
🔑 **Key Clues and Rules:**
- Official cover vs. truth
- Cost in SAN, memory, or allegiance
- Space for future hooks or closure
		""",
		"creative_space": """
🧩 **Creative Space:**
- Tailor outcomes to player choices and final checks
- Echo symbols seen earlier (totem, chains, ash)
- Leave one unsettling detail unresolved
		""",
		"prompt_template": """
{key_clues}

{npcs}

{transitions}

{creative_space}

**Player Context:**
{character_name} | Final Stats: STR {str}, INT {int_val}, POW {pow}, SPOT {spot}, LISTEN {listen}, STEALTH {stealth}, CHARM {charm}, LUCK {luck}, SAN {san}

Provide closure aligned to the chosen path. Keep it brief and resonant.
		""",
		"transitions": [],
		"npcs": [
			{"name": "Silas", "role": "May appear if escaped", "personality": "", "plot_behaviors": "If escape ending: may be encountered on road; shows relief but doesn't want to discuss what happened", "keeper_intent": ""},
			{"name": "Investigator/Researcher", "role": "Epilogue narrator", "personality": "", "plot_behaviors": "May investigate aftermath; discovers official cover story vs. truth; finds evidence of other victims", "keeper_intent": ""},
			{"name": "Hospital staff", "role": "If madness ending", "personality": "", "plot_behaviors": "Soft voices, gentle care; patient speaks of fire behind eyelids; ongoing SAN effects", "keeper_intent": ""}
		]
	}
}


def get_scene_prompt(scene_id: str, character: Dict[str, Any]) -> str:
	"""Get the formatted prompt template for a scene"""
	scene = SCENES.get(scene_id, {})
	if not scene:
		return ""
	
	template = scene.get("prompt_template", "")
	character_name = character.get("name", "Investigator")
	
	# Format NPCs information
	npcs = scene.get("npcs", [])
	npcs_text = ""
	if npcs:
		npcs_text = "👥 **NPCs in this Scene:**\n"
		for npc in npcs:
			name = npc.get("name", "Unknown")
			role = npc.get("role", "")
			personality = npc.get("personality", "")
			plot_behaviors = npc.get("plot_behaviors", "")
			keeper_intent = npc.get("keeper_intent", "")
			
			npcs_text += f"- **{name}** ({role})\n"
			if personality:
				npcs_text += f"  - Personality: {personality}\n"
			if plot_behaviors:
				npcs_text += f"  - Plot Behaviors: {plot_behaviors}\n"
			if keeper_intent:
				npcs_text += f"  - Keeper Intent (for reference): {keeper_intent}\n"
			npcs_text += "\n"
	
	# Format transitions information
	transitions = scene.get("transitions", [])
	transitions_text = ""
	if transitions:
		# Get scene names for better readability
		transition_names = []
		for trans_id in transitions:
			trans_scene = SCENES.get(trans_id, {})
			trans_name = trans_scene.get("name", trans_id)
			transition_names.append(f"{trans_id} ({trans_name})")
		
		transitions_text = "🔄 **Available Scene Transitions:**\n"
		transitions_text += f"When the player's actions suggest moving to a new location, you can call the change_scene tool with one of these scene IDs:\n"
		for trans_id in transitions:
			trans_scene = SCENES.get(trans_id, {})
			trans_name = trans_scene.get("name", trans_id)
			trans_desc = trans_scene.get("description", "")
			transitions_text += f"- **{trans_id}**: {trans_name}"
			if trans_desc:
				transitions_text += f" - {trans_desc}"
			transitions_text += "\n"
		transitions_text += "\n"
	else:
		transitions_text = "🔄 **Scene Transitions:**\nNo transitions available from this scene (likely an ending scene).\n\n"
	
	# Format template with character attributes
	formatted = template.format(
		key_clues=scene.get("key_clues", ""),
		npcs=npcs_text,
		transitions=transitions_text,
		creative_space=scene.get("creative_space", ""),
		character_name=character_name,
		str=character.get("str", 50),
		int_val=character.get("int", 50),
		pow=character.get("pow", 50),
		spot=character.get("spot", 50),
		listen=character.get("listen", 50),
		stealth=character.get("stealth", 50),
		charm=character.get("charm", 50),
		luck=character.get("luck", 50),
		san=character.get("san", 60)
	)
	
	return formatted


def get_available_transitions(scene_id: str) -> List[str]:
	"""Get available scene transitions from current scene"""
	return SCENES.get(scene_id, {}).get("transitions", [])


def get_story_overview() -> str:
	"""Get the story overview for global prompt"""
	return STORY_OVERVIEW
