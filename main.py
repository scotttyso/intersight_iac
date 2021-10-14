#!/usr/bin/env python3
import json
import lib_ucs
import sys
import validating_ucs
from pathlib import Path

home = Path.home()

def process_config_conversion(json_data):
    print(f'\n---------------------------------------------------------------------------------------\n')
    print(f'  Starting the Easy IMM Configuration Conversion Wizard!')
    print(f'\n---------------------------------------------------------------------------------------\n')

    type = 'pools'
    lib_ucs.config_conversion(json_data, type).ip_pools()
    lib_ucs.config_conversion(json_data, type).iqn_pools()
    lib_ucs.config_conversion(json_data, type).mac_pools()
    lib_ucs.config_conversion(json_data, type).uuid_pools()
    lib_ucs.config_conversion(json_data, type).wwnn_pools()
    lib_ucs.config_conversion(json_data, type).wwpn_pools()
    type = 'policies'
    lib_ucs.config_conversion(json_data, type).bios_policies()
    lib_ucs.config_conversion(json_data, type).boot_order_policies()
    lib_ucs.config_conversion(json_data, type).ethernet_adapter_policies()
    lib_ucs.config_conversion(json_data, type).ethernet_network_control_policies()
    lib_ucs.config_conversion(json_data, type).ethernet_network_group_policies()
    lib_ucs.config_conversion(json_data, type).ethernet_network_policies()
    lib_ucs.config_conversion(json_data, type).ethernet_qos_policies()
    lib_ucs.config_conversion(json_data, type).fibre_channel_adapter_policies()
    lib_ucs.config_conversion(json_data, type).fibre_channel_network_policies()
    lib_ucs.config_conversion(json_data, type).fibre_channel_qos_policies()
    lib_ucs.config_conversion(json_data, type).flow_control_policies()
    lib_ucs.config_conversion(json_data, type).imc_access_policies()
    lib_ucs.config_conversion(json_data, type).ipmi_over_lan_policies()
    lib_ucs.config_conversion(json_data, type).iscsi_adapter_policies()
    lib_ucs.config_conversion(json_data, type).iscsi_boot_policies()
    lib_ucs.config_conversion(json_data, type).iscsi_static_target_policies()
    lib_ucs.config_conversion(json_data, type).lan_connectivity_policies()
    lib_ucs.config_conversion(json_data, type).link_aggregation_policies()
    lib_ucs.config_conversion(json_data, type).link_control_policies()
    lib_ucs.config_conversion(json_data, type).network_connectivity_policies()
    lib_ucs.config_conversion(json_data, type).ntp_policies()
    lib_ucs.config_conversion(json_data, type).port_policies()
    lib_ucs.config_conversion(json_data, type).power_policies()
    lib_ucs.config_conversion(json_data, type).san_connectivity_policies()
    lib_ucs.config_conversion(json_data, type).sd_card_policies()
    lib_ucs.config_conversion(json_data, type).serial_over_lan_policies()
    lib_ucs.config_conversion(json_data, type).snmp_policies()
    lib_ucs.config_conversion(json_data, type).storage_policies()
    lib_ucs.config_conversion(json_data, type).switch_control_policies()
    lib_ucs.config_conversion(json_data, type).syslog_policies()
    lib_ucs.config_conversion(json_data, type).system_qos_policies()
    lib_ucs.config_conversion(json_data, type).thermal_policies()
    lib_ucs.config_conversion(json_data, type).virtual_kvm_policies()
    lib_ucs.config_conversion(json_data, type).virtual_media_policies()
    lib_ucs.config_conversion(json_data, type).vsan_policies()
    type = 'policies_vlans'
    lib_ucs.config_conversion(json_data, type).multicast_policies()
    lib_ucs.config_conversion(json_data, type).vlan_policies()
    type = 'ucs_domain_profiles'
    lib_ucs.config_conversion(json_data, type).ucs_domain_profiles()
    type = 'ucs_server_profiles'
    lib_ucs.config_conversion(json_data, type).ucs_server_profile_templates()
    lib_ucs.config_conversion(json_data, type).ucs_server_profiles()

    print(f'\n---------------------------------------------------------------------------------------\n')
    print(f'  Proceedures Complete!!! Closing Environment and Exiting Script.')
    print(f'\n---------------------------------------------------------------------------------------\n')
    exit()

def process_wizard():
    print(f'\n-------------------------------------------------------------------------------------------\n')
    print(f'  Starting the Easy IMM Initial Configuration Wizard!')
    print(f'\n-------------------------------------------------------------------------------------------\n')

    templateVars = {}
    templateVars["multi_select"] = False
    templateVars["policy_file"] = 'wizard_menu.txt'
    templateVars["var_description"] = '    Select the Deployment type you would like to do with the wizard:\n\n'
    templateVars["var_type"] = 'Menu Option'
    main_menu = lib_ucs.variable_loop(**templateVars)
    main_menu = main_menu.replace(' ', '_')
    main_menu = main_menu.lower()

    if main_menu == 'deploy_domain_wizard':
        policy_list = [
            # Pools
            'ip_pools',
            'mac_pools',
            'uuid_pools',
            'wwnn_pools',
            'wwpn_pools',
            # UCS Domain Policies and Profiles
            'multicast_policies',
            'vlan_policies',
            'vsan_policies',
            'flow_control_policies',
            'link_aggregation_policies',
            'link_control_policies',
            'port_policies',
            'ntp_policies',
            'syslog_policies',
            'network_connectivity_policies',
            'snmp_policies',
            'system_qos_policies',
            'switch_control_policies',
            'ucs_domain_profiles',
            # UCS Chassis Policies and Profiles
            'imc_access_policies',
            'power_policies',
            'thermal_policies',
            'ucs_chassis_profiles',
            # UCS Server Policies and Profiles
            'bios_policies',
            'boot_order_policies',
            'virtual_media_policies',
            'certificate_management_policies',
            'ipmi_over_lan_policies',
            'local_user_policies',
            'serial_over_lan_policies',
            'virtual_kvm_policies',
            'sd_card_policies',
            'storage_policies',
            'ethernet_adapter_policies',
            'ethernet_network_control_policies',
            'ethernet_network_group_policies',
            'ethernet_qos_policies',
            'iscsi_adapter_policies',
            'iscsi_boot_policies',
            'iscsi_static_target_policies',
            'lan_connectivity_policies',
            'fibre_channel_adapter_policies',
            'fibre_channel_network_policies',
            'fibre_channel_qos_policies',
            'san_connectivity_policies',
            'ucs_server_template_profiles',
            'ucs_server_profiles',
        ]
    elif main_menu == 'deploy_domain_chassis_wizard':
        policy_list = [
            # UCS Chassis Policies and Profiles
            'power_policies',
            'thermal_policies',
            'ucs_chassis_profiles'
        ]
    elif main_menu == 'deploy_domain_fabric_interconnect_wizard':
        policy_list = [
            # UCS Domain Policies and Profiles
            'multicast_policies',
            'vlan_policies',
            'vsan_policies',
            'flow_control_policies',
            'link_aggregation_policies',
            'link_control_policies',
            'port_policies',
            'ntp_policies',
            'network_connectivity_policies',
            'system_qos_policies',
            'switch_control_policies',
            'ucs_domain_profiles',
        ]
    elif main_menu == 'deploy_domain_servers_wizard':
        policy_list = [
            # Pools
            'ip_pools',
            'mac_pools',
            'uuid_pools',
            'wwnn_pools',
            'wwpn_pools',
            # UCS Server Policies and Profiles
            'bios_policies',
            'boot_order_policies',
            'virtual_media_policies',
            'certificate_management_policies',
            'ipmi_over_lan_policies',
            'local_user_policies',
            'serial_over_lan_policies',
            'virtual_kvm_policies',
            'sd_card_policies',
            'storage_policies',
            'ethernet_adapter_policies',
            'ethernet_network_control_policies',
            'ethernet_network_group_policies',
            'ethernet_qos_policies',
            'iscsi_adapter_policies',
            'iscsi_boot_policies',
            'iscsi_static_target_policies',
            'lan_connectivity_policies',
            'fibre_channel_adapter_policies',
            'fibre_channel_network_policies',
            'fibre_channel_qos_policies',
            'san_connectivity_policies',
            'ucs_server_template_profiles',
            'ucs_server_profiles',
        ]
    elif main_menu == 'deploy_standalone_servers_wizard':
        policy_list = [
            # Pools
            'ip_pools',
            'mac_pools',
            'uuid_pools',
            'wwnn_pools',
            'wwpn_pools',
            # UCS Server Policies and Profiles
            'bios_policies',
            'boot_order_policies',
            'persistent_memory_policies',
            'virtual_media_policies',
            'device_connector_policies',
            'ipmi_over_lan_policies',
            'ldap_policies',
            'serial_over_lan_policies',
            'smtp_policies',
            'snmp_policies',
            'ssh_policies',
            'syslog_policies',
            'virtual_kvm_policies',
            'sd_card_policies',
            'storage_policies',
            'adapter_configuration_policies',
            'ethernet_adapter_policies',
            'ethernet_network_control_policies',
            'ethernet_network_group_policies',
            'ethernet_network_policies',
            'ethernet_qos_policies',
            'iscsi_adapter_policies',
            'iscsi_boot_policies',
            'iscsi_static_target_policies',
            'lan_connectivity_policies',
            'fibre_channel_adapter_policies',
            'fibre_channel_network_policies',
            'fibre_channel_qos_policies',
            'san_connectivity_policies',
            'ucs_server_template_profiles',
            'ucs_server_profiles',
        ]

    policy_list = []
    if main_menu == 'deploy_individual_policies':
        templateVars["policy_file"] = 'select_type_menu.txt'
        templateVars["var_description"] = '    Select the Module Type:\n\n'
        templateVars["var_type"] = 'Configuration Type'
        type_menu = lib_ucs.variable_loop(**templateVars)
        if type_menu == 'Policies':
            templateVars["multi_select"] = True
            templateVars["policy_file"] = 'policies.txt'
            templateVars["var_description"] = '    Select the Policies to Create:\n'\
                '    - Single policy: 1 or 5\n'\
                '    - List of Policies: 1,2,3\n'\
                '    - Range of Policies: 1-3,5-6\n'
            templateVars["var_type"] = 'Configuration Type'
            policies_list = lib_ucs.variable_loop(**templateVars)
            for line in policies_list:
                line = line.replace(' ', '_')
                line = line.replace('-', '_')
                line = line.lower()
                policy_list.append(line)
        elif type_menu == 'Pools':
            templateVars["multi_select"] = True
            templateVars["policy_file"] = 'pools.txt'
            templateVars["var_description"] = '    Select the Pools to Create:\n'\
                '    - Single Pool: 1 or 5\n'\
                '    - List of Pools: 1,2,3\n'\
                '    - Range of Pools: 1-3,5-6\n'
            templateVars["var_type"] = 'Configuration Type'
            policies_list = lib_ucs.variable_loop(**templateVars)
            for line in policies_list:
                line = line.replace(' ', '_')
                line = line.replace('-', '_')
                line = line.lower()
                policy_list.append(line)
        elif type_menu == 'Profiles':
            templateVars["multi_select"] = True
            templateVars["policy_file"] = 'profiles.txt'
            templateVars["var_description"] = '    Select the Profiles to Create:\n'\
                '    - Single Profile: 1 or 5\n'\
                '    - List of Profiles: 1,2,3\n'\
                '    - Range of Profiles: 1-3,5-6\n'
            templateVars["var_type"] = 'Configuration Type'
            policies_list = lib_ucs.variable_loop(**templateVars)
            for line in policies_list:
                line = line.replace(' ', '_')
                line = line.replace('-', '_')
                line = line.lower()
                policy_list.append(line)

    valid = False
    while valid == False:
        org = input('What is your Intersight Organization Name?  [default]: ')
        if org == '':
            org = 'default'
        valid = validating_ucs.org_rule('Intersight Organization', org, 1, 62)

    print(f'\n-------------------------------------------------------------------------------------------\n')
    print(f'  By Default, the Intersight Organization will be used as the Name Prefix for Pools ')
    print(f'  and Policies.  To Assign a different Prefix to the Pools and Policies use the prefix ')
    print(f'  options below.  As Options, a different prefix for UCS domain policies and a prefix')
    print(f'  for Pools and Server Policies can be entered to override the default behavior.')
    print(f'\n-------------------------------------------------------------------------------------------\n')

    valid = False
    while valid == False:
        domain_prefix = input('Enter a Name Prefix for Domain Profile Policies.  [press enter to skip]: ')
        if domain_prefix == '':
            valid = True
        else:
            valid = validating_ucs.name_rule(f"Name Prefix", domain_prefix, 1, 62)
    valid = False
    while valid == False:
        name_prefix = input('Enter a Name Prefix for Pools and Server Policies.  [press enter to skip]: ')
        if name_prefix == '':
            valid = True
        else:
            valid = validating_ucs.name_rule(f"Name Prefix", name_prefix, 1, 62)

    for policy in policy_list:
        pci_order_consumed = [{0:[]},{1:[]}]
        type = 'pools'
        if policy == 'ip_pools':
            lib_ucs.easy_imm_wizard(name_prefix, org, type).ip_pools()
        elif policy == 'iqn_pools':
            lib_ucs.easy_imm_wizard(name_prefix, org, type).iqn_pools()
        elif policy == 'mac_pools':
            lib_ucs.easy_imm_wizard(name_prefix, org, type).mac_pools()
        elif policy == 'wwnn_pools':
            lib_ucs.easy_imm_wizard(name_prefix, org, type).wwnn_pools()
        elif policy == 'wwpn_pools':
            lib_ucs.easy_imm_wizard(name_prefix, org, type).wwpn_pools()
        elif policy == 'uuid_pools':
            lib_ucs.easy_imm_wizard(name_prefix, org, type).uuid_pools()

        type = 'policies_vlans'
        if policy == 'multicast_policies':
            lib_ucs.easy_imm_wizard(domain_prefix, org, type).multicast_policies()
        elif policy == 'vlan_policies':
            lib_ucs.easy_imm_wizard(domain_prefix, org, type).vlan_policies()

        type = 'policies'
        #================================
        # Policies needed for 1st release
        #================================
        # boot_order_policies
        # lan_connectivity_policies
        # sd_card_policies
        # storage_policies
        # ucs_server_profiles
        # virtual_media_policies
        #================================
        # Policies needed for 2nd release
        #================================
        # certificate_management_policies
        # iscsi_adapter_policies
        # iscsi_boot_policies
        # iscsi_static_target_policies
        if policy == 'adapter_configuration_policies':
            lib_ucs.easy_imm_wizard(name_prefix, org, type).adapter_configuration_policies()
        if policy == 'bios_policies':
            lib_ucs.easy_imm_wizard(name_prefix, org, type).bios_policies()
        if policy == 'boot_order_policies':
            lib_ucs.easy_imm_wizard(name_prefix, org, type).boot_order_policies()
        #========================================================
        # Certificate Management Policies doesn't work
        #========================================================
        # elif policy == 'certificate_management_policies':
        #     lib_ucs.easy_imm_wizard(name_prefix, org, type).certificate_management_policies()
        elif policy == 'device_connector_policies':
            lib_ucs.easy_imm_wizard(name_prefix, org, type).device_connector_policies()
        elif policy == 'ethernet_adapter_policies':
            lib_ucs.easy_imm_wizard(name_prefix, org, type).ethernet_adapter_policies()
        elif policy == 'ethernet_network_control_policies':
            lib_ucs.easy_imm_wizard(name_prefix, org, type).ethernet_network_control_policies()
        elif policy == 'ethernet_network_group_policies':
            lib_ucs.easy_imm_wizard(name_prefix, org, type).ethernet_network_group_policies()
        elif policy == 'ethernet_network_policies':
            lib_ucs.easy_imm_wizard(name_prefix, org, type).ethernet_network_policies()
        elif policy == 'ethernet_qos_policies':
            lib_ucs.easy_imm_wizard(name_prefix, org, type).ethernet_qos_policies()
        elif policy == 'fibre_channel_adapter_policies':
            lib_ucs.easy_imm_wizard(name_prefix, org, type).fibre_channel_adapter_policies()
        elif policy == 'fibre_channel_network_policies':
            lib_ucs.easy_imm_wizard(name_prefix, org, type).fibre_channel_network_policies()
        elif policy == 'fibre_channel_qos_policies':
            lib_ucs.easy_imm_wizard(name_prefix, org, type).fibre_channel_qos_policies()
        elif policy == 'flow_control_policies':
            lib_ucs.easy_imm_wizard(domain_prefix, org, type).flow_control_policies()
        elif policy == 'imc_access_policies':
            lib_ucs.easy_imm_wizard(name_prefix, org, type).imc_access_policies()
        elif policy == 'ipmi_over_lan_policies':
            lib_ucs.easy_imm_wizard(name_prefix, org, type).ipmi_over_lan_policies()
        #========================================================
        # Policies that Will not be Supported at initial Release
        #========================================================
        # elif policy == 'iscsi_adapter_policies':
        #     lib_ucs.easy_imm_wizard(name_prefix, org, type).iscsi_adapter_policies()
        # elif policy == 'iscsi_boot_policies':
        #     lib_ucs.easy_imm_wizard(name_prefix, org, type).iscsi_boot_policies()
        # elif policy == 'iscsi_static_target_policies':
        #     lib_ucs.easy_imm_wizard(name_prefix, org, type).iscsi_static_target_policies()
        elif policy == 'lan_connectivity_policies':
            lib_ucs.easy_imm_wizard(name_prefix, org, type).lan_connectivity_policies()
        elif policy == 'ldap_policies':
            lib_ucs.easy_imm_wizard(name_prefix, org, type).ldap_policies()
        elif policy == 'link_aggregation_policies':
            lib_ucs.easy_imm_wizard(domain_prefix, org, type).link_aggregation_policies()
        elif policy == 'link_control_policies':
            lib_ucs.easy_imm_wizard(domain_prefix, org, type).link_control_policies()
        elif policy == 'local_user_policies':
            lib_ucs.easy_imm_wizard(name_prefix, org, type).local_user_policies()
        elif policy == 'network_connectivity_policies':
            lib_ucs.easy_imm_wizard(name_prefix, org, type).network_connectivity_policies()
        elif policy == 'ntp_policies':
            lib_ucs.easy_imm_wizard(name_prefix, org, type).ntp_policies()
        elif policy == 'persistent_memory_policies':
            lib_ucs.easy_imm_wizard(name_prefix, org, type).persistent_memory_policies()
        elif policy == 'port_policies':
            lib_ucs.easy_imm_wizard(domain_prefix, org, type).port_policies()
        elif policy == 'power_policies':
            lib_ucs.easy_imm_wizard(name_prefix, org, type).power_policies()
        #========================================================
        # Work in Progress
        # Need to finish LAN Policies for pci_order_consumed
        #========================================================
        elif policy == 'san_connectivity_policies':
            pci_order_consumed = [{0:[0, 1, 2, 3, 4, 5, 6, 7]},{1:[0, 1, 2, 3, 4, 5, 6, 7]}]
            lib_ucs.easy_imm_wizard(name_prefix, org, type).san_connectivity_policies(pci_order_consumed)
        elif policy == 'sd_card_policies':
            lib_ucs.easy_imm_wizard(name_prefix, org, type).sd_card_policies()
        elif policy == 'serial_over_lan_policies':
            lib_ucs.easy_imm_wizard(name_prefix, org, type).serial_over_lan_policies()
        elif policy == 'smtp_policies':
            lib_ucs.easy_imm_wizard(name_prefix, org, type).smtp_policies()
        elif policy == 'snmp_policies':
            lib_ucs.easy_imm_wizard(name_prefix, org, type).snmp_policies()
        elif policy ==  'ssh_policies':
             lib_ucs.easy_imm_wizard(name_prefix, org, type).ssh_policies()
        elif policy == 'storage_policies':
            lib_ucs.easy_imm_wizard(name_prefix, org, type).storage_policies()
        elif policy == 'switch_control_policies':
            lib_ucs.easy_imm_wizard(domain_prefix, org, type).switch_control_policies()
        elif policy == 'syslog_policies':
            lib_ucs.easy_imm_wizard(name_prefix, org, type).syslog_policies()
        elif policy == 'system_qos_policies':
            lib_ucs.easy_imm_wizard(domain_prefix, org, type).system_qos_policies()
        elif policy == 'thermal_policies':
            lib_ucs.easy_imm_wizard(name_prefix, org, type).thermal_policies()
        elif policy == 'virtual_kvm_policies':
            lib_ucs.easy_imm_wizard(name_prefix, org, type).virtual_kvm_policies()
        elif policy == 'virtual_media_policies':
            lib_ucs.easy_imm_wizard(name_prefix, org, type).virtual_media_policies()
        elif policy == 'vsan_policies':
            lib_ucs.easy_imm_wizard(domain_prefix, org, type).vsan_policies()

        type = 'ucs_chassis_profiles'
        if policy == 'ucs_chassis_profiles':
            lib_ucs.easy_imm_wizard(domain_prefix, org, type).ucs_chassis_profiles()

        type = 'ucs_domain_profiles'
        if policy == 'ucs_domain_profiles':
            lib_ucs.easy_imm_wizard(domain_prefix, org, type).ucs_domain_profiles(name_prefix)

        type = 'ucs_server_profiles'
        if policy == 'ucs_server_profile_templates':
            lib_ucs.easy_imm_wizard(name_prefix, org, type).ucs_server_profile_templates()
        elif policy == 'ucs_server_profiles':
            lib_ucs.easy_imm_wizard(name_prefix, org, type).ucs_server_profiles()

    # 35 Complete 7 to go



    print(f'\n-------------------------------------------------------------------------------------------\n')
    print(f'  Proceedures Complete!!! Closing Environment and Exiting Script.')
    print(f'\n-------------------------------------------------------------------------------------------\n')
    exit()

def main():
    if len(sys.argv) > 1:
        json_file = sys.argv[1]
        json_open = open(json_file, 'r')
        json_data = json.load(json_open)
        process_config_conversion(json_data)
    else:
        process_wizard()

if __name__ == '__main__':
    main()
