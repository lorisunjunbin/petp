import logging

from core.processor import Processor
from utils.DateUtil import DateUtil


class BIZ_SPECIFIC_DATA_COLLECTProcessor(Processor):
    TPL: str = '{"LandscapeExportSheet0":"", "LandscapeExportSheet1":"", "CustomerServerOverviewSheet0":"", "CustomerServerOverviewSheet1":"",  "data_key":"name on data_chain"}'
    DESC: str = f''' 
   
    customerServerOverview.xlsx  ---过滤掉K列(TIC Server Comment)：以CMS，CGS开头的行，S列(System Number)以DR开头的行之后，按照T列(System ID)分组，按E列(Server Name)执行命令获取azure数据
    
    LandscapeExport.xlsx ---对比的目标文件，按照M列(SID)分组，过滤T列(ServerType)=MASTER，AE列(StartDate)+AG列(Runtime)大于当前时间，X列(StorageGB)相加即为要比较的数值

        {TPL}

    '''

    def process(self):
        # System ID|Server Name|System Number|TIC Server Comment
        CustomerServerOverviewSheet0 = self.get_data(self.get_param('CustomerServerOverviewSheet0'))
        CustomerServerOverviewSheet1 = self.get_data(self.get_param('CustomerServerOverviewSheet1'))

        # SID|ServerType|StartDate|Runtime|StorageGB
        LandscapeExportSheet0 = self.get_data(self.get_param('LandscapeExportSheet0'))
        LandscapeExportSheet1 = self.get_data(self.get_param('LandscapeExportSheet1'))

        filtered_CustomerServerOverviewSheet0 = list(
            filter(
                lambda row: not row[3].startswith('CMD') and not row[3].startswith('CGS') and row[2].startswith('DR'),
                CustomerServerOverviewSheet0)
        )

        filtered_LandscapeExportSheet0 = list(
            filter(
                lambda row: row[1] == 'MASTER' and DateUtil.is_after_now(
                    DateUtil.months_delta(DateUtil.get_date(row[2], "%Y-%m-%d"), float(row[3]))),
                LandscapeExportSheet0
            )
        )

        data = {
            "filtered_CustomerServerOverviewSheet0": filtered_CustomerServerOverviewSheet0,
            "filtered_LandscapeExportSheet0": filtered_LandscapeExportSheet0
        }

        logging.info(str(data))

        self.populate_data(self.get_param('data_key'), data)
