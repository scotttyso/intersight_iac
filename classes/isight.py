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
part2 = '(l|s)an_connectivity|local_user|network_connectivity|snmp|storage|syslog|system_qos'
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
        if not re.search('^(organization|resource)/', kwargs.uri): org_moid = kwargs.org_moids[kwargs.org].moid
        #=====================================================
        # Authenticate to the API
        #=====================================================
        def api_auth_function(kwargs):
            api_key_id      = kwargs.args.intersight_api_key_id
            secret_key      = kwargs.args.intersight_secret_key
            if os.path.isfile(secret_key): kwargs.api_auth = IntersightAuth(api_key_id=api_key_id, secret_key_filename=secret_key)
            else: kwargs.api_auth = IntersightAuth(api_key_id=api_key_id, secret_key_string=secret_key)
            kwargs.auth_time= time.time()
            return kwargs
        if not kwargs.get('api_auth'): kwargs = api_auth_function(kwargs)
        #=====================================================
        # Setup API Parameters
        #=====================================================
        if 'get' == kwargs.method:
            if not kwargs.get('api_filter'):
                if re.search('(vlans|vsans|port.port_)', kwargs.qtype): names = ", ".join(map(str, kwargs.names))
                else: names = "', '".join(kwargs.names).strip("', '")
                if re.search('(organization|resource_group)', kwargs.qtype): api_filter = f"Name in ('{names}')"
                else: api_filter = f"Name in ('{names}') and Organization.Moid eq '{org_moid}'"
                if 'asset_target' == kwargs.qtype:         api_filter = f"TargetId in ('{names}')"
                elif 'connectivity.vhbas' in kwargs.qtype: api_filter = f"Name in ('{names}') and SanConnectivityPolicy.Moid eq '{kwargs.pmoid}'"
                elif 'connectivity.vnics' in kwargs.qtype: api_filter = f"Name in ('{names}') and LanConnectivityPolicy.Moid eq '{kwargs.pmoid}'"
                elif 'hcl_status' == kwargs.qtype:         api_filter = f"ManagedObject.Moid in ('{names}')"
                elif 'iam_role' == kwargs.qtype:           api_filter = f"Name in ('{names}') and Type eq 'IMC'"
                elif 'port.port_channel_' in kwargs.qtype: api_filter = f"PcId in ({names}) and PortPolicy.Moid eq '{kwargs.pmoid}'"
                elif 'port.port_modes' == kwargs.qtype:    api_filter = f"PortIdStart in ({names}) and PortPolicy.Moid eq '{kwargs.pmoid}'"
                elif 'port.port_role_' in kwargs.qtype:    api_filter = f"PortId in ({names}) and PortPolicy.Moid eq '{kwargs.pmoid}'"
                elif 'registered_device' == kwargs.qtype:  api_filter = f"Moid in ('{names}')"
                elif 'reservations' in kwargs.qtype:       api_filter = f"Identity in ('{names}') and Pool.Moid eq '{kwargs.pmoid}'"
                elif 'serial_number' == kwargs.qtype:      api_filter = f"Serial in ('{names}')"
                elif 'switch' == kwargs.qtype:             api_filter = f"Name in ('{names}') and SwitchClusterProfile.Moid eq '{kwargs.pmoid}'"
                elif 'user_role' == kwargs.qtype:          api_filter = f"EndPointUser.Moid in ('{names}') and EndPointUserPolicy.Moid eq '{kwargs.pmoid}'"
                elif 'vlan.vlans' == kwargs.qtype:         api_filter = f"VlanId in ({names}) and EthNetworkPolicy.Moid eq '{kwargs.pmoid}'"
                elif 'vsan.vsans' == kwargs.qtype:         api_filter = f"VsanId in ({names}) and FcNetworkPolicy.Moid eq '{kwargs.pmoid}'"
                elif 'wwnn_pool_leases' == kwargs.qtype:   api_filter = f"PoolPurpose eq 'WWNN' and AssignedToEntity.Moid in ('{names}')"
                elif 'wwpn_pool_leases' == kwargs.qtype:   api_filter = f"PoolPurpose eq 'WWPN' and AssignedToEntity.Moid in ('{names}')"
                elif re.search('ww(n|p)n', kwargs.qtype):  api_filter = api_filter + f" and PoolPurpose eq '{kwargs.qtype.upper()}'"
                if kwargs.top1000 == True and len(kwargs.api_filter) > 0: api_args = f'?$filter={kwargs.api_filter}&$top=1000'
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
                    for k, v in (response.json()).items(): prRed(f"    {k} is '{v}'")
                    sys.exit(1)
                if 'get_by_moid' in kwargs.method: response =  requests.get(f'{url}/api/v1/{uri}/{moid}', auth=api_auth)
                elif 'get' in kwargs.method:       response =  requests.get(f'{url}/api/v1/{uri}{api_args}', auth=api_auth)
                elif 'patch' in kwargs.method:     response =requests.patch(f'{url}/api/v1/{uri}/{moid}', auth=api_auth, json=payload)
                elif 'post' in kwargs.method:      response = requests.post(f'{url}/api/v1/{uri}', auth=api_auth, json=payload)
                status = response
                if re.search('40[0|3]', str(status)):
                    retry_action = False
                    send_error()
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
                    if i < retries -1: time.sleep(45); continue
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
        if int(debug_level) >= 1: prCyan(response)
        if int(debug_level)>= 5:
            if kwargs.method == 'get_by_moid': prCyan(f'  URL: {url}/api/v1/{uri}/{moid}')
            elif kwargs.method ==       'get': prCyan(f'  URL: {url}/api/v1/{uri}{api_args}')
            elif kwargs.method ==     'patch': prCyan(f'  URL: {url}/api/v1/{uri}/{moid}')
            elif kwargs.method ==      'post': prCyan(f'  URL: {url}/api/v1/{uri}')
        if int(debug_level) >= 6: prCyan(api_results)
        if int(debug_level) == 7:
            prCyan(json.dumps(payload, indent=4))
            prCyan(payload)
        #=====================================================
        # Gather Results from the apiCall
        #=====================================================
        if api_results.get('Results'): kwargs.results = api_results.Results
        else: kwargs.results = api_results
        if 'post' in kwargs.method:
            if re.search('bulk.(MoCloner|Request)', api_results.ObjectType):
                kwargs.pmoids = build_pmoid_dictionary(api_results, kwargs)
            else:
                kwargs.pmoid = api_results.Moid
                if kwargs.apiBody.get('Name'): kwargs.pmoids[kwargs.apiBody['Name']] = kwargs.pmoid
        elif 'inventory' in kwargs.uri: icount = 0
        else:
            if not kwargs.get('build_skip'): kwargs.pmoids = build_pmoid_dictionary(api_results, kwargs)
        #=====================================================
        # Print Progress Notifications
        #=====================================================
        if re.search('(patch|post)', kwargs.method):
            if re.search('bulk.(MoCloner|Request)', api_results.ObjectType):
                for e in api_results.Results:
                    kwargs.api_results = e.Body
                    validating.completed_item(self.type, kwargs)
            else:
                kwargs.api_results = api_results
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
                kwargs.apiBody={'Description':f'{org} Resource Group', 'Name':org}
                kwargs.method= 'post'
                kwargs.uri   = 'resource/Groups'
                kwargs       = api(kwargs.qtype).calls(kwargs)
                kwargs.rsg_moids[org].moid     = kwargs.results.Moid
                kwargs.rsg_moids[org].selectors= kwargs.results.Selectors
            if not org in kwargs.org_moids:
                kwargs.apiBody={'Description':f'{org} Organization', 'Name':org,
                                'ResourceGroups':[{'Moid': kwargs.rsg_moids[org].moid, 'ObjectType': 'resource.Group'}]}
                kwargs.method= 'post'
                kwargs.uri   = 'organization/Organizations'
                kwargs       = api(kwargs.qtype).calls(kwargs)
                kwargs.org_moids[org].moid = kwargs.results.Moid
        return kwargs

#=======================================================
# Policies Class
#=======================================================
class imm(object):
    def __init__(self, type): self.type = type

    #=======================================================
    # BIOS Policy Modification
    #=======================================================
    def bios(self, apiBody, item, kwargs):
        if apiBody.get('bios_template'):
            btemplate = kwargs.ezdata['bios.template'].properties
            if '-tpm' in apiBody['bios_template']:
                apiBody = dict(apiBody, **btemplate[item.bios_template.replace('-tpm', '')].toDict(), **btemplate.tpm.toDict())
            else: apiBody = dict(apiBody, **btemplate[item.bios_template].toDict(), **btemplate.tpm_disabled.toDict())
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
                if re.search('(Iscsi|LocalDisk|Nvme|PchStorage|San|SdCard)', i.object_type) and apiBody['ConfiguredBootMode'] == 'Uefi':
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
            apiBody  = dict(apiBody, **atemplate[item.adapter_template].toDict())
            apiBody.pop('adapter_template')
        return apiBody

    #=======================================================
    # Fibre-Channel Adapter Policy Modification
    #=======================================================
    def fibre_channel_adapter(self, apiBody, item, kwargs):
        if apiBody.get('adapter_template'):
            atemplate= kwargs.ezdata['fibre_channel_adapter.template'].properties
            apiBody  = dict(apiBody, **atemplate[item.adapter_template].toDict())
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
        return apiBody

    #=======================================================
    # Identity Reservations
    #=======================================================
    def identity_reservations(self, ptitle, reservations, kwargs):
        #=====================================================
        # Send Begin Notification and Load Variables
        #=====================================================
        validating.begin_section(ptitle, 'pool reservations')
        kwargs.post_list = []
        #=====================================================
        # Get Existing Reservations via the API
        #=====================================================
        reservations = DotMap(reservations)
        for k, v in reservations.items():
            names         = [e for e in v.reservations.Identity]
            kwargs.method = 'get'
            kwargs.pmoid  = kwargs.isight[kwargs.org].pool[self.type][k]
            kwargs        = api_get(True, names, f'{self.type}.reservations', kwargs)
            reserve_moids = kwargs.pmoids
            #=====================================================
            # Construct apiBody Payload
            #=====================================================
            apiBody = {}
            for e in v.reservations.identities:
                for a, b in v.reservations.items():
                    if not 'Identity' == a: apiBody.update({a:b})
                apiBody.update({'Identity':e,'Pool':{'Moid':kwargs.isight[kwargs.org].pool[self.type][k],'ObjectType':v.object_type}})
                apiBody = org_map(apiBody)
                kwargs.method = 'post'
                if not reserve_moids.get(apiBody['Identity']): kwargs.post_list.append(deepcopy(apiBody))
        #=====================================================
        # POST Bulk Request if Post List > 0
        #=====================================================
        if len(kwargs.post_list) > 0:
            kwargs.uri = kwargs.ezdata[self.type].intersight_uri
            kwargs     = bulk_post_request(kwargs)
        #=====================================================
        # Send End Notification and return kwargs
        #=====================================================
        validating.end_section(ptitle, 'pool reservations')
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
        if len(names) > 0: kwargs = api_get(False, names, 'ip', kwargs)
        for i in ptype:
            if apiBody.get(i):
                if '/' in apiBody[i]['Moid']: org, pool = apiBody[i]['Moid'].split('/')
                else: org = kwargs.org; pool = apiBody[i]['Moid']
                if not kwargs.isight[org].pool['ip'].get(pool):
                    validating.error_policy_doesnt_exist(i, apiBody[i]['Moid'], self.type, 'policy', apiBody['Name'])
                org_moid = kwargs.org_moids[org].moid
                indx = next((index for (index, d) in enumerate(kwargs.results) if d.Name == pool and d.Organization.Moid == org_moid), None)
                if len(kwargs.results[indx].IpV4Config.Gateway) > 0: apiBody['AddressType']['EnableIpV4'] = True
                if len(kwargs.results[indx].IpV6Config.Gateway) > 0: apiBody['AddressType']['EnableIpV6'] = True
                apiBody[i]['Moid'] = kwargs.isight[org].pool['ip'][pool]
        return apiBody

    #=======================================================
    # IPMI over LAN Policy Modification
    #=======================================================
    def ipmi_over_lan(self, apiBody, item, kwargs):
        item = item; kwargs = kwargs
        if apiBody.get('encryption_key'):
            if os.environ.get('ipmi_key') == None:
                kwargs.sensitive_var = "ipmi_key"
                kwargs = ezfunctions.sensitive_var_value(kwargs)
                apiBody.update({'EncryptionKey':kwargs.var_value})
            else: apiBody.update({'EncryptionKey':os.environ.get('ipmi_key')})
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
        # Attach Pools/Policies to the API Body
        #=====================================================
        if apiBody.get('InitiatorIpPool'):
            ip_pool= apiBody['InitiatorIpPool']['Moid']
            if '/' in apiBody['InitiatorIpPool']['Moid']: org, pool = apiBody['InitiatorIpPool']['Moid'].split('/')
            else: org = kwargs.org; pool = apiBody['InitiatorIpPool']['Moid']
            if not kwargs.isight[org].pool['ip'].get(pool): kwargs = api_get(False, [ip_pool], 'ip', kwargs)
            apiBody['InitiatorIpPool']['Moid'] = kwargs.isight[org].pool['ip'][pool]
        names = []; plist = ['PrimaryTargetPolicy', 'SecondaryTargetPolicy']
        for p in plist:
            if apiBody.get(p):
                if '/' in apiBody[p]['Moid']: org, policy = apiBody[p]['Moid'].split('/')
                else: org = kwargs.org; policy = apiBody[p]['Moid']
                if not kwargs.isight[org].policy['iscsi_static_target'].get(policy): names.append(apiBody[p]['Moid'])
        if len(kwargs.names) > 0: kwargs = api_get(False, names, 'iscsi_static_target', kwargs)
        for p in plist:
            if apiBody.get(p):
                if '/' in apiBody[p]['Moid']: org, policy = apiBody[p]['Moid'].split('/')
                else: org = kwargs.org; policy = apiBody[p]['Moid']
                if not kwargs.isight[org].policy['iscsi_static_target'].get(policy):
                    validating.error_policy_doesnt_exist(p, apiBody[p]['Moid'], self.type, 'policy', apiBody['Name'])
                apiBody[p]['Moid'] = kwargs.isight[org].policy['iscsi_static_target'][policy]
        return apiBody

    #=======================================================
    # iSCSI Static Target Policy Modification
    #=======================================================
    def iscsi_static_target(self, apiBody, item, kwargs):
        item = item; kwargs = kwargs; apiBody['Lun'] = {'Bootable':True}
        return apiBody

    #=======================================================
    # LAN Connectivity Policy Modification
    #=======================================================
    def lan_connectivity(self, apiBody, item, kwargs):
        if not apiBody.get('PlacementMode'): apiBody.update({'PlacementMode':'custom'})
        if not apiBody.get('TargetPlatform'): apiBody.update({'TargetPlatform': 'FIAttached'})
        if item.get('IqnPool'):
            apiBody['IqnAllocationType'] = 'Pool'
            if '/' in item.iqn_pool: org, pool = item.iqn_pool.split('/')
            else: org = kwargs.org; pool = item.iqn_pool
            if not kwargs.isight[org].pool['iqn'].get(pool): kwargs = api_get(False, [item.iqn_pool], 'iqn', kwargs)
            apiBody['IqnPool']['Moid'] = kwargs.isight[org].pool['iqn'][pool]
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
                if len(item[dtype]) > 0: apiBody.update({f'PreferredIp{i}dnsServer':item[dtype][0]})
                if len(item[dtype]) > 1: apiBody.update({f'AlternateIp{i}dnsServer':item[dtype][1]})
                apiBody.pop(dtype)
        return apiBody

    #=====================================================
    #  Policies Function
    #=====================================================
    def policies(self, kwargs):
        #=====================================================
        # Send Begin Notification and Load Variables
        #=====================================================
        ptitle= ezfunctions.mod_pol_description((self.type.replace('_', ' ').title()))
        validating.begin_section(ptitle, 'policies')
        idata = DotMap(dict(pair for d in kwargs.ezdata[self.type].allOf for pair in d.properties.items()))
        pdict = deepcopy(kwargs.imm_dict.orgs[kwargs.org].policies[self.type])
        if self.type == 'port': policies = list({v.names[0]:v for v in pdict}.values())
        else: policies = list({v.name:v for v in pdict}.values())
        #=====================================================
        # Get Existing Policies
        #=====================================================
        names = []
        for i in policies:
            if self.type == 'port': names.extend([i.names[x] for x in range(0,len(i.names))])
            else: names.append(i['name'])
        kwargs = api_get(True, names, self.type, kwargs)
        kwargs.policy_results= kwargs.results
        #=====================================================
        # If Modified Patch the Policy via the Intersight API
        #=====================================================
        def policies_to_api(apiBody, kwargs):
            kwargs.qtype = self.type
            kwargs.uri   = kwargs.ezdata[self.type].intersight_uri
            if kwargs.isight[kwargs.org].policy[self.type].get(apiBody['Name']):
                kwargs.method = 'patch'
                kwargs.pmoid  = kwargs.isight[kwargs.org].policy[self.type][apiBody['Name']]
                indx = next((index for (index, d) in enumerate(kwargs.policy_results) if d['Name'] == apiBody['Name']), None)
                patch_policy = compare_body_result(apiBody, kwargs.policy_results[indx])
                if patch_policy == True:
                    kwargs.apiBody = apiBody
                    kwargs = api(kwargs.qtype).calls(kwargs)
                    kwargs.pmoids[apiBody['Name']].moid = kwargs.pmoid
                else: prCyan(f"      * Skipping {ptitle} Policy: `{apiBody['Name']}`.  Intersight Matches Configuration.  Moid: {kwargs.pmoid}")
            else: kwargs.post_list.append(deepcopy(apiBody))
            return kwargs
        #=====================================================
        # Loop through Policy Items
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
                    kwargs = policies_to_api(apiBody, kwargs)
            else:
                #=====================================================
                # Construct apiBody Payload
                #=====================================================
                apiBody = {'ObjectType':kwargs.ezdata[self.type].ObjectType}
                apiBody = build_apiBody(apiBody, idata, item, self.type, kwargs)
                kwargs = policies_to_api(apiBody, kwargs)
        #=====================================================
        # POST Bulk Request if Post List > 0
        #=====================================================
        if len(kwargs.post_list) > 0:
            kwargs.uri    = kwargs.ezdata[self.type].intersight_uri
            kwargs        = bulk_post_request(kwargs)
            for e in kwargs.results: kwargs.isight[kwargs.org].policy[self.type][e.Body.Name] = e.Body.Moid
        #=====================================================
        # Loop Thru Sub-Items
        #=====================================================
        pdict = deepcopy(kwargs.imm_dict.orgs[kwargs.org].policies[self.type])
        if self.type == 'port': kwargs.policies = list({v['names'][0]:v for v in pdict}.values())
        else: kwargs.policies = list({v['name']:v for v in pdict}.values())
        if 'port' == self.type:
            kwargs = imm('port.port_modes').port_modes(kwargs)
            kwargs = imm('port').ports(kwargs)
        elif re.search('(l|s)an_connectivity|local_user|storage|v(l|s)an', self.type):
            sub_list = ['lan_connectivity.vnics', 'local_user.users', 'san_connectivity.vhbas', 'storage.drive_groups', 'vlan.vlans', 'vsan.vsans']
            for e in sub_list:
                a, b = e.split('.')
                if a == self.type:
                    if re.search('vnics|vhbas', e): kwargs = eval(f'imm(e).vnics(kwargs)')
                    else: kwargs = eval(f'imm(e).{b}(kwargs)')
        #=====================================================
        # Send End Notification and return kwargs
        #=====================================================
        validating.end_section(ptitle, 'policies')
        return kwargs

    #=====================================================
    #  Pools Function
    #=====================================================
    def pools(self, kwargs):
        #=====================================================
        # Send Begin Notification and Load Variables
        #=====================================================
        ptitle = ezfunctions.mod_pol_description((self.type.replace('_', ' ').title()))
        validating.begin_section(ptitle, 'pool')
        kwargs.post_list = []; reservations = DotMap()
        idata = DotMap(dict(pair for d in kwargs.ezdata[self.type].allOf for pair in d.properties.items()))
        pools = list({v['name']:v for v in kwargs.imm_dict.orgs[kwargs.org].pools[self.type]}.values())
        #=====================================================
        # Get Existing Pools
        #=====================================================
        kwargs = api_get(True, [e.name for e in pools], self.type, kwargs)
        kwargs.pool_results = kwargs.results
        #=====================================================
        # Loop through Items
        #=====================================================
        for item in pools:
            #=====================================================
            # Construct apiBody Payload
            #=====================================================
            apiBody = {'ObjectType':kwargs.ezdata[self.type].ObjectType}
            apiBody = build_apiBody(apiBody, idata, item, self.type, kwargs)
            #=====================================================
            # Add Pool Specific Attributes
            #=====================================================
            if re.search('ww(n|p)n', self.type):  apiBody.update({'PoolPurpose':self.type.upper()})
            #=====================================================
            # If reservations; Build Dict and Pop reservations
            #=====================================================
            if apiBody.get('reservations'):
                reservations[apiBody['Name']].reservations= apiBody['reservations']
                reservations[apiBody['Name']].object_type = kwargs.ezdata[self.type].ObjectType
                apiBody.pop('reservations')
            #=====================================================
            # If Modified Patch the Pool via the Intersight API
            #=====================================================
            kwargs.apiBody= apiBody
            kwargs.qtype  = self.type
            kwargs.uri    = kwargs.ezdata[self.type].intersight_uri
            if kwargs.isight[kwargs.org].pool[self.type].get(apiBody['Name']):
                kwargs.method = 'patch'
                kwargs.pmoid  = kwargs.isight[kwargs.org].pool[self.type][apiBody['Name']]
                indx = next((index for (index, d) in enumerate(kwargs.pool_results) if d['Name'] == apiBody['Name']), None)
                patch_pool = compare_body_result(apiBody, kwargs.pool_results[indx])
                if patch_pool == True: kwargs = api(kwargs.qtype).calls(kwargs)
                else: prCyan(f"      * Skipping {ptitle} Pool: `{apiBody['Name']}`.  Intersight Matches Configuration.  Moid: {kwargs.pmoid}")
            else: kwargs.post_list.append(deepcopy(kwargs.apiBody))
        #=====================================================
        # POST Bulk Request if Post List > 0
        #=====================================================
        if len(kwargs.post_list) > 0:
            kwargs.uri    = kwargs.ezdata[self.type].intersight_uri
            kwargs        = bulk_post_request(kwargs)
            for e in kwargs.results: kwargs.isight[kwargs.org].pool[self.type][e.Body.Name] = e.Body.Moid
        #=====================================================
        # Loop Through Reservations if > 0
        #=====================================================
        if len(reservations) > 0: kwargs = imm.identity_reservations(ptitle, reservations, kwargs)
        #=====================================================
        # Send End Notification and return kwargs
        #=====================================================
        validating.end_section(ptitle, 'pool')
        return kwargs

    #=====================================================
    # Port Modes for Port Policies
    #=====================================================
    def port_modes(self, kwargs):
        #=====================================================
        # Loop Through Port Modes
        #=====================================================
        kwargs.post_list = []
        ezdata= kwargs.ezdata[self.type]
        p     = self.type.split('.')
        for item in kwargs.policies:
            if item.get(p[1]):
                for x in range(0,len(item['names'])):
                    kwargs.port_policy[item['names'][x]].names = []
                    for e in item[p[1]]: kwargs.port_policy[item['names'][x]].names.append(e.port_list[0])
                for i in list(kwargs.port_policy.keys()):
                    parent_moid = kwargs.isight[kwargs.org].policy['port'][i]
                    kwargs.pmoid= kwargs.isight[kwargs.org].policy['port'][i]
                    kwargs = api_get(True, kwargs.port_policy[i].names, self.type, kwargs)
                    port_modes  = kwargs.pmoids
                    port_results= deepcopy(kwargs.results)
                    for e in item[p[1]]:
                        kwargs.apiBody = {'CustomMode':e.custom_mode,'ObjectType':ezdata.ObjectType,
                                          'PortIdStart':e.port_list[0],'PortIdEnd':e.port_list[1],
                                          ezdata.parent_policy:{'Moid':parent_moid,'ObjectType':ezdata.parent_object}}
                        if e.get('slot_id'): kwargs.apiBody.update({'SlotId':e.slot_id})
                        else: kwargs.apiBody.update({'SlotId':1})
                        #=====================================================
                        # Create or Patch the Policy via the Intersight API
                        #=====================================================
                        kwargs.parent_name = i
                        if port_modes.get(parent_moid):
                            if port_modes[parent_moid].get(str(e.port_list[0])):
                                kwargs.method= 'patch'
                                kwargs.pmoid = port_modes[parent_moid][str(e.port_list[0])].moid
                            else: kwargs.method= 'post'
                        else: kwargs.method= 'post'
                        if kwargs.method == 'post': kwargs.post_list.append(deepcopy(kwargs.apiBody))
                        else:
                            indx = next((index for (index, d) in enumerate(port_results) if d['PortIdStart'] == e.port_list[0]), None)
                            patch_port = compare_body_result(kwargs.apiBody, port_results[indx])
                            if patch_port == True: kwargs = api(kwargs.qtype).calls(kwargs)
                            else:
                                ps = e.port_list[0]; pe = e.port_list[1]
                                prCyan(f"      * Skipping Port Policy: `{i}`, CustomMode: `{e.custom_mode}`,  PortIdStart: `{ps}` and PortIdEnd: `{pe}`.\n"\
                                       f"         Intersight Matches Configuration.  Moid: {kwargs.pmoid}")
        #=====================================================
        # POST Bulk Request if Post List > 0
        #=====================================================
        if len(kwargs.post_list) > 0:
            kwargs.uri    = kwargs.ezdata[self.type].intersight_uri
            kwargs        = bulk_post_request(kwargs)
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
            if re.search('port_channel', port_type): name = int(kwargs.apiBody['PcId']); key_id = 'PcId'
            else: name = int(kwargs.apiBody['PortId']); key_id = 'PortId'
            if kwargs.port_moids[port_type].get(kwargs.parent_moid):
                if kwargs.port_moids[port_type][kwargs.parent_moid].get(str(name)):
                    kwargs.method= 'patch'
                    kwargs.pmoid = kwargs.port_moids[port_type][kwargs.parent_moid][str(name)].moid
                else: kwargs.method= 'post'
            else: kwargs.method= 'post'
            kwargs.uri = kwargs.ezdata[f'port.{port_type}'].intersight_uri
            if kwargs.method == 'patch':
                indx = next((index for (index, d) in enumerate(kwargs.port_results[port_type]) if d[key_id] == name), None)
                patch_port = compare_body_result(kwargs.apiBody, kwargs.port_results[port_type][indx])
                if patch_port == True:
                    kwargs.qtype  = f'port.{port_type}'
                    kwargs        = api(kwargs.qtype).calls(kwargs)
                else:
                    prCyan(f"      * Skipping Port Policy: `{kwargs.parent_name}`, {key_id}: `{name}`."\
                           f"  Intersight Matches Configuration.  Moid: {kwargs.pmoid}")
            else:
                kwargs.plist[port_type].append({'Body':deepcopy(kwargs.apiBody), 'ClassId':'bulk.RestSubRequest',
                                                'ObjectType':'bulk.RestSubRequest', 'Verb':'POST', 'Uri':f'/v1/{kwargs.uri}'})
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
            kwargs.port_results[port_type] = kwargs.results
            return kwargs

        #=====================================================
        # Attach Ethernet/Flow/Link Policies
        #=====================================================
        def policy_update(port_type, i, x, kwargs):
            for p in ['EthNetworkControl', 'EthNetworkGroup', 'FlowControl', 'LinkAggregation', 'LinkControl']:
                p = f'{p}Policy'
                if kwargs.apiBody.get(p):
                    ptype = (snakecase(p).replace('eth_', 'ethernet_')).replace('_policy', '')
                    if '/' in kwargs.apiBody[p]['Moid']: org, policy = kwargs.apiBody[p]['Moid'].split('/')
                    else: org = kwargs.org; policy = kwargs.apiBody[p]['Moid']
                    if not kwargs.isight[org].policy[ptype].get(policy):
                        validating.error_policy_doesnt_exist(ptype, kwargs.apiBody[p]['Moid'], f'port.{port_type}', 'policy', i.names[x])
                    kwargs.apiBody[p]['Moid'] = kwargs.isight[org].policy[ptype][policy]
                    if 'Group' in p: kwargs.apiBody[p] = [kwargs.apiBody[p]]
            return kwargs
        
        #=====================================================
        # Create API Body for Port Policies
        #=====================================================
        def port_type_call(port_type, item, x, kwargs):
            ezdata = kwargs.ezdata[f'port.{port_type}']
            for i in item[port_type]:
                apiBody = {'ObjectType':ezdata.ObjectType, 'PortPolicy':{'Moid':kwargs.parent_moid,'ObjectType':'fabric.PortPolicy'}}
                kwargs.apiBody = build_apiBody(apiBody, ezdata.properties, i, f'port.{port_type}', kwargs)
                if i.get('pc_ids'):
                    if len(kwargs.apiBody['PcId']) == 2: kwargs.apiBody['PcId'] = i.pc_ids[x]
                    else: kwargs.apiBody['PcId'] = i.pc_ids[x]
                    if re.search('appliance|ethernet|fcoe', port_type): kwargs = policy_update(port_type, i, x, kwargs)
                    for x in range(len(apiBody['Ports'])):
                        if not kwargs.apiBody['Ports'][x].get('AggregatePortId'): kwargs.apiBody['Ports'][x]['AggregatePortId'] = 0
                        if not kwargs.apiBody['Ports'][x].get('SlotId'): kwargs.apiBody['Ports'][x]['SlotId'] = 1
                else:
                    if not kwargs.apiBody.get('AggregatePortId'): kwargs.apiBody['AggregatePortId'] = 0
                    if not kwargs.apiBody.get('SlotId'): kwargs.apiBody['SlotId'] = 1
                if i.get('vsan_ids'):
                    if len(i['vsan_ids']) > 1: kwargs.apiBody['VsanId'] = i['vsan_ids'][x]
                    else: kwargs.apiBody['VsanId'] = i['vsan_ids'][0]
                kwargs.apiBody.pop('Organization'); kwargs.apiBody.pop('Tags')
                if re.search('port_channel', port_type): kwargs = api_calls(port_type, kwargs)
                elif re.search('role', port_type):
                    for e in ezfunctions.vlan_list_full(i.port_list):
                        kwargs.apiBody['PortId'] = int(e)
                        kwargs = api_calls(port_type, kwargs)
            return kwargs

        #=====================================================
        # Get Policies
        #=====================================================
        def policy_list(policy, ptype, kwargs):
            orginal_policy = policy
            if '/' in policy: org, policy = policy.split('/')
            else: org = kwargs.org; policy = policy
            if not kwargs.isight[org].policy[ptype].get(policy): kwargs.cp[ptype].names.append(orginal_policy)
            return kwargs
        #=====================================================
        # Build Child Policy Map
        #=====================================================
        kwargs.cp = DotMap(); kwargs.port_types = []; kwargs.ports = []
        for k,v in kwargs.ezdata.port.allOf[0].properties.items():
            if re.search('^port_(cha|rol)', k): kwargs.port_types.append(k)
        for e in kwargs.port_types:
            kwargs.port_type[e].names = []
            for item in kwargs.policies:
                if item.get(e):
                    kwargs.ports.append(e)
                    for i in item[e]:
                        if 'port_channel' in e: kwargs.port_type[e].names.extend(i.pc_ids)
                        for k, v in i.items():
                            if re.search('^(ethernet|flow|link)_', k):
                                ptype = (k.replace('_policies', '')).replace('_policy', '')
                                if type(v) == list:
                                    for e in v: kwargs = policy_list(e, ptype, kwargs)
                                else: kwargs = policy_list(v, ptype, kwargs)
        kwargs.ports = list(numpy.unique(numpy.array(kwargs.ports)))
        for e in list(kwargs.cp.keys()):
            if len(kwargs.cp[e].names) > 0:
                names  = list(numpy.unique(numpy.array(kwargs.cp[e].names)))
                kwargs = api_get(False, names, e, kwargs)
        #=====================================================
        # Create API Body for Port Types
        #=====================================================
        kwargs.plist = DotMap()
        for item in kwargs.policies:
            for x in range(0,len(item.names)):
                for e in kwargs.ports:
                    if item.get(e):
                        kwargs.plist[e] = []
                        kwargs.parent_name = item.names[x]
                        kwargs.parent_moid = kwargs.isight[kwargs.org].policy['port'][item.names[x]]
                        kwargs = get_ports(e, item, x, kwargs)
                        port_type_call(e, item, x, kwargs)
                        if len(kwargs.plist[e]) > 0:
                            kwargs.apiBody= {'Requests':kwargs.plist[e]}
                            kwargs.method = 'post'
                            kwargs.qtype  = 'bulk_request'
                            kwargs.uri    = 'bulk/Requests'
                            kwargs        = api(kwargs.qtype).calls(kwargs)
        return kwargs

    #=====================================================
    # Build Chassis Profiles
    #=====================================================
    def profile_chassis(self, profiles, kwargs):
        ezdata = kwargs.ezdata[self.type]
        for item in profiles:
            apiBody = {'ObjectType':ezdata.ObjectType}
            for i in item.targets:
                pitems = dict(deepcopy(item), **i)
                pop_items = ['action', 'targets']
                for e in pop_items:
                    if pitems.get(e): pitems.pop(e)
                apiBody = build_apiBody(apiBody, kwargs.idata, pitems, self.type, kwargs)
                apiBody = profile_policy_bucket(apiBody, kwargs)
                if apiBody.get('SerialNumber'): apiBody = assign_physical_device(apiBody, kwargs)
                kwargs = profile_api_calls(apiBody, kwargs)
        #=====================================================
        # POST Bulk Request if Post List > 0
        #=====================================================
        if len(kwargs.post_list) > 0:
            kwargs.uri = kwargs.ezdata[self.type].intersight_uri
            kwargs     = bulk_post_request(kwargs)
        return kwargs

    #=====================================================
    # Build Chassis Profiles
    #=====================================================
    def profile_domain(self, profiles, kwargs):
        ezdata = kwargs.ezdata[self.type]
        for item in profiles:
            pdata = {'name':item.name}; plist = ['description', 'tags']
            for e in plist:
                if item.get(e): pdata.update({e:item[e]})
            apiBody = {'ObjectType':ezdata.ObjectType}
            apiBody = build_apiBody(apiBody, kwargs.idata, pdata, self.type, kwargs)
            kwargs  = profile_api_calls(apiBody, kwargs)
            if len(kwargs.post_list) > 0:
                if not kwargs.plist.get('domain'): kwargs.plist.domain = []
                kwargs.plist.domain.extend(kwargs.post_list)
                kwargs.post_list = []
            #=====================================================
            # Build apiBody for Switch Profiles
            #=====================================================
            cluster_moid = kwargs.isight[kwargs.org].profile[self.type][item.name]
            for x in range(0,2):
                sw_name = f"{item.name}-{chr(ord('@')+x+1)}"; otype = 'SwitchClusterProfile'
                if kwargs.switch_moids.get(item.name):
                    kwargs.isight[kwargs.org].profile['switch'][sw_name] = kwargs.switch_moids[item.name][sw_name].moid
                pdata = dict(deepcopy(item), **{'name':sw_name})
                apiBody = {'Name':sw_name, 'ObjectType':'fabric.SwitchProfile', otype:{'Moid':cluster_moid,'ObjectType':f'fabric.{otype}'}}
                apiBody = build_apiBody(apiBody, kwargs.idata, pdata, self.type, kwargs)
                kwargs.x_number = x; kwargs.type = 'switch'
                apiBody = profile_policy_bucket(apiBody, kwargs)
                if apiBody.get('SerialNumber'): apiBody = assign_physical_device(apiBody, kwargs)
                pop_list = ['Action', 'Description', 'Organization', 'Tags']
                for e in pop_list:
                    if apiBody.get(e): apiBody.pop(e)
                temp_results = kwargs.profile_results
                kwargs.profile_results = kwargs.switch_results[item.name]
                kwargs  = profile_api_calls(apiBody, kwargs)
                kwargs.profile_results = temp_results
                if len(kwargs.post_list) > 0:
                    if not kwargs.plist.get('switch'): kwargs.plist.switch = []
                    kwargs.plist.switch.extend(kwargs.post_list)
                    kwargs.post_list = []
        #=====================================================
        # POST Bulk Request if Post List > 0
        #=====================================================
        for e in list(kwargs.plist.keys()):
            if len(kwargs.plist[e]) > 0:
                if 'domain' == e: kwargs.uri = kwargs.ezdata[self.type].intersight_uri
                else: kwargs.uri = kwargs.ezdata[self.type].intersight_uri_switch
                kwargs.post_list = kwargs.plist[e]
                kwargs = bulk_post_request(kwargs)
        return kwargs

    #=====================================================
    # Build Chassis Profiles
    #=====================================================
    def profile_server(self, profiles, templates, kwargs):
        ezdata = kwargs.ezdata[self.type]
        for item in profiles:
            apiBody = {'ObjectType':ezdata.ObjectType}
            for i in item.targets:
                create_from_template = False; policy_bucket = False
                if item.get('create_from_template'):
                    if item.create_from_template == True: create_from_template = True
                    else: policy_bucket = True
                else: policy_bucket = True
                if item.get('ucs_server_template'):
                    if '/' in item.ucs_server_template: org, template = item.ucs_server_template
                    else: org = kwargs.org; template = item.ucs_server_template
                    if create_from_template == True:
                        if not kwargs.isight[org].profile['server_template'].get(template):
                            ptype = 'ucs_server_template'; tname = item.ucs_server_template
                            validating.error_policy_doesnt_exist(ptype, tname, i.name, self.type, 'Profile')
                else: create_from_template = False
                if create_from_template == True:
                    if not kwargs.isight[kwargs.org].profile['server'].get(i.name):
                        if not kwargs.bulk_template.get(item.ucs_server_template):
                            kwargs = bulk_template(i, item.ucs_server_template, kwargs)
                        kwargs = bulk_template_append(i, item.ucs_server_template, kwargs)
                if policy_bucket == True:
                    if item.get('ucs_server_template'):
                        pitems = dict(deepcopy(item), **templates[org][template], **i)
                    else: pitems = dict(deepcopy(item), **i)
                    pop_items = ['action', 'create_from_template', 'targets', 'ucs_server_template']
                    for e in pop_items:
                        if pitems.get(e): pitems.pop(e)
                    apiBody = {'ObjectType':ezdata.ObjectType}
                    apiBody = build_apiBody(apiBody, kwargs.idata, item, self.type, kwargs)
                    if not apiBody.get('TargetPlatform'): apiBody['TargetPlatform'] = 'FIAttached'
                    apiBody = profile_policy_bucket(apiBody, kwargs)
                    if apiBody.get('SerialNumber'): apiBody = assign_physical_device(apiBody, kwargs)
                    kwargs = profile_api_calls(apiBody, kwargs)
        #=====================================================
        # POST Bulk Request if Post List > 0
        #=====================================================
        if len(kwargs.bulk_template) > 0:
            for e in kwargs.bulk_template.keys():
                kwargs.apiBody= kwargs.bulk_template[e]
                kwargs.method = 'post'
                kwargs.qtype  = 'bulk'
                kwargs.uri    = 'bulk/MoCloners'
                kwargs = api(kwargs.qtype).calls(kwargs)
        if len(kwargs.post_list) > 0:
            kwargs.uri = kwargs.ezdata[self.type].intersight_uri
            kwargs     = bulk_post_request(kwargs)
        return kwargs

    #=====================================================
    # Build Chassis Profiles
    #=====================================================
    def profile_template(self, profiles, kwargs):
        ezdata = kwargs.ezdata[self.type]
        for item in profiles:
            apiBody = {'ObjectType':ezdata.ObjectType}
            apiBody = build_apiBody(apiBody, kwargs.idata, item, self.type, kwargs)
            if not apiBody.get('TargetPlatform'): apiBody['TargetPlatform'] = 'FIAttached'
            apiBody = profile_policy_bucket(apiBody, kwargs)
            apiBody.pop('create_template')
            if item.create_template == True: kwargs = profile_api_calls(apiBody, kwargs)
        #=====================================================
        # POST Bulk Request if Post List > 0
        #=====================================================
        if len(kwargs.post_list) > 0:
            kwargs.uri = kwargs.ezdata[self.type].intersight_uri
            kwargs     = bulk_post_request(kwargs)
        return kwargs

    #=====================================================
    #  Profiles Function
    #=====================================================
    def profiles(self, kwargs):
        #=====================================================
        # Send Begin Notification and Load Variables
        #=====================================================
        ptitle= ezfunctions.mod_pol_description((self.type.replace('_', ' ').title()))
        validating.begin_section(ptitle, 'profiles')
        names = []; kwargs.bulk_profiles = []; kwargs.cp = DotMap(); kwargs.post_list = []
        kwargs.serials = []; kwargs.templates = []
        ezdata = kwargs.ezdata[self.type]
        idata = DotMap(dict(pair for d in kwargs.ezdata[self.type].allOf for pair in d.properties.items()))
        if re.search('chassis|server', self.type):
            targets = DotMap(dict(pair for d in idata.targets['items'].allOf for pair in d.properties.items()))
            idata.pop('targets')
            idata = DotMap(dict(idata.toDict(), **targets.toDict()))
        if 'template' in self.type: profiles= list({v.name:v for v in kwargs.imm_dict.orgs[kwargs.org]['templates']['server']}.values())
        else:
            if self.type == 'domain': profiles = list({v.name:v for v in kwargs.imm_dict.orgs[kwargs.org].profiles[self.type]}.values())
            else: profiles =list({v.targets[0].name:v for v in kwargs.imm_dict.orgs[kwargs.org].profiles[self.type]}.values())
        if 'server' == self.type:
            templates = DotMap()
            for i in profiles:
                if i.get('ucs_server_template'):
                    if '/' in i.ucs_server_template: org, template = i.ucs_server_template.split('/')
                    else: org = kwargs.org; template = i.ucs_server_template
                    if not kwargs.isight[org].profile['server_template'].get(template):
                        if i.create_from_template == True: kwargs.templates.append(i.ucs_server_template)
                    if not i.create_from_template == True:
                        if not templates[org].get(template):
                            template_exist = False
                            if kwargs.imm_dict.org.get(org):
                                if kwargs.imm_dict.orgs[org].get('templates'):
                                    for e in kwargs.imm_dict.orgs[kwargs.org]['templates']['server']: templates[org][e.name] = e
                                    if templates[org].get(template): template_exist = True
                            if template_exist == False:
                                ptype = 'ucs_server_template'; tname = i.ucs_server_template
                                validating.error_policy_doesnt_exist(ptype, tname, i.name, self.type, 'Profile')
        #=====================================================
        # Compile List of Profile Names
        #=====================================================
        for item in profiles:
            if re.search('^(chassis|server)$', self.type):
                for i in item.targets:
                    names.append(i.name)
                    if i.get('serial_number'): kwargs.serials.append(i.serial_number)
            else:
                names.append(item.name)
                if item.get('serial_numbers'): kwargs.serials.extend(item.serial_numbers)
        #==================================
        # Get Moids for Profiles/Templates
        #==================================
        kwargs = api_get(True, names, self.type, kwargs)
        kwargs.profile_results = kwargs.results
        if len(kwargs.templates) > 0:
            kwargs = api_get(False, list(numpy.unique(numpy.array(kwargs.templates))), 'server_template', kwargs)
            kwargs.template_results = kwargs.results
        #==================================
        # Get Moids for Switch Profiles
        #==================================
        if 'domain' in self.type:
            kwargs.qtype = 'switch'
            kwargs.uri   = ezdata.intersight_uri_switch
            for c in names:
                kwargs.names  = []
                if kwargs.isight[kwargs.org].profile[self.type].get(c):
                    for x in range(0,2): kwargs.names.append(f"{c}-{chr(ord('@')+x+1)}")
                    kwargs.pmoid = kwargs.isight[kwargs.org].profile[self.type][c]
                    kwargs = api('switch').calls(kwargs)
                    kwargs.switch_moids[c] = kwargs.pmoids
                    kwargs.switch_results[c] = kwargs.results
        #=================================
        # Compile List of Policy Names
        #=================================
        def policy_search(item, kwargs):
            for k, v in item.items():
                if re.search('_polic(ies|y)|_pool$', k):
                    ptype = (((k.replace('_policies', '')).replace('_address_pools', '')).replace('_pool', '')).replace('_policy', '')
                    if not kwargs.cp.get(ptype): kwargs.cp[ptype].names = []
                    def policy_list(k, policy, ptype, kwargs):
                        original_policy = policy
                        if '/' in policy: org, policy = policy.split('/')
                        else: org = kwargs.org; policy = policy
                        if 'pool' in k: p = 'pool'
                        else: p = 'policy'
                        if not kwargs.isight[org][p][ptype].get(policy): kwargs.cp[ptype].names.append(original_policy)
                        return kwargs
                    if type(v) == list:
                        for e in v: kwargs = policy_list(k, e, ptype, kwargs)
                    else: kwargs = policy_list(k, v, ptype, kwargs)
            return kwargs
        #========================================
        # Get Policy Moids
        #========================================
        for item in profiles: kwargs = policy_search(item, kwargs)
        for e in list(kwargs.cp.keys()):
            if len(kwargs.cp[e].names) > 0:
                names  = list(numpy.unique(numpy.array(kwargs.cp[e].names)))
                kwargs = api_get(False, names, e, kwargs)
        if 'server' == self.type:
            if len(templates) > 0:
                original_org = kwargs.org
                for e in list(templates.keys()):
                    kwargs.org = e
                    kwargs.cp = DotMap()
                    for i in list(templates[e].keys()): kwargs = policy_search(i, kwargs)
                    for c in list(kwargs.cp.keys()):
                        #========================================
                        # Get Policy Moids
                        #========================================
                        if len(kwargs.cp[c].names) > 0:
                            names  = list(numpy.unique(numpy.array(kwargs.cp[e].names)))
                            kwargs = api_get(False, names, e, kwargs)
                kwargs.org = original_org
        #========================================
        # Get Serial Moids
        #========================================
        if len(kwargs.serials) > 0:
            kwargs.qtype        = 'serial_number'
            kwargs.names        = kwargs.serials
            kwargs.uri          = ezdata.intersight_uri_serial
            kwargs              = api(kwargs.qtype).calls(kwargs)
            kwargs.serial_moids = kwargs.pmoids
        kwargs.uri = ezdata.intersight_uri
        #=====================================================
        # Create the Profiles with the Functions
        #=====================================================
        kwargs.idata = idata; kwargs.type = self.type
        if 'chassis' == self.type:
            kwargs = imm.profile_chassis(self, profiles, kwargs)
            kwargs = deploy_chassis_server_profiles(profiles, kwargs)
        elif 'domain' == self.type:
            kwargs = imm.profile_domain(self, profiles, kwargs)
            kwargs = deploy_domain_profiles(profiles, kwargs)
        elif 'server' == self.type:
            kwargs = imm.profile_server(self, profiles, templates, kwargs)
            kwargs = deploy_chassis_server_profiles(profiles, kwargs)
        elif 'server_template' == self.type:
            kwargs = imm.profile_template(self, profiles, kwargs)
        #========================================================
        # End Function and return kwargs
        #========================================================
        validating.end_section(ptitle, 'profiles')
        return kwargs

    #=======================================================
    # SAN Connectivity Policy Modification
    #=======================================================
    def san_connectivity(self, apiBody, item, kwargs):
        if not apiBody.get('PlacementMode'): apiBody.update({'PlacementMode':'custom'})
        if item.get('wwnn_pool'):
            apiBody['WwnnAddressType'] = 'POOL'
            if '/' in item.wwnn_pool: org, pool = item.wwnn_pool.split('/')
            else: org = kwargs.org; pool = item.wwnn_pool
            if not kwargs.isight[org].pool['wwnn'].get(pool): kwargs = api_get(False, [item.wwnn_pool], 'wwnn', kwargs)
            apiBody['WwnnPool']['Moid'] = kwargs.isight[org].pool['wwnn'][pool]
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
    # Syslog Policy Modification
    #=======================================================
    def syslog(self, apiBody, item, kwargs):
        item = item; kwargs = kwargs
        if apiBody.get('LocalClients'): apiBody['LocalClients'] = [apiBody['LocalClients']]
        return apiBody

    #=======================================================
    # System QoS Policy Modification
    #=======================================================
    def system_qos(self, apiBody, item, kwargs):
        item = item
        if apiBody.get('configure_recommended_classes'):
            if apiBody['configure_recommended_classes'] == True:
                apiBody['Classes'] = kwargs.ezdata['system_qos.classes_recommended'].classes
            apiBody.pop('configure_recommended_classes')
        elif apiBody.get('configure_default_classes'):
            if apiBody['configure_default_classes'] == True:
                apiBody['Classes'] = kwargs.ezdata['system_qos.classes_default'].classes
            apiBody.pop('configure_default_classes')
        elif apiBody.get('configure_recommended_classes') == None and (apiBody.get('Classes') == None or len(apiBody.get('Classes')) == 0):
            apiBody['Classes'] = kwargs.ezdata['system_qos.classes_default'].classes
        if apiBody.get('jumbo_mtu'):
            if apiBody['jumbo_mtu'] == False:
                for x in range(apiBody['Classes']):
                    if not apiBody['Classes'][x]['Name'] == 'FC': apiBody['Classes'][x]['Mtu'] = 1500
            apiBody.pop('jumbo_mtu')
        classes = deepcopy(apiBody['Classes']); apiBody['Classes'] = []
        for e in classes:
            if type(e) == dict: apiBody['Classes'].append(e)
            else: apiBody['Classes'].append(e.toDict())
        return apiBody

    #=====================================================
    # Assign Users to Local User Policies
    #=====================================================
    def users(self, kwargs):
        #=====================================================
        # Get Existing Users
        #=====================================================
        names = []; kwargs.post_list = []; role_names = []; kwargs.cp = DotMap()
        ezdata = kwargs.ezdata[self.type]
        for i in kwargs.policies:
            if i.get('users'):
                for e in i.users: names.append(e.username); role_names.append(e.role)
        if len(names) > 0:
            names  = list(numpy.unique(numpy.array(names)))
            kwargs = api_get(True, names, self.type, kwargs)
            kwargs.user_moids   = kwargs.pmoids
            kwargs.user_results = kwargs.results
        if len(role_names) > 0:
            kwargs.names       = list(numpy.unique(numpy.array(role_names)))
            kwargs.qtype       = 'iam_role'
            kwargs.uri         = 'iam/EndPointRoles'
            kwargs             = api(kwargs.qtype).calls(kwargs)
            kwargs.role_moids  = kwargs.pmoids
            kwargs.role_results= kwargs.results
        for i in kwargs.policies:
            if i.get('users'):
                if len(names) > 0:
                    kwargs.names = [v.moid for k, v in kwargs.user_moids.items()]
                    kwargs.pmoid = kwargs.isight[kwargs.org].policy[self.type.split('.')[0]][i.name]
                    kwargs.qtype = 'user_role'
                    kwargs.uri   = 'iam/EndPointUserRoles'
                    kwargs       = api(kwargs.qtype).calls(kwargs)
                    kwargs.cp[kwargs.pmoid].moids  = kwargs.pmoids
                    kwargs.cp[kwargs.pmoid].results= kwargs.results

        #=====================================================
        # Construct API Body Users
        #=====================================================
        for e in names:
            if not kwargs.user_moids.get(e):
                apiBody = {'Name':e.username,'ObjectType':ezdata.ObjectType}
                apiBody = org_map(apiBody, kwargs.org_moids[kwargs.org].moid)
                kwargs.post_list.append(deepcopy(apiBody))
            else: prCyan(f"      * Skipping User: `{e}`.  Intersight Matches Configuration.  Moid: {kwargs.user_moids[e].moid}")
        #=====================================================
        # POST Bulk Request if Post List > 0
        #=====================================================
        if len(kwargs.post_list) > 0:
            kwargs.uri = kwargs.ezdata[self.type].intersight_uri
            kwargs     = bulk_post_request(kwargs)
        kwargs.user_moids = dict(kwargs.user_moids, **kwargs.pmoids)
        kwargs.post_list = []
        for i in kwargs.policies:
            parent_moid = kwargs.isight[kwargs.org].policy[self.type.split('.')[0]][i.name]
            if i.get('users'):
                for e in i.users:
                    kwargs.sensitive_var = f"local_user_password_{e.password}"
                    kwargs = ezfunctions.sensitive_var_value(kwargs)
                    user_moid = kwargs.user_moids[e.username].moid
                    #=====================================================
                    # Create API Body for User Role
                    #=====================================================
                    if i.get('enabled'): apiBody = {'Enabled':e.enabled,'ObjectType':'iam.EndPointUserRole'}
                    else: apiBody = {'Enabled':True,'ObjectType':'iam.EndPointUserRole'}
                    apiBody.update({
                        'EndPointRole':[{'Moid':kwargs.role_moids[e.role].moid,'ObjectType':'iam.EndPointRole'}],
                        'EndPointUser':{'Moid':user_moid,'ObjectType':'iam.EndPointUser'},
                        'EndPointUserPolicy':{'Moid':parent_moid,'ObjectType':'iam.EndPointUserPolicy'},
                        'Password':kwargs.var_value})
                    #=====================================================
                    # Create or Patch the Policy via the Intersight API
                    #=====================================================
                    if kwargs.cp[parent_moid].moids.get(user_moid):
                        kwargs.apiBody= apiBody
                        kwargs.method = 'patch'
                        kwargs.pmoid  = kwargs.cp[parent_moid].moids[user_moid].moid
                        kwargs.qtype  = 'user_role'
                        kwargs.uri    = 'iam/EndPointUserRoles'
                        kwargs = api(kwargs.qtype).calls(kwargs)
                    else: kwargs.post_list.append(deepcopy(apiBody))
        #=====================================================
        # POST Bulk Request if Post List > 0
        #=====================================================
        if len(kwargs.post_list) > 0:
            kwargs.uri = 'iam/EndPointUserRoles'
            kwargs     = bulk_post_request(kwargs)
        return kwargs

    #=======================================================
    # Virtual Media Policy Modification
    #=======================================================
    def virtual_media(self, apiBody, item, kwargs):
        item = item
        if apiBody.get('Mappings'):
            for x in range(apiBody['Mappings']):
                if apiBody['Mappings'][x].get('Password'):
                    kwargs.sensitive_var = f"vmedia_password_{apiBody['Mappings'][x]['Password']}"
                    kwargs = ezfunctions.sensitive_var_value(kwargs)
                    apiBody['Mappings'][x]['Password'] = kwargs.var_value
        return apiBody

    #=====================================================
    # Assign VLANs to VLAN Policies
    #=====================================================
    def vlans(self, kwargs):
        #=====================================================
        # Loop Through VLAN Lists to Create apiBody(s)
        #=====================================================
        def configure_vlans(e, kwargs):
            ezdata = kwargs.ezdata[self.type]
            apiBody = {'EthNetworkPolicy':{'Moid':kwargs.vlan_moid, 'ObjectType':'fabric.EthNetworkPolicy'}, 'ObjectType':ezdata.ObjectType}
            apiBody = build_apiBody(apiBody, ezdata.properties, e, self.type, kwargs)
            apiBody.pop('Organization'); apiBody.pop('Tags')
            if not apiBody.get('AutoAllowOnUplinks'): apiBody.update({'AutoAllowOnUplinks':False})
            if '/' in e.multicast_policy: org, policy = e.multicast_policy.split('/')
            else: org = kwargs.org; policy = e.multicast_policy
            if not kwargs.isight[org].policy['multicast'].get(policy):
                validating.error_policy_doesnt_exist('multicast_policy', e.multicast_policy, self.type, 'Vlans', e.vlan_list)
            apiBody['MulticastPolicy']['Moid'] = kwargs.isight[org].policy['multicast'][policy]
            if not apiBody.get('IsNative'): apiBody['IsNative'] = False
            for x in ezfunctions.vlan_list_full(e.vlan_list):
                if type(x) == str: x = int(x)
                if not len(ezfunctions.vlan_list_full(e.vlan_list)) == 1:
                    if e.name == 'vlan': apiBody['Name'] = f"{e.name}{'0'*(4 - len(str(x)))}{x}"
                    else: apiBody['Name'] = f"{e.name}-vl{'0'*(4 - len(str(x)))}{x}"
                apiBody['VlanId'] = x
                #=====================================================
                # Create or Patch the VLANs via the Intersight API
                #=====================================================
                if not kwargs.isight[kwargs.org].policy[self.type].get(str(x)): kwargs.post_list.append(deepcopy(apiBody))
                else:
                    indx = next((index for (index, d) in enumerate(kwargs.vlans_results) if d['VlanId'] == x), None)
                    patch_vlan = compare_body_result(apiBody, kwargs.vlans_results[indx])
                    kwargs.apiBody= apiBody
                    kwargs.method = 'patch'
                    kwargs.pmoid  = kwargs.isight[kwargs.org].policy[self.type][str(x)]
                    if patch_vlan == True:
                        kwargs.qtype  = self.type
                        kwargs.uri    = ezdata.intersight_uri
                        kwargs        = api(kwargs.qtype).calls(kwargs)
                    else:
                        prCyan(f"      * Skipping VLAN Policy: `{kwargs.vlan_policy}`, VLAN: `{x}`."\
                            f"  Intersight Matches Configuration.  Moid: {kwargs.pmoid}")
            return kwargs
        #=====================================================
        # Get Multicast Policies
        #=====================================================
        mcast_names = []
        for i in kwargs.policies:
            if i.get('vlans'):
                for e in i.vlans:
                    if '/' in e.multicast_policy: org, policy = e.multicast_policy.split('/')
                    else: org = kwargs.org; policy = e.multicast_policy
                    if not kwargs.isight[org].policy['multicast'].get(policy): mcast_names.append(e.multicast_policy)
        mcast_names= list(numpy.unique(numpy.array(mcast_names)))
        kwargs     = api_get(False, mcast_names, 'multicast', kwargs)
        #=====================================================
        # Loop Through VLAN Policies
        #=====================================================
        kwargs.post_list = []
        for i in kwargs.policies:
            vnames = []
            kwargs.pmoid      = kwargs.isight[kwargs.org].policy[self.type.split('.')[0]][i.name]
            kwargs.vlan_moid  = kwargs.pmoid
            kwargs.vlan_policy= i.name
            if i.get('vlans'):
                for e in i.vlans: vnames.extend(ezfunctions.vlan_list_full(e.vlan_list))
                kwargs = api_get(True, vnames, self.type, kwargs)
                kwargs.vlans_results= kwargs.results
                for e in i.vlans: kwargs = configure_vlans(e, kwargs)
        #=====================================================
        # POST Bulk Request if Post List > 0
        #=====================================================
        if len(kwargs.post_list) > 0:
            kwargs.uri    = kwargs.ezdata[self.type].intersight_uri
            kwargs        = bulk_post_request(kwargs)
        return kwargs

    #=====================================================
    # Assign VNICs to LAN Connectivity Policies
    #=====================================================
    def vnics(self, kwargs):
        #=====================================================
        # Get Policies and Pools
        #=====================================================
        ezdata = kwargs.ezdata[self.type]
        kwargs.cp = DotMap(); kwargs.post_list = []
        if self.type == 'lan_connectivity.vnics':
            vpolicy   = 'LanConnectivityPolicy'; vtype = 'vnics'
        else: vpolicy = 'SanConnectivityPolicy'; vtype = 'vhbas'
        for item in kwargs.policies:
            for i in item[vtype]:
                for k,v in i.items():
                    if re.search('_polic(ies|y)|_pools$', k):
                        ptype = (((k.replace('_policies', '')).replace('_address_pools', '')).replace('_pools', '')).replace('_policy', '')
                        if not kwargs.cp.get(ptype): kwargs.cp[ptype].names = []
                        def policy_list(k, policy, ptype, kwargs):
                            original_policy = policy
                            if '/' in policy: org, policy = policy.split('/')
                            else: org = kwargs.org; policy = policy
                            if 'pool' in k: p = 'pool'
                            else: p = 'policy'
                            if not kwargs.isight[org][p][ptype].get(policy): kwargs.cp[ptype].names.append(original_policy)
                            return kwargs
                        if type(v) == list:
                            for e in v: kwargs = policy_list(k, e, ptype, kwargs)
                        else: kwargs = policy_list(k, v, ptype, kwargs)
        for e in list(kwargs.cp.keys()):
            if len(kwargs.cp[e].names) > 0:
                names  = list(numpy.unique(numpy.array(kwargs.cp[e].names)))
                kwargs = api_get(False, names, e, kwargs)
        #=====================================================
        # Create API Body for vNICs
        #=====================================================
        for item in kwargs.policies:
            cp_moid = kwargs.isight[kwargs.org].policy[self.type.split('.')[0]][item.name]
            names   = []
            for i in item[vtype]: names.extend(i.names)
            kwargs = api_get(True, names, self.type, kwargs)
            vnic_results= kwargs.results
            for i in item[vtype]:
                for x in range(len(i.names)):
                    apiBody = {vpolicy:{'Moid':cp_moid,'ObjectType':f'vnic.{vpolicy}'}, 'ObjectType':ezdata.ObjectType}
                    apiBody = build_apiBody(apiBody, ezdata.properties, i, self.type, kwargs)
                    apiBody.update({'Name':i.names[x]})
                    apiBody.pop('Organization'); apiBody.pop('Tags')
                    apiBody['Order'] = i.placement.pci_order[x]
                    if apiBody['Placement'].get('Order'): apiBody['Placement'].pop('Order')
                    for k, v in i.items():
                        if re.search('_polic(ies|y)|_pools$', k):
                            ptype = (((k.replace('_policies', '')).replace('_address_pools', '')).replace('_pools', '')).replace('_policy', '')
                            if type(v) == list:
                                if len(v) >= 2: pname = v[x]
                                else: pname = v[0]
                            else: pname = v
                            if '/' in pname: org, policy = pname.split('/')
                            else: org = kwargs.org; policy = pname
                            if 'pool' in k: p = 'pool'
                            else: p = 'policy'
                            if not kwargs.isight[org][p][ptype].get(policy):
                                validating.error_policy_doesnt_exist(ptype, pname, self.type, 'policy', i.names[x])
                            apiBody[ezdata.properties[k].intersight_api.split(':')[1]]['Moid'] = kwargs.isight[org][p][ptype][policy]
                    if 'vnics' in self.type:
                        if not apiBody.get('Cdn'): apiBody.update({'Cdn':{'Value':i.names[x],'Source':'vnic','ObjectType':'vnic.Cdn'}})
                        apiBody['FabricEthNetworkGroupPolicy'] = [apiBody['FabricEthNetworkGroupPolicy']]
                        if apiBody.get('StaticMacAddress'): apiBody['StaticMacAddress'] = apiBody['StaticMacAddress'][x]
                    else:
                        def zone_update(pname, ptype, kwargs):
                            if '/' in pname: org, policy = pname.split('/')
                            else: org = kwargs.org; policy = pname
                            if not kwargs.isight[org].policy[ptype].get(policy):
                                validating.error_policy_doesnt_exist(ptype, pname, self.type, 'policy', i.names[x])
                            kwargs.zbody['Moid'] = kwargs.isight[org].policy[ptype][policy]
                            return kwargs.zbody
                        if i.get('fc_zone_policies'):
                            kwargs.zbody= deepcopy(apiBody['FcZonePolicies'])
                            apiBody['FcZonePolicies'] = []
                            if len(i.names) == 2:
                                half = len(i.fc_zone_policies)//2
                                if x == 0: zlist = i.fc_zone_policies[half:]
                                else: zlist = i.fc_zone_policies[:half]
                                for e in zlist: apiBody['FcZonePolicies'].append(zone_update(e, 'fc_zone', kwargs))
                            else:
                                for e in i.fc_zone_policies: apiBody['FcZonePolicies'].append(zone_update(e, 'fc_zone', kwargs))
                        if apiBody.get('StaticWwpnAddress'): apiBody['StaticWwpnAddress'] = apiBody['StaticWwpnAddress'][x]
                    if x == 0: side = 'A'
                    else: side = 'B'
                    apiBody.update({'Placement':{'Id':'MLOM','ObjectType':'vnic.PlacementSettings','PciLink':0,'SwitchId':side,'Uplink':0}})
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
                    kwargs.apiBody= apiBody
                    kwargs.uri    = ezdata.intersight_uri
                    if kwargs.isight[kwargs.org].policy[self.type].get(i.names[x]):
                        kwargs.method = 'patch'
                        kwargs.pmoid  = kwargs.isight[kwargs.org].policy[self.type][i.names[x]]
                        indx = next((index for (index, d) in enumerate(vnic_results) if d['Name'] == i.names[x]), None)
                        patch_vsan = compare_body_result(kwargs.apiBody, vnic_results[indx])
                        if patch_vsan == True:
                            kwargs.qtype = self.type
                            kwargs       = api(kwargs.qtype).calls(kwargs)
                        else:
                            prCyan(f"      * Skipping {vpolicy}: `{item.name}`, VNIC: `{i.names[x]}`."\
                                f"  Intersight Matches Configuration.  Moid: {kwargs.pmoid}")
                    else: kwargs.post_list.append(deepcopy(kwargs.apiBody))
        #=====================================================
        # POST Bulk Request if Post List > 0
        #=====================================================
        if len(kwargs.post_list) > 0:
            kwargs.uri    = ezdata.intersight_uri
            kwargs        = bulk_post_request(kwargs)
        return kwargs

    #=====================================================
    # Assign VSANs to VSAN Policies
    #=====================================================
    def vsans(self, kwargs):
        #=====================================================
        # Loop Through VLAN Lists
        #=====================================================
        def configure_vsans(e, kwargs):
            ezdata = kwargs.ezdata[self.type]
            apiBody = {'FcNetworkPolicy':{'Moid':kwargs.vsan_moid, 'ObjectType':'fabric.FcNetworkPolicy'}, 'ObjectType':ezdata.ObjectType}
            apiBody = build_apiBody(apiBody, ezdata.properties, e, self.type, kwargs)
            apiBody.pop('Organization'); apiBody.pop('Tags')
            if not apiBody.get('VsanScope'): apiBody['VsanScope'] = 'Uplink'
            if not apiBody.get('FcoeVlan'): apiBody['FcoeVlan'] = apiBody['VsanId']
            #=====================================================
            # Create or Patch the VLANs via the Intersight API
            #=====================================================
            if not kwargs.isight[kwargs.org].policy[self.type].get(str(apiBody['VsanId'])): kwargs.post_list.append(deepcopy(apiBody))
            else:
                indx = next((index for (index, d) in enumerate(kwargs.vsans_results) if d['VsanId'] == apiBody['VsanId']), None)
                patch_vsan = compare_body_result(apiBody, kwargs.vsans_results[indx])
                if patch_vsan == True:
                    kwargs.apiBody= apiBody
                    kwargs.method = 'patch'
                    kwargs.pmoid  = kwargs.isight[kwargs.org].policy[self.type][str(apiBody['VsanId'])]
                    kwargs.qtype  = self.type
                    kwargs.uri    = ezdata.intersight_uri
                    kwargs        = api(kwargs.qtype).calls(kwargs)
                else:
                    prCyan(f"      * Skipping VSAN Policy: `{kwargs.vsan_policy}`, VSAN: `{apiBody['VsanId']}`."\
                           f"  Intersight Matches Configuration.  Moid: {kwargs.pmoid}")
            return kwargs

        #=====================================================
        # Loop Through VSAN Policies
        #=====================================================
        kwargs.post_list = []
        for i in kwargs.policies:
            vnames = []
            kwargs.vsan_policy = i.name
            kwargs.pmoid = kwargs.isight[kwargs.org].policy[self.type.split('.')[0]][i.name]
            kwargs.vsan_moid = kwargs.pmoid
            if i.get('vsans'):
                for e in i.vsans: vnames.append(e.vsan_id)
                kwargs = api_get(True, vnames, self.type, kwargs)
                kwargs.vsans_results= kwargs.results
                #=====================================================
                # Create API Body for VSANs
                #=====================================================
                for e in i.vsans: kwargs = configure_vsans(e, kwargs)

        #=====================================================
        # POST Bulk Request if Post List > 0
        #=====================================================
        if len(kwargs.post_list) > 0:
            kwargs.uri    = kwargs.ezdata[self.type].intersight_uri
            kwargs        = bulk_post_request(kwargs)
        return kwargs

#======================================================
# Function - API Get Calls
#======================================================
def api_get(empty, names, otype, kwargs):
    original_org = kwargs.org
    kwargs.glist = DotMap()
    for e in names:
        if '/' in names: org, policy = e.split('/')
        else: org = kwargs.org; policy = e
        if not kwargs.glist[org].names: kwargs.glist[org].names = []
        kwargs.glist[org].names.append(policy)
    orgs = list(kwargs.glist.keys())
    results = []
    pmoids  = DotMap()
    for org in orgs:
        kwargs.org = org
        kwargs.names = kwargs.glist[org].names
        kwargs.method= 'get'
        kwargs.qtype = otype
        kwargs.uri   = kwargs.ezdata[otype].intersight_uri
        kwargs       = api(kwargs.qtype).calls(kwargs)
        if empty == False and kwargs.results == []: empty_results(kwargs)
        else:
            if kwargs.ezdata[otype].get('intersight_type'):
                for k, v in kwargs.pmoids.items(): kwargs.isight[org][kwargs.ezdata[otype].intersight_type][otype][k] = v.moid
            if len(kwargs.results) > 0:
                results.extend(kwargs.results)
                pmoids = DotMap(dict(pmoids.toDict(), **kwargs.pmoids.toDict()))
    kwargs.org    = original_org
    kwargs.pmoids = pmoids
    kwargs.results= results
    return kwargs

#======================================================
# Function - Assign Physical Device
#======================================================
def assign_physical_device(apiBody, kwargs):
    if kwargs.type == 'switch':
        if len(apiBody['SerialNumber']) == 2: serial = apiBody['SerialNumber'][kwargs.x_number]
        else: serial = 'BLAH'
    else: serial = apiBody['SerialNumber']
    if re.search(serial_regex, serial): serial_true = True
    else: serial_true = False
    if serial_true == True:
        if kwargs.serial_moids.get(serial):
            serial_moid = kwargs.serial_moids[serial].moid
            sobject     = kwargs.serial_moids[serial]['object_type']
        else: validating.error_serial_number(apiBody['Name'], serial)
        ptype = kwargs.type.capitalize()
        apiBody.update({f'Assigned{ptype}':{'Moid':serial_moid, 'ObjectType':sobject}})
        apiBody = dict(sorted(apiBody.items()))
    apiBody.pop('SerialNumber')
    return apiBody

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
                # if not apiBody.get(x[1]): apiBody.update({x[1]:{'ObjectType':x[2]}})
                # apiBody[x[1]].update({x[3]:v})
                if not apiBody.get(x[1]): apiBody.update({x[1]:{x[3]:v, 'ObjectType':x[2]}})
            elif '$pbucket:' in idata[k].intersight_api:
                if not apiBody.get('PolicyBucket'): apiBody['PolicyBucket'] = []
                x = idata[k].intersight_api.split(':')
                apiBody['PolicyBucket'].append({x[2]:v,'policy':k,'ObjectType':x[1]})
            else: apiBody.update({idata[k].intersight_api:v})
        elif idata[k].type == 'array':
            if re.search('boolean|string|integer',  idata[k]['items'].type):
                if '$ref:' in idata[k]['items'].intersight_api:
                    x = idata[k]['items'].intersight_api.split(':')
                    if not apiBody.get(x[1]): apiBody.update({x[1]:{'ObjectType':x[2]}})
                    apiBody[x[1]].update({x[3]:v})
                elif '$pbucket:' in idata[k].intersight_api:
                    if not apiBody.get('PolicyBucket'): apiBody['PolicyBucket'] = []
                    x = idata[k].intersight_api.split(':')
                    apiBody['PolicyBucket'].append({x[2]:v,'policy':k,'ObjectType':x[1]})
                else:
                    apiBody[idata[k]['items'].intersight_api] = []
                    for e in v: apiBody[idata[k]['items'].intersight_api].append(e)
            else:
                apiBody[idata[k]['items'].intersight_api] = []
                for e in v:
                    if type(e) == str:
                        apiBody[idata[k]['items'].intersight_api].append(e)
                    else:
                        idict = {'ObjectType':idata[k]['items'].ObjectType}
                        for a, b in idata[k]['items'].properties.items():
                            if re.search('boolean|string|integer', b.type):
                                if a in e: idict.update({b.intersight_api:e[a]})
                            elif b.type == 'object' and a in e:
                                idict.update({b.intersight_api:{'ObjectType':b.ObjectType}})
                                for c, d in b.properties.items():
                                    if e[a].get(c): idict[b.intersight_api].update({d.intersight_api:e[a][c]})
                            elif b.type == 'array' and a in e:
                                #print('not accounted for')
                                idict[b.intersight_api] = e[a]
                        apiBody[idata[k]['items'].intersight_api].append(idict)
        elif idata[k].type == 'object':
            apiBody[idata[k].intersight_api] = {'ObjectType':idata[k].ObjectType}
            for a, b in idata[k].properties.items():
                if b.type == 'array':
                    if v.get(a): apiBody[idata[k].intersight_api].update({b.intersight_api:v[a]})
                elif b.type == 'object':
                    print(f'2 matched {b.type}')
                    #exit()
                elif v.get(a): apiBody[idata[k].intersight_api].update({b.intersight_api:v[a]})

    #=====================================================
    # Validate all Parameters are String if BIOS
    #=====================================================
    if ptype == 'bios':
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
    #print(json.dumps(apiBody, indent=4))
    return apiBody

#=====================================================
# Process API Results
#=====================================================
def build_pmoid_dictionary(api_results, kwargs):
    apiDict = DotMap()
    if api_results.get('Results'):
        for i in api_results.Results:
            if i.get('Body'): i = i.Body
            if i.get('VlanId'): iname = str(i.VlanId)
            elif i.get('PcId'): iname = str(i.PcId)
            elif i.get('PortId'): iname = str(i.PortId)
            elif i.ObjectType == 'asset.DeviceRegistration': iname = i.Serial[0]
            elif i.get('Serial'): iname = i.Serial
            elif i.get('VsanId'): iname = str(i.VsanId)
            elif i.get('Answers'): iname = i.Answers.Hostname
            elif i.get('Name'): iname = i.Name
            elif kwargs.qtype == 'upgrade':
                if i.Status == 'IN_PROGRESS': iname = kwargs.srv_moid
            elif i.get('SocketDesignation'): iname = i.Dn
            elif i.get('EndPointUser'): iname = i.EndPointUser.Moid
            elif i.get('PortIdStart'): iname = str(i.PortIdStart)
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
def bulk_post_request(kwargs):
    kwargs.apiBody = {'Requests':[]}
    for e in kwargs.post_list:
        kwargs.apiBody['Requests'].append(
            {'Body':e, 'ClassId':'bulk.RestSubRequest', 'ObjectType':'bulk.RestSubRequest', 'Verb':'POST', 'Uri':f'/v1/{kwargs.uri}'})
    kwargs.method = 'post'
    kwargs.qtype  = 'bulk_request'
    kwargs.uri    = 'bulk/Requests'
    kwargs        = api(kwargs.qtype).calls(kwargs)
    return kwargs

#=====================================================
# Create Bulk Server Template
#=====================================================
def bulk_template(i, server_template, kwargs):
    if not kwargs.isight[kwargs.org].profile['server_template'].get(server_template):
        validating.error_policy_doesnt_exist('template', server_template, i.name, kwargs.type, 'Profile')
    tmoid = kwargs.isight[kwargs.org].profile['server_template'][server_template]
    kwargs.bulk_template[server_template] = {
        'ObjectType': 'bulk.MoCloner', 'Sources':[{'Moid':tmoid, 'ObjectType':'server.ProfileTemplate'}], 'Targets':[]}
    return kwargs

#=====================================================
# Create Bulk Server Template
#=====================================================
def bulk_template_append(i, template, kwargs):
    if kwargs.serial_moids.get(i.serial_number):
        serial_moid= kwargs.serial_moids[i.serial_number].moid
        sobject    = kwargs.serial_moids[i.serial_number]['object_type']
    else: validating.error_serial_number(kwargs.name, serial_moid)
    idict = {'AssignedServer':{'Moid':serial_moid,'ObjectType':sobject}, 'Description': i.description, 'Name':i.name,
            'Organization': {}, 'ObjectType':'server.Profile', 'ServerAssignmentMode': 'Static'}
    idict = org_map(idict, kwargs.org_moids[kwargs.org].moid)
    kwargs.bulk_template[template]['Targets'].append(idict)
    return kwargs

#=======================================================
# Add Organization Key Map to Dictionaries
#=======================================================
def compare_body_result(apiBody, result):
    if apiBody.get('PolicyBucket'):
        apiBody['PolicyBucket'] = sorted(apiBody['PolicyBucket'], key=lambda item: item['ObjectType'])
        result['PolicyBucket'] = sorted(result['PolicyBucket'], key=lambda item: item['ObjectType'])
    patch_return = False
    for k, v in apiBody.items():
        if type(v) == dict:
            for a,b in v.items():
                if not result[k][a] == b: patch_return = True
        elif type(v) == list:
            count = 0
            for e in v:
                if type(e) == dict:
                    for a, b in e.items():
                        if type(b) == dict:
                            for c, d in b.items():
                                if not result[k][count][a][c] == d: patch_return = True
                        else:
                            if 'Password' in a: skip = 1
                            elif not result[k][count][a] == b: patch_return = True
                elif type(e) == list:
                    prRed(e)
                    prRed('compare_body_result; not accounted for')
                    sys.exit(1)
                else:
                    if not result[k][count] == e: patch_return = True
                count += 1
        else:
            if not result[k] == v: patch_return = True
    return patch_return

#======================================================
# Function - Deploy Domain Profile(s) if Action is Deploy
#======================================================
def deploy_domain_profiles(profiles, kwargs):
    deploy_profiles = False
    for item in profiles:
        for x in range(0,2):
            if item.get('action') and item.get('serial_numbers'):
                if item.action == 'Deploy' and re.search(serial_regex, item.serial_numbers[x]):
                    pname = f"{item.name}-{chr(ord('@')+x+1)}"
                    kwargs.method = 'get_by_moid'
                    kwargs.pmoid  = kwargs.isight[kwargs.org].profile['switch'][pname]
                    kwargs.qtype  = 'switch'
                    kwargs.uri    = kwargs.ezdata['domain'].intersight_uri_switch
                    kwargs = api(kwargs.qtype).calls(kwargs)
                    results= kwargs.results
                    if len(results.ConfigChanges.Changes) > 0 or results.ConfigContext.ConfigState == 'Assigned':
                        deploy_profiles = True
                        kwargs.cluster_update[item.name].pending_changes = True; break
    pending_changes = False
    for e in kwargs.cluster_pending.keys():
        if kwargs[e].cluster_pending == True: pending_changes = True
    if deploy_profiles == True: prLightPurple(f'\n{"-"*81}\n')
    if pending_changes == True: prCyan('      * Sleeping for 120 Seconds'); time.sleep(120)
    for item in profiles:
        if kwargs.cluster_update[item.name].pending_changes == True:
            for x in range(0,2):
                pname = f"{item.name}-{chr(ord('@')+x+1)}"
                prGreen(f'    - Beginning Profile Deployment for {pname}')
                kwargs.apiBody= {'Action':'Deploy'}
                kwargs.method = 'patch'
                kwargs.pmoid  = kwargs.isight[kwargs.org].profile['switch'][pname]
                kwargs = api('switch').calls(kwargs)
    if deploy_profiles == True: prLightPurple(f'\n{"-"*81}\n'); time.sleep(60)
    for item in profiles:
        if kwargs.cluster_update[item.name].pending_changes == True:
            for x in range(0,2):
                pname = f"{item.name}-{chr(ord('@')+x+1)}"
                kwargs.method= 'get_by_moid'
                kwargs.pmoid = kwargs.isight[kwargs.org].profile['switch'][pname]
                kwargs.qtype = 'switch'
                deploy_complete = False
                while deploy_complete == False:
                    kwargs = api(kwargs.qtype).calls(kwargs)
                    if kwargs.results.ConfigContext.ControlAction == 'No-op':
                        prGreen(f'    - Completed Profile Deployment for {pname}')
                        deploy_complete = True
                    else:  prCyan(f'      * Deploy Still Occuring on {pname}.  Waiting 120 seconds.'); time.sleep(120)
    if deploy_profiles == True: prLightPurple(f'\n{"-"*81}\n')
    return kwargs

#======================================================
# Function - Deploy Chassis/Server Profile if Action is Deploy
#======================================================
def deploy_chassis_server_profiles(profiles, kwargs):
    pending_changes = False
    kwargs.profile_update = DotMap()
    for item in profiles:
        for i in item.targets:
            if item.get('action') and i.get('serial_number'):
                if item.action == 'Deploy' and re.search(serial_regex, i.serial_number):
                    kwargs.profile_update[i.name] = DotMap(dict(item.toDict(), **i.toDict()))
                    kwargs.profile_update[i.name].pending_changes = 'Blank'
    if len(kwargs.profile_update) > 0:
        kwargs = api_get(False, list(kwargs.profile_update.keys()), kwargs.type, kwargs)
        profile_results = kwargs.results
        for e in list(kwargs.profile_update.keys()):
            indx = next((index for (index, d) in enumerate(profile_results) if d['Name'] == e), None)
            if len(profile_results[indx].ConfigChanges.Changes) > 0 or profile_results[indx].ConfigContext.ConfigState == 'Assigned':
                if pending_changes == False: pending_changes = 'Deploy'
                kwargs.profile_update[e].pending_changes = True
            elif len(profile_results[indx].ConfigChanges.PolicyDisruptions) > 0:
                if pending_changes == False: pending_changes = True
                kwargs.profile_update[e].pending_changes = 'Activate'
        if pending_changes == True:
            prLightPurple(f'\n{"-"*81}\n')
            deploy_pending = False
            for e in list(kwargs.profile_updates.keys()):
                if kwargs.profile_update[e].pending_changes == 'Deploy': deploy_pending = True
            if deploy_pending == True:
                if 'server' == kwargs.type:  prLightPurple('    * Pending Changes.  Sleeping for 120 Seconds'); time.sleep(120)
                else:  prLightPurple('    * Pending Changes.  Sleeping for 60 Seconds'); time.sleep(60)
            for e in list(kwargs.profile_update.keys()):
                if kwargs.profile_update[e].pending_changes == 'Deploy':
                    prGreen(f'    - Beginning Profile Deployment for `{e}`.')
                    kwargs.apiBody= {'Action':'Deploy'}
                    kwargs.method = 'patch'
                    kwargs.pmoid  = kwargs.isight[kwargs.org].profile[kwargs.type][e]
                    kwargs = api(kwargs.type).calls(kwargs)
                else: prLightPurple(f'    - Skipping Profile Deployment for `{e}`.  No Pending Changes.')
            if deploy_pending == True:
                if 'server' == kwargs.type:  prLightPurple('    * Deploying Changes.  Sleeping for 600 Seconds'); time.sleep(600)
                else:  prLightPurple('    * Deploying Changes.  Sleeping for 60 Seconds'); time.sleep(60)
            for e in list(kwargs.profile_update.keys()):
                if kwargs.profile_update[e].pending_changes == 'Deploy':
                    deploy_complete= False
                    while deploy_complete == False:
                        kwargs.method = 'get_by_moid'
                        kwargs.pmoid  = kwargs.isight[kwargs.org].profile[kwargs.type][e]
                        kwargs = api(kwargs.qtype).calls(kwargs)
                        if kwargs.results.ConfigContext.ControlAction == 'No-op':
                            deploy_complete = True
                            if re.search('^(chassis)$', kwargs.type): prGreen(f'    - Completed Profile Deployment for `{e}`.')
                        else: 
                            if 'server' == kwargs.type: prCyan(f'      * Deploy Still Occuring on `{e}`.  Waiting 120 seconds.'); time.sleep(120)
                            else: prCyan(f'      * Deploy Still Occuring on `{e}`.  Waiting 60 seconds.'); time.sleep(60)
            if 'server' == kwargs.type:
                prLightPurple(f'\n{"-"*81}\n')
                names = []
                for e in list(kwargs.profile_update.keys()):
                    if not kwargs.profile_update[e].pending_changes == 'Blank': names.append(e)
                if len(names) > 0:
                    kwargs = api_get(False, names, kwargs.type, kwargs)
                    profile_results = kwargs.results
                for e in list(kwargs.profile_update.keys()):
                    if not kwargs.profile_update[e].pending_changes == 'Blank':
                        indx = next((index for (index, d) in enumerate(profile_results) if d['Name'] == e), None)
                        if len(profile_results[indx].ConfigChanges.PolicyDisruptions) > 0:
                            prGreen(f'    - Beginning Profile Activation for `{e}`.')
                            kwargs.apiBody= {'ScheduledActions':[{'Action':'Activate', 'ProceedOnReboot':True}]}
                            kwargs.method = 'patch'
                            kwargs.pmoid  = kwargs.isight[kwargs.org].profile[kwargs.type][e]
                            kwargs = api(kwargs.qtype).calls(kwargs)
                        else:
                            prLightPurple(f'    - Skipping Profile Activation for `{e}`.  No Pending Changes.')
                            kwargs.profile_update[e].pending_changes = 'Blank'
                prLightPurple(f'\n{"-"*81}\n')
                prLightPurple('    * Pending Activitions.  Sleeping for 600 Seconds'); time.sleep(600)
                for e in list(kwargs.profile_update.keys()):
                    if not kwargs.profile_update[e].pending_changes == 'Blank':
                        deploy_complete = False
                        while deploy_complete == False:
                            kwargs.method = 'get_by_moid'
                            kwargs.pmoid  = kwargs.isight[kwargs.org].profile[kwargs.type][e]
                            kwargs.qtype  = kwargs.type
                            kwargs = api(kwargs.type).calls(kwargs)
                            results = DotMap(kwargs['results'])
                            if results.ConfigContext.ControlAction == 'No-op':
                                prGreen(f'    - Completed Profile Activiation for `{e}`.')
                                deploy_complete = True
                            else:  prCyan(f'      * Activiation Still Occuring on `{e}`.  Waiting 120 seconds.'); time.sleep(120)
            prLightPurple(f'\n{"-"*81}\n')
    return kwargs

#======================================================
# Function - Exit on Empty Results
#======================================================
def empty_results(kwargs):
        prRed(f"The API Query Results were empty for {kwargs.uri}.  Exiting..."); sys.exit(1)

#=======================================================
# Add Organization Key Map to Dictionaries
#=======================================================
def org_map(apiBody, org_moid):
    apiBody.update({'Organization':{'Moid':org_moid, 'ObjectType':'organization.Organization'}})
    return apiBody

#=======================================================
# Profile Creation Function
#=======================================================
def profile_api_calls(apiBody, kwargs):
    if kwargs.isight[kwargs.org].profile[kwargs.type].get(apiBody['Name']):
        kwargs.method = 'patch'
        kwargs.pmoid  = kwargs.isight[kwargs.org].profile[kwargs.type][apiBody['Name']]
        indx = next((index for (index, d) in enumerate(kwargs.profile_results) if d['Name'] == apiBody['Name']), None)
        patch_port = compare_body_result(apiBody, kwargs.profile_results[indx])
        if patch_port == True:
            kwargs.apiBody= apiBody
            kwargs.qtype  = kwargs.type
            kwargs        = api(kwargs.qtype).calls(kwargs)
        else:
            if 'server_template' in kwargs.type: ntitle = 'Server Profile Template'
            else: ntitle = f'{kwargs.type.title()} Profile'
            prCyan(f"      * Skipping {ntitle}: `{apiBody['Name']}`.  Intersight Matches Configuration.  Moid: {kwargs.pmoid}")
    else: kwargs.post_list.append(deepcopy(apiBody))
    return kwargs

#=====================================================
# Assign Moid to Policy in Bucket
#=====================================================
def profile_policy_bucket(apiBody, kwargs):
    for x in range(len(apiBody['PolicyBucket'])):
        ptype = ((apiBody['PolicyBucket'][x]['policy']).replace('_policy', '')).replace('_policies', '')
        apiBody['PolicyBucket'][x].pop('policy')
        if kwargs.type == 'switch':
            if re.search('-A', apiBody['Name']): f = 0
            else: f = 1
        if type(apiBody['PolicyBucket'][x]['Moid']) == list:
            if len(apiBody['PolicyBucket'][x]['Moid']) == 2: opolicy = apiBody['PolicyBucket'][x]['Moid'][f]
            else: opolicy = apiBody['PolicyBucket'][x]['Moid'][0]
        else: opolicy = apiBody['PolicyBucket'][x]['Moid']
        if '/' in opolicy: org, policy = opolicy.split('/')
        else: org = kwargs.org; policy = opolicy
        if not kwargs.isight[org].policy[ptype].get(policy):
            validating.error_policy_doesnt_exist(ptype, opolicy, kwargs.type, 'profile', apiBody['Name'])
        apiBody['PolicyBucket'][x]['Moid'] = kwargs.isight[org].policy[ptype][policy]
    if apiBody.get('UuidPool'):
        apiBody['UuidAddressType'] = 'POOL'
        if '/' in apiBody.get('UuidPool'): org, pool = apiBody['UuidPool']['Moid'].split('/')
        else: org = kwargs.org; pool = apiBody['UuidPool']['Moid']
        if not kwargs.isight[org].pool['uuid'].get(pool):
            validating.error_policy_doesnt_exist('uuid', apiBody['UuidPool']['Moid'], kwargs.type, 'profile', apiBody['Name'])
        apiBody['UuidPool']['Moid'] = kwargs.isight[org].pool['uuid'][pool]
    return apiBody
