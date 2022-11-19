from copy import deepcopy
import ezfunctions
import ipaddress
import json
import re

class transition(object):
    def __init__(self, type):
        self.type = type

    def policy_loop(self, **kwargs):
        # Set the org_count to 0 for the First Organization
        # Loop through the orgs discovered by the Class
        json_data = kwargs['json_data']
        for item in json_data['config']['orgs']:
            kwargs['immDict']['orgs'].update({item['name']:{}})
        org_list = list(kwargs['immDict']['orgs'].keys())
        for o in org_list:
            kwargs['org'] = o
            orgDict = [i for i in json_data['config']['orgs'] if i['name'] == o][0]
            for key, value in orgDict.items():
                if re.search('_(policies|pools|profiles)', key):
                    if '_policies' in key:
                        p1 = 'policies'
                        p2 = key.replace('_policies', '')
                    elif '_pools' in key:
                        p1 = 'pools'
                        p2 = key.replace('_pools', '')
                    elif '_profiles' in key:
                        p1 = 'profiles'
                        p2 = key.replace('_profiles', '')
                    for item in value:
                        polVars = deepcopy(item)
                        if polVars.get('descr'):
                            polVars['description'] = polVars['descr']
                            polVars.pop('descr')
                        if polVars.get('tags'): polVars.pop('tags')
                        if   p2 == 'ip':         polVars = modify_ip(polVars)
                        elif p2 == 'iqn':        polVars = modify_iqn(polVars)
                        elif p2 == 'mac':        polVars = modify_mac(polVars)
                        elif p2 == 'port':       polVars = modify_port(polVars)
                        elif p2 == 'system_qos': polVars = modify_system_qos(polVars)
                        elif p2 == 'uuid':       polVars = modify_uuid(polVars)
                        elif p2 == 'wwnn':       polVars = modify_wwnn(polVars)
                        elif p2 == 'wwpn':       polVars = modify_wwpn(polVars)
                        kwargs['class_path'] = f'intersight,{p1},{p2}'
                        kwargs = ezfunctions.ez_append(polVars, **kwargs)
        return kwargs

def modify_ip(polVars):
    if not polVars.get('ipv4_blocks') == None:
        index_count = len(polVars['ipv4_blocks'])
        for r in range(0,index_count):
            if not polVars['ipv4_blocks'][r].get('to') == None:
                polVars['ipv4_blocks'][r]['size'] = int(
                    ipaddress.IPv4Address(polVars['ipv4_blocks'][r]['to'])
                ) - int(ipaddress.IPv4Address(polVars['ipv4_blocks'][r]['from'])) + 1
                polVars['ipv4_blocks'][r].pop('to')
    if not polVars.get('ipv6_blocks') == None:
        index_count = len(polVars['ipv4_blocks'])
        for r in range(0,index_count):
            if not polVars['ipv6_blocks'][r].get('to') == None:
                polVars['ipv6_blocks'][r]['size'] = int(
                    ipaddress.IPv6Address(polVars['ipv6_blocks'][r]['to'])
                ) - int(ipaddress.IPv6Address(polVars['ipv6_blocks'][r]['from'])) + 1
                polVars['ipv6_blocks'][r].pop('to')
    return polVars

def modify_iqn(polVars):
    if not polVars.get('iqn_blocks') == None:
        index_count = len(polVars['iqn_blocks'])
        for r in range(0,index_count):
            if not polVars['iqn_blocks'][r].get('to') == None:
                polVars['iqn_blocks'][r]['size'] = int(
                    polVars['iqn_blocks'][r]['to']
                    ) - int(polVars['iqn_blocks'][r]['from']) + 1
                polVars['iqn_blocks'][r].pop('to')
    return polVars

def modify_mac(polVars):
    if not polVars.get('mac_blocks') == None:
        index_count = len(polVars['mac_blocks'])
        for r in range(0,index_count):
            if 'to' in polVars['mac_blocks'][r]:
                int_from = int(polVars['mac_blocks'][r]['from'].replace(':', ''), 16)
                int_to = int(polVars['mac_blocks'][r]['to'].replace(':', ''), 16)
                polVars['mac_blocks'][r]['size'] = int_to - int_from + 1
                polVars['mac_blocks'][r].pop('to')
    return polVars

def modify_port(polVars):
    polVars['names'] = [polVars['name']]
    del polVars['name']
    port_type_list = [
        'port_channel_appliances,appliance_port_channels',
        'port_channel_ethernet_uplinks,lan_port_channels',
        'port_channel_fc_uplinks,san_port_channels' ,
        'port_channel_fcoe_uplinks,fcoe_port_channels',
        'port_modes,san_unified_ports',
        'port_role_appliances,appliance_ports',
        'port_role_ethernet_uplinks,lan_uplink_ports',
        'port_role_fc_storage,storage_ports',
        'port_role_fc_uplinks,san_uplink_ports',
        'port_role_fcoe_uplinks,fcoe_ports',
        'port_role_servers,server_ports'
    ]
    for i in port_type_list:
        easy_imm = i.split(',')[0]
        imm_transition = i.split(',')[1]
        if not polVars.get(imm_transition) == None:
            polVars[f'{easy_imm}'] = polVars[imm_transition]
            del polVars[imm_transition]
    for item in port_type_list:
        port_type = item.split(',')[0]
        if not polVars.get(port_type) == None:
            if re.search('_port_channels', port_type):
                pcount = 0
                for i in polVars[port_type]:
                    polVars[port_type][pcount]['pc_ids'] = polVars[port_type][pcount]['pc_id']
                    del polVars[port_type][pcount]['pc_id']
                    pcount += 1
            if re.search('port_modes', port_type):
                polVars[port_type]['port_list'] = [polVars[port_type]['port_id_start'], polVars[port_type]['port_id_end']]
                polVars[port_type].pop('port_id_start')
                polVars[port_type].pop('port_id_end')
                if polVars[port_type]['slot_id'] == 1:
                    polVars[port_type].pop('slot_id')
                print(json.dumps(polVars, indent=4))
                if re.search('(UCS-FI-6536)', polVars['device_model']):
                    polVars[port_type]['custom_mode'] = 'BreakoutFibreChannel32G'
                else: polVars[port_type]['custom_mode'] = 'FibreChannel'
            if re.search('port_role', port_type):
                pcount = 0
                for v in polVars[port_type]:
                    v['port_list'] = v['port_id']
                    v.pop('port_id')
                    if v['slot_id'] == 1:
                        v.pop('slot_id')
    return polVars

def modify_system_qos(polVars):
    if not polVars.get('mac_blocks') == None:
        total_weight = 0
        for r in range(0,6):
            if polVars['classes'][r]['state'] == 'Enabled':
                total_weight += int(polVars['classes'][r]['weight'])
        for r in range(0,6):
            if polVars['classes'][r]['state'] == 'Enabled':
                x = ((int(polVars['classes'][r]['weight']) / total_weight) * 100)
                polVars['classes'][r]['bandwidth_percent'] = str(x).split('.')[0]
            else: polVars['classes'][r]['bandwidth_percent'] = 0
    return polVars

def modify_uuid(polVars):
    if not polVars.get('uuid_blocks') == None:
        index_count = len(polVars['uuid_blocks'])
        for r in range(0,index_count):
            if not polVars['uuid_blocks'][r].get('to') == None:
                parg = {}
                for i in ['from', 'to']:
                    if re.search('[a-zA-Z]', polVars['uuid_blocks'][r][i].split('-')[1]):
                        parg[f'int_{i}'] = int(polVars['uuid_blocks'][r][i].split('-')[1], 16)
                    else:
                        parg[f'int_{i}'] = int(polVars['uuid_blocks'][r][i].split('-')[1])
                int_from = parg[f'int_from']
                int_to = parg[f'int_to']
                polVars['uuid_blocks'][r]['size'] = int_to - int_from + 1
                polVars['uuid_blocks'][r].pop('to')
    return polVars

def modify_wwnn(polVars):
    if not polVars.get('wwnn_blocks') == None:
        index_count = len(polVars['wwnn_blocks'])
        for r in range(0,index_count):
            if 'to' in polVars['wwnn_blocks'][r]:
                int_from = int(polVars['wwnn_blocks'][r]['from'].replace(':', ''), 16)
                int_to = int(polVars['wwnn_blocks'][r]['to'].replace(':', ''), 16)
                polVars['wwnn_blocks'][r]['size'] = int_to - int_from + 1
                polVars['id_blocks'] = polVars['wwnn_blocks']
                polVars['id_blocks'][r].pop('to')
        if polVars.get('wwnn_blocks'): polVars.pop('wwnn_blocks')
    return polVars

def modify_wwpn(polVars):
    if not polVars.get('wwpn_blocks') == None:
        index_count = len(polVars['wwpn_blocks'])
        for r in range(0,index_count):
            if 'to' in polVars['wwpn_blocks'][r]:
                int_from = int(polVars['wwpn_blocks'][r]['from'].replace(':', ''), 16)
                int_to = int(polVars['wwpn_blocks'][r]['to'].replace(':', ''), 16)
                polVars['wwpn_blocks'][r]['size'] = int_to - int_from + 1
                polVars['id_blocks'] = polVars['wwpn_blocks']
                polVars['id_blocks'][r].pop('to')
        if polVars.get('wwpn_blocks'): polVars.pop('wwpn_blocks')
    return polVars
