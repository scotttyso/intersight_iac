import ipaddress
import re
import string
import validators

# Errors
def error_file_location(varName, varValue):
    print(f'\n-------------------------------------------------------------------------------------------\n')
    print(f'  Error!! The "{varName}" "{varValue}"')
    print(f'  is invalid.  Please valid the Entry for "{varName}".')
    print(f'\n-------------------------------------------------------------------------------------------\n')

def error_request(status, text):
    print(f'\n-------------------------------------------------------------------------------------------\n')
    print(f'   Error in Retreiving Terraform Cloud Organization Workspaces')
    print(f'   Exiting on Error {status} with the following output:')
    print(f'   {text}')
    print(f'\n-------------------------------------------------------------------------------------------\n')
    exit()

def error_subnet_check(**kwargs):
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

def error_number_in_range(varName, varValue, minNum, maxNum):
    print(f'\n-------------------------------------------------------------------------------------------\n')
    print(f'  Error!! {varName} with value {varValue}.')
    print(f'  Please enter a number in the range of {minNum} and {maxNum}.')
    print(f'\n-------------------------------------------------------------------------------------------\n')

# Validations
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

def string_length(varName, varValue, minLength, maxLength):
    if not validators.length(str(varValue), min=int(minLength), max=int(maxLength)):
        print(f'\n-----------------------------------------------------------------------------\n')
        print(f'   Error with {varName}! {varValue} must be between')
        print(f'   {minLength} and {maxLength} characters.')
        print(f'\n-----------------------------------------------------------------------------\n')
        return False
    else:
        return True

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