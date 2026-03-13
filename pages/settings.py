import streamlit as st
from core.templates import get_template_names, get_template_tasks, seed_templates
from core.supabase_client import get_client
from core.constants import ROLES, TASK_TYPES, STAGES


def settings_page():
    st.title("Settings")

    tab_templates, tab_roles, tab_connection = st.tabs(["Task Templates", "Roles", "Connection"])

    with tab_templates:
        _templates_tab()

    with tab_roles:
        _roles_tab()

    with tab_connection:
        _connection_tab()


def _templates_tab():
    st.subheader("Task Templates")

    if st.button("Seed Default Templates (Kitchen, Bathroom, Closet)"):
        count = seed_templates()
        if count > 0:
            st.success(f"Seeded {count} template tasks.")
        else:
            st.info("Templates already exist — nothing seeded.")

    names = get_template_names()
    if not names:
        st.caption("No templates found. Click 'Seed Default Templates' to populate.")
        return

    selected = st.selectbox("View template", names)
    if selected:
        tasks = get_template_tasks(selected)
        if tasks:
            import pandas as pd
            df = pd.DataFrame(tasks)[["sort_order", "task_type", "title", "assigned_to"]]
            df.columns = ["Order", "Type", "Task", "Default Assignee"]
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.caption("No tasks in this template.")


def _roles_tab():
    st.subheader("Assignable Roles")
    st.caption("These roles are used for task assignment and waiting-on tracking.")
    for role in ROLES:
        st.markdown(f"• {role}")
    st.markdown("---")
    st.caption("To modify roles, update `core/constants.py` and redeploy.")


def _connection_tab():
    st.subheader("Supabase Connection")
    try:
        db = get_client()
        result = db.table("jobs").select("id", count="exact").execute()
        job_count = result.count or 0
        st.success(f"Connected — {job_count} job(s) in database.")
    except Exception as e:
        st.error(f"Connection failed: {e}")
