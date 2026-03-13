from datetime import datetime, timezone
from typing import Optional
from core.supabase_client import get_client
from core.constants import AGING_YELLOW, AGING_RED


def get_task_age_days(task: dict) -> int:
    created_str = task.get("created_at", "")
    if not created_str:
        return 0
    try:
        created = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
        return (datetime.now(timezone.utc) - created).days
    except Exception:
        return 0


def get_age_indicator(task: dict) -> str:
    """Return emoji color indicator based on task age and priority."""
    # Critical priority always red regardless of age
    if task.get("priority") == "Critical":
        return "🔴"
    if task.get("priority") == "Urgent":
        age = get_task_age_days(task)
        return "🔴" if age >= AGING_YELLOW else "🟡"
    age = get_task_age_days(task)
    if age >= AGING_RED:
        return "🔴"
    elif age >= AGING_YELLOW:
        return "🟡"
    return ""


def get_all_tasks(include_complete: bool = False) -> list[dict]:
    db = get_client()
    query = db.table("tasks").select("*, jobs(job_name)").order("created_at")
    if not include_complete:
        query = query.neq("status", "Complete")
    result = query.execute()
    return result.data or []


def get_tasks_for_job(job_id: str, include_complete: bool = True) -> list[dict]:
    db = get_client()
    query = db.table("tasks").select("*").eq("job_id", job_id).order("created_at")
    if not include_complete:
        query = query.neq("status", "Complete")
    result = query.execute()
    return result.data or []


def get_my_tasks(assigned_to: str = "Karl", include_complete: bool = False) -> list[dict]:
    db = get_client()
    query = (
        db.table("tasks")
        .select("*, jobs(job_name)")
        .eq("assigned_to", assigned_to)
        .order("created_at")
    )
    if not include_complete:
        query = query.neq("status", "Complete")
    result = query.execute()
    return result.data or []


def get_waiting_tasks() -> list[dict]:
    db = get_client()
    result = (
        db.table("tasks")
        .select("*, jobs(job_name)")
        .not_.is_("waiting_on", "null")
        .neq("status", "Complete")
        .order("created_at")
        .execute()
    )
    return result.data or []


def get_team_tasks(include_complete: bool = False) -> list[dict]:
    """All tasks not assigned to Karl (team/delegation tasks)."""
    db = get_client()
    query = (
        db.table("tasks")
        .select("*, jobs(job_name)")
        .neq("assigned_to", "Karl")
        .order("assigned_to")
    )
    if not include_complete:
        query = query.neq("status", "Complete")
    result = query.execute()
    return result.data or []


def create_task(
    job_id: str,
    title: str,
    task_type: str = "Field",
    assigned_to: str = "Karl",
    waiting_on: Optional[str] = None,
    status: str = "Open",
    priority: str = "Normal",
) -> dict:
    db = get_client()
    payload = {
        "job_id": job_id,
        "title": title,
        "task_type": task_type,
        "assigned_to": assigned_to,
        "waiting_on": waiting_on,
        "status": status,
        "priority": priority,
    }
    result = db.table("tasks").insert(payload).execute()
    return result.data[0]


def complete_task(task_id: str) -> None:
    db = get_client()
    db.table("tasks").update(
        {
            "status": "Complete",
            "completed_at": datetime.now(timezone.utc).isoformat(),
        }
    ).eq("id", task_id).execute()


def update_task(task_id: str, **fields) -> None:
    db = get_client()
    db.table("tasks").update(fields).eq("id", task_id).execute()


def delete_task(task_id: str) -> None:
    db = get_client()
    db.table("tasks").delete().eq("id", task_id).execute()


def get_open_task_count(job_id: str) -> int:
    db = get_client()
    result = (
        db.table("tasks")
        .select("id", count="exact")
        .eq("job_id", job_id)
        .neq("status", "Complete")
        .execute()
    )
    return result.count or 0


def has_red_tasks(job_id: str) -> bool:
    tasks = get_tasks_for_job(job_id, include_complete=False)
    for t in tasks:
        if get_age_indicator(t) == "🔴":
            return True
    return False
