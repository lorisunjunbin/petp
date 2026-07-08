import json
import logging
import re
from typing import Optional

from core.task import Task

"""
Load Chrome DevTools Recorder JSON export, then convert to PETP tasks.

Step type mapping:
    - navigate       → GO_TO_PAGE
    - click          → FIND_THEN_CLICK
    - doubleClick    → FIND_THEN_COLLECT
    - change         → FIND_THEN_KEYIN
    - keyDown+keyUp  → FIND_THEN_KEYIN  (merged pair, key name → KEY_* constant)
    - waitForElement → WAIT_FOR

Selector resolution order: xpath > id (from #id CSS) > css
"""

_KEY_MAP = {
    'Enter': 'KEY_ENTER',
    'Tab': 'KEY_TAB',
    'Escape': 'KEY_ESCAPE',
    'Backspace': 'KEY_BACKSPACE',
    'Delete': 'KEY_DELETE',
    'ArrowLeft': 'KEY_LEFT',
    'ArrowRight': 'KEY_RIGHT',
    'ArrowUp': 'KEY_UP',
    'ArrowDown': 'KEY_DOWN',
    'Home': 'KEY_HOME',
    'End': 'KEY_END',
    'PageUp': 'KEY_PAGE_UP',
    'PageDown': 'KEY_PAGE_DOWN',
    'Insert': 'KEY_INSERT',
    'Space': 'KEY_SPACE',
    ' ': 'KEY_SPACE',
    'Shift': 'KEY_SHIFT',
    'Control': 'KEY_CONTROL',
    'Alt': 'KEY_ALT',
    'Meta': 'KEY_META',
    'F1': 'KEY_F1', 'F2': 'KEY_F2', 'F3': 'KEY_F3', 'F4': 'KEY_F4',
    'F5': 'KEY_F5', 'F6': 'KEY_F6', 'F7': 'KEY_F7', 'F8': 'KEY_F8',
    'F9': 'KEY_F9', 'F10': 'KEY_F10', 'F11': 'KEY_F11', 'F12': 'KEY_F12',
}

_CSS_ID_PATTERN = re.compile(r'^#([\w-]+)$')


class ChromeRecorderConverter:
    """Converts Chrome DevTools Recorder JSON exports into PETP Task lists."""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self._data = None
        logging.info('ChromeRecorderConverter will load from: %s', self.file_path)

    def is_initialized(self) -> bool:
        return self.file_path is not None

    def get_title(self) -> str:
        return self._load().get('title', '')

    def convert(self) -> list[Task]:
        data = self._load()
        steps = data.get('steps', [])
        tasks = []
        i = 0
        while i < len(steps):
            step = steps[i]
            step_type = step.get('type', '')

            if step_type == 'keyDown':
                task = self._handle_key_down(step)
                if task:
                    tasks.append(task)
                if i + 1 < len(steps) and steps[i + 1].get('type') == 'keyUp':
                    i += 1
            else:
                handler = self._STEP_MAP.get(step_type)
                if handler:
                    task = handler(self, step)
                    if task:
                        tasks.append(task)
                else:
                    logging.debug('Unsupported Chrome Recorder step type: %s', step_type)
            i += 1
        return tasks

    # ── step handlers ───────────────────────────────────────────────

    def _handle_navigate(self, step: dict) -> Task:
        return Task('GO_TO_PAGE', json.dumps({'url': step['url']}))

    def _handle_click(self, step: dict) -> Optional[Task]:
        locator = self._resolve_selector(step.get('selectors', []))
        if locator is None:
            return self._log_no_selector(step)
        by, identity = locator
        return Task('FIND_THEN_CLICK', json.dumps({'find_by': by, 'identity': identity}))

    def _handle_double_click(self, step: dict) -> Optional[Task]:
        locator = self._resolve_selector(step.get('selectors', []))
        if locator is None:
            return self._log_no_selector(step)
        by, identity = locator
        return Task('FIND_THEN_COLLECT', json.dumps({
            'find_by': by, 'identity': identity,
            'value_type': 'text', 'value_key': f'dblclick_{self._selector_key(identity)}',
        }))

    def _handle_change(self, step: dict) -> Optional[Task]:
        locator = self._resolve_selector(step.get('selectors', []))
        if locator is None:
            return self._log_no_selector(step)
        by, identity = locator
        return Task('FIND_THEN_KEYIN', json.dumps({
            'find_by': by, 'identity': identity, 'value': step.get('value', ''),
        }))

    def _handle_key_down(self, step: dict) -> Optional[Task]:
        key = step.get('key', '')
        petp_key = _KEY_MAP.get(key)
        if petp_key is None:
            if len(key) == 1:
                petp_key = key
            else:
                logging.debug('Unmapped key: %s', key)
                return None
        return Task('FIND_THEN_KEYIN', json.dumps({
            'find_by': 'xpath', 'identity': '//body', 'value': petp_key,
        }))

    def _handle_wait_for_element(self, step: dict) -> Optional[Task]:
        locator = self._resolve_selector(step.get('selectors', []))
        if locator is None:
            return self._log_no_selector(step)
        by, identity = locator
        timeout_ms = step.get('timeout', 5000)
        return Task('WAIT_FOR', json.dumps({
            'waitfor': by, 'identity': identity, 'timeout': max(1, timeout_ms // 1000),
        }))

    _STEP_MAP = {
        'navigate': _handle_navigate,
        'click': _handle_click,
        'doubleClick': _handle_double_click,
        'change': _handle_change,
        'waitForElement': _handle_wait_for_element,
    }

    # ── selector resolution ─────────────────────────────────────────

    @staticmethod
    def _resolve_selector(selectors: list) -> Optional[tuple[str, str]]:
        xpath_hit = None
        css_hit = None

        for group in selectors:
            for sel in group:
                if not isinstance(sel, str):
                    continue
                if sel.startswith('xpath/'):
                    if xpath_hit is None:
                        xpath_hit = sel[len('xpath/'):]
                elif sel.startswith('aria/') or sel.startswith('pierce/') or sel.startswith('text/'):
                    continue
                else:
                    if css_hit is None:
                        css_hit = sel

        if xpath_hit:
            return ('xpath', xpath_hit)

        if css_hit:
            m = _CSS_ID_PATTERN.match(css_hit)
            if m:
                return ('id', m.group(1))
            return ('css', css_hit)

        return None

    # ── helpers ──────────────────────────────────────────────────────

    @staticmethod
    def _selector_key(identity: str) -> str:
        return re.sub(r'[^a-zA-Z0-9]', '_', identity)[:30].strip('_') or 'element'

    def _load(self) -> dict:
        if self._data is None:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self._data = json.load(f)
        return self._data

    @staticmethod
    def _log_no_selector(step: dict) -> None:
        logging.info('Cannot resolve selector for step: %s', json.dumps(step, ensure_ascii=False))
        return None
