#!/usr/bin/env python3
from copy import deepcopy
import ezfunctions
import ipaddress
import json
import lan
import p1
import p2
import p3
import pools
import profiles
import re
import san
import textwrap
import validating
import vxan
import yaml

class MyDumper(yaml.Dumper):
    def increase_indent(self, flow=False, indentless=False):
        return super(MyDumper, self).increase_indent(flow, False)

class quick_start(object):
    def __init__(self, name_prefix, org, type):
        self.name_prefix = name_prefix
        self.org = org
        self.type = type

    #==============================================
    # BIOS Policy
    #==============================================
    def bios_policies(self, **kwargs):
        args = kwargs['args']
        baseRepo = args.dir
        org = self.org
        path_sep = kwargs['path_sep']

        print(f'\n-------------------------------------------------------------------------------------------\n')
        print(f'  The Quick Deployment Module - BIOS policies for a UCS Server ')
        print(f'  This wizard will save the output for the BIOS Policy to the following file:\n')
        print(f'  - {baseRepo}{path_sep}{org}{path_sep}{self.type}{path_sep}compute.yaml')
        print(f'\n-------------------------------------------------------------------------------------------\n')
        # Trusted Platform Module
        kwargs['Description'] = 'Flag to Determine if the Servers have a TPM Installed.'
        kwargs['varInput'] = f'Will any of these servers have a TPM Module Installed?'
        kwargs['varDefault'] = 'Y'
        kwargs['varName'] = 'TPM Installed'
        kwargs['tpm_installed'] = ezfunctions.varBoolLoop(**kwargs)

        #_______________________________________________________________________
        #
        # Configure BIOS Policy
        #_______________________________________________________________________
        polVars = {}
        template_names = ['M5-Virtualization', 'M5-virtualization-tpm', 'M6-virtualization-tpm']
        for bname in template_names:
            name = bname
            polVars['name'] = name
            polVars['descr'] = f'{name} BIOS Policy'
            if bname == 'M5-Virtualization':
                polVars['bios_template'] = 'Virtualization'
            elif name == 'M5-virtualization-tpm':
                polVars['bios_template'] = 'Virtualization_tpm'
            elif name == 'M6-virtualization-tpm':
                polVars['bios_template'] = 'M6_Virtualization_tpm'
            polVars['baud_rate'] = 115200
            polVars['console_redirection'] = 'serial-port-a'
            polVars['execute_disable_bit'] = 'disabled'
            polVars['lv_ddr_mode'] = 'auto'
            polVars['serial_port_aenable'] = 'enabled'
            polVars['terminal_type'] = 'vt100'

            # Add Policy Variables to immDict
            kwargs['class_path'] = 'intersight,policies,bios'
            kwargs = ezfunctions.ez_append(polVars, **kwargs)
        return kwargs

    #==============================================
    # Boot and Storage Policies
    #==============================================
    def boot_and_storage(self, **kwargs):
        args = kwargs['args']
        baseRepo = args.dir
        boot_type = kwargs['boot_type']
        org = self.org
        path_sep = kwargs['path_sep']

        print(f'\n-------------------------------------------------------------------------------------------\n')
        print(f'  The Quick Deployment Module - Boot/Storage, Policies.\n')
        print(f'  This wizard will save the output for these pools in the following files:\n')
        print(f'  - {baseRepo}{path_sep}{org}{path_sep}policies{path_sep}compute.yaml')
        print(f'  - {baseRepo}{path_sep}{org}{path_sep}policies{path_sep}storage_policies.yaml')
        print(f'\n-------------------------------------------------------------------------------------------\n')
        #_______________________________________________________________________
        #
        # Configure Boot Order Policy
        #_______________________________________________________________________
        polVars = {}
        secBootList = [False, True]
        if boot_type == 'm2' or boot_type == 'raid1': secBootList = [False, True]
        else: secBootList = [False]
        for i in secBootList:
            # Configure Boot Order Policy
            if i   == False and boot_type == 'm2': name = 'M2-pxe'
            elif i == True  and boot_type == 'm2': name = 'M2'
            elif i == False and boot_type == 'raid1': name = 'Raid1-pxe'
            elif i == True  and boot_type == 'raid1': name = 'Raid1'
            elif boot_type == 'stateless': name = 'pxe'
            polVars['name'] = name
            polVars['boot_mode'] = 'Uefi'
            if not boot_type == 'stateless' and kwargs['tpm_installed'] == True:
                polVars['enable_secure_boot'] = i
            else: polVars['enable_secure_boot'] = False
            polVars['boot_devices'] = [{
                'device_name':'KVM-DVD',
                'device_type':'virtual_media',
                'object_type':'boot.VirtualMedia',
                'subtype':'kvm-mapped-dvd'
            }]
            if boot_type == 'm2':
                polVars['boot_devices'].append[{
                    'device_name':'M2',
                    'device_type':'local_disk',
                    'enabled':True,
                    'object_type':'boot.LocalDisk',
                    'slot':'MSTOR-RAID'
                }]
            if boot_type == 'raid1':
                polVars['boot_devices'].append[{
                    'device_name':'MRAID',
                    'device_type':'local_disk',
                    'enabled':True,
                    'object_type':'boot.LocalDisk',
                    'slot':'MRAID'
                }]
            if i == False:
                polVars['boot_devices'].append[{
                    'device_name':'PXE',
                    'device_type':'pxe_boot',
                    'enabled':True,
                    'interface_name':'mgmt-a',
                    'interface_source':'name',
                    'ip_type':'IPv4',
                    'object_type':'boot.Pxe',
                    'slot':'MLOM'
                }]
            # Add Policy Variables to immDict
            kwargs['class_path'] = 'intersight,policies,boot'
            kwargs = ezfunctions.ez_append(polVars, **kwargs)

        #_______________________________________________________________________
        #
        # Configure Storage Policy
        #_______________________________________________________________________
        polVars = {}
        if boot_type == 'm2':
            polVars['name'] = 'M2-Raid'
            polVars['m2_configuration'] = {'controller_slot':'MSTOR-RAID-1'}
            polVars['use_jbod_for_vd_creation'] = True
        elif boot_type == 'raid1':
            polVars['name'] = 'Raid1'
            polVars['drive_group'] = [{
                'drive_group_name':'DG1',
                'manual_drive_selection':{'drive_array_spans':[{'slots':'1,2'}]},
                'raid_level':'Raid1',
                'virtual_drives':[{
                    'access_policy':'Default',
                    'boot_drive':True,
                    'disk_cache':'Default',
                    'expand_to_available':True,
                    'read_policy':'Always Read Ahead',
                    'size':10,
                    'stripe_size':'64KiB',
                    'vd_name':'VD1',
                    'write_policy':'Write Back Good BBU'
                }]
            }]
            polVars['unused_disks_state'] = 'No Change'
            polVars['use_jbod_for_vd_creation'] = True
        if boot_type == 'm2' or boot_type == 'raid1':
            # Add Policy Variables to immDict
            kwargs['class_path'] = 'intersight,policies,storage'
            kwargs = ezfunctions.ez_append(polVars, **kwargs)
        return kwargs

    #==============================================
    # UCS Domain and Policies
    #==============================================
    def domain_policies(self, **kwargs):
        args        = kwargs['args']
        baseRepo    = args.dir
        ezData      = kwargs['ezData']
        jsonData    = kwargs['jsonData']
        name_prefix = kwargs['domain_prefix']
        org         = self.org
        path_sep    = kwargs['path_sep']
        kwargs['name_prefix'] = name_prefix

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  The Quick Deployment Module - Domain Policies, will configure pools for a UCS Domain ')
            print(f'  Profile.\n')
            print(f'  This wizard will save the output for these pools in the following files:\n')
            print(f'  - {baseRepo}{path_sep}{org}{path_sep}policies{path_sep}domain.yaml')
            print(f'  - {baseRepo}{path_sep}{org}{path_sep}policies{path_sep}management.yaml')
            print(f'  - {baseRepo}{path_sep}{org}{path_sep}policies{path_sep}port.yaml')
            print(f'  - {baseRepo}{path_sep}{org}{path_sep}policies{path_sep}switch.yaml')
            print(f'  - {baseRepo}{path_sep}{org}{path_sep}policies{path_sep}vlan.yaml')
            print(f'  - {baseRepo}{path_sep}{org}{path_sep}policies{path_sep}vsan.yaml')
            print(f'  - {baseRepo}{path_sep}{org}{path_sep}profiles{path_sep}chassis.yaml')
            print(f'  - {baseRepo}{path_sep}{org}{path_sep}profiles{path_sep}domain.yaml')
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

                    kwargs['name'] = 'Quick Deployment Module'

                    kwargs['multi_select'] = False
                    jsonVars = jsonData['policy.AbstractProfile']['allOf'][1]['properties']

                    #_______________________________________________________________________
                    #
                    # Prompt User for Domain Name
                    #_______________________________________________________________________
                    kwargs['Description'] = jsonVars['Name']['description']
                    kwargs['varInput'] = 'What is the name for this UCS Domain?'
                    kwargs['varDefault'] = ''
                    kwargs['varName'] = 'UCS Domain Name'
                    kwargs['varRegex'] = jsonVars['Name']['pattern']
                    kwargs['minLength'] = 1
                    kwargs['maxLength'] = 64
                    domain_name = ezfunctions.varStringLoop(**kwargs)

                    #_______________________________________________________________________
                    #
                    # Prompt User for Device Model for Domain
                    #_______________________________________________________________________
                    kwargs['multi_select'] = False
                    jsonVars = jsonData['fabric.PortPolicy']['allOf'][1]['properties']
                    kwargs['var_description'] = jsonVars['DeviceModel']['description']
                    kwargs['jsonVars'] = sorted(jsonVars['DeviceModel']['enum'])
                    kwargs['jsonVars'].remove('unknown')
                    kwargs['defaultVar'] = jsonVars['DeviceModel']['default']
                    kwargs['varType'] = 'Device Model'
                    device_model = ezfunctions.variablesFromAPI(**kwargs)
                    kwargs['device_model'] = device_model

                    #_______________________________________________________________________
                    #
                    # Prompt User for FI Serial Numbers
                    #_______________________________________________________________________
                    serials = ezfunctions.ucs_domain_serials(**kwargs)

                    #_______________________________________________________________________
                    #
                    # Prompt User for VLANs for Domain
                    #_______________________________________________________________________
                    valid = False
                    while valid == False:
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        print(f'  IMPORTANT NOTE: The FCoE VLAN will be assigned based on the VSAN Identifier.')
                        print(f'                  Be sure to exclude the VSAN for Fabric A and B from the VLAN Pool.')
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        VlanList,vlanListExpanded = ezfunctions.vlan_pool()
                        
                        nativeVlan = input('Do you want to configure one of these VLANs as the Native VLAN?  [press enter to skip]: ')
                        if nativeVlan == '': valid = True
                        else:
                            native_count = 0
                            for vlan in vlanListExpanded:
                                if int(nativeVlan) == int(vlan): native_count = 1
                            if not native_count == 1:
                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                print(f'  Error!! The Native VLAN "{nativeVlan}" was not in the VLAN Policy List.')
                                print(f'  VLAN Policy List is: "{VlanList}"')
                                print(f'\n-------------------------------------------------------------------------------------------\n')
                            else: valid = True

                    #_______________________________________________________________________
                    #
                    # Configure Multicast Policy
                    #_______________________________________________________________________
                    polVars = {'name':'mcast'}

                    # Add Policy Variables to immDict
                    kwargs['class_path'] = 'intersight,policies,multicast'
                    kwargs = ezfunctions.ez_append(polVars, **kwargs)

                    #_______________________________________________________________________
                    #
                    # Configure VLAN Policy
                    #_______________________________________________________________________
                    polVars = {'name': org}
                    vlan_list_expanded = ezfunctions.vlan_list_full(VlanList)
                    if not nativeVlan == '':
                        if int(nativeVlan) in vlan_list_expanded:
                            vlan_list_expanded.remove(int(nativeVlan))
                    elif nativeVlan == '' and 1 in vlan_list_expanded:
                        nativeVlan == 1
                        vlan_list_expanded.remove(1)

                    # Prepare Values to Return to main module
                    kwargs['vlan_list_expanded'] = vlan_list_expanded
                    kwargs["vlan_list"] = ezfunctions.vlan_list_format(vlan_list_expanded)

                    polVars["vlans"] = []
                    if not nativeVlan == '':
                        polVars["vlans"].append({
                            'auto_allow_on_uplinks':True,
                            'multicast_policy':'mcast',
                            'name':'default',
                            'native_vlan':True,
                            'vlan_list':kwargs["native_vlan"]
                        })
                    polVars["vlans"].append({
                        'multicast_policy':'mcast',
                        'name':org,
                        'vlan_list':kwargs["vlan_list"]
                    })

                    # Add Policy Variables to immDict
                    kwargs['class_path'] = 'intersight,policies,vlan'
                    kwargs = ezfunctions.ez_append(polVars, **kwargs)


                    #_______________________________________________________________________
                    #
                    # Configure Flow Control Policy
                    #_______________________________________________________________________
                    polVars = {'name': 'flow_ctrl'}

                    # Add Policy Variables to immDict
                    kwargs['class_path'] = 'intersight,policies,flow_control'
                    kwargs = ezfunctions.ez_append(polVars, **kwargs)

                    #_______________________________________________________________________
                    #
                    # Configure Link Aggregation Policy
                    #_______________________________________________________________________
                    polVars = {'name': 'link_agg'}

                    # Add Policy Variables to immDict
                    kwargs['class_path'] = 'intersight,policies,link_aggregation'
                    kwargs = ezfunctions.ez_append(polVars, **kwargs)

                    #_______________________________________________________________________
                    #
                    # Configure Link Control Policy
                    #_______________________________________________________________________
                    polVars = {'name': 'link_ctrl'}

                    # Add Policy Variables to immDict
                    kwargs['class_path'] = 'intersight,policies,link_control'
                    kwargs = ezfunctions.ez_append(polVars, **kwargs)

                    #_______________________________________________________________________
                    #
                    # Determine if Fibre-Channel will be Utilized
                    #_______________________________________________________________________
                    kwargs = p2.port_modes_fc(**kwargs)

                    # If Unified Ports Exist Configure VSAN Policies
                    if len(kwargs['fc_converted_ports']) > 0:
                        # Obtain the VSAN for Fabric A/B
                        fabrics = ['a', 'b']
                        for x in fabrics:
                            valid = False
                            while valid == False:
                                if loop_count % 2 == 0:
                                    vsan_id = input(f"Enter the VSAN id to add to {org} Fabric {x.upper()}. [100]: ")
                                else: vsan_id = input(f"Enter the VSAN id to add to {org} Fabric {x.upper()}. [200]: ")
                                if loop_count % 2 == 0 and vsan_id == '': vsan_id = 100
                                elif vsan_id == '': vsan_id = 200
                                if re.search(r'[0-9]{1,4}', str(vsan_id)):
                                    valid_count = 0
                                    for y in kwargs['vlan_list_expanded']:
                                        if int(y) == int(vsan_id):
                                            valid_count += 1
                                            continue
                                    if valid_count == 0:
                                        kwargs[f"vsan_id_{x}"] = vsan_id
                                        valid_vlan = validating.number_in_range('VSAN ID', vsan_id, 1, 4094)
                                        if valid_vlan == True:
                                            loop_count += 1
                                            valid = True
                                    else:
                                        print(f'\n-------------------------------------------------------------------------------------------\n')
                                        print(f'  Invalid VSAN!  The FCoE VLAN {x.upper()} must not be assigned to the Domain VLAN Pool.')
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
                        polVars = {}
                        # Configure VSAN Policy
                        for x in fabrics:
                            polVars['name'] = f'vsan-{kwargs[f"vsan_id_{x}"]}'
                            polVars['vsans'] = [{
                                'fcoe_vlan_id':kwargs[f"vsan_id_{x}"],
                                'name':f'vsan-{x}',
                                'vsan_id':kwargs[f"vsan_id_{x}"]
                            }]

                            # Add Policy Variables to immDict
                            kwargs['class_path'] = 'intersight,policies,vsan'
                            kwargs = ezfunctions.ez_append(polVars, **kwargs)

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  IMPORTANT NOTE: If you want to assign one of the VLANs from the Pool as the Native VLAN')
                    print(f'                  for the Port-Channel assign that here.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid = False
                    while valid == False:
                        nativeVlan = input('What is the Native VLAN for the Ethernet Port-Channel?  [press enter to skip]: ')
                        if nativeVlan == '': valid = True
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
                            else: valid = True

                    #_______________________________________________________________________
                    #
                    # Configure Ethernet Network Group Policy
                    #_______________________________________________________________________
                    polVars = {}
                    name = f'{domain_name}-uplink'
                    polVars['name'] = name
                    polVars['allowed_vlans'] = VlanList
                    if not nativeVlan == '':
                        polVars['native_vlan'] = nativeVlan
                    else:
                        polVars['native_vlan'] = ''
                        polVars.pop('native_vlan')

                    # Add Policy Variables to immDict
                    kwargs['class_path'] = 'intersight,policies,ethernet_network_group'
                    kwargs = ezfunctions.ez_append(polVars, **kwargs)

                    #_______________________________________________________________________
                    #
                    # Configure Ethernet Uplink Port-Channels
                    #_______________________________________________________________________
                    kwargs['port_type'] = 'Ethernet Uplink Port-Channel'
                    kwargs = p2.port_list_eth(**kwargs)
                    kwargs['port_channel_ethernet_uplinks'] = kwargs['portDict']

                    kwargs['fc_ports_in_use'] = []
                    if len(kwargs['fc_converted_ports']) > 0:
                        #_______________________________________________________________________
                        #
                        # Configure Fibre-Channel Uplink Port-Channels
                        #_______________________________________________________________________
                        kwargs['portDict'] = []
                        kwargs['port_type'] = 'Fibre-Channel Port-Channel'
                        kwargs = p2.port_list_fc(**kwargs)
                        kwargs['port_channel_fc_uplinks'] = kwargs['portDict']

                    #_______________________________________________________________________
                    #
                    # Configure Server Ports
                    #_______________________________________________________________________
                    kwargs['portDict'] = []
                    kwargs['port_type'] = 'Server Ports'
                    kwargs = p2.port_list_eth(**kwargs)
                    kwargs['port_role_servers'] = kwargs['portDict']

                    kwargs['port_policy'] = {
                        'names': [f'{domain_name}-a', f'{domain_name}-b'],
                        'port_channel_ethernet_uplinks': kwargs['port_channel_ethernet_uplinks'],
                        'port_role_servers': kwargs['port_role_servers'],
                    }
                    if len(kwargs['fc_converted_ports']) > 0:
                        kwargs['port_policy'].update({
                            'port_channel_fc_uplinks': kwargs['port_channel_fc_uplinks'],
                            'port_modes': kwargs['port_modes'],
                        })

                    # System MTU for System QoS Policy
                    kwargs['Description'] = 'This option will set the MTU to 9216 if answer is "Y" or 1500 if answer is "N".'
                    kwargs['varInput'] = f'Do you want to enable Jumbo MTU?  Enter "Y" or "N"'
                    kwargs['varDefault'] = 'Y'
                    kwargs['varName'] = 'MTU'
                    answer = ezfunctions.varBoolLoop(**kwargs)
                    if answer == True: mtu = 9216
                    else: mtu = 1500

                    # NTP Servers
                    primary_ntp = ezfunctions.ntp_primary()
                    alternate_ntp = ezfunctions.ntp_alternate()

                    ntp_servers = [primary_ntp]
                    if not alternate_ntp == '': ntp_servers.append(alternate_ntp)

                    # Timezone
                    polVars['multi_select'] = False
                    jsonVars = jsonData['appliance.SystemInfo']['allOf'][1]['properties']['TimeZone']['enum']
                    tz_regions = []
                    for i in jsonVars:
                        tz_region = i.split('/')[0]
                        if not tz_region in tz_regions: tz_regions.append(tz_region)
                    tz_regions = sorted(tz_regions)
                    kwargs['var_description'] = 'Timezone Regions...'
                    kwargs['jsonVars'] = tz_regions
                    kwargs['defaultVar'] = 'America'
                    kwargs['varType'] = 'Time Region'
                    time_region = ezfunctions.variablesFromAPI(**kwargs)

                    region_tzs = []
                    for item in jsonVars:
                        if time_region in item: region_tzs.append(item)

                    kwargs['var_description'] = 'Region Timezones...'
                    kwargs['jsonVars'] = sorted(region_tzs)
                    kwargs['defaultVar'] = ''
                    kwargs['varType'] = 'Region Timezones'
                    timezone = ezfunctions.variablesFromAPI(**kwargs)

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  UCS Domain Name: {domain_name}')
                    print(f'  Device Model: {device_model}')
                    print(f'  Serials: {serials}')
                    print(f'  Port Policy:')
                    print(textwrap.indent(yaml.dump(kwargs['port_policy'], Dumper=MyDumper, default_flow_style=False
                    ), " "*4, predicate=None))
                    print(f'  System MTU: {mtu}')
                    print(f'  NTP Variables:')
                    print(textwrap.indent(yaml.dump(ntp_servers, Dumper=MyDumper, default_flow_style=False
                    ), " "*3, predicate=None))
                    print(f'    timezone: {timezone}')
                    print(f'  VLAN Pool: {VlanList}')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
                        if confirm_policy == 'Y' or confirm_policy == '':

                            #_______________________________________________________________________
                            #
                            # Configure Sytem QoS Settings
                            #_______________________________________________________________________
                            polVars = {}
                            polVars['name'] = 'system-qos'
                            kwargs['Platinum'] = {
                                'bandwidth_percent':20, 'cos':5, 'mtu':mtu, 'multicast_optimize':False,
                                'packet_drop':False, 'priority':'Platinum', 'state':'Enabled', 'weight':10,
                            }
                            kwargs['Gold'] = {
                                'bandwidth_percent':18, 'cos':4, 'mtu':mtu, 'multicast_optimize':False,
                                'packet_drop':True, 'priority':'Gold', 'state':'Enabled', 'weight':9,
                            }
                            kwargs['FC'] = {
                                'bandwidth_percent':20, 'cos':3, 'mtu':2240, 'multicast_optimize':False,
                                'packet_drop':False, 'priority':'FC', 'state':'Enabled', 'weight':10,
                            }
                            kwargs['Silver'] = {
                                'bandwidth_percent':18, 'cos':2, 'mtu':mtu, 'multicast_optimize':False,
                                'packet_drop':True, 'priority':'Silver', 'state':'Enabled', 'weight':8,
                            }
                            kwargs['Bronze'] = {
                                'bandwidth_percent':14, 'cos':1, 'mtu':mtu, 'multicast_optimize':False,
                                'packet_drop':True, 'priority':'Bronze', 'state':'Enabled', 'weight':7,
                            }
                            kwargs['Best Effort'] = {
                                'bandwidth_percent':10, 'cos':255, 'mtu':mtu, 'multicast_optimize':False,
                                'packet_drop':True, 'priority':'Best Effort', 'state':'Enabled', 'weight':5,
                            }

                            polVars['classes'] = []
                            priorities = ['Platinum', 'Gold', 'FC', 'Silver', 'Bronze', 'Best Effort']

                            for priority in priorities:
                                polVars['classes'].append(kwargs[priority])

                            # Add Policy Variables to immDict
                            kwargs['class_path'] = 'intersight,policies,system_qos'
                            kwargs = ezfunctions.ez_append(polVars, **kwargs)

                            #_______________________________________________________________________
                            #
                            # Configure Network Connectivity Policy
                            #_______________________________________________________________________
                            polVars = {}
                            polVars['name'] = f'dns'
                            polVars['dns_servers_v4'] = [kwargs['primary_dns']]
                            if not kwargs['secondary_dns'] == '':
                                polVars['dns_servers_v4'].append(kwargs['secondary_dns'])

                            # Add Policy Variables to immDict
                            kwargs['class_path'] = 'intersight,policies,network_connectivity'
                            kwargs = ezfunctions.ez_append(polVars, **kwargs)

                            #_______________________________________________________________________
                            #
                            # Configure NTP Policy
                            #_______________________________________________________________________
                            polVars = {}
                            polVars['name'] = f'ntp'
                            polVars['ntp_servers'] = ntp_servers
                            polVars['timezone'] = timezone

                            # Add Policy Variables to immDict
                            kwargs['class_path'] = 'intersight,policies,ntp'
                            kwargs = ezfunctions.ez_append(polVars, **kwargs)

                            #_______________________________________________________________________
                            #
                            # Configure Switch Control Policy
                            #_______________________________________________________________________
                            polVars = {}
                            polVars['name'] = f'sw_ctrl'
                            polVars['vlan_port_count_optimization'] = False

                            # Add Policy Variables to immDict
                            kwargs['class_path'] = 'intersight,policies,switch_control'
                            kwargs = ezfunctions.ez_append(polVars, **kwargs)

                            #_______________________________________________________________________
                            #
                            # Configure Port Policy
                            #_______________________________________________________________________
                            polVars = kwargs['port_policy']

                            # Add Policy Variables to immDict
                            kwargs['class_path'] = 'intersight,policies,port'
                            kwargs = ezfunctions.ez_append(polVars, **kwargs)

                            #_______________________________________________________________________
                            #
                            # Configure UCS Chassis Profile
                            #_______________________________________________________________________
                            kwargs["Description"] = f'Number of Chassis attached to {domain_name}.'
                            kwargs["varInput"] = f'Enter the Number of Chassis attached to {domain_name}:'
                            kwargs["varDefault"] = 1
                            kwargs["varName"] = 'Chassis Count'
                            kwargs["minNum"] = 1
                            kwargs["maxNum"] = 20
                            chassis_count = ezfunctions.varNumberLoop(**kwargs)

                            chassis_models = ['5108', '9508']
                            chassis_dict = {}
                            imc_policy = kwargs['immDict']['orgs'][org]['intersight']['pools']['ip'][0]['name']
                            for i in chassis_models:
                                chassis_dict.update({
                                    i: {
                                        'imc_access_policy':imc_policy, 'names':[], 'power_policy':i,
                                        'snmp_policy':'snmp', 'thermal_policy':i,
                                    }
                                })
                            rangex = int(chassis_count) + 1
                            for x in range(1,rangex):
                                # Chassis Model
                                kwargs["multi_select"] = False
                                jsonVars = ezData['ezimm']['allOf'][1]['properties']['policies']['thermal.Policy']
                                kwargs["var_description"] = jsonVars['chassisType']['description']
                                kwargs["jsonVars"] = sorted(jsonVars['chassisType']['enum'])
                                kwargs["defaultVar"] = jsonVars['chassisType']['default']
                                kwargs["varType"] = 'Chassis Model'
                                chassis_model = ezfunctions.variablesFromAPI(**kwargs)

                                # Obtain Chassis Serial Number or Skip
                                kwargs["Description"] = 'Serial Number of the Chassis to assign to the Profile.'
                                kwargs["varDefault"] = ''
                                kwargs["varInput"] = f'What is the Serial Number of Chassis {x}? [press enter to skip]:'
                                kwargs["varName"] = 'Serial Number'
                                kwargs["varRegex"] = '^[A-Z]{3}[2-3][\\d]([0][1-9]|[1-4][0-9]|[5][1-3])[\\dA-Z]{4}$'
                                kwargs["minLength"] = 11
                                kwargs["maxLength"] = 11
                                serial_number = ezfunctions.varStringLoop(**kwargs)
                                if serial_number == '': serial_number = 'unknown'
                                chassis_dict[f'{chassis_model}']['names'].append([f'{domain_name}-{x}', serial_number])
                            
                            # Add Policy Variables to immDict
                            for i in chassis_models:
                                if len(chassis_dict[i]['names']) > 0:
                                    polVars = chassis_dict[i]
                                    kwargs['class_path'] = 'intersight,profiles,chassis'
                                    kwargs = ezfunctions.ez_append(polVars, **kwargs)

                            #_______________________________________________________________________
                            #
                            # Configure UCS Domain Profile
                            #_______________________________________________________________________
                            polVars = {}
                            polVars['name'] = domain_name
                            polVars['action'] = 'No-op'
                            polVars['network_connectivity_policy'] = f'dns'
                            polVars['ntp_policy'] = f'ntp'
                            polVars['port_policies'] = [f'{domain_name}-a', f'{domain_name}-b']
                            polVars['snmp_policy'] = f'snmp-domain'
                            polVars['switch_control_policy'] = 'sw_ctrl'
                            polVars['syslog_policy'] = f'syslog-domain'
                            polVars['system_qos_policy'] = 'system-qos'
                            polVars['vlan_policies'] = [org]
                            if len(kwargs['fc_converted_ports']) > 0:
                                polVars['vsan_policies'] = [f'vsan-{kwargs["vsan_id_a"]}', f'vsan-{kwargs["vsan_id_b"]}']

                            # Add Policy Variables to immDict
                            kwargs['class_path'] = 'intersight,profiles,domain'
                            kwargs = ezfunctions.ez_append(polVars, **kwargs)

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
            kwargs['Config'] = True
        elif configure == 'N':
            kwargs['Config'] = False
        return kwargs

    #==============================================
    # LAN and SAN Policies
    #==============================================
    def lan_san_policies(self, **kwargs):
        args = kwargs['args']
        baseRepo = args.dir
        ezData = kwargs['ezData']
        fc_ports_in_use = kwargs['fc_ports_in_use']
        jsonData = kwargs['jsonData']
        org = self.org
        path_sep = kwargs['path_sep']
        if kwargs['mtu'] > 8999:
            mtu = 9000
        else: mtu = 1500
        vlanListExpanded = kwargs['vlanListExpanded']

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  The Quick Deployment Module - Network Configuration, will configure policies for the')
            print(f'  Network Configuration of a UCS Server Profile connected to an IMM Domain.\n')
            print(f'  This wizard will save the output for these pools in the following files:\n')
            print(f'  - {baseRepo}{path_sep}{org}{path_sep}{self.type}/ethernet.yaml')
            print(f'  - {baseRepo}{path_sep}{org}{path_sep}{self.type}/fibre_channel.yaml')
            print(f'  - {baseRepo}{path_sep}{org}{path_sep}{self.type}/lan_connectivity.yaml')
            print(f'  - {baseRepo}{path_sep}{org}{path_sep}{self.type}/san_connectivity.yaml')
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

                    vlan_policy = kwargs['vlan_policy']
                    vlan_list = kwargs['vlans']
                    polVars['vsan_A'] = kwargs['vsan_a']
                    polVars['vsan_B'] = kwargs['vsan_b']
                    fc_ports_in_use = kwargs['fc_ports']
                    vlan_policy_list = ezfunctions.vlan_list_full(vlan_list)

                    polVars['multi_select'] = False
                    jsonVars = jsonVars = ezData['policies']['fabric.EthNetworkControlPolicy']

                    # Neighbor Discovery Protocol
                    kwargs['var_description'] = jsonVars['discoveryProtocol']['description']
                    kwargs['jsonVars'] = sorted(jsonVars['discoveryProtocol']['enum'])
                    kwargs['defaultVar'] = jsonVars['discoveryProtocol']['default']
                    kwargs['varType'] = 'Neighbor Discovery Protocol'
                    neighbor_discovery = ezfunctions.variablesFromAPI(**kwargs)

                    # Management VLAN
                    valid = False
                    while valid == False:
                        kwargs['Description'] = 'LAN Connectivity Policy vNICs - MGMT VLAN Identifier'
                        kwargs['varInput'] = 'Enter the VLAN ID for MGMT:'
                        kwargs['varDefault'] = 1
                        kwargs['varName'] = 'Management VLAN ID'
                        kwargs['minNum'] = 1
                        kwargs['maxNum'] = 4094
                        mgmt_vlan = ezfunctions.varNumberLoop(**kwargs)
                        valid = ezfunctions.validate_vlan_in_policy(vlan_policy_list, mgmt_vlan)

                    # vMotion VLAN
                    valid = False
                    while valid == False:
                        kwargs['Description'] = 'LAN Connectivity Policy vNICs - vMotion VLAN Identifier'
                        kwargs['varInput'] = 'Enter the VLAN ID for vMotion:'
                        kwargs['varDefault'] = 2
                        kwargs['varName'] = 'Management VLAN ID'
                        kwargs['minNum'] = 1
                        kwargs['maxNum'] = 4094
                        migration_vlan = ezfunctions.varNumberLoop(**kwargs)
                        valid = ezfunctions.validate_vlan_in_policy(vlan_policy_list, migration_vlan)

                    # Storage VLAN
                    valid = False
                    while valid == False:
                        kwargs['Description'] = 'LAN Connectivity Policy vNICs - Storage VLAN Identifier'
                        kwargs['varInput'] = 'Enter the VLAN ID for Storage:'
                        kwargs['varDefault'] = 3
                        kwargs['varName'] = 'Storage VLAN ID'
                        kwargs['minNum'] = 1
                        kwargs['maxNum'] = 4094
                        storage_vlan = ezfunctions.varNumberLoop(**kwargs)
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
                                if valid_vlan == False: continue
                                else:
                                    vlan_count = 0
                                    for vlans in vlan_policy_list:
                                        if int(vlan) == int(vlans):
                                            vlan_count += 1
                                            break
                                    if vlan_count == 0: vlans_not_in_domain_policy.append(vlan)

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

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  Network Configuration Variables:')
                    print(f'    MGMT VLAN     = {mgmt_vlan}')
                    print(f'    Migration VLAN  = {migration_vlan}')
                    print(f'    Storage VLAN  = {storage_vlan}')
                    print(f'    Data VLANs    = "{VlanList}"')
                    if len(fc_ports_in_use) > 0:
                        print(f'    VSAN Fabric A = {kwargs["vsan_a"]}')
                        print(f'    VSAN Fabric B = {kwargs["vsan_b"]}')
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
                            polVars = {}
                            name = 'VMware'
                            polVars['name'] = name
                            polVars['adapter_template'] = 'VMware'

                            # Add Policy Variables to immDict
                            kwargs['class_path'] = 'intersight,policies,ethernet_adapter'
                            kwargs = ezfunctions.ez_append(polVars, **kwargs)

                            #_______________________________________________________________________
                            #
                            # Configure Ethernet Network Control Policy
                            #_______________________________________________________________________
                            polVars = {}
                            polVars['name'] = neighbor_discovery
                            polVars['descr'] = f'{name} Ethernet Network Control Policy'
                            polVars['action_on_uplink_fail'] = "linkDown"
                            if neighbor_discovery == 'CDP':
                                polVars['cdp_enable'] = True
                            else:
                                polVars['cdp_enable'] = False
                            if neighbor_discovery == 'LLDP':
                                polVars['lldp_receive_enable'] = True
                                polVars['lldp_transmit_enable'] = True
                            else:
                                polVars['lldp_receive_enable'] = False
                                polVars['lldp_transmit_enable'] = False
                            polVars['mac_register_mode'] = "nativeVlanOnly"
                            polVars['mac_security_forge'] = "allow"

                            # Add Policy Variables to immDict
                            kwargs['class_path'] = 'intersight,policies,ethernet_network_control'
                            kwargs = ezfunctions.ez_append(polVars, **kwargs)

                            #_______________________________________________________________________
                            #
                            # Configure Ethernet Network Group Policy
                            #_______________________________________________________________________
                            polVars = {}
                            names = [kwargs['vlan_policy'], 'mgmt', 'migration', 'storage', 'dvs']
                            for x in names:
                                if x == kwargs['vlan_policy']:
                                    allowed_vlans = kwargs['vlans']
                                    native_vlan = kwargs['native_vlan']
                                elif x == 'mgmt':
                                    allowed_vlans = mgmt_vlan
                                    native_vlan = mgmt_vlan
                                elif x == 'migration':
                                    allowed_vlans = migration_vlan
                                    native_vlan = migration_vlan
                                elif x == 'storage':
                                    allowed_vlans = storage_vlan
                                    native_vlan = storage_vlan
                                elif x == 'dvs':
                                    allowed_vlans = VlanList
                                    native_vlan = nativeVlan
                                name = x
                                polVars['name'] = name
                                polVars['allowed_vlans'] = allowed_vlans
                                if not native_vlan == '':
                                    polVars['native_vlan'] = native_vlan
                                else:
                                    polVars['native_vlan'] = ''
                                    polVars.pop('native_vlan')

                                # Add Policy Variables to immDict
                                kwargs['class_path'] = 'intersight,policies,ethernet_network_group'
                                kwargs = ezfunctions.ez_append(polVars, **kwargs)

                            #_______________________________________________________________________
                            #
                            # Configure Ethernet QoS Policy
                            #_______________________________________________________________________
                            polVars = {}
                            names = ['Bronze', 'Gold', 'Platinum', 'Silver']
                            for x in names:
                                name = x
                                polVars['name'] = name
                                polVars['descr'] = f'{name} Ethernet QoS Policy'
                                polVars['allowed_vlans'] = mgmt_vlan
                                polVars['native_vlan'] = mgmt_vlan
                                polVars['burst'] = 1024
                                polVars['enable_trust_host_cos'] = False
                                polVars['priority'] = x
                                polVars['mtu'] = mtu
                                polVars['rate_limit'] = 0

                                # Add Policy Variables to immDict
                                kwargs['class_path'] = 'intersight,policies,ethernet_qos'
                                kwargs = ezfunctions.ez_append(polVars, **kwargs)

                            if len(fc_ports_in_use) > 0:
                                #_______________________________________________________________________
                                #
                                # Configure Fibre-Channel Adapter Policy
                                #_______________________________________________________________________
                                polVars = {}
                                name = 'VMware'
                                polVars['name'] = name
                                polVars['descr'] = f'{name} Fibre-Channel Adapter Policy'
                                polVars['policy_template'] = 'VMware'

                                # Add Policy Variables to immDict
                                kwargs['class_path'] = 'intersight,policies,fibre_channel_adapter'
                                kwargs = ezfunctions.ez_append(polVars, **kwargs)

                                #_______________________________________________________________________
                                #
                                # Configure Fibre-Channel Network Policy
                                #_______________________________________________________________________
                                polVars = {}
                                fabrics = ['a', 'b']
                                for fab in fabrics:
                                    name = f'san-{fab}'
                                    polVars['name'] = name
                                    polVars['default_vlan'] = 0
                                    polVars['vsan_id'] = polVars[f"vsan_{fab}"]

                                    # Add Policy Variables to immDict
                                    kwargs['class_path'] = 'intersight,policies,fibre_channel_network'
                                    kwargs = ezfunctions.ez_append(polVars, **kwargs)

                                #_______________________________________________________________________
                                #
                                # Configure Fibre-Channel QoS Policy
                                #_______________________________________________________________________
                                polVars = {}
                                name = 'fc-qos'
                                polVars['name'] = name
                                polVars['burst'] = 1024
                                polVars['max_data_field_size'] = 2112
                                polVars['rate_limit'] = 0

                                # Add Policy Variables to immDict
                                kwargs['class_path'] = 'intersight,policies,fibre_channel_qos'
                                kwargs = ezfunctions.ez_append(polVars, **kwargs)

                            Order = 0
                            if len(fc_ports_in_use) > 0:
                                #_______________________________________________________________________
                                #
                                # SAN Connectivity Policy
                                #_______________________________________________________________________
                                polVars = {}
                                polVars['name'] = f'{org}-scp'
                                polVars['target_platform'] = "FIAttached"
                                polVars['vhbas'] = [{
                                    'fibre_channel_adapter_policy':'VMware',
                                    'fibre_channel_network_policy':f'san-{fab}',
                                    'fibre_channel_qos_policy':'fc-qos',
                                    'names':['hba-a', 'hba-b'],
                                    'pci_order':[Order, Order + 1],
                                    'wwpn_allocation_type':'POOL',
                                    'wwpn_pools':[f'{org}-a', f'{org}-b']
                                }]
                                polVars['wwnn_allocation_type'] = "POOL"
                                polVars['wwnn_pool'] = org
                                Order += 2

                                # Add Policy Variables to immDict
                                kwargs['class_path'] = 'intersight,policies,san_connectivity'
                                kwargs = ezfunctions.ez_append(polVars, **kwargs)

                            #_______________________________________________________________________
                            #
                            # LAN Connectivity Policy
                            #_______________________________________________________________________
                            polVars = {}
                            polVars['name'] = 'vmware-lcp'
                            polVars['target_platform'] = "FIAttached"
                            polVars['vnics'] = []
                            names = ['mgmt_Silver', 'migration_Bronze', 'storage_Platinum', 'dvs_Gold']
                            for nam in names:
                                vname = nam.split('_')[0]
                                qos = nam.split('_')[1]
                                vnic = {
                                    'ethernet_adapter_policy':'VMware',
                                    'ethernet_network_control_policy':neighbor_discovery,
                                    'ethernet_network_group_policy':vname,
                                    'ethernet_qos_policy':qos,
                                    'mac_address_pools':[f'{org}-a',f'{org}-b',],
                                    'names':[f'{vname}-a',f'{vname}-b',],
                                    'pci_order':[Order, Order + 1],
                                }
                                polVars['vnics'].append(vnic)
                                Order += 2

                            # Add Policy Variables to immDict
                            kwargs['class_path'] = 'intersight,policies,lan_connectivity'
                            kwargs = ezfunctions.ez_append(polVars, **kwargs)


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
    def pools(self, **kwargs):
        args = kwargs['args']
        baseRepo = args.dir
        org = self.org
        ezData = kwargs['ezData']
        jsonData = kwargs['jsonData']
        path_sep = kwargs['path_sep']
        polVars = {}

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  The Quick Deployment Module - Pools, will configure pools for a UCS Server Profile')
            print(f'  connected to an IMM Domain.\n')
            print(f'  This wizard will save the output for these pools in the following files:\n')
            print(f'  - {baseRepo}{path_sep}{org}{path_sep}{self.type}/pools.yaml')
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
                    print(f'  The following pools will be configured with the prefix value:')
                    print(f'    * Note: (Policy maximum 1000 addresses per pool in Intersight will be assigned):')
                    print(f'    * MAC Pools')
                    print(f'      - dvs-a:           00:25:B5:[prefix]:G0:00, size: 1000')
                    print(f'      - dvs-b:           00:25:B5:[prefix]:H0:00, size: 1000')
                    print(f'      - mgmt-a:          00:25:B5:[prefix]:A0:00, size: 1000')
                    print(f'      - mgmt-b:          00:25:B5:[prefix]:B0:00, size: 1000')
                    print(f'      - migration-a:     00:25:B5:[prefix]:C0:00, size: 1000')
                    print(f'      - migration-b:     00:25:B5:[prefix]:D0:00, size: 1000')
                    print(f'      - storage-a:       00:25:B5:[prefix]:E0:00, size: 1000')
                    print(f'      - storage-b:       00:25:B5:[prefix]:F0:00, size: 1000')
                    print(f'    * UUID Pool')
                    print(f'      - {org}:        000025B5-[prefix]00-0000, size: 1000')
                    print(f'    * WWNN Pool')
                    print(f'      - {org}:   20:00:00:25:B5:[prefix]:00:00, size: 1000')
                    print(f'    * WWPN Pools')
                    print(f'      - {org}-a: 20:00:00:25:B5:[prefix]:A0:00, size: 1000')
                    print(f'      - {org}-b: 20:00:00:25:B5:[prefix]:B0:00, size: 1000')
                    print(f'\n-------------------------------------------------------------------------------------------\n')

                    kwargs['multi_select'] = False
                    jsonVars = jsonData['ippool.IpV4Config']['allOf'][1]['properties']
                    kwargs['Description'] = jsonVars['Gateway']['description']
                    kwargs['varInput'] = 'What is the Gateway for the KVM IP Pool? [198.18.0.1]:'
                    kwargs['varDefault'] = '198.18.0.1'
                    kwargs['varName'] = 'Gateway'
                    kwargs['varRegex'] = jsonVars['Gateway']['pattern']
                    kwargs['minLength'] = 7
                    kwargs['maxLength'] = 15
                    gateway = ezfunctions.varStringLoop(**kwargs)

                    kwargs['Description'] = jsonVars['Netmask']['description']
                    kwargs['varInput'] = 'What is the Netmask for the KVM IP Pool? [255.255.255.0]:'
                    kwargs['varDefault'] = '255.255.255.0'
                    kwargs['varName'] = 'Netmask'
                    kwargs['varRegex'] = jsonVars['Netmask']['pattern']
                    kwargs['minLength'] = 7
                    kwargs['maxLength'] = 15
                    netmask = ezfunctions.varStringLoop(**kwargs)

                    kwargs['Description'] = jsonVars['PrimaryDns']['description']
                    kwargs['varInput'] = 'What is the Primary Dns for the KVM IP Pool? [208.67.220.220]:'
                    kwargs['varDefault'] = '208.67.220.220'
                    kwargs['varName'] = 'Primary Dns'
                    kwargs['varRegex'] = jsonVars['PrimaryDns']['pattern']
                    kwargs['minLength'] = 7
                    kwargs['maxLength'] = 15
                    primary_dns = ezfunctions.varStringLoop(**kwargs)

                    kwargs['Description'] = jsonVars['SecondaryDns']['description']
                    kwargs['varInput'] = 'What is the Secondary Dns for the KVM IP Pool? [press enter to skip]:'
                    kwargs['varDefault'] = ''
                    kwargs['varName'] = 'Secondary Dns'
                    kwargs['varRegex'] = jsonVars['SecondaryDns']['pattern']
                    kwargs['minLength'] = 7
                    kwargs['maxLength'] = 15
                    secondary_dns = ezfunctions.varStringLoop(**kwargs)

                    jsonVars = jsonData['ippool.IpV4Block']['allOf'][1]['properties']
                    kwargs['Description'] = jsonVars['From']['description']
                    kwargs['varInput'] = 'What is the First IP Address for the KVM IP Pool? [198.18.0.10]:'
                    kwargs['varDefault'] = '198.18.0.10'
                    kwargs['varName'] = 'Beginning IP Address'
                    kwargs['varRegex'] = jsonVars['From']['pattern']
                    kwargs['minLength'] = 7
                    kwargs['maxLength'] = 15
                    pool_from = ezfunctions.varStringLoop(**kwargs)

                    kwargs['Description'] = jsonVars['To']['description']
                    kwargs['varInput'] = 'What is the Last IP Address for the KVM IP Pool? [198.18.0.254]:'
                    kwargs['varDefault'] = '198.18.0.254'
                    kwargs['varName'] = 'Ending IP Address'
                    kwargs['varRegex'] = jsonVars['To']['pattern']
                    kwargs['minLength'] = 7
                    kwargs['maxLength'] = 15
                    pool_to = ezfunctions.varStringLoop(**kwargs)

                    kwargs['Description'] = 'Prefix to assign to Pools'
                    kwargs['varInput'] = 'What is the 2 Digit (Hex) Prefix to assign to the MAC, UUID, WWNN, and WWPN Pools? [00]:'
                    kwargs['varDefault'] = '00'
                    kwargs['varName'] = 'Pool Prefix'
                    kwargs['varRegex'] = '^[0-9a-zA-Z][0-9a-zA-Z]$'
                    kwargs['minLength'] = 2
                    kwargs['maxLength'] = 2
                    pool_prefix = ezfunctions.varStringLoop(**kwargs)
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

                            name = pool_from
                            polVars['name'] = name
                            pool_size = int(ipaddress.IPv4Address(pool_to)) - int(ipaddress.IPv4Address(pool_from)) + 1
                            polVars['ipv4_blocks'] = [{'from':pool_from, 'size':pool_size}]
                            polVars['ipv4_configuration'] = {
                                'gateway':gateway, 'prefix':netmask,
                                'primary_dns':primary_dns, 'secondary_dns':secondary_dns
                            }
                            kwargs['primary_dns'] = primary_dns
                            kwargs['secondary_dns'] = secondary_dns

                            # Add Policy Variables to immDict
                            kwargs['class_path'] = 'intersight,pools,ip'
                            kwargs = ezfunctions.ez_append(polVars, **kwargs)

                            #_______________________________________________________________________
                            #
                            # Configure MAC Pools
                            #_______________________________________________________________________

                            polVars = {}
                            names = ['dvs', 'mgmt', 'migration', 'storage']
                            fabrics = ['a', 'b']
                            for i in names:
                                for fab in fabrics:
                                    if   i == 'mgmt' and fab == 'a': key_id = 'A'
                                    elif i == 'mgmt' and fab == 'b': key_id = 'B'
                                    elif i == 'migration' and fab == 'a': key_id = 'C'
                                    elif i == 'migration' and fab == 'b': key_id = 'D'
                                    elif i == 'storage' and fab == 'a': key_id = 'E'
                                    elif i == 'storage' and fab == 'b': key_id = 'F'
                                    elif i == 'dvs' and fab == 'a': key_id = '1'
                                    elif i == 'dvs' and fab == 'b': key_id = '2'

                                    name = f'{i}-{fab}'
                                    polVars['name'] = name
                                    pool_from = f'00:25:B5:{pool_prefix}:{key_id}0:00'
                                    polVars['mac_blocks'] = [{'from':pool_from, 'size':1000}]

                                    # Add Policy Variables to immDict
                                    kwargs['class_path'] = 'intersight,pools,mac'
                                    kwargs = ezfunctions.ez_append(polVars, **kwargs)

                            #_______________________________________________________________________
                            #
                            # Configure UUID Pool
                            #_______________________________________________________________________

                            polVars = {}
                            name = org
                            polVars['name'] = name
                            polVars['descr'] = f'{name} UUID Pool'
                            polVars['prefix'] = f'000025B5-{pool_prefix}00-0000'
                            polVars['uuid_blocks'] = [{'from':'0000-000000000000', 'size':1000}]

                            # Add Policy Variables to immDict
                            kwargs['class_path'] = 'intersight,pools,uuid'
                            kwargs = ezfunctions.ez_append(polVars, **kwargs)

                            #_______________________________________________________________________
                            #
                            # Configure WWNN Pool
                            #_______________________________________________________________________

                            polVars = {}
                            name = org
                            polVars['name'] = name
                            pool_from = f'20:00:00:25:B5:{pool_prefix}:00:00'
                            polVars['id_blocks'] = [{'from':pool_from, 'size':1000}]

                            # Add Policy Variables to immDict
                            kwargs['class_path'] = 'intersight,pools,wwnn'
                            kwargs = ezfunctions.ez_append(polVars, **kwargs)

                            #_______________________________________________________________________
                            #
                            # Configure WWPN Pools
                            #_______________________________________________________________________

                            for fab in fabrics:
                                name = f'{org}-{fab}'
                                polVars['name'] = name
                                pool_from = f'20:00:00:25:B5:{pool_prefix}:{fab.upper()}0:00'
                                polVars['id_blocks'] = [{'from':pool_from, 'size':1000,}]

                                # Add Policy Variables to immDict
                                kwargs['class_path'] = 'intersight,pools,wwpn'
                                kwargs = ezfunctions.ez_append(polVars, **kwargs)

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

        return kwargs

    #==============================================
    # Server Policies for Domain and Standalone
    #==============================================
    def server_policies(self, **kwargs):
        args = kwargs['args']
        baseRepo = args.dir
        ezData = kwargs['ezData']
        jsonData = kwargs['jsonData']
        org = self.org
        path_sep = kwargs['path_sep']
        server_type = kwargs['server_type']
        vlan_list = kwargs['vlan_list']

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  The Quick Deployment Module - Pools, will configure pools for a UCS Server Profile')
            print(f'  connected to an IMM Domain.\n')
            print(f'  This wizard will save the output for these pools in the following files:\n')
            print(f'  - {baseRepo}{path_sep}{org}{path_sep}{self.type}/imc_access_policies.yaml')
            print(f'  - {baseRepo}{path_sep}{org}{path_sep}{self.type}/ipmi_over_lan_policies.yaml')
            print(f'  - {baseRepo}{path_sep}{org}{path_sep}{self.type}/local_user_policies.yaml')
            print(f'  - {baseRepo}{path_sep}{org}{path_sep}{self.type}/power_policies.yaml')
            print(f'  - {baseRepo}{path_sep}{org}{path_sep}{self.type}/serial_over_lan_policies.yaml')
            print(f'  - {baseRepo}{path_sep}{org}{path_sep}{self.type}/snmp_policies.yaml')
            print(f'  - {baseRepo}{path_sep}{org}{path_sep}{self.type}/syslog_policies.yaml')
            print(f'  - {baseRepo}{path_sep}{org}{path_sep}{self.type}/thermal_policies.yaml')
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

                    kwargs['name'] = 'Quick Deployment Module'

                    vlan_policy_list = ezfunctions.vlan_list_full(vlan_list)

                    kwargs['multi_select'] = False

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  Now Starting the IMC Access Policy Section.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')

                    #_______________________________________________________________________
                    #
                    # Prompt User for IMC Access Type
                    #_______________________________________________________________________
                    jsonVars = jsonData['access.Policy']['allOf'][1]['properties']
                    kwargs['var_description'] = jsonVars['ConfigurationType']['description']
                    kwargs['jsonVars'] = ['inband', 'out_of_band']
                    kwargs['defaultVar'] = 'inband'
                    kwargs['varType'] = 'IMC Access Type'
                    imcBand = ezfunctions.variablesFromAPI(**kwargs)

                    if imcBand == 'inband':
                        valid = False
                        while valid == False:
                            kwargs['Description'] = 'IMC Access VLAN Identifier'
                            kwargs['varInput'] = 'Enter the VLAN ID for the IMC Access Policy.'
                            kwargs['varDefault'] = 4
                            kwargs['varName'] = 'IMC Access Policy VLAN ID'
                            kwargs['minNum'] = 4
                            kwargs['maxNum'] = 4094
                            inband_vlan_id = ezfunctions.varNumberLoop(**kwargs)
                            if server_type == 'FIAttached':
                                valid = ezfunctions.validate_vlan_in_policy(vlan_policy_list, inband_vlan_id)
                            else:
                                valid = True

                    #_______________________________________________________________________
                    #
                    # Prompt User for IPMI Encryption Key
                    #_______________________________________________________________________
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  Need to obtain the IPMI Key for IPMI over LAN Policy Encryption.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    kwargs['Variable'] = 'ipmi_key'
                    kwargs['ipmi_key'] = ezfunctions.sensitive_var_value(**kwargs)

                    #_______________________________________________________________________
                    #
                    # Prompt User for Local User Policy
                    #_______________________________________________________________________
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  Now Starting the Local User Policy Section.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    kwargs["enforce_strong_password"] = True
                    kwargs['Description'] = '  Local User Configuration.'
                    kwargs['varInput'] = f'Would you like to configure the Local users Policy?'
                    kwargs['varDefault'] = 'Y'
                    kwargs['varName'] = 'Local Users'
                    question = ezfunctions.varBoolLoop(**kwargs)
                    if question == True:
                        kwargs = ezfunctions.local_users_function(**kwargs)

                    #_______________________________________________________________________
                    #
                    # Prompt User for SNMP Policy Parameters
                    #_______________________________________________________________________
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  Now Starting the SNMP Policy Section.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    # Pull in the Policies for SNMP Policies
                    jsonVars = jsonData['snmp.Policy']['allOf'][1]['properties']

                    kwargs['Description'] = jsonVars['SysContact']['description'] + \
                        'Note: Enter a string up to 64 characters, such as an email address or a name and telephone number.'
                    kwargs['varDefault'] = ''
                    kwargs['varInput'] = 'SNMP System Contact:'
                    kwargs['varName'] = 'SNMP System Contact'
                    kwargs['varRegex'] = '.*'
                    kwargs['minLength'] = 1
                    kwargs['maxLength'] = jsonVars['SysContact']['maxLength']
                    kwargs['system_contact'] = ezfunctions.varStringLoop(**kwargs)

                    kwargs['Description'] = jsonVars['SysLocation']['description']
                    kwargs['varDefault'] = ''
                    kwargs['varInput'] = 'What is the Location of the host on which the SNMP agent (server) runs?'
                    kwargs['varName'] = 'SNMP System Location'
                    kwargs['varRegex'] = '.*'
                    kwargs['minLength'] = 1
                    kwargs['maxLength'] = jsonVars['SysLocation']['maxLength']
                    kwargs['system_location'] = ezfunctions.varStringLoop(**kwargs)

                    snmp_loop = False
                    while snmp_loop == False:
                        question = input(f'Would you like to configure an SNMPv3 User?  Enter "Y" or "N" [Y]: ')
                        if question == '' or question == 'Y':
                            kwargs = ezfunctions.snmp_users(**kwargs)
                        elif question == 'N':
                            snmp_loop = True
                        else:
                            print(f'\n------------------------------------------------------\n')
                            print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                            print(f'\n------------------------------------------------------\n')

                    snmp_loop = False
                    if len(kwargs['users']) > 0:
                        while snmp_loop == False:
                            question = input(f'Would you like to configure SNMP Trap Destionations?  Enter "Y" or "N" [Y]: ')
                            if question == '' or question == 'Y':
                                kwargs = ezfunctions.snmp_trap_servers(**kwargs)
                            elif question == 'N':
                                snmp_loop = True
                            else:
                                print(f'\n------------------------------------------------------\n')
                                print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                                print(f'\n------------------------------------------------------\n')
                    #kwargs['trap_destinations'] = snmp_dests

                    #_______________________________________________________________________
                    #
                    # Prompt User for Syslog Policy
                    #_______________________________________________________________________
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  Now Starting the Syslog Policy Section.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    # Syslog Section
                    syslog_loop = False
                    while syslog_loop == False:
                        question = input(f'Do you want to configure Remote Syslog Servers?  Enter "Y" or "N" [Y]: ')
                        if question == '' or question == 'Y':
                            # Syslog Local Logging
                            jsonVars = jsonData['syslog.LocalClientBase']['allOf'][1]['properties']
                            kwargs['var_description'] = jsonVars['MinSeverity']['description']
                            kwargs['jsonVars'] = sorted(jsonVars['MinSeverity']['enum'])
                            kwargs['defaultVar'] = jsonVars['MinSeverity']['default']
                            kwargs['varType'] = 'Syslog Local Minimum Severity'
                            kwargs['min_severity'] = ezfunctions.variablesFromAPI(**kwargs)

                            kwargs['local_logging'] = {'file':{'min_severity':kwargs['min_severity']}}
                            kwargs = ezfunctions.syslog_servers(**kwargs)
                            syslog_loop = True

                        elif question == 'N':
                            kwargs['min_severity'] = 'warning'
                            kwargs['local_logging'] = {'file':{'min_severity':kwargs['min_severity']}}
                            kwargs['remote_clients'] = {'server1':{},'server2':{}}
                            syslog_loop = True
                        else:
                            print(f'\n------------------------------------------------------\n')
                            print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                            print(f'\n------------------------------------------------------\n')

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  Policy Variables:')
                    print(f'    IMC Access Mode  = "{imcBand}"')
                    if imcBand == 'Inband':
                        print(f'    IMC Access VLAN  = {kwargs["inband_vlan_id"]}')
                    if len(kwargs['local_users']) > 0:
                        print(textwrap.indent(yaml.dump(kwargs['local_users'], Dumper=MyDumper, default_flow_style=False
                        ), " "*3, predicate=None))
                    print(f'    System Contact   = "{kwargs["system_contact"]}"')
                    print(f'    System Locaction = "{kwargs["system_location"]}"')
                    print(f'    SNMP Trap Destinations:')
                    if len(kwargs['trap_destinations']) > 0:
                        print(textwrap.indent(yaml.dump({'snmp_traps':kwargs['trap_destinations']
                        }, Dumper=MyDumper, default_flow_style=False), " "*3, predicate=None))
                    print(f'    SNMP Users:')
                    if len(kwargs['users']) > 0:
                        print(textwrap.indent(yaml.dump({'snmp_users':kwargs['trap_destinations']
                        }, Dumper=MyDumper, default_flow_style=False), " "*3, predicate=None))
                    print(f'    Syslog Remote Clients:')
                    print(textwrap.indent(yaml.dump({'remote_clients':kwargs['remote_clients']
                    }, Dumper=MyDumper, default_flow_style=False), " "*3, predicate=None))
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
                        if confirm_policy == 'Y' or confirm_policy == '':

                            #_______________________________________________________________________
                            #
                            # Configure IMC Access Policy
                            #_______________________________________________________________________
                            polVars = {}
                            polVars['name'] = ezData['immDict']['orgs'][org]['intersight']['pools']['ip'][0]['name']
                            polVars[f'{imcBand}_ip_pool'] = ezData['immDict']['orgs'][org]['intersight']['pools']['ip'][0]['name']
                            if imcBand == 'inband':
                                polVars['inband_vlan_id'] = inband_vlan_id

                            # Add Policy Variables to immDict
                            kwargs['class_path'] = 'intersight,policies,imc_access'
                            kwargs = ezfunctions.ez_append(polVars, **kwargs)
                            kwargs['imc_access_policy'] = polVars['name']

                            #_______________________________________________________________________
                            #
                            # Configure IPMI over LAN Policy
                            #_______________________________________________________________________
                            polVars = {}
                            polVars['name'] = f'{org}-ipmi'
                            polVars['enabled'] = True

                            # Add Policy Variables to immDict
                            kwargs['class_path'] = 'intersight,policies,ipmi_over_lan'
                            kwargs = ezfunctions.ez_append(polVars, **kwargs)

                            #_______________________________________________________________________
                            #
                            # Configure Local User Policy
                            #_______________________________________________________________________
                            polVars = {}
                            polVars['name'] = f'{org}-users'
                            polVars['users'] = kwargs['users']

                            # Add Policy Variables to immDict
                            kwargs['class_path'] = 'intersight,policies,local_user'
                            kwargs = ezfunctions.ez_append(polVars, **kwargs)

                            #_______________________________________________________________________
                            #
                            # Configure Power Policy
                            #_______________________________________________________________________
                            polVars = {}
                            names = ['5108', '9508', 'Server']
                            for name in names:
                                polVars['allocated_budget'] = 0
                                polVars['name'] = name
                                if name == 'Server':
                                    polVars['power_restore'] = 'LastState'
                                    
                                elif name == '9508':
                                    polVars['power_allocation'] = 8400

                                polVars['power_redundancy'] = 'Grid'

                                # Add Policy Variables to immDict
                                kwargs['class_path'] = 'intersight,policies,power'
                                kwargs = ezfunctions.ez_append(polVars, **kwargs)

                            #_______________________________________________________________________
                            #
                            # Configure Serial over LAN Policy
                            #_______________________________________________________________________
                            polVars = {}
                            polVars['name'] = 'sol'
                            polVars['descr'] = f'{name} Serial over LAN Policy'
                            polVars['enabled'] = True

                            # Add Policy Variables to immDict
                            kwargs['class_path'] = 'intersight,policies,serial_over_lan'
                            kwargs = ezfunctions.ez_append(polVars, **kwargs)

                            #_______________________________________________________________________
                            #
                            # Configure SNMP Policy
                            #_______________________________________________________________________
                            polVars = {}
                            names = ['snmp', 'snmp-domain']
                            for name in names:
                                polVars['name'] = name
                                polVars['enabled'] = True
                                polVars['system_contact'] = kwargs['system_contact']
                                polVars['system_location'] = kwargs['system_location']
                                polVars['snmp_traps'] = kwargs['snmp_traps']
                                polVars['snmp_users'] = kwargs['snmp_users']

                                # Add Policy Variables to immDict
                                kwargs['class_path'] = 'intersight,policies,snmp'
                                kwargs = ezfunctions.ez_append(polVars, **kwargs)

                            #_______________________________________________________________________
                            #
                            # Configure Syslog Policy
                            #_______________________________________________________________________
                            polVars = {}
                            names = ['syslog', 'syslog-domain']
                            for name in names:
                                polVars['name'] = name
                                polVars['min_severity']   = kwargs['min_severity']
                                polVars['local_logging']  = kwargs['local_logging']
                                polVars['remote_logging'] = kwargs['remote_logging']
                                polVars['remote_clients'] = kwargs['remote_clients']

                                # Add Policy Variables to immDict
                                kwargs['class_path'] = 'intersight,policies,syslog'
                                kwargs = ezfunctions.ez_append(polVars, **kwargs)

                            #_______________________________________________________________________
                            #
                            # Configure Thermal Policy
                            #_______________________________________________________________________
                            polVars = {}
                            names = ['5108', '9508']
                            for name in names:
                                polVars['name'] = name
                                polVars['fan_control_mode'] = 'Balanced'

                                # Add Policy Variables to immDict
                                kwargs['class_path'] = 'intersight,policies,thermal'
                                kwargs = ezfunctions.ez_append(polVars, **kwargs)

                            #_______________________________________________________________________
                            #
                            # Configure Virtual KVM Policy
                            #_______________________________________________________________________
                            polVars = {}
                            polVars['name'] = 'vkvm'
                            polVars['allow_tunneled_kvm'] = False

                            # Add Policy Variables to immDict
                            kwargs['class_path'] = 'intersight,policies,virtual_kvm'
                            kwargs = ezfunctions.ez_append(polVars, **kwargs)

                            #_______________________________________________________________________
                            #
                            # Configure Virtual Media Policy
                            #_______________________________________________________________________
                            polVars = {}
                            polVars['name'] = 'vmedia'
                            polVars['enable_virtual_media_encryption'] = True

                            # Add Policy Variables to immDict
                            kwargs['class_path'] = 'intersight,policies,virtual_media'
                            kwargs = ezfunctions.ez_append(polVars, **kwargs)

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
        return kwargs

    #==============================================
    # UCS Domain and Policies
    #==============================================
    def server_profiles(self, **kwargs):
        name_prefix = self.name_prefix
        args = kwargs['args']
        baseRepo = args.dir
        org = self.org
        path_sep = kwargs['path_sep']
        kwargs['fc_ports'] = kwargs['fc_ports']
        kwargs['server_type'] = kwargs['server_type']
        kwargs['boot_order_policy'] = kwargs['boot_order_policy']

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  The Quick Deployment Module - Domain Policies, will configure pools for a UCS Domain ')
            print(f'  Profile.\n')
            print(f'  This wizard will save the output for these pools in the following files:\n')
            print(f'  - {baseRepo}{path_sep}{org}{path_sep}{self.type}/ucs_server_profile_templates.yaml')
            print(f'  - {baseRepo}{path_sep}{org}{path_sep}{self.type}/ucs_server_profiles.yaml')
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
                    kwargs = profiles.profiles(name_prefix, org, self.type).quick_start_server_profiles(**kwargs)
                    kwargs = profiles.profiles(name_prefix, org, self.type).quick_start_server_templates(**kwargs)
                    policy_loop = True
                    configure_loop = True

            elif configure == 'N':
                configure_loop = True
            else:
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                print(f'\n-------------------------------------------------------------------------------------------\n')
        return kwargs
        
    #==============================================
    # Standalone Server Policies
    #==============================================
    def standalone_policies(self, **kwargs):
        args = kwargs['args']
        baseRepo = args.dir
        ezData = kwargs['ezData']
        jsonData = kwargs['jsonData']
        name_prefix = self.name_prefix
        org = self.org
        path_sep = kwargs['path_sep']
        polVars = {}

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  The Quick Deployment Module - Standalone Policies.\n')
            print(f'  This wizard will save the output for these policies in the following files:\n')
            print(f'  - {baseRepo}{path_sep}{org}{path_sep}{self.type}{path_sep}compute.yaml')
            print(f'  - {baseRepo}{path_sep}{org}{path_sep}{self.type}{path_sep}environment.yaml')
            print(f'  - {baseRepo}{path_sep}{org}{path_sep}{self.type}{path_sep}ethernet.yaml')
            print(f'  - {baseRepo}{path_sep}{org}{path_sep}{self.type}{path_sep}fibre_channel.yaml')
            print(f'  - {baseRepo}{path_sep}{org}{path_sep}{self.type}{path_sep}management.yaml')
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
                    jsonVars = jsonData['snmp.Policy']['allOf'][1]['properties']

                    # SNMP Contact
                    polVars['Description'] = jsonVars['SysContact']['description'] + \
                        'Note: Enter a string up to 64 characters, such as an email address or a name and telephone number.'
                    polVars['varDefault'] = ''
                    polVars['varInput'] = 'SNMP System Contact:'
                    polVars['varName'] = 'SNMP System Contact'
                    polVars['varRegex'] = '.*'
                    polVars['minLength'] = 1
                    polVars['maxLength'] = jsonVars['SysContact']['maxLength']
                    polVars['system_contact'] = ezfunctions.varStringLoop(**polVars)

                    # SNMP Location
                    polVars['Description'] = jsonVars['SysLocation']['description']
                    polVars['varDefault'] = ''
                    polVars['varInput'] = 'What is the Location of the host on which the SNMP agent (server) runs?'
                    polVars['varName'] = 'SNMP System Location'
                    polVars['varRegex'] = '.*'
                    polVars['minLength'] = 1
                    polVars['maxLength'] = jsonVars['SysLocation']['maxLength']
                    polVars['system_location'] = ezfunctions.varStringLoop(**polVars)

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
                    polVars['users'] = snmp_user_list

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
                    polVars['trap_destinations'] = snmp_dests

                    # Syslog Local Logging
                    jsonVars = jsonData['syslog.LocalClientBase']['allOf'][1]['properties']
                    polVars['var_description'] = jsonVars['MinSeverity']['description']
                    polVars['jsonVars'] = sorted(jsonVars['MinSeverity']['enum'])
                    polVars['defaultVar'] = jsonVars['MinSeverity']['default']
                    polVars['varType'] = 'Syslog Local Minimum Severity'
                    polVars['min_severity'] = ezfunctions.variablesFromAPI(**polVars)

                    polVars['local_logging'] = {'file':{'min_severity':polVars['min_severity']}}
                    remote_logging = ezfunctions.syslog_servers(jsonData, **polVars)
                    polVars['remote_logging'] = remote_logging

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  Network Configuration Variables:"')
                    print(f'    System Contact   = "{polVars["system_contact"]}"')
                    print(f'    System Locaction = "{polVars["system_location"]}"')
                    if len(polVars['trap_destinations']) > 0:
                        print(f'    snmp_trap_destinations = ''{')
                        for item in polVars['trap_destinations']:
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
                    if len(polVars['users']) > 0:
                        print(f'    snmp_users = ''{')
                        for item in polVars['users']:
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
                    for key, value in polVars['remote_logging'].items():
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

                            polVars['initial_write'] = True
                            polVars['policy_type'] = 'BIOS Policy'
                            polVars['header'] = '%s Variables' % (polVars['policy_type'])
                            polVars['template_file'] = 'template_open.jinja2'
                            polVars['template_type'] = 'bios_policies'

                            # Open the Template file
                            ezfunctions.write_to_template(self, **polVars)
                            polVars['initial_write'] = False

                            # Configure BIOS Policy
                            name = 'VMware'
                            polVars['name'] = name
                            polVars['descr'] = f'{name} BIOS Policy'
                            polVars['bios_template'] = 'Virtualization'


                            # Write Policies to Template File
                            polVars['template_file'] = '%s.jinja2' % (polVars['template_type'])
                            ezfunctions.write_to_template(self, **polVars)

                            # Close the Template file
                            polVars['template_file'] = 'template_close.jinja2'
                            ezfunctions.write_to_template(self, **polVars)

                            #_______________________________________________________________________
                            #
                            # Configure Boot Order Policy
                            #_______________________________________________________________________

                            polVars['initial_write'] = True
                            polVars['policy_type'] = 'Boot Order Policy'
                            polVars['header'] = '%s Variables' % (polVars['policy_type'])
                            polVars['template_file'] = 'template_open.jinja2'
                            polVars['template_type'] = 'boot_order_policies'

                            # Open the Template file
                            ezfunctions.write_to_template(self, **polVars)
                            polVars['initial_write'] = False

                            # Configure Boot Order Policy
                            name = 'VMware_M2'
                            polVars['name'] = name
                            polVars['descr'] = f'{name} Boot Order Policy'
                            polVars['boot_mode'] = 'Uefi'
                            polVars['enable_secure_boot'] = True
                            polVars['boot_mode'] = 'Uefi'
                            polVars['boot_devices'] = [
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
                            polVars['template_file'] = '%s.jinja2' % ('boot_policies')
                            ezfunctions.write_to_template(self, **polVars)

                            # Close the Template file
                            polVars['template_file'] = 'template_close.jinja2'
                            ezfunctions.write_to_template(self, **polVars)

                            #_______________________________________________________________________
                            #
                            # Configure IMC Access Policy
                            #_______________________________________________________________________

                            polVars['initial_write'] = True
                            polVars['policy_type'] = 'IMC Access Policy'
                            polVars['header'] = '%s Variables' % (polVars['policy_type'])
                            polVars['template_file'] = 'template_open.jinja2'
                            polVars['template_type'] = 'imc_access_policies'

                            # Open the Template file
                            ezfunctions.write_to_template(self, **polVars)
                            polVars['initial_write'] = False

                            # Configure IMC Access Policy
                            name = org
                            polVars['name'] = name
                            polVars['descr'] = f'{name} IMC Access Policy'
                            polVars['inband_ip_pool'] = 'VMware_KVM'
                            polVars['ipv4_address_configuration'] = True
                            polVars['ipv6_address_configuration'] = False

                            # Write Policies to Template File
                            polVars['template_file'] = '%s.jinja2' % (polVars['template_type'])
                            ezfunctions.write_to_template(self, **polVars)

                            # Close the Template file
                            polVars['template_file'] = 'template_close.jinja2'
                            ezfunctions.write_to_template(self, **polVars)

                            #_______________________________________________________________________
                            #
                            # Configure IPMI over LAN Policy
                            #_______________________________________________________________________

                            polVars['initial_write'] = True
                            polVars['policy_type'] = 'IPMI over LAN Policy'
                            polVars['header'] = '%s Variables' % (polVars['policy_type'])
                            polVars['template_file'] = 'template_open.jinja2'
                            polVars['template_type'] = 'ipmi_over_lan_policies'

                            # Open the Template file
                            ezfunctions.write_to_template(self, **polVars)
                            polVars['initial_write'] = False

                            # IPMI over LAN Settings
                            name = org
                            polVars['name'] = name
                            polVars['descr'] = f'{name} IPMI over LAN Policy'
                            polVars['enabled'] = True
                            polVars['ipmi_key'] = 1

                            # Write Policies to Template File
                            polVars['template_file'] = '%s.jinja2' % (polVars['template_type'])
                            ezfunctions.write_to_template(self, **polVars)

                            # Close the Template file
                            polVars['template_file'] = 'template_close.jinja2'
                            ezfunctions.write_to_template(self, **polVars)

                            #_______________________________________________________________________
                            #
                            # Configure Local User Policy
                            #_______________________________________________________________________

                            polVars['initial_write'] = True
                            polVars['policy_type'] = 'Local User Policy'
                            polVars['header'] = '%s Variables' % (polVars['policy_type'])
                            polVars['template_file'] = 'template_open.jinja2'
                            polVars['template_type'] = 'local_user_policies'

                            # Open the Template file
                            ezfunctions.write_to_template(self, **polVars)
                            polVars['initial_write'] = False

                            # Local User Settings
                            name = org
                            polVars['name'] = name
                            polVars['descr'] = f'{name} Local User Policy'
                            polVars['enabled'] = True
                            polVars['ipmi_key'] = 1

                            # Write Policies to Template File
                            polVars['template_file'] = '%s.jinja2' % (polVars['template_type'])
                            ezfunctions.write_to_template(self, **polVars)

                            # Close the Template file
                            polVars['template_file'] = 'template_close.jinja2'
                            ezfunctions.write_to_template(self, **polVars)

                            #_______________________________________________________________________
                            #
                            # Configure Power Policy
                            #_______________________________________________________________________

                            polVars['initial_write'] = True
                            polVars['policy_type'] = 'Power Policy'
                            polVars['header'] = '%s Variables' % (polVars['policy_type'])
                            polVars['template_file'] = 'template_open.jinja2'
                            polVars['template_type'] = 'power_policies'

                            # Open the Template file
                            ezfunctions.write_to_template(self, **polVars)
                            polVars['initial_write'] = False

                            # Power Settings
                            names = ['5108', '9508', 'Server']
                            for name in names:
                                polVars['allocated_budget'] = 0
                                polVars['name'] = name
                                polVars['descr'] = f'{name} Power Policy'
                                if name == 'Server': polVars['power_restore_state'] = 'LastState'
                                elif name == '9508': polVars['allocated_budget'] = 5600

                                polVars['power_redundancy'] = 'Grid'
                                polVars['ipmi_key'] = 1

                                # Write Policies to Template File
                                polVars['template_file'] = '%s.jinja2' % (polVars['template_type'])
                                ezfunctions.write_to_template(self, **polVars)

                            # Close the Template file
                            polVars['template_file'] = 'template_close.jinja2'
                            ezfunctions.write_to_template(self, **polVars)

                            #_______________________________________________________________________
                            #
                            # Configure Serial over LAN Policy
                            #_______________________________________________________________________

                            polVars['initial_write'] = True
                            polVars['policy_type'] = 'Serial over LAN Policy'
                            polVars['header'] = '%s Variables' % (polVars['policy_type'])
                            polVars['template_file'] = 'template_open.jinja2'
                            polVars['template_type'] = 'serial_over_lan_policies'

                            # Open the Template file
                            ezfunctions.write_to_template(self, **polVars)
                            polVars['initial_write'] = False

                            # Serial over LAN Settings
                            name = org
                            polVars['name'] = name
                            polVars['descr'] = f'{name} Serial over LAN Policy'
                            polVars['enabled'] = True
                            polVars['baud_rate'] = 115200
                            polVars['com_port'] = 'com0'
                            polVars['ssh_port'] = 2400

                            # Write Policies to Template File
                            polVars['template_file'] = '%s.jinja2' % (polVars['template_type'])
                            ezfunctions.write_to_template(self, **polVars)

                            # Close the Template file
                            polVars['template_file'] = 'template_close.jinja2'
                            ezfunctions.write_to_template(self, **polVars)

                            #_______________________________________________________________________
                            #
                            # Configure SNMP Policy
                            #_______________________________________________________________________

                            polVars['initial_write'] = True
                            polVars['policy_type'] = 'SNMP Policy'
                            polVars['header'] = '%s Variables' % (polVars['policy_type'])
                            polVars['template_file'] = 'template_open.jinja2'
                            polVars['template_type'] = 'snmp_policies'

                            # Open the Template file
                            ezfunctions.write_to_template(self, **polVars)
                            polVars['initial_write'] = False

                            # SNMP Settings
                            name = org
                            polVars['name'] = name
                            polVars['descr'] = f'{name} SNMP Policy'
                            polVars['access_community_string'] = ''
                            polVars['enabled'] = True
                            polVars['engine_input_id'] = ''
                            polVars['port'] = 161
                            polVars['snmp_community_access'] = 'Disabled'
                            polVars['trap_community_string'] = ''

                            # Write Policies to Template File
                            polVars['template_file'] = '%s.jinja2' % (polVars['template_type'])
                            ezfunctions.write_to_template(self, **polVars)

                            # Close the Template file
                            polVars['template_file'] = 'template_close.jinja2'
                            ezfunctions.write_to_template(self, **polVars)

                            #_______________________________________________________________________
                            #
                            # Configure Storage Policy
                            #_______________________________________________________________________

                            polVars['initial_write'] = True
                            polVars['policy_type'] = 'Storage Policy'
                            polVars['header'] = '%s Variables' % (polVars['policy_type'])
                            polVars['template_file'] = 'template_open.jinja2'
                            polVars['template_type'] = 'storage_policies'

                            # Open the Template file
                            ezfunctions.write_to_template(self, **polVars)
                            polVars['initial_write'] = False

                            name = 'M2_Raid'
                            polVars['name'] = name
                            polVars['descr'] = f'{name} Storage Policy'
                            polVars['drive_group'] = {}
                            polVars['global_hot_spares'] = ''
                            polVars['m2_configuration'] = [ { 'controller_slot':'MSTOR-RAID-1,MSTOR-RAID-2' } ]
                            polVars['single_drive_raid_configuration'] = {}
                            polVars['unused_disks_state'] = 'No Change'
                            polVars['use_jbod_for_vd_creation'] = True

                            # Write Policies to Template File
                            polVars['template_file'] = '%s.jinja2' % (polVars['template_type'])
                            ezfunctions.write_to_template(self, **polVars)

                            # Close the Template file
                            polVars['template_file'] = 'template_close.jinja2'
                            ezfunctions.write_to_template(self, **polVars)

                            #_______________________________________________________________________
                            #
                            # Configure Syslog Policy
                            #_______________________________________________________________________

                            polVars['initial_write'] = True
                            polVars['policy_type'] = 'Syslog Policy'
                            polVars['header'] = '%s Variables' % (polVars['policy_type'])
                            polVars['template_file'] = 'template_open.jinja2'
                            polVars['template_type'] = 'syslog_policies'

                            # Open the Template file
                            ezfunctions.write_to_template(self, **polVars)
                            polVars['initial_write'] = False

                            # Syslog Settings
                            name = org
                            polVars['name'] = name
                            polVars['descr'] = f'{name} Syslog Policy'
                            polVars['enabled'] = True
                            polVars['ipmi_key'] = 1

                            # Write Policies to Template File
                            polVars['template_file'] = '%s.jinja2' % (polVars['template_type'])
                            ezfunctions.write_to_template(self, **polVars)

                            # Close the Template file
                            polVars['template_file'] = 'template_close.jinja2'
                            ezfunctions.write_to_template(self, **polVars)

                            #_______________________________________________________________________
                            #
                            # Configure Thermal Policy
                            #_______________________________________________________________________

                            polVars['initial_write'] = True
                            polVars['policy_type'] = 'Thermal Policy'
                            polVars['header'] = '%s Variables' % (polVars['policy_type'])
                            polVars['template_file'] = 'template_open.jinja2'
                            polVars['template_type'] = 'thermal_policies'

                            # Open the Template file
                            ezfunctions.write_to_template(self, **polVars)
                            polVars['initial_write'] = False

                            # Thermal Settings
                            names = ['5108', '9508']
                            for name in names:
                                polVars['name'] = name
                                polVars['descr'] = f'{name} Thermal Policy'
                                polVars['fan_control_mode'] = 'Balanced'

                                # Write Policies to Template File
                                polVars['template_file'] = '%s.jinja2' % (polVars['template_type'])
                                ezfunctions.write_to_template(self, **polVars)

                            # Close the Template file
                            polVars['template_file'] = 'template_close.jinja2'
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

def policy_select_loop(**kwargs):
    ezData = kwargs['ezData']
    policy = kwargs['policy']
    name_prefix = kwargs['name_prefix']
    org = kwargs['org']
    loop_valid = False
    while loop_valid == False:
        create_policy = True
        kwargs['inner_policy'] = policy.split('.')[1]
        kwargs['inner_type']   = policy.split('.')[0]
        kwargs['inner_var']    = policy.split('.')[2]
        inner_policy = kwargs['inner_policy']
        inner_type   = kwargs['inner_type']
        kwargs = ezfunctions.policies_parse(inner_type, inner_policy, **kwargs)
        if not len(kwargs["policies"]) > 0:
            valid = False
            while valid == False:

                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'   There was no {inner_policy} found.')
                print(f'\n-------------------------------------------------------------------------------------------\n')

                policy_description = ezfunctions.mod_pol_description(inner_policy)

                if kwargs["allow_opt_out"] == True:
                    Question = input(f'Do you want to create a(n) {policy_description}?  Enter "Y" or "N" [Y]: ')
                    if Question == '' or Question == 'Y':
                        create_policy = True
                        valid = True
                    elif Question == 'N':
                        create_policy = False
                        valid = True
                        return kwargs
                else:
                    create_policy = True
                    valid = True

        else:
            kwargs = ezfunctions.choose_policy(inner_policy, **kwargs)
            if kwargs['policy'] == 'create_policy':
                create_policy = True
            elif kwargs['policy'] == '' and kwargs["allow_opt_out"] == True:
                loop_valid = True
                create_policy = False
                kwargs[kwargs['inner_var']] = ''
                return kwargs
            elif not kwargs['policy'] == '':
                loop_valid = True
                create_policy = False
                kwargs[kwargs['inner_var']] = kwargs['policy']
                return kwargs

        # Simple Loop to show name_prefix in Use
        ncount = 0
        if ncount == 5:
            print(name_prefix)
        
        # Create Policy if Option was Selected
        if create_policy == True:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  Starting module to create {inner_policy} in {org}')
            print(f'\n-------------------------------------------------------------------------------------------\n')

            lan_list = ezData['ezimm']['allOf'][1]['properties']['lan_list']
            p1_list = ezData['ezimm']['allOf'][1]['properties']['p1_list']
            p2_list = ezData['ezimm']['allOf'][1]['properties']['p2_list']
            p3_list = ezData['ezimm']['allOf'][1]['properties']['p3_list']
            san_list = ezData['ezimm']['allOf'][1]['properties']['san_list']
            vxan_list = ezData['ezimm']['allOf'][1]['properties']['vxan_list']
            if re.search('pools$', inner_policy):
                kwargs = eval(f"pools.pools(name_prefix, org, inner_type).{inner_policy}(**kwargs)")
            elif inner_policy in p1_list:
                kwargs = eval(f"p1.policies(name_prefix, org, inner_type).{inner_policy}(**kwargs)")
            elif inner_policy in p2_list:
                kwargs = eval(f"p2.policies(name_prefix, org, inner_type).{inner_policy}(**kwargs)")
            elif inner_policy in p3_list:
                kwargs = eval(f"p3.policies(name_prefix, org, inner_type).{inner_policy}(**kwargs)")
            elif inner_policy in lan_list:
                kwargs = eval(f"lan.policies(name_prefix, org, inner_type).{inner_policy}(**kwargs)")
            elif inner_policy in san_list:
                kwargs = eval(f"san.policies(name_prefix, org, inner_type).{inner_policy}(**kwargs)")
            elif inner_policy in vxan_list:
                kwargs = eval(f"vxan.policies(name_prefix, org, inner_type).{inner_policy}(**kwargs)")
