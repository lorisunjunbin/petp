import json
import logging

from core.processor import Processor
from utils.DateUtil import DateUtil


class BIZ_SPECIFIC_DATA_COLLECTProcessor(Processor):
    TPL: str = '{"json_filtered_data_netapp_dr":"json_filtered_data_netapp_dr","json_filtered_data_netapp":"json_filtered_data_netapp","json_filtered_data_vm":"json_filtered_data_vm", "json_filtered_data_vm_dr":"json_filtered_data_vm_dr", "LandscapeExportSheet0":"", "CustomerServerOverviewSheet0":"", "data_key":"name on data_chain"}'

    DESC: str = f''' 

        非通用处理器，特殊业务   

        {TPL}

    '''

    def process(self):
        # 将vmdata 中normal和dr分开 2.23
        json_filtered_data_vm = self.get_data(self.get_param('json_filtered_data_vm'))
        json_filtered_data_vm_dr = self.get_data(self.get_param('json_filtered_data_vm_dr'))
        json_filtered_data = json_filtered_data_vm + json_filtered_data_vm_dr

        json_filtered_data_netapp = self.get_data(self.get_param('json_filtered_data_netapp'))
        json_filtered_data_netapp_dr = self.get_data(self.get_param('json_filtered_data_netapp_dr'))

        # System ID|Server Name|System Number|TIC Server Comment
        CustomerServerOverviewSheet0 = self.get_data(self.get_param('CustomerServerOverviewSheet0'))
        # SID|ServerType|StartDate|Runtime|StorageGB|Database|Service|InstanceType|DB SID (HANA)|SystemNumber
        LandscapeExportSheet0 = self.get_data(self.get_param('LandscapeExportSheet0'))

        # apply filter logics
        filtered_CustomerServerOverviewSheet0 = self.filter_CustomerServerOverview(CustomerServerOverviewSheet0)
        reserved_landscape, filtered_out_landscape = self.collect_LandscapeExport(LandscapeExportSheet0)

        # filter inactive data
        Inactive_Data_sheet0 = LandscapeExportSheet0[0]
        Inactive_Data_sheet0.append("comment")
        inactive_Data = self.filter_InactiveData(LandscapeExportSheet0, CustomerServerOverviewSheet0)
        inactive_Data.insert(0, Inactive_Data_sheet0)

        # 截取 name 后三位 作为 SID 到 Landscape 找，如果找不到， 则记录异常
        netapp_exceptions_normal = self.find_netapp_exception(json_filtered_data_netapp, "Normal",
                                                              reserved_landscape)

        netapp_exceptions_dr = self.find_netapp_exception(json_filtered_data_netapp_dr, "DR",
                                                          reserved_landscape)

        netapp_exceptions = [*netapp_exceptions_normal, *netapp_exceptions_dr]

        errors = self.validate(reserved_landscape, filtered_CustomerServerOverviewSheet0)

        if (len(errors) > 0):
            errors.insert(0, ['SID', 'ERROR_TYPE'])
            logging.error("Validate failure, refer to generated excel for more details.")

        # add titles as first row
        reserved_landscape.insert(0, LandscapeExportSheet0[0])

        # collect result and exceptio
        result, exception = self.collect_result_and_exception(json_filtered_data_netapp, json_filtered_data_netapp_dr,
                                                              json_filtered_data,
                                                              filtered_CustomerServerOverviewSheet0,
                                                              reserved_landscape)

        self.populate_data(self.get_param('data_key'), {
            "OVERVIEW": self.collect_overview(result),
            "ERROR": errors,
            "RESULT": result,
            "InactiveData": inactive_Data,
            "Exception": [*exception, *netapp_exceptions],
            "CustomerServerOverview": filtered_CustomerServerOverviewSheet0,
            "LandscapeExport": reserved_landscape,
            "Filteredout_LandscapeExport": filtered_out_landscape
        })

    def collect_overview(self, result):
        number = 0  # diff 个数
        sum = 0  # diff 总和
        flaver_sum = 0  # flaver false 个数

        for item in result:
            if str(type(item[7])) != "<class 'str'>":
                if int(item[7]) > 0:
                    number += 1
                sum += item[7]
                if item[9] == False:
                    flaver_sum += 1

        return [
            ["SystemRequireOptimization", number],
            ["VMFlaverNotMatchDED", flaver_sum],
            ["StorageCanBeSaved(GB)", abs(sum)]
        ]

    def collect_LandscapeExport(self, LandscapeExportSheet0):
        reserved = []
        filtered_out = []

        ded_records_be_deleted = self.find_records_be_deleted(LandscapeExportSheet0)

        for idx, row in enumerate(LandscapeExportSheet0):
            if self.shoud_be_reserved(idx, row, ded_records_be_deleted):
                reserved.append(row)
            else:
                filtered_out.append(row)

        return reserved, filtered_out

    def shoud_be_reserved(self, idx, row, ded_records_be_deleted):
        return not idx in ded_records_be_deleted \
            and len(row[7]) > 0 \
            and (row[1] == 'MASTER' or row[1] == 'STANDBY') \
            and DateUtil.is_after_now(DateUtil.months_delta(DateUtil.get_date(row[2], "%Y-%m-%d"), float(row[3])))

    def find_records_be_deleted(self, LandscapeExportSheet0):
        deleted_flag = ['Decommissioned', 'Cancelled', 'Off Boarding']
        in_deleting = False
        deleted_row_idx = []

        for idx, row in enumerate(LandscapeExportSheet0):
            if row[11] in deleted_flag \
                    or (len(row[11]) is 0 and in_deleting):

                in_deleting = True
                deleted_row_idx.append(idx)
            else:
                in_deleting = False

        return deleted_row_idx

    def filter_InactiveData(self, LandscapeExportSheet0, CustomerServerOverviewSheet0):
        # 输出Active=N的数据 row[10]为N Feb 9
        # 添加comment:如果Active=N, 但是在customerserveroverview里能找到 2.16
        InactiveData = list(
            filter(
                lambda row: (not row[11] == 'Decommission')
                            and (row[10] == 'N')
                            and (row[1] == 'MASTER' or row[1] == 'STANDBY')
                            and (DateUtil.is_after_now(
                    DateUtil.months_delta(DateUtil.get_date(row[2], "%Y-%m-%d"), float(row[3])))), LandscapeExportSheet0
            )
        )
        Comment = ""
        for item in InactiveData:
            for tempcid in CustomerServerOverviewSheet0:
                if item[0] in tempcid:
                    comment = "Active =N But SID exists in customerserveroverview"
                    item.append(comment)
                    break

        return InactiveData

    def filter_CustomerServerOverview(self, CustomerServerOverviewSheet0):
        return list(
            filter(
                lambda row: not row[3].startswith('CMS') and not row[3].startswith('CGS'),
                CustomerServerOverviewSheet0
            )
        )

    def collect_result_and_exception(self, json_filtered_data_netapp: [{}],
                                     json_filtered_data_netapp_dr: [{}],
                                     json_filtered_data: [{}],
                                     filtered_CustomerServerOverviewSheet0,
                                     filtered_LandscapeExportSheet0):
        # data from azure, after any changes of json-path, should review here
        data_from_azure = list(
            map(lambda record: {
                "name": record['name'],
                "vmSize": record['properties.hardwareProfile.vmSize'],
                "osDiskTotalGB": record['properties.storageProfile.osDisk.diskSizeGB'],
                "dataDiskTotalGB": self.calc_datadisk_size_total(record),
                "azure_datadisk_details": record['properties.storageProfile.dataDisks']
            }, json_filtered_data)
        )

        return self.build_result_and_collect_exception(json_filtered_data_netapp, json_filtered_data_netapp_dr,
                                                       data_from_azure,
                                                       filtered_CustomerServerOverviewSheet0,
                                                       filtered_LandscapeExportSheet0)

    def calc_datadisk_size_total(self, record):
        sum_disksizeGB = 0
        for item in record['properties.storageProfile.dataDisks']:
            if 'diskSizeGB' in item:
                current_disksizeGB = item['diskSizeGB']
                sum_disksizeGB += current_disksizeGB

        temp_sum = sum(list(
            map(lambda r: r['diskSizeGB'] if 'diskSizeGB' in r else 0, record['properties.storageProfile.dataDisks'])))
        if sum_disksizeGB != temp_sum:
            print("========================nonononono=======================================")

        return temp_sum

    def build_result_and_collect_exception(self, json_filtered_data_netapp,
                                           json_filtered_data_netapp_dr,
                                           data_from_azure,
                                           filtered_CustomerServerOverviewSheet0,
                                           filtered_LandscapeExportSheet0):
        # SID, hana-none-hana, servername, az dis, ded disk, details.
        # excel first row as title row.
        final_result = [
            ["SID", "TYPE", "DB SID(HANA)", "DR or NOT", "NetAppVolumeQuota", "AZURE_DataDiskSize", "DED_storageSize",
             "diff(VolumeQuota+AzureSize-20-DEDSize)", "Server Name(s)", "Flavor Matched", "Flavor Found",
             "Flavor Azure", "Flavor DED", "NoMatched Reason",  # "DED_details", "Azure_details"
             ]]

        # group by
        cso_SystemID_2_records, le_SID_2_records = self.prepare_groupby_data(filtered_CustomerServerOverviewSheet0,
                                                                             filtered_LandscapeExportSheet0)

        # Exceptions
        final_exception: [[]] = self.collect_exception(le_SID_2_records, cso_SystemID_2_records)

        # RESULT
        final_result = self.collect_each_row_of_result(cso_SystemID_2_records, data_from_azure, final_result,
                                                       json_filtered_data_netapp, json_filtered_data_netapp_dr,
                                                       le_SID_2_records)

        return final_result, final_exception

    def prepare_groupby_data(self, filtered_CustomerServerOverviewSheet0, filtered_LandscapeExportSheet0):
        # ['System ID', 'Server Name', 'System Number', 'TIC Server Comment']
        # ['VD1', 'hec44v023219', '000000000500239629', 'HIL VD1 FTP  |B1_0304137835-4309806-HSO.000191-16-982_PROCESS_ID:53911958']
        cso_SystemID_2_records: dict[str:[]] = self.group_by(
            lambda r: r[0] + ("|DR" if r[2].startswith("DR_") else "|Normal"),
            filtered_CustomerServerOverviewSheet0
        )

        # ['SID', 'ServerType', 'StartDate', 'Runtime', 'StorageGB', 'Database', 'Service', 'InstanceType', 'DB SID (HANA)', 'SystemNumber']
        # ['D79', 'MASTER', '2021-09-30', '60.000000', '1049.000000', 'HANA', 'HANA-Virtual-256GiB-AZURE, Linux(M32ls)', 'DB|DB01|', 'D89', '000000000500227006']
        #  {"D89|HANA|D79|DR" : [{},{}] }
        #  {"D79|NoneHANA|-|DR" : [{},{}]}
        le_SID_2_records: dict[str:[]] = self.group_by(
            lambda r: (r[8] + '|HANA|' + r[0] if r[6].startswith("HANA-") else r[0] + "|NoneHANA|-")
                      + ("|DR" if r[9].startswith("DR_") else "|Normal"),
            filtered_LandscapeExportSheet0
        )

        return cso_SystemID_2_records, le_SID_2_records

    def collect_each_row_of_result(self, cso_SystemID_2_records, data_from_azure, final_result,
                                   json_filtered_data_netapp, json_filtered_data_netapp_dr, le_SID_2_records):
        # server name has both hana, none-hana, then none-hana SID consider as duplicated.
        duplicated_records = self.find_duplicated_records(le_SID_2_records, cso_SystemID_2_records)

        for sid_type in sorted(le_SID_2_records.keys()):
            sid0type1Id2DRorNot3 = sid_type.split(self.SEPARATOR)

            sid = sid0type1Id2DRorNot3[0]
            type = sid0type1Id2DRorNot3[1]
            drornot = sid0type1Id2DRorNot3[3]

            filtered_server_names = self.find_proper_server_names(
                duplicated_records, cso_SystemID_2_records, drornot, sid
            )

            azure_servers = list(filter(lambda r: r['name'] in filtered_server_names, data_from_azure))
            azure_storage_size = sum(list(map(lambda r: float(r['dataDiskTotalGB']), azure_servers)))
            azure_flavor = list(map(lambda r: r['vmSize'][9:], azure_servers))  # remove the leading: Standard_

            ded_details = self.collect_ded_details(le_SID_2_records[sid_type])
            ded_storage_size = self.collect_ded_storage_size(ded_details)
            ded_flavor = list(map(
                lambda r: r["Service"], list(filter(
                    lambda r: "NO SERVER" not in r["Service"],
                    ded_details
                ))
            ))
            ded_dbsid = ded_details[0].get("DB SID(HANA)")

            flavor_matched, flavor_found_matched, flaver_nomatched_reason = self.compare_flaver(azure_flavor,
                                                                                                ded_flavor)

            netapp_volume_quota = self.calc_quota(sid0type1Id2DRorNot3[0],
                                                  json_filtered_data_netapp_dr if "DR" == drornot else json_filtered_data_netapp)

            final_result.append(
                [sid, type, ded_dbsid, drornot, netapp_volume_quota, azure_storage_size, ded_storage_size,
                 self.collect_diff(netapp_volume_quota, azure_storage_size, ded_storage_size),
                 self.SEPARATOR.join(filtered_server_names),
                 flavor_matched,
                 json.dumps(flavor_found_matched),
                 json.dumps(azure_flavor),
                 json.dumps(ded_flavor),
                 json.dumps(flaver_nomatched_reason),
                 # json.dumps(ded_details),  # DED_details
                 # json.dumps(azure_servers)  # Azure_details
                 ])

        return final_result

    def find_cso_records(self, cso_SystemID_2_records, drornot, sid):
        cso_key = self.SEPARATOR.join([sid, drornot])
        cso_records = cso_SystemID_2_records[cso_key] if cso_key in cso_SystemID_2_records else []
        return cso_records

    def find_proper_server_names(self, duplicated_records, cso_SystemID_2_records, drornot, sid):
        cso_records = self.find_cso_records(cso_SystemID_2_records, drornot, sid)
        duplicated_server_names = duplicated_records[sid] if sid in duplicated_records else []
        server_names = list(set(list(map(lambda r: r[1], cso_records))))
        return list(filter(lambda r: not r in duplicated_server_names, server_names))

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

    def value_2_count(self, given: dict = {}):
        result = {}
        for key in sorted(given.keys()):
            result[key] = len(given[key])

        return result

    def collect_ded_details(self, filtered_LandscapeExportSheet0):
        # SID|ServerType|StartDate|Runtime|StorageGB|Database|Service|InstanceType|DB SID(HANA)
        # 2.16添加DB SID 列
        return list(map(
            lambda i: {
                "SID": i[0],
                "ServerType": i[1],
                "StartDate": i[2],
                "Runtime": i[3],
                "StorageGB": i[4],
                "Database": i[5],
                "Service": i[6],
                "InstanceType": i[7],
                "DB SID(HANA)": i[8]
            }, filtered_LandscapeExportSheet0
        ))

    def collect_diff(self, netapp_volume_quota, azure_datadisk_totalGB, ded_storage_size):
        return netapp_volume_quota + azure_datadisk_totalGB - 20 - ded_storage_size

    def collect_ded_storage_size(self, ded_details):
        # 2.23 如果landscape里stroageGB列为空，设为100
        '''
        return sum(
            list(map(lambda r: float(r['StorageGB']) if 'storageGB' in r else 100, ded_details))
        )
        '''
        return sum(
            list(map(lambda r: float(r['StorageGB']), ded_details))
        )

    def validate(self, filtered_LandscapeExportSheet0, filtered_CustomerServerOverviewSheet0):
        """
        当DED 和 CustomerOverview 中 按照 sid group by count 不相同时报错；
        """
        sid_map2_count_2be_deleted = {}

        ded_groupby = self.group_by(lambda r: self.get_sid_or_dbsid(r, sid_map2_count_2be_deleted),
                                    filtered_LandscapeExportSheet0, skip_first=False)
        sid_2_count_ded = self.value_2_count(ded_groupby)

        cso_groupby = self.group_by(lambda r: r[0], filtered_CustomerServerOverviewSheet0)
        sid_2_count_cso = self.value_2_count(cso_groupby)

        found = []
        # customer overview 中有的 sid，需要在ded中存在， 并且个数相同
        for cso_sid in sid_2_count_cso.keys():
            if cso_sid in sid_2_count_ded.keys():
                count_cso = (sid_2_count_cso[cso_sid] - sid_map2_count_2be_deleted[
                    cso_sid]) if cso_sid in sid_map2_count_2be_deleted else sid_2_count_cso[cso_sid]

                count_ded = sid_2_count_ded[cso_sid]

                # Customer overview 中的 sid 对应的 记录数 跟 ded中对应的 记录数不同
                if not count_cso == count_ded:
                    found.append([
                        cso_sid,
                        'CustomerOverviewHasMore'
                        if count_cso > count_ded else
                        'LandscapeHasMore',
                        count_cso,
                        count_ded
                    ])
            else:
                found.append([cso_sid, 'InCustomerOverviewNotInLandscape'])

        if '' in sid_2_count_ded.keys():
            found.append(['', 'LandscapHasEmptySID', sid_2_count_ded['']])

        return found

    def get_sid_or_dbsid(self, row, sid_map2_count_2be_deleted):
        sid = row[0]
        dbsid = row[8]
        is_hana = row[6].startswith('HANA-')

        if is_hana:
            if sid in sid_map2_count_2be_deleted:
                sid_map2_count_2be_deleted[sid] += 1
            else:
                sid_map2_count_2be_deleted[sid] = 1

        return dbsid if is_hana else sid

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

        result = [["SID", "DRorNOT", "SOURCE", "Records NotIn Landscape"]]

        for sid_drornot in exception_entites.keys():
            sid0DRorNot1 = sid_drornot.split(self.SEPARATOR)
            result.append([
                sid0DRorNot1[0],
                sid0DRorNot1[1],
                "CustomerOverview",
                json.dumps(exception_entites[sid_drornot])
            ])

        return result

    def calc_quota(self, sid, json_filtered_data_netapp):
        found = list(filter(lambda r: sid in r['name'], json_filtered_data_netapp))

        if len(found) > 0:
            return sum(map(lambda r: int(r['usageThreshold']), found)) / 1024 / 1024 / 1024

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
                        if not row[1] in result[le_rid]:
                            result[le_rid].append(row[1])
        return result

    def find_netapp_exception(self, json_data_netapp, drornot, filtered_LandscapeExportSheet0):
        """
        :param json_data_netapp:
        :param filtered_LandscapeExportSheet0:
        SID|ServerType|StartDate|Runtime|StorageGB|Database|Service|InstanceType|DB SID (HANA)|SystemNumber

        :return: list of SID, DRorNOT, in JSON but not in Landscape
        """
        # 2.10 修改usageThreshold单位fromBtoGB
        result = []
        for item in json_data_netapp:
            name = item['name']
            # 后三位是 -HA 就再向前取 三个
            sid = name[-6:-3] if name[-3:] == "-HA" else name[-3:]

            found = list(filter(
                lambda r: (sid in r[0] or sid in r[8]),
                filtered_LandscapeExportSheet0
            ))

            if len(found) == 0:
                unique_name = name
                item["name"] = name.split('/')[-1]
                item["volume_unique_name"] = unique_name
                threshold = item['usageThreshold']
                usageThreshold = threshold / 1024 / 1024 / 1024
                item['usageThreshold'] = usageThreshold
                result.append([sid, drornot, "NetAppVolumeJson", json.dumps(item)])

        return result

    # 判断flavor 是否match
    # 2023.2.9 添加parameterNonMatched_reason，展示flavor 不匹配的原因
    def compare_flaver(self, azure_flavor, ded_flavor):
        found_matched = []
        NonMatched_reason = ""
        for azure_idx, azure_one in enumerate(azure_flavor):
            for ded_idx, ded_one in enumerate(ded_flavor):
                if azure_one in ded_one and not ded_idx in found_matched:
                    found_matched.append(ded_idx)

        #                     如果 从 Azure中 收集的 Flavor 在 ded Flavor中都找到
        matched = True if len(azure_flavor) == len(found_matched) \
                          and len(azure_flavor) == len(ded_flavor) else False  # 并且 azure flavor的个数 和 ded flavor 个数相同

        # 如果个数一直说明value不一致，否则值不同
        if len(azure_flavor) == len(ded_flavor) and matched == False:
            NonMatched_reason = "Value not matched"
        elif matched == False:
            NonMatched_reason = "Number not matched"
        else:
            NonMatched_reason = ""

        return matched, found_matched, NonMatched_reason