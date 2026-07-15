import logging
from typing import Optional

# Processor types that require OS-level GUI interaction (no headless alternative)
_PURE_GUI_TYPES = {
    "FILE_CHOOSER",
}

GUI_PROCESSOR_TYPES = set(_PURE_GUI_TYPES)

VALID_POLICIES = {"skip", "abort"}


def normalize_policy(policy: Optional[str], default: str = "skip") -> str:
    value = (policy or default or "skip").strip().lower()
    if value not in VALID_POLICIES:
        logging.warning(
            "Invalid nogui_ui_processor_policy=%s, fallback to %s",
            policy,
            default,
        )
        return default
    return value


def is_gui_processor(task_type: Optional[str]) -> bool:
    return (task_type or "").strip().upper() in GUI_PROCESSOR_TYPES


def decide(task_type: Optional[str], policy: str) -> str:
    if not is_gui_processor(task_type):
        return "allow"
    return normalize_policy(policy)


