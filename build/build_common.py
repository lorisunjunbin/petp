"""Shared build utilities for PETP GUI and Background builds."""

import glob
import importlib
import os
import re
import shutil
import subprocess
import sys

# Ensure working directory is project root regardless of where the script is invoked
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(PROJECT_ROOT)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import psutil

from core.definition.yamlro import YamlRO
from utils.OSUtils import OSUtils

EXECUTIONS_RELEASED = [
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
    'OOTB_RUN_JS.yaml',
    'T_CENC_EARTHQUAKE_SEARCH.yaml',
    'ootb_keep_screen_unlocked.yaml',
    'T_SEND_EMAIL.yaml',
    'T_RECEIVE_EMAIL.yaml',
    'T_DAILY_ALMANAC.yaml',
    'T_WEATHER_QUERY.yaml'
]

KNOWN_PROBLEMATIC_MODULES = [
    'pandas', 'numpy', 'PIL', 'matplotlib', 'selenium',
    'bs4', 'lxml', 'openpyxl', 'cryptography',
]

COPY_DIRS_COMMON = [
    'config',
    'core/executions',
    'core/processors',
    'core/pipelines',
    'image',
    'resources',
    'download',
    'testcoverage',
    os.path.join('webdriver', OSUtils.get_system()),
]


def copy_folder_to_app_bundle(directories, dist_name):
    """Copy runtime resource directories from dist/<name>/ into PETP.app/Contents/Resources/ (macOS only)."""
    if sys.platform != 'darwin':
        return
    app_resources = os.path.join('dist', f'{dist_name}.app', 'Contents', 'Resources')
    if not os.path.isdir(app_resources):
        print(f'Warning: .app Resources dir not found at {app_resources}')
        return
    dist_dir = os.path.join('dist', dist_name)
    for source in directories:
        src_path = os.path.join(dist_dir, source)
        destination = os.path.join(app_resources, source)
        try:
            if os.path.exists(destination):
                shutil.rmtree(destination)
            if os.path.exists(src_path):
                shutil.copytree(src_path, destination)
            else:
                print(f'Warning: source directory {src_path!r} does not exist')
        except Exception as e:
            print(f'Error copying {src_path!r} -> {destination!r}: {e}')
    print(f'Copied runtime resources into {app_resources}')


def kill_chromedriver():
    for proc in psutil.process_iter():
        try:
            if proc.name() in ('chromedriver', 'chromedriver.exe'):
                proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass


def replace_words_in_file(file_path, old_word, new_word):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    content = content.replace(old_word, new_word)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)


def copy_folder_to_dist(directories, dist_name):
    for source in directories:
        destination = os.path.join('dist', dist_name, source)
        try:
            if os.path.exists(source):
                shutil.copytree(source, destination, dirs_exist_ok=True)
            else:
                print(f'Warning: source directory {source!r} does not exist')
        except Exception as e:
            print(f'Error copying {source!r} -> {destination!r}: {e}')


def clean_dist(dist_name):
    target = os.path.join('dist', dist_name)
    if os.path.exists(target):
        shutil.rmtree(target, ignore_errors=True)
    os.makedirs(target, exist_ok=True)


def clean_build(dist_name, work_spec):
    build_dir = os.path.join('build', dist_name)
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir, ignore_errors=True)
    if os.path.exists(work_spec):
        try:
            os.remove(work_spec)
        except Exception as e:
            print(f'Warning: could not remove {work_spec}: {e}')


def find_imported_modules():
    """Scan all .py files and return the set of importable top-level modules."""
    import_patterns = [
        re.compile(r'^\s*import\s+(\w+)'),
        re.compile(r'^\s*from\s+(\w+)\s+import'),
        re.compile(r'^\s*import\s+([^,\s]+)(?:,\s*([^,\s]+))*'),
        re.compile(r'^\s*from\s+([^,\s.]+)(?:\.[^,\s.]+)*\s+import'),
    ]

    modules = set()
    for file_path in glob.glob('**/*.py', recursive=True):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    for pattern in import_patterns:
                        for match in pattern.findall(line):
                            if isinstance(match, tuple):
                                for m in match:
                                    if m and m.strip():
                                        modules.add(m.strip())
                            elif match and match.strip():
                                modules.add(match.strip())
        except Exception as e:
            print(f'Error reading {file_path}: {e}')

    installed = set()
    for module in modules:
        if module.startswith('.'):
            continue
        try:
            importlib.import_module(module)
            installed.add(module)
        except ImportError:
            pass
        except TypeError as e:
            if 'relative import' not in str(e):
                print(f'TypeError importing {module}: {e}')
        except Exception as e:
            print(f'Error importing {module}: {e}')

    return installed


def collect_hidden_imports(template_spec, work_spec, extra_hidden_imports=None):
    """Prepare the working spec file with all hidden imports filled in."""
    if os.path.exists(work_spec):
        os.remove(work_spec)
    shutil.copy(template_spec, work_spec)

    loaded_files = (
        glob.glob(os.path.join('utils', '**/*.py'), recursive=True) +
        glob.glob(os.path.join('core', 'processors', 'sub', '**/*.py'), recursive=True)
    )
    loaded_imports = [
        f.replace('\\', '.').replace('/', '.').rstrip('.py')
        for f in loaded_files
    ]

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
    ]

    if extra_hidden_imports:
        hidden_imports.extend(extra_hidden_imports)

    for module in find_imported_modules():
        if module not in hidden_imports and not module.startswith(('os', 'sys', 're')):
            hidden_imports.append(module)

    for module in KNOWN_PROBLEMATIC_MODULES:
        try:
            importlib.import_module(module)
            if module not in hidden_imports:
                hidden_imports.append(module)
                print(f'Added {module} to hidden imports')
        except ImportError:
            pass

    for hi in loaded_imports:
        if hi not in hidden_imports:
            hidden_imports.append(hi)

    replace_words_in_file(work_spec, '$hidden_imports$', str(hidden_imports))

    collect_submodules = []
    for module in ['selenium', 'PIL', 'requests']:
        try:
            importlib.import_module(module)
            collect_submodules.append(module)
        except ImportError:
            pass
    replace_words_in_file(work_spec, '$collect_submodules$', str(collect_submodules))

    data_dirs = [
        ('config', 'config'),
        ('core/executions', 'core/executions'),
        ('image', 'image'),
        ('resources', 'resources'),
    ]
    replace_words_in_file(work_spec, '$data_dirs$', str(data_dirs))


def keep_released_execution_only(dist_name):
    executions_path = os.path.join('dist', dist_name, 'core', 'executions')
    if not (os.path.exists(executions_path) and os.path.isdir(executions_path)):
        print(f'Warning: executions directory not found at {executions_path}')
        return
    for execution in os.listdir(executions_path):
        if execution not in EXECUTIONS_RELEASED and execution.endswith('.yaml'):
            file_path = os.path.join(executions_path, execution)
            print(f'Removing execution file: {file_path}')
            os.remove(file_path)


def expand_env_vars_in_config(dist_name):
    """Replace ${ENV_VAR} placeholders in dist config with actual env values."""
    import re
    config_path = os.path.join('dist', dist_name, 'config', 'petpconfig.yaml')
    if not os.path.exists(config_path):
        print(f'Warning: config file not found at {config_path}')
        return
    try:
        yaml_content = YamlRO.get_yaml_from_file(config_path)
        app = yaml_content.get('application', {})
        changed = False
        for key, value in app.items():
            if isinstance(value, str):
                m = re.fullmatch(r'\$\{(.+)\}', value.strip())
                if m:
                    resolved = os.environ.get(m.group(1), '')
                    if resolved:
                        app[key] = resolved
                        print(f'Expanded {key}: ${{{m.group(1)}}} -> (resolved)')
                        changed = True
                    else:
                        print(f'Warning: env var {m.group(1)} not set, leaving {key} unchanged')
        if changed:
            YamlRO.write(config_path, yaml_content)
    except Exception as e:
        print(f'Error expanding env vars in config: {e}')


def change_http_port(dist_name, port):
    config_path = os.path.join('dist', dist_name, 'config', 'petpconfig.yaml')
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
    except Exception as e:
        print(f'Error updating HTTP port: {e}')


def run_pyinstaller(spec_path):
    if sys.platform == 'darwin':
        try:
            from PyInstaller.utils import osx as _osx
            _original_sign = _osx.sign_binary

            def _tolerant_sign(filename, identity=None, entitlements_file=None, deep=False):
                try:
                    _original_sign(filename, identity, entitlements_file, deep)
                except SystemError as e:
                    print(f'Warning: codesign failed (non-fatal): {e}')

            _osx.sign_binary = _tolerant_sign
        except Exception:
            pass
    try:
        import PyInstaller.__main__
        PyInstaller.__main__.run(['-y', f'./{spec_path}'])
        print('Build completed successfully')
    except SystemExit as e:
        if e.code:
            print(f'Build failed with exit code: {e.code}')
            sys.exit(1)
    except Exception as e:
        print(f'Build failed: {e}')
        sys.exit(1)


def sync_dist_to_build(dist_name):
    source_dir = os.path.join('dist', dist_name)
    target_dir = os.path.join('build', dist_name)

    if not os.path.isdir(source_dir):
        print(f'Warning: dist output directory not found at {source_dir}')
        return

    try:
        shutil.copytree(source_dir, target_dir, dirs_exist_ok=True)
        print(f'Synced dist output to build directory: {source_dir} -> {target_dir}')
    except Exception as e:
        print(f'Warning: failed to sync dist output to build directory: {e}')


def verify_executable(dist_name, exe_name):
    if sys.platform.startswith('win'):
        executable = os.path.join('dist', dist_name, f'{exe_name}.exe')
    else:
        executable = os.path.join('dist', dist_name, exe_name)

    if os.path.exists(executable):
        print(f'Executable created at: {executable}')
    else:
        print(f'WARNING: executable not found at expected path: {executable}')

    # onedir build requires the bundled Python runtime under dist/<name>/_internal
    if sys.platform.startswith('win'):
        runtime_dll = os.path.join('dist', dist_name, '_internal', 'python314.dll')
        if os.path.exists(runtime_dll):
            print(f'Runtime DLL verified at: {runtime_dll}')
        else:
            print(
                'WARNING: python314.dll not found in dist runtime folder. '
                'Do not run build/<name>/<exe>.exe; run the executable under dist/<name>/ instead.'
            )

