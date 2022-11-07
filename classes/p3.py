#!/usr/bin/env python3
from copy import deepcopy
import ezfunctions
import jinja2
import os
import pkg_resources
import re
import stdiomask
import validating

ucs_template_path = pkg_resources.resource_filename('p3', '../templates/')

class policies(object):
    def __init__(self, name_prefix, org, type):
        self.templateLoader = jinja2.FileSystemLoader(
            searchpath=(ucs_template_path + '%s/') % (type))
        self.templateEnv = jinja2.Environment(loader=self.templateLoader)
        self.name_prefix = name_prefix
        self.org = org
        self.type = type

    #==============================================
    # Power Policy Module
    #==============================================
    def power_policies(self, jsonData, ezData, **kwargs):
        name_prefix = self.name_prefix
        opSystem = kwargs['opSystem']
        org = self.org
        policy_type = 'Power Policy'
        polVars = {}
        polVars["header"] = '%s Variables' % (policy_type)
        polVars["initial_write"] = True
        polVars["org"] = org
        polVars["policy_type"] = policy_type
        polVars["template_file"] = 'template_open.jinja2'
        polVars["template_type"] = 'power_policies'
        tfDir = kwargs['tfDir']

        # Open the Template file
        ezfunctions.write_to_template(self, **polVars)
        polVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  A {policy_type} will configure the Power Redundancy Policies for Chassis and Servers.')
            print(f'  For Servers it will configure the Power Restore State.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            if opSystem == 'Windows':
                print(f'  - {tfDir}\\{org}\\{self.type}\\{polVars["template_type"]}.auto.tfvars')
            else:
                print(f'  - {tfDir}/{org}/{self.type}/{polVars["template_type"]}.auto.tfvars')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            loop_count = 1
            policy_loop = False
            while policy_loop == False:

                print('staring loop again')
                polVars["multi_select"] = False
                polVars["var_description"] = ezData['policies']['power.Policy']['systemType']['description']
                polVars["jsonVars"] = sorted(ezData['policies']['power.Policy']['systemType']['enum'])
                polVars["defaultVar"] = ezData['policies']['power.Policy']['systemType']['default']
                polVars["varType"] = 'System Type'
                system_type = ezfunctions.variablesFromAPI(**polVars)

                if not name_prefix == '':
                    name = '%s_%s' % (name_prefix, system_type)
                else:
                    name = '%s_%s' % (org, system_type)

                polVars["name"] = ezfunctions.policy_name(name, policy_type)
                polVars["descr"] = ezfunctions.policy_descr(polVars["name"], policy_type)

                polVars["multi_select"] = False
                jsonVars = jsonData['power.Policy']['allOf'][1]['properties']

                if system_type == '9508':
                    valid = False
                    while valid == False:
                        polVars["power_allocation"] = input('What is the Power Budget you would like to Apply?\n'
                            'This should be a value between 2800 Watts and 16800 Watts. [5600]: ')
                        if polVars["power_allocation"] == '':
                            polVars["power_allocation"] = 5600
                        valid = validating.number_in_range('Chassis Power Budget', polVars["power_allocation"], 2800, 16800)

                    polVars["var_description"] = jsonVars['DynamicRebalancing']['description']
                    polVars["jsonVars"] = sorted(jsonVars['DynamicRebalancing']['enum'])
                    polVars["defaultVar"] = jsonVars['DynamicRebalancing']['default']
                    polVars["varType"] = 'Dynamic Power Rebalancing'
                    polVars["dynamic_power_rebalancing"] = ezfunctions.variablesFromAPI(**polVars)

                    polVars["var_description"] = jsonVars['PowerSaveMode']['description']
                    polVars["jsonVars"] = sorted(jsonVars['PowerSaveMode']['enum'])
                    polVars["defaultVar"] = jsonVars['PowerSaveMode']['default']
                    polVars["varType"] = 'Power Save Mode'
                    polVars["power_save_mode"] = ezfunctions.variablesFromAPI(**polVars)

                else:
                    polVars["power_allocation"] = 0
                    polVars["dynamic_power_rebalancing"] = 'Enabled'
                    polVars["power_save_mode"] = 'Enabled'

                if system_type == 'Server':
                    polVars["var_description"] = jsonVars['PowerPriority']['description']
                    polVars["jsonVars"] = sorted(jsonVars['PowerPriority']['enum'])
                    polVars["defaultVar"] = jsonVars['PowerPriority']['default']
                    polVars["varType"] = 'Power Priority'
                    polVars["power_priority"] = ezfunctions.variablesFromAPI(**polVars)

                    polVars["var_description"] = jsonVars['PowerProfiling']['description']
                    polVars["jsonVars"] = sorted(jsonVars['PowerProfiling']['enum'])
                    polVars["defaultVar"] = jsonVars['PowerProfiling']['default']
                    polVars["varType"] = 'Power Profiling'
                    polVars["power_profiling"] = ezfunctions.variablesFromAPI(**polVars)

                    polVars["var_description"] = jsonVars['PowerRestoreState']['description']
                    polVars["jsonVars"] = sorted(jsonVars['PowerRestoreState']['enum'])
                    polVars["defaultVar"] = jsonVars['PowerRestoreState']['default']
                    polVars["varType"] = 'Power Restore'
                    polVars["power_restore"] = ezfunctions.variablesFromAPI(**polVars)

                if system_type == '5108':
                    polVars["popList"] = ['N+2']
                elif system_type == 'Server':
                    polVars["popList"] = ['N+1','N+2']
                polVars["var_description"] = jsonVars['RedundancyMode']['description']
                polVars["jsonVars"] = sorted(jsonVars['RedundancyMode']['enum'])
                polVars["defaultVar"] = jsonVars['RedundancyMode']['default']
                polVars["varType"] = 'Power Redundancy Mode'
                polVars["power_redundancy"] = ezfunctions.variablesFromAPI(**polVars)

                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'   description               = "{polVars["descr"]}"')
                print(f'   name                      = "{polVars["name"]}"')
                if system_type == '9508':
                    # print(f'   dynamic_power_rebalancing = "{polVars["dynamic_power_rebalancing"]}"')
                    print(f'   power_allocation          = {polVars["power_allocation"]}')
                    # print(f'   power_save_mode           = "{polVars["power_save_mode"]}"')
                if system_type == 'Server':
                    # print(f'   power_priority            = "{polVars["power_priority"]}"')
                    print(f'   power_profiling           = "{polVars["power_profiling"]}"')
                    print(f'   power_restore             = "{polVars["power_restore"]}"')
                print(f'   power_redundancy          = "{polVars["power_redundancy"]}"')
                print(f'\n-------------------------------------------------------------------------------------------\n')
                valid_confirm = False
                while valid_confirm == False:
                    confirm_policy = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                    if confirm_policy == 'Y' or confirm_policy == '':
                        confirm_policy = 'Y'

                        # Write Policies to Template File
                        polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                        ezfunctions.write_to_template(self, **polVars)

                        if loop_count < 3:
                            configure_loop, policy_loop = ezfunctions.exit_default_yes(polVars["policy_type"])
                        else:
                            configure_loop, policy_loop = ezfunctions.exit_default_no(polVars["policy_type"])
                        loop_count += 1
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
    # SD Card Policy Module
    #==============================================
    def sd_card_policies(self, jsonData, ezData, **kwargs):
        name_prefix = self.name_prefix
        name_suffix = 'sdcard'
        opSystem = kwargs['opSystem']
        org = self.org
        policy_type = 'SD Card Policy'
        polVars = {}
        polVars["header"] = '%s Variables' % (policy_type)
        polVars["initial_write"] = True
        polVars["org"] = org
        polVars["policy_type"] = policy_type
        polVars["template_file"] = 'template_open.jinja2'
        polVars["template_type"] = 'sd_card_policies'
        tfDir = kwargs['tfDir']

        # Open the Template file
        ezfunctions.write_to_template(self, **polVars)
        polVars["initial_write"] = False

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

                    polVars["name"] = ezfunctions.policy_name(name, policy_type)
                    polVars["descr"] = ezfunctions.policy_descr(polVars["name"], policy_type)

                    polVars["priority"] = 'auto'
                    polVars["receive"] = 'Disabled'
                    polVars["send"] = 'Disabled'

                    # Write Policies to Template File
                    polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                    ezfunctions.write_to_template(self, **polVars)

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
        polVars["template_file"] = 'template_close.jinja2'
        ezfunctions.write_to_template(self, **polVars)

    #==============================================
    # Serial over LAN Policy Module
    #==============================================
    def serial_over_lan_policies(self, jsonData, ezData, **kwargs):
        name_prefix = self.name_prefix
        name_suffix = 'sol'
        opSystem = kwargs['opSystem']
        org = self.org
        policy_type = 'Serial over LAN Policy'
        polVars = {}
        polVars["header"] = '%s Variables' % (policy_type)
        polVars["initial_write"] = True
        polVars["org"] = org
        polVars["policy_type"] = policy_type
        polVars["template_file"] = 'template_open.jinja2'
        polVars["template_type"] = 'serial_over_lan_policies'
        tfDir = kwargs['tfDir']

        # Open the Template file
        ezfunctions.write_to_template(self, **polVars)
        polVars["initial_write"] = False

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
                    polVars["enabled"] = True

                    polVars["multi_select"] = False
                    jsonVars = jsonData['sol.Policy']['allOf'][1]['properties']
                    polVars["var_description"] = jsonVars['BaudRate']['description']
                    polVars["jsonVars"] = sorted(jsonVars['BaudRate']['enum'])
                    polVars["defaultVar"] = jsonVars['BaudRate']['default']
                    polVars["varType"] = 'Baud Rate'
                    polVars["baud_rate"] = ezfunctions.variablesFromAPI(**polVars)

                    polVars["var_description"] = jsonVars['ComPort']['description']
                    polVars["jsonVars"] = sorted(jsonVars['ComPort']['enum'])
                    polVars["defaultVar"] = jsonVars['ComPort']['default']
                    polVars["varType"] = 'Com Port'
                    polVars["com_port"] = ezfunctions.variablesFromAPI(**polVars)

                    valid = False
                    while valid == False:
                        polVars["ssh_port"] = input('What is the SSH Port you would like to assign?\n'
                            'This should be a value between 1024-65535. [2400]: ')
                        if polVars["ssh_port"] == '':
                            polVars["ssh_port"] = 2400
                        valid = validating.number_in_range('SSH Port', polVars["ssh_port"], 1024, 65535)

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'   baud_rate   = "{polVars["baud_rate"]}"')
                    print(f'   com_port    = "{polVars["com_port"]}"')
                    print(f'   description = "{polVars["descr"]}"')
                    print(f'   enabled     = "{polVars["enabled"]}"')
                    print(f'   name        = "{polVars["name"]}"')
                    print(f'   ssh_port    = "{polVars["ssh_port"]}"')
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
    # SMTP Policy Module
    #==============================================
    def smtp_policies(self, jsonData, ezData, **kwargs):
        name_prefix = self.name_prefix
        name_suffix = 'smtp'
        opSystem = kwargs['opSystem']
        org = self.org
        policy_type = 'SMTP Policy'
        polVars = {}
        polVars["header"] = '%s Variables' % (policy_type)
        polVars["initial_write"] = True
        polVars["org"] = org
        polVars["policy_type"] = policy_type
        polVars["template_file"] = 'template_open.jinja2'
        polVars["template_type"] = 'smtp_policies'
        tfDir = kwargs['tfDir']

        # Open the Template file
        ezfunctions.write_to_template(self, **polVars)
        polVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  An {policy_type} sends server faults as email alerts to the configured SMTP server.')
            print(f'  You can specify the preferred settings for outgoing communication and select the fault ')
            print(f'  severity level to report and the mail recipients.\n\n')
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
                    polVars["enable_smtp"] = True

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  IP address or hostname of the SMTP server. The SMTP server is used by the managed device ')
                    print(f'  to send email notifications.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid = False
                    while valid == False:
                        polVars["smtp_server_address"] = input('What is the SMTP Server Address? ')
                        if re.search(r'^[a-zA-Z0-9]:', polVars["smtp_server_address"]):
                            valid = validating.ip_address('SMTP Server Address', polVars["smtp_server_address"])
                        if re.search(r'[a-zA-Z]', polVars["smtp_server_address"]):
                            valid = validating.dns_name('SMTP Server Address', polVars["smtp_server_address"])
                        elif re.search (r'^([0-9]{1,3}\.){3}[0-9]{1,3}$'):
                            valid = validating.ip_address('SMTP Server Address', polVars["smtp_server_address"])
                        else:
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            print(f'  "{polVars["smtp_server_address"]}" is not a valid address.')
                            print(f'\n-------------------------------------------------------------------------------------------\n')

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  Port number used by the SMTP server for outgoing SMTP communication.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid = False
                    while valid == False:
                        polVars["smtp_port"] = input('What is the SMTP Port?  [25]: ')
                        if polVars["smtp_port"] == '':
                            polVars["smtp_port"] = 25
                        if re.search(r'[\d]+', str(polVars["smtp_port"])):
                            valid = validating.number_in_range('SMTP Port', polVars["smtp_port"], 1, 65535)
                        else:
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            print(f'  "{polVars["smtp_port"]}" is not a valid port.')
                            print(f'\n-------------------------------------------------------------------------------------------\n')

                    polVars["multi_select"] = False
                    jsonVars = jsonData['smtp.Policy']['allOf'][1]['properties']
                    polVars["var_description"] = jsonVars['MinSeverity']['description']
                    polVars["jsonVars"] = sorted(jsonVars['MinSeverity']['enum'])
                    polVars["defaultVar"] = jsonVars['MinSeverity']['default']
                    polVars["varType"] = 'Minimum Severity'
                    polVars["minimum_severity"] = ezfunctions.variablesFromAPI(**polVars)

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  The email address entered here will be displayed as the from address (mail received from ')
                    print(f'  address) of all the SMTP mail alerts that are received. If not configured, the hostname ')
                    print(f'  of the server is used in the from address field.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid = False
                    while valid == False:
                        polVars["smtp_alert_sender_address"] = input(f'What is the SMTP Alert Sender Address?  '\
                            '[press enter to use server hostname]: ')
                        if polVars["smtp_alert_sender_address"] == '':
                            polVars["smtp_alert_sender_address"] = ''
                            valid = True
                        else:
                            valid = validating.email('SMTP Alert Sender Address', polVars["smtp_alert_sender_address"])

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  List of email addresses that will receive notifications for faults.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    polVars["mail_alert_recipients"] = []
                    valid = False
                    while valid == False:
                        mail_recipient = input(f'What is address you would like to send these notifications to?  ')
                        valid_email = validating.email('Mail Alert Recipient', mail_recipient)
                        if valid_email == True:
                            polVars["mail_alert_recipients"].append(mail_recipient)
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
                    print(f'    description               = "{polVars["descr"]}"')
                    print(f'    enable_smtp                   = {polVars["enable_smtp"]}')
                    print(f'    mail_alert_recipients     = [')
                    for x in polVars["mail_alert_recipients"]:
                        print(f'      "{x}",')
                    print(f'    ]')
                    print(f'    minimum_severity          = "{polVars["minimum_severity"]}"')
                    print(f'    name                      = "{polVars["name"]}"')
                    print(f'    smtp_alert_sender_address = "{polVars["smtp_alert_sender_address"]}"')
                    print(f'    smtp_port                 = {polVars["smtp_port"]}')
                    print(f'    smtp_server_address       = "{polVars["smtp_server_address"]}"')
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
    # SNMP Policy Module
    #==============================================
    def snmp_policies(self, jsonData, ezData, **kwargs):
        name_prefix = self.name_prefix
        name_suffix = 'snmp'
        opSystem = kwargs['opSystem']
        org = self.org
        policy_type = 'SNMP Policy'
        polVars = {}
        polVars["header"] = '%s Variables' % (policy_type)
        polVars["initial_write"] = True
        polVars["org"] = org
        polVars["policy_type"] = policy_type
        polVars["template_file"] = 'template_open.jinja2'
        polVars["template_type"] = 'snmp_policies'
        tfDir = kwargs['tfDir']

        # Open the Template file
        ezfunctions.write_to_template(self, **polVars)
        polVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  An {policy_type} will configure chassis, domains, and servers with SNMP parameters.')
            print(f'  This Policy is not required to standup a server but is a good practice for day 2 support.')
            print(f'  This wizard will save the configuration for this section to the following file:')
            if opSystem == 'Windows':
                print(f'  - {tfDir}\\{org}\\{self.type}\\{polVars["template_type"]}.auto.tfvars')
            else:
                print(f'  - {tfDir}/{org}/{self.type}/{polVars["template_type"]}.auto.tfvars')
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

                    polVars["name"] = ezfunctions.policy_name(name, policy_type)
                    polVars["descr"] = ezfunctions.policy_descr(polVars["name"], policy_type)
                    polVars["enabled"] = True

                    valid = False
                    while valid == False:
                        polVars["port"] = input(f'Note: The following Ports cannot be chosen: [22, 23, 80, 123, 389, 443, 623, 636, 2068, 3268, 3269]\n'\
                            'Enter the Port to Assign to this SNMP Policy.  Valid Range is 1-65535.  [161]: ')
                        if polVars["port"] == '':
                            polVars["port"] = 161
                        if re.search(r'[0-9]{1,4}', str(polVars["port"])):
                            valid = validating.snmp_port('SNMP Port', polVars["port"], 1, 65535)
                        else:
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            print(f'  Invalid Entry!  Please Enter a valid Port in the range of 1-65535.')
                            print(f'  Excluding [22, 23, 80, 123, 389, 443, 623, 636, 2068, 3268, 3269].')
                            print(f'\n-------------------------------------------------------------------------------------------\n')

                    polVars["multi_select"] = False
                    jsonVars = jsonData['snmp.Policy']['allOf'][1]['properties']

                    # SNMP Contact
                    polVars["Description"] = jsonVars['SysContact']['description']
                    polVars["varDefault"] = 'UCS Admins'
                    polVars["varInput"] = 'SNMP System Contact:'
                    polVars["varName"] = 'SNMP System Contact'
                    polVars["varRegex"] = '.*'
                    polVars["minLength"] = 1
                    polVars["maxLength"] = jsonVars['SysContact']['maxLength']
                    polVars["system_contact"] = ezfunctions.varStringLoop(**polVars)

                    # SNMP Location
                    polVars["Description"] = jsonVars['SysLocation']['description']
                    polVars["varDefault"] = 'Data Center'
                    polVars["varInput"] = 'What is the Location of the host on which the SNMP agent (server) runs?'
                    polVars["varName"] = 'System Location'
                    polVars["varRegex"] = '.*'
                    polVars["minLength"] = 1
                    polVars["maxLength"] = jsonVars['SysLocation']['maxLength']
                    polVars["system_location"] = ezfunctions.varStringLoop(**polVars)

                    polVars["access_community_string"] = ''
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
                            polVars["access_community_string"] = loop_count
                            TF_VAR = 'TF_VAR_access_community_string_%s' % (loop_count)
                            os.environ[TF_VAR] = '%s' % (input_string)
                            valid = True
                        elif question == '' or question == 'N':
                            valid = True
                        else:
                            print(f'\n------------------------------------------------------\n')
                            print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                            print(f'\n------------------------------------------------------\n')

                    if not polVars["access_community_string"] == '':
                        polVars["var_description"] = jsonVars['CommunityAccess']['description']
                        polVars["jsonVars"] = sorted(jsonVars['CommunityAccess']['enum'])
                        polVars["defaultVar"] = jsonVars['CommunityAccess']['default']
                        polVars["varType"] = 'Community Access'
                        polVars["community_access"] = ezfunctions.variablesFromAPI(**polVars)
                    else:
                        polVars["community_access"] = 'Disabled'

                    polVars["trap_community_string"] = ''
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
                            polVars["trap_community_string"] = loop_count
                            TF_VAR = 'TF_VAR_snmp_trap_community_%s' % (loop_count)
                            os.environ[TF_VAR] = '%s' % (input_string)
                            valid = True
                        elif question == '' or question == 'N':
                            valid = True
                        else:
                            print(f'\n------------------------------------------------------\n')
                            print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                            print(f'\n------------------------------------------------------\n')

                    polVars["engine_input_id"] = ''
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
                            polVars["snmp_engine_input_id"] = input_string
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
                    polVars["Description"] = 'Configure SNMP Users'
                    polVars["varInput"] = f'Would you like to configure an SNMPv3 User?'
                    polVars["varDefault"] = 'Y'
                    polVars["varName"] = 'Enable Trunking'
                    configure_snmp_users = ezfunctions.varBoolLoop(**polVars)
                    if configure_snmp_users == True:
                        snmp_loop = False
                        while snmp_loop == False:
                            snmp_user_list,snmp_loop = ezfunctions.snmp_users(jsonData, ilCount, **polVars)

                    # SNMP Trap Destinations
                    ilCount = 1
                    snmp_dests = []
                    snmp_loop = False
                    while snmp_loop == False:
                        question = input(f'Would you like to configure SNMP Trap Destionations?  Enter "Y" or "N" [Y]: ')
                        if question == '' or question == 'Y':
                            snmp_dests,snmp_loop = ezfunctions.snmp_trap_servers(jsonData, ilCount, snmp_user_list, **polVars)
                        elif question == 'N':
                            snmp_loop = True
                        else:
                            print(f'\n------------------------------------------------------\n')
                            print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                            print(f'\n------------------------------------------------------\n')
                    polVars["trap_destinations"] = snmp_dests

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    if not polVars["access_community_string"] == '':
                        print(f'    access_community_string = "Sensitive"')
                    print(f'    description             = "{polVars["descr"]}"')
                    print(f'    enable_snmp             = {polVars["enabled"]}')
                    print(f'    name                    = "{polVars["name"]}"')
                    print(f'    snmp_community_access   = "{polVars["community_access"]}"')
                    print(f'    snmp_engine_input_id    = "{polVars["engine_input_id"]}"')
                    print(f'    snmp_port               = {polVars["port"]}')
                    if len(polVars["trap_destinations"]) > 0:
                        print(f'    snmp_trap_destinations = ''{')
                        for item in polVars["trap_destinations"]:
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
                    if len(polVars["users"]) > 0:
                        print(f'    snmp_users = ''{')
                        for item in polVars["users"]:
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
                    if not polVars["trap_community_string"] == '':
                        print(f'    trap_community_string   = "Sensitive"')
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
    # SSH Policy Module
    #==============================================
    def ssh_policies(self, jsonData, ezData, **kwargs):
        name_prefix = self.name_prefix
        name_suffix = 'ssh'
        opSystem = kwargs['opSystem']
        org = self.org
        policy_type = 'SSH Policy'
        polVars = {}
        polVars["header"] = '%s Variables' % (policy_type)
        polVars["initial_write"] = True
        polVars["org"] = org
        polVars["policy_type"] = policy_type
        polVars["template_file"] = 'template_open.jinja2'
        polVars["template_type"] = 'ssh_policies'
        tfDir = kwargs['tfDir']

        # Open the Template file
        ezfunctions.write_to_template(self, **polVars)
        polVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  An {policy_type} enables an SSH client to make a secure, encrypted connection. You can ')
            print(f'  create one or more SSH policies that contain a specific grouping of SSH properties for a ')
            print(f'  server or a set of servers.\n\n')
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
                    polVars["enable_ssh"] = True

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  Port used for secure shell access.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid = False
                    while valid == False:
                        polVars["ssh_port"] = input('What is the SSH Port?  [22]: ')
                        if polVars["ssh_port"] == '':
                            polVars["ssh_port"] = 22
                        if re.search(r'[\d]+', str(polVars["ssh_port"])):
                            valid = validating.number_in_range('SSH Port', polVars["ssh_port"], 1, 65535)
                        else:
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            print(f'  "{polVars["ssh_port"]}" is not a valid port.')
                            print(f'\n-------------------------------------------------------------------------------------------\n')

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  Number of seconds to wait before the system considers an SSH request to have timed out.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid = False
                    while valid == False:
                        polVars["ssh_timeout"] = input('What value do you want to set for the SSH Timeout?  [1800]: ')
                        if polVars["ssh_timeout"] == '':
                            polVars["ssh_timeout"] = 1800
                        if re.search(r'[\d]+', str(polVars["ssh_timeout"])):
                            valid = validating.number_in_range('SSH Timeout', polVars["ssh_timeout"], 60, 10800)
                        else:
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            print(f'  "{polVars["ssh_timeout"]}" is not a valid value.  Must be between 60 and 10800')
                            print(f'\n-------------------------------------------------------------------------------------------\n')


                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'    description = "{polVars["descr"]}"')
                    print(f'    enable_ssh  = {polVars["enable_ssh"]}')
                    print(f'    name        = "{polVars["name"]}"')
                    print(f'    ssh_port    = {polVars["ssh_port"]}')
                    print(f'    ssh_timeout = "{polVars["ssh_timeout"]}"')
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

    #========================================
    # Storage Policy Module
    #========================================
    def storage_policies(self, jsonData, ezData, **kwargs):
        name_prefix = self.name_prefix
        name_suffix = 'storage'
        opSystem = kwargs['opSystem']
        org = self.org
        ezfunctions.policy_names = []
        policy_type = 'Storage Policy'
        polVars = {}
        polVars["header"] = '%s Variables' % (policy_type)
        polVars["initial_write"] = True
        polVars["org"] = org
        polVars["policy_type"] = policy_type
        polVars["template_file"] = 'template_open.jinja2'
        polVars["template_type"] = 'storage_policies'
        tfDir = kwargs['tfDir']

        # Open the Template file
        ezfunctions.write_to_template(self, **polVars)
        polVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  A {policy_type} allows you to create drive groups, virtual drives, configure the ')
            print(f'  storage capacity of a virtual drive, and configure the M.2 RAID controllers.\n')
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

                    # Obtain Policy Name
                    polVars["name"] = ezfunctions.policy_name(name, policy_type)
                    # Obtain Policy Description
                    polVars["descr"] = ezfunctions.policy_descr(polVars["name"], policy_type)

                    # Configure the Global Host Spares Setting
                    polVars["multi_select"] = False
                    jsonVars = jsonData['storage.StoragePolicy']['allOf'][1]['properties']

                    # Configure the Global Host Spares Setting
                    polVars["Description"] = jsonVars['GlobalHotSpares']['description']
                    polVars["varDefault"] = ''
                    polVars["varInput"] = 'Specify the disks that are to be used as hot spares,\n globally,'\
                        ' for all the Drive Groups. [press enter to skip]:'
                    polVars["varName"] = 'Global Hot Spares'
                    polVars["varRegex"] = jsonVars['GlobalHotSpares']['pattern']
                    polVars["minLength"] = 0
                    polVars["maxLength"] = 128
                    polVars["global_hot_spares"] = ezfunctions.varStringLoop(**polVars)

                    # Obtain Unused Disks State
                    polVars["var_description"] = jsonVars['UnusedDisksState']['description']
                    polVars["jsonVars"] = sorted(jsonVars['UnusedDisksState']['enum'])
                    polVars["defaultVar"] = jsonVars['UnusedDisksState']['default']
                    polVars["varType"] = 'Unused Disks State'
                    polVars["unused_disks_state"] = ezfunctions.variablesFromAPI(**polVars)

                    # Configure the Global Host Spares Setting
                    polVars["Description"] = jsonVars['UseJbodForVdCreation']['description']
                    polVars["varInput"] = f'Do you want to Use JBOD drives for Virtual Drive creation?'
                    polVars["varDefault"] = 'N'
                    polVars["varName"] = 'Use Jbod For Vd Creation'
                    polVars["use_jbod_for_vd_creation"] = ezfunctions.varBoolLoop(**polVars)

                    # Ask if Drive Groups should be configured
                    polVars["Description"] = 'Drive Group Configuration - Enable to add RAID drive groups that can be used to create'\
                        ' virtual drives.  You can also specify the Global Hot Spares information.'
                    polVars["varInput"] = f'Do you want to Configure Drive Groups?'
                    polVars["varDefault"] = 'N'
                    polVars["varName"] = 'Drive Groups'
                    driveGroups = ezfunctions.varBoolLoop(**polVars)

                    # If True configure Drive Groups
                    if driveGroups == True:
                        polVars["drive_groups"] = []
                        inner_loop_count = 1
                        drive_group = []
                        drive_group_loop = False
                        while drive_group_loop == False:
                            jsonVars = jsonData['storage.DriveGroup']['allOf'][1]['properties']

                            # Request Drive Group Name
                            polVars["Description"] = jsonVars['Name']['description']
                            polVars["varDefault"] = f'dg{inner_loop_count - 1}'
                            polVars["varInput"] = f'Enter the Drive Group Name.  [{polVars["varDefault"]}]:'
                            polVars["varName"] = 'Drive Group Name'
                            polVars["varRegex"] = jsonVars['Name']['pattern']
                            polVars["minLength"] = 1
                            polVars["maxLength"] = 60
                            dgName = ezfunctions.varStringLoop(**polVars)

                            # Obtain Raid Level for Drive Group
                            polVars["var_description"] = jsonVars['RaidLevel']['description']
                            polVars["jsonVars"] = sorted(jsonVars['RaidLevel']['enum'])
                            polVars["defaultVar"] = jsonVars['RaidLevel']['default']
                            polVars["varType"] = 'Raid Level'
                            RaidLevel = ezfunctions.variablesFromAPI(**polVars)

                            jsonVars = jsonData['storage.ManualDriveGroup']['allOf'][1]['properties']

                            # If Raid Level is anything other than Raid0 ask for Hot Spares
                            if not RaidLevel == 'Raid0':
                                polVars["Description"] = jsonVars['DedicatedHotSpares']['description']
                                polVars["varInput"] = 'Enter the Drives to add as Dedicated Hot Spares [press enter to skip]:'
                                polVars["varName"] = 'Dedicated Hot Spares'
                                polVars["varRegex"] = jsonVars['DedicatedHotSpares']['pattern']
                                polVars["minLength"] = 1
                                polVars["maxLength"] = 60
                                DedicatedHotSpares = ezfunctions.varStringLoop(**polVars)
                            else:
                                DedicatedHotSpares = ''

                            # Configure Span Slots
                            SpanSlots = []
                            # If Riad is 10, 50 or 60 allow multiple Span Slots
                            if re.fullmatch('^Raid(10|50|60)$', RaidLevel):
                                polVars["var_description"] = jsonVars['SpanGroups']['items']['description']
                                polVars["jsonVars"] = [2, 4, 6, 8]
                                polVars["defaultVar"] = 2
                                polVars["varType"] = 'Span Groups'
                                SpanGroups = ezfunctions.variablesFromAPI(**polVars)
                                if SpanGroups == 2:
                                    SpanGroups = [0, 1]
                                elif SpanGroups == 4:
                                    SpanGroups = [0, 1, 2, 3]
                                elif SpanGroups == 6:
                                    SpanGroups = [0, 1, 2, 3, 4, 5]
                                elif SpanGroups == 8:
                                    SpanGroups = [0, 1, 2, 3, 4, 5, 6, 7]


                                for span in SpanGroups:
                                    jsonVars = jsonData['storage.SpanDrives']['allOf'][1]['properties']
                                    polVars["Description"] = jsonVars['Slots']['description']
                                    if re.fullmatch('^Raid10$', RaidLevel):
                                        Drive1 = (inner_loop_count * 2) - 1
                                        Drive2 = (inner_loop_count * 2)
                                        polVars["varDefault"] = f'{Drive1}-{Drive2}'
                                    elif re.fullmatch('^Raid50$', RaidLevel):
                                        Drive1 = (inner_loop_count * 3) - 2
                                        Drive2 = (inner_loop_count * 3)
                                        polVars["varDefault"] = f'{Drive1}-{Drive2}'
                                    elif re.fullmatch('^Raid60$', RaidLevel):
                                        Drive1 = (inner_loop_count * 4) - 3
                                        Drive2 = (inner_loop_count * 4)
                                        polVars["varDefault"] = f'{Drive1}-{Drive2}'
                                    polVars["varInput"] = f'Enter the Drive Slots for Drive Array Span {span}. [{polVars["varDefault"]}]:'
                                    polVars["varName"] = 'Drive Slots'
                                    polVars["varRegex"] = jsonVars['Slots']['pattern']
                                    polVars["minLength"] = 1
                                    polVars["maxLength"] = 10
                                    SpanSlots.append({'slots':ezfunctions.varStringLoop(**polVars)})
                            elif re.fullmatch('^Raid(0|1|5|6)$', RaidLevel):
                                jsonVars = jsonData['storage.SpanDrives']['allOf'][1]['properties']
                                polVars["Description"] = jsonVars['Slots']['description']
                                if re.fullmatch('^Raid(0|1)$', RaidLevel):
                                    Drive1 = (inner_loop_count * 2) - 1
                                    Drive2 = (inner_loop_count * 2)
                                    polVars["varDefault"] = f'{Drive1}-{Drive2}'
                                elif re.fullmatch('^Raid5$', RaidLevel):
                                    Drive1 = (inner_loop_count * 3) - 2
                                    Drive2 = (inner_loop_count * 3)
                                    polVars["varDefault"] = f'{Drive1}-{Drive2}'
                                elif re.fullmatch('^Raid6$', RaidLevel):
                                    Drive1 = (inner_loop_count * 4) - 3
                                    Drive2 = (inner_loop_count * 4)
                                    polVars["varDefault"] = f'{Drive1}-{Drive2}'
                                polVars["varInput"] = f'Enter the Drive Slots for Drive Array Span 0. [{polVars["varDefault"]}]:'
                                polVars["varName"] = 'Drive Slots'
                                polVars["varRegex"] = jsonVars['Slots']['pattern']
                                polVars["minLength"] = 1
                                polVars["maxLength"] = 10
                                SpanSlots.append({'slots':ezfunctions.varStringLoop(**polVars)})
                                
                            virtualDrives = []
                            sub_loop_count = 0
                            sub_loop = False
                            while sub_loop == False:
                                jsonVars = jsonData['storage.VirtualDriveConfiguration']['allOf'][1]['properties']

                                polVars["Description"] = jsonVars['Name']['description']
                                polVars["varDefault"] = f'vd{sub_loop_count}'
                                polVars["varInput"] = f'Enter the name of the Virtual Drive.  [vd{sub_loop_count}]'
                                polVars["varName"] = 'Drive Group Name'
                                polVars["varRegex"] = jsonVars['Name']['pattern']
                                polVars["minLength"] = 1
                                polVars["maxLength"] = 60
                                vd_name = ezfunctions.varStringLoop(**polVars)

                                polVars["Description"] = jsonVars['ExpandToAvailable']['description']
                                polVars["varInput"] = f'Do you want to expand to all the space in the drive group?'
                                polVars["varDefault"] = 'Y'
                                polVars["varName"] = 'Expand To Available'
                                ExpandToAvailable = ezfunctions.varBoolLoop(**polVars)

                                # If Expand to Available is Disabled obtain Virtual Drive disk size
                                if ExpandToAvailable == False:
                                    polVars["Description"] = jsonVars['Size']['description']
                                    polVars["varDefault"] =  '1'
                                    polVars["varInput"] = 'What is the Size for this Virtual Drive?'
                                    polVars["varName"] = 'Size'
                                    polVars["varRegex"] = '[0-9]+'
                                    polVars["minNum"] = jsonVars['Size']['minimum']
                                    polVars["maxNum"] = 9999999999
                                    vdSize = ezfunctions.varNumberLoop(**polVars)
                                else:
                                    vdSize = 1
                                
                                polVars["Description"] = jsonVars['BootDrive']['description']
                                polVars["varInput"] = f'Do you want to configure {vd_name} as a boot drive?'
                                polVars["varDefault"] = 'Y'
                                polVars["varName"] = 'Boot Drive'
                                BootDrive = ezfunctions.varBoolLoop(**polVars)

                                jsonVars = jsonData['storage.VirtualDrivePolicy']['allOf'][1]['properties']

                                polVars["var_description"] = jsonVars['AccessPolicy']['description']
                                polVars["jsonVars"] = sorted(jsonVars['AccessPolicy']['enum'])
                                polVars["defaultVar"] = jsonVars['AccessPolicy']['default']
                                polVars["varType"] = 'Access Policy'
                                AccessPolicy = ezfunctions.variablesFromAPI(**polVars)

                                polVars["var_description"] = jsonVars['DriveCache']['description']
                                polVars["jsonVars"] = sorted(jsonVars['DriveCache']['enum'])
                                polVars["defaultVar"] = jsonVars['DriveCache']['default']
                                polVars["varType"] = 'Drive Cache'
                                DriveCache = ezfunctions.variablesFromAPI(**polVars)

                                polVars["var_description"] = jsonVars['ReadPolicy']['description']
                                polVars["jsonVars"] = sorted(jsonVars['ReadPolicy']['enum'])
                                polVars["defaultVar"] = jsonVars['ReadPolicy']['default']
                                polVars["varType"] = 'Read Policy'
                                ReadPolicy = ezfunctions.variablesFromAPI(**polVars)

                                polVars["var_description"] = jsonVars['StripSize']['description']
                                polVars["jsonVars"] = sorted(jsonVars['StripSize']['enum'])
                                polVars["defaultVar"] = jsonVars['StripSize']['default']
                                polVars["varType"] = 'Strip Size'
                                StripSize = ezfunctions.variablesFromAPI(**polVars)

                                polVars["var_description"] = jsonVars['WritePolicy']['description']
                                polVars["jsonVars"] = sorted(jsonVars['WritePolicy']['enum'])
                                polVars["defaultVar"] = jsonVars['WritePolicy']['default']
                                polVars["varType"] = 'Write Policy'
                                WritePolicy = ezfunctions.variablesFromAPI(**polVars)

                                virtual_drive = {
                                    'access_policy':AccessPolicy,
                                    'boot_drive':BootDrive,
                                    'disk_cache':DriveCache,
                                    'expand_to_available':ExpandToAvailable,
                                    'name':vd_name,
                                    'read_policy':ReadPolicy,
                                    'size':vdSize,
                                    'strip_size':StripSize,
                                    'write_policy':WritePolicy,
                                }
                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                print(f'    "{virtual_drive["name"]}" = ''{')
                                print(f'      access_policy       = "{virtual_drive["access_policy"]}"')
                                print(f'      boot_drive          = {virtual_drive["boot_drive"]}')
                                print(f'      disk_cache          = "{virtual_drive["disk_cache"]}"')
                                print(f'      expand_to_available = {virtual_drive["expand_to_available"]}')
                                print(f'      read_policy         = "{virtual_drive["read_policy"]}"')
                                print(f'      size                = {virtual_drive["size"]}')
                                print(f'      strip_size          = "{virtual_drive["strip_size"]}"')
                                print(f'      write_policy        = "{virtual_drive["write_policy"]}"')
                                print(f'    ''}')
                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                valid_confirm = False
                                while valid_confirm == False:
                                    confirm_v = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
                                    if confirm_v == 'Y' or confirm_v == '':
                                        virtualDrives.append(virtual_drive)
                                        valid_exit = False
                                        while valid_exit == False:
                                            loop_exit = input(f'Would You like to Configure another Virtual Drive for {dgName}?  Enter "Y" or "N" [N]: ')
                                            if loop_exit == 'Y':
                                                inner_loop_count += 1
                                                valid_confirm = True
                                                valid_exit = True
                                            elif loop_exit == 'N' or loop_exit == '':
                                                drive_group_loop = True
                                                valid_confirm = True
                                                valid_exit = True
                                            else:
                                                print(f'\n------------------------------------------------------\n')
                                                print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                                                print(f'\n------------------------------------------------------\n')

                                    elif confirm_v == 'N':
                                        print(f'\n-------------------------------------------------------------------------------------------\n')
                                        print(f'  Starting Virtual Drive Configuration Over.')
                                        print(f'\n-------------------------------------------------------------------------------------------\n')
                                        valid_confirm = True
                                    else:
                                        print(f'\n------------------------------------------------------\n')
                                        print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                                        print(f'\n------------------------------------------------------\n')


                            drive_group = {
                                'drive_group_name':dgName,
                                'manual_drive_selection':{
                                    'dedicated_hot_spares':DedicatedHotSpares,
                                    'drive_array_spans':[
                                        SpanSlots
                                    ]
                                },
                                'raid_level':RaidLevel,
                                'virtual_drives':virtualDrives
                            }
                            dg_count = 0
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            print(f'      "{drive_group["drive_group_name"]}" = ''{')
                            print(f'        manual_drive_group = ''{')
                            print(f'          "{dg_count}" = ''{')
                            print(f'            dedicated_hot_spares = "{drive_group["manual_drive_group"]["dedicated_hot_spares"]}"')
                            print(f'            drive_array_spans = ''{')
                            span_count = 0
                            for i in drive_group["manual_drive_group"]["drive_array_spans"]:
                                print(f'              "span_{span_count}" = ''{slots = "'f'{i["slots"]}"''}')
                                span_count += 1
                                print(f'              ''}')
                            print(f'              ''}')
                            print(f'            ''}')
                            print(f'          ''}')
                            print(f'          ''}')
                            print(f'        ''}')
                            print(f'        raid_level = "{RaidLevel}"')
                            print(f'        virtual_drives = ''{')
                            for virtual_drive in virtualDrives:
                                print(f'          "{virtual_drive["name"]}" = ''{')
                                print(f'            access_policy       = "{virtual_drive["access_policy"]}"')
                                print(f'            boot_drive          = "{virtual_drive["boot_drive"]}"')
                                print(f'            disk_cache          = "{virtual_drive["disk_cache"]}"')
                                print(f'            expand_to_available = {virtual_drive["expand_to_available"]}')
                                print(f'            read_policy         = "{virtual_drive["read_policy"]}"')
                                print(f'            size                = {virtual_drive["size"]}')
                                print(f'            strip_size          = "{virtual_drive["strip_size"]}"')
                                print(f'            write_policy        = "{virtual_drive["write_policy"]}"')
                                print(f'          ''}')
                            print(f'        ''}')
                            print(f'      ''}')
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            valid_confirm = False
                            while valid_confirm == False:
                                confirm_v = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
                                if confirm_v == 'Y' or confirm_v == '':
                                    polVars["drive_groups"].append(drive_group)
                                    valid_exit = False
                                    while valid_exit == False:
                                        loop_exit = input(f'Would You like to Configure another Drive Group?  Enter "Y" or "N" [N]: ')
                                        if loop_exit == 'Y':
                                            inner_loop_count += 1
                                            valid_confirm = True
                                            valid_exit = True
                                        elif loop_exit == 'N' or loop_exit == '':
                                            drive_group_loop = True
                                            valid_confirm = True
                                            valid_exit = True
                                        else:
                                            print(f'\n------------------------------------------------------\n')
                                            print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                                            print(f'\n------------------------------------------------------\n')

                                elif confirm_v == 'N':
                                    print(f'\n-------------------------------------------------------------------------------------------\n')
                                    print(f'  Starting Drive Group Configuration Over.')
                                    print(f'\n-------------------------------------------------------------------------------------------\n')
                                    valid_confirm = True
                                else:
                                    print(f'\n------------------------------------------------------\n')
                                    print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                                    print(f'\n------------------------------------------------------\n')
                    else:
                        polVars["drive_groups"] = []

                    # Ask if M2 should be configured
                    polVars["Description"] = jsonVars['M2VirtualDrive']['description']
                    polVars["varInput"] = f'Do you want to Enable the M.2 Virtual Drive Configuration?'
                    polVars["varDefault"] = 'Y'
                    polVars["varName"] = 'M.2 Virtual Drive'
                    M2VirtualDrive = ezfunctions.varBoolLoop(**polVars)

                    # Configure M2 if it is True if not Pop it from the list
                    if M2VirtualDrive == True:
                        jsonVars = jsonData['storage.M2VirtualDriveConfig']['allOf'][1]['properties']

                        polVars["var_description"] = jsonVars['ControllerSlot']['description']
                        polVars["jsonVars"] = sorted(jsonVars['ControllerSlot']['enum'])
                        polVars["defaultVar"] = 'MSTOR-RAID-1'
                        polVars["varType"] = 'Controller Slot'
                        ControllerSlot = ezfunctions.variablesFromAPI(**polVars)

                        polVars["m2_configuration"] = {
                            'controller_slot':ControllerSlot,
                            'enable':True
                        }
                    else:
                        polVars.pop('m2_configuration')

                    # Ask if Drive Groups should be configured
                    polVars["Description"] = 'Enable to create RAID0 virtual drives on each physical drive..'
                    polVars["varInput"] = f"Do you want to Configure Single Drive RAID's?"
                    polVars["varDefault"] = 'N'
                    polVars["varName"] = 'Single Drive RAID'
                    singledriveRaid = ezfunctions.varBoolLoop(**polVars)

                    # If True configure Drive Groups
                    if singledriveRaid == True:
                        single_drive_loop = False
                        while single_drive_loop == False:
                            # Obtain the Single Drive Raid Slots
                            jsonVars = jsonData['storage.R0Drive']['allOf'][1]['properties']
                            polVars["Description"] = jsonVars['DriveSlots']['description']
                            polVars["varDefault"] = f'1-2'
                            polVars["varInput"] = f'Enter the Drive Slots for Drive Array Span 0. [{polVars["varDefault"]}]:'
                            polVars["varName"] = 'Drive Slots'
                            polVars["varRegex"] = jsonVars['DriveSlots']['pattern']
                            polVars["minLength"] = 1
                            polVars["maxLength"] = 64
                            DriveSlots = ezfunctions.varStringLoop(**polVars)
                                
                            # Obtain the Virtual Drive Policies
                            jsonVars = jsonData['storage.VirtualDrivePolicy']['allOf'][1]['properties']

                            # Access Policy
                            polVars["var_description"] = jsonVars['AccessPolicy']['description']
                            polVars["jsonVars"] = sorted(jsonVars['AccessPolicy']['enum'])
                            polVars["defaultVar"] = jsonVars['AccessPolicy']['default']
                            polVars["varType"] = 'Access Policy'
                            AccessPolicy = ezfunctions.variablesFromAPI(**polVars)

                            # Drive Cache
                            polVars["var_description"] = jsonVars['DriveCache']['description']
                            polVars["jsonVars"] = sorted(jsonVars['DriveCache']['enum'])
                            polVars["defaultVar"] = jsonVars['DriveCache']['default']
                            polVars["varType"] = 'Drive Cache'
                            DriveCache = ezfunctions.variablesFromAPI(**polVars)

                            # Read Policy
                            polVars["var_description"] = jsonVars['ReadPolicy']['description']
                            polVars["jsonVars"] = sorted(jsonVars['ReadPolicy']['enum'])
                            polVars["defaultVar"] = jsonVars['ReadPolicy']['default']
                            polVars["varType"] = 'Read Policy'
                            ReadPolicy = ezfunctions.variablesFromAPI(**polVars)

                            # Strip Size
                            polVars["var_description"] = jsonVars['StripSize']['description']
                            polVars["jsonVars"] = sorted(jsonVars['StripSize']['enum'])
                            polVars["defaultVar"] = jsonVars['StripSize']['default']
                            polVars["varType"] = 'Strip Size'
                            StripSize = ezfunctions.variablesFromAPI(**polVars)

                            # Write Policy
                            polVars["var_description"] = jsonVars['WritePolicy']['description']
                            polVars["jsonVars"] = sorted(jsonVars['WritePolicy']['enum'])
                            polVars["defaultVar"] = jsonVars['WritePolicy']['default']
                            polVars["varType"] = 'Write Policy'
                            WritePolicy = ezfunctions.variablesFromAPI(**polVars)

                            polVars["single_drive_raid_configuration"] = {
                                'access_policy':AccessPolicy,
                                'disk_cache':DriveCache,
                                'drive_slots':DriveSlots,
                                'enable':True,
                                'read_policy':ReadPolicy,
                                'strip_size':StripSize,
                                'write_policy':WritePolicy,
                            }
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            print(f'    "0" = ''{')
                            print(f'      access_policy = "{polVars["single_drive_raid_configuration"]["access_policy"]}"')
                            print(f'      disk_cache    = "{polVars["single_drive_raid_configuration"]["disk_cache"]}"')
                            print(f'      drive_slots   = "{polVars["single_drive_raid_configuration"]["drive_slots"]}"')
                            print(f'      enable        = {polVars["single_drive_raid_configuration"]["enable"]}')
                            print(f'      read_policy   = "{polVars["single_drive_raid_configuration"]["read_policy"]}"')
                            print(f'      strip_size    = "{polVars["single_drive_raid_configuration"]["strip_size"]}"')
                            print(f'      write_policy  = "{polVars["single_drive_raid_configuration"]["write_policy"]}"')
                            print(f'    ''}')
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            valid_confirm = False
                            while valid_confirm == False:
                                confirm_v = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
                                if confirm_v == 'Y' or confirm_v == '':
                                    single_drive_loop = True
                                    valid_confirm = True
                                    valid_exit = True
                                elif confirm_v == 'N':
                                    print(f'\n-------------------------------------------------------------------------------------------\n')
                                    print(f'  Starting Single Drive RAID Configuration Over.')
                                    print(f'\n-------------------------------------------------------------------------------------------\n')
                                    valid_confirm = True
                                else:
                                    print(f'\n------------------------------------------------------\n')
                                    print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                                    print(f'\n------------------------------------------------------\n')

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'    description              = "{polVars["descr"]}"')
                    print(f'    global_hot_spares        = "{polVars["global_hot_spares"]}"')
                    print(f'    unused_disks_state       = "{polVars["unused_disks_state"]}"')
                    print(f'    use_jbod_for_vd_creation = "{polVars["use_jbod_for_vd_creation"]}"')
                    dg_count = 0
                    if len(polVars["drive_groups"]) > 0:
                        print(f'    drive_groups = ''{')
                        for drive_group in polVars["drive_groups"]:
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            print(f'      "{drive_group["drive_group_name"]}" = ''{')
                            print(f'        manual_drive_group = ''{')
                            print(f'          "{dg_count}" = ''{')
                            print(f'            dedicated_hot_spares = "{drive_group["manual_drive_group"]["dedicated_hot_spares"]}"')
                            print(f'            drive_array_spans = ''{')
                            span_count = 0
                            for i in drive_group["manual_drive_group"]["drive_array_spans"]:
                                print(f'              "span_{span_count}" = ''{slots = "'f'{i["slots"]}"''}')
                                span_count += 1
                                print(f'              ''}')
                            print(f'              ''}')
                            print(f'            ''}')
                            print(f'          ''}')
                            print(f'          ''}')
                            print(f'        ''}')
                            print(f'        raid_level = "{RaidLevel}"')
                            print(f'        virtual_drives = ''{')
                            for virtual_drive in virtualDrives:
                                print(f'          "{virtual_drive["name"]}" = ''{')
                                print(f'            access_policy       = "{virtual_drive["access_policy"]}"')
                                print(f'            boot_drive          = "{virtual_drive["boot_drive"]}"')
                                print(f'            disk_cache          = "{virtual_drive["disk_cache"]}"')
                                print(f'            expand_to_available = {virtual_drive["expand_to_available"]}')
                                print(f'            read_policy         = "{virtual_drive["read_policy"]}"')
                                print(f'            size                = {virtual_drive["size"]}')
                                print(f'            strip_size          = "{virtual_drive["strip_size"]}"')
                                print(f'            write_policy        = "{virtual_drive["write_policy"]}"')
                                print(f'          ''}')
                            print(f'        ''}')
                            print(f'      ''}')
                            dg_count += 1
                        print(f'    ''}')
                    else:
                        print(f'    drive_groups = ''{}')
                    if polVars.get("m2_configuration"):
                        print(f'    m2_configuration = ''{')
                        print(f'      "0" = ''{')
                        print(f'        controller_slot = "{polVars["m2_configuration"]["controller_slot"]}"')
                        print(f'      ''}')
                        print(f'    ''}')
                    else:
                        print(f'    m2_configuration = ''{}')
                    if polVars.get("single_drive_raid_configuration"):
                        print(f'    single_drive_raid_configuration = ''{')
                        print(f'    "0" = ''{')
                        print(f'      access_policy = "{polVars["single_drive_raid_configuration"]["access_policy"]}"')
                        print(f'      disk_cache    = "{polVars["single_drive_raid_configuration"]["disk_cache"]}"')
                        print(f'      drive_slots   = "{polVars["single_drive_raid_configuration"]["drive_slots"]}"')
                        print(f'      enable        = {polVars["single_drive_raid_configuration"]["enable"]}')
                        print(f'      read_policy   = "{polVars["single_drive_raid_configuration"]["read_policy"]}"')
                        print(f'      strip_size    = "{polVars["single_drive_raid_configuration"]["strip_size"]}"')
                        print(f'      write_policy  = "{polVars["single_drive_raid_configuration"]["write_policy"]}"')
                        print(f'    ''}')
                    else:
                        print(f'    single_drive_raid_configuration = ''{}')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
                        if confirm_policy == 'Y' or confirm_policy == '':
                            confirm_policy = 'Y'

                            # Write Policies to Template File
                            polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                            ezfunctions.write_to_template(self, **polVars)

                            # Add Template Name to Policies Output
                            ezfunctions.policy_names.append(polVars["name"])

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
    # Switch Control Policy Module
    #==============================================
    def switch_control_policies(self, jsonData, ezData, **kwargs):
        name_prefix = self.name_prefix
        name_suffix = 'sw_ctrl'
        opSystem = kwargs['opSystem']
        org = self.org
        policy_type = 'Switch Control Policy'
        polVars = {}
        polVars["header"] = '%s Variables' % (policy_type)
        polVars["initial_write"] = True
        polVars["org"] = org
        polVars["policy_type"] = policy_type
        polVars["template_file"] = 'template_open.jinja2'
        polVars["template_type"] = 'switch_control_policies'
        tfDir = kwargs['tfDir']

        # Open the Template file
        ezfunctions.write_to_template(self, **polVars)
        polVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  A Switch Control Policy will configure Unidirectional Link Detection Protocol and')
            print(f'  MAC Address Learning Settings for the UCS Domain Profile.')
            print(f'  We recommend the settings the wizard is setup to push.  So you will only be asked for')
            print(f'  the name and description for the Policy.  You only need one of these policies for')
            print(f'  Organization {org}.\n')
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

                polVars["mac_address_table_aging"] = 'Default'
                polVars["mac_aging_time"] = 14500
                polVars["udld_message_interval"] = 15
                polVars["udld_recovery_action"] = "reset"
                polVars["vlan_port_count_optimization"] = False

                # Pull Information from the API
                polVars["multi_select"] = False
                jsonVars = jsonData['fabric.FcNetworkPolicy']['allOf'][1]['properties']

                # Ethernet Switching Mode
                polVars["var_description"] = jsonVars['EthernetSwitchingMode']['description']
                polVars["jsonVars"] = sorted(jsonVars['EthernetSwitchingMode']['enum'])
                polVars["defaultVar"] = jsonVars['EthernetSwitchingMode']['default']
                polVars["varType"] = 'Ethernet Switching Mode'
                polVars["ethernet_switching_mode"] = ezfunctions.variablesFromAPI(**polVars)

                # Ethernet Switching Mode
                polVars["var_description"] = jsonVars['FcSwitchingMode']['description']
                polVars["jsonVars"] = sorted(jsonVars['FcSwitchingMode']['enum'])
                polVars["defaultVar"] = jsonVars['FcSwitchingMode']['default']
                polVars["varType"] = 'FC Switching Mode'
                polVars["fc_switching_mode"] = ezfunctions.variablesFromAPI(**polVars)

                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'    description                  = "{polVars["descr"]}"')
                print(f'    ethernet_switching_mode      = "{polVars["ethernet_switching_mode"]}"')
                print(f'    fc_switching_mode            = "{polVars["fc_switching_mode"]}"')
                print(f'    mac_address_table_aging      = "{polVars["mac_address_table_aging"]}"')
                print(f'    mac_aging_time               = {polVars["mac_aging_time"]}')
                print(f'    name                         = "{polVars["name"]}"')
                print(f'    udld_message_interval        = {polVars["udld_message_interval"]}')
                print(f'    udld_recovery_action         = "{polVars["udld_recovery_action"]}"')
                print(f'    vlan_port_count_optimization = {polVars["vlan_port_count_optimization"]}')
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
    # Syslog Policy Module
    #==============================================
    def syslog_policies(self, jsonData, ezData, **kwargs):
        name_prefix = self.name_prefix
        name_suffix = 'syslog'
        opSystem = kwargs['opSystem']
        org = self.org
        policy_type = 'Syslog Policy'
        polVars = {}
        polVars["header"] = '%s Variables' % (policy_type)
        polVars["initial_write"] = True
        polVars["org"] = org
        polVars["policy_type"] = policy_type
        polVars["template_file"] = 'template_open.jinja2'
        polVars["template_type"] = 'syslog_policies'
        tfDir = kwargs['tfDir']

        # Open the Template file
        ezfunctions.write_to_template(self, **polVars)
        polVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  A {policy_type} will configure domain and servers with remote syslog servers.')
            print(f'  You can configure up to two Remote Syslog Servers.')
            print(f'  This Policy is not required to standup a server but is a good practice for day 2 support.')
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

                    # Syslog Local Logging
                    polVars["multi_select"] = False
                    jsonVars = jsonData['syslog.LocalClientBase']['allOf'][1]['properties']
                    polVars["var_description"] = jsonVars['MinSeverity']['description']
                    polVars["jsonVars"] = sorted(jsonVars['MinSeverity']['enum'])
                    polVars["defaultVar"] = jsonVars['MinSeverity']['default']
                    polVars["varType"] = 'Syslog Local Minimum Severity'
                    polVars["min_severity"] = ezfunctions.variablesFromAPI(**polVars)

                    polVars["local_logging"] = {'file':{'min_severity':polVars["min_severity"]}}

                    remote_logging = ezfunctions.syslog_servers(jsonData, **polVars)
                    polVars['remote_logging'] = remote_logging

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'    description        = "{polVars["descr"]}"')
                    print(f'    local_min_severity = "{polVars["min_severity"]}"')
                    print(f'    name               = "{polVars["name"]}"')
                    print(f'    remote_clients = [')
                    item_count = 1
                    if polVars["remote_logging"].get("server1"):
                        print(f'      ''{')
                        print(f'        enabled      = {"%s".lower() % (polVars["remote_logging"]["server1"]["enable"])}')
                        print(f'        hostname     = "{polVars["remote_logging"]["server1"]["hostname"]}"')
                        print(f'        min_severity = "{polVars["remote_logging"]["server1"]["min_severity"]}"')
                        print(f'        port         = {polVars["remote_logging"]["server1"]["port"]}')
                        print(f'        protocol     = "{polVars["remote_logging"]["server1"]["protocol"]}"')
                        print(f'      ''}')
                        item_count += 1
                    if polVars["remote_logging"].get("server2"):
                        print(f'      ''{')
                        print(f'        enabled      = {"%s".lower() % (polVars["remote_logging"]["server2"]["enable"])}')
                        print(f'        hostname     = "{polVars["remote_logging"]["server2"]["hostname"]}"')
                        print(f'        min_severity = "{polVars["remote_logging"]["server2"]["min_severity"]}"')
                        print(f'        port         = {polVars["remote_logging"]["server2"]["port"]}')
                        print(f'        protocol     = "{polVars["remote_logging"]["server2"]["protocol"]}"')
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
    # System QoS Policy Module
    #==============================================
    def system_qos_policies(self, jsonData, ezData, **kwargs):
        name_prefix = self.name_prefix
        name_suffix = 'qos'
        opSystem = kwargs['opSystem']
        org = self.org
        policy_type = 'System QoS Policy'
        polVars = {}
        polVars["header"] = '%s Variables' % (policy_type)
        polVars["initial_write"] = True
        polVars["org"] = org
        polVars["policy_type"] = policy_type
        polVars["template_file"] = 'template_open.jinja2'
        polVars["template_type"] = 'system_qos_policies'
        tfDir = kwargs['tfDir']

        # Open the Template file
        ezfunctions.write_to_template(self, **polVars)
        polVars["initial_write"] = False

        configure_loop = False
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
                    mtu = input('Do you want to enable Jumbo MTU?  Enter "Y" or "N" [Y]: ')
                    if mtu == '' or mtu == 'Y':
                        polVars["mtu"] = 9216
                        valid = True
                    elif mtu == 'N':
                        polVars["mtu"] = 1500
                        valid = True
                    else:
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        print(f'  Error!! Invalid Option.  Please enter "Y" or "N".')
                        print(f'\n-------------------------------------------------------------------------------------------\n')

                domain_mtu = polVars["mtu"]

                polVars["Platinum"] = {
                    'bandwidth_percent':20,
                    'cos':5,
                    'mtu':polVars["mtu"],
                    'multicast_optimize':False,
                    'packet_drop':False,
                    'priority':'Platinum',
                    'state':'Enabled',
                    'weight':10,
                }
                polVars["Gold"] = {
                    'bandwidth_percent':18,
                    'cos':4,
                    'mtu':polVars["mtu"],
                    'multicast_optimize':False,
                    'packet_drop':True,
                    'priority':'Gold',
                    'state':'Enabled',
                    'weight':9,
                }
                polVars["FC"] = {
                    'bandwidth_percent':20,
                    'cos':3,
                    'mtu':2240,
                    'multicast_optimize':False,
                    'packet_drop':False,
                    'priority':'FC',
                    'state':'Enabled',
                    'weight':10,
                }
                polVars["Silver"] = {
                    'bandwidth_percent':18,
                    'cos':2,
                    'mtu':polVars["mtu"],
                    'multicast_optimize':False,
                    'packet_drop':True,
                    'priority':'Silver',
                    'state':'Enabled',
                    'weight':8,
                }
                polVars["Bronze"] = {
                    'bandwidth_percent':14,
                    'cos':1,
                    'mtu':polVars["mtu"],
                    'multicast_optimize':False,
                    'packet_drop':True,
                    'priority':'Bronze',
                    'state':'Enabled',
                    'weight':7,
                }
                polVars["Best Effort"] = {
                    'bandwidth_percent':10,
                    'cos':255,
                    'mtu':polVars["mtu"],
                    'multicast_optimize':False,
                    'packet_drop':True,
                    'priority':'Best Effort',
                    'state':'Enabled',
                    'weight':5,
                }

                polVars["classes"] = []
                priorities = ['Platinum', 'Gold', 'FC', 'Silver', 'Bronze', 'Best Effort']

                for priority in priorities:
                    polVars["classes"].append(polVars[priority])
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'    description = "{polVars["descr"]}"')
                print(f'    name        = "{polVars["name"]}"')
                print('    classes = {')
                for item in polVars["classes"]:
                    for k, v in item.items():
                        if k == 'priority':
                            print(f'      "{v}" = ''{')
                    for k, v in item.items():
                        if k == 'bandwidth_percent':
                            print(f'        bandwidth_percent  = {v}')
                        elif k == 'cos':
                            print(f'        cos                = {v}')
                        elif k == 'mtu':
                            print(f'        mtu                = {v}')
                        elif k == 'multicast_optimize':
                            print(f'        multicast_optimize = {v}')
                        elif k == 'packet_drop':
                            print(f'        packet_drop        = {v}')
                        elif k == 'state':
                            print(f'        state              = "{v}"')
                        elif k == 'weight':
                            print(f'        weight             = {v}')
                    print('      }')
                print('    }')
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
    # Thermal Policy Module
    #==============================================
    def thermal_policies(self, jsonData, ezData, **kwargs):
        name_prefix = self.name_prefix
        opSystem = kwargs['opSystem']
        org = self.org
        policy_type = 'Thermal Policy'
        polVars = {}
        polVars["header"] = '%s Variables' % (policy_type)
        polVars["initial_write"] = True
        polVars["org"] = org
        polVars["policy_type"] = policy_type
        polVars["template_file"] = 'template_open.jinja2'
        polVars["template_type"] = 'thermal_policies'
        tfDir = kwargs['tfDir']

        # Open the Template file
        ezfunctions.write_to_template(self, **polVars)
        polVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  A {policy_type} will configure the Cooling/FAN Policy for Chassis.  We recommend ')
            print(f'  Balanced for a 5108 and Acoustic for a 9508 Chassis, as of this writing.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            if opSystem == 'Windows':
                print(f'  - {tfDir}\\{org}\\{self.type}\\{polVars["template_type"]}.auto.tfvars')
            else:
                print(f'  - {tfDir}/{org}/{self.type}/{polVars["template_type"]}.auto.tfvars')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            policy_loop = False
            while policy_loop == False:

                polVars["multi_select"] = False
                jsonVars = ezData['policies']['thermal.Policy']
                polVars["var_description"] = jsonVars['chassisType']['description']
                polVars["jsonVars"] = sorted(jsonVars['chassisType']['enum'])
                polVars["defaultVar"] = jsonVars['chassisType']['default']
                polVars["varType"] = 'Chassis Type'
                polVars["chassis_type"] = ezfunctions.variablesFromAPI(**polVars)

                if not name_prefix == '':
                    name = '%s_%s' % (name_prefix, polVars["chassis_type"])
                else:
                    name = '%s_%s' % (org, polVars["chassis_type"])

                polVars["name"] = ezfunctions.policy_name(name, policy_type)
                polVars["descr"] = ezfunctions.policy_descr(polVars["name"], policy_type)

                if polVars["chassis_type"] == '5108':
                    polVars["popList"] = ['Acoustic', 'HighPower', 'MaximumPower']
                if polVars["chassis_type"] == '9508':
                    polVars["popList"] = []
                jsonVars = jsonData['thermal.Policy']['allOf'][1]['properties']
                polVars["var_description"] = jsonVars['FanControlMode']['description']
                polVars["jsonVars"] = sorted(jsonVars['FanControlMode']['enum'])
                polVars["defaultVar"] = jsonVars['FanControlMode']['default']
                polVars["varType"] = 'Fan Control Mode'
                polVars["fan_control_mode"] = ezfunctions.variablesFromAPI(**polVars)

                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'   description      = "{polVars["descr"]}"')
                print(f'   name             = "{polVars["name"]}"')
                print(f'   fan_control_mode = "{polVars["fan_control_mode"]}"')
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
    # Virtual KVM Policy Module
    #==============================================
    def virtual_kvm_policies(self, jsonData, ezData, **kwargs):
        name_prefix = self.name_prefix
        name_suffix = 'vkvm'
        opSystem = kwargs['opSystem']
        org = self.org
        policy_type = 'Virtual KVM Policy'
        polVars = {}
        polVars["header"] = '%s Variables' % (policy_type)
        polVars["initial_write"] = True
        polVars["org"] = org
        polVars["policy_type"] = policy_type
        polVars["template_file"] = 'template_open.jinja2'
        polVars["template_type"] = 'virtual_kvm_policies'
        tfDir = kwargs['tfDir']

        # Open the Template file
        ezfunctions.write_to_template(self, **polVars)
        polVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  A {policy_type} will configure the Server for KVM access.  Settings include:')
            print(f'   - Local Server Video - If enabled, displays KVM on any monitor attached to the server.')
            print(f'   - Video Encryption - encrypts all video information sent through KVM.')
            print(f'   - Remote Port - The port used for KVM communication. Range is 1 to 65535.\n')
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
                polVars["enable_virtual_kvm"] = True
                polVars["maximum_sessions"] = 4

                # Pull in the Policies for Virtual KVM
                jsonVars = jsonData['kvm.Policy']['allOf'][1]['properties']
                polVars["multi_select"] = False

                # Enable Local Server Video
                polVars["Description"] = 'Enables Tunneled vKVM on the endpoint. Applicable only for Device Connectors that support Tunneled vKVM'
                polVars["varInput"] = f'Do you want to Tunneled vKVM through Intersight for this Policy?\n'
                '* Note: Make sure to Enable Virtual Tunneled KVM Launch and Configuration under:\n'
                'Setttings > Settings > Security & Privacy.'
                polVars["varDefault"] = 'N'
                polVars["varName"] = 'Allow Tunneled vKVM'
                polVars["allow_tunneled_vkvm"] = ezfunctions.varBoolLoop(**polVars)

                # Enable Local Server Video
                polVars["Description"] = jsonVars['EnableLocalServerVideo']['description']
                polVars["varInput"] = f'Do you want to Display KVM on Monitors attached to the Server?'
                polVars["varDefault"] = 'Y'
                polVars["varName"] = 'Enable Local Server Video'
                polVars["enable_local_server_video"] = ezfunctions.varBoolLoop(**polVars)

                # Enable Video Encryption
                polVars["Description"] = jsonVars['EnableVideoEncryption']['description']
                polVars["varInput"] = f'Do you want to Enable video Encryption?'
                polVars["varDefault"] = 'Y'
                polVars["varName"] = 'Enable Video Encryption'
                polVars["enable_video_encryption"] = ezfunctions.varBoolLoop(**polVars)

                # Obtain the Port to Use for vKVM
                polVars["Description"] = jsonVars['RemotePort']['description']
                polVars["varDefault"] =  jsonVars['RemotePort']['default']
                polVars["varInput"] = 'What is the Port you would like to Assign for Remote Access?\n'
                'This should be a value between 1024-65535. [2068]: '
                polVars["varName"] = 'Remote Port'
                polVars["varRegex"] = '^[0-9]+$'
                polVars["minNum"] = 1
                polVars["maxNum"] = 65535
                polVars["remote_port"] = ezfunctions.varNumberLoop(**polVars)

                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'   description               = "{polVars["descr"]}"')
                print(f'   enable_local_server_video = {polVars["enable_local_server_video"]}')
                print(f'   enable_video_encryption   = {polVars["enable_video_encryption"]}')
                print(f'   enable_virtual_kvm        = {polVars["enable_virtual_kvm"]}')
                print(f'   maximum_sessions          = {polVars["maximum_sessions"]}')
                print(f'   name                      = "{polVars["name"]}"')
                print(f'   remote_port               = "{polVars["remote_port"]}"')
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
    # Virtual Media Policy Policy Module
    #==============================================
    def virtual_media_policies(self, jsonData, ezData, **kwargs):
        name_prefix = self.name_prefix
        name_suffix = 'vmedia'
        opSystem = kwargs['opSystem']
        org = self.org
        policy_type = 'Virtual Media Policy'
        polVars = {}
        polVars["header"] = '%s Variables' % (policy_type)
        polVars["initial_write"] = True
        polVars["org"] = org
        polVars["policy_type"] = policy_type
        polVars["template_file"] = 'template_open.jinja2'
        polVars["template_type"] = 'virtual_media_policies'
        tfDir = kwargs['tfDir']

        # Open the Template file
        ezfunctions.write_to_template(self, **polVars)
        polVars["initial_write"] = False

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
            if opSystem == 'Windows':
                print(f'  - {tfDir}\\{org}\\{self.type}\\{polVars["template_type"]}.auto.tfvars')
            else:
                print(f'  - {tfDir}/{org}/{self.type}/{polVars["template_type"]}.auto.tfvars')
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

                    polVars["name"] = ezfunctions.policy_name(name, policy_type)
                    polVars["descr"] = ezfunctions.policy_descr(polVars["name"], policy_type)
                    polVars["enable_virtual_media"] = True

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'    Select this option to enable the appearance of virtual drives on the boot selection menu')
                    print(f'    after mapping the image and rebooting the host. This property is enabled by default.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid = False
                    while valid == False:
                        question = input(f'Do you want to Enable Low Power USB?  Enter "Y" or "N" [Y]: ')
                        if question == 'N':
                            polVars["enable_low_power_usb"] = False
                            valid = True
                        elif question == '' or question == 'Y':
                            polVars["enable_low_power_usb"] = True
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
                            polVars["enable_virtual_media_encryption"] = False
                            valid = True
                        elif question == '' or question == 'Y':
                            polVars["enable_virtual_media_encryption"] = True
                            valid = True
                        else:
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                            print(f'\n-------------------------------------------------------------------------------------------\n')

                    polVars["virtual_media"] = []
                    inner_loop_count = 1
                    sub_loop = False
                    while sub_loop == False:
                        question = input(f'\nWould you like to add vMedia to this Policy?  Enter "Y" or "N" [Y]: ')
                        if question == '' or question == 'Y':
                            valid_sub = False
                            while valid_sub == False:
                                polVars["multi_select"] = False
                                jsonVars = jsonData['vmedia.Mapping']['allOf'][1]['properties']
                                polVars["var_description"] = jsonVars['MountProtocol']['description']
                                polVars["jsonVars"] = sorted(jsonVars['MountProtocol']['enum'])
                                polVars["defaultVar"] = jsonVars['MountProtocol']['default']
                                polVars["varType"] = 'vMedia Mount Protocol'
                                Protocol = ezfunctions.variablesFromAPI(**polVars)

                                polVars["var_description"] = jsonVars['MountProtocol']['description']
                                polVars["jsonVars"] = sorted(jsonVars['MountProtocol']['enum'])
                                polVars["defaultVar"] = jsonVars['MountProtocol']['default']
                                polVars["varType"] = 'vMedia Mount Protocol'
                                deviceType = ezfunctions.variablesFromAPI(**polVars)

                                if Protocol == 'cifs':
                                    polVars["var_description"] = jsonVars['AuthenticationProtocol']['description']
                                    polVars["jsonVars"] = sorted(jsonVars['AuthenticationProtocol']['enum'])
                                    polVars["defaultVar"] = jsonVars['AuthenticationProtocol']['default']
                                    polVars["varType"] = 'CIFS Authentication Protocol'
                                    authProtocol = ezfunctions.variablesFromAPI(**polVars)

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
                                        polVars["varName"] = 'File Location'
                                        varValue = Question
                                        if re.search('(http|https)', Protocol):
                                            valid = validating.url(polVars["varName"], varValue)
                                        else:
                                            varValue = 'http://%s' % (Question)
                                            valid = validating.url(polVars["varName"], varValue)
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
                                        polVars["minLength"] = 1
                                        polVars["maxLength"] = 255
                                        polVars["varName"] = 'Username'
                                        varValue = Question
                                        valid = validating.string_length(polVars["varName"], varValue, polVars["minLength"], polVars["maxLength"])
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
                                        polVars["minLength"] = 1
                                        polVars["maxLength"] = 255
                                        polVars["rePattern"] = '^[\\S]+$'
                                        polVars["varName"] = 'Password'
                                        varValue = Password
                                        valid_passphrase = validating.length_and_regex_sensitive(polVars["rePattern"], polVars["varName"], varValue, polVars["minLength"], polVars["maxLength"])
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
                                    polVars["multi_select"] = True
                                    jsonVars = ezData['policies']['vmedia.Mapping']
                                    if Protocol == 'cifs':
                                        polVars["var_description"] = jsonVars['cifs.mountOptions']['description']
                                        polVars["jsonVars"] = sorted(jsonVars['cifs.mountOptions']['enum'])
                                        polVars["defaultVar"] = jsonVars['cifs.mountOptions']['default']
                                    elif Protocol == 'nfs':
                                        polVars["var_description"] = jsonVars['nfs.mountOptions']['description']
                                        polVars["jsonVars"] = sorted(jsonVars['nfs.mountOptions']['enum'])
                                        polVars["defaultVar"] = jsonVars['nfs.mountOptions']['default']
                                    else:
                                        polVars["multi_select"] = False
                                        polVars["var_description"] = jsonVars['http.mountOptions']['description']
                                        polVars["jsonVars"] = sorted(jsonVars['http.mountOptions']['enum'])
                                        polVars["defaultVar"] = jsonVars['http.mountOptions']['default']
                                    polVars["varType"] = 'Mount Options'
                                    mount_loop = ezfunctions.variablesFromAPI(**polVars)

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
                                                    polVars["minNum"] = 1
                                                    polVars["maxNum"] = 65535
                                                    polVars["varName"] = 'NFS Port'
                                                    varValue = Question
                                                    valid = validating.number_in_range(polVars["varName"], varValue, polVars["minNum"], polVars["maxNum"])
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
                                                    polVars["minNum"] = 1
                                                    polVars["maxNum"] = 65535
                                                    polVars["varName"] = 'NFS Port'
                                                    varValue = Question
                                                    valid = validating.number_in_range(polVars["varName"], varValue, polVars["minNum"], polVars["maxNum"])
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
                                                    polVars["minNum"] = 60
                                                    polVars["maxNum"] = 600
                                                    polVars["varName"] = 'NFS timeo'
                                                    varValue = Question
                                                    valid = validating.number_in_range(polVars["varName"], varValue, polVars["minNum"], polVars["maxNum"])
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
                                                    polVars["minNum"] = 1024
                                                    polVars["maxNum"] = 1048576
                                                    polVars["varName"] = 'NFS timeo'
                                                    varValue = Question
                                                    validCount = 0
                                                    validNum = validating.number_in_range(polVars["varName"], varValue, polVars["minNum"], polVars["maxNum"])
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
                                        polVars["virtual_media"].append(vmedia_map)
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
                    print(f'    description                     = "{polVars["descr"]}"')
                    print(f'    enable_low_power_usb            = "{polVars["enable_low_power_usb"]}"')
                    print(f'    enable_virtual_media            = "{polVars["enable_virtual_media"]}"')
                    print(f'    enable_virtual_media_encryption = "{polVars["enable_virtual_media_encryption"]}"')
                    print(f'    name                            = "{polVars["name"]}"')
                    if len(polVars["virtual_media"]) > 0:
                        print(f'    virtual_media = ''{')
                        for item in polVars["virtual_media"]:
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
