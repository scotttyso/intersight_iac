#!/usr/bin/env python3

import ipaddress
import jinja2
import pkg_resources
import re
import validating
from class_policies_lan import policies_lan
from class_policies_san import policies_san
from class_policies_p1 import policies_p1
from class_policies_p2 import port_list_eth, port_list_fc, port_modes_fc
from class_policies_p2 import policies_p2
from class_policies_p3 import policies_p3
from class_policies_vxan import policies_vxan
from class_pools import pools
from class_profiles import profiles
from easy_functions import choose_policy, policies_parse
from easy_functions import ipmi_key_function, local_users_function
from easy_functions import ntp_alternate, ntp_primary
from easy_functions import snmp_trap_servers, snmp_users
from easy_functions import syslog_servers
from easy_functions import ucs_domain_serials
from easy_functions import validate_vlan_in_policy
from easy_functions import variablesFromAPI
from easy_functions import varBoolLoop
from easy_functions import varNumberLoop
from easy_functions import varStringLoop
from easy_functions import vlan_list_full, vlan_pool
from easy_functions import write_to_template

ucs_template_path = pkg_resources.resource_filename('class_quick_start', 'Templates/')

class quick_start(object):
    def __init__(self, name_prefix, org, type):
        self.templateLoader = jinja2.FileSystemLoader(
            searchpath=(ucs_template_path + '%s/') % (type))
        self.templateEnv = jinja2.Environment(loader=self.templateLoader)
        self.name_prefix = name_prefix
        self.org = org
        self.type = type

    #==============================================
    # UCS Domain and Policies
    #==============================================
    def domain_policies(self, jsonData, easy_jsonData, **kwargs):
        name_prefix = self.name_prefix
        org = self.org
        templateVars = {}
        templateVars["org"] = org
        chassis_type = 'profiles'
        domain_type = 'ucs_domain_profiles'

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  The Quick Deployment Module - Domain Policies, will configure pools for a UCS Domain ')
            print(f'  Profile.\n')
            print(f'  This wizard will save the output for these pools in the following files:\n')
            print(f'  - Intersight/{org}/{self.type}/flow_control_policies.auto.tfvars')
            print(f'  - Intersight/{org}/{self.type}/link_aggregation_policies.auto.tfvars')
            print(f'  - Intersight/{org}/{self.type}/link_control_policies.auto.tfvars')
            print(f'  - Intersight/{org}/{self.type}/multicast_policies.auto.tfvars')
            print(f'  - Intersight/{org}/{self.type}/network_connectivity_policies.auto.tfvars')
            print(f'  - Intersight/{org}/{self.type}/ntp_policies.auto.tfvars')
            print(f'  - Intersight/{org}/{self.type}/port_policies.auto.tfvars')
            print(f'  - Intersight/{org}/{self.type}/system_qos_policies.auto.tfvars')
            print(f'  - Intersight/{org}/{self.type}/switch_control_policies.auto.tfvars')
            print(f'  - Intersight/{org}/{self.type}/vsan_policies.auto.tfvars')
            print(f'  - Intersight/{org}/{self.type}/vlan_policies.auto.tfvars')
            print(f'  - Intersight/{org}/{chassis_type}/ucs_chassis_profiles.auto.tfvars')
            print(f'  - Intersight/{org}/{domain_type}/ucs_domain_profiles.auto.tfvars')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to run the Quick Deployment Module - Domain Policy Configuration?  \nEnter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                loop_count = 0
                policy_loop = False
                while policy_loop == False:
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  Below are the Questions that will be asked by the Domain Policies Portion of the wizard.')
                    print(f'   - UCS Domain Name.')
                    print(f'   - UCS Domain Model.')
                    print(f'   - UCS Serial Number for both Fabrics.')
                    print(f'   - NTP Configuration:')
                    print(f'     * Timezone')
                    print(f'     * NTP Servers')
                    print(f'   - Port Configuration.')
                    print(f'     * Ethernet Uplink Ports.')
                    print(f'     * Fibre-Channel Uplink Ports.')
                    print(f'     * Server Ports.')
                    print(f'   - System MTU for the Domain.')
                    print(f'   - VLAN Pool for the Domain.')
                    print(f'   - VSAN ID for Fabric A.')
                    print(f'   - VSAN ID for Fabric B.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')

                    templateVars["name"] = 'Quick Deployment Module'

                    templateVars["multi_select"] = False
                    jsonVars = jsonData['components']['schemas']['policy.AbstractProfile']['allOf'][1]['properties']

                    # Domain Name
                    templateVars["Description"] = jsonVars['Name']['description']
                    templateVars["varInput"] = 'What is the name for this UCS Domain?'
                    templateVars["varDefault"] = ''
                    templateVars["varName"] = 'UCS Domain Name'
                    templateVars["varRegex"] = jsonVars['Name']['pattern']
                    templateVars["minLength"] = 1
                    templateVars["maxLength"] = 64
                    templateVars["name"] = varStringLoop(**templateVars)
                    domain_name = templateVars["name"]

                    # Domain Model
                    templateVars["multi_select"] = False
                    jsonVars = jsonData['components']['schemas']['fabric.PortPolicy']['allOf'][1]['properties']
                    templateVars["var_description"] = jsonVars['DeviceModel']['description']
                    templateVars["jsonVars"] = sorted(jsonVars['DeviceModel']['enum'])
                    templateVars["defaultVar"] = jsonVars['DeviceModel']['default']
                    templateVars["varType"] = 'Device Model'
                    templateVars["device_model"] = variablesFromAPI(**templateVars)

                    # Serial Numbers
                    serial_a,serial_b = ucs_domain_serials()
                    templateVars["serial_number_fabric_a"] = serial_a
                    templateVars["serial_number_fabric_b"] = serial_b

                    # VLAN Pool
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  IMPORTANT NOTE: The FCoE VLAN will be assigned based on the VSAN Identifier.')
                    print(f'                  Be sure to exclude the VSAN for Fabric A and B from the VLAN Pool.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    VlanList,vlanListExpanded = vlan_pool()

                    #_______________________________________________________________________
                    #
                    # Configure Multicast Policy
                    #_______________________________________________________________________

                    templateVars["name"] = domain_name
                    templateVars["descr"] = f'{templateVars["name"]} Multicast Policy'
                    policies_vxan(name_prefix, org, 'policies').quick_start_multicast(**templateVars)

                    #_______________________________________________________________________
                    #
                    # Configure VLAN Policy
                    #_______________________________________________________________________

                    templateVars["multicast_policy"] = templateVars["name"]
                    templateVars["descr"] = f'{templateVars["name"]} VLAN Policy'
                    templateVars["native_vlan"] = ''
                    templateVars["vlan_list"] = VlanList
                    policies_vxan(name_prefix, org, 'policies').quick_start_vlan(**templateVars)

                    #_______________________________________________________________________
                    #
                    # Configure Flow Control Policy
                    #_______________________________________________________________________

                    templateVars["initial_write"] = True
                    templateVars["policy_type"] = 'Flow Control Policy'
                    templateVars["header"] = '%s Variables' % (templateVars["policy_type"])
                    templateVars["template_file"] = 'template_open.jinja2'
                    templateVars["template_type"] = 'flow_control_policies'

                    # Open the Template file
                    write_to_template(self, **templateVars)
                    templateVars["initial_write"] = False

                    # Configure Flow Control Policy
                    name = domain_name
                    templateVars["name"] = name
                    templateVars["descr"] = f'{name} Flow Control Policy'
                    templateVars["priority"] = 'auto'
                    templateVars["receive"] = 'Enabled'
                    templateVars["send"] = 'Enabled'

                    # Write Policies to Template File
                    templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
                    write_to_template(self, **templateVars)

                    # Close the Template file
                    templateVars["template_file"] = 'template_close.jinja2'
                    write_to_template(self, **templateVars)

                    #_______________________________________________________________________
                    #
                    # Configure Link Aggregation Policy
                    #_______________________________________________________________________

                    templateVars["initial_write"] = True
                    templateVars["policy_type"] = 'Link Aggregation Policy'
                    templateVars["header"] = '%s Variables' % (templateVars["policy_type"])
                    templateVars["template_file"] = 'template_open.jinja2'
                    templateVars["template_type"] = 'link_aggregation_policies'

                    # Open the Template file
                    write_to_template(self, **templateVars)
                    templateVars["initial_write"] = False

                    # Configure Link Aggregation Policy
                    name = domain_name
                    templateVars["name"] = name
                    templateVars["descr"] = f'{name} Link Aggregation Policy'
                    templateVars["lacp_rate"] = 'normal'
                    templateVars["suspend_individual"] = False

                    # Write Policies to Template File
                    templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
                    write_to_template(self, **templateVars)

                    # Close the Template file
                    templateVars["template_file"] = 'template_close.jinja2'
                    write_to_template(self, **templateVars)

                    #_______________________________________________________________________
                    #
                    # Configure Link Control Policy
                    #_______________________________________________________________________

                    templateVars["initial_write"] = True
                    templateVars["policy_type"] = 'Link Control Policy'
                    templateVars["header"] = '%s Variables' % (templateVars["policy_type"])
                    templateVars["template_file"] = 'template_open.jinja2'
                    templateVars["template_type"] = 'link_control_policies'

                    # Open the Template file
                    write_to_template(self, **templateVars)
                    templateVars["initial_write"] = False

                    # Configure Link Control Policy
                    name = domain_name
                    templateVars["name"] = name
                    templateVars["descr"] = f'{name} Link Control Policy'
                    templateVars["admin_state"] = 'Enabled'
                    templateVars["mode"] = 'normal'

                    # Write Policies to Template File
                    templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
                    write_to_template(self, **templateVars)

                    # Close the Template file
                    templateVars["template_file"] = 'template_close.jinja2'
                    write_to_template(self, **templateVars)

                    # Configure Fibre-Channel Unified Ports
                    fc_mode,ports_in_use,fc_converted_ports,port_modes = port_modes_fc(jsonData, easy_jsonData, name_prefix, **templateVars)
                    templateVars["fc_mode"] = fc_mode
                    templateVars["ports_in_use"] = ports_in_use
                    templateVars["fc_converted_ports"] = fc_converted_ports
                    templateVars["port_modes"] = port_modes
                    if templateVars["port_modes"].get("port_list"):
                        templateVars["fc_ports"] = templateVars["port_modes"]["port_list"]
                    else:
                        templateVars["fc_ports"] = []

                    # If Unified Ports Exist Configure VSAN Policies
                    if len(templateVars["fc_converted_ports"]) > 0:
                        # Obtain the VSAN for Fabric A/B
                        fabrics = ['A', 'B']
                        for x in fabrics:
                            valid = False
                            while valid == False:
                                if loop_count % 2 == 0:
                                    vsan_id = input(f'Enter the VSAN id to add to {templateVars["name"]} Fabric {x}. [100]: ')
                                else:
                                    vsan_id = input(f'Enter the VSAN id to add to {templateVars["name"]} Fabric {x}. [200]: ')
                                if loop_count % 2 == 0 and vsan_id == '':
                                    vsan_id = 100
                                elif vsan_id == '':
                                    vsan_id = 200
                                if re.search(r'[0-9]{1,4}', str(vsan_id)):
                                    valid_count = 0
                                    for y in vlanListExpanded:
                                        if int(y) == int(vsan_id):
                                            valid_count += 1
                                            continue
                                    if valid_count == 0:
                                        templateVars[f"vsan_id_{x}"] = vsan_id
                                        valid_vlan = validating.number_in_range('VSAN ID', vsan_id, 1, 4094)
                                        if valid_vlan == True:
                                            loop_count += 1
                                            valid = True
                                    else:
                                        print(f'\n-------------------------------------------------------------------------------------------\n')
                                        print(f'  Invalid VSAN!  The FCoE VLAN {x} must not be assigned to the Domain VLAN Pool.')
                                        print(f'  Choose an Alternate VSAN Value.')
                                        print(f'\n-------------------------------------------------------------------------------------------\n')

                                else:
                                    print(f'\n-------------------------------------------------------------------------------------------\n')
                                    print(f'  Invalid Entry!  Please Enter a VSAN ID in the range of 1-4094.')
                                    print(f'\n-------------------------------------------------------------------------------------------\n')
                        
                        #_______________________________________________________________________
                        #
                        # Configure VSAN Policies
                        #_______________________________________________________________________

                        templateVars["initial_write"] = True
                        templateVars["policy_type"] = 'VSAN Policy'
                        templateVars["header"] = '%s Variables' % (templateVars["policy_type"])
                        templateVars["template_file"] = 'template_open.jinja2'
                        templateVars["template_type"] = 'vsan_policies'

                        # Open the Template file
                        write_to_template(self, **templateVars)
                        templateVars["initial_write"] = False

                        # Configure VSAN Policy
                        for x in fabrics:
                            name = f'{domain_name}-{x}'
                            templateVars["name"] = name
                            templateVars["descr"] = f'{name} VSAN Policy'
                            templateVars["uplink_trunking"] = False
                            xlower = x.lower()
                            templateVars['vsans'] = []
                            vsans = {
                                'fcoe_vlan_id':templateVars[f"vsan_id_{x}"],
                                'name':f'{domain_name}-{xlower}',
                                'id':templateVars[f"vsan_id_{x}"]
                            }
                            templateVars['vsans'].append(vsans)

                            # Write Policies to Template File
                            templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
                            write_to_template(self, **templateVars)

                        # Close the Template file
                        templateVars["template_file"] = 'template_close.jinja2'
                        write_to_template(self, **templateVars)

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  IMPORTANT NOTE: If you want to assign one of the VLANs from the Pool as the Native VLAN')
                    print(f'                  for the Port-Channel assign that here.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid = False
                    while valid == False:
                        nativeVlan = input('What is the Native VLAN for the Ethernet Port-Channel?  [press enter to skip]: ')
                        if nativeVlan == '':
                            valid = True
                        else:
                            native_count = 0
                            for vlan in vlanListExpanded:
                                if int(nativeVlan) == int(vlan):
                                    native_count = 1
                            if not native_count == 1:
                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                print(f'  Error!! The Native VLAN "{nativeVlan}" was not in the VLAN Policy List.')
                                print(f'  VLAN Policy List is: "{VlanList}"')
                                print(f'\n-------------------------------------------------------------------------------------------\n')
                            else:
                                valid = True

                    #_______________________________________________________________________
                    #
                    # Configure Ethernet Network Group Policy
                    #_______________________________________________________________________

                    templateVars["initial_write"] = True
                    templateVars["policy_type"] = 'Ethernet Network Group Policy'
                    templateVars["header"] = '%s Variables' % (templateVars["policy_type"])
                    templateVars["template_file"] = 'template_open.jinja2'
                    templateVars["template_type"] = 'ethernet_network_group_policies'

                    # Open the Template file
                    write_to_template(self, **templateVars)
                    templateVars["initial_write"] = False

                    # Configure Link Control Policy
                    name = f'{domain_name}-vg'
                    templateVars["name"] = name
                    templateVars["descr"] = f'{name} Ethernet Network Group Policy'
                    templateVars["allowed_vlans"] = VlanList
                    if not nativeVlan == '':
                        templateVars["native_vlan"] = nativeVlan
                    else:
                        templateVars["native_vlan"] = ''
                        templateVars.pop('native_vlan')

                    # Write Policies to Template File
                    templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
                    write_to_template(self, **templateVars)

                    # Close the Template file
                    templateVars["template_file"] = 'template_close.jinja2'
                    write_to_template(self, **templateVars)

                    # Ethernet Uplink Port-Channel
                    templateVars["name"] = domain_name
                    templateVars['port_type'] = 'Ethernet Uplink Port-Channel'
                    port_channel_ethernet_uplinks,templateVars['ports_in_use'] = port_list_eth(jsonData, easy_jsonData, name_prefix, **templateVars)

                    templateVars["fc_ports_in_use"] = []
                    templateVars["port_type"] = 'Fibre-Channel Port-Channel'
                    Fab_A,Fab_B,fc_ports_in_use = port_list_fc(jsonData, easy_jsonData, name_prefix, **templateVars)
                    Fabric_A_fc_port_channels = Fab_A
                    Fabric_B_fc_port_channels = Fab_B
                    templateVars["fc_ports_in_use"] = fc_ports_in_use

                    # Server Ports
                    templateVars['port_type'] = 'Server Ports'
                    port_role_servers,templateVars['ports_in_use'] = port_list_eth(jsonData, easy_jsonData, name_prefix, **templateVars)

                    # System MTU for System QoS Policy
                    templateVars["Description"] = 'This option will set the MTU to 9216 if answer is "Y" or 1500 if answer is "N".'
                    templateVars["varInput"] = f'Do you want to enable Jumbo MTU?  Enter "Y" or "N"'
                    templateVars["varDefault"] = 'Y'
                    templateVars["varName"] = 'MTU'
                    answer = varBoolLoop(**templateVars)
                    if answer == True:
                        mtu = 9216
                    else:
                        mtu = 1500

                    # NTP Servers
                    primary_ntp = ntp_primary()
                    alternate_ntp = ntp_alternate()

                    templateVars["enabled"] = True
                    templateVars["ntp_servers"] = []
                    templateVars["ntp_servers"].append(primary_ntp)
                    if not alternate_ntp == '':
                        templateVars["ntp_servers"].append(alternate_ntp)

                    # Timezone
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

                    templateVars["port_channel_ethernet_uplinks"] = port_channel_ethernet_uplinks
                    templateVars["Fabric_A_fc_port_channels"] = Fabric_A_fc_port_channels
                    templateVars["Fabric_B_fc_port_channels"] = Fabric_B_fc_port_channels
                    templateVars["port_role_servers"] = port_role_servers
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  UCS Domain Name        = "{domain_name}"')
                    print(f'  Device Model           = "{templateVars["device_model"]}"')
                    print(f'  Serial Number Fabric A = "{templateVars["serial_number_fabric_a"]}"')
                    print(f'  Serial Number Fabric B = "{templateVars["serial_number_fabric_b"]}"')
                    print(f'  Port Policy Variables:')
                    if len(templateVars["fc_converted_ports"]) > 0:
                        port_type_list = ['port_channel_ethernet_uplinks', 'Fabric_A_fc_port_channels', 'Fabric_B_fc_port_channels', 'port_role_servers']
                    else:
                        port_type_list = ['port_channel_ethernet_uplinks', 'port_role_servers']
                    for port_list in port_type_list:
                        if port_list == 'port_channel_ethernet_uplinks':
                            print(f'    Ethernet Port-Channel Ports = [')
                        elif port_list == 'Fabric_A_fc_port_channels':
                            print(f'    Fibre-Channel Port-Channel Fabric A = [')
                        elif port_list == 'Fabric_B_fc_port_channels':
                            print(f'    Fibre-Channel Port-Channel Fabric B = [')
                        elif port_list == 'port_role_servers':
                            print(f'    Server Ports = [')
                        for item in templateVars[f"{port_list}"]:
                            for key, value in item.items():
                                if key == 'admin_speed':
                                    print(f'        admin_speed                   = "{value}"')
                                elif key == 'ethernet_network_group_policy':
                                    print(f'        ethernet_network_group_policy = "{value}"')
                                elif key == 'fill_pattern':
                                    print(f'        fill_pattern                  = "{value}"')
                                elif key == 'flow_control_policy':
                                    print(f'        flow_control_policy           = "{value}"')
                                elif key == 'link_aggregation_policy':
                                    print(f'        link_aggregation_policy       = "{value}"')
                                elif key == 'link_control_policy':
                                    print(f'        link_control_policy           = "{value}"')
                                elif key == 'link_aggregation_policy':
                                    print(f'        link_aggregation_policy       = "{value}"')
                                elif key == 'pc_id':
                                    print(f'        pc_id = "{value}"')
                                elif key == 'port_list':
                                    print(f'        port_list = "{value}"')
                                elif key == 'slot_id':
                                    print(f'        slot_id   = "{value}"')
                                elif key == 'interfaces':
                                    int_count = 0
                                    print(f'        interfaces = [')
                                    for i in value:
                                        print(f'          "{int_count}" = ''{')
                                        for k, v in i.items():
                                            print(f'            {k} = {v}')
                                        print(f'          ''}')
                                        int_count +=1
                        print(f'        ]')
                    print(f'  System MTU: {mtu}')
                    print(f'  NTP Variables:')
                    print(f'    timezone: "{templateVars["timezone"]}"')
                    if len(templateVars["ntp_servers"]) > 0:
                        print(f'    ntp_servers = [')
                        for server in templateVars["ntp_servers"]:
                            print(f'      "{server}",')
                        print(f'    ]')
                    print(f'  VLAN Pool: "{VlanList}"')
                    print(f'  VSAN Fabric A: "{templateVars["vsan_id_A"]}"')
                    print(f'  VSAN Fabric B: "{templateVars["vsan_id_B"]}"')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
                        if confirm_policy == 'Y' or confirm_policy == '':

                            #_______________________________________________________________________
                            #
                            # Configure Sytem MTU Settings
                            #_______________________________________________________________________

                            templateVars["initial_write"] = True
                            templateVars["policy_type"] = 'System QoS Policy'
                            templateVars["header"] = '%s Variables' % (templateVars["policy_type"])
                            templateVars["template_file"] = 'template_open.jinja2'
                            templateVars["template_type"] = 'system_qos_policies'

                            # Open the Template file
                            write_to_template(self, **templateVars)
                            templateVars["initial_write"] = False

                            # System QoS Settings
                            templateVars["mtu"] = mtu
                            name = domain_name
                            templateVars["name"] = name
                            templateVars["descr"] = f'{name} System QoS Policy'
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

                            # Write Policies to Template File
                            templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
                            write_to_template(self, **templateVars)

                            # Close the Template file
                            templateVars["template_file"] = 'template_close.jinja2'
                            write_to_template(self, **templateVars)

                            #_______________________________________________________________________
                            #
                            # Configure Network Connectivity Policy
                            #_______________________________________________________________________

                            templateVars["initial_write"] = True
                            templateVars["policy_type"] = 'Network Connectivity Policy'
                            templateVars["header"] = '%s Variables' % (templateVars["policy_type"])
                            templateVars["template_file"] = 'template_open.jinja2'
                            templateVars["template_type"] = 'network_connectivity_policies'

                            # Open the Template file
                            write_to_template(self, **templateVars)
                            templateVars["initial_write"] = False

                            # Network Connectivity Access Settings
                            name = domain_name
                            templateVars["name"] = name
                            templateVars["descr"] = f'{name} Network Connectivity Policy'
                            templateVars["preferred_ipv4_dns_server"] = kwargs['primary_dns']
                            templateVars["alternate_ipv4_dns_server"] = kwargs['secondary_dns']
                            templateVars["enable_ipv6"] = False

                            # Write Policies to Template File
                            templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
                            write_to_template(self, **templateVars)

                            # Close the Template file
                            templateVars["template_file"] = 'template_close.jinja2'
                            write_to_template(self, **templateVars)

                            #_______________________________________________________________________
                            #
                            # Configure NTP Policy
                            #_______________________________________________________________________

                            templateVars["initial_write"] = True
                            templateVars["policy_type"] = 'NTP Policy'
                            templateVars["header"] = '%s Variables' % (templateVars["policy_type"])
                            templateVars["template_file"] = 'template_open.jinja2'
                            templateVars["template_type"] = 'ntp_policies'

                            # Open the Template file
                            write_to_template(self, **templateVars)
                            templateVars["initial_write"] = False

                            # NTP Settings
                            name = domain_name
                            templateVars["name"] = name
                            templateVars["descr"] = f'{name} NTP Policy'

                            # Write Policies to Template File
                            templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
                            write_to_template(self, **templateVars)

                            # Close the Template file
                            templateVars["template_file"] = 'template_close.jinja2'
                            write_to_template(self, **templateVars)

                            #_______________________________________________________________________
                            #
                            # Configure Switch Control Policy
                            #_______________________________________________________________________

                            templateVars["initial_write"] = True
                            templateVars["policy_type"] = 'Switch Control Policy'
                            templateVars["header"] = '%s Variables' % (templateVars["policy_type"])
                            templateVars["template_file"] = 'template_open.jinja2'
                            templateVars["template_type"] = 'switch_control_policies'

                            # Open the Template file
                            write_to_template(self, **templateVars)
                            templateVars["initial_write"] = False

                            # Switch Control Settings
                            name = domain_name
                            templateVars["name"] = name
                            templateVars["descr"] = f'{name} Switch Control Policy'
                            templateVars["mac_address_table_aging"] = 'Default'
                            templateVars["mac_aging_time"] = 14500
                            templateVars["udld_message_interval"] = 15
                            templateVars["udld_recovery_action"] = "reset"
                            templateVars["vlan_port_count_optimization"] = False

                            # Write Policies to Template File
                            templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
                            write_to_template(self, **templateVars)

                            # Close the Template file
                            templateVars["template_file"] = 'template_close.jinja2'
                            write_to_template(self, **templateVars)

                            #_______________________________________________________________________
                            #
                            # Configure Port Policy
                            #_______________________________________________________________________

                            templateVars["initial_write"] = True
                            templateVars["policy_type"] = 'Port Policy'
                            templateVars["header"] = '%s Variables' % (templateVars["policy_type"])
                            templateVars["template_file"] = 'template_open.jinja2'
                            templateVars["template_type"] = 'port_policies'

                            # Open the Template file
                            write_to_template(self, **templateVars)
                            templateVars["initial_write"] = False

                            # Port Settings
                            name = domain_name
                            templateVars["name"] = name
                            templateVars["descr"] = f'{name} Port Policy'

                            templateVars["port_channel_appliances"] = []
                            templateVars["port_channel_ethernet_uplinks"] = port_channel_ethernet_uplinks
                            templateVars["port_channel_fcoe_uplinks"] = []
                            templateVars["port_role_appliances"] = []
                            templateVars["port_role_ethernet_uplinks"] = []
                            templateVars["port_role_fcoe_uplinks"] = []
                            templateVars["port_role_servers"] = port_role_servers

                            for x in fabrics:
                                xlower = x.lower()
                                templateVars["name"] = f'{domain_name}-{xlower}'
                                if x == 'A':
                                    templateVars["port_channel_fc_uplinks"] = Fabric_A_fc_port_channels
                                else:
                                    templateVars["port_channel_fc_uplinks"] = Fabric_B_fc_port_channels
                                templateVars["port_role_fc_uplinks"] = []

                                # Write Policies to Template File
                                templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
                                write_to_template(self, **templateVars)

                            # Close the Template file
                            templateVars["template_file"] = 'template_close.jinja2'
                            write_to_template(self, **templateVars)

                            #_______________________________________________________________________
                            #
                            # Configure UCS Chassis Profile
                            #_______________________________________________________________________
                            name = domain_name
                            templateVars["name"] = name
                            profiles(name_prefix, org, 'profiles').quick_start_chassis(easy_jsonData, **templateVars)

                            #_______________________________________________________________________
                            #
                            # Configure UCS Domain Profile
                            #_______________________________________________________________________

                            # UCS Domain Profile Settings
                            name = domain_name
                            templateVars["name"] = name
                            templateVars["descr"] = f'{name} UCS Domain Profile'
                            templateVars["action"] = 'No-op'
                            templateVars["network_connectivity_policy"] = domain_name
                            templateVars["ntp_policy"] = domain_name
                            templateVars["port_policies"] = {
                                'fabric_a':f'{domain_name}-a',
                                'fabric_b':f'{domain_name}-b'
                            }
                            templateVars["snmp_policy"] = f'{org}_domain'
                            templateVars["switch_control_policy"] = domain_name
                            templateVars["syslog_policy"] = f'{org}_domain'
                            templateVars["system_qos_policy"] = domain_name
                            templateVars["vlan_policies"] = {
                                'fabric_a':domain_name,
                                'fabric_b':domain_name
                            }
                            if len(templateVars["fc_converted_ports"]) > 0:
                                templateVars["vsan_policies"] = {
                                    'fabric_a':f'{domain_name}-A',
                                    'fabric_b':f'{domain_name}-B'
                                }
                            else:
                                templateVars["vsan_policies"] = {
                                    'fabric_a':'',
                                    'fabric_b':''
                                }

                            profiles(name_prefix, org, 'ucs_domain_profiles').quick_start_domain(**templateVars)

                            configure_loop = True
                            policy_loop = True
                            valid_confirm = True

                        elif confirm_policy == 'N':
                            print(f'\n------------------------------------------------------\n')
                            print(f'  Starting Section over.')
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
        
        vlan_policy = {'vlan_policy':f'{domain_name}','vlans':VlanList}
        vsan_a = templateVars["vsan_id_A"]
        vsan_b = templateVars["vsan_id_B"]
        fc_ports = templateVars["fc_converted_ports"]
        mtu = templateVars["mtu"]
        return vlan_policy,vsan_a,vsan_b,fc_ports,mtu

    #==============================================
    # LAN and SAN Policies
    #==============================================
    def lan_san_policies(self, jsonData, easy_jsonData, **kwargs):
        if kwargs['mtu'] > 8999:
            mtu = 9000
        else:
            mtu = 1500
        org = self.org
        templateVars = {}
        templateVars["org"] = org

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  The Quick Deployment Module - Network Configuration, will configure policies for the')
            print(f'  Network Configuration of a UCS Server Profile connected to an IMM Domain.\n')
            print(f'  This wizard will save the output for these pools in the following files:\n')
            print(f'  - Intersight/{org}/{self.type}/ethernet_adapter_policies.auto.tfvars')
            print(f'  - Intersight/{org}/{self.type}/ethernet_network_control_policies.auto.tfvars')
            print(f'  - Intersight/{org}/{self.type}/ethernet_network_group_policies.auto.tfvars')
            print(f'  - Intersight/{org}/{self.type}/ethernet_qos_policies.auto.tfvars')
            print(f'  - Intersight/{org}/{self.type}/fibre_channel_adapter_policies.auto.tfvars')
            print(f'  - Intersight/{org}/{self.type}/fibre_channel_network_policies.auto.tfvars')
            print(f'  - Intersight/{org}/{self.type}/fibre_channel_qos_policies.auto.tfvars')
            print(f'  - Intersight/{org}/{self.type}/lan_connectivity_policies.auto.tfvars')
            print(f'  - Intersight/{org}/{self.type}/san_connectivity_policies.auto.tfvars')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to run the Quick Deployment Module - Network Configuration?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                loop_count = 1
                policy_loop = False
                while policy_loop == False:
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  Below are the Questions that will be asked by the Policies Portion of the wizard.')
                    print(f'   - Choice to use CDP or LDP for Device Discovery.')
                    print(f'   - Choice to enable Jumbo MTU (9000 MB) or Run standard 1500 MB MTU for vNICs.')
                    print(f'   - LAN Connectivity Policy (vNICs):')
                    print(f'     * VLAN ID for ESXi MGMT')
                    print(f'     * VLAN ID for ESXi vMotion')
                    print(f'     * VLAN ID for ESXi Storage')
                    print(f'     * VLAN List for DATA (Virtual Machines)')
                    print(f'   - SAN Connectivity Policy (vHBAs):')
                    print(f'     * VSAN ID for Fabric A')
                    print(f'     * VSAN ID for Fabric B')
                    print(f'     ** Note: This should not overlap with any of the VLANs assigned to the')
                    print(f'              LAN Connectivity Policies.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')

                    vlan_policy = kwargs["vlan_policy"]
                    vlan_list = kwargs["vlans"]
                    templateVars["vsan_A"] = kwargs["vsan_a"]
                    templateVars["vsan_B"] = kwargs["vsan_b"]
                    fc_ports_in_use = kwargs["fc_ports"]
                    vlan_policy_list = vlan_list_full(vlan_list)

                    templateVars["multi_select"] = False
                    jsonVars = jsonVars = easy_jsonData['policies']['fabric.EthNetworkControlPolicy']

                    # Neighbor Discovery Protocol
                    templateVars["var_description"] = jsonVars['discoveryProtocol']['description']
                    templateVars["jsonVars"] = sorted(jsonVars['discoveryProtocol']['enum'])
                    templateVars["defaultVar"] = jsonVars['discoveryProtocol']['default']
                    templateVars["varType"] = 'Neighbor Discovery Protocol'
                    neighbor_discovery = variablesFromAPI(**templateVars)

                    # Management VLAN
                    valid = False
                    while valid == False:
                        templateVars["Description"] = 'LAN Connectivity Policy vNICs - MGMT VLAN Identifier'
                        templateVars["varInput"] = 'Enter the VLAN ID for MGMT:'
                        templateVars["varDefault"] = 1
                        templateVars["varName"] = 'Management VLAN ID'
                        templateVars["minNum"] = 1
                        templateVars["maxNum"] = 4094
                        mgmt_vlan = varNumberLoop(**templateVars)
                        valid = validate_vlan_in_policy(vlan_policy_list, mgmt_vlan)

                    # vMotion VLAN
                    valid = False
                    while valid == False:
                        templateVars["Description"] = 'LAN Connectivity Policy vNICs - vMotion VLAN Identifier'
                        templateVars["varInput"] = 'Enter the VLAN ID for vMotion:'
                        templateVars["varDefault"] = 2
                        templateVars["varName"] = 'Management VLAN ID'
                        templateVars["minNum"] = 1
                        templateVars["maxNum"] = 4094
                        vmotion_vlan = varNumberLoop(**templateVars)
                        valid = validate_vlan_in_policy(vlan_policy_list, vmotion_vlan)

                    # Storage VLAN
                    valid = False
                    while valid == False:
                        templateVars["Description"] = 'LAN Connectivity Policy vNICs - Storage VLAN Identifier'
                        templateVars["varInput"] = 'Enter the VLAN ID for Storage:'
                        templateVars["varDefault"] = 3
                        templateVars["varName"] = 'Storage VLAN ID'
                        templateVars["minNum"] = 1
                        templateVars["maxNum"] = 4094
                        storage_vlan = varNumberLoop(**templateVars)
                        valid = validate_vlan_in_policy(vlan_policy_list, storage_vlan)

                    valid = False
                    while valid == False:
                        VlanList = input('Enter the VLAN or List of VLANs to add to the DATA (Virtual Machine) vNICs: ')
                        if not VlanList == '':
                            vlanListExpanded = vlan_list_full(VlanList)
                            valid_vlan = True
                            vlans_not_in_domain_policy = []
                            for vlan in vlanListExpanded:
                                valid_vlan = validating.number_in_range('VLAN ID', vlan, 1, 4094)
                                if valid_vlan == False:
                                    continue
                                else:
                                    vlan_count = 0
                                    for vlans in vlan_policy_list:
                                        if int(vlan) == int(vlans):
                                            vlan_count += 1
                                            break
                                    if vlan_count == 0:
                                        vlans_not_in_domain_policy.append(vlan)


                            if len(vlans_not_in_domain_policy) > 0:
                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                print(f'  Error with VLAN(s) assignment!!  The following VLAN(s) are missing.')
                                print(f'  - Domain VLAN Policy: "{vlan_policy}"')
                                print(f'  - VLANs in Policy: "{vlan_list}"')
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

                    fabrics = ['A', 'B']
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  Network Configuration Variables:')
                    print(f'    MGMT VLAN     = {mgmt_vlan}')
                    print(f'    vMotion VLAN  = {vmotion_vlan}')
                    print(f'    Storage VLAN  = {storage_vlan}')
                    print(f'    Data VLANs    = "{VlanList}"')
                    if len(fc_ports_in_use) > 0:
                        print(f'    VSAN Fabric A = {templateVars["vsan_A"]}')
                        print(f'    VSAN Fabric B = {templateVars["vsan_B"]}')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
                        if confirm_policy == 'Y' or confirm_policy == '':
                            confirm_policy = 'Y'

                            #_______________________________________________________________________
                            #
                            # Configure Ethernet Adapter Policy
                            #_______________________________________________________________________

                            templateVars["initial_write"] = True
                            templateVars["policy_type"] = 'Ethernet Adapter Policy'
                            templateVars["header"] = '%s Variables' % (templateVars["policy_type"])
                            templateVars["template_file"] = 'template_open.jinja2'
                            templateVars["template_type"] = 'ethernet_adapter_policies'

                            # Open the Template file
                            write_to_template(self, **templateVars)
                            templateVars["initial_write"] = False

                            name = 'VMware'
                            templateVars["name"] = name
                            templateVars["descr"] = f'{name} Ethernet Adapter Policy'
                            templateVars["policy_template"] = 'VMware'

                            # Write Policies to Template File
                            templateVars["template_file"] = '%s.jinja2' % ('ethernet_adapter_templates')
                            write_to_template(self, **templateVars)

                            # Close the Template file
                            templateVars["template_file"] = 'template_close.jinja2'
                            write_to_template(self, **templateVars)

                            #_______________________________________________________________________
                            #
                            # Configure Ethernet Network Control Policy
                            #_______________________________________________________________________

                            templateVars["initial_write"] = True
                            templateVars["policy_type"] = 'Ethernet Network Control Policy'
                            templateVars["header"] = '%s Variables' % (templateVars["policy_type"])
                            templateVars["template_file"] = 'template_open.jinja2'
                            templateVars["template_type"] = 'ethernet_network_control_policies'

                            # Open the Template file
                            write_to_template(self, **templateVars)
                            templateVars["initial_write"] = False

                            name = neighbor_discovery
                            templateVars["name"] = name
                            templateVars["descr"] = f'{name} Ethernet Network Control Policy'
                            templateVars["action_on_uplink_fail"] = "linkDown"
                            if neighbor_discovery == 'CDP':
                                templateVars["cdp_enable"] = True
                            else:
                                templateVars["cdp_enable"] = False
                            if neighbor_discovery == 'LLDP':
                                templateVars["lldp_receive_enable"] = True
                                templateVars["lldp_transmit_enable"] = True
                            else:
                                templateVars["lldp_receive_enable"] = False
                                templateVars["lldp_transmit_enable"] = False
                            templateVars["mac_register_mode"] = "nativeVlanOnly"
                            templateVars["mac_security_forge"] = "allow"

                            # Write Policies to Template File
                            templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
                            write_to_template(self, **templateVars)

                            # Close the Template file
                            templateVars["template_file"] = 'template_close.jinja2'
                            write_to_template(self, **templateVars)

                            #_______________________________________________________________________
                            #
                            # Configure Ethernet Network Group Policy
                            #_______________________________________________________________________

                            templateVars["initial_write"] = True
                            templateVars["policy_type"] = 'Ethernet Network Group Policy'
                            templateVars["header"] = '%s Variables' % (templateVars["policy_type"])
                            templateVars["template_file"] = 'template_open.jinja2'
                            templateVars["template_type"] = 'ethernet_network_group_policies'

                            # Open the Template file
                            write_to_template(self, **templateVars)
                            templateVars["initial_write"] = False

                            names = ['MGMT', 'VMOTION', 'STORAGE', 'DATA']
                            for x in names:
                                if x == 'MGMT':
                                    allowed_vlans = mgmt_vlan
                                    native_vlan = mgmt_vlan
                                elif x == 'MGMT':
                                    allowed_vlans = vmotion_vlan
                                    native_vlan = vmotion_vlan
                                elif x == 'MGMT':
                                    allowed_vlans = storage_vlan
                                    native_vlan = storage_vlan
                                elif x == 'DATA':
                                    allowed_vlans = VlanList
                                    native_vlan = nativeVlan
                                name = x
                                templateVars["name"] = name
                                templateVars["descr"] = f'{name} Ethernet Network Group Policy'
                                templateVars["allowed_vlans"] = allowed_vlans
                                if not native_vlan == '':
                                    templateVars["native_vlan"] = native_vlan
                                else:
                                    templateVars["native_vlan"] = ''
                                    templateVars.pop('native_vlan')

                                # Write Policies to Template File
                                templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
                                write_to_template(self, **templateVars)

                            # Close the Template file
                            templateVars["template_file"] = 'template_close.jinja2'
                            write_to_template(self, **templateVars)

                            #_______________________________________________________________________
                            #
                            # Configure Ethernet QoS Policy
                            #_______________________________________________________________________

                            templateVars["initial_write"] = True
                            templateVars["policy_type"] = 'Ethernet QoS Policy'
                            templateVars["header"] = '%s Variables' % (templateVars["policy_type"])
                            templateVars["template_file"] = 'template_open.jinja2'
                            templateVars["template_type"] = 'ethernet_qos_policies'

                            # Open the Template file
                            write_to_template(self, **templateVars)
                            templateVars["initial_write"] = False

                            names = ['Bronze', 'Gold', 'Platinum', 'Silver']
                            for x in names:
                                name = x
                                templateVars["name"] = name
                                templateVars["descr"] = f'{name} Ethernet QoS Policy'
                                templateVars["allowed_vlans"] = mgmt_vlan
                                templateVars["native_vlan"] = mgmt_vlan
                                templateVars["burst"] = 1024
                                templateVars["enable_trust_host_cos"] = False
                                templateVars["priority"] = x
                                templateVars["mtu"] = mtu
                                templateVars["rate_limit"] = 0

                                # Write Policies to Template File
                                templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
                                write_to_template(self, **templateVars)

                            # Close the Template file
                            templateVars["template_file"] = 'template_close.jinja2'
                            write_to_template(self, **templateVars)

                            if len(fc_ports_in_use) > 0:
                                #_______________________________________________________________________
                                #
                                # Configure Fibre-Channel Adapter Policy
                                #_______________________________________________________________________

                                templateVars["initial_write"] = True
                                templateVars["policy_type"] = 'Fibre-Channel Adapter Policy'
                                templateVars["header"] = '%s Variables' % (templateVars["policy_type"])
                                templateVars["template_file"] = 'template_open.jinja2'
                                templateVars["template_type"] = 'fibre_channel_adapter_policies'

                                # Open the Template file
                                write_to_template(self, **templateVars)
                                templateVars["initial_write"] = False

                                name = 'VMware'
                                templateVars["name"] = name
                                templateVars["descr"] = f'{name} Fibre-Channel Adapter Policy'
                                templateVars["policy_template"] = 'VMware'

                                # Write Policies to Template File
                                templateVars["template_file"] = '%s.jinja2' % ('ethernet_adapter_templates')
                                write_to_template(self, **templateVars)

                                # Close the Template file
                                templateVars["template_file"] = 'template_close.jinja2'
                                write_to_template(self, **templateVars)

                                #_______________________________________________________________________
                                #
                                # Configure Fibre-Channel Network Policy
                                #_______________________________________________________________________

                                templateVars["initial_write"] = True
                                templateVars["policy_type"] = 'Fibre-Channel Network Policy'
                                templateVars["header"] = '%s Variables' % (templateVars["policy_type"])
                                templateVars["template_file"] = 'template_open.jinja2'
                                templateVars["template_type"] = 'fibre_channel_network_policies'

                                # Open the Template file
                                write_to_template(self, **templateVars)
                                templateVars["initial_write"] = False

                                fabrics = ['A', 'B']
                                for fab in fabrics:
                                    name = f'Fabric-{fab}'
                                    templateVars["name"] = name
                                    templateVars["descr"] = f'{name} Fibre-Channel Network Policy'
                                    templateVars["default_vlan"] = 0
                                    templateVars["vsan_id"] = templateVars[f"vsan_{fab}"]

                                    # Write Policies to Template File
                                    templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
                                    write_to_template(self, **templateVars)

                                # Close the Template file
                                templateVars["template_file"] = 'template_close.jinja2'
                                write_to_template(self, **templateVars)

                                #_______________________________________________________________________
                                #
                                # Configure Fibre-Channel QoS Policy
                                #_______________________________________________________________________

                                templateVars["initial_write"] = True
                                templateVars["policy_type"] = 'Fibre-Channel QoS Policy'
                                templateVars["header"] = '%s Variables' % (templateVars["policy_type"])
                                templateVars["template_file"] = 'template_open.jinja2'
                                templateVars["template_type"] = 'fibre_channel_qos_policies'

                                # Open the Template file
                                write_to_template(self, **templateVars)
                                templateVars["initial_write"] = False

                                name = 'FC_QoS'
                                templateVars["name"] = name
                                templateVars["descr"] = f'{name} Fibre-Channel QoS Policy'
                                templateVars["burst"] = 1024
                                templateVars["max_data_field_size"] = 2112
                                templateVars["rate_limit"] = 0

                                # Write Policies to Template File
                                templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
                                write_to_template(self, **templateVars)

                                # Close the Template file
                                templateVars["template_file"] = 'template_close.jinja2'
                                write_to_template(self, **templateVars)

                            #_______________________________________________________________________
                            #
                            # LAN Connectivity Policy
                            #_______________________________________________________________________

                            templateVars["initial_write"] = True
                            templateVars["policy_type"] = 'LAN Connectivity Policy'
                            templateVars["header"] = '%s Variables' % (templateVars["policy_type"])
                            templateVars["template_file"] = 'template_open.jinja2'
                            templateVars["template_type"] = 'lan_connectivity_policies'

                            # Open the Template file
                            write_to_template(self, **templateVars)
                            templateVars["initial_write"] = False

                            name = 'VMware_LAN'
                            templateVars["name"] = name
                            templateVars["descr"] = f'{name} LAN Connectivity Policy'
                            templateVars["enable_azure_stack_host_qos"] = False
                            templateVars["iqn_allocation_type"] = "None"
                            templateVars["vnic_placement_mode"] = "custom"
                            templateVars["target_platform"] = "FIAttached"
                            templateVars["vnics"] = []

                            names = ['MGMT_Silver', 'VMOTION_Bronze', 'STORAGE_Platinum', 'DATA_Gold']
                            Order = 0
                            for nam in names:
                                vname = nam.split('_')[0]
                                qos = nam.split('_')[1]
                                for fab in fabrics:
                                    vnic = {
                                        'cdn_source':'vnic',
                                        'enable_failover':False,
                                        'ethernet_adapter_policy':'VMware',
                                        'ethernet_network_control_policy':neighbor_discovery,
                                        'ethernet_network_group_policy':vname,
                                        'ethernet_qos_policy':qos,
                                        'mac_address_allocation_type':'POOL',
                                        'mac_address_pool':f'{vname}-{fab}',
                                        'name':f'{vname}-{fab}',
                                        'placement_pci_link':0,
                                        'placement_pci_order':Order,
                                        'placement_slot_id':'MLOM',
                                        'placement_switch_id':fab
                                    }
                                    templateVars["vnics"].append(vnic)
                                    Order += 1

                            # Write Policies to Template File
                            templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
                            write_to_template(self, **templateVars)

                            # Close the Template file
                            templateVars["template_file"] = 'template_close.jinja2'
                            write_to_template(self, **templateVars)

                            if len(fc_ports_in_use) > 0:
                                #_______________________________________________________________________
                                #
                                # SAN Connectivity Policy
                                #_______________________________________________________________________

                                templateVars["initial_write"] = True
                                templateVars["policy_type"] = 'SAN Connectivity Policy'
                                templateVars["header"] = '%s Variables' % (templateVars["policy_type"])
                                templateVars["template_file"] = 'template_open.jinja2'
                                templateVars["template_type"] = 'san_connectivity_policies'

                                # Open the Template file
                                write_to_template(self, **templateVars)
                                templateVars["initial_write"] = False

                                name = 'VMware_SAN'
                                templateVars["name"] = name
                                templateVars["descr"] = f'{name} SAN Connectivity Policy'
                                templateVars["target_platform"] = "FIAttached"
                                templateVars["vhba_placement_mode"] = "custom"
                                templateVars["vhbas"] = []
                                templateVars["wwnn_allocation_type"] = "POOL"
                                templateVars["wwnn_pool"] = "VMware"

                                for fab in fabrics:
                                    vhba = {
                                        'fibre_channel_adapter_policy':'VMware',
                                        'fibre_channel_network_policy':f'Fabric-{fab}',
                                        'fibre_channel_qos_policy':'FC_QoS',
                                        'name':f'HBA-{fab}',
                                        'persistent_lun_bindings':False,
                                        'placement_pci_link':0,
                                        'placement_pci_order':Order,
                                        'placement_slot_id':'MLOM',
                                        'placement_switch_id':fab,
                                        'wwpn_allocation_type':'POOL',
                                        'wwpn_pool':f'VMware-{fab}',
                                    }
                                    templateVars["vhbas"].append(vhba)
                                    Order += 1

                                # Write Policies to Template File
                                templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
                                write_to_template(self, **templateVars)

                                # Close the Template file
                                templateVars["template_file"] = 'template_close.jinja2'
                                write_to_template(self, **templateVars)

                            configure_loop = True
                            policy_loop = True
                            valid_confirm = True

                        elif confirm_policy == 'N':
                            print(f'\n------------------------------------------------------\n')
                            print(f'  Starting Section over.')
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

    #==============================================
    # Pools
    #==============================================
    def pools(self, jsonData, easy_jsonData):
        org = self.org
        templateVars = {}
        templateVars["org"] = org

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  The Quick Deployment Module - Pools, will configure pools for a UCS Server Profile')
            print(f'  connected to an IMM Domain.\n')
            print(f'  This wizard will save the output for these pools in the following files:\n')
            print(f'  - Intersight/{org}/{self.type}/ip_pools.auto.tfvars')
            print(f'  - Intersight/{org}/{self.type}/mac_pools.auto.tfvars')
            print(f'  - Intersight/{org}/{self.type}/uuid_pools.auto.tfvars')
            print(f'  - Intersight/{org}/{self.type}/wwnn_pools.auto.tfvars')
            print(f'  - Intersight/{org}/{self.type}/wwpn_pools.auto.tfvars')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to run the Quick Deployment Module - Pools?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                loop_count = 1
                policy_loop = False
                while policy_loop == False:
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  Below are the Questions that will be asked by the Pools Portion of the wizard.')
                    print(f'   - IP Pool for IMC/KVM Access')
                    print(f'     * Gateway')
                    print(f'     * Netmask')
                    print(f'     * Starting IP Address for the Pool')
                    print(f'     * Ending IP Address for the Pool')
                    print(f'     * Primary DNS Server')
                    print(f'     * Secondary DNS Server (optional)')
                    print(f'   - Inband VLAN ID for IMC Policy (KVM Access)')
                    print(f'   - MAC/UUID/WWNN/WWPN Pools')
                    print(f'     * Prefix Value')
                    print(f'       The following pools will be configured with the prefix value:')
                    print(f'        (Policy maximum 1000 addresses per pool in Intersight):')
                    print(f'        - MGMT Pool A: 00:25:B5:[prefix]:A0:00 to 00:25:B5:[prefix]:A3:E7')
                    print(f'        - MGMT Pool B: 00:25:B5:[prefix]:B0:00 to 00:25:B5:[prefix]:B3:E7')
                    print(f'        - VMOTION Pool A: 00:25:B5:[prefix]:C0:00 to 00:25:B5:[prefix]:C3:E7')
                    print(f'        - VMOTION Pool B: 00:25:B5:[prefix]:D0:00 to 00:25:B5:[prefix]:D3:E7')
                    print(f'        - STORAGE Pool A: 00:25:B5:[prefix]:E0:00 to 00:25:B5:[prefix]:E3:E7')
                    print(f'        - STORAGE Pool B: 00:25:B5:[prefix]:F0:00 to 00:25:B5:[prefix]:F3:E7')
                    print(f'        - DATA Pool A: 00:25:B5:[prefix]:G0:00 to 00:25:B5:[prefix]:G3:E7')
                    print(f'        - DATA Pool B: 00:25:B5:[prefix]:H0:00 to 00:25:B5:[prefix]:H3:E7')
                    print(f'        - UUID Pool: 000025B5-[prefix]00-0000 to 000025B5-[prefix]00-03E7')
                    print(f'        - WWNN Pool: 20:00:00:25:B5:[prefix]:00:00 to 20:00:00:25:B5:[prefix]:03:E7')
                    print(f'        - WWPN Pool A: 20:00:00:25:B5:[prefix]:A0:00 to 20:00:00:25:B5:[prefix]:A3:E7')
                    print(f'        - WWPN Pool B: 20:00:00:25:B5:[prefix]:B0:00 to 20:00:00:25:B5:[prefix]:B3:E7')
                    print(f'\n-------------------------------------------------------------------------------------------\n')

                    templateVars["multi_select"] = False
                    jsonVars = jsonData['components']['schemas']['ippool.IpV4Config']['allOf'][1]['properties']

                    templateVars["Description"] = jsonVars['Gateway']['description']
                    templateVars["varInput"] = 'What is the Gateway for the KVM IP Pool? [198.18.0.1]:'
                    templateVars["varDefault"] = '198.18.0.1'
                    templateVars["varName"] = 'Gateway'
                    templateVars["varRegex"] = jsonVars['Gateway']['pattern']
                    templateVars["minLength"] = 7
                    templateVars["maxLength"] = 15
                    gateway = varStringLoop(**templateVars)

                    templateVars["Description"] = jsonVars['Netmask']['description']
                    templateVars["varInput"] = 'What is the Netmask for the KVM IP Pool? [255.255.255.0]:'
                    templateVars["varDefault"] = '255.255.255.0'
                    templateVars["varName"] = 'Netmask'
                    templateVars["varRegex"] = jsonVars['Netmask']['pattern']
                    templateVars["minLength"] = 7
                    templateVars["maxLength"] = 15
                    netmask = varStringLoop(**templateVars)

                    templateVars["Description"] = jsonVars['PrimaryDns']['description']
                    templateVars["varInput"] = 'What is the Primary Dns for the KVM IP Pool? [208.67.220.220]:'
                    templateVars["varDefault"] = '208.67.220.220'
                    templateVars["varName"] = 'Primary Dns'
                    templateVars["varRegex"] = jsonVars['PrimaryDns']['pattern']
                    templateVars["minLength"] = 7
                    templateVars["maxLength"] = 15
                    primary_dns = varStringLoop(**templateVars)

                    templateVars["Description"] = jsonVars['SecondaryDns']['description']
                    templateVars["varInput"] = 'What is the Secondary Dns for the KVM IP Pool? [press enter to skip]:'
                    templateVars["varDefault"] = ''
                    templateVars["varName"] = 'Secondary Dns'
                    templateVars["varRegex"] = jsonVars['SecondaryDns']['pattern']
                    templateVars["minLength"] = 7
                    templateVars["maxLength"] = 15
                    secondary_dns = varStringLoop(**templateVars)

                    jsonVars = jsonData['components']['schemas']['ippool.IpV4Block']['allOf'][1]['properties']

                    templateVars["Description"] = jsonVars['From']['description']
                    templateVars["varInput"] = 'What is the First IP Address for the KVM IP Pool? [198.18.0.10]:'
                    templateVars["varDefault"] = '198.18.0.10'
                    templateVars["varName"] = 'Beginning IP Address'
                    templateVars["varRegex"] = jsonVars['From']['pattern']
                    templateVars["minLength"] = 7
                    templateVars["maxLength"] = 15
                    pool_from = varStringLoop(**templateVars)

                    templateVars["Description"] = jsonVars['To']['description']
                    templateVars["varInput"] = 'What is the Last IP Address for the KVM IP Pool? [198.18.0.254]:'
                    templateVars["varDefault"] = '198.18.0.254'
                    templateVars["varName"] = 'Ending IP Address'
                    templateVars["varRegex"] = jsonVars['To']['pattern']
                    templateVars["minLength"] = 7
                    templateVars["maxLength"] = 15
                    pool_to = varStringLoop(**templateVars)

                    templateVars["Description"] = 'Prefix to assign to Pools'
                    templateVars["varInput"] = 'What is the 2 Digit (Hex) Prefix to assign to the MAC, UUID, WWNN, and WWPN Pools? [00]:'
                    templateVars["varDefault"] = '00'
                    templateVars["varName"] = 'Pool Prefix'
                    templateVars["varRegex"] = '^[0-9a-zA-Z][0-9a-zA-Z]$'
                    templateVars["minLength"] = 2
                    templateVars["maxLength"] = 2
                    pool_prefix = varStringLoop(**templateVars)
                    pool_prefix = pool_prefix.upper()

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  KVM IP Pool Variables:"')
                    print(f'    Gateway       = "{gateway}"')
                    print(f'    Netmask       = "{netmask}"')
                    print(f'    Primary DNS   = "{primary_dns}"')
                    print(f'    Secondary DNS = "{secondary_dns}"')
                    print(f'    Starting IP   = "{pool_from}"')
                    print(f'    Ending IP     = "{pool_to}"')
                    print(f'  Pool Prefix for the rest of the Pools = "{pool_prefix}"')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
                        if confirm_policy == 'Y' or confirm_policy == '':
                            confirm_policy = 'Y'

                            #_______________________________________________________________________
                            #
                            # Configure IP Pool
                            #_______________________________________________________________________

                            templateVars["initial_write"] = True
                            templateVars["policy_type"] = 'IP Pool'
                            templateVars["header"] = '%s Variables' % (templateVars["policy_type"])
                            templateVars["template_file"] = 'template_open.jinja2'
                            templateVars["template_type"] = 'ip_pools'

                            # Open the Template file
                            write_to_template(self, **templateVars)
                            templateVars["initial_write"] = False

                            name = 'VMWare_KVM'
                            templateVars["name"] = name
                            templateVars["descr"] = f'{name} KVM IP Pool'
                            templateVars["assignment_order"] = 'sequential'
                            pool_size = int(ipaddress.IPv4Address(pool_to)) - int(ipaddress.IPv4Address(pool_from)) + 1
                            templateVars["ipv4_blocks"] = [
                                {
                                    'from':pool_from,
                                    'size':pool_size,
                                    'to':pool_to
                                }
                            ]
                            templateVars["ipv4_configuration"] = {
                                'gateway':gateway,
                                'prefix':netmask,
                                'primary_dns':primary_dns,
                                'secondary_dns':secondary_dns
                            }

                            # Write Policies to Template File
                            templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
                            write_to_template(self, **templateVars)

                            # Close the Template file
                            templateVars["template_file"] = 'template_close.jinja2'
                            write_to_template(self, **templateVars)

                            #_______________________________________________________________________
                            #
                            # Configure MAC Pools
                            #_______________________________________________________________________

                            templateVars["initial_write"] = True
                            templateVars["policy_type"] = 'MAC Pool'
                            templateVars["header"] = '%s Variables' % (templateVars["policy_type"])
                            templateVars["template_file"] = 'template_open.jinja2'
                            templateVars["template_type"] = 'mac_pools'

                            # Open the Template file
                            write_to_template(self, **templateVars)
                            templateVars["initial_write"] = False

                            names = ['DATA', 'MGMT', 'MIGRATION', 'STORAGE']
                            fabrics = ['A', 'B']
                            for nam in names:
                                for fab in fabrics:
                                    if nam == 'MGMT' and fab == 'A': key_id = 'A'
                                    elif nam == 'MGMT' and fab == 'B': key_id = 'B'
                                    elif nam == 'MIGRATION' and fab == 'A': key_id = 'C'
                                    elif nam == 'MIGRATION' and fab == 'B': key_id = 'D'
                                    elif nam == 'STORAGE' and fab == 'A': key_id = 'E'
                                    elif nam == 'STORAGE' and fab == 'B': key_id = 'F'
                                    elif nam == 'DATA' and fab == 'A': key_id = '1'
                                    elif nam == 'DATA' and fab == 'B': key_id = '2'

                                    name = f'{nam}-{fab}'
                                    templateVars["name"] = name
                                    templateVars["descr"] = f'{name} MAC Pool'
                                    templateVars["assignment_order"] = 'sequential'
                                    pool_from = f'00:25:B5:{pool_prefix}:{key_id}0:00'
                                    pool_to = f'00:25:B5:{pool_prefix}:{key_id}3:E7'
                                    templateVars["mac_blocks"] = [
                                        {
                                            'from':pool_from,
                                            'size':1000,
                                            'to':pool_to
                                        }
                                    ]
                                    # Write Policies to Template File
                                    templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
                                    write_to_template(self, **templateVars)

                            # Close the Template file
                            templateVars["template_file"] = 'template_close.jinja2'
                            write_to_template(self, **templateVars)

                            #_______________________________________________________________________
                            #
                            # Configure UUID Pool
                            #_______________________________________________________________________

                            templateVars["initial_write"] = True
                            templateVars["policy_type"] = 'UUID Pool'
                            templateVars["header"] = '%s Variables' % (templateVars["policy_type"])
                            templateVars["template_file"] = 'template_open.jinja2'
                            templateVars["template_type"] = 'uuid_pools'

                            # Open the Template file
                            write_to_template(self, **templateVars)
                            templateVars["initial_write"] = False

                            name = 'VMware'
                            templateVars["name"] = name
                            templateVars["descr"] = f'{name} UUID Pool'
                            templateVars["assignment_order"] = 'sequential'
                            templateVars["prefix"] = f'000025B5-{pool_prefix}00-0000'
                            templateVars["uuid_blocks"] = [
                                {
                                    'from':'0000-000000000000',
                                    'size':1000,
                                    'to':'0000-0000000003E7'
                                }
                            ]
                            # Write Policies to Template File
                            templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
                            write_to_template(self, **templateVars)

                            # Close the Template file
                            templateVars["template_file"] = 'template_close.jinja2'
                            write_to_template(self, **templateVars)

                            #_______________________________________________________________________
                            #
                            # Configure WWNN Pool
                            #_______________________________________________________________________

                            templateVars["initial_write"] = True
                            templateVars["policy_type"] = 'WWNN Pool'
                            templateVars["header"] = '%s Variables' % (templateVars["policy_type"])
                            templateVars["template_file"] = 'template_open.jinja2'
                            templateVars["template_type"] = 'wwnn_pools'

                            # Open the Template file
                            write_to_template(self, **templateVars)
                            templateVars["initial_write"] = False

                            name = 'VMware'
                            templateVars["name"] = name
                            templateVars["descr"] = f'{name} WWNN Pool'
                            templateVars["assignment_order"] = 'sequential'
                            pool_from = f'20:00:00:25:B5:{pool_prefix}:00:00'
                            pool_to = f'20:00:00:25:B5:{pool_prefix}:03:E7'
                            templateVars["wwnn_blocks"] = [
                                {
                                    'from':pool_from,
                                    'size':1000,
                                    'to':pool_to
                                }
                            ]
                            # Write Policies to Template File
                            templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
                            write_to_template(self, **templateVars)

                            # Close the Template file
                            templateVars["template_file"] = 'template_close.jinja2'
                            write_to_template(self, **templateVars)

                            #_______________________________________________________________________
                            #
                            # Configure WWPN Pools
                            #_______________________________________________________________________

                            templateVars["initial_write"] = True
                            templateVars["policy_type"] = 'WWPN Pool'
                            templateVars["header"] = '%s Variables' % (templateVars["policy_type"])
                            templateVars["template_file"] = 'template_open.jinja2'
                            templateVars["template_type"] = 'wwpn_pools'

                            # Open the Template file
                            write_to_template(self, **templateVars)
                            templateVars["initial_write"] = False

                            for fab in fabrics:
                                name = f'VMware-{fab}'
                                templateVars["name"] = name
                                templateVars["descr"] = f'{name} WWPN Pool Fabric {fab}'
                                templateVars["assignment_order"] = 'sequential'
                                pool_from = f'20:00:00:25:B5:{pool_prefix}:{fab}0:00'
                                pool_to = f'20:00:00:25:B5:{pool_prefix}:{fab}3:E7'
                                templateVars["wwpn_blocks"] = [
                                    {
                                        'from':pool_from,
                                        'size':1000,
                                        'to':pool_to
                                    }
                                ]
                                # Write Policies to Template File
                                templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
                                write_to_template(self, **templateVars)

                            # Close the Template file
                            templateVars["template_file"] = 'template_close.jinja2'
                            write_to_template(self, **templateVars)

                            configure_loop = True
                            policy_loop = True
                            valid_confirm = True

                        elif confirm_policy == 'N':
                            print(f'\n------------------------------------------------------\n')
                            print(f'  Starting Section over.')
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

        return primary_dns,secondary_dns

    #==============================================
    # Server Policies for Domain and Standalone
    #==============================================
    def server_policies(self, jsonData, easy_jsonData, **kwargs):
        server_type = kwargs['server_type']
        vlan_list = kwargs['vlans']
        org = self.org
        templateVars = {}
        templateVars["org"] = org

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  The Quick Deployment Module - Pools, will configure pools for a UCS Server Profile')
            print(f'  connected to an IMM Domain.\n')
            print(f'  This wizard will save the output for these pools in the following files:\n')
            print(f'  - Intersight/{org}/{self.type}/imc_access_policies.auto.tfvars')
            print(f'  - Intersight/{org}/{self.type}/ipmi_over_lan_policies.auto.tfvars')
            print(f'  - Intersight/{org}/{self.type}/local_user_policies.auto.tfvars')
            print(f'  - Intersight/{org}/{self.type}/power_policies.auto.tfvars')
            print(f'  - Intersight/{org}/{self.type}/serial_over_lan_policies.auto.tfvars')
            print(f'  - Intersight/{org}/{self.type}/snmp_policies.auto.tfvars')
            print(f'  - Intersight/{org}/{self.type}/syslog_policies.auto.tfvars')
            print(f'  - Intersight/{org}/{self.type}/thermal_policies.auto.tfvars')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to run the Quick Deployment Module - Policy Configuration?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                loop_count = 1
                policy_loop = False
                while policy_loop == False:
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  Below are the Questions that will be asked by the Policies Portion of the wizard.')
                    print(f'   - VLAN ID for IMC Access Policy.')
                    print(f'   - Local User Policy (Required for direct KVM Access).')
                    print(f'     * user and role')
                    print(f'     * user password (strong passwords enforced)')
                    print(f'   - SNMP Policy')
                    print(f'     * Contact')
                    print(f'     * Location')
                    print(f'     * SNMPv3 Users (optional)')
                    print(f'     * SNMPv3 Trap Servers (optional)')
                    print(f'   - Syslog Policy - (Optional)')
                    print(f'     * Remote Syslog Server(s)')
                    print(f'\n-------------------------------------------------------------------------------------------\n')

                    templateVars["name"] = 'Quick Deployment Module'

                    vlan_policy_list = vlan_list_full(vlan_list)

                    templateVars["multi_select"] = False

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  Now Starting the IMC Access Policy Section.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    # IMC Access VLAN
                    valid = False
                    while valid == False:
                        templateVars["Description"] = 'IMC Access VLAN Identifier'
                        templateVars["varInput"] = 'Enter the VLAN ID for the IMC Access Policy.'
                        templateVars["varDefault"] = 1
                        templateVars["varName"] = 'IMC Access Policy VLAN ID'
                        templateVars["minNum"] = 1
                        templateVars["maxNum"] = 4094
                        imc_vlan = varNumberLoop(**templateVars)
                        if server_type == 'FIAttached':
                            valid = validate_vlan_in_policy(vlan_policy_list, imc_vlan)
                        else:
                            valid = True

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  Need to obtain the IPMI Key for IPMI over LAN Policy Encryption.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    templateVars["ipmi_key"] = ipmi_key_function(**templateVars)

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  Now Starting the Local User Policy Section.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    # Local Users
                    templateVars["always_send_user_password"] = False
                    templateVars["enforce_strong_password"] = True
                    templateVars["grace_period"] = 0
                    templateVars["notification_period"] = 15
                    templateVars["password_expiry_duration"] = 90
                    templateVars["password_history"] = 5
                    ilCount = 1
                    local_users = []
                    user_loop = False
                    while user_loop == False:
                        question = input(f'Would you like to configure a Local user?  Enter "Y" or "N" [Y]: ')
                        if question == '' or question == 'Y':
                            local_users,user_loop = local_users_function(
                                jsonData, easy_jsonData, ilCount, **templateVars
                            )
                        elif question == 'N':
                            user_loop = True
                        else:
                            print(f'\n------------------------------------------------------\n')
                            print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                            print(f'\n------------------------------------------------------\n')
                    templateVars["local_users"] = local_users

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  Now Starting the SNMP Policy Section.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    # Pull in the Policies for SNMP Policies
                    jsonVars = jsonData['components']['schemas']['snmp.Policy']['allOf'][1]['properties']

                    # SNMP Contact
                    templateVars["Description"] = jsonVars['SysContact']['description'] + \
                        'Note: Enter a string up to 64 characters, such as an email address or a name and telephone number.'
                    templateVars["varDefault"] = ''
                    templateVars["varInput"] = 'SNMP System Contact:'
                    templateVars["varName"] = 'SNMP System Contact'
                    templateVars["varRegex"] = '.*'
                    templateVars["minLength"] = 1
                    templateVars["maxLength"] = jsonVars['SysContact']['maxLength']
                    templateVars["system_contact"] = varStringLoop(**templateVars)

                    # SNMP Location
                    templateVars["Description"] = jsonVars['SysLocation']['description']
                    templateVars["varDefault"] = ''
                    templateVars["varInput"] = 'What is the Location of the host on which the SNMP agent (server) runs?'
                    templateVars["varName"] = 'SNMP System Location'
                    templateVars["varRegex"] = '.*'
                    templateVars["minLength"] = 1
                    templateVars["maxLength"] = jsonVars['SysLocation']['maxLength']
                    templateVars["system_location"] = varStringLoop(**templateVars)

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
                    if len(snmp_user_list) > 0:
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
                    print(f'  Now Starting the Syslog Policy Section.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    # Syslog Section
                    ilCount = 1
                    syslog_loop = False
                    while syslog_loop == False:
                        question = input(f'Do you want to configure Remote Syslog Servers?  Enter "Y" or "N" [Y]: ')
                        if question == '' or question == 'Y':
                            # Syslog Local Logging
                            jsonVars = jsonData['components']['schemas']['syslog.LocalClientBase']['allOf'][1]['properties']
                            templateVars["var_description"] = jsonVars['MinSeverity']['description']
                            templateVars["jsonVars"] = sorted(jsonVars['MinSeverity']['enum'])
                            templateVars["defaultVar"] = jsonVars['MinSeverity']['default']
                            templateVars["varType"] = 'Syslog Local Minimum Severity'
                            templateVars["min_severity"] = variablesFromAPI(**templateVars)

                            templateVars["local_logging"] = {'file':{'min_severity':templateVars["min_severity"]}}
                            remote_logging = syslog_servers(jsonData, **templateVars)
                            templateVars['remote_logging'] = remote_logging

                            syslog_loop = True

                        elif question == 'N':
                            templateVars["min_severity"] = 'warning'
                            templateVars['remote_logging'] = {}
                            server1 = {
                                'server1':{
                                'enable':False,
                                'hostname':'0.0.0.0',
                                'min_severity':'warning',
                                'port':514,
                                'protocol':'udp'
                                }
                            }
                            server2 = {
                                'server2':{
                                'enable':False,
                                'hostname':'0.0.0.0',
                                'min_severity':'warning',
                                'port':514,
                                'protocol':'udp'
                                }
                            }
                            templateVars['remote_logging'].update(server1)
                            templateVars['remote_logging'].update(server2)

                            syslog_loop = True
                        else:
                            print(f'\n------------------------------------------------------\n')
                            print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                            print(f'\n------------------------------------------------------\n')

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  Policy Variables:')
                    print(f'    IMC Access VLAN  = {imc_vlan}')
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
                    print(f'    System Contact   = "{templateVars["system_contact"]}"')
                    print(f'    System Locaction = "{templateVars["system_location"]}"')
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
                        confirm_policy = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
                        if confirm_policy == 'Y' or confirm_policy == '':

                            #_______________________________________________________________________
                            #
                            # Configure IMC Access Policy
                            #_______________________________________________________________________

                            templateVars["initial_write"] = True
                            templateVars["policy_type"] = 'IMC Access Policy'
                            templateVars["header"] = '%s Variables' % (templateVars["policy_type"])
                            templateVars["template_file"] = 'template_open.jinja2'
                            templateVars["template_type"] = 'imc_access_policies'

                            # Open the Template file
                            write_to_template(self, **templateVars)
                            templateVars["initial_write"] = False

                            # Configure IMC Access Policy
                            name = org
                            templateVars["name"] = name
                            templateVars["descr"] = f'{name} IMC Access Policy'
                            templateVars["inband_ip_pool"] = 'VMWare_KVM'
                            templateVars["inband_vlan_id"] = imc_vlan
                            templateVars["ipv4_address_configuration"] = True
                            templateVars["ipv6_address_configuration"] = False

                            # Write Policies to Template File
                            templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
                            write_to_template(self, **templateVars)

                            # Close the Template file
                            templateVars["template_file"] = 'template_close.jinja2'
                            write_to_template(self, **templateVars)

                            #_______________________________________________________________________
                            #
                            # Configure IPMI over LAN Policy
                            #_______________________________________________________________________

                            templateVars["initial_write"] = True
                            templateVars["policy_type"] = 'IPMI over LAN Policy'
                            templateVars["header"] = '%s Variables' % (templateVars["policy_type"])
                            templateVars["template_file"] = 'template_open.jinja2'
                            templateVars["template_type"] = 'ipmi_over_lan_policies'

                            # Open the Template file
                            write_to_template(self, **templateVars)
                            templateVars["initial_write"] = False

                            # IPMI over LAN Settings
                            name = org
                            templateVars["name"] = name
                            templateVars["descr"] = f'{name} IPMI over LAN Policy'
                            templateVars["enabled"] = True

                            # Write Policies to Template File
                            templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
                            write_to_template(self, **templateVars)

                            # Close the Template file
                            templateVars["template_file"] = 'template_close.jinja2'
                            write_to_template(self, **templateVars)

                            #_______________________________________________________________________
                            #
                            # Configure Local User Policy
                            #_______________________________________________________________________

                            templateVars["initial_write"] = True
                            templateVars["policy_type"] = 'Local User Policy'
                            templateVars["header"] = '%s Variables' % (templateVars["policy_type"])
                            templateVars["template_file"] = 'template_open.jinja2'
                            templateVars["template_type"] = 'local_user_policies'

                            # Open the Template file
                            write_to_template(self, **templateVars)
                            templateVars["initial_write"] = False

                            # Local User Settings
                            name = org
                            templateVars["name"] = name
                            templateVars["descr"] = f'{name} Local User Policy'


                            # Write Policies to Template File
                            templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
                            write_to_template(self, **templateVars)

                            # Close the Template file
                            templateVars["template_file"] = 'template_close.jinja2'
                            write_to_template(self, **templateVars)

                            #_______________________________________________________________________
                            #
                            # Configure Power Policy
                            #_______________________________________________________________________

                            templateVars["initial_write"] = True
                            templateVars["policy_type"] = 'Power Policy'
                            templateVars["header"] = '%s Variables' % (templateVars["policy_type"])
                            templateVars["template_file"] = 'template_open.jinja2'
                            templateVars["template_type"] = 'power_policies'

                            # Open the Template file
                            write_to_template(self, **templateVars)
                            templateVars["initial_write"] = False

                            # Power Settings
                            names = ['5108', '9508', 'Server']
                            for name in names:
                                templateVars["allocated_budget"] = 0
                                templateVars["name"] = name
                                templateVars["descr"] = f'{name} Power Policy'
                                if name == 'Server': templateVars["power_restore_state"] = 'LastState'
                                elif name == '9508': templateVars["allocated_budget"] = 5600

                                templateVars["power_redundancy"] = 'Grid'

                                # Write Policies to Template File
                                templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
                                write_to_template(self, **templateVars)

                            # Close the Template file
                            templateVars["template_file"] = 'template_close.jinja2'
                            write_to_template(self, **templateVars)

                            #_______________________________________________________________________
                            #
                            # Configure Serial over LAN Policy
                            #_______________________________________________________________________

                            templateVars["initial_write"] = True
                            templateVars["policy_type"] = 'Serial over LAN Policy'
                            templateVars["header"] = '%s Variables' % (templateVars["policy_type"])
                            templateVars["template_file"] = 'template_open.jinja2'
                            templateVars["template_type"] = 'serial_over_lan_policies'

                            # Open the Template file
                            write_to_template(self, **templateVars)
                            templateVars["initial_write"] = False

                            # Serial over LAN Settings
                            name = org
                            templateVars["name"] = name
                            templateVars["descr"] = f'{name} Serial over LAN Policy'
                            templateVars["enabled"] = True
                            templateVars["baud_rate"] = 115200
                            templateVars["com_port"] = 'com0'
                            templateVars["ssh_port"] = 2400

                            # Write Policies to Template File
                            templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
                            write_to_template(self, **templateVars)

                            # Close the Template file
                            templateVars["template_file"] = 'template_close.jinja2'
                            write_to_template(self, **templateVars)

                            #_______________________________________________________________________
                            #
                            # Configure SNMP Policy
                            #_______________________________________________________________________

                            templateVars["initial_write"] = True
                            templateVars["policy_type"] = 'SNMP Policy'
                            templateVars["header"] = '%s Variables' % (templateVars["policy_type"])
                            templateVars["template_file"] = 'template_open.jinja2'
                            templateVars["template_type"] = 'snmp_policies'

                            # Open the Template file
                            write_to_template(self, **templateVars)
                            templateVars["initial_write"] = False

                            # SNMP Settings
                            name = org
                            templateVars["name"] = name
                            templateVars["descr"] = f'{name} SNMP Policy'
                            templateVars["access_community_string"] = ''
                            templateVars["enabled"] = True
                            templateVars["engine_input_id"] = ''
                            templateVars["port"] = 161
                            templateVars["snmp_community_access"] = 'Disabled'
                            templateVars["trap_community_string"] = ''

                            # Write Policies to Template File
                            templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
                            write_to_template(self, **templateVars)

                            # Close the Template file
                            templateVars["template_file"] = 'template_close.jinja2'
                            write_to_template(self, **templateVars)

                            #_______________________________________________________________________
                            #
                            # Configure Syslog Policy
                            #_______________________________________________________________________

                            templateVars["initial_write"] = True
                            templateVars["policy_type"] = 'Syslog Policy'
                            templateVars["header"] = '%s Variables' % (templateVars["policy_type"])
                            templateVars["template_file"] = 'template_open.jinja2'
                            templateVars["template_type"] = 'syslog_policies'

                            # Open the Template file
                            write_to_template(self, **templateVars)
                            templateVars["initial_write"] = False

                            # Syslog Settings
                            name = org
                            templateVars["name"] = name
                            templateVars["descr"] = f'{name} Syslog Policy'

                            # Write Policies to Template File
                            templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
                            write_to_template(self, **templateVars)

                            # Close the Template file
                            templateVars["template_file"] = 'template_close.jinja2'
                            write_to_template(self, **templateVars)

                            #_______________________________________________________________________
                            #
                            # Configure Thermal Policy
                            #_______________________________________________________________________

                            templateVars["initial_write"] = True
                            templateVars["policy_type"] = 'Thermal Policy'
                            templateVars["header"] = '%s Variables' % (templateVars["policy_type"])
                            templateVars["template_file"] = 'template_open.jinja2'
                            templateVars["template_type"] = 'thermal_policies'

                            # Open the Template file
                            write_to_template(self, **templateVars)
                            templateVars["initial_write"] = False

                            # Thermal Settings
                            names = ['5108', '9508']
                            for name in names:
                                templateVars["name"] = name
                                templateVars["descr"] = f'{name} Thermal Policy'
                                templateVars["fan_control_mode"] = 'Balanced'

                                # Write Policies to Template File
                                templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
                                write_to_template(self, **templateVars)

                            # Close the Template file
                            templateVars["template_file"] = 'template_close.jinja2'
                            write_to_template(self, **templateVars)

                            #_______________________________________________________________________
                            #
                            # Configure Virtual KVM Policy
                            #_______________________________________________________________________

                            templateVars["initial_write"] = True
                            templateVars["policy_type"] = 'Virtual KVM Policy'
                            templateVars["header"] = '%s Variables' % (templateVars["policy_type"])
                            templateVars["template_file"] = 'template_open.jinja2'
                            templateVars["template_type"] = 'virtual_kvm_policies'

                            # Open the Template file
                            write_to_template(self, **templateVars)
                            templateVars["initial_write"] = False

                            # Virtual KVM Settings
                            name = org
                            templateVars["name"] = name
                            templateVars["descr"] = f'{name} Virtual KVM Policy'
                            templateVars["enable_local_server_video"] = True
                            templateVars["enable_video_encryption"] = True
                            templateVars["enable_virtual_kvm"] = True
                            templateVars["remote_port"] = 2068

                            # Write Policies to Template File
                            templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
                            write_to_template(self, **templateVars)

                            # Close the Template file
                            templateVars["template_file"] = 'template_close.jinja2'
                            write_to_template(self, **templateVars)

                            configure_loop = True
                            policy_loop = True
                            valid_confirm = True

                        elif confirm_policy == 'N':
                            print(f'\n------------------------------------------------------\n')
                            print(f'  Starting Section over.')
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

    #==============================================
    # UCS Domain and Policies
    #==============================================
    def server_profiles(self, jsonData, easy_jsonData, **kwargs):
        name_prefix = self.name_prefix
        org = self.org
        server_type = 'profiles'
        templateVars = {}
        templateVars["org"] = org
        templateVars["fc_ports"] = kwargs["fc_ports"]
        templateVars["server_type"] = kwargs["server_type"]
        templateVars["boot_order_policy"] = kwargs["boot_order_policy"]

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  The Quick Deployment Module - Domain Policies, will configure pools for a UCS Domain ')
            print(f'  Profile.\n')
            print(f'  This wizard will save the output for these pools in the following files:\n')
            print(f'  - Intersight/{org}/{self.type}/ucs_server_profile_templates.auto.tfvars')
            print(f'  - Intersight/{org}/{self.type}/ucs_server_profiles.auto.tfvars')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to run the Quick Deployment Module - Server Profiles Configuration?  \nEnter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                policy_loop = False
                while policy_loop == False:
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  Below are the Questions that will be asked by the Server Profiles Portion of the wizard.')
                    print(f'   - Number of Servers you are going to deploy.')
                    print(f'   - Name of the Server Profile(s).')
                    print(f'   - Serial Number of the Server Profile(s).')
                    print(f'\n-------------------------------------------------------------------------------------------\n')

                    #_______________________________________________________________________
                    #
                    # Configure UCS Chassis Profile
                    #_______________________________________________________________________
                    profiles(name_prefix, org, self.type).quick_start_server_profiles(**templateVars)
                    profiles(name_prefix, org, self.type).quick_start_server_templates(**templateVars)
                    policy_loop = True
                    configure_loop = True

            elif configure == 'N':
                configure_loop = True
            else:
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                print(f'\n-------------------------------------------------------------------------------------------\n')
        
    #==============================================
    # Standalone Server Policies
    #==============================================
    def standalone_policies(self, jsonData, easy_jsonData):
        name_prefix = self.name_prefix
        org = self.org
        templateVars = {}
        templateVars["org"] = org

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  The Quick Deployment Module - Pools, will configure pools for a UCS Server Profile')
            print(f'  connected to an IMM Domain.\n')
            print(f'  This wizard will save the output for these pools in the following files:\n')
            print(f'  - Intersight/{org}/{self.type}/adapter_configuration_policies.auto.tfvars')
            print(f'  - Intersight/{org}/{self.type}/device_connector_policies.auto.tfvars')
            print(f'  - Intersight/{org}/{self.type}/ethernet_network_policies.auto.tfvars')
            print(f'  - Intersight/{org}/{self.type}/ldap_policies.auto.tfvars')
            print(f'  - Intersight/{org}/{self.type}/network_connectivity_policies.auto.tfvars')
            print(f'  - Intersight/{org}/{self.type}/ntp_policies.auto.tfvars')
            print(f'  - Intersight/{org}/{self.type}/persistent_memory_policies.auto.tfvars')
            print(f'  - Intersight/{org}/{self.type}/smtp_policies.auto.tfvars')
            print(f'  - Intersight/{org}/{self.type}/ssh_policies.auto.tfvars')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to run the Quick Deployment Module - Standalone Policy Configuration?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                loop_count = 1
                policy_loop = False
                while policy_loop == False:
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  Below are the Questions that will be asked by the Policies Portion of the wizard.')
                    print(f'   - If the Server will Have a VIC Installed.')
                    print(f'     * What the Ethernet Settings should be.')
                    print(f'   - DNS Servers (Primary/Secondary).')
                    print(f'   - LDAP Policy (Optional).')
                    print(f'     * Base Distinguished Name')
                    print(f'     * LDAP Groups')
                    print(f'     * LDAP Security')
                    print(f'   - NTP Configuration:')
                    print(f'     * Timezone')
                    print(f'     * NTP Servers')
                    print(f'   - Persistent Memory Policies (Optional)')
                    print(f'   - SMTP Policy (Optional)')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    # Pull in the Policies for SNMP Policies
                    jsonVars = jsonData['components']['schemas']['snmp.Policy']['allOf'][1]['properties']

                    # SNMP Contact
                    templateVars["Description"] = jsonVars['SysContact']['description'] + \
                        'Note: Enter a string up to 64 characters, such as an email address or a name and telephone number.'
                    templateVars["varDefault"] = ''
                    templateVars["varInput"] = 'SNMP System Contact:'
                    templateVars["varName"] = 'SNMP System Contact'
                    templateVars["varRegex"] = '.*'
                    templateVars["minLength"] = 1
                    templateVars["maxLength"] = jsonVars['SysContact']['maxLength']
                    templateVars["system_contact"] = varStringLoop(**templateVars)

                    # SNMP Location
                    templateVars["Description"] = jsonVars['SysLocation']['description']
                    templateVars["varDefault"] = ''
                    templateVars["varInput"] = 'What is the Location of the host on which the SNMP agent (server) runs?'
                    templateVars["varName"] = 'SNMP System Location'
                    templateVars["varRegex"] = '.*'
                    templateVars["minLength"] = 1
                    templateVars["maxLength"] = jsonVars['SysLocation']['maxLength']
                    templateVars["system_location"] = varStringLoop(**templateVars)

                    # SNMP Users
                    snmp_user_list = []
                    inner_loop_count = 1
                    snmp_loop = False
                    while snmp_loop == False:
                        question = input(f'Would you like to configure an SNMPv3 User?  Enter "Y" or "N" [Y]: ')
                        if question == '' or question == 'Y':
                            snmp_user_list,snmp_loop = snmp_users(jsonData, inner_loop_count, **templateVars)
                        elif question == 'N':
                            snmp_loop = True
                        else:
                            print(f'\n------------------------------------------------------\n')
                            print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                            print(f'\n------------------------------------------------------\n')
                    templateVars["users"] = snmp_user_list

                    # SNMP Trap Destinations
                    snmp_dests = []
                    inner_loop_count = 1
                    snmp_loop = False
                    if len(snmp_user_list) > 0:
                        while snmp_loop == False:
                            question = input(f'Would you like to configure SNMP Trap Destionations?  Enter "Y" or "N" [Y]: ')
                            if question == '' or question == 'Y':
                                snmp_dests,snmp_loop = snmp_trap_servers(jsonData, inner_loop_count, snmp_user_list, **templateVars)
                            elif question == 'N':
                                snmp_loop = True
                            else:
                                print(f'\n------------------------------------------------------\n')
                                print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                                print(f'\n------------------------------------------------------\n')
                    templateVars["trap_destinations"] = snmp_dests

                    # Syslog Local Logging
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
                    print(f'  Network Configuration Variables:"')
                    print(f'    System Contact   = "{templateVars["system_contact"]}"')
                    print(f'    System Locaction = "{templateVars["system_location"]}"')
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
                        confirm_policy = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
                        if confirm_policy == 'Y' or confirm_policy == '':
                            confirm_policy = 'Y'

                            #_______________________________________________________________________
                            #
                            # Configure BIOS Policy
                            #_______________________________________________________________________

                            templateVars["initial_write"] = True
                            templateVars["policy_type"] = 'BIOS Policy'
                            templateVars["header"] = '%s Variables' % (templateVars["policy_type"])
                            templateVars["template_file"] = 'template_open.jinja2'
                            templateVars["template_type"] = 'bios_policies'

                            # Open the Template file
                            write_to_template(self, **templateVars)
                            templateVars["initial_write"] = False

                            # Configure BIOS Policy
                            name = 'VMware'
                            templateVars["name"] = name
                            templateVars["descr"] = f'{name} BIOS Policy'
                            templateVars["bios_template"] = 'VMware'

                            # Write Policies to Template File
                            templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
                            write_to_template(self, **templateVars)

                            # Close the Template file
                            templateVars["template_file"] = 'template_close.jinja2'
                            write_to_template(self, **templateVars)

                            #_______________________________________________________________________
                            #
                            # Configure Boot Order Policy
                            #_______________________________________________________________________

                            templateVars["initial_write"] = True
                            templateVars["policy_type"] = 'Boot Order Policy'
                            templateVars["header"] = '%s Variables' % (templateVars["policy_type"])
                            templateVars["template_file"] = 'template_open.jinja2'
                            templateVars["template_type"] = 'boot_order_policies'

                            # Open the Template file
                            write_to_template(self, **templateVars)
                            templateVars["initial_write"] = False

                            # Configure Boot Order Policy
                            name = 'VMware_M2'
                            templateVars["name"] = name
                            templateVars["descr"] = f'{name} Boot Order Policy'
                            templateVars["boot_mode"] = 'Uefi'
                            templateVars["enable_secure_boot"] = True
                            templateVars["boot_mode"] = 'Uefi'
                            templateVars["boot_devices"] = [
                                {
                                    'enabled':True,
                                    'device_name':'kvm-dvd',
                                    'object_type':'boot.VirtualMedia',
                                    'Subtype':'cimc-mapped-dvd'
                                },
                                {
                                    'device_name':'m2',
                                    'enabled':True,
                                    'object_type':'boot.LocalDisk',
                                    'Slot':'MSTOR-RAID'
                                },
                                {
                                    'device_name':'pxe',
                                    'enabled':True,
                                    'InterfaceName':'MGMT-A',
                                    'InterfaceSource':'name',
                                    'IpType':'IPv4',
                                    'MacAddress':'',
                                    'object_type':'boot.Pxe',
                                    'Port':-1,
                                    'Slot':'MLOM'
                                }
                            ]

                            # Write Policies to Template File
                            templateVars["template_file"] = '%s.jinja2' % ('boot_policies')
                            write_to_template(self, **templateVars)

                            # Close the Template file
                            templateVars["template_file"] = 'template_close.jinja2'
                            write_to_template(self, **templateVars)

                            #_______________________________________________________________________
                            #
                            # Configure IMC Access Policy
                            #_______________________________________________________________________

                            templateVars["initial_write"] = True
                            templateVars["policy_type"] = 'IMC Access Policy'
                            templateVars["header"] = '%s Variables' % (templateVars["policy_type"])
                            templateVars["template_file"] = 'template_open.jinja2'
                            templateVars["template_type"] = 'imc_access_policies'

                            # Open the Template file
                            write_to_template(self, **templateVars)
                            templateVars["initial_write"] = False

                            # Configure IMC Access Policy
                            name = org
                            templateVars["name"] = name
                            templateVars["descr"] = f'{name} IMC Access Policy'
                            templateVars["inband_ip_pool"] = 'VMWare_KVM'
                            templateVars["ipv4_address_configuration"] = True
                            templateVars["ipv6_address_configuration"] = False

                            # Write Policies to Template File
                            templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
                            write_to_template(self, **templateVars)

                            # Close the Template file
                            templateVars["template_file"] = 'template_close.jinja2'
                            write_to_template(self, **templateVars)

                            #_______________________________________________________________________
                            #
                            # Configure IPMI over LAN Policy
                            #_______________________________________________________________________

                            templateVars["initial_write"] = True
                            templateVars["policy_type"] = 'IPMI over LAN Policy'
                            templateVars["header"] = '%s Variables' % (templateVars["policy_type"])
                            templateVars["template_file"] = 'template_open.jinja2'
                            templateVars["template_type"] = 'ipmi_over_lan_policies'

                            # Open the Template file
                            write_to_template(self, **templateVars)
                            templateVars["initial_write"] = False

                            # IPMI over LAN Settings
                            name = org
                            templateVars["name"] = name
                            templateVars["descr"] = f'{name} IPMI over LAN Policy'
                            templateVars["enabled"] = True
                            templateVars["ipmi_key"] = 1

                            # Write Policies to Template File
                            templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
                            write_to_template(self, **templateVars)

                            # Close the Template file
                            templateVars["template_file"] = 'template_close.jinja2'
                            write_to_template(self, **templateVars)

                            #_______________________________________________________________________
                            #
                            # Configure Local User Policy
                            #_______________________________________________________________________

                            templateVars["initial_write"] = True
                            templateVars["policy_type"] = 'Local User Policy'
                            templateVars["header"] = '%s Variables' % (templateVars["policy_type"])
                            templateVars["template_file"] = 'template_open.jinja2'
                            templateVars["template_type"] = 'local_user_policies'

                            # Open the Template file
                            write_to_template(self, **templateVars)
                            templateVars["initial_write"] = False

                            # Local User Settings
                            name = org
                            templateVars["name"] = name
                            templateVars["descr"] = f'{name} Local User Policy'
                            templateVars["enabled"] = True
                            templateVars["ipmi_key"] = 1

                            # Write Policies to Template File
                            templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
                            write_to_template(self, **templateVars)

                            # Close the Template file
                            templateVars["template_file"] = 'template_close.jinja2'
                            write_to_template(self, **templateVars)

                            #_______________________________________________________________________
                            #
                            # Configure Power Policy
                            #_______________________________________________________________________

                            templateVars["initial_write"] = True
                            templateVars["policy_type"] = 'Power Policy'
                            templateVars["header"] = '%s Variables' % (templateVars["policy_type"])
                            templateVars["template_file"] = 'template_open.jinja2'
                            templateVars["template_type"] = 'power_policies'

                            # Open the Template file
                            write_to_template(self, **templateVars)
                            templateVars["initial_write"] = False

                            # Power Settings
                            names = ['5108', '9508', 'Server']
                            for name in names:
                                templateVars["allocated_budget"] = 0
                                templateVars["name"] = name
                                templateVars["descr"] = f'{name} Power Policy'
                                if name == 'Server': templateVars["power_restore_state"] = 'LastState'
                                elif name == '9508': templateVars["allocated_budget"] = 5600

                                templateVars["power_redundancy"] = 'Grid'
                                templateVars["ipmi_key"] = 1

                                # Write Policies to Template File
                                templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
                                write_to_template(self, **templateVars)

                            # Close the Template file
                            templateVars["template_file"] = 'template_close.jinja2'
                            write_to_template(self, **templateVars)

                            #_______________________________________________________________________
                            #
                            # Configure Serial over LAN Policy
                            #_______________________________________________________________________

                            templateVars["initial_write"] = True
                            templateVars["policy_type"] = 'Serial over LAN Policy'
                            templateVars["header"] = '%s Variables' % (templateVars["policy_type"])
                            templateVars["template_file"] = 'template_open.jinja2'
                            templateVars["template_type"] = 'serial_over_lan_policies'

                            # Open the Template file
                            write_to_template(self, **templateVars)
                            templateVars["initial_write"] = False

                            # Serial over LAN Settings
                            name = org
                            templateVars["name"] = name
                            templateVars["descr"] = f'{name} Serial over LAN Policy'
                            templateVars["enabled"] = True
                            templateVars["baud_rate"] = 115200
                            templateVars["com_port"] = 'com0'
                            templateVars["ssh_port"] = 2400

                            # Write Policies to Template File
                            templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
                            write_to_template(self, **templateVars)

                            # Close the Template file
                            templateVars["template_file"] = 'template_close.jinja2'
                            write_to_template(self, **templateVars)

                            #_______________________________________________________________________
                            #
                            # Configure SNMP Policy
                            #_______________________________________________________________________

                            templateVars["initial_write"] = True
                            templateVars["policy_type"] = 'SNMP Policy'
                            templateVars["header"] = '%s Variables' % (templateVars["policy_type"])
                            templateVars["template_file"] = 'template_open.jinja2'
                            templateVars["template_type"] = 'snmp_policies'

                            # Open the Template file
                            write_to_template(self, **templateVars)
                            templateVars["initial_write"] = False

                            # SNMP Settings
                            name = org
                            templateVars["name"] = name
                            templateVars["descr"] = f'{name} SNMP Policy'
                            templateVars["access_community_string"] = ''
                            templateVars["enabled"] = True
                            templateVars["engine_input_id"] = ''
                            templateVars["port"] = 161
                            templateVars["snmp_community_access"] = 'Disabled'
                            templateVars["trap_community_string"] = ''

                            # Write Policies to Template File
                            templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
                            write_to_template(self, **templateVars)

                            # Close the Template file
                            templateVars["template_file"] = 'template_close.jinja2'
                            write_to_template(self, **templateVars)

                            #_______________________________________________________________________
                            #
                            # Configure Storage Policy
                            #_______________________________________________________________________

                            templateVars["initial_write"] = True
                            templateVars["policy_type"] = 'Storage Policy'
                            templateVars["header"] = '%s Variables' % (templateVars["policy_type"])
                            templateVars["template_file"] = 'template_open.jinja2'
                            templateVars["template_type"] = 'storage_policies'

                            # Open the Template file
                            write_to_template(self, **templateVars)
                            templateVars["initial_write"] = False

                            name = 'M2_Raid'
                            templateVars["name"] = name
                            templateVars["descr"] = f'{name} Storage Policy'
                            templateVars["drive_group"] = {}
                            templateVars["global_hot_spares"] = ''
                            templateVars["m2_configuration"] = [ { 'controller_slot':'MSTOR-RAID-1,MSTOR-RAID-2' } ]
                            templateVars["single_drive_raid_configuration"] = {}
                            templateVars["unused_disks_state"] = 'No Change'
                            templateVars["use_jbod_for_vd_creation"] = True

                            # Write Policies to Template File
                            templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
                            write_to_template(self, **templateVars)

                            # Close the Template file
                            templateVars["template_file"] = 'template_close.jinja2'
                            write_to_template(self, **templateVars)

                            #_______________________________________________________________________
                            #
                            # Configure Syslog Policy
                            #_______________________________________________________________________

                            templateVars["initial_write"] = True
                            templateVars["policy_type"] = 'Syslog Policy'
                            templateVars["header"] = '%s Variables' % (templateVars["policy_type"])
                            templateVars["template_file"] = 'template_open.jinja2'
                            templateVars["template_type"] = 'syslog_policies'

                            # Open the Template file
                            write_to_template(self, **templateVars)
                            templateVars["initial_write"] = False

                            # Syslog Settings
                            name = org
                            templateVars["name"] = name
                            templateVars["descr"] = f'{name} Syslog Policy'
                            templateVars["enabled"] = True
                            templateVars["ipmi_key"] = 1

                            # Write Policies to Template File
                            templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
                            write_to_template(self, **templateVars)

                            # Close the Template file
                            templateVars["template_file"] = 'template_close.jinja2'
                            write_to_template(self, **templateVars)

                            #_______________________________________________________________________
                            #
                            # Configure Thermal Policy
                            #_______________________________________________________________________

                            templateVars["initial_write"] = True
                            templateVars["policy_type"] = 'Thermal Policy'
                            templateVars["header"] = '%s Variables' % (templateVars["policy_type"])
                            templateVars["template_file"] = 'template_open.jinja2'
                            templateVars["template_type"] = 'thermal_policies'

                            # Open the Template file
                            write_to_template(self, **templateVars)
                            templateVars["initial_write"] = False

                            # Thermal Settings
                            names = ['5108', '9508']
                            for name in names:
                                templateVars["name"] = name
                                templateVars["descr"] = f'{name} Thermal Policy'
                                templateVars["fan_control_mode"] = 'Balanced'

                                # Write Policies to Template File
                                templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
                                write_to_template(self, **templateVars)

                            # Close the Template file
                            templateVars["template_file"] = 'template_close.jinja2'
                            write_to_template(self, **templateVars)

                        elif confirm_policy == 'N':
                            print(f'\n------------------------------------------------------\n')
                            print(f'  Starting Section over.')
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

    #==============================================
    # VMware M2 - Boot and Storage Policies
    #==============================================
    def vmware_m2(self):
        org = self.org
        templateVars = {}
        templateVars["org"] = org

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  The Quick Deployment Module - Boot/Storage, will configure policies for a UCS Server ')
            print(f'  Profile connected to an IMM Domain.\n')
            print(f'  This wizard will save the output for these pools in the following files:\n')
            print(f'  - Intersight/{org}/{self.type}/boot_order_policies.auto.tfvars')
            print(f'  - Intersight/{org}/{self.type}/storage_policies.auto.tfvars')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to run the Quick Deployment Module - Boot/Storage Configuration?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                # Trusted Platform Module
                templateVars["Description"] = 'Flag to Determine if the Servers have a TPM Installed.'
                templateVars["varInput"] = f'Will these servers have a TPM Module Installed?'
                templateVars["varDefault"] = 'Y'
                templateVars["varName"] = 'TPM Installed'
                tpm_installed = varBoolLoop(**templateVars)

                #_______________________________________________________________________
                #
                # Configure BIOS Policy
                #_______________________________________________________________________

                templateVars["initial_write"] = True
                templateVars["policy_type"] = 'BIOS Policy'
                templateVars["header"] = '%s Variables' % (templateVars["policy_type"])
                templateVars["template_file"] = 'template_open.jinja2'
                templateVars["template_type"] = 'bios_policies'

                # Open the Template file
                write_to_template(self, **templateVars)
                templateVars["initial_write"] = False

                # Configure BIOS Policy
                name = 'VMware'
                templateVars["name"] = name
                templateVars["descr"] = f'{name} BIOS Policy'
                if tpm_installed == True:
                    templateVars["policy_template"] = 'VMware_tpm'
                else:
                    templateVars["policy_template"] = 'VMware'

                # Write Policies to Template File
                templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
                write_to_template(self, **templateVars)

                # Close the Template file
                templateVars["template_file"] = 'template_close.jinja2'
                write_to_template(self, **templateVars)

                #_______________________________________________________________________
                #
                # Configure Boot Order Policy
                #_______________________________________________________________________

                templateVars["initial_write"] = True
                templateVars["policy_type"] = 'Boot Order Policy'
                templateVars["header"] = '%s Variables' % (templateVars["policy_type"])
                templateVars["template_file"] = 'template_open.jinja2'
                templateVars["template_type"] = 'boot_order_policies'

                # Open the Template file
                write_to_template(self, **templateVars)
                templateVars["initial_write"] = False

                secBootList = [False, True]
                for i in secBootList:
                    # Configure Boot Order Policy
                    if i == False:
                        name = 'VMware_M2_pxe'
                    else:
                        name = 'VMware_M2'
                    templateVars["name"] = name
                    templateVars["descr"] = f'{name} Boot Order Policy'
                    templateVars["boot_mode"] = 'Uefi'
                    if tpm_installed == True:
                        templateVars["enable_secure_boot"] = i
                    else:
                        templateVars["enable_secure_boot"] = False
                    templateVars["boot_mode"] = 'Uefi'
                    if i == False:
                        templateVars["boot_devices"] = [
                            {
                                'enabled':True,
                                'device_name':'KVM-DVD',
                                'device_type':'virtual_media',
                                'object_type':'boot.VirtualMedia',
                                'subtype':'kvm-mapped-dvd'
                            },
                            {
                                'device_name':'M2',
                                'device_type':'local_disk',
                                'enabled':True,
                                'object_type':'boot.LocalDisk',
                                'slot':'MSTOR-RAID'
                            },
                            {
                                'device_name':'PXE',
                                'device_type':'pxe_boot',
                                'enabled':True,
                                'interface_name':'MGMT-A',
                                'interface_source':'name',
                                'ip_type':'IPv4',
                                'object_type':'boot.Pxe',
                                'slot':'MLOM'
                            }
                        ]
                    else:
                        templateVars["boot_devices"] = [
                            {
                                'enabled':True,
                                'device_name':'KVM-DVD',
                                'device_type':'virtual_media',
                                'object_type':'boot.VirtualMedia',
                                'subtype':'kvm-mapped-dvd'
                            },
                            {
                                'device_name':'M2',
                                'device_type':'local_disk',
                                'enabled':True,
                                'object_type':'boot.LocalDisk',
                                'slot':'MSTOR-RAID'
                            }
                        ]

                    # Write Policies to Template File
                    templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
                    write_to_template(self, **templateVars)

                # Close the Template file
                templateVars["template_file"] = 'template_close.jinja2'
                write_to_template(self, **templateVars)

                #_______________________________________________________________________
                #
                # Configure Storage Policy
                #_______________________________________________________________________

                templateVars["initial_write"] = True
                templateVars["policy_type"] = 'Storage Policy'
                templateVars["header"] = '%s Variables' % (templateVars["policy_type"])
                templateVars["template_file"] = 'template_open.jinja2'
                templateVars["template_type"] = 'storage_policies'

                # Open the Template file
                write_to_template(self, **templateVars)
                templateVars["initial_write"] = False

                # Storage Policy Settings
                name = 'M2_Raid'
                templateVars["name"] = name
                templateVars["descr"] = f'{name} Storage Policy'
                templateVars["drive_group"] = {}
                templateVars["global_hot_spares"] = ''
                templateVars["m2_configuration"] = { 'controller_slot':'MSTOR-RAID-1,MSTOR-RAID-2' }
                templateVars["single_drive_raid_configuration"] = {}
                templateVars["unused_disks_state"] = 'No Change'
                templateVars["use_jbod_for_vd_creation"] = True

                # Write Policies to Template File
                templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
                write_to_template(self, **templateVars)

                # Close the Template file
                templateVars["template_file"] = 'template_close.jinja2'
                write_to_template(self, **templateVars)

                configure_loop = True

            elif configure == 'N':
                configure_loop = True
            else:
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                print(f'\n-------------------------------------------------------------------------------------------\n')

    #================================================
    # VMware Raid1 - BIOS, Boot and Storage Policies
    #================================================
    def vmware_raid1(self):
        org = self.org
        templateVars = {}
        templateVars["org"] = org

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  The Quick Deployment Module - Boot/Storage, will configure policies for a UCS Server ')
            print(f'  Profile connected to an IMM Domain.\n')
            print(f'  This wizard will save the output for these pools in the following files:\n')
            print(f'  - Intersight/{org}/{self.type}/bios_policies.auto.tfvars')
            print(f'  - Intersight/{org}/{self.type}/boot_order_policies.auto.tfvars')
            print(f'  - Intersight/{org}/{self.type}/storage_policies.auto.tfvars')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to run the Quick Deployment Module - Boot/Storage Configuration?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                # Trusted Platform Module
                templateVars["Description"] = 'Flag to Determine if the Servers have a TPM Installed.'
                templateVars["varInput"] = f'Will these servers have a TPM Module Installed?'
                templateVars["varDefault"] = 'Y'
                templateVars["varName"] = 'TPM Installed'
                tpm_installed = varBoolLoop(**templateVars)

                #_______________________________________________________________________
                #
                # Configure BIOS Policy
                #_______________________________________________________________________

                templateVars["initial_write"] = True
                templateVars["policy_type"] = 'BIOS Policy'
                templateVars["header"] = '%s Variables' % (templateVars["policy_type"])
                templateVars["template_file"] = 'template_open.jinja2'
                templateVars["template_type"] = 'bios_policies'

                # Open the Template file
                write_to_template(self, **templateVars)
                templateVars["initial_write"] = False

                # Configure BIOS Policy
                name = 'VMware'
                templateVars["name"] = name
                templateVars["descr"] = f'{name} BIOS Policy'
                if tpm_installed == True:
                    templateVars["policy_template"] = 'VMware_tpm'
                else:
                    templateVars["policy_template"] = 'VMware'

                # Write Policies to Template File
                templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
                write_to_template(self, **templateVars)

                # Close the Template file
                templateVars["template_file"] = 'template_close.jinja2'
                write_to_template(self, **templateVars)

                #_______________________________________________________________________
                #
                # Configure Boot Order Policy
                #_______________________________________________________________________

                templateVars["initial_write"] = True
                templateVars["policy_type"] = 'Boot Order Policy'
                templateVars["header"] = '%s Variables' % (templateVars["policy_type"])
                templateVars["template_file"] = 'template_open.jinja2'
                templateVars["template_type"] = 'boot_order_policies'

                # Open the Template file
                write_to_template(self, **templateVars)
                templateVars["initial_write"] = False

                secBootList = [False, True]
                for i in secBootList:
                    # Configure Boot Order Policy
                    if i == False:
                        name = 'VMware_Raid1_pxe'
                    else:
                        name = 'VMware_Raid1'
                    templateVars["name"] = name
                    templateVars["descr"] = f'{name} Boot Order Policy'
                    templateVars["boot_mode"] = 'Uefi'
                    if tpm_installed == True:
                        templateVars["enable_secure_boot"] = i
                    else:
                        templateVars["enable_secure_boot"] = False
                    templateVars["boot_mode"] = 'Uefi'
                    if i == False:
                        templateVars["boot_devices"] = [
                            {
                                'enabled':True,
                                'device_name':'KVM-DVD',
                                'device_type':'virtual_media',
                                'object_type':'boot.VirtualMedia',
                                'subtype':'kvm-mapped-dvd'
                            },
                            {
                                'device_name':'MRAID',
                                'device_type':'local_disk',
                                'enabled':True,
                                'object_type':'boot.LocalDisk',
                                'slot':'MRAID'
                            },
                            {
                                'device_name':'PXE',
                                'device_type':'pxe_boot',
                                'enabled':True,
                                'interface_name':'MGMT-A',
                                'interface_source':'name',
                                'ip_type':'IPv4',
                                'object_type':'boot.Pxe',
                                'slot':'MLOM'
                            }
                        ]
                    else:
                        templateVars["boot_devices"] = [
                            {
                                'enabled':True,
                                'device_name':'KVM-DVD',
                                'device_type':'virtual_media',
                                'object_type':'boot.VirtualMedia',
                                'subtype':'kvm-mapped-dvd'
                            },
                            {
                                'device_name':'MRAID',
                                'device_type':'local_disk',
                                'enabled':True,
                                'object_type':'boot.LocalDisk',
                                'slot':'MRAID'
                            }
                        ]

                    # Write Policies to Template File
                    templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
                    write_to_template(self, **templateVars)

                # Close the Template file
                templateVars["template_file"] = 'template_close.jinja2'
                write_to_template(self, **templateVars)

                #_______________________________________________________________________
                #
                # Configure Storage Policy
                #_______________________________________________________________________

                templateVars["initial_write"] = True
                templateVars["policy_type"] = 'Storage Policy'
                templateVars["header"] = '%s Variables' % (templateVars["policy_type"])
                templateVars["template_file"] = 'template_open.jinja2'
                templateVars["template_type"] = 'storage_policies'

                # Open the Template file
                write_to_template(self, **templateVars)
                templateVars["initial_write"] = False

                name = 'MRAID'
                templateVars["name"] = name
                templateVars["descr"] = f'{name} Storage Policy'
                templateVars["drive_group"] = [
                    {
                        'drive_group_name':'DG1',
                        'manual_drive_selection':{
                            'drive_array_spans':[
                                {
                                    'slots':'1,2'
                                }
                            ]
                        },
                        'raid_level':'Raid1',
                        'virtual_drives':[
                            {
                                'access_policy':'Default',
                                'boot_drive':True,
                                'disk_cache':'Default',
                                'expand_to_available':True,
                                'read_policy':'Always Read Ahead',
                                'size':10,
                                'stripe_size':'64KiB',
                                'vd_name':'VD1',
                                'write_policy':'Write Back Good BBU'
                            }
                        ]
                    }
                ]
                templateVars["global_hot_spares"] = ''
                templateVars["m2_configuration"] = []
                templateVars["single_drive_raid_configuration"] = {}
                templateVars["unused_disks_state"] = 'No Change'
                templateVars["use_jbod_for_vd_creation"] = True

                # Write Policies to Template File
                templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
                write_to_template(self, **templateVars)

                # Close the Template file
                templateVars["template_file"] = 'template_close.jinja2'
                write_to_template(self, **templateVars)

                configure_loop = True

            elif configure == 'N':
                configure_loop = True
            else:
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                print(f'\n-------------------------------------------------------------------------------------------\n')

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
                policies_p1(name_prefix, templateVars["org"], inner_type).adapter_configuration_policies(jsonData, easy_jsonData)
            elif inner_policy == 'bios_policies':
                policies_p1(name_prefix, templateVars["org"], inner_type).bios_policies(jsonData, easy_jsonData)
            elif inner_policy == 'boot_order_policies':
                policies_p1(name_prefix, templateVars["org"], inner_type).boot_order_policies(jsonData, easy_jsonData)
            elif inner_policy == 'certificate_management_policies':
                policies_p1(name_prefix, templateVars["org"], inner_type).certificate_management_policies(jsonData, easy_jsonData)
            elif inner_policy == 'device_connector_policies':
                policies_p1(name_prefix, templateVars["org"], inner_type).device_connector_policies(jsonData, easy_jsonData)
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
                policies_p1(name_prefix, templateVars["org"], inner_type).flow_control_policies(jsonData, easy_jsonData)
            elif inner_policy == 'imc_access_policies':
                policies_p1(name_prefix, templateVars["org"], inner_type).imc_access_policies(jsonData, easy_jsonData)
            elif inner_policy == 'ipmi_over_lan_policies':
                policies_p1(name_prefix, templateVars["org"], inner_type).ipmi_over_lan_policies(jsonData, easy_jsonData)
            elif inner_policy == 'iscsi_adapter_policies':
                policies_lan(name_prefix, templateVars["org"], inner_type).iscsi_adapter_policies(jsonData, easy_jsonData)
            elif inner_policy == 'iscsi_boot_policies':
                policies_lan(name_prefix, templateVars["org"], inner_type).iscsi_boot_policies(jsonData, easy_jsonData)
            elif inner_policy == 'iscsi_static_target_policies':
                policies_lan(name_prefix, templateVars["org"], inner_type).iscsi_static_target_policies(jsonData, easy_jsonData)
            elif inner_policy == 'lan_connectivity_policies':
                policies_lan(name_prefix, templateVars["org"], inner_type).lan_connectivity_policies(jsonData, easy_jsonData)
            elif inner_policy == 'ldap_policies':
                policies_p1(name_prefix, templateVars["org"], inner_type).ldap_policies(jsonData, easy_jsonData)
            elif inner_policy == 'link_aggregation_policies':
                policies_p1(name_prefix, templateVars["org"], inner_type).link_aggregation_policies(jsonData, easy_jsonData)
            elif inner_policy == 'link_control_policies':
                policies_p1(name_prefix, templateVars["org"], inner_type).link_control_policies(jsonData, easy_jsonData)
            elif inner_policy == 'local_user_policies':
                policies_p2(name_prefix, templateVars["org"], inner_type).local_user_policies(jsonData, easy_jsonData)
            elif inner_policy == 'multicast_policies':
                policies_vxan(name_prefix, templateVars["org"], inner_type).multicast_policies(jsonData, easy_jsonData)
            elif inner_policy == 'network_connectivity_policies':
                policies_p2(name_prefix, templateVars["org"], inner_type).network_connectivity_policies(jsonData, easy_jsonData)
            elif inner_policy == 'ntp_policies':
                policies_p2(name_prefix, templateVars["org"], inner_type).ntp_policies(jsonData, easy_jsonData)
            elif inner_policy == 'persistent_memory_policies':
                policies_p2(name_prefix, templateVars["org"], inner_type).persistent_memory_policies(jsonData, easy_jsonData)
            elif inner_policy == 'port_policies':
                policies_p2(name_prefix, templateVars["org"], inner_type).port_policies(jsonData, easy_jsonData)
            elif inner_policy == 'san_connectivity_policies':
                policies_san(name_prefix, templateVars["org"], inner_type).san_connectivity_policies(jsonData, easy_jsonData)
            elif inner_policy == 'sd_card_policies':
                policies_p3(name_prefix, templateVars["org"], inner_type).sd_card_policies(jsonData, easy_jsonData)
            elif inner_policy == 'serial_over_lan_policies':
                policies_p3(name_prefix, templateVars["org"], inner_type).serial_over_lan_policies(jsonData, easy_jsonData)
            elif inner_policy == 'smtp_policies':
                policies_p3(name_prefix, templateVars["org"], inner_type).smtp_policies(jsonData, easy_jsonData)
            elif inner_policy == 'snmp_policies':
                policies_p3(name_prefix, templateVars["org"], inner_type).snmp_policies(jsonData, easy_jsonData)
            elif inner_policy == 'ssh_policies':
                policies_p3(name_prefix, templateVars["org"], inner_type).ssh_policies(jsonData, easy_jsonData)
            elif inner_policy == 'storage_policies':
                policies_p3(name_prefix, templateVars["org"], inner_type).storage_policies(jsonData, easy_jsonData)
            elif inner_policy == 'switch_control_policies':
                policies_p3(name_prefix, templateVars["org"], inner_type).switch_control_policies(jsonData, easy_jsonData)
            elif inner_policy == 'syslog_policies':
                policies_p3(name_prefix, templateVars["org"], inner_type).syslog_policies(jsonData, easy_jsonData)
            elif inner_policy == 'system_qos_policies':
                policies_p3(name_prefix, templateVars["org"], inner_type).system_qos_policies(jsonData, easy_jsonData)
            elif inner_policy == 'thermal_policies':
                policies_p3(name_prefix, templateVars["org"], inner_type).thermal_policies(jsonData, easy_jsonData)
            elif inner_policy == 'ucs_server_profiles':
                profiles(name_prefix, templateVars["org"], inner_type).ucs_server_profiles(jsonData, easy_jsonData)
            elif inner_policy == 'ucs_server_profile_templates':
                profiles(name_prefix, templateVars["org"], inner_type).ucs_server_profile_templates(jsonData, easy_jsonData)
            elif inner_policy == 'virtual_kvm_policies':
                policies_p3(name_prefix, templateVars["org"], inner_type).virtual_kvm_policies(jsonData, easy_jsonData)
            elif inner_policy == 'virtual_media_policies':
                policies_p3(name_prefix, templateVars["org"], inner_type).virtual_media_policies(jsonData, easy_jsonData)
            elif inner_policy == 'vlan_policies':
                policies_vxan(name_prefix, templateVars["org"], inner_type).vlan_policies(jsonData, easy_jsonData)
            elif inner_policy == 'vsan_policies':
                policies_vxan(name_prefix, templateVars["org"], inner_type).vsan_policies(jsonData, easy_jsonData)
