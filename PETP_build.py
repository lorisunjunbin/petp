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
        shutil.copytree(source, destination)


if __name__ == '__main__':

    # step1 figure out all the processor and sub processor files,  make them as hidden imports
    processor_files = glob.glob(os.path.join('core/processors', '**/*.py'), recursive=True)
    processor_imports = [f.replace('\\', '.').replace('/', '.').rstrip('.py') for f in processor_files]
    _hiddenimports = ['core.processors']
    for processor in processor_imports:
        _hiddenimports.append(processor)

    replace_words_in_file('PETP.spec', '$hidden_imports$', str(_hiddenimports))

    # step2 move config,core, image, testcoverage to dist folder.
    copy_folder_to_dist(['config', 'core/executions', 'core/processors', 'core/pipelines', 'image', 'resources', 'testcoverage'])

    # step3 run pyinstaller
    subprocess.run(['pyinstaller', './PETP.spec'], check=True)