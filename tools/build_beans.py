import subprocess
import os
import json
import sys
import pprint

mib_path = r"C:\\Users\\leonm\\OneDrive - Radware LTD\\Doc\\Alteon\\31.0.10.50\\MIBS\\"
mib_url = 'C:/Users/leonm/OneDrive - Radware LTD/Doc/Alteon/31.0.10.50/MIBS/'
mibdump_script = r"C:\\Users\\leonm\\AppData\\Local\\Programs\\Python\\Python36\\Scripts\\mibdump.py"
out_path = os.path.join(mib_path, 'out')

GLOBAL_BEAN_WORDS = ['Cur', 'Cfg', 'Enh', 'New']
RESERVED_WORDS = ['import', 'global', 'if', 'else', 'def', 'in', 'and', 'or', 'for', 'from', 'continue']
ENUM_PREFIX = 'Enum'


class BeanTable(object):
    def __init__(self):
        self.indexes = list()
        self.properties = list()
        self.enums = dict()
        self.prop_to_enum = dict()

    def __str__(self):
        return str(self.__dict__)

    __repr__ = __str__


bean_objects = {
    'table': list(),
    'scalar': list(),
    'row': list(),
    'column': list()
}
oid_to_name = {
    'table': dict(),
    'row': dict(),
    'table_to_row': dict()
}


def generate_mib_json():
    pysmi_params = [
        '--mib-source=file:{0}'.format(mib_url),
        '--mib-source=http://mibs.snmplabs.com/asn1/@mib@',
        '--destination-directory={0}'.format(out_path),
        '--destination-format=json',
        '--no-dependencies',
        '--mib-stub=SNMPv2-SMI',
        '--ignore-errors',
        '--generate-mib-texts',
        '--keep-texts-layout',
        '--rebuild'
    ]

    cmd = list()
    cmd.append('python')
    cmd.append(mibdump_script)
    cmd.extend(pysmi_params)
    for p in os.listdir(mib_path):
        if os.path.isfile(os.path.join(mib_path, p)):
            cmd.append(p)
    if os.path.exists(out_path):
        for p in os.listdir(out_path):
            f = os.path.join(out_path, p)
            if os.path.isfile(f):
                os.unlink(f)
    subprocess.call(cmd, stderr=subprocess.STDOUT)


def write_bean_files(classes):

    def _generate_attr_str(bean_attrs: BeanTable):
        return_str = ''
        for prop in bean_attrs.properties:
            if prop not in bean_attrs.prop_to_enum:
                return_str += """        self.{0} = kwargs.get('{0}', None)\n""".format(prop)
            else:
                return_str += """        self.{1} = {0}.enum(kwargs.get('{1}', None))\n""".format(
                    bean_attrs.prop_to_enum[prop], prop)
        return return_str

    def _generate_index_str(bean_attrs: BeanTable):
        return_str = ''
        for index in bean_attrs.indexes:
            return_str += """self.{0}, """.format(index)
        return_str = return_str[0:len(return_str)-1]
        return return_str

    def _generate_index_names(bean_attrs: BeanTable):
        return_str = ''
        for index in bean_attrs.indexes:
            return_str += """'{0}', """.format(index)
        return_str = return_str[0:len(return_str)-1]
        return return_str

    def _prepare_enum_str(bean_attrs: BeanTable):
        e_str = ''
        for k, v in bean_attrs.enums.items():
            enum_values_str = ''
            for e_item_name, e_item_val in v.items():
                if e_item_name in RESERVED_WORDS:
                    e_item_name = e_item_name + '_'
                e_item_name = e_item_name.replace('-', '_')
                enum_values_str += "    {0} = {1}\n".format(e_item_name, e_item_val)

            e_str += """class {0}(BaseBeanEnum):\n{1}\n\n""".format(k, enum_values_str)
        if len(e_str) > 2:
            return '\n' + e_str[:(len(e_str) - 1)]
        return e_str

    for f in os.listdir('beans'):
        if not f.startswith('__'):
            os.remove("beans{0}{1}".format(os.path.sep, f))

    for key, value in classes.items():

        with open("beans{1}{0}.py".format(key, os.path.sep), 'w') as f:
            attr_str = _generate_attr_str(value)
            enum_str = _prepare_enum_str(value)
            if key != 'Global':

                index_str = _generate_index_str(value)
                index_names = _generate_index_names(value)

                clss_text = """
from radware.sdk.beans_common import *\n\n{3}
class {0}(DeviceBean):
    def __init__(self, **kwargs):
{1}
    def get_indexes(self):
        return {2}
    
    @classmethod
    def get_index_names(cls):
        return {4}\n\n""".format(key, attr_str, index_str, enum_str, index_names)
            else:
                clss_text = """
from radware.sdk.beans_common import *\n\n{1}
class Root(DeviceBean):
    def __init__(self, **kwargs):
{0}\n\n""".format(attr_str, enum_str)

            f.write(clss_text)
            f.close()


def get_row_name(table_name):
    for k, v in oid_to_name['table'].items():
        if v == table_name:
            row_oid = oid_to_name['table_to_row'][k]
            return oid_to_name['row'][row_oid]


def build_table_structure():
    def enum_handler(mib_obj, t_name):
        if 'constraints' in mib_obj['syntax'] and 'enumeration' in mib_obj['syntax']['constraints']:
            bean_table[t_name].enums.update({mib_obj['name']: mib_obj['syntax']['constraints']['enumeration']})

    def get_parent_oid(oid):
        return oid[:oid.rindex('.')]

    def _filter_out_new_props(props_arr):
        tmp_arr = list()
        for item in props_arr:
            if 'Cur' in item:
                t = item.replace('Cur', 'New', 1)
                if t not in props_arr:
                    tmp_arr.append(item)
            else:
                tmp_arr.append(item)
        return tmp_arr

    def _filter_out_new_table(table_map):
        tmp_dict = dict()
        for key, val in table_map.items():
            if 'Cur' in key:
                t = key.replace('Cur', 'New', 1)
                if t not in table_map:
                    tmp_dict.update({key: val})
            else:
                tmp_dict.update({key: val})
        return tmp_dict

    bean_table = {
        'Global': BeanTable()
    }
    for p in os.listdir(out_path):
        f = os.path.join(out_path, p)
        if os.path.isfile(f):
            with open(f, 'r') as fp:
                f_json = json.load(fp)

            for k, v in f_json.items():
                if 'oid' in v and 'nodetype' in v:
                    bean_objects[v['nodetype']].append(v)
                    if v['nodetype'] == 'table' or v['nodetype'] == 'row':
                        oid_to_name[v['nodetype']].update({v['oid']: v['name']})

            for k, v in oid_to_name['table'].items():
                bean_table.update({v: BeanTable()})

            for k, v in oid_to_name['row'].items():
                oid_to_name['table_to_row'].update({get_parent_oid(k): k})

            for row in bean_objects['row']:
                table_oid = get_parent_oid(row['oid'])
                table_name = oid_to_name['table'][table_oid]
                for i in row['indices']:
                    bean_table[table_name].indexes.append(i['object'])

            for column in bean_objects['column']:
                if column['status'] != 'obsolete':
                    row_oid = get_parent_oid(column['oid'])
                    table_oid = get_parent_oid(row_oid)
                    table_name = oid_to_name['table'][table_oid]
                    bean_table[table_name].properties.append(column['name'])
                    enum_handler(column, table_name)

            for scalar in bean_objects['scalar']:
                if scalar['status'] != 'obsolete':
                    if scalar['name'] not in bean_table['Global'].properties:
                        bean_table['Global'].properties.append(scalar['name'])
                        enum_handler(scalar, 'Global')

    bean_table['Global'].properties = _filter_out_new_props(bean_table['Global'].properties)
    for k in list(bean_table['Global'].enums.keys()):
        if k not in bean_table['Global'].properties:
            bean_table['Global'].enums.pop(k)
    return _filter_out_new_table(bean_table)


def to_rest_format(tables):
    def _name_to_arr_upper_case(src_str_name):
        new_name_arr = []
        break_idx = []
        prev_upper = False
        for i, c in enumerate(src_str_name):
            if i == 0:
                continue
            if c.isupper():
                if not prev_upper and i > 1:
                    break_idx.append(i)
                prev_upper = True
            else:
                prev_upper = False

        prev_index = 0
        for i in break_idx:
            new_name_arr.append(src_str_name[prev_index:i])
            prev_index = i
        new_name_arr.append(src_str_name[prev_index:])
        return new_name_arr

    def _trim_table(row_key, bean_table: BeanTable):
        def handle_props(prop_list):
            prev = ''
            new_props = []
            for prop in prop_list:
                cur_prop_arr = _name_to_arr_upper_case(prop)
                cur_prefix = ''
                prefix_for_enum = ''
                cur_word_len = 0

                for i, cur_word in enumerate(table_name_arr):
                    if i == len(cur_prop_arr):
                        break
                    if cur_word.lower() == cur_prop_arr[i].lower():
                        cur_prefix += cur_prop_arr[i]
                        if cur_prop_arr[i] not in GLOBAL_BEAN_WORDS:
                            if len(cur_prop_arr[i]) > 3 and cur_prop_arr[i][-3:] in GLOBAL_BEAN_WORDS:
                                prefix_for_enum += cur_prop_arr[i][0:-3]
                            else:
                                prefix_for_enum += cur_prop_arr[i]
                        cur_word_len = len(cur_prop_arr[i])
                    elif cur_word.lower() == (cur_prop_arr[i].lower()+'s'):
                        cur_prefix += cur_prop_arr[i]
                        if cur_prop_arr[i] not in GLOBAL_BEAN_WORDS:
                            if len(cur_prop_arr[i]) > 3 and cur_prop_arr[i][-3:] in GLOBAL_BEAN_WORDS:
                                prefix_for_enum += cur_prop_arr[i][0:-3]
                            else:
                                prefix_for_enum += cur_prop_arr[i]
                        cur_word_len = len(cur_prop_arr[i])
                        break
                    else:
                        break

                if prev == prop[len(cur_prefix):]:
                    prev = prop[(len(cur_prefix) - cur_word_len):]
                else:
                    prev = prop[len(cur_prefix):]
                new_props.append(prev)
                if prop in bean_table.enums:
                    enum_suffix = prefix_for_enum+prev
                    enum_suffix = enum_suffix[0].upper() + enum_suffix[1:]
                    enum_class = ENUM_PREFIX+enum_suffix
                    new_bean_table.enums.update({enum_class: bean_table.enums[prop]})
                    new_bean_table.prop_to_enum.update({prev: enum_class})

            return new_props

        table_name_arr = _name_to_arr_upper_case(row_key)
        new_bean_table = BeanTable()
        new_bean_table.indexes = handle_props(bean_table.indexes)
        new_bean_table.properties = handle_props(bean_table.properties)
        return new_bean_table

    rest_tables = dict()
    for k, v in tables.items():
        if k != 'Global':
            row_name = get_row_name(k)
            new = _trim_table(row_name, v)
            rest_tables.update({k[0].upper()+k[1:]: new})
        else:
            cur_root_enums = v.enums
            v.enums = dict()
            for k2, v2 in cur_root_enums.items():
                enum_class_root = ENUM_PREFIX + k2[0].upper() + k2[1:]
                v.enums.update({enum_class_root: v2})
                v.prop_to_enum.update({k2: enum_class_root})
            rest_tables.update({k: v})

    return rest_tables

from radware.alteon.sdk.impl import AlteonRest


def bean_test_alteon(tables):
    alteon_va = AlteonRest('192.168.31.100','admin','admin',validate_certs=False)
    alteon_vx = AlteonRest('10.170.2.31','admin','radware',validate_certs=False)
    alteon_vadc = AlteonRest('10.170.16.16','admin','admin',validate_certs=False)

    def submit_call(alteon, uri):
        try:
            alteon.read_data_object(uri)
        except Exception:
            return False
        return True

    root_err = list()
    table_error = list()

    alteon_va.read_data_object('sysName')
    alteon_vx.read_data_object('sysName')
    alteon_vadc.read_data_object('sysName')

    for k, v in tables.items():
        if k != 'Global':
            if not submit_call(alteon_va, k) and not submit_call(alteon_vx, k) and not submit_call(alteon_vadc, k):
                table_error.append(k)
        else:
            for prop in v.properties:
                if not submit_call(alteon_va, prop) and not submit_call(alteon_vx, prop) and not submit_call(alteon_vadc, prop):
                    root_err.append(prop)

    print('Root Error: {0}'.format(root_err))
    print('Table Error: {0}'.format(table_error))


EXCL_ROOT_PROPS = ['bgpVersion', 'bgpLocalAs', 'bgpIdentifier', 'entLastChangeTime', 'dot3adTablesLastChanged', 'ospfRouterId', 'ospfAdminStat', 'ospfVersionNumber', 'ospfAreaBdrRtrStatus', 'ospfASBdrRtrStatus', 'ospfExternLsaCount', 'ospfExternLsaCksumSum', 'ospfTOSSupport', 'ospfOriginateNewLsas', 'ospfRxNewLsas', 'ospfExtLsdbLimit', 'ospfMulticastExtensions', 'ospfExitOverflowInterval', 'ospfDemandExtensions', 'ipForwarding', 'ipDefaultTTL', 'ipInReceives', 'ipInHdrErrors', 'ipInAddrErrors', 'ipForwDatagrams', 'ipInUnknownProtos', 'ipInDiscards', 'ipInDelivers', 'ipOutRequests', 'ipOutDiscards', 'ipOutNoRoutes', 'ipReasmTimeout', 'ipReasmReqds', 'ipReasmOKs', 'ipReasmFails', 'ipFragOKs', 'ipFragFails', 'ipFragCreates', 'ipRoutingDiscards', 'icmpInMsgs', 'icmpInErrors', 'icmpInDestUnreachs', 'icmpInTimeExcds', 'icmpInParmProbs', 'icmpInSrcQuenchs', 'icmpInRedirects', 'icmpInEchos', 'icmpInEchoReps', 'icmpInTimestamps', 'icmpInTimestampReps', 'icmpInAddrMasks', 'icmpInAddrMaskReps', 'icmpOutMsgs', 'icmpOutErrors', 'icmpOutDestUnreachs', 'icmpOutTimeExcds', 'icmpOutParmProbs', 'icmpOutSrcQuenchs', 'icmpOutRedirects', 'icmpOutEchos', 'icmpOutEchoReps', 'icmpOutTimestamps', 'icmpOutTimestampReps', 'icmpOutAddrMasks', 'icmpOutAddrMaskReps', 'tcpRtoAlgorithm', 'tcpRtoMin', 'tcpRtoMax', 'tcpMaxConn', 'tcpActiveOpens', 'tcpPassiveOpens', 'tcpAttemptFails', 'tcpEstabResets', 'tcpCurrEstab', 'tcpInSegs', 'tcpOutSegs', 'tcpRetransSegs', 'tcpInErrs', 'tcpOutRsts', 'udpInDatagrams', 'udpNoPorts', 'udpInErrors', 'udpOutDatagrams', 'egpInMsgs', 'egpInErrors', 'egpOutMsgs', 'egpOutErrors', 'egpAs', 'snmpOutPkts', 'snmpInTooBigs', 'snmpInNoSuchNames', 'snmpInBadValues', 'snmpInReadOnlys', 'snmpInGenErrs', 'snmpInTotalReqVars', 'snmpInTotalSetVars', 'snmpInGetRequests', 'snmpInGetNexts', 'snmpInSetRequests', 'snmpInGetResponses', 'snmpInTraps', 'snmpOutTooBigs', 'snmpOutNoSuchNames', 'snmpOutBadValues', 'snmpOutGenErrs', 'snmpOutGetRequests', 'snmpOutGetNexts', 'snmpOutSetRequests', 'snmpOutGetResponses', 'snmpOutTraps']
EXCL_BEANS = ['SlbStatSpAuxSessTable', 'SpMemUsageStatsTable', 'BgpPeerTable', 'BgpRcvdPathAttrTable', 'Bgp4PathAttrTable', 'Dot1dStpExtPortTable', 'EntPhysicalTable', 'EntLogicalTable', 'EntLPMappingTable', 'EntAliasMappingTable', 'EntPhysicalContainsTable', 'Dot3StatsTable', 'Dot3CollTable', 'Dot3adAggTable', 'Dot3adAggPortListTable', 'Dot3adAggPortTable', 'Dot3adAggPortStatsTable', 'Dot3adAggPortDebugTable', 'OspfAreaTable', 'OspfStubAreaTable', 'OspfLsdbTable', 'OspfAreaRangeTable', 'OspfHostTable', 'OspfIfTable', 'OspfIfMetricTable', 'OspfVirtIfTable', 'OspfNbrTable', 'OspfVirtNbrTable', 'OspfExtLsdbTable', 'OspfAreaAggregateTable', 'AtTable', 'IpAddrTable', 'IpRouteTable', 'IpNetToMediaTable', 'TcpConnTable', 'UdpTable', 'EgpNeighTable', 'EtherStatsTable', 'HistoryControlTable', 'EtherHistoryTable', 'AlarmTable', 'HostControlTable', 'HostTable', 'HostTimeTable', 'HostTopNControlTable', 'HostTopNTable', 'MatrixControlTable', 'MatrixSDTable', 'MatrixDSTable', 'FilterTable', 'ChannelTable', 'BufferControlTable', 'CaptureBufferTable', 'EventTable', 'LogTable']


def filter_alteon_beans(tables):
    for k, v in list(tables.items()):
        if k != 'Global':
            if k in EXCL_BEANS:
                tables.pop(k)
        else:
            v.properties[:] = [x for x in v.properties if x not in EXCL_ROOT_PROPS]
            [v.enums.pop(x) for x in list(v.enums.keys()) if x[4].lower()+x[5:] in EXCL_ROOT_PROPS]


def main():
    generate_mib_json()
    tables = build_table_structure()
    tables = to_rest_format(tables)
    #print(pprint.pformat(tables))
    filter_alteon_beans(tables)
    write_bean_files(tables)
    #bean_test_alteon(tables)


if __name__ == '__main__':
    main()




