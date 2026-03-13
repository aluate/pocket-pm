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
/* Larger tap targets everywhere */
.stButton > button {
    min-height: 2.75rem;
}
/* Comfortable nav on any screen width */
@media (max-width: 768px) {
    .block-container {
        padding: 0.5rem 0.75rem 2rem;
    }
    .stButton > button {
        font-size: 0.85rem;
        padding: 0.4rem 0.3rem;
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

    # Hide nav when in job detail — back button is enough
    if current != "job_detail":
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            nav_button("🏠 Home", "home", current)
        with c2:
            nav_button("📋 Jobs", "jobs", current)
        with c3:
            nav_button("📅 Schedule", "schedule", current)
        with c4:
            nav_button("⚙️ Settings", "settings", current)
        st.markdown("---")

    if current == "home":
        home_page()
    elif current == "jobs":
        jobs_kanban_page()
    elif current == "job_detail":
        job_detail_page()
    elif current == "schedule":
        install_calendar_page()
    elif current == "settings":
        settings_page()
    else:
        home_page()


if __name__ == "__main__":
    main()
