from core.supabase_client import get_client

# Standard workflow template — applies to all jobs by default
# COQs and Change Orders are added manually per job as needed
SEED_TEMPLATES = [
    {"template_name": "Standard", "task_type": "Estimate",      "title": "Estimate",                    "assigned_to": "Karl",        "sort_order": 1},
    {"template_name": "Standard", "task_type": "Design",        "title": "Preliminary drawings",        "assigned_to": "Karl",        "sort_order": 2},
    {"template_name": "Standard", "task_type": "Selections",    "title": "Selections",                  "assigned_to": "Client",      "sort_order": 3},
    {"template_name": "Standard", "task_type": "Approval",      "title": "Client approval",             "assigned_to": "Client",      "sort_order": 4},
    {"template_name": "Standard", "task_type": "Design",        "title": "Final drawings / redlines",   "assigned_to": "Karl",        "sort_order": 5},
    {"template_name": "Standard", "task_type": "Engineering",   "title": "Shop drawings",               "assigned_to": "Engineering", "sort_order": 6},
    {"template_name": "Standard", "task_type": "Production",    "title": "Release to production",       "assigned_to": "Shop",        "sort_order": 7},
    {"template_name": "Standard", "task_type": "Production",    "title": "Hardware / material order",   "assigned_to": "Shop",        "sort_order": 8},
    {"template_name": "Standard", "task_type": "Field",         "title": "Site measure",                "assigned_to": "Karl",        "sort_order": 9},
    {"template_name": "Standard", "task_type": "Field",         "title": "Delivery / shipping",         "assigned_to": "Shop",        "sort_order": 10},
    {"template_name": "Standard", "task_type": "Install",       "title": "Schedule install",            "assigned_to": "Karl",        "sort_order": 11},
    {"template_name": "Standard", "task_type": "Install",       "title": "Install",                     "assigned_to": "Installer",   "sort_order": 12},
    {"template_name": "Standard", "task_type": "Install",       "title": "Punch list",                  "assigned_to": "Karl",        "sort_order": 13},
    {"template_name": "Standard", "task_type": "Field",         "title": "Final photos",                "assigned_to": "Karl",        "sort_order": 14},
    {"template_name": "Standard", "task_type": "Financial",     "title": "Job closeout",                "assigned_to": "Admin",       "sort_order": 15},
]


def seed_templates() -> int:
    """Insert default templates if table is empty. Returns count inserted."""
    db = get_client()
    existing = db.table("task_templates").select("id", count="exact").execute()
    if existing.count and existing.count > 0:
        return 0
    db.table("task_templates").insert(SEED_TEMPLATES).execute()
    return len(SEED_TEMPLATES)


def reseed_templates() -> int:
    """Force-wipe and reseed templates."""
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
