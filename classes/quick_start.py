#!/usr/bin/env python3
from p2 import port_list_eth, port_list_fc, port_modes_fc
import lan
import p1
import p2
import p3
import pools
import profiles
import san
import vxan
import ezfunctions
import ipaddress
import jinja2
import pkg_resources
import re
import validating

ucs_template_path = pkg_resources.resource_filename('quick_start', '../templates/')

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
        path_sep = kwargs['path_sep']
        polVars = {}
        polVars["org"] = org
        tfDir = kwargs['tfDir']

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  The Quick Deployment Module - Domain Policies, will configure pools for a UCS Domain ')
            print(f'  Profile.\n')
            print(f'  This wizard will save the output for these pools in the following files:\n')
            print(f'  - {tfDir}{path_sep}{org}{path_sep}policies{path_sep}domain.yaml')
            print(f'  - {tfDir}{path_sep}{org}{path_sep}policies{path_sep}management.yaml')
            print(f'  - {tfDir}{path_sep}{org}{path_sep}policies{path_sep}port.yaml')
            print(f'  - {tfDir}{path_sep}{org}{path_sep}policies{path_sep}switch.yaml')
            print(f'  - {tfDir}{path_sep}{org}{path_sep}policies{path_sep}vlan.yaml')
            print(f'  - {tfDir}{path_sep}{org}{path_sep}policies{path_sep}vsan.yaml')
            print(f'  - {tfDir}{path_sep}{org}{path_sep}profiles{path_sep}chassis.yaml')
            print(f'  - {tfDir}{path_sep}{org}{path_sep}profiles{path_sep}domain.yaml')
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

                    polVars["name"] = 'Quick Deployment Module'

                    polVars["multi_select"] = False
                    jsonVars = jsonData['components']['schemas']['policy.AbstractProfile']['allOf'][1]['properties']

                    # Domain Name
                    polVars["Description"] = jsonVars['Name']['description']
                    polVars["varInput"] = 'What is the name for this UCS Domain?'
                    polVars["varDefault"] = ''
                    polVars["varName"] = 'UCS Domain Name'
                    polVars["varRegex"] = jsonVars['Name']['pattern']
                    polVars["minLength"] = 1
                    polVars["maxLength"] = 64
                    polVars["name"] = ezfunctions.varStringLoop(**polVars)
                    domain_name = polVars["name"]

                    # Domain Model
                    polVars["multi_select"] = False
                    jsonVars = jsonData['components']['schemas']['fabric.PortPolicy']['allOf'][1]['properties']
                    polVars["var_description"] = jsonVars['DeviceModel']['description']
                    polVars["jsonVars"] = sorted(jsonVars['DeviceModel']['enum'])
                    polVars["defaultVar"] = jsonVars['DeviceModel']['default']
                    polVars["varType"] = 'Device Model'
                    polVars["device_model"] = ezfunctions.variablesFromAPI(**polVars)

                    # Serial Numbers
                    serial_a,serial_b = ezfunctions.ucs_domain_serials()
                    polVars["serial_number_fabric_a"] = serial_a
                    polVars["serial_number_fabric_b"] = serial_b

                    # VLAN Pool
                    valid = False
                    while valid == False:
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        print(f'  IMPORTANT NOTE: The FCoE VLAN will be assigned based on the VSAN Identifier.')
                        print(f'                  Be sure to exclude the VSAN for Fabric A and B from the VLAN Pool.')
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        VlanList,vlanListExpanded = ezfunctions.vlan_pool()
                        
                        nativeVlan = input('Do you want to configure one of these VLANs as the Native VLAN?  [press enter to skip]: ')
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
                    # Configure Multicast Policy
                    #_______________________________________________________________________

                    polVars["name"] = domain_name
                    polVars["descr"] = f'{polVars["name"]} Multicast Policy'
                    vxan.policies(name_prefix, org, 'policies').quick_start_multicast(**polVars)

                    #_______________________________________________________________________
                    #
                    # Configure VLAN Policy
                    #_______________________________________________________________________

                    polVars["multicast_policy"] = polVars["name"]
                    polVars["descr"] = f'{polVars["name"]} VLAN Policy'
                    polVars["native_vlan"] = nativeVlan
                    polVars["vlan_list"] = VlanList
                    vxan.policies(name_prefix, org, 'policies').quick_start_vlan(**polVars)

                    #_______________________________________________________________________
                    #
                    # Configure Flow Control Policy
                    #_______________________________________________________________________

                    polVars["initial_write"] = True
                    polVars["policy_type"] = 'Flow Control Policy'
                    polVars["header"] = '%s Variables' % (polVars["policy_type"])
                    polVars["template_file"] = 'template_open.jinja2'
                    polVars["template_type"] = 'flow_control_policies'

                    # Open the Template file
                    ezfunctions.write_to_template(self, **polVars)
                    polVars["initial_write"] = False

                    # Configure Flow Control Policy
                    name = domain_name
                    polVars["name"] = name
                    polVars["descr"] = f'{name} Flow Control Policy'
                    polVars["priority"] = 'auto'
                    polVars["receive"] = 'Disabled'
                    polVars["send"] = 'Disabled'

                    # Write Policies to Template File
                    polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                    ezfunctions.write_to_template(self, **polVars)

                    # Close the Template file
                    polVars["template_file"] = 'template_close.jinja2'
                    ezfunctions.write_to_template(self, **polVars)

                    #_______________________________________________________________________
                    #
                    # Configure Link Aggregation Policy
                    #_______________________________________________________________________

                    polVars["initial_write"] = True
                    polVars["policy_type"] = 'Link Aggregation Policy'
                    polVars["header"] = '%s Variables' % (polVars["policy_type"])
                    polVars["template_file"] = 'template_open.jinja2'
                    polVars["template_type"] = 'link_aggregation_policies'

                    # Open the Template file
                    ezfunctions.write_to_template(self, **polVars)
                    polVars["initial_write"] = False

                    # Configure Link Aggregation Policy
                    name = domain_name
                    polVars["name"] = name
                    polVars["descr"] = f'{name} Link Aggregation Policy'
                    polVars["lacp_rate"] = 'normal'
                    polVars["suspend_individual"] = False

                    # Write Policies to Template File
                    polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                    ezfunctions.write_to_template(self, **polVars)

                    # Close the Template file
                    polVars["template_file"] = 'template_close.jinja2'
                    ezfunctions.write_to_template(self, **polVars)

                    #_______________________________________________________________________
                    #
                    # Configure Link Control Policy
                    #_______________________________________________________________________

                    polVars["initial_write"] = True
                    polVars["policy_type"] = 'Link Control Policy'
                    polVars["header"] = '%s Variables' % (polVars["policy_type"])
                    polVars["template_file"] = 'template_open.jinja2'
                    polVars["template_type"] = 'link_control_policies'

                    # Open the Template file
                    ezfunctions.write_to_template(self, **polVars)
                    polVars["initial_write"] = False

                    # Configure Link Control Policy
                    name = domain_name
                    polVars["name"] = name
                    polVars["descr"] = f'{name} Link Control Policy'
                    polVars["admin_state"] = 'Enabled'
                    polVars["mode"] = 'normal'

                    # Write Policies to Template File
                    polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                    ezfunctions.write_to_template(self, **polVars)

                    # Close the Template file
                    polVars["template_file"] = 'template_close.jinja2'
                    ezfunctions.write_to_template(self, **polVars)

                    # Configure Fibre-Channel Unified Ports
                    fc_mode,ports_in_use,fc_converted_ports,port_modes = port_modes_fc(jsonData, easy_jsonData, name_prefix, **polVars)
                    polVars["fc_mode"] = fc_mode
                    polVars["ports_in_use"] = ports_in_use
                    polVars["fc_converted_ports"] = fc_converted_ports
                    polVars["port_modes"] = port_modes
                    if polVars["port_modes"].get("port_list"):
                        polVars["fc_ports"] = polVars["port_modes"]["port_list"]
                    else:
                        polVars["fc_ports"] = []

                    # If Unified Ports Exist Configure VSAN Policies
                    if len(polVars["fc_converted_ports"]) > 0:
                        # Obtain the VSAN for Fabric A/B
                        fabrics = ['A', 'B']
                        for x in fabrics:
                            valid = False
                            while valid == False:
                                if loop_count % 2 == 0:
                                    vsan_id = input(f'Enter the VSAN id to add to {polVars["name"]} Fabric {x}. [100]: ')
                                else:
                                    vsan_id = input(f'Enter the VSAN id to add to {polVars["name"]} Fabric {x}. [200]: ')
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
                                        polVars[f"vsan_id_{x}"] = vsan_id
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

                        polVars["initial_write"] = True
                        polVars["policy_type"] = 'VSAN Policy'
                        polVars["header"] = '%s Variables' % (polVars["policy_type"])
                        polVars["template_file"] = 'template_open.jinja2'
                        polVars["template_type"] = 'vsan_policies'

                        # Open the Template file
                        ezfunctions.write_to_template(self, **polVars)
                        polVars["initial_write"] = False

                        # Configure VSAN Policy
                        for x in fabrics:
                            name = f'{domain_name}-{x}'
                            polVars["name"] = name
                            polVars["descr"] = f'{name} VSAN Policy'
                            polVars["uplink_trunking"] = False
                            xlower = x.lower()
                            polVars['vsans'] = []
                            vsans = {
                                'fcoe_vlan_id':polVars[f"vsan_id_{x}"],
                                'name':f'{domain_name}-{xlower}',
                                'id':polVars[f"vsan_id_{x}"]
                            }
                            polVars['vsans'].append(vsans)

                            # Write Policies to Template File
                            polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                            ezfunctions.write_to_template(self, **polVars)

                        # Close the Template file
                        polVars["template_file"] = 'template_close.jinja2'
                        ezfunctions.write_to_template(self, **polVars)

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

                    polVars["initial_write"] = True
                    polVars["policy_type"] = 'Ethernet Network Group Policy'
                    polVars["header"] = '%s Variables' % (polVars["policy_type"])
                    polVars["template_file"] = 'template_open.jinja2'
                    polVars["template_type"] = 'ethernet_network_group_policies'

                    # Open the Template file
                    ezfunctions.write_to_template(self, **polVars)
                    polVars["initial_write"] = False

                    # Configure Ethernet Network Group Policy
                    name = f'{domain_name}'
                    polVars["name"] = name
                    polVars["descr"] = f'{name} Ethernet Network Group Policy'
                    polVars["allowed_vlans"] = VlanList
                    if not nativeVlan == '':
                        polVars["native_vlan"] = nativeVlan
                    else:
                        polVars["native_vlan"] = ''
                        polVars.pop('native_vlan')

                    # Write Policies to Template File
                    polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                    ezfunctions.write_to_template(self, **polVars)

                    # Close the Template file
                    polVars["template_file"] = 'template_close.jinja2'
                    ezfunctions.write_to_template(self, **polVars)

                    # Ethernet Uplink Port-Channel
                    polVars["name"] = domain_name
                    polVars['port_type'] = 'Ethernet Uplink Port-Channel'
                    port_channel_ethernet_uplinks,polVars['ports_in_use'] = port_list_eth(jsonData, easy_jsonData, name_prefix, **polVars)

                    polVars["fc_ports_in_use"] = []
                    polVars["port_type"] = 'Fibre-Channel Port-Channel'
                    Fab_A,Fab_B,fc_ports_in_use = port_list_fc(jsonData, easy_jsonData, name_prefix, **polVars)
                    Fabric_A_fc_port_channels = Fab_A
                    Fabric_B_fc_port_channels = Fab_B
                    polVars["fc_ports_in_use"] = fc_ports_in_use

                    # Server Ports
                    polVars['port_type'] = 'Server Ports'
                    port_role_servers,polVars['ports_in_use'] = port_list_eth(jsonData, easy_jsonData, name_prefix, **polVars)

                    # System MTU for System QoS Policy
                    polVars["Description"] = 'This option will set the MTU to 9216 if answer is "Y" or 1500 if answer is "N".'
                    polVars["varInput"] = f'Do you want to enable Jumbo MTU?  Enter "Y" or "N"'
                    polVars["varDefault"] = 'Y'
                    polVars["varName"] = 'MTU'
                    answer = ezfunctions.varBoolLoop(**polVars)
                    if answer == True:
                        mtu = 9216
                    else:
                        mtu = 1500

                    # NTP Servers
                    primary_ntp = ezfunctions.ntp_primary()
                    alternate_ntp = ezfunctions.ntp_alternate()

                    polVars["enabled"] = True
                    polVars["ntp_servers"] = []
                    polVars["ntp_servers"].append(primary_ntp)
                    if not alternate_ntp == '':
                        polVars["ntp_servers"].append(alternate_ntp)

                    # Timezone
                    polVars["multi_select"] = False
                    jsonVars = jsonData['components']['schemas']['appliance.SystemInfo']['allOf'][1]['properties']['TimeZone']['enum']
                    tz_regions = []
                    for i in jsonVars:
                        tz_region = i.split('/')[0]
                        if not tz_region in tz_regions:
                            tz_regions.append(tz_region)
                    tz_regions = sorted(tz_regions)
                    polVars["var_description"] = 'Timezone Regions...'
                    polVars["jsonVars"] = tz_regions
                    polVars["defaultVar"] = 'America'
                    polVars["varType"] = 'Time Region'
                    time_region = ezfunctions.variablesFromAPI(**polVars)

                    region_tzs = []
                    for item in jsonVars:
                        if time_region in item:
                            region_tzs.append(item)

                    polVars["var_description"] = 'Region Timezones...'
                    polVars["jsonVars"] = sorted(region_tzs)
                    polVars["defaultVar"] = ''
                    polVars["varType"] = 'Region Timezones'
                    polVars["timezone"] = ezfunctions.variablesFromAPI(**polVars)

                    polVars["port_channel_ethernet_uplinks"] = port_channel_ethernet_uplinks
                    polVars["Fabric_A_fc_port_channels"] = Fabric_A_fc_port_channels
                    polVars["Fabric_B_fc_port_channels"] = Fabric_B_fc_port_channels
                    polVars["port_role_servers"] = port_role_servers
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  UCS Domain Name        = "{domain_name}"')
                    print(f'  Device Model           = "{polVars["device_model"]}"')
                    print(f'  Serial Number Fabric A = "{polVars["serial_number_fabric_a"]}"')
                    print(f'  Serial Number Fabric B = "{polVars["serial_number_fabric_b"]}"')
                    print(f'  Port Policy Variables:')
                    if len(polVars["fc_converted_ports"]) > 0:
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
                        for item in polVars[f"{port_list}"]:
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
                    print(f'    timezone: "{polVars["timezone"]}"')
                    if len(polVars["ntp_servers"]) > 0:
                        print(f'    ntp_servers = [')
                        for server in polVars["ntp_servers"]:
                            print(f'      "{server}",')
                        print(f'    ]')
                    print(f'  VLAN Pool: "{VlanList}"')
                    if len(polVars["fc_converted_ports"]) > 0:
                        print(f'  VSAN Fabric A: "{polVars["vsan_id_A"]}"')
                        print(f'  VSAN Fabric B: "{polVars["vsan_id_B"]}"')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
                        if confirm_policy == 'Y' or confirm_policy == '':

                            #_______________________________________________________________________
                            #
                            # Configure Sytem MTU Settings
                            #_______________________________________________________________________

                            polVars["initial_write"] = True
                            polVars["policy_type"] = 'System QoS Policy'
                            polVars["header"] = '%s Variables' % (polVars["policy_type"])
                            polVars["template_file"] = 'template_open.jinja2'
                            polVars["template_type"] = 'system_qos_policies'

                            # Open the Template file
                            ezfunctions.write_to_template(self, **polVars)
                            polVars["initial_write"] = False

                            # System QoS Settings
                            polVars["mtu"] = mtu
                            name = domain_name
                            polVars["name"] = name
                            polVars["descr"] = f'{name} System QoS Policy'
                            polVars["Platinum"] = {
                                'bandwidth_percent':20,
                                'cos':5,
                                'mtu':polVars["mtu"],
                                'multicast_optimize':False,
                                'packet_drop':False,
                                'priority':'Platinum',
                                'state':'Enabled',
                                'weight':10,
                            }
                            polVars["Gold"] = {
                                'bandwidth_percent':18,
                                'cos':4,
                                'mtu':polVars["mtu"],
                                'multicast_optimize':False,
                                'packet_drop':True,
                                'priority':'Gold',
                                'state':'Enabled',
                                'weight':9,
                            }
                            polVars["FC"] = {
                                'bandwidth_percent':20,
                                'cos':3,
                                'mtu':2240,
                                'multicast_optimize':False,
                                'packet_drop':False,
                                'priority':'FC',
                                'state':'Enabled',
                                'weight':10,
                            }
                            polVars["Silver"] = {
                                'bandwidth_percent':18,
                                'cos':2,
                                'mtu':polVars["mtu"],
                                'multicast_optimize':False,
                                'packet_drop':True,
                                'priority':'Silver',
                                'state':'Enabled',
                                'weight':8,
                            }
                            polVars["Bronze"] = {
                                'bandwidth_percent':14,
                                'cos':1,
                                'mtu':polVars["mtu"],
                                'multicast_optimize':False,
                                'packet_drop':True,
                                'priority':'Bronze',
                                'state':'Enabled',
                                'weight':7,
                            }
                            polVars["Best Effort"] = {
                                'bandwidth_percent':10,
                                'cos':255,
                                'mtu':polVars["mtu"],
                                'multicast_optimize':False,
                                'packet_drop':True,
                                'priority':'Best Effort',
                                'state':'Enabled',
                                'weight':5,
                            }

                            polVars["classes"] = []
                            priorities = ['Platinum', 'Gold', 'FC', 'Silver', 'Bronze', 'Best Effort']

                            for priority in priorities:
                                polVars["classes"].append(polVars[priority])

                            # Write Policies to Template File
                            polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                            ezfunctions.write_to_template(self, **polVars)

                            # Close the Template file
                            polVars["template_file"] = 'template_close.jinja2'
                            ezfunctions.write_to_template(self, **polVars)

                            #_______________________________________________________________________
                            #
                            # Configure Network Connectivity Policy
                            #_______________________________________________________________________

                            polVars["initial_write"] = True
                            polVars["policy_type"] = 'Network Connectivity Policy'
                            polVars["header"] = '%s Variables' % (polVars["policy_type"])
                            polVars["template_file"] = 'template_open.jinja2'
                            polVars["template_type"] = 'network_connectivity_policies'

                            # Open the Template file
                            ezfunctions.write_to_template(self, **polVars)
                            polVars["initial_write"] = False

                            # Network Connectivity Access Settings
                            name = domain_name
                            polVars["name"] = name
                            polVars["descr"] = f'{name} Network Connectivity Policy'
                            polVars["preferred_ipv4_dns_server"] = kwargs['primary_dns']
                            polVars["alternate_ipv4_dns_server"] = kwargs['secondary_dns']
                            polVars["enable_ipv6"] = False

                            # Write Policies to Template File
                            polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                            ezfunctions.write_to_template(self, **polVars)

                            # Close the Template file
                            polVars["template_file"] = 'template_close.jinja2'
                            ezfunctions.write_to_template(self, **polVars)

                            #_______________________________________________________________________
                            #
                            # Configure NTP Policy
                            #_______________________________________________________________________

                            polVars["initial_write"] = True
                            polVars["policy_type"] = 'NTP Policy'
                            polVars["header"] = '%s Variables' % (polVars["policy_type"])
                            polVars["template_file"] = 'template_open.jinja2'
                            polVars["template_type"] = 'ntp_policies'

                            # Open the Template file
                            ezfunctions.write_to_template(self, **polVars)
                            polVars["initial_write"] = False

                            # NTP Settings
                            name = domain_name
                            polVars["name"] = name
                            polVars["descr"] = f'{name} NTP Policy'

                            # Write Policies to Template File
                            polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                            ezfunctions.write_to_template(self, **polVars)

                            # Close the Template file
                            polVars["template_file"] = 'template_close.jinja2'
                            ezfunctions.write_to_template(self, **polVars)

                            #_______________________________________________________________________
                            #
                            # Configure Switch Control Policy
                            #_______________________________________________________________________

                            polVars["initial_write"] = True
                            polVars["policy_type"] = 'Switch Control Policy'
                            polVars["header"] = '%s Variables' % (polVars["policy_type"])
                            polVars["template_file"] = 'template_open.jinja2'
                            polVars["template_type"] = 'switch_control_policies'

                            # Open the Template file
                            ezfunctions.write_to_template(self, **polVars)
                            polVars["initial_write"] = False

                            # Switch Control Settings
                            name = domain_name
                            polVars["name"] = name
                            polVars["descr"] = f'{name} Switch Control Policy'
                            polVars["mac_address_table_aging"] = 'Default'
                            polVars["mac_aging_time"] = 14500
                            polVars["udld_message_interval"] = 15
                            polVars["udld_recovery_action"] = "reset"
                            polVars["vlan_port_count_optimization"] = False

                            # Write Policies to Template File
                            polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                            ezfunctions.write_to_template(self, **polVars)

                            # Close the Template file
                            polVars["template_file"] = 'template_close.jinja2'
                            ezfunctions.write_to_template(self, **polVars)

                            #_______________________________________________________________________
                            #
                            # Configure Port Policy
                            #_______________________________________________________________________

                            polVars["initial_write"] = True
                            polVars["policy_type"] = 'Port Policy'
                            polVars["header"] = '%s Variables' % (polVars["policy_type"])
                            polVars["template_file"] = 'template_open.jinja2'
                            polVars["template_type"] = 'port_policies'

                            # Open the Template file
                            ezfunctions.write_to_template(self, **polVars)
                            polVars["initial_write"] = False

                            # Port Settings
                            name = domain_name
                            polVars["name"] = name
                            polVars["descr"] = f'{name} Port Policy'

                            polVars["port_channel_appliances"] = []
                            polVars["port_channel_ethernet_uplinks"] = port_channel_ethernet_uplinks
                            polVars["port_channel_fcoe_uplinks"] = []
                            polVars["port_role_appliances"] = []
                            polVars["port_role_ethernet_uplinks"] = []
                            polVars["port_role_fcoe_uplinks"] = []
                            polVars["port_role_servers"] = port_role_servers

                            if len(polVars["fc_converted_ports"]) > 0:
                                for x in fabrics:
                                    xlower = x.lower()
                                    polVars["name"] = f'{domain_name}-{xlower}'
                                    if x == 'A':
                                        polVars["port_channel_fc_uplinks"] = Fabric_A_fc_port_channels
                                    else:
                                        polVars["port_channel_fc_uplinks"] = Fabric_B_fc_port_channels
                                    polVars["port_role_fc_uplinks"] = []

                                    # Write Policies to Template File
                                    polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                                    ezfunctions.write_to_template(self, **polVars)

                            # Close the Template file
                            polVars["template_file"] = 'template_close.jinja2'
                            ezfunctions.write_to_template(self, **polVars)

                            #_______________________________________________________________________
                            #
                            # Configure UCS Chassis Profile
                            #_______________________________________________________________________
                            name = domain_name
                            polVars["name"] = name
                            profiles(name_prefix, org, 'profiles').quick_start_chassis(easy_jsonData, **polVars)

                            #_______________________________________________________________________
                            #
                            # Configure UCS Domain Profile
                            #_______________________________________________________________________

                            # UCS Domain Profile Settings
                            name = domain_name
                            polVars["name"] = name
                            polVars["descr"] = f'{name} UCS Domain Profile'
                            polVars["action"] = 'No-op'
                            polVars["network_connectivity_policy"] = domain_name
                            polVars["ntp_policy"] = domain_name
                            polVars["port_policies"] = {
                                'fabric_a':f'{domain_name}-a',
                                'fabric_b':f'{domain_name}-b'
                            }
                            polVars["snmp_policy"] = f'{org}_domain'
                            polVars["switch_control_policy"] = domain_name
                            polVars["syslog_policy"] = f'{org}_domain'
                            polVars["system_qos_policy"] = domain_name
                            polVars["vlan_policies"] = {
                                'fabric_a':domain_name,
                                'fabric_b':domain_name
                            }
                            if len(polVars["fc_converted_ports"]) > 0:
                                polVars["vsan_policies"] = {
                                    'fabric_a':f'{domain_name}-A',
                                    'fabric_b':f'{domain_name}-B'
                                }
                            else:
                                polVars["vsan_policies"] = {
                                    'fabric_a':'',
                                    'fabric_b':''
                                }

                            profiles(name_prefix, org, 'ucs_domain_profiles').quick_start_domain(**polVars)

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
        
        if configure == 'Y' or configure == '':
            vlan_policy = {'vlan_policy':f'{domain_name}','vlans':VlanList,'native_vlan':nativeVlan}
            if len(polVars["fc_converted_ports"]) > 0:
                vsan_a = polVars["vsan_id_A"]
                vsan_b = polVars["vsan_id_B"]
            else:
                vsan_a = 0
                vsan_b = 0
            fc_ports = polVars["fc_converted_ports"]
            mtu = polVars["mtu"]
            configure = True
        elif configure == 'N':
            vlan_policy = {}
            vsan_a = 0
            vsan_b = 0
            fc_ports = []
            mtu = 1500
            configure = False
        return configure,vlan_policy,vsan_a,vsan_b,fc_ports,mtu

    #==============================================
    # LAN and SAN Policies
    #==============================================
    def lan_san_policies(self, jsonData, easy_jsonData, **kwargs):
        if kwargs['mtu'] > 8999:
            mtu = 9000
        else:
            mtu = 1500
        opSystem = kwargs['opSystem']
        if opSystem == 'Windows' : path_sep = '\\'
        else: path_sep = '/'
        org = self.org
        polVars = {}
        polVars["org"] = org
        tfDir = kwargs['tfDir']


        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  The Quick Deployment Module - Network Configuration, will configure policies for the')
            print(f'  Network Configuration of a UCS Server Profile connected to an IMM Domain.\n')
            print(f'  This wizard will save the output for these pools in the following files:\n')
            print(f'  - {tfDir}{path_sep}{org}{path_sep}{self.type}/ethernet_adapter_policies.yaml')
            print(f'  - {tfDir}{path_sep}{org}{path_sep}{self.type}/ethernet_network_control_policies.yaml')
            print(f'  - {tfDir}{path_sep}{org}{path_sep}{self.type}/ethernet_network_group_policies.yaml')
            print(f'  - {tfDir}{path_sep}{org}{path_sep}{self.type}/ethernet_qos_policies.yaml')
            print(f'  - {tfDir}{path_sep}{org}{path_sep}{self.type}/fibre_channel_adapter_policies.yaml')
            print(f'  - {tfDir}{path_sep}{org}{path_sep}{self.type}/fibre_channel_network_policies.yaml')
            print(f'  - {tfDir}{path_sep}{org}{path_sep}{self.type}/fibre_channel_qos_policies.yaml')
            print(f'  - {tfDir}{path_sep}{org}{path_sep}{self.type}/lan_connectivity_policies.yaml')
            print(f'  - {tfDir}{path_sep}{org}{path_sep}{self.type}/san_connectivity_policies.yaml')
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
                    polVars["vsan_A"] = kwargs["vsan_a"]
                    polVars["vsan_B"] = kwargs["vsan_b"]
                    fc_ports_in_use = kwargs["fc_ports"]
                    vlan_policy_list = ezfunctions.vlan_list_full(vlan_list)

                    polVars["multi_select"] = False
                    jsonVars = jsonVars = easy_jsonData['policies']['fabric.EthNetworkControlPolicy']

                    # Neighbor Discovery Protocol
                    polVars["var_description"] = jsonVars['discoveryProtocol']['description']
                    polVars["jsonVars"] = sorted(jsonVars['discoveryProtocol']['enum'])
                    polVars["defaultVar"] = jsonVars['discoveryProtocol']['default']
                    polVars["varType"] = 'Neighbor Discovery Protocol'
                    neighbor_discovery = ezfunctions.variablesFromAPI(**polVars)

                    # Management VLAN
                    valid = False
                    while valid == False:
                        polVars["Description"] = 'LAN Connectivity Policy vNICs - MGMT VLAN Identifier'
                        polVars["varInput"] = 'Enter the VLAN ID for MGMT:'
                        polVars["varDefault"] = 1
                        polVars["varName"] = 'Management VLAN ID'
                        polVars["minNum"] = 1
                        polVars["maxNum"] = 4094
                        mgmt_vlan = ezfunctions.varNumberLoop(**polVars)
                        valid = ezfunctions.validate_vlan_in_policy(vlan_policy_list, mgmt_vlan)

                    # vMotion VLAN
                    valid = False
                    while valid == False:
                        polVars["Description"] = 'LAN Connectivity Policy vNICs - vMotion VLAN Identifier'
                        polVars["varInput"] = 'Enter the VLAN ID for vMotion:'
                        polVars["varDefault"] = 2
                        polVars["varName"] = 'Management VLAN ID'
                        polVars["minNum"] = 1
                        polVars["maxNum"] = 4094
                        vmotion_vlan = ezfunctions.varNumberLoop(**polVars)
                        valid = ezfunctions.validate_vlan_in_policy(vlan_policy_list, vmotion_vlan)

                    # Storage VLAN
                    valid = False
                    while valid == False:
                        polVars["Description"] = 'LAN Connectivity Policy vNICs - Storage VLAN Identifier'
                        polVars["varInput"] = 'Enter the VLAN ID for Storage:'
                        polVars["varDefault"] = 3
                        polVars["varName"] = 'Storage VLAN ID'
                        polVars["minNum"] = 1
                        polVars["maxNum"] = 4094
                        storage_vlan = ezfunctions.varNumberLoop(**polVars)
                        valid = ezfunctions.validate_vlan_in_policy(vlan_policy_list, storage_vlan)

                    valid = False
                    while valid == False:
                        VlanList = input('Enter the VLAN or List of VLANs to add to the DATA (Virtual Machine) vNICs: ')
                        if not VlanList == '':
                            vlanListExpanded = ezfunctions.vlan_list_full(VlanList)
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
                        print(f'    VSAN Fabric A = {polVars["vsan_A"]}')
                        print(f'    VSAN Fabric B = {polVars["vsan_B"]}')
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

                            polVars["initial_write"] = True
                            polVars["policy_type"] = 'Ethernet Adapter Policy'
                            polVars["header"] = '%s Variables' % (polVars["policy_type"])
                            polVars["template_file"] = 'template_open.jinja2'
                            polVars["template_type"] = 'ethernet_adapter_policies'

                            # Open the Template file
                            ezfunctions.write_to_template(self, **polVars)
                            polVars["initial_write"] = False

                            name = 'VMware'
                            polVars["name"] = name
                            polVars["descr"] = f'{name} Ethernet Adapter Policy'
                            polVars["policy_template"] = 'VMware'

                            # Write Policies to Template File
                            polVars["template_file"] = '%s.jinja2' % ('ethernet_adapter_templates')
                            ezfunctions.write_to_template(self, **polVars)

                            # Close the Template file
                            polVars["template_file"] = 'template_close.jinja2'
                            ezfunctions.write_to_template(self, **polVars)

                            #_______________________________________________________________________
                            #
                            # Configure Ethernet Network Control Policy
                            #_______________________________________________________________________

                            polVars["initial_write"] = True
                            polVars["policy_type"] = 'Ethernet Network Control Policy'
                            polVars["header"] = '%s Variables' % (polVars["policy_type"])
                            polVars["template_file"] = 'template_open.jinja2'
                            polVars["template_type"] = 'ethernet_network_control_policies'

                            # Open the Template file
                            ezfunctions.write_to_template(self, **polVars)
                            polVars["initial_write"] = False

                            name = neighbor_discovery
                            polVars["name"] = name
                            polVars["descr"] = f'{name} Ethernet Network Control Policy'
                            polVars["action_on_uplink_fail"] = "linkDown"
                            if neighbor_discovery == 'CDP':
                                polVars["cdp_enable"] = True
                            else:
                                polVars["cdp_enable"] = False
                            if neighbor_discovery == 'LLDP':
                                polVars["lldp_receive_enable"] = True
                                polVars["lldp_transmit_enable"] = True
                            else:
                                polVars["lldp_receive_enable"] = False
                                polVars["lldp_transmit_enable"] = False
                            polVars["mac_register_mode"] = "nativeVlanOnly"
                            polVars["mac_security_forge"] = "allow"

                            # Write Policies to Template File
                            polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                            ezfunctions.write_to_template(self, **polVars)

                            # Close the Template file
                            polVars["template_file"] = 'template_close.jinja2'
                            ezfunctions.write_to_template(self, **polVars)

                            #_______________________________________________________________________
                            #
                            # Configure Ethernet Network Group Policy
                            #_______________________________________________________________________

                            polVars["initial_write"] = True
                            polVars["policy_type"] = 'Ethernet Network Group Policy'
                            polVars["header"] = '%s Variables' % (polVars["policy_type"])
                            polVars["template_file"] = 'template_open.jinja2'
                            polVars["template_type"] = 'ethernet_network_group_policies'

                            # Open the Template file
                            ezfunctions.write_to_template(self, **polVars)
                            polVars["initial_write"] = False

                            names = [kwargs["vlan_policy"], 'MGMT', 'VMOTION', 'STORAGE', 'DATA']
                            for x in names:
                                if x == kwargs["vlan_policy"]:
                                    allowed_vlans = kwargs["vlans"]
                                    native_vlan = kwargs["native_vlan"]
                                elif x == 'MGMT':
                                    allowed_vlans = mgmt_vlan
                                    native_vlan = mgmt_vlan
                                elif x == 'VMOTION':
                                    allowed_vlans = vmotion_vlan
                                    native_vlan = vmotion_vlan
                                elif x == 'STORAGE':
                                    allowed_vlans = storage_vlan
                                    native_vlan = storage_vlan
                                elif x == 'DATA':
                                    allowed_vlans = VlanList
                                    native_vlan = nativeVlan
                                name = x
                                polVars["name"] = name
                                polVars["descr"] = f'{name} Ethernet Network Group Policy'
                                polVars["allowed_vlans"] = allowed_vlans
                                if not native_vlan == '':
                                    polVars["native_vlan"] = native_vlan
                                else:
                                    polVars["native_vlan"] = ''
                                    polVars.pop('native_vlan')

                                # Write Policies to Template File
                                polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                                ezfunctions.write_to_template(self, **polVars)

                            # Close the Template file
                            polVars["template_file"] = 'template_close.jinja2'
                            ezfunctions.write_to_template(self, **polVars)

                            #_______________________________________________________________________
                            #
                            # Configure Ethernet QoS Policy
                            #_______________________________________________________________________

                            polVars["initial_write"] = True
                            polVars["policy_type"] = 'Ethernet QoS Policy'
                            polVars["header"] = '%s Variables' % (polVars["policy_type"])
                            polVars["template_file"] = 'template_open.jinja2'
                            polVars["template_type"] = 'ethernet_qos_policies'

                            # Open the Template file
                            ezfunctions.write_to_template(self, **polVars)
                            polVars["initial_write"] = False

                            names = ['Bronze', 'Gold', 'Platinum', 'Silver']
                            for x in names:
                                name = x
                                polVars["name"] = name
                                polVars["descr"] = f'{name} Ethernet QoS Policy'
                                polVars["allowed_vlans"] = mgmt_vlan
                                polVars["native_vlan"] = mgmt_vlan
                                polVars["burst"] = 1024
                                polVars["enable_trust_host_cos"] = False
                                polVars["priority"] = x
                                polVars["mtu"] = mtu
                                polVars["rate_limit"] = 0

                                # Write Policies to Template File
                                polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                                ezfunctions.write_to_template(self, **polVars)

                            # Close the Template file
                            polVars["template_file"] = 'template_close.jinja2'
                            ezfunctions.write_to_template(self, **polVars)

                            if len(fc_ports_in_use) > 0:
                                #_______________________________________________________________________
                                #
                                # Configure Fibre-Channel Adapter Policy
                                #_______________________________________________________________________

                                polVars["initial_write"] = True
                                polVars["policy_type"] = 'Fibre-Channel Adapter Policy'
                                polVars["header"] = '%s Variables' % (polVars["policy_type"])
                                polVars["template_file"] = 'template_open.jinja2'
                                polVars["template_type"] = 'fibre_channel_adapter_policies'

                                # Open the Template file
                                ezfunctions.write_to_template(self, **polVars)
                                polVars["initial_write"] = False

                                name = 'VMware'
                                polVars["name"] = name
                                polVars["descr"] = f'{name} Fibre-Channel Adapter Policy'
                                polVars["policy_template"] = 'VMware'

                                # Write Policies to Template File
                                polVars["template_file"] = '%s.jinja2' % ('ethernet_adapter_templates')
                                ezfunctions.write_to_template(self, **polVars)

                                # Close the Template file
                                polVars["template_file"] = 'template_close.jinja2'
                                ezfunctions.write_to_template(self, **polVars)

                                #_______________________________________________________________________
                                #
                                # Configure Fibre-Channel Network Policy
                                #_______________________________________________________________________

                                polVars["initial_write"] = True
                                polVars["policy_type"] = 'Fibre-Channel Network Policy'
                                polVars["header"] = '%s Variables' % (polVars["policy_type"])
                                polVars["template_file"] = 'template_open.jinja2'
                                polVars["template_type"] = 'fibre_channel_network_policies'

                                # Open the Template file
                                ezfunctions.write_to_template(self, **polVars)
                                polVars["initial_write"] = False

                                fabrics = ['A', 'B']
                                for fab in fabrics:
                                    name = f'Fabric-{fab}'
                                    polVars["name"] = name
                                    polVars["descr"] = f'{name} Fibre-Channel Network Policy'
                                    polVars["default_vlan"] = 0
                                    polVars["vsan_id"] = polVars[f"vsan_{fab}"]

                                    # Write Policies to Template File
                                    polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                                    ezfunctions.write_to_template(self, **polVars)

                                # Close the Template file
                                polVars["template_file"] = 'template_close.jinja2'
                                ezfunctions.write_to_template(self, **polVars)

                                #_______________________________________________________________________
                                #
                                # Configure Fibre-Channel QoS Policy
                                #_______________________________________________________________________

                                polVars["initial_write"] = True
                                polVars["policy_type"] = 'Fibre-Channel QoS Policy'
                                polVars["header"] = '%s Variables' % (polVars["policy_type"])
                                polVars["template_file"] = 'template_open.jinja2'
                                polVars["template_type"] = 'fibre_channel_qos_policies'

                                # Open the Template file
                                ezfunctions.write_to_template(self, **polVars)
                                polVars["initial_write"] = False

                                name = 'FC_QoS'
                                polVars["name"] = name
                                polVars["descr"] = f'{name} Fibre-Channel QoS Policy'
                                polVars["burst"] = 1024
                                polVars["max_data_field_size"] = 2112
                                polVars["rate_limit"] = 0

                                # Write Policies to Template File
                                polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                                ezfunctions.write_to_template(self, **polVars)

                                # Close the Template file
                                polVars["template_file"] = 'template_close.jinja2'
                                ezfunctions.write_to_template(self, **polVars)

                            #_______________________________________________________________________
                            #
                            # LAN Connectivity Policy
                            #_______________________________________________________________________

                            polVars["initial_write"] = True
                            polVars["policy_type"] = 'LAN Connectivity Policy'
                            polVars["header"] = '%s Variables' % (polVars["policy_type"])
                            polVars["template_file"] = 'template_open.jinja2'
                            polVars["template_type"] = 'lan_connectivity_policies'

                            # Open the Template file
                            ezfunctions.write_to_template(self, **polVars)
                            polVars["initial_write"] = False

                            name = 'VMware_LAN'
                            polVars["name"] = name
                            polVars["descr"] = f'{name} LAN Connectivity Policy'
                            polVars["enable_azure_stack_host_qos"] = False
                            polVars["iqn_allocation_type"] = "None"
                            polVars["vnic_placement_mode"] = "custom"
                            polVars["target_platform"] = "FIAttached"
                            polVars["vnics"] = []

                            Order = 0
                            if len(fc_ports_in_use) > 0:
                                #_______________________________________________________________________
                                #
                                # SAN Connectivity Policy
                                #_______________________________________________________________________

                                polVars["initial_write"] = True
                                polVars["policy_type"] = 'SAN Connectivity Policy'
                                polVars["header"] = '%s Variables' % (polVars["policy_type"])
                                polVars["template_file"] = 'template_open.jinja2'
                                polVars["template_type"] = 'san_connectivity_policies'

                                # Open the Template file
                                ezfunctions.write_to_template(self, **polVars)
                                polVars["initial_write"] = False

                                name = 'VMware_SAN'
                                polVars["name"] = name
                                polVars["descr"] = f'{name} SAN Connectivity Policy'
                                polVars["target_platform"] = "FIAttached"
                                polVars["vhba_placement_mode"] = "custom"
                                polVars["vhbas"] = []
                                polVars["wwnn_allocation_type"] = "POOL"
                                polVars["wwnn_pool"] = "VMware"

                                for fab in fabrics:
                                    vhba = {
                                        'fibre_channel_adapter_policy':'VMware',
                                        'fibre_channel_network_policy':f'Fabric-{fab}',
                                        'fibre_channel_qos_policy':'FC_QoS',
                                        'name':f'HBA-{fab}',
                                        'persistent_lun_bindings':False,
                                        'pci_link':0,
                                        'pci_order':Order,
                                        'slot_id':'MLOM',
                                        'switch_id':fab,
                                        'wwpn_allocation_type':'POOL',
                                        'wwpn_pool':f'VMware-{fab}',
                                    }
                                    polVars["vhbas"].append(vhba)
                                    Order += 1

                                # Write Policies to Template File
                                polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                                ezfunctions.write_to_template(self, **polVars)

                                # Close the Template file
                                polVars["template_file"] = 'template_close.jinja2'
                                ezfunctions.write_to_template(self, **polVars)

                            name = 'VMware_LAN'
                            polVars["name"] = name
                            polVars["descr"] = f'{name} LAN Connectivity Policy'
                            polVars["template_type"] = 'lan_connectivity_policies'
                            names = ['MGMT_Silver', 'VMOTION_Bronze', 'STORAGE_Platinum', 'DATA_Gold']
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
                                        'pci_link':0,
                                        'pci_order':Order,
                                        'slot_id':'MLOM',
                                        'switch_id':fab
                                    }
                                    polVars["vnics"].append(vnic)
                                    Order += 1

                            # Write Policies to Template File
                            polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                            ezfunctions.write_to_template(self, **polVars)

                            # Close the Template file
                            polVars["template_file"] = 'template_close.jinja2'
                            ezfunctions.write_to_template(self, **polVars)

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
    def pools(self, jsonData, easy_jsonData, **kwargs):
        org = self.org
        opSystem = kwargs['opSystem']
        if opSystem == 'Windows' : path_sep = '\\'
        else: path_sep = '/'
        primary_dns = '208.67.220.220'
        secondary_dns = ''
        polVars = {}
        polVars["org"] = org
        tfDir = kwargs['tfDir']

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  The Quick Deployment Module - Pools, will configure pools for a UCS Server Profile')
            print(f'  connected to an IMM Domain.\n')
            print(f'  This wizard will save the output for these pools in the following files:\n')
            print(f'  - {tfDir}{path_sep}{org}{path_sep}{self.type}/ip_pools.yaml')
            print(f'  - {tfDir}{path_sep}{org}{path_sep}{self.type}/mac_pools.yaml')
            print(f'  - {tfDir}{path_sep}{org}{path_sep}{self.type}/uuid_pools.yaml')
            print(f'  - {tfDir}{path_sep}{org}{path_sep}{self.type}/wwnn_pools.yaml')
            print(f'  - {tfDir}{path_sep}{org}{path_sep}{self.type}/wwpn_pools.yaml')
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

                    polVars["multi_select"] = False
                    jsonVars = jsonData['components']['schemas']['ippool.IpV4Config']['allOf'][1]['properties']

                    polVars["Description"] = jsonVars['Gateway']['description']
                    polVars["varInput"] = 'What is the Gateway for the KVM IP Pool? [198.18.0.1]:'
                    polVars["varDefault"] = '198.18.0.1'
                    polVars["varName"] = 'Gateway'
                    polVars["varRegex"] = jsonVars['Gateway']['pattern']
                    polVars["minLength"] = 7
                    polVars["maxLength"] = 15
                    gateway = ezfunctions.varStringLoop(**polVars)

                    polVars["Description"] = jsonVars['Netmask']['description']
                    polVars["varInput"] = 'What is the Netmask for the KVM IP Pool? [255.255.255.0]:'
                    polVars["varDefault"] = '255.255.255.0'
                    polVars["varName"] = 'Netmask'
                    polVars["varRegex"] = jsonVars['Netmask']['pattern']
                    polVars["minLength"] = 7
                    polVars["maxLength"] = 15
                    netmask = ezfunctions.varStringLoop(**polVars)

                    polVars["Description"] = jsonVars['PrimaryDns']['description']
                    polVars["varInput"] = 'What is the Primary Dns for the KVM IP Pool? [208.67.220.220]:'
                    polVars["varDefault"] = '208.67.220.220'
                    polVars["varName"] = 'Primary Dns'
                    polVars["varRegex"] = jsonVars['PrimaryDns']['pattern']
                    polVars["minLength"] = 7
                    polVars["maxLength"] = 15
                    primary_dns = ezfunctions.varStringLoop(**polVars)

                    polVars["Description"] = jsonVars['SecondaryDns']['description']
                    polVars["varInput"] = 'What is the Secondary Dns for the KVM IP Pool? [press enter to skip]:'
                    polVars["varDefault"] = ''
                    polVars["varName"] = 'Secondary Dns'
                    polVars["varRegex"] = jsonVars['SecondaryDns']['pattern']
                    polVars["minLength"] = 7
                    polVars["maxLength"] = 15
                    secondary_dns = ezfunctions.varStringLoop(**polVars)

                    jsonVars = jsonData['components']['schemas']['ippool.IpV4Block']['allOf'][1]['properties']

                    polVars["Description"] = jsonVars['From']['description']
                    polVars["varInput"] = 'What is the First IP Address for the KVM IP Pool? [198.18.0.10]:'
                    polVars["varDefault"] = '198.18.0.10'
                    polVars["varName"] = 'Beginning IP Address'
                    polVars["varRegex"] = jsonVars['From']['pattern']
                    polVars["minLength"] = 7
                    polVars["maxLength"] = 15
                    pool_from = ezfunctions.varStringLoop(**polVars)

                    polVars["Description"] = jsonVars['To']['description']
                    polVars["varInput"] = 'What is the Last IP Address for the KVM IP Pool? [198.18.0.254]:'
                    polVars["varDefault"] = '198.18.0.254'
                    polVars["varName"] = 'Ending IP Address'
                    polVars["varRegex"] = jsonVars['To']['pattern']
                    polVars["minLength"] = 7
                    polVars["maxLength"] = 15
                    pool_to = ezfunctions.varStringLoop(**polVars)

                    polVars["Description"] = 'Prefix to assign to Pools'
                    polVars["varInput"] = 'What is the 2 Digit (Hex) Prefix to assign to the MAC, UUID, WWNN, and WWPN Pools? [00]:'
                    polVars["varDefault"] = '00'
                    polVars["varName"] = 'Pool Prefix'
                    polVars["varRegex"] = '^[0-9a-zA-Z][0-9a-zA-Z]$'
                    polVars["minLength"] = 2
                    polVars["maxLength"] = 2
                    pool_prefix = ezfunctions.varStringLoop(**polVars)
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

                            polVars["initial_write"] = True
                            polVars["policy_type"] = 'IP Pool'
                            polVars["header"] = '%s Variables' % (polVars["policy_type"])
                            polVars["template_file"] = 'template_open.jinja2'
                            polVars["template_type"] = 'ip_pools'

                            # Open the Template file
                            ezfunctions.write_to_template(self, **polVars)
                            polVars["initial_write"] = False

                            name = 'VMware_KVM'
                            polVars["name"] = name
                            polVars["descr"] = f'{name} KVM IP Pool'
                            polVars["assignment_order"] = 'sequential'
                            pool_size = int(ipaddress.IPv4Address(pool_to)) - int(ipaddress.IPv4Address(pool_from)) + 1
                            polVars["ipv4_blocks"] = [
                                {
                                    'from':pool_from,
                                    'size':pool_size,
                                    'to':pool_to
                                }
                            ]
                            polVars["ipv4_configuration"] = {
                                'gateway':gateway,
                                'prefix':netmask,
                                'primary_dns':primary_dns,
                                'secondary_dns':secondary_dns
                            }

                            # Write Policies to Template File
                            polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                            ezfunctions.write_to_template(self, **polVars)

                            # Close the Template file
                            polVars["template_file"] = 'template_close.jinja2'
                            ezfunctions.write_to_template(self, **polVars)

                            #_______________________________________________________________________
                            #
                            # Configure MAC Pools
                            #_______________________________________________________________________

                            polVars["initial_write"] = True
                            polVars["policy_type"] = 'MAC Pool'
                            polVars["header"] = '%s Variables' % (polVars["policy_type"])
                            polVars["template_file"] = 'template_open.jinja2'
                            polVars["template_type"] = 'mac_pools'

                            # Open the Template file
                            ezfunctions.write_to_template(self, **polVars)
                            polVars["initial_write"] = False

                            names = ['DATA', 'MGMT', 'VMOTION', 'STORAGE']
                            fabrics = ['A', 'B']
                            for nam in names:
                                for fab in fabrics:
                                    if nam == 'MGMT' and fab == 'A': key_id = 'A'
                                    elif nam == 'MGMT' and fab == 'B': key_id = 'B'
                                    elif nam == 'VMOTION' and fab == 'A': key_id = 'C'
                                    elif nam == 'VMOTION' and fab == 'B': key_id = 'D'
                                    elif nam == 'STORAGE' and fab == 'A': key_id = 'E'
                                    elif nam == 'STORAGE' and fab == 'B': key_id = 'F'
                                    elif nam == 'DATA' and fab == 'A': key_id = '1'
                                    elif nam == 'DATA' and fab == 'B': key_id = '2'

                                    name = f'{nam}-{fab}'
                                    polVars["name"] = name
                                    polVars["descr"] = f'{name} MAC Pool'
                                    polVars["assignment_order"] = 'sequential'
                                    pool_from = f'00:25:B5:{pool_prefix}:{key_id}0:00'
                                    pool_to = f'00:25:B5:{pool_prefix}:{key_id}3:E7'
                                    polVars["mac_blocks"] = [
                                        {
                                            'from':pool_from,
                                            'size':1000,
                                            'to':pool_to
                                        }
                                    ]
                                    # Write Policies to Template File
                                    polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                                    ezfunctions.write_to_template(self, **polVars)

                            # Close the Template file
                            polVars["template_file"] = 'template_close.jinja2'
                            ezfunctions.write_to_template(self, **polVars)

                            #_______________________________________________________________________
                            #
                            # Configure UUID Pool
                            #_______________________________________________________________________

                            polVars["initial_write"] = True
                            polVars["policy_type"] = 'UUID Pool'
                            polVars["header"] = '%s Variables' % (polVars["policy_type"])
                            polVars["template_file"] = 'template_open.jinja2'
                            polVars["template_type"] = 'uuid_pools'

                            # Open the Template file
                            ezfunctions.write_to_template(self, **polVars)
                            polVars["initial_write"] = False

                            name = 'VMware'
                            polVars["name"] = name
                            polVars["descr"] = f'{name} UUID Pool'
                            polVars["assignment_order"] = 'sequential'
                            polVars["prefix"] = f'000025B5-{pool_prefix}00-0000'
                            polVars["uuid_blocks"] = [
                                {
                                    'from':'0000-000000000000',
                                    'size':1000,
                                    'to':'0000-0000000003E7'
                                }
                            ]
                            # Write Policies to Template File
                            polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                            ezfunctions.write_to_template(self, **polVars)

                            # Close the Template file
                            polVars["template_file"] = 'template_close.jinja2'
                            ezfunctions.write_to_template(self, **polVars)

                            #_______________________________________________________________________
                            #
                            # Configure WWNN Pool
                            #_______________________________________________________________________

                            polVars["initial_write"] = True
                            polVars["policy_type"] = 'WWNN Pool'
                            polVars["header"] = '%s Variables' % (polVars["policy_type"])
                            polVars["template_file"] = 'template_open.jinja2'
                            polVars["template_type"] = 'wwnn_pools'

                            # Open the Template file
                            ezfunctions.write_to_template(self, **polVars)
                            polVars["initial_write"] = False

                            name = 'VMware'
                            polVars["name"] = name
                            polVars["descr"] = f'{name} WWNN Pool'
                            polVars["assignment_order"] = 'sequential'
                            pool_from = f'20:00:00:25:B5:{pool_prefix}:00:00'
                            pool_to = f'20:00:00:25:B5:{pool_prefix}:03:E7'
                            polVars["wwnn_blocks"] = [
                                {
                                    'from':pool_from,
                                    'size':1000,
                                    'to':pool_to
                                }
                            ]
                            # Write Policies to Template File
                            polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                            ezfunctions.write_to_template(self, **polVars)

                            # Close the Template file
                            polVars["template_file"] = 'template_close.jinja2'
                            ezfunctions.write_to_template(self, **polVars)

                            #_______________________________________________________________________
                            #
                            # Configure WWPN Pools
                            #_______________________________________________________________________

                            polVars["initial_write"] = True
                            polVars["policy_type"] = 'WWPN Pool'
                            polVars["header"] = '%s Variables' % (polVars["policy_type"])
                            polVars["template_file"] = 'template_open.jinja2'
                            polVars["template_type"] = 'wwpn_pools'

                            # Open the Template file
                            ezfunctions.write_to_template(self, **polVars)
                            polVars["initial_write"] = False

                            for fab in fabrics:
                                name = f'VMware-{fab}'
                                polVars["name"] = name
                                polVars["descr"] = f'{name} WWPN Pool Fabric {fab}'
                                polVars["assignment_order"] = 'sequential'
                                pool_from = f'20:00:00:25:B5:{pool_prefix}:{fab}0:00'
                                pool_to = f'20:00:00:25:B5:{pool_prefix}:{fab}3:E7'
                                polVars["wwpn_blocks"] = [
                                    {
                                        'from':pool_from,
                                        'size':1000,
                                        'to':pool_to
                                    }
                                ]
                                # Write Policies to Template File
                                polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                                ezfunctions.write_to_template(self, **polVars)

                            # Close the Template file
                            polVars["template_file"] = 'template_close.jinja2'
                            ezfunctions.write_to_template(self, **polVars)

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
        opSystem = kwargs['opSystem']
        if opSystem == 'Windows' : path_sep = '\\'
        else: path_sep = '/'
        org = self.org
        polVars = {}
        polVars["org"] = org
        tfDir = kwargs['tfDir']

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  The Quick Deployment Module - Pools, will configure pools for a UCS Server Profile')
            print(f'  connected to an IMM Domain.\n')
            print(f'  This wizard will save the output for these pools in the following files:\n')
            print(f'  - {tfDir}{path_sep}{org}{path_sep}{self.type}/imc_access_policies.yaml')
            print(f'  - {tfDir}{path_sep}{org}{path_sep}{self.type}/ipmi_over_lan_policies.yaml')
            print(f'  - {tfDir}{path_sep}{org}{path_sep}{self.type}/local_user_policies.yaml')
            print(f'  - {tfDir}{path_sep}{org}{path_sep}{self.type}/power_policies.yaml')
            print(f'  - {tfDir}{path_sep}{org}{path_sep}{self.type}/serial_over_lan_policies.yaml')
            print(f'  - {tfDir}{path_sep}{org}{path_sep}{self.type}/snmp_policies.yaml')
            print(f'  - {tfDir}{path_sep}{org}{path_sep}{self.type}/syslog_policies.yaml')
            print(f'  - {tfDir}{path_sep}{org}{path_sep}{self.type}/thermal_policies.yaml')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to run the Quick Deployment Module - Policy Configuration?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                loop_count = 1
                policy_loop = False
                while policy_loop == False:
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  Below are the Questions that will be asked by the Policies Portion of the wizard.')
                    print(f'   - If the IMC Policy is Inband our Ooband.')
                    print(f'     * If the IMC Policy is inband, VLAN ID for IMC Access Policy.')
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

                    polVars["name"] = 'Quick Deployment Module'

                    vlan_policy_list = ezfunctions.vlan_list_full(vlan_list)

                    polVars["multi_select"] = False

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  Now Starting the IMC Access Policy Section.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')

                    # IMC Access Type
                    jsonVars = jsonData['components']['schemas']['access.Policy']['allOf'][1]['properties']
                    polVars["var_description"] = jsonVars['ConfigurationType']['description']
                    polVars["jsonVars"] = ['inband', 'out_of_band']
                    polVars["defaultVar"] = 'inband'
                    polVars["varType"] = 'IMC Access Type'
                    imcBand = ezfunctions.variablesFromAPI(**polVars)

                    if imcBand == 'inband':
                        # IMC Access VLAN
                        valid = False
                        while valid == False:
                            polVars["Description"] = 'IMC Access VLAN Identifier'
                            polVars["varInput"] = 'Enter the VLAN ID for the IMC Access Policy.'
                            polVars["varDefault"] = 4
                            polVars["varName"] = 'IMC Access Policy VLAN ID'
                            polVars["minNum"] = 4
                            polVars["maxNum"] = 4094
                            polVars["inband_vlan_id"] = ezfunctions.varNumberLoop(**polVars)
                            if server_type == 'FIAttached':
                                valid = ezfunctions.validate_vlan_in_policy(vlan_policy_list, polVars["inband_vlan_id"])
                            else:
                                valid = True

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  Need to obtain the IPMI Key for IPMI over LAN Policy Encryption.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    polVars["ipmi_key"] = ezfunctions.ipmi_key_function(**polVars)

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  Now Starting the Local User Policy Section.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    # Local Users
                    polVars["always_send_user_password"] = False
                    polVars["enforce_strong_password"] = True
                    polVars["grace_period"] = 0
                    polVars["notification_period"] = 15
                    polVars["password_expiry_duration"] = 90
                    polVars["password_history"] = 5
                    ilCount = 1
                    local_users = []
                    user_loop = False
                    while user_loop == False:
                        question = input(f'Would you like to configure a Local user?  Enter "Y" or "N" [Y]: ')
                        if question == '' or question == 'Y':
                            local_users,user_loop = ezfunctions.local_users_function(
                                jsonData, easy_jsonData, ilCount, **polVars
                            )
                        elif question == 'N':
                            user_loop = True
                        else:
                            print(f'\n------------------------------------------------------\n')
                            print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                            print(f'\n------------------------------------------------------\n')
                    polVars["local_users"] = local_users

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  Now Starting the SNMP Policy Section.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    # Pull in the Policies for SNMP Policies
                    jsonVars = jsonData['components']['schemas']['snmp.Policy']['allOf'][1]['properties']

                    # SNMP Contact
                    polVars["Description"] = jsonVars['SysContact']['description'] + \
                        'Note: Enter a string up to 64 characters, such as an email address or a name and telephone number.'
                    polVars["varDefault"] = ''
                    polVars["varInput"] = 'SNMP System Contact:'
                    polVars["varName"] = 'SNMP System Contact'
                    polVars["varRegex"] = '.*'
                    polVars["minLength"] = 1
                    polVars["maxLength"] = jsonVars['SysContact']['maxLength']
                    polVars["system_contact"] = ezfunctions.varStringLoop(**polVars)

                    # SNMP Location
                    polVars["Description"] = jsonVars['SysLocation']['description']
                    polVars["varDefault"] = ''
                    polVars["varInput"] = 'What is the Location of the host on which the SNMP agent (server) runs?'
                    polVars["varName"] = 'SNMP System Location'
                    polVars["varRegex"] = '.*'
                    polVars["minLength"] = 1
                    polVars["maxLength"] = jsonVars['SysLocation']['maxLength']
                    polVars["system_location"] = ezfunctions.varStringLoop(**polVars)

                    # SNMP Users
                    ilCount = 1
                    snmp_user_list = []
                    snmp_loop = False
                    while snmp_loop == False:
                        question = input(f'Would you like to configure an SNMPv3 User?  Enter "Y" or "N" [Y]: ')
                        if question == '' or question == 'Y':
                            snmp_user_list,snmp_loop = ezfunctions.snmp_users(jsonData, ilCount, **polVars)
                        elif question == 'N':
                            snmp_loop = True
                        else:
                            print(f'\n------------------------------------------------------\n')
                            print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                            print(f'\n------------------------------------------------------\n')
                    polVars["users"] = snmp_user_list

                    # SNMP Trap Destinations
                    ilCount = 1
                    snmp_dests = []
                    snmp_loop = False
                    if len(snmp_user_list) > 0:
                        while snmp_loop == False:
                            question = input(f'Would you like to configure SNMP Trap Destionations?  Enter "Y" or "N" [Y]: ')
                            if question == '' or question == 'Y':
                                snmp_dests,snmp_loop = ezfunctions.snmp_trap_servers(jsonData, ilCount, snmp_user_list, **polVars)
                            elif question == 'N':
                                snmp_loop = True
                            else:
                                print(f'\n------------------------------------------------------\n')
                                print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                                print(f'\n------------------------------------------------------\n')
                    polVars["trap_destinations"] = snmp_dests

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
                            polVars["var_description"] = jsonVars['MinSeverity']['description']
                            polVars["jsonVars"] = sorted(jsonVars['MinSeverity']['enum'])
                            polVars["defaultVar"] = jsonVars['MinSeverity']['default']
                            polVars["varType"] = 'Syslog Local Minimum Severity'
                            polVars["min_severity"] = ezfunctions.variablesFromAPI(**polVars)

                            polVars["local_logging"] = {'file':{'min_severity':polVars["min_severity"]}}
                            remote_logging = ezfunctions.syslog_servers(jsonData, **polVars)
                            polVars['remote_logging'] = remote_logging

                            syslog_loop = True

                        elif question == 'N':
                            polVars["min_severity"] = 'warning'
                            polVars["local_logging"] = {'file':{'min_severity':polVars["min_severity"]}}
                            polVars['remote_logging'] = {}
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
                            polVars['remote_logging'].update(server1)
                            polVars['remote_logging'].update(server2)

                            syslog_loop = True
                        else:
                            print(f'\n------------------------------------------------------\n')
                            print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                            print(f'\n------------------------------------------------------\n')

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  Policy Variables:')
                    print(f'    IMC Access Mode  = "{imcBand}"')
                    if imcBand == 'Inband':
                        print(f'    IMC Access VLAN  = {polVars["inband_vlan_id"]}')
                    if len(polVars["local_users"]) > 0:
                        print(f'    local_users = ''{')
                        for item in polVars["local_users"]:
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
                    print(f'    System Contact   = "{polVars["system_contact"]}"')
                    print(f'    System Locaction = "{polVars["system_location"]}"')
                    if len(polVars["trap_destinations"]) > 0:
                        print(f'    snmp_trap_destinations = ''{')
                        for item in polVars["trap_destinations"]:
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
                    if len(polVars["users"]) > 0:
                        print(f'    snmp_users = ''{')
                        for item in polVars["users"]:
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
                    for key, value in polVars["remote_logging"].items():
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

                            polVars["initial_write"] = True
                            polVars["policy_type"] = 'IMC Access Policy'
                            polVars["header"] = '%s Variables' % (polVars["policy_type"])
                            polVars["template_file"] = 'template_open.jinja2'
                            polVars["template_type"] = 'imc_access_policies'

                            # Open the Template file
                            ezfunctions.write_to_template(self, **polVars)
                            polVars["initial_write"] = False

                            # Configure IMC Access Policy
                            name = org
                            polVars["name"] = name
                            polVars["descr"] = f'{name} IMC Access Policy'
                            polVars[f"{imcBand}_ip_pool"] = 'VMware_KVM'
                            polVars["ipv4_address_configuration"] = True
                            polVars["ipv6_address_configuration"] = False

                            # Write Policies to Template File
                            polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                            ezfunctions.write_to_template(self, **polVars)

                            # Close the Template file
                            polVars["template_file"] = 'template_close.jinja2'
                            ezfunctions.write_to_template(self, **polVars)

                            #_______________________________________________________________________
                            #
                            # Configure IPMI over LAN Policy
                            #_______________________________________________________________________

                            polVars["initial_write"] = True
                            polVars["policy_type"] = 'IPMI over LAN Policy'
                            polVars["header"] = '%s Variables' % (polVars["policy_type"])
                            polVars["template_file"] = 'template_open.jinja2'
                            polVars["template_type"] = 'ipmi_over_lan_policies'

                            # Open the Template file
                            ezfunctions.write_to_template(self, **polVars)
                            polVars["initial_write"] = False

                            # IPMI over LAN Settings
                            name = org
                            polVars["name"] = name
                            polVars["descr"] = f'{name} IPMI over LAN Policy'
                            polVars["enabled"] = True

                            # Write Policies to Template File
                            polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                            ezfunctions.write_to_template(self, **polVars)

                            # Close the Template file
                            polVars["template_file"] = 'template_close.jinja2'
                            ezfunctions.write_to_template(self, **polVars)

                            #_______________________________________________________________________
                            #
                            # Configure Local User Policy
                            #_______________________________________________________________________

                            polVars["initial_write"] = True
                            polVars["policy_type"] = 'Local User Policy'
                            polVars["header"] = '%s Variables' % (polVars["policy_type"])
                            polVars["template_file"] = 'template_open.jinja2'
                            polVars["template_type"] = 'local_user_policies'

                            # Open the Template file
                            ezfunctions.write_to_template(self, **polVars)
                            polVars["initial_write"] = False

                            # Local User Settings
                            name = org
                            polVars["name"] = name
                            polVars["descr"] = f'{name} Local User Policy'


                            # Write Policies to Template File
                            polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                            ezfunctions.write_to_template(self, **polVars)

                            # Close the Template file
                            polVars["template_file"] = 'template_close.jinja2'
                            ezfunctions.write_to_template(self, **polVars)

                            #_______________________________________________________________________
                            #
                            # Configure Power Policy
                            #_______________________________________________________________________

                            polVars["initial_write"] = True
                            polVars["policy_type"] = 'Power Policy'
                            polVars["header"] = '%s Variables' % (polVars["policy_type"])
                            polVars["template_file"] = 'template_open.jinja2'
                            polVars["template_type"] = 'power_policies'

                            # Open the Template file
                            ezfunctions.write_to_template(self, **polVars)
                            polVars["initial_write"] = False

                            # Power Settings
                            names = ['5108', '9508', 'Server']
                            for name in names:
                                polVars["allocated_budget"] = 0
                                polVars["name"] = name
                                polVars["descr"] = f'{name} Power Policy'
                                if name == 'Server':
                                    polVars["power_restore"] = 'LastState'
                                    
                                elif name == '9508':
                                    polVars["power_allocation"] = 5600

                                polVars["power_redundancy"] = 'Grid'

                                # Write Policies to Template File
                                polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                                ezfunctions.write_to_template(self, **polVars)

                            # Close the Template file
                            polVars["template_file"] = 'template_close.jinja2'
                            ezfunctions.write_to_template(self, **polVars)

                            #_______________________________________________________________________
                            #
                            # Configure Serial over LAN Policy
                            #_______________________________________________________________________

                            polVars["initial_write"] = True
                            polVars["policy_type"] = 'Serial over LAN Policy'
                            polVars["header"] = '%s Variables' % (polVars["policy_type"])
                            polVars["template_file"] = 'template_open.jinja2'
                            polVars["template_type"] = 'serial_over_lan_policies'

                            # Open the Template file
                            ezfunctions.write_to_template(self, **polVars)
                            polVars["initial_write"] = False

                            # Serial over LAN Settings
                            name = org
                            polVars["name"] = name
                            polVars["descr"] = f'{name} Serial over LAN Policy'
                            polVars["enabled"] = True
                            polVars["baud_rate"] = 115200
                            polVars["com_port"] = 'com0'
                            polVars["ssh_port"] = 2400

                            # Write Policies to Template File
                            polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                            ezfunctions.write_to_template(self, **polVars)

                            # Close the Template file
                            polVars["template_file"] = 'template_close.jinja2'
                            ezfunctions.write_to_template(self, **polVars)

                            #_______________________________________________________________________
                            #
                            # Configure SNMP Policy
                            #_______________________________________________________________________

                            polVars["initial_write"] = True
                            polVars["policy_type"] = 'SNMP Policy'
                            polVars["header"] = '%s Variables' % (polVars["policy_type"])
                            polVars["template_file"] = 'template_open.jinja2'
                            polVars["template_type"] = 'snmp_policies'

                            # Open the Template file
                            ezfunctions.write_to_template(self, **polVars)
                            polVars["initial_write"] = False

                            # SNMP Settings
                            name = org
                            polVars["name"] = name
                            polVars["descr"] = f'{name} SNMP Policy'
                            polVars["access_community_string"] = ''
                            polVars["enabled"] = True
                            polVars["engine_input_id"] = ''
                            polVars["port"] = 161
                            polVars["snmp_community_access"] = 'Disabled'
                            polVars["trap_community_string"] = ''

                            # Write Policies to Template File
                            polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                            ezfunctions.write_to_template(self, **polVars)

                            # Close the Template file
                            polVars["template_file"] = 'template_close.jinja2'
                            ezfunctions.write_to_template(self, **polVars)

                            #_______________________________________________________________________
                            #
                            # Configure Syslog Policy
                            #_______________________________________________________________________

                            polVars["initial_write"] = True
                            polVars["policy_type"] = 'Syslog Policy'
                            polVars["header"] = '%s Variables' % (polVars["policy_type"])
                            polVars["template_file"] = 'template_open.jinja2'
                            polVars["template_type"] = 'syslog_policies'

                            # Open the Template file
                            ezfunctions.write_to_template(self, **polVars)
                            polVars["initial_write"] = False

                            # Syslog Settings
                            name = org
                            polVars["name"] = name
                            polVars["descr"] = f'{name} Syslog Policy'

                            # Write Policies to Template File
                            polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                            ezfunctions.write_to_template(self, **polVars)

                            # Close the Template file
                            polVars["template_file"] = 'template_close.jinja2'
                            ezfunctions.write_to_template(self, **polVars)

                            #_______________________________________________________________________
                            #
                            # Configure Thermal Policy
                            #_______________________________________________________________________

                            polVars["initial_write"] = True
                            polVars["policy_type"] = 'Thermal Policy'
                            polVars["header"] = '%s Variables' % (polVars["policy_type"])
                            polVars["template_file"] = 'template_open.jinja2'
                            polVars["template_type"] = 'thermal_policies'

                            # Open the Template file
                            ezfunctions.write_to_template(self, **polVars)
                            polVars["initial_write"] = False

                            # Thermal Settings
                            names = ['5108', '9508']
                            for name in names:
                                polVars["name"] = name
                                polVars["descr"] = f'{name} Thermal Policy'
                                polVars["fan_control_mode"] = 'Balanced'

                                # Write Policies to Template File
                                polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                                ezfunctions.write_to_template(self, **polVars)

                            # Close the Template file
                            polVars["template_file"] = 'template_close.jinja2'
                            ezfunctions.write_to_template(self, **polVars)

                            #_______________________________________________________________________
                            #
                            # Configure Virtual KVM Policy
                            #_______________________________________________________________________

                            polVars["initial_write"] = True
                            polVars["policy_type"] = 'Virtual KVM Policy'
                            polVars["header"] = '%s Variables' % (polVars["policy_type"])
                            polVars["template_file"] = 'template_open.jinja2'
                            polVars["template_type"] = 'virtual_kvm_policies'

                            # Open the Template file
                            ezfunctions.write_to_template(self, **polVars)
                            polVars["initial_write"] = False

                            # Virtual KVM Settings
                            name = org
                            polVars["name"] = name
                            polVars["descr"] = f'{name} Virtual KVM Policy'
                            polVars["enable_local_server_video"] = True
                            polVars["enable_video_encryption"] = True
                            polVars["enable_virtual_kvm"] = True
                            polVars["remote_port"] = 2068

                            # Write Policies to Template File
                            polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                            ezfunctions.write_to_template(self, **polVars)

                            # Close the Template file
                            polVars["template_file"] = 'template_close.jinja2'
                            ezfunctions.write_to_template(self, **polVars)

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
        opSystem = kwargs['opSystem']
        if opSystem == 'Windows' : path_sep = '\\'
        else: path_sep = '/'
        org = self.org
        server_type = 'profiles'
        polVars = {}
        polVars["org"] = org
        polVars["fc_ports"] = kwargs["fc_ports"]
        polVars["server_type"] = kwargs["server_type"]
        polVars["boot_order_policy"] = kwargs["boot_order_policy"]
        tfDir = kwargs['tfDir']

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  The Quick Deployment Module - Domain Policies, will configure pools for a UCS Domain ')
            print(f'  Profile.\n')
            print(f'  This wizard will save the output for these pools in the following files:\n')
            print(f'  - {tfDir}{path_sep}{org}{path_sep}{self.type}/ucs_server_profile_templates.yaml')
            print(f'  - {tfDir}{path_sep}{org}{path_sep}{self.type}/ucs_server_profiles.yaml')
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
                    # Configure UCS Server Profiles
                    #_______________________________________________________________________
                    profiles(name_prefix, org, self.type).quick_start_server_profiles(jsonData, easy_jsonData, **polVars)
                    profiles(name_prefix, org, self.type).quick_start_server_templates(**polVars)
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
    def standalone_policies(self, jsonData, easy_jsonData, **kwargs):
        name_prefix = self.name_prefix
        opSystem = kwargs['opSystem']
        if opSystem == 'Windows' : path_sep = '\\'
        else: path_sep = '/'
        org = self.org
        polVars = {}
        polVars["org"] = org
        tfDir = kwargs['tfDir']

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  The Quick Deployment Module - Pools, will configure pools for a UCS Server Profile')
            print(f'  connected to an IMM Domain.\n')
            print(f'  This wizard will save the output for these pools in the following files:\n')
            print(f'  - {tfDir}{path_sep}{org}{path_sep}{self.type}{path_sep}adapter_configuration_policies.yaml')
            print(f'  - {tfDir}{path_sep}{org}{path_sep}{self.type}{path_sep}device_connector_policies.yaml')
            print(f'  - {tfDir}{path_sep}{org}{path_sep}{self.type}{path_sep}ethernet_network_policies.yaml')
            print(f'  - {tfDir}{path_sep}{org}{path_sep}{self.type}{path_sep}ldap_policies.yaml')
            print(f'  - {tfDir}{path_sep}{org}{path_sep}{self.type}{path_sep}network_connectivity_policies.yaml')
            print(f'  - {tfDir}{path_sep}{org}{path_sep}{self.type}{path_sep}ntp_policies.yaml')
            print(f'  - {tfDir}{path_sep}{org}{path_sep}{self.type}{path_sep}persistent_memory_policies.yaml')
            print(f'  - {tfDir}{path_sep}{org}{path_sep}{self.type}{path_sep}smtp_policies.yaml')
            print(f'  - {tfDir}{path_sep}{org}{path_sep}{self.type}{path_sep}ssh_policies.yaml')
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
                    polVars["Description"] = jsonVars['SysContact']['description'] + \
                        'Note: Enter a string up to 64 characters, such as an email address or a name and telephone number.'
                    polVars["varDefault"] = ''
                    polVars["varInput"] = 'SNMP System Contact:'
                    polVars["varName"] = 'SNMP System Contact'
                    polVars["varRegex"] = '.*'
                    polVars["minLength"] = 1
                    polVars["maxLength"] = jsonVars['SysContact']['maxLength']
                    polVars["system_contact"] = ezfunctions.varStringLoop(**polVars)

                    # SNMP Location
                    polVars["Description"] = jsonVars['SysLocation']['description']
                    polVars["varDefault"] = ''
                    polVars["varInput"] = 'What is the Location of the host on which the SNMP agent (server) runs?'
                    polVars["varName"] = 'SNMP System Location'
                    polVars["varRegex"] = '.*'
                    polVars["minLength"] = 1
                    polVars["maxLength"] = jsonVars['SysLocation']['maxLength']
                    polVars["system_location"] = ezfunctions.varStringLoop(**polVars)

                    # SNMP Users
                    snmp_user_list = []
                    inner_loop_count = 1
                    snmp_loop = False
                    while snmp_loop == False:
                        question = input(f'Would you like to configure an SNMPv3 User?  Enter "Y" or "N" [Y]: ')
                        if question == '' or question == 'Y':
                            snmp_user_list,snmp_loop = ezfunctions.snmp_users(jsonData, inner_loop_count, **polVars)
                        elif question == 'N':
                            snmp_loop = True
                        else:
                            print(f'\n------------------------------------------------------\n')
                            print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                            print(f'\n------------------------------------------------------\n')
                    polVars["users"] = snmp_user_list

                    # SNMP Trap Destinations
                    snmp_dests = []
                    inner_loop_count = 1
                    snmp_loop = False
                    if len(snmp_user_list) > 0:
                        while snmp_loop == False:
                            question = input(f'Would you like to configure SNMP Trap Destionations?  Enter "Y" or "N" [Y]: ')
                            if question == '' or question == 'Y':
                                snmp_dests,snmp_loop = ezfunctions.snmp_trap_servers(jsonData, inner_loop_count, snmp_user_list, **polVars)
                            elif question == 'N':
                                snmp_loop = True
                            else:
                                print(f'\n------------------------------------------------------\n')
                                print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                                print(f'\n------------------------------------------------------\n')
                    polVars["trap_destinations"] = snmp_dests

                    # Syslog Local Logging
                    jsonVars = jsonData['components']['schemas']['syslog.LocalClientBase']['allOf'][1]['properties']
                    polVars["var_description"] = jsonVars['MinSeverity']['description']
                    polVars["jsonVars"] = sorted(jsonVars['MinSeverity']['enum'])
                    polVars["defaultVar"] = jsonVars['MinSeverity']['default']
                    polVars["varType"] = 'Syslog Local Minimum Severity'
                    polVars["min_severity"] = ezfunctions.variablesFromAPI(**polVars)

                    polVars["local_logging"] = {'file':{'min_severity':polVars["min_severity"]}}
                    remote_logging = ezfunctions.syslog_servers(jsonData, **polVars)
                    polVars['remote_logging'] = remote_logging

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  Network Configuration Variables:"')
                    print(f'    System Contact   = "{polVars["system_contact"]}"')
                    print(f'    System Locaction = "{polVars["system_location"]}"')
                    if len(polVars["trap_destinations"]) > 0:
                        print(f'    snmp_trap_destinations = ''{')
                        for item in polVars["trap_destinations"]:
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
                    if len(polVars["users"]) > 0:
                        print(f'    snmp_users = ''{')
                        for item in polVars["users"]:
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
                    for key, value in polVars["remote_logging"].items():
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

                            polVars["initial_write"] = True
                            polVars["policy_type"] = 'BIOS Policy'
                            polVars["header"] = '%s Variables' % (polVars["policy_type"])
                            polVars["template_file"] = 'template_open.jinja2'
                            polVars["template_type"] = 'bios_policies'

                            # Open the Template file
                            ezfunctions.write_to_template(self, **polVars)
                            polVars["initial_write"] = False

                            # Configure BIOS Policy
                            name = 'VMware'
                            polVars["name"] = name
                            polVars["descr"] = f'{name} BIOS Policy'
                            polVars["bios_template"] = 'Virtualization'


                            # Write Policies to Template File
                            polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                            ezfunctions.write_to_template(self, **polVars)

                            # Close the Template file
                            polVars["template_file"] = 'template_close.jinja2'
                            ezfunctions.write_to_template(self, **polVars)

                            #_______________________________________________________________________
                            #
                            # Configure Boot Order Policy
                            #_______________________________________________________________________

                            polVars["initial_write"] = True
                            polVars["policy_type"] = 'Boot Order Policy'
                            polVars["header"] = '%s Variables' % (polVars["policy_type"])
                            polVars["template_file"] = 'template_open.jinja2'
                            polVars["template_type"] = 'boot_order_policies'

                            # Open the Template file
                            ezfunctions.write_to_template(self, **polVars)
                            polVars["initial_write"] = False

                            # Configure Boot Order Policy
                            name = 'VMware_M2'
                            polVars["name"] = name
                            polVars["descr"] = f'{name} Boot Order Policy'
                            polVars["boot_mode"] = 'Uefi'
                            polVars["enable_secure_boot"] = True
                            polVars["boot_mode"] = 'Uefi'
                            polVars["boot_devices"] = [
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
                            polVars["template_file"] = '%s.jinja2' % ('boot_policies')
                            ezfunctions.write_to_template(self, **polVars)

                            # Close the Template file
                            polVars["template_file"] = 'template_close.jinja2'
                            ezfunctions.write_to_template(self, **polVars)

                            #_______________________________________________________________________
                            #
                            # Configure IMC Access Policy
                            #_______________________________________________________________________

                            polVars["initial_write"] = True
                            polVars["policy_type"] = 'IMC Access Policy'
                            polVars["header"] = '%s Variables' % (polVars["policy_type"])
                            polVars["template_file"] = 'template_open.jinja2'
                            polVars["template_type"] = 'imc_access_policies'

                            # Open the Template file
                            ezfunctions.write_to_template(self, **polVars)
                            polVars["initial_write"] = False

                            # Configure IMC Access Policy
                            name = org
                            polVars["name"] = name
                            polVars["descr"] = f'{name} IMC Access Policy'
                            polVars["inband_ip_pool"] = 'VMware_KVM'
                            polVars["ipv4_address_configuration"] = True
                            polVars["ipv6_address_configuration"] = False

                            # Write Policies to Template File
                            polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                            ezfunctions.write_to_template(self, **polVars)

                            # Close the Template file
                            polVars["template_file"] = 'template_close.jinja2'
                            ezfunctions.write_to_template(self, **polVars)

                            #_______________________________________________________________________
                            #
                            # Configure IPMI over LAN Policy
                            #_______________________________________________________________________

                            polVars["initial_write"] = True
                            polVars["policy_type"] = 'IPMI over LAN Policy'
                            polVars["header"] = '%s Variables' % (polVars["policy_type"])
                            polVars["template_file"] = 'template_open.jinja2'
                            polVars["template_type"] = 'ipmi_over_lan_policies'

                            # Open the Template file
                            ezfunctions.write_to_template(self, **polVars)
                            polVars["initial_write"] = False

                            # IPMI over LAN Settings
                            name = org
                            polVars["name"] = name
                            polVars["descr"] = f'{name} IPMI over LAN Policy'
                            polVars["enabled"] = True
                            polVars["ipmi_key"] = 1

                            # Write Policies to Template File
                            polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                            ezfunctions.write_to_template(self, **polVars)

                            # Close the Template file
                            polVars["template_file"] = 'template_close.jinja2'
                            ezfunctions.write_to_template(self, **polVars)

                            #_______________________________________________________________________
                            #
                            # Configure Local User Policy
                            #_______________________________________________________________________

                            polVars["initial_write"] = True
                            polVars["policy_type"] = 'Local User Policy'
                            polVars["header"] = '%s Variables' % (polVars["policy_type"])
                            polVars["template_file"] = 'template_open.jinja2'
                            polVars["template_type"] = 'local_user_policies'

                            # Open the Template file
                            ezfunctions.write_to_template(self, **polVars)
                            polVars["initial_write"] = False

                            # Local User Settings
                            name = org
                            polVars["name"] = name
                            polVars["descr"] = f'{name} Local User Policy'
                            polVars["enabled"] = True
                            polVars["ipmi_key"] = 1

                            # Write Policies to Template File
                            polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                            ezfunctions.write_to_template(self, **polVars)

                            # Close the Template file
                            polVars["template_file"] = 'template_close.jinja2'
                            ezfunctions.write_to_template(self, **polVars)

                            #_______________________________________________________________________
                            #
                            # Configure Power Policy
                            #_______________________________________________________________________

                            polVars["initial_write"] = True
                            polVars["policy_type"] = 'Power Policy'
                            polVars["header"] = '%s Variables' % (polVars["policy_type"])
                            polVars["template_file"] = 'template_open.jinja2'
                            polVars["template_type"] = 'power_policies'

                            # Open the Template file
                            ezfunctions.write_to_template(self, **polVars)
                            polVars["initial_write"] = False

                            # Power Settings
                            names = ['5108', '9508', 'Server']
                            for name in names:
                                polVars["allocated_budget"] = 0
                                polVars["name"] = name
                                polVars["descr"] = f'{name} Power Policy'
                                if name == 'Server': polVars["power_restore_state"] = 'LastState'
                                elif name == '9508': polVars["allocated_budget"] = 5600

                                polVars["power_redundancy"] = 'Grid'
                                polVars["ipmi_key"] = 1

                                # Write Policies to Template File
                                polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                                ezfunctions.write_to_template(self, **polVars)

                            # Close the Template file
                            polVars["template_file"] = 'template_close.jinja2'
                            ezfunctions.write_to_template(self, **polVars)

                            #_______________________________________________________________________
                            #
                            # Configure Serial over LAN Policy
                            #_______________________________________________________________________

                            polVars["initial_write"] = True
                            polVars["policy_type"] = 'Serial over LAN Policy'
                            polVars["header"] = '%s Variables' % (polVars["policy_type"])
                            polVars["template_file"] = 'template_open.jinja2'
                            polVars["template_type"] = 'serial_over_lan_policies'

                            # Open the Template file
                            ezfunctions.write_to_template(self, **polVars)
                            polVars["initial_write"] = False

                            # Serial over LAN Settings
                            name = org
                            polVars["name"] = name
                            polVars["descr"] = f'{name} Serial over LAN Policy'
                            polVars["enabled"] = True
                            polVars["baud_rate"] = 115200
                            polVars["com_port"] = 'com0'
                            polVars["ssh_port"] = 2400

                            # Write Policies to Template File
                            polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                            ezfunctions.write_to_template(self, **polVars)

                            # Close the Template file
                            polVars["template_file"] = 'template_close.jinja2'
                            ezfunctions.write_to_template(self, **polVars)

                            #_______________________________________________________________________
                            #
                            # Configure SNMP Policy
                            #_______________________________________________________________________

                            polVars["initial_write"] = True
                            polVars["policy_type"] = 'SNMP Policy'
                            polVars["header"] = '%s Variables' % (polVars["policy_type"])
                            polVars["template_file"] = 'template_open.jinja2'
                            polVars["template_type"] = 'snmp_policies'

                            # Open the Template file
                            ezfunctions.write_to_template(self, **polVars)
                            polVars["initial_write"] = False

                            # SNMP Settings
                            name = org
                            polVars["name"] = name
                            polVars["descr"] = f'{name} SNMP Policy'
                            polVars["access_community_string"] = ''
                            polVars["enabled"] = True
                            polVars["engine_input_id"] = ''
                            polVars["port"] = 161
                            polVars["snmp_community_access"] = 'Disabled'
                            polVars["trap_community_string"] = ''

                            # Write Policies to Template File
                            polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                            ezfunctions.write_to_template(self, **polVars)

                            # Close the Template file
                            polVars["template_file"] = 'template_close.jinja2'
                            ezfunctions.write_to_template(self, **polVars)

                            #_______________________________________________________________________
                            #
                            # Configure Storage Policy
                            #_______________________________________________________________________

                            polVars["initial_write"] = True
                            polVars["policy_type"] = 'Storage Policy'
                            polVars["header"] = '%s Variables' % (polVars["policy_type"])
                            polVars["template_file"] = 'template_open.jinja2'
                            polVars["template_type"] = 'storage_policies'

                            # Open the Template file
                            ezfunctions.write_to_template(self, **polVars)
                            polVars["initial_write"] = False

                            name = 'M2_Raid'
                            polVars["name"] = name
                            polVars["descr"] = f'{name} Storage Policy'
                            polVars["drive_group"] = {}
                            polVars["global_hot_spares"] = ''
                            polVars["m2_configuration"] = [ { 'controller_slot':'MSTOR-RAID-1,MSTOR-RAID-2' } ]
                            polVars["single_drive_raid_configuration"] = {}
                            polVars["unused_disks_state"] = 'No Change'
                            polVars["use_jbod_for_vd_creation"] = True

                            # Write Policies to Template File
                            polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                            ezfunctions.write_to_template(self, **polVars)

                            # Close the Template file
                            polVars["template_file"] = 'template_close.jinja2'
                            ezfunctions.write_to_template(self, **polVars)

                            #_______________________________________________________________________
                            #
                            # Configure Syslog Policy
                            #_______________________________________________________________________

                            polVars["initial_write"] = True
                            polVars["policy_type"] = 'Syslog Policy'
                            polVars["header"] = '%s Variables' % (polVars["policy_type"])
                            polVars["template_file"] = 'template_open.jinja2'
                            polVars["template_type"] = 'syslog_policies'

                            # Open the Template file
                            ezfunctions.write_to_template(self, **polVars)
                            polVars["initial_write"] = False

                            # Syslog Settings
                            name = org
                            polVars["name"] = name
                            polVars["descr"] = f'{name} Syslog Policy'
                            polVars["enabled"] = True
                            polVars["ipmi_key"] = 1

                            # Write Policies to Template File
                            polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                            ezfunctions.write_to_template(self, **polVars)

                            # Close the Template file
                            polVars["template_file"] = 'template_close.jinja2'
                            ezfunctions.write_to_template(self, **polVars)

                            #_______________________________________________________________________
                            #
                            # Configure Thermal Policy
                            #_______________________________________________________________________

                            polVars["initial_write"] = True
                            polVars["policy_type"] = 'Thermal Policy'
                            polVars["header"] = '%s Variables' % (polVars["policy_type"])
                            polVars["template_file"] = 'template_open.jinja2'
                            polVars["template_type"] = 'thermal_policies'

                            # Open the Template file
                            ezfunctions.write_to_template(self, **polVars)
                            polVars["initial_write"] = False

                            # Thermal Settings
                            names = ['5108', '9508']
                            for name in names:
                                polVars["name"] = name
                                polVars["descr"] = f'{name} Thermal Policy'
                                polVars["fan_control_mode"] = 'Balanced'

                                # Write Policies to Template File
                                polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                                ezfunctions.write_to_template(self, **polVars)

                            # Close the Template file
                            polVars["template_file"] = 'template_close.jinja2'
                            ezfunctions.write_to_template(self, **polVars)

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

        if configure == 'Y' or configure == '':
            configure = True
        elif configure == 'N':
            configure = False
        return configure

    #==============================================
    # VMware M2 - Boot and Storage Policies
    #==============================================
    def vmware_m2(self, **kwargs):
        opSystem = kwargs['opSystem']
        if opSystem == 'Windows' : path_sep = '\\'
        else: path_sep = '/'
        org = self.org
        polVars = {}
        polVars["org"] = org
        tfDir = kwargs['tfDir']

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  The Quick Deployment Module - Boot/Storage, will configure policies for a UCS Server ')
            print(f'  Profile connected to an IMM Domain.\n')
            print(f'  This wizard will save the output for these pools in the following files:\n')
            print(f'  - {tfDir}{path_sep}{org}{path_sep}{self.type}{path_sep}bios_policies.yaml')
            print(f'  - {tfDir}{path_sep}{org}{path_sep}{self.type}{path_sep}boot_order_policies.yaml')
            print(f'  - {tfDir}{path_sep}{org}{path_sep}{self.type}{path_sep}storage_policies.yaml')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to run the Quick Deployment Module - Boot/Storage Configuration?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                # Trusted Platform Module
                polVars["Description"] = 'Flag to Determine if the Servers have a TPM Installed.'
                polVars["varInput"] = f'Will any of these servers have a TPM Module Installed?'
                polVars["varDefault"] = 'Y'
                polVars["varName"] = 'TPM Installed'
                tpm_installed = ezfunctions.varBoolLoop(**polVars)

                #_______________________________________________________________________
                #
                # Configure BIOS Policy
                #_______________________________________________________________________

                polVars["initial_write"] = True
                polVars["policy_type"] = 'BIOS Policy'
                polVars["header"] = '%s Variables' % (polVars["policy_type"])
                polVars["template_file"] = 'template_open.jinja2'
                polVars["template_type"] = 'bios_policies'

                # Open the Template file
                ezfunctions.write_to_template(self, **polVars)
                polVars["initial_write"] = False

                # Configure BIOS Policy
                template_names = ['M5_VMware', 'M5_VMware_tpm', 'M6_VMware_tpm']
                for bname in template_names:
                    name = bname
                    polVars["name"] = name
                    polVars["descr"] = f'{name} BIOS Policy'
                    if bname == 'M5_VMware':
                        polVars["policy_template"] = 'Virtualization'
                    elif name == 'M5_VMware_tpm':
                        polVars["policy_template"] = 'Virtualization_tpm'
                    elif name == 'M6_VMware_tpm':
                        polVars["policy_template"] = 'M6_Virtualization_tpm'
                    polVars["bios_settings"] = {
                        'baud_rate':115200,
                        'console_redirection':'serial-port-a',
                        'execute_disable_bit':'disabled',
                        'lv_ddr_mode':'auto',
                        'serial_port_aenable':'enabled',
                        'terminal_type':'vt100'
                    }

                    # Write Policies to Template File
                    polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                    ezfunctions.write_to_template(self, **polVars)

                # Close the Template file
                polVars["template_file"] = 'template_close.jinja2'
                ezfunctions.write_to_template(self, **polVars)

                #_______________________________________________________________________
                #
                # Configure Boot Order Policy
                #_______________________________________________________________________

                polVars["initial_write"] = True
                polVars["policy_type"] = 'Boot Order Policy'
                polVars["header"] = '%s Variables' % (polVars["policy_type"])
                polVars["template_file"] = 'template_open.jinja2'
                polVars["template_type"] = 'boot_order_policies'

                # Open the Template file
                ezfunctions.write_to_template(self, **polVars)
                polVars["initial_write"] = False

                secBootList = [False, True]
                for i in secBootList:
                    # Configure Boot Order Policy
                    if i == False:
                        name = 'VMware_M2_pxe'
                    else:
                        name = 'VMware_M2'
                    polVars["name"] = name
                    polVars["descr"] = f'{name} Boot Order Policy'
                    polVars["boot_mode"] = 'Uefi'
                    if tpm_installed == True:
                        polVars["enable_secure_boot"] = i
                    else:
                        polVars["enable_secure_boot"] = False
                    polVars["boot_mode"] = 'Uefi'
                    if i == False:
                        polVars["boot_devices"] = [
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
                        polVars["boot_devices"] = [
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
                    polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                    ezfunctions.write_to_template(self, **polVars)

                # Close the Template file
                polVars["template_file"] = 'template_close.jinja2'
                ezfunctions.write_to_template(self, **polVars)

                #_______________________________________________________________________
                #
                # Configure Storage Policy
                #_______________________________________________________________________

                polVars["initial_write"] = True
                polVars["policy_type"] = 'Storage Policy'
                polVars["header"] = '%s Variables' % (polVars["policy_type"])
                polVars["template_file"] = 'template_open.jinja2'
                polVars["template_type"] = 'storage_policies'

                # Open the Template file
                ezfunctions.write_to_template(self, **polVars)
                polVars["initial_write"] = False

                # Storage Policy Settings
                name = 'M2_Raid'
                polVars["name"] = name
                polVars["descr"] = f'{name} Storage Policy'
                polVars["drive_group"] = {}
                polVars["global_hot_spares"] = ''
                polVars["m2_configuration"] = { 'controller_slot':'MSTOR-RAID-1' }
                polVars["single_drive_raid_configuration"] = {}
                polVars["unused_disks_state"] = 'No Change'
                polVars["use_jbod_for_vd_creation"] = True

                # Write Policies to Template File
                polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                ezfunctions.write_to_template(self, **polVars)

                # Close the Template file
                polVars["template_file"] = 'template_close.jinja2'
                ezfunctions.write_to_template(self, **polVars)

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
    def vmware_raid1(self, **kwargs):
        opSystem = kwargs['opSystem']
        if opSystem == 'Windows' : path_sep = '\\'
        else: path_sep = '/'
        org = self.org
        polVars = {}
        polVars["org"] = org
        tfDir = kwargs['tfDir']

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  The Quick Deployment Module - Boot/Storage, will configure policies for a UCS Server ')
            print(f'  Profile connected to an IMM Domain.\n')
            print(f'  This wizard will save the output for these pools in the following files:\n')
            print(f'  - {tfDir}{path_sep}{org}{path_sep}{self.type}{path_sep}bios_policies.yaml')
            print(f'  - {tfDir}{path_sep}{org}{path_sep}{self.type}{path_sep}boot_order_policies.yaml')
            print(f'  - {tfDir}{path_sep}{org}{path_sep}{self.type}{path_sep}storage_policies.yaml')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to run the Quick Deployment Module - Boot/Storage Configuration?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                # Trusted Platform Module
                polVars["Description"] = 'Flag to Determine if the Servers have a TPM Installed.'
                polVars["varInput"] = f'Will these servers have a TPM Module Installed?'
                polVars["varDefault"] = 'Y'
                polVars["varName"] = 'TPM Installed'
                tpm_installed = ezfunctions.varBoolLoop(**polVars)

                #_______________________________________________________________________
                #
                # Configure BIOS Policy
                #_______________________________________________________________________

                polVars["initial_write"] = True
                polVars["policy_type"] = 'BIOS Policy'
                polVars["header"] = '%s Variables' % (polVars["policy_type"])
                polVars["template_file"] = 'template_open.jinja2'
                polVars["template_type"] = 'bios_policies'

                # Open the Template file
                ezfunctions.write_to_template(self, **polVars)
                polVars["initial_write"] = False

                # Configure BIOS Policy
                name = 'VMware'
                polVars["name"] = name
                polVars["descr"] = f'{name} BIOS Policy'
                if tpm_installed == True:
                    polVars["policy_template"] = 'VMware_tpm'
                else:
                    polVars["policy_template"] = 'VMware'

                # Write Policies to Template File
                polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                ezfunctions.write_to_template(self, **polVars)

                # Close the Template file
                polVars["template_file"] = 'template_close.jinja2'
                ezfunctions.write_to_template(self, **polVars)

                #_______________________________________________________________________
                #
                # Configure Boot Order Policy
                #_______________________________________________________________________

                polVars["initial_write"] = True
                polVars["policy_type"] = 'Boot Order Policy'
                polVars["header"] = '%s Variables' % (polVars["policy_type"])
                polVars["template_file"] = 'template_open.jinja2'
                polVars["template_type"] = 'boot_order_policies'

                # Open the Template file
                ezfunctions.write_to_template(self, **polVars)
                polVars["initial_write"] = False

                secBootList = [False, True]
                for i in secBootList:
                    # Configure Boot Order Policy
                    if i == False:
                        name = 'VMware_Raid1_pxe'
                    else:
                        name = 'VMware_Raid1'
                    polVars["name"] = name
                    polVars["descr"] = f'{name} Boot Order Policy'
                    polVars["boot_mode"] = 'Uefi'
                    if tpm_installed == True:
                        polVars["enable_secure_boot"] = i
                    else:
                        polVars["enable_secure_boot"] = False
                    polVars["boot_mode"] = 'Uefi'
                    if i == False:
                        polVars["boot_devices"] = [
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
                        polVars["boot_devices"] = [
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
                    polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                    ezfunctions.write_to_template(self, **polVars)

                # Close the Template file
                polVars["template_file"] = 'template_close.jinja2'
                ezfunctions.write_to_template(self, **polVars)

                #_______________________________________________________________________
                #
                # Configure Storage Policy
                #_______________________________________________________________________

                polVars["initial_write"] = True
                polVars["policy_type"] = 'Storage Policy'
                polVars["header"] = '%s Variables' % (polVars["policy_type"])
                polVars["template_file"] = 'template_open.jinja2'
                polVars["template_type"] = 'storage_policies'

                # Open the Template file
                ezfunctions.write_to_template(self, **polVars)
                polVars["initial_write"] = False

                name = 'MRAID'
                polVars["name"] = name
                polVars["descr"] = f'{name} Storage Policy'
                polVars["drive_group"] = [
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
                polVars["global_hot_spares"] = ''
                polVars["m2_configuration"] = []
                polVars["single_drive_raid_configuration"] = {}
                polVars["unused_disks_state"] = 'No Change'
                polVars["use_jbod_for_vd_creation"] = True

                # Write Policies to Template File
                polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                ezfunctions.write_to_template(self, **polVars)

                # Close the Template file
                polVars["template_file"] = 'template_close.jinja2'
                ezfunctions.write_to_template(self, **polVars)

                configure_loop = True

            elif configure == 'N':
                configure_loop = True
            else:
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                print(f'\n-------------------------------------------------------------------------------------------\n')

    #================================================
    # VMware PXE - BIOS, Boot and Storage Policies
    #================================================
    def vmware_pxe(self, **kwargs):
        org                 = self.org
        path_sep            = kwargs['path_sep']
        polVars        = {}
        polVars["org"] = org
        tfDir = kwargs['tfDir']

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  The Quick Deployment Module - Boot/Storage, will configure policies for a UCS Server ')
            print(f'  Profile connected to an IMM Domain.\n')
            print(f'  This wizard will save the output for these policies in the following file:\n')
            print(f'  - {tfDir}{path_sep}{org}{path_sep}{self.type}{path_sep}compute.yaml')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to run the Quick Deployment Module - Boot/Storage Configuration?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                # Trusted Platform Module
                polVars["Description"] = 'Flag to Determine if the Servers have a TPM Installed.'
                polVars["varInput"] = f'Will these servers have a TPM Module Installed?'
                polVars["varDefault"] = 'Y'
                polVars["varName"] = 'TPM Installed'
                tpm_installed = ezfunctions.varBoolLoop(**polVars)

                #_______________________________________________________________________
                #
                # Configure BIOS Policy
                #_______________________________________________________________________

                polVars["initial_write"] = True
                polVars["policy_type"] = 'BIOS Policy'
                polVars["header"] = '%s Variables' % (polVars["policy_type"])
                polVars["template_file"] = 'template_open.jinja2'
                polVars["template_type"] = 'bios_policies'

                # Open the Template file
                ezfunctions.write_to_template(self, **polVars)
                polVars["initial_write"] = False

                # Configure BIOS Policy
                name = 'VMware'
                polVars["name"] = name
                polVars["descr"] = f'{name} BIOS Policy'
                if tpm_installed == True:
                    polVars["policy_template"] = 'VMware_tpm'
                else:
                    polVars["policy_template"] = 'VMware'

                # Write Policies to Template File
                polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                ezfunctions.write_to_template(self, **polVars)

                # Close the Template file
                polVars["template_file"] = 'template_close.jinja2'
                ezfunctions.write_to_template(self, **polVars)

                #_______________________________________________________________________
                #
                # Configure Boot Order Policy
                #_______________________________________________________________________

                polVars["initial_write"] = True
                polVars["policy_type"] = 'Boot Order Policy'
                polVars["header"] = '%s Variables' % (polVars["policy_type"])
                polVars["template_file"] = 'template_open.jinja2'
                polVars["template_type"] = 'boot_order_policies'

                # Open the Template file
                ezfunctions.write_to_template(self, **polVars)
                polVars["initial_write"] = False

                # Configure Boot Order Policy
                name = 'VMware_PXE'
                polVars["name"] = name
                polVars["descr"] = f'{name} Boot Order Policy'
                polVars["boot_mode"] = 'Uefi'
                polVars["enable_secure_boot"] = False
                polVars["boot_mode"] = 'Uefi'
                polVars["boot_devices"] = [
                    {
                        'enabled':True,
                        'device_name':'KVM-DVD',
                        'device_type':'virtual_media',
                        'object_type':'boot.VirtualMedia',
                        'subtype':'kvm-mapped-dvd'
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

                # Write Policies to Template File
                polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                ezfunctions.write_to_template(self, **polVars)

                # Close the Template file
                polVars["template_file"] = 'template_close.jinja2'
                ezfunctions.write_to_template(self, **polVars)

                configure_loop = True

            elif configure == 'N':
                configure_loop = True
            else:
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                print(f'\n-------------------------------------------------------------------------------------------\n')

def policy_select_loop(jsonData, easy_jsonData, name_prefix, policy, **polVars):
    loop_valid = False
    while loop_valid == False:
        create_policy = True
        inner_policy = policy.split('.')[1]
        inner_type = policy.split('.')[0]
        inner_var = policy.split('.')[2]
        polVars[inner_var] = ''
        polVars["policies"],policyData = ezfunctions.policies_parse(polVars["org"], inner_type, inner_policy)
        if not len(polVars["policies"]) > 0:
            valid = False
            while valid == False:

                x = inner_policy.split('_')
                policy_description = []
                for y in x:
                    y = y.capitalize()
                    policy_description.append(y)
                policy_description = " ".join(policy_description)
                policy_description = policy_description.replace('Ipmi', 'IPMI')
                policy_description = policy_description.replace('Ip', 'IP')
                policy_description = policy_description.replace('Iqn', 'IQN')
                policy_description = policy_description.replace('Ldap', 'LDAP')
                policy_description = policy_description.replace('Ntp', 'NTP')
                policy_description = policy_description.replace('Sd', 'SD')
                policy_description = policy_description.replace('Smtp', 'SMTP')
                policy_description = policy_description.replace('Snmp', 'SNMP')
                policy_description = policy_description.replace('Ssh', 'SSH')
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

                if polVars["allow_opt_out"] == True:
                    Question = input(f'Do you want to create a(n) {policy_description}?  Enter "Y" or "N" [Y]: ')
                    if Question == '' or Question == 'Y':
                        create_policy = True
                        valid = True
                    elif Question == 'N':
                        create_policy = False
                        valid = True
                        return polVars[inner_var],policyData
                else:
                    create_policy = True
                    valid = True

        else:
            polVars[inner_var] = ezfunctions.choose_policy(inner_policy, **polVars)
            if inner_var == 'ldap_policy':
                print('matched')
                print(polVars[inner_var])
                exit()
            if polVars[inner_var] == 'create_policy':
                create_policy = True
            elif polVars[inner_var] == '' and polVars["allow_opt_out"] == True:
                loop_valid = True
                create_policy = False
                return polVars[inner_var],policyData
            elif not polVars[inner_var] == '':
                loop_valid = True
                create_policy = False
                return polVars[inner_var],policyData
        if create_policy == True:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  Starting module to create {inner_policy}')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            if inner_policy == 'ip_pools':
                pools.pools(name_prefix, polVars["org"], inner_type).ip_pools(jsonData, easy_jsonData)
            elif inner_policy == 'iqn_pools':
                pools.pools(name_prefix, polVars["org"], inner_type).iqn_pools(jsonData, easy_jsonData)
            elif inner_policy == 'mac_pools':
                pools.pools(name_prefix, polVars["org"], inner_type).mac_pools(jsonData, easy_jsonData)
            elif inner_policy == 'uuid_pools':
                pools.pools(name_prefix, polVars["org"], inner_type).uuid_pools(jsonData, easy_jsonData)
            elif inner_policy == 'wwnn_pools':
                pools.pools(name_prefix, polVars["org"], inner_type).wwnn_pools(jsonData, easy_jsonData)
            elif inner_policy == 'wwpn_pools':
                pools.pools(name_prefix, polVars["org"], inner_type).wwpn_pools(jsonData, easy_jsonData)
            elif inner_policy == 'adapter_configuration_policies':
                p1.policies(name_prefix, polVars["org"], inner_type).adapter_configuration_policies(jsonData, easy_jsonData)
            elif inner_policy == 'bios_policies':
                p1.policies(name_prefix, polVars["org"], inner_type).bios_policies(jsonData, easy_jsonData)
            elif inner_policy == 'boot_order_policies':
                p1.policies(name_prefix, polVars["org"], inner_type).boot_order_policies(jsonData, easy_jsonData)
            elif inner_policy == 'certificate_management_policies':
                p1.policies(name_prefix, polVars["org"], inner_type).certificate_management_policies(jsonData, easy_jsonData)
            elif inner_policy == 'device_connector_policies':
                p1.policies(name_prefix, polVars["org"], inner_type).device_connector_policies(jsonData, easy_jsonData)
            elif inner_policy == 'ethernet_adapter_policies':
                lan.policies(name_prefix, polVars["org"], inner_type).ethernet_adapter_policies(jsonData, easy_jsonData)
            elif inner_policy == 'ethernet_network_control_policies':
                lan.policies(name_prefix, polVars["org"], inner_type).ethernet_network_control_policies(jsonData, easy_jsonData)
            elif inner_policy == 'ethernet_network_group_policies':
                lan.policies(name_prefix, polVars["org"], inner_type).ethernet_network_group_policies(jsonData, easy_jsonData)
            elif inner_policy == 'ethernet_network_policies':
                lan.policies(name_prefix, polVars["org"], inner_type).ethernet_network_policies(jsonData, easy_jsonData)
            elif inner_policy == 'ethernet_qos_policies':
                lan.policies(name_prefix, polVars["org"], inner_type).ethernet_qos_policies(jsonData, easy_jsonData)
            elif inner_policy == 'fibre_channel_adapter_policies':
                san.policies(name_prefix, polVars["org"], inner_type).fibre_channel_adapter_policies(jsonData, easy_jsonData)
            elif inner_policy == 'fibre_channel_network_policies':
                san.policies(name_prefix, polVars["org"], inner_type).fibre_channel_network_policies(jsonData, easy_jsonData)
            elif inner_policy == 'fibre_channel_qos_policies':
                san.policies(name_prefix, polVars["org"], inner_type).fibre_channel_qos_policies(jsonData, easy_jsonData)
            elif inner_policy == 'flow_control_policies':
                p1.policies(name_prefix, polVars["org"], inner_type).flow_control_policies(jsonData, easy_jsonData)
            elif inner_policy == 'imc_access_policies':
                p1.policies(name_prefix, polVars["org"], inner_type).imc_access_policies(jsonData, easy_jsonData)
            elif inner_policy == 'ipmi_over_lan_policies':
                p1.policies(name_prefix, polVars["org"], inner_type).ipmi_over_lan_policies(jsonData, easy_jsonData)
            elif inner_policy == 'iscsi_adapter_policies':
                lan.policies(name_prefix, polVars["org"], inner_type).iscsi_adapter_policies(jsonData, easy_jsonData)
            elif inner_policy == 'iscsi_boot_policies':
                lan.policies(name_prefix, polVars["org"], inner_type).iscsi_boot_policies(jsonData, easy_jsonData)
            elif inner_policy == 'iscsi_static_target_policies':
                lan.policies(name_prefix, polVars["org"], inner_type).iscsi_static_target_policies(jsonData, easy_jsonData)
            elif inner_policy == 'lan_connectivity_policies':
                lan.policies(name_prefix, polVars["org"], inner_type).lan_connectivity_policies(jsonData, easy_jsonData)
            elif inner_policy == 'ldap_policies':
                p1.policies(name_prefix, polVars["org"], inner_type).ldap_policies(jsonData, easy_jsonData)
            elif inner_policy == 'link_aggregation_policies':
                p1.policies(name_prefix, polVars["org"], inner_type).link_aggregation_policies(jsonData, easy_jsonData)
            elif inner_policy == 'link_control_policies':
                p1.policies(name_prefix, polVars["org"], inner_type).link_control_policies(jsonData, easy_jsonData)
            elif inner_policy == 'local_user_policies':
                p2.policies(name_prefix, polVars["org"], inner_type).local_user_policies(jsonData, easy_jsonData)
            elif inner_policy == 'multicast_policies':
                vxan.policies(name_prefix, polVars["org"], inner_type).multicast_policies(jsonData, easy_jsonData)
            elif inner_policy == 'network_connectivity_policies':
                p2.policies(name_prefix, polVars["org"], inner_type).network_connectivity_policies(jsonData, easy_jsonData)
            elif inner_policy == 'ntp_policies':
                p2.policies(name_prefix, polVars["org"], inner_type).ntp_policies(jsonData, easy_jsonData)
            elif inner_policy == 'persistent_memory_policies':
                p2.policies(name_prefix, polVars["org"], inner_type).persistent_memory_policies(jsonData, easy_jsonData)
            elif inner_policy == 'port_policies':
                p2.policies(name_prefix, polVars["org"], inner_type).port_policies(jsonData, easy_jsonData)
            elif inner_policy == 'san_connectivity_policies':
                san.policies(name_prefix, polVars["org"], inner_type).san_connectivity_policies(jsonData, easy_jsonData)
            elif inner_policy == 'sd_card_policies':
                p3.policies(name_prefix, polVars["org"], inner_type).sd_card_policies(jsonData, easy_jsonData)
            elif inner_policy == 'serial_over_lan_policies':
                p3.policies(name_prefix, polVars["org"], inner_type).serial_over_lan_policies(jsonData, easy_jsonData)
            elif inner_policy == 'smtp_policies':
                p3.policies(name_prefix, polVars["org"], inner_type).smtp_policies(jsonData, easy_jsonData)
            elif inner_policy == 'snmp_policies':
                p3.policies(name_prefix, polVars["org"], inner_type).snmp_policies(jsonData, easy_jsonData)
            elif inner_policy == 'ssh_policies':
                p3.policies(name_prefix, polVars["org"], inner_type).ssh_policies(jsonData, easy_jsonData)
            elif inner_policy == 'storage_policies':
                p3.policies(name_prefix, polVars["org"], inner_type).storage_policies(jsonData, easy_jsonData)
            elif inner_policy == 'switch_control_policies':
                p3.policies(name_prefix, polVars["org"], inner_type).switch_control_policies(jsonData, easy_jsonData)
            elif inner_policy == 'syslog_policies':
                p3.policies(name_prefix, polVars["org"], inner_type).syslog_policies(jsonData, easy_jsonData)
            elif inner_policy == 'system_qos_policies':
                p3.policies(name_prefix, polVars["org"], inner_type).system_qos_policies(jsonData, easy_jsonData)
            elif inner_policy == 'thermal_policies':
                p3.policies(name_prefix, polVars["org"], inner_type).thermal_policies(jsonData, easy_jsonData)
            elif inner_policy == 'ucs_server_profiles':
                profiles.profiles(name_prefix, polVars["org"], inner_type).ucs_server_profiles(jsonData, easy_jsonData)
            elif inner_policy == 'ucs_server_profile_templates':
                profiles.profiles(name_prefix, polVars["org"], inner_type).ucs_server_profile_templates(jsonData, easy_jsonData)
            elif inner_policy == 'virtual_kvm_policies':
                p3.policies(name_prefix, polVars["org"], inner_type).virtual_kvm_policies(jsonData, easy_jsonData)
            elif inner_policy == 'virtual_media_policies':
                p3.policies(name_prefix, polVars["org"], inner_type).virtual_media_policies(jsonData, easy_jsonData)
            elif inner_policy == 'vlan_policies':
                vxan.policies(name_prefix, polVars["org"], inner_type).vlan_policies(jsonData, easy_jsonData)
            elif inner_policy == 'vsan_policies':
                vxan.policies(name_prefix, polVars["org"], inner_type).vsan_policies(jsonData, easy_jsonData)
