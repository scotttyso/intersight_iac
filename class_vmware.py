#!/usr/bin/env python3

from easy_functions import process_kwargs
from easy_functions import process_method
from intersight.api import asset_api
from intersight.api import compute_api
from intersight.api import fabric_api
from intersight.api import server_api
from intersight.api import vnic_api
from intersight.model.organization_organization_relationship import OrganizationOrganizationRelationship
from operator import itemgetter
from pathlib import Path
import credentials
import jinja2
import json
import pkg_resources
import re
import validating
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

home = Path.home()
template_path = pkg_resources.resource_filename('class_vmware', 'Templates/')

# Exception Classes
class InsufficientArgs(Exception):
    pass

class ErrException(Exception):
    pass

class InvalidArg(Exception):
    pass

class LoginFailed(Exception):
    pass

class Servers(object):
    # def __init__(self, name_prefix, org, type):
    def __init__(self, ws):
        self.templateLoader = jinja2.FileSystemLoader(
            searchpath=(template_path + f'{ws}/'))
        self.templateEnv = jinja2.Environment(loader=self.templateLoader)
        # self.name_prefix = name_prefix
        # self.org = org
        # self.type = type

    # Method must be called with the following kwargs.
    # Please Refer to the Input Spreadsheet "Notes" in the relevant column headers
    # for Detailed information on the Arguments used by this Method.
    def globals(self, args, pydict, row_num, wb, ws, **kwargs):
        # Dicts for required and optional args
        required_args = {'instance': '',
                         'domain': '',
                         'dns1': '',
                         'ntp1': '',
                         'timezone': ''}
        optional_args = {'dns2': '',
                         'ntp2': ''}

        # Validate inputs, return dict of template vars
        templateVars = process_kwargs(required_args, optional_args, **kwargs)

        try:
            # Validate DNS Servers
            validating.ws_ip_address(row_num, ws, 'DNS', templateVars['dns1'])
            dns_servers = [templateVars['dns1']]
            validating.ws_ip_address(row_num, ws, 'NTP', templateVars['ntp1'])
            ntp_servers = [templateVars['ntp1']]
            if templateVars['dns2']:
                validating.ws_ip_address(row_num, ws, 'DNS', templateVars['dns2'])
                dns_servers.append(templateVars['dns2'])
            if templateVars['ntp2']:
                validating.ws_ip_address(row_num, ws, 'NTP', templateVars['ntp2'])
                ntp_servers.append(templateVars['ntp2'])
        except Exception as err:
            Error_Return = '%s\nError on Worksheet %s Row %s.  Please verify Input Information.' % (SystemExit(err), ws, row_num)
            raise ErrException(Error_Return)

        sectSettings = {
            templateVars['instance']:{
                'domain':templateVars['domain'],
                'dns_servers':dns_servers,
                'ntp_servers':ntp_servers,
                'timezone':templateVars['timezone']
            }
        }
        pydict['global_settings'].update(sectSettings)
        return pydict

    # Method must be called with the following kwargs.
    # Please Refer to the Input Spreadsheet "Notes" in the relevant column headers
    # for Detailed information on the Arguments used by this Method.
    def server(self, args, pydict, row_num, wb, ws, **kwargs):
        # Dicts for required and optional args
        required_args = {'hostname': '',
                         'vcenter': '',
                         'cluster': '',
                         'global_settings': '',
                         'license_type': '',
                         'vmk0': '',
                         'vmk0_instance': '',
                         'vmk1': '',
                         'vmk1_instance': '',
                         'vnic1': '',
                         'vnic2': ''}
        optional_args = {'vmk2': '',
                         'vmk2_instance': '',
                         'vnic3': '',
                         'vnic4': ''}

        # Validate inputs, return dict of template vars
        templateVars = process_kwargs(required_args, optional_args, **kwargs)

        try:
            # Validate Required Arguments
            hosts = [templateVars['hostname'], templateVars['vcenter']]
            for host in hosts:
                if re.search('(^\d+\.{3}\d+$|^[a-fA-F0-9]{1,4}\:)', host):
                    validating.ws_ip_address(row_num, ws, 'Name', host)
                else:
                    validating.ws_hostname(row_num, ws, 'Name', host)
            
            # Validate VMKernel IP Addresses
            ipAddresses = [templateVars['vmk0'], templateVars['vmk1']]
            if templateVars['vmk2']:
                ipAddresses.append(templateVars['vmk2'])
            for ipAddress in ipAddresses:
                validating.ws_ip_address(row_num, ws, 'IP Address', ipAddress)

        except Exception as err:
            Error_Return = '%s\nError on Worksheet %s Row %s.  Please verify Input Information.' % (SystemExit(err), ws, row_num)
            raise ErrException(Error_Return)

        # Obtain Server Profile Data
        api_client = credentials.config_credentials(home, args)
        api_handle = server_api.ServerApi(api_client)
        query_filter = f"Name eq '{templateVars['hostname']}'"
        kwargs = dict(filter=query_filter)
        apiQuery = api_handle.get_server_profile_list(**kwargs)
        if apiQuery.results:
            pResults = apiQuery.results[0]
            profileMoid = pResults.moid
            UcsName = pResults.name
            if pResults.associated_server:
                # Obtain Physical UCS Server Information
                serverMoid = pResults.associated_server.moid
                serverType = pResults.associated_server.object_type
                api_handle = compute_api.ComputeApi(api_client)
                if serverType == 'compute.Blade':
                    apiQuery = api_handle.get_compute_blade_by_moid(serverMoid)
                    UcsDn = 'chassis-' + str(apiQuery.chassis_id) + "/blade-" + str(apiQuery.slot_id)
                else:
                    apiQuery = api_handle.get_compute_rack_unit_by_moid(serverMoid)
                    UcsDn = 'rackunit-' + str(apiQuery.server_id)
                UcsSerial = apiQuery.serial

                api_handle = asset_api.AssetApi(api_client)
                serverReg = api_handle.get_asset_device_registration_by_moid(apiQuery.registered_device.moid)
                # domainReg = api_handle.get_asset_device_registration_by_moid(serverReg.parent_connection.moid)
            
            # Obtain Server vNICs
            api_handle = vnic_api.VnicApi(api_client)
            query_filter = f"Profile.Moid eq '{profileMoid}'"
            kwargs = dict(filter=query_filter)
            apiQuery = api_handle.get_vnic_eth_if_list(**kwargs)
            vnics = {}
            for item in apiQuery.results:
                vnic_name = item['name']
                mac_address = item['mac_address']
                ngpMoid = item['fabric_eth_network_group_policy'][0].moid
                qosMoid = item['eth_qos_policy']['moid']
                api_handle = vnic_api.VnicApi(api_client)
                qosPolicy = api_handle.get_vnic_eth_qos_policy_by_moid(qosMoid)
                mTu = qosPolicy.mtu
                # api_handle = fabric_api.FabricApi(api_client)
                # ngpQuery = api_handle.get_fabric_eth_network_group_policy_by_moid(ngpMoid)
                # netGroupP = ngpQuery.name
                vnic = {
                    vnic_name: {
                        'mac_address':mac_address,
                        'mtu':mTu,
                    }
                }
                vnics.update(vnic)

            # vnicsSorted = sorted(vnics, key = itemgetter('name'))
            gins = templateVars['global_settings']
            vcin = templateVars['vcenter']
            
            vswitches = []
            for x in range(1,5):
                if templateVars[f'vnic{x}']:
                    vni = templateVars[f'vnic{x}']
                    vnic_name = pydict['vnic_dict'][vni]['vnic_name']
                    vsw_name = pydict['vnic_dict'][vni]['vswitch']
                    vswitch = {
                        'name': vsw_name,
                        'type': pydict['vcenters'][vcin]['vswitches'][vsw_name]['type'],
                        'maca': vnics[f'{vnic_name}-A']['mac_address'],
                        'macb': vnics[f'{vnic_name}-B']['mac_address'],
                        'mtu': vnics[f'{vnic_name}-A']['mtu'],
                        'vmks':{}
                    }
                    vmk_list = ['vmk0', 'vmk1', 'vmk2']
                    for vmk in vmk_list:
                        if templateVars[vmk]:
                            vki = templateVars[f'{vmk}_instance']
                            vmkernel = {vmk:{
                                'ip':templateVars[vmk],
                                'management': pydict['vmk_dict'][vki]['management'],
                                'name':vmk,
                                'netmask': pydict['vmk_dict'][vki]['netmask'],
                                'port_group': pydict['vmk_dict'][vki]['port_group'],
                                'vlan_id': pydict['vmk_dict'][vki]['vlan_id'],
                                'vmotion': pydict['vmk_dict'][vki]['vmotion'],
                                'vswitch': pydict['vmk_dict'][vki]['vswitch']
                            }}
                            if vmkernel[vmk]['vswitch'] == vsw_name:
                                vswitch['vmks'].update(vmkernel)
                    
                    # Append Results to the vswitches list
                    vswitches.append(vswitch)

            
            serverDict = {
                f"{UcsName}.{pydict['global_settings'][gins]['domain']}":{
                    'domain':pydict['global_settings'][gins]['domain'],
                    'dns_servers': pydict['global_settings'][gins]['dns_servers'],
                    # 'netpolicy': netGroupP,
                    'license_type':templateVars['license_type'],
                    'ntp_servers': pydict['global_settings'][gins]['ntp_servers'],
                    'serial': UcsSerial,
                    'timezone': pydict['global_settings'][gins]['timezone'],
                    'vcenter': pydict['vcenters'][vcin]['name'],
                    'vswitches': vswitches
                }
            }
            # Print Results
            # print(f"\nServer {UcsName}:")
            # print(f"  * Server Profile Moid is: {profileMoid}")
            # print(f"  * UCS Hardware Moid is:   {serverMoid}")
            # print(f"  * Server Type is:         {serverType}")
            # print(f"  * Serial Number is:       {UcsSerial}")
            # print(f"  * Distinguished Name is:  {UcsDn}")
            # print(f"  * UCS Domain is:  {domainReg.device_hostname[0]}")
            # print(f"  * Distinguished Name is:  {UcsDn}\n")
            pydict['servers'].update(serverDict)
            return pydict

    # Method must be called with the following kwargs.
    # Please Refer to the Input Spreadsheet "Notes" in the relevant column headers
    # for Detailed information on the Arguments used by this Method.
    def vcenter(self, args, pydict, row_num, wb, ws, **kwargs):
        # Dicts for required and optional args
        required_args = {'instance': '',
                         'name': '',
                         'global_settings': '',
                         'vswitch1': '',
                         'sw1_type': '',
                         'vswitch2': '',
                         'sw2_type': '',}
        optional_args = {'vswitch3': '',
                         'sw3_type': '',
                         'vswitch4': '',
                         'sw4_type': '',}

        # Validate inputs, return dict of template vars
        templateVars = process_kwargs(required_args, optional_args, **kwargs)

        try:
            if re.search('(^\d+\.{3}\d+$|^[a-fA-F0-9]{1,4}\:)', templateVars['name']):
                validating.ws_ip_address(row_num, ws, 'vCenter', templateVars['name'])
                vcenter_name = templateVars['name']
            else:
                validating.ws_hostname(row_num, ws, 'vCenter', templateVars['name'])
                gins = templateVars['global_settings']
                vcenter_name = f"{templateVars['name']}.{pydict['global_settings'][gins]['domain']}"

        except Exception as err:
            Error_Return = '%s\nError on Worksheet %s Row %s.  Please verify Input Information.' % (SystemExit(err), ws, row_num)
            raise ErrException(Error_Return)
        
        vsw_dict = {
            templateVars['vswitch1']:{'type':templateVars['sw1_type']},
            templateVars['vswitch2']:{'type':templateVars['sw2_type']}
        }
        if templateVars['vswitch3']:
            vsw_dict.update({templateVars['vswitch3']:{'type':templateVars['sw3_type']}})
        if templateVars['vswitch4']:
            vsw_dict.update({templateVars['vswitch4']:{'type':templateVars['sw4_type']}})
        
        sectSettings = {
            templateVars['instance']: {
                'name':vcenter_name,
                'vswitches':vsw_dict
            }
        }
        pydict['vcenters'].update(sectSettings)
        return pydict

    # Method must be called with the following kwargs.
    # Please Refer to the Input Spreadsheet "Notes" in the relevant column headers
    # for Detailed information on the Arguments used by this Method.
    def vmks(self, args, pydict, row_num, wb, ws, **kwargs):
        # Dicts for required and optional args
        required_args = {'instance': '',
                         'management': '',
                         'netmask': '',
                         'vswitch': '',
                         'port_group': '',
                         'vmotion': ''}
        optional_args = {'vlan_id': ''}

        # Validate inputs, return dict of template vars
        templateVars = process_kwargs(required_args, optional_args, **kwargs)

        if not templateVars['vlan_id']:
            templateVars['vlan_id'] = ''
        sectSettings = {
            templateVars['instance']:{
                'management':templateVars['management'],
                'netmask':templateVars['netmask'],
                'port_group':templateVars['port_group'],
                'vlan_id':templateVars['vlan_id'],
                'vmotion':templateVars['vmotion'],
                'vswitch':templateVars['vswitch']
            }
        }
        pydict['vmk_dict'].update(sectSettings)
        return pydict

    # Method must be called with the following kwargs.
    # Please Refer to the Input Spreadsheet "Notes" in the relevant column headers
    # for Detailed information on the Arguments used by this Method.
    def vnics(self, args, pydict, row_num, wb, ws, **kwargs):
        # Dicts for required and optional args
        required_args = {'instance': '',
                         'vnic_name': '',
                         'vswitch': ''}
        optional_args = {}

        # Validate inputs, return dict of template vars
        templateVars = process_kwargs(required_args, optional_args, **kwargs)

        sectSettings = {
            templateVars['instance']:{
                'vnic_name':templateVars['vnic_name'],
                'vswitch':templateVars['vswitch']
            }
        }
        pydict['vnic_dict'].update(sectSettings)
        return pydict
