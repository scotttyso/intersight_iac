#=============================================================================
# Source Modules
#=============================================================================
def prRed(skk): print("\033[91m {}\033[00m" .format(skk))
import sys
try:
    from classes import ezfunctions, pcolor, validating
    from intersight_auth import IntersightAuth
    from copy import deepcopy
    from dotmap import DotMap
    from stringcase import snakecase
    import json, numpy, os, re, requests, time, urllib3
except ImportError as e:
    prRed(f'!!! ERROR !!!\n{e.__class__.__name__}')
    prRed(f" Module {e.name} is required to run this script")
    prRed(f" Install the module using the following: `pip install {e.name}`")
    sys.exit(1)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
serial_regex = re.compile('^[A-Z]{3}[2-3][\\d]([0][1-9]|[1-4][0-9]|[5][0-3])[\\dA-Z]{4}$')
part1 = 'adapter_configuration|bios|boot_order|(ethernet|fibre_channel)_adapter|firmware|imc_access|ipmi_over_lan|iscsi_(boot|static_target)'
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
        def api_calls(kwargs):
            #=====================================================
            # Perform the apiCall
            #=====================================================
            api_args= kwargs.api_args
            api_auth= kwargs.api_auth
            moid    = kwargs.pmoid
            payload = kwargs.api_body
            retries = 3
            uri     = kwargs.uri
            url     = kwargs.args.url
            for i in range(retries):
                try:
                    def send_error():
                        prRed(json.dumps(kwargs.api_body, indent=4))
                        prRed(kwargs.api_body)
                        prRed(f'!!! ERROR !!!')
                        if kwargs.method == 'get_by_moid': prRed(f'  URL: {url}/api/v1/{uri}/{moid}')
                        elif kwargs.method ==    'delete': prRed(f'  URL: {url}/api/v1/{uri}/{moid}')
                        elif kwargs.method ==       'get': prRed(f'  URL: {url}/api/v1/{uri}{api_args}')
                        elif kwargs.method ==     'patch': prRed(f'  URL: {url}/api/v1/{uri}/{moid}')
                        elif kwargs.method ==      'post': prRed(f'  URL: {url}/api/v1/{uri}')
                        prRed(f'  Running Process: {kwargs.method} {kwargs.qtype}')
                        prRed(f'    Error status is {status}')
                        for k, v in (response.json()).items(): prRed(f"    {k} is '{v}'")
                        sys.exit(1)
                    if 'get_by_moid' in kwargs.method: response =  requests.get(f'{url}/api/v1/{uri}/{moid}', auth=api_auth)
                    elif 'delete' in kwargs.method:    response =requests.delete(f'{url}/api/v1/{uri}/{moid}', auth=api_auth)
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
                            pcolor.Purple('     **NOTICE** Profile in Validating State.  Sleeping for 45 Seconds and Retrying.')
                            time.sleep(45)
                            continue
                        else: send_error()
                    elif not re.search('(20[0-9])', str(status)): send_error()
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
            if int(debug_level) >= 1: pcolor.Cyan(response)
            if int(debug_level)>= 5:
                if kwargs.method == 'get_by_moid': pcolor.Cyan(f'  URL: {url}/api/v1/{uri}/{moid}')
                elif kwargs.method ==       'get': pcolor.Cyan(f'  URL: {url}/api/v1/{uri}{api_args}')
                elif kwargs.method ==     'patch': pcolor.Cyan(f'  URL: {url}/api/v1/{uri}/{moid}')
                elif kwargs.method ==      'post': pcolor.Cyan(f'  URL: {url}/api/v1/{uri}')
            if int(debug_level) >= 6: pcolor.Cyan(api_results)
            if int(debug_level) == 7:
                pcolor.Cyan(json.dumps(payload, indent=4))
                pcolor.Cyan(payload)
            #=====================================================
            # Gather Results from the apiCall
            #=====================================================
            if api_results.get('Results'): kwargs.results = api_results.Results
            else: kwargs.results = api_results
            if 'post' in kwargs.method:
                if api_results.get('Responses'):
                    api_results['Results'] = deepcopy(api_results['Responses'])
                    kwargs.pmoids = build_pmoid_dictionary(api_results, kwargs)
                elif re.search('bulk.(MoCloner|Request)', api_results.ObjectType):
                    kwargs.pmoids = build_pmoid_dictionary(api_results, kwargs)
                else:
                    kwargs.pmoid = api_results.Moid
                    if kwargs.api_body.get('Name'): kwargs.pmoids[kwargs.api_body['Name']] = kwargs.pmoid
            elif 'inventory' in kwargs.uri: icount = 0
            elif not kwargs.get('build_skip'): kwargs.pmoids = build_pmoid_dictionary(api_results, kwargs)
            #=====================================================
            # Print Progress Notifications
            #=====================================================
            if re.search('(patch|post)', kwargs.method):
                if api_results.get('Responses'):
                    for e in api_results.Responses:
                        kwargs.api_results = e.Body
                        validating.completed_item(self.type, kwargs)
                elif re.search('bulk.Request', api_results.ObjectType):
                    for e in api_results.Results:
                        kwargs.api_results = e.Body
                        if 'bulk.Request' in api_results.ObjectType:
                            if e.Body.get('Name'): name_key = 'Name'
                            elif e.Body.get('PcId'): name_key = 'PcId'
                            elif e.Body.get('PortId'): name_key = 'PortId'
                            elif e.Body.get('PortIdStart'): name_key = 'PortIdStart'
                            elif e.Body.get('VlanId'): name_key = 'VlanId'
                            elif e.Body.get('VsanId'): name_key = 'VsanId'
                            elif e.Body.ObjectType == 'iam.EndPointUserRole': icount = 0
                            else:
                                pcolor.Red(json.dumps(e.Body, indent=4))
                                pcolor.Red('Missing name_key.  isight.py line 164')
                                sys.exit(1)
                            if not e.Body['ObjectType'] == 'iam.EndPointUserRole':
                                indx = next((index for (index, d) in enumerate(kwargs.api_body['Requests']) if d['Body'][name_key] == e.Body[name_key]), None)
                                kwargs.method = (kwargs.api_body['Requests'][indx]['Verb']).lower()
                        validating.completed_item(self.type, kwargs)
                else:
                    kwargs.api_results = api_results
                    validating.completed_item(self.type, kwargs)
            return kwargs
        #=====================================================
        # Pagenation for Get > 1000
        #=====================================================
        if kwargs.method == 'get':
            def build_api_args(kwargs):
                if not kwargs.get('api_filter'):
                    if re.search('(vlans|vsans|port.port_)', kwargs.qtype): names = ", ".join(map(str, kwargs.names))
                    else: names = "', '".join(kwargs.names).strip("', '")
                    if re.search('(organization|resource_group)', kwargs.qtype): api_filter = f"Name in ('{names}')"
                    else: api_filter = f"Name in ('{names}') and Organization.Moid eq '{org_moid}'"
                    if 'asset_target' == kwargs.qtype:          api_filter = f"TargetId in ('{names}')"
                    elif 'connectivity.vhbas' in kwargs.qtype:  api_filter = f"Name in ('{names}') and SanConnectivityPolicy.Moid eq '{kwargs.pmoid}'"
                    elif 'connectivity.vnics' in kwargs.qtype:  api_filter = f"Name in ('{names}') and LanConnectivityPolicy.Moid eq '{kwargs.pmoid}'"
                    elif 'hcl_status' == kwargs.qtype:          api_filter = f"ManagedObject.Moid in ('{names}')"
                    elif 'iam_role' == kwargs.qtype:            api_filter = f"Name in ('{names}') and Type eq 'IMC'"
                    elif 'port.port_channel_' in kwargs.qtype:  api_filter = f"PcId in ({names}) and PortPolicy.Moid eq '{kwargs.pmoid}'"
                    elif 'port.port_modes' == kwargs.qtype:     api_filter = f"PortIdStart in ({names}) and PortPolicy.Moid eq '{kwargs.pmoid}'"
                    elif 'port.port_role_' in kwargs.qtype:     api_filter = f"PortId in ({names}) and PortPolicy.Moid eq '{kwargs.pmoid}'"
                    elif 'registered_device' == kwargs.qtype:   api_filter = f"Moid in ('{names}')"
                    elif 'reservations' in kwargs.qtype:        api_filter = f"Identity in ('{names}') and Pool.Moid eq '{kwargs.pmoid}'"
                    elif 'serial_number' == kwargs.qtype:       api_filter = f"Serial in ('{names}')"
                    elif 'storage.drive_groups' == kwargs.qtype:api_filter = f"Name in ('{names}') and StoragePolicy.Moid eq '{kwargs.pmoid}'"
                    elif 'switch' == kwargs.qtype:              api_filter = f"Name in ('{names}') and SwitchClusterProfile.Moid eq '{kwargs.pmoid}'"
                    elif 'user_role' == kwargs.qtype:           api_filter = f"EndPointUser.Moid in ('{names}') and EndPointUserPolicy.Moid eq '{kwargs.pmoid}'"
                    elif 'vlan.vlans' == kwargs.qtype:          api_filter = f"VlanId in ({names}) and EthNetworkPolicy.Moid eq '{kwargs.pmoid}'"
                    elif 'vsan.vsans' == kwargs.qtype:          api_filter = f"VsanId in ({names}) and FcNetworkPolicy.Moid eq '{kwargs.pmoid}'"
                    elif 'wwnn_pool_leases' == kwargs.qtype:    api_filter = f"PoolPurpose eq 'WWNN' and AssignedToEntity.Moid in ('{names}')"
                    elif 'wwpn_pool_leases' == kwargs.qtype:    api_filter = f"PoolPurpose eq 'WWPN' and AssignedToEntity.Moid in ('{names}')"
                    elif re.search('ww(n|p)n', kwargs.qtype):   api_filter = api_filter + f" and PoolPurpose eq '{kwargs.qtype.upper()}'"
                    if kwargs.top1000 == True and len(kwargs.api_filter) > 0: api_args = f'?$filter={kwargs.api_filter}&$top=1000'
                    elif len(kwargs.names) > 99: api_args = f'?$filter={api_filter}&$top=1000'
                    elif kwargs.top1000 == True: api_args = '?$top=1000'
                    elif api_filter == '': ''
                    else: api_args = f'?$filter={api_filter}'
                elif kwargs.api_filter == 'ignore': api_args=''
                else: api_args = f'?$filter={kwargs.api_filter}'
                return api_args

            if len(kwargs.names) > 1000:
                chunked_list = list(); chunk_size = 1000
                for i in range(0, len(kwargs.names), chunk_size):
                    chunked_list.append(kwargs.names[i:i+chunk_size])
                results = []
                moid_dict = {}
                parent_moid = kwargs.pmoid
                for i in chunked_list:
                    kwargs.names = i
                    kwargs.api_args = build_api_args(kwargs)
                    if re.search('leases|port.port|reservations|user_role|vhbas|vlans|vsans|vnics', kwargs.qtype):
                        kwargs.pmoid = parent_moid
                    kwargs = api_calls(kwargs)
                    results.append(kwargs.results)
                    moid_dict = dict(moid_dict, **kwargs.pmoids.toDict())
                kwargs.pmoids = DotMap(moid_dict)
                kwargs.results = results
            else:
                kwargs.api_args = build_api_args(kwargs)
                kwargs = api_calls(kwargs)
        else:
            kwargs.api_args = ''
            kwargs = api_calls(kwargs)
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
                kwargs.api_body={'Description':f'{org} Resource Group', 'Name':org}
                kwargs.method= 'post'
                kwargs.uri   = 'resource/Groups'
                kwargs       = api(kwargs.qtype).calls(kwargs)
                kwargs.rsg_moids[org].moid     = kwargs.results.Moid
                kwargs.rsg_moids[org].selectors= kwargs.results.Selectors
            if not org in kwargs.org_moids:
                kwargs.api_body={'Description':f'{org} Organization', 'Name':org,
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
    def adapter_configuration(self, api_body, item, kwargs):
        item = item; kwargs = kwargs
        if api_body.get('Settings'):
            for xx in range(0, len(api_body['Settings'])):
                fec_mode = api_body['Settings'][xx]['DceInterfaceSettings']['FecMode']
                api_body['Settings'][xx]['DceInterfaceSettings'] = []
                for x in range(0,4):
                    idict = {'FecMode': '', 'InterfaceId': x, 'ObjectType': 'adapter.DceInterfaceSettings'}
                    if len(fec_mode) - 1 >= x: idict['FecMode'] = fec_mode[x]
                    else: idict['FecMode'] = fec_mode[0]
                    api_body['Settings'][xx]['DceInterfaceSettings'].append(idict)
        return api_body

    #=======================================================
    # BIOS Policy Modification
    #=======================================================
    def bios(self, api_body, item, kwargs):
        if api_body.get('bios_template'):
            btemplate = kwargs.ezdata['bios.template'].properties
            if '-tpm' in api_body['bios_template']:
                api_body = dict(api_body, **btemplate[item.bios_template.replace('-tpm', '')].toDict(), **btemplate.tpm.toDict())
            else: api_body = dict(api_body, **btemplate[item.bios_template].toDict(), **btemplate.tpm_disabled.toDict())
            api_body.pop('bios_template')
        return api_body

    #=======================================================
    # Boot Order Policy Modification
    #=======================================================
    def boot_order(self, api_body, item, kwargs):
        ezdata = kwargs.ezdata['boot_order.boot_devices'].properties
        if item.get('boot_devices'):
            api_body['BootDevices'] = []
            for i in item.boot_devices:
                boot_dev = {'Name':i.name,'ObjectType':i.object_type}
                if re.search('(Iscsi|LocalDisk|Nvme|PchStorage|San|SdCard)', i.object_type) and api_body['ConfiguredBootMode'] == 'Uefi':
                    boot_dev['Bootloader'] = {'ObjectType':'boot.Bootloader'}
                    if 'bootloader' in i:
                        ez1 = kwargs.ezdata['boot_order.boot_devices.boot_loader'].properties
                        for k, v in i.items():
                            if k in ez1: boot_dev['Bootloader'].update({ez1[k].intersight_api:v})
                    else: boot_dev['Bootloader'].update({'Name':'BOOTx64.EFI','Path':"\\EFI\\BOOT\\"})
                for k, v in i.items():
                    if k in ezdata: boot_dev.update({ezdata[k].intersight_api:v})
                api_body['BootDevices'].append(deepcopy(boot_dev))
        return api_body

    #=====================================================
    # Assign Drive Groups to Storage Policies
    #=====================================================
    def drive_groups(self, kwargs):
        ezdata = kwargs.ezdata[self.type]
        kwargs.bulk_list = []
        np, ns = ezfunctions.name_prefix_suffix('storage', kwargs)
        for i in kwargs.policies:
            if i.get('drive_groups'):
                #=====================================================
                # Get Storage Policies
                #=====================================================
                names = []
                for e in i.drive_groups: names.append(e.name)
                kwargs.parent_name = f'{np}{i.name}{ns}'
                kwargs.parent_type = 'storage'
                kwargs.parent_moid = kwargs.isight[kwargs.org].policy['storage'][kwargs.parent_name]
                kwargs.pmoid       = kwargs.parent_moid
                kwargs.qtype       = self.type
                kwargs = api_get(True, names, self.type, kwargs)
                dg_results = kwargs.results
                #=====================================================
                # Create API Body for Storage Drive Groups
                #=====================================================
                for e in i.drive_groups:
                    api_body = {'ObjectType':ezdata.ObjectType}
                    api_body.update({'StoragePolicy':{'Moid':kwargs.parent_moid,'ObjectType':'storage.StoragePolicy'}})
                    api_body = build_api_body(api_body, ezdata.properties, e, self.type, kwargs)
                    api_body.pop('Organization'); api_body.pop('Tags')
                    for x in range(len(api_body['VirtualDrives'])):
                        if not api_body['VirtualDrives'][x].get('VirtualDrivePolicy'):
                            api_body['VirtualDrives'][x]['VirtualDrivePolicy'] = {'ObjectType':'storage.VirtualDrivePolicy'}
                            for k,v in kwargs.ezdata['storage.virtual_drive_policy'].properties.items():
                                if api_body['VirtualDrives'][x]['VirtualDrivePolicy'].get(k):
                                    api_body['VirtualDrives'][x]['VirtualDrivePolicy'][v.intersight_api] = api_body['VirtualDrives'][x]['VirtualDrivePolicy'][k]
                                else: api_body['VirtualDrives'][x]['VirtualDrivePolicy'][v.intersight_api] = v.default
                        api_body['VirtualDrives'][x]['VirtualDrivePolicy'] = dict(
                            sorted(api_body['VirtualDrives'][x]['VirtualDrivePolicy'].items()))
                    #=====================================================
                    # Create or Patch the VLANs via the Intersight API
                    #=====================================================
                    if not kwargs.isight[kwargs.org].policy[self.type].get(api_body['Name']): kwargs.bulk_list.append(deepcopy(api_body))
                    else:
                        indx = next((index for (index, d) in enumerate(dg_results) if d['Name'] == api_body['Name']), None)
                        patch_policy = compare_body_result(api_body, dg_results[indx])
                        api_body['pmoid'] = kwargs.isight[kwargs.org].policy[self.type][api_body['Name']]
                        if patch_policy == True: kwargs.bulk_list.append(deepcopy(api_body))
                        else:
                            pcolor.Cyan(f"      * Skipping {kwargs.parent_type}: `{kwargs.parent_name}`, DriveGroup: `{api_body['Name']}`."\
                                f"  Intersight Matches Configuration.  Moid: {api_body['pmoid']}")
        #=====================================================
        # POST Bulk Request if Post List > 0
        #=====================================================
        if len(kwargs.bulk_list) > 0:
            kwargs.uri = kwargs.ezdata[self.type].intersight_uri
            kwargs     = bulk_request(kwargs)
        return kwargs

    #=======================================================
    # Ethernet Adapter Policy Modification
    #=======================================================
    def ethernet_adapter(self, api_body, item, kwargs):
        if api_body.get('adapter_template'):
            atemplate= kwargs.ezdata['ethernet_adapter.template'].properties
            api_body  = dict(api_body, **atemplate[item.adapter_template].toDict())
            api_body.pop('adapter_template')
        return api_body

    #=======================================================
    # Fibre-Channel Adapter Policy Modification
    #=======================================================
    def fibre_channel_adapter(self, api_body, item, kwargs):
        if api_body.get('adapter_template'):
            atemplate= kwargs.ezdata['fibre_channel_adapter.template'].properties
            api_body  = dict(api_body, **atemplate[item.adapter_template].toDict())
            api_body.pop('adapter_template')
        return api_body

    #=======================================================
    # Fibre-Channel Network Policies Policy Modification
    #=======================================================
    def firmware(self, api_body, item, kwargs):
        item = item; kwargs = kwargs
        if api_body.get('ExcludeComponentList'):
            exclude_components = list(api_body['ExcludeComponentList'].keys())
            api_body['ExcludeComponentList'] = exclude_components
        if api_body.get('ModelBundleCombo'):
            combos = deepcopy(api_body['ModelBundleCombo']); api_body['ModelBundleCombo'] = []
            for e in combos:
                for i in e['ModelFamily']:
                    idict = deepcopy(e); idict['ModelFamily'] = i
                    api_body['ModelBundleCombo'].append(idict)
        return api_body

    #=======================================================
    # Identity Reservations
    #=======================================================
    def identity_reservations(self, ptitle, reservations, kwargs):
        #=====================================================
        # Send Begin Notification and Load Variables
        #=====================================================
        validating.begin_section(ptitle, 'pool reservations')
        kwargs.bulk_list = []
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
            # Construct api_body Payload
            #=====================================================
            api_body = {}
            for e in v.reservations.identities:
                for a, b in v.reservations.items():
                    if not 'Identity' == a: api_body.update({a:b})
                api_body.update({'Identity':e,'Pool':{'Moid':kwargs.isight[kwargs.org].pool[self.type][k],'ObjectType':v.object_type}})
                api_body = org_map(api_body)
                kwargs.method = 'post'
                if not reserve_moids.get(api_body['Identity']): kwargs.bulk_list.append(deepcopy(api_body))
        #=====================================================
        # POST Bulk Request if Post List > 0
        #=====================================================
        if len(kwargs.bulk_list) > 0:
            kwargs.uri = kwargs.ezdata[self.type].intersight_uri
            kwargs     = bulk_request(kwargs)
        #=====================================================
        # Send End Notification and return kwargs
        #=====================================================
        validating.end_section(ptitle, 'pool reservations')
        return kwargs

    #=======================================================
    # IMC Access Policy Modification
    #=======================================================
    def imc_access(self, api_body, item, kwargs):
        item = item
        if not api_body.get('AddressType'): api_body.update({ 'AddressType':{ 'EnableIpV4':False, 'EnableIpV6':False }})
        api_body.update({ 'ConfigurationType':{ 'ConfigureInband': False, 'ConfigureOutOfBand': False }})
        #=====================================================
        # Attach Pools to the API Body
        #=====================================================
        names = []; ptype = ['InbandIpPool', 'OutOfBandIpPool']
        np, ns = ezfunctions.name_prefix_suffix('ip', kwargs)
        for i in ptype:
            if api_body.get(i):
                if '/' in api_body[i]['Moid']: org, pool = api_body[i]['Moid'].split('/')
                else: org = kwargs.org; pool = api_body[i]['Moid']
                pool = f"{np}{pool}{ns}"
                if '/' in api_body[i]['Moid']: new_pool = f'{org}/{pool}'
                else: new_pool = pool
                names.append(new_pool)
                api_body['ConfigurationType'][f'Configure{i.split("Ip")[0]}'] = True
        if len(names) > 0: kwargs = api_get(False, names, 'ip', kwargs)
        for i in ptype:
            if api_body.get(i):
                if '/' in api_body[i]['Moid']: org, pool = api_body[i]['Moid'].split('/')
                else: org = kwargs.org; pool = api_body[i]['Moid']
                pool = f"{np}{pool}{ns}"
                if not kwargs.isight[org].pool['ip'].get(pool):
                    if '/' in api_body[i]['Moid']: new_pool = f'{org}/{pool}'
                    else: new_pool = pool
                    validating.error_policy_doesnt_exist(i, new_pool, self.type, 'policy', api_body['Name'])
                org_moid = kwargs.org_moids[org].moid
                indx = next((index for (index, d) in enumerate(kwargs.results) if d.Name == pool and d.Organization.Moid == org_moid), None)
                if len(kwargs.results[indx].IpV4Config.Gateway) > 0: api_body['AddressType']['EnableIpV4'] = True
                if len(kwargs.results[indx].IpV6Config.Gateway) > 0: api_body['AddressType']['EnableIpV6'] = True
                api_body[i]['Moid'] = kwargs.isight[org].pool['ip'][pool]
        return api_body

    #=======================================================
    # IPMI over LAN Policy Modification
    #=======================================================
    def ipmi_over_lan(self, api_body, item, kwargs):
        item = item; kwargs = kwargs
        if api_body.get('encryption_key'):
            if os.environ.get('ipmi_key') == None:
                kwargs.sensitive_var = "ipmi_key"
                kwargs = ezfunctions.sensitive_var_value(kwargs)
                api_body.update({'EncryptionKey':kwargs.var_value})
            else: api_body.update({'EncryptionKey':os.environ.get('ipmi_key')})
        return api_body

    #=======================================================
    # iSCSI Adapter Policy Modification
    #=======================================================
    def iscsi_boot(self, api_body, item, kwargs):
        item = item
        if api_body.get('IscsiAdapterPolicy'):
            names = []
            if '/' in api_body['IscsiAdapterPolicy']['Moid']: org, policy = api_body['IscsiAdapterPolicy']['Moid'].split('/')
            else: org = kwargs.org; policy = api_body['IscsiAdapterPolicy']['Moid']
            if not kwargs.isight[org].policy['iscsi_adapter'].get(policy): kwargs = api_get(False, [item.iscsi_adapter_policy], 'iscsi_adapter', kwargs)
            if not kwargs.isight[org].policy['iscsi_adapter'].get(policy):
                validating.error_policy_doesnt_exist('iscsi_adapter', api_body['IscsiAdapterPolicy']['Moid'], self.type, 'policy', api_body['Name'])
            api_body['IscsiAdapterPolicy']['Moid'] = kwargs.isight[org].policy['iscsi_adapter'][policy]

        if api_body.get('InitiatorStaticIpV4Config'):
            api_body['InitiatorStaticIpV4Address'] = api_body['InitiatorStaticIpV4Config']['IpAddress']
            api_body['InitiatorStaticIpV4Config'].pop('IpAddress')
        if api_body.get('Chap'):
            kwargs.sensitive_var = 'iscsi_boot_password'
            kwargs = ezfunctions.sensitive_var_value(kwargs)
            if api_body['authentication'] == 'mutual_chap':
                api_body['MutualChap'] = api_body['Chap']; api_body.pop('Chap')
                api_body['MutualChap']['Password'] = kwargs.var_value
            else: api_body['Chap']['Password'] = kwargs.var_value
        if api_body['authentication']: api_body.pop('authentication')
        #=====================================================
        # Attach Pools/Policies to the API Body
        #=====================================================
        if api_body.get('InitiatorIpPool'):
            ip_pool= api_body['InitiatorIpPool']['Moid']
            if '/' in api_body['InitiatorIpPool']['Moid']: org, pool = api_body['InitiatorIpPool']['Moid'].split('/')
            else: org = kwargs.org; pool = api_body['InitiatorIpPool']['Moid']
            if not kwargs.isight[org].pool['ip'].get(pool): kwargs = api_get(False, [ip_pool], 'ip', kwargs)
            api_body['InitiatorIpPool']['Moid'] = kwargs.isight[org].pool['ip'][pool]
        names = []; plist = ['PrimaryTargetPolicy', 'SecondaryTargetPolicy']
        for p in plist:
            if api_body.get(p):
                if '/' in api_body[p]['Moid']: org, policy = api_body[p]['Moid'].split('/')
                else: org = kwargs.org; policy = api_body[p]['Moid']
                if not kwargs.isight[org].policy['iscsi_static_target'].get(policy): names.append(api_body[p]['Moid'])
        if len(kwargs.names) > 0: kwargs = api_get(False, names, 'iscsi_static_target', kwargs)
        for p in plist:
            if api_body.get(p):
                if '/' in api_body[p]['Moid']: org, policy = api_body[p]['Moid'].split('/')
                else: org = kwargs.org; policy = api_body[p]['Moid']
                if not kwargs.isight[org].policy['iscsi_static_target'].get(policy):
                    validating.error_policy_doesnt_exist(p, api_body[p]['Moid'], self.type, 'policy', api_body['Name'])
                api_body[p]['Moid'] = kwargs.isight[org].policy['iscsi_static_target'][policy]
        return api_body

    #=======================================================
    # iSCSI Static Target Policy Modification
    #=======================================================
    def iscsi_static_target(self, api_body, item, kwargs):
        item = item; kwargs = kwargs; api_body['Lun'] = {'Bootable':True}
        return api_body

    #=====================================================
    # Assign Users to Local User Policies
    #=====================================================
    def ldap_groups(self, kwargs):
        #=====================================================
        # Get Existing Users
        #=====================================================
        ezdata = kwargs.ezdata[self.type]
        kwargs.group_post_list = []; kwargs.server_post_list = []; role_names = []; kwargs.cp = DotMap()
        np, ns = ezfunctions.name_prefix_suffix('ldap', kwargs)
        for i in kwargs.policies:
            if i.get('ldap_groups'):
                kwargs.parent_name = f'{np}{i.name}{ns}'
                for e in i.ldap_groups: role_names.append(e.role)
                kwargs.pmoid = kwargs.isight[kwargs.org].policy[self.type.split('.')[0]][kwargs.parent_name]
                names  = [e.name for e in i.ldap_groups]
                kwargs = api_get(True, names, self.type, kwargs)
                kwargs.cp[kwargs.pmoid].group_moids  = kwargs.pmoids
                kwargs.cp[kwargs.pmoid].group_results= kwargs.results
                kwargs.pmoid = kwargs.isight[kwargs.org].policy[self.type.split('.')[0]][kwargs.parent_name]
            if i.get('ldap_servers'):
                names  = [e.server for e in i.ldap_servers]
                kwargs = api_get(True, names, 'ldap.ldap_servers', kwargs)
                kwargs.cp[kwargs.pmoid].server_moids  = kwargs.pmoids
                kwargs.cp[kwargs.pmoid].server_results= kwargs.results
        if len(role_names) > 0:
            kwargs.names       = list(numpy.unique(numpy.array(role_names)))
            kwargs.qtype       = 'iam_role'
            kwargs.uri         = 'iam/EndPointRoles'
            kwargs             = api(kwargs.qtype).calls(kwargs)
            kwargs.role_moids  = kwargs.pmoids
            kwargs.role_results= kwargs.results
        #=====================================================
        # Construct API Body LDAP Policies
        #=====================================================
        for i in kwargs.policies:
            kwargs.parent_name = f'{np}{i.name}{ns}'
            kwargs.parent_type = 'LDAP Policy'
            kwargs.parent_moid = kwargs.isight[kwargs.org].policy[self.type.split('.')[0]][kwargs.parent_name]
            for e in i.ldap_groups:
                #=====================================================
                # Create API Body for User Role
                #=====================================================
                api_body = {'LdapPolicy':{'Moid':kwargs.parent_moid,'ObjectType':'iam.LdapPolicy'},'ObjectType':ezdata.ObjectType}
                api_body = build_api_body(api_body, ezdata, e, self.type, kwargs)
                api_body['EndPointRole']['Moid'] = kwargs.role_moids[e.role].moid
                #=====================================================
                # Create or Patch the Policy via the Intersight API
                #=====================================================
                if kwargs.cp[kwargs.parent_moid].group_moids.get(e.name):
                    indx = next((index for (index, d) in enumerate(kwargs.cp[kwargs.parent_moid].group_results) if d['Name'] == api_body['Name']), None)
                    patch_policy = compare_body_result(api_body, kwargs.cp[kwargs.parent_moid].group_results[indx])
                    api_body['pmoid'] = kwargs.cp[kwargs.parent_moid].moids[e.name].moid
                    if patch_policy == True: kwargs.group_post_list.append(deepcopy(api_body))
                    else:
                        pcolor.Cyan(f"      * Skipping {kwargs.parent_type}: `{kwargs.parent_name}`, Group: `{api_body['Name']}`."\
                            f"  Intersight Matches Configuration.  Moid: {api_body['pmoid']}")
                else: kwargs.group_post_list.append(deepcopy(api_body))
            for e in i.ldap_servers:
                #=====================================================
                # Create API Body for User Role
                #=====================================================
                api_body = {'LdapPolicy':{'Moid':kwargs.parent_moid,'ObjectType':'iam.LdapPolicy'},'ObjectType':kwargs.ezdata['ldap.ldap_servers'].ObjectType}
                api_body = build_api_body(api_body, ezdata, e, 'ldap.ldap_servers', kwargs)
                #=====================================================
                # Create or Patch the Policy via the Intersight API
                #=====================================================
                if kwargs.cp[kwargs.parent_moid].server_moids.get(e.server):
                    indx = next((index for (index, d) in enumerate(kwargs.cp[kwargs.parent_moid].server_results) if d['Name'] == api_body['Name']), None)
                    patch_policy = compare_body_result(api_body, kwargs.cp[kwargs.parent_moid].server_results[indx])
                    api_body['pmoid'] = kwargs.cp[kwargs.parent_moid].moids[e.server].moid
                    if patch_policy == True: kwargs.server_post_list.append(deepcopy(api_body))
                    else:
                        pcolor.Cyan(f"      * Skipping {kwargs.parent_type}: `{kwargs.parent_name}`, Group: `{api_body['Name']}`."\
                            f"  Intersight Matches Configuration.  Moid: {api_body['pmoid']}")
                else: kwargs.server_post_list.append(deepcopy(api_body))
        #=====================================================
        # POST Bulk Request if Post List > 0
        #=====================================================
        if len(kwargs.group_post_list) > 0:
            kwargs.uri = ezdata.interight_uri
            kwargs     = bulk_request(kwargs)
        if len(kwargs.server_post_list) > 0:
            kwargs.uri = ezdata.interight_uri
            kwargs     = bulk_request(kwargs)
        return kwargs

    #=======================================================
    # LAN Connectivity Policy Modification
    #=======================================================
    def lan_connectivity(self, api_body, item, kwargs):
        if not api_body.get('PlacementMode'): api_body.update({'PlacementMode':'custom'})
        if not api_body.get('TargetPlatform'): api_body.update({'TargetPlatform': 'FIAttached'})
        if item.get('IqnPool'):
            api_body['IqnAllocationType'] = 'Pool'
            if '/' in item.iqn_pool: org, pool = item.iqn_pool.split('/')
            else: org = kwargs.org; pool = item.iqn_pool
            if not kwargs.isight[org].pool['iqn'].get(pool): kwargs = api_get(False, [item.iqn_pool], 'iqn', kwargs)
            api_body['IqnPool']['Moid'] = kwargs.isight[org].pool['iqn'][pool]
        return api_body

    #=======================================================
    # Local User Policy Modification
    #=======================================================
    def local_user(self, api_body, item, kwargs):
        if not api_body.get('PasswordProperties'): api_body['PasswordProperties'] = {}
        for k, v in kwargs.ezdata['local_user.password_properties'].properties.items():
            if item.get('password_properties'):
                if item.password_properties.get(k):
                    api_body['PasswordProperties'][v.intersight_api] =  item.password_properties[k]
                else: api_body['PasswordProperties'][v.intersight_api] = v.default
            else: api_body['PasswordProperties'][v.intersight_api] = v.default
        return api_body

    #=======================================================
    # Network Connectivity Policy Modification
    #=======================================================
    def network_connectivity(self, api_body, item, kwargs):
        dns_list = ['v4', 'v6']; kwargs = kwargs
        for i in dns_list:
            dtype = f'dns_servers_{i}'
            if dtype in api_body:
                if len(item[dtype]) > 0: api_body.update({f'PreferredIp{i}dnsServer':item[dtype][0]})
                if len(item[dtype]) > 1: api_body.update({f'AlternateIp{i}dnsServer':item[dtype][1]})
                api_body.pop(dtype)
        return api_body

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
        np, ns = ezfunctions.name_prefix_suffix(self.type, kwargs)
        names = []
        for i in policies:
            if self.type == 'port': names.extend([f'{np}{i.names[x]}{ns}' for x in range(0,len(i.names))])
            else: names.append(f"{np}{i['name']}{ns}")
        kwargs = api_get(True, names, self.type, kwargs)
        kwargs.policy_results= kwargs.results
        #=====================================================
        # If Modified Patch the Policy via the Intersight API
        #=====================================================
        def policies_to_api(api_body, kwargs):
            kwargs.qtype = self.type
            kwargs.uri   = kwargs.ezdata[self.type].intersight_uri
            if kwargs.isight[kwargs.org].policy[self.type].get(api_body['Name']):
                indx = next((index for (index, d) in enumerate(kwargs.policy_results) if d['Name'] == api_body['Name']), None)
                patch_policy = compare_body_result(api_body, kwargs.policy_results[indx])
                api_body['pmoid']  = kwargs.isight[kwargs.org].policy[self.type][api_body['Name']]
                if patch_policy == True:
                    kwargs.bulk_list.append(deepcopy(api_body))
                    kwargs.pmoids[api_body['Name']].moid = api_body['pmoid']
                else: pcolor.Cyan(f"      * Skipping {ptitle} Policy: `{api_body['Name']}`.  Intersight Matches Configuration.  Moid: {api_body['pmoid']}")
            else: kwargs.bulk_list.append(deepcopy(api_body))
            return kwargs
        #=====================================================
        # Loop through Policy Items
        #=====================================================
        kwargs.bulk_list = []; kwargs.type = self.type
        for item in policies:
            if self.type == 'port':
                names = item.names; item.pop('names')
                for x in range(0,len(names)):
                    #=====================================================
                    # Construct api_body Payload
                    #=====================================================
                    api_body = {'Name':f'{np}{names[x]}{ns}','ObjectType':kwargs.ezdata[self.type].ObjectType}
                    api_body = build_api_body(api_body, idata, item, self.type, kwargs)
                    kwargs = policies_to_api(api_body, kwargs)
            else:
                #=====================================================
                # Construct api_body Payload
                #=====================================================
                api_body = {'ObjectType':kwargs.ezdata[self.type].ObjectType}
                api_body = build_api_body(api_body, idata, item, self.type, kwargs)
                kwargs = policies_to_api(api_body, kwargs)
        #=====================================================
        # POST Bulk Request if Post List > 0
        #=====================================================
        if len(kwargs.bulk_list) > 0:
            kwargs.uri    = kwargs.ezdata[self.type].intersight_uri
            kwargs        = bulk_request(kwargs)
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
        kwargs.bulk_list = []; reservations = DotMap()
        idata = DotMap(dict(pair for d in kwargs.ezdata[self.type].allOf for pair in d.properties.items()))
        pools = list({v['name']:v for v in kwargs.imm_dict.orgs[kwargs.org].pools[self.type]}.values())
        #=====================================================
        # Get Existing Pools
        #=====================================================
        np, ns = ezfunctions.name_prefix_suffix(self.type, kwargs)
        kwargs = api_get(True, [f'{np}{e.name}{ns}' for e in pools], self.type, kwargs)
        kwargs.pool_results = kwargs.results
        #=====================================================
        # Loop through Items
        #=====================================================
        for item in pools:
            #=====================================================
            # Construct api_body Payload
            #=====================================================
            api_body = {'ObjectType':kwargs.ezdata[self.type].ObjectType}
            api_body = build_api_body(api_body, idata, item, self.type, kwargs)
            #=====================================================
            # Add Pool Specific Attributes
            #=====================================================
            if re.search('ww(n|p)n', self.type):  api_body.update({'PoolPurpose':self.type.upper()})
            #=====================================================
            # If reservations; Build Dict and Pop reservations
            #=====================================================
            if api_body.get('reservations'):
                reservations[api_body['Name']].reservations= api_body['reservations']
                reservations[api_body['Name']].object_type = kwargs.ezdata[self.type].ObjectType
                api_body.pop('reservations')
            #=====================================================
            # If Resource Pool Build Selector
            #=====================================================
            if api_body.get('serial_number_list'):
                kwargs.method = 'get'
                kwargs.names  = api_body['serial_number_list']
                kwargs.qtype  = 'serial_number'
                kwargs.uri    = kwargs.ezdata[self.type].intersight_uri_serial
                kwargs        = api(kwargs.qtype).calls(kwargs)
                smoids        = kwargs.pmoids
                selector = "','".join([smoids[e].moid for e in list(smoids.keys())]); selector = f"'{selector}'"
                stype = f"{smoids[api_body['serial_number_list'][0]].object_type.split('.')[1]}s"
                mmode = smoids[api_body['serial_number_list'][0]].management_mode
                api_body['Selectors'] = [{
                    'ObjectType': 'resource.Selector',
                    'Selector': f"/api/v1/compute/{stype}?$filter=(Moid in ({selector})) and (ManagementMode eq '{mmode}')"
                }]
                api_body.pop('serial_number_list')
            #=====================================================
            # If Modified Patch the Pool via the Intersight API
            #=====================================================
            if kwargs.isight[kwargs.org].pool[self.type].get(api_body['Name']):
                indx = next((index for (index, d) in enumerate(kwargs.pool_results) if d['Name'] == api_body['Name']), None)
                patch_pool = compare_body_result(api_body, kwargs.pool_results[indx])
                api_body['pmoid'] = kwargs.isight[kwargs.org].pool[self.type][api_body['Name']]
                if patch_pool == True: kwargs.bulk_list.append(deepcopy(api_body))
                else: pcolor.Cyan(f"      * Skipping {ptitle} Pool: `{api_body['Name']}`.  Intersight Matches Configuration.  Moid: {api_body['pmoid']}")
            else: kwargs.bulk_list.append(deepcopy(api_body))
        #=====================================================
        # POST Bulk Request if Post List > 0
        #=====================================================
        if len(kwargs.bulk_list) > 0:
            kwargs.uri    = kwargs.ezdata[self.type].intersight_uri
            kwargs        = bulk_request(kwargs)
            for e in kwargs.results: kwargs.isight[kwargs.org].pool[self.type][e.Body.Name] = e.Body.Moid
        #=====================================================
        # Loop Through Reservations if > 0
        #=====================================================
        if len(reservations) > 0: kwargs = imm.identity_reservations(self, ptitle, reservations, kwargs)
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
        np, ns = ezfunctions.name_prefix_suffix('port', kwargs)
        kwargs.bulk_list = []
        ezdata= kwargs.ezdata[self.type]
        p     = self.type.split('.')
        for item in kwargs.policies:
            if item.get(p[1]):
                for x in range(0,len(item['names'])):
                    kwargs.port_policy[f"{np}{item['names'][x]}{ns}"].names = []
                    for e in item[p[1]]: kwargs.port_policy[f"{np}{item['names'][x]}{ns}"].names.append(e.port_list[0])
                for i in list(kwargs.port_policy.keys()):
                    indx = next((index for (index, d) in enumerate(kwargs.policy_results) if d['Name'] == i), None)
                    kwargs.parent_moid = kwargs.policy_results[indx].Moid
                    kwargs.pmoid = kwargs.policy_results[indx].Moid
                    kwargs = api_get(True, kwargs.port_policy[i].names, self.type, kwargs)
                    port_modes  = kwargs.pmoids
                    port_results= deepcopy(kwargs.results)
                    for e in item[p[1]]:
                        api_body = {'CustomMode':e.custom_mode,'ObjectType':ezdata.ObjectType,
                                          'PortIdStart':e.port_list[0],'PortIdEnd':e.port_list[1],
                                          ezdata.parent_policy:{'Moid':kwargs.parent_moid,'ObjectType':ezdata.parent_object}}
                        if e.get('slot_id'): api_body.update({'SlotId':e.slot_id})
                        else: api_body.update({'SlotId':1})
                        #=====================================================
                        # Create or Patch the Policy via the Intersight API
                        #=====================================================
                        kwargs.parent_name = i
                        kwargs.parent_type = 'Port Policy'
                        kwargs.parent_moid = kwargs.isight[kwargs.org].policy['port'][i]
                        if port_modes.get(kwargs.parent_moid):
                            if port_modes[kwargs.parent_moid].get(str(e.port_list[0])):
                                kwargs.method= 'patch'
                            else: kwargs.method= 'post'
                        else: kwargs.method= 'post'
                        if kwargs.method == 'post': kwargs.bulk_list.append(deepcopy(api_body))
                        else:
                            indx = next((index for (index, d) in enumerate(port_results) if d['PortIdStart'] == e.port_list[0]), None)
                            patch_port = compare_body_result(api_body, port_results[indx])
                            api_body['pmoid'] = port_modes[kwargs.parent_moid][str(e.port_list[0])].moid
                            if patch_port == True: kwargs.bulk_list.append(deepcopy(api_body))
                            else:
                                ps = e.port_list[0]; pe = e.port_list[1]
                                pcolor.Cyan(f"      * Skipping Port Policy: `{i}`, CustomMode: `{e.custom_mode}`,  PortIdStart: `{ps}` and PortIdEnd: `{pe}`.\n"\
                                       f"         Intersight Matches Configuration.  Moid: {api_body['pmoid']}")
        #=====================================================
        # POST Bulk Request if Post List > 0
        #=====================================================
        if len(kwargs.bulk_list) > 0:
            kwargs.uri    = kwargs.ezdata[self.type].intersight_uri
            kwargs        = bulk_request(kwargs)
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
            if re.search('port_channel', port_type): name = int(kwargs.api_body['PcId']); key_id = 'PcId'
            else: name = int(kwargs.api_body['PortId']); key_id = 'PortId'
            if kwargs.port_moids[port_type].get(kwargs.parent_moid):
                if kwargs.port_moids[port_type][kwargs.parent_moid].get(str(name)):
                    kwargs.method= 'patch'
                    kwargs.pmoid = kwargs.port_moids[port_type][kwargs.parent_moid][str(name)].moid
                else: kwargs.method= 'post'
            else: kwargs.method= 'post'
            kwargs.uri = kwargs.ezdata[f'port.{port_type}'].intersight_uri
            if kwargs.method == 'patch':
                indx = next((index for (index, d) in enumerate(kwargs.port_results[port_type]) if d[key_id] == name), None)
                patch_port = compare_body_result(kwargs.api_body, kwargs.port_results[port_type][indx])
                if patch_port == True:
                    kwargs.qtype  = f'port.{port_type}'
                    kwargs        = api(kwargs.qtype).calls(kwargs)
                else:
                    pcolor.Cyan(f"      * Skipping Port Policy: `{kwargs.parent_name}`, {key_id}: `{name}`."\
                           f"  Intersight Matches Configuration.  Moid: {kwargs.pmoid}")
            else:
                kwargs.plist[port_type].append({'Body':deepcopy(kwargs.api_body), 'ClassId':'bulk.RestSubRequest',
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
                if kwargs.api_body.get(p):
                    ptype = (snakecase(p).replace('eth_', 'ethernet_')).replace('_policy', '')
                    if '/' in kwargs.api_body[p]['Moid']: org, policy = kwargs.api_body[p]['Moid'].split('/')
                    else: org = kwargs.org; policy = kwargs.api_body[p]['Moid']
                    np, ns = ezfunctions.name_prefix_suffix(ptype, kwargs)
                    policy = f"{np}{policy}{ns}"
                    if '/' in kwargs.api_body[p]['Moid']: new_policy = f'{org}/{policy}'
                    else: new_policy = policy
                    if not kwargs.isight[org].policy[ptype].get(policy):
                        validating.error_policy_doesnt_exist(ptype, new_policy, f'port.{port_type}', 'policy', i.names[x])
                    kwargs.api_body[p]['Moid'] = kwargs.isight[org].policy[ptype][policy]
                    if 'Group' in p: kwargs.api_body[p] = [kwargs.api_body[p]]
            return kwargs
        
        #=====================================================
        # Create API Body for Port Policies
        #=====================================================
        def port_type_call(port_type, item, x, kwargs):
            ezdata = kwargs.ezdata[f'port.{port_type}']
            for i in item[port_type]:
                api_body = {'ObjectType':ezdata.ObjectType, 'PortPolicy':{'Moid':kwargs.parent_moid,'ObjectType':'fabric.PortPolicy'}}
                kwargs.api_body = build_api_body(api_body, ezdata.properties, i, f'port.{port_type}', kwargs)
                if i.get('pc_ids'):
                    if len(kwargs.api_body['PcId']) == 2: kwargs.api_body['PcId'] = i.pc_ids[x]
                    else: kwargs.api_body['PcId'] = i.pc_ids[x]
                    if re.search('appliance|ethernet|fcoe', port_type): kwargs = policy_update(port_type, i, x, kwargs)
                    for x in range(len(api_body['Ports'])):
                        if not kwargs.api_body['Ports'][x].get('AggregatePortId'): kwargs.api_body['Ports'][x]['AggregatePortId'] = 0
                        if not kwargs.api_body['Ports'][x].get('SlotId'): kwargs.api_body['Ports'][x]['SlotId'] = 1
                else:
                    if not kwargs.api_body.get('AggregatePortId'): kwargs.api_body['AggregatePortId'] = 0
                    if not kwargs.api_body.get('SlotId'): kwargs.api_body['SlotId'] = 1
                if i.get('vsan_ids'):
                    if len(i['vsan_ids']) > 1: kwargs.api_body['VsanId'] = i['vsan_ids'][x]
                    else: kwargs.api_body['VsanId'] = i['vsan_ids'][0]
                kwargs.api_body.pop('Organization'); kwargs.api_body.pop('Tags')
                if re.search('port_channel', port_type): kwargs = api_calls(port_type, kwargs)
                elif re.search('role', port_type):
                    for e in ezfunctions.vlan_list_full(i.port_list):
                        kwargs.api_body['PortId'] = int(e)
                        kwargs = api_calls(port_type, kwargs)
            return kwargs

        #=====================================================
        # Get Policies
        #=====================================================
        def policy_list(policy, ptype, kwargs):
            original_policy = policy
            if '/' in policy: org, policy = policy.split('/')
            else: org = kwargs.org; policy = policy
            np, ns = ezfunctions.name_prefix_suffix(ptype, kwargs)
            policy = f"{np}{policy}{ns}"
            if '/' in original_policy: new_policy = f'{org}/{policy}'
            else: new_policy = policy
            if not kwargs.isight[org].policy[ptype].get(policy): kwargs.cp[ptype].names.append(new_policy)
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
                                    for d in v: kwargs = policy_list(d, ptype, kwargs)
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
                        kwargs.parent_type = 'Port Policy'
                        kwargs.parent_moid = kwargs.isight[kwargs.org].policy['port'][item.names[x]]
                        kwargs = get_ports(e, item, x, kwargs)
                        port_type_call(e, item, x, kwargs)
                        if len(kwargs.plist[e]) > 0:
                            kwargs.api_body= {'Requests':kwargs.plist[e]}
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
            api_body = {'ObjectType':ezdata.ObjectType}
            for i in item.targets:
                pitems = dict(deepcopy(item), **i)
                pop_items = ['action', 'targets']
                for e in pop_items:
                    if pitems.get(e): pitems.pop(e)
                api_body = build_api_body(api_body, kwargs.idata, pitems, self.type, kwargs)
                api_body = profile_policy_bucket(api_body, kwargs)
                if api_body.get('SerialNumber'): api_body = assign_physical_device(api_body, kwargs)
                kwargs = profile_api_calls(api_body, kwargs)
        #=====================================================
        # POST Bulk Request if Post List > 0
        #=====================================================
        if len(kwargs.bulk_list) > 0:
            kwargs.uri = kwargs.ezdata[self.type].intersight_uri
            kwargs     = bulk_request(kwargs)
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
            api_body = {'ObjectType':ezdata.ObjectType}
            api_body = build_api_body(api_body, kwargs.idata, pdata, self.type, kwargs)
            kwargs  = profile_api_calls(api_body, kwargs)
            if len(kwargs.bulk_list) > 0:
                if not kwargs.plist.get('domain'): kwargs.plist.domain = []
                kwargs.plist.domain.extend(kwargs.bulk_list)
                kwargs.bulk_list = []
            #=====================================================
            # Build api_body for Switch Profiles
            #=====================================================
            cluster_moid = kwargs.isight[kwargs.org].profile[self.type][item.name]
            for x in range(0,2):
                sw_name = f"{item.name}-{chr(ord('@')+x+1)}"; otype = 'SwitchClusterProfile'
                if kwargs.switch_moids.get(item.name):
                    kwargs.isight[kwargs.org].profile['switch'][sw_name] = kwargs.switch_moids[item.name][sw_name].moid
                pdata = dict(deepcopy(item), **{'name':sw_name})
                api_body = {'Name':sw_name, 'ObjectType':'fabric.SwitchProfile', otype:{'Moid':cluster_moid,'ObjectType':f'fabric.{otype}'}}
                api_body = build_api_body(api_body, kwargs.idata, pdata, self.type, kwargs)
                kwargs.x_number = x; kwargs.type = 'switch'
                api_body = profile_policy_bucket(api_body, kwargs)
                if api_body.get('SerialNumber'): api_body = assign_physical_device(api_body, kwargs)
                pop_list = ['Action', 'Description', 'Organization', 'Tags']
                for e in pop_list:
                    if api_body.get(e): api_body.pop(e)
                temp_results = kwargs.profile_results
                kwargs.profile_results = kwargs.switch_results[item.name]
                kwargs  = profile_api_calls(api_body, kwargs)
                kwargs.profile_results = temp_results
                if len(kwargs.bulk_list) > 0:
                    if not kwargs.plist.get('switch'): kwargs.plist.switch = []
                    kwargs.plist.switch.extend(kwargs.bulk_list)
                    kwargs.bulk_list = []
        #=====================================================
        # POST Bulk Request if Post List > 0
        #=====================================================
        for e in list(kwargs.plist.keys()):
            if len(kwargs.plist[e]) > 0:
                if 'domain' == e: kwargs.uri = kwargs.ezdata[self.type].intersight_uri
                else: kwargs.uri = kwargs.ezdata[self.type].intersight_uri_switch
                kwargs.bulk_list = kwargs.plist[e]
                kwargs = bulk_request(kwargs)
        return kwargs

    #=====================================================
    # Build Chassis Profiles
    #=====================================================
    def profile_server(self, profiles, templates, kwargs):
        ezdata = kwargs.ezdata[self.type]
        for item in profiles:
            api_body = {'ObjectType':ezdata.ObjectType}
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
                    api_body = {'ObjectType':ezdata.ObjectType}
                    api_body = build_api_body(api_body, kwargs.idata, item, self.type, kwargs)
                    if not api_body.get('TargetPlatform'): api_body['TargetPlatform'] = 'FIAttached'
                    api_body = profile_policy_bucket(api_body, kwargs)
                    if api_body.get('SerialNumber'): api_body = assign_physical_device(api_body, kwargs)
                    kwargs = profile_api_calls(api_body, kwargs)
        #=====================================================
        # POST Bulk Request if Post List > 0
        #=====================================================
        if len(kwargs.bulk_template) > 0:
            for e in kwargs.bulk_template.keys():
                kwargs.api_body= kwargs.bulk_template[e]
                kwargs.method = 'post'
                kwargs.qtype  = 'bulk'
                kwargs.uri    = 'bulk/MoCloners'
                kwargs = api(kwargs.qtype).calls(kwargs)
        if len(kwargs.bulk_list) > 0:
            kwargs.uri = kwargs.ezdata[self.type].intersight_uri
            kwargs     = bulk_request(kwargs)
        return kwargs

    #=====================================================
    # Build Chassis Profiles
    #=====================================================
    def profile_template(self, profiles, kwargs):
        ezdata = kwargs.ezdata[self.type]
        for item in profiles:
            api_body = {'ObjectType':ezdata.ObjectType}
            api_body = build_api_body(api_body, kwargs.idata, item, self.type, kwargs)
            if not api_body.get('TargetPlatform'): api_body['TargetPlatform'] = 'FIAttached'
            api_body = profile_policy_bucket(api_body, kwargs)
            api_body.pop('create_template')
            if item.create_template == True: kwargs = profile_api_calls(api_body, kwargs)
        #=====================================================
        # POST Bulk Request if Post List > 0
        #=====================================================
        if len(kwargs.bulk_list) > 0:
            kwargs.uri = kwargs.ezdata[self.type].intersight_uri
            kwargs     = bulk_request(kwargs)
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
        names = []; kwargs.bulk_profiles = []; kwargs.cp = DotMap(); kwargs.bulk_list = []
        kwargs.serials = []; kwargs.templates = []
        ezdata = kwargs.ezdata[self.type]
        idata = DotMap(dict(pair for d in kwargs.ezdata[self.type].allOf for pair in d.properties.items()))
        if re.search('chassis|server', self.type):
            targets = DotMap(dict(pair for d in idata.targets['items'].allOf for pair in d.properties.items()))
            idata.pop('targets')
            idata = DotMap(dict(idata.toDict(), **targets.toDict()))
        if 'template' in self.type:
            profiles= list({v.name:v for v in kwargs.imm_dict.orgs[kwargs.org]['templates']['server']}.values())
        else:
            if self.type == 'domain':
                profiles = list({v.name:v for v in kwargs.imm_dict.orgs[kwargs.org].profiles[self.type]}.values())
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
                    ptype = (((k.replace('_policies', '')).replace(
                        '_address_pools', '')).replace('_pool', '')).replace('_policy', '')
                    if not kwargs.cp.get(ptype): kwargs.cp[ptype].names = []
                    def policy_list(k, policy, ptype, kwargs):
                        original_policy = policy
                        if '/' in policy: org, policy = policy.split('/')
                        else: org = kwargs.org; policy = policy
                        if 'pool' in k: p = 'pool'
                        else: p = 'policy'
                        np, ns = ezfunctions.name_prefix_suffix(ptype, kwargs)
                        policy = f"{np}{policy}{ns}"
                        if '/' in original_policy: new_policy = f'{org}/{policy}'
                        else: new_policy = policy
                        if not kwargs.isight[org][p][ptype].get(policy): kwargs.cp[ptype].names.append(new_policy)
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
    def san_connectivity(self, api_body, item, kwargs):
        if not api_body.get('PlacementMode'): api_body.update({'PlacementMode':'custom'})
        if item.get('wwnn_pool'):
            api_body['WwnnAddressType'] = 'POOL'
            if '/' in item.wwnn_pool: org, pool = item.wwnn_pool.split('/')
            else: org = kwargs.org; pool = item.wwnn_pool
            if not kwargs.isight[org].pool['wwnn'].get(pool): kwargs = api_get(False, [item.wwnn_pool], 'wwnn', kwargs)
            api_body['WwnnPool']['Moid'] = kwargs.isight[org].pool['wwnn'][pool]
        return api_body

    #=======================================================
    # SNMP Policy Modification
    #=======================================================
    def snmp(self, api_body, item, kwargs):
        item = item
        if api_body.get('SnmpTraps'):
            for x in range(len(api_body['SnmpTraps'])):
                if api_body['SnmpTraps'][x].get('Community'):
                    kwargs.sensitive_var = f"snmp_trap_community_{api_body['SnmpTraps'][x]['Community']}"
                    kwargs = ezfunctions.sensitive_var_value(kwargs)
                    api_body['SnmpTraps'][x]['Community'] = kwargs.var_value
        if api_body.get('SnmpUsers'):
            for x in range(len(api_body['SnmpUsers'])):
                if api_body['SnmpUsers'][x].get('AuthPassword'):
                    kwargs.sensitive_var = f"snmp_auth_password_{api_body['SnmpUsers'][x]['AuthPassword']}"
                    kwargs = ezfunctions.sensitive_var_value(kwargs)
                    api_body['SnmpUsers'][x]['AuthPassword'] = kwargs.var_value
                if api_body['SnmpUsers'][x].get('PrivacyPassword'):
                    kwargs.sensitive_var = f"snmp_privacy_password_{api_body['SnmpUsers'][x]['PrivacyPassword']}"
                    kwargs = ezfunctions.sensitive_var_value(kwargs)
                    api_body['SnmpUsers'][x]['PrivacyPassword'] = kwargs.var_value
        return api_body

    #=======================================================
    # Storage Policy Modification
    #=======================================================
    def storage(self, api_body, item, kwargs):
        item = item; kwargs = kwargs
        if api_body.get('M2VirtualDrive'): api_body['M2VirtualDrive']['Enable'] = True
        if api_body.get('Raid0Drive'):
            if not api_body['Raid0Drive'].get('Enable'): api_body['Raid0Drive']['Enable'] = True
            if not api_body['Raid0Drive'].get('VirtualDrivePolicy'):
                api_body['Raid0Drive']['VirtualDrivePolicy'] = {'ObjectType':'storage.VirtualDrivePolicy'}
                for k,v in kwargs.ezdata['storage.virtual_drive_policy'].properties.items():
                    if api_body['Raid0Drive']['VirtualDrivePolicy'].get(k):
                        api_body['Raid0Drive']['VirtualDrivePolicy'][v.intersight_api] = api_body['Raid0Drive']['VirtualDrivePolicy'][k]
                    else: api_body['Raid0Drive']['VirtualDrivePolicy'][v.intersight_api] = v.default
        return api_body

    #=======================================================
    # Syslog Policy Modification
    #=======================================================
    def syslog(self, api_body, item, kwargs):
        item = item; kwargs = kwargs
        if api_body.get('LocalClients'): api_body['LocalClients'] = [api_body['LocalClients']]
        return api_body

    #=======================================================
    # System QoS Policy Modification
    #=======================================================
    def system_qos(self, api_body, item, kwargs):
        item = item
        if api_body.get('configure_recommended_classes'):
            if api_body['configure_recommended_classes'] == True:
                api_body['Classes'] = kwargs.ezdata['system_qos.classes_recommended'].classes
            api_body.pop('configure_recommended_classes')
        elif api_body.get('configure_default_classes'):
            if api_body['configure_default_classes'] == True:
                api_body['Classes'] = kwargs.ezdata['system_qos.classes_default'].classes
            api_body.pop('configure_default_classes')
        elif api_body.get('configure_recommended_classes') == None and (api_body.get('Classes') == None or len(api_body.get('Classes')) == 0):
            api_body['Classes'] = kwargs.ezdata['system_qos.classes_default'].classes
        if api_body.get('jumbo_mtu'):
            for x in range(0, len(api_body['Classes'])):
                if api_body['Classes'][x].get('Priority'):
                    api_body['Classes'][x]['Name'] = api_body['Classes'][x]['Priority']; api_body['Classes'][x].pop('Priority')
                if api_body['jumbo_mtu'] == True: api_body['Classes'][x]['Mtu'] = 9000
                else: api_body['Classes'][x]['Mtu'] = 9000
                if api_body['Classes'][x]['Name'] == 'FC': api_body['Classes'][x]['Mtu'] = 2240
            api_body.pop('jumbo_mtu')
        classes = deepcopy(api_body['Classes']); api_body['Classes'] = []
        for e in classes:
            if not type(e) == dict: e.toDict()
            api_body['Classes'].append(e)
        return api_body

    #=====================================================
    # Assign Users to Local User Policies
    #=====================================================
    def users(self, kwargs):
        #=====================================================
        # Get Existing Users
        #=====================================================
        names = []; kwargs.bulk_list = []; role_names = []; kwargs.cp = DotMap()
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
                api_body = {'Name':e.username,'ObjectType':ezdata.ObjectType}
                api_body = org_map(api_body, kwargs.org_moids[kwargs.org].moid)
                kwargs.bulk_list.append(deepcopy(api_body))
            else: pcolor.Cyan(f"      * Skipping User: `{e}`.  Intersight Matches Configuration.  Moid: {kwargs.user_moids[e].moid}")
        #=====================================================
        # POST Bulk Request if Post List > 0
        #=====================================================
        if len(kwargs.bulk_list) > 0:
            kwargs.uri = kwargs.ezdata[self.type].intersight_uri
            kwargs     = bulk_request(kwargs)
        kwargs.user_moids = dict(kwargs.user_moids, **kwargs.pmoids)
        kwargs.bulk_list = []
        np, ns = ezfunctions.name_prefix_suffix('local_user', kwargs)
        for i in kwargs.policies:
            kwargs.parent_name = f'{np}{i.name}{ns}'
            kwargs.parent_type = 'Local User Policy'
            kwargs.parent_moid = kwargs.isight[kwargs.org].policy[self.type.split('.')[0]][kwargs.parent_name]
            if i.get('users'):
                for e in i.users:
                    kwargs.sensitive_var = f"local_user_password_{e.password}"
                    kwargs = ezfunctions.sensitive_var_value(kwargs)
                    user_moid = kwargs.user_moids[e.username].moid
                    #=====================================================
                    # Create API Body for User Role
                    #=====================================================
                    if e.get('enabled'): api_body = {'Enabled':e.enabled,'ObjectType':'iam.EndPointUserRole'}
                    else: api_body = {'Enabled':True,'ObjectType':'iam.EndPointUserRole'}
                    api_body.update({
                        'EndPointRole':[{'Moid':kwargs.role_moids[e.role].moid,'ObjectType':'iam.EndPointRole'}],
                        'EndPointUser':{'Moid':user_moid,'ObjectType':'iam.EndPointUser'},
                        'EndPointUserPolicy':{'Moid':kwargs.parent_moid,'ObjectType':'iam.EndPointUserPolicy'},
                        'Password':kwargs.var_value})
                    #=====================================================
                    # Create or Patch the Policy via the Intersight API
                    #=====================================================
                    if kwargs.cp[kwargs.parent_moid].moids.get(user_moid):
                        api_body['pmoid'] = kwargs.cp[kwargs.parent_moid].moids[user_moid].moid
                        kwargs.bulk_list.append(deepcopy(api_body))
                    else: kwargs.bulk_list.append(deepcopy(api_body))
        #=====================================================
        # POST Bulk Request if Post List > 0
        #=====================================================
        if len(kwargs.bulk_list) > 0:
            kwargs.uri = 'iam/EndPointUserRoles'
            kwargs     = bulk_request(kwargs)
        return kwargs

    #=======================================================
    # Virtual Media Policy Modification
    #=======================================================
    def virtual_media(self, api_body, item, kwargs):
        item = item
        if api_body.get('Mappings'):
            for x in range(api_body['Mappings']):
                if api_body['Mappings'][x].get('Password'):
                    kwargs.sensitive_var = f"vmedia_password_{api_body['Mappings'][x]['Password']}"
                    kwargs = ezfunctions.sensitive_var_value(kwargs)
                    api_body['Mappings'][x]['Password'] = kwargs.var_value
        return api_body

    #=====================================================
    # Assign VLANs to VLAN Policies
    #=====================================================
    def vlans(self, kwargs):
        #=====================================================
        # Loop Through VLAN Lists to Create api_body(s)
        #=====================================================
        def configure_vlans(e, kwargs):
            ezdata = kwargs.ezdata[self.type]
            api_body = {'EthNetworkPolicy':{'Moid':kwargs.parent_moid, 'ObjectType':'fabric.EthNetworkPolicy'}, 'ObjectType':ezdata.ObjectType}
            api_body = build_api_body(api_body, ezdata.properties, e, self.type, kwargs)
            api_body.pop('Organization'); api_body.pop('Tags')
            if not api_body.get('AutoAllowOnUplinks'): api_body.update({'AutoAllowOnUplinks':False})
            if '/' in e.multicast_policy: org, policy = e.multicast_policy.split('/')
            else: org = kwargs.org; policy = e.multicast_policy
            np, ns = ezfunctions.name_prefix_suffix('multicast', kwargs)
            policy = f"{np}{policy}{ns}"
            if not kwargs.isight[org].policy['multicast'].get(policy):
                validating.error_policy_doesnt_exist('multicast_policy', e.multicast_policy, self.type, 'Vlans', e.vlan_list)
            api_body['MulticastPolicy']['Moid'] = kwargs.isight[org].policy['multicast'][policy]
            if not api_body.get('IsNative'): api_body['IsNative'] = False
            for x in ezfunctions.vlan_list_full(e.vlan_list):
                if type(x) == str: x = int(x)
                if not len(ezfunctions.vlan_list_full(e.vlan_list)) == 1:
                    if e.name == 'vlan': api_body['Name'] = f"{e.name}{'0'*(4 - len(str(x)))}{x}"
                    else: api_body['Name'] = f"{e.name}-vl{'0'*(4 - len(str(x)))}{x}"
                api_body['VlanId'] = x
                #=====================================================
                # Create or Patch the VLANs via the Intersight API
                #=====================================================
                if not kwargs.isight[kwargs.org].policy[self.type].get(str(x)): kwargs.bulk_list.append(deepcopy(api_body))
                else:
                    indx = next((index for (index, d) in enumerate(kwargs.vlans_results) if d['VlanId'] == x), None)
                    patch_vlan = compare_body_result(api_body, kwargs.vlans_results[indx])
                    api_body['pmoid'] = kwargs.isight[kwargs.org].policy[self.type][str(x)]
                    if patch_vlan == True: kwargs.bulk_list.append(deepcopy(api_body))
                    else:
                        pcolor.Cyan(f"      * Skipping VLAN Policy: `{kwargs.parent_name}`, VLAN: `{x}`."\
                            f"  Intersight Matches Configuration.  Moid: {api_body['pmoid']}")
                    api_body.pop('pmoid')
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
                    np, ns = ezfunctions.name_prefix_suffix('multicast', kwargs)
                    policy = f"{np}{policy}{ns}"
                    if not kwargs.isight[org].policy['multicast'].get(policy):
                        if '/' in e.multicast_policy: policy = f'{org}/{policy}'
                        mcast_names.append(policy)
        mcast_names= list(numpy.unique(numpy.array(mcast_names)))
        kwargs     = api_get(False, mcast_names, 'multicast', kwargs)
        #=====================================================
        # Loop Through VLAN Policies
        #=====================================================
        kwargs.bulk_list = []
        np, ns = ezfunctions.name_prefix_suffix('vlan', kwargs)
        for i in kwargs.policies:
            vnames = []
            kwargs.parent_name= f'{np}{i.name}{ns}'
            kwargs.parent_type= 'VLAN Policy'
            kwargs.parent_moid= kwargs.isight[kwargs.org].policy[self.type.split('.')[0]][kwargs.parent_name]
            kwargs.pmoid      = kwargs.parent_moid
            kwargs.vlan_policy= f'{np}{i.name}{ns}'
            if i.get('vlans'):
                for e in i.vlans: vnames.extend(ezfunctions.vlan_list_full(e.vlan_list))
                kwargs = api_get(True, vnames, self.type, kwargs)
                kwargs.vlans_results= kwargs.results
                for e in i.vlans: kwargs = configure_vlans(e, kwargs)
        #=====================================================
        # POST Bulk Request if Post List > 0
        #=====================================================
        if len(kwargs.bulk_list) > 0:
            kwargs.uri    = kwargs.ezdata[self.type].intersight_uri
            kwargs        = bulk_request(kwargs)
        return kwargs

    #=====================================================
    # Assign VNICs to LAN Connectivity Policies
    #=====================================================
    def vnics(self, kwargs):
        #=====================================================
        # Get Policies and Pools
        #=====================================================
        ezdata = kwargs.ezdata[self.type]
        kwargs.cp = DotMap(); kwargs.bulk_list = []
        x = self.type.split('.')
        vpolicy = (kwargs.ezdata[x[0]].ObjectType).split('.')[1]
        kwargs.parent_type = (snakecase(vpolicy).replace('_', ' ')).title()
        vtype = x[1]
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
                            np, ns = ezfunctions.name_prefix_suffix(ptype, kwargs)
                            policy = f"{np}{policy}{ns}"
                            if '/' in original_policy: new_policy = f'{org}/{policy}'
                            else: new_policy = policy
                            if not kwargs.isight[org][p][ptype].get(policy): kwargs.cp[ptype].names.append(new_policy)
                            return kwargs
                        if type(v) == list:
                            for e in v: kwargs = policy_list(k, e, ptype, kwargs)
                        else: kwargs = policy_list(k, v, ptype, kwargs)
        for e in list(kwargs.cp.keys()):
            if len(kwargs.cp[e].names) > 0:
                names  = list(numpy.unique(numpy.array(names)))
                kwargs = api_get(False, names, e, kwargs)
        #=====================================================
        # Create API Body for vNICs
        #=====================================================
        for item in kwargs.policies:
            np, ns = ezfunctions.name_prefix_suffix('lan_connectivity', kwargs)
            kwargs.parent_name= f'{np}{item.name}{ns}'
            kwargs.parent_moid= kwargs.isight[kwargs.org].policy[self.type.split('.')[0]][kwargs.parent_name]
            kwargs.pmoid      = kwargs.parent_moid
            names   = []
            for i in item[vtype]: names.extend(i.names)
            kwargs = api_get(True, names, self.type, kwargs)
            vnic_results= kwargs.results
            for i in item[vtype]:
                for x in range(len(i.names)):
                    api_body = {vpolicy:{'Moid':kwargs.parent_moid,'ObjectType':f'vnic.{vpolicy}'}, 'ObjectType':ezdata.ObjectType}
                    api_body = build_api_body(api_body, ezdata.properties, i, self.type, kwargs)
                    api_body.update({'Name':i.names[x]})
                    api_body.pop('Organization'); api_body.pop('Tags')
                    api_body['Order'] = i.placement.pci_order[x]
                    if api_body['Placement'].get('Order'): api_body['Placement'].pop('Order')
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
                            np, ns = ezfunctions.name_prefix_suffix(ptype, kwargs)
                            policy = f"{np}{policy}{ns}"
                            if not kwargs.isight[org][p][ptype].get(policy):
                                if '/' in pname: err_policy = f'{org}/{policy}'
                                else: err_policy = policy
                                validating.error_policy_doesnt_exist(ptype, err_policy, self.type, p, i.names[x])
                            api_body[ezdata.properties[k].intersight_api.split(':')[1]]['Moid'] = kwargs.isight[org][p][ptype][policy]
                    if 'vnics' in self.type:
                        if not api_body.get('Cdn'): api_body.update({'Cdn':{'Value':i.names[x],'Source':'vnic','ObjectType':'vnic.Cdn'}})
                        api_body['FabricEthNetworkGroupPolicy'] = [api_body['FabricEthNetworkGroupPolicy']]
                        if api_body.get('StaticMacAddress'): api_body['StaticMacAddress'] = api_body['StaticMacAddress'][x]
                    else:
                        def zone_update(pname, ptype, kwargs):
                            if '/' in pname: org, policy = pname.split('/')
                            else: org = kwargs.org; policy = pname
                            np, ns = ezfunctions.name_prefix_suffix(ptype, kwargs)
                            policy = f"{np}{policy}{ns}"
                            if not kwargs.isight[org].policy[ptype].get(policy):
                                if '/' in pname: err_policy = f'{org}/{policy}'
                                else: err_policy = policy
                                validating.error_policy_doesnt_exist(ptype, err_policy, self.type, 'policy', i.names[x])
                            kwargs.zbody['Moid'] = kwargs.isight[org].policy[ptype][policy]
                            return kwargs.zbody
                        if i.get('fc_zone_policies'):
                            kwargs.zbody= deepcopy(api_body['FcZonePolicies'])
                            api_body['FcZonePolicies'] = []
                            if len(i.names) == 2:
                                half = len(i.fc_zone_policies)//2
                                if x == 0: zlist = i.fc_zone_policies[half:]
                                else: zlist = i.fc_zone_policies[:half]
                                for e in zlist: api_body['FcZonePolicies'].append(zone_update(e, 'fc_zone', kwargs))
                            else:
                                for e in i.fc_zone_policies: api_body['FcZonePolicies'].append(zone_update(e, 'fc_zone', kwargs))
                        if api_body.get('StaticWwpnAddress'): api_body['StaticWwpnAddress'] = api_body['StaticWwpnAddress'][x]
                    if x == 0: side = 'A'
                    else: side = 'B'
                    api_body.update({'Placement':{'Id':'MLOM','ObjectType':'vnic.PlacementSettings','PciLink':0,'SwitchId':side,'Uplink':0}})
                    if i.get('placement'):
                        place_list = ['pci_links', 'slot_ids', 'switch_ids', 'uplink_ports']
                        for p in place_list:
                            if i.get(p):
                                if len(i[p]) == 2: pval = i[p][x]
                                else: pval = i[p][0]
                                api_body['Placement'][ezdata.properties.placement.properties[p].intersight_api] = pval
                    #=====================================================
                    # Create or Patch the VLANs via the Intersight API
                    #=====================================================
                    if kwargs.isight[kwargs.org].policy[self.type].get(i.names[x]):
                        indx = next((index for (index, d) in enumerate(vnic_results) if d['Name'] == i.names[x]), None)
                        patch_vsan = compare_body_result(api_body, vnic_results[indx])
                        api_body['pmoid'] = kwargs.isight[kwargs.org].policy[self.type][i.names[x]]
                        if patch_vsan == True: kwargs.bulk_list.append(deepcopy(api_body))
                        else:
                            pcolor.Cyan(f"      * Skipping {kwargs.parent_type} `{kwargs.parent_name}`: VNIC: `{i.names[x]}`."\
                                f"  Intersight Matches Configuration.  Moid: {api_body['pmoid']}")
                    else: kwargs.bulk_list.append(deepcopy(api_body))
        #=====================================================
        # POST Bulk Request if Post List > 0
        #=====================================================
        if len(kwargs.bulk_list) > 0:
            kwargs.uri    = ezdata.intersight_uri
            kwargs        = bulk_request(kwargs)
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
            api_body = {'FcNetworkPolicy':{'Moid':kwargs.parent_moid, 'ObjectType':'fabric.FcNetworkPolicy'}, 'ObjectType':ezdata.ObjectType}
            api_body = build_api_body(api_body, ezdata.properties, e, self.type, kwargs)
            api_body.pop('Organization'); api_body.pop('Tags')
            if not api_body.get('VsanScope'): api_body['VsanScope'] = 'Uplink'
            if not api_body.get('FcoeVlan'): api_body['FcoeVlan'] = api_body['VsanId']
            #=====================================================
            # Create or Patch the VLANs via the Intersight API
            #=====================================================
            if not kwargs.isight[kwargs.org].policy[self.type].get(str(api_body['VsanId'])): kwargs.bulk_list.append(deepcopy(api_body))
            else:
                indx = next((index for (index, d) in enumerate(kwargs.vsans_results) if d['VsanId'] == api_body['VsanId']), None)
                patch_vsan = compare_body_result(api_body, kwargs.vsans_results[indx])
                api_body['pmoid']  = kwargs.isight[kwargs.org].policy[self.type][str(api_body['VsanId'])]
                if patch_vsan == True: kwargs.bulk_list.append(deepcopy(api_body))
                else:
                    pcolor.Cyan(f"      * Skipping VSAN Policy: `{kwargs.parent_name}`, VSAN: `{api_body['VsanId']}`."\
                           f"  Intersight Matches Configuration.  Moid: {api_body['pmoid']}")
            return kwargs
        #=====================================================
        # Loop Through VSAN Policies
        #=====================================================
        kwargs.bulk_list = []
        np, ns = ezfunctions.name_prefix_suffix('vsan', kwargs)
        for i in kwargs.policies:
            vnames = []
            kwargs.parent_name= f'{np}{i.name}{ns}'
            kwargs.parent_type= 'VSAN Policy'
            kwargs.parent_moid= kwargs.isight[kwargs.org].policy[self.type.split('.')[0]][kwargs.parent_name]
            kwargs.pmoid      = kwargs.parent_moid
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
        if len(kwargs.bulk_list) > 0:
            kwargs.uri    = kwargs.ezdata[self.type].intersight_uri
            kwargs        = bulk_request(kwargs)
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
def assign_physical_device(api_body, kwargs):
    if kwargs.type == 'switch':
        if len(api_body['SerialNumber']) == 2: serial = api_body['SerialNumber'][kwargs.x_number]
        else: serial = 'BLAH'
    else: serial = api_body['SerialNumber']
    if re.search(serial_regex, serial): serial_true = True
    else: serial_true = False
    if serial_true == True:
        if kwargs.serial_moids.get(serial):
            serial_moid = kwargs.serial_moids[serial].moid
            sobject     = kwargs.serial_moids[serial]['object_type']
        else: validating.error_serial_number(api_body['Name'], serial)
        ptype = kwargs.type.capitalize()
        api_body.update({f'Assigned{ptype}':{'Moid':serial_moid, 'ObjectType':sobject}})
        api_body = dict(sorted(api_body.items()))
    api_body.pop('SerialNumber')
    return api_body

#=====================================================
# Add Attributes to the api_body
#=====================================================
def build_api_body(api_body, idata, item, ptype, kwargs):
    np, ns = ezfunctions.name_prefix_suffix(ptype, kwargs)
    for k, v in item.items():
        #print(json.dumps(idata, indent=4))
        #print(k, v)
        if re.search('boolean|string|integer', idata[k].type):
            if '$ref:' in idata[k].intersight_api:
                x = idata[k].intersight_api.split(':')
                if not api_body.get(x[1]): api_body.update({x[1]:{x[3]:v, 'ObjectType':x[2]}})
            elif '$pbucket:' in idata[k].intersight_api:
                if not api_body.get('PolicyBucket'): api_body['PolicyBucket'] = []
                x = idata[k].intersight_api.split(':')
                api_body['PolicyBucket'].append({x[2]:v,'policy':k,'ObjectType':x[1]})
            else: api_body.update({idata[k].intersight_api:v})
        elif idata[k].type == 'array':
            if re.search('boolean|string|integer',  idata[k]['items'].type):
                if '$ref:' in idata[k]['items'].intersight_api:
                    x = idata[k]['items'].intersight_api.split(':')
                    if not api_body.get(x[1]): api_body.update({x[1]:{'ObjectType':x[2]}})
                    api_body[x[1]].update({x[3]:v})
                elif '$pbucket:' in idata[k].intersight_api:
                    if not api_body.get('PolicyBucket'): api_body['PolicyBucket'] = []
                    x = idata[k].intersight_api.split(':')
                    api_body['PolicyBucket'].append({x[2]:v,'policy':k,'ObjectType':x[1]})
                else:
                    api_body[idata[k]['items'].intersight_api] = []
                    for e in v: api_body[idata[k]['items'].intersight_api].append(e)
            else:
                api_body[idata[k]['items'].intersight_api] = []
                for e in v:
                    if type(e) == str:
                        api_body[idata[k]['items'].intersight_api].append(e)
                    else:
                        idict = {'ObjectType':idata[k]['items'].ObjectType}
                        for a, b in idata[k]['items'].properties.items():
                            if re.search('boolean|string|integer', b.type):
                                if a in e and '$ref:' in b.intersight_api:
                                    x = b.intersight_api.split(':')
                                    if not idict.get(x[1]): idict.update({x[1]:{x[3]:e[a], 'ObjectType':x[2]}})
                                elif a in e: idict.update({b.intersight_api:e[a]})
                            elif b.type == 'object' and a in e:
                                idict.update({b.intersight_api:{'ObjectType':b.ObjectType}})
                                for c, d in b.properties.items():
                                    if e[a].get(c): idict[b.intersight_api].update({d.intersight_api:e[a][c]})
                            elif b.type == 'array' and a in e:
                                if not re.search('(l|s)an_connectivity|firmware|port|storage', kwargs.type):
                                    pcolor.Cyan(f'\n++{"-"*91}\n\n')
                                    pcolor.Cyan(f'{k}\n{a}\n{b}\n{e[c]}')
                                    prRed(f'!!! ERROR !!! undefined mapping for array in array: `{d.type}`')
                                    pcolor.Cyan(kwargs.type)
                                    pcolor.Cyan(f'\n++{"-"*91}\n\n')
                                    sys.exit(1)
                                idict[b.intersight_api] = e[a]
                        idict = dict(sorted(idict.items()))
                        api_body[idata[k]['items'].intersight_api].append(idict)
        elif idata[k].type == 'object':
            api_body[idata[k].intersight_api] = {'ObjectType':idata[k].ObjectType}
            for a, b in idata[k].properties.items():
                if b.type == 'array':
                    if re.search('pci_(links|order)|slot_ids|switch_ids|uplink_ports', a):
                        if v.get(a): api_body[idata[k].intersight_api].update({b.intersight_api:v[a]})
                    elif v.get(a):
                        api_body[idata[k].intersight_api].update({b.intersight_api:[]})
                        idict = {'ObjectType':b['items'].ObjectType}
                        for e in v[a]:
                            for c,d in b['items'].properties.items():
                                if d.type == 'string' and e.get(c):
                                    idict.update({d.intersight_api:e[c]})
                                    api_body[idata[k].intersight_api][b.intersight_api].append(idict)
                                else:
                                    pcolor.Cyan(f'\n++{"-"*91}\n\n')
                                    pcolor.Cyan(f'{c}\n{d}\n{e}\n{e[c]}')
                                    prRed(f'!!! ERROR !!! undefined mapping for array in object: `{d.type}`')
                                    pcolor.Cyan(f'\n++{"-"*91}\n\n')
                                    sys.exit(1)
                elif b.type == 'object':
                    pcolor.Cyan(f'\n++{"-"*91}\n\n')
                    pcolor.Cyan(f'{k}\n{a}\n{b}\n{v}')
                    prRed('!!! ERROR !!! undefined mapping for object in object')
                    pcolor.Cyan(f'\n++{"-"*91}\n\n')
                    sys.exit(1)
                elif v.get(a): api_body[idata[k].intersight_api].update({b.intersight_api:v[a]})
            api_body[idata[k].intersight_api] = dict(sorted(api_body[idata[k].intersight_api].items()))
    #=====================================================
    # Validate all Parameters are String if BIOS
    #=====================================================
    if ptype == 'bios':
        for k, v in api_body.items():
            if type(v) == int or type(v) == float: api_body[k] = str(v)
    #=====================================================
    # Add Policy Specific Settings
    #=====================================================
    if re.fullmatch(policy_specific_regex, ptype): api_body = eval(f'imm(ptype).{ptype}(api_body, item, kwargs)')
    plist1 = [
        'pc_appliances', 'pc_ethernet_uplinks', 'pc_fc_uplinks', 'pc_fcoe_uplinks', 'port_modes',
        'rl_appliances', 'rl_ethernet_uplinks', 'rl_fc_storage', 'rl_fc_uplinks', 'rl_fcoe_uplinks', 'rl_servers',
        'drive_groups', 'ldap_groups', 'ldap_servers', 'users', 'vhbas', 'vlans', 'vnics', 'vsans']
    pop_list = []
    for e in plist1: pop_list.append((e.replace('pc_', 'port_channel_')).replace('rl_', 'port_role_'))
    for e in pop_list:
        if api_body.get(e): api_body.pop(e)
    #=====================================================
    # Attach Organization Map, Tags, and return Dict
    #=====================================================
    api_body = org_map(api_body, kwargs.org_moids[kwargs.org].moid)
    if api_body.get('Tags'): api_body['Tags'].append(kwargs.ez_tags.toDict())
    else: api_body.update({'Tags':[kwargs.ez_tags.toDict()]})
    api_body = dict(sorted(api_body.items()))
    if api_body.get('Descr'):
        if api_body['Name'] in api_body['Descr']: api_body['Descr'].replace(api_body['Name'], f"{np}{api_body['Name']}{ns}")
    if not re.search('DriveGroups|EndPointUser|LdapGroups|vlan|vnic|vsan', api_body['ObjectType']):
        if api_body.get('Name'): api_body['Name'] = f"{np}{api_body['Name']}{ns}"
    #print(json.dumps(api_body, indent=4))
    return api_body

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
            elif i.get('PciSlot'): iname = str(i.PciSlot)
            if i.get('PcId') or i.get('PortId') or i.get('PortIdStart'):
                apiDict[i.PortPolicy.Moid][iname].moid = i.Moid
            else: apiDict[iname].moid = i.Moid
            if i.get('IpV4Config'): apiDict[iname].ipv4_config = i.IpV4Config
            if i.get('IpV6Config'): apiDict[iname].ipv6_config = i.IpV6Config
            if i.get('ManagementMode'): apiDict[iname].management_mode = i.ManagementMode
            if i.get('MgmtIpAddress'): apiDict[iname].management_ip_address = i.MgmtIpAddress
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
def bulk_request(kwargs):
    def post_to_api(kwargs):
        kwargs.method = 'post'
        kwargs.qtype  = 'bulk_request'
        kwargs.uri    = 'bulk/Requests'
        kwargs        = api(kwargs.qtype).calls(kwargs)
        return kwargs

    def loop_thru_lists(kwargs):
        if len(kwargs.api_body['Requests']) > 99:
            requests_list = deepcopy(kwargs.api_body['Requests'])
            chunked_list = list(); chunk_size = 100
            for i in range(0, len(requests_list), chunk_size):
                chunked_list.append(requests_list[i:i+chunk_size])
            for i in chunked_list:
                kwargs.api_body['Requests'] = i
                kwargs = post_to_api(kwargs)
        else: kwargs = post_to_api(kwargs)
        return kwargs

    patch_list = []
    post_list  = []
    for e in kwargs.bulk_list:
        if e.get('pmoid'):
            tmoid = e['pmoid']
            e.pop('pmoid')
            patch_list.append({
                'Body':e, 'ClassId':'bulk.RestSubRequest', 'ObjectType':'bulk.RestSubRequest', 'TargetMoid': tmoid,
                'Uri':f'/v1/{kwargs.uri}', 'Verb':'PATCH'})
        else:
            post_list.append({
                'Body':e, 'ClassId':'bulk.RestSubRequest', 'ObjectType':'bulk.RestSubRequest', 'Uri':f'/v1/{kwargs.uri}', 'Verb':'POST'})
    if len(patch_list) > 0:
        kwargs.api_body = {'Requests':patch_list}
        kwargs = loop_thru_lists(kwargs)
    if len(post_list) > 0:
        kwargs.api_body = {'Requests':post_list}
        kwargs = loop_thru_lists(kwargs)
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
def compare_body_result(api_body, result):
    if api_body.get('PolicyBucket'):
        api_body['PolicyBucket'] = sorted(api_body['PolicyBucket'], key=lambda item: item['ObjectType'])
        result['PolicyBucket'] = sorted(result['PolicyBucket'], key=lambda item: item['ObjectType'])
    patch_return = False
    for k, v in api_body.items():
        if type(v) == dict:
            for a,b in v.items():
                if type(b) == list:
                    count = 0
                    for e in b:
                        if type(e) == dict:
                            for c,d in e.items():
                                if len(result[k][a]) - 1 < count: patch_return = True
                                elif not result[k][a][count][c] == d: patch_return = True
                        else:
                            if len(result[k][a]) - 1 < count: patch_return = True
                            elif not result[k][a][count] == e: patch_return = True
                elif not result[k][a] == b: patch_return = True
        elif type(v) == list:
            count = 0
            for e in v:
                if type(e) == dict:
                    for a,b in e.items():
                        if type(b) == dict:
                            for c,d in b.items():
                                if len(result[k]) - 1 < count: patch_return = True
                                elif not result[k][count][a][c] == d: patch_return = True
                        elif type(b) == list:
                            scount = 0
                            for s in b:
                                if type(s) == dict:
                                    for g,h in s.items():
                                        if len(result[k]) - 1 < count: patch_return = True
                                        elif not result[k][count][a][scount][g] == h: patch_return = True
                                scount += 1
                        else:
                            if 'Password' in a: count = count
                            elif len(result[k]) - 1 < count: patch_return = True
                            elif not result[k][count][a] == b: patch_return = True
                elif type(e) == list:
                    prRed(e)
                    prRed('compare_body_result; not accounted for')
                    sys.exit(1)
                else:
                    if len(result[k]) - 1 < count: patch_return = True
                    elif not result[k][count] == e: patch_return = True
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
    if deploy_profiles == True: pcolor.LightPurple(f'\n{"-"*91}\n')
    if pending_changes == True: pcolor.Cyan('      * Sleeping for 120 Seconds'); time.sleep(120)
    for item in profiles:
        if kwargs.cluster_update[item.name].pending_changes == True:
            for x in range(0,2):
                pname = f"{item.name}-{chr(ord('@')+x+1)}"
                pcolor.Green(f'    - Beginning Profile Deployment for {pname}')
                kwargs.api_body= {'Action':'Deploy'}
                kwargs.method = 'patch'
                kwargs.pmoid  = kwargs.isight[kwargs.org].profile['switch'][pname]
                kwargs = api('switch').calls(kwargs)
    if deploy_profiles == True: pcolor.LightPurple(f'\n{"-"*91}\n'); time.sleep(60)
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
                        pcolor.Green(f'    - Completed Profile Deployment for {pname}')
                        deploy_complete = True
                    else:  pcolor.Cyan(f'      * Deploy Still Occuring on {pname}.  Waiting 120 seconds.'); time.sleep(120)
    if deploy_profiles == True: pcolor.LightPurple(f'\n{"-"*91}\n')
    return kwargs

#======================================================
# Function - Deploy Chassis/Server Profile if Action is Deploy
#======================================================
def deploy_chassis_server_profiles(profiles, kwargs):
    print('matched deploy')
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
            pcolor.LightPurple(f'\n{"-"*91}\n')
            deploy_pending = False
            for e in list(kwargs.profile_updates.keys()):
                if kwargs.profile_update[e].pending_changes == 'Deploy': deploy_pending = True
            if deploy_pending == True:
                if 'server' == kwargs.type:  pcolor.LightPurple('    * Pending Changes.  Sleeping for 120 Seconds'); time.sleep(120)
                else:  pcolor.LightPurple('    * Pending Changes.  Sleeping for 60 Seconds'); time.sleep(60)
            for e in list(kwargs.profile_update.keys()):
                if kwargs.profile_update[e].pending_changes == 'Deploy':
                    pcolor.Green(f'    - Beginning Profile Deployment for `{e}`.')
                    kwargs.api_body= {'Action':'Deploy'}
                    kwargs.method = 'patch'
                    kwargs.pmoid  = kwargs.isight[kwargs.org].profile[kwargs.type][e]
                    kwargs = api(kwargs.type).calls(kwargs)
                else: pcolor.LightPurple(f'    - Skipping Profile Deployment for `{e}`.  No Pending Changes.')
            if deploy_pending == True:
                if 'server' == kwargs.type:  pcolor.LightPurple('    * Deploying Changes.  Sleeping for 600 Seconds'); time.sleep(600)
                else:  pcolor.LightPurple('    * Deploying Changes.  Sleeping for 60 Seconds'); time.sleep(60)
            for e in list(kwargs.profile_update.keys()):
                if kwargs.profile_update[e].pending_changes == 'Deploy':
                    deploy_complete= False
                    while deploy_complete == False:
                        kwargs.method = 'get_by_moid'
                        kwargs.pmoid  = kwargs.isight[kwargs.org].profile[kwargs.type][e]
                        kwargs = api(kwargs.qtype).calls(kwargs)
                        if kwargs.results.ConfigContext.ControlAction == 'No-op':
                            deploy_complete = True
                            if re.search('^(chassis)$', kwargs.type): pcolor.Green(f'    - Completed Profile Deployment for `{e}`.')
                        else: 
                            if 'server' == kwargs.type: pcolor.Cyan(f'      * Deploy Still Occuring on `{e}`.  Waiting 120 seconds.'); time.sleep(120)
                            else: pcolor.Cyan(f'      * Deploy Still Occuring on `{e}`.  Waiting 60 seconds.'); time.sleep(60)
            if 'server' == kwargs.type:
                pcolor.LightPurple(f'\n{"-"*91}\n')
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
                            pcolor.Green(f'    - Beginning Profile Activation for `{e}`.')
                            kwargs.api_body= {'ScheduledActions':[{'Action':'Activate', 'ProceedOnReboot':True}]}
                            kwargs.method = 'patch'
                            kwargs.pmoid  = kwargs.isight[kwargs.org].profile[kwargs.type][e]
                            kwargs = api(kwargs.qtype).calls(kwargs)
                        else:
                            pcolor.LightPurple(f'    - Skipping Profile Activation for `{e}`.  No Pending Changes.')
                            kwargs.profile_update[e].pending_changes = 'Blank'
                pcolor.LightPurple(f'\n{"-"*91}\n')
                pcolor.LightPurple('    * Pending Activitions.  Sleeping for 600 Seconds'); time.sleep(600)
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
                                pcolor.Green(f'    - Completed Profile Activiation for `{e}`.')
                                deploy_complete = True
                            else:  pcolor.Cyan(f'      * Activiation Still Occuring on `{e}`.  Waiting 120 seconds.'); time.sleep(120)
            pcolor.LightPurple(f'\n{"-"*91}\n')
    exit()
    return kwargs

#======================================================
# Function - Exit on Empty Results
#======================================================
def empty_results(kwargs):
        prRed(f"The API Query Results were empty for {kwargs.uri}.  Exiting..."); sys.exit(1)

#=======================================================
# Add Organization Key Map to Dictionaries
#=======================================================
def org_map(api_body, org_moid):
    api_body.update({'Organization':{'Moid':org_moid, 'ObjectType':'organization.Organization'}})
    return api_body

#=======================================================
# Profile Creation Function
#=======================================================
def profile_api_calls(api_body, kwargs):
    if kwargs.isight[kwargs.org].profile[kwargs.type].get(api_body['Name']):
        indx = next((index for (index, d) in enumerate(kwargs.profile_results) if d['Name'] == api_body['Name']), None)
        patch_port = compare_body_result(api_body, kwargs.profile_results[indx])
        api_body['pmoid'] = kwargs.isight[kwargs.org].profile[kwargs.type][api_body['Name']]
        if patch_port == True: kwargs.bulk_list.append(deepcopy(api_body))
        else:
            if 'server_template' in kwargs.type: ntitle = 'Server Profile Template'
            else: ntitle = f'{kwargs.type.title()} Profile'
            pcolor.Cyan(f"      * Skipping {ntitle}: `{api_body['Name']}`.  Intersight Matches Configuration.  Moid: {api_body['pmoid']}")
    else: kwargs.bulk_list.append(deepcopy(api_body))
    return kwargs

#=====================================================
# Assign Moid to Policy in Bucket
#=====================================================
def profile_policy_bucket(api_body, kwargs):
    for x in range(len(api_body['PolicyBucket'])):
        ptype = ((api_body['PolicyBucket'][x]['policy']).replace('_policy', '')).replace('_policies', '')
        api_body['PolicyBucket'][x].pop('policy')
        if kwargs.type == 'switch':
            if re.search('-A', api_body['Name']): f = 0
            else: f = 1
        if type(api_body['PolicyBucket'][x]['Moid']) == list:
            if len(api_body['PolicyBucket'][x]['Moid']) == 2: opolicy = api_body['PolicyBucket'][x]['Moid'][f]
            else: opolicy = api_body['PolicyBucket'][x]['Moid'][0]
        else: opolicy = api_body['PolicyBucket'][x]['Moid']
        if '/' in opolicy: org, policy = opolicy.split('/')
        else: org = kwargs.org; policy = opolicy
        if not kwargs.isight[org].policy[ptype].get(policy):
            validating.error_policy_doesnt_exist(ptype, opolicy, kwargs.type, 'profile', api_body['Name'])
        api_body['PolicyBucket'][x]['Moid'] = kwargs.isight[org].policy[ptype][policy]
    if api_body.get('UuidPool'):
        api_body['UuidAddressType'] = 'POOL'
        if '/' in api_body.get('UuidPool'): org, pool = api_body['UuidPool']['Moid'].split('/')
        else: org = kwargs.org; pool = api_body['UuidPool']['Moid']
        if not kwargs.isight[org].pool['uuid'].get(pool):
            validating.error_policy_doesnt_exist('uuid', api_body['UuidPool']['Moid'], kwargs.type, 'profile', api_body['Name'])
        api_body['UuidPool']['Moid'] = kwargs.isight[org].pool['uuid'][pool]
    return api_body
