#!/usr/bin/env python3
from intersight.api import asset_api
from intersight.api import compute_api
from intersight.api import server_api
from intersight.api import vnic_api
from intersight.model.organization_organization_relationship import OrganizationOrganizationRelationship
from pathlib import Path
import credentials
import ezfunctions
import jinja2
import json
import pkg_resources
import re
import validating
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

home = Path.home()
template_path = pkg_resources.resource_filename('vmware', '../templates/')

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
        polVars = ezfunctions.process_kwargs(required_args, optional_args, **kwargs)

        try:
            # Validate DNS Servers
            validating.ws_ip_address(row_num, ws, 'DNS', polVars['dns1'])
            dns_servers = [polVars['dns1']]
            validating.ws_ip_address(row_num, ws, 'NTP', polVars['ntp1'])
            ntp_servers = [polVars['ntp1']]
            if polVars['dns2']:
                validating.ws_ip_address(row_num, ws, 'DNS', polVars['dns2'])
                dns_servers.append(polVars['dns2'])
            if polVars['ntp2']:
                validating.ws_ip_address(row_num, ws, 'NTP', polVars['ntp2'])
                ntp_servers.append(polVars['ntp2'])
        except Exception as err:
            Error_Return = '%s\nError on Worksheet %s Row %s.  Please verify Input Information.' % (SystemExit(err), ws, row_num)
            raise ErrException(Error_Return)

        sectSettings = {
            polVars['instance']:{
                'domain':polVars['domain'],
                'dns_servers':dns_servers,
                'ntp_servers':ntp_servers,
                'timezone':polVars['timezone']
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
        polVars = ezfunctions.process_kwargs(required_args, optional_args, **kwargs)

        try:
            # Validate Required Arguments
            hosts = [polVars['hostname'], polVars['vcenter']]
            for host in hosts:
                if re.search('(^\d+\.{3}\d+$|^[a-fA-F0-9]{1,4}\:)', host):
                    validating.ws_ip_address(row_num, ws, 'Name', host)
                else:
                    validating.ws_hostname(row_num, ws, 'Name', host)
            
            # Validate VMKernel IP Addresses
            ipAddresses = [polVars['vmk0'], polVars['vmk1']]
            if polVars['vmk2']:
                ipAddresses.append(polVars['vmk2'])
            for ipAddress in ipAddresses:
                validating.ws_ip_address(row_num, ws, 'IP Address', ipAddress)

        except Exception as err:
            Error_Return = '%s\nError on Worksheet %s Row %s.  Please verify Input Information.' % (SystemExit(err), ws, row_num)
            raise ErrException(Error_Return)

        # Obtain Server Profile Data
        api_client = credentials.config_credentials(home, args)
        api_handle = server_api.ServerApi(api_client)
        query_filter = f"Name eq '{polVars['hostname']}'"
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
            
            # Obtain Server vNICs (Ethernet/Fibre-Channel)
            api_handle = vnic_api.VnicApi(api_client)
            query_filter = f"Profile.Moid eq '{profileMoid}'"
            kwargs = dict(filter=query_filter)
            eth_apiQuery = api_handle.get_vnic_eth_if_list(**kwargs)
            fc_apiQuery = api_handle.get_vnic_fc_if_list(**kwargs)
            vnics = {}
            for item in eth_apiQuery.results:
                vnic_name = item['name']
                mac_address = item['mac_address']
                ngpMoid = item['fabric_eth_network_group_policy'][0].moid
                qosMoid = item['eth_qos_policy']['moid']
                api_handle = vnic_api.VnicApi(api_client)
                qosPolicy = api_handle.get_vnic_eth_qos_policy_by_moid(qosMoid)
                mTu = qosPolicy.mtu
                vnic = {
                    vnic_name: {
                        'mac_address':mac_address,
                        'mtu':mTu,
                    }
                }
                vnics.update(vnic)

            vhbas = {}
            for item in fc_apiQuery.results:
                vhba_name = item['name']
                wwpn_address = item['wwpn']
                fcnpMoid = item['fc_network_policy'].moid
                vhba = {
                    vhba_name: {
                        'wwpn_address':wwpn_address
                    }
                }
                vhbas.update(vhba)

            # Obtain Server vHBAs
            # vnicsSorted = sorted(vnics, key = itemgetter('name'))
            gins = polVars['global_settings']
            vcin = polVars['vcenter']
            
            vswitches = []
            for x in range(1,5):
                if polVars[f'vnic{x}']:
                    vni = polVars[f'vnic{x}']
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
                        if polVars[vmk]:
                            vki = polVars[f'{vmk}_instance']
                            vmkernel = {vmk:{
                                'ip':polVars[vmk],
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
                    'license_type':polVars['license_type'],
                    'ntp_servers': pydict['global_settings'][gins]['ntp_servers'],
                    'serial': UcsSerial,
                    'timezone': pydict['global_settings'][gins]['timezone'],
                    'vcenter': pydict['vcenters'][vcin]['name'],
                    'vhbas':vhbas,
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
        polVars = ezfunctions.process_kwargs(required_args, optional_args, **kwargs)

        try:
            if re.search('(^\d+\.{3}\d+$|^[a-fA-F0-9]{1,4}\:)', polVars['name']):
                validating.ws_ip_address(row_num, ws, 'vCenter', polVars['name'])
                vcenter_name = polVars['name']
            else:
                validating.ws_hostname(row_num, ws, 'vCenter', polVars['name'])
                gins = polVars['global_settings']
                vcenter_name = f"{polVars['name']}.{pydict['global_settings'][gins]['domain']}"

        except Exception as err:
            Error_Return = '%s\nError on Worksheet %s Row %s.  Please verify Input Information.' % (SystemExit(err), ws, row_num)
            raise ErrException(Error_Return)
        
        vsw_dict = {
            polVars['vswitch1']:{'type':polVars['sw1_type']},
            polVars['vswitch2']:{'type':polVars['sw2_type']}
        }
        if polVars['vswitch3']:
            vsw_dict.update({polVars['vswitch3']:{'type':polVars['sw3_type']}})
        if polVars['vswitch4']:
            vsw_dict.update({polVars['vswitch4']:{'type':polVars['sw4_type']}})
        
        sectSettings = {
            polVars['instance']: {
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
        polVars = ezfunctions.process_kwargs(required_args, optional_args, **kwargs)

        if not polVars['vlan_id']:
            polVars['vlan_id'] = ''
        sectSettings = {
            polVars['instance']:{
                'management':polVars['management'],
                'netmask':polVars['netmask'],
                'port_group':polVars['port_group'],
                'vlan_id':polVars['vlan_id'],
                'vmotion':polVars['vmotion'],
                'vswitch':polVars['vswitch']
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
        polVars = ezfunctions.process_kwargs(required_args, optional_args, **kwargs)

        sectSettings = {
            polVars['instance']:{
                'vnic_name':polVars['vnic_name'],
                'vswitch':polVars['vswitch']
            }
        }
        pydict['vnic_dict'].update(sectSettings)
        return pydict
