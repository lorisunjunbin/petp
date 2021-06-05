import json
import logging
import os
import time

import cryptocode

from core.task import Task
from utils.OSUtils import OSUtils
from utils.SeleniumUtil import SeleniumUtil

"""

TODO: 

    WEB_PERFORMANCE_TRACEProcessor
    
    ETC.Processor
    
"""

class Processor(object):
    SEPARATOR: str = ';'
    ITEMSEPARATOR: str = '='
    SALT:str = 'petpisawesome'

    TPL: str
    DESC: str = f''' 
        TODO: Explain the usage of current  processor 
        - overview
        - parameter explaination for  one by one
        - give example
    '''

    task: Task
    input_param: dict

    def process(self):
        # implemented in sub class
        pass

    def do_process(self):
        self.process()

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
    def get_ddir(self):
        return os.path.realpath('./download')

    def set_task(self, task: Task):
        self.task = task
        self.input_param = json.loads(self.task.input)

    def get_param(self, name):
        if self.has_param(name):
            return self.input_param[name]

    def has_param(self, name):

        return name in self.input_param and \
               (
                   len(self.input_param[name])> 0
                if type(self.input_param[name]) is str
                else not self.input_param[name] is None
                )

    def get_all_params(self):
        return self.input_param

    def populate_data(self, k, v):
        d = self.task.data_chain
        if k in d:
            logging.warning(f"key [ {k} ] occupied and overwritten!")
        d[k] = v

    def get_data_by_param_default_data(self, param, default_data_name):
        return self.get_data(self.get_param(param)) if self.has_param(param) else self.get_data(default_data_name)

    def get_data_by_param_default_param(self, param, default_param_name):
        return self.get_data(self.get_param(param)) if self.has_param(param) else self.expression2str(self.get_param(default_param_name))

    def get_data(self, k):
        return self._get_data(self.task.data_chain, k)

    def has_data(self, k):
        try:
            return k in self.task.data_chain
        except:
            return hasattr(self.task.data_chain, k)

    def del_data(self, k):
        if(self.has_data(k)):
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

    def get_element_by(self, chrome, by: str, identity: str, timeout=200):
        if by == 'id':
            return self.get_element_with_wait(chrome, id=identity, timeout=timeout)
        elif by == 'xpath':
            return self.get_element_with_wait(chrome, xpath=identity, timeout=timeout)
        elif by == 'link':
            return self.get_element_with_wait(chrome, link=identity, timeout=timeout)
        elif by == 'css':
            return self.get_element_with_wait(chrome, css=identity, timeout=timeout)
        else:
            raise Exception('unsupported by: ' + by)

    def get_element_with_wait(self, chrome, id=None, xpath=None, link=None, css=None, timeout=200):
        if not id == None:
            SeleniumUtil.wait_for_element_id_presence(chrome, id, timeout)
            ele = SeleniumUtil.find_element_by_id(chrome, id)
            SeleniumUtil.move_to_ele(chrome, ele)
            SeleniumUtil.wait_for_element_id_visible(chrome, id, timeout)
            return SeleniumUtil.find_element_by_id(chrome, id)

        if not xpath == None:
            SeleniumUtil.wait_for_element_xpath_presence(chrome, xpath, timeout)
            ele = SeleniumUtil.find_element_by_x_path(chrome, xpath)
            SeleniumUtil.move_to_ele(chrome, ele)
            SeleniumUtil.wait_for_element_xpath_visible(chrome, xpath, timeout)
            return SeleniumUtil.find_element_by_x_path(chrome, xpath)

        if not link == None:
            SeleniumUtil.wait_for_element_link_presence(chrome, link, timeout)
            ele = SeleniumUtil.find_element_by_link(chrome, link)
            SeleniumUtil.move_to_ele(chrome, ele)
            SeleniumUtil.wait_for_element_link_visible(chrome, link, timeout)
            return SeleniumUtil.find_element_by_link(chrome, link)

        if not css == None:
            SeleniumUtil.wait_for_element_css_presence(chrome, css, timeout)
            ele = SeleniumUtil.find_element_by_css(chrome, css)
            SeleniumUtil.move_to_ele(chrome, ele)
            SeleniumUtil.wait_for_element_css_visible(chrome, css, timeout)
            return SeleniumUtil.find_element_by_css(chrome, css)

    def expression2str(self, expression):
        if not expression is None and len(expression) > 0:
            return eval("f'" + expression + "'")

    def str2dict(self, str) -> dict:
        result = {}
        for kv in str.split(self.SEPARATOR):
            key0value1 = kv.split(self.ITEMSEPARATOR)
            result[key0value1[0]] = key0value1[1]
        return result

    def decrypt(self, str):
        return Processor.decrypt_pwd(str)

    @staticmethod
    def encrypt_pwd(str)->str:
        return cryptocode.encrypt(str, Processor.SALT)

    @staticmethod
    def decrypt_pwd(str):
        return cryptocode.decrypt(str, Processor.SALT)

    @staticmethod
    def get_processors():
        processors = OSUtils.get_file_list(os.path.realpath('core') + '/processors')
        result = list(map(lambda f: f.replace('Processor.py', ''), processors))
        result.sort()
        return result

    @staticmethod
    def get_processor_by_type(prefix: str):
        class_name = prefix + 'Processor'
        module_name = 'core.processors.' + class_name
        module = __import__(module_name, fromlist=[module_name])
        processor: Processor = getattr(module, class_name)()
        return processor
