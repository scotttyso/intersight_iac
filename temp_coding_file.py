#!/usr/bin/env python3

import jinja2
import json
import os
import pkg_resources
import re
import stdiomask
import subprocess
import validating

ucs_template_path = pkg_resources.resource_filename('lib_ucs', 'ucs_templates/')

class easy_imm_wizard(object):
    def __init__(self, name_prefix, org, type):
        self.templateLoader = jinja2.FileSystemLoader(
            searchpath=(ucs_template_path + '%s/') % (type))
        self.templateEnv = jinja2.Environment(loader=self.templateLoader)
        self.name_prefix = name_prefix
        self.org = org
        self.type = type


    #========================================
    # Easy Deployment Module - Easy Pools
    #========================================
    def easy_domain_network_policies(self, jsonData, easy_jsonData):
        name_prefix = self.name_prefix
        org = self.org
        templateVars = {}
        templateVars["org"] = org

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  The Easy Deployment Module - Pools, will configure pools for a UCS Server Profile')
            print(f'  connected to an IMM Domain.\n')
            print(f'  This wizard will save the output for these pools in the following files:\n')
            print(f'  - Intersight/{org}/{self.type}/bios_policies.auto.tfvars')
            print(f'  - Intersight/{org}/{self.type}/boot_order_policies.auto.tfvars')
            print(f'  - Intersight/{org}/{self.type}/imc_access_policies.auto.tfvars')
            print(f'  - Intersight/{org}/{self.type}/ipmi_over_lan_policies.auto.tfvars')
            print(f'  - Intersight/{org}/{self.type}/local_user_policies.auto.tfvars')
            print(f'  - Intersight/{org}/{self.type}/power_policies.auto.tfvars')
            print(f'  - Intersight/{org}/{self.type}/serial_over_lan_policies.auto.tfvars')
            print(f'  - Intersight/{org}/{self.type}/snmp_policies.auto.tfvars')
            print(f'  - Intersight/{org}/{self.type}/storage_policies.auto.tfvars')
            print(f'  - Intersight/{org}/{self.type}/syslog_policies.auto.tfvars')
            print(f'  - Intersight/{org}/{self.type}/thermal_policies.auto.tfvars')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to run the Easy Deployment Module - Network Configuration?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                loop_count = 1
                policy_loop = False
                while policy_loop == False:
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  Below are the Questions that will be asked by the Policies Portion of the wizard.')
                    print(f'   - Choice to use CDP or LDP for Device Discovery.')
                    print(f'   - Choice to enable Jumbo MTU (9000 MB) or Run standard 1500 MB MTU for vNICs.')
                    print(f'   - LAN Connectivity Policy (vNICs):')
                    print(f'     * VLAN ID for ESXi MGMT')
                    print(f'     * VLAN ID for ESXi vMotion')
                    print(f'     * VLAN ID for ESXi Storage')
                    print(f'     * VLAN List for DATA (Virtual Machines)')
                    print(f'   - SAN Connectivity Policy (vHBAs):')
                    print(f'     * VSAN ID for Fabric A')
                    print(f'     * VSAN ID for Fabric B')
                    print(f'     ** Note: This should not overlap with any of the VLANs assigned to the')
                    print(f'              LAN Connectivity Policies.')
                    print(f'   - Local User Policy (Required for KVM Access).')
                    print(f'     * user and role')
                    print(f'     * user password (strong passwords enforced)')
                    print(f'   - SNMP Policy')
                    print(f'     * Contact')
                    print(f'     * Location')
                    print(f'     * SNMPv3 Users (optional)')
                    print(f'     * SNMPv3 Trap Servers (optional)')
                    print(f'   - Syslog Policy - (Optional)')
                    print(f'     * Remote Syslog Server(s)')
                    print(f'\n-------------------------------------------------------------------------------------------\n')

                    # Get List of VLAN's from the Domain Policies
                    policy_list = [
                        'policies_vlans.vlan_policies.vlan_policy',
                    ]
                    templateVars["allow_opt_out"] = False
                    for policy in policy_list:
                        vlan_policy,policyData = policy_select_loop(jsonData, easy_jsonData, name_prefix, policy, **templateVars)

                    vlan_list = []
                    for item in policyData['vlan_policies'][0][vlan_policy][0]['vlans']:
                        for k, v in item.items():
                            vlan_list.append(v[0]['vlan_list'])

                    vlan_convert = ''
                    for vlan in vlan_list:
                        if vlan_convert == '':
                            vlan_convert = str(vlan)
                        else:
                            vlan_convert = vlan_convert + ',' + str(vlan)

                    vlan_policy_list = vlan_list_full(vlan_convert)

                    templateVars["multi_select"] = False
                    jsonVars = jsonVars = easy_jsonData['policies']['fabric.EthNetworkControlPolicy']

                    # Neighbor Discovery Protocol
                    templateVars["var_description"] = jsonVars['discoveryProtocol']['description']
                    templateVars["jsonVars"] = sorted(jsonVars['discoveryProtocol']['enum'])
                    templateVars["defaultVar"] = jsonVars['discoveryProtocol']['default']
                    templateVars["varType"] = 'Neighbor Discovery Protocol'
                    neighbor_discovery = variablesFromAPI(**templateVars)

                    # MTU
                    templateVars["Description"] = 'MTU for Server vNICs'
                    templateVars["varInput"] = f'Do you want to enable Jumbo MTU?  Enter "Y" or "N"'
                    templateVars["varDefault"] = 'Y'
                    templateVars["varName"] = 'MTU'
                    answer = varBoolLoop(**templateVars)
                    if answer == True:
                        mtu = 9000
                    else:
                        mtu = 1500

                    # Management VLAN
                    valid = False
                    while valid == False:
                        templateVars["Description"] = 'Management VLAN Identifier'
                        templateVars["varInput"] = 'Enter the VLAN ID for MGMT.'
                        templateVars["varDefault"] = 1
                        templateVars["varName"] = 'Management VLAN ID'
                        templateVars["minNum"] = 1
                        templateVars["maxNum"] = 4094
                        mgmt_vlan = varNumberLoop(**templateVars)
                        valid = validate_vlan_in_policy(vlan_policy_list, mgmt_vlan)

                    # vMotion VLAN
                    valid = False
                    while valid == False:
                        templateVars["Description"] = 'vMotion VLAN Identifier'
                        templateVars["varInput"] = 'Enter the VLAN ID for vMotion.'
                        templateVars["varDefault"] = 2
                        templateVars["varName"] = 'Management VLAN ID'
                        templateVars["minNum"] = 1
                        templateVars["maxNum"] = 4094
                        vmotion_vlan = varNumberLoop(**templateVars)
                        valid = validate_vlan_in_policy(vlan_policy_list, vmotion_vlan)

                    # Storage VLAN
                    valid = False
                    while valid == False:
                        templateVars["Description"] = 'Storage VLAN Identifier'
                        templateVars["varInput"] = 'Enter the VLAN ID for Storage.'
                        templateVars["varDefault"] = 3
                        templateVars["varName"] = 'Storage VLAN ID'
                        templateVars["minNum"] = 1
                        templateVars["maxNum"] = 4094
                        storage_vlan = varNumberLoop(**templateVars)
                        valid = validate_vlan_in_policy(vlan_policy_list, storage_vlan)

                    valid = False
                    while valid == False:
                        VlanList = input('Enter the VLAN or List of VLANs to add to the DATA (Virtual Machine) vNICs: ')
                        if not VlanList == '':
                            vlanListExpanded = vlan_list_full(VlanList)
                            valid_vlan = True
                            vlans_not_in_domain_policy = []
                            for vlan in vlanListExpanded:
                                valid_vlan = validating.number_in_range('VLAN ID', vlan, 1, 4094)
                                if valid_vlan == False:
                                    continue
                                else:
                                    vlan_count = 0
                                    for vlans in vlan_list:
                                        if int(vlan) == int(vlans):
                                            vlan_count += 1
                                            break
                                    if vlan_count == 0:
                                        vlans_not_in_domain_policy.append(vlan)


                            if len(vlans_not_in_domain_policy) > 0:
                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                print(f'  Error with VLAN(s) assignment!!  The following VLAN(s) are missing.')
                                print(f'  - Domain VLAN Policy: "{vlan_policy}"')
                                print(f'  - Missing VLANs: {vlans_not_in_domain_policy}')
                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                valid_vlan = False

                            native_count = 0
                            nativeVlan = ''
                            if valid_vlan == True:
                                nativeValid = False
                                while nativeValid == False:
                                    nativeVlan = input('Do you want to Configure one of the VLANs as a Native VLAN?  [press enter to skip]:')
                                    if nativeVlan == '':
                                        nativeValid = True
                                        valid = True
                                    else:
                                        for vlan in vlanListExpanded:
                                            if int(nativeVlan) == int(vlan):
                                                native_count = 1
                                        if not native_count == 1:
                                            print(f'\n-------------------------------------------------------------------------------------------\n')
                                            print(f'  Error!! The Native VLAN was not in the Allowed List.')
                                            print(f'  Allowed VLAN List is: "{vlan_list}"')
                                            print(f'\n-------------------------------------------------------------------------------------------\n')
                                        else:
                                            nativeValid = True
                                            valid = True

                        else:
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            print(f'  The allowed vlan list can be in the format of:')
                            print(f'     5 - Single VLAN')
                            print(f'     1-10 - Range of VLANs')
                            print(f'     1,2,3,4,5,11,12,13,14,15 - List of VLANs')
                            print(f'     1-10,20-30 - Ranges and Lists of VLANs')
                            print(f'\n-------------------------------------------------------------------------------------------\n')

                    fabrics = ['A', 'B']
                    for x in fabrics:
                        valid = False
                        while valid == False:
                            templateVars["Description"] = f'VSAN Identifier for Fabric {x}'
                            templateVars["varInput"] = 'What VSAN Identifier do you want to Assign to Fabric {x}?'
                            if x == 'A':
                                templateVars["varDefault"] = 100
                            else:
                                templateVars["varDefault"] = 200
                            templateVars["varName"] = 'VSAN'
                            templateVars["minNum"] = 1
                            templateVars["maxNum"] = 4094
                            vsan_id = varNumberLoop(**templateVars)
                        
                            policy_list = [
                                'policies.vsan_policies.vsan_policy'
                            ]
                            templateVars["allow_opt_out"] = False
                            for policy in policy_list:
                                vsan_policy,policyData = policy_select_loop(jsonData, easy_jsonData, name_prefix, policy, **templateVars)

                            vsan_list = []
                            for item in policyData['vsan_policies'][0][vsan_policy][0]['vsans']:
                                for key, value in item.items():
                                    vsan_list.append(value[0]['vsan_id'])

                            vsan_string = ''
                            for vsan in vsan_list:
                                if vsan_string == '':
                                    vsan_string = str(vsan)
                                else:
                                    vsan_string = vsan_string + ',' + str(vsan)
                            vsan_list = vlan_list_full(vsan_string)
                            vsan_count = 0
                            for vsan in vsan_list:
                                if int(vsan_id) == int(vsan):
                                    vsan_count = 1
                                    break
                            if vsan_count == 0:
                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                print(f'  Error with VSAN!!  The VSAN {vsan_id} is not in the VSAN Policy')
                                print(f'  {vsan_policy}.  Options are {vsan_list}.')
                                print(f'\n-------------------------------------------------------------------------------------------\n')
                            else:
                                templateVars[f"vsan_{x}"] = vsan_id
                                valid = True
                    
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  Network Configuration Variables:"')
                    print(f'    MGMT VLAN     = {mgmt_vlan}')
                    print(f'    vMotion VLAN  = {vmotion_vlan}')
                    print(f'    Storage VLAN  = {storage_vlan}')
                    print(f'    Data VLANs    = "{VlanList}"')
                    print(f'    VSAN Fabric A = {templateVars["vsan_A"]}')
                    print(f'    VSAN Fabric B = {templateVars["vsan_B"]}')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
                        if confirm_policy == 'Y' or confirm_policy == '':
                            confirm_policy = 'Y'

                            #_______________________________________________________________________
                            #
                            # Configure Ethernet Adapter Policy
                            #_______________________________________________________________________

                            templateVars["initial_write"] = True
                            templateVars["policy_type"] = 'Ethernet Adapter Policy'
                            templateVars["header"] = '%s Variables' % (templateVars["policy_type"])
                            templateVars["template_file"] = 'template_open.jinja2'
                            templateVars["template_type"] = 'ethernet_adapter_policies'

                            # Open the Template file
                            write_to_template(self, **templateVars)
                            templateVars["initial_write"] = False

                            name = 'VMware'
                            templateVars["name"] = name
                            templateVars["description"] = f'{name} Ethernet Adapter Policy'
                            templateVars["adapter_template"] = 'VMware'

                            # Write Policies to Template File
                            templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
                            write_to_template(self, **templateVars)

                            # Close the Template file
                            templateVars["template_file"] = 'template_close.jinja2'
                            write_to_template(self, **templateVars)

                            #_______________________________________________________________________
                            #
                            # Configure Ethernet Network Control Policy
                            #_______________________________________________________________________

                            templateVars["initial_write"] = True
                            templateVars["policy_type"] = 'Ethernet Network Control Policy'
                            templateVars["header"] = '%s Variables' % (templateVars["policy_type"])
                            templateVars["template_file"] = 'template_open.jinja2'
                            templateVars["template_type"] = 'ethernet_network_control_policies'

                            # Open the Template file
                            write_to_template(self, **templateVars)
                            templateVars["initial_write"] = False

                            name = neighbor_discovery
                            templateVars["name"] = name
                            templateVars["description"] = f'{name} Ethernet Network Control Policy'
                            templateVars["action_on_uplink_fail"] = "linkDown"
                            if neighbor_discovery == 'CDP':
                                templateVars["cdp_enable"] = True
                            else:
                                templateVars["cdp_enable"] = False
                            if neighbor_discovery == 'LLDP':
                                templateVars["lldp_enable_receive"] = True
                                templateVars["lldp_enable_transmit"] = True
                            else:
                                templateVars["lldp_enable_receive"] = False
                                templateVars["lldp_enable_transmit"] = False
                            templateVars["mac_register_mode"] = "nativeVlanOnly"
                            templateVars["mac_security_forge"] = "allow"

                            # Write Policies to Template File
                            templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
                            write_to_template(self, **templateVars)

                            # Close the Template file
                            templateVars["template_file"] = 'template_close.jinja2'
                            write_to_template(self, **templateVars)

                            #_______________________________________________________________________
                            #
                            # Configure Ethernet Network Group Policy
                            #_______________________________________________________________________

                            templateVars["initial_write"] = True
                            templateVars["policy_type"] = 'Ethernet Network Group Policy'
                            templateVars["header"] = '%s Variables' % (templateVars["policy_type"])
                            templateVars["template_file"] = 'template_open.jinja2'
                            templateVars["template_type"] = 'ethernet_network_group_policies'

                            # Open the Template file
                            write_to_template(self, **templateVars)
                            templateVars["initial_write"] = False

                            names = ['MGMT', 'VMOTION', 'STORAGE', 'DATA']
                            for x in names:
                                if x == 'MGMT':
                                    allowed_vlans = mgmt_vlan
                                    native_vlan = mgmt_vlan
                                elif x == 'MGMT':
                                    allowed_vlans = vmotion_vlan
                                    native_vlan = vmotion_vlan
                                elif x == 'MGMT':
                                    allowed_vlans = storage_vlan
                                    native_vlan = storage_vlan
                                elif x == 'DATA':
                                    allowed_vlans = VlanList
                                    native_vlan = nativeVlan
                                name = x
                                templateVars["name"] = name
                                templateVars["description"] = f'{name} Ethernet Network Group Policy'
                                templateVars["allowed_vlans"] = allowed_vlans
                                if not native_vlan == '':
                                    templateVars["native_vlan"] = native_vlan
                                else:
                                    templateVars["native_vlan"] = ''
                                    templateVars.pop('native_vlan')

                                # Write Policies to Template File
                                templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
                                write_to_template(self, **templateVars)

                            # Close the Template file
                            templateVars["template_file"] = 'template_close.jinja2'
                            write_to_template(self, **templateVars)

                            #_______________________________________________________________________
                            #
                            # Configure Ethernet QoS Policy
                            #_______________________________________________________________________

                            templateVars["initial_write"] = True
                            templateVars["policy_type"] = 'Ethernet QoS Policy'
                            templateVars["header"] = '%s Variables' % (templateVars["policy_type"])
                            templateVars["template_file"] = 'template_open.jinja2'
                            templateVars["template_type"] = 'ethernet_qos_policies'

                            # Open the Template file
                            write_to_template(self, **templateVars)
                            templateVars["initial_write"] = False

                            names = ['Bronze', 'Gold', 'Platinum', 'Silver']
                            for x in names:
                                name = x
                                templateVars["name"] = name
                                templateVars["description"] = f'{name} Ethernet QoS Policy'
                                templateVars["allowed_vlans"] = mgmt_vlan
                                templateVars["native_vlan"] = mgmt_vlan
                                templateVars["burst"] = 1024
                                templateVars["enable_trust_host_cos"] = False
                                templateVars["priority"] = x
                                templateVars["mtu"] = mtu
                                templateVars["rate_limit"] = 0

                                # Write Policies to Template File
                                templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
                                write_to_template(self, **templateVars)

                            # Close the Template file
                            templateVars["template_file"] = 'template_close.jinja2'
                            write_to_template(self, **templateVars)

                            #_______________________________________________________________________
                            #
                            # Configure Fibre Channel Adapter Policy
                            #_______________________________________________________________________

                            templateVars["initial_write"] = True
                            templateVars["policy_type"] = 'Fibre-Channel Adapter Policy'
                            templateVars["header"] = '%s Variables' % (templateVars["policy_type"])
                            templateVars["template_file"] = 'template_open.jinja2'
                            templateVars["template_type"] = 'fibre_channel_adapter_policies'

                            # Open the Template file
                            write_to_template(self, **templateVars)
                            templateVars["initial_write"] = False

                            name = 'VMware'
                            templateVars["name"] = name
                            templateVars["description"] = f'{name} Fibre-Channel Adapter Policy'
                            templateVars["adapter_template"] = 'VMware'

                            # Write Policies to Template File
                            templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
                            write_to_template(self, **templateVars)

                            # Close the Template file
                            templateVars["template_file"] = 'template_close.jinja2'
                            write_to_template(self, **templateVars)

                            #_______________________________________________________________________
                            #
                            # Configure Fibre Channel Network Policy
                            #_______________________________________________________________________

                            templateVars["initial_write"] = True
                            templateVars["policy_type"] = 'Fibre-Channel Network Policy'
                            templateVars["header"] = '%s Variables' % (templateVars["policy_type"])
                            templateVars["template_file"] = 'template_open.jinja2'
                            templateVars["template_type"] = 'fibre_channel_network_policies'

                            # Open the Template file
                            write_to_template(self, **templateVars)
                            templateVars["initial_write"] = False

                            fabrics = ['A', 'B']
                            for x in fabrics:
                                name = f'Fabric_{x}'
                                templateVars["name"] = name
                                templateVars["description"] = f'{name} Fibre-Channel Network Policy'
                                templateVars["default_vlan_id"] = 0
                                templateVars["vsan_id"] = templateVars[f"vsan_{x}"]

                                # Write Policies to Template File
                                templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
                                write_to_template(self, **templateVars)

                            # Close the Template file
                            templateVars["template_file"] = 'template_close.jinja2'
                            write_to_template(self, **templateVars)

                            #_______________________________________________________________________
                            #
                            # Configure Fibre Channel QoS Policy
                            #_______________________________________________________________________

                            templateVars["initial_write"] = True
                            templateVars["policy_type"] = 'Fibre-Channel QoS Policy'
                            templateVars["header"] = '%s Variables' % (templateVars["policy_type"])
                            templateVars["template_file"] = 'template_open.jinja2'
                            templateVars["template_type"] = 'fibre_channel_qos_policies'

                            # Open the Template file
                            write_to_template(self, **templateVars)
                            templateVars["initial_write"] = False

                            name = 'FC_QoS'
                            templateVars["name"] = name
                            templateVars["description"] = f'{name} Fibre-Channel QoS Policy'
                            templateVars["burst"] = 1024
                            templateVars["max_data_field_size"] = 2112
                            templateVars["rate_limit"] = 0

                            # Write Policies to Template File
                            templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
                            write_to_template(self, **templateVars)

                            # Close the Template file
                            templateVars["template_file"] = 'template_close.jinja2'
                            write_to_template(self, **templateVars)

                            #_______________________________________________________________________
                            #
                            # LAN Connectivity Policy
                            #_______________________________________________________________________

                            templateVars["initial_write"] = True
                            templateVars["policy_type"] = 'LAN Connectivity Policy'
                            templateVars["header"] = '%s Variables' % (templateVars["policy_type"])
                            templateVars["template_file"] = 'template_open.jinja2'
                            templateVars["template_type"] = 'lan_connectivity_policies'

                            # Open the Template file
                            write_to_template(self, **templateVars)
                            templateVars["initial_write"] = False

                            name = 'LAN_Policy'
                            templateVars["name"] = name
                            templateVars["description"] = f'{name} LAN Connectivity Policy'
                            templateVars["enable_azure_stack_host_qos"] = False
                            templateVars["iqn_allocation_type"] = "None"
                            templateVars["vnic_placement_mode"] = "custom"
                            templateVars["target_platform"] = "FIAttached"
                            templateVars["vnics"] = []

                            names = ['MGMT_Silver', 'VMOTION_Bronze', 'STORAGE_Platinum', 'DATA_Gold']
                            Order = 0
                            for x in names:
                                vname = x.split('_')[0]
                                qos = x.split('_')[1]
                                for y in fabrics:
                                    vnic = {
                                        'cdn_source':'vnic',
                                        'enable_failover':False,
                                        'ethernet_adapter_policy':'VMware',
                                        'ethernet_network_control_policy':neighbor_discovery,
                                        'ethernet_network_group_policy':vname,
                                        'ethernet_qos_policy':qos,
                                        'mac_address_allocation_type':'POOL',
                                        'mac_address_pool':f'Fabric_{y}',
                                        'name':f'{vname}-{y}',
                                        'placement_pci_link':0,
                                        'placement_pci_order':Order,
                                        'placement_slot_id':'MLOM',
                                        'placement_switch_id':y
                                    }
                                    templateVars["vnics"].append(vnic)
                                    Order += 1

                            # Write Policies to Template File
                            templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
                            write_to_template(self, **templateVars)

                            # Close the Template file
                            templateVars["template_file"] = 'template_close.jinja2'
                            write_to_template(self, **templateVars)

                            #_______________________________________________________________________
                            #
                            # SAN Connectivity Policy
                            #_______________________________________________________________________

                            templateVars["initial_write"] = True
                            templateVars["policy_type"] = 'SAN Connectivity Policy'
                            templateVars["header"] = '%s Variables' % (templateVars["policy_type"])
                            templateVars["template_file"] = 'template_open.jinja2'
                            templateVars["template_type"] = 'san_connectivity_policies'

                            # Open the Template file
                            write_to_template(self, **templateVars)
                            templateVars["initial_write"] = False

                            name = 'SAN_Policy'
                            templateVars["name"] = name
                            templateVars["description"] = f'{name} SAN Connectivity Policy'
                            templateVars["target_platform"] = "FIAttached"
                            templateVars["vhba_placement_mode"] = "custom"
                            templateVars["vhbas"] = []
                            templateVars["wwnn_allocation_type"] = "POOL"
                            templateVars["wwnn_pool"] = "WWNN_POOL"

                            for x in fabrics:
                                vhba = {
                                    'fibre_channel_adapter_policy':'VMware',
                                    'fibre_channel_network_policy':f'Fabric_{x}',
                                    'fibre_channel_qos_policy':'FC_QoS',
                                    'name':f'HBA-{x}',
                                    'persistent_lun_bindings':False,
                                    'placement_pci_link':0,
                                    'placement_pci_order':Order,
                                    'placement_slot_id':'MLOM',
                                    'placement_switch_id':y,
                                    'wwpn_allocation_type':'POOL',
                                    'wwpn_pool':f'Fabric_{x}',
                                }
                                templateVars["vhbas"].append(vhba)
                                Order += 1

                            # Write Policies to Template File
                            templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
                            write_to_template(self, **templateVars)

                            # Close the Template file
                            templateVars["template_file"] = 'template_close.jinja2'
                            write_to_template(self, **templateVars)


                        elif confirm_policy == 'N':
                            print(f'\n------------------------------------------------------\n')
                            print(f'  Starting Section over.')
                            print(f'\n------------------------------------------------------\n')
                            valid_confirm = True

                        else:
                            print(f'\n------------------------------------------------------\n')
                            print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                            print(f'\n------------------------------------------------------\n')


            elif configure == 'N':
                configure_loop = True
            else:
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                print(f'\n-------------------------------------------------------------------------------------------\n')

    #========================================
    # Storage Policy Module
    #========================================
    def storage_policies(self, jsonData, easy_jsonData):
        name_prefix = self.name_prefix
        name_suffix = 'storage'
        org = self.org
        policy_names = []
        policy_type = 'Storage Policy'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'storage_policies'

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  A {policy_type} allows you to create drive groups, virtual drives, configure the ')
            print(f'  storage capacity of a virtual drive, and configure the M.2 RAID controllers.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - Intersight/{org}/{self.type}/{templateVars["template_type"]}.auto.tfvars')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure a {policy_type}?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                loop_count = 1
                policy_loop = False
                while policy_loop == False:

                    if not name_prefix == '':
                        name = '%s_%s' % (name_prefix, name_suffix)
                    else:
                        name = '%s_%s' % (org, name_suffix)

                    templateVars["name"] = policy_name(name, policy_type)
                    templateVars["descr"] = policy_descr(templateVars["name"], policy_type)

                    templateVars["multi_select"] = False
                    jsonVars = jsonData['components']['schemas']['storage.StoragePolicy']['allOf'][1]['properties']

                    templateVars["Description"] = jsonVars['GlobalHotSpares']['description']
                    templateVars["varInput"] = 'What is the name for this vNIC?'
                    templateVars["varName"] = 'Specify the disks that are to be used as hot spares,\n globally for all the RAID groups. [press enter to skip]:'
                    templateVars["varRegex"] = jsonVars['GlobalHotSpares']['pattern']
                    templateVars["minLength"] = 1
                    templateVars["maxLength"] = 128
                    templateVars["global_hot_spares"] = varStringLoop(**templateVars)

                    templateVars["Description"] = jsonVars['UseJbodForVdCreation']['description']
                    templateVars["varInput"] = f'Do you want to Use JBOD drives for Virtual Drive creation?'
                    templateVars["varDefault"] = 'N'
                    templateVars["varName"] = 'Use Jbod For Vd Creation'
                    templateVars["use_jbod_for_vd_creation"] = varBoolLoop(**templateVars)

                    templateVars["var_description"] = jsonVars['UnusedDisksState']['description']
                    templateVars["jsonVars"] = sorted(jsonVars['UnusedDisksState']['enum'])
                    templateVars["defaultVar"] = jsonVars['UnusedDisksState']['default']
                    templateVars["varType"] = 'Unused Disks State'
                    templateVars["unused_disks_state"] = variablesFromAPI(**templateVars)

                    templateVars["Description"] = jsonVars['M2VirtualDrive']['description']
                    templateVars["varInput"] = f'Do you want to Enable the M.2 Virtual Drive Configuration?'
                    templateVars["varDefault"] = 'N'
                    templateVars["varName"] = 'M.2 Virtual Drive'
                    templateVars["m2_configuration"] = varBoolLoop(**templateVars)

                    if templateVars["m2_configuration"] == True:
                        jsonVars = jsonData['components']['schemas']['storage.StoragePolicy']['allOf'][1]['properties']

                        templateVars["var_description"] = jsonVars['ControllerSlot']['description']
                        templateVars["jsonVars"] = sorted(jsonVars['ControllerSlot']['enum'])
                        templateVars["defaultVar"] = jsonVars['ControllerSlot']['default']
                        templateVars["varType"] = 'Controller Slot'
                        templateVars["controller_slot"] = variablesFromAPI(**templateVars)

                        templateVars["m2_configuration"] = {
                            'controller_slot':templateVars["controller_slot"],
                            'enable':True
                        }
                    else:
                        templateVars.pop('m2_configuration')

                    templateVars["Description"] = 'Drive Group Configuration - Enable to add RAID drive groups that can be used to create virtual drives. '\
                    'You can also specify the Global Hot Spares information.'
                    templateVars["varInput"] = f'Do you want to Configure Drive Groups?'
                    templateVars["varDefault"] = 'N'
                    templateVars["varName"] = 'Drive Groups'
                    templateVars["drive_group"] = varBoolLoop(**templateVars)

                    if templateVars["drive_group"] == True:
                        templateVars["drive_groups"] = []
                        inner_loop_count = 1
                        drive_group = []
                        drive_group_loop = False
                        while drive_group_loop == False:
                            jsonVars = jsonData['components']['schemas']['storage.DriveGroup']['allOf'][1]['properties']

                            templateVars["Description"] = jsonVars['Name']['description']
                            templateVars["varInput"] = 'Enter the Drive Group Name:'
                            templateVars["varName"] = 'Drive Group Name'
                            templateVars["varRegex"] = jsonVars['Name']['pattern']
                            templateVars["minLength"] = 1
                            templateVars["maxLength"] = 60
                            Name = varStringLoop(**templateVars)

                            templateVars["var_description"] = jsonVars['RaidLevel']['description']
                            templateVars["jsonVars"] = sorted(jsonVars['RaidLevel']['enum'])
                            templateVars["defaultVar"] = jsonVars['RaidLevel']['default']
                            templateVars["varType"] = 'Raid Level'
                            raid_level = variablesFromAPI(**templateVars)

                            jsonVars = jsonData['components']['schemas']['storage.ManualDriveGroup']['allOf'][1]['properties']

                            if not raid_level == 'Raid0':
                                templateVars["Description"] = jsonVars['DedicatedHotSpares']['description']
                                templateVars["varInput"] = 'Enter the Drives to add as Dedicated Hot Spares [press enter to skip]:'
                                templateVars["varName"] = 'Dedicated Hot Spares'
                                templateVars["varRegex"] = jsonVars['DedicatedHotSpares']['pattern']
                                templateVars["minLength"] = 1
                                templateVars["maxLength"] = 60
                                DedicatedHotSpares = varStringLoop(**templateVars)
                            else:
                                DedicatedHotSpares = ''

                            SpanGroups = []
                            if re.fullmatch('^Raid(10|50|60)$', raid_level):
                                templateVars["var_description"] = jsonVars['SpanGroups']['items']['description']
                                templateVars["jsonVars"] = [2, 4, 6, 8]
                                templateVars["defaultVar"] = 2
                                templateVars["varType"] = 'Span Groups'
                                Spans = variablesFromAPI(**templateVars)
                                if Spans == 2:
                                    Spans = [0, 1]
                                elif Spans == 4:
                                    Spans = [0, 1, 2, 3]
                                elif Spans == 6:
                                    Spans = [0, 1, 2, 3, 4, 5]
                                elif Spans == 8:
                                    Spans = [0, 1, 2, 3, 4, 5, 6, 7]

                                jsonVars = jsonData['components']['schemas']['storage.DriveGroup']['allOf'][1]['properties']
                                for span in Spans:
                                    templateVars["Description"] = jsonVars['Slots']['description']
                                    templateVars["varDefault"] = '1-2'
                                    templateVars["varInput"] = 'Enter the Drive Slots for Drive Array Span {span}. [1-2]:'
                                    templateVars["varName"] = 'Drive Slots'
                                    templateVars["varRegex"] = jsonVars['Slots']['pattern']
                                    templateVars["minLength"] = 1
                                    templateVars["maxLength"] = 10
                                    SpanGroups.append({span:varStringLoop(**templateVars)})
                            elif re.fullmatch('^Raid(0|1|5|6)$', raid_level):
                                jsonVars = jsonData['components']['schemas']['storage.DriveGroup']['allOf'][1]['properties']

                                templateVars["Description"] = jsonVars['Slots']['description']
                                templateVars["varDefault"] = '1-2'
                                templateVars["varInput"] = f'Enter the Drive Slots for Drive Array Span 0. [1-2]:'
                                templateVars["varName"] = 'Drive Slots'
                                templateVars["varRegex"] = jsonVars['Slots']['pattern']
                                templateVars["minLength"] = 1
                                templateVars["maxLength"] = 10
                                SpanGroups.append({0:varStringLoop(**templateVars)})

                            virtualDrives = []
                            sub_loop_count = 1
                            sub_loop = False
                            while sub_loop == False:
                                print('hello')

                                jsonVars = jsonData['components']['schemas']['storage.DriveGroup']['allOf'][1]['properties']

                                templateVars["Description"] = jsonVars['Name']['description']
                                templateVars["varInput"] = 'Enter the name of the drive group:'
                                templateVars["varName"] = 'Drive Group Name'
                                templateVars["varRegex"] = jsonVars['Name']['pattern']
                                templateVars["minLength"] = 1
                                templateVars["maxLength"] = 60
                                Name = varStringLoop(**templateVars)

                                templateVars["var_description"] = jsonVars['RaidLevel']['description']
                                templateVars["jsonVars"] = sorted(jsonVars['RaidLevel']['enum'])
                                templateVars["defaultVar"] = jsonVars['RaidLevel']['default']
                                templateVars["varType"] = 'Raid Level'
                                raid_level = variablesFromAPI(**templateVars)
                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                for item in virtualDrives:
                                    for k, v in item.items():
                                        if k == 'name':
                                            print(f'        "{k}" = ''{')
                                    for k, v in item.items():
                                        if k == 'access_policy':
                                            print(f'          access_policy       = "{v}"')
                                        elif k == 'boot_drive':
                                            print(f'          boot_drive          = "{v}"')
                                        elif k == 'disk_cache':
                                            print(f'          disk_cache          = "{v}"')
                                        elif k == 'expand_to_available':
                                            print(f'          expand_to_available = "{v}"')
                                        elif k == 'read_policy':
                                            print(f'          read_policy         = "{v}"')
                                        elif k == 'size':
                                            print(f'          size                = "{v}"')
                                        elif k == 'strip_size':
                                            print(f'          strip_size          = "{v}"')
                                        elif k == 'write_policy':
                                            print(f'          write_policy        = "{v}"')
                                            print(f'        ''}')
                                print(f'      ''}')
                                print(f'    ''}')
                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                valid_confirm = False
                                while valid_confirm == False:
                                    confirm_v = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
                                    if confirm_v == 'Y' or confirm_v == '':
                                        templateVars["drive_groups"].append(drive_group)
                                        valid_exit = False
                                        while valid_exit == False:
                                            loop_exit = input(f'Would You like to Configure another Drive Group?  Enter "Y" or "N" [N]: ')
                                            if loop_exit == 'Y':
                                                inner_loop_count += 1
                                                valid_confirm = True
                                                valid_exit = True
                                            elif loop_exit == 'N' or loop_exit == '':
                                                drive_group_loop = True
                                                valid_confirm = True
                                                valid_exit = True
                                            else:
                                                print(f'\n------------------------------------------------------\n')
                                                print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                                                print(f'\n------------------------------------------------------\n')

                                    elif confirm_v == 'N':
                                        print(f'\n-------------------------------------------------------------------------------------------\n')
                                        print(f'  Starting Remote Host Configuration Over.')
                                        print(f'\n-------------------------------------------------------------------------------------------\n')
                                        valid_confirm = True
                                    else:
                                        print(f'\n------------------------------------------------------\n')
                                        print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                                        print(f'\n------------------------------------------------------\n')
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            print(f'    drive_group = ''{')
                            print(f'      manual_drive_group = ''{')
                            print(f'        dedicated_hot_spares = "{DedicatedHotSpares}"')
                            print(f'        drive_array_spans = ''{')
                            for item in SpanGroups:
                                for k, v in item.items():
                                    print(f'          "{k}" = ''{')
                                    print(f'            slots = "{v}"')
                                    print(f'          ''}')
                            print(f'        ''}')
                            print(f'      ''}')
                            print(f'      raid_level = "{raid_level}"')
                            print(f'      virtual_drives = ''{')
                            for item in virtualDrives:
                                print(f'        "{Name}" = ''{')
                                for k, v in item.items():
                                    if k == 'access_policy':
                                        print(f'          access_policy       = "{v}"')
                                    elif k == 'boot_drive':
                                        print(f'          boot_drive          = "{v}"')
                                    elif k == 'disk_cache':
                                        print(f'          disk_cache          = "{v}"')
                                    elif k == 'expand_to_available':
                                        print(f'          expand_to_available = "{v}"')
                                    elif k == 'read_policy':
                                        print(f'          read_policy         = "{v}"')
                                    elif k == 'size':
                                        print(f'          size                = "{v}"')
                                    elif k == 'strip_size':
                                        print(f'          strip_size          = "{v}"')
                                    elif k == 'write_policy':
                                        print(f'          write_policy        = "{v}"')
                                        print(f'        ''}')
                            print(f'      ''}')
                            print(f'    ''}')
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            valid_confirm = False
                            while valid_confirm == False:
                                confirm_v = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
                                if confirm_v == 'Y' or confirm_v == '':
                                    templateVars["drive_groups"].append(drive_group)
                                    valid_exit = False
                                    while valid_exit == False:
                                        loop_exit = input(f'Would You like to Configure another Drive Group?  Enter "Y" or "N" [N]: ')
                                        if loop_exit == 'Y':
                                            inner_loop_count += 1
                                            valid_confirm = True
                                            valid_exit = True
                                        elif loop_exit == 'N' or loop_exit == '':
                                            drive_group_loop = True
                                            valid_confirm = True
                                            valid_exit = True
                                        else:
                                            print(f'\n------------------------------------------------------\n')
                                            print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                                            print(f'\n------------------------------------------------------\n')

                                elif confirm_v == 'N':
                                    print(f'\n-------------------------------------------------------------------------------------------\n')
                                    print(f'  Starting Remote Host Configuration Over.')
                                    print(f'\n-------------------------------------------------------------------------------------------\n')
                                    valid_confirm = True
                                else:
                                    print(f'\n------------------------------------------------------\n')
                                    print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                                    print(f'\n------------------------------------------------------\n')
                    else:
                        templateVars["drive_group"] = {}




                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'    description                 = {templateVars["descr"]}')
                    print(f'    enable_azure_stack_host_qos = "{templateVars["enable_azure_stack_host_qos"]}"')
                    print(f'    iqn_allocation_type         = "{templateVars["iqn_allocation_type"]}"')
                    print(f'    iqn_pool                    = "{templateVars["iqn_pool"]}"')
                    print(f'    iqn_static_identifier       = "{templateVars["iqn_static_identifier"]}"')
                    print(f'    name                        = "{templateVars["name"]}"')
                    print(f'    target_platform             = "{templateVars["target_platform"]}"')
                    print(f'    vnic_placement_mode         = "{templateVars["vnic_placement_mode"]}"')
                    if len(templateVars["vnics"]) > 0:
                        print(f'    vnics = ''{')
                        for item in templateVars["vnics"]:
                            for k, v in item.items():
                                if k == 'name':
                                    print(f'      "{v}" = ''{')
                            for k, v in item.items():
                                if k == 'cdn_source':
                                    print(f'        cdn_source                      = "{v}"')
                                elif k == 'cdn_value':
                                    print(f'        cdn_value                       = "{v}"')
                                elif k == 'enable_failover':
                                    print(f'        enable_failover                 = "{v}"')
                                elif k == 'ethernet_adapter_policy':
                                    print(f'        ethernet_adapter_policy         = "{v}"')
                                elif k == 'ethernet_network_control_policy':
                                    print(f'        ethernet_network_control_policy = "{v}"')
                                elif k == 'ethernet_network_group_policy':
                                    print(f'        ethernet_network_group_policy   = "{v}"')
                                elif k == 'ethernet_network_policy':
                                    print(f'        ethernet_network_policy         = "{v}"')
                                elif k == 'iscsi_boot_policy':
                                    print(f'        iscsi_boot_policy               = "{v}"')
                                elif k == 'mac_address_allocation_type':
                                    print(f'        mac_address_allocation_type     = "{v}"')
                                elif k == 'mac_address_pool':
                                    print(f'        mac_address_pool                = "{v}"')
                                elif k == 'mac_address_static':
                                    print(f'        mac_address_static              = "{v}"')
                                elif k == 'name':
                                    print(f'        name                            = "{v}"')
                                elif k == 'pci_link':
                                    print(f'        placement_pci_link              = {v}')
                                elif k == 'pci_order':
                                    print(f'        placement_pci_order             = {v}')
                                elif k == 'slot_id':
                                    print(f'        placement_slot_id               = "{v}"')
                                elif k == 'switch_id':
                                    print(f'        placement_switch_id             = "{v}"')
                                elif k == 'uplink_port':
                                    print(f'        placement_uplink_port           = {v}')
                            print(f'      ''}')
                        print(f'    ''}')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
                        if confirm_policy == 'Y' or confirm_policy == '':
                            confirm_policy = 'Y'

                            # Write Policies to Template File
                            templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
                            write_to_template(self, **templateVars)

                            # Add Template Name to Policies Output
                            policy_names.append(templateVars["name"])

                            configure_loop, policy_loop = exit_default_no(templateVars["policy_type"])
                            valid_confirm = True

                        elif confirm_policy == 'N':
                            print(f'\n------------------------------------------------------\n')
                            print(f'  Starting {templateVars["policy_type"]} Section over.')
                            print(f'\n------------------------------------------------------\n')
                            valid_confirm = True

                        else:
                            print(f'\n------------------------------------------------------\n')
                            print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                            print(f'\n------------------------------------------------------\n')

            elif configure == 'N':
                configure_loop = True
            else:
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                print(f'\n-------------------------------------------------------------------------------------------\n')

        # Close the Template file
        templateVars["template_file"] = 'template_close.jinja2'
        write_to_template(self, **templateVars)


def validate_vlan_in_policy(vlan_policy_list, vlan_id):
    valid = False
    vlan_count = 0
    for vlan in vlan_policy_list:
        if int(vlan) == int(vlan_id):
            vlan_count = 1
            continue
    if vlan_count == 1:
        valid = True
    else:
        print(f'\n-------------------------------------------------------------------------------------------\n')
        print(f'  VLAN {vlan_id} not found in the VLAN Policy List.  Please us a VLAN from the list below:')
        print(f'  {vlan_policy_list}')
        print(f'\n-------------------------------------------------------------------------------------------\n')
    return valid

def choose_policy(policy, **templateVars):

    if 'policies' in policy:
        policy_short = policy.replace('policies', 'policy')
    elif 'pools' in policy:
        policy_short = policy.replace('pools', 'pool')
    x = policy_short.split('_')
    policy_description = []
    for y in x:
        y = y.capitalize()
        policy_description.append(y)
    policy_description = " ".join(policy_description)
    policy_description = policy_description.replace('Ip', 'IP')
    policy_description = policy_description.replace('Ntp', 'NTP')
    policy_description = policy_description.replace('Snmp', 'SNMP')
    policy_description = policy_description.replace('Wwnn', 'WWNN')
    policy_description = policy_description.replace('Wwpn', 'WWPN')

    if len(policy) > 0:
        templateVars["policy"] = policy_description
        policy_short = policies_list(templateVars["policies"], **templateVars)
    else:
        policy_short = ""
    return policy_short

def exit_default_no(policy_type):
    valid_exit = False
    while valid_exit == False:
        exit_answer = input(f'Would You like to Configure another {policy_type}?  Enter "Y" or "N" [N]: ')
        if exit_answer == '' or exit_answer == 'N':
            policy_loop = True
            configure_loop = True
            valid_exit = True
        elif exit_answer == 'Y':
            policy_loop = False
            configure_loop = False
            valid_exit = True
        else:
            print(f'\n------------------------------------------------------\n')
            print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
            print(f'\n------------------------------------------------------\n')
    return configure_loop, policy_loop

def exit_default_yes(policy_type):
    valid_exit = False
    while valid_exit == False:
        exit_answer = input(f'Would You like to Configure another {policy_type}?  Enter "Y" or "N" [Y]: ')
        if exit_answer == '' or exit_answer == 'Y':
            policy_loop = False
            configure_loop = False
            valid_exit = True
        elif exit_answer == 'N':
            policy_loop = True
            configure_loop = True
            valid_exit = True
        else:
            print(f'\n------------------------------------------------------\n')
            print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
            print(f'\n------------------------------------------------------\n')
    return configure_loop, policy_loop

def exit_loop_default_yes(loop_count, policy_type):
    valid_exit = False
    while valid_exit == False:
        if loop_count % 2 == 0:
            exit_answer = input(f'Would You like to Configure another {policy_type}?  Enter "Y" or "N" [Y]: ')
        else:
            exit_answer = input(f'Would You like to Configure another {policy_type}?  Enter "Y" or "N" [N]: ')
        if (loop_count % 2 == 0 and exit_answer == '') or exit_answer == 'Y':
            policy_loop = False
            configure_loop = False
            loop_count += 1
            valid_exit = True
        elif not loop_count % 2 == 0 and exit_answer == '':
            policy_loop = True
            configure_loop = True
            valid_exit = True
        elif exit_answer == 'N':
            policy_loop = True
            configure_loop = True
            valid_exit = True
        else:
            print(f'\n------------------------------------------------------\n')
            print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
            print(f'\n------------------------------------------------------\n')
    return configure_loop, loop_count, policy_loop

def naming_rule(name_prefix, name_suffix, org):
    if not name_prefix == '':
        name = '%s_%s' % (name_prefix, name_suffix)
    else:
        name = '%s_%s' % (org, name_suffix)
    return name

def naming_rule_fabric(loop_count, name_prefix, org):
    if loop_count % 2 == 0:
        if not name_prefix == '':
            name = '%s_A' % (name_prefix)
        elif not org == 'default':
            name = '%s_A' % (org)
        else:
            name = 'Fabric_A'
    else:
        if not name_prefix == '':
            name = '%s_B' % (name_prefix)
        elif not org == 'default':
            name = '%s_B' % (org)
        else:
            name = 'Fabric_B'
    return name

def policies_list(policies_list, **templateVars):
    valid = False
    while valid == False:
        print(f'\n-------------------------------------------------------------------------------------------\n')
        print(f'  {templateVars["policy"]} Options:')
        for i, v in enumerate(policies_list):
            i += 1
            if i < 10:
                print(f'     {i}. {v}')
            else:
                print(f'    {i}. {v}')
        if templateVars["allow_opt_out"] == True:
            print(f'     99. Do not assign a(n) {templateVars["policy"]}.')
        print(f'     100. Create a New {templateVars["policy"]}.')
        print(f'\n-------------------------------------------------------------------------------------------\n')
        policy_temp = input(f'Select the Option Number for the {templateVars["policy"]} to Assign to {templateVars["name"]}: ')
        for i, v in enumerate(policies_list):
            i += 1
            if int(policy_temp) == i:
                policy = v
                valid = True
                return policy
            elif int(policy_temp) == 99:
                policy = ''
                valid = True
                return policy
            elif int(policy_temp) == 100:
                policy = 'create_policy'
                valid = True
                return policy

        if policy_temp == '':
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  Error!! Invalid Selection.  Please Select a valid Index from the List.')
            print(f'\n-------------------------------------------------------------------------------------------\n')
        elif int(policy_temp) == 99:
            policy = ''
            valid = True
            return policy
        elif int(policy_temp) == 100:
            policy = 'create_policy'
            valid = True
            return policy

def policies_parse(org, policy_type, policy):
    policies = []
    policy_file = './Intersight/%s/%s/%s.auto.tfvars' % (org, policy_type, policy)
    if os.path.isfile(policy_file):
        if len(policy_file) > 0:
            cmd = 'json2hcl -reverse < %s' % (policy_file)
            p = subprocess.run(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            )
            if 'unable to parse' in p.stdout.decode('utf-8'):
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'  !!!! Encountered Error in Attempting to read file !!!!')
                print(f'  - {policy_file}')
                print(f'  Error was:')
                print(f'  - {p.stdout.decode("utf-8")}')
                print(f'\n-------------------------------------------------------------------------------------------\n')
                jsonData = {}
                return policies,jsonData
            else:
                jsonData = json.loads(p.stdout.decode('utf-8'))
                for i in jsonData[policy]:
                    for k, v in i.items():
                        policies.append(k)
                return policies,jsonData
    else:
        jsonData = {}
        return policies,jsonData

def policy_loop_standard(self, header, initial_policy, template_type):
    # Set the org_count to 0 for the First Organization
    org_count = 0

    # Loop through the orgs discovered by the Class
    for org in self.orgs:

        # Pull in Variables from Class
        templateVars = self.templateVars
        templateVars["org"] = org

        # Define the Template Source
        templateVars["header"] = header
        templateVars["template_type"] = template_type
        template_file = "template_open.jinja2"
        template = self.templateEnv.get_template(template_file)


        # Process the template
        dest_dir = '%s' % (self.type)
        dest_file = '%s.auto.tfvars' % (template_type)
        if initial_policy == True:
            write_method = 'w'
        else:
            write_method = 'a'
        process_method(write_method, dest_dir, dest_file, template, **templateVars)

        # Define the Template Source
        template_file = '%s.jinja2' % (template_type)
        template = self.templateEnv.get_template(template_file)

        if template_type in self.json_data["config"]["orgs"][org_count]:
            for item in self.json_data["config"]["orgs"][org_count][template_type]:
                # Reset TemplateVars to Default for each Loop
                templateVars = {}
                templateVars["org"] = org

                # Define the Template Source
                templateVars["header"] = header

                # Loop Through Json Items to Create templateVars Blocks
                for k, v in item.items():
                    templateVars[k] = v

                # if template_type == 'iscsi_boot_policies':
                #     print(templateVars)
                # Process the template
                dest_dir = '%s' % (self.type)
                dest_file = '%s.auto.tfvars' % (template_type)
                process_method('a', dest_dir, dest_file, template, **templateVars)

        # Define the Template Source
        template_file = "template_close.jinja2"
        template = self.templateEnv.get_template(template_file)

        # Process the template
        dest_dir = '%s' % (self.type)
        dest_file = '%s.auto.tfvars' % (template_type)
        process_method('a', dest_dir, dest_file, template, **templateVars)

        # Increment the org_count for the next Organization Loop
        org_count += 1

def policy_select_loop(name_prefix, policy, **templateVars):
    valid = False
    while valid == False:
        create_policy = True
        inner_policy = policy.split('.')[1]
        inner_type = policy.split('.')[0]
        inner_var = policy.split('.')[2]
        templateVars[inner_var] = ''
        templateVars["policies"],policyData = policies_parse(templateVars["org"], inner_type, inner_policy)
        if not len(templateVars['policies']) > 0:
            create_policy = True
        else:
            templateVars[inner_var] = choose_policy(inner_policy, **templateVars)
        if templateVars[inner_var] == 'create_policy':
            create_policy = True
        elif templateVars[inner_var] == '' and templateVars["allow_opt_out"] == True:
            valid = True
            create_policy = False
            return templateVars[inner_var],policyData
        elif not templateVars[inner_var] == '':
            valid = True
            create_policy = False
            return templateVars[inner_var],policyData
        if create_policy == True:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  Starting module to create {inner_policy}')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            if inner_policy == 'ip_pools':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).ip_pools()
            elif inner_policy == 'iqn_pools':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).iqn_pools()
            elif inner_policy == 'mac_pools':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).mac_pools()
            elif inner_policy == 'uuid_pools':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).uuid_pools()
            elif inner_policy == 'wwnn_pools':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).wwnn_pools()
            elif inner_policy == 'wwpn_pools':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).wwpn_pools()
            elif inner_policy == 'adapter_configuration_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).adapter_configuration_policies()
            elif inner_policy == 'bios_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).bios_policies()
            elif inner_policy == 'boot_order_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).boot_order_policies()
            elif inner_policy == 'certificate_management_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).certificate_management_policies()
            elif inner_policy == 'device_connector_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).device_connector_policies()
            elif inner_policy == 'ethernet_adapter_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).ethernet_adapter_policies()
            elif inner_policy == 'ethernet_network_control_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).ethernet_network_control_policies()
            elif inner_policy == 'ethernet_network_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).ethernet_network_policies()
            elif inner_policy == 'ethernet_qos_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).ethernet_qos_policies()
            elif inner_policy == 'fibre_channel_adapter_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).fibre_channel_adapter_policies()
            elif inner_policy == 'fibre_channel_network_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).fibre_channel_network_policies()
            elif inner_policy == 'fibre_channel_qos_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).fibre_channel_qos_policies()
            elif inner_policy == 'flow_control_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).flow_control_policies()
            elif inner_policy == 'imc_access_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).imc_access_policies()
            elif inner_policy == 'ipmi_over_lan_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).ipmi_over_lan_policies()
            elif inner_policy == 'iscsi_adapter_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).iscsi_adapter_policies()
            elif inner_policy == 'iscsi_boot_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).iscsi_boot_policies()
            elif inner_policy == 'iscsi_static_target_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).iscsi_static_target_policies()
            elif inner_policy == 'lan_connectivity_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).lan_connectivity_policies()
            elif inner_policy == 'ldap_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).ldap_policies()
            elif inner_policy == 'link_aggregation_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).link_aggregation_policies()
            elif inner_policy == 'link_control_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).link_control_policies()
            elif inner_policy == 'local_user_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).local_user_policies()
            elif inner_policy == 'multicast_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).multicast_policies()
            elif inner_policy == 'network_connectivity_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).network_connectivity_policies()
            elif inner_policy == 'ntp_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).ntp_policies()
            elif inner_policy == 'persistent_memory_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).persistent_memory_policies()
            elif inner_policy == 'port_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).port_policies()
            elif inner_policy == 'san_connectivity_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).san_connectivity_policies()
            elif inner_policy == 'sd_card_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).sd_card_policies()
            elif inner_policy == 'serial_over_lan_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).serial_over_lan_policies()
            elif inner_policy == 'smtp_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).smtp_policies()
            elif inner_policy == 'snmp_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).snmp_policies()
            elif inner_policy == 'ssh_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).ssh_policies()
            elif inner_policy == 'storage_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).storage_policies()
            elif inner_policy == 'switch_control_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).switch_control_policies()
            elif inner_policy == 'syslog_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).syslog_policies()
            elif inner_policy == 'system_qos_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).system_qos_policies()
            elif inner_policy == 'thermal_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).thermal_policies()
            elif inner_policy == 'virtual_kvm_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).virtual_kvm_policies()
            elif inner_policy == 'virtual_media_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).virtual_media_policies()
            elif inner_policy == 'vlan_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).vlan_policies()
            elif inner_policy == 'vsan_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).vsan_policies()

def policy_descr(name, policy_type):
    valid = False
    while valid == False:
        descr = input(f'What is the Description for the {policy_type}?  [{name} {policy_type}]: ')
        if descr == '':
            descr = '%s %s' % (name, policy_type)
        valid = validating.description(f'{policy_type} Description', descr, 1, 62)
        if valid == True:
            return descr

def policy_name(namex, policy_type):
    valid = False
    while valid == False:
        name = input(f'What is the Name for the {policy_type}?  [{namex}]: ')
        if name == '':
            name = '%s' % (namex)
        valid = validating.name_rule(f'{policy_type} Name', name, 1, 62)
        if valid == True:
            return name

def policy_template(self, **templateVars):
    configure_loop = False
    while configure_loop == False:
        policy_loop = False
        while policy_loop == False:

            valid = False
            while valid == False:
                policy_file = 'ucs_templates/variables/%s' % (templateVars["policy_file"])
                if os.path.isfile(policy_file):
                    template_file = open(policy_file, 'r')
                    template_file.seek(0)
                    policy_templates = []
                    for line in template_file:
                        line = line.strip()
                        policy_templates.append(line)
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  {templateVars["policy_type"]} Templates:')
                    for i, v in enumerate(policy_templates):
                        i += 1
                        if i < 10:
                            print(f'     {i}. {v}')
                        else:
                            print(f'    {i}. {v}')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                policy_temp = input(f'Enter the Index Number for the {templateVars["policy_type"]} Template to Create: ')
                for i, v in enumerate(policy_templates):
                    i += 1
                    if int(policy_temp) == i:
                        templateVars["policy_template"] = v
                        valid = True
                if valid == False:
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  Error!! Invalid Selection.  Please Select a valid Index from the List.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                template_file.close()

            if not templateVars["name_prefix"] == '':
                name = '%s_%s' % (templateVars["name_prefix"], templateVars["policy_template"])
            else:
                name = '%s_%s' % (templateVars["org"], templateVars["policy_template"])

            templateVars["name"] = policy_name(name, templateVars["policy_type"])
            templateVars["descr"] = policy_descr(templateVars["name"], templateVars["policy_type"])

            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  Do you want to accept the following configuration?')
            if templateVars["template_type"] == 'bios_policies':
                print(f'   bios_template = "{templateVars["policy_template"]}"')
                print(f'   description   = "{templateVars["descr"]}"')
                print(f'   name          = "{templateVars["name"]}"')
            else:
                print(f'   adapter_template = "{templateVars["policy_template"]}"')
                print(f'   description      = "{templateVars["descr"]}"')
                print(f'   name             = "{templateVars["name"]}"')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            valid_confirm = False
            while valid_confirm == False:
                confirm_policy = input('Enter "Y" or "N" [Y]: ')
                if confirm_policy == 'Y' or confirm_policy == '':
                    confirm_policy = 'Y'

                    # Write Policies to Template File
                    write_to_template(self, **templateVars)

                    configure_loop, policy_loop = exit_default_yes(templateVars["policy_type"])
                    valid_confirm = True

                elif confirm_policy == 'N':
                    print(f'\n------------------------------------------------------\n')
                    print(f'  Starting {templateVars["policy_type"]} Section over.')
                    print(f'\n------------------------------------------------------\n')
                    valid_confirm = True

                else:
                    print(f'\n------------------------------------------------------\n')
                    print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                    print(f'\n------------------------------------------------------\n')

def vars_from_list(var_options, **templateVars):
    selection = []
    selection_count = 0
    valid = False
    while valid == False:
        print(f'\n-------------------------------------------------------------------------------------------\n')
        print(f'{templateVars["var_description"]}')
        for index, value in enumerate(var_options):
            index += 1
            if index < 10:
                print(f'     {index}. {value}')
            else:
                print(f'    {index}. {value}')
        print(f'\n-------------------------------------------------------------------------------------------\n')
        exit_answer = False
        while exit_answer == False:
            var_selection = input(f'Please Enter the Option Number to Select for {templateVars["var_type"]}: ')
            if not var_selection == '':
                if re.search(r'[0-9]+', str(var_selection)):
                    xcount = 1
                    for index, value in enumerate(var_options):
                        index += 1
                        if int(var_selection) == index:
                            selection.append(value)
                            xcount = 0
                    if xcount == 0:
                        if selection_count % 2 == 0 and templateVars["multi_select"] == True:
                            answer_finished = input(f'Would you like to add another port to the {templateVars["port_type"]}?  Enter "Y" or "N" [Y]: ')
                        elif templateVars["multi_select"] == True:
                            answer_finished = input(f'Would you like to add another port to the {templateVars["port_type"]}?  Enter "Y" or "N" [N]: ')
                        elif templateVars["multi_select"] == False:
                            answer_finished = 'N'
                        if (selection_count % 2 == 0 and answer_finished == '') or answer_finished == 'Y':
                            exit_answer = True
                            selection_count += 1
                        elif answer_finished == '' or answer_finished == 'N':
                            exit_answer = True
                            valid = True
                        elif templateVars["multi_select"] == False:
                            exit_answer = True
                            valid = True
                        else:
                            print(f'\n------------------------------------------------------\n')
                            print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                            print(f'\n------------------------------------------------------\n')
                    else:
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        print(f'  Error!! Invalid Selection.  Please select a valid option from the List.')
                        print(f'\n-------------------------------------------------------------------------------------------\n')

                else:
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  Error!! Invalid Selection.  Please Select a valid Option from the List.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
            else:
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'  Error!! Invalid Selection.  Please Select a valid Option from the List.')
                print(f'\n-------------------------------------------------------------------------------------------\n')
    return selection

def process_method(wr_method, dest_dir, dest_file, template, **templateVars):
    dest_dir = './Intersight/%s/%s' % (templateVars["org"], dest_dir)
    if not os.path.isdir(dest_dir):
        mk_dir = 'mkdir -p %s' % (dest_dir)
        os.system(mk_dir)
    dest_file_path = '%s/%s' % (dest_dir, dest_file)
    if not os.path.isfile(dest_file_path):
        create_file = 'touch %s' % (dest_file_path)
        os.system(create_file)
    tf_file = dest_file_path
    wr_file = open(tf_file, wr_method)

    # Render Payload and Write to File
    payload = template.render(templateVars)
    wr_file.write(payload)
    wr_file.close()

def variablesFromAPI(**templateVars):
    valid = False
    while valid == False:
        json_vars = templateVars["jsonVars"]
        if 'popList' in templateVars:
            if len(templateVars["popList"]) > 0:
                for x in templateVars["popList"]:
                    varsCount = len(json_vars)
                    for r in range(0, varsCount):
                        if json_vars[r] == x:
                            json_vars.pop(r)
                            break
        print(f'\n-------------------------------------------------------------------------------------------\n')
        print(f'{templateVars["var_description"]}')
        print(f'\n    Select an Option Below:')
        for index, value in enumerate(json_vars):
            index += 1
            if value == templateVars["defaultVar"]:
                defaultIndex = index
            if index < 10:
                print(f'     {index}. {value}')
            else:
                print(f'    {index}. {value}')
        print(f'\n-------------------------------------------------------------------------------------------\n')
        if templateVars["multi_select"] == True:
            if not templateVars["defaultVar"] == '':
                var_selection = input(f'Please Enter the Option Number(s) to Select for {templateVars["varType"]}.  [{defaultIndex}]: ')
            else:
                var_selection = input(f'Please Enter the Option Number(s) to Select for {templateVars["varType"]}: ')
        else:
            if not templateVars["defaultVar"] == '':
                var_selection = input(f'Please Enter the Option Number to Select for {templateVars["varType"]}.  [{defaultIndex}]: ')
            else:
                var_selection = input(f'Please Enter the Option Number to Select for {templateVars["varType"]}: ')
        if var_selection == '':
            var_selection = defaultIndex
        if templateVars["multi_select"] == False and re.search(r'^[0-9]+$', str(var_selection)):
            for index, value in enumerate(json_vars):
                index += 1
                if int(var_selection) == index:
                    selection = value
                    valid = True
        elif templateVars["multi_select"] == True and re.search(r'(^[0-9]+$|^[0-9\-,]+[0-9]$)', str(var_selection)):
            var_list = vlan_list_full(var_selection)
            var_length = int(len(var_list))
            var_count = 0
            selection = []
            for index, value in enumerate(json_vars):
                index += 1
                for vars in var_list:
                    if int(vars) == index:
                        var_count += 1
                        selection.append(value)
            if var_count == var_length:
                valid = True
            else:
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'  The list of Vars {var_list} did not match the available list.')
                print(f'\n-------------------------------------------------------------------------------------------\n')
        else:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  Error!! Invalid Selection.  Please Select a valid Option from the List.')
            print(f'\n-------------------------------------------------------------------------------------------\n')
    return selection

def varBoolLoop(**templateVars):
    print(f'\n-------------------------------------------------------------------------------------------\n')
    print(f'  {templateVars["Description"]}')
    print(f'\n-------------------------------------------------------------------------------------------\n')
    valid = False
    while valid == False:
        varValue = input(f'{templateVars["varInput"]} [{templateVars["varDefault"]}]: ')
        if varValue == '':
            if templateVars["varDefault"] == 'Y':
                varValue = True
            elif templateVars["varDefault"] == 'N':
                varValue = False
            valid = True
        elif varValue == 'N':
            varValue = False
            valid = True
        elif varValue == 'Y':
            varValue = True
            valid = True
        else:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'   {templateVars["varName"]} value of "{varValue}" is Invalid!!! Please enter "Y" or "N".')
            print(f'\n-------------------------------------------------------------------------------------------\n')
    return varValue

def varNumberLoop(**templateVars):
    maxNum = templateVars["maxNum"]
    minNum = templateVars["minNum"]
    varName = templateVars["varName"]

    print(f'\n-------------------------------------------------------------------------------------------\n')
    print(f'  {templateVars["Description"]}')
    print(f'\n-------------------------------------------------------------------------------------------\n')
    valid = False
    while valid == False:
        varValue = input(f'{templateVars["varInput"]}  [{templateVars["varDefault"]}]: ')
        if varValue == '':
            varValue = templateVars["varDefault"]
        if re.fullmatch(r'^[0-9]+$', str(varValue)):
            valid = validating.number_in_range(varName, varValue, minNum, maxNum)
        else:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'   {varName} value of "{varValue}" is Invalid!!! ')
            print(f'   Valid range is {minNum} to {maxNum}.')
            print(f'\n-------------------------------------------------------------------------------------------\n')
    return varValue

def varSensitiveStringLoop(**templateVars):
    maxLength = templateVars["maxLength"]
    minLength = templateVars["minLength"]
    varName = templateVars["varName"]
    varRegex = templateVars["varRegex"]

    print(f'\n-------------------------------------------------------------------------------------------\n')
    print(f'  {templateVars["Description"]}')
    print(f'\n-------------------------------------------------------------------------------------------\n')
    valid = False
    while valid == False:
        varValue = stdiomask.getpass(f'{templateVars["varInput"]} ')
        if not varValue == '':
            valid = validating.length_and_regex_sensitive(varRegex, varName, varValue, minLength, maxLength)
        else:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'   {varName} value is Invalid!!! ')
            print(f'\n-------------------------------------------------------------------------------------------\n')
    return varValue

def varStringLoop(**templateVars):
    maxLength = templateVars["maxLength"]
    minLength = templateVars["minLength"]
    varName = templateVars["varName"]
    varRegex = templateVars["varRegex"]

    print(f'\n-------------------------------------------------------------------------------------------\n')
    print(f'  {templateVars["Description"]}')
    print(f'\n-------------------------------------------------------------------------------------------\n')
    valid = False
    while valid == False:
        varValue = input(f'{templateVars["varInput"]} ')
        if 'press enter to skip' in templateVars["varInput"] and varValue == '':
            valid = True
        elif not templateVars["varDefault"] == '' and varValue == '':
            varValue = templateVars["varDefault"]
            valid = True
        elif not varValue == '':
            valid = validating.length_and_regex(varRegex, varName, varValue, minLength, maxLength)
        else:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'   {varName} value of "{varValue}" is Invalid!!! ')
            print(f'\n-------------------------------------------------------------------------------------------\n')
    return varValue

def variable_loop(**templateVars):
    valid = False
    while valid == False:
        print(f'\n-------------------------------------------------------------------------------------------\n')
        print(f'{templateVars["var_description"]}')
        policy_file = 'ucs_templates/variables/%s' % (templateVars["policy_file"])
        if os.path.isfile(policy_file):
            variable_file = open(policy_file, 'r')
            varsx = []
            for line in variable_file:
                varsx.append(line.strip())
            for index, value in enumerate(varsx):
                index += 1
                if index < 10:
                    print(f'     {index}. {value}')
                else:
                    print(f'    {index}. {value}')
        print(f'\n-------------------------------------------------------------------------------------------\n')
        var_selection = input(f'Please Enter the Option Number to Select for {templateVars["var_type"]}: ')
        if not var_selection == '':
            if templateVars["multi_select"] == False and re.search(r'^[0-9]+$', str(var_selection)):
                for index, value in enumerate(varsx):
                    index += 1
                    if int(var_selection) == index:
                        selection = value
                        valid = True
            elif templateVars["multi_select"] == True and re.search(r'(^[0-9]+$|^[0-9\-,]+[0-9]$)', str(var_selection)):
                var_list = vlan_list_full(var_selection)
                var_length = int(len(var_list))
                var_count = 0
                selection = []
                for index, value in enumerate(varsx):
                    index += 1
                    for vars in var_list:
                        if int(vars) == index:
                            var_count += 1
                            selection.append(value)
                if var_count == var_length:
                    valid = True
                else:
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  The list of Vars {var_list} did not match the available list.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
            else:
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'  Error!! Invalid Selection.  Please Select a valid Option from the List.')
                print(f'\n-------------------------------------------------------------------------------------------\n')
        else:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  Error!! Invalid Selection.  Please Select a valid Option from the List.')
            print(f'\n-------------------------------------------------------------------------------------------\n')
    return selection

def vlan_list_full(vlan_list):
    full_vlan_list = []
    if re.search(r',', str(vlan_list)):
        vlist = vlan_list.split(',')
        for v in vlist:
            if re.fullmatch('^\\d{1,4}\\-\\d{1,4}$', v):
                a,b = v.split('-')
                a = int(a)
                b = int(b)
                vrange = range(a,b+1)
                for vl in vrange:
                    full_vlan_list.append(vl)
            elif re.fullmatch('^\\d{1,4}$', v):
                full_vlan_list.append(v)
    elif re.search('\\-', str(vlan_list)):
        a,b = vlan_list.split('-')
        a = int(a)
        b = int(b)
        vrange = range(a,b+1)
        for v in vrange:
            full_vlan_list.append(v)
    else:
        full_vlan_list.append(vlan_list)
    return full_vlan_list

def write_to_template(self, **templateVars):
    # Define the Template Source
    template = self.templateEnv.get_template(templateVars["template_file"])

    # Process the template
    dest_dir = '%s' % (self.type)
    dest_file = '%s.auto.tfvars' % (templateVars["template_type"])
    if templateVars["initial_write"] == True:
        write_method = 'w'
    else:
        write_method = 'a'
    process_method(write_method, dest_dir, dest_file, template, **templateVars)
