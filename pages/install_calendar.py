import streamlit as st
from datetime import date, timedelta
from core.jobs import get_install_jobs, get_all_jobs, update_job
from core.constants import INSTALL_STATUSES


def install_calendar_page():
    st.title("Install Schedule")

    # Week navigation
    if "cal_week_offset" not in st.session_state:
        st.session_state.cal_week_offset = 0

    today = date.today()
    # Start on Monday of the current offset week
    monday = today - timedelta(days=today.weekday()) + timedelta(weeks=st.session_state.cal_week_offset)
    sunday = monday + timedelta(days=6)

    c1, c2, c3 = st.columns([1, 4, 1])
    with c1:
        if st.button("← Prev", use_container_width=True):
            st.session_state.cal_week_offset -= 1
            st.rerun()
    with c2:
        st.markdown(
            f"<h4 style='text-align:center'>Week of {monday.strftime('%b %d, %Y')}</h4>",
            unsafe_allow_html=True,
        )
    with c3:
        if st.button("Next →", use_container_width=True):
            st.session_state.cal_week_offset += 1
            st.rerun()

    # Schedule install form
    if st.button("＋ Schedule Install", type="primary"):
        st.session_state.show_schedule_form = True

    if st.session_state.get("show_schedule_form"):
        _schedule_install_form()
        st.divider()

    # Calendar grid
    jobs = get_install_jobs(start_date=monday, end_date=sunday)
    _render_week(monday, jobs)


def _render_week(monday: date, jobs: list[dict]):
    days = [monday + timedelta(days=i) for i in range(7)]
    day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    # Group jobs by date
    by_date: dict[str, list] = {}
    for j in jobs:
        d = j.get("install_date", "")
        by_date.setdefault(d, []).append(j)

    cols = st.columns(7)
    for i, (day, name) in enumerate(zip(days, day_names)):
        with cols[i]:
            day_str = day.isoformat()
            is_today = day == date.today()
            header = f"**{name}**\n{day.strftime('%m/%d')}"
            if is_today:
                st.markdown(f"🔵 {header}", unsafe_allow_html=False)
            else:
                st.markdown(header)

            day_jobs = by_date.get(day_str, [])
            if not day_jobs:
                st.caption("—")
            for job in day_jobs:
                status = job.get("install_status", "Scheduled")
                crew = job.get("installer_crew", "")
                icon = {"Scheduled": "📅", "In Progress": "🔨", "Complete": "✅"}.get(status, "")
                st.markdown(f"{icon} **{job['job_name']}**")
                if crew:
                    st.caption(crew)
                # Quick status update
                new_status = st.selectbox(
                    "Status",
                    INSTALL_STATUSES,
                    index=INSTALL_STATUSES.index(status) if status in INSTALL_STATUSES else 0,
                    key=f"cal_status_{job['id']}",
                    label_visibility="collapsed",
                )
                if new_status != status:
                    update_job(job["id"], install_status=new_status)
                    st.rerun()


def _schedule_install_form():
    all_jobs = get_all_jobs()
    job_options = {j["job_name"]: j["id"] for j in all_jobs}

    with st.form("schedule_install_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            selected_job = st.selectbox("Job", options=list(job_options.keys()))
            install_date = st.date_input("Install Date")
        with c2:
            installer_crew = st.text_input("Crew", placeholder="e.g. Team A")
            install_status = st.selectbox("Status", INSTALL_STATUSES)

        c_submit, c_cancel = st.columns(2)
        with c_submit:
            submitted = st.form_submit_button("Schedule", type="primary", use_container_width=True)
        with c_cancel:
            cancelled = st.form_submit_button("Cancel", use_container_width=True)

        if submitted:
            update_job(
                job_options[selected_job],
                install_date=install_date,
                installer_crew=installer_crew,
                install_status=install_status,
                stage="Install",
            )
            st.success(f"Scheduled: {selected_job} on {install_date}")
            st.session_state.show_schedule_form = False
            st.rerun()
        if cancelled:
            st.session_state.show_schedule_form = False
            st.rerun()
