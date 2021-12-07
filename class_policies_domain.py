#!/usr/bin/env python3

import jinja2
import pkg_resources
import re
import validating
from class_policies_lan import policies_lan
from class_policies_system_qos import system_qos
from class_policies_vxan import policies_vxan
from easy_functions import choose_policy, policies_parse
from easy_functions import exit_default_no
from easy_functions import policy_descr, policy_name
from easy_functions import variablesFromAPI
from easy_functions import vars_from_list
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
                templateVars["fc_ports"] = templateVars["port_modes"]["port_list"]

                # Appliance Port-Channel
                templateVars['port_type'] = 'Appliance Port-Channel'
                port_channel_appliances,templateVars['ports_in_use'] = port_list_eth(jsonData, easy_jsonData, name_prefix, **templateVars)

                # Ethernet Uplink Port-Channel
                templateVars['port_type'] = 'Ethernet Uplink Port-Channel'
                port_channel_ethernet_uplinks,templateVars['ports_in_use'] = port_list_eth(jsonData, easy_jsonData, name_prefix, **templateVars)

                # Fibre Channel Port-Channel
                templateVars["fc_ports_in_use"] = []
                templateVars["port_type"] = 'Fibre Channel Port-Channel'
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
                templateVars["port_type"] = 'Fibre-Channel Uplink'
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
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'   There were no {policy_description} found.')
                print(f'\n-------------------------------------------------------------------------------------------\n')

                if 'Policies' in policy_description:
                    policy_description = policy_description.replace('Policies', 'Policy')

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
            if inner_policy == 'ethernet_network_control_policies':
                policies_lan(name_prefix, templateVars["org"], inner_type).ethernet_network_control_policies(jsonData, easy_jsonData)
            elif inner_policy == 'ethernet_network_group_policies':
                policies_lan(name_prefix, templateVars["org"], inner_type).ethernet_network_group_policies(jsonData, easy_jsonData)
            elif inner_policy == 'flow_control_policies':
                policies_domain(name_prefix, templateVars["org"], inner_type).flow_control_policies(jsonData, easy_jsonData)
            elif inner_policy == 'link_aggregation_policies':
                policies_domain(name_prefix, templateVars["org"], inner_type).link_aggregation_policies(jsonData, easy_jsonData)
            elif inner_policy == 'link_control_policies':
                policies_domain(name_prefix, templateVars["org"], inner_type).link_control_policies(jsonData, easy_jsonData)
            elif inner_policy == 'multicast_policies':
                policies_vxan(name_prefix, templateVars["org"], inner_type).multicast_policies(jsonData, easy_jsonData)
            elif inner_policy == 'port_policies':
                policies_domain(name_prefix, templateVars["org"], inner_type).port_policies(jsonData, easy_jsonData)
            elif inner_policy == 'switch_control_policies':
                policies_domain(name_prefix, templateVars["org"], inner_type).switch_control_policies(jsonData, easy_jsonData)
            elif inner_policy == 'system_qos_policies':
                system_qos(name_prefix, templateVars["org"], inner_type).system_qos_policies(jsonData, easy_jsonData)
            elif inner_policy == 'vlan_policies':
                policies_vxan(name_prefix, templateVars["org"], inner_type).vlan_policies(jsonData, easy_jsonData)
            elif inner_policy == 'vsan_policies':
                policies_vxan(name_prefix, templateVars["org"], inner_type).vsan_policies(jsonData, easy_jsonData)

def port_list_eth(jsonData, easy_jsonData, name_prefix, **templateVars):
    port_channels = []
    port_roles = []
    port_count = 1
    ports_in_use = templateVars["ports_in_use"]
    if templateVars["port_type"] == 'Appliance Port-Channel' and templateVars["device_model"] == 'UCS-FI-64108':
        portx = '99,100'
    elif templateVars["port_type"] == 'Appliance Port-Channel':
        portx = '51,52'
    elif templateVars["port_type"] == 'Ethernet Uplink Port-Channel' and templateVars["device_model"] == 'UCS-FI-64108':
        portx = '97,98'
    elif templateVars["port_type"] == 'Ethernet Uplink Port-Channel':
        portx = '49,50'
    elif templateVars["port_type"] == 'FCoE Uplink Port-Channel' and templateVars["device_model"] == 'UCS-FI-64108':
        portx = '101,102'
    elif templateVars["port_type"] == 'FCoE Uplink Port-Channel':
        portx = '53,54'
    elif templateVars["port_type"] == 'Appliance Ports' and templateVars["device_model"] == 'UCS-FI-64108':
        portx = '99'
    elif templateVars["port_type"] == 'Appliance Ports':
        portx = '51'
    elif templateVars["port_type"] == 'Ethernet Uplink' and templateVars["device_model"] == 'UCS-FI-64108':
        portx = '97'
    elif templateVars["port_type"] == 'Ethernet Uplink':
        portx = '49'
    elif templateVars["port_type"] == 'FCoE Uplink' and templateVars["device_model"] == 'UCS-FI-64108':
        portx = '101'
    elif templateVars["port_type"] == 'FCoE Uplink':
        portx = '53'
    elif templateVars["port_type"] == 'Server Ports' and templateVars["device_model"] == 'UCS-FI-64108':
        portx = '5-36'
    elif templateVars["port_type"] == 'Server Ports':
        portx = '5-18'
    if re.search('(Ethernet Uplink Port-Channel|Server Ports)', templateVars["port_type"]):
        default_answer = 'Y'
    else:
        default_answer = 'N'
    valid = False
    while valid == False:
        question = input(f'Do you want to configure an {templateVars["port_type"]}?  Enter "Y" or "N" [{default_answer}]: ')
        if question == 'Y' or (default_answer == 'Y' and question == ''):
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
                            if not templateVars["port_type"] == 'Server Ports':
                                templateVars["multi_select"] = False
                                jsonVars = jsonData['components']['schemas']['fabric.TransceiverRole']['allOf'][1]['properties']
                                templateVars["var_description"] = jsonVars['AdminSpeed']['description']
                                templateVars["jsonVars"] = jsonVars['AdminSpeed']['enum']
                                templateVars["defaultVar"] = jsonVars['AdminSpeed']['default']
                                templateVars["varType"] = 'Admin Speed'
                                templateVars["admin_speed"] = variablesFromAPI(**templateVars)

                            if re.search('^(Appliance Appliance Ports|(Ethernet|FCoE) Uplink)$', templateVars["port_type"]):
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
                            elif re.search('Ethernet Uplink', templateVars["port_type"]):
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

        elif question == 'N'  or (default_answer == 'N' and question == ''):
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

    if templateVars["port_type"] == 'Fibre Channel Port-Channel':
        default_answer = 'Y'
    else:
        default_answer = 'N'
    A_port_channels = []
    B_port_channels = []
    A_port_role = []
    B_port_role = []
    fc_ports_in_use = templateVars["fc_ports_in_use"]
    port_count = 1
    if len(templateVars["fc_converted_ports"]) > 0:
        configure_fc = True
    else:
        configure_fc = False
    if configure_fc == True:
        valid = False
        while valid == False:
            question = input(f'Do you want to configure a {templateVars["port_type"]}?  Enter "Y" or "N" [{default_answer}]: ')
            if question == 'Y' or (default_answer == 'Y' and question == ''):
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

            elif question == 'N' or (default_answer == 'N' and question == ''):
                valid = True
            else:
                print(f'\n------------------------------------------------------\n')
                print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                print(f'\n------------------------------------------------------\n')

    if templateVars["port_type"] == 'Fibre Channel Port-Channel':
        return A_port_channels,B_port_channels,fc_ports_in_use
    else:
        return A_port_role,B_port_role,fc_ports_in_use

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
