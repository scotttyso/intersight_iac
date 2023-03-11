from intersight.api import access_api
from intersight.api import adapter_api
from intersight.api import bios_api
from intersight.api import boot_api
from intersight.api import certificatemanagement_api
from intersight.api import deviceconnector_api
from intersight.api import fabric_api
from intersight.api import fcpool_api
from intersight.api import iam_api
from intersight.api import ipmioverlan_api
from intersight.api import ippool_api
from intersight.api import kvm_api
from intersight.api import macpool_api
from intersight.api import memory_api
from intersight.api import networkconfig_api
from intersight.api import ntp_api
from intersight.api import organization_api
from intersight.api import power_api
from intersight.api import resourcepool_api
from intersight.api import smtp_api
from intersight.api import snmp_api
from intersight.api import sol_api
from intersight.api import ssh_api
from intersight.api import storage_api
from intersight.api import syslog_api
from intersight.api import thermal_api
from intersight.api import uuidpool_api
from intersight.api import vmedia_api
from intersight.api import vnic_api
from intersight.exceptions import ApiException
import credentials
import json
import re
import sys
import urllib3
import validating
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Global options for debugging
print_payload = False
print_response_always = False
print_response_on_fail = True

class isdk_pools(object):
    def __init__(self, type):
        self.type = type

    #=====================================================
    # Parse API Results
    #=====================================================
    def api_results(self, apiQuery):
        api_dict = {}
        api_list = []
        empty = False
        if apiQuery.get('Results'):
            for i in apiQuery['Results']:
                iMoid = i['Moid']
                if i.get('Name'): iName = i['Name']
                elif i.get('PcId'): iName = i['PcId']
                elif i.get('PortIdStart'): iName = i['PortIdStart']
                elif i.get('PortId'): iName = i['PortId']
                api_dict.update({iName:{'Moid':iMoid}})
                if i.get('Profiles'):
                    api_dict[iName]['profiles'] = []
                    for x in i['Profiles']:
                        xdict = {'class_id':'mo.MoRef','moid':x['Moid'],'object_type':x['ObjectType']}
                        api_dict[iName]['profiles'].append(xdict)
                api_list.append(iName)
            return empty, api_dict, api_list
        else:
            empty = True
            return empty, api_dict, api_list

    #=====================================================
    # Return Error When apiQuery Returns Empty Results
    #=====================================================
    def empty_results(self, apiQuery):
            print(f"The API Query Results were empty for {apiQuery['ObjectType']}.  Exiting...")
            sys.exit(1)

    #=====================================================
    # Create/Patch WWNN/WWPN Pools
    #=====================================================
    def fc(self, **kwargs):
        #=====================================================
        # Load Kwargs from Main
        #=====================================================
        args      = kwargs['args']
        dpools    = {}
        jsonVars  = kwargs['ezData']['policies']['allOf'][1]['properties']
        home      = kwargs['home']
        org       = kwargs['org']
        org_moids = kwargs['org_moids']
        if self.type == 'WWPN': pools = kwargs['immDict']['orgs'][org]['pools']['wwpn']
        else: pools = kwargs['immDict']['orgs'][org]['pools']['wwnn']
        #=====================================================
        # Login to Intersight API
        #=====================================================
        api_client = credentials.config_credentials(home, args)
        api_handle = fcpool_api.FcpoolApi(api_client)
        validating.begin_section(self.type)
        for item in pools:
            pname = item['name']
            org_moid = org_moids[org]['Moid']
            #=====================================================
            # Confirm if the Pool Already Exists
            #=====================================================
            get_policy = api_handle.get_fcpool_pool_list
            empty, fc_pools = isdk_pools('get').get_api(get_policy, pname, org_moid)
            #=====================================================
            # Construct API Body Payload
            #=====================================================
            api_body = {}
            if item.get('assignment_order'): api_body.update({'assignment_order':item['assignment_order']})
            else: api_body.update({'assignment_order':'sequential'})
            api_body.update({'class_id':'fcpool.Pool', 'name':item['name'], 'object_type':'fcpool.Pool'})
            if item.get('description'): api_body.update({'description':item.get('description')})
            api_body.update({'pool_purpose':self.type})
            if item.get('id_blocks'):
                api_body.update({'IdBlocks':[]})
                for i in item['id_blocks']:
                    api_body['IdBlocks'].append({
                        'ClassId':'fcpool.Block', 'ObjectType':'fcpool.Block',
                        'From':i['from'], 'Size':i['size']
                    })
            api_body.update({'organization':{
                'class_id':'mo.MoRef','moid':org_moid,'object_type':'organization.Organization'
            }})
            if item.get('tags'):
                api_body.update({'tags':item['tags']})
                api_body['tags'].append(jsonVars['tags'])
            else: api_body.update({'tags':[jsonVars['tags']]})
            #=====================================================
            # Create the Pool via the Intersight API
            #=====================================================
            try:
                if empty == True:
                    api_method = 'create'
                    api_args = dict(_preload_content = False)
                    api_call = json.loads(api_handle.create_fcpool_pool(api_body, **api_args).data)
                    pol_moid = api_call['Moid']
                    if print_response_always == True: print(json.dumps(api_call, indent=4))
                    validating.completed_item(self.type, item['name'], api_method, pol_moid)
                else:
                    pol_moid = fc_pools[item['name']]['Moid']
                    print(f"    - Skipped name: {item['name']}, pool already exists. - Moid: {pol_moid}")
                dpools.update({item['name']:pol_moid})
            except ApiException as e:
                print("Exception when calling FcpoolApi->create_fcpool_pool: %s\n" % e)
                sys.exit(1)
        validating.end_section(self.type)
        return dpools

    #=====================================================
    # Get Policies, Pools, and Profiles from API
    #=====================================================
    def get_api(self, get_policy, pname, org_moid):
        if pname == 'ALLP': query_filter = f"Organization.Moid eq '{org_moid}'"
        else:  query_filter = f"Name eq '{pname}' and Organization.Moid eq '{org_moid}'"
        query_args   = dict(filter=query_filter, _preload_content = False)
        api_query    = json.loads(get_policy(**query_args).data)
        empty, policies, policy_names = isdk_pools('api_results').api_results(api_query)
        return empty, policies
    
    #=====================================================
    # Get Defined List of Policies from API
    #=====================================================
    def get_api_policy_list(self, api_client, org_moid, policy_list, **kwargs):
        for policy in policy_list:
            if policy == 'adapter_configuration_policy':
                api_handle = adapter_api.AdapterApi(api_client)
                get_policy = api_handle.get_adapter_config_policy_list
            elif policy == 'bios_policy':
                api_handle = bios_api.BiosApi(api_client)
                get_policy = api_handle.get_bios_policy_list
            elif policy == 'boot_order_policy':
                api_handle = boot_api.BootApi(api_client)
                get_policy = api_handle.get_boot_precision_policy_list
            elif policy == 'certificate_management_policy':
                api_handle = certificatemanagement_api.CertificatemanagementApi(api_client)
                get_policy = api_handle.get_certificatemanagement_policy_list
            elif policy == 'device_connector_policy':
                api_handle = deviceconnector_api.DeviceconnectorApi(api_client)
                get_policy = api_handle.get_deviceconnector_policy_list
            elif policy == 'imc_access_policy':
                api_handle = access_api.AccessApi(api_client)
                get_policy = api_handle.get_access_policy_list
            elif policy == 'ipmi_over_lan_policy':
                api_handle = ipmioverlan_api.IpmioverlanApi(api_client)
                get_policy = api_handle.get_ipmioverlan_policy_list
            elif policy == 'lan_connectivity_policy':
                api_handle = vnic_api.VnicApi(api_client)
                get_policy = api_handle.get_vnic_lan_connectivity_policy_list
            elif policy == 'ldap_policy':
                api_handle = iam_api.IamApi(api_client)
                get_policy = api_handle.get_iam_ldap_policy_list
            elif policy == 'local_user_policy':
                api_handle = iam_api.IamApi(api_client)
                get_policy = api_handle.get_iam_end_point_user_policy_list
            elif policy == 'network_connectivity_policy':
                api_handle = networkconfig_api.NetworkconfigApi(api_client)
                get_policy = api_handle.get_networkconfig_policy_list
            elif policy == 'ntp_policy':
                api_handle = ntp_api.NtpApi(api_client)
                get_policy = api_handle.get_ntp_policy_list
            elif policy == 'persistent_memory_policy':
                api_handle = memory_api.MemoryApi(api_client)
                get_policy = api_handle.get_memory_persistent_memory_policy_list
            elif policy == 'port_policies':
                api_handle = fabric_api.FabricApi(api_client)
                get_policy = api_handle.get_fabric_port_policy_list
            elif policy == 'power_policy':
                api_handle = power_api.PowerApi(api_client)
                get_policy = api_handle.get_power_policy_list
            elif policy == 'resource_pool':
                api_handle = resourcepool_api.ResourcepoolApi(api_client)
                get_policy = api_handle.get_resourcepool_pool_list
            elif policy == 'san_connectivity_policy':
                api_handle = vnic_api.VnicApi(api_client)
                get_policy = api_handle.get_vnic_san_connectivity_policy_list
            elif policy == 'serial_over_lan_policy':
                api_handle = sol_api.SolApi(api_client)
                get_policy = api_handle.get_sol_policy_list
            elif policy == 'smtp_policy':
                api_handle = smtp_api.SmtpApi(api_client)
                get_policy = api_handle.get_smtp_policy_list
            elif policy == 'snmp_policy':
                api_handle = snmp_api.SnmpApi(api_client)
                get_policy = api_handle.get_snmp_policy_list
            elif policy == 'ssh_policy':
                api_handle = ssh_api.SshApi(api_client)
                get_policy = api_handle.get_ssh_policy_list
            elif policy == 'storage_policy':
                api_handle = storage_api.StorageApi(api_client)
                get_policy = api_handle.get_storage_storage_policy_list
            elif policy == 'switch_control_policy':
                api_handle = fabric_api.FabricApi(api_client)
                get_policy = api_handle.get_fabric_switch_control_policy_list
            elif policy == 'system_qos_policy':
                api_handle = fabric_api.FabricApi(api_client)
                get_policy = api_handle.get_fabric_system_qos_policy_list
            elif policy == 'syslog_policy':
                api_handle = syslog_api.SyslogApi(api_client)
                get_policy = api_handle.get_syslog_policy_list
            elif policy == 'thermal_policy':
                api_handle = thermal_api.ThermalApi(api_client)
                get_policy = api_handle.get_thermal_policy_list
            elif policy == 'virtual_kvm_policy':
                api_handle = kvm_api.KvmApi(api_client)
                get_policy = api_handle.get_kvm_policy_list
            elif policy == 'virtual_media_policy':
                api_handle = vmedia_api.VmediaApi(api_client)
                get_policy = api_handle.get_vmedia_policy_list
            elif policy == 'uuid_pool':
                api_handle = uuidpool_api.UuidpoolApi(api_client)
                get_policy = api_handle.get_uuidpool_pool_list
            elif policy == 'vlan_policies':
                api_handle = fabric_api.FabricApi(api_client)
                get_policy = api_handle.get_fabric_eth_network_policy_list
            elif policy == 'vsan_policies':
                api_handle = fabric_api.FabricApi(api_client)
                get_policy = api_handle.get_fabric_fc_network_policy_list
            empty, kwargs['full_policy_list'][policy] = isdk_pools('get').get_api(get_policy, 'ALLP', org_moid)
        # return kwargs
        return kwargs

    #=====================================================
    # Get Policies, Pools, and Profiles from API
    #=====================================================
    def get_subtype(self, get_policy, query_filter):
        query_args   = dict(filter=query_filter, _preload_content = False)
        api_query    = json.loads(get_policy(**query_args).data)
        empty, policies, policy_names = isdk_pools('api_results').api_results(api_query)
        return empty, policies
    
    #=====================================================
    # Get IAM EndPoint User Roles Policies
    #=====================================================
    def get_iam_user_role(self, api_client, user_moid, lpolicy_moid):
        api_handle = iam_api.IamApi(api_client)
        query_filter = f"EndPointUser.Moid eq '{user_moid}' and EndPointUserPolicy eq '{lpolicy_moid}'"
        query_args   = dict(filter=query_filter, _preload_content = False)
        api_query    = json.loads(api_handle.get_iam_end_point_user_role_list(**query_args).data)
        if api_query.get('Results'):
            empty = False
            roles = {api_query['Results']['EndPointUser']['Moid']:{'Moid':api_query['Results']['Moid']}}
        else:
            empty = True
            roles = {}
        return empty, roles
    
    #=====================================================
    # Create/Patch IP Pools
    #=====================================================
    def ip(self, **kwargs):
        #=====================================================
        # Load Kwargs from Main
        #=====================================================
        args      = kwargs['args']
        dpools    = {}
        jsonVars  = kwargs['ezData']['policies']['allOf'][1]['properties']
        home      = kwargs['home']
        org       = kwargs['org']
        org_moids = kwargs['org_moids']
        pools     = kwargs['immDict']['orgs'][org]['pools']['ip']
        #=====================================================
        # Login to Intersight API
        #=====================================================
        api_client = credentials.config_credentials(home, args)
        api_handle = ippool_api.IppoolApi(api_client)
        validating.begin_section('IP Pools')
        for item in pools:
            pname = item['name']
            org_moid = org_moids[org]['Moid']
            #=====================================================
            # Confirm if the Pool Already Exists
            #=====================================================
            get_policy = api_handle.get_ippool_pool_list
            empty, ip_pools = isdk_pools('get').get_api(get_policy, pname, org_moid)
            #=====================================================
            # Construct API Body Payload
            #=====================================================
            api_body = {}
            if item.get('assignment_order'): api_body.update({'assignment_order':item['assignment_order']})
            else: api_body.update({'assignment_order':'sequential'})
            api_body.update({'class_id':'ippool.Pool','name':item['name'],'object_type':'ippool.Pool'})
            if item.get('description'): api_body.update({'description':item.get('description')})
            if item.get('ipv4_blocks'):
                api_body.update({'IpV4Blocks':[]})
                for i in item['ipv4_blocks']:
                    api_body['IpV4Blocks'].append({
                        'ClassId':'ippool.IpV4Block', 'ObjectType':'ippool.IpV4Block',
                        'From':i['from'],'Size':i['size']
                    })
            if item.get('ipv4_configuration'):
                ipcfg = item['ipv4_configuration'][0]
                api_body.update({'IpV4Config':{
                    'ClassId':'ippool.IpV4Config', 'ObjectType':'ippool.IpV4Config',
                    'Gateway':ipcfg['gateway'], 'Netmask':ipcfg['netmask'],
                    'PrimaryDns':ipcfg['primary_dns'], 'SecondaryDns':ipcfg['secondary_dns']
                }})
            if item.get('ipv6_blocks'):
                api_body.update({'IpV6Blocks':[]})
                for i in item['ipv6_blocks']:
                    api_body['IpV6Blocks'].append({
                        'ClassId':'ippool.IpV6Block', 'ObjectType':'ippool.IpV6Block',
                        'From':i['from'], 'Size':i['size']
                    })
            if item.get('ipv6_configuration'):
                ipcfg = item['ipv6_configuration'][0]
                api_body.update({'IpV6Config':{
                    'class_id':'ippool.IpV6Config', 'object_type':'ippool.IpV6Config',
                    'Gateway':ipcfg['gateway'], 'Netmask':ipcfg['prefix'],
                    'PrimaryDns':ipcfg['primary_dns'], 'SecondaryDns':ipcfg['secondary_dns']
                }})
            api_body.update({'organization':{
                'class_id':'mo.MoRef','moid':org_moid,'object_type':'organization.Organization'
            }})
            if item.get('tags'):
                api_body.update({'tags':item['tags']})
                api_body['tags'].append(jsonVars['tags'])
            else: api_body.update({'tags':[jsonVars['tags']]})
            #=====================================================
            # Create the Pool via the Intersight API
            #=====================================================
            try:
                if empty == True:
                    api_method = 'create'
                    api_args = dict(_preload_content = False)
                    api_call = json.loads(api_handle.create_ippool_pool(api_body, **api_args).data)
                    pol_moid = api_call['Moid']
                    if print_response_always == True: print(json.dumps(api_call, indent=4))
                    validating.completed_item('IP Pools', item['name'], api_method, pol_moid)
                else:
                    pol_moid = ip_pools[item['name']]['Moid']
                    print(f"    - Skipped name: {item['name']}, pool already exists. - Moid: {pol_moid}")
                dpools.update({item['name']:pol_moid})
            except ApiException as e:
                print("Exception when calling IppoolApi->create_ippool_pool: %s\n" % e)
                sys.exit(1)
        validating.end_section('IP Pools')
        return dpools

    #=====================================================
    # Create/Patch MAC Pools
    #=====================================================
    def mac(self, **kwargs):
        #=====================================================
        # Load Kwargs from Main
        #=====================================================
        args      = kwargs['args']
        dpools    = {}
        jsonVars  = kwargs['ezData']['policies']['allOf'][1]['properties']
        home      = kwargs['home']
        org       = kwargs['org']
        org_moids = kwargs['org_moids']
        pools     = kwargs['immDict']['orgs'][org]['pools']['mac']
        #=====================================================
        # Login to Intersight API
        #=====================================================
        api_client = credentials.config_credentials(home, args)
        api_handle = macpool_api.MacpoolApi(api_client)
        validating.begin_section('Mac Pools')
        for item in pools:
            pname = item['name']
            org_moid = org_moids[org]['Moid']
            #=====================================================
            # Confirm if the Policy Already Exists
            #=====================================================
            get_policy = api_handle.get_macpool_pool_list
            empty, mac_pools = isdk_pools('get').get_api(get_policy, pname, org_moid)
            #=====================================================
            # Construct API Body Payload
            #=====================================================
            api_body = {}
            if item.get('assignment_order'): api_body.update({'assignment_order':item['assignment_order']})
            else: api_body.update({'assignment_order':'sequential'})
            api_body.update({'class_id':'macpool.Pool','name':item['name'],'object_type':'macpool.Pool'})
            if item.get('description'): api_body.update({'description':item.get('description')})
            if item.get('mac_blocks'):
                api_body.update({'MacBlocks':[]})
                for i in item['mac_blocks']:
                    api_body['MacBlocks'].append({
                        'ClassId':'macpool.Block', 'ObjectType':'macpool.Block',
                        'From':i['from'], 'Size':i['size']
                    })
            api_body.update({'organization':{
                'class_id':'mo.MoRef','moid':org_moid,'object_type':'organization.Organization'
            }})
            if item.get('tags'):
                api_body.update({'tags':item['tags']})
                api_body['tags'].append(jsonVars['tags'])
            else: api_body.update({'tags':[jsonVars['tags']]})
            #=====================================================
            # Create the Pool via the Intersight API
            #=====================================================
            try:
                if empty == True:
                    api_method = 'create'
                    api_args = dict(_preload_content = False)
                    api_call = json.loads(api_handle.create_macpool_pool(api_body, **api_args).data)
                    pol_moid = api_call['Moid']
                    if print_response_always == True: print(json.dumps(api_call, indent=4))
                    validating.completed_item('Mac Pools', item['name'], api_method, pol_moid)
                else:
                    pol_moid = mac_pools[item['name']]['Moid']
                    print(f"    - Skipped name: {item['name']}, pool already exists. - Moid: {pol_moid}")
                dpools.update({item['name']:pol_moid})
            except ApiException as e:
                print("Exception when calling MacpoolApi->create_macpool_pool: %s\n" % e)
                sys.exit(1)
        validating.end_section('Mac Pools')
        return dpools

    #=====================================================
    # Get Organizations from Intersight
    #=====================================================
    def organizations(self, **kwargs):
        #=====================================================
        # Load Kwargs from Main
        #=====================================================
        args = kwargs['args']
        home = kwargs['home']
        #=====================================================
        # Login to Intersight API
        #=====================================================
        api_client = credentials.config_credentials(home, args)
        api_handle = organization_api.OrganizationApi(api_client)
        api_args   = dict(_preload_content = False)
        api_query = json.loads(api_handle.get_organization_organization_list(**api_args).data)
        empty, org_moids, org_names = isdk_pools('api_results').api_results(api_query)
        if empty == True: isdk_pools('api_results').empty_results(api_query)
        kwargs['org_moids'] = org_moids
        kwargs['org_names'] = org_names
        return kwargs

    #=====================================================
    # Create/Patch UUID Pools
    #=====================================================
    def uuid(self, **kwargs):
        #=====================================================
        # Load Kwargs from Main
        #=====================================================
        args      = kwargs['args']
        dpools    = {}
        jsonVars  = kwargs['ezData']['policies']['allOf'][1]['properties']
        home      = kwargs['home']
        org       = kwargs['org']
        org_moids = kwargs['org_moids']
        pools     = kwargs['immDict']['orgs'][org]['pools']['uuid']
        #=====================================================
        # Login to Intersight API
        #=====================================================
        api_client = credentials.config_credentials(home, args)
        api_handle = uuidpool_api.UuidpoolApi(api_client)
        validating.begin_section('UUID Pools')
        for item in pools:
            pname = item['name']
            org_moid = org_moids[org]['Moid']
            #=====================================================
            # Confirm if the Policy Already Exists
            #=====================================================
            get_policy = api_handle.get_uuidpool_pool_list
            empty, uuid_pools = isdk_pools('get').get_api(get_policy, pname, org_moid)
            #=====================================================
            # Construct API Body Payload
            #=====================================================
            api_body = {}
            if item.get('assignment_order'): api_body.update({'assignment_order':item['assignment_order']})
            else: api_body.update({'assignment_order':'sequential'})
            api_body.update({'class_id':'uuidpool.Pool','name':item['name'],'object_type':'uuidpool.Pool'})
            if item.get('description'): api_body.update({'description':item.get('description')})
            api_body.update({'prefix':item['prefix']})
            if item.get('uuid_blocks'):
                api_body.update({'UuidSuffixBlocks':[]})
                for i in item['uuid_blocks']:
                    api_body['UuidSuffixBlocks'].append({
                        'ClassId':'uuidpool.UuidBlock', 'ObjectType':'uuidpool.UuidBlock',
                        'From':i['from'], 'Size':i['size']
                    })
            api_body.update({'organization':{
                'class_id':'mo.MoRef','moid':org_moid,'object_type':'organization.Organization'
            }})
            if item.get('tags'):
                api_body.update({'tags':item['tags']})
                api_body['tags'].append(jsonVars['tags'])
            else: api_body.update({'tags':[jsonVars['tags']]})
            #=====================================================
            # Create the Pool via the Intersight API
            #=====================================================
            try:
                if empty == True:
                    api_method = 'create'
                    api_args = dict(_preload_content = False)
                    api_call = json.loads(api_handle.create_uuidpool_pool(api_body, **api_args).data)
                    pol_moid = api_call['Moid']
                    if print_response_always == True: print(json.dumps(api_call, indent=4))
                    validating.completed_item('UUID Pools', item['name'], api_method, pol_moid)
                else:
                    pol_moid = uuid_pools[item['name']]['Moid']
                    print(f"    - Skipped name: {item['name']}, pool already exists. - Moid: {pol_moid}")
                dpools.update({item['name']:pol_moid})
            except ApiException as e:
                print("Exception when calling uuidpool_api->create_uuidpool_pool: %s\n" % e)
                sys.exit(1)
        validating.end_section('UUID Pools')
        return dpools

    #=====================================================
    # Create/Patch WWNN Pools
    #=====================================================
    def wwnn(self, **kwargs):
        isdk_pools('WWNN').fc(**kwargs)
    
    #=====================================================
    # Create/Patch WWPN Pools
    #=====================================================
    def wwpn(self, **kwargs):
        isdk_pools('WWPN').fc(**kwargs)
