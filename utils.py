import streamlit as st


def initialize_session_state() -> None:

	if "character" not in st.session_state:
		st.session_state["character"] = None
	if "messages" not in st.session_state:
		st.session_state["messages"] = []
	if "current_scene" not in st.session_state:
		st.session_state["current_scene"] = "arrival"


def save_character(
	name: str,
	str_attr: int, int_attr: int, pow_attr: int,
	spot: int, listen: int, stealth: int, charm: int, luck: int,
	san: int,
	avatar: str = None,
	background_story: str = ""
) -> None:

	st.session_state["character"] = {
		"name": name.strip(),
		"str": int(str_attr),
		"int": int(int_attr),
		"pow": int(pow_attr),
		"spot": int(spot),
		"listen": int(listen),
		"stealth": int(stealth),
		"charm": int(charm),
		"luck": int(luck),
		"san": int(san),
		"avatar": avatar,
		"background_story": background_story.strip() if background_story else "",
	}


def generate_kp_reply(user_text: str, character: dict | None) -> str:

	name = character.get("name") if character else "Investigator"
	return (
		f"[KP] {name}, your steps echo in the dust-laden library. A stale odor hangs in the air, and a whispering draft seeps through the window frames.\n"
		f"You just said: '{user_text}'. Somewhere in the stacks, a page rustles. What do you do?"
	)


