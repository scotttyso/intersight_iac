#!/usr/bin/env python3
import ezfunctions
import ipaddress
import jinja2
import pkg_resources
import re
import validating

ucs_template_path = pkg_resources.resource_filename('pools', '../templates/')

class pools(object):
    def __init__(self, name_prefix, org, type):
        self.templateLoader = jinja2.FileSystemLoader(
            searchpath=(ucs_template_path + '%s/') % (type))
        self.templateEnv = jinja2.Environment(loader=self.templateLoader)
        self.name_prefix = name_prefix
        self.org = org
        self.type = type

    #==============================================
    # IP Pools Module
    #==============================================
    def ip_pools(self, jsonData, easy_jsonData, **kwargs):
        name_prefix = self.name_prefix
        name_suffix = 'ip_pool'
        opSystem = kwargs['opSystem']
        org = self.org
        policy_type = 'IP Pool'
        polVars = {}
        polVars["header"] = '%s Variables' % (policy_type)
        polVars["initial_write"] = True
        polVars["org"] = org
        polVars["policy_type"] = policy_type
        polVars["template_file"] = 'template_open.jinja2'
        polVars["template_type"] = 'ip_pools'
        tfDir = kwargs['tfDir']

        # Open the Template file
        ezfunctions.write_to_template(self, **polVars)
        polVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  At a minimum you will need one IP Pool for KVM Access to Servers.  Currently out-of-band')
            print(f'  management is not supported for KVM access.  This IP Pool will need to be associated to a ')
            print(f'  VLAN assigned to the VLAN Pool of the Domain.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            if opSystem == 'Windows':
                print(f'  - {tfDir}\\{org}\\{self.type}\\{polVars["template_type"]}.auto.tfvars')
            else:
                print(f'  - {tfDir}/{org}/{self.type}/{polVars["template_type"]}.auto.tfvars')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure an {policy_type}?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                policy_loop = False
                while policy_loop == False:

                    if not name_prefix == '':
                        name = '%s_%s' % (name_prefix, name_suffix)
                    else:
                        name = '%s_%s' % (org, name_suffix)

                    polVars["name"] = ezfunctions.policy_name(name, policy_type)
                    polVars["descr"] = ezfunctions.policy_descr(polVars["name"], policy_type)

                    polVars["multi_select"] = False
                    jsonVars = jsonData['components']['schemas']['pool.AbstractPool']['allOf'][1]['properties']

                    polVars["var_description"] = jsonVars['AssignmentOrder']['description']
                    polVars["jsonVars"] = sorted(jsonVars['AssignmentOrder']['enum'])
                    polVars["defaultVar"] = jsonVars['AssignmentOrder']['default']
                    polVars["varType"] = 'Assignment Order'
                    polVars["assignment_order"] = ezfunctions.variablesFromAPI(**polVars)

                    valid = False
                    while valid == False:
                        config_ipv4 = input('Do you want to configure IPv4 for this Pool?  Enter "Y" or "N" [Y]: ')
                        if config_ipv4 == 'Y' or config_ipv4 == '':
                            valid = True
                        elif config_ipv4 == 'N':
                            valid = True
                        else:
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                            print(f'\n-------------------------------------------------------------------------------------------\n')

                    if config_ipv4 == 'Y' or config_ipv4 == '':
                        jsonVars = jsonData['components']['schemas']['ippool.IpV4Block']['allOf'][1]['properties']

                        polVars["Description"] = 'The Gateway/Prefix to Assign to the Pool'
                        polVars["varDefault"] = '198.18.0.1/24'
                        polVars["varInput"] = 'What is the Gateway/Prefix to Assign to the Pool?  [198.18.0.1/24]:'
                        polVars["varName"] = 'Gateway/Prefix'
                        polVars["varRegex"] = '^([1-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\\.{3}([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\/[0-9]{1,2}$'
                        polVars["minLength"] = 7
                        polVars["maxLength"] = 20
                        network_prefix = ezfunctions.varStringLoop(**polVars)

                        gateway = str(ipaddress.IPv4Interface(network_prefix).ip)
                        netmask = str(ipaddress.IPv4Interface(network_prefix).netmask)
                        network = str(ipaddress.IPv4Interface(network_prefix).network)
                        prefix = network_prefix.split('/')[1]

                        polVars["Description"] = jsonVars['From']['description']
                        polVars["varDefault"] = '198.18.0.2'
                        polVars["varInput"] = 'What is the Starting IP Address to Assign to the Pool?  [198.18.0.2]:'
                        polVars["varName"] = 'Starting IP Address'
                        polVars["varRegex"] = jsonVars['From']['pattern']
                        polVars["minLength"] = 7
                        polVars["maxLength"] = 15
                        pool_from = ezfunctions.varStringLoop(**polVars)

                        jsonVars = jsonData['components']['schemas']['pool.AbstractBlockType']['allOf'][1]['properties']

                        polVars["Description"] = jsonVars['Size']['description']
                        polVars["varInput"] = 'How Many IP Addresses should be added to the Pool?  Range is 1-1000.'
                        polVars["varDefault"] = 253
                        polVars["varName"] = 'Pool Size'
                        polVars["minNum"] = jsonVars['Size']['minimum']
                        polVars["maxNum"] = jsonVars['Size']['maximum']
                        pool_size = ezfunctions.varNumberLoop(**polVars)

                        jsonVars = jsonData['components']['schemas']['ippool.IpV4Config']['allOf'][1]['properties']

                        polVars["Description"] = jsonVars['PrimaryDns']['description']
                        polVars["varDefault"] = '208.67.220.220'
                        polVars["varInput"] = 'What is your Primary DNS Server?  [208.67.220.220]:'
                        polVars["varName"] = 'Primary Dns'
                        polVars["varRegex"] = jsonVars['PrimaryDns']['pattern']
                        polVars["minLength"] = 7
                        polVars["maxLength"] = 15
                        primary_dns = ezfunctions.varStringLoop(**polVars)

                        polVars["Description"] = jsonVars['SecondaryDns']['description']
                        polVars["varDefault"] = ''
                        polVars["varInput"] = 'What is your Secondary DNS Server?  [press enter to skip]:'
                        polVars["varName"] = 'Secondary Dns'
                        polVars["varRegex"] = jsonVars['SecondaryDns']['pattern']
                        polVars["minLength"] = 7
                        polVars["maxLength"] = 15
                        secondary_dns = ezfunctions.varStringLoop(**polVars)

                        beginx = int(ipaddress.IPv4Address(pool_from))
                        add_dec = (beginx + int(pool_size) - 1)
                        pool_to = str(ipaddress.IPv4Address(add_dec))

                        polVars["ipv4_blocks"] = [
                            {
                                'from':pool_from,
                                'size':pool_size,
                                'to':pool_to
                            }
                        ]
                        polVars["ipv4_configuration"] = {
                            'gateway':gateway,
                            'netmask':netmask,
                            'primary_dns':primary_dns,
                            'secondary_dns':secondary_dns
                        }

                    valid = False
                    while valid == False:
                        config_ipv6 = input('Do you want to configure IPv6 for this Pool?  Enter "Y" or "N" [N]: ')
                        if config_ipv6 == 'Y':
                            valid = True
                        elif config_ipv6 == 'N' or config_ipv6 == '':
                            valid = True
                        else:
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                            print(f'\n-------------------------------------------------------------------------------------------\n')

                    if config_ipv6 == 'Y':
                        jsonVars = jsonData['components']['schemas']['ippool.IpV6Block']['allOf'][1]['properties']

                        polVars["Description"] = 'The Gateway/Prefix to Assign to the Pool'
                        polVars["varDefault"] = '2001:0002::1/64'
                        polVars["varInput"] = 'What is the Gateway/Prefix to Assign to the Pool?  [2001:0002::1/64]:'
                        polVars["varName"] = 'Gateway/Prefix'
                        polVars["varRegex"] = '^$|^(([0-9A-Fa-f]{1,4}:([0-9A-Fa-f]{1,4}:([0-9A-Fa-f]{1,4}:([0-9A-Fa-f]{1,4}:([0-9A-Fa-f]{1,4}:[0-9A-Fa-f]{0,4}|:[0-9A-Fa-f]{1,4})?|(:[0-9A-Fa-f]{1,4}){0,2})|(:[0-9A-Fa-f]{1,4}){0,3})|(:[0-9A-Fa-f]{1,4}){0,4})|:(:[0-9A-Fa-f]{1,4}){0,5})((:[0-9A-Fa-f]{1,4}){2}|:(25[0-5]|(2[0-4]|1[0-9]|[1-9])?[0-9])(\\.(25[0-5]|(2[0-4]|1[0-9]|[1-9])?[0-9])){3})|(([0-9A-Fa-f]{1,4}:){1,6}|:):[0-9A-Fa-f]{0,4}|([0-9A-Fa-f]{1,4}:){7}:)\/[0-9]{1,3}$'
                        polVars["minLength"] = 6
                        polVars["maxLength"] = 164
                        network_prefix = ezfunctions.varStringLoop(**polVars)

                        # broadcast = str(ipaddress.IPv4Interface(network_prefix).broadcast_address)
                        gateway = str(ipaddress.IPv6Interface(network_prefix).ip)
                        if re.search('[a-z]+', gateway):
                            gateway = gateway.upper()
                        network = str(ipaddress.IPv6Interface(network_prefix).network)
                        prefix = network_prefix.split('/')[1]

                        polVars["Description"] = jsonVars['From']['description']
                        polVars["varDefault"] = '2001:0002::2'
                        polVars["varInput"] = 'What is the Starting IP Address to Assign to the Pool?  [2001:0002::2]:'
                        polVars["varName"] = 'Starting IPv6 Address'
                        polVars["varRegex"] = jsonVars['From']['pattern']
                        polVars["minLength"] = 3
                        polVars["maxLength"] = 164
                        starting = ezfunctions.varStringLoop(**polVars)

                        jsonVars = jsonData['components']['schemas']['pool.AbstractBlockType']['allOf'][1]['properties']

                        polVars["Description"] = jsonVars['Size']['description']
                        polVars["varInput"] = 'How Many IPv6 Addresses should be added to the Pool?  Range is 1-1000.'
                        polVars["varDefault"] = 1000
                        polVars["varName"] = 'Pool Size'
                        polVars["minNum"] = jsonVars['Size']['minimum']
                        polVars["maxNum"] = jsonVars['Size']['maximum']
                        pool_size = ezfunctions.varNumberLoop(**polVars)

                        jsonVars = jsonData['components']['schemas']['ippool.IpV6Config']['allOf'][1]['properties']

                        polVars["Description"] = jsonVars['PrimaryDns']['description']
                        polVars["varDefault"] = '2620:119:53::53'
                        polVars["varInput"] = 'What is your Primary DNS Server?  [2620:119:53::53]:'
                        polVars["varName"] = 'Primary Dns'
                        polVars["varRegex"] = jsonVars['PrimaryDns']['pattern']
                        polVars["minLength"] = 3
                        polVars["maxLength"] = 164
                        primary_dns = ezfunctions.varStringLoop(**polVars)

                        polVars["Description"] = jsonVars['SecondaryDns']['description']
                        polVars["varDefault"] = ''
                        polVars["varInput"] = 'What is your Secondary DNS Server?  [press enter to skip]:'
                        polVars["varName"] = 'Secondary Dns'
                        polVars["varRegex"] = jsonVars['SecondaryDns']['pattern']
                        polVars["minLength"] = 3
                        polVars["maxLength"] = 164
                        secondary_dns = ezfunctions.varStringLoop(**polVars)

                        beginx = int(ipaddress.IPv6Address(starting))
                        add_dec = (beginx + int(pool_size) - 1)
                        ending = str(ipaddress.IPv6Address(add_dec))

                        polVars["ipv6_blocks"] = [
                            {
                                'from':starting,
                                'size':pool_size,
                                'to':ending
                            }
                        ]
                        polVars["ipv6_configuration"] = {
                            'gateway':gateway,
                            'prefix':prefix,
                            'primary_dns':primary_dns,
                            'secondary_dns':secondary_dns
                        }

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'    assignment_order = "{polVars["assignment_order"]}"')
                    print(f'    description      = "{polVars["descr"]}"')
                    print(f'    name             = "{polVars["name"]}"')
                    if config_ipv4 == 'Y' or config_ipv4 == '':
                        print(f'    ipv4_blocks = ''[')
                        for item in polVars["ipv4_blocks"]:
                            print('      {')
                            for k, v in item.items():
                                if k == 'from':
                                    print(f'        from = "{v}" ')
                                elif k == 'size':
                                    print(f'        size = {v}')
                                elif k == 'to':
                                    print(f'        to   = "{v}"')
                            print('      }')
                        print(f'    '']')
                        print('    ipv4_configuration = {')
                        print('      [')
                        for k, v in polVars["ipv4_configuration"].items():
                            if k == 'gateway':
                                print(f'        gateway       = "{v}"')
                            elif k == 'netmask':
                                print(f'        netmask       = "{v}"')
                            elif k == 'primary_dns':
                                print(f'        primary_dns   = "{v}"')
                            elif k == 'secondary_dns':
                                print(f'        secondary_dns = "{v}"')
                        print('      }')
                        print('    ]')
                    if config_ipv6 == 'Y':
                        print(f'    ipv6_blocks = ''{')
                        for item in polVars["ipv6_blocks"]:
                            print('      [')
                            for k, v in item.items():
                                if k == 'from':
                                    print(f'        from = "{v}"')
                                elif k == 'size':
                                    print(f'        size = {v}')
                                elif k == 'to':
                                    print(f'        to   = "{v}"')
                            print('      }')
                        print(f'    '']')
                        print('    ipv6_configuration = [')
                        print('      {')
                        for k, v in polVars["ipv6_configuration"].items():
                            if k == 'gateway':
                                print(f'        gateway       = "{v}"')
                            elif k == 'prefix':
                                print(f'        prefix        = "{v}"')
                            elif k == 'primary_dns':
                                print(f'        primary_dns   = "{v}"')
                            elif k == 'secondary_dns':
                                print(f'        secondary_dns = "{v}"')
                        print('      }')
                        print('    ]')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                        if confirm_policy == 'Y' or confirm_policy == '':
                            confirm_policy = 'Y'

                            # Write Policies to Template File
                            polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                            ezfunctions.write_to_template(self, **polVars)

                            configure_loop, policy_loop = ezfunctions.exit_default_no(polVars["policy_type"])
                            valid_confirm = True

                        elif confirm_policy == 'N':
                            print(f'\n------------------------------------------------------\n')
                            print(f'  Starting {polVars["policy_type"]} Section over.')
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
        polVars["template_file"] = 'template_close.jinja2'
        ezfunctions.write_to_template(self, **polVars)

    #==============================================
    # IQN Pools Module
    #==============================================
    def iqn_pools(self, jsonData, easy_jsonData, **kwargs):
        name_prefix = self.name_prefix
        name_suffix = 'iqn_pool'
        opSystem = kwargs['opSystem']
        org = self.org
        policy_type = 'IQN Pool'
        polVars = {}
        polVars["header"] = '%s Variables' % (policy_type)
        polVars["initial_write"] = True
        polVars["org"] = org
        polVars["policy_type"] = policy_type
        polVars["template_file"] = 'template_open.jinja2'
        polVars["template_type"] = 'iqn_pools'
        tfDir = kwargs['tfDir']

        # Open the Template file
        ezfunctions.write_to_template(self, **polVars)
        polVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure a {policy_type}.  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                policy_loop = False
                while policy_loop == False:

                    if not name_prefix == '':
                        name = '%s_%s' % (name_prefix, name_suffix)
                    else:
                        name = '%s_%s' % (org, name_suffix)

                    polVars["name"] = ezfunctions.policy_name(name, policy_type)
                    polVars["descr"] = ezfunctions.policy_descr(polVars["name"], policy_type)

                    polVars["multi_select"] = False
                    jsonVars = jsonData['components']['schemas']['pool.AbstractPool']['allOf'][1]['properties']

                    polVars["var_description"] = jsonVars['AssignmentOrder']['description']
                    polVars["jsonVars"] = sorted(jsonVars['AssignmentOrder']['enum'])
                    polVars["defaultVar"] = jsonVars['AssignmentOrder']['default']
                    polVars["varType"] = 'Assignment Order'
                    polVars["assignment_order"] = ezfunctions.variablesFromAPI(**polVars)

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
                        jsonVars = jsonData['components']['schemas']['iqnpool.Pool']['allOf'][1]['properties']

                        polVars["Description"] = jsonVars['Prefix']['description']
                        polVars["varDefault"] = 'iqn.1984-12.com.cisco'
                        polVars["varInput"] = 'What is the IQN Prefix you would like to assign to the Pool?  [iqn.1984-12.com.cisco]:'
                        polVars["varName"] = 'IQN Prefix'
                        polVars["varRegex"] = '^$|^(?:iqn\\.[0-9]{4}-[0-9]{2}(?:\\.[A-Za-z](?:[A-Za-z0-9\\-]*[A-Za-z0-9])?)+?'
                        polVars["minLength"] = 7
                        polVars["maxLength"] = 64
                        polVars["prefix"] = ezfunctions.varStringLoop(**polVars)

                        jsonVars = jsonData['components']['schemas']['iqnpool.IqnSuffixBlock']['allOf'][1]['properties']

                        polVars["Description"] = jsonVars['From']['description']
                        polVars["varInput"] = jsonVars['From']['description'] 
                        polVars["varDefault"] = 0
                        polVars["varName"] = 'Starting Suffix'
                        polVars["minNum"] = 0
                        polVars["maxNum"] = 60000000000
                        pool_from = ezfunctions.varNumberLoop(**polVars)

                        polVars["Description"] = jsonVars['Suffix']['description']
                        polVars["varDefault"] = 'ucs-host'
                        polVars["varInput"] = 'What is the IQN Suffix you would like to assign to the Pool?  [ucs-host]:'
                        polVars["varName"] = 'IQN Suffix'
                        polVars["varRegex"] = '[0-9a-zA-Z]'
                        polVars["minLength"] = 3
                        polVars["maxLength"] = 32
                        suffix = ezfunctions.varStringLoop(**polVars)

                        jsonVars = jsonData['components']['schemas']['pool.AbstractBlockType']['allOf'][1]['properties']

                        polVars["Description"] = jsonVars['Size']['description']
                        polVars["varInput"] = 'How Many IP Addresses should be added to the Pool?  Range is 1-1000.'
                        polVars["varDefault"] = 1000
                        polVars["varName"] = 'Pool Size'
                        polVars["minNum"] = jsonVars['Size']['minimum']
                        polVars["maxNum"] = jsonVars['Size']['maximum']
                        pool_size = ezfunctions.varNumberLoop(**polVars)

                        pool_to = pool_from + pool_size - 1
                        from_iqn = '%s:%s%s' % (polVars['prefix'], suffix, pool_from)
                        to_iqn = '%s:%s%s' % (polVars['prefix'], suffix, pool_to)
                        valid_starting_iqn = validating.iqn_address('IQN Staring Address', from_iqn)
                        valid_ending_iqn = validating.iqn_address('IQN Ending Address', to_iqn)
                        if valid_starting_iqn == True and valid_ending_iqn == True:
                            valid = True


                    polVars["iqn_blocks"] = [
                        {
                            'from':pool_from,
                            'size':pool_size,
                            'suffix':suffix,
                            'to':pool_to
                        }
                    ]
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'    assignment_order = "{polVars["assignment_order"]}"')
                    print(f'    description      = "{polVars["descr"]}"')
                    print(f'    name             = "{polVars["name"]}"')
                    print(f'    prefix           = "{polVars["prefix"]}"')
                    print(f'    iqn_blocks = ''[')
                    for i in polVars["iqn_blocks"]:
                        print(f'      ''{')
                        for k, v in i.items():
                            if k == 'from':
                                print(f'        from   = {v}')
                            elif k == 'size':
                                print(f'        size   = {v}')
                            elif k == 'suffix':
                                print(f'        suffix = "{v}"')
                            elif k == 'to':
                                print(f'        to     = {v}')
                        print(f'      ''}')
                    print(f'    '']')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
                        if confirm_policy == 'Y' or confirm_policy == '':
                            confirm_policy = 'Y'

                            # Write Policies to Template File
                            polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                            ezfunctions.write_to_template(self, **polVars)

                            configure_loop, policy_loop = ezfunctions.exit_default_no(polVars["policy_type"])
                            valid_confirm = True

                        elif confirm_policy == 'N':
                            print(f'\n------------------------------------------------------\n')
                            print(f'  Starting {polVars["policy_type"]} Section over.')
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
        polVars["template_file"] = 'template_close.jinja2'
        ezfunctions.write_to_template(self, **polVars)

    #==============================================
    # MAC Pools Module
    #==============================================
    def mac_pools(self, jsonData, easy_jsonData, **kwargs):
        name_prefix = self.name_prefix
        opSystem = kwargs['opSystem']
        org = self.org
        policy_type = 'MAC Pool'
        polVars = {}
        polVars["header"] = '%s Variables' % (policy_type)
        polVars["initial_write"] = True
        polVars["org"] = org
        polVars["policy_type"] = policy_type
        polVars["template_file"] = 'template_open.jinja2'
        polVars["template_type"] = 'mac_pools'
        tfDir = kwargs['tfDir']

        # Open the Template file
        ezfunctions.write_to_template(self, **polVars)
        polVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  MAC Pool Convention Recommendations:')
            print(f'  - Leverage the Cisco UCS OUI of 00:25:B5 for the MAC Pool Prefix.')
            print(f'  - For MAC Pools; create a pool for each Fabric.')
            print(f'  - Pool Size can be between 1 and 1000 addresses.')
            print(f'  - Refer to "UCS Naming Conventions 0.5.ppsx" in the Repository for further guidance.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            if opSystem == 'Windows':
                print(f'  - {tfDir}\\{org}\\{self.type}\\{polVars["template_type"]}.auto.tfvars')
            else:
                print(f'  - {tfDir}/{org}/{self.type}/{polVars["template_type"]}.auto.tfvars')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            loop_count = 0
            policy_loop = False
            while policy_loop == False:

                name = ezfunctions.naming_rule_fabric(loop_count, name_prefix, org)

                polVars["name"] = ezfunctions.policy_name(name, policy_type)
                polVars["descr"] = ezfunctions.policy_descr(polVars["name"], policy_type)

                polVars["multi_select"] = False
                jsonVars = jsonData['components']['schemas']['pool.AbstractPool']['allOf'][1]['properties']

                polVars["var_description"] = jsonVars['AssignmentOrder']['description']
                polVars["jsonVars"] = sorted(jsonVars['AssignmentOrder']['enum'])
                polVars["defaultVar"] = jsonVars['AssignmentOrder']['default']
                polVars["varType"] = 'Assignment Order'
                polVars["assignment_order"] = ezfunctions.variablesFromAPI(**polVars)

                jsonVars = jsonData['components']['schemas']['macpool.Block']['allOf'][1]['properties']

                polVars["Description"] = jsonVars['From']['description']
                if loop_count % 2 == 0: 
                    polVars["varDefault"] = '00:25:B5:0A:00:00'
                    polVars["varInput"] = 'What is the Starting MAC Address to Assign to the Pool?  [00:25:B5:0A:00:00]:'
                else:
                    polVars["varDefault"] = '00:25:B5:0B:00:00'
                    polVars["varInput"] = 'What is the Starting MAC Address to Assign to the Pool?  [00:25:B5:0B:00:00]:'
                polVars["varName"] = 'Starting MAC Address'
                polVars["varRegex"] = '^([0-9a-zA-Z]{2}:){5}[0-9a-zA-Z]{2}$'
                polVars["minLength"] = 17
                polVars["maxLength"] = 17
                pool_from = ezfunctions.varStringLoop(**polVars)

                jsonVars = jsonData['components']['schemas']['pool.AbstractBlockType']['allOf'][1]['properties']

                polVars["Description"] = jsonVars['Size']['description']
                polVars["varInput"] = 'How Many IP Addresses should be added to the Pool?  Range is 1-1000.'
                polVars["varDefault"] = 1000
                polVars["varName"] = 'Pool Size'
                polVars["minNum"] = jsonVars['Size']['minimum']
                polVars["maxNum"] = jsonVars['Size']['maximum']
                pool_size = ezfunctions.varNumberLoop(**polVars)

                if re.search('[a-z]', pool_from):
                    pool_from = pool_from.upper()
                beginx = int(pool_from.replace(':', ''), 16)
                add_dec = (beginx + int(pool_size) - 1)
                pool_to = ':'.join(['{}{}'.format(a, b)
                    for a, b
                    in zip(*[iter('{:012x}'.format(add_dec))]*2)])
                pool_to = pool_to.upper()
                polVars["mac_blocks"] = [
                    {
                        'from':pool_from,
                        'size':pool_size,
                        'to':pool_to
                    }
                ]

                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'    assignment_order = "{polVars["assignment_order"]}"')
                print(f'    description      = "{polVars["descr"]}"')
                print(f'    name             = "{polVars["name"]}"')
                print(f'    mac_blocks = ''[')
                for item in polVars["mac_blocks"]:
                    print('      {')
                    for k, v in item.items():
                        if k == 'from':
                            print(f'        from = "{v}" ')
                        elif k == 'size':
                            print(f'        size = {v}')
                        elif k == 'to':
                            print(f'        to   = "{v}"')
                    print('      }')
                print(f'    '']')
                print(f'\n-------------------------------------------------------------------------------------------\n')
                valid_confirm = False
                while valid_confirm == False:
                    confirm_policy = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                    if confirm_policy == 'Y' or confirm_policy == '':
                        confirm_policy = 'Y'

                        # Write Policies to Template File
                        polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                        ezfunctions.write_to_template(self, **polVars)

                        configure_loop, loop_count, policy_loop = ezfunctions.exit_loop_default_yes(loop_count, policy_type)

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

        # Close the Template file
        polVars["template_file"] = 'template_close.jinja2'
        ezfunctions.write_to_template(self, **polVars)

    #==============================================
    # Resource Pool Module
    #==============================================
    def resource_pools(self, jsonData, easy_jsonData, **kwargs):
        name_prefix = self.name_prefix
        name_suffix = 'resource'
        opSystem = kwargs['opSystem']
        org = self.org
        policy_type = 'Resource Pool'
        polVars = {}
        polVars["header"] = '%s Variables' % (policy_type)
        polVars["initial_write"] = True
        polVars["org"] = org
        polVars["policy_type"] = policy_type
        polVars["template_file"] = 'template_open.jinja2'
        polVars["template_type"] = 'resource_pools'
        tfDir = kwargs['tfDir']

        # Open the Template file
        ezfunctions.write_to_template(self, **polVars)
        polVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  The {policy_type} represents a collection of resources that can be associated to ')
            print(f'  the configuration entities such as server profiles.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            if opSystem == 'Windows':
                print(f'  - {tfDir}\\{org}\\{self.type}\\{polVars["template_type"]}.auto.tfvars')
            else:
                print(f'  - {tfDir}/{org}/{self.type}/{polVars["template_type"]}.auto.tfvars')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure a {policy_type}?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                policy_loop = False
                while policy_loop == False:

                    if not name_prefix == '':
                        name = '%s_%s' % (name_prefix, name_suffix)
                    else:
                        name = '%s_%s' % (org, name_suffix)

                    polVars["name"] = ezfunctions.policy_name(name, policy_type)
                    polVars["descr"] = ezfunctions.policy_descr(polVars["name"], policy_type)

                    # Pull in the Policies for iSCSI Boot
                    polVars["multi_select"] = False

                    # Assignment Order
                    jsonVars = jsonData['components']['schemas']['pool.AbstractPool']['allOf'][1]['properties']
                    polVars["var_description"] = jsonVars['AssignmentOrder']['description']
                    polVars["jsonVars"] = sorted(jsonVars['AssignmentOrder']['enum'])
                    polVars["defaultVar"] = jsonVars['AssignmentOrder']['default']
                    polVars["varType"] = 'Assignment Order'
                    polVars["assignment_order"] = ezfunctions.variablesFromAPI(**polVars)

                    # List of Serial Numbers
                    polVars['serial_number_list'] = []
                    valid = False
                    while valid == False:
                        polVars["Description"] = 'A List of Serial Numbers to add to the Resource Pool.'
                        polVars["varDefault"] = ''
                        polVars["varInput"] = 'Enter the Server Serial Number:'
                        polVars["varName"] = 'Serial Number'
                        polVars["varRegex"] = '^[A-Z]{3}[2-3][\\d]([0][1-9]|[1-4][0-9]|[5][1-3])[\\dA-Z]{4}$'
                        polVars["minLength"] = 11
                        polVars["maxLength"] = 11
                        polVars['serial_number_list'].append(ezfunctions.varStringLoop(**polVars))

                        polVars["Description"] = 'Add Additional Serial Numbers.'
                        polVars["varInput"] = f'Do you want to add another Serial Number?'
                        polVars["varDefault"] = 'N'
                        polVars["varName"] = 'Additional Serial Numbers'
                        valid = ezfunctions.varBoolLoop(**polVars)

                    # Server Type
                    jsonVars = easy_jsonData['pools']['resourcepool.Pool']
                    polVars["var_description"] = jsonVars['server_type']['description']
                    polVars["jsonVars"] = sorted(jsonVars['server_type']['enum'])
                    polVars["defaultVar"] = jsonVars['server_type']['default']
                    polVars["varType"] = 'Server Type'
                    polVars["server_type"] = ezfunctions.variablesFromAPI(**polVars)

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'   assignment_order   = "{polVars["assignment_order"]}"')
                    print(f'   description        = "{polVars["descr"]}"')
                    print(f'   name               = "{polVars["name"]}"')
                    print(f'   serial_number_list = {polVars["serial_number_list"]}')
                    print(f'   server_type        = "{polVars["server_type"]}"')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                        if confirm_policy == 'Y' or confirm_policy == '':
                            confirm_policy = 'Y'

                            # Write Policies to Template File
                            polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                            ezfunctions.write_to_template(self, **polVars)

                            configure_loop, policy_loop = ezfunctions.exit_default_no(polVars["policy_type"])
                            valid_confirm = True

                        elif confirm_policy == 'N':
                            print(f'\n------------------------------------------------------\n')
                            print(f'  Starting {polVars["policy_type"]} Section over.')
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
        polVars["template_file"] = 'template_close.jinja2'
        ezfunctions.write_to_template(self, **polVars)

    #==============================================
    # UUID Pools Module
    #==============================================
    def uuid_pools(self, jsonData, easy_jsonData, **kwargs):
        name_prefix = self.name_prefix
        name_suffix = 'uuid_pool'
        opSystem = kwargs['opSystem']
        org = self.org
        policy_type = 'UUID Pool'
        polVars = {}
        polVars["header"] = '%s Variables' % (policy_type)
        polVars["initial_write"] = True
        polVars["org"] = org
        polVars["policy_type"] = policy_type
        polVars["template_file"] = 'template_open.jinja2'
        polVars["template_type"] = 'uuid_pools'
        tfDir = kwargs['tfDir']

        # Open the Template file
        ezfunctions.write_to_template(self, **polVars)
        polVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  The Universally Unique Identifier (UUID) are written in 5 groups of hexadecimal digits')
            print(f'  separated by hyphens.  The length of each group is: 8-4-4-4-12. UUIDs are fixed length.')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure a {policy_type}.  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                policy_loop = False
                while policy_loop == False:

                    if not name_prefix == '':
                        name = '%s_%s' % (name_prefix, name_suffix)
                    else:
                        name = '%s_%s' % (org, name_suffix)

                    polVars["name"] = ezfunctions.policy_name(name, policy_type)
                    polVars["descr"] = ezfunctions.policy_descr(polVars["name"], policy_type)

                    polVars["multi_select"] = False
                    jsonVars = jsonData['components']['schemas']['pool.AbstractPool']['allOf'][1]['properties']

                    polVars["var_description"] = jsonVars['AssignmentOrder']['description']
                    polVars["jsonVars"] = sorted(jsonVars['AssignmentOrder']['enum'])
                    polVars["defaultVar"] = jsonVars['AssignmentOrder']['default']
                    polVars["varType"] = 'Assignment Order'
                    polVars["assignment_order"] = ezfunctions.variablesFromAPI(**polVars)

                    jsonVars = jsonData['components']['schemas']['uuidpool.Pool']['allOf'][1]['properties']

                    polVars["Description"] = jsonVars['Prefix']['description']
                    polVars["varDefault"] = '000025B5-0000-0000'
                    polVars["varInput"] = 'What is the UUID Prefix you would like to assign to the Pool?  [000025B5-0000-0000]:'
                    polVars["varName"] = 'UUID Prefix'
                    polVars["varRegex"] = jsonVars['Prefix']['pattern']
                    polVars["minLength"] = 18
                    polVars["maxLength"] = 18
                    polVars["prefix"] = ezfunctions.varStringLoop(**polVars)

                    jsonVars = jsonData['components']['schemas']['uuidpool.UuidBlock']['allOf'][1]['properties']

                    polVars["Description"] = jsonVars['From']['description']
                    polVars["varDefault"] = '0000-000000000000'
                    polVars["varInput"] = 'What is the First UUID Suffix in the Block?  [0000-000000000000]:'
                    polVars["varName"] = 'UUID First Suffix'
                    polVars["varRegex"] = jsonVars['From']['pattern']
                    polVars["minLength"] = 17
                    polVars["maxLength"] = 17
                    pool_from = ezfunctions.varStringLoop(**polVars)

                    jsonVars = jsonData['components']['schemas']['pool.AbstractBlockType']['allOf'][1]['properties']

                    polVars["Description"] = jsonVars['Size']['description']
                    polVars["varInput"] = 'How Many IP Addresses should be added to the Pool?  Range is 1-1000.'
                    polVars["varDefault"] = 1000
                    polVars["varName"] = 'Pool Size'
                    polVars["minNum"] = jsonVars['Size']['minimum']
                    polVars["maxNum"] = jsonVars['Size']['maximum']
                    pool_size = ezfunctions.varNumberLoop(**polVars)

                    if re.search('[a-z]', pool_from):
                        pool_from = pool_from.upper()
                    from_split = pool_from.split('-')
                    pool_to = hex(int(from_split[1], 16) + pool_size - 1).split('x')[-1]
                    add_zeros = 12 - len(pool_to)
                    if not add_zeros == 0:
                        pool_to = str(from_split[0]) + '-' + ('0' * add_zeros) + pool_to
                    pool_to = pool_to.upper()

                    polVars["uuid_blocks"] = [
                        {
                            'from':pool_from,
                            'size':pool_size,
                            'to':pool_to
                        }
                    ]
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'    assignment_order = "{polVars["assignment_order"]}"')
                    print(f'    description      = "{polVars["descr"]}"')
                    print(f'    name             = "{polVars["name"]}"')
                    print(f'    prefix           = "{polVars["prefix"]}"')
                    print(f'    uuid_blocks = ''[')
                    for i in polVars["uuid_blocks"]:
                        print(f'      ''{')
                        for k, v in i.items():
                            if k == 'from':
                                print(f'        from = "{v}"')
                            elif k == 'size':
                                print(f'        size = {v}')
                            elif k == 'to':
                                print(f'        to   = "{v}"')
                        print(f'      ''}')
                    print(f'    '']')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
                        if confirm_policy == 'Y' or confirm_policy == '':
                            confirm_policy = 'Y'

                            # Write Policies to Template File
                            polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                            ezfunctions.write_to_template(self, **polVars)

                            configure_loop, policy_loop = ezfunctions.exit_default_no(polVars["policy_type"])
                            valid_confirm = True

                        elif confirm_policy == 'N':
                            print(f'\n------------------------------------------------------\n')
                            print(f'  Starting {polVars["policy_type"]} Section over.')
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
        polVars["template_file"] = 'template_close.jinja2'
        ezfunctions.write_to_template(self, **polVars)

    #==============================================
    # WWNN Pools Module
    #==============================================
    def wwnn_pools(self, jsonData, easy_jsonData, **kwargs):
        name_prefix = self.name_prefix
        name_suffix = 'wwnn_pool'
        opSystem = kwargs['opSystem']
        org = self.org
        policy_type = 'WWNN Pool'
        polVars = {}
        polVars["header"] = '%s Variables' % (policy_type)
        polVars["initial_write"] = True
        polVars["org"] = org
        polVars["policy_type"] = policy_type
        polVars["template_file"] = 'template_open.jinja2'
        polVars["template_type"] = 'wwnn_pools'
        tfDir = kwargs['tfDir']

        # Open the Template file
        ezfunctions.write_to_template(self, **polVars)
        polVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  WWNN Pool Convention Recommendations:')
            print(f'  - Leverage the Cisco UCS OUI of 20:00:00:25:B5 for the WWNN Pool Prefix.')
            print(f'  - Pool Size can be between 1 and 1000 addresses.')
            print(f'  - Refer to "UCS Naming Conventions 0.5.ppsx" in the Repository for further guidance.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            if opSystem == 'Windows':
                print(f'  - {tfDir}\\{org}\\{self.type}\\{polVars["template_type"]}.auto.tfvars')
            else:
                print(f'  - {tfDir}/{org}/{self.type}/{polVars["template_type"]}.auto.tfvars')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure a {policy_type}?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                policy_loop = False
                while policy_loop == False:

                    if not name_prefix == '':
                        name = '%s_%s' % (name_prefix, name_suffix)
                    else:
                        name = '%s_%s' % (org, name_suffix)

                    polVars["name"] = ezfunctions.policy_name(name, policy_type)
                    polVars["descr"] = ezfunctions.policy_descr(polVars["name"], policy_type)

                    polVars["multi_select"] = False
                    jsonVars = jsonData['components']['schemas']['pool.AbstractPool']['allOf'][1]['properties']

                    polVars["var_description"] = jsonVars['AssignmentOrder']['description']
                    polVars["jsonVars"] = sorted(jsonVars['AssignmentOrder']['enum'])
                    polVars["defaultVar"] = jsonVars['AssignmentOrder']['default']
                    polVars["varType"] = 'Assignment Order'
                    polVars["assignment_order"] = ezfunctions.variablesFromAPI(**polVars)

                    jsonVars = jsonData['components']['schemas']['fcpool.Block']['allOf'][1]['properties']

                    polVars["Description"] = jsonVars['From']['description']
                    polVars["varDefault"] = '20:00:00:25:B5:00:00:00'
                    polVars["varInput"] = 'What is the Starting WWNN Address to Assign to the Pool?  [20:00:00:25:B5:00:00:00]:'
                    polVars["varName"] = 'Starting WWNN Address'
                    polVars["varRegex"] = jsonVars['From']['pattern']
                    polVars["minLength"] = 23
                    polVars["maxLength"] = 23
                    pool_from = ezfunctions.varStringLoop(**polVars)

                    jsonVars = jsonData['components']['schemas']['pool.AbstractBlockType']['allOf'][1]['properties']

                    polVars["Description"] = jsonVars['Size']['description']
                    polVars["varInput"] = 'How Many WWNN Addresses should be added to the Pool?  Range is 1-1000.'
                    polVars["varDefault"] = 1000
                    polVars["varName"] = 'Pool Size'
                    polVars["minNum"] = jsonVars['Size']['minimum']
                    polVars["maxNum"] = jsonVars['Size']['maximum']
                    pool_size = ezfunctions.varNumberLoop(**polVars)

                    if re.search('[a-z]', pool_from):
                        pool_from = pool_from.upper()
                    beginx = int(pool_from.replace(':', ''), 16)
                    add_dec = (beginx + int(pool_size) - 1)
                    pool_to = ':'.join(['{}{}'.format(a, b)
                        for a, b
                        in zip(*[iter('{:012x}'.format(add_dec))]*2)])
                    pool_to = pool_to.upper()

                    polVars["wwnn_blocks"] = [
                        {
                            'from':pool_from,
                            'size':pool_size,
                            'to':pool_to
                        }
                    ]

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'    assignment_order = "{polVars["assignment_order"]}"')
                    print(f'    description      = "{polVars["descr"]}"')
                    print(f'    name             = "{polVars["name"]}"')
                    print(f'    id_blocks = ''[')
                    for item in polVars["wwnn_blocks"]:
                        print('      {')
                        for k, v in item.items():
                            if k == 'from':
                                print(f'        from = "{v}" ')
                            elif k == 'size':
                                print(f'        size = {v}')
                            elif k == 'to':
                                print(f'        to   = "{v}"')
                        print('      }')
                    print(f'    '']')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                        if confirm_policy == 'Y' or confirm_policy == '':
                            confirm_policy = 'Y'

                            # Write Policies to Template File
                            polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                            ezfunctions.write_to_template(self, **polVars)

                            configure_loop, policy_loop = ezfunctions.exit_default_no(polVars["policy_type"])
                            valid_confirm = True

                        elif confirm_policy == 'N':
                            print(f'\n------------------------------------------------------\n')
                            print(f'  Starting {polVars["policy_type"]} Section over.')
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
        polVars["template_file"] = 'template_close.jinja2'
        ezfunctions.write_to_template(self, **polVars)

    #==============================================
    # WWPN Pools Module
    #==============================================
    def wwpn_pools(self, jsonData, easy_jsonData, **kwargs):
        name_prefix = self.name_prefix
        opSystem = kwargs['opSystem']
        org = self.org
        policy_type = 'WWPN Pool'
        polVars = {}
        polVars["header"] = '%s Variables' % (policy_type)
        polVars["initial_write"] = True
        polVars["org"] = org
        polVars["policy_type"] = policy_type
        polVars["template_file"] = 'template_open.jinja2'
        polVars["template_type"] = 'wwpn_pools'
        tfDir = kwargs['tfDir']

        # Open the Template file
        ezfunctions.write_to_template(self, **polVars)
        polVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  WWPN Pool Convention Recommendations:')
            print(f'  - Leverage the Cisco UCS OUI of 20:00:00:25:B5 for the WWPN Pool Prefix.')
            print(f'  - For WWPN Pools; create a pool for each Fabric.')
            print(f'  - Pool Size can be between 1 and 1000 addresses.')
            print(f'  - Refer to "UCS Naming Conventions 0.5.ppsx" in the Repository for further guidance.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            if opSystem == 'Windows':
                print(f'  - {tfDir}\\{org}\\{self.type}\\{polVars["template_type"]}.auto.tfvars')
            else:
                print(f'  - {tfDir}/{org}/{self.type}/{polVars["template_type"]}.auto.tfvars')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure a {policy_type}?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                loop_count = 0
                policy_loop = False
                while policy_loop == False:

                    name = ezfunctions.naming_rule_fabric(loop_count, name_prefix, org)

                    polVars["name"] = ezfunctions.policy_name(name, policy_type)
                    polVars["descr"] = ezfunctions.policy_descr(polVars["name"], policy_type)

                    polVars["multi_select"] = False
                    jsonVars = jsonData['components']['schemas']['pool.AbstractPool']['allOf'][1]['properties']

                    polVars["var_description"] = jsonVars['AssignmentOrder']['description']
                    polVars["jsonVars"] = sorted(jsonVars['AssignmentOrder']['enum'])
                    polVars["defaultVar"] = jsonVars['AssignmentOrder']['default']
                    polVars["varType"] = 'Assignment Order'
                    polVars["assignment_order"] = ezfunctions.variablesFromAPI(**polVars)

                    jsonVars = jsonData['components']['schemas']['fcpool.Block']['allOf'][1]['properties']

                    polVars["Description"] = jsonVars['From']['description']
                    if loop_count % 2 == 0: 
                        polVars["varDefault"] = '20:00:00:25:B5:0A:00:00'
                        polVars["varInput"] = 'What is the Starting WWPN Address to Assign to the Pool?  [20:00:00:25:B5:0A:00:00]:'
                    else:
                        polVars["varDefault"] = '20:00:00:25:B5:0B:00:00'
                        polVars["varInput"] = 'What is the Starting WWPN Address to Assign to the Pool?  [20:00:00:25:B5:0B:00:00]:'
                    polVars["varName"] = 'Starting WWPN Address'
                    polVars["varRegex"] = jsonVars['From']['pattern']
                    polVars["minLength"] = 23
                    polVars["maxLength"] = 23
                    pool_from = ezfunctions.varStringLoop(**polVars)

                    jsonVars = jsonData['components']['schemas']['pool.AbstractBlockType']['allOf'][1]['properties']

                    polVars["Description"] = jsonVars['Size']['description']
                    polVars["varInput"] = 'How Many WWPN Addresses should be added to the Pool?  Range is 1-1000.'
                    polVars["varDefault"] = 1000
                    polVars["varName"] = 'Pool Size'
                    polVars["minNum"] = jsonVars['Size']['minimum']
                    polVars["maxNum"] = jsonVars['Size']['maximum']
                    pool_size = ezfunctions.varNumberLoop(**polVars)

                    if re.search('[a-z]', pool_from):
                        pool_from = pool_from.upper()
                    beginx = int(pool_from.replace(':', ''), 16)
                    add_dec = (beginx + int(pool_size) - 1)
                    pool_to = ':'.join(['{}{}'.format(a, b)
                        for a, b
                        in zip(*[iter('{:012x}'.format(add_dec))]*2)])
                    pool_to = pool_to.upper()

                    polVars["wwpn_blocks"] = [
                        {
                            'from':pool_from,
                            'size':pool_size,
                            'to':pool_to
                        }
                    ]

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'    assignment_order = "{polVars["assignment_order"]}"')
                    print(f'    description      = "{polVars["descr"]}"')
                    print(f'    name             = "{polVars["name"]}"')
                    print(f'    id_blocks = ''[')
                    for item in polVars["wwpn_blocks"]:
                        print('      {')
                        for k, v in item.items():
                            if k == 'from':
                                print(f'        from = "{v}" ')
                            elif k == 'size':
                                print(f'        size = {v}')
                            elif k == 'to':
                                print(f'        to   = "{v}"')
                        print('      }')
                    print(f'    '']')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                        if confirm_policy == 'Y' or confirm_policy == '':
                            confirm_policy = 'Y'

                            # Write Policies to Template File
                            polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                            ezfunctions.write_to_template(self, **polVars)

                            configure_loop, loop_count, policy_loop = ezfunctions.exit_loop_default_yes(loop_count, policy_type)
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
                print(f'\n------------------------------------------------------\n')
                print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                print(f'\n------------------------------------------------------\n')

        # Close the Template file
        polVars["template_file"] = 'template_close.jinja2'
        ezfunctions.write_to_template(self, **polVars)
