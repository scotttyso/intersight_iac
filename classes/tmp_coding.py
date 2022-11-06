#!/usr/bin/env python3

import classes.ezfunctions
import jinja2
import json
import os
import pkg_resources
import re
import stdiomask
import subprocess
import validating

ucs_template_path = pkg_resources.resource_filename('temp_coding', '../templates/')

class temp_coding(object):
    def __init__(self, name_prefix, org, type):
        self.templateLoader = jinja2.FileSystemLoader(
            searchpath=(ucs_template_path + '%s/') % (type))
        self.templateEnv = jinja2.Environment(loader=self.templateLoader)
        self.name_prefix = name_prefix
        self.org = org
        self.type = type

    #========================================
    # Storage Policy Module
    #========================================
    def storage_policies(self, jsonData, easy_jsonData):
        name_prefix = self.name_prefix
        name_suffix = 'storage'
        org = self.org
        classes.ezfunctions.policy_names = []
        policy_type = 'Storage Policy'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'storage_policies'

        # Open the Template file
        classes.ezfunctions.write_to_template(self, **templateVars)
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

                    # Obtain Policy Name
                    templateVars["name"] = classes.ezfunctions.policy_name(name, policy_type)
                    # Obtain Policy Description
                    templateVars["descr"] = classes.ezfunctions.policy_descr(templateVars["name"], policy_type)

                    # Configure the Global Host Spares Setting
                    templateVars["multi_select"] = False
                    jsonVars = jsonData['components']['schemas']['storage.StoragePolicy']['allOf'][1]['properties']

                    # Configure the Global Host Spares Setting
                    templateVars["Description"] = jsonVars['GlobalHotSpares']['description']
                    templateVars["varDefault"] = ''
                    templateVars["varInput"] = 'Specify the disks that are to be used as hot spares,\n globally,'\
                        ' for all the Drive Groups. [press enter to skip]:'
                    templateVars["varName"] = 'Global Hot Spares'
                    templateVars["varRegex"] = jsonVars['GlobalHotSpares']['pattern']
                    templateVars["minLength"] = 0
                    templateVars["maxLength"] = 128
                    templateVars["global_hot_spares"] = classes.ezfunctions.varStringLoop(**templateVars)

                    # Obtain Unused Disks State
                    templateVars["var_description"] = jsonVars['UnusedDisksState']['description']
                    templateVars["jsonVars"] = sorted(jsonVars['UnusedDisksState']['enum'])
                    templateVars["defaultVar"] = jsonVars['UnusedDisksState']['default']
                    templateVars["varType"] = 'Unused Disks State'
                    templateVars["unused_disks_state"] = classes.ezfunctions.variablesFromAPI(**templateVars)

                    # Configure the Global Host Spares Setting
                    templateVars["Description"] = jsonVars['UseJbodForVdCreation']['description']
                    templateVars["varInput"] = f'Do you want to Use JBOD drives for Virtual Drive creation?'
                    templateVars["varDefault"] = 'N'
                    templateVars["varName"] = 'Use Jbod For Vd Creation'
                    templateVars["use_jbod_for_vd_creation"] = classes.ezfunctions.varBoolLoop(**templateVars)

                    # Ask if Drive Groups should be configured
                    templateVars["Description"] = 'Drive Group Configuration - Enable to add RAID drive groups that can be used to create'\
                        ' virtual drives.  You can also specify the Global Hot Spares information.'
                    templateVars["varInput"] = f'Do you want to Configure Drive Groups?'
                    templateVars["varDefault"] = 'N'
                    templateVars["varName"] = 'Drive Groups'
                    driveGroups = classes.ezfunctions.varBoolLoop(**templateVars)

                    # If True configure Drive Groups
                    if driveGroups == True:
                        templateVars["drive_groups"] = []
                        inner_loop_count = 1
                        drive_group = []
                        drive_group_loop = False
                        while drive_group_loop == False:
                            jsonVars = jsonData['components']['schemas']['storage.DriveGroup']['allOf'][1]['properties']

                            # Request Drive Group Name
                            templateVars["Description"] = jsonVars['Name']['description']
                            templateVars["varDefault"] = f'dg{inner_loop_count - 1}'
                            templateVars["varInput"] = f'Enter the Drive Group Name.  [{templateVars["varDefault"]}]:'
                            templateVars["varName"] = 'Drive Group Name'
                            templateVars["varRegex"] = jsonVars['Name']['pattern']
                            templateVars["minLength"] = 1
                            templateVars["maxLength"] = 60
                            dgName = classes.ezfunctions.varStringLoop(**templateVars)

                            # Obtain Raid Level for Drive Group
                            templateVars["var_description"] = jsonVars['RaidLevel']['description']
                            templateVars["jsonVars"] = sorted(jsonVars['RaidLevel']['enum'])
                            templateVars["defaultVar"] = jsonVars['RaidLevel']['default']
                            templateVars["varType"] = 'Raid Level'
                            RaidLevel = classes.ezfunctions.variablesFromAPI(**templateVars)

                            jsonVars = jsonData['components']['schemas']['storage.ManualDriveGroup']['allOf'][1]['properties']

                            # If Raid Level is anything other than Raid0 ask for Hot Spares
                            if not RaidLevel == 'Raid0':
                                templateVars["Description"] = jsonVars['DedicatedHotSpares']['description']
                                templateVars["varInput"] = 'Enter the Drives to add as Dedicated Hot Spares [press enter to skip]:'
                                templateVars["varName"] = 'Dedicated Hot Spares'
                                templateVars["varRegex"] = jsonVars['DedicatedHotSpares']['pattern']
                                templateVars["minLength"] = 1
                                templateVars["maxLength"] = 60
                                DedicatedHotSpares = classes.ezfunctions.varStringLoop(**templateVars)
                            else:
                                DedicatedHotSpares = ''

                            # Configure Span Slots
                            SpanSlots = []
                            # If Riad is 10, 50 or 60 allow multiple Span Slots
                            if re.fullmatch('^Raid(10|50|60)$', RaidLevel):
                                templateVars["var_description"] = jsonVars['SpanGroups']['items']['description']
                                templateVars["jsonVars"] = [2, 4, 6, 8]
                                templateVars["defaultVar"] = 2
                                templateVars["varType"] = 'Span Groups'
                                SpanGroups = classes.ezfunctions.variablesFromAPI(**templateVars)
                                if SpanGroups == 2:
                                    SpanGroups = [0, 1]
                                elif SpanGroups == 4:
                                    SpanGroups = [0, 1, 2, 3]
                                elif SpanGroups == 6:
                                    SpanGroups = [0, 1, 2, 3, 4, 5]
                                elif SpanGroups == 8:
                                    SpanGroups = [0, 1, 2, 3, 4, 5, 6, 7]


                                for span in SpanGroups:
                                    jsonVars = jsonData['components']['schemas']['storage.SpanDrives']['allOf'][1]['properties']
                                    templateVars["Description"] = jsonVars['Slots']['description']
                                    if re.fullmatch('^Raid10$', RaidLevel):
                                        Drive1 = (inner_loop_count * 2) - 1
                                        Drive2 = (inner_loop_count * 2)
                                        templateVars["varDefault"] = f'{Drive1}-{Drive2}'
                                    elif re.fullmatch('^Raid50$', RaidLevel):
                                        Drive1 = (inner_loop_count * 3) - 2
                                        Drive2 = (inner_loop_count * 3)
                                        templateVars["varDefault"] = f'{Drive1}-{Drive2}'
                                    elif re.fullmatch('^Raid60$', RaidLevel):
                                        Drive1 = (inner_loop_count * 4) - 3
                                        Drive2 = (inner_loop_count * 4)
                                        templateVars["varDefault"] = f'{Drive1}-{Drive2}'
                                    templateVars["varInput"] = f'Enter the Drive Slots for Drive Array Span {span}. [{templateVars["varDefault"]}]:'
                                    templateVars["varName"] = 'Drive Slots'
                                    templateVars["varRegex"] = jsonVars['Slots']['pattern']
                                    templateVars["minLength"] = 1
                                    templateVars["maxLength"] = 10
                                    SpanSlots.append({'slots':classes.ezfunctions.varStringLoop(**templateVars)})
                            elif re.fullmatch('^Raid(0|1|5|6)$', RaidLevel):
                                jsonVars = jsonData['components']['schemas']['storage.SpanDrives']['allOf'][1]['properties']
                                templateVars["Description"] = jsonVars['Slots']['description']
                                if re.fullmatch('^Raid(0|1)$', RaidLevel):
                                    Drive1 = (inner_loop_count * 2) - 1
                                    Drive2 = (inner_loop_count * 2)
                                    templateVars["varDefault"] = f'{Drive1}-{Drive2}'
                                elif re.fullmatch('^Raid5$', RaidLevel):
                                    Drive1 = (inner_loop_count * 3) - 2
                                    Drive2 = (inner_loop_count * 3)
                                    templateVars["varDefault"] = f'{Drive1}-{Drive2}'
                                elif re.fullmatch('^Raid6$', RaidLevel):
                                    Drive1 = (inner_loop_count * 4) - 3
                                    Drive2 = (inner_loop_count * 4)
                                    templateVars["varDefault"] = f'{Drive1}-{Drive2}'
                                templateVars["varInput"] = f'Enter the Drive Slots for Drive Array Span 0. [{templateVars["varDefault"]}]:'
                                templateVars["varName"] = 'Drive Slots'
                                templateVars["varRegex"] = jsonVars['Slots']['pattern']
                                templateVars["minLength"] = 1
                                templateVars["maxLength"] = 10
                                SpanSlots.append({'slots':classes.ezfunctions.varStringLoop(**templateVars)})
                                
                            virtualDrives = []
                            sub_loop_count = 0
                            sub_loop = False
                            while sub_loop == False:
                                jsonVars = jsonData['components']['schemas']['storage.VirtualDriveConfiguration']['allOf'][1]['properties']

                                templateVars["Description"] = jsonVars['Name']['description']
                                templateVars["varDefault"] = f'vd{sub_loop_count}'
                                templateVars["varInput"] = f'Enter the name of the Virtual Drive.  [vd{sub_loop_count}]'
                                templateVars["varName"] = 'Drive Group Name'
                                templateVars["varRegex"] = jsonVars['Name']['pattern']
                                templateVars["minLength"] = 1
                                templateVars["maxLength"] = 60
                                vd_name = classes.ezfunctions.varStringLoop(**templateVars)

                                templateVars["Description"] = jsonVars['ExpandToAvailable']['description']
                                templateVars["varInput"] = f'Do you want to expand to all the space in the drive group?'
                                templateVars["varDefault"] = 'Y'
                                templateVars["varName"] = 'Expand To Available'
                                ExpandToAvailable = classes.ezfunctions.varBoolLoop(**templateVars)

                                # If Expand to Available is Disabled obtain Virtual Drive disk size
                                if ExpandToAvailable == False:
                                    templateVars["Description"] = jsonVars['Size']['description']
                                    templateVars["varDefault"] =  '1'
                                    templateVars["varInput"] = 'What is the Size for this Virtual Drive?'
                                    templateVars["varName"] = 'Size'
                                    templateVars["varRegex"] = '[0-9]+'
                                    templateVars["minNum"] = jsonVars['Size']['minimum']
                                    templateVars["maxNum"] = 9999999999
                                    vdSize = classes.ezfunctions.varNumberLoop(**templateVars)
                                else:
                                    vdSize = 1
                                
                                templateVars["Description"] = jsonVars['BootDrive']['description']
                                templateVars["varInput"] = f'Do you want to configure {vd_name} as a boot drive?'
                                templateVars["varDefault"] = 'Y'
                                templateVars["varName"] = 'Boot Drive'
                                BootDrive = classes.ezfunctions.varBoolLoop(**templateVars)

                                jsonVars = jsonData['components']['schemas']['storage.VirtualDrivePolicy']['allOf'][1]['properties']

                                templateVars["var_description"] = jsonVars['AccessPolicy']['description']
                                templateVars["jsonVars"] = sorted(jsonVars['AccessPolicy']['enum'])
                                templateVars["defaultVar"] = jsonVars['AccessPolicy']['default']
                                templateVars["varType"] = 'Access Policy'
                                AccessPolicy = classes.ezfunctions.variablesFromAPI(**templateVars)

                                templateVars["var_description"] = jsonVars['DriveCache']['description']
                                templateVars["jsonVars"] = sorted(jsonVars['DriveCache']['enum'])
                                templateVars["defaultVar"] = jsonVars['DriveCache']['default']
                                templateVars["varType"] = 'Drive Cache'
                                DriveCache = classes.ezfunctions.variablesFromAPI(**templateVars)

                                templateVars["var_description"] = jsonVars['ReadPolicy']['description']
                                templateVars["jsonVars"] = sorted(jsonVars['ReadPolicy']['enum'])
                                templateVars["defaultVar"] = jsonVars['ReadPolicy']['default']
                                templateVars["varType"] = 'Read Policy'
                                ReadPolicy = classes.ezfunctions.variablesFromAPI(**templateVars)

                                templateVars["var_description"] = jsonVars['StripSize']['description']
                                templateVars["jsonVars"] = sorted(jsonVars['StripSize']['enum'])
                                templateVars["defaultVar"] = jsonVars['StripSize']['default']
                                templateVars["varType"] = 'Strip Size'
                                StripSize = classes.ezfunctions.variablesFromAPI(**templateVars)

                                templateVars["var_description"] = jsonVars['WritePolicy']['description']
                                templateVars["jsonVars"] = sorted(jsonVars['WritePolicy']['enum'])
                                templateVars["defaultVar"] = jsonVars['WritePolicy']['default']
                                templateVars["varType"] = 'Write Policy'
                                WritePolicy = classes.ezfunctions.variablesFromAPI(**templateVars)

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
                                            else:
                                                print(f'\n------------------------------------------------------\n')
                                                print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                                                print(f'\n------------------------------------------------------\n')

                                    elif confirm_v == 'N':
                                        print(f'\n-------------------------------------------------------------------------------------------\n')
                                        print(f'  Starting Virtual Drive Configuration Over.')
                                        print(f'\n-------------------------------------------------------------------------------------------\n')
                                        valid_confirm = True
                                    else:
                                        print(f'\n------------------------------------------------------\n')
                                        print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                                        print(f'\n------------------------------------------------------\n')


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
                                    print(f'  Starting Drive Group Configuration Over.')
                                    print(f'\n-------------------------------------------------------------------------------------------\n')
                                    valid_confirm = True
                                else:
                                    print(f'\n------------------------------------------------------\n')
                                    print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                                    print(f'\n------------------------------------------------------\n')
                    else:
                        templateVars["drive_group"] = []

                    # Ask if M2 should be configured
                    templateVars["Description"] = jsonVars['M2VirtualDrive']['description']
                    templateVars["varInput"] = f'Do you want to Enable the M.2 Virtual Drive Configuration?'
                    templateVars["varDefault"] = 'Y'
                    templateVars["varName"] = 'M.2 Virtual Drive'
                    M2VirtualDrive = classes.ezfunctions.varBoolLoop(**templateVars)

                    # Configure M2 if it is True if not Pop it from the list
                    if M2VirtualDrive == True:
                        jsonVars = jsonData['components']['schemas']['storage.M2VirtualDriveConfig']['allOf'][1]['properties']

                        templateVars["var_description"] = jsonVars['ControllerSlot']['description']
                        templateVars["jsonVars"] = sorted(jsonVars['ControllerSlot']['enum'])
                        templateVars["defaultVar"] = 'MSTOR-RAID-1,MSTOR-RAID-2'
                        templateVars["varType"] = 'Controller Slot'
                        ControllerSlot = classes.ezfunctions.variablesFromAPI(**templateVars)

                        templateVars["m2_configuration"] = {
                            'controller_slot':ControllerSlot,
                            'enable':True
                        }
                    else:
                        templateVars.pop('m2_configuration')

                    # Ask if Drive Groups should be configured
                    templateVars["Description"] = 'Enable to create RAID0 virtual drives on each physical drive..'
                    templateVars["varInput"] = f"Do you want to Configure Single Drive RAID's?"
                    templateVars["varDefault"] = 'N'
                    templateVars["varName"] = 'Single Drive RAID'
                    singledriveRaid = classes.ezfunctions.varBoolLoop(**templateVars)

                    # If True configure Drive Groups
                    if singledriveRaid == True:
                        single_drive_loop = False
                        while single_drive_loop == False:
                            # Obtain the Single Drive Raid Slots
                            jsonVars = jsonData['components']['schemas']['storage.R0Drive']['allOf'][1]['properties']
                            templateVars["Description"] = jsonVars['DriveSlots']['description']
                            templateVars["varDefault"] = f'{Drive1}-{Drive2}'
                            templateVars["varInput"] = f'Enter the Drive Slots for Drive Array Span 0. [{templateVars["varDefault"]}]:'
                            templateVars["varName"] = 'Drive Slots'
                            templateVars["varRegex"] = jsonVars['DriveSlots']['pattern']
                            templateVars["minLength"] = 1
                            templateVars["maxLength"] = 64
                            DriveSlots = classes.ezfunctions.varStringLoop(**templateVars)
                                
                            # Obtain the Virtual Drive Policies
                            jsonVars = jsonData['components']['schemas']['storage.VirtualDrivePolicy']['allOf'][1]['properties']

                            # Access Policy
                            templateVars["var_description"] = jsonVars['AccessPolicy']['description']
                            templateVars["jsonVars"] = sorted(jsonVars['AccessPolicy']['enum'])
                            templateVars["defaultVar"] = jsonVars['AccessPolicy']['default']
                            templateVars["varType"] = 'Access Policy'
                            AccessPolicy = classes.ezfunctions.variablesFromAPI(**templateVars)

                            # Drive Cache
                            templateVars["var_description"] = jsonVars['DriveCache']['description']
                            templateVars["jsonVars"] = sorted(jsonVars['DriveCache']['enum'])
                            templateVars["defaultVar"] = jsonVars['DriveCache']['default']
                            templateVars["varType"] = 'Drive Cache'
                            DriveCache = classes.ezfunctions.variablesFromAPI(**templateVars)

                            # Read Policy
                            templateVars["var_description"] = jsonVars['ReadPolicy']['description']
                            templateVars["jsonVars"] = sorted(jsonVars['ReadPolicy']['enum'])
                            templateVars["defaultVar"] = jsonVars['ReadPolicy']['default']
                            templateVars["varType"] = 'Read Policy'
                            ReadPolicy = classes.ezfunctions.variablesFromAPI(**templateVars)

                            # Strip Size
                            templateVars["var_description"] = jsonVars['StripSize']['description']
                            templateVars["jsonVars"] = sorted(jsonVars['StripSize']['enum'])
                            templateVars["defaultVar"] = jsonVars['StripSize']['default']
                            templateVars["varType"] = 'Strip Size'
                            StripSize = classes.ezfunctions.variablesFromAPI(**templateVars)

                            # Write Policy
                            templateVars["var_description"] = jsonVars['WritePolicy']['description']
                            templateVars["jsonVars"] = sorted(jsonVars['WritePolicy']['enum'])
                            templateVars["defaultVar"] = jsonVars['WritePolicy']['default']
                            templateVars["varType"] = 'Write Policy'
                            WritePolicy = classes.ezfunctions.variablesFromAPI(**templateVars)

                            templateVars["single_drive_raid_configuration"] = {
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
                            print(f'      access_policy = "{templateVars["single_drive_raid_configuration"]["access_policy"]}"')
                            print(f'      disk_cache    = "{templateVars["single_drive_raid_configuration"]["disk_cache"]}"')
                            print(f'      drive_slots   = "{templateVars["single_drive_raid_configuration"]["expand_to_available"]}"')
                            print(f'      enable        = {templateVars["single_drive_raid_configuration"]["enable"]}')
                            print(f'      read_policy   = "{templateVars["single_drive_raid_configuration"]["read_policy"]}"')
                            print(f'      strip_size    = "{templateVars["single_drive_raid_configuration"]["strip_size"]}"')
                            print(f'      write_policy  = "{templateVars["single_drive_raid_configuration"]["write_policy"]}"')
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
                                    print(f'\n-------------------------------------------------------------------------------------------\n')
                                    print(f'  Starting Single Drive RAID Configuration Over.')
                                    print(f'\n-------------------------------------------------------------------------------------------\n')
                                    valid_confirm = True
                                else:
                                    print(f'\n------------------------------------------------------\n')
                                    print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                                    print(f'\n------------------------------------------------------\n')

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'    description              = "{templateVars["descr"]}"')
                    print(f'    global_hot_spares        = "{templateVars["global_hot_spares"]}"')
                    print(f'    unused_disks_state       = "{templateVars["unused_disks_state"]}"')
                    print(f'    use_jbod_for_vd_creation = "{templateVars["use_jbod_for_vd_creation"]}"')
                    dg_count = 0
                    if len(templateVars["drive_groups"]) > 0:
                        print(f'    drive_groups = ''{')
                        for drive_group in templateVars["drive_groups"]:
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
                            dg_count += 1
                        print(f'    ''}')
                    else:
                        print(f'    drive_groups = ''{}')
                    if templateVars.get("m2_configuration"):
                        print(f'    m2_configuration = ''{')
                        print(f'      "0" = ''{')
                        print(f'        controller_slot = "{templateVars["m2_configuration"]["controller_slot"]}"')
                        print(f'      ''}')
                        print(f'    ''}')
                    else:
                        print(f'    m2_configuration = ''{}')
                    if templateVars.get("single_drive_raid_configuration"):
                        print(f'    single_drive_raid_configuration = ''{')
                        print(f'    "0" = ''{')
                        print(f'      access_policy = "{templateVars["single_drive_raid_configuration"]["access_policy"]}"')
                        print(f'      disk_cache    = "{templateVars["single_drive_raid_configuration"]["disk_cache"]}"')
                        print(f'      drive_slots   = "{templateVars["single_drive_raid_configuration"]["drive_slots"]}"')
                        print(f'      enable        = {templateVars["single_drive_raid_configuration"]["enable"]}')
                        print(f'      read_policy   = "{templateVars["single_drive_raid_configuration"]["read_policy"]}"')
                        print(f'      strip_size    = "{templateVars["single_drive_raid_configuration"]["strip_size"]}"')
                        print(f'      write_policy  = "{templateVars["single_drive_raid_configuration"]["write_policy"]}"')
                        print(f'    ''}')
                    else:
                        print(f'    single_drive_raid_configuration = ''{}')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
                        if confirm_policy == 'Y' or confirm_policy == '':
                            confirm_policy = 'Y'

                            # Write Policies to Template File
                            templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
                            classes.ezfunctions.write_to_template(self, **templateVars)

                            # Add Template Name to Policies Output
                            classes.ezfunctions.policy_names.append(templateVars["name"])

                            configure_loop, policy_loop = classes.ezfunctions.exit_default_no(templateVars["policy_type"])
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
        classes.ezfunctions.write_to_template(self, **templateVars)
