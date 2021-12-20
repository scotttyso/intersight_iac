#!/usr/bin/env python3

import jinja2
import os
import pkg_resources
import re
import stdiomask
import validating
from easy_functions import exit_default_no, exit_default_yes
from easy_functions import policy_descr, policy_name
from easy_functions import snmp_trap_servers, snmp_users
from easy_functions import syslog_servers
from easy_functions import varBoolLoop
from easy_functions import variablesFromAPI
from easy_functions import varNumberLoop
from easy_functions import varStringLoop
from easy_functions import write_to_template

ucs_template_path = pkg_resources.resource_filename('class_policies_p3', 'Templates/')

class policies_p3(object):
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
                    templateVars["Description"] = 'Configure SNMP Users'
                    templateVars["varInput"] = f'Would you like to configure an SNMPv3 User?'
                    templateVars["varDefault"] = 'Y'
                    templateVars["varName"] = 'Enable Trunking'
                    configure_snmp_users = varBoolLoop(**templateVars)
                    if configure_snmp_users == True:
                        snmp_loop = False
                        while snmp_loop == False:
                            snmp_user_list,snmp_loop = snmp_users(jsonData, ilCount, **templateVars)

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

    #========================================
    # Storage Policy Module
    #========================================
    def storage_policies(self, jsonData, easy_jsonData):
        name_prefix = self.name_prefix
        name_suffix = 'storage'
        org = self.org
        policy_names = []
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
            print(f'  A {policy_type} allows you to create drive groups, virtual drives, configure the ')
            print(f'  storage capacity of a virtual drive, and configure the M.2 RAID controllers.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - Intersight/{org}/{self.type}/{templateVars["template_type"]}.auto.tfvars')
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
                    templateVars["name"] = policy_name(name, policy_type)
                    # Obtain Policy Description
                    templateVars["descr"] = policy_descr(templateVars["name"], policy_type)

                    # Configure the Global Host Spares Setting
                    templateVars["multi_select"] = False
                    jsonVars = jsonData['components']['schemas']['storage.StoragePolicy']['allOf'][1]['properties']

                    # Configure the Global Host Spares Setting
                    templateVars["Description"] = jsonVars['GlobalHotSpares']['description']
                    templateVars["varDefault"] = ''
                    templateVars["varInput"] = 'Specify the disks that are to be used as hot spares,\n globally,'\
                        ' for all the Drive Groups. [press enter to skip]:'
                    templateVars["varName"] = 'Global Hot Spares'
                    templateVars["varRegex"] = jsonVars['GlobalHotSpares']['pattern']
                    templateVars["minLength"] = 0
                    templateVars["maxLength"] = 128
                    templateVars["global_hot_spares"] = varStringLoop(**templateVars)

                    # Obtain Unused Disks State
                    templateVars["var_description"] = jsonVars['UnusedDisksState']['description']
                    templateVars["jsonVars"] = sorted(jsonVars['UnusedDisksState']['enum'])
                    templateVars["defaultVar"] = jsonVars['UnusedDisksState']['default']
                    templateVars["varType"] = 'Unused Disks State'
                    templateVars["unused_disks_state"] = variablesFromAPI(**templateVars)

                    # Configure the Global Host Spares Setting
                    templateVars["Description"] = jsonVars['UseJbodForVdCreation']['description']
                    templateVars["varInput"] = f'Do you want to Use JBOD drives for Virtual Drive creation?'
                    templateVars["varDefault"] = 'N'
                    templateVars["varName"] = 'Use Jbod For Vd Creation'
                    templateVars["use_jbod_for_vd_creation"] = varBoolLoop(**templateVars)

                    # Ask if Drive Groups should be configured
                    templateVars["Description"] = 'Drive Group Configuration - Enable to add RAID drive groups that can be used to create'\
                        ' virtual drives.  You can also specify the Global Hot Spares information.'
                    templateVars["varInput"] = f'Do you want to Configure Drive Groups?'
                    templateVars["varDefault"] = 'N'
                    templateVars["varName"] = 'Drive Groups'
                    driveGroups = varBoolLoop(**templateVars)

                    # If True configure Drive Groups
                    if driveGroups == True:
                        templateVars["drive_groups"] = []
                        inner_loop_count = 1
                        drive_group = []
                        drive_group_loop = False
                        while drive_group_loop == False:
                            jsonVars = jsonData['components']['schemas']['storage.DriveGroup']['allOf'][1]['properties']

                            # Request Drive Group Name
                            templateVars["Description"] = jsonVars['Name']['description']
                            templateVars["varDefault"] = f'dg{inner_loop_count - 1}'
                            templateVars["varInput"] = f'Enter the Drive Group Name.  [{templateVars["varDefault"]}]:'
                            templateVars["varName"] = 'Drive Group Name'
                            templateVars["varRegex"] = jsonVars['Name']['pattern']
                            templateVars["minLength"] = 1
                            templateVars["maxLength"] = 60
                            dgName = varStringLoop(**templateVars)

                            # Obtain Raid Level for Drive Group
                            templateVars["var_description"] = jsonVars['RaidLevel']['description']
                            templateVars["jsonVars"] = sorted(jsonVars['RaidLevel']['enum'])
                            templateVars["defaultVar"] = jsonVars['RaidLevel']['default']
                            templateVars["varType"] = 'Raid Level'
                            RaidLevel = variablesFromAPI(**templateVars)

                            jsonVars = jsonData['components']['schemas']['storage.ManualDriveGroup']['allOf'][1]['properties']

                            # If Raid Level is anything other than Raid0 ask for Hot Spares
                            if not RaidLevel == 'Raid0':
                                templateVars["Description"] = jsonVars['DedicatedHotSpares']['description']
                                templateVars["varInput"] = 'Enter the Drives to add as Dedicated Hot Spares [press enter to skip]:'
                                templateVars["varName"] = 'Dedicated Hot Spares'
                                templateVars["varRegex"] = jsonVars['DedicatedHotSpares']['pattern']
                                templateVars["minLength"] = 1
                                templateVars["maxLength"] = 60
                                DedicatedHotSpares = varStringLoop(**templateVars)
                            else:
                                DedicatedHotSpares = ''

                            # Configure Span Slots
                            SpanSlots = []
                            # If Riad is 10, 50 or 60 allow multiple Span Slots
                            if re.fullmatch('^Raid(10|50|60)$', RaidLevel):
                                templateVars["var_description"] = jsonVars['SpanGroups']['items']['description']
                                templateVars["jsonVars"] = [2, 4, 6, 8]
                                templateVars["defaultVar"] = 2
                                templateVars["varType"] = 'Span Groups'
                                SpanGroups = variablesFromAPI(**templateVars)
                                if SpanGroups == 2:
                                    SpanGroups = [0, 1]
                                elif SpanGroups == 4:
                                    SpanGroups = [0, 1, 2, 3]
                                elif SpanGroups == 6:
                                    SpanGroups = [0, 1, 2, 3, 4, 5]
                                elif SpanGroups == 8:
                                    SpanGroups = [0, 1, 2, 3, 4, 5, 6, 7]


                                for span in SpanGroups:
                                    jsonVars = jsonData['components']['schemas']['storage.SpanDrives']['allOf'][1]['properties']
                                    templateVars["Description"] = jsonVars['Slots']['description']
                                    if re.fullmatch('^Raid10$', RaidLevel):
                                        Drive1 = (inner_loop_count * 2) - 1
                                        Drive2 = (inner_loop_count * 2)
                                        templateVars["varDefault"] = f'{Drive1}-{Drive2}'
                                    elif re.fullmatch('^Raid50$', RaidLevel):
                                        Drive1 = (inner_loop_count * 3) - 2
                                        Drive2 = (inner_loop_count * 3)
                                        templateVars["varDefault"] = f'{Drive1}-{Drive2}'
                                    elif re.fullmatch('^Raid60$', RaidLevel):
                                        Drive1 = (inner_loop_count * 4) - 3
                                        Drive2 = (inner_loop_count * 4)
                                        templateVars["varDefault"] = f'{Drive1}-{Drive2}'
                                    templateVars["varInput"] = f'Enter the Drive Slots for Drive Array Span {span}. [{templateVars["varDefault"]}]:'
                                    templateVars["varName"] = 'Drive Slots'
                                    templateVars["varRegex"] = jsonVars['Slots']['pattern']
                                    templateVars["minLength"] = 1
                                    templateVars["maxLength"] = 10
                                    SpanSlots.append({'slots':varStringLoop(**templateVars)})
                            elif re.fullmatch('^Raid(0|1|5|6)$', RaidLevel):
                                jsonVars = jsonData['components']['schemas']['storage.SpanDrives']['allOf'][1]['properties']
                                templateVars["Description"] = jsonVars['Slots']['description']
                                if re.fullmatch('^Raid(0|1)$', RaidLevel):
                                    Drive1 = (inner_loop_count * 2) - 1
                                    Drive2 = (inner_loop_count * 2)
                                    templateVars["varDefault"] = f'{Drive1}-{Drive2}'
                                elif re.fullmatch('^Raid5$', RaidLevel):
                                    Drive1 = (inner_loop_count * 3) - 2
                                    Drive2 = (inner_loop_count * 3)
                                    templateVars["varDefault"] = f'{Drive1}-{Drive2}'
                                elif re.fullmatch('^Raid6$', RaidLevel):
                                    Drive1 = (inner_loop_count * 4) - 3
                                    Drive2 = (inner_loop_count * 4)
                                    templateVars["varDefault"] = f'{Drive1}-{Drive2}'
                                templateVars["varInput"] = f'Enter the Drive Slots for Drive Array Span 0. [{templateVars["varDefault"]}]:'
                                templateVars["varName"] = 'Drive Slots'
                                templateVars["varRegex"] = jsonVars['Slots']['pattern']
                                templateVars["minLength"] = 1
                                templateVars["maxLength"] = 10
                                SpanSlots.append({'slots':varStringLoop(**templateVars)})
                                
                            virtualDrives = []
                            sub_loop_count = 0
                            sub_loop = False
                            while sub_loop == False:
                                jsonVars = jsonData['components']['schemas']['storage.VirtualDriveConfiguration']['allOf'][1]['properties']

                                templateVars["Description"] = jsonVars['Name']['description']
                                templateVars["varDefault"] = f'vd{sub_loop_count}'
                                templateVars["varInput"] = f'Enter the name of the Virtual Drive.  [vd{sub_loop_count}]'
                                templateVars["varName"] = 'Drive Group Name'
                                templateVars["varRegex"] = jsonVars['Name']['pattern']
                                templateVars["minLength"] = 1
                                templateVars["maxLength"] = 60
                                vd_name = varStringLoop(**templateVars)

                                templateVars["Description"] = jsonVars['ExpandToAvailable']['description']
                                templateVars["varInput"] = f'Do you want to expand to all the space in the drive group?'
                                templateVars["varDefault"] = 'Y'
                                templateVars["varName"] = 'Expand To Available'
                                ExpandToAvailable = varBoolLoop(**templateVars)

                                # If Expand to Available is Disabled obtain Virtual Drive disk size
                                if ExpandToAvailable == False:
                                    templateVars["Description"] = jsonVars['Size']['description']
                                    templateVars["varDefault"] =  '1'
                                    templateVars["varInput"] = 'What is the Size for this Virtual Drive?'
                                    templateVars["varName"] = 'Size'
                                    templateVars["varRegex"] = '[0-9]+'
                                    templateVars["minNum"] = jsonVars['Size']['minimum']
                                    templateVars["maxNum"] = 9999999999
                                    vdSize = varNumberLoop(**templateVars)
                                else:
                                    vdSize = 1
                                
                                templateVars["Description"] = jsonVars['BootDrive']['description']
                                templateVars["varInput"] = f'Do you want to configure {vd_name} as a boot drive?'
                                templateVars["varDefault"] = 'Y'
                                templateVars["varName"] = 'Boot Drive'
                                BootDrive = varBoolLoop(**templateVars)

                                jsonVars = jsonData['components']['schemas']['storage.VirtualDrivePolicy']['allOf'][1]['properties']

                                templateVars["var_description"] = jsonVars['AccessPolicy']['description']
                                templateVars["jsonVars"] = sorted(jsonVars['AccessPolicy']['enum'])
                                templateVars["defaultVar"] = jsonVars['AccessPolicy']['default']
                                templateVars["varType"] = 'Access Policy'
                                AccessPolicy = variablesFromAPI(**templateVars)

                                templateVars["var_description"] = jsonVars['DriveCache']['description']
                                templateVars["jsonVars"] = sorted(jsonVars['DriveCache']['enum'])
                                templateVars["defaultVar"] = jsonVars['DriveCache']['default']
                                templateVars["varType"] = 'Drive Cache'
                                DriveCache = variablesFromAPI(**templateVars)

                                templateVars["var_description"] = jsonVars['ReadPolicy']['description']
                                templateVars["jsonVars"] = sorted(jsonVars['ReadPolicy']['enum'])
                                templateVars["defaultVar"] = jsonVars['ReadPolicy']['default']
                                templateVars["varType"] = 'Read Policy'
                                ReadPolicy = variablesFromAPI(**templateVars)

                                templateVars["var_description"] = jsonVars['StripSize']['description']
                                templateVars["jsonVars"] = sorted(jsonVars['StripSize']['enum'])
                                templateVars["defaultVar"] = jsonVars['StripSize']['default']
                                templateVars["varType"] = 'Strip Size'
                                StripSize = variablesFromAPI(**templateVars)

                                templateVars["var_description"] = jsonVars['WritePolicy']['description']
                                templateVars["jsonVars"] = sorted(jsonVars['WritePolicy']['enum'])
                                templateVars["defaultVar"] = jsonVars['WritePolicy']['default']
                                templateVars["varType"] = 'Write Policy'
                                WritePolicy = variablesFromAPI(**templateVars)

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
                                    templateVars["drive_groups"].append(drive_group)
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
                        templateVars["drive_group"] = []

                    # Ask if M2 should be configured
                    templateVars["Description"] = jsonVars['M2VirtualDrive']['description']
                    templateVars["varInput"] = f'Do you want to Enable the M.2 Virtual Drive Configuration?'
                    templateVars["varDefault"] = 'Y'
                    templateVars["varName"] = 'M.2 Virtual Drive'
                    M2VirtualDrive = varBoolLoop(**templateVars)

                    # Configure M2 if it is True if not Pop it from the list
                    if M2VirtualDrive == True:
                        jsonVars = jsonData['components']['schemas']['storage.M2VirtualDriveConfig']['allOf'][1]['properties']

                        templateVars["var_description"] = jsonVars['ControllerSlot']['description']
                        templateVars["jsonVars"] = sorted(jsonVars['ControllerSlot']['enum'])
                        templateVars["defaultVar"] = 'MSTOR-RAID-1,MSTOR-RAID-2'
                        templateVars["varType"] = 'Controller Slot'
                        ControllerSlot = variablesFromAPI(**templateVars)

                        templateVars["m2_configuration"] = {
                            'controller_slot':ControllerSlot,
                            'enable':True
                        }
                    else:
                        templateVars.pop('m2_configuration')

                    # Ask if Drive Groups should be configured
                    templateVars["Description"] = 'Enable to create RAID0 virtual drives on each physical drive..'
                    templateVars["varInput"] = f"Do you want to Configure Single Drive RAID's?"
                    templateVars["varDefault"] = 'N'
                    templateVars["varName"] = 'Single Drive RAID'
                    singledriveRaid = varBoolLoop(**templateVars)

                    # If True configure Drive Groups
                    if singledriveRaid == True:
                        single_drive_loop = False
                        while single_drive_loop == False:
                            # Obtain the Single Drive Raid Slots
                            jsonVars = jsonData['components']['schemas']['storage.R0Drive']['allOf'][1]['properties']
                            templateVars["Description"] = jsonVars['DriveSlots']['description']
                            templateVars["varDefault"] = f'{Drive1}-{Drive2}'
                            templateVars["varInput"] = f'Enter the Drive Slots for Drive Array Span 0. [{templateVars["varDefault"]}]:'
                            templateVars["varName"] = 'Drive Slots'
                            templateVars["varRegex"] = jsonVars['DriveSlots']['pattern']
                            templateVars["minLength"] = 1
                            templateVars["maxLength"] = 64
                            DriveSlots = varStringLoop(**templateVars)
                                
                            # Obtain the Virtual Drive Policies
                            jsonVars = jsonData['components']['schemas']['storage.VirtualDrivePolicy']['allOf'][1]['properties']

                            # Access Policy
                            templateVars["var_description"] = jsonVars['AccessPolicy']['description']
                            templateVars["jsonVars"] = sorted(jsonVars['AccessPolicy']['enum'])
                            templateVars["defaultVar"] = jsonVars['AccessPolicy']['default']
                            templateVars["varType"] = 'Access Policy'
                            AccessPolicy = variablesFromAPI(**templateVars)

                            # Drive Cache
                            templateVars["var_description"] = jsonVars['DriveCache']['description']
                            templateVars["jsonVars"] = sorted(jsonVars['DriveCache']['enum'])
                            templateVars["defaultVar"] = jsonVars['DriveCache']['default']
                            templateVars["varType"] = 'Drive Cache'
                            DriveCache = variablesFromAPI(**templateVars)

                            # Read Policy
                            templateVars["var_description"] = jsonVars['ReadPolicy']['description']
                            templateVars["jsonVars"] = sorted(jsonVars['ReadPolicy']['enum'])
                            templateVars["defaultVar"] = jsonVars['ReadPolicy']['default']
                            templateVars["varType"] = 'Read Policy'
                            ReadPolicy = variablesFromAPI(**templateVars)

                            # Strip Size
                            templateVars["var_description"] = jsonVars['StripSize']['description']
                            templateVars["jsonVars"] = sorted(jsonVars['StripSize']['enum'])
                            templateVars["defaultVar"] = jsonVars['StripSize']['default']
                            templateVars["varType"] = 'Strip Size'
                            StripSize = variablesFromAPI(**templateVars)

                            # Write Policy
                            templateVars["var_description"] = jsonVars['WritePolicy']['description']
                            templateVars["jsonVars"] = sorted(jsonVars['WritePolicy']['enum'])
                            templateVars["defaultVar"] = jsonVars['WritePolicy']['default']
                            templateVars["varType"] = 'Write Policy'
                            WritePolicy = variablesFromAPI(**templateVars)

                            templateVars["single_drive_raid_configuration"] = {
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
                            print(f'      access_policy = "{templateVars["single_drive_raid_configuration"]["access_policy"]}"')
                            print(f'      disk_cache    = "{templateVars["single_drive_raid_configuration"]["disk_cache"]}"')
                            print(f'      drive_slots   = "{templateVars["single_drive_raid_configuration"]["expand_to_available"]}"')
                            print(f'      enable        = {templateVars["single_drive_raid_configuration"]["enable"]}')
                            print(f'      read_policy   = "{templateVars["single_drive_raid_configuration"]["read_policy"]}"')
                            print(f'      strip_size    = "{templateVars["single_drive_raid_configuration"]["strip_size"]}"')
                            print(f'      write_policy  = "{templateVars["single_drive_raid_configuration"]["write_policy"]}"')
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
                    print(f'    description              = "{templateVars["descr"]}"')
                    print(f'    global_hot_spares        = "{templateVars["global_hot_spares"]}"')
                    print(f'    unused_disks_state       = "{templateVars["unused_disks_state"]}"')
                    print(f'    use_jbod_for_vd_creation = "{templateVars["use_jbod_for_vd_creation"]}"')
                    dg_count = 0
                    if len(templateVars["drive_groups"]) > 0:
                        print(f'    drive_groups = ''{')
                        for drive_group in templateVars["drive_groups"]:
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
                    if templateVars.get("m2_configuration"):
                        print(f'    m2_configuration = ''{')
                        print(f'      "0" = ''{')
                        print(f'        controller_slot = "{templateVars["m2_configuration"]["controller_slot"]}"')
                        print(f'      ''}')
                        print(f'    ''}')
                    else:
                        print(f'    m2_configuration = ''{}')
                    if templateVars.get("single_drive_raid_configuration"):
                        print(f'    single_drive_raid_configuration = ''{')
                        print(f'    "0" = ''{')
                        print(f'      access_policy = "{templateVars["single_drive_raid_configuration"]["access_policy"]}"')
                        print(f'      disk_cache    = "{templateVars["single_drive_raid_configuration"]["disk_cache"]}"')
                        print(f'      drive_slots   = "{templateVars["single_drive_raid_configuration"]["drive_slots"]}"')
                        print(f'      enable        = {templateVars["single_drive_raid_configuration"]["enable"]}')
                        print(f'      read_policy   = "{templateVars["single_drive_raid_configuration"]["read_policy"]}"')
                        print(f'      strip_size    = "{templateVars["single_drive_raid_configuration"]["strip_size"]}"')
                        print(f'      write_policy  = "{templateVars["single_drive_raid_configuration"]["write_policy"]}"')
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
                            templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
                            write_to_template(self, **templateVars)

                            # Add Template Name to Policies Output
                            policy_names.append(templateVars["name"])

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
    # Switch Control Policy Module
    #==============================================
    def switch_control_policies(self, jsonData, easy_jsonData):
        name_prefix = self.name_prefix
        name_suffix = 'sw_ctrl'
        org = self.org
        policy_type = 'Switch Control Policy'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'switch_control_policies'

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  A Switch Control Policy will configure Unidirectional Link Detection Protocol and')
            print(f'  MAC Address Learning Settings for the UCS Domain Profile.')
            print(f'  We recommend the settings the wizard is setup to push.  So you will only be asked for')
            print(f'  the name and description for the Policy.  You only need one of these policies for')
            print(f'  Organization {org}.\n')
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

                templateVars["mac_address_table_aging"] = 'Default'
                templateVars["mac_aging_time"] = 14500
                templateVars["udld_message_interval"] = 15
                templateVars["udld_recovery_action"] = "reset"
                templateVars["vlan_port_count_optimization"] = False

                # Pull Information from the API
                templateVars["multi_select"] = False
                jsonVars = jsonData['components']['schemas']['fabric.FcNetworkPolicy']['allOf'][1]['properties']

                # Ethernet Switching Mode
                templateVars["var_description"] = jsonVars['EthernetSwitchingMode']['description']
                templateVars["jsonVars"] = sorted(jsonVars['EthernetSwitchingMode']['enum'])
                templateVars["defaultVar"] = jsonVars['EthernetSwitchingMode']['default']
                templateVars["varType"] = 'Ethernet Switching Mode'
                templateVars["ethernet_switching_mode"] = variablesFromAPI(**templateVars)

                # Ethernet Switching Mode
                templateVars["var_description"] = jsonVars['FcSwitchingMode']['description']
                templateVars["jsonVars"] = sorted(jsonVars['FcSwitchingMode']['enum'])
                templateVars["defaultVar"] = jsonVars['FcSwitchingMode']['default']
                templateVars["varType"] = 'FC Switching Mode'
                templateVars["fc_switching_mode"] = variablesFromAPI(**templateVars)

                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'    description                  = "{templateVars["descr"]}"')
                print(f'    ethernet_switching_mode      = "{templateVars["ethernet_switching_mode"]}"')
                print(f'    fc_switching_mode            = "{templateVars["fc_switching_mode"]}"')
                print(f'    mac_address_table_aging      = "{templateVars["mac_address_table_aging"]}"')
                print(f'    mac_aging_time               = {templateVars["mac_aging_time"]}')
                print(f'    name                         = "{templateVars["name"]}"')
                print(f'    udld_message_interval        = {templateVars["udld_message_interval"]}')
                print(f'    udld_recovery_action         = "{templateVars["udld_recovery_action"]}"')
                print(f'    vlan_port_count_optimization = {templateVars["vlan_port_count_optimization"]}')
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
                    if templateVars["remote_logging"].get("server1"):
                        print(f'      ''{')
                        print(f'        enabled      = {"%s".lower() % (templateVars["remote_logging"]["server1"]["enable"])}')
                        print(f'        hostname     = "{templateVars["remote_logging"]["server1"]["hostname"]}"')
                        print(f'        min_severity = "{templateVars["remote_logging"]["server1"]["min_severity"]}"')
                        print(f'        port         = {templateVars["remote_logging"]["server1"]["port"]}')
                        print(f'        protocol     = "{templateVars["remote_logging"]["server1"]["protocol"]}"')
                        print(f'      ''}')
                        item_count += 1
                    if templateVars["remote_logging"].get("server2"):
                        print(f'      ''{')
                        print(f'        enabled      = {"%s".lower() % (templateVars["remote_logging"]["server2"]["enable"])}')
                        print(f'        hostname     = "{templateVars["remote_logging"]["server2"]["hostname"]}"')
                        print(f'        min_severity = "{templateVars["remote_logging"]["server2"]["min_severity"]}"')
                        print(f'        port         = {templateVars["remote_logging"]["server2"]["port"]}')
                        print(f'        protocol     = "{templateVars["remote_logging"]["server2"]["protocol"]}"')
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
    # System QoS Policy Module
    #==============================================
    def system_qos_policies(self, jsonData, easy_jsonData):
        name_prefix = self.name_prefix
        name_suffix = 'qos'
        org = self.org
        policy_type = 'System QoS Policy'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'system_qos_policies'

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

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
                    mtu = input('Do you want to enable Jumbo MTU?  Enter "Y" or "N" [Y]: ')
                    if mtu == '' or mtu == 'Y':
                        templateVars["mtu"] = 9216
                        valid = True
                    elif mtu == 'N':
                        templateVars["mtu"] = 1500
                        valid = True
                    else:
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        print(f'  Error!! Invalid Option.  Please enter "Y" or "N".')
                        print(f'\n-------------------------------------------------------------------------------------------\n')

                domain_mtu = templateVars["mtu"]

                templateVars["Platinum"] = {
                    'bandwidth_percent':20,
                    'cos':5,
                    'mtu':templateVars["mtu"],
                    'multicast_optimize':False,
                    'packet_drop':False,
                    'priority':'Platinum',
                    'state':'Enabled',
                    'weight':10,
                }
                templateVars["Gold"] = {
                    'bandwidth_percent':18,
                    'cos':4,
                    'mtu':templateVars["mtu"],
                    'multicast_optimize':False,
                    'packet_drop':True,
                    'priority':'Gold',
                    'state':'Enabled',
                    'weight':9,
                }
                templateVars["FC"] = {
                    'bandwidth_percent':20,
                    'cos':3,
                    'mtu':2240,
                    'multicast_optimize':False,
                    'packet_drop':False,
                    'priority':'FC',
                    'state':'Enabled',
                    'weight':10,
                }
                templateVars["Silver"] = {
                    'bandwidth_percent':18,
                    'cos':2,
                    'mtu':templateVars["mtu"],
                    'multicast_optimize':False,
                    'packet_drop':True,
                    'priority':'Silver',
                    'state':'Enabled',
                    'weight':8,
                }
                templateVars["Bronze"] = {
                    'bandwidth_percent':14,
                    'cos':1,
                    'mtu':templateVars["mtu"],
                    'multicast_optimize':False,
                    'packet_drop':True,
                    'priority':'Bronze',
                    'state':'Enabled',
                    'weight':7,
                }
                templateVars["Best Effort"] = {
                    'bandwidth_percent':10,
                    'cos':255,
                    'mtu':templateVars["mtu"],
                    'multicast_optimize':False,
                    'packet_drop':True,
                    'priority':'Best Effort',
                    'state':'Enabled',
                    'weight':5,
                }

                templateVars["classes"] = []
                priorities = ['Platinum', 'Gold', 'FC', 'Silver', 'Bronze', 'Best Effort']

                for priority in priorities:
                    templateVars["classes"].append(templateVars[priority])
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'    description = "{templateVars["descr"]}"')
                print(f'    name        = "{templateVars["name"]}"')
                print('    classes = {')
                for item in templateVars["classes"]:
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
