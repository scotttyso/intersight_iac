#!/usr/bin/env python3

import copy
import ipaddress
import jinja2
import pkg_resources
import re
from easy_functions import process_method

ucs_template_path = pkg_resources.resource_filename('class_imm_transition', 'Templates/')

class imm_transition(object):
    def __init__(self, json_data, type):
        self.json_data = json_data
        self.templateLoader = jinja2.FileSystemLoader(
            searchpath=(ucs_template_path + '%s/') % (type))
        self.templateEnv = jinja2.Environment(loader=self.templateLoader)
        self.templateVars = {}
        self.type = type
        self.orgs = []
        for item in json_data["config"]["orgs"]:
            for k, v in item.items():
                if k == 'name':
                    self.orgs.append(v)

    def return_orgs(self):
        orgs = self.orgs
        return orgs

    def bios_policies(self):
        header = 'BIOS Policy Variables'
        initial_policy = True
        template_type = 'bios_policies'
        policy_loop_standard(self, header, initial_policy, template_type)

    def boot_order_policies(self):
        header = 'Boot Order Policy Variables'
        initial_policy = True
        template_type = 'boot_order_policies'
        policy_loop_standard(self, header, initial_policy, template_type)

    def ethernet_adapter_policies(self):
        header = 'Ethernet Adapter Policy Variables'
        initial_policy = True
        template_type = 'ethernet_adapter_policies'
        policy_loop_standard(self, header, initial_policy, template_type)

    def ethernet_network_control_policies(self):
        header = 'Ethernet Network Control Policy Variables'
        initial_policy = True
        template_type = 'ethernet_network_control_policies'
        policy_loop_standard(self, header, initial_policy, template_type)

    def ethernet_network_group_policies(self):
        header = 'Ethernet Network Group Policy Variables'
        initial_policy = True
        template_type = 'ethernet_network_group_policies'
        policy_loop_standard(self, header, initial_policy, template_type)

    def ethernet_network_policies(self):
        header = 'Ethernet Network Policy Variables'
        initial_policy = True
        template_type = 'ethernet_network_policies'
        policy_loop_standard(self, header, initial_policy, template_type)

    def ethernet_qos_policies(self):
        header = 'Ethernet QoS Policy Variables'
        initial_policy = True
        template_type = 'ethernet_qos_policies'
        policy_loop_standard(self, header, initial_policy, template_type)

    def fibre_channel_adapter_policies(self):
        header = 'Fibre-Channel Adapter Policy Variables'
        initial_policy = True
        template_type = 'fibre_channel_adapter_policies'
        policy_loop_standard(self, header, initial_policy, template_type)

    def fibre_channel_network_policies(self):
        header = 'Fibre-Channel Network Policy Variables'
        initial_policy = True
        template_type = 'fibre_channel_network_policies'
        policy_loop_standard(self, header, initial_policy, template_type)

    def fibre_channel_qos_policies(self):
        header = 'Fibre-Channel QoS Policy Variables'
        initial_policy = True
        template_type = 'fibre_channel_qos_policies'
        policy_loop_standard(self, header, initial_policy, template_type)

    def flow_control_policies(self):
        header = 'Flow Control Policy Variables'
        initial_policy = True
        template_type = 'flow_control_policies'
        policy_loop_standard(self, header, initial_policy, template_type)

    def imc_access_policies(self):
        header = 'IMC Access Policiy Variables'
        initial_policy = True
        template_type = 'imc_access_policies'
        policy_loop_standard(self, header, initial_policy, template_type)

    def ip_pools(self):
        header = 'IP Pool Variables'
        initial_policy = True
        template_type = 'ip_pools'
        policy_loop_standard(self, header, initial_policy, template_type)

    def ipmi_over_lan_policies(self):
        header = 'IPMI over LAN Policy Variables'
        initial_policy = True
        template_type = 'ipmi_over_lan_policies'
        policy_loop_standard(self, header, initial_policy, template_type)

    def iqn_pools(self):
        header = 'IQN Pool Variables'
        initial_policy = True
        template_type = 'iqn_pools'
        policy_loop_standard(self, header, initial_policy, template_type)

    def iscsi_adapter_policies(self):
        header = 'iSCSI Adapter Policy Variables'
        initial_policy = True
        template_type = 'iscsi_adapter_policies'
        policy_loop_standard(self, header, initial_policy, template_type)

    def iscsi_boot_policies(self):
        header = 'iSCSI Boot Policy Variables'
        initial_policy = True
        template_type = 'iscsi_boot_policies'
        policy_loop_standard(self, header, initial_policy, template_type)

    def iscsi_static_target_policies(self):
        header = 'iSCSI Static Target Policy Variables'
        initial_policy = True
        template_type = 'iscsi_static_target_policies'
        policy_loop_standard(self, header, initial_policy, template_type)

    def lan_connectivity_policies(self):
        header = 'LAN Connectivity Policy Variables'
        initial_policy = True
        template_type = 'lan_connectivity_policies'
        policy_loop_standard(self, header, initial_policy, template_type)

    def link_aggregation_policies(self):
        header = 'Link Aggregation Policy Variables'
        initial_policy = True
        template_type = 'link_aggregation_policies'
        policy_loop_standard(self, header, initial_policy, template_type)

    def link_control_policies(self):
        header = 'Link Control Policy Variables'
        initial_policy = True
        template_type = 'link_control_policies'
        policy_loop_standard(self, header, initial_policy, template_type)

    def mac_pools(self):
        header = 'MAC Pool Variables'
        initial_policy = True
        template_type = 'mac_pools'
        policy_loop_standard(self, header, initial_policy, template_type)

    def multicast_policies(self):
        header = 'Multicast Policy Variables'
        initial_policy = True
        template_type = 'multicast_policies'
        policy_loop_standard(self, header, initial_policy, template_type)

    def network_connectivity_policies(self):
        header = 'Network Connectivity (DNS) Policy Variables'
        initial_policy = True
        template_type = 'network_connectivity_policies'
        policy_loop_standard(self, header, initial_policy, template_type)

    def ntp_policies(self):
        header = 'NTP Policy Variables'
        initial_policy = True
        template_type = 'ntp_policies'
        policy_loop_standard(self, header, initial_policy, template_type)

    def port_policies(self):
        header = 'Port Policy Variables'
        initial_policy = True
        template_type = 'port_policies'

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
                    for k, v in item.items():
                        if re.search(r'(_port_channels)', k):
                            templateVars[k] = []
                            attribute_list = {}
                            for i in v:
                                interface_list = []
                                for key, value in i.items():
                                    attribute_list.update({key: value})

                                attribute_list = dict(sorted(attribute_list.items()))
                                xdeep = copy.deepcopy(attribute_list)
                                templateVars[k].append(xdeep)

                        elif re.search(r'(server_ports)', k):
                            aggr_ids = []
                            ports_count = 0
                            templateVars[k] = []
                            slot_ids = []
                            for i in v:
                                for key, value in i.items():
                                    if key == 'aggr_id':
                                        aggr_ids.append(value)
                                    if key == 'slot_id':
                                        slot_ids.append(value)
                            aggr_ids = list(set(aggr_ids))
                            slot_ids = list(set(slot_ids))
                            if len(aggr_ids) or len(slot_ids) > 1:
                                for i in v:
                                    attribute_list = {}
                                    port_list = []
                                    for key, value in i.items():
                                        if key == 'aggr_id':
                                            attribute_list.update({'breakout_port_id': value})
                                        elif key == 'port_id':
                                            port_list.append(value)
                                        else:
                                            attribute_list.update({'slot_id': value})
                                    attribute_list.update({'key_id': ports_count})
                                    attribute_list.update({'port_list': port_list})
                                    attribute_list = dict(sorted(attribute_list.items()))
                                    xdeep = copy.deepcopy(attribute_list)
                                    templateVars[k].append(xdeep)
                                    ports_count += 1
                            else:
                                attribute_list = {}
                                port_list = []
                                for i in v:
                                    for key, value in i.items():
                                        if key == 'aggr_id':
                                            attribute_list.update({'aggr_id': value})
                                        elif key == 'port_id':
                                            port_list.append(value)
                                        elif key == 'slot_id':
                                            attribute_list.update({'slot_id': value})
                                attribute_list.update({'key_id': ports_count})
                                ports_count += 1
                                port_list = ",".join("{0}".format(n) for n in port_list)
                                attribute_list.update({'port_list': port_list})
                                attribute_list = dict(sorted(attribute_list.items()))
                                xdeep = copy.deepcopy(attribute_list)
                                templateVars[k].append(xdeep)
                            # print(k, templateVars[k])
                        elif re.search(r'(san_unified_ports)', k):
                            for key, value in v.items():
                                if key == 'port_id_start':
                                    begin = value
                                elif key == 'port_id_end':
                                    end = value
                                elif key == 'slot_id':
                                    slot_id = value
                            templateVars["port_modes"] = {'port_list': [begin, end], 'slot_id': slot_id}
                        elif re.search(r'(_ports)$', k):
                            ports_count = 0
                            templateVars[k] = []
                            attribute_list = {}
                            for i in v:
                                for key, value in i.items():
                                    attribute_list.update({key: value})
                                attribute_list.update({'key_id': ports_count})
                                attribute_list = dict(sorted(attribute_list.items()))
                                xdeep = copy.deepcopy(attribute_list)
                                templateVars[k].append(xdeep)
                                ports_count += 1
                        else:
                            templateVars[k] = v
                    if 'appliance_port_channels' in templateVars:
                        templateVars["port_channel_appliances"] = templateVars["appliance_port_channels"]
                        del templateVars["appliance_port_channels"]
                    if 'lan_port_channels' in templateVars:
                        templateVars["port_channel_ethernet_uplinks"] = templateVars["lan_port_channels"]
                        del templateVars["lan_port_channels"]
                    if 'san_port_channels' in templateVars:
                        templateVars["port_channel_fc_uplinks"] = templateVars["san_port_channels"]
                        del templateVars["san_port_channels"]
                    if 'fcoe_port_channels' in templateVars:
                        templateVars["port_channel_fcoe_uplinks"] = templateVars["fcoe_port_channels"]
                        del templateVars["fcoe_port_channels"]
                    if 'appliance_ports' in templateVars:
                        templateVars["port_role_appliances"] = templateVars["appliance_ports"]
                        del templateVars["appliance_ports"]
                    if 'lan_uplink_ports' in templateVars:
                        templateVars["port_role_ethernet_uplinks"] = templateVars["lan_uplink_ports"]
                        del templateVars["lan_uplink_ports"]
                    if 'storage_ports' in templateVars:
                        templateVars["port_role_fc_storage"] = templateVars["storage_ports"]
                        del templateVars["storage_ports"]
                    if 'san_uplink_ports' in templateVars:
                        templateVars["port_role_fc_uplinks"] = templateVars["san_uplink_ports"]
                        del templateVars["san_uplink_ports"]
                    if 'fcoe_uplink_ports' in templateVars:
                        templateVars["port_role_fcoe_uplinks"] = templateVars["fcoe_uplink_ports"]
                        del templateVars["fcoe_uplink_ports"]
                    if 'server_ports' in templateVars:
                        templateVars["port_role_servers"] = templateVars["server_ports"]
                        del templateVars["server_ports"]

                    templateVars = dict(sorted(templateVars.items()))
                    # print(templateVars)

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

    def power_policies(self):
        header = 'Power Policy Variables'
        initial_policy = True
        template_type = 'power_policies'
        policy_loop_standard(self, header, initial_policy, template_type)

    def san_connectivity_policies(self):
        header = 'SAN Connectivity Policy Variables'
        initial_policy = True
        template_type = 'san_connectivity_policies'
        policy_loop_standard(self, header, initial_policy, template_type)

    def sd_card_policies(self):
        header = 'SD Card Policy Variables'
        initial_policy = True
        template_type = 'sd_card_policies'
        policy_loop_standard(self, header, initial_policy, template_type)

    def serial_over_lan_policies(self):
        header = 'Serial over LAN Policy Variables'
        initial_policy = True
        template_type = 'serial_over_lan_policies'
        policy_loop_standard(self, header, initial_policy, template_type)

    def snmp_policies(self):
        header = 'SNMP Policy Variables'
        initial_policy = True
        template_type = 'snmp_policies'
        policy_loop_standard(self, header, initial_policy, template_type)

    def storage_policies(self):
        header = 'Storage Policy Variables'
        initial_policy = True
        template_type = 'storage_policies'
        policy_loop_standard(self, header, initial_policy, template_type)

    def switch_control_policies(self):
        header = 'Switch Control Policy Variables'
        initial_policy = True
        template_type = 'switch_control_policies'
        policy_loop_standard(self, header, initial_policy, template_type)

    def syslog_policies(self):
        header = 'Syslog Policy Variables'
        initial_policy = True
        template_type = 'syslog_policies'
        policy_loop_standard(self, header, initial_policy, template_type)

    def system_qos_policies(self):
        header = 'System QoS Policy Variables'
        initial_policy = True
        template_type = 'system_qos_policies'
        policy_loop_standard(self, header, initial_policy, template_type)

    def thermal_policies(self):
        header = 'Thermal Policy Variables'
        initial_policy = True
        template_type = 'thermal_policies'
        policy_loop_standard(self, header, initial_policy, template_type)

    def ucs_chassis_profiles(self):
        header = 'UCS Chassis Profile Variables'
        initial_policy = True
        template_type = 'ucs_chassis_profiles'
        policy_loop_standard(self, header, initial_policy, template_type)

    def ucs_domain_profiles(self):
        header = 'UCS Domain Profile Variables'
        initial_policy = True
        template_type = 'ucs_domain_profiles'
        policy_loop_standard(self, header, initial_policy, template_type)

    def ucs_server_profiles(self):
        header = 'UCS Server Profile Variables'
        initial_policy = True
        template_type = 'ucs_server_profiles'
        policy_loop_standard(self, header, initial_policy, template_type)

    def ucs_server_profile_templates(self):
        header = 'UCS Server Profile Template Variables'
        initial_policy = True
        template_type = 'ucs_server_profile_templates'
        policy_loop_standard(self, header, initial_policy, template_type)

    def virtual_kvm_policies(self):
        header = 'Virtual KVM Policy Variables'
        initial_policy = True
        template_type = 'virtual_kvm_policies'
        policy_loop_standard(self, header, initial_policy, template_type)

    def virtual_media_policies(self):
        header = 'Virtual Media Policy Variables'
        initial_policy = True
        template_type = 'virtual_media_policies'
        policy_loop_standard(self, header, initial_policy, template_type)

    def vlan_policies(self):
        header = 'VLAN Policy Variables'
        initial_policy = True
        template_type = 'vlan_policies'
        policy_loop_standard(self, header, initial_policy, template_type)

    def vsan_policies(self):
        header = 'VSAN Policy Variables'
        initial_policy = True
        template_type = 'vsan_policies'
        policy_loop_standard(self, header, initial_policy, template_type)

    def uuid_pools(self):
        header = 'UUID Pool Variables'
        initial_policy = True
        template_type = 'uuid_pools'
        policy_loop_standard(self, header, initial_policy, template_type)

    def wwnn_pools(self):
        header = 'Fibre-Channel WWNN Pool Variables'
        initial_policy = True
        template_type = 'wwnn_pools'
        policy_loop_standard(self, header, initial_policy, template_type)

    def wwpn_pools(self):
        header = 'Fibre-Channel WWPN Pool Variables'
        initial_policy = True
        template_type = 'wwpn_pools'
        policy_loop_standard(self, header, initial_policy, template_type)

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

        if template_type == 'boot_order_policies':
            imm_template_type = 'boot_policies'
        else:
            imm_template_type = template_type
        if imm_template_type in self.json_data["config"]["orgs"][org_count]:
            for item in self.json_data["config"]["orgs"][org_count][imm_template_type]:
                # Reset TemplateVars to Default for each Loop
                templateVars = {}
                templateVars["org"] = org

                # Define the Template Source
                templateVars["header"] = header

                # Loop Through Json Items to Create templateVars Blocks
                if template_type == 'bios_policies':
                    for k, v in item.items():
                        if (k == 'name' or k == 'descr' or k == 'tags'):
                            templateVars[k] = v

                    templateVars["bios_settings"] = {}
                    for k, v in item.items():
                        if not (k == 'name' or k == 'descr' or k == 'tags'):
                            templateVars["bios_settings"][k] = v
                elif template_type == 'system_qos_policies':
                    for k, v in item.items():
                        if (k == 'name' or k == 'descr' or k == 'tags'):
                            templateVars[k] = v

                    templateVars["classes"] = [{},{},{},{},{},{}]
                    for key, value in item.items():
                        if key == 'classes':
                            class_count = 0
                            for i in value:
                                for k, v in i.items():
                                    templateVars["classes"][class_count][k] = v
                                class_count += 1
                else:
                    for k, v in item.items():
                        templateVars[k] = v

                if template_type == 'ip_pools':
                    if 'ipv4_blocks' in templateVars:
                        index_count = 0
                        for i in templateVars["ipv4_blocks"]:
                             index_count += 1
                        for r in range(0,index_count):
                            if 'to' in templateVars["ipv4_blocks"][r]:
                                templateVars["ipv4_blocks"][r]["size"] = int(
                                    ipaddress.IPv4Address(templateVars["ipv4_blocks"][r]["to"])
                                    ) - int(ipaddress.IPv4Address(templateVars["ipv4_blocks"][r]["from"])) + 1
                                ipv4_to = templateVars["ipv4_blocks"][r]['to']
                                templateVars["ipv4_blocks"][r].pop('to')
                                templateVars["ipv4_blocks"][r]['to'] = ipv4_to

                    if 'ipv6_blocks' in templateVars:
                        index_count = 0
                        for i in templateVars["ipv6_blocks"]:
                             index_count += 1
                        for r in range(0,index_count):
                            if 'to' in templateVars["ipv6_blocks"][r]:
                                templateVars["ipv6_blocks"][r]["size"] = int(
                                    ipaddress.IPv6Address(templateVars["ipv6_blocks"][r]["to"])
                                    ) - int(ipaddress.IPv6Address(templateVars["ipv6_blocks"][r]["from"])) + 1
                                ipv6_to = templateVars["ipv6_blocks"][r]['to']
                                templateVars["ipv6_blocks"][r].pop('to')
                                templateVars["ipv6_blocks"][r]['to'] = ipv6_to
                elif template_type == 'iqn_pools':
                    if 'iqn_blocks' in templateVars:
                        index_count = 0
                        for i in templateVars["iqn_blocks"]:
                             index_count += 1
                        for r in range(0,index_count):
                            if 'to' in templateVars["iqn_blocks"][r]:
                                templateVars["iqn_blocks"][r]["size"] = int(
                                    templateVars["iqn_blocks"][r]["to"]
                                    ) - int(templateVars["iqn_blocks"][r]["from"]) + 1
                                iqn_to = templateVars["iqn_blocks"][r]["to"]
                                templateVars["iqn_blocks"][r].pop('to')
                                templateVars["iqn_blocks"][r]["to"] = iqn_to
                elif template_type == 'mac_pools':
                    if 'mac_blocks' in templateVars:
                        index_count = 0
                        for i in templateVars["mac_blocks"]:
                             index_count += 1
                        for r in range(0,index_count):
                            if 'to' in templateVars["mac_blocks"][r]:
                                int_from = int(templateVars["mac_blocks"][r]["from"].replace(':', ''), 16)
                                int_to = int(templateVars["mac_blocks"][r]["to"].replace(':', ''), 16)
                                templateVars["mac_blocks"][r]["size"] = int_to - int_from + 1
                                mac_to = templateVars["mac_blocks"][r]["to"]
                                templateVars["mac_blocks"][r].pop('to')
                                templateVars["mac_blocks"][r]["to"] = mac_to
                elif template_type == 'system_qos_policies':
                    total_weight = 0
                    for r in range(0,6):
                        if templateVars["classes"][r]["state"] == 'Enabled':
                            total_weight += int(templateVars["classes"][r]["weight"])
                    for r in range(0,6):
                        if templateVars["classes"][r]["state"] == 'Enabled':
                            x = ((int(templateVars["classes"][r]["weight"]) / total_weight) * 100)
                            templateVars["classes"][r]["bandwidth_percent"] = str(x).split('.')[0]
                        else:
                            templateVars["classes"][r]["bandwidth_percent"] = 0
                elif template_type == 'uuid_pools':
                    if 'uuid_blocks' in templateVars:
                        index_count = 0
                        for i in templateVars["uuid_blocks"]:
                             index_count += 1
                        for r in range(0,index_count):
                            if 'to' in templateVars["uuid_blocks"][r]:
                                if re.search('[a-zA-Z]', templateVars["uuid_blocks"][r]["from"].split('-')[1]) or re.search('[a-zA-Z]', templateVars["uuid_blocks"][r]["to"].split('-')[1]):
                                    int_from = int(templateVars["uuid_blocks"][r]["from"].split('-')[1], 16)
                                    int_to = int(templateVars["uuid_blocks"][r]["to"].split('-')[1], 16)
                                else:
                                    int_from = int(templateVars["uuid_blocks"][r]["from"].split('-')[1])
                                    int_to = int(templateVars["uuid_blocks"][r]["to"].split('-')[1])
                                templateVars["uuid_blocks"][r]["size"] = int_to - int_from + 1
                                uuid_to = templateVars["uuid_blocks"][r]["to"]
                                templateVars["uuid_blocks"][r].pop('to')
                                templateVars["uuid_blocks"][r]["to"] = uuid_to
                elif template_type == 'wwnn_pools':
                    if 'wwnn_blocks' in templateVars:
                        index_count = 0
                        for i in templateVars["wwnn_blocks"]:
                             index_count += 1
                        for r in range(0,index_count):
                            if 'to' in templateVars["wwnn_blocks"][r]:
                                int_from = int(templateVars["wwnn_blocks"][r]["from"].replace(':', ''), 16)
                                int_to = int(templateVars["wwnn_blocks"][r]["to"].replace(':', ''), 16)
                                templateVars["wwnn_blocks"][r]["size"] = int_to - int_from + 1
                                wwxn_to = templateVars["wwnn_blocks"][r]["to"]
                                templateVars["wwnn_blocks"][r].pop('to')
                                templateVars["wwnn_blocks"][r]["to"] = wwxn_to
                elif template_type == 'wwpn_pools':
                    if 'wwpn_blocks' in templateVars:
                        index_count = 0
                        for i in templateVars["wwpn_blocks"]:
                             index_count += 1
                        for r in range(0,index_count):
                            if 'to' in templateVars["wwpn_blocks"][r]:
                                int_from = int(templateVars["wwpn_blocks"][r]["from"].replace(':', ''), 16)
                                int_to = int(templateVars["wwpn_blocks"][r]["to"].replace(':', ''), 16)
                                templateVars["wwpn_blocks"][r]["size"] = int_to - int_from + 1
                                wwxn_to = templateVars["wwpn_blocks"][r]["to"]
                                templateVars["wwpn_blocks"][r].pop('to')
                                templateVars["wwpn_blocks"][r]["to"] = wwxn_to
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
