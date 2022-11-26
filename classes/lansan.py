from copy import deepcopy
import ezfunctions
import pools
import re
import secrets
import textwrap
import validating
import yaml

class MyDumper(yaml.Dumper):
    def increase_indent(self, flow=False, indentless=False):
        return super(MyDumper, self).increase_indent(flow, False)

class policies(object):
    def __init__(self, name_prefix, org, type):
        self.name_prefix = name_prefix
        self.org = org
        self.type = type

    #==============================================
    # Ethernet Adapter Policy Module
    #==============================================
    def ethernet_adapter(self, **kwargs):
        baseRepo       = kwargs['args'].dir
        configure_loop = False
        ezData         = kwargs['ezData']
        name_prefix    = self.name_prefix
        org            = self.org
        path_sep       = kwargs['path_sep']
        policy_type    = 'Ethernet Adapter'
        yaml_file      = 'ethernet'
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  {policy_type} Policy:  To simplify your work, this wizard will use {policy_type}')
            print(f'  Templates that are pre-configured.  You can add custom {policy_type} Policy')
            print(f'  configuration to the {yaml_file}.yaml file at your descretion.')
            print(f'  That will not be covered by this wizard as the focus of the wizard is on simplicity.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - {baseRepo}{path_sep}{org}{path_sep}{self.type}{path_sep}{yaml_file}.yaml')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure an {policy_type} Policy?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                policy_loop = False
                while policy_loop == False:
                    polVars = {}
                    # Prompt User for Ethernet Adapter Template
                    kwargs['multi_select'] = False
                    jsonVars = ezData['ezimm']['allOf'][1]['properties']['policies']['vnic.EthNetworkPolicy']
                    kwargs['jData'] = deepcopy(jsonVars['templates'])
                    kwargs['jData']['varType'] = 'Ethernet Adapter Template'
                    policy_template = ezfunctions.variablesFromAPI(**kwargs)
                    if not name_prefix == '': name = '%s-%s' % (name_prefix, policy_template)
                    else: name = '%s-%s' % (org, policy_template)
                    polVars['name']        = ezfunctions.policy_name(name, policy_type)
                    polVars['description'] = ezfunctions.policy_descr(polVars['name'], policy_type)

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(textwrap.indent(yaml.dump(polVars, Dumper=MyDumper, default_flow_style=False), ' '*4, predicate=None))
                    print(f'-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
                        if confirm_policy == 'Y' or confirm_policy == '':
                            # Add Policy Variables to immDict
                            kwargs['class_path'] = 'intersight,policies,ethernet_adapter'
                            kwargs = ezfunctions.ez_append(polVars, **kwargs)

                            configure_loop, policy_loop = ezfunctions.exit_default(policy_type, 'Y')
                            valid_confirm = True
                        elif confirm_policy == 'N':
                            ezfunctions.message_starting_over(policy_type)
                            valid_confirm = True
                        else: ezfunctions.message_invalid_y_or_n('short')
            elif configure == 'N': configure_loop = True
            else: ezfunctions.message_invalid_y_or_n('long')
        # Return kwargs
        return kwargs

    #==============================================
    # Ethernet Network Control Policy Module
    #==============================================
    def ethernet_network_control(self, **kwargs):
        baseRepo       = kwargs['args'].dir
        configure_loop = False
        jsonData       = kwargs['jsonData']
        name_prefix    = self.name_prefix
        name_suffix    = 'ntwk-ctrl'
        org            = self.org
        path_sep       = kwargs['path_sep']
        policy_type    = 'Ethernet Network Control Policy'
        yaml_file      = 'ethernet'
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  An {policy_type} will allow you to control Network Discovery with ')
            print(f'  protocols like CDP and LLDP as well as MAC Address Control Features.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - {baseRepo}{path_sep}{org}{path_sep}{self.type}{path_sep}{yaml_file}.yaml')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            policy_loop = False
            while policy_loop == False:
                polVars = {}
                if not name_prefix == '': name = f'{name_prefix}-{name_suffix}'
                else: name = f'{org}-{name_suffix}'
                polVars['name']        = ezfunctions.policy_name(name, policy_type)
                polVars['description'] = ezfunctions.policy_descr(polVars['name'], policy_type)
                polVars['action_on_uplink_fail'] = 'linkDown'

                # Pull Information from API Documentation
                kwargs['multi_select'] = False
                jsonVars = jsonData['fabric.LldpSettings']['allOf'][1]['properties']

                # Prompt User for LLDP
                kwargs['jData'] = deepcopy(jsonVars['ReceiveEnabled'])
                kwargs['jData']['varInput'] = f'Do you want to enable LLDP Recieve for this Policy?'
                kwargs['jData']['varName']  = 'LLDP Receive'
                answer = ezfunctions.varBoolLoop(**kwargs)
                if answer == True: polVars['lldp_receive_enable'] = True
                kwargs['jData'] = deepcopy(jsonVars['TransmitEnabled'])
                kwargs['jData']['varInput'] = f'Do you want to enable LLDP Transmit for this Policy?'
                kwargs['jData']['varName']  = 'LLDP Transmit'
                answer = ezfunctions.varBoolLoop(**kwargs)
                if answer == True: polVars['lldp_transmit_enable'] = True

                # Pull Information from API Documentation
                jsonVars = jsonData['fabric.EthNetworkControlPolicy']['allOf'][1]['properties']
                # Prompt User for CDP Enable
                kwargs['jData'] = deepcopy(jsonVars['CdpEnabled'])
                kwargs['jData']['varInput'] = f'Do you want to enable CDP (Cisco Discovery Protocol) for this Policy?'
                kwargs['jData']['varName']  = 'CDP Enable'
                answer = ezfunctions.varBoolLoop(**kwargs)
                if answer == True: polVars['cdp_enable'] = True

                # Prompt User for MAC Register Mode
                kwargs['jData'] = deepcopy(jsonVars['MacRegistrationMode'])
                kwargs['jData']['varType'] = 'MAC Registration Mode'
                polVars['mac_register_mode'] = ezfunctions.variablesFromAPI(**kwargs)

                # Prompt User for MAC Security Forge
                kwargs['jData'] = deepcopy(jsonVars['ForgeMac'])
                kwargs['jData']['varType'] = 'MAC Security Forge'
                polVars['mac_security_forge'] = ezfunctions.variablesFromAPI(**kwargs)

                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(textwrap.indent(yaml.dump(polVars, Dumper=MyDumper, default_flow_style=False), ' '*4, predicate=None))
                print(f'-------------------------------------------------------------------------------------------\n')
                valid_confirm = False
                while valid_confirm == False:
                    confirm_policy = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                    if confirm_policy == 'Y' or confirm_policy == '':
                        # Add Policy Variables to immDict
                        kwargs['class_path'] = 'intersight,policies,ethernet_network_control'
                        kwargs = ezfunctions.ez_append(polVars, **kwargs)

                        configure_loop, policy_loop = ezfunctions.exit_default(policy_type, 'N')
                        valid_confirm = True
                    elif confirm_policy == 'N':
                        ezfunctions.message_starting_over(policy_type)
                        valid_confirm = True
                    else: ezfunctions.message_invalid_y_or_n('long')
        # Return kwargs
        return kwargs

    #==============================================
    # Ethernet Network Group Policy Module
    #==============================================
    def ethernet_network_group(self, **kwargs):
        baseRepo       = kwargs['args'].dir
        configure_loop = False
        name_prefix    = self.name_prefix
        name_suffix    = ['mgmt', 'migration', 'storage', 'dvs']
        org            = self.org
        path_sep       = kwargs['path_sep']
        policy_type    = 'Ethernet Network Group Policy'
        yaml_file      = 'ethernet'
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  An {policy_type} will define the Allowed VLANs on a Server vNIC Template.')
            print(f'  As a recommendation you will need an {policy_type} per vNIC Grouping.')
            print(f'  For Instance with a Virtual Host that may have the following vNIC Pairs:')
            print(f'     1. mgmt')
            print(f'     2. migration')
            print(f'     3. storage')
            print(f'     4. dvs')
            print(f'  You will want to configure 1 {policy_type} per Group.')
            print(f'  The allowed vlan list can be in the format of:')
            print(f'     5 - Single VLAN')
            print(f'     1-10 - Range of VLANs')
            print(f'     1,2,3,4,5,11,12,13,14,15 - List of VLANs')
            print(f'     1-10,20-30 - Ranges and Lists of VLANs')
            print(f'  If you want to Assign a Native VLAN Make sure it is in the allowed list.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - {baseRepo}{path_sep}{org}{path_sep}{self.type}{path_sep}{yaml_file}.yaml')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            loop_count = 0
            policy_loop = False
            while policy_loop == False:
                name = ''
                for i, v in enumerate(name_suffix):
                    if int(loop_count) == i:
                        if not name_prefix == '': name = '%s-%s' % (name_prefix, v)
                        else: name = '%s-%s' % (org, v)
                if name == '':  name = '%s-%s' % (org, 'vlg')
                polVars = {}
                polVars['name']        = ezfunctions.policy_name(name, policy_type)
                polVars['description'] = ezfunctions.policy_descr(polVars['name'], policy_type)
                polVars['action_on_uplink_fail'] = 'linkDown'
                kwargs['name_prefix'] = name_prefix
                kwargs['name']        = polVars['name']
                kwargs['policy'] = 'policies.vlan.vlan_policy'
                kwargs['allow_opt_out'] = False
                kwargs = policy_select_loop(**kwargs)
                vlan_list = []
                for item in kwargs['immDict']['orgs'][org]['intersight']['policies']['vlan']:
                    if item['name'] == kwargs['vlan_policy']:
                        for i in item['vlans']:
                            vlan_list.append(i['vlan_list'])
                all_vlans = ','.join(vlan_list)
                vlan_policy_list = ezfunctions.vlan_list_full(all_vlans)
                valid = False
                while valid == False:
                    VlanList = input('Enter the VLAN or List of VLANs to add to {}: '.format(polVars['name']))
                    if not VlanList == '':
                        vlanListExpanded = ezfunctions.vlan_list_full(VlanList)
                        valid_vlan = True
                        vlans_not_in_domain_policy = []
                        for vlan in vlanListExpanded:
                            if str(vlan).isnumeric():
                                valid_vlan = validating.number_in_range('VLAN ID', vlan, 1, 4094)
                                if not valid_vlan == False:
                                    vlan_count = 0
                                    for i in vlan_policy_list:
                                        if int(vlan) == int(i):
                                            vlan_count += 1
                                            break
                                    if vlan_count == 0: vlans_not_in_domain_policy.append(vlan)
                            else: vlans_not_in_domain_policy.append(vlan)
                        if len(vlans_not_in_domain_policy) > 0:
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            print(f'  Error with VLAN(s) assignment!!  The following VLAN(s) are missing.')
                            print(f'  - Missing VLANs: {vlans_not_in_domain_policy}')
                            print(f'  - VLAN Policy: "{kwargs["vlan_policy"]}"')
                            print(f'  - Has VLANs: "{all_vlans}"')
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            valid_vlan = False
                        else: valid = True
                    else:
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        print(f'  The allowed vlan list can be in the format of:')
                        print(f'     5 - Single VLAN')
                        print(f'     1-10 - Range of VLANs')
                        print(f'     1,2,3,4,5,11,12,13,14,15 - List of VLANs')
                        print(f'     1-10,20-30 - Ranges and Lists of VLANs')
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                # Prompt User for Native VLAN
                polVars['native_vlan'] = ezfunctions.vlan_native_function(vlan_policy_list, vlan_list)
                if polVars['native_vlan'] == '': polVars.pop('native_vlan')
                polVars['allowed_vlans'] = VlanList
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(textwrap.indent(yaml.dump(polVars, Dumper=MyDumper, default_flow_style=False), ' '*4, predicate=None))
                print(f'-------------------------------------------------------------------------------------------\n')
                valid_confirm = False
                while valid_confirm == False:
                    confirm_policy = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                    if confirm_policy == 'Y' or confirm_policy == '':
                        # Add Policy Variables to immDict
                        kwargs['class_path'] = 'intersight,policies,ethernet_network_group'
                        kwargs = ezfunctions.ez_append(polVars, **kwargs)

                        if loop_count < 4: configure_loop, policy_loop = ezfunctions.exit_default(policy_type, 'Y')
                        else: configure_loop, policy_loop = ezfunctions.exit_default(policy_type, 'N')
                        if policy_loop == False and configure_loop == False: loop_count += 1
                        valid_confirm = True
                    elif confirm_policy == 'N':
                        ezfunctions.message_starting_over(policy_type)
                        valid_confirm = True
                    else: ezfunctions.message_invalid_y_or_n('long')
        # Return kwargs
        return kwargs

    #==============================================
    # Ethernet Network Policy Module
    #==============================================
    def ethernet_network(self, **kwargs):
        baseRepo       = kwargs['args'].dir
        configure_loop = False
        jsonData       = kwargs['jsonData']
        name_prefix    = self.name_prefix
        name_suffix    = 'network'
        org            = self.org
        path_sep       = kwargs['path_sep']
        policy_type    = 'Ethernet Network Policy'
        yaml_file      = 'ethernet'
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  An {policy_type} determines if the port can carry single VLAN (Access) ')
            print(f'  or multiple VLANs (Trunk) traffic. You can specify the VLAN to be associated with an ')
            print(f'  Ethernet packet if no tag is found.\n\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - {baseRepo}{path_sep}{org}{path_sep}{self.type}{path_sep}{yaml_file}.yaml')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure an {policy_type}?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                policy_loop = False
                while policy_loop == False:
                    polVars = {}
                    if not name_prefix == '': name = f'{name_prefix}-{name_suffix}'
                    else: name = f'{org}-{name_suffix}'
                    polVars['name']        = ezfunctions.policy_name(name, policy_type)
                    polVars['description'] = ezfunctions.policy_descr(polVars['name'], policy_type)

                    # Get VLAN Settings from API Data
                    kwargs['multi_select'] = False
                    jsonVars = jsonData['vnic.VlanSettings']['allOf'][1]['properties']

                    kwargs['jData'] = deepcopy(jsonVars['Mode'])
                    kwargs['jData']['varType'] = 'VLAN Mode'
                    polVars['vlan_mode'] = ezfunctions.variablesFromAPI(**kwargs)

                    valid = False
                    while valid == False:
                        kwargs['default_vlan'] = input('What is the default vlan to assign to this Policy.  Range is 0 to 4094: ')
                        if re.fullmatch(r'[0-9]{1,4}', polVars['default_vlan']):
                            valid = validating.number_in_range('VLAN ID', polVars['default_vlan'], 0, 4094)

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(textwrap.indent(yaml.dump(polVars, Dumper=MyDumper, default_flow_style=False), ' '*4, predicate=None))
                    print(f'-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
                        if confirm_policy == 'Y' or confirm_policy == '':
                            # Add Policy Variables to immDict
                            kwargs['class_path'] = 'intersight,policies,ethernet_network'
                            kwargs = ezfunctions.ez_append(polVars, **kwargs)

                            configure_loop, policy_loop = ezfunctions.exit_default(policy_type, 'N')
                            valid_confirm = True
                        elif confirm_policy == 'N':
                            ezfunctions.message_starting_over(policy_type)
                            valid_confirm = True
                        else: ezfunctions.message_invalid_y_or_n('short')
            elif configure == 'N':
                configure_loop = True
            else: ezfunctions.message_invalid_y_or_n('long')
        # Return kwargs
        return kwargs

    #==============================================
    # Ethernet QoS Policy Module
    #==============================================
    def ethernet_qos(self, **kwargs):
        baseRepo       = kwargs['args'].dir
        configure_loop = False
        jsonData       = kwargs['jsonData']
        name_prefix    = self.name_prefix
        name_suffix    = ['mgmt', 'migration', 'storage', 'dvs']
        org            = self.org
        path_sep       = kwargs['path_sep']
        policy_type    = 'Ethernet QoS Policy'
        yaml_file      = 'ethernet'
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  An {policy_type} will configure QoS on a Server vNIC Template.')
            print(f'  As a recommendation you will need an {policy_type} per vNIC Group.')
            print(f'  For Instance with a Virtual Host that may have the following vNIC Groups:')
            print(f'     1. mgmt')
            print(f'     2. nigration')
            print(f'     3. storage')
            print(f'     4. dvs')
            print(f'  It would be a good practice to configure different QoS Priorities for Each vNIC Group.')
            print(f'  For Instance a good practice would be something like the following:')
            print(f'     mgmt - Silver')
            print(f'     migration - Bronze')
            print(f'     storage - Platinum')
            print(f'     dvs - Gold.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - {baseRepo}{path_sep}{org}{path_sep}{self.type}{path_sep}{yaml_file}.yaml')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            # Get Variables from API Data
            kwargs['multi_select'] = False
            jsonVars = jsonData['vnic.EthNetworkPolicy']['allOf'][1]['properties']
            kwargs['jData'] = deepcopy(jsonVars['TargetPlatform'])
            kwargs['jData']['default'] = 'FIAttached'
            kwargs['jData']['varType'] = 'Target Platform'
            target_platform = ezfunctions.variablesFromAPI(**kwargs)
            loop_count = 0
            policy_loop = False
            while policy_loop == False:
                polVars = {}
                polVars['target_platform'] == target_platform
                name = ''
                if polVars['target_platform'] == 'FIAttached':
                    for i, v in enumerate(name_suffix):
                        if int(loop_count) == i:
                            if not name_prefix == '': name = f'{name_prefix}-{v}'
                            else: name = f'{name_prefix}-{v}'
                else: 
                    if not name_prefix == '': name = f'{name_prefix}-qos'
                if name == '': name = f'{org}-qos'
                polVars['name']        = ezfunctions.policy_name(name, policy_type)
                polVars['description'] = ezfunctions.policy_descr(polVars['name'], policy_type)

                # Get API Data
                kwargs['multi_select'] = False
                jsonVars = jsonData['vnic.EthQosPolicy']['allOf'][1]['properties']

                # Prompt User for Trust Host CoS
                kwargs['jData'] = deepcopy(jsonVars['TrustHostCos'])
                kwargs['jData']['varInput'] = f'Do you want to Enable Trust Host based CoS?'
                kwargs['jData']['varName']  = 'Trust Host CoS'
                polVars['enable_trust_host_cos'] = ezfunctions.varBoolLoop(**kwargs)

                # Prompt User for Rate Limit
                kwargs['jData'] = deepcopy(jsonVars['RateLimit'])
                kwargs['jData']['varInput'] = f'What is the Rate Limit you want to assign to the Policy?'
                kwargs['jData']['varName']  = 'Rate Limit'
                polVars['rate_limit'] = ezfunctions.varNumberLoop(**kwargs)

                if polVars['target_platform'] == 'Standalone':
                    polVars['burst'] = 1024
                    polVars['priority'] = 'Best Effort'
                    # Prompt User for Class of Service
                    kwargs['jData'] = deepcopy(jsonVars['Cos'])
                    kwargs['jData']['varInput'] = f'What is the Class of Service you want to assign to the Policy?'
                    kwargs['jData']['varName']  = 'Class of Service'
                    polVars['cos'] = ezfunctions.varNumberLoop(**kwargs)

                    # Prompt User for MTU
                    kwargs['jData'] = deepcopy(jsonVars['Mtu'])
                    kwargs['jData']['varInput'] = f'What is the MTU you want to assign to the Policy?'
                    kwargs['jData']['varName']  = 'MTU'
                    polVars['mtu'] = ezfunctions.varNumberLoop(**kwargs)
                else:
                    polVars['cos'] = 0
                    # Prompt User for Burst
                    kwargs['jData'] = deepcopy(jsonVars['Burst'])
                    kwargs['jData']['varInput'] = f'What is the Burst you want to assign to the Policy?'
                    kwargs['jData']['varName']  = 'Burst'
                    polVars['burst'] = ezfunctions.varNumberLoop(**kwargs)

                    # Prompt User for Priority
                    kwargs['jData'] = deepcopy(jsonVars['Priority'])
                    kwargs['jData']['varType'] = f"{polVars['name']} QoS Priority"
                    polVars['priority'] = ezfunctions.variablesFromAPI(**kwargs)

                    if loop_count == 0:
                        if polVars['target_platform'] == 'FIAttached':
                            polVars['allow_opt_out'] = False
                            kwargs['policy'] = 'policies.system_qos.system_qos_policy'
                            kwargs = policy_select_loop(**kwargs)
                    mtu = 1500
                    for i in kwargs['immDict']['orgs'][org]['policies']['system_qos']:
                        if i['name'] == kwargs['system_qos_policy']:
                            mtu = ['classes'][polVars['priority']]['mtu']
                    if mtu > 8999: polVars['mtu'] = 9000
                    else: polVars['mtu'] = mtu

                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(textwrap.indent(yaml.dump(polVars, Dumper=MyDumper, default_flow_style=False), ' '*4, predicate=None))
                print(f'\n-------------------------------------------------------------------------------------------\n')
                valid_confirm = False
                while valid_confirm == False:
                    confirm_policy = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
                    if confirm_policy == 'Y' or confirm_policy == '':
                        # Add Policy Variables to immDict
                        kwargs['class_path'] = 'intersight,policies,ethernet_qos'
                        kwargs = ezfunctions.ez_append(polVars, **kwargs)

                        valid_exit = False
                        while valid_exit == False:
                            if loop_count < 3 and target_platform == 'FIAttached':
                                configure_loop, policy_loop = ezfunctions.exit_default(policy_type, 'Y')
                            else: configure_loop, policy_loop = ezfunctions.exit_default(policy_type, 'N')
                            if policy_loop == False and configure_loop == False: loop_count += 1
                            valid_exit = True
                        valid_confirm = True
                    elif confirm_policy == 'N':
                        ezfunctions.message_starting_over(policy_type)
                        valid_confirm = True
                    else: ezfunctions.message_invalid_y_or_n('long')
        # Return kwargs
        return kwargs

    #==============================================
    # Fibre-Channel Adapter Policy Module
    #==============================================
    def fibre_channel_adapter(self, **kwargs):
        baseRepo       = kwargs['args'].dir
        configure_loop = False
        ezData         = kwargs['ezData']
        name_prefix    = self.name_prefix
        org            = self.org
        path_sep       = kwargs['path_sep']
        policy_type    = 'Fibre-Channel Adapter Policy'
        yaml_file      = 'fibre_channel'
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  You can Skip this policy if you are not configuring Fibre-Channel.\n')
            print(f'  {policy_type} Policies:  To simplify your work, this wizard will use {policy_type}')
            print(f'  Templates that are pre-configured.  You can add custom {policy_type} policy')
            print(f'  configuration to the {yaml_file}.yaml file at your descretion.  ')
            print(f'  That will not be covered by this wizard as the focus of the wizard is on simplicity.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - {baseRepo}{path_sep}{org}{path_sep}{self.type}{path_sep}{yaml_file}.yaml')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure a {policy_type}?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                policy_loop = False
                while policy_loop == False:
                    polVars = {}
                    # Pull Information from API Documentation
                    polVars["multi_select"] = False
                    jsonVars = ezData['ezimm']['allOf'][1]['properties']['policies']['vnic.FcNetworkPolicy']

                    kwargs['jData'] = deepcopy(jsonVars['MacRegistrationMode'])
                    kwargs['jData']["varType"] = 'Fibre-Channel Adapter Template'
                    policy_template = ezfunctions.variablesFromAPI(**kwargs)

                    if not name_prefix == '': name = '%s-%s' % (name_prefix, policy_template)
                    else: name = '%s-%s' % (org, policy_template)
                    polVars['name']        = ezfunctions.policy_name(name, policy_template)
                    polVars['description'] = ezfunctions.policy_descr(polVars['name'], policy_type)

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(textwrap.indent(yaml.dump(polVars, Dumper=MyDumper, default_flow_style=False), ' '*4, predicate=None))
                    print(f'-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
                        if confirm_policy == 'Y' or confirm_policy == '':
                            # Add Policy Variables to immDict
                            kwargs['class_path'] = 'intersight,policies,fibre_channel_adapter'
                            kwargs = ezfunctions.ez_append(polVars, **kwargs)

                            configure_loop, policy_loop = ezfunctions.exit_default(policy_type, 'Y')
                            valid_confirm = True
                        elif confirm_policy == 'N':
                            ezfunctions.message_invalid_y_or_n('short')
                            valid_confirm = True
                        else: ezfunctions.message_invalid_y_or_n('short')
            elif configure == 'N': configure_loop = True
            else: ezfunctions.message_invalid_y_or_n('long')
        # Return kwargs
        return kwargs

    #==============================================
    # Fibre-Channel Network Policy Module
    #==============================================
    def fibre_channel_network(self, **kwargs):
        baseRepo       = kwargs['args'].dir
        configure_loop = False
        jsonData       = kwargs['jsonData']
        name_prefix    = self.name_prefix
        org            = self.org
        path_sep       = kwargs['path_sep']
        policy_type    = 'Fibre-Channel Network Policy'
        yaml_file      = 'fibre_channel'
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  You can Skip this policy if you are not configuring Fibre-Channel.\n')
            print(f'  Fibre-Channel Network Policies Notes:')
            print(f'  - You will need one Policy per Fabric.  VSAN A and VSAN B.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - {baseRepo}{path_sep}{org}{path_sep}{self.type}{path_sep}{yaml_file}.yaml')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure a {policy_type}?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                loop_count = 0
                policy_loop = False
                while policy_loop == False:
                    polVars = {}
                    name = ezfunctions.naming_rule_fabric(loop_count, name_prefix, org)
                    polVars['name']        = ezfunctions.policy_name(name, policy_type)
                    polVars['description'] = ezfunctions.policy_descr(polVars['name'], policy_type)

                    kwargs["multi_select"] = False
                    jsonVars = jsonData['server.BaseProfile']['allOf'][1]['properties']

                    kwargs['jData'] = deepcopy(jsonVars['TargetPlatform'])
                    kwargs['jData']["default"] = 'FIAttached'
                    kwargs['jData']["varType"] = 'Target Platform'
                    polVars["target_platform"] = ezfunctions.variablesFromAPI(**kwargs)

                    jsonVars = jsonData['vnic.VsanSettings']['allOf'][1]['properties']
                    if polVars["target_platform"] == 'Standalone':
                        kwargs['jData'] = deepcopy(jsonVars['DefaultVlanId'])
                        kwargs['jData']['minimum'] = 1
                        kwargs['jData']['varInput'] = 'What is the Default VLAN you want to Assign to this Policy?'
                        kwargs['jData']['varName']  = 'Default VLAN'
                        polVars['default_vlan'] = ezfunctions.varNumberLoop(**kwargs)

                        valid = False
                        while valid == False:
                            kwargs['jData'] = deepcopy(jsonVars['Id'])
                            if loop_count % 2 == 0: kwargs['jData']['defualt'] = 100
                            else: kwargs['jData']['defualt'] = 200
                            kwargs['jData']['varInput'] = 'What VSAN Do you want to Assign to this Policy?'
                            kwargs['jData']['varName']  = 'VSAN'
                            vsan_id = ezfunctions.varNumberLoop(**kwargs)
                            if polVars["target_platform"] == 'FIAttached':
                                kwargs["allow_opt_out"] = False
                                kwargs['policy'] = 'policies.vsan.vsan_policy'
                                kwargs = policy_select_loop(**kwargs)
                                vsan_list = []
                                for item in kwargs['immDict'][['org']][org]['vsan']:
                                    if item['name'] == kwargs['vsan_policy']:
                                        for i in item['vsan']: vsan_list.append(i['vsan_id'])
                                vsan_string = ','.join(str(vsan_list))
                                vsan_list = ezfunctions.vlan_list_full(vsan_string)
                                vcount = 0
                                for vsan in vsan_list:
                                    if int(vsan_id) == int(vsan):
                                        vcount = 1
                                        break
                                if vcount == 0: ezfunctions.message_invalid_vsan_id(kwargs['vsan_policy'], vsan_id, vsan_list)
                                else: valid = True
                    if polVars["target_platform"] == 'FIAttached': polVars.pop('target_platform')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(textwrap.indent(yaml.dump(polVars, Dumper=MyDumper, default_flow_style=False), ' '*4, predicate=None))
                    print(f'-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                        if confirm_policy == 'Y' or confirm_policy == '':
                            # Add Policy Variables to immDict
                            kwargs['class_path'] = 'intersight,policies,fibre_channel_network'
                            kwargs = ezfunctions.ez_append(polVars, **kwargs)

                            configure_loop, loop_count, policy_loop = ezfunctions.exit_loop_default_yes(loop_count, policy_type)
                            valid_confirm = True
                        elif confirm_policy == 'N':
                            ezfunctions.message_starting_over(policy_type)
                            valid_confirm = True
                        else: ezfunctions.message_invalid_y_or_n('short')
            elif configure == 'N': configure_loop = True
            else: ezfunctions.message_invalid_y_or_n('long')
        # Return kwargs
        return kwargs

    #==============================================
    # Fibre-Channel QoS Policy Module
    #==============================================
    def fibre_channel_qos(self, **kwargs):
        baseRepo       = kwargs['args'].dir
        configure_loop = False
        name_prefix    = self.name_prefix
        name_suffix    = 'fc-qos'
        org            = self.org
        path_sep       = kwargs['path_sep']
        policy_type    = 'Fibre-Channel QoS Policy'
        yaml_file      = 'fibre_channel'
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  You can Skip this policy if you are not configuring Fibre-Channel.\n')
            print(f'  It is a good practice to apply a {policy_type} to the vHBAs.  This wizard')
            print(f'  creates the policy with all the default values, so you only need one')
            print(f'  {policy_type}.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - {baseRepo}{path_sep}{org}{path_sep}{self.type}{path_sep}{yaml_file}.yaml')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure a {policy_type}?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                policy_loop = False
                while policy_loop == False:
                    polVars = {}
                    if not name_prefix == '': name = f'{name_prefix}-{name_suffix}'
                    else: name = f'{org}-{name_suffix}'
                    polVars['name']        = ezfunctions.policy_name(name, policy_type)
                    polVars['description'] = ezfunctions.policy_descr(polVars['name'], policy_type)

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(textwrap.indent(yaml.dump(polVars, Dumper=MyDumper, default_flow_style=False), ' '*4, predicate=None))
                    print(f'-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                        if confirm_policy == 'Y' or confirm_policy == '':
                            # Add Policy Variables to immDict
                            kwargs['class_path'] = 'intersight,policies,fibre_channel_qos'
                            kwargs = ezfunctions.ez_append(polVars, **kwargs)

                            configure_loop, policy_loop = ezfunctions.exit_default(policy_type, 'N')
                            valid_confirm = True
                        elif confirm_policy == 'N':
                            ezfunctions.message_starting_over(policy_type)
                            valid_confirm = True
                        else: ezfunctions.message_invalid_y_or_n('short')
            elif configure == 'N': configure_loop = True
            else: ezfunctions.message_invalid_y_or_n('long')
        # Return kwargs
        return kwargs

    #==============================================
    # Flow Control Policy Module
    #==============================================
    def flow_control(self, **kwargs):
        baseRepo       = kwargs['args'].dir
        configure_loop = False
        name_prefix    = self.name_prefix
        name_suffix    = 'flow-ctrl'
        org            = self.org
        path_sep       = kwargs['path_sep']
        policy_type    = 'Flow Control Policy'
        yaml_file      = 'ethernet'
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  The Flow Control Policy will enable Priority Flow Control on the Fabric Interconnects.')
            print(f'  We recommend the default parameters so you will only be asked for the name and')
            print(f'  description for the Policy.  You only need one of these policies for Organization')
            print(f'  {org}.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - {baseRepo}{path_sep}{org}{path_sep}{self.type}{path_sep}{yaml_file}.yaml')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            policy_loop = False
            while policy_loop == False:
                polVars = {}
                if not name_prefix == '': name = f'{name_prefix}-{name_suffix}'
                else: name = f'{org}-{name_suffix}'
                polVars['name']        = ezfunctions.policy_name(name, policy_type)
                polVars['description'] = ezfunctions.policy_descr(polVars['name'], policy_type)

                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(textwrap.indent(yaml.dump(polVars, Dumper=MyDumper, default_flow_style=False), ' '*4, predicate=None))
                print(f'-------------------------------------------------------------------------------------------\n')
                valid_confirm = False
                while valid_confirm == False:
                    confirm_policy = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                    if confirm_policy == 'Y' or confirm_policy == '':
                        # Add Policy Variables to immDict
                        kwargs['class_path'] = 'intersight,policies,flow_control'
                        kwargs = ezfunctions.ez_append(polVars, **kwargs)

                        configure_loop, policy_loop = ezfunctions.exit_default(policy_type, 'N')
                        valid_confirm = True
                    elif confirm_policy == 'N':
                        ezfunctions.message_starting_over(policy_type)
                        valid_confirm = True
                    else: ezfunctions.message_invalid_y_or_n('long')
        # Return kwargs
        return kwargs

    #==============================================
    # iSCSI Adapter Policy Module
    #==============================================
    def iscsi_adapter(self, **kwargs):
        baseRepo       = kwargs['args'].dir
        configure_loop = False
        jsonData       = kwargs['jsonData']
        name_prefix    = self.name_prefix
        name_suffix    = 'adapter'
        org            = self.org
        path_sep       = kwargs['path_sep']
        policy_type    = 'iSCSI Adapter Policy'
        yaml_file      = 'ethernet'
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  The {policy_type} allows you to configure values for TCP Connection Timeout, ')
            print(f'  DHCP Timeout, and the Retry Count if the specified LUN ID is busy.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - {baseRepo}{path_sep}{org}{path_sep}{self.type}{path_sep}{yaml_file}.yaml')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure a {policy_type}?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                policy_loop = False
                while policy_loop == False:
                    polVars = {}
                    if not name_prefix == '': name = f'{name_prefix}-{name_suffix}'
                    else: name = f'{org}-{name_suffix}'
                    polVars['name']        = ezfunctions.policy_name(name, policy_type)
                    polVars['description'] = ezfunctions.policy_descr(polVars['name'], policy_type)

                    # Pull in the Policies for iSCSI Adapter
                    kwargs['multi_select'] = False
                    jsonVars = jsonData['vnic.IscsiAdapterPolicy']['allOf'][1]['properties']

                    # DHCP Timeout
                    kwargs['jData'] = deepcopy(jsonVars['DhcpTimeout'])
                    kwargs['jData']['default']  = 60
                    kwargs['jData']['varInput'] = f'Enter the number of seconds after which the DHCP times out.'
                    kwargs['jData']['varName']  = 'DHCP Timeout'
                    polVars['dhcp_timeout'] = ezfunctions.varNumberLoop(**kwargs)

                    # LUN Busy Retry Count
                    kwargs['jData'] = deepcopy(jsonVars['LunBusyRetryCount'])
                    kwargs['jData']['default']  = 15
                    kwargs['jData']['varInput'] = f'Enter the number of times connection is to be attempted when the LUN ID is busy.'
                    kwargs['jData']['varName']  = 'LUN Busy Retry Count'
                    polVars['lun_busy_retry_count'] = ezfunctions.varNumberLoop(**kwargs)

                    # TCP Connection Timeout
                    kwargs['jData'] = deepcopy(jsonVars['ConnectionTimeOut'])
                    kwargs['jData']['default']  = 15
                    kwargs['jData']['varInput'] = f'Enter the number of seconds after which the TCP connection times out.'
                    kwargs['jData']['varName']  = 'TCP Connection Timeout'
                    polVars['tcp_connection_timeout'] = ezfunctions.varNumberLoop(**kwargs)

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(textwrap.indent(yaml.dump(polVars, Dumper=MyDumper, default_flow_style=False), ' '*4, predicate=None))
                    print(f'-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                        if confirm_policy == 'Y' or confirm_policy == '':
                            # Add Policy Variables to immDict
                            confirm_policy = 'Y'
                            kwargs['class_path'] = 'intersight,policies,iscsi_adapter'
                            kwargs = ezfunctions.ez_append(polVars, **kwargs)
                            configure_loop, policy_loop = ezfunctions.exit_default(policy_type, 'N')
                            valid_confirm = True
                        elif confirm_policy == 'N':
                            ezfunctions.message_starting_over(policy_type)
                            valid_confirm = True
                        else: ezfunctions.message_invalid_y_or_n('short')
            elif configure == 'N':
                configure_loop = True
            else: ezfunctions.message_invalid_y_or_n('long')
        # Return kwargs
        return kwargs

    #==============================================
    # iSCSI Boot Policy Module
    #==============================================
    def iscsi_boot(self, **kwargs):
        baseRepo       = kwargs['args'].dir
        configure_loop = False
        jsonData       = kwargs['jsonData']
        name_prefix    = self.name_prefix
        name_suffix    = 'boot'
        org            = self.org
        path_sep       = kwargs['path_sep']
        policy_type    = 'iSCSI Boot Policy'
        yaml_file      = 'ethernet'
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  The {policy_type} allows you to initialize the Operating System on FI-attached ')
            print(f'  blade and rack servers from a remote disk across a Storage Area Network. The remote disk, ')
            print(f'  known as the target, is accessed using TCP/IP and iSCSI boot firmware.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - {baseRepo}{path_sep}{org}{path_sep}{self.type}{path_sep}{yaml_file}.yaml')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure a {policy_type}?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                policy_loop = False
                while policy_loop == False:
                    polVars = {}
                    if not name_prefix == '': name = f'{name_prefix}-{name_suffix}'
                    else: name = f'{org}-{name_suffix}'
                    polVars['name']        = ezfunctions.policy_name(name, policy_type)
                    polVars['description'] = ezfunctions.policy_descr(polVars['name'], policy_type)

                    # Pull in the Policies for iSCSI Boot from API Data
                    kwargs['multi_select'] = False
                    jsonVars = jsonData['vnic.IscsiBootPolicy']['allOf'][1]['properties']

                    # Target Source Type
                    kwargs['jData'] = deepcopy(jsonVars['TargetSourceType'])
                    kwargs['jData']['varType'] = 'Target Source Type'
                    polVars['target_source_type'] = ezfunctions.variablesFromAPI(**kwargs)

                    if polVars['target_source_type'] == 'Auto':
                        polVars['authentication'] = 'none'
                        polVars['initiator_ip_source'] = 'DHCP'
                        polVars['primary_target_policy'] = ''
                        polVars['secondary_target_policy'] = ''

                        kwargs['jData'] = deepcopy(jsonVars['AutoTargetvendorName'])
                        kwargs['jData']['default']  = ''
                        kwargs['jData']['minimum'] = 1
                        kwargs['jData']['maximum'] = 32
                        kwargs['jData']['pattern'] = '^[\\S]+$'
                        kwargs['jData']['varInput'] = 'DHCP Vendor ID or IQN:'
                        kwargs['jData']['varName']  = 'DHCP Vendor ID or IQN'
                        polVars['dhcp_vendor_id_iqn'] = ezfunctions.varStringLoop(**kwargs)

                    elif polVars['target_source_type'] == 'Static':
                        kwargs['optional_message'] = '  !!! Select the Primary Static Target !!!\n'
                        kwargs['allow_opt_out'] = False
                        kwargs['policy'] = 'policies.iscsi_static_target.iscsi_static_target_policy'
                        kwargs = policy_select_loop(**kwargs)
                        polVars['primary_target_policy'] = kwargs['iscsi_static_target_policy']
                        
                        kwargs['optional_message'] = ''\
                            '  !!! Optionally Select the Secondary Static Target or enter 100 for no Secondary !!!\n'
                        kwargs['allow_opt_out'] = True
                        kwargs = policy_select_loop(**kwargs)
                        polVars['secondary_target_policy'] = kwargs['iscsi_static_target_policy']
                        kwargs.pop('optional_message')
                        # polVars.update(policyData)
                        # polVars.update(policyData)

                        # Initiator IP Source
                        kwargs['jData'] = deepcopy(jsonVars['InitiatorIpSource'])
                        kwargs['jData']['varType'] = 'Initiator IP Source'
                        polVars['initiator_ip_source'] = ezfunctions.variablesFromAPI(**kwargs)

                        if polVars['initiator_ip_source'] == 'Pool':
                            # Prompt User for the IP Pool
                            kwargs['optional_message'] = '  !!! Initiator IP Pool !!!\n'
                            kwargs['allow_opt_out'] = False
                            kwargs['policy'] = 'pools.ip.ip_pool'
                            kwargs = policy_select_loop(**kwargs)
                            kwargs.pop('optional_message')
                            polVars['ip_pool'] = kwargs['ip_pool']

                        elif polVars['initiator_ip_source'] == 'Static':
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            print(jsonVars['InitiatorStaticIpV4Config']['description'])
                            print(f'\n-------------------------------------------------------------------------------------------\n')

                            jsonVars = jsonData['vnic.IscsiStaticTargetPolicyInventory']['allOf'][1]['properties']
                            kwargs['jData'] = deepcopy(jsonVars['IpAddress'])
                            kwargs['jData']['varInput'] = f'IP Address:'
                            kwargs['jData']['varName']  = f'IP Address'
                            ipAddress = ezfunctions.varStringLoop(**kwargs)

                            jsonVars = jsonData['ippool.IpV4Config']['allOf'][1]['properties']
                            kwargs['jData'] = deepcopy(jsonVars['Netmask'])
                            kwargs['jData']['varInput'] = f'Subnet Mask:'
                            kwargs['jData']['varName']  = f'Subnet Mask'
                            subnetMask = ezfunctions.varStringLoop(**kwargs)

                            kwargs['jData'] = deepcopy(jsonVars['Gateway'])
                            kwargs['jData']['varInput'] = f'Default Gateway:'
                            kwargs['jData']['varName']  = f'Default Gateway'
                            defaultGateway = ezfunctions.varStringLoop(**kwargs)

                            kwargs['jData'] = deepcopy(jsonVars['SecondaryDns'])
                            kwargs['jData']['varInput'] = f'Primary DNS Server.  [press enter to skip]:'
                            kwargs['jData']['varName']  = f'Primary DNS Server'
                            primaryDns = ezfunctions.varStringLoop(**kwargs)

                            kwargs['jData'] = deepcopy(jsonVars['SecondaryDns'])
                            kwargs['jData']['varInput'] = f'Secondary DNS Server.  [press enter to skip]:'
                            kwargs['jData']['varName']  = f'Secondary DNS Server'
                            secondaryDns = ezfunctions.varStringLoop(**kwargs)

                            polVars['initiator_static_ip_v4_config'] = {
                                'ip_address':ipAddress, 'subnet_mask':subnetMask,
                                'default_gateway':defaultGateway,
                                'primary_dns':primaryDns, 'secondary_dns':secondaryDns,
                            }

                        # Type of Authentication
                        kwargs['jData'] = deepcopy()
                        kwargs['jData']['description'] = 'Select Which Type of Authentication you want to Perform.'
                        kwargs['jData']['enum'] = ['chap', 'mutual_chap', 'none']
                        kwargs['jData']['default'] = 'none'
                        kwargs['jData']['varType'] = 'Authentication Type'
                        polVars['authentication'] = ezfunctions.variablesFromAPI(**kwargs)

                        if re.search('chap', polVars['authentication']):
                            jsonVars = jsonData['vnic.IscsiAuthProfile']['allOf'][1]['properties']
                            auth_type = str.title(polVars['authentication'].replace('_', ' '))

                            kwargs['jData'] = deepcopy(jsonVars['UserId'])
                            kwargs['jData']['varInput'] = f'{auth_type} Username:'
                            kwargs['jData']['varName']  = f'{auth_type} Username'
                            polVars['username'] = ezfunctions.varStringLoop(**kwargs)

                            kwargs['Variable'] = 'iscsi_boot_password'
                            kwargs['iscsi_boot_password'] = ezfunctions.sensitive_var_value(**kwargs)

                    # Prompt User for the iSCSI Adapter Policy
                    polVars['allow_opt_out'] = True
                    kwargs['policy'] = 'policies.iscsi_adapter.iscsi_adapter_policy'
                    kwargs = policy_select_loop(**kwargs)
                    polVars['iscsi_adapter_policy'] = kwargs['iscsi_adapter_policy']
                    if polVars['authentication'] == 'none': polVars.pop('authentication')

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(textwrap.indent(yaml.dump(polVars, Dumper=MyDumper, default_flow_style=False), ' '*4, predicate=None))
                    print(f'-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                        if confirm_policy == 'Y' or confirm_policy == '':
                            # Add Policy Variables to immDict
                            kwargs['class_path'] = 'intersight,policies,iscsi_boot'
                            kwargs = ezfunctions.ez_append(polVars, **kwargs)
                            configure_loop, policy_loop = ezfunctions.exit_default(policy_type, 'N')
                            valid_confirm = True
                        elif confirm_policy == 'N':
                            ezfunctions.message_starting_over(policy_type)
                            valid_confirm = True
                        else: ezfunctions.message_invalid_y_or_n('short')
            elif configure == 'N': configure_loop = True
            else: ezfunctions.message_invalid_y_or_n('long')
        # Return kwargs
        return kwargs

    #==============================================
    # iSCSI Static Target Policy Module
    #==============================================
    def iscsi_static_target(self, **kwargs):
        baseRepo       = kwargs['args'].dir
        configure_loop = False
        jsonData       = kwargs['jsonData']
        name_prefix    = self.name_prefix
        name_suffix    = 'target'
        org            = self.org
        path_sep       = kwargs['path_sep']
        policy_type    = 'iSCSI Static Target Policy'
        yaml_file      = 'ethernet'
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  The {policy_type} allows you to specify the name, IP address, port, and ')
            print(f'  logical unit number of the primary target for iSCSI boot. You can optionally specify these ')
            print(f'  details for a secondary target as well.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - {baseRepo}{path_sep}{org}{path_sep}{self.type}{path_sep}{yaml_file}.yaml')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure a {policy_type}?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                policy_loop = False
                while policy_loop == False:
                    polVars = {}
                    if not name_prefix == '': name = f'{name_prefix}-{name_suffix}'
                    else: name = f'{org}-{name_suffix}'
                    polVars['name']        = ezfunctions.policy_name(name, policy_type)
                    polVars['description'] = ezfunctions.policy_descr(polVars['name'], policy_type)

                    # Pull in the Policies for iSCSI Static Target
                    jsonVars = jsonData['vnic.IscsiStaticTargetPolicy']['allOf'][1]['properties']
                    desc_add = '\n  such as:\n  * iqn.1984-12.com.cisco:lnx1\n  * iqn.1984-12.com.cisco:win-server1'

                    # Target Name
                    kwargs['jData'] = deepcopy(jsonVars['TargetName'])
                    kwargs['jData']['description'] = kwargs['jData']['description'] + desc_add
                    polVars['jData']['varInput'] = 'Enter the name of the target:'
                    polVars['jData']['varName']  = 'Target Name'
                    polVars['target_name'] = ezfunctions.varStringLoop(**kwargs)

                    # IP Address
                    kwargs['jData'] = deepcopy(jsonVars['IpAddress'])
                    kwargs['jData']['varInput'] = f'IP Address:'
                    kwargs['jData']['varName']  = f'IP Address'
                    polVars['ip_address'] = ezfunctions.varStringLoop(**kwargs)

                    # Port
                    kwargs['jData'] = deepcopy(jsonVars['Port'])
                    kwargs['jData']['default']  = 3260
                    kwargs['jData']['varInput'] = 'Enter the port number of the target.'
                    kwargs['jData']['varName']  = 'Port'
                    polVars['port'] = ezfunctions.varNumberLoop(**kwargs)

                    # LUN Identifier
                    kwargs['jData'] = deepcopy(jsonVars['Port'])
                    kwargs['jData']['default']  = 0
                    polVars['jData']['maximum'] = 1024
                    polVars['jData']['minimum'] = 0
                    kwargs['jData']['varInput'] = 'Enter the ID of the boot logical unit number.'
                    kwargs['jData']['varName']  = 'LUN Identifier'
                    polVars['lun_id'] = ezfunctions.varNumberLoop(**kwargs)

                    # LUN Bootable
                    polVars['jData']['default']  = True
                    polVars['jData']['varInput'] = f'Should LUN {polVars["lun_id"]} be bootable?'
                    polVars['jData']['varName']  = 'LUN Identifier'
                    polVars['bootable'] = ezfunctions.varBoolLoop(**kwargs)

                    polVars['lun'] = {'bootable':polVars['bootable'],'lun_id':polVars['lun_id']}
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(textwrap.indent(yaml.dump(polVars, Dumper=MyDumper, default_flow_style=False), ' '*4, predicate=None))
                    print(f'-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                        if confirm_policy == 'Y' or confirm_policy == '':
                            # Add Policy Variables to immDict
                            kwargs['class_path'] = 'intersight,policies,iscsi_static_target'
                            kwargs = ezfunctions.ez_append(polVars, **kwargs)

                            configure_loop, policy_loop = ezfunctions.exit_default(policy_type, 'N')
                            valid_confirm = True
                        elif confirm_policy == 'N':
                            ezfunctions.message_starting_over(policy_type)
                            valid_confirm = True
                        else: ezfunctions.message_invalid_y_or_n('short')
            elif configure == 'N': configure_loop = True
            else: ezfunctions.message_invalid_y_or_n('long')
        # Return kwargs
        return kwargs

    #==============================================
    # Multicast Policy Module
    #==============================================
    def multicast(self, **kwargs):
        baseRepo       = kwargs['args'].dir
        configure_loop = False
        jsonData       = kwargs['jsonData']
        name_prefix    = self.name_prefix
        name_suffix    = 'mcast'
        org            = self.org
        path_sep       = kwargs['path_sep']
        policy_type    = 'Multicast Policy'
        yaml_file      = 'vlan'
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  Each VLAN must have a Multicast Policy applied to it.  Optional attributes will be')
            print(f'  the IGMP Querier IPs.  IGMP Querier IPs are only needed if you have a non Routed VLAN')
            print(f'  and you need the Fabric Interconnects to act as IGMP Queriers for the network.')
            print(f'  If you configure IGMP Queriers for a Multicast Policy that Policy should only be')
            print(f'  Assigned to the VLAN for which those Queriers will service.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - {baseRepo}{path_sep}{org}{path_sep}{self.type}{path_sep}{yaml_file}.yaml')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            policy_loop = False
            while policy_loop == False:
                polVars = {}
                if not name_prefix == '': name = f'{name_prefix}-{name_suffix}'
                else: name = f'{org}-{name_suffix}'
                polVars['name'] = ezfunctions.policy_name(name, policy_type)
                polVars['description'] = ezfunctions.policy_descr(polVars['name'], policy_type)

                # Pull Information from API Documentation
                kwargs['multi_select'] = False
                jsonVars = jsonData['fabric.MulticastPolicy']['allOf'][1]['properties']

                # Prompt User for Querier
                kwargs['jData'] = deepcopy(jsonVars['QuerierIpAddress'])
                kwargs['jData']['varInput'] = 'IGMP Querier IP for Fabric Interconnect A.  [press enter to skip]:'
                kwargs['jData']['varName']  = 'IGMP Querier IP'
                polVars['querier_ip_address'] = ezfunctions.varStringLoop(**kwargs)
                if not polVars['querier_ip_address'] == '':
                    kwargs['jData'] = deepcopy(jsonVars['QuerierIpAddressPeer'])
                    kwargs['jData']['varInput'] = 'IGMP Querier Peer IP for Fabric Interconnect B.  [press enter to skip]:'
                    kwargs['jData']['varName']  = 'IGMP Querier Peer IP'
                    polVars['querier_ip_address_peer'] = ezfunctions.varStringLoop(**kwargs)
                if polVars['querier_ip_address'] == '': polVars.pop('querier_ip_address')
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(textwrap.indent(yaml.dump(polVars, Dumper=MyDumper, default_flow_style=False), ' '*4, predicate=None))
                print(f'-------------------------------------------------------------------------------------------\n')
                valid_confirm = False
                while valid_confirm == False:
                    confirm_policy = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                    if confirm_policy == 'Y' or confirm_policy == '':
                        # Add Policy Variables to immDict
                        kwargs['class_path'] = 'intersight,policies,multicast'
                        kwargs = ezfunctions.ez_append(polVars, **kwargs)

                        configure_loop, policy_loop = ezfunctions.exit_default(policy_type, 'N')
                        valid_confirm = True
                    elif confirm_policy == 'N':
                        ezfunctions.message_starting_over(policy_type)
                        valid_confirm = True
                    else: ezfunctions.message_invalid_y_or_n('long')
        # Return kwargs
        return kwargs

    #==============================================
    # LAN Connectivity Policy Module
    #==============================================
    def lan_connectivity(self, **kwargs):
        baseRepo       = kwargs['args'].dir
        configure_loop = False
        jsonData       = kwargs['jsonData']
        name_prefix    = self.name_prefix
        name_suffix    = ['mgmt', 'migration', 'storage', 'dvs']
        org            = self.org
        path_sep       = kwargs['path_sep']
        policy_type    = 'LAN Connectivity Policy'
        yaml_file      = 'lan_connectivity'
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  A {policy_type} will configure vNIC adapters for Server Profiles.\n')
            print(f'  If failover is not configured the Wizard will create a Pair of vNICs.')
            print(f'  For Instance with a Virtual Host that may have the following vNIC Pairs:')
            print(f'     1. mgmt')
            print(f'     2. migration')
            print(f'     3. storage')
            print(f'     4. dvs\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - {baseRepo}{path_sep}{org}{path_sep}{self.type}{path_sep}{yaml_file}.yaml')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure a {policy_type}?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                loop_count = 1
                policy_loop = False
                while policy_loop == False:
                    if not name_prefix == '': name = '%s-%s' % (name_prefix, 'lcp')
                    else: name = '%s-%s' % (org, 'lcp')
                    kwargs['name']        = ezfunctions.policy_name(name, policy_type)
                    kwargs['description'] = ezfunctions.policy_descr(kwargs['name'], policy_type)

                    # Get LAN Connectivity Policy API Parameters
                    kwargs['multi_select'] = False
                    jsonVars = jsonData['vnic.LanConnectivityPolicy']['allOf'][1]['properties']

                    kwargs['jData'] = deepcopy(jsonVars['TargetPlatform'])
                    kwargs['jData']['default'] = 'FIAttached'
                    kwargs['jData']['varType'] = 'Target Platform'
                    kwargs['target_platform'] = ezfunctions.variablesFromAPI(**kwargs)

                    if kwargs['target_platform'] == 'FIAttached':
                        kwargs['jData'] = deepcopy(jsonVars['AzureQosEnabled'])
                        kwargs['jData']['varInput'] = f'Do you want to Enable AzureStack-Host QoS?'
                        kwargs['jData']['varName']  = 'AzureStack-Host QoS'
                        kwargs['enable_azure_stack_host_qos'] = ezfunctions.varBoolLoop(**kwargs)

                        kwargs['jData'] = deepcopy(jsonVars['IqnAllocationType'])
                        kwargs['jData']['varType'] = 'Iqn Allocation Type'
                        kwargs['iqn_allocation_type'] = ezfunctions.variablesFromAPI(**kwargs)

                        if kwargs['iqn_allocation_type'] == 'Pool':
                            kwargs['iqn_static_identifier'] = ''
                            kwargs['allow_opt_out'] = False
                            kwargs['policy'] = 'pools.iqn.iqn_pool'
                            kwargs = policy_select_loop(**kwargs)
                            kwargs['iqn_pool'] = kwargs['iqn_pool']

                        elif kwargs['iqn_allocation_type'] == 'Static':
                                kwargs['iqn_pool'] = ''
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
                                    question = input(f'\nWould you Like the script to auto generate an IQN For you?'\
                                        '  Enter "Y" or "N" [Y]: ')
                                    if question == '' or question == 'Y':
                                        kwargs['iqn_static_identifier'] = f'iqn.1984-12.com.cisco.iscsi:{secrets.token_hex(6)}'
                                        print(f'IQN is {kwargs["iqn_static_identifier"]}')
                                        valid = True
                                    elif question == 'N':
                                        kwargs['jData'] = deepcopy(jsonVars['StaticIqnName'])
                                        kwargs['jData']['varInput'] = 'What is the Static IQN you would like to assign'\
                                            ' to this LAN Policy?'
                                        kwargs['jData']['varName'] = 'Static IQN'
                                        kwargs['iqn_static_identifier'] = ezfunctions.varStringLoop(**kwargs)
                    else:
                        kwargs['iqn_allocation_type'] = 'None'
                        kwargs['iqn_pool'] = ''
                        kwargs['iqn_static_identifier'] = ''

                    global_name = kwargs['name']
                    print(f'\n-----------------------------------------------------------------------------------------------\n')
                    print(f'Easy IMM will now begin the vNIC Configuration Process.  We recommend the following guidlines:')
                    print(f'  - For Baremetal Operating Systems like Linux and Windows; use a Failover Policy with a single vnic')
                    print(f'  - For a Virtual Environment it is a Good Practice to not use Failover and use the following')
                    print(f'    vnic layout:')
                    print(f'    1. mgmt')
                    print(f'    2. migration')
                    print(f'    3. storage')
                    print(f'    4. dvs')
                    print(f'If you select no for Failover Policy the script will create mirroring vnics for A and B')
                    print(f'\n-----------------------------------------------------------------------------------------------\n')
                    inner_loop_count = 1
                    pci_order_consumed = {0:[]},{1:[]}

                    kwargs['allow_opt_out'] = True
                    kwargs['policy'] = 'policies.san_connectivity.san_connectivity_policy'
                    kwargs = policy_select_loop(**kwargs)
                    san_connectivity_policy = kwargs['san_connectivity_policy']

                    if not san_connectivity_policy == '':
                        for item in kwargs['immDict']['orgs'][org]['san_connectivity']:
                            if item['name'] == san_connectivity_policy:
                                for i in item['vhbas']:
                                    if i.get('placement_pci_link') == None: placement_pci_link = 0
                                    else: placement_pci_link = i['placement_pci_link']
                                    pci_order_consumed[placement_pci_link].append(i['placement_pci_order'])
                    kwargs['order_consumed_0'] = max(pci_order_consumed[0])
                    kwargs['order_consumed_1'] = max(pci_order_consumed[1])
                    kwargs['vnics'] = []
                    vnic_loop = False
                    while vnic_loop == False:
                        jsonVars = jsonData['vnic.EthIf']['allOf'][1]['properties']

                        kwargs['jData'] = deepcopy(jsonVars['FailoverEnabled'])
                        kwargs['jData']['varInput'] = f'Do you want to Enable Failover for this vNIC?'
                        kwargs['jData']['varName']  = 'Enable Failover'
                        kwargs['enable_failover'] = ezfunctions.varBoolLoop(**kwargs)

                        print(f' inner loop count is {inner_loop_count}')
                        if kwargs['enable_failover'] == True:
                            fabrics = ['a']
                            varDefault = 'vnic'
                        else:
                            fabrics = ['a','b']
                            if inner_loop_count < 5: varDefault = name_suffix[inner_loop_count -1]
                            else: varDefault = 'vnic'
                        kwargs['jData'] = deepcopy(jsonVars['Name'])
                        kwargs['jData']['minimum']  = 1
                        kwargs['jData']['varInput'] = f'What is the name for this vNIC? [{varDefault}]:'
                        kwargs['jData']['varName']  = 'vNIC Name'
                        Name = ezfunctions.varStringLoop(**kwargs)
                        for x in fabrics:
                            kwargs[f'name-{x}'] = '%s-%s' % (Name, x)

                        if kwargs['target_platform'] == 'FIAttached':
                            kwargs['jData'] = deepcopy(jsonVars['MacAddressType'])
                            kwargs['jData']['varType'] = 'Mac Address Type'
                            kwargs[f'mac_address_allocation_type'] = ezfunctions.variablesFromAPI(**kwargs)

                            if kwargs[f'mac_address_allocation_type'] == 'POOL':
                                for x in fabrics:
                                    kwargs['name'] = kwargs[f'name-{x}']
                                    kwargs['allow_opt_out'] = False
                                    kwargs['policy'] = 'pools.mac.mac_pool'
                                    kwargs['optional_message'] = f'{kwargs[f"name-{x}"]} MAC Address Pool'
                                    kwargs = policy_select_loop(**kwargs)
                                    kwargs[f'mac_pool_{x}'] = kwargs[f'mac_pool']
                                    kwargs.pop('optional_message')
                            else:
                                for x in fabrics:
                                    kwargs['jData'] = deepcopy(jsonVars['StaticMacAddress'])
                                    if kwargs['enable_failover'] == True:
                                        kwargs['jData']['varInput'] = f'What is the static MAC Address?'
                                    else:
                                        kwargs['jData']['varInput'] = f'What is the static MAC Address for Fabric {x.upper()}?'
                                    if kwargs['enable_failover'] == True: kwargs['jData']['varName'] = f'Static Mac Address'
                                    else: kwargs['jData']['varName'] = f'Fabric {x} Mac Address'
                                    kwargs['jData']['pattern'] = jsonData['boot.Pxe']['allOf'][1]['properties'][
                                        'MacAddress']['pattern']
                                    kwargs[f'static_mac_{x}'] = ezfunctions.varStringLoop(**kwargs)

                        # Pull in API Attributes
                        jsonVars = jsonData['vnic.PlacementSettings']['allOf'][1]['properties']

                        for x in fabrics:
                            kwargs['jData'] = deepcopy(jsonVars['PciLink'])
                            if kwargs['enable_failover'] == False:
                                kwargs['jData']['description'] = kwargs['jData']['description'] + \
                                    f'\n\nPCI Link For Fabric {x.upper()}'
                            if kwargs['enable_failover'] == True: kwargs['jData']['varType'] = 'PCI Link'
                            else: kwargs['jData']['varType'] = f'Fabric {x.upper()} PCI Link'
                            kwargs[f'placement_pci_link_{x}'] = ezfunctions.varNumberLoop(**kwargs)

                            if kwargs['target_platform'] == 'Standalone':
                                kwargs['jData'] = deepcopy(jsonVars['Uplink'])
                                kwargs['jData']['varInput'] = f'What is the {jsonVars["Uplink"]["description"]}?'
                                kwargs['jData']['varType']  = 'Adapter Port'
                                kwargs[f'placement_uplink_port_{x}'] = ezfunctions.varNumberLoop(**kwargs)

                            kwargs['jData'] = deepcopy(jsonVars['Id'])
                            kwargs['jData']['default']  = 'MLOM'
                            kwargs['jData']['varInput'] = f'What is the {jsonVars["Id"]["description"]}?'
                            kwargs['jData']['varType']  = 'vNIC PCIe Slot'
                            kwargs[f'placement_slot_id_{x}'] = ezfunctions.varStringLoop(**kwargs)

                        # Pull in API Attributes
                        jsonVars = jsonData['vnic.Cdn']['allOf'][1]['properties']

                        kwargs['jData'] = deepcopy(jsonVars['Source'])
                        kwargs['jData']['varType'] = 'CDN Source'
                        kwargs['cdn_source'] = ezfunctions.variablesFromAPI(**kwargs)

                        if kwargs['cdn_source'] == 'user':
                            for x in fabrics:
                                kwargs['jData'] = deepcopy(jsonVars['Value'])
                                kwargs['jData']['minimum'] = 1
                                if kwargs['enable_failover'] == True:
                                    kwargs['jData']['varInput'] = 'What is the value for the Consistent Device Name?'
                                else:
                                    kwargs['jData']['varInput'] = f'What is the value for Fabric {x.upper()} Consistent Device Name?'
                                kwargs['jData']['varName'] = 'CDN Name'
                                kwargs[f'cdn_value_{x}'] = ezfunctions.varStringLoop(**kwargs)

                        kwargs['name'] = kwargs['name'].split('-')[0]
                        policy_list = ['policies.ethernet_adapter.ethernet_adapter_policy']
                        if kwargs['target_platform'] == 'Standalone':
                            policy_list.append('policies.ethernet_network.ethernet_network_policy')
                        else:
                            policy_list.append('policies.ethernet_network_control.ethernet_network_control_policy')
                            policy_list.append('policies.ethernet_network_group.ethernet_network_group_policy')
                        policy_list.append('policies.ethernet_qos.ethernet_qos_policy')
                        kwargs['allow_opt_out'] = False
                        for policy in policy_list:
                            kwargs['policy'] = policy
                            kwargs = policy_select_loop(**kwargs)
                        if not kwargs['iqn_allocation_type'] == 'None':
                            kwargs['policy'] = 'policies.iscsi_boot.iscsi_boot_policy'
                            if kwargs['enable_failover'] == False:
                                kwargs['optional_message'] = f'iSCSI Boot Policy for Fabric {x.upper()}'
                            kwargs = policy_select_loop(**kwargs)


                        polVars = {}
                        polVars['names'] = []
                        if kwargs['cdn_source'] == 'user':
                            polVars['cdn_source'] == 'user'
                            polVars['cdn_values'] = []
                        if kwargs['enable_failover'] == True: polVars['enable_failover'] == True
                        for i in policy_list.split(',')[2]: polVars[i] = kwargs[i]
                        placement_list = ['placement_pci_link', 'placement_slot_id']
                        if kwargs['target_platform'] == 'FIAttached':
                            if kwargs['mac_address_allocation_type'] == 'POOL': polVars['mac_address_pools']= []
                            else:
                                polVars['mac_address_allocation_type'] = kwargs['mac_address_allocation_type']
                                polVars['mac_address_static'] = []
                        else: placement_list.append('placement_uplink_port')
                        for i in placement_list: polVars[i] = []
                        for x in fabrics:
                            for i in placement_list: polVars[i].append(f'{i}_{x}')
                        for i in placement_list: polVars[i] = list(set(polVars[i]))
                        polVars['placement_pci_order'] = []
                        for x in fabrics:
                            polVars['names'].append(kwargs[f'name_{x}'])
                            if kwargs['cdn_source'] == 'user': polVars['cdn_values'].append(kwargs[f'cdn_value_{x}'])
                            if kwargs['target_platform'] == 'FIAttached':
                                if kwargs['mac_address_allocation_type'] == 'POOL':
                                    polVars['mac_address_pools'].append(kwargs[f'mac_pool_{x}'])
                                else: polVars['mac_address_static'].append(kwargs[f'static_mac_{x}'])
                            polVars['placement_pci_order'].append(kwargs[f'order_consumed_{kwargs[f"placement_pci_link_{x}"]}'])
                            kwargs[f'order_consumed_{kwargs[f"placement_pci_link_{x}"]}'] += 1
                        
                        # Remove Placement Values if Match Defaults
                        if polVars['placement_pci_link'] == [0]: polVars.pop('placement_pci_link')
                        if polVars['placement_slot_id'] == ['MLOM']: polVars.pop('placement_slot_id')
                        if not polVars.get('placement_uplink_port') == None:
                            if polVars['placement_uplink_port'] == [0]: polVars.pop('placement_pci_link')

                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        print(textwrap.indent(yaml.dump(polVars, Dumper=MyDumper, default_flow_style=False), ' '*4, predicate=None))
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        valid_confirm = False
                        while valid_confirm == False:
                            confirm_conf = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
                            pol_type = 'vNIC'
                            if confirm_conf == 'Y' or confirm_conf == '':
                                kwargs['vnics'].append(polVars)
                                valid_exit = False
                                while valid_exit == False:
                                    if inner_loop_count < 4:
                                        configure_loop, policy_loop = ezfunctions.exit_default(pol_type, 'Y')
                                    else: vnic_loop, valid_confirm = ezfunctions.exit_default(pol_type, 'N')
                                    if vnic_loop == False and valid_confirm == False:
                                        inner_loop_count += 1
                                        valid_confirm = True
                                        valid_exit = True
                                    else:
                                        valid_exit = True
                            elif confirm_conf == 'N':
                                ezfunctions.message_starting_over(pol_type)
                                valid_confirm = True
                            else: ezfunctions.message_invalid_y_or_n('short')
                    
                    polVars = {
                        'name': global_name,
                        'enable_azure_stack_host_qos': kwargs['enable_azure_stack_host_qos'],
                        'iqn_allocation_type': kwargs['iqn_allocation_type'],
                        'iqn_pool': kwargs['iqn_pool'],
                        'iqn_static_identifier': kwargs['iqn_static_identifier'],
                        'target_platform': kwargs['target_platform'],
                        'vnics': kwargs['vnics']
                    }
                    if kwargs['target_platform'] == 'FIAttached' : polVars.pop('target_platform')
                    if kwargs['iqn_allocation_type'] == 'None':
                        iqn_list = ['iqn_allocation_type', 'iqn_pool', 'iqn_static_identifier']
                        for i in iqn_list: polVars.pop(i)
                    elif kwargs['iqn_allocation_type'] == 'Static': polVars.pop('iqn_pool')
                    elif kwargs['iqn_allocation_type'] == 'Pool': polVars.pop('iqn_static_identifier')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(textwrap.indent(yaml.dump(polVars, Dumper=MyDumper, default_flow_style=False), ' '*4, predicate=None))
                    print(f'-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
                        if confirm_policy == 'Y' or confirm_policy == '':
                            # Add Policy Variables to immDict
                            kwargs['class_path'] = 'intersight,policies,lan_connectivity'
                            kwargs = ezfunctions.ez_append(polVars, **kwargs)

                            configure_loop, policy_loop = ezfunctions.exit_default(policy_type, 'N')
                            valid_confirm = True
                        elif confirm_policy == 'N':
                            ezfunctions.message_starting_over(policy_type)
                            valid_confirm = True
                        else: ezfunctions.message_invalid_y_or_n('short')
            elif configure == 'N': configure_loop = True
            else: ezfunctions.message_invalid_y_or_n('long')
        # Return kwargs
        return kwargs

    #==============================================
    # Link Aggregation Policy Module
    #==============================================
    def link_aggregation(self, **kwargs):
        baseRepo       = kwargs['args'].dir
        configure_loop = False
        name_prefix    = self.name_prefix
        name_suffix    = 'link-agg'
        org            = self.org
        path_sep       = kwargs['path_sep']
        policy_type    = 'Link Aggregation Policy'
        yaml_file      = 'ethernet'
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  A Link Aggregation Policy will assign LACP settings to the Ethernet Port-Channels and')
            print(f'  uplinks.  We recommend the default wizard settings so you will only be asked for the ')
            print(f'  name and description for the Policy.  You only need one of these policies for ')
            print(f'  Organization {org}.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - {baseRepo}{path_sep}{org}{path_sep}{self.type}{path_sep}{yaml_file}.yaml')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            policy_loop = False
            while policy_loop == False:
                polVars = {}
                if not name_prefix == '': name = f'{name_prefix}-{name_suffix}'
                else: name = f'{org}-{name_suffix}'
                polVars['name']        = ezfunctions.policy_name(name, policy_type)
                polVars['description'] = ezfunctions.policy_descr(polVars['name'], policy_type)

                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(textwrap.indent(yaml.dump(polVars, Dumper=MyDumper, default_flow_style=False), ' '*4, predicate=None))
                print(f'-------------------------------------------------------------------------------------------\n')
                valid_confirm = False
                while valid_confirm == False:
                    confirm_policy = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                    if confirm_policy == 'Y' or confirm_policy == '':
                        # Add Policy Variables to immDict
                        kwargs['class_path'] = 'intersight,policies,link_aggregation'
                        kwargs = ezfunctions.ez_append(polVars, **kwargs)

                        configure_loop, policy_loop = ezfunctions.exit_default(policy_type, 'N')
                        valid_confirm = True
                    elif confirm_policy == 'N':
                        ezfunctions.message_starting_over(policy_type)
                        valid_confirm = True
                    else: ezfunctions.message_invalid_y_or_n('long')
        # Return kwargs
        return kwargs

    #==============================================
    # Link Control Policy Module
    #==============================================
    def link_control(self, **kwargs):
        baseRepo       = kwargs['args'].dir
        configure_loop = False
        name_prefix    = self.name_prefix
        name_suffix    = 'link-ctrl'
        org            = self.org
        path_sep       = kwargs['path_sep']
        policy_type    = 'Link Control Policy'
        yaml_file      = 'ethernet'
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  A Link Control Policy will configure the Unidirectional Link Detection Protocol for')
            print(f'  Ethernet Uplinks/Port-Channels.')
            print(f'  We recommend the wizards default parameters so you will only be asked for the name')
            print(f'  and description for the Policy.  You only need one of these policies for')
            print(f'  Organization {org}.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - {baseRepo}{path_sep}{org}{path_sep}{self.type}{path_sep}{yaml_file}.yaml')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            policy_loop = False
            while policy_loop == False:
                polVars = {}
                if not name_prefix == '': name = f'{name_prefix}-{name_suffix}'
                else: name = f'{org}-{name_suffix}'
                polVars['name']        = ezfunctions.policy_name(name, policy_type)
                polVars['description'] = ezfunctions.policy_descr(polVars['name'], policy_type)

                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(textwrap.indent(yaml.dump(polVars, Dumper=MyDumper, default_flow_style=False), ' '*4, predicate=None))
                print(f'-------------------------------------------------------------------------------------------\n')
                valid_confirm = False
                while valid_confirm == False:
                    confirm_policy = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                    if confirm_policy == 'Y' or confirm_policy == '':
                        # Add Policy Variables to immDict
                        kwargs['class_path'] = 'intersight,policies,link_control'
                        kwargs = ezfunctions.ez_append(polVars, **kwargs)

                        configure_loop, policy_loop = ezfunctions.exit_default(policy_type, 'N')
                        valid_confirm = True
                    elif confirm_policy == 'N':
                        ezfunctions.message_starting_over(policy_type)
                        valid_confirm = True
                    else: ezfunctions.message_invalid_y_or_n('long')
        # Return kwargs
        return kwargs

    #==============================================
    # SAN Connectivity Policy Module
    #==============================================
    def san_connectivity(self, **kwargs):
        baseRepo       = kwargs['args'].dir
        configure_loop = False
        jsonData       = kwargs['jsonData']
        name_prefix    = self.name_prefix
        name_suffix    = 'scp'
        org            = self.org
        path_sep       = kwargs['path_sep']
        policy_type    = 'SAN Connectivity Policy'
        yaml_file      = 'san_connectivity'
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  You can Skip this policy if you are not configuring Fibre-Channel.\n')
            print(f'  A {policy_type} will configure vHBA adapters for Server Profiles.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - {baseRepo}{path_sep}{org}{path_sep}{self.type}{path_sep}{yaml_file}.yaml')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure a {policy_type}?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                policy_loop = False
                while policy_loop == False:
                    polVars = {}
                    if not name_prefix == '': name = f'{name_prefix}-{name_suffix}'
                    else: name = f'{org}-{name_suffix}'
                    polVars['name']        = ezfunctions.policy_name(name, policy_type)
                    polVars['description'] = ezfunctions.policy_descr(polVars['name'], policy_type)

                    # Pull in Attributes from API Data
                    kwargs["multi_select"] = False
                    jsonVars = jsonData['vnic.SanConnectivityPolicy']['allOf'][1]['properties']
                    
                    kwargs['jData'] = deepcopy(jsonVars['TargetPlatform'])
                    kwargs['jData']["default"] = 'FIAttached'
                    kwargs['jData']['varType'] = 'Target Platform'
                    kwargs["target_platform"] = ezfunctions.variablesFromAPI(**kwargs)

                    if polVars["target_platform"] == 'FIAttached':
                        kwargs['jData'] = deepcopy(jsonVars['WwnnAddressType'])
                        kwargs['jData']["varType"] = 'WWNN Allocation Type'
                        kwargs["wwnn_allocation_type"] = ezfunctions.variablesFromAPI(**kwargs)
                        polVars["wwnn_pool"] = ''
                        polVars["wwnn_static"] = ''
                        if kwargs["wwnn_allocation_type"] == 'POOL':
                            kwargs["allow_opt_out"] = False
                            kwargs['policy'] = 'pools.wwnn.wwnn_pool'
                            kwargs = policy_select_loop(**kwargs)
                        else:
                            kwargs['jData'] = deepcopy(jsonVars['StaticWwnnAddress'])
                            kwargs['jData']['varInput'] = 'What is the Static WWNN you would like to assign to this SAN Policy?'
                            kwargs['jData']['varName']  = 'Static WWNN'
                            static_wwnn = ezfunctions.varStringLoop(**kwargs)
                    policy_name = polVars['name']
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'   BEGINNING vHBA Creation Process')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    fabrics = ['a', 'b']
                    kwargs['order_consumed_0'] = 0
                    kwargs['order_consumed_1'] = 0
                    kwargs['vhbas'] = []
                    inner_loop_count = 1
                    vhba_loop = False
                    while vhba_loop == False:
                        policy_list = [
                            'policies.fc_zone.fc_zone_policies',
                            'policies.fibre_channel_adapter.fibre_channel_adapter_policy',
                            'policies.fibre_channel_qos.fibre_channel_qos_policy'
                        ]
                        for kwargs['policy'] in policy_list:
                            if 'fc_zone' in kwargs['policy']:
                                kwargs["allow_opt_out"] = True
                                kwargs['policy_multi_select'] = True
                            else: kwargs["allow_opt_out"] = False
                            kwargs = policy_select_loop(**kwargs)
                        for x in fabrics:
                            kwargs['policy'] = 'policies.fibre_channel_network.fibre_channel_network_policy'
                            kwargs["name"] = f"the {kwargs['policy'].split(',')[2]} for vHBA on Fabric {x.upper()}"
                            kwargs = policy_select_loop(**kwargs)
                            kwargs[f'fc_network_policy_{x}'] = kwargs['fibre_channel_network_policy']
                        for x in fabrics:
                            valid = False
                            while valid == False:
                                kwargs[f'name_{x}'] = input(f'What is the name for Fabric {x.upper} vHBA?  [vhba-{x}]: ')
                                if kwargs[f'name_{x}'] == '': kwargs[f'name_{x}'] = 'vhba-%s' % (x)
                                valid = validating.vname('vNIC Name', kwargs[f'name_{x}'])
                        jsonVars = jsonData['vnic.FcIfInventory']['allOf'][1]['properties']
                        kwargs['jData'] = deepcopy(jsonVars['PersistentBindings'])
                        kwargs['jData']['varInput'] = f'Do you want to Enable Persistent LUN Bindings?'
                        kwargs['jData']['varName']  = 'Persistent LUN Bindings'
                        kwargs['persistent_lun_bindings'] = ezfunctions.varBoolLoop(**kwargs)

                        # Pull in API Attributes
                        jsonVars = jsonData['vnic.PlacementSettings']['allOf'][1]['properties']
                        for x in fabrics:
                            kwargs['jData'] = deepcopy(jsonVars['PciLink'])
                            if kwargs['enable_failover'] == False:
                                kwargs['jData']['description'] = kwargs['jData']['description'] + \
                                    f'\n\nPCI Link For Fabric {x.upper()}'
                            if kwargs['enable_failover'] == True: kwargs['jData']['varType'] = 'PCI Link'
                            else: kwargs['jData']['varType'] = f'Fabric {x.upper()} PCI Link'
                            kwargs[f'placement_pci_link_{x}'] = ezfunctions.varNumberLoop(**kwargs)

                            if kwargs['target_platform'] == 'Standalone':
                                kwargs['jData'] = deepcopy(jsonVars['Uplink'])
                                kwargs['jData']['varInput'] = f'What is the {jsonVars["Uplink"]["description"]}?'
                                kwargs['jData']['varType']  = 'Adapter Port'
                                kwargs[f'placement_uplink_port_{x}'] = ezfunctions.varNumberLoop(**kwargs)
                            kwargs['jData'] = deepcopy(jsonVars['Id'])
                            kwargs['jData']['default']  = 'MLOM'
                            kwargs['jData']['varInput'] = f'What is the {jsonVars["Id"]["description"]}?'
                            kwargs['jData']['varType']  = 'vNIC PCIe Slot'
                            kwargs[f'placement_slot_id_{x}'] = ezfunctions.varStringLoop(**kwargs)

                        jsonVars = jsonData['vnic.FcIf']['allOf'][1]['properties']
                        kwargs['jData'] = deepcopy(jsonVars['Type'])
                        kwargs['jData']['varType'] = 'vHBA Type'
                        kwargs['vhba_type'] = ezfunctions.variablesFromAPI(**kwargs)

                        if polVars["target_platform"] == 'FIAttached':
                            kwargs['jData'] = deepcopy(jsonVars['WwpnAddressType'])
                            kwargs['jData']['varType'] = 'WWPN Allocation Type'
                            kwargs['wwpn_allocation_type'] = ezfunctions.variablesFromAPI(**kwargs)
                            if kwargs["wwpn_allocation_type"] == 'POOL':
                                kwargs["allow_opt_out"] = False
                                kwargs['policy'] = 'pools.wwpn_pools.wwpn_pool'
                                for x in fabrics:
                                    print(f'\n{"-"*91}\n')
                                    print(f'  Select the WWPN Pool for Fabric {x.upper()}:')
                                    print(f'\n{"-"*91}\n')
                                    kwargs = policy_select_loop(**kwargs)
                                    kwargs[f'wwpn_pool_{x}'] = kwargs[f'wwpn_pool']
                            else:
                                for x in fabrics:
                                    kwargs['jData'] = deepcopy(jsonVars['StaticWwpnAddress'])
                                    kwargs['jData']['varInput'] = f'What is the Static WWPN you would like to'\
                                        f' assign to Fabric {x.upper()}?'
                                    kwargs['jData']['varName']  = 'WWPN Static Address'
                                    kwargs[f'static_wwpn_{x}'] = ezfunctions.varStringLoop(**kwargs)
                        polVars = {}
                        polVars['names'] = []
                        polVars['fibre_channel_network_policies'] = []
                        for i in policy_list.split(',')[2]: polVars[i] = kwargs[i]
                        placement_list = ['placement_pci_link', 'placement_slot_id']
                        if kwargs['target_platform'] == 'FIAttached':
                            if kwargs['wwpn_allocation_type'] == 'POOL': polVars['wwpn_pools']= []
                            else:
                                polVars['wwpn_allocation_type'] = kwargs['wwpn_allocation_type']
                                polVars['wwpn_address_static'] = []
                        else: placement_list.append('placement_uplink_port')
                        for i in placement_list: polVars[i] = []
                        for x in fabrics:
                            for i in placement_list: polVars[i].append(f'{i}_{x}')
                        for i in placement_list: polVars[i] = list(set(polVars[i]))
                        polVars['placement_pci_order'] = []
                        polVars['persistent_lun_bindings'] = kwargs['persistent_lun_bindings']
                        for x in fabrics:
                            polVars['fibre_channel_network_policies'].append(kwargs[f'fc_network_policy_{x}'])
                            polVars['names'].append(kwargs[f'name_{x}'])
                            if kwargs['target_platform'] == 'FIAttached':
                                if kwargs['wwpn_allocation_type'] == 'POOL':
                                    polVars['wwpn_pools'].append(kwargs[f'mac_pool_{x}'])
                                else: polVars['wwpn_address_static'].append(kwargs[f'static_wwpn_{x}'])
                            polVars['placement_pci_order'].append(kwargs[f'order_consumed_{kwargs[f"placement_pci_link_{x}"]}'])
                            kwargs[f'order_consumed_{kwargs[f"placement_pci_link_{x}"]}'] += 1
                        
                        # Remove Placement Values if Match Defaults
                        if polVars['placement_pci_link'] == [0]: polVars.pop('placement_pci_link')
                        if polVars['placement_slot_id'] == ['MLOM']: polVars.pop('placement_slot_id')
                        if not polVars.get('placement_uplink_port') == None:
                            if polVars['placement_uplink_port'] == [0]: polVars.pop('placement_pci_link')

                        # Remove Placement Values if Match Defaults
                        if polVars['placement_pci_link'] == [0]: polVars.pop('placement_pci_link')
                        if polVars['placement_slot_id'] == ['MLOM']: polVars.pop('placement_slot_id')
                        if not polVars.get('placement_uplink_port') == None:
                            if polVars['placement_uplink_port'] == [0]: polVars.pop('placement_pci_link')
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        print(textwrap.indent(yaml.dump(polVars, Dumper=MyDumper, default_flow_style=False), ' '*4, predicate=None))
                        print(f'-------------------------------------------------------------------------------------------\n')
                        valid_confirm = False
                        while valid_confirm == False:
                            confirm_conf = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
                            pol_type = 'vHBA'
                            if confirm_conf == 'Y' or confirm_conf == '':
                                kwargs["vhbas"].append(polVars)
                                valid_exit = False
                                while valid_exit == False:
                                    vhba_loop, valid_confirm = ezfunctions.exit_default(pol_type, 'N')
                                    if vhba_loop == False and valid_confirm == False:
                                        inner_loop_count += 1
                                        valid_confirm = True
                                        valid_exit = True
                                    else: valid_exit = True
                            elif confirm_conf == 'N':
                                pol_type = 'vHBA'
                                ezfunctions.message_starting_over(pol_type)
                                valid_confirm = True
                            else: ezfunctions.message_invalid_y_or_n('short')

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(textwrap.indent(yaml.dump(polVars, Dumper=MyDumper, default_flow_style=False), ' '*4, predicate=None))
                    print(f'-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                        if confirm_policy == 'Y' or confirm_policy == '':
                            # Add Policy Variables to immDict
                            kwargs['class_path'] = 'intersight,policies,lan_connectivity'
                            kwargs = ezfunctions.ez_append(polVars, **kwargs)

                            configure_loop, policy_loop = ezfunctions.exit_default(policy_type, 'N')
                            valid_confirm = True
                        elif confirm_policy == 'N':
                            ezfunctions.message_starting_over(policy_type)
                            valid_confirm = True
                        else: ezfunctions.message_invalid_y_or_n('short')
            elif configure == 'N': configure_loop = True
            else: ezfunctions.message_invalid_y_or_n('long')
        # Return kwargs
        return kwargs

    #==============================================
    # Switch Control Policy Module
    #==============================================
    def switch_control(self, **kwargs):
        baseRepo       = kwargs['args'].dir
        configure_loop = False
        jsonData       = kwargs['jsonData']
        name_prefix    = self.name_prefix
        name_suffix    = 'sw-ctrl'
        org            = self.org
        path_sep       = kwargs['path_sep']
        policy_type    = 'Switch Control Policy'
        yaml_file      = 'switch'
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  A Switch Control Policy will configure Unidirectional Link Detection Protocol and')
            print(f'  MAC Address Learning Settings for the UCS Domain Profile.')
            print(f'  We recommend the settings the wizard is setup to push.  So you will only be asked for')
            print(f'  the name and description for the Policy.  You only need one of these policies for')
            print(f'  Organization {org}.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - {baseRepo}{path_sep}{org}{path_sep}{self.type}{path_sep}{yaml_file}.yaml')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            policy_loop = False
            while policy_loop == False:
                polVars = {}
                if not name_prefix == '': name = f'{name_prefix}-{name_suffix}'
                else: name = f'{org}-{name_suffix}'
                polVars['name']        = ezfunctions.policy_name(name, policy_type)
                polVars['description'] = ezfunctions.policy_descr(polVars['name'], policy_type)
                polVars["vlan_port_count_optimization"] = False

                # Pull Information from the API
                polVars["multi_select"] = False
                jsonVars = jsonData['fabric.FcNetworkPolicy']['allOf'][1]['properties']

                # Ethernet Switching Mode
                kwargs['jData'] = deepcopy(jsonVars['EthernetSwitchingMode'])
                kwargs['jData']['varType'] = 'Ethernet Switching Mode'
                polVars["ethernet_switching_mode"] = ezfunctions.variablesFromAPI(**kwargs)

                # Fibre-Channel Switching Mode
                kwargs['jData'] = deepcopy(jsonVars['FcSwitchingMode'])
                kwargs['jData']['varType'] = 'Fibre-Channel Switching Mode'
                polVars["fc_switching_mode"] = ezfunctions.variablesFromAPI(**kwargs)

                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(textwrap.indent(yaml.dump(polVars, Dumper=MyDumper, default_flow_style=False), ' '*4, predicate=None))
                print(f'-------------------------------------------------------------------------------------------\n')
                valid_confirm = False
                while valid_confirm == False:
                    confirm_policy = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                    if confirm_policy == 'Y' or confirm_policy == '':
                        # Add Policy Variables to immDict
                        kwargs['class_path'] = 'intersight,policies,switch_control'
                        kwargs = ezfunctions.ez_append(polVars, **kwargs)

                        configure_loop, policy_loop = ezfunctions.exit_default(policy_type, 'N')
                        valid_confirm = True
                    elif confirm_policy == 'N':
                        ezfunctions.message_starting_over(policy_type)
                        valid_confirm = True
                    else: ezfunctions.message_invalid_y_or_n('long')
        # Return kwargs
        return kwargs

    #==============================================
    # System QoS Policy Module
    #==============================================
    def system_qos(self, **kwargs):
        baseRepo       = kwargs['args'].dir
        configure_loop = False
        ezData         = kwargs['ezData']
        jsonData       = kwargs['jsonData']
        name_prefix    = self.name_prefix
        name_suffix    = 'qos'
        org            = self.org
        path_sep       = kwargs['path_sep']
        policy_type    = 'System QoS Policy'
        yaml_file      = 'switch'
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
            print(f'  - {baseRepo}{path_sep}{org}{path_sep}{self.type}{path_sep}{yaml_file}.yaml')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            policy_loop = False
            while policy_loop == False:
                polVars = {}
                if not name_prefix == '': name = f'{name_prefix}-{name_suffix}'
                else: name = f'{org}-{name_suffix}'
                polVars['name']        = ezfunctions.policy_name(name, policy_type)
                polVars['description'] = ezfunctions.policy_descr(polVars['name'], policy_type)

                # Pull Information from the API
                polVars["multi_select"] = False
                jsonVars = jsonData['fabric.QosClass']['allOf'][1]['properties']

                # Ethernet Switching Mode
                kwargs['jData'] = deepcopy(jsonVars['Mtu'])
                kwargs['jData']['default'] = True
                kwargs['jData']['varInput'] = f'Do you want to enable Jumbo MTU?'
                kwargs['jData']['varType']  = 'Domain MTU'
                mtu = ezfunctions.varBoolLoop(**kwargs)
                if mtu == True: domain_mtu = 9216
                else: domain_mtu = 1500

                priorities = ['Platinum', 'Gold', 'FC', 'Silver', 'Bronze', 'Best Effort']
                polVars['classes'] = []
                for i in priorities:
                    iDict = ezData['ezimm']['allOf'][1]['properties']['systemQos'][i]
                    if i == 'FC': class_mtu = 2240
                    else: class_mtu = domain_mtu
                    polVars['classes'].append({
                        'bandwidth_percent':iDict['bandwidth_percent'],
                        'cos':iDict['bandwidth_percent'],
                        'mtu':class_mtu,
                        'multicast_optimize':iDict['multicast_optimize'],
                        'packet_drop':iDict['packet_drop'],
                        'priority':i,
                        'state':'Enabled',
                        'weight':iDict['weight'],
                    })
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(textwrap.indent(yaml.dump(polVars, Dumper=MyDumper, default_flow_style=False), ' '*4, predicate=None))
                print(f'-------------------------------------------------------------------------------------------\n')
                valid_confirm = False
                while valid_confirm == False:
                    confirm_policy = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                    if confirm_policy == 'Y' or confirm_policy == '':
                        # Add Policy Variables to immDict
                        kwargs['class_path'] = 'intersight,policies,system_qos'
                        kwargs = ezfunctions.ez_append(polVars, **kwargs)

                        configure_loop, policy_loop = ezfunctions.exit_default(policy_type, 'N')
                        valid_confirm = True
                    elif confirm_policy == 'N':
                        ezfunctions.message_starting_over(policy_type)
                        valid_confirm = True
                    else: ezfunctions.message_invalid_y_or_n('long')
        # Return kwargs
        return kwargs

    #==============================================
    # VLAN Policy Module
    #==============================================
    def vlan(self, **kwargs):
        baseRepo       = kwargs['args'].dir
        configure_loop = False
        name_prefix    = self.name_prefix
        name_suffix    = 'vlan'
        org            = self.org
        path_sep       = kwargs['path_sep']
        policy_type    = 'VLAN Policy'
        yaml_file      = 'vlan'
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
            print(f'  - {baseRepo}{path_sep}{org}{path_sep}{self.type}{path_sep}{yaml_file}.yaml')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            policy_loop = False
            while policy_loop == False:
                polVars = {}
                if not name_prefix == '': name = f'{name_prefix}-{name_suffix}'
                else: name = f'{org}-{name_suffix}'
                polVars['name']  = ezfunctions.policy_name(name, policy_type)
                polVars['description'] = ezfunctions.policy_descr(polVars['name'], policy_type)
                polVars['auto_allow_on_uplinks'] = True

                valid = False
                while valid == False:
                    vlan_list = input(f"Enter the VLAN or List of VLANs to add to {polVars['name']}: ")
                    if not vlan_list == '':
                        vlan_list_expanded = ezfunctions.vlan_list_full(vlan_list)
                        valid_vlan = True
                        for vlan in vlan_list_expanded:
                            valid_vlan = validating.number_in_range('VLAN ID', vlan, 1, 4094)
                            if valid_vlan == False: break
                        if valid_vlan == True:
                            valid_name = False
                            while valid_name == False:
                                if len(vlan_list_expanded) == 1:
                                    vlan_name = '%s' % (input(f'Enter the Name you want to assign to "{vlan_list}".  [{org}]: '))
                                    max = 62
                                else:
                                    vlan_name = '%s' % (input(f'Enter the Prefix Name you want to assign to "{vlan_list}".  [{org}]: '))
                                    max = 55
                                if vlan_name == '': vlan_name = org
                                valid_name = validating.name_rule('VLAN Name', vlan_name, 1, max)
                            nativeVlan = input('Do you want to configure one of the VLANs as a Native VLAN? [press enter to skip]:')
                        if not nativeVlan == '' and valid_vlan == True:
                            native_vlan = ezfunctions.vlan_native_function(vlan_list_expanded, vlan_list)
                            while valid_name == False:
                                native_name = '%s' % (input(f'Enter the Name to assign to the Native VLAN {native_vlan}.  [default]: '))
                                if native_name == '': native_name = 'default'
                                valid_name = validating.name_rule('VLAN Name', vlan_name, 1, 62)
                            valid = True
                        else: native_vlan = ''; valid = True
                    else:
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        print(f'  The allowed vlan list can be in the format of:')
                        print(f'     5 - Single VLAN')
                        print(f'     1-10 - Range of VLANs')
                        print(f'     1,2,3,4,5,11,12,13,14,15 - List of VLANs')
                        print(f'     1-10,20-30 - Ranges and Lists of VLANs')
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                if not native_vlan == '':
                    vlan_list_expanded.remove(int(native_vlan))
                vlan_list = ezfunctions.vlan_list_format(vlan_list_expanded)
                kwargs['name'] = polVars['name']
                kwargs['policy'] = 'policies.multicast.multicast_policy'
                kwargs['allow_opt_out'] = False
                kwargs = policy_select_loop(**kwargs)
                polVars['vlans'] = []
                if not native_vlan == '' and len(vlan_list) > 1:
                    if int(native_vlan) == 1: auto_native = True
                    else: auto_native = False
                    polVars['vlans'].append({
                        'auto_allow_on_uplinks':auto_native,
                        'multicast_policy':kwargs['multicast_policy'],
                        'name':native_name, 'native_vlan':True,
                        'vlan_list':native_vlan
                    })
                polVars['vlans'].append({
                        'multicast_policy':kwargs['multicast_policy'],
                        'name':vlan_name, 'vlan_list':vlan_list
                })
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(textwrap.indent(yaml.dump(polVars, Dumper=MyDumper, default_flow_style=False), ' '*4, predicate=None))
                print(f'-------------------------------------------------------------------------------------------\n')
                valid_confirm = False
                while valid_confirm == False:
                    confirm_policy = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                    if confirm_policy == 'Y' or confirm_policy == '':
                        # Add Policy Variables to immDict
                        kwargs['class_path'] = 'intersight,policies,vlan'
                        kwargs = ezfunctions.ez_append(polVars, **kwargs)

                        configure_loop, policy_loop = ezfunctions.exit_default(policy_type, 'N')
                        valid_confirm = True
                    elif confirm_policy == 'N':
                        ezfunctions.message_starting_over(policy_type)
                        valid_confirm = True
                    else: ezfunctions.message_invalid_y_or_n('long')
        # Return kwargs
        return kwargs

    #==============================================
    # VSAN Policy Module
    #==============================================
    def vsan(self, **kwargs):
        baseRepo       = kwargs['args'].dir
        configure_loop = False
        jsonData       = kwargs['jsonData']
        name_prefix    = self.name_prefix
        org            = self.org
        path_sep       = kwargs['path_sep']
        policy_type    = 'VSAN Policy'
        yaml_file      = 'vsan'
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  You can Skip this policy if you are not configuring Fibre-Channel.\n')
            print(f'  A {policy_type} will define the VSANs Assigned to the Fabric Interconnects.  You will need')
            print(f'  one VSAN Policy for Fabric A and another VSAN Policy for Fabric B.\n')
            print(f'  IMPORTANT Note: The Fabric Interconnects will encapsulate Fibre-Channel traffic locally')
            print(f'                  in a FCoE (Fibre-Channel over Ethernet) VLAN.  This VLAN Must not be')
            print(f'                  already used by the VLAN Policy.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - {baseRepo}{path_sep}{org}{path_sep}{self.type}{path_sep}{yaml_file}.yaml')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure a {policy_type}?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                loop_count = 0
                policy_loop = False
                while policy_loop == False:
                    polVars = {}
                    kwargs['name_prefix'] = name_prefix
                    name = ezfunctions.naming_rule_fabric(loop_count, name_prefix, org)
                    polVars['name'] = ezfunctions.policy_name(name, policy_type)
                    polVars['description'] = ezfunctions.policy_descr(polVars['name'], policy_type)
                    polVars['auto_allow_on_uplinks'] = True
                    # Pull Information from the API
                    kwargs['name'] = polVars['name']
                    kwargs['multi_select'] = False
                    jsonVars = jsonData['fabric.FcNetworkPolicy']['allOf'][1]['properties']

                    # Uplink Trunking
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  Uplink Trunking: Default is No.')
                    print(f'     Most deployments do not enable Uplink Trunking for Fibre-Channel. ')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    kwargs['jData'] = deepcopy(jsonVars['EnableTrunking'])
                    kwargs['jData']['default']  = False
                    kwargs['jData']['varInput'] = f'Do you want to Enable Uplink Trunking for this VSAN Policy?'
                    kwargs['jData']['varName']  = 'Enable Trunking'
                    kwargs['uplink_trunking'] = ezfunctions.varBoolLoop(**kwargs)
                    polVars['vsans'] = []
                    vsan_count = 0
                    vsan_loop = False
                    while vsan_loop == False:
                        valid = False
                        while valid == False:
                            if loop_count % 2 == 0: vsan_id = input(f"Enter the VSAN id to add to {name}. [100]: ")
                            else: vsan_id = input(f"Enter the VSAN id to add to {name}. [200]: ")
                            if loop_count % 2 == 0 and vsan_id == '': vsan_id = 100
                            elif vsan_id == '': vsan_id = 200
                            if re.search(r'[0-9]{1,4}', str(vsan_id)):
                                valid = validating.number_in_range('VSAN ID', vsan_id, 1, 4094)
                            else: ezfunctions.message_invalid_vlan()
                        valid = False
                        while valid == False:
                            fcoe_id = input(f'Enter the VLAN id for the FCOE VLAN to encapsulate "{vsan_id}" over Ethernet.'\
                                f'  [{vsan_id}]: ')
                            if fcoe_id == '': fcoe_id = vsan_id
                            if re.search(r'[0-9]{1,4}', str(fcoe_id)):
                                valid_vlan = validating.number_in_range('VSAN ID', fcoe_id, 1, 4094)
                                if valid_vlan == True:
                                    kwargs['policy'] = 'policies.vlan.vlan_policy'
                                    kwargs['allow_opt_out'] = False
                                    kwargs = policy_select_loop(**kwargs)
                                    vlan_list = []
                                    for item in kwargs['immDict']['orgs'][org]['intersight']['policies']['vlan']:
                                        if item['name'] == kwargs['vlan_policy']:
                                            for i in item['vlans']:
                                                vlan_list.append(i['vlan_list'])
                                    vlan_list = ezfunctions.vlan_list_full(','.join(vlan_list))
                                    overlap = False
                                    for vlan in vlan_list:
                                        if int(vlan) == int(fcoe_id):
                                            ezfunctions.message_fcoe_vlan(fcoe_id, kwargs['vlan_policy'])
                                            overlap = True
                                            break
                                    if overlap == False: valid = True
                                else: ezfunctions.message_invalid_vlan()
                            else: ezfunctions.message_invalid_vlan()
                        jsonVars = jsonData['fabric.Vsan']['allOf'][1]['properties']
                        # VSAN Name
                        kwargs['jData'] = deepcopy(jsonVars['Name'])
                        kwargs['jData']['default'] = f'vsan-{vsan_id}'
                        kwargs['jData']['pattern'] = '^[a-zA-Z0-9\\_\\-]{1,62}$'
                        kwargs['jData']['varInput'] = f'What Name would you like to assign to "{vsan_id}"?'
                        kwargs['jData']['varName'] = 'VSAN Name'
                        vsan_name = ezfunctions.varStringLoop(**kwargs)
                        # Assign the VSAN Scope for this List
                        kwargs['jData'] = deepcopy(jsonVars['VsanScope'])
                        kwargs['jData']['varType'] = 'Vsan Scope'
                        vsan_scope = ezfunctions.variablesFromAPI(**kwargs)
                        vsan = {
                            'fcoe_vlan_id':fcoe_id, 'name':vsan_name,
                            'vsan_id':vsan_id, 'vsan_scope':vsan_scope
                        }
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        print(textwrap.indent(yaml.dump(vsan, Dumper=MyDumper, default_flow_style=False), ' '*4, predicate=None))
                        print(f'-------------------------------------------------------------------------------------------\n')
                        valid_confirm = False
                        while valid_confirm == False:
                            pol_type = 'VSAN'
                            confirm_vsan = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                            if confirm_vsan == 'Y' or confirm_vsan == '':
                                polVars['vsans'].append(vsan)
                                valid_exit = False
                                while valid_exit == False:
                                    valid_exit, vsan_loop = ezfunctions.exit_default(pol_type, 'N')
                                    if valid_exit == True: vsan_count += 1; valid_confirm = True; valid_exit = True
                                    else: valid_confirm = True; valid_exit = True
                            elif confirm_vsan == 'N':
                                ezfunctions.message_starting_over(pol_type)
                                valid_confirm = True
                            else: ezfunctions.message_invalid_y_or_n('short')

                    # Add VSANs to VSAN Policy List
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(textwrap.indent(yaml.dump(polVars, Dumper=MyDumper, default_flow_style=False), ' '*4, predicate=None))
                    print(f'-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                        if confirm_policy == 'Y' or confirm_policy == '':
                            # Add Policy Variables to immDict
                            kwargs['class_path'] = 'intersight,policies,vsan'
                            kwargs = ezfunctions.ez_append(polVars, **kwargs)

                            configure_loop, loop_count, policy_loop = ezfunctions.exit_loop_default_yes(loop_count, policy_type)
                            valid_confirm = True
                        elif confirm_policy == 'N':
                            ezfunctions.message_starting_over(policy_type)
                            valid_confirm = True
                        else: ezfunctions.message_invalid_y_or_n('short')
            elif configure == 'N': configure_loop = True
            else: ezfunctions.message_invalid_y_or_n('long')
        # Return kwargs
        return kwargs

#==============================================
# Select Policy Function
#==============================================
def policy_select_loop(**kwargs):
    ezData = kwargs['ezData']
    policy = kwargs['policy']
    name   = kwargs['name']
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
        inner_var    = kwargs['inner_var']
        kwargs = ezfunctions.policies_parse(inner_type, inner_policy, **kwargs)
        if not len(kwargs['policies'][kwargs['inner_policy']]) > 0:
            valid = False
            while valid == False:
                policy_description = ezfunctions.mod_pol_description(inner_var)
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'   There was no {policy_description} found.')
                print(f'\n-------------------------------------------------------------------------------------------\n')
                if kwargs['allow_opt_out'] == True:
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
            kwargs['name'] = name
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
            print(f'  Starting module to create {policy_description} in Organization {org}')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            lansan_list = ezData['ezimm']['allOf'][1]['properties']['lansan_list']['enum']
            if re.search('pools$', inner_policy):
                kwargs = eval(f'pools.pools(name_prefix, org, inner_type).{inner_policy}(**kwargs)')
            elif inner_policy in lansan_list:
                kwargs = eval(f'policies(name_prefix, org, inner_type).{inner_policy}(**kwargs)')
