#!/usr/bin/env python3

import copy
import ipaddress
import jinja2
import json
import os
import pkg_resources
import re
import subprocess
import stdiomask
import sys
import validating
from textwrap import fill

ucs_template_path = pkg_resources.resource_filename('lib_ucs', 'Templates/')

class config_conversion(object):
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
                        if (k == 'name' or k == 'descr' or k == 'tags'):
                            templateVars[k] = v

                    templateVars["bios_settings"] = {}
                    for k, v in item.items():
                        if not (k == 'name' or k == 'descr' or k == 'tags'):
                            templateVars["bios_settings"][k] = v

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

    def boot_order_policies(self):
        header = 'Boot Order Policy Variables'
        initial_policy = True
        template_type = 'boot_policies'

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
        header = 'Fibre Channel Adapter Policy Variables'
        initial_policy = True
        template_type = 'fibre_channel_adapter_policies'

        policy_loop_standard(self, header, initial_policy, template_type)

    def fibre_channel_network_policies(self):
        header = 'Fibre Channel Network Policy Variables'
        initial_policy = True
        template_type = 'fibre_channel_network_policies'

        policy_loop_standard(self, header, initial_policy, template_type)

    def fibre_channel_qos_policies(self):
        header = 'Fibre Channel QoS Policy Variables'
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
                        templateVars[k] = v

                    if 'ipv6_blocks' in templateVars:
                        index_count = 0
                        for i in templateVars["ipv6_blocks"]:
                             index_count += 1

                        for r in range(0,index_count):
                            if 'to' in templateVars["ipv6_blocks"][r]:
                                templateVars["ipv6_blocks"][r]["size"] = templateVars["ipv6_blocks"][r].pop('to')
                                templateVars["ipv6_blocks"][r]["size"] = int(
                                    ipaddress.IPv6Address(templateVars["ipv6_blocks"][r]["size"])
                                    ) - int(ipaddress.IPv6Address(templateVars["ipv6_blocks"][r]["from"])) + 1

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

    def ipmi_over_lan_policies(self):
        header = 'IPMI over LAN Policy Variables'
        initial_policy = True
        template_type = 'ipmi_over_lan_policies'

        policy_loop_standard(self, header, initial_policy, template_type)

    def iqn_pools(self):
        header = 'IQN Pool Variables'
        initial_policy = True
        template_type = 'iqn_pools'

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
                        templateVars[k] = v

                    if 'iqn_blocks' in templateVars:
                        index_count = 0
                        for i in templateVars["iqn_blocks"]:
                             index_count += 1

                        for r in range(0,index_count):
                            if 'to' in templateVars["iqn_blocks"][r]:
                                templateVars["iqn_blocks"][r]["size"] = templateVars["iqn_blocks"][r].pop('to')
                                templateVars["iqn_blocks"][r]["size"] = int(
                                    templateVars["iqn_blocks"][r]["size"]
                                    ) - int(templateVars["iqn_blocks"][r]["from"]) + 1

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
                                    #if key == 'interfaces':
                                    #    for interfaces in value:
                                    #        int_dict = {}
                                    #        for keys, values in interfaces.items():
                                    #            if keys == 'aggr_id':
                                    #                int_dict.update({'breakout_port_id': values})
                                    #            elif keys == 'port_id':
                                    #                int_dict.update({'port_id': values})
                                    #            elif keys == 'slot_id':
                                    #                int_dict.update({'slot_id': values})
                                    #        x = copy.deepcopy(int_dict)
                                    #        interface_list.append(x)
                                    #        int_dict = {}
                                    # else:
                                    #     attribute_list.update({key: value})
                                    # attribute_list.update({'interfaces': interface_list})
                                    attribute_list.update({key: value})

                                attribute_list = dict(sorted(attribute_list.items()))
                                xdeep = copy.deepcopy(attribute_list)
                                templateVars[k].append(xdeep)
                                # print(k, templateVars[k])
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
                            # print(k, templateVars[k])
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
                        print(templateVars["port_channel_fc_uplinks"])
                    if 'fcoe_port_channels' in templateVars:
                        templateVars["port_channel_fcoe_uplinks"] = templateVars["fcoe_port_channels"]
                        del templateVars["fcoe_port_channels"]
                    if 'appliance_ports' in templateVars:
                        templateVars["port_role_appliances"] = templateVars["appliance_ports"]
                        del templateVars["appliance_ports"]
                    if 'lan_uplink_ports' in templateVars:
                        templateVars["port_role_ethernet_uplinks"] = templateVars["lan_uplink_ports"]
                        del templateVars["lan_uplink_ports"]
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
                        if (k == 'name' or k == 'descr' or k == 'tags'):
                            templateVars[k] = v

                templateVars["classes"] = []
                for r in range(0,6):
                    xdict = {}
                    templateVars["classes"].append(xdict)

                class_count = 0
                for item in self.json_data["config"]["orgs"][org_count][template_type][0]["classes"]:
                    for k, v in item.items():
                        templateVars["classes"][class_count][k] = v

                    class_count += 1

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

    def thermal_policies(self):
        header = 'Thermal Policy Variables'
        initial_policy = True
        template_type = 'thermal_policies'

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
        header = 'Fibre Channel WWNN Pool Variables'
        initial_policy = True
        template_type = 'wwnn_pools'

        policy_loop_standard(self, header, initial_policy, template_type)

    def wwpn_pools(self):
        header = 'Fibre Channel WWPN Pool Variables'
        initial_policy = True
        template_type = 'wwpn_pools'

        policy_loop_standard(self, header, initial_policy, template_type)

class easy_imm_wizard(object):
    def __init__(self, name_prefix, org, type):
        self.templateLoader = jinja2.FileSystemLoader(
            searchpath=(ucs_template_path + '%s/') % (type))
        self.templateEnv = jinja2.Environment(loader=self.templateLoader)
        self.name_prefix = name_prefix
        self.org = org
        self.type = type

    #========================================
    # Adapter Configuration Policy Module
    #========================================
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
            print(f'  This wizard will save the configuraton for this section to the following file:')
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

    #========================================
    # BIOS Policy Module
    #========================================
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
            print(f'  This wizard will save the configuraton for this section to the following file:')
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

    #========================================
    # Boot Order Policy Module
    #========================================
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
            print(f'  This wizard will save the configuraton for this section to the following file:')
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

    #========================================
    # Device Connector Policy Module
    #========================================
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
            print(f'  This wizard will save the configuraton for this section to the following file:')
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

    #========================================
    # Ethernet Adapter Policy Module
    #========================================
    def ethernet_adapter_policies(self, jsonData, easy_jsonData):
        name_prefix = self.name_prefix
        org = self.org
        policy_type = 'Ethernet Adapter Policy'
        policy_x = 'Ethernet Adapter'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["name_prefix"] = name_prefix
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'ethernet_adapter_policies'

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
            print(f'  This wizard will save the configuraton for this section to the following file:')
            print(f'  - Intersight/{org}/{self.type}/{templateVars["template_type"]}.auto.tfvars')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure a {policy_type}?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                policy_loop = False
                while policy_loop == False:

                    templateVars["multi_select"] = False
                    jsonVars = easy_jsonData['policies']['vnic.EthNetworkPolicy']
                    templateVars["var_description"] = jsonVars['templates']['description']
                    templateVars["jsonVars"] = sorted(jsonVars['templates']['enum'])
                    templateVars["defaultVar"] = jsonVars['templates']['default']
                    templateVars["varType"] = 'Ethernet Adapter Template'
                    templateVars["policy_template"] = variablesFromAPI(**templateVars)

                    if not templateVars["name_prefix"] == '':
                        name = '%s_%s' % (templateVars["name_prefix"], templateVars["policy_template"])
                    else:
                        name = '%s_%s' % (templateVars["org"], templateVars["policy_template"])

                    templateVars["name"] = policy_name(name, templateVars["policy_type"])
                    templateVars["descr"] = policy_descr(templateVars["name"], templateVars["policy_type"])

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'   adapter_template = "{templateVars["policy_template"]}"')
                    print(f'   description      = "{templateVars["descr"]}"')
                    print(f'   name             = "{templateVars["name"]}"')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
                        if confirm_policy == 'Y' or confirm_policy == '':
                            confirm_policy = 'Y'

                            # Write Policies to Template File
                            templateVars["template_file"] = '%s.jinja2' % ('ethernet_adapter_templates')
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

    #========================================
    # Ethernet Network Control Policy Module
    #========================================
    def ethernet_network_control_policies(self, jsonData, easy_jsonData):
        name_prefix = self.name_prefix
        name_suffix = 'netwk_ctrl'
        org = self.org
        policy_type = 'Ethernet Network Control Policy'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'ethernet_network_control_policies'

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  An {policy_type} will allow you to control Network Discovery with ')
            print(f'  protocols like CDP and LLDP as well as MAC Address Control Features.\n')
            print(f'  This wizard will save the configuraton for this section to the following file:')
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
                templateVars["action_on_uplink_fail"] = 'linkDown'

                valid = False
                while valid == False:
                    cdp = input('Do you want to enable CDP (Cisco Discovery Protocol) for this Policy?  Enter "Y" or "N" [Y]: ')
                    if cdp == '' or cdp == 'Y':
                        templateVars["cdp_enable"] = True
                        valid = True
                    elif cdp == 'N':
                        templateVars["cdp_enable"] = False
                        valid = True
                    else:
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        print(f'  Error!! Invalid Option.  Please enter "Y" or "N".')
                        print(f'\n-------------------------------------------------------------------------------------------\n')

                valid = False
                while valid == False:
                    cdp = input('Do you want to enable LLDP (Link Level Discovery Protocol) for this Policy?  Enter "Y" or "N" [Y]: ')
                    if cdp == '' or cdp == 'Y':
                        templateVars["lldp_receive_enable"] = True
                        templateVars["lldp_transmit_enable"] = True
                        valid = True
                    elif cdp == 'N':
                        templateVars["lldp_receive_enable"] = False
                        templateVars["lldp_transmit_enable"] = False
                        valid = True
                    else:
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        print(f'  Error!! Invalid Option.  Please enter "Y" or "N".')
                        print(f'\n-------------------------------------------------------------------------------------------\n')

                templateVars["multi_select"] = False
                jsonVars = jsonData['components']['schemas']['fabric.EthNetworkControlPolicy']['allOf'][1]['properties']
                templateVars["var_description"] = jsonVars['MacRegistrationMode']['description']
                templateVars["jsonVars"] = sorted(jsonVars['MacRegistrationMode']['enum'])
                templateVars["defaultVar"] = jsonVars['MacRegistrationMode']['default']
                templateVars["varType"] = 'MAC Registration Mode'
                templateVars["mac_register_mode"] = variablesFromAPI(**templateVars)

                templateVars["var_description"] = jsonVars['ForgeMac']['description']
                templateVars["jsonVars"] = sorted(jsonVars['ForgeMac']['enum'])
                templateVars["defaultVar"] = jsonVars['ForgeMac']['default']
                templateVars["varType"] = 'MAC Security Forge'
                templateVars["mac_security_forge"] = variablesFromAPI(**templateVars)

                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'    action_on_uplink_fail = "{templateVars["action_on_uplink_fail"]}"')
                print(f'    cdp_enable            = {templateVars["cdp_enable"]}')
                print(f'    description           = "{templateVars["descr"]}"')
                print(f'    lldp_enable_receive   = {templateVars["lldp_receive_enable"]}')
                print(f'    lldp_enable_transmit  = {templateVars["lldp_transmit_enable"]}')
                print(f'    mac_register_mode     = "{templateVars["mac_register_mode"]}"')
                print(f'    mac_security_forge    = "{templateVars["mac_security_forge"]}"')
                print(f'    name                  = "{templateVars["name"]}"')
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

    #========================================
    # Ethernet Network Group Policy Module
    #========================================
    def ethernet_network_group_policies(self, jsonData, easy_jsonData):
        name_prefix = self.name_prefix
        name_suffix = ['Management', 'Migration', 'Storage', 'VMs']
        org = self.org
        policy_type = 'Ethernet Network Group Policy'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'ethernet_network_group_policies'

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  An {policy_type} will define the Allowed VLANs on a Server vNIC Template.')
            print(f'  As a recommendation you will need an {policy_type} per vNIC Grouping.')
            print(f'  For Instance with a Virtual Host that may have the following vNIC Pairs:')
            print(f'     1. Management')
            print(f'     2. Migration/vMotion')
            print(f'     3. Storage')
            print(f'     4. Virtual Machines')
            print(f'  You will want to configure 1 {policy_type} per Group.')
            print(f'  The allowed vlan list can be in the format of:')
            print(f'     5 - Single VLAN')
            print(f'     1-10 - Range of VLANs')
            print(f'     1,2,3,4,5,11,12,13,14,15 - List of VLANs')
            print(f'     1-10,20-30 - Ranges and Lists of VLANs')
            print(f'  If you want to Assign a Native VLAN Make sure it is in the allowed list.\n')
            print(f'  This wizard will save the configuraton for this section to the following file:')
            print(f'  - Intersight/{org}/{self.type}/{templateVars["template_type"]}.auto.tfvars')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            loop_count = 0
            policy_loop = False
            while policy_loop == False:

                name = ''
                for i, v in enumerate(name_suffix):
                    if int(loop_count) == i:
                        if not name_prefix == '':
                            name = '%s_%s' % (name_prefix, v)
                        else:
                            name = '%s_%s' % (org, v)
                if name == '':
                    name = '%s_%s' % (org, 'vlan_group')

                templateVars["name"] = policy_name(name, policy_type)
                templateVars["descr"] = policy_descr(templateVars["name"], policy_type)
                templateVars["action_on_uplink_fail"] = 'linkDown'

                valid = False
                while valid == False:
                    VlanList = input('Enter the VLAN or List of VLANs to add to this VLAN Group: ')
                    if not VlanList == '':
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
                        vlanListExpanded = vlan_list_full(VlanList)
                        valid_vlan = True
                        vlans_not_in_domain_policy = []
                        for vlan in vlanListExpanded:
                            valid_vlan = validating.number_in_range('VLAN ID', vlan, 1, 4094)
                            if valid_vlan == False:
                                break
                            else:
                                vlan_count = 0
                                for vlans in vlan_list:
                                    if int(vlan) == int(vlans):
                                        vlan_count += 1
                                        break
                                if vlan_count == 0:
                                    vlans_not_in_domain_policy.append(vlans)


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

                templateVars["allowed_vlans"] = VlanList
                if not nativeVlan == '':
                    templateVars["native_vlan"] = nativeVlan
                else:
                    templateVars["native_vlan"] = ''
                    templateVars.pop('native_vlan')

                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'    allowed_vlans = "{templateVars["allowed_vlans"]}"')
                print(f'    description   = "{templateVars["descr"]}"')
                print(f'    name          = "{templateVars["name"]}"')
                if not nativeVlan == '':
                    print(f'    native_vlan   = {templateVars["native_vlan"]}')
                print(f'\n-------------------------------------------------------------------------------------------\n')
                valid_confirm = False
                while valid_confirm == False:
                    confirm_policy = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                    if confirm_policy == 'Y' or confirm_policy == '':
                        confirm_policy = 'Y'

                        # Write Policies to Template File
                        templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
                        write_to_template(self, **templateVars)

                        valid_exit = False
                        while valid_exit == False:
                            if loop_count < 3:
                                exit_answer = input(f'Would You like to Configure another {policy_type}?  Enter "Y" or "N" [Y]: ')
                            else:
                                exit_answer = input(f'Would You like to Configure another {policy_type}?  Enter "Y" or "N" [N]: ')
                            if (loop_count < 3 and exit_answer == '') or exit_answer == 'Y':
                                loop_count += 1
                                valid_exit = True
                            elif (loop_count > 2 and exit_answer == '') or exit_answer == 'N':
                                policy_loop = True
                                configure_loop = True
                                valid_exit = True
                            else:
                                print(f'\n------------------------------------------------------\n')
                                print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                                print(f'\n------------------------------------------------------\n')
                        valid_confirm = True

                    elif confirm_policy == 'N':
                        print(f'\n------------------------------------------------------\n')
                        print(f'  Starting {policy_type} Section over.')
                        print(f'\n------------------------------------------------------\n')
                        valid_confirm = True
                    else:
                        print(f'\n------------------------------------------------------\n')
                        print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                        print(f'\n------------------------------------------------------\n')

        # Close the Template file
        templateVars["template_file"] = 'template_close.jinja2'
        write_to_template(self, **templateVars)

    #========================================
    # Ethernet Network Policy Module
    #========================================
    def ethernet_network_policies(self, jsonData, easy_jsonData):
        name_prefix = self.name_prefix
        name_suffix = 'network'
        org = self.org
        policy_type = 'Ethernet Network Policy'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'ethernet_network_policies'

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  An {policy_type} determines if the port can carry single VLAN (Access) ')
            print(f'  or multiple VLANs (Trunk) traffic. You can specify the VLAN to be associated with an ')
            print(f'  Ethernet packet if no tag is found.\n\n')
            print(f'  This wizard will save the configuraton for this section to the following file:')
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

                    templateVars["multi_select"] = False
                    jsonVars = jsonData['components']['schemas']['vnic.VlanSettings']['allOf'][1]['properties']
                    templateVars["var_description"] = jsonVars['Mode']['description']
                    templateVars["jsonVars"] = sorted(jsonVars['Mode']['enum'])
                    templateVars["defaultVar"] = jsonVars['Mode']['default']
                    templateVars["varType"] = 'VLAN Mode'
                    templateVars["vlan_mode"] = variablesFromAPI(**templateVars)

                    valid = False
                    while valid == False:
                        templateVars["default_vlan"] = input('What is the default vlan to assign to this Policy.  Range is 0 to 4094: ')
                        if re.fullmatch(r'[0-9]{1,4}', templateVars["default_vlan"]):
                            valid = validating.number_in_range('VLAN ID', templateVars["default_vlan"], 0, 4094)

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'    default_vlan  = {templateVars["default_vlan"]}')
                    print(f'    description   = "{templateVars["descr"]}"')
                    print(f'    name          = "{templateVars["name"]}"')
                    print(f'    vlan_mode     = "{templateVars["vlan_mode"]}"')
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

    #========================================
    # Ethernet QoS Policy Module
    #========================================
    def ethernet_qos_policies(self, jsonData, easy_jsonData):
        name_prefix = self.name_prefix
        name_suffix = ['Management', 'Migration', 'Storage', 'VMs']
        org = self.org
        policy_type = 'Ethernet QoS Policy'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'ethernet_qos_policies'

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  An {policy_type} will configure QoS on a Server vNIC Template.')
            print(f'  As a recommendation you will need an {policy_type} per vNIC Group.')
            print(f'  For Instance with a Virtual Host that may have the following vNIC Groups:')
            print(f'     1. Management')
            print(f'     2. Migration/vMotion')
            print(f'     3. Storage')
            print(f'     4. Virtual Machines')
            print(f'  It would be a good practice to configure different QoS Priorities for Each vNIC Group.')
            print(f'  For Instance a good practice would be something like the following:')
            print(f'     Management - Silver')
            print(f'     Migration/vMotion - Bronze')
            print(f'     Storage - Platinum')
            print(f'     Virtual Machines - Gold.\n')
            print(f'  This wizard will save the configuraton for this section to the following file:')
            print(f'  - Intersight/{org}/{self.type}/{templateVars["template_type"]}.auto.tfvars')
            print(f'\n-------------------------------------------------------------------------------------------\n')

            templateVars["multi_select"] = False
            jsonVars = jsonData['components']['schemas']['vnic.EthNetworkPolicy']['allOf'][1]['properties']
            templateVars["var_description"] = jsonVars['TargetPlatform']['description']
            templateVars["jsonVars"] = sorted(jsonVars['TargetPlatform']['enum'])
            templateVars["defaultVar"] = jsonVars['TargetPlatform']['default']
            templateVars["varType"] = 'Target Platform'
            templateVars["target_platform"] = variablesFromAPI(**templateVars)

            loop_count = 0
            policy_loop = False
            while policy_loop == False:

                name = ''
                if templateVars["target_platform"] == 'FIAttached':
                    for i, v in enumerate(name_suffix):
                        if int(loop_count) == i:
                            if not name_prefix == '':
                                name = '%s_%s' % (name_prefix, v)
                            else:
                                name = '%s_%s' % (org, v)
                else:
                    if not name_prefix == '':
                        name = '%s_%s' % (name_prefix, 'qos')

                if name == '':
                    name = '%s_%s' % (org, 'qos')

                templateVars["name"] = policy_name(name, policy_type)
                templateVars["descr"] = policy_descr(templateVars["name"], policy_type)

                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'    Enable Trust Host CoS enables the VIC to Pass thru the CoS value recieved from the Host.')
                print(f'\n-------------------------------------------------------------------------------------------\n')
                valid = False
                while valid == False:
                    question = input(f'Do you want to Enable Trust Host based CoS?  Enter "Y" or "N" [N]: ')
                    if question == '' or question == 'N':
                        templateVars["enable_trust_host_cos"] = False
                        valid = True
                    elif question == 'Y':
                        templateVars["enable_trust_host_cos"] = True
                        valid = True
                    else:
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                        print(f'\n-------------------------------------------------------------------------------------------\n')

                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'    The value in Mbps (0-100000) to use for limiting the data rate on the virtual interface. ')
                print(f'    Setting this to zero will turn rate limiting off.')
                print(f'\n-------------------------------------------------------------------------------------------\n')
                valid = False
                while valid == False:
                    Question = input('What is the Rate Limit you want to assign to the Policy?  [0]: ')
                    if Question == '':
                        Question = 0
                    if re.fullmatch(r'^[0-9]{1,6}$', str(Question)):
                        minValue = 0
                        maxValue = 100000
                        templateVars["varName"] = 'Rate Limit'
                        varValue = Question
                        valid = validating.number_in_range(templateVars["varName"], varValue, minValue, maxValue)
                    else:
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        print(f'    Invalid Rate Limit value "{Question}"!!!')
                        print(f'    The valid range is between 0 and 100000. The default value is 0.')
                        print(f'\n-------------------------------------------------------------------------------------------\n')

                templateVars["rate_limit"] = Question

                if templateVars["target_platform"] == 'Standalone':
                    templateVars["burst"] = 1024
                    templateVars["priority"] = 'Best Effort'
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'    The Class of Service to be associated to the traffic on the virtual interface.')
                    print(f'    The valid range is between 0 and 6. The default value is 0.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid = False
                    while valid == False:
                        Question = input('What is the Class of Service you want to assign to the Policy?  [0]: ')
                        if Question == '':
                            Question = 0
                        if re.fullmatch(r'^[0-6]$', str(Question)):
                            minValue = 0
                            maxValue = 6
                            templateVars["varName"] = 'Class of Service'
                            varValue = Question
                            valid = validating.number_in_range(templateVars["varName"], varValue, minValue, maxValue)
                        else:
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            print(f'    Invalid Class of Service value "{Question}"!!!')
                            print(f'    The valid range is between 0 and 6. The default value is 0.')
                            print(f'\n-------------------------------------------------------------------------------------------\n')

                    templateVars["cos"] = Question

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'    The Maximum Transmission Unit (MTU) or packet size that the virtual interface accepts.')
                    print(f'    The valid range is between 1500 and 9000. The default value is 1500.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid = False
                    while valid == False:
                        Question = input('What is the MTU you want to assign to the Policy?  [1500]: ')
                        if Question == '':
                            Question = 1500
                        if re.fullmatch(r'^[0-9]{4}$', str(Question)):
                            minValue = 1500
                            maxValue = 9000
                            templateVars["varName"] = 'MTU'
                            varValue = Question
                            valid = validating.number_in_range(templateVars["varName"], varValue, minValue, maxValue)
                        else:
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            print(f'    Invalid MTU value "{Question}"!!!')
                            print(f'    The valid range is between 1500 and 9000. The default value is 1500.')
                            print(f'\n-------------------------------------------------------------------------------------------\n')

                    templateVars["mtu"] = Question

                else:
                    templateVars["cos"] = 0
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'    The burst traffic allowed on the vNIC in bytes.')
                    print(f'    The valid range is between 1024 and 1000000. The default value is 1024.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid = False
                    while valid == False:
                        Question = input('What is the Burst Rate you want to assign to the Policy?  [1024]: ')
                        if Question == '':
                            Question = 1024
                        if re.fullmatch(r'^[0-9]{4,7}$', str(Question)):
                            minValue = 1024
                            maxValue = 1000000
                            templateVars["varName"] = 'Burst'
                            varValue = Question
                            valid = validating.number_in_range(templateVars["varName"], varValue, minValue, maxValue)
                        else:
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            print(f'    Invalid Burst value "{Question}"!!!')
                            print(f'    The valid range is between 1024 and 1000000. The default value is 1024.')
                            print(f'\n-------------------------------------------------------------------------------------------\n')

                    templateVars["burst"] = Question

                    templateVars["multi_select"] = False
                    jsonVars = jsonData['components']['schemas']['vnic.EthQosPolicy']['allOf'][1]['properties']
                    templateVars["var_description"] = jsonVars['Priority']['description']
                    templateVars["jsonVars"] = sorted(jsonVars['Priority']['enum'])
                    templateVars["defaultVar"] = jsonVars['Priority']['default']
                    templateVars["varType"] = '%s QoS Priority' % (templateVars["name"])
                    templateVars["priority"] = variablesFromAPI(**templateVars)

                    if loop_count == 0:
                        if templateVars["target_platform"] == 'FIAttached':
                            policy_list = [
                                'policies.system_qos_policies.system_qos_policy',
                            ]
                            templateVars["allow_opt_out"] = False
                            for policy in policy_list:
                                system_qos_policy,policyData = policy_select_loop(jsonData, easy_jsonData, name_prefix, policy, **templateVars)

                    mtu = policyData['system_qos_policies'][0][system_qos_policy][0]['classes'][0][templateVars["priority"]][0]['mtu']
                    if mtu > 8999:
                        templateVars["mtu"] = mtu
                    else:
                        templateVars["mtu"] = mtu

                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'  ')
                if templateVars["target_platform"] == 'FIAttached':
                    print(f'   burst                 = {templateVars["burst"]}')
                if templateVars["target_platform"] == 'Standalone':
                    print(f'   cos                   = {templateVars["cos"]}')
                print(f'   description           = "{templateVars["descr"]}"')
                print(f'   enable_trust_host_cos = {templateVars["enable_trust_host_cos"]}')
                print(f'   mtu                   = {templateVars["mtu"]}')
                print(f'   name                  = "{templateVars["name"]}"')
                if templateVars["target_platform"] == 'FIAttached':
                    print(f'   priority              = "{templateVars["priority"]}"')
                print(f'   rate_limit            = {templateVars["rate_limit"]}')
                print(f'\n-------------------------------------------------------------------------------------------\n')
                valid_confirm = False
                while valid_confirm == False:
                    confirm_policy = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
                    if confirm_policy == 'Y' or confirm_policy == '':
                        confirm_policy = 'Y'

                        # Write Policies to Template File
                        templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
                        write_to_template(self, **templateVars)

                        valid_exit = False
                        while valid_exit == False:
                            if loop_count < 3 and templateVars["target_platform"] == 'FIAttached':
                                exit_answer = input(f'Would You like to Configure another {policy_type}?  Enter "Y" or "N" [Y]: ')
                            else:
                                exit_answer = input(f'Would You like to Configure another {policy_type}?  Enter "Y" or "N" [N]: ')
                            if loop_count < 3 and exit_answer == '' and templateVars["target_platform"] == 'FIAttached':
                                loop_count += 1
                                valid_exit = True
                            elif exit_answer == 'Y':
                                loop_count += 1
                                valid_exit = True
                            elif (exit_answer == '') or exit_answer == 'N':
                                policy_loop = True
                                configure_loop = True
                                valid_exit = True
                            else:
                                print(f'\n------------------------------------------------------\n')
                                print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                                print(f'\n------------------------------------------------------\n')
                        valid_confirm = True

                    elif confirm_policy == 'N':
                        print(f'\n------------------------------------------------------\n')
                        print(f'  Starting {policy_type} Section over.')
                        print(f'\n------------------------------------------------------\n')
                        valid_confirm = True
                    else:
                        print(f'\n------------------------------------------------------\n')
                        print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                        print(f'\n------------------------------------------------------\n')

        # Close the Template file
        templateVars["template_file"] = 'template_close.jinja2'
        write_to_template(self, **templateVars)

    #========================================
    # Fibre-Channel Adapter Policy Module
    #========================================
    def fibre_channel_adapter_policies(self, jsonData, easy_jsonData):
        name_prefix = self.name_prefix
        org = self.org
        policy_type = 'Fibre-Channel Adapter Policy'
        policy_x = 'Fibre-Channel Adapter'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["name_prefix"] = name_prefix
        templateVars["org"] = org
        templateVars["policy_file"] = 'fibre_channel_adapter_templates.txt'
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'fibre_channel_adapter_policies'

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  You can Skip this policy if you are not configuring Fibre-Channel.\n')
            print(f'  {policy_x} Policies:  To simplify your work, this wizard will use {policy_x}')
            print(f'  Templates that are pre-configured.  You can add custom {policy_x} policy')
            print(f'  configuration to the {templateVars["template_type"]}.auto.tfvars file at your descretion.  ')
            print(f'  That will not be covered by this wizard as the focus of the wizard is on simplicity.\n')
            print(f'  This wizard will save the configuraton for this section to the following file:')
            print(f'  - Intersight/{org}/{self.type}/{templateVars["template_type"]}.auto.tfvars')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure a {policy_type}?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                policy_loop = False
                while policy_loop == False:

                    templateVars["multi_select"] = False
                    jsonVars = easy_jsonData['policies']['vnic.FcNetworkPolicy']
                    templateVars["var_description"] = jsonVars['templates']['description']
                    templateVars["jsonVars"] = sorted(jsonVars['templates']['enum'])
                    templateVars["defaultVar"] = jsonVars['templates']['default']
                    templateVars["varType"] = 'Fibre Channel Adapter Template'
                    templateVars["policy_template"] = variablesFromAPI(**templateVars)

                    if not templateVars["name_prefix"] == '':
                        name = '%s_%s' % (templateVars["name_prefix"], templateVars["policy_template"])
                    else:
                        name = '%s_%s' % (templateVars["org"], templateVars["policy_template"])

                    templateVars["name"] = policy_name(name, templateVars["policy_type"])
                    templateVars["descr"] = policy_descr(templateVars["name"], templateVars["policy_type"])

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'   adapter_template = "{templateVars["policy_template"]}"')
                    print(f'   description      = "{templateVars["descr"]}"')
                    print(f'   name             = "{templateVars["name"]}"')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
                        if confirm_policy == 'Y' or confirm_policy == '':
                            confirm_policy = 'Y'

                            # Write Policies to Template File
                            templateVars["template_file"] = '%s.jinja2' % ('ethernet_adapter_templates')
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

    #========================================
    # Fibre-Channel Network Policy Module
    #========================================
    def fibre_channel_network_policies(self, jsonData, easy_jsonData):
        name_prefix = self.name_prefix
        org = self.org
        policy_type = 'Fibre-Channel Network Policy'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'fibre_channel_network_policies'

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  You can Skip this policy if you are not configuring Fibre-Channel.\n')
            print(f'  Fibre-Channel Network Policies Notes:')
            print(f'  - You will need one Policy per Fabric.  VSAN A and VSAN B.\n')
            print(f'  This wizard will save the configuraton for this section to the following file:')
            print(f'  - Intersight/{org}/{self.type}/{templateVars["template_type"]}.auto.tfvars')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure a {policy_type}?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                loop_count = 0
                policy_loop = False
                while policy_loop == False:

                    name = naming_rule_fabric(loop_count, name_prefix, org)

                    templateVars["name"] = policy_name(name, policy_type)
                    templateVars["descr"] = policy_descr(templateVars["name"], policy_type)

                    templateVars["multi_select"] = False
                    jsonVars = jsonData['components']['schemas']['server.BaseProfile']['allOf'][1]['properties']
                    templateVars["var_description"] = jsonVars['TargetPlatform']['description']
                    templateVars["jsonVars"] = sorted(jsonVars['TargetPlatform']['enum'])
                    templateVars["defaultVar"] = jsonVars['TargetPlatform']['default']
                    templateVars["varType"] = 'Target Platform'
                    templateVars["target_platform"] = variablesFromAPI(**templateVars)

                    if templateVars["target_platform"] == 'Standalone':
                        valid = False
                        while valid == False:
                            templateVars["default_vlan"] = input('What is the Default VLAN you want to Assign to this Policy? ')
                            valid = validating.number_in_range('Default VLAN', templateVars["default_vlan"], 1, 4094)
                    else:
                        templateVars["default_vlan"] = 0

                    valid = False
                    while valid == False:
                        if loop_count % 2 == 0:
                            templateVars["vsan_id"] = input('What VSAN Do you want to Assign to this Policy?  [100]: ')
                        else:
                            templateVars["vsan_id"] = input('What VSAN Do you want to Assign to this Policy?  [200]: ')
                        if templateVars["vsan_id"] == '':
                            if loop_count % 2 == 0:
                                templateVars["vsan_id"] = 100
                            else:
                                templateVars["vsan_id"] = 200
                        vsan_valid = validating.number_in_range('VSAN ID', templateVars["vsan_id"], 1, 4094)
                        if vsan_valid == True:
                            if templateVars["target_platform"] == 'FIAttached':
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

                                vsan_string = ''
                                for vsan in vsan_list:
                                    vsan_string = vsan_string + ',' + str(vsan)
                                vsan_list = vlan_list_full(vsan_string)
                                vsan_count = 0
                                for vsan in vsan_list:
                                    if int(templateVars["vsan_id"]) == int(vsan):
                                        vsan_count = 1
                                        break
                                if vsan_count == 0:
                                    print(f'\n-------------------------------------------------------------------------------------------\n')
                                    print(f'  Error with VSAN!!  The VSAN {templateVars["vsan_id"]} is not in the VSAN Policy')
                                    print(f'  {vsan_policy}.  Options are {vsan_list}.')
                                    print(f'\n-------------------------------------------------------------------------------------------\n')
                                else:
                                    valid = True

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    if templateVars["target_platform"] == 'Standalone':
                        print(f'   default_vlan = "{templateVars["default_vlan"]}"')
                    print(f'   description  = "{templateVars["descr"]}"')
                    print(f'   name         = "{templateVars["name"]}"')
                    print(f'   vsan_id      = "{templateVars["vsan_id"]}"')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                        if confirm_policy == 'Y' or confirm_policy == '':
                            confirm_policy = 'Y'

                            # Write Policies to Template File
                            templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
                            write_to_template(self, **templateVars)

                            configure_loop, loop_count, policy_loop = exit_loop_default_yes(loop_count, policy_type)
                            valid_confirm = True

                        elif confirm_policy == 'N':
                            print(f'\n------------------------------------------------------\n')
                            print(f'  Starting {policy_type} Section over.')
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

    #========================================
    # Fibre-Channel QoS Policy Module
    #========================================
    def fibre_channel_qos_policies(self, jsonData, easy_jsonData):
        name_prefix = self.name_prefix
        name_suffix = 'qos'
        org = self.org
        policy_type = 'Fibre-Channel QoS Policy'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'fibre_channel_qos_policies'

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  You can Skip this policy if you are not configuring Fibre-Channel.\n')
            print(f'  It is a good practice to apply a {policy_type} to the vHBAs.  This wizard')
            print(f'  creates the policy with all the default values, so you only need one')
            print(f'  {policy_type}.\n')
            print(f'  This wizard will save the configuraton for this section to the following file:')
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
                    templateVars["burst"] = 1024
                    templateVars["max_data_field_size"] = 2112
                    templateVars["rate_limit"] = 0

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'    burst               = "{templateVars["burst"]}"')
                    print(f'    description         = "{templateVars["descr"]}"')
                    print(f'    max_data_field_size = "{templateVars["max_data_field_size"]}"')
                    print(f'    name                = "{templateVars["name"]}"')
                    print(f'    rate_limit          = "{templateVars["rate_limit"]}"')
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

    #========================================
    # Firmware - UCS Domain Module
    #========================================
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

    #========================================
    # Flow Control Policy Module
    #========================================
    def flow_control_policies(self, jsonData, easy_jsonData):
        name_prefix = self.name_prefix
        name_suffix = 'flow_ctrl'
        org = self.org
        policy_type = 'Flow Control Policy'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'flow_control_policies'

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
            print(f'  This wizard will save the configuraton for this section to the following file:')
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

                templateVars["priority"] = 'auto'
                templateVars["receive"] = 'Enabled'
                templateVars["send"] = 'Enabled'

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

    #========================================
    # IMC Access Policy Module
    #========================================
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
            print(f'  This wizard will save the configuraton for this section to the following file:')
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

    #========================================
    # IP Pools Module
    #========================================
    def ip_pools(self, jsonData, easy_jsonData):
        name_prefix = self.name_prefix
        name_suffix = 'ip_pool'
        org = self.org
        policy_type = 'IP Pool'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'ip_pools'

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  At a minimum you will need one IP Pool for KVM Access to Servers.  Currently out-of-band')
            print(f'  management is not supported for KVM access.  This IP Pool will need to be associated to a ')
            print(f'  VLAN assigned to the VLAN Pool of the Domain.\n')
            print(f'  This wizard will save the configuraton for this section to the following file:')
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

                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'  Assignment order decides the order in which the next identifier is allocated.')
                print(f'    1. default - (Intersight Default) Assignment order is decided by the system.')
                print(f'    2. sequential - (Recommended) Identifiers are assigned in a sequential order.')
                print(f'\n-------------------------------------------------------------------------------------------\n')
                valid = False
                while valid == False:
                    templateVars["assignment_order"] = input('Specify the number for the value to select.  [2]: ')
                    if templateVars["assignment_order"] == '' or templateVars["assignment_order"] == '2':
                        templateVars["assignment_order"] = 'sequential'
                        valid = True
                    elif templateVars["assignment_order"] == '1':
                        templateVars["assignment_order"] = 'default'
                        valid = True
                    else:
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        print(f'  Error!! Invalid Option.  Please Select a valid option from the List.')
                        print(f'\n-------------------------------------------------------------------------------------------\n')

                valid = False
                while valid == False:
                    config_ipv4 = input('Do you want to configure IPv4 for this Pool?  Enter "Y" or "N" [Y]: ')
                    if config_ipv4 == 'Y' or config_ipv4 == '':
                        valid = True
                    elif config_ipv4 == 'N':
                        valid = True
                    else:
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                        print(f'\n-------------------------------------------------------------------------------------------\n')

                if config_ipv4 == 'Y' or config_ipv4 == '':
                    valid = False
                    while valid == False:
                        network_prefix = input('What is the Gateway/Mask to Assign to the Pool?  [198.18.0.1/24]: ')
                        if network_prefix == '':
                            network_prefix = '198.18.0.1/24'
                        gateway_valid = validating.ip_address('Gateway Address', network_prefix)
                        mask_valid = validating.number_in_range('Mask Length', network_prefix.split('/')[1], 1, 30)
                        if gateway_valid == True and mask_valid == True:
                            valid = True
                        else:
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            print(f'  Error!! Invalid Value.  Please Verify you have entered the gateway/prefix correctly.')
                            print(f'\n-------------------------------------------------------------------------------------------\n')

                    gateway = str(ipaddress.IPv4Interface(network_prefix).ip)
                    netmask = str(ipaddress.IPv4Interface(network_prefix).netmask)
                    network = str(ipaddress.IPv4Interface(network_prefix).network)
                    prefix = network_prefix.split('/')[1]

                    valid = False
                    while valid == False:
                        starting = input('What is the Starting IP Address to Assign to the Pool?  [198.18.0.10]: ')
                        if starting == '':
                            starting = '198.18.0.10'
                        valid_ip = validating.ip_address('Starting IP Address', starting)
                        if valid_ip == True:
                            if network == str(ipaddress.IPv4Interface('/'.join([starting, prefix])).network):
                                valid = True
                            else:
                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                print(f'  Error!! Invalid Value.  Please Verify the starting IP is in the same network')
                                print(f'  as the Gateway')
                                print(f'\n-------------------------------------------------------------------------------------------\n')

                    valid = False
                    while valid == False:
                        pool_size = input('How Many IP Addresses should be added to the Pool?  Range is 1-1000 [160]: ')
                        if pool_size == '':
                            pool_size = '160'
                        valid = validating.number_in_range('Pool Size', pool_size, 1, 1000)

                    valid = False
                    while valid == False:
                        primary_dns = input('What is your Primary DNS Server [208.67.220.220]? ')
                        if primary_dns == '':
                            primary_dns = '208.67.220.220'
                        valid = validating.ip_address('Primary DNS Server', primary_dns)

                    valid = False
                    while valid == False:
                        alternate_true = input('Do you want to Configure an Alternate DNS Server?  Enter "Y" or "N" [Y]: ')
                        if alternate_true == 'Y' or alternate_true == '':
                            secondary_dns = input('What is your Alternate DNS Server [208.67.222.222]? ')
                            if secondary_dns == '':
                                secondary_dns = '208.67.222.222'
                            valid = validating.ip_address('Alternate DNS Server', secondary_dns)
                        elif alternate_true == 'N':
                            secondary_dns = ''
                            valid = True
                        else:
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                            print(f'\n-------------------------------------------------------------------------------------------\n')

                    beginx = int(ipaddress.IPv4Address(starting))
                    add_dec = (beginx + int(pool_size))
                    ending = str(ipaddress.IPv4Address(add_dec))

                    templateVars["ipv4_blocks"] = [{'from':starting, 'to':ending}]
                    templateVars["ipv4_configuration"] = {'gateway':gateway, 'netmask':netmask,
                        'primary_dns':primary_dns, 'secondary_dns':secondary_dns}

                valid = False
                while valid == False:
                    config_ipv6 = input('Do you want to configure IPv6 for this Pool?  Enter "Y" or "N" [N]: ')
                    if config_ipv6 == 'Y':
                        valid = True
                    elif config_ipv6 == 'N' or config_ipv6 == '':
                        valid = True
                    else:
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                        print(f'\n-------------------------------------------------------------------------------------------\n')

                if config_ipv6 == 'Y':
                    valid = False
                    while valid == False:
                        network_prefix = input('What is the Gateway/Mask to Assign to the Pool?  [2001:0002::1/64]: ')
                        if network_prefix == '':
                            network_prefix = '2001:0002::1/64'
                        gateway_valid = validating.ip_address('Gateway Address', network_prefix)
                        mask_valid = validating.number_in_range('Mask Length', network_prefix.split('/')[1], 48, 127)
                        if gateway_valid == True and mask_valid == True:
                            valid = True
                        else:
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            print(f'  Error!! Invalid Value.  Please Verify you have entered the gateway/prefix correctly.')
                            print(f'\n-------------------------------------------------------------------------------------------\n')

                    # broadcast = str(ipaddress.IPv4Interface(network_prefix).broadcast_address)
                    gateway = str(ipaddress.IPv6Interface(network_prefix).ip)
                    network = str(ipaddress.IPv6Interface(network_prefix).network)
                    prefix = network_prefix.split('/')[1]

                    valid = False
                    while valid == False:
                        starting = input('What is the Starting IP Address to Assign to the Pool?  [2001:0002::10]: ')
                        if starting == '':
                            starting = '2001:0002::10'
                        valid_ip = validating.ip_address('Starting IP Address', starting)
                        if valid_ip == True:
                            if network == str(ipaddress.IPv6Interface('/'.join([starting, prefix])).network):
                                valid = True
                                # print('gateway and starting ip are in the same network')
                            else:
                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                print(f'  Error!! Invalid Value.  Please Verify the starting IP is in the same network')
                                print(f'  as the Gateway')
                                print(f'\n-------------------------------------------------------------------------------------------\n')

                    valid = False
                    while valid == False:
                        pool_size = input('How Many IP Addresses should be added to the Pool?  Range is 1-1000 [160]: ')
                        if pool_size == '':
                            pool_size = '160'
                        valid = validating.number_in_range('Pool Size', pool_size, 1, 1000)

                    valid = False
                    while valid == False:
                        primary_dns = input('What is your Primary DNS Server [2620:119:35::35]? ')
                        if primary_dns == '':
                            primary_dns = '2620:119:35::35'
                        valid = validating.ip_address('Primary DNS Server', primary_dns)

                    valid = False
                    while valid == False:
                        alternate_true = input('Do you want to Configure an Alternate DNS Server? Enter "Y" or "N" [Y]: ')
                        if alternate_true == 'Y' or alternate_true == '':
                            secondary_dns = input('What is your Alternate DNS Server [2620:119:53::53]? ')
                            if secondary_dns == '':
                                secondary_dns = '2620:119:53::53'
                            valid = validating.ip_address('Alternate DNS Server', secondary_dns)
                        elif alternate_true == 'N':
                            secondary_dns = ''
                            valid = True
                        else:
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                            print(f'\n-------------------------------------------------------------------------------------------\n')

                    # beginx = int(ipaddress.IPv6Address(starting))
                    # add_dec = (beginx + int(pool_size))
                    # ending = str(ipaddress.IPv6Address(add_dec))

                    templateVars["ipv6_blocks"] = [{'from':starting, 'size':pool_size}]
                    templateVars["ipv6_configuration"] = {'gateway':gateway, 'prefix':prefix,
                        'primary_dns':primary_dns, 'secondary_dns':secondary_dns}

                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'    assignment_order = "{templateVars["assignment_order"]}"')
                print(f'    description      = "{templateVars["descr"]}"')
                print(f'    name             = "{templateVars["name"]}"')
                if config_ipv4 == 'Y' or config_ipv4 == '':
                    print(f'    ipv4_blocks = [')
                    for item in templateVars["ipv4_blocks"]:
                        print('      {')
                        for k, v in item.items():
                            if k == 'from':
                                print(f'        from = "{v}" ')
                            elif k == 'to':
                                print(f'        to   = "{v}"')
                        print('      }')
                    print(f'    ]')
                    print('    ipv4_configuration = {')
                    print('      {')
                    for k, v in templateVars["ipv4_configuration"].items():
                        if k == 'gateway':
                            print(f'        gateway       = "{v}"')
                        elif k == 'netmask':
                            print(f'        netmask       = "{v}"')
                        elif k == 'primary_dns':
                            print(f'        primary_dns   = "{v}"')
                        elif k == 'secondary_dns':
                            print(f'        secondary_dns = "{v}"')
                    print('      }')
                    print('    }')
                if config_ipv6 == 'Y':
                    print(f'    ipv6_blocks = [')
                    for item in templateVars["ipv6_blocks"]:
                        print('      {')
                        for k, v in item.items():
                            if k == 'from':
                                print(f'        from = {v}')
                            elif k == 'size':
                                print(f'        size = {v}')
                        print('      }')
                    print(f'    ]')
                    print('    ipv6_configuration = {')
                    print('      {')
                    for k, v in templateVars["ipv6_configuration"].items():
                        if k == 'gateway':
                            print(f'        gateway       = "{v}"')
                        elif k == 'prefix':
                            print(f'        prefix        = "{v}"')
                        elif k == 'primary_dns':
                            print(f'        primary_dns   = "{v}"')
                        elif k == 'secondary_dns':
                            print(f'        secondary_dns = "{v}"')
                    print('      }')
                    print('    }')
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

    #========================================
    # IPMI over LAN Policy Module
    #========================================
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
            print(f'  This wizard will save the configuraton for this section to the following file:')
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

    #========================================
    # Intersight Module
    #========================================
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

        templateVars["tags"] = '[{ key = "Module", value = "terraform-intersight-easy-imm" }, { key = "Version", value = "'f'{easy_jsonData["version"]}''" }]'

        # Write Policies to Template File
        templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
        write_to_template(self, **templateVars)

    #========================================
    # IQN Pools Module
    #========================================
    def iqn_pools(self, jsonData, easy_jsonData):
        name_prefix = self.name_prefix
        name_suffix = 'iqn_pool'
        org = self.org
        policy_type = 'IQN Pool'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'iqn_pools'

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
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

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  Assignment order decides the order in which the next identifier is allocated.')
                    print(f'    1. default - (Intersight Default) Assignment order is decided by the system.')
                    print(f'    2. sequential - (Recommended) Identifiers are assigned in a sequential order.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid = False
                    while valid == False:
                        templateVars["assignment_order"] = input('Specify the Index for the value to select [2]: ')
                        if templateVars["assignment_order"] == '' or templateVars["assignment_order"] == '2':
                            templateVars["assignment_order"] = 'sequential'
                            valid = True
                        elif templateVars["assignment_order"] == '1':
                            templateVars["assignment_order"] = 'default'
                            valid = True
                        else:
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            print(f'  Error!! Invalid Option.  Please Select a valid option from the List.')
                            print(f'\n-------------------------------------------------------------------------------------------\n')

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  The iSCSI Qualified Name (IQN) format is: iqn.yyyy-mm.naming-authority:unique name, where:')
                    print(f'    - literal iqn (iSCSI Qualified Name) - always iqn')
                    print(f'    - date (yyyy-mm) that the naming authority took ownership of the domain')
                    print(f'    - reversed domain name of the authority (e.g. org.linux, com.example, com.cisco)')
                    print(f'    - unique name is any name you want to use, for example, the name of your host. The naming')
                    print(f'      authority must make sure that any names assigned following the colon are unique, such as:')
                    print(f'        * iqn.1984-12.com.cisco:lnx1')
                    print(f'        * iqn.1984-12.com.cisco:win-server1')
                    print(f'        * iqn.1984-12.com.cisco:win-server1')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid = False
                    while valid == False:
                        templateVars['prefix'] = input(f'\nWhat is the IQN Prefix you would like to assign to the Pool?  [iqn.1984-12.com.cisco]: ')
                        if templateVars['prefix'] == '':
                            templateVars['prefix'] = 'iqn.1984-12.com.cisco'

                        suffix = input(f'\nWhat is the IQN Suffix you would like to assign to the Pool?  [ucs-host]: ')
                        if suffix == '':
                            suffix = 'ucs-host'

                        pool_from = input(f'\nWhat is the first Suffix Number in the Block?  [1]: ')
                        if pool_from == '':
                            pool_from = '1'
                        valid_from = validating.number_in_range('IQN Pool From', pool_from, 1, 1000)

                        pool_size = input(f'\nWhat is the size of the Block?  [512]: ')
                        if pool_size == '':
                            pool_size = '512'
                        valid_size = validating.number_in_range('IQN Pool Size', pool_size, 1, 1000)

                        from_iqn = '%s:%s%s' % (templateVars['prefix'], suffix, pool_from)
                        valid_iqn = validating.iqn_address('IQN Staring Address', from_iqn)

                        if valid_from == True and valid_size == True and valid_iqn == True:
                            valid = True
                    templateVars["iqn_blocks"] = [
                        {
                            'from':pool_from,
                            'size':pool_size,
                            'suffix':suffix
                        }
                    ]
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'    assignment_order = "{templateVars["assignment_order"]}"')
                    print(f'    description      = "{templateVars["descr"]}"')
                    print(f'    name             = "{templateVars["name"]}"')
                    print(f'    prefix           = "{templateVars["prefix"]}"')
                    print(f'    iqn_blocks = [')
                    for i in templateVars["iqn_blocks"]:
                        print(f'      ''{')
                        for k, v in i.items():
                            if k == 'from':
                                print(f'        from   = {v}')
                            elif k == 'size':
                                print(f'        size   = {v}')
                            elif k == 'suffix':
                                print(f'        suffix = "{v}"')
                        print(f'      ''}')
                    print(f'    ]')
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

    #========================================
    # iSCSI Adapter Policy Module
    #========================================
    def iscsi_adapter_policies(self, jsonData, easy_jsonData):
        name_prefix = self.name_prefix
        name_suffix = 'adapter'
        org = self.org
        policy_type = 'iSCSI Adapter Policy'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'iscsi_adapter_policies'

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  The {policy_type} allows you to configure values for TCP Connection Timeout, ')
            print(f'  DHCP Timeout, and the Retry Count if the specified LUN ID is busy.\n')
            print(f'  This wizard will save the configuraton for this section to the following file:')
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

                    # Pull in the Policies for iSCSI Adapter
                    jsonVars = jsonData['components']['schemas']['vnic.IscsiAdapterPolicy']['allOf'][1]['properties']

                    # DHCP Timeout
                    templateVars["Description"] = jsonVars['DhcpTimeout']['description']
                    templateVars["varInput"] = 'Enter the number of seconds after which the DHCP times out.'
                    templateVars["varDefault"] = 60
                    templateVars["varName"] = 'DHCP Timeout'
                    templateVars["minNum"] = jsonVars['DhcpTimeout']['minimum']
                    templateVars["maxNum"] = jsonVars['DhcpTimeout']['maximum']
                    templateVars["dhcp_timeout"] = varNumberLoop(**templateVars)

                    # LUN Busy Retry Count
                    templateVars["Description"] = jsonVars['LunBusyRetryCount']['description']
                    templateVars["varInput"] = 'Enter the number of times connection is to be attempted when the LUN ID is busy.'
                    templateVars["varDefault"] = 15
                    templateVars["varName"] = 'LUN Busy Retry Count'
                    templateVars["minNum"] = jsonVars['LunBusyRetryCount']['minimum']
                    templateVars["maxNum"] = jsonVars['LunBusyRetryCount']['maximum']
                    templateVars["lun_busy_retry_count"] = varNumberLoop(**templateVars)

                    # TCP Connection Timeout
                    templateVars["Description"] = jsonVars['ConnectionTimeOut']['description']
                    templateVars["varInput"] = 'Enter the number of seconds after which the TCP connection times out.'
                    templateVars["varDefault"] = 15
                    templateVars["varName"] = 'TCP Connection Timeout'
                    templateVars["minNum"] = jsonVars['ConnectionTimeOut']['minimum']
                    templateVars["maxNum"] = jsonVars['ConnectionTimeOut']['maximum']
                    templateVars["tcp_connection_timeout"] = varNumberLoop(**templateVars)

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'   dhcp_timeout           = {templateVars["dhcp_timeout"]}')
                    print(f'   description            = "{templateVars["descr"]}"')
                    print(f'   lun_busy_retry_count   = "{templateVars["lun_busy_retry_count"]}"')
                    print(f'   name                   = "{templateVars["name"]}"')
                    print(f'   tcp_connection_timeout = "{templateVars["tcp_connection_timeout"]}"')
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

    #========================================
    # iSCSI Boot Policy Module
    #========================================
    def iscsi_boot_policies(self, jsonData, easy_jsonData):
        name_prefix = self.name_prefix
        name_suffix = 'boot'
        org = self.org
        policy_type = 'iSCSI Boot Policy'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'iscsi_boot_policies'

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  The {policy_type} allows you to initialize the Operating System on FI-attached ')
            print(f'  blade and rack servers from a remote disk across a Storage Area Network. The remote disk, ')
            print(f'  known as the target, is accessed using TCP/IP and iSCSI boot firmware.\n')
            print(f'  This wizard will save the configuraton for this section to the following file:')
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

                    # Pull in the Policies for iSCSI Boot
                    jsonVars = jsonData['components']['schemas']['vnic.IscsiBootPolicy']['allOf'][1]['properties']
                    templateVars["multi_select"] = False

                    # Target Source Type
                    templateVars["var_description"] = jsonVars['TargetSourceType']['description']
                    templateVars["jsonVars"] = sorted(jsonVars['TargetSourceType']['enum'])
                    templateVars["defaultVar"] = jsonVars['TargetSourceType']['default']
                    templateVars["varType"] = 'Target Source Type'
                    templateVars["target_source_type"] = variablesFromAPI(**templateVars)

                    if templateVars["target_source_type"] == 'Auto':
                        Authentication = 'none'
                        templateVars["initiator_ip_source"] = 'DHCP'
                        templateVars["primary_target_policy"] = ''
                        templateVars["secondary_target_policy"] = ''

                        templateVars["Description"] = jsonVars['AutoTargetvendorName']['description']
                        templateVars["varDefault"] = ''
                        templateVars["varInput"] = 'DHCP Vendor ID or IQN:'
                        templateVars["varName"] = 'DHCP Vendor ID or IQN'
                        templateVars["varRegex"] = '^[\\S]+$'
                        templateVars["minLength"] = 1
                        templateVars["maxLength"] = 32
                        templateVars["dhcp_vendor_id_iqn"] = varStringLoop(**templateVars)

                    elif templateVars["target_source_type"] == 'Static':
                        templateVars["optional_message"] = '  !!! Select the Primary Static Target !!!\n'
                        policy_list = [
                            'policies.iscsi_static_target_policies.iscsi_static_target_policy'
                        ]
                        templateVars["allow_opt_out"] = False
                        for policy in policy_list:
                            policy_short = policy.split('.')[2]
                            templateVars["primary_target_policy"],policyData = policy_select_loop(jsonData, easy_jsonData, name_prefix, policy, **templateVars)
                            templateVars.update(policyData)

                        templateVars["optional_message"] = '  !!! Optionally Select the Secondary Static Target or enter 100 for no Secondary !!!\n'
                        policy_list = [
                            'policies.iscsi_static_target_policies.iscsi_static_target_policy'
                        ]
                        templateVars["allow_opt_out"] = True
                        for policy in policy_list:
                            policy_short = policy.split('.')[2]
                            templateVars["secondary_target_policy"],policyData = policy_select_loop(jsonData, easy_jsonData, name_prefix, policy, **templateVars)
                            templateVars.update(policyData)

                        templateVars.pop("optional_message")
                        # Initiator IP Source
                        templateVars["var_description"] = jsonVars['InitiatorIpSource']['description']
                        templateVars["jsonVars"] = sorted(jsonVars['InitiatorIpSource']['enum'])
                        templateVars["defaultVar"] = jsonVars['InitiatorIpSource']['default']
                        templateVars["varType"] = 'Initiator IP Source'
                        templateVars["initiator_ip_source"] = variablesFromAPI(**templateVars)

                        if templateVars["initiator_ip_source"] == 'Pool':
                            templateVars["optional_message"] = '  !!! Initiator IP Pool !!!\n'
                            # Prompt User for the IP Pool
                            policy_list = [
                                'pools.ip_pools.ip_pool'
                            ]
                            templateVars["allow_opt_out"] = False
                            for policy in policy_list:
                                policy_short = policy.split('.')[2]
                                templateVars['ip_pool'],policyData = policy_select_loop(jsonData, easy_jsonData, name_prefix, policy, **templateVars)
                                templateVars.update(policyData)
                            templateVars.pop("optional_message")

                        elif templateVars["initiator_ip_source"] == 'Static':
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            print(jsonVars['InitiatorStaticIpV4Config']['description'])
                            print(f'\n-------------------------------------------------------------------------------------------\n')

                            jsonVars = jsonData['components']['schemas']['ippool.IpV4Config']['allOf'][1]['properties']
                            templateVars["Description"] = 'Static IP address provided for iSCSI Initiator.'
                            templateVars["varDefault"] = ''
                            templateVars["varInput"] = f'IP Address:'
                            templateVars["varName"] = f'IP Address'
                            templateVars["varRegex"] = jsonVars['Gateway']['pattern']
                            templateVars["minLength"] = 5
                            templateVars["maxLength"] = 15
                            ipAddress = varStringLoop(**templateVars)

                            templateVars["Description"] = jsonVars['Netmask']['description']
                            templateVars["varDefault"] = ''
                            templateVars["varInput"] = f'Subnet Mask:'
                            templateVars["varName"] = f'Subnet Mask'
                            templateVars["varRegex"] = jsonVars['Netmask']['pattern']
                            templateVars["minLength"] = 5
                            templateVars["maxLength"] = 15
                            subnetMask = varStringLoop(**templateVars)

                            templateVars["Description"] = jsonVars['Gateway']['description']
                            templateVars["varDefault"] = ''
                            templateVars["varInput"] = f'Default Gateway:'
                            templateVars["varName"] = f'Default Gateway'
                            templateVars["varRegex"] = jsonVars['Gateway']['pattern']
                            templateVars["minLength"] = 5
                            templateVars["maxLength"] = 15
                            defaultGateway = varStringLoop(**templateVars)

                            templateVars["Description"] = jsonVars['PrimaryDns']['description']
                            templateVars["varDefault"] = ''
                            templateVars["varInput"] = f'Primary DNS Server.  [press enter to skip]:'
                            templateVars["varName"] = f'Primary DNS Server'
                            templateVars["varRegex"] = jsonVars['PrimaryDns']['pattern']
                            templateVars["minLength"] = 5
                            templateVars["maxLength"] = 15
                            primaryDns = varStringLoop(**templateVars)

                            templateVars["Description"] = jsonVars['SecondaryDns']['description']
                            templateVars["varDefault"] = ''
                            templateVars["varInput"] = f'Secondary DNS Server.  [press enter to skip]:'
                            templateVars["varName"] = f'Secondary DNS Server'
                            templateVars["varRegex"] = jsonVars['SecondaryDns']['pattern']
                            templateVars["minLength"] = 5
                            templateVars["maxLength"] = 15
                            secondaryDns = varStringLoop(**templateVars)

                            templateVars["initiator_static_ip_v4_config"] = {
                                'ip_address':ipAddress,
                                'subnet_mask':subnetMask,
                                'default_gateway':defaultGateway,
                                'primary_dns':primaryDns,
                                'secondary_dns':secondaryDns,
                            }

                        # Type of Authentication
                        templateVars["var_description"] = 'Select Which Type of Authentication you want to Perform.'
                        templateVars["jsonVars"] = ['chap', 'mutual_chap', 'none']
                        templateVars["defaultVar"] = 'none'
                        templateVars["varType"] = 'Authentication Type'
                        Authentication = variablesFromAPI(**templateVars)

                        if re.search('chap', Authentication):
                            jsonVars = jsonData['components']['schemas']['vnic.IscsiAuthProfile']['allOf'][1]['properties']
                            auth_type = Authentication.replace('_', ' ')
                            auth_type = auth_type.capitalize()

                            templateVars["Description"] = jsonVars['UserId']['description']
                            templateVars["varDefault"] = ''
                            templateVars["varInput"] = f'{auth_type} Username:'
                            templateVars["varName"] = f'{auth_type} Username'
                            templateVars["varRegex"] = jsonVars['UserId']['pattern']
                            templateVars["minLength"] = 1
                            templateVars["maxLength"] = 128
                            user_id = varStringLoop(**templateVars)

                            templateVars["Description"] = jsonVars['Password']['description']
                            templateVars["varDefault"] = ''
                            templateVars["varInput"] = f'{auth_type} Password:'
                            templateVars["varName"] = f'{auth_type} Password'
                            templateVars["varRegex"] = jsonVars['Password']['pattern']
                            templateVars["minLength"] = 12
                            templateVars["maxLength"] = 16
                            iscsi_boot_password = varSensitiveStringLoop(**templateVars)
                            os.environ['TF_VAR_iscsi_boot_password'] = '%s' % (iscsi_boot_password)
                            password = 1

                            templateVars[Authentication] = {
                                'password':password,
                                'user_id':user_id
                            }

                    # Prompt User for the iSCSI Adapter Policy
                    policy_list = [
                        'policies.iscsi_adapter_policies.iscsi_adapter_policy'
                    ]
                    templateVars["allow_opt_out"] = True
                    for policy in policy_list:
                        policy_short = policy.split('.')[2]
                        templateVars[policy_short],policyData = policy_select_loop(jsonData, easy_jsonData, name_prefix, policy, **templateVars)
                        templateVars.update(policyData)


                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    if 'chap' in Authentication:
                        print(f'   authentication      = "Authentication"')
                    print(f'   description         = "{templateVars["descr"]}"')
                    if templateVars["target_source_type"] == 'Auto':
                        print(f'   dhcp_vendor_id_iqn  = "{templateVars["dhcp_vendor_id_iqn"]}"')
                    if templateVars["initiator_ip_source"] == 'Pool':
                        print(f'   initiator_ip_pool   = "{templateVars["ip_pool"]}"')
                    print(f'   initiator_ip_source = "{templateVars["initiator_ip_source"]}"')
                    if templateVars.get('initiator_static_ip_v4_config'):
                        print(f'   initiator_static_ip_v4_config = ''{')
                        print(f'     default_gateway = "{templateVars["initiator_static_ip_v4_config"]["default_gateway"]}"')
                        print(f'     ip_address      = "{templateVars["initiator_static_ip_v4_config"]["ip_address"]}"')
                        print(f'     primary_dns     = "{templateVars["initiator_static_ip_v4_config"]["primary_dns"]}"')
                        print(f'     secondary_dns   = "{templateVars["initiator_static_ip_v4_config"]["secondary_dns"]}"')
                        print(f'     subnet_mask     = "{templateVars["initiator_static_ip_v4_config"]["subnet_mask"]}"')
                        print(f'   ''}')
                    print(f'   iscsi_adapter_policy    = "{templateVars["iscsi_adapter_policy"]}"')
                    print(f'   name                    = "{templateVars["name"]}"')
                    if 'chap' in Authentication:
                        print(f'   password                = {password}')
                    print(f'   primary_target_policy   = "{templateVars["primary_target_policy"]}"')
                    print(f'   secondary_target_policy = "{templateVars["secondary_target_policy"]}"')
                    print(f'   target_source_type      = "{templateVars["target_source_type"]}"')
                    if 'chap' in Authentication:
                        print(f'   username                = {user_id}')
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

    #========================================
    # iSCSI Static Target Policy Module
    #========================================
    def iscsi_static_target_policies(self, jsonData, easy_jsonData):
        name_prefix = self.name_prefix
        name_suffix = 'target'
        org = self.org
        policy_type = 'iSCSI Static Target Policy'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'iscsi_static_target_policies'

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  The {policy_type} allows you to specify the name, IP address, port, and ')
            print(f'  logical unit number of the primary target for iSCSI boot. You can optionally specify these ')
            print(f'  details for a secondary target as well.\n')
            print(f'  This wizard will save the configuraton for this section to the following file:')
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

                    # Pull in the Policies for iSCSI Static Target
                    jsonVars = jsonData['components']['schemas']['vnic.IscsiStaticTargetPolicy']['allOf'][1]['properties']

                    desc_add = '\n  such as:\n  * iqn.1984-12.com.cisco:lnx1\n  * iqn.1984-12.com.cisco:win-server1'
                    # Target Name
                    templateVars["Description"] = jsonVars['TargetName']['description'] + desc_add
                    templateVars["varDefault"] = ''
                    templateVars["varInput"] = 'Enter the name of the target:'
                    templateVars["varName"] = 'Target Name'
                    templateVars["varRegex"] = jsonVars['TargetName']['pattern']
                    templateVars["minLength"] = 1
                    templateVars["maxLength"] = 255
                    templateVars["target_name"] = varStringLoop(**templateVars)

                    # IP Address
                    templateVars["Description"] = jsonVars['IpAddress']['description']
                    templateVars["varDefault"] = ''
                    templateVars["varInput"] = 'Enter the target IP address:'
                    templateVars["varName"] = 'IP Address'
                    templateVars["varRegex"] = jsonVars['IpAddress']['pattern']
                    templateVars["minLength"] = 5
                    templateVars["maxLength"] = 15
                    templateVars["ip_address"] = varStringLoop(**templateVars)

                    # Port
                    templateVars["Description"] = jsonVars['Port']['description']
                    templateVars["varInput"] = 'Enter the port number of the target.'
                    templateVars["varDefault"] = 3260
                    templateVars["varName"] = 'Port'
                    templateVars["minNum"] = jsonVars['Port']['minimum']
                    templateVars["maxNum"] = jsonVars['Port']['maximum']
                    templateVars["port"] = varNumberLoop(**templateVars)

                    # LUN Identifier
                    templateVars["Description"] = jsonVars['Lun']['description']
                    templateVars["varInput"] = 'Enter the ID of the boot logical unit number.'
                    templateVars["varDefault"] = 0
                    templateVars["varName"] = 'LUN Identifier'
                    templateVars["minNum"] = 0
                    templateVars["maxNum"] = 1024
                    templateVars["lun_id"] = varNumberLoop(**templateVars)

                    # LUN Bootable
                    templateVars["Description"] = jsonVars['Lun']['description']
                    templateVars["varInput"] = f'Should LUN {templateVars["lun_id"]} be bootable?'
                    templateVars["varDefault"] = 'Y'
                    templateVars["varName"] = 'LUN Identifier'
                    templateVars["bootable"] = varBoolLoop(**templateVars)

                    templateVars["lun"] = {
                        'bootable':templateVars["bootable"],
                        'lun_id':templateVars["lun_id"]
                    }
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'   description = "{templateVars["descr"]}"')
                    print(f'   ip_address  = "{templateVars["ip_address"]}"')
                    print(f'   name        = "{templateVars["name"]}"')
                    print(f'   port        = {templateVars["port"]}')
                    print(f'   target_name = "{templateVars["target_name"]}"')
                    print(f'   lun = [')
                    print(f'     ''{')
                    print(f'       bootable = {templateVars["lun"]["bootable"]}')
                    print(f'       lun_id   = {templateVars["lun"]["lun_id"]}')
                    print(f'     ''}')
                    print(f'   ]')
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

    #========================================
    # LAN Connectivity Policy Module
    #========================================
    def lan_connectivity_policies(self, jsonData, easy_jsonData):
        name_prefix = self.name_prefix
        name_suffix = ['Management', 'Migration', 'Storage', 'Virtual_Machines']
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
            print(f'  If failover is not configured the Wizard will create a Pair of vNICs.')
            print(f'  For Instance with a Virtual Host that may have the following vNIC Pairs:')
            print(f'     1. Management')
            print(f'     2. Migration/vMotion')
            print(f'     3. Storage')
            print(f'     4. Virtual Machines\n')
            print(f'  This wizard will save the configuraton for this section to the following file:')
            print(f'  - Intersight/{org}/{self.type}/{templateVars["template_type"]}.auto.tfvars')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure a {policy_type}?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                loop_count = 1
                policy_loop = False
                while policy_loop == False:

                    if not name_prefix == '':
                        name = '%s_%s' % (name_prefix, 'lancon')
                    else:
                        name = '%s_%s' % (org, 'lancon')

                    templateVars["name"] = policy_name(name, policy_type)
                    templateVars["descr"] = policy_descr(templateVars["name"], policy_type)

                    templateVars["multi_select"] = False
                    jsonVars = jsonData['components']['schemas']['vnic.LanConnectivityPolicy']['allOf'][1]['properties']

                    templateVars["var_description"] = jsonVars['TargetPlatform']['description']
                    templateVars["jsonVars"] = sorted(jsonVars['TargetPlatform']['enum'])
                    templateVars["defaultVar"] = jsonVars['TargetPlatform']['default']
                    templateVars["varType"] = 'Target Platform'
                    templateVars["target_platform"] = variablesFromAPI(**templateVars)

                    if templateVars["target_platform"] == 'FIAttached':
                        templateVars["Description"] = jsonVars['AzureQosEnabled']['description']
                        templateVars["varInput"] = f'Do you want to Enable AzureStack-Host QoS?'
                        templateVars["varDefault"] = 'N'
                        templateVars["varName"] = 'AzureStack-Host QoS'
                        templateVars["enable_azure_stack_host_qos"] = varBoolLoop(**templateVars)

                        templateVars["var_description"] = jsonVars['IqnAllocationType']['description']
                        templateVars["jsonVars"] = sorted(jsonVars['IqnAllocationType']['enum'])
                        templateVars["defaultVar"] = jsonVars['IqnAllocationType']['default']
                        templateVars["varType"] = 'Iqn Allocation Type'
                        templateVars["iqn_allocation_type"] = variablesFromAPI(**templateVars)

                        if templateVars["iqn_allocation_type"] == 'Pool':
                            templateVars["iqn_static_identifier"] = ''
                            policy_list = [
                                'pools.iqn_pools.iqn_pool',
                            ]
                            templateVars["allow_opt_out"] = False
                            for policy in policy_list:
                                policy_short = policy.split('.')[2]
                                templateVars[policy_short],policyData = policy_select_loop(jsonData, easy_jsonData, name_prefix, policy, **templateVars)
                                templateVars.update(policyData)

                        elif templateVars["iqn_allocation_type"] == 'Static':
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
                                        templateVars["Description"] = jsonVars['StaticIqnName']['description']
                                        templateVars["varDefault"] = ''
                                        templateVars["varInput"] = 'What is the Static IQN you would like to assign to this LAN Policy?'
                                        templateVars["varName"] = 'Static IQN'
                                        templateVars["varRegex"] = jsonVars['StaticIqnName']['pattern']
                                        templateVars["minLength"] = 4
                                        templateVars["maxLength"] = 128
                                        templateVars["iqn_static_identifier"] = varStringLoop(**templateVars)

                        templateVars["var_description"] = jsonVars['PlacementMode']['description']
                        templateVars["jsonVars"] = sorted(jsonVars['PlacementMode']['enum'])
                        templateVars["defaultVar"] = jsonVars['PlacementMode']['default']
                        templateVars["varType"] = 'Placement Mode'
                        templateVars["vnic_placement_mode"] = variablesFromAPI(**templateVars)

                    else:
                        templateVars["iqn_allocation_type"] = 'None'

                    global_name = templateVars["name"]
                    print(f'\n-----------------------------------------------------------------------------------------------\n')
                    print(f'Easy IMM will now begin the vNIC Configuration Process.  We recommend the following guidlines:')
                    print(f'  - For Baremetal Operating Systems like Linux and Windows; use a Failover Policy with a single vnic')
                    print(f'  - For a Virtual Environment it is a Good Practice to not use Failover and use the following')
                    print(f'    vnic layout:')
                    print(f'    1. Management')
                    print(f'    2. Migration/vMotion')
                    print(f'    3. Storage')
                    print(f'    4. Virtual Machines')
                    print(f'If you select no for Failover Policy the script will create mirroring vnics for A and B')
                    print(f'\n-----------------------------------------------------------------------------------------------\n')
                    inner_loop_count = 1
                    pci_order_consumed = [{0:[]},{1:[]}]
                    templateVars["vnics"] = []
                    vnic_loop = False
                    while vnic_loop == False:
                        jsonVars = jsonData['components']['schemas']['vnic.EthIf']['allOf'][1]['properties']

                        templateVars["Description"] = jsonVars['FailoverEnabled']['description']
                        templateVars["varInput"] = f'Do you want to Enable Failover for this vNIC?'
                        templateVars["varDefault"] = 'N'
                        templateVars["varName"] = 'Enable Failover'
                        templateVars["enable_failover"] = varBoolLoop(**templateVars)

                        print(f' inner loop count is {inner_loop_count}')
                        if templateVars["enable_failover"] == True:
                            fabrics = ['A']
                            templateVars["varDefault"] = 'vnic'
                        else:
                            fabrics = ['A','B']
                            if inner_loop_count < 5:
                                numValue = inner_loop_count -1
                                templateVars["varDefault"] = name_suffix[numValue]
                            else:
                                templateVars["varDefault"] = 'vnic'
                        templateVars["Description"] = jsonVars['Name']['description']
                        templateVars["varInput"] = f'What is the name for this vNIC? [{templateVars["varDefault"]}]:'
                        templateVars["varName"] = 'vNIC Name'
                        templateVars["varRegex"] = jsonVars['Name']['pattern']
                        templateVars["minLength"] = 1
                        templateVars["maxLength"] = jsonVars['Name']['maxLength']
                        Name = varStringLoop(**templateVars)
                        for x in fabrics:
                            templateVars[f"name_{x}"] = '%s-%s' % (Name, x)

                        if templateVars["target_platform"] == 'FIAttached':
                            templateVars["var_description"] = jsonVars['MacAddressType']['description']
                            templateVars["jsonVars"] = sorted(jsonVars['MacAddressType']['enum'])
                            templateVars["defaultVar"] = jsonVars['MacAddressType']['default']
                            templateVars["varType"] = 'Mac Address Type'
                            templateVars[f"mac_address_allocation_type"] = variablesFromAPI(**templateVars)

                            if templateVars[f"mac_address_allocation_type"] == 'POOL':
                                for x in fabrics:
                                    templateVars["name"] = templateVars[f"name_{x}"]
                                    policy_list = [
                                        'pools.mac_pools.mac_pool',
                                    ]
                                    templateVars["allow_opt_out"] = False
                                    for policy in policy_list:
                                        templateVars[f"static_mac_{x}"] = ''
                                        if templateVars["enable_failover"] == False:
                                            templateVars["optional_message"] = f'MAC Address Pool for Fabric {x}'
                                        policy_short = policy.split('.')[2]
                                        templateVars[f'mac_pool_{x}'],policyData = policy_select_loop(jsonData, easy_jsonData, name_prefix, policy, **templateVars)
                                        templateVars.update(policyData)
                                    templateVars.pop('optional_message')
                            else:
                                for x in fabrics:
                                    templateVars[f'mac_pool_{x}'] = ''
                                    templateVars["Description"] = jsonVars['StaticMacAddress']['description']
                                    if templateVars["enable_failover"] == True:
                                        templateVars["varInput"] = f'What is the static MAC Address?'
                                    else:
                                        templateVars["varInput"] = f'What is the static MAC Address for Fabric {x}?'
                                    if templateVars["enable_failover"] == True:
                                        templateVars["varName"] = f'Static Mac Address'
                                    else:
                                        templateVars["varName"] = f'Fabric {x} Mac Address'
                                    templateVars["varRegex"] = jsonData['components']['schemas']['boot.Pxe']['allOf'][1]['properties']['MacAddress']['pattern']
                                    templateVars["minLength"] = 17
                                    templateVars["maxLength"] = 17
                                    templateVars[f"static_mac_{x}"] = varStringLoop(**templateVars)

                        # Pull in API Attributes
                        jsonVars = jsonData['components']['schemas']['vnic.PlacementSettings']['allOf'][1]['properties']

                        for x in fabrics:
                            templateVars["var_description"] = jsonVars['PciLink']['description']
                            if templateVars["enable_failover"] == False:
                                templateVars["var_description"] = templateVars["var_description"] + f'\n\nPCI Link For Fabric {x}'
                            templateVars["jsonVars"] = [0, 1]
                            templateVars["defaultVar"] = jsonVars['PciLink']['default']
                            if templateVars["enable_failover"] == True:
                                templateVars["varType"] = 'PCI Link'
                            else:
                                templateVars["varType"] = f'Fabric {x} PCI Link'
                            templateVars[f"pci_link_{x}"] = variablesFromAPI(**templateVars)
                            print(templateVars[f"pci_link_{x}"])

                            if templateVars["target_platform"] == 'Standalone':
                                templateVars["var_description"] = jsonVars['Uplink']['description']
                                templateVars["jsonVars"] = [0, 1, 2, 3]
                                templateVars["defaultVar"] = 0
                                templateVars["varType"] = 'Mac Address Type'
                                templateVars[f"uplink_port_{x}"] = variablesFromAPI(**templateVars)

                        templateVars["var_description"] = jsonVars['Id']['description']
                        templateVars["jsonVars"] = easy_jsonData['policies']['vnic.PlacementSettings']['enum']
                        templateVars["defaultVar"] = easy_jsonData['policies']['vnic.PlacementSettings']['default']
                        templateVars["varType"] = 'Slot ID'
                        templateVars[f"slot_id"] = variablesFromAPI(**templateVars)

                        # Pull in API Attributes
                        jsonVars = jsonData['components']['schemas']['vnic.EthIf']['allOf'][1]['properties']

                        for x in fabrics:
                            valid = False
                            while valid == False:
                                templateVars["Description"] = jsonVars['Order']['description']
                                if templateVars["enable_failover"] == False:
                                    templateVars["varInput"] = f'\nPCI Order For Fabric {x}.'
                                else:
                                    templateVars["varInput"] = f'\nPCI Order.'
                                if len(pci_order_consumed[0][templateVars[f"pci_link_{x}"]]) > 0:
                                    templateVars["varDefault"] = len(pci_order_consumed[0][templateVars[f"pci_link_{x}"]])
                                else:
                                    templateVars["varDefault"] = 0
                                templateVars["varName"] = 'PCI Order'
                                templateVars["minNum"] = 0
                                templateVars["maxNum"] = 255
                                templateVars[f"pci_order_{x}"] = varNumberLoop(**templateVars)

                                consumed_count = 0
                                for i in pci_order_consumed[0][templateVars[f"pci_link_{x}"]]:
                                    if int(i) == int(templateVars[f"pci_order_{x}"]):
                                        print(f'\n-------------------------------------------------------------------------------------------\n')
                                        print(f'  Error!! PCI Order "{templateVars[f"PciOrder_{x}"]}" is already in use.  Please use an alternative.')
                                        print(f'\n-------------------------------------------------------------------------------------------\n')
                                        consumed_count += 1

                                if consumed_count == 0:
                                    pci_order_consumed[0][templateVars[f"pci_link_{x}"]].append(templateVars[f"pci_order_{x}"])
                                    valid = True

                        # Pull in API Attributes
                        jsonVars = jsonData['components']['schemas']['vnic.Cdn']['allOf'][1]['properties']

                        templateVars["var_description"] = jsonVars['Source']['description']
                        templateVars["jsonVars"] = jsonVars['Source']['enum']
                        templateVars["defaultVar"] = jsonVars['Source']['default']
                        templateVars["varType"] = 'CDN Source'
                        templateVars["cdn_source"] = variablesFromAPI(**templateVars)

                        if templateVars["cdn_source"] == 'user':
                            for x in fabrics:
                                templateVars["Description"] = jsonVars['Value']['description']
                                if templateVars["enable_failover"] == True:
                                    templateVars["varInput"] = 'What is the value for the Consistent Device Name?'
                                else:
                                    templateVars["varInput"] = 'What is the value for Fabric {x} Consistent Device Name?'
                                templateVars["varName"] = 'CDN Name'
                                templateVars["varRegex"] = jsonVars['Value']['pattern']
                                templateVars["minLength"] = 1
                                templateVars["maxLength"] = jsonVars['Value']['maxLength']
                                templateVars[f"cdn_value_{x}"] = varStringLoop(**templateVars)
                        else:
                            for x in fabrics:
                                templateVars[f"cdn_value_{x}"] = ''

                        templateVars["name"] = templateVars["name"].split('-')[0]
                        policy_list = [
                            'policies.ethernet_adapter_policies.ethernet_adapter_policy',
                        ]
                        if templateVars["target_platform"] == 'Standalone':
                            policy_list.append('policies.ethernet_network_policies.ethernet_network_policy')
                        else:
                            policy_list.append('policies.ethernet_network_control_policies.ethernet_network_control_policy')
                            policy_list.append('policies.ethernet_network_group_policies.ethernet_network_group_policy')
                        policy_list.append('policies.ethernet_qos_policies.ethernet_qos_policy')
                        templateVars["allow_opt_out"] = False
                        for policy in policy_list:
                            policy_short = policy.split('.')[2]
                            templateVars[policy_short],policyData = policy_select_loop(jsonData, easy_jsonData, name_prefix, policy, **templateVars)
                            templateVars.update(policyData)
                        if not templateVars["iqn_allocation_type"] == 'None':
                            policy_list [
                                'policies.iscsi_boot_policies.iscsi_boot_policy'
                            ]
                            for x in fabrics:
                                if templateVars["enable_failover"] == False:
                                    templateVars["optional_message"] = f'iSCSI Boot Policy for Fabric {x}'
                                policy_short = policy.split('.')[2]
                                templateVars[f"{policy_short}_{x}"],policyData = policy_select_loop(jsonData, easy_jsonData, name_prefix, policy, **templateVars)
                                templateVars.update(policyData)
                            else:
                                templateVars[f'iscsi_boot_policy_{x}'] = ''



                        for x in fabrics:
                            templateVars[f"vnic_fabric_{x}"] = {
                                'cdn_source':templateVars["cdn_source"],
                            }
                            if not templateVars[f"cdn_value_{x}"] == '':
                                templateVars[f"vnic_fabric_{x}"].update({'cdn_value':templateVars[f"cdn_value_{x}"]})
                            templateVars[f"vnic_fabric_{x}"].update({'enable_failover':templateVars["enable_failover"]})
                            templateVars[f"vnic_fabric_{x}"].update({'ethernet_adapter_policy':templateVars["ethernet_adapter_policy"]})
                            if templateVars["target_platform"] == 'Standalone':
                                templateVars[f"vnic_fabric_{x}"].update({'ethernet_network_policy':templateVars["ethernet_network_policy"]})
                            else:
                                templateVars[f"vnic_fabric_{x}"].update({'ethernet_network_control_policy':templateVars["ethernet_network_control_policy"]})
                                templateVars[f"vnic_fabric_{x}"].update({'ethernet_network_group_policy':templateVars["ethernet_network_group_policy"]})
                            templateVars[f"vnic_fabric_{x}"].update({'ethernet_qos_policy':templateVars["ethernet_qos_policy"]})
                            if not templateVars["iqn_allocation_type"] == 'None':
                                templateVars[f"vnic_fabric_{x}"].update({'iscsi_boot_policy':templateVars[f"iscsi_boot_policy_{x}"]})
                            if templateVars["target_platform"] == 'FIAttached':
                                templateVars[f"vnic_fabric_{x}"].update({'mac_address_allocation_type':templateVars[f"mac_address_allocation_type"]})
                                if templateVars["mac_address_allocation_type"] == 'POOL':
                                    templateVars[f"vnic_fabric_{x}"].update({'mac_address_pool':templateVars[f"mac_pool_{x}"]})
                                else:
                                    templateVars[f"vnic_fabric_{x}"].update({'mac_address_static':templateVars[f"static_mac_{x}"]})
                            templateVars[f"vnic_fabric_{x}"].update({'name':templateVars[f"name_{x}"]})
                            templateVars[f"vnic_fabric_{x}"].update({'pci_link':templateVars[f"pci_link_{x}"]})
                            templateVars[f"vnic_fabric_{x}"].update({'pci_order':templateVars[f"pci_order_{x}"]})
                            templateVars[f"vnic_fabric_{x}"].update({'slot_id':templateVars[f"slot_id"]})
                            if templateVars["target_platform"] == 'FIAttached':
                                templateVars[f"vnic_fabric_{x}"].update({'switch_id':f"{x}"})
                            else:
                                templateVars[f"vnic_fabric_{x}"].update({'uplink_port':templateVars[f"uplink_port_{x}"]})

                        templateVars["name"] = global_name
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        for x in fabrics:
                            if templateVars["enable_failover"] == False:
                                print(f'Fabric {x}:')
                            for k, v in templateVars[f"vnic_fabric_{x}"].items():
                                if k == 'cdn_source':
                                    print(f'    cdn_source                      = "{v}"')
                                elif k == 'cdn_value':
                                    print(f'    cdn_value                       = "{v}"')
                                elif k == 'enable_failover':
                                    print(f'    enable_failover                 = {v}')
                                elif k == 'ethernet_adapter_policy':
                                    print(f'    ethernet_adapter_policy         = "{v}"')
                                elif k == 'ethernet_network_control_policy':
                                    print(f'    ethernet_network_control_policy = "{v}"')
                                elif k == 'ethernet_network_group_policy':
                                    print(f'    ethernet_network_group_policy   = "{v}"')
                                elif k == 'ethernet_network_policy':
                                    print(f'    ethernet_network_policy         = "{v}"')
                                elif k == 'iscsi_boot_policy':
                                    print(f'    iscsi_boot_policy               = "{v}"')
                                elif k == 'mac_address_allocation_type':
                                    print(f'    mac_address_allocation_type     = "{v}"')
                                elif k == 'mac_address_pool':
                                    print(f'    mac_address_pool                = "{v}"')
                                elif k == 'mac_address_static':
                                    print(f'    mac_address_static              = "{v}"')
                                elif k == 'name':
                                    print(f'    name                            = "{v}"')
                                elif k == 'pci_link':
                                    print(f'    placement_pci_link              = {v}')
                                elif k == 'pci_order':
                                    print(f'    placement_pci_order             = {v}')
                                elif k == 'slot_id':
                                    print(f'    placement_slot_id               = "{v}"')
                                elif k == 'switch_id':
                                    print(f'    placement_switch_id             = "{v}"')
                                elif k == 'uplink_port':
                                    print(f'    placement_uplink_port           = {v}')
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        valid_confirm = False
                        while valid_confirm == False:
                            confirm_v = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
                            if confirm_v == 'Y' or confirm_v == '':
                                for x in fabrics:
                                    templateVars["vnics"].append(templateVars[f"vnic_fabric_{x}"])
                                valid_exit = False
                                while valid_exit == False:
                                    if inner_loop_count < 4:
                                        loop_exit = input(f'Would You like to Configure another vNIC?  Enter "Y" or "N" [Y]: ')
                                    else:
                                        loop_exit = input(f'Would You like to Configure another vNIC?  Enter "Y" or "N" [N]: ')
                                    if loop_exit == 'Y' or (inner_loop_count < 4 and loop_exit == ''):
                                        inner_loop_count += 1
                                        valid_confirm = True
                                        valid_exit = True
                                    elif loop_exit == 'N' or loop_exit == '':
                                        vnic_loop = True
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
                    print(f'    description                 = {templateVars["descr"]}')
                    if templateVars["target_platform"] == 'FIAttached':
                        print(f'    enable_azure_stack_host_qos = {templateVars["enable_azure_stack_host_qos"]}')
                    if not templateVars["iqn_allocation_type"] == 'None':
                        print(f'    iqn_allocation_type         = "{templateVars["iqn_allocation_type"]}"')
                    if templateVars["iqn_allocation_type"] == 'Pool':
                        print(f'    iqn_pool                    = "{templateVars["iqn_pool"]}"')
                    if templateVars["iqn_allocation_type"] == 'Static':
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
                                    print(f'        enable_failover                 = {v}')
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

    #========================================
    # LDAP Policy Module
    #========================================
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
            print(f'  This wizard will save the configuraton for this section to the following file:')
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

    #========================================
    # Link Aggregation Policy Module
    #========================================
    def link_aggregation_policies(self, jsonData, easy_jsonData):
        name_prefix = self.name_prefix
        name_suffix = 'link_agg'
        org = self.org
        policy_type = 'Link Aggregation Policy'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'link_aggregation_policies'

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
            print(f'  This wizard will save the configuraton for this section to the following file:')
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

    #========================================
    # Link Control Policy Module
    #========================================
    def link_control_policies(self, jsonData, easy_jsonData):
        name_prefix = self.name_prefix
        name_suffix = 'link_ctrl'
        org = self.org
        policy_type = 'Link Control Policy'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'link_control_policies'

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
            print(f'  This wizard will save the configuraton for this section to the following file:')
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

    #========================================
    # Local User Policy Module
    #========================================
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

                                # for k, v in os.environ.items():
                                #     print(f'key is {k}, and value is {v}')
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

    #========================================
    # MAC Pools Module
    #========================================
    def mac_pools(self, jsonData, easy_jsonData):
        name_prefix = self.name_prefix
        org = self.org
        policy_type = 'MAC Pool'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'mac_pools'

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  MAC Pool Convention Recommendations:')
            print(f'  - Leverage the Cisco UCS OUI of 00:25:B5 for the MAC Pool Prefix.')
            print(f'  - For MAC Pools; create a pool for each Fabric.')
            print(f'  - Pool Size can be between 1 and 1000 addresses.')
            print(f'  - Refer to "UCS Naming Conventions 0.5.ppsx" in the Repository for further guidance.\n')
            print(f'  This wizard will save the configuraton for this section to the following file:')
            print(f'  - Intersight/{org}/{self.type}/{templateVars["template_type"]}.auto.tfvars')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            loop_count = 0
            policy_loop = False
            while policy_loop == False:

                name = naming_rule_fabric(loop_count, name_prefix, org)

                templateVars["name"] = policy_name(name, policy_type)
                templateVars["descr"] = policy_descr(templateVars["name"], policy_type)

                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'  Assignment order decides the order in which the next identifier is allocated.')
                print(f'    1. default - (Intersight Default) Assignment order is decided by the system.')
                print(f'    2. sequential - (Recommended) Identifiers are assigned in a sequential order.')
                print(f'\n-------------------------------------------------------------------------------------------\n')
                valid = False
                while valid == False:
                    templateVars["assignment_order"] = input('Specify the number for the value to select.  [2]: ')
                    if templateVars["assignment_order"] == '' or templateVars["assignment_order"] == '2':
                        templateVars["assignment_order"] = 'sequential'
                        valid = True
                    elif templateVars["assignment_order"] == '1':
                        templateVars["assignment_order"] = 'default'
                        valid = True
                    else:
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        print(f'  Error!! Invalid Option.  Please Select a valid option from the List.')
                        print(f'\n-------------------------------------------------------------------------------------------\n')

                valid = False
                while valid == False:
                    if loop_count % 2 == 0:
                        begin = input('What is the Beginning MAC Address to Assign to the Pool?  [00:25:B5:0A:00:00]: ')
                    else:
                        begin = input('What is the Beginning MAC Address to Assign to the Pool?  [00:25:B5:0B:00:00]: ')
                    if begin == '':
                        if loop_count % 2 == 0:
                            begin = '00:25:B5:0A:00:00'
                        else:
                            begin = '00:25:B5:0B:00:00'
                    valid = validating.mac_address('MAC Pool Address', begin)

                valid = False
                while valid == False:
                    pool_size = input('How Many Mac Addresses should be added to the Pool?  Range is 1-1000 [512]: ')
                    if pool_size == '':
                        pool_size = '512'
                    valid = validating.number_in_range('Pool Size', pool_size, 1, 1000)

                begin = begin.upper()
                beginx = int(begin.replace(':', ''), 16)
                add_dec = (beginx + int(pool_size))
                ending = ':'.join(['{}{}'.format(a, b)
                    for a, b
                    in zip(*[iter('{:012x}'.format(add_dec))]*2)])
                ending = ending.upper()
                templateVars["mac_blocks"] = [{'from':begin, 'to':ending}]

                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'    assignment_order = "{templateVars["assignment_order"]}"')
                print(f'    description      = "{templateVars["descr"]}"')
                print(f'    name             = "{templateVars["name"]}"')
                print(f'    mac_blocks = [')
                for item in templateVars["mac_blocks"]:
                    print('      {')
                    for k, v in item.items():
                        if k == 'from':
                            print(f'        from = "{v}" ')
                        elif k == 'to':
                            print(f'        to   = "{v}"')
                    print('      }')
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

                        configure_loop, loop_count, policy_loop = exit_loop_default_yes(loop_count, policy_type)

                        valid_confirm = True

                    elif confirm_policy == 'N':
                        print(f'\n------------------------------------------------------\n')
                        print(f'  Starting {policy_type} Section over.')
                        print(f'\n------------------------------------------------------\n')
                        valid_confirm = True

                    else:
                        print(f'\n------------------------------------------------------\n')
                        print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                        print(f'\n------------------------------------------------------\n')

        # Close the Template file
        templateVars["template_file"] = 'template_close.jinja2'
        write_to_template(self, **templateVars)

    #========================================
    # Multicast Policy Module
    #========================================
    def multicast_policies(self, jsonData, easy_jsonData):
        name_prefix = self.name_prefix
        name_suffix = 'multicast'
        org = self.org
        policy_type = 'Multicast Policy'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'multicast_policies'

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  Each VLAN must have a Multicast Policy applied to it.  Optional attributes will be')
            print(f'  the IGMP Querier IPs.  IGMP Querier IPs are only needed if you have a non Routed VLAN')
            print(f'  and you need the Fabric Interconnects to act as IGMP Queriers for the network.')
            print(f'  If you configure IGMP Queriers for a Multicast Policy that Policy should only be')
            print(f'  Assigned to the VLAN for which those Queriers will service.\n')
            print(f'  This wizard will save the configuraton for this section to the following file:')
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
                templateVars["igmp_snooping_state"] = 'Enabled'

                valid = False
                while valid == False:
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    templateVars["querier_ip_address"] = input('IGMP Querier IP for Fabric Interconnect A.  [press enter to skip] ')
                    if templateVars["querier_ip_address"] == '':
                        valid = True
                    if not templateVars["querier_ip_address"] == '':
                        valid = validating.ip_address('Fabric A IGMP Querier IP', templateVars["querier_ip_address"])

                    if not templateVars["querier_ip_address"] == '':
                        templateVars["igmp_snooping_querier_state"] == 'Enabled'
                        valid = False
                        while valid == False:
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            templateVars["querier_ip_address_peer"] = input('IGMP Querier IP for Fabric Interconnect B.  [press enter to skip] ')
                            if templateVars["querier_ip_address_peer"] == '':
                                valid = True
                            if not templateVars["querier_ip_address_peer"] == '':
                                valid = validating.ip_address('Fabric B IGMP Querier IP', templateVars["querier_ip_address"])
                    else:
                        templateVars["igmp_snooping_querier_state"] = 'Disabled'
                        templateVars["querier_ip_address_peer"] = ''

                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'    description                 = "{templateVars["descr"]}"')
                print(f'    igmp_snooping_state         = "{templateVars["igmp_snooping_state"]}"')
                print(f'    igmp_snooping_querier_state = "{templateVars["igmp_snooping_querier_state"]}"')
                print(f'    name                        = "{templateVars["name"]}"')
                if not templateVars["querier_ip_address_peer"] == '':
                    print(f'    querier_ip_address          = "{templateVars["querier_ip_address"]}"')
                    print(f'    querier_ip_address_peer     = "{templateVars["querier_ip_address_peer"]}"')
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

    #========================================
    # Network Connectivity Policy Module
    #========================================
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
            print(f'  This wizard will save the configuraton for this section to the following file:')
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

    #========================================
    # NTP Policy Module
    #========================================
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
            print(f'  This wizard will save the configuraton for this section to the following file:')
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
                    primary_ntp = input('What is your Primary NTP Server [0.north-america.pool.ntp.org]: ')
                    if primary_ntp == "":
                        primary_ntp = '0.north-america.pool.ntp.org'
                    if re.search(r'[a-zA-Z]+', primary_ntp):
                        valid = validating.dns_name('Primary NTP Server', primary_ntp)
                    else:
                        valid = validating.ip_address('Primary NTP Server', primary_ntp)

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

                templateVars["enabled"] = True
                templateVars["ntp_servers"] = []
                templateVars["ntp_servers"].append(primary_ntp)
                if alternate_true == 'Y' or alternate_true == '':
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

                templateVars["var_description"] = 'Timezone Regions...'
                templateVars["jsonVars"] = sorted(region_tzs)
                templateVars["defaultVar"] = ''
                templateVars["varType"] = 'Time Region'
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

    #========================================
    # Persistent Memory Policy Module
    #========================================
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
            print(f'  This wizard will save the configuraton for this section to the following file:')
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

    #========================================
    # Port Policy Module
    #========================================
    def port_policies(self, jsonData, easy_jsonData):
        name_prefix = self.name_prefix
        org = self.org
        policy_type = 'Port Policy'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'port_policies'

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

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
            print(f'   - Fibre-Channel Uplinks')
            print(f'   - Fibre-Channel Uplink Port-Channels')
            print(f'   - Server Ports\n')
            print(f'  This wizard will save the configuraton for this section to the following file:')
            print(f'  - Intersight/{org}/{self.type}/{templateVars["template_type"]}.auto.tfvars')
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

                templateVars["name"] = policy_name(name, policy_type)
                templateVars["descr"] = policy_descr(templateVars["name"], policy_type)

                templateVars["multi_select"] = False
                jsonVars = jsonData['components']['schemas']['fabric.PortPolicy']['allOf'][1]['properties']
                templateVars["var_description"] = jsonVars['DeviceModel']['description']
                templateVars["jsonVars"] = sorted(jsonVars['DeviceModel']['enum'])
                templateVars["defaultVar"] = jsonVars['DeviceModel']['default']
                templateVars["varType"] = 'Device Model'
                templateVars["device_model"] = variablesFromAPI(**templateVars)

                fc_mode = ''
                ports_in_use = []
                fc_converted_ports = []
                valid = False
                while valid == False:
                    fc_mode = input('Do you want to convert ports to Fibre Channel Mode?  Enter "Y" or "N" [Y]: ')
                    if fc_mode == '' or fc_mode == 'Y':
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
                        templateVars["port_modes"] = {'custom_mode':'FibreChannel','port_list':fc_ports,'slot_id':1}
                        valid = True
                    elif fc_mode == 'N':
                        valid = True
                    else:
                        print(f'\n------------------------------------------------------\n')
                        print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                        print(f'\n------------------------------------------------------\n')

                port_channel_appliances = []
                port_type = 'Appliance Port-Channel'
                port_count = 1
                valid = False
                while valid == False:
                    configure_port = input(f'Do you want to configure an {port_type}?  Enter "Y" or "N" [N]: ')
                    if configure_port == 'Y':
                        configure_valid = False
                        while configure_valid == False:
                            print(f'\n------------------------------------------------------\n')
                            print(f'  The Port List can be in the format of:')
                            print(f'     5 - Single Port')
                            print(f'     5,11,12,13,14,15 - List of Ports')
                            print(f'\n------------------------------------------------------\n')
                            if templateVars["device_model"] == 'UCS-FI-64108':
                                port_list = input(f'Please enter the list of ports you want to add to the {port_type}?  [95,96]: ')
                            else:
                                port_list = input(f'Please enter the list of ports you want to add to the {port_type}?  [47,48]: ')
                            if port_list == '' and templateVars["device_model"] == 'UCS-FI-64108':
                                port_list = '95,96'
                            elif port_list == '':
                                port_list = '47,48'
                            port_group = []
                            if re.search(r'(^[0-9]+$)', port_list):
                                port_group.append(port_list)
                            elif re.search(r'(^[0-9]+,{1,16}[0-9]+$)', port_list):
                                x = port_list.split(',')
                                port_group = []
                                for i in x:
                                    port_group.append(i)
                            if re.search(r'(^[0-9]+$|^[0-9]+,{1,16}[0-9]+$)', port_list):
                                port_list = port_group
                                port_overlap_count = 0
                                port_overlap = []
                                for x in ports_in_use:
                                    for y in port_list:
                                        if int(x) == int(y):
                                            port_overlap_count += 1
                                            port_overlap.append(x)
                                if port_overlap_count == 0:
                                    if templateVars["device_model"] == 'UCS-FI-64108':
                                        max_port = 108
                                    else:
                                        max_port = 54
                                    if fc_mode == 'Y':
                                        min_port = int(fc_ports[1])
                                    else:
                                        min_port = 1
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

                                        # Prompt User for the Admin Speed of the Port
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
                                        policy_list = [
                                            'policies.ethernet_network_control_policies.ethernet_network_control_policy',
                                            'policies.ethernet_network_group_policies.ethernet_network_group_policy',
                                        ]
                                        templateVars["allow_opt_out"] = False
                                        for policy in policy_list:
                                            policy_short = policy.split('.')[2]
                                            templateVars[policy_short],policyData = policy_select_loop(jsonData, easy_jsonData, name_prefix, policy, **templateVars)
                                            templateVars.update(policyData)

                                        interfaces = []
                                        for i in port_list:
                                            interfaces.append({'port_id':i,'slot_id':1})

                                        pc_id = port_list[0]
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
                                        print(f'\n-------------------------------------------------------------------------------------------\n')
                                        print(f'    admin_speed                     = "{templateVars["admin_speed"]}"')
                                        print(f'    ethernet_network_control_policy = "{templateVars["ethernet_network_control_policy"]}"')
                                        print(f'    ethernet_network_group_policy   = "{templateVars["ethernet_network_group_policy"]}"')
                                        print(f'    interfaces = [')
                                        for item in interfaces:
                                            print('      {')
                                            for k, v in item.items():
                                                print(f'        {k}          = {v}')
                                            print('      }')
                                        print(f'    ]')
                                        print(f'    mode         = "{templateVars["mode"]}"')
                                        print(f'    priority     = "{templateVars["priority"]}"')
                                        print(f'    pc_id        = {pc_id}')
                                        print(f'\n-------------------------------------------------------------------------------------------\n')
                                        valid_confirm = False
                                        while valid_confirm == False:
                                            confirm_port = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                                            if confirm_port == 'Y' or confirm_port == '':
                                                port_channel_appliances.append(port_channel)
                                                for i in port_list:
                                                    ports_in_use.append(i)

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
                                                    else:
                                                        print(f'\n------------------------------------------------------\n')
                                                        print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                                                        print(f'\n------------------------------------------------------\n')

                                            elif confirm_port == 'N':
                                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                                print(f'  Starting {port_type} Configuration Over.')
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

                port_channel_ethernet_uplinks = []
                port_type = 'Ethernet Uplink Port-Channel'
                port_count = 1
                valid = False
                while valid == False:
                    configure_port = input(f'Do you want to configure an {port_type}?  Enter "Y" or "N" [Y]: ')
                    if configure_port == '' or configure_port == 'Y':
                        configure_valid = False
                        while configure_valid == False:
                            print(f'\n------------------------------------------------------\n')
                            print(f'  The Port List can be in the format of:')
                            print(f'     5 - Single Port')
                            print(f'     5,11,12,13,14,15 - List of Ports')
                            print(f'\n------------------------------------------------------\n')
                            if templateVars["device_model"] == 'UCS-FI-64108':
                                port_list = input(f'Please enter the list of ports you want to add to the {port_type}?  [97,98]: ')
                            else:
                                port_list = input(f'Please enter the list of ports you want to add to the {port_type}?  [49,50]: ')
                            if port_list == '' and templateVars["device_model"] == 'UCS-FI-64108':
                                port_list = '97,98'
                            elif port_list == '':
                                port_list = '49,50'
                            port_group = []
                            if re.search(r'(^[0-9]+$)', port_list):
                                port_group.append(port_list)
                            elif re.search(r'(^[0-9]+,{1,16}[0-9]+$)', port_list):
                                x = port_list.split(',')
                                port_group = []
                                for i in x:
                                    port_group.append(i)
                            if re.search(r'(^[0-9]+$|^[0-9]+,{1,16}[0-9]+$)', port_list):
                                port_list = port_group
                                port_overlap_count = 0
                                port_overlap = []
                                for x in ports_in_use:
                                    for y in port_list:
                                        if int(x) == int(y):
                                            port_overlap_count += 1
                                            port_overlap.append(x)
                                if port_overlap_count == 0:
                                    if templateVars["device_model"] == 'UCS-FI-64108':
                                        max_port = 108
                                    else:
                                        max_port = 54
                                    if fc_mode == 'Y':
                                        min_port = int(fc_ports[1])
                                    else:
                                        min_port = 1
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

                                        # Prompt User for the
                                        policy_list = [
                                            'policies.flow_control_policies.flow_control_policy',
                                            'policies.link_aggregation_policies.link_aggregation_policy',
                                            'policies.link_control_policies.link_control_policy',
                                        ]
                                        templateVars["allow_opt_out"] = True
                                        for policy in policy_list:
                                            policy_short = policy.split('.')[2]
                                            templateVars[policy_short],policyData = policy_select_loop(jsonData, easy_jsonData, name_prefix, policy, **templateVars)
                                            templateVars.update(policyData)

                                        interfaces = []
                                        for i in port_list:
                                            interfaces.append({'port_id':i,'slot_id':1})

                                        pc_id = port_list[0]
                                        port_channel = {
                                            'admin_speed':templateVars["admin_speed"],
                                            'flow_control_policy':templateVars["flow_control_policy"],
                                            'interfaces':interfaces,
                                            'link_aggregation_policy':templateVars["link_aggregation_policy"],
                                            'link_control_policy':templateVars["link_control_policy"],
                                            'pc_id':pc_id,
                                            'slot_id':1
                                        }
                                        print(f'\n-------------------------------------------------------------------------------------------\n')
                                        print(f'    admin_speed             = "{templateVars["admin_speed"]}"')
                                        print(f'    flow_control_policy     = "{templateVars["flow_control_policy"]}"')
                                        print(f'    interfaces = [')
                                        for item in interfaces:
                                            print('      {')
                                            for k, v in item.items():
                                                print(f'        {k}          = {v}')
                                            print('      }')
                                        print(f'    ]')
                                        print(f'    link_aggregation_policy = "{templateVars["link_aggregation_policy"]}"')
                                        print(f'    link_control_policy     = "{templateVars["link_control_policy"]}"')
                                        print(f'    pc_id                   = {pc_id}')
                                        print(f'\n-------------------------------------------------------------------------------------------\n')
                                        valid_confirm = False
                                        while valid_confirm == False:
                                            confirm_port = input('Do you want to accept the Configuration Above?  Enter "Y" or "N" [Y]: ')
                                            if confirm_port == 'Y' or confirm_port == '':
                                                port_channel_ethernet_uplinks.append(port_channel)
                                                for i in port_list:
                                                    ports_in_use.append(i)

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
                                                    else:
                                                        print(f'\n------------------------------------------------------\n')
                                                        print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                                                        print(f'\n------------------------------------------------------\n')

                                            elif confirm_port == 'N':
                                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                                print(f'  Starting {port_type} Configuration Over.')
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

                    elif configure_port == 'N':
                        valid = True
                    else:
                        print(f'\n------------------------------------------------------\n')
                        print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                        print(f'\n------------------------------------------------------\n')

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

                fc_ports_in_use = []
                Fabric_A_fc_port_channels = []
                Fabric_B_fc_port_channels = []
                port_type = 'Fibre Channel Port-Channel'
                valid = False
                while valid == False:
                    if len(fc_converted_ports) > 0:
                        configure_port = input(f'Do you want to configure a {port_type}?  Enter "Y" or "N" [Y]: ')
                    else:
                        configure_port = 'N'
                        valid = True
                    if configure_port == '' or configure_port == 'Y':
                        configure_valid = False
                        while configure_valid == False:
                            templateVars["multi_select"] = True
                            templateVars["port_type"] = port_type
                            templateVars["var_description"] = '    Please Select a Port for the Port-Channel:\n'
                            templateVars["var_type"] = 'Unified Port'
                            port_list = vars_from_list(fc_converted_ports, **templateVars)

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

                                print(vsan_list)
                                if len(vsan_list) > 1:
                                    vsan_list = ','.join(str(vsan_list))
                                else:
                                    vsan_list = vsan_list[0]
                                vsan_list = vlan_list_full(vsan_list)

                                templateVars["multi_select"] = False
                                templateVars["port_type"] = port_type
                                templateVars["var_description"] = '    Please Select a VSAN for the Port-Channel:\n'
                                templateVars["var_type"] = 'VSAN'
                                vsan_x = vars_from_list(vsan_list, **templateVars)
                                for vs in vsan_x:
                                    vsan = vs
                                vsans.update({fabric:vsan})


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
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            print(f'    admin_speed  = "{templateVars["admin_speed"]}"')
                            print(f'    fill_pattern = "{templateVars["fill_pattern"]}"')
                            print(f'    interfaces = [')
                            for item in interfaces:
                                print('      {')
                                for k, v in item.items():
                                    print(f'        {k}          = {v}')
                                print('      }')
                            print(f'    ]')
                            print(f'    vsan_id_fabric_a = {vsans.get("Fabric_A")}')
                            print(f'    vsan_id_fabric_b = {vsans.get("Fabric_B")}')
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            valid_confirm = False
                            while valid_confirm == False:
                                confirm_port = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                                if confirm_port == 'Y' or confirm_port == '':
                                    Fabric_A_fc_port_channels.append(port_channel_a)
                                    Fabric_B_fc_port_channels.append(port_channel_b)
                                    for i in port_list:
                                        fc_ports_in_use.append(i)

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
                                        else:
                                            print(f'\n------------------------------------------------------\n')
                                            print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                                            print(f'\n------------------------------------------------------\n')

                                elif confirm_port == 'N':
                                    print(f'\n-------------------------------------------------------------------------------------------\n')
                                    print(f'  Starting {port_type} Configuration Over.')
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

                port_channel_fcoe_uplinks = []
                port_type = 'FCoE Uplink Port-Channel'
                port_count = 1
                valid = False
                while valid == False:
                    configure_port = input(f'Do you want to configure an {port_type}?  Enter "Y" or "N" [N]: ')
                    if configure_port == 'Y':
                        configure_valid = False
                        while configure_valid == False:
                            print(f'\n------------------------------------------------------\n')
                            print(f'  The Port List can be in the format of:')
                            print(f'     5 - Single Port')
                            print(f'     5,11,12,13,14,15 - List of Ports')
                            print(f'\n------------------------------------------------------\n')
                            if templateVars["device_model"] == 'UCS-FI-64108':
                                port_list = input(f'Please enter the list of ports you want to add to the {port_type}?  [97,98]: ')
                            else:
                                port_list = input(f'Please enter the list of ports you want to add to the {port_type}?  [49,50]: ')
                            if port_list == '' and templateVars["device_model"] == 'UCS-FI-64108':
                                port_list = '97,98'
                            elif port_list == '':
                                port_list = '49,50'
                            port_group = []
                            if re.search(r'(^[0-9]+$)', port_list):
                                port_group.append(port_list)
                            elif re.search(r'(^[0-9]+,{1,16}[0-9]+$)', port_list):
                                x = port_list.split(',')
                                port_group = []
                                for i in x:
                                    port_group.append(i)
                            if re.search(r'(^[0-9]+$|^[0-9]+,{1,16}[0-9]+$)', port_list):
                                port_list = port_group
                                port_overlap_count = 0
                                port_overlap = []
                                for x in ports_in_use:
                                    for y in port_list:
                                        if int(x) == int(y):
                                            port_overlap_count += 1
                                            port_overlap.append(x)
                                if port_overlap_count == 0:
                                    if templateVars["device_model"] == 'UCS-FI-64108':
                                        max_port = 108
                                    else:
                                        max_port = 54
                                    if fc_mode == 'Y':
                                        min_port = int(fc_ports[1])
                                    else:
                                        min_port = 1
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

                                        # Prompt User for the
                                        policy_list = [
                                            'policies.link_aggregation_policies.link_aggregation_policy',
                                            'policies.link_control_policies.link_control_policy',
                                        ]
                                        templateVars["allow_opt_out"] = True
                                        for policy in policy_list:
                                            policy_short = policy.split('.')[2]
                                            templateVars[policy_short],policyData = policy_select_loop(jsonData, easy_jsonData, name_prefix, policy, **templateVars)
                                            templateVars.update(policyData)

                                        interfaces = []
                                        for i in port_list:
                                            interfaces.append({'port_id':i,'slot_id':1})

                                        pc_id = port_list[0]
                                        port_channel = {
                                            'admin_speed':templateVars["admin_speed"],
                                            'interfaces':interfaces,
                                            'link_aggregation_policy':templateVars["link_aggregation_policy"],
                                            'link_control_policy':templateVars["link_control_policy"],
                                            'pc_id':pc_id,
                                            'slot_id':1
                                        }
                                        print(f'\n-------------------------------------------------------------------------------------------\n')
                                        print(f'    admin_speed             = "{templateVars["admin_speed"]}"')
                                        print(f'    interfaces = [')
                                        for item in interfaces:
                                            print('      {')
                                            for k, v in item.items():
                                                print(f'        {k}          = {v}')
                                            print('      }')
                                        print(f'    ]')
                                        print(f'    link_aggregation_policy = "{templateVars["link_aggregation_policy"]}"')
                                        print(f'    link_control_policy     = "{templateVars["link_control_policy"]}"')
                                        print(f'    pc_id                   = {pc_id}')
                                        print(f'\n-------------------------------------------------------------------------------------------\n')
                                        valid_confirm = False
                                        while valid_confirm == False:
                                            confirm_port = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                                            if confirm_port == 'Y' or confirm_port == '':
                                                port_channel_fcoe_uplinks.append(port_channel)
                                                for i in port_list:
                                                    ports_in_use.append(i)

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
                                                    else:
                                                        print(f'\n------------------------------------------------------\n')
                                                        print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                                                        print(f'\n------------------------------------------------------\n')

                                            elif confirm_port == 'N':
                                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                                print(f'  Starting {port_type} Configuration Over.')
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

                port_role_appliances = []
                port_type = 'Appliance Ports'
                port_count = 1
                valid = False
                while valid == False:
                    configure_port = input(f'Do you want to configure an {port_type}?  Enter "Y" or "N" [N]: ')
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
                            if templateVars["device_model"] == 'UCS-FI-64108':
                                port_list = input(f'Please enter the ports you want to add to the {port_type}?  [94]: ')
                            else:
                                port_list = input(f'Please enter the ports you want to add to the {port_type}?  [46]: ')
                            if port_list == '' and templateVars["device_model"] == 'UCS-FI-64108':
                                port_list = '94'
                            elif port_list == '':
                                port_list = '46'
                            if re.search(r'(^\d+$|^\d+,{1,48}\d+$|^(\d+\-\d+|\d,){1,48}\d+$)', port_list):
                                original_port_list = port_list
                                ports_expanded = vlan_list_full(port_list)
                                port_list = ports_expanded
                                port_overlap_count = 0
                                port_overlap = []
                                for x in ports_in_use:
                                    for y in port_list:
                                        if int(x) == int(y):
                                            port_overlap_count += 1
                                            port_overlap.append(x)
                                if port_overlap_count == 0:
                                    if templateVars["device_model"] == 'UCS-FI-64108':
                                        max_port = 108
                                    else:
                                        max_port = 54
                                    if fc_mode == 'Y':
                                        min_port = int(fc_ports[1])
                                    else:
                                        min_port = 1
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

                                        # Prompt User for the FEC Mode of the Port
                                        templateVars["var_description"] = jsonVars['Fec']['description']
                                        templateVars["jsonVars"] = sorted(jsonVars['Fec']['enum'])
                                        templateVars["defaultVar"] = jsonVars['Fec']['default']
                                        templateVars["varType"] = 'Fec Mode'
                                        templateVars["fec"] = variablesFromAPI(**templateVars)

                                        # Prompt User for the Port Mode and Priority
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

                                        # Prompt User for the Ethernet Network Control and Group Policies
                                        policy_list = [
                                            'policies.ethernet_network_control_policies.ethernet_network_control_policy',
                                            'policies.ethernet_network_group_policies.ethernet_network_group_policy',
                                        ]
                                        templateVars["allow_opt_out"] = False
                                        for policy in policy_list:
                                            policy_short = policy.split('.')[2]
                                            templateVars[policy_short],
                                            policyData = policy_select_loop(jsonData, easy_jsonData, name_prefix, policy, **templateVars)
                                            templateVars.update(policyData)

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
                                        print(f'\n-------------------------------------------------------------------------------------------\n')
                                        print(f'    admin_speed                     = "{templateVars["admin_speed"]}"')
                                        print(f'    ethernet_network_control_policy = "{templateVars["ethernet_network_control_policy"]}"')
                                        print(f'    ethernet_network_group_policy   = "{templateVars["ethernet_network_group_policy"]}"')
                                        print(f'    fec                             = "{templateVars["fec"]}"')
                                        print(f'    mode                            = "{templateVars["mode"]}"')
                                        print(f'    port_list                       = "{original_port_list}"')
                                        print(f'    priority                        = "{templateVars["priority"]}"')
                                        print(f'\n-------------------------------------------------------------------------------------------\n')
                                        valid_confirm = False
                                        while valid_confirm == False:
                                            confirm_port = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                                            if confirm_port == 'Y' or confirm_port == '':
                                                port_role_appliances.append(port_role)
                                                for i in port_list:
                                                    ports_in_use.append(i)

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
                                                    else:
                                                        print(f'\n------------------------------------------------------\n')
                                                        print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                                                        print(f'\n------------------------------------------------------\n')

                                            elif confirm_port == 'N':
                                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                                print(f'  Starting {port_type} Configuration Over.')
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

                port_role_ethernet_uplinks = []
                port_type = 'Ethernet Uplink'
                port_count = 1
                valid = False
                while valid == False:
                    configure_port = input(f'Do you want to configure an {port_type}?  Enter "Y" or "N" [N]: ')
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
                            if templateVars["device_model"] == 'UCS-FI-64108':
                                port_list = input(f'Please enter the list of ports you want to add to the {port_type}?  [97]: ')
                            else:
                                port_list = input(f'Please enter the list of ports you want to add to the {port_type}?  [49]: ')
                            if port_list == '' and templateVars["device_model"] == 'UCS-FI-64108':
                                port_list = '97'
                            elif port_list == '':
                                port_list = '49'
                            if re.search(r'(^\d+$|^\d+,{1,48}\d+$|^(\d+\-\d+|\d,){1,48}\d+$)', port_list):
                                original_port_list = port_list
                                ports_expanded = vlan_list_full(port_list)
                                port_list = ports_expanded
                                port_overlap_count = 0
                                port_overlap = []
                                for x in ports_in_use:
                                    for y in port_list:
                                        if int(x) == int(y):
                                            port_overlap_count += 1
                                            port_overlap.append(x)
                                if port_overlap_count == 0:
                                    if templateVars["device_model"] == 'UCS-FI-64108':
                                        max_port = 108
                                    else:
                                        max_port = 54
                                    if fc_mode == 'Y':
                                        min_port = int(fc_ports[1])
                                    else:
                                        min_port = 1
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

                                        # Prompt User for the FEC Mode of the Port
                                        templateVars["var_description"] = jsonVars['Fec']['description']
                                        templateVars["jsonVars"] = sorted(jsonVars['Fec']['enum'])
                                        templateVars["defaultVar"] = jsonVars['Fec']['default']
                                        templateVars["varType"] = 'Fec Mode'
                                        templateVars["fec"] = variablesFromAPI(**templateVars)

                                        # Prompt User for the
                                        policy_list = [
                                            'policies.flow_control_policies.flow_control_policy',
                                            'policies.link_control_policies.link_control_policy',
                                        ]
                                        templateVars["allow_opt_out"] = True
                                        for policy in policy_list:
                                            policy_short = policy.split('.')[2]
                                            templateVars[policy_short],
                                            policyData = policy_select_loop(jsonData, easy_jsonData, name_prefix, policy, **templateVars)
                                            templateVars.update(policyData)

                                        port_role = {
                                            'admin_speed':templateVars["admin_speed"],
                                            'fec':templateVars["fec"],
                                            'flow_control_policy':templateVars["flow_control_policy"],
                                            'link_control_policy':templateVars["link_control_policy"],
                                            'port_id':original_port_list,
                                            'slot_id':1
                                        }
                                        print(f'\n-------------------------------------------------------------------------------------------\n')
                                        print(f'    admin_speed         = "{templateVars["admin_speed"]}"')
                                        print(f'    fec                 = "{templateVars["fec"]}"')
                                        print(f'    flow_control_policy = "{templateVars["flow_control_policy"]}"')
                                        print(f'    link_control_policy = "{templateVars["link_control_policy"]}"')
                                        print(f'    port_list           = "{original_port_list}"')
                                        print(f'\n-------------------------------------------------------------------------------------------\n')
                                        valid_confirm = False
                                        while valid_confirm == False:
                                            confirm_port = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                                            if confirm_port == 'Y' or confirm_port == '':
                                                port_role_ethernet_uplinks.append(port_role)
                                                for i in port_list:
                                                    ports_in_use.append(i)

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
                                                    else:
                                                        print(f'\n------------------------------------------------------\n')
                                                        print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                                                        print(f'\n------------------------------------------------------\n')

                                            elif confirm_port == 'N':
                                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                                print(f'  Starting {port_type} Configuration Over.')
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

                Fabric_A_port_role_fc = []
                Fabric_B_port_role_fc = []
                port_type = 'Fibre-Channel Uplink'
                valid = False
                while valid == False:
                    if len(fc_converted_ports) > 0:
                        configure_port = input(f'Do you want to configure a {port_type}?  Enter "Y" or "N" [N]: ')
                    else:
                        configure_port = 'N'
                        valid = True
                    if configure_port == 'Y':
                        configure_valid = False
                        while configure_valid == False:
                            templateVars["multi_select"] = False
                            templateVars["port_type"] = port_type
                            templateVars["var_description"] = '    Please Select a Port for the Uplink:\n'
                            templateVars["var_type"] = 'Unified Port'
                            port_list = vars_from_list(fc_converted_ports, **templateVars)

                            # Prompt User for the Admin Speed of the Port
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

                                vsan_list = ','.join(vsan_list)
                                vsan_list = vlan_list_full(vsan_list)

                                templateVars["multi_select"] = False
                                templateVars["port_type"] = port_type
                                templateVars["var_description"] = '    Please Select a VSAN for the Port-Channel:\n'
                                templateVars["var_type"] = 'VSAN'
                                vsan_x = vars_from_list(vsan_list, **templateVars)
                                for vs in vsan_x:
                                    vsan = vs
                                vsans.update({fabric:vsan})

                            port_list = '%s' % (port_list[0])
                            fc_port_role_a = {
                                'admin_speed':templateVars["admin_speed"],
                                'fill_pattern':templateVars["fill_pattern"],
                                'port_id':port_list,
                                'slot_id':1,
                                'vsan_id':vsans.get("Fabric_A")
                            }
                            fc_port_role_b = {
                                'admin_speed':templateVars["admin_speed"],
                                'fill_pattern':templateVars["fill_pattern"],
                                'port_id':port_list,
                                'slot_id':1,
                                'vsan_id':vsans.get("Fabric_B")
                            }
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            print(f'    admin_speed      = "{templateVars["admin_speed"]}"')
                            print(f'    fill_pattern     = "{templateVars["fill_pattern"]}"')
                            print(f'    port_list        = "{port_list}"')
                            print(f'    vsan_id_fabric_a = {vsans.get("Fabric_A")}')
                            print(f'    vsan_id_fabric_b = {vsans.get("Fabric_B")}')
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            valid_confirm = False
                            while valid_confirm == False:
                                confirm_port = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                                if confirm_port == 'Y' or confirm_port == '':
                                    Fabric_A_port_role_fc.append(fc_port_role_a)
                                    Fabric_B_port_role_fc.append(fc_port_role_b)
                                    for i in port_list:
                                        fc_ports_in_use.append(i)

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
                                        else:
                                            print(f'\n------------------------------------------------------\n')
                                            print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                                            print(f'\n------------------------------------------------------\n')

                                elif confirm_port == 'N':
                                    print(f'\n-------------------------------------------------------------------------------------------\n')
                                    print(f'  Starting {port_type} Configuration Over.')
                                    print(f'\n-------------------------------------------------------------------------------------------\n')
                                    valid_confirm = True
                                else:
                                    print(f'\n------------------------------------------------------\n')
                                    print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                                    print(f'\n------------------------------------------------------\n')

                    elif configure_port == '' or configure_port == 'N':
                        valid = True
                    else:
                        print(f'\n------------------------------------------------------\n')
                        print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                        print(f'\n------------------------------------------------------\n')

                port_role_fcoe_uplinks = []
                port_type = 'FCoE Uplink'
                port_count = 1
                valid = False
                while valid == False:
                    configure_port = input(f'Do you want to configure an {port_type}?  Enter "Y" or "N" [N]: ')
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
                            if templateVars["device_model"] == 'UCS-FI-64108':
                                port_list = input(f'Please enter the list of ports you want to add to the {port_type}?  [97]: ')
                            else:
                                port_list = input(f'Please enter the list of ports you want to add to the {port_type}?  [49]: ')
                            if port_list == '' and templateVars["device_model"] == 'UCS-FI-64108':
                                port_list = '97'
                            elif port_list == '':
                                port_list = '49'
                            if re.search(r'(^\d+$|^\d+,{1,48}\d+$|^(\d+\-\d+|\d,){1,48}\d+$)', port_list):
                                original_port_list = port_list
                                ports_expanded = vlan_list_full(port_list)
                                port_list = ports_expanded
                                port_overlap_count = 0
                                port_overlap = []
                                for x in ports_in_use:
                                    for y in port_list:
                                        if int(x) == int(y):
                                            port_overlap_count += 1
                                            port_overlap.append(x)
                                if port_overlap_count == 0:
                                    if templateVars["device_model"] == 'UCS-FI-64108':
                                        max_port = 108
                                    else:
                                        max_port = 54
                                    if fc_mode == 'Y':
                                        min_port = int(fc_ports[1])
                                    else:
                                        min_port = 1
                                    for port in port_list:
                                        valid_ports = validating.number_in_range('Port Range', port, min_port, max_port)
                                        if valid_ports == False:
                                            break
                                    if valid_ports == True:
                                        # Prompt User for the Admin Speed of the Port
                                        # Prompt User for the Admin Speed of the Port
                                        templateVars["multi_select"] = False
                                        jsonVars = jsonData['components']['schemas']['fabric.TransceiverRole']['allOf'][1]['properties']
                                        templateVars["var_description"] = jsonVars['AdminSpeed']['description']
                                        templateVars["jsonVars"] = jsonVars['AdminSpeed']['enum']
                                        templateVars["defaultVar"] = jsonVars['AdminSpeed']['default']
                                        templateVars["varType"] = 'Admin Speed'
                                        templateVars["admin_speed"] = variablesFromAPI(**templateVars)

                                        # Prompt User for the FEC Mode of the Port
                                        templateVars["var_description"] = jsonVars['Fec']['description']
                                        templateVars["jsonVars"] = sorted(jsonVars['Fec']['enum'])
                                        templateVars["defaultVar"] = jsonVars['Fec']['default']
                                        templateVars["varType"] = 'Fec Mode'
                                        templateVars["fec"] = variablesFromAPI(**templateVars)

                                        # Prompt User for the
                                        policy_list = [
                                            'policies.link_control_policies.link_control_policy'
                                        ]
                                        templateVars["allow_opt_out"] = True
                                        for policy in policy_list:
                                            policy_short = policy.split('.')[2]
                                            templateVars[policy_short],
                                            policyData = policy_select_loop(jsonData, easy_jsonData, name_prefix, policy, **templateVars)
                                            templateVars.update(policyData)

                                        port_role = {
                                            'admin_speed':templateVars["admin_speed"],
                                            'fec':templateVars["fec"],
                                            'link_control_policy':templateVars["link_control_policy"],
                                            'port_id':original_port_list,
                                            'slot_id':1
                                        }
                                        print(f'\n-------------------------------------------------------------------------------------------\n')
                                        print(f'    admin_speed         = "{templateVars["admin_speed"]}"')
                                        print(f'    fec                 = "{templateVars["fec"]}"')
                                        print(f'    link_control_policy = "{templateVars["link_control_policy"]}"')
                                        print(f'    port_list           = "{original_port_list}"')
                                        print(f'\n-------------------------------------------------------------------------------------------\n')
                                        valid_confirm = False
                                        while valid_confirm == False:
                                            confirm_port = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                                            if confirm_port == 'Y' or confirm_port == '':
                                                port_role_fcoe_uplinks.append(port_role)
                                                for i in port_list:
                                                    ports_in_use.append(i)

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
                                                    else:
                                                        print(f'\n------------------------------------------------------\n')
                                                        print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                                                        print(f'\n------------------------------------------------------\n')

                                            elif confirm_port == 'N':
                                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                                print(f'  Starting {port_type} Configuration Over.')
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

                port_role_servers = []
                port_type = 'Server Ports'
                port_count = 1
                valid = False
                while valid == False:
                    configure_port = input(f'Do you want to configure {port_type}?  Enter "Y" or "N" [Y]: ')
                    if configure_port == '' or configure_port == 'Y':
                        configure_valid = False
                        while configure_valid == False:
                            print(f'\n------------------------------------------------------\n')
                            print(f'  The Port List can be in the format of:')
                            print(f'     5 - Single Port')
                            print(f'     5-10 - Range of Ports')
                            print(f'     5,11,12,13,14,15 - List of Ports')
                            print(f'     5-10,20-30 - Ranges and Lists of Ports')
                            print(f'\n------------------------------------------------------\n')
                            if templateVars["device_model"] == 'UCS-FI-64108':
                                port_list = input(f'Please enter the list of ports you want to add to the {port_type}?  [5-36]: ')
                            else:
                                port_list = input(f'Please enter the list of ports you want to add to the {port_type}?  [5-18]: ')
                            if port_list == '' and templateVars["device_model"] == 'UCS-FI-64108':
                                port_list = '5-36'
                            elif port_list == '':
                                port_list = '5-18'
                            if re.search(r'(^\d+$|^\d+,{1,48}\d+$|^(\d+\-\d+|\d,){1,48}\d+$)', port_list):
                                original_port_list = port_list
                                ports_expanded = vlan_list_full(port_list)
                                port_list = ports_expanded
                                port_overlap_count = 0
                                port_overlap = []
                                for x in ports_in_use:
                                    for y in port_list:
                                        if int(x) == int(y):
                                            port_overlap_count += 1
                                            port_overlap.append(x)
                                if port_overlap_count == 0:
                                    if templateVars["device_model"] == 'UCS-FI-64108':
                                        max_port = 108
                                    else:
                                        max_port = 54
                                    if fc_mode == 'Y':
                                        min_port = int(fc_ports[1])
                                    else:
                                        min_port = 1
                                    for port in port_list:
                                        valid_ports = validating.number_in_range('Port Range', port, min_port, max_port)
                                        if valid_ports == False:
                                            break
                                    if valid_ports == True:
                                        print(f'\n-------------------------------------------------------------------------------------------\n')
                                        print(f'  Do you want to accept the following Server Port configuration?')
                                        print(f'    port_list           = "{original_port_list}"')
                                        print(f'\n-------------------------------------------------------------------------------------------\n')
                                        valid_confirm = False
                                        while valid_confirm == False:
                                            confirm_port = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                                            if confirm_port == 'Y' or confirm_port == '':
                                                server_ports = {'port_list':original_port_list,'slot_id':1}
                                                port_role_servers.append(server_ports)
                                                for i in port_list:
                                                    ports_in_use.append(i)

                                                valid_exit = False
                                                while valid_exit == False:
                                                    port_exit = input(f'Would You like to Configure more {port_type}?  Enter "Y" or "N" [N]: ')
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
                                                print(f'  Starting {port_type} Configuration Over.')
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

                    elif configure_port == 'N':
                        valid = True
                    else:
                        print(f'\n------------------------------------------------------\n')
                        print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                        print(f'\n------------------------------------------------------\n')

                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'    description  = "{templateVars["descr"]}"')
                print(f'    device_model = "{templateVars["device_model"]}"')
                print(f'    name         = "{templateVars["name"]}"')
                if len(port_channel_appliances) > 0:
                    print(f'    port_channel_appliances = [')
                    for item in port_channel_appliances:
                        for k, v in item.items():
                            if k == 'pc_id':
                                print(f'      {v} = ''{')
                        for k, v in item.items():
                            if k == 'admin_speed':
                                print(f'        admin_speed                     = "{v}"')
                            elif k == 'ethernet_network_control_policy':
                                print(f'        ethernet_network_control_policy = "{v}"')
                            elif k == 'ethernet_network_group_policy':
                                print(f'        ethernet_network_group_policy   = "{v}"')
                            elif k == 'interfaces':
                                print(f'        interfaces = [')
                                for i in v:
                                    print('          {')
                                    for x, y in i.items():
                                        print(f'            {x}          = {y}')
                                    print('          }')
                                print(f'        ]')
                            elif k == 'mode':
                                print(f'        mode     = "{v}"')
                            elif k == 'priority':
                                print(f'        priority = "{v}"')
                        print('      }')
                    print(f'    ]')
                if len(port_channel_ethernet_uplinks) > 0:
                    print(f'    port_channel_ethernet_uplinks = [')
                    for item in port_channel_ethernet_uplinks:
                        for k, v in item.items():
                            if k == 'pc_id':
                                print(f'      {v} = ''{')
                        for k, v in item.items():
                            if k == 'admin_speed':
                                print(f'        admin_speed         = "{v}"')
                            elif k == 'flow_control_policy':
                                print(f'        flow_control_policy = "{v}"')
                            elif k == 'interfaces':
                                print(f'        interfaces = [')
                                for i in v:
                                    print('          {')
                                    for x, y in i.items():
                                        print(f'            {x}          = {y}')
                                    print('          }')
                                print(f'        ]')
                            elif k == 'link_aggregation_policy':
                                print(f'        link_aggregation_policy = "{v}"')
                            elif k == 'link_control_policy':
                                print(f'        link_control_policy     = "{v}"')
                        print('      }')
                    print(f'    ]')
                if len(Fabric_A_fc_port_channels) > 0:
                    print(f'    port_channel_fc_uplinks = [')
                    item_count = 0
                    for item in Fabric_A_fc_port_channels:
                        for k, v in item.items():
                            if k == 'pc_id':
                                print(f'      {v} = ''{')
                        for k, v in item.items():
                            if k == 'admin_speed':
                                print(f'        admin_speed  = "{v}"')
                            elif k == 'fill_pattern':
                                print(f'        fill_pattern = "{v}"')
                            elif k == 'interfaces':
                                print(f'        interfaces = [')
                                for i in v:
                                    print('          {')
                                    for x, y in i.items():
                                        print(f'            {x}          = {y}')
                                    print('          }')
                                print(f'        ]')
                            elif k == 'vsan_id':
                                print(f'        vsan_fabric_a = "{v}"')
                                print(f'        vsan_fabric_b = "{Fabric_B_fc_port_channels[item_count].get("vsan_id")}"')
                        print('      }')
                        item_count += 1
                    print(f'    ]')
                if len(port_channel_fcoe_uplinks) > 0:
                    print(f'    port_channel_fcoe_uplinks = [')
                    for item in port_channel_fcoe_uplinks:
                        for k, v in item.items():
                            if k == 'pc_id':
                                print('      {v} = {')
                        for k, v in item.items():
                            if k == 'admin_speed':
                                print(f'        admin_speed = "{v}"')
                            elif k == 'interfaces':
                                print(f'        interfaces = [')
                                for i in v:
                                    print('          {')
                                    for x, y in i.items():
                                        print(f'            {x}          = {y}')
                                    print('          }')
                                print(f'        ]')
                            elif k == 'link_aggregation_policy':
                                print(f'        link_aggregation_policy = "{v}"')
                            elif k == 'link_control_policy':
                                print(f'        link_control_policy     = "{v}"')
                        print('      }')
                    print(f'    ]')
                if len(templateVars["port_modes"]) > 0:
                    print('    port_modes = {')
                    for k, v in templateVars["port_modes"].items():
                        if k == 'custom_mode':
                            print(f'      custom_mode = "{v}"')
                        elif k == 'port_list':
                            print(f'      port_list   = "{v}"')
                        elif k == 'slot_id':
                            print(f'      slot_id     = {v}')
                    print('    }')
                item_count = 0
                if len(port_role_appliances) > 0:
                    print(f'    port_role_appliances = [')
                    for item in port_role_appliances:
                        print(f'      {item_count} = ''{')
                        item_count += 1
                        for k, v in item.items():
                            if k == 'admin_speed':
                                print(f'        admin_speed                     = "{v}"')
                            elif k == 'ethernet_network_control_policy':
                                print(f'        ethernet_network_control_policy = "{v}"')
                            elif k == 'ethernet_network_group_policy':
                                print(f'        ethernet_network_group_policy   = "{v}"')
                            elif k == 'fec':
                                print(f'        fec                             = "{v}"')
                            elif k == 'mode':
                                print(f'        mode                            = "{v}"')
                            elif k == 'port_id':
                                print(f'        port_list                       = "{v}"')
                            elif k == 'priority':
                                print(f'        priority                        = "{v}"')
                            elif k == 'slot_id':
                                print(f'        slot_id                         = 1')
                        print('      }')
                    print(f'    ]')
                item_count = 0
                if len(port_role_ethernet_uplinks) > 0:
                    print(f'    port_role_ethernet_uplinks = [')
                    for item in port_role_ethernet_uplinks:
                        print(f'      {item_count} = ''{')
                        item_count += 1
                        for k, v in item.items():
                            if k == 'admin_speed':
                                print(f'        admin_speed         = "{v}"')
                            elif k == 'fec':
                                print(f'        fec                 = "{v}"')
                            elif k == 'flow_control_policy':
                                print(f'        flow_control_policy = "{v}"')
                            elif k == 'link_control_policy':
                                print(f'        link_control_policy = "{v}"')
                            elif k == 'port_id':
                                print(f'        port_list           = "{v}"')
                            elif k == 'slot_id':
                                print(f'        slot_id             = 1')
                        print('      }')
                    print(f'    ]')
                item_count = 0
                if len(Fabric_A_port_role_fc) > 0:
                    print(f'    port_role_fc_uplinks = [')
                    for item in Fabric_A_port_role_fc:
                        print(f'      {item_count} = ''{')
                        for k, v in item.items():
                            if k == 'admin_speed':
                                print(f'        admin_speed   = "{v}"')
                            elif k == 'fill_pattern':
                                print(f'        fill_pattern  = "{v}"')
                            elif k == 'port_id':
                                print(f'        port_list     = "{v}"')
                            elif k == 'slot_id':
                                print(f'        slot_id       = 1')
                            elif k == 'vsan_id':
                                print(f'        vsan_fabric_a = "{v}"')
                                print(f'        vsan_fabric_b = "{Fabric_B_port_role_fc[item_count].get("vsan_id")}"')
                        print('      }')
                        item_count += 1
                    print(f'    ]')
                item_count = 0
                if len(port_role_fcoe_uplinks) > 0:
                    print(f'    port_role_fcoe_uplinks = [')
                    for item in port_role_fcoe_uplinks:
                        print(f'      {item_count} = ''{')
                        item_count += 1
                        for k, v in item.items():
                            if k == 'admin_speed':
                                print(f'        admin_speed         = "{v}"')
                            elif k == 'fec':
                                print(f'        fec                 = "{v}"')
                            elif k == 'link_control_policy':
                                print(f'        link_control_policy = "{v}"')
                            elif k == 'port_id':
                                print(f'        port_list           = "{v}"')
                            elif k == 'slot_id':
                                print(f'        slot_id             = 1')
                        print('      }')
                    print(f'    ]')
                if len(port_role_servers) > 0:
                    print(f'    port_role_servers = [')
                    for item in port_role_servers:
                        print(f'      {item_count} = ''{')
                        item_count += 1
                        for k, v in item.items():
                            if k == 'port_list':
                                print(f'        port_list           = "{v}"')
                            if k == 'slot_id':
                                print(f'        slot_id             = {v}')
                        print('      }')
                    print(f'    ]')
                print(f'\n-------------------------------------------------------------------------------------------\n')
                valid_confirm = False
                while valid_confirm == False:
                    confirm_policy = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                    if confirm_policy == 'Y' or confirm_policy == '':
                        confirm_policy = 'Y'

                        templateVars["port_channel_appliances"] = port_channel_appliances
                        templateVars["port_channel_ethernet_uplinks"] = port_channel_ethernet_uplinks
                        templateVars["port_channel_fcoe_uplinks"] = port_channel_fcoe_uplinks
                        templateVars["port_role_appliances"] = port_role_appliances
                        templateVars["port_role_ethernet_uplinks"] = port_role_ethernet_uplinks
                        templateVars["port_role_fcoe_uplinks"] = port_role_fcoe_uplinks
                        templateVars["port_role_servers"] = port_role_servers
                        # templateVars["port_modes"] = [{'custom_mode':'FibreChannel','port_list':fc_ports,'slot_id':1}]

                        original_name = templateVars["name"]
                        templateVars["name"] = '%s_A' % (original_name)
                        templateVars["port_channel_fc_uplinks"] = Fabric_A_fc_port_channels
                        templateVars["port_role_fc_uplinks"] = Fabric_A_port_role_fc

                        # Write Policies to Template File
                        templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
                        write_to_template(self, **templateVars)

                        templateVars["name"] = '%s_B' % (original_name)
                        templateVars["port_channel_fc_uplinks"] = Fabric_B_fc_port_channels
                        templateVars["port_role_fc_uplinks"] = Fabric_B_port_role_fc

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

    #========================================
    # Power Policy Module
    #========================================
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
            print(f'  This wizard will save the configuraton for this section to the following file:')
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

    #========================================
    # Resource Pool Module
    #========================================
    def resource_pools(self, jsonData, easy_jsonData):
        name_prefix = self.name_prefix
        name_suffix = 'resource'
        org = self.org
        policy_type = 'Resource Pool'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'resource_pools'

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  The {policy_type} represents a collection of resources that can be associated to ')
            print(f'  the configuration entities such as server profiles.\n')
            print(f'  This wizard will save the configuraton for this section to the following file:')
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

                    # Pull in the Policies for iSCSI Boot
                    templateVars["multi_select"] = False

                    # Assignment Order
                    jsonVars = jsonData['components']['schemas']['pool.AbstractPool']['allOf'][1]['properties']
                    templateVars["var_description"] = jsonVars['AssignmentOrder']['description']
                    templateVars["jsonVars"] = sorted(jsonVars['AssignmentOrder']['enum'])
                    templateVars["defaultVar"] = jsonVars['AssignmentOrder']['default']
                    templateVars["varType"] = 'Assignment Order'
                    templateVars["assignment_order"] = variablesFromAPI(**templateVars)

                    # List of Serial Numbers
                    templateVars['serial_number_list'] = []
                    valid = False
                    while valid == False:
                        templateVars["Description"] = 'A List of Serial Numbers to add to the Resource Pool.'
                        templateVars["varDefault"] = ''
                        templateVars["varInput"] = 'Enter the Server Serial Number:'
                        templateVars["varName"] = 'Serial Number'
                        templateVars["varRegex"] = '^[A-Z]{3}[2-3][\\d]([0][1-9]|[1-4][0-9]|[5][1-3])[\\dA-Z]{4}$'
                        templateVars["minLength"] = 11
                        templateVars["maxLength"] = 11
                        templateVars['serial_number_list'].append(varStringLoop(**templateVars))

                        templateVars["Description"] = 'Add Additional Serial Numbers.'
                        templateVars["varInput"] = f'Do you want to add another Serial Number?'
                        templateVars["varDefault"] = 'N'
                        templateVars["varName"] = 'Additional Serial Numbers'
                        valid = varBoolLoop(**templateVars)

                    # Server Type
                    jsonVars = easy_jsonData['pools']['resourcepool.Pool']
                    templateVars["var_description"] = jsonVars['server_type']['description']
                    templateVars["jsonVars"] = sorted(jsonVars['server_type']['enum'])
                    templateVars["defaultVar"] = jsonVars['server_type']['default']
                    templateVars["varType"] = 'Server Type'
                    templateVars["server_type"] = variablesFromAPI(**templateVars)

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'   assignment_order   = "{templateVars["assignment_order"]}"')
                    print(f'   description        = "{templateVars["descr"]}"')
                    print(f'   name               = "{templateVars["name"]}"')
                    print(f'   serial_number_list = {templateVars["serial_number_list"]}')
                    print(f'   server_type        = "{templateVars["server_type"]}"')
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

    #========================================
    # SAN Connectivity Policy Module
    #========================================
    def san_connectivity_policies(self, jsonData, easy_jsonData):
        pci_order_consumed = [{0:[0, 1, 2, 3, 4, 5, 6, 7]},{1:[0, 1, 2, 3, 4, 5, 6, 7]}]
        name_prefix = self.name_prefix
        name_suffix = 'san'
        org = self.org
        policy_type = 'SAN Connectivity Policy'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'san_connectivity_policies'

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  You can Skip this policy if you are not configuring Fibre-Channel.\n')
            print(f'  A {policy_type} will configure vHBA adapters for Server Profiles.\n')
            print(f'  This wizard will save the configuraton for this section to the following file:')
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
                    jsonVars = jsonData['components']['schemas']['vnic.SanConnectivityPolicy']['allOf'][1]['properties']
                    templateVars["var_description"] = jsonVars['TargetPlatform']['description']
                    templateVars["jsonVars"] = sorted(jsonVars['TargetPlatform']['enum'])
                    templateVars["defaultVar"] = jsonVars['TargetPlatform']['default']
                    templateVars["varType"] = 'Target Platform'
                    templateVars["target_platform"] = variablesFromAPI(**templateVars)

                    if templateVars["target_platform"] == 'FIAttached':
                        templateVars["var_description"] = jsonVars['PlacementMode']['description']
                        templateVars["jsonVars"] = sorted(jsonVars['PlacementMode']['enum'])
                        templateVars["defaultVar"] = jsonVars['PlacementMode']['default']
                        templateVars["varType"] = 'Placement Mode'
                        templateVars["vhba_placement_mode"] = variablesFromAPI(**templateVars)

                        templateVars["var_description"] = jsonVars['WwnnAddressType']['description']
                        templateVars["jsonVars"] = sorted(jsonVars['WwnnAddressType']['enum'])
                        templateVars["defaultVar"] = jsonVars['WwnnAddressType']['default']
                        templateVars["varType"] = 'WWNN Allocation Type'
                        templateVars["wwnn_allocation_type"] = variablesFromAPI(**templateVars)

                        templateVars["wwnn_pool"] = ''
                        templateVars["wwnn_static"] = ''
                        if templateVars["wwnn_allocation_type"] == 'POOL':
                            policy_list = [
                                'pools.wwnn_pools.wwnn_pool'
                            ]
                            templateVars["allow_opt_out"] = False
                            for policy in policy_list:
                                templateVars["wwnn_pool"],policyData = policy_select_loop(jsonData, easy_jsonData, name_prefix, policy, **templateVars)
                                templateVars.update(policyData)

                        else:
                            valid = False
                            while valid == False:
                                templateVars["wwnn_static"] = input(f'What is the Static WWNN you would like to assign to this SAN Policy?  ')
                                if not templateVars["wwnn_static"] == '':
                                    valid = validating.wwxn_address('WWNN Static', templateVars["wwnn_static"])

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'   BEGINNING vHBA Creation Process')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    fabrics = ['A', 'B']
                    templateVars["vhbas"] = []
                    inner_loop_count = 1
                    vhba_loop = False
                    while vhba_loop == False:
                        temp_policy_name = templateVars["name"]
                        templateVars["name"] = 'the vHBAs'
                        policy_list = [
                            'policies.fibre_channel_adapter_policies.fibre_channel_adapter_policy',
                            'policies.fibre_channel_qos_policies.fibre_channel_qos_policy'
                        ]
                        templateVars["allow_opt_out"] = False
                        for policy in policy_list:
                            policy_short = policy.split('.')[2]
                            templateVars[policy_short],policyData = policy_select_loop(jsonData, easy_jsonData, name_prefix, policy, **templateVars)
                            templateVars.update(policyData)
                            print(f'policy is {policy_short} and value is {templateVars[policy_short]}')

                        for x in fabrics:
                            templateVars["name"] = f'the vHBA on Fabric {x}'
                            policy_list = [
                                'policies.fibre_channel_network_policies.fibre_channel_network_policy'
                            ]
                            templateVars["allow_opt_out"] = False
                            for policy in policy_list:
                                policy_short = policy.split('.')[2]
                                templateVars[f"{policy_short}_{x}"],policyData = policy_select_loop(jsonData, easy_jsonData, name_prefix, policy, **templateVars)
                                templateVars.update(policyData)

                        templateVars["name"] = temp_policy_name

                        for x in fabrics:
                            valid = False
                            while valid == False:
                                templateVars[f'name_{x}'] = input(f'What is the name for Fabric {x} vHBA?  [HBA-{x}]: ')
                                if templateVars[f'name_{x}'] == '':
                                    templateVars[f'name_{x}'] = 'HBA-%s' % (x)
                                valid = validating.vname('vNIC Name', templateVars[f'name_{x}'])

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

                        templateVars["multi_select"] = False
                        jsonVars = easy_jsonData['policies']
                        templateVars["var_description"] = jsonVars['vnic.PlacementSettings']['description']
                        templateVars["jsonVars"] = [x for x in jsonVars['vnic.PlacementSettings']['enum']]
                        templateVars["defaultVar"] = jsonVars['vnic.PlacementSettings']['default']
                        templateVars["varType"] = 'Slot Id'
                        templateVars["slot_id"] = variablesFromAPI(**templateVars)

                        if not templateVars["target_platform"] == 'FIAttached':
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            print(f'    The Uplink Port is the Adapter port on which the virtual interface will be created.')
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            for x in fabrics:
                                valid = False
                                while valid == False:
                                    question = input(f'What is the Uplink Port you want to Assign to Fabric {x}?  Range is 0-3.  [0]: ')
                                    if question == '':
                                        templateVars[f"uplink_port_{x}"] = 0
                                    if re.fullmatch(r'^[0-3]', str(question)):
                                        templateVars[f"uplink_port_{x}"] = question
                                        valid = validating.number_in_range(f'Fabric {x} PCI Uplink', templateVars[f"uplink_port_{x}"], 0, 3)
                                    else:
                                        print(f'\n-------------------------------------------------------------------------------------------\n')
                                        print(f'  Error!! Invalid Value.  Please enter 0 or 1.')
                                        print(f'\n-------------------------------------------------------------------------------------------\n')

                        jsonVars = jsonData['components']['schemas']['vnic.FcIf']['allOf'][1]['properties']
                        templateVars["var_description"] = jsonVars['Type']['description']
                        templateVars["jsonVars"] = sorted(jsonVars['Type']['enum'])
                        templateVars["defaultVar"] = jsonVars['Type']['default']
                        templateVars["varType"] = 'vHBA Type'
                        templateVars["vhba_type"] = variablesFromAPI(**templateVars)

                        templateVars["var_description"] = jsonVars['WwpnAddressType']['description']
                        templateVars["jsonVars"] = sorted(jsonVars['WwpnAddressType']['enum'])
                        templateVars["defaultVar"] = jsonVars['WwpnAddressType']['default']
                        templateVars["varType"] = 'WWPN Allocation Type'
                        templateVars["wwpn_allocation_type"] = variablesFromAPI(**templateVars)

                        if templateVars["target_platform"] == 'FIAttached':
                            templateVars[f'wwpn_pool_A'] = ''
                            templateVars[f'wwpn_pool_B'] = ''
                            templateVars[f'wwpn_static_A'] = ''
                            templateVars[f'wwpn_static_B'] = ''
                            if templateVars["wwpn_allocation_type"] == 'POOL':
                                policy_list = [
                                    'pools.wwpn_pools.wwpn_pool'
                                ]
                                templateVars["allow_opt_out"] = False
                                for x in fabrics:
                                    print(f'\n-------------------------------------------------------------------------------------------\n')
                                    print(f'  Select WWPN Pool for Fabric {x}:')
                                    print(f'\n-------------------------------------------------------------------------------------------\n')
                                    for policy in policy_list:
                                        policy_short = policy.split('.')[2]
                                        templateVars[f'{policy_short}_{x}'],policyData = policy_select_loop(jsonData, easy_jsonData, name_prefix, policy, **templateVars)
                                        templateVars.update(policyData)

                            else:
                                valid = False
                                while valid == False:
                                    for x in fabrics:
                                        templateVars["wwpn_static"] = input(f'What is the Static WWPN you would like to assign to Fabric {x}?  ')
                                    if not templateVars["wwpn_static"] == '':
                                        templateVars[f"wwpn_static_{x}"]
                                        valid = validating.wwxn_address(f'Fabric {x} WWPN Static', templateVars["wwpn_static"])

                        if templateVars["target_platform"] == 'FIAttached':
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
                                'wwpn_static':templateVars["wwpn_static_B"]
                            }
                        else:
                            vhba_fabric_a = {
                                'fibre_channel_adapter_policy':templateVars["fibre_channel_adapter_policy"],
                                'fibre_channel_network_policy':templateVars["fibre_channel_network_policy_A"],
                                'fibre_channel_qos_policy':templateVars["fibre_channel_qos_policy"],
                                'name':templateVars["name_A"],
                                'persistent_lun_bindings':templateVars["persistent_lun_bindings"],
                                'pci_link':templateVars["pci_link_A"],
                                'pci_order':templateVars["pci_order_A"],
                                'slot_id':templateVars["slot_id"],
                                'uplink_port':templateVars["uplink_port_A"],
                                'vhba_type':templateVars["vhba_type"],
                                'wwpn_allocation_type':templateVars["wwpn_allocation_type"],
                                'wwpn_pool':templateVars["wwpn_pool_A"],
                                'wwpn_static':templateVars["wwpn_static_A"]
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
                                'uplink_port':templateVars["uplink_port_B"],
                                'vhba_type':templateVars["vhba_type"],
                                'wwpn_allocation_type':templateVars["wwpn_allocation_type"],
                                'wwpn_pool':templateVars["wwpn_pool_B"],
                                'wwpn_static':templateVars["wwpn_static_B"]
                            }
                        print(vhba_fabric_a)
                        print(vhba_fabric_b)
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
                        if templateVars["target_platform"] == 'FIAttached':
                            print(f'   placement_switch_id          = "A"')
                        else:
                            print(f'   placement_uplink_port        = "{templateVars["uplink_port_A"]}"')
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
                        if templateVars["target_platform"] == 'FIAttached':
                            print(f'   placement_switch_id          = "B"')
                        else:
                            print(f'   placement_uplink_port        = "{templateVars["uplink_port_B"]}"')
                        print(f'   vhba_type                    = "{templateVars["vhba_type"]}"')
                        if templateVars["target_platform"] == 'FIAttached':
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
                    print(f'    description          = "{templateVars["descr"]}"')
                    print(f'    name                 = "{templateVars["name"]}"')
                    print(f'    target_platform      = "{templateVars["target_platform"]}"')
                    if templateVars["target_platform"] == 'FIAttached':
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
                                    print(f'        name                         = "{v}"')
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
                                elif k == 'uplink_port':
                                    print(f'        placement_uplink_port        = "{v}"')
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

    #========================================
    # SD Card Policy Module
    #========================================
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

    #========================================
    # Serial over LAN Policy Module
    #========================================
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
            print(f'  This wizard will save the configuraton for this section to the following file:')
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

    #========================================
    # SMTP Policy Module
    #========================================
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
            print(f'  This wizard will save the configuraton for this section to the following file:')
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

    #========================================
    # SNMP Policy Module
    #========================================
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
            print(f'  This wizard will save the configuraton for this section to the following file:')
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

                    valid = False
                    while valid == False:
                        templateVars["system_contact"] = input(f'Note: Enter a string up to 64 characters, such as an email address or a name and telephone number.\n'\
                            'What is the Contact person responsible for the SNMP implementation?  [UCS Admins]: ')
                        if templateVars["system_contact"] == '':
                            templateVars["system_contact"] = 'UCS Admins'
                        valid = validating.string_length('System Contact', templateVars["system_contact"], 1, 64)

                    valid = False
                    while valid == False:
                        templateVars["system_location"] = input(f'What is the Location of the host on which the SNMP agent (server) runs?  [Data Center]: ')
                        if templateVars["system_location"] == '':
                            templateVars["system_location"] = 'Data Center'
                        valid = validating.string_length('System Location', templateVars["system_location"], 1, 64)

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
                        templateVars["multi_select"] = False
                        jsonVars = jsonData['components']['schemas']['snmp.Policy']['allOf'][1]['properties']
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

                    templateVars["users"] = []
                    inner_loop_count = 1
                    snmp_loop = False
                    while snmp_loop == False:
                        question = input(f'Would you like to configure an SNMPv3 User?  Enter "Y" or "N" [Y]: ')
                        if question == '' or question == 'Y':
                            valid_users = False
                            while valid_users == False:
                                valid = False
                                while valid == False:
                                    snmp_user = input(f'What is your SNMPv3 username? ')
                                    if not snmp_user == '':
                                        valid = validating.snmp_string('SNMPv3 User', snmp_user)
                                    else:
                                        print(f'\n-------------------------------------------------------------------------------------------\n')
                                        print(f'  Error!! Invalid Value.  Please Re-enter the SNMPv3 Username.')
                                        print(f'\n-------------------------------------------------------------------------------------------\n')

                                templateVars["multi_select"] = False
                                jsonVars = jsonData['components']['schemas']['snmp.User']['allOf'][1]['properties']
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
                                    snmp_userx = {
                                        'auth_password':inner_loop_count,
                                        'auth_type':auth_type,
                                        'name':snmp_user,
                                        'privacy_password':inner_loop_count,
                                        'privacy_type':privacy_type,
                                        'security_level':security_level
                                    }
                                elif security_level == 'AuthNoPriv':
                                    snmp_userx = {
                                        'auth_password':inner_loop_count,
                                        'auth_type':auth_type,
                                        'name':snmp_user,
                                        'security_level':security_level
                                    }

                                # for k, v in os.environ.items():
                                #     print(f'key is {k}, and value is {v}')
                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                print(f'   auth_password    = "Sensitive"')
                                print(f'   auth_type        = "{auth_type}"')
                                if security_level == 'AuthPriv':
                                    print(f'   privacy_password = "Sensitive"')
                                    print(f'   privacy_type     = "{privacy_type}"')
                                print(f'   security_level   = "{security_level}"')
                                print(f'   snmp_user        = "{snmp_user}"')
                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                valid_confirm = False
                                while valid_confirm == False:
                                    confirm_v = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
                                    if confirm_v == 'Y' or confirm_v == '':
                                        templateVars["users"].append(snmp_userx)
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
                                        print(f'  Starting Remote Host Configuration Over.')
                                        print(f'\n-------------------------------------------------------------------------------------------\n')
                                        valid_confirm = True
                                    else:
                                        print(f'\n------------------------------------------------------\n')
                                        print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                                        print(f'\n------------------------------------------------------\n')

                        elif question == 'N':
                            snmp_loop = True
                        else:
                            print(f'\n------------------------------------------------------\n')
                            print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                            print(f'\n------------------------------------------------------\n')


                    snmp_user_list = []
                    if len(templateVars["users"]):
                        for item in templateVars["users"]:
                            for k, v in item.items():
                                if k == 'name':
                                    snmp_user_list.append(v)

                    templateVars["trap_destinations"] = []
                    inner_loop_count = 1
                    snmp_loop = False
                    while snmp_loop == False:
                        question = input(f'Would you like to configure SNMP Trap Destionations?  Enter "Y" or "N" [Y]: ')
                        if question == '' or question == 'Y':
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
                                    snmp_user = vars_from_list(snmp_user_list, **templateVars)
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
                                        templateVars["trap_destinations"].append(snmp_destination)
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

                        elif question == 'N':
                            snmp_loop = True
                        else:
                            print(f'\n------------------------------------------------------\n')
                            print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                            print(f'\n------------------------------------------------------\n')

                    templateVars["enabled"] = True
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    if templateVars["access_community_string"] == '':
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
                                    print(f'        community_string = "Sensitive"')
                                elif k == 'enabled':
                                    print(f'        enable           = {v}')
                                elif k == 'trap_type':
                                    print(f'        trap_type        = "{v}"')
                                elif k == 'port':
                                    print(f'        port             = {v}')
                                elif k == 'user':
                                    print(f'        user             = "{v}"')
                                elif k == 'version':
                                    print(f'        snmp_server      = "{v}"')
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
                    if templateVars["trap_community_string"] == '':
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

    #========================================
    # SSH Policy Module
    #========================================
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
            print(f'  This wizard will save the configuraton for this section to the following file:')
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

    #========================================
    # Storage Policy Module
    #========================================
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

    #========================================
    # Switch Control Policy Module
    #========================================
    def switch_control_policies(self, jsonData, easy_jsonData):
        name_prefix = self.name_prefix
        name_suffix = 'sw_ctrl'
        org = self.org
        policy_type = 'Switch Control Policy'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'switch_control_policies'

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  A Switch Control Policy will configure Unidirectional Link Detection Protocol and')
            print(f'  MAC Address Learning Settings for the UCS Domain Profile.')
            print(f'  We recommend the settings the wizard is setup to push.  So you will only be asked for')
            print(f'  the name and description for the Policy.  You only need one of these policies for')
            print(f'  Organization {org}.\n')
            print(f'  This wizard will save the configuraton for this section to the following file:')
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

                templateVars["mac_address_table_aging"] = 'Default'
                templateVars["mac_aging_time"] = 14500
                templateVars["udld_message_interval"] = 15
                templateVars["udld_recovery_action"] = "reset"
                templateVars["vlan_port_count_optimization"] = False

                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'    description                  = "{templateVars["descr"]}"')
                print(f'    mac_address_table_aging      = "{templateVars["mac_address_table_aging"]}"')
                print(f'    mac_aging_time               = {templateVars["mac_aging_time"]}')
                print(f'    name                         = "{templateVars["name"]}"')
                print(f'    udld_message_interval        = {templateVars["udld_message_interval"]}')
                print(f'    udld_recovery_action         = "{templateVars["udld_recovery_action"]}"')
                print(f'    vlan_port_count_optimization = {templateVars["vlan_port_count_optimization"]}')
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

    #========================================
    # Syslog Policy Module
    #========================================
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
            print(f'  This wizard will save the configuraton for this section to the following file:')
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
                    jsonVars = jsonData['components']['schemas']['syslog.LocalClientBase']['allOf'][1]['properties']
                    templateVars["var_description"] = jsonVars['MinSeverity']['description']
                    templateVars["jsonVars"] = sorted(jsonVars['MinSeverity']['enum'])
                    templateVars["defaultVar"] = jsonVars['MinSeverity']['default']
                    templateVars["varType"] = 'Syslog Local Minimum Severity'
                    templateVars["min_severity"] = variablesFromAPI(**templateVars)

                    templateVars["local_logging"] = {'file':{'min_severity':templateVars["min_severity"]}}

                    templateVars["remote_logging"] = {}
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
                                    templateVars['remote_logging'].update({'server1':remote_host})
                                if syslog_count == 2:
                                    templateVars['remote_logging'].update({'server2':remote_host})
                                if syslog_count == 1:
                                    valid_exit = False
                                    while valid_exit == False:
                                        remote_exit = input(f'Would You like to Configure another Remote Host?  Enter "Y" or "N" [Y]: ')
                                        if remote_exit == 'Y' or remote_exit == '':
                                            syslog_count += 1
                                            valid_confirm = True
                                            valid_exit = True
                                        elif remote_exit == 'N':
                                            syslog_loop = True
                                            valid_exit = True
                                        else:
                                            print(f'\n------------------------------------------------------\n')
                                            print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                                            print(f'\n------------------------------------------------------\n')

                                else:
                                    syslog_loop = True
                                    valid_confirm = True

                            elif confirm_host == 'N':
                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                print(f'  Starting Remote Host Configuration Over.')
                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                syslog_loop = True
                                valid_confirm = True
                            else:
                                print(f'\n------------------------------------------------------\n')
                                print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                                print(f'\n------------------------------------------------------\n')

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

    #========================================
    # System QoS Policy Module
    #========================================
    def system_qos_policies(self, jsonData, easy_jsonData):
        name_prefix = self.name_prefix
        name_suffix = 'qos'
        org = self.org
        policy_type = 'System QoS Policy'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'system_qos_policies'

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  A System QoS Policy will configure the QoS Policies for the UCS Domain Profile')
            print(f'  These Queues are represented by the following Priorities:')
            print(f'    - Platinum')
            print(f'    - Gold')
            print(f'    - FC')
            print(f'    - Silver')
            print(f'    - Bronze')
            print(f'    - Best Effort')
            print(f'  For the System MTU we recommend to set the MTU to Jumbo frames unless you are unable.')
            print(f'  to configure jumbo frames in your network.  Any traffic that is moving large')
            print(f'  amounts of packets through the network will be improved with Jumbo MTU support.')
            print(f'  Beyond the System MTU, we recommend you utilize the default parameters of this wizard.')
            print(f'  You only need one of these policies for Organization {org}.\n')
            print(f'  This wizard will save the configuraton for this section to the following file:')
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
                    mtu = input('Do you want to enable Jumbo MTU?  Enter "Y" or "N" [Y]: ')
                    if mtu == '' or mtu == 'Y':
                        templateVars["mtu"] = 9216
                        valid = True
                    elif mtu == 'N':
                        templateVars["mtu"] = 1500
                        valid = True
                    else:
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        print(f'  Error!! Invalid Option.  Please enter "Y" or "N".')
                        print(f'\n-------------------------------------------------------------------------------------------\n')

                domain_mtu = templateVars["mtu"]

                templateVars["Platinum"] = {
                    'bandwidth_percent':20,
                    'cos':5,
                    'mtu':templateVars["mtu"],
                    'multicast_optimize':False,
                    'packet_drop':False,
                    'priority':'Platinum',
                    'state':'Enabled',
                    'weight':10,
                }
                templateVars["Gold"] = {
                    'bandwidth_percent':18,
                    'cos':4,
                    'mtu':templateVars["mtu"],
                    'multicast_optimize':False,
                    'packet_drop':True,
                    'priority':'Gold',
                    'state':'Enabled',
                    'weight':9,
                }
                templateVars["FC"] = {
                    'bandwidth_percent':20,
                    'cos':3,
                    'mtu':2240,
                    'multicast_optimize':False,
                    'packet_drop':False,
                    'priority':'FC',
                    'state':'Enabled',
                    'weight':10,
                }
                templateVars["Silver"] = {
                    'bandwidth_percent':18,
                    'cos':2,
                    'mtu':templateVars["mtu"],
                    'multicast_optimize':False,
                    'packet_drop':True,
                    'priority':'Silver',
                    'state':'Enabled',
                    'weight':8,
                }
                templateVars["Bronze"] = {
                    'bandwidth_percent':14,
                    'cos':1,
                    'mtu':templateVars["mtu"],
                    'multicast_optimize':False,
                    'packet_drop':True,
                    'priority':'Bronze',
                    'state':'Enabled',
                    'weight':7,
                }
                templateVars["Best Effort"] = {
                    'bandwidth_percent':10,
                    'cos':255,
                    'mtu':templateVars["mtu"],
                    'multicast_optimize':False,
                    'packet_drop':True,
                    'priority':'Best Effort',
                    'state':'Enabled',
                    'weight':5,
                }

                templateVars["classes"] = []
                priorities = ['Platinum', 'Gold', 'FC', 'Silver', 'Bronze', 'Best Effort']

                for priority in priorities:
                    templateVars["classes"].append(templateVars[priority])
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'    description = "{templateVars["descr"]}"')
                print(f'    name        = "{templateVars["name"]}"')
                print('    classes = {')
                for item in templateVars["classes"]:
                    for k, v in item.items():
                        if k == 'priority':
                            print(f'      "{v}" = ''{')
                    for k, v in item.items():
                        if k == 'bandwidth_percent':
                            print(f'        bandwidth_percent  = {v}')
                        elif k == 'cos':
                            print(f'        cos                = {v}')
                        elif k == 'mtu':
                            print(f'        mtu                = {v}')
                        elif k == 'multicast_optimize':
                            print(f'        multicast_optimize = {v}')
                        elif k == 'packet_drop':
                            print(f'        packet_drop        = {v}')
                        elif k == 'state':
                            print(f'        state              = "{v}"')
                        elif k == 'weight':
                            print(f'        weight             = {v}')
                    print('      }')
                print('    }')
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

    #========================================
    # Thermal Policy Module
    #========================================
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
            print(f'  This wizard will save the configuraton for this section to the following file:')
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

    #========================================
    # UCS Chassis Profile Module
    #========================================
    def ucs_chassis_profiles(self, jsonData, easy_jsonData):
        name_prefix = self.name_prefix
        name_suffix = 'chassis'
        org = self.org
        policy_type = 'UCS Chassis Profile'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'ucs_chassis_profiles'

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
                        name = '%s' % (name_prefix)
                    else:
                        name = '%s_%s' % (org, name_suffix)

                    templateVars["name"] = policy_name(name, policy_type)
                    templateVars["descr"] = policy_descr(templateVars["name"], policy_type)

                    templateVars["multi_select"] = False
                    jsonVars = easy_jsonData['profiles']
                    templateVars["var_description"] = jsonVars['action']['description']
                    templateVars["jsonVars"] = sorted(jsonVars['action']['enum'])
                    templateVars["defaultVar"] = jsonVars['action']['default']
                    templateVars["varType"] = 'Action'
                    templateVars["action"] = variablesFromAPI(**templateVars)

                    valid = False
                    while valid == False:
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        print(f'  Note: If you do not have the Serial Number at this time you can manually add it to the:')
                        print(f'        - ucs_chassis_profiles/ucs_chassis_profiles.auto.tfvars file later.')
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        templateVars["serial_number"] = input('What is the Serial Number of the Chassis? [press enter to skip]: ')
                        if templateVars["serial_number"] == '':
                            valid = True
                        elif re.fullmatch(r'^[A-Z]{3}[2-3][\d]([0][1-9]|[1-4][0-9]|[5][1-3])[\dA-Z]{4}$', templateVars["serial_number"]):
                            valid = True
                        else:
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            print(f'  Error!! Invalid Serial Number.  "{templateVars["serial_number"]}" is not a valid serial.')
                            print(f'\n-------------------------------------------------------------------------------------------\n')

                    policy_list = [
                        'policies.imc_access_policies.imc_access_policy',
                        'policies.power_policies.power_policy',
                        'policies.snmp_policies.snmp_policy',
                        'policies.thermal_policies.thermal_policy'
                    ]
                    templateVars["allow_opt_out"] = True
                    for policy in policy_list:
                        policy_short = policy.split('.')[2]
                        templateVars[policy_short],policyData = policy_select_loop(jsonData, easy_jsonData, name_prefix, policy, **templateVars)
                        templateVars.update(policyData)

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'    action            = "No-op"')
                    if not templateVars["serial_number"] == '':
                        print(f'    assign_chassis    = True')
                    else:
                        print(f'    assign_chassis    = False')
                    print(f'    name              = "{templateVars["name"]}"')
                    print(f'    imc_access_policy = "{templateVars["imc_access_policy"]}"')
                    print(f'    power_policy      = "{templateVars["power_policy"]}"')
                    print(f'    serial_number     = "{templateVars["serial_number"]}"')
                    print(f'    snmp_policy       = "{templateVars["snmp_policy"]}"')
                    print(f'    thermal_policy    = "{templateVars["thermal_policy"]}"')
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

    #========================================
    # UCS Domain Profile Module
    #========================================
    def ucs_domain_profiles(self, jsonData, easy_jsonData, policy_prefix):
        name_prefix = self.name_prefix
        name_suffix = 'ucs'
        org = self.org
        policy_type = 'UCS Domain Profile'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'ucs_domain_profiles'

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
                        name = '%s' % (name_prefix)
                    else:
                        name = '%s_%s' % (org, name_suffix)

                    templateVars["name"] = policy_name(name, policy_type)
                    templateVars["descr"] = policy_descr(templateVars["name"], policy_type)

                    templateVars["multi_select"] = False
                    jsonVars = easy_jsonData['profiles']
                    templateVars["var_description"] = jsonVars['action']['description']
                    templateVars["jsonVars"] = sorted(jsonVars['action']['enum'])
                    templateVars["defaultVar"] = jsonVars['action']['default']
                    templateVars["varType"] = 'Action'
                    templateVars["action"] = variablesFromAPI(**templateVars)

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  Note: If you do not have the Serial Number at this time you can manually add it to the:')
                    print(f'        - ucs_domain_profiles/ucs_domain_profiles.auto.tfvars file later.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid = False
                    while valid == False:
                        templateVars["serial_number_fabric_a"] = input('What is the Serial Number of Fabric A? [press enter to skip]: ')
                        if templateVars["serial_number_fabric_a"] == '':
                            valid = True
                        elif re.fullmatch(r'^[A-Z]{3}[2-3][\d]([0][1-9]|[1-4][0-9]|[5][1-3])[\dA-Z]{4}$', templateVars["serial_number_fabric_a"]):
                            valid = True
                        else:
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            print(f'  Error!! Invalid Serial Number.  "{templateVars["serial_number_fabric_a"]}" is not a valid serial.')
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid = False
                    while valid == False:
                        templateVars["serial_number_fabric_b"] = input('What is the Serial Number of Fabric B? [press enter to skip]: ')
                        if templateVars["serial_number_fabric_b"] == '':
                            valid = True
                        elif re.fullmatch(r'^[A-Z]{3}[2-3][\d]([0][1-9]|[1-4][0-9]|[5][1-3])[\dA-Z]{4}$', templateVars["serial_number_fabric_b"]):
                            valid = True
                        else:
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            print(f'  Error!! Invalid Serial Number.  "{templateVars["serial_number_fabric_b"]}" is not a valid serial.')
                            print(f'\n-------------------------------------------------------------------------------------------\n')

                    policy_list = [
                        'policies.network_connectivity_policies.network_connectivity_policy',
                        'policies.ntp_policies.ntp_policy',
                        'policies.snmp_policies.snmp_policy',
                        'policies.switch_control_policies.switch_control_policy',
                        'policies.syslog_policies.syslog_policy',
                        'policies.system_qos_policies.system_qos_policy'
                    ]
                    templateVars["allow_opt_out"] = True
                    for policy in policy_list:
                        policy_short = policy.split('.')[2]
                        if re.search(r'(switch_control|system_qos)', policy):
                            templateVars[policy_short],policyData = policy_select_loop(jsonData, easy_jsonData, name_prefix, policy, **templateVars)
                        else:
                            templateVars[policy_short],policyData = policy_select_loop(jsonData, easy_jsonData, policy_prefix, policy, **templateVars)
                        templateVars.update(policyData)

                    policy_list = [
                        'policies.port_policies.port_policy',
                        'policies_vlans.vlan_policies.vlan_policy',
                        'policies.vsan_policies.vsan_policy'
                    ]
                    templateVars["allow_opt_out"] = False
                    for policy in policy_list:
                        policy_long = policy.split('.')[1]
                        policy_short = policy.split('.')[2]
                        x = policy_short.split('_')
                        policy_description = []
                        for y in x:
                            y = y.capitalize()
                            policy_description.append(y)
                        policy_description = " ".join(policy_description)

                        templateVars[policy_long] = {}
                        # templateVars["policy"] = '%s Fabric A' % (policy_description)
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        print(f'  !!! Select the {policy_description} for Fabric A !!!')
                        fabric_a,policyData = policy_select_loop(jsonData, easy_jsonData, name_prefix, policy, **templateVars)
                        # templateVars["policy"] = '%s Fabric B' % (policy_description)
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        print(f'  !!! Select the {policy_description} for Fabric B !!!')
                        fabric_b,policyData = policy_select_loop(jsonData, easy_jsonData, name_prefix, policy, **templateVars)
                        templateVars[policy_long].update({'fabric_a':fabric_a})
                        templateVars[policy_long].update({'fabric_b':fabric_b})
                        if policy_long == 'port_policies':
                            device_model_a = policyData['port_policies'][0][fabric_a][0]['device_model']
                            device_model_b = policyData['port_policies'][0][fabric_b][0]['device_model']
                            if not device_model_a == device_model_b:
                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                print(f'  !!! Error.  Device Model for the port Policies does not match !!!')
                                print(f'  Fabric A Port Policy device_model is {device_model_a}.')
                                print(f'  Fabric B Port Policy device_model is {device_model_b}.')
                                print(f'  The script is going to set the device_model to match Fabric A for now but you should.')
                                print(f'  either reject this configuration assuming you mistakenly chose non-matching port policies.')
                                print(f'  or re-run the port-policy wizard again to correct the configuration.')
                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                templateVars["device_model"] = device_model_a
                            else:
                                templateVars["device_model"] = device_model_a


                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'    action                      = "No-op"')
                    if not (templateVars["serial_number_fabric_a"] == '' and templateVars["serial_number_fabric_a"] == ''):
                        print(f'    assign_switches             = True')
                    else:
                        print(f'    assign_switches             = False')
                    print(f'    device_model                = "{templateVars["device_model"]}"')
                    print(f'    name                        = "{templateVars["name"]}"')
                    print(f'    network_connectivity_policy = "{templateVars["network_connectivity_policy"]}"')
                    print(f'    ntp_policy                  = "{templateVars["ntp_policy"]}"')
                    print(f'    port_policy_fabric_a        = "{templateVars["port_policies"]["fabric_a"]}"')
                    print(f'    port_policy_fabric_b        = "{templateVars["port_policies"]["fabric_b"]}"')
                    print(f'    serial_number_fabric_a      = "{templateVars["serial_number_fabric_a"]}"')
                    print(f'    serial_number_fabric_b      = "{templateVars["serial_number_fabric_b"]}"')
                    print(f'    snmp_policy                 = "{templateVars["snmp_policy"]}"')
                    print(f'    switch_control_policy       = "{templateVars["switch_control_policy"]}"')
                    print(f'    syslog_policy               = "{templateVars["syslog_policy"]}"')
                    print(f'    system_qos_policy           = "{templateVars["system_qos_policy"]}"')
                    print(f'    vlan_policy_fabric_a        = "{templateVars["vlan_policies"]["fabric_a"]}"')
                    print(f'    vlan_policy_fabric_b        = "{templateVars["vlan_policies"]["fabric_b"]}"')
                    print(f'    vsan_policy_fabric_a        = "{templateVars["vsan_policies"]["fabric_a"]}"')
                    print(f'    vsan_policy_fabric_b        = "{templateVars["vsan_policies"]["fabric_b"]}"')
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

    #========================================
    # UCS Server Profile Module
    #========================================
    def ucs_server_profiles(self, jsonData, easy_jsonData):
        name_prefix = self.name_prefix
        name_suffix = 'server'
        org = self.org
        policy_type = 'UCS Server Profile'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'ucs_server_profiles'

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            policy_loop = False
            while policy_loop == False:

                if not name_prefix == '':
                    name = '%s_%s' % (name_prefix, name_suffix)
                else:
                    name = '%s_%s' % (org, name_suffix)

                templateVars["name"] = policy_name(name, policy_type)
                templateVars["descr"] = policy_descr(templateVars["name"], policy_type)

                templateVars["allow_opt_out"] = False
                templateVars["multi_select"] = False
                jsonVars = easy_jsonData['profiles']
                templateVars["var_description"] = jsonVars['action']['description']
                templateVars["jsonVars"] = sorted(jsonVars['action']['enum'])
                templateVars["defaultVar"] = jsonVars['action']['default']
                templateVars["varType"] = 'Action'
                templateVars["action"] = variablesFromAPI(**templateVars)


                jsonVars = jsonData['components']['schemas']['server.Profile']['allOf'][1]['properties']
                templateVars["var_description"] = jsonVars['ServerAssignmentMode']['description']
                templateVars["jsonVars"] = sorted(jsonVars['ServerAssignmentMode']['enum'])
                templateVars["defaultVar"] = jsonVars['ServerAssignmentMode']['default']
                templateVars["varType"] = 'Server Assignment Mode'
                templateVars["server_assignment_mode"] = variablesFromAPI(**templateVars)

                if templateVars["server_assignment_mode"] == 'Static':
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  Note: If you do not have the Serial Number at this time you can manually add it to the:')
                    print(f'        - ucs_server_profiles/ucs_server_profiles.auto.tfvars file later.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    templateVars["Description"] = 'Serial Number of the Physical Compute Resource to assign to the Profile.'
                    templateVars["varDefault"] = ''
                    templateVars["varInput"] = 'What is the Serial Number of the Server? [press enter to skip]:'
                    templateVars["varName"] = 'Serial Number'
                    templateVars["varRegex"] = '^[A-Z]{3}[2-3][\\d]([0][1-9]|[1-4][0-9]|[5][1-3])[\\dA-Z]{4}$'
                    templateVars["minLength"] = 11
                    templateVars["maxLength"] = 11
                    templateVars['serial_number'] = varStringLoop(**templateVars)
                elif templateVars["server_assignment_mode"] == 'Pool':
                    policy_list = [
                        'pools.resource_pools.resource_pool'
                    ]
                    templateVars["allow_opt_out"] = False
                    for policy in policy_list:
                        policy_short = policy.split('.')[2]
                        templateVars[policy_short],policyData = policy_select_loop(jsonData, easy_jsonData, name_prefix, policy, **templateVars)
                        templateVars.update(policyData)
                        server_template = True
                        valid = True

                valid = False
                while valid == False:
                    server_template = input('Do you want to Associate to a UCS Server Profile Template?  Enter "Y" or "N" [Y]: ')
                    if server_template == '' or server_template == 'Y':
                        policy_list = [
                            'ucs_server_profiles.ucs_server_profile_templates.ucs_server_profile_template'
                        ]
                        templateVars["allow_opt_out"] = False
                        for policy in policy_list:
                            policy_short = policy.split('.')[2]
                            templateVars[policy_short],policyData = policy_select_loop(jsonData, easy_jsonData, name_prefix, policy, **templateVars)
                            templateVars.update(policyData)
                            server_template = True
                            valid = True
                    elif server_template == 'N':
                        server_template = False
                        valid = True
                    else:
                        print(f'\n------------------------------------------------------\n')
                        print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                        print(f'\n------------------------------------------------------\n')

                if server_template == False:
                    templateVars["multi_select"] = False
                    jsonVars = jsonData['components']['schemas']['server.BaseProfile']['allOf'][1]['properties']
                    templateVars["var_description"] = jsonVars['TargetPlatform']['description']
                    templateVars["jsonVars"] = sorted(jsonVars['TargetPlatform']['enum'])
                    templateVars["defaultVar"] = jsonVars['TargetPlatform']['default']
                    templateVars["varType"] = 'Target Platform'
                    templateVars["target_platform"] = variablesFromAPI(**templateVars)

                    #___________________________________________________________________________
                    #
                    # Policies On Hold for Right Now
                    # 'policies.certificate_management_policies.certificate_management_policy',
                    #___________________________________________________________________________
                    if templateVars["target_platform"] == 'FIAttached':
                        policy_list = [
                            #___________________________
                            #
                            # Compute Configuration
                            #___________________________
                            'pools.uuid_pools.uuid_pool',
                            'policies.bios_policies.bios_policy',
                            'policies.boot_order_policies.boot_order_policy',
                            'policies.power_policies.power_policy',
                            'policies.virtual_media_policies.virtual_media_policy',
                            #___________________________
                            #
                            # Management Configuration
                            #___________________________
                            'policies.imc_access_policies.imc_access_policy',
                            'policies.ipmi_over_lan_policies.ipmi_over_lan_policy',
                            'policies.local_user_policies.local_user_policy',
                            'policies.serial_over_lan_policies.serial_over_lan_policy',
                            'policies.snmp_policies.snmp_policy',
                            'policies.syslog_policies.syslog_policy',
                            'policies.virtual_kvm_policies.virtual_kvm_policy',
                            #___________________________
                            #
                            # Storage Configuration
                            #___________________________
                            'policies.sd_card_policies.sd_card_policy',
                            'policies.storage_policies.storage_policy',
                            #___________________________
                            #
                            # Network Configuration
                            #___________________________
                            'policies.lan_connectivity_policies.lan_connectivity_policy',
                            'policies.san_connectivity_policies.san_connectivity_policy',
                        ]
                    elif templateVars["target_platform"] == 'Standalone':
                        policy_list = [
                            #___________________________
                            #
                            # Compute Configuration
                            #___________________________
                            'policies.bios_policies.bios_policy',
                            'policies.boot_order_policies.boot_order_policy',
                            'policies.persistent_memory_policies.persistent_memory_policy',
                            'policies.virtual_media_policies.virtual_media_policy',
                            #___________________________
                            #
                            # Management Configuration
                            #___________________________
                            'policies.device_connector_policies.device_connector_policy',
                            'policies.ipmi_over_lan_policies.ipmi_over_lan_policy',
                            'policies.ldap_policies_policies.ldap_policy',
                            'policies.local_user_policies.local_user_policy',
                            'policies.network_connectivity_policies.network_connectivity_policy',
                            'policies.ntp_policies.ntp_policy',
                            'policies.serial_over_lan_policies.serial_over_lan_policy',
                            'policies.smtp_policies.smtp_policy',
                            'policies.snmp_policies.snmp_policy',
                            'policies.ssh_policies.ssh_policy',
                            'policies.syslog_policies.syslog_policy',
                            'policies.virtual_kvm_policies.virtual_kvm_policy',
                            #___________________________
                            #
                            # Storage Configuration
                            #___________________________
                            'policies.sd_card_policies.sd_card_policy',
                            'policies.storage_policies.storage_policy',
                            #___________________________
                            #
                            # Network Configuration
                            #___________________________
                            'policies.adapter_configuration_policies.adapter_configuration_policy',
                            'policies.lan_connectivity_policies.lan_connectivity_policy',
                            'policies.san_connectivity_policies.san_connectivity_policy',
                        ]
                    templateVars["allow_opt_out"] = True
                    for policy in policy_list:
                        policy_short = policy.split('.')[2]
                        templateVars[policy_short],policyData = policy_select_loop(jsonData, easy_jsonData, name_prefix, policy, **templateVars)
                        templateVars.update(policyData)

                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'    action          = "{templateVars["action"]}"')
                print(f'    description     = "{templateVars["descr"]}"')
                print(f'    name            = "{templateVars["name"]}"')
                if templateVars["server_assignment_mode"] == 'Pool':
                    print(f'    resource_pool   = {templateVars["resource_pool"]}')
                if templateVars["server_assignment_mode"] == 'Static':
                    print(f'    serial_number   = "{templateVars["serial_number"]}"')
                if server_template == True:
                    print(f'    ucs_server_profile_template = "{templateVars["ucs_server_profile_template"]}"')
                if server_template == False:
                    print(f'    target_platform = "{templateVars["target_platform"]}"')
                if server_template == False:
                    print(f'    #___________________________"')
                    print(f'    #')
                    print(f'    # Compute Configuration')
                    print(f'    #___________________________"')
                    if not templateVars["static_uuid_address"] == '':
                        print(f'    static_uuid_address        = "{templateVars["static_uuid_address"]}"')
                    if not templateVars["uuid_pool"] == '':
                        print(f'    uuid_pool                  = "{templateVars["uuid_pool"]}"')
                    print(f'    bios_policy                = "{templateVars["bios_policy"]}"')
                    print(f'    boot_order_policy          = "{templateVars["boot_order_policy"]}"')
                    if templateVars["target_platform"] == 'Standalone':
                        print(f'    persistent_memory_policies = "{templateVars["persistent_memory_policies"]}"')
                    if templateVars["target_platform"] == 'FIAttached':
                        print(f'    power_policy               = "{templateVars["power_policy"]}"')
                    print(f'    virtual_media_policy       = "{templateVars["virtual_media_policy"]}"')
                    print(f'    #___________________________"')
                    print(f'    #')
                    print(f'    # Management Configuration')
                    print(f'    #___________________________"')
                    # if target_platform == 'FIAttached':
                    #     print(f'    certificate_management_policy = "{templateVars["pcertificate_management_policy"]}"')
                    if templateVars["target_platform"] == 'Standalone':
                        print(f'    device_connector_policies     = "{templateVars["device_connector_policies"]}"')
                    if templateVars["target_platform"] == 'FIAttached':
                        print(f'    imc_access_policy             = "{templateVars["imc_access_policy"]}"')
                    print(f'    ipmi_over_lan_policy          = "{templateVars["ipmi_over_lan_policy"]}"')
                    if templateVars["target_platform"] == 'Standalone':
                        print(f'    ldap_policies                 = "{templateVars["ldap_policies"]}"')
                    print(f'    local_user_policy             = "{templateVars["local_user_policy"]}"')
                    if templateVars["target_platform"] == 'Standalone':
                        print(f'    network_connectivity_policy   = "{templateVars["network_connectivity_policy"]}"')
                    if templateVars["target_platform"] == 'Standalone':
                        print(f'    ntp_policy                    = "{templateVars["ntp_policy"]}"')
                    print(f'    serial_over_lan_policy        = "{templateVars["serial_over_lan_policy"]}"')
                    if templateVars["target_platform"] == 'Standalone':
                        print(f'    smtp_policy                   = "{templateVars["smtp_policy"]}"')
                    print(f'    snmp_policy                   = "{templateVars["snmp_policy"]}"')
                    if templateVars["target_platform"] == 'Standalone':
                        print(f'    ssh_policy                    = "{templateVars["ssh_policy"]}"')
                    print(f'    syslog_policy                 = "{templateVars["syslog_policy"]}"')
                    print(f'    virtual_kvm_policy            = "{templateVars["virtual_kvm_policy"]}"')
                    print(f'    #___________________________"')
                    print(f'    #')
                    print(f'    # Storage Configuration')
                    print(f'    #___________________________"')
                    print(f'    sd_card_policy = "{templateVars["sd_card_policy"]}"')
                    print(f'    storage_policy = "{templateVars["storage_policy"]}"')
                    print(f'    #___________________________"')
                    print(f'    #')
                    print(f'    # Network Configuration')
                    print(f'    #___________________________"')
                    if templateVars["target_platform"] == 'Standalone':
                        print(f'    adapter_configuration_policy = "{templateVars["adapter_configuration_policy"]}"')
                    print(f'    lan_connectivity_policy      = "{templateVars["lan_connectivity_policy"]}"')
                    print(f'    san_connectivity_policy      = "{templateVars["san_connectivity_policy"]}"')
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

    #========================================
    # UCS Server Profile Template Module
    #========================================
    def ucs_server_profile_templates(self, jsonData, easy_jsonData):
        name_prefix = self.name_prefix
        name_suffix = 'template'
        org = self.org
        policy_type = 'UCS Server Profile Template'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'ucs_server_profile_templates'

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

                    templateVars["multi_select"] = False
                    jsonVars = jsonData['components']['schemas']['server.BaseProfile']['allOf'][1]['properties']
                    templateVars["var_description"] = jsonVars['TargetPlatform']['description']
                    templateVars["jsonVars"] = sorted(jsonVars['TargetPlatform']['enum'])
                    templateVars["defaultVar"] = jsonVars['TargetPlatform']['default']
                    templateVars["varType"] = 'Target Platform'
                    templateVars["target_platform"] = variablesFromAPI(**templateVars)

                    #___________________________________________________________________________
                    #
                    # Policies On Hold for Right Now
                    # 'policies.certificate_management_policies.certificate_management_policy',
                    #___________________________________________________________________________
                    if templateVars["target_platform"] == 'FIAttached':
                        policy_list = [
                            #___________________________
                            #
                            # Compute Configuration
                            #___________________________
                            'pools.uuid_pools.uuid_pool'
                            'policies.bios_policies.bios_policy',
                            'policies.boot_order_policies.boot_order_policy',
                            'policies.power_policies.power_policy',
                            'policies.virtual_media_policies.virtual_media_policy',
                            #___________________________
                            #
                            # Management Configuration
                            #___________________________
                            'policies.imc_access_policies.imc_access_policy',
                            'policies.ipmi_over_lan_policies.ipmi_over_lan_policy',
                            'policies.local_user_policies.local_user_policy',
                            'policies.serial_over_lan_policies.serial_over_lan_policy',
                            'policies.snmp_policies.snmp_policy',
                            'policies.syslog_policies.syslog_policy',
                            'policies.virtual_kvm_policies.virtual_kvm_policy',
                            #___________________________
                            #
                            # Storage Configuration
                            #___________________________
                            'policies.sd_card_policies.sd_card_policy',
                            'policies.storage_policies.storage_policy',
                            #___________________________
                            #
                            # Network Configuration
                            #___________________________
                            'policies.lan_connectivity_policies.lan_connectivity_policy',
                            'policies.san_connectivity_policies.san_connectivity_policy',
                        ]
                    elif templateVars["target_platform"] == 'Standalone':
                        policy_list = [
                            #___________________________
                            #
                            # Compute Configuration
                            #___________________________
                            'policies.bios_policies.bios_policy',
                            'policies.boot_order_policies.boot_order_policy',
                            'policies.persistent_memory_policies.persistent_memory_policy',
                            'policies.virtual_media_policies.virtual_media_policy',
                            #___________________________
                            #
                            # Management Configuration
                            #___________________________
                            'policies.device_connector_policies.device_connector_policy',
                            'policies.ipmi_over_lan_policies.ipmi_over_lan_policy',
                            'policies.ldap_policies_policies.ldap_policy',
                            'policies.local_user_policies.local_user_policy',
                            'policies.network_connectivity_policies.network_connectivity_policy',
                            'policies.ntp_policies.ntp_policy',
                            'policies.serial_over_lan_policies.serial_over_lan_policy',
                            'policies.smtp_policies.smtp_policy',
                            'policies.snmp_policies.snmp_policy',
                            'policies.ssh_policies.ssh_policy',
                            'policies.syslog_policies.syslog_policy',
                            'policies.virtual_kvm_policies.virtual_kvm_policy',
                            #___________________________
                            #
                            # Storage Configuration
                            #___________________________
                            'policies.sd_card_policies.sd_card_policy',
                            'policies.storage_policies.storage_policy',
                            #___________________________
                            #
                            # Network Configuration
                            #___________________________
                            'policies.adapter_configuration_policies.adapter_configuration_policy',
                            'policies.lan_connectivity_policies.lan_connectivity_policy',
                            'policies.san_connectivity_policies.san_connectivity_policy',
                        ]
                    templateVars["allow_opt_out"] = True
                    for policy in policy_list:
                        policy_short = policy.split('.')[2]
                        templateVars[policy_short],policyData = policy_select_loop(jsonData, easy_jsonData, name_prefix, policy, **templateVars)
                        templateVars.update(policyData)

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'    description     = "{templateVars["descr"]}"')
                    print(f'    name            = "{templateVars["name"]}"')
                    print(f'    target_platform = "{templateVars["target_platform"]}"')
                    print(f'    #___________________________"')
                    print(f'    #')
                    print(f'    # Compute Configuration')
                    print(f'    #___________________________"')
                    if templateVars["target_platform"] == 'FIAttached':
                        print(f'    uuid_pool                  = "{templateVars["uuid_pool"]}"')
                    print(f'    bios_policy                = "{templateVars["bios_policy"]}"')
                    print(f'    boot_order_policy          = "{templateVars["boot_order_policy"]}"')
                    if templateVars["target_platform"] == 'Standalone':
                        print(f'    persistent_memory_policies = "{templateVars["persistent_memory_policies"]}"')
                    if templateVars["target_platform"] == 'FIAttached':
                        print(f'    power_policy               = "{templateVars["power_policy"]}"')
                    print(f'    virtual_media_policy       = "{templateVars["virtual_media_policy"]}"')
                    print(f'    #___________________________"')
                    print(f'    #')
                    print(f'    # Management Configuration')
                    print(f'    #___________________________"')
                    # if target_platform == 'FIAttached':
                    #     print(f'    certificate_management_policy = "{templateVars["certificate_management_policy"]}"')
                    if templateVars["target_platform"] == 'Standalone':
                        print(f'    device_connector_policies     = "{templateVars["device_connector_policies"]}"')
                    if templateVars["target_platform"] == 'FIAttached':
                        print(f'    imc_access_policy             = "{templateVars["imc_access_policy"]}"')
                    print(f'    ipmi_over_lan_policy          = "{templateVars["ipmi_over_lan_policy"]}"')
                    if templateVars["target_platform"] == 'Standalone':
                        print(f'    ldap_policies                 = "{templateVars["ldap_policies"]}"')
                    print(f'    local_user_policy             = "{templateVars["local_user_policy"]}"')
                    if templateVars["target_platform"] == 'Standalone':
                        print(f'    network_connectivity_policy   = "{templateVars["network_connectivity_policy"]}"')
                    if templateVars["target_platform"] == 'Standalone':
                        print(f'    ntp_policy                    = "{templateVars["ntp_policy"]}"')
                    print(f'    serial_over_lan_policy        = "{templateVars["serial_over_lan_policy"]}"')
                    if templateVars["target_platform"] == 'Standalone':
                        print(f'    smtp_policy                   = "{templateVars["smtp_policy"]}"')
                    print(f'    snmp_policy                   = "{templateVars["snmp_policy"]}"')
                    if templateVars["target_platform"] == 'Standalone':
                        print(f'    ssh_policy                    = "{templateVars["ssh_policy"]}"')
                    print(f'    syslog_policy                 = "{templateVars["syslog_policy"]}"')
                    print(f'    virtual_kvm_policy            = "{templateVars["virtual_kvm_policy"]}"')
                    print(f'    #___________________________"')
                    print(f'    #')
                    print(f'    # Storage Configuration')
                    print(f'    #___________________________"')
                    print(f'    sd_card_policy = "{templateVars["sd_card_policy"]}"')
                    print(f'    storage_policy = "{templateVars["storage_policy"]}"')
                    print(f'    #___________________________"')
                    print(f'    #')
                    print(f'    # Network Configuration')
                    print(f'    #___________________________"')
                    if templateVars["target_platform"] == 'Standalone':
                        print(f'    adapter_configuration_policy = "{templateVars["adapter_configuration_policy"]}"')
                    print(f'    lan_connectivity_policy      = "{templateVars["lan_connectivity_policy"]}"')
                    print(f'    san_connectivity_policy      = "{templateVars["san_connectivity_policy"]}"')
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

    #========================================
    # UUID Pools Module
    #========================================
    def uuid_pools(self, jsonData, easy_jsonData):
        name_prefix = self.name_prefix
        name_suffix = 'uuid_pool'
        org = self.org
        policy_type = 'UUID Pool'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'uuid_pools'

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  The Universally Unique Identifier (UUID) are written in 5 groups of hexadecimal digits')
            print(f'  separated by hyphens.  The length of each group is: 8-4-4-4-12. UUIDs are fixed length.')
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

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  Assignment order decides the order in which the next identifier is allocated.')
                    print(f'    1. default - (Intersight Default) Assignment order is decided by the system.')
                    print(f'    2. sequential - (Recommended) Identifiers are assigned in a sequential order.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid = False
                    while valid == False:
                        templateVars["assignment_order"] = input('Specify the Index for the value to select [2]: ')
                        if templateVars["assignment_order"] == '' or templateVars["assignment_order"] == '2':
                            templateVars["assignment_order"] = 'sequential'
                            valid = True
                        elif templateVars["assignment_order"] == '1':
                            templateVars["assignment_order"] = 'default'
                            valid = True
                        else:
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            print(f'  Error!! Invalid Option.  Please Select a valid option from the List.')
                            print(f'\n-------------------------------------------------------------------------------------------\n')

                    valid = False
                    while valid == False:
                        templateVars['prefix'] = input(f'\nWhat is the UUID Prefix you would like to assign to the Pool?  [000025B5-0000-0000]: ')
                        if templateVars['prefix'] == '':
                            templateVars['prefix'] = '000025B5-0000-0000'
                        valid = validating.uuid_prefix('UUID Pool From', templateVars['prefix'])

                    valid = False
                    while valid == False:
                        pool_from = input(f'\nWhat is the first Suffix in the Block?  [0000-000000000000]: ')
                        if pool_from == '':
                            pool_from = '0000-000000000000'
                        valid = validating.uuid_suffix('UUID Pool From', pool_from)

                    valid = False
                    while valid == False:
                        pool_size = input(f'\nWhat is the size of the Block?  [512]: ')
                        if pool_size == '':
                            pool_size = '512'
                        valid = validating.number_in_range('UUID Pool Size', pool_size, 1, 1000)

                    templateVars["uuid_blocks"] = [
                        {
                            'from':pool_from,
                            'size':pool_size
                        }
                    ]
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'    assignment_order = "{templateVars["assignment_order"]}"')
                    print(f'    description      = "{templateVars["descr"]}"')
                    print(f'    name             = "{templateVars["name"]}"')
                    print(f'    prefix           = "{templateVars["prefix"]}"')
                    print(f'    uuid_blocks = [')
                    for i in templateVars["uuid_blocks"]:
                        print(f'      ''{')
                        for k, v in i.items():
                            if k == 'from':
                                print(f'        from   = {v}')
                            elif k == 'size':
                                print(f'        size   = {v}')
                        print(f'      ''}')
                    print(f'    ]')
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

    #========================================
    # Virtual KVM Policy Module
    #========================================
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
            print(f'  This wizard will save the configuraton for this section to the following file:')
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

    #========================================
    # Virtual Media Policy Policy Module
    #========================================
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
            print(f'  This wizard will save the configuraton for this section to the following file:')
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

    #========================================
    # VLAN Policy Module
    #========================================
    def vlan_policies(self, jsonData, easy_jsonData):
        vlan_policies_vlans = []
        name_prefix = self.name_prefix
        name_suffix = 'vlans'
        org = self.org
        policy_type = 'VLAN Policy'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'vlan_policies'

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  A {policy_type} will define the VLANs Assigned to the Fabric Interconnects.')
            print(f'  The vlan list can be in the format of:')
            print(f'     5 - Single VLAN')
            print(f'     1-10 - Range of VLANs')
            print(f'     1,2,3,4,5,11,12,13,14,15 - List of VLANs')
            print(f'     1-10,20-30 - Ranges and Lists of VLANs')
            print(f'  When configuring a VLAN List or Range the name will be used as a prefix in the format of:')
            print('     {name}-vlXXXX')
            print(f'  Where XXXX would be 0001 for vlan 1, 0100 for vlan 100, and 4094 for vlan 4094.')
            print(f'  If you want to Assign a Native VLAN Make sure it is in the vlan list for this wizard.')
            print(f'  IMPORTANT NOTE: You can only have one Native VLAN for the Fabric at this time,')
            print(f'                  as Disjoint Layer 2 is not yet supported.\n')
            print(f'  This wizard will save the configuraton for this section to the following file:')
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
                templateVars["auto_allow_on_uplinks"] = True

                valid = False
                while valid == False:
                    vlan_list = '%s' % (input(f'Enter the VLAN or List of VLANs to add to {templateVars["name"]}: '))
                    if not vlan_list == '':
                        vlan_list_expanded = vlan_list_full(vlan_list)
                        valid_vlan = True
                        for vlan in vlan_list_expanded:
                            valid_vlan = validating.number_in_range('VLAN ID', vlan, 1, 4094)
                            if valid_vlan == False:
                                break
                        native_count = 0
                        native_vlan = ''
                        native_name = ''
                        if valid_vlan == True:
                            valid_name = False
                            while valid_name == False:
                                if len(vlan_list_expanded) == 1:
                                    vlan_name = '%s' % (input(f'Enter the Name you want to assign to "{vlan_list}": '))
                                    valid_name = validating.name_rule('VLAN Name', vlan_name, 1, 62)
                                else:
                                    vlan_name = '%s' % (input(f'Enter the Prefix Name you want to assign to "{vlan_list}": '))
                                    valid_name = validating.name_rule('VLAN Name', vlan_name, 1, 55)
                            native_vlan = input('Do you want to configure one of the VLANs as a Native VLAN? [press enter to skip]:')
                        if not native_vlan == '' and valid_vlan == True:
                            for vlan in vlan_list_expanded:
                                if int(native_vlan) == int(vlan):
                                    native_count = 1
                            if native_count == 1:
                                valid_name = False
                                while valid_name == False:
                                    native_name = '%s' % (input(f'Enter the Name to assign to the Native VLAN {native_vlan}.  [default]: '))
                                    if native_name == '':
                                        native_name = 'default'
                                    valid_name = validating.name_rule('VLAN Name', vlan_name, 1, 62)
                                valid = True
                            else:
                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                print(f'  Error!! The Native VLAN was not in the Allowed List.')
                                print(f'\n-------------------------------------------------------------------------------------------\n')

                        elif valid_vlan == True:
                            valid = True
                    else:
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        print(f'  The allowed vlan list can be in the format of:')
                        print(f'     5 - Single VLAN')
                        print(f'     1-10 - Range of VLANs')
                        print(f'     1,2,3,4,5,11,12,13,14,15 - List of VLANs')
                        print(f'     1-10,20-30 - Ranges and Lists of VLANs')
                        print(f'\n-------------------------------------------------------------------------------------------\n')

                policy_list = [
                    'policies_vlans.multicast_policies.multicast_policy'
                ]
                templateVars["allow_opt_out"] = False
                for policy in policy_list:
                    policy_short = policy.split('.')[2]
                    templateVars[policy_short],policyData = policy_select_loop(jsonData, easy_jsonData, name_prefix, policy, **templateVars)
                    templateVars.update(policyData)

                if not native_vlan == '' and len(vlan_list) > 1:
                    templateVars["vlans"] = [
                        {
                            'auto_allow_on_uplinks':True,
                            'id':native_vlan,
                            'multicast_policy':templateVars["multicast_policy"],
                            'name':native_name,
                            'native_vlan':True
                        },
                        {
                            'auto_allow_on_uplinks':True,
                            'id':vlan_list,
                            'multicast_policy':templateVars["multicast_policy"],
                            'name':vlan_name,
                            'native_vlan':False
                        }
                    ]
                elif not native_vlan == '' and len(vlan_list) == 1:
                    templateVars["vlans"] = [
                        {
                            'auto_allow_on_uplinks':True,
                            'id':native_vlan,
                            'multicast_policy':templateVars["multicast_policy"],
                            'name':native_name,
                            'native_vlan':True
                        }
                    ]
                else:
                    templateVars["vlans"] = [
                        {
                            'auto_allow_on_uplinks':True,
                            'id':vlan_list,
                            'multicast_policy':templateVars["multicast_policy"],
                            'name':vlan_name,
                            'native_vlan':False
                        }
                    ]

                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'   description      = "{templateVars["descr"]}"')
                print(f'   multicast_policy = "{templateVars["multicast_policy"]}"')
                print(f'   name             = "{templateVars["name"]}"')
                if not native_vlan == '':
                    print(f'   native_vlan      = "{native_vlan}"')
                    print(f'   native_vlan_name = "{native_name}"')
                print(f'   vlan_list        = "{vlan_list}"')
                print(f'   vlan_name        = "{vlan_name}"')
                print(f'\n-------------------------------------------------------------------------------------------\n')
                valid_confirm = False
                while valid_confirm == False:
                    confirm_policy = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                    if confirm_policy == 'Y' or confirm_policy == '':
                        confirm_policy = 'Y'

                        # Write Policies to Template File
                        templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
                        write_to_template(self, **templateVars)

                        # Add VLANs to VLAN Policy List
                        vlan_policies_vlans.append({templateVars['name']:vlan_list_expanded})

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

    #========================================
    # VSAN Policy Module
    #========================================
    def vsan_policies(self, jsonData, easy_jsonData):
        vsan_policies_vsans = []
        name_prefix = self.name_prefix
        org = self.org
        policy_type = 'VSAN Policy'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'vsan_policies'

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  You can Skip this policy if you are not configuring Fibre-Channel.\n')
            print(f'  A {policy_type} will define the VSANs Assigned to the Fabric Interconnects.  You will need')
            print(f'  one VSAN Policy for Fabric A and another VSAN Policy for Fabric B.\n')
            print(f'  IMPORTANT Note: The Fabric Interconnects will encapsulate Fibre-Channel traffic locally')
            print(f'                  in a FCoE (Fibre-Channel over Ethernet) VLAN.  This VLAN Must not be')
            print(f'                  already used by the VLAN Policy.\n')
            print(f'  This wizard will save the configuraton for this section to the following file:')
            print(f'  - Intersight/{org}/{self.type}/{templateVars["template_type"]}.auto.tfvars')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure a {policy_type}?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                loop_count = 0
                policy_loop = False
                while policy_loop == False:

                    name = naming_rule_fabric(loop_count, name_prefix, org)

                    templateVars["name"] = policy_name(name, policy_type)
                    templateVars["descr"] = policy_descr(templateVars["name"], policy_type)
                    templateVars["auto_allow_on_uplinks"] = True

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  Uplink Trunking: Default is No.')
                    print(f'     Most deployments do not enable Uplink Trunking for Fibre-Channel. ')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid = False
                    while valid == False:
                        uplink_trunking = input('Do you want to Enable Uplink Trunking for this VSAN Policy? [N]? ')
                        if uplink_trunking == 'Y':
                            templateVars["uplink_trunking"] = True
                            valid = True
                        else:
                            templateVars["uplink_trunking"] = False
                            valid = True

                    templateVars["vsans"] = []
                    vsan_count = 0
                    vsan_loop = False
                    while vsan_loop == False:
                        valid = False
                        while valid == False:
                            if loop_count % 2 == 0:
                                vsan_id = input(f'Enter the VSAN id to add to {templateVars["name"]}. [100]: ')
                            else:
                                vsan_id = input(f'Enter the VSAN id to add to {templateVars["name"]}. [200]: ')
                            if loop_count % 2 == 0 and vsan_id == '':
                                vsan_id = 100
                            elif vsan_id == '':
                                vsan_id = 200
                            if re.search(r'[0-9]{1,4}', str(vsan_id)):
                                valid = validating.number_in_range('VSAN ID', vsan_id, 1, 4094)
                            else:
                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                print(f'  Invalid Entry!  Please Enter a VSAN ID in the range of 1-4094.')
                                print(f'\n-------------------------------------------------------------------------------------------\n')

                        valid = False
                        while valid == False:
                            fcoe_id = input(f'Enter the VLAN id for the FCOE VLAN to encapsulate "{vsan_id}" over Ethernet.  [{vsan_id}]: ')
                            if fcoe_id == '':
                                fcoe_id = vsan_id
                            if re.search(r'[0-9]{1,4}', str(fcoe_id)):
                                valid_vlan = validating.number_in_range('VSAN ID', fcoe_id, 1, 4094)
                                if valid_vlan == True:
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

                                    vlan_list = ','.join(vlan_list)
                                    vlan_list = vlan_list_full(vlan_list)
                                    overlap = False
                                    for vlan in vlan_list:
                                        if int(vlan) == int(fcoe_id):
                                            print(f'\n-------------------------------------------------------------------------------------------\n')
                                            print(f'  Error!!  The FCoE VLAN {fcoe_id} is already assigned to the VLAN Policy')
                                            print(f'  {vlan_policy}.  Please choose a VLAN id that is not already in use.')
                                            print(f'\n-------------------------------------------------------------------------------------------\n')
                                            overlap = True
                                            break
                                    if overlap == False:
                                        valid = True
                                else:
                                    print(f'\n-------------------------------------------------------------------------------------------\n')
                                    print(f'  Invalid Entry!  Please Enter a valid VLAN ID in the range of 1-4094.')
                                    print(f'\n-------------------------------------------------------------------------------------------\n')

                            else:
                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                print(f'  Invalid Entry!  Please Enter a valid VLAN ID in the range of 1-4094.')
                                print(f'\n-------------------------------------------------------------------------------------------\n')

                        valid = False
                        while valid == False:
                            if loop_count % 2 == 0:
                                vsan_name = input(f'What Name would you like to assign to "{vsan_id}"?  [VSAN-A]: ')
                            else:
                                vsan_name = input(f'What Name would you like to assign to "{vsan_id}"?  [VSAN-B]: ')
                            if loop_count % 2 == 0 and vsan_name == '':
                                vsan_name = 'VSAN-A'
                            elif vsan_name == '':
                                vsan_name = 'VSAN-B'
                            valid = validating.name_rule('VSAN Name', vsan_name, 1, 62)

                        vsan = {
                            'fcoe_vlan_id':fcoe_id,
                            'name':vsan_name,
                            'id':vsan_id
                        }
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        print(f'   fcoe_vlan_id = {fcoe_id}')
                        print(f'   vsan_id      = {vsan_id}')
                        print(f'   vsan_name    = "{vsan_name}"')
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        valid_confirm = False
                        while valid_confirm == False:
                            confirm_vsan = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                            if confirm_vsan == 'Y' or confirm_vsan == '':
                                templateVars['vsans'].append(vsan)
                                valid_exit = False
                                while valid_exit == False:
                                    vsan_exit = input(f'Would You like to Configure another VSAN?  Enter "Y" or "N" [N]: ')
                                    if vsan_exit == 'Y':
                                        vsan_count += 1
                                        valid_confirm = True
                                        valid_exit = True
                                    elif vsan_exit == 'N' or vsan_exit == '':
                                        vsan_loop = True
                                        valid_confirm = True
                                        valid_exit = True
                                    else:
                                        print(f'\n------------------------------------------------------\n')
                                        print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                                        print(f'\n------------------------------------------------------\n')

                            elif confirm_vsan == 'N':
                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                print(f'  Starting VSAN Configuration Over.')
                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                valid_confirm = True
                            else:
                                print(f'\n------------------------------------------------------\n')
                                print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                                print(f'\n------------------------------------------------------\n')

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'    description     = "{templateVars["descr"]}"')
                    print(f'    name            = "{templateVars["name"]}"')
                    print(f'    uplink_trunking = {templateVars["uplink_trunking"]}')
                    print(f'    vsans           = [')
                    item_count = 1
                    for item in templateVars["vsans"]:
                        print(f'      {item_count} = ''{')
                        for k, v in item.items():
                            if k == 'fcoe_vlan_id':
                                print(f'        fcoe_vlan_id = {v}')
                            elif k == 'name':
                                print(f'        name         = "{v}"')
                            elif k == 'id':
                                print(f'        vsan_id      = {v}')
                        print('      }')
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

                            # Add VSANs to VSAN Policy List
                            vsan_policies_vsans.append({templateVars['name']:templateVars["vsans"]})

                            configure_loop, loop_count, policy_loop = exit_loop_default_yes(loop_count, policy_type)
                            valid_confirm = True

                        elif confirm_policy == 'N':
                            print(f'\n------------------------------------------------------\n')
                            print(f'  Starting {policy_type} Section over.')
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

    #========================================
    # WWNN Pools Module
    #========================================
    def wwnn_pools(self, jsonData, easy_jsonData):
        name_prefix = self.name_prefix
        name_suffix = 'wwnn_pool'
        org = self.org
        policy_type = 'WWNN Pool'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'wwnn_pools'

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  WWNN Pool Convention Recommendations:')
            print(f'  - Leverage the Cisco UCS OUI of 20:00:00:25:B5 for the WWNN Pool Prefix.')
            print(f'  - Pool Size can be between 1 and 1000 addresses.')
            print(f'  - Refer to "UCS Naming Conventions 0.5.ppsx" in the Repository for further guidance.\n')
            print(f'  This wizard will save the configuraton for this section to the following file:')
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

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  Assignment order decides the order in which the next identifier is allocated.')
                    print(f'    1. default - (Intersight Default) Assignment order is decided by the system.')
                    print(f'    2. sequential - (Recommended) Identifiers are assigned in a sequential order.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid = False
                    while valid == False:
                        templateVars["assignment_order"] = input('Specify the number for the value to select.  [2]: ')
                        if templateVars["assignment_order"] == '' or templateVars["assignment_order"] == '2':
                            templateVars["assignment_order"] = 'sequential'
                            valid = True
                        elif templateVars["assignment_order"] == '1':
                            templateVars["assignment_order"] = 'default'
                            valid = True
                        else:
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            print(f'  Error!! Invalid Option.  Please Select a valid option from the List.')
                            print(f'\n-------------------------------------------------------------------------------------------\n')

                    valid = False
                    while valid == False:
                        begin = input('What is the Beginning WWNN Address to Assign to the Pool?  [20:00:00:25:B5:00:00:00]: ')
                        if begin == '':
                            begin = '20:00:00:25:B5:00:00:00'
                        valid = validating.wwxn_address('WWNN Pool Address', begin)

                    valid = False
                    while valid == False:
                        pool_size = input('How Many WWNN Addresses should be added to the Pool?  Range is 1-1000 [512]: ')
                        if pool_size == '':
                            pool_size = '512'
                        valid = validating.number_in_range('Pool Size', pool_size, 1, 1000)

                    begin = begin.upper()
                    beginx = int(begin.replace(':', ''), 16)
                    add_dec = (beginx + int(pool_size))
                    ending = ':'.join(['{}{}'.format(a, b)
                        for a, b
                        in zip(*[iter('{:012x}'.format(add_dec))]*2)])
                    ending = ending.upper()
                    templateVars["wwnn_blocks"] = [{'from':begin, 'to':ending}]

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'    assignment_order = "{templateVars["assignment_order"]}"')
                    print(f'    description      = "{templateVars["descr"]}"')
                    print(f'    name             = "{templateVars["name"]}"')
                    print(f'    wwnn_blocks = [')
                    for item in templateVars["wwnn_blocks"]:
                        print('      {')
                        for k, v in item.items():
                            if k == 'from':
                                print(f'        from = "{v}" ')
                            elif k == 'to':
                                print(f'        to   = "{v}"')
                        print('      }')
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

    #========================================
    # WWPN Pools Module
    #========================================
    def wwpn_pools(self, jsonData, easy_jsonData):
        name_prefix = self.name_prefix
        org = self.org
        policy_type = 'WWPN Pool'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'wwpn_pools'

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  WWPN Pool Convention Recommendations:')
            print(f'  - Leverage the Cisco UCS OUI of 20:00:00:25:B5 for the WWPN Pool Prefix.')
            print(f'  - For WWPN Pools; create a pool for each Fabric.')
            print(f'  - Pool Size can be between 1 and 1000 addresses.')
            print(f'  - Refer to "UCS Naming Conventions 0.5.ppsx" in the Repository for further guidance.\n')
            print(f'  This wizard will save the configuraton for this section to the following file:')
            print(f'  - Intersight/{org}/{self.type}/{templateVars["template_type"]}.auto.tfvars')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure a {policy_type}?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                loop_count = 0
                policy_loop = False
                while policy_loop == False:

                    name = naming_rule_fabric(loop_count, name_prefix, org)

                    templateVars["name"] = policy_name(name, policy_type)
                    templateVars["descr"] = policy_descr(templateVars["name"], policy_type)

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  Assignment order decides the order in which the next identifier is allocated.')
                    print(f'    1. default - (Intersight Default) Assignment order is decided by the system.')
                    print(f'    2. sequential - (Recommended) Identifiers are assigned in a sequential order.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid = False
                    while valid == False:
                        templateVars["assignment_order"] = input('Specify the number for the value to select.  [2]: ')
                        if templateVars["assignment_order"] == '' or templateVars["assignment_order"] == '2':
                            templateVars["assignment_order"] = 'sequential'
                            valid = True
                        elif templateVars["assignment_order"] == '1':
                            templateVars["assignment_order"] = 'default'
                            valid = True
                        else:
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            print(f'  Error!! Invalid Option.  Please Select a valid option from the List.')
                            print(f'\n-------------------------------------------------------------------------------------------\n')

                    valid = False
                    while valid == False:
                        if loop_count % 2 == 0:
                            begin = input('What is the Beginning WWPN Address to Assign to the Pool?  [20:00:00:25:B5:0A:00:00]: ')
                        else:
                            begin = input('What is the Beginning WWPN Address to Assign to the Pool?  [20:00:00:25:B5:0B:00:00]: ')
                        if begin == '':
                            if loop_count % 2 == 0:
                                begin = '20:00:00:25:B5:0A:00:00'
                            else:
                                begin = '20:00:00:25:B5:0B:00:00'
                        valid = validating.wwxn_address('WWPN Pool Address', begin)

                    valid = False
                    while valid == False:
                        pool_size = input('How Many WWPN Addresses should be added to the Pool?  Range is 1-1000 [512]: ')
                        if pool_size == '':
                            pool_size = '512'
                        valid = validating.number_in_range('Pool Size', pool_size, 1, 1000)

                    begin = begin.upper()
                    beginx = int(begin.replace(':', ''), 16)
                    add_dec = (beginx + int(pool_size))
                    ending = ':'.join(['{}{}'.format(a, b)
                        for a, b
                        in zip(*[iter('{:012x}'.format(add_dec))]*2)])
                    ending = ending.upper()
                    templateVars["wwpn_blocks"] = [{'from':begin, 'to':ending}]

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'    assignment_order = "{templateVars["assignment_order"]}"')
                    print(f'    description      = "{templateVars["descr"]}"')
                    print(f'    name             = "{templateVars["name"]}"')
                    print(f'    wwpn_blocks = [')
                    for item in templateVars["wwpn_blocks"]:
                        print('      {')
                        for k, v in item.items():
                            if k == 'from':
                                print(f'        from = "{v}" ')
                            elif k == 'to':
                                print(f'        to   = "{v}"')
                        print('      }')
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

                            configure_loop, loop_count, policy_loop = exit_loop_default_yes(loop_count, policy_type)
                            valid_confirm = True

                        elif confirm_policy == 'N':
                            print(f'\n------------------------------------------------------\n')
                            print(f'  Starting {policy_type} Section over.')
                            print(f'\n------------------------------------------------------\n')
                            valid_confirm = True

                        else:
                            print(f'\n------------------------------------------------------\n')
                            print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                            print(f'\n------------------------------------------------------\n')

            elif configure == 'N':
                configure_loop = True
            else:
                print(f'\n------------------------------------------------------\n')
                print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                print(f'\n------------------------------------------------------\n')

        # Close the Template file
        templateVars["template_file"] = 'template_close.jinja2'
        write_to_template(self, **templateVars)

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
        valid = validating.description(f'{policy_type} templateVars["Description"]', descr, 1, 62)
        if valid == True:
            return descr

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
                elif 'pools' in policy_description:
                    policy_description = policy_description.replace('Pools', 'Pool')

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
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).ip_pools(jsonData, easy_jsonData)
            elif inner_policy == 'iqn_pools':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).iqn_pools(jsonData, easy_jsonData)
            elif inner_policy == 'mac_pools':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).mac_pools(jsonData, easy_jsonData)
            elif inner_policy == 'uuid_pools':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).uuid_pools(jsonData, easy_jsonData)
            elif inner_policy == 'wwnn_pools':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).wwnn_pools(jsonData, easy_jsonData)
            elif inner_policy == 'wwpn_pools':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).wwpn_pools(jsonData, easy_jsonData)
            elif inner_policy == 'adapter_configuration_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).adapter_configuration_policies(jsonData, easy_jsonData)
            elif inner_policy == 'bios_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).bios_policies(jsonData, easy_jsonData)
            elif inner_policy == 'boot_order_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).boot_order_policies(jsonData, easy_jsonData)
            elif inner_policy == 'certificate_management_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).certificate_management_policies(jsonData, easy_jsonData)
            elif inner_policy == 'device_connector_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).device_connector_policies(jsonData, easy_jsonData)
            elif inner_policy == 'ethernet_adapter_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).ethernet_adapter_policies(jsonData, easy_jsonData)
            elif inner_policy == 'ethernet_network_control_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).ethernet_network_control_policies(jsonData, easy_jsonData)
            elif inner_policy == 'ethernet_network_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).ethernet_network_policies(jsonData, easy_jsonData)
            elif inner_policy == 'ethernet_qos_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).ethernet_qos_policies(jsonData, easy_jsonData)
            elif inner_policy == 'fibre_channel_adapter_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).fibre_channel_adapter_policies(jsonData, easy_jsonData)
            elif inner_policy == 'fibre_channel_network_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).fibre_channel_network_policies(jsonData, easy_jsonData)
            elif inner_policy == 'fibre_channel_qos_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).fibre_channel_qos_policies(jsonData, easy_jsonData)
            elif inner_policy == 'flow_control_policies':
                print('creating policy')
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).flow_control_policies(jsonData, easy_jsonData)
            elif inner_policy == 'imc_access_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).imc_access_policies(jsonData, easy_jsonData)
            elif inner_policy == 'ipmi_over_lan_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).ipmi_over_lan_policies(jsonData, easy_jsonData)
            elif inner_policy == 'iscsi_adapter_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).iscsi_adapter_policies(jsonData, easy_jsonData)
            elif inner_policy == 'iscsi_boot_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).iscsi_boot_policies(jsonData, easy_jsonData)
            elif inner_policy == 'iscsi_static_target_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).iscsi_static_target_policies(jsonData, easy_jsonData)
            elif inner_policy == 'lan_connectivity_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).lan_connectivity_policies(jsonData, easy_jsonData)
            elif inner_policy == 'ldap_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).ldap_policies(jsonData, easy_jsonData)
            elif inner_policy == 'link_aggregation_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).link_aggregation_policies(jsonData, easy_jsonData)
            elif inner_policy == 'link_control_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).link_control_policies(jsonData, easy_jsonData)
            elif inner_policy == 'local_user_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).local_user_policies(jsonData, easy_jsonData)
            elif inner_policy == 'multicast_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).multicast_policies(jsonData, easy_jsonData)
            elif inner_policy == 'network_connectivity_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).network_connectivity_policies(jsonData, easy_jsonData)
            elif inner_policy == 'ntp_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).ntp_policies(jsonData, easy_jsonData)
            elif inner_policy == 'persistent_memory_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).persistent_memory_policies(jsonData, easy_jsonData)
            elif inner_policy == 'port_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).port_policies(jsonData, easy_jsonData)
            elif inner_policy == 'san_connectivity_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).san_connectivity_policies(jsonData, easy_jsonData)
            elif inner_policy == 'sd_card_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).sd_card_policies(jsonData, easy_jsonData)
            elif inner_policy == 'serial_over_lan_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).serial_over_lan_policies(jsonData, easy_jsonData)
            elif inner_policy == 'smtp_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).smtp_policies(jsonData, easy_jsonData)
            elif inner_policy == 'snmp_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).snmp_policies(jsonData, easy_jsonData)
            elif inner_policy == 'ssh_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).ssh_policies(jsonData, easy_jsonData)
            elif inner_policy == 'storage_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).storage_policies(jsonData, easy_jsonData)
            elif inner_policy == 'switch_control_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).switch_control_policies(jsonData, easy_jsonData)
            elif inner_policy == 'syslog_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).syslog_policies(jsonData, easy_jsonData)
            elif inner_policy == 'system_qos_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).system_qos_policies(jsonData, easy_jsonData)
            elif inner_policy == 'thermal_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).thermal_policies(jsonData, easy_jsonData)
            elif inner_policy == 'virtual_kvm_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).virtual_kvm_policies(jsonData, easy_jsonData)
            elif inner_policy == 'virtual_media_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).virtual_media_policies(jsonData, easy_jsonData)
            elif inner_policy == 'vlan_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).vlan_policies(jsonData, easy_jsonData)
            elif inner_policy == 'vsan_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).vsan_policies(jsonData, easy_jsonData)

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
