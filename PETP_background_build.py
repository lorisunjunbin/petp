"""
PETP_background_build.py
Build script for PETP_backgroud.py (no-GUI / background mode).
Modelled after PETP_build.py.

Usage:
    python PETP_background_build.py

The output lands in  dist/PETP_background/
"""

import glob
import importlib
import os
import re
import shutil
import subprocess
import sys

import psutil

from core.definition.yamlro import YamlRO
from utils.OSUtils import OSUtils

# ---------------------------------------------------------------------------
# Released executions bundled into the distribution
# ---------------------------------------------------------------------------
executions_released = [
    'test_zip.yaml',
    'test_wait_for_seconds.yaml',
    'test_read_from_excel.yaml',
    'test_read_excel_loop_each_row_show.yaml',
    'test_data_convert.yaml',
    'ootb_find_icons.yaml',
    'loop_time.yaml',
    'test_petp_http_service.yaml',
    'OOTB_BS4_GET_DATA_FROM_news.ceic.ac.cn.yaml',
    'OOTB_AI_LLM_OLLAMA_MCP.yaml',
    'ENDECODER.yaml',
    'TEST_FIB_WITH_CACHE.yaml',
    'OOTB_AI_LLM_ZHIPU.yaml',
    'OOTB_AI_LLM_ZHIPU_MCP.yaml',
]

# Common third-party modules that PyInstaller may miss
KNOWN_PROBLEMATIC_MODULES = [
    'pandas', 'numpy', 'PIL', 'matplotlib', 'selenium',
    'bs4', 'lxml', 'openpyxl', 'cryptography', 'sklearn',
    'sqlalchemy', 'tensorflow', 'torch',
]

# Spec file names used by this build
_TEMPLATE_SPEC = 'PETP_background_build.spec'
_WORK_SPEC = 'PETP_background.spec'
_DIST_NAME = 'PETP_background'


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def kill_chromedriver_process_if_existed() -> None:
    for proc in psutil.process_iter():
        try:
            if proc.name() in ('chromedriver', 'chromedriver.exe'):
                proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass


def replace_words_in_file(file_path: str, old_word: str, new_word: str) -> None:
    with open(file_path, 'r', encoding='utf-8') as fh:
        content = fh.read()
    content = content.replace(old_word, new_word)
    with open(file_path, 'w', encoding='utf-8') as fh:
        fh.write(content)


def copy_folder_to_dist(directories: list) -> None:
    for source in directories:
        destination = os.path.join('dist', _DIST_NAME, source)
        try:
            if os.path.exists(source):
                shutil.copytree(source, destination, dirs_exist_ok=True)
            else:
                print(f'Warning: source directory {source!r} does not exist')
        except Exception as exc:
            print(f'Error copying {source!r} → {destination!r}: {exc}')


def clean_dist() -> None:
    shutil.rmtree('dist', ignore_errors=True)
    os.makedirs('dist', exist_ok=True)
    target = os.path.join('dist', _DIST_NAME)
    if os.path.exists(target):
        shutil.rmtree(target, ignore_errors=True)
    os.makedirs(target, exist_ok=True)


def clean_build() -> None:
    build_dir = os.path.join('build', _DIST_NAME)
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir, ignore_errors=True)
    if os.path.exists(_WORK_SPEC):
        try:
            os.remove(_WORK_SPEC)
        except Exception as exc:
            print(f'Warning: could not remove {_WORK_SPEC}: {exc}')


# ---------------------------------------------------------------------------
# Hidden-imports collection
# ---------------------------------------------------------------------------

def find_imported_modules() -> set:
    """Scan all .py files and return the set of importable top-level modules."""
    import_patterns = [
        re.compile(r'^\s*import\s+(\w+)'),
        re.compile(r'^\s*from\s+(\w+)\s+import'),
        re.compile(r'^\s*import\s+([^,\s]+)(?:,\s*([^,\s]+))*'),
        re.compile(r'^\s*from\s+([^,\s.]+)(?:\.[^,\s.]+)*\s+import'),
    ]

    modules: set = set()
    for file_path in glob.glob('**/*.py', recursive=True):
        try:
            with open(file_path, 'r', encoding='utf-8') as fh:
                for line in fh:
                    for pattern in import_patterns:
                        for match in pattern.findall(line):
                            if isinstance(match, tuple):
                                for m in match:
                                    if m and m.strip():
                                        modules.add(m.strip())
                            else:
                                if match and match.strip():
                                    modules.add(match.strip())
        except Exception as exc:
            print(f'Error reading {file_path}: {exc}')

    installed: set = set()
    for module in modules:
        if module.startswith('.'):
            continue
        try:
            importlib.import_module(module)
            installed.add(module)
        except ImportError:
            pass
        except TypeError as exc:
            if 'relative import' not in str(exc):
                print(f'TypeError importing {module}: {exc}')
        except Exception as exc:
            print(f'Error importing {module}: {exc}')

    return installed


def collect_hidden_imports() -> None:
    """Prepare the working spec file with all hidden imports filled in."""
    if os.path.exists(_WORK_SPEC):
        os.remove(_WORK_SPEC)
    shutil.copy(_TEMPLATE_SPEC, _WORK_SPEC)

    # Utility-module imports
    loaded_files = glob.glob(os.path.join('utils', '**/*.py'), recursive=True)
    loaded_imports = [
        f.replace('\\', '.').replace('/', '.').rstrip('.py')
        for f in loaded_files
    ]

    # Base hidden imports (no GUI / wx entries needed for background mode)
    hidden_imports = [
        'utils', 'sqlite3', 'requests',
        'core.processors.sub.dbprocessors.BaseDBAccess',
        'encodings', 'pkg_resources.py2_warn',
        'packaging', 'packaging.version',
        'numpy.core._methods', 'numpy.lib.format',
        'appdirs',
        'engineio.async_drivers.threading',
        'engineio.async_drivers.eventlet',
        'socketio.async_drivers.threading',
        'engineio.async_drivers',
        'json', 'urllib3', 'xml', 'xmlrpc',
        'asyncio.base_subprocess', 'asyncio.subprocess',
        'asyncio.proactor_events',
        # Background-specific
        'argparse', 'signal', 'threading',
        'core.runtime.BackgroundRuntime',
        'core.runtime.UiProcessorPolicy',
        'httpservice.BackgroundHttpServer',
        'mvp.model.PETPModel',
    ]

    for module in find_imported_modules():
        if module not in hidden_imports and not module.startswith(('os', 'sys', 're')):
            hidden_imports.append(module)

    for module in KNOWN_PROBLEMATIC_MODULES:
        try:
            importlib.import_module(module)
            if module not in hidden_imports:
                hidden_imports.append(module)
        except ImportError:
            pass

    for hi in loaded_imports:
        if hi not in hidden_imports:
            hidden_imports.append(hi)

    replace_words_in_file(_WORK_SPEC, '$hidden_imports$', str(hidden_imports))

    # collect_submodules list
    collect_submodules = []
    for module in ['selenium', 'PIL', 'requests']:
        try:
            importlib.import_module(module)
            collect_submodules.append(module)
        except ImportError:
            pass
    replace_words_in_file(_WORK_SPEC, '$collect_submodules$', str(collect_submodules))

    # Data directories to bundle
    data_dirs = [
        ('config', 'config'),
        ('core/executions', 'core/executions'),
        ('image', 'image'),
        ('resources', 'resources'),
    ]
    replace_words_in_file(_WORK_SPEC, '$data_dirs$', str(data_dirs))


# ---------------------------------------------------------------------------
# Post-build helpers
# ---------------------------------------------------------------------------

def keep_released_execution_only() -> None:
    executions_path = os.path.join('dist', _DIST_NAME, 'core', 'executions')
    if not (os.path.exists(executions_path) and os.path.isdir(executions_path)):
        print(f'Warning: executions directory not found at {executions_path}')
        return
    for execution in os.listdir(executions_path):
        if execution not in executions_released and execution.endswith('.yaml'):
            file_path = os.path.join(executions_path, execution)
            print(f'Removing execution file: {file_path}')
            os.remove(file_path)


def change_http_port(port: int) -> None:
    """Update the HTTP port in the bundled petpconfig.yaml."""
    config_path = os.path.join('dist', _DIST_NAME, 'config', 'petpconfig.yaml')
    if not os.path.exists(config_path):
        print(f'Warning: config file not found at {config_path}')
        return
    try:
        yaml_content = YamlRO.get_yaml_from_file(config_path)
        if 'application' in yaml_content and 'http_port' in yaml_content['application']:
            yaml_content['application']['http_port'] = port
            print(f'Updating HTTP port to: {port}')
            YamlRO.write(config_path, yaml_content)
        else:
            print("Warning: 'application.http_port' not found in config")
    except Exception as exc:
        print(f'Error updating HTTP port: {exc}')


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    # 1. Kill lingering chromedriver processes
    kill_chromedriver_process_if_existed()

    # 2. Clean previous artefacts
    clean_build()
    clean_dist()

    # 3. Resolve hidden imports and prepare the working spec
    collect_hidden_imports()

    # 4. Run PyInstaller
    try:
        subprocess.run(['pyinstaller', '-y', f'./{_WORK_SPEC}'], check=True)
        print('Build completed successfully')
    except subprocess.CalledProcessError as exc:
        print(f'Build failed: {exc}')
        sys.exit(1)

    # 5. Verify the executable was produced
    if sys.platform.startswith('win'):
        executable = os.path.join('dist', _DIST_NAME, f'{_DIST_NAME}.exe')
    else:
        executable = os.path.join('dist', _DIST_NAME, _DIST_NAME)

    if os.path.exists(executable):
        print(f'Executable created at: {executable}')
    else:
        print(f'WARNING: executable not found at expected path: {executable}')

    # 6. Copy runtime resources into the dist folder
    copy_folder_to_dist([
        'config',
        'core/executions',
        'core/processors',
        'core/pipelines',
        'image',
        'resources',
        'download',
        'testcoverage',
        os.path.join('webdriver', OSUtils.get_system()),
    ])

    # 7. Strip non-released executions and set the HTTP port
    keep_released_execution_only()
    change_http_port(8866)

