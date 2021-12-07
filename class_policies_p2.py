#!/usr/bin/env python3

import jinja2
import os
import pkg_resources
import re
import stdiomask
import validating
from easy_functions import exit_default_no, exit_default_yes
from easy_functions import policy_descr, policy_name
from easy_functions import ntp_alternate, ntp_primary
from easy_functions import snmp_trap_servers, snmp_users
from easy_functions import syslog_servers
from easy_functions import variablesFromAPI
from easy_functions import varStringLoop
from easy_functions import write_to_template

ucs_template_path = pkg_resources.resource_filename('class_policies_p2', 'Templates/')

class policies_p2(object):
    def __init__(self, name_prefix, org, type):
        self.templateLoader = jinja2.FileSystemLoader(
            searchpath=(ucs_template_path + '%s/') % (type))
        self.templateEnv = jinja2.Environment(loader=self.templateLoader)
        self.name_prefix = name_prefix
        self.org = org
        self.type = type

    #==============================================
    # Network Connectivity Policy Module
    #==============================================
    def network_connectivity_policies(self, jsonData, easy_jsonData):
        name_prefix = self.name_prefix
        name_suffix = 'dns'
        org = self.org
        policy_type = 'Network Connectivity Policy'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'network_connectivity_policies'

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  It is strongly recommended to have a Network Connectivity (DNS) Policy for the')
            print(f'  UCS Domain Profile.  Without it, DNS resolution will fail.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - Intersight/{org}/{self.type}/{templateVars["template_type"]}.auto.tfvars')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            policy_loop = False
            while policy_loop == False:

                if not name_prefix == '':
                    name = '%s_%s' % (name_prefix, name_suffix)
                else:
                    name = '%s_%s' % (org, name_suffix)

                templateVars["name"] = policy_name(name, policy_type)
                templateVars["descr"] = policy_descr(templateVars["name"], policy_type)

                valid = False
                while valid == False:
                    templateVars["preferred_ipv4_dns_server"] = input('What is your Primary IPv4 DNS Server?  [208.67.220.220]: ')
                    if templateVars["preferred_ipv4_dns_server"] == '':
                        templateVars["preferred_ipv4_dns_server"] = '208.67.220.220'
                    valid = validating.ip_address('Primary IPv4 DNS Server', templateVars["preferred_ipv4_dns_server"])

                valid = False
                while valid == False:
                    alternate_true = input('Do you want to Configure an Alternate IPv4 DNS Server?  Enter "Y" or "N" [Y]: ')
                    if alternate_true == 'Y' or alternate_true == '':
                        templateVars["alternate_ipv4_dns_server"] = input('What is your Alternate IPv4 DNS Server?  [208.67.222.222]: ')
                        if templateVars["alternate_ipv4_dns_server"] == '':
                            templateVars["alternate_ipv4_dns_server"] = '208.67.222.222'
                        valid = validating.ip_address('Alternate IPv4 DNS Server', templateVars["alternate_ipv4_dns_server"])
                    elif alternate_true == 'N':
                        templateVars["alternate_ipv4_dns_server"] = ''
                        valid = True
                    else:
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                        print(f'\n-------------------------------------------------------------------------------------------\n')

                valid = False
                while valid == False:
                    enable_ipv6 = input('Do you want to Configure IPv6 DNS?  Enter "Y" or "N" [N]: ')
                    if enable_ipv6 == 'Y':
                        templateVars["enable_ipv6"] = True
                        templateVars["preferred_ipv6_dns_server"] = input('What is your Primary IPv6 DNS Server?  [2620:119:35::35]: ')
                        if templateVars["preferred_ipv6_dns_server"] == '':
                            templateVars["preferred_ipv6_dns_server"] = '2620:119:35::35'
                        valid = validating.ip_address('Primary IPv6 DNS Server', templateVars["preferred_ipv6_dns_server"])
                    if enable_ipv6 == 'N' or enable_ipv6 == '':
                        templateVars["enable_ipv6"] = False
                        templateVars["preferred_ipv6_dns_server"] = ''
                        valid = True

                valid = False
                while valid == False:
                    if enable_ipv6 == 'Y':
                        alternate_true = input('Do you want to Configure an Alternate IPv6 DNS Server?  Enter "Y" or "N" [Y]: ')
                        if alternate_true == 'Y' or alternate_true == '':
                            templateVars["alternate_ipv6_dns_server"] = input('What is your Alternate IPv6 DNS Server?  [2620:119:53::53]: ')
                            if templateVars["alternate_ipv6_dns_server"] == '':
                                templateVars["alternate_ipv6_dns_server"] = '2620:119:53::53'
                            valid = validating.ip_address('Alternate IPv6 DNS Server', templateVars["alternate_ipv6_dns_server"])
                        elif alternate_true == 'N':
                            templateVars["alternate_ipv6_dns_server"] = ''
                            valid = True
                        else:
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                    else:
                        templateVars["alternate_ipv6_dns_server"] = ''
                        valid = True

                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'    description = "{templateVars["descr"]}"')
                print(f'    name        = "{templateVars["name"]}"')
                if not templateVars["preferred_ipv4_dns_server"] == '':
                    print(f'    dns_servers_v4 = [')
                    print(f'      {templateVars["preferred_ipv4_dns_server"]},')
                    if not templateVars["alternate_ipv4_dns_server"] == '':
                        print(f'      {templateVars["alternate_ipv4_dns_server"]}')
                    print(f'    ]')
                if not templateVars["preferred_ipv6_dns_server"] == '':
                    print(f'    dns_servers_v6 = [')
                    print(f'      {templateVars["preferred_ipv6_dns_server"]},')
                    if not templateVars["alternate_ipv6_dns_server"] == '':
                        print(f'      {templateVars["alternate_ipv6_dns_server"]}')
                    print(f'    ]')
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

        # Close the Template file
        templateVars["template_file"] = 'template_close.jinja2'
        write_to_template(self, **templateVars)

    #==============================================
    # NTP Policy Module
    #==============================================
    def ntp_policies(self, jsonData, easy_jsonData):
        name_prefix = self.name_prefix
        name_suffix = 'ntp'
        org = self.org
        policy_type = 'NTP Policy'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'ntp_policies'

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  It is strongly recommended to configure an NTP Policy for the UCS Domain Profile.')
            print(f'  Without an NTP Policy Events can be incorrectly timestamped and Intersight ')
            print(f'  Communication, as an example, could be interrupted with Certificate Validation\n')
            print(f'  checks, as an example.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - Intersight/{org}/{self.type}/{templateVars["template_type"]}.auto.tfvars')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            policy_loop = False
            while policy_loop == False:

                if not name_prefix == '':
                    name = '%s_%s' % (name_prefix, name_suffix)
                else:
                    name = '%s_%s' % (org, name_suffix)

                templateVars["name"] = policy_name(name, policy_type)
                templateVars["descr"] = policy_descr(templateVars["name"], policy_type)

                primary_ntp = ntp_primary()
                alternate_ntp = ntp_alternate()

                templateVars["enabled"] = True
                templateVars["ntp_servers"] = []
                templateVars["ntp_servers"].append(primary_ntp)
                if not alternate_ntp == '':
                    templateVars["ntp_servers"].append(alternate_ntp)

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

                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'    description = "{templateVars["descr"]}"')
                print(f'    name        = "{templateVars["name"]}"')
                print(f'    timezone    = "{templateVars["timezone"]}"')
                if len(templateVars["ntp_servers"]) > 0:
                    print(f'    ntp_servers = [')
                    for server in templateVars["ntp_servers"]:
                        print(f'      "{server}",')
                    print(f'    ]')
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

        # Close the Template file
        templateVars["template_file"] = 'template_close.jinja2'
        write_to_template(self, **templateVars)

    #==============================================
    # Persistent Memory Policy Module
    #==============================================
    def persistent_memory_policies(self, jsonData, easy_jsonData):
        name_prefix = self.name_prefix
        name_suffix = 'persistent_memory'
        org = self.org
        policy_type = 'Persistent Memory Policy'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'persistent_memory_policies'

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  A {policy_type} allows the configuration of security, Goals, and ')
            print(f'  Namespaces of Persistent Memory Modules:')
            print(f'  - Goal - Used to configure volatile memory and regions in all the PMem Modules connected ')
            print(f'    to all the sockets of the server. Intersight supports only the creation and modification')
            print(f'    of a Goal as part of the Persistent Memory policy. Some data loss occurs when a Goal is')
            print(f'    modified during the creation or modification of a Persistent Memory Policy.')
            print(f'  - Namespaces - Used to partition a region mapped to a specific socket or a PMem Module on a')
            print(f'    socket.  Intersight supports only the creation and deletion of Namespaces as part of the ')
            print(f'    Persistent Memory Policy. Modifying a Namespace is not supported. Some data loss occurs ')
            print(f'    when a Namespace is created or deleted during the creation of a Persistent Memory policy.')
            print(f'    It is important to consider the memory performance guidelines and population rules of ')
            print(f'    the Persistent Memory Modules before they are installed or replaced, and the policy is ')
            print(f'    deployed. The population guidelines for the PMem Modules can be divided into the  ')
            print(f'    following categories, based on the number of CPU sockets:')
            print(f'    * Dual CPU for UCS B200 M6, C220 M6, C240 M6, and xC210 M6 servers')
            print(f'    * Dual CPU for UCS C220 M5, C240 M5, and B200 M5 servers')
            print(f'    * Dual CPU for UCS S3260 M5 servers')
            print(f'    * Quad CPU for UCS C480 M5 and B480 M5 servers')
            print(f'  - Security - Used to configure the secure passphrase for all the persistent memory modules.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - Intersight/{org}/{self.type}/{templateVars["template_type"]}.auto.tfvars')
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
                    jsonVars = jsonData['components']['schemas']['memory.PersistentMemoryPolicy']['allOf'][1]['properties']
                    templateVars["var_description"] = jsonVars['ManagementMode']['description']
                    templateVars["jsonVars"] = sorted(jsonVars['ManagementMode']['enum'])
                    templateVars["defaultVar"] = jsonVars['ManagementMode']['default']
                    templateVars["varType"] = 'Management Mode'
                    templateVars["management_mode"] = variablesFromAPI(**templateVars)

                    if templateVars["management_mode"] == 'configured-from-intersight':
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        print(f'  A Secure passphrase will enable the protection of data on the persistent memory modules. ')
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        valid = False
                        while valid == False:
                            encrypt_memory = input('Do you want to enable a secure passphrase?  Enter "Y" or "N" [Y]: ')
                            if encrypt_memory == 'Y' or encrypt_memory == '':
                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                print(f'  The Passphrase must be between 8 and 32 characters in length.  The allowed characters are:')
                                print(f'   - a-z, A-Z, 0-9 and special characters: \u0021, &, #, $, %, +, ^, @, _, *, -.')
                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                valid_passphrase = False
                                while valid_passphrase == False:
                                    secure_passphrase = stdiomask.getpass(prompt='Enter the Secure Passphrase: ')
                                    templateVars["minLength"] = 8
                                    templateVars["maxLength"] = 32
                                    templateVars["rePattern"] = '^[a-zA-Z0-9\\u0021\\&\\#\\$\\%\\+\\%\\@\\_\\*\\-\\.]+$'
                                    templateVars["varName"] = 'Secure Passphrase'
                                    varValue = secure_passphrase
                                    valid_passphrase = validating.length_and_regex_sensitive(templateVars["rePattern"],
                                        templateVars["varName"],
                                        varValue,
                                        templateVars["minLength"],
                                        templateVars["maxLength"]
                                    )

                                os.environ['TF_VAR_secure_passphrase'] = '%s' % (secure_passphrase)
                                valid = True
                            else:
                                valid = True

                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        print(f'  The percentage of volatile memory required for goal creation.')
                        print(f'  The actual volatile and persistent memory size allocated to the region may differ with')
                        print(f'  the given percentage.')
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        valid = False
                        while valid == False:
                            templateVars["memory_mode_percentage"] = input('What is the Percentage of Valatile Memory to assign to this Policy?  [0]: ')
                            if templateVars["memory_mode_percentage"] == '':
                                templateVars["memory_mode_percentage"] = 0
                            if re.search(r'[\d]+', str(templateVars["memory_mode_percentage"])):
                                valid = validating.number_in_range('Memory Mode Percentage', templateVars["memory_mode_percentage"], 1, 100)
                            else:
                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                print(f'  "{templateVars["memory_mode_percentage"]}" is not a valid number.')
                                print(f'\n-------------------------------------------------------------------------------------------\n')

                        jsonVars = jsonData['components']['schemas']['memory.PersistentMemoryGoal']['allOf'][1]['properties']
                        templateVars["var_description"] = jsonVars['PersistentMemoryType']['description']
                        templateVars["jsonVars"] = sorted(jsonVars['PersistentMemoryType']['enum'])
                        templateVars["defaultVar"] = jsonVars['PersistentMemoryType']['default']
                        templateVars["varType"] = 'Persistent Memory Type'
                        templateVars["persistent_memory_type"] = variablesFromAPI(**templateVars)

                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        print(f'  This Flag will enable or Disable the retention of Namespaces between Server Profile')
                        print(f'  association and dissassociation.')
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        valid = False
                        while valid == False:
                            templateVars["retain_namespaces"] = input('Do you want to Retain Namespaces?  Enter "Y" or "N" [Y]: ')
                            if templateVars["retain_namespaces"] == '' or templateVars["retain_namespaces"] == 'Y':
                                templateVars["retain_namespaces"] = True
                                valid = True
                            elif templateVars["retain_namespaces"] == 'N':
                                templateVars["retain_namespaces"] = False
                                valid = True
                            else:
                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                                print(f'\n-------------------------------------------------------------------------------------------\n')

                        templateVars["namespaces"] = []
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        print(f'  Namespace is a partition made in one or more Persistent Memory Regions. You can create a')
                        print(f'  namespace in Raw or Block mode.')
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        namespace_configure = input(f'Do You Want to Configure a namespace?  Enter "Y" or "N" [Y]: ')
                        if namespace_configure == 'Y' or namespace_configure == '':
                            sub_loop = False
                            while sub_loop == False:
                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                print(f'  Name of this Namespace to be created on the server.')
                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                valid = False
                                while valid == False:
                                    namespace_name = input('What is the Name for this Namespace? ')
                                    templateVars["minLength"] = 1
                                    templateVars["maxLength"] = 63
                                    templateVars["rePattern"] = '^[a-zA-Z0-9\\#\\_\\-]+$'
                                    templateVars["varName"] = 'Name for the Namespace'
                                    varValue = namespace_name
                                    valid = validating.length_and_regex(templateVars["rePattern"], templateVars["varName"], varValue, templateVars["minLength"], templateVars["maxLength"])

                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                print(f'  Capacity of this Namespace in gibibytes (GiB).  Range is 1-9223372036854775807')
                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                valid = False
                                while valid == False:
                                    capacity = input('What is the Capacity to assign to this Namespace? ')
                                    templateVars["minNum"] = 1
                                    templateVars["maxNum"] = 9223372036854775807
                                    templateVars["varName"] = 'Namespace Capacity'
                                    varValue = int(capacity)
                                    if re.search(r'[\d]+',str(varValue)):
                                        valid = validating.number_in_range(templateVars["varName"], varValue, templateVars["minNum"], templateVars["maxNum"])
                                    else:
                                        print(f'\n-------------------------------------------------------------------------------------------\n')
                                        print(f'  "{varValue}" is not a valid number.')
                                        print(f'\n-------------------------------------------------------------------------------------------\n')

                                jsonVars = jsonData['components']['schemas']['memory.PersistentMemoryLogicalNamespace']['allOf'][1]['properties']
                                templateVars["var_description"] = jsonVars['Mode']['description']
                                templateVars["jsonVars"] = sorted(jsonVars['Mode']['enum'])
                                templateVars["defaultVar"] = jsonVars['Mode']['default']
                                templateVars["varType"] = 'Mode'
                                mode = variablesFromAPI(**templateVars)

                                templateVars["var_description"] = jsonVars['SocketId']['description']
                                templateVars["jsonVars"] = sorted(jsonVars['SocketId']['enum'])
                                templateVars["defaultVar"] = jsonVars['SocketId']['default']
                                templateVars["varType"] = 'Socket Id'
                                socket_id = variablesFromAPI(**templateVars)

                                if templateVars["persistent_memory_type"] == 'app-direct-non-interleaved':
                                    templateVars["var_description"] = jsonVars['SocketMemoryId']['description']
                                    templateVars["jsonVars"] = [x for x in jsonVars['SocketMemoryId']['enum']]
                                    templateVars["defaultVar"] = '2'
                                    templateVars["popList"] = ['Not Applicable']
                                    templateVars["varType"] = 'Socket Memory Id'
                                    socket_memory_id = variablesFromAPI(**templateVars)
                                else:
                                    socket_memory_id = 'Not Applicable'

                                namespace = {
                                    'capacity':capacity,
                                    'mode':mode,
                                    'name':namespace_name,
                                    'socket_id':socket_id,
                                    'socket_memory_id':socket_memory_id
                                }
                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                print(f'   capacity         = "{capacity}"')
                                print(f'   mode             = "{mode}"')
                                print(f'   name             = "{namespace_name}"')
                                print(f'   socket_id        = "{socket_id}"')
                                print(f'   socket_memory_id = "{socket_memory_id}"')
                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                valid_confirm = False
                                while valid_confirm == False:
                                    confirm_namespace = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                                    if confirm_namespace == 'Y' or confirm_namespace == '':
                                        templateVars["namespaces"].append(namespace)

                                        valid_exit = False
                                        while valid_exit == False:
                                            sub_exit = input(f'Would You like to Configure another namespace?  Enter "Y" or "N" [N]: ')
                                            if sub_exit == 'Y':
                                                valid_confirm = True
                                                valid_exit = True
                                            elif sub_exit == 'N' or sub_exit == '':
                                                sub_loop = True
                                                valid = True
                                                valid_confirm = True
                                                valid_exit = True
                                            else:
                                                print(f'\n------------------------------------------------------\n')
                                                print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                                                print(f'\n------------------------------------------------------\n')

                                    elif confirm_namespace == 'N':
                                        print(f'\n-------------------------------------------------------------------------------------------\n')
                                        print(f'  Starting namespace Configuration Over.')
                                        print(f'\n-------------------------------------------------------------------------------------------\n')
                                        valid_confirm = True
                                    else:
                                        print(f'\n------------------------------------------------------\n')
                                        print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                                        print(f'\n------------------------------------------------------\n')

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'    description     = "{templateVars["descr"]}"')
                    print(f'    management_mode = "{templateVars["management_mode"]}"')
                    print(f'    name            = "{templateVars["name"]}"')
                    if templateVars["management_mode"]  == 'configured-from-intersight':
                        print(f'    # GOALS')
                        print(f'    memory_mode_percentage = {templateVars["memory_mode_percentage"]}')
                        print(f'    persistent_memory_type = {templateVars["persistent_memory_type"]}')
                        print(f'    # NAMESPACES')
                        print(f'    namespaces = ''{')
                        for item in templateVars["namespaces"]:
                            for k, v in item.items():
                                if k == 'name':
                                    print(f'      "{v}" = ''{')
                            for k, v in item.items():
                                if k == 'capacity':
                                    print(f'        capacity         = {v}')
                                elif k == 'mode':
                                    print(f'        mode             = {v}')
                                elif k == 'socket_id':
                                    print(f'        socket_id        = {v}')
                                elif k == 'socket_memory_id':
                                    print(f'        socket_memory_id = {v}')
                            print(f'      ''}')
                        print(f'    ''}')
                        print(f'   retain_namespaces = "{templateVars["retain_namespaces"]}"')
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
    # Power Policy Module
    #==============================================
    def power_policies(self, jsonData, easy_jsonData):
        name_prefix = self.name_prefix
        org = self.org
        policy_type = 'Power Policy'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'power_policies'

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  A {policy_type} will configure the Power Redundancy Policies for Chassis and Servers.')
            print(f'  For Servers it will configure the Power Restore State.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - Intersight/{org}/{self.type}/{templateVars["template_type"]}.auto.tfvars')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            loop_count = 1
            policy_loop = False
            while policy_loop == False:

                print('staring loop again')
                templateVars["multi_select"] = False
                templateVars["var_description"] = easy_jsonData['policies']['power.Policy']['systemType']['description']
                templateVars["jsonVars"] = sorted(easy_jsonData['policies']['power.Policy']['systemType']['enum'])
                templateVars["defaultVar"] = easy_jsonData['policies']['power.Policy']['systemType']['default']
                templateVars["varType"] = 'System Type'
                system_type = variablesFromAPI(**templateVars)

                if not name_prefix == '':
                    name = '%s_%s' % (name_prefix, system_type)
                else:
                    name = '%s_%s' % (org, system_type)

                templateVars["name"] = policy_name(name, policy_type)
                templateVars["descr"] = policy_descr(templateVars["name"], policy_type)

                if system_type == '9508':
                    valid = False
                    while valid == False:
                        templateVars["allocated_budget"] = input('What is the Power Budget you would like to Apply?\n'
                            'This should be a value between 2800 Watts and 16800 Watts. [5600]: ')
                        if templateVars["allocated_budget"] == '':
                            templateVars["allocated_budget"] = 5600
                        valid = validating.number_in_range('Chassis Power Budget', templateVars["allocated_budget"], 2800, 16800)
                else:
                    templateVars["allocated_budget"] = 0

                templateVars["multi_select"] = False
                jsonVars = jsonData['components']['schemas']['power.Policy']['allOf'][1]['properties']

                if system_type == 'Server':
                    templateVars["var_description"] = jsonVars['PowerRestoreState']['description']
                    templateVars["jsonVars"] = sorted(jsonVars['PowerRestoreState']['enum'])
                    templateVars["defaultVar"] = jsonVars['PowerRestoreState']['default']
                    templateVars["varType"] = 'Power Restore State'
                    templateVars["power_restore_state"] = variablesFromAPI(**templateVars)

                if system_type == '5108':
                    templateVars["popList"] = ['N+2']
                elif system_type == 'Server':
                    templateVars["popList"] = ['N+1','N+2']
                templateVars["var_description"] = jsonVars['RedundancyMode']['description']
                templateVars["jsonVars"] = sorted(jsonVars['RedundancyMode']['enum'])
                templateVars["defaultVar"] = jsonVars['RedundancyMode']['default']
                templateVars["varType"] = 'Power Redundancy Mode'
                templateVars["power_redundancy"] = variablesFromAPI(**templateVars)

                print(f'\n-------------------------------------------------------------------------------------------\n')
                if system_type == '9508':
                    print(f'   allocated_budget    = {templateVars["allocated_budget"]}')
                print(f'   description         = "{templateVars["descr"]}"')
                print(f'   name                = "{templateVars["name"]}"')
                if system_type == 'Server':
                    print(f'   power_restore_state = "{templateVars["power_restore_state"]}"')
                print(f'   redundancy_mode     = "{templateVars["power_redundancy"]}"')
                print(f'\n-------------------------------------------------------------------------------------------\n')
                valid_confirm = False
                while valid_confirm == False:
                    confirm_policy = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                    if confirm_policy == 'Y' or confirm_policy == '':
                        confirm_policy = 'Y'

                        # Write Policies to Template File
                        templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
                        write_to_template(self, **templateVars)

                        if loop_count < 3:
                            configure_loop, policy_loop = exit_default_yes(templateVars["policy_type"])
                        else:
                            configure_loop, policy_loop = exit_default_no(templateVars["policy_type"])
                        loop_count += 1
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

        # Close the Template file
        templateVars["template_file"] = 'template_close.jinja2'
        write_to_template(self, **templateVars)

    #==============================================
    # SD Card Policy Module
    #==============================================
    def sd_card_policies(self, jsonData, easy_jsonData):
        name_prefix = self.name_prefix
        name_suffix = 'sdcard'
        org = self.org
        policy_type = 'SD Card Policy'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'sd_card_policies'

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
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

                    templateVars["priority"] = 'auto'
                    templateVars["receive"] = 'Disabled'
                    templateVars["send"] = 'Disabled'

                    # Write Policies to Template File
                    templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
                    write_to_template(self, **templateVars)

                    exit_answer = input(f'Would You like to Configure another {policy_type}?  Enter "Y" or "N" [N]: ')
                    if exit_answer == 'N' or exit_answer == '':
                        policy_loop = True
                        configure_loop = True
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
    # Serial over LAN Policy Module
    #==============================================
    def serial_over_lan_policies(self, jsonData, easy_jsonData):
        name_prefix = self.name_prefix
        name_suffix = 'sol'
        org = self.org
        policy_type = 'Serial over LAN Policy'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'serial_over_lan_policies'

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  A {policy_type} will configure the Server to allow access to the Communications Port over')
            print(f'  Ethernet.  Settings include:')
            print(f'   - Baud Rate')
            print(f'   - COM Port')
            print(f'   - SSH Port\n')
            print(f'  This Policy is not required to standup a server but is a good practice for day 2 support.')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - Intersight/{org}/{self.type}/{templateVars["template_type"]}.auto.tfvars')
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
                    templateVars["enabled"] = True

                    templateVars["multi_select"] = False
                    jsonVars = jsonData['components']['schemas']['sol.Policy']['allOf'][1]['properties']
                    templateVars["var_description"] = jsonVars['BaudRate']['description']
                    templateVars["jsonVars"] = sorted(jsonVars['BaudRate']['enum'])
                    templateVars["defaultVar"] = jsonVars['BaudRate']['default']
                    templateVars["varType"] = 'Baud Rate'
                    templateVars["baud_rate"] = variablesFromAPI(**templateVars)

                    templateVars["var_description"] = jsonVars['ComPort']['description']
                    templateVars["jsonVars"] = sorted(jsonVars['ComPort']['enum'])
                    templateVars["defaultVar"] = jsonVars['ComPort']['default']
                    templateVars["varType"] = 'Com Port'
                    templateVars["com_port"] = variablesFromAPI(**templateVars)

                    valid = False
                    while valid == False:
                        templateVars["ssh_port"] = input('What is the SSH Port you would like to assign?\n'
                            'This should be a value between 1024-65535. [2400]: ')
                        if templateVars["ssh_port"] == '':
                            templateVars["ssh_port"] = 2400
                        valid = validating.number_in_range('SSH Port', templateVars["ssh_port"], 1024, 65535)

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'   baud_rate   = "{templateVars["baud_rate"]}"')
                    print(f'   com_port    = "{templateVars["com_port"]}"')
                    print(f'   description = "{templateVars["descr"]}"')
                    print(f'   enabled     = "{templateVars["enabled"]}"')
                    print(f'   name        = "{templateVars["name"]}"')
                    print(f'   ssh_port    = "{templateVars["ssh_port"]}"')
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
    # SMTP Policy Module
    #==============================================
    def smtp_policies(self, jsonData, easy_jsonData):
        name_prefix = self.name_prefix
        name_suffix = 'smtp'
        org = self.org
        policy_type = 'SMTP Policy'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'smtp_policies'

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  An {policy_type} sends server faults as email alerts to the configured SMTP server.')
            print(f'  You can specify the preferred settings for outgoing communication and select the fault ')
            print(f'  severity level to report and the mail recipients.\n\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - Intersight/{org}/{self.type}/{templateVars["template_type"]}.auto.tfvars')
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
                    templateVars["enable_smtp"] = True

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  IP address or hostname of the SMTP server. The SMTP server is used by the managed device ')
                    print(f'  to send email notifications.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid = False
                    while valid == False:
                        templateVars["smtp_server_address"] = input('What is the SMTP Server Address? ')
                        if re.search(r'^[a-zA-Z0-9]:', templateVars["smtp_server_address"]):
                            valid = validating.ip_address('SMTP Server Address', templateVars["smtp_server_address"])
                        if re.search(r'[a-zA-Z]', templateVars["smtp_server_address"]):
                            valid = validating.dns_name('SMTP Server Address', templateVars["smtp_server_address"])
                        elif re.search (r'^([0-9]{1,3}\.){3}[0-9]{1,3}$'):
                            valid = validating.ip_address('SMTP Server Address', templateVars["smtp_server_address"])
                        else:
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            print(f'  "{templateVars["smtp_server_address"]}" is not a valid address.')
                            print(f'\n-------------------------------------------------------------------------------------------\n')

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  Port number used by the SMTP server for outgoing SMTP communication.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid = False
                    while valid == False:
                        templateVars["smtp_port"] = input('What is the SMTP Port?  [25]: ')
                        if templateVars["smtp_port"] == '':
                            templateVars["smtp_port"] = 25
                        if re.search(r'[\d]+', str(templateVars["smtp_port"])):
                            valid = validating.number_in_range('SMTP Port', templateVars["smtp_port"], 1, 65535)
                        else:
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            print(f'  "{templateVars["smtp_port"]}" is not a valid port.')
                            print(f'\n-------------------------------------------------------------------------------------------\n')

                    templateVars["multi_select"] = False
                    jsonVars = jsonData['components']['schemas']['smtp.Policy']['allOf'][1]['properties']
                    templateVars["var_description"] = jsonVars['MinSeverity']['description']
                    templateVars["jsonVars"] = sorted(jsonVars['MinSeverity']['enum'])
                    templateVars["defaultVar"] = jsonVars['MinSeverity']['default']
                    templateVars["varType"] = 'Minimum Severity'
                    templateVars["minimum_severity"] = variablesFromAPI(**templateVars)

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  The email address entered here will be displayed as the from address (mail received from ')
                    print(f'  address) of all the SMTP mail alerts that are received. If not configured, the hostname ')
                    print(f'  of the server is used in the from address field.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid = False
                    while valid == False:
                        templateVars["smtp_alert_sender_address"] = input(f'What is the SMTP Alert Sender Address?  '\
                            '[press enter to use server hostname]: ')
                        if templateVars["smtp_alert_sender_address"] == '':
                            templateVars["smtp_alert_sender_address"] = ''
                            valid = True
                        else:
                            valid = validating.email('SMTP Alert Sender Address', templateVars["smtp_alert_sender_address"])

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  List of email addresses that will receive notifications for faults.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    templateVars["mail_alert_recipients"] = []
                    valid = False
                    while valid == False:
                        mail_recipient = input(f'What is address you would like to send these notifications to?  ')
                        valid_email = validating.email('Mail Alert Recipient', mail_recipient)
                        if valid_email == True:
                            templateVars["mail_alert_recipients"].append(mail_recipient)
                            valid_answer = False
                            while valid_answer == False:
                                add_another = input(f'Would you like to add another E-mail?  Enter "Y" or "N" [N]: ')
                                if add_another == '' or add_another == 'N':
                                    valid = True
                                    valid_answer = True
                                elif add_another == 'Y':
                                    valid_answer = True
                                else:
                                    print(f'\n-------------------------------------------------------------------------------------------\n')
                                    print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                                    print(f'\n-------------------------------------------------------------------------------------------\n')

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'    description               = "{templateVars["descr"]}"')
                    print(f'    enable_smtp                   = {templateVars["enable_smtp"]}')
                    print(f'    mail_alert_recipients     = [')
                    for x in templateVars["mail_alert_recipients"]:
                        print(f'      "{x}",')
                    print(f'    ]')
                    print(f'    minimum_severity          = "{templateVars["minimum_severity"]}"')
                    print(f'    name                      = "{templateVars["name"]}"')
                    print(f'    smtp_alert_sender_address = "{templateVars["smtp_alert_sender_address"]}"')
                    print(f'    smtp_port                 = {templateVars["smtp_port"]}')
                    print(f'    smtp_server_address       = "{templateVars["smtp_server_address"]}"')
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
    # SNMP Policy Module
    #==============================================
    def snmp_policies(self, jsonData, easy_jsonData):
        name_prefix = self.name_prefix
        name_suffix = 'snmp'
        org = self.org
        policy_type = 'SNMP Policy'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'snmp_policies'

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  An {policy_type} will configure chassis, domains, and servers with SNMP parameters.')
            print(f'  This Policy is not required to standup a server but is a good practice for day 2 support.')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - Intersight/{org}/{self.type}/{templateVars["template_type"]}.auto.tfvars')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure an {policy_type}?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                loop_count = 1
                policy_loop = False
                while policy_loop == False:

                    if not name_prefix == '':
                        name = '%s_%s' % (name_prefix, name_suffix)
                    else:
                        name = '%s_%s' % (org, name_suffix)

                    templateVars["name"] = policy_name(name, policy_type)
                    templateVars["descr"] = policy_descr(templateVars["name"], policy_type)
                    templateVars["enabled"] = True

                    valid = False
                    while valid == False:
                        templateVars["port"] = input(f'Note: The following Ports cannot be chosen: [22, 23, 80, 123, 389, 443, 623, 636, 2068, 3268, 3269]\n'\
                            'Enter the Port to Assign to this SNMP Policy.  Valid Range is 1-65535.  [161]: ')
                        if templateVars["port"] == '':
                            templateVars["port"] = 161
                        if re.search(r'[0-9]{1,4}', str(templateVars["port"])):
                            valid = validating.snmp_port('SNMP Port', templateVars["port"], 1, 65535)
                        else:
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            print(f'  Invalid Entry!  Please Enter a valid Port in the range of 1-65535.')
                            print(f'  Excluding [22, 23, 80, 123, 389, 443, 623, 636, 2068, 3268, 3269].')
                            print(f'\n-------------------------------------------------------------------------------------------\n')

                    templateVars["multi_select"] = False
                    jsonVars = jsonData['components']['schemas']['snmp.Policy']['allOf'][1]['properties']

                    # SNMP Contact
                    templateVars["Description"] = jsonVars['SysContact']['description']
                    templateVars["varDefault"] = 'UCS Admins'
                    templateVars["varInput"] = 'SNMP System Contact:'
                    templateVars["varName"] = 'SNMP System Contact'
                    templateVars["varRegex"] = '.*'
                    templateVars["minLength"] = 1
                    templateVars["maxLength"] = jsonVars['SysContact']['maxLength']
                    templateVars["system_contact"] = varStringLoop(**templateVars)

                    # SNMP Location
                    templateVars["Description"] = jsonVars['SysLocation']['description']
                    templateVars["varDefault"] = 'Data Center'
                    templateVars["varInput"] = 'What is the Location of the host on which the SNMP agent (server) runs?'
                    templateVars["varName"] = 'System Location'
                    templateVars["varRegex"] = '.*'
                    templateVars["minLength"] = 1
                    templateVars["maxLength"] = jsonVars['SysLocation']['maxLength']
                    templateVars["system_location"] = varStringLoop(**templateVars)

                    templateVars["access_community_string"] = ''
                    valid = False
                    while valid == False:
                        question = input(f'Would you like to configure an SNMP Access Community String?  Enter "Y" or "N" [N]: ')
                        if question == 'Y':
                            input_valid = False
                            while input_valid == False:
                                input_string = stdiomask.getpass(f'What is your SNMP Access Community String? ')
                                if not input_string == '':
                                    input_valid = validating.snmp_string('SNMP Access Community String', input_string)
                                else:
                                    print(f'\n-------------------------------------------------------------------------------------------\n')
                                    print(f'  Error!! Invalid Value.  Please Re-enter the SNMP Access Community String.')
                                    print(f'\n-------------------------------------------------------------------------------------------\n')
                            templateVars["access_community_string"] = loop_count
                            TF_VAR = 'TF_VAR_access_community_string_%s' % (loop_count)
                            os.environ[TF_VAR] = '%s' % (input_string)
                            valid = True
                        elif question == '' or question == 'N':
                            valid = True
                        else:
                            print(f'\n------------------------------------------------------\n')
                            print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                            print(f'\n------------------------------------------------------\n')

                    if not templateVars["access_community_string"] == '':
                        templateVars["var_description"] = jsonVars['CommunityAccess']['description']
                        templateVars["jsonVars"] = sorted(jsonVars['CommunityAccess']['enum'])
                        templateVars["defaultVar"] = jsonVars['CommunityAccess']['default']
                        templateVars["varType"] = 'Community Access'
                        templateVars["community_access"] = variablesFromAPI(**templateVars)
                    else:
                        templateVars["community_access"] = 'Disabled'

                    templateVars["trap_community_string"] = ''
                    valid = False
                    while valid == False:
                        question = input(f'Would you like to configure an SNMP Trap Community String?  Enter "Y" or "N" [N]: ')
                        if question == 'Y':
                            input_valid = False
                            while input_valid == False:
                                input_string = stdiomask.getpass(f'What is your SNMP Trap Community String? ')
                                if not input_string == '':
                                    input_valid = validating.snmp_string('SNMP Trap Community String', input_string)
                                else:
                                    print(f'\n-------------------------------------------------------------------------------------------\n')
                                    print(f'  Error!! Invalid Value.  Please Re-enter the SNMP Trap Community String.')
                                    print(f'\n-------------------------------------------------------------------------------------------\n')
                            templateVars["trap_community_string"] = loop_count
                            TF_VAR = 'TF_VAR_snmp_trap_community_%s' % (loop_count)
                            os.environ[TF_VAR] = '%s' % (input_string)
                            valid = True
                        elif question == '' or question == 'N':
                            valid = True
                        else:
                            print(f'\n------------------------------------------------------\n')
                            print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                            print(f'\n------------------------------------------------------\n')

                    templateVars["engine_input_id"] = ''
                    valid = False
                    while valid == False:
                        question = input(f'Note: By default this is derived from the BMC serial number.\n'\
                            'Would you like to configure a Unique string to identify the device for administration purpose?  Enter "Y" or "N" [N]: ')
                        if question == 'Y':
                            input_valid = False
                            while input_valid == False:
                                input_string = input(f'What is the SNMP Engine Input ID? ')
                                if not input_string == '':
                                    input_valid = validating.string_length('SNMP Engine Input ID', input_string, 1, 27)
                                else:
                                    print(f'\n-------------------------------------------------------------------------------------------\n')
                                    print(f'  Error!! Invalid Value.  Please Re-enter the SNMP Engine Input ID.')
                                    print(f'\n-------------------------------------------------------------------------------------------\n')
                            templateVars["snmp_engine_input_id"] = input_string
                            valid = True
                        elif question == '' or question == 'N':
                            valid = True
                        else:
                            print(f'\n------------------------------------------------------\n')
                            print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                            print(f'\n------------------------------------------------------\n')

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
                    if not templateVars["access_community_string"] == '':
                        print(f'    access_community_string = "Sensitive"')
                    print(f'    description             = "{templateVars["descr"]}"')
                    print(f'    enable_snmp             = {templateVars["enabled"]}')
                    print(f'    name                    = "{templateVars["name"]}"')
                    print(f'    snmp_community_access   = "{templateVars["community_access"]}"')
                    print(f'    snmp_engine_input_id    = "{templateVars["engine_input_id"]}"')
                    print(f'    snmp_port               = {templateVars["port"]}')
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
                                elif k == 'version':
                                    print(f'        snmp_server         = "{v}"')
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
                    if not templateVars["trap_community_string"] == '':
                        print(f'    trap_community_string   = "Sensitive"')
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
    # SSH Policy Module
    #==============================================
    def ssh_policies(self, jsonData, easy_jsonData):
        name_prefix = self.name_prefix
        name_suffix = 'ssh'
        org = self.org
        policy_type = 'SSH Policy'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'ssh_policies'

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  An {policy_type} enables an SSH client to make a secure, encrypted connection. You can ')
            print(f'  create one or more SSH policies that contain a specific grouping of SSH properties for a ')
            print(f'  server or a set of servers.\n\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - Intersight/{org}/{self.type}/{templateVars["template_type"]}.auto.tfvars')
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
                    templateVars["enable_ssh"] = True

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  Port used for secure shell access.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid = False
                    while valid == False:
                        templateVars["ssh_port"] = input('What is the SSH Port?  [22]: ')
                        if templateVars["ssh_port"] == '':
                            templateVars["ssh_port"] = 22
                        if re.search(r'[\d]+', str(templateVars["ssh_port"])):
                            valid = validating.number_in_range('SSH Port', templateVars["ssh_port"], 1, 65535)
                        else:
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            print(f'  "{templateVars["ssh_port"]}" is not a valid port.')
                            print(f'\n-------------------------------------------------------------------------------------------\n')

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  Number of seconds to wait before the system considers an SSH request to have timed out.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid = False
                    while valid == False:
                        templateVars["ssh_timeout"] = input('What value do you want to set for the SSH Timeout?  [1800]: ')
                        if templateVars["ssh_timeout"] == '':
                            templateVars["ssh_timeout"] = 1800
                        if re.search(r'[\d]+', str(templateVars["ssh_timeout"])):
                            valid = validating.number_in_range('SSH Timeout', templateVars["ssh_timeout"], 60, 10800)
                        else:
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            print(f'  "{templateVars["ssh_timeout"]}" is not a valid value.  Must be between 60 and 10800')
                            print(f'\n-------------------------------------------------------------------------------------------\n')


                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'    description = "{templateVars["descr"]}"')
                    print(f'    enable_ssh  = {templateVars["enable_ssh"]}')
                    print(f'    name        = "{templateVars["name"]}"')
                    print(f'    ssh_port    = {templateVars["ssh_port"]}')
                    print(f'    ssh_timeout = "{templateVars["ssh_timeout"]}"')
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
    # Storage Policy Module
    #==============================================
    def storage_policies(self, jsonData, easy_jsonData):
        name_prefix = self.name_prefix
        name_suffix = 'storage'
        org = self.org
        policy_type = 'Storage Policy'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'storage_policies'

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
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

                    templateVars["priority"] = 'auto'
                    templateVars["receive"] = 'Disabled'
                    templateVars["send"] = 'Disabled'

                    # Write Policies to Template File
                    templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
                    write_to_template(self, **templateVars)

                    exit_answer = input(f'Would You like to Configure another {policy_type}?  Enter "Y" or "N" [N]: ')
                    if exit_answer == 'N' or exit_answer == '':
                        policy_loop = True
                        configure_loop = True
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
    # Syslog Policy Module
    #==============================================
    def syslog_policies(self, jsonData, easy_jsonData):
        name_prefix = self.name_prefix
        name_suffix = 'syslog'
        org = self.org
        policy_type = 'Syslog Policy'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'syslog_policies'

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  A {policy_type} will configure domain and servers with remote syslog servers.')
            print(f'  You can configure up to two Remote Syslog Servers.')
            print(f'  This Policy is not required to standup a server but is a good practice for day 2 support.')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - Intersight/{org}/{self.type}/{templateVars["template_type"]}.auto.tfvars')
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

                    # Syslog Local Logging
                    templateVars["multi_select"] = False
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
                    print(f'    description        = "{templateVars["descr"]}"')
                    print(f'    local_min_severity = "{templateVars["min_severity"]}"')
                    print(f'    name               = "{templateVars["name"]}"')
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
    # Thermal Policy Module
    #==============================================
    def thermal_policies(self, jsonData, easy_jsonData):
        name_prefix = self.name_prefix
        org = self.org
        policy_type = 'Thermal Policy'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'thermal_policies'

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  A {policy_type} will configure the Cooling/FAN Policy for Chassis.  We recommend ')
            print(f'  Balanced for a 5108 and Acoustic for a 9508 Chassis, as of this writing.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - Intersight/{org}/{self.type}/{templateVars["template_type"]}.auto.tfvars')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            policy_loop = False
            while policy_loop == False:

                templateVars["multi_select"] = False
                jsonVars = easy_jsonData['policies']['thermal.Policy']
                templateVars["var_description"] = jsonVars['chassisType']['description']
                templateVars["jsonVars"] = sorted(jsonVars['chassisType']['enum'])
                templateVars["defaultVar"] = jsonVars['chassisType']['default']
                templateVars["varType"] = 'Chassis Type'
                templateVars["chassis_type"] = variablesFromAPI(**templateVars)

                if not name_prefix == '':
                    name = '%s_%s' % (name_prefix, templateVars["chassis_type"])
                else:
                    name = '%s_%s' % (org, templateVars["chassis_type"])

                templateVars["name"] = policy_name(name, policy_type)
                templateVars["descr"] = policy_descr(templateVars["name"], policy_type)

                if templateVars["chassis_type"] == '5108':
                    templateVars["popList"] = ['Acoustic', 'HighPower', 'MaximumPower']
                if templateVars["chassis_type"] == '9508':
                    templateVars["popList"] = []
                jsonVars = jsonData['components']['schemas']['thermal.Policy']['allOf'][1]['properties']
                templateVars["var_description"] = jsonVars['FanControlMode']['description']
                templateVars["jsonVars"] = sorted(jsonVars['FanControlMode']['enum'])
                templateVars["defaultVar"] = jsonVars['FanControlMode']['default']
                templateVars["varType"] = 'Fan Control Mode'
                templateVars["fan_control_mode"] = variablesFromAPI(**templateVars)

                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'   description      = "{templateVars["descr"]}"')
                print(f'   name             = "{templateVars["name"]}"')
                print(f'   fan_control_mode = "{templateVars["fan_control_mode"]}"')
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

        # Close the Template file
        templateVars["template_file"] = 'template_close.jinja2'
        write_to_template(self, **templateVars)

    #==============================================
    # Virtual KVM Policy Module
    #==============================================
    def virtual_kvm_policies(self, jsonData, easy_jsonData):
        name_prefix = self.name_prefix
        name_suffix = 'vkvm'
        org = self.org
        policy_type = 'Virtual KVM Policy'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'virtual_kvm_policies'

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  A {policy_type} will configure the Server for KVM access.  Settings include:')
            print(f'   - Local Server Video - If enabled, displays KVM on any monitor attached to the server.')
            print(f'   - Video Encryption - encrypts all video information sent through KVM.')
            print(f'   - Remote Port - The port used for KVM communication. Range is 1 to 65535.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - Intersight/{org}/{self.type}/{templateVars["template_type"]}.auto.tfvars')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            policy_loop = False
            while policy_loop == False:

                if not name_prefix == '':
                    name = '%s_%s' % (name_prefix, name_suffix)
                else:
                    name = '%s_%s' % (org, name_suffix)

                templateVars["name"] = policy_name(name, policy_type)
                templateVars["descr"] = policy_descr(templateVars["name"], policy_type)
                templateVars["enable_virtual_kvm"] = True
                templateVars["maximum_sessions"] = 4

                valid = False
                while valid == False:
                    local_video = input('Do you want to Display KVM on Monitors attached to the Server?  Enter "Y" or "N" [Y]: ')
                    if local_video == '' or local_video == 'Y':
                        templateVars["enable_local_server_video"] = True
                        valid = True
                    elif local_video == 'N':
                        templateVars["enable_local_server_video"] = False
                        valid = True
                    else:
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                        print(f'\n-------------------------------------------------------------------------------------------\n')

                valid = False
                while valid == False:
                    video_encrypt = input('Do you want to Enable video Encryption?  Enter "Y" or "N" [Y]: ')
                    if video_encrypt == '' or video_encrypt == 'Y':
                        templateVars["enable_video_encryption"] = True
                        valid = True
                    elif video_encrypt == 'N':
                        templateVars["enable_video_encryption"] = False
                        valid = True
                    else:
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                        print(f'\n-------------------------------------------------------------------------------------------\n')

                valid = False
                while valid == False:
                    templateVars["remote_port"] = input('What is the Port you would like to Assign for Remote Access?\n'
                        'This should be a value between 1024-65535. [2068]: ')
                    if templateVars["remote_port"] == '':
                        templateVars["remote_port"] = 2068
                    valid = validating.number_in_range('Remote Port', templateVars["remote_port"], 1, 65535)

                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'   description               = "{templateVars["descr"]}"')
                print(f'   enable_local_server_video = {templateVars["enable_local_server_video"]}')
                print(f'   enable_video_encryption   = {templateVars["enable_video_encryption"]}')
                print(f'   enable_virtual_kvm        = {templateVars["enable_virtual_kvm"]}')
                print(f'   maximum_sessions          = {templateVars["maximum_sessions"]}')
                print(f'   name                      = "{templateVars["name"]}"')
                print(f'   remote_port               = "{templateVars["remote_port"]}"')
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

        # Close the Template file
        templateVars["template_file"] = 'template_close.jinja2'
        write_to_template(self, **templateVars)

    #==============================================
    # Virtual Media Policy Policy Module
    #==============================================
    def virtual_media_policies(self, jsonData, easy_jsonData):
        name_prefix = self.name_prefix
        name_suffix = 'vmedia'
        org = self.org
        policy_type = 'Virtual Media Policy'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'virtual_media_policies'

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  A {policy_type} enables you to install an operating system on the server using the ')
            print(f'  KVM console and virtual media, mount files to the host from a remote file share, and ')
            print(f'  enable virtual media encryption. You can create one or more virtual media policies, which ')
            print(f'  could contain virtual media mappings for different OS images, and configure up to two ')
            print(f'  virtual media mappings, one for ISO files through CDD and the other for IMG files ')
            print(f'  through HDD.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - Intersight/{org}/{self.type}/{templateVars["template_type"]}.auto.tfvars')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure an {policy_type}?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                loop_count = 1
                policy_loop = False
                while policy_loop == False:

                    if not name_prefix == '':
                        name = '%s_%s' % (name_prefix, name_suffix)
                    else:
                        name = '%s_%s' % (org, name_suffix)

                    templateVars["name"] = policy_name(name, policy_type)
                    templateVars["descr"] = policy_descr(templateVars["name"], policy_type)
                    templateVars["enable_virtual_media"] = True

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'    Select this option to enable the appearance of virtual drives on the boot selection menu')
                    print(f'    after mapping the image and rebooting the host. This property is enabled by default.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid = False
                    while valid == False:
                        question = input(f'Do you want to Enable Low Power USB?  Enter "Y" or "N" [Y]: ')
                        if question == 'N':
                            templateVars["enable_low_power_usb"] = False
                            valid = True
                        elif question == '' or question == 'Y':
                            templateVars["enable_low_power_usb"] = True
                            valid = True
                        else:
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                            print(f'\n-------------------------------------------------------------------------------------------\n')

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'    Select this option to enable encryption of the virtual media communications. ')
                    print(f'    This property is enabled by default.')
                    print(f'    Note: For firmware versions 4.2(1a) or higher, this encryption parameter is deprecated ')
                    print(f'          and disabling the encryption will further result in validation failure during')
                    print(f'          the server profile deployment.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid = False
                    while valid == False:
                        question = input(f'Do you want to Enable Virtual Media Encryption?  Enter "Y" or "N" [Y]: ')
                        if question == 'N':
                            templateVars["enable_virtual_media_encryption"] = False
                            valid = True
                        elif question == '' or question == 'Y':
                            templateVars["enable_virtual_media_encryption"] = True
                            valid = True
                        else:
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                            print(f'\n-------------------------------------------------------------------------------------------\n')

                    templateVars["virtual_media"] = []
                    inner_loop_count = 1
                    sub_loop = False
                    while sub_loop == False:
                        question = input(f'\nWould you like to add vMedia to this Policy?  Enter "Y" or "N" [Y]: ')
                        if question == '' or question == 'Y':
                            valid_sub = False
                            while valid_sub == False:
                                templateVars["multi_select"] = False
                                jsonVars = jsonData['components']['schemas']['vmedia.Mapping']['allOf'][1]['properties']
                                templateVars["var_description"] = jsonVars['MountProtocol']['description']
                                templateVars["jsonVars"] = sorted(jsonVars['MountProtocol']['enum'])
                                templateVars["defaultVar"] = jsonVars['MountProtocol']['default']
                                templateVars["varType"] = 'vMedia Mount Protocol'
                                Protocol = variablesFromAPI(**templateVars)

                                templateVars["var_description"] = jsonVars['MountProtocol']['description']
                                templateVars["jsonVars"] = sorted(jsonVars['MountProtocol']['enum'])
                                templateVars["defaultVar"] = jsonVars['MountProtocol']['default']
                                templateVars["varType"] = 'vMedia Mount Protocol'
                                deviceType = variablesFromAPI(**templateVars)

                                if Protocol == 'cifs':
                                    templateVars["var_description"] = jsonVars['AuthenticationProtocol']['description']
                                    templateVars["jsonVars"] = sorted(jsonVars['AuthenticationProtocol']['enum'])
                                    templateVars["defaultVar"] = jsonVars['AuthenticationProtocol']['default']
                                    templateVars["varType"] = 'CIFS Authentication Protocol'
                                    authProtocol = variablesFromAPI(**templateVars)

                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                print(f'  Provide the remote file location path: Host Name or IP address/file path/file name')
                                print(f'  * IP Address—The IP address or the hostname of the remote server.')
                                print(f'  * File Path—The path to the location of the image on the remote server.')
                                print(f'  The format of the File Location should be:')
                                if deviceType == 'cdd' and re.search('(cifs|nfs)', Protocol):
                                    print(f'  * hostname-or-ip-address/filePath/fileName.iso')
                                elif deviceType == 'hdd' and re.search('(cifs|nfs)', Protocol):
                                    print(f'  * hostname-or-ip-address/filePath/fileName.img')
                                elif deviceType == 'cdd' and Protocol == 'http':
                                    print(f'  * http://hostname-or-ip-address/filePath/fileName.iso')
                                elif deviceType == 'hdd' and Protocol == 'http':
                                    print(f'  * http://hostname-or-ip-address/filePath/fileName.img')
                                elif deviceType == 'cdd' and Protocol == 'https':
                                    print(f'  * https://hostname-or-ip-address/filePath/fileName.iso')
                                elif deviceType == 'hdd' and Protocol == 'https':
                                    print(f'  * https://hostname-or-ip-address/filePath/fileName.img')
                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                valid = False
                                while valid == False:
                                    Question = input(f'What is the file Location? ')
                                    if not Question == '':
                                        templateVars["varName"] = 'File Location'
                                        varValue = Question
                                        if re.search('(http|https)', Protocol):
                                            valid = validating.url(templateVars["varName"], varValue)
                                        else:
                                            varValue = 'http://%s' % (Question)
                                            valid = validating.url(templateVars["varName"], varValue)
                                    else:
                                        print(f'\n-------------------------------------------------------------------------------------------\n')
                                        print(f'  Error!! Invalid Value.  Please Re-enter the LDAP Group.')
                                        print(f'\n-------------------------------------------------------------------------------------------\n')

                                # Assign the Variable
                                file_location = Question

                                valid = False
                                while valid == False:
                                    Question = input(f'What is the Username you would like to configure for Authentication? [press enter for no username]: ')
                                    if not Question == '':
                                        templateVars["minLength"] = 1
                                        templateVars["maxLength"] = 255
                                        templateVars["varName"] = 'Username'
                                        varValue = Question
                                        valid = validating.string_length(templateVars["varName"], varValue, templateVars["minLength"], templateVars["maxLength"])
                                    if Question == '':
                                        valid = True
                                    else:
                                        print(f'\n-------------------------------------------------------------------------------------------\n')
                                        print(f'  Error!! Invalid Value.  Please Re-enter the LDAP Group.')
                                        print(f'\n-------------------------------------------------------------------------------------------\n')

                                # Assign the Variable
                                Username = Question

                                if not Username == '':
                                    valid = False
                                    while valid == False:
                                        Password = stdiomask.getpass(prompt='What is the password for authentication? ')
                                        templateVars["minLength"] = 1
                                        templateVars["maxLength"] = 255
                                        templateVars["rePattern"] = '^[\\S]+$'
                                        templateVars["varName"] = 'Password'
                                        varValue = Password
                                        valid_passphrase = validating.length_and_regex_sensitive(templateVars["rePattern"], templateVars["varName"], varValue, templateVars["minLength"], templateVars["maxLength"])
                                        if valid_passphrase == True:
                                            env_password = 'TF_VAR_vmedia_password_%s' % (inner_loop_count)
                                            os.environ[env_password] = '%s' % (Password)
                                            Password = inner_loop_count
                                            valid = True
                                else:
                                    Password = 0

                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                print(f'  The mount options for the virtual media mapping.')
                                if Protocol == 'cifs':
                                    print(f'  * supported options are soft, nounix, noserverino, guest, ver=3.0, or ver=2.0.')
                                elif Protocol == 'nfs':
                                    print(f'  * supported options are ro, rw, nolock, noexec, soft, port=VALUE, timeo=VALUE, retry=VALUE.')
                                else:
                                    print(f'  * the only supported option is noauto')
                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                valid = False
                                while valid == False:
                                    Question = input(f'Would you like to assign any mount options?  Enter "Y" or "N" [N]: ')
                                    if Question == '' or Question == 'N':
                                        assignOptions = False
                                        valid = True
                                    elif Question == 'Y':
                                        assignOptions = True
                                        valid = True
                                    else:
                                        print(f'\n-------------------------------------------------------------------------------------------\n')
                                        print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                                        print(f'\n-------------------------------------------------------------------------------------------\n')

                                if assignOptions == True:
                                    templateVars["multi_select"] = True
                                    jsonVars = easy_jsonData['policies']['vmedia.Mapping']
                                    if Protocol == 'cifs':
                                        templateVars["var_description"] = jsonVars['cifs.mountOptions']['description']
                                        templateVars["jsonVars"] = sorted(jsonVars['cifs.mountOptions']['enum'])
                                        templateVars["defaultVar"] = jsonVars['cifs.mountOptions']['default']
                                    elif Protocol == 'nfs':
                                        templateVars["var_description"] = jsonVars['nfs.mountOptions']['description']
                                        templateVars["jsonVars"] = sorted(jsonVars['nfs.mountOptions']['enum'])
                                        templateVars["defaultVar"] = jsonVars['nfs.mountOptions']['default']
                                    else:
                                        templateVars["multi_select"] = False
                                        templateVars["var_description"] = jsonVars['http.mountOptions']['description']
                                        templateVars["jsonVars"] = sorted(jsonVars['http.mountOptions']['enum'])
                                        templateVars["defaultVar"] = jsonVars['http.mountOptions']['default']
                                    templateVars["varType"] = 'Mount Options'
                                    mount_loop = variablesFromAPI(**templateVars)

                                    mount_output = []
                                    for x in mount_loop:
                                        mount_output.append(x)
                                    print(mount_output)
                                    for x in mount_loop:
                                        if x == 'port':
                                            valid = False
                                            while valid == False:
                                                Question = input(f'What Port would you like to assign?  [2049]: ')
                                                if Question == '':
                                                    Question = 2049
                                                if re.fullmatch(r'^[0-9]{1,4}$', str(Question)):
                                                    templateVars["minNum"] = 1
                                                    templateVars["maxNum"] = 65535
                                                    templateVars["varName"] = 'NFS Port'
                                                    varValue = Question
                                                    valid = validating.number_in_range(templateVars["varName"], varValue, templateVars["minNum"], templateVars["maxNum"])
                                            port = 'port=%s' % (Question)
                                            mount_output.remove(x)
                                            mount_output.append(port)
                                        elif x == 'retry':
                                            valid = False
                                            while valid == False:
                                                Question = input(f'What Retry would you like to assign?  [2]: ')
                                                if Question == '':
                                                    Question = 2
                                                if re.fullmatch(r'^[0-9]{1,4}$', str(Question)):
                                                    templateVars["minNum"] = 1
                                                    templateVars["maxNum"] = 65535
                                                    templateVars["varName"] = 'NFS Port'
                                                    varValue = Question
                                                    valid = validating.number_in_range(templateVars["varName"], varValue, templateVars["minNum"], templateVars["maxNum"])
                                            retry = 'retry=%s' % (Question)
                                            mount_output.remove(x)
                                            mount_output.append(retry)
                                        elif x == 'timeo':
                                            valid = False
                                            while valid == False:
                                                Question = input(f'What Timeout (timeo) would you like to assign?  [600]: ')
                                                if Question == '':
                                                    Question = 600
                                                if re.fullmatch(r'^[0-9]{1,4}$', str(Question)):
                                                    templateVars["minNum"] = 60
                                                    templateVars["maxNum"] = 600
                                                    templateVars["varName"] = 'NFS timeo'
                                                    varValue = Question
                                                    valid = validating.number_in_range(templateVars["varName"], varValue, templateVars["minNum"], templateVars["maxNum"])
                                            timeo = 'timeo=%s' % (Question)
                                            mount_output.remove(x)
                                            mount_output.append(timeo)
                                        elif re.search('(rsize|wsize)', x):
                                            valid = False
                                            while valid == False:
                                                Question = input(f'What is the value of {x} you want to assign?  [1024]: ')
                                                if Question == '':
                                                    Question = 1024
                                                if re.fullmatch(r'^[0-9]{4,7}$', str(Question)):
                                                    templateVars["minNum"] = 1024
                                                    templateVars["maxNum"] = 1048576
                                                    templateVars["varName"] = 'NFS timeo'
                                                    varValue = Question
                                                    validCount = 0
                                                    validNum = validating.number_in_range(templateVars["varName"], varValue, templateVars["minNum"], templateVars["maxNum"])
                                                    if validNum == True:
                                                        validCount += 1
                                                    if int(Question) % 1024 == 0:
                                                        validCount += 1
                                                    else:
                                                        print(f'\n-------------------------------------------------------------------------------------------\n')
                                                        print(f'  {x} should be a divisable value of 1024 between 1024 and 1048576')
                                                        print(f'\n-------------------------------------------------------------------------------------------\n')
                                                    if validCount == 2:
                                                        valid = True
                                            xValue = '%s=%s' % (x, Question)
                                            mount_output.remove(x)
                                            mount_output.append(xValue)
                                    mount_options = ','.join(mount_output)
                                else:
                                    mount_options = ''

                                print(mount_options)

                                if Protocol == 'cifs':
                                    vmedia_map = {
                                        'authentication_protocol':authProtocol,
                                        'device_type':deviceType,
                                        'file_location':file_location,
                                        'mount_options':mount_options,
                                        'name':name,
                                        'password':Password,
                                        'protocol':Protocol,
                                        'username':Username
                                    }
                                else:
                                    vmedia_map = {
                                        'device_type':deviceType,
                                        'file_location':file_location,
                                        'mount_options':mount_options,
                                        'name':name,
                                        'password':Password,
                                        'protocol':Protocol,
                                        'username':Username
                                    }

                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                if Protocol == 'cifs':
                                    print(f'   authentication_protocol = "{authProtocol}"')
                                print(f'   device_type             = "{deviceType}"')
                                print(f'   file_location           = "{file_location}"')
                                if not mount_options == '':
                                    print(f'   mount_options           = "{mount_options}"')
                                print(f'   name                    = "{name}"')
                                if not Password == 0:
                                    print(f'   password                = "{Password}"')
                                print(f'   protocol                = "{Protocol}"')
                                if not Username == '':
                                    print(f'   username                = "{Username}"')
                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                valid_confirm = False
                                while valid_confirm == False:
                                    confirm_config = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
                                    if confirm_config == 'Y' or confirm_config == '':
                                        templateVars["virtual_media"].append(vmedia_map)
                                        valid_exit = False
                                        while valid_exit == False:
                                            loop_exit = input(f'Would You like to Configure another Virtual Media Map?  Enter "Y" or "N" [N]: ')
                                            if loop_exit == 'Y':
                                                inner_loop_count += 1
                                                valid_confirm = True
                                                valid_exit = True
                                            elif loop_exit == 'N' or loop_exit == '':
                                                sub_loop = True
                                                valid_confirm = True
                                                valid_exit = True
                                                valid_sub = True
                                            else:
                                                print(f'\n------------------------------------------------------\n')
                                                print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                                                print(f'\n------------------------------------------------------\n')

                                    elif confirm_config == 'N':
                                        print(f'\n-------------------------------------------------------------------------------------------\n')
                                        print(f'  Starting LDAP Group Configuration Over.')
                                        print(f'\n-------------------------------------------------------------------------------------------\n')
                                        valid_confirm = True
                                    else:
                                        print(f'\n------------------------------------------------------\n')
                                        print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                                        print(f'\n------------------------------------------------------\n')

                        elif question == 'N':
                            sub_loop = True
                        else:
                            print(f'\n------------------------------------------------------\n')
                            print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                            print(f'\n------------------------------------------------------\n')

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'    description                     = "{templateVars["descr"]}"')
                    print(f'    enable_low_power_usb            = "{templateVars["enable_low_power_usb"]}"')
                    print(f'    enable_virtual_media            = "{templateVars["enable_virtual_media"]}"')
                    print(f'    enable_virtual_media_encryption = "{templateVars["enable_virtual_media_encryption"]}"')
                    print(f'    name                            = "{templateVars["name"]}"')
                    if len(templateVars["virtual_media"]) > 0:
                        print(f'    virtual_media = ''{')
                        for item in templateVars["virtual_media"]:
                            for k, v in item.items():
                                if k == 'name':
                                    print(f'      "{v}" = ''{')
                            for k, v in item.items():
                                if k == 'authentication_protocol':
                                    print(f'        authentication_protocol = "{v}"')
                                elif k == 'device_type':
                                    print(f'        device_type             = "{v}"')
                                elif k == 'file_location':
                                    print(f'        file_location           = "{v}"')
                                elif k == 'mount_options':
                                    print(f'        mount_options           = "{v}"')
                                elif k == 'password' and v != 0:
                                    print(f'        password                = {v}')
                                elif k == 'protocol':
                                    print(f'        protocol                = "{v}"')
                                elif k == 'username' and v != '':
                                    print(f'        username                = "{v}"')
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
