"""Scene definitions based on 'Alone Against the Flames' - Semi-open prompt templates"""
from typing import List, Dict, Any

# Story Overview for Global Keeper Prompt
STORY_OVERVIEW = """
**Story: Alone Against the Flames**

You are trapped in a remote village after your bus breaks down. Strange events begin to unfold as you discover the villagers are preparing for a sinister ritual. You must investigate, survive, and ultimately face a terrible choice: stop the ritual or become part of it.

**Core Themes:**
- Isolation and dread in a remote setting
- Uncovering a dark secret through investigation
- Facing cosmic horror that defies understanding
- Moral choices with lasting consequences

**Story Arc:**
1. Arrival - Discovering something is wrong in the village
2. Exploration - Uncovering clues about the ritual and the cult
3. Final Ritual - Confronting the horror at its climax
4. Ending - Consequences of your choices
"""

# Scene Templates with semi-open prompt structure
SCENES: Dict[str, Dict[str, Any]] = {
	"arrival": {
		"name": "Arrival at the Village",
		"description": "Your bus breaks down and you find yourself in a remote village. Something feels wrong.",
		"background": """
🧭 **Scene Background:**
You have just arrived at a small, remote village after your long-distance bus broke down. It's just past noon, but the clouds overhead cast everything in a pale, uneasy glow. The village seems quiet—too quiet. A few windows show dim light, but there's an unsettling emptiness to the place.

**Atmosphere Instructions:**
- Be concise—convey unease through actions and dialogue, not lengthy descriptions
- Mention sensory details only when relevant to the player's actions
- Create tension through what happens, not through excessive description
- Keep environmental details minimal—focus on player actions and responses
		""",
		
		"few_shot_examples": """
🪞 **Example Player Actions (Few-Shot Guidance):**

**Example 1:**
Player: "I want to look around the village entrance, see what buildings are nearby."
Keeper Response: "To your left, a path leads to a village square with a church steeple. Closer is an inn with a flickering sign. The bus driver points: 'The Ashbury Inn—that's where you'll want to go.' As he speaks, you catch movement in an upper window, but when you look again, it's gone. [Spot Hidden check: 50]"

**Example 2:**
Player: "I'll ask the bus driver what he knows about this place."
Keeper Response: "What do you ask him? How do you phrase your question?"
(Note: If player says something vague like this, Keeper should ask for specific dialogue. Once player provides details like "I'll ask casually if he's been through here before and what he thinks of the village", THEN proceed with: "The driver shifts. 'Not much. I've been through here a few times, but...' He trails off. 'Folks here keep to themselves. Just get to the inn, wait for the mechanic, and you'll be back on the road.' There's something in his voice—eagerness to leave? [Psychology check: 40]")

**Example 3:**
Player: "I walk toward the inn, but I'm listening carefully to my surroundings."
Keeper Response: "You walk along the muddy path. The wind carries something—distant chanting? It fades before you can be sure. [Listen check: 50]"
		""",
		
		"key_clues": """
🔑 **Critical Narrative Anchors (Must Include):**
- The bus driver's clear unease about staying in the village
- Visible but mostly empty village (buildings present but few people)
- The inn is the obvious first destination
- Opportunity to observe the church or other buildings from a distance
- Sense of being observed or watched
- Subtle hints of ritual activity (distant sounds, strange symbols if actively searched)
		""",
		
		"creative_space": """
🧩 **Creative Space for Keeper:**
- Generate specific dialogue with the bus driver
- Create unique details about the village's appearance
- Design NPCs who might appear (shopkeeper, villager, etc.)
- Invent subtle environmental storytelling (weird symbols, odd arrangements)
- Decide on the weather, time of day details, specific buildings visible
- Craft the precise moment of transition when player moves toward the inn or explores
		""",
		
		"prompt_template": """
{background}

{few_shot_examples}

{key_clues}

{creative_space}

**Current Player Context:**
Player Name: {character_name}
Current Attributes: STR {str}, INT {int_val}, POW {pow}, SPOT {spot}, LISTEN {listen}, STEALTH {stealth}, CHARM {charm}, LUCK {luck}, SAN {san}

**Your Task:**
Respond to the player's actions naturally, using the examples as style guidance. Incorporate key clues organically. Feel free to add your own creative details that enhance the atmosphere. When a skill check is needed, use the roll_dice tool first, then narrate the result.
		""",
		
		"transitions": ["exploration_inn", "exploration_village", "exploration_church"]
	},
	
	"exploration_inn": {
		"name": "The Ashbury Inn",
		"description": "A dimly lit inn where you seek refuge. What secrets does it hold?",
		"background": """
🧭 **Scene Background:**
The Ashbury Inn stands before you, a two-story building that has seen better days. The sign creaks in the wind, and through the windows, you see warm but dim light. Inside, there's a common room with a fireplace, a counter where an innkeeper might work, and stairs leading to guest rooms above. The atmosphere is claustrophobic—cozy on the surface, but something feels trapped here.

**Atmosphere Instructions:**
- Be concise—show suspicion through NPC behavior, not lengthy descriptions
- Keep room descriptions brief unless player actively searches
- Focus on what NPCs say and do, not the environment
		""",
		
		"few_shot_examples": """
🪞 **Example Player Actions:**

**Example 1:**
Player: "I enter the inn and look for the innkeeper."
Keeper Response: "A woman emerges—Mrs. Hargrove. She smiles, but it doesn't reach her eyes. 'From the bus? I've a room available, just for the night?' Her manner seems rehearsed. [Psychology check: 40]"

**Example 2:**
Player: "I want to examine my room carefully for anything unusual."
Keeper Response: "The room is clean—too clean. A desk drawer is locked, with scratches around the keyhole. Beneath the bed, a crumpled paper with strange symbols. [Spot Hidden check: 50]"

**Example 3:**
Player: "I'll try to charm information out of the innkeeper about what's going on in the village."
Keeper Response: "What do you say to charm her? How do you approach the conversation?"
(Note: Keeper asks for clarification instead of inventing player dialogue. Once player provides details like "I'll compliment her inn and ask casually about village life", THEN proceed with: "Mrs. Hargrove's expression tightens. 'It's quiet here. Always has been.' You press gently about the village. 'There's been talk. Strange things, especially at night. Best not to ask too many questions.' Her eyes dart toward the window. [Charm check: 50; if successful, she reveals villagers gather at the church at midnight]")
		""",
		
		"key_clues": """
🔑 **Critical Narrative Anchors:**
- The innkeeper knows more than she's saying (hints about the ritual)
- Opportunity to find clues in rooms (hidden notes, locked drawers, strange objects)
- If player asks directly about the church or strange events, innkeeper becomes evasive
- Overheard conversations or sounds at night (if player stays)
- The inn should be a source of partial information, not the full truth
		""",
		
		"creative_space": """
🧩 **Creative Space:**
- Design the innkeeper's personality and dialogue
- Create specific clues to be found (notes, objects, symbols)
- Invent other guests or their absence
- Craft the inn's layout and atmosphere
- Decide on what happens if player stays overnight
		""",
		
		"prompt_template": """
{background}

{few_shot_examples}

{key_clues}

{creative_space}

**Player Context:**
Player: {character_name} | STR {str}, INT {int_val}, POW {pow}, SPOT {spot}, LISTEN {listen}, STEALTH {stealth}, CHARM {charm}, LUCK {luck}, SAN {san}

Narrate naturally, following the style of examples. Integrate key clues organically. Use roll_dice tool for skill checks.
		""",
		
		"transitions": ["exploration_village", "exploration_church", "final_ritual"]
	},
	
	"exploration_village": {
		"name": "Exploring the Village",
		"description": "You venture into the village streets, searching for answers about what's happening here.",
		"background": """
🧭 **Scene Background:**
The village streets are mostly empty, but you can sense eyes on you from behind curtains. The buildings are old, some in disrepair. There's a general store, a few houses, and at the center, the church looms. You can explore, talk to any villagers you encounter, or investigate specific locations. The feeling of wrongness grows stronger the longer you stay.

**Atmosphere Instructions:**
- Be concise—convey paranoia through NPC reactions, not lengthy descriptions
- Show environmental details only when player actively investigates
- Keep descriptions brief—focus on NPC interactions and player actions
- The church is important, but don't over-describe it
		""",
		
		"few_shot_examples": """
🪞 **Example Player Actions:**

**Example 1:**
Player: "I want to search for villagers and see if anyone will talk to me."
Keeper Response: "How do you search? Where do you go? Do you knock on doors, look for people in public areas, or something else?"
(Note: If player gives vague instructions, ask for specifics. Once player provides details like "I'll walk along the main street and look for people in their gardens or outside their houses", THEN proceed with: "You spot an old man in a garden. As you approach, he freezes, then turns. 'You shouldn't be here,' he whispers. 'Not tonight. They'll come for you if you stay.' He hurries inside and locks his door. [Luck check: 60 to encounter someone willing to talk]")

**Example 2:**
Player: "I'll investigate the general store and see if I can find anything useful or get information."
Keeper Response: "How do you investigate? Do you browse the shelves, talk to the shopkeeper, examine specific items, or something else? What information are you looking for?"
(Note: Ask for specifics. Once player provides details like "I'll browse the shelves first, then talk to the shopkeeper and ask about the village", THEN proceed with: "The store is dark but unlocked. Mr. Corbin, the shopkeeper, looks up warily. 'Can I help you?' he asks. The shelves are sparse. On the counter, a pamphlet mentions a 'Harvest Festival' tonight. [Spot Hidden check: 50 to notice the pamphlet; Charm check: 50 to get info about the festival]")

**Example 3:**
Player: "I'll stealthily approach the church and try to listen for any sounds from inside."
Keeper Response: "You move quietly along the church wall. Pressing your ear against the stone, you hear voices—chanting. Ancient words you don't recognize. Footsteps. Someone's coming. [Stealth check: 50 to avoid detection; Listen check: 50 to make out the words]"
		""",
		
		"key_clues": """
🔑 **Critical Narrative Anchors:**
- Villagers are aware of something happening tonight (the ritual)
- The "Harvest Festival" or similar event is mentioned (it's the ritual)
- Strange symbols or markings appear in various locations
- The church is the focal point, with activity inside
- Evidence that villagers are preparing for something
- Hints about what will happen if the ritual completes
		""",
		
		"creative_space": """
🧩 **Creative Space:**
- Create specific NPCs with unique personalities
- Design environmental clues (symbols, objects, writings)
- Craft the village layout and specific locations
- Invent overheard conversations or partial information
- Build tension through what is seen vs. what is hidden
		""",
		
		"prompt_template": """
{background}

{few_shot_examples}

{key_clues}

{creative_space}

**Player Context:**
{character_name} | Attributes: STR {str}, INT {int_val}, POW {pow}, SPOT {spot}, LISTEN {listen}, STEALTH {stealth}, CHARM {charm}, LUCK {luck}, SAN {san}

Narrate using the example style. Integrate key clues naturally. Use roll_dice for skill checks.
		""",
		
		"transitions": ["exploration_church", "final_ritual", "exploration_inn"]
	},
	
	"exploration_church": {
		"name": "The Village Church",
		"description": "The old church stands at the center of the mystery. What horrors await inside?",
		"background": """
🧭 **Scene Background:**
The church is ancient, its stone walls weathered by time. The stained glass windows are dark, but flickering light from within suggests activity. The building feels heavy, oppressive, as if it holds secrets within its walls. This is clearly the heart of whatever is happening in the village.

**Atmosphere Instructions:**
- Be concise—build tension through what's discovered, not lengthy descriptions
- Show ritual evidence clearly but briefly
- Focus on player actions and discoveries, not environmental details
- The climax approaches—keep momentum
		""",
		
		"few_shot_examples": """
🪞 **Example Player Actions:**

**Example 1:**
Player: "I'll carefully enter the church and see what's inside."
Keeper Response: "The door opens. The air smells of incense and something metallic. Pews pushed aside, and in the center—a circle with symbols drawn in chalk or ash. The altar has been moved, revealing a trapdoor. [Spot Hidden check: 50 to notice the trapdoor; SAN check if examining symbols]"

**Example 2:**
Player: "I want to investigate the symbols and see if I can understand what they mean."
Keeper Response: "The symbols are angular, sharp, with curves that seem to shift. Ancient. Pre-human. Your head aches. [INT check: 50 to recall similar symbols; if successful, recognizes forbidden text elements; SAN loss if fails]"

**Example 3:**
Player: "I'll hide and wait to see who comes to the church, trying to understand what's happening."
Keeper Response: "You hide in an alcove. Footsteps. Villagers file in, faces blank, entranced. They take positions around the circle. A figure in dark robes steps forward: 'The time approaches.' [Stealth check: 50 to remain hidden; Listen check: 60 to overhear ritual details]"
		""",
		
		"key_clues": """
🔑 **Critical Narrative Anchors:**
- The church contains the ritual circle and preparation for the ceremony
- Evidence of a cult or dark worship
- The trapdoor or hidden area leads to something important
- Villagers are gathering, preparing for the ritual
- Clear indication that the ritual will happen soon (tonight)
- The player learns what the ritual actually does (summoning? sacrifice? transformation?)
		""",
		
		"creative_space": """
🧩 **Creative Space:**
- Design the church's interior layout
- Create specific ritual elements and symbols
- Craft the cult leader or ritual master
- Invent what the ritual actually does (what horror it summons)
- Build the reveal of the full conspiracy
		""",
		
		"prompt_template": """
{background}

{few_shot_examples}

{key_clues}

{creative_space}

**Player Context:**
{character_name} | STR {str}, INT {int_val}, POW {pow}, SPOT {spot}, LISTEN {listen}, STEALTH {stealth}, CHARM {charm}, LUCK {luck}, SAN {san}

Narrate with building tension. Integrate key clues. Use roll_dice for checks. This scene should lead toward the final confrontation.
		""",
		
		"transitions": ["final_ritual"]
	},
	
	"final_ritual": {
		"name": "The Final Ritual",
		"description": "The ritual reaches its climax. You must act now or face the consequences.",
		"background": """
🧭 **Scene Background:**
The ritual has begun. Whether you're witnessing it, interrupting it, or participating unwillingly, this is the moment of truth. The cosmic horror is manifesting, and the village's dark secret is revealed in full. You must make choices that will determine not just your fate, but potentially the fate of others.

**Atmosphere Instructions:**
- Be direct and urgent—no lengthy setup
- Make stakes clear immediately
- Focus on player actions and consequences
- Keep horror description concise but impactful
- Multiple resolution paths available
		""",
		
		"few_shot_examples": """
🪞 **Example Player Actions:**

**Example 1:**
Player: "I'll try to disrupt the ritual by attacking the cult leader."
Keeper Response: "You rush forward, but the villagers move to intercept. They're not themselves—their eyes are wrong, their movements too fluid. The cult leader turns, and you see... something that shouldn't be human. [STR check: 50 to break through; if successful, you reach the leader but must face the horror directly; SAN check on seeing the transformed leader]"

**Example 2:**
Player: "I want to use my knowledge to reverse or counter the ritual symbols."
Keeper Response: "You scramble to find chalk or anything to mark the symbols. The ritual circle is complex, but you see a pattern—if you break the circle at specific points, it might disrupt the summoning. But the thing in the center is growing, manifesting. You have moments. [INT check: 60 to understand the pattern; POW check: 50 to disrupt the ritual; if both succeed, you can stop it but must still escape]"

**Example 3:**
Player: "I'll try to escape and get help, or at least survive to warn others."
Keeper Response: "You turn and run, but the villagers are everywhere now. The thing behind you screams—a sound that tears at reality itself. You feel something pulling at your mind. [Luck check: 50 to find an escape route; STEALTH check: 50 to slip past the villagers; SAN check due to exposure to the horror]"
		""",
		
		"key_clues": """
🔑 **Critical Narrative Anchors:**
- The ritual must reach a climax point where player must act
- Multiple resolution paths available (stop it, escape, join, destroy)
- The cosmic horror should be revealed but not fully described (preserve mystery)
- Player's actions here determine the ending
- SAN loss is significant but not necessarily fatal
- Some villagers can be saved, depending on player choices
		""",
		
		"creative_space": """
🧩 **Creative Space:**
- Design the specific manifestation of the horror
- Create the cult leader's true form or nature
- Craft the mechanics of stopping/interrupting the ritual
- Invent consequences for different player choices
- Build the emotional weight of the final confrontation
		""",
		
		"prompt_template": """
{background}

{few_shot_examples}

{key_clues}

{creative_space}

**Player Context:**
{character_name} | STR {str}, INT {int_val}, POW {pow}, SPOT {spot}, LISTEN {listen}, STEALTH {stealth}, CHARM {charm}, LUCK {luck}, SAN {san}

This is the climax. Narrate with intensity and consequence. Player choices matter. Use roll_dice for all checks. Lead toward a resolution that transitions to the ending scene.
		""",
		
		"transitions": ["ending"]
	},
	
	"ending": {
		"name": "The Aftermath",
		"description": "The ritual is over. What remains, and what have you become?",
		"background": """
🧭 **Scene Background:**
The dust settles—or perhaps it doesn't. Whether you stopped the ritual, escaped, or became part of something larger, your experience in the village has changed you. This scene deals with the consequences, the aftermath, and the question of whether you can ever truly return to normal life.

**Atmosphere Instructions:**
- Be concise—summarize consequences clearly
- Show the cost without lengthy reflection
- Keep open-ended but brief
- Focus on what changed, not lengthy description
		""",
		
		"few_shot_examples": """
🪞 **Example Player Actions:**

**Example 1:**
Player: "What happens to me after this? Do I get away?"
Keeper Response: "Days later, you're on another bus, heading anywhere but here. In your bag, there's a newspaper clipping about a 'gas leak' that killed several villagers in Ashbury. The official story is clean, but you know. You'll always know. Sleep doesn't come easy anymore. [Final SAN check to see if you can cope; if SAN is very low, describe ongoing paranoia]"

**Example 2:**
Player: "I want to know what happened to the village and if anyone else survived."
Keeper Response: "Weeks pass. You make inquiries, carefully, from a distance. The village is... empty now. Some say the survivors moved away. Others whisper about disappearances. You find one name in your research: someone like you, who was there that night. They're in an asylum now, babbling about things that shouldn't exist. [INT check: 50 to research; reveals the true cost of the ritual]"

**Example 3:**
Player: "How has this changed my character? What do I do next?"
Keeper Response: "You have a choice: try to forget and live a life of half-truths, or embrace the knowledge you've gained and seek out others who understand. Some doors, once opened, cannot be closed. The question is whether you'll walk through them or spend your life trying to ignore what's on the other side. [Character development based on player's choices during the story]"
		""",
		
		"key_clues": """
🔑 **Critical Narrative Anchors:**
- The official story vs. what really happened
- The cost of the experience (SAN, memories, relationships)
- Lingering effects of exposure to cosmic horror
- Possibility of future encounters or investigations
- The question of whether normal life is still possible
- Open ending that respects player's choices throughout
		""",
		
		"creative_space": """
🧩 **Creative Space:**
- Create specific consequences based on how the ritual ended
- Design the aftermath for the village and villagers
- Craft the character's new reality
- Invent hints about future possibilities (or close them off)
- Build an ending that feels earned and meaningful
		""",
		
		"prompt_template": """
{background}

{few_shot_examples}

{key_clues}

{creative_space}

**Player Context:**
{character_name} | Final Stats: STR {str}, INT {int_val}, POW {pow}, SPOT {spot}, LISTEN {listen}, STEALTH {stealth}, CHARM {charm}, LUCK {luck}, SAN {san}

This is the epilogue. Provide closure based on player's choices. Reflect on what was lost and what was gained. End with a sense of completion, but allow the horror to linger.
		""",
		
		"transitions": []
	}
}


def get_scene_prompt(scene_id: str, character: Dict[str, Any]) -> str:
	"""Get the formatted prompt template for a scene"""
	scene = SCENES.get(scene_id, {})
	if not scene:
		return ""
	
	template = scene.get("prompt_template", "")
	character_name = character.get("name", "Investigator")
	
	# Format template with character attributes
	formatted = template.format(
		background=scene.get("background", ""),
		few_shot_examples=scene.get("few_shot_examples", ""),
		key_clues=scene.get("key_clues", ""),
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
