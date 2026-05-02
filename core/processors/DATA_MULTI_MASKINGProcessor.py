import logging
from core.processor import Processor
from utils.CodeExplainerUtil import CodeExplainerUtil


class DATA_MULTI_MASKINGProcessor(Processor):
    TPL: str = '{"source_key":"", "content_clean_func":"return content", "masking_func":"return \'SJB-\' + str(colnum) + str(rownum) ", "masking_columns":"0|>1|>2|>3", "masking_dict_name":"", "masking_dict_inverted":"Yes"}'

    DESC: str = f'''
        Perform multi-column data masking on a collection (list of rows). Unlike the single-column
        DATA_MASKINGProcessor, this processor supports masking multiple columns at once. Each specified
        column is cleaned and replaced with a masked value. Per-column masking dictionaries are
        maintained so that identical original values always map to the same masked value.

        The masking_func has access to: mask_dict, row, rownum, colnum.
        The content_clean_func has access to: content (the raw cell value).

        - source_key: Key in data_chain for the input list of rows to mask (supports expression, default: "")
        - content_clean_func: Python function body to clean/normalize cell content before masking; takes (content) (supports expression, default: "return content")
        - masking_func: Python function body to generate a masked replacement value; takes (mask_dict, row, rownum, colnum) (supports expression, default: "return 'SJB-' + str(colnum) + str(rownum)")
        - masking_columns: Pipe-separated list of zero-based column indices to mask (supports expression, default: "0|>1|>2|>3")
        - masking_dict_name: Key in data_chain to store the masking dictionary after processing; if empty, the dict is discarded (supports expression, default: "")
        - masking_dict_inverted: If "Yes" or "yes", stores the inverted mapping (masked -> original) instead of (original -> masked) (supports expression, default: "Yes")

        {TPL}

    '''

    def get_category(self) -> str:
        return super().CATE_DATA_PROCESSING

    def process(self):
        masking_dict = {}

        given_collection = self.get_data(self.get_param('source_key'))
        masking_dict_inverted = True if "yes" == str(self.get_param('masking_dict_inverted')).lower() else False
        masking_dict_name = self.get_param('masking_dict_name')
        masking_func_body = self.get_param('masking_func')
        content_clean_func = self.get_param('content_clean_func')
        masking_columns = self.get_param('masking_columns').split(self.SEPARATOR)

        masking_func = CodeExplainerUtil.create_and_execute_func('DATA_MULTI_MASKINGProcessor_masking',
                                                                 '(masking_dict, row, rownum, colnum)',
                                                                 masking_func_body)

        content_clean_func = CodeExplainerUtil.create_and_execute_func('DATA_MULTI_MASKINGProcessor_clean',
                                                                       '(content)',
                                                                       content_clean_func)

        for rownum, row in enumerate(given_collection):

            for masking_columnnum_str in masking_columns:

                masking_columnnum = int(masking_columnnum_str)

                masking_column_content = content_clean_func(row[masking_columnnum])

                if (masking_columnnum_str not in masking_dict):
                    masking_dict[masking_columnnum_str] = {}

                if masking_column_content not in masking_dict[masking_columnnum_str]:
                    masking_dict[masking_columnnum_str][masking_column_content] = masking_func(
                        masking_dict[masking_columnnum_str], row, rownum, masking_columnnum)

                    logging.debug(
                        '"%s" -> %s', masking_column_content, str(masking_dict[masking_columnnum_str][masking_column_content]))

                row[masking_columnnum] = masking_dict[masking_columnnum_str][masking_column_content]

        total_unique = sum(len(v) for v in masking_dict.values())
        logging.info('Masking complete: %d columns, %d unique values masked', len(masking_columns), total_unique)

        if masking_dict_name:
            if masking_dict_inverted:
                masking_dict = {k: {iv: ik for ik, iv in v.items()}
                                for k, v in masking_dict.items()}
            self.populate_data(masking_dict_name, masking_dict)
        else:
            masking_dict.clear()
