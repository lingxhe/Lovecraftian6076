import streamlit as st
import os
from utils import initialize_session_state
from agents.kp_agent import get_kp_response
from utils.logging import init_logger, get_logger, log_message, stop_logger

initialize_session_state()

# Initialize logger if character exists and logger not already initialized
if st.session_state.get("character") and not st.session_state.get("_logger_initialized", False):
	character_name = st.session_state["character"].get("name", "Unknown")
	init_logger(character_name, enable_print_capture=True)
	st.session_state["_logger_initialized"] = True
	st.session_state["_log_file"] = get_logger().log_file if get_logger() else None

# Sidebar configuration
with st.sidebar:
	st.header("⚙️ Configuration")
	
	# API Key input
	st.subheader("OpenAI API Key")
	api_key_placeholder = st.session_state.get("openai_api_key", "") if st.session_state.get("openai_api_key") else ""
	api_key_input = st.text_input(
		"Enter your OpenAI API Key",
		value=api_key_placeholder,
		type="password",
		placeholder="sk-...",
		help="Get your API key from https://platform.openai.com/api-keys",
		label_visibility="collapsed"
	)
	
	if api_key_input:
		st.session_state["openai_api_key"] = api_key_input
		if api_key_input.startswith("sk-"):
			st.success("✓ API Key saved")
		else:
			st.warning("⚠️ API Key should start with 'sk-'")
	elif api_key_placeholder:
		# Keep existing key if input is cleared
		pass
	else:
		st.info("💡 Enter your OpenAI API Key to enable LLM features")
	
	st.divider()
	
	# Show character info if available
	if st.session_state.get("character"):
		st.subheader("Current Character")
		ch = st.session_state["character"]
		st.text(f"Name: {ch.get('name', 'N/A')}")
		st.text(f"STR: {ch.get('str', 0)} | INT: {ch.get('int', 0)} | POW: {ch.get('pow', 0)}")
		st.text(f"SAN: {ch.get('san', 0)}")
		st.caption(f"SPOT: {ch.get('spot', 0)} | LISTEN: {ch.get('listen', 0)} | STEALTH: {ch.get('stealth', 0)}")
		st.caption(f"CHARM: {ch.get('charm', 0)} | LUCK: {ch.get('luck', 0)}")
	
	# Show current scene
	if "current_scene" in st.session_state:
		st.divider()
		st.subheader("Current Scene")
		from agents.scenes import SCENES
		scene_id = st.session_state["current_scene"]
		scene_info = SCENES.get(scene_id, {})
		
		if scene_info:
			# Display scene name
			scene_name = scene_info.get("name", scene_id)
			st.text(f"📍 {scene_name}")
			
			# Display scene description
			scene_description = scene_info.get("description", "")
			if scene_description:
				st.caption(scene_description)
			

		else:
			st.warning(f"Scene '{scene_id}' not found")
			st.caption(f"Available scenes: {', '.join(SCENES.keys())}")
			# Debug: show what we're looking for
			st.caption(f"Debug: Looking for scene_id='{scene_id}' (type: {type(scene_id)})")
			st.caption(f"Debug: SCENES dict has {len(SCENES)} scenes")
	
	# Debug panel (expandable)
	st.divider()
	with st.expander("🐛 Debug Info", expanded=False):
		st.caption("Session State Values:")
		st.text(f"current_scene: {st.session_state.get('current_scene', 'NOT SET')}")
		st.text(f"messages count: {len(st.session_state.get('messages', []))}")
		if "character" in st.session_state:
			st.text(f"character SAN: {st.session_state['character'].get('san', 'N/A')}")
		st.text(f"API key set: {bool(st.session_state.get('openai_api_key', ''))}")
		
		# Show full session state keys (without values to avoid clutter)
		st.caption("Session State Keys:")
		keys = [k for k in st.session_state.keys() if not k.startswith('_')]
		st.write(", ".join(keys) if keys else "No keys")
		
		# Toggle debug mode
		debug_mode = st.checkbox("Enable Debug Mode", value=st.session_state.get("_debug_mode", False))
		st.session_state["_debug_mode"] = debug_mode
		if debug_mode:
			st.info("Debug mode enabled - state changes will be shown in main view")
	
	# Logging section
	if st.session_state.get("character"):
		st.divider()
		st.subheader("📝 Chat Log")
		logger = get_logger()
		if logger and logger.log_file:
			st.success(f"✅ Logging enabled")
			st.caption(f"Log file: `{logger.log_file}`")
			try:
				with open(logger.log_file, 'r', encoding='utf-8') as f:
					log_content = f.read()
					st.download_button(
						"💾 Download Log",
						log_content,
						file_name=os.path.basename(logger.log_file),
						mime="text/markdown",
						use_container_width=True
					)
			except Exception as e:
				st.error(f"Error reading log: {e}")
		else:
			st.info("💡 Logging will start automatically when you create a character")
	
	# Restart button
	st.divider()
	if st.button("🔄 Restart Conversation", use_container_width=True, type="secondary"):
		# Clear messages
		st.session_state["messages"] = []
		# Reset scene to arrival
		st.session_state["current_scene"] = "arrival_village"
		# Restart logger
		if st.session_state.get("character"):
			stop_logger()
			character_name = st.session_state["character"].get("name", "Unknown")
			init_logger(character_name, enable_print_capture=True)
			st.session_state["_log_file"] = get_logger().log_file if get_logger() else None
		st.success("Conversation restarted!")
		st.rerun()

st.title("KP Chat")

character = st.session_state.get("character")
if not character:
	st.info("Please create and save a character on the 'Create Character' page first.")
	st.stop()

# Get avatar from character
user_avatar = character.get("avatar") if character else None

# Initialize current scene in session state
if "current_scene" not in st.session_state:
	st.session_state["current_scene"] = "arrival_village"
else:
	# Fix old scene IDs that may exist in session state
	old_scene = st.session_state["current_scene"]
	from agents.scenes import SCENES
	# If scene ID doesn't exist in SCENES, reset to arrival_village
	if old_scene not in SCENES:
		st.session_state["current_scene"] = "arrival_village"
		st.rerun()  # Rerun to apply the fix immediately

# Generate opening scene if this is the first time (no messages yet)
character_name = character.get("name", "Investigator")
if len(st.session_state["messages"]) == 0:
	opening_scene = f"""
The taxi hums steadily along the winding mountain road, its wipers smearing rain across the windshield. You sit in the back seat beside your suitcase—the sum of your old life—on your way to a new beginning in Arkham. The driver, a thin man in a worn cap, hasn’t spoken much. Only the low hiss of the tires and the rhythmic drone of the engine fill the silence.

As the car climbs higher, fog begins to roll in—thick, gray, and slow-moving. The landscape outside grows sparse: no other cars, no houses, only black trees leaning under the weight of the mist. Then, with a sputter and a cough, the engine falters.

“Damn it,” the driver mutters, steering the vehicle to the roadside. He tries the ignition twice, then sighs. “No luck. We’re near a village called **Emberhead**—just over that hill.” He gestures towards faint lights in the mist. “You’ll have to see if you can find a place to stay the night there. I’ll go and look for a mechanic.”

You step out into the damp air, clutching your coat tighter. The road behind you disappears into the mist. Ahead, through the drizzle, the village of **Emberhead** waits—silent except for the distant crackle of unseen fires.

Your journey to a new life has taken an unexpected detour.

*What would you like to do, {character_name}?*
"""

	# Add opening scene to messages
	st.session_state["messages"].append({"role": "assistant", "content": opening_scene})
	
	# Log opening scene
	log_message("assistant", opening_scene, st.session_state.get("current_scene", "arrival_village"))

# Display chat history
for msg in st.session_state["messages"]:
	role = msg["role"]
	# Use custom avatar for user messages if available
	if role == "user" and user_avatar:
		with st.chat_message("user", avatar=user_avatar):
			st.markdown(msg["content"])
	else:
		with st.chat_message(role):
			st.markdown(msg["content"]) 

# User input
user_text = st.chat_input("Talk to the KP. Describe your actions, thoughts, or checks...")
if user_text:
	# Add user message to history
	st.session_state["messages"].append({"role": "user", "content": user_text})
	with st.chat_message("user", avatar=user_avatar):
		st.markdown(user_text)
	
	# Log user message
	log_message("user", user_text, st.session_state.get("current_scene", "arrival_village"))

	# Get KP response using LangGraph agent
	with st.chat_message("assistant"):
		with st.spinner("KP is thinking..."):
			try:
				api_key = st.session_state.get("openai_api_key", "")
				current_scene = st.session_state.get("current_scene", "arrival_village")
				
				result = get_kp_response(
					user_input=user_text,
					character=character,
					chat_history=st.session_state["messages"][:-1],  # Exclude current message
					api_key=api_key,
					current_scene=current_scene
				)
				
				kp_reply = result["response"]
				new_scene = result.get("current_scene", current_scene)
				updated_character = result.get("character", character)
				
				st.markdown(kp_reply)
				st.session_state["messages"].append({"role": "assistant", "content": kp_reply})
				
				# Log keeper response
				log_message("assistant", kp_reply, new_scene)
				
				# Update character state (especially SAN if changed)
				if updated_character and updated_character.get("san") != character.get("san"):
					st.session_state["character"] = updated_character
					# Debug: show SAN change
					if st.session_state.get("_debug_mode", False):
						st.info(f"🔍 DEBUG: SAN changed from {character.get('san')} to {updated_character.get('san')}")
					st.rerun()  # Rerun to update sidebar with new SAN value
				
				# Update scene state
				if new_scene != current_scene:
					# Debug: show scene change
					if st.session_state.get("_debug_mode", False):
						st.info(f"🔍 DEBUG: Scene changing from '{current_scene}' to '{new_scene}'")
					st.session_state["current_scene"] = new_scene
					st.rerun()  # Rerun to update sidebar scene display
			except Exception as e:
				error_msg = f"⚠️ Error: {str(e)}\n\nPlease check your OPENAI_API_KEY and ensure LangGraph dependencies are installed."
				st.error(error_msg)
				st.session_state["messages"].append({"role": "assistant", "content": error_msg})


