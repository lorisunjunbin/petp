import logging

from core.processor import Processor
from utils.CodeExplainerUtil import CodeExplainerUtil


class GO_TO_TASKProcessor(Processor):
    TPL: str = '{"target_task":"", "condition_fn":"return True"}'

    DESC: str = f'''
        Conditionally jump to a specific task within the current execution.
        When the condition evaluates to True, execution continues from the target task
        instead of the next sequential task. When False, execution proceeds normally.

        - target_task: 1-based task number to jump to (supports expression, required)
        - condition_fn: Python function body (data_chain); return True to jump,
          False to skip and continue normally (default: "return True")

        {TPL}
    '''

    def get_category(self) -> str:
        return super().CATE_GENERAL

    def process(self):
        super().process()

        if not self.has_param('target_task'):
            logging.warning('GO_TO_TASK: target_task is required but not provided, skipping jump')
            return

        target_str = self.expression2str(self.get_param('target_task')).strip()
        if not target_str or not target_str.lstrip('-').isdigit():
            logging.warning('GO_TO_TASK: target_task "%s" is not a valid integer, skipping jump', target_str)
            return

        target = int(target_str)
        condition_body = self.explain_param_or_default('condition_fn', 'return True')

        cond_fn = CodeExplainerUtil.create_and_execute_func(
            'GO_TO_TASK_condition_fn', '(data_chain)', condition_body)

        if cond_fn(self.get_data_chain()):
            logging.info('GO_TO_TASK: condition met, will jump to task %s', target)
            self.populate_data('__goto_task', target)
        else:
            logging.info('GO_TO_TASK: condition not met, continue normally')
