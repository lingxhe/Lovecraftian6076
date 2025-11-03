import streamlit as st
from utils import initialize_session_state
from agents.kp_agent import get_kp_response

initialize_session_state()

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
		st.text(scene_info.get("name", scene_id))
		st.caption(scene_info.get("description", ""))
	
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
	
	# Restart button
	st.divider()
	if st.button("🔄 Restart Conversation", use_container_width=True, type="secondary"):
		# Clear messages
		st.session_state["messages"] = []
		# Reset scene to arrival
		st.session_state["current_scene"] = "arrival"
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
	st.session_state["current_scene"] = "arrival"

# Generate opening scene if this is the first time (no messages yet)
character_name = character.get("name", "Investigator")
if len(st.session_state["messages"]) == 0:
	opening_scene = f"""The long-distance bus groans and shudders as it comes to an abrupt halt. Rain patters steadily against the windows, and the dim interior lights flicker uncertainly. Outside, it is just past noon—clouds cloak the sun and lend everything a pale, uneasy glow.

Through the fogged glass, you can make out the shape of a small village in the distance: **Ashbury**. The driver turns to address the few remaining passengers with an apologetic expression.

"Sorry folks," he says, his voice carrying a hint of weariness. "The engine's acting up. We won't be able to continue until later, and the nearest mechanic is in Ashbury. I'll take you there—it's just a short walk. There's an inn where you can wait this out."

You gather your belongings as the driver leads the way. The path to Ashbury is muddy and uneven, with an unsettling quiet that seems to press in around you. As you approach the village, a few windows show dim light, but the place feels...empty. Too quiet for a place that should have life.

Welcome to Ashbury, {character_name}. The day stretches ahead, and something tells you this is not going to be a simple stopover.

*What would you like to do?*"""

	# Add opening scene to messages
	st.session_state["messages"].append({"role": "assistant", "content": opening_scene})

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

	# Get KP response using LangGraph agent
	with st.chat_message("assistant"):
		with st.spinner("KP is thinking..."):
			try:
				api_key = st.session_state.get("openai_api_key", "")
				current_scene = st.session_state.get("current_scene", "arrival")
				
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


