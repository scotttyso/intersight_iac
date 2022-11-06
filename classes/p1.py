#!/usr/bin/env python3
from textwrap import fill
import base64
import lan
import san
import vxan
import pools
import ezfunctions
import jinja2
import json
import os
import pkg_resources
import platform
import re
import stdiomask
import validating

ucs_template_path = pkg_resources.resource_filename('p1', '../templates/')

class policies(object):
    def __init__(self, name_prefix, org, type):
        self.templateLoader = jinja2.FileSystemLoader(
            searchpath=(ucs_template_path + '%s/') % (type))
        self.templateEnv = jinja2.Environment(loader=self.templateLoader)
        self.name_prefix = name_prefix
        self.org = org
        self.type = type

    #==============================================
    # Adapter Configuration Policy Module
    #==============================================
    def adapter_configuration_policies(self, jsonData, easy_jsonData, **kwargs):
        name_prefix = self.name_prefix
        name_suffix = 'adapter'
        opSystem = kwargs['opSystem']
        org = self.org
        policy_type = 'Adapter Configuration Policy'
        polVars = {}
        polVars["header"] = '%s Variables' % (policy_type)
        polVars["initial_write"] = True
        polVars["org"] = org
        polVars["policy_type"] = policy_type
        polVars["template_file"] = 'template_open.jinja2'
        polVars["template_type"] = 'adapter_configuration_policies'
        tfDir = kwargs['tfDir']

        # Open the Template file
        ezfunctions.write_to_template(self, **polVars)
        polVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  An {policy_type} configures the Ethernet and Fibre-Channel settings for the ')
            print(f'  Virtual Interface Card (VIC) adapter.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            if opSystem == 'Windows':
                print(f'  - {tfDir}\\{org}\\{self.type}\\{polVars["template_type"]}.auto.tfvars')
            else:
                print(f'  - {tfDir}/{org}/{self.type}/{polVars["template_type"]}.auto.tfvars')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure an {policy_type}?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                policy_loop = False
                while policy_loop == False:

                    if not name_prefix == '':
                        name = '%s_%s' % (name_prefix, name_suffix)
                    else:
                        name = '%s_%s' % (org, name_suffix)

                    polVars["name"] = ezfunctions.policy_name(name, policy_type)
                    polVars["descr"] = ezfunctions.policy_descr(polVars["name"], policy_type)

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  If Selected, then FCoE Initialization Protocol (FIP) mode is enabled. FIP mode ensures ')
                    print(f'  that the adapter is compatible with current FCoE standards.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid = False
                    while valid == False:
                        Question = input('Do you want to Enable FIP on the VIC?  Enter "Y" or "N" [Y]: ')
                        if Question == '' or Question == 'Y':
                            polVars["enable_fip"] = True
                            valid = True
                        elif Question == 'N':
                            polVars["enable_fip"] = False
                            valid = True
                        else:
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                            print(f'\n-------------------------------------------------------------------------------------------\n')

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  If Selected, then Link Layer Discovery Protocol (LLDP) enables all the Data Center ')
                    print(f'  Bridging Capability Exchange protocol (DCBX) functionality, which includes FCoE,')
                    print(f'  priority based flow control.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid = False
                    while valid == False:
                        Question = input('Do you want to Enable LLDP on the VIC?  Enter "Y" or "N" [Y]: ')
                        if Question == '' or Question == 'Y':
                            polVars["enable_lldp"] = True
                            valid = True
                        elif Question == 'N':
                            polVars["enable_lldp"] = False
                            valid = True
                        else:
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                            print(f'\n-------------------------------------------------------------------------------------------\n')

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  When Port Channel is enabled, two vNICs and two vHBAs are available for use on the adapter')
                    print(f'  card.  When disabled, four vNICs and four vHBAs are available for use on the adapter card.')
                    print(f'  Disabling port channel reboots the server. Port Channel is supported only for')
                    print(f'  Cisco 4th Gen VIC Adapters with 4 interfaces.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid = False
                    while valid == False:
                        Question = input('Do you want to Enable Port-Channel on the VIC?  Enter "Y" or "N" [Y]: ')
                        if Question == '' or Question == 'Y':
                            polVars["enable_port_channel"] = True
                            valid = True
                        elif Question == 'N':
                            polVars["enable_port_channel"] = False
                            valid = True
                        else:
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                            print(f'\n-------------------------------------------------------------------------------------------\n')

                    intList = [1, 2, 3, 4]
                    for x in intList:
                        polVars["multi_select"] = False
                        jsonVars = jsonData['components']['schemas']['adapter.DceInterfaceSettings']['allOf'][1]['properties']
                        polVars["var_description"] = jsonVars['FecMode']['description']
                        polVars["jsonVars"] = sorted(jsonVars['FecMode']['enum'])
                        polVars["defaultVar"] = jsonVars['FecMode']['default']
                        polVars["varType"] = f'DCE Interface {x} FEC Mode'
                        intFec = f'fec_mode_{x}'
                        polVars[intFec] = ezfunctions.variablesFromAPI(**polVars)

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'    description         = "{polVars["descr"]}"')
                    print(f'    enable_fip          = {polVars["enable_fip"]}')
                    print(f'    enable_lldp         = {polVars["enable_lldp"]}')
                    print(f'    enable_port_channel = {polVars["enable_port_channel"]}')
                    print(f'    fec_mode_1          = "{polVars["fec_mode_1"]}"')
                    print(f'    fec_mode_2          = "{polVars["fec_mode_2"]}"')
                    print(f'    fec_mode_3          = "{polVars["fec_mode_3"]}"')
                    print(f'    fec_mode_4          = "{polVars["fec_mode_4"]}"')
                    print(f'    name                = "{polVars["name"]}"')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
                        if confirm_policy == 'Y' or confirm_policy == '':
                            confirm_policy = 'Y'

                            # Write Policies to Template File
                            polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                            ezfunctions.write_to_template(self, **polVars)

                            configure_loop, policy_loop = ezfunctions.exit_default_no(polVars["policy_type"])
                            valid_confirm = True

                        elif confirm_policy == 'N':
                            print(f'\n------------------------------------------------------\n')
                            print(f'  Starting {polVars["policy_type"]} Section over.')
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
        polVars["template_file"] = 'template_close.jinja2'
        ezfunctions.write_to_template(self, **polVars)

    #==============================================
    # BIOS Policy Module
    #==============================================
    def bios_policies(self, jsonData, easy_jsonData, **kwargs):
        name_prefix = self.name_prefix
        opSystem = kwargs['opSystem']
        org = self.org
        policy_type = 'BIOS Policy'
        policy_x = 'BIOS'
        polVars = {}
        polVars["header"] = '%s Variables' % (policy_type)
        polVars["initial_write"] = True
        polVars["name_prefix"] = name_prefix
        polVars["org"] = org
        polVars["policy_type"] = policy_type
        polVars["template_file"] = 'template_open.jinja2'
        polVars["template_type"] = 'bios_policies'
        tfDir = kwargs['tfDir']

        # Open the Template file
        ezfunctions.write_to_template(self, **polVars)
        polVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  {policy_x} Policies:  To simplify your work, this wizard will use {policy_x}')
            print(f'  Templates that are pre-configured.  You can add custom {policy_x} policy')
            print(f'  configuration to the {polVars["template_type"]}.auto.tfvars file at your descretion.')
            print(f'  That will not be covered by this wizard as the focus of the wizard is on simplicity.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            if opSystem == 'Windows':
                print(f'  - {tfDir}\\{org}\\{self.type}\\{polVars["template_type"]}.auto.tfvars')
            else:
                print(f'  - {tfDir}/{org}/{self.type}/{polVars["template_type"]}.auto.tfvars')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure a {policy_type}?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                policy_loop = False
                while policy_loop == False:

                    polVars["multi_select"] = False
                    jsonVars = easy_jsonData['policies']['bios.Policy']
                    polVars["var_description"] = jsonVars['templates']['description']
                    polVars["jsonVars"] = sorted(jsonVars['templates']['enum'])
                    polVars["defaultVar"] = jsonVars['templates']['default']
                    polVars["varType"] = 'BIOS Template'
                    polVars["policy_template"] = ezfunctions.variablesFromAPI(**polVars)

                    if not polVars["name_prefix"] == '':
                        name = '%s_%s' % (polVars["name_prefix"], polVars["policy_template"])
                    else:
                        name = '%s_%s' % (polVars["org"], polVars["policy_template"])

                    polVars["name"] = ezfunctions.policy_name(name, polVars["policy_type"])
                    polVars["descr"] = ezfunctions.policy_descr(polVars["name"], polVars["policy_type"])

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'   bios_template = "{polVars["policy_template"]}"')
                    print(f'   description   = "{polVars["descr"]}"')
                    print(f'   name          = "{polVars["name"]}"')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
                        if confirm_policy == 'Y' or confirm_policy == '':
                            confirm_policy = 'Y'

                            # Write Policies to Template File
                            polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                            ezfunctions.write_to_template(self, **polVars)

                            configure_loop, policy_loop = ezfunctions.exit_default_yes(polVars["policy_type"])
                            valid_confirm = True

                        elif confirm_policy == 'N':
                            print(f'\n------------------------------------------------------\n')
                            print(f'  Starting {polVars["policy_type"]} Section over.')
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
        polVars["template_file"] = 'template_close.jinja2'
        ezfunctions.write_to_template(self, **polVars)

    #==============================================
    # Boot Order Policy Module
    #==============================================
    def boot_order_policies(self, jsonData, easy_jsonData, **kwargs):
        name_prefix = self.name_prefix
        name_suffix = 'boot_order'
        opSystem = kwargs['opSystem']
        org = self.org
        policy_type = 'Boot Order Policy'
        polVars = {}
        polVars["header"] = '%s Variables' % (policy_type)
        polVars["initial_write"] = True
        polVars["org"] = org
        polVars["policy_type"] = policy_type
        polVars["template_file"] = 'template_open.jinja2'
        polVars["template_type"] = 'boot_order_policies'
        tfDir = kwargs['tfDir']

        # Open the Template file
        ezfunctions.write_to_template(self, **polVars)
        polVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  A {policy_type} configures the linear ordering of devices and enables you to change ')
            print(f'  the boot order and boot mode. You can also add multiple devices under various device types,')
            print(f'  rearrange the boot order, and set parameters for each boot device type.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            if opSystem == 'Windows':
                print(f'  - {tfDir}\\{org}\\{self.type}\\{polVars["template_type"]}.auto.tfvars')
            else:
                print(f'  - {tfDir}/{org}/{self.type}/{polVars["template_type"]}.auto.tfvars')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure a {policy_type}.  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                policy_loop = False
                while policy_loop == False:

                    if not name_prefix == '':
                        name = '%s_%s' % (name_prefix, name_suffix)
                    else:
                        name = '%s_%s' % (org, name_suffix)

                    polVars["name"] = ezfunctions.policy_name(name, policy_type)
                    polVars["descr"] = ezfunctions.policy_descr(polVars["name"], policy_type)

                    # Pull in the Policies for iSCSI Boot
                    jsonVars = jsonData['components']['schemas']['boot.PrecisionPolicy']['allOf'][1]['properties']
                    polVars["multi_select"] = False

                    # Configured Boot Mode
                    polVars["var_description"] = jsonVars['ConfiguredBootMode']['description']
                    polVars["jsonVars"] = sorted(jsonVars['ConfiguredBootMode']['enum'])
                    polVars["defaultVar"] = jsonVars['ConfiguredBootMode']['default']
                    polVars["varType"] = 'Configured Boot Mode'
                    polVars["boot_mode"] = ezfunctions.variablesFromAPI(**polVars)

                    if polVars["boot_mode"] == 'Uefi':
                        # Enforce Uefi SecureBoot
                        polVars["Description"] = jsonVars['EnforceUefiSecureBoot']['description']
                        polVars["varInput"] = f'Do you want to Enforce Uefi Secure Boot?'
                        polVars["varDefault"] = 'Y'
                        polVars["varName"] = 'Uefi SecureBoot'
                        polVars["enable_secure_boot"] = ezfunctions.varBoolLoop(**polVars)
                    else:
                        polVars["enable_secure_boot"] = False


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
                                jsonVars = jsonData['components']['schemas']['boot.DeviceBase']['allOf'][1]['properties']

                                # Configured Boot Mode
                                polVars["var_description"] = 'Select the Type of Boot Device to configure.'
                                polVars["jsonVars"] = sorted(jsonVars['ClassId']['enum'])
                                polVars["defaultVar"] = 'boot.LocalDisk'
                                polVars["varType"] = 'Boot Device Class ID'
                                objectType = ezfunctions.variablesFromAPI(**polVars)

                                polVars["Description"] = jsonVars['Name']['description']
                                polVars["varDefault"] = ''
                                polVars["varInput"] = 'Boot Device Name:'
                                polVars["varName"] = 'Boot Device Name'
                                polVars["varRegex"] = jsonVars['Name']['pattern']
                                polVars["minLength"] = 1
                                polVars["maxLength"] = 30
                                device_name = ezfunctions.varStringLoop(**polVars)

                                boot_device = {
                                    "enabled":True,
                                    "device_name":device_name,
                                    "object_type":objectType
                                }

                                if objectType == 'boot.Iscsi':
                                    device_type = 'iscsi_boot'
                                    jsonVars = jsonData['components']['schemas']['boot.Iscsi']['allOf'][1]['properties']
                                elif objectType == 'boot.LocalCdd':
                                    device_type = 'local_cdd'
                                elif objectType == 'boot.LocalDisk':
                                    device_type = 'local_disk'
                                    jsonVars = jsonData['components']['schemas']['boot.LocalDisk']['allOf'][1]['properties']
                                elif objectType == 'boot.Nvme':
                                    device_type = 'nvme'
                                    jsonVars = jsonData['components']['schemas']['boot.Nvme']['allOf'][1]['properties']
                                elif objectType == 'boot.PchStorage':
                                    device_type = 'pch_storage'
                                    jsonVars = jsonData['components']['schemas']['boot.PchStorage']['allOf'][1]['properties']
                                elif objectType == 'boot.Pxe':
                                    device_type = 'pxe_boot'
                                    jsonVars = jsonData['components']['schemas']['boot.Pxe']['allOf'][1]['properties']
                                elif objectType == 'boot.San':
                                    device_type = 'san_boot'
                                    jsonVars = jsonData['components']['schemas']['boot.San']['allOf'][1]['properties']
                                elif objectType == 'boot.SdCard':
                                    device_type = 'sd_card'
                                    jsonVars = jsonData['components']['schemas']['boot.SdCard']['allOf'][1]['properties']
                                elif objectType == 'boot.UefiShell':
                                    device_type = 'uefi_shell'
                                    jsonVars = jsonData['components']['schemas']['boot.UefiShell']['allOf'][1]['properties']
                                elif objectType == 'boot.Usb':
                                    device_type = 'usb'
                                    jsonVars = jsonData['components']['schemas']['boot.Usb']['allOf'][1]['properties']
                                elif objectType == 'boot.VirtualMedia':
                                    device_type = 'virtual_media'
                                    jsonVars = jsonData['components']['schemas']['boot.VirtualMedia']['allOf'][1]['properties']

                                boot_device.update({'device_type':device_type})

                                if polVars["boot_mode"] == 'Uefi' and re.fullmatch('boot\.(Iscsi|LocalDisk|Nvme|PchStorage|San|SdCard)', objectType):
                                    addLoader = {
                                        "bootloader_description":"Uefi Bootloader",
                                        "bootloader_name":"BOOTX64.EFI",
                                        "bootloader_path":"\\\\EFI\\\\BOOT\\\\"
                                    }
                                    boot_device.update(addLoader)

                                if objectType == 'boot.LocalDisk':
                                    polVars["multi_select"] = False
                                    jsonVars = jsonData['components']['schemas']['vnic.EthNetworkPolicy']['allOf'][1]['properties']
                                    polVars["var_description"] = jsonVars['TargetPlatform']['description']
                                    polVars["jsonVars"] = sorted(jsonVars['TargetPlatform']['enum'])
                                    polVars["defaultVar"] = jsonVars['TargetPlatform']['default']
                                    polVars["varType"] = 'Target Platform'
                                    target_platform = ezfunctions.variablesFromAPI(**polVars)

                                    # Slot
                                    jsonVars = jsonData['components']['schemas']['boot.LocalDisk']['allOf'][1]['properties']
                                    polVars["var_description"] = jsonVars['Slot']['description']
                                    polVars["jsonVars"] = easy_jsonData['policies']['boot.PrecisionPolicy']['boot.Localdisk'][target_platform]
                                    polVars["defaultVar"] = easy_jsonData['policies']['boot.PrecisionPolicy']['boot.Localdisk']['default']
                                    polVars["varType"] = 'Slot'
                                    Slot = ezfunctions.variablesFromAPI(**polVars)

                                    if re.search('[0-9]+', Slot):
                                        polVars["Description"] = 'Slot Number between 1 and 205.'
                                        polVars["varDefault"] =  1
                                        polVars["varInput"] = 'Slot ID of the Localdisk:'
                                        polVars["varName"] = 'Slot'
                                        polVars["varRegex"] = '[0-9]+'
                                        polVars["minNum"] = 1
                                        polVars["maxNum"] = 205
                                        Slot = ezfunctions.varNumberLoop(**polVars)

                                    localDisk = {'slot':Slot}
                                    boot_device.update(localDisk)

                                if objectType == 'boot.Pxe':
                                    # IPv4 or IPv6
                                    polVars["var_description"] = jsonVars['IpType']['description']
                                    polVars["jsonVars"] = sorted(jsonVars['IpType']['enum'])
                                    polVars["defaultVar"] = jsonVars['IpType']['default']
                                    polVars["varType"] = 'IP Type'
                                    IpType = ezfunctions.variablesFromAPI(**polVars)

                                    # Interface Source
                                    polVars["var_description"] = jsonVars['InterfaceSource']['description']
                                    polVars["jsonVars"] = sorted(jsonVars['InterfaceSource']['enum'])
                                    polVars["defaultVar"] = jsonVars['InterfaceSource']['default']
                                    polVars["varType"] = 'Interface Source'
                                    InterfaceSource = ezfunctions.variablesFromAPI(**polVars)

                                if objectType == 'boot.Iscsi' or (objectType == 'boot.Pxe' and InterfaceSource == 'name'):
                                    policy_list = [
                                        'policies.lan_connectivity_policies.lan_connectivity_policy',
                                    ]
                                    polVars["allow_opt_out"] = False
                                    for policy in policy_list:
                                        lan_connectivity_policy,policyData = policy_select_loop(jsonData, easy_jsonData, name_prefix, policy, **polVars)
                                    vnicNames = []
                                    for x in policyData['lan_connectivity_policies']:
                                        for keys, values in x.items():
                                            if keys == lan_connectivity_policy:
                                                for i in values[0]['vnics']:
                                                    for k, v in i.items():
                                                        vnicNames.append(k)

                                                polVars["var_description"] = 'LAN Connectivity vNIC Names.'
                                                polVars["jsonVars"] = sorted(vnicNames)
                                                polVars["defaultVar"] = ''
                                                polVars["varType"] = 'vNIC Names'
                                                vnicTemplate = ezfunctions.variablesFromAPI(**polVars)
                                                InterfaceName = values[0]['vnics'][0][vnicTemplate][0]['name']
                                                Slot = values[0]['vnics'][0][vnicTemplate][0]['placement_slot_id']

                                    if objectType == 'boot.Iscsi':
                                        Port = 0
                                    else:
                                        Port = -1
                                        MacAddress = ''

                                if objectType == 'boot.Pxe':
                                    if InterfaceSource == 'mac':
                                        polVars["Description"] = jsonVars['MacAddress']['description']
                                        polVars["varDefault"] = ''
                                        polVars["varInput"] = 'The MAC Address of the adapter on the underlying Virtual NIC:'
                                        polVars["varName"] = 'Mac Address'
                                        polVars["varRegex"] = jsonVars['MacAddress']['pattern']
                                        polVars["minLength"] = 17
                                        polVars["maxLength"] = 17
                                        MacAddress = ezfunctions.varStringLoop(**polVars)
                                        InterfaceName = ''
                                        Port = -1
                                    elif InterfaceSource == 'port':
                                        polVars["Description"] = jsonVars['Port']['description']
                                        polVars["varDefault"] =  jsonVars['Port']['default']
                                        polVars["varInput"] = 'The Port ID of the adapter on the underlying Virtual NIC:'
                                        polVars["varName"] = 'Port'
                                        polVars["varRegex"] = jsonVars['Port']['pattern']
                                        polVars["minNum"] = 1
                                        polVars["maxNum"] = 3
                                        Port = ezfunctions.varNumberLoop(**polVars)
                                        InterfaceName = ''
                                        MacAddress = ''

                                    if not InterfaceSource == 'name':
                                        polVars["Description"] = jsonVars['Slot']['description']
                                        polVars["varDefault"] = 'MLOM'
                                        polVars["varInput"] = 'The Slot ID of the adapter on the underlying Virtual NIC:'
                                        polVars["varName"] = 'Slot'
                                        polVars["varRegex"] = jsonVars['Slot']['pattern']
                                        polVars["minLength"] = 1
                                        polVars["maxLength"] = 4
                                        Slot = ezfunctions.varStringLoop(**polVars)

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
                                    jsonVars = jsonData['components']['schemas']['boot.Iscsi']['allOf'][1]['properties']

                                    # Port
                                    polVars["Description"] = jsonVars['Port']['description']
                                    polVars["varInput"] = 'Enter the Port ID of the Adapter:'
                                    polVars["varDefault"] = jsonVars['Port']['description']
                                    polVars["varName"] = 'Port'
                                    polVars["minNum"] = jsonVars['Port']['minimum']
                                    polVars["maxNum"] = jsonVars['Port']['maximum']
                                    polVars["port"] = ezfunctions.varNumberLoop(**polVars)

                                if re.fullmatch('boot\.(PchStorage|San|SdCard)', objectType):
                                    polVars["Description"] = jsonVars['Lun']['description']
                                    polVars["varDefault"] =  jsonVars['Lun']['default']
                                    polVars["varInput"] = 'LUN Identifier:'
                                    polVars["varName"] = 'LUN ID'
                                    polVars["varRegex"] = '[\\d]+'
                                    polVars["minNum"] = jsonVars['Lun']['minimum']
                                    polVars["maxNum"] = jsonVars['Lun']['maximum']
                                    Lun = ezfunctions.varNumberLoop(**polVars)
                                    boot_device.update({'lun':Lun})

                                if objectType == 'boot.San':
                                    policy_list = [
                                        'policies.san_connectivity_policies.san_connectivity_policy',
                                    ]
                                    polVars["allow_opt_out"] = False
                                    for policy in policy_list:
                                        san_connectivity_policy,policyData = policy_select_loop(jsonData, easy_jsonData, name_prefix, policy, **polVars)
                                    vnicNames = []
                                    for x in policyData['san_connectivity_policies']:
                                        for keys, values in x.items():
                                            if keys == san_connectivity_policy:
                                                for i in values[0]['vhbas']:
                                                    for k, v in i.items():
                                                        vnicNames.append(k)

                                                polVars["var_description"] = 'SAN Connectivity vNIC Names.'
                                                polVars["jsonVars"] = sorted(vnicNames)
                                                polVars["defaultVar"] = ''
                                                polVars["varType"] = 'vHBA Names'
                                                vnicTemplate = ezfunctions.variablesFromAPI(**polVars)
                                                InterfaceName = values[0]['vhbas'][0][vnicTemplate][0]['name']
                                                Slot = values[0]['vhbas'][0][vnicTemplate][0]['placement_slot_id']

                                    polVars["Description"] = jsonVars['Wwpn']['description']
                                    polVars["varDefault"] = ''
                                    polVars["varInput"] = 'WWPN of the Target Appliance:'
                                    polVars["varName"] = 'WWPN'
                                    polVars["varRegex"] = jsonVars['Wwpn']['pattern']
                                    polVars["minLength"] = 23
                                    polVars["maxLength"] = 23
                                    Wwpn = ezfunctions.varStringLoop(**polVars)

                                    targetWwpn = {'target_wwpn':Wwpn}
                                    boot_device.update(targetWwpn)

                                if re.fullmatch('boot\.(SdCard|Usb|VirtualMedia)', objectType):
                                    if objectType == 'boot.SdCard':
                                        # Pull in the Sub Types for Virtual Media
                                        jsonVars = jsonData['components']['schemas']['boot.SdCard']['allOf'][1]['properties']
                                    elif objectType == 'boot.Usb':
                                        # Pull in the Sub Types for Virtual Media
                                        jsonVars = jsonData['components']['schemas']['boot.Usb']['allOf'][1]['properties']
                                    elif objectType == 'boot.VirtualMedia':
                                        # Pull in the Sub Types for Virtual Media
                                        jsonVars = jsonData['components']['schemas']['boot.VirtualMedia']['allOf'][1]['properties']

                                    # Configured Boot Mode
                                    polVars["var_description"] = jsonVars['Subtype']['description']
                                    polVars["jsonVars"] = sorted(jsonVars['Subtype']['enum'])
                                    polVars["defaultVar"] = jsonVars['Subtype']['default']
                                    polVars["varType"] = 'Sub type'
                                    Subtype = ezfunctions.variablesFromAPI(**polVars)

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
                                            else:
                                                print(f'\n------------------------------------------------------\n')
                                                print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                                                print(f'\n------------------------------------------------------\n')

                                    elif confirm_config == 'N':
                                        print(f'\n-------------------------------------------------------------------------------------------\n')
                                        print(f'  Starting Boot Order Configuration Over.')
                                        print(f'\n-------------------------------------------------------------------------------------------\n')
                                        valid_confirm = True
                                    else:
                                        print(f'\n------------------------------------------------------\n')
                                        print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                                        print(f'\n------------------------------------------------------\n')

                        elif question == 'N':
                            sub_loop = True
                        else:
                            print(f'\n------------------------------------------------------\n')
                            print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                            print(f'\n------------------------------------------------------\n')

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'    boot_mode          = "{polVars["boot_mode"]}"')
                    print(f'    description        = "{polVars["descr"]}"')
                    print(f'    enable_secure_boot = {polVars["enable_secure_boot"]}')
                    print(f'    name               = "{polVars["name"]}"')
                    if len(polVars['boot_devices']) > 0:
                        print(f'    boot_devices = ''{')
                        for i in polVars['boot_devices']:
                            for k, v in i.items():
                                if k == 'device_name':
                                    print(f'      "{v}" = ''{')
                            for k, v in i.items():
                                if k == 'bootloader_description':
                                    print(f'        bootloader_description = "{v}"')
                                elif k == 'bootloader_name':
                                    print(f'        bootloader_name        = "{v}"')
                                elif k == 'bootloader_path':
                                    print(f'        bootloader_path        = "{v}"')
                                elif k == 'enabled':
                                    print(f'        enabled                = {v}')
                                elif k == 'interface_name':
                                    print(f'        InterfaceName          = "{v}"')
                                elif k == 'interface_source':
                                    print(f'        InterfaceSource        = "{v}"')
                                elif k == 'ip_type':
                                    print(f'        IpType                 = "{v}"')
                                elif k == 'mac_address':
                                    print(f'        MacAddress             = "{v}"')
                                elif k == 'lun':
                                    print(f'        Lun                    = {v}')
                                elif k == 'object_type':
                                    print(f'        object_type            = "{v}"')
                                elif k == 'port':
                                    print(f'        Port                   = {v}')
                                elif k == 'slot':
                                    print(f'        Slot                   = "{v}"')
                                elif k == 'subtype':
                                    print(f'        Subtype                = "{v}"')
                                elif k == 'target_wwpn':
                                    print(f'        Wwpn                   = "{v}"')
                        print(f'      ''}')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
                        if confirm_policy == 'Y' or confirm_policy == '':
                            confirm_policy = 'Y'

                            # Write Policies to Template File
                            polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                            ezfunctions.write_to_template(self, **polVars)

                            configure_loop, policy_loop = ezfunctions.exit_default_no(polVars["policy_type"])
                            valid_confirm = True

                        elif confirm_policy == 'N':
                            print(f'\n------------------------------------------------------\n')
                            print(f'  Starting {polVars["policy_type"]} Section over.')
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
        polVars["template_file"] = 'template_close.jinja2'
        ezfunctions.write_to_template(self, **polVars)

    #==============================================
    # Certificate Management Policy Module
    #==============================================
    def certificate_management_policies(self, jsonData, easy_jsonData, **kwargs):
        name_prefix = self.name_prefix
        name_suffix = 'cert_mgmt'
        opSystem = kwargs['opSystem']
        org = self.org
        policy_type = 'Certificate Management Policy'
        polVars = {}
        polVars["header"] = '%s Variables' % (policy_type)
        polVars["initial_write"] = True
        polVars["org"] = org
        polVars["policy_type"] = policy_type
        polVars["template_file"] = 'template_open.jinja2'
        polVars["template_type"] = 'certificate_management_policies'
        tfDir = kwargs['tfDir']

        # Open the Template file
        ezfunctions.write_to_template(self, **polVars)
        polVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  A {policy_type} Allows you to specify the certificate and private key-pair ')
            print(f'  details for an external certificate.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            if opSystem == 'Windows':
                print(f'  - {tfDir}\\{org}\\{self.type}\\{polVars["template_type"]}.auto.tfvars')
            else:
                print(f'  - {tfDir}/{org}/{self.type}/{polVars["template_type"]}.auto.tfvars')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            loop_count = 1
            configure = input(f'Do You Want to Configure a {policy_type}.  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                policy_loop = False
                while policy_loop == False:

                    if not name_prefix == '':
                        name = '%s_%s' % (name_prefix, name_suffix)
                    else:
                        name = '%s_%s' % (org, name_suffix)

                    polVars["name"] = ezfunctions.policy_name(name, policy_type)
                    polVars["descr"] = ezfunctions.policy_descr(polVars["name"], policy_type)

                    # Pull in the Policies for Certificate Management
                    jsonVars = jsonData['components']['schemas']['certificatemanagement.CertificateBase']['allOf'][1]['properties']
                    polVars["multi_select"] = False

                    # Request Certificate
                    polVars["Multi_Line_Input"] = True
                    polVars["Description"] = jsonVars['Certificate']['description']
                    polVars["Variable"] = f'base64_certificate_{loop_count}'
                    certificate = ezfunctions.sensitive_var_value(jsonData, **polVars)
                    polVars["certificate"] = loop_count

                    # Encode the Certificate as Base64
                    base64Cert = base64.b64encode(str.encode(certificate)).decode()
                    print('base64 encoded:')
                    print(base64Cert)
                    TF_VAR = f'base64_certificate_{loop_count}'
                    os.environ[TF_VAR] = base64Cert

                    # Request Private Key
                    polVars["Multi_Line_Input"] = True
                    polVars["Description"] = jsonVars['Privatekey']['description']
                    polVars["Variable"] = f'base64_private_key_{loop_count}'
                    privateKey = ezfunctions.sensitive_var_value(jsonData, **polVars)
                    polVars["private_key"] = loop_count

                    # Encode the Certificate as Base64
                    base64Key = base64.b64encode(str.encode(privateKey)).decode()
                    print('base64 encoded:')
                    print(base64Key)
                    TF_VAR = f'base64_certificate_{loop_count}'
                    os.environ[TF_VAR] = base64Key

                    polVars["enabled"] = True
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'    certificate = {polVars["certificate"]}')
                    print(f'    description = "{polVars["descr"]}"')
                    print(f'    enabled     = {polVars["enabled"]}')
                    print(f'    name        = "{polVars["name"]}"')
                    print(f'    private_key = {polVars["private_key"]}')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
                        if confirm_policy == 'Y' or confirm_policy == '':
                            confirm_policy = 'Y'

                            # Write Policies to Template File
                            polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                            ezfunctions.write_to_template(self, **polVars)

                            configure_loop, policy_loop = ezfunctions.exit_default_no(polVars["policy_type"])
                            print(f'configure loop is {configure_loop}')
                            print(f'policy loop is {policy_loop}')
                            loop_count += 1
                            valid_confirm = True

                        elif confirm_policy == 'N':
                            print(f'\n------------------------------------------------------\n')
                            print(f'  Starting {polVars["policy_type"]} Section over.')
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
        polVars["template_file"] = 'template_close.jinja2'
        ezfunctions.write_to_template(self, **polVars)

    #==============================================
    # Device Connector Policy Module
    #==============================================
    def device_connector_policies(self, jsonData, easy_jsonData, **kwargs):
        name_prefix = self.name_prefix
        name_suffix = 'devcon'
        opSystem = kwargs['opSystem']
        org = self.org
        policy_type = 'Device Connector Policy'
        polVars = {}
        polVars["header"] = '%s Variables' % (policy_type)
        polVars["initial_write"] = True
        polVars["org"] = org
        polVars["policy_type"] = policy_type
        polVars["template_file"] = 'template_open.jinja2'
        polVars["template_type"] = 'device_connector_policies'
        tfDir = kwargs['tfDir']

        # Open the Template file
        ezfunctions.write_to_template(self, **polVars)
        polVars["initial_write"] = False

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
            if opSystem == 'Windows':
                print(f'  - {tfDir}\\{org}\\{self.type}\\{polVars["template_type"]}.auto.tfvars')
            else:
                print(f'  - {tfDir}/{org}/{self.type}/{polVars["template_type"]}.auto.tfvars')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure a {policy_type}?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                policy_loop = False
                while policy_loop == False:

                    if not name_prefix == '':
                        name = '%s_%s' % (name_prefix, name_suffix)
                    else:
                        name = '%s_%s' % (org, name_suffix)

                    polVars["name"] = ezfunctions.policy_name(name, policy_type)
                    polVars["descr"] = ezfunctions.policy_descr(polVars["name"], policy_type)

                    jsonVars = jsonData['components']['schemas']['deviceconnector.Policy']['allOf'][1]['properties']
                    polVars["Description"] = jsonVars['LockoutEnabled']['description']
                    polVars["varInput"] = f'Do you want to lock down Configuration to Intersight only?'
                    polVars["varDefault"] = 'N'
                    polVars["varName"] = 'Lockout Enabled'
                    polVars["configuration_lockout"] = ezfunctions.varBoolLoop(**polVars)

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  ')
                    print(f'   configuration_lockout = {polVars["configuration_lockout"]}')
                    print(f'   description           = "{polVars["descr"]}"')
                    print(f'   name                  = "{polVars["name"]}"')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
                        if confirm_policy == 'Y' or confirm_policy == '':
                            confirm_policy = 'Y'

                            # Write Policies to Template File
                            polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                            ezfunctions.write_to_template(self, **polVars)

                            configure_loop, policy_loop = ezfunctions.exit_default_no(polVars["policy_type"])
                            valid_confirm = True

                        elif confirm_policy == 'N':
                            print(f'\n------------------------------------------------------\n')
                            print(f'  Starting {polVars["policy_type"]} Section over.')
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
        polVars["template_file"] = 'template_close.jinja2'
        ezfunctions.write_to_template(self, **polVars)

    #==============================================
    # Firmware - UCS Domain Module
    #==============================================
    def firmware_ucs_domain(self, jsonData, easy_jsonData, **kwargs):
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
    # Flow Control Policy Module
    #==============================================
    def flow_control_policies(self, jsonData, easy_jsonData, **kwargs):
        name_prefix = self.name_prefix
        name_suffix = 'flow_ctrl'
        opSystem = kwargs['opSystem']
        org = self.org
        policy_type = 'Flow Control Policy'
        polVars = {}
        polVars["header"] = '%s Variables' % (policy_type)
        polVars["initial_write"] = True
        polVars["org"] = org
        polVars["policy_type"] = policy_type
        polVars["template_file"] = 'template_open.jinja2'
        polVars["template_type"] = 'flow_control_policies'
        tfDir = kwargs['tfDir']

        # Open the Template file
        ezfunctions.write_to_template(self, **polVars)
        polVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  The Flow Control Policy will enable Priority Flow Control on the Fabric Interconnects.')
            print(f'  We recommend the default parameters so you will only be asked for the name and')
            print(f'  description for the Policy.  You only need one of these policies for Organization')
            print(f'  {org}.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            if opSystem == 'Windows':
                print(f'  - {tfDir}\\{org}\\{self.type}\\{polVars["template_type"]}.auto.tfvars')
            else:
                print(f'  - {tfDir}/{org}/{self.type}/{polVars["template_type"]}.auto.tfvars')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            policy_loop = False
            while policy_loop == False:

                if not name_prefix == '':
                    name = '%s_%s' % (name_prefix, name_suffix)
                else:
                    name = '%s_%s' % (org, name_suffix)

                polVars["name"] = ezfunctions.policy_name(name, policy_type)
                polVars["descr"] = ezfunctions.policy_descr(polVars["name"], policy_type)

                polVars["priority"] = 'auto'
                polVars["receive"] = 'Disabled'
                polVars["send"] = 'Disabled'

                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'    description = "{polVars["descr"]}"')
                print(f'    name        = "{polVars["name"]}"')
                print(f'    priority    = "{polVars["priority"]}"')
                print(f'    receive     = "{polVars["receive"]}"')
                print(f'    send        = "{polVars["send"]}"')
                print(f'\n-------------------------------------------------------------------------------------------\n')
                valid_confirm = False
                while valid_confirm == False:
                    confirm_policy = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                    if confirm_policy == 'Y' or confirm_policy == '':
                        confirm_policy = 'Y'

                        # Write Policies to Template File
                        polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                        ezfunctions.write_to_template(self, **polVars)

                        configure_loop, policy_loop = ezfunctions.exit_default_no(polVars["policy_type"])
                        valid_confirm = True

                    elif confirm_policy == 'N':
                        print(f'\n------------------------------------------------------\n')
                        print(f'  Starting {polVars["policy_type"]} Section over.')
                        print(f'\n------------------------------------------------------\n')
                        valid_confirm = True

                    else:
                        print(f'\n------------------------------------------------------\n')
                        print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                        print(f'\n------------------------------------------------------\n')

        # Close the Template file
        polVars["template_file"] = 'template_close.jinja2'
        ezfunctions.write_to_template(self, **polVars)

    #==============================================
    # IMC Access Policy Module
    #==============================================
    def imc_access_policies(self, jsonData, easy_jsonData, **kwargs):
        name_prefix = self.name_prefix
        name_suffix = 'imc_access'
        opSystem = kwargs['opSystem']
        org = self.org
        policy_type = 'IMC Access Policy'
        polVars = {}
        polVars["header"] = '%s Variables' % (policy_type)
        polVars["initial_write"] = True
        polVars["org"] = org
        polVars["policy_type"] = policy_type
        polVars["template_file"] = 'template_open.jinja2'
        polVars["template_type"] = 'imc_access_policies'
        tfDir = kwargs['tfDir']

        # Open the Template file
        ezfunctions.write_to_template(self, **polVars)
        polVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  You will need to configure an IMC Access Policy in order to Assign the VLAN and IPs to ')
            print(f'  the Servers for KVM Access.  At this time only inband access is supported in IMM mode.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            if opSystem == 'Windows':
                print(f'  - {tfDir}\\{org}\\{self.type}\\{polVars["template_type"]}.auto.tfvars')
            else:
                print(f'  - {tfDir}/{org}/{self.type}/{polVars["template_type"]}.auto.tfvars')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            loop_count = 0
            policy_loop = False
            while policy_loop == False:
                if not name_prefix == '':
                    name = '%s_%s' % (name_prefix, name_suffix)
                else:
                    name = '%s_%s' % (org, name_suffix)

                polVars["name"] = ezfunctions.policy_name(name, policy_type)
                polVars["descr"] = ezfunctions.policy_descr(polVars["name"], policy_type)
                polVars["default_vlan"] = 0

                polVars["multi_select"] = False
                jsonVars = jsonData['components']['schemas']['server.BaseProfile']['allOf'][1]['properties']
                polVars["var_description"] = jsonVars['TargetPlatform']['description']
                polVars["jsonVars"] = sorted(jsonVars['TargetPlatform']['enum'])
                polVars["defaultVar"] = 'FIAttached'
                polVars["varType"] = 'Target Platform'
                polVars["target_platform"] = ezfunctions.variablesFromAPI(**polVars)

                # IMC Access Type
                jsonVars = jsonData['components']['schemas']['access.Policy']['allOf'][1]['properties']
                polVars["var_description"] = jsonVars['ConfigurationType']['description']
                polVars["jsonVars"] = ['inband', 'out_of_band']
                polVars["defaultVar"] = 'inband'
                polVars["varType"] = 'IMC Access Type'
                imcBand = ezfunctions.variablesFromAPI(**polVars)

                policy_list = [
                    f'pools.ip_pools.{imcBand}_ip_pool'
                ]
                polVars["allow_opt_out"] = False
                for policy in policy_list:
                    policy_type = policy.split('.')[2]
                    polVars[policy_type],policyData = policy_select_loop(jsonData, easy_jsonData, name_prefix, policy, **polVars)

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
                                    vlan_policy,policyData = policy_select_loop(jsonData, easy_jsonData, name_prefix, policy, **polVars)
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
                print(f'   description                = "{polVars["descr"]}"')
                if imcBand == 'inband':
                    print(f'   inband_ip_pool             = "{polVars["inband_ip_pool"]}"')
                    print(f'   inband_vlan_id             = {polVars["inband_vlan_id"]}')
                print(f'   ipv4_address_configuration = {polVars["ipv4_address_configuration"]}')
                print(f'   ipv6_address_configuration = {polVars["ipv6_address_configuration"]}')
                if imcBand == 'out_of_band':
                    print(f'   out_of_band_ip_pool        = "{polVars["out_of_band_ip_pool"]}"')
                print(f'\n-------------------------------------------------------------------------------------------\n')
                valid_confirm = False
                while valid_confirm == False:
                    confirm_policy = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                    if confirm_policy == 'Y' or confirm_policy == '':
                        confirm_policy = 'Y'

                        # Write Policies to Template File
                        polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                        ezfunctions.write_to_template(self, **polVars)

                        configure_loop, policy_loop = ezfunctions.exit_default_no(polVars["policy_type"])
                        valid_confirm = True

                    elif confirm_policy == 'N':
                        print(f'\n------------------------------------------------------\n')
                        print(f'  Starting {polVars["policy_type"]} Section over.')
                        print(f'\n------------------------------------------------------\n')
                        valid_confirm = True

                    else:
                        print(f'\n------------------------------------------------------\n')
                        print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                        print(f'\n------------------------------------------------------\n')

        # Close the Template file
        polVars["template_file"] = 'template_close.jinja2'
        ezfunctions.write_to_template(self, **polVars)

    #==============================================
    # IPMI over LAN Policy Module
    #==============================================
    def ipmi_over_lan_policies(self, jsonData, easy_jsonData, **kwargs):
        name_prefix = self.name_prefix
        name_suffix = 'ipmi'
        opSystem = kwargs['opSystem']
        org = self.org
        policy_type = 'IPMI over LAN Policy'
        polVars = {}
        polVars["header"] = '%s Variables' % (policy_type)
        polVars["initial_write"] = True
        polVars["org"] = org
        polVars["policy_type"] = policy_type
        polVars["template_file"] = 'template_open.jinja2'
        polVars["template_type"] = 'ipmi_over_lan_policies'
        tfDir = kwargs['tfDir']

        # Open the Template file
        ezfunctions.write_to_template(self, **polVars)
        polVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  An {policy_type} will configure IPMI over LAN access on a Server Profile.  This policy')
            print(f'  allows you to determine whether IPMI commands can be sent directly to the server, using ')
            print(f'  the IP address.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            if opSystem == 'Windows':
                print(f'  - {tfDir}\\{org}\\{self.type}\\{polVars["template_type"]}.auto.tfvars')
            else:
                print(f'  - {tfDir}/{org}/{self.type}/{polVars["template_type"]}.auto.tfvars')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure an {policy_type}?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                policy_loop = False
                while policy_loop == False:

                    if not name_prefix == '':
                        name = '%s_%s' % (name_prefix, name_suffix)
                    else:
                        name = '%s_%s' % (org, name_suffix)

                    polVars["name"] = ezfunctions.policy_name(name, policy_type)
                    polVars["descr"] = ezfunctions.policy_descr(polVars["name"], policy_type)
                    polVars["enabled"] = True

                    valid = False
                    while valid == False:
                        encrypt_traffic = input('Do you want to encrypt IPMI over LAN Traffic?  Enter "Y" or "N" [Y]: ')
                        if encrypt_traffic == 'Y' or encrypt_traffic == '':
                            polVars["ipmi_key"] = ezfunctions.ipmi_key_function(**polVars)

                    polVars["multi_select"] = False
                    jsonVars = jsonData['components']['schemas']['ipmioverlan.Policy']['allOf'][1]['properties']
                    polVars["var_description"] = jsonVars['Privilege']['description']
                    polVars["jsonVars"] = sorted(jsonVars['Privilege']['enum'])
                    polVars["defaultVar"] = jsonVars['Privilege']['default']
                    polVars["varType"] = 'Privilege'
                    polVars["privilege"] = ezfunctions.variablesFromAPI(**polVars)

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'   description = "{polVars["descr"]}"')
                    print(f'   enabled     = {polVars["enabled"]}')
                    if polVars["ipmi_key"]:
                        print(f'   ipmi_key    = "Sensitive_value"')
                    print(f'   name        = "{polVars["name"]}"')
                    print(f'   privilege   = "{polVars["privilege"]}"')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                        if confirm_policy == 'Y' or confirm_policy == '':
                            confirm_policy = 'Y'

                            # Write Policies to Template File
                            polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                            ezfunctions.write_to_template(self, **polVars)

                            configure_loop, policy_loop = ezfunctions.exit_default_no(polVars["policy_type"])
                            valid_confirm = True

                        elif confirm_policy == 'N':
                            print(f'\n------------------------------------------------------\n')
                            print(f'  Starting {polVars["policy_type"]} Section over.')
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
        polVars["template_file"] = 'template_close.jinja2'
        ezfunctions.write_to_template(self, **polVars)

    #==============================================
    # Intersight Module
    #==============================================
    def intersight(self, easy_jsonData, tfcb_config):
        org = self.org
        policy_type = 'Intersight'
        polVars = {}
        polVars["header"] = '%s Variables' % (policy_type)
        polVars["initial_write"] = True
        polVars["org"] = org
        polVars["policy_type"] = policy_type
        polVars["template_file"] = 'template_open.jinja2'
        polVars["template_type"] = 'intersight'
        policyVar = self.type

        polVars["org"] = org
        for item in tfcb_config:
            for k, v in item.items():
                if k == 'backend':
                    polVars["backend"] = v
                elif k == 'tfc_organization':
                    polVars["tfc_organization"] = v
                if policyVar == 'policies':
                    if k == 'pools':
                        polVars["pools_ws"] = v
                    elif k == 'ucs_domain_profiles':
                        polVars["domain_profiles_ws"] = v
                elif policyVar == 'profiles':
                    if k == 'pools':
                        polVars["pools_ws"] = v
                    elif k == 'policies':
                        polVars["policies_ws"] = v

        polVars["tags"] = '[{ key = "Module", value = "terraform-intersight-easy-imm" }, { key = "Version", value = "'f'{easy_jsonData["version"]}''" }]'

        # Write Policies to Template File
        polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
        ezfunctions.write_to_template(self, **polVars)

    #==============================================
    # LDAP Policy Module
    #==============================================
    def ldap_policies(self, jsonData, easy_jsonData, **kwargs):
        name_prefix = self.name_prefix
        name_suffix = 'ldap'
        opSystem = kwargs['opSystem']
        org = self.org
        policy_type = 'LDAP Policy'
        polVars = {}
        polVars["header"] = '%s Variables' % (policy_type)
        polVars["initial_write"] = True
        polVars["org"] = org
        polVars["policy_type"] = policy_type
        polVars["template_file"] = 'template_open.jinja2'
        polVars["template_type"] = 'ldap_policies'
        tfDir = kwargs['tfDir']

        # Open the Template file
        ezfunctions.write_to_template(self, **polVars)
        polVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  An {policy_type} stores and maintains directory information in a network. When LDAP is ')
            print(f'  enabled in the Cisco IMC, user authentication and role authorization is performed by the ')
            print(f'  LDAP server for user accounts not found in the local user database. You can enable and ')
            print(f'  configure LDAP, and configure LDAP servers and LDAP groups.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            if opSystem == 'Windows':
                print(f'  - {tfDir}\\{org}\\{self.type}\\{polVars["template_type"]}.auto.tfvars')
            else:
                print(f'  - {tfDir}/{org}/{self.type}/{polVars["template_type"]}.auto.tfvars')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure an {policy_type}?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                loop_count = 1
                policy_loop = False
                while policy_loop == False:

                    if not name_prefix == '':
                        name = '%s_%s' % (name_prefix, name_suffix)
                    else:
                        name = '%s_%s' % (org, name_suffix)

                    polVars["name"] = ezfunctions.policy_name(name, policy_type)
                    polVars["descr"] = ezfunctions.policy_descr(polVars["name"], policy_type)
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
                    jsonVars = jsonData['components']['schemas']['iam.LdapBaseProperties']['allOf'][1]['properties']
                    polVars["var_description"] = jsonVars['BindMethod']['description']
                    polVars["jsonVars"] = sorted(jsonVars['BindMethod']['enum'])
                    polVars["defaultVar"] = jsonVars['BindMethod']['default']
                    polVars["varType"] = 'LDAP Bind Method'
                    bind_method = ezfunctions.variablesFromAPI(**polVars)

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
                        else:
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                            print(f'\n-------------------------------------------------------------------------------------------\n')

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
                        else:
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                            print(f'\n-------------------------------------------------------------------------------------------\n')

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
                        else:
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                            print(f'\n-------------------------------------------------------------------------------------------\n')

                    if ldap_from_dns == True:
                        polVars["multi_select"] = False
                        jsonVars = jsonData['components']['schemas']['iam.LdapDnsParameters']['allOf'][1]['properties']
                        polVars["var_description"] = jsonVars['Source']['description']
                        polVars["jsonVars"] = sorted(jsonVars['Source']['enum'])
                        polVars["defaultVar"] = jsonVars['Source']['default']
                        polVars["varType"] = 'LDAP Domain Source'
                        varSource = ezfunctions.variablesFromAPI(**polVars)

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
                    jsonVars = jsonData['components']['schemas']['iam.LdapPolicy']['allOf'][1]['properties']
                    polVars["var_description"] = jsonVars['UserSearchPrecedence']['description']
                    polVars["jsonVars"] = sorted(jsonVars['UserSearchPrecedence']['enum'])
                    polVars["defaultVar"] = jsonVars['UserSearchPrecedence']['default']
                    polVars["varType"] = 'User Search Precedence'
                    polVars["user_search_precedence"] = ezfunctions.variablesFromAPI(**polVars)

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
                                jsonVars = easy_jsonData['policies']['iam.LdapPolicy']
                                polVars["var_description"] = jsonVars['role']['description']
                                polVars["jsonVars"] = sorted(jsonVars['role']['enum'])
                                polVars["defaultVar"] = jsonVars['role']['default']
                                polVars["varType"] = 'Group Role'
                                role = ezfunctions.variablesFromAPI(**polVars)

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
                                            else:
                                                print(f'\n------------------------------------------------------\n')
                                                print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                                                print(f'\n------------------------------------------------------\n')

                                    elif confirm_config == 'N':
                                        print(f'\n-------------------------------------------------------------------------------------------\n')
                                        print(f'  Starting LDAP Group Configuration Over.')
                                        print(f'\n-------------------------------------------------------------------------------------------\n')
                                        valid_confirm = True
                                    else:
                                        print(f'\n------------------------------------------------------\n')
                                        print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                                        print(f'\n------------------------------------------------------\n')

                        elif question == 'N':
                            sub_loop = True
                        else:
                            print(f'\n------------------------------------------------------\n')
                            print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                            print(f'\n------------------------------------------------------\n')

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
                                            else:
                                                print(f'\n------------------------------------------------------\n')
                                                print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                                                print(f'\n------------------------------------------------------\n')

                                    elif confirm_config == 'N':
                                        print(f'\n-------------------------------------------------------------------------------------------\n')
                                        print(f'  Starting LDAP Server Configuration Over.')
                                        print(f'\n-------------------------------------------------------------------------------------------\n')
                                        valid_confirm = True
                                    else:
                                        print(f'\n------------------------------------------------------\n')
                                        print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                                        print(f'\n------------------------------------------------------\n')

                        elif question == 'N':
                            sub_loop = True
                        else:
                            print(f'\n------------------------------------------------------\n')
                            print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                            print(f'\n------------------------------------------------------\n')

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'    base_settings = ''{')
                    print(f'      base_dn = "{polVars["base_settings"]["base_dn"]}"')
                    print(f'      domain  = "{polVars["base_settings"]["domain"]}"')
                    print(f'      timeout = "{polVars["base_settings"]["timeout"]}"')
                    print(f'    ''}')
                    print(f'    binding_parameters = ''{')
                    if not bind_method == 'LoginCredentials':
                        print(f'      bind_dn     = "{polVars["binding_parameters"]["bind_dn"]}"')
                    print(f'      bind_method = "{polVars["binding_parameters"]["bind_method"]}"')
                    print(f'    ''}')
                    print(f'    description                = "{polVars["descr"]}"')
                    print(f'    enable_encryption          = {polVars["enable_encryption"]}')
                    print(f'    enable_group_authorization = {polVars["enable_group_authorization"]}')
                    print(f'    enable_ldap                = {polVars["enable_ldap"]}')
                    if not ldap_from_dns == False:
                        print(f'    ldap_from_dns = ''{')
                        print(f'      enable        = True')
                        if not varSource == 'Extracted':
                            print(f'      search_domain = "{searchDomain}"')
                            print(f'      search_domain = "{searchForest}"')
                        print(f'      source        = "{varSource}"')
                        print(f'    ''}')
                    print(f'    name                      = "{polVars["name"]}"')
                    print(f'    nested_group_search_depth = "{polVars["nested_group_search_depth"]}"')
                    if len(polVars["ldap_groups"]) > 0:
                        print(f'    ldap_groups = ''{')
                        for item in polVars["ldap_groups"]:
                            for k, v in item.items():
                                if k == 'group':
                                    print(f'      "{v}" = ''{')
                            for k, v in item.items():
                                if k == 'role':
                                    print(f'        {k} = "{v}"')
                            print(f'      ''}')
                        print(f'    ''}')
                    if len(polVars["ldap_servers"]) > 0:
                        print(f'    ldap_servers = ''{')
                        for item in polVars["ldap_servers"]:
                            for k, v in item.items():
                                if k == 'server':
                                    print(f'      "{v}" = ''{')
                            for k, v in item.items():
                                if k == 'port':
                                    print(f'        {k} = {v}')
                            print(f'      ''}')
                        print(f'    ''}')
                    print(f'    user_search_precedence = "{polVars["user_search_precedence"]}"')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
                        if confirm_policy == 'Y' or confirm_policy == '':
                            confirm_policy = 'Y'

                            # Write Policies to Template File
                            polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                            ezfunctions.write_to_template(self, **polVars)

                            configure_loop, policy_loop = ezfunctions.exit_default_no(polVars["policy_type"])
                            valid_confirm = True

                        elif confirm_policy == 'N':
                            print(f'\n------------------------------------------------------\n')
                            print(f'  Starting {polVars["policy_type"]} Section over.')
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
        polVars["template_file"] = 'template_close.jinja2'
        ezfunctions.write_to_template(self, **polVars)

    #==============================================
    # Link Aggregation Policy Module
    #==============================================
    def link_aggregation_policies(self, jsonData, easy_jsonData, **kwargs):
        name_prefix = self.name_prefix
        name_suffix = 'link_agg'
        opSystem = kwargs['opSystem']
        org = self.org
        policy_type = 'Link Aggregation Policy'
        polVars = {}
        polVars["header"] = '%s Variables' % (policy_type)
        polVars["initial_write"] = True
        polVars["org"] = org
        polVars["policy_type"] = policy_type
        polVars["template_file"] = 'template_open.jinja2'
        polVars["template_type"] = 'link_aggregation_policies'
        tfDir = kwargs['tfDir']

        # Open the Template file
        ezfunctions.write_to_template(self, **polVars)
        polVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  A Link Aggregation Policy will assign LACP settings to the Ethernet Port-Channels and')
            print(f'  uplinks.  We recommend the default wizard settings so you will only be asked for the ')
            print(f'  name and description for the Policy.  You only need one of these policies for ')
            print(f'  Organization {org}.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            if opSystem == 'Windows':
                print(f'  - {tfDir}\\{org}\\{self.type}\\{polVars["template_type"]}.auto.tfvars')
            else:
                print(f'  - {tfDir}/{org}/{self.type}/{polVars["template_type"]}.auto.tfvars')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            policy_loop = False
            while policy_loop == False:

                if not name_prefix == '':
                    name = '%s_%s' % (name_prefix, name_suffix)
                else:
                    name = '%s_%s' % (org, name_suffix)

                polVars["name"] = ezfunctions.policy_name(name, policy_type)
                polVars["descr"] = ezfunctions.policy_descr(polVars["name"], policy_type)

                polVars["lacp_rate"] = 'normal'
                polVars["suspend_individual"] = False

                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'    description        = "{polVars["descr"]}"')
                print(f'    lacp_rate          = "{polVars["lacp_rate"]}"')
                print(f'    name               = "{polVars["name"]}"')
                print(f'    suspend_individual = {polVars["suspend_individual"]}')
                print(f'\n-------------------------------------------------------------------------------------------\n')
                valid_confirm = False
                while valid_confirm == False:
                    confirm_policy = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                    if confirm_policy == 'Y' or confirm_policy == '':
                        confirm_policy = 'Y'

                        # Write Policies to Template File
                        polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                        ezfunctions.write_to_template(self, **polVars)

                        configure_loop, policy_loop = ezfunctions.exit_default_no(polVars["policy_type"])
                        valid_confirm = True

                    elif confirm_policy == 'N':
                        print(f'\n------------------------------------------------------\n')
                        print(f'  Starting {polVars["policy_type"]} Section over.')
                        print(f'\n------------------------------------------------------\n')
                        valid_confirm = True

                    else:
                        print(f'\n------------------------------------------------------\n')
                        print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                        print(f'\n------------------------------------------------------\n')

        # Close the Template file
        polVars["template_file"] = 'template_close.jinja2'
        ezfunctions.write_to_template(self, **polVars)

    #==============================================
    # Link Control Policy Module
    #==============================================
    def link_control_policies(self, jsonData, easy_jsonData, **kwargs):
        name_prefix = self.name_prefix
        name_suffix = 'link_ctrl'
        opSystem = kwargs['opSystem']
        org = self.org
        policy_type = 'Link Control Policy'
        polVars = {}
        polVars["header"] = '%s Variables' % (policy_type)
        polVars["initial_write"] = True
        polVars["org"] = org
        polVars["policy_type"] = policy_type
        polVars["template_file"] = 'template_open.jinja2'
        polVars["template_type"] = 'link_control_policies'
        tfDir = kwargs['tfDir']

        # Open the Template file
        ezfunctions.write_to_template(self, **polVars)
        polVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  A Link Control Policy will configure the Unidirectional Link Detection Protocol for')
            print(f'  Ethernet Uplinks/Port-Channels.')
            print(f'  We recommend the wizards default parameters so you will only be asked for the name')
            print(f'  and description for the Policy.  You only need one of these policies for')
            print(f'  Organization {org}.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            if opSystem == 'Windows':
                print(f'  - {tfDir}\\{org}\\{self.type}\\{polVars["template_type"]}.auto.tfvars')
            else:
                print(f'  - {tfDir}/{org}/{self.type}/{polVars["template_type"]}.auto.tfvars')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            policy_loop = False
            while policy_loop == False:

                if not name_prefix == '':
                    name = '%s_%s' % (name_prefix, name_suffix)
                else:
                    name = '%s_%s' % (org, name_suffix)

                polVars["name"] = ezfunctions.policy_name(name, policy_type)
                polVars["descr"] = ezfunctions.policy_descr(polVars["name"], policy_type)

                polVars["admin_state"] = 'Enabled'
                polVars["mode"] = 'normal'

                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'    admin_state = "{polVars["admin_state"]}"')
                print(f'    description = "{polVars["descr"]}"')
                print(f'    mode        = "{polVars["mode"]}"')
                print(f'    name        = "{polVars["name"]}"')
                print(f'\n-------------------------------------------------------------------------------------------\n')
                valid_confirm = False
                while valid_confirm == False:
                    confirm_policy = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                    if confirm_policy == 'Y' or confirm_policy == '':
                        confirm_policy = 'Y'

                        # Write Policies to Template File
                        polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                        ezfunctions.write_to_template(self, **polVars)

                        configure_loop, policy_loop = ezfunctions.exit_default_no(polVars["policy_type"])
                        valid_confirm = True

                    elif confirm_policy == 'N':
                        print(f'\n------------------------------------------------------\n')
                        print(f'  Starting {polVars["policy_type"]} Section over.')
                        print(f'\n------------------------------------------------------\n')
                        valid_confirm = True

                    else:
                        print(f'\n------------------------------------------------------\n')
                        print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                        print(f'\n------------------------------------------------------\n')

        # Close the Template file
        polVars["template_file"] = 'template_close.jinja2'
        ezfunctions.write_to_template(self, **polVars)

def policy_select_loop(jsonData, easy_jsonData, name_prefix, policy, **polVars):
    loop_valid = False
    while loop_valid == False:
        create_policy = True
        inner_policy = policy.split('.')[1]
        inner_type = policy.split('.')[0]
        inner_var = policy.split('.')[2]
        polVars[inner_var] = ''
        polVars["policies"],policyData = ezfunctions.policies_parse(polVars["org"], inner_type, inner_policy)
        if not len(polVars["policies"]) > 0:
            valid = False
            while valid == False:

                x = inner_policy.split('_')
                ezfunctions.policy_description = []
                for y in x:
                    y = y.capitalize()
                    ezfunctions.policy_description.append(y)
                ezfunctions.policy_description = " ".join(ezfunctions.policy_description)
                ezfunctions.policy_description = ezfunctions.policy_description.replace('Ip', 'IP')
                ezfunctions.policy_description = ezfunctions.policy_description.replace('Lan', 'LAN')
                ezfunctions.policy_description = ezfunctions.policy_description.replace('San', 'SAN')
                ezfunctions.policy_description = ezfunctions.policy_description.replace('Vlan', 'VLAN')
                ezfunctions.policy_description = ezfunctions.policy_description.replace('Vsan', 'VSAN')
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'   There were no {ezfunctions.policy_description} found.')
                print(f'\n-------------------------------------------------------------------------------------------\n')

                if 'Policies' in ezfunctions.policy_description:
                    ezfunctions.policy_description = ezfunctions.policy_description.replace('Policies', 'Policy')
                elif 'Pools' in ezfunctions.policy_description:
                    ezfunctions.policy_description = ezfunctions.policy_description.replace('Pools', 'Pool')
                elif 'Profiles' in ezfunctions.policy_description:
                    ezfunctions.policy_description = ezfunctions.policy_description.replace('Profiles', 'Profile')
                elif 'Templates' in ezfunctions.policy_description:
                    ezfunctions.policy_description = ezfunctions.policy_description.replace('Templates', 'Template')

                if polVars["allow_opt_out"] == True:
                    Question = input(f'Do you want to create a(n) {ezfunctions.policy_description}?  Enter "Y" or "N" [Y]: ')
                    if Question == '' or Question == 'Y':
                        create_policy = True
                        valid = True
                    elif Question == 'N':
                        create_policy = False
                        valid = True
                        return polVars[inner_var],policyData
                else:
                    create_policy = True
                    valid = True

        else:
            polVars[inner_var] = ezfunctions.choose_policy(inner_policy, **polVars)
            if polVars[inner_var] == 'create_policy':
                create_policy = True
            elif polVars[inner_var] == '' and polVars["allow_opt_out"] == True:
                loop_valid = True
                create_policy = False
                return polVars[inner_var],policyData
            elif not polVars[inner_var] == '':
                loop_valid = True
                create_policy = False
                return polVars[inner_var],policyData
        if create_policy == True:
            kwargs = {}
            opSystem = platform.system()
            if os.environ.get('TF_DEST_DIR') is None:
                tfDir = 'Intersight'
            else:
                tfDir = os.environ.get('TF_DEST_DIR')
            if tfDir[-1] == '\\' or tfDir[-1] == '/':
                    tfDir = tfDir[:-1]

            kwargs.update({'opSystem':opSystem,'tfDir':tfDir})

            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  Starting module to create {inner_policy}')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            if inner_policy == 'ip_pools':
                pools.pools(name_prefix, polVars["org"], inner_type).ip_pools(jsonData, easy_jsonData, **kwargs)
            elif inner_policy == 'lan_connectivity_policies':
                lan.policies(name_prefix, polVars["org"], inner_type).lan_connectivity_policies(jsonData, easy_jsonData, **kwargs)
            elif inner_policy == 'san_connectivity_policies':
                san.policies(name_prefix, polVars["org"], inner_type).san_connectivity_policies(jsonData, easy_jsonData, **kwargs)
            elif inner_policy == 'vlan_policies':
                vxan.policies(name_prefix, polVars["org"], inner_type).vlan_policies(jsonData, easy_jsonData, **kwargs)
