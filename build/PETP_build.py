"""Build script for PETP (GUI mode)."""

from build_common import (
    COPY_DIRS_COMMON,
    kill_chromedriver, clean_build, clean_dist,
    collect_hidden_imports, run_pyinstaller,
    verify_executable, copy_folder_to_dist, copy_folder_to_app_bundle,
    keep_released_execution_only, change_http_port, expand_env_vars_in_config,
    sync_dist_to_build,
)

DIST_NAME = 'PETP'
TEMPLATE_SPEC = 'build/PETP_build.spec'
WORK_SPEC = 'PETP.spec'

EXTRA_HIDDEN_IMPORTS = [
    'pyautogui',
    'PIL._tkinter_finder',
    'wx._xml', 'wx._html', 'wx._adv',
    'wx._core', 'wx._aui', 'wx._dataview',
    'wx._grid', 'wx._richtext', 'wx._stc',
    'ctypes.macholib.dyld',
]

if __name__ == '__main__':
    kill_chromedriver()
    clean_build(DIST_NAME, WORK_SPEC)
    clean_dist(DIST_NAME)
    collect_hidden_imports(TEMPLATE_SPEC, WORK_SPEC, EXTRA_HIDDEN_IMPORTS)
    run_pyinstaller(WORK_SPEC)
    verify_executable(DIST_NAME, 'PETP')
    copy_folder_to_dist(COPY_DIRS_COMMON, DIST_NAME)
    keep_released_execution_only(DIST_NAME)
    change_http_port(DIST_NAME, 8888)
    expand_env_vars_in_config(DIST_NAME)
    copy_folder_to_app_bundle(COPY_DIRS_COMMON, DIST_NAME)
    sync_dist_to_build(DIST_NAME)
