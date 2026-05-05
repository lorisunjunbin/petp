"""Build script for PETP background (no-GUI / headless mode)."""

from build_common import (
    COPY_DIRS_COMMON,
    kill_chromedriver, clean_build, clean_dist,
    collect_hidden_imports, run_pyinstaller,
    verify_executable, copy_folder_to_dist,
    keep_released_execution_only, change_http_port,
    sync_dist_to_build,
)

DIST_NAME = 'PETP_background'
TEMPLATE_SPEC = 'build/PETP_background_build.spec'
WORK_SPEC = 'PETP_background.spec'

EXTRA_HIDDEN_IMPORTS = [
    'argparse', 'signal', 'threading',
    'core.runtime.BackgroundRuntime',
    'core.runtime.UiProcessorPolicy',
    'httpservice.BackgroundHttpServer',
    'mvp.model.PETPModel',
]

if __name__ == '__main__':
    kill_chromedriver()
    clean_build(DIST_NAME, WORK_SPEC)
    clean_dist(DIST_NAME)
    collect_hidden_imports(TEMPLATE_SPEC, WORK_SPEC, EXTRA_HIDDEN_IMPORTS)
    run_pyinstaller(WORK_SPEC)
    verify_executable(DIST_NAME, DIST_NAME)
    copy_folder_to_dist(COPY_DIRS_COMMON, DIST_NAME)
    keep_released_execution_only(DIST_NAME)
    change_http_port(DIST_NAME, 8866)
    sync_dist_to_build(DIST_NAME)
