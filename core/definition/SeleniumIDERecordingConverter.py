import json
import logging
import os.path
from typing import Optional, Callable

from core.task import Task

"""
Load Selenium IDE recording (.side) from file, then convert to PETP tasks.

Supported Selenium IDE commands → PETP task types:
    - open        → GO_TO_PAGE
    - click       → FIND_THEN_CLICK
    - type        → FIND_THEN_KEYIN
    - sendKeys    → FIND_THEN_KEYIN  (strips leading '$' from key constants)
    - doubleClick → FIND_THEN_COLLECT

Locator resolution order: xpath > id > css
"""

# Locator prefixes in order of preference
_LOCATOR_STRATEGIES = [
    ('xpath=', 'xpath'),
    ('id=', 'id'),
    ('css=', 'css'),
]


class SeleniumIDERecordingConverter:
    """Converts Selenium IDE .side recording files into PETP Task lists."""

    def __init__(self, file_path: str, test_name: str = ''):
        self.file_path = file_path
        self.test_name = test_name
        logging.info(
            f'SeleniumIDERecordingConverter will load tasks from recording: {self.test_name}, {self.file_path}')

    def set_test_name(self, test_name: str):
        self.test_name = test_name

    def get_test_names(self) -> list[str]:
        with open(self.file_path, 'r', encoding='utf-8') as f:
            return [t['name'] for t in json.load(f)['tests']]

    def is_initialized(self) -> bool:
        return self.file_path is not None and self.test_name is not None

    def convert_from_selenium_ide_recording(self) -> list[Task]:
        with open(self.file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        base_url = data['url']
        commands = self._find_commands_by_test_name(data, self.test_name)
        return [task for cmd in commands if (task := self._convert(cmd, base_url)) is not None]

    # ── command → Task dispatch ──────────────────────────────────────

    _COMMAND_MAP = {
        'open': '_handle_open',
        'click': '_handle_click',
        'type': '_handle_type',
        'sendKeys': '_handle_send_keys',
        'doubleClick': '_handle_double_click',
    }

    def _convert(self, command: dict, base_url: str) -> Optional[Task]:
        handler_name = self._COMMAND_MAP.get(command['command'])
        if handler_name is None:
            logging.debug(f"Unsupported Selenium IDE command: {command['command']}")
            return None
        return getattr(self, handler_name)(command, base_url)

    # ── individual command handlers ──────────────────────────────────

    def _handle_open(self, command: dict, base_url: str) -> Task:
        return Task('GO_TO_PAGE', json.dumps({'url': f"{base_url}{command['target']}"}))

    def _handle_click(self, command: dict, _base_url: str) -> Optional[Task]:
        return self._build_locator_task(command, 'FIND_THEN_CLICK', by_key='clickby')

    def _handle_type(self, command: dict, _base_url: str) -> Optional[Task]:
        return self._build_keyin_task(command)

    def _handle_send_keys(self, command: dict, _base_url: str) -> Optional[Task]:
        return self._build_keyin_task(command, value_fn=lambda v: v.replace('$', ''))

    def _handle_double_click(self, command: dict, _base_url: str) -> Optional[Task]:
        locator = self._find_proper_locator(command)
        if locator is None:
            return self._log_no_locator(command)
        by, identity = locator
        value_key = command.get('comment') or command['id']
        return Task('FIND_THEN_COLLECT', json.dumps({
            'collectby': by, 'identity': identity,
            'value_type': 'any', 'value_key': value_key,
        }))

    # ── shared builders ──────────────────────────────────────────────

    def _build_locator_task(self, command: dict, task_type: str, by_key: str) -> Optional[Task]:
        locator = self._find_proper_locator(command)
        if locator is None:
            return self._log_no_locator(command)
        by, identity = locator
        return Task(task_type, json.dumps({by_key: by, 'identity': identity}))

    def _build_keyin_task(self, command: dict,
                          value_fn: Callable[[str], str] = lambda v: v) -> Optional[Task]:
        locator = self._find_proper_locator(command)
        if locator is None:
            return self._log_no_locator(command)
        by, identity = locator
        return Task('FIND_THEN_KEYIN', json.dumps({
            'keyinby': by, 'identity': identity, 'value': value_fn(command['value']),
        }))

    # ── locator helpers ──────────────────────────────────────────────

    @staticmethod
    def _find_proper_locator(command: dict) -> Optional[tuple[str, str]]:
        """Return (strategy, value) for the first matching locator, or None."""
        for prefix, strategy in _LOCATOR_STRATEGIES:
            value = SeleniumIDERecordingConverter._find_first_by_prefix(prefix, command)
            if value is not None:
                return (strategy, value)
        return None

    @staticmethod
    def _find_first_by_prefix(prefix: str, command: dict) -> Optional[str]:
        target = command['target']
        if target.startswith(prefix):
            return target[len(prefix):]
        for ts in command.get('targets', []):
            if ts[0].startswith(prefix):
                return ts[0][len(prefix):]
        return None

    @staticmethod
    def _log_no_locator(command: dict) -> None:
        logging.info(json.dumps({'msg': 'cannot find proper locator: ' + str(command)}))
        return None

    # ── test lookup ──────────────────────────────────────────────────

    @staticmethod
    def _find_commands_by_test_name(data: dict, test_name: str) -> list[dict]:
        test = next((t for t in data['tests'] if t['name'] == test_name), None)
        if test is None:
            raise ValueError(f'Test "{test_name}" not found in recording')
        return test['commands']


if __name__ == '__main__':
    # customerserveroverview.side
    given = os.path.realpath('../../testcoverage/selenium/customerserveroverview.side')
    c = SeleniumIDERecordingConverter(given, 'Testcustomerserviewoverview')
    for t in c.convert_from_selenium_ide_recording():
        print(t)

    # GC-phoenix.side
    given = os.path.realpath('../../testcoverage/selenium/GC-phoenix.side')
    c = SeleniumIDERecordingConverter(given, 'gc-phoenix')
    for t in c.convert_from_selenium_ide_recording():
        print(t)
