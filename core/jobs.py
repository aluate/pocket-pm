from datetime import date
from typing import Optional
from core.supabase_client import get_client
from core.templates import get_template_tasks
from core.constants import STAGES


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
    }
    if its_id:
        payload["its_id"] = its_id

    result = db.table("jobs").insert(payload).execute()
    job = result.data[0]

    # Always auto-generate tasks from Standard template
    template_tasks = get_template_tasks("Standard")
    if template_tasks:
        task_rows = [
            {
                "job_id": job["id"],
                "title": t["title"],
                "task_type": t["task_type"],
                "assigned_to": t["assigned_to"],
                "status": "Open",
                "priority": "Normal",
            }
            for t in template_tasks
        ]
        db.table("tasks").insert(task_rows).execute()

    return job


def update_job_stage(job_id: str, stage: str) -> None:
    db = get_client()
    db.table("jobs").update({"stage": stage}).eq("id", job_id).execute()


def update_job(job_id: str, **fields) -> None:
    db = get_client()
    # Convert date objects to ISO strings
    for k, v in fields.items():
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
    """Get jobs with install dates, optionally filtered by date range."""
    db = get_client()
    query = db.table("jobs").select("*").not_.is_("install_date", "null")
    if start_date:
        query = query.gte("install_date", start_date.isoformat())
    if end_date:
        query = query.lte("install_date", end_date.isoformat())
    result = query.order("install_date").execute()
    return result.data or []
