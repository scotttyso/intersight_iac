#!/usr/bin/env python3

import json
import os
import re
import subprocess
import stdiomask
import validating
from class_policies_domain import policies_domain
from class_policies_lan import policies_lan
from class_policies_san import policies_san
from class_policies_sect1 import policies_sect1
from class_policies_sect2 import policies_sect2
from class_pools import pools
from class_profiles import profiles
from textwrap import fill

def choose_policy(policy, **templateVars):

    if 'policies' in policy:
        policy_short = policy.replace('policies', 'policy')
    elif 'pools' in policy:
        policy_short = policy.replace('pools', 'pool')
    elif 'templates' in policy:
        policy_short = policy.replace('templates', 'template')
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

def ntp_alternate():
    valid = False
    while valid == False:
        alternate_true = input('Do you want to Configure an Alternate NTP Server?  Enter "Y" or "N" [Y]: ')
        if alternate_true == 'Y' or alternate_true == '':
            alternate_ntp = input('What is your Alternate NTP Server? [1.north-america.pool.ntp.org]: ')
            if alternate_ntp == '':
                alternate_ntp = '1.north-america.pool.ntp.org'
            if re.search(r'[a-zA-Z]+', alternate_ntp):
                valid = validating.dns_name('Alternate NTP Server', alternate_ntp)
            else:
                valid = validating.ip_address('Alternate NTP Server', alternate_ntp)
        elif alternate_true == 'N':
            alternate_ntp = ''
            valid = True
        else:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
            print(f'\n-------------------------------------------------------------------------------------------\n')
    return alternate_ntp

def ntp_primary():
    valid = False
    while valid == False:
        primary_ntp = input('What is your Primary NTP Server [0.north-america.pool.ntp.org]: ')
        if primary_ntp == "":
            primary_ntp = '0.north-america.pool.ntp.org'
        if re.search(r'[a-zA-Z]+', primary_ntp):
            valid = validating.dns_name('Primary NTP Server', primary_ntp)
        else:
            valid = validating.ip_address('Primary NTP Server', primary_ntp)
    return primary_ntp

def policies_list(policies_list, **templateVars):
    valid = False
    while valid == False:
        print(f'\n-------------------------------------------------------------------------------------------\n')
        if templateVars.get('optional_message'):
            print(templateVars["optional_message"])
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
        policyOption = input(f'Select the Option Number for the {templateVars["policy"]} to Assign to {templateVars["name"]}: ')
        if re.search(r'^[0-9]{1,3}$', policyOption):
            for i, v in enumerate(policies_list):
                i += 1
                if int(policyOption) == i:
                    policy = v
                    valid = True
                    return policy
                elif int(policyOption) == 99:
                    policy = ''
                    valid = True
                    return policy
                elif int(policyOption) == 100:
                    policy = 'create_policy'
                    valid = True
                    return policy

            if int(policyOption) == 99:
                policy = ''
                valid = True
                return policy
            elif int(policyOption) == 100:
                policy = 'create_policy'
                valid = True
                return policy
        else:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  Error!! Invalid Selection.  Please Select a valid Index from the List.')
            print(f'\n-------------------------------------------------------------------------------------------\n')

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
                json_data = {}
                return policies,json_data
            else:
                json_data = json.loads(p.stdout.decode('utf-8'))
                for i in json_data[policy]:
                    for k, v in i.items():
                        policies.append(k)
                return policies,json_data
    else:
        json_data = {}
        return policies,json_data

def policy_descr(name, policy_type):
    valid = False
    while valid == False:
        descr = input(f'What is the Description for the {policy_type}?  [{name} {policy_type}]: ')
        if descr == '':
            descr = '%s %s' % (name, policy_type)
        valid = validating.description(f'{policy_type} templateVars["descr"]', descr, 1, 62)
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
                policy_description = policy_description.replace('Ntp', 'NTP')
                policy_description = policy_description.replace('Snmp', 'SNMP')
                policy_description = policy_description.replace('Wwnn', 'WWNN')
                policy_description = policy_description.replace('Wwpn', 'WWPN')
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
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  Starting module to create {inner_policy}')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            if inner_policy == 'ip_pools':
                pools(name_prefix, templateVars["org"], inner_type).ip_pools(jsonData, easy_jsonData)
            elif inner_policy == 'iqn_pools':
                pools(name_prefix, templateVars["org"], inner_type).iqn_pools(jsonData, easy_jsonData)
            elif inner_policy == 'mac_pools':
                pools(name_prefix, templateVars["org"], inner_type).mac_pools(jsonData, easy_jsonData)
            elif inner_policy == 'uuid_pools':
                pools(name_prefix, templateVars["org"], inner_type).uuid_pools(jsonData, easy_jsonData)
            elif inner_policy == 'wwnn_pools':
                pools(name_prefix, templateVars["org"], inner_type).wwnn_pools(jsonData, easy_jsonData)
            elif inner_policy == 'wwpn_pools':
                pools(name_prefix, templateVars["org"], inner_type).wwpn_pools(jsonData, easy_jsonData)
            elif inner_policy == 'adapter_configuration_policies':
                policies_sect1(name_prefix, templateVars["org"], inner_type).adapter_configuration_policies(jsonData, easy_jsonData)
            elif inner_policy == 'bios_policies':
                policies_sect1(name_prefix, templateVars["org"], inner_type).bios_policies(jsonData, easy_jsonData)
            elif inner_policy == 'boot_order_policies':
                policies_sect1(name_prefix, templateVars["org"], inner_type).boot_order_policies(jsonData, easy_jsonData)
            elif inner_policy == 'certificate_management_policies':
                policies_sect1(name_prefix, templateVars["org"], inner_type).certificate_management_policies(jsonData, easy_jsonData)
            elif inner_policy == 'device_connector_policies':
                policies_sect1(name_prefix, templateVars["org"], inner_type).device_connector_policies(jsonData, easy_jsonData)
            elif inner_policy == 'ethernet_adapter_policies':
                policies_lan(name_prefix, templateVars["org"], inner_type).ethernet_adapter_policies(jsonData, easy_jsonData)
            elif inner_policy == 'ethernet_network_control_policies':
                policies_lan(name_prefix, templateVars["org"], inner_type).ethernet_network_control_policies(jsonData, easy_jsonData)
            elif inner_policy == 'ethernet_network_group_policies':
                policies_lan(name_prefix, templateVars["org"], inner_type).ethernet_network_group_policies(jsonData, easy_jsonData)
            elif inner_policy == 'ethernet_network_policies':
                policies_lan(name_prefix, templateVars["org"], inner_type).ethernet_network_policies(jsonData, easy_jsonData)
            elif inner_policy == 'ethernet_qos_policies':
                policies_lan(name_prefix, templateVars["org"], inner_type).ethernet_qos_policies(jsonData, easy_jsonData)
            elif inner_policy == 'fibre_channel_adapter_policies':
                policies_san(name_prefix, templateVars["org"], inner_type).fibre_channel_adapter_policies(jsonData, easy_jsonData)
            elif inner_policy == 'fibre_channel_network_policies':
                policies_san(name_prefix, templateVars["org"], inner_type).fibre_channel_network_policies(jsonData, easy_jsonData)
            elif inner_policy == 'fibre_channel_qos_policies':
                policies_san(name_prefix, templateVars["org"], inner_type).fibre_channel_qos_policies(jsonData, easy_jsonData)
            elif inner_policy == 'flow_control_policies':
                policies_domain(name_prefix, templateVars["org"], inner_type).flow_control_policies(jsonData, easy_jsonData)
            elif inner_policy == 'imc_access_policies':
                policies_sect1(name_prefix, templateVars["org"], inner_type).imc_access_policies(jsonData, easy_jsonData)
            elif inner_policy == 'ipmi_over_lan_policies':
                policies_sect1(name_prefix, templateVars["org"], inner_type).ipmi_over_lan_policies(jsonData, easy_jsonData)
            elif inner_policy == 'iscsi_adapter_policies':
                policies_lan(name_prefix, templateVars["org"], inner_type).iscsi_adapter_policies(jsonData, easy_jsonData)
            elif inner_policy == 'iscsi_boot_policies':
                policies_lan(name_prefix, templateVars["org"], inner_type).iscsi_boot_policies(jsonData, easy_jsonData)
            elif inner_policy == 'iscsi_static_target_policies':
                policies_lan(name_prefix, templateVars["org"], inner_type).iscsi_static_target_policies(jsonData, easy_jsonData)
            elif inner_policy == 'lan_connectivity_policies':
                policies_lan(name_prefix, templateVars["org"], inner_type).lan_connectivity_policies(jsonData, easy_jsonData)
            elif inner_policy == 'ldap_policies':
                policies_sect1(name_prefix, templateVars["org"], inner_type).ldap_policies(jsonData, easy_jsonData)
            elif inner_policy == 'link_aggregation_policies':
                policies_domain(name_prefix, templateVars["org"], inner_type).link_aggregation_policies(jsonData, easy_jsonData)
            elif inner_policy == 'link_control_policies':
                policies_domain(name_prefix, templateVars["org"], inner_type).link_control_policies(jsonData, easy_jsonData)
            elif inner_policy == 'local_user_policies':
                policies_sect1(name_prefix, templateVars["org"], inner_type).local_user_policies(jsonData, easy_jsonData)
            elif inner_policy == 'multicast_policies':
                policies_domain(name_prefix, templateVars["org"], inner_type).multicast_policies(jsonData, easy_jsonData)
            elif inner_policy == 'network_connectivity_policies':
                policies_sect2(name_prefix, templateVars["org"], inner_type).network_connectivity_policies(jsonData, easy_jsonData)
            elif inner_policy == 'ntp_policies':
                policies_sect2(name_prefix, templateVars["org"], inner_type).ntp_policies(jsonData, easy_jsonData)
            elif inner_policy == 'persistent_memory_policies':
                policies_sect2(name_prefix, templateVars["org"], inner_type).persistent_memory_policies(jsonData, easy_jsonData)
            elif inner_policy == 'port_policies':
                policies_domain(name_prefix, templateVars["org"], inner_type).port_policies(jsonData, easy_jsonData)
            elif inner_policy == 'san_connectivity_policies':
                policies_san(name_prefix, templateVars["org"], inner_type).san_connectivity_policies(jsonData, easy_jsonData)
            elif inner_policy == 'sd_card_policies':
                policies_sect2(name_prefix, templateVars["org"], inner_type).sd_card_policies(jsonData, easy_jsonData)
            elif inner_policy == 'serial_over_lan_policies':
                policies_sect2(name_prefix, templateVars["org"], inner_type).serial_over_lan_policies(jsonData, easy_jsonData)
            elif inner_policy == 'smtp_policies':
                policies_sect2(name_prefix, templateVars["org"], inner_type).smtp_policies(jsonData, easy_jsonData)
            elif inner_policy == 'snmp_policies':
                policies_sect2(name_prefix, templateVars["org"], inner_type).snmp_policies(jsonData, easy_jsonData)
            elif inner_policy == 'ssh_policies':
                policies_sect2(name_prefix, templateVars["org"], inner_type).ssh_policies(jsonData, easy_jsonData)
            elif inner_policy == 'storage_policies':
                policies_sect2(name_prefix, templateVars["org"], inner_type).storage_policies(jsonData, easy_jsonData)
            elif inner_policy == 'switch_control_policies':
                policies_domain(name_prefix, templateVars["org"], inner_type).switch_control_policies(jsonData, easy_jsonData)
            elif inner_policy == 'syslog_policies':
                policies_sect2(name_prefix, templateVars["org"], inner_type).syslog_policies(jsonData, easy_jsonData)
            elif inner_policy == 'system_qos_policies':
                policies_domain(name_prefix, templateVars["org"], inner_type).system_qos_policies(jsonData, easy_jsonData)
            elif inner_policy == 'thermal_policies':
                policies_sect2(name_prefix, templateVars["org"], inner_type).thermal_policies(jsonData, easy_jsonData)
            elif inner_policy == 'ucs_server_profiles':
                profiles(name_prefix, templateVars["org"], inner_type).ucs_server_profiles(jsonData, easy_jsonData)
            elif inner_policy == 'ucs_server_profile_templates':
                profiles(name_prefix, templateVars["org"], inner_type).ucs_server_profile_templates(jsonData, easy_jsonData)
            elif inner_policy == 'virtual_kvm_policies':
                policies_sect2(name_prefix, templateVars["org"], inner_type).virtual_kvm_policies(jsonData, easy_jsonData)
            elif inner_policy == 'virtual_media_policies':
                policies_sect2(name_prefix, templateVars["org"], inner_type).virtual_media_policies(jsonData, easy_jsonData)
            elif inner_policy == 'vlan_policies':
                policies_domain(name_prefix, templateVars["org"], inner_type).vlan_policies(jsonData, easy_jsonData)
            elif inner_policy == 'vsan_policies':
                policies_domain(name_prefix, templateVars["org"], inner_type).vsan_policies(jsonData, easy_jsonData)

def port_modes_fc(jsonData, easy_jsonData, name_prefix, **templateVars):
    port_modes = {}
    ports_in_use = []
    fc_converted_ports = []
    valid = False
    while valid == False:
        fc_mode = input('Do you want to convert ports to Fibre Channel Mode?  Enter "Y" or "N" [Y]: ')
        if fc_mode == '' or fc_mode == 'Y':
            fc_mode = 'Y'
            jsonVars = easy_jsonData['policies']['fabric.PortPolicy']
            templateVars["var_description"] = jsonVars['unifiedPorts']['description']
            templateVars["jsonVars"] = sorted(jsonVars['unifiedPorts']['enum'])
            templateVars["defaultVar"] = jsonVars['unifiedPorts']['default']
            templateVars["varType"] = 'Unified Port Ranges'
            fc_ports = variablesFromAPI(**templateVars)
            x = fc_ports.split('-')
            fc_ports = [int(x[0]),int(x[1])]
            for i in range(int(x[0]), int(x[1]) + 1):
                ports_in_use.append(i)
                fc_converted_ports.append(i)
            port_modes = {'custom_mode':'FibreChannel','port_list':fc_ports,'slot_id':1}
            valid = True
        elif fc_mode == 'N':
            valid = True
        else:
            print(f'\n------------------------------------------------------\n')
            print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
            print(f'\n------------------------------------------------------\n')
    
    return fc_mode,ports_in_use,fc_converted_ports,port_modes

def port_list_eth(jsonData, easy_jsonData, name_prefix, **templateVars):
    port_channels = []
    port_roles = []
    port_count = 1
    ports_in_use = templateVars["ports_in_use"]
    if templateVars["port_type"] == 'Appliance Port-Channel' and templateVars["device_model"] == 'UCS-FI-64108': portx = '99,100'
    elif templateVars["port_type"] == 'Appliance Port-Channel': portx = '51,52'
    elif templateVars["port_type"] == 'Ethernet Uplink Port-Channel' and templateVars["device_model"] == 'UCS-FI-64108': portx = '97,98'
    elif templateVars["port_type"] == 'Ethernet Uplink Port-Channel': portx = '49,50'
    elif templateVars["port_type"] == 'FCoE Uplink Port-Channel' and templateVars["device_model"] == 'UCS-FI-64108': portx = '101,102'
    elif templateVars["port_type"] == 'FCoE Uplink Port-Channel': portx = '53,54'
    elif templateVars["port_type"] == 'Appliance Ports' and templateVars["device_model"] == 'UCS-FI-64108': portx = '99'
    elif templateVars["port_type"] == 'Appliance Ports': portx = '51'
    elif templateVars["port_type"] == 'Ethernet Uplink' and templateVars["device_model"] == 'UCS-FI-64108': portx = '97'
    elif templateVars["port_type"] == 'Ethernet Uplink': portx = '49'
    elif templateVars["port_type"] == 'FCoE Uplink' and templateVars["device_model"] == 'UCS-FI-64108': portx = '101'
    elif templateVars["port_type"] == 'FCoE Uplink': portx = '53'
    elif templateVars["port_type"] == 'Server Ports' and templateVars["device_model"] == 'UCS-FI-64108': portx = '5-36'
    elif templateVars["port_type"] == 'Server Ports': portx = '5-18'
    valid = False
    while valid == False:
        configure_port = input(f'Do you want to configure an {templateVars["port_type"]}?  Enter "Y" or "N" [N]: ')
        if configure_port == 'Y':
            configure_valid = False
            while configure_valid == False:
                print(f'\n------------------------------------------------------\n')
                print(f'  The Port List can be in the format of:')
                print(f'     5 - Single Port')
                print(f'     5-10 - Range of Ports')
                print(f'     5,11,12,13,14,15 - List of Ports')
                print(f'     5-10,20-30 - Ranges and Lists of Ports')
                print(f'\n------------------------------------------------------\n')
                port_list = input(f'Please enter the list of ports you want to add to the {templateVars["port_type"]}?  [{portx}]: ')
                if port_list == '': port_list = portx

                if re.search(r'(^\d+$|^\d+,{1,48}\d+$|^(\d+\-\d+|\d,){1,48}\d+$)', port_list):
                    original_port_list = port_list
                    ports_expanded = vlan_list_full(port_list)
                    port_list = []
                    for x in ports_expanded:
                        port_list.append(int(x))
                    port_overlap_count = 0
                    port_overlap = []
                    for x in ports_in_use:
                        for y in port_list:
                            if int(x) == int(y):
                                port_overlap_count += 1
                                port_overlap.append(x)
                    if port_overlap_count == 0:
                        if templateVars["device_model"] == 'UCS-FI-64108': max_port = 108
                        else: max_port = 54
                        if templateVars["fc_mode"] == 'Y': min_port = int(templateVars["fc_ports"][1])
                        else: min_port = 1
                        for port in port_list:
                            valid_ports = validating.number_in_range('Port Range', port, min_port, max_port)
                            if valid_ports == False:
                                break
                        if valid_ports == True:
                            # Prompt User for the Admin Speed of the Port
                            templateVars["multi_select"] = False
                            jsonVars = jsonData['components']['schemas']['fabric.TransceiverRole']['allOf'][1]['properties']
                            templateVars["var_description"] = jsonVars['AdminSpeed']['description']
                            templateVars["jsonVars"] = jsonVars['AdminSpeed']['enum']
                            templateVars["defaultVar"] = jsonVars['AdminSpeed']['default']
                            templateVars["varType"] = 'Admin Speed'
                            templateVars["admin_speed"] = variablesFromAPI(**templateVars)

                            if re.search('(Appliance Appliance Ports|(Ethernet|FCoE) Uplink)', templateVars["port_type"]):
                                # Prompt User for the FEC Mode of the Port
                                templateVars["var_description"] = jsonVars['Fec']['description']
                                templateVars["jsonVars"] = sorted(jsonVars['Fec']['enum'])
                                templateVars["defaultVar"] = jsonVars['Fec']['default']
                                templateVars["varType"] = 'Fec Mode'
                                templateVars["fec"] = variablesFromAPI(**templateVars)

                            if re.search('(Appliance Port-Channel|Appliance Ports)', templateVars["port_type"]):
                                # Prompt User for the Mode of the Port
                                jsonVars = jsonData['components']['schemas']['fabric.AppliancePcRole']['allOf'][1]['properties']
                                templateVars["var_description"] = jsonVars['Mode']['description']
                                templateVars["jsonVars"] = sorted(jsonVars['Mode']['enum'])
                                templateVars["defaultVar"] = jsonVars['Mode']['default']
                                templateVars["varType"] = 'Mode'
                                templateVars["mode"] = variablesFromAPI(**templateVars)

                                templateVars["var_description"] = jsonVars['Priority']['description']
                                templateVars["jsonVars"] = sorted(jsonVars['Priority']['enum'])
                                templateVars["defaultVar"] = jsonVars['Priority']['default']
                                templateVars["varType"] = 'Priority'
                                templateVars["priority"] = variablesFromAPI(**templateVars)

                            # Prompt User for the
                            if re.search('(Appliance Port-Channel|Appliance Ports)', templateVars["port_type"]):
                                policy_list = [
                                    'policies.ethernet_network_control_policies.ethernet_network_control_policy',
                                    'policies.ethernet_network_group_policies.ethernet_network_group_policy',
                                ]
                            elif re.search('(Ethernet Uplink Port-Channel|Ethernet Uplink)', templateVars["port_type"]):
                                policy_list = [
                                    'policies.ethernet_network_group_policies.ethernet_network_group_policy',
                                    'policies.flow_control_policies.flow_control_policy',
                                    'policies.link_aggregation_policies.link_aggregation_policy',
                                    'policies.link_control_policies.link_control_policy',
                                ]
                            elif re.search('(FCoE Uplink Port-Channel|FCoE Uplink)', templateVars["port_type"]):
                                policy_list = [
                                    'policies.link_aggregation_policies.link_aggregation_policy',
                                    'policies.link_control_policies.link_control_policy',
                                ]
                            templateVars["allow_opt_out"] = False
                            if not templateVars["port_type"] == 'Server Ports':
                                for policy in policy_list:
                                    policy_short = policy.split('.')[2]
                                    templateVars[policy_short],policyData = policy_select_loop(jsonData, easy_jsonData, name_prefix, policy, **templateVars)
                                    templateVars.update(policyData)

                            interfaces = []
                            pc_id = port_list[0]
                            for i in port_list:
                                interfaces.append({'port_id':i,'slot_id':1})

                            if templateVars["port_type"] == 'Appliance Port-Channel':
                                port_channel = {
                                    'admin_speed':templateVars["admin_speed"],
                                    'ethernet_network_control_policy':templateVars["ethernet_network_control_policy"],
                                    'ethernet_network_group_policy':templateVars["ethernet_network_group_policy"],
                                    'interfaces':interfaces,
                                    'mode':templateVars["mode"],
                                    'pc_id':pc_id,
                                    'priority':templateVars["priority"],
                                    'slot_id':1
                                }
                            elif templateVars["port_type"] == 'Ethernet Uplink Port-Channel':
                                port_channel = {
                                    'admin_speed':templateVars["admin_speed"],
                                    'ethernet_network_group_policy':templateVars["ethernet_network_group_policy"],
                                    'flow_control_policy':templateVars["flow_control_policy"],
                                    'interfaces':interfaces,
                                    'link_aggregation_policy':templateVars["link_aggregation_policy"],
                                    'link_control_policy':templateVars["link_control_policy"],
                                    'pc_id':pc_id,
                                    'slot_id':1
                                }
                            elif templateVars["port_type"] == 'FCoE Uplink Port-Channel':
                                port_channel = {
                                    'admin_speed':templateVars["admin_speed"],
                                    'interfaces':interfaces,
                                    'link_aggregation_policy':templateVars["link_aggregation_policy"],
                                    'link_control_policy':templateVars["link_control_policy"],
                                    'pc_id':pc_id,
                                    'slot_id':1
                                }
                            elif templateVars["port_type"] == 'Appliance Ports':
                                port_role = {
                                    'admin_speed':templateVars["admin_speed"],
                                    'ethernet_network_control_policy':templateVars["ethernet_network_control_policy"],
                                    'ethernet_network_group_policy':templateVars["ethernet_network_group_policy"],
                                    'fec':templateVars["fec"],
                                    'mode':templateVars["mode"],
                                    'port_id':original_port_list,
                                    'priority':templateVars["priority"],
                                    'slot_id':1
                                }
                            elif templateVars["port_type"] == 'Ethernet Uplink':
                                port_role = {
                                    'admin_speed':templateVars["admin_speed"],
                                    'ethernet_network_group_policy':templateVars["ethernet_network_group_policy"],
                                    'fec':templateVars["fec"],
                                    'flow_control_policy':templateVars["flow_control_policy"],
                                    'link_control_policy':templateVars["link_control_policy"],
                                    'port_id':original_port_list,
                                    'slot_id':1
                                }
                            elif templateVars["port_type"] == 'FCoE Uplink':
                                port_role = {
                                    'admin_speed':templateVars["admin_speed"],
                                    'fec':templateVars["fec"],
                                    'link_control_policy':templateVars["link_control_policy"],
                                    'port_id':original_port_list,
                                    'slot_id':1
                                }
                            elif templateVars["port_type"] == 'Server Ports':
                                server_ports = {'port_list':original_port_list,'slot_id':1}
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            if not templateVars["port_type"] == 'Server Ports':
                                print(f'    admin_speed                     = "{templateVars["admin_speed"]}"')
                            if re.search('Appliance', templateVars["port_type"]):
                                print(f'    ethernet_network_control_policy = "{templateVars["ethernet_network_control_policy"]}"')
                            if re.search('(Appliance|Ethernet)', templateVars["port_type"]):
                                print(f'    ethernet_network_group_policy   = "{templateVars["ethernet_network_group_policy"]}"')
                            if re.search('Ethernet', templateVars["port_type"]):
                                print(f'    flow_control_policy             = "{templateVars["flow_control_policy"]}"')
                            if re.search('(Ethernet|FCoE) Uplink Port-Channel', templateVars["port_type"]):
                                print(f'    link_aggregation_policy         = "{templateVars["link_aggregation_policy"]}"')
                            if re.search('(Ethernet|FCoE)', templateVars["port_type"]):
                                print(f'    link_control_policy             = "{templateVars["link_control_policy"]}"')
                            if re.search('Port-Channel', templateVars["port_type"]):
                                print(f'    interfaces = [')
                                for item in interfaces:
                                    print('      {')
                                    for k, v in item.items():
                                        print(f'        {k} = {v}')
                                    print('      }')
                                print(f'    ]')
                            if re.search('Appliance', templateVars["port_type"]):
                                print(f'    mode      = "{templateVars["mode"]}"')
                            if re.search('Port-Channel', templateVars["port_type"]):
                                print(f'    pc_id     = {pc_id}')
                            if re.search('Appliance', templateVars["port_type"]):
                                print(f'    priority  = "{templateVars["priority"]}"')
                            if re.search('^(Appliance Ports|(Ethernet|FCoE) Uplink|Server Ports)$', templateVars["port_type"]):
                                print(f'    port_list = {original_port_list}')
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            valid_confirm = False
                            while valid_confirm == False:
                                confirm_port = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                                if confirm_port == 'Y' or confirm_port == '':
                                    if re.search('Port-Channel', templateVars["port_type"]):
                                        port_channels.append(port_channel)
                                    elif re.search('^(Appliance Ports|(Ethernet|FCoE) Uplink)$', templateVars["port_type"]):
                                        port_roles.append(port_role)
                                    elif templateVars["port_type"] == 'Server Ports':
                                        port_roles.append(server_ports)
                                    for i in port_list:
                                        templateVars["ports_in_use"].append(i)

                                    valid_exit = False
                                    while valid_exit == False:
                                        port_exit = input(f'Would You like to Configure another {templateVars["port_type"]}?  Enter "Y" or "N" [N]: ')
                                        if port_exit == 'Y':
                                            port_count += 1
                                            valid_confirm = True
                                            valid_exit = True
                                        elif port_exit == 'N' or port_exit == '':
                                            configure_valid = True
                                            valid = True
                                            valid_confirm = True
                                            valid_exit = True
                                        else:
                                            print(f'\n------------------------------------------------------\n')
                                            print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                                            print(f'\n------------------------------------------------------\n')

                                elif confirm_port == 'N':
                                    print(f'\n-------------------------------------------------------------------------------------------\n')
                                    print(f'  Starting {templateVars["port_type"]} Configuration Over.')
                                    print(f'\n-------------------------------------------------------------------------------------------\n')
                                    valid_confirm = True
                                else:
                                    print(f'\n------------------------------------------------------\n')
                                    print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                                    print(f'\n------------------------------------------------------\n')

                    else:
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        print(f'  Error!! The following Ports are already in use: {port_overlap}.')
                        print(f'\n-------------------------------------------------------------------------------------------\n')

                else:
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  Error!! Invalid Port Range.  A port Range should be in the format 49-50 for example.')
                    print(f'  The following port range is invalid: "{port_list}"')
                    print(f'\n-------------------------------------------------------------------------------------------\n')

        elif configure_port == '' or configure_port == 'N':
            valid = True
        else:
            print(f'\n------------------------------------------------------\n')
            print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
            print(f'\n------------------------------------------------------\n')

    if re.search('Port-Channel', templateVars["port_type"]):
        return port_channels,ports_in_use
    elif re.search('^(Appliance Ports|(Ethernet|FCoE) Uplink|Server Ports)$', templateVars["port_type"]):
        return port_roles,ports_in_use
    
def port_list_fc(jsonData, easy_jsonData, name_prefix, **templateVars):
    fill_pattern_descr = 'For Cisco UCS 6400 Series fabric interconnect, if the FC uplink speed is 8 Gbps, set the '\
        'fill pattern as IDLE on the uplink switch. If the fill pattern is not set as IDLE, FC '\
        'uplinks operating at 8 Gbps might go to an errDisabled state, lose SYNC intermittently, or '\
        'notice errors or bad packets.  For speeds greater than 8 Gbps we recommend Arbff.  Below'\
        'is a configuration example on MDS to match this setting:\n\n'\
        'mds-a(config-if)# switchport fill-pattern IDLE speed 8000\n'\
        'mds-a(config-if)# show port internal inf interface fc1/1 | grep FILL\n'\
        '  FC_PORT_CAP_FILL_PATTERN_8G_CHANGE_CAPABLE (1)\n'\
        'mds-a(config-if)# show run int fc1/16 | incl fill\n\n'\
        'interface fc1/16\n'\
        '  switchport fill-pattern IDLE speed 8000\n\n'\
        'mds-a(config-if)#\n'

    A_port_channels = []
    B_port_channels = []
    A_port_role = []
    B_port_role = []
    fc_ports_in_use = templateVars["fc_ports_in_use"]
    port_count = 1
    templateVars["port_type"] = 'Fibre Channel Port-Channel'
    valid = False
    while valid == False:
        if len(templateVars["fc_converted_ports"]) > 0:
            configure_port = input(f'Do you want to configure a {templateVars["port_type"]}?  Enter "Y" or "N" [Y]: ')
        else:
            configure_port = 'N'
            valid = True
        if configure_port == '' or configure_port == 'Y':
            configure_valid = False
            while configure_valid == False:
                if templateVars["port_type"] == 'Fibre Channel Port-Channel':
                    templateVars["multi_select"] = True
                    templateVars["var_description"] = '    Please Select a Port for the Port-Channel:\n'
                else:
                    templateVars["multi_select"] = False
                    templateVars["var_description"] = '    Please Select a Port for the Uplink:\n'
                templateVars["var_type"] = 'Unified Port'
                port_list = vars_from_list(templateVars["fc_converted_ports"], **templateVars)

                # Prompt User for the Admin Speed of the Port
                templateVars["multi_select"] = False
                jsonVars = jsonData['components']['schemas']['fabric.FcUplinkPcRole']['allOf'][1]['properties']
                templateVars["var_description"] = jsonVars['AdminSpeed']['description']
                templateVars["jsonVars"] = jsonVars['AdminSpeed']['enum']
                templateVars["defaultVar"] = jsonVars['AdminSpeed']['default']
                templateVars["varType"] = 'Admin Speed'
                templateVars["admin_speed"] = variablesFromAPI(**templateVars)

                # Prompt User for the Fill Pattern of the Port
                templateVars["var_description"] = jsonVars['FillPattern']['description']
                templateVars["var_description"] = '%s\n%s' % (templateVars["var_description"], fill_pattern_descr)
                templateVars["jsonVars"] = sorted(jsonVars['FillPattern']['enum'])
                templateVars["defaultVar"] = jsonVars['FillPattern']['default']
                templateVars["varType"] = 'Fill Pattern'
                templateVars["fill_pattern"] = variablesFromAPI(**templateVars)

                vsans = {}
                fabrics = ['Fabric_A', 'Fabric_B']
                for fabric in fabrics:
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  Please Select the VSAN Policy for {fabric}')
                    policy_list = [
                        'policies.vsan_policies.vsan_policy',
                    ]
                    templateVars["allow_opt_out"] = False
                    for policy in policy_list:
                        vsan_policy,policyData = policy_select_loop(jsonData, easy_jsonData, name_prefix, policy, **templateVars)

                    vsan_list = []
                    for item in policyData['vsan_policies']:
                        for key, value in item.items():
                            if key == vsan_policy:
                                for i in value[0]['vsans']:
                                    for k, v in i.items():
                                        for x in v:
                                            for y, val in x.items():
                                                if y == 'vsan_id':
                                                    vsan_list.append(val)

                    if len(vsan_list) > 1:
                        vsan_list = ','.join(str(vsan_list))
                    else:
                        vsan_list = vsan_list[0]
                    vsan_list = vlan_list_full(vsan_list)

                    templateVars["multi_select"] = False
                    if templateVars["port_type"] == 'Fibre Channel Port-Channel':
                        templateVars["var_description"] = '    Please Select a VSAN for the Port-Channel:\n'
                    else:
                        templateVars["var_description"] = '    Please Select a VSAN for the Uplink:\n'
                    templateVars["var_type"] = 'VSAN'
                    vsan_x = vars_from_list(vsan_list, **templateVars)
                    for vs in vsan_x:
                        vsan = vs
                    vsans.update({fabric:vsan})


                if templateVars["port_type"] == 'Fibre Channel Port-Channel':
                    interfaces = []
                    for i in port_list:
                        interfaces.append({'port_id':i,'slot_id':1})

                    pc_id = port_list[0]
                    port_channel_a = {
                        'admin_speed':templateVars["admin_speed"],
                        'fill_pattern':templateVars["fill_pattern"],
                        'interfaces':interfaces,
                        'pc_id':pc_id,
                        'slot_id':1,
                        'vsan_id':vsans.get("Fabric_A")
                    }
                    port_channel_b = {
                        'admin_speed':templateVars["admin_speed"],
                        'fill_pattern':templateVars["fill_pattern"],
                        'interfaces':interfaces,
                        'pc_id':pc_id,
                        'slot_id':1,
                        'vsan_id':vsans.get("Fabric_B")
                    }
                else:
                    port_list = '%s' % (port_list[0])
                    fc_port_role_a = {
                        'admin_speed':templateVars["admin_speed"],
                        'fill_pattern':templateVars["fill_pattern"],
                        'port_id':port_list,
                        'slot_id':1,
                        'vsan_id':vsans["Fabric_A"]
                    }
                    fc_port_role_b = {
                        'admin_speed':templateVars["admin_speed"],
                        'fill_pattern':templateVars["fill_pattern"],
                        'port_id':port_list,
                        'slot_id':1,
                        'vsan_id':vsans["Fabric_B"]
                    }
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'    admin_speed      = "{templateVars["admin_speed"]}"')
                print(f'    fill_pattern     = "{templateVars["fill_pattern"]}"')
                if templateVars["port_type"] == 'Fibre Channel Uplink':
                    print(f'    port_list        = "{port_list}"')
                print(f'    vsan_id_fabric_a = {vsans["Fabric_A"]}')
                print(f'    vsan_id_fabric_b = {vsans["Fabric_B"]}')
                if templateVars["port_type"] == 'Fibre Channel Port-Channel':
                    print(f'    interfaces = [')
                    for item in interfaces:
                        print('      {')
                        for k, v in item.items():
                            print(f'        {k}          = {v}')
                        print('      }')
                    print(f'    ]')
                print(f'\n-------------------------------------------------------------------------------------------\n')
                valid_confirm = False
                while valid_confirm == False:
                    confirm_port = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                    if confirm_port == 'Y' or confirm_port == '':
                        if templateVars["port_type"] == 'Fibre Channel Port-Channel':
                            A_port_channels.append(port_channel_a)
                            B_port_channels.append(port_channel_b)
                        else:
                            A_port_role.append(fc_port_role_a)
                            B_port_role.append(fc_port_role_b)
                        for i in port_list:
                            fc_ports_in_use.append(i)

                        valid_exit = False
                        while valid_exit == False:
                            port_exit = input(f'Would You like to Configure another {templateVars["port_type"]}?  Enter "Y" or "N" [N]: ')
                            if port_exit == 'Y':
                                port_count += 1
                                valid_confirm = True
                                valid_exit = True
                            elif port_exit == 'N' or port_exit == '':
                                configure_valid = True
                                valid = True
                                valid_confirm = True
                                valid_exit = True
                            else:
                                print(f'\n------------------------------------------------------\n')
                                print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                                print(f'\n------------------------------------------------------\n')

                    elif confirm_port == 'N':
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        print(f'  Starting {templateVars["port_type"]} Configuration Over.')
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        valid_confirm = True
                    else:
                        print(f'\n------------------------------------------------------\n')
                        print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                        print(f'\n------------------------------------------------------\n')

        elif configure_port == 'N':
            valid = True
        else:
            print(f'\n------------------------------------------------------\n')
            print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
            print(f'\n------------------------------------------------------\n')

    if templateVars["port_type"] == 'Fibre Channel Port-Channel':
        return A_port_channels,B_port_channels,fc_ports_in_use
    else:
        return A_port_role,B_port_role,fc_ports_in_use

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

def snmp_trap_servers(jsonData, inner_loop_count, snmp_user_list, **templateVars):
    trap_servers = []
    valid_traps = False
    while valid_traps == False:
        templateVars["multi_select"] = False
        jsonVars = jsonData['components']['schemas']['snmp.Trap']['allOf'][1]['properties']
        if len(snmp_user_list) == 0:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  There are no valid SNMP Users so Trap Destinations can only be set to SNMPv2.')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            snmp_version = 'V2'
        else:
            templateVars["var_description"] = jsonVars['Version']['description']
            templateVars["jsonVars"] = sorted(jsonVars['Version']['enum'])
            templateVars["defaultVar"] = jsonVars['Version']['default']
            templateVars["varType"] = 'SNMP Version'
            snmp_version = variablesFromAPI(**templateVars)

        if snmp_version == 'V2':
            valid = False
            while valid == False:
                community_string = stdiomask.getpass(f'What is the Community String for the Destination? ')
                if not community_string == '':
                    valid = validating.snmp_string('SNMP Community String', community_string)
                else:
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  Error!! Invalid Value.  Please Re-enter the SNMP Community String.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
            TF_VAR = 'TF_VAR_snmp_community_string_%s' % (inner_loop_count)
            os.environ[TF_VAR] = '%s' % (community_string)
            community_string = inner_loop_count

        if snmp_version == 'V3':
            templateVars["multi_select"] = False
            templateVars["var_description"] = '    Please Select the SNMP User to assign to this Destination:\n'
            templateVars["var_type"] = 'SNMP User'
            snmp_users = []
            for item in snmp_user_list:
                snmp_users.append(item['name'])
            snmp_user = vars_from_list(snmp_users, **templateVars)
            snmp_user = snmp_user[0]

        if snmp_version == 'V2':
            templateVars["var_description"] = jsonVars['Type']['description']
            templateVars["jsonVars"] = sorted(jsonVars['Type']['enum'])
            templateVars["defaultVar"] = jsonVars['Type']['default']
            templateVars["varType"] = 'SNMP Trap Type'
            trap_type = variablesFromAPI(**templateVars)
        else:
            trap_type = 'Trap'

        valid = False
        while valid == False:
            destination_address = input(f'What is the SNMP Trap Destination Hostname/Address? ')
            if not destination_address == '':
                if re.search(r'^[0-9a-fA-F]+[:]+[0-9a-fA-F]$', destination_address) or \
                    re.search(r'^(\d{1,3}\.){3}\d{1,3}$', destination_address):
                    valid = validating.ip_address('SNMP Trap Destination', destination_address)
                else:
                    valid = validating.dns_name('SNMP Trap Destination', destination_address)
            else:
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'  Error!! Invalid Value.  Please Re-enter the SNMP Trap Destination Hostname/Address.')
                print(f'\n-------------------------------------------------------------------------------------------\n')

        valid = False
        while valid == False:
            port = input(f'Enter the Port to Assign to this Destination.  Valid Range is 1-65535.  [162]: ')
            if port == '':
                port = 162
            if re.search(r'[0-9]{1,4}', str(port)):
                valid = validating.snmp_port('SNMP Port', port, 1, 65535)
            else:
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'  Invalid Entry!  Please Enter a valid Port in the range of 1-65535.')
                print(f'\n-------------------------------------------------------------------------------------------\n')

        if snmp_version == 'V3':
            snmp_destination = {
                'destination_address':destination_address,
                'enabled':True,
                'port':port,
                'trap_type':trap_type,
                'user':snmp_user,
                'version':snmp_version
            }
        else:
            snmp_destination = {
                'community':community_string,
                'destination_address':destination_address,
                'enabled':True,
                'port':port,
                'trap_type':trap_type,
                'version':snmp_version
            }

        print(f'\n-------------------------------------------------------------------------------------------\n')
        if snmp_version == 'V2':
            print(f'   community_string    = "Sensitive"')
        print(f'   destination_address = "{destination_address}"')
        print(f'   enable              = True')
        print(f'   trap_type           = "{trap_type}"')
        print(f'   snmp_version        = "{snmp_version}"')
        if snmp_version == 'V3':
            print(f'   user                = "{snmp_user}"')
        print(f'\n-------------------------------------------------------------------------------------------\n')
        valid_confirm = False
        while valid_confirm == False:
            confirm_v = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
            if confirm_v == 'Y' or confirm_v == '':
                trap_servers.append(snmp_destination)
                valid_exit = False
                while valid_exit == False:
                    loop_exit = input(f'Would You like to Configure another SNMP Trap Destination?  Enter "Y" or "N" [N]: ')
                    if loop_exit == 'Y':
                        inner_loop_count += 1
                        valid_confirm = True
                        valid_exit = True
                    elif loop_exit == 'N' or loop_exit == '':
                        snmp_loop = True
                        valid_confirm = True
                        valid_exit = True
                        valid_traps = True
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

    return trap_servers,snmp_loop

def snmp_users(jsonData, inner_loop_count, **templateVars):
    snmp_user_list = []
    valid_users = False
    while valid_users == False:
        templateVars["multi_select"] = False
        jsonVars = jsonData['components']['schemas']['snmp.User']['allOf'][1]['properties']

        templateVars["Description"] = jsonVars['Name']['description']
        templateVars["varDefault"] = 'admin'
        templateVars["varInput"] = 'What is the SNMPv3 Username:'
        templateVars["varName"] = 'SNMP User'
        templateVars["varRegex"] = '^([a-zA-Z]+[a-zA-Z0-9\\-\\_\\.\\@]+)$'
        templateVars["minLength"] = jsonVars['Name']['minLength']
        templateVars["maxLength"] = jsonVars['Name']['maxLength']
        snmp_user = varStringLoop(**templateVars)

        templateVars["var_description"] = jsonVars['SecurityLevel']['description']
        templateVars["jsonVars"] = sorted(jsonVars['SecurityLevel']['enum'])
        templateVars["defaultVar"] = jsonVars['SecurityLevel']['default']
        templateVars["varType"] = 'SNMP Security Level'
        security_level = variablesFromAPI(**templateVars)

        if security_level == 'AuthNoPriv' or security_level == 'AuthPriv':
            templateVars["var_description"] = jsonVars['AuthType']['description']
            templateVars["jsonVars"] = sorted(jsonVars['AuthType']['enum'])
            templateVars["defaultVar"] = 'SHA'
            templateVars["popList"] = ['NA', 'SHA-224', 'SHA-256', 'SHA-384', 'SHA-512']
            templateVars["varType"] = 'SNMP Auth Type'
            auth_type = variablesFromAPI(**templateVars)

        if security_level == 'AuthNoPriv' or security_level == 'AuthPriv':
            valid = False
            while valid == False:
                auth_password = stdiomask.getpass(f'What is the authorization password for {snmp_user}? ')
                if not auth_password == '':
                    valid = validating.snmp_string('SNMPv3 Authorization Password', auth_password)
                else:
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  Error!! Invalid Value.  Please Re-enter the SNMPv3 Username.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
            TF_VAR = 'TF_VAR_snmp_auth_password_%s' % (inner_loop_count)
            os.environ[TF_VAR] = '%s' % (auth_password)
            auth_password = inner_loop_count

        if security_level == 'AuthPriv':
            templateVars["var_description"] = jsonVars['PrivacyType']['description']
            templateVars["jsonVars"] = sorted(jsonVars['PrivacyType']['enum'])
            templateVars["defaultVar"] = 'AES'
            templateVars["popList"] = ['NA']
            templateVars["varType"] = 'SNMP Auth Type'
            privacy_type = variablesFromAPI(**templateVars)

            valid = False
            while valid == False:
                privacy_password = stdiomask.getpass(f'What is the privacy password for {snmp_user}? ')
                if not privacy_password == '':
                    valid = validating.snmp_string('SNMPv3 Privacy Password', privacy_password)
                else:
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  Error!! Invalid Value.  Please Re-enter the SNMPv3 Username.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
            TF_VAR = 'TF_VAR_snmp_privacy_password_%s' % (inner_loop_count)
            os.environ[TF_VAR] = '%s' % (privacy_password)
            privacy_password = inner_loop_count

        if security_level == 'AuthPriv':
            snmp_user = {
                'auth_password':inner_loop_count,
                'auth_type':auth_type,
                'name':snmp_user,
                'privacy_password':inner_loop_count,
                'privacy_type':privacy_type,
                'security_level':security_level
            }
        elif security_level == 'AuthNoPriv':
            snmp_user = {
                'auth_password':inner_loop_count,
                'auth_type':auth_type,
                'name':snmp_user,
                'security_level':security_level
            }

        print(f'\n-------------------------------------------------------------------------------------------\n')
        print(f'   auth_password    = "Sensitive"')
        print(f'   auth_type        = "{auth_type}"')
        if security_level == 'AuthPriv':
            print(f'   privacy_password = "Sensitive"')
            print(f'   privacy_type     = "{privacy_type}"')
        print(f'   security_level   = "{security_level}"')
        print(f'   snmp_user        = "{snmp_user["name"]}"')
        print(f'\n-------------------------------------------------------------------------------------------\n')
        valid_confirm = False
        while valid_confirm == False:
            confirm_v = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
            if confirm_v == 'Y' or confirm_v == '':
                snmp_user_list.append(snmp_user)
                valid_exit = False
                while valid_exit == False:
                    loop_exit = input(f'Would You like to Configure another SNMP User?  Enter "Y" or "N" [N]: ')
                    if loop_exit == 'Y':
                        inner_loop_count += 1
                        valid_confirm = True
                        valid_exit = True
                    elif loop_exit == 'N' or loop_exit == '':
                        snmp_loop = True
                        valid_confirm = True
                        valid_exit = True
                        valid_users = True
                    else:
                        print(f'\n------------------------------------------------------\n')
                        print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                        print(f'\n------------------------------------------------------\n')

            elif confirm_v == 'N':
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'  Starting SNMP User Configuration Over.')
                print(f'\n-------------------------------------------------------------------------------------------\n')
                valid_confirm = True
            else:
                print(f'\n------------------------------------------------------\n')
                print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                print(f'\n------------------------------------------------------\n')
    return snmp_user_list,snmp_loop

def syslog_servers(jsonData, **templateVars):
    remote_logging = {}
    syslog_count = 1
    syslog_loop = False
    while syslog_loop == False:
        valid = False
        while valid == False:
            hostname = input(f'Enter the Hostname/IP Address of the Remote Server: ')
            if re.search(r'[a-zA-Z]+', hostname):
                valid = validating.dns_name('Remote Logging Server', hostname)
            else:
                valid = validating.ip_address('Remote Logging Server', hostname)

        jsonVars = jsonData['components']['schemas']['syslog.RemoteClientBase']['allOf'][1]['properties']
        templateVars["var_description"] = jsonVars['MinSeverity']['description']
        templateVars["jsonVars"] = sorted(jsonVars['MinSeverity']['enum'])
        templateVars["defaultVar"] = jsonVars['MinSeverity']['default']
        templateVars["varType"] = 'Syslog Remote Minimum Severity'
        min_severity = variablesFromAPI(**templateVars)

        templateVars["var_description"] = jsonVars['Protocol']['description']
        templateVars["jsonVars"] = sorted(jsonVars['Protocol']['enum'])
        templateVars["defaultVar"] = jsonVars['Protocol']['default']
        templateVars["varType"] = 'Syslog Protocol'
        templateVars["protocol"] = variablesFromAPI(**templateVars)

        valid = False
        while valid == False:
            port = input(f'Enter the Port to Assign to this Policy.  Valid Range is 1-65535.  [514]: ')
            if port == '':
                port = 514
            if re.search(r'[0-9]{1,4}', str(port)):
                valid = validating.number_in_range('Port', port, 1, 65535)
            else:
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'  Invalid Entry!  Please Enter a valid Port in the range of 1-65535.')
                print(f'\n-------------------------------------------------------------------------------------------\n')

        remote_host = {
            'enable':True,
            'hostname':hostname,
            'min_severity':min_severity,
            'port':port,
            'protocol':templateVars["protocol"]
        }
        print(f'\n-------------------------------------------------------------------------------------------\n')
        print(f'   hostname     = "{hostname}"')
        print(f'   min_severity = "{min_severity}"')
        print(f'   port         = {port}')
        print(f'   protocol     = "{templateVars["protocol"]}"')
        print(f'\n-------------------------------------------------------------------------------------------\n')
        valid_confirm = False
        while valid_confirm == False:
            confirm_host = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
            if confirm_host == 'Y' or confirm_host == '':
                if syslog_count == 1:
                    remote_logging.update({'server1':remote_host})
                elif syslog_count == 2:
                    remote_logging.update({'server2':remote_host})
                    syslog_loop = True
                    valid_confirm = True
                if syslog_count == 1:
                    valid_exit = False
                    while valid_exit == False:
                        remote_exit = input(f'Would You like to Configure another Remote Host?  Enter "Y" or "N" [Y]: ')
                        if remote_exit == 'Y' or remote_exit == '':
                            syslog_count += 1
                            valid_confirm = True
                            valid_exit = True
                        elif remote_exit == 'N':
                            remote_host = {
                                'enable':False,
                                'hostname':'0.0.0.0',
                                'min_severity':'warning',
                                'port':514,
                                'protocol':'udp'
                            }
                            remote_logging.update({'server2':remote_host})
                            syslog_loop = True
                            valid_confirm = True
                            valid_exit = True
                        else:
                            print(f'\n------------------------------------------------------\n')
                            print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                            print(f'\n------------------------------------------------------\n')

            elif confirm_host == 'N':
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'  Starting Syslog Server Configuration Over.')
                print(f'\n-------------------------------------------------------------------------------------------\n')
                valid_confirm = True
            else:
                print(f'\n------------------------------------------------------\n')
                print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                print(f'\n------------------------------------------------------\n')

    return remote_logging

def ucs_domain_serials():
    print(f'\n-------------------------------------------------------------------------------------------\n')
    print(f'  Note: If you do not have the Serial Number at this time you can manually add it to the:')
    print(f'        - ucs_domain_profiles/ucs_domain_profiles.auto.tfvars file later.')
    print(f'\n-------------------------------------------------------------------------------------------\n')
    valid = False
    while valid == False:
        templateVars = {}
        fabrics = ['A','B']
        for x in fabrics:
            templateVars[f"serial_{x}"] = input(f'What is the Serial Number of Fabric {x}? [press enter to skip]: ')
            if templateVars[f"serial_{x}"] == '':
                valid = True
            elif re.fullmatch(r'^[A-Z]{3}[2-3][\d]([0][1-9]|[1-4][0-9]|[5][1-3])[\dA-Z]{4}$', templateVars[f"serial_{x}"]):
                valid = True
            else:
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'  Error!! Invalid Serial Number.  "templateVars["serial_{x}"]" is not a valid serial.')
                print(f'\n-------------------------------------------------------------------------------------------\n')
    serial_a = templateVars["serial_a"]
    serial_b = templateVars["serial_b"]
    return serial_a,serial_b

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
        newDescr = templateVars["var_description"]
        if '\n' in newDescr:
            newDescr = newDescr.split('\n')
            for line in newDescr:
                if '*' in line:
                    print(fill(f'{line}',width=88, subsequent_indent='    '))
                else:
                    print(fill(f'{line}',88))
        else:
            print(fill(f'{templateVars["var_description"]}',88))
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
    newDescr = templateVars["Description"]
    if '\n' in newDescr:
        newDescr = newDescr.split('\n')
        for line in newDescr:
            if '*' in line:
                print(fill(f'{line}',width=88, subsequent_indent='    '))
            else:
                print(fill(f'{line}',88))
    else:
        print(fill(f'{templateVars["Description"]}',88))
    print(f'\n-------------------------------------------------------------------------------------------\n')
    valid = False
    while valid == False:
        varValue = input(f'{templateVars["varInput"]}  [{templateVars["varDefault"]}]: ')
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
    newDescr = templateVars["Description"]
    if '\n' in newDescr:
        newDescr = newDescr.split('\n')
        for line in newDescr:
            if '*' in line:
                print(fill(f'{line}',width=88, subsequent_indent='    '))
            else:
                print(fill(f'{line}',88))
    else:
        print(fill(f'{templateVars["Description"]}',88))
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
    newDescr = templateVars["Description"]
    if '\n' in newDescr:
        newDescr = newDescr.split('\n')
        for line in newDescr:
            if '*' in line:
                print(fill(f'{line}',width=88, subsequent_indent='    '))
            else:
                print(fill(f'{line}',88))
    else:
        print(fill(f'{templateVars["Description"]}',88))
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
    newDescr = templateVars["Description"]
    if '\n' in newDescr:
        newDescr = newDescr.split('\n')
        for line in newDescr:
            if '*' in line:
                print(fill(f'{line}',width=88, subsequent_indent='    '))
            else:
                print(fill(f'{line}',88))
    else:
        print(fill(f'{templateVars["Description"]}',88))
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
