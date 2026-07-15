"""Sync engine/utils from the main repo into portable/ (prevents stale copies).
Run from repo root:  python portable/sync_portable.py
Overwrites engine code; never touches portable/core/executions, webdriver/, or CF config.
"""
import os, shutil, sys, subprocess

PORTABLE = os.path.dirname(os.path.realpath(__file__))
REPO = os.path.dirname(PORTABLE)

EXCLUDE_PROCESSORS = {
    'FILE_CHOOSERProcessor.py', 'MOUSE_CLICKProcessor.py',
    'MOUSE_POSITIONProcessor.py', 'MOUSE_SCROLLProcessor.py',
}

# (src_rel, dst_rel) directories copied wholesale
COPY_DIRS = [
    ('core/definition', 'core/definition'),
    ('core/runtime', 'core/runtime'),
    ('core/cron', 'core/cron'),
    ('utils', 'utils'),
]
# individual engine files (copied verbatim from main repo).
# NOTE: PETP uses implicit namespace packages (PEP 420) — the repo ships almost
# no __init__.py. portable/ relies on the same mechanism (petp_run.py puts
# portable/ on sys.path), so we neither copy nor create __init__.py files.
# MAINTENANCE: this list is hand-maintained. When the engine gains a new
# dependency file, add it here. The smoke check below only catches import-time
# (module top-level) breakage, not lazy/runtime imports inside untested processors.
COPY_FILES = [
    'core/processor.py', 'core/execution.py', 'core/task.py',
    'core/executionstate.py', 'core/loop.py', 'core/pipeline.py', 'core/constants.py',
    'mvp/presenter/event/PETPEvent.py',
]


def _copy_file(rel):
    src = os.path.join(REPO, rel)
    dst = os.path.join(PORTABLE, rel)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)


def _copy_dir(src_rel, dst_rel):
    src = os.path.join(REPO, src_rel)
    dst = os.path.join(PORTABLE, dst_rel)
    if os.path.isdir(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns('__pycache__'))


def _copy_processors():
    src = os.path.join(REPO, 'core/processors')
    dst = os.path.join(PORTABLE, 'core/processors')
    if os.path.isdir(dst):
        shutil.rmtree(dst)
    def ignore(dirpath, names):
        return {n for n in names if n in EXCLUDE_PROCESSORS or n == '__pycache__'}
    shutil.copytree(src, dst, ignore=ignore)


def main():
    for rel in COPY_FILES:
        _copy_file(rel)
    for s, d in COPY_DIRS:
        _copy_dir(s, d)
    _copy_processors()
    print('sync: engine/utils copied.')

    r = subprocess.run([sys.executable, '-c', 'import petp_run'],
                       cwd=PORTABLE, capture_output=True, text=True)
    if r.returncode != 0:
        print('SMOKE IMPORT FAILED:\n' + r.stderr)
        sys.exit(1)
    print('sync: import smoke check PASS.')


if __name__ == '__main__':
    main()
