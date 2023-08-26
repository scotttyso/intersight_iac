from classes import pools
from dotmap import DotMap
from copy import deepcopy
import ezfunctions
import os
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
        baseRepo       = kwargs.args.dir
        configure_loop = False
        ezData         = kwargs.ezData
        name_prefix    = self.name_prefix
        org            = self.org
        
        policy_type    = 'Ethernet Adapter'
        yaml_file      = 'ethernet'
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  {policy_type} Policy:  To simplify your work, this wizard will use {policy_type}')
            print(f'  Templates that are pre-configured.  You can add custom {policy_type} Policy')
            print(f'  configuration to the {yaml_file}.yaml file at your descretion.')
            print(f'  That will not be covered by this wizard as the focus of the wizard is on simplicity.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - {baseRepo}{os.sep}{org}{os.sep}{self.type}{os.sep}{yaml_file}.yaml')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure an {policy_type} Policy?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                policy_loop = False
                while policy_loop == False:
                    polVars = {}
                    #==============================================
                    # Get API Data
                    #==============================================
                    kwargs.multi_select = False
                    jsonVars = ezData.ezimm.allOf[1].properties.policies.vnic.EthNetworkPolicy
                    #==============================================
                    # Prompt User for Template Name
                    #==============================================
                    kwargs.jData = deepcopy(jsonVars.templates)
                    kwargs.jData.varType = 'Ethernet Adapter Template'
                    adapter_template = ezfunctions.variablesFromAPI(**kwargs)
                    #==============================================
                    # Prompt User for Name and Description
                    #==============================================
                    if not name_prefix == '': name = '%s-%s' % (name_prefix, adapter_template)
                    else: name = adapter_template
                    polVars.adapter_template = adapter_template
                    polVars.name             = ezfunctions.policy_name(name, policy_type)
                    polVars.description      = ezfunctions.policy_descr(polVars.name, policy_type)
                    #==============================================
                    # Print Policy and Prompt User to Accept
                    #==============================================
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(textwrap.indent(yaml.dump(polVars, Dumper=MyDumper, default_flow_style=False), ' '*4, predicate=None))
                    print(f'-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
                        if confirm_policy == 'Y' or confirm_policy == '':
                            #==============================================
                            # Add Policy Variables to immDict
                            #==============================================
                            kwargs.class_path = 'policies,ethernet_adapter'
                            kwargs = ezfunctions.ez_append(polVars, **kwargs)
                            #==============================================
                            # Create Additional Policy or Exit Loop
                            #==============================================
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
    # Ethernet Network Control Policy Module
    #==============================================
    def ethernet_network_control(self, **kwargs):
        baseRepo       = kwargs.args.dir
        configure_loop = False
        jsonData       = kwargs.jsonData
        name_prefix    = self.name_prefix
        name_suffix    = 'ntwk-ctrl'
        org            = self.org
        policy_type    = 'Ethernet Network Control Policy'
        yaml_file      = 'ethernet'
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  An {policy_type} will allow you to control Network Discovery with ')
            print(f'  protocols like CDP and LLDP as well as MAC Address Control Features.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - {baseRepo}{os.sep}{org}{os.sep}{self.type}{os.sep}{yaml_file}.yaml')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            policy_loop = False
            while policy_loop == False:
                polVars = {}
                #==============================================
                # Prompt User for Name and Description
                #==============================================
                if not name_prefix == '': name = f'{name_prefix}-{name_suffix}'
                else: name = f'{name_suffix}'
                polVars.name        = ezfunctions.policy_name(name, policy_type)
                polVars.description = ezfunctions.policy_descr(polVars.name, policy_type)
                polVars.action_on_uplink_fail = 'linkDown'
                #==============================================
                # Get API Data
                #==============================================
                kwargs.multi_select = False
                jsonVars = jsonData.fabric.LldpSettings.allOf[1].properties
                #==============================================
                # Prompt User for LLDP Protocol
                #==============================================
                kwargs.jData = deepcopy(jsonVars.ReceiveEnabled)
                kwargs.jData.varInput = f'Do you want to enable LLDP Recieve for this Policy?'
                kwargs.jData.varName  = 'LLDP Receive'
                answer = ezfunctions.varBoolLoop(**kwargs)
                if answer == True: polVars.lldp_receive_enable = True
                kwargs.jData = deepcopy(jsonVars.TransmitEnabled)
                kwargs.jData.varInput = f'Do you want to enable LLDP Transmit for this Policy?'
                kwargs.jData.varName  = 'LLDP Transmit'
                answer = ezfunctions.varBoolLoop(**kwargs)
                if answer == True: polVars.lldp_transmit_enable = True
                # Pull Information from API Documentation
                jsonVars = jsonData.fabric.EthNetworkControlPolicy.allOf[1].properties
                #==============================================
                # Prompt User for CDP Protocol
                #==============================================
                kwargs.jData = deepcopy(jsonVars.CdpEnabled)
                kwargs.jData.default  = True
                kwargs.jData.varInput = f'Do you want to enable CDP (Cisco Discovery Protocol) for this Policy?'
                kwargs.jData.varName  = 'CDP Enable'
                answer = ezfunctions.varBoolLoop(**kwargs)
                if answer == True: polVars.cdp_enable = True
                #==============================================
                # Prompt User for Mac Registration Mode
                #==============================================
                kwargs.jData = deepcopy(jsonVars.MacRegistrationMode)
                kwargs.jData.varType = 'MAC Registration Mode'
                polVars.mac_register_mode = ezfunctions.variablesFromAPI(**kwargs)
                #==============================================
                # Prompt User for MAC Security Forge
                #==============================================
                kwargs.jData = deepcopy(jsonVars.ForgeMac)
                kwargs.jData.varType = 'MAC Security Forge'
                polVars.mac_security_forge = ezfunctions.variablesFromAPI(**kwargs)
                #==============================================
                # Print Policy and Prompt User to Accept
                #==============================================
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(textwrap.indent(yaml.dump(polVars, Dumper=MyDumper, default_flow_style=False), ' '*4, predicate=None))
                print(f'-------------------------------------------------------------------------------------------\n')
                valid_confirm = False
                while valid_confirm == False:
                    confirm_policy = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                    if confirm_policy == 'Y' or confirm_policy == '':
                        #==============================================
                        # Add Policy Variables to immDict
                        #==============================================
                        kwargs.class_path = 'policies,ethernet_network_control'
                        kwargs = ezfunctions.ez_append(polVars, **kwargs)
                        #==============================================
                        # Create Additional Policy or Exit Loop
                        #==============================================
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
        baseRepo       = kwargs.args.dir
        configure_loop = False
        name_prefix    = self.name_prefix
        name_suffix    = ['dvs', 'mgmt', 'migration', 'storage']
        org            = self.org
        
        policy_type    = 'Ethernet Network Group Policy'
        yaml_file      = 'ethernet'
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  An {policy_type} will define the Allowed VLANs on a Server vNIC Template.')
            print(f'  As a recommendation you will need an {policy_type} per vNIC Grouping.')
            print(f'  For Instance with a Virtual Host that may have the following vNIC Pairs:')
            print(f'     1. dvs')
            print(f'     2. mgmt')
            print(f'     3. migration')
            print(f'     4. storage')
            print(f'  You will want to configure 1 {policy_type} per Group.')
            print(f'  The allowed vlan list can be in the format of:')
            print(f'     5 - Single VLAN')
            print(f'     1-10 - Range of VLANs')
            print(f'     1,2,3,4,5,11,12,13,14,15 - List of VLANs')
            print(f'     1-10,20-30 - Ranges and Lists of VLANs')
            print(f'  If you want to Assign a Native VLAN Make sure it is in the allowed list.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - {baseRepo}{os.sep}{org}{os.sep}{self.type}{os.sep}{yaml_file}.yaml')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            #==============================================
            # Prompt User for VLAN Policy Name
            #==============================================
            kwargs.name   = 'Ethernet Network Group'
            kwargs.policy = 'policies.vlan.vlan_policy'
            kwargs.allow_opt_out = False
            kwargs = policy_select_loop(self, **kwargs)
            loop_count = 0
            policy_loop = False
            while policy_loop == False:
                #==============================================
                # Prompt User for Name and Description
                #==============================================
                name = ''
                for i, v in enumerate(name_suffix):
                    if int(loop_count) == i:
                        if not name_prefix == '': name = '%s-%s' % (name_prefix, v)
                        else: name = v
                if name == '':  name = '%s-%s' % (org, 'vlg')
                polVars = {}
                polVars.name        = ezfunctions.policy_name(name, policy_type)
                polVars.description = ezfunctions.policy_descr(polVars.name, policy_type)
                #==============================================
                # Get VLAN Policy VLAN(s) and Compare
                #==============================================
                vlan_list = []
                for item in kwargs.immDict.orgs[org].policies.vlan:
                    if item.name == kwargs.vlan_policy:
                        for i in item.vlans:
                            vlan_list.append(i.vlan_list)
                all_vlans = ','.join(vlan_list)
                vlan_policy_list = ezfunctions.vlan_list_full(all_vlans)
                valid = False
                while valid == False:
                    VlanList = input('Enter the VLAN or List of VLANs to add to {}: '.format(polVars.name))
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
                            print('  - VLAN Policy: "{}"').format(kwargs.vlan_policy)
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
                #==============================================
                # Prompt User for Native VLAN
                #==============================================
                polVars.native_vlan = ezfunctions.vlan_native_function(vlan_policy_list, vlan_list)
                if polVars.native_vlan == '': polVars.pop('native_vlan')
                polVars.allowed_vlans = VlanList
                #==============================================
                # Print Policy and Prompt User to Accept
                #==============================================
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(textwrap.indent(yaml.dump(polVars, Dumper=MyDumper, default_flow_style=False), ' '*4, predicate=None))
                print(f'-------------------------------------------------------------------------------------------\n')
                valid_confirm = False
                while valid_confirm == False:
                    confirm_policy = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                    if confirm_policy == 'Y' or confirm_policy == '':
                        #==============================================
                        # Add Policy Variables to immDict
                        #==============================================
                        kwargs.class_path = 'policies,ethernet_network_group'
                        kwargs = ezfunctions.ez_append(polVars, **kwargs)
                        #==============================================
                        # Create Additional Policy or Exit Loop
                        #==============================================
                        if loop_count < 3: configure_loop, policy_loop = ezfunctions.exit_default(policy_type, 'Y')
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
        baseRepo       = kwargs.args.dir
        configure_loop = False
        jsonData       = kwargs.jsonData
        name_prefix    = self.name_prefix
        name_suffix    = 'network'
        org            = self.org
        policy_type    = 'Ethernet Network Policy'
        yaml_file      = 'ethernet'
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  An {policy_type} determines if the port can carry single VLAN (Access) ')
            print(f'  or multiple VLANs (Trunk) traffic. You can specify the VLAN to be associated with an ')
            print(f'  Ethernet packet if no tag is found.\n\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - {baseRepo}{os.sep}{org}{os.sep}{self.type}{os.sep}{yaml_file}.yaml')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure an {policy_type}?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                policy_loop = False
                while policy_loop == False:
                    polVars = {}
                    #==============================================
                    # Prompt User for Name and Description
                    #==============================================
                    if not name_prefix == '': name = f'{name_prefix}-{name_suffix}'
                    else: name = f'{name_suffix}'
                    polVars.name        = ezfunctions.policy_name(name, policy_type)
                    polVars.description = ezfunctions.policy_descr(polVars.name, policy_type)
                    #==============================================
                    # Get API Data
                    #==============================================
                    kwargs.multi_select = False
                    jsonVars = jsonData.vnic.VlanSettings.allOf[1].properties
                    #==============================================
                    # Prompt User for VLAN Mode
                    #==============================================
                    kwargs.jData = deepcopy(jsonVars.Mode)
                    kwargs.jData.varType = 'VLAN Mode'
                    polVars.vlan_mode = ezfunctions.variablesFromAPI(**kwargs)
                    #==============================================
                    # Prompt User for Default VLAN
                    #==============================================
                    valid = False
                    while valid == False:
                        default_vlan = input('What is the default vlan to assign to this Policy.  Range is 0 to 4094: ')
                        if re.fullmatch(r'[0-9]{1,4}', default_vlan):
                            polVars.default_vlan = default_vlan
                            valid = validating.number_in_range('VLAN ID', polVars.default_vlan, 0, 4094)
                    #==============================================
                    # Print Policy and Prompt User to Accept
                    #==============================================
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(textwrap.indent(yaml.dump(polVars, Dumper=MyDumper, default_flow_style=False), ' '*4, predicate=None))
                    print(f'-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
                        if confirm_policy == 'Y' or confirm_policy == '':
                            #==============================================
                            # Add Policy Variables to immDict
                            #==============================================
                            kwargs.class_path = 'policies,ethernet_network'
                            kwargs = ezfunctions.ez_append(polVars, **kwargs)
                            #==============================================
                            # Create Additional Policy or Exit Loop
                            #==============================================
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
        baseRepo        = kwargs.args.dir
        configure_loop  = False
        jsonData        = kwargs.jsonData
        name_prefix     = self.name_prefix
        name_suffix     = ['Bronze', 'Gold', 'Platinum', 'Silver']
        org             = self.org
        policy_type     = 'Ethernet QoS Policy'
        target_platform = kwargs.target_platform
        yaml_file       = 'ethernet'
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
            print(f'  - {baseRepo}{os.sep}{org}{os.sep}{self.type}{os.sep}{yaml_file}.yaml')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            #================================================
            # Prompt User for Sytem QoS Policy if FIAttached
            #================================================
            if target_platform == 'FIAttached':
                kwargs.name = 'Ethernet QoS'
                kwargs.allow_opt_out = False
                kwargs.policy = 'policies.system_qos.system_qos_policy'
                kwargs = policy_select_loop(self, **kwargs)
            loop_count = 0
            policy_loop = False
            while policy_loop == False:
                polVars = {}
                #==============================================
                # Prompt User for Name and Description
                #==============================================
                name = ''
                if target_platform == 'FIAttached':
                    for i, v in enumerate(name_suffix):
                        if int(loop_count) == i:
                            if not name_prefix == '': name = f'{name_prefix}-{v}'
                            else: name = v
                else: 
                    if not name_prefix == '': name = f'{name_prefix}-qos'
                if name == '': name = f'{org}-qos'
                polVars.name        = ezfunctions.policy_name(name, policy_type)
                polVars.description = ezfunctions.policy_descr(polVars.name, policy_type)
                #==============================================
                # Get API Data
                #==============================================
                kwargs.multi_select = False
                jsonVars = jsonData.vnic.EthQosPolicy.allOf[1].properties
                #==============================================
                # Prompt User for Trust Host CoS
                #==============================================
                kwargs.jData = deepcopy(jsonVars.TrustHostCos)
                kwargs.jData.varInput = f'Do you want to Enable Trust Host based CoS?'
                kwargs.jData.varName  = 'Trust Host CoS'
                polVars.enable_trust_host_cos = ezfunctions.varBoolLoop(**kwargs)
                #==============================================
                # Prompt User for Rate Limit
                #==============================================
                kwargs.jData = deepcopy(jsonVars.RateLimit)
                kwargs.jData.varInput = f'What is the Rate Limit you want to assign to the Policy?'
                kwargs.jData.varName  = 'Rate Limit'
                polVars.rate_limit = ezfunctions.varNumberLoop(**kwargs)

                if target_platform == 'Standalone':
                    #==============================================
                    # Prompt User for Class of Service
                    #==============================================
                    kwargs.jData = deepcopy(jsonVars.Cos)
                    kwargs.jData.varInput = f'What is the Class of Service you want to assign to the Policy?'
                    kwargs.jData.varName  = 'Class of Service'
                    polVars.cos = ezfunctions.varNumberLoop(**kwargs)
                    #==============================================
                    # Prompt User for MTU
                    #==============================================
                    kwargs.jData = deepcopy(jsonVars.Mtu)
                    kwargs.jData.varInput = f'What is the MTU you want to assign to the Policy?'
                    kwargs.jData.varName  = 'MTU'
                    polVars.mtu = ezfunctions.varNumberLoop(**kwargs)
                else:
                    #==============================================
                    # Prompt User for Burst
                    #==============================================
                    kwargs.jData = deepcopy(jsonVars.Burst)
                    kwargs.jData.varInput = f'What is the Burst you want to assign to the Policy?'
                    kwargs.jData.varName  = 'Burst'
                    polVars.burst = ezfunctions.varNumberLoop(**kwargs)
                    #==============================================
                    # Prompt User for Priority
                    #==============================================
                    kwargs.jData = deepcopy(jsonVars.Priority)
                    kwargs.jData.varType = f"{polVars.name} QoS Priority"
                    polVars.priority = ezfunctions.variablesFromAPI(**kwargs)
                    mtu = 1500
                    for i in kwargs.immDict.orgs[org].policies.system_qos:
                        if i.name == kwargs.system_qos_policy:
                            for k in i.classes:
                                if k.priority == polVars.priority:
                                    mtu = k.mtu
                    if mtu > 8999: polVars.mtu = 9000
                    else: polVars.mtu = mtu
                #==============================================
                # Print Policy and Prompt User to Accept
                #==============================================
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(textwrap.indent(yaml.dump(polVars, Dumper=MyDumper, default_flow_style=False), ' '*4, predicate=None))
                print(f'\n-------------------------------------------------------------------------------------------\n')
                valid_confirm = False
                while valid_confirm == False:
                    confirm_policy = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
                    if confirm_policy == 'Y' or confirm_policy == '':
                        #==============================================
                        # Add Policy Variables to immDict
                        #==============================================
                        kwargs.class_path = 'policies,ethernet_qos'
                        kwargs = ezfunctions.ez_append(polVars, **kwargs)
                        #==============================================
                        # Create Additional Policy or Exit Loop
                        #==============================================
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
    # Fibre-Channel Network Policy Module
    #==============================================
    def fc_zone(self, **kwargs):
        baseRepo       = kwargs.args.dir
        configure_loop = False
        jsonData       = kwargs.jsonData
        name_prefix    = self.name_prefix
        org            = self.org
        policy_type    = 'FC Zone Policy'
        yaml_file      = 'fibre_channel'
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  You can Skip this policy if you are not configuring Fibre-Channel.\n')
            print(f'  FC Zone Policy Notes:')
            print(f'  - You will need at a Minimum One Zone Policy per Fabric.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - {baseRepo}{os.sep}{org}{os.sep}{self.type}{os.sep}{yaml_file}.yaml')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure a {policy_type}?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                loop_count = 0
                policy_loop = False
                while policy_loop == False:
                    polVars = {}
                    #==============================================
                    # Prompt User for Name and Description
                    #==============================================
                    if name_prefix == '': name_prefix = 'vsan'
                    name = ezfunctions.naming_rule_fabric(loop_count, name_prefix, org)
                    polVars.name        = ezfunctions.policy_name(name, policy_type)
                    kwargs.name         = polVars.name
                    polVars.description = ezfunctions.policy_descr(polVars.name, policy_type)

                    #==============================================
                    # Get API Data
                    #==============================================
                    kwargs.multi_select = False
                    jsonVars = jsonData.fabric.FcZonePolicy.allOf[1].properties
                    #==============================================
                    # Prompt User for FC Target Zoning Type
                    #==============================================
                    kwargs.jData = deepcopy(jsonVars.FcTargetZoningType)
                    kwargs.jData.default  = 'SIMT'
                    kwargs.jData.varType  = 'FC Target Zoning Type'
                    polVars.fc_target_zoning_type = ezfunctions.variablesFromAPI(**kwargs)

                    #==============================================
                    # Prompt User for Target(s) for the Policy
                    #==============================================
                    polVars.targets = []
                    inner_loop_count = 0
                    sub_loop = False
                    while sub_loop == False:
                        tg = {}
                        jsonVars = jsonData.fabric.FcZoneMember.allOf[1].properties
                        #==============================================
                        # Prompt User for FC Zone Target Name
                        #==============================================
                        kwargs.jData = deepcopy(jsonVars.Name)
                        kwargs.jData.pattern = '^[\\S]{1,64}$'
                        kwargs.jData.varInput = f'What is the FC Zone Target Name?'
                        kwargs.jData.varName = 'FC Zone Target Name'
                        tg.name = ezfunctions.varStringLoop(**kwargs)
                        name = tg.name
                        #==============================================
                        # Prompt User for Target WWPN
                        #==============================================
                        kwargs.jData = deepcopy(jsonVars.Wwpn)
                        kwargs.jData.varInput = f'What is the Target WWPN?'
                        kwargs.jData.varName = 'Target WWPN'
                        tg.wwpn = ezfunctions.varStringLoop(**kwargs)
                        #==============================================
                        # Prompt User for Target Switch Id
                        #==============================================
                        kwargs.jData = deepcopy(jsonVars.SwitchId)
                        kwargs.jData.varType = 'Target Switch ID'
                        tg.switch_id = ezfunctions.variablesFromAPI(**kwargs)
                        valid = False
                        while valid == False:
                            #==============================================
                            # Prompt User for Target VSAN
                            #==============================================
                            kwargs.jData = deepcopy(jsonVars.VsanId)
                            if loop_count % 2 == 0:  kwargs.jData.default = 100
                            else:  kwargs.jData.default = 200
                            kwargs.jData.varInput = f'What is the Target VSAN Id?'
                            kwargs.jData.varName = 'VSAN ID'
                            vsan_id = ezfunctions.varNumberLoop(**kwargs)
                            #==============================================
                            # Prompt User for Fabric VSAN Policy
                            #==============================================
                            kwargs.allow_opt_out = False
                            kwargs.policy = 'policies.vsan.vsan_policy'
                            kwargs = policy_select_loop(self, **kwargs)
                            vsan_list = []
                            for item in kwargs.immDict.orgs[org].policies.vsan:
                                if item.name == kwargs.vsan_policy:
                                    for i in item.vsans: vsan_list.append(i.vsan_id)
                            if len(vsan_list) > 1: vsan_string = ','.join(str(vsan_list))
                            else: vsan_string = vsan_list[0]
                            vsan_list = ezfunctions.vlan_list_full(vsan_string)
                            vcount = 0
                            for vsan in vsan_list:
                                if int(vsan_id) == int(vsan):
                                    vcount = 1
                                    break
                            if vcount == 0: ezfunctions.message_invalid_vsan_id(kwargs.vsan_policy, vsan_id, vsan_list)
                            else: valid = True
                        tg.vsan_id = vsan_id
                        #==============================================
                        # Print Policy and Prompt User to Accept
                        #==============================================
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        print(textwrap.indent(yaml.dump(tg, Dumper=MyDumper, default_flow_style=False), ' '*4, predicate=None))
                        print(f'-------------------------------------------------------------------------------------------\n')
                        valid_confirm = False
                        while valid_confirm == False:
                            pol_type = 'FC Zone Targets'
                            confirm_vsan = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                            if confirm_vsan == 'Y' or confirm_vsan == '':
                                polVars.targets.append(tg)
                                #==============================================
                                # Create Additional Policy or Exit Loop
                                #==============================================
                                valid_exit = False
                                while valid_exit == False:
                                    valid_exit, sub_loop = ezfunctions.exit_default(pol_type, 'Y')
                                    if valid_exit == True: inner_loop_count += 1; valid_confirm = True; valid_exit = True
                                    else: valid_confirm = True; valid_exit = True
                            elif confirm_vsan == 'N':
                                ezfunctions.message_starting_over(pol_type)
                                valid_confirm = True
                            else: ezfunctions.message_invalid_y_or_n('short')
                    #==============================================
                    # Print Policy and Prompt User to Accept
                    #==============================================
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(textwrap.indent(yaml.dump(polVars, Dumper=MyDumper, default_flow_style=False), ' '*4, predicate=None))
                    print(f'-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                        if confirm_policy == 'Y' or confirm_policy == '':
                            #==============================================
                            # Add Policy Variables to immDict
                            #==============================================
                            kwargs.class_path = 'policies,fc_zone'
                            kwargs = ezfunctions.ez_append(polVars, **kwargs)
                            #==============================================
                            # Create Additional Policy or Exit Loop
                            #==============================================
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
    # Fibre-Channel Adapter Policy Module
    #==============================================
    def fibre_channel_adapter(self, **kwargs):
        baseRepo       = kwargs.args.dir
        configure_loop = False
        ezData         = kwargs.ezData
        name_prefix    = self.name_prefix
        org            = self.org
        
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
            print(f'  - {baseRepo}{os.sep}{org}{os.sep}{self.type}{os.sep}{yaml_file}.yaml')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure a {policy_type}?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                policy_loop = False
                while policy_loop == False:
                    polVars = {}
                    #==============================================
                    # Get API Data
                    #==============================================
                    kwargs.multi_select = False
                    jsonVars = ezData.ezimm.allOf[1].properties.policies.vnic.FcNetworkPolicy
                    #==============================================
                    # Prompt User for Template Name
                    #==============================================
                    kwargs.jData = deepcopy(jsonVars.templates)
                    kwargs.jData.varType = 'Fibre-Channel Adapter Template'
                    adapter_template = ezfunctions.variablesFromAPI(**kwargs)
                    #==============================================
                    # Prompt User for Name and Description
                    #==============================================
                    if not name_prefix == '': name = '%s-%s' % (name_prefix, adapter_template)
                    else: name = adapter_template
                    polVars.adapter_template = adapter_template
                    polVars.name             = ezfunctions.policy_name(name, adapter_template)
                    polVars.description      = ezfunctions.policy_descr(polVars.name, policy_type)
                    #==============================================
                    # Print Policy and Prompt User to Accept
                    #==============================================
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(textwrap.indent(yaml.dump(polVars, Dumper=MyDumper, default_flow_style=False), ' '*4, predicate=None))
                    print(f'-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
                        if confirm_policy == 'Y' or confirm_policy == '':
                            #==============================================
                            # Add Policy Variables to immDict
                            #==============================================
                            kwargs.class_path = 'policies,fibre_channel_adapter'
                            kwargs = ezfunctions.ez_append(polVars, **kwargs)
                            #==============================================
                            # Create Additional Policy or Exit Loop
                            #==============================================
                            configure_loop, policy_loop = ezfunctions.exit_default(policy_type, 'N')
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
        baseRepo        = kwargs.args.dir
        configure_loop  = False
        jsonData        = kwargs.jsonData
        name_prefix     = self.name_prefix
        org             = self.org
        policy_type     = 'Fibre-Channel Network Policy'
        target_platform = kwargs.target_platform
        yaml_file       = 'fibre_channel'
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  You can Skip this policy if you are not configuring Fibre-Channel.\n')
            print(f'  Fibre-Channel Network Policies Notes:')
            print(f'  - You will need one Policy per Fabric.  VSAN A and VSAN B.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - {baseRepo}{os.sep}{org}{os.sep}{self.type}{os.sep}{yaml_file}.yaml')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure a {policy_type}?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                loop_count = 0
                policy_loop = False
                while policy_loop == False:
                    polVars = {}
                    #==============================================
                    # Prompt User for Name and Description
                    #==============================================
                    if name_prefix == '': name_prefix = 'vsan'
                    name = ezfunctions.naming_rule_fabric(loop_count, name_prefix, org)
                    polVars.name        = ezfunctions.policy_name(name, policy_type)
                    kwargs.name         = polVars.name
                    polVars.description = ezfunctions.policy_descr(polVars.name, policy_type)

                    jsonVars = jsonData.vnic.VsanSettings.allOf[1].properties
                    if target_platform == 'Standalone':
                        #==============================================
                        # Prompt User for Default VLAN Id
                        #==============================================
                        kwargs.jData = deepcopy(jsonVars.DefaultVlanId)
                        kwargs.jData.minimum = 1
                        kwargs.jData.varInput = 'What is the Default VLAN you want to Assign to this Policy?'
                        kwargs.jData.varName  = 'Default VLAN'
                        polVars.default_vlan = ezfunctions.varNumberLoop(**kwargs)

                    valid = False
                    while valid == False:
                        #==============================================
                        # Prompt User for VSAN Id
                        #==============================================
                        kwargs.jData = deepcopy(jsonVars.Id)
                        if loop_count % 2 == 0: kwargs.jData.default = 100
                        else: kwargs.jData.default = 200
                        kwargs.jData.varInput = 'What VSAN Do you want to Assign to this Policy?'
                        kwargs.jData.varName  = 'VSAN'
                        vsan_id = ezfunctions.varNumberLoop(**kwargs)
                        #==============================================
                        # Prompt User for VSAN Policy
                        #==============================================
                        if target_platform == 'FIAttached':
                            kwargs.allow_opt_out = False
                            kwargs.policy = 'policies.vsan.vsan_policy'
                            kwargs = policy_select_loop(self, **kwargs)
                            vsan_list = []
                            for item in kwargs.immDict.orgs[org].policies.vsan:
                                if item.name == kwargs.vsan_policy:
                                    for i in item.vsans: vsan_list.append(i.vsan_id)
                            print(f'vsan list is {vsan_list}')
                            if len(vsan_list) > 1: vsan_string = ','.join(str(vsan_list))
                            else: vsan_string = vsan_list[0]
                            vsan_list = ezfunctions.vlan_list_full(vsan_string)
                            vcount = 0
                            for vsan in vsan_list:
                                if int(vsan_id) == int(vsan):
                                    vcount = 1
                                    break
                            if vcount == 0: ezfunctions.message_invalid_vsan_id(kwargs.vsan_policy, vsan_id, vsan_list)
                            else: valid = True
                    polVars.vsan_id = vsan_id
                    #==============================================
                    # Print Policy and Prompt User to Accept
                    #==============================================
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(textwrap.indent(yaml.dump(polVars, Dumper=MyDumper, default_flow_style=False), ' '*4, predicate=None))
                    print(f'-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                        if confirm_policy == 'Y' or confirm_policy == '':
                            #==============================================
                            # Add Policy Variables to immDict
                            #==============================================
                            kwargs.class_path = 'policies,fibre_channel_network'
                            kwargs = ezfunctions.ez_append(polVars, **kwargs)
                            #==============================================
                            # Create Additional Policy or Exit Loop
                            #==============================================
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
        baseRepo       = kwargs.args.dir
        configure_loop = False
        name_prefix    = self.name_prefix
        name_suffix    = 'fc-qos'
        org            = self.org
        
        policy_type    = 'Fibre-Channel QoS Policy'
        yaml_file      = 'fibre_channel'
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  You can Skip this policy if you are not configuring Fibre-Channel.\n')
            print(f'  It is a good practice to apply a {policy_type} to the vHBAs.  This wizard')
            print(f'  creates the policy with all the default values, so you only need one')
            print(f'  {policy_type}.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - {baseRepo}{os.sep}{org}{os.sep}{self.type}{os.sep}{yaml_file}.yaml')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure a {policy_type}?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                policy_loop = False
                while policy_loop == False:
                    polVars = {}
                    #==============================================
                    # Prompt User for Name and Description
                    #==============================================
                    if not name_prefix == '': name = f'{name_prefix}-{name_suffix}'
                    else: name = f'{name_suffix}'
                    polVars.name        = ezfunctions.policy_name(name, policy_type)
                    polVars.description = ezfunctions.policy_descr(polVars.name, policy_type)
                    #==============================================
                    # Print Policy and Prompt User to Accept
                    #==============================================
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(textwrap.indent(yaml.dump(polVars, Dumper=MyDumper, default_flow_style=False), ' '*4, predicate=None))
                    print(f'-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                        if confirm_policy == 'Y' or confirm_policy == '':
                            #==============================================
                            # Add Policy Variables to immDict
                            #==============================================
                            kwargs.class_path = 'policies,fibre_channel_qos'
                            kwargs = ezfunctions.ez_append(polVars, **kwargs)
                            #==============================================
                            # Create Additional Policy or Exit Loop
                            #==============================================
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
        baseRepo       = kwargs.args.dir
        configure_loop = False
        name_prefix    = self.name_prefix
        name_suffix    = 'flow-ctrl'
        org            = self.org
        
        policy_type    = 'Flow Control Policy'
        yaml_file      = 'ethernet'
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  The Flow Control Policy will enable Priority Flow Control on the Fabric Interconnects.')
            print(f'  We recommend the default parameters so you will only be asked for the name and')
            print(f'  description for the Policy.  You only need one of these policies for Organization')
            print(f'  {org}.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - {baseRepo}{os.sep}{org}{os.sep}{self.type}{os.sep}{yaml_file}.yaml')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            policy_loop = False
            while policy_loop == False:
                polVars = {}
                #==============================================
                # Prompt User for Name and Description
                #==============================================
                if not name_prefix == '': name = f'{name_prefix}-{name_suffix}'
                else: name = f'{name_suffix}'
                polVars.name        = ezfunctions.policy_name(name, policy_type)
                polVars.description = ezfunctions.policy_descr(polVars.name, policy_type)
                #==============================================
                # Print Policy and Prompt User to Accept
                #==============================================
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(textwrap.indent(yaml.dump(polVars, Dumper=MyDumper, default_flow_style=False), ' '*4, predicate=None))
                print(f'-------------------------------------------------------------------------------------------\n')
                valid_confirm = False
                while valid_confirm == False:
                    confirm_policy = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                    if confirm_policy == 'Y' or confirm_policy == '':
                        #==============================================
                        # Add Policy Variables to immDict
                        #==============================================
                        kwargs.class_path = 'policies,flow_control'
                        kwargs = ezfunctions.ez_append(polVars, **kwargs)
                        #==============================================
                        # Create Additional Policy or Exit Loop
                        #==============================================
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
        baseRepo       = kwargs.args.dir
        configure_loop = False
        jsonData       = kwargs.jsonData
        name_prefix    = self.name_prefix
        name_suffix    = 'adapter'
        org            = self.org
        policy_type    = 'iSCSI Adapter Policy'
        yaml_file      = 'ethernet'
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  The {policy_type} allows you to configure values for TCP Connection Timeout, ')
            print(f'  DHCP Timeout, and the Retry Count if the specified LUN ID is busy.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - {baseRepo}{os.sep}{org}{os.sep}{self.type}{os.sep}{yaml_file}.yaml')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure a {policy_type}?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                policy_loop = False
                while policy_loop == False:
                    polVars = {}
                    #==============================================
                    # Prompt User for Name and Description
                    #==============================================
                    if not name_prefix == '': name = f'{name_prefix}-{name_suffix}'
                    else: name = f'{name_suffix}'
                    polVars.name        = ezfunctions.policy_name(name, policy_type)
                    polVars.description = ezfunctions.policy_descr(polVars.name, policy_type)
                    #==============================================
                    # Get API Data
                    #==============================================
                    kwargs.multi_select = False
                    jsonVars = jsonData.vnic.IscsiAdapterPolicy.allOf[1].properties
                    #==============================================
                    # Prompt User for DHCP Timeout
                    #==============================================
                    kwargs.jData = deepcopy(jsonVars.DhcpTimeout)
                    kwargs.jData.default  = 60
                    kwargs.jData.varInput = f'Enter the number of seconds after which the DHCP times out.'
                    kwargs.jData.varName  = 'DHCP Timeout'
                    polVars.dhcp_timeout = ezfunctions.varNumberLoop(**kwargs)
                    #==============================================
                    # Prompt User for LUN Busy Retry Count
                    #==============================================
                    kwargs.jData = deepcopy(jsonVars.LunBusyRetryCount)
                    kwargs.jData.default  = 15
                    kwargs.jData.varInput = f'Enter the number of times connection is to be attempted when the LUN ID is busy.'
                    kwargs.jData.varName  = 'LUN Busy Retry Count'
                    polVars.lun_busy_retry_count = ezfunctions.varNumberLoop(**kwargs)
                    #==============================================
                    # Prompt User for TCP Connection Timeout
                    #==============================================
                    kwargs.jData = deepcopy(jsonVars.ConnectionTimeOut)
                    kwargs.jData.default  = 15
                    kwargs.jData.varInput = f'Enter the number of seconds after which the TCP connection times out.'
                    kwargs.jData.varName  = 'TCP Connection Timeout'
                    polVars.tcp_connection_timeout = ezfunctions.varNumberLoop(**kwargs)
                    #==============================================
                    # Print Policy and Prompt User to Accept
                    #==============================================
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(textwrap.indent(yaml.dump(polVars, Dumper=MyDumper, default_flow_style=False), ' '*4, predicate=None))
                    print(f'-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                        if confirm_policy == 'Y' or confirm_policy == '':
                            #==============================================
                            # Add Policy Variables to immDict
                            #==============================================
                            confirm_policy = 'Y'
                            kwargs.class_path = 'policies,iscsi_adapter'
                            kwargs = ezfunctions.ez_append(polVars, **kwargs)
                            #==============================================
                            # Create Additional Policy or Exit Loop
                            #==============================================
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
        baseRepo       = kwargs.args.dir
        configure_loop = False
        jsonData       = kwargs.jsonData
        name_prefix    = self.name_prefix
        name_suffix    = 'boot'
        org            = self.org
        policy_type    = 'iSCSI Boot Policy'
        yaml_file      = 'ethernet'
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  The {policy_type} allows you to initialize the Operating System on FI-attached ')
            print(f'  blade and rack servers from a remote disk across a Storage Area Network. The remote disk, ')
            print(f'  known as the target, is accessed using TCP/IP and iSCSI boot firmware.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - {baseRepo}{os.sep}{org}{os.sep}{self.type}{os.sep}{yaml_file}.yaml')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure a {policy_type}?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                policy_loop = False
                while policy_loop == False:
                    polVars = {}
                    #==============================================
                    # Prompt User for Name and Description
                    #==============================================
                    if not name_prefix == '': name = f'{name_prefix}-{name_suffix}'
                    else: name = f'{name_suffix}'
                    polVars.name        = ezfunctions.policy_name(name, policy_type)
                    kwargs.name         = polVars.name
                    polVars.description = ezfunctions.policy_descr(polVars.name, policy_type)
                    #==============================================
                    # Get API Data
                    #==============================================
                    kwargs.multi_select = False
                    jsonVars = jsonData.vnic.IscsiBootPolicy.allOf[1].properties
                    #==============================================
                    # Prompt User for Target Source Type
                    #==============================================
                    # Target Source Type
                    kwargs.jData = deepcopy(jsonVars.TargetSourceType)
                    kwargs.jData.varType = 'Target Source Type'
                    polVars.target_source_type = ezfunctions.variablesFromAPI(**kwargs)
                    if polVars.target_source_type == 'Auto':
                        #==============================================
                        # Prompt User for DHCP Vendor ID or IQN
                        #==============================================
                        polVars.authentication = 'none'
                        polVars.initiator_ip_source = 'DHCP'
                        kwargs.jData = deepcopy(jsonVars.AutoTargetvendorName)
                        kwargs.jData.default  = ''
                        kwargs.jData.minimum = 1
                        kwargs.jData.maximum = 32
                        kwargs.jData.pattern = '^[\\S]+$'
                        kwargs.jData.varInput = 'DHCP Vendor ID or IQN:'
                        kwargs.jData.varName  = 'DHCP Vendor ID or IQN'
                        polVars.dhcp_vendor_id_iqn = ezfunctions.varStringLoop(**kwargs)
                    elif polVars.target_source_type == 'Static':
                        #==============================================
                        # Prompt User for Primary Static Target
                        #==============================================
                        kwargs.optional_message = '  !!! Select the Primary Static Target !!!\n'
                        kwargs.allow_opt_out = False
                        kwargs.policy = 'policies.iscsi_static_target.iscsi_static_target_policy'
                        kwargs = policy_select_loop(self, **kwargs)
                        polVars.primary_target_policy = kwargs.iscsi_static_target_policy
                        #==============================================
                        # Prompt User for Secondary Static Target
                        #==============================================
                        kwargs.optional_message = ''\
                            '  !!! Optionally Select the Secondary Static Target or enter 99 for no Secondary !!!\n'
                        kwargs.allow_opt_out = True
                        kwargs.policy = 'policies.iscsi_static_target.iscsi_static_target_policy'
                        kwargs = policy_select_loop(self, **kwargs)
                        polVars.secondary_target_policy = kwargs.iscsi_static_target_policy
                        kwargs.pop('optional_message')
                        #==============================================
                        # Prompt User for Initiator IP Source
                        #==============================================
                        kwargs.jData = deepcopy(jsonVars.InitiatorIpSource)
                        kwargs.jData.varType = 'Initiator IP Source'
                        polVars.initiator_ip_source = ezfunctions.variablesFromAPI(**kwargs)

                        if polVars.initiator_ip_source == 'Pool':
                            #==============================================
                            # Prompt User for IP Pool
                            #==============================================
                            kwargs.optional_message = '  !!! Initiator IP Pool !!!\n'
                            kwargs.allow_opt_out = False
                            kwargs.policy = 'pools.ip.ip_pool'
                            kwargs = policy_select_loop(self, **kwargs)
                            kwargs.pop('optional_message')
                            polVars.ip_pool = kwargs.ip_pool

                        elif polVars.initiator_ip_source == 'Static':
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            print(jsonVars.InitiatorStaticIpV4Config.description)
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            #==============================================
                            # Prompt User for IP Address
                            #==============================================
                            polVars.initiator_static_ip_v4_config = {}
                            jsonVars = jsonData.vnic.IscsiStaticTargetPolicyInventory.allOf[1].properties
                            kwargs.jData = deepcopy(jsonVars.IpAddress)
                            kwargs.jData.varInput = f'IP Address:'
                            kwargs.jData.varName  = f'IP Address'
                            polVars.initiator_static_ip_v4_config.ip_address = ezfunctions.varStringLoop(**kwargs)
                            #==============================================
                            # Prompt User for Subnet Mask
                            #==============================================
                            jsonVars = jsonData.ippool.IpV4Config.allOf[1].properties
                            kwargs.jData = deepcopy(jsonVars.Netmask)
                            kwargs.jData.varInput = f'Subnet Mask:'
                            kwargs.jData.varName  = f'Subnet Mask'
                            polVars.initiator_static_ip_v4_config.subnet_mask = ezfunctions.varStringLoop(**kwargs)
                            #==============================================
                            # Prompt User for Default Gateway
                            #==============================================
                            kwargs.jData = deepcopy(jsonVars.Gateway)
                            kwargs.jData.varInput = f'Default Gateway:'
                            kwargs.jData.varName  = f'Default Gateway'
                            polVars.initiator_static_ip_v4_config.default_gateway = ezfunctions.varStringLoop(**kwargs)
                            #==============================================
                            # Prompt User for Primary DNS Server
                            #==============================================
                            kwargs.jData = deepcopy(jsonVars.SecondaryDns)
                            kwargs.jData.varInput = f'Primary DNS Server.  [press enter to skip]:'
                            kwargs.jData.varName  = f'Primary DNS Server'
                            polVars.initiator_static_ip_v4_config.primary_dns = ezfunctions.varStringLoop(**kwargs)
                            if polVars.initiator_static_ip_v4_config.primary_dns == '':
                                polVars.initiator_static_ip_v4_config.pop('primary_dns')
                            #==============================================
                            # Prompt User for Secondary DNS Server
                            #==============================================
                            kwargs.jData = deepcopy(jsonVars.SecondaryDns)
                            kwargs.jData.varInput = f'Secondary DNS Server.  [press enter to skip]:'
                            kwargs.jData.varName  = f'Secondary DNS Server'
                            polVars.initiator_static_ip_v4_config.secondary_dns = ezfunctions.varStringLoop(**kwargs)
                            if polVars.initiator_static_ip_v4_config.secondary_dns == '':
                                polVars.initiator_static_ip_v4_config.pop('secondary_dns')
                        #==============================================
                        # Prompt User for Type of Authentication
                        #==============================================
                        kwargs.jData = deepcopy({})
                        kwargs.jData.description = 'Select Which Type of Authentication you want to Perform.'
                        kwargs.jData.enum = ['chap', 'mutual_chap', 'none']
                        kwargs.jData.default = 'none'
                        kwargs.jData.varType = 'Authentication Type'
                        polVars.authentication = ezfunctions.variablesFromAPI(**kwargs)
                        if polVars.authentication == 'none': polVars.pop('authentication')

                        if re.search('chap', polVars.authentication):
                            jsonVars = jsonData.vnic.IscsiAuthProfile.allOf[1].properties
                            auth_type = str.title(polVars.authentication.replace('_', ' '))
                            #==============================================
                            # Prompt User for Username
                            #==============================================
                            kwargs.jData = deepcopy(jsonVars.UserId)
                            kwargs.jData.varInput = f'{auth_type} Username:'
                            kwargs.jData.varName  = f'{auth_type} Username'
                            polVars.username = ezfunctions.varStringLoop(**kwargs)
                            #==============================================
                            # Prompt User for Password
                            #==============================================
                            kwargs.Variable = 'iscsi_boot_password'
                            kwargs.iscsi_boot_password = ezfunctions.sensitive_var_value(**kwargs)
                    #==============================================
                    # Prompt User for iSCSI Adapter Policy
                    #==============================================
                    kwargs.allow_opt_out = True
                    kwargs.policy = 'policies.iscsi_adapter.iscsi_adapter_policy'
                    kwargs = policy_select_loop(self, **kwargs)
                    polVars.iscsi_adapter_policy = kwargs.iscsi_adapter_policy
                    #==============================================
                    # Print Policy and Prompt User to Accept
                    #==============================================
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(textwrap.indent(yaml.dump(polVars, Dumper=MyDumper, default_flow_style=False), ' '*4, predicate=None))
                    print(f'-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                        if confirm_policy == 'Y' or confirm_policy == '':
                            #==============================================
                            # Add Policy Variables to immDict
                            #==============================================
                            kwargs.class_path = 'policies,iscsi_boot'
                            kwargs = ezfunctions.ez_append(polVars, **kwargs)
                            #==============================================
                            # Create Additional Policy or Exit Loop
                            #==============================================
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
        baseRepo       = kwargs.args.dir
        configure_loop = False
        jsonData       = kwargs.jsonData
        name_prefix    = self.name_prefix
        name_suffix    = 'target'
        org            = self.org
        policy_type    = 'iSCSI Static Target Policy'
        yaml_file      = 'ethernet'
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  The {policy_type} allows you to specify the name, IP address, port, and ')
            print(f'  logical unit number of the primary target for iSCSI boot. You can optionally specify these ')
            print(f'  details for a secondary target as well.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - {baseRepo}{os.sep}{org}{os.sep}{self.type}{os.sep}{yaml_file}.yaml')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure a {policy_type}?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                policy_loop = False
                while policy_loop == False:
                    polVars = {}
                    #==============================================
                    # Prompt User for Name and Description
                    #==============================================
                    if not name_prefix == '': name = f'{name_prefix}-{name_suffix}'
                    else: name = f'{name_suffix}'
                    polVars.name        = ezfunctions.policy_name(name, policy_type)
                    polVars.description = ezfunctions.policy_descr(polVars.name, policy_type)
                    #==============================================
                    # Get API Data
                    #==============================================
                    jsonVars = jsonData.vnic.IscsiStaticTargetPolicy.allOf[1].properties
                    desc_add = '\n  such as:\n  * iqn.1984-12.com.cisco:lnx1\n  * iqn.1984-12.com.cisco:win-server1'
                    #==============================================
                    # Prompt User for Target Name
                    #==============================================
                    kwargs.jData = deepcopy(jsonVars.TargetName)
                    kwargs.jData.description = kwargs.jData.description + desc_add
                    kwargs.jData.varInput = 'Enter the name of the target:'
                    kwargs.jData.varName  = 'Target Name'
                    polVars.target_name = ezfunctions.varStringLoop(**kwargs)
                    #==============================================
                    # Prompt User for IP Address
                    #==============================================
                    kwargs.jData = deepcopy(jsonVars.IpAddress)
                    kwargs.jData.varInput = f'IP Address:'
                    kwargs.jData.varName  = f'IP Address'
                    polVars.ip_address = ezfunctions.varStringLoop(**kwargs)
                    #==============================================
                    # Prompt User for Port
                    #==============================================
                    kwargs.jData = deepcopy(jsonVars.Port)
                    kwargs.jData.default  = 3260
                    kwargs.jData.varInput = 'Enter the port number of the target.'
                    kwargs.jData.varName  = 'Port'
                    polVars.port = ezfunctions.varNumberLoop(**kwargs)
                    #==============================================
                    # Prompt User for LUN Identifier
                    #==============================================
                    jsonVars = jsonData.vnic.Lun.allOf[1].properties
                    kwargs.jData = deepcopy(jsonVars.LunId)
                    kwargs.jData.default  = 0
                    kwargs.jData.maximum = 1024
                    kwargs.jData.minimum = 0
                    kwargs.jData.varInput = 'Enter the ID of the boot logical unit number.'
                    kwargs.jData.varName  = 'LUN Identifier'
                    LunId = ezfunctions.varNumberLoop(**kwargs)
                    #==============================================
                    # Prompt User for LUN Bootable
                    #==============================================
                    kwargs.jData = deepcopy(jsonVars.Bootable)
                    kwargs.jData.default     = True
                    kwargs.jData.varInput    = f'Should LUN {LunId} be bootable?'
                    kwargs.jData.varName     = 'LUN Identifier'
                    Bootable = ezfunctions.varBoolLoop(**kwargs)
                    polVars.lun = {'bootable':Bootable,'lun_id':LunId}
                    #==============================================
                    # Print Policy and Prompt User to Accept
                    #==============================================
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(textwrap.indent(yaml.dump(polVars, Dumper=MyDumper, default_flow_style=False), ' '*4, predicate=None))
                    print(f'-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                        if confirm_policy == 'Y' or confirm_policy == '':
                            #==============================================
                            # Add Policy Variables to immDict
                            #==============================================
                            kwargs.class_path = 'policies,iscsi_static_target'
                            kwargs = ezfunctions.ez_append(polVars, **kwargs)
                            #==============================================
                            # Create Additional Policy or Exit Loop
                            #==============================================
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
    # LAN Connectivity Policy Module
    #==============================================
    def lan_connectivity(self, **kwargs):
        baseRepo        = kwargs.args.dir
        configure_loop  = False
        jsonData        = kwargs.jsonData
        name_prefix     = self.name_prefix
        name_suffix     = ['mgmt', 'migration', 'storage', 'dvs']
        org             = self.org
        policy_type     = 'LAN Connectivity Policy'
        target_platform = kwargs.target_platform
        yaml_file       = 'lan_connectivity'
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
            print(f'  - {baseRepo}{os.sep}{org}{os.sep}{self.type}{os.sep}{yaml_file}.yaml')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure a {policy_type}?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                policy_loop = False
                while policy_loop == False:
                    #==============================================
                    # Prompt User for Name and Description
                    #==============================================
                    polVars = {}
                    if not name_prefix == '': name = f'{name_prefix}-lcp'
                    else: name = 'lcp'
                    polVars.name        = ezfunctions.policy_name(name, policy_type)
                    kwargs.name         = polVars.name
                    polVars.description = ezfunctions.policy_descr(polVars.name, policy_type)
                    #==============================================
                    # Get API Data
                    #==============================================
                    kwargs.multi_select = False
                    jsonVars = jsonData.vnic.LanConnectivityPolicy.allOf[1].properties
                    if target_platform == 'FIAttached':
                        #==============================================
                        # Prompt User for Azure Stack Host QoS
                        #==============================================
                        kwargs.jData = deepcopy(jsonVars.AzureQosEnabled)
                        kwargs.jData.varInput = f'Do you want to Enable AzureStack-Host QoS?'
                        kwargs.jData.varName  = 'AzureStack-Host QoS'
                        polVars.enable_azure_stack_host_qos = ezfunctions.varBoolLoop(**kwargs)
                        #==============================================
                        # Prompt User for IQN Allocation Type
                        #==============================================
                        kwargs.jData = deepcopy(jsonVars.IqnAllocationType)
                        kwargs.jData.varType = 'Iqn Allocation Type'
                        polVars.iqn_allocation_type = ezfunctions.variablesFromAPI(**kwargs)
                        #================================================
                        # Prompt User for IQN Pool if Allocation is Pool
                        #================================================
                        if polVars.iqn_allocation_type == 'Pool':
                            polVars.iqn_static_identifier = ''
                            kwargs.allow_opt_out = False
                            kwargs.policy = 'pools.iqn.iqn_pool'
                            kwargs = policy_select_loop(self, **kwargs)
                            polVars.iqn_pool = kwargs.iqn_pool
                        elif polVars.iqn_allocation_type == 'Static':
                            #================================================
                            # Prompt User for IQN Static Address
                            #================================================
                            kwargs.iqn_pool = ''
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
                                    kwargs.iqn_static_identifier = f'iqn.1984-12.com.cisco.iscsi:{secrets.token_hex(6)}'
                                    print('IQN is {}'.format(kwargs.iqn_static_identifier))
                                    valid = True
                                elif question == 'N':
                                    kwargs.jData = deepcopy(jsonVars.StaticIqnName)
                                    kwargs.jData.varInput = 'What is the Static IQN you would like to assign'\
                                        ' to this LAN Policy?'
                                    kwargs.jData.varName = 'Static IQN'
                                    polVars.iqn_static_identifier = ezfunctions.varStringLoop(**kwargs)
                        else: polVars.pop('iqn_allocation_type')
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
                    kwargs.pci_order_consumed = {0:[],1:[]}
                    #================================================
                    # Prompt User for SAN Connectivity Policy
                    #================================================
                    kwargs.allow_opt_out = True
                    kwargs.policy = 'policies.san_connectivity.san_connectivity_policy'
                    kwargs = policy_select_loop(self, **kwargs)
                    san_connectivity_policy = kwargs.san_connectivity_policy
                    #================================================
                    # Pull PCI Order Consumed from SAN Policy
                    #================================================
                    if not san_connectivity_policy == '':
                        for item in kwargs.immDict.orgs[org].policies.san_connectivity:
                            if item.name == san_connectivity_policy:
                                for i in item.vhbas:
                                    if i.get('placement_pci_link') == None: placement_pci_link = 0
                                    else: placement_pci_link = i.placement_pci_link
                                    for x in i.placement_pci_order:
                                        kwargs.pci_order_consumed[placement_pci_link].append(x)
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'   BEGINNING vNIC Creation Process')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    #================================================
                    # Loop to Create vNIC(s)
                    #================================================
                    polVars.vnics = []
                    vnic_loop = False
                    while vnic_loop == False:
                        vnic = {}
                        jsonVars = jsonData.vnic.EthIf.allOf[1].properties
                        #================================================
                        # Prompt User for Failover
                        #================================================
                        kwargs.jData = deepcopy(jsonVars.FailoverEnabled)
                        kwargs.jData.varInput = f'Do you want to Enable Failover for this vNIC?'
                        kwargs.jData.varName  = 'Enable Failover'
                        vnic.enable_failover = ezfunctions.varBoolLoop(**kwargs)
                        #==================================================
                        # Prompt User for vNIC Name Prefix from Loop Count
                        #==================================================
                        if vnic.enable_failover == True:
                            fabrics = ['a']
                            varDefault = 'vnic'
                        else:
                            fabrics = ['a','b']
                            if inner_loop_count < 5: varDefault = name_suffix[inner_loop_count -1]
                            else: varDefault = 'vnic'
                        kwargs.jData = deepcopy(jsonVars.Name)
                        kwargs.jData.default  = varDefault
                        kwargs.jData.minimum  = 1
                        kwargs.jData.varInput = f'What is the name for this/these vNIC?'
                        kwargs.jData.varName  = 'vNIC Name'
                        Name = ezfunctions.varStringLoop(**kwargs)
                        vnic.names = []
                        for x in fabrics: vnic.names.append(f'{Name}-{x}')
                        kwargs.name = Name

                        if target_platform == 'FIAttached':
                            #==================================================
                            # Prompt User for vNIC MAC Type
                            #==================================================
                            kwargs.jData = deepcopy(jsonVars.MacAddressType)
                            kwargs.jData.varType = 'Mac Address Type'
                            mac_address_allocation_type = ezfunctions.variablesFromAPI(**kwargs)
                            if mac_address_allocation_type == 'POOL':
                                #==================================================
                                # Prompt User for MAC Address Pools
                                #==================================================
                                vnic.mac_address_pools = []
                                for x in range(len(fabrics)):
                                    kwargs.allow_opt_out = False
                                    kwargs.policy = 'pools.mac.mac_pool'
                                    kwargs.optional_message = '* {} MAC Address Pool'.format(vnic.names[x])
                                    kwargs = policy_select_loop(self, **kwargs)
                                    vnic.mac_address_pools.append(kwargs['mac_pool'])
                                    kwargs.pop('optional_message')
                            else:
                                #==================================================
                                # Prompt User for vNIC Static MAC Addresses
                                #==================================================
                                vnic.mac_address_allocation_type = mac_address_allocation_type
                                vnic.mac_addresses_static = []
                                for x in fabrics:
                                    kwargs.jData = deepcopy(jsonVars.StaticMacAddress)
                                    if vnic.enable_failover == True:
                                        kwargs.jData.varInput = f'What is the static MAC Address?'
                                    else:
                                        kwargs.jData.varInput = f'What is the static MAC Address for Fabric {x.upper()}?'
                                    if vnic.enable_failover == True: kwargs.jData.varName = f'Static Mac Address'
                                    else: kwargs.jData.varName = f'Fabric {x} Mac Address'
                                    kwargs.jData.pattern = jsonData.boot.Pxe.allOf[1].properties.MacAddress.pattern
                                    vnic.mac_addresses_static.append(ezfunctions.varStringLoop(**kwargs))
                        #==============================================
                        # Get API Data
                        #==============================================
                        jsonVars = jsonData.vnic.PlacementSettings.allOf[1].properties
                        placement_pci_links    = []
                        placement_slot_ids     = []
                        placement_uplink_ports = []
                        if target_platform == 'Standalone': vnic.placement_uplink_ports = []
                        for x in fabrics:
                            #==================================================
                            # Prompt User for Placement PCI Link(s)
                            #==================================================
                            kwargs.jData = deepcopy(jsonVars.PciLink)
                            if vnic.enable_failover == False:
                                kwargs.jData.description = kwargs.jData.description + \
                                    f'\n\nPCI Link For Fabric {x.upper()}'
                            kwargs.jData.varInput = f'What is the PCI Link for Fabric {x.upper()}?'
                            if vnic.enable_failover == True: kwargs.jData.varName = 'PCI Link'
                            else: kwargs.jData.varName = f'Fabric {x.upper()} PCI Link'
                            placement_pci_links.append(ezfunctions.varNumberLoop(**kwargs))
                            #==================================================
                            # Prompt User for Placement Slot Id(s)
                            #==================================================
                            kwargs.jData = deepcopy(jsonVars.Id)
                            kwargs.jData.default  = 'MLOM'
                            kwargs.jData.varInput = 'What is the {}?'.format(jsonVars.Id.description)
                            kwargs.jData.varName  = 'vNIC PCIe Slot'
                            placement_slot_ids.append(ezfunctions.varStringLoop(**kwargs))
                            #==================================================
                            # Prompt User for Placement Uplink Port(s)
                            #==================================================
                            if target_platform == 'Standalone':
                                kwargs.jData = deepcopy(jsonVars.Uplink)
                                kwargs.jData.varInput = 'What is the {}?'.format(jsonVars.Uplink.description)
                                kwargs.jData.varName  = 'Adapter Port'
                                placement_uplink_ports.append(ezfunctions.varNumberLoop(**kwargs))
                        vnic.placement_slot_ids   = [*set(placement_slot_ids)]
                        if vnic.placement_slot_ids == ['MLOM']: vnic.pop('placement_slot_ids')
                        if target_platform == 'Standalone':
                            vnic.placement_uplink_ports = [*set(placement_uplink_ports)]
                            if vnic.placement_uplink_ports == [0]: vnic.pop('placement_uplink_ports')
                        #==============================================
                        # Get API Data
                        #==============================================
                        jsonVars = jsonData.vnic.Cdn.allOf[1].properties
                        #==================================================
                        # Prompt User for vNIC CDN Source
                        #==================================================
                        kwargs.jData = deepcopy(jsonVars.Source)
                        kwargs.jData.varType = 'CDN Source'
                        vnic.cdn_source = ezfunctions.variablesFromAPI(**kwargs)
                        if vnic.cdn_source == 'user':
                            #==================================================
                            # Prompt User for vNIC CDN Name(s)
                            #==================================================
                            vnic.cdn_values = []
                            for x in fabrics:
                                kwargs.jData = deepcopy(jsonVars.Value)
                                kwargs.jData.minimum = 1
                                if vnic.enable_failover == True:
                                    kwargs.jData.varInput = 'What is the value for the Consistent Device Name?'
                                else:
                                    kwargs.jData.varInput = f'What is the value for Fabric {x.upper()} Consistent Device Name?'
                                kwargs.jData.varName = 'CDN Name'
                                vnic[f'cdn_values.append(ezfunctions.varStringLoop(**kwargs))']
                        else: vnic.pop('cdn_source')
                        #==================================================
                        # Prompt User for Policy Assignments
                        #==================================================
                        policy_list = ['policies.ethernet_adapter.ethernet_adapter_policy']
                        if target_platform == 'Standalone':
                            policy_list.append('policies.ethernet_network.ethernet_network_policy')
                        else:
                            policy_list.append('policies.ethernet_network_control.ethernet_network_control_policy')
                            policy_list.append('policies.ethernet_network_group.ethernet_network_group_policy')
                        policy_list.append('policies.ethernet_qos.ethernet_qos_policy')
                        kwargs.allow_opt_out = False
                        for policy in policy_list:
                            kwargs.policy = policy
                            kwargs = policy_select_loop(self, **kwargs)
                            vnic['{}'.format(policy.split('.')[2])] = kwargs['{}'.format(policy.split('.')[2])]
                        if polVars.get('iqn_allocation_type'):
                            kwargs.policy = 'policies.iscsi_boot.iscsi_boot_policy'
                            if vnic.enable_failover == False:
                                kwargs.optional_message = f'iSCSI Boot Policy for Fabric {x.upper()}'
                            kwargs = policy_select_loop(self, **kwargs)
                            vnic.iscsi_boot_policy = kwargs.iscsi_boot_policy
                        #==================================================
                        # Configure Placement PCI Order
                        #==================================================
                        if vnic.enable_failover == False: vnic.pop('enable_failover')
                        vnic.placement_pci_order = []
                        for x in range(len(fabrics)):
                            pci_link = placement_pci_links[x]
                            vnic.placement_pci_order.append(kwargs.pci_order_consumed[pci_link][-1]+1)
                            kwargs.pci_order_consumed[pci_link].append(kwargs.pci_order_consumed[pci_link][-1]+1)
                        vnic.placement_pci_links  = [*set(placement_pci_links)]
                        if vnic.placement_pci_links == [0]: vnic.pop('placement_pci_links')
                        #==============================================
                        # Print Policy and Prompt User to Accept
                        #==============================================
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        print(textwrap.indent(yaml.dump(vnic, Dumper=MyDumper, default_flow_style=False), ' '*4, predicate=None))
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        valid_confirm = False
                        while valid_confirm == False:
                            confirm_conf = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
                            pol_type = 'vNIC'
                            if confirm_conf == 'Y' or confirm_conf == '':
                                polVars.vnics.append(vnic)
                                #==============================================
                                # Create Additional Policy or Exit Loop
                                #==============================================
                                valid_exit = False
                                while valid_exit == False:
                                    if inner_loop_count < 4:
                                        configure_loop, policy_loop = ezfunctions.exit_default(pol_type, 'Y')
                                    else: vnic_loop, valid_confirm = ezfunctions.exit_default(pol_type, 'N')
                                    if vnic_loop == False and valid_confirm == False:
                                        inner_loop_count += 1
                                        valid_confirm = True
                                        valid_exit = True
                                    else: valid_exit = True
                            elif confirm_conf == 'N':
                                ezfunctions.message_starting_over(pol_type)
                                valid_confirm = True
                            else: ezfunctions.message_invalid_y_or_n('short')
                    if target_platform == 'Standalone': polVars.target_platform = target_platform
                    #==============================================
                    # Print Policy and Prompt User to Accept
                    #==============================================
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(textwrap.indent(yaml.dump(polVars, Dumper=MyDumper, default_flow_style=False), ' '*4, predicate=None))
                    print(f'-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
                        if confirm_policy == 'Y' or confirm_policy == '':
                            #==============================================
                            # Add Policy Variables to immDict
                            #==============================================
                            kwargs.class_path = 'policies,lan_connectivity'
                            kwargs = ezfunctions.ez_append(polVars, **kwargs)
                            #==============================================
                            # Create Additional Policy or Exit Loop
                            #==============================================
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
        baseRepo       = kwargs.args.dir
        configure_loop = False
        name_prefix    = self.name_prefix
        name_suffix    = 'link-agg'
        org            = self.org
        policy_type    = 'Link Aggregation Policy'
        yaml_file      = 'ethernet'
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  A Link Aggregation Policy will assign LACP settings to the Ethernet Port-Channels and')
            print(f'  uplinks.  We recommend the default wizard settings so you will only be asked for the ')
            print(f'  name and description for the Policy.  You only need one of these policies for ')
            print(f'  Organization {org}.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - {baseRepo}{os.sep}{org}{os.sep}{self.type}{os.sep}{yaml_file}.yaml')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            policy_loop = False
            while policy_loop == False:
                polVars = {}
                #==============================================
                # Prompt User for Name and Description
                #==============================================
                if not name_prefix == '': name = f'{name_prefix}-{name_suffix}'
                else: name = f'{name_suffix}'
                polVars.name        = ezfunctions.policy_name(name, policy_type)
                polVars.description = ezfunctions.policy_descr(polVars.name, policy_type)
                #==============================================
                # Print Policy and Prompt User to Accept
                #==============================================
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(textwrap.indent(yaml.dump(polVars, Dumper=MyDumper, default_flow_style=False), ' '*4, predicate=None))
                print(f'-------------------------------------------------------------------------------------------\n')
                valid_confirm = False
                while valid_confirm == False:
                    confirm_policy = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                    if confirm_policy == 'Y' or confirm_policy == '':
                        #==============================================
                        # Add Policy Variables to immDict
                        #==============================================
                        kwargs.class_path = 'policies,link_aggregation'
                        kwargs = ezfunctions.ez_append(polVars, **kwargs)
                        #==============================================
                        # Create Additional Policy or Exit Loop
                        #==============================================
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
        baseRepo       = kwargs.args.dir
        configure_loop = False
        name_prefix    = self.name_prefix
        name_suffix    = 'link-ctrl'
        org            = self.org
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
            print(f'  - {baseRepo}{os.sep}{org}{os.sep}{self.type}{os.sep}{yaml_file}.yaml')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            policy_loop = False
            while policy_loop == False:
                polVars = {}
                #==============================================
                # Prompt User for Name and Description
                #==============================================
                if not name_prefix == '': name = f'{name_prefix}-{name_suffix}'
                else: name = f'{name_suffix}'
                polVars.name        = ezfunctions.policy_name(name, policy_type)
                polVars.description = ezfunctions.policy_descr(polVars.name, policy_type)
                #==============================================
                # Print Policy and Prompt User to Accept
                #==============================================
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(textwrap.indent(yaml.dump(polVars, Dumper=MyDumper, default_flow_style=False), ' '*4, predicate=None))
                print(f'-------------------------------------------------------------------------------------------\n')
                valid_confirm = False
                while valid_confirm == False:
                    confirm_policy = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                    if confirm_policy == 'Y' or confirm_policy == '':
                        #==============================================
                        # Add Policy Variables to immDict
                        #==============================================
                        kwargs.class_path = 'policies,link_control'
                        kwargs = ezfunctions.ez_append(polVars, **kwargs)
                        #==============================================
                        # Create Additional Policy or Exit Loop
                        #==============================================
                        configure_loop, policy_loop = ezfunctions.exit_default(policy_type, 'N')
                        valid_confirm = True
                    elif confirm_policy == 'N':
                        ezfunctions.message_starting_over(policy_type)
                        valid_confirm = True
                    else: ezfunctions.message_invalid_y_or_n('long')
        # Return kwargs
        return kwargs

    #==============================================
    # Multicast Policy Module
    #==============================================
    def multicast(self, **kwargs):
        baseRepo       = kwargs.args.dir
        configure_loop = False
        domain_prefix  = kwargs.domain_prefix
        jsonData       = kwargs.jsonData
        name_suffix    = 'mcast'
        org            = self.org
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
            print(f'  - {baseRepo}{os.sep}{org}{os.sep}{self.type}{os.sep}{yaml_file}.yaml')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            policy_loop = False
            while policy_loop == False:
                polVars = {}
                #==============================================
                # Prompt User for Name and Description
                #==============================================
                if not domain_prefix == '': name = f'{domain_prefix}-{name_suffix}'
                else: name = f'{name_suffix}'
                polVars.name = ezfunctions.policy_name(name, policy_type)
                polVars.description = ezfunctions.policy_descr(polVars.name, policy_type)
                #==============================================
                # Get API Data
                #==============================================
                kwargs.multi_select = False
                jsonVars = jsonData.fabric.MulticastPolicy.allOf[1].properties
                #==============================================
                # Prompt User for Querier Infromation
                #==============================================
                kwargs.jData = deepcopy(jsonVars.QuerierIpAddress)
                kwargs.jData.varInput = 'IGMP Querier IP for Fabric Interconnect A.  [press enter to skip]:'
                kwargs.jData.varName  = 'IGMP Querier IP'
                polVars.querier_ip_address = ezfunctions.varStringLoop(**kwargs)
                if not polVars.querier_ip_address == '':
                    kwargs.jData = deepcopy(jsonVars.QuerierIpAddressPeer)
                    kwargs.jData.varInput = 'IGMP Querier Peer IP for Fabric Interconnect B.  [press enter to skip]:'
                    kwargs.jData.varName  = 'IGMP Querier Peer IP'
                    polVars.querier_ip_address_peer = ezfunctions.varStringLoop(**kwargs)
                if polVars.querier_ip_address == '': polVars.pop('querier_ip_address')
                #==============================================
                # Print Policy and Prompt User to Accept
                #==============================================
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(textwrap.indent(yaml.dump(polVars, Dumper=MyDumper, default_flow_style=False), ' '*4, predicate=None))
                print(f'-------------------------------------------------------------------------------------------\n')
                valid_confirm = False
                while valid_confirm == False:
                    confirm_policy = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                    if confirm_policy == 'Y' or confirm_policy == '':
                        #==============================================
                        # Add Policy Variables to immDict
                        #==============================================
                        kwargs.class_path = 'policies,multicast'
                        kwargs = ezfunctions.ez_append(polVars, **kwargs)
                        #==============================================
                        # Create Additional Policy or Exit Loop
                        #==============================================
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
        baseRepo        = kwargs.args.dir
        configure_loop  = False
        jsonData        = kwargs.jsonData
        name_prefix     = self.name_prefix
        name_suffix     = 'scp'
        org             = self.org
        policy_type     = 'SAN Connectivity Policy'
        target_platform = kwargs.target_platform
        yaml_file       = 'san_connectivity'
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  You can Skip this policy if you are not configuring Fibre-Channel.\n')
            print(f'  A {policy_type} will configure vHBA adapters for Server Profiles.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - {baseRepo}{os.sep}{org}{os.sep}{self.type}{os.sep}{yaml_file}.yaml')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure a {policy_type}?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                policy_loop = False
                while policy_loop == False:
                    #==============================================
                    # Prompt User for Name and Description
                    #==============================================
                    polVars = {}
                    if not name_prefix == '': name = f'{name_prefix}-{name_suffix}'
                    else: name = f'{name_suffix}'
                    polVars.name        = ezfunctions.policy_name(name, policy_type)
                    kwargs.name         = polVars.name
                    polVars.description = ezfunctions.policy_descr(polVars.name, policy_type)
                    #==============================================
                    # Get API Data
                    #==============================================
                    kwargs.multi_select = False
                    if target_platform == 'FIAttached':
                        #==============================================
                        # Prompt User for WWNN Allocation Type
                        #==============================================
                        kwargs.jData = deepcopy(jsonVars.WwnnAddressType)
                        kwargs.jData.varType = 'WWNN Allocation Type'
                        kwargs.wwnn_allocation_type = ezfunctions.variablesFromAPI(**kwargs)
                        #==============================================
                        # Prompt User for WWNN Pool
                        #==============================================
                        if kwargs.wwnn_allocation_type == 'POOL':
                            kwargs.allow_opt_out = False
                            kwargs.policy = 'pools.wwnn.wwnn_pool'
                            kwargs = policy_select_loop(self, **kwargs)
                            polVars.wwnn_pool = kwargs.wwnn_pool
                        #==============================================
                        # Prompt User for WWNN Static Address
                        #==============================================
                        else:
                            kwargs.jData = deepcopy(jsonVars.StaticWwnnAddress)
                            kwargs.jData.varInput = 'What is the Static WWNN you would like to assign to this SAN Policy?'
                            kwargs.jData.varName  = 'Static WWNN'
                            polVars.wwnn_static = ezfunctions.varStringLoop(**kwargs)
                    #================================================
                    # Loop to Create vHBA(s)
                    #================================================
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'   BEGINNING vHBA Creation Process')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    fabrics = ['a', 'b']
                    kwargs.order_consumed_0 = 0
                    kwargs.order_consumed_1 = 0
                    polVars.vhbas = []
                    inner_loop_count = 1
                    vhba_loop = False
                    while vhba_loop == False:
                        vhba = {}
                        #==============================================
                        # Get API Data
                        #==============================================
                        kwargs.policy_multi_select = False
                        jsonVars = jsonData.vnic.FcIfInventory.allOf[1].properties
                        kwargs.jData = deepcopy(jsonVars.Name)
                        kwargs.jData.default  = 'vhba'
                        kwargs.jData.minimum  = 1
                        kwargs.jData.varInput = f'What is the name for these vHBA(s)?'
                        kwargs.jData.varName  = 'vHBA Name'
                        Name = ezfunctions.varStringLoop(**kwargs)
                        vhba.names = []
                        for x in fabrics: vhba.names.append(f'{Name}-{x}')
                        kwargs.name = Name
                        #==================================================
                        # Prompt User for Persistent Lun Bindings
                        #==================================================
                        kwargs.jData = deepcopy(jsonVars.PersistentBindings)
                        kwargs.jData.default  = True
                        kwargs.jData.varInput = f'Do you want to Enable Persistent LUN Bindings?'
                        kwargs.jData.varName  = 'Persistent LUN Bindings'
                        kwargs.persistent_lun_bindings = ezfunctions.varBoolLoop(**kwargs)
                        #==============================================
                        # Prompt User for vHBA Type
                        #==============================================
                        jsonVars = jsonData.vnic.FcIf.allOf[1].properties
                        kwargs.jData = deepcopy(jsonVars.Type)
                        kwargs.jData.varType = 'vHBA Type'
                        vhba.vhba_type = ezfunctions.variablesFromAPI(**kwargs)
                        #==================================================
                        # Prompt User for vHBA WWPN Type
                        #==================================================
                        if target_platform == 'FIAttached':
                            kwargs.jData = deepcopy(jsonVars.WwpnAddressType)
                            kwargs.jData.varType = 'WWPN Allocation Type'
                            kwargs.wwpn_allocation_type = ezfunctions.variablesFromAPI(**kwargs)
                            if kwargs.wwpn_allocation_type == 'POOL':
                                vhba.wwpn_pools = []
                                kwargs.allow_opt_out = False
                                for x in fabrics:
                                    kwargs.policy = 'pools.wwpn.wwpn_pool'
                                    kwargs.optional_message = '* Select the WWPN Pool for Fabric {}'.format(x.upper())
                                    kwargs = policy_select_loop(self, **kwargs)
                                    vhba.wwpn_pools.append(kwargs[f'wwpn_pool'])
                                kwargs.pop('optional_message')
                            else:
                                vhba.wwpn_addresses_static = []
                                for x in fabrics:
                                    kwargs.jData = deepcopy(jsonVars.StaticWwpnAddress)
                                    kwargs.jData.varInput = f'What is the Static WWPN you would like to'\
                                        f' assign to Fabric {x.upper()}?'
                                    kwargs.jData.varName  = 'WWPN Static Address'
                                    vhba.wwpn_addresses_static.append(ezfunctions.varStringLoop(**kwargs))
                        #==============================================
                        # Get API Data
                        #==============================================
                        jsonVars = jsonData.vnic.PlacementSettings.allOf[1].properties
                        placement_pci_links    = []
                        placement_slot_ids     = []
                        placement_uplink_ports = []
                        if target_platform == 'Standalone': vhba.placement_uplink_ports = []
                        for x in fabrics:
                            #==================================================
                            # Prompt User for Placement PCI Link(s)
                            #==================================================
                            kwargs.jData = deepcopy(jsonVars.PciLink)
                            kwargs.jData.description = kwargs.jData.description + \
                                f'\n\nPCI Link For Fabric {x.upper()}'
                            kwargs.jData.varInput = f'What is the PCI Link for Fabric {x.upper()}?'
                            kwargs.jData.varName  = f'Fabric {x.upper()} PCI Link'
                            placement_pci_links.append(ezfunctions.varNumberLoop(**kwargs))
                            #==================================================
                            # Prompt User for Placement Slot Id(s)
                            #==================================================
                            kwargs.jData = deepcopy(jsonVars.Id)
                            kwargs.jData.default  = 'MLOM'
                            kwargs.jData.varInput = 'What is the {}?'.format(jsonVars.Id.description)
                            kwargs.jData.varName  = 'vHBA PCIe Slot'
                            placement_slot_ids.append(ezfunctions.varStringLoop(**kwargs))
                            if target_platform == 'Standalone':
                                kwargs.jData = deepcopy(jsonVars.Uplink)
                                kwargs.jData.varInput = 'What is the {}?'.format(jsonVars.Uplink.description)
                                kwargs.jData.varName  = 'Adapter Port'
                                placement_uplink_ports.append(ezfunctions.varNumberLoop(**kwargs))
                        vhba.placement_slot_ids   = [*set(placement_slot_ids)]
                        if vhba.placement_slot_ids == ['MLOM']: vhba.pop('placement_slot_ids')
                        if target_platform == 'Standalone':
                            vhba.placement_uplink_ports = [*set(placement_uplink_ports)]
                            if vhba.placement_uplink_ports == [0]: vhba.pop('placement_uplink_ports')
                        #================================================
                        # Prompt User for Policy Assignments
                        #================================================
                        policy_list = [
                            'policies.fc_zone.fc_zone_policies',
                            'policies.fibre_channel_adapter.fibre_channel_adapter_policy',
                            'policies.fibre_channel_qos.fibre_channel_qos_policy'
                        ]
                        for policy in policy_list:
                            kwargs.policy = policy
                            if 'fc_zone' in kwargs.policy:
                                kwargs.allow_opt_out = True
                                kwargs.policy_multi_select = True
                            else: kwargs.allow_opt_out = False
                            print(kwargs)
                            kwargs = policy_select_loop(self, **kwargs)
                            ptype = policy.split('.')[2]
                            vhba[ptype] = kwargs[ptype]
                        #================================================
                        # Prompt User for Fibre-Channel Network Policies
                        #================================================
                        vhba.fibre_channel_network_policies = []
                        for x in fabrics:
                            kwargs.policy = 'policies.fibre_channel_network.fibre_channel_network_policy'
                            ptype = kwargs.policy.split('.')[2]
                            kwargs.optional_message = 'The {} for vHBA on Fabric {}'.format(ptype, x.upper())
                            kwargs.name = Name
                            kwargs = policy_select_loop(self, **kwargs)
                            vhba.fibre_channel_network_policies.append(kwargs.fibre_channel_network_policy)
                            kwargs.pop('optional_message')

                        vhba.placement_pci_order = []
                        for x in range(len(fabrics)):
                            pci_link = placement_pci_links[x]
                            vhba.placement_pci_order.append(kwargs[f'order_consumed_{pci_link}'])
                            kwargs[f'order_consumed_{pci_link}'] += 1
                        
                        # Remove Placement Values if Match Defaults
                        vhba.placement_pci_links  = [*set(placement_pci_links)]
                        if vhba.placement_pci_links == [0]: vhba.pop('placement_pci_links')
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        print(textwrap.indent(yaml.dump(vhba, Dumper=MyDumper, default_flow_style=False), ' '*4, predicate=None))
                        print(f'-------------------------------------------------------------------------------------------\n')
                        valid_confirm = False
                        while valid_confirm == False:
                            confirm_conf = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
                            pol_type = 'vHBA'
                            if confirm_conf == 'Y' or confirm_conf == '':
                                polVars.vhbas.append(vhba)
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
                    if target_platform == 'Standalone': polVars.target_platform = target_platform
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(textwrap.indent(yaml.dump(polVars, Dumper=MyDumper, default_flow_style=False), ' '*4, predicate=None))
                    print(f'-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                        if confirm_policy == 'Y' or confirm_policy == '':
                            # Add Policy Variables to immDict
                            kwargs.class_path = 'policies,san_connectivity'
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
        baseRepo       = kwargs.args.dir
        configure_loop = False
        domain_prefix  = kwargs.domain_prefix
        jsonData       = kwargs.jsonData
        name_suffix    = 'sw-ctrl'
        org            = self.org
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
            print(f'  - {baseRepo}{os.sep}{org}{os.sep}{self.type}{os.sep}{yaml_file}.yaml')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            policy_loop = False
            while policy_loop == False:
                polVars = {}
                #==============================================
                # Prompt User for Name and Description
                #==============================================
                if not domain_prefix == '': name = f'{domain_prefix}-{name_suffix}'
                else: name = f'{name_suffix}'
                polVars.name        = ezfunctions.policy_name(name, policy_type)
                polVars.description = ezfunctions.policy_descr(polVars.name, policy_type)
                polVars.vlan_port_count_optimization = False
                #==============================================
                # Get API Data
                #==============================================
                kwargs.multi_select = False
                jsonVars = jsonData.fabric.SwitchControlPolicy.allOf[1].properties
                #==============================================
                # Prompt User for Ethernet Switching Mode
                #==============================================
                kwargs.jData = deepcopy(jsonVars.EthernetSwitchingMode)
                kwargs.jData.varType = 'Ethernet Switching Mode'
                polVars.ethernet_switching_mode = ezfunctions.variablesFromAPI(**kwargs)
                #==============================================
                # Prompt User for Fibre-Channel Switching Mode
                #==============================================
                kwargs.jData = deepcopy(jsonVars.FcSwitchingMode)
                kwargs.jData.varType = 'Fibre-Channel Switching Mode'
                polVars.fc_switching_mode = ezfunctions.variablesFromAPI(**kwargs)
                #==============================================
                # Print Policy and Prompt User to Accept
                #==============================================
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(textwrap.indent(yaml.dump(polVars, Dumper=MyDumper, default_flow_style=False), ' '*4, predicate=None))
                print(f'-------------------------------------------------------------------------------------------\n')
                valid_confirm = False
                while valid_confirm == False:
                    confirm_policy = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                    if confirm_policy == 'Y' or confirm_policy == '':
                        #==============================================
                        # Add Policy Variables to immDict
                        #==============================================
                        kwargs.class_path = 'policies,switch_control'
                        kwargs = ezfunctions.ez_append(polVars, **kwargs)
                        #==============================================
                        # Create Additional Policy or Exit Loop
                        #==============================================
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
        baseRepo       = kwargs.args.dir
        configure_loop = False
        domain_prefix  = kwargs.domain_prefix
        ezData         = kwargs.ezData
        jsonData       = kwargs.jsonData
        name_suffix    = 'qos'
        org            = self.org
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
            print(f'  - {baseRepo}{os.sep}{org}{os.sep}{self.type}{os.sep}{yaml_file}.yaml')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            policy_loop = False
            while policy_loop == False:
                polVars = {}
                #==============================================
                # Prompt User for Name and Description
                #==============================================
                if not domain_prefix == '': name = f'{domain_prefix}-{name_suffix}'
                else: name = f'{name_suffix}'
                polVars.name        = ezfunctions.policy_name(name, policy_type)
                polVars.description = ezfunctions.policy_descr(polVars.name, policy_type)
                #==============================================
                # Get API Data
                #==============================================
                kwargs.multi_select = False
                jsonVars = jsonData.fabric.QosClass.allOf[1].properties
                #==============================================
                # Prompt User for System MTU
                #==============================================
                kwargs.jData = deepcopy(jsonVars.Mtu)
                kwargs.jData.default = True
                kwargs.jData.varInput = f'Do you want to enable Jumbo MTU?'
                kwargs.jData.varName  = 'Domain MTU'
                mtu = ezfunctions.varBoolLoop(**kwargs)
                if mtu == True: domain_mtu = 9216
                else: domain_mtu = 1500
                #==============================================
                # Configure System Classes
                #==============================================
                priorities = ['Platinum', 'Gold', 'FC', 'Silver', 'Bronze', 'Best Effort']
                polVars.classes = []
                for i in priorities:
                    iDict = ezData.ezimm.allOf[1].properties.systemQos[i]
                    if i == 'FC': class_mtu = 2240
                    else: class_mtu = domain_mtu
                    polVars.classes.append({
                        'bandwidth_percent':iDict.bandwidth_percent,
                        'cos':iDict.bandwidth_percent,
                        'mtu':class_mtu,
                        'multicast_optimize':iDict.multicast_optimize,
                        'packet_drop':iDict.packet_drop,
                        'priority':i,
                        'state':'Enabled',
                        'weight':iDict.weight,
                    })
                #==============================================
                # Print Policy and Prompt User to Accept
                #==============================================
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(textwrap.indent(yaml.dump(polVars, Dumper=MyDumper, default_flow_style=False), ' '*4, predicate=None))
                print(f'-------------------------------------------------------------------------------------------\n')
                valid_confirm = False
                while valid_confirm == False:
                    confirm_policy = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                    if confirm_policy == 'Y' or confirm_policy == '':
                        #==============================================
                        # Add Policy Variables to immDict
                        #==============================================
                        kwargs.class_path = 'policies,system_qos'
                        kwargs = ezfunctions.ez_append(polVars, **kwargs)
                        #==============================================
                        # Create Additional Policy or Exit Loop
                        #==============================================
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
        baseRepo       = kwargs.args.dir
        configure_loop = False
        domain_prefix  = kwargs.domain_prefix
        name_suffix    = 'vlan'
        org            = self.org
        policy_type    = 'VLAN Policy'
        yaml_file      = 'vlan'
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  A {policy_type} will define the VLANs Assigned to the Fabric Interconnects.')
            print(f'  When configuring a VLAN List or Range the name will be used as a prefix in the format of:')
            print('     {name}-vlXXXX')
            print(f'  Where XXXX would be 0001 for vlan 1, 0100 for vlan 100, and 4094 for vlan 4094.')
            print(f'  If you want to Assign a Native VLAN Make sure it is in the vlan list for this wizard.')
            print(f'  IMPORTANT NOTE: You can only have one Native VLAN for the Fabric at this time,')
            print(f'                  as Disjoint Layer 2 is not yet supported.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - {baseRepo}{os.sep}{org}{os.sep}{self.type}{os.sep}{yaml_file}.yaml')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            policy_loop = False
            while policy_loop == False:
                polVars = {}
                #==============================================
                # Prompt User for Name and Description
                #==============================================
                if not domain_prefix == '': name = f'{domain_prefix}-{name_suffix}'
                else: name = f'{name_suffix}'
                polVars.name  = ezfunctions.policy_name(name, policy_type)
                kwargs.name   = polVars.name
                polVars.description = ezfunctions.policy_descr(polVars.name, policy_type)
                #==============================================
                # Prompt User for VLANs for the Policy
                #==============================================
                VlanList,vlanListExpanded = ezfunctions.vlan_pool(polVars.name)
                if len(vlanListExpanded) == 1:
                    vlan_name = '%s' % (input(f'Enter the Name you want to assign to "{VlanList}".  [{org}]: '))
                    max = 62
                else:
                    vlan_name = '%s' % (input(f'Enter the Prefix Name you want to assign to "{VlanList}".  [{org}]: '))
                    max = 55
                if vlan_name == '': vlan_name = org
                valid_name = validating.name_rule('VLAN Name', vlan_name, 1, max)
                native_vlan = ezfunctions.vlan_native_function(vlanListExpanded, VlanList)
                if not native_vlan == '':
                    valid_name = False
                    while valid_name == False:
                        native_name = '%s' % (input(f'Enter the Name to assign to the Native VLAN {native_vlan}.  [default]: '))
                        if native_name == '': native_name = 'default'
                        valid_name = validating.name_rule('VLAN Name', vlan_name, 1, 62)
                #==============================================
                # Prompt User for Multicast Policy
                #==============================================
                kwargs.policy = 'policies.multicast.multicast_policy'
                kwargs.allow_opt_out = False
                kwargs = policy_select_loop(self, **kwargs)
                polVars.vlans = []
                if not native_vlan == '' and len(VlanList) > 1:
                    if int(native_vlan) == 1: auto_native = True
                    else: auto_native = False
                    vlanListExpanded.remove(1)
                    polVars.vlans.append({
                        'auto_allow_on_uplinks':auto_native,
                        'multicast_policy':kwargs.multicast_policy,
                        'name':native_name, 'native_vlan':True,
                        'vlan_list':native_vlan
                    })
                vlan_list = ezfunctions.vlan_list_format(vlanListExpanded)
                polVars.vlans.append({
                        'multicast_policy':kwargs.multicast_policy,
                        'name':vlan_name, 'vlan_list':vlan_list
                })
                #==============================================
                # Print Policy and Prompt User to Accept
                #==============================================
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(textwrap.indent(yaml.dump(polVars, Dumper=MyDumper, default_flow_style=False), ' '*4, predicate=None))
                print(f'-------------------------------------------------------------------------------------------\n')
                valid_confirm = False
                while valid_confirm == False:
                    confirm_policy = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                    if confirm_policy == 'Y' or confirm_policy == '':
                        #==============================================
                        # Add Policy Variables to immDict
                        #==============================================
                        kwargs.class_path = 'policies,vlan'
                        kwargs = ezfunctions.ez_append(polVars, **kwargs)
                        #==============================================
                        # Create Additional Policy or Exit Loop
                        #==============================================
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
        baseRepo       = kwargs.args.dir
        configure_loop = False
        domain_prefix  = kwargs.domain_prefix
        jsonData       = kwargs.jsonData
        org            = self.org
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
            print(f'  - {baseRepo}{os.sep}{org}{os.sep}{self.type}{os.sep}{yaml_file}.yaml')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure a {policy_type}?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                loop_count = 0
                policy_loop = False
                while policy_loop == False:
                    polVars = {}
                    #==============================================
                    # Prompt User for Name and Description
                    #==============================================
                    name = ezfunctions.naming_rule_fabric(loop_count, domain_prefix, org)
                    polVars.name        = ezfunctions.policy_name(name, policy_type)
                    kwargs.name         = polVars.name
                    polVars.description = ezfunctions.policy_descr(polVars.name, policy_type)
                    polVars.auto_allow_on_uplinks = True
                    #==============================================
                    # Get API Data
                    #==============================================
                    kwargs.multi_select = False
                    jsonVars = jsonData.fabric.FcNetworkPolicy.allOf[1].properties
                    #==============================================
                    # Prompt User for Uplink Trunking
                    #==============================================
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  Uplink Trunking: Default is No.')
                    print(f'     Most deployments do not enable Uplink Trunking for Fibre-Channel. ')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    kwargs.jData = deepcopy(jsonVars.EnableTrunking)
                    kwargs.jData.default  = False
                    kwargs.jData.varInput = f'Do you want to Enable Uplink Trunking for this VSAN Policy?'
                    kwargs.jData.varName  = 'Enable Trunking'
                    kwargs.uplink_trunking = ezfunctions.varBoolLoop(**kwargs)
                    #==============================================
                    # Prompt User for VSAN(s) for the Policy
                    #==============================================
                    polVars.vsans = []
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
                            else: ezfunctions.message_invalid_vxan()
                        #==============================================
                        # Prompt User for FCoE VLAN
                        #==============================================
                        valid = False
                        while valid == False:
                            fcoe_id = input(f'Enter the VLAN id for the FCoE VLAN to encapsulate "{vsan_id}" over Ethernet.'\
                                f'  [{vsan_id}]: ')
                            if fcoe_id == '': fcoe_id = vsan_id
                            if re.search(r'[0-9]{1,4}', str(fcoe_id)):
                                valid_vlan = validating.number_in_range('VSAN ID', fcoe_id, 1, 4094)
                                if valid_vlan == True:
                                    kwargs.policy = 'policies.vlan.vlan_policy'
                                    kwargs.allow_opt_out = False
                                    kwargs = policy_select_loop(self, **kwargs)
                                    vlan_list = []
                                    for item in kwargs.immDict.orgs[org].policies.vlan:
                                        if item.name == kwargs.vlan_policy:
                                            for i in item.vlans:
                                                vlan_list.append(i.vlan_list)
                                    vlan_list = ezfunctions.vlan_list_full(','.join(vlan_list))
                                    overlap = False
                                    for vlan in vlan_list:
                                        if int(vlan) == int(fcoe_id):
                                            ezfunctions.message_fcoe_vlan(fcoe_id, kwargs.vlan_policy)
                                            overlap = True
                                            break
                                    if overlap == False: valid = True
                                else: ezfunctions.message_invalid_vxan()
                            else: ezfunctions.message_invalid_vxan()
                        jsonVars = jsonData.fabric.Vsan.allOf[1].properties
                        #==============================================
                        # Prompt User for VSAN Name
                        #==============================================
                        kwargs.jData = deepcopy(jsonVars.Name)
                        kwargs.jData.default = f'vsan-{vsan_id}'
                        kwargs.jData.pattern = '^[a-zA-Z0-9\\_\\-]{1,62}$'
                        kwargs.jData.varInput = f'What Name would you like to assign to "{vsan_id}"?'
                        kwargs.jData.varName = 'VSAN Name'
                        vsan_name = ezfunctions.varStringLoop(**kwargs)
                        #==============================================
                        # Prompt User for VSAN Scope
                        #==============================================
                        kwargs.jData = deepcopy(jsonVars.VsanScope)
                        kwargs.jData.varType = 'Vsan Scope'
                        vsan_scope = ezfunctions.variablesFromAPI(**kwargs)
                        vsan = {
                            'fcoe_vlan_id':fcoe_id, 'name':vsan_name,
                            'vsan_id':vsan_id, 'vsan_scope':vsan_scope
                        }
                        #==============================================
                        # Print Policy and Prompt User to Accept
                        #==============================================
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        print(textwrap.indent(yaml.dump(vsan, Dumper=MyDumper, default_flow_style=False), ' '*4, predicate=None))
                        print(f'-------------------------------------------------------------------------------------------\n')
                        valid_confirm = False
                        while valid_confirm == False:
                            pol_type = 'VSAN'
                            confirm_vsan = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                            if confirm_vsan == 'Y' or confirm_vsan == '':
                                polVars.vsans.append(vsan)
                                #==============================================
                                # Create Additional Policy or Exit Loop
                                #==============================================
                                valid_exit = False
                                while valid_exit == False:
                                    valid_exit, vsan_loop = ezfunctions.exit_default(pol_type, 'N')
                                    if valid_exit == True: vsan_count += 1; valid_confirm = True; valid_exit = True
                                    else: valid_confirm = True; valid_exit = True
                            elif confirm_vsan == 'N':
                                ezfunctions.message_starting_over(pol_type)
                                valid_confirm = True
                            else: ezfunctions.message_invalid_y_or_n('short')
                    #==============================================
                    # Print Policy and Prompt User to Accept
                    #==============================================
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(textwrap.indent(yaml.dump(polVars, Dumper=MyDumper, default_flow_style=False), ' '*4, predicate=None))
                    print(f'-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                        if confirm_policy == 'Y' or confirm_policy == '':
                            #==============================================
                            # Add Policy Variables to immDict
                            #==============================================
                            kwargs.class_path = 'policies,vsan'
                            kwargs = ezfunctions.ez_append(polVars, **kwargs)
                            #==============================================
                            # Create Additional Policy or Exit Loop
                            #==============================================
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
def policy_select_loop(self, **kwargs):
    ezData      = kwargs.ezData
    policy      = kwargs.policy
    name        = kwargs.name
    name_prefix = self.name_prefix
    org         = kwargs.org
    loop_valid  = False
    while loop_valid == False:
        create_policy = True
        kwargs.inner_policy = policy.split('.')[1]
        kwargs.inner_type   = policy.split('.')[0]
        kwargs.inner_var    = policy.split('.')[2]
        inner_policy = kwargs.inner_policy
        inner_type   = kwargs.inner_type
        inner_var    = kwargs.inner_var
        policy_description = ezfunctions.mod_pol_description(inner_var)
        kwargs = ezfunctions.policies_parse(inner_type, inner_policy, **kwargs)
        if not len(kwargs.policies[kwargs.inner_policy]) > 0:
            valid = False
            while valid == False:
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'   There was no {policy_description} found.')
                print(f'\n-------------------------------------------------------------------------------------------\n')
                if kwargs.allow_opt_out == True:
                    Question = input(f'Do you want to create a(n) {policy_description}?  Enter "Y" or "N" [Y]: ')
                    if Question == '' or Question == 'Y': create_policy = True; valid = True
                    elif Question == 'N': create_policy = False; valid = True; return kwargs
                else: create_policy = True; valid = True
        else:
            kwargs.name = name
            kwargs = ezfunctions.choose_policy(inner_policy, **kwargs)
            if kwargs.policy == 'create_policy': create_policy = True
            elif kwargs.policy == '' and kwargs.allow_opt_out == True:
                loop_valid = True
                create_policy = False
                kwargs[kwargs.inner_var] = ''
                return kwargs
            elif not kwargs.policy == '':
                loop_valid = True
                create_policy = False
                kwargs[kwargs.inner_var] = kwargs.policy
                return kwargs
        # Simple Loop to show name_prefix in Use
        ncount = 0
        if ncount == 5: print(name_prefix)
        # Create Policy if Option was Selected
        if create_policy == True:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  Starting module to create {policy_description} in Organization {org}')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            list_lansan = ezData.ezimm.allOf[1].properties.list_lansan.enum
            if re.search('pool$', inner_var):
                kwargs = eval(f'pools.pools(name_prefix, org, inner_type).{inner_policy}(**kwargs)')
            elif inner_policy in list_lansan:
                kwargs = eval(f'policies(name_prefix, org, inner_type).{inner_policy}(**kwargs)')
    # Return kwargs
    return kwargs