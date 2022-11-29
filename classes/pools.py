from copy import deepcopy
import ezfunctions
import ipaddress
import re
import textwrap
import validating
import yaml

class MyDumper(yaml.Dumper):
    def increase_indent(self, flow=False, indentless=False):
        return super(MyDumper, self).increase_indent(flow, False)

class pools(object):
    def __init__(self, name_prefix, org, type):
        self.name_prefix = name_prefix
        self.org = org
        self.type = type

    #==============================================
    # IP Pools Module
    #==============================================
    def ip(self, **kwargs):
        baseRepo       = kwargs['args'].dir
        configure_loop = False
        jsonData       = kwargs['jsonData']
        name_prefix    = self.name_prefix
        name_suffix    = 'ip'
        org            = self.org
        path_sep       = kwargs['path_sep']
        policy_type    = 'IP Pool'
        yaml_file      = 'pools'
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  At a minimum you will need one IP Pool for KVM Access to Servers.  Currently out-of-band')
            print(f'  management is not supported for KVM access.  This IP Pool will need to be associated to a ')
            print(f'  VLAN assigned to the VLAN Pool of the Domain.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - {baseRepo}{path_sep}{org}{path_sep}{self.type}{path_sep}{yaml_file}.yaml')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure an {policy_type}?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                policy_loop = False
                while policy_loop == False:
                    polVars = {}
                    if not name_prefix == '': name = f'{name_prefix}-{name_suffix}'
                    else: name = f'{name_suffix}'
                    polVars['name']        = ezfunctions.policy_name(name, policy_type)
                    polVars['description'] = ezfunctions.policy_descr(polVars['name'], policy_type)
                    # Pull Information from API Documentation
                    kwargs['multi_select'] = False
                    jsonVars = jsonData['pool.AbstractPool']['allOf'][1]['properties']
                    #==============================================
                    # Prompt User for Assignment Order
                    #==============================================
                    kwargs['jData'] = deepcopy(jsonVars['AssignmentOrder'])
                    kwargs['jData']['varType'] = 'Assignment Order'
                    polVars['assignment_order'] = ezfunctions.variablesFromAPI(**kwargs)
                    valid = False
                    while valid == False:
                        config_ipv4 = input('Do you want to configure IPv4 for this Pool?  Enter "Y" or "N" [Y]: ')
                        if config_ipv4 == 'Y' or config_ipv4 == '': 
                            config_ipv4 = 'Y'
                            valid = True
                        elif config_ipv4 == 'N': valid = True
                        else: ezfunctions.message_invalid_y_or_n('short')
                    if config_ipv4 == 'Y':
                        #==============================================
                        # Prompt User for Subnet Mask
                        #==============================================
                        jsonVars = jsonData['ippool.IpV4Config']['allOf'][1]['properties']
                        kwargs['jData'] = deepcopy(jsonVars['Netmask'])
                        kwargs['jData']['default']  = '255.255.255.0'
                        kwargs['jData']['varInput'] = 'Subnet Mask:'
                        kwargs['jData']['varName']  = 'Subnet Mask'
                        kwargs['subnetMask'] = ezfunctions.varStringLoop(**kwargs)
                        #==============================================
                        # Prompt User for Default Gateway
                        #==============================================
                        kwargs['jData'] = deepcopy(jsonVars['Gateway'])
                        kwargs['jData']['default']  = '198.18.1.1'
                        kwargs['jData']['varInput'] = 'Default Gateway:'
                        kwargs['jData']['varName']  = 'Default Gateway'
                        kwargs['defaultGateway'] = ezfunctions.varStringLoop(**kwargs)
                        #==============================================
                        # Prompt User for Primary DNS Server
                        #==============================================
                        kwargs['jData'] = deepcopy(jsonVars['PrimaryDns'])
                        kwargs['jData']['default']  = '208.67.220.220'
                        kwargs['jData']['varInput'] = f'Primary DNS Server.'
                        kwargs['jData']['varName']  = f'Primary DNS Server'
                        primaryDns = ezfunctions.varStringLoop(**kwargs)
                        #==============================================
                        # Prompt User for Secondary DNS Server
                        #==============================================
                        kwargs['jData'] = deepcopy(jsonVars['SecondaryDns'])
                        kwargs['jData']['varInput'] = f'Secondary DNS Server.  [press enter to skip]:'
                        kwargs['jData']['varName']  = f'Secondary DNS Server'
                        secondaryDns = ezfunctions.varStringLoop(**kwargs)
                        #==============================================
                        # Configure IPv4 Configuration Parameters
                        #==============================================
                        polVars['ipv4_config'] = [{
                            'gateway':kwargs['defaultGateway'], 'netmask':kwargs['subnetMask'],
                            'primary_dns':primaryDns, 'secondary_dns':secondaryDns
                        }]
                        polVars['ipv4_blocks'] = []
                        inner_loop_count = 0
                        ipv4_loop = False
                        while ipv4_loop == False:
                            jsonVars = jsonData['ippool.IpV4Block']['allOf'][1]['properties']
                            #==============================================
                            # Prompt User for IPv4 Block Starting Address
                            #==============================================
                            kwargs['ip_version'] = 'v4'
                            subnetList = ezfunctions.subnet_list(**kwargs)
                            kwargs['jData'] = deepcopy(jsonVars['From'])
                            kwargs['jData']['default']  = subnetList[9]
                            kwargs['jData']['varInput'] = f'What is the Starting IP Address to Assign to the Block?'
                            kwargs['jData']['varName']  = f'IPv4 Block Starting IP Address'
                            kwargs['pool_from'] = ezfunctions.varStringLoop(**kwargs)
                            #==============================================
                            # Prompt User for Block Size
                            #==============================================
                            jsonVars = jsonData['pool.AbstractBlockType']['allOf'][1]['properties']
                            kwargs['jData'] = deepcopy(jsonVars['Size'])
                            kwargs['jData']['default']  = len(subnetList)-10
                            kwargs['jData']['varInput'] = 'How Many IP Addresses should be added to the Block?  Range is 1-1024.'
                            kwargs['jData']['varName'] = 'Block Size'
                            pool_size = ezfunctions.varNumberLoop(**kwargs)
                            #==============================================
                            # Configure IP Block Parameters
                            #==============================================
                            beginx = int(ipaddress.IPv4Address(kwargs['pool_from']))
                            add_dec = (beginx + int(pool_size) - 1)
                            kwargs['pool_to'] = str(ipaddress.IPv4Address(add_dec))
                            valid = validating.error_subnet_check(**kwargs)
                            ipv4_block = {'from':str(kwargs['pool_from']), 'size':pool_size}
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            print(textwrap.indent(yaml.dump(ipv4_block, Dumper=MyDumper, default_flow_style=False), ' '*4, predicate=None))
                            print(f'-------------------------------------------------------------------------------------------\n')
                            valid_confirm = False
                            while valid_confirm == False:
                                confirm_conf = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
                                pol_type = 'IPv4 Block'
                                if confirm_conf == 'Y' or confirm_conf == '':
                                    polVars['ipv4_blocks'].append(ipv4_block)
                                    valid_exit = False
                                    while valid_exit == False:
                                        ipv4_loop, valid_confirm = ezfunctions.exit_default(pol_type, 'N')
                                        if ipv4_loop == False and valid_confirm == False:
                                            inner_loop_count += 1
                                            valid_confirm = True
                                            valid_exit = True
                                        else: valid_exit = True
                                elif confirm_conf == 'N':
                                    ezfunctions.message_starting_over(pol_type)
                                    valid_confirm = True
                                else: ezfunctions.message_invalid_y_or_n('short')
                    valid = False
                    while valid == False:
                        config_ipv6 = input('Do you want to configure IPv6 for this Pool?  Enter "Y" or "N" [N]: ')
                        if config_ipv6 == 'Y': 
                            config_ipv6 = 'Y'
                            valid = True
                        elif config_ipv6 == 'N' or config_ipv6 == '': valid = True
                        else: ezfunctions.message_invalid_y_or_n('short')

                    if config_ipv6 == 'Y':
                        jsonVars = jsonData['ippool.IpV6Config']['allOf'][1]['properties']
                        #==============================================
                        # Prompt User for Subnet Prefix
                        #==============================================
                        kwargs['jData'] = deepcopy(jsonVars['Prefix'])
                        kwargs['jData']['default']  = 64
                        kwargs['jData']['varInput'] = f'Prefix:'
                        kwargs['jData']['varName']  = f'Prefix'
                        kwargs['prefix'] = ezfunctions.varNumberLoop(**kwargs)
                        #==============================================
                        # Prompt User for Default Gateway
                        #==============================================
                        kwargs['jData'] = deepcopy(jsonVars['Gateway'])
                        kwargs['jData']['default']  = '2001:db8::1'
                        kwargs['jData']['varInput'] = f'Default Gateway:'
                        kwargs['jData']['varName']  = f'Default Gateway'
                        kwargs['defaultGateway'] = ezfunctions.varStringLoop(**kwargs)
                        #==============================================
                        # Prompt User for Primary DNS Server
                        #==============================================
                        kwargs['jData'] = deepcopy(jsonVars['SecondaryDns'])
                        kwargs['jData']['default']  = '2620:119:53::53'
                        kwargs['jData']['varInput'] = f'Primary DNS Server.'
                        kwargs['jData']['varName']  = f'Primary DNS Server'
                        primaryDns = ezfunctions.varStringLoop(**kwargs)
                        #==============================================
                        # Prompt User for Secondary DNS Server
                        #==============================================
                        kwargs['jData'] = deepcopy(jsonVars['SecondaryDns'])
                        kwargs['jData']['varInput'] = f'Secondary DNS Server.  [press enter to skip]:'
                        kwargs['jData']['varName']  = f'Secondary DNS Server'
                        secondaryDns = ezfunctions.varStringLoop(**kwargs)
                        #==============================================
                        # Configure IPv6 Configuration Parameters
                        #==============================================
                        polVars['ipv6_config'] = [{
                            'gateway':kwargs['defaultGateway'], 'prefix':kwargs['prefix'],
                            'primary_dns':primaryDns, 'secondary_dns':secondaryDns
                        }]
                        polVars['ipv6_blocks'] = []
                        inner_loop_count = 0
                        ipv6_loop = False
                        while ipv6_loop == False:
                            jsonVars = jsonData['ippool.IpV6Block']['allOf'][1]['properties']
                            #==============================================
                            # Prompt User for IPv6 Block Starting Address
                            #==============================================
                            v6network = ipaddress.ip_network(f"{kwargs['defaultGateway']}/{kwargs['prefix']}", strict=False)
                            kwargs['ip_version'] = 'v6'
                            kwargs['jData'] = deepcopy(jsonVars['From'])
                            kwargs['jData']['default']  = v6network[10]
                            kwargs['jData']['varInput'] = f'What is the Starting IPv6 Address to Assign to the Block?'
                            kwargs['jData']['varName']  = f'IPv6 Block Starting IP Address'
                            kwargs['pool_from'] = ezfunctions.varStringLoop(**kwargs)
                            #==============================================
                            # Prompt User for Block Size
                            #==============================================
                            jsonVars = jsonData['pool.AbstractBlockType']['allOf'][1]['properties']
                            kwargs['jData'] = deepcopy(jsonVars['Size'])
                            kwargs['jData']['default']  = 1024
                            kwargs['jData']['varInput'] = 'How Many IPv6 Addresses should be added to the Pool?  Range is 1-1024.'
                            kwargs['jData']['varName'] = 'Pool Size'
                            pool_size = ezfunctions.varNumberLoop(**kwargs)
                            #==============================================
                            # Configure IP Block Parameters
                            #==============================================
                            beginx = int(ipaddress.IPv6Address(kwargs['pool_from']))
                            add_dec = (beginx + int(pool_size) - 1)
                            kwargs['pool_to'] = str(ipaddress.IPv6Address(add_dec))
                            valid = validating.error_subnet_check(**kwargs)
                            ipv6_block = {'from':str(kwargs['pool_from']), 'size':pool_size}
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            print(textwrap.indent(yaml.dump(ipv6_block, Dumper=MyDumper, default_flow_style=False), ' '*4, predicate=None))
                            print(f'-------------------------------------------------------------------------------------------\n')
                            valid_confirm = False
                            while valid_confirm == False:
                                confirm_conf = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
                                pol_type = 'IPv6 Block'
                                if confirm_conf == 'Y' or confirm_conf == '':
                                    polVars['ipv6_blocks'].append(ipv6_block)
                                    valid_exit = False
                                    while valid_exit == False:
                                        ipv6_loop, valid_confirm = ezfunctions.exit_default(pol_type, 'N')
                                        if ipv6_loop == False and valid_confirm == False:
                                            inner_loop_count += 1
                                            valid_confirm = True
                                            valid_exit = True
                                        else: valid_exit = True
                                elif confirm_conf == 'N':
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
                            kwargs['class_path'] = 'intersight,pools,ip'
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
    # IQN Pools Module
    #==============================================
    def iqn(self, **kwargs):
        baseRepo       = kwargs['args'].dir
        configure_loop = False
        jsonData       = kwargs['jsonData']
        name_prefix    = self.name_prefix
        name_suffix    = 'ip'
        org            = self.org
        path_sep       = kwargs['path_sep']
        policy_type    = 'IQN Pool'
        yaml_file      = 'pools'
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure a {policy_type}.  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                policy_loop = False
                while policy_loop == False:
                    polVars = {}
                    if not name_prefix == '': name = f'{name_prefix}-{name_suffix}'
                    else: name = f'{name_suffix}'
                    polVars['name']        = ezfunctions.policy_name(name, policy_type)
                    polVars['description'] = ezfunctions.policy_descr(polVars['name'], policy_type)
                    kwargs['multi_select'] = False
                    jsonVars = jsonData['pool.AbstractPool']['allOf'][1]['properties']
                    kwargs['jData'] = deepcopy(jsonVars['AssignmentOrder'])
                    kwargs['jData']['varType'] = 'Assignment Order'
                    polVars['assignment_order'] = ezfunctions.variablesFromAPI(**kwargs)
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
                        jsonVars = jsonData['iqnpool.Pool']['allOf'][1]['properties']
                        #==============================================
                        # Prompt User for IQN Prefix
                        #==============================================
                        kwargs['jData'] = deepcopy(jsonVars['Prefix'])
                        kwargs['jData']['default']  = 'iqn.1984-12.com.cisco'
                        kwargs['jData']['maximum']  = 64
                        kwargs['jData']['minimum']  = 7
                        kwargs['jData']['pattern']  = '^$|^(?:iqn\\.[0-9]{4}-[0-9]{2}(?:\\.[A-Za-z](?:[A-Za-z0-9\\-]*[A-Za-z0-9])?)+?'
                        kwargs['jData']['varInput'] = 'What is the IQN Prefix you would like to assign to the Pool?'
                        kwargs['jData']['varName']  = 'IQN Prefix'
                        prefix = ezfunctions.varStringLoop(**kwargs)
                        #==============================================
                        # Prompt User for Starting Address
                        #==============================================
                        jsonVars = jsonData['iqnpool.IqnSuffixBlock']['allOf'][1]['properties']
                        kwargs['jData'] = deepcopy(jsonVars['From'])
                        kwargs['jData']['default']  = 0
                        kwargs['jData']['maximum']  = 60000000000
                        kwargs['jData']['varInput'] = f"{jsonVars['From']['description'] }?"
                        kwargs['jData']['varName']  = 'Starting Address'
                        pool_from = ezfunctions.varNumberLoop(**kwargs)
                        #==============================================
                        # Prompt User for IQN Suffix
                        #==============================================
                        kwargs['jData'] = deepcopy(jsonVars['Suffix'])
                        kwargs['jData']['default']  = 'ucs-host'
                        kwargs['jData']['pattern']  = '^[0-9a-zA-Z]{3,32}$'
                        kwargs['jData']['varInput'] = 'What is the IQN Suffix you would like to assign to the Pool?'
                        kwargs['jData']['varName']  = 'IQN Suffix'
                        suffix = ezfunctions.varStringLoop(**kwargs)
                        #==============================================
                        # Prompt User for Pool Size
                        #==============================================
                        jsonVars = jsonData['pool.AbstractBlockType']['allOf'][1]['properties']
                        kwargs['jData'] = deepcopy(jsonVars['Size'])
                        kwargs['jData']['default']  = 1024
                        kwargs['jData']['varInput'] = 'How Many IP Addresses should be added to the Pool?  Range is 1-1024.'
                        kwargs['jData']['varName']  = 'Pool Size'
                        pool_size = ezfunctions.varNumberLoop(**kwargs)
                        #==============================================
                        # Configure Pool Parameters
                        #==============================================
                        pool_to = pool_from + pool_size - 1
                        from_iqn = f"{prefix}:{suffix}{pool_from}"
                        to_iqn = f"{prefix}:{suffix}{pool_to}"
                        valid_starting_iqn = validating.iqn_address('IQN Staring Address', from_iqn)
                        valid_ending_iqn = validating.iqn_address('IQN Ending Address', to_iqn)
                        if valid_starting_iqn == True and valid_ending_iqn == True: valid = True
                    polVars['iqn_blocks'] = [{'from':pool_from, 'size':pool_size, 'suffix':suffix}]
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(textwrap.indent(yaml.dump(polVars, Dumper=MyDumper, default_flow_style=False), ' '*4, predicate=None))
                    print(f'-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
                        if confirm_policy == 'Y' or confirm_policy == '':
                            # Add Policy Variables to immDict
                            kwargs['class_path'] = 'intersight,pools,iqn'
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
    # MAC Pools Module
    #==============================================
    def mac(self, **kwargs):
        baseRepo       = kwargs['args'].dir
        configure_loop = False
        jsonData       = kwargs['jsonData']
        name_prefix    = self.name_prefix
        org            = self.org
        path_sep       = kwargs['path_sep']
        policy_type    = 'MAC Pool'
        yaml_file      = 'pools'
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  MAC Pool Convention Recommendations:')
            print(f'  - Leverage the Cisco UCS OUI of 00:25:B5 for the MAC Pool Prefix.')
            print(f'  - For MAC Pools; create a pool for each Fabric.')
            print(f'  - Pool Size can be between 1 and 1024 addresses.')
            print(f'  - Refer to "UCS Naming Conventions 0.5.ppsx" in the Repository for further guidance.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - {baseRepo}{path_sep}{org}{path_sep}{self.type}{path_sep}{yaml_file}.yaml')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            loop_count = 0
            policy_loop = False
            while policy_loop == False:
                polVars = {}
                if name_prefix == '': name_prefix = 'mac'
                name = ezfunctions.naming_rule_fabric(loop_count, name_prefix, org)
                polVars['name']        = ezfunctions.policy_name(name, policy_type)
                polVars['description'] = ezfunctions.policy_descr(polVars['name'], policy_type)
                kwargs['multi_select'] = False
                jsonVars = jsonData['pool.AbstractPool']['allOf'][1]['properties']
                #==============================================
                #
                # Prompt User for Assignment Order
                #==============================================
                kwargs['jData'] = deepcopy(jsonVars['AssignmentOrder'])
                kwargs['jData']['varType'] = 'Assignment Order'
                polVars['assignment_order'] = ezfunctions.variablesFromAPI(**kwargs)
                #==============================================
                #
                # Prompt User for Starting MAC Address
                #==============================================
                jsonVars = jsonData['macpool.Block']['allOf'][1]['properties']
                kwargs['jData'] = deepcopy(jsonVars['From'])
                if loop_count % 2 == 0: 
                    kwargs['jData']['default'] = '00:25:B5:0A:00:00'
                    kwargs['jData']['varInput'] = 'What is the Starting MAC Address to Assign to the Pool?'
                else:
                    kwargs['jData']['default'] = '00:25:B5:0B:00:00'
                    kwargs['jData']['varInput'] = 'What is the Starting MAC Address to Assign to the Pool?'
                kwargs['jData']['maximum'] = 17
                kwargs['jData']['minimum'] = 17
                kwargs['jData']['pattern'] = '^([0-9a-zA-Z]{2}:){5}[0-9a-zA-Z]{2}$'
                kwargs['jData']['varName'] = 'Starting MAC Address'
                pool_from = ezfunctions.varStringLoop(**kwargs)
                #==============================================
                #
                # Prompt User for Block Size
                #==============================================
                jsonVars = jsonData['pool.AbstractBlockType']['allOf'][1]['properties']
                kwargs['jData'] = deepcopy(jsonVars['Size'])
                kwargs['jData']['default']  = 1024
                kwargs['jData']['varInput'] = 'How Many MAC Addresses should be added to the Pool?  Range is 1-1024.'
                kwargs['jData']['varName']  = 'Block Size'
                pool_size = ezfunctions.varNumberLoop(**kwargs)
                #==============================================
                #
                # Configure Pool Paramemters
                #==============================================
                if re.search('[a-z]', pool_from): pool_from = pool_from.upper()
                beginx = int(pool_from.replace(':', ''), 16)
                add_dec = (beginx + int(pool_size) - 1)
                pool_to = ':'.join(['{}{}'.format(a, b)
                    for a, b in zip(*[iter('{:012x}'.format(add_dec))]*2)])
                pool_to = pool_to.upper()
                polVars['mac_blocks'] = [{'from':pool_from, 'size':pool_size}]
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(textwrap.indent(yaml.dump(polVars, Dumper=MyDumper, default_flow_style=False), ' '*4, predicate=None))
                print(f'-------------------------------------------------------------------------------------------\n')
                valid_confirm = False
                while valid_confirm == False:
                    confirm_policy = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                    if confirm_policy == 'Y' or confirm_policy == '':
                        # Add Policy Variables to immDict
                        kwargs['class_path'] = 'intersight,pools,mac'
                        kwargs = ezfunctions.ez_append(polVars, **kwargs)

                        configure_loop, loop_count, policy_loop = ezfunctions.exit_loop_default_yes(loop_count, policy_type)
                        valid_confirm = True
                    elif confirm_policy == 'N':
                        ezfunctions.message_starting_over(policy_type)
                        valid_confirm = True
                    else: ezfunctions.message_invalid_y_or_n('long')
        # Return kwargs
        return kwargs

    #==============================================
    # Resource Pool Module
    #==============================================
    def resource(self, **kwargs):
        baseRepo       = kwargs['args'].dir
        configure_loop = False
        ezData         = kwargs['ezData']
        name_prefix    = self.name_prefix
        name_suffix    = 'resource'
        org            = self.org
        path_sep       = kwargs['path_sep']
        policy_type    = 'Resource Pool'
        yaml_file      = 'pools'
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  The {policy_type} represents a collection of resources that can be associated to ')
            print(f'  the configuration entities such as server profiles.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - {baseRepo}{path_sep}{org}{path_sep}{self.type}{path_sep}{yaml_file}.yaml')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure a {policy_type}?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                policy_loop = False
                while policy_loop == False:
                    polVars = {}
                    if not name_prefix == '': name = f'{name_prefix}-{name_suffix}'
                    else: name = f'{name_suffix}'
                    polVars['name']        = ezfunctions.policy_name(name, policy_type)
                    polVars['description'] = ezfunctions.policy_descr(polVars['name'], policy_type)

                    # Pull in the Policies from API Documentation
                    kwargs['multi_select'] = False
                    #==============================================
                    # Prompt User for Assignment Order
                    #==============================================
                    kwargs['jData'] = deepcopy(jsonVars['AssignmentOrder'])
                    kwargs['jData']['varType'] = 'Assignment Order'
                    polVars['assignment_order'] = ezfunctions.variablesFromAPI(**kwargs)
                    #==============================================
                    # Prompt User for Serial Number List
                    #==============================================
                    polVars['serial_number_list'] = []
                    valid = False
                    while valid == False:
                        kwargs['jData'] = deepcopy({})
                        kwargs['jData']['description'] = 'A List of Serial Numbers to add to the Resource Pool.'
                        kwargs['jData']['pattern']  = '^[A-Z]{3}[2-3][\\d]([0][1-9]|[1-4][0-9]|[5][1-3])[\\dA-Z]{4}$'
                        kwargs['jData']['minimum']  = 11
                        kwargs['jData']['maximum']  = 11
                        kwargs['jData']['varInput'] = 'Enter the Server Serial Number:'
                        kwargs['jData']['varName']  = 'Serial Number'
                        polVars['serial_number_list'].append(ezfunctions.varStringLoop(**kwargs))
                        kwargs['jData'] = deepcopy({})
                        kwargs['jData']['default']     = True
                        kwargs['jData']['description'] = 'Add Additional Serial Numbers.'
                        kwargs['jData']['varInput']    = f'Do you want to add another Serial Number?'
                        kwargs['jData']['varName']     = 'Additional Serial Numbers'
                        valid = ezfunctions.varBoolLoop(**kwargs)
                    #==============================================
                    # Prompt User for Server Type
                    #==============================================
                    jsonVars = ezData['pools']['resourcepool.Pool']
                    kwargs['jData'] = deepcopy(jsonVars['server_type'])
                    kwargs['jData']['description'] = jsonVars['server_type']['description']
                    kwargs['jData']['jsonVars'] = sorted(jsonVars['server_type']['enum'])
                    kwargs['jData']['defaultVar'] = jsonVars['server_type']['default']
                    kwargs['jData']['varType'] = 'Server Type'
                    polVars['server_type'] = ezfunctions.variablesFromAPI(**kwargs)
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(textwrap.indent(yaml.dump(polVars, Dumper=MyDumper, default_flow_style=False), ' '*4, predicate=None))
                    print(f'-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                        if confirm_policy == 'Y' or confirm_policy == '':
                            # Add Policy Variables to immDict
                            kwargs['class_path'] = 'intersight,pools,resource'
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
    # UUID Pools Module
    #==============================================
    def uuid(self, **kwargs):
        baseRepo       = kwargs['args'].dir
        configure_loop = False
        jsonData       = kwargs['jsonData']
        name_prefix    = self.name_prefix
        name_suffix    = 'uuid'
        org            = self.org
        path_sep       = kwargs['path_sep']
        policy_type    = 'UUID Pool'
        yaml_file      = 'pools'
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  The Universally Unique Identifier (UUID) are written in 5 groups of hexadecimal digits')
            print(f'  separated by hyphens.  The length of each group is: 8-4-4-4-12. UUIDs are fixed length.')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure a {policy_type}.  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                policy_loop = False
                while policy_loop == False:
                    polVars = {}
                    if not name_prefix == '': name = f'{name_prefix}-{name_suffix}'
                    else: name = f'{name_suffix}'
                    polVars['name']        = ezfunctions.policy_name(name, policy_type)
                    polVars['description'] = ezfunctions.policy_descr(polVars['name'], policy_type)
                    kwargs['multi_select'] = False
                    jsonVars = jsonData['pool.AbstractPool']['allOf'][1]['properties']
                    #==============================================
                    # Prompt User for Assignment Order
                    #==============================================
                    kwargs['jData'] = deepcopy(jsonVars['AssignmentOrder'])
                    kwargs['jData']['varType'] = 'Assignment Order'
                    polVars['assignment_order'] = ezfunctions.variablesFromAPI(**kwargs)
                    #==============================================
                    # Prompt User for UUID Prefix
                    #==============================================
                    jsonVars = jsonData['uuidpool.Pool']['allOf'][1]['properties']
                    kwargs['jData'] = deepcopy(jsonVars['Prefix'])
                    kwargs['jData']['default']  = '000025B5-0000-0000'
                    kwargs['jData']['maximum']  = 18
                    kwargs['jData']['minimum']  = 18
                    kwargs['jData']['varInput'] = 'What is the UUID Prefix you would like to assign to the Pool?'
                    kwargs['jData']['varName']  = 'UUID Prefix'
                    polVars['prefix'] = ezfunctions.varStringLoop(**kwargs)
                    #==============================================
                    # Prompt User for UUID First Suffix
                    #==============================================
                    jsonVars = jsonData['uuidpool.UuidBlock']['allOf'][1]['properties']
                    kwargs['jData'] = deepcopy(jsonVars['From'])
                    kwargs['jData']['default']  = '0000-000000000000'
                    kwargs['jData']['varInput'] = 'What is the First UUID Suffix in the Block?'
                    kwargs['jData']['varName']  = 'UUID First Suffix'
                    pool_from = ezfunctions.varStringLoop(**kwargs)
                    #==============================================
                    # Prompt User for Pool Size
                    #==============================================
                    jsonVars = jsonData['pool.AbstractBlockType']['allOf'][1]['properties']
                    kwargs['jData'] = deepcopy(jsonVars['Size'])
                    kwargs['jData']['default']  = 1024
                    kwargs['jData']['varInput'] = 'How Many IP Addresses should be added to the Pool?  Range is 1-1024.'
                    kwargs['jData']['varName']  = 'Pool Size'
                    pool_size = ezfunctions.varNumberLoop(**kwargs)
                    #==============================================
                    # Configure UUID Pool Parameters
                    #==============================================
                    if re.search('[a-z]', pool_from):
                        pool_from = pool_from.upper()
                    from_split = pool_from.split('-')
                    pool_to = hex(int(from_split[1], 16) + pool_size - 1).split('x')[-1]
                    add_zeros = 12 - len(pool_to)
                    if not add_zeros == 0:
                        pool_to = str(from_split[0]) + '-' + ('0' * add_zeros) + pool_to
                    pool_to = pool_to.upper()
                    polVars['uuid_blocks'] = [{'from':pool_from, 'size':pool_size}]
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(textwrap.indent(yaml.dump(polVars, Dumper=MyDumper, default_flow_style=False), ' '*4, predicate=None))
                    print(f'-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
                        if confirm_policy == 'Y' or confirm_policy == '':
                            # Add Policy Variables to immDict
                            kwargs['class_path'] = 'intersight,pools,uuid'
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
    # WWNN Pools Module
    #==============================================
    def wwnn(self, **kwargs):
        baseRepo       = kwargs['args'].dir
        configure_loop = False
        jsonData       = kwargs['jsonData']
        name_prefix    = self.name_prefix
        name_suffix    = 'wwnn'
        org            = self.org
        path_sep       = kwargs['path_sep']
        policy_type    = 'WWNN Pool'
        yaml_file      = 'pools'
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  WWNN Pool Convention Recommendations:')
            print(f'  - Leverage the Cisco UCS OUI of 20:00:00:25:B5 for the WWNN Pool Prefix.')
            print(f'  - Pool Size can be between 1 and 1024 addresses.')
            print(f'  - Refer to "UCS Naming Conventions 0.5.ppsx" in the Repository for further guidance.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - {baseRepo}{path_sep}{org}{path_sep}{self.type}{path_sep}{yaml_file}.yaml')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure a {policy_type}?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                policy_loop = False
                while policy_loop == False:
                    polVars = {}
                    if not name_prefix == '': name = f'{name_prefix}-{name_suffix}'
                    else: name = f'{name_suffix}'
                    polVars['name']        = ezfunctions.policy_name(name, policy_type)
                    polVars['description'] = ezfunctions.policy_descr(polVars['name'], policy_type)
                    kwargs['multi_select'] = False
                    jsonVars = jsonData['pool.AbstractPool']['allOf'][1]['properties']
                    #==============================================
                    # Prompt User for Assignment Order
                    #==============================================
                    kwargs['jData'] = deepcopy(jsonVars['AssignmentOrder'])
                    kwargs['jData']['varType'] = 'Assignment Order'
                    polVars['assignment_order'] = ezfunctions.variablesFromAPI(**kwargs)
                    #==============================================
                    # Prompt User for Starting Address
                    #==============================================
                    jsonVars = jsonData['fcpool.Block']['allOf'][1]['properties']
                    kwargs['jData'] = deepcopy(jsonVars['From'])
                    kwargs['jData']['default']  = '20:00:00:25:B5:00:00:00'
                    kwargs['jData']['varInput'] = 'What is the Starting WWNN Address to Assign to the Pool?'
                    kwargs['jData']['varName']  = 'Starting WWNN Address'
                    pool_from = ezfunctions.varStringLoop(**kwargs)
                    #==============================================
                    # Prompt User for Block Size
                    #==============================================
                    jsonVars = jsonData['pool.AbstractBlockType']['allOf'][1]['properties']
                    kwargs['jData'] = deepcopy(jsonVars['Size'])
                    kwargs['jData']['default']  = 1024
                    kwargs['jData']['varInput'] = 'How Many WWNN Addresses should be added to the Pool?  Range is 1-1024.'
                    kwargs['jData']['varName']  = 'Pool Size'
                    pool_size = ezfunctions.varNumberLoop(**kwargs)
                    #==============================================
                    # Configure Pool Parameters
                    #==============================================
                    if re.search('[a-z]', pool_from): pool_from = pool_from.upper()
                    beginx = int(pool_from.replace(':', ''), 16)
                    add_dec = (beginx + int(pool_size) - 1)
                    pool_to = ':'.join(['{}{}'.format(a, b)
                    for a, b in zip(*[iter('{:012x}'.format(add_dec))]*2)])
                    pool_to = pool_to.upper()
                    polVars['id_blocks'] = [{'from':pool_from, 'size':pool_size}]
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(textwrap.indent(yaml.dump(polVars, Dumper=MyDumper, default_flow_style=False), ' '*4, predicate=None))
                    print(f'-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                        if confirm_policy == 'Y' or confirm_policy == '':
                            # Add Policy Variables to immDict
                            kwargs['class_path'] = 'intersight,pools,wwnn'
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
    # WWPN Pools Module
    #==============================================
    def wwpn(self, **kwargs):
        baseRepo       = kwargs['args'].dir
        configure_loop = False
        jsonData       = kwargs['jsonData']
        name_prefix    = self.name_prefix
        org            = self.org
        path_sep       = kwargs['path_sep']
        policy_type    = 'WWPN Pool'
        yaml_file      = 'pools'
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  WWPN Pool Convention Recommendations:')
            print(f'  - Leverage the Cisco UCS OUI of 20:00:00:25:B5 for the WWPN Pool Prefix.')
            print(f'  - For WWPN Pools; create a pool for each Fabric.')
            print(f'  - Pool Size can be between 1 and 1024 addresses.')
            print(f'  - Refer to "UCS Naming Conventions 0.5.ppsx" in the Repository for further guidance.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - {baseRepo}{path_sep}{org}{path_sep}{self.type}{path_sep}{yaml_file}.yaml')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure a {policy_type}?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                loop_count = 0
                policy_loop = False
                while policy_loop == False:
                    polVars = {}
                    if name_prefix == '': name_prefix = 'wwpn'
                    name = ezfunctions.naming_rule_fabric(loop_count, name_prefix, org)
                    polVars['name']        = ezfunctions.policy_name(name, policy_type)
                    polVars['description'] = ezfunctions.policy_descr(polVars['name'], policy_type)
                    kwargs['multi_select'] = False
                    jsonVars = jsonData['pool.AbstractPool']['allOf'][1]['properties']
                    #==============================================
                    # Prompt User for Assignment Order
                    #==============================================
                    kwargs['jData'] = deepcopy(jsonVars['AssignmentOrder'])
                    kwargs['jData']['varType'] = 'Assignment Order'
                    polVars['assignment_order'] = ezfunctions.variablesFromAPI(**kwargs)
                    jsonVars = jsonData['fcpool.Block']['allOf'][1]['properties']
                    #==============================================
                    # Prompt User for Starting Address
                    #==============================================
                    kwargs['jData'] = deepcopy(jsonVars['From'])
                    if loop_count % 2 == 0: 
                        kwargs['jData']['default'] = '20:00:00:25:B5:0A:00:00'
                        kwargs['jData']['varInput'] = 'What is the Starting WWPN Address to Assign to the Pool?'
                    else:
                        kwargs['jData']['default'] = '20:00:00:25:B5:0B:00:00'
                        kwargs['jData']['varInput'] = 'What is the Starting WWPN Address to Assign to the Pool?'
                    kwargs['jData']['varName'] = 'Starting WWPN Address'
                    pool_from = ezfunctions.varStringLoop(**kwargs)
                    #==============================================
                    # Prompt User for Block Size
                    #==============================================
                    jsonVars = jsonData['pool.AbstractBlockType']['allOf'][1]['properties']
                    kwargs['jData'] = deepcopy(jsonVars['Size'])
                    kwargs['jData']['default']  = 1024
                    kwargs['jData']['varInput'] = 'How Many WWPN Addresses should be added to the Pool?  Range is 1-1024.'
                    kwargs['jData']['varName']  = 'Pool Size'
                    pool_size = ezfunctions.varNumberLoop(**kwargs)
                    #==============================================
                    # Configure Pool Parameters
                    #==============================================
                    if re.search('[a-z]', pool_from): pool_from = pool_from.upper()
                    beginx = int(pool_from.replace(':', ''), 16)
                    add_dec = (beginx + int(pool_size) - 1)
                    pool_to = ':'.join(['{}{}'.format(a, b)
                    for a, b in zip(*[iter('{:012x}'.format(add_dec))]*2)])
                    pool_to = pool_to.upper()
                    polVars['id_blocks'] = [{'from':pool_from, 'size':pool_size}]
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(textwrap.indent(yaml.dump(polVars, Dumper=MyDumper, default_flow_style=False), ' '*4, predicate=None))
                    print(f'-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                        if confirm_policy == 'Y' or confirm_policy == '':
                            # Add Policy Variables to immDict
                            kwargs['class_path'] = 'intersight,pools,wwpn'
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
