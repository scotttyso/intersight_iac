#!/usr/bin/env python3

import ipaddress
import jinja2
import pkg_resources
import validating
from easy_functions import ntp_alternate, ntp_primary
from easy_functions import policy_select_loop
from easy_functions import port_list_eth, port_list_fc, port_modes_fc
from easy_functions import snmp_trap_servers, snmp_users
from easy_functions import syslog_servers
from easy_functions import ucs_domain_serials
from easy_functions import validate_vlan_in_policy
from easy_functions import variablesFromAPI
from easy_functions import varBoolLoop
from easy_functions import varNumberLoop
from easy_functions import varStringLoop
from easy_functions import vlan_list_full
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
        primary_dns = kwargs['primary_dns']
        secondary_dns = kwargs['secondary_dns']
        name_prefix = self.name_prefix
        org = self.org
        templateVars = {}
        templateVars["org"] = org
        vlan_type = 'policies_vlan'
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
            print(f'  - Intersight/{org}/{self.type}/network_connectivity_policies.auto.tfvars')
            print(f'  - Intersight/{org}/{self.type}/ntp_policies.auto.tfvars')
            print(f'  - Intersight/{org}/{self.type}/port_policies.auto.tfvars')
            print(f'  - Intersight/{org}/{self.type}/system_qos_policies.auto.tfvars')
            print(f'  - Intersight/{org}/{self.type}/switch_control_policies.auto.tfvars')
            print(f'  - Intersight/{org}/{self.type}/vsan_policies.auto.tfvars')
            print(f'  - Intersight/{org}/{vlan_type}/multicast_policies.auto.tfvars')
            print(f'  - Intersight/{org}/{vlan_type}/vlan_policies.auto.tfvars')
            print(f'  - Intersight/{org}/{domain_type}/ucs_domain_profiles.auto.tfvars')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to run the Quick Deployment Module - Domain Policy Configuration?  \nEnter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                loop_count = 1
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

                    fc_mode,ports_in_use,fc_converted_ports,port_modes = port_modes_fc(jsonData, easy_jsonData, name_prefix, **templateVars)
                    templateVars["fc_mode"] = fc_mode
                    templateVars["ports_in_use"] = ports_in_use
                    templateVars["fc_converted_ports"] = fc_converted_ports
                    templateVars["port_modes"] = port_modes

                    # Ethernet Uplink Port-Channel
                    templateVars['port_type'] = 'Ethernet Uplink Port-Channel'
                    port_channel_ethernet_uplinks,templateVars['ports_in_use'] = port_list_eth(jsonData, easy_jsonData, name_prefix, **templateVars)

                    # Fibre-Channel Port-Channel
                    templateVars["fc_ports_in_use"] = []
                    templateVars["port_type"] == 'Fibre Channel Port-Channel'
                    Fab_A,Fab_B,fc_ports_in_use = port_list_fc(jsonData, easy_jsonData, name_prefix, **templateVars)
                    Fabric_A_fc_port_channels = Fab_A
                    Fabric_B_fc_port_channels = Fab_B
                    templateVars["fc_ports_in_use"] = fc_ports_in_use

                    # Server Ports
                    templateVars['port_type'] = 'Server Ports'
                    port_role_servers,templateVars['ports_in_use'] = port_list_eth(jsonData, easy_jsonData, name_prefix, **templateVars)

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

                    # System MTU for System QoS Policy
                    templateVars["Description"] = 'This option will set the MTU to 9000 if answer is "Y"; 1500 if answer is "N".'
                    templateVars["varInput"] = f'Do you want to enable Jumbo MTU?  Enter "Y" or "N"'
                    templateVars["varDefault"] = 'Y'
                    templateVars["varName"] = 'MTU'
                    answer = varBoolLoop(**templateVars)
                    if answer == True:
                        mtu = 9000
                    else:
                        mtu = 1500

                    valid = False
                    while valid == False:
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        print(f'  The allowed vlan list can be in the format of:')
                        print(f'     5 - Single VLAN')
                        print(f'     1-10 - Range of VLANs')
                        print(f'     1,2,3,4,5,11,12,13,14,15 - List of VLANs')
                        print(f'     1-10,20-30 - Ranges and Lists of VLANs')
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        VlanList = input('Enter the VLAN or List of VLANs to add to the Domain: ')
                        if not VlanList == '':
                            vlanListExpanded = vlan_list_full(VlanList)
                            valid_vlan = True
                            for vlan in vlanListExpanded:
                                valid_vlan = validating.number_in_range('VLAN ID', vlan, 1, 4094)
                                if valid_vlan == False:
                                    continue
                            if valid_vlan == False:
                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                print(f'  Error with VLAN(s) assignment!!! VLAN List: "{VlanList}" is not Valid.')
                                print(f'  The allowed vlan list can be in the format of:')
                                print(f'     5 - Single VLAN')
                                print(f'     1-10 - Range of VLANs')
                                print(f'     1,2,3,4,5,11,12,13,14,15 - List of VLANs')
                                print(f'     1-10,20-30 - Ranges and Lists of VLANs')
                                print(f'\n-------------------------------------------------------------------------------------------\n')
                            else:
                                valid = True
                        else:
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            print(f'  The allowed vlan list can be in the format of:')
                            print(f'     5 - Single VLAN')
                            print(f'     1-10 - Range of VLANs')
                            print(f'     1,2,3,4,5,11,12,13,14,15 - List of VLANs')
                            print(f'     1-10,20-30 - Ranges and Lists of VLANs')
                            print(f'\n-------------------------------------------------------------------------------------------\n')

                    valid = False
                    while valid == False:
                        nativeVlan = input('What is the Native VLAN for the Ethernet Port-Channel?  [press enter to skip]: ')
                        if nativeVlan == '':
                            valid = True
                        else:
                            for vlan in vlanListExpanded:
                                if int(nativeVlan) == int(vlan):
                                    native_count = 1
                            if not native_count == 1:
                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                print(f'  Error!! The Native VLAN was not in the VLAN Policy List.')
                                print(f'  VLAN Policy List is: "{VlanList}"')
                                print(f'\n-------------------------------------------------------------------------------------------\n')
                            else:
                                valid = True

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  UCS Domain Name        = "{domain_name}"')
                    print(f'  Device Model           = "{templateVars["device_model"]}"')
                    print(f'  Serial Number Fabric A = "{templateVars["serial_number_fabric_a"]}"')
                    print(f'  Serial Number Fabric B = "{templateVars["serial_number_fabric_b"]}"')
                    print(f'  Port Policy Variables:')
                    print(f'    Ethernet Port-Channel Ports      = "{templateVars["timezone"]}"')
                    print(f'    Fibre-Channel Port-Channel Ports = "{templateVars["timezone"]}"')
                    print(f'    Server Ports                     = "{templateVars["timezone"]}"')
                    print(f'  System MTU: {mtu}')
                    print(f'  NTP Variables:')
                    print(f'    timezone: "{templateVars["timezone"]}"')
                    if len(templateVars["ntp_servers"]) > 0:
                        print(f'    ntp_servers = [')
                        for server in templateVars["ntp_servers"]:
                            print(f'      "{server}",')
                        print(f'    ]')
                    print(f'  VLAN Pool: "{VlanList}"')
                    print(f'  VSAN Fabric A: "{templateVars["vsan_a"]}"')
                    print(f'  VSAN Fabric B: "{templateVars["vsan_b"]}"')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
                        if confirm_policy == 'Y' or confirm_policy == '':

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
                            templateVars["inband_vlan_id"] = name
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
    # LAN and SAN Policies
    #==============================================
    def lan_san_policies(self, jsonData, easy_jsonData, **kwargs):
        mtu = kwargs['mtu']
        name_prefix = self.name_prefix
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

                    # Get List of VLAN's from the Domain Policies
                    templateVars["name"] = 'Quick Start Deployment'
                    policy_list = [
                        'policies_vlans.vlan_policies.vlan_policy',
                    ]
                    templateVars["allow_opt_out"] = False
                    for policy in policy_list:
                        vlan_policy,policyData = policy_select_loop(jsonData, easy_jsonData, name_prefix, policy, **templateVars)

                    vlan_list = []
                    for item in policyData['vlan_policies'][0][vlan_policy][0]['vlans']:
                        for k, v in item.items():
                            vlan_list.append(v[0]['vlan_list'])

                    vlan_convert = ''
                    for vlan in vlan_list:
                        if vlan_convert == '':
                            vlan_convert = str(vlan)
                        else:
                            vlan_convert = vlan_convert + ',' + str(vlan)

                    vlan_policy_list = vlan_list_full(vlan_convert)

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
                    for x in fabrics:
                        valid = False
                        while valid == False:
                            templateVars["Description"] = f'VSAN Identifier for Fabric {x}'
                            templateVars["varInput"] = f'What VSAN Identifier do you want to Assign to Fabric {x}?'
                            if x == 'A':
                                templateVars["varDefault"] = 100
                            else:
                                templateVars["varDefault"] = 200
                            templateVars["varName"] = 'VSAN'
                            templateVars["minNum"] = 1
                            templateVars["maxNum"] = 4094
                            vsan_id = varNumberLoop(**templateVars)
                        
                            policy_list = [
                                'policies.vsan_policies.vsan_policy'
                            ]
                            templateVars["allow_opt_out"] = False
                            for policy in policy_list:
                                vsan_policy,policyData = policy_select_loop(jsonData, easy_jsonData, name_prefix, policy, **templateVars)

                            vsan_list = []
                            for item in policyData['vsan_policies'][0][vsan_policy][0]['vsans']:
                                for key, value in item.items():
                                    vsan_list.append(value[0]['vsan_id'])

                            vsan_string = ''
                            for vsan in vsan_list:
                                if vsan_string == '':
                                    vsan_string = str(vsan)
                                else:
                                    vsan_string = vsan_string + ',' + str(vsan)
                            vsan_list = vlan_list_full(vsan_string)
                            vsan_count = 0
                            for vsan in vsan_list:
                                if int(vsan_id) == int(vsan):
                                    vsan_count = 1
                                    break
                            if vsan_count == 0:
                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                print(f'  Error with VSAN!!  The VSAN {vsan_id} is not in the VSAN Policy')
                                print(f'  {vsan_policy}.  Options are {vsan_list}.')
                                print(f'\n-------------------------------------------------------------------------------------------\n')
                            else:
                                templateVars[f"vsan_{x}"] = vsan_id
                                valid = True
                    
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  Network Configuration Variables:')
                    print(f'    MGMT VLAN     = {mgmt_vlan}')
                    print(f'    vMotion VLAN  = {vmotion_vlan}')
                    print(f'    Storage VLAN  = {storage_vlan}')
                    print(f'    Data VLANs    = "{VlanList}"')
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
                            templateVars["adapter_template"] = 'VMware'

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

                            #_______________________________________________________________________
                            #
                            # Configure Fibre Channel Adapter Policy
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
                            templateVars["adapter_template"] = 'VMware'

                            # Write Policies to Template File
                            templateVars["template_file"] = '%s.jinja2' % ('ethernet_adapter_templates')
                            write_to_template(self, **templateVars)

                            # Close the Template file
                            templateVars["template_file"] = 'template_close.jinja2'
                            write_to_template(self, **templateVars)

                            #_______________________________________________________________________
                            #
                            # Configure Fibre Channel Network Policy
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
                            # Configure Fibre Channel QoS Policy
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
                    print(f'        - WWNN Pool A: 20:00:00:25:B5:[prefix]:00:00 to 20:00:00:25:B5:[prefix]:03:E7')
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
                                    elif nam == 'DATA' and fab == 'A': key_id = 'G'
                                    elif nam == 'DATA' and fab == 'B': key_id = 'H'

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
        vlan_policy = kwargs['vlan_policy']
        vsan_policies = kwargs['vsan_policies']
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
            print(f'  - Intersight/{org}/{self.type}/bios_policies.auto.tfvars')
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

                    # Get List of VLAN's from the Domain Policies
                    policy_list = [
                        'policies_vlans.vlan_policies.vlan_policy',
                    ]
                    templateVars["allow_opt_out"] = False
                    for policy in policy_list:
                        vlan_policy,policyData = policy_select_loop(jsonData, easy_jsonData, name_prefix, policy, **templateVars)

                    vlan_list = []
                    for item in policyData['vlan_policies'][0][vlan_policy][0]['vlans']:
                        for k, v in item.items():
                            vlan_list.append(v[0]['vlan_list'])

                    vlan_convert = ''
                    for vlan in vlan_list:
                        if vlan_convert == '':
                            vlan_convert = str(vlan)
                        else:
                            vlan_convert = vlan_convert + ',' + str(vlan)

                    vlan_policy_list = vlan_list_full(vlan_convert)

                    templateVars["multi_select"] = False

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

                    ilCount = 1
                    syslog_loop = False
                    while syslog_loop == False:
                        question = input(f'Do you want to configure Remote Syslog?  Enter "Y" or "N" [Y]: ')
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
                            templateVars['remote_logging'] = [
                                {
                                    'server1':{
                                        'enable':False,
                                        'hostname':'0.0.0.0',
                                        'min_severity':'warning',
                                        'port':514,
                                        'protocol':'udp'
                                    },
                                    'server2':{
                                        'enable':False,
                                        'hostname':'0.0.0.0',
                                        'min_severity':'warning',
                                        'port':514,
                                        'protocol':'udp'
                                    }
                                }
                            ]
                            syslog_loop = True
                        else:
                            print(f'\n------------------------------------------------------\n')
                            print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                            print(f'\n------------------------------------------------------\n')

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  Policy Variables:')
                    print(f'    IMC Access VLAN  = {imc_vlan}')
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
    # Standalone Server Policies
    #==============================================
    def standalone_policies(self, jsonData, easy_jsonData, server_type):
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
            print(f'  - Intersight/{org}/{self.type}/bios_policies.auto.tfvars')
            print(f'  - Intersight/{org}/{self.type}/boot_order_policies.auto.tfvars')
            print(f'  - Intersight/{org}/{self.type}/imc_access_policies.auto.tfvars')
            print(f'  - Intersight/{org}/{self.type}/ipmi_over_lan_policies.auto.tfvars')
            print(f'  - Intersight/{org}/{self.type}/local_user_policies.auto.tfvars')
            print(f'  - Intersight/{org}/{self.type}/power_policies.auto.tfvars')
            print(f'  - Intersight/{org}/{self.type}/serial_over_lan_policies.auto.tfvars')
            print(f'  - Intersight/{org}/{self.type}/snmp_policies.auto.tfvars')
            print(f'  - Intersight/{org}/{self.type}/storage_policies.auto.tfvars')
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

                    # Get List of VLAN's from the Domain Policies
                    policy_list = [
                        'policies_vlans.vlan_policies.vlan_policy',
                    ]
                    templateVars["allow_opt_out"] = False
                    for policy in policy_list:
                        vlan_policy,policyData = policy_select_loop(jsonData, easy_jsonData, name_prefix, policy, **templateVars)

                    vlan_list = []
                    for item in policyData['vlan_policies'][0][vlan_policy][0]['vlans']:
                        for k, v in item.items():
                            vlan_list.append(v[0]['vlan_list'])

                    vlan_convert = ''
                    for vlan in vlan_list:
                        if vlan_convert == '':
                            vlan_convert = str(vlan)
                        else:
                            vlan_convert = vlan_convert + ',' + str(vlan)

                    vlan_policy_list = vlan_list_full(vlan_convert)

                    templateVars["multi_select"] = False

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
                    print(f'    IMC Access VLAN  = {imc_vlan}')
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
        name_prefix = self.name_prefix
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

                # Write Policies to Template File
                templateVars["template_file"] = '%s.jinja2' % ('boot_policies')
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

                configure_loop = True

            elif configure == 'N':
                configure_loop = True
            else:
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                print(f'\n-------------------------------------------------------------------------------------------\n')

    #==============================================
    # VMware Raid1 - Boot and Storage Policies
    #==============================================
    def vmware_raid1(self):
        name_prefix = self.name_prefix
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
                name = 'VMware_Raid1'
                templateVars["name"] = name
                templateVars["descr"] = f'{name} Boot Order Policy'
                templateVars["boot_mode"] = 'Uefi'
                templateVars["enable_secure_boot"] = True
                templateVars["boot_mode"] = 'Uefi'
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

                # Write Policies to Template File
                templateVars["template_file"] = '%s.jinja2' % ('boot_policies')
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
