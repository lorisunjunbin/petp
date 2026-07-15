import json
import logging
import os

from core.cron.runnableascron import RunnableAsCron
from core.definition.yamlro import YamlRO
from core.execution import Execution
from utils.AppPaths import get_pipelines_dir
from utils.DateUtil import DateUtil
from utils.OSUtils import OSUtils

from threading import Condition

"""
Pipeline 1-n Execution
"""


class Pipeline(RunnableAsCron):
    pipeline: str
    cronExp: str
    cronEnabled: bool
    cronDesc: str = ''
    list: list  # item of list: {execution:'', input:''}

    cond: Condition

    def __init__(self, pipeline, list, cronEnabled=False, cronExp='0 * * * *', cronDesc=''):

        self.pipeline = pipeline
        self.cronExp = cronExp
        self.cronEnabled = cronEnabled
        self.cronDesc = cronDesc
        self.list = list

    def run(self, initdata, view):
        self.cond = Condition()
        self._run(initdata, self.cond, view)

    def run_sync(self, initdata, view, cond):
        self._run(initdata, cond, view)

    def get_name(self):
        return self.pipeline

    def get_key(self):
        return f'{self.pipeline}_{self.cronExp}'

    def get_cron(self):
        return self.cronExp

    def _run(self, initdata, cond, view):

        data_chain = initdata | {'run_in_pipeline': 'yes'}
        total_steps = len(self.list)
        data_chain['__pipeline_context'] = {
            'pipeline_name': self.pipeline,
            'step_index': 0,
            'step_total': total_steps,
            'is_pipeline': True,
        }

        if 'running_as_cron' in initdata:
            logging.info(f'<<<<<<<<<<<<<<<<<<<<<-  Start RUN Pipeline (CRON): {self.pipeline}  [ {self.cronExp} ] {self.cronDesc} - >>>>>>>>>>>>>>>>>>>>>')
        else:
            logging.info(f'<<<<<<<<<<<<<<<<<<<<<-  Start RUN Pipeline: {self.pipeline} - >>>>>>>>>>>>>>>>>>>>>')

        self._post_pipeline_event(view, 'start', self.pipeline)

        for idx, executionDic in enumerate(self.list, start=1):
            execution: Execution = Execution.get_execution(executionDic['execution'])

            executionInitData: dict = self.load_proper_input(executionDic)

            mcp_defaults = execution.expand_mcp_defaults(data_chain)
            for k, v in mcp_defaults.items():
                if k not in data_chain and k not in executionInitData:
                    executionInitData[k] = v

            data_chain = data_chain | executionInitData
            data_chain['__pipeline_context'] = {
                'pipeline_name': self.pipeline,
                'step_index': idx - 1,
                'step_total': total_steps,
                'is_pipeline': True,
            }

            logging.info(
                f'[ {self.pipeline} ]>>{DateUtil.get_now_in_str("%Y-%m-%d %H:%M:%S")} >============> Execution {idx}: {execution.execution}')

            self._post_pipeline_event(view, 'step', self.pipeline, execution.execution, idx - 1)

            try:
                data_chain = execution.run(data_chain, cond, view)
            except Exception as e:
                logging.error(f'[ {self.pipeline} ] Execution {idx}: {execution.execution} FAILED: {e}')
                self._post_pipeline_event(view, 'error', self.pipeline, execution.execution, idx - 1)
                raise

            logging.info(
                f'[ {self.pipeline} ]<<{DateUtil.get_now_in_str("%Y-%m-%d %H:%M:%S")} <============< Execution {idx}: {execution.execution} < DONE \n')

        logging.info(f'<<<<<<<<<<<<<<<<<<<<<-  Successfully RUN Pipeline: {self.pipeline} - >>>>>>>>>>>>>>>>>>>>>')

        self._post_pipeline_event(view, 'done', self.pipeline)

    @staticmethod
    def _post_pipeline_event(view, action, *args):
        if view is None:
            return
        try:
            from mvp.presenter.event.PETPEvent import PETPEvent
            import wx
            wx.PostEvent(view, PETPEvent(PETPEvent.PIPELINE_STEP, [action, *args]))
        except Exception:
            pass

    def load_proper_input(self, executionDic):
        if not (executionDic.get('input') or '').strip():
            return {}
        try:
            result = json.loads(executionDic['input'])
            if type(result) is dict:
                return result
            logging.warning(
                f"invalid input {executionDic['input']} for execution: {executionDic['execution']}, will return empty dict.")
            return {}
        except:
            logging.warning(
                f"invalid input {executionDic['input']} for execution: {executionDic['execution']}, will return empty dict.")
            return {}

    def _get_file_path(self):
        return os.path.join(get_pipelines_dir(), f'{self.pipeline}.yaml')

    def delete(self):
        fp = self._get_file_path()
        trash_dir = os.path.join(get_pipelines_dir(), 'trash')
        os.makedirs(trash_dir, exist_ok=True)
        OSUtils.copy2(fp, trash_dir)
        OSUtils.delete_file_if_existed(fp)

    def save(self):
        if (len(self.list) > 0):
            YamlRO.write(self._get_file_path(), self)
            logging.info('Successfully save cron -> ' + self._get_file_path())

    def __str__(self):
        return str(self.__dict__)

    @staticmethod
    def get_pipeline(filename):
        file_absolute_path = os.path.join(get_pipelines_dir(), f'{filename}.yaml')
        if OSUtils.is_file_existed(file_absolute_path):
            # logging.info(f'Load pipeline from {file_absolute_path}')
            return YamlRO.get_yaml_from_file(file_absolute_path)
        else:
            logging.warning(f'File not existed: {file_absolute_path}')
            return None

    @staticmethod
    def get_available_pipelines():
        pipelines = OSUtils.get_file_list(get_pipelines_dir())
        result = list(map(lambda f: f.replace('.yaml', ''), pipelines))
        result.sort()

        return result
