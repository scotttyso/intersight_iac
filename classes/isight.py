#=============================================================================
# Print Color Functions
#=============================================================================
def prCyan(skk):        print("\033[96m {}\033[00m" .format(skk))
def prGreen(skk):       print("\033[92m {}\033[00m" .format(skk))
def prLightPurple(skk): print("\033[94m {}\033[00m" .format(skk))
def prLightGray(skk):   print("\033[94m {}\033[00m" .format(skk))
def prPurple(skk):      print("\033[95m {}\033[00m" .format(skk))
def prRed(skk):         print("\033[91m {}\033[00m" .format(skk))
def prYellow(skk):      print("\033[93m {}\033[00m" .format(skk))

#=============================================================================
# Source Modules
#=============================================================================
try:
    from classes import ezfunctions, validating
    from intersight_auth import IntersightAuth
    from copy import deepcopy
    from dotmap import DotMap
    from stringcase import pascalcase, snakecase
    import json, numpy, os, re, requests, sys, time, urllib3
except ImportError as e:
    prRed(f'!!! ERROR !!!\n{e.__class__.__name__}')
    prRed(f" Module {e.name} is required to run this script")
    prRed(f" Install the module using the following: `pip install {e.name}`")
    sys.exit(1)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

serial_regex = re.compile('^[A-Z]{3}[2-3][\\d]([0][1-9]|[1-4][0-9]|[5][0-3])[\\dA-Z]{4}$')
part1 = 'bios|boot_order|(ethernet|fibre_channel)_adapter|firmware|imc_access|ipmi_over_lan|iscsi_(boot|static_target)'
part2 = '(l|s)an_connectivity|local_user|network_connectivity|snmp|storage|system_qos'
policy_specific_regex = re.compile(f'^{part1}|{part2}$')

#=======================================================
# API Class
#=======================================================
class api(object):
    def __init__(self, type):
        self.type = type

    #=====================================================
    # Perform API Calls to Intersight
    #=====================================================
    def calls(self, kwargs):
        #=======================================================
        # Global options for debugging
        # 1 - Shows the api request response status code
        # 5 - Show URL String + Lower Options
        # 6 - Adds Results + Lower Options
        # 7 - Adds json payload + Lower Options
        # Note: payload shows as pretty and straight to check
        #       for stray object types like Dotmap and numpy
        #=======================================================
        debug_level   = kwargs.args.debug_level

        #=====================================================
        # Authenticate to the API
        #=====================================================
        if not re.search('^(organization|resource)/', kwargs.uri):
            org_moid = kwargs.org_moids[kwargs.org].moid
        #=====================================================
        # Authenticate to the API
        #=====================================================
        def api_auth_function(kwargs):
            api_key_id      = kwargs.args.intersight_api_key_id
            secret_key      = kwargs.args.intersight_secret_key
            if os.path.isfile(secret_key):
                kwargs.api_auth = IntersightAuth(api_key_id=api_key_id, secret_key_filename=secret_key)
            else: kwargs.api_auth = IntersightAuth(api_key_id=api_key_id, secret_key_string=secret_key)
            kwargs.auth_time= time.time()
            return kwargs
        #if not kwargs.get('api_auth'):
        #    if time.time() - kwargs.auth_time > 599:
        #        kwargs = api_auth_function(kwargs)
        #else: kwargs = api_auth_function(kwargs)
        if not kwargs.get('api_auth'): kwargs = api_auth_function(kwargs)
        #=====================================================
        # Setup API Parameters
        #=====================================================
        if 'get' == kwargs.method:
            if not kwargs.get('api_filter'):
                if re.search('(vlans|vsans|port.port_)', kwargs.qtype):
                    names = ", ".join(map(str, kwargs.names))
                else: names = "', '".join(kwargs.names).strip("', '")
                if re.search('(organization|resource_group)', kwargs.qtype):
                    api_filter = f"Name in ('{names}')"
                else: api_filter = f"Name in ('{names}') and Organization.Moid eq '{org_moid}'"
                if 'asset_target' == kwargs.qtype:
                    api_filter = f"TargetId in ('{names}')"
                elif 'wwnn_pool_leases' == kwargs.qtype:
                    api_filter = f"PoolPurpose eq 'WWNN' and AssignedToEntity.Moid in ('{names}')"
                elif 'port.port_channel_' in kwargs.qtype:
                    api_filter = f"PcId in ({names}) and PortPolicy.Moid eq '{kwargs.pmoid}'"
                elif 'port.port_modes' == kwargs.qtype:
                    api_filter = f"PortIdStart in ({names}) and PortPolicy.Moid eq '{kwargs.pmoid}'"
                elif 'port.port_role_' == kwargs.qtype:
                    api_filter = f"PortId in ({names}) and PortPolicy.Moid eq '{kwargs.pmoid}'"
                elif 'hcl_status' == kwargs.qtype:
                    api_filter = f"ManagedObject.Moid in ('{names}')"
                elif 'registered_device' == kwargs.qtype:
                    api_filter = f"Moid in ('{names}')"
                elif 'reservations' == kwargs.qtype:
                    api_filter = f"Identity in ('{names}') and Pool.Moid eq '{kwargs.pmoid}'"
                elif 'serial_number' == kwargs.qtype:
                    api_filter = f"Serial in ('{names}')"
                elif 'switch' == kwargs.qtype:
                    api_filter = f"Name in ('{names}') and SwitchClusterProfile.Moid eq '{kwargs.pmoid}'"
                elif re.search('^vhbas|san_connectivity.vhbas$', kwargs.qtype):
                    api_filter = f"Name in ('{names}') and SanConnectivityPolicy.Moid eq '{kwargs.pmoid}'"
                elif re.search('vlans|vlan.vlans', kwargs.qtype):
                    api_filter = f"VlanId in ({names}) and EthNetworkPolicy.Moid eq '{kwargs.pmoid}'"
                elif 'user_role' == kwargs.qtype:
                    api_filter = f"Name in ('{names}') and Type eq 'IMC'"
                elif re.search('^vnics|lan_connectivity.vnics$', kwargs.qtype):
                    api_filter = f"Name in ('{names}') and LanConnectivityPolicy.Moid eq '{kwargs.pmoid}'"
                elif re.search('^vsans|vsan.vsans$', kwargs.qtype):
                    api_filter = f"VsanId in ({names}) and FcNetworkPolicy.Moid eq '{kwargs.pmoid}'"
                elif 'wwnn_pool_leases' == kwargs.qtype:
                    api_filter = f"PoolPurpose eq 'WWNN' and AssignedToEntity.Moid in ('{names}')"
                elif re.search('ww(n|p)n', kwargs.qtype):
                    api_filter = api_filter + f" and PoolPurpose eq '{kwargs.qtype.upper()}'"
                if kwargs.top1000 == True and len(kwargs.api_filter) > 0:
                    api_args = f'?$filter={kwargs.api_filter}&$top=1000'
                elif kwargs.top1000 == True: api_args = '?$top=1000'
                elif api_filter == '': ''
                else: api_args = f'?$filter={api_filter}'
            elif kwargs.api_filter == 'ignore': api_args=''
            else: api_args = f'?$filter={kwargs.api_filter}'
        else: api_args = ''

        #=====================================================
        # Perform the apiCall
        #=====================================================
        api_auth=kwargs.api_auth
        moid    = kwargs.pmoid
        payload = kwargs.apiBody
        retries = 3
        uri     = kwargs.uri
        url     = kwargs.args.url

        for i in range(retries):
            try:
                if 'get_by_moid' in kwargs.method:
                    response=  requests.get(f'{url}/api/v1/{uri}/{moid}', auth=api_auth)
                elif 'get' in kwargs.method:
                    response=  requests.get(f'{url}/api/v1/{uri}{api_args}', auth=api_auth)
                elif 'patch' in kwargs.method:
                    response=requests.patch(f'{url}/api/v1/{uri}/{moid}', auth=api_auth, json=payload)
                elif 'post' in kwargs.method:
                    response= requests.post(f'{url}/api/v1/{uri}', auth=api_auth, json=payload)
                status = response

                def send_error():
                    prRed(json.dumps(kwargs.apiBody, indent=4))
                    prRed(kwargs.apiBody)
                    prRed(f'!!! ERROR !!!')
                    if kwargs.method == 'get_by_moid': prRed(f'  URL: {url}/api/v1/{uri}/{moid}')
                    elif kwargs.method ==       'get': prRed(f'  URL: {url}/api/v1/{uri}{api_args}')
                    elif kwargs.method ==     'patch': prRed(f'  URL: {url}/api/v1/{uri}/{moid}')
                    elif kwargs.method ==      'post': prRed(f'  URL: {url}/api/v1/{uri}')
                    prRed(f'  Running Process: {kwargs.method} {kwargs.qtype}')
                    prRed(f'    Error status is {status}')
                    for k, v in (response.json()).items():
                        prRed(f"    {k} is '{v}'")
                    sys.exit(1)
                if re.search('40[0|3]', str(status)):
                    retry_action = False
                    for k, v in (response.json()).items():
                        if 'user_action_is_not_allowed' in v: retry_action = True
                        elif 'policy_attached_to_multiple_profiles_cannot_be_edited' in v: retry_action = True
                    if i < retries -1 and retry_action == True:
                        prPurple('     **NOTICE** Profile in Validating State.  Sleeping for 45 Seconds and Retrying.')
                        time.sleep(45)
                        continue
                    else: send_error()

                elif not re.search('(20[0-9])', str(status)): send_error()
                api_results = DotMap(response.json())
            except requests.HTTPError as e:
                if re.search('Your token has expired', str(e)) or re.search('Not Found', str(e)):
                    kwargs.results = False
                    return kwargs
                elif re.search('user_action_is_not_allowed', str(e)):
                    if i < retries -1:
                        time.sleep(45)
                        continue
                    else: raise
                elif re.search('There is an upgrade already running', str(e)):
                    kwargs.running = True
                    return kwargs
                else:
                    prRed(f"Exception when calling {kwargs.uri}: {e}\n")
                    sys.exit(1)
            break
        #=====================================================
        # Print Debug Information if Turned on
        #=====================================================
        api_results = DotMap(response.json())
        if int(debug_level) >= 1:
            prCyan(response)
        if int(debug_level)>= 5:
            if kwargs.method == 'get_by_moid': prCyan(f'  URL: {url}/api/v1/{uri}/{moid}')
            elif kwargs.method ==       'get': prCyan(f'  URL: {url}/api/v1/{uri}{api_args}')
            elif kwargs.method ==     'patch': prCyan(f'  URL: {url}/api/v1/{uri}/{moid}')
            elif kwargs.method ==      'post': prCyan(f'  URL: {url}/api/v1/{uri}')
        if int(debug_level) >= 6:
            prCyan(api_results)
        if int(debug_level) == 7:
            prCyan(json.dumps(payload, indent=4))
            prCyan(payload)
        #=====================================================
        # Gather Results from the apiCall
        #=====================================================
        if 'post' in kwargs.method:
            if kwargs.qtype == 'bulk':
                kwargs.pmoid = api_results.Responses[0].Body.Moid
            else: kwargs.pmoid = api_results.Moid
        elif 'inventory' in kwargs.uri: icount = 0
        else:
            if not kwargs.get('build_skip'):
                kwargs.pmoids = build_pmoid_dictionary(api_results, kwargs)
        if re.search('(patch|post)', kwargs.method):
            if kwargs.apiBody.get('name'):
                kwargs.pmoids[kwargs.apiBody['Name']] = kwargs.pmoid
        if 'get_by_moid' in kwargs.method: kwargs.results = api_results
        elif 'get' in kwargs.method: kwargs.results = api_results.Results
        elif re.search('(os_install|upgrade)', kwargs.qtype): kwargs.results = api_results
        elif re.search('(patch|post)', kwargs.method): kwargs.results = api_results
        #=====================================================
        # Print Progress Notifications
        #=====================================================
        if re.search('(patch|post)', kwargs.method):
            validating.completed_item(self.type, kwargs)
        #=====================================================
        # Return kwargs
        #=====================================================
        if kwargs.get('api_filter'): kwargs.pop('api_filter')
        if kwargs.get('build_skip'): kwargs.pop('build_skip')
        if kwargs.get('top1000'): kwargs.pop('top1000')
        return kwargs

    #=====================================================
    # Get Organizations from Intersight
    #=====================================================
    def all_organizations(self, kwargs):
        #=====================================================
        # Get Organization List from the API
        #=====================================================
        kwargs.api_filter= 'ignore'
        kwargs.method    = 'get'
        kwargs.qtype     = 'organization'
        kwargs.uri       = 'organization/Organizations'
        kwargs           = api(self.type).calls(kwargs)
        kwargs.org_moids = kwargs.pmoids
        return kwargs

    #=====================================================
    # Get Organizations from Intersight
    #=====================================================
    def organizations(self, kwargs):
        names = []
        for i in kwargs.orgs: names.append(i)
        kwargs.method   = 'get'
        kwargs.names    = names
        kwargs.qtype    = 'resource_group'
        kwargs.uri      = 'resource/Groups'
        kwargs          = api(kwargs.qtype).calls(kwargs)
        kwargs.rsg_moids= kwargs.pmoids
        #=====================================================
        # Get Organization List from the API
        #=====================================================
        kwargs.qtype    = 'organization'
        kwargs.uri      = 'organization/Organizations'
        kwargs          = api(self.type).calls(kwargs)
        kwargs.org_moids= kwargs.pmoids
        for org in kwargs.orgs:
            if not org in kwargs.rsg_moids:
                kwargs.apiBody={
                    'Description':f'{org} Resource Group',
                    'Name':org
                }
                kwargs.method= 'post'
                kwargs.uri   = 'resource/Groups'
                kwargs       = api(kwargs.qtype).calls(kwargs)
                kwargs.rsg_moids[org].moid     = kwargs.results.Moid
                kwargs.rsg_moids[org].selectors= kwargs.results.Selectors
            if not org in kwargs.org_moids:
                kwargs.apiBody={
                    'Description':f'{org} Organization',
                    'Name':org,
                    'ResourceGroups':[{
                        'Moid': kwargs.rsg_moids[org].moid,
                        'ObjectType': 'resource.Group'
                    }]
                }
                kwargs.method= 'post'
                kwargs.uri   = 'organization/Organizations'
                kwargs       = api(kwargs.qtype).calls(kwargs)
                kwargs.org_moids[org].moid = kwargs.results.Moid
        return kwargs

#=======================================================
# Policies Class
#=======================================================
class imm(object):
    def __init__(self, type):
        self.type = type

    #=======================================================
    # BIOS Policy Modification
    #=======================================================
    def bios(self, apiBody, item, kwargs):
        if apiBody.get('bios_template'):
            btemplate = kwargs.ezdata['bios.template'].properties
            if '-tpm' in apiBody['bios_template']:
                apiBody = dict(apiBody, **btemplate[item.bios_template.replace('-tpm', '')], **btemplate.tpm)
            else: apiBody = dict(apiBody, **btemplate[item.bios_template], **btemplate.tpm_disabled)
            apiBody.pop('bios_template')
        return apiBody

    #=======================================================
    # Boot Order Policy Modification
    #=======================================================
    def boot_order(self, apiBody, item, kwargs):
        ezdata = kwargs.ezdata['boot_order.boot_devices'].properties
        if item.get('boot_devices'):
            apiBody['BootDevices'] = []
            for i in item.boot_devices:
                boot_dev = {'Name':i.name,'ObjectType':i.object_type}
                if re.search('(Iscsi|LocalDisk|Nvme|PchStorage|San|SdCard)', i.object_type
                             ) and apiBody['ConfiguredBootMode'] == 'Uefi':
                    boot_dev['Bootloader'] = {'ObjectType':'boot.Bootloader'}
                    if 'bootloader' in i:
                        ez1 = kwargs.ezdata['boot_order.boot_devices.boot_loader'].properties
                        for k, v in i.items():
                            if k in ez1: boot_dev['Bootloader'].update({ez1[k].intersight_api:v})
                    else: boot_dev['Bootloader'].update({'Name':'BOOTx64.EFI','Path':"\\EFI\\BOOT\\"})
                for k, v in i.items():
                    if k in ezdata: boot_dev.update({ezdata[k].intersight_api:v})
                apiBody['BootDevices'].append(deepcopy(boot_dev))
        return apiBody

    #=======================================================
    # Ethernet Adapter Policy Modification
    #=======================================================
    def ethernet_adapter(self, apiBody, item, kwargs):
        if apiBody.get('adapter_template'):
            atemplate= kwargs.ezdata['ethernet_adapter.template'].properties
            apiBody  = dict(apiBody, **atemplate[item.adapter_template])
            apiBody.pop('adapter_template')
        return apiBody

    #=======================================================
    # Fibre-Channel Adapter Policy Modification
    #=======================================================
    def fibre_channel_adapter(self, apiBody, item, kwargs):
        if apiBody.get('adapter_template'):
            atemplate= kwargs.ezdata['fibre_channel_adapter.template'].properties
            apiBody  = dict(apiBody, **atemplate[item.adapter_template])
            apiBody.pop('adapter_template')
        return apiBody

    #=======================================================
    # Fibre-Channel Network Policies Policy Modification
    #=======================================================
    def firmware(self, apiBody, item, kwargs):
        item = item; kwargs = kwargs
        if apiBody.get('ExcludeComponentList'):
            exclude_components = list(apiBody['ExcludeComponentList'].keys())
            apiBody['ExcludeComponentList'] = exclude_components
        if apiBody.get('ModelBundleCombo'):
            combos = deepcopy(apiBody['ModelBundleCombo']); apiBody['ModelBundleCombo'] = []
            for e in combos:
                for i in e['ModelFamily']:
                    idict = deepcopy(e); idict['ModelFamily'] = i
                    apiBody['ModelBundleCombo'].append(idict)
        # Return apiBody
        return apiBody

    #=======================================================
    # Identity Reservations
    #=======================================================
    def identity_reservations(self, reservations, kwargs):
        #=====================================================
        # Get Existing Reservations via the API
        #=====================================================
        reservations = DotMap(reservations)
        for k, v in reservations.items():
            kwargs.method = 'get'
            kwargs.names  = [e for e in v.reservations.Identity]
            kwargs.pmoid  = kwargs.pmoids[k].moid
            kwargs.qtype  = 'reservations'
            kwargs.uri    = kwargs.ezdata[f'{self.type}.reservations'].intersight_uri
            kwargs        = api(kwargs.qtype).calls(kwargs)
            reserve_moids = kwargs.pmoids

            #=====================================================
            # Construct apiBody Payload
            #=====================================================
            apiBody = {}
            for e in v.reservations.identities:
                for a, b in v.reservations.items():
                    if not 'Identity' == a: apiBody.update({a:b})
                apiBody.update({'Identity':e,'Pool':{'Moid':kwargs.pmoids[k].moid,'ObjectType':v.object_type}})
                apiBody = org_map(apiBody)
                kwargs.apiBody = apiBody
                kwargs.method = 'post'

                #=====================================================
                # Create/Patch the Pool via the Intersight API
                #=====================================================
                kwargs.apiBody = apiBody
                if not reserve_moids.get(apiBody['Identity']):
                    kwargs.method = 'post'
                    kwargs = api(kwargs.qtype).calls(kwargs)

        # Return kwargs
        return kwargs

    #=======================================================
    # IMC Access Policy Modification
    #=======================================================
    def imc_access(self, apiBody, item, kwargs):
        item = item
        if not apiBody.get('AddressType'): apiBody.update({ 'AddressType':{ 'EnableIpV4':False, 'EnableIpV6':False }})
        apiBody.update({ 'ConfigurationType':{ 'ConfigureInband': False, 'ConfigureOutOfBand': False }})
        #=====================================================
        # Attach Pools to the API Body
        #=====================================================
        names = []; ptype = ['InbandIpPool', 'OutOfBandIpPool']
        for i in ptype:
            if apiBody.get(i):
                names.append(apiBody[i]['Moid'])
                apiBody['ConfigurationType'][f'Configure{i.split("Ip")[0]}'] = True
        kwargs = api_get(False, names, 'ip', kwargs)
        for i in ptype:
            if apiBody.get(i):
                if not kwargs.pmoids.get(apiBody[i]['Moid']):
                    validating.error_policy_doesnt_exist(i, apiBody[i]['Moid'], self.type, 'policy', apiBody['Name'])
                if len(kwargs.pmoids[apiBody[i]['Moid']].ipv4_config.Gateway) > 0: apiBody['AddressType']['EnableIpV4'] = True
                if len(kwargs.pmoids[apiBody[i]['Moid']].ipv6_config.Gateway) > 0: apiBody['AddressType']['EnableIpV6'] = True
                apiBody[i]['Moid'] = kwargs.pmoids[apiBody[i]['Moid']].moid
        return apiBody

    #=======================================================
    # IPMI over LAN Policy Modification
    #=======================================================
    def ipmi_over_lan(self, apiBody, item, kwargs):
        item = item; kwargs = kwargs
        if apiBody.get('encryption_key'):
            if os.environ.get('ipmi_key') == None:
                kwargs.sensitive_var = f"ipmi_key"
                kwargs = ezfunctions.sensitive_var_value(kwargs)
            apiBody.update({'EncryptionKey':kwargs['var_value']})
            apiBody.update({'EncryptionKey':os.environ.get('ipmi_key')})
        return apiBody

    #=======================================================
    # iSCSI Adapter Policy Modification
    #=======================================================
    def iscsi_boot(self, apiBody, item, kwargs):
        item = item
        if apiBody.get('InitiatorStaticIpV4Config'):
            apiBody['InitiatorStaticIpV4Address'] = apiBody['InitiatorStaticIpV4Config']['IpAddress']
            apiBody['InitiatorStaticIpV4Config'].pop('IpAddress')
        if apiBody.get('Chap'):
            kwargs.sensitive_var = 'iscsi_boot_password'
            kwargs = ezfunctions.sensitive_var_value(kwargs)
            if apiBody['authentication'] == 'mutual_chap':
                apiBody['MutualChap'] = apiBody['Chap']; apiBody.pop('Chap')
                apiBody['MutualChap']['Password'] = kwargs.var_value
            else: apiBody['Chap']['Password'] = kwargs.var_value
        #=====================================================
        # Attach Pools to the API Body
        #=====================================================
        if apiBody.get('InitiatorIpPool'):
            ip_pool = apiBody['InitiatorIpPool']['Moid']
            kwargs = api_get(False, [ip_pool], 'ip', kwargs)
            apiBody['InitiatorIpPool']['Moid'] = kwargs.pmoids[ip_pool].moid
        plist = ['PrimaryTargetPolicy', 'SecondaryTargetPolicy']
        names = []
        for p in plist:
            if apiBody.get(p): names.append(apiBody[p]['Moid'])
        if len(kwargs.names) > 0: kwargs = api_get(False, names, 'iscsi_static_target', kwargs)
        for p in plist:
            if apiBody.get(p): apiBody[p]['Moid'] = kwargs.pmoids[apiBody[p]['Moid']].moid
        return apiBody

    #=======================================================
    # iSCSI Adapter Policy Modification
    #=======================================================
    def iscsi_static_target(self, apiBody, item, kwargs):
        item = item; kwargs = kwargs
        apiBody['Lun'] = {'Bootable':True}
        return apiBody

    #=======================================================
    # LAN Connectivity Policy Modification
    #=======================================================
    def lan_connectivity(self, apiBody, item, kwargs):
        if not apiBody.get('PlacementMode'): apiBody.update({'PlacementMode':'custom'})
        if not apiBody.get('TargetPlatform'): apiBody.update({'TargetPlatform': 'FIAttached'})
        if item.get('IqnPool'):
            apiBody['IqnAllocationType'] = 'Pool'
            kwargs = api_get(False, [item.iqn_pool], 'iqn', kwargs)
            apiBody['IqnPool']['Moid'] = kwargs.pmoids[item.iqn_pool].moid
        return apiBody

    #=======================================================
    # Local User Policy Modification
    #=======================================================
    def local_user(self, apiBody, item, kwargs):
        if not apiBody.get('PasswordProperties'): apiBody['PasswordProperties'] = {}
        for k, v in kwargs.ezdata['local_user.password_properties'].properties.items():
            if item.get('password_properties'):
                if item.password_properties.get(k):
                    apiBody['PasswordProperties'][v.intersight_api] =  item.password_properties[k]
                else: apiBody['PasswordProperties'][v.intersight_api] = v.default
            else: apiBody['PasswordProperties'][v.intersight_api] = v.default
        return apiBody

    #=======================================================
    # Network Connectivity Policy Modification
    #=======================================================
    def network_connectivity(self, apiBody, item, kwargs):
        dns_list = ['v4', 'v6']; kwargs = kwargs
        for i in dns_list:
            dtype = f'dns_servers_{i}'
            if dtype in apiBody:
                if len(item[dtype])  > 0: apiBody.update({f'PreferredIp{i}dnsServer':item[dtype][0]})
                if len(item[dtype]) == 2: apiBody.update({f'AlternateIp{i}dnsServer':item[dtype][1]})
                apiBody.pop(dtype)

        # Return apiBody
        return apiBody

    #=====================================================
    #  Policies Function
    #=====================================================
    def policies(self, kwargs):
        #=====================================================
        # Load Variables and Send Begin Notification
        #=====================================================
        idata = DotMap(dict(pair for d in kwargs.ezdata[self.type].allOf for pair in d.properties.items()))
        pdict = deepcopy(kwargs.imm_dict.orgs[kwargs.org].policies[self.type])
        if self.type == 'port': policies = list({v['names'][0]:v for v in pdict}.values())
        else: policies = list({v['name']:v for v in pdict}.values())
        validating.begin_section(self.type, 'policies')
        #=====================================================
        # Get Existing Policies
        #=====================================================
        names = []
        for i in policies:
            if self.type == 'port': names.extend([i.names[x] for x in range(0,len(i.names))])
            else: names.append(i['name'])
        kwargs = api_get(True, names, self.type, kwargs)
        policy_moids = kwargs.pmoids

        #=====================================================
        # Create/Patch the Policy via the Intersight API
        #=====================================================
        def policies_to_api(apiBody, kwargs):
            kwargs.apiBody= apiBody
            kwargs.qtype  = self.type
            kwargs.uri    = kwargs.ezdata[self.type].intersight_uri
            if policy_moids.get(apiBody['Name']):
                kwargs.method= 'patch'
                kwargs.pmoid = policy_moids[apiBody['Name']].moid
            else: kwargs.method= 'post'
            kwargs       = api(self.type).calls(kwargs)
            kwargs.pmoid = kwargs.pmoid
            return kwargs

        #=====================================================
        # Loop through Items
        #=====================================================
        for item in policies:
            if self.type == 'port':
                names = item.names; item.pop('names')
                for x in range(0,len(names)):
                    #=====================================================
                    # Construct apiBody Payload
                    #=====================================================
                    apiBody = {'Name':names[x],'ObjectType':kwargs.ezdata[self.type].ObjectType}
                    apiBody = build_apiBody(apiBody, idata, item, self.type, kwargs)
                    #kwargs = policies_to_api(apiBody, kwargs)
            else:
                #=====================================================
                # Construct apiBody Payload
                #=====================================================
                apiBody = {'ObjectType':kwargs.ezdata[self.type].ObjectType}
                apiBody = build_apiBody(apiBody, idata, item, self.type, kwargs)
                #kwargs = policies_to_api(apiBody, kwargs)
        #=====================================================
        # Loop Thru Sub-Items
        #=====================================================
        pdict = deepcopy(kwargs.imm_dict.orgs[kwargs.org].policies[self.type])
        if self.type == 'port': kwargs.policies = list({v['names'][0]:v for v in pdict}.values())
        else: kwargs.policies = list({v['name']:v for v in pdict}.values())
        kwargs.policy_moids = policy_moids
        sub_list = ['lan_connectivity.vnics', 'local_user.users', 'san_connectivity.vhbas',
                        'storage.drive_groups', 'vlan.vlans', 'vsan.vsans']
        for e in sub_list:
            a, b = e.split('.')
            #a = e.split('.')[0]; b = e.split('.')[1]
            if a == self.type: kwargs = eval(f'imm(e).sub_policy(kwargs)')
        if 'port' == self.type:
            kwargs = imm('port.port_modes').port_modes(kwargs)
            kwargs = imm('ports').ports(kwargs)
        #=====================================================
        # Send End Notification and return kwargs
        #=====================================================
        validating.end_section(self.type, 'policies')
        return kwargs

    #=====================================================
    #  Pools Function
    #=====================================================
    def pools(self, kwargs):
        reservations = DotMap()
        #=====================================================
        # Load Variables and Send Begin Notification
        #=====================================================
        idata = DotMap(dict(pair for d in kwargs.ezdata[self.type].allOf for pair in d.properties.items()))
        pools = list({v['name']:v for v in kwargs.imm_dict.orgs[kwargs.org].pools[self.type]}.values())
        validating.begin_section(self.type, 'pool')
        #=====================================================
        # Get Existing Pools
        #=====================================================
        kwargs = api_get(True, [e.name for e in pools], self.type, kwargs)
        pool_moids= kwargs.pmoids
        #=====================================================
        # Loop through Items
        #=====================================================
        for item in pools:
            #=====================================================
            # Construct apiBody Payload
            #=====================================================
            apiBody = {'ObjectType':idata.ObjectType}
            apiBody = build_apiBody(apiBody, idata, item, self.type, kwargs)

            #=====================================================
            # Add Pool Specific Attributes
            #=====================================================
            if re.search('ww(n|p)n', self.type):  apiBody.update({'PoolPurpose':self.type.upper()})

            #=====================================================
            # If Reservations Pop Reservations and Save
            #=====================================================
            if apiBody.get('reservations'):
                reservations[apiBody['Name']].reservations= apiBody['reservations']
                reservations[apiBody['Name']].object_type = kwargs.ezdata[self.type].ObjectType
                apiBody.pop('reservations')

            #=====================================================
            # Create/Patch the Pool via the Intersight API
            #=====================================================
            kwargs.apiBody = apiBody
            if pool_moids.get(apiBody['Name']):
                kwargs.method = 'patch'
                kwargs.pmoid  = pool_moids[apiBody['Name']].moid
            else: kwargs.method = 'post'
            kwargs = api(self.type).calls(kwargs)
            kwargs.pmoids[apiBody['Name']].moid = kwargs.pmoid

        #=====================================================
        # Configure Reservations
        #=====================================================
        if len(reservations) > 0: kwargs = imm.identity_reservations(reservations, kwargs)

        #=====================================================
        # Send End Notification and return kwargs
        #=====================================================
        validating.end_section(self.type, 'pool')
        return kwargs

    #=====================================================
    # Port Modes for Port Policies
    #=====================================================
    def port_modes(self, kwargs):
        #=====================================================
        # Loop Through Port Modes
        #=====================================================
        ezdata= kwargs.ezdata[self.type]
        p     = self.type.split('.')
        for item in kwargs.policies:
            if item.get(p[1]):
                for x in range(0,len(item['names'])):
                    kwargs.port_policy[item['names'][x]].names = []
                    for e in item[p[1]]: kwargs.port_policy[item['names'][x]].names.append(e.port_list[0])
                for i in list(kwargs.port_policy.keys()):
                    kwargs.pmoid = kwargs.policy_moids[i].moid
                    kwargs = api_get(True, kwargs.port_policy[i].names, self.type, kwargs)
                    kwargs.port_modes[i] = kwargs.pmoids
                    parent_moid = kwargs.policy_moids[i].moid
                    for e in item[p[1]]:
                        kwargs.apiBody = {
                            'CustomMode':e.custom_mode,'ObjectType':ezdata.ObjectType,
                            'PortIdStart':e.port_list[0],'PortIdEnd':e.port_list[1],
                            ezdata.parent_policy:{'Moid':parent_moid,'ObjectType':ezdata.parent_object}}
                        if e.get('slot_id'): kwargs.apiBody.update({'SlotId':e.slot_id})
                        else: kwargs.apiBody.update({'SlotId':1})
                        #=====================================================
                        # Create or Patch the Policy via the Intersight API
                        #=====================================================
                        kwargs.port_policy_name= kwargs.item['names'][x]
                        if kwargs.pmoids.get(parent_moid):
                            if kwargs.pmoids[parent_moid].get(e.port_list[0]):
                                kwargs.method= 'patch'
                                kwargs.pmoid = kwargs.pmoids[parent_moid][e.port_list[0]].moid
                            else: kwargs.method= 'post'
                        else: kwargs.method= 'post'
                        kwargs = api(kwargs.qtype).calls(kwargs)
        return kwargs

    #=====================================================
    # Assign Port Types to Port Policies
    #=====================================================
    def ports(self, kwargs):
        #=====================================================
        # Create/Patch the Port Policy Port Types
        #=====================================================
        def api_calls(port_type, kwargs):
            #=====================================================
            # Create or Patch the Policy via the Intersight API
            #=====================================================
            if re.search('port_channel', port_type): name = int(kwargs.apiBody['PcId'])
            else: name = int(kwargs.apiBody['PortId'])
            if kwargs.port_moids[port_type].get(kwargs.parent_moid):
                if kwargs.port_moids[kwargs.type][kwargs.parent_moid].get(name):
                    kwargs.method= 'patch'
                    kwargs.pmoid = kwargs.moids[port_type][kwargs.parent_moid][name].moid
                else: kwargs.method= 'post'
            else: kwargs.method= 'post'
            kwargs.qtype  = f'port.{port_type}'
            kwargs        = api(kwargs.type).calls(kwargs)
            return kwargs
        
        #=====================================================
        # Check if the Port Policy Port Type Exists
        #=====================================================
        def get_ports(port_type, item, x, kwargs):
            names = []
            for i in item[port_type]:
                if re.search('port_channel', port_type):
                    if len(i.pc_ids) == 2: names.append(int(i.pc_ids[x]))
                    else: names.append(int(i.pc_ids[0]))
                else:
                    for e in ezfunctions.vlan_list_full(i.port_list): names.append(e)
            kwargs.pmoid = kwargs.parent_moid
            kwargs = api_get(True, names, f'port.{port_type}', kwargs)
            kwargs.port_moids[port_type] = kwargs.pmoids
            return kwargs

        #=====================================================
        # Attach Ethernet/Flow/Link Policies
        #=====================================================
        def policy_update(kwargs):
            plist = ['EthNetworkControl', 'EthNetworkGroup', 'FlowControl', 'LinkAggregation', 'LinkControl']
            for p in plist:
                p = f'{p}Policy'
                if kwargs.apiBody.get(p):
                    kwargs.apiBody[p]['Moid'] = kwargs.cp[snakecase(p).replace('eth_', 'ethernet_')].moids[kwargs.apiBody[p]['Moid']].moid
                    if 'Group' in p: kwargs.apiBody[p] = [kwargs.apiBody[p]]
            return kwargs
        
        #=====================================================
        # Create API Body for Port Policies
        #=====================================================
        def port_type_call(port_type, item, x, kwargs):
            idata = kwargs.ezdata[f'port.{port_type}'].properties
            for i in item[port_type]:
                apiBody = {'PortPolicy':{'Moid':kwargs.parent_moid,'ObjectType':'fabric.PortPolicy'}}
                kwargs.apiBody = build_apiBody(apiBody, idata, i, f'port.{port_type}', kwargs)
                if i.get('pc_ids'):
                    if len(kwargs.apiBody['PcId']) == 2: kwargs.apiBody['PcId'] = i.pc_ids[x]
                    else: kwargs.apiBody['PcId'] = i.pc_ids[x]
                    if re.search('appliance|ethernet|fcoe', port_type): kwargs = policy_update(kwargs)
                if i.get('vsan_ids'):
                    if len(i['vsan_ids']) > 1: kwargs.apiBody['VsanId'] = i['vsan_ids'][x]
                    else: kwargs.apiBody['VsanId'] = i['vsan_ids'][0]
                kwargs.apiBody.pop('Organization')
                kwargs.apiBody.pop('Tags')
                if re.search('port_channel', port_type):
                    print('hello')
                    #kwargs = api_calls(port_type, kwargs)
                elif re.search('role', port_type):
                    for e in ezfunctions.vlan_list_full(i.port_list):
                        kwargs.apiBody['PortId'] = e
                        #kwargs = api_calls(port_type, kwargs)
            return kwargs

        #=====================================================
        # Get Policies
        #=====================================================
        kwargs.port_types = []
        kwargs.ports      = []
        for k,v in kwargs.ezdata.port.allOf[0].properties.items():
            if re.search('^port_(cha|rol)', k):
                kwargs.port_types.append(k)
                for a,b in v['items'].properties.items():
                    if re.search('^(ethernet|flow|link)_', a):
                        if not kwargs.cp.get(a): kwargs.cp[a].names = []
        for e in kwargs.port_types:
            kwargs.port_type[e].names = []
            for item in kwargs.policies:
                if item.get(e):
                    kwargs.ports.append(e)
                    for i in item[e]:
                        if 'port_channel' in e: kwargs.port_type[e].names.extend(i.pc_ids)
                        for c in list(kwargs.cp.keys()):
                            if i.get(c):
                                if type(i[c]) == list: kwargs.cp[c].names.extend(i[c])
                                else: kwargs.cp[c].names.append(i[c])
        kwargs.ports = list(numpy.unique(numpy.array(kwargs.ports)))
        if kwargs.cp.get('ethernet_network_group_policies'):
            if kwargs.cp.get('ethernet_network_group_policy'):
                kwargs.cp.ethernet_network_group_policy.names.extend(kwargs.cp.ethernet_network_group_policies.names)
            else: kwargs.cp.ethernet_network_group_policy.names = kwargs.cp.ethernet_network_group_policies.names
            kwargs.cp.pop('ethernet_network_group_policies')
        for e in list(kwargs.cp.keys()):
            names  = list(numpy.unique(numpy.array(kwargs.cp[e].names)))
            if len(names) > 0:
                kwargs = api_get(False, names, e.replace('_policy', ''), kwargs)
                kwargs.cp[e].moids = kwargs.pmoids
        #=====================================================
        # Create API Body for Port Types
        #=====================================================
        for item in kwargs.policies:
            for x in range(0,len(item['names'])):
                for e in kwargs.ports:
                    if item.get(e):
                        kwargs.parent_name = item['names'][x]
                        kwargs.parent_moid = kwargs.policy_moids[item['names'][x]].moid
                        kwargs = get_ports(e, item, x, kwargs)
                        port_type_call(e, item, x, kwargs)
        return kwargs

    #=======================================================
    # SAN Connectivity Policy Modification
    #=======================================================
    def san_connectivity(self, apiBody, item, kwargs):
        kwargs.uri = kwargs.ezdata.wwnn.intersight_uri
        if not apiBody.get('PlacementMode'): apiBody.update({'PlacementMode':'custom'})
        if item.get('wwnn_pool'):
            kwargs = api_get(False, [item.wwnn_pool], 'wwnn', kwargs)
            apiBody['WwnnPool']['Moid'] = kwargs.pmoids[item.wwnn_pool].moid
        return apiBody

    #=======================================================
    # SNMP Policy Modification
    #=======================================================
    def snmp(self, apiBody, item, kwargs):
        item = item
        if apiBody.get('SnmpTraps'):
            for x in range(len(apiBody['SnmpTraps'])):
                if apiBody['SnmpTraps'][x].get('Community'):
                    kwargs.sensitive_var = f"snmp_trap_community_{apiBody['SnmpTraps'][x]['Community']}"
                    kwargs = ezfunctions.sensitive_var_value(kwargs)
                    apiBody['SnmpTraps'][x]['Community'] = kwargs.var_value
        if apiBody.get('SnmpUsers'):
            for x in range(len(apiBody['SnmpUsers'])):
                if apiBody['SnmpUsers'][x].get('AuthPassword'):
                    kwargs.sensitive_var = f"snmp_auth_password_{apiBody['SnmpUsers'][x]['AuthPassword']}"
                    kwargs = ezfunctions.sensitive_var_value(kwargs)
                    apiBody['SnmpUsers'][x]['AuthPassword'] = kwargs.var_value
                if apiBody['SnmpUsers'][x].get('PrivacyPassword'):
                    kwargs.sensitive_var = f"snmp_privacy_password_{apiBody['SnmpUsers'][x]['PrivacyPassword']}"
                    kwargs = ezfunctions.sensitive_var_value(kwargs)
                    apiBody['SnmpUsers'][x]['PrivacyPassword'] = kwargs.var_value
        # Return apiBody
        return apiBody

    #=======================================================
    # Storage Policy Modification
    #=======================================================
    def storage(self, apiBody, item, kwargs):
        item = item; kwargs = kwargs
        if apiBody.get('M2VirtualDrive'): apiBody['M2VirtualDrive']['Enable'] = True
        if apiBody.get('Raid0Drive'):
            apiBody['Raid0Drive']['Enable'] = True
            if not apiBody['Raid0Drive'].get('VirtualDrivePolicy'):
                apiBody['Raid0Drive']['VirtualDrivePolicy'] = {'ObjectType':'storage.VirtualDrivePolicy'}
                for k,v in kwargs.ezdata['storage.virtual_drive_policy'].properties.items():
                    if item.get(k): apiBody['Raid0Drive']['VirtualDrivePolicy'][v.intersight_api] = item[k]
                    else: apiBody['Raid0Drive']['VirtualDrivePolicy'][v.intersight_api] = v.default
        return apiBody

    #=====================================================
    # Assign Drive Groups to Storage Policies
    #=====================================================
    def storage_drive_groups(self, kwargs):
        jsonVars = kwargs.ezdata.policies.allOf[1].properties.storage.virtual_drive_map
        #=====================================================
        # Get Storage Policies
        #=====================================================
        kwargs.method = 'get'
        kwargs.names = []
        kwargs.qtype = 'storage_drive_group'
        for i in kwargs.item: kwargs.names.append(i.name)
        kwargs = api('storage_drive_group').calls(kwargs)
        dg_moids = kwargs.pmoids
        #=====================================================
        # Create API Body for Storage Drive Groups
        #=====================================================
        for i in kwargs.item:
            #=====================================================
            # Create API Body for VLANs
            #=====================================================
            apiBody = {
                'Name':i.name,
                'ObjectType':'storage.DriveGroup', 'RaidLevel':i.raid_level
                }
            apiBody.update({'storage_policy':{
                'Moid':kwargs.pmoid,'ObjectType':'storage.StoragePolicy'
            }})
            if i.get('manual_drive_group'):
                apiBody['ManualDriveGroup'] = {'ObjectType':'storage.ManualDriveGroup'}
                if i['manual_drive_group'][0].get('dedicated_hot_spares'):
                    apiBody['ManualDriveGroup']['DedicatedHotSpares'] = i[
                        'manual_drive_group']['dedicated_hot_spares']
                apiBody['ManualDriveGroup']['SpanGroups'] = []
                for x in i.manual_drive_group[0].drive_array_spans:
                    apiBody['ManualDriveGroup']['SpanGroups'].append({
                        'ObjectType':'storage.SpanDrives','Slots':x['slots']
                    })
            jvars = jsonVars.virtual_drive_map
            if i.get('virtual_drives'):
                apiBody['VirtualDrives'] = []
                for x in i.virtual_drives:
                    vdBody = {}
                    for k, v in x.items():
                        if k in jvars: vdBody.update({jvars[k]:v})
                    vdBody.update({'ObjectType':'storage.VirtualDriveConfiguration'})
                    if vdBody.get('VirtualDrivePolicy'):
                        vdBody['virtual_drive_policy'].update({'ObjectType':'storage.VirtualDrivePolicy'})
                    apiBody['VirtualDrives'].append(vdBody)
            #=====================================================
            # Create or Patch the Policy via the Intersight API
            #=====================================================
            if dg_moids.get(i.name):
                kwargs.method= 'patch'
                kwargs.pmoid = dg_moids[i.name].moid
            else: kwargs.method = 'post'
            kwargs.apiBody= apiBody
            kwargs.qtype  = 'storage_drive_group'
            kwargs.uri    = jsonVars.uri_drive_group
            kwargs        = api(kwargs.qtype).calls(kwargs)
        return kwargs

    #=======================================================
    # System QoS Policy Modification
    #=======================================================
    def system_qos(self, apiBody, item, kwargs):
        item = item
        if apiBody.get('configure_recommended_classes'):
            if apiBody['configure_recommended_classes'] == True:
                apiBody.pop('configure_recommended_classes')
                apiBody['Classes'] = kwargs.ezdata['system_qos.classes_recommended'].classes
        if apiBody.get('configure_default_policy'):
            if apiBody['configure_default_policy'] == True:
                apiBody.pop('configure_default_policy')
                apiBody['Classes'] = kwargs.ezdata['system_qos.classes_default'].classes
        elif apiBody.get('configure_recommended_classes') == None and len(apiBody.get('Classes')) == 0:
            apiBody['Classes'] = kwargs.ezdata['system_qos.classes_default'].classes
        if apiBody.get('jumbo_mtu'):
            if apiBody['jumbo_mtu'] == False:
                for x in range(apiBody['Classes']):
                    if not apiBody['Classes'][x]['Name'] == 'FC': apiBody['Classes'][x]['Mtu'] = 1500
        return apiBody

    #=====================================================
    # Assign Users to Local User Policies
    #=====================================================
    def users(self, kwargs):
        #=====================================================
        # Get Existing Users
        #=====================================================
        jsonVars = kwargs.ezdata.policies.allOf[1].properties.local_user
        kwargs.method= 'get'
        kwargs.names = []
        kwargs.qtype = 'local_users'
        kwargs.uri   = jsonVars.uri_users
        for i in kwargs.item: kwargs.names.append(i['username'])
        kwargs       = api('local_users').calls(kwargs)
        user_moids   = kwargs.pmoids
        kwargs.names = []
        for i in kwargs.item: kwargs.names.append(i['role'])
        rnames           = "', '".join(kwargs.names).strip("', '")
        kwargs.api_filter= f"Name in ('{rnames}') and Type eq 'IMC'"
        kwargs.qtype     = 'iam_role'
        kwargs.uri       = jsonVars.uri_iam_role
        kwargs = api(kwargs.qtype).calls(kwargs)
        role_moids  = kwargs.pmoids
        kwargs.names= []
        umoids      = []
        for k, v in user_moids.items(): umoids.append(v.moid)
        umoids = "', '".join(umoids).strip("', '")
        kwargs.api_filter= f"EndPointUser.Moid in ('{umoids}')"
        kwargs.qtype     = 'user_role'
        kwargs.uri       = jsonVars.uri_user_role
        kwargs = api('user_role').calls(kwargs)
        urole_moids    = kwargs.pmoids
        local_user_moid= kwargs.pmoid
        #=====================================================
        # Construct API Body Users
        #=====================================================
        for i in kwargs.item:
            apiBody = {'Name':i['username']}
            apiBody = org_map(apiBody, kwargs.org_moid)
            kwargs.sensitive_var = f"local_user_password_{i['password']}"
            kwargs = ezfunctions.sensitive_var_value(kwargs)
            kwargs.apiBody= apiBody
            kwargs.qtype  = 'local_users'
            kwargs.uri    = jsonVars.uri_users
            if not user_moids.get(i['username']):
                kwargs.method= 'post'
                kwargs       = api(self.type).calls(kwargs)
                user_moid    = kwargs.pmoid
            else: user_moid = user_moids[i['username']].moid
            #=====================================================
            # Create API Body for User Role
            #=====================================================
            if i.get('enabled'): apiBody = {'Enabled':i['enabled']}
            else: apiBody = {}
            apiBody['Password'] = kwargs['var_value']
            apiBody.update({'EndPointRole':[{'Moid':role_moids[i['role']].moid,'ObjectType':'iam.EndPointRole'}]})
            apiBody.update({'EndPointUser':{'Moid':user_moid,'ObjectType':'iam.EndPointUser'}})
            apiBody.update({'EndPointUserPolicy':{'Moid':local_user_moid,'ObjectType':'iam.EndPointUserPolicy'}})
            #=====================================================
            # Create or Patch the Policy via the Intersight API
            #=====================================================
            if not urole_moids.get(user_moid): kwargs.method = 'post'
            else:
                kwargs.method= 'patch'
                kwargs.pmoid = urole_moids[user_moid].moid
            kwargs.apiBody= apiBody
            kwargs.qtype  = i['username']
            kwargs.uri    = jsonVars.uri_user_role
            kwargs = api('user_role').calls(kwargs)
        return kwargs

    #=====================================================
    # Assign VNICs to LAN Connectivity Policies
    #=====================================================
    def vhbas(self, kwargs):
        jsonVars = kwargs.ezdata.policies.allOf[1].properties[self.type]
        #=====================================================
        # Get Policies and Pools
        #=====================================================
        scp_moid = kwargs.pmoid
        kwargs.method = 'get'
        for p in jsonVars.policy_list:
            pshort = ((p.replace('_policy', '')).replace('_policies', '')).replace('_pools', '')
            kwargs.names  = []
            for i in kwargs.item:
                if i.get(p) and 'policy' in p: kwargs.names.append(i[p])
                elif p == 'vhbas': kwargs.names.extend(i['names'])
                elif i.get(p): kwargs.names.extend(i[p])
            kwargs.qtype = pshort
            if 'wwpn' in p:
                kwargs.uri = kwargs.ezdata.pools.allOf[1].properties.fc.uri
            else: kwargs.uri = kwargs.ezdata.policies.allOf[1].properties[pshort].uri
            kwargs.names   = numpy.unique(numpy.array(kwargs.names))
            kwargs         = api(pshort).calls(kwargs)
            kwargs.moids[p]= kwargs.pmoids

        #=====================================================
        # Create API Body for VNICs
        #=====================================================
        policy_list = deepcopy(jsonVars.policy_list)
        remove_list = ['vhbas', 'wwpn_pools']
        for x in remove_list: policy_list.remove(x)
        for i in kwargs.item:
            if not i.get('fc_zone_policies'): policy_list.remove('fc_zone_policies')
            for x in range(0,len(i.names)):
                apiBody = {'Name':i.names[x],'Order':i.placement.pci_order[x]}
                for k, v in i.items():
                    if k in jsonVars.key_map:
                        apiBody.update({jsonVars.key_map[k]:v})
                apiBody.update({'ObjectType':'vnic.FcIf'})
                for p in policy_list:
                    pshort = (p.replace('_policy', '')).replace('_policies', '')
                    jVars = kwargs.ezdata.policies.allOf[1].properties[pshort]
                    if type(i[p]) == list: pname = i[p][x]
                    else: pname = i[p]
                    if not kwargs.moids[p].get(pname):
                        validating.error_policy_doesnt_exist(p, pname, self.type, 'policy', apiBody['Name'])
                    else:
                        pmoid = kwargs.moids[p][pname].moid
                        apiBody.update({jVars['object_name']:{
                            'moid':pmoid,'ObjectType':jVars['object_type']
                        }})
                apiBody.update({'SanConnectivityPolicy':{
                    'Moid':scp_moid,'ObjectType':'vnic.SanConnectivityPolicy'
                }})
                if x == 0: side = 'A'
                else: side = 'B'
                apiBody.update({'Placement':{
                    'Id':'MLOM','ObjectType':'vnic.PlacementSettings','PciLink':0,'SwitchId':side,'Uplink':0
                }})
                if i.get('fc_zone_policies'):
                    zone_policies = numpy.array_split(i['fc_zone_policies'], 2)
                    jVars = kwargs.ezdata.policies.allOf[1].properties['fc_zone']
                    apiBody.update({jVars['object_name']:[]})
                    for z in zone_policies[x]:
                        pname = z
                        if not kwargs.moids['fc_zone_policies'].get(pname):
                            validating.error_policy_doesnt_exist('fc_zone_policy', pname, self.type, 'policy', apiBody['Name'])
                        apiBody[jVars['object_name']].append({
                            'Moid':kwargs.moids['fc_zone_policies'][pname].moid,
                            'ObjectType':'fabric.FcZonePolicy'}
                        )
                if i.get('placement'):
                    place_list = ['pci_links', 'slot_ids', 'switch_ids', 'uplink_ports']
                    for p in place_list:
                        count = 0
                        if i.get(p): count += 1
                        if count == 1:
                            if len(i[p]) == 2: pval = i[p][x]
                            else: pval = i[p][0]
                            if 'uplink' in p: pvar = 'UplinkPort'
                            elif 'slot' in p: pvar = 'Id'
                            elif 'switch_id' in p: pvar = 'SwitchId'
                            else: pvar = 'PciLink'
                            apiBody['Placement'][pvar] = pval
                if i.get('vhba_type'):
                    apiBody.update({'Type':i['vhba_type']})
                    apiBody.pop('vhba_type')
                else: apiBody.update({'Type':'fc-initiator'})
                if i.get('wwpn_pools'):
                    wwpnpool = kwargs.moids['wwpn_pools'][i['wwpn_pools'][x]].moid
                    apiBody.update({
                        'WwpnAddressType':'POOL',
                        'WwpnPool':{'Moid':wwpnpool,'ObjectType':'fcpool.Pool'}
                    })
                #=====================================================
                # Create or Patch the VLANs via the Intersight API
                #=====================================================
                if not kwargs.moids.vhbas.get(i['names'][x]): kwargs.method = 'post'
                else:
                    kwargs.method= 'patch'
                    kwargs.pmoid = kwargs.moids.vhbas[i['names'][x]].moid
                kwargs.apiBody= apiBody
                kwargs.qtype  = 'vhbas'
                kwargs.uri    = jsonVars.uri
                kwargs        = api('vhbas').calls(kwargs)
        return kwargs

    #=======================================================
    # Virtual Media Policy Modification
    #=======================================================
    def virtual_media(self, apiBody, item, kwargs):
        jsonVars = kwargs.ezdata.policies.allOf[1].properties['virtual_media']['add_key_map']
        if item.get('add_virtual_media'):
            apiBody.update({'mappings':[]})
            for i in item['add_virtual_media']:
                vmedia_add = {}
                for k, v in i.items():
                    if k in jsonVars: vmedia_add.update({jsonVars[k]:v})
                vmedia_add.update({'object_type':'vmeida.Mapping'})
                apiBody['mappings'].append(vmedia_add)
        return apiBody

    #=====================================================
    # Assign VLANs to VLAN Policies
    #=====================================================
    def vlans(self, kwargs):
        #=====================================================
        # Get Multicast Policies
        #=====================================================
        mcast_names  = []
        for i in kwargs.policies:
            mcast_names.append(i.multicast_policy)
        mcast_names = numpy.unique(numpy.array(mcast_names))
        kwargs      = api_get(False, mcast_names, 'multicast', kwargs)
        mcast_moids = kwargs.pmoids
        for i in kwargs.policies:
            vnames = []; post_list = []
            vlan_list = ezfunctions.vlan_list_full(i.vlan_list)
            for i in vlan_list: vnames.append(i)
            kwargs.pmoid = kwargs.policy_moids[i.name].moid
            vlan_moid = kwargs.pmoid
            kwargs = api_get(True, vnames, self.type, kwargs)
            vlans_moid = kwargs.pmoids
            vlans_results = kwargs.results
            #=====================================================
            # Create API Body for VLANs
            #=====================================================
            ezdata = kwargs.ezdata[self.type]
            apiBody = {'EthNetworkPolicy':{'Moid':vlan_moid, 'ObjectType':'fabric.EthNetworkPolicy'},'ObjectType':ezdata.ObjectType}
            apiBody = build_apiBody(apiBody, ezdata.properties, i, self.type, kwargs)
            apiBody.pop('Organizations'); apiBody.pop('Tags')
            if not apiBody.get('AutoAllowOnUplinks'): apiBody.update({'AutoAllowOnUplinks':False})
            if not mcast_moids.get(i.multicast_policy):
                validating.error_policy_doesnt_exist('multicast_policy', i.multicast_policy, self.type, 'Vlans', i.vlan_list)
            apiBody['MulticastPolicy']['Moid'] = mcast_moids[i.multicast_policy].moid
            if not apiBody.get('IsNative'): apiBody['IsNative'] = False
            for x in vlan_list:
                if type(x) == str: x = int(x)
                if not len(vlan_list) == 1:
                    if i.name == 'vlan': apiBody['Name'] = f"{i.name}{'0'*(4 - len(str(x)))}{x}"
                    else: apiBody['Name'] = f"{i.name}-vl{'0'*(4 - len(str(x)))}{x}"
                apiBody['VlanId'] = x
                #=====================================================
                # Create or Patch the VLANs via the Intersight API
                #=====================================================
                if not vlans_moid.get(x): post_list.append(apiBody)
                else:
                    indx = next((index for (index, d) in enumerate(vlans_results) if d['VlanId'] == x), None)
                    patch_vlan = compare_body_result(apiBody, vlans_results[indx])
                    #if not   vlans_results[indx].AutoAllowOnUplinks == apiBody['AutoAllowOnUplinks']: patchVlan = True
                    #elif not vlans_results[indx].Name == apiBody['Name']: patchVlan = True
                    #elif not vlans_results[indx].IsNative == native: patchVlan = True
                    #elif not vlans_results[indx].MulticastPolicy.Moid == apiBody['MulticastPolicy']['Moid']: patchVlan = True
                    if patch_vlan == True:
                        kwargs.apiBody= apiBody
                        kwargs.method = 'patch'
                        kwargs.qtype  = self.type
                        kwargs.uri    = ezdata.intersight_uri
                        kwargs        = api(kwargs.qtype).calls(kwargs)
                    else: prCyan(f"      * Skipping VLAN {x}.  Intersight Matches Configuration.")
            if len(post_list) > 0:
                kwargs.method = 'POST'
                kwargs.uri    = ezdata.intersight_uri
                kwargs = bulk_request(post_list, kwargs)
                kwargs.method = 'post'
                kwargs.qtype  = 'bulk_request'
                kwargs.uri    = 'bulk/Requests'
                kwargs = api(kwargs.qtype).calls(kwargs)
        return kwargs

    #=====================================================
    # Assign VNICs to LAN Connectivity Policies
    #=====================================================
    def vnics(self, kwargs):
        ezdata = kwargs.ezdata[self.type]
        #=====================================================
        # Get Policies and Pools
        #=====================================================
        for item in kwargs.policies:
            for i in item.vnics:
                for k,v in i.items():
                    if re.search('_polic(ies|y)|_pools$', k):
                        ptype = (k.replace('cies', 'cy')).replace('_address_pools', '')
                        if not kwargs.cp.get(ptype): kwargs.cp[ptype].names = []
                        if type(v) == list: kwargs.cp[ptype].extend(v)
                        else: kwargs.cp[ptype].append(v)
        for e in list(kwargs.cp.keys()):
            names = list(numpy.unique(numpy.array(kwargs.cp[e].names)))
            kwargs = api_get(False, names, e.replace('_policy', ''), kwargs)
            kwargs.cp[e].moids = kwargs.pmoids
        #=====================================================
        # Create API Body for vNICs
        #=====================================================
        for item in kwargs.policies:
            lcp_moid = kwargs.policy_moids[item.name].moid
            names = []
            for i in item.vnics: names.extend(i.names)
            kwargs = api_get(True, names, self.type, kwargs)
            vnic_moids = kwargs.pmoids
            for i in item.vnics:
                apiBody = {'LanConnectivityPolicy':{'Moid':lcp_moid,'ObjectType':'vnic.LanConnectivityPolicy'},
                        'ObjectType':ezdata.ObjectType}
                for x in range(len(i.names)):
                    apiBody.update({'Name':i.names[x]})
                    #apiBody.update({'Name':i.names[x],'Order':i.placement.pci_order[x]})
                    apiBody = build_apiBody(ezdata.properties, i, self.type, kwargs)
                    apiBody.pop('Organizations'); apiBody.pop('Tags')
                    if not apiBody.get('Cdn'):
                        apiBody.update({'Cdn':{'Value':i.names[x],'Source':'vnic','ObjectType':'vnic.Cdn'}})
                    apiBody['Order'] = i.placement.pci_order[x]
                    if apiBody['Placement'].get['Order']: apiBody['Placement'].pop('Order')
                    for k, v in i.items():
                        if re.search('_polic(ies|y)|_pools$', k):
                            ptype = (k.replace('cies', 'cy')).replace('_address_pools', '')
                            if type(v) == list:
                                if len(v) == 2: pname = v[x]
                                else: pname = v[0]
                            else: pname = v
                            if not kwargs.cp[ptype].moids.get(pname):
                                validating.error_policy_doesnt_exist(ptype, pname, self.type, 'policy', i.names[x])
                            apiBody[ezdata.properties[k].intersight_api.split(':')[1]]['Moid'
                            ] = kwargs.cp[ptype].moids[pname].moid
                    apiBody['FabricEthNetworkGroupPolicy'] = [apiBody['FabricEthNetworkGroupPolicy']]
                if x == 0: side = 'A'
                else: side = 'B'
                apiBody.update({'Placement':{
                    'Id':'MLOM','ObjectType':'vnic.PlacementSettings','PciLink':0,'SwitchId':side,'Uplink':0}})
                if i.get('placement'):
                    place_list = ['pci_links', 'slot_ids', 'switch_ids', 'uplink_ports']
                    for p in place_list:
                        if i.get(p):
                            if len(i[p]) == 2: pval = i[p][x]
                            else: pval = i[p][0]
                            apiBody['Placement'][ezdata.properties.placement.properties[p].intersight_api] = pval
                #=====================================================
                # Create or Patch the VLANs via the Intersight API
                #=====================================================
                if vnic_moids.get(i['names'][x]):
                    kwargs.method = 'patch'
                    kwargs.pmoid = vnic_moids[i['names'][x]].moid
                else: kwargs.method = 'post'
                kwargs.apiBody= apiBody
                kwargs.qtype  = self.type
                kwargs.uri    = ezdata.intersight_uri
                kwargs        = api(kwargs.qtype).calls(kwargs)
        return kwargs

    #=====================================================
    # Assign VSANs to VSAN Policies
    #=====================================================
    def vsans(self, kwargs):
        jsonVars = kwargs.ezdata.policies.allOf[1].properties[self.type]
        #=====================================================
        # Get Policies and Pools
        #=====================================================
        kwargs.names = []
        for i in kwargs.item: kwargs.names.append(str(i['vsan_id']))
        kwargs.method= 'get'
        kwargs.qtype = 'vsans'
        kwargs.uri   = jsonVars.uri
        vsan_moid    = kwargs.pmoid
        kwargs = api('vsans').calls(kwargs)
        vsans_moids = kwargs.pmoids
        for i in kwargs.item:
                #=====================================================
                # Create API Body for the VSANs
                #=====================================================
                apiBody = {'FcNetworkPolicy':{
                    'Moid':vsan_moid,'ObjectType':'fabric.FcNetworkPolicy'}}
                for k, v in i.items():
                    if k in jsonVars.key_map: apiBody.update({jsonVars.key_map[k]:v})
                if not apiBody.get('FcoeVlan'): apiBody.update({'FcoeVlan':i['vsan_id']})
                #=====================================================
                # Create or Patch the VSANs via the Intersight API
                #=====================================================
                if vsans_moids.get(i['vsan_id']):
                    kwargs.method = 'patch'
                    kwargs.pmoid = vsans_moids[i['vsan_id']].moid
                else: kwargs.method = 'post'
                kwargs.apiBody= apiBody
                kwargs.qtype  = 'vsans'
                kwargs.uri    = jsonVars.uri
                kwargs        = api('vsans').calls(kwargs)
        return kwargs

#=======================================================
# Profiles Class
#=======================================================
class profiles_class(object):
    def __init__(self, type):
        self.type = type

    #=====================================================
    #  Profiles Function
    #=====================================================
    def profiles(self, kwargs):
        #=====================================================
        # Load Variables and Send Begin Notification
        #=====================================================
        jsonVars = kwargs.ezdata.profiles.allOf[1].properties[self.type]
        if 'templates' == self.type:
            profiles = kwargs.imm_dict.orgs[kwargs.org][self.type]['server']
            profiles = list({v['name']:v for v in profiles}.values())
        else:
            profiles = kwargs.imm_dict.orgs[kwargs.org].profiles[self.type]
            if self.type == 'domain':
                profiles = list({v['name']:v for v in profiles}.values())
            else: profiles=list({v['targets'][0]['name']:v for v in profiles}.values())
        if 'server' == self.type:
            templates = {}
            if kwargs.imm_dict.orgs[kwargs.org].get('templates'):
                for item in kwargs.imm_dict.orgs[kwargs.org]['templates']['server']:
                    templates.update({item['name']:item})
        kwargs.org_moid = kwargs.org_moids[kwargs.org].moid
        validating.begin_section(self.type, 'profiles')

        #=====================================================
        # Setup Arguments
        #=====================================================
        kwargs.method = 'get'
        kwargs.jsonVars  = jsonVars
        kwargs.names     = []
        kwargs.policies  = {}
        kwargs.serials   = []
        kwargs.templates = []
        kwargs.uri       = jsonVars.uri

        #=================================
        # Compile List of Serial Numbers
        #=================================
        for item in profiles:
            if re.search('^(chassis|server)$', self.type):
                if 'server' == self.type:
                    if item.get('ucs_server_profile_template'):
                        kwargs.templates.append(item['ucs_server_profile_template'])
                        kwargs.template = item['ucs_server_profile_template']
                for i in item['targets']:
                    kwargs.names.append(i['name'])
                    if i.get('serial_number'): kwargs.serials.append(i.serial_number)
            else:
                kwargs.names.append(item['name'])
                if item.get('serial_numbers'): kwargs.serials.extend(item.serial_numbers)

        #==================================
        # Get Moids for Profiles/Templates
        #==================================
        kwargs.method= 'get'
        kwargs.qtype = self.type
        kwargs = api(self.type).calls(kwargs)
        kwargs.moids[self.type] = kwargs.pmoids
        if len(kwargs.templates) > 0:
            kwargs.names= numpy.unique(numpy.array(kwargs.templates))
            kwargs.qtype= 'templates'
            kwargs.uri  = jsonVars.uri_template
            kwargs      = api('templates').calls(kwargs)
            kwargs.moids.templates = kwargs.pmoids
        if 'domain' in self.type:
            clusters      = kwargs.names
            kwargs.qtype  = 'switch'
            kwargs.names  = []
            kwargs.fabrics= ['A', 'B']
            kwargs.uri    = jsonVars.uri_switch
            for c in clusters:
                if kwargs.moids[self.type].get(c):
                    for x in range(0,len(kwargs.fabrics)): kwargs.names.append(f'{c}-{kwargs.fabrics[x]}')
                    kwargs.pmoid = kwargs.moids[self.type][c].moid
                    kwargs = api('switch').calls(kwargs)
                    kwargs.moids.switch = kwargs.pmoids
            kwargs.uri = jsonVars.uri
        #=================================
        # Compile List of Policy Moids
        #=================================
        for p in jsonVars.policy_list:
            kwargs.names = []
            for item in profiles:
                if item.get(p):
                    if 'policies' in item[p]:
                        for i in item[p]: kwargs.names.append(i)
                    else: kwargs.names.append(item[p])
                if item.get('ucs_server_profile_template'):
                    spt = item['ucs_server_profile_template']
                    if templates[spt].get(p):
                        kwargs.names.append(templates[spt][p])
            ptype = ((p.replace('_policy', '')).replace('_pool', '')).replace('_policies', '')
            if 'pool' in p: kwargs.uri = kwargs.ezdata.pools.allOf[1].properties[ptype].uri
            else: kwargs.uri = kwargs.ezdata.policies.allOf[1].properties[ptype].uri
            kwargs.names  = numpy.unique(numpy.array(kwargs.names))
            kwargs.method = 'get'
            kwargs.qtype  = ptype
            kwargs        = api(ptype).calls(kwargs)
            kwargs.policy_moids[p]= deepcopy(kwargs.pmoids)

        #========================================
        # Get Serial Moids
        #========================================
        kwargs.uri = self.type
        if len(kwargs.serials) > 0:
            kwargs.qtype        = 'serial_number'
            kwargs.names        = kwargs.serials
            kwargs.uri          = jsonVars.uri_serial
            kwargs              = api(kwargs.qtype).calls(kwargs)
            kwargs.serial_moids = kwargs.pmoids
        kwargs.uri = jsonVars.uri

        #=====================================================
        # Create the Profiles with the Functions
        #=====================================================
        kwargs.type = self.type
        for item in profiles:
            if kwargs.description: kwargs.pop('description')
            if kwargs.serial_number: kwargs.pop('serial_number')
            if kwargs.tags: kwargs.pop('tags')
            if item.get('tags'):
                kwargs.tags = item.tags.toDict()
                kwargs.tags.extend(kwargs.ezdata.tags.toDict())
            else: kwargs.tags = [kwargs.ezdata.tags.toDict()]
            if re.search('^(chassis|server)$', self.type):
                for i in item['targets']:
                    kwargs.apiBody = {'Name':i.name, 'Description': '', 'Tags':kwargs.tags}
                    if i.get('description'): kwargs.apiBody.update({'Description':i.description})
                    else: kwargs.apiBody.pop('Description')
                    if i.get('serial_number'): kwargs.serial_number = i.serial_number
                    if item.get('ucs_server_profile_template'):
                        i.update({'ucs_server_profile_template':item['ucs_server_profile_template']})
                        if not kwargs.moids['templates'].get(i['ucs_server_profile_template']):
                            ptype = 'ucs_server_profile_template'
                            tname = i['ucs_server_profile_template']
                            validating.error_policy_doesnt_exist(
                                ptype, tname, kwargs.name, kwargs.type, 'Profile')
                        kwargs.template_policies = templates[i['ucs_server_profile_template']]
                        if item.get('create_from_template'): i.update(
                                {'create_from_template':item['create_from_template']})
                    for p in jsonVars.policy_list:
                        if item.get(p): i.update({p:item[p]})
                    kwargs = profile_function(i, kwargs)
                    kwargs.moids[self.type][i.name].moid = kwargs.pmoid
            elif re.search('^domain$', self.type):
                kwargs.apiBody = {'Name':item.name, 'Description': '', 'Tags':kwargs.tags}
                if item.get('description'): kwargs.apiBody.update({'Description':item.description})
                profile_domain(item, kwargs)
            elif 'templates' == self.type:
                kwargs.apiBody = {'Name':item.name, 'Description': '', 'Tags':kwargs.tags}
                if item.get('description'): kwargs.apiBody.update({'Description':item.description})
                if item.get('serial_number'): kwargs.serial_number = item.serial_number
                kwargs = profile_function(item, kwargs)
                kwargs.moids[self.type][item.name].moid = kwargs.pmoid

        #========================================================
        # Deploy Domain Profiles if Action is Deploy
        #========================================================
        deploy_profiles = False
        if re.search('^domain$', self.type):
            for item in profiles:
                if item.get('action'):
                    for x in range(0,len(kwargs.fabrics)):
                        if item['action'] == 'Deploy' and re.search(serial_regex, item.serial_numbers[x]):
                            if deploy_profiles == False:
                                deploy_profiles = True
                                prLightPurple(f'\n{"-"*81}\n')
                            pname = f"{item['name']}-{kwargs.fabrics[x]}"
                            prGreen(f'    - Beginning Profile Deployment for {pname}')
                            kwargs.apiBody= {'Action':'Deploy'}
                            kwargs.method = 'patch'
                            kwargs.pmoid  = kwargs.moids['switch'][pname].moid
                            kwargs.qtype  = 'switch'
                            kwargs.uri    = jsonVars.uri_switch
                            kwargs = api('switch').calls(kwargs)
            if deploy_profiles == True:
                prLightPurple(f'\n{"-"*81}\n')
                time.sleep(60)
            for item in profiles:
                if item.get('action'):
                    for x in range(0,len(kwargs.fabrics)):
                        if item['action'] == 'Deploy' and re.search(serial_regex, item.serial_numbers[x]):
                            pname = f"{item['name']}-{kwargs.fabrics[x]}"
                            kwargs.method= 'get_by_moid'
                            kwargs.pmoid = kwargs.moids['switch'][pname].moid
                            kwargs.qtype = 'switch'
                            deploy_complete = False
                            while deploy_complete == False:
                                kwargs = api('switch').calls(kwargs)
                                if kwargs['results']['ConfigContext']['ControlAction'] == 'No-op':
                                    deploy_complete = True
                                    pname = item['name']
                                    prGreen(f'    - Completed Profile Deployment for {pname}')
                                else: 
                                    prCyan(f'      * Deploy Still Occuring on {pname}.  Waiting 120 seconds.')
                                    #validating.deploy_notification(self.type, pname)
                                    time.sleep(120)
            if deploy_profiles == True:
                prLightPurple(f'\n{"-"*81}\n')

        #========================================================
        # Deploy Chassis/Server Profiles if Action is Deploy
        #========================================================
        pending_changes = False
        if re.search('^(chassis|server)$', self.type):
            for item in profiles:
                for i in item['targets']:
                    if item.get('action'):
                        if item['action'] == 'Deploy' and re.search(serial_regex, i.serial_number):
                            if deploy_profiles == False:
                                deploy_profiles = True
                                prLightPurple(f'\n{"-"*81}\n')
                            pname         = i['name']
                            kwargs.method = 'get_by_moid'
                            kwargs.pmoid  = kwargs.moids[self.type][pname].moid
                            kwargs.qtype  = self.type
                            kwargs.uri    = jsonVars.uri
                            kwargs = api(self.type).calls(kwargs)
                            results = DotMap(kwargs['results'])
                            if len(results.ConfigChanges.Changes) > 0:
                                pending_changes = True
                                break
                if pending_changes == True: break
        if pending_changes == True: time.sleep(120)
        if re.search('^(chassis|server)$', self.type):
            for item in profiles:
                for i in item['targets']:
                    if item.get('action'):
                        if item['action'] == 'Deploy' and re.search(serial_regex, i.serial_number):
                            if deploy_profiles == False:
                                deploy_profiles = True
                                prLightPurple(f'\n{"-"*81}\n')
                            pname         = i['name']
                            kwargs.method = 'get_by_moid'
                            kwargs.pmoid  = kwargs.moids[self.type][pname].moid
                            kwargs.qtype  = self.type
                            kwargs.uri    = jsonVars.uri
                            kwargs = api(self.type).calls(kwargs)
                            results = DotMap(kwargs['results'])
                            if (len(results.ConfigChanges.Changes) > 0 and 'server' in self.type) or 'chassis' in self.type:
                                prGreen(f'    - Beginning Profile Deployment for {pname}')
                                kwargs.apiBody= {'Action':'Deploy'}
                                kwargs.method = 'patch'
                                kwargs.pmoid  = kwargs.moids[self.type][pname].moid
                                kwargs.qtype  = self.type
                                kwargs.uri    = jsonVars.uri
                                kwargs = api(self.type).calls(kwargs)
                            else:
                                prLightPurple(f'    - Skipping Profile Deployment for {pname}.  No Pending Changes')
            if deploy_profiles == True: prLightPurple(f'\n{"-"*81}\n')
        if pending_changes == True: time.sleep(60)
        if re.search('^(chassis|server)$', self.type):
            for item in profiles:
                for i in item['targets']:
                    if item.get('action'):
                        if item['action'] == 'Deploy' and re.search(serial_regex, i.serial_number):
                            pname           = i['name']
                            deploy_profiles = True
                            deploy_complete = False
                            while deploy_complete == False:
                                kwargs.method = 'get_by_moid'
                                kwargs.pmoid  = kwargs.moids[self.type][pname].moid
                                kwargs.qtype  = self.type
                                kwargs = api(self.type).calls(kwargs)
                                results = DotMap(kwargs['results'])
                                if results.ConfigContext.ControlAction == 'No-op':
                                    deploy_complete = True
                                    if re.search('^(chassis)$', self.type):
                                        prGreen(f'    - Completed Profile Deployment for {pname}')
                                else: 
                                    prCyan(f'      * Deploy Still Occuring on {pname}.  Waiting 120 seconds.')
                                    #validating.deploy_notification(self.type, pname)
                                    time.sleep(120)
            if deploy_profiles == True:
                prLightPurple(f'\n{"-"*81}\n')
        if re.search('^(server)$', self.type) and pending_changes == True:
            for item in profiles:
                for i in item['targets']:
                    if item.get('action'):
                        if item['action'] == 'Deploy' and re.search(serial_regex, i.serial_number):
                            pname = i['name']
                            kwargs.method = 'get_by_moid'
                            kwargs.pmoid  = kwargs.moids[self.type][pname].moid
                            kwargs.qtype  = self.type
                            kwargs = api(self.type).calls(kwargs)
                            results = DotMap(kwargs['results'])
                            if len(results.ConfigChanges.PolicyDisruptions) > 0:
                                prGreen(f'    - Beginning Profile Activation for {pname}')
                                kwargs.apiBody= {'ScheduledActions':[{'Action':'Activate', 'ProceedOnReboot':True}]}
                                kwargs.method = 'patch'
                                kwargs.pmoid  = kwargs.moids[self.type][pname].moid
                                kwargs.qtype  = self.type
                                kwargs.uri    = jsonVars.uri
                                kwargs = api(self.type).calls(kwargs)
            if deploy_profiles == True:
                prLightPurple(f'\n{"-"*81}\n')
                time.sleep(60)
            for item in profiles:
                for i in item['targets']:
                    if item.get('action'):
                        if item['action'] == 'Deploy' and re.search(serial_regex, i.serial_number):
                            pname           = i['name']
                            deploy_profiles = True
                            deploy_complete = False
                            while deploy_complete == False:
                                kwargs.method = 'get_by_moid'
                                kwargs.pmoid  = kwargs.moids[self.type][pname].moid
                                kwargs.qtype  = self.type
                                kwargs = api(self.type).calls(kwargs)
                                results = DotMap(kwargs['results'])
                                if results.ConfigContext.ControlAction == 'No-op':
                                    deploy_complete = True
                                    prGreen(f'    - Completed Profile Deployment for {pname}')
                                else: 
                                    prCyan(f'      * Deploy Still Occuring on {pname}.  Waiting 120 seconds.')
                                    time.sleep(120)
            if deploy_profiles == True:
                prLightPurple(f'\n{"-"*81}\n')

        #========================================================
        # End Function and return kwargs
        #========================================================
        validating.end_section(self.type, 'profiles')
        return kwargs

#======================================================
# Function - API Get Calls
#======================================================
def api_get(empty, names, otype, kwargs):
    kwargs.names = names
    kwargs.method= 'get'
    kwargs.qtype = otype
    kwargs.uri   = kwargs.ezdata[otype].intersight_uri
    kwargs       = api(kwargs.qtype).calls(kwargs)
    if empty == False and kwargs.results == []: empty_results(kwargs)
    return kwargs

#=====================================================
# Add Attributes to the apiBody
#=====================================================
def build_apiBody(apiBody, idata, item, ptype, kwargs):
    for k, v in item.items():
        #print(json.dumps(idata, indent=4))
        #print(k, v)
        if re.search('boolean|string|integer', idata[k].type):
            if '$ref:' in idata[k].intersight_api:
                x = idata[k].intersight_api.split(':')
                if not apiBody.get(x[1]): apiBody.update({x[1]:{'ObjectType':x[2]}})
                apiBody[x[1]].update({x[3]:v})
            else: apiBody.update({idata[k].intersight_api:v})
        elif idata[k].type == 'array':
            if re.search('boolean|string|integer',  idata[k]['items'].type):
                apiBody[idata[k]['items'].intersight_api] = []
                for e in v: apiBody[idata[k]['items'].intersight_api].append(e)
            else:
                apiBody[idata[k]['items'].intersight_api] = []
                for e in v:
                    idict = {'ObjectType':idata[k]['items'].ObjectType}
                    for a, b in idata[k]['items'].properties.items():
                        if re.search('boolean|string|integer', b.type):
                            if a in e: idict.update({b.intersight_api:e[a]})
                        elif b.type == 'object' and a in e:
                            idict.update({b.intersight_api:{'ObjectType':b.ObjectType}})
                            for c, d in b.properties.items():
                                if e[a].get(c): idict[b.intersight_api].update({d.intersight_api:e[a][c]})
                        elif b.type == 'array' and a in e:
                            print(b)
                            print(a)
                            print(e)
                            idict[b.intersight_api] = e[a]
                            print('not accounted for')
                    apiBody[idata[k]['items'].intersight_api].append(idict)
        elif idata[k].type == 'object':
            apiBody[idata[k].intersight_api] = {'ObjectType':idata[k].ObjectType}
            for a, b in idata[k].properties.items():
                if re.search('array|object', b.type):
                    print(b)
                    print(f'2 matched {b.type}')
                    exit()
                if v.get(a):
                    apiBody[idata[k].intersight_api].update({b.intersight_api:v[a]})

    #=====================================================
    # Validate all Parameters are String
    #=====================================================
    for k, v in apiBody.items():
        if type(v) == int or type(v) == float: apiBody[k] = str(v)
    #=====================================================
    # Add Policy Specific Settings
    #=====================================================
    if re.fullmatch(policy_specific_regex, ptype): apiBody = eval(f'imm(ptype).{ptype}(apiBody, item, kwargs)')
    plist1 = [
        'pc_appliances', 'pc_ethernet_uplinks', 'pc_fc_uplinks', 'pc_fcoe_uplinks', 'port_modes',
        'rl_appliances', 'rl_ethernet_uplinks', 'rl_fc_storage', 'rl_fc_uplinks', 'rl_fcoe_uplinks', 'rl_servers',
        'drive_groups', 'ldap_groups', 'ldap_servers', 'users', 'vhbas', 'vlans', 'vnics', 'vsans']
    pop_list = []
    for e in plist1: pop_list.append((e.replace('pc_', 'port_channel_')).replace('rl_', 'port_role_'))
    for e in pop_list:
        if apiBody.get(e): apiBody.pop(e)
    #=====================================================
    # Attach Organization Map, Tags, and return Dict
    #=====================================================
    apiBody = org_map(apiBody, kwargs.org_moids[kwargs.org].moid)
    if apiBody.get('Tags'): apiBody['Tags'].append(kwargs.ez_tags.toDict())
    else: apiBody.update({'Tags':[kwargs.ez_tags.toDict()]})
    apiBody = dict(sorted(apiBody.items()))
    print(json.dumps(apiBody, indent=4))
    return apiBody

#=====================================================
# Process API Results
#=====================================================
def build_pmoid_dictionary(api_results, kwargs):
    apiDict = DotMap()
    if api_results.get('Results'):
        for i in api_results.Results:
            if i.get('VlanId'): iname = i.VlanId
            elif i.get('PcId'): iname = i.PcId
            elif i.get('PortId'): iname = i.PortId
            elif i.ObjectType == 'asset.DeviceRegistration': iname = i.Serial[0]
            elif i.get('Serial'): iname = i.Serial
            elif i.get('VsanId'): iname = i.VsanId
            elif i.get('Answers'): iname = i.Answers.Hostname
            elif i.get('Name'): iname = i.Name
            elif kwargs.qtype == 'upgrade':
                if i.Status == 'IN_PROGRESS': iname = kwargs.srv_moid
            elif i.get('SocketDesignation'): iname = i.Dn
            elif i.get('EndPointUser'): iname = i.EndPointUser.Moid
            elif i.get('PortIdStart'): iname = i.PortIdStart
            elif i.get('Version'): iname = i.Version
            elif i.get('ControllerId'): iname = i.ControllerId
            elif i.get('Identity'): iname = i.Identity
            if i.get('PcId') or i.get('PortId') or i.get('PortIdStart'):
                apiDict[i.PortPolicy.Moid][iname].moid = i.Moid
            else: apiDict[iname].moid = i.Moid
            if i.get('IpV4Config'): apiDict[iname].ipv4_config = i.IpV4Config
            if i.get('IpV6Config'): apiDict[iname].ipv6_config = i.IpV6Config
            if i.get('Model'):
                apiDict[iname].model = i.Model
                apiDict[iname].object_type = i.ObjectType
                apiDict[iname].registered_device = i.RegisteredDevice.Moid
                if i.get('ChassisId'): apiDict[iname].id = i.ChassisId
                if i.get('SourceObjectType'): apiDict[iname].object_type = i.SourceObjectType
            if i.get('PolicyBucket'): apiDict[iname].policy_bucket = i.PolicyBucket
            if i.get('Selectors'): apiDict[iname].selectors = i.Selectors
            if i.get('SwitchId'): apiDict[iname].switch_id = i.SwitchId
            if i.get('Tags'): apiDict[iname].tags = i.Tags
            if i.get('UpgradeStatus'): apiDict[iname].upgrade_status = i.UpgradeStatus
            if i.get('Profiles'):
                apiDict[iname].profiles = []
                for x in i['Profiles']:
                    xdict = DotMap(Moid=x.Moid,ObjectType=x.ObjectType)
                    apiDict[iname].profiles.append(xdict)
    return apiDict

#=====================================================
# Bulk API Request Body
#=====================================================
def bulk_request(request_body, kwargs):
    kwargs.apiBody = []
    for e in request_body:
        kwargs.apiBody.append({'Body':e, 'ClassId':'bulk.RestSubRequest', 'ObjectType':'bulk.RestSubRequest',
                               'Verb':kwargs.method, 'Uri':f'/v1/{kwargs.uri}'})
    return kwargs

#=======================================================
# Add Organization Key Map to Dictionaries
#=======================================================
def compare_body_result(apibody, result):
    patch_return = False
    for k, v in apibody.items():
        if type(v) == dict:
            for a,b in v.items():
                if not result[k][a] == b: patch_return = True
        elif type(v) == list:
            count = 0
            for e in v:
                for a, b in e.items():
                    if not result[k][count][a] == b: patch_return = True
                count += 1
        else:
            if not result[k] == v: patch_return = True
    return patch_return

#=======================================================
# Add Organization Key Map to Dictionaries
#=======================================================
def org_map(apiBody, org_moid):
    apiBody.update({'Organization':{'Moid':org_moid, 'ObjectType':'organization.Organization'}})
    return apiBody

#=======================================================
# Domain Profile Creation Function
#=======================================================
def profile_domain(item, kwargs):
    #=====================================================
    # Build apiBody
    #=====================================================
    kwargs.apiBody = org_map(kwargs.apiBody, kwargs.org_moid)
    kwargs.apiBody.update({'ObjectType':'fabric.SwitchClusterProfile'})
    #=====================================================
    # Create/Patch the Profile via the Intersight API
    #=====================================================
    kwargs.qtype  = 'cluster'
    kwargs.uri    = kwargs.jsonVars.uri
    if kwargs.moids[kwargs.type].get(kwargs.apiBody['Name']):
        kwargs.method = 'patch'
        kwargs.pmoid = kwargs.moids[kwargs.type][kwargs.apiBody['Name']].moid
    else: kwargs.method = 'post'
    kwargs = api('cluster').calls(kwargs)
    cluster_moid = kwargs.pmoid
    #=====================================================
    # Build apiBody for Switch Profiles
    #=====================================================
    sw_names = []
    for x in range(0,len(kwargs.fabrics)):
        sw_name = f"{item['name']}-{kwargs.fabrics[x]}"
        sw_names.append(sw_name)
        apiBody = {'Name':sw_name}
        apiBody.update({'ObjectType':'fabric.SwitchProfile'})
        apiBody.update({'SwitchClusterProfile':{'Moid':cluster_moid,'ObjectType':'fabric.SwitchClusterProfile'}})
        if item.get('serial_numbers'):
            if re.search(serial_regex, item.serial_numbers[x]): serial_true = True
            else: serial_true = False
        if serial_true == True:
            serial_true += 1
            if kwargs.serial_moids.get(item.serial_numbers[x]):
                serial_moid = kwargs.serial_moids[item.serial_numbers[x]].moid
            else: validating.error_serial_number(sw_name, item.serial_numbers[x])
            apiBody.update({'AssignedSwitch':{'Moid':serial_moid,'ObjectType':'network.Element'}})
        #=====================================================
        # Attach Policies to Switch Profiles
        #=====================================================
        for p in kwargs.jsonVars.policy_list:
            pshort = ((p.replace('_policy', '')).replace('_pool', '')).replace('_policies', '')
            pObject = kwargs.ezdata.policies.allOf[1].properties[pshort]['object_type']
            add_policy = False
            if item.get(p):
                if len(item[p]) > 0: add_policy = True
            if add_policy == True:
                if not apiBody.get('PolicyBucket'): apiBody.update({'PolicyBucket':[]})
                if type(item[p]) == list:
                    if len(item[p]) == 2: ppolicy = item[p][x]
                    else: ppolicy = item[p][0]
                else: ppolicy = item[p]
                if not kwargs.policy_moids[p].get(ppolicy):
                    validating.error_policy_doesnt_exist(p, ppolicy, item.name, kwargs.type, 'Profile')
                pmoid = kwargs.policy_moids[p][ppolicy].moid
                pbucket = {'Moid':pmoid,'ObjectType':pObject}
                apiBody['PolicyBucket'].append(pbucket)

        #=====================================================
        # Attach Policies to Switch Profiles
        #=====================================================
        kwargs.apiBody= apiBody
        kwargs.qtype  = 'switch'
        kwargs.uri    = kwargs.jsonVars.uri_switch
        if kwargs.moids['switch'].get(apiBody['Name']):
            kwargs.method = 'patch'
            kwargs.pmoid = kwargs.moids['switch'][apiBody['Name']].moid
        else: kwargs.method = 'post'
        kwargs = api('switch').calls(kwargs)
        kwargs.moids['switch'][sw_name].moid = kwargs.pmoid

    # Retrun to profiles Module
    return kwargs

#=======================================================
# Profile Creation Function
#=======================================================
def profile_function(item, kwargs):
    #=====================================================
    # Build apiBody
    #=====================================================
    apiBody = kwargs.apiBody
    apiBody = org_map(apiBody, kwargs.org_moid)
    if kwargs.type == 'templates': apiBody.update({'ObjectType':'server.ProfileTemplate'})
    elif kwargs.type == 'server':  apiBody.update({'ObjectType':'server.Profile'})
    elif kwargs.type == 'chassis': apiBody.update({'ObjectType':'chassis.Profile'})
    serial_true = False
    if kwargs.get('serial_number'):
        if re.search(serial_regex, kwargs.serial_number): serial_true = True
        else: serial_true = False
    if serial_true == True:
        if kwargs.serial_moids.get(kwargs.serial_number):
            serial_moid = kwargs.serial_moids[kwargs.serial_number].moid
            sobject     = kwargs.serial_moids[kwargs.serial_number]['object_type']
        else: validating.error_serial_number(kwargs.name, serial_moid)
        apiBody.update({f'Assigned{kwargs.type.capitalize()}':{
            'Moid':serial_moid, 'ObjectType':sobject
        }})

    #=================================================================
    # Determine if Policy Bucket Should be Utilized
    # For Server Profile Determine if Policy is Sourced from Template
    #=================================================================
    create_from_template = False
    policy_bucket = False
    server_template = ''
    if re.search('(chassis|templates)', kwargs.type): policy_bucket = True
    elif kwargs.type == 'server':
        if item.get('create_from_template'):
            if item['create_from_template'] == True:
                create_from_template = True
            else: policy_bucket = True
        else: policy_bucket = True
        if item.get('ucs_server_profile_template'):
            server_template = item['ucs_server_profile_template']

    #=====================================================
    # Attach Server Template to Server if Defined
    #=====================================================
    if len(server_template) > 0 and create_from_template == True:
        tmoid = kwargs.moids['templates'][server_template].moid
        bulkBody = {
            'ObjectType': 'bulk.MoCloner',
            'Sources':[{'Moid':tmoid, 'ObjectType':'server.ProfileTemplate'}],
            'Targets':[{
                'AssignedServer':apiBody[f'Assigned{kwargs.type.capitalize()}'],
                'Description': apiBody['Description'],
                'Name':apiBody['Name'],
                'Organization': apiBody['Organization'],
                'ObjectType':'server.Profile',
                'ServerAssignmentMode': 'Static'
            }]
        }

        #=====================================================
        # Create the Profile from the Template
        #=====================================================
        existing_profiles = list(kwargs.moids[kwargs.type].keys())
        if not apiBody['Name'] in existing_profiles:
            kwargs.apiBody= bulkBody
            kwargs.method = 'post'
            kwargs.qtype  = 'bulk'
            kwargs.uri    = 'bulk/MoCloners'
            kwargs = api('bulk').calls(kwargs)
            #kwargs.moids['server'][apiBody['Name']] = DotMap(moid = kwargs.pmoid)
            #kwargs.pmoid = kwargs.pmoid
        else: kwargs.pmoid = kwargs.moids[kwargs.type][apiBody['Name']].moid

    #=================================================================
    # Add Policies to the Policy Bucket if not deployed from Template
    #=================================================================
    if kwargs.type == 'templates' or (kwargs.type == 'server' and create_from_template == False):
        if item.get('target_platform'):
            apiBody.update({'TargetPlatform':item['target_platform']})
        else: apiBody.update({'TargetPlatform':'FIAttached'})
    if policy_bucket == True:
        if 'uuid_pool' in kwargs.jsonVars.policy_list: kwargs.jsonVars.policy_list.remove('uuid_pool')
        for p in kwargs.jsonVars.policy_list:
            pshort = p.replace('_policy', '')
            pObject = kwargs.ezdata.policies.allOf[1].properties[pshort]['object_type']
            add_policy = False
            if item.get(p):
                if len(item[p]) > 0:
                    add_policy = True
                    pname = item[p]
            elif kwargs.get('template_policies'):
                if kwargs.template_policies.get(p):
                    if len(kwargs.template_policies[p]) > 0:
                        add_policy = True
                        pname = kwargs.template_policies[p]
            if add_policy == True:
                if not apiBody.get('PolicyBucket'): apiBody.update({'PolicyBucket':[]})
                if not kwargs.policy_moids[p].get(pname):
                    validating.error_policy_doesnt_exist(p, pname, item.name, kwargs.type, 'Profile')
                pmoid = kwargs.policy_moids[p][pname].moid
                pbucket = {'Moid':pmoid,'ObjectType':pObject}
                apiBody['PolicyBucket'].append(pbucket)

    #=====================================================
    # Attach UUID Pool if it Exists
    #=====================================================
    add_policy = False
    p = 'uuid_pool'
    if item.get('uuid_pool') and create_from_template == False:
        if len(item[p]) > 0:
            add_policy = True
            pname = item[p]
    elif create_from_template == False:
        if kwargs.get('template_policies'):
            if kwargs.template_policies.get(p):
                if len(kwargs.template_policies[p]) > 0:
                    add_policy = True
                    pname = kwargs.template_policies[p]
        elif item.get(p):
            if len(item[p]) > 0:
                add_policy = True
                pname = item[p]
    if add_policy == True:
        pshort = p.replace('_pool', '')
        if not kwargs.policy_moids[p].get(pname):
            validating.error_policy_doesnt_exist(p, pname, item.name, kwargs.type, 'Profile')
        pmoid = kwargs.policy_moids[p][pname].moid
        pObject = kwargs.ezdata.pools.allOf[1].properties[pshort]['object_type']
        apiBody.update({'UuidAddressType':'POOL'})
        apiBody.update({'UuidPool':{'Moid':pmoid, 'ObjectType':pObject}})

    #=====================================================
    # Create/Patch the Profile via the Intersight API
    #=====================================================
    kwargs.apiBody= apiBody
    kwargs.qtype  = kwargs.type
    kwargs.uri    = kwargs.jsonVars.uri
    if create_from_template == False:
        if kwargs.moids[kwargs.type].get(apiBody['Name']):
            kwargs.method= 'patch'
            kwargs.pmoid = kwargs.moids[kwargs.type][apiBody['Name']].moid
        else: kwargs.method = 'post'
        kwargs = api(kwargs.type).calls(kwargs)
        kwargs.pmoid = kwargs.pmoid
    return kwargs

#======================================================
# Function - Exit on Empty Results
#======================================================
def empty_results(kwargs):
        prRed(f"The API Query Results were empty for {kwargs.uri}.  Exiting..."); sys.exit(1)
