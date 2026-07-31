"""Sync engine code + executions from the main repo into portable/, then optionally
into external targets. Run from repo root:  python portable/sync_portable.py
Executions follow an allowlist: SYNC_EXECUTIONS for portable/ (mirror — prunes extras),
per-target lists for SYNC_TARGETS (upsert — never deletes the target's own files).
Never touches webdriver/ or CF config.
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
    'T_Supplier_Registration_huihui',
    'T_Supplier_Creation_huihui',
    'T_Supplier_Registration_CPTDC',
    'T_Supplier_Creation_CPTDC'
]

# Portable-only executions to keep (not in the main repo). SMOKE_TEST is
# petp_run.py's default self-check target — pruning it would break the smoke check.
KEEP_EXECUTIONS = ['SMOKE_TEST']

# After portable is refreshed, push its code into each external target, then upsert
# that target's own executions from the main repo. Each target: {'dir', 'executions'}.
# Only code is pushed (core/utils/mvp + top files) — NOT webdriver/download/log/config.
# Missing target dir is skipped (never created). Empty list = skip external sync.
SYNC_TARGETS = [
    {'dir': '/Users/i335607/MyProject/ariba_ai_assistant/rpa',
     'executions': ['T_Supplier_Registration_huihui', 'T_Supplier_Creation_huihui']},
    {'dir': '/Users/i335607/MyProject/ariba_ai_agent_base/rpa',
     'executions': ['T_Supplier_Registration_CPTDC', 'T_Supplier_Creation_CPTDC']},
]

# Portable "code" dirs pushed to each target (executions/ excluded — synced per-target).
TARGET_SYNC_DIRS = ['core', 'utils', 'mvp']
# Portable top-level files pushed to each target.
TARGET_SYNC_FILES = ['petp_run.py', 'requirements.txt']
# Never copy these into targets (heavy binaries / runtime products / per-target dir).
TARGET_IGNORE = shutil.ignore_patterns('__pycache__', '*.pyc', '.DS_Store',
                                       'webdriver', 'download', 'log', 'executions')


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
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns('__pycache__', *EXCLUDE_PROCESSORS))


def _exec_fname(n):
    return n if n.endswith('.yaml') else n + '.yaml'


def _sync_execution_dir(dst_dir, exec_names, prune=False):
    """Copy each name in exec_names from the main repo into dst_dir. When prune=True,
    also delete any other .yaml not in exec_names + KEEP_EXECUTIONS (mirror semantics —
    only for portable's OWN dir). External targets pass prune=False (upsert only): we
    add our executions but never delete files the target's owner put there.
    Returns (copied, removed, missing)."""
    src_dir = os.path.join(REPO, 'core/executions')
    os.makedirs(dst_dir, exist_ok=True)

    copied, missing = 0, []
    for name in exec_names:
        fname = _exec_fname(name)
        src = os.path.join(src_dir, fname)
        if not os.path.isfile(src):
            missing.append(fname)
            continue
        shutil.copy2(src, os.path.join(dst_dir, fname))
        copied += 1

    removed = []
    if prune:
        keep = {_exec_fname(n) for n in exec_names} | {_exec_fname(n) for n in KEEP_EXECUTIONS}
        for existing in os.listdir(dst_dir):
            if existing.endswith('.yaml') and existing not in keep:
                os.remove(os.path.join(dst_dir, existing))
                removed.append(existing)
    return copied, removed, missing


def _copy_executions():
    """Sync portable/core/executions to EXACTLY SYNC_EXECUTIONS (+ KEEP_EXECUTIONS)."""
    dst_dir = os.path.join(PORTABLE, 'core/executions')
    copied, removed, missing = _sync_execution_dir(dst_dir, SYNC_EXECUTIONS, prune=True)
    print('sync: %d execution(s) copied.' % copied)
    if removed:
        print('sync: %d stale execution(s) removed: %s' % (len(removed), ', '.join(sorted(removed))))
    if missing:
        print('sync: WARNING missing in main repo (not copied): ' + ', '.join(missing))


def _sync_to_targets():
    """Push portable's code dirs (executions/ excluded) + top files into each target,
    then upsert each target's own executions list from the main repo. Files the target
    already has — including executions we don't ship — are kept (never deleted)."""
    if not SYNC_TARGETS:
        return
    for target in SYNC_TARGETS:
        target_dir = target['dir']
        if not os.path.isdir(target_dir):
            print('sync: WARNING target dir missing (skipped): ' + target_dir)
            continue
        for d in TARGET_SYNC_DIRS:
            src = os.path.join(PORTABLE, d)
            if os.path.isdir(src):
                shutil.copytree(src, os.path.join(target_dir, d),
                                ignore=TARGET_IGNORE, dirs_exist_ok=True)
        for f in TARGET_SYNC_FILES:
            src = os.path.join(PORTABLE, f)
            if os.path.isfile(src):
                shutil.copy2(src, os.path.join(target_dir, f))
        # upsert this target's own executions (no prune — we don't own the target dir)
        exec_names = target.get('executions', [])
        copied, removed, missing = _sync_execution_dir(
            os.path.join(target_dir, 'core/executions'), exec_names)
        msg = 'sync: pushed code to target -> %s (%d execution(s)' % (target_dir, copied)
        if removed:
            msg += ', %d removed' % len(removed)
        msg += ')'
        print(msg)
        if missing:
            print('sync: WARNING missing in main repo (not copied to %s): %s'
                  % (target_dir, ', '.join(missing)))


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
