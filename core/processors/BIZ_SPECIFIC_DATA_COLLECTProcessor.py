import json
import logging

from core.processor import Processor
from utils.DateUtil import DateUtil


class BIZ_SPECIFIC_DATA_COLLECTProcessor(Processor):
    TPL: str = '{"json_filtered_data":"json_filtered_data","LandscapeExportSheet0":"", "LandscapeExportSheet1":"", "CustomerServerOverviewSheet0":"", "CustomerServerOverviewSheet1":"",  "data_key":"name on data_chain"}'
    DESC: str = f''' 
   
    customerServerOverview.xlsx  ---过滤掉K列(TIC Server Comment)：以CMS，CGS开头的行，S列(System Number)以DR开头的行之后，按照T列(System ID)分组，按E列(Server Name)执行命令获取azure数据
    
    LandscapeExport.xlsx ---对比的目标文件，按照M列(SID)分组，过滤T列(ServerType)=MASTER，AE列(StartDate)+AG列(Runtime)大于当前时间，X列(StorageGB)相加即为要比较的数值

        {TPL}

    '''

    def process(self):
        # System ID|Server Name|System Number|TIC Server Comment
        CustomerServerOverviewSheet0 = self.get_data(self.get_param('CustomerServerOverviewSheet0'))
        CustomerServerOverviewSheet1 = self.get_data(self.get_param('CustomerServerOverviewSheet1'))

        json_filtered_data = self.get_data(self.get_param('json_filtered_data'))

        # SID|ServerType|StartDate|Runtime|StorageGB
        LandscapeExportSheet0 = self.get_data(self.get_param('LandscapeExportSheet0'))
        LandscapeExportSheet1 = self.get_data(self.get_param('LandscapeExportSheet1'))

        filtered_CustomerServerOverviewSheet0 = list(
            filter(
                lambda row: not row[3].startswith('CMD') and not row[3].startswith('CGS'),
                CustomerServerOverviewSheet0)
        )

        filtered_LandscapeExportSheet0 = list(
            filter(
                lambda row: row[1] == 'MASTER' and DateUtil.is_after_now(
                    DateUtil.months_delta(DateUtil.get_date(row[2], "%Y-%m-%d"), float(row[3]))),
                LandscapeExportSheet0
            )
        )

        logging.info(json.dumps(json_filtered_data))

        filtered_LandscapeExportSheet0.insert(0, LandscapeExportSheet0[0])
        result = self.collect_result(json_filtered_data, filtered_CustomerServerOverviewSheet0,
                                     filtered_LandscapeExportSheet0)
        data = {
            "result": result,
            "CustomerServerOverviewSheet0": filtered_CustomerServerOverviewSheet0,
            "LandscapeExportSheet0": filtered_LandscapeExportSheet0
        }

        logging.info(json.dumps(data))

        self.populate_data(self.get_param('data_key'), data)

    def collect_result(self, json_filtered_data: [{}], filtered_CustomerServerOverviewSheet0,
                       filtered_LandscapeExportSheet0):
        # data from azure, after any changes of json-path, should review here
        data_from_azure = list(
            map(lambda record: {
                "name": record['name'],
                "vmSize": record['properties.hardwareProfile.vmSize'],
                "osDiskTotalGB": record['properties.storageProfile.osDisk.diskSizeGB'],
                "dataDiskTotalGB": sum(
                    list(map(lambda r: r['diskSizeGB'], record['properties.storageProfile.dataDisks']))),
                "azure_datadisk_details": record['properties.storageProfile.dataDisks']
            }, json_filtered_data)
        )

        logging.info(json.dumps(data_from_azure))

        return self.build_result(data_from_azure, filtered_CustomerServerOverviewSheet0, filtered_LandscapeExportSheet0)

    def build_result(self, data_from_azure, filtered_CustomerServerOverviewSheet0, filtered_LandscapeExportSheet0):
        final_result = [
            # excel first row as title row.
            ["Server Name",
             "AZURE_DataDiskSize",
             "DED_storageSize",
             "diff(AzureSize-20-DEDSize)",
             "Azure_details",
             "DED_details"]
        ]
        for azure_server in data_from_azure:
            ded_details = self.collect_ded_details(azure_server["name"], filtered_CustomerServerOverviewSheet0,
                                                   filtered_LandscapeExportSheet0)
            ded_storage_size = self.collect_ded_storage_size(ded_details)
            final_result.append([
                azure_server["name"],  # Server Name
                azure_server["dataDiskTotalGB"],  # AZURE_DataDiskSize
                ded_storage_size,  # DED_storageSize
                self.collect_diff(azure_server["dataDiskTotalGB"], ded_storage_size),  # diff(AzureSize-20-DEDSize)
                json.dumps(azure_server['azure_datadisk_details']),  # Azure_details
                json.dumps(ded_details)  # DED_details
            ])
        return final_result

    def collect_ded_details(self, server_name, filtered_CustomerServerOverviewSheet0, filtered_LandscapeExportSheet0):
        sids = list(map(
            lambda i: i[0], list(filter(
                lambda r: r[1] == server_name, filtered_CustomerServerOverviewSheet0)
            ))
        )
        # SID|ServerType|StartDate|Runtime|StorageGB|Database|Service|InstanceType
        return list(map(
            lambda i: {
                "SID": i[0],
                "ServerType": i[1],
                "StartDate": i[2],
                "Runtime": i[3],
                "StorageGB": i[4],
                "Database": i[5],
                "Service": i[6],
                "InstanceType": i[7]
            }, list(filter(
                lambda r: r[0] in sids, filtered_LandscapeExportSheet0))
        ))

    def collect_diff(self, azure_datadisk_totalGB, ded_storage_size):
        return azure_datadisk_totalGB - 20 - ded_storage_size

    def collect_ded_storage_size(self, ded_details):
        return sum(
            list(map(lambda r: float(r['StorageGB']), ded_details))
        )
