STAGES = ["Sales", "Design", "Engineering", "Production", "Install", "Closeout"]

TASK_TYPES = [
    "Estimate",
    "Design",
    "Selections",
    "Approval",
    "Engineering",
    "Production",
    "Field",
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

# Task type order for display grouping (matches workflow order)
TASK_TYPE_ORDER = [
    "Estimate",
    "Design",
    "Selections",
    "Approval",
    "Engineering",
    "Production",
    "Field",
    "Install",
    "Financial",
    "Communication",
]
