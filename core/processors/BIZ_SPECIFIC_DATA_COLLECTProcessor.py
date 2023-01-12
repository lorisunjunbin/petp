import json
import logging

from core.processor import Processor
from utils.DateUtil import DateUtil


class BIZ_SPECIFIC_DATA_COLLECTProcessor(Processor):
    TPL: str = '{"json_filtered_data_netapp":"json_filtered_data_netapp","json_filtered_data":"json_filtered_data","LandscapeExportSheet0":"", "CustomerServerOverviewSheet0":"", "data_key":"name on data_chain"}'

    DESC: str = f''' 
   
    MAPPING - customerServerOverview.xlsx  ---过滤掉K列(TIC Server Comment)：以CMS，CGS开头的行，S列(System Number)以DR开头的行之后，按照T列(System ID)分组，按E列(Server Name)执行命令获取azure数据
    
    DED - LandscapeExport.xlsx ---对比的目标文件，按照M列(SID)分组，过滤T列(ServerType)=MASTER，AE列(StartDate)+AG列(Runtime)大于当前时间，X列(StorageGB)相加即为要比较的数值
    
    1， 数据加载，筛选，校验，
    2， 异常数据收集
    3， 磁盘资源 比对结果报告生成
    
        {TPL}

    '''

    #  DR 开头要过 去区分开；
    #  第一步DED校验逻辑：U列InstanceType为空且Service 不包含 NO SERVER
    def process(self):
        json_filtered_data = self.get_data(self.get_param('json_filtered_data'))
        json_filtered_data_netapp = self.get_data(self.get_param('json_filtered_data_netapp'))

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
        result, exception = self.collect_result_and_exception(json_filtered_data_netapp, json_filtered_data,
                                                              filtered_CustomerServerOverviewSheet0,
                                                              filtered_LandscapeExportSheet0)
        data = {
            "RESULT": result,
            "Exception": exception,
            "CustomerServerOverview": filtered_CustomerServerOverviewSheet0,
            "LandscapeExport": filtered_LandscapeExportSheet0,
        }

        self.populate_data(self.get_param('data_key'), data)

    def collect_result_and_exception(self, json_filtered_data_netapp: [{}], json_filtered_data: [{}],
                                     filtered_CustomerServerOverviewSheet0,
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

        return self.build_result(json_filtered_data_netapp, data_from_azure, filtered_CustomerServerOverviewSheet0,
                                 filtered_LandscapeExportSheet0)

    def build_result(self, json_filtered_data_netapp, data_from_azure, filtered_CustomerServerOverviewSheet0,
                     filtered_LandscapeExportSheet0):
        # SID, hana-none-hana, servername, az dis, ded disk, details.
        final_result = [
            # excel first row as title row.
            [
                "SID",
                "TYPE",
                "DR or NOT",
                "NetAppVolumeQuota",
                "AZURE_DataDiskSize",
                "DED_storageSize",
                "diff(VolumeQuota+AzureSize-20-DEDSize)",
                "Server Name(s)",
                # "DED_details",
                # "Azure_details"
            ]
        ]
        # filtered_CustomerServerOverviewSheet0:
        # ['System ID', 'Server Name', 'System Number', 'TIC Server Comment']
        # ['VD1', 'hec44v023219', '000000000500239629', 'HIL VD1 FTP  |B1_0304137835-4309806-HSO.000191-16-982_PROCESS_ID:53911958']

        cso_SystemID_2_records = self.group_by(
            lambda r: r[0] + ("|DR" if r[2].startswith("DR_") else "|Normal"),
            filtered_CustomerServerOverviewSheet0)

        # filtered_LandscapeExportSheet0
        # ['SID', 'ServerType', 'StartDate', 'Runtime', 'StorageGB', 'Database', 'Service', 'InstanceType', 'DB SID (HANA)', 'SystemNumber']
        # ['D79', 'MASTER', '2021-09-30', '60.000000', '1049.000000', 'HANA', 'HANA-Virtual-256GiB-AZURE, Linux(M32ls)', 'DB|DB01|', 'D89', '000000000500227006']

        le_SID_2_records = self.group_by(
            lambda r: (r[8] + '|HANA|' + r[0] if r[6].startswith("HANA-") else r[0] + "|NoneHANA|-")
                      + ("|DR" if r[9].startswith("DR_") else "|Normal"),
            filtered_LandscapeExportSheet0)

        final_exception: [[]] = self.collect_exception(le_SID_2_records, cso_SystemID_2_records)

        duplicated_records = self.find_duplicated_records(le_SID_2_records, cso_SystemID_2_records)

        for sid_type in sorted(le_SID_2_records.keys()):
            sid0type1Id2DRorNot3 = sid_type.split(self.SEPARATOR)
            sid = sid0type1Id2DRorNot3[0]
            drornot = sid0type1Id2DRorNot3[3]

            le_records = le_SID_2_records[sid_type]
            cso_key = self.SEPARATOR.join([sid, drornot])
            cso_records = cso_SystemID_2_records[cso_key] if cso_key in cso_SystemID_2_records else []

            duplicated_server_names = duplicated_records[sid] if sid in duplicated_records else []

            server_names = list(set(list(map(lambda r: r[1], cso_records))))

            filtered_server_names = list(filter(lambda r: not r in duplicated_server_names, server_names))

            azure_servers = list(filter(lambda r: r['name'] in filtered_server_names, data_from_azure))
            azure_storage_size = sum(list(map(lambda r: float(r['dataDiskTotalGB']), azure_servers)))
            ded_details = self.collect_ded_details(le_records)

            ded_storage_size = self.collect_ded_storage_size(ded_details)
            netapp_volume_quota = self.find_quota(sid0type1Id2DRorNot3[0], json_filtered_data_netapp)

            final_result.append([
                sid,  # SID
                sid0type1Id2DRorNot3[1],  # TYPE
                drornot,  # DR OR not
                netapp_volume_quota,  # NetAppVolumnQuta
                azure_storage_size,  # AZURE_DataDiskSize
                ded_storage_size,  # DED_storageSize
                self.collect_diff(netapp_volume_quota, azure_storage_size, ded_storage_size),
                # diff(AzureSize-20-DEDSize)
                self.SEPARATOR.join(server_names),  # Server Names

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

    def collect_diff(self, netapp_volume_quota, azure_datadisk_totalGB, ded_storage_size):
        return netapp_volume_quota + azure_datadisk_totalGB - 20 - ded_storage_size

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
        le_keys = le_SID_2_records.keys()
        for sid_drornot in sorted(cso_SystemID_2_records.keys()):
            sid0DRorNot1 = sid_drornot.split(self.SEPARATOR)
            found = list(filter(lambda k: str(sid0DRorNot1[0]) in k, le_keys))
            if (len(found)) == 0:
                exception_entites[sid_drornot] = cso_SystemID_2_records[sid_drornot]

        result = [["SID", "DRorNOT", "Records in CustomerOverview NotIn Landscape"]]

        for sid_drornot in exception_entites.keys():
            sid0DRorNot1 = sid_drornot.split(self.SEPARATOR)
            result.append([
                sid0DRorNot1[0],
                sid0DRorNot1[1],
                json.dumps(exception_entites[sid_drornot])
            ])

        return result

    def find_quota(self, sid, json_filtered_data_netapp):
        found = list(filter(lambda r: sid in r['name'], json_filtered_data_netapp))
        if len(found) > 0:
            return int(found[0]['usageThreshold']) / 1024 / 1024 / 1024
        return 0

    def find_duplicated_records(self, le_SID_2_records, cso_SystemID_2_records):
        result = {}
        for sid_drornot in cso_SystemID_2_records.keys():
            cso_sid0drornot1 = sid_drornot.split(self.SEPARATOR)

            cso_sid = cso_sid0drornot1[0]

            for sid_type_rid_drornot in le_SID_2_records.keys():
                le_sid0type1rid2dronot3 = sid_type_rid_drornot.split(self.SEPARATOR)

                le_sid = le_sid0type1rid2dronot3[0]
                le_type = le_sid0type1rid2dronot3[1]
                le_rid = le_sid0type1rid2dronot3[2]

                if cso_sid == le_sid and 'HANA' == le_type:
                    if not le_rid in result:
                        result[le_rid] = []
                        for row in cso_SystemID_2_records[sid_drornot]:
                            result[le_rid].append(row[1])
        return result
