import sys
from pathlib import Path
import streamlit as st

# Add project root to path FIRST
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = None

# Log out Sidebar
with st.sidebar:
    if st.session_state.logged_in:
        st.markdown(f"**Logged in as:** {st.session_state.username}")

        if st.button("Log out"):
            st.session_state.clear()
            st.rerun()
    else:
        st.markdown("**Not logged in**")


# Pages
Classes = st.Page(
    "Navigation/multi_room_classes.py",
    title="Multi Room Classes",
    icon=":material/school:",
    default=False,
)

Meetings = st.Page(
    "Navigation/avg_meeting_time.py",
    title="Average Meeting Duration",
    icon=":material/groups:",
    default=False,
)

Rooms = st.Page(
    "Navigation/top_rooms.py",
    title="Top Rooms by Utilization",
    icon=":material/view_list:",
    default=False,
)

Sections = st.Page(
    "Navigation/sections_by_day.py",
    title="Sections by day",
    icon=":material/calendar_month:",
    default=False,
)

Departments = st.Page(
    "Navigation/top_departments.py",
    title="Top Departments",
    icon=":material/business:",
    default=False,
)

Prereqs = st.Page(
    "Navigation/class_without_prereqs.py",
    title="Class Without Prerequisites",
    icon=":material/menu_book:",
    default=False,
)


login_page = st.Page(
    "Navigation/sign_in.py", title="Log in", icon=":material/login:", default=False
)

Chatbot = st.Page(
    "chatbot.py", title="Chatbot", icon=":material/robot_2:", default=True
)

if st.session_state.logged_in:
    nav = st.navigation(
        {
            "Navigation": [
                Chatbot,
                Classes,
                Meetings,
                Rooms,
                Sections,
                Departments,
                Prereqs,
            ]
        }
    )
else:
    nav = st.navigation([login_page])

# st.audio("audio/audio-club-amapiano-319840.wav", start_time= 0, loop= True, autoplay=True)
nav.run()
