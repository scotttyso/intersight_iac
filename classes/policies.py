from copy import deepcopy
from textwrap import fill
import base64
import lansan
import pools
import ezfunctions
import json
import os
import re
import stdiomask
import textwrap
import validating
import yaml

class MyDumper(yaml.Dumper):
    def increase_indent(self, flow=False, indentless=False):
        return super(MyDumper, self).increase_indent(flow, False)

class policies(object):
    def __init__(self, name_prefix, org, type):
        self.name_prefix = name_prefix
        self.org = org
        self.type = type

    #==============================================
    # Adapter Configuration Policy Module
    #==============================================
    def adapter_configuration_policies(self, **kwargs):
        baseRepo       = kwargs['args'].dir
        configure_loop = False
        ezData         = kwargs['ezData']
        jsonData       = kwargs['jsonData']
        name_prefix    = self.name_prefix
        name_suffix    = 'adapter'
        org            = self.org
        path_sep       = kwargs['path_sep']
        policy_type    = 'Adapter Configuration Policy'
        yaml_file      = 'ethernet'
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  An {policy_type} configures the Ethernet and Fibre-Channel settings for the ')
            print(f'  Virtual Interface Card (VIC) adapter.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - {baseRepo}{path_sep}{org}{path_sep}{self.type}{path_sep}{yaml_file}.yaml')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure an {policy_type}?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                policy_loop = False
                while policy_loop == False:
                    polVars = {}
                    if not name_prefix == '': name = f'{name_prefix}-{name_suffix}'
                    else: name = f'{org}-{name_suffix}'
                    polVars['name']        = ezfunctions.policy_name(name, policy_type)
                    polVars['description'] = ezfunctions.policy_descr(polVars['name'], policy_type)

                    # Get API Data
                    kwargs['multi_select'] = False
                    jsonVars = jsonData['adapter.FcSettings']['allOf'][1]['properties']
                    kwargs['jData'] = deepcopy(jsonVars['FipEnabled'])
                    kwargs['jData']['description'] = 'If Selected, then FCoE Initialization Protocol (FIP) mode is enabled.'\
                        ' FIP mode ensures that the adapter is compatible with current FCoE standards.'
                    kwargs['jData']['varInput'] = f'Do you want to Enable FIP on the VIC?'
                    kwargs['jData']['varName']  = 'FIP Enabled'
                    polVars["enable_fip"] = ezfunctions.varBoolLoop(**kwargs)

                    jsonVars = jsonData['adapter.EthSettings']['allOf'][1]['properties']
                    kwargs['jData'] = deepcopy(jsonVars['LldpEnabled'])
                    kwargs['jData']['description'] = 'If Selected, then Link Layer Discovery Protocol (LLDP) enables all'\
                        ' the Data Center Bridging Capability Exchange protocol (DCBX) functionality, which '\
                        'includes FCoE, priority based flow control.'
                    kwargs['jData']['varInput'] = f'Do you want to Enable LLDP on the VIC?'
                    kwargs['jData']['varName']  = 'LLDP Enabled'
                    polVars["enable_lldp"] = ezfunctions.varBoolLoop(**kwargs)

                    jsonVars = jsonData['adapter.PortChannelSettings']['allOf'][1]['properties']
                    kwargs['jData'] = deepcopy(jsonVars['Enabled'])
                    kwargs['jData']['varInput'] = f'Do you want to Enable Port-Channel on the VIC?'
                    kwargs['jData']['varName']  = 'Port-Channel Settings'
                    polVars["enable_port_channel"] = ezfunctions.varBoolLoop(**kwargs)

                    jsonVars = jsonData['adapter.DceInterfaceSettings']['allOf'][1]['properties']
                    intList = [1, 2, 3, 4]
                    for x in intList:
                        polVars["multi_select"] = False
                        polVars['description'] = jsonVars['FecMode']['description']
                        polVars["jsonVars"] = sorted(jsonVars['FecMode']['enum'])
                        polVars["defaultVar"] = jsonVars['FecMode']['default']
                        polVars["varType"] = f'DCE Interface {x} FEC Mode'
                        intFec = f'fec_mode_{x}'
                        polVars[intFec] = ezfunctions.variablesFromAPI(**kwargs)
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(textwrap.indent(yaml.dump(polVars, Dumper=MyDumper, default_flow_style=False), ' '*4, predicate=None))
                    print(f'-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
                        if confirm_policy == 'Y' or confirm_policy == '':
                            # Write Policies to Template File
                            polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                            ezfunctions.write_to_template(self, **kwargs)

                            configure_loop, policy_loop = ezfunctions.exit_default(policy_type, 'N')
                            valid_confirm = True
                        elif confirm_policy == 'N':
                            ezfunctions.message_starting_over(policy_type)
                            valid_confirm = True
                        else: ezfunctions.message_invalid_y_or_n('short')
            elif configure == 'N': configure_loop = True
            else: ezfunctions.message_invalid_y_or_n('long')
        # Return kwargs
        return kwargs

    #==============================================
    # BIOS Policy Module
    #==============================================
    def bios_policies(self, **kwargs):
        baseRepo       = kwargs['args'].dir
        configure_loop = False
        ezData         = kwargs['ezData']
        jsonData       = kwargs['jsonData']
        name_prefix    = self.name_prefix
        org            = self.org
        path_sep       = kwargs['path_sep']
        policy_type    = 'BIOS Policy'
        yaml_file      = 'compute'
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  {policy_type} Policies:  To simplify your work, this wizard will use {policy_type}')
            print(f'  Templates that are pre-configured.  You can add custom {policy_type} policy')
            print(f'  configuration to the {yaml_file}.yaml file at your descretion.')
            print(f'  That will not be covered by this wizard as the focus of the wizard is on simplicity.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - {baseRepo}{path_sep}{org}{path_sep}{self.type}{path_sep}{yaml_file}.yaml')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure a {policy_type}?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                policy_loop = False
                while policy_loop == False:
                    polVars = {}
                    polVars["multi_select"] = False
                    jsonVars = ezData['policies']['bios.Policy']
                    polVars['description'] = jsonVars['templates']['description']
                    polVars["jsonVars"] = sorted(jsonVars['templates']['enum'])
                    polVars["defaultVar"] = jsonVars['templates']['default']
                    polVars["varType"] = 'BIOS Template'
                    polVars["policy_template"] = ezfunctions.variablesFromAPI(**kwargs)

                    if not polVars["name_prefix"] == '':
                        name = '%s-%s' % (polVars["name_prefix"], polVars["policy_template"])
                    else: name = '%s-%s' % (polVars["org"], polVars["policy_template"])
                    polVars['name']        = ezfunctions.policy_name(name, polVars["policy_type"])
                    polVars['description'] = ezfunctions.policy_descr(polVars['name'], polVars["policy_type"])
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(textwrap.indent(yaml.dump(polVars, Dumper=MyDumper, default_flow_style=False), ' '*4, predicate=None))
                    print(f'-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
                        if confirm_policy == 'Y' or confirm_policy == '':
                            # Write Policies to Template File
                            polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                            ezfunctions.write_to_template(self, **kwargs)

                            configure_loop, policy_loop = ezfunctions.exit_default(policy_type, 'Y')
                            valid_confirm = True
                        elif confirm_policy == 'N':
                            ezfunctions.message_starting_over(policy_type)
                            valid_confirm = True
                        else: ezfunctions.message_invalid_y_or_n('short')
            elif configure == 'N': configure_loop = True
            else: ezfunctions.message_invalid_y_or_n('long')
        # Return kwargs
        return kwargs

    #==============================================
    # Boot Order Policy Module
    #==============================================
    def boot_order_policies(self, **kwargs):
        baseRepo       = kwargs['args'].dir
        configure_loop = False
        ezData         = kwargs['ezData']
        jsonData       = kwargs['jsonData']
        name_prefix    = self.name_prefix
        name_suffix    = 'boot'
        org            = self.org
        path_sep       = kwargs['path_sep']
        policy_type    = 'Boot Order Policy'
        yaml_file      = 'compute'
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  A {policy_type} configures the linear ordering of devices and enables you to change ')
            print(f'  the boot order and boot mode. You can also add multiple devices under various device types,')
            print(f'  rearrange the boot order, and set parameters for each boot device type.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - {baseRepo}{path_sep}{org}{path_sep}{self.type}{path_sep}{yaml_file}.yaml')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure a {policy_type}.  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                policy_loop = False
                while policy_loop == False:
                    polVars = {}
                    if not name_prefix == '': name = f'{name_prefix}-{name_suffix}'
                    else: name = f'{org}-{name_suffix}'
                    polVars['name']        = ezfunctions.policy_name(name, policy_type)
                    polVars['description'] = ezfunctions.policy_descr(polVars['name'], policy_type)

                    # Pull in the Policies for iSCSI Boot
                    jsonVars = jsonData['boot.PrecisionPolicy']['allOf'][1]['properties']
                    kwargs["multi_select"] = False
                    # Configured Boot Mode
                    kwargs['jData'] = deepcopy(jsonVars['ConfiguredBootMode'])
                    kwargs['jData'].update({'varType': 'Configured Boot Mode'})
                    polVars["boot_mode"] = ezfunctions.variablesFromAPI(**kwargs)
                    if polVars["boot_mode"] == 'Uefi':
                        # Enforce Uefi SecureBoot
                        kwargs['jData'] = deepcopy(jsonVars['EnforceUefiSecureBoot'])
                        kwargs['jData'].update({'default': False, 'varName': 'Uefi SecureBoot'})
                        kwargs['jData']["varInput"] = f'Do you want to Enforce Uefi Secure Boot?'
                        polVars["enable_secure_boot"] = ezfunctions.varBoolLoop(**kwargs)
                    else: polVars["enable_secure_boot"] = False
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  Add and configure a boot device. The configuration options vary with boot device types.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    polVars["boot_devices"] = []
                    inner_loop_count = 1
                    sub_loop = False
                    while sub_loop == False:
                        question = input(f'\nWould you like to configure a Boot Device?  Enter "Y" or "N" [Y]: ')
                        if question == '' or question == 'Y':
                            valid_sub = False
                            while valid_sub == False:
                                # Pull in the Policies for iSCSI Boot
                                jsonVars = jsonData['boot.DeviceBase']['allOf'][1]['properties']
                                # Configured Boot Mode
                                kwargs['jData'] = deepcopy(jsonVars['ClassId'])
                                kwargs['jData']["default"] = 'boot.LocalDisk'
                                kwargs['jData']['description'] = 'Select the Type of Boot Device to configure.'
                                kwargs['jData']["varType"] = 'Boot Device Class ID'
                                objectType = ezfunctions.variablesFromAPI(**kwargs)

                                polVars['description'] = jsonVars['Name']['description']
                                polVars["varDefault"] = ''
                                polVars["varInput"] = 'Boot Device Name:'
                                polVars["varName"] = 'Boot Device Name'
                                polVars["varRegex"] = jsonVars['Name']['pattern']
                                polVars["minLength"] = 1
                                polVars["maxLength"] = 30
                                device_name = ezfunctions.varStringLoop(**kwargs)
                                boot_device = {"enabled":True, "device_name":device_name, "object_type":objectType}
                                if objectType == 'boot.Iscsi':
                                    device_type = 'iscsi_boot'
                                    jsonVars = jsonData['boot.Iscsi']['allOf'][1]['properties']
                                elif objectType == 'boot.LocalCdd':
                                    device_type = 'local_cdd'
                                elif objectType == 'boot.LocalDisk':
                                    device_type = 'local_disk'
                                    jsonVars = jsonData['boot.LocalDisk']['allOf'][1]['properties']
                                elif objectType == 'boot.Nvme':
                                    device_type = 'nvme'
                                    jsonVars = jsonData['boot.Nvme']['allOf'][1]['properties']
                                elif objectType == 'boot.PchStorage':
                                    device_type = 'pch_storage'
                                    jsonVars = jsonData['boot.PchStorage']['allOf'][1]['properties']
                                elif objectType == 'boot.Pxe':
                                    device_type = 'pxe_boot'
                                    jsonVars = jsonData['boot.Pxe']['allOf'][1]['properties']
                                elif objectType == 'boot.San':
                                    device_type = 'san_boot'
                                    jsonVars = jsonData['boot.San']['allOf'][1]['properties']
                                elif objectType == 'boot.SdCard':
                                    device_type = 'sd_card'
                                    jsonVars = jsonData['boot.SdCard']['allOf'][1]['properties']
                                elif objectType == 'boot.UefiShell':
                                    device_type = 'uefi_shell'
                                    jsonVars = jsonData['boot.UefiShell']['allOf'][1]['properties']
                                elif objectType == 'boot.Usb':
                                    device_type = 'usb'
                                    jsonVars = jsonData['boot.Usb']['allOf'][1]['properties']
                                elif objectType == 'boot.VirtualMedia':
                                    device_type = 'virtual_media'
                                    jsonVars = jsonData['boot.VirtualMedia']['allOf'][1]['properties']

                                boot_device.update({'device_type':device_type})

                                if objectType == 'boot.LocalDisk':
                                    polVars["multi_select"] = False
                                    jsonVars = jsonData['vnic.EthNetworkPolicy']['allOf'][1]['properties']
                                    polVars['description'] = jsonVars['TargetPlatform']['description']
                                    polVars["jsonVars"] = sorted(jsonVars['TargetPlatform']['enum'])
                                    polVars["defaultVar"] = jsonVars['TargetPlatform']['default']
                                    polVars["varType"] = 'Target Platform'
                                    target_platform = ezfunctions.variablesFromAPI(**kwargs)

                                    # Slot
                                    jsonVars = jsonData['boot.LocalDisk']['allOf'][1]['properties']
                                    polVars['description'] = jsonVars['Slot']['description']
                                    polVars["jsonVars"] = ezData['policies']['boot.PrecisionPolicy']['boot.Localdisk'][target_platform]
                                    polVars["defaultVar"] = ezData['policies']['boot.PrecisionPolicy']['boot.Localdisk']['default']
                                    polVars["varType"] = 'Slot'
                                    Slot = ezfunctions.variablesFromAPI(**kwargs)

                                    if re.search('[0-9]+', Slot):
                                        polVars['description'] = 'Slot Number between 1 and 205.'
                                        polVars["varDefault"] =  1
                                        polVars["varInput"] = 'Slot ID of the Localdisk:'
                                        polVars["varName"] = 'Slot'
                                        polVars["varRegex"] = '[0-9]+'
                                        polVars["minNum"] = 1
                                        polVars["maxNum"] = 205
                                        Slot = ezfunctions.varNumberLoop(**kwargs)
                                    localDisk = {'slot':Slot}
                                    boot_device.update(localDisk)
                                if objectType == 'boot.Pxe':
                                    # IPv4 or IPv6
                                    polVars['description'] = jsonVars['IpType']['description']
                                    polVars["jsonVars"] = sorted(jsonVars['IpType']['enum'])
                                    polVars["defaultVar"] = jsonVars['IpType']['default']
                                    polVars["varType"] = 'IP Type'
                                    IpType = ezfunctions.variablesFromAPI(**kwargs)

                                    # Interface Source
                                    polVars['description'] = jsonVars['InterfaceSource']['description']
                                    polVars["jsonVars"] = sorted(jsonVars['InterfaceSource']['enum'])
                                    polVars["defaultVar"] = jsonVars['InterfaceSource']['default']
                                    polVars["varType"] = 'Interface Source'
                                    InterfaceSource = ezfunctions.variablesFromAPI(**kwargs)

                                if objectType == 'boot.Iscsi' or (objectType == 'boot.Pxe' and InterfaceSource == 'name'):
                                    polVars["allow_opt_out"] = False
                                    kwargs['policy'] = 'policies.lan_connectivity_policies.lan_connectivity_policy'
                                    lan_connectivity_policy = kwargs['lan_connectivity_policy']
                                    kwargs = policy_select_loop(**kwargs)
                                    vnicNames = []
                                    for item in kwargs['immDict']['orgs'][org]['intersight']['policies']['lan_connectivity_policies']:
                                        if item['name'] == lan_connectivity_policy:
                                            for i in item['vnics']:
                                                vnicNames.append(i['names'])

                                    vnicNames = [i for s in vnicNames for i in s]
                                    polVars['description'] = 'LAN Connectivity vNIC Names.'
                                    polVars["jsonVars"] = sorted(vnicNames)
                                    polVars["defaultVar"] = ''
                                    polVars["varType"] = 'vNIC Names'
                                    vnicTemplate = ezfunctions.variablesFromAPI(**kwargs)
                                    InterfaceName = values[0]['vnics'][0][vnicTemplate][0]['name']
                                    Slot = values[0]['vnics'][0][vnicTemplate][0]['placement_slot_id']

                                    if objectType == 'boot.Iscsi':
                                        Port = 0
                                    else:
                                        Port = -1
                                        MacAddress = ''

                                if objectType == 'boot.Pxe':
                                    if InterfaceSource == 'mac':
                                        polVars['description'] = jsonVars['MacAddress']['description']
                                        polVars["varDefault"] = ''
                                        polVars["varInput"] = 'The MAC Address of the adapter on the underlying Virtual NIC:'
                                        polVars["varName"] = 'Mac Address'
                                        polVars["varRegex"] = jsonVars['MacAddress']['pattern']
                                        polVars["minLength"] = 17
                                        polVars["maxLength"] = 17
                                        MacAddress = ezfunctions.varStringLoop(**kwargs)
                                        InterfaceName = ''
                                        Port = -1
                                    elif InterfaceSource == 'port':
                                        polVars['description'] = jsonVars['Port']['description']
                                        polVars["varDefault"] =  jsonVars['Port']['default']
                                        polVars["varInput"] = 'The Port ID of the adapter on the underlying Virtual NIC:'
                                        polVars["varName"] = 'Port'
                                        polVars["varRegex"] = jsonVars['Port']['pattern']
                                        polVars["minNum"] = 1
                                        polVars["maxNum"] = 3
                                        Port = ezfunctions.varNumberLoop(**kwargs)
                                        InterfaceName = ''
                                        MacAddress = ''

                                    if not InterfaceSource == 'name':
                                        polVars['description'] = jsonVars['Slot']['description']
                                        polVars["varDefault"] = 'MLOM'
                                        polVars["varInput"] = 'The Slot ID of the adapter on the underlying Virtual NIC:'
                                        polVars["varName"] = 'Slot'
                                        polVars["varRegex"] = jsonVars['Slot']['pattern']
                                        polVars["minLength"] = 1
                                        polVars["maxLength"] = 4
                                        Slot = ezfunctions.varStringLoop(**kwargs)

                                    pxeBoot = {
                                        'interface_name':InterfaceName,
                                        'interface_source':InterfaceSource,
                                        'ip_type':IpType,
                                        'mac_address':MacAddress,
                                        'port':Port,
                                        'slot':Slot
                                    }
                                    boot_device.update(pxeBoot)

                                if re.fullmatch('boot\.Iscsi', objectType):
                                    jsonVars = jsonData['boot.Iscsi']['allOf'][1]['properties']

                                    # Port
                                    polVars['description'] = jsonVars['Port']['description']
                                    polVars["varInput"] = 'Enter the Port ID of the Adapter:'
                                    polVars["varDefault"] = jsonVars['Port']['description']
                                    polVars["varName"] = 'Port'
                                    polVars["minNum"] = jsonVars['Port']['minimum']
                                    polVars["maxNum"] = jsonVars['Port']['maximum']
                                    polVars["port"] = ezfunctions.varNumberLoop(**kwargs)

                                if re.fullmatch('boot\.(PchStorage|San|SdCard)', objectType):
                                    polVars['description'] = jsonVars['Lun']['description']
                                    polVars["varDefault"] =  jsonVars['Lun']['default']
                                    polVars["varInput"] = 'LUN Identifier:'
                                    polVars["varName"] = 'LUN ID'
                                    polVars["varRegex"] = '[\\d]+'
                                    polVars["minNum"] = jsonVars['Lun']['minimum']
                                    polVars["maxNum"] = jsonVars['Lun']['maximum']
                                    Lun = ezfunctions.varNumberLoop(**kwargs)
                                    boot_device.update({'lun':Lun})

                                if objectType == 'boot.San':
                                    policy_list = [
                                        'policies.san_connectivity_policies.san_connectivity_policy',
                                    ]
                                    polVars["allow_opt_out"] = False
                                    for policy in policy_list:
                                        san_connectivity_policy,policyData = policy_select_loop(jsonData, ezData, name_prefix, policy, **kwargs)
                                    vnicNames = []
                                    for x in policyData['san_connectivity_policies']:
                                        for keys, values in x.items():
                                            if keys == san_connectivity_policy:
                                                for i in values[0]['vhbas']:
                                                    for k, v in i.items():
                                                        vnicNames.append(k)

                                                polVars['description'] = 'SAN Connectivity vNIC Names.'
                                                polVars["jsonVars"] = sorted(vnicNames)
                                                polVars["defaultVar"] = ''
                                                polVars["varType"] = 'vHBA Names'
                                                vnicTemplate = ezfunctions.variablesFromAPI(**kwargs)
                                                InterfaceName = values[0]['vhbas'][0][vnicTemplate][0]['name']
                                                Slot = values[0]['vhbas'][0][vnicTemplate][0]['placement_slot_id']

                                    polVars['description'] = jsonVars['Wwpn']['description']
                                    polVars["varDefault"] = ''
                                    polVars["varInput"] = 'WWPN of the Target Appliance:'
                                    polVars["varName"] = 'WWPN'
                                    polVars["varRegex"] = jsonVars['Wwpn']['pattern']
                                    polVars["minLength"] = 23
                                    polVars["maxLength"] = 23
                                    Wwpn = ezfunctions.varStringLoop(**kwargs)

                                    targetWwpn = {'target_wwpn':Wwpn}
                                    boot_device.update(targetWwpn)

                                if re.fullmatch('boot\.(SdCard|Usb|VirtualMedia)', objectType):
                                    if objectType == 'boot.SdCard':
                                        # Pull in the Sub Types for Virtual Media
                                        jsonVars = jsonData['boot.SdCard']['allOf'][1]['properties']
                                    elif objectType == 'boot.Usb':
                                        # Pull in the Sub Types for Virtual Media
                                        jsonVars = jsonData['boot.Usb']['allOf'][1]['properties']
                                    elif objectType == 'boot.VirtualMedia':
                                        # Pull in the Sub Types for Virtual Media
                                        jsonVars = jsonData['boot.VirtualMedia']['allOf'][1]['properties']

                                    # Configured Boot Mode
                                    polVars['description'] = jsonVars['Subtype']['description']
                                    polVars["jsonVars"] = sorted(jsonVars['Subtype']['enum'])
                                    polVars["defaultVar"] = jsonVars['Subtype']['default']
                                    polVars["varType"] = 'Sub type'
                                    Subtype = ezfunctions.variablesFromAPI(**kwargs)

                                    boot_device.update({'subtype':Subtype})

                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                for k, v in boot_device.items():
                                    if k == 'bootloader_description':
                                        print(f'   bootloader_description = "{v}"')
                                    elif k == 'bootloader_name':
                                        print(f'   bootloader_name        = "{v}"')
                                    elif k == 'bootloader_path':
                                        print(f'   bootloader_path        = "{v}"')
                                    elif k == 'enabled':
                                        print(f'   enabled                = {v}')
                                    elif k == 'interface_name':
                                        print(f'   InterfaceName          = "{v}"')
                                    elif k == 'interface_source':
                                        print(f'   InterfaceSource        = "{v}"')
                                    elif k == 'ip_type':
                                        print(f'   IpType                 = "{v}"')
                                    elif k == 'mac_address':
                                        print(f'   MacAddress             = "{v}"')
                                    elif k == 'device_name':
                                        print(f'   name                   = "{v}"')
                                    elif k == 'lun':
                                        print(f'   Lun                    = {v}')
                                    elif k == 'object_type':
                                        print(f'   object_type            = "{v}"')
                                    elif k == 'port':
                                        print(f'   Port                   = {v}')
                                    elif k == 'slot':
                                        print(f'   Slot                   = "{v}"')
                                    elif k == 'subtype':
                                        print(f'   Subtype                = "{v}"')
                                    elif k == 'target_wwpn':
                                        print(f'   Wwpn                   = "{v}"')
                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                valid_confirm = False
                                while valid_confirm == False:
                                    confirm_config = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
                                    if confirm_config == 'Y' or confirm_config == '':
                                        polVars["boot_devices"].append(boot_device)
                                        valid_exit = False
                                        while valid_exit == False:
                                            if inner_loop_count < 3:
                                                loop_exit = input(f'Would You like to Configure another Boot Device?  Enter "Y" or "N" [Y]: ')
                                            else:
                                                loop_exit = input(f'Would You like to Configure another Boot Device?  Enter "Y" or "N" [N]: ')
                                            if loop_exit == 'Y' or (inner_loop_count < 3 and loop_exit == ''):
                                                inner_loop_count += 1
                                                valid_confirm = True
                                                valid_exit = True
                                            elif loop_exit == 'N' or loop_exit == '':
                                                sub_loop = True
                                                valid_confirm = True
                                                valid_exit = True
                                                valid_sub = True
                                            else: ezfunctions.message_invalid_y_or_n('short')

                                    elif confirm_config == 'N':
                                        print(f'\n-------------------------------------------------------------------------------------------\n')
                                        print(f'  Starting Boot Order Configuration Over.')
                                        print(f'\n-------------------------------------------------------------------------------------------\n')
                                        valid_confirm = True
                                    else: ezfunctions.message_invalid_y_or_n('short')

                        elif question == 'N':
                            sub_loop = True
                        else: ezfunctions.message_invalid_y_or_n('short')

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(textwrap.indent(yaml.dump(polVars, Dumper=MyDumper, default_flow_style=False), ' '*4, predicate=None))
                    print(f'-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
                        if confirm_policy == 'Y' or confirm_policy == '':
                            confirm_policy = 'Y'

                            # Write Policies to Template File
                            polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                            ezfunctions.write_to_template(self, **kwargs)

                            configure_loop, policy_loop = ezfunctions.exit_default(policy_type, 'N')
                            valid_confirm = True
                        elif confirm_policy == 'N':
                            ezfunctions.message_starting_over(policy_type)
                            valid_confirm = True
                        else: ezfunctions.message_invalid_y_or_n('short')
            elif configure == 'N': configure_loop = True
            else: ezfunctions.message_invalid_y_or_n('long')

        # Return kwargs
        return kwargs

    #==============================================
    # Certificate Management Policy Module
    #==============================================
    def certificate_management_policies(self, **kwargs):
        baseRepo    = kwargs['args'].dir
        ezData      = kwargs['ezData']
        jsonData    = kwargs['jsonData']
        name_prefix = self.name_prefix
        name_suffix = 'cert'
        org         = self.org
        path_sep    = kwargs['path_sep']
        policy_type = 'Certificate Management Policy'
        yaml_file   = 'management'
        polVars = {}

        # Open the Template file
        ezfunctions.write_to_template(self, **kwargs)
        polVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  A {policy_type} Allows you to specify the certificate and private key-pair ')
            print(f'  details for an external certificate.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - {baseRepo}{path_sep}{org}{path_sep}{self.type}{path_sep}{yaml_file}.yaml')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            loop_count = 1
            configure = input(f'Do You Want to Configure a {policy_type}.  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                policy_loop = False
                while policy_loop == False:

                    if not name_prefix == '': name = f'{name_prefix}-{name_suffix}'
                    else: name = f'{org}-{name_suffix}'

                    polVars['name']        = ezfunctions.policy_name(name, policy_type)
                    polVars['description'] = ezfunctions.policy_descr(polVars['name'], policy_type)

                    # Pull in the Policies for Certificate Management
                    jsonVars = jsonData['certificatemanagement.CertificateBase']['allOf'][1]['properties']
                    polVars["multi_select"] = False

                    # Request Certificate
                    polVars["Multi_Line_Input"] = True
                    polVars['description'] = jsonVars['Certificate']['description']
                    polVars["Variable"] = f'base64_certificate_{loop_count}'
                    certificate = ezfunctions.sensitive_var_value(jsonData, **kwargs)
                    polVars["certificate"] = loop_count

                    # Encode the Certificate as Base64
                    base64Cert = base64.b64encode(str.encode(certificate)).decode()
                    print('base64 encoded:')
                    print(base64Cert)
                    TF_VAR = f'base64_certificate_{loop_count}'
                    os.environ[TF_VAR] = base64Cert

                    # Request Private Key
                    polVars["Multi_Line_Input"] = True
                    polVars['description'] = jsonVars['Privatekey']['description']
                    polVars["Variable"] = f'base64_private_key_{loop_count}'
                    privateKey = ezfunctions.sensitive_var_value(jsonData, **kwargs)
                    polVars["private_key"] = loop_count

                    # Encode the Certificate as Base64
                    base64Key = base64.b64encode(str.encode(privateKey)).decode()
                    print('base64 encoded:')
                    print(base64Key)
                    TF_VAR = f'base64_certificate_{loop_count}'
                    os.environ[TF_VAR] = base64Key

                    polVars["enabled"] = True
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(textwrap.indent(yaml.dump(polVars, Dumper=MyDumper, default_flow_style=False), ' '*4, predicate=None))
                    print(f'-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
                        if confirm_policy == 'Y' or confirm_policy == '':
                            confirm_policy = 'Y'

                            # Write Policies to Template File
                            polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                            ezfunctions.write_to_template(self, **kwargs)

                            configure_loop, policy_loop = ezfunctions.exit_default(policy_type, 'N')
                            print(f'configure loop is {configure_loop}')
                            print(f'policy loop is {policy_loop}')
                            loop_count += 1
                            valid_confirm = True
                        elif confirm_policy == 'N':
                            ezfunctions.message_starting_over(policy_type)
                            valid_confirm = True
                        else: ezfunctions.message_invalid_y_or_n('short')
            elif configure == 'N': configure_loop = True
            else: ezfunctions.message_invalid_y_or_n('long')

        # Return kwargs
        return kwargs

    #==============================================
    # Device Connector Policy Module
    #==============================================
    def device_connector_policies(self, **kwargs):
        baseRepo    = kwargs['args'].dir
        ezData      = kwargs['ezData']
        jsonData    = kwargs['jsonData']
        name_prefix = self.name_prefix
        name_suffix = 'devcon'
        org         = self.org
        path_sep    = kwargs['path_sep']
        policy_type = 'Device Connector Policy'
        yaml_file   = 'management'
        polVars = {}

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  A {policy_type} lets you choose the Configuration from Intersight only option to control ')
            print(f'  configuration changes allowed from Cisco IMC. The Configuration from Intersight only ')
            print(f'  option is enabled by default. You will observe the following changes when you deploy the ')
            print(f'  Device Connector policy in Intersight:')
            print(f'  * Validation tasks will fail:')
            print(f'    - If Intersight Read-only mode is enabled in the claimed device.')
            print(f'    - If the firmware version of the Standalone C-Series Servers is lower than 4.0(1).')
            print(f'  * If Intersight Read-only mode is enabled, firmware upgrades will be successful only when ')
            print(f'    performed from Intersight. Firmware upgrade performed locally from Cisco IMC will fail.')
            print(f'  * IPMI over LAN privileges will be reset to read-only level if Configuration from ')
            print(f'    Intersight only is enabled through the Device Connector policy, or if the same ')
            print(f'    configuration is enabled in the Device Connector in Cisco IMC.\n\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - {baseRepo}{path_sep}{org}{path_sep}{self.type}{path_sep}{yaml_file}.yaml')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure a {policy_type}?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                policy_loop = False
                while policy_loop == False:

                    if not name_prefix == '': name = f'{name_prefix}-{name_suffix}'
                    else: name = f'{org}-{name_suffix}'

                    polVars['name']        = ezfunctions.policy_name(name, policy_type)
                    polVars['description'] = ezfunctions.policy_descr(polVars['name'], policy_type)

                    jsonVars = jsonData['deviceconnector.Policy']['allOf'][1]['properties']
                    polVars['description'] = jsonVars['LockoutEnabled']['description']
                    polVars["varInput"] = f'Do you want to lock down Configuration to Intersight only?'
                    polVars["varDefault"] = 'N'
                    polVars["varName"] = 'Lockout Enabled'
                    polVars["configuration_lockout"] = ezfunctions.varBoolLoop(**kwargs)

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(textwrap.indent(yaml.dump(polVars, Dumper=MyDumper, default_flow_style=False), ' '*4, predicate=None))
                    print(f'-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
                        if confirm_policy == 'Y' or confirm_policy == '':
                            confirm_policy = 'Y'

                            # Write Policies to Template File
                            polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                            ezfunctions.write_to_template(self, **kwargs)

                            configure_loop, policy_loop = ezfunctions.exit_default(policy_type, 'N')
                            valid_confirm = True
                        elif confirm_policy == 'N':
                            ezfunctions.message_starting_over(policy_type)
                            valid_confirm = True
                        else: ezfunctions.message_invalid_y_or_n('short')
            elif configure == 'N': configure_loop = True
            else: ezfunctions.message_invalid_y_or_n('long')

        # Return kwargs
        return kwargs

    #==============================================
    # Firmware - UCS Domain Module
    #==============================================
    def firmware_ucs_domain(self, **kwargs):
        polVars = {}
        polVars["header"] = 'UCS Domain Profile Variables'
        polVars["initial_write"] = True
        polVars["org"] = self.org
        polVars["policy_type"] = 'UCS Domain Profile'
        polVars["template_file"] = 'template_open.jinja2'
        polVars["template_type"] = 'ntp_policies'
        valid = False
        while valid == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'   UCS Version of Software to Deploy...')
            if os.path.isfile('ucs_version.txt'):
                version_file = open('ucs_version.txt', 'r')
                versions = []
                for line in version_file:
                    line = line.strip()
                    versions.append(line)
                for i, v in enumerate(versions):
                    i += 1
                    if i < 10:
                        print(f'     {i}. {v}')
                    else:
                        print(f'    {i}. {v}')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            ucs_version = input('Enter the Index Number for the Version of Software to Run: ')
            for i, v in enumerate(versions):
                i += 1
                if int(ucs_version) == i:
                    ucs_domain_version = v
                    valid = True
            if valid == False:
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'  Error!! Invalid Selection.  Please Select a valid Index from the List.')
                print(f'\n-------------------------------------------------------------------------------------------\n')
            version_file.close()

    #==============================================
    # IMC Access Policy Module
    #==============================================
    def imc_access_policies(self, **kwargs):
        baseRepo    = kwargs['args'].dir
        ezData      = kwargs['ezData']
        jsonData    = kwargs['jsonData']
        name_prefix = self.name_prefix
        name_suffix = 'imc'
        org         = self.org
        path_sep    = kwargs['path_sep']
        policy_type = 'IMC Access Policy'
        yaml_file   = 'management'
        polVars = {}

        # Open the Template file
        ezfunctions.write_to_template(self, **kwargs)
        polVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  You will need to configure an IMC Access Policy in order to Assign the VLAN and IPs to ')
            print(f'  the Servers for KVM Access.  At this time only inband access is supported in IMM mode.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - {baseRepo}{path_sep}{org}{path_sep}{self.type}{path_sep}{yaml_file}.yaml')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            loop_count = 0
            policy_loop = False
            while policy_loop == False:
                if not name_prefix == '':
                    name = f'{name_prefix}-{name_suffix}'
                else:
                    name = f'{org}-{name_suffix}'

                polVars['name']        = ezfunctions.policy_name(name, policy_type)
                polVars['description'] = ezfunctions.policy_descr(polVars['name'], policy_type)
                polVars["default_vlan"] = 0

                polVars["multi_select"] = False
                jsonVars = jsonData['server.BaseProfile']['allOf'][1]['properties']
                polVars['description'] = jsonVars['TargetPlatform']['description']
                polVars["jsonVars"] = sorted(jsonVars['TargetPlatform']['enum'])
                polVars["defaultVar"] = 'FIAttached'
                polVars["varType"] = 'Target Platform'
                polVars["target_platform"] = ezfunctions.variablesFromAPI(**kwargs)

                # IMC Access Type
                jsonVars = jsonData['access.Policy']['allOf'][1]['properties']
                polVars['description'] = jsonVars['ConfigurationType']['description']
                polVars["jsonVars"] = ['inband', 'out_of_band']
                polVars["defaultVar"] = 'inband'
                polVars["varType"] = 'IMC Access Type'
                imcBand = ezfunctions.variablesFromAPI(**kwargs)

                policy_list = [
                    f'pools.ip_pools.{imcBand}_ip_pool'
                ]
                polVars["allow_opt_out"] = False
                for policy in policy_list:
                    policy_type = policy.split('.')[2]
                    polVars[policy_type],policyData = policy_select_loop(jsonData, ezData, name_prefix, policy, **kwargs)

                if imcBand == 'inband':
                    valid = False
                    while valid == False:
                        polVars["inband_vlan_id"] = input('What VLAN Do you want to Assign to this Policy? ')
                        valid_vlan = validating.number_in_range('VLAN ID', polVars["inband_vlan_id"], 1, 4094)
                        if valid_vlan == True:
                            if polVars["target_platform"] == 'FIAttached':
                                policy_list = [
                                    'policies.vlan_policies.vlan_policy',
                                ]
                                polVars["allow_opt_out"] = False
                                for policy in policy_list:
                                    vlan_policy,policyData = policy_select_loop(jsonData, ezData, name_prefix, policy, **kwargs)
                                vlan_list = []
                                print(json.dumps(policyData['vlan_policies'], indent=4))
                                for key, value in policyData['vlan_policies'].items():
                                    if key == vlan_policy:
                                        for k, v in value['vlans'].items():
                                            vlan_list.append(v['vlan_list'])

                                vlan_convert = ''
                                for vlan in vlan_list:
                                    vlan = str(vlan)
                                    vlan_convert = vlan_convert + ',' + str(vlan)
                                vlan_list = ezfunctions.vlan_list_full(vlan_convert)
                                vlan_count = 0
                                for vlan in vlan_list:
                                    if int(polVars["inband_vlan_id"]) == int(vlan):
                                        vlan_count = 1
                                        break
                                if vlan_count == 0:
                                    vlan_string = ', '.join(map(str,vlan_list))
                                    print(f'\n-------------------------------------------------------------------------------------------\n')
                                    print(f'  Error with Inband VLAN Assignment!!  The VLAN {polVars["inband_vlan_id"]} is not in the VLAN Policy')
                                    print(f'  {vlan_policy}.  VALID VLANs are:')
                                    print(fill(f'    {vlan_string}',width=88, subsequent_indent='    '))
                                    print(f'\n-------------------------------------------------------------------------------------------\n')
                                else:
                                    valid = True
                            else:
                                valid = True

                valid = False
                while valid == False:
                    enable_ipv4 = input('Do you want to enable IPv4 for this Policy?  Enter "Y" or "N" [Y]: ')
                    if enable_ipv4 == 'Y' or enable_ipv4 == '':
                        polVars["ipv4_address_configuration"] = True
                        valid = True
                    else:
                        polVars["ipv4_address_configuration"] = False
                        valid = True

                valid = False
                while valid == False:
                    enable_ipv4 = input('Do you want to enable IPv6 for this Policy?  Enter "Y" or "N" [N]: ')
                    if enable_ipv4 == 'Y':
                        polVars["ipv6_address_configuration"] = True
                        valid = True
                    else:
                        polVars["ipv6_address_configuration"] = False
                        valid = True

                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(textwrap.indent(yaml.dump(polVars, Dumper=MyDumper, default_flow_style=False), ' '*4, predicate=None))
                print(f'-------------------------------------------------------------------------------------------\n')
                valid_confirm = False
                while valid_confirm == False:
                    confirm_policy = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                    if confirm_policy == 'Y' or confirm_policy == '':
                        confirm_policy = 'Y'

                        # Write Policies to Template File
                        polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                        ezfunctions.write_to_template(self, **kwargs)

                        configure_loop, policy_loop = ezfunctions.exit_default(policy_type, 'N')
                        valid_confirm = True
                    elif confirm_policy == 'N':
                        ezfunctions.message_starting_over(policy_type)
                        valid_confirm = True
                    else: ezfunctions.message_invalid_y_or_n('long')
        # Return kwargs
        return kwargs

    #==============================================
    # IPMI over LAN Policy Module
    #==============================================
    def ipmi_over_lan_policies(self, **kwargs):
        baseRepo    = kwargs['args'].dir
        ezData      = kwargs['ezData']
        jsonData    = kwargs['jsonData']
        name_prefix = self.name_prefix
        name_suffix = 'ipmi'
        org         = self.org
        path_sep    = kwargs['path_sep']
        policy_type = 'IPMI over LAN Policy'
        yaml_file   = 'management'

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  An {policy_type} will configure IPMI over LAN access on a Server Profile.  This policy')
            print(f'  allows you to determine whether IPMI commands can be sent directly to the server, using ')
            print(f'  the IP address.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - {baseRepo}{path_sep}{org}{path_sep}{self.type}{path_sep}{yaml_file}.yaml')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure an {policy_type}?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                policy_loop = False
                while policy_loop == False:

                    if not name_prefix == '': name = f'{name_prefix}-{name_suffix}'
                    else: name = f'{org}-{name_suffix}'
                    polVars = {}
                    polVars['name']        = ezfunctions.policy_name(name, policy_type)
                    polVars['description'] = ezfunctions.policy_descr(polVars['name'], policy_type)

                    valid = False
                    while valid == False:
                        encrypt_traffic = input('Do you want to encrypt IPMI over LAN Traffic?  Enter "Y" or "N" [Y]: ')
                        if encrypt_traffic == 'Y' or encrypt_traffic == '':
                            kwargs['Variable'] = 'ipmi_key'
                            kwargs['ipmi_key'] = ezfunctions.sensitive_var_value(**kwargs)

                    kwargs["multi_select"] = False
                    jsonVars = jsonData['ipmioverlan.Policy']['allOf'][1]['properties']

                    kwargs['jData'] = deepcopy(jsonVars['Privilege'])
                    kwargs['jData']["varType"] = 'IPMI Privilege'
                    polVars["privilege"] = ezfunctions.variablesFromAPI(**kwargs)

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(textwrap.indent(yaml.dump(polVars, Dumper=MyDumper, default_flow_style=False), ' '*4, predicate=None))
                    print(f'-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                        if confirm_policy == 'Y' or confirm_policy == '':
                            confirm_policy = 'Y'

                            # Write Policies to Template File
                            polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                            ezfunctions.write_to_template(self, **kwargs)

                            configure_loop, policy_loop = ezfunctions.exit_default(policy_type, 'N')
                            valid_confirm = True
                        elif confirm_policy == 'N':
                            ezfunctions.message_starting_over(policy_type)
                            valid_confirm = True
                        else: ezfunctions.message_invalid_y_or_n('short')
            elif configure == 'N': configure_loop = True
            else: ezfunctions.message_invalid_y_or_n('long')
        # Return kwargs
        return kwargs

    #==============================================
    # LDAP Policy Module
    #==============================================
    def ldap_policies(self, **kwargs):
        baseRepo    = kwargs['args'].dir
        ezData      = kwargs['ezData']
        jsonData    = kwargs['jsonData']
        name_prefix = self.name_prefix
        name_suffix = 'ldap'
        org         = self.org
        path_sep    = kwargs['path_sep']
        policy_type = 'LDAP Policy'
        yaml_file   = 'management'
        polVars = {}

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  An {policy_type} stores and maintains directory information in a network. When LDAP is ')
            print(f'  enabled in the Cisco IMC, user authentication and role authorization is performed by the ')
            print(f'  LDAP server for user accounts not found in the local user database. You can enable and ')
            print(f'  configure LDAP, and configure LDAP servers and LDAP groups.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - {baseRepo}{path_sep}{org}{path_sep}{self.type}{path_sep}{yaml_file}.yaml')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure an {policy_type}?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                loop_count = 1
                policy_loop = False
                while policy_loop == False:

                    if not name_prefix == '': name = f'{name_prefix}-{name_suffix}'
                    else: name = f'{org}-{name_suffix}'

                    polVars['name']        = ezfunctions.policy_name(name, policy_type)
                    polVars['description'] = ezfunctions.policy_descr(polVars['name'], policy_type)
                    polVars["enable_ldap"] = True

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  The LDAP Base domain that all users must be in.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid = False
                    while valid == False:
                        domain = input(f'What is your LDAP Base Domain? [example.com]: ')
                        if domain == '':
                            domain = 'example.com'
                        valid = validating.domain('LDAP Domain', domain)

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  Base Distinguished Name (DN). Starting point from where the server will search for users')
                    print(f'  and groups. An example would be "dc=example,dc=com".')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid = False
                    while valid == False:
                        domain_split = domain.split('.')
                        base_dn_var = 'DC=%s' % (',DC='.join(domain_split))

                        base_dn = input(f'What is your Base Distinguished Name?  [{base_dn_var}]: ')
                        if base_dn == '':
                            base_dn = base_dn_var
                        base_split = base_dn.split(',')
                        base_count = 0
                        for x in base_split:
                            if not re.search(r'^(dc)\=[a-zA-Z0-9\-]+$', x, re.IGNORECASE):
                                base_count += 1
                        if base_count == 0:
                            valid = True
                        else:
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            print(f'  Error!! "{base_dn}" is not a valid Base DN.')
                            print(f'\n-------------------------------------------------------------------------------------------\n')

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  LDAP authentication timeout duration, in seconds.  Range is 0 to 180.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid = False
                    while valid == False:
                        base_timeout = input(f'What do you want set for LDAP Authentication Timeout?  [0]: ')
                        if base_timeout == '':
                            base_timeout = 0
                        if re.fullmatch(r'[0-9]+', str(base_timeout)):
                            polVars["minNum"] = 0
                            polVars["maxNum"] = 180
                            polVars["varName"] = 'LDAP Timeout'
                            varValue = base_timeout
                            valid = validating.number_in_range(polVars["varName"], varValue, polVars["minNum"], polVars["maxNum"])
                        else:
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            print(f'  Error!! Invalid Value.  Please enter a number in the range of 0 to 180.')
                            print(f'\n-------------------------------------------------------------------------------------------\n')

                    polVars["base_settings"] = {
                        'base_dn':base_dn,
                        'domain':domain,
                        'timeout':base_timeout
                    }

                    polVars["multi_select"] = False
                    jsonVars = jsonData['iam.LdapBaseProperties']['allOf'][1]['properties']
                    polVars['description'] = jsonVars['BindMethod']['description']
                    polVars["jsonVars"] = sorted(jsonVars['BindMethod']['enum'])
                    polVars["defaultVar"] = jsonVars['BindMethod']['default']
                    polVars["varType"] = 'LDAP Bind Method'
                    bind_method = ezfunctions.variablesFromAPI(**kwargs)

                    if not bind_method == 'LoginCredentials':
                        valid = False
                        while valid == False:
                            varUser = input(f'What is the username you want to use for authentication? ')
                            varOU = input(f'What is the Organizational Unit for {varUser}? ')
                            bind_dn = input(f'What is the Distinguished Name for the user? [CN={varUser},OU={varOU},{base_dn}]')
                            if bind_dn == '':
                                bind_dn = 'CN=%s,OU=%s,%s' % (varUser, varOU, base_dn)
                            polVars["minLength"] = 1
                            polVars["maxLength"] = 254
                            polVars["varName"] = 'LDAP Bind DN'
                            varValue = bind_dn
                            valid = validating.string_length(polVars["varName"], varValue, polVars["minLength"], polVars["maxLength"])

                        valid = False
                        while valid == False:
                            secure_passphrase = stdiomask.getpass(prompt='What is the password of the user for initial bind process? ')
                            polVars["minLength"] = 1
                            polVars["maxLength"] = 254
                            polVars["rePattern"] = '^[\\S]+$'
                            polVars["varName"] = 'LDAP Password'
                            varValue = secure_passphrase
                            valid_passphrase = validating.length_and_regex_sensitive(polVars["rePattern"], polVars["varName"], varValue, polVars["minLength"], polVars["maxLength"])
                            if valid_passphrase == True:
                                os.environ['TF_VAR_binding_parameters_password'] = '%s' % (secure_passphrase)
                                valid = True
                        polVars["binding_parameters"] = {
                            'bind_dn':bind_dn,
                            'bind_method':bind_method
                        }
                    else:
                        polVars["binding_parameters"] = {
                            'bind_method':bind_method
                        }
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  Secure LDAP is not supported but LDAP encryption is.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid = False
                    while valid == False:
                        enable_encryption = input(f'\nDo you want to encrypt all information sent to the LDAP server?  Enter "Y" or "N" [Y]: ')
                        if enable_encryption == 'N':
                            polVars["enable_encryption"] = False
                            valid = True
                        elif enable_encryption == '' or enable_encryption == 'Y':
                            polVars["enable_encryption"] = True
                            valid = True
                        else: ezfunctions.message_invalid_y_or_n('short')

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  If enabled, user authorization is also done at the group level for LDAP users not in the')
                    print(f'  local user database.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid = False
                    while valid == False:
                        group_auth = input(f'\nDo you want to enable Group Authorization?  Enter "Y" or "N" [Y]: ')
                        if group_auth == 'N':
                            polVars["enable_group_authorization"] = False
                            valid = True
                        elif group_auth == '' or group_auth == 'Y':
                            polVars["enable_group_authorization"] = True
                            valid = True
                        else: ezfunctions.message_invalid_y_or_n('short')

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  This Section gives you the option to query DNS for LDAP Server information isntead of')
                    print(f'  defining the LDAP Servers.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid = False
                    while valid == False:
                        ldap_from_dns = input(f'\nDo you want to use DNS for LDAP Server discovery?  Enter "Y" or "N" [N]: ')
                        if ldap_from_dns == '' or ldap_from_dns == 'N':
                            ldap_from_dns = False
                            valid = True
                        elif ldap_from_dns == 'Y':
                            ldap_from_dns = True
                            valid = True
                        else: ezfunctions.message_invalid_y_or_n('short')

                    if ldap_from_dns == True:
                        polVars["multi_select"] = False
                        jsonVars = jsonData['iam.LdapDnsParameters']['allOf'][1]['properties']
                        polVars['description'] = jsonVars['Source']['description']
                        polVars["jsonVars"] = sorted(jsonVars['Source']['enum'])
                        polVars["defaultVar"] = jsonVars['Source']['default']
                        polVars["varType"] = 'LDAP Domain Source'
                        varSource = ezfunctions.variablesFromAPI(**kwargs)

                        if not varSource == 'Extracted':
                            valid = False
                            while valid == False:
                                searchDomain = input(f'\nNote: Domain that acts as a source for a DNS query.\n'\
                                    'What is the Search Domain? ')
                                valid = validating.domain('Search Domain', searchDomain)

                            valid = False
                            while valid == False:
                                searchForest = input(f'\nNote: Forst that acts as a source for a DNS query.\n'\
                                    'What is the Search Forest? ')
                                valid = validating.domain('Search Forest', searchForest)
                            polVars["ldap_From_dns"] = {
                                'enable':True,
                                'search_domain':searchDomain,
                                'search_forest':searchForest,
                                'source':varSource
                            }
                        else:
                            polVars["ldap_From_dns"] = {
                                'enable':True,
                                'source':varSource
                            }

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  An LDAP attribute that contains the role and locale information for the user. This ')
                    print(f'  property is always a name-value pair. The system queries the user record for the value ')
                    print(f'  that matches this attribute name.')
                    print(f'  The LDAP attribute can use an existing LDAP attribute that is mapped to the Cisco IMC user')
                    print(f'  roles and locales, or can modify the schema such that a new LDAP attribute can be created.')
                    print(f'  For example, CiscoAvPair.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid = False
                    while valid == False:
                        varAttribute = input(f'What is the attribute to use for the LDAP Search?  [CiscoAvPair]: ')
                        if varAttribute == '':
                            varAttribute = 'CiscoAvPair'
                        valid = True

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  This field must match the configured attribute in the schema on the LDAP server.')
                    print(f'  By default, this field displays sAMAccountName.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid = False
                    while valid == False:
                        varFilter = input(f'What is the Filter to use for matching the username?  [sAMAccountName]: ')
                        if varFilter == '':
                            varFilter = 'sAMAccountName'
                        valid = True

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  This field must match the configured attribute in the schema on the LDAP server.')
                    print(f'  By default, this field displays memberOf.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid = False
                    while valid == False:
                        varGroupAttribute = input(f'What is the Group Attribute to use for matching the Group Names?  [memberOf]: ')
                        if varGroupAttribute == '':
                            varGroupAttribute = 'memberOf'
                        valid = True

                    polVars["search_parameters"] = {
                        'attribute':varAttribute,
                        'filter':varFilter,
                        'group_attribute':varGroupAttribute
                    }

                    valid = False
                    while valid == False:
                        varNested = input(f'What is the Search depth to look for a nested LDAP group in an LDAP group map?  Range is 1 to 128.  [128]: ')
                        if varNested == '':
                            varNested = 128
                        if re.fullmatch(r'^[0-9]+', str(varNested)):
                            polVars["minNum"] = 1
                            polVars["maxNum"] = 128
                            polVars["varName"] = 'Nested Group Search Depth'
                            varValue = varNested
                            valid = validating.number_in_range(polVars["varName"], varValue, polVars["minNum"], polVars["maxNum"])
                        else:
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            print(f'  Error!! Invalid Value.  Please enter a port in the range of {polVars["minNum"]} and {polVars["maxNum"]}.')
                            print(f'\n-------------------------------------------------------------------------------------------\n')

                    polVars["nested_group_search_depth"] = varNested

                    polVars["multi_select"] = False
                    jsonVars = jsonData['iam.LdapPolicy']['allOf'][1]['properties']
                    polVars['description'] = jsonVars['UserSearchPrecedence']['description']
                    polVars["jsonVars"] = sorted(jsonVars['UserSearchPrecedence']['enum'])
                    polVars["defaultVar"] = jsonVars['UserSearchPrecedence']['default']
                    polVars["varType"] = 'User Search Precedence'
                    polVars["user_search_precedence"] = ezfunctions.variablesFromAPI(**kwargs)

                    polVars["ldap_groups"] = []
                    inner_loop_count = 1
                    sub_loop = False
                    while sub_loop == False:
                        question = input(f'\nWould you like to configure an LDAP Group?  Enter "Y" or "N" [Y]: ')
                        if question == '' or question == 'Y':
                            valid_sub = False
                            while valid_sub == False:
                                valid = False
                                while valid == False:
                                    varGroup = input(f'What is Group you would like to add from LDAP? ')
                                    if not varGroup == '':
                                        polVars["minLength"] = 1
                                        polVars["maxLength"] = 127
                                        polVars["rePattern"] = '^([^+\\-][a-zA-Z0-9\\=\\!\\#\\$\\%\\(\\)\\+,\\-\\.\\:\\;\\@ \\_\\{\\|\\}\\~\\?\\&]+)$'
                                        polVars["varName"] = 'LDAP Group'
                                        varValue = varGroup
                                        valid = validating.length_and_regex(polVars["rePattern"], polVars["varName"], varValue, polVars["minLength"], polVars["maxLength"])
                                    else:
                                        print(f'\n-------------------------------------------------------------------------------------------\n')
                                        print(f'  Error!! Invalid Value.  Please Re-enter the LDAP Group.')
                                        print(f'\n-------------------------------------------------------------------------------------------\n')

                                polVars["multi_select"] = False
                                jsonVars = ezData['policies']['iam.LdapPolicy']
                                polVars['description'] = jsonVars['role']['description']
                                polVars["jsonVars"] = sorted(jsonVars['role']['enum'])
                                polVars["defaultVar"] = jsonVars['role']['default']
                                polVars["varType"] = 'Group Role'
                                role = ezfunctions.variablesFromAPI(**kwargs)

                                ldap_group = {
                                    'group':varGroup,
                                    'role':role
                                }

                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                print(f'   group = "{varGroup}"')
                                print(f'   role  = "{role}"')
                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                valid_confirm = False
                                while valid_confirm == False:
                                    confirm_config = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
                                    if confirm_config == 'Y' or confirm_config == '':
                                        polVars["ldap_groups"].append(ldap_group)
                                        valid_exit = False
                                        while valid_exit == False:
                                            loop_exit = input(f'Would You like to Configure another LDAP Group?  Enter "Y" or "N" [N]: ')
                                            if loop_exit == 'Y':
                                                inner_loop_count += 1
                                                valid_confirm = True
                                                valid_exit = True
                                            elif loop_exit == 'N' or loop_exit == '':
                                                sub_loop = True
                                                valid_confirm = True
                                                valid_exit = True
                                                valid_sub = True
                                            else: ezfunctions.message_invalid_y_or_n('short')

                                    elif confirm_config == 'N':
                                        print(f'\n-------------------------------------------------------------------------------------------\n')
                                        print(f'  Starting LDAP Group Configuration Over.')
                                        print(f'\n-------------------------------------------------------------------------------------------\n')
                                        valid_confirm = True
                                    else: ezfunctions.message_invalid_y_or_n('short')

                        elif question == 'N':
                            sub_loop = True
                        else: ezfunctions.message_invalid_y_or_n('short')

                    polVars["ldap_servers"] = []
                    inner_loop_count = 1
                    sub_loop = False
                    while sub_loop == False:
                        question = input(f'\nWould you like to configure LDAP Servers?  Enter "Y" or "N" [Y]: ')
                        if question == '' or question == 'Y':
                            valid_sub = False
                            while valid_sub == False:
                                valid = False
                                while valid == False:
                                    varServer = input(f'What is Hostname/IP of the LDAP Server? ')
                                    polVars["varName"] = 'LDAP Server'
                                    varValue = varServer
                                    if re.fullmatch(r'^([0-9]{1,3}\.){3}[0-9]{1,3}$', varServer):
                                        valid = validating.ip_address(polVars["varName"], varValue)
                                    else:
                                        valid = validating.dns_name(polVars["varName"], varValue)

                                valid = False
                                while valid == False:
                                    if polVars["enable_encryption"] == True:
                                        xPort = 636
                                    else:
                                        xPort = 389
                                    varPort = input(f'What is Port for {varServer}? [{xPort}]: ')
                                    if varPort == '':
                                        varPort = xPort
                                    if re.fullmatch(r'^[0-9]+', str(varPort)):
                                        polVars["minNum"] = 1
                                        polVars["maxNum"] = 65535
                                        polVars["varName"] = 'Server Port'
                                        varValue = varPort
                                        valid = validating.number_in_range(polVars["varName"], varValue, polVars["minNum"], polVars["maxNum"])
                                    else:
                                        print(f'\n-------------------------------------------------------------------------------------------\n')
                                        print(f'  Error!! Invalid Value.  Please enter a port in the range of {polVars["minNum"]} and {polVars["maxNum"]}.')
                                        print(f'\n-------------------------------------------------------------------------------------------\n')

                                ldap_server = {
                                    'port':varPort,
                                    'server':varServer
                                }

                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                print(f'   port   = "{varPort}"')
                                print(f'   server = "{varServer}"')
                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                valid_confirm = False
                                while valid_confirm == False:
                                    confirm_config = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
                                    if confirm_config == 'Y' or confirm_config == '':
                                        polVars["ldap_servers"].append(ldap_server)
                                        valid_exit = False
                                        while valid_exit == False:
                                            loop_exit = input(f'Would You like to Configure another LDAP Server?  Enter "Y" or "N" [N]: ')
                                            if loop_exit == 'Y':
                                                inner_loop_count += 1
                                                valid_confirm = True
                                                valid_exit = True
                                            elif loop_exit == 'N' or loop_exit == '':
                                                sub_loop = True
                                                valid_confirm = True
                                                valid_exit = True
                                                valid_sub = True
                                            else: ezfunctions.message_invalid_y_or_n('short')

                                    elif confirm_config == 'N':
                                        print(f'\n-------------------------------------------------------------------------------------------\n')
                                        print(f'  Starting LDAP Server Configuration Over.')
                                        print(f'\n-------------------------------------------------------------------------------------------\n')
                                        valid_confirm = True
                                    else: ezfunctions.message_invalid_y_or_n('short')

                        elif question == 'N':
                            sub_loop = True
                        else: ezfunctions.message_invalid_y_or_n('short')

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(textwrap.indent(yaml.dump(polVars, Dumper=MyDumper, default_flow_style=False), ' '*4, predicate=None))
                    print(f'-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
                        if confirm_policy == 'Y' or confirm_policy == '':
                            confirm_policy = 'Y'

                            # Write Policies to Template File
                            polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                            ezfunctions.write_to_template(self, **kwargs)

                            configure_loop, policy_loop = ezfunctions.exit_default(policy_type, 'N')
                            valid_confirm = True
                        elif confirm_policy == 'N':
                            ezfunctions.message_starting_over(policy_type)
                            valid_confirm = True
                        else: ezfunctions.message_invalid_y_or_n('short')
            elif configure == 'N': configure_loop = True
            else: ezfunctions.message_invalid_y_or_n('long')
        # Return kwargs
        return kwargs

    #==============================================
    # Local User Policy Module
    #==============================================
    def local_user_policies(self, jsonData, ezData, **kwargs):
        baseRepo    = kwargs['args'].dir
        ezData      = kwargs['ezData']
        jsonData    = kwargs['jsonData']
        name_prefix = self.name_prefix
        name_suffix = 'users'
        org         = self.org
        path_sep    = kwargs['path_sep']
        policy_type = 'Local User Policy'
        yaml_file   = 'management'
        polVars = {}

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  A {policy_type} will configure servers with Local Users for KVM Access.  This Policy ')
            print(f'  is not required to standup a server but is a good practice for day 2 support.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - {baseRepo}{path_sep}{org}{path_sep}{self.type}{path_sep}{yaml_file}.yaml')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure a {policy_type}?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                loop_count = 1
                policy_loop = False
                while policy_loop == False:

                    if not name_prefix == '': name = f'{name_prefix}-{name_suffix}'
                    else: name = f'{org}-{name_suffix}'

                    polVars['name']        = ezfunctions.policy_name(name, policy_type)
                    polVars['description'] = ezfunctions.policy_descr(polVars['name'], policy_type)

                    # Obtain Information for iam.EndpointPasswordProperties
                    polVars["multi_select"] = False
                    jsonVars = jsonData['iam.EndPointPasswordProperties']['allOf'][1]['properties']

                    # Local User Always Send Password
                    polVars['description'] = jsonVars['ForceSendPassword']['description']
                    polVars["varInput"] = f'Do you want Intersight to Always send the user password with policy updates?'
                    polVars["varDefault"] = 'N'
                    polVars["varName"] = 'Force Send Password'
                    polVars["always_send_user_password"] = ezfunctions.varBoolLoop(**kwargs)

                    # Local User Enforce Strong Password
                    polVars['description'] = jsonVars['EnforceStrongPassword']['description']
                    polVars["varInput"] = f'Do you want to Enforce Strong Passwords?'
                    polVars["varDefault"] = 'Y'
                    polVars["varName"] = 'Enforce Strong Password'
                    polVars["enforce_strong_password"] = ezfunctions.varBoolLoop(**kwargs)

                    # Local User Password Expiry
                    polVars['description'] = jsonVars['EnablePasswordExpiry']['description']
                    polVars["varInput"] = f'Do you want to Enable password Expiry on the Endpoint?'
                    polVars["varDefault"] = 'Y'
                    polVars["varName"] = 'Enable Password Expiry'
                    polVars["enable_password_expiry"] = ezfunctions.varBoolLoop(**kwargs)

                    if polVars["enable_password_expiry"] == True:
                        # Local User Grace Period
                        polVars['description'] = 'Grace Period, in days, after the password is expired '\
                                'that a user can continue to use their expired password.'\
                                'The allowed grace period is between 0 to 5 days.  With 0 being no grace period.'
                        polVars["varDefault"] =  jsonVars['GracePeriod']['default']
                        polVars["varInput"] = 'How many days would you like to set for the Grace Period?'
                        polVars["varName"] = 'Grace Period'
                        polVars["varRegex"] = '[0-9]+'
                        polVars["minNum"] = jsonVars['GracePeriod']['minimum']
                        polVars["maxNum"] = jsonVars['GracePeriod']['maximum']
                        polVars["grace_period"] = ezfunctions.varNumberLoop(**kwargs)

                        # Local User Notification Period
                        polVars['description'] = 'Notification Period - Number of days, between 0 to 15 '\
                                '(0 being disabled), that a user is notified to change their password before it expires.'
                        polVars["varDefault"] =  jsonVars['NotificationPeriod']['default']
                        polVars["varInput"] = 'How many days would you like to set for the Notification Period?'
                        polVars["varName"] = 'Notification Period'
                        polVars["varRegex"] = '[0-9]+'
                        polVars["minNum"] = jsonVars['NotificationPeriod']['minimum']
                        polVars["maxNum"] = jsonVars['NotificationPeriod']['maximum']
                        polVars["notification_period"] = ezfunctions.varNumberLoop(**kwargs)

                        # Local User Password Expiry Duration
                        valid = False
                        while valid == False:
                            polVars['description'] = 'Note: When Password Expiry is Enabled, Password Expiry '\
                                    'Duration sets the duration of time, (in days), a password may be valid.  '\
                                    'The password expiryduration must be greater than '\
                                    'notification period + grace period.  Range is 1-3650.'
                            polVars["varDefault"] =  jsonVars['PasswordExpiryDuration']['default']
                            polVars["varInput"] = 'How many days would you like to set for the Password Expiry Duration?'
                            polVars["varName"] = 'Password Expiry Duration'
                            polVars["varRegex"] = '[0-9]+'
                            polVars["minNum"] = jsonVars['PasswordExpiryDuration']['minimum']
                            polVars["maxNum"] = jsonVars['PasswordExpiryDuration']['maximum']
                            polVars["password_expiry_duration"] = ezfunctions.varNumberLoop(**kwargs)
                            x = int(polVars["grace_period"])
                            y = int(polVars["notification_period"])
                            z = int(polVars["password_expiry_duration"])
                            if z > (x + y):
                                valid = True
                            else:
                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                print(f'  Error!! The Value of Password Expiry Duration must be greater than Grace Period +')
                                print(f'  Notification Period.  {z} is not greater than [{x} + {y}]')
                                print(f'\n-------------------------------------------------------------------------------------------\n')

                        # Local User Notification Period
                        polVars['description'] = jsonVars['PasswordHistory']['description'] + \
                            ' Range is 0 to 5.'
                        polVars["varDefault"] =  jsonVars['PasswordHistory']['default']
                        polVars["varInput"] = 'How many passwords would you like to store for a user?'
                        polVars["varName"] = 'Password History'
                        polVars["varRegex"] = '[0-9]+'
                        polVars["minNum"] = jsonVars['PasswordHistory']['minimum']
                        polVars["maxNum"] = jsonVars['PasswordHistory']['maximum']
                        polVars["password_history"] = ezfunctions.varNumberLoop(**kwargs)

                    else:
                        polVars["grace_period"] = 0
                        polVars["notification_period"] = 15
                        polVars["password_expiry_duration"] = 90
                        polVars["password_history"] = 5

                    # Local Users
                    ilCount = 1
                    local_users = []
                    user_loop = False
                    while user_loop == False:
                        question = input(f'Would you like to configure a Local user?  Enter "Y" or "N" [Y]: ')
                        if question == '' or question == 'Y':
                            local_users,user_loop = ezfunctions.local_users_function(
                                jsonData, ezData, ilCount, **kwargs
                            )
                        elif question == 'N':
                            user_loop = True
                        else: ezfunctions.message_invalid_y_or_n('short')
                    polVars["local_users"] = local_users

                    polVars["enabled"] = True
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(textwrap.indent(yaml.dump(polVars, Dumper=MyDumper, default_flow_style=False), ' '*4, predicate=None))
                    print(f'-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                        if confirm_policy == 'Y' or confirm_policy == '':
                            confirm_policy = 'Y'

                            # Write Policies to Template File
                            polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                            ezfunctions.write_to_template(self, **kwargs)

                            configure_loop, policy_loop = ezfunctions.exit_default(policy_type, 'N')
                            valid_confirm = True
                        elif confirm_policy == 'N':
                            ezfunctions.message_starting_over(policy_type)
                            valid_confirm = True
                        else: ezfunctions.message_invalid_y_or_n('short')
            elif configure == 'N': configure_loop = True
            else: ezfunctions.message_invalid_y_or_n('long')
        # Return kwargs
        return kwargs

    #==============================================
    # Network Connectivity Policy Module
    #==============================================
    def network_connectivity_policies(self, **kwargs):
        baseRepo    = kwargs['args'].dir
        ezData      = kwargs['ezData']
        jsonData    = kwargs['jsonData']
        name_prefix = self.name_prefix
        name_suffix = 'dns'
        org         = self.org
        path_sep    = kwargs['path_sep']
        policy_type = 'Network Connectivity Policy'
        yaml_file   = 'management'
        polVars = {}

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  It is strongly recommended to have a Network Connectivity (DNS) Policy for the')
            print(f'  UCS Domain Profile.  Without it, DNS resolution will fail.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - {baseRepo}{path_sep}{org}{path_sep}{self.type}{path_sep}{yaml_file}.yaml')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            policy_loop = False
            while policy_loop == False:

                if not name_prefix == '':
                    name = f'{name_prefix}-{name_suffix}'
                else:
                    name = f'{org}-{name_suffix}'

                polVars['name']        = ezfunctions.policy_name(name, policy_type)
                polVars['description'] = ezfunctions.policy_descr(polVars['name'], policy_type)

                valid = False
                while valid == False:
                    polVars["preferred_ipv4_dns_server"] = input('What is your Primary IPv4 DNS Server?  [208.67.220.220]: ')
                    if polVars["preferred_ipv4_dns_server"] == '':
                        polVars["preferred_ipv4_dns_server"] = '208.67.220.220'
                    valid = validating.ip_address('Primary IPv4 DNS Server', polVars["preferred_ipv4_dns_server"])

                valid = False
                while valid == False:
                    alternate_true = input('Do you want to Configure an Alternate IPv4 DNS Server?  Enter "Y" or "N" [Y]: ')
                    if alternate_true == 'Y' or alternate_true == '':
                        polVars["alternate_ipv4_dns_server"] = input('What is your Alternate IPv4 DNS Server?  [208.67.222.222]: ')
                        if polVars["alternate_ipv4_dns_server"] == '':
                            polVars["alternate_ipv4_dns_server"] = '208.67.222.222'
                        valid = validating.ip_address('Alternate IPv4 DNS Server', polVars["alternate_ipv4_dns_server"])
                    elif alternate_true == 'N':
                        polVars["alternate_ipv4_dns_server"] = ''
                        valid = True
                    else: ezfunctions.message_invalid_y_or_n('short')

                valid = False
                while valid == False:
                    enable_ipv6 = input('Do you want to Configure IPv6 DNS?  Enter "Y" or "N" [N]: ')
                    if enable_ipv6 == 'Y':
                        polVars["enable_ipv6"] = True
                        polVars["preferred_ipv6_dns_server"] = input('What is your Primary IPv6 DNS Server?  [2620:119:35::35]: ')
                        if polVars["preferred_ipv6_dns_server"] == '':
                            polVars["preferred_ipv6_dns_server"] = '2620:119:35::35'
                        valid = validating.ip_address('Primary IPv6 DNS Server', polVars["preferred_ipv6_dns_server"])
                    if enable_ipv6 == 'N' or enable_ipv6 == '':
                        polVars["enable_ipv6"] = False
                        polVars["preferred_ipv6_dns_server"] = ''
                        valid = True

                valid = False
                while valid == False:
                    if enable_ipv6 == 'Y':
                        alternate_true = input('Do you want to Configure an Alternate IPv6 DNS Server?  Enter "Y" or "N" [Y]: ')
                        if alternate_true == 'Y' or alternate_true == '':
                            polVars["alternate_ipv6_dns_server"] = input('What is your Alternate IPv6 DNS Server?  [2620:119:53::53]: ')
                            if polVars["alternate_ipv6_dns_server"] == '':
                                polVars["alternate_ipv6_dns_server"] = '2620:119:53::53'
                            valid = validating.ip_address('Alternate IPv6 DNS Server', polVars["alternate_ipv6_dns_server"])
                        elif alternate_true == 'N':
                            polVars["alternate_ipv6_dns_server"] = ''
                            valid = True
                        else: ezfunctions.message_invalid_y_or_n('short')
                    else:
                        polVars["alternate_ipv6_dns_server"] = ''
                        valid = True

                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(textwrap.indent(yaml.dump(polVars, Dumper=MyDumper, default_flow_style=False), ' '*4, predicate=None))
                print(f'-------------------------------------------------------------------------------------------\n')
                valid_confirm = False
                while valid_confirm == False:
                    confirm_policy = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                    if confirm_policy == 'Y' or confirm_policy == '':
                        confirm_policy = 'Y'

                        # Write Policies to Template File
                        polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                        ezfunctions.write_to_template(self, **kwargs)

                        configure_loop, policy_loop = ezfunctions.exit_default(policy_type, 'N')
                        valid_confirm = True
                    elif confirm_policy == 'N':
                        ezfunctions.message_starting_over(policy_type)
                        valid_confirm = True
                    else: ezfunctions.message_invalid_y_or_n('long')
        # Return kwargs
        return kwargs

    #==============================================
    # NTP Policy Module
    #==============================================
    def ntp_policies(self, **kwargs):
        baseRepo    = kwargs['args'].dir
        ezData      = kwargs['ezData']
        jsonData    = kwargs['jsonData']
        name_prefix = self.name_prefix
        name_suffix = 'ntp'
        org         = self.org
        path_sep    = kwargs['path_sep']
        policy_type = 'NTP Policy'
        yaml_file   = 'management'
        polVars = {}

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  It is strongly recommended to configure an NTP Policy for the UCS Domain Profile.')
            print(f'  Without an NTP Policy Events can be incorrectly timestamped and Intersight ')
            print(f'  Communication, as an example, could be interrupted with Certificate Validation\n')
            print(f'  checks, as an example.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - {baseRepo}{path_sep}{org}{path_sep}{self.type}{path_sep}{yaml_file}.yaml')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            policy_loop = False
            while policy_loop == False:

                if not name_prefix == '':
                    name = f'{name_prefix}-{name_suffix}'
                else:
                    name = f'{org}-{name_suffix}'

                polVars['name']        = ezfunctions.policy_name(name, policy_type)
                polVars['description'] = ezfunctions.policy_descr(polVars['name'], policy_type)

                primary_ntp = ezfunctions.ntp_primary()
                alternate_ntp = ezfunctions.ntp_alternate()

                polVars["enabled"] = True
                polVars["ntp_servers"] = []
                polVars["ntp_servers"].append(primary_ntp)
                if not alternate_ntp == '':
                    polVars["ntp_servers"].append(alternate_ntp)

                polVars["multi_select"] = False
                jsonVars = jsonData['appliance.SystemInfo']['allOf'][1]['properties']['TimeZone']['enum']
                tz_regions = []
                for i in jsonVars:
                    tz_region = i.split('/')[0]
                    if not tz_region in tz_regions:
                        tz_regions.append(tz_region)
                tz_regions = sorted(tz_regions)
                polVars['description'] = 'Timezone Regions...'
                polVars["jsonVars"] = tz_regions
                polVars["defaultVar"] = 'America'
                polVars["varType"] = 'Time Region'
                time_region = ezfunctions.variablesFromAPI(**kwargs)

                region_tzs = []
                for item in jsonVars:
                    if time_region in item:
                        region_tzs.append(item)

                polVars['description'] = 'Region Timezones...'
                polVars["jsonVars"] = sorted(region_tzs)
                polVars["defaultVar"] = ''
                polVars["varType"] = 'Region Timezones'
                polVars["timezone"] = ezfunctions.variablesFromAPI(**kwargs)

                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(textwrap.indent(yaml.dump(polVars, Dumper=MyDumper, default_flow_style=False), ' '*4, predicate=None))
                print(f'-------------------------------------------------------------------------------------------\n')
                valid_confirm = False
                while valid_confirm == False:
                    confirm_policy = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                    if confirm_policy == 'Y' or confirm_policy == '':
                        confirm_policy = 'Y'

                        # Write Policies to Template File
                        polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                        ezfunctions.write_to_template(self, **kwargs)

                        configure_loop, policy_loop = ezfunctions.exit_default(policy_type, 'N')
                        valid_confirm = True
                    elif confirm_policy == 'N':
                        ezfunctions.message_starting_over(policy_type)
                        valid_confirm = True
                    else: ezfunctions.message_invalid_y_or_n('long')
        # Return kwargs
        return kwargs

    #==============================================
    # Persistent Memory Policy Module
    #==============================================
    def persistent_memory_policies(self, **kwargs):
        baseRepo    = kwargs['args'].dir
        ezData      = kwargs['ezData']
        jsonData    = kwargs['jsonData']
        name_prefix = self.name_prefix
        name_suffix = 'pmem'
        org         = self.org
        path_sep    = kwargs['path_sep']
        policy_type = 'Persistent Memory Policy'
        yaml_file   = 'compute'
        polVars = {}

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  A {policy_type} allows the configuration of security, Goals, and ')
            print(f'  Namespaces of Persistent Memory Modules:')
            print(f'  - Goal - Used to configure volatile memory and regions in all the PMem Modules connected ')
            print(f'    to all the sockets of the server. Intersight supports only the creation and modification')
            print(f'    of a Goal as part of the Persistent Memory policy. Some data loss occurs when a Goal is')
            print(f'    modified during the creation or modification of a Persistent Memory Policy.')
            print(f'  - Namespaces - Used to partition a region mapped to a specific socket or a PMem Module on a')
            print(f'    socket.  Intersight supports only the creation and deletion of Namespaces as part of the ')
            print(f'    Persistent Memory Policy. Modifying a Namespace is not supported. Some data loss occurs ')
            print(f'    when a Namespace is created or deleted during the creation of a Persistent Memory policy.')
            print(f'    It is important to consider the memory performance guidelines and population rules of ')
            print(f'    the Persistent Memory Modules before they are installed or replaced, and the policy is ')
            print(f'    deployed. The population guidelines for the PMem Modules can be divided into the  ')
            print(f'    following categories, based on the number of CPU sockets:')
            print(f'    * Dual CPU for UCS B200 M6, C220 M6, C240 M6, and xC210 M6 servers')
            print(f'    * Dual CPU for UCS C220 M5, C240 M5, and B200 M5 servers')
            print(f'    * Dual CPU for UCS S3260 M5 servers')
            print(f'    * Quad CPU for UCS C480 M5 and B480 M5 servers')
            print(f'  - Security - Used to configure the secure passphrase for all the persistent memory modules.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - {baseRepo}{path_sep}{org}{path_sep}{self.type}{path_sep}{yaml_file}.yaml')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure a {policy_type}?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                policy_loop = False
                while policy_loop == False:

                    if not name_prefix == '': name = f'{name_prefix}-{name_suffix}'
                    else: name = f'{org}-{name_suffix}'

                    polVars['name']        = ezfunctions.policy_name(name, policy_type)
                    polVars['description'] = ezfunctions.policy_descr(polVars['name'], policy_type)

                    polVars["multi_select"] = False
                    jsonVars = jsonData['memory.PersistentMemoryPolicy']['allOf'][1]['properties']
                    polVars['description'] = jsonVars['ManagementMode']['description']
                    polVars["jsonVars"] = sorted(jsonVars['ManagementMode']['enum'])
                    polVars["defaultVar"] = jsonVars['ManagementMode']['default']
                    polVars["varType"] = 'Management Mode'
                    polVars["management_mode"] = ezfunctions.variablesFromAPI(**kwargs)

                    if polVars["management_mode"] == 'configured-from-intersight':
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        print(f'  A Secure passphrase will enable the protection of data on the persistent memory modules. ')
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        valid = False
                        while valid == False:
                            encrypt_memory = input('Do you want to enable a secure passphrase?  Enter "Y" or "N" [Y]: ')
                            if encrypt_memory == 'Y' or encrypt_memory == '':
                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                print(f'  The Passphrase must be between 8 and 32 characters in length.  The allowed characters are:')
                                print(f'   - a-z, A-Z, 0-9 and special characters: \u0021, &, #, $, %, +, ^, @, _, *, -.')
                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                valid_passphrase = False
                                while valid_passphrase == False:
                                    secure_passphrase = stdiomask.getpass(prompt='Enter the Secure Passphrase: ')
                                    polVars["minLength"] = 8
                                    polVars["maxLength"] = 32
                                    polVars["rePattern"] = '^[a-zA-Z0-9\\u0021\\&\\#\\$\\%\\+\\%\\@\\_\\*\\-\\.]+$'
                                    polVars["varName"] = 'Secure Passphrase'
                                    varValue = secure_passphrase
                                    valid_passphrase = validating.length_and_regex_sensitive(polVars["rePattern"],
                                        polVars["varName"],
                                        varValue,
                                        polVars["minLength"],
                                        polVars["maxLength"]
                                    )

                                os.environ['TF_VAR_secure_passphrase'] = '%s' % (secure_passphrase)
                                valid = True
                            else:
                                valid = True

                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        print(f'  The percentage of volatile memory required for goal creation.')
                        print(f'  The actual volatile and persistent memory size allocated to the region may differ with')
                        print(f'  the given percentage.')
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        valid = False
                        while valid == False:
                            polVars["memory_mode_percentage"] = input('What is the Percentage of Valatile Memory to assign to this Policy?  [0]: ')
                            if polVars["memory_mode_percentage"] == '':
                                polVars["memory_mode_percentage"] = 0
                            if re.search(r'[\d]+', str(polVars["memory_mode_percentage"])):
                                valid = validating.number_in_range('Memory Mode Percentage', polVars["memory_mode_percentage"], 1, 100)
                            else:
                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                print(f'  "{polVars["memory_mode_percentage"]}" is not a valid number.')
                                print(f'\n-------------------------------------------------------------------------------------------\n')

                        jsonVars = jsonData['memory.PersistentMemoryGoal']['allOf'][1]['properties']
                        polVars['description'] = jsonVars['PersistentMemoryType']['description']
                        polVars["jsonVars"] = sorted(jsonVars['PersistentMemoryType']['enum'])
                        polVars["defaultVar"] = jsonVars['PersistentMemoryType']['default']
                        polVars["varType"] = 'Persistent Memory Type'
                        polVars["persistent_memory_type"] = ezfunctions.variablesFromAPI(**kwargs)

                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        print(f'  This Flag will enable or Disable the retention of Namespaces between Server Profile')
                        print(f'  association and dissassociation.')
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        valid = False
                        while valid == False:
                            polVars["retain_namespaces"] = input('Do you want to Retain Namespaces?  Enter "Y" or "N" [Y]: ')
                            if polVars["retain_namespaces"] == '' or polVars["retain_namespaces"] == 'Y':
                                polVars["retain_namespaces"] = True
                                valid = True
                            elif polVars["retain_namespaces"] == 'N':
                                polVars["retain_namespaces"] = False
                                valid = True
                            else: ezfunctions.message_invalid_y_or_n('short')

                        polVars["namespaces"] = []
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        print(f'  Namespace is a partition made in one or more Persistent Memory Regions. You can create a')
                        print(f'  namespace in Raw or Block mode.')
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        namespace_configure = input(f'Do You Want to Configure a namespace?  Enter "Y" or "N" [Y]: ')
                        if namespace_configure == 'Y' or namespace_configure == '':
                            sub_loop = False
                            while sub_loop == False:
                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                print(f'  Name of this Namespace to be created on the server.')
                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                valid = False
                                while valid == False:
                                    namespace_name = input('What is the Name for this Namespace? ')
                                    polVars["minLength"] = 1
                                    polVars["maxLength"] = 63
                                    polVars["rePattern"] = '^[a-zA-Z0-9\\#\\_\\-]+$'
                                    polVars["varName"] = 'Name for the Namespace'
                                    varValue = namespace_name
                                    valid = validating.length_and_regex(polVars["rePattern"], polVars["varName"], varValue, polVars["minLength"], polVars["maxLength"])

                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                print(f'  Capacity of this Namespace in gibibytes (GiB).  Range is 1-9223372036854775807')
                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                valid = False
                                while valid == False:
                                    capacity = input('What is the Capacity to assign to this Namespace? ')
                                    polVars["minNum"] = 1
                                    polVars["maxNum"] = 9223372036854775807
                                    polVars["varName"] = 'Namespace Capacity'
                                    varValue = int(capacity)
                                    if re.search(r'[\d]+',str(varValue)):
                                        valid = validating.number_in_range(polVars["varName"], varValue, polVars["minNum"], polVars["maxNum"])
                                    else:
                                        print(f'\n-------------------------------------------------------------------------------------------\n')
                                        print(f'  "{varValue}" is not a valid number.')
                                        print(f'\n-------------------------------------------------------------------------------------------\n')

                                jsonVars = jsonData['memory.PersistentMemoryLogicalNamespace']['allOf'][1]['properties']
                                polVars['description'] = jsonVars['Mode']['description']
                                polVars["jsonVars"] = sorted(jsonVars['Mode']['enum'])
                                polVars["defaultVar"] = jsonVars['Mode']['default']
                                polVars["varType"] = 'Mode'
                                mode = ezfunctions.variablesFromAPI(**kwargs)

                                polVars['description'] = jsonVars['SocketId']['description']
                                polVars["jsonVars"] = sorted(jsonVars['SocketId']['enum'])
                                polVars["defaultVar"] = jsonVars['SocketId']['default']
                                polVars["varType"] = 'Socket Id'
                                socket_id = ezfunctions.variablesFromAPI(**kwargs)

                                if polVars["persistent_memory_type"] == 'app-direct-non-interleaved':
                                    polVars['description'] = jsonVars['SocketMemoryId']['description']
                                    polVars["jsonVars"] = [x for x in jsonVars['SocketMemoryId']['enum']]
                                    polVars["defaultVar"] = '2'
                                    polVars["popList"] = ['Not Applicable']
                                    polVars["varType"] = 'Socket Memory Id'
                                    socket_memory_id = ezfunctions.variablesFromAPI(**kwargs)
                                else:
                                    socket_memory_id = 'Not Applicable'

                                namespace = {
                                    'capacity':capacity,
                                    'mode':mode,
                                    'name':namespace_name,
                                    'socket_id':socket_id,
                                    'socket_memory_id':socket_memory_id
                                }
                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                print(f'   capacity         = "{capacity}"')
                                print(f'   mode             = "{mode}"')
                                print(f'   name             = "{namespace_name}"')
                                print(f'   socket_id        = "{socket_id}"')
                                print(f'   socket_memory_id = "{socket_memory_id}"')
                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                valid_confirm = False
                                while valid_confirm == False:
                                    confirm_namespace = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                                    if confirm_namespace == 'Y' or confirm_namespace == '':
                                        polVars["namespaces"].append(namespace)

                                        valid_exit = False
                                        while valid_exit == False:
                                            sub_exit = input(f'Would You like to Configure another namespace?  Enter "Y" or "N" [N]: ')
                                            if sub_exit == 'Y':
                                                valid_confirm = True
                                                valid_exit = True
                                            elif sub_exit == 'N' or sub_exit == '':
                                                sub_loop = True
                                                valid = True
                                                valid_confirm = True
                                                valid_exit = True
                                            else: ezfunctions.message_invalid_y_or_n('short')

                                    elif confirm_namespace == 'N':
                                        print(f'\n-------------------------------------------------------------------------------------------\n')
                                        print(f'  Starting namespace Configuration Over.')
                                        print(f'\n-------------------------------------------------------------------------------------------\n')
                                        valid_confirm = True
                                    else: ezfunctions.message_invalid_y_or_n('short')

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(textwrap.indent(yaml.dump(polVars, Dumper=MyDumper, default_flow_style=False), ' '*4, predicate=None))
                    print(f'-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
                        if confirm_policy == 'Y' or confirm_policy == '':
                            confirm_policy = 'Y'

                            # Write Policies to Template File
                            polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                            ezfunctions.write_to_template(self, **kwargs)

                            configure_loop, policy_loop = ezfunctions.exit_default(policy_type, 'N')
                            valid_confirm = True
                        elif confirm_policy == 'N':
                            ezfunctions.message_starting_over(policy_type)
                            valid_confirm = True
                        else: ezfunctions.message_invalid_y_or_n('short')
            elif configure == 'N': configure_loop = True
            else: ezfunctions.message_invalid_y_or_n('long')
        # Return kwargs
        return kwargs

    #==============================================
    # Port Policy Module
    #==============================================
    def port_policies(self, **kwargs):
        baseRepo    = kwargs['args'].dir
        ezData      = kwargs['ezData']
        jsonData    = kwargs['jsonData']
        name_prefix = self.name_prefix
        org         = self.org
        path_sep    = kwargs['path_sep']
        policy_type = 'Port Policy'
        yaml_file   = 'port'
        polVars = {}

        port_count = 0
        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  A {policy_type} is used to configure the ports for a UCS Domain Profile.  This includes:')
            print(f'   - Unified Ports - Ports to convert to Fibre-Channel Mode.')
            print(f'   - Appliance Ports')
            print(f'   - Appliance Port-Channels')
            print(f'   - Ethernet Uplinks')
            print(f'   - Ethernet Uplink Port-Channels')
            print(f'   - FCoE Uplinks')
            print(f'   - FCoE Uplink Port-Channels')
            print(f'   - Fibre-Channel Storage')
            print(f'   - Fibre-Channel Uplinks')
            print(f'   - Fibre-Channel Uplink Port-Channels')
            print(f'   - Server Ports\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - {baseRepo}{path_sep}{org}{path_sep}{self.type}{path_sep}{yaml_file}.yaml')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            policy_loop = False
            while policy_loop == False:

                print(f'   IMPORTANT NOTE: The wizard will create a Port Policy for Fabric A and Fabric B')
                print(f'                   automatically.  The Policy Name will be appended with [name]_A for ')
                print(f'                   Fabric A and [name]_B for Fabric B.  You only need one Policy per')
                print(f'                   Domain.')
                print(f'\n-------------------------------------------------------------------------------------------\n')

                if not name_prefix == '':
                    name = '%s' % (name_prefix)
                else:
                    name = '%s' % (org)

                polVars['name']        = ezfunctions.policy_name(name, policy_type)
                polVars['description'] = ezfunctions.policy_descr(polVars['name'], policy_type)

                polVars["multi_select"] = False
                jsonVars = jsonData['fabric.PortPolicy']['allOf'][1]['properties']
                polVars['description'] = jsonVars['DeviceModel']['description']
                polVars["jsonVars"] = sorted(jsonVars['DeviceModel']['enum'])
                polVars["defaultVar"] = jsonVars['DeviceModel']['default']
                polVars["varType"] = 'Device Model'
                polVars["device_model"] = ezfunctions.variablesFromAPI(**kwargs)
                
                fc_mode,ports_in_use,fc_converted_ports,port_modes = port_modes_fc(jsonData, ezData, name_prefix, **kwargs)
                polVars["fc_mode"] = fc_mode
                polVars["ports_in_use"] = ports_in_use
                polVars["fc_converted_ports"] = fc_converted_ports
                polVars["port_modes"] = port_modes
                polVars["fc_ports"] = polVars["port_modes"]["port_list"]

                # Appliance Port-Channel
                polVars['port_type'] = 'Appliance Port-Channel'
                port_channel_appliances,polVars['ports_in_use'] = port_list_eth(jsonData, ezData, name_prefix, **kwargs)

                # Ethernet Uplink Port-Channel
                polVars['port_type'] = 'Ethernet Uplink Port-Channel'
                port_channel_ethernet_uplinks,polVars['ports_in_use'] = port_list_eth(jsonData, ezData, name_prefix, **kwargs)

                # Fibre-Channel Port-Channel
                polVars["fc_ports_in_use"] = []
                polVars["port_type"] = 'Fibre-Channel Port-Channel'
                Fab_A,Fab_B,fc_ports_in_use = port_list_fc(jsonData, ezData, name_prefix, **kwargs)
                Fabric_A_fc_port_channels = Fab_A
                Fabric_B_fc_port_channels = Fab_B
                polVars["fc_ports_in_use"] = fc_ports_in_use

                # FCoE Uplink Port-Channel
                polVars['port_type'] = 'FCoE Uplink Port-Channel'
                port_channel_fcoe_uplinks,polVars['ports_in_use'] = port_list_eth(jsonData, ezData, name_prefix, **kwargs)

                # Appliance Ports
                polVars['port_type'] = 'Appliance Ports'
                port_role_appliances,polVars['ports_in_use'] = port_list_eth(jsonData, ezData, name_prefix, **kwargs)

                # Ethernet Uplink
                polVars['port_type'] = 'Ethernet Uplink'
                port_role_ethernet_uplinks,polVars['ports_in_use'] = port_list_eth(jsonData, ezData, name_prefix, **kwargs)

                # Fibre-Channel Storage
                polVars["port_type"] = 'Fibre-Channel Storage'
                Fab_A,Fab_B,fc_ports_in_use = port_list_fc(jsonData, ezData, name_prefix, **kwargs)
                Fabric_A_port_role_fc_storage = Fab_A
                Fabric_B_port_role_fc_storage = Fab_B
                polVars["fc_ports_in_use"] = fc_ports_in_use

                # Fibre-Channel Uplink
                polVars["port_type"] = 'Fibre-Channel Uplink'
                Fab_A,Fab_B,fc_ports_in_use = port_list_fc(jsonData, ezData, name_prefix, **kwargs)
                Fabric_A_port_role_fc_uplink = Fab_A
                Fabric_B_port_role_fc_uplink = Fab_B
                polVars["fc_ports_in_use"] = fc_ports_in_use

                # FCoE Uplink
                polVars['port_type'] = 'FCoE Uplink'
                port_role_fcoe_uplinks,polVars['ports_in_use'] = port_list_eth(jsonData, ezData, name_prefix, **kwargs)

                # Server Ports
                polVars['port_type'] = 'Server Ports'
                port_role_servers,polVars['ports_in_use'] = port_list_eth(jsonData, ezData, name_prefix, **kwargs)

                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(textwrap.indent(yaml.dump(polVars, Dumper=MyDumper, default_flow_style=False), ' '*4, predicate=None))
                print(f'-------------------------------------------------------------------------------------------\n')
                valid_confirm = False
                while valid_confirm == False:
                    confirm_policy = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                    if confirm_policy == 'Y' or confirm_policy == '':
                        confirm_policy = 'Y'

                        polVars["port_channel_appliances"] = port_channel_appliances
                        polVars["port_channel_ethernet_uplinks"] = port_channel_ethernet_uplinks
                        polVars["port_channel_fcoe_uplinks"] = port_channel_fcoe_uplinks
                        polVars["port_role_appliances"] = port_role_appliances
                        polVars["port_role_ethernet_uplinks"] = port_role_ethernet_uplinks
                        polVars["port_role_fcoe_uplinks"] = port_role_fcoe_uplinks
                        polVars["port_role_servers"] = port_role_servers

                        original_name = polVars['name']
                        polVars['name']        = '%s_A' % (original_name)
                        polVars["port_channel_fc_uplinks"] = Fabric_A_fc_port_channels
                        polVars["port_role_fc_storage"] = Fabric_A_port_role_fc_storage
                        polVars["port_role_fc_uplinks"] = Fabric_A_port_role_fc_uplink

                        # Write Policies to Template File
                        polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                        ezfunctions.write_to_template(self, **kwargs)

                        polVars['name']        = '%s_B' % (original_name)
                        polVars["port_channel_fc_uplinks"] = Fabric_B_fc_port_channels
                        polVars["port_role_fc_storage"] = Fabric_B_port_role_fc_storage
                        polVars["port_role_fc_uplinks"] = Fabric_B_port_role_fc_uplink

                        # Write Policies to Template File
                        polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                        ezfunctions.write_to_template(self, **kwargs)

                        configure_loop, policy_loop = ezfunctions.exit_default(policy_type, 'N')
                        valid_confirm = True
                    elif confirm_policy == 'N':
                        ezfunctions.message_starting_over(policy_type)
                        valid_confirm = True
                    else: ezfunctions.message_invalid_y_or_n('long')
        # Return kwargs
        return kwargs

    #==============================================
    # Power Policy Module
    #==============================================
    def power_policies(self, **kwargs):
        baseRepo    = kwargs['args'].dir
        ezData      = kwargs['ezData']
        jsonData    = kwargs['jsonData']
        name_prefix = self.name_prefix
        org         = self.org
        path_sep    = kwargs['path_sep']
        policy_type = 'Power Policy'
        yaml_file   = 'environment'
        polVars = {}

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  A {policy_type} will configure the Power Redundancy Policies for Chassis and Servers.')
            print(f'  For Servers it will configure the Power Restore State.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - {baseRepo}{path_sep}{org}{path_sep}{self.type}{path_sep}{yaml_file}.yaml')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            loop_count = 1
            policy_loop = False
            while policy_loop == False:

                print('staring loop again')
                polVars["multi_select"] = False
                polVars['description'] = ezData['policies']['power.Policy']['systemType']['description']
                polVars["jsonVars"] = sorted(ezData['policies']['power.Policy']['systemType']['enum'])
                polVars["defaultVar"] = ezData['policies']['power.Policy']['systemType']['default']
                polVars["varType"] = 'System Type'
                system_type = ezfunctions.variablesFromAPI(**kwargs)

                if not name_prefix == '':
                    name = '%s-%s' % (name_prefix, system_type)
                else:
                    name = '%s-%s' % (org, system_type)

                polVars['name']        = ezfunctions.policy_name(name, policy_type)
                polVars['description'] = ezfunctions.policy_descr(polVars['name'], policy_type)

                polVars["multi_select"] = False
                jsonVars = jsonData['power.Policy']['allOf'][1]['properties']

                if system_type == '9508':
                    valid = False
                    while valid == False:
                        polVars["power_allocation"] = input('What is the Power Budget you would like to Apply?\n'
                            'This should be a value between 2800 Watts and 16800 Watts. [5600]: ')
                        if polVars["power_allocation"] == '':
                            polVars["power_allocation"] = 5600
                        valid = validating.number_in_range('Chassis Power Budget', polVars["power_allocation"], 2800, 16800)

                    polVars['description'] = jsonVars['DynamicRebalancing']['description']
                    polVars["jsonVars"] = sorted(jsonVars['DynamicRebalancing']['enum'])
                    polVars["defaultVar"] = jsonVars['DynamicRebalancing']['default']
                    polVars["varType"] = 'Dynamic Power Rebalancing'
                    polVars["dynamic_power_rebalancing"] = ezfunctions.variablesFromAPI(**kwargs)

                    polVars['description'] = jsonVars['PowerSaveMode']['description']
                    polVars["jsonVars"] = sorted(jsonVars['PowerSaveMode']['enum'])
                    polVars["defaultVar"] = jsonVars['PowerSaveMode']['default']
                    polVars["varType"] = 'Power Save Mode'
                    polVars["power_save_mode"] = ezfunctions.variablesFromAPI(**kwargs)

                else:
                    polVars["power_allocation"] = 0
                    polVars["dynamic_power_rebalancing"] = 'Enabled'
                    polVars["power_save_mode"] = 'Enabled'

                if system_type == 'Server':
                    polVars['description'] = jsonVars['PowerPriority']['description']
                    polVars["jsonVars"] = sorted(jsonVars['PowerPriority']['enum'])
                    polVars["defaultVar"] = jsonVars['PowerPriority']['default']
                    polVars["varType"] = 'Power Priority'
                    polVars["power_priority"] = ezfunctions.variablesFromAPI(**kwargs)

                    polVars['description'] = jsonVars['PowerProfiling']['description']
                    polVars["jsonVars"] = sorted(jsonVars['PowerProfiling']['enum'])
                    polVars["defaultVar"] = jsonVars['PowerProfiling']['default']
                    polVars["varType"] = 'Power Profiling'
                    polVars["power_profiling"] = ezfunctions.variablesFromAPI(**kwargs)

                    polVars['description'] = jsonVars['PowerRestoreState']['description']
                    polVars["jsonVars"] = sorted(jsonVars['PowerRestoreState']['enum'])
                    polVars["defaultVar"] = jsonVars['PowerRestoreState']['default']
                    polVars["varType"] = 'Power Restore'
                    polVars["power_restore"] = ezfunctions.variablesFromAPI(**kwargs)

                if system_type == '5108':
                    polVars["popList"] = ['N+2']
                elif system_type == 'Server':
                    polVars["popList"] = ['N+1','N+2']
                polVars['description'] = jsonVars['RedundancyMode']['description']
                polVars["jsonVars"] = sorted(jsonVars['RedundancyMode']['enum'])
                polVars["defaultVar"] = jsonVars['RedundancyMode']['default']
                polVars["varType"] = 'Power Redundancy Mode'
                polVars["power_redundancy"] = ezfunctions.variablesFromAPI(**kwargs)

                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(textwrap.indent(yaml.dump(polVars, Dumper=MyDumper, default_flow_style=False), ' '*4, predicate=None))
                print(f'-------------------------------------------------------------------------------------------\n')
                valid_confirm = False
                while valid_confirm == False:
                    confirm_policy = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                    if confirm_policy == 'Y' or confirm_policy == '':
                        confirm_policy = 'Y'

                        # Write Policies to Template File
                        polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                        ezfunctions.write_to_template(self, **kwargs)

                        if loop_count < 3:
                            configure_loop, policy_loop = ezfunctions.exit_default(policy_type, 'Y')
                        else:
                            configure_loop, policy_loop = ezfunctions.exit_default(policy_type, 'N')
                        loop_count += 1
                        valid_confirm = True
                    elif confirm_policy == 'N':
                        ezfunctions.message_starting_over(policy_type)
                        valid_confirm = True
                    else: ezfunctions.message_invalid_y_or_n('long')
        # Return kwargs
        return kwargs

    #==============================================
    # SD Card Policy Module
    #==============================================
    def sd_card_policies(self, **kwargs):
        name_prefix = self.name_prefix
        name_suffix = 'sdcard'
        org         = self.org
        policy_type = 'SD Card Policy'
        yaml_file   = 'storage'
        polVars = {}

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure a {policy_type}?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                policy_loop = False
                while policy_loop == False:

                    if not name_prefix == '': name = f'{name_prefix}-{name_suffix}'
                    else: name = f'{org}-{name_suffix}'

                    polVars['name']        = ezfunctions.policy_name(name, policy_type)
                    polVars['description'] = ezfunctions.policy_descr(polVars['name'], policy_type)

                    polVars["priority"] = 'auto'
                    polVars["receive"] = 'Disabled'
                    polVars["send"] = 'Disabled'

                    # Write Policies to Template File
                    polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                    ezfunctions.write_to_template(self, **kwargs)

                    exit_answer = input(f'Would You like to Configure another {policy_type}?  Enter "Y" or "N" [N]: ')
                    if exit_answer == 'N' or exit_answer == '':
                        policy_loop = True
                        configure_loop = True
            elif configure == 'N':
                configure_loop = True
            else: ezfunctions.message_invalid_y_or_n('short')
        # Return kwargs
        return kwargs

    #==============================================
    # Serial over LAN Policy Module
    #==============================================
    def serial_over_lan_policies(self, **kwargs):
        baseRepo    = kwargs['args'].dir
        jsonData    = kwargs['jsonData']
        name_prefix = self.name_prefix
        name_suffix = 'sol'
        org         = self.org
        path_sep    = kwargs['path_sep']
        policy_type = 'Serial over LAN Policy'
        yaml_file   = 'management'
        polVars = {}

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  A {policy_type} will configure the Server to allow access to the Communications Port over')
            print(f'  Ethernet.  Settings include:')
            print(f'   - Baud Rate')
            print(f'   - COM Port')
            print(f'   - SSH Port\n')
            print(f'  This Policy is not required to standup a server but is a good practice for day 2 support.')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - {baseRepo}{path_sep}{org}{path_sep}{self.type}{path_sep}{yaml_file}.yaml')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure a {policy_type}?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                policy_loop = False
                while policy_loop == False:

                    if not name_prefix == '': name = f'{name_prefix}-{name_suffix}'
                    else: name = f'{org}-{name_suffix}'

                    polVars['name']        = ezfunctions.policy_name(name, policy_type)
                    polVars['description'] = ezfunctions.policy_descr(polVars['name'], policy_type)
                    polVars["enabled"] = True

                    polVars["multi_select"] = False
                    jsonVars = jsonData['sol.Policy']['allOf'][1]['properties']
                    polVars['description'] = jsonVars['BaudRate']['description']
                    polVars["jsonVars"] = sorted(jsonVars['BaudRate']['enum'])
                    polVars["defaultVar"] = jsonVars['BaudRate']['default']
                    polVars["varType"] = 'Baud Rate'
                    polVars["baud_rate"] = ezfunctions.variablesFromAPI(**kwargs)

                    polVars['description'] = jsonVars['ComPort']['description']
                    polVars["jsonVars"] = sorted(jsonVars['ComPort']['enum'])
                    polVars["defaultVar"] = jsonVars['ComPort']['default']
                    polVars["varType"] = 'Com Port'
                    polVars["com_port"] = ezfunctions.variablesFromAPI(**kwargs)

                    valid = False
                    while valid == False:
                        polVars["ssh_port"] = input('What is the SSH Port you would like to assign?\n'
                            'This should be a value between 1024-65535. [2400]: ')
                        if polVars["ssh_port"] == '':
                            polVars["ssh_port"] = 2400
                        valid = validating.number_in_range('SSH Port', polVars["ssh_port"], 1024, 65535)

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(textwrap.indent(yaml.dump(polVars, Dumper=MyDumper, default_flow_style=False), ' '*4, predicate=None))
                    print(f'-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                        if confirm_policy == 'Y' or confirm_policy == '':
                            confirm_policy = 'Y'

                            # Write Policies to Template File
                            polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                            ezfunctions.write_to_template(self, **kwargs)

                            configure_loop, policy_loop = ezfunctions.exit_default(policy_type, 'N')
                            valid_confirm = True
                        elif confirm_policy == 'N':
                            ezfunctions.message_starting_over(policy_type)
                            valid_confirm = True
                        else: ezfunctions.message_invalid_y_or_n('short')
            elif configure == 'N': configure_loop = True
            else: ezfunctions.message_invalid_y_or_n('short')
        # Return kwargs
        return kwargs

    #==============================================
    # SMTP Policy Module
    #==============================================
    def smtp_policies(self, **kwargs):
        baseRepo    = kwargs['args'].dir
        jsonData    = kwargs['jsonData']
        name_prefix = self.name_prefix
        name_suffix = 'smtp'
        org         = self.org
        path_sep    = kwargs['path_sep']
        policy_type = 'SMTP Policy'
        yaml_file   = 'management'
        polVars = {}

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  An {policy_type} sends server faults as email alerts to the configured SMTP server.')
            print(f'  You can specify the preferred settings for outgoing communication and select the fault ')
            print(f'  severity level to report and the mail recipients.\n\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - {baseRepo}{path_sep}{org}{path_sep}{self.type}{path_sep}{yaml_file}.yaml')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure an {policy_type}?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                policy_loop = False
                while policy_loop == False:

                    if not name_prefix == '': name = f'{name_prefix}-{name_suffix}'
                    else: name = f'{org}-{name_suffix}'

                    polVars['name']        = ezfunctions.policy_name(name, policy_type)
                    polVars['description'] = ezfunctions.policy_descr(polVars['name'], policy_type)
                    polVars["enable_smtp"] = True

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  IP address or hostname of the SMTP server. The SMTP server is used by the managed device ')
                    print(f'  to send email notifications.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid = False
                    while valid == False:
                        polVars["smtp_server_address"] = input('What is the SMTP Server Address? ')
                        if re.search(r'^[a-zA-Z0-9]:', polVars["smtp_server_address"]):
                            valid = validating.ip_address('SMTP Server Address', polVars["smtp_server_address"])
                        if re.search(r'[a-zA-Z]', polVars["smtp_server_address"]):
                            valid = validating.dns_name('SMTP Server Address', polVars["smtp_server_address"])
                        elif re.search (r'^([0-9]{1,3}\.){3}[0-9]{1,3}$'):
                            valid = validating.ip_address('SMTP Server Address', polVars["smtp_server_address"])
                        else:
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            print(f'  "{polVars["smtp_server_address"]}" is not a valid address.')
                            print(f'\n-------------------------------------------------------------------------------------------\n')

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  Port number used by the SMTP server for outgoing SMTP communication.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid = False
                    while valid == False:
                        polVars["smtp_port"] = input('What is the SMTP Port?  [25]: ')
                        if polVars["smtp_port"] == '':
                            polVars["smtp_port"] = 25
                        if re.search(r'[\d]+', str(polVars["smtp_port"])):
                            valid = validating.number_in_range('SMTP Port', polVars["smtp_port"], 1, 65535)
                        else:
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            print(f'  "{polVars["smtp_port"]}" is not a valid port.')
                            print(f'\n-------------------------------------------------------------------------------------------\n')

                    polVars["multi_select"] = False
                    jsonVars = jsonData['smtp.Policy']['allOf'][1]['properties']
                    polVars['description'] = jsonVars['MinSeverity']['description']
                    polVars["jsonVars"] = sorted(jsonVars['MinSeverity']['enum'])
                    polVars["defaultVar"] = jsonVars['MinSeverity']['default']
                    polVars["varType"] = 'Minimum Severity'
                    polVars["minimum_severity"] = ezfunctions.variablesFromAPI(**kwargs)

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  The email address entered here will be displayed as the from address (mail received from ')
                    print(f'  address) of all the SMTP mail alerts that are received. If not configured, the hostname ')
                    print(f'  of the server is used in the from address field.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid = False
                    while valid == False:
                        polVars["smtp_alert_sender_address"] = input(f'What is the SMTP Alert Sender Address?  '\
                            '[press enter to use server hostname]: ')
                        if polVars["smtp_alert_sender_address"] == '':
                            polVars["smtp_alert_sender_address"] = ''
                            valid = True
                        else:
                            valid = validating.email('SMTP Alert Sender Address', polVars["smtp_alert_sender_address"])

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  List of email addresses that will receive notifications for faults.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    polVars["mail_alert_recipients"] = []
                    valid = False
                    while valid == False:
                        mail_recipient = input(f'What is address you would like to send these notifications to?  ')
                        valid_email = validating.email('Mail Alert Recipient', mail_recipient)
                        if valid_email == True:
                            polVars["mail_alert_recipients"].append(mail_recipient)
                            valid_answer = False
                            while valid_answer == False:
                                add_another = input(f'Would you like to add another E-mail?  Enter "Y" or "N" [N]: ')
                                if add_another == '' or add_another == 'N':
                                    valid = True
                                    valid_answer = True
                                elif add_another == 'Y':
                                    valid_answer = True
                                else: ezfunctions.message_invalid_y_or_n('short')

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(textwrap.indent(yaml.dump(polVars, Dumper=MyDumper, default_flow_style=False), ' '*4, predicate=None))
                    print(f'-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
                        if confirm_policy == 'Y' or confirm_policy == '':
                            confirm_policy = 'Y'

                            # Write Policies to Template File
                            polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                            ezfunctions.write_to_template(self, **kwargs)

                            configure_loop, policy_loop = ezfunctions.exit_default(policy_type, 'N')
                            valid_confirm = True
                        elif confirm_policy == 'N':
                            ezfunctions.message_starting_over(policy_type)
                            valid_confirm = True
                        else: ezfunctions.message_invalid_y_or_n('short')
            elif configure == 'N': configure_loop = True
            else: ezfunctions.message_invalid_y_or_n('long')
        # Return kwargs
        return kwargs

    #==============================================
    # SNMP Policy Module
    #==============================================
    def snmp_policies(self, **kwargs):
        baseRepo    = kwargs['args'].dir
        jsonData    = kwargs['jsonData']
        name_prefix = self.name_prefix
        name_suffix = 'snmp'
        org         = self.org
        path_sep    = kwargs['path_sep']
        policy_type = 'SNMP Policy'
        yaml_file   = 'management'
        polVars = {}

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  An {policy_type} will configure chassis, domains, and servers with SNMP parameters.')
            print(f'  This Policy is not required to standup a server but is a good practice for day 2 support.')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - {baseRepo}{path_sep}{org}{path_sep}{self.type}{path_sep}{yaml_file}.yaml')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure an {policy_type}?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                loop_count = 1
                policy_loop = False
                while policy_loop == False:

                    if not name_prefix == '': name = f'{name_prefix}-{name_suffix}'
                    else: name = f'{org}-{name_suffix}'

                    polVars['name']        = ezfunctions.policy_name(name, policy_type)
                    polVars['description'] = ezfunctions.policy_descr(polVars['name'], policy_type)
                    polVars["enabled"] = True

                    valid = False
                    while valid == False:
                        polVars["port"] = input(f'Note: The following Ports cannot be chosen: [22, 23, 80, 123, 389, 443, 623, 636, 2068, 3268, 3269]\n'\
                            'Enter the Port to Assign to this SNMP Policy.  Valid Range is 1-65535.  [161]: ')
                        if polVars["port"] == '':
                            polVars["port"] = 161
                        if re.search(r'[0-9]{1,4}', str(polVars["port"])):
                            valid = validating.snmp_port('SNMP Port', polVars["port"], 1, 65535)
                        else:
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            print(f'  Invalid Entry!  Please Enter a valid Port in the range of 1-65535.')
                            print(f'  Excluding [22, 23, 80, 123, 389, 443, 623, 636, 2068, 3268, 3269].')
                            print(f'\n-------------------------------------------------------------------------------------------\n')

                    polVars["multi_select"] = False
                    jsonVars = jsonData['snmp.Policy']['allOf'][1]['properties']

                    # SNMP Contact
                    polVars['description'] = jsonVars['SysContact']['description']
                    polVars["varDefault"] = 'UCS Admins'
                    polVars["varInput"] = 'SNMP System Contact:'
                    polVars["varName"] = 'SNMP System Contact'
                    polVars["varRegex"] = '.*'
                    polVars["minLength"] = 1
                    polVars["maxLength"] = jsonVars['SysContact']['maxLength']
                    polVars["system_contact"] = ezfunctions.varStringLoop(**kwargs)

                    # SNMP Location
                    polVars['description'] = jsonVars['SysLocation']['description']
                    polVars["varDefault"] = 'Data Center'
                    polVars["varInput"] = 'What is the Location of the host on which the SNMP agent (server) runs?'
                    polVars["varName"] = 'System Location'
                    polVars["varRegex"] = '.*'
                    polVars["minLength"] = 1
                    polVars["maxLength"] = jsonVars['SysLocation']['maxLength']
                    polVars["system_location"] = ezfunctions.varStringLoop(**kwargs)

                    polVars["access_community_string"] = ''
                    valid = False
                    while valid == False:
                        question = input(f'Would you like to configure an SNMP Access Community String?  Enter "Y" or "N" [N]: ')
                        if question == 'Y':
                            input_valid = False
                            while input_valid == False:
                                input_string = stdiomask.getpass(f'What is your SNMP Access Community String? ')
                                if not input_string == '':
                                    input_valid = validating.snmp_string('SNMP Access Community String', input_string)
                                else:
                                    print(f'\n-------------------------------------------------------------------------------------------\n')
                                    print(f'  Error!! Invalid Value.  Please Re-enter the SNMP Access Community String.')
                                    print(f'\n-------------------------------------------------------------------------------------------\n')
                            polVars["access_community_string"] = loop_count
                            TF_VAR = 'TF_VAR_access_community_string_%s' % (loop_count)
                            os.environ[TF_VAR] = '%s' % (input_string)
                            valid = True
                        elif question == '' or question == 'N':
                            valid = True
                        else: ezfunctions.message_invalid_y_or_n('short')

                    if not polVars["access_community_string"] == '':
                        polVars['description'] = jsonVars['CommunityAccess']['description']
                        polVars["jsonVars"] = sorted(jsonVars['CommunityAccess']['enum'])
                        polVars["defaultVar"] = jsonVars['CommunityAccess']['default']
                        polVars["varType"] = 'Community Access'
                        polVars["community_access"] = ezfunctions.variablesFromAPI(**kwargs)
                    else:
                        polVars["community_access"] = 'Disabled'

                    polVars["trap_community_string"] = ''
                    valid = False
                    while valid == False:
                        question = input(f'Would you like to configure an SNMP Trap Community String?  Enter "Y" or "N" [N]: ')
                        if question == 'Y':
                            input_valid = False
                            while input_valid == False:
                                input_string = stdiomask.getpass(f'What is your SNMP Trap Community String? ')
                                if not input_string == '':
                                    input_valid = validating.snmp_string('SNMP Trap Community String', input_string)
                                else:
                                    print(f'\n-------------------------------------------------------------------------------------------\n')
                                    print(f'  Error!! Invalid Value.  Please Re-enter the SNMP Trap Community String.')
                                    print(f'\n-------------------------------------------------------------------------------------------\n')
                            polVars["trap_community_string"] = loop_count
                            TF_VAR = 'TF_VAR_snmp_trap_community_%s' % (loop_count)
                            os.environ[TF_VAR] = '%s' % (input_string)
                            valid = True
                        elif question == '' or question == 'N':
                            valid = True
                        else: ezfunctions.message_invalid_y_or_n('short')

                    polVars["engine_input_id"] = ''
                    valid = False
                    while valid == False:
                        question = input(f'Note: By default this is derived from the BMC serial number.\n'\
                            'Would you like to configure a Unique string to identify the device for administration purpose?  Enter "Y" or "N" [N]: ')
                        if question == 'Y':
                            input_valid = False
                            while input_valid == False:
                                input_string = input(f'What is the SNMP Engine Input ID? ')
                                if not input_string == '':
                                    input_valid = validating.string_length('SNMP Engine Input ID', input_string, 1, 27)
                                else:
                                    print(f'\n-------------------------------------------------------------------------------------------\n')
                                    print(f'  Error!! Invalid Value.  Please Re-enter the SNMP Engine Input ID.')
                                    print(f'\n-------------------------------------------------------------------------------------------\n')
                            polVars["snmp_engine_input_id"] = input_string
                            valid = True
                        elif question == '' or question == 'N':
                            valid = True
                        else: ezfunctions.message_invalid_y_or_n('short')

                    # SNMP Users
                    ilCount = 1
                    snmp_user_list = []
                    polVars['description'] = 'Configure SNMP Users'
                    polVars["varInput"] = f'Would you like to configure an SNMPv3 User?'
                    polVars["varDefault"] = 'Y'
                    polVars["varName"] = 'Enable Trunking'
                    configure_snmp_users = ezfunctions.varBoolLoop(**kwargs)
                    if configure_snmp_users == True:
                        snmp_loop = False
                        while snmp_loop == False:
                            snmp_user_list,snmp_loop = ezfunctions.snmp_users(jsonData, ilCount, **kwargs)

                    # SNMP Trap Destinations
                    ilCount = 1
                    snmp_dests = []
                    snmp_loop = False
                    while snmp_loop == False:
                        question = input(f'Would you like to configure SNMP Trap Destionations?  Enter "Y" or "N" [Y]: ')
                        if question == '' or question == 'Y':
                            snmp_dests,snmp_loop = ezfunctions.snmp_trap_servers(jsonData, ilCount, snmp_user_list, **kwargs)
                        elif question == 'N':
                            snmp_loop = True
                        else: ezfunctions.message_invalid_y_or_n('short')
                    polVars["trap_destinations"] = snmp_dests

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(textwrap.indent(yaml.dump(polVars, Dumper=MyDumper, default_flow_style=False), ' '*4, predicate=None))
                    print(f'-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                        if confirm_policy == 'Y' or confirm_policy == '':
                            confirm_policy = 'Y'

                            # Write Policies to Template File
                            polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                            ezfunctions.write_to_template(self, **kwargs)

                            configure_loop, policy_loop = ezfunctions.exit_default(policy_type, 'N')
                            valid_confirm = True
                        elif confirm_policy == 'N':
                            ezfunctions.message_starting_over(policy_type)
                            valid_confirm = True
                        else: ezfunctions.message_invalid_y_or_n('short')
            elif configure == 'N': configure_loop = True
            else: ezfunctions.message_invalid_y_or_n('long')
        # Return kwargs
        return kwargs

    #==============================================
    # SSH Policy Module
    #==============================================
    def ssh_policies(self, **kwargs):
        baseRepo    = kwargs['args'].dir
        ezData      = kwargs['ezData']
        jsonData    = kwargs['jsonData']
        name_prefix = self.name_prefix
        name_suffix = 'ssh'
        org         = self.org
        path_sep    = kwargs['path_sep']
        policy_type = 'SSH Policy'
        yaml_file   = 'storage'
        polVars = {}

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  An {policy_type} enables an SSH client to make a secure, encrypted connection. You can ')
            print(f'  create one or more SSH policies that contain a specific grouping of SSH properties for a ')
            print(f'  server or a set of servers.\n\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - {baseRepo}{path_sep}{org}{path_sep}{self.type}{path_sep}{yaml_file}.yaml')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure an {policy_type}?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                policy_loop = False
                while policy_loop == False:

                    if not name_prefix == '': name = f'{name_prefix}-{name_suffix}'
                    else: name = f'{org}-{name_suffix}'

                    polVars['name']        = ezfunctions.policy_name(name, policy_type)
                    polVars['description'] = ezfunctions.policy_descr(polVars['name'], policy_type)
                    polVars["enable_ssh"] = True

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  Port used for secure shell access.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid = False
                    while valid == False:
                        polVars["ssh_port"] = input('What is the SSH Port?  [22]: ')
                        if polVars["ssh_port"] == '':
                            polVars["ssh_port"] = 22
                        if re.search(r'[\d]+', str(polVars["ssh_port"])):
                            valid = validating.number_in_range('SSH Port', polVars["ssh_port"], 1, 65535)
                        else:
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            print(f'  "{polVars["ssh_port"]}" is not a valid port.')
                            print(f'\n-------------------------------------------------------------------------------------------\n')

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  Number of seconds to wait before the system considers an SSH request to have timed out.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid = False
                    while valid == False:
                        polVars["ssh_timeout"] = input('What value do you want to set for the SSH Timeout?  [1800]: ')
                        if polVars["ssh_timeout"] == '':
                            polVars["ssh_timeout"] = 1800
                        if re.search(r'[\d]+', str(polVars["ssh_timeout"])):
                            valid = validating.number_in_range('SSH Timeout', polVars["ssh_timeout"], 60, 10800)
                        else:
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            print(f'  "{polVars["ssh_timeout"]}" is not a valid value.  Must be between 60 and 10800')
                            print(f'\n-------------------------------------------------------------------------------------------\n')


                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(textwrap.indent(yaml.dump(polVars, Dumper=MyDumper, default_flow_style=False), ' '*4, predicate=None))
                    print(f'-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
                        if confirm_policy == 'Y' or confirm_policy == '':
                            confirm_policy = 'Y'

                            # Write Policies to Template File
                            polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                            ezfunctions.write_to_template(self, **kwargs)

                            configure_loop, policy_loop = ezfunctions.exit_default(policy_type, 'N')
                            valid_confirm = True

                        elif confirm_policy == 'N':
                            ezfunctions.message_starting_over(policy_type)
                            valid_confirm = True
                        else: ezfunctions.message_invalid_y_or_n('short')
            elif configure == 'N': configure_loop = True
            else: ezfunctions.message_invalid_y_or_n('long')
        # Return kwargs
        return kwargs

    #========================================
    # Storage Policy Module
    #========================================
    def storage_policies(self, **kwargs):
        baseRepo    = kwargs['args'].dir
        ezData      = kwargs['ezData']
        jsonData    = kwargs['jsonData']
        name_prefix = self.name_prefix
        name_suffix = 'storage'
        org         = self.org
        path_sep    = kwargs['path_sep']
        policy_type = 'Storage Policy'
        yaml_file   = 'storage'
        policy_names = []
        polVars = {}

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  A {policy_type} allows you to create drive groups, virtual drives, configure the ')
            print(f'  storage capacity of a virtual drive, and configure the M.2 RAID controllers.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - {baseRepo}{path_sep}{org}{path_sep}{self.type}{path_sep}{yaml_file}.yaml')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure a {policy_type}?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                loop_count = 1
                policy_loop = False
                while policy_loop == False:

                    if not name_prefix == '': name = f'{name_prefix}-{name_suffix}'
                    else: name = f'{org}-{name_suffix}'

                    # Obtain Policy Name
                    polVars['name']        = ezfunctions.policy_name(name, policy_type)
                    # Obtain Policy Description
                    polVars['description'] = ezfunctions.policy_descr(polVars['name'], policy_type)

                    # Configure the Global Host Spares Setting
                    polVars["multi_select"] = False
                    jsonVars = jsonData['storage.StoragePolicy']['allOf'][1]['properties']

                    # Configure the Global Host Spares Setting
                    polVars['description'] = jsonVars['GlobalHotSpares']['description']
                    polVars["varDefault"] = ''
                    polVars["varInput"] = 'Specify the disks that are to be used as hot spares,\n globally,'\
                        ' for all the Drive Groups. [press enter to skip]:'
                    polVars["varName"] = 'Global Hot Spares'
                    polVars["varRegex"] = jsonVars['GlobalHotSpares']['pattern']
                    polVars["minLength"] = 0
                    polVars["maxLength"] = 128
                    polVars["global_hot_spares"] = ezfunctions.varStringLoop(**kwargs)

                    # Obtain Unused Disks State
                    polVars['description'] = jsonVars['UnusedDisksState']['description']
                    polVars["jsonVars"] = sorted(jsonVars['UnusedDisksState']['enum'])
                    polVars["defaultVar"] = jsonVars['UnusedDisksState']['default']
                    polVars["varType"] = 'Unused Disks State'
                    polVars["unused_disks_state"] = ezfunctions.variablesFromAPI(**kwargs)

                    # Configure the Global Host Spares Setting
                    polVars['description'] = jsonVars['UseJbodForVdCreation']['description']
                    polVars["varInput"] = f'Do you want to Use JBOD drives for Virtual Drive creation?'
                    polVars["varDefault"] = 'N'
                    polVars["varName"] = 'Use Jbod For Vd Creation'
                    polVars["use_jbod_for_vd_creation"] = ezfunctions.varBoolLoop(**kwargs)

                    # Ask if Drive Groups should be configured
                    polVars['description'] = 'Drive Group Configuration - Enable to add RAID drive groups that can be used to create'\
                        ' virtual drives.  You can also specify the Global Hot Spares information.'
                    polVars["varInput"] = f'Do you want to Configure Drive Groups?'
                    polVars["varDefault"] = 'N'
                    polVars["varName"] = 'Drive Groups'
                    driveGroups = ezfunctions.varBoolLoop(**kwargs)

                    # If True configure Drive Groups
                    if driveGroups == True:
                        polVars["drive_groups"] = []
                        inner_loop_count = 1
                        drive_group = []
                        drive_group_loop = False
                        while drive_group_loop == False:
                            jsonVars = jsonData['storage.DriveGroup']['allOf'][1]['properties']

                            # Request Drive Group Name
                            polVars['description'] = jsonVars['Name']['description']
                            polVars["varDefault"] = f'dg{inner_loop_count - 1}'
                            polVars["varInput"] = f'Enter the Drive Group Name.  [{polVars["varDefault"]}]:'
                            polVars["varName"] = 'Drive Group Name'
                            polVars["varRegex"] = jsonVars['Name']['pattern']
                            polVars["minLength"] = 1
                            polVars["maxLength"] = 60
                            dgName = ezfunctions.varStringLoop(**kwargs)

                            # Obtain Raid Level for Drive Group
                            polVars['description'] = jsonVars['RaidLevel']['description']
                            polVars["jsonVars"] = sorted(jsonVars['RaidLevel']['enum'])
                            polVars["defaultVar"] = jsonVars['RaidLevel']['default']
                            polVars["varType"] = 'Raid Level'
                            RaidLevel = ezfunctions.variablesFromAPI(**kwargs)

                            jsonVars = jsonData['storage.ManualDriveGroup']['allOf'][1]['properties']

                            # If Raid Level is anything other than Raid0 ask for Hot Spares
                            if not RaidLevel == 'Raid0':
                                polVars['description'] = jsonVars['DedicatedHotSpares']['description']
                                polVars["varInput"] = 'Enter the Drives to add as Dedicated Hot Spares [press enter to skip]:'
                                polVars["varName"] = 'Dedicated Hot Spares'
                                polVars["varRegex"] = jsonVars['DedicatedHotSpares']['pattern']
                                polVars["minLength"] = 1
                                polVars["maxLength"] = 60
                                DedicatedHotSpares = ezfunctions.varStringLoop(**kwargs)
                            else:
                                DedicatedHotSpares = ''

                            # Configure Span Slots
                            SpanSlots = []
                            # If Riad is 10, 50 or 60 allow multiple Span Slots
                            if re.fullmatch('^Raid(10|50|60)$', RaidLevel):
                                polVars['description'] = jsonVars['SpanGroups']['items']['description']
                                polVars["jsonVars"] = [2, 4, 6, 8]
                                polVars["defaultVar"] = 2
                                polVars["varType"] = 'Span Groups'
                                SpanGroups = ezfunctions.variablesFromAPI(**kwargs)
                                if SpanGroups == 2:
                                    SpanGroups = [0, 1]
                                elif SpanGroups == 4:
                                    SpanGroups = [0, 1, 2, 3]
                                elif SpanGroups == 6:
                                    SpanGroups = [0, 1, 2, 3, 4, 5]
                                elif SpanGroups == 8:
                                    SpanGroups = [0, 1, 2, 3, 4, 5, 6, 7]


                                for span in SpanGroups:
                                    jsonVars = jsonData['storage.SpanDrives']['allOf'][1]['properties']
                                    polVars['description'] = jsonVars['Slots']['description']
                                    if re.fullmatch('^Raid10$', RaidLevel):
                                        Drive1 = (inner_loop_count * 2) - 1
                                        Drive2 = (inner_loop_count * 2)
                                        polVars["varDefault"] = f'{Drive1}-{Drive2}'
                                    elif re.fullmatch('^Raid50$', RaidLevel):
                                        Drive1 = (inner_loop_count * 3) - 2
                                        Drive2 = (inner_loop_count * 3)
                                        polVars["varDefault"] = f'{Drive1}-{Drive2}'
                                    elif re.fullmatch('^Raid60$', RaidLevel):
                                        Drive1 = (inner_loop_count * 4) - 3
                                        Drive2 = (inner_loop_count * 4)
                                        polVars["varDefault"] = f'{Drive1}-{Drive2}'
                                    polVars["varInput"] = f'Enter the Drive Slots for Drive Array Span {span}. [{polVars["varDefault"]}]:'
                                    polVars["varName"] = 'Drive Slots'
                                    polVars["varRegex"] = jsonVars['Slots']['pattern']
                                    polVars["minLength"] = 1
                                    polVars["maxLength"] = 10
                                    SpanSlots.append({'slots':ezfunctions.varStringLoop(**kwargs)})
                            elif re.fullmatch('^Raid(0|1|5|6)$', RaidLevel):
                                jsonVars = jsonData['storage.SpanDrives']['allOf'][1]['properties']
                                polVars['description'] = jsonVars['Slots']['description']
                                if re.fullmatch('^Raid(0|1)$', RaidLevel):
                                    Drive1 = (inner_loop_count * 2) - 1
                                    Drive2 = (inner_loop_count * 2)
                                    polVars["varDefault"] = f'{Drive1}-{Drive2}'
                                elif re.fullmatch('^Raid5$', RaidLevel):
                                    Drive1 = (inner_loop_count * 3) - 2
                                    Drive2 = (inner_loop_count * 3)
                                    polVars["varDefault"] = f'{Drive1}-{Drive2}'
                                elif re.fullmatch('^Raid6$', RaidLevel):
                                    Drive1 = (inner_loop_count * 4) - 3
                                    Drive2 = (inner_loop_count * 4)
                                    polVars["varDefault"] = f'{Drive1}-{Drive2}'
                                polVars["varInput"] = f'Enter the Drive Slots for Drive Array Span 0. [{polVars["varDefault"]}]:'
                                polVars["varName"] = 'Drive Slots'
                                polVars["varRegex"] = jsonVars['Slots']['pattern']
                                polVars["minLength"] = 1
                                polVars["maxLength"] = 10
                                SpanSlots.append({'slots':ezfunctions.varStringLoop(**kwargs)})
                                
                            virtualDrives = []
                            sub_loop_count = 0
                            sub_loop = False
                            while sub_loop == False:
                                jsonVars = jsonData['storage.VirtualDriveConfiguration']['allOf'][1]['properties']

                                polVars['description'] = jsonVars['Name']['description']
                                polVars["varDefault"] = f'vd{sub_loop_count}'
                                polVars["varInput"] = f'Enter the name of the Virtual Drive.  [vd{sub_loop_count}]'
                                polVars["varName"] = 'Drive Group Name'
                                polVars["varRegex"] = jsonVars['Name']['pattern']
                                polVars["minLength"] = 1
                                polVars["maxLength"] = 60
                                vd_name = ezfunctions.varStringLoop(**kwargs)

                                polVars['description'] = jsonVars['ExpandToAvailable']['description']
                                polVars["varInput"] = f'Do you want to expand to all the space in the drive group?'
                                polVars["varDefault"] = 'Y'
                                polVars["varName"] = 'Expand To Available'
                                ExpandToAvailable = ezfunctions.varBoolLoop(**kwargs)

                                # If Expand to Available is Disabled obtain Virtual Drive disk size
                                if ExpandToAvailable == False:
                                    polVars['description'] = jsonVars['Size']['description']
                                    polVars["varDefault"] =  '1'
                                    polVars["varInput"] = 'What is the Size for this Virtual Drive?'
                                    polVars["varName"] = 'Size'
                                    polVars["varRegex"] = '[0-9]+'
                                    polVars["minNum"] = jsonVars['Size']['minimum']
                                    polVars["maxNum"] = 9999999999
                                    vdSize = ezfunctions.varNumberLoop(**kwargs)
                                else:
                                    vdSize = 1
                                
                                polVars['description'] = jsonVars['BootDrive']['description']
                                polVars["varInput"] = f'Do you want to configure {vd_name} as a boot drive?'
                                polVars["varDefault"] = 'Y'
                                polVars["varName"] = 'Boot Drive'
                                BootDrive = ezfunctions.varBoolLoop(**kwargs)

                                jsonVars = jsonData['storage.VirtualDrivePolicy']['allOf'][1]['properties']

                                polVars['description'] = jsonVars['AccessPolicy']['description']
                                polVars["jsonVars"] = sorted(jsonVars['AccessPolicy']['enum'])
                                polVars["defaultVar"] = jsonVars['AccessPolicy']['default']
                                polVars["varType"] = 'Access Policy'
                                AccessPolicy = ezfunctions.variablesFromAPI(**kwargs)

                                polVars['description'] = jsonVars['DriveCache']['description']
                                polVars["jsonVars"] = sorted(jsonVars['DriveCache']['enum'])
                                polVars["defaultVar"] = jsonVars['DriveCache']['default']
                                polVars["varType"] = 'Drive Cache'
                                DriveCache = ezfunctions.variablesFromAPI(**kwargs)

                                polVars['description'] = jsonVars['ReadPolicy']['description']
                                polVars["jsonVars"] = sorted(jsonVars['ReadPolicy']['enum'])
                                polVars["defaultVar"] = jsonVars['ReadPolicy']['default']
                                polVars["varType"] = 'Read Policy'
                                ReadPolicy = ezfunctions.variablesFromAPI(**kwargs)

                                polVars['description'] = jsonVars['StripSize']['description']
                                polVars["jsonVars"] = sorted(jsonVars['StripSize']['enum'])
                                polVars["defaultVar"] = jsonVars['StripSize']['default']
                                polVars["varType"] = 'Strip Size'
                                StripSize = ezfunctions.variablesFromAPI(**kwargs)

                                polVars['description'] = jsonVars['WritePolicy']['description']
                                polVars["jsonVars"] = sorted(jsonVars['WritePolicy']['enum'])
                                polVars["defaultVar"] = jsonVars['WritePolicy']['default']
                                polVars["varType"] = 'Write Policy'
                                WritePolicy = ezfunctions.variablesFromAPI(**kwargs)

                                virtual_drive = {
                                    'access_policy':AccessPolicy,
                                    'boot_drive':BootDrive,
                                    'disk_cache':DriveCache,
                                    'expand_to_available':ExpandToAvailable,
                                    'name':vd_name,
                                    'read_policy':ReadPolicy,
                                    'size':vdSize,
                                    'strip_size':StripSize,
                                    'write_policy':WritePolicy,
                                }
                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                print(f'    "{virtual_drive["name"]}" = ''{')
                                print(f'      access_policy       = "{virtual_drive["access_policy"]}"')
                                print(f'      boot_drive          = {virtual_drive["boot_drive"]}')
                                print(f'      disk_cache          = "{virtual_drive["disk_cache"]}"')
                                print(f'      expand_to_available = {virtual_drive["expand_to_available"]}')
                                print(f'      read_policy         = "{virtual_drive["read_policy"]}"')
                                print(f'      size                = {virtual_drive["size"]}')
                                print(f'      strip_size          = "{virtual_drive["strip_size"]}"')
                                print(f'      write_policy        = "{virtual_drive["write_policy"]}"')
                                print(f'    ''}')
                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                valid_confirm = False
                                while valid_confirm == False:
                                    confirm_v = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
                                    if confirm_v == 'Y' or confirm_v == '':
                                        virtualDrives.append(virtual_drive)
                                        valid_exit = False
                                        while valid_exit == False:
                                            loop_exit = input(f'Would You like to Configure another Virtual Drive for {dgName}?  Enter "Y" or "N" [N]: ')
                                            if loop_exit == 'Y':
                                                inner_loop_count += 1
                                                valid_confirm = True
                                                valid_exit = True
                                            elif loop_exit == 'N' or loop_exit == '':
                                                drive_group_loop = True
                                                valid_confirm = True
                                                valid_exit = True
                                            else: ezfunctions.message_invalid_y_or_n('short')

                                    elif confirm_v == 'N':
                                        pol_type = 'Virtual Drive Configuration'
                                        ezfunctions.message_starting_over(pol_type)
                                        valid_confirm = True
                                    else: ezfunctions.message_invalid_y_or_n('short')


                            drive_group = {
                                'drive_group_name':dgName,
                                'manual_drive_selection':{
                                    'dedicated_hot_spares':DedicatedHotSpares,
                                    'drive_array_spans':[
                                        SpanSlots
                                    ]
                                },
                                'raid_level':RaidLevel,
                                'virtual_drives':virtualDrives
                            }
                            dg_count = 0
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            print(f'      "{drive_group["drive_group_name"]}" = ''{')
                            print(f'        manual_drive_group = ''{')
                            print(f'          "{dg_count}" = ''{')
                            print(f'            dedicated_hot_spares = "{drive_group["manual_drive_group"]["dedicated_hot_spares"]}"')
                            print(f'            drive_array_spans = ''{')
                            span_count = 0
                            for i in drive_group["manual_drive_group"]["drive_array_spans"]:
                                print(f'              "span_{span_count}" = ''{slots = "'f'{i["slots"]}"''}')
                                span_count += 1
                                print(f'              ''}')
                            print(f'              ''}')
                            print(f'            ''}')
                            print(f'          ''}')
                            print(f'          ''}')
                            print(f'        ''}')
                            print(f'        raid_level = "{RaidLevel}"')
                            print(f'        virtual_drives = ''{')
                            for virtual_drive in virtualDrives:
                                print(f'          "{virtual_drive["name"]}" = ''{')
                                print(f'            access_policy       = "{virtual_drive["access_policy"]}"')
                                print(f'            boot_drive          = "{virtual_drive["boot_drive"]}"')
                                print(f'            disk_cache          = "{virtual_drive["disk_cache"]}"')
                                print(f'            expand_to_available = {virtual_drive["expand_to_available"]}')
                                print(f'            read_policy         = "{virtual_drive["read_policy"]}"')
                                print(f'            size                = {virtual_drive["size"]}')
                                print(f'            strip_size          = "{virtual_drive["strip_size"]}"')
                                print(f'            write_policy        = "{virtual_drive["write_policy"]}"')
                                print(f'          ''}')
                            print(f'        ''}')
                            print(f'      ''}')
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            valid_confirm = False
                            while valid_confirm == False:
                                confirm_v = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
                                if confirm_v == 'Y' or confirm_v == '':
                                    polVars["drive_groups"].append(drive_group)
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
                                        else: ezfunctions.message_invalid_y_or_n('short')

                                elif confirm_v == 'N':
                                    pol_type = 'Drive Grouop Configuration'
                                    ezfunctions.message_starting_over(pol_type)
                                    valid_confirm = True
                                else: ezfunctions.message_invalid_y_or_n('short')
                    else:
                        polVars["drive_groups"] = []

                    # Ask if M2 should be configured
                    polVars['description'] = jsonVars['M2VirtualDrive']['description']
                    polVars["varInput"] = f'Do you want to Enable the M.2 Virtual Drive Configuration?'
                    polVars["varDefault"] = 'Y'
                    polVars["varName"] = 'M.2 Virtual Drive'
                    M2VirtualDrive = ezfunctions.varBoolLoop(**kwargs)

                    # Configure M2 if it is True if not Pop it from the list
                    if M2VirtualDrive == True:
                        jsonVars = jsonData['storage.M2VirtualDriveConfig']['allOf'][1]['properties']

                        polVars['description'] = jsonVars['ControllerSlot']['description']
                        polVars["jsonVars"] = sorted(jsonVars['ControllerSlot']['enum'])
                        polVars["defaultVar"] = 'MSTOR-RAID-1'
                        polVars["varType"] = 'Controller Slot'
                        ControllerSlot = ezfunctions.variablesFromAPI(**kwargs)

                        polVars["m2_configuration"] = {
                            'controller_slot':ControllerSlot,
                            'enable':True
                        }
                    else:
                        polVars.pop('m2_configuration')

                    # Ask if Drive Groups should be configured
                    polVars['description'] = 'Enable to create RAID0 virtual drives on each physical drive..'
                    polVars["varInput"] = f"Do you want to Configure Single Drive RAID's?"
                    polVars["varDefault"] = 'N'
                    polVars["varName"] = 'Single Drive RAID'
                    singledriveRaid = ezfunctions.varBoolLoop(**kwargs)

                    # If True configure Drive Groups
                    if singledriveRaid == True:
                        single_drive_loop = False
                        while single_drive_loop == False:
                            # Obtain the Single Drive Raid Slots
                            jsonVars = jsonData['storage.R0Drive']['allOf'][1]['properties']
                            polVars['description'] = jsonVars['DriveSlots']['description']
                            polVars["varDefault"] = f'1-2'
                            polVars["varInput"] = f'Enter the Drive Slots for Drive Array Span 0. [{polVars["varDefault"]}]:'
                            polVars["varName"] = 'Drive Slots'
                            polVars["varRegex"] = jsonVars['DriveSlots']['pattern']
                            polVars["minLength"] = 1
                            polVars["maxLength"] = 64
                            DriveSlots = ezfunctions.varStringLoop(**kwargs)
                                
                            # Obtain the Virtual Drive Policies
                            jsonVars = jsonData['storage.VirtualDrivePolicy']['allOf'][1]['properties']

                            # Access Policy
                            polVars['description'] = jsonVars['AccessPolicy']['description']
                            polVars["jsonVars"] = sorted(jsonVars['AccessPolicy']['enum'])
                            polVars["defaultVar"] = jsonVars['AccessPolicy']['default']
                            polVars["varType"] = 'Access Policy'
                            AccessPolicy = ezfunctions.variablesFromAPI(**kwargs)

                            # Drive Cache
                            polVars['description'] = jsonVars['DriveCache']['description']
                            polVars["jsonVars"] = sorted(jsonVars['DriveCache']['enum'])
                            polVars["defaultVar"] = jsonVars['DriveCache']['default']
                            polVars["varType"] = 'Drive Cache'
                            DriveCache = ezfunctions.variablesFromAPI(**kwargs)

                            # Read Policy
                            polVars['description'] = jsonVars['ReadPolicy']['description']
                            polVars["jsonVars"] = sorted(jsonVars['ReadPolicy']['enum'])
                            polVars["defaultVar"] = jsonVars['ReadPolicy']['default']
                            polVars["varType"] = 'Read Policy'
                            ReadPolicy = ezfunctions.variablesFromAPI(**kwargs)

                            # Strip Size
                            polVars['description'] = jsonVars['StripSize']['description']
                            polVars["jsonVars"] = sorted(jsonVars['StripSize']['enum'])
                            polVars["defaultVar"] = jsonVars['StripSize']['default']
                            polVars["varType"] = 'Strip Size'
                            StripSize = ezfunctions.variablesFromAPI(**kwargs)

                            # Write Policy
                            polVars['description'] = jsonVars['WritePolicy']['description']
                            polVars["jsonVars"] = sorted(jsonVars['WritePolicy']['enum'])
                            polVars["defaultVar"] = jsonVars['WritePolicy']['default']
                            polVars["varType"] = 'Write Policy'
                            WritePolicy = ezfunctions.variablesFromAPI(**kwargs)

                            polVars["single_drive_raid_configuration"] = {
                                'access_policy':AccessPolicy,
                                'disk_cache':DriveCache,
                                'drive_slots':DriveSlots,
                                'enable':True,
                                'read_policy':ReadPolicy,
                                'strip_size':StripSize,
                                'write_policy':WritePolicy,
                            }
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            print(f'    "0" = ''{')
                            print(f'      access_policy = "{polVars["single_drive_raid_configuration"]["access_policy"]}"')
                            print(f'      disk_cache    = "{polVars["single_drive_raid_configuration"]["disk_cache"]}"')
                            print(f'      drive_slots   = "{polVars["single_drive_raid_configuration"]["drive_slots"]}"')
                            print(f'      enable        = {polVars["single_drive_raid_configuration"]["enable"]}')
                            print(f'      read_policy   = "{polVars["single_drive_raid_configuration"]["read_policy"]}"')
                            print(f'      strip_size    = "{polVars["single_drive_raid_configuration"]["strip_size"]}"')
                            print(f'      write_policy  = "{polVars["single_drive_raid_configuration"]["write_policy"]}"')
                            print(f'    ''}')
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            valid_confirm = False
                            while valid_confirm == False:
                                confirm_v = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
                                if confirm_v == 'Y' or confirm_v == '':
                                    single_drive_loop = True
                                    valid_confirm = True
                                    valid_exit = True
                                elif confirm_v == 'N':
                                    pol_type = 'Single Drive RAID Configuration'
                                    ezfunctions.message_starting_over(pol_type)
                                    valid_confirm = True
                                else: ezfunctions.message_invalid_y_or_n('short')

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(textwrap.indent(yaml.dump(polVars, Dumper=MyDumper, default_flow_style=False), ' '*4, predicate=None))
                    print(f'-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
                        if confirm_policy == 'Y' or confirm_policy == '':
                            confirm_policy = 'Y'

                            # Write Policies to Template File
                            polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                            ezfunctions.write_to_template(self, **kwargs)

                            # Add Template Name to Policies Output
                            ezfunctions.policy_names.append(polVars['name'])

                            configure_loop, policy_loop = ezfunctions.exit_default(policy_type, 'N')
                            valid_confirm = True

                        elif confirm_policy == 'N':
                            ezfunctions.message_starting_over(policy_type)
                            valid_confirm = True
                        else: ezfunctions.message_invalid_y_or_n('short')
            elif configure == 'N': configure_loop = True
            else: ezfunctions.message_invalid_y_or_n('long')
        # Return kwargs
        return kwargs

    #==============================================
    # Syslog Policy Module
    #==============================================
    def syslog_policies(self, **kwargs):
        baseRepo    = kwargs['args'].dir
        ezData      = kwargs['ezData']
        jsonData    = kwargs['jsonData']
        name_prefix = self.name_prefix
        name_suffix = 'syslog'
        org         = self.org
        path_sep    = kwargs['path_sep']
        policy_type = 'Syslog Policy'
        yaml_file   = 'management'
        polVars = {}

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  A {policy_type} will configure domain and servers with remote syslog servers.')
            print(f'  You can configure up to two Remote Syslog Servers.')
            print(f'  This Policy is not required to standup a server but is a good practice for day 2 support.')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - {baseRepo}{path_sep}{org}{path_sep}{self.type}{path_sep}{yaml_file}.yaml')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure a {policy_type}?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                policy_loop = False
                while policy_loop == False:

                    if not name_prefix == '': name = f'{name_prefix}-{name_suffix}'
                    else: name = f'{org}-{name_suffix}'

                    polVars['name']        = ezfunctions.policy_name(name, policy_type)
                    polVars['description'] = ezfunctions.policy_descr(polVars['name'], policy_type)

                    # Syslog Local Logging
                    polVars["multi_select"] = False
                    jsonVars = jsonData['syslog.LocalClientBase']['allOf'][1]['properties']
                    polVars['description'] = jsonVars['MinSeverity']['description']
                    polVars["jsonVars"] = sorted(jsonVars['MinSeverity']['enum'])
                    polVars["defaultVar"] = jsonVars['MinSeverity']['default']
                    polVars["varType"] = 'Syslog Local Minimum Severity'
                    polVars["min_severity"] = ezfunctions.variablesFromAPI(**kwargs)

                    polVars["local_logging"] = {'file':{'min_severity':polVars["min_severity"]}}

                    remote_logging = ezfunctions.syslog_servers(jsonData, **kwargs)
                    polVars['remote_logging'] = remote_logging

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(textwrap.indent(yaml.dump(polVars, Dumper=MyDumper, default_flow_style=False), ' '*4, predicate=None))
                    print(f'-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                        if confirm_policy == 'Y' or confirm_policy == '':
                            confirm_policy = 'Y'

                            # Write Policies to Template File
                            polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                            ezfunctions.write_to_template(self, **kwargs)

                            configure_loop, policy_loop = ezfunctions.exit_default(policy_type, 'N')
                            valid_confirm = True

                        elif confirm_policy == 'N':
                            ezfunctions.message_starting_over(policy_type)
                            valid_confirm = True
                        else: ezfunctions.message_invalid_y_or_n('short')
            elif configure == 'N': configure_loop = True
            else: ezfunctions.message_invalid_y_or_n('long')
        # Return kwargs
        return kwargs

    #==============================================
    # Thermal Policy Module
    #==============================================
    def thermal_policies(self, **kwargs):
        baseRepo    = kwargs['args'].dir
        ezData      = kwargs['ezData']
        jsonData    = kwargs['jsonData']
        name_prefix = self.name_prefix
        org         = self.org
        path_sep    = kwargs['path_sep']
        policy_type = 'Thermal Policy'
        yaml_file   = 'environment'
        polVars = {}

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  A {policy_type} will configure the Cooling/FAN Policy for Chassis.  We recommend ')
            print(f'  Balanced for a 5108 and Acoustic for a 9508 Chassis, as of this writing.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - {baseRepo}{path_sep}{org}{path_sep}{self.type}{path_sep}{yaml_file}.yaml')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            policy_loop = False
            while policy_loop == False:

                polVars["multi_select"] = False
                jsonVars = ezData['policies']['thermal.Policy']
                polVars['description'] = jsonVars['chassisType']['description']
                polVars["jsonVars"] = sorted(jsonVars['chassisType']['enum'])
                polVars["defaultVar"] = jsonVars['chassisType']['default']
                polVars["varType"] = 'Chassis Type'
                polVars["chassis_type"] = ezfunctions.variablesFromAPI(**kwargs)

                if not name_prefix == '':
                    name = '%s-%s' % (name_prefix, polVars["chassis_type"])
                else:
                    name = '%s-%s' % (org, polVars["chassis_type"])

                polVars['name']        = ezfunctions.policy_name(name, policy_type)
                polVars['description'] = ezfunctions.policy_descr(polVars['name'], policy_type)

                if polVars["chassis_type"] == '5108':
                    polVars["popList"] = ['Acoustic', 'HighPower', 'MaximumPower']
                if polVars["chassis_type"] == '9508':
                    polVars["popList"] = []
                jsonVars = jsonData['thermal.Policy']['allOf'][1]['properties']
                polVars['description'] = jsonVars['FanControlMode']['description']
                polVars["jsonVars"] = sorted(jsonVars['FanControlMode']['enum'])
                polVars["defaultVar"] = jsonVars['FanControlMode']['default']
                polVars["varType"] = 'Fan Control Mode'
                polVars["fan_control_mode"] = ezfunctions.variablesFromAPI(**kwargs)

                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(textwrap.indent(yaml.dump(polVars, Dumper=MyDumper, default_flow_style=False), ' '*4, predicate=None))
                print(f'-------------------------------------------------------------------------------------------\n')
                valid_confirm = False
                while valid_confirm == False:
                    confirm_policy = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                    if confirm_policy == 'Y' or confirm_policy == '':
                        confirm_policy = 'Y'

                        # Write Policies to Template File
                        polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                        ezfunctions.write_to_template(self, **kwargs)

                        configure_loop, policy_loop = ezfunctions.exit_default(policy_type, 'N')
                        valid_confirm = True
                    elif confirm_policy == 'N':
                        ezfunctions.message_starting_over(policy_type)
                        valid_confirm = True
                    else: ezfunctions.message_invalid_y_or_n('long')
        # Return kwargs
        return kwargs

    #==============================================
    # Provider and Variables Module
    #==============================================
    def variables(self, **kwargs):
        baseRepo      = kwargs['args'].dir
        ezData        = kwargs['ezData']
        org           = self.org
        kwargs['org'] = self.org
        policy_type   = 'variables'
        polVars = {}
        polVars['endpoint'] = kwargs['args'].endpoint
        polVars["organization"] = org
        polVars["tags"] = [
            {'key': "Module", 'value': "terraform-intersight-easy-imm"},
            {'key': "Version", 'value': f"{ezData['version']}"}
        ]
        # Write Policies to Template File
        kwargs["template_file"] = '%s.j2' % (policy_type)
        kwargs['dest_file'] = f'{policy_type}.auto.tfvars'
        ezfunctions.write_to_org_folder(polVars, **kwargs)

        policy_type = 'provider'
        polVars = {
            'intersight_provider_version': kwargs['latest_versions']['intersight_provider_version'],
            'terraform_version': kwargs['latest_versions']['terraform_version'],
            'utils_provider_version': kwargs['latest_versions']['utils_provider_version']
        }
        # Write Policies to Template File
        kwargs["template_file"] = '%s.j2' % (policy_type)
        kwargs['dest_file'] = f'{policy_type}.tf'
        ezfunctions.write_to_org_folder(polVars, **kwargs)
        ezfunctions.terraform_fmt(os.path.join(baseRepo, org))


    #==============================================
    # Virtual KVM Policy Module
    #==============================================
    def virtual_kvm_policies(self, **kwargs):
        baseRepo    = kwargs['args'].dir
        ezData      = kwargs['ezData']
        jsonData    = kwargs['jsonData']
        name_prefix = self.name_prefix
        name_suffix = 'vkvm'
        org         = self.org
        path_sep    = kwargs['path_sep']
        policy_type = 'Virtual KVM Policy'
        yaml_file   = 'management'
        polVars = {}

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  A {policy_type} will configure the Server for KVM access.  Settings include:')
            print(f'   - Local Server Video - If enabled, displays KVM on any monitor attached to the server.')
            print(f'   - Video Encryption - encrypts all video information sent through KVM.')
            print(f'   - Remote Port - The port used for KVM communication. Range is 1 to 65535.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - {baseRepo}{path_sep}{org}{path_sep}{self.type}{path_sep}{yaml_file}.yaml')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            policy_loop = False
            while policy_loop == False:
                if not name_prefix == '': name = f'{name_prefix}-{name_suffix}'
                else: name = f'{org}-{name_suffix}'
                polVars['name']        = ezfunctions.policy_name(name, policy_type)
                polVars['description'] = ezfunctions.policy_descr(polVars['name'], policy_type)
                polVars["enable_virtual_kvm"] = True
                polVars["maximum_sessions"] = 4

                # Pull in the Policies for Virtual KVM
                jsonVars = jsonData['kvm.Policy']['allOf'][1]['properties']
                polVars["multi_select"] = False

                # Enable Local Server Video
                polVars['description'] = 'Enables Tunneled vKVM on the endpoint. Applicable only for Device Connectors that support Tunneled vKVM'
                polVars["varInput"] = f'Do you want to Tunneled vKVM through Intersight for this Policy?\n'
                '* Note: Make sure to Enable Virtual Tunneled KVM Launch and Configuration under:\n'
                'Setttings > Settings > Security & Privacy.'
                polVars["varDefault"] = 'N'
                polVars["varName"] = 'Allow Tunneled vKVM'
                polVars["allow_tunneled_vkvm"] = ezfunctions.varBoolLoop(**kwargs)

                # Enable Local Server Video
                polVars['description'] = jsonVars['EnableLocalServerVideo']['description']
                polVars["varInput"] = f'Do you want to Display KVM on Monitors attached to the Server?'
                polVars["varDefault"] = 'Y'
                polVars["varName"] = 'Enable Local Server Video'
                polVars["enable_local_server_video"] = ezfunctions.varBoolLoop(**kwargs)

                # Enable Video Encryption
                polVars['description'] = jsonVars['EnableVideoEncryption']['description']
                polVars["varInput"] = f'Do you want to Enable video Encryption?'
                polVars["varDefault"] = 'Y'
                polVars["varName"] = 'Enable Video Encryption'
                polVars["enable_video_encryption"] = ezfunctions.varBoolLoop(**kwargs)

                # Obtain the Port to Use for vKVM
                polVars['description'] = jsonVars['RemotePort']['description']
                polVars["varDefault"] =  jsonVars['RemotePort']['default']
                polVars["varInput"] = 'What is the Port you would like to Assign for Remote Access?\n'
                'This should be a value between 1024-65535. [2068]: '
                polVars["varName"] = 'Remote Port'
                polVars["varRegex"] = '^[0-9]+$'
                polVars["minNum"] = 1
                polVars["maxNum"] = 65535
                polVars["remote_port"] = ezfunctions.varNumberLoop(**kwargs)

                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(textwrap.indent(yaml.dump(polVars, Dumper=MyDumper, default_flow_style=False), ' '*4, predicate=None))
                print(f'-------------------------------------------------------------------------------------------\n')
                valid_confirm = False
                while valid_confirm == False:
                    confirm_policy = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                    if confirm_policy == 'Y' or confirm_policy == '':
                        confirm_policy = 'Y'

                        # Write Policies to Template File
                        polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                        ezfunctions.write_to_template(self, **kwargs)

                        configure_loop, policy_loop = ezfunctions.exit_default(policy_type, 'N')
                        valid_confirm = True
                    elif confirm_policy == 'N':
                        ezfunctions.message_starting_over(policy_type)
                        valid_confirm = True
                    else: ezfunctions.message_invalid_y_or_n('long')
        # Return kwargs
        return kwargs

    #==============================================
    # Virtual Media Policy Policy Module
    #==============================================
    def virtual_media_policies(self, **kwargs):
        baseRepo    = kwargs['args'].dir
        ezData      = kwargs['ezData']
        jsonData    = kwargs['jsonData']
        name_prefix = self.name_prefix
        name_suffix = 'vmedia'
        org         = self.org
        path_sep    = kwargs['path_sep']
        policy_type = 'Virtual Media Policy'
        yaml_file   = 'management'
        polVars = {}

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  A {policy_type} enables you to install an operating system on the server using the ')
            print(f'  KVM console and virtual media, mount files to the host from a remote file share, and ')
            print(f'  enable virtual media encryption. You can create one or more virtual media policies, which ')
            print(f'  could contain virtual media mappings for different OS images, and configure up to two ')
            print(f'  virtual media mappings, one for ISO files through CDD and the other for IMG files ')
            print(f'  through HDD.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - {baseRepo}{path_sep}{org}{path_sep}{self.type}{path_sep}{yaml_file}.yaml')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure an {policy_type}?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                loop_count = 1
                policy_loop = False
                while policy_loop == False:

                    if not name_prefix == '': name = f'{name_prefix}-{name_suffix}'
                    else: name = f'{org}-{name_suffix}'

                    polVars['name']        = ezfunctions.policy_name(name, policy_type)
                    polVars['description'] = ezfunctions.policy_descr(polVars['name'], policy_type)
                    polVars["enable_virtual_media"] = True

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'    Select this option to enable the appearance of virtual drives on the boot selection menu')
                    print(f'    after mapping the image and rebooting the host. This property is enabled by default.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid = False
                    while valid == False:
                        question = input(f'Do you want to Enable Low Power USB?  Enter "Y" or "N" [Y]: ')
                        if question == 'N':
                            polVars["enable_low_power_usb"] = False
                            valid = True
                        elif question == '' or question == 'Y':
                            polVars["enable_low_power_usb"] = True
                            valid = True
                        else: ezfunctions.message_invalid_y_or_n('short')

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'    Select this option to enable encryption of the virtual media communications. ')
                    print(f'    This property is enabled by default.')
                    print(f'    Note: For firmware versions 4.2(1a) or higher, this encryption parameter is deprecated ')
                    print(f'          and disabling the encryption will further result in validation failure during')
                    print(f'          the server profile deployment.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid = False
                    while valid == False:
                        question = input(f'Do you want to Enable Virtual Media Encryption?  Enter "Y" or "N" [Y]: ')
                        if question == 'N':
                            polVars["enable_virtual_media_encryption"] = False
                            valid = True
                        elif question == '' or question == 'Y':
                            polVars["enable_virtual_media_encryption"] = True
                            valid = True
                        else: ezfunctions.message_invalid_y_or_n('short')

                    polVars["virtual_media"] = []
                    inner_loop_count = 1
                    sub_loop = False
                    while sub_loop == False:
                        question = input(f'\nWould you like to add vMedia to this Policy?  Enter "Y" or "N" [Y]: ')
                        if question == '' or question == 'Y':
                            valid_sub = False
                            while valid_sub == False:
                                polVars["multi_select"] = False
                                jsonVars = jsonData['vmedia.Mapping']['allOf'][1]['properties']
                                polVars['description'] = jsonVars['MountProtocol']['description']
                                polVars["jsonVars"] = sorted(jsonVars['MountProtocol']['enum'])
                                polVars["defaultVar"] = jsonVars['MountProtocol']['default']
                                polVars["varType"] = 'vMedia Mount Protocol'
                                Protocol = ezfunctions.variablesFromAPI(**kwargs)

                                polVars['description'] = jsonVars['MountProtocol']['description']
                                polVars["jsonVars"] = sorted(jsonVars['MountProtocol']['enum'])
                                polVars["defaultVar"] = jsonVars['MountProtocol']['default']
                                polVars["varType"] = 'vMedia Mount Protocol'
                                deviceType = ezfunctions.variablesFromAPI(**kwargs)

                                if Protocol == 'cifs':
                                    polVars['description'] = jsonVars['AuthenticationProtocol']['description']
                                    polVars["jsonVars"] = sorted(jsonVars['AuthenticationProtocol']['enum'])
                                    polVars["defaultVar"] = jsonVars['AuthenticationProtocol']['default']
                                    polVars["varType"] = 'CIFS Authentication Protocol'
                                    authProtocol = ezfunctions.variablesFromAPI(**kwargs)

                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                print(f'  Provide the remote file location path: Host Name or IP address/file path/file name')
                                print(f'  * IP Address—The IP address or the hostname of the remote server.')
                                print(f'  * File Path—The path to the location of the image on the remote server.')
                                print(f'  The format of the File Location should be:')
                                if deviceType == 'cdd' and re.search('(cifs|nfs)', Protocol):
                                    print(f'  * hostname-or-ip-address/filePath/fileName.iso')
                                elif deviceType == 'hdd' and re.search('(cifs|nfs)', Protocol):
                                    print(f'  * hostname-or-ip-address/filePath/fileName.img')
                                elif deviceType == 'cdd' and Protocol == 'http':
                                    print(f'  * http://hostname-or-ip-address/filePath/fileName.iso')
                                elif deviceType == 'hdd' and Protocol == 'http':
                                    print(f'  * http://hostname-or-ip-address/filePath/fileName.img')
                                elif deviceType == 'cdd' and Protocol == 'https':
                                    print(f'  * https://hostname-or-ip-address/filePath/fileName.iso')
                                elif deviceType == 'hdd' and Protocol == 'https':
                                    print(f'  * https://hostname-or-ip-address/filePath/fileName.img')
                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                valid = False
                                while valid == False:
                                    Question = input(f'What is the file Location? ')
                                    if not Question == '':
                                        polVars["varName"] = 'File Location'
                                        varValue = Question
                                        if re.search('(http|https)', Protocol):
                                            valid = validating.url(polVars["varName"], varValue)
                                        else:
                                            varValue = 'http://%s' % (Question)
                                            valid = validating.url(polVars["varName"], varValue)
                                    else:
                                        print(f'\n-------------------------------------------------------------------------------------------\n')
                                        print(f'  Error!! Invalid Value.  Please Re-enter the LDAP Group.')
                                        print(f'\n-------------------------------------------------------------------------------------------\n')

                                # Assign the Variable
                                file_location = Question

                                valid = False
                                while valid == False:
                                    Question = input(f'What is the Username you would like to configure for Authentication? [press enter for no username]: ')
                                    if not Question == '':
                                        polVars["minLength"] = 1
                                        polVars["maxLength"] = 255
                                        polVars["varName"] = 'Username'
                                        varValue = Question
                                        valid = validating.string_length(polVars["varName"], varValue, polVars["minLength"], polVars["maxLength"])
                                    if Question == '':
                                        valid = True
                                    else:
                                        print(f'\n-------------------------------------------------------------------------------------------\n')
                                        print(f'  Error!! Invalid Value.  Please Re-enter the LDAP Group.')
                                        print(f'\n-------------------------------------------------------------------------------------------\n')

                                # Assign the Variable
                                Username = Question

                                if not Username == '':
                                    valid = False
                                    while valid == False:
                                        Password = stdiomask.getpass(prompt='What is the password for authentication? ')
                                        polVars["minLength"] = 1
                                        polVars["maxLength"] = 255
                                        polVars["rePattern"] = '^[\\S]+$'
                                        polVars["varName"] = 'Password'
                                        varValue = Password
                                        valid_passphrase = validating.length_and_regex_sensitive(polVars["rePattern"], polVars["varName"], varValue, polVars["minLength"], polVars["maxLength"])
                                        if valid_passphrase == True:
                                            env_password = 'TF_VAR_vmedia_password_%s' % (inner_loop_count)
                                            os.environ[env_password] = '%s' % (Password)
                                            Password = inner_loop_count
                                            valid = True
                                else:
                                    Password = 0

                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                print(f'  The mount options for the virtual media mapping.')
                                if Protocol == 'cifs':
                                    print(f'  * supported options are soft, nounix, noserverino, guest, ver=3.0, or ver=2.0.')
                                elif Protocol == 'nfs':
                                    print(f'  * supported options are ro, rw, nolock, noexec, soft, port=VALUE, timeo=VALUE, retry=VALUE.')
                                else:
                                    print(f'  * the only supported option is noauto')
                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                valid = False
                                while valid == False:
                                    Question = input(f'Would you like to assign any mount options?  Enter "Y" or "N" [N]: ')
                                    if Question == '' or Question == 'N':
                                        assignOptions = False
                                        valid = True
                                    elif Question == 'Y':
                                        assignOptions = True
                                        valid = True
                                    else: ezfunctions.message_invalid_y_or_n('short')

                                if assignOptions == True:
                                    polVars["multi_select"] = True
                                    jsonVars = ezData['policies']['vmedia.Mapping']
                                    if Protocol == 'cifs':
                                        polVars['description'] = jsonVars['cifs.mountOptions']['description']
                                        polVars["jsonVars"] = sorted(jsonVars['cifs.mountOptions']['enum'])
                                        polVars["defaultVar"] = jsonVars['cifs.mountOptions']['default']
                                    elif Protocol == 'nfs':
                                        polVars['description'] = jsonVars['nfs.mountOptions']['description']
                                        polVars["jsonVars"] = sorted(jsonVars['nfs.mountOptions']['enum'])
                                        polVars["defaultVar"] = jsonVars['nfs.mountOptions']['default']
                                    else:
                                        polVars["multi_select"] = False
                                        polVars['description'] = jsonVars['http.mountOptions']['description']
                                        polVars["jsonVars"] = sorted(jsonVars['http.mountOptions']['enum'])
                                        polVars["defaultVar"] = jsonVars['http.mountOptions']['default']
                                    polVars["varType"] = 'Mount Options'
                                    mount_loop = ezfunctions.variablesFromAPI(**kwargs)

                                    mount_output = []
                                    for x in mount_loop:
                                        mount_output.append(x)
                                    print(mount_output)
                                    for x in mount_loop:
                                        if x == 'port':
                                            valid = False
                                            while valid == False:
                                                Question = input(f'What Port would you like to assign?  [2049]: ')
                                                if Question == '':
                                                    Question = 2049
                                                if re.fullmatch(r'^[0-9]{1,4}$', str(Question)):
                                                    polVars["minNum"] = 1
                                                    polVars["maxNum"] = 65535
                                                    polVars["varName"] = 'NFS Port'
                                                    varValue = Question
                                                    valid = validating.number_in_range(polVars["varName"], varValue, polVars["minNum"], polVars["maxNum"])
                                            port = 'port=%s' % (Question)
                                            mount_output.remove(x)
                                            mount_output.append(port)
                                        elif x == 'retry':
                                            valid = False
                                            while valid == False:
                                                Question = input(f'What Retry would you like to assign?  [2]: ')
                                                if Question == '':
                                                    Question = 2
                                                if re.fullmatch(r'^[0-9]{1,4}$', str(Question)):
                                                    polVars["minNum"] = 1
                                                    polVars["maxNum"] = 65535
                                                    polVars["varName"] = 'NFS Port'
                                                    varValue = Question
                                                    valid = validating.number_in_range(polVars["varName"], varValue, polVars["minNum"], polVars["maxNum"])
                                            retry = 'retry=%s' % (Question)
                                            mount_output.remove(x)
                                            mount_output.append(retry)
                                        elif x == 'timeo':
                                            valid = False
                                            while valid == False:
                                                Question = input(f'What Timeout (timeo) would you like to assign?  [600]: ')
                                                if Question == '':
                                                    Question = 600
                                                if re.fullmatch(r'^[0-9]{1,4}$', str(Question)):
                                                    polVars["minNum"] = 60
                                                    polVars["maxNum"] = 600
                                                    polVars["varName"] = 'NFS timeo'
                                                    varValue = Question
                                                    valid = validating.number_in_range(polVars["varName"], varValue, polVars["minNum"], polVars["maxNum"])
                                            timeo = 'timeo=%s' % (Question)
                                            mount_output.remove(x)
                                            mount_output.append(timeo)
                                        elif re.search('(rsize|wsize)', x):
                                            valid = False
                                            while valid == False:
                                                Question = input(f'What is the value of {x} you want to assign?  [1024]: ')
                                                if Question == '':
                                                    Question = 1024
                                                if re.fullmatch(r'^[0-9]{4,7}$', str(Question)):
                                                    polVars["minNum"] = 1024
                                                    polVars["maxNum"] = 1048576
                                                    polVars["varName"] = 'NFS timeo'
                                                    varValue = Question
                                                    validCount = 0
                                                    validNum = validating.number_in_range(polVars["varName"], varValue, polVars["minNum"], polVars["maxNum"])
                                                    if validNum == True:
                                                        validCount += 1
                                                    if int(Question) % 1024 == 0:
                                                        validCount += 1
                                                    else:
                                                        print(f'\n-------------------------------------------------------------------------------------------\n')
                                                        print(f'  {x} should be a divisable value of 1024 between 1024 and 1048576')
                                                        print(f'\n-------------------------------------------------------------------------------------------\n')
                                                    if validCount == 2:
                                                        valid = True
                                            xValue = '%s=%s' % (x, Question)
                                            mount_output.remove(x)
                                            mount_output.append(xValue)
                                    mount_options = ','.join(mount_output)
                                else:
                                    mount_options = ''

                                print(mount_options)

                                if Protocol == 'cifs':
                                    vmedia_map = {
                                        'authentication_protocol':authProtocol,
                                        'device_type':deviceType,
                                        'file_location':file_location,
                                        'mount_options':mount_options,
                                        'name':name,
                                        'password':Password,
                                        'protocol':Protocol,
                                        'username':Username
                                    }
                                else:
                                    vmedia_map = {
                                        'device_type':deviceType,
                                        'file_location':file_location,
                                        'mount_options':mount_options,
                                        'name':name,
                                        'password':Password,
                                        'protocol':Protocol,
                                        'username':Username
                                    }

                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                if Protocol == 'cifs':
                                    print(f'   authentication_protocol = "{authProtocol}"')
                                print(f'   device_type             = "{deviceType}"')
                                print(f'   file_location           = "{file_location}"')
                                if not mount_options == '':
                                    print(f'   mount_options           = "{mount_options}"')
                                print(f'   name                    = "{name}"')
                                if not Password == 0:
                                    print(f'   password                = "{Password}"')
                                print(f'   protocol                = "{Protocol}"')
                                if not Username == '':
                                    print(f'   username                = "{Username}"')
                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                valid_confirm = False
                                while valid_confirm == False:
                                    confirm_config = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
                                    if confirm_config == 'Y' or confirm_config == '':
                                        polVars["virtual_media"].append(vmedia_map)
                                        valid_exit = False
                                        while valid_exit == False:
                                            loop_exit = input(f'Would You like to Configure another Virtual Media Map?  Enter "Y" or "N" [N]: ')
                                            if loop_exit == 'Y':
                                                inner_loop_count += 1
                                                valid_confirm = True
                                                valid_exit = True
                                            elif loop_exit == 'N' or loop_exit == '':
                                                sub_loop = True
                                                valid_confirm = True
                                                valid_exit = True
                                                valid_sub = True
                                            else: ezfunctions.message_invalid_y_or_n('short')
                                    elif confirm_config == 'N':
                                        pol_type = 'Virtual Media Configuration'
                                        ezfunctions.message_starting_over(pol_type)
                                        valid_confirm = True
                                    else: ezfunctions.message_invalid_y_or_n('short')
                        elif question == 'N': sub_loop = True
                        else: ezfunctions.message_invalid_y_or_n('short')

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(textwrap.indent(yaml.dump(polVars, Dumper=MyDumper, default_flow_style=False), ' '*4, predicate=None))
                    print(f'-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
                        if confirm_policy == 'Y' or confirm_policy == '':
                            confirm_policy = 'Y'

                            # Write Policies to Template File
                            polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                            ezfunctions.write_to_template(self, **kwargs)

                            configure_loop, policy_loop = ezfunctions.exit_default(policy_type, 'N')
                            valid_confirm = True
                        elif confirm_policy == 'N':
                            ezfunctions.message_starting_over(policy_type)
                            valid_confirm = True
                        else: ezfunctions.message_invalid_y_or_n('short')
            elif configure == 'N': configure_loop = True
            else: ezfunctions.message_invalid_y_or_n('long')
        # Return kwargs
        return kwargs

def policy_select_loop(**kwargs):
    ezData = kwargs['ezData']
    policy = kwargs['policy']
    name_prefix = kwargs['name_prefix']
    org = kwargs['org']
    loop_valid = False
    while loop_valid == False:
        create_policy = True
        kwargs['inner_policy'] = policy.split('.')[1]
        kwargs['inner_type']   = policy.split('.')[0]
        kwargs['inner_var']    = policy.split('.')[2]
        inner_policy = kwargs['inner_policy']
        inner_type   = kwargs['inner_type']
        kwargs = ezfunctions.policies_parse(inner_type, inner_policy, **kwargs)
        if not len(kwargs['policies']) > 0:
            valid = False
            while valid == False:
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'   There was no {inner_policy} found.')
                print(f'\n-------------------------------------------------------------------------------------------\n')
                policy_description = ezfunctions.mod_pol_description(inner_policy)
                if kwargs['allow_opt_out'] == True:
                    Question = input(f'Do you want to create a(n) {policy_description}?  Enter "Y" or "N" [Y]: ')
                    if Question == '' or Question == 'Y':
                        create_policy = True
                        valid = True
                    elif Question == 'N':
                        create_policy = False
                        valid = True
                        return kwargs
                else:
                    create_policy = True
                    valid = True
        else:
            kwargs = ezfunctions.choose_policy(inner_policy, **kwargs)
            if kwargs['policy'] == 'create_policy': create_policy = True
            elif kwargs['policy'] == '' and kwargs['allow_opt_out'] == True:
                loop_valid = True
                create_policy = False
                kwargs[kwargs['inner_var']] = ''
                return kwargs
            elif not kwargs['policy'] == '':
                loop_valid = True
                create_policy = False
                kwargs[kwargs['inner_var']] = kwargs['policy']
                return kwargs

        # Simple Loop to show name_prefix in Use
        ncount = 0
        if ncount == 5: print(name_prefix)
        
        # Create Policy if Option was Selected
        if create_policy == True:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  Starting module to create {inner_policy} in {org}')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            lansan_list = ezData['ezimm']['allOf'][1]['properties']['lansan_list']['enum']
            policies_list = ezData['ezimm']['allOf'][1]['properties']['policies_list']['enum']
            profile_list = ['ucs_server_profiles', 'ucs_server_profile_templates']
            if re.search('pools$', inner_policy):
                kwargs = eval(f'pools.pools(name_prefix, org, inner_type).{inner_policy}(**kwargs)')
            elif inner_policy in lansan_list:
                kwargs = eval(f'lansan.policies(name_prefix, org, inner_type).{inner_policy}(**kwargs)')
            elif inner_policy in policies_list:
                kwargs = eval(f'policies(name_prefix, org, inner_type).{inner_policy}(**kwargs)')
            elif inner_policy in profile_list:
                kwargs = eval(f'profiles(name_prefix, org, inner_type).{inner_policy}(**kwargs)')

def port_list_eth(**kwargs):
    device_model       = kwargs["device_model"]
    jsonData           = kwargs["jsonData"]
    kwargs['portDict'] = []
    port_count         = 1
    port_type          = kwargs["port_type"]
    ports_in_use       = kwargs["ports_in_use"]
    if  len(kwargs["fc_converted_ports"]) > 0: fc_count = len(kwargs["fc_converted_ports"])
    else: fc_count = 0
    if   kwargs["device_model"] == 'UCS-FI-64108': uplinks = ezfunctions.vlan_list_full('99-108')
    elif kwargs["device_model"] == 'UCS-FI-6536': uplinks = ezfunctions.vlan_list_full('1-36')
    else: uplinks = ezfunctions.vlan_list_full('49-54')
    uplink_list = uplinks
    for item in ports_in_use:
        for i in uplink_list:
            if int(item) == int(i): uplinks.remove(i)
    if   port_type == 'Appliance Port-Channel' and device_model == 'UCS-FI-64108': portx = f'{uplinks[-4]},{uplinks[-1]}'
    elif port_type == 'Appliance Port-Channel' and device_model == 'UCS-FI-6536' : portx = f'{uplinks[1]},{uplinks[0]}'
    elif port_type == 'Appliance Port-Channel': portx = f'{uplinks[-2]},{uplinks[-1]}'
    elif port_type == 'Ethernet Uplink Port-Channel' and device_model == 'UCS-FI-64108': portx = f'{uplinks[-4]},{uplinks[-1]}'
    elif port_type == 'Ethernet Uplink Port-Channel' and device_model == 'UCS-FI-6536' : portx =f'{uplinks[1]},{uplinks[0]}'
    elif port_type == 'Ethernet Uplink Port-Channel': portx = f'{uplinks[-2]},{uplinks[-1]}'
    elif port_type == 'FCoE Uplink Port-Channel' and device_model == 'UCS-FI-64108': portx = f'{uplinks[-4]},{uplinks[-1]}'
    elif port_type == 'FCoE Uplink Port-Channel' and device_model == 'UCS-FI-6536' : portx = f'{uplinks[1]},{uplinks[0]}'
    elif port_type == 'FCoE Uplink Port-Channel': portx = f'{uplinks[-2]},{uplinks[-1]}'
    elif port_type == 'Appliance Ports' and device_model == 'UCS-FI-64108': portx = f'{uplinks[-1]}'
    elif port_type == 'Appliance Ports' and device_model == 'UCS-FI-6536' : portx = f'{uplinks[0]}'
    elif port_type == 'Appliance Ports': portx = f'{uplinks[-1]}'
    elif port_type == 'Ethernet Uplink' and device_model == 'UCS-FI-64108': portx = f'{uplinks[-1]}'
    elif port_type == 'Ethernet Uplink' and device_model == 'UCS-FI-6536' : portx = f'{uplinks[0]}'
    elif port_type == 'Ethernet Uplink': portx = f'{uplinks[-1]}'
    elif port_type == 'FCoE Uplink' and device_model == 'UCS-FI-64108': portx = f'{uplinks[-1]}'
    elif port_type == 'FCoE Uplink' and device_model == 'UCS-FI-6536' : portx = f'{uplinks[0]}'
    elif port_type == 'FCoE Uplink': portx = f'{uplinks[-1]}'
    elif port_type == 'Server Ports' and device_model == 'UCS-FI-64108': portx = f'{fc_count + 1}-36'
    elif port_type == 'Server Ports' and device_model == 'UCS-FI-6536' : portx = f'{uplinks[0]}-32'
    elif port_type == 'Server Ports': portx = f'{fc_count + 1}-18'
    if re.search('(Ethernet Uplink Port-Channel|Server Ports)', kwargs["port_type"]): default_answer = 'Y'
    else: default_answer = 'N'
    valid = False
    while valid == False:
        if kwargs["port_type"] == 'Server Ports':
            question = input(f'Do you want to configure {port_type}?  Enter "Y" or "N" [{default_answer}]: ')
        else: question = input(f'Do you want to configure an {port_type}?  Enter "Y" or "N" [{default_answer}]: ')
        if question == 'Y' or (default_answer == 'Y' and question == ''):
            configure_valid = False
            while configure_valid == False:
                print(f'\n------------------------------------------------------\n')
                print(f'  The Port List can be in the format of:')
                print(f'     5 - Single Port')
                print(f'     5-10 - Range of Ports')
                print(f'     5,11,12,13,14,15 - List of Ports')
                print(f'     5-10,20-30 - Ranges and Lists of Ports')
                print(f'\n------------------------------------------------------\n')
                port_list = input(f'Please enter the list of ports you want to add to the {port_type}?  [{portx}]: ')
                if port_list == '': port_list = portx

                if re.search(r'(^\d+$|^\d+,{1,48}\d+$|^(\d+[\-,\d+]+){1,48}\d+$)', port_list):
                    original_port_list = port_list
                    ports_expanded = ezfunctions.vlan_list_full(port_list)
                    port_list = []
                    for x in ports_expanded: port_list.append(int(x))
                    port_overlap_count = 0
                    port_overlap = []
                    for x in ports_in_use:
                        for y in port_list:
                            if int(x) == int(y):
                                port_overlap_count += 1
                                port_overlap.append(x)
                    if port_overlap_count == 0:
                        if   kwargs["device_model"] == 'UCS-FI-64108': max_port = 108
                        elif kwargs["device_model"] == 'UCS-FI-6536': max_port = 36
                        else: max_port = 54
                        if kwargs["fc_mode"] == 'Y': min_port = int(kwargs["fc_ports"][1]) + 1
                        else: min_port = 1
                        for port in port_list:
                            valid_ports = validating.number_in_range('Port Range', port, min_port, max_port)
                            if valid_ports == False: break
                        if valid_ports == True:
                            # Prompt User for the Admin Speed of the Port
                            if not kwargs["port_type"] == 'Server Ports':
                                kwargs["multi_select"] = False
                                jsonVars = jsonData['fabric.TransceiverRole']['allOf'][1]['properties']
                                kwargs['jData'] = deepcopy(jsonVars['AdminSpeed'])
                                kwargs['jData']['dontsort'] = True
                                kwargs['jData']["varType"] = 'Admin Speed'
                                admin_speed = ezfunctions.variablesFromAPI(**kwargs)
                            if re.search('^(Appliance|(Ethernet|FCoE) Uplink)$', port_type):
                                # Prompt User for the FEC Mode of the Port
                                kwargs['jData'] = deepcopy(jsonVars['AdminSpeed'])
                                kwargs['jData']["varType"] = 'Fec Mode'
                                fec = ezfunctions.variablesFromAPI(**kwargs)
                            if re.search('(Appliance)', port_type):
                                # Prompt User for the Mode of the Port
                                jsonVars = jsonData['fabric.AppliancePcRole']['allOf'][1]['properties']
                                kwargs['jData'] = deepcopy(jsonVars['Mode'])
                                kwargs['jData']["varType"] = 'Mode'
                                mode = ezfunctions.variablesFromAPI(**kwargs)

                                kwargs['jData'] = deepcopy(jsonVars['Priority'])
                                kwargs['jData']["varType"] = 'Priority'
                                priority = ezfunctions.variablesFromAPI(**kwargs)
                            # Prompt User for the
                            policy_list = []
                            if re.search('(Appliance|FCoE)', port_type):
                                policy_list.extend(['policies.ethernet_network_control.ethernet_network_control_policy'])
                            if re.search('(Appliance|Ethernet)', port_type):
                                policy_list.extend(['policies.ethernet_network_group.ethernet_network_group_policy'])
                            if re.search('(Ethernet|FCoE)', port_type):
                                policy_list.extend(['policies.link_aggregation.link_aggregation_policy'])
                            if re.search('Ethernet Uplink', port_type):
                                policy_list.extend([
                                    'policies.flow_control.flow_control_policy', 'policies.link_control.link_control_policy'
                                ])
                            kwargs["allow_opt_out"] = False
                            if not kwargs["port_type"] == 'Server Ports':
                                for i in policy_list:
                                    kwargs['policy'] = i
                                    kwargs = policy_select_loop(**kwargs)
                            interfaces = []
                            pc_id = port_list[0]
                            for i in port_list: interfaces.append({'port_id':i})
                            if port_type == 'Appliance Port-Channel':
                                port_config = {
                                    'admin_speed':admin_speed,
                                    'ethernet_network_control_policy':kwargs["ethernet_network_control_policy"],
                                    'ethernet_network_group_policy':kwargs["ethernet_network_group_policy"],
                                    'interfaces':interfaces, 'mode':kwargs["mode"], 'pc_ids':[pc_id, pc_id], 'priority':priority
                                }
                            elif port_type == 'Ethernet Uplink Port-Channel':
                                port_config = {
                                    'admin_speed':admin_speed,
                                    'ethernet_network_group_policy':kwargs["ethernet_network_group_policy"],
                                    'flow_control_policy':kwargs["flow_control_policy"],
                                    'interfaces':interfaces, 'link_aggregation_policy':kwargs["link_aggregation_policy"],
                                    'link_control_policy':kwargs["link_control_policy"], 'pc_ids':[pc_id, pc_id]
                                }
                            elif port_type == 'FCoE Uplink Port-Channel':
                                port_config = {
                                    'admin_speed':admin_speed, 'interfaces':interfaces,
                                    'link_aggregation_policy':kwargs["link_aggregation_policy"],
                                    'link_control_policy':kwargs["link_control_policy"],
                                    'pc_ids':[pc_id, pc_id]
                                }
                            elif port_type == 'Appliance Ports':
                                port_config = {
                                    'admin_speed':admin_speed,
                                    'ethernet_network_control_policy':kwargs["ethernet_network_control_policy"],
                                    'ethernet_network_group_policy':kwargs["ethernet_network_group_policy"],
                                    'fec':fec, 'mode':kwargs["mode"], 'port_list':original_port_list, 'priority':priority
                                }
                            elif port_type == 'Ethernet Uplink':
                                port_config = {
                                    'admin_speed':admin_speed,
                                    'ethernet_network_group_policy':kwargs["ethernet_network_group_policy"],
                                    'fec':fec, 'flow_control_policy':kwargs["flow_control_policy"],
                                    'link_control_policy':kwargs["link_control_policy"], 'port_list':original_port_list
                                }
                            elif port_type == 'FCoE Uplink':
                                port_config = {
                                    'admin_speed':admin_speed, 'fec':fec,
                                    'link_control_policy':kwargs["link_control_policy"],
                                    'port_list':original_port_list
                                }
                            elif port_type == 'Server Ports': port_config = {'port_list':original_port_list}
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            print(textwrap.indent(yaml.dump({port_type:port_config}, Dumper=MyDumper, default_flow_style=False
                            ), " "*4, predicate=None))
                            print(f'-------------------------------------------------------------------------------------------\n')
                            valid_confirm = False
                            while valid_confirm == False:
                                confirm_port = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                                if confirm_port == 'Y' or confirm_port == '':
                                    kwargs['portDict'].append(port_config)
                                    for i in port_list:
                                        kwargs["ports_in_use"].append(i)

                                    valid_exit = False
                                    while valid_exit == False:
                                        port_exit = input(f'Would You like to Configure another {port_type}?  Enter "Y" or "N" [N]: ')
                                        if port_exit == 'Y':
                                            port_count += 1
                                            valid_confirm = True
                                            valid_exit = True
                                        elif port_exit == 'N' or port_exit == '':
                                            configure_valid = True
                                            valid = True
                                            valid_confirm = True
                                            valid_exit = True
                                        else: ezfunctions.message_invalid_y_or_n('short')
                                elif confirm_port == 'N':
                                    ezfunctions.message_starting_over(port_type)
                                    valid_confirm = True
                                else: ezfunctions.message_invalid_y_or_n('short')
                    else:
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        print(f'  Error!! The following Ports are already in use: {port_overlap}.')
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                else:
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  Error!! Invalid Port Range.  A port Range should be in the format 49-50 for example.')
                    print(f'  The following port range is invalid: "{port_list}"')
                    print(f'\n-------------------------------------------------------------------------------------------\n')

        elif question == 'N'  or (default_answer == 'N' and question == ''): valid = True
        else: ezfunctions.message_invalid_y_or_n('short')
    # Return kwargs
    return kwargs
    
def port_list_fc(**kwargs):
    jsonData  = kwargs['jsonData']
    org       = kwargs['org']
    port_type = kwargs['port_type']
    fill_pattern_descr = 'For Cisco UCS 6400 Series fabric interconnect, if the FC uplink speed is 8 Gbps, set the '\
        'fill pattern as IDLE on the uplink switch. If the fill pattern is not set as IDLE, FC '\
        'uplinks operating at 8 Gbps might go to an errDisabled state, lose SYNC intermittently, or '\
        'notice errors or bad packets.  For speeds greater than 8 Gbps we recommend Arbff.  Below '\
        'is a configuration example on MDS to match this setting:\n\n'\
        'mds-a(config-if)# switchport fill-pattern IDLE speed 8000\n'\
        'mds-a(config-if)# show port internal inf interface fc1/1 | grep FILL\n'\
        '  FC_PORT_CAP_FILL_PATTERN_8G_CHANGE_CAPABLE (1)\n'\
        'mds-a(config-if)# show run int fc1/16 | incl fill\n\n'\
        'interface fc1/16\n'\
        '  switchport fill-pattern IDLE speed 8000\n\n'\
        'mds-a(config-if)#\n'

    if port_type == 'Fibre-Channel Port-Channel': default_answer = 'Y'
    else: default_answer = 'N'
    port_count = 1
    if len(kwargs["fc_converted_ports"]) > 0: configure_fc = True
    else: configure_fc = False
    if configure_fc == True:
        valid = False
        while valid == False:
            question = input(f'Do you want to configure a {port_type}?  Enter "Y" or "N" [{default_answer}]: ')
            if question == 'Y' or (default_answer == 'Y' and question == ''):
                configure_valid = False
                while configure_valid == False:
                    if port_type == 'Fibre-Channel Port-Channel':
                        kwargs["multi_select"] = True
                        kwargs["Description"] = '    Please Select a Port for the Port-Channel:\n'
                    elif port_type == 'Fibre-Channel Storage':
                        kwargs["multi_select"] = False
                        kwargs["Description"] = '    Please Select a Port for the Storage Port:\n'
                    else:
                        kwargs["multi_select"] = False
                        kwargs["Description"] = '    Please Select a Port for the Uplink Port:\n'
                    kwargs["var_type"] = 'Unified Port'
                    port_list = ezfunctions.vars_from_list(kwargs["fc_converted_ports"], **kwargs)

                    # Prompt User for the Admin Speed of the Port
                    kwargs["multi_select"] = False
                    jsonVars = jsonData['fabric.FcUplinkPcRole']['allOf'][1]['properties']
                    kwargs['jData'] = deepcopy(jsonVars['AdminSpeed'])
                    kwargs['jData']['enum'].remove('Auto')
                    kwargs['jData']["default"] = kwargs['jData']['enum'][2]
                    kwargs['jData']['dontsort'] = True
                    kwargs['jData']["varType"] = 'Admin Speed'
                    admin_speed = ezfunctions.variablesFromAPI(**kwargs)

                    # Prompt User for the Fill Pattern of the Port
                    if not port_type == 'Fibre-Channel Storage':
                        kwargs['jData'] = deepcopy(jsonVars['FillPattern'])
                        kwargs['jData']["description"] = kwargs['jData']["description"] + '\n' + fill_pattern_descr
                        kwargs['jData']["default"] = kwargs['jData']['enum'][1]
                        kwargs['jData']["varType"] = 'Fill Pattern'
                        fill_pattern = ezfunctions.variablesFromAPI(**kwargs)

                    vsans = {}
                    fabrics = ['Fabric_A', 'Fabric_B']
                    for fabric in fabrics:
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        print(f'  Please Select the VSAN Policy for {fabric}')
                        kwargs["allow_opt_out"] = False
                        kwargs['policy'] = 'policies.vsan.vsan_policy'
                        kwargs = policy_select_loop(**kwargs)
                        print(kwargs['vsan_policy'])
                        vsan_list = []
                        for i in kwargs['immDict']['orgs'][org]['intersight']['policies']['vsan']:
                            if i['name'] == kwargs['vsan_policy']:
                                for item in i['vsans']: vsan_list.append(item['vsan_id'])
                        if len(vsan_list) > 1: vsan_list = ','.join(str(vsan_list))
                        else: vsan_list = vsan_list[0]
                        vsan_list = ezfunctions.vlan_list_full(vsan_list)

                        kwargs["multi_select"] = False
                        if port_type == 'Fibre-Channel Port-Channel': fc_type = 'Port-Channel'
                        elif port_type == 'Fibre-Channel Storage': fc_type = 'Storage Port'
                        else: fc_type = 'Uplink Port'
                        kwargs["Description"] = f'    Please Select a VSAN for the Fibre-Channel {fc_type} Port:\n'
                        kwargs["var_type"] = 'VSAN'
                        vsan_x = ezfunctions.vars_from_list(vsan_list, **kwargs)
                        for vs in vsan_x: vsan = vs
                        vsans.update({fabric:vsan})
                    if port_type == 'Fibre-Channel Port-Channel':
                        interfaces = []
                        for i in port_list: interfaces.append({'port_id':i})
                        pc_id = port_list[0]
                        port_config = {
                            'admin_speed':admin_speed, 'fill_pattern':fill_pattern, 'interfaces':interfaces,
                            'pc_ids':[pc_id, pc_id], 'vsan_ids':[vsans.get("Fabric_A"), vsans.get("Fabric_B")]
                        }
                    elif port_type == 'Fibre-Channel Storage':
                        port_list = '%s' % (port_list[0])
                        port_config = {
                            'admin_speed':admin_speed, 'port_id':port_list, 'slot_id':1,
                            'vsan_ids':[vsans.get("Fabric_A"), vsans.get("Fabric_B")]
                        }
                    else:
                        port_list = '%s' % (port_list[0])
                        port_config = {
                            'admin_speed':admin_speed, 'fill_pattern':fill_pattern, 'port_id':port_list,
                            'slot_id':1, 'vsan_id':[vsans.get("Fabric_A"), vsans.get("Fabric_B")]
                        }
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(textwrap.indent(yaml.dump({port_type:port_config}, Dumper=MyDumper, default_flow_style=False
                    ), " "*4, predicate=None))
                    print(f'-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_port = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                        if confirm_port == 'Y' or confirm_port == '':
                            kwargs['portDict'].append(port_config)
                            for i in port_list: kwargs['fc_ports_in_use'].append(i)
                            valid_exit = False
                            while valid_exit == False:
                                port_exit = input(f'Would You like to Configure another {port_type}?  Enter "Y" or "N" [N]: ')
                                if port_exit == 'Y':
                                    port_count += 1
                                    valid_confirm = True
                                    valid_exit = True
                                elif port_exit == 'N' or port_exit == '':
                                    configure_valid = True
                                    valid = True
                                    valid_confirm = True
                                    valid_exit = True
                                else: ezfunctions.message_invalid_y_or_n('short')
                        elif confirm_port == 'N':
                            ezfunctions.message_starting_over(port_type)
                            valid_confirm = True
                        else: ezfunctions.message_invalid_y_or_n('short')
            elif question == 'N' or (default_answer == 'N' and question == ''): valid = True
            else: ezfunctions.message_invalid_y_or_n('short')
    # Return kwargs
    return kwargs

def port_modes_fc(**kwargs):
    ezData             = kwargs["ezData"]
    fc_converted_ports = []
    port_modes         = {}
    ports_in_use       = []
    valid = False
    while valid == False:
        fc_mode = input('Do you want to convert ports to Fibre-Channel Mode?  Enter "Y" or "N" [Y]: ')
        if fc_mode == '' or fc_mode == 'Y':
            fc_mode = 'Y'
            if kwargs['device_model'] == 'UCS-FI-6536':
                jsonVars   = ezData['ezimm']['allOf'][1]['properties']['policies']['fabric.PortPolicy_Gen5']
            else: jsonVars = ezData['ezimm']['allOf'][1]['properties']['policies']['fabric.PortPolicy_Gen4']
            kwargs['jData'] = deepcopy(jsonVars['unifiedPorts'])
            kwargs['jData']['dontsort'] = True
            kwargs['jData']["varType"] = 'Unified Port Ranges'
            fc_ports = ezfunctions.variablesFromAPI(**kwargs)
            x = fc_ports.split('-')
            fc_ports = [int(x[0]),int(x[1])]
            for i in range(int(x[0]), int(x[1]) + 1):
                ports_in_use.append(i)
                fc_converted_ports.append(i)
            if kwargs['device_model'] == 'UCS-FI-6536':
                port_modes = {'custom_mode':'BreakoutFibreChannel32G','port_list':fc_ports,}
            else: port_modes = {'custom_mode':'FibreChannel','port_list':fc_ports,}
            valid = True
        elif fc_mode == 'N':
            fc_ports = []
            port_modes = {}
            valid = True
        else: ezfunctions.message_invalid_y_or_n('short')
    # Return kwargs
    kwargs['fc_converted_ports'] = fc_converted_ports
    kwargs['fc_mode']    = fc_mode
    kwargs['fc_ports']   = fc_ports
    kwargs['port_modes'] = port_modes
    kwargs['ports_in_use'] = ports_in_use
    return kwargs
