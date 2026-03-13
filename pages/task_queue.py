import streamlit as st
from core.tasks import (
    get_my_tasks,
    get_team_tasks,
    get_waiting_tasks,
    complete_task,
    get_age_indicator,
    get_task_age_days,
)


def task_queue_page():
    st.title("Task Queue")

    tab_mine, tab_team, tab_waiting = st.tabs(["My Tasks", "Team Tasks", "Waiting"])

    with tab_mine:
        _my_tasks_tab()

    with tab_team:
        _team_tasks_tab()

    with tab_waiting:
        _waiting_tab()


def _render_task_row(task: dict, show_job: bool = True):
    indicator = get_age_indicator(task)
    age = get_task_age_days(task)
    age_str = f"{age}d" if age > 0 else "today"
    assigned = task.get("assigned_to", "—")
    job_name = (task.get("jobs") or {}).get("job_name", "—")
    priority = task.get("priority", "Normal")
    priority_badge = " ⚡" if priority == "Urgent" else " 🚨" if priority == "Critical" else ""

    c1, c2 = st.columns([6, 1])
    with c1:
        job_part = f" — <span style='color:gray'>{job_name}</span>" if show_job else ""
        st.markdown(
            f"{indicator}{priority_badge} **{task['title']}**{job_part} "
            f"<span style='color:gray;font-size:0.85em'>({assigned}, {age_str})</span>",
            unsafe_allow_html=True,
        )
    with c2:
        if st.button("✓", key=f"tq_done_{task['id']}", help="Mark complete", use_container_width=True):
            complete_task(task["id"])
            st.rerun()


def _my_tasks_tab():
    tasks = get_my_tasks(assigned_to="Karl")
    if not tasks:
        st.info("No open tasks assigned to you.")
        return

    # Sort oldest first
    tasks = sorted(tasks, key=lambda t: get_task_age_days(t), reverse=True)

    # Summary metrics
    red = sum(1 for t in tasks if get_age_indicator(t) == "🔴")
    yellow = sum(1 for t in tasks if get_age_indicator(t) == "🟡")
    c1, c2, c3 = st.columns(3)
    c1.metric("Total", len(tasks))
    c2.metric("🔴 Overdue", red)
    c3.metric("🟡 Aging", yellow)
    st.divider()

    for task in tasks:
        _render_task_row(task)


def _team_tasks_tab():
    tasks = get_team_tasks()
    if not tasks:
        st.info("No open tasks assigned to the team.")
        return

    # Group by assigned_to
    grouped: dict[str, list] = {}
    for t in tasks:
        role = t.get("assigned_to", "Unknown")
        grouped.setdefault(role, []).append(t)

    for role, role_tasks in sorted(grouped.items()):
        oldest = max(get_task_age_days(t) for t in role_tasks)
        oldest_str = f"{oldest}d" if oldest > 0 else "today"
        st.markdown(f"**{role}** — {len(role_tasks)} task(s), oldest: {oldest_str}")
        for task in role_tasks:
            _render_task_row(task)
        st.markdown("---")


def _waiting_tab():
    tasks = get_waiting_tasks()
    if not tasks:
        st.info("Nothing currently waiting on anyone.")
        return

    # Group by waiting_on
    grouped: dict[str, list] = {}
    for t in tasks:
        role = t.get("waiting_on", "Unknown")
        grouped.setdefault(role, []).append(t)

    for role, role_tasks in sorted(grouped.items()):
        st.markdown(f"**Waiting on {role}**")
        for task in role_tasks:
            indicator = get_age_indicator(task)
            age = get_task_age_days(task)
            age_str = f"{age}d" if age > 0 else "today"
            job_name = (task.get("jobs") or {}).get("job_name", "—")
            st.markdown(
                f"&nbsp;&nbsp;{indicator} {task['title']} — <span style='color:gray'>{job_name} ({age_str})</span>",
                unsafe_allow_html=True,
            )
        st.markdown("---")
