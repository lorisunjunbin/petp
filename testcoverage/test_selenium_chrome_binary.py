"""Verify chrome binary resolution: env > bundled > None.
Run: python testcoverage/test_selenium_chrome_binary.py  (exit 0 = pass)
NOTE: does not launch Chrome — only tests path resolution logic.
"""
import os, sys
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
from utils.SeleniumUtil import SeleniumUtil


def test_env_takes_priority():
    os.environ['PETP_CHROME_BINARY'] = '/tmp/my-chrome'
    try:
        assert SeleniumUtil._resolve_chrome_binary() == '/tmp/my-chrome'
    finally:
        del os.environ['PETP_CHROME_BINARY']


def test_none_when_nothing_available():
    os.environ.pop('PETP_CHROME_BINARY', None)
    # In a clean checkout there is no webdriver/<system>/chrome* bundled,
    # so resolution must return None (preserving legacy auto-detect).
    assert SeleniumUtil._resolve_chrome_binary() is None


def test_bundled_headless_shell_preferred(tmp_setup=None):
    """bundled chrome-headless-shell 应优先于 chrome 被解析(在 webdriver/<system>/ 下)。"""
    import tempfile, shutil
    from utils.OSUtils import OSUtils
    os.environ.pop('PETP_CHROME_BINARY', None)
    system = OSUtils.get_system()
    base = os.path.join(os.path.realpath('webdriver'), system)
    made_dir = not os.path.isdir(base)
    os.makedirs(base, exist_ok=True)
    hs = os.path.join(base, 'chrome-headless-shell')
    created = not os.path.isfile(hs)
    if created:
        with open(hs, 'w') as f:
            f.write('#!/bin/sh\n')  # placeholder, not executed
    try:
        resolved = SeleniumUtil._resolve_chrome_binary()
        assert resolved == hs, f'expected {hs}, got {resolved}'
    finally:
        if created:
            os.remove(hs)
        if made_dir:
            # only remove dirs we created, and only if now empty
            try:
                os.removedirs(base)
            except OSError:
                pass


def test_headless_shell_name_detection_contract():
    """守护 --headless=new 跳过逻辑所依赖的命名契约。"""
    assert 'headless-shell' in os.path.basename('/x/y/chrome-headless-shell')
    assert 'headless-shell' in os.path.basename('chrome-headless-shell')
    assert 'headless-shell' not in os.path.basename('/x/y/chrome')
    assert 'headless-shell' not in os.path.basename('chrome')


if __name__ == '__main__':
    fails = 0
    for name, fn in list(globals().items()):
        if name.startswith('test_') and callable(fn):
            try:
                fn(); print(f'PASS {name}')
            except Exception as e:
                fails += 1; print(f'FAIL {name}: {e}')
    sys.exit(1 if fails else 0)
