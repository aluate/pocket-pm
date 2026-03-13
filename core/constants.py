STAGES = ["Sales", "Design", "Engineering", "Production", "Install", "Closeout"]

TASK_TYPES = [
    "Field",
    "Design",
    "Engineering",
    "Procurement",
    "Install",
    "Financial",
    "Communication",
]

ROLES = [
    "Karl",
    "Engineering",
    "Shop",
    "Installer",
    "Builder",
    "Client",
    "Supplier",
    "Admin",
]

INSTALL_TYPES = ["Install", "Ship"]
TASK_STATUSES = ["Open", "In Progress", "Waiting", "Complete"]
TASK_PRIORITIES = ["Normal", "Urgent", "Critical"]
JOB_SOURCES = ["manual", "intake"]
INSTALL_STATUSES = ["Scheduled", "In Progress", "Complete"]

# Task aging thresholds (days)
AGING_YELLOW = 3
AGING_RED = 6

# Task type order for display grouping (matches typical workflow order)
TASK_TYPE_ORDER = [
    "Field",
    "Design",
    "Engineering",
    "Procurement",
    "Install",
    "Financial",
    "Communication",
]
