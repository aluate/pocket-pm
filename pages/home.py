import streamlit as st
from core.tasks import get_my_tasks, get_waiting_tasks, complete_task, create_task, get_age_indicator, get_task_age_days
from core.jobs import get_all_jobs, get_install_jobs
from core.constants import ROLES, TASK_TYPES
from datetime import date, timedelta


def home_page():
    st.title("Pocket PM")

    # --- Quick Add Task (always visible, top of page) ---
    _quick_add_task()
    st.divider()

    col1, col2 = st.columns([3, 2])

    with col1:
        _my_tasks_section()

    with col2:
        _waiting_section()
        st.markdown("---")
        _install_schedule_section()


def _quick_add_task():
    jobs = get_all_jobs()
    if not jobs:
        st.info("No jobs yet. Create a job in the Jobs page first.")
        return

    job_options = {j["job_name"]: j["id"] for j in jobs}

    with st.form("quick_add_task", clear_on_submit=True):
        c1, c2, c3, c4 = st.columns([3, 3, 2, 1])
        with c1:
            selected_job = st.selectbox("Job", options=list(job_options.keys()), label_visibility="collapsed", placeholder="Job")
        with c2:
            task_title = st.text_input("Task", placeholder="Task description", label_visibility="collapsed")
        with c3:
            assigned_to = st.selectbox("Assign to", options=ROLES, label_visibility="collapsed")
        with c4:
            submitted = st.form_submit_button("＋ Add", use_container_width=True, type="primary")

        if submitted and task_title.strip():
            create_task(
                job_id=job_options[selected_job],
                title=task_title.strip(),
                assigned_to=assigned_to,
            )
            st.success(f"Added: {task_title}")
            st.rerun()


def _my_tasks_section():
    st.subheader("My Tasks")
    tasks = get_my_tasks(assigned_to="Karl")

    if not tasks:
        st.caption("No open tasks. Nice work.")
        return

    # Sort by age descending (oldest first)
    tasks = sorted(tasks, key=lambda t: get_task_age_days(t), reverse=True)

    for task in tasks:
        job_name = (task.get("jobs") or {}).get("job_name", "—")
        age = get_task_age_days(task)
        indicator = get_age_indicator(task)
        age_str = f"{age}d" if age > 0 else "today"
        priority = task.get("priority", "Normal")
        priority_badge = " ⚡" if priority == "Urgent" else " 🚨" if priority == "Critical" else ""

        col_text, col_btn = st.columns([5, 1])
        with col_text:
            st.markdown(
                f"{indicator}{priority_badge} **{task['title']}** — {job_name} "
                f"<span style='color:gray;font-size:0.8em'>({age_str})</span>",
                unsafe_allow_html=True,
            )
        with col_btn:
            if st.button("✓", key=f"done_{task['id']}", help="Mark complete"):
                complete_task(task["id"], job_id=task.get("job_id"))
                st.rerun()


def _waiting_section():
    st.subheader("Waiting On")
    tasks = get_waiting_tasks()

    if not tasks:
        st.caption("Nothing blocked.")
        return

    # Group by waiting_on
    grouped: dict[str, list] = {}
    for t in tasks:
        role = t.get("waiting_on", "Unknown")
        grouped.setdefault(role, []).append(t)

    for role, role_tasks in sorted(grouped.items()):
        st.markdown(f"**{role}**")
        for task in role_tasks:
            job_name = (task.get("jobs") or {}).get("job_name", "—")
            indicator = get_age_indicator(task)
            st.markdown(
                f"&nbsp;&nbsp;{indicator} {task['title']} — <span style='color:gray'>{job_name}</span>",
                unsafe_allow_html=True,
            )


def _install_schedule_section():
    st.subheader("Installs")
    today = date.today()
    two_weeks = today + timedelta(days=14)
    jobs = get_install_jobs(start_date=today, end_date=two_weeks)

    if not jobs:
        st.caption("No installs scheduled in next 2 weeks.")
        return

    for job in jobs:
        install_date = job.get("install_date", "")
        status = job.get("install_status", "")
        status_icon = {"Scheduled": "📅", "In Progress": "🔨", "Complete": "✅"}.get(status, "")
        st.markdown(f"{status_icon} **{install_date}** — {job['job_name']}")
