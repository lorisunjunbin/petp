import json
import logging

from core.processor import Processor
from utils.DateUtil import DateUtil


class BIZ_SPECIFIC_DATA_COLLECTProcessor(Processor):
    TPL: str = '{"json_filtered_data":"json_filtered_data","LandscapeExportSheet0":"", "CustomerServerOverviewSheet0":"", "data_key":"name on data_chain"}'

    DESC: str = f''' 
   
    MAPPING - customerServerOverview.xlsx  ---过滤掉K列(TIC Server Comment)：以CMS，CGS开头的行，S列(System Number)以DR开头的行之后，按照T列(System ID)分组，按E列(Server Name)执行命令获取azure数据
    
    DED - LandscapeExport.xlsx ---对比的目标文件，按照M列(SID)分组，过滤T列(ServerType)=MASTER，AE列(StartDate)+AG列(Runtime)大于当前时间，X列(StorageGB)相加即为要比较的数值

        {TPL}

    '''

    #  DR 开头要过 去区分开；
    #  第一步DED校验逻辑：U列InstanceType为空且Service 不包含 NO SERVER
    def process(self):
        json_filtered_data = self.get_data(self.get_param('json_filtered_data'))

        # System ID|Server Name|System Number|TIC Server Comment
        CustomerServerOverviewSheet0 = self.get_data(self.get_param('CustomerServerOverviewSheet0'))

        # SID|ServerType|StartDate|Runtime|StorageGB|Database|Service|InstanceType|DB SID (HANA)|SystemNumber
        LandscapeExportSheet0 = self.get_data(self.get_param('LandscapeExportSheet0'))

        filtered_CustomerServerOverviewSheet0 = list(
            filter(
                lambda row: not row[3].startswith('CMS') and not row[3].startswith('CGS'),
                CustomerServerOverviewSheet0
            )
        )

        filtered_LandscapeExportSheet0 = list(
            filter(
                lambda row: (row[1] == 'MASTER' or row[1] == 'STANDBY') and DateUtil.is_after_now(
                    DateUtil.months_delta(DateUtil.get_date(row[2], "%Y-%m-%d"), float(row[3]))
                ),
                LandscapeExportSheet0
            )
        )

        # 第一步DED校验逻辑：U列InstanceType为空且Service 不包含 NO SERVER 程序停止并抛错
        self.validate(filtered_LandscapeExportSheet0)

        filtered_LandscapeExportSheet0.insert(0, LandscapeExportSheet0[0])
        result, exception = self.collect_result_and_exception(json_filtered_data, filtered_CustomerServerOverviewSheet0,
                                                              filtered_LandscapeExportSheet0)
        data = {
            "RESULT": result,
            "Exception": exception,
            "CustomerServerOverview": filtered_CustomerServerOverviewSheet0,
            "LandscapeExport": filtered_LandscapeExportSheet0,
        }

        self.populate_data(self.get_param('data_key'), data)

    def collect_result_and_exception(self, json_filtered_data: [{}], filtered_CustomerServerOverviewSheet0,
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

        return self.build_result(data_from_azure, filtered_CustomerServerOverviewSheet0, filtered_LandscapeExportSheet0)

    def build_result(self, data_from_azure, filtered_CustomerServerOverviewSheet0, filtered_LandscapeExportSheet0):
        # SID, hana-none-hana, servername, az dis, ded disk, details.
        final_result = [
            # excel first row as title row.
            [
                "SID",
                "TYPE",
                "DR or NOT",
                "Server Name(s)",
                "AZURE_DataDiskSize",
                "DED_storageSize",
                "diff(AzureSize-20-DEDSize)",
                # "DED_details",
                # "Azure_details"
            ]
        ]
        # filtered_CustomerServerOverviewSheet0:
        # ['System ID', 'Server Name', 'System Number', 'TIC Server Comment']
        # ['VD1', 'hec44v023219', '000000000500239629', 'HIL VD1 FTP  |B1_0304137835-4309806-HSO.000191-16-982_PROCESS_ID:53911958']

        cso_SystemID_2_records = self.group_by(
            lambda r: r[0]
                      + ('|HANA' if "DB DB" in r[3] else "|NoneHANA")
                      + ("|DR" if r[2].startswith("DR_") else "|Normal"),
            filtered_CustomerServerOverviewSheet0)

        # filtered_LandscapeExportSheet0
        # ['SID', 'ServerType', 'StartDate', 'Runtime', 'StorageGB', 'Database', 'Service', 'InstanceType', 'DB SID (HANA)', 'SystemNumber']
        # ['D79', 'MASTER', '2021-09-30', '60.000000', '1049.000000', 'HANA', 'HANA-Virtual-256GiB-AZURE, Linux(M32ls)', 'DB|DB01|', 'D89', '000000000500227006']

        le_SID_2_records = self.group_by(lambda r: r[0]
                                                   + ('|HANA' if 'DB' in r[7] else "|NoneHANA")
                                                   + ("|DR" if r[9].startswith("DR_") else "|Normal"),
                                         filtered_LandscapeExportSheet0)

        final_exception: [[]] = self.collect_exception(le_SID_2_records, cso_SystemID_2_records)

        for sid_type in sorted(le_SID_2_records.keys()):
            sid0type1DRorNot2 = sid_type.split(self.SEPARATOR)

            le_records = le_SID_2_records[sid_type]
            cso_records = cso_SystemID_2_records[sid_type] if sid_type in cso_SystemID_2_records else []

            server_names = list(set(list(map(lambda r: r[1], cso_records))))

            azure_servers = list(filter(lambda r: r['name'] in server_names, data_from_azure))
            azure_storage_size = sum(list(map(lambda r: float(r['dataDiskTotalGB']), azure_servers)))
            ded_details = self.collect_ded_details(le_records)

            ded_storage_size = self.collect_ded_storage_size(ded_details)

            final_result.append([
                sid0type1DRorNot2[0],  # SID
                sid0type1DRorNot2[1],  # TYPE
                sid0type1DRorNot2[2],  # DR OR not
                self.SEPARATOR.join(server_names),  # Server Names
                azure_storage_size,  # AZURE_DataDiskSize
                ded_storage_size,  # DED_storageSize
                self.collect_diff(azure_storage_size, ded_storage_size),  # diff(AzureSize-20-DEDSize)
                # json.dumps(ded_details),  # DED_details
                # json.dumps(azure_servers)  # Azure_details
            ])

        return final_result, final_exception

    def group_by(self, fn, given: [] = [], skip_first: bool = True):
        result: dict[str:[]] = {}
        for idx, row in enumerate(given):
            if idx == 0 and skip_first:
                continue
            key = fn(row)
            if not key in result:
                result[key] = []
            result[key].append(row)
        return result

    def collect_ded_details(self, filtered_LandscapeExportSheet0):

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
            }, filtered_LandscapeExportSheet0
        ))

    def collect_diff(self, azure_datadisk_totalGB, ded_storage_size):
        return azure_datadisk_totalGB - 20 - ded_storage_size

    def collect_ded_storage_size(self, ded_details):
        return sum(
            list(map(lambda r: float(r['StorageGB']), ded_details))
        )

    def validate(self, filtered_LandscapeExportSheet0):
        # #  第一步DED校验逻辑：U列InstanceType为空且Service 不包含 NO SERVER
        # SID|ServerType|StartDate|Runtime|StorageGB|Database|Service|InstanceType|DB SID (HANA)|SystemNumber
        found = list(filter(
            lambda r: (r[7] is None or len(r[7]) == 0) and (not "NO SERVER" in r[6])
            , filtered_LandscapeExportSheet0
        ))

        if len(found) > 0:
            err_msg = " 和同数据待完善, 原因：InstanceType为空, 且Service 不包含 NO SERVER "
            logging.error(err_msg)
            raise ValueError(err_msg)

    def collect_exception(self, le_SID_2_records, cso_SystemID_2_records):
        """
        :param le_SID_2_records:
        :param cso_SystemID_2_records:
        :return: the entities which are in customer overview, but not in landscape
        """
        exception_entites = {}
        for sid_type_drornot in sorted(cso_SystemID_2_records.keys()):
            if not sid_type_drornot in le_SID_2_records:
                exception_entites[sid_type_drornot] = cso_SystemID_2_records[sid_type_drornot]

        result = [["SID", "TYPE", "DRorNOT", "Records in CustomerOverview NotIn Landscape"]]

        for sid_type_drornot in exception_entites.keys():
            sid0type1DRorNot2 = sid_type_drornot.split(self.SEPARATOR)
            result.append([
                sid0type1DRorNot2[0],
                sid0type1DRorNot2[1],
                sid0type1DRorNot2[2],
                json.dumps(exception_entites[sid_type_drornot])
            ])

        return result
