import os
import csv
from openpyxl import Workbook
from openpyxl import load_workbook
import wx
import wx.dataview
import wx.lib.colourutils

import subprocess
import logging

from utils.DateUtil import DateUtil


class ExcelUtil:

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

        with open(csvFilePath, 'r', newline='', encoding='utf-16') as f:
            reader = csv.reader(f, delimiter=dlr)
            for row in reader:
                ws.append(row)

        wb.save(xlsxFilePath)
        logging.info(f'convert_csv_to_xlsx save file to: {xlsxFilePath}')

    @staticmethod
    def get_data_from_excel_file(fileName, startAtRow=0, endAtColumn=50):
        result = []
        wb = load_workbook(filename=fileName, read_only=True)
        ws = wb.worksheets[0]
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


if __name__ == '__main__':
    pass
    # print(ExcelUtil.get_email_template_path())
    # print(ExcelUtil.get_data_from_excel_file(
    #     '/Users/i335607/LoriProject/PycharmProjects/RSDAssistant/folder_file_bak/export_CW33.xlsx', 1, 12))
