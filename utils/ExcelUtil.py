import os
import csv
from openpyxl import Workbook
from openpyxl import load_workbook
import wx
import wx.dataview
import wx.lib.colourutils

import subprocess
import logging

from openpyxl.worksheet._read_only import ReadOnlyWorksheet
from openpyxl.worksheet.worksheet import Worksheet

from utils.DateUtil import DateUtil


class ExcelUtil:
    @staticmethod
    def filter_by_fields(fields: [str] = [], data: [[]] = []):
        """
        1, find all matched column index from data[0] associated with fields
        2, collect matched columns into new data_filtered, then return

        """
        # figure out which columns should be kept
        first_row = data[0]
        column_idx = ExcelUtil.find_column_index_arr_via_fields(first_row, fields)

        logging.info('fields:' + str(fields) + ' @column: ' + str(column_idx))

        # construct new data in [[]]
        data_filtered: [[]] = []
        for row_idx, row in enumerate(data):
            new_row: [] = []
            for col_idx in column_idx:
                new_row.append(row[col_idx])

            data_filtered.append(new_row)

        return data_filtered

    @staticmethod
    def find_column_index_arr_via_fields(first_row: [], fields: [str] = []):
        column_idx: [int] = []
        for f_idx, field in enumerate(fields):
            for c_idx, cell in enumerate(first_row):
                if field == cell:
                    column_idx.append(c_idx)
        return column_idx

    @staticmethod
    def get_data_from_csv(csvFilePath, skipFirst=False, dlr='\t'):
        result = []
        with open(csvFilePath, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=dlr)
            rowNum = 0
            for row in reader:
                rowNum += 1
                if skipFirst and rowNum == 1:
                    continue
                result.append(row)
        logging.info(f'get_data_from_csv file: {csvFilePath}, data: {str(result)}')
        return result

    @staticmethod
    def convert_csv_to_xlsx(csvFilePath, xlsxFilePath, dlr='\t'):
        wb = Workbook()
        ws = wb.active

        with open(csvFilePath, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=dlr)
            for row in reader:
                ws.append(row)

        wb.save(xlsxFilePath)
        logging.info(f'convert_csv_to_xlsx save file to: {xlsxFilePath}')

    @staticmethod
    def write_dict_to_excel(full_file_path: str, data_as_dict: dict[str:[]]):
        if len(data_as_dict) == 0:
            logging.info(f'not data to write: {full_file_path}')
            return

        wb = Workbook()
        # remove the default active sheet.
        wb.remove(wb.active)

        for k, v in data_as_dict.items():
            sheet: Worksheet = wb.create_sheet(k)
            for row in v:
                sheet.append(row)
        # save to target file
        wb.save(full_file_path)

    @staticmethod
    def get_data_from_excel_file(fileName, startAtRow=0, endAtColumn=50, sheet_index=0):
        result = []
        wb = load_workbook(filename=fileName, read_only=True, data_only=True)
        ws = wb.worksheets[sheet_index]
        for idx_row, row in enumerate(ws.rows):
            if idx_row >= startAtRow:
                isEnd = False
                cells = []

                for idx_cell, cell in enumerate(row):
                    if (idx_cell == endAtColumn):
                        break

                    if idx_cell == 0 and cell.value is None:
                        isEnd = True
                        cells = []
                        break
                    else:
                        if cell.value is None:
                            cells.append('')
                        else:
                            cells.append(str(cell.value))

                if isEnd == True:
                    break
                else:
                    if (len(cells) > 0):
                        result.append(cells)

        logging.info(f'get_data_from_excel_file load {len(result)} records from file: {fileName} ')

        return result

    @staticmethod
    def get_data_from_excel_file_by_fields(fileName, sheet_index=0, startAtRow=0, fields=[]):
        result = []
        wb = load_workbook(filename=fileName, read_only=True)
        ws: ReadOnlyWorksheet = wb.worksheets[sheet_index]
        logging.info(f'type is: {type(ws)}')
        column_indexes = ExcelUtil.find_column_index_arr_via_fields(ExcelUtil.get_first_row(ws), fields)

        for row in ws.iter_rows(min_row=startAtRow + 1, max_row=ws.max_row):
            cells = []

            if len(column_indexes) > 0:
                for c_idx in column_indexes:
                    if row[c_idx] is not None:
                        cells.append(str(row[c_idx].value))
                    else:
                        cells.append('')

                if (len(cells) > 0):
                    result.append(cells)
            else:
                break

        logging.info(f'get_data_from_excel_file_by_fields load {len(result)} records from file: {fileName} ')

        return result

    @staticmethod
    def get_first_row(work_sheet):
        first_row = []
        cur_row = 1
        for row in work_sheet.iter_rows(min_row=1, max_row=1, values_only=True):
            for cell in row:
                first_row.append(str(cell))
            break
        return first_row

    @staticmethod
    def generate_file(fullFilePath, data=[], anyway=True):
        count = len(data)
        if count > 0 or anyway:
            wb = Workbook()
            ws = wb.active
            for idx, rowData in enumerate(data):
                ws.append(rowData)
            wb.save(fullFilePath)

    @staticmethod
    def generate_target_files(data, name, finalRow, folder_output):
        count = len(data)

        if count > 0:

            data.append(finalRow)
            fileName = name + DateUtil.get_now_in_str() + ".xlsx"
            fullFilePath = folder_output + os.path.sep + fileName

            ExcelUtil.generate_file(fullFilePath, data)

            logging.info('generate excel file:' + fullFilePath)

            ExcelUtil.open_specific_file(fullFilePath, name)

        else:
            logging.info('generate excel file sikped, given data is empty, for name: ' + name)

    @staticmethod
    def open_specific_file(fullFilePath, name):
        dlg = wx.MessageDialog(None, "结果文件输出：" + fullFilePath
                               + "\n是否打开文件 ？", name, wx.YES_NO | wx.ICON_QUESTION)

        if dlg.ShowModal() == wx.ID_YES:
            subprocess.call(["open", fullFilePath])
        dlg.Destroy()

    @staticmethod
    def open_specific_file_directly(fullFilePath):
        subprocess.call(["open", fullFilePath])

    @staticmethod
    def init_folders(file_folder, output_folder):
        ExcelUtil.create_folder_if_not_existed(file_folder)
        ExcelUtil.create_folder_if_not_existed(output_folder)

    @staticmethod
    def create_folder_if_not_existed(filePath):
        if not os.path.exists(filePath):
            os.makedirs(filePath)

    @staticmethod
    def get_log_file_path(app):
        return os.path.realpath('log') + "/" + app + ".log"

    @staticmethod
    def get_email_template_path(fileName):
        return "file://" + os.path.realpath('email_template') + fileName
