import json
import logging
import os
import time
from threading import Condition

import cryptocode

from core.loop import Loop
from core.task import Task
from mvp.view.PETPView import PETPView
from utils.DateUtil import DateUtil
from utils.OSUtils import OSUtils


class Processor:
    SEPARATOR: str = '|'
    ITEM_SEPARATOR: str = '->'
    SALT: str = 'petpisawesome'

    TPL: str
    DESC: str = f''' 
        TODO: Explain the usage of current  processor 
        - overview
        - parameter explanation for  one by one
        - give example
    '''

    # Available categories:
    CATE_DEFAULT: str = 'Default'
    CATE_FILE: str = 'File'
    CATE_ZIP: str = 'Zip'
    CATE_SELENIUM: str = 'Selenium'
    CATE_MOUSE: str = 'Mouse'
    CATE_GUI: str = 'GUI'
    CATE_EMAIL: str = 'Email'
    CATE_DATABASE: str = 'Database'
    CATE_PARAMIKO: str = 'Paramiko'
    CATE_JSON: str = 'JSON'
    CATE_EXCEL: str = 'Excel'
    CATE_GENERAL: str = 'General'
    CATE_YUTUBE: str = 'Youtube'
    CATE_DATA_PROCESSING: str = 'DataProcessing'
    CATE_HTTP: str = 'HTTP'

    is_in_loop: False
    current_loop: Loop

    task: Task
    input_param: dict
    condition: Condition
    view: PETPView

    category: str = 'default'

    def process(self) -> None:
        # must be implemented in subclass
        pass

    def get_category(self) -> str:
        return self.category

    def do_process(self):
        self.process()

    def handle_ui_thread_callback(self, given):
        pass

    def set_current_loop(self, loop):
        self.current_loop = loop

    def get_current_loop(self):
        return self.current_loop

    def set_in_loop(self, is_in_loop):
        self.is_in_loop = is_in_loop

    def set_view(self, view):
        self.view = view

    def get_view(self):
        return self.view

    def set_condition(self, condition: Condition):
        self.condition = condition

    def get_condition(self):
        return self.condition

    def need_skip(self):
        # if run in cron and skip_in_pipeline is yes.
        if self.has_param("skip_in_pipeline") and self.has_param("run_in_pipeline"):
            skip_in_pipeline = self.get_param("skip_in_pipeline")
            run_in_pipeline = self.get_param("run_in_pipeline")
            if "yes" == skip_in_pipeline.lower() and "yes" == run_in_pipeline.lower():
                return True

        return False

    def extra_wait(self):
        if self.has_param("wait"):
            wait_in_seconds = int(self.get_param("wait"))
            if wait_in_seconds > 0:
                time.sleep(wait_in_seconds)

    def get_tpl(self):
        return self.TPL

    def get_desc(self):
        return f'''
        ----------------------------------------------------{self.DESC}    ----------------------------------------------------'''

    def get_now_str(self):
        return DateUtil.get_now_in_str()

    def get_ddir(self):
        return os.path.realpath('./download')

    def get_rdir(self):
        return os.path.realpath('./resources')

    def get_tdir(self):
        return os.path.realpath('./testcoverage')

    def set_task(self, task: Task):
        self.task = task
        self.input_param = json.loads(self.task.input)

    def get_param_bool_if_equal(self, name, true_flag='yes'):
        return True \
            if self.has_param(name) and true_flag == self.input_param[name].lower() \
            else False

    def get_param(self, name):
        if self.has_param(name):
            return self.input_param[name]

    def has_param(self, name):

        return name in self.input_param and \
            (
                len(self.input_param[name]) > 0
                if type(self.input_param[name]) is str
                else not self.input_param[name] is None
            )

    def get_all_params(self):
        return self.input_param

    def append_data_for_loop(self, k, v):
        """
        keep the data @ data_chain[loop_code][current_idx][k] = v
        """
        d = self.task.data_chain
        l = self.get_current_loop()
        loop_code = l.get_loop_code()
        loop_index_key = l.get_loop_index_key()
        current_idx = d[loop_index_key]

        if not loop_code in d:
            d[loop_code] = {}

        if not current_idx in d[loop_code]:
            d[loop_code][current_idx] = {}

        d[loop_code][current_idx][k] = v

        if not l.get_item_key() in d[loop_code][current_idx]:
            d[loop_code][current_idx][l.get_item_key()] = d[l.get_item_key()]

    def get_data_by_loop(self, k):
        d = self.task.data_chain
        l = self.get_current_loop()
        loop_code = l.get_loop_code()
        loop_index_key = l.get_loop_index_key()
        current_idx = d[loop_index_key]
        return d[loop_code][current_idx][k]

    def populate_data(self, k, v):
        d = self.task.data_chain
        if k in d:
            logging.warning(f"key [ {k} ] occupied and overwritten!")
        d[k] = v

    def get_data_by_param_default_data(self, param, default_data_name):
        return self.get_data(self.get_param(param)) if self.has_param(param) else self.get_data(default_data_name)

    def get_data_by_param_default_param(self, param, default_param_name):
        return self.get_data(self.get_param(param)) if self.has_param(param) else self.expression2str(
            self.get_param(default_param_name))

    def get_data(self, k):
        return self._get_data(self.task.data_chain, k)

    def get_data_chain_str(self):
        return str(self.task.data_chain)

    def has_data(self, k):
        try:
            return k in self.task.data_chain
        except:
            return hasattr(self.task.data_chain, k)

    def del_data(self, k):
        if (self.has_data(k)):
            del self.task.data_chain[k]

    def _get_data(self, obj, k):
        result = obj
        try:
            return result[k]
        except:
            pass
        try:
            return getattr(result, k)
        except:
            pass

    def get_deep_data(self, keys):
        result: any = self.task.data_chain

        for key in keys:
            result = self._get_data(result, key)

        return result

    def expression2str(self, expression):
        if not expression is None and len(expression) > 0:
            return eval("f'" + expression + "'")

    def str2dict(self, str) -> dict:
        result = {}
        for kv in str.split(self.SEPARATOR):
            key0value1 = kv.split(self.ITEM_SEPARATOR)
            result[key0value1[0]] = key0value1[1]
        return result

    def str2list(self, str) -> list:
        return str.split(self.SEPARATOR)

    def decrypt(self, str):
        return Processor.decrypt_pwd(str)

    @staticmethod
    def encrypt_pwd(str) -> str:
        return cryptocode.encrypt(str, Processor.SALT)

    @staticmethod
    def decrypt_pwd(str):
        return cryptocode.decrypt(str, Processor.SALT)

    @staticmethod
    def get_processors():
        processors = OSUtils.get_file_list(os.path.realpath('core') + '/processors')
        result = list(
            map(
                lambda p: p.replace('Processor.py', ''),
                filter(lambda p: 'Processor.py' in p, processors)
            )
        )
        result.sort()
        return result

    @staticmethod
    def get_processor_by_type(prefix: str):
        class_name = prefix + 'Processor'
        module_name = 'core.processors.' + class_name
        module = __import__(module_name, fromlist=[module_name])
        processor: Processor = getattr(module, class_name)()
        return processor
