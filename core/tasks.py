from datetime import datetime, date, timezone
from typing import Optional
from core.supabase_client import get_client
from core.constants import AGING_YELLOW, AGING_RED


def get_task_age_days(task: dict) -> int:
    # Use activated_at if set (sequential tasks age from activation); fall back to created_at
    ts_str = task.get("activated_at") or task.get("created_at", "")
    if not ts_str:
        return 0
    try:
        ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
        return (datetime.now(timezone.utc) - ts).days
    except Exception:
        return 0


def get_due_days(task: dict) -> Optional[int]:
    """Days until due (negative = overdue). None if no due date."""
    due_str = task.get("due_date")
    if not due_str:
        return None
    try:
        due = date.fromisoformat(due_str)
        return (due - date.today()).days
    except Exception:
        return None


def get_age_indicator(task: dict) -> str:
    """
    🔴 overdue due date, Critical priority, or Urgent+old
    🟡 aging, Urgent priority
    🔵 waiting on someone else (not Karl's problem)
    """
    # Waiting on someone → blue (informational, not urgent to Karl)
    if task.get("waiting_on") or task.get("status") == "Waiting":
        return "🔵"

    # Critical always red
    if task.get("priority") == "Critical":
        return "🔴"

    # Overdue due date → red regardless of age
    due_days = get_due_days(task)
    if due_days is not None and due_days < 0:
        return "🔴"

    # Urgent priority
    if task.get("priority") == "Urgent":
        age = get_task_age_days(task)
        return "🔴" if age >= AGING_YELLOW else "🟡"

    # Normal aging
    age = get_task_age_days(task)
    if age >= AGING_RED:
        return "🔴"
    elif age >= AGING_YELLOW:
        return "🟡"
    return ""


def task_score(task: dict) -> int:
    """
    Higher score = should be done sooner.
    Used to rank Karl's task queue on the home screen.
    """
    score = 0
    priority = task.get("priority", "Normal")
    age = get_task_age_days(task)
    due_days = get_due_days(task)
    title = task.get("title", "")

    # Priority
    if priority == "Critical":
        score += 100
    elif priority == "Urgent":
        score += 40

    # Age (3 pts/day, capped at 60 so ancient tasks don't bury everything else)
    score += min(age * 3, 60)

    # Due date
    if due_days is not None:
        if due_days < 0:                      # overdue: 15 pts/day, capped at 90
            score += min(abs(due_days) * 15, 90)
        elif due_days == 0:                   # due today
            score += 35
        elif due_days <= 2:                   # due very soon
            score += 20
        elif due_days <= 5:
            score += 10

    # Auto-generated follow-ups are already past a threshold — treat as urgent
    if title.lower().startswith("follow up"):
        score += 35

    return score


def get_due_label(task: dict) -> str:
    """Human-readable due date label."""
    due_days = get_due_days(task)
    if due_days is None:
        return ""
    if due_days < 0:
        return f"⚠️ {abs(due_days)}d overdue"
    if due_days == 0:
        return "due today"
    if due_days <= 3:
        return f"due in {due_days}d"
    due_str = task.get("due_date", "")
    return f"due {due_str}"


def check_and_create_followups(job_id: str) -> int:
    """
    Check tasks with followup_days set. If still open and age >= followup_days
    and no follow-up created yet, auto-create a follow-up task for Karl.
    Returns count of follow-ups created.
    """
    db = get_client()
    tasks = (
        db.table("tasks")
        .select("*")
        .eq("job_id", job_id)
        .not_.is_("followup_days", "null")
        .eq("followup_created", False)
        .neq("status", "Complete")
        .execute()
    ).data or []

    created = 0
    for task in tasks:
        age = get_task_age_days(task)
        if age >= task["followup_days"]:
            # Create follow-up task
            db.table("tasks").insert({
                "job_id": job_id,
                "title": f"Follow up: {task['title']}",
                "task_type": "Communication",
                "assigned_to": "Karl",
                "status": "Open",
                "priority": "Urgent",
                "wo_number": task.get("wo_number", ""),
            }).execute()
            # Mark original so we don't duplicate
            db.table("tasks").update({"followup_created": True}).eq("id", task["id"]).execute()
            created += 1
    return created


def get_all_tasks(include_complete: bool = False) -> list[dict]:
    db = get_client()
    query = db.table("tasks").select("*, jobs(job_name)").order("created_at")
    if not include_complete:
        query = query.neq("status", "Complete")
    result = query.execute()
    return result.data or []


def get_tasks_for_job(job_id: str, include_complete: bool = True, include_pending: bool = True) -> list[dict]:
    db = get_client()
    query = db.table("tasks").select("*").eq("job_id", job_id).order("seq_order").order("created_at")
    if not include_complete:
        query = query.neq("status", "Complete")
    if not include_pending:
        query = query.neq("status", "Pending")
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
    query = query.neq("status", "Pending")
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
    db = get_client()
    query = (
        db.table("tasks")
        .select("*, jobs(job_name)")
        .neq("assigned_to", "Karl")
        .neq("status", "Pending")
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
    wo_number: str = "",
    due_date: Optional[date] = None,
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
        "wo_number": wo_number,
        "due_date": due_date.isoformat() if due_date else None,
    }
    result = db.table("tasks").insert(payload).execute()
    return result.data[0]


def activate_next_task(job_id: str) -> Optional[str]:
    """Activate the next Pending task for a job (lowest seq_order). Returns activated task id or None."""
    db = get_client()
    result = (
        db.table("tasks")
        .select("id, seq_order")
        .eq("job_id", job_id)
        .eq("status", "Pending")
        .order("seq_order")
        .limit(1)
        .execute()
    )
    rows = result.data or []
    if not rows:
        return None
    next_id = rows[0]["id"]
    db.table("tasks").update({
        "status": "Open",
        "activated_at": datetime.now(timezone.utc).isoformat(),
    }).eq("id", next_id).execute()
    return next_id


def activate_task(task_id: str) -> None:
    """Manually activate a specific Pending task."""
    db = get_client()
    db.table("tasks").update({
        "status": "Open",
        "activated_at": datetime.now(timezone.utc).isoformat(),
    }).eq("id", task_id).execute()


def complete_task(task_id: str, job_id: Optional[str] = None) -> None:
    db = get_client()
    db.table("tasks").update(
        {
            "status": "Complete",
            "completed_at": datetime.now(timezone.utc).isoformat(),
        }
    ).eq("id", task_id).execute()
    if job_id:
        activate_next_task(job_id)


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
        ind = get_age_indicator(t)
        if ind == "🔴":
            return True
    return False
