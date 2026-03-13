import streamlit as st
from core.jobs import get_job, update_job, update_job_stage
from core.tasks import (
    get_tasks_for_job,
    create_task,
    complete_task,
    update_task,
    delete_task,
    get_age_indicator,
    get_task_age_days,
)
from core.photos import upload_photo, get_photos_for_job
from core.constants import STAGES, TASK_TYPES, ROLES, TASK_STATUSES, TASK_PRIORITIES, INSTALL_TYPES, INSTALL_STATUSES, TASK_TYPE_ORDER


def job_detail_page():
    job_id = st.session_state.get("selected_job_id")
    if not job_id:
        st.error("No job selected.")
        if st.button("← Back to Jobs"):
            st.session_state.current_page = "jobs"
            st.rerun()
        return

    job = get_job(job_id)
    if not job:
        st.error("Job not found.")
        return

    # Breadcrumb
    if st.button("← Jobs"):
        st.session_state.current_page = "jobs"
        st.rerun()

    st.title(job["job_name"])

    # --- Job Header ---
    _job_header(job)
    st.divider()

    # --- Tasks ---
    st.subheader("Tasks")
    _quick_add_task_for_job(job_id)
    _tasks_section(job_id)
    st.divider()

    # --- Photos ---
    st.subheader("Photos")
    _photos_section(job_id)


def _job_header(job: dict):
    c1, c2, c3 = st.columns([3, 2, 1])

    with c1:
        job_num = job.get("job_number", "")
        builder = job.get("builder", "—")
        client = job.get("client_name", "—")
        pm = job.get("responsible_pm", "—")
        install_date = job.get("install_date", "—")
        install_type = job.get("install_type", "—")
        num_str = f" &nbsp; **Job #:** {job_num}" if job_num else ""
        st.markdown(
            f"**Builder:** {builder} &nbsp; **Client:** {client} &nbsp; **PM:** {pm}{num_str}<br>"
            f"**Install:** {install_date} ({install_type})",
            unsafe_allow_html=True,
        )

    with c2:
        current_stage = job.get("stage", STAGES[0])
        new_stage = st.selectbox(
            "Stage",
            STAGES,
            index=STAGES.index(current_stage) if current_stage in STAGES else 0,
            key=f"stage_select_{job['id']}",
        )
        if new_stage != current_stage:
            update_job_stage(job["id"], new_stage)
            st.rerun()

    with c3:
        if st.button("Edit Job", use_container_width=True):
            st.session_state[f"editing_job_{job['id']}"] = True

    if st.session_state.get(f"editing_job_{job['id']}"):
        _edit_job_form(job)


def _edit_job_form(job: dict):
    with st.form(f"edit_job_{job['id']}"):
        c1, c2 = st.columns(2)
        with c1:
            job_name = st.text_input("Job Name", value=job.get("job_name", ""))
            job_number = st.text_input("Job #", value=job.get("job_number", ""))
            builder = st.text_input("Builder", value=job.get("builder", ""))
            install_type = st.selectbox(
                "Install Type",
                INSTALL_TYPES,
                index=INSTALL_TYPES.index(job.get("install_type", "Install")) if job.get("install_type") in INSTALL_TYPES else 0,
            )
        with c2:
            client_name = st.text_input("Client", value=job.get("client_name", ""))
            install_date_val = job.get("install_date")
            install_date = st.date_input("Install Date", value=install_date_val or None)
            install_status = st.selectbox(
                "Install Status",
                INSTALL_STATUSES,
                index=INSTALL_STATUSES.index(job.get("install_status", "Scheduled")) if job.get("install_status") in INSTALL_STATUSES else 0,
            )
        installer_crew = st.text_input("Installer Crew", value=job.get("installer_crew", ""))
        notes = st.text_area("Notes", value=job.get("notes", ""), height=80)

        c_save, c_cancel = st.columns(2)
        with c_save:
            saved = st.form_submit_button("Save", type="primary", use_container_width=True)
        with c_cancel:
            cancelled = st.form_submit_button("Cancel", use_container_width=True)

        if saved:
            update_job(
                job["id"],
                job_name=job_name,
                job_number=job_number,
                builder=builder,
                client_name=client_name,
                install_type=install_type,
                install_date=install_date,
                install_status=install_status,
                installer_crew=installer_crew,
                notes=notes,
            )
            st.session_state[f"editing_job_{job['id']}"] = False
            st.rerun()
        if cancelled:
            st.session_state[f"editing_job_{job['id']}"] = False
            st.rerun()


def _quick_add_task_for_job(job_id: str):
    with st.form(f"quick_add_{job_id}", clear_on_submit=True):
        c1, c2, c3, c4, c5 = st.columns([4, 2, 2, 2, 1])
        with c1:
            title = st.text_input("Task", placeholder="Task description", label_visibility="collapsed")
        with c2:
            task_type = st.selectbox("Type", TASK_TYPES, label_visibility="collapsed")
        with c3:
            assigned_to = st.selectbox("Assign", ROLES, label_visibility="collapsed")
        with c4:
            wo_number = st.text_input("WO#", placeholder="WO# (optional)", label_visibility="collapsed")
        with c5:
            submitted = st.form_submit_button("＋", use_container_width=True, type="primary")
        if submitted and title.strip():
            create_task(
                job_id=job_id,
                title=title.strip(),
                task_type=task_type,
                assigned_to=assigned_to,
                wo_number=wo_number.strip(),
            )
            st.rerun()


def _tasks_section(job_id: str):
    tasks = get_tasks_for_job(job_id, include_complete=False)

    if not tasks:
        st.caption("No open tasks.")
        return

    # Group by task_type in order
    grouped: dict[str, list] = {}
    for t in tasks:
        ttype = t.get("task_type", "Field")
        grouped.setdefault(ttype, []).append(t)

    for ttype in TASK_TYPE_ORDER:
        if ttype not in grouped:
            continue
        st.markdown(f"**{ttype.upper()}**")
        for task in grouped[ttype]:
            _task_row(task)


def _task_row(task: dict):
    indicator = get_age_indicator(task)
    age = get_task_age_days(task)
    age_str = f"{age}d" if age > 0 else "today"
    assigned = task.get("assigned_to", "—")
    waiting = task.get("waiting_on")
    waiting_str = f" ⏳ waiting on {waiting}" if waiting else ""
    priority = task.get("priority", "Normal")
    priority_badge = " ⚡" if priority == "Urgent" else " 🚨" if priority == "Critical" else ""
    wo = task.get("wo_number", "")
    wo_str = f" &nbsp;<span style='background:#2d2d2d;color:#aaa;padding:1px 5px;border-radius:3px;font-size:0.78em'>WO#{wo}</span>" if wo else ""

    c1, c2, c3, c4 = st.columns([5, 2, 1, 1])
    with c1:
        st.markdown(
            f"{indicator}{priority_badge} {task['title']}{wo_str} "
            f"<span style='color:gray;font-size:0.85em'>— {assigned} ({age_str}){waiting_str}</span>",
            unsafe_allow_html=True,
        )
    with c2:
        # Delegate inline
        key_delegate = f"delegate_{task['id']}"
        if st.session_state.get(key_delegate):
            with st.form(f"delegate_form_{task['id']}"):
                new_assign = st.selectbox("Assign to", ROLES, key=f"new_assign_{task['id']}", label_visibility="collapsed")
                new_waiting = st.selectbox("Waiting on", ["—"] + ROLES, key=f"new_wait_{task['id']}", label_visibility="collapsed")
                c_s, c_c = st.columns(2)
                with c_s:
                    if st.form_submit_button("Save", use_container_width=True):
                        update_task(
                            task["id"],
                            assigned_to=new_assign,
                            waiting_on=None if new_waiting == "—" else new_waiting,
                            status="Waiting" if new_waiting != "—" else task.get("status", "Open"),
                        )
                        st.session_state[key_delegate] = False
                        st.rerun()
                with c_c:
                    if st.form_submit_button("Cancel", use_container_width=True):
                        st.session_state[key_delegate] = False
                        st.rerun()
        else:
            if st.button("→ Delegate", key=f"del_btn_{task['id']}", use_container_width=True):
                st.session_state[key_delegate] = True
                st.rerun()
    with c3:
        if st.button("✓", key=f"done_{task['id']}", help="Mark complete", use_container_width=True):
            complete_task(task["id"])
            st.rerun()
    with c4:
        if st.button("🗑", key=f"del_{task['id']}", help="Delete task", use_container_width=True):
            delete_task(task["id"])
            st.rerun()


def _photos_section(job_id: str):
    uploaded = st.file_uploader(
        "Upload photos/videos",
        accept_multiple_files=True,
        type=["jpg", "jpeg", "png", "gif", "webp", "mp4", "mov", "heic"],
        key=f"photo_upload_{job_id}",
    )
    if uploaded:
        for f in uploaded:
            with st.spinner(f"Uploading {f.name}..."):
                upload_photo(
                    file_bytes=f.read(),
                    filename=f.name,
                    job_id=job_id,
                )
        st.success(f"Uploaded {len(uploaded)} file(s).")
        st.rerun()

    # Display existing photos
    photos = get_photos_for_job(job_id)
    if not photos:
        st.caption("No photos yet.")
        return

    # Show in a grid (3 columns)
    photo_files = [p for p in photos if not p["filename"].lower().endswith((".mp4", ".mov"))]
    video_files = [p for p in photos if p["filename"].lower().endswith((".mp4", ".mov"))]

    if photo_files:
        cols = st.columns(3)
        for i, photo in enumerate(photo_files):
            with cols[i % 3]:
                st.image(photo["file_url"], caption=photo.get("notes", photo["filename"]), use_column_width=True)

    if video_files:
        for v in video_files:
            st.video(v["file_url"])
