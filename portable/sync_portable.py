"""Sync engine/utils from the main repo into portable/ (prevents stale copies).
Run from repo root:  python portable/sync_portable.py
Overwrites engine code; only the executions named in SYNC_EXECUTIONS are copied
into portable/core/executions (direct overwrite); never touches webdriver/ or CF config.
"""
import os, shutil, sys, subprocess

PORTABLE = os.path.dirname(os.path.realpath(__file__))
REPO = os.path.dirname(PORTABLE)

EXCLUDE_PROCESSORS = {
    'FILE_CHOOSERProcessor.py', 'MOUSE_CLICKProcessor.py',
    'MOUSE_POSITIONProcessor.py', 'MOUSE_SCROLLProcessor.py',
}

# Names may be given with or without the .yaml suffix.
SYNC_EXECUTIONS = [
    'T_Supplier_Registration',
    'T_Supplier_Creation_CPTDC',
]

# After portable is refreshed, also push the CODE parts of portable into each of
# these external target directories (per-file overwrite; files already present in
# the target that we don't ship are kept). Only code is copied — NOT webdriver/,
# download/, log/, config/, or CF config — so the target gets a runnable engine +
# processors + the SYNC_EXECUTIONS without the heavy binaries or runtime junk.
# A target directory that does not exist is reported and skipped (never created).
# Leave empty to skip external sync entirely.
SYNC_TARGET_DIRS = [
    '/Users/i335607/MyProject/ariba_ai_assistant/rpa',
]

# Portable subdirectories that count as "code" — pushed to each target.
TARGET_SYNC_DIRS = ['core', 'utils', 'mvp']
# Portable top-level files pushed to each target.
TARGET_SYNC_FILES = ['petp_run.py', 'requirements.txt']
# Never copy these into targets (heavy binaries / runtime products / caches).
TARGET_IGNORE = shutil.ignore_patterns('__pycache__', '*.pyc', '.DS_Store',
                                       'webdriver', 'download', 'log')


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


def _copy_executions():
    """Copy each allowlisted execution YAML from the main repo into portable
    (direct overwrite). Names in SYNC_EXECUTIONS may omit the .yaml suffix.
    A named execution missing from the main repo is reported, not silently skipped."""
    src_dir = os.path.join(REPO, 'core/executions')
    dst_dir = os.path.join(PORTABLE, 'core/executions')
    os.makedirs(dst_dir, exist_ok=True)
    copied, missing = 0, []
    for name in SYNC_EXECUTIONS:
        fname = name if name.endswith('.yaml') else name + '.yaml'
        src = os.path.join(src_dir, fname)
        if not os.path.isfile(src):
            missing.append(fname)
            continue
        shutil.copy2(src, os.path.join(dst_dir, fname))
        copied += 1
    print('sync: %d execution(s) copied.' % copied)
    if missing:
        print('sync: WARNING missing in main repo (not copied): ' + ', '.join(missing))


def _sync_to_targets():
    """Push the CODE parts of portable into each external target (per-file
    overwrite, keeping files the target has that we don't ship). Runs after
    portable itself is refreshed, so targets get the freshly-synced engine +
    processors + executions — minus webdriver/download/log/config."""
    if not SYNC_TARGET_DIRS:
        return
    for target in SYNC_TARGET_DIRS:
        if not os.path.isdir(target):
            print('sync: WARNING target dir missing (skipped): ' + target)
            continue
        for d in TARGET_SYNC_DIRS:
            src = os.path.join(PORTABLE, d)
            if os.path.isdir(src):
                shutil.copytree(src, os.path.join(target, d),
                                ignore=TARGET_IGNORE, dirs_exist_ok=True)
        for f in TARGET_SYNC_FILES:
            src = os.path.join(PORTABLE, f)
            if os.path.isfile(src):
                shutil.copy2(src, os.path.join(target, f))
        print('sync: pushed code to target -> ' + target)


def main():
    for rel in COPY_FILES:
        _copy_file(rel)
    for s, d in COPY_DIRS:
        _copy_dir(s, d)
    _copy_processors()
    _copy_executions()
    print('sync: engine/utils copied.')

    r = subprocess.run([sys.executable, '-c', 'import petp_run'],
                       cwd=PORTABLE, capture_output=True, text=True)
    if r.returncode != 0:
        print('SMOKE IMPORT FAILED:\n' + r.stderr)
        sys.exit(1)
    print('sync: import smoke check PASS.')

    _sync_to_targets()


if __name__ == '__main__':
    main()
