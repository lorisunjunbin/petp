import json
import logging
import os.path

from core.task import Task

"""
load Selenium IDE recording from file, then convert to tasks: 
    Current supported tasks: 
    - GO_TO_PAGE
    - FIND_THEN_CLICK
    - FIND_THEN_KEYIN is from [type] and [sendKeys]
    - FIND_THEN_COLLECT
"""


class SeleniumIDERecordingConverter(object):
    file_path: str
    test_name: str

    def __init__(self, file_path: str, test_name: str = ''):
        self.file_path = file_path
        self.test_name = test_name
        logging.info(
            f'SeleniumIDERecordingConverter will load tasks from recording: {self.test_name}, {self.file_path}')

    def set_test_name(self, test_name):
        self.test_name = test_name

    def get_test_names(self):
        with open(self.file_path, "r", encoding='utf-8') as read_file:
            data = json.load(read_file)
            return list(map(lambda x: x['name'], data['tests']))

    def is_initialized(self):
        return not self.file_path is None \
            and not self.test_name is None

    def convert_from_selenium_ide_recording(self) -> list:
        tasks = []
        with open(self.file_path, "r", encoding='utf-8') as read_file:
            data = json.load(read_file)
            base_url = data['url']
            commends = self.find_commands_by_test_name(data, self.test_name)

            for command in commends:
                task = self.convert(command, base_url)
                if not task is None:
                    tasks.append(task)

        return tasks

    def convert(self, command, baseUrl) -> Task | None:
        cmd = command['command']

        if cmd == 'open':
            return self.buildGO_TO_PAGETask(baseUrl, command['target'])

        if cmd == 'click':
            return self.buildFIND_THEN_CLICKTask(command)

        if cmd == 'type':
            return self.buildFIND_THEN_KEYINTask(command)

        if cmd == 'sendKeys':
            return self.buildFIND_THEN_KEYINTask(command, lambda v: v.replace('$', ''))

        if cmd == 'doubleClick':
            return self.buildFIND_THEN_COLLECTTask(command)

        return None

    def buildGO_TO_PAGETask(self, baseUrl, targetUrl):
        return Task('GO_TO_PAGE', json.dumps({"url": f"{baseUrl}{targetUrl}"}))

    def buildFIND_THEN_CLICKTask(self, command):
        by0id1 = self.find_proper_locator(command)
        if len(by0id1) == 0:
            logging.info(json.dumps({'msg': 'can not find proper xpath: ' + str(command)}))
            return None

        return Task('FIND_THEN_CLICK', json.dumps({'clickby': by0id1[0], 'identity': by0id1[1]}))

    def buildFIND_THEN_KEYINTask(self, command, fn=lambda v: v):
        by0id1 = self.find_proper_locator(command)
        if len(by0id1) == 0:
            logging.info(json.dumps({'msg': 'can not find proper xpath: ' + str(command)}))
            return None

        return Task('FIND_THEN_KEYIN',
                    json.dumps({'keyinby': by0id1[0], 'identity': by0id1[1], 'value': fn(command['value'])}))

    def buildFIND_THEN_COLLECTTask(self, command):
        by0id1 = self.find_proper_locator(command)

        if len(by0id1) == 0:
            logging.info(json.dumps({'msg': 'can not find proper xpath: ' + str(command)}))
            return None

        value_key = command['comment'] if len(command['comment']) > 0 else command['id']
        return Task('FIND_THEN_COLLECT', json.dumps({'collectby': by0id1[0], 'identity': by0id1[1],
                                                     'value_type': 'any', 'value_key': value_key}))

    def find_proper_locator(self, command) -> list[str]:

        xpathlocator = self.find_first_by_prefix('xpath=', command)
        if not xpathlocator == None:
            return ['xpath', xpathlocator]

        idlocator = self.find_first_by_prefix('id=', command)
        if not idlocator == None:
            return ['id', idlocator]

        csslocator = self.find_first_by_prefix('css=', command)
        if not csslocator == None:
            return ['css', csslocator]

    def find_first_by_prefix(self, prefix, command) -> str | None:

        default_target = command['target']

        if default_target.startswith(prefix):
            return default_target.replace(prefix, '')

        elif len(command['targets']) > 0:
            for ts in command['targets']:
                t = ts[0]
                if t.startswith(prefix):
                    return t.replace(prefix, '')

        return None

    def find_commands_by_test_name(self, data, testName):
        test = self.find_test_by_name(data, testName)
        commends = test['commands']
        return commends

    def find_test_by_name(self, data, testName):
        return next(filter(lambda t: t['name'] == testName, data['tests']), None)


if __name__ == '__main__':
    # customerserveroverview.side
    given = os.path.realpath('../../testcoverage/selenium/customerserveroverview.side')
    c = SeleniumIDERecordingConverter(given, 'Testcustomerserviewoverview')
    tasks = c.convert_from_selenium_ide_recording()
    for t in tasks:
        print(str(t))

    # GC-phoenix.side
    given = os.path.realpath('../../testcoverage/selenium/GC-phoenix.side')
    c = SeleniumIDERecordingConverter(given, 'gc-phoenix')
    tasks = c.convert_from_selenium_ide_recording()
    for t in tasks:
        print(str(t))
