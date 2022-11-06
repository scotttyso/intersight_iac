#!/usr/bin/env python3
import p1
import lan
import vxan
import ezfunctions
import jinja2
import os
import pkg_resources
import platform
import re
import stdiomask
import validating

ucs_template_path = pkg_resources.resource_filename('p2', '../templates/')

class policies(object):
    def __init__(self, name_prefix, org, type):
        self.templateLoader = jinja2.FileSystemLoader(
            searchpath=(ucs_template_path + '%s/') % (type))
        self.templateEnv = jinja2.Environment(loader=self.templateLoader)
        self.name_prefix = name_prefix
        self.org = org
        self.type = type

    #==============================================
    # Local User Policy Module
    #==============================================
    def local_user_policies(self, jsonData, easy_jsonData, **kwargs):
        name_prefix = self.name_prefix
        name_suffix = 'local_users'
        opSystem = kwargs['opSystem']
        org = self.org
        policy_type = 'Local User Policy'
        polVars = {}
        polVars["header"] = '%s Variables' % (policy_type)
        polVars["initial_write"] = True
        polVars["org"] = org
        polVars["policy_type"] = policy_type
        polVars["template_file"] = 'template_open.jinja2'
        polVars["template_type"] = 'local_user_policies'
        tfDir = kwargs['tfDir']

        # Open the Template file
        ezfunctions.write_to_template(self, **polVars)
        polVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  A {policy_type} will configure servers with Local Users for KVM Access.  This Policy ')
            print(f'  is not required to standup a server but is a good practice for day 2 support.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            if opSystem == 'Windows':
                print(f'  - {tfDir}\\{org}\\{self.type}\\{polVars["template_type"]}.auto.tfvars')
            else:
                print(f'  - {tfDir}/{org}/{self.type}/{polVars["template_type"]}.auto.tfvars')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure a {policy_type}?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                loop_count = 1
                policy_loop = False
                while policy_loop == False:

                    if not name_prefix == '':
                        name = '%s_%s' % (name_prefix, name_suffix)
                    else:
                        name = '%s_%s' % (org, name_suffix)

                    polVars["name"] = ezfunctions.policy_name(name, policy_type)
                    polVars["descr"] = ezfunctions.policy_descr(polVars["name"], policy_type)

                    # Obtain Information for iam.EndpointPasswordProperties
                    polVars["multi_select"] = False
                    jsonVars = jsonData['components']['schemas']['iam.EndPointPasswordProperties']['allOf'][1]['properties']

                    # Local User Always Send Password
                    polVars["Description"] = jsonVars['ForceSendPassword']['description']
                    polVars["varInput"] = f'Do you want Intersight to Always send the user password with policy updates?'
                    polVars["varDefault"] = 'N'
                    polVars["varName"] = 'Force Send Password'
                    polVars["always_send_user_password"] = ezfunctions.varBoolLoop(**polVars)

                    # Local User Enforce Strong Password
                    polVars["Description"] = jsonVars['EnforceStrongPassword']['description']
                    polVars["varInput"] = f'Do you want to Enforce Strong Passwords?'
                    polVars["varDefault"] = 'Y'
                    polVars["varName"] = 'Enforce Strong Password'
                    polVars["enforce_strong_password"] = ezfunctions.varBoolLoop(**polVars)

                    # Local User Password Expiry
                    polVars["Description"] = jsonVars['EnablePasswordExpiry']['description']
                    polVars["varInput"] = f'Do you want to Enable password Expiry on the Endpoint?'
                    polVars["varDefault"] = 'Y'
                    polVars["varName"] = 'Enable Password Expiry'
                    polVars["enable_password_expiry"] = ezfunctions.varBoolLoop(**polVars)

                    if polVars["enable_password_expiry"] == True:
                        # Local User Grace Period
                        polVars["Description"] = 'Grace Period, in days, after the password is expired '\
                                'that a user can continue to use their expired password.'\
                                'The allowed grace period is between 0 to 5 days.  With 0 being no grace period.'
                        polVars["varDefault"] =  jsonVars['GracePeriod']['default']
                        polVars["varInput"] = 'How many days would you like to set for the Grace Period?'
                        polVars["varName"] = 'Grace Period'
                        polVars["varRegex"] = '[0-9]+'
                        polVars["minNum"] = jsonVars['GracePeriod']['minimum']
                        polVars["maxNum"] = jsonVars['GracePeriod']['maximum']
                        polVars["grace_period"] = ezfunctions.varNumberLoop(**polVars)

                        # Local User Notification Period
                        polVars["Description"] = 'Notification Period - Number of days, between 0 to 15 '\
                                '(0 being disabled), that a user is notified to change their password before it expires.'
                        polVars["varDefault"] =  jsonVars['NotificationPeriod']['default']
                        polVars["varInput"] = 'How many days would you like to set for the Notification Period?'
                        polVars["varName"] = 'Notification Period'
                        polVars["varRegex"] = '[0-9]+'
                        polVars["minNum"] = jsonVars['NotificationPeriod']['minimum']
                        polVars["maxNum"] = jsonVars['NotificationPeriod']['maximum']
                        polVars["notification_period"] = ezfunctions.varNumberLoop(**polVars)

                        # Local User Password Expiry Duration
                        valid = False
                        while valid == False:
                            polVars["Description"] = 'Note: When Password Expiry is Enabled, Password Expiry '\
                                    'Duration sets the duration of time, (in days), a password may be valid.  '\
                                    'The password expiryduration must be greater than '\
                                    'notification period + grace period.  Range is 1-3650.'
                            polVars["varDefault"] =  jsonVars['PasswordExpiryDuration']['default']
                            polVars["varInput"] = 'How many days would you like to set for the Password Expiry Duration?'
                            polVars["varName"] = 'Password Expiry Duration'
                            polVars["varRegex"] = '[0-9]+'
                            polVars["minNum"] = jsonVars['PasswordExpiryDuration']['minimum']
                            polVars["maxNum"] = jsonVars['PasswordExpiryDuration']['maximum']
                            polVars["password_expiry_duration"] = ezfunctions.varNumberLoop(**polVars)
                            x = int(polVars["grace_period"])
                            y = int(polVars["notification_period"])
                            z = int(polVars["password_expiry_duration"])
                            if z > (x + y):
                                valid = True
                            else:
                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                print(f'  Error!! The Value of Password Expiry Duration must be greater than Grace Period +')
                                print(f'  Notification Period.  {z} is not greater than [{x} + {y}]')
                                print(f'\n-------------------------------------------------------------------------------------------\n')

                        # Local User Notification Period
                        polVars["Description"] = jsonVars['PasswordHistory']['description'] + \
                            ' Range is 0 to 5.'
                        polVars["varDefault"] =  jsonVars['PasswordHistory']['default']
                        polVars["varInput"] = 'How many passwords would you like to store for a user?'
                        polVars["varName"] = 'Password History'
                        polVars["varRegex"] = '[0-9]+'
                        polVars["minNum"] = jsonVars['PasswordHistory']['minimum']
                        polVars["maxNum"] = jsonVars['PasswordHistory']['maximum']
                        polVars["password_history"] = ezfunctions.varNumberLoop(**polVars)

                    else:
                        polVars["grace_period"] = 0
                        polVars["notification_period"] = 15
                        polVars["password_expiry_duration"] = 90
                        polVars["password_history"] = 5

                    # Local Users
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

                    polVars["enabled"] = True
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'    always_send_user_password = {polVars["always_send_user_password"]}')
                    print(f'    description               = "{polVars["descr"]}"')
                    print(f'    enable_password_expiry    = {polVars["enable_password_expiry"]}')
                    print(f'    enforce_strong_password   = {polVars["enforce_strong_password"]}')
                    print(f'    grace_period              = "{polVars["grace_period"]}"')
                    print(f'    name                      = "{polVars["name"]}"')
                    print(f'    password_expiry_duration  = "{polVars["password_expiry_duration"]}"')
                    print(f'    password_history          = "{polVars["password_history"]}"')
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
    # Network Connectivity Policy Module
    #==============================================
    def network_connectivity_policies(self, jsonData, easy_jsonData, **kwargs):
        name_prefix = self.name_prefix
        name_suffix = 'dns'
        opSystem = kwargs['opSystem']
        org = self.org
        policy_type = 'Network Connectivity Policy'
        polVars = {}
        polVars["header"] = '%s Variables' % (policy_type)
        polVars["initial_write"] = True
        polVars["org"] = org
        polVars["policy_type"] = policy_type
        polVars["template_file"] = 'template_open.jinja2'
        polVars["template_type"] = 'network_connectivity_policies'
        tfDir = kwargs['tfDir']

        # Open the Template file
        ezfunctions.write_to_template(self, **polVars)
        polVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  It is strongly recommended to have a Network Connectivity (DNS) Policy for the')
            print(f'  UCS Domain Profile.  Without it, DNS resolution will fail.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            if opSystem == 'Windows':
                print(f'  - {tfDir}\\{org}\\{self.type}\\{polVars["template_type"]}.auto.tfvars')
            else:
                print(f'  - {tfDir}/{org}/{self.type}/{polVars["template_type"]}.auto.tfvars')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            policy_loop = False
            while policy_loop == False:

                if not name_prefix == '':
                    name = '%s_%s' % (name_prefix, name_suffix)
                else:
                    name = '%s_%s' % (org, name_suffix)

                polVars["name"] = ezfunctions.policy_name(name, policy_type)
                polVars["descr"] = ezfunctions.policy_descr(polVars["name"], policy_type)

                valid = False
                while valid == False:
                    polVars["preferred_ipv4_dns_server"] = input('What is your Primary IPv4 DNS Server?  [208.67.220.220]: ')
                    if polVars["preferred_ipv4_dns_server"] == '':
                        polVars["preferred_ipv4_dns_server"] = '208.67.220.220'
                    valid = validating.ip_address('Primary IPv4 DNS Server', polVars["preferred_ipv4_dns_server"])

                valid = False
                while valid == False:
                    alternate_true = input('Do you want to Configure an Alternate IPv4 DNS Server?  Enter "Y" or "N" [Y]: ')
                    if alternate_true == 'Y' or alternate_true == '':
                        polVars["alternate_ipv4_dns_server"] = input('What is your Alternate IPv4 DNS Server?  [208.67.222.222]: ')
                        if polVars["alternate_ipv4_dns_server"] == '':
                            polVars["alternate_ipv4_dns_server"] = '208.67.222.222'
                        valid = validating.ip_address('Alternate IPv4 DNS Server', polVars["alternate_ipv4_dns_server"])
                    elif alternate_true == 'N':
                        polVars["alternate_ipv4_dns_server"] = ''
                        valid = True
                    else:
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                        print(f'\n-------------------------------------------------------------------------------------------\n')

                valid = False
                while valid == False:
                    enable_ipv6 = input('Do you want to Configure IPv6 DNS?  Enter "Y" or "N" [N]: ')
                    if enable_ipv6 == 'Y':
                        polVars["enable_ipv6"] = True
                        polVars["preferred_ipv6_dns_server"] = input('What is your Primary IPv6 DNS Server?  [2620:119:35::35]: ')
                        if polVars["preferred_ipv6_dns_server"] == '':
                            polVars["preferred_ipv6_dns_server"] = '2620:119:35::35'
                        valid = validating.ip_address('Primary IPv6 DNS Server', polVars["preferred_ipv6_dns_server"])
                    if enable_ipv6 == 'N' or enable_ipv6 == '':
                        polVars["enable_ipv6"] = False
                        polVars["preferred_ipv6_dns_server"] = ''
                        valid = True

                valid = False
                while valid == False:
                    if enable_ipv6 == 'Y':
                        alternate_true = input('Do you want to Configure an Alternate IPv6 DNS Server?  Enter "Y" or "N" [Y]: ')
                        if alternate_true == 'Y' or alternate_true == '':
                            polVars["alternate_ipv6_dns_server"] = input('What is your Alternate IPv6 DNS Server?  [2620:119:53::53]: ')
                            if polVars["alternate_ipv6_dns_server"] == '':
                                polVars["alternate_ipv6_dns_server"] = '2620:119:53::53'
                            valid = validating.ip_address('Alternate IPv6 DNS Server', polVars["alternate_ipv6_dns_server"])
                        elif alternate_true == 'N':
                            polVars["alternate_ipv6_dns_server"] = ''
                            valid = True
                        else:
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                    else:
                        polVars["alternate_ipv6_dns_server"] = ''
                        valid = True

                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'    description = "{polVars["descr"]}"')
                print(f'    name        = "{polVars["name"]}"')
                if not polVars["preferred_ipv4_dns_server"] == '':
                    print(f'    dns_servers_v4 = [')
                    print(f'      {polVars["preferred_ipv4_dns_server"]},')
                    if not polVars["alternate_ipv4_dns_server"] == '':
                        print(f'      {polVars["alternate_ipv4_dns_server"]}')
                    print(f'    ]')
                if not polVars["preferred_ipv6_dns_server"] == '':
                    print(f'    dns_servers_v6 = [')
                    print(f'      {polVars["preferred_ipv6_dns_server"]},')
                    if not polVars["alternate_ipv6_dns_server"] == '':
                        print(f'      {polVars["alternate_ipv6_dns_server"]}')
                    print(f'    ]')
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

        # Close the Template file
        polVars["template_file"] = 'template_close.jinja2'
        ezfunctions.write_to_template(self, **polVars)

    #==============================================
    # NTP Policy Module
    #==============================================
    def ntp_policies(self, jsonData, easy_jsonData, **kwargs):
        name_prefix = self.name_prefix
        name_suffix = 'ntp'
        opSystem = kwargs['opSystem']
        org = self.org
        policy_type = 'NTP Policy'
        polVars = {}
        polVars["header"] = '%s Variables' % (policy_type)
        polVars["initial_write"] = True
        polVars["org"] = org
        polVars["policy_type"] = policy_type
        polVars["template_file"] = 'template_open.jinja2'
        polVars["template_type"] = 'ntp_policies'
        tfDir = kwargs['tfDir']

        # Open the Template file
        ezfunctions.write_to_template(self, **polVars)
        polVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  It is strongly recommended to configure an NTP Policy for the UCS Domain Profile.')
            print(f'  Without an NTP Policy Events can be incorrectly timestamped and Intersight ')
            print(f'  Communication, as an example, could be interrupted with Certificate Validation\n')
            print(f'  checks, as an example.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            if opSystem == 'Windows':
                print(f'  - {tfDir}\\{org}\\{self.type}\\{polVars["template_type"]}.auto.tfvars')
            else:
                print(f'  - {tfDir}/{org}/{self.type}/{polVars["template_type"]}.auto.tfvars')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            policy_loop = False
            while policy_loop == False:

                if not name_prefix == '':
                    name = '%s_%s' % (name_prefix, name_suffix)
                else:
                    name = '%s_%s' % (org, name_suffix)

                polVars["name"] = ezfunctions.policy_name(name, policy_type)
                polVars["descr"] = ezfunctions.policy_descr(polVars["name"], policy_type)

                primary_ntp = ezfunctions.ntp_primary()
                alternate_ntp = ezfunctions.ntp_alternate()

                polVars["enabled"] = True
                polVars["ntp_servers"] = []
                polVars["ntp_servers"].append(primary_ntp)
                if not alternate_ntp == '':
                    polVars["ntp_servers"].append(alternate_ntp)

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

                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'    description = "{polVars["descr"]}"')
                print(f'    name        = "{polVars["name"]}"')
                print(f'    timezone    = "{polVars["timezone"]}"')
                if len(polVars["ntp_servers"]) > 0:
                    print(f'    ntp_servers = [')
                    for server in polVars["ntp_servers"]:
                        print(f'      "{server}",')
                    print(f'    ]')
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

        # Close the Template file
        polVars["template_file"] = 'template_close.jinja2'
        ezfunctions.write_to_template(self, **polVars)

    #==============================================
    # Persistent Memory Policy Module
    #==============================================
    def persistent_memory_policies(self, jsonData, easy_jsonData, **kwargs):
        name_prefix = self.name_prefix
        name_suffix = 'persistent_memory'
        opSystem = kwargs['opSystem']
        org = self.org
        policy_type = 'Persistent Memory Policy'
        polVars = {}
        polVars["header"] = '%s Variables' % (policy_type)
        polVars["initial_write"] = True
        polVars["org"] = org
        polVars["policy_type"] = policy_type
        polVars["template_file"] = 'template_open.jinja2'
        polVars["template_type"] = 'persistent_memory_policies'
        tfDir = kwargs['tfDir']

        # Open the Template file
        ezfunctions.write_to_template(self, **polVars)
        polVars["initial_write"] = False

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
                    jsonVars = jsonData['components']['schemas']['memory.PersistentMemoryPolicy']['allOf'][1]['properties']
                    polVars["var_description"] = jsonVars['ManagementMode']['description']
                    polVars["jsonVars"] = sorted(jsonVars['ManagementMode']['enum'])
                    polVars["defaultVar"] = jsonVars['ManagementMode']['default']
                    polVars["varType"] = 'Management Mode'
                    polVars["management_mode"] = ezfunctions.variablesFromAPI(**polVars)

                    if polVars["management_mode"] == 'configured-from-intersight':
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
                                    polVars["minLength"] = 8
                                    polVars["maxLength"] = 32
                                    polVars["rePattern"] = '^[a-zA-Z0-9\\u0021\\&\\#\\$\\%\\+\\%\\@\\_\\*\\-\\.]+$'
                                    polVars["varName"] = 'Secure Passphrase'
                                    varValue = secure_passphrase
                                    valid_passphrase = validating.length_and_regex_sensitive(polVars["rePattern"],
                                        polVars["varName"],
                                        varValue,
                                        polVars["minLength"],
                                        polVars["maxLength"]
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
                            polVars["memory_mode_percentage"] = input('What is the Percentage of Valatile Memory to assign to this Policy?  [0]: ')
                            if polVars["memory_mode_percentage"] == '':
                                polVars["memory_mode_percentage"] = 0
                            if re.search(r'[\d]+', str(polVars["memory_mode_percentage"])):
                                valid = validating.number_in_range('Memory Mode Percentage', polVars["memory_mode_percentage"], 1, 100)
                            else:
                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                print(f'  "{polVars["memory_mode_percentage"]}" is not a valid number.')
                                print(f'\n-------------------------------------------------------------------------------------------\n')

                        jsonVars = jsonData['components']['schemas']['memory.PersistentMemoryGoal']['allOf'][1]['properties']
                        polVars["var_description"] = jsonVars['PersistentMemoryType']['description']
                        polVars["jsonVars"] = sorted(jsonVars['PersistentMemoryType']['enum'])
                        polVars["defaultVar"] = jsonVars['PersistentMemoryType']['default']
                        polVars["varType"] = 'Persistent Memory Type'
                        polVars["persistent_memory_type"] = ezfunctions.variablesFromAPI(**polVars)

                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        print(f'  This Flag will enable or Disable the retention of Namespaces between Server Profile')
                        print(f'  association and dissassociation.')
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        valid = False
                        while valid == False:
                            polVars["retain_namespaces"] = input('Do you want to Retain Namespaces?  Enter "Y" or "N" [Y]: ')
                            if polVars["retain_namespaces"] == '' or polVars["retain_namespaces"] == 'Y':
                                polVars["retain_namespaces"] = True
                                valid = True
                            elif polVars["retain_namespaces"] == 'N':
                                polVars["retain_namespaces"] = False
                                valid = True
                            else:
                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                                print(f'\n-------------------------------------------------------------------------------------------\n')

                        polVars["namespaces"] = []
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
                                    polVars["minLength"] = 1
                                    polVars["maxLength"] = 63
                                    polVars["rePattern"] = '^[a-zA-Z0-9\\#\\_\\-]+$'
                                    polVars["varName"] = 'Name for the Namespace'
                                    varValue = namespace_name
                                    valid = validating.length_and_regex(polVars["rePattern"], polVars["varName"], varValue, polVars["minLength"], polVars["maxLength"])

                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                print(f'  Capacity of this Namespace in gibibytes (GiB).  Range is 1-9223372036854775807')
                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                valid = False
                                while valid == False:
                                    capacity = input('What is the Capacity to assign to this Namespace? ')
                                    polVars["minNum"] = 1
                                    polVars["maxNum"] = 9223372036854775807
                                    polVars["varName"] = 'Namespace Capacity'
                                    varValue = int(capacity)
                                    if re.search(r'[\d]+',str(varValue)):
                                        valid = validating.number_in_range(polVars["varName"], varValue, polVars["minNum"], polVars["maxNum"])
                                    else:
                                        print(f'\n-------------------------------------------------------------------------------------------\n')
                                        print(f'  "{varValue}" is not a valid number.')
                                        print(f'\n-------------------------------------------------------------------------------------------\n')

                                jsonVars = jsonData['components']['schemas']['memory.PersistentMemoryLogicalNamespace']['allOf'][1]['properties']
                                polVars["var_description"] = jsonVars['Mode']['description']
                                polVars["jsonVars"] = sorted(jsonVars['Mode']['enum'])
                                polVars["defaultVar"] = jsonVars['Mode']['default']
                                polVars["varType"] = 'Mode'
                                mode = ezfunctions.variablesFromAPI(**polVars)

                                polVars["var_description"] = jsonVars['SocketId']['description']
                                polVars["jsonVars"] = sorted(jsonVars['SocketId']['enum'])
                                polVars["defaultVar"] = jsonVars['SocketId']['default']
                                polVars["varType"] = 'Socket Id'
                                socket_id = ezfunctions.variablesFromAPI(**polVars)

                                if polVars["persistent_memory_type"] == 'app-direct-non-interleaved':
                                    polVars["var_description"] = jsonVars['SocketMemoryId']['description']
                                    polVars["jsonVars"] = [x for x in jsonVars['SocketMemoryId']['enum']]
                                    polVars["defaultVar"] = '2'
                                    polVars["popList"] = ['Not Applicable']
                                    polVars["varType"] = 'Socket Memory Id'
                                    socket_memory_id = ezfunctions.variablesFromAPI(**polVars)
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
                                        polVars["namespaces"].append(namespace)

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
                    print(f'    description     = "{polVars["descr"]}"')
                    print(f'    management_mode = "{polVars["management_mode"]}"')
                    print(f'    name            = "{polVars["name"]}"')
                    if polVars["management_mode"]  == 'configured-from-intersight':
                        print(f'    # GOALS')
                        print(f'    memory_mode_percentage = {polVars["memory_mode_percentage"]}')
                        print(f'    persistent_memory_type = {polVars["persistent_memory_type"]}')
                        print(f'    # NAMESPACES')
                        print(f'    namespaces = ''{')
                        for item in polVars["namespaces"]:
                            print(f'      "{item["name"]}" = ''{')
                            print(f'        capacity         = {item["capacity"]}')
                            print(f'        mode             = {item["mode"]}')
                            print(f'        socket_id        = {item["socket_id"]}')
                            print(f'        socket_memory_id = {item["socket_memory_id"]}')
                            print(f'      ''}')
                        print(f'    ''}')
                        print(f'   retain_namespaces = "{polVars["retain_namespaces"]}"')
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
    # Port Policy Module
    #==============================================
    def port_policies(self, jsonData, easy_jsonData, **kwargs):
        name_prefix = self.name_prefix
        opSystem = kwargs['opSystem']
        org = self.org
        policy_type = 'Port Policy'
        polVars = {}
        polVars["header"] = '%s Variables' % (policy_type)
        polVars["initial_write"] = True
        polVars["org"] = org
        polVars["policy_type"] = policy_type
        polVars["template_file"] = 'template_open.jinja2'
        polVars["template_type"] = 'port_policies'
        tfDir = kwargs['tfDir']

        # Open the Template file
        ezfunctions.write_to_template(self, **polVars)
        polVars["initial_write"] = False

        port_count = 0
        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  A {policy_type} is used to configure the ports for a UCS Domain Profile.  This includes:')
            print(f'   - Unified Ports - Ports to convert to Fibre-Channel Mode.')
            print(f'   - Appliance Ports')
            print(f'   - Appliance Port-Channels')
            print(f'   - Ethernet Uplinks')
            print(f'   - Ethernet Uplink Port-Channels')
            print(f'   - FCoE Uplinks')
            print(f'   - FCoE Uplink Port-Channels')
            print(f'   - Fibre-Channel Storage')
            print(f'   - Fibre-Channel Uplinks')
            print(f'   - Fibre-Channel Uplink Port-Channels')
            print(f'   - Server Ports\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            if opSystem == 'Windows':
                print(f'  - {tfDir}\\{org}\\{self.type}\\{polVars["template_type"]}.auto.tfvars')
            else:
                print(f'  - {tfDir}/{org}/{self.type}/{polVars["template_type"]}.auto.tfvars')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            policy_loop = False
            while policy_loop == False:

                print(f'   IMPORTANT NOTE: The wizard will create a Port Policy for Fabric A and Fabric B')
                print(f'                   automatically.  The Policy Name will be appended with [name]_A for ')
                print(f'                   Fabric A and [name]_B for Fabric B.  You only need one Policy per')
                print(f'                   Domain.')
                print(f'\n-------------------------------------------------------------------------------------------\n')

                if not name_prefix == '':
                    name = '%s' % (name_prefix)
                else:
                    name = '%s' % (org)

                polVars["name"] = ezfunctions.policy_name(name, policy_type)
                polVars["descr"] = ezfunctions.policy_descr(polVars["name"], policy_type)

                polVars["multi_select"] = False
                jsonVars = jsonData['components']['schemas']['fabric.PortPolicy']['allOf'][1]['properties']
                polVars["var_description"] = jsonVars['DeviceModel']['description']
                polVars["jsonVars"] = sorted(jsonVars['DeviceModel']['enum'])
                polVars["defaultVar"] = jsonVars['DeviceModel']['default']
                polVars["varType"] = 'Device Model'
                polVars["device_model"] = ezfunctions.variablesFromAPI(**polVars)
                
                fc_mode,ports_in_use,fc_converted_ports,port_modes = port_modes_fc(jsonData, easy_jsonData, name_prefix, **polVars)
                polVars["fc_mode"] = fc_mode
                polVars["ports_in_use"] = ports_in_use
                polVars["fc_converted_ports"] = fc_converted_ports
                polVars["port_modes"] = port_modes
                polVars["fc_ports"] = polVars["port_modes"]["port_list"]

                # Appliance Port-Channel
                polVars['port_type'] = 'Appliance Port-Channel'
                port_channel_appliances,polVars['ports_in_use'] = port_list_eth(jsonData, easy_jsonData, name_prefix, **polVars)

                # Ethernet Uplink Port-Channel
                polVars['port_type'] = 'Ethernet Uplink Port-Channel'
                port_channel_ethernet_uplinks,polVars['ports_in_use'] = port_list_eth(jsonData, easy_jsonData, name_prefix, **polVars)

                # Fibre-Channel Port-Channel
                polVars["fc_ports_in_use"] = []
                polVars["port_type"] = 'Fibre-Channel Port-Channel'
                Fab_A,Fab_B,fc_ports_in_use = port_list_fc(jsonData, easy_jsonData, name_prefix, **polVars)
                Fabric_A_fc_port_channels = Fab_A
                Fabric_B_fc_port_channels = Fab_B
                polVars["fc_ports_in_use"] = fc_ports_in_use

                # FCoE Uplink Port-Channel
                polVars['port_type'] = 'FCoE Uplink Port-Channel'
                port_channel_fcoe_uplinks,polVars['ports_in_use'] = port_list_eth(jsonData, easy_jsonData, name_prefix, **polVars)

                # Appliance Ports
                polVars['port_type'] = 'Appliance Ports'
                port_role_appliances,polVars['ports_in_use'] = port_list_eth(jsonData, easy_jsonData, name_prefix, **polVars)

                # Ethernet Uplink
                polVars['port_type'] = 'Ethernet Uplink'
                port_role_ethernet_uplinks,polVars['ports_in_use'] = port_list_eth(jsonData, easy_jsonData, name_prefix, **polVars)

                # Fibre-Channel Storage
                polVars["port_type"] = 'Fibre-Channel Storage'
                Fab_A,Fab_B,fc_ports_in_use = port_list_fc(jsonData, easy_jsonData, name_prefix, **polVars)
                Fabric_A_port_role_fc_storage = Fab_A
                Fabric_B_port_role_fc_storage = Fab_B
                polVars["fc_ports_in_use"] = fc_ports_in_use

                # Fibre-Channel Uplink
                polVars["port_type"] = 'Fibre-Channel Uplink'
                Fab_A,Fab_B,fc_ports_in_use = port_list_fc(jsonData, easy_jsonData, name_prefix, **polVars)
                Fabric_A_port_role_fc_uplink = Fab_A
                Fabric_B_port_role_fc_uplink = Fab_B
                polVars["fc_ports_in_use"] = fc_ports_in_use

                # FCoE Uplink
                polVars['port_type'] = 'FCoE Uplink'
                port_role_fcoe_uplinks,polVars['ports_in_use'] = port_list_eth(jsonData, easy_jsonData, name_prefix, **polVars)

                # Server Ports
                polVars['port_type'] = 'Server Ports'
                port_role_servers,polVars['ports_in_use'] = port_list_eth(jsonData, easy_jsonData, name_prefix, **polVars)

                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'    description  = "{polVars["descr"]}"')
                print(f'    device_model = "{polVars["device_model"]}"')
                print(f'    name         = "{polVars["name"]}"')
                if len(port_channel_appliances) > 0:
                    print(f'    port_channel_appliances = [')
                    for item in port_channel_appliances:
                        for k, v in item.items():
                            if k == 'pc_id':
                                print(f'      {v} = ''{')
                        for k, v in item.items():
                            if k == 'admin_speed':
                                print(f'        admin_speed                     = "{v}"')
                            elif k == 'ethernet_network_control_policy':
                                print(f'        ethernet_network_control_policy = "{v}"')
                            elif k == 'ethernet_network_group_policy':
                                print(f'        ethernet_network_group_policy   = "{v}"')
                            elif k == 'interfaces':
                                print(f'        interfaces = [')
                                for i in v:
                                    print('          {')
                                    for x, y in i.items():
                                        print(f'            {x}          = {y}')
                                    print('          }')
                                print(f'        ]')
                            elif k == 'mode':
                                print(f'        mode     = "{v}"')
                            elif k == 'priority':
                                print(f'        priority = "{v}"')
                        print('      }')
                    print(f'    ]')
                if len(port_channel_ethernet_uplinks) > 0:
                    print(f'    port_channel_ethernet_uplinks = [')
                    for item in port_channel_ethernet_uplinks:
                        for k, v in item.items():
                            if k == 'pc_id':
                                print(f'      {v} = ''{')
                        for k, v in item.items():
                            if k == 'admin_speed':
                                print(f'        admin_speed         = "{v}"')
                            elif k == 'flow_control_policy':
                                print(f'        flow_control_policy = "{v}"')
                            elif k == 'interfaces':
                                print(f'        interfaces = [')
                                for i in v:
                                    print('          {')
                                    for x, y in i.items():
                                        print(f'            {x}          = {y}')
                                    print('          }')
                                print(f'        ]')
                            elif k == 'link_aggregation_policy':
                                print(f'        link_aggregation_policy = "{v}"')
                            elif k == 'link_control_policy':
                                print(f'        link_control_policy     = "{v}"')
                        print('      }')
                    print(f'    ]')
                if len(Fabric_A_fc_port_channels) > 0:
                    print(f'    port_channel_fc_uplinks = [')
                    item_count = 0
                    for item in Fabric_A_fc_port_channels:
                        for k, v in item.items():
                            if k == 'pc_id':
                                print(f'      {v} = ''{')
                        for k, v in item.items():
                            if k == 'admin_speed':
                                print(f'        admin_speed  = "{v}"')
                            elif k == 'fill_pattern':
                                print(f'        fill_pattern = "{v}"')
                            elif k == 'interfaces':
                                print(f'        interfaces = [')
                                for i in v:
                                    print('          {')
                                    for x, y in i.items():
                                        print(f'            {x}          = {y}')
                                    print('          }')
                                print(f'        ]')
                            elif k == 'vsan_id':
                                print(f'        vsan_fabric_a = "{v}"')
                                print(f'        vsan_fabric_b = "{Fabric_B_fc_port_channels[item_count].get("vsan_id")}"')
                        print('      }')
                        item_count += 1
                    print(f'    ]')
                if len(port_channel_fcoe_uplinks) > 0:
                    print(f'    port_channel_fcoe_uplinks = [')
                    for item in port_channel_fcoe_uplinks:
                        for k, v in item.items():
                            if k == 'pc_id':
                                print('      {v} = {')
                        for k, v in item.items():
                            if k == 'admin_speed':
                                print(f'        admin_speed = "{v}"')
                            elif k == 'interfaces':
                                print(f'        interfaces = [')
                                for i in v:
                                    print('          {')
                                    for x, y in i.items():
                                        print(f'            {x}          = {y}')
                                    print('          }')
                                print(f'        ]')
                            elif k == 'link_aggregation_policy':
                                print(f'        link_aggregation_policy = "{v}"')
                            elif k == 'link_control_policy':
                                print(f'        link_control_policy     = "{v}"')
                        print('      }')
                    print(f'    ]')
                if len(polVars["port_modes"]) > 0:
                    print('    port_modes = {')
                    for k, v in polVars["port_modes"].items():
                        if k == 'custom_mode':
                            print(f'      custom_mode = "{v}"')
                        elif k == 'port_list':
                            print(f'      port_list   = "{v}"')
                        elif k == 'slot_id':
                            print(f'      slot_id     = {v}')
                    print('    }')
                item_count = 0
                if len(port_role_appliances) > 0:
                    print(f'    port_role_appliances = [')
                    for item in port_role_appliances:
                        print(f'      {item_count} = ''{')
                        item_count += 1
                        for k, v in item.items():
                            if k == 'admin_speed':
                                print(f'        admin_speed                     = "{v}"')
                            elif k == 'ethernet_network_control_policy':
                                print(f'        ethernet_network_control_policy = "{v}"')
                            elif k == 'ethernet_network_group_policy':
                                print(f'        ethernet_network_group_policy   = "{v}"')
                            elif k == 'fec':
                                print(f'        fec                             = "{v}"')
                            elif k == 'mode':
                                print(f'        mode                            = "{v}"')
                            elif k == 'port_id':
                                print(f'        port_list                       = "{v}"')
                            elif k == 'priority':
                                print(f'        priority                        = "{v}"')
                            elif k == 'slot_id':
                                print(f'        slot_id                         = 1')
                        print('      }')
                    print(f'    ]')
                item_count = 0
                if len(port_role_ethernet_uplinks) > 0:
                    print(f'    port_role_ethernet_uplinks = [')
                    for item in port_role_ethernet_uplinks:
                        print(f'      {item_count} = ''{')
                        item_count += 1
                        for k, v in item.items():
                            if k == 'admin_speed':
                                print(f'        admin_speed         = "{v}"')
                            elif k == 'fec':
                                print(f'        fec                 = "{v}"')
                            elif k == 'flow_control_policy':
                                print(f'        flow_control_policy = "{v}"')
                            elif k == 'link_control_policy':
                                print(f'        link_control_policy = "{v}"')
                            elif k == 'port_id':
                                print(f'        port_list           = "{v}"')
                            elif k == 'slot_id':
                                print(f'        slot_id             = 1')
                        print('      }')
                    print(f'    ]')
                item_count = 0
                if len(Fabric_A_port_role_fc_storage) > 0:
                    print(f'    port_role_fc_storage = [')
                    for item in Fabric_A_port_role_fc_storage:
                        print(f'      {item_count} = ''{')
                        for k, v in item.items():
                            if k == 'admin_speed':
                                print(f'        admin_speed   = "{v}"')
                            elif k == 'fill_pattern':
                                print(f'        fill_pattern  = "{v}"')
                            elif k == 'port_id':
                                print(f'        port_list     = "{v}"')
                            elif k == 'slot_id':
                                print(f'        slot_id       = 1')
                            elif k == 'vsan_id':
                                print(f'        vsan_fabric_a = "{v}"')
                                print(f'        vsan_fabric_b = "{Fabric_B_port_role_fc_storage[item_count].get("vsan_id")}"')
                        print('      }')
                        item_count += 1
                    print(f'    ]')
                item_count = 0
                if len(Fabric_A_port_role_fc_uplink) > 0:
                    print(f'    port_role_fc_uplinks = [')
                    for item in Fabric_A_port_role_fc_uplink:
                        print(f'      {item_count} = ''{')
                        for k, v in item.items():
                            if k == 'admin_speed':
                                print(f'        admin_speed   = "{v}"')
                            elif k == 'fill_pattern':
                                print(f'        fill_pattern  = "{v}"')
                            elif k == 'port_id':
                                print(f'        port_list     = "{v}"')
                            elif k == 'slot_id':
                                print(f'        slot_id       = 1')
                            elif k == 'vsan_id':
                                print(f'        vsan_fabric_a = "{v}"')
                                print(f'        vsan_fabric_b = "{Fabric_B_port_role_fc_uplink[item_count].get("vsan_id")}"')
                        print('      }')
                        item_count += 1
                    print(f'    ]')
                item_count = 0
                if len(port_role_fcoe_uplinks) > 0:
                    print(f'    port_role_fcoe_uplinks = [')
                    for item in port_role_fcoe_uplinks:
                        print(f'      {item_count} = ''{')
                        item_count += 1
                        for k, v in item.items():
                            if k == 'admin_speed':
                                print(f'        admin_speed         = "{v}"')
                            elif k == 'fec':
                                print(f'        fec                 = "{v}"')
                            elif k == 'link_control_policy':
                                print(f'        link_control_policy = "{v}"')
                            elif k == 'port_id':
                                print(f'        port_list           = "{v}"')
                            elif k == 'slot_id':
                                print(f'        slot_id             = 1')
                        print('      }')
                    print(f'    ]')
                if len(port_role_servers) > 0:
                    print(f'    port_role_servers = [')
                    for item in port_role_servers:
                        print(f'      {item_count} = ''{')
                        item_count += 1
                        for k, v in item.items():
                            if k == 'port_list':
                                print(f'        port_list           = "{v}"')
                            if k == 'slot_id':
                                print(f'        slot_id             = {v}')
                        print('      }')
                    print(f'    ]')
                print(f'\n-------------------------------------------------------------------------------------------\n')
                valid_confirm = False
                while valid_confirm == False:
                    confirm_policy = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                    if confirm_policy == 'Y' or confirm_policy == '':
                        confirm_policy = 'Y'

                        polVars["port_channel_appliances"] = port_channel_appliances
                        polVars["port_channel_ethernet_uplinks"] = port_channel_ethernet_uplinks
                        polVars["port_channel_fcoe_uplinks"] = port_channel_fcoe_uplinks
                        polVars["port_role_appliances"] = port_role_appliances
                        polVars["port_role_ethernet_uplinks"] = port_role_ethernet_uplinks
                        polVars["port_role_fcoe_uplinks"] = port_role_fcoe_uplinks
                        polVars["port_role_servers"] = port_role_servers

                        original_name = polVars["name"]
                        polVars["name"] = '%s_A' % (original_name)
                        polVars["port_channel_fc_uplinks"] = Fabric_A_fc_port_channels
                        polVars["port_role_fc_storage"] = Fabric_A_port_role_fc_storage
                        polVars["port_role_fc_uplinks"] = Fabric_A_port_role_fc_uplink

                        # Write Policies to Template File
                        polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                        ezfunctions.write_to_template(self, **polVars)

                        polVars["name"] = '%s_B' % (original_name)
                        polVars["port_channel_fc_uplinks"] = Fabric_B_fc_port_channels
                        polVars["port_role_fc_storage"] = Fabric_B_port_role_fc_storage
                        polVars["port_role_fc_uplinks"] = Fabric_B_port_role_fc_uplink

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

        # Close the Template file
        polVars["template_file"] = 'template_close.jinja2'
        ezfunctions.write_to_template(self, **polVars)

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
                ezfunctions.policy_description = []
                for y in x:
                    y = y.capitalize()
                    ezfunctions.policy_description.append(y)
                ezfunctions.policy_description = " ".join(ezfunctions.policy_description)
                ezfunctions.policy_description = ezfunctions.policy_description.replace('Wwnn', 'WWNN')
                ezfunctions.policy_description = ezfunctions.policy_description.replace('Wwpn', 'WWPN')
                ezfunctions.policy_description = ezfunctions.policy_description.replace('Vsan', 'VSAN')
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'   There were no {ezfunctions.policy_description} found.')
                print(f'\n-------------------------------------------------------------------------------------------\n')

                if 'Policies' in ezfunctions.policy_description:
                    ezfunctions.policy_description = ezfunctions.policy_description.replace('Policies', 'Policy')
                elif 'Pools' in ezfunctions.policy_description:
                    ezfunctions.policy_description = ezfunctions.policy_description.replace('Pools', 'Pool')
                elif 'Profiles' in ezfunctions.policy_description:
                    ezfunctions.policy_description = ezfunctions.policy_description.replace('Profiles', 'Profile')
                elif 'Templates' in ezfunctions.policy_description:
                    ezfunctions.policy_description = ezfunctions.policy_description.replace('Templates', 'Template')

                if polVars["allow_opt_out"] == True:
                    Question = input(f'Do you want to create a(n) {ezfunctions.policy_description}?  Enter "Y" or "N" [Y]: ')
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
            kwargs = {}
            opSystem = platform.system()
            if os.environ.get('TF_DEST_DIR') is None:
                tfDir = 'Intersight'
            else:
                tfDir = os.environ.get('TF_DEST_DIR')
            if tfDir[-1] == '\\' or tfDir[-1] == '/':
                    tfDir = tfDir[:-1]

            kwargs.update({'opSystem':opSystem,'tfDir':tfDir})

            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  Starting module to create {inner_policy}')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            if inner_policy == 'ethernet_network_control_policies':
                lan.policies(name_prefix, polVars["org"], inner_type).ethernet_network_control_policies(jsonData, easy_jsonData, **kwargs)
            elif inner_policy == 'ethernet_network_group_policies':
                lan.policies(name_prefix, polVars["org"], inner_type).ethernet_network_group_policies(jsonData, easy_jsonData, **kwargs)
            elif inner_policy == 'flow_control_policies':
                p1.policies(name_prefix, polVars["org"], inner_type).flow_control_policies(jsonData, easy_jsonData, **kwargs)
            elif inner_policy == 'link_aggregation_policies':
                p1.policies(name_prefix, polVars["org"], inner_type).link_aggregation_policies(jsonData, easy_jsonData, **kwargs)
            elif inner_policy == 'link_control_policies':
                p1.policies(name_prefix, polVars["org"], inner_type).link_control_policies(jsonData, easy_jsonData, **kwargs)
            elif inner_policy == 'vsan_policies':
                vxan.policies(name_prefix, polVars["org"], inner_type).vsan_policies(jsonData, easy_jsonData, **kwargs)

def port_list_eth(jsonData, easy_jsonData, name_prefix, **polVars):
    port_channels = []
    port_roles = []
    port_count = 1
    ports_in_use = polVars["ports_in_use"]
    if  len(polVars["fc_converted_ports"]) > 0:
        fc_count = len(polVars["fc_converted_ports"])
    else:
        fc_count = 0
    if polVars["port_type"] == 'Appliance Port-Channel' and polVars["device_model"] == 'UCS-FI-64108':
        portx = '99,100'
    elif polVars["port_type"] == 'Appliance Port-Channel':
        portx = '51,52'
    elif polVars["port_type"] == 'Ethernet Uplink Port-Channel' and polVars["device_model"] == 'UCS-FI-64108':
        portx = '97,98'
    elif polVars["port_type"] == 'Ethernet Uplink Port-Channel':
        portx = '49,50'
    elif polVars["port_type"] == 'FCoE Uplink Port-Channel' and polVars["device_model"] == 'UCS-FI-64108':
        portx = '101,102'
    elif polVars["port_type"] == 'FCoE Uplink Port-Channel':
        portx = '53,54'
    elif polVars["port_type"] == 'Appliance Ports' and polVars["device_model"] == 'UCS-FI-64108':
        portx = '99'
    elif polVars["port_type"] == 'Appliance Ports':
        portx = '51'
    elif polVars["port_type"] == 'Ethernet Uplink' and polVars["device_model"] == 'UCS-FI-64108':
        portx = '97'
    elif polVars["port_type"] == 'Ethernet Uplink':
        portx = '49'
    elif polVars["port_type"] == 'FCoE Uplink' and polVars["device_model"] == 'UCS-FI-64108':
        portx = '101'
    elif polVars["port_type"] == 'FCoE Uplink':
        portx = '53'
    elif polVars["port_type"] == 'Server Ports' and polVars["device_model"] == 'UCS-FI-64108':
        portx = f'{fc_count + 1}-36'
    elif polVars["port_type"] == 'Server Ports':
        portx = f'{fc_count + 1}-18'
    if re.search('(Ethernet Uplink Port-Channel|Server Ports)', polVars["port_type"]):
        default_answer = 'Y'
    else:
        default_answer = 'N'
    valid = False
    while valid == False:
        if polVars["port_type"] == 'Server Ports':
            question = input(f'Do you want to configure {polVars["port_type"]}?  Enter "Y" or "N" [{default_answer}]: ')
        else:
            question = input(f'Do you want to configure an {polVars["port_type"]}?  Enter "Y" or "N" [{default_answer}]: ')
        if question == 'Y' or (default_answer == 'Y' and question == ''):
            configure_valid = False
            while configure_valid == False:
                print(f'\n------------------------------------------------------\n')
                print(f'  The Port List can be in the format of:')
                print(f'     5 - Single Port')
                print(f'     5-10 - Range of Ports')
                print(f'     5,11,12,13,14,15 - List of Ports')
                print(f'     5-10,20-30 - Ranges and Lists of Ports')
                print(f'\n------------------------------------------------------\n')
                port_list = input(f'Please enter the list of ports you want to add to the {polVars["port_type"]}?  [{portx}]: ')
                if port_list == '': port_list = portx

                print('matching port list')
                if re.search(r'(^\d+$|^\d+,{1,48}\d+$|^(\d+[\-,\d+]+){1,48}\d+$)', port_list):
                    original_port_list = port_list
                    ports_expanded = ezfunctions.vlan_list_full(port_list)
                    port_list = []
                    for x in ports_expanded:
                        port_list.append(int(x))
                    port_overlap_count = 0
                    port_overlap = []
                    for x in ports_in_use:
                        for y in port_list:
                            if int(x) == int(y):
                                port_overlap_count += 1
                                port_overlap.append(x)
                    if port_overlap_count == 0:
                        if polVars["device_model"] == 'UCS-FI-64108': max_port = 108
                        else: max_port = 54
                        if polVars["fc_mode"] == 'Y': min_port = int(polVars["fc_ports"][1]) + 1
                        else: min_port = 1
                        for port in port_list:
                            valid_ports = validating.number_in_range('Port Range', port, min_port, max_port)
                            if valid_ports == False:
                                break
                        if valid_ports == True:
                            # Prompt User for the Admin Speed of the Port
                            if not polVars["port_type"] == 'Server Ports':
                                polVars["multi_select"] = False
                                jsonVars = jsonData['components']['schemas']['fabric.TransceiverRole']['allOf'][1]['properties']
                                polVars["var_description"] = jsonVars['AdminSpeed']['description']
                                polVars["jsonVars"] = jsonVars['AdminSpeed']['enum']
                                polVars["defaultVar"] = jsonVars['AdminSpeed']['default']
                                polVars["varType"] = 'Admin Speed'
                                polVars["admin_speed"] = ezfunctions.variablesFromAPI(**polVars)

                            if re.search('^(Appliance Appliance Ports|(Ethernet|FCoE) Uplink)$', polVars["port_type"]):
                                # Prompt User for the FEC Mode of the Port
                                polVars["var_description"] = jsonVars['Fec']['description']
                                polVars["jsonVars"] = sorted(jsonVars['Fec']['enum'])
                                polVars["defaultVar"] = jsonVars['Fec']['default']
                                polVars["varType"] = 'Fec Mode'
                                polVars["fec"] = ezfunctions.variablesFromAPI(**polVars)

                            if re.search('(Appliance Port-Channel|Appliance Ports)', polVars["port_type"]):
                                # Prompt User for the Mode of the Port
                                jsonVars = jsonData['components']['schemas']['fabric.AppliancePcRole']['allOf'][1]['properties']
                                polVars["var_description"] = jsonVars['Mode']['description']
                                polVars["jsonVars"] = sorted(jsonVars['Mode']['enum'])
                                polVars["defaultVar"] = jsonVars['Mode']['default']
                                polVars["varType"] = 'Mode'
                                polVars["mode"] = ezfunctions.variablesFromAPI(**polVars)

                                polVars["var_description"] = jsonVars['Priority']['description']
                                polVars["jsonVars"] = sorted(jsonVars['Priority']['enum'])
                                polVars["defaultVar"] = jsonVars['Priority']['default']
                                polVars["varType"] = 'Priority'
                                polVars["priority"] = ezfunctions.variablesFromAPI(**polVars)

                            # Prompt User for the
                            if re.search('(Appliance Port-Channel|Appliance Ports)', polVars["port_type"]):
                                policy_list = [
                                    'policies.ethernet_network_control_policies.ethernet_network_control_policy',
                                    'policies.ethernet_network_group_policies.ethernet_network_group_policy',
                                ]
                            elif re.search('Ethernet Uplink', polVars["port_type"]):
                                policy_list = [
                                    'policies.ethernet_network_group_policies.ethernet_network_group_policy',
                                    'policies.flow_control_policies.flow_control_policy',
                                    'policies.link_aggregation_policies.link_aggregation_policy',
                                    'policies.link_control_policies.link_control_policy',
                                ]
                            elif re.search('(FCoE Uplink Port-Channel|FCoE Uplink)', polVars["port_type"]):
                                policy_list = [
                                    'policies.link_aggregation_policies.link_aggregation_policy',
                                    'policies.link_control_policies.link_control_policy',
                                ]
                            polVars["allow_opt_out"] = False
                            if not polVars["port_type"] == 'Server Ports':
                                for policy in policy_list:
                                    policy_short = policy.split('.')[2]
                                    polVars[policy_short],policyData = policy_select_loop(jsonData, easy_jsonData, name_prefix, policy, **polVars)
                                    polVars.update(policyData)

                            interfaces = []
                            pc_id = port_list[0]
                            for i in port_list:
                                interfaces.append({'port_id':i,'slot_id':1})

                            if polVars["port_type"] == 'Appliance Port-Channel':
                                port_channel = {
                                    'admin_speed':polVars["admin_speed"],
                                    'ethernet_network_control_policy':polVars["ethernet_network_control_policy"],
                                    'ethernet_network_group_policy':polVars["ethernet_network_group_policy"],
                                    'interfaces':interfaces,
                                    'mode':polVars["mode"],
                                    'pc_id':pc_id,
                                    'priority':polVars["priority"]
                                }
                            elif polVars["port_type"] == 'Ethernet Uplink Port-Channel':
                                port_channel = {
                                    'admin_speed':polVars["admin_speed"],
                                    'ethernet_network_group_policy':polVars["ethernet_network_group_policy"],
                                    'flow_control_policy':polVars["flow_control_policy"],
                                    'interfaces':interfaces,
                                    'link_aggregation_policy':polVars["link_aggregation_policy"],
                                    'link_control_policy':polVars["link_control_policy"],
                                    'pc_id':pc_id,
                                }
                            elif polVars["port_type"] == 'FCoE Uplink Port-Channel':
                                port_channel = {
                                    'admin_speed':polVars["admin_speed"],
                                    'interfaces':interfaces,
                                    'link_aggregation_policy':polVars["link_aggregation_policy"],
                                    'link_control_policy':polVars["link_control_policy"],
                                    'pc_id':pc_id,
                                }
                            elif polVars["port_type"] == 'Appliance Ports':
                                port_role = {
                                    'admin_speed':polVars["admin_speed"],
                                    'ethernet_network_control_policy':polVars["ethernet_network_control_policy"],
                                    'ethernet_network_group_policy':polVars["ethernet_network_group_policy"],
                                    'fec':polVars["fec"],
                                    'mode':polVars["mode"],
                                    'port_id':original_port_list,
                                    'priority':polVars["priority"],
                                    'slot_id':1
                                }
                            elif polVars["port_type"] == 'Ethernet Uplink':
                                port_role = {
                                    'admin_speed':polVars["admin_speed"],
                                    'ethernet_network_group_policy':polVars["ethernet_network_group_policy"],
                                    'fec':polVars["fec"],
                                    'flow_control_policy':polVars["flow_control_policy"],
                                    'link_control_policy':polVars["link_control_policy"],
                                    'port_id':original_port_list,
                                    'slot_id':1
                                }
                            elif polVars["port_type"] == 'FCoE Uplink':
                                port_role = {
                                    'admin_speed':polVars["admin_speed"],
                                    'fec':polVars["fec"],
                                    'link_control_policy':polVars["link_control_policy"],
                                    'port_id':original_port_list,
                                    'slot_id':1
                                }
                            elif polVars["port_type"] == 'Server Ports':
                                server_ports = {
                                    'port_list':original_port_list,
                                    'slot_id':1
                                }
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            if not polVars["port_type"] == 'Server Ports':
                                print(f'    admin_speed                     = "{polVars["admin_speed"]}"')
                            if re.search('Appliance', polVars["port_type"]):
                                print(f'    ethernet_network_control_policy = "{polVars["ethernet_network_control_policy"]}"')
                            if re.search('(Appliance|Ethernet)', polVars["port_type"]):
                                print(f'    ethernet_network_group_policy   = "{polVars["ethernet_network_group_policy"]}"')
                            if re.search('Ethernet', polVars["port_type"]):
                                print(f'    flow_control_policy             = "{polVars["flow_control_policy"]}"')
                            if re.search('(Ethernet|FCoE) Uplink Port-Channel', polVars["port_type"]):
                                print(f'    link_aggregation_policy         = "{polVars["link_aggregation_policy"]}"')
                            if re.search('(Ethernet|FCoE)', polVars["port_type"]):
                                print(f'    link_control_policy             = "{polVars["link_control_policy"]}"')
                            if re.search('Port-Channel', polVars["port_type"]):
                                print(f'    interfaces = [')
                                for item in interfaces:
                                    print('      {')
                                    for k, v in item.items():
                                        print(f'        {k} = {v}')
                                    print('      }')
                                print(f'    ]')
                            if re.search('Appliance', polVars["port_type"]):
                                print(f'    mode      = "{polVars["mode"]}"')
                            if re.search('Port-Channel', polVars["port_type"]):
                                print(f'    pc_id     = {pc_id}')
                            if re.search('Appliance', polVars["port_type"]):
                                print(f'    priority  = "{polVars["priority"]}"')
                            if re.search('^(Appliance Ports|(Ethernet|FCoE) Uplink|Server Ports)$', polVars["port_type"]):
                                print(f'    port_list = {original_port_list}')
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            valid_confirm = False
                            while valid_confirm == False:
                                confirm_port = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                                if confirm_port == 'Y' or confirm_port == '':
                                    if re.search('Port-Channel', polVars["port_type"]):
                                        port_channels.append(port_channel)
                                    elif re.search('^(Appliance Ports|(Ethernet|FCoE) Uplink)$', polVars["port_type"]):
                                        port_roles.append(port_role)
                                    elif polVars["port_type"] == 'Server Ports':
                                        port_roles.append(server_ports)
                                    for i in port_list:
                                        polVars["ports_in_use"].append(i)

                                    valid_exit = False
                                    while valid_exit == False:
                                        port_exit = input(f'Would You like to Configure another {polVars["port_type"]}?  Enter "Y" or "N" [N]: ')
                                        if port_exit == 'Y':
                                            port_count += 1
                                            valid_confirm = True
                                            valid_exit = True
                                        elif port_exit == 'N' or port_exit == '':
                                            configure_valid = True
                                            valid = True
                                            valid_confirm = True
                                            valid_exit = True
                                        else:
                                            print(f'\n------------------------------------------------------\n')
                                            print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                                            print(f'\n------------------------------------------------------\n')

                                elif confirm_port == 'N':
                                    print(f'\n-------------------------------------------------------------------------------------------\n')
                                    print(f'  Starting {polVars["port_type"]} Configuration Over.')
                                    print(f'\n-------------------------------------------------------------------------------------------\n')
                                    valid_confirm = True
                                else:
                                    print(f'\n------------------------------------------------------\n')
                                    print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                                    print(f'\n------------------------------------------------------\n')

                    else:
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        print(f'  Error!! The following Ports are already in use: {port_overlap}.')
                        print(f'\n-------------------------------------------------------------------------------------------\n')

                else:
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  Error!! Invalid Port Range.  A port Range should be in the format 49-50 for example.')
                    print(f'  The following port range is invalid: "{port_list}"')
                    print(f'\n-------------------------------------------------------------------------------------------\n')

        elif question == 'N'  or (default_answer == 'N' and question == ''):
            valid = True
        else:
            print(f'\n------------------------------------------------------\n')
            print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
            print(f'\n------------------------------------------------------\n')

    if re.search('Port-Channel', polVars["port_type"]):
        return port_channels,ports_in_use
    elif re.search('^(Appliance Ports|(Ethernet|FCoE) Uplink|Server Ports)$', polVars["port_type"]):
        return port_roles,ports_in_use
    
def port_list_fc(jsonData, easy_jsonData, name_prefix, **polVars):
    fill_pattern_descr = 'For Cisco UCS 6400 Series fabric interconnect, if the FC uplink speed is 8 Gbps, set the '\
        'fill pattern as IDLE on the uplink switch. If the fill pattern is not set as IDLE, FC '\
        'uplinks operating at 8 Gbps might go to an errDisabled state, lose SYNC intermittently, or '\
        'notice errors or bad packets.  For speeds greater than 8 Gbps we recommend Arbff.  Below '\
        'is a configuration example on MDS to match this setting:\n\n'\
        'mds-a(config-if)# switchport fill-pattern IDLE speed 8000\n'\
        'mds-a(config-if)# show port internal inf interface fc1/1 | grep FILL\n'\
        '  FC_PORT_CAP_FILL_PATTERN_8G_CHANGE_CAPABLE (1)\n'\
        'mds-a(config-if)# show run int fc1/16 | incl fill\n\n'\
        'interface fc1/16\n'\
        '  switchport fill-pattern IDLE speed 8000\n\n'\
        'mds-a(config-if)#\n'

    if polVars["port_type"] == 'Fibre-Channel Port-Channel':
        default_answer = 'Y'
    else:
        default_answer = 'N'
    A_port_channels = []
    B_port_channels = []
    A_port_role = []
    B_port_role = []
    fc_ports_in_use = polVars["fc_ports_in_use"]
    port_count = 1
    if len(polVars["fc_converted_ports"]) > 0:
        configure_fc = True
    else:
        configure_fc = False
    if configure_fc == True:
        valid = False
        while valid == False:
            question = input(f'Do you want to configure a {polVars["port_type"]}?  Enter "Y" or "N" [{default_answer}]: ')
            if question == 'Y' or (default_answer == 'Y' and question == ''):
                configure_valid = False
                while configure_valid == False:
                    if polVars["port_type"] == 'Fibre-Channel Port-Channel':
                        polVars["multi_select"] = True
                        polVars["var_description"] = '    Please Select a Port for the Port-Channel:\n'
                    elif polVars["port_type"] == 'Fibre-Channel Storage':
                        polVars["multi_select"] = False
                        polVars["var_description"] = '    Please Select a Port for the Storage Port:\n'
                    else:
                        polVars["multi_select"] = False
                        polVars["var_description"] = '    Please Select a Port for the Uplink Port:\n'
                    polVars["var_type"] = 'Unified Port'
                    port_list = ezfunctions.vars_from_list(polVars["fc_converted_ports"], **polVars)

                    # Prompt User for the Admin Speed of the Port
                    polVars["multi_select"] = False
                    jsonVars = jsonData['components']['schemas']['fabric.FcUplinkPcRole']['allOf'][1]['properties']
                    polVars["var_description"] = jsonVars['AdminSpeed']['description']
                    jsonVars['AdminSpeed']['enum'].remove('Auto')
                    polVars["jsonVars"] = jsonVars['AdminSpeed']['enum']
                    polVars["defaultVar"] = jsonVars['AdminSpeed']['enum'][2]
                    polVars["varType"] = 'Admin Speed'
                    polVars["admin_speed"] = ezfunctions.variablesFromAPI(**polVars)

                    # Prompt User for the Fill Pattern of the Port
                    if not polVars["port_type"] == 'Fibre-Channel Storage':
                        polVars["var_description"] = jsonVars['FillPattern']['description']
                        polVars["var_description"] = '%s\n%s' % (polVars["var_description"], fill_pattern_descr)
                        polVars["jsonVars"] = sorted(jsonVars['FillPattern']['enum'])
                        polVars["defaultVar"] = jsonVars['FillPattern']['enum'][1]
                        polVars["varType"] = 'Fill Pattern'
                        polVars["fill_pattern"] = ezfunctions.variablesFromAPI(**polVars)

                    vsans = {}
                    fabrics = ['Fabric_A', 'Fabric_B']
                    for fabric in fabrics:
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        print(f'  Please Select the VSAN Policy for {fabric}')
                        policy_list = [
                            'policies.vsan_policies.vsan_policy',
                        ]
                        polVars["allow_opt_out"] = False
                        for policy in policy_list:
                            vsan_policy,policyData = policy_select_loop(jsonData, easy_jsonData, name_prefix, policy, **polVars)

                        vsan_list = []
                        for key, value in policyData['vsan_policies'].items():
                            if key == vsan_policy:
                                for k, v in value['vsans'].items():
                                    for y, val in v.items():
                                        if y == 'vsan_id':
                                            vsan_list.append(val)

                        if len(vsan_list) > 1:
                            vsan_list = ','.join(str(vsan_list))
                        else:
                            vsan_list = vsan_list[0]
                        vsan_list = ezfunctions.vlan_list_full(vsan_list)

                        polVars["multi_select"] = False
                        if polVars["port_type"] == 'Fibre-Channel Port-Channel':
                            polVars["var_description"] = '    Please Select a VSAN for the Port-Channel:\n'
                        elif polVars["port_type"] == 'Fibre-Channel Storage':
                            polVars["var_description"] = '    Please Select a VSAN for the Storage Port:\n'
                        else:
                            polVars["var_description"] = '    Please Select a VSAN for the Uplink Port:\n'
                        polVars["var_type"] = 'VSAN'
                        vsan_x = ezfunctions.vars_from_list(vsan_list, **polVars)
                        for vs in vsan_x:
                            vsan = vs
                        vsans.update({fabric:vsan})


                    if polVars["port_type"] == 'Fibre-Channel Port-Channel':
                        interfaces = []
                        for i in port_list:
                            interfaces.append({'port_id':i,'slot_id':1})

                        pc_id = port_list[0]
                        port_channel_a = {
                            'admin_speed':polVars["admin_speed"],
                            'fill_pattern':polVars["fill_pattern"],
                            'interfaces':interfaces,
                            'pc_id':pc_id,
                            'vsan_id':vsans.get("Fabric_A")
                        }
                        port_channel_b = {
                            'admin_speed':polVars["admin_speed"],
                            'fill_pattern':polVars["fill_pattern"],
                            'interfaces':interfaces,
                            'pc_id':pc_id,
                            'vsan_id':vsans.get("Fabric_B")
                        }
                    elif polVars["port_type"] == 'Fibre-Channel Storage':
                        port_list = '%s' % (port_list[0])
                        fc_port_role_a = {
                            'admin_speed':polVars["admin_speed"],
                            'port_id':port_list,
                            'slot_id':1,
                            'vsan_id':vsans["Fabric_A"]
                        }
                        fc_port_role_b = {
                            'admin_speed':polVars["admin_speed"],
                            'port_id':port_list,
                            'slot_id':1,
                            'vsan_id':vsans["Fabric_B"]
                        }
                    else:
                        port_list = '%s' % (port_list[0])
                        fc_port_role_a = {
                            'admin_speed':polVars["admin_speed"],
                            'fill_pattern':polVars["fill_pattern"],
                            'port_id':port_list,
                            'slot_id':1,
                            'vsan_id':vsans["Fabric_A"]
                        }
                        fc_port_role_b = {
                            'admin_speed':polVars["admin_speed"],
                            'fill_pattern':polVars["fill_pattern"],
                            'port_id':port_list,
                            'slot_id':1,
                            'vsan_id':vsans["Fabric_B"]
                        }
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'    admin_speed      = "{polVars["admin_speed"]}"')
                    if not polVars["port_type"] == 'Fibre-Channel Storage':
                        print(f'    fill_pattern     = "{polVars["fill_pattern"]}"')
                    if re.search('Uplink|Storage', polVars["port_type"]):
                        print(f'    port_list        = "{port_list}"')
                    print(f'    vsan_id_fabric_a = {vsans["Fabric_A"]}')
                    print(f'    vsan_id_fabric_b = {vsans["Fabric_B"]}')
                    if polVars["port_type"] == 'Fibre-Channel Port-Channel':
                        print(f'    interfaces = [')
                        for item in interfaces:
                            print('      {')
                            for k, v in item.items():
                                print(f'        {k}          = {v}')
                            print('      }')
                        print(f'    ]')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_port = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                        if confirm_port == 'Y' or confirm_port == '':
                            if polVars["port_type"] == 'Fibre-Channel Port-Channel':
                                A_port_channels.append(port_channel_a)
                                B_port_channels.append(port_channel_b)
                            else:
                                A_port_role.append(fc_port_role_a)
                                B_port_role.append(fc_port_role_b)
                            for i in port_list:
                                fc_ports_in_use.append(i)

                            valid_exit = False
                            while valid_exit == False:
                                port_exit = input(f'Would You like to Configure another {polVars["port_type"]}?  Enter "Y" or "N" [N]: ')
                                if port_exit == 'Y':
                                    port_count += 1
                                    valid_confirm = True
                                    valid_exit = True
                                elif port_exit == 'N' or port_exit == '':
                                    configure_valid = True
                                    valid = True
                                    valid_confirm = True
                                    valid_exit = True
                                else:
                                    print(f'\n------------------------------------------------------\n')
                                    print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                                    print(f'\n------------------------------------------------------\n')

                        elif confirm_port == 'N':
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            print(f'  Starting {polVars["port_type"]} Configuration Over.')
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            valid_confirm = True
                        else:
                            print(f'\n------------------------------------------------------\n')
                            print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                            print(f'\n------------------------------------------------------\n')

            elif question == 'N' or (default_answer == 'N' and question == ''):
                valid = True
            else:
                print(f'\n------------------------------------------------------\n')
                print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                print(f'\n------------------------------------------------------\n')

    if polVars["port_type"] == 'Fibre-Channel Port-Channel':
        return A_port_channels,B_port_channels,fc_ports_in_use
    else:
        return A_port_role,B_port_role,fc_ports_in_use

def port_modes_fc(jsonData, easy_jsonData, name_prefix, **polVars):
    port_modes = {}
    ports_in_use = []
    fc_converted_ports = []
    valid = False
    while valid == False:
        fc_mode = input('Do you want to convert ports to Fibre-Channel Mode?  Enter "Y" or "N" [Y]: ')
        if fc_mode == '' or fc_mode == 'Y':
            fc_mode = 'Y'
            jsonVars = easy_jsonData['policies']['fabric.PortPolicy']
            polVars["var_description"] = jsonVars['unifiedPorts']['description']
            polVars["jsonVars"] = jsonVars['unifiedPorts']['enum']
            polVars["defaultVar"] = jsonVars['unifiedPorts']['default']
            polVars["varType"] = 'Unified Port Ranges'
            fc_ports = ezfunctions.variablesFromAPI(**polVars)
            x = fc_ports.split('-')
            fc_ports = [int(x[0]),int(x[1])]
            for i in range(int(x[0]), int(x[1]) + 1):
                ports_in_use.append(i)
                fc_converted_ports.append(i)
            port_modes = {'custom_mode':'FibreChannel','port_list':fc_ports,'slot_id':1}
            valid = True
        elif fc_mode == 'N':
            fc_ports = []
            port_modes = {'custom_mode':'FibreChannel','port_list':fc_ports,'slot_id':1}
            valid = True
        else:
            print(f'\n------------------------------------------------------\n')
            print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
            print(f'\n------------------------------------------------------\n')
    
    return fc_mode,ports_in_use,fc_converted_ports,port_modes
