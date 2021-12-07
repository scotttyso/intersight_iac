#!/usr/bin/env python3

import jinja2
import pkg_resources
import re
import validating
from easy_functions import exit_default_no, exit_loop_default_yes
from easy_functions import naming_rule_fabric
from easy_functions import policy_descr, policy_name
from easy_functions import policy_select_loop
from easy_functions import port_list_eth, port_list_fc, port_modes_fc
from easy_functions import variablesFromAPI
from easy_functions import vlan_list_full
from easy_functions import write_to_template

ucs_template_path = pkg_resources.resource_filename('class_policies_domain', 'Templates/')

class policies_domain(object):
    def __init__(self, name_prefix, org, type):
        self.templateLoader = jinja2.FileSystemLoader(
            searchpath=(ucs_template_path + '%s/') % (type))
        self.templateEnv = jinja2.Environment(loader=self.templateLoader)
        self.name_prefix = name_prefix
        self.org = org
        self.type = type

    #==============================================
    # Flow Control Policy Module
    #==============================================
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

    #==============================================
    # Link Aggregation Policy Module
    #==============================================
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

    #==============================================
    # Multicast Policy Module
    #==============================================
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

    #==============================================
    # Port Policy Module
    #==============================================
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
            print(f'  This wizard will save the configuration for this section to the following file:')
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
                
                fc_mode,ports_in_use,fc_converted_ports,port_modes = port_modes_fc(jsonData, easy_jsonData, name_prefix, **templateVars)
                templateVars["fc_mode"] = fc_mode
                templateVars["ports_in_use"] = ports_in_use
                templateVars["fc_converted_ports"] = fc_converted_ports
                templateVars["port_modes"] = port_modes

                # Appliance Port-Channel
                templateVars['port_type'] = 'Appliance Port-Channel'
                port_channel_appliances,templateVars['ports_in_use'] = port_list_eth(jsonData, easy_jsonData, name_prefix, **templateVars)

                # Ethernet Uplink Port-Channel
                templateVars['port_type'] = 'Ethernet Uplink Port-Channel'
                port_channel_ethernet_uplinks,templateVars['ports_in_use'] = port_list_eth(jsonData, easy_jsonData, name_prefix, **templateVars)

                # Fibre Channel Port-Channel
                templateVars["fc_ports_in_use"] = []
                templateVars["port_type"] == 'Fibre Channel Port-Channel'
                Fab_A,Fab_B,fc_ports_in_use = port_list_fc(jsonData, easy_jsonData, name_prefix, **templateVars)
                Fabric_A_fc_port_channels = Fab_A
                Fabric_B_fc_port_channels = Fab_B
                templateVars["fc_ports_in_use"] = fc_ports_in_use

                # FCoE Uplink Port-Channel
                templateVars['port_type'] = 'FCoE Uplink Port-Channel'
                port_channel_fcoe_uplinks,templateVars['ports_in_use'] = port_list_eth(jsonData, easy_jsonData, name_prefix, **templateVars)

                # Appliance Ports
                templateVars['port_type'] = 'Appliance Ports'
                port_role_appliances,templateVars['ports_in_use'] = port_list_eth(jsonData, easy_jsonData, name_prefix, **templateVars)

                # Ethernet Uplink
                templateVars['port_type'] = 'Ethernet Uplink'
                port_role_ethernet_uplinks,templateVars['ports_in_use'] = port_list_eth(jsonData, easy_jsonData, name_prefix, **templateVars)

                # Fibre-Channel Uplink
                templateVars["port_type"] == 'Fibre-Channel Uplink'
                Fab_A,Fab_B,fc_ports_in_use = port_list_fc(jsonData, easy_jsonData, name_prefix, **templateVars)
                Fabric_A_port_role_fc = Fab_A
                Fabric_B_port_role_fc = Fab_B
                templateVars["fc_ports_in_use"] = fc_ports_in_use

                # FCoE Uplink
                templateVars['port_type'] = 'FCoE Uplink'
                port_role_fcoe_uplinks,templateVars['ports_in_use'] = port_list_eth(jsonData, easy_jsonData, name_prefix, **templateVars)

                # Server Ports
                templateVars['port_type'] = 'Server Ports'
                port_role_servers,templateVars['ports_in_use'] = port_list_eth(jsonData, easy_jsonData, name_prefix, **templateVars)

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

    #==============================================
    # Switch Control Policy Module
    #==============================================
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

    #==============================================
    # System QoS Policy Module
    #==============================================
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

    #==============================================
    # VLAN Policy Module
    #==============================================
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
                            'auto_allow_on_uplinks':False,
                            'id':native_vlan,
                            'multicast_policy':templateVars["multicast_policy"],
                            'name':native_name,
                            'native_vlan':True
                        },
                        {
                            'auto_allow_on_uplinks':False,
                            'id':vlan_list,
                            'multicast_policy':templateVars["multicast_policy"],
                            'name':vlan_name,
                            'native_vlan':False
                        }
                    ]
                elif not native_vlan == '' and len(vlan_list) == 1:
                    templateVars["vlans"] = [
                        {
                            'auto_allow_on_uplinks':False,
                            'id':native_vlan,
                            'multicast_policy':templateVars["multicast_policy"],
                            'name':native_name,
                            'native_vlan':True
                        }
                    ]
                else:
                    templateVars["vlans"] = [
                        {
                            'auto_allow_on_uplinks':False,
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

    #==============================================
    # VSAN Policy Module
    #==============================================
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
            print(f'  This wizard will save the configuration for this section to the following file:')
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
