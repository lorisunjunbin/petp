import os
import glob
import shutil

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
	'test_petp_http_service.yaml'
]

def kill_chromedriver_process_if_existed():
	for proc in psutil.process_iter():
		if proc.name() == "chromedriver" or proc.name() == "chromedriver.exe":
			proc.kill()


def replace_words_in_file(file_path, old_word, new_word):
	with open(file_path, 'r') as file:
		file_content = file.read()

	file_content = file_content.replace(old_word, new_word)

	with open(file_path, 'w') as file:
		file.write(file_content)


def copy_folder_to_dist(directories):
	for source in directories:
		destination = os.path.join('dist', source)
		shutil.copytree(source, destination, dirs_exist_ok=True)


def clean_dist():
	shutil.rmtree('dist', ignore_errors=True)
	os.makedirs('dist', exist_ok=True)


def clean_build():
	shutil.rmtree('build' + os.sep + 'PETP', ignore_errors=True)


def collect_hidden_imports():
	# delete PETP.spec if existed
	if os.path.exists('PETP.spec'):
		os.remove('PETP.spec')

	# copy PETP_build.spec to PETP.spec
	shutil.copy('PETP_build.spec', 'PETP.spec')
	loaded_files = glob.glob(os.path.join('utils', '**/*.py'), recursive=True)
	loaded_imports = [f.replace('\\', '.').replace('/', '.').rstrip('.py') for f in loaded_files]

	_hiddenimports = ['pyautogui', 'utils', 'sqlite3','requests','core.processors.sub.dbprocessors.BaseDBAccess']  # any more required hidden imports can be added here.

	for hidden_import in loaded_imports:
		_hiddenimports.append(hidden_import)

	replace_words_in_file('PETP.spec', '$hidden_imports$', str(_hiddenimports))


def keey_released_execution_only():

	executions_path = os.path.join('dist', 'core', 'executions')
	
	if os.path.exists(executions_path) and os.path.isdir(executions_path):
		all_executions = os.listdir(executions_path)
		
		for execution in all_executions:

			if execution not in executions_released and execution.endswith('.yaml'):
				file_path = os.path.join(executions_path, execution)
				print(f"Removing execution file: {file_path}")
				os.remove(file_path)

	else:
		print(f"Warning: Executions directory not found at {executions_path}")


if __name__ == '__main__':
	# kill chromedriver process if existed
	kill_chromedriver_process_if_existed()

	# clean dist folder
	clean_build()
	clean_dist()

	# figure out all the necessary python files,  make them as hidden imports
	collect_hidden_imports()

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

	keey_released_execution_only()

	# run pyinstaller
	subprocess.run(['pyinstaller', './PETP.spec'], check=True)

