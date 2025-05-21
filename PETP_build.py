import os
import glob
import shutil
import sys
import importlib
import re
import psutil
import subprocess

from utils.OSUtils import OSUtils

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
	'TEST_FIB_WITH_CACHE.yaml'
]

# Common problematic modules that need special handling
KNOWN_PROBLEMATIC_MODULES = [
	'pandas', 'numpy', 'PIL', 'matplotlib', 'selenium', 'wx',
	'bs4', 'lxml', 'openpyxl', 'cryptography', 'sklearn',
	'sqlalchemy', 'PyQt5', 'PySide2', 'tensorflow', 'torch'
]


def kill_chromedriver_process_if_existed():
	for proc in psutil.process_iter():
		if proc.name() == "chromedriver" or proc.name() == "chromedriver.exe":
			proc.kill()


def replace_words_in_file(file_path, old_word, new_word):
	with open(file_path, 'r', encoding='utf-8') as file:
		file_content = file.read()

	file_content = file_content.replace(old_word, new_word)

	with open(file_path, 'w', encoding='utf-8') as file:
		file.write(file_content)


def copy_folder_to_dist(directories):
	for source in directories:
		destination = os.path.join('dist', 'PETP', source)
		try:
			if os.path.exists(source):
				shutil.copytree(source, destination, dirs_exist_ok=True)
			else:
				print(f"Warning: Source directory {source} does not exist")
		except Exception as e:
			print(f"Error copying {source} to {destination}: {e}")


def clean_dist():
	# Remove the entire dist directory
	shutil.rmtree('dist', ignore_errors=True)
	os.makedirs('dist', exist_ok=True)

	# Also ensure PETP subdirectory is clean (in case rmtree failed partially)
	petp_dir = os.path.join('dist', 'PETP')
	if os.path.exists(petp_dir):
		shutil.rmtree(petp_dir, ignore_errors=True)
	os.makedirs(petp_dir, exist_ok=True)


def clean_build():
	# Clean build directory
	build_dir = 'build' + os.sep + 'PETP'
	if os.path.exists(build_dir):
		shutil.rmtree(build_dir, ignore_errors=True)

	# Also remove spec file to ensure clean build
	if os.path.exists('PETP.spec'):
		try:
			os.remove('PETP.spec')
		except Exception as e:
			print(f"Warning: Could not remove PETP.spec: {e}")


def find_imported_modules():
	"""Find all imported modules from Python files recursively."""
	# Define patterns to find imports in Python code
	import_patterns = [
		re.compile(r'^\s*import\s+(\w+)'),
		re.compile(r'^\s*from\s+(\w+)\s+import'),
		re.compile(r'^\s*import\s+([^,\s]+)(?:,\s*([^,\s]+))*'),
		re.compile(r'^\s*from\s+([^,\s\.]+)(?:\.[^,\s\.]+)*\s+import'),
	]

	modules = set()

	# Find all Python files in the project
	python_files = glob.glob('**/*.py', recursive=True)

	for file_path in python_files:
		try:
			with open(file_path, 'r', encoding='utf-8') as file:
				for line in file:
					for pattern in import_patterns:
						matches = pattern.findall(line)
						if matches:
							for match in matches:
								if isinstance(match, tuple):
									for m in match:
										if m and m.strip():
											modules.add(m.strip())
								else:
									if match and match.strip():
										modules.add(match.strip())
		except Exception as e:
			print(f"Error processing file {file_path}: {e}")

	# Check installed status
	installed_modules = set()
	for module in modules:
		try:
			importlib.import_module(module)
			installed_modules.add(module)
		except ImportError:
			pass

	return installed_modules


def collect_hidden_imports():
	# delete PETP.spec if existed
	if os.path.exists('PETP.spec'):
		os.remove('PETP.spec')

	# copy PETP_build.spec to PETP.spec
	shutil.copy('PETP_build.spec', 'PETP.spec')
	loaded_files = glob.glob(os.path.join('utils', '**/*.py'), recursive=True)
	loaded_imports = [f.replace('\\', '.').replace('/', '.').rstrip('.py') for f in loaded_files]

	# Base hidden imports covering common problematic areas
	_hiddenimports = [
		'pyautogui', 'utils', 'sqlite3', 'requests',
		'core.processors.sub.dbprocessors.BaseDBAccess',
		'encodings', 'pkg_resources.py2_warn', 'packaging', 'packaging.version',
		'numpy.core._methods', 'numpy.lib.format',
		'appdirs', 'engineio.async_drivers.threading',
		'engineio.async_drivers.eventlet', 'socketio.async_drivers.threading',
		'engineio.async_drivers', 'json', 'urllib3', 'xml', 'xmlrpc',
		'PIL._tkinter_finder', 'wx._xml', 'wx._html', 'wx._adv',
		'wx._core', 'wx._aui', 'wx._dataview', 'wx._grid', 'wx._richtext',
		'wx._stc', 'ctypes.macholib.dyld', 'asyncio.base_subprocess',
		'asyncio.subprocess', 'asyncio.proactor_events',
	]

	# Find all imported third-party modules
	for module in find_imported_modules():
		if module not in _hiddenimports and not module.startswith(('os', 'sys', 're')):
			_hiddenimports.append(module)

	# Add submodules for known problematic modules
	for module in KNOWN_PROBLEMATIC_MODULES:
		try:
			importlib.import_module(module)
			_hiddenimports.append(module)
			print(f"Added {module} to hidden imports")
		except ImportError:
			pass

	for hidden_import in loaded_imports:
		if hidden_import not in _hiddenimports:
			_hiddenimports.append(hidden_import)

	# Replace the placeholder in the spec file
	replace_words_in_file('PETP.spec', '$hidden_imports$', str(_hiddenimports))

	# Also generate a collect_submodules list for really problematic packages
	collect_submodules = []
	for module in ['wx', 'numpy', 'pandas', 'selenium', 'PIL', 'requests']:
		try:
			importlib.import_module(module)
			collect_submodules.append(module)
		except ImportError:
			pass

	replace_words_in_file('PETP.spec', '$collect_submodules$', str(collect_submodules))

	# Add data files collection for runtime resources
	data_dirs = [
		('config', 'config'),
		('core/executions', 'core/executions'),
		('image', 'image'),
		('resources', 'resources'),
	]
	replace_words_in_file('PETP.spec', '$data_dirs$', str(data_dirs))


def keep_released_execution_only():
	executions_path = os.path.join('dist', 'PETP', 'core', 'executions')

	if os.path.exists(executions_path) and os.path.isdir(executions_path):
		all_executions = os.listdir(executions_path)

		for execution in all_executions:
			if execution not in executions_released and execution.endswith('.yaml'):
				file_path = os.path.join(executions_path, execution)
				print(f"Removing execution file: {file_path}")
				os.remove(file_path)
	else:
		print(f"Warning: Executions directory not found at {executions_path}")


def create_debug_version():
	"""Create a debug version first to help diagnose issues"""
	# Copy the spec file to a debug version
	shutil.copy('PETP.spec', 'PETP_debug.spec')

	# Enable debug options
	replace_words_in_file('PETP_debug.spec', 'debug=False', 'debug=True')
	replace_words_in_file('PETP_debug.spec', 'console=False', 'console=True')

	# Run PyInstaller with the debug spec and extra verbosity
	try:
		subprocess.run(['pyinstaller', '--log-level=DEBUG', './PETP_debug.spec'], check=True)
		print("Debug build completed successfully")
	except subprocess.CalledProcessError as e:
		print(f"Debug build failed: {e}")
		sys.exit(1)


if __name__ == '__main__':
	# kill chromedriver process if existed
	kill_chromedriver_process_if_existed()

	# clean dist folder
	clean_build()
	clean_dist()

	# figure out all the necessary python files,  make them as hidden imports
	collect_hidden_imports()

	# Create a debug version first if needed (uncomment when debugging crashes)
	# create_debug_version()

	# run pyinstaller with -y option to force overwrite
	try:
		subprocess.run(['pyinstaller', '-y', './PETP.spec'], check=True)
		print("Build completed successfully")
	except subprocess.CalledProcessError as e:
		print(f"Build failed: {e}")
		sys.exit(1)

	# Test the executable before distribution
	print("Build successful! Testing the executable...")
	try:
		if sys.platform.startswith('win'):
			executable = os.path.join('dist', 'PETP', 'PETP.exe')
		else:
			executable = os.path.join('dist', 'PETP', 'PETP')

		# Just check if it exists, don't actually run it
		if os.path.exists(executable):
			print(f"Executable created at: {executable}")
		else:
			print(f"WARNING: Executable not found at expected path: {executable}")
	except Exception as e:
		print(f"Error checking executable: {e}")

	# move config,core, image, testcoverage to dist folder.
	copy_folder_to_dist(
		['config',
		 'core/executions', 'core/processors', 'core/pipelines',
		 'image',
		 'resources',
		 'download',
		 'testcoverage',
		 'webdriver' + os.sep + OSUtils.get_system()
		 ]
	)

	keep_released_execution_only()
