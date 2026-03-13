import streamlit as st
from core.jobs import get_jobs_by_stage, create_job, get_all_jobs
from core.tasks import get_open_task_count, has_red_tasks
from core.constants import STAGES, INSTALL_TYPES, ROLES
from core.templates import get_template_names
from datetime import date


def jobs_kanban_page():
    st.title("Jobs")

    col_title, col_btn = st.columns([5, 1])
    with col_btn:
        if st.button("＋ New Job", type="primary", use_container_width=True):
            st.session_state.show_new_job_form = True

    if st.session_state.get("show_new_job_form"):
        _new_job_form()
        st.divider()

    _kanban_board()


def _new_job_form():
    st.subheader("New Job")
    template_names = get_template_names()
    template_options = ["None"] + template_names

    with st.form("new_job_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            job_name = st.text_input("Job Name *", placeholder="e.g. Johnson Kitchen")
            builder = st.text_input("Builder", placeholder="e.g. Selkirk Builders")
            install_type = st.selectbox("Install Type", INSTALL_TYPES)
            install_date = st.date_input("Install Date", value=None)
        with c2:
            client_name = st.text_input("Client Name", placeholder="e.g. Johnson Family")
            responsible_pm = st.selectbox("Responsible PM", ROLES, index=0)
            template = st.selectbox("Task Template", template_options)
            stage = st.selectbox("Starting Stage", STAGES)

        notes = st.text_area("Notes", height=60)

        c_submit, c_cancel = st.columns([1, 1])
        with c_submit:
            submitted = st.form_submit_button("Create Job", type="primary", use_container_width=True)
        with c_cancel:
            cancelled = st.form_submit_button("Cancel", use_container_width=True)

        if submitted:
            if not job_name.strip():
                st.error("Job Name is required.")
            else:
                job = create_job(
                    job_name=job_name.strip(),
                    builder=builder.strip(),
                    client_name=client_name.strip(),
                    responsible_pm=responsible_pm,
                    stage=stage,
                    install_type=install_type,
                    install_date=install_date if install_date else None,
                    notes=notes.strip(),
                    template_name=template if template != "None" else None,
                )
                st.success(f"Created: {job['job_name']}")
                st.session_state.show_new_job_form = False
                st.rerun()

        if cancelled:
            st.session_state.show_new_job_form = False
            st.rerun()


def _kanban_board():
    cols = st.columns(len(STAGES))

    for i, stage in enumerate(STAGES):
        with cols[i]:
            jobs = get_jobs_by_stage(stage)
            st.markdown(f"**{stage}** <span style='color:gray'>({len(jobs)})</span>", unsafe_allow_html=True)
            st.markdown("---")

            if not jobs:
                st.caption("—")
                continue

            for job in jobs:
                _job_card(job, stage)


def _job_card(job: dict, stage: str):
    job_id = job["id"]
    task_count = get_open_task_count(job_id)
    red = has_red_tasks(job_id)
    alert = " 🔴" if red else ""

    install_date = job.get("install_date")
    date_line = f"📅 {install_date}" if install_date else ""

    builder = job.get("builder", "")
    builder_line = f"<span style='color:gray;font-size:0.85em'>{builder}</span>" if builder else ""

    task_line = f"<span style='color:gray;font-size:0.85em'>{task_count} task{'s' if task_count != 1 else ''}</span>"

    with st.container(border=True):
        st.markdown(
            f"**{job['job_name']}**{alert}<br>{builder_line}<br>{task_line}"
            + (f"<br><span style='font-size:0.85em'>{date_line}</span>" if date_line else ""),
            unsafe_allow_html=True,
        )
        if st.button("Open", key=f"open_{job_id}", use_container_width=True):
            st.session_state.current_page = "job_detail"
            st.session_state.selected_job_id = job_id
            st.rerun()
