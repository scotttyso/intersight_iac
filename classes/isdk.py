from intersight.api import access_api
from intersight.api import adapter_api
from intersight.api import bios_api
from intersight.api import boot_api
from intersight.api import bulk_api
from intersight.api import certificatemanagement_api
from intersight.api import chassis_api
from intersight.api import compute_api
from intersight.api import deviceconnector_api
from intersight.api import equipment_api
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
from intersight.api import server_api
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
import time
import urllib3
import validating
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Global options for debugging
print_payload = False
print_response_always = False
print_response_on_fail = True

fabric_regex = re.compile(
    '(domain|fc_z|flow|link_(ag|co)|multicast|network_(control|group)|port|switch_c|system_q|v(l|s)an[s]?)'
)
vnic_regex = re.compile('^((ethernet|fibre_channel)_(adapter|network|qos)|(l|s)an_connectivity|vhba|vnic)')

class api(object):
    def __init__(self, type):
        self.type = type

    #=====================================================
    # Process API Results
    #=====================================================
    def api_results(self, pargs, apiQuery):
        apiDict = {}
        if apiQuery.get('Results'):
            for i in apiQuery['Results']:
                iMoid = i['Moid']
                if i.get('VlanId'): iName = i['VlanId']
                elif i.get('PcId'): iName = i['PcId']
                elif i.get('PortId'): iName = i['PortId']
                elif i.get('Serial'): iName = i['Serial']
                elif i.get('VsanId'): iName = i['VsanId']
                elif i.get('Name'): iName = i['Name']
                elif i.get('EndPointUser'): iName = i['EndPointUser']['Moid']
                elif i.get('PortIdStart'): iName = i['PortIdStart']
                if i.get('PcId') or i.get('PortId') or i.get('PortIdStart'):
                    apiDict.update({i['PortPolicy']['Moid']:{iName:{'Moid':iMoid}}})
                else: apiDict.update({iName:{'Moid':iMoid}})
                if i.get('Model'):
                    apiDict[iName]['Model'] = i['Model']
                    apiDict[iName]['RegisteredDevice'] = i['RegisteredDevice']['Moid']
                if i.get('Profiles'):
                    apiDict[iName]['profiles'] = []
                    for x in i['Profiles']:
                        xdict = {'class_id':'mo.MoRef','moid':x['Moid'],'object_type':x['ObjectType']}
                        apiDict[iName]['profiles'].append(xdict)
        return apiDict

    #=====================================================
    # Perform API Calls to Intersight
    #=====================================================
    def calls(self, pargs, **kwargs):
        #=====================================================
        # Authenticate to the API
        #=====================================================
        if not 'organization' == pargs.policy:
            org_moid = kwargs['org_moids'][kwargs['org']]['Moid']
        #=====================================================
        # Authenticate to the API
        #=====================================================
        if kwargs.get('api_authenticated') and kwargs.get('api_auth_time'):
            if time.time() - kwargs['api_auth_time'] > 599:
                apiClient = credentials.config_credentials(kwargs['home'], kwargs['args'])
                kwargs['api_authenticated'] = apiClient
                kwargs['api_auth_time'] = time.time()
            else: apiClient = kwargs['api_authenticated']
        else:
            apiClient = credentials.config_credentials(kwargs['home'], kwargs['args'])
            kwargs['api_authenticated'] = apiClient
            kwargs['api_auth_time'] = time.time()
        #=====================================================
        # Determine the apiCall to Create
        #=====================================================
        if re.search(fabric_regex, pargs.policy):
            apiHandle = fabric_api.FabricApi(apiClient)
            if 'vlans' == pargs.policy:
                if pargs.apiMethod == 'by_moid':  apiCall = apiHandle.get_fabric_vlan_by_moid
                elif pargs.apiMethod == 'get':    apiCall = apiHandle.get_fabric_vlan_list
                elif pargs.apiMethod == 'create': apiCall = apiHandle.create_fabric_vlan
                elif pargs.apiMethod == 'patch':  apiCall = apiHandle.patch_fabric_vlan
            elif 'port_role_server' in pargs.policy:
                if pargs.apiMethod == 'by_moid':  apiCall = apiHandle.get_fabric_server_role_by_moid
                elif pargs.apiMethod == 'get':    apiCall = apiHandle.get_fabric_server_role_list
                elif pargs.apiMethod == 'create': apiCall = apiHandle.create_fabric_server_role
                elif pargs.apiMethod == 'patch':  apiCall = apiHandle.patch_fabric_server_role
            elif 'ethernet_network_group' in pargs.policy:
                if pargs.apiMethod == 'by_moid':  apiCall = apiHandle.get_fabric_eth_network_group_policy_by_moid
                elif pargs.apiMethod == 'get':    apiCall = apiHandle.get_fabric_eth_network_group_policy_list
                elif pargs.apiMethod == 'create': apiCall = apiHandle.create_fabric_eth_network_group_policy
                elif pargs.apiMethod == 'patch':  apiCall = apiHandle.patch_fabric_eth_network_group_policy
            elif 'vsans' == pargs.policy:
                if pargs.apiMethod == 'by_moid':  apiCall = apiHandle.get_fabric_vsan_by_moid
                elif pargs.apiMethod == 'get':    apiCall = apiHandle.get_fabric_vsan_list
                elif pargs.apiMethod == 'create': apiCall = apiHandle.create_fabric_vsan
                elif pargs.apiMethod == 'patch':  apiCall = apiHandle.patch_fabric_vsan
            elif 'domain' == pargs.policy:
                if pargs.apiMethod == 'by_moid':  apiCall = apiHandle.get_fabric_switch_cluster_profile_by_moid
                elif pargs.apiMethod == 'get':    apiCall = apiHandle.get_fabric_switch_cluster_profile_list
                elif pargs.apiMethod == 'create': apiCall = apiHandle.create_fabric_switch_cluster_profile
                elif pargs.apiMethod == 'patch':  apiCall = apiHandle.patch_fabric_switch_cluster_profile
            elif 'ethernet_network_control' in pargs.policy:
                if pargs.apiMethod == 'by_moid':  apiCall = apiHandle.get_fabric_eth_network_control_policy_by_moid
                elif pargs.apiMethod == 'get':    apiCall = apiHandle.get_fabric_eth_network_control_policy_list
                elif pargs.apiMethod == 'create': apiCall = apiHandle.create_fabric_eth_network_control_policy
                elif pargs.apiMethod == 'patch':  apiCall = apiHandle.patch_fabric_eth_network_control_policy
            elif 'fc_zone' in pargs.policy:
                if pargs.apiMethod == 'by_moid':  apiCall = apiHandle.get_fabric_fc_zone_policy_by_moid
                elif pargs.apiMethod == 'get':    apiCall = apiHandle.get_fabric_fc_zone_policy_list
                elif pargs.apiMethod == 'create': apiCall = apiHandle.create_fabric_fc_zone_policy
                elif pargs.apiMethod == 'patch':  apiCall = apiHandle.patch_fabric_fc_zone_policy
            elif 'flow_control' in pargs.policy:
                if pargs.apiMethod == 'by_moid':  apiCall = apiHandle.get_fabric_flow_control_policy_by_moid
                elif pargs.apiMethod == 'get':    apiCall = apiHandle.get_fabric_flow_control_policy_list
                elif pargs.apiMethod == 'create': apiCall = apiHandle.create_fabric_flow_control_policy
                elif pargs.apiMethod == 'patch':  apiCall = apiHandle.patch_fabric_flow_control_policy
            elif 'link_aggregation' in pargs.policy:
                if pargs.apiMethod == 'by_moid':  apiCall = apiHandle.get_fabric_link_aggregation_policy_by_moid
                elif pargs.apiMethod == 'get':    apiCall = apiHandle.get_fabric_link_aggregation_policy_list
                elif pargs.apiMethod == 'create': apiCall = apiHandle.create_fabric_link_aggregation_policy
                elif pargs.apiMethod == 'patch':  apiCall = apiHandle.patch_fabric_link_aggregation_policy
            elif 'link_control' in pargs.policy:
                if pargs.apiMethod == 'by_moid':  apiCall = apiHandle.get_fabric_link_control_policy_by_moid
                elif pargs.apiMethod == 'get':    apiCall = apiHandle.get_fabric_link_control_policy_list
                elif pargs.apiMethod == 'create': apiCall = apiHandle.create_fabric_link_control_policy
                elif pargs.apiMethod == 'patch':  apiCall = apiHandle.patch_fabric_link_control_policy
            elif 'multicast' in pargs.policy:
                if pargs.apiMethod == 'by_moid':  apiCall = apiHandle.get_fabric_multicast_policy_by_moid
                elif pargs.apiMethod == 'get':    apiCall = apiHandle.get_fabric_multicast_policy_list
                elif pargs.apiMethod == 'create': apiCall = apiHandle.create_fabric_multicast_policy
                elif pargs.apiMethod == 'patch':  apiCall = apiHandle.patch_fabric_multicast_policy
            elif 'port' == pargs.policy:
                if pargs.apiMethod == 'by_moid':  apiCall = apiHandle.get_fabric_port_policy_by_moid
                elif pargs.apiMethod == 'get':    apiCall = apiHandle.get_fabric_port_policy_list
                elif pargs.apiMethod == 'create': apiCall = apiHandle.create_fabric_port_policy
                elif pargs.apiMethod == 'patch':  apiCall = apiHandle.patch_fabric_port_policy
            elif 'port_channel_ethernet_uplink' in pargs.policy:
                if pargs.apiMethod == 'by_moid':  apiCall = apiHandle.get_fabric_uplink_pc_role_by_moid
                elif pargs.apiMethod == 'get':    apiCall = apiHandle.get_fabric_uplink_pc_role_list
                elif pargs.apiMethod == 'create': apiCall = apiHandle.create_fabric_uplink_pc_role
                elif pargs.apiMethod == 'patch':  apiCall = apiHandle.patch_fabric_uplink_pc_role
            elif 'port_channel_fc_uplink' in pargs.policy:
                if pargs.apiMethod == 'by_moid':  apiCall = apiHandle.get_fabric_fc_uplink_pc_role_by_moid
                elif pargs.apiMethod == 'get':    apiCall = apiHandle.get_fabric_fc_uplink_pc_role_list
                elif pargs.apiMethod == 'create': apiCall = apiHandle.create_fabric_fc_uplink_pc_role
                elif pargs.apiMethod == 'patch':  apiCall = apiHandle.patch_fabric_fc_uplink_pc_role
            elif 'switch_control' == pargs.policy:
                if pargs.apiMethod == 'by_moid':  apiCall = apiHandle.get_fabric_switch_control_policy_by_moid
                elif pargs.apiMethod == 'get':    apiCall = apiHandle.get_fabric_switch_control_policy_list
                elif pargs.apiMethod == 'create': apiCall = apiHandle.create_fabric_switch_control_policy
                elif pargs.apiMethod == 'patch':  apiCall = apiHandle.patch_fabric_switch_control_policy
            elif 'switch_profile' == pargs.policy:
                if pargs.apiMethod == 'by_moid':  apiCall = apiHandle.get_fabric_switch_profile_by_moid
                elif pargs.apiMethod == 'get':    apiCall = apiHandle.get_fabric_switch_profile_list
                elif pargs.apiMethod == 'create': apiCall = apiHandle.create_fabric_switch_profile
                elif pargs.apiMethod == 'patch':  apiCall = apiHandle.patch_fabric_switch_profile
            elif 'system_qos' == pargs.policy:
                if pargs.apiMethod == 'by_moid':  apiCall = apiHandle.get_fabric_system_qos_policy_by_moid
                elif pargs.apiMethod == 'get':    apiCall = apiHandle.get_fabric_system_qos_policy_list
                elif pargs.apiMethod == 'create': apiCall = apiHandle.create_fabric_system_qos_policy
                elif pargs.apiMethod == 'patch':  apiCall = apiHandle.patch_fabric_system_qos_policy
            elif 'link_control' in pargs.policy:
                if pargs.apiMethod == 'by_moid':  apiCall = apiHandle.get_fabric_link_control_policy_by_moid
                elif pargs.apiMethod == 'get':    apiCall = apiHandle.get_fabric_link_control_policy_list
                elif pargs.apiMethod == 'create': apiCall = apiHandle.create_fabric_link_control_policy
                elif pargs.apiMethod == 'patch':  apiCall = apiHandle.patch_fabric_link_control_policy
            elif 'vlan' == pargs.policy:
                if pargs.apiMethod == 'by_moid':  apiCall = apiHandle.get_fabric_eth_network_policy_by_moid
                elif pargs.apiMethod == 'get':    apiCall = apiHandle.get_fabric_eth_network_policy_list
                elif pargs.apiMethod == 'create': apiCall = apiHandle.create_fabric_eth_network_policy
                elif pargs.apiMethod == 'patch':  apiCall = apiHandle.patch_fabric_eth_network_policy
            elif 'vsan' == pargs.policy:
                if pargs.apiMethod == 'by_moid':  apiCall = apiHandle.get_fabric_fc_network_policy_by_moid
                elif pargs.apiMethod == 'get':    apiCall = apiHandle.get_fabric_fc_network_policy_list
                elif pargs.apiMethod == 'create': apiCall = apiHandle.create_fabric_fc_network_policy
                elif pargs.apiMethod == 'patch':  apiCall = apiHandle.patch_fabric_fc_network_policy
            elif 'port_role_ethernet_uplink' in pargs.policy:
                if pargs.apiMethod == 'by_moid':  apiCall = apiHandle.get_fabric_uplink_role_by_moid
                elif pargs.apiMethod == 'get':    apiCall = apiHandle.get_fabric_uplink_pc_role_list
                elif pargs.apiMethod == 'create': apiCall = apiHandle.create_fabric_uplink_role
                elif pargs.apiMethod == 'patch':  apiCall = apiHandle.patch_fabric_uplink_role
            elif 'port_role_fc_uplink' in pargs.policy:
                if pargs.apiMethod == 'by_moid':  apiCall = apiHandle.get_fabric_fc_uplink_role_by_moid
                elif pargs.apiMethod == 'get':    apiCall = apiHandle.get_fabric_fc_uplink_pc_role_list
                elif pargs.apiMethod == 'create': apiCall = apiHandle.create_fabric_fc_uplink_role
                elif pargs.apiMethod == 'patch':  apiCall = apiHandle.patch_fabric_fc_uplink_role
            elif 'port_role_fc_storage' in pargs.policy:
                if pargs.apiMethod == 'bymoid': apiCall = apiHandle.get_fabric_fc_storage_role_by_moid
                elif pargs.apiMethod == 'get':    apiCall = apiHandle.get_fabric_fc_storage_role_list
                elif pargs.apiMethod == 'create': apiCall = apiHandle.create_fabric_fc_storage_role
                elif pargs.apiMethod == 'patch':  apiCall = apiHandle.patch_fabric_fc_storage_role
            elif 'port_mode' == pargs.policy:
                if pargs.apiMethod == 'by_moid':  apiCall = apiHandle.get_fabric_port_mode_by_moid
                elif pargs.apiMethod == 'get':    apiCall = apiHandle.get_fabric_port_mode_list
                elif pargs.apiMethod == 'create': apiCall = apiHandle.create_fabric_port_mode
                elif pargs.apiMethod == 'patch':  apiCall = apiHandle.patch_fabric_port_mode
            elif 'port_channel_appliance' in pargs.policy:
                if pargs.apiMethod == 'by_moid':  apiCall = apiHandle.get_fabric_appliance_pc_role_by_moid
                elif pargs.apiMethod == 'get':    apiCall = apiHandle.get_fabric_appliance_pc_role_list
                elif pargs.apiMethod == 'create': apiCall = apiHandle.create_fabric_appliance_pc_role
                elif pargs.apiMethod == 'patch':  apiCall = apiHandle.patch_fabric_appliance_pc_role
            elif 'port_role_appliance' in pargs.policy:
                if pargs.apiMethod == 'by_moid':  apiCall = apiHandle.get_fabric_appliance_role_by_moid
                elif pargs.apiMethod == 'get':    apiCall = apiHandle.get_fabric_appliance_role_list
                elif pargs.apiMethod == 'create': apiCall = apiHandle.create_fabric_appliance_role
                elif pargs.apiMethod == 'patch':  apiCall = apiHandle.patch_fabric_appliance_role
            elif 'port_channel_fcoe_uplink' in pargs.policy:
                if pargs.apiMethod == 'by_moid':  apiCall = apiHandle.get_fabric_fcoe_uplink_pc_role_by_moid
                elif pargs.apiMethod == 'get':    apiCall = apiHandle.get_fabric_fcoe_uplink_pc_role_list
                elif pargs.apiMethod == 'create': apiCall = apiHandle.create_fabric_fcoe_uplink_pc_role
                elif pargs.apiMethod == 'patch':  apiCall = apiHandle.patch_fabric_fcoe_uplink_pc_role
            elif 'port_role_fcoe_uplink' in pargs.policy:
                if pargs.apiMethod == 'by_moid':  apiCall = apiHandle.get_fabric_fcoe_uplink_role_by_moid
                elif pargs.apiMethod == 'get':    apiCall = apiHandle.get_fabric_fcoe_uplink_role_list
                elif pargs.apiMethod == 'create': apiCall = apiHandle.create_fabric_fcoe_uplink_role
                elif pargs.apiMethod == 'patch':  apiCall = apiHandle.patch_fabric_fcoe_uplink_role
        elif re.search('^(chassis|domain|server|templates)$', pargs.purpose):
            apiHandle = server_api.ServerApi(apiClient)
            if 'server' == pargs.policy:
                if pargs.apiMethod == 'by_moid':  apiCall = apiHandle.get_server_profile_by_moid
                elif pargs.apiMethod == 'get':    apiCall = apiHandle.get_server_profile_list
                elif pargs.apiMethod == 'create': apiCall = apiHandle.create_server_profile
                elif pargs.apiMethod == 'patch':  apiCall = apiHandle.patch_server_profile
            elif 'templates' in pargs.policy:
                if pargs.apiMethod == 'by_moid':  apiCall = apiHandle.get_server_profile_template_by_moid
                elif pargs.apiMethod == 'get':    apiCall = apiHandle.get_server_profile_template_list
                elif pargs.apiMethod == 'create': apiCall = apiHandle.create_server_profile_template
                elif pargs.apiMethod == 'patch':  apiCall = apiHandle.patch_server_profile_template
            elif 'cluster' == pargs.policy:
                apiHandle = fabric_api.FabricApi(apiClient)
                if pargs.apiMethod == 'by_moid':  apiCall = apiHandle.get_fabric_switch_cluster_profile_by_moid
                elif pargs.apiMethod == 'get':    apiCall = apiHandle.get_fabric_switch_cluster_profile_list
                elif pargs.apiMethod == 'create': apiCall = apiHandle.create_fabric_switch_cluster_profile
                elif pargs.apiMethod == 'patch':  apiCall = apiHandle.patch_fabric_switch_cluster_profile
            elif 'chassis' == pargs.policy:
                apiHandle = chassis_api.ChassisApi(apiClient)
                if pargs.apiMethod == 'by_moid':  apiCall = apiHandle.get_chassis_profile_by_moid
                elif pargs.apiMethod == 'get':    apiCall = apiHandle.get_chassis_profile_list
                elif pargs.apiMethod == 'create': apiCall = apiHandle.create_chassis_profile
                elif pargs.apiMethod == 'patch':  apiCall = apiHandle.patch_chassis_profile
            elif 'switch' == pargs.policy:
                apiHandle = fabric_api.FabricApi(apiClient)
                if pargs.apiMethod == 'by_moid':  apiCall = apiHandle.get_fabric_switch_profile_by_moid
                elif pargs.apiMethod == 'get':    apiCall = apiHandle.get_fabric_switch_profile_list
                elif pargs.apiMethod == 'create': apiCall = apiHandle.create_fabric_switch_profile
                elif pargs.apiMethod == 'patch':  apiCall = apiHandle.patch_fabric_switch_profile
            elif 'serial_number' == pargs.policy:
                if 'server' == pargs.purpose:
                    apiHandle = compute_api.ComputeApi(apiClient)
                    apiCall   = apiHandle.get_compute_physical_summary_list
                elif 'chassis' == pargs.purpose:
                    apiHandle = equipment_api.EquipmentApi(apiClient)
                    apiCall   = apiHandle.get_equipment_chassis_list
                elif 'domain' == pargs.purpose:
                    apiHandle = fabric_api.FabricApi(apiClient)
                    apiCall   = apiHandle.get_fabric_element_identity_list
        elif re.search(vnic_regex, pargs.policy):
            apiHandle = vnic_api.VnicApi(apiClient)
            if 'vnic' in pargs.policy:
                if pargs.apiMethod == 'by_moid':  apiCall = apiHandle.get_vnic_eth_if_by_moid
                elif pargs.apiMethod == 'get':    apiCall = apiHandle.get_vnic_eth_if_list
                elif pargs.apiMethod == 'create': apiCall = apiHandle.create_vnic_eth_if
                elif pargs.apiMethod == 'patch':  apiCall = apiHandle.patch_vnic_eth_if
            elif 'vhba' in pargs.policy:
                if pargs.apiMethod == 'by_moid':  apiCall = apiHandle.get_vnic_fc_if_by_moid
                elif pargs.apiMethod == 'get':    apiCall = apiHandle.get_vnic_fc_if_list
                elif pargs.apiMethod == 'create': apiCall = apiHandle.create_vnic_fc_if
                elif pargs.apiMethod == 'patch':  apiCall = apiHandle.patch_vnic_fc_if
            elif 'ethernet_adapter' in pargs.policy:
                if pargs.apiMethod == 'by_moid':  apiCall = apiHandle.get_vnic_eth_adapter_policy_by_moid
                elif pargs.apiMethod == 'get':    apiCall = apiHandle.get_vnic_eth_adapter_policy_list
                elif pargs.apiMethod == 'create': apiCall = apiHandle.create_vnic_eth_adapter_policy
                elif pargs.apiMethod == 'patch':  apiCall = apiHandle.patch_vnic_eth_adapter_policy
            elif 'ethernet_network' in pargs.policy:
                if pargs.apiMethod == 'by_moid':  apiCall = apiHandle.get_vnic_eth_network_policy_by_moid
                elif pargs.apiMethod == 'get':    apiCall = apiHandle.get_vnic_eth_network_policy_list
                elif pargs.apiMethod == 'create': apiCall = apiHandle.create_vnic_eth_network_policy
                elif pargs.apiMethod == 'patch':  apiCall = apiHandle.patch_vnic_eth_network_policy
            elif 'ethernet_qos' in pargs.policy:
                if pargs.apiMethod == 'by_moid':  apiCall = apiHandle.get_vnic_eth_qos_policy_by_moid
                elif pargs.apiMethod == 'get':    apiCall = apiHandle.get_vnic_eth_qos_policy_list
                elif pargs.apiMethod == 'create': apiCall = apiHandle.create_vnic_eth_qos_policy
                elif pargs.apiMethod == 'patch':  apiCall = apiHandle.patch_vnic_eth_qos_policy
            elif 'fibre_channel_adapter' in pargs.policy:
                if pargs.apiMethod == 'by_moid':  apiCall = apiHandle.get_vnic_fc_adapter_policy_by_moid
                elif pargs.apiMethod == 'get':    apiCall = apiHandle.get_vnic_fc_adapter_policy_list
                elif pargs.apiMethod == 'create': apiCall = apiHandle.create_vnic_fc_adapter_policy
                elif pargs.apiMethod == 'patch':  apiCall = apiHandle.patch_vnic_fc_adapter_policy
            elif 'fibre_channel_network' in pargs.policy:
                if pargs.apiMethod == 'by_moid':  apiCall = apiHandle.get_vnic_fc_network_policy_by_moid
                elif pargs.apiMethod == 'get':    apiCall = apiHandle.get_vnic_fc_network_policy_list
                elif pargs.apiMethod == 'create': apiCall = apiHandle.create_vnic_fc_network_policy
                elif pargs.apiMethod == 'patch':  apiCall = apiHandle.patch_vnic_fc_network_policy
            elif 'fibre_channel_qos' in pargs.policy:
                if pargs.apiMethod == 'by_moid':  apiCall = apiHandle.get_vnic_fc_qos_policy_by_moid
                elif pargs.apiMethod == 'get':    apiCall = apiHandle.get_vnic_fc_qos_policy_list
                elif pargs.apiMethod == 'create': apiCall = apiHandle.create_vnic_fc_qos_policy
                elif pargs.apiMethod == 'patch':  apiCall = apiHandle.patch_vnic_fc_qos_policy
            elif 'lan_connectivity' in pargs.policy:
                if pargs.apiMethod == 'by_moid':  apiCall = apiHandle.get_vnic_lan_connectivity_policy_by_moid
                elif pargs.apiMethod == 'get':    apiCall = apiHandle.get_vnic_lan_connectivity_policy_list
                elif pargs.apiMethod == 'create': apiCall = apiHandle.create_vnic_lan_connectivity_policy
                elif pargs.apiMethod == 'patch':  apiCall = apiHandle.patch_vnic_lan_connectivity_policy
            elif 'san_connectivity' in pargs.policy:
                if pargs.apiMethod == 'by_moid':  apiCall = apiHandle.get_vnic_san_connectivity_policy_by_moid
                elif pargs.apiMethod == 'get':    apiCall = apiHandle.get_vnic_san_connectivity_policy_list
                elif pargs.apiMethod == 'create': apiCall = apiHandle.create_vnic_san_connectivity_policy
                elif pargs.apiMethod == 'patch':  apiCall = apiHandle.patch_vnic_san_connectivity_policy
        elif 'adapter_configuration' in pargs.policy:
            apiHandle = adapter_api.AdapterApi(apiClient)
            if pargs.apiMethod == 'by_moid':  apiCall = apiHandle.get_adapter_config_policy_by_moid
            elif pargs.apiMethod == 'get':    apiCall = apiHandle.get_adapter_config_policy_list
            elif pargs.apiMethod == 'create': apiCall = apiHandle.create_adapter_config_policy
            elif pargs.apiMethod == 'patch':  apiCall = apiHandle.patch_adapter_config_policy
        elif 'bios' in pargs.policy:
            apiHandle = bios_api.BiosApi(apiClient)
            if pargs.apiMethod == 'by_moid':  apiCall = apiHandle.get_bios_policy_by_moid
            elif pargs.apiMethod == 'get':    apiCall = apiHandle.get_bios_policy_list
            elif pargs.apiMethod == 'create': apiCall = apiHandle.create_bios_policy
            elif pargs.apiMethod == 'patch':  apiCall = apiHandle.patch_bios_policy
        elif 'bulk' in pargs.policy:
            apiHandle = bulk_api.BulkApi(apiClient)
            apiCall = apiHandle.create_bulk_mo_cloner
        elif 'boot_order' in pargs.policy:
            apiHandle = boot_api.BootApi(apiClient)
            if pargs.apiMethod == 'by_moid':  apiCall = apiHandle.get_boot_precision_policy_by_moid
            elif pargs.apiMethod == 'get':    apiCall = apiHandle.get_boot_precision_policy_list
            elif pargs.apiMethod == 'create': apiCall = apiHandle.create_boot_precision_policy
            elif pargs.apiMethod == 'patch':  apiCall = apiHandle.patch_boot_precision_policy
        elif 'certificate_management' in pargs.policy:
            apiHandle = certificatemanagement_api.CertificatemanagementApi(apiClient)
            if pargs.apiMethod == 'by_moid':  apiCall = apiHandle.get_certificatemanagement_policy_by_moid
            elif pargs.apiMethod == 'get':    apiCall = apiHandle.get_certificatemanagement_policy_list
            elif pargs.apiMethod == 'create': apiCall = apiHandle.create_certificatemanagement_policy
            elif pargs.apiMethod == 'patch':  apiCall = apiHandle.patch_certificatemanagement_policy
        elif 'device_connector' in pargs.policy:
            apiHandle = deviceconnector_api.DeviceconnectorApi(apiClient)
            if pargs.apiMethod == 'by_moid':  apiCall = apiHandle.get_deviceconnector_policy_by_moid
            elif pargs.apiMethod == 'get':    apiCall = apiHandle.get_deviceconnector_policy_list
            elif pargs.apiMethod == 'create': apiCall = apiHandle.create_deviceconnector_policy
            elif pargs.apiMethod == 'patch':  apiCall = apiHandle.patch_deviceconnector_policy
        elif 'imc_access' in pargs.policy:
            apiHandle = access_api.AccessApi(apiClient)
            if pargs.apiMethod == 'by_moid':  apiCall = apiHandle.get_access_policy_by_moid
            elif pargs.apiMethod == 'get':    apiCall = apiHandle.get_access_policy_list
            elif pargs.apiMethod == 'create': apiCall = apiHandle.create_access_policy
            elif pargs.apiMethod == 'patch':  apiCall = apiHandle.patch_access_policy
        elif 'ip' == pargs.policy:
            apiHandle = ippool_api.IppoolApi(apiClient)
            if pargs.apiMethod == 'by_moid':  apiCall = apiHandle.get_ippool_pool_by_moid
            elif pargs.apiMethod == 'get':    apiCall = apiHandle.get_ippool_pool_list
            elif pargs.apiMethod == 'create': apiCall = apiHandle.create_ippool_pool
            elif pargs.apiMethod == 'patch':  apiCall = apiHandle.patch_ippool_pool
        elif 'ipmi_over_lan' in pargs.policy:
            apiHandle = ipmioverlan_api.IpmioverlanApi(apiClient)
            if pargs.apiMethod == 'by_moid':  apiCall = apiHandle.get_ipmioverlan_policy_by_moid
            elif pargs.apiMethod == 'get':    apiCall = apiHandle.get_ipmioverlan_policy_list
            elif pargs.apiMethod == 'create': apiCall = apiHandle.create_ipmioverlan_policy
            elif pargs.apiMethod == 'patch':  apiCall = apiHandle.patch_ipmioverlan_policy
        elif re.search('(iamrole|ldap(_group)?|local(_user)?|user_role)', pargs.policy):
            apiHandle = iam_api.IamApi(apiClient)
            if 'iamrole' == pargs.policy:
                if pargs.apiMethod == 'by_moid':  apiCall = apiHandle.get_iam_end_point_role_by_moid
                elif pargs.apiMethod == 'get':    apiCall = apiHandle.get_iam_end_point_role_list
            elif 'ldap' == pargs.policy:
                if pargs.apiMethod == 'by_moid':  apiCall = apiHandle.get_iam_ldap_provider_by_moid
                elif pargs.apiMethod == 'get':    apiCall = apiHandle.get_iam_ldap_policy_list
                elif pargs.apiMethod == 'create': apiCall = apiHandle.create_iam_ldap_policy
                elif pargs.apiMethod == 'patch':  apiCall = apiHandle.patch_iam_ldap_policy
            elif 'ldap_group' == pargs.policy:
                if pargs.apiMethod == 'by_moid':  apiCall = apiHandle.get_iam_ldap_group_by_moid
                elif pargs.apiMethod == 'get':    apiCall = apiHandle.get_iam_ldap_policy_list
                elif pargs.apiMethod == 'create': apiCall = apiHandle.create_iam_ldap_group
                elif pargs.apiMethod == 'patch':  apiCall = apiHandle.patch_iam_ldap_group
            elif 'local_user' == pargs.policy:
                if pargs.apiMethod == 'by_moid':  apiCall = apiHandle.get_iam_end_point_user_policy_by_moid
                elif pargs.apiMethod == 'get':    apiCall = apiHandle.get_iam_end_point_user_policy_list
                elif pargs.apiMethod == 'create': apiCall = apiHandle.create_iam_end_point_user_policy
                elif pargs.apiMethod == 'patch':  apiCall = apiHandle.patch_iam_end_point_user_policy
            elif 'local_users' == pargs.policy:
                if pargs.apiMethod == 'by_moid':  apiCall = apiHandle.get_iam_end_point_user_by_moid
                elif pargs.apiMethod == 'get':    apiCall = apiHandle.get_iam_end_point_user_list
                elif pargs.apiMethod == 'create': apiCall = apiHandle.create_iam_end_point_user
                elif pargs.apiMethod == 'patch':  apiCall = apiHandle.patch_iam_end_point_user
            elif 'user_role' == pargs.policy:
                if pargs.apiMethod == 'by_moid':  apiCall = apiHandle.get_iam_end_point_user_role_by_moid
                elif pargs.apiMethod == 'get':    apiCall = apiHandle.get_iam_end_point_user_role_list
                elif pargs.apiMethod == 'create': apiCall = apiHandle.create_iam_end_point_user_role
                elif pargs.apiMethod == 'patch':  apiCall = apiHandle.patch_iam_end_point_user_role
        elif 'mac' == pargs.policy:
            apiHandle = macpool_api.MacpoolApi(apiClient)
            if pargs.apiMethod == 'by_moid':  apiCall = apiHandle.get_macpool_pool_by_moid
            elif pargs.apiMethod == 'get':    apiCall = apiHandle.get_macpool_pool_list
            elif pargs.apiMethod == 'create': apiCall = apiHandle.create_macpool_pool
            elif pargs.apiMethod == 'patch':  apiCall = apiHandle.patch_macpool_pool
        elif 'network_connectivity' in pargs.policy:
            apiHandle = networkconfig_api.NetworkconfigApi(apiClient)
            if pargs.apiMethod == 'by_moid':  apiCall = apiHandle.get_networkconfig_policy_by_moid
            elif pargs.apiMethod == 'get':    apiCall = apiHandle.get_networkconfig_policy_list
            elif pargs.apiMethod == 'create': apiCall = apiHandle.create_networkconfig_policy
            elif pargs.apiMethod == 'patch':  apiCall = apiHandle.patch_networkconfig_policy
        elif 'ntp' in pargs.policy:
            apiHandle = ntp_api.NtpApi(apiClient)
            if pargs.apiMethod == 'by_moid':  apiCall = apiHandle.get_ntp_policy_by_moid
            elif pargs.apiMethod == 'get':    apiCall = apiHandle.get_ntp_policy_list
            elif pargs.apiMethod == 'create': apiCall = apiHandle.create_ntp_policy
            elif pargs.apiMethod == 'patch':  apiCall = apiHandle.patch_ntp_policy
        elif 'organization' == pargs.policy:
            apiHandle = organization_api.OrganizationApi(apiClient)
            if pargs.apiMethod == 'by_moid':  apiCall = apiHandle.get_organization_organization_by_moid
            elif pargs.apiMethod == 'get':    apiCall = apiHandle.get_organization_organization_list
            elif pargs.apiMethod == 'create': apiCall = apiHandle.create_organization_organization
            elif pargs.apiMethod == 'patch':  apiCall = apiHandle.patch_organization_organization
        elif 'persistent_memory' in pargs.policy:
            apiHandle = memory_api.MemoryApi(apiClient)
            if pargs.apiMethod == 'by_moid':  apiCall = apiHandle.get_memory_persistent_memory_policy_by_moid
            elif pargs.apiMethod == 'get':    apiCall = apiHandle.get_memory_persistent_memory_policy_list
            elif pargs.apiMethod == 'create': apiCall = apiHandle.create_memory_persistent_memory_policy
            elif pargs.apiMethod == 'patch':  apiCall = apiHandle.patch_memory_persistent_memory_policy
        elif 'power' in pargs.policy:
            apiHandle = power_api.PowerApi(apiClient)
            if pargs.apiMethod == 'by_moid':  apiCall = apiHandle.get_power_policy_by_moid
            elif pargs.apiMethod == 'get':    apiCall = apiHandle.get_power_policy_list
            elif pargs.apiMethod == 'create': apiCall = apiHandle.create_power_policy
            elif pargs.apiMethod == 'patch':  apiCall = apiHandle.patch_power_policy
        elif 'resource' == pargs.policy:
            apiHandle = resourcepool_api.ResourcepoolApi(apiClient)
            if pargs.apiMethod == 'by_moid':  apiCall = apiHandle.get_resourcepool_pool_by_moid
            elif pargs.apiMethod == 'get':    apiCall = apiHandle.get_resourcepool_pool_list
            elif pargs.apiMethod == 'create': apiCall = apiHandle.create_resourcepool_pool
            elif pargs.apiMethod == 'patch':  apiCall = apiHandle.patch_resourcepool_pool
        elif 'serial_over_lan' in pargs.policy:
            apiHandle = sol_api.SolApi(apiClient)
            if pargs.apiMethod == 'by_moid':  apiCall = apiHandle.get_sol_policy_by_moid
            elif pargs.apiMethod == 'get':    apiCall = apiHandle.get_sol_policy_list
            elif pargs.apiMethod == 'create': apiCall = apiHandle.create_sol_policy
            elif pargs.apiMethod == 'patch':  apiCall = apiHandle.patch_sol_policy
        elif 'smtp' in pargs.policy:
            apiHandle = smtp_api.SmtpApi(apiClient)
            if pargs.apiMethod == 'by_moid':  apiCall = apiHandle.get_smtp_policy_by_moid
            elif pargs.apiMethod == 'get':    apiCall = apiHandle.get_smtp_policy_list
            elif pargs.apiMethod == 'create': apiCall = apiHandle.create_smtp_policy
            elif pargs.apiMethod == 'patch':  apiCall = apiHandle.patch_smtp_policy
        elif 'snmp' in pargs.policy:
            apiHandle = snmp_api.SnmpApi(apiClient)
            if pargs.apiMethod == 'by_moid':  apiCall = apiHandle.get_snmp_policy_by_moid
            elif pargs.apiMethod == 'get':    apiCall = apiHandle.get_snmp_policy_list
            elif pargs.apiMethod == 'create': apiCall = apiHandle.create_snmp_policy
            elif pargs.apiMethod == 'patch':  apiCall = apiHandle.patch_snmp_policy
        elif 'ssh' in pargs.policy:
            apiHandle = ssh_api.SshApi(apiClient)
            if pargs.apiMethod == 'by_moid':  apiCall = apiHandle.get_ssh_policy_by_moid
            elif pargs.apiMethod == 'get':    apiCall = apiHandle.get_ssh_policy_list
            elif pargs.apiMethod == 'create': apiCall = apiHandle.create_ssh_policy
            elif pargs.apiMethod == 'patch':  apiCall = apiHandle.patch_ssh_policy
        elif 'storage' in pargs.policy:
            apiHandle = storage_api.StorageApi(apiClient)
            if 'storage_drive_group' in pargs.policy:
                if pargs.apiMethod == 'by_moid':  apiCall = apiHandle.get_storage_drive_group_by_moid
                elif pargs.apiMethod == 'get':    apiCall = apiHandle.get_storage_drive_group_list
                elif pargs.apiMethod == 'create': apiCall = apiHandle.create_storage_drive_group
                elif pargs.apiMethod == 'patch':  apiCall = apiHandle.patch_storage_drive_group
            elif 'storage' == pargs.policy:
                if pargs.apiMethod == 'by_moid':  apiCall = apiHandle.get_storage_storage_policy_by_moid
                elif pargs.apiMethod == 'get':    apiCall = apiHandle.get_storage_storage_policy_list
                elif pargs.apiMethod == 'create': apiCall = apiHandle.create_storage_storage_policy
                elif pargs.apiMethod == 'patch':  apiCall = apiHandle.patch_storage_storage_policy
        elif 'syslog' in pargs.policy:
            apiHandle = syslog_api.SyslogApi(apiClient)
            if pargs.apiMethod == 'by_moid':  apiCall = apiHandle.get_syslog_policy_by_moid
            elif pargs.apiMethod == 'get':    apiCall = apiHandle.get_syslog_policy_list
            elif pargs.apiMethod == 'create': apiCall = apiHandle.create_syslog_policy
            elif pargs.apiMethod == 'patch':  apiCall = apiHandle.patch_syslog_policy
        elif 'thermal' in pargs.policy:
            apiHandle = thermal_api.ThermalApi(apiClient)
            if pargs.apiMethod == 'by_moid':  apiCall = apiHandle.get_thermal_policy_by_moid
            elif pargs.apiMethod == 'get':    apiCall = apiHandle.get_thermal_policy_list
            elif pargs.apiMethod == 'create': apiCall = apiHandle.create_thermal_policy
            elif pargs.apiMethod == 'patch':  apiCall = apiHandle.patch_thermal_policy
        elif 'uuid' == pargs.policy:
            apiHandle = uuidpool_api.UuidpoolApi(apiClient)
            if pargs.apiMethod == 'by_moid':  apiCall = apiHandle.get_uuidpool_pool_by_moid
            elif pargs.apiMethod == 'get':    apiCall = apiHandle.get_uuidpool_pool_list
            elif pargs.apiMethod == 'create': apiCall = apiHandle.create_uuidpool_pool
            elif pargs.apiMethod == 'patch':  apiCall = apiHandle.patch_uuidpool_pool
        elif 'virtual_kvm' in pargs.policy:
            apiHandle = kvm_api.KvmApi(apiClient)
            if pargs.apiMethod == 'by_moid':  apiCall = apiHandle.get_kvm_policy_by_moid
            elif pargs.apiMethod == 'get':    apiCall = apiHandle.get_kvm_policy_list
            elif pargs.apiMethod == 'create': apiCall = apiHandle.create_kvm_policy
            elif pargs.apiMethod == 'patch':  apiCall = apiHandle.patch_kvm_policy
        elif 'virtual_media' in pargs.policy:
            apiHandle = vmedia_api.VmediaApi(apiClient)
            if pargs.apiMethod == 'by_moid':  apiCall = apiHandle.get_vmedia_policy_by_moid
            elif pargs.apiMethod == 'get':    apiCall = apiHandle.get_vmedia_policy_list
            elif pargs.apiMethod == 'create': apiCall = apiHandle.create_vmedia_policy
            elif pargs.apiMethod == 'patch':  apiCall = apiHandle.patch_vmedia_policy
        elif re.search('ww(n|p)n', pargs.policy):
            apiHandle = fcpool_api.FcpoolApi(apiClient)
            if pargs.apiMethod == 'by_moid':  apiCall = apiHandle.get_fcpool_pool_by_moid
            elif pargs.apiMethod == 'get':    apiCall = apiHandle.get_fcpool_pool_list
            elif pargs.apiMethod == 'create': apiCall = apiHandle.create_fcpool_pool
            elif pargs.apiMethod == 'patch':  apiCall = apiHandle.patch_fcpool_pool
        #=====================================================
        # Setup API Parameters
        #=====================================================
        if pargs.apiMethod == 'by_moid': pargs.apiMethod = 'get_by_moid'
        if 'get' in pargs.apiMethod:
            if 'organization' in pargs.policy: apiArgs = dict(_preload_content = False)
            elif not pargs.get('apiQuery'):
                if re.search('(vlans|vsans)', pargs.policy):
                    names = ", ".join(map(str, pargs.names))
                else: names = "', '".join(pargs.names).strip("', '")
                apiQuery = f"Name in ('{names}') and Organization.Moid eq '{org_moid}'"
                if 'user_role' == pargs.policy:
                    apiQuery = f"Name in ('{names}') and Type eq 'IMC'"
                elif 'serial_number' == pargs.policy:
                    apiQuery = f"Serial in ('{names}')"
                elif 'switch' == pargs.policy:
                    apiQuery = f"Name in ('{names}') and SwitchClusterProfile.Moid eq '{pargs.pmoid}'"
                elif 'vhbas' == pargs.policy:
                    apiQuery = f"Name in ('{names}') and SanConnectivityPolicy.Moid eq '{pargs.pmoid}'"
                elif 'vlans' == pargs.policy:
                    apiQuery = f"VlanId in ({names}) and EthNetworkPolicy.Moid eq '{pargs.pmoid}'"
                elif 'vnics' == pargs.policy:
                    apiQuery = f"Name in ('{names}') and LanConnectivityPolicy.Moid eq '{pargs.pmoid}'"
                elif 'vsans' == pargs.policy:
                    apiQuery = f"VsanId in ({names}) and FcNetworkPolicy.Moid eq '{pargs.pmoid}'"
                elif re.search('ww(n|p)n', pargs.policy):
                    apiQuery = apiQuery + f" and PoolPurpose eq '{pargs.policy.upper()}'"
                apiArgs = dict(filter = apiQuery, _preload_content = False)
            else: apiArgs = dict(filter = pargs.apiQuery, _preload_content = False)
        else: apiArgs = dict(_preload_content = False)
        apiMessage = re.search('method ([a-zA-Z\.\_]+) of', str(apiCall)).group(1)
        #=====================================================
        # Perform the apiCall
        #=====================================================
        try:
            if 'get_by_moid' in pargs.apiMethod: apiResults = json.loads(apiCall(pargs.pmoid, **apiArgs).data)
            elif 'get' in pargs.apiMethod: apiResults = json.loads(apiCall(**apiArgs).data)
            elif 'patch' in pargs.apiMethod:
                apiResults = json.loads(apiCall(pargs.pmoid, pargs.apiBody, **apiArgs).data)
            elif 'create' in pargs.apiMethod:
                apiResults = json.loads(apiCall(pargs.apiBody, **apiArgs).data)
        except ApiException as e:
            print(f"Exception when calling {apiMessage}: {e}\n")
            sys.exit(1)
        #=====================================================
        # Gather Results from the apiCall
        #=====================================================
        if re.search('(get_by_moid|patch)', pargs.apiMethod): kwargs['pmoid'] = pargs.pmoid
        elif 'create' in pargs.apiMethod: kwargs['pmoid'] = apiResults['Moid']
        else: kwargs['pmoids'] = api('results').api_results(pargs, apiResults)
        if re.search('(create|patch)', pargs.apiMethod):
            if pargs.apiBody.get('name'):
                kwargs['pmoids'].update({pargs.apiBody.get('name'):kwargs['pmoid']})
        if 'get_by_moid' in pargs.apiMethod:
            kwargs['results'] = apiResults
        #=====================================================
        # Use for Viewing apiCall Results
        #=====================================================
        if print_response_always == True: print(json.dumps(apiResults, indent=4))
        #=====================================================
        # Print Progress Notifications
        #=====================================================
        if re.search('(create|patch)', pargs.apiMethod):
            validating.completed_item(self.type, pargs, kwargs['pmoid'])
        #=====================================================
        # Return kwargs
        #=====================================================
        return kwargs

    #=====================================================
    # Get Organizations from Intersight
    #=====================================================
    def organizations(self, pargs, **kwargs):
        pargs.apiMethod = 'get'
        pargs.policy    = self.type
        pargs.purpose   = self.type
        #=====================================================
        # Get Organization List from the API
        #=====================================================
        kwargs = api(self.type).calls(pargs, **kwargs)
        kwargs['org_moids'] = kwargs['pmoids']
        return kwargs
