from core.supabase_client import get_client

# Standard workflow template
# due_days_from_created: due N business days after job creation
# due_days_from_install: due N days before install date (negative = before)
# followup_days: auto-create a follow-up task if still open after N days
SEED_TEMPLATES = [
    {"template_name": "Standard", "task_type": "Estimate",    "title": "Estimate",                   "assigned_to": "Karl",        "sort_order": 1,  "due_days_from_created": 2,  "due_days_from_install": None, "followup_days": None},
    {"template_name": "Standard", "task_type": "Design",      "title": "Preliminary drawings",       "assigned_to": "Karl",        "sort_order": 2,  "due_days_from_created": None, "due_days_from_install": None, "followup_days": None},
    {"template_name": "Standard", "task_type": "Selections",  "title": "Selections",                 "assigned_to": "Client",      "sort_order": 3,  "due_days_from_created": None, "due_days_from_install": None, "followup_days": 7},
    {"template_name": "Standard", "task_type": "Approval",    "title": "Client approval",            "assigned_to": "Client",      "sort_order": 4,  "due_days_from_created": None, "due_days_from_install": None, "followup_days": 5},
    {"template_name": "Standard", "task_type": "Design",      "title": "Final drawings / redlines",  "assigned_to": "Karl",        "sort_order": 5,  "due_days_from_created": None, "due_days_from_install": None, "followup_days": None},
    {"template_name": "Standard", "task_type": "Engineering", "title": "Shop drawings",              "assigned_to": "Engineering", "sort_order": 6,  "due_days_from_created": None, "due_days_from_install": None, "followup_days": 28},
    {"template_name": "Standard", "task_type": "Production",  "title": "Release to production",      "assigned_to": "Shop",        "sort_order": 7,  "due_days_from_created": None, "due_days_from_install": None, "followup_days": None},
    {"template_name": "Standard", "task_type": "Production",  "title": "Hardware / material order",  "assigned_to": "Shop",        "sort_order": 8,  "due_days_from_created": None, "due_days_from_install": None, "followup_days": None},
    {"template_name": "Standard", "task_type": "Field",       "title": "Site measure",               "assigned_to": "Karl",        "sort_order": 9,  "due_days_from_created": None, "due_days_from_install": -56,  "followup_days": None},
    {"template_name": "Standard", "task_type": "Field",       "title": "Delivery / shipping",        "assigned_to": "Shop",        "sort_order": 10, "due_days_from_created": None, "due_days_from_install": None, "followup_days": None},
    {"template_name": "Standard", "task_type": "Install",     "title": "Schedule install",           "assigned_to": "Karl",        "sort_order": 11, "due_days_from_created": None, "due_days_from_install": -21,  "followup_days": None},
    {"template_name": "Standard", "task_type": "Install",     "title": "Install",                    "assigned_to": "Installer",   "sort_order": 12, "due_days_from_created": None, "due_days_from_install": 0,    "followup_days": None},
    {"template_name": "Standard", "task_type": "Install",     "title": "Walk install / punch list",  "assigned_to": "Karl",        "sort_order": 13, "due_days_from_created": None, "due_days_from_install": 1,    "followup_days": None},
    {"template_name": "Standard", "task_type": "Field",       "title": "Final photos",               "assigned_to": "Karl",        "sort_order": 14, "due_days_from_created": None, "due_days_from_install": None, "followup_days": None},
    {"template_name": "Standard", "task_type": "Financial",   "title": "Job closeout",               "assigned_to": "Admin",       "sort_order": 15, "due_days_from_created": None, "due_days_from_install": None, "followup_days": None},
]

# Sample tasks added based on finish type — inserted after Preliminary drawings
SAMPLE_TASKS = {
    "stain": [
        {"task_type": "Production", "title": "Make stain samples",    "assigned_to": "Shop",   "sort_order": 25},
        {"task_type": "Approval",   "title": "Approve stain samples", "assigned_to": "Client", "sort_order": 26, "followup_days": 5},
    ],
    "paint": [
        {"task_type": "Production", "title": "Make paint samples",    "assigned_to": "Shop",   "sort_order": 27},
        {"task_type": "Approval",   "title": "Approve paint samples", "assigned_to": "Client", "sort_order": 28, "followup_days": 5},
    ],
    "tfl": [
        {"task_type": "Procurement", "title": "Order TFL samples",         "assigned_to": "Shop",     "sort_order": 29},
        {"task_type": "Procurement", "title": "Verify TFL lead times",     "assigned_to": "Supplier", "sort_order": 30, "followup_days": 3},
    ],
}


def seed_templates() -> int:
    db = get_client()
    existing = db.table("task_templates").select("id", count="exact").execute()
    if existing.count and existing.count > 0:
        return 0
    db.table("task_templates").insert(SEED_TEMPLATES).execute()
    return len(SEED_TEMPLATES)


def reseed_templates() -> int:
    db = get_client()
    db.table("task_templates").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
    db.table("task_templates").insert(SEED_TEMPLATES).execute()
    return len(SEED_TEMPLATES)


def get_template_names() -> list[str]:
    db = get_client()
    result = db.table("task_templates").select("template_name").execute()
    names = sorted(set(row["template_name"] for row in (result.data or [])))
    return names


def get_template_tasks(template_name: str) -> list[dict]:
    db = get_client()
    result = (
        db.table("task_templates")
        .select("*")
        .eq("template_name", template_name)
        .order("sort_order")
        .execute()
    )
    return result.data or []
