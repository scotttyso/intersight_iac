#=============================================================================
# Source Modules
#=============================================================================
def prRed(skk): print("\033[91m {}\033[00m" .format(skk))
import sys
try:
    from classes import pcolor
    import ipaddress, json, re, validators
except ImportError as e:
    prRed(f'!!! ERROR !!!\n{e.__class__.__name__}')
    prRed(f" Module {e.name} is required to run this script")
    prRed(f" Install the module using the following: `pip install {e.name}`")
    sys.exit(1)

oregex = re.compile(
    'fabric.([a-zA-z]+(Mode|Role)|(Eth|Fc)NetworkP)|vnic.(Eth|Fc)If|iam.EndPointUserRole|DriveGroup|Ldap(Group|Provider)')
policy_regex = re.compile('(network_connectivity|ntp|port|snmp|switch_control|syslog|system_qos|vlan|vsan)')

# Errors & Notifications
def begin_loop(ptype1, ptype2):
    pcolor.LightGray(f'\n-------------------------------------------------------------------------------------------\n')
    pcolor.LightPurple(f"  Beginning {' '.join(ptype1.split('_')).title()} {ptype2} Deployment.\n")

def begin_section(ptype1, ptype2):
    pcolor.LightGray(f'\n-------------------------------------------------------------------------------------------\n')
    pcolor.LightPurple(
        f"  Beginning {ptype1} {' '.join(ptype2.split('_')).title()} Deployments.\n")

def completed_item(ptype, kwargs):
    iresults = kwargs.api_results
    method = kwargs.method
    pmoid  = iresults.Moid
    if   'vnic.EthIf' == iresults['ObjectType']: name = f"vNIC {iresults['Name']}"
    elif 'vnic.FcIf' == iresults['ObjectType']:  name = f"vHBA {iresults['Name']}"
    elif 'autosupport' == ptype:        name = "AutoSupport"
    elif iresults.get('PcId'):          name = f"PC {iresults['PcId']}"
    elif iresults.get('PortId'):        name = f"Port {iresults['PortId']}"
    elif iresults.get('PortIdStart'):   name = f"PortIdStart {iresults['PortIdStart']}"
    elif iresults.get('VirtualDrives'): name = f"DriveGroup {iresults['Name']}"
    elif iresults.get('VlanId'):        name = f"VLAN {iresults['VlanId']}"
    elif iresults.get('VsanId'):        name = f"VSAN {iresults['VsanId']}"
    elif 'user_role' in ptype:          name = f"Role for {kwargs.qtype}"
    elif 'upgrade' in kwargs.qtype:     name = f".  Performing Firmware Upgrade on {kwargs.serial} - {kwargs.server} Server Profile"
    elif iresults.get('UserId'):        name = f"{iresults['UserId']} CCO User Authentication"
    elif 'eula' in kwargs.qtype:        name = f"Account EULA Acceptance"
    elif iresults.get('Action'):
        if iresults['Action'] == 'Deploy': name = f"Deploy Profile {pmoid}"
        else: name = iresults['Name']
    elif iresults.get('ScheduledActions'): name = f"Activating Profile {pmoid}"
    elif iresults.get('Targets'):          name = iresults['Targets'][0]['Name']
    elif 'update_tags' in kwargs.qtype:    name = f"Tags updated for Physical Server attached to {kwargs.tag_server_profile}"
    else: name = iresults['Name']
    if re.search(oregex, iresults.get('ObjectType')):
        parent_type = iresults['ObjectType'].split('.')[1]
        if method == 'post':
            pcolor.Green(f'      * Completed {method} for {kwargs.parent_type} `{kwargs.parent_name}`: {name} - Moid: {pmoid}')
        else: pcolor.LightPurple(f'      * Completed {method} for {kwargs.parent_type} `{kwargs.parent_name}`: {name} - Moid: {pmoid}')
    elif re.search('^(Activating|Deploy)', name): pcolor.Cyan(f'      * {name}.')
    elif re.search('(eula|upgrade)', kwargs.qtype) and kwargs.qtype == 'firmware':
        if method == 'post': pcolor.Green(f'      * Completed {method} for {kwargs.qtype} {name}.')
        else: pcolor.LightPurple(f'      * Completed {method} for {kwargs.qtype} {name}.')
    elif iresults.get('Targets'):
        if method == 'post': pcolor.Green(f'    - Completed Bulk Clone {method} for name: {name} - Moid: {pmoid}')
        else: pcolor.LightPurple(f'    - Completed Bulk Clone {method} for name: {name} - Moid: {pmoid}')
    else:
        if method == 'post': pcolor.Green(f'    - Completed {method} for name: {name} - Moid: {pmoid}')
        else: pcolor.LightPurple(f'    - Completed {method} for name: {name} - Moid: {pmoid}')

def deploy_notification(profile, profile_type):
    print(f'\n-------------------------------------------------------------------------------------------\n')
    pcolor.LightPurple(f'   Deploy Action Still ongoing for {profile_type} Profile {profile}')
    print(f'\n-------------------------------------------------------------------------------------------\n')

def error_file_location(varName, varValue):
    print(f'\n-------------------------------------------------------------------------------------------\n')
    print(f'  !!! ERROR !!! The "{varName}" "{varValue}"')
    print(f'  is invalid.  Please valid the Entry for "{varName}".')
    print(f'\n-------------------------------------------------------------------------------------------\n')

def end_loop(ptype1, ptype2):
    pcolor.LightPurple(f"\n   Completed {' '.join(ptype1.split('_')).title()} {ptype2} Deployment.")

def end_section(ptype1, ptype2):
    pcolor.LightPurple(f"\n   Completed {ptype1} {' '.join(ptype2.split('_')).title()} Deployments.")

def error_policy_doesnt_exist(policy_type, policy_name, profile, profile_type, ptype):
    print(f'\n-------------------------------------------------------------------------------------------\n')
    print(f'   !!! ERROR !!! The Following policy was attached to {profile_type} {ptype} {profile}')
    print(f'   But it has not been created.')
    print(f'   Policy Type: {policy_type}')
    print(f'   Policy Name: {policy_name}')
    print(f'\n-------------------------------------------------------------------------------------------\n')
    sys.exit(1)

def error_request(status, text):
    print(f'\n-------------------------------------------------------------------------------------------\n')
    print(f'   !!! ERROR !!! in Retreiving Terraform Cloud Organization Workspaces')
    print(f'   Exiting on Error {status} with the following output:')
    print(f'   {text}')
    print(f'\n-------------------------------------------------------------------------------------------\n')
    sys.exit(1)

def error_request_netapp(method, status, text, uri):
    print(f'\n-------------------------------------------------------------------------------------------\n')
    print(f'   !!! ERROR !!! when attempting {method} to {uri}')
    print(f'   Exiting on Error {status} with the following output:')
    print(f'   {text}')
    print(f'\n-------------------------------------------------------------------------------------------\n')
    sys.exit(1)

def error_request_pure_storage(method, status, text, uri):
    print(f'\n-------------------------------------------------------------------------------------------\n')
    print(f'   !!! ERROR !!! when attempting {method} to {uri}')
    print(f'   Exiting on Error {status} with the following output:')
    print(f'   {text}')
    print(f'\n-------------------------------------------------------------------------------------------\n')
    sys.exit(1)

def error_serial_number(name, serial):
    print(f'\n-------------------------------------------------------------------------------------------\n')
    print(f'  !!! ERROR !!! The Serial Number "{serial}" for "{name}" was not found in inventory.')
    print(f'  Please check the serial number for "{name}".')
    print(f'\n-------------------------------------------------------------------------------------------\n')
    sys.exit(1)

def error_subnet_check(kwargs):
    ip_version = kwargs['ip_version']
    if ip_version == 'v4': prefix = kwargs['subnetMask']
    else: prefix = kwargs['prefix']
    gateway = kwargs['defaultGateway']
    pool_from = ipaddress.ip_address(kwargs['pool_from'])
    pool_to = ipaddress.ip_address(kwargs['pool_to'])
    if not pool_from in ipaddress.ip_network(f"{gateway}/{prefix}", strict=False):
        print(f'\n{"-"*91}\n')
        print(f'   !!! ERROR !!!  {pool_from} is not in network {gateway}/{prefix}:')
        print(f'   Exiting....')
        print(f'\n{"-"*91}\n')
        sys.exit(1)
    if not pool_to in ipaddress.ip_network(f"{gateway}/{prefix}", strict=False):
        print(f'\n{"-"*91}\n')
        print(f'   !!! ERROR !!!  {pool_to} is not in network {gateway}/{prefix}:')
        print(f'   Exiting....')
        print(f'\n{"-"*91}\n')
        sys.exit(1)


def error_subnet_not_found(kwargs):
    poolFrom = kwargs['pool_from']
    print(f'\n{"-"*91}\n')
    print(f'   !!! ERROR !!!  Did not Find a Correlating Network for {poolFrom}.')
    print(f'   Defined Network List:')
    for i in kwargs['networks']:
        print(f'    * {i}')
        print(f'   Exiting....')
    print(f'\n{"-"*91}\n')
    sys.exit(1)


def unmapped_keys(policy_type, name, key):
    print(f'\n{"-"*91}\n')
    print(f'   !!! ERROR !!!! For {policy_type}, {name}, unknown key {key}')
    print(f'\n{"-"*91}\n')
    sys.exit(1)
 
# Validations
def boolean(var, kwargs):
    row_num = kwargs['row_num']
    ws = kwargs['ws']
    varValue = kwargs['var_dict'][var]
    valid_count = 1
    if varValue == 'True' or varValue == 'False':
        valid_count = 0
    if not valid_count == 0:
        print(f'\n--------------------------------------------------------------------------------\n')
        print(f'   Error on Worksheet "{ws.title}", Row {row_num}, Variable {var};')
        print(f'   must be True or False.  Exiting....')
        print(f'\n--------------------------------------------------------------------------------\n')
        sys.exit(1)

def description(varName, varValue, minLength, maxLength):
    if not (re.search(r'^[a-zA-Z0-9\\!#$%()*,-./:;@ _{|}~?&+]+$',  varValue) and \
    validators.length(str(varValue), min=int(minLength), max=int(maxLength))):
        print(f'\n-----------------------------------------------------------------------------\n')
        print(f'   The description is an invalid Value... It failed one of the following')
        print(f'   complexity tests:')
        print(f'    - Min Length {minLength}')
        print(f'    - Max Length {maxLength}')
        print('    - Regex [a-zA-Z0-9\\!#$%()*,-./:;@ _{|}~?&+]+')
        print(f'\n-----------------------------------------------------------------------------\n')
        return False
    else: return True

def domain(varName, varValue):
    if not validators.domain(varValue):
        print(f'\n-----------------------------------------------------------------------------\n')
        print(f'   Error with {varName}!!!  Invalid Domain {varValue}')
        print(f'   Please Validate the domain and retry.')
        print(f'\n-----------------------------------------------------------------------------\n')
        return False
    else: return True

def domain_ws(var, kwargs):
    row_num  = kwargs['row_num']
    ws       = kwargs['ws']
    varValue = kwargs['var_dict'][var]
    if not validators.domain(varValue):
        print(f'\n-----------------------------------------------------------------------------\n')
        print(f'   Error on Worksheet {ws.title}, Row {row_num} {var}, {varValue} ')
        print(f'   Error with {var}. Invalid Domain "{varValue}"')
        print(f'   Please Validate the domain and retry.')
        print(f'\n-----------------------------------------------------------------------------\n')
        sys.sys.exit(1)
    else: return True

def dns_name(varName, varValue):
    hostname = varValue
    valid_count = 0
    if len(hostname) > 255: valid_count =+ 1
    if not validators.domain(hostname): valid_count =+ 1
    if hostname[-1] == ".": hostname = hostname[:-1] # strip exactly one dot from the right, if present
    allowed = re.compile("(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
    if not all(allowed.match(x) for x in hostname.split(".")): valid_count =+ 1
    if not valid_count == 0:
        print(f'\n--------------------------------------------------------------------------------\n')
        print(f'   Error with {varName}.  "{varValue}" is not a valid Hostname/Domain.')
        print(f'   Confirm that you have entered the DNS Name Correctly.')
        print(f'\n--------------------------------------------------------------------------------\n')
        return False
    else: return True

def dns_name_ws(var, kwargs):
    row_num  = kwargs['row_num']
    ws       = kwargs['ws']
    varValue = kwargs['var_dict'][var]
    hostname = varValue
    valid_count = 0
    if len(hostname) > 255:
        valid_count =+ 1
    if re.search('^\\..*', varValue):
        domain = varValue.strip('.')
        if not validators.domain(domain): valid_count =+ 1
    if not re.search('^\\..*', hostname):
        if hostname[-1] == ".": hostname = hostname[:-1] # strip exactly one dot from the right, if present
        allowed = re.compile("(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
        if not all(allowed.match(x) for x in hostname.split(".")):
            valid_count =+ 1
    if not valid_count == 0:
        print(f'\n--------------------------------------------------------------------------------\n')
        print(f'   Error on Worksheet {ws.title}, Row {row_num} {var}, {varValue} ')
        print(f'   is not a valid Hostname.  Confirm that you have entered the DNS Name Correctly.')
        print(f'   Exiting....')
        print(f'\n--------------------------------------------------------------------------------\n')
        sys.exit(1)

def email(varName, varValue):
    if not validators.email(varValue, whitelist=None):
        print(f'\n-----------------------------------------------------------------------------\n')
        print(f'   Error with {varName}. Email address "{varValue}"')
        print(f'   is invalid.  Please Validate the email and retry.')
        print(f'\n-----------------------------------------------------------------------------\n')
        return False
    else: return True

def email_ws(var, kwargs):
    row_num  = kwargs['row_num']
    ws       = kwargs['ws']
    varValue = kwargs['var_dict'][var]
    if not validators.email(varValue, whitelist=None):
        print(f'\n-----------------------------------------------------------------------------\n')
        print(f'   Error on Worksheet {ws.title}, Row {row_num} {var}, {varValue} ')
        print(f'   Error with {var}. Email address "{varValue}"')
        print(f'   is invalid.  Please Validate the email and retry.')
        print(f'\n-----------------------------------------------------------------------------\n')
        sys.sys.exit(1)
    else: return True

def ip_address(varName, varValue):
    if re.search('/', varValue):
        x = varValue.split('/')
        address = x[0]
    else: address = varValue
    valid_count = 0
    if re.search(r'\.', address):
        if not validators.ip_address.ipv4(address): valid_count =+ 1
    else:
        if not validators.ip_address.ipv6(address): valid_count =+ 1
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
    else: return True

def ip_address_ws(var, kwargs):
    row_num  = kwargs['row_num']
    ws       = kwargs['ws']
    varValue = kwargs['var_dict'][var]
    if re.search('/', varValue):
        x = varValue.split('/')
        address = x[0]
    else: address = varValue
    valid_count = 0
    if re.search(r'\.', address):
        if not validators.ip_address.ipv4(address): valid_count =+ 1
    else:
        if not validators.ip_address.ipv6(address): valid_count =+ 1
    if not valid_count == 0 and re.search(r'\.', address):
        print(f'\n-----------------------------------------------------------------------------\n')
        print(f'   Error on row {row_num} with {var}. "{varValue}" is not a valid IPv4 Address.')
        print(f'\n-----------------------------------------------------------------------------\n')
        return False
    elif not valid_count == 0:
        print(f'\n-----------------------------------------------------------------------------\n')
        print(f'   Error on row {row_num} with {var}. "{varValue}" is not a valid IPv6 Address.')
        print(f'\n-----------------------------------------------------------------------------\n')
        return False
    else: return True

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
    else: return True

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
    else: return True

def length_and_regex(answer, minLength, maxLength, pattern, title):
    invalid_count = 0
    if minLength == 0 and maxLength == 0: invalid_count = 0
    else:
        if not validators.length(answer, min=int(minLength), max=int(maxLength)):
            invalid_count += 1
            print(f'\n--------------------------------------------------------------------------------------\n')
            print(f'   !!! {title} value "{answer}" is Invalid!!!')
            print(f'   Length Must be between {minLength} and {maxLength} characters.')
            print(f'\n--------------------------------------------------------------------------------------\n')
    if not re.search(pattern, str(answer)):
        invalid_count += 1
        print(f'\n--------------------------------------------------------------------------------------\n')
        print(f'   !!! Invalid Characters in {answer}.  The allowed characters are:')
        print(f'   - "{pattern}"')
        print(f'\n--------------------------------------------------------------------------------------\n')
    if invalid_count == 0:
        return True
    else: return False

def list_values(var, json_data, kwargs):
    json_data = kwargs['validateData']
    row_num = kwargs['row_num']
    ws = kwargs['ws']
    varList = json_data[var]['enum']
    varValue = kwargs['var_dict'][var]
    match_count = 0
    for x in varList:
        if str(x) == str(varValue):
            match_count =+ 1
    if not match_count > 0:
        print(f'\n-----------------------------------------------------------------------------\n')
        print(f'   Error on Worksheet {ws.title}, Row {row_num} {var}, {varValue}. ')
        print(f'   {var} should be one of the following:')
        for x in varList:
            print(f'    - {x}')
        print(f'    Exiting....')
        print(f'\n-----------------------------------------------------------------------------\n')
        sys.exit(1)

def list_values_key(dictkey, var, kwargs):
    json_data = kwargs['validateData']
    row_num = kwargs['row_num']
    ws = kwargs['ws']
    varList = json_data[dictkey]['enum']
    varValue = kwargs['var_dict'][var]
    match_count = 0
    for x in varList:
        if x == varValue:
            match_count =+ 1
    if not match_count > 0:
        print(f'\n-----------------------------------------------------------------------------\n')
        print(f'   Error on Worksheet {ws.title}, Row {row_num} {var}, {varValue}. ')
        print(f'   {var} should be one of the following:')
        for x in varList:
            print(f'    - {x}')
        print(f'    Exiting....')
        print(f'\n-----------------------------------------------------------------------------\n')
        sys.exit(1)

def mac_address(varName, varValue):
    if not validators.mac_address(varValue):
        print(f'\n-----------------------------------------------------------------------------\n')
        print(f'   Error with {varName}. "{varValue}" is not a valid MAC Address.')
        print(f'\n-----------------------------------------------------------------------------\n')
        return False
    else: return True

def number_check(var, json_data, kwargs):
    minimum = json_data[var]['minimum']
    maximum = json_data[var]['maximum']
    row_num = kwargs['row_num']
    ws = kwargs['ws']
    varValue = kwargs['var_dict'][var]
    if not (validators.between(int(varValue), min=int(minimum), max=int(maximum))):
        print(f'\n-----------------------------------------------------------------------------\n')
        print(f'   Error on Worksheet {ws.title}, Row {row_num} {var}, {varValue}. Valid Values ')
        print(f'   are between {minimum} and {maximum}.  Exiting....')
        print(f'\n-----------------------------------------------------------------------------\n')
        sys.exit(1)

def number_list(var, kwargs):
    json_data = kwargs['validateData']
    minimum = json_data[var]['minimum']
    maximum = json_data[var]['maximum']
    row_num = kwargs['row_num']
    ws = kwargs['ws']
    varValue = kwargs['var_dict'][var]
    if '-' in str(varValue):
        varValue = varValue.split('-')
        if ',' in str(varValue):
            varValue = varValue.split(',')
    elif ',' in str(varValue):
        varValue = varValue.split(',')
    else:
        varValue = [varValue]
    for x in varValue:
        if not (validators.between(int(x), min=int(minimum), max=int(maximum))):
            print(f'\n-----------------------------------------------------------------------------\n')
            print(f'   Error on Worksheet {ws.title}, Row {row_num} {var}, {x}. Valid Values ')
            print(f'   are between {minimum} and {maximum}.  Exiting....')
            print(f'\n-----------------------------------------------------------------------------\n')
            sys.exit(1)

def string_list(var, json_data, kwargs):
    # Get Variables from Library
    minimum = json_data[var]['minimum']
    maximum = json_data[var]['maximum']
    pattern = json_data[var]['pattern']
    row_num = kwargs['row_num']
    varValues = kwargs['var_dict'][var]
    ws = kwargs['ws']
    for varValue in varValues.split(','):
        if not (re.fullmatch(pattern,  varValue) and validators.length(
            str(varValue), min=int(minimum), max=int(maximum))):
            print(f'\n-----------------------------------------------------------------------------\n')
            print(f'   Error on Worksheet {ws.title}, Row {row_num} {var}. ')
            print(f'   "{varValue}" is an invalid Value...')
            print(f'   It failed one of the complexity tests:')
            print(f'    - Min Length {maximum}')
            print(f'    - Max Length {maximum}')
            print(f'    - Regex {pattern}')
            print(f'    Exiting....')
            print(f'\n-----------------------------------------------------------------------------\n')
            sys.exit(1)

def string_pattern(var, json_data, kwargs):
    # Get Variables from Library
    minimum = json_data[var]['minimum']
    maximum = json_data[var]['maximum']
    pattern = json_data[var]['pattern']
    row_num = kwargs['row_num']
    varValue = kwargs['var_dict'][var]
    ws = kwargs['ws']
    if not (re.fullmatch(pattern,  varValue) and validators.length(
        str(varValue), min=int(minimum), max=int(maximum))):
        print(f'\n-----------------------------------------------------------------------------\n')
        print(f'   Error on Worksheet {ws.title}, Row {row_num} {var}. ')
        print(f'   "{varValue}" is an invalid Value...')
        print(f'   It failed one of the complexity tests:')
        print(f'    - Min Length {minimum}')
        print(f'    - Max Length {maximum}')
        print(f'    - Regex {pattern}')
        print(f'    Exiting....')
        print(f'\n-----------------------------------------------------------------------------\n')
        sys.exit(1)

def wwxn_address(varName, varValue):
    if not re.search(r'([0-9A-F]{2}[:-]){7}([0-9A-F]{2})', varValue):
        print(f'\n-----------------------------------------------------------------------------\n')
        print(f'   Error with {varName}. "{varValue}" is not a valid WWxN Address.')
        print(f'\n-----------------------------------------------------------------------------\n')
        return False
    else: return True

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
    else: return True

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
    else: return True

def number_in_range(varName, varValue, minNum, maxNum):
    if not validators.between(int(varValue), min=int(minNum), max=int(maxNum)):
        print(f'\n-----------------------------------------------------------------------------\n')
        print(f'   Error with {varName}! "{varValue}".')
        print(f'   Valid values are between {minNum} and {maxNum}.')
        print(f'\n-----------------------------------------------------------------------------\n')
        return False
    else: return True

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
    if valid_count == 0: return False
    else: return True

def snmp_string(varName, varValue):
    if not (re.fullmatch(r'^([a-zA-Z]+[a-zA-Z0-9\-\_\.\@]+)$', varValue) and validators.length(varValue, min=8, max=32)):
        print(f'\n-----------------------------------------------------------------------------\n')
        print(f'   Error!!  {varName} is invalid.  The community and ')
        print(f'   username policy name must be a minimum of 8 and maximum of 32 characters ')
        print(f'   in length.  The name can contain only letters, numbers and the special ')
        print(f'   characters of underscore (_), hyphen (-), at sign (@), or period (.).')
        print(f'\n-----------------------------------------------------------------------------\n')
        return False
    else: return True

def string_length(varName, varValue, minLength, maxLength):
    if not validators.length(str(varValue), min=int(minLength), max=int(maxLength)):
        print(f'\n-----------------------------------------------------------------------------\n')
        print(f'   Error with {varName}! {varValue} must be between')
        print(f'   {minLength} and {maxLength} characters.')
        print(f'\n-----------------------------------------------------------------------------\n')
        return False
    else: return True

def url(varName, varValue):
    if not validators.url(varValue):
        print(f'\n-----------------------------------------------------------------------------\n')
        print(f'   Error with {varName}, {varValue}. ')
        print(f'   {varName} should be a valid URL.  The Following is not a valid URL:')
        print(f'    - {varValue}')
        print(f'\n-----------------------------------------------------------------------------\n')
        return False
    else: return True

def username(varName, varValue, minLength, maxLength):
    if not re.search(r'^[a-zA-Z0-9\.\-\_]+$', varValue) and validators.length(str(varValue), min=int(minLength), max=int(maxLength)):
        print(f'\n-----------------------------------------------------------------------------\n')
        print(f'   Error with {varName}! Username {varValue} must be between ')
        print(f'   {varName} should be a valid URL.  The Following is not a valid URL:')
        print(f'    - {varValue}')
        print(f'    Exiting....')
        print(f'\n-----------------------------------------------------------------------------\n')
        return False
    else: return True

def uuid(varName, varValue):
    if not re.fullmatch(r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$', varValue):
        print(f'\n---------------------------------------------------------------------------------------\n')
        print(f'   Error with {varName}! "{varValue}"')
        print(f'   Is not a Valid UUID Identifier.')
        print(f'\n---------------------------------------------------------------------------------------\n')
        return False
    else: return True

def uuid_prefix(varName, varValue):
    if not re.fullmatch(r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}$', varValue):
        print(f'\n---------------------------------------------------------------------------------------\n')
        print(f'   Error with {varName}! "{varValue}"')
        print(f'   Is not a Valid UUID Prefix.')
        print(f'\n---------------------------------------------------------------------------------------\n')
        return False
    else: return True

def uuid_suffix(varName, varValue):
    if not re.fullmatch(r'^[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$', varValue):
        print(f'\n---------------------------------------------------------------------------------------\n')
        print(f'   Error with {varName}! "{varValue}"')
        print(f'   Is not a Valid UUID Suffix.')
        print(f'\n---------------------------------------------------------------------------------------\n')
        return False
    else: return True

def vlans(var, kwargs):
    row_num = kwargs['row_num']
    ws = kwargs['ws']
    varValue = kwargs['var_dict'][var]
    if re.search(',', str(varValue)):
        vlan_split = varValue.split(',')
        for x in vlan_split:
            if re.search('\\-', x):
                dash_split = x.split('-')
                for z in dash_split:
                    if not validators.between(int(z), min=1, max=4095):
                        print(f'\n-----------------------------------------------------------------------------\n')
                        print(f'   Error on Worksheet {ws.title}, Row {row_num} {var}. Valid VLAN Values are:')
                        print(f'   between 1 and 4095.  "{z}" is not valid.  Exiting....')
                        print(f'\n-----------------------------------------------------------------------------\n')
                        sys.exit(1)
            elif not validators.between(int(x), min=1, max=4095):
                print(f'\n-----------------------------------------------------------------------------\n')
                print(f'   Error on Worksheet {ws.title}, Row {row_num} {var}. Valid VLAN Values are:')
                print(f'   between 1 and 4095.  "{x}" is not valid.  Exiting....')
                print(f'\n-----------------------------------------------------------------------------\n')
                sys.exit(1)
    elif re.search('\\-', str(varValue)):
        dash_split = varValue.split('-')
        for x in dash_split:
            if not validators.between(int(x), min=1, max=4095):
                print(f'\n-----------------------------------------------------------------------------\n')
                print(f'   Error on Worksheet {ws.title}, Row {row_num} {var}. Valid VLAN Values are:')
                print(f'   between 1 and 4095.  "{x}" is not valid.  Exiting....')
                print(f'\n-----------------------------------------------------------------------------\n')
                sys.exit(1)
    elif not validators.between(int(varValue), min=1, max=4095):
        print(f'\n-----------------------------------------------------------------------------\n')
        print(f'   Error on Worksheet {ws.title}, Row {row_num} {var}. Valid VLAN Values are:')
        print(f'   between 1 and 4095.  "{varValue}" is not valid.  Exiting....')
        print(f'\n-----------------------------------------------------------------------------\n')
        sys.exit(1)

def vname(varName, varValue):
    if not re.fullmatch(r'^[a-zA-Z0-9\-\.\_:]{1,31}$', varValue):
        print(f'\n---------------------------------------------------------------------------------------\n')
        print(f'   Error with {varName}! "{varValue}" did not meet the validation rules.  The name can')
        print(f'   can contain letters (a-zA-Z), numbers (0-9), dash "-", period ".", underscore "_",')
        print(f'   and colon ":". and be between 1 and 31 characters.')
        print(f'\n---------------------------------------------------------------------------------------\n')
        return False
    else: return True
