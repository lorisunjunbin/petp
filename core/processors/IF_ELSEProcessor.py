import logging

from core.processor import Processor
from utils.CodeExplainerUtil import CodeExplainerUtil


class IF_ELSEProcessor(Processor):
    TPL: str = '{"condition_fn":"return True", "then_tasks":"1", "else_tasks":"0"}'

    DESC: str = '''
        Conditional branching — skip "then" or "else" task blocks based on a condition.

        - condition_fn: Python function body receiving (data_chain), must return bool.
          True → execute then-block, skip else-block.
          False → skip then-block, execute else-block.
        - then_tasks: number of tasks immediately following this one that form the "then" block (default: 1)
        - else_tasks: number of tasks after the then-block that form the "else" block (default: 0)

        Example layout (IF_ELSE at task 3, then_tasks=2, else_tasks=1):
          Task 3: IF_ELSE
          Task 4: (then-block start)
          Task 5: (then-block end)
          Task 6: (else-block)
          Task 7: (continues regardless)

        Works inside loops: condition is re-evaluated each iteration; loop variables (loop_idx, loop_item) are accessible in condition_fn.

        Constraints:
          - then/else blocks must NOT span across loop boundaries (all tasks must stay within the same loop range)
          - Nesting IF_ELSE is NOT supported (inner IF_ELSE overwrites the skip range of the outer one)
          - Do NOT combine with GO_TO_TASK jumping into/out of then/else blocks
          - then_tasks + else_tasks count must be exact — miscounting will skip or execute wrong tasks
    '''

    def get_category(self) -> str:
        return super().CATE_GENERAL

    def process(self):
        super().process()

        condition_body = self.explain_param_or_default('condition_fn', 'return True')
        then_count = self.explain_param_as_int('then_tasks', 1)
        else_count = self.explain_param_as_int('else_tasks', 0)

        cond_fn = CodeExplainerUtil.create_and_execute_func(
            'IF_ELSE_condition_fn', '(data_chain)', condition_body)

        result = cond_fn(self.get_data_chain())
        current_seq = self.task.run_sequence

        if result:
            logging.info('IF_ELSE: condition TRUE, execute then-block (%d tasks), skip else-block (%d tasks)',
                         then_count, else_count)
            if else_count > 0:
                skip_start = current_seq + then_count + 1
                self.populate_data('__skip_range', (skip_start, skip_start + else_count - 1))
        else:
            logging.info('IF_ELSE: condition FALSE, skip then-block (%d tasks), execute else-block (%d tasks)',
                         then_count, else_count)
            if then_count > 0:
                skip_start = current_seq + 1
                self.populate_data('__skip_range', (skip_start, skip_start + then_count - 1))
