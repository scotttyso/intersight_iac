#!/usr/bin/env python3

import json
import os
import re
import subprocess
import stdiomask
import validating
# from class_policies_domain import policies_domain
from textwrap import fill

def choose_policy(policy, **templateVars):

    if 'policies' in policy:
        policy_short = policy.replace('policies', 'policy')
    elif 'pools' in policy:
        policy_short = policy.replace('pools', 'pool')
    elif 'templates' in policy:
        policy_short = policy.replace('templates', 'template')
    x = policy_short.split('_')
    policy_description = []
    for y in x:
        y = y.capitalize()
        policy_description.append(y)
    policy_description = " ".join(policy_description)
    policy_description = policy_description.replace('Ip', 'IP')
    policy_description = policy_description.replace('Ntp', 'NTP')
    policy_description = policy_description.replace('Snmp', 'SNMP')
    policy_description = policy_description.replace('Wwnn', 'WWNN')
    policy_description = policy_description.replace('Wwpn', 'WWPN')

    if len(policy) > 0:
        templateVars["policy"] = policy_description
        policy_short = policies_list(templateVars["policies"], **templateVars)
    else:
        policy_short = ""
    return policy_short

def exit_default_no(policy_type):
    valid_exit = False
    while valid_exit == False:
        exit_answer = input(f'Would You like to Configure another {policy_type}?  Enter "Y" or "N" [N]: ')
        if exit_answer == '' or exit_answer == 'N':
            policy_loop = True
            configure_loop = True
            valid_exit = True
        elif exit_answer == 'Y':
            policy_loop = False
            configure_loop = False
            valid_exit = True
        else:
            print(f'\n------------------------------------------------------\n')
            print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
            print(f'\n------------------------------------------------------\n')
    return configure_loop, policy_loop

def exit_default_yes(policy_type):
    valid_exit = False
    while valid_exit == False:
        exit_answer = input(f'Would You like to Configure another {policy_type}?  Enter "Y" or "N" [Y]: ')
        if exit_answer == '' or exit_answer == 'Y':
            policy_loop = False
            configure_loop = False
            valid_exit = True
        elif exit_answer == 'N':
            policy_loop = True
            configure_loop = True
            valid_exit = True
        else:
            print(f'\n------------------------------------------------------\n')
            print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
            print(f'\n------------------------------------------------------\n')
    return configure_loop, policy_loop

def exit_loop_default_yes(loop_count, policy_type):
    valid_exit = False
    while valid_exit == False:
        if loop_count % 2 == 0:
            exit_answer = input(f'Would You like to Configure another {policy_type}?  Enter "Y" or "N" [Y]: ')
        else:
            exit_answer = input(f'Would You like to Configure another {policy_type}?  Enter "Y" or "N" [N]: ')
        if (loop_count % 2 == 0 and exit_answer == '') or exit_answer == 'Y':
            policy_loop = False
            configure_loop = False
            loop_count += 1
            valid_exit = True
        elif not loop_count % 2 == 0 and exit_answer == '':
            policy_loop = True
            configure_loop = True
            valid_exit = True
        elif exit_answer == 'N':
            policy_loop = True
            configure_loop = True
            valid_exit = True
        else:
            print(f'\n------------------------------------------------------\n')
            print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
            print(f'\n------------------------------------------------------\n')
    return configure_loop, loop_count, policy_loop

def ipmi_key_function(**templateVars):
    print(f'\n-------------------------------------------------------------------------------------------\n')
    print(f'  The ipmi_key Must be in Hexidecimal Format [a-fA-F0-9] and no longer than 40 characters.')
    print(f'\n-------------------------------------------------------------------------------------------\n')
    valid = False
    while valid == False:
        password1 = stdiomask.getpass(prompt='Enter the ipmi_key: ')
        password2 = stdiomask.getpass(prompt='Please re-enter ipmi_key: ')
        if not password1 == '':
            if password1 == password2:
                TF_VAR = 'TF_VAR_ipmi_key_1'
                os.environ[TF_VAR] = '%s' % (password1)
                templateVars["ipmi_key"] = 1
                valid = validating.ipmi_key_check(password1)
            else:
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'  Error!! The Keys did not match.  Please Re-enter the IPMI Key.')
                print(f'\n-------------------------------------------------------------------------------------------\n')
        else:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  Error!! Invalid Value.  Please Re-enter the IPMI Key.')
            print(f'\n-------------------------------------------------------------------------------------------\n')

    return templateVars["ipmi_key"]

def local_users_function(jsonData, easy_jsonData, inner_loop_count, **templateVars):
    local_users = []
    valid_users = False
    while valid_users == False:
        templateVars["multi_select"] = False
        jsonVars = jsonData['components']['schemas']['iam.EndPointUser']['allOf'][1]['properties']

        templateVars["Description"] = jsonVars['Name']['description']
        templateVars["varDefault"] = 'admin'
        templateVars["varInput"] = 'What is the Local username?'
        templateVars["varName"] = 'Local User'
        templateVars["varRegex"] = jsonVars['Name']['pattern']
        templateVars["minLength"] = 1
        templateVars["maxLength"] = jsonVars['Name']['maxLength']
        username = varStringLoop(**templateVars)

        templateVars["multi_select"] = False
        jsonVars = easy_jsonData['policies']['iam.LocalUserPasswordPolicy']
        templateVars["var_description"] = jsonVars['role']['description']
        templateVars["jsonVars"] = sorted(jsonVars['role']['enum'])
        templateVars["defaultVar"] = jsonVars['role']['default']
        templateVars["varType"] = 'User Role'
        role = variablesFromAPI(**templateVars)

        if templateVars["enforce_strong_password"] == True:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print('Enforce Strong Password is enabled so the following rules must be followed:')
            print('  - The password must have a minimum of 8 and a maximum of 20 characters.')
            print("  - The password must not contain the User's Name.")
            print('  - The password must contain characters from three of the following four categories.')
            print('    * English uppercase characters (A through Z).')
            print('    * English lowercase characters (a through z).')
            print('    * Base 10 digits (0 through 9).')
            print('    * Non-alphabetic characters (! , @, #, $, %, ^, &, *, -, _, +, =)\n\n')
        valid = False
        while valid == False:
            password1 = stdiomask.getpass(f'What is the password for {username}? ')
            password2 = stdiomask.getpass(f'Please re-enter the password for {username}? ')
            if not password1 == '':
                if password1 == password2:
                    if templateVars["enforce_strong_password"] == True:
                        valid = validating.strong_password(f"{username}'s password", password1, 8, 20)

                    else:
                        valid = validating.string_length(f'{username} password', password1, 1, 127)

                else:
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  Error!! The Passwords did not match.  Please Re-enter the password for {username}.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
            else:
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'  Error!! Invalid Value.  Please Re-enter the password for {username}.')
                print(f'\n-------------------------------------------------------------------------------------------\n')
        TF_VAR = 'TF_VAR_local_user_password_%s' % (inner_loop_count)
        os.environ[TF_VAR] = '%s' % (password1)
        password1 = inner_loop_count

        user_attributes = {
            'enabled':True,
            'password':inner_loop_count,
            'role':role,
            'username':username
        }
        print(f'\n-------------------------------------------------------------------------------------------\n')
        print(f'   enabled  = True')
        print(f'   password = "Sensitive"')
        print(f'   role     = "{role}"')
        print(f'   username = "{username}"')
        print(f'\n-------------------------------------------------------------------------------------------\n')
        valid_confirm = False
        while valid_confirm == False:
            question = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
            if question == 'Y' or question == '':
                local_users.append(user_attributes)
                valid_exit = False
                while valid_exit == False:
                    loop_exit = input(f'Would You like to Configure another Local User?  Enter "Y" or "N" [N]: ')
                    if loop_exit == 'Y':
                        inner_loop_count += 1
                        valid_confirm = True
                        valid_exit = True
                    elif loop_exit == 'N' or loop_exit == '':
                        user_loop = True
                        valid_confirm = True
                        valid_exit = True
                        valid_users = True
                    else:
                        print(f'\n------------------------------------------------------\n')
                        print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                        print(f'\n------------------------------------------------------\n')

            elif question == 'N':
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'  Starting Local User Configuration Over.')
                print(f'\n-------------------------------------------------------------------------------------------\n')
                valid_confirm = True
            else:
                print(f'\n------------------------------------------------------\n')
                print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                print(f'\n------------------------------------------------------\n')

    return local_users,user_loop

def naming_rule(name_prefix, name_suffix, org):
    if not name_prefix == '':
        name = '%s_%s' % (name_prefix, name_suffix)
    else:
        name = '%s_%s' % (org, name_suffix)
    return name

def naming_rule_fabric(loop_count, name_prefix, org):
    if loop_count % 2 == 0:
        if not name_prefix == '':
            name = '%s_A' % (name_prefix)
        elif not org == 'default':
            name = '%s_A' % (org)
        else:
            name = 'Fabric_A'
    else:
        if not name_prefix == '':
            name = '%s_B' % (name_prefix)
        elif not org == 'default':
            name = '%s_B' % (org)
        else:
            name = 'Fabric_B'
    return name

def ntp_alternate():
    valid = False
    while valid == False:
        alternate_true = input('Do you want to Configure an Alternate NTP Server?  Enter "Y" or "N" [Y]: ')
        if alternate_true == 'Y' or alternate_true == '':
            alternate_ntp = input('What is your Alternate NTP Server? [1.north-america.pool.ntp.org]: ')
            if alternate_ntp == '':
                alternate_ntp = '1.north-america.pool.ntp.org'
            if re.search(r'[a-zA-Z]+', alternate_ntp):
                valid = validating.dns_name('Alternate NTP Server', alternate_ntp)
            else:
                valid = validating.ip_address('Alternate NTP Server', alternate_ntp)
        elif alternate_true == 'N':
            alternate_ntp = ''
            valid = True
        else:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
            print(f'\n-------------------------------------------------------------------------------------------\n')
    return alternate_ntp

def ntp_primary():
    valid = False
    while valid == False:
        primary_ntp = input('What is your Primary NTP Server [0.north-america.pool.ntp.org]: ')
        if primary_ntp == "":
            primary_ntp = '0.north-america.pool.ntp.org'
        if re.search(r'[a-zA-Z]+', primary_ntp):
            valid = validating.dns_name('Primary NTP Server', primary_ntp)
        else:
            valid = validating.ip_address('Primary NTP Server', primary_ntp)
    return primary_ntp

def policies_list(policies_list, **templateVars):
    valid = False
    while valid == False:
        print(f'\n-------------------------------------------------------------------------------------------\n')
        if templateVars.get('optional_message'):
            print(templateVars["optional_message"])
        print(f'  {templateVars["policy"]} Options:')
        for i, v in enumerate(policies_list):
            i += 1
            if i < 10:
                print(f'     {i}. {v}')
            else:
                print(f'    {i}. {v}')
        if templateVars["allow_opt_out"] == True:
            print(f'     99. Do not assign a(n) {templateVars["policy"]}.')
        print(f'     100. Create a New {templateVars["policy"]}.')
        print(f'\n-------------------------------------------------------------------------------------------\n')
        policyOption = input(f'Select the Option Number for the {templateVars["policy"]} to Assign to {templateVars["name"]}: ')
        if re.search(r'^[0-9]{1,3}$', policyOption):
            for i, v in enumerate(policies_list):
                i += 1
                if int(policyOption) == i:
                    policy = v
                    valid = True
                    return policy
                elif int(policyOption) == 99:
                    policy = ''
                    valid = True
                    return policy
                elif int(policyOption) == 100:
                    policy = 'create_policy'
                    valid = True
                    return policy

            if int(policyOption) == 99:
                policy = ''
                valid = True
                return policy
            elif int(policyOption) == 100:
                policy = 'create_policy'
                valid = True
                return policy
        else:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  Error!! Invalid Selection.  Please Select a valid Index from the List.')
            print(f'\n-------------------------------------------------------------------------------------------\n')

def policies_parse(org, policy_type, policy):
    if os.environ.get('TF_DEST_DIR') is None:
        tfDir = 'Intersight'
    else:
        tfDir = os.environ.get('TF_DEST_DIR')
    policies = []
    policy_file = f'./{tfDir}/{org}/{policy_type}/{policy}.auto.tfvars'
    if os.path.isfile(policy_file):
        if len(policy_file) > 0:
            cmd = 'json2hcl -reverse < %s' % (policy_file)
            p = subprocess.run(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            )
            if 'unable to parse' in p.stdout.decode('utf-8'):
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'  !!!! Encountered Error in Attempting to read file !!!!')
                print(f'  - {policy_file}')
                print(f'  Error was:')
                print(f'  - {p.stdout.decode("utf-8")}')
                print(f'\n-------------------------------------------------------------------------------------------\n')
                json_data = {}
                return policies,json_data
            else:
                json_data = json.loads(p.stdout.decode('utf-8'))
                for i in json_data[policy]:
                    for k, v in i.items():
                        policies.append(k)
                return policies,json_data
    else:
        json_data = {}
        return policies,json_data

def policy_descr(name, policy_type):
    valid = False
    while valid == False:
        descr = input(f'What is the Description for the {policy_type}?  [{name} {policy_type}]: ')
        if descr == '':
            descr = '%s %s' % (name, policy_type)
        valid = validating.description(f'{policy_type} templateVars["descr"]', descr, 1, 62)
        if valid == True:
            return descr

def policy_name(namex, policy_type):
    valid = False
    while valid == False:
        name = input(f'What is the Name for the {policy_type}?  [{namex}]: ')
        if name == '':
            name = '%s' % (namex)
        valid = validating.name_rule(f'{policy_type} Name', name, 1, 62)
        if valid == True:
            return name

def process_method(wr_method, dest_dir, dest_file, template, **templateVars):
    if os.environ.get('TF_DEST_DIR') is None:
        tfDir = 'Intersight'
    else:
        tfDir = os.environ.get('TF_DEST_DIR')
    dest_dir = './%s/%s/%s' % (tfDir, templateVars["org"], dest_dir)
    if not os.path.isdir(dest_dir):
        mk_dir = 'mkdir -p %s' % (dest_dir)
        os.system(mk_dir)
    dest_file_path = '%s/%s' % (dest_dir, dest_file)
    if not os.path.isfile(dest_file_path):
        create_file = 'touch %s' % (dest_file_path)
        os.system(create_file)
    tf_file = dest_file_path
    wr_file = open(tf_file, wr_method)

    # Render Payload and Write to File
    payload = template.render(templateVars)
    wr_file.write(payload)
    wr_file.close()

def sensitive_var_value(jsonData, **templateVars):
    sensitive_var = 'TF_VAR_%s' % (templateVars['Variable'])
    # -------------------------------------------------------------------------------------------------------------------------
    # Check to see if the Variable is already set in the Environment, and if not prompt the user for Input.
    #--------------------------------------------------------------------------------------------------------------------------
    if os.environ.get(sensitive_var) is None:
        print(f"\n----------------------------------------------------------------------------------\n")
        print(f"  The Script did not find {sensitive_var} as an 'environment' variable.")
        print(f"  To not be prompted for the value of {templateVars['Variable']} each time")
        print(f"  add the following to your local environemnt:\n")
        print(f"   - export {sensitive_var}='{templateVars['Variable']}_value'")
        print(f"\n----------------------------------------------------------------------------------\n")

    if os.environ.get(sensitive_var) is None:
        valid = False
        while valid == False:
            varValue = input('press enter to continue: ')
            if varValue == '':
                valid = True

        valid = False
        while valid == False:
            if templateVars.get('Multi_Line_Input'):
                print(f'Enter the value for {templateVars["Variable"]}:')
                lines = []
                while True:
                    # line = input('')
                    line = stdiomask.getpass(prompt='')
                    if line:
                        lines.append(line)
                    else:
                        break
                if not re.search('(certificate|private_key)', sensitive_var):
                    secure_value = '\\n'.join(lines)
                else:
                    secure_value = '\n'.join(lines)
            else:
                secure_value = stdiomask.getpass(prompt=f'Enter the value for {templateVars["Variable"]}: ')

            # Validate Sensitive Passwords
            cert_regex = re.compile(r'^\-{5}BEGIN (CERTIFICATE|PRIVATE KEY)\-{5}.*\-{5}END (CERTIFICATE|PRIVATE KEY)\-{5}$')
            if re.search('(certificate|private_key)', sensitive_var):
                if not re.search(cert_regex, secure_value):
                    valid = True
                else:
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'    Error!!! Invalid Value for the {sensitive_var}.  Please re-enter the {sensitive_var}.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
            elif re.search('(apikey|secretkey)', sensitive_var):
                if not sensitive_var == '':
                    valid = True
            elif 'bind' in sensitive_var:
                jsonVars = jsonData['components']['schemas']['iam.LdapBaseProperties']['allOf'][1]['properties']
                minLength = 1
                maxLength = 254
                rePattern = jsonVars['Password']['pattern']
                varName = 'SNMP Community'
                valid = validating.length_and_regex_sensitive(rePattern, varName, secure_value, minLength, maxLength)
            elif 'community' in sensitive_var:
                jsonVars = jsonData['components']['schemas']['snmp.Policy']['allOf'][1]['properties']
                minLength = 1
                maxLength = jsonVars['TrapCommunity']['maxLength']
                rePattern = '^[\\S]+$'
                varName = 'SNMP Community'
                valid = validating.length_and_regex_sensitive(rePattern, varName, secure_value, minLength, maxLength)
            elif 'ipmi_key' in sensitive_var:
                jsonVars = jsonData['components']['schemas']['ipmioverlan.Policy']['allOf'][1]['properties']
                minLength = 2
                maxLength = jsonVars['EncryptionKey']['maxLength']
                rePattern = jsonVars['EncryptionKey']['pattern']
                varName = 'IPMI Encryption Key'
                valid = validating.length_and_regex_sensitive(rePattern, varName, secure_value, minLength, maxLength)
            elif 'iscsi_boot' in sensitive_var:
                jsonVars = jsonData['components']['schemas']['vnic.IscsiAuthProfile']['allOf'][1]['properties']
                minLength = 12
                maxLength = 16
                rePattern = jsonVars['Password']['pattern']
                varName = 'iSCSI Boot Password'
                valid = validating.length_and_regex_sensitive(rePattern, varName, secure_value, minLength, maxLength)
            elif 'local' in sensitive_var:
                jsonVars = jsonData['components']['schemas']['iam.EndPointUserRole']['allOf'][1]['properties']
                minLength = jsonVars['Password']['minLength']
                maxLength = jsonVars['Password']['maxLength']
                rePattern = jsonVars['Password']['pattern']
                varName = 'Local User Password'
                valid = validating.length_and_regex_sensitive(rePattern, varName, secure_value, minLength, maxLength)
            elif 'secure_passphrase' in sensitive_var:
                jsonVars = jsonData['components']['schemas']['memory.PersistentMemoryLocalSecurity']['allOf'][1]['properties']
                minLength = jsonVars['SecurePassphrase']['minLength']
                maxLength = jsonVars['SecurePassphrase']['maxLength']
                rePattern = jsonVars['SecurePassphrase']['pattern']
                varName = 'Persistent Memory Secure Passphrase'
                valid = validating.length_and_regex_sensitive(rePattern, varName, secure_value, minLength, maxLength)
            elif 'snmp' in sensitive_var:
                jsonVars = jsonData['components']['schemas']['snmp.Policy']['allOf'][1]['properties']
                minLength = 1
                maxLength = jsonVars['TrapCommunity']['maxLength']
                rePattern = '^[\\S]+$'
                if 'auth' in sensitive_var:
                    varName = 'SNMP Authorization Password'
                else:
                    varName = 'SNMP Privacy Password'
                valid = validating.length_and_regex_sensitive(rePattern, varName, secure_value, minLength, maxLength)
            elif 'vmedia' in sensitive_var:
                jsonVars = jsonData['components']['schemas']['vmedia.Mapping']['allOf'][1]['properties']
                minLength = 1
                maxLength = jsonVars['Password']['maxLength']
                rePattern = '^[\\S]+$'
                varName = 'vMedia Mapping Password'
                valid = validating.length_and_regex_sensitive(rePattern, varName, secure_value, minLength, maxLength)

        # Add the Variable to the Environment
        os.environ[sensitive_var] = '%s' % (secure_value)
        var_value = secure_value

    else:
        # Add the Variable to the Environment
        if templateVars.get('Multi_Line_Input'):
            var_value = os.environ.get(sensitive_var)
            var_value = var_value.replace('\n', '\\n')
        else:
            var_value = os.environ.get(sensitive_var)

    return var_value

def snmp_trap_servers(jsonData, inner_loop_count, snmp_user_list, **templateVars):
    trap_servers = []
    valid_traps = False
    while valid_traps == False:
        templateVars["multi_select"] = False
        jsonVars = jsonData['components']['schemas']['snmp.Trap']['allOf'][1]['properties']
        if len(snmp_user_list) == 0:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  There are no valid SNMP Users so Trap Destinations can only be set to SNMPv2.')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            snmp_version = 'V2'
        else:
            templateVars["var_description"] = jsonVars['Version']['description']
            templateVars["jsonVars"] = sorted(jsonVars['Version']['enum'])
            templateVars["defaultVar"] = jsonVars['Version']['default']
            templateVars["varType"] = 'SNMP Version'
            snmp_version = variablesFromAPI(**templateVars)

        if snmp_version == 'V2':
            valid = False
            while valid == False:
                community_string = stdiomask.getpass(f'What is the Community String for the Destination? ')
                if not community_string == '':
                    valid = validating.snmp_string('SNMP Community String', community_string)
                else:
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  Error!! Invalid Value.  Please Re-enter the SNMP Community String.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
            TF_VAR = 'TF_VAR_snmp_community_string_%s' % (inner_loop_count)
            os.environ[TF_VAR] = '%s' % (community_string)
            community_string = inner_loop_count

        if snmp_version == 'V3':
            templateVars["multi_select"] = False
            templateVars["var_description"] = '    Please Select the SNMP User to assign to this Destination:\n'
            templateVars["var_type"] = 'SNMP User'
            snmp_users = []
            for item in snmp_user_list:
                snmp_users.append(item['name'])
            snmp_user = vars_from_list(snmp_users, **templateVars)
            snmp_user = snmp_user[0]

        if snmp_version == 'V2':
            templateVars["var_description"] = jsonVars['Type']['description']
            templateVars["jsonVars"] = sorted(jsonVars['Type']['enum'])
            templateVars["defaultVar"] = jsonVars['Type']['default']
            templateVars["varType"] = 'SNMP Trap Type'
            trap_type = variablesFromAPI(**templateVars)
        else:
            trap_type = 'Trap'

        valid = False
        while valid == False:
            destination_address = input(f'What is the SNMP Trap Destination Hostname/Address? ')
            if not destination_address == '':
                if re.search(r'^[0-9a-fA-F]+[:]+[0-9a-fA-F]$', destination_address) or \
                    re.search(r'^(\d{1,3}\.){3}\d{1,3}$', destination_address):
                    valid = validating.ip_address('SNMP Trap Destination', destination_address)
                else:
                    valid = validating.dns_name('SNMP Trap Destination', destination_address)
            else:
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'  Error!! Invalid Value.  Please Re-enter the SNMP Trap Destination Hostname/Address.')
                print(f'\n-------------------------------------------------------------------------------------------\n')

        valid = False
        while valid == False:
            port = input(f'Enter the Port to Assign to this Destination.  Valid Range is 1-65535.  [162]: ')
            if port == '':
                port = 162
            if re.search(r'[0-9]{1,4}', str(port)):
                valid = validating.snmp_port('SNMP Port', port, 1, 65535)
            else:
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'  Invalid Entry!  Please Enter a valid Port in the range of 1-65535.')
                print(f'\n-------------------------------------------------------------------------------------------\n')

        if snmp_version == 'V3':
            snmp_destination = {
                'destination_address':destination_address,
                'enabled':True,
                'port':port,
                'trap_type':trap_type,
                'user':snmp_user,
                'version':snmp_version
            }
        else:
            snmp_destination = {
                'community':community_string,
                'destination_address':destination_address,
                'enabled':True,
                'port':port,
                'trap_type':trap_type,
                'version':snmp_version
            }

        print(f'\n-------------------------------------------------------------------------------------------\n')
        if snmp_version == 'V2':
            print(f'   community_string    = "Sensitive"')
        print(f'   destination_address = "{destination_address}"')
        print(f'   enable              = True')
        print(f'   trap_type           = "{trap_type}"')
        print(f'   snmp_version        = "{snmp_version}"')
        if snmp_version == 'V3':
            print(f'   user                = "{snmp_user}"')
        print(f'\n-------------------------------------------------------------------------------------------\n')
        valid_confirm = False
        while valid_confirm == False:
            confirm_v = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
            if confirm_v == 'Y' or confirm_v == '':
                trap_servers.append(snmp_destination)
                valid_exit = False
                while valid_exit == False:
                    loop_exit = input(f'Would You like to Configure another SNMP Trap Destination?  Enter "Y" or "N" [N]: ')
                    if loop_exit == 'Y':
                        inner_loop_count += 1
                        valid_confirm = True
                        valid_exit = True
                    elif loop_exit == 'N' or loop_exit == '':
                        snmp_loop = True
                        valid_confirm = True
                        valid_exit = True
                        valid_traps = True
                    else:
                        print(f'\n------------------------------------------------------\n')
                        print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                        print(f'\n------------------------------------------------------\n')

            elif confirm_v == 'N':
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'  Starting Remote Host Configuration Over.')
                print(f'\n-------------------------------------------------------------------------------------------\n')
                valid_confirm = True
            else:
                print(f'\n------------------------------------------------------\n')
                print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                print(f'\n------------------------------------------------------\n')

    return trap_servers,snmp_loop

def snmp_users(jsonData, inner_loop_count, **templateVars):
    snmp_user_list = []
    valid_users = False
    while valid_users == False:
        templateVars["multi_select"] = False
        jsonVars = jsonData['components']['schemas']['snmp.User']['allOf'][1]['properties']

        templateVars["Description"] = jsonVars['Name']['description']
        templateVars["varDefault"] = 'admin'
        templateVars["varInput"] = 'What is the SNMPv3 Username:'
        templateVars["varName"] = 'SNMP User'
        templateVars["varRegex"] = '^([a-zA-Z]+[a-zA-Z0-9\\-\\_\\.\\@]+)$'
        templateVars["minLength"] = jsonVars['Name']['minLength']
        templateVars["maxLength"] = jsonVars['Name']['maxLength']
        snmp_user = varStringLoop(**templateVars)

        templateVars["var_description"] = jsonVars['SecurityLevel']['description']
        templateVars["jsonVars"] = sorted(jsonVars['SecurityLevel']['enum'])
        templateVars["defaultVar"] = jsonVars['SecurityLevel']['default']
        templateVars["varType"] = 'SNMP Security Level'
        security_level = variablesFromAPI(**templateVars)

        if security_level == 'AuthNoPriv' or security_level == 'AuthPriv':
            templateVars["var_description"] = jsonVars['AuthType']['description']
            templateVars["jsonVars"] = sorted(jsonVars['AuthType']['enum'])
            templateVars["defaultVar"] = 'SHA'
            templateVars["popList"] = ['NA', 'SHA-224', 'SHA-256', 'SHA-384', 'SHA-512']
            templateVars["varType"] = 'SNMP Auth Type'
            auth_type = variablesFromAPI(**templateVars)

        if security_level == 'AuthNoPriv' or security_level == 'AuthPriv':
            valid = False
            while valid == False:
                password1 = stdiomask.getpass(f'What is the authorization password for {snmp_user}? ')
                password2 = stdiomask.getpass(f'Please re-enter the authorization password for {snmp_user}? ')
                if not password1 == '':
                    if password1 == password2:
                        TF_VAR = 'TF_VAR_snmp_auth_password_%s' % (inner_loop_count)
                        os.environ[TF_VAR] = '%s' % (password1)
                        auth_password = inner_loop_count
                        valid = validating.snmp_string(f"{snmp_user}'s Authorization Password", password1)
                    else:
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        print(f'  Error!! The Passwords did not match.  Please Re-enter the password for {snmp_user}.')
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                else:
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  Error!! Invalid Value.  Please Re-enter the password for {snmp_user}.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')

        if security_level == 'AuthPriv':
            templateVars["var_description"] = jsonVars['PrivacyType']['description']
            templateVars["jsonVars"] = sorted(jsonVars['PrivacyType']['enum'])
            templateVars["defaultVar"] = 'AES'
            templateVars["popList"] = ['NA']
            templateVars["varType"] = 'SNMP Auth Type'
            privacy_type = variablesFromAPI(**templateVars)

            valid = False
            while valid == False:
                password1 = stdiomask.getpass(f'What is the privacy password for {snmp_user}? ')
                password2 = stdiomask.getpass(f'Please re-enter the privacy password for {snmp_user}? ')
                if not password1 == '':
                    if password1 == password2:
                        TF_VAR = 'TF_VAR_snmp_privacy_password_%s' % (inner_loop_count)
                        os.environ[TF_VAR] = '%s' % (password1)
                        privacy_password = inner_loop_count
                        valid = validating.snmp_string(f"{snmp_user}'s Privacy Password", password1)
                    else:
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        print(f'  Error!! The Passwords did not match.  Please Re-enter the password for {snmp_user}.')
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                else:
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  Error!! Invalid Value.  Please Re-enter the password for {snmp_user}.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')

        if security_level == 'AuthPriv':
            snmp_user = {
                'auth_password':auth_password,
                'auth_type':auth_type,
                'name':snmp_user,
                'privacy_password':privacy_password,
                'privacy_type':privacy_type,
                'security_level':security_level
            }
        elif security_level == 'AuthNoPriv':
            snmp_user = {
                'auth_password':auth_password,
                'auth_type':auth_type,
                'name':snmp_user,
                'security_level':security_level
            }

        print(f'\n-------------------------------------------------------------------------------------------\n')
        print(f'   auth_password    = "Sensitive"')
        print(f'   auth_type        = "{auth_type}"')
        if security_level == 'AuthPriv':
            print(f'   privacy_password = "Sensitive"')
            print(f'   privacy_type     = "{privacy_type}"')
        print(f'   security_level   = "{security_level}"')
        print(f'   snmp_user        = "{snmp_user["name"]}"')
        print(f'\n-------------------------------------------------------------------------------------------\n')
        valid_confirm = False
        while valid_confirm == False:
            confirm_v = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
            if confirm_v == 'Y' or confirm_v == '':
                snmp_user_list.append(snmp_user)
                valid_exit = False
                while valid_exit == False:
                    loop_exit = input(f'Would You like to Configure another SNMP User?  Enter "Y" or "N" [N]: ')
                    if loop_exit == 'Y':
                        inner_loop_count += 1
                        valid_confirm = True
                        valid_exit = True
                    elif loop_exit == 'N' or loop_exit == '':
                        snmp_loop = True
                        valid_confirm = True
                        valid_exit = True
                        valid_users = True
                    else:
                        print(f'\n------------------------------------------------------\n')
                        print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                        print(f'\n------------------------------------------------------\n')

            elif confirm_v == 'N':
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'  Starting SNMP User Configuration Over.')
                print(f'\n-------------------------------------------------------------------------------------------\n')
                valid_confirm = True
            else:
                print(f'\n------------------------------------------------------\n')
                print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                print(f'\n------------------------------------------------------\n')
    return snmp_user_list,snmp_loop

def syslog_servers(jsonData, **templateVars):
    remote_logging = {}
    syslog_count = 1
    syslog_loop = False
    while syslog_loop == False:
        valid = False
        while valid == False:
            hostname = input(f'Enter the Hostname/IP Address of the Remote Server: ')
            if re.search(r'[a-zA-Z]+', hostname):
                valid = validating.dns_name('Remote Logging Server', hostname)
            else:
                valid = validating.ip_address('Remote Logging Server', hostname)

        jsonVars = jsonData['components']['schemas']['syslog.RemoteClientBase']['allOf'][1]['properties']
        templateVars["var_description"] = jsonVars['MinSeverity']['description']
        templateVars["jsonVars"] = sorted(jsonVars['MinSeverity']['enum'])
        templateVars["defaultVar"] = jsonVars['MinSeverity']['default']
        templateVars["varType"] = 'Syslog Remote Minimum Severity'
        min_severity = variablesFromAPI(**templateVars)

        templateVars["var_description"] = jsonVars['Protocol']['description']
        templateVars["jsonVars"] = sorted(jsonVars['Protocol']['enum'])
        templateVars["defaultVar"] = jsonVars['Protocol']['default']
        templateVars["varType"] = 'Syslog Protocol'
        templateVars["protocol"] = variablesFromAPI(**templateVars)

        valid = False
        while valid == False:
            port = input(f'Enter the Port to Assign to this Policy.  Valid Range is 1-65535.  [514]: ')
            if port == '':
                port = 514
            if re.search(r'[0-9]{1,4}', str(port)):
                valid = validating.number_in_range('Port', port, 1, 65535)
            else:
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'  Invalid Entry!  Please Enter a valid Port in the range of 1-65535.')
                print(f'\n-------------------------------------------------------------------------------------------\n')

        remote_host = {
            'enable':True,
            'hostname':hostname,
            'min_severity':min_severity,
            'port':port,
            'protocol':templateVars["protocol"]
        }
        print(f'\n-------------------------------------------------------------------------------------------\n')
        print(f'   hostname     = "{hostname}"')
        print(f'   min_severity = "{min_severity}"')
        print(f'   port         = {port}')
        print(f'   protocol     = "{templateVars["protocol"]}"')
        print(f'\n-------------------------------------------------------------------------------------------\n')
        valid_confirm = False
        while valid_confirm == False:
            confirm_host = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
            if confirm_host == 'Y' or confirm_host == '':
                if syslog_count == 1:
                    remote_logging.update({'server1':remote_host})
                elif syslog_count == 2:
                    remote_logging.update({'server2':remote_host})
                    syslog_loop = True
                    valid_confirm = True
                if syslog_count == 1:
                    valid_exit = False
                    while valid_exit == False:
                        remote_exit = input(f'Would You like to Configure another Remote Host?  Enter "Y" or "N" [Y]: ')
                        if remote_exit == 'Y' or remote_exit == '':
                            syslog_count += 1
                            valid_confirm = True
                            valid_exit = True
                        elif remote_exit == 'N':
                            remote_host = {
                                'enable':False,
                                'hostname':'0.0.0.0',
                                'min_severity':'warning',
                                'port':514,
                                'protocol':'udp'
                            }
                            remote_logging.update({'server2':remote_host})
                            syslog_loop = True
                            valid_confirm = True
                            valid_exit = True
                        else:
                            print(f'\n------------------------------------------------------\n')
                            print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                            print(f'\n------------------------------------------------------\n')

            elif confirm_host == 'N':
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'  Starting Syslog Server Configuration Over.')
                print(f'\n-------------------------------------------------------------------------------------------\n')
                valid_confirm = True
            else:
                print(f'\n------------------------------------------------------\n')
                print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                print(f'\n------------------------------------------------------\n')

    return remote_logging

def ucs_domain_serials():
    print(f'\n-------------------------------------------------------------------------------------------\n')
    print(f'  Note: If you do not have the Serial Number at this time you can manually add it to the:')
    print(f'        - ucs_domain_profiles/ucs_domain_profiles.auto.tfvars file later.')
    print(f'\n-------------------------------------------------------------------------------------------\n')
    valid = False
    while valid == False:
        templateVars = {}
        fabrics = ['A','B']
        for x in fabrics:
            templateVars[f"serial_{x}"] = input(f'What is the Serial Number of Fabric {x}? [press enter to skip]: ')
            if templateVars[f"serial_{x}"] == '':
                valid = True
            elif re.fullmatch(r'^[A-Z]{3}[2-3][\d]([0][1-9]|[1-4][0-9]|[5][1-3])[\dA-Z]{4}$', templateVars[f"serial_{x}"]):
                valid = True
            else:
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'  Error!! Invalid Serial Number.  "templateVars["serial_{x}"]" is not a valid serial.')
                print(f'\n-------------------------------------------------------------------------------------------\n')
    serial_a = templateVars["serial_A"]
    serial_b = templateVars["serial_B"]
    return serial_a,serial_b

def validate_vlan_in_policy(vlan_policy_list, vlan_id):
    valid = False
    vlan_count = 0
    for vlan in vlan_policy_list:
        if int(vlan) == int(vlan_id):
            vlan_count = 1
            continue
    if vlan_count == 1:
        valid = True
    else:
        print(f'\n-------------------------------------------------------------------------------------------\n')
        print(f'  VLAN {vlan_id} not found in the VLAN Policy List.  Please us a VLAN from the list below:')
        print(f'  {vlan_policy_list}')
        print(f'\n-------------------------------------------------------------------------------------------\n')
    return valid

def variablesFromAPI(**templateVars):
    valid = False
    while valid == False:
        json_vars = templateVars["jsonVars"]
        if 'popList' in templateVars:
            if len(templateVars["popList"]) > 0:
                for x in templateVars["popList"]:
                    varsCount = len(json_vars)
                    for r in range(0, varsCount):
                        if json_vars[r] == x:
                            json_vars.pop(r)
                            break
        print(f'\n-------------------------------------------------------------------------------------------\n')
        newDescr = templateVars["var_description"]
        if '\n' in newDescr:
            newDescr = newDescr.split('\n')
            for line in newDescr:
                if '*' in line:
                    print(fill(f'{line}',width=88, subsequent_indent='    '))
                else:
                    print(fill(f'{line}',88))
        else:
            print(fill(f'{templateVars["var_description"]}',88))
        print(f'\n    Select an Option Below:')
        for index, value in enumerate(json_vars):
            index += 1
            if value == templateVars["defaultVar"]:
                defaultIndex = index
            if index < 10:
                print(f'     {index}. {value}')
            else:
                print(f'    {index}. {value}')
        print(f'\n-------------------------------------------------------------------------------------------\n')
        if templateVars["multi_select"] == True:
            if not templateVars["defaultVar"] == '':
                var_selection = input(f'Please Enter the Option Number(s) to Select for {templateVars["varType"]}.  [{defaultIndex}]: ')
            else:
                var_selection = input(f'Please Enter the Option Number(s) to Select for {templateVars["varType"]}: ')
        else:
            if not templateVars["defaultVar"] == '':
                var_selection = input(f'Please Enter the Option Number to Select for {templateVars["varType"]}.  [{defaultIndex}]: ')
            else:
                var_selection = input(f'Please Enter the Option Number to Select for {templateVars["varType"]}: ')
        if not templateVars["defaultVar"] == '' and var_selection == '':
            var_selection = defaultIndex

        if templateVars["multi_select"] == False and re.search(r'^[0-9]+$', str(var_selection)):
            for index, value in enumerate(json_vars):
                index += 1
                if int(var_selection) == index:
                    selection = value
                    valid = True
        elif templateVars["multi_select"] == True and re.search(r'(^[0-9]+$|^[0-9\-,]+[0-9]$)', str(var_selection)):
            var_list = vlan_list_full(var_selection)
            var_length = int(len(var_list))
            var_count = 0
            selection = []
            for index, value in enumerate(json_vars):
                index += 1
                for vars in var_list:
                    if int(vars) == index:
                        var_count += 1
                        selection.append(value)
            if var_count == var_length:
                valid = True
            else:
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'  The list of Vars {var_list} did not match the available list.')
                print(f'\n-------------------------------------------------------------------------------------------\n')
        else:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  Error!! Invalid Selection.  Please Select a valid Option from the List.')
            print(f'\n-------------------------------------------------------------------------------------------\n')
    return selection

def varBoolLoop(**templateVars):
    print(f'\n-------------------------------------------------------------------------------------------\n')
    newDescr = templateVars["Description"]
    if '\n' in newDescr:
        newDescr = newDescr.split('\n')
        for line in newDescr:
            if '*' in line:
                print(fill(f'{line}',width=88, subsequent_indent='    '))
            else:
                print(fill(f'{line}',88))
    else:
        print(fill(f'{templateVars["Description"]}',88))
    print(f'\n-------------------------------------------------------------------------------------------\n')
    valid = False
    while valid == False:
        varValue = input(f'{templateVars["varInput"]}  [{templateVars["varDefault"]}]: ')
        if varValue == '':
            if templateVars["varDefault"] == 'Y':
                varValue = True
            elif templateVars["varDefault"] == 'N':
                varValue = False
            valid = True
        elif varValue == 'N':
            varValue = False
            valid = True
        elif varValue == 'Y':
            varValue = True
            valid = True
        else:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'   {templateVars["varName"]} value of "{varValue}" is Invalid!!! Please enter "Y" or "N".')
            print(f'\n-------------------------------------------------------------------------------------------\n')
    return varValue

def varNumberLoop(**templateVars):
    maxNum = templateVars["maxNum"]
    minNum = templateVars["minNum"]
    varName = templateVars["varName"]

    print(f'\n-------------------------------------------------------------------------------------------\n')
    newDescr = templateVars["Description"]
    if '\n' in newDescr:
        newDescr = newDescr.split('\n')
        for line in newDescr:
            if '*' in line:
                print(fill(f'{line}',width=88, subsequent_indent='    '))
            else:
                print(fill(f'{line}',88))
    else:
        print(fill(f'{templateVars["Description"]}',88))
    print(f'\n-------------------------------------------------------------------------------------------\n')
    valid = False
    while valid == False:
        varValue = input(f'{templateVars["varInput"]}  [{templateVars["varDefault"]}]: ')
        if varValue == '':
            varValue = templateVars["varDefault"]
        if re.fullmatch(r'^[0-9]+$', str(varValue)):
            valid = validating.number_in_range(varName, varValue, minNum, maxNum)
        else:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'   {varName} value of "{varValue}" is Invalid!!! ')
            print(f'   Valid range is {minNum} to {maxNum}.')
            print(f'\n-------------------------------------------------------------------------------------------\n')
    return varValue

def varSensitiveStringLoop(**templateVars):
    maxLength = templateVars["maxLength"]
    minLength = templateVars["minLength"]
    varName = templateVars["varName"]
    varRegex = templateVars["varRegex"]

    print(f'\n-------------------------------------------------------------------------------------------\n')
    newDescr = templateVars["Description"]
    if '\n' in newDescr:
        newDescr = newDescr.split('\n')
        for line in newDescr:
            if '*' in line:
                print(fill(f'{line}',width=88, subsequent_indent='    '))
            else:
                print(fill(f'{line}',88))
    else:
        print(fill(f'{templateVars["Description"]}',88))
    print(f'\n-------------------------------------------------------------------------------------------\n')
    valid = False
    while valid == False:
        varValue = stdiomask.getpass(f'{templateVars["varInput"]} ')
        if not varValue == '':
            valid = validating.length_and_regex_sensitive(varRegex, varName, varValue, minLength, maxLength)
        else:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'   {varName} value is Invalid!!! ')
            print(f'\n-------------------------------------------------------------------------------------------\n')
    return varValue

def varStringLoop(**templateVars):
    maxLength = templateVars["maxLength"]
    minLength = templateVars["minLength"]
    varName = templateVars["varName"]
    varRegex = templateVars["varRegex"]

    print(f'\n-------------------------------------------------------------------------------------------\n')
    newDescr = templateVars["Description"]
    if '\n' in newDescr:
        newDescr = newDescr.split('\n')
        for line in newDescr:
            if '*' in line:
                print(fill(f'{line}',width=88, subsequent_indent='    '))
            else:
                print(fill(f'{line}',88))
    else:
        print(fill(f'{templateVars["Description"]}',88))
    print(f'\n-------------------------------------------------------------------------------------------\n')
    valid = False
    while valid == False:
        varValue = input(f'{templateVars["varInput"]} ')
        if 'press enter to skip' in templateVars["varInput"] and varValue == '':
            valid = True
        elif not templateVars["varDefault"] == '' and varValue == '':
            varValue = templateVars["varDefault"]
            valid = True
        elif not varValue == '':
            valid = validating.length_and_regex(varRegex, varName, varValue, minLength, maxLength)
        else:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'   {varName} value of "{varValue}" is Invalid!!! ')
            print(f'\n-------------------------------------------------------------------------------------------\n')
    return varValue

def vars_from_list(var_options, **templateVars):
    selection = []
    selection_count = 0
    valid = False
    while valid == False:
        print(f'\n-------------------------------------------------------------------------------------------\n')
        print(f'{templateVars["var_description"]}')
        for index, value in enumerate(var_options):
            index += 1
            if index < 10:
                print(f'     {index}. {value}')
            else:
                print(f'    {index}. {value}')
        print(f'\n-------------------------------------------------------------------------------------------\n')
        exit_answer = False
        while exit_answer == False:
            var_selection = input(f'Please Enter the Option Number to Select for {templateVars["var_type"]}: ')
            if not var_selection == '':
                if re.search(r'[0-9]+', str(var_selection)):
                    xcount = 1
                    for index, value in enumerate(var_options):
                        index += 1
                        if int(var_selection) == index:
                            selection.append(value)
                            xcount = 0
                    if xcount == 0:
                        if selection_count % 2 == 0 and templateVars["multi_select"] == True:
                            answer_finished = input(f'Would you like to add another port to the {templateVars["port_type"]}?  Enter "Y" or "N" [Y]: ')
                        elif templateVars["multi_select"] == True:
                            answer_finished = input(f'Would you like to add another port to the {templateVars["port_type"]}?  Enter "Y" or "N" [N]: ')
                        elif templateVars["multi_select"] == False:
                            answer_finished = 'N'
                        if (selection_count % 2 == 0 and answer_finished == '') or answer_finished == 'Y':
                            exit_answer = True
                            selection_count += 1
                        elif answer_finished == '' or answer_finished == 'N':
                            exit_answer = True
                            valid = True
                        elif templateVars["multi_select"] == False:
                            exit_answer = True
                            valid = True
                        else:
                            print(f'\n------------------------------------------------------\n')
                            print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                            print(f'\n------------------------------------------------------\n')
                    else:
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        print(f'  Error!! Invalid Selection.  Please select a valid option from the List.')
                        print(f'\n-------------------------------------------------------------------------------------------\n')

                else:
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  Error!! Invalid Selection.  Please Select a valid Option from the List.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
            else:
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'  Error!! Invalid Selection.  Please Select a valid Option from the List.')
                print(f'\n-------------------------------------------------------------------------------------------\n')
    return selection

def vlan_list_full(vlan_list):
    full_vlan_list = []
    if re.search(r',', str(vlan_list)):
        vlist = vlan_list.split(',')
        for v in vlist:
            if re.fullmatch('^\\d{1,4}\\-\\d{1,4}$', v):
                a,b = v.split('-')
                a = int(a)
                b = int(b)
                vrange = range(a,b+1)
                for vl in vrange:
                    full_vlan_list.append(vl)
            elif re.fullmatch('^\\d{1,4}$', v):
                full_vlan_list.append(v)
    elif re.search('\\-', str(vlan_list)):
        a,b = vlan_list.split('-')
        a = int(a)
        b = int(b)
        vrange = range(a,b+1)
        for v in vrange:
            full_vlan_list.append(v)
    else:
        full_vlan_list.append(vlan_list)
    return full_vlan_list

def vlan_pool():
    valid = False
    while valid == False:
        print(f'\n-------------------------------------------------------------------------------------------\n')
        print(f'  The allowed vlan list can be in the format of:')
        print(f'     5 - Single VLAN')
        print(f'     1-10 - Range of VLANs')
        print(f'     1,2,3,4,5,11,12,13,14,15 - List of VLANs')
        print(f'     1-10,20-30 - Ranges and Lists of VLANs')
        print(f'\n-------------------------------------------------------------------------------------------\n')
        VlanList = input('Enter the VLAN or List of VLANs to assign to the Domain VLAN Pool: ')
        if not VlanList == '':
            vlanListExpanded = vlan_list_full(VlanList)
            valid_vlan = True
            for vlan in vlanListExpanded:
                valid_vlan = validating.number_in_range('VLAN ID', vlan, 1, 4094)
                if valid_vlan == False:
                    continue
            if valid_vlan == False:
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'  Error with VLAN(s) assignment!!! VLAN List: "{VlanList}" is not Valid.')
                print(f'  The allowed vlan list can be in the format of:')
                print(f'     5 - Single VLAN')
                print(f'     1-10 - Range of VLANs')
                print(f'     1,2,3,4,5,11,12,13,14,15 - List of VLANs')
                print(f'     1-10,20-30 - Ranges and Lists of VLANs')
                print(f'\n-------------------------------------------------------------------------------------------\n')
            else:
                valid = True
        else:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  The allowed vlan list can be in the format of:')
            print(f'     5 - Single VLAN')
            print(f'     1-10 - Range of VLANs')
            print(f'     1,2,3,4,5,11,12,13,14,15 - List of VLANs')
            print(f'     1-10,20-30 - Ranges and Lists of VLANs')
            print(f'\n-------------------------------------------------------------------------------------------\n')
    
    return VlanList,vlanListExpanded

def write_to_template(self, **templateVars):
    # Define the Template Source
    template = self.templateEnv.get_template(templateVars["template_file"])

    # Process the template
    dest_dir = '%s' % (self.type)
    dest_file = '%s.auto.tfvars' % (templateVars["template_type"])
    if templateVars["initial_write"] == True:
        write_method = 'w'
    else:
        write_method = 'a'
    process_method(write_method, dest_dir, dest_file, template, **templateVars)
