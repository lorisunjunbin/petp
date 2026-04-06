import logging
import shutil
from typing import Optional

# Processor types that always require a display (no headless alternative)
_PURE_GUI_TYPES = {
    "SHOW_RESULT",
    "INPUT_DIALOG",
    "MATPLOTLIB",
    "FILE_CHOOSER",
}

# Processor types that need Chrome + chromedriver (can run headless in Docker)
_SELENIUM_TYPES = {
    "GO_TO_PAGE",
    "CLOSE_CHROME",
    "ENTER_FULLSCREEN",
    "FIND_THEN_CLICK",
    "FIND_THEN_COLLECT",
    "FIND_THEN_KEYIN",
    "FIND_MULTI_THEN_CLICK",
    "FIND_MULTI_THEN_COLLECT",
    "GET_COOKIE",
    "GO_BACK",
    "MOVE_TO_IFRAME",
    "SCREENSHOT",
}

# Processor types that need a display + pyautogui (no headless alternative)
_MOUSE_TYPES = {
    "MOUSE_CLICK",
    "MOUSE_POSITION",
    "MOUSE_SCROLL",
}


def _chrome_available() -> bool:
    """Check if chromium/chrome and chromedriver are installed on the system."""
    return (
        shutil.which('chromedriver') is not None
        and (shutil.which('chromium') is not None
             or shutil.which('chromium-browser') is not None
             or shutil.which('google-chrome') is not None
             or shutil.which('google-chrome-stable') is not None)
    )


_CHROME_OK = _chrome_available()

# Build the effective skip set at import time
GUI_PROCESSOR_TYPES = set(_PURE_GUI_TYPES | _MOUSE_TYPES)
if not _CHROME_OK:
    GUI_PROCESSOR_TYPES |= _SELENIUM_TYPES
    logging.info("Chrome/chromedriver NOT found — Selenium processors will be skipped in no-GUI mode")
else:
    logging.info("Chrome/chromedriver found — Selenium processors will run in headless mode")

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


