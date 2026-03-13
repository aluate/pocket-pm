from datetime import date, timedelta
from typing import Optional
from core.supabase_client import get_client
from core.templates import get_template_tasks, SAMPLE_TASKS
from core.constants import STAGES


def _add_business_days(start: date, days: int) -> date:
    current = start
    added = 0
    while added < days:
        current += timedelta(days=1)
        if current.weekday() < 5:
            added += 1
    return current


def _calc_due_date(t: dict, created: date, install: Optional[date]) -> Optional[str]:
    if t.get("due_days_from_created") is not None:
        return _add_business_days(created, t["due_days_from_created"]).isoformat()
    if t.get("due_days_from_install") is not None and install:
        return (install + timedelta(days=t["due_days_from_install"])).isoformat()
    return None


def get_all_jobs() -> list[dict]:
    db = get_client()
    result = db.table("jobs").select("*").order("created_at", desc=True).execute()
    return result.data or []


def get_job(job_id: str) -> Optional[dict]:
    db = get_client()
    result = db.table("jobs").select("*").eq("id", job_id).single().execute()
    return result.data


def create_job(
    job_name: str,
    job_number: str = "",
    builder: str = "",
    client_name: str = "",
    responsible_pm: str = "Karl",
    stage: str = "Sales",
    install_type: str = "Install",
    install_date: Optional[date] = None,
    notes: str = "",
    its_id: Optional[str] = None,
    source: str = "manual",
    has_tfl: bool = False,
    has_stain: bool = False,
    has_paint: bool = False,
) -> dict:
    db = get_client()
    payload = {
        "job_name": job_name,
        "job_number": job_number,
        "builder": builder,
        "client_name": client_name,
        "responsible_pm": responsible_pm,
        "stage": stage,
        "install_type": install_type,
        "install_date": install_date.isoformat() if install_date else None,
        "notes": notes,
        "source": source,
        "has_tfl": has_tfl,
        "has_stain": has_stain,
        "has_paint": has_paint,
    }
    if its_id:
        payload["its_id"] = its_id

    result = db.table("jobs").insert(payload).execute()
    job = result.data[0]
    today = date.today()

    # Build task list: standard template + finish-type sample tasks
    template_tasks = get_template_tasks("Standard")
    extra_tasks = []
    if has_stain:
        extra_tasks += SAMPLE_TASKS["stain"]
    if has_paint:
        extra_tasks += SAMPLE_TASKS["paint"]
    if has_tfl:
        extra_tasks += SAMPLE_TASKS["tfl"]

    all_tasks = template_tasks + extra_tasks
    if all_tasks:
        task_rows = [
            {
                "job_id": job["id"],
                "title": t["title"],
                "task_type": t["task_type"],
                "assigned_to": t["assigned_to"],
                "status": "Open",
                "priority": "Normal",
                "due_date": _calc_due_date(t, today, install_date),
                "followup_days": t.get("followup_days"),
                "followup_created": False,
                "wo_number": "",
            }
            for t in all_tasks
        ]
        db.table("tasks").insert(task_rows).execute()

    return job


def update_job_stage(job_id: str, stage: str) -> None:
    db = get_client()
    db.table("jobs").update({"stage": stage}).eq("id", job_id).execute()


def update_job(job_id: str, **fields) -> None:
    db = get_client()
    for k, v in list(fields.items()):
        if isinstance(v, date):
            fields[k] = v.isoformat()
    db.table("jobs").update(fields).eq("id", job_id).execute()


def delete_job(job_id: str) -> None:
    db = get_client()
    db.table("jobs").delete().eq("id", job_id).execute()


def get_jobs_by_stage(stage: str) -> list[dict]:
    db = get_client()
    result = (
        db.table("jobs")
        .select("*")
        .eq("stage", stage)
        .order("created_at", desc=True)
        .execute()
    )
    return result.data or []


def get_install_jobs(start_date: Optional[date] = None, end_date: Optional[date] = None) -> list[dict]:
    db = get_client()
    query = db.table("jobs").select("*").not_.is_("install_date", "null")
    if start_date:
        query = query.gte("install_date", start_date.isoformat())
    if end_date:
        query = query.lte("install_date", end_date.isoformat())
    result = query.order("install_date").execute()
    return result.data or []
