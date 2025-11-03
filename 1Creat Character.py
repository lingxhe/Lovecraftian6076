import streamlit as st
import random
from utils import initialize_session_state, save_character


st.set_page_config(page_title="CoC Solo · LLM KP", page_icon="🦑", layout="wide", initial_sidebar_state="expanded")
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

st.title("Create Character")
st.caption("Set up your CoC investigator. More attributes can be added later.")

# Story background information
st.info("""
**📖 Story: Alone Against the Flames**

**Identity:** Ordinary person (Investigator, profession optional), preparing to move to a new town to start a new life.

**Opening Scene:** You are taking a long-distance bus. The bus breaks down en route, and the driver takes you to a remote village. Strange events begin to unfold as you discover the villagers are preparing for a sinister ritual.

You are about to begin a journey into the unknown. Your character will navigate through mysterious events, uncovering dark secrets, and ultimately face a terrible choice. Create your investigator below and prepare for what lies ahead...
""")

# Avatar selection (outside form to use buttons)
st.subheader("Avatar Selection")

# Initialize selected avatar in session state
if "selected_avatar" not in st.session_state:
	current_avatar = st.session_state.get("character", {}).get("avatar") if st.session_state.get("character") else None
	st.session_state["selected_avatar"] = current_avatar if current_avatar else "🧑‍🔬"

# Avatar options - just emojis
avatar_options = [
	"🧑‍🔬", "🧑‍🎓", "🧑‍⚕️", "🧑‍🏫", "🧑‍💼", "🧑‍🔧",
	"🧙", "🕵️", "👮", "🎩", "👤", "🧛",
	
]

# Display avatar options in a grid with large emoji + select button
cols_per_row = 6  # fewer columns for larger cells
emoji_style = "font-size: 48px; line-height: 1; text-align:center;"
for i in range(0, len(avatar_options), cols_per_row):
	cols = st.columns(cols_per_row)
	for j, emoji in enumerate(avatar_options[i:i+cols_per_row]):
		with cols[j]:
			# Big emoji preview
			st.markdown(f"<div style='{emoji_style}'>{emoji}</div>", unsafe_allow_html=True)
			# Select button
			is_selected = st.session_state["selected_avatar"] == emoji
			if st.button(
				"Select" if not is_selected else "Selected",
				key=f"avatar_btn_{i+j}",
				use_container_width=True,
				type="primary" if is_selected else "secondary",
			):
				st.session_state["selected_avatar"] = emoji
				st.rerun()

# Show currently selected avatar
if st.session_state["selected_avatar"]:
	st.info(f"Selected avatar: {st.session_state['selected_avatar']}")

# Get current character values for form defaults
current_character = st.session_state.get("character", {})
default_name = current_character.get("name", "") if current_character else ""
default_str = current_character.get("str", 60) if current_character else 60
default_int = current_character.get("int", 60) if current_character else 60
default_pow = current_character.get("pow", 60) if current_character else 60
default_spot = current_character.get("spot", 60) if current_character else 50
default_listen = current_character.get("listen", 60) if current_character else 50
default_stealth = current_character.get("stealth", 60) if current_character else 50
default_charm = current_character.get("charm", 60) if current_character else 50
default_luck = current_character.get("luck", 50) if current_character else 50
default_background = current_character.get("background_story", "") if current_character else ""
# Note: SAN is now calculated from POW, not stored separately

# Initialize luck roll history (outside form)
if "luck_rolls" not in st.session_state:
	st.session_state["luck_rolls"] = []
if "luck_roll_count" not in st.session_state:
	st.session_state["luck_roll_count"] = 0
if "best_luck" not in st.session_state:
	st.session_state["best_luck"] = default_luck

# LUCK - Roll 3 times, keep the best (outside form because st.button can't be in form)
st.subheader("LUCK")
st.caption("Roll 3d6×5 to generate LUCK (can roll 3 times, keep the best result)")

# Show roll history
if st.session_state["luck_rolls"]:
	st.write("Roll history:")
	for i, roll_value in enumerate(st.session_state["luck_rolls"], 1):
		st.write(f"Roll {i}: {roll_value}")
	st.write(f"**Best result: {st.session_state['best_luck']}**")

# Roll button (disabled after 3 rolls)
can_roll = st.session_state["luck_roll_count"] < 3
if can_roll:
	roll_col1, roll_col2 = st.columns([1, 3])
	with roll_col1:
		if st.button("Roll LUCK", type="primary", key="roll_luck_btn"):
			# Roll 3d6
			dice1 = random.randint(1, 6)
			dice2 = random.randint(1, 6)
			dice3 = random.randint(1, 6)
			roll_result = (dice1 + dice2 + dice3) * 5
			
			# Save roll
			st.session_state["luck_rolls"].append(roll_result)
			st.session_state["luck_roll_count"] += 1
			
			# Update best if better
			if roll_result > st.session_state["best_luck"]:
				st.session_state["best_luck"] = roll_result
			
			st.rerun()
	with roll_col2:
		st.caption(f"Rolls remaining: {3 - st.session_state['luck_roll_count']}")
else:
	st.info(f"✓ LUCK finalized: {st.session_state['best_luck']} (3 rolls completed)")

# Get luck value for form submission
luck = st.session_state["best_luck"]

st.divider()

# Core Attributes (outside form for real-time updates)
st.subheader("Core Attributes")
st.caption("Total of STR + INT + POW must not exceed 180")
col1, col2, col3 = st.columns(3)
with col1:
	str_attr = st.number_input("STR (Strength)", min_value=1, max_value=100, value=default_str, key="str_input")
with col2:
	int_attr = st.number_input("INT (Intelligence)", min_value=1, max_value=100, value=default_int, key="int_input")
with col3:
	pow_attr = st.number_input("POW (Power)", min_value=1, max_value=100, value=default_pow, key="pow_input")

# Validate core attributes total (real-time)
core_total = str_attr + int_attr + pow_attr
if core_total > 180:
	st.error(f"⚠️ Core attributes total ({core_total}) exceeds 180! Current: STR={str_attr}, INT={int_attr}, POW={pow_attr}")
else:
	st.info(f"Core attributes total: {core_total}/180")

# Skills (outside form for real-time updates)
st.subheader("Skills")

# Calculate skill points budget (INT * 4, standard CoC rule)
skill_points_budget = int_attr * 4

# Track skill points (excluding LUCK)
st.caption(f"Skill points budget (INT × 4): {skill_points_budget} points (LUCK not included)")

col1, col2, col3 = st.columns(3)
with col1:
	spot = st.number_input("SPOT (Spot Hidden)", min_value=1, max_value=100, value=default_spot, key="spot_input")
	listen = st.number_input("LISTEN", min_value=1, max_value=100, value=default_listen, key="listen_input")
with col2:
	stealth = st.number_input("STEALTH", min_value=1, max_value=100, value=default_stealth, key="stealth_input")
	charm = st.number_input("CHARM", min_value=1, max_value=100, value=default_charm, key="charm_input")
with col3:
	# SAN equals POW
	san = pow_attr
	st.info(f"SAN (Sanity): {san} (equals POW)")
	# Display LUCK (rolled outside form)
	luck_display = st.session_state.get("best_luck", default_luck)
	st.info(f"LUCK: {luck_display} (rolled above)")

# Calculate skill points used (sum of all four skills)
skill_points_used = spot + listen + stealth + charm

# Real-time skill points display with breakdown
skill_breakdown = f"SPOT({spot}) + LISTEN({listen}) + STEALTH({stealth}) + CHARM({charm}) = {skill_points_used}"

if skill_points_used > skill_points_budget:
	st.error(f"⚠️ Skill points used ({skill_points_used}) exceeds budget ({skill_points_budget})!")
	st.caption(skill_breakdown)
else:
	st.info(f"Skill points used: {skill_points_used}/{skill_points_budget} (remaining: {skill_points_budget - skill_points_used})")
	st.caption(skill_breakdown)

st.divider()

# Form for background story and submission
with st.form("character_form"):
	name = st.text_input("Name", value=default_name, placeholder="e.g., Graduate from Arkham", key="name_input")
	background_story = st.text_area("Background Story", value=default_background, placeholder="Enter your character's background story...", height=150, key="background_input")

	submitted = st.form_submit_button("Save Character")

if submitted:
	errors = []
	
	# Validation checks
	if not name.strip():
		errors.append("Please enter a name before saving.")
	
	if core_total > 180:
		errors.append(f"Core attributes total ({core_total}) exceeds 180.")
	
	if skill_points_used > skill_points_budget:
		errors.append(f"Skill points used ({skill_points_used}) exceeds budget ({skill_points_budget}).")
	
	if st.session_state["luck_roll_count"] == 0:
		errors.append("Please roll LUCK at least once before saving.")
	
	if errors:
		for error in errors:
			st.error(error)
	else:
		selected_avatar = st.session_state.get("selected_avatar", "🧑‍🔬")
		# Get luck from session state (may have been updated by roll button)
		luck = st.session_state["best_luck"]
		save_character(
			name,
			str_attr, int_attr, pow_attr,
			spot, listen, stealth, charm, luck,
			san,
			selected_avatar,
			background_story
		)
		st.success("Character saved.")

if st.session_state["character"]:
	st.subheader("Current Character")
	st.json(st.session_state["character"])


