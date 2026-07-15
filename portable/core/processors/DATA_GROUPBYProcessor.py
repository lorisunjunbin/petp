import logging
from core.processor import Processor
from utils.CodeExplainerUtil import CodeExplainerUtil


class DATA_GROUPBYProcessor(Processor):
    TPL: str = '{"source_key":"", "group_by_func":"return row[0] ", "mapping_func":"return row","collect_func":"return key + str(rows)", "data_key":"dict_group_by"}'

    DESC: str = '''
        Group source_key by a key function, optionally map and collect the grouped results into a dict.

        - source_key: key of data_chain pointing to the input list
        - group_by_func: Python function body returning group key, variable "row" is available (default: "return row[0]")
        - mapping_func: Python function body to transform each row, variable "row" is available (default: "return row")
        - collect_func: Python function body to aggregate each group, variables "key" and "rows" are available (default: "return key + str(rows)")
        - data_key: key of data_chain to store the grouped dict result (default: "dict_group_by")
    '''

    def get_category(self) -> str:
        return super().CATE_DATA_PROCESSING

    def process(self):
        group_by_dict = {}

        given_collection = self.get_data(self.get_param('source_key'))
        group_by_func = self.get_param('group_by_func')
        mapping_func = self.get_param('mapping_func')
        collect_func = self.get_param('collect_func')
        target_dict_key = self.expression2str(self.get_param('data_key'))

        group_by_func = CodeExplainerUtil.create_and_execute_func('DATA_GROUPBYProcessor_group_by_func','(row, p)', group_by_func)
        mapping_func = CodeExplainerUtil.create_and_execute_func('DATA_GROUPBYProcessor_mapping_func', '(row, p)', mapping_func)
        collect_func = CodeExplainerUtil.create_and_execute_func('DATA_GROUPBYProcessor_collect_func', '(key, rows, p)', collect_func) if collect_func else None

        for rownum, row in enumerate(given_collection):
            group_by_key = group_by_func(row, self)
            mapping_func_result = mapping_func(row, self)

            if group_by_key not in group_by_dict:
                group_by_dict[group_by_key] = []

            group_by_dict[group_by_key].append(mapping_func_result)

        if collect_func:
            group_by_dict = {key : collect_func(key, rows, self) for key, rows in group_by_dict.items()}

        logging.debug(f'"{target_dict_key}" size: {len(group_by_dict)} : {str(group_by_dict)}')

        self.populate_data(target_dict_key, group_by_dict)