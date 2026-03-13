import streamlit as st

st.set_page_config(
    page_title="Pocket PM",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Mobile-friendly CSS
st.markdown("""
<style>
/* Larger tap targets on mobile */
.stButton > button {
    min-height: 2.5rem;
}
/* Reduce padding on mobile */
@media (max-width: 768px) {
    .block-container {
        padding: 0.5rem 0.75rem 2rem;
    }
    /* Stack nav buttons more comfortably */
    .stButton > button {
        font-size: 0.75rem;
        padding: 0.4rem 0.2rem;
    }
}
/* Hide Streamlit branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Page imports
from pages.home import home_page
from pages.jobs_kanban import jobs_kanban_page
from pages.job_detail import job_detail_page
from pages.task_queue import task_queue_page
from pages.install_calendar import install_calendar_page
from pages.settings import settings_page


def nav_button(label: str, page: str, current: str):
    active = current == page
    if st.button(label, use_container_width=True, type="primary" if active else "secondary"):
        st.session_state.current_page = page
        st.rerun()


def main():
    if "current_page" not in st.session_state:
        st.session_state.current_page = "home"

    current = st.session_state.current_page

    # Top navigation — 5 columns (removed empty 6th)
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        nav_button("🏠 Home", "home", current)
    with c2:
        nav_button("📋 Jobs", "jobs", current)
    with c3:
        nav_button("✅ Tasks", "tasks", current)
    with c4:
        nav_button("📅 Schedule", "schedule", current)
    with c5:
        nav_button("⚙️ Settings", "settings", current)

    st.markdown("---")

    if current == "home":
        home_page()
    elif current == "jobs":
        jobs_kanban_page()
    elif current == "job_detail":
        job_detail_page()
    elif current == "tasks":
        task_queue_page()
    elif current == "schedule":
        install_calendar_page()
    elif current == "settings":
        settings_page()
    else:
        home_page()


if __name__ == "__main__":
    main()
