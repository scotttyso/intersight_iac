#!/usr/bin/env python3

import ipaddress
import jinja2
import pkg_resources
import re
import validating
from easy_functions import exit_default_no, exit_loop_default_yes
from easy_functions import naming_rule_fabric
from easy_functions import policy_descr, policy_name
from easy_functions import variablesFromAPI
from easy_functions import variablesFromAPI
from easy_functions import variablesFromAPI
from easy_functions import varBoolLoop
from easy_functions import varNumberLoop
from easy_functions import varStringLoop
from easy_functions import write_to_template

ucs_template_path = pkg_resources.resource_filename('class_pools', 'Templates/')

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
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'ip_pools'
        tfDir = kwargs['tfDir']

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  At a minimum you will need one IP Pool for KVM Access to Servers.  Currently out-of-band')
            print(f'  management is not supported for KVM access.  This IP Pool will need to be associated to a ')
            print(f'  VLAN assigned to the VLAN Pool of the Domain.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            if opSystem == 'Windows':
                print(f'  - {tfDir}\\{org}\\{self.type}\\{templateVars["template_type"]}.auto.tfvars')
            else:
                print(f'  - {tfDir}/{org}/{self.type}/{templateVars["template_type"]}.auto.tfvars')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure an {policy_type}?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                policy_loop = False
                while policy_loop == False:

                    if not name_prefix == '':
                        name = '%s_%s' % (name_prefix, name_suffix)
                    else:
                        name = '%s_%s' % (org, name_suffix)

                    templateVars["name"] = policy_name(name, policy_type)
                    templateVars["descr"] = policy_descr(templateVars["name"], policy_type)

                    templateVars["multi_select"] = False
                    jsonVars = jsonData['components']['schemas']['pool.AbstractPool']['allOf'][1]['properties']

                    templateVars["var_description"] = jsonVars['AssignmentOrder']['description']
                    templateVars["jsonVars"] = sorted(jsonVars['AssignmentOrder']['enum'])
                    templateVars["defaultVar"] = jsonVars['AssignmentOrder']['default']
                    templateVars["varType"] = 'Assignment Order'
                    templateVars["assignment_order"] = variablesFromAPI(**templateVars)

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

                        templateVars["Description"] = 'The Gateway/Prefix to Assign to the Pool'
                        templateVars["varDefault"] = '198.18.0.1/24'
                        templateVars["varInput"] = 'What is the Gateway/Prefix to Assign to the Pool?  [198.18.0.1/24]:'
                        templateVars["varName"] = 'Gateway/Prefix'
                        templateVars["varRegex"] = '^([1-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\\.{3}([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\/[0-9]{1,2}$'
                        templateVars["minLength"] = 7
                        templateVars["maxLength"] = 20
                        network_prefix = varStringLoop(**templateVars)

                        gateway = str(ipaddress.IPv4Interface(network_prefix).ip)
                        netmask = str(ipaddress.IPv4Interface(network_prefix).netmask)
                        network = str(ipaddress.IPv4Interface(network_prefix).network)
                        prefix = network_prefix.split('/')[1]

                        templateVars["Description"] = jsonVars['From']['description']
                        templateVars["varDefault"] = '198.18.0.2'
                        templateVars["varInput"] = 'What is the Starting IP Address to Assign to the Pool?  [198.18.0.2]:'
                        templateVars["varName"] = 'Starting IP Address'
                        templateVars["varRegex"] = jsonVars['From']['pattern']
                        templateVars["minLength"] = 7
                        templateVars["maxLength"] = 15
                        pool_from = varStringLoop(**templateVars)

                        jsonVars = jsonData['components']['schemas']['pool.AbstractBlockType']['allOf'][1]['properties']

                        templateVars["Description"] = jsonVars['Size']['description']
                        templateVars["varInput"] = 'How Many IP Addresses should be added to the Pool?  Range is 1-1000.'
                        templateVars["varDefault"] = 253
                        templateVars["varName"] = 'Pool Size'
                        templateVars["minNum"] = jsonVars['Size']['minimum']
                        templateVars["maxNum"] = jsonVars['Size']['maximum']
                        pool_size = varNumberLoop(**templateVars)

                        jsonVars = jsonData['components']['schemas']['ippool.IpV4Config']['allOf'][1]['properties']

                        templateVars["Description"] = jsonVars['PrimaryDns']['description']
                        templateVars["varDefault"] = '208.67.220.220'
                        templateVars["varInput"] = 'What is your Primary DNS Server?  [208.67.220.220]:'
                        templateVars["varName"] = 'Primary Dns'
                        templateVars["varRegex"] = jsonVars['PrimaryDns']['pattern']
                        templateVars["minLength"] = 7
                        templateVars["maxLength"] = 15
                        primary_dns = varStringLoop(**templateVars)

                        templateVars["Description"] = jsonVars['SecondaryDns']['description']
                        templateVars["varDefault"] = ''
                        templateVars["varInput"] = 'What is your Secondary DNS Server?  [press enter to skip]:'
                        templateVars["varName"] = 'Secondary Dns'
                        templateVars["varRegex"] = jsonVars['SecondaryDns']['pattern']
                        templateVars["minLength"] = 7
                        templateVars["maxLength"] = 15
                        secondary_dns = varStringLoop(**templateVars)

                        beginx = int(ipaddress.IPv4Address(pool_from))
                        add_dec = (beginx + int(pool_size) - 1)
                        pool_to = str(ipaddress.IPv4Address(add_dec))

                        templateVars["ipv4_blocks"] = [
                            {
                                'from':pool_from,
                                'size':pool_size,
                                'to':pool_to
                            }
                        ]
                        templateVars["ipv4_configuration"] = {
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

                        templateVars["Description"] = 'The Gateway/Prefix to Assign to the Pool'
                        templateVars["varDefault"] = '2001:0002::1/64'
                        templateVars["varInput"] = 'What is the Gateway/Prefix to Assign to the Pool?  [2001:0002::1/64]:'
                        templateVars["varName"] = 'Gateway/Prefix'
                        templateVars["varRegex"] = '^$|^(([0-9A-Fa-f]{1,4}:([0-9A-Fa-f]{1,4}:([0-9A-Fa-f]{1,4}:([0-9A-Fa-f]{1,4}:([0-9A-Fa-f]{1,4}:[0-9A-Fa-f]{0,4}|:[0-9A-Fa-f]{1,4})?|(:[0-9A-Fa-f]{1,4}){0,2})|(:[0-9A-Fa-f]{1,4}){0,3})|(:[0-9A-Fa-f]{1,4}){0,4})|:(:[0-9A-Fa-f]{1,4}){0,5})((:[0-9A-Fa-f]{1,4}){2}|:(25[0-5]|(2[0-4]|1[0-9]|[1-9])?[0-9])(\\.(25[0-5]|(2[0-4]|1[0-9]|[1-9])?[0-9])){3})|(([0-9A-Fa-f]{1,4}:){1,6}|:):[0-9A-Fa-f]{0,4}|([0-9A-Fa-f]{1,4}:){7}:)\/[0-9]{1,3}$'
                        templateVars["minLength"] = 6
                        templateVars["maxLength"] = 164
                        network_prefix = varStringLoop(**templateVars)

                        # broadcast = str(ipaddress.IPv4Interface(network_prefix).broadcast_address)
                        gateway = str(ipaddress.IPv6Interface(network_prefix).ip)
                        if re.search('[a-z]+', gateway):
                            gateway = gateway.upper()
                        network = str(ipaddress.IPv6Interface(network_prefix).network)
                        prefix = network_prefix.split('/')[1]

                        templateVars["Description"] = jsonVars['From']['description']
                        templateVars["varDefault"] = '2001:0002::2'
                        templateVars["varInput"] = 'What is the Starting IP Address to Assign to the Pool?  [2001:0002::2]:'
                        templateVars["varName"] = 'Starting IPv6 Address'
                        templateVars["varRegex"] = jsonVars['From']['pattern']
                        templateVars["minLength"] = 3
                        templateVars["maxLength"] = 164
                        starting = varStringLoop(**templateVars)

                        jsonVars = jsonData['components']['schemas']['pool.AbstractBlockType']['allOf'][1]['properties']

                        templateVars["Description"] = jsonVars['Size']['description']
                        templateVars["varInput"] = 'How Many IPv6 Addresses should be added to the Pool?  Range is 1-1000.'
                        templateVars["varDefault"] = 1000
                        templateVars["varName"] = 'Pool Size'
                        templateVars["minNum"] = jsonVars['Size']['minimum']
                        templateVars["maxNum"] = jsonVars['Size']['maximum']
                        pool_size = varNumberLoop(**templateVars)

                        jsonVars = jsonData['components']['schemas']['ippool.IpV6Config']['allOf'][1]['properties']

                        templateVars["Description"] = jsonVars['PrimaryDns']['description']
                        templateVars["varDefault"] = '2620:119:53::53'
                        templateVars["varInput"] = 'What is your Primary DNS Server?  [2620:119:53::53]:'
                        templateVars["varName"] = 'Primary Dns'
                        templateVars["varRegex"] = jsonVars['PrimaryDns']['pattern']
                        templateVars["minLength"] = 3
                        templateVars["maxLength"] = 164
                        primary_dns = varStringLoop(**templateVars)

                        templateVars["Description"] = jsonVars['SecondaryDns']['description']
                        templateVars["varDefault"] = ''
                        templateVars["varInput"] = 'What is your Secondary DNS Server?  [press enter to skip]:'
                        templateVars["varName"] = 'Secondary Dns'
                        templateVars["varRegex"] = jsonVars['SecondaryDns']['pattern']
                        templateVars["minLength"] = 3
                        templateVars["maxLength"] = 164
                        secondary_dns = varStringLoop(**templateVars)

                        beginx = int(ipaddress.IPv6Address(starting))
                        add_dec = (beginx + int(pool_size) - 1)
                        ending = str(ipaddress.IPv6Address(add_dec))

                        templateVars["ipv6_blocks"] = [
                            {
                                'from':starting,
                                'size':pool_size,
                                'to':ending
                            }
                        ]
                        templateVars["ipv6_configuration"] = {
                            'gateway':gateway,
                            'prefix':prefix,
                            'primary_dns':primary_dns,
                            'secondary_dns':secondary_dns
                        }

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'    assignment_order = "{templateVars["assignment_order"]}"')
                    print(f'    description      = "{templateVars["descr"]}"')
                    print(f'    name             = "{templateVars["name"]}"')
                    if config_ipv4 == 'Y' or config_ipv4 == '':
                        print(f'    ipv4_blocks = ''{')
                        for item in templateVars["ipv4_blocks"]:
                            print('      {')
                            for k, v in item.items():
                                if k == 'from':
                                    print(f'        from = "{v}" ')
                                elif k == 'size':
                                    print(f'        size = {v}')
                                elif k == 'to':
                                    print(f'        to   = "{v}"')
                            print('      }')
                        print(f'    ''}')
                        print('    ipv4_configuration = {')
                        print('      config = {')
                        for k, v in templateVars["ipv4_configuration"].items():
                            if k == 'gateway':
                                print(f'        gateway       = "{v}"')
                            elif k == 'netmask':
                                print(f'        netmask       = "{v}"')
                            elif k == 'primary_dns':
                                print(f'        primary_dns   = "{v}"')
                            elif k == 'secondary_dns':
                                print(f'        secondary_dns = "{v}"')
                        print('      }')
                        print('    }')
                    if config_ipv6 == 'Y':
                        print(f'    ipv6_blocks = ''{')
                        for item in templateVars["ipv6_blocks"]:
                            print('      {')
                            for k, v in item.items():
                                if k == 'from':
                                    print(f'        from = "{v}"')
                                elif k == 'size':
                                    print(f'        size = {v}')
                                elif k == 'to':
                                    print(f'        to   = "{v}"')
                            print('      }')
                        print(f'    ''}')
                        print('    ipv6_configuration = {')
                        print('      config = {')
                        for k, v in templateVars["ipv6_configuration"].items():
                            if k == 'gateway':
                                print(f'        gateway       = "{v}"')
                            elif k == 'prefix':
                                print(f'        prefix        = "{v}"')
                            elif k == 'primary_dns':
                                print(f'        primary_dns   = "{v}"')
                            elif k == 'secondary_dns':
                                print(f'        secondary_dns = "{v}"')
                        print('      }')
                        print('    }')
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

            elif configure == 'N':
                configure_loop = True
            else:
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                print(f'\n-------------------------------------------------------------------------------------------\n')

        # Close the Template file
        templateVars["template_file"] = 'template_close.jinja2'
        write_to_template(self, **templateVars)

    #==============================================
    # IQN Pools Module
    #==============================================
    def iqn_pools(self, jsonData, easy_jsonData, **kwargs):
        name_prefix = self.name_prefix
        name_suffix = 'iqn_pool'
        opSystem = kwargs['opSystem']
        org = self.org
        policy_type = 'IQN Pool'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'iqn_pools'
        tfDir = kwargs['tfDir']

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

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

                    templateVars["name"] = policy_name(name, policy_type)
                    templateVars["descr"] = policy_descr(templateVars["name"], policy_type)

                    templateVars["multi_select"] = False
                    jsonVars = jsonData['components']['schemas']['pool.AbstractPool']['allOf'][1]['properties']

                    templateVars["var_description"] = jsonVars['AssignmentOrder']['description']
                    templateVars["jsonVars"] = sorted(jsonVars['AssignmentOrder']['enum'])
                    templateVars["defaultVar"] = jsonVars['AssignmentOrder']['default']
                    templateVars["varType"] = 'Assignment Order'
                    templateVars["assignment_order"] = variablesFromAPI(**templateVars)

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

                        templateVars["Description"] = jsonVars['Prefix']['description']
                        templateVars["varDefault"] = 'iqn.1984-12.com.cisco'
                        templateVars["varInput"] = 'What is the IQN Prefix you would like to assign to the Pool?  [iqn.1984-12.com.cisco]:'
                        templateVars["varName"] = 'IQN Prefix'
                        templateVars["varRegex"] = '^$|^(?:iqn\\.[0-9]{4}-[0-9]{2}(?:\\.[A-Za-z](?:[A-Za-z0-9\\-]*[A-Za-z0-9])?)+?'
                        templateVars["minLength"] = 7
                        templateVars["maxLength"] = 64
                        templateVars["prefix"] = varStringLoop(**templateVars)

                        jsonVars = jsonData['components']['schemas']['iqnpool.IqnSuffixBlock']['allOf'][1]['properties']

                        templateVars["Description"] = jsonVars['From']['description']
                        templateVars["varInput"] = jsonVars['From']['description'] 
                        templateVars["varDefault"] = 0
                        templateVars["varName"] = 'Starting Suffix'
                        templateVars["minNum"] = 0
                        templateVars["maxNum"] = 60000000000
                        pool_from = varNumberLoop(**templateVars)

                        templateVars["Description"] = jsonVars['Suffix']['description']
                        templateVars["varDefault"] = 'ucs-host'
                        templateVars["varInput"] = 'What is the IQN Suffix you would like to assign to the Pool?  [ucs-host]:'
                        templateVars["varName"] = 'IQN Suffix'
                        templateVars["varRegex"] = '[0-9a-zA-Z]'
                        templateVars["minLength"] = 3
                        templateVars["maxLength"] = 32
                        suffix = varStringLoop(**templateVars)

                        jsonVars = jsonData['components']['schemas']['pool.AbstractBlockType']['allOf'][1]['properties']

                        templateVars["Description"] = jsonVars['Size']['description']
                        templateVars["varInput"] = 'How Many IP Addresses should be added to the Pool?  Range is 1-1000.'
                        templateVars["varDefault"] = 1000
                        templateVars["varName"] = 'Pool Size'
                        templateVars["minNum"] = jsonVars['Size']['minimum']
                        templateVars["maxNum"] = jsonVars['Size']['maximum']
                        pool_size = varNumberLoop(**templateVars)

                        pool_to = pool_from + pool_size - 1
                        from_iqn = '%s:%s%s' % (templateVars['prefix'], suffix, pool_from)
                        to_iqn = '%s:%s%s' % (templateVars['prefix'], suffix, pool_to)
                        valid_starting_iqn = validating.iqn_address('IQN Staring Address', from_iqn)
                        valid_ending_iqn = validating.iqn_address('IQN Ending Address', to_iqn)
                        if valid_starting_iqn == True and valid_ending_iqn == True:
                            valid = True


                    templateVars["iqn_blocks"] = [
                        {
                            'from':pool_from,
                            'size':pool_size,
                            'suffix':suffix,
                            'to':pool_to
                        }
                    ]
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'    assignment_order = "{templateVars["assignment_order"]}"')
                    print(f'    description      = "{templateVars["descr"]}"')
                    print(f'    name             = "{templateVars["name"]}"')
                    print(f'    prefix           = "{templateVars["prefix"]}"')
                    print(f'    iqn_blocks = ''{')
                    for i in templateVars["iqn_blocks"]:
                        print(f'      ''"0" = {')
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
                    print(f'    ''}')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
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

            elif configure == 'N':
                configure_loop = True
            else:
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                print(f'\n-------------------------------------------------------------------------------------------\n')

        # Close the Template file
        templateVars["template_file"] = 'template_close.jinja2'
        write_to_template(self, **templateVars)

    #==============================================
    # MAC Pools Module
    #==============================================
    def mac_pools(self, jsonData, easy_jsonData, **kwargs):
        name_prefix = self.name_prefix
        opSystem = kwargs['opSystem']
        org = self.org
        policy_type = 'MAC Pool'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'mac_pools'
        tfDir = kwargs['tfDir']

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

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
                print(f'  - {tfDir}\\{org}\\{self.type}\\{templateVars["template_type"]}.auto.tfvars')
            else:
                print(f'  - {tfDir}/{org}/{self.type}/{templateVars["template_type"]}.auto.tfvars')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            loop_count = 0
            policy_loop = False
            while policy_loop == False:

                name = naming_rule_fabric(loop_count, name_prefix, org)

                templateVars["name"] = policy_name(name, policy_type)
                templateVars["descr"] = policy_descr(templateVars["name"], policy_type)

                templateVars["multi_select"] = False
                jsonVars = jsonData['components']['schemas']['pool.AbstractPool']['allOf'][1]['properties']

                templateVars["var_description"] = jsonVars['AssignmentOrder']['description']
                templateVars["jsonVars"] = sorted(jsonVars['AssignmentOrder']['enum'])
                templateVars["defaultVar"] = jsonVars['AssignmentOrder']['default']
                templateVars["varType"] = 'Assignment Order'
                templateVars["assignment_order"] = variablesFromAPI(**templateVars)

                jsonVars = jsonData['components']['schemas']['macpool.Block']['allOf'][1]['properties']

                templateVars["Description"] = jsonVars['From']['description']
                if loop_count % 2 == 0: 
                    templateVars["varDefault"] = '00:25:B5:0A:00:00'
                    templateVars["varInput"] = 'What is the Starting MAC Address to Assign to the Pool?  [00:25:B5:0A:00:00]:'
                else:
                    templateVars["varDefault"] = '00:25:B5:0B:00:00'
                    templateVars["varInput"] = 'What is the Starting MAC Address to Assign to the Pool?  [00:25:B5:0B:00:00]:'
                templateVars["varName"] = 'Starting MAC Address'
                templateVars["varRegex"] = '^([0-9a-zA-Z]{2}:){5}[0-9a-zA-Z]{2}$'
                templateVars["minLength"] = 17
                templateVars["maxLength"] = 17
                pool_from = varStringLoop(**templateVars)

                jsonVars = jsonData['components']['schemas']['pool.AbstractBlockType']['allOf'][1]['properties']

                templateVars["Description"] = jsonVars['Size']['description']
                templateVars["varInput"] = 'How Many IP Addresses should be added to the Pool?  Range is 1-1000.'
                templateVars["varDefault"] = 1000
                templateVars["varName"] = 'Pool Size'
                templateVars["minNum"] = jsonVars['Size']['minimum']
                templateVars["maxNum"] = jsonVars['Size']['maximum']
                pool_size = varNumberLoop(**templateVars)

                if re.search('[a-z]', pool_from):
                    pool_from = pool_from.upper()
                beginx = int(pool_from.replace(':', ''), 16)
                add_dec = (beginx + int(pool_size) - 1)
                pool_to = ':'.join(['{}{}'.format(a, b)
                    for a, b
                    in zip(*[iter('{:012x}'.format(add_dec))]*2)])
                pool_to = pool_to.upper()
                templateVars["mac_blocks"] = [
                    {
                        'from':pool_from,
                        'size':pool_size,
                        'to':pool_to
                    }
                ]

                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'    assignment_order = "{templateVars["assignment_order"]}"')
                print(f'    description      = "{templateVars["descr"]}"')
                print(f'    name             = "{templateVars["name"]}"')
                print(f'    mac_blocks = ''{')
                for item in templateVars["mac_blocks"]:
                    print('      "0" = {')
                    for k, v in item.items():
                        if k == 'from':
                            print(f'        from = "{v}" ')
                        elif k == 'size':
                            print(f'        size = {v}')
                        elif k == 'to':
                            print(f'        to   = "{v}"')
                    print('      }')
                print(f'    ''}')
                print(f'\n-------------------------------------------------------------------------------------------\n')
                valid_confirm = False
                while valid_confirm == False:
                    confirm_policy = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                    if confirm_policy == 'Y' or confirm_policy == '':
                        confirm_policy = 'Y'

                        # Write Policies to Template File
                        templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
                        write_to_template(self, **templateVars)

                        configure_loop, loop_count, policy_loop = exit_loop_default_yes(loop_count, policy_type)

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
        templateVars["template_file"] = 'template_close.jinja2'
        write_to_template(self, **templateVars)

    #==============================================
    # Resource Pool Module
    #==============================================
    def resource_pools(self, jsonData, easy_jsonData, **kwargs):
        name_prefix = self.name_prefix
        name_suffix = 'resource'
        opSystem = kwargs['opSystem']
        org = self.org
        policy_type = 'Resource Pool'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'resource_pools'
        tfDir = kwargs['tfDir']

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  The {policy_type} represents a collection of resources that can be associated to ')
            print(f'  the configuration entities such as server profiles.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            if opSystem == 'Windows':
                print(f'  - {tfDir}\\{org}\\{self.type}\\{templateVars["template_type"]}.auto.tfvars')
            else:
                print(f'  - {tfDir}/{org}/{self.type}/{templateVars["template_type"]}.auto.tfvars')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure a {policy_type}?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                policy_loop = False
                while policy_loop == False:

                    if not name_prefix == '':
                        name = '%s_%s' % (name_prefix, name_suffix)
                    else:
                        name = '%s_%s' % (org, name_suffix)

                    templateVars["name"] = policy_name(name, policy_type)
                    templateVars["descr"] = policy_descr(templateVars["name"], policy_type)

                    # Pull in the Policies for iSCSI Boot
                    templateVars["multi_select"] = False

                    # Assignment Order
                    jsonVars = jsonData['components']['schemas']['pool.AbstractPool']['allOf'][1]['properties']
                    templateVars["var_description"] = jsonVars['AssignmentOrder']['description']
                    templateVars["jsonVars"] = sorted(jsonVars['AssignmentOrder']['enum'])
                    templateVars["defaultVar"] = jsonVars['AssignmentOrder']['default']
                    templateVars["varType"] = 'Assignment Order'
                    templateVars["assignment_order"] = variablesFromAPI(**templateVars)

                    # List of Serial Numbers
                    templateVars['serial_number_list'] = []
                    valid = False
                    while valid == False:
                        templateVars["Description"] = 'A List of Serial Numbers to add to the Resource Pool.'
                        templateVars["varDefault"] = ''
                        templateVars["varInput"] = 'Enter the Server Serial Number:'
                        templateVars["varName"] = 'Serial Number'
                        templateVars["varRegex"] = '^[A-Z]{3}[2-3][\\d]([0][1-9]|[1-4][0-9]|[5][1-3])[\\dA-Z]{4}$'
                        templateVars["minLength"] = 11
                        templateVars["maxLength"] = 11
                        templateVars['serial_number_list'].append(varStringLoop(**templateVars))

                        templateVars["Description"] = 'Add Additional Serial Numbers.'
                        templateVars["varInput"] = f'Do you want to add another Serial Number?'
                        templateVars["varDefault"] = 'N'
                        templateVars["varName"] = 'Additional Serial Numbers'
                        valid = varBoolLoop(**templateVars)

                    # Server Type
                    jsonVars = easy_jsonData['pools']['resourcepool.Pool']
                    templateVars["var_description"] = jsonVars['server_type']['description']
                    templateVars["jsonVars"] = sorted(jsonVars['server_type']['enum'])
                    templateVars["defaultVar"] = jsonVars['server_type']['default']
                    templateVars["varType"] = 'Server Type'
                    templateVars["server_type"] = variablesFromAPI(**templateVars)

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'   assignment_order   = "{templateVars["assignment_order"]}"')
                    print(f'   description        = "{templateVars["descr"]}"')
                    print(f'   name               = "{templateVars["name"]}"')
                    print(f'   serial_number_list = {templateVars["serial_number_list"]}')
                    print(f'   server_type        = "{templateVars["server_type"]}"')
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

            elif configure == 'N':
                configure_loop = True
            else:
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                print(f'\n-------------------------------------------------------------------------------------------\n')

        # Close the Template file
        templateVars["template_file"] = 'template_close.jinja2'
        write_to_template(self, **templateVars)

    #==============================================
    # UUID Pools Module
    #==============================================
    def uuid_pools(self, jsonData, easy_jsonData, **kwargs):
        name_prefix = self.name_prefix
        name_suffix = 'uuid_pool'
        opSystem = kwargs['opSystem']
        org = self.org
        policy_type = 'UUID Pool'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'uuid_pools'
        tfDir = kwargs['tfDir']

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

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

                    templateVars["name"] = policy_name(name, policy_type)
                    templateVars["descr"] = policy_descr(templateVars["name"], policy_type)

                    templateVars["multi_select"] = False
                    jsonVars = jsonData['components']['schemas']['pool.AbstractPool']['allOf'][1]['properties']

                    templateVars["var_description"] = jsonVars['AssignmentOrder']['description']
                    templateVars["jsonVars"] = sorted(jsonVars['AssignmentOrder']['enum'])
                    templateVars["defaultVar"] = jsonVars['AssignmentOrder']['default']
                    templateVars["varType"] = 'Assignment Order'
                    templateVars["assignment_order"] = variablesFromAPI(**templateVars)

                    jsonVars = jsonData['components']['schemas']['uuidpool.Pool']['allOf'][1]['properties']

                    templateVars["Description"] = jsonVars['Prefix']['description']
                    templateVars["varDefault"] = '000025B5-0000-0000'
                    templateVars["varInput"] = 'What is the UUID Prefix you would like to assign to the Pool?  [000025B5-0000-0000]:'
                    templateVars["varName"] = 'UUID Prefix'
                    templateVars["varRegex"] = jsonVars['Prefix']['pattern']
                    templateVars["minLength"] = 18
                    templateVars["maxLength"] = 18
                    templateVars["prefix"] = varStringLoop(**templateVars)

                    jsonVars = jsonData['components']['schemas']['uuidpool.UuidBlock']['allOf'][1]['properties']

                    templateVars["Description"] = jsonVars['From']['description']
                    templateVars["varDefault"] = '0000-000000000000'
                    templateVars["varInput"] = 'What is the First UUID Suffix in the Block?  [0000-000000000000]:'
                    templateVars["varName"] = 'UUID First Suffix'
                    templateVars["varRegex"] = jsonVars['From']['pattern']
                    templateVars["minLength"] = 17
                    templateVars["maxLength"] = 17
                    pool_from = varStringLoop(**templateVars)

                    jsonVars = jsonData['components']['schemas']['pool.AbstractBlockType']['allOf'][1]['properties']

                    templateVars["Description"] = jsonVars['Size']['description']
                    templateVars["varInput"] = 'How Many IP Addresses should be added to the Pool?  Range is 1-1000.'
                    templateVars["varDefault"] = 1000
                    templateVars["varName"] = 'Pool Size'
                    templateVars["minNum"] = jsonVars['Size']['minimum']
                    templateVars["maxNum"] = jsonVars['Size']['maximum']
                    pool_size = varNumberLoop(**templateVars)

                    if re.search('[a-z]', pool_from):
                        pool_from = pool_from.upper()
                    from_split = pool_from.split('-')
                    pool_to = hex(int(from_split[1], 16) + pool_size - 1).split('x')[-1]
                    add_zeros = 12 - len(pool_to)
                    if not add_zeros == 0:
                        pool_to = str(from_split[0]) + '-' + ('0' * add_zeros) + pool_to
                    pool_to = pool_to.upper()

                    templateVars["uuid_blocks"] = [
                        {
                            'from':pool_from,
                            'size':pool_size,
                            'to':pool_to
                        }
                    ]
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'    assignment_order = "{templateVars["assignment_order"]}"')
                    print(f'    description      = "{templateVars["descr"]}"')
                    print(f'    name             = "{templateVars["name"]}"')
                    print(f'    prefix           = "{templateVars["prefix"]}"')
                    print(f'    uuid_blocks = ''{')
                    for i in templateVars["uuid_blocks"]:
                        print(f'      ''{')
                        for k, v in i.items():
                            if k == 'from':
                                print(f'        from = "{v}"')
                            elif k == 'size':
                                print(f'        size = {v}')
                            elif k == 'to':
                                print(f'        to   = "{v}"')
                        print(f'      ''}')
                    print(f'    ''}')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
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

            elif configure == 'N':
                configure_loop = True
            else:
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                print(f'\n-------------------------------------------------------------------------------------------\n')

        # Close the Template file
        templateVars["template_file"] = 'template_close.jinja2'
        write_to_template(self, **templateVars)

    #==============================================
    # WWNN Pools Module
    #==============================================
    def wwnn_pools(self, jsonData, easy_jsonData, **kwargs):
        name_prefix = self.name_prefix
        name_suffix = 'wwnn_pool'
        opSystem = kwargs['opSystem']
        org = self.org
        policy_type = 'WWNN Pool'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'wwnn_pools'
        tfDir = kwargs['tfDir']

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  WWNN Pool Convention Recommendations:')
            print(f'  - Leverage the Cisco UCS OUI of 20:00:00:25:B5 for the WWNN Pool Prefix.')
            print(f'  - Pool Size can be between 1 and 1000 addresses.')
            print(f'  - Refer to "UCS Naming Conventions 0.5.ppsx" in the Repository for further guidance.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            if opSystem == 'Windows':
                print(f'  - {tfDir}\\{org}\\{self.type}\\{templateVars["template_type"]}.auto.tfvars')
            else:
                print(f'  - {tfDir}/{org}/{self.type}/{templateVars["template_type"]}.auto.tfvars')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure a {policy_type}?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                policy_loop = False
                while policy_loop == False:

                    if not name_prefix == '':
                        name = '%s_%s' % (name_prefix, name_suffix)
                    else:
                        name = '%s_%s' % (org, name_suffix)

                    templateVars["name"] = policy_name(name, policy_type)
                    templateVars["descr"] = policy_descr(templateVars["name"], policy_type)

                    templateVars["multi_select"] = False
                    jsonVars = jsonData['components']['schemas']['pool.AbstractPool']['allOf'][1]['properties']

                    templateVars["var_description"] = jsonVars['AssignmentOrder']['description']
                    templateVars["jsonVars"] = sorted(jsonVars['AssignmentOrder']['enum'])
                    templateVars["defaultVar"] = jsonVars['AssignmentOrder']['default']
                    templateVars["varType"] = 'Assignment Order'
                    templateVars["assignment_order"] = variablesFromAPI(**templateVars)

                    jsonVars = jsonData['components']['schemas']['fcpool.Block']['allOf'][1]['properties']

                    templateVars["Description"] = jsonVars['From']['description']
                    templateVars["varDefault"] = '20:00:00:25:B5:00:00:00'
                    templateVars["varInput"] = 'What is the Starting WWNN Address to Assign to the Pool?  [20:00:00:25:B5:00:00:00]:'
                    templateVars["varName"] = 'Starting WWNN Address'
                    templateVars["varRegex"] = jsonVars['From']['pattern']
                    templateVars["minLength"] = 23
                    templateVars["maxLength"] = 23
                    pool_from = varStringLoop(**templateVars)

                    jsonVars = jsonData['components']['schemas']['pool.AbstractBlockType']['allOf'][1]['properties']

                    templateVars["Description"] = jsonVars['Size']['description']
                    templateVars["varInput"] = 'How Many WWNN Addresses should be added to the Pool?  Range is 1-1000.'
                    templateVars["varDefault"] = 1000
                    templateVars["varName"] = 'Pool Size'
                    templateVars["minNum"] = jsonVars['Size']['minimum']
                    templateVars["maxNum"] = jsonVars['Size']['maximum']
                    pool_size = varNumberLoop(**templateVars)

                    if re.search('[a-z]', pool_from):
                        pool_from = pool_from.upper()
                    beginx = int(pool_from.replace(':', ''), 16)
                    add_dec = (beginx + int(pool_size) - 1)
                    pool_to = ':'.join(['{}{}'.format(a, b)
                        for a, b
                        in zip(*[iter('{:012x}'.format(add_dec))]*2)])
                    pool_to = pool_to.upper()

                    templateVars["wwnn_blocks"] = [
                        {
                            'from':pool_from,
                            'size':pool_size,
                            'to':pool_to
                        }
                    ]

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'    assignment_order = "{templateVars["assignment_order"]}"')
                    print(f'    description      = "{templateVars["descr"]}"')
                    print(f'    name             = "{templateVars["name"]}"')
                    print(f'    id_blocks = ''{')
                    for item in templateVars["wwnn_blocks"]:
                        print('      "0" = {')
                        for k, v in item.items():
                            if k == 'from':
                                print(f'        from = "{v}" ')
                            elif k == 'size':
                                print(f'        size = {v}')
                            elif k == 'to':
                                print(f'        to   = "{v}"')
                        print('      }')
                    print(f'    ''}')
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

            elif configure == 'N':
                configure_loop = True
            else:
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                print(f'\n-------------------------------------------------------------------------------------------\n')

        # Close the Template file
        templateVars["template_file"] = 'template_close.jinja2'
        write_to_template(self, **templateVars)

    #==============================================
    # WWPN Pools Module
    #==============================================
    def wwpn_pools(self, jsonData, easy_jsonData, **kwargs):
        name_prefix = self.name_prefix
        opSystem = kwargs['opSystem']
        org = self.org
        policy_type = 'WWPN Pool'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'wwpn_pools'
        tfDir = kwargs['tfDir']

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

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
                print(f'  - {tfDir}\\{org}\\{self.type}\\{templateVars["template_type"]}.auto.tfvars')
            else:
                print(f'  - {tfDir}/{org}/{self.type}/{templateVars["template_type"]}.auto.tfvars')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure a {policy_type}?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                loop_count = 0
                policy_loop = False
                while policy_loop == False:

                    name = naming_rule_fabric(loop_count, name_prefix, org)

                    templateVars["name"] = policy_name(name, policy_type)
                    templateVars["descr"] = policy_descr(templateVars["name"], policy_type)

                    templateVars["multi_select"] = False
                    jsonVars = jsonData['components']['schemas']['pool.AbstractPool']['allOf'][1]['properties']

                    templateVars["var_description"] = jsonVars['AssignmentOrder']['description']
                    templateVars["jsonVars"] = sorted(jsonVars['AssignmentOrder']['enum'])
                    templateVars["defaultVar"] = jsonVars['AssignmentOrder']['default']
                    templateVars["varType"] = 'Assignment Order'
                    templateVars["assignment_order"] = variablesFromAPI(**templateVars)

                    jsonVars = jsonData['components']['schemas']['fcpool.Block']['allOf'][1]['properties']

                    templateVars["Description"] = jsonVars['From']['description']
                    if loop_count % 2 == 0: 
                        templateVars["varDefault"] = '20:00:00:25:B5:0A:00:00'
                        templateVars["varInput"] = 'What is the Starting WWPN Address to Assign to the Pool?  [20:00:00:25:B5:0A:00:00]:'
                    else:
                        templateVars["varDefault"] = '20:00:00:25:B5:0B:00:00'
                        templateVars["varInput"] = 'What is the Starting WWPN Address to Assign to the Pool?  [20:00:00:25:B5:0B:00:00]:'
                    templateVars["varName"] = 'Starting WWPN Address'
                    templateVars["varRegex"] = jsonVars['From']['pattern']
                    templateVars["minLength"] = 23
                    templateVars["maxLength"] = 23
                    pool_from = varStringLoop(**templateVars)

                    jsonVars = jsonData['components']['schemas']['pool.AbstractBlockType']['allOf'][1]['properties']

                    templateVars["Description"] = jsonVars['Size']['description']
                    templateVars["varInput"] = 'How Many WWPN Addresses should be added to the Pool?  Range is 1-1000.'
                    templateVars["varDefault"] = 1000
                    templateVars["varName"] = 'Pool Size'
                    templateVars["minNum"] = jsonVars['Size']['minimum']
                    templateVars["maxNum"] = jsonVars['Size']['maximum']
                    pool_size = varNumberLoop(**templateVars)

                    if re.search('[a-z]', pool_from):
                        pool_from = pool_from.upper()
                    beginx = int(pool_from.replace(':', ''), 16)
                    add_dec = (beginx + int(pool_size) - 1)
                    pool_to = ':'.join(['{}{}'.format(a, b)
                        for a, b
                        in zip(*[iter('{:012x}'.format(add_dec))]*2)])
                    pool_to = pool_to.upper()

                    templateVars["wwpn_blocks"] = [
                        {
                            'from':pool_from,
                            'size':pool_size,
                            'to':pool_to
                        }
                    ]

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'    assignment_order = "{templateVars["assignment_order"]}"')
                    print(f'    description      = "{templateVars["descr"]}"')
                    print(f'    name             = "{templateVars["name"]}"')
                    print(f'    id_blocks = ''{')
                    for item in templateVars["wwpn_blocks"]:
                        print('      "0" = {')
                        for k, v in item.items():
                            if k == 'from':
                                print(f'        from = "{v}" ')
                            elif k == 'size':
                                print(f'        size = {v}')
                            elif k == 'to':
                                print(f'        to   = "{v}"')
                        print('      }')
                    print(f'    ''}')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                        if confirm_policy == 'Y' or confirm_policy == '':
                            confirm_policy = 'Y'

                            # Write Policies to Template File
                            templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
                            write_to_template(self, **templateVars)

                            configure_loop, loop_count, policy_loop = exit_loop_default_yes(loop_count, policy_type)
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
        templateVars["template_file"] = 'template_close.jinja2'
        write_to_template(self, **templateVars)
