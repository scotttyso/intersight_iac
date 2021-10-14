#!/usr/bin/env python3

import codecs
import copy
import getpass
import ipaddress
import jinja2
import json
import os, re, sys
import pkg_resources
import subprocess
import validating_ucs
from pathlib import Path

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
    # LAN Connectivity Policy Module
    #========================================
    def lan_connectivity_policies(self, policies, pci_order_consumed):
        name_prefix = self.name_prefix
        name_suffix = 'lan'
        org = self.org
        policy_names = []
        policy_type = 'LAN Connectivity Policy'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'lan_connectivity_policies'

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  A {policy_type} will configure vNIC adapters for Server Profiles.\n')
            print(f'  This wizard will save the configuraton for this section to the following file:')
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

                    templateVars["policy_file"] = 'target_platform.txt'
                    templateVars["var_description"] = '    The platform for which the server profile is applicable. It can either be:\n'
                    templateVars["var_type"] = 'Target Platform'
                    target_platform = variable_loop(**templateVars)
                    templateVars["target_platform"] = target_platform

                    valid = False
                    while valid == False:
                        question = input(f'\nNote: Enabling AzureStack-Host QoS on an adapter allows the user to carve out \n'\
                            'traffic classes for RDMA traffic which ensures that a desired portion of the bandwidth is allocated to it.\n\n'\
                            'Do you want to Enable Azure Stack Host QoS for this LAN Policy?    Enter "Y" or "N" [N]: ')
                        if question == '' or question == 'N':
                            templateVars["enable_azure_stack_host_qos"] = False
                            valid = True
                        elif question == 'Y':
                            templateVars["enable_azure_stack_host_qos"] = True
                            valid = True
                        else:
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                            print(f'\n-------------------------------------------------------------------------------------------\n')

                    valid = False
                    while valid == False:
                        question = input(f'\nDo you want to Enable iSCSI Policies for this LAN Connectivity Policy?  Enter "Y" or "N" [N]: ')
                        if question == '' or question == 'N':
                            iscsi_policies = False
                            valid = True
                        elif question == 'Y':
                            iscsi_policies = True
                            valid = True
                        else:
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                            print(f'\n-------------------------------------------------------------------------------------------\n')

                    if iscsi_policies == True:
                        templateVars["policy_file"] = 'allocation_type.txt'
                        templateVars["var_description"] = '    Allocation Type of iSCSI Qualified Name.  Options are:\n'
                        templateVars["var_type"] = 'IQN Allocation Type'
                        templateVars["iqn_allocation_type"] = variable_loop(**templateVars)
                        if templateVars["iqn_allocation_type"] == 'Pool':
                            templateVars["iqn_static_identifier"] = ''

                            policy_list = ['iqn_pools']
                            templateVars["allow_opt_out"] = False
                            for policy in policy_list:
                                templateVars["policies"] = policies.get(policy)
                                templateVars['inband_ip_pool'] = choose_policy(policy, **templateVars)
                        else:
                            templateVars["iqn_pool"] = ''
                            valid = False
                            while valid == False:
                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                print(f'  User provided static iSCSI Qualified Name (IQN) for use as initiator identifiers by iSCSI')
                                print(f'  vNICs.')
                                print(f'  The iSCSI Qualified Name (IQN) format is: iqn.yyyy-mm.naming-authority:unique name, where:')
                                print(f'    - literal iqn (iSCSI Qualified Name) - always iqn')
                                print(f'    - date (yyyy-mm) that the naming authority took ownership of the domain')
                                print(f'    - reversed domain name of the authority (e.g. org.linux, com.example, com.cisco)')
                                print(f'    - unique name is any name you want to use, for example, the name of your host. The naming')
                                print(f'      authority must make sure that any names assigned following the colon are unique, such as:')
                                print(f'        * iqn.1984-12.com.cisco.iscsi:lnx1')
                                print(f'        * iqn.1984-12.com.cisco.iscsi:win-server1')
                                print(f'  Note: You can also obtain an IQN by going to any Linux system and typing in the command:')
                                print(f'        - iscsi-iname')
                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                question = input(f'\nWould you Like the script to auto generate an IQN For you?  Enter "Y" or "N" [Y]: ')
                                if question == '' or question == 'Y':
                                    p = subprocess.Popen(['iscsi-iname'],
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.STDOUT)
                                    for line in iter(p.stdout.readline, b''):
                                        line = line.decode("utf-8")
                                        line = line.strip()
                                        suffix = line.split(':')[1]
                                        templateVars["iqn_static_identifier"] = 'iqn.1984-12.com.cisco.iscsi:%s' % (suffix)
                                        print(f'IQN is {templateVars["iqn_static_identifier"]}')
                                    valid = True
                                elif question == 'N':
                                    templateVars["iqn_static_identifier"] = input(f'What is the Static IQN you would like to assign to this LAN Policy?  ')
                                    if not templateVars["iqn_static_identifier"] == '':
                                        valid = validating_ucs.iqn_static('IQN Static Identifier', templateVars["iqn_static_identifier"])

                    else:
                        templateVars["iqn_allocation_type"] = 'None'
                        templateVars["iqn_pool"] = ''
                        templateVars["iqn_static_identifier"] = ''

                    templateVars["policy_file"] = 'placement_mode.txt'
                    templateVars["var_description"] = '    Default is custom.  The mode used for placement of vNICs on network adapters. Options are:\n'
                    templateVars["var_type"] = 'vNIC Placement Mode'
                    templateVars["vnic_placement_mode"] = variable_loop(**templateVars)

                    templateVars["policy_file"] = 'cdn_source.txt'
                    templateVars["var_description"] = '    Default is vnic.  Source of the CDN. It can either be user specified or be the same as the vNIC name.\n'
                    templateVars["var_type"] = 'CDN Source'
                    templateVars["vnic_placement_mode"] = variable_loop(**templateVars)

                    print(f'\n-----------------------------------------------------------------------------------------------\n')
                    print(f'  Easy IMM will now begin the vNIC Configuration Process.  We recommend the following guidlines:')
                    print(f'    - For Baremetal Operating Systems like Linux and Windows; use a Failover Policy with a single vnic')
                    print(f'    - For a Virtual Environment it is a Good Practice to not use Failover and use the following')
                    print(f'      vnic layout:')
                    print(f'      1. Management')
                    print(f'      2. Migration/vMotion')
                    print(f'      3. Storage')
                    print(f'      4. Virtual Machines')
                    print(f'  If you select no for Failover Policy the script will create mirroring vnics for A and B')
                    print(f'\n-----------------------------------------------------------------------------------------------\n')
                    templateVars["vnics"] = []
                    inner_loop_count = 1
                    vnic_loop = False
                    while vnic_loop == False:
                        fabrics = ['A','B']
                        valid = False
                        while valid == False:
                            question = input(f'\nDo you want to Enable Failover for this vNIC?    Enter "Y" or "N" [N]: ')
                            if question == '' or question == 'N':
                                templateVars["enable_failover"] = False
                                valid = True
                            elif question == 'Y':
                                templateVars["enable_failover"] = True
                                valid = True
                            else:
                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                                print(f'\n-------------------------------------------------------------------------------------------\n')

                        valid = False
                        while valid == False:
                            if templateVars["enable_failover"] == True:
                                question = input(f'What is the name for this vNIC?  [vnic]: ')
                                if question == '':
                                    question = 'vnic'
                            else:
                                if inner_loop_count == 0:
                                    question = input(f'What is the name for this vNIC?  [Management]: ')
                                    if question == '':
                                        question = 'Management'
                                elif inner_loop_count == 1:
                                    question = input(f'What is the name for this vNIC?  [Migration]: ')
                                    if question == '':
                                        question = 'Migration'
                                elif inner_loop_count == 2:
                                    question = input(f'What is the name for this vNIC?  [Storage]: ')
                                    if question == '':
                                        question = 'Storage'
                                elif inner_loop_count == 3:
                                    question = input(f'What is the name for this vNIC?  [Virtual_Machines]: ')
                                    if question == '':
                                        question = 'Virtual_Machines'
                                else:
                                    question = input(f'What is the name for this vNIC?  [Virtual_Machines]: ')

                            vnic_name = question
                            valid = validating_ucs.vnic_name('vNIC Name', vnic_name)

                        policy_list = [
                            'ethernet_adapter_policies',
                            'ethernet_network_control_policies',
                            'ethernet_network_group_policies',
                            'ethernet_qos_policies',
                            'ethernet_network_policies'
                        ]
                        templateVars["allow_opt_out"] = False
                        for policy in policy_list:
                            policy_short = policy.replace('policies', 'policy')
                            templateVars["policies"] = policies.get(policy)
                            templateVars[policy_short] = choose_policy(policy, **templateVars)

                        if iscsi_policies == True:
                            policy_list = [
                                'iscsi_boot_policy'
                            ]
                            templateVars["allow_opt_out"] = True
                            for policy in policy_list:
                                policy_short = policy.replace('policies', 'policy')
                                templateVars["policies"] = policies.get(policy)
                                templateVars[policy_short] = choose_policy(policy, **templateVars)

                        temp_policy_name = templateVars["name"]
                        templateVars["name"] = 'the vHBAs'
                        policy_list = [
                            'fibre_channel_adapter_policies',
                            'fibre_channel_qos_policies'
                        ]
                        templateVars["allow_opt_out"] = False
                        for policy in policy_list:
                            policy_short = policy.replace('policies', 'policy')
                            templateVars["policies"] = policies.get(policy)
                            templateVars[policy_short] = choose_policy(policy, **templateVars)

                        for x in fabrics:
                            templateVars["name"] = f'the vHBA on Fabric {x}'
                            policy_list = [
                                'fibre_channel_network_policies'
                            ]
                            templateVars["allow_opt_out"] = False
                            for policy in policy_list:
                                policy_short = policy.replace('policies', 'policy')
                                templateVars["policies"] = policies.get(policy)
                                templateVars[f"{policy_short}_{x}"] = choose_policy(policy, **templateVars)

                        templateVars["name"] = temp_policy_name

                        for x in fabrics:
                            valid = False
                            while valid == False:
                                templateVars[f'name_{x}'] = input(f'What is the name for Fabric {x} vHBA?  [HBA-{x}]: ')
                                if templateVars[f'name_{x}'] == '':
                                    templateVars[f'name_{x}'] = 'HBA-%s' % (x)
                                valid = validating_ucs.vname('vNIC Name', templateVars[f'name_{x}'])

                        valid = False
                        while valid == False:
                            question = input(f'\nNote: Persistent LUN Binding Enables retention of LUN ID associations in memory until they are'\
                                ' manually cleared.\n\n'\
                                'Do you want to Enable Persistent LUN Bindings?    Enter "Y" or "N" [N]: ')
                            if question == '' or question == 'N':
                                templateVars["persistent_lun_bindings"] = False
                                valid = True
                            elif question == 'Y':
                                templateVars["persistent_lun_bindings"] = True
                                valid = True
                            else:
                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                                print(f'\n-------------------------------------------------------------------------------------------\n')

                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        print(f'    The PCI Link used as transport for the virtual interface. All VIC adapters have a')
                        print(f'    single PCI link except VIC 1385 which has two.')
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        for x in fabrics:
                            valid = False
                            while valid == False:
                                question = input(f'What is the PCI Link you want to Assign to Fabric {x}?  Range is 0-1.  [0]: ')
                                if question == '' or int(question) == 0:
                                    templateVars[f"pci_link_{x}"] = 0
                                    valid = True
                                elif int(question) == 1:
                                    templateVars[f"pci_link_{x}"] = 1
                                    valid = True
                                else:
                                    print(f'\n-------------------------------------------------------------------------------------------\n')
                                    print(f'  Error!! Invalid Value.  Please enter 0 or 1.')
                                    print(f'\n-------------------------------------------------------------------------------------------\n')

                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        print(f'    PCI Order establishes The order in which the virtual interface is brought up. The order ')
                        print(f'    assigned to an interface should be unique for all the Ethernet and Fibre-Channel ')
                        print(f'    interfaces on each PCI link on a VIC adapter. The maximum value of PCI order is limited ')
                        print(f'    by the number of virtual interfaces (Ethernet and Fibre-Channel) on each PCI link on a ')
                        print(f'    VIC adapter. All VIC adapters have a single PCI link except VIC 1385 which has two.')
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        pci_order_0 = 0
                        pci_order_1 = 0
                        for x in fabrics:
                            for item in pci_order_consumed:
                                for k, v in item.items():
                                    if int(k) == 0:
                                        for i in v:
                                            pci_order_0 = i
                                    else:
                                        for i in v:
                                            pci_order_1 = i
                            valid = False
                            while valid == False:
                                if templateVars[f'pci_link_{x}'] == 0:
                                    pci_order = (int(pci_order_0) + 1)
                                elif templateVars[f'pci_link_{x}'] == 1:
                                    pci_order = (int(pci_order_1) + 1)
                                question = input(f'What is the PCI Order you want to Assign to Fabric {x}?  [{pci_order}]: ')
                                if question == '':
                                    templateVars[f"pci_order_{x}"] = pci_order
                                duplicate = 0
                                for item in pci_order_consumed:
                                    for k, v in item.items():
                                        if templateVars[f'pci_link_{x}'] == 0 and int(k) == 0:
                                            for i in v:
                                                if int(i) == int(pci_order):
                                                    duplicate += 1
                                                    print(f'\n-------------------------------------------------------------------------------------------\n')
                                                    print(f'  Error!! PCI Order "{pci_order}" is already in use.  Please use an alternate.')
                                                    print(f'\n-------------------------------------------------------------------------------------------\n')
                                        elif templateVars[f'pci_link_{x}'] == 1 and int(k) == 1:
                                            for i in v:
                                                if int(i) == int(pci_order):
                                                    duplicate += 1
                                                    print(f'\n-------------------------------------------------------------------------------------------\n')
                                                    print(f'  Error!! PCI Order "{pci_order}" is already in use.  Please use an alternate.')
                                                    print(f'\n-------------------------------------------------------------------------------------------\n')
                                if duplicate == 0:
                                    if templateVars[f'pci_link_{x}'] == 0:
                                        pci_order_consumed[0][0].append(pci_order)
                                    elif templateVars[f'pci_link_{x}'] == 1:
                                        pci_order_consumed[1][1].append(pci_order)
                                    valid = True

                        templateVars["policy_file"] = 'slot_id.txt'
                        templateVars["var_description"] = '  PCIe Slot where the VIC adapter is installed. Supported values are (1-15) and MLOM.\n\n'
                        templateVars["var_type"] = 'Slot ID'
                        templateVars["slot_id"] = variable_loop(**templateVars)

                        templateVars["policy_file"] = 'vhba_type.txt'
                        templateVars["var_description"] = '    vhba_type - VHBA Type for the vHBA Policy.\n'\
                            '    - fc-initiator (Default) - The default value set for vHBA Type Configuration. \n'\
                            '         Fc-initiator specifies vHBA as a consumer of storage. Enables SCSI commands to\n'\
                            '         transfer data and status information between host and target storage systems.\n'\
                            '    - fc-nvme-initiator - Fc-nvme-initiator specifies vHBA as a consumer of storage. \n'\
                            '         Enables NVMe-based message commands to transfer data and status information \n'\
                            '         between host and target storage systems.\n'\
                            '    - fc-nvme-target - Fc-nvme-target specifies vHBA as a provider of storage volumes to\n'\
                            '         initiators.  Enables NVMe-based message commands to transfer data and status \n'\
                            '         information between host and target storage systems.  Currently tech-preview, \n'\
                            '         only enabled with an asynchronous driver.\n'\
                            '    - fc-target - Fc-target specifies vHBA as a provider of storage volumes to initiators. \n'\
                            '         Enables SCSI commands to transfer data and status information between host and \n'\
                            '         target storage systems.  fc-target is enabled only with an asynchronous driver.\n\n'
                        templateVars["var_type"] = 'vHBA Type'
                        templateVars["vhba_type"] = variable_loop(**templateVars)

                        templateVars["policy_file"] = 'allocation_type.txt'
                        templateVars["var_description"] = '    Type of allocation to assign a WWPN address to each vHBA for this SAN policy.\n'
                        templateVars["var_type"] = 'WWPN Allocation Type'
                        templateVars["wwpn_allocation_type"] = variable_loop(**templateVars)

                        templateVars[f'wwpn_pool_A'] = ''
                        templateVars[f'wwpn_pool_B'] = ''
                        templateVars[f'wwpn_static_A'] = ''
                        templateVars[f'wwpn_static_B'] = ''
                        if templateVars["wwpn_allocation_type"] == 'Pool':
                            policy_list = ['wwpn_pools']
                            templateVars["allow_opt_out"] = False
                            for x in fabrics:
                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                print(f'  Select WWPN Pool for Fabric {x}:')
                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                for policy in policy_list:
                                    policy_short = policy.replace('policies', 'policy')
                                    templateVars["policies"] = policies.get(policy)
                                    templateVars[policy_short] = choose_policy(policy, **templateVars)
                                templateVars[f'wwpn_pool_{x}'] = templateVars[policy_short]
                        else:
                            valid = False
                            while valid == False:
                                for x in fabrics:
                                    templateVars["wwpn_static"] = input(f'What is the Static WWPN you would like to assign to Fabric {x}?  ')
                                if not templateVars["wwpn_static"] == '':
                                    templateVars[f"wwpn_static_{x}"]
                                    valid = validating_ucs.wwxn_address(f'Fabric {x} WWPN Static', templateVars["wwpn_static"])

                        vhba_fabric_a = {
                            'fibre_channel_adapter_policy':templateVars["fibre_channel_adapter_policy"],
                            'fibre_channel_network_policy':templateVars["fibre_channel_network_policy_A"],
                            'fibre_channel_qos_policy':templateVars["fibre_channel_qos_policy"],
                            'name':templateVars["name_A"],
                            'persistent_lun_bindings':templateVars["persistent_lun_bindings"],
                            'pci_link':templateVars["pci_link_A"],
                            'pci_order':templateVars["pci_order_A"],
                            'slot_id':templateVars["slot_id"],
                            'switch_id':'A',
                            'vhba_type':templateVars["vhba_type"],
                            'wwpn_allocation_type':templateVars["wwpn_allocation_type"],
                            'wwpn_pool':templateVars["wwpn_pool_A"],
                            'wwpn_static':templateVars["wwpn_static_A"],
                        }
                        vhba_fabric_b = {
                            'fibre_channel_adapter_policy':templateVars["fibre_channel_adapter_policy"],
                            'fibre_channel_network_policy':templateVars["fibre_channel_network_policy_B"],
                            'fibre_channel_qos_policy':templateVars["fibre_channel_qos_policy"],
                            'name':templateVars["name_B"],
                            'persistent_lun_bindings':templateVars["persistent_lun_bindings"],
                            'pci_link':templateVars["pci_link_B"],
                            'pci_order':templateVars["pci_order_B"],
                            'slot_id':templateVars["slot_id"],
                            'switch_id':'B',
                            'vhba_type':templateVars["vhba_type"],
                            'wwpn_allocation_type':templateVars["wwpn_allocation_type"],
                            'wwpn_pool':templateVars["wwpn_pool_B"],
                            'wwpn_static':templateVars["wwpn_static_B"],
                        }
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        print(f'Fabric A:')
                        print(f'   fibre_channel_adapter_policy = "{templateVars["fibre_channel_adapter_policy"]}"')
                        print(f'   fibre_channel_network_policy = "{templateVars["fibre_channel_network_policy_A"]}"')
                        print(f'   fibre_channel_qos_policy     = "{templateVars["fibre_channel_qos_policy"]}"')
                        print(f'   name                         = "{templateVars["name_A"]}"')
                        print(f'   persistent_lun_bindings      = {templateVars["persistent_lun_bindings"]}')
                        print(f'   placement_pci_link           = {templateVars["pci_link_A"]}')
                        print(f'   placement_pci_order          = {templateVars["pci_order_A"]}')
                        print(f'   placement_slot_id            = "{templateVars["slot_id"]}"')
                        print(f'   placement_switch_id          = "A"')
                        print(f'   vhba_type                    = "{templateVars["vhba_type"]}"')
                        print(f'   wwpn_allocation_type         = "{templateVars["wwpn_allocation_type"]}"')
                        if templateVars["wwpn_allocation_type"] == 'Pool':
                            print(f'   wwpn_pool                    = "{templateVars["wwpn_pool_A"]}"')
                        else:
                            print(f'   wwpn_static_address          = "{templateVars["wwpn_static_A"]}"')
                        print(f'Fabric B:')
                        print(f'   fibre_channel_adapter_policy = "{templateVars["fibre_channel_adapter_policy"]}"')
                        print(f'   fibre_channel_network_policy = "{templateVars["fibre_channel_network_policy_B"]}"')
                        print(f'   fibre_channel_qos_policy     = "{templateVars["fibre_channel_qos_policy"]}"')
                        print(f'   name                         = "{templateVars["name_B"]}"')
                        print(f'   persistent_lun_bindings      = {templateVars["persistent_lun_bindings"]}')
                        print(f'   placement_pci_link           = {templateVars["pci_link_B"]}')
                        print(f'   placement_pci_order          = {templateVars["pci_order_B"]}')
                        print(f'   placement_slot_id            = "{templateVars["slot_id"]}"')
                        print(f'   placement_switch_id          = "B"')
                        print(f'   vhba_type                    = "{templateVars["vhba_type"]}"')
                        print(f'   wwpn_allocation_type         = "{templateVars["wwpn_allocation_type"]}"')
                        if templateVars["wwpn_allocation_type"] == 'Pool':
                            print(f'   wwpn_pool                    = "{templateVars["wwpn_pool_B"]}"')
                        else:
                            print(f'   wwpn_static_address          = "{templateVars["wwpn_static_B"]}"')
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        valid_confirm = False
                        while valid_confirm == False:
                            confirm_v = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
                            if confirm_v == 'Y' or confirm_v == '':
                                templateVars["vhbas"].append(vhba_fabric_a)
                                templateVars["vhbas"].append(vhba_fabric_b)
                                valid_exit = False
                                while valid_exit == False:
                                    loop_exit = input(f'Would You like to Configure another set of vHBAs?  Enter "Y" or "N" [N]: ')
                                    if loop_exit == 'Y':
                                        inner_loop_count += 1
                                        valid_confirm = True
                                        valid_exit = True
                                    elif loop_exit == 'N' or loop_exit == '':
                                        vhba_loop = True
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
                    print(f'  Do you want to accept the following configuration?')
                    print(f'    description          = {templateVars["descr"]}')
                    print(f'    name                 = "{templateVars["name"]}"')
                    print(f'    target_platform      = "{target_platform}"')
                    print(f'    vhba_placement_mode  = "{templateVars["vhba_placement_mode"]}"')
                    print(f'    wwnn_allocation_type = "{templateVars["wwnn_allocation_type"]}"')
                    print(f'    wwnn_pool            = "{templateVars["wwnn_pool"]}"')
                    print(f'    wwnn_static          = "{templateVars["wwnn_static"]}"')
                    if len(templateVars["vhbas"]) > 0:
                        print(f'    vhbas = ''[')
                        for item in templateVars["vhbas"]:
                            print(f'      ''{')
                            for k, v in item.items():
                                if k == 'fibre_channel_adapter_policy':
                                    print(f'        fibre_channel_adapter_policy = "{v}"')
                                elif k == 'fibre_channel_network_policy':
                                    print(f'        fibre_channel_network_policy = "{v}"')
                                elif k == 'fibre_channel_qos_policy':
                                    print(f'        fibre_channel_qos_policy     = "{v}"')
                                elif k == 'name':
                                    print(f'        name                         = {v}')
                                elif k == 'persistent_lun_bindings':
                                    print(f'        persistent_lun_bindings      = {v}')
                                elif k == 'pci_link':
                                    print(f'        placement_pci_link           = {v}')
                                elif k == 'pci_link':
                                    print(f'        placement_pci_order          = {v}')
                                elif k == 'placement_slot_id':
                                    print(f'        placement_slot_id            = "{v}"')
                                elif k == 'switch_id':
                                    print(f'        placement_switch_id          = "{v}"')
                                elif k == 'vhba_type':
                                    print(f'        vhba_type                    = "{v}"')
                                elif k == 'wwpn_allocation_type':
                                    print(f'        wwpn_allocation_type         = "{v}"')
                                elif k == 'wwpn_pool':
                                    print(f'        wwpn_pool                    = "{v}"')
                                elif k == 'wwpn_static':
                                    print(f'        wwpn_static                  = "{v}"')
                            print(f'      ''}')
                        print(f'    '']')
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
        valid = validating_ucs.description(f'{policy_type} Description', descr, 1, 62)
        if valid == True:
            return descr

def policy_name(namex, policy_type):
    valid = False
    while valid == False:
        name = input(f'What is the Name for the {policy_type}?  [{namex}]: ')
        if name == '':
            name = '%s' % (namex)
        valid = validating_ucs.name_rule(f'{policy_type} Name', name, 1, 62)
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
