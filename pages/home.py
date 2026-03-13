import streamlit as st
from core.tasks import get_my_tasks, get_waiting_tasks, complete_task, create_task, get_age_indicator, get_task_age_days, get_due_label, task_score
from core.jobs import get_all_jobs, get_install_jobs
from core.constants import ROLES, TASK_TYPES
from datetime import date, timedelta

# Tasks with score above this threshold go into "Do Now"
DO_NOW_THRESHOLD = 50


def home_page():
    # --- Upcoming installs strip ---
    _install_strip()

    # --- Quick Add ---
    _quick_add_task()
    st.divider()

    # --- Main queue tabs ---
    tab_queue, tab_watching = st.tabs(["My Queue", "👀 Watching"])

    with tab_queue:
        _queue_section()

    with tab_watching:
        _watching_section()


def _install_strip():
    today = date.today()
    jobs = get_install_jobs(start_date=today, end_date=today + timedelta(days=21))
    if not jobs:
        return
    icons = {"Scheduled": "📅", "In Progress": "🔨", "Complete": "✅"}
    parts = []
    for job in jobs[:5]:  # cap at 5 to keep it compact
        d = job.get("install_date", "")
        status = job.get("install_status", "Scheduled")
        icon = icons.get(status, "📅")
        parts.append(f"{icon} **{d}** {job['job_name']}")
    st.markdown(" &nbsp;|&nbsp; ".join(parts), unsafe_allow_html=True)
    st.markdown("")


def _quick_add_task():
    jobs = get_all_jobs()
    if not jobs:
        return

    job_options = {j["job_name"]: j["id"] for j in jobs}

    with st.form("quick_add_task", clear_on_submit=True):
        c1, c2, c3, c4 = st.columns([3, 3, 2, 1])
        with c1:
            selected_job = st.selectbox("Job", options=list(job_options.keys()), label_visibility="collapsed")
        with c2:
            task_title = st.text_input("Task", placeholder="Quick-add a task…", label_visibility="collapsed")
        with c3:
            assigned_to = st.selectbox("Assign to", options=ROLES, label_visibility="collapsed")
        with c4:
            submitted = st.form_submit_button("＋", use_container_width=True, type="primary")

        if submitted and task_title.strip():
            create_task(
                job_id=job_options[selected_job],
                title=task_title.strip(),
                assigned_to=assigned_to,
            )
            st.rerun()


def _queue_section():
    tasks = get_my_tasks(assigned_to="Karl")

    if not tasks:
        st.caption("Nothing on your plate. Nice work.")
        return

    # Score and sort
    tasks = sorted(tasks, key=task_score, reverse=True)

    do_now = [t for t in tasks if task_score(t) >= DO_NOW_THRESHOLD]
    up_next = [t for t in tasks if task_score(t) < DO_NOW_THRESHOLD]

    if do_now:
        st.markdown("#### 🔴 Do Now")
        for task in do_now:
            _task_row(task)

    if up_next:
        if do_now:
            st.markdown("#### 📋 Up Next")
        for task in up_next:
            _task_row(task)


def _task_row(task: dict):
    job_name = (task.get("jobs") or {}).get("job_name", "—")
    job_id = task.get("job_id")
    age = get_task_age_days(task)
    age_str = f"{age}d" if age > 0 else "today"
    indicator = get_age_indicator(task)
    priority = task.get("priority", "Normal")
    priority_badge = " ⚡" if priority == "Urgent" else " 🚨" if priority == "Critical" else ""
    due = get_due_label(task)
    due_str = f" <span style='color:#e07b00;font-size:0.8em'>{due}</span>" if due else ""

    col_text, col_job, col_btn = st.columns([5, 2, 1])

    with col_text:
        st.markdown(
            f"{indicator}{priority_badge} **{task['title']}**{due_str} "
            f"<span style='color:gray;font-size:0.82em'>({age_str})</span>",
            unsafe_allow_html=True,
        )

    with col_job:
        # Tap job name → go to job detail
        if job_id and st.button(
            job_name,
            key=f"home_job_{task['id']}",
            use_container_width=True,
        ):
            st.session_state.selected_job_id = job_id
            st.session_state.current_page = "job_detail"
            st.rerun()

    with col_btn:
        if st.button("✓", key=f"done_{task['id']}", help="Mark complete", use_container_width=True):
            complete_task(task["id"], job_id=job_id)
            st.rerun()


def _watching_section():
    tasks = get_waiting_tasks()

    if not tasks:
        st.caption("Nothing waiting on others.")
        return

    # Group by who we're waiting on
    grouped: dict[str, list] = {}
    for t in tasks:
        role = t.get("waiting_on") or "Unknown"
        grouped.setdefault(role, []).append(t)

    for role, role_tasks in sorted(grouped.items()):
        st.markdown(f"**{role}**")
        for task in role_tasks:
            job_name = (task.get("jobs") or {}).get("job_name", "—")
            job_id = task.get("job_id")
            age = get_task_age_days(task)
            age_str = f"{age}d" if age > 0 else "today"
            col_text, col_job = st.columns([5, 2])
            with col_text:
                st.markdown(
                    f"🔵 {task['title']} <span style='color:gray;font-size:0.82em'>({age_str})</span>",
                    unsafe_allow_html=True,
                )
            with col_job:
                if job_id and st.button(
                    job_name,
                    key=f"watch_job_{task['id']}",
                    use_container_width=True,
                ):
                    st.session_state.selected_job_id = job_id
                    st.session_state.current_page = "job_detail"
                    st.rerun()
