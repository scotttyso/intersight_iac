#!/usr/bin/env python3

import base64
import jinja2
import json
import os
import pkg_resources
import platform
import re
import stdiomask
import validating
from class_policies_lan import policies_lan
from class_policies_san import policies_san
from class_policies_vxan import policies_vxan
from class_pools import pools
from easy_functions import choose_policy, policies_parse
from easy_functions import exit_default_no, exit_default_yes
from easy_functions import ipmi_key_function
from easy_functions import policy_descr, policy_name
from easy_functions import sensitive_var_value
from easy_functions import variablesFromAPI
from easy_functions import varBoolLoop
from easy_functions import varNumberLoop
from easy_functions import varStringLoop
from easy_functions import vlan_list_full
from easy_functions import write_to_template
from textwrap import fill

ucs_template_path = pkg_resources.resource_filename('class_policies_p1', 'Templates/')

class policies_p1(object):
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
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'adapter_configuration_policies'
        tfDir = kwargs['tfDir']

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  An {policy_type} configures the Ethernet and Fibre-Channel settings for the ')
            print(f'  Virtual Interface Card (VIC) adapter.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            if opSystem == 'Windows':
                print(f'  - {tfDir}\\{org}\\{self.type}\\{templateVars["template_type"]}.auto.tfvars')
            else:
                print(f'  - {tfDir}/{org}/{self.type}/{templateVars["template_type"]}.auto.tfvars')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure an {policy_type}?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                policy_loop = False
                while policy_loop == False:

                    if not name_prefix == '':
                        name = '%s_%s' % (name_prefix, name_suffix)
                    else:
                        name = '%s_%s' % (org, name_suffix)

                    templateVars["name"] = policy_name(name, policy_type)
                    templateVars["descr"] = policy_descr(templateVars["name"], policy_type)

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  If Selected, then FCoE Initialization Protocol (FIP) mode is enabled. FIP mode ensures ')
                    print(f'  that the adapter is compatible with current FCoE standards.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid = False
                    while valid == False:
                        Question = input('Do you want to Enable FIP on the VIC?  Enter "Y" or "N" [Y]: ')
                        if Question == '' or Question == 'Y':
                            templateVars["enable_fip"] = True
                            valid = True
                        elif Question == 'N':
                            templateVars["enable_fip"] = False
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
                            templateVars["enable_lldp"] = True
                            valid = True
                        elif Question == 'N':
                            templateVars["enable_lldp"] = False
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
                            templateVars["enable_port_channel"] = True
                            valid = True
                        elif Question == 'N':
                            templateVars["enable_port_channel"] = False
                            valid = True
                        else:
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                            print(f'\n-------------------------------------------------------------------------------------------\n')

                    intList = [1, 2, 3, 4]
                    for x in intList:
                        templateVars["multi_select"] = False
                        jsonVars = jsonData['components']['schemas']['adapter.DceInterfaceSettings']['allOf'][1]['properties']
                        templateVars["var_description"] = jsonVars['FecMode']['description']
                        templateVars["jsonVars"] = sorted(jsonVars['FecMode']['enum'])
                        templateVars["defaultVar"] = jsonVars['FecMode']['default']
                        templateVars["varType"] = f'DCE Interface {x} FEC Mode'
                        intFec = f'fec_mode_{x}'
                        templateVars[intFec] = variablesFromAPI(**templateVars)

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'    description         = "{templateVars["descr"]}"')
                    print(f'    enable_fip          = {templateVars["enable_fip"]}')
                    print(f'    enable_lldp         = {templateVars["enable_lldp"]}')
                    print(f'    enable_port_channel = {templateVars["enable_port_channel"]}')
                    print(f'    fec_mode_1          = "{templateVars["fec_mode_1"]}"')
                    print(f'    fec_mode_2          = "{templateVars["fec_mode_2"]}"')
                    print(f'    fec_mode_3          = "{templateVars["fec_mode_3"]}"')
                    print(f'    fec_mode_4          = "{templateVars["fec_mode_4"]}"')
                    print(f'    name                = "{templateVars["name"]}"')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
                        if confirm_policy == 'Y' or confirm_policy == '':
                            confirm_policy = 'Y'

                            # Write Policies to Template File
                            templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
                            write_to_template(self, **templateVars)

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

    #==============================================
    # BIOS Policy Module
    #==============================================
    def bios_policies(self, jsonData, easy_jsonData, **kwargs):
        name_prefix = self.name_prefix
        opSystem = kwargs['opSystem']
        org = self.org
        policy_type = 'BIOS Policy'
        policy_x = 'BIOS'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["name_prefix"] = name_prefix
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'bios_policies'
        tfDir = kwargs['tfDir']

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  {policy_x} Policies:  To simplify your work, this wizard will use {policy_x}')
            print(f'  Templates that are pre-configured.  You can add custom {policy_x} policy')
            print(f'  configuration to the {templateVars["template_type"]}.auto.tfvars file at your descretion.')
            print(f'  That will not be covered by this wizard as the focus of the wizard is on simplicity.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            if opSystem == 'Windows':
                print(f'  - {tfDir}\\{org}\\{self.type}\\{templateVars["template_type"]}.auto.tfvars')
            else:
                print(f'  - {tfDir}/{org}/{self.type}/{templateVars["template_type"]}.auto.tfvars')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure a {policy_type}?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                policy_loop = False
                while policy_loop == False:

                    templateVars["multi_select"] = False
                    jsonVars = easy_jsonData['policies']['bios.Policy']
                    templateVars["var_description"] = jsonVars['templates']['description']
                    templateVars["jsonVars"] = sorted(jsonVars['templates']['enum'])
                    templateVars["defaultVar"] = jsonVars['templates']['default']
                    templateVars["varType"] = 'BIOS Template'
                    templateVars["policy_template"] = variablesFromAPI(**templateVars)

                    if not templateVars["name_prefix"] == '':
                        name = '%s_%s' % (templateVars["name_prefix"], templateVars["policy_template"])
                    else:
                        name = '%s_%s' % (templateVars["org"], templateVars["policy_template"])

                    templateVars["name"] = policy_name(name, templateVars["policy_type"])
                    templateVars["descr"] = policy_descr(templateVars["name"], templateVars["policy_type"])

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'   bios_template = "{templateVars["policy_template"]}"')
                    print(f'   description   = "{templateVars["descr"]}"')
                    print(f'   name          = "{templateVars["name"]}"')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
                        if confirm_policy == 'Y' or confirm_policy == '':
                            confirm_policy = 'Y'

                            # Write Policies to Template File
                            templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
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

            elif configure == 'N':
                configure_loop = True
            else:
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                print(f'\n-------------------------------------------------------------------------------------------\n')

        # Close the Template file
        templateVars["template_file"] = 'template_close.jinja2'
        write_to_template(self, **templateVars)

    #==============================================
    # Boot Order Policy Module
    #==============================================
    def boot_order_policies(self, jsonData, easy_jsonData, **kwargs):
        name_prefix = self.name_prefix
        name_suffix = 'boot_order'
        opSystem = kwargs['opSystem']
        org = self.org
        policy_type = 'Boot Order Policy'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'boot_order_policies'
        tfDir = kwargs['tfDir']

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  A {policy_type} configures the linear ordering of devices and enables you to change ')
            print(f'  the boot order and boot mode. You can also add multiple devices under various device types,')
            print(f'  rearrange the boot order, and set parameters for each boot device type.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            if opSystem == 'Windows':
                print(f'  - {tfDir}\\{org}\\{self.type}\\{templateVars["template_type"]}.auto.tfvars')
            else:
                print(f'  - {tfDir}/{org}/{self.type}/{templateVars["template_type"]}.auto.tfvars')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure a {policy_type}.  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                policy_loop = False
                while policy_loop == False:

                    if not name_prefix == '':
                        name = '%s_%s' % (name_prefix, name_suffix)
                    else:
                        name = '%s_%s' % (org, name_suffix)

                    templateVars["name"] = policy_name(name, policy_type)
                    templateVars["descr"] = policy_descr(templateVars["name"], policy_type)

                    # Pull in the Policies for iSCSI Boot
                    jsonVars = jsonData['components']['schemas']['boot.PrecisionPolicy']['allOf'][1]['properties']
                    templateVars["multi_select"] = False

                    # Configured Boot Mode
                    templateVars["var_description"] = jsonVars['ConfiguredBootMode']['description']
                    templateVars["jsonVars"] = sorted(jsonVars['ConfiguredBootMode']['enum'])
                    templateVars["defaultVar"] = jsonVars['ConfiguredBootMode']['default']
                    templateVars["varType"] = 'Configured Boot Mode'
                    templateVars["boot_mode"] = variablesFromAPI(**templateVars)

                    if templateVars["boot_mode"] == 'Uefi':
                        # Enforce Uefi SecureBoot
                        templateVars["Description"] = jsonVars['EnforceUefiSecureBoot']['description']
                        templateVars["varInput"] = f'Do you want to Enforce Uefi Secure Boot?'
                        templateVars["varDefault"] = 'Y'
                        templateVars["varName"] = 'Uefi SecureBoot'
                        templateVars["enable_secure_boot"] = varBoolLoop(**templateVars)
                    else:
                        templateVars["enable_secure_boot"] = False


                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  Add and configure a boot device. The configuration options vary with boot device types.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    templateVars["boot_devices"] = []
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
                                templateVars["var_description"] = 'Select the Type of Boot Device to configure.'
                                templateVars["jsonVars"] = sorted(jsonVars['ClassId']['enum'])
                                templateVars["defaultVar"] = 'boot.LocalDisk'
                                templateVars["varType"] = 'Boot Device Class ID'
                                objectType = variablesFromAPI(**templateVars)

                                templateVars["Description"] = jsonVars['Name']['description']
                                templateVars["varDefault"] = ''
                                templateVars["varInput"] = 'Boot Device Name:'
                                templateVars["varName"] = 'Boot Device Name'
                                templateVars["varRegex"] = jsonVars['Name']['pattern']
                                templateVars["minLength"] = 1
                                templateVars["maxLength"] = 30
                                device_name = varStringLoop(**templateVars)

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

                                if templateVars["boot_mode"] == 'Uefi' and re.fullmatch('boot\.(Iscsi|LocalDisk|Nvme|PchStorage|San|SdCard)', objectType):
                                    addLoader = {
                                        "bootloader_description":"Uefi Bootloader",
                                        "bootloader_name":"BOOTX64.EFI",
                                        "bootloader_path":"\\\\EFI\\\\BOOT\\\\"
                                    }
                                    boot_device.update(addLoader)

                                if objectType == 'boot.LocalDisk':
                                    templateVars["multi_select"] = False
                                    jsonVars = jsonData['components']['schemas']['vnic.EthNetworkPolicy']['allOf'][1]['properties']
                                    templateVars["var_description"] = jsonVars['TargetPlatform']['description']
                                    templateVars["jsonVars"] = sorted(jsonVars['TargetPlatform']['enum'])
                                    templateVars["defaultVar"] = jsonVars['TargetPlatform']['default']
                                    templateVars["varType"] = 'Target Platform'
                                    target_platform = variablesFromAPI(**templateVars)

                                    # Slot
                                    jsonVars = jsonData['components']['schemas']['boot.LocalDisk']['allOf'][1]['properties']
                                    templateVars["var_description"] = jsonVars['Slot']['description']
                                    templateVars["jsonVars"] = easy_jsonData['policies']['boot.PrecisionPolicy']['boot.Localdisk'][target_platform]
                                    templateVars["defaultVar"] = easy_jsonData['policies']['boot.PrecisionPolicy']['boot.Localdisk']['default']
                                    templateVars["varType"] = 'Slot'
                                    Slot = variablesFromAPI(**templateVars)

                                    if re.search('[0-9]+', Slot):
                                        templateVars["Description"] = 'Slot Number between 1 and 205.'
                                        templateVars["varDefault"] =  1
                                        templateVars["varInput"] = 'Slot ID of the Localdisk:'
                                        templateVars["varName"] = 'Slot'
                                        templateVars["varRegex"] = '[0-9]+'
                                        templateVars["minNum"] = 1
                                        templateVars["maxNum"] = 205
                                        Slot = varNumberLoop(**templateVars)

                                    localDisk = {'slot':Slot}
                                    boot_device.update(localDisk)

                                if objectType == 'boot.Pxe':
                                    # IPv4 or IPv6
                                    templateVars["var_description"] = jsonVars['IpType']['description']
                                    templateVars["jsonVars"] = sorted(jsonVars['IpType']['enum'])
                                    templateVars["defaultVar"] = jsonVars['IpType']['default']
                                    templateVars["varType"] = 'IP Type'
                                    IpType = variablesFromAPI(**templateVars)

                                    # Interface Source
                                    templateVars["var_description"] = jsonVars['InterfaceSource']['description']
                                    templateVars["jsonVars"] = sorted(jsonVars['InterfaceSource']['enum'])
                                    templateVars["defaultVar"] = jsonVars['InterfaceSource']['default']
                                    templateVars["varType"] = 'Interface Source'
                                    InterfaceSource = variablesFromAPI(**templateVars)

                                if objectType == 'boot.Iscsi' or (objectType == 'boot.Pxe' and InterfaceSource == 'name'):
                                    policy_list = [
                                        'policies.lan_connectivity_policies.lan_connectivity_policy',
                                    ]
                                    templateVars["allow_opt_out"] = False
                                    for policy in policy_list:
                                        lan_connectivity_policy,policyData = policy_select_loop(jsonData, easy_jsonData, name_prefix, policy, **templateVars)
                                    vnicNames = []
                                    for x in policyData['lan_connectivity_policies']:
                                        for keys, values in x.items():
                                            if keys == lan_connectivity_policy:
                                                for i in values[0]['vnics']:
                                                    for k, v in i.items():
                                                        vnicNames.append(k)

                                                templateVars["var_description"] = 'LAN Connectivity vNIC Names.'
                                                templateVars["jsonVars"] = sorted(vnicNames)
                                                templateVars["defaultVar"] = ''
                                                templateVars["varType"] = 'vNIC Names'
                                                vnicTemplate = variablesFromAPI(**templateVars)
                                                InterfaceName = values[0]['vnics'][0][vnicTemplate][0]['name']
                                                Slot = values[0]['vnics'][0][vnicTemplate][0]['placement_slot_id']

                                    if objectType == 'boot.Iscsi':
                                        Port = 0
                                    else:
                                        Port = -1
                                        MacAddress = ''

                                if objectType == 'boot.Pxe':
                                    if InterfaceSource == 'mac':
                                        templateVars["Description"] = jsonVars['MacAddress']['description']
                                        templateVars["varDefault"] = ''
                                        templateVars["varInput"] = 'The MAC Address of the adapter on the underlying Virtual NIC:'
                                        templateVars["varName"] = 'Mac Address'
                                        templateVars["varRegex"] = jsonVars['MacAddress']['pattern']
                                        templateVars["minLength"] = 17
                                        templateVars["maxLength"] = 17
                                        MacAddress = varStringLoop(**templateVars)
                                        InterfaceName = ''
                                        Port = -1
                                    elif InterfaceSource == 'port':
                                        templateVars["Description"] = jsonVars['Port']['description']
                                        templateVars["varDefault"] =  jsonVars['Port']['default']
                                        templateVars["varInput"] = 'The Port ID of the adapter on the underlying Virtual NIC:'
                                        templateVars["varName"] = 'Port'
                                        templateVars["varRegex"] = jsonVars['Port']['pattern']
                                        templateVars["minNum"] = 1
                                        templateVars["maxNum"] = 3
                                        Port = varNumberLoop(**templateVars)
                                        InterfaceName = ''
                                        MacAddress = ''

                                    if not InterfaceSource == 'name':
                                        templateVars["Description"] = jsonVars['Slot']['description']
                                        templateVars["varDefault"] = 'MLOM'
                                        templateVars["varInput"] = 'The Slot ID of the adapter on the underlying Virtual NIC:'
                                        templateVars["varName"] = 'Slot'
                                        templateVars["varRegex"] = jsonVars['Slot']['pattern']
                                        templateVars["minLength"] = 1
                                        templateVars["maxLength"] = 4
                                        Slot = varStringLoop(**templateVars)

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
                                    templateVars["Description"] = jsonVars['Port']['description']
                                    templateVars["varInput"] = 'Enter the Port ID of the Adapter:'
                                    templateVars["varDefault"] = jsonVars['Port']['description']
                                    templateVars["varName"] = 'Port'
                                    templateVars["minNum"] = jsonVars['Port']['minimum']
                                    templateVars["maxNum"] = jsonVars['Port']['maximum']
                                    templateVars["port"] = varNumberLoop(**templateVars)

                                if re.fullmatch('boot\.(PchStorage|San|SdCard)', objectType):
                                    templateVars["Description"] = jsonVars['Lun']['description']
                                    templateVars["varDefault"] =  jsonVars['Lun']['default']
                                    templateVars["varInput"] = 'LUN Identifier:'
                                    templateVars["varName"] = 'LUN ID'
                                    templateVars["varRegex"] = '[\\d]+'
                                    templateVars["minNum"] = jsonVars['Lun']['minimum']
                                    templateVars["maxNum"] = jsonVars['Lun']['maximum']
                                    Lun = varNumberLoop(**templateVars)
                                    boot_device.update({'lun':Lun})

                                if objectType == 'boot.San':
                                    policy_list = [
                                        'policies.san_connectivity_policies.san_connectivity_policy',
                                    ]
                                    templateVars["allow_opt_out"] = False
                                    for policy in policy_list:
                                        san_connectivity_policy,policyData = policy_select_loop(jsonData, easy_jsonData, name_prefix, policy, **templateVars)
                                    vnicNames = []
                                    for x in policyData['san_connectivity_policies']:
                                        for keys, values in x.items():
                                            if keys == san_connectivity_policy:
                                                for i in values[0]['vhbas']:
                                                    for k, v in i.items():
                                                        vnicNames.append(k)

                                                templateVars["var_description"] = 'SAN Connectivity vNIC Names.'
                                                templateVars["jsonVars"] = sorted(vnicNames)
                                                templateVars["defaultVar"] = ''
                                                templateVars["varType"] = 'vHBA Names'
                                                vnicTemplate = variablesFromAPI(**templateVars)
                                                InterfaceName = values[0]['vhbas'][0][vnicTemplate][0]['name']
                                                Slot = values[0]['vhbas'][0][vnicTemplate][0]['placement_slot_id']

                                    templateVars["Description"] = jsonVars['Wwpn']['description']
                                    templateVars["varDefault"] = ''
                                    templateVars["varInput"] = 'WWPN of the Target Appliance:'
                                    templateVars["varName"] = 'WWPN'
                                    templateVars["varRegex"] = jsonVars['Wwpn']['pattern']
                                    templateVars["minLength"] = 23
                                    templateVars["maxLength"] = 23
                                    Wwpn = varStringLoop(**templateVars)

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
                                    templateVars["var_description"] = jsonVars['Subtype']['description']
                                    templateVars["jsonVars"] = sorted(jsonVars['Subtype']['enum'])
                                    templateVars["defaultVar"] = jsonVars['Subtype']['default']
                                    templateVars["varType"] = 'Sub type'
                                    Subtype = variablesFromAPI(**templateVars)

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
                                        templateVars["boot_devices"].append(boot_device)
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
                    print(f'    boot_mode          = "{templateVars["boot_mode"]}"')
                    print(f'    description        = "{templateVars["descr"]}"')
                    print(f'    enable_secure_boot = {templateVars["enable_secure_boot"]}')
                    print(f'    name               = "{templateVars["name"]}"')
                    if len(templateVars['boot_devices']) > 0:
                        print(f'    boot_devices = ''{')
                        for i in templateVars['boot_devices']:
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
                            templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
                            write_to_template(self, **templateVars)

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

    #==============================================
    # Certificate Management Policy Module
    #==============================================
    def certificate_management_policies(self, jsonData, easy_jsonData, **kwargs):
        name_prefix = self.name_prefix
        name_suffix = 'cert_mgmt'
        opSystem = kwargs['opSystem']
        org = self.org
        policy_type = 'Certificate Management Policy'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'certificate_management_policies'
        tfDir = kwargs['tfDir']

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  A {policy_type} Allows you to specify the certificate and private key-pair ')
            print(f'  details for an external certificate.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            if opSystem == 'Windows':
                print(f'  - {tfDir}\\{org}\\{self.type}\\{templateVars["template_type"]}.auto.tfvars')
            else:
                print(f'  - {tfDir}/{org}/{self.type}/{templateVars["template_type"]}.auto.tfvars')
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

                    templateVars["name"] = policy_name(name, policy_type)
                    templateVars["descr"] = policy_descr(templateVars["name"], policy_type)

                    # Pull in the Policies for Certificate Management
                    jsonVars = jsonData['components']['schemas']['certificatemanagement.CertificateBase']['allOf'][1]['properties']
                    templateVars["multi_select"] = False

                    # Request Certificate
                    templateVars["Multi_Line_Input"] = True
                    templateVars["Description"] = jsonVars['Certificate']['description']
                    templateVars["Variable"] = f'base64_certificate_{loop_count}'
                    certificate = sensitive_var_value(jsonData, **templateVars)
                    templateVars["certificate"] = loop_count

                    # Encode the Certificate as Base64
                    base64Cert = base64.b64encode(str.encode(certificate)).decode()
                    print('base64 encoded:')
                    print(base64Cert)
                    TF_VAR = f'base64_certificate_{loop_count}'
                    os.environ[TF_VAR] = base64Cert

                    # Request Private Key
                    templateVars["Multi_Line_Input"] = True
                    templateVars["Description"] = jsonVars['Privatekey']['description']
                    templateVars["Variable"] = f'base64_private_key_{loop_count}'
                    privateKey = sensitive_var_value(jsonData, **templateVars)
                    templateVars["private_key"] = loop_count

                    # Encode the Certificate as Base64
                    base64Key = base64.b64encode(str.encode(privateKey)).decode()
                    print('base64 encoded:')
                    print(base64Key)
                    TF_VAR = f'base64_certificate_{loop_count}'
                    os.environ[TF_VAR] = base64Key

                    templateVars["enabled"] = True
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'    certificate = {templateVars["certificate"]}')
                    print(f'    description = "{templateVars["descr"]}"')
                    print(f'    enabled     = {templateVars["enabled"]}')
                    print(f'    name        = "{templateVars["name"]}"')
                    print(f'    private_key = {templateVars["private_key"]}')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
                        if confirm_policy == 'Y' or confirm_policy == '':
                            confirm_policy = 'Y'

                            # Write Policies to Template File
                            templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
                            write_to_template(self, **templateVars)

                            configure_loop, policy_loop = exit_default_no(templateVars["policy_type"])
                            print(f'configure loop is {configure_loop}')
                            print(f'policy loop is {policy_loop}')
                            loop_count += 1
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

    #==============================================
    # Device Connector Policy Module
    #==============================================
    def device_connector_policies(self, jsonData, easy_jsonData, **kwargs):
        name_prefix = self.name_prefix
        name_suffix = 'devcon'
        opSystem = kwargs['opSystem']
        org = self.org
        policy_type = 'Device Connector Policy'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'device_connector_policies'
        tfDir = kwargs['tfDir']

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

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
                print(f'  - {tfDir}\\{org}\\{self.type}\\{templateVars["template_type"]}.auto.tfvars')
            else:
                print(f'  - {tfDir}/{org}/{self.type}/{templateVars["template_type"]}.auto.tfvars')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure a {policy_type}?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                policy_loop = False
                while policy_loop == False:

                    if not name_prefix == '':
                        name = '%s_%s' % (name_prefix, name_suffix)
                    else:
                        name = '%s_%s' % (org, name_suffix)

                    templateVars["name"] = policy_name(name, policy_type)
                    templateVars["descr"] = policy_descr(templateVars["name"], policy_type)

                    jsonVars = jsonData['components']['schemas']['deviceconnector.Policy']['allOf'][1]['properties']
                    templateVars["Description"] = jsonVars['LockoutEnabled']['description']
                    templateVars["varInput"] = f'Do you want to lock down Configuration to Intersight only?'
                    templateVars["varDefault"] = 'N'
                    templateVars["varName"] = 'Lockout Enabled'
                    templateVars["configuration_lockout"] = varBoolLoop(**templateVars)

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  ')
                    print(f'   configuration_lockout = {templateVars["configuration_lockout"]}')
                    print(f'   description           = "{templateVars["descr"]}"')
                    print(f'   name                  = "{templateVars["name"]}"')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
                        if confirm_policy == 'Y' or confirm_policy == '':
                            confirm_policy = 'Y'

                            # Write Policies to Template File
                            templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
                            write_to_template(self, **templateVars)

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

    #==============================================
    # Firmware - UCS Domain Module
    #==============================================
    def firmware_ucs_domain(self, jsonData, easy_jsonData, **kwargs):
        templateVars = {}
        templateVars["header"] = 'UCS Domain Profile Variables'
        templateVars["initial_write"] = True
        templateVars["org"] = self.org
        templateVars["policy_type"] = 'UCS Domain Profile'
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'ntp_policies'
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
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'flow_control_policies'
        tfDir = kwargs['tfDir']

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  The Flow Control Policy will enable Priority Flow Control on the Fabric Interconnects.')
            print(f'  We recommend the default parameters so you will only be asked for the name and')
            print(f'  description for the Policy.  You only need one of these policies for Organization')
            print(f'  {org}.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            if opSystem == 'Windows':
                print(f'  - {tfDir}\\{org}\\{self.type}\\{templateVars["template_type"]}.auto.tfvars')
            else:
                print(f'  - {tfDir}/{org}/{self.type}/{templateVars["template_type"]}.auto.tfvars')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            policy_loop = False
            while policy_loop == False:

                if not name_prefix == '':
                    name = '%s_%s' % (name_prefix, name_suffix)
                else:
                    name = '%s_%s' % (org, name_suffix)

                templateVars["name"] = policy_name(name, policy_type)
                templateVars["descr"] = policy_descr(templateVars["name"], policy_type)

                templateVars["priority"] = 'auto'
                templateVars["receive"] = 'Disabled'
                templateVars["send"] = 'Disabled'

                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'    description = "{templateVars["descr"]}"')
                print(f'    name        = "{templateVars["name"]}"')
                print(f'    priority    = "{templateVars["priority"]}"')
                print(f'    receive     = "{templateVars["receive"]}"')
                print(f'    send        = "{templateVars["send"]}"')
                print(f'\n-------------------------------------------------------------------------------------------\n')
                valid_confirm = False
                while valid_confirm == False:
                    confirm_policy = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                    if confirm_policy == 'Y' or confirm_policy == '':
                        confirm_policy = 'Y'

                        # Write Policies to Template File
                        templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
                        write_to_template(self, **templateVars)

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

        # Close the Template file
        templateVars["template_file"] = 'template_close.jinja2'
        write_to_template(self, **templateVars)

    #==============================================
    # IMC Access Policy Module
    #==============================================
    def imc_access_policies(self, jsonData, easy_jsonData, **kwargs):
        name_prefix = self.name_prefix
        name_suffix = 'imc_access'
        opSystem = kwargs['opSystem']
        org = self.org
        policy_type = 'IMC Access Policy'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'imc_access_policies'
        tfDir = kwargs['tfDir']

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  You will need to configure an IMC Access Policy in order to Assign the VLAN and IPs to ')
            print(f'  the Servers for KVM Access.  At this time only inband access is supported in IMM mode.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            if opSystem == 'Windows':
                print(f'  - {tfDir}\\{org}\\{self.type}\\{templateVars["template_type"]}.auto.tfvars')
            else:
                print(f'  - {tfDir}/{org}/{self.type}/{templateVars["template_type"]}.auto.tfvars')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            loop_count = 0
            policy_loop = False
            while policy_loop == False:
                if not name_prefix == '':
                    name = '%s_%s' % (name_prefix, name_suffix)
                else:
                    name = '%s_%s' % (org, name_suffix)

                templateVars["name"] = policy_name(name, policy_type)
                templateVars["descr"] = policy_descr(templateVars["name"], policy_type)
                templateVars["default_vlan"] = 0

                templateVars["multi_select"] = False
                jsonVars = jsonData['components']['schemas']['server.BaseProfile']['allOf'][1]['properties']
                templateVars["var_description"] = jsonVars['TargetPlatform']['description']
                templateVars["jsonVars"] = sorted(jsonVars['TargetPlatform']['enum'])
                templateVars["defaultVar"] = 'FIAttached'
                templateVars["varType"] = 'Target Platform'
                templateVars["target_platform"] = variablesFromAPI(**templateVars)

                # IMC Access Type
                jsonVars = jsonData['components']['schemas']['access.Policy']['allOf'][1]['properties']
                templateVars["var_description"] = jsonVars['ConfigurationType']['description']
                templateVars["jsonVars"] = ['inband', 'out_of_band']
                templateVars["defaultVar"] = 'inband'
                templateVars["varType"] = 'IMC Access Type'
                imcBand = variablesFromAPI(**templateVars)

                policy_list = [
                    f'pools.ip_pools.{imcBand}_ip_pool'
                ]
                templateVars["allow_opt_out"] = False
                for policy in policy_list:
                    policy_type = policy.split('.')[2]
                    templateVars[policy_type],policyData = policy_select_loop(jsonData, easy_jsonData, name_prefix, policy, **templateVars)

                if imcBand == 'inband':
                    valid = False
                    while valid == False:
                        templateVars["inband_vlan_id"] = input('What VLAN Do you want to Assign to this Policy? ')
                        valid_vlan = validating.number_in_range('VLAN ID', templateVars["inband_vlan_id"], 1, 4094)
                        if valid_vlan == True:
                            if templateVars["target_platform"] == 'FIAttached':
                                policy_list = [
                                    'policies.vlan_policies.vlan_policy',
                                ]
                                templateVars["allow_opt_out"] = False
                                for policy in policy_list:
                                    vlan_policy,policyData = policy_select_loop(jsonData, easy_jsonData, name_prefix, policy, **templateVars)
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
                                vlan_list = vlan_list_full(vlan_convert)
                                vlan_count = 0
                                for vlan in vlan_list:
                                    if int(templateVars["inband_vlan_id"]) == int(vlan):
                                        vlan_count = 1
                                        break
                                if vlan_count == 0:
                                    vlan_string = ', '.join(map(str,vlan_list))
                                    print(f'\n-------------------------------------------------------------------------------------------\n')
                                    print(f'  Error with Inband VLAN Assignment!!  The VLAN {templateVars["inband_vlan_id"]} is not in the VLAN Policy')
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
                        templateVars["ipv4_address_configuration"] = True
                        valid = True
                    else:
                        templateVars["ipv4_address_configuration"] = False
                        valid = True

                valid = False
                while valid == False:
                    enable_ipv4 = input('Do you want to enable IPv6 for this Policy?  Enter "Y" or "N" [N]: ')
                    if enable_ipv4 == 'Y':
                        templateVars["ipv6_address_configuration"] = True
                        valid = True
                    else:
                        templateVars["ipv6_address_configuration"] = False
                        valid = True

                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'   description                = "{templateVars["descr"]}"')
                if imcBand == 'inband':
                    print(f'   inband_ip_pool             = "{templateVars["inband_ip_pool"]}"')
                    print(f'   inband_vlan_id             = {templateVars["inband_vlan_id"]}')
                print(f'   ipv4_address_configuration = {templateVars["ipv4_address_configuration"]}')
                print(f'   ipv6_address_configuration = {templateVars["ipv6_address_configuration"]}')
                if imcBand == 'out_of_band':
                    print(f'   out_of_band_ip_pool        = "{templateVars["out_of_band_ip_pool"]}"')
                print(f'\n-------------------------------------------------------------------------------------------\n')
                valid_confirm = False
                while valid_confirm == False:
                    confirm_policy = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                    if confirm_policy == 'Y' or confirm_policy == '':
                        confirm_policy = 'Y'

                        # Write Policies to Template File
                        templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
                        write_to_template(self, **templateVars)

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

        # Close the Template file
        templateVars["template_file"] = 'template_close.jinja2'
        write_to_template(self, **templateVars)

    #==============================================
    # IPMI over LAN Policy Module
    #==============================================
    def ipmi_over_lan_policies(self, jsonData, easy_jsonData, **kwargs):
        name_prefix = self.name_prefix
        name_suffix = 'ipmi'
        opSystem = kwargs['opSystem']
        org = self.org
        policy_type = 'IPMI over LAN Policy'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'ipmi_over_lan_policies'
        tfDir = kwargs['tfDir']

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  An {policy_type} will configure IPMI over LAN access on a Server Profile.  This policy')
            print(f'  allows you to determine whether IPMI commands can be sent directly to the server, using ')
            print(f'  the IP address.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            if opSystem == 'Windows':
                print(f'  - {tfDir}\\{org}\\{self.type}\\{templateVars["template_type"]}.auto.tfvars')
            else:
                print(f'  - {tfDir}/{org}/{self.type}/{templateVars["template_type"]}.auto.tfvars')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure an {policy_type}?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                policy_loop = False
                while policy_loop == False:

                    if not name_prefix == '':
                        name = '%s_%s' % (name_prefix, name_suffix)
                    else:
                        name = '%s_%s' % (org, name_suffix)

                    templateVars["name"] = policy_name(name, policy_type)
                    templateVars["descr"] = policy_descr(templateVars["name"], policy_type)
                    templateVars["enabled"] = True

                    valid = False
                    while valid == False:
                        encrypt_traffic = input('Do you want to encrypt IPMI over LAN Traffic?  Enter "Y" or "N" [Y]: ')
                        if encrypt_traffic == 'Y' or encrypt_traffic == '':
                            templateVars["ipmi_key"] = ipmi_key_function(**templateVars)

                    templateVars["multi_select"] = False
                    jsonVars = jsonData['components']['schemas']['ipmioverlan.Policy']['allOf'][1]['properties']
                    templateVars["var_description"] = jsonVars['Privilege']['description']
                    templateVars["jsonVars"] = sorted(jsonVars['Privilege']['enum'])
                    templateVars["defaultVar"] = jsonVars['Privilege']['default']
                    templateVars["varType"] = 'Privilege'
                    templateVars["privilege"] = variablesFromAPI(**templateVars)

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'   description = "{templateVars["descr"]}"')
                    print(f'   enabled     = {templateVars["enabled"]}')
                    if templateVars["ipmi_key"]:
                        print(f'   ipmi_key    = "Sensitive_value"')
                    print(f'   name        = "{templateVars["name"]}"')
                    print(f'   privilege   = "{templateVars["privilege"]}"')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                        if confirm_policy == 'Y' or confirm_policy == '':
                            confirm_policy = 'Y'

                            # Write Policies to Template File
                            templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
                            write_to_template(self, **templateVars)

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

    #==============================================
    # Intersight Module
    #==============================================
    def intersight(self, easy_jsonData, tfcb_config):
        org = self.org
        policy_type = 'Intersight'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'intersight'
        policyVar = self.type

        templateVars["org"] = org
        for item in tfcb_config:
            for k, v in item.items():
                if k == 'backend':
                    templateVars["backend"] = v
                elif k == 'tfc_organization':
                    templateVars["tfc_organization"] = v
                if policyVar == 'policies':
                    if k == 'pools':
                        templateVars["pools_ws"] = v
                    elif k == 'ucs_domain_profiles':
                        templateVars["domain_profiles_ws"] = v
                elif policyVar == 'profiles':
                    if k == 'pools':
                        templateVars["pools_ws"] = v
                    elif k == 'policies':
                        templateVars["policies_ws"] = v

        templateVars["tags"] = '[{ key = "Module", value = "terraform-intersight-easy-imm" }, { key = "Version", value = "'f'{easy_jsonData["version"]}''" }]'

        # Write Policies to Template File
        templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
        write_to_template(self, **templateVars)

    #==============================================
    # LDAP Policy Module
    #==============================================
    def ldap_policies(self, jsonData, easy_jsonData, **kwargs):
        name_prefix = self.name_prefix
        name_suffix = 'ldap'
        opSystem = kwargs['opSystem']
        org = self.org
        policy_type = 'LDAP Policy'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'ldap_policies'
        tfDir = kwargs['tfDir']

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  An {policy_type} stores and maintains directory information in a network. When LDAP is ')
            print(f'  enabled in the Cisco IMC, user authentication and role authorization is performed by the ')
            print(f'  LDAP server for user accounts not found in the local user database. You can enable and ')
            print(f'  configure LDAP, and configure LDAP servers and LDAP groups.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            if opSystem == 'Windows':
                print(f'  - {tfDir}\\{org}\\{self.type}\\{templateVars["template_type"]}.auto.tfvars')
            else:
                print(f'  - {tfDir}/{org}/{self.type}/{templateVars["template_type"]}.auto.tfvars')
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

                    templateVars["name"] = policy_name(name, policy_type)
                    templateVars["descr"] = policy_descr(templateVars["name"], policy_type)
                    templateVars["enable_ldap"] = True

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
                            templateVars["minNum"] = 0
                            templateVars["maxNum"] = 180
                            templateVars["varName"] = 'LDAP Timeout'
                            varValue = base_timeout
                            valid = validating.number_in_range(templateVars["varName"], varValue, templateVars["minNum"], templateVars["maxNum"])
                        else:
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            print(f'  Error!! Invalid Value.  Please enter a number in the range of 0 to 180.')
                            print(f'\n-------------------------------------------------------------------------------------------\n')

                    templateVars["base_settings"] = {
                        'base_dn':base_dn,
                        'domain':domain,
                        'timeout':base_timeout
                    }

                    templateVars["multi_select"] = False
                    jsonVars = jsonData['components']['schemas']['iam.LdapBaseProperties']['allOf'][1]['properties']
                    templateVars["var_description"] = jsonVars['BindMethod']['description']
                    templateVars["jsonVars"] = sorted(jsonVars['BindMethod']['enum'])
                    templateVars["defaultVar"] = jsonVars['BindMethod']['default']
                    templateVars["varType"] = 'LDAP Bind Method'
                    bind_method = variablesFromAPI(**templateVars)

                    if not bind_method == 'LoginCredentials':
                        valid = False
                        while valid == False:
                            varUser = input(f'What is the username you want to use for authentication? ')
                            varOU = input(f'What is the Organizational Unit for {varUser}? ')
                            bind_dn = input(f'What is the Distinguished Name for the user? [CN={varUser},OU={varOU},{base_dn}]')
                            if bind_dn == '':
                                bind_dn = 'CN=%s,OU=%s,%s' % (varUser, varOU, base_dn)
                            templateVars["minLength"] = 1
                            templateVars["maxLength"] = 254
                            templateVars["varName"] = 'LDAP Bind DN'
                            varValue = bind_dn
                            valid = validating.string_length(templateVars["varName"], varValue, templateVars["minLength"], templateVars["maxLength"])

                        valid = False
                        while valid == False:
                            secure_passphrase = stdiomask.getpass(prompt='What is the password of the user for initial bind process? ')
                            templateVars["minLength"] = 1
                            templateVars["maxLength"] = 254
                            templateVars["rePattern"] = '^[\\S]+$'
                            templateVars["varName"] = 'LDAP Password'
                            varValue = secure_passphrase
                            valid_passphrase = validating.length_and_regex_sensitive(templateVars["rePattern"], templateVars["varName"], varValue, templateVars["minLength"], templateVars["maxLength"])
                            if valid_passphrase == True:
                                os.environ['TF_VAR_binding_parameters_password'] = '%s' % (secure_passphrase)
                                valid = True
                        templateVars["binding_parameters"] = {
                            'bind_dn':bind_dn,
                            'bind_method':bind_method
                        }
                    else:
                        templateVars["binding_parameters"] = {
                            'bind_method':bind_method
                        }
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  Secure LDAP is not supported but LDAP encryption is.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid = False
                    while valid == False:
                        enable_encryption = input(f'\nDo you want to encrypt all information sent to the LDAP server?  Enter "Y" or "N" [Y]: ')
                        if enable_encryption == 'N':
                            templateVars["enable_encryption"] = False
                            valid = True
                        elif enable_encryption == '' or enable_encryption == 'Y':
                            templateVars["enable_encryption"] = True
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
                            templateVars["enable_group_authorization"] = False
                            valid = True
                        elif group_auth == '' or group_auth == 'Y':
                            templateVars["enable_group_authorization"] = True
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
                        templateVars["multi_select"] = False
                        jsonVars = jsonData['components']['schemas']['iam.LdapDnsParameters']['allOf'][1]['properties']
                        templateVars["var_description"] = jsonVars['Source']['description']
                        templateVars["jsonVars"] = sorted(jsonVars['Source']['enum'])
                        templateVars["defaultVar"] = jsonVars['Source']['default']
                        templateVars["varType"] = 'LDAP Domain Source'
                        varSource = variablesFromAPI(**templateVars)

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
                            templateVars["ldap_From_dns"] = {
                                'enable':True,
                                'search_domain':searchDomain,
                                'search_forest':searchForest,
                                'source':varSource
                            }
                        else:
                            templateVars["ldap_From_dns"] = {
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

                    templateVars["search_parameters"] = {
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
                            templateVars["minNum"] = 1
                            templateVars["maxNum"] = 128
                            templateVars["varName"] = 'Nested Group Search Depth'
                            varValue = varNested
                            valid = validating.number_in_range(templateVars["varName"], varValue, templateVars["minNum"], templateVars["maxNum"])
                        else:
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            print(f'  Error!! Invalid Value.  Please enter a port in the range of {templateVars["minNum"]} and {templateVars["maxNum"]}.')
                            print(f'\n-------------------------------------------------------------------------------------------\n')

                    templateVars["nested_group_search_depth"] = varNested

                    templateVars["multi_select"] = False
                    jsonVars = jsonData['components']['schemas']['iam.LdapPolicy']['allOf'][1]['properties']
                    templateVars["var_description"] = jsonVars['UserSearchPrecedence']['description']
                    templateVars["jsonVars"] = sorted(jsonVars['UserSearchPrecedence']['enum'])
                    templateVars["defaultVar"] = jsonVars['UserSearchPrecedence']['default']
                    templateVars["varType"] = 'User Search Precedence'
                    templateVars["user_search_precedence"] = variablesFromAPI(**templateVars)

                    templateVars["ldap_groups"] = []
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
                                        templateVars["minLength"] = 1
                                        templateVars["maxLength"] = 127
                                        templateVars["rePattern"] = '^([^+\\-][a-zA-Z0-9\\=\\!\\#\\$\\%\\(\\)\\+,\\-\\.\\:\\;\\@ \\_\\{\\|\\}\\~\\?\\&]+)$'
                                        templateVars["varName"] = 'LDAP Group'
                                        varValue = varGroup
                                        valid = validating.length_and_regex(templateVars["rePattern"], templateVars["varName"], varValue, templateVars["minLength"], templateVars["maxLength"])
                                    else:
                                        print(f'\n-------------------------------------------------------------------------------------------\n')
                                        print(f'  Error!! Invalid Value.  Please Re-enter the LDAP Group.')
                                        print(f'\n-------------------------------------------------------------------------------------------\n')

                                templateVars["multi_select"] = False
                                jsonVars = easy_jsonData['policies']['iam.LdapPolicy']
                                templateVars["var_description"] = jsonVars['role']['description']
                                templateVars["jsonVars"] = sorted(jsonVars['role']['enum'])
                                templateVars["defaultVar"] = jsonVars['role']['default']
                                templateVars["varType"] = 'Group Role'
                                role = variablesFromAPI(**templateVars)

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
                                        templateVars["ldap_groups"].append(ldap_group)
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

                    templateVars["ldap_servers"] = []
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
                                    templateVars["varName"] = 'LDAP Server'
                                    varValue = varServer
                                    if re.fullmatch(r'^([0-9]{1,3}\.){3}[0-9]{1,3}$', varServer):
                                        valid = validating.ip_address(templateVars["varName"], varValue)
                                    else:
                                        valid = validating.dns_name(templateVars["varName"], varValue)

                                valid = False
                                while valid == False:
                                    if templateVars["enable_encryption"] == True:
                                        xPort = 636
                                    else:
                                        xPort = 389
                                    varPort = input(f'What is Port for {varServer}? [{xPort}]: ')
                                    if varPort == '':
                                        varPort = xPort
                                    if re.fullmatch(r'^[0-9]+', str(varPort)):
                                        templateVars["minNum"] = 1
                                        templateVars["maxNum"] = 65535
                                        templateVars["varName"] = 'Server Port'
                                        varValue = varPort
                                        valid = validating.number_in_range(templateVars["varName"], varValue, templateVars["minNum"], templateVars["maxNum"])
                                    else:
                                        print(f'\n-------------------------------------------------------------------------------------------\n')
                                        print(f'  Error!! Invalid Value.  Please enter a port in the range of {templateVars["minNum"]} and {templateVars["maxNum"]}.')
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
                                        templateVars["ldap_servers"].append(ldap_server)
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
                    print(f'      base_dn = "{templateVars["base_settings"]["base_dn"]}"')
                    print(f'      domain  = "{templateVars["base_settings"]["domain"]}"')
                    print(f'      timeout = "{templateVars["base_settings"]["timeout"]}"')
                    print(f'    ''}')
                    print(f'    binding_parameters = ''{')
                    if not bind_method == 'LoginCredentials':
                        print(f'      bind_dn     = "{templateVars["binding_parameters"]["bind_dn"]}"')
                    print(f'      bind_method = "{templateVars["binding_parameters"]["bind_method"]}"')
                    print(f'    ''}')
                    print(f'    description                = "{templateVars["descr"]}"')
                    print(f'    enable_encryption          = {templateVars["enable_encryption"]}')
                    print(f'    enable_group_authorization = {templateVars["enable_group_authorization"]}')
                    print(f'    enable_ldap                = {templateVars["enable_ldap"]}')
                    if not ldap_from_dns == False:
                        print(f'    ldap_from_dns = ''{')
                        print(f'      enable        = True')
                        if not varSource == 'Extracted':
                            print(f'      search_domain = "{searchDomain}"')
                            print(f'      search_domain = "{searchForest}"')
                        print(f'      source        = "{varSource}"')
                        print(f'    ''}')
                    print(f'    name                      = "{templateVars["name"]}"')
                    print(f'    nested_group_search_depth = "{templateVars["nested_group_search_depth"]}"')
                    if len(templateVars["ldap_groups"]) > 0:
                        print(f'    ldap_groups = ''{')
                        for item in templateVars["ldap_groups"]:
                            for k, v in item.items():
                                if k == 'group':
                                    print(f'      "{v}" = ''{')
                            for k, v in item.items():
                                if k == 'role':
                                    print(f'        {k} = "{v}"')
                            print(f'      ''}')
                        print(f'    ''}')
                    if len(templateVars["ldap_servers"]) > 0:
                        print(f'    ldap_servers = ''{')
                        for item in templateVars["ldap_servers"]:
                            for k, v in item.items():
                                if k == 'server':
                                    print(f'      "{v}" = ''{')
                            for k, v in item.items():
                                if k == 'port':
                                    print(f'        {k} = {v}')
                            print(f'      ''}')
                        print(f'    ''}')
                    print(f'    user_search_precedence = "{templateVars["user_search_precedence"]}"')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
                        if confirm_policy == 'Y' or confirm_policy == '':
                            confirm_policy = 'Y'

                            # Write Policies to Template File
                            templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
                            write_to_template(self, **templateVars)

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

    #==============================================
    # Link Aggregation Policy Module
    #==============================================
    def link_aggregation_policies(self, jsonData, easy_jsonData, **kwargs):
        name_prefix = self.name_prefix
        name_suffix = 'link_agg'
        opSystem = kwargs['opSystem']
        org = self.org
        policy_type = 'Link Aggregation Policy'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'link_aggregation_policies'
        tfDir = kwargs['tfDir']

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  A Link Aggregation Policy will assign LACP settings to the Ethernet Port-Channels and')
            print(f'  uplinks.  We recommend the default wizard settings so you will only be asked for the ')
            print(f'  name and description for the Policy.  You only need one of these policies for ')
            print(f'  Organization {org}.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            if opSystem == 'Windows':
                print(f'  - {tfDir}\\{org}\\{self.type}\\{templateVars["template_type"]}.auto.tfvars')
            else:
                print(f'  - {tfDir}/{org}/{self.type}/{templateVars["template_type"]}.auto.tfvars')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            policy_loop = False
            while policy_loop == False:

                if not name_prefix == '':
                    name = '%s_%s' % (name_prefix, name_suffix)
                else:
                    name = '%s_%s' % (org, name_suffix)

                templateVars["name"] = policy_name(name, policy_type)
                templateVars["descr"] = policy_descr(templateVars["name"], policy_type)

                templateVars["lacp_rate"] = 'normal'
                templateVars["suspend_individual"] = False

                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'    description        = "{templateVars["descr"]}"')
                print(f'    lacp_rate          = "{templateVars["lacp_rate"]}"')
                print(f'    name               = "{templateVars["name"]}"')
                print(f'    suspend_individual = {templateVars["suspend_individual"]}')
                print(f'\n-------------------------------------------------------------------------------------------\n')
                valid_confirm = False
                while valid_confirm == False:
                    confirm_policy = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                    if confirm_policy == 'Y' or confirm_policy == '':
                        confirm_policy = 'Y'

                        # Write Policies to Template File
                        templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
                        write_to_template(self, **templateVars)

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

        # Close the Template file
        templateVars["template_file"] = 'template_close.jinja2'
        write_to_template(self, **templateVars)

    #==============================================
    # Link Control Policy Module
    #==============================================
    def link_control_policies(self, jsonData, easy_jsonData, **kwargs):
        name_prefix = self.name_prefix
        name_suffix = 'link_ctrl'
        opSystem = kwargs['opSystem']
        org = self.org
        policy_type = 'Link Control Policy'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'link_control_policies'
        tfDir = kwargs['tfDir']

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

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
                print(f'  - {tfDir}\\{org}\\{self.type}\\{templateVars["template_type"]}.auto.tfvars')
            else:
                print(f'  - {tfDir}/{org}/{self.type}/{templateVars["template_type"]}.auto.tfvars')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            policy_loop = False
            while policy_loop == False:

                if not name_prefix == '':
                    name = '%s_%s' % (name_prefix, name_suffix)
                else:
                    name = '%s_%s' % (org, name_suffix)

                templateVars["name"] = policy_name(name, policy_type)
                templateVars["descr"] = policy_descr(templateVars["name"], policy_type)

                templateVars["admin_state"] = 'Enabled'
                templateVars["mode"] = 'normal'

                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'    admin_state = "{templateVars["admin_state"]}"')
                print(f'    description = "{templateVars["descr"]}"')
                print(f'    mode        = "{templateVars["mode"]}"')
                print(f'    name        = "{templateVars["name"]}"')
                print(f'\n-------------------------------------------------------------------------------------------\n')
                valid_confirm = False
                while valid_confirm == False:
                    confirm_policy = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                    if confirm_policy == 'Y' or confirm_policy == '':
                        confirm_policy = 'Y'

                        # Write Policies to Template File
                        templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
                        write_to_template(self, **templateVars)

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

        # Close the Template file
        templateVars["template_file"] = 'template_close.jinja2'
        write_to_template(self, **templateVars)

def policy_select_loop(jsonData, easy_jsonData, name_prefix, policy, **templateVars):
    loop_valid = False
    while loop_valid == False:
        create_policy = True
        inner_policy = policy.split('.')[1]
        inner_type = policy.split('.')[0]
        inner_var = policy.split('.')[2]
        templateVars[inner_var] = ''
        templateVars["policies"],policyData = policies_parse(templateVars["org"], inner_type, inner_policy)
        if not len(templateVars["policies"]) > 0:
            valid = False
            while valid == False:

                x = inner_policy.split('_')
                policy_description = []
                for y in x:
                    y = y.capitalize()
                    policy_description.append(y)
                policy_description = " ".join(policy_description)
                policy_description = policy_description.replace('Ip', 'IP')
                policy_description = policy_description.replace('Lan', 'LAN')
                policy_description = policy_description.replace('San', 'SAN')
                policy_description = policy_description.replace('Vlan', 'VLAN')
                policy_description = policy_description.replace('Vsan', 'VSAN')
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'   There were no {policy_description} found.')
                print(f'\n-------------------------------------------------------------------------------------------\n')

                if 'Policies' in policy_description:
                    policy_description = policy_description.replace('Policies', 'Policy')
                elif 'Pools' in policy_description:
                    policy_description = policy_description.replace('Pools', 'Pool')
                elif 'Profiles' in policy_description:
                    policy_description = policy_description.replace('Profiles', 'Profile')
                elif 'Templates' in policy_description:
                    policy_description = policy_description.replace('Templates', 'Template')

                if templateVars["allow_opt_out"] == True:
                    Question = input(f'Do you want to create a(n) {policy_description}?  Enter "Y" or "N" [Y]: ')
                    if Question == '' or Question == 'Y':
                        create_policy = True
                        valid = True
                    elif Question == 'N':
                        create_policy = False
                        valid = True
                        return templateVars[inner_var],policyData
                else:
                    create_policy = True
                    valid = True

        else:
            templateVars[inner_var] = choose_policy(inner_policy, **templateVars)
            if templateVars[inner_var] == 'create_policy':
                create_policy = True
            elif templateVars[inner_var] == '' and templateVars["allow_opt_out"] == True:
                loop_valid = True
                create_policy = False
                return templateVars[inner_var],policyData
            elif not templateVars[inner_var] == '':
                loop_valid = True
                create_policy = False
                return templateVars[inner_var],policyData
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
                pools(name_prefix, templateVars["org"], inner_type).ip_pools(jsonData, easy_jsonData, **kwargs)
            elif inner_policy == 'lan_connectivity_policies':
                policies_lan(name_prefix, templateVars["org"], inner_type).lan_connectivity_policies(jsonData, easy_jsonData, **kwargs)
            elif inner_policy == 'san_connectivity_policies':
                policies_san(name_prefix, templateVars["org"], inner_type).san_connectivity_policies(jsonData, easy_jsonData, **kwargs)
            elif inner_policy == 'vlan_policies':
                policies_vxan(name_prefix, templateVars["org"], inner_type).vlan_policies(jsonData, easy_jsonData, **kwargs)
