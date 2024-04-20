import os
import glob
import shutil
import subprocess


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


def collect_hidden_imports():
    loaded_files = glob.glob(os.path.join('utils', '**/*.py'), recursive=True)
    loaded_imports = [f.replace('\\', '.').replace('/', '.').rstrip('.py') for f in loaded_files]
    _hiddenimports = ['utils']
    for hidden_import in loaded_imports:
        _hiddenimports.append(hidden_import)

    replace_words_in_file('PETP.spec', '$hidden_imports$', str(_hiddenimports))


if __name__ == '__main__':
    # clean dist folder
    clean_dist()

    # figure out all the necessary python files,  make them as hidden imports
    collect_hidden_imports()

    # move config,core, image, testcoverage to dist folder.
    copy_folder_to_dist(
        ['config', 'core/executions', 'core/processors', 'core/pipelines', 'image', 'resources', 'testcoverage']
    )

    # run pyinstaller
    subprocess.run(['pyinstaller', './PETP.spec'], check=True)
