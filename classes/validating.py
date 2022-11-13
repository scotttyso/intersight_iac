#!/usr/bin/env python3

import ipaddress
import phonenumbers
import re
import string
import validators

# Errors
def subnet_check(**kwargs):
    ip_version = kwargs['ip_version']
    if ip_version == 'v4': prefix = kwargs['subnetMask']
    else: prefix = kwargs['Prefix']
    gateway = kwargs['defaultGateway']
    pool_from = kwargs['pool_from']
    pool_to = kwargs['pool_to']
    subnetList = list(ipaddress.ip_network(f"{gateway}/{prefix}", strict=False).hosts())
    if not pool_from in subnetList:
        print(f'\n{"-"*91}\n')
        print(f'   Error!!!  {pool_from} is not in network {gateway}/{prefix}:')
        print(f'   Exiting....')
        print(f'\n{"-"*91}\n')
        exit()
    if not pool_from in subnetList:
        print(f'\n{"-"*91}\n')
        print(f'   Error!!!  {pool_to} is not in network {gateway}/{prefix}:')
        print(f'   Exiting....')
        print(f'\n{"-"*91}\n')
        exit()

# Validations
def description(varName, varValue, minLength, maxLength):
    if not (re.search(r'^[a-zA-Z0-9\\!#$%()*,-./:;@ _{|}~?&+]+$',  varValue) and \
    validators.length(str(varValue), min=int(minLength), max=int(maxLength))):
        print(f'\n-----------------------------------------------------------------------------\n')
        print(f'   The description is an invalid Value... It failed one of the complexity tests:')
        print(f'    - Min Length {minLength}')
        print(f'    - Max Length {maxLength}')
        print('    - Regex [a-zA-Z0-9\\!#$%()*,-./:;@ _{|}~?&+]+')
        print(f'\n-----------------------------------------------------------------------------\n')
        return False
    else:
        return True

def days(row_num, ws, var, var_value):
    if not re.search('^(every-day|even-day|odd-day|Sunday|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday)$', var_value):
        print(f'\n---------------------------------------------------------------------------------------\n')
        print(f'   Error on Worksheet {ws.title}, Row {row_num} {var}, {var_value} Valid Values are:')
        print(f'    - every-day')
        print(f'    - even-day')
        print(f'    - odd-day')
        print(f'    - Sunday')
        print(f'    - Sunday')
        print(f'    - Monday')
        print(f'    - Tuesday')
        print(f'    - Wednesday')
        print(f'    - Thursday')
        print(f'    - Friday')
        print(f'    - Saturday')
        print(f'   Exiting....')
        print(f'\n---------------------------------------------------------------------------------------\n')
        exit()

def dscp(row_num, ws, var, var_value):
    if not re.search('^(AF[1-4][1-3]|CS[0-7]|EF|VA|unspecified)$', var_value):
        print(f'\n-----------------------------------------------------------------------------\n')
        print(f'   Error on Worksheet {ws.title}, Row {row_num} {var}. Valid Values are:')
        print(f'   AF11, AF12, AF13, AF21, AF22, AF23, AF31, AF32, AF33, AF41, AF42, AF43,')
        print(f'   CS0, CS1, CS2, CS3, CS4, CS5, CS6, CS7, EF, VA or unspecified.  Exiting....')
        print(f'\n-----------------------------------------------------------------------------\n')
        exit()

def domain(varName, varValue):
    if not validators.domain(varValue):
        print(f'\n-----------------------------------------------------------------------------\n')
        print(f'   Error with {varName}!!!  Invalid Domain {varValue}')
        print(f'   Please Validate the domain and retry.')
        print(f'\n-----------------------------------------------------------------------------\n')
        return False
    else:
        return True

def dns_name(varName, varValue):
    hostname = varValue
    valid_count = 0
    if len(hostname) > 255:
        valid_count =+ 1
    if hostname[-1] == ".":
        hostname = hostname[:-1] # strip exactly one dot from the right, if present
    allowed = re.compile("(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
    if not all(allowed.match(x) for x in hostname.split(".")):
        valid_count =+ 1
    if not valid_count == 0:
        print(f'\n--------------------------------------------------------------------------------\n')
        print(f'   Error with {varName}.  "{varValue}" is not a valid Hostname.')
        print(f'   Confirm that you have entered the DNS Name Correctly.')
        print(f'\n--------------------------------------------------------------------------------\n')
        return False
    else:
        return True

def email(varName, varValue):
    if not validators.email(varValue, whitelist=None):
        print(f'\n-----------------------------------------------------------------------------\n')
        print(f'   Error with {varName}. Email address "{varValue}"')
        print(f'   is invalid.  Please Validate the email and retry.')
        print(f'\n-----------------------------------------------------------------------------\n')
        return False
    else:
        return True

def encryption_key(row_num, ws, var, var_value):
    if not validators.length(str(var_value), min=16, max=32):
        print(f'\n-----------------------------------------------------------------------------\n')
        print(f'   Error on Worksheet {ws.title}, Row {row_num} {var}. The Encryption Key')
        print(f'   Length must be between 16 and 32 characters.  Exiting....')
        print(f'\n-----------------------------------------------------------------------------\n')
        exit()

def error_enforce(row_num, vrf):
    print(f'\n-----------------------------------------------------------------------------\n')
    print(f'   Error on Row {row_num}. VRF {vrf}, Enforcement was not defined in the')
    print(f'   VRF Worksheet.  Exiting....')
    print(f'\n-----------------------------------------------------------------------------\n')
    exit()

def error_enforcement(row_num, epg, ws2, ws3):
    print(f'\n-----------------------------------------------------------------------------\n')
    print(f'   Error on Row {row_num} of Worksheet {ws3}. Enforcement on the EPG {epg}')
    print(f'   is set to enforced but the VRF is unenforced in {ws2}.  Exiting....')
    print(f'\n-----------------------------------------------------------------------------\n')
    exit()

def error_policy_names(row_num, ws, policy_1, policy_2):
    print(f'\n-----------------------------------------------------------------------------\n')
    print(f'   Error on Row {row_num} of Worksheet {ws}. The Policy {policy_1} was ')
    print(f'   not the same as {policy_2}. Exiting....')
    print(f'\n-----------------------------------------------------------------------------\n')
    exit()

def error_int_selector(row_num, ws, int_select):
    print(f'\n-----------------------------------------------------------------------------\n')
    print(f'   Error on Row {row_num} of Worksheet {ws}. Interface Selector {int_select}')
    print(f'   was not found in the terraform state file.  Exiting....')
    print(f'\n-----------------------------------------------------------------------------\n')
    exit()

def error_request(status, text):
    print(f'\n-----------------------------------------------------------------------------\n')
    print(f'   Error in Retreiving Terraform Cloud Organization Workspaces')
    print(f'   Exiting on Error {status} with the following output:')
    print(f'   {text}')
    print(f'\n-----------------------------------------------------------------------------\n')
    exit()

def error_switch(row_num, ws, switch_ipr):
    print(f'\n-----------------------------------------------------------------------------\n')
    print(f'   Error on Row {row_num} of Worksheet {ws}. Interface Profile {switch_ipr}')
    print(f'   was not found in the terraform state file.  Exiting....')
    print(f'\n-----------------------------------------------------------------------------\n')
    exit()

def error_tenant(row_num, tenant, ws1, ws2):
    print(f'\n-----------------------------------------------------------------------------\n')
    print(f'   Error on Row {row_num} of Worksheet {ws2}. Tenant {tenant} was not found')
    print(f'   in the {ws1} Worksheet.  Exiting....')
    print(f'\n-----------------------------------------------------------------------------\n')
    exit()

def error_vlan_to_epg(row_num, vlan, ws):
    print(f'\n-----------------------------------------------------------------------------\n')
    print(f'   Error on Row {row_num}. Did not Find EPG corresponding to VLAN {vlan}')
    print(f'   in Worksheet {ws}.  Exiting....')
    print(f'\n-----------------------------------------------------------------------------\n')
    exit()

def error_vrf(row_num, vrf):
    print(f'\n-----------------------------------------------------------------------------\n')
    print(f'   Error on Row {row_num}. VRF {vrf} was not found in the VRF Worksheet.')
    print(f'   Exiting....')
    print(f'\n-----------------------------------------------------------------------------\n')
    exit()

def filter_ports(row_num, ws, var, var_value):
    valid_count = 0
    if re.match(r'\d', var_value):
        if not validators.between(int(var_value), min=1, max=65535):
            valid_count =+ 1
    elif re.match(r'[a-z]', var_value):
        if not re.search('^(dns|ftpData|http|https|pop3|rtsp|smtp|unspecified)$', var_value):
            valid_count =+ 1
    else:
        valid_count =+ 1
    if not valid_count == 0:
        print(f'\n-----------------------------------------------------------------------------\n')
        print(f'   Error on Worksheet {ws.title} Row {row_num}. {var} {var_value} did not')
        print(f'   match allowed values. {var} can be:')
        print(f'    - dns')
        print(f'    - ftpData')
        print(f'    - http')
        print(f'    - https')
        print(f'    - pop3')
        print(f'    - rtsp')
        print(f'    - smtp')
        print(f'    - unspecified')
        print(f'    - or between 1 and 65535')
        print(f'   Exiting....')
        print(f'\n-----------------------------------------------------------------------------\n')
        exit()

def hostname(row_num, ws, var, var_value):
    if not (re.search('^[a-zA-Z0-9\\-]+$', var_value) and validators.length(var_value, min=1, max=63)):
        print(f'\n-----------------------------------------------------------------------------\n')
        print(f'   Error on Worksheet {ws.title}, Row {row_num} {var}, {var_value} ')
        print(f'   is not a valid Hostname.  Be sure you are not using the FQDN.  Exiting....')
        print(f'\n-----------------------------------------------------------------------------\n')
        exit()

def ip_address(varName, varValue):
    if re.search('/', varValue):
        x = varValue.split('/')
        address = x[0]
    else:
        address = varValue
    valid_count = 0
    if re.search(r'\.', address):
        if not validators.ip_address.ipv4(address):
            valid_count =+ 1
    else:
        if not validators.ip_address.ipv6(address):
            valid_count =+ 1
    if not valid_count == 0 and re.search(r'\.', address):
        print(f'\n-----------------------------------------------------------------------------\n')
        print(f'   Error with {varName}. "{varValue}" is not a valid IPv4 Address.')
        print(f'\n-----------------------------------------------------------------------------\n')
        return False
    elif not valid_count == 0:
        print(f'\n-----------------------------------------------------------------------------\n')
        print(f'   Error with {varName}. "{varValue}" is not a valid IPv6 Address.')
        print(f'\n-----------------------------------------------------------------------------\n')
        return False
    else:
        return True

def ipmi_key_check(varValue):
    valid_count = 0
    varValue = varValue.capitalize()
    if ((varValue < '0' or varValue > '9') and (varValue < 'A' or varValue > 'F')):
        valid_count += 1
    if not validators.length(varValue, min=2, max=40):
        valid_count += 1
    if not len(varValue) % 2 == 0:
        valid_count += 1
    if not valid_count == 0:
        print(f'\n-----------------------------------------------------------------------------\n')
        print(f'   Error with ipmi_key!!  The encryption key should have an even number of ')
        print(f'   hexadecimal characters and not exceed 40 characters.\n')
        print(f'   Valid Hex Characters are:')
        print(f'    - {string.hexdigits}')
        print(f'\n-----------------------------------------------------------------------------\n')
        return False
    else:
        return True

def iqn_prefix(varName, varValue):
    invalid_count = 0
    if not re.fullmatch(r'^iqn\.[0-9]{4}-[0-9]{2}\.([A-Za-z][A-Za-z0-9\-]*[A-Za-z0-9])?)', varValue):
        invalid_count += 1
    if not invalid_count == 0:
        print(f'\n---------------------------------------------------------------------------------------\n')
        print(f'   Error with {varName}! "{varValue}" did not meet one of the following rules:')
        print(f'     - it must start with "iqn".')
        print(f"     - The second octet must be a valid date in the format YYYY-MM.")
        print(f'     - The third and fourth octet must be a valid domain that starts with a letter or ')
        print(f'       number ends with a letter or number and may have a dash in the middle.')
        print(f'\n---------------------------------------------------------------------------------------\n')
        return False
    else:
        return True

def iqn_address(varName, varValue):
    invalid_count = 0
    if not re.fullmatch(r'^(?:iqn\.[0-9]{4}-[0-9]{2}(?:\.[A-Za-z](?:[A-Za-z0-9\-]*[A-Za-z0-9])?)+(?::.*)?|eui\.[0-9A-Fa-f]{16})', varValue):
        invalid_count += 1
    if not invalid_count == 0:
        print(f'\n---------------------------------------------------------------------------------------\n')
        print(f'   Error with {varName}! "{varValue}" did not meet one of the following rules:')
        print(f'     - it must start with "iqn".')
        print(f"     - The second octet must be a valid date in the format YYYY-MM.")
        print(f'     - The third and fourth octet must be a valid domain that starts with a letter or ')
        print(f'       number ends with a letter or number and may have a dash in the middle.')
        print(f'     - it must have a colon to mark the beginning of the prefix.')
        print(f'\n---------------------------------------------------------------------------------------\n')
        return False
    else:
        return True

def length_and_regex(regex_pattern, varName, varValue, minLength, maxLength):
    invalid_count = 0
    if minLength == 0 and maxLength == 0: invalid_count = 0
    else:
        if not validators.length(varValue, min=int(minLength), max=int(maxLength)):
            invalid_count += 1
            print(f'\n--------------------------------------------------------------------------------------\n')
            print(f'   !!! {varName} value "{varValue}" is Invalid!!!')
            print(f'   Length Must be between {minLength} and {maxLength} characters.')
            print(f'\n--------------------------------------------------------------------------------------\n')
    if not re.search(regex_pattern, varValue):
        invalid_count += 1
        print(f'\n--------------------------------------------------------------------------------------\n')
        print(f'   !!! Invalid Characters in {varValue}.  The allowed characters are:')
        print(f'   - "{regex_pattern}"')
        print(f'\n--------------------------------------------------------------------------------------\n')
    if invalid_count == 0:
        return True
    else:
        return False

def length_and_regex_sensitive(regex_pattern, varName, varValue, minLength, maxLength):
    invalid_count = 0
    if not validators.length(varValue, min=int(minLength), max=int(maxLength)):
        invalid_count += 1
        print(f'\n--------------------------------------------------------------------------------------\n')
        print(f'   !!! {varName} is Invalid!!!')
        print(f'   Length Must be between {minLength} and {maxLength} characters.')
        print(f'\n--------------------------------------------------------------------------------------\n')
    if not re.search(regex_pattern, varValue):
        invalid_count += 1
        print(f'\n--------------------------------------------------------------------------------------\n')
        print(f'   !!! Invalid Characters in {varName}.  The allowed characters are:')
        print(f'   - "{regex_pattern}"')
        print(f'\n--------------------------------------------------------------------------------------\n')
    if invalid_count == 0:
        return True
    else:
        return False

def link_level(row_num, ws, var, var_value):
    if not re.search('(_Auto|_NoNeg)$', var_value):
        print(f'\n-----------------------------------------------------------------------------\n')
        print(f'   Error on Worksheet {ws.title}, Row {row_num} {var}, value {var_value}:')
        print(f'   Please Select a valid Link Level from the drop-down menu.  Exiting....')
        print(f'\n-----------------------------------------------------------------------------\n')
        exit()
    if not re.search('^(100M_|1G_|(1|4|5)0G_|25G_|[1-2]00G_|400G_|inherit_)', var_value):
        print(f'\n-----------------------------------------------------------------------------\n')
        print(f'   Error on Worksheet {ws.title}, Row {row_num} {var}, value {var_value}:')
        print(f'   Please Select a valid Link Level from the drop-down menu.  Exiting....')
        print(f'\n-----------------------------------------------------------------------------\n')
        exit()

def log_level(row_num, ws, var, var_value):
    if var == 'Severity' or var == 'Local_Level' or var == 'Minimum_Level':
        if not re.match('(emergencies|alerts|critical|errors|warnings|notifications|information|debugging)', var_value):
            print(f'\n-----------------------------------------------------------------------------\n')
            print(f'   Error on Worksheet {ws.title} Row {row_num}. Logging Level for "{var}"')
            print(f'   with "{var_value}" is not valid.  Logging Levels can be:')
            print(f'   [emergencies|alerts|critical|errors|warnings|notifications|information|debugging]')
            print(f'   Exiting....')
            print(f'\n-----------------------------------------------------------------------------\n')
            exit()
    elif var == 'Console_Level':
        if not re.match('^(emergencies|alerts|critical)$', var_value):
            print(f'\n-----------------------------------------------------------------------------\n')
            print(f'   Error on Worksheet {ws.title} Row {row_num}. Logging Level for "{var}"  with "{var_value}"')
            print(f'   is not valid.  Logging Levels can be: [emergencies|alerts|critical].  Exiting....')
            print(f'\n-----------------------------------------------------------------------------\n')
            exit()

def login_type(row_num, ws, var1, var1_value, var2, var2_value):
    login_type_count = 0
    if var1_value == 'console':
        if not re.fullmatch('^(local|ldap|radius|tacacs|rsa)$', var2_value):
            login_type_count += 1
    elif var1_value == 'default':
        if not re.fullmatch('^(local|ldap|radius|tacacs|rsa|saml)$', var2_value):
            login_type_count += 1
    if not login_type_count == 0:
        print(f'\n-----------------------------------------------------------------------------\n')
        print(f'   Error in Worksheet {ws.title} Row {row_num}.  The Login Domain Type should be')
        print(f'   one of the following:')
        if var1_value == 'console':
            print(f'       [local|ldap|radius|tacacs|rsa]')
        elif var1_value == 'default':
            print(f'       [local|ldap|radius|tacacs|rsa|saml]')
        print(f'   "{var2_value}" did not match one of these types.  Exiting....')
        print(f'\n-----------------------------------------------------------------------------\n')
        exit()

def mac_address(varName, varValue):
    if not validators.mac_address(varValue):
        print(f'\n-----------------------------------------------------------------------------\n')
        print(f'   Error with {varName}. "{varValue}" is not a valid MAC Address.')
        print(f'\n-----------------------------------------------------------------------------\n')
        return False
    else:
        return True

def wwxn_address(varName, varValue):
    if not re.search(r'([0-9A-F]{2}[:-]){7}([0-9A-F]{2})', varValue):
        print(f'\n-----------------------------------------------------------------------------\n')
        print(f'   Error with {varName}. "{varValue}" is not a valid WWxN Address.')
        print(f'\n-----------------------------------------------------------------------------\n')
        return False
    else:
        return True

def match_t(row_num, ws, var, var_value):
    if not re.search('^(All|AtleastOne|AtmostOne|None)$', var_value):
        print(f'\n-----------------------------------------------------------------------------\n')
        print(f'   Error on Worksheet {ws.title}, Row {row_num} {var}. Valid Values are:')
        print(f'   All, AtleastOne, AtmostOne or None.  Exiting....')
        print(f'\n-----------------------------------------------------------------------------\n')
        exit()

def match_current_gw(row_num, current_inb_gwv4, inb_gwv4):
    if not current_inb_gwv4 == inb_gwv4:
        print(f'\n-----------------------------------------------------------------------------\n')
        print(f'   Error on Line {row_num}.  Current inband = "{current_inb_gwv4}" and found')
        print(f'   "{inb_gwv4}".  The Inband Network should be the same on all APICs and Switches.')
        print(f'   A Different Gateway was found.  Exiting....')
        print(f'\n-----------------------------------------------------------------------------\n')
        exit()

def mgmt_domain(row_num, ws, var, var_value):
    if var_value == 'oob':
        var_value = 'oob-default'
    elif var_value == 'inband':
        var_value = 'inb-default'
    else:
        print(f'\n-----------------------------------------------------------------------------\n')
        print(f'   Error on Worksheet {ws.title}, Row {row_num} {var} value {var_value}.')
        print(f'   The Management Domain Should be inband or oob.  Exiting....')
        print(f'\n-----------------------------------------------------------------------------\n')
        exit()
    return var_value

def mgmt_epg(row_num, ws, var, var_value):
    if var_value == 'var_inb':
        var_value = 'in_band'
    elif var_value == 'var_oob':
        var_value = 'out_of_band'
    else:
        print(f'\n-----------------------------------------------------------------------------\n')
        print(f'   Error on Worksheet {ws.title}, Row {row_num} {var} value {var_value}.')
        print(f'   The Management EPG Should be var_inb or var_oob.  Exiting....')
        print(f'\n-----------------------------------------------------------------------------\n')
        exit()
    return var_value

def mgmt_network(row_num, ws, var1, var1_value, var2, var2_value):
    x = var1_value.split('/')
    ip_add = x[0]
    valid_count = 0
    if re.search(r'\.', ip_add):
        mgmt_check_ip = ipaddress.IPv4Interface(var1_value)
        mgmt_network = mgmt_check_ip.network
        if not ipaddress.IPv4Address(var2_value) in ipaddress.IPv4Network(mgmt_network):
            valid_count =+ 1
    else:
        if not validators.ip_address.ipv6(ip_add):
            valid_count =+ 1
    if not valid_count == 0:
        print(f'\n-----------------------------------------------------------------------------\n')
        print(f'   Error on Worksheet {ws.title}, Row {row_num}.  {var1} Network')
        print(f'   does not Match {var2} Network.')
        print(f'   Mgmt IP/Prefix: "{var1_value}"')
        print(f'   Gateway IP: "{var2_value}"')
        print(f'   Exiting....')
        print(f'\n-----------------------------------------------------------------------------\n')
        exit()

def modules(row_num, name, switch_role, modules):
    module_count = 0
    if switch_role == 'leaf' and int(modules) == 1:
        module_count += 1
    elif switch_role == 'leaf':
        print(f'\n-----------------------------------------------------------------------------\n')
        print(f'   Error on Row {row_num}. {name} module count is not valid.')
        print(f'   A Leaf can only have one module.  Exiting....')
        print(f'\n-----------------------------------------------------------------------------\n')
        exit()
    elif switch_role == 'spine' and int(modules) < 17:
        module_count += 1
    elif switch_role == 'spine':
        print(f'\n-----------------------------------------------------------------------------\n')
        print(f'   Error on Row {row_num}. {name} module count is not valid.')
        print(f'   A Spine needs between 1 and 16 modules.  Exiting....')
        print(f'\n-----------------------------------------------------------------------------\n')
        exit()

def name_complexity(row_num, ws, var, var_value):
    login_domain_count = 0
    if not re.fullmatch('^([a-zA-Z0-9\\_]+)$', var_value):
        login_domain_count += 1
    elif not validators.length(var_value, min=1, max=10):
        login_domain_count += 1
    if not login_domain_count == 0:
        print(f'\n-----------------------------------------------------------------------------\n')
        print(f'   Error on Worksheet {ws.title}, Row {row_num}, {var}, {var_value}.  The Value')
        print(f'   must be between 1 and 10 characters.  The only non alphanumeric characters')
        print(f'   allowed is "_"; but it must not start with "_".  "{var_value}" did not')
        print(f'   meet these restrictions.  Exiting....')
        print(f'\n-----------------------------------------------------------------------------\n')
        exit()

def name_rule(varName, varValue, minLength, maxLength):
    if not (re.search(r'^[a-zA-Z0-9_-]+$',  varValue) and validators.length(str(varValue), min=int(minLength), max=int(maxLength))):
        print(f'\n-----------------------------------------------------------------------------\n')
        print(f'   Error with {varName}!!  "{varValue}" failed one of the complexity tests:')
        print(f'    - Min Length {minLength}')
        print(f'    - Max Length {maxLength}')
        print(f'    - Name can only contain letters(a-z,A-Z), numbers(0-9), hyphen(-),')
        print(f'      or an underscore(_)')
        print(f'\n-----------------------------------------------------------------------------\n')
        return False
    else:
        return True

def org_rule(varName, varValue, minLength, maxLength):
    if not (re.search(r'^[a-zA-Z0-9:_-]+$',  varValue) and validators.length(str(varValue), min=int(minLength), max=int(maxLength))):
        print(f'\n-----------------------------------------------------------------------------\n')
        print(f'   Error with {varName}!!  "{varValue}" failed one of the complexity tests:')
        print(f'    - Min Length {minLength}')
        print(f'    - Max Length {maxLength}')
        print(f'    - Name can only contain letters(a-z,A-Z), numbers(0-9), hyphen(-),')
        print(f'      period(.), colon(:), or an underscore(_)')
        print(f'\n-----------------------------------------------------------------------------\n')
        return False
    else:
        return True

def number_in_range(varName, varValue, minNum, maxNum):
    if not validators.between(int(varValue), min=int(minNum), max=int(maxNum)):
        print(f'\n-----------------------------------------------------------------------------\n')
        print(f'   Error with {varName}! "{varValue}".')
        print(f'   Valid values are between {minNum} and {maxNum}.')
        print(f'\n-----------------------------------------------------------------------------\n')
        return False
    else:
        return True

def not_empty(row_num, ws, var, var_value):
    if var_value == None:
        print(f'\n-----------------------------------------------------------------------------\n')
        print(f'   Error on Worksheet {ws.title}, Row {row_num} {var}, {var_value}. This is a  ')
        print(f'   required variable.  Exiting....')
        print(f'\n-----------------------------------------------------------------------------\n')
        exit()

def phone(row_num, ws, var, var_value):
    phone_number = phonenumbers.parse(var_value, None)
    if not phonenumbers.is_possible_number(phone_number):
        print(f'\n-----------------------------------------------------------------------------\n')
        print(f'   Error on Worksheet {ws.title}, Row {row_num} {var}. Phone Number "{phone_number}" ')
        print(f'   is invalid.  Make sure you are including the country code and the full phone number.')
        print(f'   Exiting....')
        print(f'\n-----------------------------------------------------------------------------\n')
        exit()

def policy_type(row_num, ws, var, policy_group):
        print(f'\n-----------------------------------------------------------------------------\n')
        print(f'   Error on Worksheet {ws.title}, Row {row_num} {policy_group}. A required')
        print(f'   policy of type {var} was not found.  Please verify {policy_group} is.')
        print(f'   configured properly.  Exiting....')
        print(f'\n-----------------------------------------------------------------------------\n')
        exit()

def port_count(row_num, name, switch_role, port_count):
    if not re.search('^(16|32|34|36|48|54|60|64|66|102|108)$', port_count):
        print(f'\n-----------------------------------------------------------------------------\n')
        print(f'   Error on Row {row_num}. {name} port count of {port_count} is not valid.')
        print(f'   Valid port counts are 16, 32, 34, 36, 48, 54, 60, 64, 66, 102, 108.  Exiting....')
        print(f'\n-----------------------------------------------------------------------------\n')
        exit()

def qos_priority(row_num, ws, var, var_value):
    if not re.search('^(level[1-6]|unspecified)$', var_value):
        print(f'\n-----------------------------------------------------------------------------\n')
        print(f'   Error on Worksheet {ws.title}, Row {row_num} {var}. Valid Values are:')
        print(f'   level1, level2, level3, level4, level5, level6 or unspecified.  Exiting....')
        print(f'\n-----------------------------------------------------------------------------\n')
        exit()

def sensitive_var(row_num, ws, var, var_value):
    if not re.search('^(sensitive_var[1-7])$', var_value):
        print(f'\n-----------------------------------------------------------------------------\n')
        print(f'   Error on Worksheet {ws.title}, Row {row_num} {var}. Valid Values are:')
        print(f'   sensitive_var[1-7].  Exiting....')
        print(f'\n-----------------------------------------------------------------------------\n')
        exit()

def site_group(row_num, ws, var, var_value):
    if re.search('Grp_', var_value):
        if not re.search('Grp_[A-F]', var_value):
            print(f'\n-----------------------------------------------------------------------------\n')
            print(f'   Error on Worksheet {ws.title}, Row {row_num} {var}, Site_Group "{var_value}"')
            print(f'   is invalid.  A valid Group Name is Grp_A thru Grp_F.  Exiting....')
            print(f'\n-----------------------------------------------------------------------------\n')
            exit()
    elif re.search(r'\d+', var_value):
        if not validators.between(int(var_value), min=1, max=12):
            print(f'\n-----------------------------------------------------------------------------\n')
            print(f'   Error on Worksheet {ws.title}, Row {row_num} {var}, Site_Group "{var_value}"')
            print(f'   is invalid.  A valid Site ID is between 1 and 12.  Exiting....')
            print(f'\n-----------------------------------------------------------------------------\n')
            exit()
    else:
        print(f'\n-----------------------------------------------------------------------------\n')
        print(f'   Error on Worksheet {ws.title}, Row {row_num} {var}, Site_Group "{var_value}"')
        print(f'   is invalid.  A valid Site_Group is either 1 thru 12 or Group_A thru Group_F.')
        print(f'   Exiting....')
        print(f'\n-----------------------------------------------------------------------------\n')
        exit()

def snmp_auth(row_num, ws, priv_type, priv_key, auth_type, auth_key):
    if not (priv_type == None or priv_type == 'none' or priv_type == 'aes-128' or priv_type == 'des'):
        print(f'\n-----------------------------------------------------------------------------\n')
        print(f'    Error on Worksheet {ws.title}, Row {row_num}. priv_type {priv_type} is not ')
        print(f'    [none|des|aes-128].  Exiting....')
        print(f'\n-----------------------------------------------------------------------------\n')
        exit()
    if not (priv_type == 'none' or priv_type == None):
        if not validators.length(priv_key, min=8, max=32):
            print(f'\n-----------------------------------------------------------------------------\n')
            print(f'   Error on Worksheet {ws.title}, Row {row_num}. priv_key does not ')
            print(f'   meet the minimum character count of 8 or the maximum of 32.  Exiting....')
            print(f'\n-----------------------------------------------------------------------------\n')
            exit()
    if not (auth_type == 'md5' or auth_type == 'sha1'):
        print(f'\n-----------------------------------------------------------------------------\n')
        print(f'    Error on Worksheet {ws.title}, Row {row_num}. priv_type {priv_type} is not ')
        print(f'    [md5|sha1].  Exiting....')
        print(f'\n-----------------------------------------------------------------------------\n')
        exit()
    if not validators.length(auth_key, min=8, max=32):
        print(f'\n-----------------------------------------------------------------------------\n')
        print(f'   Error on Worksheet {ws.title}, Row {row_num}. auth_key does not ')
        print(f'   meet the minimum character count of 8 or the maximum of 32.  Exiting....')
        print(f'\n-----------------------------------------------------------------------------\n')
        exit()

def snmp_mgmt(row_num, ws, var, var_value):
    if var_value == 'oob':
        var_value = 'Out-of-Band'
    elif var_value == 'inband':
        var_value = 'Inband'
    else:
        print(f'\n-----------------------------------------------------------------------------\n')
        print(f'   Error on Worksheet {ws.title}, Row {row_num} {var} value {var_value}.')
        print(f'   The Management Domain Should be inband or oob.  Exiting....')
        print(f'\n-----------------------------------------------------------------------------\n')
        exit()
    return var_value

def snmp_port(varName, varValue, minNum, maxNum):
    valid_count = 1
    if not (int(varValue) >= int(minNum) and int(varValue) <= int(maxNum)):
        print(f'\n-----------------------------------------------------------------------------\n')
        print(f'   Error with {varName}! "{varValue}".')
        print(f'   Valid values are between {minNum} and {maxNum}.')
        print(f'\n-----------------------------------------------------------------------------\n')
        valid_count = 0
    if re.fullmatch(r'^(22|23|80|123|389|443|623|636|2068|3268|3269)$', str(varValue)):
        print(f'\n-----------------------------------------------------------------------------\n')
        print(f'   Error with {varName}! "{varValue}".')
        print(f'   The following ports are not allowed:')
        print(f'   [22, 23, 80, 123, 389, 443, 623, 636, 2068, 3268, 3269]')
        print(f'\n-----------------------------------------------------------------------------\n')
        valid_count = 0
    if valid_count == 0:
        return False
    else:
        return True

def snmp_string(varName, varValue):
    if not (re.fullmatch(r'^([a-zA-Z]+[a-zA-Z0-9\-\_\.\@]+)$', varValue) and validators.length(varValue, min=8, max=32)):
        print(f'\n-----------------------------------------------------------------------------\n')
        print(f'   Error!!  {varName} is invalid.  The community and ')
        print(f'   username policy name must be a minimum of 8 and maximum of 32 characters ')
        print(f'   in length.  The name can contain only letters, numbers and the special ')
        print(f'   characters of underscore (_), hyphen (-), at sign (@), or period (.).')
        print(f'\n-----------------------------------------------------------------------------\n')
        return False
    else:
        return True

def stp(row_num, ws, var, var_value):
    if not re.search('^(BPDU_)', var_value):
        print(f'\n-----------------------------------------------------------------------------\n')
        print(f'   Error on Worksheet {ws.title}, Row {row_num} {var}, value {var_value}:')
        print(f'   Please Select a valid STP Policy from the drop-down menu.  Exiting....')
        print(f'\n-----------------------------------------------------------------------------\n')
        exit()
    if not re.search('(ft_and_gd|ft_or_gd|_ft|_gd)$', var_value):
        print(f'\n-----------------------------------------------------------------------------\n')
        print(f'   Error on Worksheet {ws.title}, Row {row_num} {var}, value {var_value}:')
        print(f'   Please Select a valid STP Policy from the drop-down menu.  Exiting....')
        print(f'\n-----------------------------------------------------------------------------\n')
        exit()

def string_length(varName, varValue, minLength, maxLength):
    if not validators.length(str(varValue), min=int(minLength), max=int(maxLength)):
        print(f'\n-----------------------------------------------------------------------------\n')
        print(f'   Error with {varName}! {varValue} must be between')
        print(f'   {minLength} and {maxLength} characters.')
        print(f'\n-----------------------------------------------------------------------------\n')
        return False
    else:
        return True

def sw_version(row_num, ws, var1, var_value):
    ver_count = 0
    if re.match('^n9000', var_value):
        regex = re.compile(r'^n9000\-\d{2}\.\d{1,2}\(\d{1,2}[a-z]\)$')
        if not re.fullmatch(regex, var_value):
            ver_count += 1
    else:
        regex = re.compile(r'^simsw-\d{1}\.\d{1,2}\(\d{1,2}[a-z]\)$')
        if not re.fullmatch(regex, var_value):
            ver_count += 1
    if not ver_count == 0:
        print(f"\n-----------------------------------------------------------------------------\n")
        print(f"   Error in Worksheet {ws.title} Row {row_num}.  The SW_Version {var_value}")
        print(f"   did not match against the required regex of:")
        print(f"    - {regex}.")
        print(f"   Exiting....")
        print(f"\n-----------------------------------------------------------------------------\n")
        exit()

def syslog_fac(row_num, ws, var, var_value):
    if not re.match("^local[0-7]$", var_value):
        print(f'\n-----------------------------------------------------------------------------\n')
        print(f'   Error on Worksheet {ws.title}, Row {row_num} {var}, "{var_value}" is invalid.')
        print(f'   Please verify Syslog Facility {var_value}.  Exiting...\n')
        print(f'\n-----------------------------------------------------------------------------\n')
        exit()

def tag_check(row_num, ws, var, var_value):
    tag_list = ['alice-blue', 'antique-white', 'aqua', 'aquamarine', 'azure', 'beige', 'bisque', 'black', 'blanched-almond', 'blue', 'blue-violet',
    'brown', 'burlywood', 'cadet-blue', 'chartreuse', 'chocolate', 'coral', 'cornflower-blue', 'cornsilk', 'crimson', 'cyan', 'dark-blue', 'dark-cyan',
    'dark-goldenrod', 'dark-gray', 'dark-green', 'dark-khaki', 'dark-magenta', 'dark-olive-green', 'dark-orange', 'dark-orchid', 'dark-red', 'dark-salmon',
    'dark-sea-green', 'dark-slate-blue', 'dark-slate-gray', 'dark-turquoise', 'dark-violet', 'deep-pink', 'deep-sky-blue', 'dim-gray', 'dodger-blue',
    'fire-brick', 'floral-white', 'forest-green', 'fuchsia', 'gainsboro', 'ghost-white', 'gold', 'goldenrod', 'gray', 'green', 'green-yellow', 'honeydew',
    'hot-pink', 'indian-red', 'indigo', 'ivory', 'khaki', 'lavender', 'lavender-blush', 'lawn-green', 'lemon-chiffon', 'light-blue', 'light-coral',
    'light-cyan', 'light-goldenrod-yellow', 'light-gray', 'light-green', 'light-pink', 'light-salmon', 'light-sea-green', 'light-sky-blue',
    'light-slate-gray', 'light-steel-blue', 'light-yellow', 'lime', 'lime-green', 'linen', 'magenta', 'maroon', 'medium-aquamarine', 'medium-blue',
    'medium-orchid', 'medium-purple', 'medium-sea-green', 'medium-slate-blue', 'medium-spring-green', 'medium-turquoise', 'medium-violet-red', 'midnight-blue',
    'mint-cream', 'misty-rose', 'moccasin', 'navajo-white', 'navy', 'old-lace', 'olive', 'olive-drab', 'orange', 'orange-red', 'orchid', 'pale-goldenrod',
    'pale-green', 'pale-turquoise', 'pale-violet-red', 'papaya-whip', 'peachpuff', 'peru', 'pink', 'plum', 'powder-blue', 'purple', 'red', 'rosy-brown',
    'royal-blue', 'saddle-brown', 'salmon', 'sandy-brown', 'sea-green', 'seashell', 'sienna', 'silver', 'sky-blue', 'slate-blue', 'slate-gray', 'snow',
    'spring-green', 'steel-blue', 'tan', 'teal', 'thistle', 'tomato', 'turquoise', 'violet', 'wheat', 'white', 'white-smoke', 'yellow', 'yellow-green' ]
    regx = re.compile(var_value)
    if not list(filter(regx.match, tag_list)):
        print(f'\n-----------------------------------------------------------------------------\n')
        print(f'   Error on Worksheet {ws.title}, Row {row_num} {var}, "{var_value}" is invalid.')
        print(f'   Valid Tag Values are:')
        print(f'   alice-blue, antique-white, aqua, aquamarine, azure, beige, bisque, black,')
        print(f'   blanched-almond, blue, blue-violet, brown, burlywood, cadet-blue, chartreuse,')
        print(f'   chocolate, coral, cornflower-blue, cornsilk, crimson, cyan, dark-blue, dark-cyan,')
        print(f'   dark-goldenrod, dark-gray, dark-green, dark-khaki, dark-magenta, dark-olive-green,')
        print(f'   dark-orange, dark-orchid, dark-red, dark-salmon, dark-sea-green, dark-slate-blue,')
        print(f'   dark-slate-gray, dark-turquoise, dark-violet, deep-pink, deep-sky-blue, dim-gray,')
        print(f'   dodger-blue, fire-brick, floral-white, forest-green, fuchsia, gainsboro, ghost-white,')
        print(f'   gold, goldenrod, gray, green, green-yellow, honeydew, hot-pink, indian-red, indigo,')
        print(f'   ivory, khaki, lavender, lavender-blush, lawn-green, lemon-chiffon, light-blue,')
        print(f'   light-coral, light-cyan, light-goldenrod-yellow, light-gray, light-green, light-pink,')
        print(f'   light-salmon, light-sea-green, light-sky-blue, light-slate-gray, light-steel-blue,')
        print(f'   light-yellow, lime, lime-green, linen, magenta, maroon, medium-aquamarine, medium-blue,')
        print(f'   medium-orchid, medium-purple, medium-sea-green, medium-slate-blue, medium-spring-green,')
        print(f'   medium-turquoise, medium-violet-red, midnight-blue, mint-cream, misty-rose, moccasin,')
        print(f'   navajo-white, navy, old-lace, olive, olive-drab, orange, orange-red, orchid,')
        print(f'   pale-goldenrod, pale-green, pale-turquoise, pale-violet-red, papaya-whip, peachpuff,')
        print(f'   peru, pink, plum, powder-blue, purple, red, rosy-brown, royal-blue, saddle-brown,')
        print(f'   salmon, sandy-brown, sea-green, seashell, sienna, silver, sky-blue, slate-blue,')
        print(f'   slate-gray, snow, spring-green, steel-blue, tan, teal, thistle, tomato, turquoise,')
        print(f'   violet, wheat, white, white-smoke, yellow, and yellow-green')
        print(f'   Exiting...\n')
        print(f'\n-----------------------------------------------------------------------------\n')
        exit()


def timeout(row_num, ws, var, var_value):
    timeout_count = 0
    if not validators.between(int(var_value), min=5, max=60):
        timeout_count += 1
    if not (int(var_value) % 5 == 0):
        timeout_count += 1
    if not timeout_count == 0:
        print(f'\n-----------------------------------------------------------------------------\n')
        print(f'   Error on Worksheet {ws.title}, Row {row_num} {var}, {var_value}. ')
        print(f'   {var} should be between 5 and 60 and be a factor of 5.  "{var_value}" ')
        print(f'   does not meet this.  Exiting....')
        print(f'\n-----------------------------------------------------------------------------\n')
        exit()

def url(varName, varValue):
    if not validators.url(varValue):
        print(f'\n-----------------------------------------------------------------------------\n')
        print(f'   Error with {varName}, {varValue}. ')
        print(f'   {varName} should be a valid URL.  The Following is not a valid URL:')
        print(f'    - {varValue}')
        print(f'\n-----------------------------------------------------------------------------\n')
        return False
    else:
        return True

def strong_password(varName, varValue, minLength, maxLength):
    invalid_count = 0
    if re.search(varName, varValue, re.IGNORECASE):
        invalid_count += 1
    if not validators.length(str(varValue), min=int(minLength), max=int(maxLength)):
        invalid_count += 1
    if not re.search(r'[a-z]', varValue):
        invalid_count += 1
    if not re.search(r'[A-Z]', varValue):
        invalid_count += 1
    if not re.search(r'[0-9]', varValue):
        invalid_count += 1
    if not re.search(r'[\!\@\#\$\%\^\&\*\-\_\+\=]', varValue):
        invalid_count += 1
    if not invalid_count == 0:
        print(f'\n---------------------------------------------------------------------------------------\n')
        print(f"   Error with {varName}! The password failed one of the following complexity rules:")
        print(f'     - The password must have a minimum of 8 and a maximum of 20 characters.')
        print(f"     - The password must not contain the User's Name.")
        print(f'     - The password must contain characters from three of the following four categories.')
        print(f'       * English uppercase characters (A through Z).')
        print(f'       * English lowercase characters (a through z).')
        print(f'       * Base 10 digits (0 through 9).')
        print(f'       * Non-alphabetic characters (! , @, #, $, %, ^, &, *, -, _, +, =)')
        print(f'\n---------------------------------------------------------------------------------------\n')
        return False
    else:
        return True

def username(varName, varValue, minLength, maxLength):
    if not re.search(r'^[a-zA-Z0-9\.\-\_]+$', varValue) and validators.length(str(varValue), min=int(minLength), max=int(maxLength)):
        print(f'\n-----------------------------------------------------------------------------\n')
        print(f'   Error with {varName}! Username {varValue} must be between ')
        print(f'   {varName} should be a valid URL.  The Following is not a valid URL:')
        print(f'    - {varValue}')
        print(f'    Exiting....')
        print(f'\n-----------------------------------------------------------------------------\n')
        return False
    else:
        return True

def uuid(varName, varValue):
    if not re.fullmatch(r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$', varValue):
        print(f'\n---------------------------------------------------------------------------------------\n')
        print(f'   Error with {varName}! "{varValue}"')
        print(f'   Is not a Valid UUID Identifier.')
        print(f'\n---------------------------------------------------------------------------------------\n')
        return False
    else:
        return True

def uuid_prefix(varName, varValue):
    if not re.fullmatch(r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}$', varValue):
        print(f'\n---------------------------------------------------------------------------------------\n')
        print(f'   Error with {varName}! "{varValue}"')
        print(f'   Is not a Valid UUID Prefix.')
        print(f'\n---------------------------------------------------------------------------------------\n')
        return False
    else:
        return True

def uuid_suffix(varName, varValue):
    if not re.fullmatch(r'^[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$', varValue):
        print(f'\n---------------------------------------------------------------------------------------\n')
        print(f'   Error with {varName}! "{varValue}"')
        print(f'   Is not a Valid UUID Suffix.')
        print(f'\n---------------------------------------------------------------------------------------\n')
        return False
    else:
        return True

def values(row_num, ws, var, varValue, value_list):
    match_count = 0
    for x in value_list:
        if x == varValue:
            match_count =+ 1
    if not match_count > 0:
        print(f'\n-----------------------------------------------------------------------------\n')
        print(f'   Error on Worksheet {ws.title}, Row {row_num} {var}, {varValue}. ')
        print(f'   {var} should be one of the following:')
        for x in value_list:
            print(f'    - {x}')
        print(f'    Exiting....')
        print(f'\n-----------------------------------------------------------------------------\n')
        exit()

def vlans(row_num, ws, var, var_value):
    if re.search(',', str(var_value)):
        vlan_split = var_value.split(',')
        for x in vlan_split:
            if re.search('\\-', x):
                dash_split = x.split('-')
                for z in dash_split:
                    if not validators.between(int(z), min=1, max=4095):
                        print(f'\n-----------------------------------------------------------------------------\n')
                        print(f'   Error on Worksheet {ws.title}, Row {row_num} {var}. Valid VLAN Values are:')
                        print(f'   between 1 and 4095.  Exiting....')
                        print(f'\n-----------------------------------------------------------------------------\n')
                        exit()
            elif not validators.between(int(x), min=1, max=4095):
                print(f'\n-----------------------------------------------------------------------------\n')
                print(f'   Error on Worksheet {ws.title}, Row {row_num} {var}. Valid VLAN Values are:')
                print(f'   between 1 and 4095.  Exiting....')
                print(f'\n-----------------------------------------------------------------------------\n')
                exit()
    elif re.search('\\-', str(var_value)):
        dash_split = var_value.split('-')
        for x in dash_split:
            if not validators.between(int(x), min=1, max=4095):
                print(f'\n-----------------------------------------------------------------------------\n')
                print(f'   Error on Worksheet {ws.title}, Row {row_num} {var}. Valid VLAN Values are:')
                print(f'   between 1 and 4095.  Exiting....')
                print(f'\n-----------------------------------------------------------------------------\n')
                exit()
    elif not validators.between(int(var_value), min=1, max=4095):
        print(f'\n-----------------------------------------------------------------------------\n')
        print(f'   Error on Worksheet {ws.title}, Row {row_num} {var}. Valid VLAN Values are:')
        print(f'   between 1 and 4095.  Exiting....')
        print(f'\n-----------------------------------------------------------------------------\n')
        exit()

def vname(varName, varValue):
    if not re.fullmatch(r'^[a-zA-Z0-9\-\.\_:]{1,31}$', varValue):
        print(f'\n---------------------------------------------------------------------------------------\n')
        print(f'   Error with {varName}! "{varValue}" did not meet the validation rules.  The name can')
        print(f'   can contain letters (a-zA-Z), numbers (0-9), dash "-", period ".", underscore "_",')
        print(f'   and colon ":". and be between 1 and 31 characters.')
        print(f'\n---------------------------------------------------------------------------------------\n')
        return False
    else:
        return True

def ws_hostname(row_num, ws, var, var_value):
    if not (re.search('^[a-zA-Z0-9\\-]+$', var_value) and validators.length(var_value, min=1, max=63)):
        print(f'\n-----------------------------------------------------------------------------\n')
        print(f'   Error on Worksheet {ws.title}, Row {row_num} {var}, {var_value} ')
        print(f'   is not a valid Hostname.  Be sure you are not using the FQDN.  Exiting....')
        print(f'\n-----------------------------------------------------------------------------\n')
        exit()

def ws_ip_address(row_num, ws, var, var_value):
    if re.search('/', var_value):
        x = var_value.split('/')
        address = x[0]
    else:
        address = var_value
    valid_count = 0
    if re.search(r'\.', address):
        if not validators.ip_address.ipv4(address):
            valid_count =+ 1
    else:
        if not validators.ip_address.ipv6(address):
            valid_count =+ 1
    if not valid_count == 0:
        print(f'\n-----------------------------------------------------------------------------\n')
        print(f'   Error on Worksheet {ws.title} Row {row_num}. {var} {var_value} is not ')
        print(f'   a valid IPv4 or IPv6 Address.  Exiting....')
        print(f'\n-----------------------------------------------------------------------------\n')
        exit()

