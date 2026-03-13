from core.supabase_client import get_client

# Seed data for task templates
SEED_TEMPLATES = [
    # Kitchen
    {"template_name": "Kitchen", "task_type": "Field", "title": "Site measure", "assigned_to": "Karl", "sort_order": 1},
    {"template_name": "Kitchen", "task_type": "Design", "title": "Preliminary layout", "assigned_to": "Karl", "sort_order": 2},
    {"template_name": "Kitchen", "task_type": "Design", "title": "Design meeting", "assigned_to": "Karl", "sort_order": 3},
    {"template_name": "Kitchen", "task_type": "Design", "title": "Redlines", "assigned_to": "Karl", "sort_order": 4},
    {"template_name": "Kitchen", "task_type": "Engineering", "title": "Shop drawings", "assigned_to": "Engineering", "sort_order": 5},
    {"template_name": "Kitchen", "task_type": "Procurement", "title": "Hardware spec", "assigned_to": "Karl", "sort_order": 6},
    {"template_name": "Kitchen", "task_type": "Procurement", "title": "Confirm appliance specs", "assigned_to": "Client", "sort_order": 7},
    {"template_name": "Kitchen", "task_type": "Procurement", "title": "Order materials", "assigned_to": "Shop", "sort_order": 8},
    {"template_name": "Kitchen", "task_type": "Install", "title": "Schedule install", "assigned_to": "Shop", "sort_order": 9},
    {"template_name": "Kitchen", "task_type": "Install", "title": "Install cabinets", "assigned_to": "Installer", "sort_order": 10},
    {"template_name": "Kitchen", "task_type": "Install", "title": "Punch list", "assigned_to": "Karl", "sort_order": 11},
    {"template_name": "Kitchen", "task_type": "Field", "title": "Final photos", "assigned_to": "Karl", "sort_order": 12},
    {"template_name": "Kitchen", "task_type": "Financial", "title": "Job closeout", "assigned_to": "Admin", "sort_order": 13},

    # Bathroom
    {"template_name": "Bathroom", "task_type": "Field", "title": "Site measure", "assigned_to": "Karl", "sort_order": 1},
    {"template_name": "Bathroom", "task_type": "Design", "title": "Preliminary layout", "assigned_to": "Karl", "sort_order": 2},
    {"template_name": "Bathroom", "task_type": "Design", "title": "Design meeting", "assigned_to": "Karl", "sort_order": 3},
    {"template_name": "Bathroom", "task_type": "Design", "title": "Redlines", "assigned_to": "Karl", "sort_order": 4},
    {"template_name": "Bathroom", "task_type": "Engineering", "title": "Shop drawings", "assigned_to": "Engineering", "sort_order": 5},
    {"template_name": "Bathroom", "task_type": "Procurement", "title": "Hardware spec", "assigned_to": "Karl", "sort_order": 6},
    {"template_name": "Bathroom", "task_type": "Procurement", "title": "Order materials", "assigned_to": "Shop", "sort_order": 7},
    {"template_name": "Bathroom", "task_type": "Install", "title": "Schedule install", "assigned_to": "Shop", "sort_order": 8},
    {"template_name": "Bathroom", "task_type": "Install", "title": "Install cabinets", "assigned_to": "Installer", "sort_order": 9},
    {"template_name": "Bathroom", "task_type": "Install", "title": "Punch list", "assigned_to": "Karl", "sort_order": 10},
    {"template_name": "Bathroom", "task_type": "Financial", "title": "Job closeout", "assigned_to": "Admin", "sort_order": 11},

    # Closet / Built-ins
    {"template_name": "Closet/Built-ins", "task_type": "Field", "title": "Site measure", "assigned_to": "Karl", "sort_order": 1},
    {"template_name": "Closet/Built-ins", "task_type": "Design", "title": "Preliminary layout", "assigned_to": "Karl", "sort_order": 2},
    {"template_name": "Closet/Built-ins", "task_type": "Design", "title": "Redlines", "assigned_to": "Karl", "sort_order": 3},
    {"template_name": "Closet/Built-ins", "task_type": "Engineering", "title": "Shop drawings", "assigned_to": "Engineering", "sort_order": 4},
    {"template_name": "Closet/Built-ins", "task_type": "Procurement", "title": "Order materials", "assigned_to": "Shop", "sort_order": 5},
    {"template_name": "Closet/Built-ins", "task_type": "Install", "title": "Schedule install", "assigned_to": "Shop", "sort_order": 6},
    {"template_name": "Closet/Built-ins", "task_type": "Install", "title": "Install", "assigned_to": "Installer", "sort_order": 7},
    {"template_name": "Closet/Built-ins", "task_type": "Install", "title": "Punch list", "assigned_to": "Karl", "sort_order": 8},
    {"template_name": "Closet/Built-ins", "task_type": "Financial", "title": "Job closeout", "assigned_to": "Admin", "sort_order": 9},
]


def seed_templates() -> int:
    """Insert default templates if table is empty. Returns count inserted."""
    db = get_client()
    existing = db.table("task_templates").select("id", count="exact").execute()
    if existing.count and existing.count > 0:
        return 0
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
