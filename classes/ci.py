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
    from classes import claim_device, ezfunctions, isight, netapp, validating
    from copy import deepcopy
    from dotmap import DotMap
    import ipaddress, json, numpy, os, re, requests, sys, time, urllib3
except ImportError as e:
    prRed(f'!!! ERROR !!!\n{e.__class__.__name__}')
    prRed(f" Module {e.name} is required to run this script")
    prRed(f" Install the module using the following: `pip install {e.name}`")
    sys.exit(1)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

#=============================================================================
# IMM Class
#=============================================================================
class imm(object):
    def __init__(self, type):
        self.type = type

    #=============================================================================
    # Function - Build Policies - BIOS
    #=============================================================================
    def bios(self, kwargs):
        # Build Dictionary
        descr     = (self.type.replace('_', ' ')).upper()
        btemplates= []
        dataset   = []
        for k, v in kwargs.servers.items():
            dataset.append(f"{v.gen}-{v.cpu}-{v.tpm}")
        models = numpy.unique(numpy.array(dataset))
        for i in models:
            gen, cpu, tpm = i.split('-')
            if kwargs.args.deployment_type == 'azure_hci':
                if len(tpm) > 0: btemplates.append(f'{gen}-azure-{cpu}-tpm')
                else: btemplates.append(f'{gen}-azure-{cpu}')
            else:
                if len(tpm) > 0: btemplates.append(f'{gen}-{cpu}-virtual-tpm')
                else: btemplates.append(f'{gen}-{cpu}-virtual')
        btemplates = list(numpy.unique(numpy.array(btemplates)))
        for i in btemplates:
            polVars = dict(
                baud_rate           = '115200',
                bios_template       = i,
                console_redirection = f'serial-port-a',
                description         = f'{kwargs.imm.policies.prefix}{i} {descr} Policy',
                name                = f'{kwargs.imm.policies.prefix}{i}',
                serial_port_aenable = f'enabled',
                terminal_type       = f'vt100',
            )

            # Add Policy Variables to imm_dict
            kwargs.class_path = f'policies,{self.type}'
            kwargs = ezfunctions.ez_append(polVars, kwargs)

        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs

    #=============================================================================
    # Function - Build Policies - Boot Order
    #=============================================================================
    def boot_order(self, kwargs):
        # Build Dictionary
        ptypes = []
        if kwargs.imm.policies.boot_volume == 'san': ptypes.append('fcp')
        else: ptypes.append('m2')
        for i in kwargs.vlans:
            if re.search('iscsi', i.vlan_type): ptypes.append(i.vlan_type)
        ptypes = list(numpy.unique(numpy.array(ptypes)))
        for i in ptypes:
            polVars = {
                'boot_devices': [{
                    'enabled': True,
                    'name': 'kvm',
                    'object_type': 'boot.VirtualMedia',
                    'sub_type': 'kvm-mapped-dvd'
                }],
                'boot_mode': 'Uefi',
                'description': f'{i} Boot Policy',
                'enable_secure_boot': True,
                'name': f'{kwargs.imm.policies.prefix}{i}-boot',
            }
            if 'fcp' in i:
                fabrics = ['a', 'b']
                for x in range(0,len(fabrics)):
                    for k,v in kwargs.imm_dict.orgs[kwargs.org].storage.items():
                        for e in v:
                            for s in e['wwpns'][chr(ord('@')+x+1).lower()]:
                                polVars['boot_devices'].append({
                                    'enabled': True,
                                    'interface_name': f'vhba{x+1}',
                                    'name':  e.svm + '-' + s.interface,
                                    'object_type': 'boot.San',
                                    'slot':'MLOM',
                                    'wwpn': s.wwpn
                                })
            elif 'iscsi' in i:
                fabrics = ['a', 'b']
                for fab in fabrics:
                        polVars['boot_devices'].append({
                            'enabled': True,
                            'interface_name': f'storage-{fab}',
                            'name': f'storage-{fab}',
                            'object_type': 'boot.Iscsi',
                            'slot':'MLOM'
                        })
            elif 'm2' in i:
                polVars['boot_devices'].append({
                    'enabled': True,
                    'name': f'm2',
                    'object_type': 'boot.LocalDisk',
                    'slot':'MSTOR-RAID'
                })
            polVars['boot_devices'].append({
                'enabled': True,
                'name': 'cimc',
                'object_type': 'boot.VirtualMedia',
                'sub_type': 'cimc-mapped-dvd'
            })
            polVars['boot_devices'].append({
                'enabled': True,
                'name': 'uefishell',
                'object_type': 'boot.UefiShell'
            })
            
            # Add Policy Variables to imm_dict
            kwargs.class_path = f'policies,{self.type}'
            kwargs = ezfunctions.ez_append(polVars, kwargs)

        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs

    #=============================================================================
    # Function - Build Profiles - Chassis
    #=============================================================================
    def chassis(self, kwargs):
        # Build Dictionary
        for k, v in kwargs.chassis.items():
            polVars = dict(
                action            = 'Deploy',
                imc_access_policy = f'{kwargs.imm.policies.prefix}kvm',
                power_policy      = f'{kwargs.imm.policies.prefix}{k}',
                snmp_policy       = f'{kwargs.imm.policies.prefix}snmp',
                thermal_policy    = f'{kwargs.imm.policies.prefix}{k}',
                targets           = [],
            )
            for i in v:
                polVars['targets'].append(dict(
                    description   = f'{i.domain}-{i.identity} Chassis Profile',
                    name          = f'{i.domain}-{i.identity}',
                    serial_number = i.serial
                ))
            
            # Add Policy Variables to imm_dict
            kwargs.class_path = f'profiles,{self.type}'
            kwargs = ezfunctions.ez_append(polVars, kwargs)
        
        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs

    #=============================================================================
    # Function - Build Profiles - Chassis
    #=============================================================================
    def compute_environment(self, kwargs):
        kwargs.servers  = DotMap([])
        #=====================================================
        # Server Dictionary Function
        #=====================================================
        def server_dictionary(i, kwargs):
            kwargs.method    = 'get'
            kwargs.api_filter= f"Ancestors/any(t:t/Moid eq '{i.Moid}')"
            kwargs.qtype     = 'processor'
            kwargs.uri       = 'processor/Units'
            kwargs= isight.api(kwargs.qtype).calls(kwargs)
            cpu   = kwargs.results[0]
            kwargs.api_filter= f"Ancestors/any(t:t/Moid eq '{i.Moid}')"
            kwargs.qtype     = 'storage_controllers'
            kwargs.uri       = 'storage/Controllers'
            kwargs = isight.api(kwargs.qtype).calls(kwargs)
            storage= kwargs.results
            kwargs.api_filter= f"Ancestors/any(t:t/Moid eq '{i.Moid}')"
            kwargs.qtype     = 'tpm'
            kwargs.uri       = 'equipment/Tpms'
            kwargs= isight.api(kwargs.qtype).calls(kwargs)
            tpmd  = kwargs.results
            kwargs.api_filter= f"Ancestors/any(t:t/Moid eq '{i.Moid}')"
            kwargs.qtype     = 'adapter'
            kwargs.uri       = 'adapter/Units'
            kwargs = isight.api(kwargs.qtype).calls(kwargs)
            vic    = kwargs.results
            if 'Intel' in cpu.Vendor: cv = 'intel'
            else: cv = 'amd'
            storage_controllers = DotMap()
            for e in storage:
                if len(e.Model) > 0: storage_controllers[e.Model] = e.ControllerId
            vics = []
            for e in vic:
                if re.search('(V5)', e.Model): vic_generation = 'gen5'
                else: vic_generation = 'gen4'
                if 'MLOM' in e.PciSlot:
                    vic_slot = 'MLOM'
                    vics.append(DotMap(vic_gen= vic_generation, vic_slot=vic_slot))
                elif not 'MEZZ' in e.PciSlot:
                    vic_slot = re.search('SlotID:(\\d)', e.PciSlot).group(1)
                    vics.append(DotMap(vic_gen= vic_generation, vic_slot=vic_slot))

            sg = re.search('-(M[\\d])', i.Model).group(1)
            if type(vics[0].vic_slot) == str: vs1= (vics[0].vic_slot).lower()
            else: vs1= vics[0].vic_slot
            if len(vics) == 2:
                if type(vics[1].vic_slot) == str: vs2= (vics[1].vic_slot).lower()
                else: vs2= vics[1].vic_slot
            if len(tpmd) > 0:
                tpm = 'tpm'
                if len(vics) == 2:
                    template = f"{sg}-{cv}-tpm-vic-{vics[0].vic_gen}-{vs1}-{vs2}"
                else: template = f"{sg}-{cv}-tpm-vic-{vics[0].vic_gen}-{vs1}"
            else:
                tpm = ''
                if len(vics) == 2:
                    template = f"{sg}-{cv}-vic-{vics[0].vic_gen}-{vs1}-{vs2}"
                else: template = f"{sg}-{cv}-vic-{vics[0].vic_gen}-{vs1}"
            kwargs.servers[i.Serial] = DotMap(
                chassis_id         = i.ChassisId,
                chassis_moid       = i.Parent.Moid,
                cpu                = cv,
                domain             = kwargs.domain.name,
                firmware           = i.Firmware,
                gen                = sg,
                moid               = i.Moid,
                model              = i.Model,
                object_type        = i.SourceObjectType,
                serial             = i.Serial,
                server_id          = i.ServerId,
                slot               = i.SlotId,
                storage_controllers= storage_controllers,
                template           = template,
                tpm                = tpm,
                vics               = vics
            )
            if i.SourceObjectType == 'compute.RackUnit': kwargs.servers[i.Serial].pop('chassis_moid')
            return kwargs

        #=====================================================
        # Build Domain Dictionaries
        #=====================================================
        if kwargs.domain:
            kwargs.chassis= DotMap([])
            kwargs.method = 'get'
            kwargs.names  = [kwargs.domain.serial_numbers[0]]
            kwargs.qtype  = 'serial_number'
            kwargs.uri    = 'network/Elements'
            kwargs        = isight.api(kwargs.qtype).calls(kwargs)
            pmoids        = kwargs.pmoids

            for k, v in pmoids.items(): reg_device = v.registered_device
            kwargs.api_filter= f"RegisteredDevice.Moid eq '{reg_device}'"
            kwargs.uri       = 'equipment/Chasses'
            kwargs           = isight.api(kwargs.qtype).calls(kwargs)
            chassis_pmoids   = kwargs.pmoids
            platform_types   = "('IMCBlade', 'IMCM5', 'IMCM6', 'IMCM7', 'IMCM8', 'IMCM9')"
            kwargs.api_filter= f"ParentConnection.Moid eq '{reg_device}' and PlatformType in {platform_types}"
            kwargs.uri       = 'asset/DeviceRegistrations'
            kwargs           = isight.api(kwargs.qtype).calls(kwargs)
            server_pmoids    = kwargs.pmoids
            #=====================================================
            # Build Chassis Dictionary
            #=====================================================
            models = []
            for k, v in chassis_pmoids.items(): models.append(str(v.model).lower())
            models = numpy.unique(numpy.array(models))
            for model in models: kwargs.chassis[model] = []
            for k, v in chassis_pmoids.items():
                model = str(v.model).lower()
                kwargs.chassis[model].append(DotMap(
                    domain  = kwargs.domain.name,
                    identity= v.id,
                    serial  = k
                ))

            #=====================================================
            # Build Server Dictionaries - Domain
            #=====================================================
            kwargs.names = []
            for k, v in server_pmoids.items(): kwargs.names.append(k)
            kwargs.method='get'
            kwargs.uri   = 'compute/PhysicalSummaries'
            kwargs       = isight.api(kwargs.qtype).calls(kwargs)
            prCyan('')
            for i in kwargs.results:
                prCyan(f'   - Pulling Server Inventory for the Server: {i.Serial}')
                kwargs = server_dictionary(i, kwargs)
                prCyan(f'     Completed Server Inventory for Server: {i.Serial}')
            prCyan('')

        else:
            #=====================================================
            # Build Server Dictionaries - Standalone
            #=====================================================
            kwargs.sensitive_var = 'local_user_password'
            kwargs  = ezfunctions.sensitive_var_value(kwargs)
            password=kwargs.var_value
            kwargs.yaml.device_list = [DotMap(
                device_type   = 'imc',
                devices       = kwargs.imm.cimc,
                password      = password,
                resource_group=kwargs.org,
                username      = kwargs.imm.username
            )]
            kwargs = claim_device.claim_targets(kwargs)
            serial_numbers = []
            for k,v in kwargs.result.items(): serial_numbers.append(v.serial)
            kwargs.method= 'get'
            kwargs.names = serial_numbers
            kwargs.qtype = 'serial_number'
            kwargs.uri   = 'compute/PhysicalSummaries'
            kwargs = isight.api(kwargs.qtype).calls(kwargs)
            prCyan('')
            for i in kwargs.results:
                prCyan(f'   - Pulling Server Inventory for the Server: {i.Serial}')
                kwargs = server_dictionary(i, kwargs)
                prCyan(f'     Completed Server Inventory for Server: {i.Serial}')
            prCyan('')

        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs

    #=============================================================================
    # Function - Build Profiles - Domain
    #=============================================================================
    def domain(self, kwargs):
        # Build Dictionary
        polVars = dict(
            action                     = 'Deploy',
            description                = f'{kwargs.domain.name} Domain Profile',
            name                       = kwargs.domain.name,
            network_connectivity_policy= f'{kwargs.imm.policies.prefix}dns',
            ntp_policy                 = f'{kwargs.imm.policies.prefix}ntp',
            port_policies              = [f'{kwargs.domain.name}-A', f'{kwargs.domain.name}-B'],
            serial_numbers             = kwargs.domain.serial_numbers,
            snmp_policy                = f'{kwargs.imm.policies.prefix}snmp',
            switch_control_policy      = f'{kwargs.imm.policies.prefix}sw-ctrl',
            syslog_policy              = f'{kwargs.imm.policies.prefix}syslog',
            system_qos_policy          = f'{kwargs.imm.policies.prefix}qos',
            vlan_policies              = [f'{kwargs.imm.policies.prefix}vlans'],
        )
        if kwargs.domain.get('vsans'):
            polVars['vsan_policies'] = []
            for i in kwargs.domain.vsans:
                polVars['vsan_policies'].append(f'{kwargs.imm.policies.prefix}vsan-{i}')
        # Add Policy Variables to imm_dict
        kwargs.class_path = f'profiles,{self.type}'
        kwargs = ezfunctions.ez_append(polVars, kwargs)
        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs

    #=============================================================================
    # Function - Build Policy - Ethernet Adapter
    #=============================================================================
    def ethernet_adapter(self, kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        plist = ['16RxQs-4G', '16RxQs-5G']
        for item in kwargs.virtualization:
            if item.type == 'vmware': plist.extend(['VMware', 'VMware-High-Trf'])
        for i in plist:
            polVars = dict(
                adapter_template = i,
                description      = f'{kwargs.imm.policies.prefix}{i} {descr} Policy',
                name             = f'{kwargs.imm.policies.prefix}{i}',
            )

            # Add Policy Variables to imm_dict
            kwargs.class_path = f'policies,{self.type}'
            kwargs = ezfunctions.ez_append(polVars, kwargs)
        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs

    #=============================================================================
    # Function - Build Policy - Ethernet Network Control
    #=============================================================================
    def ethernet_network_control(self, kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        name = kwargs.domain.discovery_protocol
        if 'cdp' in name: cdpe = True
        else: cdpe = False
        if 'lldp' in name: lldpe = True
        else: lldpe = False
        polVars = dict(
            cdp_enable           = cdpe,
            description          = f'{kwargs.imm.policies.prefix}{name} {descr} Policy',
            name                 = f'{kwargs.imm.policies.prefix}{name}',
            lldp_enable_receive  = lldpe,
            lldp_enable_transmit = lldpe,
            mac_register_mode    = 'nativeVlanOnly',
            mac_security_forge   = 'allow',
        )

        # Add Policy Variables to imm_dict
        kwargs.class_path = f'policies,{self.type}'
        kwargs = ezfunctions.ez_append(polVars, kwargs)
        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs

    #=============================================================================
    # Function - Build Policy - Ethernet Network Group
    #=============================================================================
    def ethernet_network_group(self, kwargs):
        kwargs.descr = (self.type.replace('_', ' ')).title()
        #=====================================================
        # Assign Configuration to Policy
        #=====================================================
        def create_eth_groups(kwargs):
            polVars = dict(
                allowed_vlans = kwargs.allowed,
                description   = f'{kwargs.imm.policies.prefix}{kwargs.name} {kwargs.descr} Policy',
                name          = f'{kwargs.imm.policies.prefix}{kwargs.name}',
                native_vlan   = kwargs.native,
            )
            # Add Policy Variables to imm_dict
            kwargs.class_path = f'policies,{self.type}'
            kwargs = ezfunctions.ez_append(polVars, kwargs)
            return kwargs

        #=====================================================
        # Add All VLANs for Guest vSwitch
        #=====================================================
        vlans = []
        for i in kwargs.vlans: vlans.append(i.vlan_id)
        for i in kwargs.ranges:
            vrange = ezfunctions.vlan_list_full(i.vlan_list); vlans.extend(vrange)
        vlans = list(numpy.unique(numpy.array(vlans))); vlans.sort()
        kwargs.vlan.all_vlans = ezfunctions.vlan_list_format(vlans)

        kwargs.disjoint= False
        kwargs.iscsi = 0;  kwargs.iscsi_vlans= []; kwargs.nvme = 0; kwargs.nvme_vlans = []
        for i in kwargs.vlans:
            if i.disjoint == True: kwargs.disjoint = True
            if i.vlan_type == 'iscsi': kwargs.iscsi+=1; kwargs.iscsi_vlans.append(i.vlan_id)
            elif i.vlan_type == 'nvme': kwargs.nvme+=1; kwargs.nvme_vlans.append(i.vlan_id)

        #=====================================================
        # Create Uplink Groups if Disjoint is Present
        #=====================================================
        if kwargs.disjoint == True:
            disjoint_vlans = []
            disjoint_native= 1
            native         = 1
            for i in kwargs.vlans:
                if i.disjoint == True:
                    disjoint_vlans.append(i.vlan_id)
                    if i.native_vlan == True: disjoint_native = i.vlan_id
                elif i.native_vlan == True: native = i.vlan_id

            for i in kwargs.ranges:
                if i.disjoint == True: disjoint_vlans.extend(ezfunctions.vlan_list_full(i.vlan_list))
            disjoint_vlans = list(numpy.unique(numpy.array(disjoint_vlans)))
            disjoint_vlans.sort()
            uplink1 = vlans
            for i in disjoint_vlans: uplink1.remove(i)
            kwargs.uplink1= ezfunctions.vlan_list_format(uplink1)
            kwargs.uplink2= ezfunctions.vlan_list_format(disjoint_vlans)
            kwargs.name   = 'uplink1'
            kwargs.allowed= kwargs.uplink1
            kwargs.native = native
            kwargs = create_eth_groups(kwargs)
            kwargs.name   = 'uplink2'
            kwargs.allowed= kwargs.uplink2
            kwargs.native = disjoint_native
            kwargs = create_eth_groups(kwargs)

        #=====================================================
        # Create Eth NetworkGroups for Virtual Switches
        #=====================================================
        for item in kwargs.virtualization:
            for i in item.virtual_switches:
                if re.search('vswitch0', i.name, re.IGNORECASE):
                    kwargs.name = i.alternate_name
                else: kwargs.name = i.name
                kwargs.native= 1
                if 'guests' in i.data_types:
                    kwargs.name = 'all_vlans'
                    kwargs.allowed= kwargs.vlan.all_vlans
                    if 'management' in i.data_types:
                        kwargs.native= kwargs.inband.vlan_id
                        kwargs       = create_eth_groups(kwargs)
                    elif 'storage' in i.data_types:
                        if kwargs.iscsi == 2:
                            for x in range(0,2):
                                if re.search('[A-Z]', i.name): suffix = chr(ord('@')+x+1)
                                else: suffix = chr(ord('@')+x+1).lower()
                                kwargs.name  = f"{i.name}-{suffix}"
                                kwargs.native= kwargs.iscsi_vlans[x]
                                kwargs       = create_eth_groups(kwargs)
                        elif 'migration' in i.data_types:
                            kwargs.native= kwargs.migration.vlan_id
                            kwargs       = create_eth_groups(kwargs)
                        else: kwargs = create_eth_groups(kwargs)
                    elif 'migration' in i.data_types:
                            kwargs.native= kwargs.migration.vlan_id
                            kwargs       = create_eth_groups(kwargs)
                    else: kwargs = create_eth_groups(kwargs)
                elif 'management' in i.data_types:
                    kwargs.native= kwargs.inband.vlan_id
                    mvlans       = [kwargs.inband.vlan_id]
                    if 'migration' in i.data_types: mvlans.append(kwargs.migration.vlan_id)
                    if 'storage' in i.data_types:
                        for v in kwargs.vlans:
                            if re.search('(iscsi|nfs|nvme)', v.vlan_type): mvlans.append(v.vlan_id)
                    mvlans.sort()
                    kwargs.allowed= ezfunctions.vlan_list_format(mvlans)
                    kwargs        = create_eth_groups(kwargs)
                elif 'migration' in i.data_types:
                    kwargs.native= kwargs.migration.vlan_id
                    mvlans       = [kwargs.migration.vlan_id]
                    if 'storage' in i.data_types:
                        for v in kwargs.vlans:
                            if re.search('(iscsi|nfs|nvme)', v.vlan_type): mvlans.append(v.vlan_id)
                    mvlans.sort()
                    kwargs.allowed= ezfunctions.vlan_list_format(mvlans)
                    kwargs        = create_eth_groups(kwargs)
                elif 'storage' in i.data_types:
                    if kwargs.iscsi == 2:
                        for x in range(0,2):
                            if re.search('[A-Z]', i.name): suffix = chr(ord('@')+x+1)
                            else: suffix = chr(ord('@')+x+1).lower()
                            kwargs.native= kwargs.iscsi_vlans[x]
                            kwargs.name  = f"{i.name}-{suffix}"
                            svlans       = [kwargs.iscsi_vlans[x]]
                            for v in kwargs.vlans:
                                if re.search('(nfs|nvme)', v.vlan_type): svlans.append(v.vlan_id)
                            kwargs.allowed= ezfunctions.vlan_list_format(svlans)
                            kwargs        = create_eth_groups(kwargs)
                    else:
                        mvlans       = [kwargs.migration.vlan_id]
                        for v in kwargs.vlans:
                            if re.search('(iscsi|nfs|nvme)', v.vlan_type): mvlans.append(v.vlan_id)
                        mvlans.sort()
                        kwargs.allowed= ezfunctions.vlan_list_format(mvlans)
                        kwargs        = create_eth_groups(kwargs)
        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs

    #=============================================================================
    # Function - Build Policy - Ethernet QoS
    #=============================================================================
    def ethernet_qos(self, kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        plist = ['Best Effort']
        if kwargs.domain.cfg_qos_priorities == True:
            plist = plist.extend(['Bronze', 'Gold', 'Platinum', 'Silver'])
        for i in plist:
            name = i.replace(' ', '-')
            polVars = dict(
                enable_trust_host_cos= False,
                burst        = 10240,
                description  = f'{kwargs.imm.policies.prefix}{name} {descr} Policy',
                name         = f'{kwargs.imm.policies.prefix}{name}',
                mtu          = 9000,
                priority     = i,
                rate_limit   = 0,
            )
            # Add Policy Variables to imm_dict
            kwargs.class_path = f'policies,{self.type}'
            kwargs = ezfunctions.ez_append(polVars, kwargs)
        
        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs

    #=============================================================================
    # Function - Build Policy - FC Zone
    #=============================================================================
    def fc_zone(self, kwargs):
        descr = (self.type.replace('_', ' ')).title()
        fabrics = ['a', 'b']
        kwargs.fc_zone = []
        for x in range(0,len(fabrics)):
            if len(kwargs.domain.vsans) == 2: vsan = kwargs.domain.vsans[x]
            else: vsan = kwargs.domain.vsans[0]
            name = f'{kwargs.imm.policies.prefix}fabric-{fabrics[x]}-vsan-{vsan}'
            # Build Dictionary
            polVars = dict(
                description           = f'{name} {descr} Policy',
                fc_target_zoning_type = 'SIMT',
                name                  = name,
                targets               = [],
            )
            kwargs.storage = kwargs.imm_dict.orgs[kwargs.org].storage
            for k, v in kwargs.storage.items():
                for e in v:
                    for i in e.wwpns[fabrics[x]]:
                        polVars['targets'].append(dict(
                            name      = e.svm + '-' + i.interface,
                            switch_id = (fabrics[x]).upper(),
                            vsan_id   = vsan,
                            wwpn      = i.wwpn
                        ))
                    kwargs.fc_zone.append(polVars['name'])

            # Add Policy Variables to imm_dict
            kwargs.class_path = f'policies,{self.type}'
            kwargs = ezfunctions.ez_append(polVars, kwargs)
        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs

    #=============================================================================
    # Function - Build Policy - Fibre-Channel Adapter
    #=============================================================================
    def fibre_channel_adapter(self, kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        plist = ['VMware', 'FCNVMeInitiator']
        for i in plist:
            polVars = dict(
                adapter_template = i,
                description      = f'{kwargs.imm.policies.prefix}{i} {descr} Policy',
                name             = f'{kwargs.imm.policies.prefix}{i}',
            )

            # Add Policy Variables to imm_dict
            kwargs.class_path = f'policies,{self.type}'
            kwargs = ezfunctions.ez_append(polVars, kwargs)
        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs

    #=============================================================================
    # Function - Build Policy - Fibre-Channel Network
    #=============================================================================
    def fibre_channel_network(self, kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        for i in kwargs.domain.vsans:
            polVars = dict(
                description = f'{kwargs.imm.policies.prefix}vsan-{i} {descr} Policy',
                name        = f'{kwargs.imm.policies.prefix}vsan-{i}',
                vsan_id     = i,
            )

            # Add Policy Variables to imm_dict
            kwargs.class_path = f'policies,{self.type}'
            kwargs = ezfunctions.ez_append(polVars, kwargs)
        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs

    #=============================================================================
    # Function - Build Policy - Fibre-Channel QoS
    #=============================================================================
    def fibre_channel_qos(self, kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        plist = ['fc-qos']
        for i in plist:
            polVars = dict(
                max_data_field_size = 2112,
                burst               = 10240,
                description         = f'{kwargs.imm.policies.prefix}{i} {descr} Policy',
                name                = f'{kwargs.imm.policies.prefix}{i}',
                rate_limit          = 0,
            )

            # Add Policy Variables to imm_dict
            kwargs.class_path = f'policies,{self.type}'
            kwargs = ezfunctions.ez_append(polVars, kwargs)
        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs

    #=============================================================================
    # Function - Build Policies - Firmware
    #=============================================================================
    def firmware(self, kwargs):
        # Build Dictionary
        descr   = (self.type.replace('_', ' ')).capitalize()
        dataset = []
        #fw_name = (fw.replace(')', '')).replace('(', '-')
        fw_name = kwargs.domain.name
        kwargs.firmware_policy_name = fw_name
        for k, v in kwargs.servers.items():
            m = re.search('(M[5-9][A-Z]?[A-Z]?)', v.model).group(1)
            g = re.search('(M[5-9])', v.model).group(1)
            v.model = v.model.replace(m, g)
            dataset.append(v.model)
        models = numpy.unique(numpy.array(dataset))
        polVars = dict(
            description = f'{kwargs.imm.policies.prefix}{fw_name} {descr} Policy', model_bundle_version = [],
            name = f'{kwargs.imm.policies.prefix}{fw_name}', target_platform = 'FIAttached'
        )
        stypes = ['blades', 'rackmount']
        for s in stypes: polVars['model_bundle_version'].append(
            dict(firmware_version= kwargs.domain.firmware[s], server_models = []))
        for i in models:
            if 'UCSC' in i: polVars['model_bundle_version'][1]['server_models'].append(i)
            else: polVars['model_bundle_version'][0]['server_models'].append(i)

        # Add Policy Variables to imm_dict
        kwargs.class_path = f'policies,{self.type}'
        kwargs = ezfunctions.ez_append(polVars, kwargs)

        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs

    #=============================================================================
    # Function - Build Policy - Flow Control
    #=============================================================================
    def flow_control(self, kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        polVars = dict(
            description = f'{kwargs.imm.policies.prefix}flow-ctrl {descr} Policy',
            name        = f'{kwargs.imm.policies.prefix}flow-ctrl',
        )

        # Add Policy Variables to imm_dict
        kwargs.class_path = f'policies,{self.type}'
        kwargs = ezfunctions.ez_append(polVars, kwargs)
        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs

    #=============================================================================
    # Function - Build Policy - IMC Access
    #=============================================================================
    def imc_access(self, kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        polVars = dict(
            description         = f'{kwargs.imm.policies.prefix}kvm {descr} Policy',
            inband_ip_pool      = f'kvm-inband',
            inband_vlan_id      = kwargs.inband.vlan_id,
            out_of_band_ip_pool = 'kvm-ooband',
            name                = f'{kwargs.imm.policies.prefix}kvm',
        )

        # Add Policy Variables to imm_dict
        kwargs.class_path = f'policies,{self.type}'
        kwargs = ezfunctions.ez_append(polVars, kwargs)
        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs

    #=============================================================================
    # Function - Build Pools - IP
    #=============================================================================
    def ip(self, kwargs):
        pdns = kwargs.dns_servers[0]
        sdns = ''
        if len(kwargs.dns_servers) >= 2: sdns = kwargs.dns_servers[1]
        # Build Dictionary
        for i in kwargs.vlans:
            if re.search('(inband|iscsi|ooband)', i.vlan_type):
                if not kwargs.pools.ip.get(i.vlan_type):
                    kwargs.pools.ip[i.vlan_type] = []
                if re.search('inband|ooband', i.vlan_type):
                    name = f'{kwargs.imm.policies.prefix}kvm-{i.vlan_type}'
                    pool_from = i.pool[0]
                    pool_to   = i.pool[-1]
                else:
                    name = f'{kwargs.imm.policies.prefix}iscsi-vlan{i.vlan_id}'
                    pool_from = i.server[0]
                    pool_to   = i.server[-1]
                kwargs['defaultGateway'] = i.gateway
                kwargs['subnetMask']     = i.netmask
                kwargs['ip_version']     = 'v4'
                kwargs['pool_from']      = pool_from
                kwargs['pool_to']        = pool_to
                validating.error_subnet_check(kwargs)
                size = int(ipaddress.IPv4Address(pool_to)) - int(ipaddress.IPv4Address(pool_from)) + 1
                polVars = dict(
                    assignment_order = 'sequential',
                    description      = f'{name} IP Pool',
                    name             = f'{name}',
                    ipv4_blocks      = [{
                        'from':pool_from,
                        'size':size
                    }],
                    ipv4_configuration = dict(
                        gateway       = i.gateway,
                        netmask       = i.netmask,
                        primary_dns   = pdns,
                        secondary_dns = sdns
                    ),
                )
                kwargs.pools.ip[i.vlan_type].append(polVars['name'])
                # Add Policy Variables to imm_dict
                kwargs.class_path = f'pools,{self.type}'
                kwargs = ezfunctions.ez_append(polVars, kwargs)
        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs

    #=============================================================================
    # Function - Build Pools - IQN
    #=============================================================================
    def iqn(self, kwargs):
        # Build Dictionary
        polVars = dict(
            assignment_order = 'sequential',
            description      = f'{kwargs.imm.policies.prefix}iscsi IQN Pool',
            name             = f'{kwargs.imm.policies.prefix}iscsi',
            prefix           = f'iqn.1984-12.com.cisco',
            iqn_blocks       = [{
                'from': 0,
                'size': 1024,
                'suffix': 'ucs-host'
            }],
        )

        # Add Policy Variables to imm_dict
        kwargs.class_path = f'pools,{self.type}'
        kwargs = ezfunctions.ez_append(polVars, kwargs)
        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs

    #=============================================================================
    # Function - Build Policy - IPMI over LAN
    #=============================================================================
    def ipmi_over_lan(self, kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        polVars = dict(
            description = f'{kwargs.imm.policies.prefix}ipmi {descr} Policy',
            name        = f'{kwargs.imm.policies.prefix}ipmi',
            privilege   = 'read-only'
        )

        # Add Policy Variables to imm_dict
        kwargs.class_path = f'policies,{self.type}'
        kwargs = ezfunctions.ez_append(polVars, kwargs)
        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs

    #=============================================================================
    # Function - Build Policy - iSCSI Adapter
    #=============================================================================
    def iscsi_adapter(self, kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        polVars = dict(
            description            = f'{kwargs.imm.policies.prefix}iadapter {descr} Policy',
            dhcp_timeout           = 60,
            name                   = f'{kwargs.imm.policies.prefix}iadapter',
            lun_busy_retry_count   = 15,
            tcp_connection_timeout = 15,
        )

        # Add Policy Variables to imm_dict
        kwargs.class_path = f'policies,{self.type}'
        kwargs = ezfunctions.ez_append(polVars, kwargs)
        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs

    #=============================================================================
    # Function - Build Policy - iSCSI Boot
    #=============================================================================
    def iscsi_boot(self, kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        fabrics = ['a', 'b']
        list_of_list = []
        for i in range(0, len(kwargs.iscsi.targets), 2): list_of_list.append(kwargs.iscsi.targets[i:i+2])
        #half = kwargs.iscsi.targets // 2
        kwargs.a.targets  = list_of_list[0]
        kwargs.b.targets  = list_of_list[1]
        kwargs.iscsi.boot = []
        for x in range(0,len(fabrics)):
            pool = kwargs.pools.ip.iscsi[x]
            polVars = dict(
                description             = f'{kwargs.imm.policies.prefix}{pool} {descr} Policy',
                initiator_ip_source     = 'Pool',
                initiator_ip_pool       = kwargs.pools.ip.iscsi[x], 
                iscsi_adapter_policy    = f'{kwargs.imm.policies.prefix}iadapter',
                name                    = f'{kwargs.imm.policies.prefix}{pool}',
                primary_target_policy   = kwargs[fabrics[x]].targets[0],
                secondary_target_policy = kwargs[fabrics[x]].targets[1],
                target_source_type      = f'Static',
            )
            kwargs.iscsi.boot.append(polVars['name'])

            # Add Policy Variables to imm_dict
            kwargs.class_path = f'policies,{self.type}'
            kwargs = ezfunctions.ez_append(polVars, kwargs)
        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs

    #=============================================================================
    # Function - Build Policy - iSCSI Target
    #=============================================================================
    def iscsi_static_target(self, kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        kwargs.iscsi.targets = []
        for k, v in kwargs.imm_dict.orgs[kwargs.org].storage.items():
            for e in v:
                for i in e.iscsi.interfaces:
                    name = e.svm + ':' + i.interface
                    polVars = dict(
                        description = f'{name} {descr} Policy',
                        ip_address  = i.ip_address,
                        lun_id      = 0,
                        name        = f'{name}',
                        port        = 3260,
                        target_name = v[0].iscsi.iqn,
                    )
                    kwargs.iscsi.targets.append(name)
                    
                    # Add Policy Variables to imm_dict
                    kwargs.class_path = f'policies,{self.type}'
                    kwargs = ezfunctions.ez_append(polVars, kwargs)
       
        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs

    #=============================================================================
    # Function - Build Policy - LAN Connectivity
    #=============================================================================
    def lan_connectivity(self, kwargs):
        # Build Dictionary
        descr= (self.type.replace('_', ' ')).title()
        vics = []
        for k, v in kwargs.servers.items():
            if len(v.vics) == 2: vics = f'{v.vics[0].vic_gen}:{v.vics[0].vic_slot}-{v.vics[1].vic_slot}'
            else: vics = f'{v.vics[0].vic_gen}:{v.vics[0].vic_slot}'

        kwargs.vic_details= list(numpy.unique(numpy.array(vics)))
        lan_policies = ['lcp']
        iscsi_vlan = False
        for i in kwargs.vlans:
            if i.vlan_type == 'iscsi': iscsi_vlan = True
        if iscsi_vlan == True: lan_policies.append('lcp-iscsi')

        for g in kwargs.vic_details:
            for lcp in lan_policies:
                ga       = g.split(':')
                gen      = ga[0]
                name     = (f'{lcp}-vic-{g}').lower()
                pci_order= kwargs.pci_order
                slots    = (ga[1]).split('-')
                polVars  = dict(
                    description          = f'{kwargs.imm.policies.prefix}{name} {descr} Policy',
                    iqn_pool             = '',
                    name                 = f'{kwargs.imm.policies.prefix}{name}',
                    target_platform      = 'FIAttached',
                    vnics                = [],
                )
                if re.search('iscsi', lcp):
                    polVars['iqn_pool'] = f'{kwargs.imm.policies.prefix}iscsi'
                else: polVars.pop('iqn_pool')
                iscsi = 0
                for v in kwargs.vlans:
                    if 'iscsi' in v.vlan_type: iscsi+=1
                vnic_count = 0
                for e in kwargs.virtualization:
                    for i in e.virtual_switches:
                        if re.search('vswitch0', i.name, re.IGNORECASE):
                            name = i.alternate_name
                        else: name = i.name
                        if re.search('[A-Z]', name): a = 'A'; b = 'B'
                        else: a = 'a'; b = 'b'
                        if 'guests' in i.data_types:
                            if iscsi==2 and 'storage' in i.data_types: network_groups = [
                                    f'{kwargs.imm.policies.prefix}{name}-{a}',
                                    f'{kwargs.imm.policies.prefix}{name}-{b}']
                            else: network_groups = [f'{kwargs.imm.policies.prefix}all_vlans']
                        elif 'storage' in i.data_types:
                            if iscsi==2: network_groups = [
                                    f'{kwargs.imm.policies.prefix}{name}-{a}',
                                    f'{kwargs.imm.policies.prefix}{name}-{b}']
                            else: network_groups = [f'{kwargs.imm.policies.prefix}{name}']
                        else: network_groups = [name]
                        if   'storage' in i.data_types:
                            if gen == 'gen5': adapter_policy= '16RxQs-5G'
                            else: adapter_policy= '16RxQs-4G'
                            adapter_policy= '16RxQs-4G'
                            if kwargs.domain.cfg_qos_priorities == True: qos_policy = 'Platinum'
                            else: qos_policy = 'Best-Effort'
                        elif 'guests' in i.data_types:
                            if e.type == 'vmware': adapter_policy= 'VMware-High-Trf'
                            if kwargs.domain.cfg_qos_priorities == True: qos_policy = 'Gold'
                            else: qos_policy = 'Best-Effort'
                        elif 'migration' in i.data_types:
                            if e.type == 'vmware': adapter_policy= 'VMware-High-Trf'
                            if kwargs.domain.cfg_qos_priorities == True: qos_policy = 'Bronze'
                            else: qos_policy = 'Best-Effort'
                        else:
                            if e.type == 'vmware': adapter_policy = 'VMware'
                            if kwargs.domain.cfg_qos_priorities == True: qos_policy = 'Silver'
                            else: qos_policy = 'Best-Effort'
                        qos_policy = 'Best-Effort'
                        if len(slots) == 1: placement_order = pci_order, pci_order + 1,
                        else: placement_order = pci_order, pci_order
                        polVars['vnics'].append(dict(
                            ethernet_adapter_policy        = adapter_policy,
                            ethernet_network_control_policy= kwargs.domain.discovery_protocol,
                            ethernet_network_group_policies= network_groups,
                            ethernet_qos_policy            = qos_policy,
                            iscsi_boot_policies            = [],
                            names                          = [f'{name}-{a}', f'{name}-{b}'],
                            mac_address_pools              = [f'{name}-{a}', f'{name}-{b}'],
                            placement = dict(
                                pci_order = placement_order,
                                slot_ids  = slots
                            )
                        ))
                        if 'storage' in i.data_type and 'iscsi' in lcp:
                            polVars['vnics'][vnic_count].update({'iscsi_boot_policies': kwargs.iscsi.boot})
                        else: polVars['vnics'][vnic_count].pop('iscsi_boot_policies')
                        if len(slots) == 1: pci_order += 2
                        else: pci_order += 1
                        vnic_count += 1
                
                # Add Policy Variables to imm_dict
                kwargs.class_path = f'policies,{self.type}'
                kwargs = ezfunctions.ez_append(polVars, kwargs)

        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        kwargs.pci_order = pci_order
        return kwargs

    #=============================================================================
    # Function - Build Policy - Link Aggregation
    #=============================================================================
    def link_aggregation(self, kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        polVars = dict(
            description = f'{kwargs.imm.policies.prefix}link-agg {descr} Policy',
            name        = f'{kwargs.imm.policies.prefix}link-agg',
        )

        # Add Policy Variables to imm_dict
        kwargs.class_path = f'policies,{self.type}'
        kwargs = ezfunctions.ez_append(polVars, kwargs)
        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs

    #=============================================================================
    # Function - Build Policy - Link Control
    #=============================================================================
    def link_control(self, kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        polVars = dict(
            description = f'{kwargs.imm.policies.prefix}link-ctrl {descr} Policy',
            name        = f'{kwargs.imm.policies.prefix}link-ctrl',
        )

        # Add Policy Variables to imm_dict
        kwargs.class_path = f'policies,{self.type}'
        kwargs = ezfunctions.ez_append(polVars, kwargs)
        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs

    #=============================================================================
    # Function - Build Policy - Local User
    #=============================================================================
    def local_user(self, kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        polVars = dict(
            description = f'{kwargs.imm.policies.prefix}users {descr} Policy',
            name        = f'{kwargs.imm.policies.prefix}users',
            users       = [dict(
                enabled  = True,
                password = 1,
                role     = 'admin',
                username = kwargs.domain.policies.local_user
            )]
        )

        # Add Policy Variables to imm_dict
        kwargs.class_path = f'policies,{self.type}'
        kwargs = ezfunctions.ez_append(polVars, kwargs)
        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs

    #=============================================================================
    # Function - Build Pools - MAC
    #=============================================================================
    def mac(self, kwargs):
        # Build Dictionary
        mcount = 1
        for e in kwargs.virtualization:
            for i in e.virtual_switches:
                for x in range(0,2):
                    if re.search('vswitch0', i.name, re.IGNORECASE):
                        name = i.alternate_name
                    else: name = i.name
                    if re.search('[A-Z]', name): pool= name + '-' + chr(ord('@')+x+1)
                    else: pool= name + '-' + chr(ord('@')+x+1).lower()
                    pid = mcount + x
                    if pid > 8: pid=chr(ord('@')+pid-8)
                    polVars = dict(
                        assignment_order = 'sequential',
                        description      = f'{kwargs.imm.policies.prefix}{pool} Pool',
                        name             = f'{kwargs.imm.policies.prefix}{pool}',
                        mac_blocks       = [{
                            'from':f'00:25:B5:{kwargs.domain.pools.prefix}:{pid}0:00',
                            'size':1024
                        }],
                    )

                    # Add Policy Variables to imm_dict
                    kwargs.class_path = f'pools,{self.type}'
                    kwargs = ezfunctions.ez_append(polVars, kwargs)
                # Increment MAC Count
                mcount = mcount + 2

        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs

    #=============================================================================
    # Function - Build Policy - Multicast
    #=============================================================================
    def multicast(self, kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        polVars = dict(
            description = f'{kwargs.imm.policies.prefix}mcast {descr} Policy',
            name        = f'{kwargs.imm.policies.prefix}mcast',
        )

        # Add Policy Variables to imm_dict
        kwargs.class_path = f'policies,{self.type}'
        kwargs = ezfunctions.ez_append(polVars, kwargs)
        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs

    #=============================================================================
    # Function - Build Policy - Network Connectivity
    #=============================================================================
    def network_connectivity(self, kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        if kwargs.args.deployment_type == 'azure_hci':
            polVars = dict(
                description              = f'{kwargs.imm.policies.prefix}dns {descr} Policy',
                dns_servers_v4           = [],
                enable_dynamic_dns       = True,
                enable_ipv6              = True,
                name                     = f'{kwargs.imm.policies.prefix}dns',
                obtain_ipv4_dns_from_dhcp= True,
                obtain_ipv6_dns_from_dhcp= True,
            )
        else:
            polVars = dict(
                description    = f'{kwargs.imm.policies.prefix}dns {descr} Policy',
                dns_servers_v4 = kwargs.dns_servers,
                name           = f'{kwargs.imm.policies.prefix}dns',
            )

        # Add Policy Variables to imm_dict
        kwargs.class_path = f'policies,network_connectivity'
        kwargs = ezfunctions.ez_append(polVars, kwargs)
        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs

    #=============================================================================
    # Function - Build Policy - NTP
    #=============================================================================
    def ntp(self, kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        polVars = dict(
            description = f'{kwargs.imm.policies.prefix}ntp {descr} Policy',
            name        = f'{kwargs.imm.policies.prefix}ntp',
            ntp_servers = kwargs.ntp_servers,
            timezone    = kwargs.timezone,
        )

        # Add Policy Variables to imm_dict
        kwargs.class_path = f'policies,ntp'
        kwargs = ezfunctions.ez_append(polVars, kwargs)
        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs

    #=============================================================================
    # Function - Build Policy - Port
    #=============================================================================
    def port(self, kwargs):
        def ethernet_pc_uplinks(kwargs):
            idict = dict(
                admin_speed                  = 'Auto',
                ethernet_network_group_policy= f'{kwargs.imm.policies.prefix}{kwargs.vlan_group}',
                flow_control_policy          = f'{kwargs.imm.policies.prefix}flow-ctrl',
                interfaces                   = kwargs.ports,
                link_aggregation_policy      = f'{kwargs.imm.policies.prefix}link-agg',
                link_control_policy          = f'{kwargs.imm.policies.prefix}link-ctrl',
                pc_ids                       = [kwargs.pc_id, kwargs.pc_id],
            )
            return idict

        eth_breakout_ports = []
        #=====================================================
        # Base Dictionary
        #=====================================================
        descr = (self.type.replace('_', ' ')).title()
        polVars = dict(
            description  = f'{kwargs.domain.name} {descr} Policy',
            device_model = kwargs.domain.device_model,
            names        = [f'{kwargs.domain.name}-A', f'{kwargs.domain.name}-B'],
            port_channel_ethernet_uplinks = []
        )

        #=====================================================
        # Uplink Port-Channels
        #=====================================================
        x = str(kwargs.domain.eth_uplinks[0]).split('/')
        if len(x) == 3: eth_breakout_ports.extend(kwargs.domain.eth_uplinks)
        if kwargs.disjoint == True:
            # First Uplink
            plength = len(kwargs.domain.eth_uplinks) // 2
            kwargs.ports = []
            for i in kwargs.domain.eth_uplinks[:plength]:
                kwargs.ports.append({'port_id':int(i.split('/')[-1])})
            if len(x) == 3: pc_id = '1' + x[1] + x[2]
            else: pc_id = x[-1]
            kwargs.pc_id     = int(pc_id)
            kwargs.vlan_group= 'uplink1'
            polVars['port_channel_ethernet_uplinks'].append(ethernet_pc_uplinks(kwargs))

            # Second Uplink
            kwargs.ports = []
            for i in kwargs.domain.eth_uplinks[plength:]:
                kwargs.ports.append({'port_id':int(i.split('/')[-1])})
            x = str(kwargs.domain.eth_uplinks[plength:][0]).split('/')
            if len(x) == 3: pc_id = '1' + x[1] + x[2]
            else: pc_id = x[-1]
            kwargs.pc_id     = int(pc_id)
            kwargs.vlan_group= 'uplink2'
            polVars['port_channel_ethernet_uplinks'].append(ethernet_pc_uplinks(kwargs))
        else:
            kwargs.ports = []
            for i in kwargs.domain.eth_uplinks:
                kwargs.ports.append({'port_id':int(i.split('/')[-1])})
            if len(x) == 3: pc_id = '1' + x[1] + x[2]
            else: pc_id = x[-1]
            kwargs.pc_id     = int(pc_id)
            kwargs.vlan_group= 'all_vlans'
            polVars['port_channel_ethernet_uplinks'].append(ethernet_pc_uplinks(kwargs))

        #=====================================================
        # Fibre-Channel Uplinks/Port-Channels
        #=====================================================
        if kwargs.domain.get('vsans'):
            ports= []
            x    = kwargs.domain.fcp_uplink_ports[0].split('/')
            if kwargs.swmode == 'end-host':
                if len(x) == 3: pc_id = '1' + x[1] + x[2]
                else: pc_id = x[-1]
                polVars.update(dict(
                    port_channel_fc_uplinks = [dict(
                        admin_speed  = kwargs.domain.fcp_uplink_speed,
                        fill_pattern = 'Idle',
                        interfaces   = [],
                        pc_ids       = [pc_id, pc_id],
                        vsan_ids     = kwargs.domain.vsans
                    )]
                ))
                for i in kwargs.domain.fcp_uplink_ports:
                    idict = {}
                    if len(x) == 3: idict.append({'breakout_port_id':int(i.split('/')[-2])})
                    idict.append({'port_id':int(i.split('/')[-1])})
                    polVars['port_channel_fc_uplinks']['interfaces'].append(idict)
            else:
                polVars['port_role_fc_storage'] = []
                if x == 3:
                    breakout = []
                    for i in kwargs.domain.fcp_uplink_ports:
                        breakout.append(int(i.split('/')[-2]))
                    breakout = numpy.unique(numpy.array(breakout))
                    for item in breakout:
                        port_list = []
                        for i in kwargs.domain.fcp_uplink_ports:
                            if int(item) == int(i.split('/')[-2]):
                                port_list.append(int(i.split('/')[-1]))
                        port_list = ezfunctions.vlan_list_format(port_list)
                        idict = dict(
                            breakout_port_id = item,
                            admin_speed      = kwargs.domain.fcp_uplink_speed,
                            port_list        = port_list,
                            vsan_ids         = kwargs.domain.vsans
                        )
                        polVars['port_role_fc_storage'].append(idict)
                else:
                    port_list = []
                    for i in kwargs.domain.fcp_uplink_ports:
                        port_list.append(int(i.split('/')[-1]))
                    port_list = ezfunctions.vlan_list_format(port_list)
                    idict = dict(
                        admin_speed  = kwargs.domain.fcp_uplink_speed,
                        port_list    = port_list,
                        vsan_ids     = kwargs.domain.vsans
                    )
                    polVars['port_role_fc_storage'].append(idict)

            #=====================================================
            # Configure Fibre Channel Unified Port Mode
            #=====================================================
            if len(x) == 3:
                port_start = int(kwargs.domain.fcp_uplink_ports[0].split('/')[-2])
                port_end   = int(kwargs.domain.fcp_uplink_ports[-1].split('/')[-2])
                polVars.update(dict(
                    port_modes = [dict(
                        custom_mode = f'BreakoutFibreChannel{kwargs.domain.fcp_uplink_speed}',
                        port_list   = [port_start, port_end]
                    )]
                ))
            else:
                port_start = int(kwargs.domain.fcp_uplink_ports[0].split('/')[-1])
                port_end   = int(kwargs.domain.fcp_uplink_ports[-1].split('/')[-1])
                if port_start < 15: port_start = 1
                if port_end > 12: port_end = 16
                elif port_end > 8: port_end = 12
                elif port_end > 4: port_end = 8
                else: port_end = 4
                polVars.update(dict(
                    port_modes = [dict(
                        custom_mode = 'FibreChannel',
                        port_list   = [port_start, port_end]
                    )]
                ))

        #=====================================================
        # Ethernet Uplink Breakout Ports if present
        #=====================================================
        if len(eth_breakout_ports) > 0:
            port_start= int(eth_breakout_ports[0].split('/'))[2]
            port_end  = int(eth_breakout_ports[-1].split('/'))[2]
            polVars['port_modes'].append(dict(
                custom_mode = f'BreakoutEthernet{kwargs.domain.eth_breakout_speed}',
                port_list   = [port_start, port_end]
            ))

        #=====================================================
        # Server Ports
        #=====================================================
        polVars.update({'port_role_servers':[]})
        for i in kwargs.domain.profiles:
            if len(i.domain_ports[0].split('/')) == 3:
                port_start= int(i.domain_ports[0].split('/'))[2]
                port_end  = int(i.domain_ports[-1].split('/'))[2]
                polVars['port_modes'].append(dict(
                    custom_mode = f'BreakoutEthernet{kwargs.domain.eth_breakout_speed}',
                    port_list   = [port_start, port_end]
                ))
                for e in i.domain_ports:
                    polVars['port_role_servers'].append(dict(
                        breakout_port_id      = e.split('/')[-2],
                        connected_device_type = i.equipment_type,
                        device_number         = i.identifier,
                        port_list             = e.split('/')[-1]
                    ))
            else:
                ports = []
                for e in i.domain_ports: ports.append(int(e.split('/')[-1]))
                port_list = ezfunctions.vlan_list_format(ports)
                polVars['port_role_servers'].append(dict(
                    connected_device_type = i.equipment_type,
                    device_number         = i.identifier,
                    port_list             = port_list
                ))

        # Add Policy Variables to imm_dict
        kwargs.class_path = f'policies,{self.type}'
        kwargs = ezfunctions.ez_append(polVars, kwargs)

        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs

    #=============================================================================
    # Function - Build Policy - Power
    #=============================================================================
    def power(self, kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        power_list = []
        for i in kwargs.chassis:
            power_list.append(i)
        power_list.append('server')
        for i in power_list:
            polVars = dict(
                description      = f'{kwargs.imm.policies.prefix}{i} {descr} Policy',
                name             = f'{kwargs.imm.policies.prefix}{i}',
                power_allocation = 0,
                power_redundancy = 'Grid',
            )
            if i == 'server': polVars.update({'power_restore':'LastState'})
            if '9508' in i: polVars['power_allocation'] = 8400
            else: polVars.pop('power_allocation')

            # Add Policy Variables to imm_dict
            kwargs.class_path = f'policies,{self.type}'
            kwargs = ezfunctions.ez_append(polVars, kwargs)
        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs

    #=============================================================================
    # Function - Build Policy - SAN Connectivity
    #=============================================================================
    def san_connectivity(self, kwargs):
        # Build Dictionary
        descr     = (self.type.replace('_', ' ')).title()
        pci_order = kwargs.pci_order
        for g in kwargs.vic_details:
            gen      = g.split(':')[0]
            name     = (f'scp-vic-{g}').lower()
            slots    = (g.split(':')[1]).split('-')
            polVars = dict(
                description          = f'{kwargs.imm.policies.prefix}{name} {descr} Policy',
                name                 = f'{kwargs.imm.policies.prefix}{name}',
                target_platform      = 'FIAttached',
                vhbas                = [],
                wwnn_allocation_type = 'POOL',
                wwnn_pool            = f'{kwargs.imm.policies.prefix}wwnn',
            )
            ncount = 1
            if 'nvme-fc' in kwargs.protocols: adapter_list = ['VMware', 'FCNVMeInitiator']
            else: adapter_list = ['VMware']
            vcount = 0
            network_policies = []
            for v in kwargs.domain.vsans:
                network_policies.append(f'vsan-{v}')

            
            if len(slots) == 1: placement_order = pci_order, pci_order + 1,
            else: placement_order = pci_order, pci_order,
            for x in range(0,len(adapter_list)):
                polVars['vhbas'].append(dict(
                    fc_zone_policies              = [],
                    fibre_channel_adapter_policy  = adapter_list[x],
                    fibre_channel_network_policies= network_policies,
                    fibre_channel_qos_policy      = 'fc-qos',
                    names                         = [f'vhba{ncount}', f'vhba{ncount + 1}'],
                    placement = dict(
                        pci_order = placement_order,
                        slot_ids  = slots
                    ),
                    wwpn_allocation_type = 'POOL',
                    wwpn_pools           = [f'wwpn-a', f'wwpn-b']
                ))
                if 'switch' in kwargs.domain.switch_mode:
                    polVars['vhbas'][vcount].update({'fc_zone_policies': kwargs.fc_zone})
                else: polVars['vhbas'][vcount].pop('fc_zone_policies')
                ncount += 2
                vcount += 1
                if len(slots) == 1: pci_order += 2
                else: pci_order += 1
                
                # Add Policy Variables to imm_dict
                kwargs.class_path = f'policies,{self.type}'
                kwargs = ezfunctions.ez_append(polVars, kwargs)
        
        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs

    #=============================================================================
    # Function - Build Policy - Serial over LAN
    #=============================================================================
    def serial_over_lan(self, kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        polVars = dict(
            description = f'{kwargs.imm.policies.prefix}sol {descr} Policy',
            name        = f'{kwargs.imm.policies.prefix}sol',
        )

        # Add Policy Variables to imm_dict
        kwargs.class_path = f'policies,{self.type}'
        kwargs = ezfunctions.ez_append(polVars, kwargs)
        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs

    #=============================================================================
    # Function - Build Profiles - Server
    #=============================================================================
    def server(self, kwargs):
        #=====================================================
        # Server Profile IP settings Function
        #=====================================================
        def server_profile_networks(name, p, kwargs):
            #=====================================================
            # Send Error Message if IP Range isn't long enough
            #=====================================================
            def error_ip_range(i):
                prRed(f'!!! ERROR !!!\nNot Enough IPs in Range {i.server} for {name}')
                sys.exit(1)

            #=====================================================
            # Send Error Message if Server Range is missing
            #=====================================================
            def error_server_range(i):
                prRed(f'!!! ERROR !!!\nDid Not Find Server IP Range defined for {i.vlan_type}:{i.name}:{i.vlan_id}')
                sys.exit(1)

            #=====================================================
            # Dictionary of IP Settings for Server
            #=====================================================
            def ipdict(i, ipindex):
                idict = dict(
                    gateway  = i.gateway,
                    ip       = i.server[ipindex],
                    netmask  = i.netmask,
                    prefix   = i.prefix,
                    vlan     = i.vlan_id,
                    vlan_name= i.name,
                )
                return idict
            
            #=====================================================
            # Obtain the Index of the Starting IP Address
            #=====================================================
            ipindex = kwargs.inband.server.index(p.inband_start)
            if 'compute.Blade' in kwargs.server_profiles[name].object_type:
                ipindex = ipindex + int(kwargs.server_profiles[name].slot) - 1

            #=====================================================
            # Loop thru the VLANs
            #=====================================================
            for i in kwargs.vlans:
                if re.search('(inband|iscsi|migration|nfs|nvme|storage|tenant)', i.vlan_type):
                    if not i.server: error_server_range(i)
                    if not len(i.server) >= ipindex: error_ip_range(i)
                if re.search('(iscsi|nvme|storage)', i.vlan_type):
                    if not kwargs.server_profiles[name].get(i.vlan_type):
                        kwargs.server_profiles[name].update({i.vlan_type:[]})
                    idict = ipdict(i, ipindex)
                    kwargs.server_profiles[name][i.vlan_type].append(idict)
                if re.search('(inband|migration|nfs|tenant)', i.vlan_type):
                    idict = ipdict(i, ipindex)
                    kwargs.server_profiles[name][i.vlan_type] = idict
            return kwargs
        
        #=====================================================
        # Build Server Profiles
        #=====================================================
        if 'fcp' in kwargs.protocols: t = 'fcp'
        else: t = 'iscsi'
        templates = []
        for k, v in kwargs.servers.items():
            templates.append(v.template)
        templates = numpy.unique(numpy.array(templates))
        for template in templates:
            polVars = dict(
                action                     = 'Deploy',
                create_from_template       = True,
                targets                    = [],
                ucs_server_profile_template= f'{t}-' + template
            )
            for k,v in kwargs.servers.items():
                if template == v.template:
                    if v.object_type == 'compute.Blade':
                        equipment_type= 'Chassis'
                        identifier    = v.chassis_id
                    else:
                        equipment_type= 'RackServer'
                        identifier    = v.server_id
                    match_profile = False
                    for p in kwargs.domain.profiles:
                        if equipment_type == p.equipment_type and int(identifier) == int(p.identifier):
                            os_type = p.os_type
                            if equipment_type == 'RackServer':
                                pstart = p.profile_start
                                match_profile = True
                            else:
                                suffix = int(p.suffix_digits)
                                pprefix= p.profile_start[:-(suffix)]
                                pstart = int(p.profile_start[-(suffix):])
                                match_profile = True
                            break
                    if match_profile == False:
                        prRed('!!! ERROR !!!')
                        prRed(f'Did not Find Profile Definition for {k}')
                        prRed(f'Profiles:\n')
                        prRed(json.dumps(kwargs.domain.profiles, indent=4))
                        prRed(f'Server Settings:\n')
                        prRed(json.dumps(v, indent=4))
                        prRed('!!! ERROR !!!\n Exiting...')
                        sys.exit(1)
                    if equipment_type == 'RackServer': name = pstart
                    else: name = f"{pprefix}{str(pstart+v.slot-1).zfill(suffix)}"

                    if template == template:
                        polVars['targets'].append(dict(
                            description  = f"{name} Server Profile.",
                            name         = name,
                            serial_number= k
                        ))
                        kwargs.server_profiles[name] = v
                        kwargs.server_profiles[name].boot_volume = kwargs.imm.policies.boot_volume
                        kwargs.server_profiles[name].os_type = os_type
                        kwargs = server_profile_networks(name, p, kwargs)
                    
            polVars['targets']  = sorted(polVars['targets'], key=lambda item: item['name'])
            kwargs.class_path= f'profiles,{self.type}'
            kwargs = ezfunctions.ez_append(polVars, kwargs)

        kwargs.server_profiles = dict(sorted(kwargs.server_profiles.items()))
        for k, v in kwargs.server_profiles.items():
            polVars = {}
            for a, b in v.items():
                polVars[a] = b
            polVars = deepcopy(v)
            polVars.update(deepcopy({'name':k}))
            kwargs.class_path= f'wizard,server_profiles'
            kwargs = ezfunctions.ez_append(polVars, kwargs)

        
        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs

    #=============================================================================
    # Function - Build Policy - SNMP
    #=============================================================================
    def snmp(self, kwargs):
        # Build Dictionary
        polVars = dict(
            description           = f'{kwargs.imm.policies.prefix}snmp Policy',
            enable_snmp           = True,
            name                  = f'{kwargs.imm.policies.prefix}snmp',
            snmp_trap_destinations= [],
            snmp_users            = [dict(
                auth_password    = 1,
                auth_type        = 'SHA',
                name             = kwargs.domain.policies.snmp.username,
                privacy_password = 1,
                privacy_type     = 'AES',
                security_level   = 'AuthPriv'
            )],
            system_contact  = kwargs.domain.policies.snmp.contact,
            system_location = kwargs.domain.policies.snmp.location,
        )
        for i in kwargs.domain.policies.snmp.servers:
            polVars['snmp_trap_destinations'].append(dict(
                destination_address = i,
                port                = 162,
                user                = kwargs.domain.policies.snmp.username
            ))

        # Add Policy Variables to imm_dict
        kwargs.class_path = f'policies,snmp'
        kwargs = ezfunctions.ez_append(polVars, kwargs)
        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs

    #=============================================================================
    # Function - Build Policy - Storage
    #=============================================================================
    def ssh(self, kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        polVars = dict(
            description             = f'{kwargs.imm.policies.prefix}ssh {descr} Policy',
            name                    = f'{kwargs.imm.policies.prefix}ssh',
        )

        # Add Policy Variables to imm_dict
        kwargs.class_path = f'policies,{self.type}'
        kwargs = ezfunctions.ez_append(polVars, kwargs)
        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs

    #=============================================================================
    # Function - Build Policy - Storage
    #=============================================================================
    def storage(self, kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        polVars = dict(
            description             = f'{kwargs.imm.policies.prefix}M2-Raid {descr} Policy',
            name                    = f'{kwargs.imm.policies.prefix}M2-Raid',
            m2_raid_configuration   = [{'slot':'MSTOR-RAID-1'}],
            use_jbod_for_vd_creation= True,
        )

        # Add Policy Variables to imm_dict
        kwargs.class_path = f'policies,{self.type}'
        kwargs = ezfunctions.ez_append(polVars, kwargs)
        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs

    #=============================================================================
    # Function - Build Policy - Switch Control
    #=============================================================================
    def switch_control(self, kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        if kwargs.domain.switch_mode: switch_mode = kwargs.domain.switch_mode
        else: switch_mode = 'end-host'
        polVars = dict(
            description       = f'{kwargs.imm.policies.prefix}sw-ctrl {descr} Policy',
            fc_switching_mode = switch_mode,
            name              = f'{kwargs.imm.policies.prefix}sw-ctrl',
            vlan_port_count_optimization = True,
        )

        # Add Policy Variables to imm_dict
        kwargs.class_path = f'policies,switch_control'
        kwargs = ezfunctions.ez_append(polVars, kwargs)
        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs

    #=============================================================================
    # Function - Build Policy - Syslog
    #=============================================================================
    def syslog(self, kwargs):
        # Build Dictionary
        polVars = dict(
            description = f'{kwargs.imm.policies.prefix}syslog Policy',
            local_logging = dict(
                minimum_severity = 'warning',
            ),
            name            = f'{kwargs.imm.policies.prefix}syslog',
            remote_logging      = [],
        )
        for i in kwargs.domain.policies.syslog.servers:
            polVars['remote_logging'].append(dict(
                enable           = True,
                hostname         = i,
                minimum_severity = 'informational',
            ))

        # Add Policy Variables to imm_dict
        kwargs.class_path = f'policies,syslog'
        kwargs = ezfunctions.ez_append(polVars, kwargs)
        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs

    #=============================================================================
    # Function - Build Policy - System QoS
    #=============================================================================
    def system_qos(self, kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        polVars = dict(
            configure_default_policy = True,
            description = f'{kwargs.imm.policies.prefix}qos {descr} Policy',
            jumbo_mtu   = True,
            name        = f'{kwargs.imm.policies.prefix}qos')
        # Add Policy Variables to imm_dict
        kwargs.class_path = f'policies,{self.type}'
        kwargs = ezfunctions.ez_append(polVars, kwargs)
        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs

    #=============================================================================
    # Function - Build Templates - Server
    #=============================================================================
    def templates(self, kwargs):
        # Build Dictionary
        template_types = []
        server_profiles = []
        for k, v in kwargs.servers.items(): server_profiles.append(v.template)
        server_profiles = list(numpy.unique(numpy.array(server_profiles)))
        if 'fcp' in kwargs.protocols: template_types.append('fcp')
        for i in kwargs.vlans:
            if i.vlan_type == 'iscsi':
                template_types.append('iscsi')
        template_types = list(numpy.unique(numpy.array(template_types)))
        fw = kwargs.firmware_policy_name
        for t in template_types:
            for p in server_profiles:
                bios_policy = p.split('-vic')[0] + '-virtual'
                bios_policy = bios_policy.replace('-tpm', '')
                if 'tpm' in p:
                    bios_policy = bios_policy + '-tpm'
                name = f'{t}-' + p
                if 'iscsi' in t: lcp = 'lcp-iscsi-vic-' + p.split('vic-')[1].replace('-', ':')
                else: lcp = 'lcp-vic-' + p.split('vic-')[1].replace('-', ':')
                scp = 'scp-vic-' + p.split('vic-')[1].replace('-', ':')
                polVars = dict(
                    bios_policy             = bios_policy,
                    boot_order_policy       = f'{kwargs.imm.policies.prefix}{t}-boot',
                    create_template         = True,
                    description             = f'{name} Server Template',
                    firmware_policy         = f'{kwargs.imm.policies.prefix}{fw}',
                    imc_access_policy       = f'{kwargs.imm.policies.prefix}kvm',
                    lan_connectivity_policy = f'{kwargs.imm.policies.prefix}{lcp}',
                    local_user_policy       = f'{kwargs.imm.policies.prefix}users',
                    name                    = name,
                    power_policy            = f'{kwargs.imm.policies.prefix}server',
                    san_connectivity_policy = f'',
                    serial_over_lan_policy  = f'{kwargs.imm.policies.prefix}sol',
                    snmp_policy             = f'{kwargs.imm.policies.prefix}snmp',
                    syslog_policy           = f'{kwargs.imm.policies.prefix}syslog',
                    uuid_pool               = f'{kwargs.imm.policies.prefix}uuid',
                    virtual_kvm_policy      = f'{kwargs.imm.policies.prefix}vkvm',
                    virtual_media_policy    = f'{kwargs.imm.policies.prefix}vmedia',
                )
                if 'M5' in p: polVars.pop('power_policy')
                if 'fcp' in t: polVars.update({'san_connectivity_policy': f'{kwargs.imm.policies.prefix}{scp}'})
                else: polVars.pop('san_connectivity_policy')
                if kwargs.args.deployment_type == 'azure_hci':
                    pop_list = ['imc_access_policy', 'lan_connectivity_policy']
                    for e in pop_list: polVars.pop(e)
                    polVars.extend(dict(
                        network_connectivity_policy= f'{kwargs.imm.policies.prefix}dns',
                        ntp_policy                 = f'{kwargs.imm.policies.prefix}ntp',
                        ssh_policy                 = f'{kwargs.imm.policies.prefix}ssh',
                    ))
                
                # Add Policy Variables to imm_dict
                kwargs.class_path = f'{self.type},server'
                kwargs = ezfunctions.ez_append(polVars, kwargs)
        
        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs

    #=============================================================================
    # Function - Build Policy - Thermal
    #=============================================================================
    def thermal(self, kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        for i in kwargs.chassis:
            polVars = dict(
                fan_control_mode = 'Balanced',
                description      = f'{kwargs.imm.policies.prefix}{i} {descr} Policy',
                name             = f'{kwargs.imm.policies.prefix}{i}',
            )

            # Add Policy Variables to imm_dict
            kwargs.class_path = f'policies,{self.type}'
            kwargs = ezfunctions.ez_append(polVars, kwargs)
        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs

    #=============================================================================
    # Function - Build Pools - MAC
    #=============================================================================
    def uuid(self, kwargs):
        # Build Dictionary
        polVars = dict(
            assignment_order = 'sequential',
            description      = f'{kwargs.imm.policies.prefix}uuid Pool',
            name             = f'{kwargs.imm.policies.prefix}uuid',
            prefix           = '000025B5-0000-0000',
            uuid_blocks      = [{
                'from':f'{kwargs.domain.pools.prefix}00-000000000000',
                'size':1024
            }],
        )

        # Add Policy Variables to imm_dict
        kwargs.class_path = f'pools,{self.type}'
        kwargs = ezfunctions.ez_append(polVars, kwargs)
        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs

    #=============================================================================
    # Function - Build Policy - Virtual KVM
    #=============================================================================
    def virtual_kvm(self, kwargs):
        # Build Dictionary
        polVars = dict(
            allow_tunneled_vkvm = True,
            description         = f'{kwargs.imm.policies.prefix}vkvm Virtual KVM Policy',
            name                = f'{kwargs.imm.policies.prefix}vkvm',
        )

        # Add Policy Variables to imm_dict
        kwargs.class_path = f'policies,{self.type}'
        kwargs = ezfunctions.ez_append(polVars, kwargs)
        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs

    #=============================================================================
    # Function - Build Policy - Virtual Media
    #=============================================================================
    def virtual_media(self, kwargs):
        descr = (self.type.replace('_', ' ')).title()
        # Build Dictionary
        polVars = dict(
            description         = f'{kwargs.imm.policies.prefix}vmedia {descr} Policy',
            name                = f'{kwargs.imm.policies.prefix}vmedia',
        )

        # Add Policy Variables to imm_dict
        kwargs.class_path = f'policies,{self.type}'
        kwargs = ezfunctions.ez_append(polVars, kwargs)
        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs

    #=============================================================================
    # Function - Build Policy - VLAN
    #=============================================================================
    def vlan(self, kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).upper()
        polVars = dict(
            description = f'{kwargs.imm.policies.prefix}vlans {descr} Policy',
            name        = f'{kwargs.imm.policies.prefix}vlans',
            vlans       = [dict(
                auto_allow_on_uplinks = True,
                multicast_policy      = 'mcast',
                name                  = 'default',
                native_vlan           = True,
                vlan_list             = str(1)
            )]
        )
        for i in kwargs.vlans:
            if not int(i.vlan_id) == 1:
                polVars['vlans'].append(dict(
                    multicast_policy = 'mcast',
                    name             = i['name'],
                    vlan_list        = str(i.vlan_id)
                ))
        for i in kwargs.ranges:
            vfull = ezfunctions.vlan_list_full(i.vlan_list)
            if 1 in vfull: vfull.remove(1)
            vlan_list = ezfunctions.vlan_list_format(vfull)
            polVars['vlans'].append(dict(
                multicast_policy = 'mcast',
                name             = i['name'],
                vlan_list        = vlan_list
            ))
        # Add Policy Variables to imm_dict
        kwargs.class_path = f'policies,{self.type}'
        kwargs = ezfunctions.ez_append(polVars, kwargs)
        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs

    #=============================================================================
    # Function - Build Policy - VSAN
    #=============================================================================
    def vsan(self, kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).upper()
        if kwargs.swmode == 'end-host': vsan_scope = 'Uplink'
        else: vsan_scope = 'Storage'
        for i in kwargs.domain.vsans:
            polVars = dict(
                description = f'{kwargs.imm.policies.prefix}vsan-{i} {descr} Policy',
                name        = f'{kwargs.imm.policies.prefix}vsan-{i}',
                vsans       = [dict(
                    fcoe_vlan_id = i,
                    name         = f'{kwargs.imm.policies.prefix}vsan-{i}',
                    vsan_id      = i,
                    vsan_scope   = vsan_scope
                )]
            )

            # Add Policy Variables to imm_dict
            kwargs.class_path = f'policies,{self.type}'
            kwargs = ezfunctions.ez_append(polVars, kwargs)
        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs

    #=============================================================================
    # Function - Build Pools - WWNN/WWPN
    #=============================================================================
    def wwnn(self, kwargs):
        # Build Dictionary
        pfx = kwargs.domain.pools.prefix
        polVars = dict(
            assignment_order = 'sequential',
            description      = f'{kwargs.imm.policies.prefix}wwnn Pool',
            name             = f'{kwargs.imm.policies.prefix}wwnn',
            id_blocks        = [{ 'from':f'20:00:00:25:B5:{pfx}:00:00', 'size':1024 }])
        # Add Policy Variables to imm_dict
        kwargs.class_path = f'pools,wwnn'
        kwargs = ezfunctions.ez_append(polVars, kwargs)
        return kwargs

    #=============================================================================
    # Function - Build Pools - WWNN/WWPN
    #=============================================================================
    def wwpn(self, kwargs):
        # Build Dictionary
        # Loop through WWPN Pools
        flist = ['A', 'B']
        pfx = kwargs.domain.pools.prefix
        for i in flist:
            polVars = dict(
                assignment_order = 'sequential',
                description      = f'{kwargs.imm.policies.prefix}wwpn-{i.lower()} Pool',
                name             = f'{kwargs.imm.policies.prefix}wwpn-{i.lower()}',
                id_blocks        = [{ 'from':f'20:00:00:25:B5:{pfx}:{i}0:00', 'size':1024 }])
            kwargs.class_path = f'pools,wwpn'
            kwargs = ezfunctions.ez_append(polVars, kwargs)
        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs

#=============================================================================
# Wizard Class
#=============================================================================
class wizard(object):
    def __init__(self, type):
        self.type = type

    #=============================================================================
    # Function - Converged Stack - Build IMM Domain Dictionaries
    #=============================================================================
    def build_imm_domain(self, kwargs):
        #==================================
        # Configure Domain Policies
        #==================================
        policy_list = []
        for k, v in kwargs.ezdata.items():
            if v.intersight_type == 'policy' and 'domain' in v.target_platforms: policy_list.append(k)
        for k, v in kwargs.imm.domain.items():
            dom_policy_list = deepcopy(policy_list)
            if not kwargs.imm.domain[k].get('vsans'): dom_policy_list.pop('vsan')
            for i in dom_policy_list:
                kwargs.domain = v; kwargs.domain.name = k
                if kwargs.imm.policies.prefix == None: kwargs.imm.policies.prefix = ''
                kwargs = eval(f'imm(i).{i}(kwargs)')
        #==================================
        # Configure Domain Profiles
        #==================================
        kwargs = imm('domain').domain(kwargs)
        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        kwargs.policy_list = policy_list
        return kwargs

    #=============================================================================
    # Function - Converged Stack - Build IMM Dictionaries
    #=============================================================================
    def build_imm_servers(self, kwargs):
        if kwargs.imm.policies.prefix == None: kwargs.imm.policies.prefix = ''
        pool_list = []; policy_list = []
        if not kwargs.args.deployment_type == 'azurestack':
            #==================================
            # Configure IMM Pools
            #==================================
            for k, v in kwargs.ezdata.items():
                if v.intersight_type == 'pool': pool_list.append(k)
            pool_list.remove('resource')
            for k, v in kwargs.imm.domain.items():
                kwargs.domain = v; kwargs.domain.name = k
                for i in pool_list: kwargs = eval(f'imm(i).{i}(kwargs)')
        #==================================
        # Modify the Policy List
        #==================================
        if kwargs.args.deployment_type == 'azurestack':
            for k, v in kwargs.ezdata.items():
                if v.intersight_type == 'policy' and 'Standalone' in v.target_platforms: policy_list.append(k)
            pop_list = kwargs.ezdata.converged_pop_list.properties.azurestack.enum
            for i in pop_list: policy_list.remove(i)
            kwargs = imm('compute_environment').compute_environment(kwargs)
            for i in policy_list: kwargs = eval(f'imm(i).{i}(kwargs)')
        else:
            for k, v in kwargs.ezdata.items():
                if v.intersight_type == 'policy' and ('chassis' in v.target_platforms or 'FIAttached' in v.target_platforms):
                    policy_list.append(k)
            policy_list.remove('iscsi_static_target')
            policy_list.insert((policy_list.index('iscsi_boot')), 'iscsi_static_target')
            pop_list = kwargs.ezdata.converged_pop_list.properties.domain.enum
            for i in pop_list: policy_list.remove(i)
            if kwargs.sw_mode == 'end-host': policy_list.remove('fc_zone')
            iscsi_type = False
            for i in kwargs.vlans:
                if i.vlan_type == 'iscsi': iscsi_type = True
            if iscsi_type == False:
                pop_list = kwargs.ezdata.converged_pop_list.properties.iscsi.enum
                for i in pop_list: policy_list.remove(i)
            #==================================
            # Configure IMM Policies
            #==================================
            domain_pop_list = True
            for k, v in kwargs.imm.domain.items():
                if v.get('vsans'): domain_pop_list = False
                kwargs = imm('compute_environment').compute_environment(kwargs)
            if domain_pop_list == True:
                pop_list = kwargs.ezdata.converged_pop_list.properties.fc.enum
                for i in pop_list: policy_list.remove(i)
            kwargs.pci_order = 0
            for i in policy_list: kwargs = eval(f'imm(i).{i}(kwargs)')
        #=====================================================
        # Configure Templates/Chassis/Server Profiles
        #=====================================================
        kwargs.policy_list = policy_list
        profiles_list = ['templates', 'chassis', 'server']
        if kwargs.args.deployment_type == 'azure_hci': profiles_list.remove('chassis')
        for p in profiles_list: kwargs = eval(f'imm(p).{p}(kwargs)')
        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs

    #=============================================================================
    # Function - Converged Stack - Build Storage Dictionaries
    #=============================================================================
    def build_netapp(self, kwargs):
        #=====================================================
        # Build NetApp Dictionaries
        #=====================================================
        plist = ['cluster']
        for name,items in kwargs.netapp.cluster.items():
            for i in plist:
                kwargs = eval(f'netapp.build(i).{i}(items, name, kwargs)')
        #==================================
        # Configure NetApp
        #==================================
        plist= ['cluster']
        for i in plist:
            kwargs = eval(f'netapp.api(i).{i}(kwargs)')

        # Add Policy Variables to imm_dict
        idict = kwargs.storage.toDict()
        for k, v in idict.items():
            for a, b in v.items():
                kwargs.class_path = f'storage,appliances'
                kwargs = ezfunctions.ez_append(b, kwargs)

        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs

    #=============================================================================
    # Function - Converged Stack - Credentials - DHCP - DNS - NTP Attributes
    #=============================================================================
    def dns_ntp(self, kwargs):
        #=====================================================
        # DHCP, DNS, NTP, Organization & Return kwargs
        #=====================================================
        i = kwargs.imm_dict.wizard.protocols
        kwargs.dhcp_servers= i.dhcp_servers
        kwargs.dns_servers = i.dns_servers
        kwargs.dns_domains = i.dns_domains
        kwargs.ntp_servers = i.ntp_servers
        kwargs.timezone    = i.timezone
        return kwargs

    #=============================================================================
    # Function - Converged Stack - IMM Attributes
    #=============================================================================
    def imm(self, kwargs):
        #=====================================================
        # Intersight Attributes
        #=====================================================
        kwargs.orgs = []
        for item in kwargs.imm_dict.wizard.intersight:
            item = DotMap(item)
            kwargs.orgs.append(item.organization)
            kwargs.org           = item.organization
            kwargs.virtualization= item.virtualization
            ecount = 0
            for e in kwargs.virtualization:
                kwargs.virtualization[ecount].syslog_server = item.policies.syslog.servers[0]
                ecount += 1
            if kwargs.args.deployment_type == 'azure_hci':
                kwargs.imm.cimc          = item.cimc
                kwargs.imm.firmware      = item.firmware
                kwargs.imm.policies      = item.policies
                kwargs.imm.profiles      = item.profiles
                kwargs.imm.tags          = kwargs.ezdata.tags
                kwargs.imm.username      = item.username
                for p in item.profiles:
                    dlength= len(p.network.data.split('/'))
                    dsplit = p.network.data.split('/')
                    msplit = p.network.management.split('/')
                    if dlength == 3:
                        bk    = int((item.breakout.split('-')[1]).replace('x', ''))
                        sport = int(dsplit[1])
                        bport = int(dsplit[2])
                        if not bport<=bk:
                            prRed('!!! ERROR !!!')
                            prRed(f'Breakout Port Format Must be in the format eth1/X/[1-{bk}]')
                            prRed(f'"{p.data}" is not correct')
                            sys.exit(1)
                        zcount= sport-1
                    #==================================
                    # Build Profile Network Dictionary
                    #==================================
                    fabrics= ['A', 'B']
                    suffix = int(p.suffix_digits)
                    pprefix= p.profile_start[:-(suffix)]
                    pstart = int(p.profile_start[-(suffix):])
                    for z in range(0,len(item.cimc)):
                        name   = f"{pprefix}{str(pstart+z).zfill(suffix)}"
                        if dlength == 3:
                            bport = bport+z-(zcount*bk)
                            nport = f"{dsplit[0]}/{sport}/{bport}"
                            if bport == bk: bport=1; sport = sport+1; zcount = zcount+1
                        else: nport = f"{dsplit[0]}/{int(dsplit[1]+z)}"
                        kwargs.network.imm[name] = DotMap(
                            data_port   = fabrics,
                            mgmt_port   = f"{msplit[0]}/{int(msplit[1]+z)}",
                            network_port= nport
                        )
            else:
                if len(str(item.pools.prefix)) == 1: item.pools.prefix = f'0{item.pools.prefix}'
                for i in item.domains:
                    i = DotMap(i)
                    #==================================
                    # Get Moids for Fabric Switches
                    #==================================
                    kwargs.method = 'get'
                    kwargs.qtype = 'serial_number'
                    kwargs.uri   = 'network/Elements'
                    kwargs.names = i.serial_numbers
                    kwargs       = isight.api(kwargs.qtype).calls(kwargs)
                    serial_moids = kwargs.pmoids
                    serial       = i.serial_numbers[0]
                    serial_moids = {k: v for k, v in sorted(serial_moids.items(), key=lambda item: (item[1]['switch_id']))}
                    kwargs.api_filter= f"RegisteredDevice.Moid eq '{serial_moids[serial]['registered_device']}'"
                    kwargs.qtype     = 'asset_target'
                    kwargs.uri       = 'asset/Targets'
                    kwargs           = isight.api(kwargs.qtype).calls(kwargs)
                    names = list(kwargs.pmoids.keys())
                    i.name= names[0]

                    #==================================
                    # Build Domain Dictionary
                    #==================================
                    kwargs.imm.pool.prefix    = item.pools.prefix
                    kwargs.imm.policies       = item.policies
                    kwargs.imm.domain[i.name] = DotMap(
                        cfg_qos_priorities = item.cfg_qos_priorities,
                        device_model       = serial_moids[serial]['model'],
                        discovery_protocol = item.discovery_protocol,
                        eth_breakout_speed = i.eth_breakout_speed,
                        eth_uplinks        = i.eth_uplink_ports,
                        firmware           = item.firmware,
                        organization       = item.organization,
                        policies           = item.policies,
                        pools              = item.pools,
                        profiles           = i.profiles,
                        registered_device  = serial_moids[serial]['registered_device'],
                        serial_numbers     = list(serial_moids.keys()),
                        tags               = kwargs.ezdata.tags
                    )
                    #==================================
                    # Build Domain Network Dictionary
                    #==================================
                    fabrics = ['A', 'B']
                    for x in range(0,2):
                        kwargs.network.imm[f'{i.name}-{fabrics[x]}'] = DotMap(
                            data_ports  = i.eth_uplink_ports,
                            data_speed  = i.eth_uplink_speed,
                            mgmt_port   = i.network.management,
                            network_port= i.network.data[x],
                            port_channel=True
                        )

                    #=====================================================
                    # Confirm if Fibre-Channel is in Use
                    #=====================================================
                    fcp_count = 0
                    if i.get('fcp_uplink_ports'):
                        if len(i.fcp_uplink_ports) >= 2: fcp_count += 1
                    if i.get('fcp_uplink_speed'): fcp_count += 1
                    if i.get('switch_mode'): fcp_count += 1
                    if i.get('vsans'):
                        if len(i.vsans) >= 2: fcp_count += 1
                    if fcp_count == 4:
                        kwargs.imm.domain[i.name].fcp_uplink_ports= i.fcp_uplink_ports
                        kwargs.imm.domain[i.name].fcp_uplink_speed= i.fcp_uplink_speed
                        kwargs.imm.domain[i.name].switch_mode     = i.switch_mode
                        kwargs.imm.domain[i.name].vsans           = i.vsans
                    kwargs.imm.domain[i.name].virtualization = item.virtualization
                if len(kwargs.imm.domains) == 0: kwargs.imm.profiles = item.profiles
        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs

    #=============================================================================
    # Function - FlexPod Converged Stack Attributes
    #=============================================================================
    def netapp(self, kwargs):
        #==================================
        # Build Cluster Dictionary
        #==================================
        kwargs.netapp.cluster = DotMap()
        kwargs.storage = DotMap()
        for item in kwargs.imm_dict.wizard.netapp:
            for i in item.clusters:
                protocols = []
                for e in i.svm.volumes: protocols.append(e.protocol)
                if 'local' in protocols: protocols.remove('local')
                if 'nvme-fc' in protocols or 'nvme-tcp' in protocols: protocols.append('nvme_of')
                protocols = list(numpy.unique(numpy.array(protocols)))
                kwargs.protocols = protocols
                kwargs.storage[i.name][i.svm.name] = DotMap(
                    cluster= i.name,
                    name   = f"{i.name}:{i.svm.name}",
                    svm    = i.svm.name,
                    vendor = 'netapp'
                )
                cname = i.name
                sname = i.svm.name
                rootv = (i.svm.name).replace('-', '_').lower() + '_root'
                kwargs.netapp.cluster[cname] = DotMap(
                    autosupport= item.autosupport,
                    banner     = i.login_banner,
                    host_prompt= r'[\w]+::>',
                    nodes      = i.nodes,
                    protocols  = protocols,
                    snmp       = item.snmp,
                    svm        = DotMap(
                        agg1     = i.nodes.node01.replace('-', '_').lower() + '_1',
                        agg2     = i.nodes.node02.replace('-', '_').lower() + '_1',
                        banner   = i.svm.login_banner,
                        name     = i.svm.name,
                        m01      = rootv + '_m01',
                        m02      = rootv + '_m02',
                        protocols= protocols,
                        rootv    = rootv,
                        volumes  = i.svm.volumes
                    ),
                    username = item.username
                )
                kwargs.netapp.cluster[cname].nodes.node_list = [i.nodes.node01, i.nodes.node02]
                #==================================
                # Build Cluster Network Dictionary
                #==================================
                nodes = kwargs.netapp.cluster[cname].nodes.node_list
                for x in range(0,len(nodes)):
                    kwargs.network.storage[nodes[x]] = DotMap(
                        data_ports  = i.nodes.data_ports,
                        data_speed  = i.nodes.data_speed,
                        mgmt_port   = i.nodes.network.management,
                        network_port= i.nodes.network.data[x],
                        port_channel=True
                    )

        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs

    #=============================================================================
    # Function - Build Policies - BIOS
    #=============================================================================
    def os_install(self, kwargs):
        #=====================================================
        # Load Variables and Send Begin Notification
        #=====================================================
        validating.begin_section(self.type, 'Install')
        kwargs.org_moid= kwargs.org_moids[kwargs.org].moid
        kwargs.models  = []
        for i in  kwargs.imm_dict.orgs[kwargs.org].wizard.os_configuration:
            kwargs.models.append(i.model)
        kwargs.models   = list(numpy.unique(numpy.array(kwargs.models)))

        #==========================================
        # Get Physical Server Tags to Check for
        # Existing OS Install
        #==========================================
        AzureStack= False
        names     = []
        OpenShift = False
        san_boot  = False
        VMware    = False
        for k,v in kwargs.server_profiles.items():
            names.append(v.serial)
        kwargs.method = 'get'
        kwargs.names = names
        kwargs.pmoid = v.moid
        kwargs.qtype = 'serial_number'
        kwargs.uri   = 'compute/PhysicalSummaries'
        kwargs       = isight.api(kwargs.qtype).calls(kwargs)
        server_profiles = deepcopy(kwargs.server_profiles)
        for k,v in server_profiles.items():
            kwargs.server_profiles[k].hardware_moid = kwargs.pmoids[v.serial].moid
            kwargs.server_profiles[k].tags = kwargs.pmoids[v.serial].tags
            kwargs.server_profiles[k].os_installed = False
            for e in kwargs.pmoids[v.serial].tags:
                if e.Key == 'os_installed' and e.Value == v.os_type:
                    kwargs.server_profiles[k].os_installed = True
            if v.os_type == 'AzureStack': AzureStack = True
            elif v.os_type == 'OpenShift': OpenShift = True
            elif v.os_type == 'VMware': VMware = True
            if v.boot_volume == 'm2':
                if not v.storage_controllers.get('UCS-M2-HWRAID'):
                    prRed(f"!!! ERROR !!!\n  Could not determine the Controller Slot for:")
                    prRed(f"  * Profile: {kwargs.server_profiles[k].name}")
                    prRed(f"  * Serial:  {kwargs.server_profiles[k].serial}\n")
                    sys.exit(1)
            elif v.boot_volume == 'san':
                san_boot = True

        #==========================================
        # Deploy Operating System for each Profile
        #==========================================
        if san_boot == True:
            san_target_a = kwargs.imm_dict.orgs[kwargs.org].storage.appliances[0].wwpns.a[0].wwpn
            san_target_b = kwargs.imm_dict.orgs[kwargs.org].storage.appliances[0].wwpns.b[0].wwpn

        #==================================
        # Get ESXi Root Password
        #==================================
        if AzureStack == True:
            kwargs.sensitive_var = 'windows_admin_password'
            kwargs = ezfunctions.sensitive_var_value(kwargs)
            kwargs.windows_admin_password = kwargs.var_value
        elif VMware == True:
            kwargs.sensitive_var = 'vmware_esxi_password'
            kwargs = ezfunctions.sensitive_var_value(kwargs)
            kwargs.vmware_esxi_password = kwargs.var_value

        #==================================
        # Get Repository Files for Wizard
        #==================================
        dir_files = os.listdir(kwargs.files_dir)
        dir_files.sort()
        if kwargs.deployment_type == 'azure_hci':
            file_types = ['AzureStack', 'ucs-scu']
            os_type    = 'AzureStack'
        else:
            file_types = ['Custom-Cisco', 'ucs-scu']
            os_type    = 'Custom-Cisco'
        for ftype in file_types:
            for f in dir_files:
                if os.path.isfile(os.path.join(kwargs.files_dir , f)):
                    if ftype in f: kwargs.files[ftype] = f

        #==================================
        # Setup Repository Files for Wizard
        #==================================
        kwargs.scu_iso    = kwargs.files['ucs-scu']
        kwargs.scu_version= (kwargs.files['ucs-scu'].split('.iso')[0]).split('-')[2]
        kwargs.os_iso     = kwargs.files[os_type]
        if kwargs.deployment_type == 'azure_hci':
            kwargs.os_name   = re.search('(AzureStackHCI_\\d+.\\d+)', kwargs.files[os_type]).group(1)
        else:  kwargs.os_name= re.search('(ESXi-\\d.\\d(\\.\\d)?)', kwargs.files[os_type]).group(1)
        jvars = kwargs.ezdata.operatingSystem.allOf[1].properties[kwargs.os_name]
        kwargs.os_config  = jvars.config
        kwargs.os_vendor  = jvars.vendor
        kwargs.os_version = jvars.version


        #==================================
        # Get Org Software Repo
        #==================================
        kwargs.method    = 'get'
        kwargs.names     = ['user-catalog']
        kwargs.qtype     = 'org_repository'
        kwargs.uri       = 'softwarerepository/Catalogs'
        kwargs           = isight.api(kwargs.qtype).calls(kwargs)
        kwargs.repository= kwargs.pmoids['user-catalog'].moid

        #==================================
        # Get OS Catalogs and OS Config
        #==================================
        kwargs.api_filter= f"Name in  ('shared')"
        kwargs.qtype     = 'os_catalog'
        kwargs.uri       = 'os/Catalogs'
        kwargs           = isight.api(kwargs.qtype).calls(kwargs)
        kwargs.os_catalog= kwargs.pmoids['shared'].moid

        kwargs.api_filter= f"Catalog.Moid eq '{kwargs.os_catalog}'"
        kwargs.qtype     = 'os_configuration'
        kwargs.uri       = 'os/ConfigurationFiles'
        kwargs           = isight.api(kwargs.qtype).calls(kwargs)
        kwargs.os_config = kwargs.pmoids[kwargs.os_config].moid

        #==================================
        # Get Existing SCU Repositories
        #==================================
        kwargs.api_filter= f"Catalog.Moid eq '{kwargs.repository}'"
        kwargs.names     = [f'scu-{kwargs.scu_version}']
        kwargs.qtype     = 'server_configuration_utility'
        kwargs.uri       = 'firmware/ServerConfigurationUtilityDistributables'
        kwargs           = isight.api(kwargs.qtype).calls(kwargs)

        #==================================
        # Create/Patch SCU Repo apiBody
        #==================================
        kwargs.apiBody = server_config_utility_repo(kwargs)
        if kwargs.pmoids.get(kwargs.apiBody['Name']):
            kwargs.method= 'patch'
            kwargs.pmoid = kwargs.pmoids[kwargs.apiBody['Name']].moid
        else: kwargs.method = 'post'
        kwargs         = isight.api(self.type).calls(kwargs)
        kwargs.scu_moid= kwargs.pmoid

        #==================================
        # Test Repo URL for File
        #==================================
        repo_url = f'https://{kwargs.repo_server}{kwargs.repo_path}{kwargs.scu_iso}'
        try: requests.head(repo_url, allow_redirects=True, verify=False, timeout=10)
        except requests.RequestException as e:
            prRed(f"!!! ERROR !!!\n  Exception when calling {repo_url}:\n {e}\n")
            sys.exit(1)

        kwargs.api_filter= f"Name eq '{kwargs.os_name}'"
        kwargs.method    = 'get'
        kwargs.names     = [kwargs.os_name]
        kwargs.qtype     = 'operating_system'
        kwargs.uri       = 'softwarerepository/OperatingSystemFiles'
        kwargs           = isight.api(kwargs.qtype).calls(kwargs)
        kwargs.os_repos  = kwargs.pmoids

        #==================================
        # Create/Patch OS Repo apiBody
        #==================================
        kwargs.apiBody = os_software_repo(kwargs)
        kwargs.uri     = 'softwarerepository/OperatingSystemFiles'
        if kwargs.os_repos.get(kwargs.apiBody['Name']):
            kwargs.method= 'patch'
            kwargs.pmoid = kwargs.os_repos[kwargs.apiBody['Name']].moid
        else: kwargs.method= 'post'
        kwargs        = isight.api(self.type).calls(kwargs)
        kwargs.os_moid= kwargs.pmoid

        #==================================
        # Test Repo URL for File
        #==================================
        repo_url = f'https://{kwargs.repo_server}{kwargs.repo_path}{kwargs.os_iso}'
        try: requests.head(repo_url, allow_redirects=True, verify=False, timeout=10)
        except requests.RequestException as e:
            prRed(f"!!! ERROR !!!\n  Exception when calling {repo_url}:\n {e}\n")
            sys.exit(1)

        #==========================================
        # Install Operating System on Servers
        #==========================================
        count = 1
        for k,v in kwargs.server_profiles.items():
            if v.boot_volume == 'san':
                if count % 2 == 0:
                    kwargs.san_target = san_target_a
                    kwargs.wwpn = 0
                else:
                    kwargs.san_target = san_target_b
                    kwargs.wwpn = 1
            if v.os_installed == False:
                indx           = [e for e, d in enumerate(v.macs) if 'mgmt-a' in d.values()][0]
                kwargs.mgmt_mac= v.macs[indx].mac
                kwargs.fqdn    = k + '.' + kwargs.dns_domains[0]
                kwargs.apiBody = os_installation_body(k, v, kwargs)
                kwargs.method  = 'post'
                kwargs.qtype   = self.type
                kwargs.uri     = 'os/Installs'
                if v.boot_volume == 'san':
                    prGreen(f"{'-'*91}\n"\
                            f"      * host {k}: initiator: {v.wwpns[kwargs.wwpn].wwpn}\n"\
                            f"         target: {kwargs.san_target}\n"\
                            f"         mac: {kwargs.mgmt_mac}\n"\
                            f"{'-'*91}\n")
                else:
                    prGreen(f"{'-'*91}\n"\
                            f"      * host {k}:\n"\
                            f"         target: {v.boot_volume}\n"\
                            f"         mac: {kwargs.mgmt_mac}\n"\
                            f"{'-'*91}\n")
                kwargs = isight.api(self.type).calls(kwargs)
                kwargs.server_profiles[k].os_install = DotMap(moid=kwargs.pmoid,workflow='')
        
        time.sleep(120)
        #=================================================
        # Monitor OS Installation until Complete
        #=================================================
        for k,v in  kwargs.server_profiles.items():
            if v.os_installed == False:
                kwargs.fqdn      = k + '.' + kwargs.dns_domains[0]
                kwargs.api_filter= f"Input.OSInstallInputs.Answers.Hostname eq '{kwargs.fqdn}'"
                kwargs.method    = 'get'
                kwargs.qtype     = self.type
                kwargs.uri       = 'workflow/WorkflowInfos'
                kwargs           = isight.api(self.type).calls(kwargs)
                v.os_install.workflow = kwargs.results[len(kwargs.results)-1].Moid
                install_complete = False
                while install_complete == False:
                    kwargs.method= 'get_by_moid'
                    kwargs.pmoid = v.os_install.workflow
                    kwargs.qtype = 'workflow_info'
                    kwargs.uri   = 'workflow/WorkflowInfos'
                    kwargs = isight.api(self.type).calls(kwargs)
                    if kwargs.results.Status == 'COMPLETED':
                        install_complete= True
                        install_success = True
                        prGreen(f'    - Completed Operating System Installation for {k}.')
                    elif re.search('(FAILED|TERMINATED|TIME_OUT)', kwargs.results.Status):
                        kwargs.upgrade.failed.update({k:v.moid})
                        prRed(f'!!! FAILED !!! Operating System Installation for Server Profile {k} failed.')
                        install_complete= True
                        install_success = False
                    else:
                        progress= kwargs.results.Progress
                        status  = kwargs.results.Status
                        prCyan(f'      * Operating System Installation for {k}.')
                        prCyan(f'        Status is {status} Progress is {progress}, Waiting 120 seconds.')
                        time.sleep(120)

                #=================================================
                # Add os_installed Tag to Physical Server
                #=================================================
                if install_success == True:
                    tags = deepcopy(v.tags)
                    tag_body = []
                    os_installed = False
                    for e in tags:
                        if e.Key == 'os_installed':
                            os_installed = True
                            tag_body.append({'Key':e.Key,'Value':v.os_type})
                        else: tag_body.append(e.toDict())
                    if os_installed == False:
                        tag_body.append({'Key':'os_installed','Value':v.os_type})
                    tags = list({v['Key']:v for v in tags}.values())
                    kwargs.apiBody={'Tags':tag_body}
                    kwargs.method = 'patch'
                    kwargs.pmoid  = v.hardware_moid
                    kwargs.qtype  = 'update_tags'
                    kwargs.tag_server_profile = k
                    if v.object_type == 'compute.Blade': kwargs.uri = 'compute/Blades'
                    else: kwargs.uri = 'compute/RackUnits'
                    kwargs        = isight.api(kwargs.qtype).calls(kwargs)
            else: prCyan(f'      * Skipping Operating System Install for {k}. OS Already Installed.')
        #=====================================================
        # Send End Notification and return kwargs
        #=====================================================
        validating.end_section(self.type, 'Install')
        return kwargs

    #=============================================================================
    # Function - Build Server Identies for Zoning host/igroups
    #=============================================================================
    def server_identities(self, kwargs):
        #=====================================================
        # Get Server Profile Names and Moids
        #=====================================================
        kwargs.names = []
        for i in kwargs.imm_dict.orgs[kwargs.org].wizard.server_profiles:
            kwargs.server_profiles[i.name] = DotMap()
            for k, v in i.items(): kwargs.server_profiles[i.name][k] = v
            kwargs.server_profiles[i.name]['hardware_moid'] = i.moid
            kwargs.server_profiles[i.name].pop('moid')
            kwargs.names.append(i.name)
        kwargs.names.sort()
        kwargs.server_profiles = DotMap(dict(sorted(kwargs.server_profiles.items())))
        
        kwargs.method = 'get'
        kwargs.qtype  = 'server'
        kwargs.uri    = 'server/Profiles'
        kwargs        = isight.api(kwargs.ptype).calls(kwargs)
        for k, v in kwargs.pmoids.items(): kwargs.server_profiles[k].moid = v.moid
        
        for k, v in kwargs.server_profiles.items():
            kwargs.api_filter= f"Profile.Moid eq '{v.moid}'"
            kwargs.method    = 'get'
            kwargs.qtype     = 'vnics'
            kwargs.uri       = 'vnic/EthIfs'
            kwargs = isight.api(kwargs.qtype).calls(kwargs)
            r = kwargs.results
            mac_list = []
            kwargs.server_profiles[k].macs = []
            kwargs.eth_moids = []
            for s in r:
                s = DotMap(s)
                kwargs.eth_moids.append(s.FabricEthNetworkGroupPolicy[0].Moid)
                mac_list.append(dict(
                    mac   = s.MacAddress,
                    name  = s.Name,
                    order = s.Order,
                    switch= s.Placement.SwitchId,
                    vgroup= s.FabricEthNetworkGroupPolicy[0].Moid
            ))
            kwargs.server_profiles[k].macs = sorted(mac_list, key=lambda k: (k['order']))
        
            #=====================================================
            # Get WWPN's for vHBAs and Add to Profile Map
            #=====================================================
            kwargs.api_filter= f"Profile.Moid eq '{v.moid}'"
            kwargs.qtype     = 'vhbas'
            kwargs.uri       = 'vnic/FcIfs'
            kwargs = isight.api(kwargs.qtype).calls(kwargs)
            r = kwargs.results
            wwpn_list = []
            for s in r:
                s = DotMap(s)
                wwpn_list.append(dict(
                    switch= s.Placement.SwitchId,
                    name  = s.Name,
                    order = s.Order,
                    wwpn  = s.Wwpn
            ))
            kwargs.server_profiles[k].wwpns = (sorted(wwpn_list, key=lambda k: (k['order'])))
        
            #=====================================================
            # Get IQN for Host and Add to Profile Map if iscsi
            #=====================================================
            iscsi_true = False
            for i in kwargs.vlans:
              if re.search('iscsi|nvme-tcp', i.vlan_type): iscsi_true = True
            if iscsi_true == True:
                kwargs.api_filter= f"AssignedToEntity.Moid eq '{v.moid}'"
                kwargs.method    = 'get'
                kwargs.qtype     = 'iqn'
                kwargs.uri       = 'iqnpool/Pools'
                kwargs = isight.api(kwargs.qtype).calls(kwargs)
                r = DotMap(kwargs.results)
                kwargs.server_profiles[k].iqn = r.IqnId
        kwargs.server_profile = DotMap(kwargs.server_profiles)
        
        # Query API for Ethernet Network Policies and Add to Server Profile Dictionaries
        kwargs.eth_moids = numpy.unique(numpy.array(kwargs.eth_moids))
        kwargs.method= 'get_by_moid'
        kwargs.qtype = 'ethernet_network_group'
        kwargs.uri   = 'fabric/EthNetworkGroupPolicies'
        server_settings = deepcopy(kwargs.server_profiles)
        for i in kwargs.eth_moids:
            kwargs.pmoid = i
            isight.api(kwargs.qtype).calls(kwargs)
            results = DotMap(kwargs.results)
            for k, v in server_settings.items():
                for e in v.macs:
                    if e.vgroup == results.Moid:
                        vgroup = e.vgroup
                        indx = [e for e, d in enumerate(v.macs) if vgroup in d.values()]
                        for ix in indx:
                            kwargs.server_profiles[k].macs[ix]['vlan_group']= results.Name
                            kwargs.server_profiles[k].macs[ix]['allowed']   = results.VlanSettings.AllowedVlans
                            kwargs.server_profiles[k].macs[ix]['native']    = results.VlanSettings.NativeVlan

        #=====================================================
        # Run Lun Creation Class
        #=====================================================
        if kwargs.args.deployment_type == 'flexpod':
            kwargs = netapp.build('lun').lun(kwargs)

        for k, v in kwargs.server_profiles.items():
            polVars = v.toDict()

            # Add Policy Variables to imm_dict
            kwargs.class_path = f'wizard,os_configuration'
            kwargs = ezfunctions.ez_append(polVars, kwargs)

        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs

    #=============================================================================
    # Function - Converged Stack - VLAN Attributes
    #=============================================================================
    def vlans(self, kwargs):
        kwargs.vlans = []
        for i in kwargs.imm_dict.wizard.vlans:
            #==================================
            # Build VLAN Dictionary
            #==================================
            netwk = '%s' % ipaddress.IPv4Network(i.network, strict=False)
            vDict = DotMap(
                configure_l2= i.configure_l2,
                configure_l3= i.configure_l3,
                disjoint    = i.disjoint,
                gateway     = i.network.split('/')[0],
                name        = i.name,
                native_vlan = i.native_vlan,
                netmask     = ((ipaddress.IPv4Network(netwk)).with_netmask).split('/')[1],
                network     = netwk,
                prefix      = i.network.split('/')[1],
                switch_type = i.switch_type,
                vlan_id     = i.vlan_id,
                vlan_type   = i.vlan_type,
            )
            def iprange(xrange):
                ipsplit = xrange.split('-')
                ip1 = ipsplit[0]
                ips = []
                a = ip1.split('.')
                for x in range(int(ip1.split('.')[-1]), int(ipsplit[1])+1):
                    ipaddress = f'{a[0]}.{a[1]}.{a[2]}.{x}'
                    ips.append(ipaddress)
                return ips
            if i.ranges.get('controller'): vDict.controller = iprange(i.ranges.controller)
            if i.ranges.get('pool') and re.search('(inband|ooband)', i.vlan_type):
                vDict.pool = iprange(i.ranges.pool)
            if i.ranges.get('server'): vDict.server = iprange(i.ranges.server)
            kwargs.vlans.append(vDict)

        #==================================
        # Build VLAN Ranges Dictionary
        #==================================
        kwargs.ranges = []
        for i in kwargs.imm_dict.wizard.vlan_ranges:
            kwargs.ranges.append(DotMap(
                configure_l2= i.configure_l2,
                disjoint    = i.disjoint,
                name        = i.name_prefix,
                vlan_list   = i.vlan_range
            ))

        #==================================
        # Build inband|nfs|ooband Dict
        #==================================
        for i in kwargs.vlans:
            if re.search('(inband|nfs|ooband|migration)', i.vlan_type):
                kwargs[i.vlan_type] = i

        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs

#=============================================================================
# Function - Build apiBody for Operating System Installation
#=============================================================================
def os_installation_body(k, v, kwargs):
    apiBody = {
        'Answers': {
            'Hostname': kwargs.fqdn,
            'IpConfigType': 'static',
            'IpConfiguration': {
                'IpV4Config': {
                    'Gateway': v.inband.gateway,
                    'IpAddress': v.inband.ip,
                    'Netmask': v.inband.netmask,
                    'ObjectType': 'comm.IpV4Interface'
                }, 'ObjectType': 'os.Ipv4Configuration',
            },
            "IsRootPasswordCrypted": False,
            'Nameserver': kwargs.dns_servers[0],
            'NetworkDevice': kwargs.mgmt_mac,
            'ObjectType': 'os.Answers',
            'RootPassword': kwargs.vmware_esxi_password,
            'Source': 'Template'
        },
        'ConfigurationFile': { 'Moid': kwargs.os_config,
            'ObjectType': 'os.ConfigurationFile',
        },
        'Image': { 'Moid': kwargs.os_moid,
            'ObjectType': 'softwarerepository.OperatingSystemFile',
        },
        'InstallMethod': 'vMedia',
        'InstallTarget': {},
        'Name': f'{k}-osinstall',
        'ObjectType': 'os.Install',
        'Organization': { 'Moid': kwargs.org_moid,
            'ObjectType': 'organization.Organization',
        },
        'OsduImage': {
            'Moid': kwargs.scu_moid,
            'ObjectType': 'firmware.ServerConfigurationUtilityDistributable',
        },
        'OverrideSecureBoot': True,
        'Server': { 'Moid': v.hardware_moid, 'ObjectType': v.object_type}
    }
    if v.boot_volume == 'san':
        apiBody['InstallTarget'] = {
            'InitiatorWwpn': v.wwpns[kwargs.wwpn].wwpn,
            'LunId': 0,
            'ObjectType': 'os.FibreChannelTarget',
            'TargetWwpn': kwargs.san_target
        }
    elif v.boot_volume == 'm2':
        apiBody['InstallTarget'] = {
            "Id": 0,
            "Name": "MStorBootVd",
            "ObjectType": "os.VirtualDrive",
            "StorageControllerSlotId": int(v.storage_controllers['UCS-M2-HWRAID'])
        }
    return apiBody

#=============================================================================
# Function - Build apiBody for Operating System Software Repository
#=============================================================================
def os_software_repo(kwargs):
    apiBody = { 'Catalog': { 'Moid': kwargs.repository,
            'ObjectType': 'softwarerepository.Catalog'
        },
        'Description': f'{kwargs.os_name} Server Configuration Utility',
        'Name': kwargs.os_name,
        'ObjectType': 'softwarerepository.OperatingSystemFile',
        'Source': {
            'LocationLink': f'https://{kwargs.repo_server}{kwargs.repo_path}{kwargs.os_iso}',
            'ObjectType': 'softwarerepository.HttpServer',
        },
        'Vendor': kwargs.os_vendor, 'Version': kwargs.os_version
    }
    return apiBody

#=============================================================================
# Function - Build apiBody for Server Configuration Utility Repository
#=============================================================================
def server_config_utility_repo(kwargs):
    apiBody = {
        'Catalog': { 'Moid': kwargs.repository,
            'ObjectType': 'softwarerepository.Catalog'
        },
        'Description': f'scu-{kwargs.scu_version} Server Configuration Utility',
        'Name': f'scu-{kwargs.scu_version}',
        'ObjectType': 'firmware.ServerConfigurationUtilityDistributable',
        'Source': {
            'LocationLink': f'https://{kwargs.repo_server}{kwargs.repo_path}{kwargs.scu_iso}',
            'ObjectType': 'softwarerepository.HttpServer',
        },
        'SupportedModels': kwargs.models,
        'Vendor': 'Cisco', 'Version': kwargs.scu_version
    }
    return apiBody
