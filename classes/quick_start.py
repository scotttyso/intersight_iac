from copy import deepcopy
import ezfunctions
import ipaddress
import json
import lansan
import policies
import pools
import re
import textwrap
import validating
import yaml

class MyDumper(yaml.Dumper):
    def increase_indent(self, flow=False, indentless=False):
        return super(MyDumper, self).increase_indent(flow, False)

class quick_start(object):
    def __init__(self, name_prefix, org, type):
        self.name_prefix = name_prefix
        self.org         = org
        self.type        = type

    #==============================================
    # BIOS Policy
    #==============================================
    def bios_policies(self, **kwargs):
        baseRepo = kwargs['args'].dir
        org      = self.org
        path_sep = kwargs['path_sep']
        print(f'\n-------------------------------------------------------------------------------------------\n')
        print(f'  The Quick Deployment Module - BIOS policies for a UCS Server ')
        print(f'  This wizard will save the output for the BIOS Policy to the following file:\n')
        print(f'  - {baseRepo}{path_sep}{org}{path_sep}{self.type}{path_sep}compute.yaml')
        print(f'\n-------------------------------------------------------------------------------------------\n')
        #==============================================
        # Trusted Platform Module
        #==============================================
        # Trusted Platform Module
        kwargs['jData'] = deepcopy({})
        kwargs['jData']['description'] = 'Flag to Determine if the Servers have a TPM Installed.'
        kwargs['jData']['default']     = True
        kwargs['jData']['varInput']    = f'Will any of these servers have a TPM Module Installed?'
        kwargs['jData']['varName']     = 'TPM Installed'
        kwargs['tpm_installed'] = ezfunctions.varBoolLoop(**kwargs)
        #==============================================
        # Configure BIOS Policy
        #==============================================
        polVars = {}
        template_names = ['M5-virtualization', 'M5-virtualization-tpm', 'M6-virtualization-tpm']
        for bname in template_names:
            name = bname
            polVars['name'] = name
            polVars['description'] = f'{name} BIOS Policy'
            if bname == 'M5-virtualization':
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
            #==============================================
            # Add Policy Variables to immDict
            #==============================================
            kwargs['class_path'] = 'policies,bios'
            kwargs = ezfunctions.ez_append(polVars, **kwargs)
        # Return kwargs
        return kwargs

    #==============================================
    # Boot and Storage Policies
    #==============================================
    def boot_and_storage(self, **kwargs):
        baseRepo  = kwargs['args'].dir
        boot_type = kwargs['boot_type']
        org       = self.org
        path_sep  = kwargs['path_sep']
        print(f'\n-------------------------------------------------------------------------------------------\n')
        print(f'  The Quick Deployment Module - Boot/Storage, Policies.\n')
        print(f'  This wizard will save the output for these pools in the following files:\n')
        print(f'  - {baseRepo}{path_sep}{org}{path_sep}policies{path_sep}compute.yaml')
        print(f'  - {baseRepo}{path_sep}{org}{path_sep}policies{path_sep}storage_policies.yaml')
        print(f'\n-------------------------------------------------------------------------------------------\n')
        #==============================================
        # Configure Boot Order Policy
        #==============================================
        polVars = {}
        secBootList = [False, True]
        if boot_type == 'm2' or boot_type == 'raid1': secBootList = [False, True]
        else: secBootList = [False]
        for i in secBootList:
            if i   == False and boot_type == 'm2': name = 'M2-pxe'
            elif i == True  and boot_type == 'm2': name = 'M2'
            elif i == False and boot_type == 'raid1': name = 'raid1-pxe'
            elif i == True  and boot_type == 'raid1': name = 'raid1'
            elif boot_type == 'stateless': name = 'pxe'
            polVars['name'] = name
            polVars['boot_mode'] = 'Uefi'
            if not boot_type == 'stateless' and kwargs['tpm_installed'] == True:
                polVars['enable_secure_boot'] = i
            else: polVars['enable_secure_boot'] = False
            polVars['boot_devices'] = [{
                'enabled':True, 'name':'kvm', 'object_type':'boot.VirtualMedia', 'sub_type':'kvm-mapped-dvd'
            }]
            if boot_type == 'm2':
                polVars['boot_devices'].append({
                    'enabled':True, 'name':'M2', 'object_type':'boot.LocalDisk', 'slot':'MSTOR-RAID'
                })
            if boot_type == 'raid1':
                polVars['boot_devices'].append({
                    'enabled':True, 'name':'mraid',
                    'object_type':'boot.LocalDisk', 'slot':'MRAID'
                })
            if i == False:
                polVars['boot_devices'].append({
                    'enabled':True, 'name':'pxe', 'interface_name':'mgmt-a', 'interface_source':'name',
                    'ip_type':'IPv4', 'object_type':'boot.Pxe', 'slot':'MLOM'
                })
            polVars['boot_devices'].append({
                'enabled':True, 'name':'uefishell', 'object_type':'boot.UefiShell'
            })
            # Add Policy Variables to immDict
            kwargs['class_path'] = 'policies,boot_order'
            kwargs = ezfunctions.ez_append(polVars, **kwargs)
        #==============================================
        # Configure Storage Policy
        #==============================================
        polVars = {}
        if boot_type == 'm2':
            polVars['name'] = 'M2'
            polVars['m2_raid_configuration'] = [{'slot':'MSTOR-RAID-1'}]
            polVars['use_jbod_for_vd_creation'] = True
        elif boot_type == 'raid1':
            polVars['name'] = 'raid1'
            polVars['drive_group'] = [{
                'manual_drive_group':[{'drive_array_spans':[{'slots':'1,2'}]}],
                'name':'DG1',
                'raid_level':'Raid1',
                'virtual_drives':[{
                    'access_policy':'Default', 'boot_drive':True, 'disk_cache':'Default',
                    'expand_to_available':True, 'read_policy':'Always Read Ahead', 'size':10,
                    'stripe_size':'64KiB', 'vd_name':'VD1', 'write_policy':'Write Back Good BBU'
                }]
            }]
            polVars['unused_disks_state'] = 'No Change'
            polVars['use_jbod_for_vd_creation'] = True
        if re.search('(m2|raid1)', boot_type):
            # Add Policy Variables to immDict
            kwargs['class_path'] = 'policies,storage'
            kwargs = ezfunctions.ez_append(polVars, **kwargs)
        # Return kwargs
        return kwargs

    #==============================================
    # UCS Chassis, Domain and Domain Policies
    #==============================================
    def domain_policies(self, **kwargs):
        baseRepo       = kwargs['args'].dir
        ezData         = kwargs['ezData']
        jsonData       = kwargs['jsonData']
        name_prefix    = kwargs['domain_prefix']
        org            = self.org
        path_sep       = kwargs['path_sep']
        configure_loop = False
        kwargs['name_prefix'] = name_prefix
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
            configure = input(f'Do You Want to run the Quick Deployment Module - Domain Policy Configuration?'\
                '  \nEnter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                loop_count  = 0
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
                    #==============================================
                    # Prompt User for Domain Name
                    #==============================================
                    kwargs['jData'] = deepcopy(jsonVars['Name'])
                    kwargs['jData']['maximum']  = 64
                    kwargs['jData']['minimum']  = 1
                    kwargs['jData']['varInput'] = 'What is the name for this UCS Domain?'
                    kwargs['jData']['varName']  = 'UCS Domain Name'
                    domain_name = ezfunctions.varStringLoop(**kwargs)
                    #==============================================
                    # Prompt User for Device Model for Domain
                    #==============================================
                    kwargs['multi_select'] = False
                    jsonVars = jsonData['fabric.PortPolicy']['allOf'][1]['properties']
                    kwargs['jData'] = deepcopy(jsonVars['DeviceModel'])
                    kwargs['jData']['enum'].remove('unknown')
                    kwargs['jData']['varType'] = 'Device Model'
                    device_model = ezfunctions.variablesFromAPI(**kwargs)
                    kwargs['device_model'] = device_model
                    #==============================================
                    # Prompt User for FI Serial Numbers
                    #==============================================
                    serials = ezfunctions.ucs_domain_serials(**kwargs)
                    #==============================================
                    # Prompt User for VLANs for Domain
                    #==============================================
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  IMPORTANT NOTE: The FCoE VLAN will be assigned based on the VSAN Identifier.')
                    print(f'                  Be sure to exclude the VSAN for Fabric A and B from the VLAN Pool.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    VlanList,vlanListExpanded = ezfunctions.vlan_pool(org)
                    nativeVlan = ezfunctions.vlan_native_function(vlanListExpanded, VlanList)
                    #==============================================
                    # Configure Multicast Policy
                    #==============================================
                    polVars = {'name':'mcast'}
                    kwargs['class_path'] = 'policies,multicast'
                    kwargs = ezfunctions.ez_append(polVars, **kwargs)
                    #==============================================
                    # Configure VLAN Policy
                    #==============================================
                    polVars = {'name': 'vlans'}
                    policy_vlan_list = deepcopy(vlanListExpanded)
                    if not nativeVlan == '':
                        if int(nativeVlan) in vlanListExpanded:
                            vlanListExpanded.remove(int(nativeVlan))
                    elif nativeVlan == '' and 1 in vlanListExpanded:
                        nativeVlan == 1
                        vlanListExpanded.remove(1)
                    #==============================================
                    # Prepare Values to Return to main module
                    #==============================================
                    kwargs['vlan_list_expanded'] = policy_vlan_list
                    kwargs['vlan_list'] = ezfunctions.vlan_list_format(vlanListExpanded)
                    polVars['vlans'] = []
                    if org == 'default': vname = 'vlan'
                    else: vname = org
                    if not nativeVlan == '':
                        polVars["vlans"].append({
                            'auto_allow_on_uplinks':True, 'multicast_policy':'mcast',
                            'name':vname, 'native_vlan':True, 'vlan_list':nativeVlan
                        })
                    if nativeVlan == '':
                        polVars["vlans"].append({
                            'auto_allow_on_uplinks':True, 'multicast_policy':'mcast',
                            'name':vname, 'native_vlan':True, 'vlan_list':1
                        })
                    polVars["vlans"].append({
                        'multicast_policy':'mcast', 'name':vname, 'vlan_list':kwargs['vlan_list']
                    })
                    kwargs['class_path'] = 'policies,vlan'
                    kwargs = ezfunctions.ez_append(polVars, **kwargs)
                    #==============================================
                    # Configure Flow Control Policy
                    #==============================================
                    polVars = {'name': 'flow-ctrl'}
                    kwargs['class_path'] = 'policies,flow_control'
                    kwargs = ezfunctions.ez_append(polVars, **kwargs)
                    #==============================================
                    # Configure Link Aggregation Policy
                    #==============================================
                    polVars = {'name': 'link-agg'}
                    kwargs['class_path'] = 'policies,link_aggregation'
                    kwargs = ezfunctions.ez_append(polVars, **kwargs)
                    #==============================================
                    # Configure Link Control Policy
                    #==============================================
                    polVars = {'name': 'link-ctrl'}
                    kwargs['class_path'] = 'policies,link_control'
                    kwargs = ezfunctions.ez_append(polVars, **kwargs)
                    #==============================================
                    # Determine if Fibre-Channel will be Utilized
                    #==============================================
                    kwargs = policies.port_modes_fc(**kwargs)
                    #================================================
                    # If Unified Ports Exist Configure VSAN Policies
                    #================================================
                    if len(kwargs['fc_converted_ports']) > 0:
                        #==============================================
                        # Prompt User for the VSAN for Fabric A and B
                        #==============================================
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
                                        kwargs[f'vsan_id_{x}'] = vsan_id
                                        valid_vlan = validating.number_in_range('VSAN ID', vsan_id, 1, 4094)
                                        if valid_vlan == True:
                                            loop_count += 1
                                            valid = True
                                    else: ezfunctions.message_fcoe_vlan(vsan_id, org)
                                else: ezfunctions.message_invalid_vsan()
                        #==============================================
                        # Configure VSAN Policies
                        #==============================================
                        polVars = {}
                        for x in fabrics:
                            polVars['name'] = f'vsan-{kwargs[f"vsan_id_{x}"]}'
                            polVars['vsans'] = [{
                                'fcoe_vlan_id':kwargs[f"vsan_id_{x}"],
                                'name':f'vsan-{x}',
                                'vsan_id':kwargs[f"vsan_id_{x}"]
                            }]
                            #==============================================
                            # Add Policy Variables to immDict
                            #==============================================
                            kwargs['class_path'] = 'policies,vsan'
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
                            if not native_count == 1: ezfunctions.message_invalid_native_vlan(nativeVlan, VlanList)
                            else: valid = True
                    #==============================================
                    # Configure Ethernet Network Group Policy
                    #==============================================
                    polVars = {}
                    name = f'uplink'
                    polVars['name'] = name
                    polVars['allowed_vlans'] = VlanList
                    if not nativeVlan == '':
                        polVars['native_vlan'] = nativeVlan
                    else:
                        polVars['native_vlan'] = ''
                        polVars.pop('native_vlan')
                    kwargs['class_path'] = 'policies,ethernet_network_group'
                    kwargs = ezfunctions.ez_append(polVars, **kwargs)
                    #==============================================
                    # Configure Ethernet Uplink Port-Channels
                    #==============================================
                    kwargs['port_type'] = 'Ethernet Uplink Port-Channels'
                    kwargs = policies.port_list_eth(self, **kwargs)
                    kwargs['port_channel_ethernet_uplinks'] = kwargs['portDict']
                    kwargs['fc_ports_in_use'] = []
                    if len(kwargs['fc_converted_ports']) > 0:
                        #==============================================
                        # Configure Fibre-Channel Uplink Port-Channels
                        #==============================================
                        kwargs['portDict'] = []
                        kwargs['port_type'] = 'FC Uplink Port-Channels'
                        kwargs = policies.port_list_fc(self, **kwargs)
                        kwargs['port_channel_fc_uplinks'] = kwargs['portDict']
                    #==============================================
                    # Configure Server Ports
                    #==============================================
                    kwargs['portDict'] = []
                    kwargs['port_type'] = 'Server Ports'
                    kwargs = policies.port_list_eth(self, **kwargs)
                    kwargs['port_role_servers'] = kwargs['portDict']

                    kwargs['port_policy'] = {
                        'names': [f'{domain_name}-a', f'{domain_name}-b'],
                        'port_channel_ethernet_uplinks': kwargs['port_channel_ethernet_uplinks'],
                        'port_role_servers': kwargs['port_role_servers']
                    }
                    if len(kwargs['fc_converted_ports']) > 0:
                        kwargs['port_policy'].update({
                            'port_channel_fc_uplinks': kwargs['port_channel_fc_uplinks'],
                            'port_modes': kwargs['port_modes'],
                        })
                    #==================================================
                    # Prompt User for System MTU for System QoS Policy
                    #==================================================
                    kwargs['jData'] = deepcopy({})
                    kwargs['jData']['default']     = True
                    kwargs['jData']['description'] = 'This option will set the MTU to 9216 if answer is "Y"'\
                        ' or 1500 if answer is "N".'
                    kwargs['jData']['varInput']    = f'Do you want to enable Jumbo MTU?'
                    kwargs['jData']['varName']     = 'MTU'
                    answer = ezfunctions.varBoolLoop(**kwargs)
                    if answer == True: mtu = 9216
                    else: mtu = 1500
                    kwargs['mtu'] = mtu
                    #==============================================
                    # Prompt User for NTP Servers
                    #==============================================
                    primary_ntp = ezfunctions.ntp_primary()
                    alternate_ntp = ezfunctions.ntp_alternate()
                    ntp_servers = [primary_ntp]
                    if not alternate_ntp == '': ntp_servers.append(alternate_ntp)
                    #==============================================
                    # Prompt User for Timezone
                    #==============================================
                    kwargs['multi_select'] = False
                    jsonVars = jsonData['appliance.SystemInfo']['allOf'][1]['properties']['TimeZone']['enum']
                    tz_regions = []
                    for i in jsonVars:
                        tz_region = i.split('/')[0]
                        if not tz_region in tz_regions: tz_regions.append(tz_region)
                    tz_regions = sorted(tz_regions)
                    kwargs['jData'] = deepcopy({})
                    kwargs['jData']['default']     = 'America'
                    kwargs['jData']['description'] = 'Timezone Regions...'
                    kwargs['jData']['enum']        = tz_regions
                    kwargs['jData']['varType']     = 'Time Region'
                    time_region = ezfunctions.variablesFromAPI(**kwargs)
                    region_tzs = []
                    for item in jsonVars:
                        if time_region in item: region_tzs.append(item)
                    kwargs['jData'] = deepcopy({})
                    kwargs['jData']['description'] = 'Region Timezones...'
                    kwargs['jData']['enum']        = sorted(region_tzs)
                    kwargs['jData']['varType']     = 'Region Timezones'
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
                            #==============================================
                            # Configure Sytem QoS Settings
                            #==============================================
                            polVars = {}
                            polVars['name'] = 'system-qos'
                            kwargs['Platinum'] = {
                                'bandwidth_percent':20, 'cos':5, 'mtu':mtu, 'multicast_optimize':False,
                            'packet_drop':False, 'priority':'Platinum', 'state':'Enabled', 'weight':10}
                            kwargs['Gold'] = {
                                'bandwidth_percent':18, 'cos':4, 'mtu':mtu, 'multicast_optimize':False,
                            'packet_drop':True, 'priority':'Gold', 'state':'Enabled', 'weight':9}
                            kwargs['FC'] = {
                                'bandwidth_percent':20, 'cos':3, 'mtu':2240, 'multicast_optimize':False,
                            'packet_drop':False, 'priority':'FC', 'state':'Enabled', 'weight':10}
                            kwargs['Silver'] = {
                                'bandwidth_percent':18, 'cos':2, 'mtu':mtu, 'multicast_optimize':False,
                            'packet_drop':True, 'priority':'Silver', 'state':'Enabled', 'weight':8}
                            kwargs['Bronze'] = {
                                'bandwidth_percent':14, 'cos':1, 'mtu':mtu, 'multicast_optimize':False,
                            'packet_drop':True, 'priority':'Bronze', 'state':'Enabled', 'weight':7}
                            kwargs['Best Effort'] = {
                                'bandwidth_percent':10, 'cos':255, 'mtu':mtu, 'multicast_optimize':False,
                            'packet_drop':True, 'priority':'Best Effort', 'state':'Enabled', 'weight':5}
                            polVars['classes'] = []
                            priorities = ['Platinum', 'Gold', 'FC', 'Silver', 'Bronze', 'Best Effort']
                            for priority in priorities:
                                polVars['classes'].append(kwargs[priority])

                            # Add Policy Variables to immDict
                            kwargs['class_path'] = 'policies,system_qos'
                            kwargs = ezfunctions.ez_append(polVars, **kwargs)
                            #==============================================
                            # Configure Network Connectivity Policy
                            #==============================================
                            polVars = {}
                            polVars['name'] = f'dns'
                            polVars['dns_servers_v4'] = [kwargs['primary_dns']]
                            if not kwargs['secondary_dns'] == '':
                                polVars['dns_servers_v4'].append(kwargs['secondary_dns'])
                            kwargs['class_path'] = 'policies,network_connectivity'
                            kwargs = ezfunctions.ez_append(polVars, **kwargs)
                            #==============================================
                            # Configure NTP Policy
                            #==============================================
                            polVars = {}
                            polVars['name'] = f'ntp'
                            polVars['ntp_servers'] = ntp_servers
                            polVars['timezone'] = timezone
                            kwargs['class_path'] = 'policies,ntp'
                            kwargs = ezfunctions.ez_append(polVars, **kwargs)
                            #==============================================
                            # Configure Switch Control Policy
                            #==============================================
                            polVars = {}
                            polVars['name'] = f'sw_ctrl'
                            polVars['vlan_port_count_optimization'] = False
                            kwargs['class_path'] = 'policies,switch_control'
                            kwargs = ezfunctions.ez_append(polVars, **kwargs)
                            #==============================================
                            # Configure Port Policy
                            #==============================================
                            polVars = kwargs['port_policy']
                            kwargs['class_path'] = 'policies,port'
                            kwargs = ezfunctions.ez_append(polVars, **kwargs)
                            #==============================================
                            # Configure UCS Chassis Profile
                            #==============================================
                            kwargs['jData'] = deepcopy({})
                            kwargs['jData']['default']     = 1
                            kwargs['jData']['description'] = f'Number of Chassis attached to {domain_name}.'
                            kwargs['jData']['maximum']     = 20
                            kwargs['jData']['minimum']     = 1
                            kwargs['jData']['varInput']    = f'Enter the Number of Chassis attached to {domain_name}:'
                            kwargs['jData']['varName']     = 'Chassis Count'
                            chassis_count = ezfunctions.varNumberLoop(**kwargs)
                            chassis_models = ['5108', '9508']
                            chassis_dict = {}
                            imc_policy = kwargs['immDict']['orgs'][org]['pools']['ip'][0]['name']
                            for i in chassis_models:
                                chassis_dict.update({ i: {
                                    'imc_access_policy':imc_policy, 'names':[], 'power_policy':i,
                                    'snmp_policy':'snmp', 'targets':[], 'thermal_policy':i,
                                }})
                            #==============================================
                            # Chassis Model
                            #==============================================
                            rangex = int(chassis_count) + 1
                            for x in range(1,rangex):
                                kwargs['multi_select'] = False
                                jsonVars = ezData['ezimm']['allOf'][1]['properties']['policies']['thermal.Policy']
                                kwargs['jData'] = deepcopy(jsonVars['chassisType'])
                                kwargs['jData']['varType'] = 'Chassis Model'
                                chassis_model = ezfunctions.variablesFromAPI(**kwargs)
                                #==============================================
                                # Prompt User for Chassis Serial Number(s)
                                #==============================================
                                kwargs['jData'] = deepcopy({})
                                kwargs['jData']['description'] = 'Serial Number of the Chassis to assign to the Profile.'
                                kwargs['jData']['maximum']     = 11
                                kwargs['jData']['minimum']     = 11
                                kwargs['jData']['pattern']     = '^[A-Z]{3}[2-3][\\d]([0][1-9]|[1-4][0-9]|[5][1-3])[\\dA-Z]{4}$'
                                kwargs['jData']['varInput']    = f'What is the Serial Number of Chassis {x}? [press enter to skip]:'
                                kwargs['jData']['varName']     = 'Serial Number'
                                serial_number = ezfunctions.varStringLoop(**kwargs)
                                if serial_number == '': serial_number = 'unknown'
                                chassis_dict[f'{chassis_model}']['targets'].append({
                                    'name':f'{domain_name}-{x}','serial_number':serial_number
                                })
                            #==============================================
                            # Add Policy Variables to immDict
                            #==============================================
                            for i in chassis_models:
                                if len(chassis_dict[i]['targets']) > 0:
                                    polVars = chassis_dict[i]
                                    kwargs['class_path'] = 'profiles,chassis'
                                    kwargs = ezfunctions.ez_append(polVars, **kwargs)
                            #==============================================
                            # Configure UCS Domain Profile
                            #==============================================
                            polVars = {
                                'name': domain_name, 'network_connectivity_policy': f'dns', 'ntp_policy': f'ntp',
                                'port_policies': [f'{domain_name}-a', f'{domain_name}-b'], 'serial_numbers': serials,
                                'snmp_policy': f'snmp-domain', 'switch_control_policy': 'sw-ctrl',
                                'syslog_policy': f'syslog-domain', 'system_qos_policy': 'qos',
                                'vlan_policies': ['vlans']
                            }
                            if len(kwargs['fc_converted_ports']) > 0:
                                polVars['vsan_policies'] = [f"vsan-{kwargs['vsan_id_a']}', f'vsan-{kwargs['vsan_id_b']}"]
                            #==============================================
                            # Add Policy Variables to immDict
                            #==============================================
                            kwargs['class_path'] = 'profiles,domain'
                            kwargs = ezfunctions.ez_append(polVars, **kwargs)
                            configure_loop = True
                            policy_loop = True
                            valid_confirm = True
                        elif confirm_policy == 'N':
                            policy_type = 'domain_policies'
                            ezfunctions.message_starting_over(policy_type)
                            valid_confirm = True
                        else: ezfunctions.message_invalid_y_or_n('short')
            elif configure == 'N': configure_loop = True
            else: ezfunctions.message_invalid_y_or_n('short')
        if configure == 'Y' or configure == '': kwargs['Config'] = True
        elif configure == 'N': kwargs['Config'] = False
        return kwargs

    #==============================================
    # LAN and SAN Policies
    #==============================================
    def lan_san_policies(self, **kwargs):
        baseRepo       = kwargs['args'].dir
        configure_loop = False
        ezData         = kwargs['ezData']
        org            = self.org
        path_sep       = kwargs['path_sep']
        if kwargs['mtu'] > 8999: mtu = 9000
        else: mtu = 1500
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
                    vlan_policy = org
                    vlan_list = kwargs['vlan_list']
                    vlan_policy_list = ezfunctions.vlan_list_full(vlan_list)
                    fc_ports_in_use = kwargs['fc_ports_in_use']
                    kwargs['multi_select'] = False
                    jsonVars = ezData['ezimm']['allOf'][1]['properties']['policies']['fabric.EthNetworkControlPolicy']
                    #==============================================
                    # Prompt User for Neighbor Discovery Protocol
                    #==============================================
                    kwargs['jData'] = deepcopy(jsonVars['discoveryProtocol'])
                    kwargs['jData']['varType'] = 'Neighbor Discovery Protocol'
                    neighbor_discovery = ezfunctions.variablesFromAPI(**kwargs)
                    #==============================================
                    # Prompt User for vNIC VLAN(s)
                    #==============================================
                    vcount = 0
                    for i in ['mgmt_1', 'migration_2', 'storage_3']:
                        valid = False
                        while valid == False:
                            vnic_name = i.split('_')[0]
                            vnic_vlan = i.split('_')[1]
                            kwargs['jData'] = deepcopy({})
                            kwargs['jData']['default']     = vnic_vlan
                            kwargs['jData']['description'] = f"LAN Connectivity Policy vNICs - {vnic_name} VLAN Identifier."
                            kwargs['jData']['minimum']     = 1
                            kwargs['jData']['maximum']     = 4094
                            kwargs['jData']['varInput']    = f"Enter the VLAN ID for {vnic_name}:"
                            kwargs['jData']['varName']     = f"{vnic_name} VLAN ID"
                            vnic_vlan = ezfunctions.varNumberLoop(**kwargs)
                            valid = ezfunctions.validate_vlan_in_policy(vlan_policy_list, vnic_vlan)
                        kwargs[f'{vnic_name}_vlan']  = vnic_vlan

                    #==============================================
                    # Prompt User for DVS VLAN(s)
                    #==============================================
                    valid = False
                    while valid == False:
                        VlanList = input('Enter the VLAN or List of VLANs to add to the dvs/(Virtual Machine) vNICs: ')
                        if not VlanList == '':
                            valid_vlan = True
                            vlans_not_in_domain_policy = []
                            vlanListExpanded = ezfunctions.vlan_list_full(VlanList)
                            for v in vlanListExpanded:
                                valid_v = ezfunctions.validate_vlan_in_policy(vlan_policy_list, v)
                                if valid_v == False: vlans_not_in_domain_policy.append(v)
                            if len(vlans_not_in_domain_policy) > 0:
                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                print(f'  Error with VLAN(s) assignment!!  The following VLAN(s) are missing.')
                                print(f'  - Domain VLAN Policy: "{vlan_policy}"')
                                print(f'  - VLANs in Policy: "{vlan_list}"')
                                print(f'  - Missing VLANs: {vlans_not_in_domain_policy}')
                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                valid_vlan = False
                            if valid_vlan == True:
                                nativeVlan = ezfunctions.vlan_native_function(vlan_policy_list, vlan_list)
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
                    print(f"    MGMT VLAN       = {kwargs['mgmt_vlan']}")
                    print(f"    Migration VLAN  = {kwargs['migration_vlan']}")
                    print(f"    Storage VLAN    = {kwargs['storage_vlan']}")
                    print(f'    Data VLANs      = "{VlanList}"')
                    if len(fc_ports_in_use) > 0:
                        print(f'    VSAN Fabric A   = {kwargs["vsan_id_a"]}')
                        print(f'    VSAN Fabric B   = {kwargs["vsan_id_b"]}')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
                        if confirm_policy == 'Y' or confirm_policy == '':
                            #==============================================
                            # Configure Ethernet Adapter Policy
                            #==============================================
                            polVars = {}
                            polVars['name'] = 'VMware'
                            polVars['adapter_template'] = 'VMware'
                            kwargs['class_path'] = 'policies,ethernet_adapter'
                            kwargs = ezfunctions.ez_append(polVars, **kwargs)
                            #==============================================
                            # Configure Ethernet Network Control Policy
                            #==============================================
                            polVars = {}
                            polVars['name'] = neighbor_discovery.lower()
                            polVars['description'] = f'{neighbor_discovery} Ethernet Network Control Policy'
                            polVars['action_on_uplink_fail'] = "linkDown"
                            if neighbor_discovery == 'CDP': polVars['cdp_enable'] = True
                            else: polVars['cdp_enable'] = False
                            if neighbor_discovery == 'LLDP':
                                polVars['lldp_receive_enable'] = True
                                polVars['lldp_transmit_enable'] = True
                            else:
                                polVars['lldp_receive_enable'] = False
                                polVars['lldp_transmit_enable'] = False
                            polVars['mac_register_mode'] = "nativeVlanOnly"
                            polVars['mac_security_forge'] = "allow"
                            kwargs['class_path'] = 'policies,ethernet_network_control'
                            kwargs = ezfunctions.ez_append(polVars, **kwargs)
                            #==============================================
                            # Configure Ethernet Network Group Policies
                            #==============================================
                            polVars = {}
                            for x in ['mgmt', 'migration', 'storage', 'dvs']:
                                polVars['name'] = x
                                if re.search('mgmt|migration|storage', x):
                                    allowed_vlans = kwargs[f'{x}_vlan']
                                    native_vlan   = kwargs[f'{x}_vlan']
                                elif x == 'dvs':
                                    allowed_vlans = VlanList
                                    if not nativeVlan == '': native_vlan = nativeVlan
                                polVars['allowed_vlans'] = allowed_vlans
                                if not native_vlan == '': polVars['native_vlan'] = native_vlan
                                else:
                                    if not polVars.get('native_vlan') == None: polVars.pop('native_vlan')
                                # Add Policy Variables to immDict
                                kwargs['class_path'] = 'policies,ethernet_network_group'
                                kwargs = ezfunctions.ez_append(polVars, **kwargs)
                            #==============================================
                            # Configure Ethernet QoS Policy
                            #==============================================
                            polVars = {}
                            names = ['Bronze', 'Gold', 'Platinum', 'Silver']
                            for x in names:
                                polVars['name'] = x
                                polVars['description'] = f'{x} Ethernet QoS Policy'
                                polVars['burst'] = 10240
                                polVars['enable_trust_host_cos'] = False
                                polVars['priority'] = x
                                polVars['mtu'] = mtu
                                polVars['rate_limit'] = 0

                                # Add Policy Variables to immDict
                                kwargs['class_path'] = 'policies,ethernet_qos'
                                kwargs = ezfunctions.ez_append(polVars, **kwargs)
                            if len(fc_ports_in_use) > 0:
                                #==============================================
                                # Configure Fibre-Channel Adapter Policy
                                #==============================================
                                polVars = {}
                                polVars['name'] = 'VMware'
                                polVars['description'] = f'VMware Fibre-Channel Adapter Policy'
                                polVars['adapter_template'] = 'VMware'
                                kwargs['class_path'] = 'policies,fibre_channel_adapter'
                                kwargs = ezfunctions.ez_append(polVars, **kwargs)
                                #==============================================
                                # Configure Fibre-Channel Network Policy
                                #==============================================
                                polVars = {}
                                fabrics = ['a', 'b']
                                for fab in fabrics:
                                    polVars['name'] = f'vsan-{fab}'
                                    polVars['default_vlan'] = 0
                                    polVars['vsan_id'] = kwargs[f"vsan_id_{fab}"]
                                    kwargs['class_path'] = 'policies,fibre_channel_network'
                                    kwargs = ezfunctions.ez_append(polVars, **kwargs)
                                #==============================================
                                # Configure Fibre-Channel QoS Policy
                                #==============================================
                                polVars = {}
                                polVars['name'] = 'fc-qos'
                                polVars['burst'] = 10240
                                polVars['max_data_field_size'] = 2112
                                polVars['rate_limit'] = 0
                                kwargs['class_path'] = 'policies,fibre_channel_qos'
                                kwargs = ezfunctions.ez_append(polVars, **kwargs)
                            Order = 0
                            if len(fc_ports_in_use) > 0:
                                #==============================================
                                # Configure SAN Connectivity Policy
                                #==============================================
                                polVars = {}
                                polVars['name'] = f'scp'
                                polVars['target_platform'] = 'FIAttached'
                                polVars['vhbas'] = [{
                                    'fibre_channel_adapter_policy':'VMware',
                                    'fibre_channel_network_policies':['vsan-a', 'vsan-b'],
                                    'fibre_channel_qos_policy':'fc-qos',
                                    'names':['vhba-a', 'vhba-b'],
                                    'placement_pci_order':[Order, Order + 1],
                                    'wwpn_allocation_type':'POOL',
                                    'wwpn_pools':[f'wwpn-a', f'wwpn-b']
                                }]
                                polVars['wwnn_allocation_type'] = 'POOL'
                                polVars['wwnn_pool'] = 'wwnn'
                                Order += 2
                                kwargs['class_path'] = 'policies,san_connectivity'
                                kwargs = ezfunctions.ez_append(polVars, **kwargs)
                            #==============================================
                            # Configure LAN Connectivity Policy
                            #==============================================
                            polVars = {}
                            polVars['name'] = 'vmware-lcp'
                            polVars['target_platform'] = 'FIAttached'
                            polVars['vnics'] = []
                            names = ['mgmt_Silver', 'migration_Bronze', 'storage_Platinum', 'dvs_Gold']
                            for nam in names:
                                vname = nam.split('_')[0]
                                qos = nam.split('_')[1]
                                vnic = {
                                    'ethernet_adapter_policy':'VMware',
                                    'ethernet_network_control_policy':neighbor_discovery.lower(),
                                    'ethernet_network_group_policy':vname,
                                    'ethernet_qos_policy':qos,
                                    'mac_address_pools':[f'{vname}-a',f'{vname}-b',],
                                    'names':[f'{vname}-a',f'{vname}-b',],
                                    'placement_pci_order':[Order, Order + 1],
                                }
                                polVars['vnics'].append(vnic)
                                Order += 2
                            #==============================================
                            # Add Policy Variables to immDict
                            #==============================================
                            kwargs['class_path'] = 'policies,lan_connectivity'
                            kwargs = ezfunctions.ez_append(polVars, **kwargs)
                            configure_loop = True
                            policy_loop = True
                            valid_confirm = True
                        elif confirm_policy == 'N':
                            policy_type = 'LAN/SAN Policies'
                            ezfunctions.message_starting_over(policy_type)
                            valid_confirm = True
                        else: ezfunctions.message_invalid_y_or_n('short')
            elif configure == 'N': configure_loop = True
            else: ezfunctions.message_invalid_y_or_n('short')
        return kwargs

    #==============================================
    # Pools
    #==============================================
    def pools(self, **kwargs):
        baseRepo       = kwargs['args'].dir
        configure_loop = False
        org            = self.org
        jsonData       = kwargs['jsonData']
        path_sep       = kwargs['path_sep']
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  The Quick Deployment Module - Pools, will configure pools for a UCS Server Profile')
            print(f'  connected to an IMM Domain.\n')
            print(f'  This wizard will save the output for these pools in the following files:\n')
            print(f'  - {baseRepo}{path_sep}{org}{path_sep}{self.type}/pools.yaml')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to run the Quick Deployment Module - Pools?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                polVars = {}
                loop_count = 1
                policy_loop = False
                while policy_loop == False:
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  Below are the Questions that will be asked by the Pools Portion of the wizard.')
                    print(f'  Note: IP Pools will be configured with the IMC Access Policy.')
                    print(f'  The following pools will be configured with the prefix value:')
                    print(f'    * Note: (Policy maximum 1024 addresses per pool in Intersight will be assigned):')
                    print(f'    * MAC Pools')
                    print(f'      - dvs-a:           00:25:B5:[prefix]:G0:00, size: 1024')
                    print(f'      - dvs-b:           00:25:B5:[prefix]:H0:00, size: 1024')
                    print(f'      - mgmt-a:          00:25:B5:[prefix]:A0:00, size: 1024')
                    print(f'      - mgmt-b:          00:25:B5:[prefix]:B0:00, size: 1024')
                    print(f'      - migration-a:     00:25:B5:[prefix]:C0:00, size: 1024')
                    print(f'      - migration-b:     00:25:B5:[prefix]:D0:00, size: 1024')
                    print(f'      - storage-a:       00:25:B5:[prefix]:E0:00, size: 1024')
                    print(f'      - storage-b:       00:25:B5:[prefix]:F0:00, size: 1024')
                    print(f'    * UUID Pool')
                    print(f'      - uuid:        000025B5-[prefix]00-0000, size: 1024')
                    print(f'    * WWNN Pool')
                    print(f'      - wwnn:   20:00:00:25:B5:[prefix]:00:00, size: 1024')
                    print(f'    * WWPN Pools')
                    print(f'      - wwpn-a: 20:00:00:25:B5:[prefix]:A0:00, size: 1024')
                    print(f'      - wwpn-b: 20:00:00:25:B5:[prefix]:B0:00, size: 1024')
                    print(f'\n-------------------------------------------------------------------------------------------\n')

                    kwargs['jData'] = deepcopy({})
                    kwargs['jData']['default']     = '00'
                    kwargs['jData']['description'] = 'Prefix to assign to Pools'
                    kwargs['jData']['pattern']     = '^[0-9a-zA-Z]{2}$'
                    kwargs['jData']['varInput']    = 'What is the 2 Digit (Hex) Prefix to assign to the MAC,'\
                        ' UUID, WWNN, and WWPN Pools?'
                    kwargs['jData']['varName']     = 'Pool Prefix'
                    pool_prefix = ezfunctions.varStringLoop(**kwargs)
                    pool_prefix = pool_prefix.upper()

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  Pool Prefix for the Pools = "{pool_prefix}"')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
                        if confirm_policy == 'Y' or confirm_policy == '':
                            #==============================================
                            # Configure MAC Pools
                            #==============================================
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
                                    polVars['name'] = f'{i}-{fab}'
                                    pool_from = f'00:25:B5:{pool_prefix}:{key_id}0:00'
                                    polVars['mac_blocks'] = [{'from':pool_from, 'size':1024}]
                                    kwargs['class_path'] = 'pools,mac'
                                    kwargs = ezfunctions.ez_append(polVars, **kwargs)
                            #==============================================
                            # Configure UUID Pool
                            #==============================================
                            polVars = {}
                            polVars['name'] = 'uuid'
                            polVars['description'] = f'uuid UUID Pool'
                            polVars['prefix'] = f'000025B5-{pool_prefix}00-0000'
                            polVars['uuid_blocks'] = [{'from':'0000-000000000000', 'size':1024}]
                            kwargs['class_path'] = 'pools,uuid'
                            kwargs = ezfunctions.ez_append(polVars, **kwargs)
                            #==============================================
                            # Configure WWNN Pool
                            #==============================================
                            polVars = {}
                            polVars['name'] = 'wwnn'
                            pool_from = f'20:00:00:25:B5:{pool_prefix}:00:00'
                            polVars['id_blocks'] = [{'from':pool_from, 'size':1024}]
                            kwargs['class_path'] = 'pools,wwnn'
                            kwargs = ezfunctions.ez_append(polVars, **kwargs)
                            #==============================================
                            # Configure WWPN Pools
                            #==============================================
                            for fab in fabrics:
                                polVars['name'] = f'wwpn-{fab}'
                                pool_from = f'20:00:00:25:B5:{pool_prefix}:{fab.upper()}0:00'
                                polVars['id_blocks'] = [{'from':pool_from, 'size':1024,}]
                                kwargs['class_path'] = 'pools,wwpn'
                                kwargs = ezfunctions.ez_append(polVars, **kwargs)
                            configure_loop = True
                            policy_loop = True
                            valid_confirm = True
                        elif confirm_policy == 'N':
                            policy_type = 'pools'
                            ezfunctions.message_starting_over(policy_type)
                            valid_confirm = True
                        else: ezfunctions.message_invalid_y_or_n('short')
            elif configure == 'N': configure_loop = True
            else: ezfunctions.message_invalid_y_or_n('short')
        return kwargs

    #==============================================
    # Server Policies for Domain and Standalone
    #==============================================
    def server_policies(self, **kwargs):
        baseRepo       = kwargs['args'].dir
        configure_loop = False
        jsonData       = kwargs['jsonData']
        org            = self.org
        path_sep       = kwargs['path_sep']
        server_type    = kwargs['server_type']
        vlan_list      = kwargs['vlan_list']

        def ip_pool_loop(kvmband, primary_dns, secondary_dns, jsonData, **kwargs):
            if kvmband == 'inband': network = '198.18.0'
            else: network = '198.18.1'
            kwargs['multi_select'] = False
            jsonVars = jsonData['ippool.IpV4Config']['allOf'][1]['properties']
            kwargs['jData'] = deepcopy(jsonVars['Gateway'])
            kwargs['jData']['default']  = f'{network}.1'
            kwargs['jData']['varInput'] = f'What is the Gateway for the KVM {kvmband} IP Pool?:'
            kwargs['jData']['varName']  = 'Gateway'
            gateway = ezfunctions.varStringLoop(**kwargs)

            kwargs['jData'] = deepcopy(jsonVars['Netmask'])
            kwargs['jData']['default']  = '255.255.255.0'
            kwargs['jData']['varInput'] = f'What is the Netmask for the KVM {kvmband} IP Pool?:'
            kwargs['jData']['varName']  = 'Netmask'
            netmask = ezfunctions.varStringLoop(**kwargs)

            jsonVars = jsonData['ippool.IpV4Block']['allOf'][1]['properties']
            kwargs['jData'] = deepcopy(jsonVars['From'])
            kwargs['jData']['default']  = f'{network}.10'
            kwargs['jData']['varInput'] = f'What is the First IP Address for the KVM {kvmband} IP Pool?'
            kwargs['jData']['varName']  = 'Beginning IP Address'
            pool_from = ezfunctions.varStringLoop(**kwargs)

            kwargs['jData'] = deepcopy(jsonVars['To'])
            kwargs['jData']['default']  = f'{network}.254'
            kwargs['jData']['varInput'] = f'What is the Last IP Address for the KVM {kvmband} IP Pool?'
            kwargs['jData']['varName']  = 'Ending IP Address'
            pool_to = ezfunctions.varStringLoop(**kwargs)

            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  KVM {kvmband} IP Pool Variables:"')
            print(f'    Gateway       = "{gateway}"')
            print(f'    Netmask       = "{netmask}"')
            print(f'    Primary DNS   = "{primary_dns}"')
            print(f'    Secondary DNS = "{secondary_dns}"')
            print(f'    Starting IP   = "{pool_from}"')
            print(f'    Ending IP     = "{pool_to}"')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            valid_confirm = False
            while valid_confirm == False:
                confirm_policy = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
                if confirm_policy == 'Y' or confirm_policy == '':
                    #==============================================
                    # Configure IP Pool
                    #==============================================
                    polVars = {}
                    if kvmband == 'inband': polVars['name'] = f'kvm-{kvmband}'
                    else: polVars['name'] = f'kvm-oob'
                    pool_size = int(ipaddress.IPv4Address(pool_to)) - int(ipaddress.IPv4Address(pool_from)) + 1
                    polVars['ipv4_blocks'] = [{'from':pool_from, 'size':pool_size}]
                    polVars['ipv4_configuration'] = [{
                        'gateway':gateway, 'netmask':netmask, 'primary_dns':primary_dns, 'secondary_dns':secondary_dns
                    }]
                    kwargs['primary_dns'] = primary_dns
                    kwargs['secondary_dns'] = secondary_dns
                    kwargs['class_path'] = 'pools,ip'
                    kwargs = ezfunctions.ez_append(polVars, **kwargs)
            return kwargs

        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  The Quick Deployment Module - Configure Policies for a UCS Server Profile.\n')
            print(f'  This wizard will save the output for these Policies in the following files:\n')
            print(f'  - {baseRepo}{path_sep}{org}{path_sep}{self.type}/environment.yaml')
            print(f'  - {baseRepo}{path_sep}{org}{path_sep}{self.type}/management.yaml')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to run the Quick Deployment Module - Policy Configuration?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                loop_count = 1
                policy_loop = False
                while policy_loop == False:
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  Below are the Questions that will be asked by the Policies Portion of the wizard.')
                    print(f'   - IP Pool(s) for IMC/KVM Access')
                    print(f'     * Gateway')
                    print(f'     * Netmask')
                    print(f'     * Starting IP Address for the Pool')
                    print(f'     * Ending IP Address for the Pool')
                    print(f'     * Primary DNS Server')
                    print(f'     * Secondary DNS Server (optional)')
                    print(f'   - IMC Policy with IP Pools for Inband and Ooband.')
                    print(f'     * For a inband Policy, VLAN ID for IMC Access Policy is required.')
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
                    if kwargs['server_type'] == 'FIAttached':
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        print(f'  Now Starting the IMC Access Policy Section.')
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        #==============================================
                        # Prompt User for IP Pool DNS Servers
                        #==============================================
                        kwargs['jData'] = deepcopy(jsonVars['PrimaryDns'])
                        kwargs['jData']['default']  = '208.67.220.220'
                        kwargs['jData']['varInput'] = 'What is the Primary DNS for the KVM IP Pool(s)?:'
                        kwargs['jData']['varName']  = 'Primary Dns'
                        primary_dns = ezfunctions.varStringLoop(**kwargs)

                        kwargs['jData'] = deepcopy(jsonVars['SecondaryDns'])
                        kwargs['jData']['varInput'] = 'What is the Secondary DNS for the KVM IP Pool(s)? [press enter to skip]:'
                        kwargs['jData']['varName']  = 'Secondary Dns'
                        secondary_dns = ezfunctions.varStringLoop(**kwargs)

                        jsonVars = jsonData['access.Policy']['allOf'][1]['properties']
                        kwargs['jData'] = deepcopy(jsonVars['ConfigurationType'])
                        kwargs['jData']['default']     = True
                        kwargs['jData']['varInput']    = f'Would you like to configure an Inband IP Pool for the KVM Policy?'
                        kwargs['jData']['varName']     = 'Inband IP Pool'
                        inband_pool = ezfunctions.varBoolLoop(**kwargs)
                        if inband_pool == True:
                            kwargs = ip_pool_loop('inband', primary_dns, secondary_dns, jsonData, **kwargs)
                            valid = False
                            while valid == False:
                                kwargs['jData'] = deepcopy({})
                                kwargs['jData']['default']     = 4
                                kwargs['jData']['description'] = 'IMC Access VLAN Identifier'
                                kwargs['jData']['maximum']     = 4094
                                kwargs['jData']['minimum']     = 4
                                kwargs['jData']['varInput']    = 'Enter the VLAN ID for the IMC Access Policy.'
                                kwargs['jData']['varName']     = 'IMC Access Policy VLAN ID'
                                inband_vlan_id = ezfunctions.varNumberLoop(**kwargs)
                                if server_type == 'FIAttached':
                                    valid = ezfunctions.validate_vlan_in_policy(vlan_policy_list, inband_vlan_id)
                                else: valid = True
                        kwargs['jData'] = deepcopy(jsonVars['ConfigurationType'])
                        kwargs['jData']['default']     = True
                        kwargs['jData']['varInput']    = f'Would you like to configure an Out-of-Band IP Pool for the KVM Policy?'
                        kwargs['jData']['varName']     = 'Out-of-Band IP Pool'
                        oob_pool = ezfunctions.varBoolLoop(**kwargs)
                        if oob_pool == True:
                            ip_pool_loop('out_of_band', primary_dns, secondary_dns, jsonData, **kwargs)
                    #==============================================
                    # Prompt User for IPMI Encryption Key
                    #==============================================
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  Need to obtain the IPMI Key for IPMI over LAN Policy Encryption.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    kwargs['Variable'] = 'ipmi_key'
                    kwargs = ezfunctions.sensitive_var_value(**kwargs)
                    #==============================================
                    # Prompt User for Local User Policy
                    #==============================================
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  Now Starting the Local User Policy Section.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    kwargs['enforce_strong_password'] = True
                    kwargs['jData'] = deepcopy({})
                    kwargs['jData']['default']     = True
                    kwargs['jData']['description'] = 'Local User Configuration.'
                    kwargs['jData']['varInput']    = f'Would you like to configure the Local users Policy?'
                    kwargs['jData']['varName']     = 'Local Users'
                    question = ezfunctions.varBoolLoop(**kwargs)
                    if question == True: kwargs = ezfunctions.local_users_function(**kwargs)
                    #==============================================
                    # Prompt User for SNMP Policy Parameters
                    #==============================================
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  Now Starting the SNMP Policy Section.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    # Pull in the Policies for SNMP Policies
                    jsonVars = jsonData['snmp.Policy']['allOf'][1]['properties']
                    #==============================================
                    # Prompt User for SNMP System Contact
                    #==============================================
                    kwargs['jData'] = deepcopy(jsonVars['SysContact'])
                    kwargs['jData']['description'] = jsonVars['SysContact']['description'] + \
                        'Note: Enter a string up to 64 characters, such as an email address or a name and telephone number.'
                    kwargs['jData']['pattern']  = '.*'
                    kwargs['jData']['minimum']  = 0
                    kwargs['jData']['varInput'] = 'SNMP System Contact:'
                    kwargs['jData']['varName']  = 'SNMP System Contact'
                    kwargs['system_contact'] = ezfunctions.varStringLoop(**kwargs)
                    #==============================================
                    # Prompt User for SNMP System Location
                    #==============================================
                    kwargs['jData'] = deepcopy(jsonVars['SysLocation'])
                    kwargs['jData']['minimum']  = 0
                    kwargs['jData']['pattern']  = '.*'
                    kwargs['jData']['varInput'] = 'What is the Location of the host on which the SNMP agent (server) runs?'
                    kwargs['jData']['varName']  = 'SNMP System Location'
                    kwargs['system_location'] = ezfunctions.varStringLoop(**kwargs)
                    snmp_loop = False
                    kwargs['snmp_users'] = []
                    kwargs['snmp_traps'] = []
                    while snmp_loop == False:
                        question = input(f'Would you like to configure an SNMPv3 User?  Enter "Y" or "N" [Y]: ')
                        if question == '' or question == 'Y':
                            kwargs = ezfunctions.snmp_users(**kwargs)
                            snmp_loop = True
                        elif question == 'N': snmp_loop = True
                        else: ezfunctions.message_invalid_y_or_n('short')
                    snmp_loop = False
                    if len(kwargs['snmp_users']) > 0:
                        while snmp_loop == False:
                            question = input(f'Would you like to configure SNMP Trap Destionations?  Enter "Y" or "N" [Y]: ')
                            if question == '' or question == 'Y':
                                kwargs = ezfunctions.snmp_trap_servers(**kwargs)
                                snmp_loop = True
                            elif question == 'N': snmp_loop = True
                            else: ezfunctions.message_invalid_y_or_n('short')
                    #==============================================
                    # Prompt User for Syslog Policy
                    #==============================================
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  Now Starting the Syslog Policy Section.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    syslog_loop = False
                    while syslog_loop == False:
                        question = input(f'Do you want to configure Remote Syslog Servers?  Enter "Y" or "N" [Y]: ')
                        if question == '' or question == 'Y':
                            jsonVars = jsonData['syslog.LocalClientBase']['allOf'][1]['properties']
                            kwargs['jData'] = deepcopy(jsonVars['MinSeverity'])
                            kwargs['jData']['varType'] = 'Syslog Local Minimum Severity'
                            min_severity = ezfunctions.variablesFromAPI(**kwargs)
                            kwargs = ezfunctions.syslog_servers(**kwargs)
                            syslog_loop = True
                        elif question == 'N':
                            min_severity = 'warning'
                            kwargs['remote_logging'] = {
                                'server1':{'enable':False,'hostname':'0.0.0.0','minimum_severity':'warning'},
                                'server2':{'enable':False,'hostname':'0.0.0.0','minimum_severity':'warning'}
                            }
                            syslog_loop = True
                        else: ezfunctions.message_invalid_y_or_n('short')
                    #==============================================
                    # Prompt User for Allow Tunneled KVM Support
                    #==============================================
                    jsonVars = jsonData['kvm.Policy']['allOf'][1]['properties']
                    kwargs['jData'] = deepcopy(jsonVars['TunneledKvmEnabled'])
                    kwargs['jData']['varInput'] = f'Do you want to enable Tunneled KVM in the KVM Policy?'
                    kwargs['jData']['varName']  = 'Tunneled KVM'
                    allow_tunneled_vkvm = ezfunctions.varBoolLoop(**kwargs)
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  Policy Variables:')
                    if len(kwargs['local_users']) > 0:
                        print(textwrap.indent(yaml.dump(kwargs['local_users'], Dumper=MyDumper, default_flow_style=False
                        ), " "*3, predicate=None))
                    print(f'    System Contact   = "{kwargs["system_contact"]}"')
                    print(f'    System Locaction = "{kwargs["system_location"]}"')
                    print(f'    SNMP Trap Destinations:')
                    if len(kwargs['snmp_traps']) > 0:
                        print(textwrap.indent(yaml.dump({'snmp_traps':kwargs['snmp_traps']
                        }, Dumper=MyDumper, default_flow_style=False), " "*3, predicate=None))
                    print(f'    SNMP Users:')
                    if len(kwargs['snmp_users']) > 0:
                        print(textwrap.indent(yaml.dump({'snmp_users':kwargs['snmp_users']
                        }, Dumper=MyDumper, default_flow_style=False), " "*3, predicate=None))
                    print(f'    Syslog Remote Clients:')
                    print(textwrap.indent(yaml.dump({'remote_logging':kwargs['remote_logging']
                    }, Dumper=MyDumper, default_flow_style=False), " "*3, predicate=None))
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
                        if confirm_policy == 'Y' or confirm_policy == '':
                            if kwargs['server_type'] == 'FIAttached':
                                #==============================================
                                # Configure IMC Access Policy
                                #==============================================
                                polVars = {}
                                ip_pool = kwargs['immDict']['orgs'][org]['pools']['ip'][0]['name']
                                polVars['name'] = 'kvm'
                                if inband_pool == True:
                                    polVars[f'inband_ip_pool'] = 'kvm-inband'
                                    polVars['inband_vlan_id'] = inband_vlan_id
                                if oob_pool == True:
                                    polVars[f'out_of_band_ip_pool'] = 'kvm-oob'
                                kwargs['class_path'] = 'policies,imc_access'
                                kwargs = ezfunctions.ez_append(polVars, **kwargs)
                                kwargs['imc_access_policy'] = polVars['name']
                            #==============================================
                            # Configure IPMI over LAN Policy
                            #==============================================
                            polVars = {}
                            polVars['name'] = f'ipmi'
                            polVars['enabled'] = True
                            kwargs['class_path'] = 'policies,ipmi_over_lan'
                            kwargs = ezfunctions.ez_append(polVars, **kwargs)
                            #==============================================
                            # Configure Local User Policy
                            #==============================================
                            polVars = {}
                            polVars['name'] = f'local_users'
                            polVars['users'] = kwargs['local_users']
                            kwargs['class_path'] = 'policies,local_user'
                            kwargs = ezfunctions.ez_append(polVars, **kwargs)
                            #==============================================
                            # Configure Power Policy
                            #==============================================
                            polVars = {}
                            names = ['5108', '9508', 'Server']
                            for name in names:
                                polVars['allocated_budget'] = 0
                                polVars['name'] = name
                                if name == 'Server': polVars['power_restore'] = 'LastState'
                                elif name == '9508': polVars['power_allocation'] = 8400
                                polVars['power_redundancy'] = 'Grid'
                                kwargs['class_path'] = 'policies,power'
                                kwargs = ezfunctions.ez_append(polVars, **kwargs)
                            #==============================================
                            # Configure Serial over LAN Policy
                            #==============================================
                            polVars = {}
                            polVars['name'] = 'sol'
                            polVars['description'] = f'{name} Serial over LAN Policy'
                            polVars['enabled'] = True
                            kwargs['class_path'] = 'policies,serial_over_lan'
                            kwargs = ezfunctions.ez_append(polVars, **kwargs)
                            #==============================================
                            # Configure SNMP Policy
                            #==============================================
                            polVars = {}
                            names = ['snmp', 'snmp-domain']
                            for name in names:
                                polVars['name'] = name
                                polVars['enable_snmp'] = True
                                polVars['system_contact'] = kwargs['system_contact']
                                polVars['system_location'] = kwargs['system_location']
                                polVars['snmp_traps'] = kwargs['snmp_traps']
                                polVars['snmp_users'] = kwargs['snmp_users']
                                kwargs['class_path'] = 'policies,snmp'
                                kwargs = ezfunctions.ez_append(polVars, **kwargs)
                            #==============================================
                            # Configure Syslog Policy
                            #==============================================
                            polVars = {}
                            names = ['syslog', 'syslog-domain']
                            for name in names:
                                polVars['name']               = name
                                polVars['local_min_severity'] = min_severity
                                polVars['remote_logging']     = kwargs['remote_logging']

                                # Add Policy Variables to immDict
                                kwargs['class_path'] = 'policies,syslog'
                                kwargs = ezfunctions.ez_append(polVars, **kwargs)
                            #==============================================
                            # Configure Thermal Policy
                            #==============================================
                            polVars = {}
                            names = ['5108', '9508']
                            for name in names:
                                polVars['name'] = name
                                polVars['fan_control_mode'] = 'Balanced'

                                # Add Policy Variables to immDict
                                kwargs['class_path'] = 'policies,thermal'
                                kwargs = ezfunctions.ez_append(polVars, **kwargs)
                            #==============================================
                            # Configure Virtual KVM Policy
                            #==============================================
                            polVars = {}
                            polVars['name'] = 'vkvm'
                            polVars['allow_tunneled_vkvm'] = allow_tunneled_vkvm
                            kwargs['class_path'] = 'policies,virtual_kvm'
                            kwargs = ezfunctions.ez_append(polVars, **kwargs)
                            #==============================================
                            # Configure Virtual Media Policy
                            #==============================================
                            polVars = {}
                            polVars['name'] = 'vmedia'
                            polVars['enable_virtual_media_encryption'] = True
                            kwargs['class_path'] = 'policies,virtual_media'
                            kwargs = ezfunctions.ez_append(polVars, **kwargs)
                            configure_loop = True
                            policy_loop = True
                            valid_confirm = True
                        elif confirm_policy == 'N':
                            policy_type = 'Server Policies'
                            ezfunctions.message_starting_over(policy_type)
                            valid_confirm = True
                        else: ezfunctions.message_invalid_y_or_n('short')
            elif configure == 'N': configure_loop = True
            else: ezfunctions.message_invalid_y_or_n('short')
        return kwargs

    #==============================================
    # UCS Server Profiles and Templates
    #==============================================
    def server_profiles(self, **kwargs):
        baseRepo        = kwargs['args'].dir
        ezData          = kwargs['ezData']
        fc_ports_in_use = kwargs['fc_ports_in_use']
        org             = self.org
        path_sep        = kwargs['path_sep']
        configure_loop  = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  The Quick Deployment Module - Domain Policies, will configure pools for a UCS Domain ')
            print(f'  Profile.\n')
            print(f'  This wizard will save the output for these pools in the following files:\n')
            print(f'  - {baseRepo}{path_sep}{org}{path_sep}{self.type}/ucs_server_profile_templates.yaml')
            print(f'  - {baseRepo}{path_sep}{org}{path_sep}{self.type}/ucs_server_profiles.yaml')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to run the Quick Deployment Module - Server Profiles Configuration?  \n'\
                'Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                policy_loop = False
                while policy_loop == False:
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  Below are the Questions that will be asked by the Server Profiles Portion of the wizard.')
                    print(f'   - Number of Servers you are going to deploy.')
                    print(f'   - Name of the Server Profile(s).')
                    print(f'   - Serial Number of the Server Profile(s).')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    #==============================================
                    # Prompt for Generation of UCS Servers
                    #==============================================
                    jsonVars = ezData['ezimm']['allOf'][1]['properties']['policies']['server.Generation']
                    kwargs['jData'] = deepcopy(jsonVars['systemType'])
                    kwargs['jData']['varType'] = 'Generation of UCS Server'
                    ucs_generation = ezfunctions.variablesFromAPI(**kwargs)
                    #==============================================
                    # Determine if the Trusted Platform Module is Installed
                    #==============================================
                    if ucs_generation == 'M5':
                        kwargs['jData'] = deepcopy({})
                        kwargs['jData']['default'] = False
                        kwargs['jData']['description'] = 'Flag to Determine if the Server has TPM Installed.'
                        kwargs['jData']['varInput'] = f'Is a Trusted Platform Module installed in this Server(s)'\
                            'and do you want to enable secure-boot?'
                        kwargs['jData']['varName'] = 'TPM Installed'
                        tpm_installed = ezfunctions.varBoolLoop(**kwargs)
                    else: tpm_installed = True
                    #==============================================
                    # Configure the Template Name
                    #==============================================
                    boot_type = kwargs['boot_type']
                    if boot_type == 'm2': template_name = 'M2-pxe'
                    elif boot_type == 'raid1': template_name = 'Raid1-pxe'
                    else: template_name = 'pxe'
                    #==============================================
                    # Configure UCS Server Profiles
                    #==============================================
                    kwargs['multi_select'] = False
                    kwargs['jData'] = deepcopy({})
                    kwargs['jData']['default']     = 1
                    kwargs['jData']['description'] = f'Number of Server Profiles.'
                    kwargs['jData']['maximum']     = 160
                    kwargs['jData']['minimum']     = 1
                    kwargs['jData']['varInput']    = f'Enter the Number of Server Profiles to Create:'
                    kwargs['jData']['varName']     = 'Server Count'
                    server_count = ezfunctions.varNumberLoop(**kwargs)
                    #==============================================
                    # Prompt User for Server Name Prefix
                    #==============================================
                    kwargs['jData'] = deepcopy({})
                    kwargs['jData']['default']      = True
                    kwargs['jData']['description']  = 'Server Name Prefix'
                    kwargs['jData']['varInput']     = f'Do you want to use a Server Name Prefix for the Server Names?'
                    kwargs['jData']['varName']      = 'Server Name Prefix'
                    question = ezfunctions.varBoolLoop(**kwargs)
                    policy_type     = 'UCS Server Profiles'
                    if question == True:
                        name = 'server'
                        valid = False
                        while valid == False:
                            prefix = input(f'What is the Prefix for the {policy_type}?  [{name}]: ')
                            if prefix == '': prefix = '%s' % (name)
                            valid = validating.name_rule(f'{policy_type} Prefix', prefix, 1, 62)
                            if valid == True: server_prefix = prefix
                    else: server_prefix = ''
                    #==============================================
                    # Prompt for Server Profile Names
                    #==============================================
                    targets = []
                    rangex = int(server_count) + 1
                    for x in range(1,rangex):
                        x = x
                        if not server_prefix == '':
                            name    = ezfunctions.policy_name(f'{server_prefix}-{x}', policy_type)
                        else: name  = ezfunctions.policy_name(f'server-{x}', policy_type)
                        #==============================================
                        # Prompt for Server Serial Number or Skip
                        #==============================================
                        kwargs['jData'] = deepcopy({})
                        kwargs['jData']['description'] = f'Serial Number of the Server Profile {name}.'
                        kwargs['jData']['maximum'] = 11
                        kwargs['jData']['minimum'] = 11
                        kwargs['jData']['pattern'] = '^[A-Z]{3}[2-3][\\d]([0][1-9]|[1-4][0-9]|[5][1-3])[\\dA-Z]{4}$'
                        kwargs['jData']['varInput'] = f'What is the Serial Number of {name}? [press enter to skip]:'
                        kwargs['jData']['varName'] = 'Serial Number'
                        serial_number = ezfunctions.varStringLoop(**kwargs)
                        if serial_number == '': serial_number = 'unknown'
                        targets.append({'name':name,'serial_number':serial_number})
                    #==============================================
                    # Configure Server Profiles
                    #==============================================
                    polVars = {}
                    polVars['targets'] = targets
                    polVars['ucs_server_profile_template'] = template_name
                    kwargs['class_path'] = 'profiles,server'
                    kwargs = ezfunctions.ez_append(polVars, **kwargs)
                    #==============================================
                    # Configure Server Template
                    #==============================================
                    polVars = {}
                    if ucs_generation == 'M5' and tpm_installed == True:
                        polVars['bios_policy'] = 'M5-virtualization-tpm'
                    elif ucs_generation == 'M5': polVars['bios_policy'] = 'M5-virtualization'
                    elif ucs_generation == 'M6': polVars['bios_policy'] = 'M6-virtualization-tpm'
                    polVars['boot_order_policy'] = template_name
                    polVars['description'] = f'{template_name} Server Profile Template'
                    polVars['name'] = template_name
                    polVars['uuid_pool'] = 'uuid'
                    polVars['virtual_media_policy'] = 'vmedia'
                    polVars['ipmi_over_lan_policy'] = f'ipmi'
                    polVars['local_user_policy'] = f'local_users'
                    polVars['serial_over_lan_policy'] = 'sol'
                    polVars['snmp_policy'] = 'snmp'
                    polVars['syslog_policy'] = 'syslog'
                    polVars['virtual_kvm_policy'] = 'vkvm'
                    polVars['sd_card_policy'] = ''
                    if boot_type == 'm2': polVars['storage_policy'] = 'M2-Raid'
                    elif boot_type == 'raid1': polVars['storage_policy'] = 'Raid1'
                    else: polVars['storage_policy'] = ''
                    polVars['lan_connectivity_policy'] = 'vmware-lcp'
                    if len(fc_ports_in_use) > 0:
                        polVars['san_connectivity_policy'] = f'scp'
                    if kwargs['server_type'] == 'FIAttached':
                        polVars['certificate_management_policy'] = ''
                        polVars['imc_access_policy'] = f'{org}'
                        polVars['power_policy'] = 'Server'
                        polVars['target_platform'] = 'FIAttached'
                    if kwargs['server_type'] == 'Standalone':
                        polVars['adapter_configuration_policy'] = f'acp'
                        polVars['device_connector_policy'] = f'dcp'
                        polVars['ldap_policy'] = f'ldap'
                        polVars['network_connectivity_policy'] = f'dns'
                        polVars['ntp_policy'] = f'ntp'
                        polVars['persistent_memory_policy'] = f'pmem'
                        polVars['smtp_policy'] = f'smtp'
                        polVars['ssh_policy'] = f'ssh'
                        polVars['target_platform'] = 'Standalone'
                    #==============================================
                    # Add Policy Variables to immDict
                    #==============================================
                    kwargs['class_path'] = 'templates,server'
                    kwargs = ezfunctions.ez_append(polVars, **kwargs)
                    policy_loop = True
                    configure_loop = True
            elif configure == 'N': configure_loop = True
            else: ezfunctions.message_invalid_y_or_n('short')
        # Return kwargs
        return kwargs
        
    #==============================================
    # Standalone Server Policies
    #==============================================
    def standalone_policies(self, **kwargs):
        baseRepo       = kwargs['args'].dir
        configure_loop = False
        ezData         = kwargs['ezData']
        jsonData       = kwargs['jsonData']
        name_prefix    = self.name_prefix
        org            = self.org
        path_sep       = kwargs['path_sep']
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  The Quick Deployment Module - Standalone Policies.\n')
            print(f'  This wizard will save the output for these policies in the following files:\n')
            print(f'  - {baseRepo}{path_sep}{org}{path_sep}{self.type}{path_sep}management.yaml')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to run the Quick Deployment Module - Standalone Policy Configuration?'\
                '  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                polVars = {}
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
            elif configure == 'N':
                configure_loop = True
            else: ezfunctions.message_invalid_y_or_n('short')
        if configure == 'Y' or configure == '': configure = True
        elif configure == 'N': configure = False
        return configure

#==============================================
# Function - Prompt User to Select Policy
#==============================================
def policy_select_loop(self, **kwargs):
    ezData      = kwargs['ezData']
    policy      = kwargs['policy']
    name        = kwargs['name']
    name_prefix = self.name_prefix
    org         = kwargs['org']
    loop_valid  = False
    while loop_valid == False:
        create_policy = True
        kwargs['inner_policy'] = policy.split('.')[1]
        kwargs['inner_type']   = policy.split('.')[0]
        kwargs['inner_var']    = policy.split('.')[2]
        inner_policy = kwargs['inner_policy']
        inner_type   = kwargs['inner_type']
        inner_var    = kwargs['inner_var']
        policy_description = ezfunctions.mod_pol_description(inner_var)
        kwargs = ezfunctions.policies_parse(inner_type, inner_policy, **kwargs)
        if not len(kwargs['policies']) > 0:
            valid = False
            while valid == False:
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'   There was no {policy_description} found.')
                print(f'\n-------------------------------------------------------------------------------------------\n')
                if kwargs['allow_opt_out'] == True:
                    Question = input(f'Do you want to create a(n) {policy_description}?  Enter "Y" or "N" [Y]: ')
                    if Question == '' or Question == 'Y': create_policy = True; valid = True
                    elif Question == 'N': create_policy = False; valid = True; return kwargs
                else: create_policy = True; valid = True
        else:
            kwargs = ezfunctions.choose_policy(inner_policy, **kwargs)
            if kwargs['policy'] == 'create_policy': create_policy = True
            elif kwargs['policy'] == '' and kwargs['allow_opt_out'] == True:
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
        if ncount == 5: print(name_prefix)
        # Create Policy if Option was Selected
        if create_policy == True:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  Starting module to create {policy_description} in {org}')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            list_lansan   = ezData['ezimm']['allOf'][1]['properties']['list_lansan']['enum']
            list_policies = ezData['ezimm']['allOf'][1]['properties']['list_policies']['enum']
            if re.search('pool$', inner_var):
                kwargs = eval(f"pools.pools(name_prefix, org, inner_type).{inner_policy}(**kwargs)")
            elif inner_policy in list_lansan:
                kwargs = eval(f"lansan.policies(name_prefix, org, inner_type).{inner_policy}(**kwargs)")
            elif inner_policy in list_policies:
                kwargs = eval(f"policies.policies(name_prefix, org, inner_type).{inner_policy}(**kwargs)")
