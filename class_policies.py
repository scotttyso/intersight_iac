#!/usr/bin/env python3

import jinja2
import os
import pkg_resources
import re
import stdiomask
import validating
from easy_functions import exit_default_no, exit_default_yes, exit_loop_default_yes
from easy_functions import naming_rule_fabric
from easy_functions import policy_descr, policy_name
from easy_functions import ntp_alternate, ntp_primary
from easy_functions import policy_select_loop
from easy_functions import snmp_trap_servers, snmp_users
from easy_functions import syslog_servers
from easy_functions import variablesFromAPI
from easy_functions import varBoolLoop
from easy_functions import varNumberLoop
from easy_functions import varStringLoop
from easy_functions import vlan_list_full
from easy_functions import write_to_template

ucs_template_path = pkg_resources.resource_filename('class_policies', 'Templates/')

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
    def adapter_configuration_policies(self, jsonData, easy_jsonData):
        name_prefix = self.name_prefix
        name_suffix = 'adapter'
        org = self.org
        policy_type = 'Adapter Configuration Policy'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'adapter_configuration_policies'

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  An {policy_type} configures the Ethernet and Fibre-Channel settings for the ')
            print(f'  Virtual Interface Card (VIC) adapter.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - Intersight/{org}/{self.type}/{templateVars["template_type"]}.auto.tfvars')
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
    def bios_policies(self, jsonData, easy_jsonData):
        name_prefix = self.name_prefix
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
            print(f'  - Intersight/{org}/{self.type}/{templateVars["template_type"]}.auto.tfvars')
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
    def boot_order_policies(self, jsonData, easy_jsonData):
        name_prefix = self.name_prefix
        name_suffix = 'boot_order'
        org = self.org
        policy_type = 'Boot Order Policy'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'boot_order_policies'

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
            print(f'  - Intersight/{org}/{self.type}/{templateVars["template_type"]}.auto.tfvars')
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
                            templateVars["template_file"] = '%s.jinja2' % ('boot_policies')
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
    # Device Connector Policy Module
    #==============================================
    def device_connector_policies(self, jsonData, easy_jsonData):
        name_prefix = self.name_prefix
        name_suffix = 'devcon'
        org = self.org
        policy_type = 'Device Connector Policy'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'device_connector_policies'

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
            print(f'  - Intersight/{org}/{self.type}/{templateVars["template_type"]}.auto.tfvars')
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
    def firmware_ucs_domain(self, jsonData, easy_jsonData):
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
    # IMC Access Policy Module
    #==============================================
    def imc_access_policies(self, jsonData, easy_jsonData):
        name_prefix = self.name_prefix
        name_suffix = 'imc_access'
        org = self.org
        policy_type = 'IMC Access Policy'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'imc_access_policies'

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  You will need to configure an IMC Access Policy in order to Assign the VLAN and IPs to ')
            print(f'  the Servers for KVM Access.  At this time only inband access is supported in IMM mode.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - Intersight/{org}/{self.type}/{templateVars["template_type"]}.auto.tfvars')
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
                templateVars["defaultVar"] = jsonVars['TargetPlatform']['default']
                templateVars["varType"] = 'Target Platform'
                templateVars["target_platform"] = variablesFromAPI(**templateVars)

                policy_list = [
                    'pools.ip_pools.inband_ip_pool'
                ]
                templateVars["allow_opt_out"] = False
                for policy in policy_list:
                    templateVars["inband_ip_pool"],policyData = policy_select_loop(jsonData, easy_jsonData, name_prefix, policy, **templateVars)

                valid = False
                while valid == False:
                    templateVars["inband_vlan_id"] = input('What VLAN Do you want to Assign to this Policy? ')
                    valid_vlan = validating.number_in_range('VLAN ID', templateVars["inband_vlan_id"], 1, 4094)
                    if valid_vlan == True:
                        if templateVars["target_platform"] == 'FIAttached':
                            policy_list = [
                                'policies_vlans.vlan_policies.vlan_policy',
                            ]
                            templateVars["allow_opt_out"] = False
                            for policy in policy_list:
                                vlan_policy,policyData = policy_select_loop(jsonData, easy_jsonData, name_prefix, policy, **templateVars)
                            vlan_list = []
                            for item in policyData['vlan_policies']:
                                for key, value in item.items():
                                    if key == vlan_policy:
                                        for i in value[0]['vlans']:
                                            for k, v in i.items():
                                                for x in v:
                                                    for y, val in x.items():
                                                        if y == 'vlan_list':
                                                            vlan_list.append(val)

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
                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                print(f'  Error with Inband VLAN Assignment!!  The VLAN {templateVars["inband_vlan_id"]} is not in the VLAN Policy')
                                print(f'  {vlan_policy}.  VALID VLANs are:{vlan_list}')
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
                print(f'   inband_ip_pool             = "{templateVars["inband_ip_pool"]}"')
                print(f'   inband_vlan_id             = {templateVars["inband_vlan_id"]}')
                print(f'   ipv4_address_configuration = {templateVars["ipv4_address_configuration"]}')
                print(f'   ipv6_address_configuration = {templateVars["ipv6_address_configuration"]}')
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
    def ipmi_over_lan_policies(self, jsonData, easy_jsonData):
        name_prefix = self.name_prefix
        name_suffix = 'ipmi'
        org = self.org
        policy_type = 'IPMI over LAN Policy'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'ipmi_over_lan_policies'

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
            print(f'  - Intersight/{org}/{self.type}/{templateVars["template_type"]}.auto.tfvars')
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
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            print(f'  The ipmi_key Must be in Hexidecimal Format and no longer than 40 characters.')
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            valid_password = False
                            while valid_password == False:
                                ipmi_key = stdiomask.getpass(prompt='Enter ipmi_key: ')
                                valid_password = validating.ipmi_key_check(ipmi_key)

                            templateVars["ipmi_key"] = 1
                            os.environ['TF_VAR_ipmi_key_1'] = '%s' % (ipmi_key)
                            valid = True
                        else:
                            valid = True

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

        templateVars["tfc_organization"] = tfcb_config[0]['tfc_organization']
        templateVars["org"] = org

        if policyVar == 'policies':
            for i in tfcb_config:
                for k, v in i.items():
                    if k == 'pools':
                        templateVars["ws_pools"] = v
                    elif k == 'ucs_chassis_profiles':
                        templateVars["ws_ucs_chassis_profiles"] = v
                    elif k == 'ws_ucs_domain_profiles':
                        templateVars["ws_ucs_domain_profiles"] = v
                    elif k == 'ws_ucs_server_profiles':
                        templateVars["ws_ucs_server_profiles"] = v
        elif policyVar == 'policies_vlans':
             for i in tfcb_config:
                for k, v in i.items():
                    if k == 'ws_ucs_domain_profiles':
                        templateVars["ws_ucs_domain_profiles"] = v
        elif policyVar == 'ucs_server_profiles':
             for i in tfcb_config:
                for k, v in i.items():
                    if k == 'pools':
                        templateVars["ws_pools"] = v

        templateVars["tags"] = '[{ key = "Module", value = "terraform-intersight-easy-imm" }, { key = "Version", value = "'f'{easy_jsonData["version"]}''" }]'

        # Write Policies to Template File
        templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
        write_to_template(self, **templateVars)

    #==============================================
    # LDAP Policy Module
    #==============================================
    def ldap_policies(self, jsonData, easy_jsonData):
        name_prefix = self.name_prefix
        name_suffix = 'ldap'
        org = self.org
        policy_type = 'LDAP Policy'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'ldap_policies'

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
            print(f'  - Intersight/{org}/{self.type}/{templateVars["template_type"]}.auto.tfvars')
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
                            # regex = re.compile(r'^(cn|ou|dc)\=[a-zA-Z0-9\\\,\+\$ ]+$')
                            # bind_split = bind_dn.split(',')
                            # for x in bind_split:
                            #     reg_test = (regex, bind_dn, re.IGNORECASE)
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
                                templateVars["var_description"] = jsonVars['iam.LdapPolicy']['description']
                                templateVars["jsonVars"] = sorted(jsonVars['iam.LdapPolicy']['enum'])
                                templateVars["defaultVar"] = jsonVars['iam.LdapPolicy']['default']
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
    # Local User Policy Module
    #==============================================
    def local_user_policies(self, jsonData, easy_jsonData):
        name_prefix = self.name_prefix
        name_suffix = 'local_users'
        org = self.org
        policy_type = 'Local User Policy'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'local_user_policies'

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  A {policy_type} will configure servers with Local Users for KVM Access.  This Policy ')
            print(f'  is not required to standup a server but is a good practice for day 2 support.\n')
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

                    valid = False
                    while valid == False:
                        always_send = input(f'\nNote: Always Send User Password - If the option is not set to true, user passwords will only \n'\
                            'be sent to endpoint devices for new users and if a user password is changed for existing users.\n\n'\
                            'Do you want Intersight to Always send the user password with policy updates?  Enter "Y" or "N" [N]: ')
                        if always_send == '' or always_send == 'N':
                            templateVars["always_send_user_password"] = False
                            valid = True
                        elif always_send == 'Y':
                            templateVars["always_send_user_password"] = True
                            valid = True
                        else:
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                            print(f'\n-------------------------------------------------------------------------------------------\n')

                    valid = False
                    while valid == False:
                        always_send = input(f'\nEnforce Strong Password, Enables a strong password policy. Strong password requirements:\n'\
                            '  A. The password must have a minimum of 8 and a maximum of 20 characters.\n'\
                            "  B. The password must not contain the User's Name.\n"\
                            '  C. The password must contain characters from three of the following four categories.\n'\
                            '    1. English uppercase characters (A through Z).\n'\
                            '    2. English lowercase characters (a through z).\n'\
                            '    3. Base 10 digits (0 through 9).\n'\
                            '    4. Non-alphabetic characters (! , @, #, $, %, ^, &, *, -, _, +, =)\n\n'\
                            'Do you want to Enforce Strong Passwords?  Enter "Y" or "N" [Y]: ')
                        if always_send == 'N':
                            templateVars["enforce_strong_password"] = False
                            valid = True
                        if always_send == '' or always_send == 'Y':
                            templateVars["enforce_strong_password"] = True
                            valid = True
                        else:
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                            print(f'\n-------------------------------------------------------------------------------------------\n')

                    valid = False
                    while valid == False:
                        always_send = input(f'\nDo you want to Enable password Expiry on the Endpoint?  Enter "Y" or "N" [Y]: ')
                        if always_send == 'N':
                            templateVars["enable_password_expiry"] = False
                            valid = True
                        elif always_send == '' or always_send == 'Y':
                            templateVars["enable_password_expiry"] = True
                            valid = True
                        else:
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                            print(f'\n-------------------------------------------------------------------------------------------\n')

                    if templateVars["enable_password_expiry"] == True:
                        valid = False
                        while valid == False:
                            templateVars["grace_period"] = input(f'\nNote: Grace Period, in days, after the password is expired that a user \n'\
                                'can continue to use their expired password.\n'\
                                'The allowed grace period is between 0 to 5 days.  With 0 being no grace period.\n\n'\
                                'How many days would you like to set for the Grace Period?  [0]: ')
                            if templateVars["grace_period"] == '':
                                templateVars["grace_period"] = 0
                            if re.fullmatch(r'[0-5]', str(templateVars["grace_period"])):
                                valid = validating.number_in_range('Grace Period', templateVars["grace_period"], 0, 5)
                            else:
                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                print(f'  Error!! Invalid Value.  Please enter a number in the range of 0 to 5.')
                                print(f'\n-------------------------------------------------------------------------------------------\n')

                        valid = False
                        while valid == False:
                            templateVars["notification_period"] = input(f'Note: Notification Period - Number of days, between 0 to 15 '\
                                '(0 being disabled),\n that a user is notified to change their password before it expires.\n\n'\
                                'How many days would you like to set for the Notification Period?  [15]: ')
                            if templateVars["notification_period"] == '':
                                templateVars["notification_period"] = 15
                            if re.search(r'^[0-9]+$', str(templateVars["notification_period"])):
                                valid = validating.number_in_range('Notification Period', templateVars["notification_period"], 0, 15)
                            else:
                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                print(f'  Error!! Invalid Value.  Please enter a number in the range of 0 to 15.')
                                print(f'\n-------------------------------------------------------------------------------------------\n')

                        valid = False
                        while valid == False:
                            templateVars["password_expiry_duration"] = input(f'Note: When Password Expiry is Enabled, Password Expiry Duration '\
                                'sets the duration of time,\n (in days), a password may be valid.  The password expiry duration must be greater than \n'\
                                'notification period + grace period.  Range is 1-3650.\n\n'\
                                'How many days would you like to set for the Password Expiry Duration?  [90]: ')
                            if templateVars["password_expiry_duration"] == '':
                                templateVars["password_expiry_duration"] = 90
                            if re.search(r'^[0-9]+$', str(templateVars["password_expiry_duration"])):
                                first_check = validating.number_in_range('Password Expiry Duration', templateVars["password_expiry_duration"], 1, 3650)
                                if first_check == True:
                                    x = int(templateVars["grace_period"])
                                    y = int(templateVars["notification_period"])
                                    if int(templateVars["password_expiry_duration"]) > (x + y):
                                        valid = True
                            else:
                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                print(f'  Error!! Invalid Value.  Please enter a number in the range of 1 to 3650.')
                                print(f'\n-------------------------------------------------------------------------------------------\n')

                        valid = False
                        while valid == False:
                            templateVars["password_history"] = input(f'\nNote: Password change history. Specifies the number of previous passwords \n'\
                                'that are stored and compared to a new password.  Range is 0 to 5.\n\n'\
                                'How many passwords would you like to store for a user?  [5]: ')
                            if templateVars["password_history"] == '':
                                templateVars["password_history"] = 5
                            if re.fullmatch(r'[0-5]', str(templateVars["password_history"])):
                                valid = validating.number_in_range('Password History', templateVars["password_history"], 0, 5)
                            else:
                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                print(f'  Error!! Invalid Value.  Please enter a number in the range of 0 to 5.')
                                print(f'\n-------------------------------------------------------------------------------------------\n')

                    else:
                        templateVars["grace_period"] = 0
                        templateVars["notification_period"] = 15
                        templateVars["password_expiry_duration"] = 90
                        templateVars["password_history"] = 5


                    templateVars["local_users"] = []
                    inner_loop_count = 1
                    user_loop = False
                    while user_loop == False:
                        question = input(f'\nWould you like to configure a Local user?  Enter "Y" or "N" [Y]: ')
                        if question == '' or question == 'Y':
                            valid_users = False
                            while valid_users == False:
                                valid = False
                                while valid == False:
                                    username = input(f'\nName of the user to be created on the endpoint. It can be any string that adheres to the following constraints:\n'\
                                        '  - It can have alphanumeric characters, dots, underscores and hyphen.\n'\
                                        '  - It cannot be more than 16 characters.\n\n'\
                                        'What is your Local username? ')
                                    if not username == '':
                                        valid = validating.username('Local User', username, 1, 16)
                                    else:
                                        print(f'\n-------------------------------------------------------------------------------------------\n')
                                        print(f'  Error!! Invalid Value.  Please Re-enter the Local Username.')
                                        print(f'\n-------------------------------------------------------------------------------------------\n')

                                templateVars["multi_select"] = False
                                jsonVars = easy_jsonData['policies']['iam.LocalUserPasswordPolicy']
                                templateVars["var_description"] = jsonVars['role']['description']
                                templateVars["jsonVars"] = sorted(jsonVars['role']['enum'])
                                templateVars["defaultVar"] = jsonVars['role']['default']
                                templateVars["varType"] = 'User Role'
                                role = variablesFromAPI(**templateVars)

                                if templateVars["enforce_strong_password"] == True:
                                    print('Enforce Strong Password is enabled so the following rules must be followed:')
                                    print('  - The password must have a minimum of 8 and a maximum of 20 characters.')
                                    print("  - The password must not contain the User's Name.")
                                    print('  - The password must contain characters from three of the following four categories.')
                                    print('    * English uppercase characters (A through Z).')
                                    print('    * English lowercase characters (a through z).')
                                    print('    * Base 10 digits (0 through 9).')
                                    print('    * Non-alphabetic characters (! , @, #, $, %, ^, &, *, -, _, +, =)\n\n')
                                valid = False
                                while valid == False:
                                    password1 = stdiomask.getpass(f'What is the password for {username}? ')
                                    password2 = stdiomask.getpass(f'Please re-enter the password for {username}? ')
                                    if not password1 == '':
                                        if password1 == password2:
                                            if templateVars["enforce_strong_password"] == True:
                                                valid = validating.strong_password(f"{username}'s password", password1, 8, 20)

                                            else:
                                                valid = validating.string_length(f'{username} password', password1, 1, 127)

                                        else:
                                            print(f'\n-------------------------------------------------------------------------------------------\n')
                                            print(f'  Error!! The Passwords did not match.  Please Re-enter the password for {username}.')
                                            print(f'\n-------------------------------------------------------------------------------------------\n')
                                    else:
                                        print(f'\n-------------------------------------------------------------------------------------------\n')
                                        print(f'  Error!! Invalid Value.  Please Re-enter the password for {username}.')
                                        print(f'\n-------------------------------------------------------------------------------------------\n')
                                TF_VAR = 'TF_VAR_local_user_password_%s' % (inner_loop_count)
                                os.environ[TF_VAR] = '%s' % (password1)
                                password1 = inner_loop_count

                                user_attributes = {
                                    'enabled':True,
                                    'password':inner_loop_count,
                                    'role':role,
                                    'username':username
                                }

                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                print(f'   enabled  = True')
                                print(f'   password = "Sensitive"')
                                print(f'   role     = "{role}"')
                                print(f'   username = "{username}"')
                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                valid_confirm = False
                                while valid_confirm == False:
                                    confirm_v = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
                                    if confirm_v == 'Y' or confirm_v == '':
                                        templateVars["local_users"].append(user_attributes)
                                        valid_exit = False
                                        while valid_exit == False:
                                            loop_exit = input(f'Would You like to Configure another Local User?  Enter "Y" or "N" [N]: ')
                                            if loop_exit == 'Y':
                                                inner_loop_count += 1
                                                valid_confirm = True
                                                valid_exit = True
                                            elif loop_exit == 'N' or loop_exit == '':
                                                user_loop = True
                                                valid_confirm = True
                                                valid_exit = True
                                                valid_users = True
                                            else:
                                                print(f'\n------------------------------------------------------\n')
                                                print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                                                print(f'\n------------------------------------------------------\n')

                                    elif confirm_v == 'N':
                                        print(f'\n-------------------------------------------------------------------------------------------\n')
                                        print(f'  Starting Local User Configuration Over.')
                                        print(f'\n-------------------------------------------------------------------------------------------\n')
                                        valid_confirm = True
                                    else:
                                        print(f'\n------------------------------------------------------\n')
                                        print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                                        print(f'\n------------------------------------------------------\n')

                        elif question == 'N':
                            user_loop = True
                        else:
                            print(f'\n------------------------------------------------------\n')
                            print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                            print(f'\n------------------------------------------------------\n')

                    templateVars["enabled"] = True
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'    always_send_user_password = {templateVars["always_send_user_password"]}')
                    print(f'    description               = "{templateVars["descr"]}"')
                    print(f'    enable_password_expiry    = {templateVars["enable_password_expiry"]}')
                    print(f'    enforce_strong_password   = {templateVars["enforce_strong_password"]}')
                    print(f'    grace_period              = "{templateVars["grace_period"]}"')
                    print(f'    name                      = "{templateVars["name"]}"')
                    print(f'    password_expiry_duration  = "{templateVars["password_expiry_duration"]}"')
                    print(f'    password_history          = "{templateVars["password_history"]}"')
                    if len(templateVars["local_users"]) > 0:
                        print(f'    local_users = ''{')
                        for item in templateVars["local_users"]:
                            for k, v in item.items():
                                if k == 'username':
                                    print(f'      "{v}" = ''{')
                            for k, v in item.items():
                                if k == 'enabled':
                                    print(f'        enable   = {v}')
                                elif k == 'password':
                                    print(f'        password = "Sensitive"')
                                elif k == 'role':
                                    print(f'        role     = {v}')
                            print(f'      ''}')
                        print(f'    ''}')
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
    # Network Connectivity Policy Module
    #==============================================
    def network_connectivity_policies(self, jsonData, easy_jsonData):
        name_prefix = self.name_prefix
        name_suffix = 'dns'
        org = self.org
        policy_type = 'Network Connectivity Policy'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'network_connectivity_policies'

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  It is strongly recommended to have a Network Connectivity (DNS) Policy for the')
            print(f'  UCS Domain Profile.  Without it, DNS resolution will fail.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - Intersight/{org}/{self.type}/{templateVars["template_type"]}.auto.tfvars')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            policy_loop = False
            while policy_loop == False:

                if not name_prefix == '':
                    name = '%s_%s' % (name_prefix, name_suffix)
                else:
                    name = '%s_%s' % (org, name_suffix)

                templateVars["name"] = policy_name(name, policy_type)
                templateVars["descr"] = policy_descr(templateVars["name"], policy_type)

                valid = False
                while valid == False:
                    templateVars["preferred_ipv4_dns_server"] = input('What is your Primary IPv4 DNS Server?  [208.67.220.220]: ')
                    if templateVars["preferred_ipv4_dns_server"] == '':
                        templateVars["preferred_ipv4_dns_server"] = '208.67.220.220'
                    valid = validating.ip_address('Primary IPv4 DNS Server', templateVars["preferred_ipv4_dns_server"])

                valid = False
                while valid == False:
                    alternate_true = input('Do you want to Configure an Alternate IPv4 DNS Server?  Enter "Y" or "N" [Y]: ')
                    if alternate_true == 'Y' or alternate_true == '':
                        templateVars["alternate_ipv4_dns_server"] = input('What is your Alternate IPv4 DNS Server?  [208.67.222.222]: ')
                        if templateVars["alternate_ipv4_dns_server"] == '':
                            templateVars["alternate_ipv4_dns_server"] = '208.67.222.222'
                        valid = validating.ip_address('Alternate IPv4 DNS Server', templateVars["alternate_ipv4_dns_server"])
                    elif alternate_true == 'N':
                        templateVars["alternate_ipv4_dns_server"] = ''
                        valid = True
                    else:
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                        print(f'\n-------------------------------------------------------------------------------------------\n')

                valid = False
                while valid == False:
                    enable_ipv6 = input('Do you want to Configure IPv6 DNS?  Enter "Y" or "N" [N]: ')
                    if enable_ipv6 == 'Y':
                        templateVars["enable_ipv6"] = True
                        templateVars["preferred_ipv6_dns_server"] = input('What is your Primary IPv6 DNS Server?  [2620:119:35::35]: ')
                        if templateVars["preferred_ipv6_dns_server"] == '':
                            templateVars["preferred_ipv6_dns_server"] = '2620:119:35::35'
                        valid = validating.ip_address('Primary IPv6 DNS Server', templateVars["preferred_ipv6_dns_server"])
                    if enable_ipv6 == 'N' or enable_ipv6 == '':
                        templateVars["enable_ipv6"] = False
                        templateVars["preferred_ipv6_dns_server"] = ''
                        valid = True

                valid = False
                while valid == False:
                    if enable_ipv6 == 'Y':
                        alternate_true = input('Do you want to Configure an Alternate IPv6 DNS Server?  Enter "Y" or "N" [Y]: ')
                        if alternate_true == 'Y' or alternate_true == '':
                            templateVars["alternate_ipv6_dns_server"] = input('What is your Alternate IPv6 DNS Server?  [2620:119:53::53]: ')
                            if templateVars["alternate_ipv6_dns_server"] == '':
                                templateVars["alternate_ipv6_dns_server"] = '2620:119:53::53'
                            valid = validating.ip_address('Alternate IPv6 DNS Server', templateVars["alternate_ipv6_dns_server"])
                        elif alternate_true == 'N':
                            templateVars["alternate_ipv6_dns_server"] = ''
                            valid = True
                        else:
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                    else:
                        templateVars["alternate_ipv6_dns_server"] = ''
                        valid = True

                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'    description = "{templateVars["descr"]}"')
                print(f'    name        = "{templateVars["name"]}"')
                if not templateVars["preferred_ipv4_dns_server"] == '':
                    print(f'    dns_servers_v4 = [')
                    print(f'      {templateVars["preferred_ipv4_dns_server"]},')
                    if not templateVars["alternate_ipv4_dns_server"] == '':
                        print(f'      {templateVars["alternate_ipv4_dns_server"]}')
                    print(f'    ]')
                if not templateVars["preferred_ipv6_dns_server"] == '':
                    print(f'    dns_servers_v6 = [')
                    print(f'      {templateVars["preferred_ipv6_dns_server"]},')
                    if not templateVars["alternate_ipv6_dns_server"] == '':
                        print(f'      {templateVars["alternate_ipv6_dns_server"]}')
                    print(f'    ]')
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
    # NTP Policy Module
    #==============================================
    def ntp_policies(self, jsonData, easy_jsonData):
        name_prefix = self.name_prefix
        name_suffix = 'ntp'
        org = self.org
        policy_type = 'NTP Policy'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'ntp_policies'

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  It is strongly recommended to configure an NTP Policy for the UCS Domain Profile.')
            print(f'  Without an NTP Policy Events can be incorrectly timestamped and Intersight ')
            print(f'  Communication, as an example, could be interrupted with Certificate Validation\n')
            print(f'  checks, as an example.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - Intersight/{org}/{self.type}/{templateVars["template_type"]}.auto.tfvars')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            policy_loop = False
            while policy_loop == False:

                if not name_prefix == '':
                    name = '%s_%s' % (name_prefix, name_suffix)
                else:
                    name = '%s_%s' % (org, name_suffix)

                templateVars["name"] = policy_name(name, policy_type)
                templateVars["descr"] = policy_descr(templateVars["name"], policy_type)

                primary_ntp = ntp_primary()
                alternate_ntp = ntp_alternate()

                templateVars["enabled"] = True
                templateVars["ntp_servers"] = []
                templateVars["ntp_servers"].append(primary_ntp)
                if not alternate_ntp == '':
                    templateVars["ntp_servers"].append(alternate_ntp)

                templateVars["multi_select"] = False
                jsonVars = jsonData['components']['schemas']['appliance.SystemInfo']['allOf'][1]['properties']['TimeZone']['enum']
                tz_regions = []
                for i in jsonVars:
                    tz_region = i.split('/')[0]
                    if not tz_region in tz_regions:
                        tz_regions.append(tz_region)
                tz_regions = sorted(tz_regions)
                templateVars["var_description"] = 'Timezone Regions...'
                templateVars["jsonVars"] = tz_regions
                templateVars["defaultVar"] = 'America'
                templateVars["varType"] = 'Time Region'
                time_region = variablesFromAPI(**templateVars)

                region_tzs = []
                for item in jsonVars:
                    if time_region in item:
                        region_tzs.append(item)

                templateVars["var_description"] = 'Region Timezones...'
                templateVars["jsonVars"] = sorted(region_tzs)
                templateVars["defaultVar"] = ''
                templateVars["varType"] = 'Region Timezones'
                templateVars["timezone"] = variablesFromAPI(**templateVars)

                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'    description = "{templateVars["descr"]}"')
                print(f'    name        = "{templateVars["name"]}"')
                print(f'    timezone    = "{templateVars["timezone"]}"')
                if len(templateVars["ntp_servers"]) > 0:
                    print(f'    ntp_servers = [')
                    for server in templateVars["ntp_servers"]:
                        print(f'      "{server}",')
                    print(f'    ]')
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
    # Persistent Memory Policy Module
    #==============================================
    def persistent_memory_policies(self, jsonData, easy_jsonData):
        name_prefix = self.name_prefix
        name_suffix = 'persistent_memory'
        org = self.org
        policy_type = 'Persistent Memory Policy'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'persistent_memory_policies'

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

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
            print(f'  - Intersight/{org}/{self.type}/{templateVars["template_type"]}.auto.tfvars')
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

                    templateVars["multi_select"] = False
                    jsonVars = jsonData['components']['schemas']['memory.PersistentMemoryPolicy']['allOf'][1]['properties']
                    templateVars["var_description"] = jsonVars['ManagementMode']['description']
                    templateVars["jsonVars"] = sorted(jsonVars['ManagementMode']['enum'])
                    templateVars["defaultVar"] = jsonVars['ManagementMode']['default']
                    templateVars["varType"] = 'Management Mode'
                    templateVars["management_mode"] = variablesFromAPI(**templateVars)

                    if templateVars["management_mode"] == 'configured-from-intersight':
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
                                    templateVars["minLength"] = 8
                                    templateVars["maxLength"] = 32
                                    templateVars["rePattern"] = '^[a-zA-Z0-9\\u0021\\&\\#\\$\\%\\+\\%\\@\\_\\*\\-\\.]+$'
                                    templateVars["varName"] = 'Secure Passphrase'
                                    varValue = secure_passphrase
                                    valid_passphrase = validating.length_and_regex_sensitive(templateVars["rePattern"],
                                        templateVars["varName"],
                                        varValue,
                                        templateVars["minLength"],
                                        templateVars["maxLength"]
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
                            templateVars["memory_mode_percentage"] = input('What is the Percentage of Valatile Memory to assign to this Policy?  [0]: ')
                            if templateVars["memory_mode_percentage"] == '':
                                templateVars["memory_mode_percentage"] = 0
                            if re.search(r'[\d]+', str(templateVars["memory_mode_percentage"])):
                                valid = validating.number_in_range('Memory Mode Percentage', templateVars["memory_mode_percentage"], 1, 100)
                            else:
                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                print(f'  "{templateVars["memory_mode_percentage"]}" is not a valid number.')
                                print(f'\n-------------------------------------------------------------------------------------------\n')

                        jsonVars = jsonData['components']['schemas']['memory.PersistentMemoryGoal']['allOf'][1]['properties']
                        templateVars["var_description"] = jsonVars['PersistentMemoryType']['description']
                        templateVars["jsonVars"] = sorted(jsonVars['PersistentMemoryType']['enum'])
                        templateVars["defaultVar"] = jsonVars['PersistentMemoryType']['default']
                        templateVars["varType"] = 'Persistent Memory Type'
                        templateVars["persistent_memory_type"] = variablesFromAPI(**templateVars)

                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        print(f'  This Flag will enable or Disable the retention of Namespaces between Server Profile')
                        print(f'  association and dissassociation.')
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        valid = False
                        while valid == False:
                            templateVars["retain_namespaces"] = input('Do you want to Retain Namespaces?  Enter "Y" or "N" [Y]: ')
                            if templateVars["retain_namespaces"] == '' or templateVars["retain_namespaces"] == 'Y':
                                templateVars["retain_namespaces"] = True
                                valid = True
                            elif templateVars["retain_namespaces"] == 'N':
                                templateVars["retain_namespaces"] = False
                                valid = True
                            else:
                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                                print(f'\n-------------------------------------------------------------------------------------------\n')

                        templateVars["namespaces"] = []
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
                                    templateVars["minLength"] = 1
                                    templateVars["maxLength"] = 63
                                    templateVars["rePattern"] = '^[a-zA-Z0-9\\#\\_\\-]+$'
                                    templateVars["varName"] = 'Name for the Namespace'
                                    varValue = namespace_name
                                    valid = validating.length_and_regex(templateVars["rePattern"], templateVars["varName"], varValue, templateVars["minLength"], templateVars["maxLength"])

                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                print(f'  Capacity of this Namespace in gibibytes (GiB).  Range is 1-9223372036854775807')
                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                valid = False
                                while valid == False:
                                    capacity = input('What is the Capacity to assign to this Namespace? ')
                                    templateVars["minNum"] = 1
                                    templateVars["maxNum"] = 9223372036854775807
                                    templateVars["varName"] = 'Namespace Capacity'
                                    varValue = int(capacity)
                                    if re.search(r'[\d]+',str(varValue)):
                                        valid = validating.number_in_range(templateVars["varName"], varValue, templateVars["minNum"], templateVars["maxNum"])
                                    else:
                                        print(f'\n-------------------------------------------------------------------------------------------\n')
                                        print(f'  "{varValue}" is not a valid number.')
                                        print(f'\n-------------------------------------------------------------------------------------------\n')

                                jsonVars = jsonData['components']['schemas']['memory.PersistentMemoryLogicalNamespace']['allOf'][1]['properties']
                                templateVars["var_description"] = jsonVars['Mode']['description']
                                templateVars["jsonVars"] = sorted(jsonVars['Mode']['enum'])
                                templateVars["defaultVar"] = jsonVars['Mode']['default']
                                templateVars["varType"] = 'Mode'
                                mode = variablesFromAPI(**templateVars)

                                templateVars["var_description"] = jsonVars['SocketId']['description']
                                templateVars["jsonVars"] = sorted(jsonVars['SocketId']['enum'])
                                templateVars["defaultVar"] = jsonVars['SocketId']['default']
                                templateVars["varType"] = 'Socket Id'
                                socket_id = variablesFromAPI(**templateVars)

                                if templateVars["persistent_memory_type"] == 'app-direct-non-interleaved':
                                    templateVars["var_description"] = jsonVars['SocketMemoryId']['description']
                                    templateVars["jsonVars"] = [x for x in jsonVars['SocketMemoryId']['enum']]
                                    templateVars["defaultVar"] = '2'
                                    templateVars["popList"] = ['Not Applicable']
                                    templateVars["varType"] = 'Socket Memory Id'
                                    socket_memory_id = variablesFromAPI(**templateVars)
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
                                        templateVars["namespaces"].append(namespace)

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
                                            else:
                                                print(f'\n------------------------------------------------------\n')
                                                print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                                                print(f'\n------------------------------------------------------\n')

                                    elif confirm_namespace == 'N':
                                        print(f'\n-------------------------------------------------------------------------------------------\n')
                                        print(f'  Starting namespace Configuration Over.')
                                        print(f'\n-------------------------------------------------------------------------------------------\n')
                                        valid_confirm = True
                                    else:
                                        print(f'\n------------------------------------------------------\n')
                                        print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                                        print(f'\n------------------------------------------------------\n')

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'    description     = "{templateVars["descr"]}"')
                    print(f'    management_mode = "{templateVars["management_mode"]}"')
                    print(f'    name            = "{templateVars["name"]}"')
                    if templateVars["management_mode"]  == 'configured-from-intersight':
                        print(f'    # GOALS')
                        print(f'    memory_mode_percentage = {templateVars["memory_mode_percentage"]}')
                        print(f'    persistent_memory_type = {templateVars["persistent_memory_type"]}')
                        print(f'    # NAMESPACES')
                        print(f'    namespaces = ''{')
                        for item in templateVars["namespaces"]:
                            for k, v in item.items():
                                if k == 'name':
                                    print(f'      "{v}" = ''{')
                            for k, v in item.items():
                                if k == 'capacity':
                                    print(f'        capacity         = {v}')
                                elif k == 'mode':
                                    print(f'        mode             = {v}')
                                elif k == 'socket_id':
                                    print(f'        socket_id        = {v}')
                                elif k == 'socket_memory_id':
                                    print(f'        socket_memory_id = {v}')
                            print(f'      ''}')
                        print(f'    ''}')
                        print(f'   retain_namespaces = "{templateVars["retain_namespaces"]}"')
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
    # Power Policy Module
    #==============================================
    def power_policies(self, jsonData, easy_jsonData):
        name_prefix = self.name_prefix
        org = self.org
        policy_type = 'Power Policy'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'power_policies'

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  A {policy_type} will configure the Power Redundancy Policies for Chassis and Servers.')
            print(f'  For Servers it will configure the Power Restore State.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - Intersight/{org}/{self.type}/{templateVars["template_type"]}.auto.tfvars')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            loop_count = 1
            policy_loop = False
            while policy_loop == False:

                print('staring loop again')
                templateVars["multi_select"] = False
                templateVars["var_description"] = easy_jsonData['policies']['power.Policy']['systemType']['description']
                templateVars["jsonVars"] = sorted(easy_jsonData['policies']['power.Policy']['systemType']['enum'])
                templateVars["defaultVar"] = easy_jsonData['policies']['power.Policy']['systemType']['default']
                templateVars["varType"] = 'System Type'
                system_type = variablesFromAPI(**templateVars)

                if not name_prefix == '':
                    name = '%s_%s' % (name_prefix, system_type)
                else:
                    name = '%s_%s' % (org, system_type)

                templateVars["name"] = policy_name(name, policy_type)
                templateVars["descr"] = policy_descr(templateVars["name"], policy_type)

                if system_type == '9508':
                    valid = False
                    while valid == False:
                        templateVars["allocated_budget"] = input('What is the Power Budget you would like to Apply?\n'
                            'This should be a value between 2800 Watts and 16800 Watts. [5600]: ')
                        if templateVars["allocated_budget"] == '':
                            templateVars["allocated_budget"] = 5600
                        valid = validating.number_in_range('Chassis Power Budget', templateVars["allocated_budget"], 2800, 16800)
                else:
                    templateVars["allocated_budget"] = 0

                templateVars["multi_select"] = False
                jsonVars = jsonData['components']['schemas']['power.Policy']['allOf'][1]['properties']

                if system_type == 'Server':
                    templateVars["var_description"] = jsonVars['PowerRestoreState']['description']
                    templateVars["jsonVars"] = sorted(jsonVars['PowerRestoreState']['enum'])
                    templateVars["defaultVar"] = jsonVars['PowerRestoreState']['default']
                    templateVars["varType"] = 'Power Restore State'
                    templateVars["power_restore_state"] = variablesFromAPI(**templateVars)

                if system_type == '5108':
                    templateVars["popList"] = ['N+2']
                elif system_type == 'Server':
                    templateVars["popList"] = ['N+1','N+2']
                templateVars["var_description"] = jsonVars['RedundancyMode']['description']
                templateVars["jsonVars"] = sorted(jsonVars['RedundancyMode']['enum'])
                templateVars["defaultVar"] = jsonVars['RedundancyMode']['default']
                templateVars["varType"] = 'Power Redundancy Mode'
                templateVars["power_redundancy"] = variablesFromAPI(**templateVars)

                print(f'\n-------------------------------------------------------------------------------------------\n')
                if system_type == '9508':
                    print(f'   allocated_budget    = {templateVars["allocated_budget"]}')
                print(f'   description         = "{templateVars["descr"]}"')
                print(f'   name                = "{templateVars["name"]}"')
                if system_type == 'Server':
                    print(f'   power_restore_state = "{templateVars["power_restore_state"]}"')
                print(f'   redundancy_mode     = "{templateVars["power_redundancy"]}"')
                print(f'\n-------------------------------------------------------------------------------------------\n')
                valid_confirm = False
                while valid_confirm == False:
                    confirm_policy = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                    if confirm_policy == 'Y' or confirm_policy == '':
                        confirm_policy = 'Y'

                        # Write Policies to Template File
                        templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
                        write_to_template(self, **templateVars)

                        if loop_count < 3:
                            configure_loop, policy_loop = exit_default_yes(templateVars["policy_type"])
                        else:
                            configure_loop, policy_loop = exit_default_no(templateVars["policy_type"])
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

        # Close the Template file
        templateVars["template_file"] = 'template_close.jinja2'
        write_to_template(self, **templateVars)

    #==============================================
    # SD Card Policy Module
    #==============================================
    def sd_card_policies(self, jsonData, easy_jsonData):
        name_prefix = self.name_prefix
        name_suffix = 'sdcard'
        org = self.org
        policy_type = 'SD Card Policy'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'sd_card_policies'

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
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

                    templateVars["priority"] = 'auto'
                    templateVars["receive"] = 'Disabled'
                    templateVars["send"] = 'Disabled'

                    # Write Policies to Template File
                    templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
                    write_to_template(self, **templateVars)

                    exit_answer = input(f'Would You like to Configure another {policy_type}?  Enter "Y" or "N" [N]: ')
                    if exit_answer == 'N' or exit_answer == '':
                        policy_loop = True
                        configure_loop = True
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
    # Serial over LAN Policy Module
    #==============================================
    def serial_over_lan_policies(self, jsonData, easy_jsonData):
        name_prefix = self.name_prefix
        name_suffix = 'sol'
        org = self.org
        policy_type = 'Serial over LAN Policy'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'serial_over_lan_policies'

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

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
            print(f'  - Intersight/{org}/{self.type}/{templateVars["template_type"]}.auto.tfvars')
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
                    templateVars["enabled"] = True

                    templateVars["multi_select"] = False
                    jsonVars = jsonData['components']['schemas']['sol.Policy']['allOf'][1]['properties']
                    templateVars["var_description"] = jsonVars['BaudRate']['description']
                    templateVars["jsonVars"] = sorted(jsonVars['BaudRate']['enum'])
                    templateVars["defaultVar"] = jsonVars['BaudRate']['default']
                    templateVars["varType"] = 'Baud Rate'
                    templateVars["baud_rate"] = variablesFromAPI(**templateVars)

                    templateVars["var_description"] = jsonVars['ComPort']['description']
                    templateVars["jsonVars"] = sorted(jsonVars['ComPort']['enum'])
                    templateVars["defaultVar"] = jsonVars['ComPort']['default']
                    templateVars["varType"] = 'Com Port'
                    templateVars["com_port"] = variablesFromAPI(**templateVars)

                    valid = False
                    while valid == False:
                        templateVars["ssh_port"] = input('What is the SSH Port you would like to assign?\n'
                            'This should be a value between 1024-65535. [2400]: ')
                        if templateVars["ssh_port"] == '':
                            templateVars["ssh_port"] = 2400
                        valid = validating.number_in_range('SSH Port', templateVars["ssh_port"], 1024, 65535)

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'   baud_rate   = "{templateVars["baud_rate"]}"')
                    print(f'   com_port    = "{templateVars["com_port"]}"')
                    print(f'   description = "{templateVars["descr"]}"')
                    print(f'   enabled     = "{templateVars["enabled"]}"')
                    print(f'   name        = "{templateVars["name"]}"')
                    print(f'   ssh_port    = "{templateVars["ssh_port"]}"')
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
    # SMTP Policy Module
    #==============================================
    def smtp_policies(self, jsonData, easy_jsonData):
        name_prefix = self.name_prefix
        name_suffix = 'smtp'
        org = self.org
        policy_type = 'SMTP Policy'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'smtp_policies'

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  An {policy_type} sends server faults as email alerts to the configured SMTP server.')
            print(f'  You can specify the preferred settings for outgoing communication and select the fault ')
            print(f'  severity level to report and the mail recipients.\n\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - Intersight/{org}/{self.type}/{templateVars["template_type"]}.auto.tfvars')
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
                    templateVars["enable_smtp"] = True

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  IP address or hostname of the SMTP server. The SMTP server is used by the managed device ')
                    print(f'  to send email notifications.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid = False
                    while valid == False:
                        templateVars["smtp_server_address"] = input('What is the SMTP Server Address? ')
                        if re.search(r'^[a-zA-Z0-9]:', templateVars["smtp_server_address"]):
                            valid = validating.ip_address('SMTP Server Address', templateVars["smtp_server_address"])
                        if re.search(r'[a-zA-Z]', templateVars["smtp_server_address"]):
                            valid = validating.dns_name('SMTP Server Address', templateVars["smtp_server_address"])
                        elif re.search (r'^([0-9]{1,3}\.){3}[0-9]{1,3}$'):
                            valid = validating.ip_address('SMTP Server Address', templateVars["smtp_server_address"])
                        else:
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            print(f'  "{templateVars["smtp_server_address"]}" is not a valid address.')
                            print(f'\n-------------------------------------------------------------------------------------------\n')

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  Port number used by the SMTP server for outgoing SMTP communication.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid = False
                    while valid == False:
                        templateVars["smtp_port"] = input('What is the SMTP Port?  [25]: ')
                        if templateVars["smtp_port"] == '':
                            templateVars["smtp_port"] = 25
                        if re.search(r'[\d]+', str(templateVars["smtp_port"])):
                            valid = validating.number_in_range('SMTP Port', templateVars["smtp_port"], 1, 65535)
                        else:
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            print(f'  "{templateVars["smtp_port"]}" is not a valid port.')
                            print(f'\n-------------------------------------------------------------------------------------------\n')

                    templateVars["multi_select"] = False
                    jsonVars = jsonData['components']['schemas']['smtp.Policy']['allOf'][1]['properties']
                    templateVars["var_description"] = jsonVars['MinSeverity']['description']
                    templateVars["jsonVars"] = sorted(jsonVars['MinSeverity']['enum'])
                    templateVars["defaultVar"] = jsonVars['MinSeverity']['default']
                    templateVars["varType"] = 'Minimum Severity'
                    templateVars["minimum_severity"] = variablesFromAPI(**templateVars)

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  The email address entered here will be displayed as the from address (mail received from ')
                    print(f'  address) of all the SMTP mail alerts that are received. If not configured, the hostname ')
                    print(f'  of the server is used in the from address field.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid = False
                    while valid == False:
                        templateVars["smtp_alert_sender_address"] = input(f'What is the SMTP Alert Sender Address?  '\
                            '[press enter to use server hostname]: ')
                        if templateVars["smtp_alert_sender_address"] == '':
                            templateVars["smtp_alert_sender_address"] = ''
                            valid = True
                        else:
                            valid = validating.email('SMTP Alert Sender Address', templateVars["smtp_alert_sender_address"])

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  List of email addresses that will receive notifications for faults.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    templateVars["mail_alert_recipients"] = []
                    valid = False
                    while valid == False:
                        mail_recipient = input(f'What is address you would like to send these notifications to?  ')
                        valid_email = validating.email('Mail Alert Recipient', mail_recipient)
                        if valid_email == True:
                            templateVars["mail_alert_recipients"].append(mail_recipient)
                            valid_answer = False
                            while valid_answer == False:
                                add_another = input(f'Would you like to add another E-mail?  Enter "Y" or "N" [N]: ')
                                if add_another == '' or add_another == 'N':
                                    valid = True
                                    valid_answer = True
                                elif add_another == 'Y':
                                    valid_answer = True
                                else:
                                    print(f'\n-------------------------------------------------------------------------------------------\n')
                                    print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                                    print(f'\n-------------------------------------------------------------------------------------------\n')

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'    description               = "{templateVars["descr"]}"')
                    print(f'    enable_smtp                   = {templateVars["enable_smtp"]}')
                    print(f'    mail_alert_recipients     = [')
                    for x in templateVars["mail_alert_recipients"]:
                        print(f'      "{x}",')
                    print(f'    ]')
                    print(f'    minimum_severity          = "{templateVars["minimum_severity"]}"')
                    print(f'    name                      = "{templateVars["name"]}"')
                    print(f'    smtp_alert_sender_address = "{templateVars["smtp_alert_sender_address"]}"')
                    print(f'    smtp_port                 = {templateVars["smtp_port"]}')
                    print(f'    smtp_server_address       = "{templateVars["smtp_server_address"]}"')
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
    # SNMP Policy Module
    #==============================================
    def snmp_policies(self, jsonData, easy_jsonData):
        name_prefix = self.name_prefix
        name_suffix = 'snmp'
        org = self.org
        policy_type = 'SNMP Policy'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'snmp_policies'

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  An {policy_type} will configure chassis, domains, and servers with SNMP parameters.')
            print(f'  This Policy is not required to standup a server but is a good practice for day 2 support.')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - Intersight/{org}/{self.type}/{templateVars["template_type"]}.auto.tfvars')
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
                    templateVars["enabled"] = True

                    valid = False
                    while valid == False:
                        templateVars["port"] = input(f'Note: The following Ports cannot be chosen: [22, 23, 80, 123, 389, 443, 623, 636, 2068, 3268, 3269]\n'\
                            'Enter the Port to Assign to this SNMP Policy.  Valid Range is 1-65535.  [161]: ')
                        if templateVars["port"] == '':
                            templateVars["port"] = 161
                        if re.search(r'[0-9]{1,4}', str(templateVars["port"])):
                            valid = validating.snmp_port('SNMP Port', templateVars["port"], 1, 65535)
                        else:
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            print(f'  Invalid Entry!  Please Enter a valid Port in the range of 1-65535.')
                            print(f'  Excluding [22, 23, 80, 123, 389, 443, 623, 636, 2068, 3268, 3269].')
                            print(f'\n-------------------------------------------------------------------------------------------\n')

                    templateVars["multi_select"] = False
                    jsonVars = jsonData['components']['schemas']['snmp.Policy']['allOf'][1]['properties']

                    # SNMP Contact
                    templateVars["Description"] = jsonVars['SysContact']['description']
                    templateVars["varDefault"] = 'UCS Admins'
                    templateVars["varInput"] = 'SNMP System Contact:'
                    templateVars["varName"] = 'SNMP System Contact'
                    templateVars["varRegex"] = '.*'
                    templateVars["minLength"] = 1
                    templateVars["maxLength"] = jsonVars['SysContact']['maxLength']
                    templateVars["system_contact"] = varStringLoop(**templateVars)

                    # SNMP Location
                    templateVars["Description"] = jsonVars['SysLocation']['description']
                    templateVars["varDefault"] = 'Data Center'
                    templateVars["varInput"] = 'What is the Location of the host on which the SNMP agent (server) runs?'
                    templateVars["varName"] = 'System Location'
                    templateVars["varRegex"] = '.*'
                    templateVars["minLength"] = 1
                    templateVars["maxLength"] = jsonVars['SysLocation']['maxLength']
                    templateVars["system_location"] = varStringLoop(**templateVars)

                    templateVars["access_community_string"] = ''
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
                            templateVars["access_community_string"] = loop_count
                            TF_VAR = 'TF_VAR_access_community_string_%s' % (loop_count)
                            os.environ[TF_VAR] = '%s' % (input_string)
                            valid = True
                        elif question == '' or question == 'N':
                            valid = True
                        else:
                            print(f'\n------------------------------------------------------\n')
                            print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                            print(f'\n------------------------------------------------------\n')

                    if not templateVars["access_community_string"] == '':
                        templateVars["var_description"] = jsonVars['CommunityAccess']['description']
                        templateVars["jsonVars"] = sorted(jsonVars['CommunityAccess']['enum'])
                        templateVars["defaultVar"] = jsonVars['CommunityAccess']['default']
                        templateVars["varType"] = 'Community Access'
                        templateVars["community_access"] = variablesFromAPI(**templateVars)
                    else:
                        templateVars["community_access"] = 'Disabled'

                    templateVars["trap_community_string"] = ''
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
                            templateVars["trap_community_string"] = loop_count
                            TF_VAR = 'TF_VAR_snmp_trap_community_%s' % (loop_count)
                            os.environ[TF_VAR] = '%s' % (input_string)
                            valid = True
                        elif question == '' or question == 'N':
                            valid = True
                        else:
                            print(f'\n------------------------------------------------------\n')
                            print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                            print(f'\n------------------------------------------------------\n')

                    templateVars["engine_input_id"] = ''
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
                            templateVars["snmp_engine_input_id"] = input_string
                            valid = True
                        elif question == '' or question == 'N':
                            valid = True
                        else:
                            print(f'\n------------------------------------------------------\n')
                            print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                            print(f'\n------------------------------------------------------\n')

                    # SNMP Users
                    ilCount = 1
                    snmp_user_list = []
                    snmp_loop = False
                    while snmp_loop == False:
                        question = input(f'Would you like to configure an SNMPv3 User?  Enter "Y" or "N" [Y]: ')
                        if question == '' or question == 'Y':
                            snmp_user_list,snmp_loop = snmp_users(jsonData, ilCount, **templateVars)
                        elif question == 'N':
                            snmp_loop = True
                        else:
                            print(f'\n------------------------------------------------------\n')
                            print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                            print(f'\n------------------------------------------------------\n')
                    templateVars["users"] = snmp_user_list

                    # SNMP Trap Destinations
                    ilCount = 1
                    snmp_dests = []
                    snmp_loop = False
                    while snmp_loop == False:
                        question = input(f'Would you like to configure SNMP Trap Destionations?  Enter "Y" or "N" [Y]: ')
                        if question == '' or question == 'Y':
                            snmp_dests,snmp_loop = snmp_trap_servers(jsonData, ilCount, snmp_user_list, **templateVars)
                        elif question == 'N':
                            snmp_loop = True
                        else:
                            print(f'\n------------------------------------------------------\n')
                            print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                            print(f'\n------------------------------------------------------\n')
                    templateVars["trap_destinations"] = snmp_dests

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    if not templateVars["access_community_string"] == '':
                        print(f'    access_community_string = "Sensitive"')
                    print(f'    description             = "{templateVars["descr"]}"')
                    print(f'    enable_snmp             = {templateVars["enabled"]}')
                    print(f'    name                    = "{templateVars["name"]}"')
                    print(f'    snmp_community_access   = "{templateVars["community_access"]}"')
                    print(f'    snmp_engine_input_id    = "{templateVars["engine_input_id"]}"')
                    print(f'    snmp_port               = {templateVars["port"]}')
                    if len(templateVars["trap_destinations"]) > 0:
                        print(f'    snmp_trap_destinations = ''{')
                        for item in templateVars["trap_destinations"]:
                            for k, v in item.items():
                                if k == 'destination_address':
                                    print(f'      "{v}" = ''{')
                            for k, v in item.items():
                                if k == 'community':
                                    print(f'        community_string    = "Sensitive"')
                                elif k == 'destination_address':
                                    print(f'        destination_address = "{v}"')
                                elif k == 'enabled':
                                    print(f'        enable              = {v}')
                                elif k == 'port':
                                    print(f'        port                = {v}')
                                elif k == 'trap_type':
                                    print(f'        trap_type           = "{v}"')
                                elif k == 'user':
                                    print(f'        user                = "{v}"')
                                elif k == 'version':
                                    print(f'        snmp_server         = "{v}"')
                            print(f'      ''}')
                        print(f'    ''}')
                    if len(templateVars["users"]) > 0:
                        print(f'    snmp_users = ''{')
                        for item in templateVars["users"]:
                            for k, v in item.items():
                                if k == 'name':
                                    print(f'      "{v}" = ''{')
                            for k, v in item.items():
                                if k == 'auth_password':
                                    print(f'        auth_password    = "Sensitive"')
                                elif k == 'auth_type':
                                    print(f'        auth_type        = "{v}"')
                                elif k == 'privacy_password':
                                    print(f'        privacy_password = "Sensitive"')
                                elif k == 'privacy_type':
                                    print(f'        privacy_type     = "{v}"')
                                elif k == 'security_level':
                                    print(f'        security_level   = "{v}"')
                            print(f'      ''}')
                        print(f'    ''}')
                    if not templateVars["trap_community_string"] == '':
                        print(f'    trap_community_string   = "Sensitive"')
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
    # SSH Policy Module
    #==============================================
    def ssh_policies(self, jsonData, easy_jsonData):
        name_prefix = self.name_prefix
        name_suffix = 'ssh'
        org = self.org
        policy_type = 'SSH Policy'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'ssh_policies'

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  An {policy_type} enables an SSH client to make a secure, encrypted connection. You can ')
            print(f'  create one or more SSH policies that contain a specific grouping of SSH properties for a ')
            print(f'  server or a set of servers.\n\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - Intersight/{org}/{self.type}/{templateVars["template_type"]}.auto.tfvars')
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
                    templateVars["enable_ssh"] = True

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  Port used for secure shell access.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid = False
                    while valid == False:
                        templateVars["ssh_port"] = input('What is the SSH Port?  [22]: ')
                        if templateVars["ssh_port"] == '':
                            templateVars["ssh_port"] = 22
                        if re.search(r'[\d]+', str(templateVars["ssh_port"])):
                            valid = validating.number_in_range('SSH Port', templateVars["ssh_port"], 1, 65535)
                        else:
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            print(f'  "{templateVars["ssh_port"]}" is not a valid port.')
                            print(f'\n-------------------------------------------------------------------------------------------\n')

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  Number of seconds to wait before the system considers an SSH request to have timed out.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid = False
                    while valid == False:
                        templateVars["ssh_timeout"] = input('What value do you want to set for the SSH Timeout?  [1800]: ')
                        if templateVars["ssh_timeout"] == '':
                            templateVars["ssh_timeout"] = 1800
                        if re.search(r'[\d]+', str(templateVars["ssh_timeout"])):
                            valid = validating.number_in_range('SSH Timeout', templateVars["ssh_timeout"], 60, 10800)
                        else:
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            print(f'  "{templateVars["ssh_timeout"]}" is not a valid value.  Must be between 60 and 10800')
                            print(f'\n-------------------------------------------------------------------------------------------\n')


                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'    description = "{templateVars["descr"]}"')
                    print(f'    enable_ssh  = {templateVars["enable_ssh"]}')
                    print(f'    name        = "{templateVars["name"]}"')
                    print(f'    ssh_port    = {templateVars["ssh_port"]}')
                    print(f'    ssh_timeout = "{templateVars["ssh_timeout"]}"')
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
    # Storage Policy Module
    #==============================================
    def storage_policies(self, jsonData, easy_jsonData):
        name_prefix = self.name_prefix
        name_suffix = 'storage'
        org = self.org
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

                    templateVars["priority"] = 'auto'
                    templateVars["receive"] = 'Disabled'
                    templateVars["send"] = 'Disabled'

                    # Write Policies to Template File
                    templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
                    write_to_template(self, **templateVars)

                    exit_answer = input(f'Would You like to Configure another {policy_type}?  Enter "Y" or "N" [N]: ')
                    if exit_answer == 'N' or exit_answer == '':
                        policy_loop = True
                        configure_loop = True
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
    # Syslog Policy Module
    #==============================================
    def syslog_policies(self, jsonData, easy_jsonData):
        name_prefix = self.name_prefix
        name_suffix = 'syslog'
        org = self.org
        policy_type = 'Syslog Policy'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'syslog_policies'

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  A {policy_type} will configure domain and servers with remote syslog servers.')
            print(f'  You can configure up to two Remote Syslog Servers.')
            print(f'  This Policy is not required to standup a server but is a good practice for day 2 support.')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - Intersight/{org}/{self.type}/{templateVars["template_type"]}.auto.tfvars')
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

                    # Syslog Local Logging
                    templateVars["multi_select"] = False
                    jsonVars = jsonData['components']['schemas']['syslog.LocalClientBase']['allOf'][1]['properties']
                    templateVars["var_description"] = jsonVars['MinSeverity']['description']
                    templateVars["jsonVars"] = sorted(jsonVars['MinSeverity']['enum'])
                    templateVars["defaultVar"] = jsonVars['MinSeverity']['default']
                    templateVars["varType"] = 'Syslog Local Minimum Severity'
                    templateVars["min_severity"] = variablesFromAPI(**templateVars)

                    templateVars["local_logging"] = {'file':{'min_severity':templateVars["min_severity"]}}

                    remote_logging = syslog_servers(jsonData, **templateVars)
                    templateVars['remote_logging'] = remote_logging

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'    description        = "{templateVars["descr"]}"')
                    print(f'    local_min_severity = "{templateVars["min_severity"]}"')
                    print(f'    name               = "{templateVars["name"]}"')
                    print(f'    remote_clients = [')
                    item_count = 1
                    for key, value in templateVars["remote_logging"].items():
                        print(f'      ''{')
                        for k, v in value.items():
                            if k == 'enable':
                                print(f'        enabled      = {"%s".lower() % (v)}')
                            elif k == 'hostname':
                                print(f'        hostname     = "{v}"')
                            elif k == 'min_severity':
                                print(f'        min_severity = "{v}"')
                            elif k == 'port':
                                print(f'        port         = {v}')
                            elif k == 'protocol':
                                print(f'        protocol     = "{v}"')
                        print(f'      ''}')
                        item_count += 1
                    print(f'    ]')
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
    # Thermal Policy Module
    #==============================================
    def thermal_policies(self, jsonData, easy_jsonData):
        name_prefix = self.name_prefix
        org = self.org
        policy_type = 'Thermal Policy'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'thermal_policies'

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  A {policy_type} will configure the Cooling/FAN Policy for Chassis.  We recommend ')
            print(f'  Balanced for a 5108 and Acoustic for a 9508 Chassis, as of this writing.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - Intersight/{org}/{self.type}/{templateVars["template_type"]}.auto.tfvars')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            policy_loop = False
            while policy_loop == False:

                templateVars["multi_select"] = False
                jsonVars = easy_jsonData['policies']['thermal.Policy']
                templateVars["var_description"] = jsonVars['chassisType']['description']
                templateVars["jsonVars"] = sorted(jsonVars['chassisType']['enum'])
                templateVars["defaultVar"] = jsonVars['chassisType']['default']
                templateVars["varType"] = 'Chassis Type'
                templateVars["chassis_type"] = variablesFromAPI(**templateVars)

                if not name_prefix == '':
                    name = '%s_%s' % (name_prefix, templateVars["chassis_type"])
                else:
                    name = '%s_%s' % (org, templateVars["chassis_type"])

                templateVars["name"] = policy_name(name, policy_type)
                templateVars["descr"] = policy_descr(templateVars["name"], policy_type)

                if templateVars["chassis_type"] == '5108':
                    templateVars["popList"] = ['Acoustic', 'HighPower', 'MaximumPower']
                jsonVars = jsonData['components']['schemas']['thermal.Policy']['allOf'][1]['properties']
                templateVars["var_description"] = jsonVars['FanControlMode']['description']
                templateVars["jsonVars"] = sorted(jsonVars['FanControlMode']['enum'])
                templateVars["defaultVar"] = jsonVars['FanControlMode']['default']
                templateVars["varType"] = 'Fan Control Mode'
                templateVars["fan_control_mode"] = variablesFromAPI(**templateVars)

                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'   description      = "{templateVars["descr"]}"')
                print(f'   name             = "{templateVars["name"]}"')
                print(f'   fan_control_mode = "{templateVars["fan_control_mode"]}"')
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
    # Virtual KVM Policy Module
    #==============================================
    def virtual_kvm_policies(self, jsonData, easy_jsonData):
        name_prefix = self.name_prefix
        name_suffix = 'vkvm'
        org = self.org
        policy_type = 'Virtual KVM Policy'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'virtual_kvm_policies'

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  A {policy_type} will configure the Server for KVM access.  Settings include:')
            print(f'   - Local Server Video - If enabled, displays KVM on any monitor attached to the server.')
            print(f'   - Video Encryption - encrypts all video information sent through KVM.')
            print(f'   - Remote Port - The port used for KVM communication. Range is 1 to 65535.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - Intersight/{org}/{self.type}/{templateVars["template_type"]}.auto.tfvars')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            policy_loop = False
            while policy_loop == False:

                if not name_prefix == '':
                    name = '%s_%s' % (name_prefix, name_suffix)
                else:
                    name = '%s_%s' % (org, name_suffix)

                templateVars["name"] = policy_name(name, policy_type)
                templateVars["descr"] = policy_descr(templateVars["name"], policy_type)
                templateVars["enable_virtual_kvm"] = True
                templateVars["maximum_sessions"] = 4

                valid = False
                while valid == False:
                    local_video = input('Do you want to Display KVM on Monitors attached to the Server?  Enter "Y" or "N" [Y]: ')
                    if local_video == '' or local_video == 'Y':
                        templateVars["enable_local_server_video"] = True
                        valid = True
                    elif local_video == 'N':
                        templateVars["enable_local_server_video"] = False
                        valid = True
                    else:
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                        print(f'\n-------------------------------------------------------------------------------------------\n')

                valid = False
                while valid == False:
                    video_encrypt = input('Do you want to Enable video Encryption?  Enter "Y" or "N" [Y]: ')
                    if video_encrypt == '' or video_encrypt == 'Y':
                        templateVars["enable_video_encryption"] = True
                        valid = True
                    elif video_encrypt == 'N':
                        templateVars["enable_video_encryption"] = False
                        valid = True
                    else:
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                        print(f'\n-------------------------------------------------------------------------------------------\n')

                valid = False
                while valid == False:
                    templateVars["remote_port"] = input('What is the Port you would like to Assign for Remote Access?\n'
                        'This should be a value between 1024-65535. [2068]: ')
                    if templateVars["remote_port"] == '':
                        templateVars["remote_port"] = 2068
                    valid = validating.number_in_range('Remote Port', templateVars["remote_port"], 1, 65535)

                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'   description               = "{templateVars["descr"]}"')
                print(f'   enable_local_server_video = {templateVars["enable_local_server_video"]}')
                print(f'   enable_video_encryption   = {templateVars["enable_video_encryption"]}')
                print(f'   enable_virtual_kvm        = {templateVars["enable_virtual_kvm"]}')
                print(f'   maximum_sessions          = {templateVars["maximum_sessions"]}')
                print(f'   name                      = "{templateVars["name"]}"')
                print(f'   remote_port               = "{templateVars["remote_port"]}"')
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
    # Virtual Media Policy Policy Module
    #==============================================
    def virtual_media_policies(self, jsonData, easy_jsonData):
        name_prefix = self.name_prefix
        name_suffix = 'vmedia'
        org = self.org
        policy_type = 'Virtual Media Policy'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'virtual_media_policies'

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

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
            print(f'  - Intersight/{org}/{self.type}/{templateVars["template_type"]}.auto.tfvars')
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
                    templateVars["enable_virtual_media"] = True

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'    Select this option to enable the appearance of virtual drives on the boot selection menu')
                    print(f'    after mapping the image and rebooting the host. This property is enabled by default.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid = False
                    while valid == False:
                        question = input(f'Do you want to Enable Low Power USB?  Enter "Y" or "N" [Y]: ')
                        if question == 'N':
                            templateVars["enable_low_power_usb"] = False
                            valid = True
                        elif question == '' or question == 'Y':
                            templateVars["enable_low_power_usb"] = True
                            valid = True
                        else:
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                            print(f'\n-------------------------------------------------------------------------------------------\n')

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
                            templateVars["enable_virtual_media_encryption"] = False
                            valid = True
                        elif question == '' or question == 'Y':
                            templateVars["enable_virtual_media_encryption"] = True
                            valid = True
                        else:
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                            print(f'\n-------------------------------------------------------------------------------------------\n')

                    templateVars["virtual_media"] = []
                    inner_loop_count = 1
                    sub_loop = False
                    while sub_loop == False:
                        question = input(f'\nWould you like to add vMedia to this Policy?  Enter "Y" or "N" [Y]: ')
                        if question == '' or question == 'Y':
                            valid_sub = False
                            while valid_sub == False:
                                templateVars["multi_select"] = False
                                jsonVars = jsonData['components']['schemas']['vmedia.Mapping']['allOf'][1]['properties']
                                templateVars["var_description"] = jsonVars['MountProtocol']['description']
                                templateVars["jsonVars"] = sorted(jsonVars['MountProtocol']['enum'])
                                templateVars["defaultVar"] = jsonVars['MountProtocol']['default']
                                templateVars["varType"] = 'vMedia Mount Protocol'
                                Protocol = variablesFromAPI(**templateVars)

                                templateVars["var_description"] = jsonVars['MountProtocol']['description']
                                templateVars["jsonVars"] = sorted(jsonVars['MountProtocol']['enum'])
                                templateVars["defaultVar"] = jsonVars['MountProtocol']['default']
                                templateVars["varType"] = 'vMedia Mount Protocol'
                                deviceType = variablesFromAPI(**templateVars)

                                if Protocol == 'cifs':
                                    templateVars["var_description"] = jsonVars['AuthenticationProtocol']['description']
                                    templateVars["jsonVars"] = sorted(jsonVars['AuthenticationProtocol']['enum'])
                                    templateVars["defaultVar"] = jsonVars['AuthenticationProtocol']['default']
                                    templateVars["varType"] = 'CIFS Authentication Protocol'
                                    authProtocol = variablesFromAPI(**templateVars)

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
                                        templateVars["varName"] = 'File Location'
                                        varValue = Question
                                        if re.search('(http|https)', Protocol):
                                            valid = validating.url(templateVars["varName"], varValue)
                                        else:
                                            varValue = 'http://%s' % (Question)
                                            valid = validating.url(templateVars["varName"], varValue)
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
                                        templateVars["minLength"] = 1
                                        templateVars["maxLength"] = 255
                                        templateVars["varName"] = 'Username'
                                        varValue = Question
                                        valid = validating.string_length(templateVars["varName"], varValue, templateVars["minLength"], templateVars["maxLength"])
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
                                        templateVars["minLength"] = 1
                                        templateVars["maxLength"] = 255
                                        templateVars["rePattern"] = '^[\\S]+$'
                                        templateVars["varName"] = 'Password'
                                        varValue = Password
                                        valid_passphrase = validating.length_and_regex_sensitive(templateVars["rePattern"], templateVars["varName"], varValue, templateVars["minLength"], templateVars["maxLength"])
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
                                    else:
                                        print(f'\n-------------------------------------------------------------------------------------------\n')
                                        print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                                        print(f'\n-------------------------------------------------------------------------------------------\n')

                                if assignOptions == True:
                                    templateVars["multi_select"] = True
                                    jsonVars = easy_jsonData['policies']['vmedia.Mapping']
                                    if Protocol == 'cifs':
                                        templateVars["var_description"] = jsonVars['cifs.mountOptions']['description']
                                        templateVars["jsonVars"] = sorted(jsonVars['cifs.mountOptions']['enum'])
                                        templateVars["defaultVar"] = jsonVars['cifs.mountOptions']['default']
                                    elif Protocol == 'nfs':
                                        templateVars["var_description"] = jsonVars['nfs.mountOptions']['description']
                                        templateVars["jsonVars"] = sorted(jsonVars['nfs.mountOptions']['enum'])
                                        templateVars["defaultVar"] = jsonVars['nfs.mountOptions']['default']
                                    else:
                                        templateVars["multi_select"] = False
                                        templateVars["var_description"] = jsonVars['http.mountOptions']['description']
                                        templateVars["jsonVars"] = sorted(jsonVars['http.mountOptions']['enum'])
                                        templateVars["defaultVar"] = jsonVars['http.mountOptions']['default']
                                    templateVars["varType"] = 'Mount Options'
                                    mount_loop = variablesFromAPI(**templateVars)

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
                                                    templateVars["minNum"] = 1
                                                    templateVars["maxNum"] = 65535
                                                    templateVars["varName"] = 'NFS Port'
                                                    varValue = Question
                                                    valid = validating.number_in_range(templateVars["varName"], varValue, templateVars["minNum"], templateVars["maxNum"])
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
                                                    templateVars["minNum"] = 1
                                                    templateVars["maxNum"] = 65535
                                                    templateVars["varName"] = 'NFS Port'
                                                    varValue = Question
                                                    valid = validating.number_in_range(templateVars["varName"], varValue, templateVars["minNum"], templateVars["maxNum"])
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
                                                    templateVars["minNum"] = 60
                                                    templateVars["maxNum"] = 600
                                                    templateVars["varName"] = 'NFS timeo'
                                                    varValue = Question
                                                    valid = validating.number_in_range(templateVars["varName"], varValue, templateVars["minNum"], templateVars["maxNum"])
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
                                                    templateVars["minNum"] = 1024
                                                    templateVars["maxNum"] = 1048576
                                                    templateVars["varName"] = 'NFS timeo'
                                                    varValue = Question
                                                    validCount = 0
                                                    validNum = validating.number_in_range(templateVars["varName"], varValue, templateVars["minNum"], templateVars["maxNum"])
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
                                        templateVars["virtual_media"].append(vmedia_map)
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

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'    description                     = "{templateVars["descr"]}"')
                    print(f'    enable_low_power_usb            = "{templateVars["enable_low_power_usb"]}"')
                    print(f'    enable_virtual_media            = "{templateVars["enable_virtual_media"]}"')
                    print(f'    enable_virtual_media_encryption = "{templateVars["enable_virtual_media_encryption"]}"')
                    print(f'    name                            = "{templateVars["name"]}"')
                    if len(templateVars["virtual_media"]) > 0:
                        print(f'    virtual_media = ''{')
                        for item in templateVars["virtual_media"]:
                            for k, v in item.items():
                                if k == 'name':
                                    print(f'      "{v}" = ''{')
                            for k, v in item.items():
                                if k == 'authentication_protocol':
                                    print(f'        authentication_protocol = "{v}"')
                                elif k == 'device_type':
                                    print(f'        device_type             = "{v}"')
                                elif k == 'file_location':
                                    print(f'        file_location           = "{v}"')
                                elif k == 'mount_options':
                                    print(f'        mount_options           = "{v}"')
                                elif k == 'password' and v != 0:
                                    print(f'        password                = {v}')
                                elif k == 'protocol':
                                    print(f'        protocol                = "{v}"')
                                elif k == 'username' and v != '':
                                    print(f'        username                = "{v}"')
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
