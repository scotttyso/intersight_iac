from copy import deepcopy
from dotmap import DotMap
import ezfunctions
import isdk
import json
import numpy
import os
import re
import time
import validating

serial_regex = re.compile('^[A-Z]{3}[2-3][\\d]([0][1-9]|[1-4][0-9]|[5][0-3])[\\dA-Z]{4}$')
part1 = '(ethernet|fibre_channel)_qos|fc_zone|flow_control|iscsi_adapter|link_aggregation'
part2 = 'multicast|ntp|port|power|serial_over_lan|thermal|virtual_kvm'
skip_regex = re.compile(f'^({part1}|{part2})$')
#=======================================================
# Policies Class
#=======================================================
class api_policies(object):
    def __init__(self, type):
        self.type = type

    #=======================================================
    # BIOS Policy Modification
    #=======================================================
    def bios(self, apiBody, item, pargs, **kwargs):
        pargs    = pargs
        jsonVars = kwargs['ezData']['policies']['allOf'][1]['properties']['bios']['template_tuning']
        for k, v in apiBody.items():
            if type(v) == int or type(v) == float: apiBody[k] = str(v)
        if item.get('bios_template'):
            template = item['bios_template']
            if '-tpm' in template:
                btemplate = template.replace('-tpm', '')
                apiBody = dict(apiBody, **jsonVars[btemplate])
                apiBody = dict(apiBody, **jsonVars['tpm'])
            else:
                apiBody = dict(apiBody, **jsonVars[template])
                apiBody = dict(apiBody, **jsonVars['tpm_disabled'])
        return apiBody

    #=======================================================
    # Boot Order Policy Modification
    #=======================================================
    def boot_order(self, apiBody, item, pargs, **kwargs):
        pargs    = pargs
        jsonVars = kwargs['ezData']['policies']['allOf'][1]['properties']['boot_order']
        if item.get('boot_devices'):
            apiBody['boot_devices'] = []
            for i in item['boot_devices']:
                boot_dev = {'class_id':i['object_type'],'name':i['name'],'object_type':i['object_type']}
                if re.search('(Iscsi|LocalDisk|Nvme|PchStorage|San|SdCard)', i['object_type']
                             ) and apiBody['configured_boot_mode'] == 'Uefi':
                    boot_dev['Bootloader'] = {'class_id':'boot.Bootloader','object_type':'boot.Bootloader'}
                    if 'bootloader' in i:
                        jVars1 = jsonVars['key_map_loader']
                        for k, v in i.items():
                            if k in jVars1: boot_dev['Bootloader'].update({jVars1[k]:v})
                    else: boot_dev['Bootloader'].update({'Name':'BOOTx64.EFI','Path':"\\EFI\\BOOT\\"})
                jVars1 = jsonVars['key_map_boot']
                for k, v in i.items():
                    if k in jVars1:
                        boot_dev.update({jVars1[k]:v})
                apiBody['boot_devices'].append(boot_dev)
        return apiBody

    #=======================================================
    # Ethernet Adapter Policy Modification
    #=======================================================
    def ethernet_adapter(self, apiBody, item, pargs, **kwargs):
        pargs    = pargs
        jsonVars = kwargs['ezData']['policies']['allOf'][1]['properties']['ethernet_adapter']['template_tuning']
        if item.get('adapter_template'):
            template = item['adapter_template']
            apiBody = dict(apiBody, **jsonVars[template])
        return apiBody

    #=======================================================
    # Ethernet Network Control Policies Policy Modification
    #=======================================================
    def ethernet_network_control(self, apiBody, item, pargs, **kwargs):
        pargs    = pargs
        jsonVars = kwargs['ezData']['policies']['allOf'][1]['properties']['ethernet_network_control']['key_map']
        for k, v in item.items():
            if 'lldp' in k:
                if not apiBody.get('lldp_settings'): apiBody['lldp_settings'] = {}
                apiBody['lldp_settings'].update({jsonVars[k]:v})
                apiBody.pop(jsonVars[k])
        return apiBody

    #=======================================================
    # Ethernet Network Group Policies Policy Modification
    #=======================================================
    def ethernet_network_group(self, apiBody, item, pargs, **kwargs):
        pargs  = pargs
        kwargs = kwargs
        apiBody.update({'vlan_settings':{'object_type':'fabric.VlanSettings'}})
        klist = ['allowed_vlans','native_vlan']
        for i in klist:
            if i in item:
                if i == 'native_vlan':
                    apiBody['vlan_settings'].update({i:int(item[i])})
                else: apiBody['vlan_settings'].update({i:item[i]})
        return apiBody


    #=======================================================
    # Fibre-Channel Adapter Policy Modification
    #=======================================================
    def fibre_channel_adapter(self, apiBody, item, pargs, **kwargs):
        pargs    = pargs
        jsonVars = kwargs['ezData']['policies']['allOf'][1]['properties']['fibre_channel_adapter']['template_tuning']
        if item.get('adapter_template'):
            template = item['adapter_template']
            apiBody = dict(apiBody, **jsonVars[template])
        return apiBody

    #=======================================================
    # Fibre-Channel Network Policies Policy Modification
    #=======================================================
    def fibre_channel_network(self, apiBody, item, pargs, **kwargs):
        pargs    = pargs
        jsonVars = kwargs['ezData']['policies']['allOf'][1]['properties']['fibre_channel_network']['key_map']
        apiBody.update({'vsan_settings':{'object_type':'vnic.VsanSettings'}})
        for k, v in item.items():
            if re.search('(default_)?(v(l|s)an(_id)?)', k) and k in jsonVars:
                apiBody['vsan_settings'].update({jsonVars[k]:v})
                apiBody.pop(jsonVars[k])
        return apiBody

    #=======================================================
    # IMC Access Policy Modification
    #=======================================================
    def imc_access(self, apiBody, item, pargs, **kwargs):
        kwargs = kwargs
        apiBody.update({'address_type':{'enable_ip_v4':True,'enable_ip_v6':False,}})
        addfam = ['v4', 'v6']
        for i in addfam:
            add_config = f'ip{i}_address_configuration'
            if add_config in item:
                apiBody['address_type'].update({f'enable_ip_{i}':item[add_config]})
        apiBody.update({'configuration_type':{
            'configure_inband': True,
            'configure_out_of_band': True,
        }})
        #=====================================================
        # Attach Pools to the API Body
        #=====================================================
        pargs.apiMethod = 'get'
        pargs.policy = 'ip'
        pargs.names = []
        ptype = ['inband_ip_pool', 'out_of_band_ip_pool']
        for i in ptype:
            if i in item: pargs.names.append(item[i])
        kwargs = isdk.api('ip').calls(pargs, **kwargs)
        for i in ptype:
            if i in item:
                if not kwargs['pmoids'].get(item[i]):
                    validating.error_policy_doesnt_exist(ptype, item[i], self.type, 'policy', apiBody['name'])
                apiBody.update({i:{
                    'class_id':'mo.MoRef','moid':kwargs['pmoids'][item[i]]['Moid'],'object_type':'ippool.Pool'
                }})
        return apiBody

    #=======================================================
    # IPMI over LAN Policy Modification
    #=======================================================
    def ipmi_over_lan(self, apiBody, item, pargs, **kwargs):
        item = item
        pargs = pargs
        if not os.environ.get('TF_VAR_ipmi_key') == None:
            apiBody.update({'encryption_key':os.environ.get('TF_VAR_ipmi_key')})
        else:
            kwargs['Variable'] = f"ipmi_key"
            kwargs = ezfunctions.sensitive_var_value(**kwargs)
            apiBody.update({'encryption_key':kwargs['var_value']})
        return apiBody

    #=======================================================
    # iSCSI Adapter Policy Modification
    #=======================================================
    def iscsi_boot(self, apiBody, item, pargs, **kwargs):
        kwargs = kwargs
        for k, v in item.items():
            if 'ip_address' in k:
                apiBody.update({
                    'initiator_static_ip_v4_address':v,
                    'initiator_static_ip_v4_config':[{
                        'class_id': 'ippool.IpV4Config',
                        'gateway': item['gateway'],
                        'netmask': item['netmask'],
                        'object_type': 'ippool.IpV4Config',
                        'primary_dns': item['primary_dns'],
                        'secondary_dns': item['secondary_dns'],
                    }]
                })
            elif 'authentication' in k:
                if re.search('(mutual_)?chap', v):
                    kwargs['Variable'] = 'iscsi_boot_password'
                    kwargs = ezfunctions.sensitive_var_value(**kwargs)
                    apiBody.update({v:{
                        'class_id': "vnic.IscsiAuthProfile",
                        'object_type': "vnic.IscsiAuthProfile",
                        'password': kwargs['var_value'],
                        'user_id': item['username']
                    }})
        #=====================================================
        # Attach Pools to the API Body
        #=====================================================
        if item.get('initiator_ip_pool'):
            ip_pool = item['initiator_ip_pool']
            pargs.apiMethod = 'get'
            pargs.policy = 'ip'
            pargs.names = []
            pargs.names.append(ip_pool)
            kwargs = isdk.api('ip').calls(pargs, **kwargs)
            if not kwargs['pmoids'].get(ip_pool):
                validating.error_policy_doesnt_exist('initiator_ip_pool', ip_pool, self.type, 'policy', apiBody['name'])
            apiBody.update({'initiator_ip_pool':{
                'class_id':'mo.MoRef','moid':kwargs['pmoids'][ip_pool]['Moid'],'object_type':'ippool.Pool'
            }})
        plist = ['primary', 'secondary']
        for p in plist:
            if item.get(f'{p}_target_policy'):
                target = f'{p}_target_policy'
                pargs.apiMethod = 'get'
                pargs.policy = 'iscsi_static_target'
                pargs.names = [item[target]]
                kwargs = isdk.api('iscsi_static_target').calls(pargs, **kwargs)
                if not kwargs['pmoids'].get(item[target]):
                    validating.error_policy_doesnt_exist(f'{p}_target', item[target], self.type, 'policy', apiBody['name'])
                apiBody.update({target:{
                    'class_id':'mo.MoRef',
                    'moid':kwargs['pmoids'][item[target]]['Moid'],
                    'object_type':'vnic.IscsiStaticTargetPolicy'
                }})
        return apiBody

    #=======================================================
    # iSCSI Adapter Policy Modification
    #=======================================================
    def iscsi_static_target(self, apiBody, item, pargs, **kwargs):
        item   = item
        kwargs = kwargs
        pargs  = pargs
        for i in apiBody['lun']: i.update({'object_type':'vnic.Lun'})
        return apiBody

    #=======================================================
    # LAN Connectivity Policy Modification
    #=======================================================
    def lan_connectivity(self, apiBody, item, pargs, **kwargs):
        item   = item
        kwargs = kwargs
        if not apiBody.get('vnic_placement_mode'): apiBody.update({'placement_mode':'custom'})
        else: apiBody.pop('vnic_placement_mode')
        if not apiBody.get('target_platform'): apiBody.update({'target_platform': 'FIAttached'})
        if item.get('iqn_pool'):
            pargs.apiMethod = 'get'
            pargs.names     = [item['iqn_pool']]
            pargs.policy    = 'iqn'
            pargs.purpose   = 'iqn'
            ptype           = 'iqn_pool'
            kwargs = isdk.api(ptype).calls(pargs, **kwargs)
            pargs.moids['iqn_pool'] = kwargs['pmoids']
            pname = item['iqn_pool']
            if not pargs.moids['iqn_pool'].get(pname):
                validating.error_policy_doesnt_exist(ptype, pname, apiBody['name'], self.type, 'Policy')
            iqnpool = pargs.moids['iqn_pool'][pname]['Moid']
            apiBody.update({
                'iqn_allocation_type':'Pool',
                'iqn_pool':{
                    'class_id':'mo.MoRef','moid':iqnpool,'object_type':'iqnpool.Pool'
                }
            })
        return apiBody

    #=======================================================
    # Link Control Policy Modification
    #=======================================================
    def link_control(self, apiBody, item, pargs, **kwargs):
        kwargs = kwargs
        if item.get('admin_state'): apiBody['udld_settings'] = {'admin_state':item['admin_state']}
        if item.get('mode'):
            if not apiBody.get('udld_settings'): apiBody['udld_settings']
            apiBody['udld_settings'].update({'mode':item['mode']})
        return apiBody

    #=======================================================
    # Local User Policy Modification
    #=======================================================
    def local_user(self, apiBody, item, pargs, **kwargs):
        jsonVars = kwargs['ezData']['policies']['allOf'][1]['properties']['local_user']['key_map_password']
        for k, v in item.items():
            if k in jsonVars:
                if not apiBody.get('password_properties'): apiBody['password_properties'] = {}
                apiBody['password_properties'].update({jsonVars[k]:v})
                if apiBody['password_properties'].get("password_history"):
                    apiBody['password_properties'].update({'password_history': 0})
        return apiBody

    #=====================================================
    # Assign Users to Local User Policies
    #=====================================================
    def local_users(self, pargs, **kwargs):
        #=====================================================
        # Get Existing Users
        #=====================================================
        pargs.apiMethod = 'get'
        pargs.names = []
        pargs.policy = 'local_users'
        for i in pargs.item: pargs.names.append(i['username'])
        kwargs = isdk.api('local_users').calls(pargs, **kwargs)
        user_moids = kwargs['pmoids']
        pargs.names  = []
        pargs.policy = 'iamrole'
        for i in pargs.item: pargs.names.append(i['role'])
        rnames = "', '".join(pargs.names).strip("', '")
        pargs.apiFilter = f"Name in ('{rnames}') and Type eq 'IMC'"
        kwargs = isdk.api('iamrole').calls(pargs, **kwargs)
        role_moids = kwargs['pmoids']
        pargs.names  = []
        pargs.policy = 'user_role'
        umoids = []
        for k, v in user_moids.items(): umoids.append(v['Moid'])
        umoids = "', '".join(umoids).strip("', '")
        pargs.apiFilter = f"EndPointUser.Moid in ('{umoids}')"
        kwargs = isdk.api('user_role').calls(pargs, **kwargs)
        urole_moids = kwargs['pmoids']
        pargs.pop('apiFilter')
        local_user_moid = pargs.pmoid
        #=====================================================
        # Construct API Body Users
        #=====================================================
        for i in pargs.item:
            apiBody = {'name':i['username']}
            apiBody = org_map(apiBody, pargs.org_moid)
            kwargs['Variable'] = f"local_user_password_{i['password']}"
            kwargs = ezfunctions.sensitive_var_value(**kwargs)
            pargs.policy = 'local_users'
            pargs.purpose = i['username']
            if not user_moids.get(i['username']):
                pargs.apiMethod = 'create'
                pargs.apiBody = apiBody
                kwargs = isdk.api(self.type).calls(pargs, **kwargs)
                user_moid = kwargs['pmoid']
            else: user_moid = user_moids[i['username']]['Moid']
            #=====================================================
            # Create API Body for User Role
            #=====================================================
            if i.get('enabled'): apiBody = {'enabled':i['enabled']}
            else: apiBody = {}
            apiBody['password'] = kwargs['var_value']
            apiBody.update({'end_point_role':[{
                'class_id':'mo.MoRef','moid':role_moids[i['role']]['Moid'],'object_type':'iam.EndPointRole'
            }]})
            apiBody.update({'end_point_user':{
                'class_id':'mo.MoRef','moid':user_moid,'object_type':'iam.EndPointUser'
            }})
            apiBody.update({'end_point_user_policy':{
                'class_id':'mo.MoRef','moid':local_user_moid,'object_type':'iam.EndPointUserPolicy'
            }})
            #=====================================================
            # Create or Patch the Policy via the Intersight API
            #=====================================================
            if not urole_moids.get(user_moid): pargs.apiMethod = 'create'
            else:
                pargs.apiMethod = 'patch'
                pargs.pmoid = urole_moids[user_moid]['Moid']
            pargs.policy = 'user_role'
            pargs.purpose = i['username']
            pargs.apiBody = apiBody
            kwargs = isdk.api('user_role').calls(pargs, **kwargs)
        return kwargs

    #=======================================================
    # Network Connectivity Policy Modification
    #=======================================================
    def network_connectivity(self, apiBody, item, pargs, **kwargs):
        dns_list = ['v4', 'v6']
        kwargs   = kwargs
        for i in dns_list:
            if f'dns_servers_{i}' in item:
                if len(item[f'dns_servers_{i}']) > 0:
                    apiBody.update({f'preferred_ip{i}dns_server':item[f'dns_servers_{i}'][0]})
                if len(item[f'dns_servers_{i}']) > 1:
                    apiBody.update({f'alternate_ip{i}dns_server':item[f'dns_servers_{i}'][1]})
        return apiBody

    #=====================================================
    #  Policies Function
    #=====================================================
    def policies(self, pargs, **kwargs):
        #=====================================================
        # Load Variables and Send Begin Notification
        #=====================================================
        jsonVars = kwargs['ezData']['policies']['allOf'][1]['properties'][self.type]['key_map']
        policies = kwargs['immDict']['orgs'][kwargs['org']]['policies'][self.type]
        validating.begin_section(self.type, 'policies')
        #=====================================================
        # Get Existing Policies
        #=====================================================
        pargs.apiMethod = 'get'
        pargs.org_moid  = kwargs['org_moids'][kwargs['org']]['Moid']
        pargs.policy    = self.type
        pargs.purpose   = self.type
        pargs.names = []
        for i in policies:
            if self.type == 'port':
                for x in range(0,len(i['names'])): pargs.names.append(i['names'][x])
            else: pargs.names.append(i['name'])
        kwargs = isdk.api(self.type).calls(pargs, **kwargs)
        policy_moids = kwargs['pmoids']
        #=====================================================
        # Add Attributes to the apiBody
        #=====================================================
        def build_apiBody(apiBody, jsonVars, pargs, **kwargs):
            for k, v in item.items():
                if k in jsonVars: apiBody.update({jsonVars[k]:v})
            apiBody = org_map(apiBody, pargs.org_moid)
            if apiBody.get('tags'): apiBody['tags'].append(kwargs['ezData']['tags'])
            else: apiBody.update({'tags':[kwargs['ezData']['tags']]})
            return apiBody

        #=====================================================
        # Create/Patch the Policy via the Intersight API
        #=====================================================
        def policies_to_api(apiBody, pargs, **kwargs):
            pargs.apiBody = apiBody
            pargs.policy = self.type
            if policy_moids.get(apiBody['name']):
                pargs.apiMethod = 'patch'
                pargs.pmoid = policy_moids[apiBody['name']]['Moid']
            else: pargs.apiMethod = 'create'
            kwargs = isdk.api(self.type).calls(pargs, **kwargs)
            pargs.pmoid = kwargs['pmoid']
            return kwargs

        #=====================================================
        # Loop through Items
        #=====================================================
        for item in policies:
            if self.type == 'port':
                for x in range(0,len(i['names'])):
                    #=====================================================
                    # Construct apiBody Payload
                    #=====================================================
                    apiBody = {'name':item['names'][x]}
                    apiBody = build_apiBody(apiBody, jsonVars, pargs, **kwargs)
                    kwargs = policies_to_api(apiBody, pargs, **kwargs)
            else:
                #=====================================================
                # Construct apiBody Payload
                #=====================================================
                apiBody = {}
                apiBody = build_apiBody(apiBody, jsonVars, pargs, **kwargs)
                #=====================================================
                # Add Policy Specific Settings
                #=====================================================
                if not re.search(skip_regex, self.type):
                    apiBody = eval(f'api_policies.{self.type}')(self, apiBody, item, pargs, **kwargs)
                pargs.policy = self.type
                kwargs = policies_to_api(apiBody, pargs, **kwargs)
            #=====================================================
            # Loop Thru Sub-Items
            #=====================================================
            if 'lan_connectivity' == self.type:
                if item.get('vnics'):
                    pargs.item = item['vnics']
                    kwargs = api_policies('vnics').vnics(pargs, **kwargs)
            elif 'local_user' == self.type:
                if item.get('users'):
                    pargs.item = item['users']
                    kwargs = api_policies('local_users').local_users(pargs, **kwargs)
            elif 'port' == self.type:
                if item.get('port_modes'):
                    pargs.item = item
                    kwargs = api_policies('port_mode').port_mode(pargs, **kwargs)
                pargs.item = item
                kwargs = api_policies('ports').ports(pargs, **kwargs)
            elif 'san_connectivity' == self.type:
                if item.get('vhbas'):
                    pargs.item = item['vhbas']
                    kwargs = api_policies('vhbas').vhbas(pargs, **kwargs)
            elif 'storage' == self.type:
                if item.get('drive_groups'):
                    pargs.item = item['drive_groups']
                    kwargs = api_policies('storage_drive_group').storage_drive_group(pargs, **kwargs)
            elif 'vlan' == self.type:
                if item.get('vlans'):
                    pargs.item = item['vlans']
                    kwargs = api_policies('vlans').vlans(pargs, **kwargs)
            elif 'vsan' == self.type:
                if item.get('vsans'):
                    pargs.item = item['vsans']
                    kwargs = api_policies('vsans').vsans(pargs, **kwargs)
        #=====================================================
        # Send End Notification and return kwargs
        #=====================================================
        validating.end_section(self.type, 'policies')
        return kwargs

    #=====================================================
    # Port Modes for Port Policies
    #=====================================================
    def port_mode(self, pargs, **kwargs):
        #=====================================================
        # Get Port Policy
        #=====================================================
        pargs.apiMethod = 'get'
        pargs.names  = []
        pargs.policy = 'port'
        pargs.names.extend(pargs.item['names'])
        kwargs = isdk.api('port').calls(pargs, **kwargs)
        port_moids = kwargs['pmoids']
        for x in range(0,len(pargs.item['names'])):
            #=====================================================
            # Confirm if the vHBAs are already Attached
            #=====================================================
            pargs.pmoid = port_moids[pargs.item['names'][x]]['Moid']
            port_moid = pargs.pmoid
            for i in pargs.item['port_modes']:
                pargs.apiMethod = 'get'
                pargs.policy = 'port_mode'
                pargs.apiFilter = f"PortIdStart eq {i['port_list'][0]} and PortPolicy.Moid eq '{port_moid}'"
                kwargs = isdk.api('port_mode').calls(pargs, **kwargs)
                pargs.pop('apiFilter')
                pm_moids = kwargs['pmoids']
                apiBody = {'object_type':'fabric.PortMode'}
                plist = i['port_list']
                apiBody.update({
                    'custom_mode':i['custom_mode'],'port_id_start':plist[0],'port_id_end':plist[1]
                })
                apiBody.update({'port_policy':{
                    'class_id':'mo.MoRef','moid':port_moid,'object_type':'fabric.PortPolicy'}})
                if i.get('slot_id'): apiBody.update({'slot_id':i['port_modes']['slot_id']})
                else: apiBody.update({'slot_id':1})
                #=====================================================
                # Create or Patch the Policy via the Intersight API
                #=====================================================
                if pm_moids.get(port_moid):
                    if pm_moids[port_moid].get(i['port_list'][0]):
                        pargs.apiMethod = 'patch'
                        pargs.pmoid = pm_moids[port_moid][i['port_list'][0]]['Moid']
                    else: pargs.apiMethod = 'create'
                else: pargs.apiMethod = 'create'
                pargs.port_policy_name = pargs.item['names'][x]
                pargs.policy = 'port_mode'
                pargs.purpose = 'port_mode'
                pargs.apiBody = apiBody
                kwargs = isdk.api('port_mode').calls(pargs, **kwargs)
        return kwargs

    #=====================================================
    # Assign Port Types to Port Policies
    #=====================================================
    def ports(self, pargs, **kwargs):
        jsonVars = kwargs['ezData']['policies']['allOf'][1]['properties']['port']
        #=====================================================
        # Create/Patch the Port Policy Port Types
        #=====================================================
        def api_calls(apiBody, pargs, **kwargs):
            #=====================================================
            # Check if the Port Policy Port Type Exists
            #=====================================================
            pargs.apiMethod = 'get'
            pargs.policy = pargs.type
            if re.search('port_channel', pargs.type):
                policy_name = int(apiBody['pc_id'])
                pargs.apiFilter = f"PcId eq {int(apiBody['pc_id'])} and PortPolicy.Moid eq '{pargs.port_policy}'"
            else:
                policy_name = int(apiBody['port_id'])
                pargs.apiFilter = f"PortId eq {int(apiBody['port_id'])} and PortPolicy.Moid eq '{pargs.port_policy}'"
            kwargs = isdk.api(pargs.policy).calls(pargs, **kwargs)
            pargs.pop('apiFilter')
            pargs.moids[pargs.type] = kwargs['pmoids']
            #=====================================================
            # Create or Patch the Policy via the Intersight API
            #=====================================================
            if pargs.moids[pargs.type].get(pargs.port_policy):
                if pargs.moids[pargs.type][pargs.port_policy].get(policy_name):
                    pargs.apiMethod = 'patch'
                    pargs.pmoid = pargs.moids[pargs.type][pargs.port_policy][policy_name]['Moid']
                else: pargs.apiMethod = 'create'
            else: pargs.apiMethod = 'create'
            pargs.policy = pargs.type
            pargs.purpose = pargs.type
            pargs.apiBody = apiBody
            kwargs = isdk.api(pargs.type).calls(pargs, **kwargs)
            return kwargs
        #=====================================================
        # Create API Body for Port Policies
        #=====================================================
        def port_type_call(item, x, pargs, **kwargs):
            pargs.port_policy = pargs.pmoid
            for i in item[pargs.type]:
                apiBody = deepcopy(pargs.jsonVars['classes'][pargs.type])
                apiBody.update({'port_policy':{
                    'class_id':'mo.MoRef','moid':pargs.port_policy,'object_type':'fabric.PortPolicy'}})
                for z in pargs.policy_list:
                    pshort = z.replace('_policy', '')
                    jVars = kwargs['ezData']['policies']['allOf'][1]['properties'][pshort]
                    if i.get(z):
                        if pargs.moids[pshort].get(i[z]):
                            pmoid = pargs.moids[pshort][i[z]]['Moid']
                        else:
                            ppname = pargs.port_policy_name
                            validating.error_policy_doesnt_exist(z, i[z], pargs.type, 'Port Policy', ppname)
                        if not 'network_group' in z:
                            apiBody.update({jVars['object_name']:{
                                'class_id':'mo.MoRef','moid':pmoid,'object_type':jVars['object_type']}})
                        else: apiBody.update({jVars['object_name']:[{
                                'class_id':'mo.MoRef','moid':pmoid,'object_type':jVars['object_type']}]})
                if i.get('admin_speed'): apiBody.update({'admin_speed':i['admin_speed']})
                if i.get('fec'): apiBody.update({'fec':i['fec']})
                if i.get('mode'): apiBody.update({'mode':i['mode']})
                if i.get('priority'): apiBody.update({'priority':i['priority']})
                if re.search('port_channel', pargs.type):
                    if len(i['pc_ids']) > 1: apiBody.update({'pc_id':i['pc_ids'][x]})
                    else: apiBody.update({'pc_id':i['pc_id'][0]})
                    if i.get('vsan_ids'):
                        if len(i['vsan_ids']) > 1: apiBody.update({'vsan_id':i['vsan_ids'][x]})
                        else: apiBody.update({'vsan_id':i['vsan_ids'][0]})
                    apiBody['ports'] = []
                    for intf in i['interfaces']:
                        intfBody = {'class_id':'fabric.PortIdentifier','object_type':'fabric.PortIdentifier'}
                        intfBody.update({'port_id':intf['port_id']})
                        if intf.get('breakout_port_id'): intfBody.update(
                                {'aggregate_port_id':intf['breakout_port_id']})
                        else: intfBody.update({'aggregate_port_id':0})
                        if intf.get('slot_id'): intfBody.update({'slot_id':intf['slot_id']})
                        else: intfBody.update({'slot_id':1})
                        apiBody['ports'].append(intfBody)
                    kwargs = api_calls(apiBody, pargs, **kwargs)
                elif re.search('role', pargs.type):
                    interfaces = ezfunctions.vlan_list_full(i['port_list'])
                    for intf in interfaces:
                        intfBody = deepcopy(apiBody)
                        if i.get('breakout_port_id'): intfBody.update(
                                {'aggregate_port_id':intf['breakout_port_id']})
                        else: intfBody.update({'aggregate_port_id':0})
                        intfBody.update({'port_id':int(intf)})
                        if i.get('device_number'): intfBody.update({'preferred_device_id':i['device_number']})
                        if i.get('connected_device_type'): intfBody.update(
                                {'preferred_device_type':i['connected_device_type']})
                        if i.get('slot_id'): intfBody.update({'slot_id':intf['slot_id']})
                        else: intfBody.update({'slot_id':1})
                        if i.get('vsan_ids'):
                            if len(i['vsan_ids']) > 1: intfBody.update({'vsan_id':i['vsan_ids'][x]})
                            else: intfBody.update({'vsan_id':i['vsan_ids'][0]})
                        kwargs = api_calls(intfBody, pargs, **kwargs)
            return kwargs

        jsonVars = kwargs['ezData']['policies']['allOf'][1]['properties']['port']
        #=====================================================
        # Get Policies
        #=====================================================
        pargs.policy_list = jsonVars['policy_list']
        pargs.jsonVars = jsonVars
        item = pargs.item
        pargs.apiMethod = 'get'
        pargs.names = pargs.item['names']
        pargs.policy = 'port'
        kwargs = isdk.api('port').calls(pargs, **kwargs)
        pargs.moids['port'] = kwargs['pmoids']
        for i in pargs.policy_list:
            pargs.names  = []
            pargs.policy = i.replace('_policy', '')
            for z in jsonVars['port_type_list']:
                if item.get(z):
                    for y in item[z]:
                        if y.get(i): pargs.names.append(y[i])
            pargs.names = numpy.unique(numpy.array(pargs.names))
            kwargs = isdk.api(pargs.policy).calls(pargs, **kwargs)
            pargs.moids[pargs.policy] = kwargs['pmoids']
        #=====================================================
        # Create API Body for Port Types
        #=====================================================
        for x in range(0,len(item['names'])):
            for z in jsonVars['port_type_list']:
                if item.get(z):
                    pargs.port_policy_name = item['names'][x]
                    pargs.pmoid = pargs.moids['port'][item['names'][x]]['Moid']
                    pargs.type = z
                    port_type_call(item, x, pargs, **kwargs)
        return kwargs

    #=======================================================
    # SAN Connectivity Policy Modification
    #=======================================================
    def san_connectivity(self, apiBody, item, pargs, **kwargs):
        jsonVars = kwargs['ezData']['policies']['allOf'][1]['properties']['san_connectivity']['key_map']
        pargs.names = []
        if item.get('wwnn_pool'): pargs.names.append(item['wwnn_pool'])
        pargs.apiMethod = 'get'
        pargs.policy = 'wwnn'
        kwargs = isdk.api('wwnn').calls(pargs, **kwargs)
        pargs.moids['wwnn_pool'] = kwargs['pmoids']
        if not apiBody.get('vhba_placement_modes'): apiBody.update({'placement_mode':'custom'})
        if item.get('wwnn_pool'):
            if not pargs.moids['wwnn_pool'].get(item['wwnn_pool']):
                        validating.error_policy_doesnt_exist(
                            'wwnn_pool', item['wwnn_pool'], self.type, 'policy', apiBody['name'])
            wwnn_moid = pargs.moids['wwnn_pool'][item['wwnn_pool']]['Moid']
            apiBody.update({'wwnn_pool':{'class_id':'mo.MoRef','moid':wwnn_moid,'object_type':'fcpool.Pool'}})
        return apiBody

    #=======================================================
    # SNMP Policy Modification
    #=======================================================
    def snmp(self, apiBody, item, pargs, **kwargs):
        jsonVars = kwargs['ezData']['policies']['allOf'][1]['properties']['bios']['template_tuning']
        for k, v in apiBody.items():
            if type(v) == int or type(v) == float: apiBody[k] = str(v)
        if item.get('bios_template'):
            template = item['bios_template']
            if '_tpm' in template:
                btemplate = template.replace('_tpm', '')
                apiBody = dict(apiBody, **jsonVars[btemplate])
                apiBody = dict(apiBody, **jsonVars['tpm'])
            else:
                apiBody = dict(apiBody, **jsonVars[template])
                apiBody = dict(apiBody, **jsonVars['tpm_disabled'])
        return apiBody

    #=======================================================
    # Storage Policy Modification
    #=======================================================
    def storage(self, apiBody, item, pargs, **kwargs):
        jsonVars = kwargs['ezData']['policies']['allOf'][1]['properties']['bios']['template_tuning']
        for k, v in apiBody.items():
            if type(v) == int or type(v) == float: apiBody[k] = str(v)
        if item.get('bios_template'):
            template = item['bios_template']
            if '_tpm' in template:
                btemplate = template.replace('_tpm', '')
                apiBody = dict(apiBody, **jsonVars[btemplate])
                apiBody = dict(apiBody, **jsonVars['tpm'])
            else:
                apiBody = dict(apiBody, **jsonVars[template])
                apiBody = dict(apiBody, **jsonVars['tpm_disabled'])
        return apiBody

    #=====================================================
    # Assign Drive Groups to Storage Policies
    #=====================================================
    def storage_drive_group(self, pargs, **kwargs):
        jsonVars = kwargs['ezData']['policies']['allOf'][1]['properties']['storage']['virtual_drive_map']
        #=====================================================
        # Get Storage Policies
        #=====================================================
        pargs.apiMethod = 'get'
        pargs.names = []
        pargs.policy = 'storage_drive_group'
        for i in pargs.item: pargs.names.append(i['name'])
        kwargs = isdk.api('storage_drive_group').calls(pargs, **kwargs)
        dg_moids = kwargs['pmoids']
        #=====================================================
        # Create API Body for Storage Drive Groups
        #=====================================================
        for i in pargs.item:
            #=====================================================
            # Create API Body for VLANs
            #=====================================================
            apiBody = {
                'class_id':'storage.DriveGroup', 'name':i['name'],
                'object_type':'storage.DriveGroup', 'raid_level':i['raid_level']
                }
            apiBody.update({'storage_policy':{
                'class_id':'mo.MoRef','moid':pargs.pmoid,'object_type':'storage.StoragePolicy'
            }})
            if i.get('manual_drive_group'):
                apiBody['manual_drive_group'] = {
                    'class_id':'storage.ManualDriveGroup','object_type':'storage.ManualDriveGroup'
                }
                if i['manual_drive_group'][0].get('dedicated_hot_spares'):
                    apiBody['manual_drive_group']['dedicated_hot_spares'] = i[
                        'manual_drive_group']['dedicated_hot_spares']
                apiBody['manual_drive_group']['span_groups'] = []
                for x in i['manual_drive_group'][0]['drive_array_spans']:
                    apiBody['manual_drive_group']['span_groups'].append({
                        'class_id':'storage.SpanDrives','object_type':'storage.SpanDrives','slots':x['slots']
                    })
            if i.get('virtual_drives'):
                apiBody['virtual_drives'] = []
                for x in i['virtual_drives']:
                    vdBody = {}
                    for k, v in x.items():
                        if k in jsonVars: vdBody.update({jsonVars[k]:v})
                    vdBody.update({'object_type':'storage.VirtualDriveConfiguration'})
                    if vdBody.get('virtual_drive_policy'):
                        vdBody['virtual_drive_policy'].update({'object_type':'storage.VirtualDrivePolicy'})
                    apiBody['virtual_drives'].append(vdBody)
            #=====================================================
            # Create or Patch the Policy via the Intersight API
            #=====================================================
            if not dg_moids.get(i['name']): pargs.apiMethod = 'create'
            else:
                pargs.apiMethod = 'patch'
                pargs.pmoid = dg_moids[i['name']]['Moid']
            pargs.policy = 'storage_drive_group'
            pargs.purpose = 'storage_drive_group'
            pargs.apiBody = apiBody
            kwargs = isdk.api('storage_drive_group').calls(pargs, **kwargs)
        return kwargs

    #=======================================================
    # Switch Control Policy Modification
    #=======================================================
    def switch_control(self, apiBody, item, pargs, **kwargs):
        jsonVars = kwargs['ezData']['policies']['allOf'][1]['properties']['switch_control']['mac_and_udld']
        apiBody.update({
            'mac_aging_settings':{
                'mac_aging_option':'Default', 'mac_aging_time':14500, 'object_type':'fabric.MacAgingSettings'
            },
            'udld_settings':{
                'message_interval':15,'recovery_action':'reset','object_type':'fabric.UdldGlobalSettings'
            }
        })
        for k, v in item.items():
            if k in jsonVars:
                if 'mac_' in k: apiBody['mac_aging_settings'].update({jsonVars[k]:v})
                elif 'udld_' in k: apiBody['udld_settings'].update({jsonVars[k]:v})
        return apiBody

    #=======================================================
    # Syslog Policy Modification
    #=======================================================
    def syslog(self, apiBody, item, pargs, **kwargs):
        jsonVars = kwargs['ezData']['policies']['allOf'][1]['properties']['syslog']['remote_logging']
        if 'local_logging' in item:
            apiBody.update({'local_clients':[{
                'class_id':'syslog.LocalFileLoggingClient',
                'object_type':'syslog.LocalFileLoggingClient',
                'min_severity':item['local_logging']['minimum_severity']
            }]})
        if item.get('remote_logging'):
            apiBody['remote_clients'] = []
            for i in item['remote_logging']:
                rsyslog = {'class_id':'syslog.RemoteLoggingClient','object_type':'syslog.RemoteLoggingClient'}
                for k, v in i.items():
                    if k in jsonVars: rsyslog.update({jsonVars[k]:v})
                if not '0.0.0.0' in rsyslog: apiBody['remote_clients'].append(rsyslog)
            if len(apiBody['remote_clients']) == 0: apiBody.pop('remote_clients')
        return apiBody

    #=======================================================
    # System QoS Policy Modification
    #=======================================================
    def system_qos(self, apiBody, item, pargs, **kwargs):
        item   = item
        kwargs = kwargs
        for i in apiBody['classes']:
            i.update({'admin_state':i['state'],'name':i['priority'],'object_type':'fabric.QosClass'})
            i.pop('priority')
            i.pop('state')
        return apiBody

    #=====================================================
    # Assign VNICs to LAN Connectivity Policies
    #=====================================================
    def vhbas(self, pargs, **kwargs):
        jsonVars = kwargs['ezData']['policies']['allOf'][1]['properties'][self.type]
        #=====================================================
        # Get Policies and Pools
        #=====================================================
        scp_moid = pargs.pmoid
        pargs.apiMethod = 'get'
        for p in jsonVars['policy_list']:
            pshort = ((p.replace('_policy', '')).replace('_policies', '')).replace('_pools', '')
            pargs.names  = []
            pargs.policy = pshort
            for i in pargs.item:
                if i.get(p) and 'policy' in p: pargs.names.append(i[p])
                elif p == 'vhbas': pargs.names.extend(i['names'])
                elif i.get(p): pargs.names.extend(i[p])
            pargs.names = numpy.unique(numpy.array(pargs.names))
            kwargs = isdk.api(pshort).calls(pargs, **kwargs)
            pargs.moids[p] = kwargs['pmoids']
        #=====================================================
        # Create API Body for VNICs
        #=====================================================
        policy_list = deepcopy(jsonVars['policy_list'])
        remove_list = ['fc_zone_policies', 'vhbas', 'wwpn_pools']
        for x in remove_list: policy_list.remove(x)
        for i in pargs.item:
            if not i.get('fc_zone_policies'): policy_list.pop('fc_zone_policies')
            for x in range(0,len(i['names'])):
                apiBody = {'name':i['names'][x],'order':i['placement_pci_order'][x]}
                for k, v in i.items():
                    if k in jsonVars['key_map']:
                        apiBody.update({jsonVars['key_map'][k]:v})
                apiBody.update({'object_type':'vnic.FcIf'})
                for p in policy_list:
                    pshort = (p.replace('_policy', '')).replace('_policies', '')
                    jVars = kwargs['ezData']['policies']['allOf'][1]['properties'][pshort]
                    if type(i[p]) == list: pname = i[p][x]
                    else: pname = i[p]
                    if not pargs.moids[p].get(pname):
                        validating.error_policy_doesnt_exist(p, pname, self.type, 'policy', apiBody['name'])
                    else:
                        pmoid = pargs.moids[p][pname]['Moid']
                        apiBody.update({jVars['object_name']:{
                            'class_id':'mo.MoRef','moid':pmoid,'object_type':jVars['object_type']
                        }})
                apiBody.update({'san_connectivity_policy':{
                    'class_id':'mo.MoRef','moid':scp_moid,'object_type':'vnic.SanConnectivityPolicy'
                }})
                apiBody.update({'placement':{
                    'id':'MLOM','object_type':'vnic.PlacementSettings','pci_link':0,'uplink':0
                }})
                if i.get('fc_zone_policies'):
                    zone_policies = numpy.array_split(i['fc_zone_policies'], 2)
                    jVars = kwargs['ezData']['policies']['allOf'][1]['properties']['fc_zone']
                    apiBody.update({jVars['object_name']:[]})
                    for z in zone_policies[x]:
                        pname = z
                        if not pargs.moids['fc_zone_policies'].get(pname):
                            validating.error_policy_doesnt_exist('fc_zone_policy', pname, self.type, 'policy', apiBody['name'])
                        apiBody[jVars['object_name']].append({
                            'class_id':'mo.MoRef',
                            'moid':pargs.moids['fc_zone_policies'][pname]['Moid'],
                            'object_type':'fabric.FcZonePolicy'}
                        )
                if i.get('placement_switch_id'):
                    apiBody['placement'].update({'switch_id':i['placement_switch_id']})
                else:
                    if x == 0: side = 'A'
                    else: side = 'B'
                    apiBody['placement'].update({'switch_id':side})
                place_list = ['placement_pci_links', 'placement_slot_ids', 'placement_uplink_ports']
                for p in place_list:
                    count = 0
                    if i.get(p): apiBody.pop(p); count += 1
                    if count == 1:
                        if len(i[p]) == 2: pval = i[p][x]
                        else: pval = i[p][0]
                        if 'slot' in p: pvar = 'id'
                        pvar = p.replace('placement_', '')
                        pvar = pvar.replace('s', '')
                        apiBody['placement'][pvar] = pval
                if i.get('vhba_type'):
                    apiBody.update({'type':i['vhba_type']})
                    apiBody.pop('vhba_type')
                else: apiBody.update({'type':'fc-initiator'})
                if i.get('wwpn_pools'):
                    wwpnpool = pargs.moids['wwpn_pools'][i['wwpn_pools'][x]]['Moid']
                    apiBody.update({
                        'wwpn_address_type':'POOL',
                        'wwpn_pool':{'class_id':'mo.MoRef','moid':wwpnpool,'object_type':'fcpool.Pool'}
                    })
                #=====================================================
                # Create or Patch the VLANs via the Intersight API
                #=====================================================
                if not pargs.moids.vhbas.get(i['names'][x]): pargs.apiMethod = 'create'
                else:
                    pargs.apiMethod = 'patch'
                    pargs.pmoid = pargs.moids.vhbas[i['names'][x]]['Moid']
                pargs.policy = 'vhbas'
                pargs.purpose = 'vhbas'
                pargs.apiBody = apiBody
                kwargs = isdk.api('vhbas').calls(pargs, **kwargs)
        return kwargs

    #=======================================================
    # Virtual Media Policy Modification
    #=======================================================
    def virtual_media(self, apiBody, item, pargs, **kwargs):
        jsonVars = kwargs['ezData']['policies']['allOf'][1]['properties']['virtual_media']['add_key_map']
        if item.get('add_virtual_media'):
            apiBody.update({'mappings':[]})
            for i in item['add_virtual_media']:
                vmedia_add = {}
                for k, v in i.items():
                    if k in jsonVars: vmedia_add.update({jsonVars[k]:v})
                vmedia_add.update({'object_type':'vmeida.Mapping'})
                apiBody['mappings'].append(vmedia_add)
        return apiBody

    #=======================================================
    # VLAN Policy Modification
    #=======================================================
    def vlan(self, apiBody, item, pargs, **kwargs):
        jsonVars = kwargs['ezData']['policies']['allOf'][1]['properties']['bios']['template_tuning']
        for k, v in apiBody.items():
            if type(v) == int or type(v) == float: apiBody[k] = str(v)
        if item.get('bios_template'):
            template = item['bios_template']
            if '_tpm' in template:
                btemplate = template.replace('_tpm', '')
                apiBody = dict(apiBody, **jsonVars[btemplate])
                apiBody = dict(apiBody, **jsonVars['tpm'])
            else:
                apiBody = dict(apiBody, **jsonVars[template])
                apiBody = dict(apiBody, **jsonVars['tpm_disabled'])
        return apiBody

    #=====================================================
    # Assign VLANs to VLAN Policies
    #=====================================================
    def vlans(self, pargs, **kwargs):
        jsonVars = kwargs['ezData']['policies']['allOf'][1]['properties'][self.type]['key_map']
        #=====================================================
        # Get Policies and Pools
        #=====================================================
        pargs.apiMethod = 'get'
        pargs.names  = []
        pargs.policy = 'multicast'
        for i in pargs.item: pargs.names.append(i['multicast_policy'])
        pargs.names = numpy.unique(numpy.array(pargs.names))
        kwargs = isdk.api('multicast').calls(pargs, **kwargs)
        mcast_moids = kwargs['pmoids']
        pargs.names  = []
        pargs.policy = 'vlans'
        for item in pargs.item:
            vlan_list = ezfunctions.vlan_list_full(item['vlan_list'])
            for i in vlan_list: pargs.names.append(i)
        kwargs = isdk.api('vlan').calls(pargs, **kwargs)
        vlans_moids = kwargs['pmoids']
        vlan_moid = pargs.pmoid
        #=====================================================
        # Create API Body for VNICs
        #=====================================================
        for i in pargs.item:
            vlan_list = ezfunctions.vlan_list_full(i['vlan_list'])
            for x in vlan_list:
                if type(x) == str: x = int(x)
                if len(vlan_list) == 1: apiBody = {'name':i['name']}
                else:
                    if re.search('^[\d]$', str(x)): zeros = '000'
                    elif re.search('^[\d]{2}$', str(x)): zeros = '00'
                    elif re.search('^[\d]{3}$', str(x)): zeros = '0'
                    elif re.search('^[\d]{4}$', str(x)): zeros = ''
                    if i['name'] == 'vlan': apiBody = {'name':f"{i['name']}{zeros}{x}"}
                    else: apiBody = {'name':f"{i['name']}-vl{zeros}{x}"}
                for k, v in i.items():
                    if k in jsonVars: apiBody.update({jsonVars[k]:v})
                if not apiBody.get('auto_allow_on_uplinks'): apiBody.update({'auto_allow_on_uplinks':False})
                apiBody.update({'vlan_id':x})
                apiBody.update({'eth_network_policy':{
                    'class_id':'mo.MoRef','moid':vlan_moid, 'object_type':'fabric.EthNetworkPolicy'
                }})
                if not mcast_moids.get(i['multicast_policy']):
                    validating.error_policy_doesnt_exist(
                        'multicast_policy', i['multicast_policy'], self.type, 'vlan_id', apiBody['vlan_id'])
                mcast_moid = mcast_moids[i['multicast_policy']]['Moid']
                apiBody.update({'multicast_policy':{
                    'class_id':'mo.MoRef', 'moid':mcast_moid, 'object_type':'fabric.MulticastPolicy'
                }})
                #=====================================================
                # Create or Patch the VLANs via the Intersight API
                #=====================================================
                if not vlans_moids.get(x):
                    pargs.apiMethod = 'create'
                    pargs.policy    = 'vlans'
                    pargs.purpose   = 'vlans'
                    pargs.apiBody   = apiBody
                    kwargs = isdk.api('vlans').calls(pargs, **kwargs)
                else:
                    pargs.apiMethod = 'by_moid'
                    pargs.policy    = 'vlans'
                    pargs.purpose   = 'vlans'
                    pargs.pmoid     = vlans_moids[x]['Moid']
                    kwargs = isdk.api('vlans').calls(pargs, **kwargs)
                    r = DotMap(deepcopy(kwargs['results']))
                    patchVlan = False
                    if not apiBody.get('is_native'): native = False
                    else: native = apiBody['is_native']
                    if not r.AutoAllowOnUplinks == apiBody['auto_allow_on_uplinks']: patchVlan = True
                    elif not r.IsNative == native: patchVlan = True
                    elif not r.MulticastPolicy.Moid == apiBody['multicast_policy']['moid']: patchVlan = True
                    if patchVlan == True:
                        pargs.apiMethod = 'patch'
                        pargs.policy = 'vlans'
                        pargs.purpose = 'vlans'
                        pargs.apiBody = apiBody
                        kwargs = isdk.api('vlans').calls(pargs, **kwargs)
                    else: print(f"      * Skipping VLAN {x}.  Intersight Matches Configuration.")
        return kwargs

    #=====================================================
    # Assign VNICs to LAN Connectivity Policies
    #=====================================================
    def vnics(self, pargs, **kwargs):
        jsonVars = kwargs['ezData']['policies']['allOf'][1]['properties'][self.type]
        #=====================================================
        # Get Policies and Pools
        #=====================================================
        lcp_moid = pargs.pmoid
        pargs.apiMethod = 'get'
        for item in jsonVars['policy_list']:
            ptype = (item.replace('_policy', '')).replace('_policies', '')
            pargs.names  = []
            pargs.policy = ptype
            pargs.purpose = ptype
            for i in pargs.item:
                if i.get('iscsi_boot_policies') and ptype == 'iscsi_boot': pargs.names.extend(i[item])
                elif i.get('ethernet_network_group_policies') and ptype == 'ethernet_network_group':
                    pargs.names.extend(i[item])
                elif i.get(item): pargs.names.append(i[item])
                elif i.get('names') and item == 'vnics': pargs.names.extend(i['names'])
                elif i.get('mac_address_pools') and item == 'mac': pargs.names.extend(i['mac_address_pools'])
            pargs.names = numpy.unique(numpy.array(pargs.names))
            kwargs = isdk.api(ptype).calls(pargs, **kwargs)
            pargs.moids[item] = kwargs['pmoids']
        #=====================================================
        # Create API Body for vNICs
        #=====================================================
        for i in pargs.item:
            vnic_count = len(i['names'])
            for x in range(0,vnic_count):
                apiBody = {'name':i['names'][x],'order':i['placement_pci_order'][x]}
                apiBody.update({'class_id':'vnic.EthIf','object_type':'vnic.EthIf'})
                if not i.get('cdn_values'):
                    apiBody.update({'cdn':{'value':i['names'][x],'source':'vnic','object_type':'vnic.Cdn'}})
                else:
                    apiBody.update({
                        'cdn':{'value':i['cdn_values'][x],'source':i['cdn_source'],'object_type':'vnic.Cdn'}
                    })
                for k, v in i.items():
                    if k in jsonVars['key_map']:
                        apiBody.update({jsonVars['key_map'][k]:v})
                policy_list = deepcopy(jsonVars['policy_list'])
                policy_list.remove('mac')
                policy_list.remove('vnics')
                if not i.get('iscsi_boot_policies'): policy_list.remove('iscsi_boot_policies')
                for p in policy_list:
                    pshort = (p.replace('_policy', '')).replace('_policies', '')
                    jVars = kwargs['ezData']['policies']['allOf'][1]['properties'][pshort]
                    if 'iscsi_boot' in p:
                        pname = i[p][x]
                    elif 'network_group' in p:
                        if len(i[p]) == 2: pname = i[p][x]
                        else: pname = i[p][0]
                    else: pname = i[p]
                    if not pargs.moids[p].get(pname):
                        validating.error_policy_doesnt_exist(p, pname, self.type, 'policy', apiBody['name'])
                    if re.search('network_(control|group)', p):
                        oname = 'fabric_' + jVars['object_name']
                    elif 'iscsi' in p: oname = 'iscsi_boot_policy'
                    else: oname = jVars['object_name']
                    pmoid = pargs.moids[p][pname]['Moid']
                    if 'network_group' in p: apiBody.update({oname:[{
                            'class_id':'mo.MoRef','moid':pmoid,'object_type':jVars['object_type']
                        }]})
                    else: apiBody.update({oname:{
                            'class_id':'mo.MoRef','moid':pmoid,'object_type':jVars['object_type']
                        }})
                apiBody.update({'lan_connectivity_policy':{
                    'class_id':'mo.MoRef','moid':lcp_moid,'object_type':'vnic.LanConnectivityPolicy'
                }})
                apiBody.update({
                    'placement':{'id':'MLOM','object_type':'vnic.PlacementSettings','pci_link':0,'uplink':0}
                })
                if i.get('placement_switch_id'):
                    apiBody['placement'].update({'switch_id':i['placement_switch_id']})
                    apiBody.pop('placement_switch_id')
                else:
                    if x == 0: side = 'A'
                    else: side = 'B'
                    apiBody['placement'].update({'switch_id':side})
                place_list = ['placement_pci_links', 'placement_slot_ids', 'placement_uplink_ports']
                for p in place_list:
                    count = 0
                    if i.get(p): apiBody.pop(p); count += 1
                    if count == 1:
                        if len(item[p]) == 2: pval = item[p][x]
                        else: pval = item[p][0]
                        if 'slot' in p: pvar = 'id'
                        pvar = p.replace('placement_', '')
                        pvar = pvar.replace('s', '')
                        apiBody['placement'][pvar] = pval
                if i.get('mac_address_pools'):
                    pname = i['mac_address_pools'][x]
                    ptype = 'mac_address_pool'
                    if not pargs.moids['mac'].get(pname):
                        validating.error_policy_doesnt_exist(ptype, pname, apiBody['name'], self.type, 'Policy')
                    macpool = pargs.moids['mac'][i['mac_address_pools'][x]]['Moid']
                    apiBody.update({
                        'mac_address_type':'POOL',
                        'mac_pool':{
                            'class_id':'mo.MoRef','moid':macpool,'object_type':'macpool.Pool'
                        }
                    })
                #=====================================================
                # Create or Patch the VLANs via the Intersight API
                #=====================================================
                if not pargs.moids.vnics.get(i['names'][x]): pargs.apiMethod = 'create'
                else:
                    pargs.apiMethod = 'patch'
                    pargs.pmoid = pargs.moids.vnics[i['names'][x]]['Moid']
                pargs.policy = 'vnics'
                pargs.purpose = 'vnics'
                pargs.apiBody = apiBody
                kwargs = isdk.api('vnics').calls(pargs, **kwargs)
        return kwargs

    #=======================================================
    # VSAN Policy Modification
    #=======================================================
    def vsan(self, apiBody, item, pargs, **kwargs):
        pargs    = pargs
        jsonVars = kwargs['ezData']['policies']['allOf'][1]['properties']['bios']['template_tuning']
        for k, v in apiBody.items():
            if type(v) == int or type(v) == float: apiBody[k] = str(v)
        if item.get('bios_template'):
            template = item['bios_template']
            if '_tpm' in template:
                btemplate = template.replace('_tpm', '')
                apiBody = dict(apiBody, **jsonVars[btemplate])
                apiBody = dict(apiBody, **jsonVars['tpm'])
            else:
                apiBody = dict(apiBody, **jsonVars[template])
                apiBody = dict(apiBody, **jsonVars['tpm_disabled'])
        return apiBody

    #=====================================================
    # Assign VSANs to VSAN Policies
    #=====================================================
    def vsans(self, pargs, **kwargs):
        jsonVars = kwargs['ezData']['policies']['allOf'][1]['properties'][self.type]['key_map']
        #=====================================================
        # Get Policies and Pools
        #=====================================================
        pargs.apiMethod = 'get'
        pargs.names  = []
        pargs.policy = 'vsans'
        vsan_moid = pargs.pmoid
        for i in pargs.item: pargs.names.append(str(i['vsan_id']))
        kwargs = isdk.api('vsans').calls(pargs, **kwargs)
        vsans_moids = kwargs['pmoids']
        for i in pargs.item:
                #=====================================================
                # Create API Body for the VSANs
                #=====================================================
                apiBody = {'fc_network_policy':{
                    'class_id':'mo.MoRef','moid':vsan_moid,'object_type':'fabric.FcNetworkPolicy'}}
                for k, v in i.items():
                    if k in jsonVars: apiBody.update({jsonVars[k]:v})
                if not apiBody.get('fcoe_vlan'): apiBody.update({'fcoe_vlan':i['vsan_id']})
                #=====================================================
                # Create or Patch the VSANs via the Intersight API
                #=====================================================
                if not vsans_moids.get(i['vsan_id']): pargs.apiMethod = 'create'
                else:
                    pargs.apiMethod = 'patch'
                    pargs.pmoid = vsans_moids[i['vsan_id']]['Moid']
                pargs.policy = 'vsans'
                pargs.purpose = 'vsans'
                pargs.apiBody = apiBody
                kwargs = isdk.api('vsans').calls(pargs, **kwargs)
        return kwargs

#=======================================================
# Pools Class
#=======================================================
class api_pools(object):
    def __init__(self, type):
        self.type = type
    #=======================================================
    # WWNN/WWPN ID Block Modification
    #=======================================================
    def fc(item, apiBody):
        if item.get('id_blocks'):
            apiBody.update({'IdBlocks':[]})
            for i in item['id_blocks']:
                apiBody['IdBlocks'].append({
                    'From':i['from'], 'ObjectType':'fcpool.Block', 'Size':i['size']
                })
        return apiBody

    #=======================================================
    # IP Block(s)/Configuration Modification
    #=======================================================
    def ip(item, apiBody):
        ip_list = ['IpV4', 'IpV6']
        for x in ip_list:
            xlower = x.lower()
            if item.get(f'{xlower}_blocks'):
                apiBody.update({f'{x}Blocks':[]})
                for i in item[f'{xlower}_blocks']:
                    apiBody[f'{x}Blocks'].append({
                        'From':i['from'], 'ObjectType':f'ippool.{x}Block', 'Size':i['size']
                    })
            if item.get(f'{xlower}_configuration'):
                ipcfg = item[f'{xlower}_configuration'][0]
                apiBody.update({f'{x}Config':{
                    'Gateway':ipcfg['gateway'], 'ObjectType':f'ippool.{x}Config',
                    'PrimaryDns':ipcfg['primary_dns'], 'SecondaryDns':ipcfg['secondary_dns']
                }})
                if '4' in xlower: apiBody[f'{x}Config'].update({'Netmask':ipcfg['netmask']})
                else: apiBody[f'{x}Config'].update({'Prefix':ipcfg['prefix']})
        return apiBody

    #=======================================================
    # IQN Block(s)/Configuration Modification
    #=======================================================
    def iqn(item, apiBody):
        if item.get('iqn_blocks'):
            apiBody.update({'IqnSuffixBlocks':[]})
            for i in item['iqn_blocks']:
                apiBody['IqnSuffixBlocks'].append({
                    'From':i['from'], 'ObjectType':'iqnpool.Block', 'Size':i['size'], 'Suffix':i['suffix']
                })
        return apiBody

    #=======================================================
    # MAC Block Modification
    #=======================================================
    def mac(item, apiBody):
        if item.get('mac_blocks'):
            apiBody.update({'MacBlocks':[]})
            for i in item['mac_blocks']:
                apiBody['MacBlocks'].append({
                    'From':i['from'], 'ObjectType':'macpool.Block', 'Size':i['size']
                })
        return apiBody

    #=====================================================
    #  Pools Function
    #=====================================================
    def pools(self, pargs, **kwargs):
        #=====================================================
        # Load Variables and Send Begin Notification
        #=====================================================
        if re.search('ww(n|p)n', self.type):
            jsonVars = kwargs['ezData']['pools']['allOf'][1]['properties']['fc']['key_map']
        else: jsonVars = kwargs['ezData']['pools']['allOf'][1]['properties'][self.type]['key_map']
        pools = kwargs['immDict']['orgs'][kwargs['org']]['pools'][self.type]
        org_moid = kwargs['org_moids'][kwargs['org']]['Moid']
        validating.begin_section(self.type, 'pool')
        #=====================================================
        # Get Existing Pools
        #=====================================================
        pargs.names = []
        for i in pools: pargs.names.append(i['name'])
        pargs.apiMethod = 'get'
        pargs.policy    = self.type
        pargs.purpose   = self.type
        kwargs = isdk.api(self.type).calls(pargs, **kwargs)
        #=====================================================
        # Loop through Items
        #=====================================================
        for item in pools:
            #=====================================================
            # Construct apiBody Payload
            #=====================================================
            apiBody = {}
            for k, v in item.items():
                if k in jsonVars: apiBody.update({jsonVars[k]:v})
            if not apiBody.get('assignment_order'): apiBody.update({'assignment_order':'sequential'})
            apiBody = org_map(apiBody, org_moid)
            if apiBody.get('tags'): apiBody['tags'].append(kwargs['ezData']['tags'])
            else: apiBody.update({'tags':[kwargs['ezData']['tags']]})
            #=====================================================
            # Add Pool Specific Attributes
            #=====================================================
            if re.search('ww(n|p)n', self.type): 
                apiBody.update({'pool_purpose':self.type.upper()})
                apiBody = api_pools.fc(item, apiBody)
            else: apiBody = eval(f'api_pools.{self.type}')(item, apiBody)
            #=====================================================
            # Create/Patch the Pool via the Intersight API
            #=====================================================
            pargs.apiBody = apiBody
            if kwargs['pmoids'].get(apiBody['name']):
                pargs.apiMethod = 'patch'
                pargs.pmoid = kwargs['pmoids'][apiBody['name']]['Moid']
            else: pargs.apiMethod = 'create'
            kwargs = isdk.api(self.type).calls(pargs, **kwargs)
        #=====================================================
        # Send End Notification and return kwargs
        #=====================================================
        validating.end_section(self.type, 'pool')
        return kwargs

    #=======================================================
    # UUID Block Modification
    #=======================================================
    def uuid(item, apiBody):
        if item.get('uuid_blocks'):
            apiBody.update({'UuidSuffixBlocks':[]})
            for i in item['uuid_blocks']:
                apiBody['UuidSuffixBlocks'].append({
                    'From':i['from'], 'ObjectType':'uuidpool.UuidBlock', 'Size':i['size']
                })
        return apiBody

#=======================================================
# Profiles Class
#=======================================================
class api_profiles(object):
    def __init__(self, type):
        self.type = type

    #=====================================================
    #  Profiles Function
    #=====================================================
    def profiles(self, pargs, **kwargs):
        #=====================================================
        # Load Variables and Send Begin Notification
        #=====================================================
        jsonVars = kwargs['ezData']['profiles']['allOf'][1]['properties'][self.type]['policy_list']
        if 'templates' == self.type:
            profiles = kwargs['immDict']['orgs'][kwargs['org']][self.type]['server']
        else: profiles = kwargs['immDict']['orgs'][kwargs['org']]['profiles'][self.type]
        if 'server' == self.type:
            templates = {}
            if kwargs['immDict']['orgs'][kwargs['org']].get('templates'):
                for item in kwargs['immDict']['orgs'][kwargs['org']]['templates']['server']:
                    templates.update({item['name']:item})
        pargs.org_moid = kwargs['org_moids'][kwargs['org']]['Moid']
        validating.begin_section(self.type, 'profiles')
        #=====================================================
        # Setup Arguments
        #=====================================================
        pargs.apiMethod = 'get'
        pargs.jsonVars  = jsonVars
        pargs.names     = []
        pargs.policies  = {}
        pargs.purpose   = self.type
        pargs.serials   = []
        pargs.templates = []
        #=================================
        # Compile List of Serial Numbers
        #=================================
        for item in profiles:
            if re.search('^(chassis|server)$', self.type):
                if 'server' == self.type:
                    if item.get('ucs_server_profile_template'):
                        pargs.templates.append(item['ucs_server_profile_template'])
                        pargs.template = item['ucs_server_profile_template']
                for i in item['targets']:
                    pargs.names.append(i['name'])
                    if i.get('serial_number'): pargs.serials.append(i['serial_number'])
            else:
                pargs.names.append(item['name'])
                if item.get('serial_numbers'): pargs.serials.extend(item['serial_numbers'])
        #==================================
        # Get Moids for Profiles/Templates
        #==================================
        pargs.moids = {}
        pargs.apiMethod = 'get'
        if 'domain' in self.type: pargs.policy = 'cluster'
        else: pargs.policy = self.type
        kwargs = isdk.api(self.type).calls(pargs, **kwargs)
        pargs.moids[self.type] = kwargs['pmoids']
        if len(pargs.templates) > 0:
            pargs.names  = numpy.unique(numpy.array(pargs.templates))
            pargs.policy = 'templates'
            kwargs = isdk.api('templates').calls(pargs, **kwargs)
            pargs.moids['templates'] = kwargs['pmoids']
        if 'domain' in self.type:
            clusters = pargs.names
            pargs.policy = 'switch'
            pargs.names = []
            pargs.fabrics = ['A', 'B']
            pargs.moids['switch'] = {}
            for c in clusters:
                if pargs.moids[self.type].get(c):
                    for x in range(0,len(pargs.fabrics)): pargs.names.append(f'{c}-{pargs.fabrics[x]}')
                    pargs.pmoid = pargs.moids[self.type][c]['Moid']
                    kwargs = isdk.api('switch').calls(pargs, **kwargs)
                    pargs.moids['switch'].update(kwargs['pmoids'])
        #=================================
        # Compile List of Policy Moids
        #=================================
        for p in jsonVars:
            pargs.names = []
            for item in profiles:
                if item.get(p):
                    if 'policies' in item[p]:
                        for i in item[p]: pargs.names.append(i)
                    else: pargs.names.append(item[p])
                if item.get('ucs_server_profile_template'):
                    spt = item['ucs_server_profile_template']
                    if templates[spt].get(p):
                        pargs.names.append(templates[spt][p])
            pargs.names = numpy.unique(numpy.array(pargs.names))
            ptype = ((p.replace('_policy', '')).replace('_pool', '')).replace('_policies', '')
            pargs.apiMethod = 'get'
            pargs.policy = ptype
            pargs.purpose = ptype
            kwargs = isdk.api(ptype).calls(pargs, **kwargs)
            pargs.moids[p] = deepcopy(kwargs['pmoids'])
        #========================================
        # Get Serial Moids
        #========================================
        pargs.purpose = self.type
        if len(pargs.serials) > 0:
            pargs.policy = 'serial_number'
            pargs.names = pargs.serials
            kwargs = isdk.api('serial_number').calls(pargs, **kwargs)
            pargs.serial_moids = kwargs['pmoids']
        #=====================================================
        # Create the Profiles with the Functions
        #=====================================================
        pargs.type = self.type
        for item in profiles:
            if re.search('^(chassis|server)$', self.type):
                for i in item['targets']:
                    if pargs.description: pargs.pop('description')
                    if pargs.serial_number: pargs.pop('serial_number')
                    pargs.name = i['name']
                    if i.get('description'): pargs.description = i['description']
                    if i.get('serial_number'): pargs.serial_number = i['serial_number']
                    if item.get('ucs_server_profile_template'):
                        i.update({'ucs_server_profile_template':item['ucs_server_profile_template']})
                        if not pargs.moids['templates'].get(i['ucs_server_profile_template']):
                            ptype = 'ucs_server_profile_template'
                            tname = i['ucs_server_profile_template']
                            validating.error_policy_doesnt_exist(ptype, tname, pargs.name, pargs.type, 'Profile')
                        pargs.template_policies = templates[i['ucs_server_profile_template']]
                        if item.get('create_from_template'): i.update({'create_from_template':item['create_from_template']})
                    for p in jsonVars:
                        if item.get(p): i.update({p:item[p]})
                    kwargs, pargs = profile_function(i, pargs, **kwargs)
                    pargs.moids[self.type].update({pargs.name:{'Moid':pargs.pmoid}})
            elif re.search('^(domain)$', self.type):
                if pargs.description: pargs.pop('description')
                if pargs.serial_number: pargs.pop('serial_number')
                pargs.name = item['name']
                if item.get('description'): pargs.description = item['description']
                if item.get('serial_numbers'): pargs.serial_numbers = item['serial_numbers']
                profile_domain(item, pargs, **kwargs)
            elif 'templates' == self.type:
                if pargs.description: pargs.pop('description')
                if pargs.serial_number: pargs.pop('serial_number')
                pargs.name = item['name']
                if item.get('description'): pargs.description = item['description']
                if item.get('serial_number'): pargs.serial_number = item['serial_number']
                kwargs, pargs = profile_function(item, pargs, **kwargs)
                pargs.moids[self.type].update({pargs.name:{'Moid':pargs.pmoid}})
        #========================================================
        # If chassis or Server Watch Results if action is Deploy
        #========================================================
        deploy_profiles = False
        if re.search('^domain$', self.type):
            for item in profiles:
                if item.get('action'):
                    for x in range(0,len(pargs.fabrics)):
                        if item['action'] == 'Deploy' and re.search(serial_regex, item['serial_numbers'][x]):
                            if deploy_profiles == False:
                                deploy_profiles = True
                                print(f'\n{"-"*81}\n')
                            pname = f"{item['name']}-{pargs.fabrics[x]}"
                            print(f'    - Beginning Profile Deployment for {pname}')
                            pargs.apiBody   = {'action':'Deploy'}
                            pargs.apiMethod = 'patch'
                            pargs.pmoid     = pargs.moids['switch'][pname]['Moid']
                            pargs.policy    = 'switch'
                            pargs.purpose   = self.type
                            kwargs = isdk.api('switch').calls(pargs, **kwargs)
            if deploy_profiles == True:
                print(f'\n{"-"*81}\n')
                time.sleep(60)
            for item in profiles:
                if item.get('action'):
                    for x in range(0,len(pargs.fabrics)):
                        if item['action'] == 'Deploy' and re.search(serial_regex, item['serial_numbers'][x]):
                            pname = f"{item['name']}-{pargs.fabrics[x]}"
                            pargs.apiMethod = 'by_moid'
                            pargs.pmoid     = pargs.moids['switch'][pname]['Moid']
                            pargs.policy    = 'switch'
                            pargs.purpose   = self.type
                            deploy_complete = False
                            while deploy_complete == False:
                                kwargs = isdk.api('switch').calls(pargs, **kwargs)
                                if kwargs['results']['ConfigContext']['ControlAction'] == 'No-op':
                                    deploy_complete = True
                                    pname = item['name']
                                    print(f'    - Completed Profile Deployment for {pname}')
                                else: 
                                    print(f'      * Deploy Still Occuring on {pname}.  Waiting 120 seconds.')
                                    #validating.deploy_notification(self.type, pname)
                                    time.sleep(120)
            if deploy_profiles == True:
                print(f'\n{"-"*81}\n')
        #========================================================
        # If chassis or Server Watch Results if action is Deploy
        #========================================================
        if re.search('^(chassis|server)$', self.type):
            for item in profiles:
                for i in item['targets']:
                    if item.get('action'):
                        if item['action'] == 'Deploy' and re.search(serial_regex, i['serial_number']):
                            if deploy_profiles == False:
                                deploy_profiles = True
                                print(f'\n{"-"*81}\n')
                            pname = i['name']
                            print(f'    - Beginning Profile Deployment for {pname}')
                            pargs.apiMethod = 'patch'
                            pargs.policy = self.type
                            pargs.pmoid = pargs.moids[self.type][pname]['Moid']
                            pargs.apiBody = {'action':'Deploy'}
                            kwargs = isdk.api(self.type).calls(pargs, **kwargs)
            if deploy_profiles == True:
                print(f'\n{"-"*81}\n')
                time.sleep(60)
            for item in profiles:
                for i in item['targets']:
                    if item.get('action'):
                        if item['action'] == 'Deploy' and re.search(serial_regex, i['serial_number']):
                            pname           = i['name']
                            deploy_profiles = True
                            deploy_complete = False
                            while deploy_complete == False:
                                pargs.apiMethod = 'by_moid'
                                pargs.pmoid     = pargs.moids[self.type][pname]['Moid']
                                pargs.policy    = self.type
                                pargs.purpose   = self.type
                                kwargs = isdk.api(self.type).calls(pargs, **kwargs)
                                if kwargs['results']['ConfigContext']['ControlAction'] == 'No-op':
                                    deploy_complete = True
                                    print(f'    - Completed Profile Deployment for {pname}')
                                else: 
                                    print(f'      * Deploy Still Occuring on {pname}.  Waiting 120 seconds.')
                                    validating.deploy_notification(self.type, pname)
                                    time.sleep(120)
            if deploy_profiles == True:
                print(f'\n{"-"*81}\n')
        #========================================================
        # End Function and return kwargs
        #========================================================
        validating.end_section(self.type, 'profiles')
        return kwargs

#=======================================================
# Add Organization Key Map to Dictionaries
#=======================================================
def org_map(apiBody, org_moid):
    apiBody.update({
        'organization':{
            'class_id':'mo.MoRef',
            'moid':org_moid,
            'object_type':'organization.Organization'
            }
        })
    return apiBody

#=======================================================
# Domain Profile Creation Function
#=======================================================
def profile_domain(item, pargs, **kwargs):
    #=====================================================
    # Build apiBody
    #=====================================================
    apiBody = {'name':pargs.name}
    if pargs.get('description'): apiBody.update({'description':pargs.get('description')})
    apiBody = org_map(apiBody, pargs.org_moid)
    apiBody.update({'object_type':'fabric.SwitchClusterProfile'})
    #=====================================================
    # Create/Patch the Profile via the Intersight API
    #=====================================================
    pargs.apiBody = apiBody
    pargs.policy  = 'cluster'
    pargs.purpose = pargs.type
    if pargs.moids[pargs.type].get(apiBody['name']):
        pargs.apiMethod = 'patch'
        pargs.pmoid = pargs.moids[pargs.type][apiBody['name']]['Moid']
    else: pargs.apiMethod = 'create'
    kwargs = isdk.api('cluster').calls(pargs, **kwargs)
    cluster_moid = kwargs['pmoid']
    #=====================================================
    # Build apiBody for Switch Profiles
    #=====================================================
    sw_names = []
    for x in range(0,len(pargs.fabrics)):
        sw_name = f"{item['name']}-{pargs.fabrics[x]}"
        sw_names.append(sw_name)
        apiBody = {'class_id':'fabric.SwitchProfile', 'object_type':'fabric.SwitchProfile'}
        apiBody.update({'name':sw_name})
        apiBody.update({'SwitchClusterProfile':{
            'class_id':'mo.MoRef','moid':cluster_moid,'object_type':'fabric.SwitchClusterProfile'
        }})
        if item.get('serial_numbers'):
            if re.search(serial_regex, item['serial_numbers'][x]): serial_true = True
            else: serial_true = False
        if serial_true == True:
            serial_true += 1
            if pargs.serial_moids.get(item['serial_numbers'][x]):
                serial_moid = pargs.serial_moids[item['serial_numbers'][x]]['Moid']
            else: validating.error_serial_number(sw_name, item['serial_numbers'][x])
            apiBody.update({'AssignedSwitch':{
                'class_id':'mo.MoRef','moid':serial_moid,'object_type':'network.Element'
            }})
        pargs.apiBody = apiBody
        pargs.policy  = 'switch'
        pargs.purpose = pargs.type
        if pargs.moids['switch'].get(apiBody['name']):
            pargs.apiMethod = 'patch'
            pargs.pmoid = pargs.moids['switch'][apiBody['name']]['Moid']
        else: pargs.apiMethod = 'create'
        kwargs = isdk.api('switch').calls(pargs, **kwargs)
        pargs.moids['switch'][sw_name] = {'Moid':kwargs['pmoid']}
    #=====================================================
    # Attach Switch Profiles to the Policies
    #=====================================================
    profiles = []
    for i in range(0,len(sw_names)):
        profile_moid = pargs.moids['switch'][sw_names[i]]['Moid']
        profiles.append({'class_id':'mo.MoRef','moid':profile_moid,'object_type':'fabric.SwitchProfile'})
    #=====================================================
    # Get Policy Moid and Data
    #=====================================================
    def get_pdict(item, p, policy_name):
        if not pargs.moids[p].get(policy_name):
            validating.error_policy_doesnt_exist(p, policy_name, item['name'], 'Domain', 'Profile')
        pdict = pargs.moids[p][policy_name]
        return pdict
    #=====================================================
    # Update the Policy Objects
    #=====================================================
    def update_policy(p, pargs, **kwargs):
        apiBody = {'profiles':pargs.result}
        jsonVars = kwargs['ezData']['policies']['allOf'][1]['properties'][pargs.ptype]
        apiBody.update({'object_type':jsonVars['object_type']})
        apiBody.update({'name':pargs.name})
        pargs.pmoid = pargs.moids[p][pargs.name]['Moid']
        pargs.apiBody   = apiBody
        pargs.apiMethod = 'patch'
        pargs.policy    = pargs.ptype
        pargs.purpose   = 'switch'
        kwargs = isdk.api(pargs.ptype).calls(pargs, **kwargs)
        return kwargs, pargs
    #=====================================================
    # Attach Policies to the Domain Switch Profiles
    #=====================================================
    for p in pargs.jsonVars:
        pargs.ptype = ((p.replace('_policy', '')).replace('_pool', '')).replace('_policies', '')
        add_to_policy = False
        if item.get(p):
            if len(item[p]) > 0: add_to_policy = True
        if add_to_policy == True:
            if type(item[p]) == list:
                for x in range(0,len(item[p])):
                    pdict       = get_pdict(item, p, item[p][x])
                    pargs.name  = item[p][x]
                    pargs.pmoid = pdict['Moid']
                    if pdict.get('profiles'): pol_profiles = pdict['profiles']
                    else: pol_profiles = []
                    if len(item[p]) == 2: pol_profiles.append(profiles[x])
                    else: pol_profiles.extend(profiles)
                    pargs.result = []
                    for z in pol_profiles:
                        if z not in pargs.result: pargs.result.append(z)
                    kwargs, pargs = update_policy(p, pargs, **kwargs)
            else:
                pdict       = get_pdict(item, p, item[p])
                pargs.name  = item[p]
                pargs.pmoid = pdict['Moid']
                if pdict.get('profiles'): pol_profiles = pdict['profiles']
                else: pol_profiles = []
                pol_profiles.extend(profiles)
                pargs.result = []
                for z in pol_profiles:
                    if z not in pargs.result: pargs.result.append(z)
                kwargs, pargs = update_policy(p, pargs, **kwargs)
    # Retrun to profiles Module
    return kwargs, pargs

#=======================================================
# Profile Creation Function
#=======================================================
def profile_function(item, pargs, **kwargs):
    #=====================================================
    # Build apiBody
    #=====================================================
    apiBody = {'name':pargs.name}
    if pargs.get('description'): apiBody.update({'description':pargs.get('description')})
    apiBody = org_map(apiBody, pargs.org_moid)
    if pargs.type == 'templates': apiBody.update({'object_type':'server.ProfileTemplate'})
    elif pargs.type == 'server':  apiBody.update({'object_type':'server.Profile'})
    elif pargs.type == 'chassis': apiBody.update({'object_type':'chassis.Profile'})
    serial_true = False
    if pargs.get('serial_number'):
        if re.search(serial_regex, pargs.serial_number): serial_true = True
        else: serial_true = False
    if serial_true == True:
        if pargs.serial_moids.get(pargs.serial_number):
            serial_moid = pargs.serial_moids[pargs.serial_number]['Moid']
            sobject     = pargs.serial_moids[pargs.serial_number]['object_type']
        else: validating.error_serial_number(pargs.name, serial_moid)
        apiBody.update({f'assigned_{pargs.type}':{
            'class_id': 'mo.MoRef', 'moid':serial_moid, 'object_type':sobject
        }})
    #=================================================================
    # Determine if Policy Bucket Should be Utilized
    # For Server Profile Determine if Policy is Sourced from Template
    #=================================================================
    create_from_template = False
    policy_bucket = False
    server_template = ''
    if re.search('(chassis|templates)', pargs.type): policy_bucket = True
    elif pargs.type == 'server':
        if item.get('create_from_template'):
            if item['create_from_template'] == True:
                create_from_template = True
            else: policy_bucket = True
        else: policy_bucket = True
        if item.get('ucs_server_profile_template'):
            server_template = item['ucs_server_profile_template']
    #=====================================================
    # Attach Server Template to Server if Defined
    #=====================================================
    if len(server_template) > 0 and create_from_template == True:
        tmoid = pargs.moids['templates'][server_template]['Moid']
        bulkBody = {
            'class_id': 'bulk.MoCloner', 'object_type': 'bulk.MoCloner',
            'sources':[{'class_id': 'server.ProfileTemplate', 'moid':tmoid,'object_type':'server.ProfileTemplate'}],
            'targets':[{'class_id': 'server.Profile', 'moid': '', 'name':apiBody['name'],'object_type':'server.Profile'}]
        }
        #=====================================================
        # Create the Profile from the Template
        #=====================================================
        print(json.dumps(bulkBody, indent=4))
        if not pargs.moids[pargs.type].get(apiBody['name']):
            pargs.apiBody   = bulkBody
            pargs.apiMethod = 'create'
            pargs.policy    = 'bulk'
            pargs.purpose   = 'bulk'
            kwargs = isdk.api('bulk').calls(pargs, **kwargs)
            pargs.moids['server'].update({apiBody['name']:{'Moid':kwargs['pmoid']}})
    #=================================================================
    # Add Policies to the Policy Bucket if not deployed from Template
    #=================================================================
    if pargs.type == 'templates' or (pargs.type == 'server' and create_from_template == False):
        if item.get('target_platform'):
            apiBody.update({'target_platform':item['target_platform']})
        else: apiBody.update({'target_platform':'FIAttached'})
    if policy_bucket == True:
        if 'uuid_pool' in pargs.jsonVars: pargs.jsonVars.remove('uuid_pool')
        for p in pargs.jsonVars:
            pshort = p.replace('_policy', '')
            pObject = kwargs['ezData']['policies']['allOf'][1]['properties'][pshort]['object_type']
            add_policy = False
            if item.get(p):
                if len(item[p]) > 0:
                    add_policy = True
                    pname = item[p]
            elif pargs.get('template_policies'):
                if pargs.template_policies.get(p):
                    if len(pargs.template_policies[p]) > 0:
                        add_policy = True
                        pname = pargs.template_policies[p]
            if add_policy == True:
                if not apiBody.get('policy_bucket'): apiBody.update({'policy_bucket':[]})
                if not pargs.moids[p].get(pname):
                    validating.error_policy_doesnt_exist(p, pname, pargs.name, pargs.type, 'Profile')
                pmoid = pargs.moids[p][pname]['Moid']
                pbucket = {'class_id':'mo.MoRef', 'moid':pmoid,'object_type':pObject}
                apiBody['policy_bucket'].append(pbucket)
    #=====================================================
    # Attach UUID Pool if it Exists
    #=====================================================
    add_policy = False
    p = 'uuid_pool'
    if item.get('uuid_pool') and create_from_template == False:
        if len(item[p]) > 0:
            add_policy = True
            pname = item[p]
    elif create_from_template == False:
        if pargs.get('template_policies'):
            if pargs.template_policies.get(p):
                if len(pargs.template_policies[p]) > 0:
                    add_policy = True
                    pname = pargs.template_policies[p]
        elif item.get(p):
            if len(item[p]) > 0:
                add_policy = True
                pname = item[p]
    if add_policy == True:
        pshort = p.replace('_pool', '')
        if not pargs.moids[p].get(pname):
            validating.error_policy_doesnt_exist(p, pname, pargs.name, pargs.type, 'Profile')
        pmoid = pargs.moids[p][pname]['Moid']
        pObject = kwargs['ezData']['pools']['allOf'][1]['properties'][pshort]['object_type']
        apiBody.update({'uuid_address_type':'POOL'})
        apiBody.update({p:{'class_id': 'mo.MoRef', 'moid':pmoid, 'object_type':pObject}})
    #=====================================================
    # Create/Patch the Profile via the Intersight API
    #=====================================================
    pargs.apiBody = apiBody
    pargs.policy  = pargs.type
    pargs.purpose = pargs.type
    if pargs.moids[pargs.type].get(apiBody['name']):
        pargs.apiMethod = 'patch'
        pargs.pmoid = pargs.moids[pargs.type][apiBody['name']]['Moid']
    else: pargs.apiMethod = 'create'
    kwargs = isdk.api(pargs.type).calls(pargs, **kwargs)
    pargs.pmoid = kwargs['pmoid']
    return kwargs, pargs
