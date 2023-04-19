#!/usr/bin/env python3

#=============================================================================
# Source Modules
#=============================================================================
from copy import deepcopy
from dotmap import DotMap
import ipaddress
import json
import numpy
import re
import requests
import sys
import time
import validating
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

sys.path.insert(0, './classes')
from classes import ezfunctions
from classes import netapp
import isdk
#=======================================================
# IMM Class
#=======================================================
class imm(object):
    def __init__(self, type):
        self.type = type

    #=============================================================================
    # Function - Build Policies - BIOS
    #=============================================================================
    def bios(self, pargs, **kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).upper()
        btemplates = []
        dataset = []
        for k, v in pargs.servers.items():
            dataset.append(f"{v.gen}_{v.cpu}_{v.tpm}")
        models = numpy.unique(numpy.array(dataset))
        for i in models:
            gen, cpu, tpm = i.split('_')
            if tpm == True:btemplates.append(f'{gen}-{cpu}-virtual-tpm')
            else: btemplates.append(f'{gen}-{cpu}-virtual')
        btemplates = list(numpy.unique(numpy.array(btemplates)))
        for i in btemplates:
            polVars = dict(
                baud_rate           = 115200,
                bios_template       = i,
                console_redirection = f'serial-port-a',
                description         = f'{pargs.domain.policies.prefix}{i} {descr} Policy',
                name                = f'{pargs.domain.policies.prefix}{i}',
                serial_port_aenable = f'enabled',
                terminal_type       = f'vt100',
            )

            # Add Policy Variables to immDict
            kwargs['class_path'] = f'policies,{self.type}'
            kwargs = ezfunctions.ez_append(polVars, **kwargs)
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - Build Policies - Boot Order
    #=============================================================================
    def boot_order(self, pargs, **kwargs):
        # Build Dictionary
        ptypes = []
        if 'fc' in pargs.dtype: ptypes.append('fcp')
        for i in pargs.vlans:
            i = DotMap(deepcopy(i))
            if not i.vlan_type in ptypes and re.search('iscsi', i.vlan_type): ptypes.append(i.vlan_type)
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
                'name': f'{pargs.domain.policies.prefix}{i}-boot',
            }
            if 'fcp' in i:
                fabrics = ['a', 'b']
                for x in range(0,len(fabrics)):
                    pargs.storage = DotMap(deepcopy(kwargs['immDict']['orgs'][kwargs['org']]['storage']))
                    for k,v in pargs.storage.items():
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
            
            # Add Policy Variables to immDict
            kwargs['class_path'] = f'policies,{self.type}'
            kwargs = ezfunctions.ez_append(polVars, **kwargs)

        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - Build Profiles - Chassis
    #=============================================================================
    def chassis(self, pargs, **kwargs):
        # Build Dictionary
        for k, v in pargs.chassis.items():
            polVars = dict(
                action            = 'Deploy',
                imc_access_policy = f'{pargs.domain.policies.prefix}kvm',
                power_policy      = f'{pargs.domain.policies.prefix}{deepcopy(k)}',
                snmp_policy       = f'{pargs.domain.policies.prefix}snmp',
                thermal_policy    = f'{pargs.domain.policies.prefix}{deepcopy(k)}',
                targets           = [],
            )
            for i in v:
                polVars['targets'].append(dict(
                    description   = f'{i.domain}-{i.identity} Chassis Profile',
                    name          = f'{i.domain}-{i.identity}',
                    serial_number = i.serial
                ))
            
            # Add Policy Variables to immDict
            kwargs['class_path'] = f'profiles,{self.type}'
            kwargs = ezfunctions.ez_append(polVars, **kwargs)
        
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - Build Profiles - Chassis
    #=============================================================================
    def compute_environment(self, pargs, **kwargs):
        pargs.servers  = DotMap([])
        #=====================================================
        # Server Dictionary Function
        #=====================================================
        def server_dictionary(i, pargs, **kwargs):
            pargs.apiMethod='get'
            pargs.apiFilter= f"Ancestors/any(t:t/Moid eq '{i.Moid}')"
            pargs.policy   = 'processor'
            pargs.purpose  = 'inventory'
            kwargs = isdk.api(pargs.policy).calls(pargs, **kwargs)
            cpu = DotMap(deepcopy(kwargs['results'][0]))
            pargs.policy   = 'tpm'
            kwargs = isdk.api(pargs.policy).calls(pargs, **kwargs)
            tpmd = deepcopy(kwargs['results'])
            pargs.policy   = 'adapter'
            kwargs = isdk.api(pargs.policy).calls(pargs, **kwargs)
            vic = DotMap(deepcopy(kwargs['results'][0]))
            pargs.pop('apiFilter')
            if 'Intel' in cpu.Model: cpu_vendor = 'intel'
            else: cpu_vendor = 'amd'
            if re.search('(V5)', vic.Model): vic_generation = 'gen5'
            else: vic_generation = 'gen4'
            server_generation = re.search('-(M[\\d])', i.Model).group(1)
            if len(tpmd) > 0:
                template = f"{server_generation}-{cpu_vendor}-tpm-vic-{vic_generation}"
                tpm = '-tpm'
            else:
                template = f"{server_generation}-{cpu_vendor}-vic-{vic_generation}"
                tpm = ''
            pargs.servers[i.Serial] = DotMap(
                chassis_id  = i.ChassisId,
                chassis_moid= i.Parent.Moid,
                cpu         = cpu_vendor,
                domain      = pargs.domain.name,
                firmware    = i.Firmware,
                gen         = server_generation,
                moid        = i.Moid,
                model       = i.Model,
                object_type = i.SourceObjectType,
                serial      = i.Serial,
                server_id   = i.ServerId,
                slot        = i.SlotId,
                template    = template,
                tpm         = tpm,
                vic         = vic_generation
            )
            if i.SourceObjectType == 'compute.RackUnit':
                pargs.servers[i.Serial].pop('chassis_moid')
            return pargs

        #=====================================================
        # Build Domain Dictionaries
        #=====================================================
        if pargs.domain:
            pargs.chassis  = DotMap([])
            pargs.apiMethod= 'get'
            pargs.names    = [pargs.domain.serial_numbers[0]]
            pargs.policy   = 'serial_number'
            pargs.purpose  = 'domain'
            kwargs         = isdk.api('serial_number').calls(pargs, **kwargs)
            pmoids         = DotMap(deepcopy(kwargs['pmoids']))

            for k, v in pmoids.items():
                reg_device = v.registered_device
            pargs.apiFilter= f"RegisteredDevice.Moid eq '{reg_device}'"
            pargs.purpose  = 'chassis'
            kwargs         = isdk.api('serial_number').calls(pargs, **kwargs)
            chassis_pmoids = DotMap(deepcopy(kwargs['pmoids']))
            pargs.purpose  = 'server'
            kwargs         = isdk.api('serial_number').calls(pargs, **kwargs)
            server_pmoids  = DotMap(deepcopy(kwargs['pmoids']))
            pargs.pop('apiFilter')
            #=====================================================
            # Build Chassis Dictionary
            #=====================================================
            for k, v in chassis_pmoids.items():
                model = str(v.model).lower()
                pargs.chassis[model].update(DotMap(
                    domain  = pargs.domain.name,
                    identity= v.id,
                    serial  = k
                ))

            #=====================================================
            # Build Server Dictionaries - Domain
            #=====================================================
            for k, v in chassis_pmoids.items():
                for e in v.blades:
                    pargs.apiMethod='by_moid'
                    pargs.policy   = 'serial_number'
                    pargs.purpose  = 'server'
                    pargs.pmoid    = e.moid
                    kwargs = isdk.api(pargs.policy).calls(pargs, **kwargs)
                    i = DotMap(deepcopy(kwargs['results']))
                    pargs = server_dictionary(i, pargs, **kwargs)
            for k, v in server_pmoids.items():
                pargs.apiMethod='by_moid'
                pargs.policy   = 'serial_number'
                pargs.purpose  = 'server'
                pargs.pmoid    = e.moid
                kwargs = isdk.api(pargs.policy).calls(pargs, **kwargs)
                i = DotMap(deepcopy(kwargs['results']))
                pargs = server_dictionary(i, pargs, **kwargs)
        else:
            #=====================================================
            # Build Server Dictionaries - Standalone
            #=====================================================
            pargs.apiMethod='get'
            pargs.names    = pargs.serial_numbers
            pargs.policy   = 'serial_number'
            pargs.purpose  = 'server'
            kwargs = isdk.api(pargs.policy).calls(pargs, **kwargs)
            for i in kwargs['results']:
                i = DotMap(deepcopy(i))
                pargs = server_dictionary(i, pargs, **kwargs)


        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - Build Profiles - Domain
    #=============================================================================
    def domain(self, pargs, **kwargs):
        # Build Dictionary
        polVars = dict(
            action                      = 'Deploy',
            description                 = f'{pargs.domain.name} Domain Profile',
            name                        = pargs.domain.name,
            network_connectivity_policy = f'{pargs.domain.policies.prefix}dns',
            ntp_policy                  = f'{pargs.domain.policies.prefix}ntp',
            port_policies               = [f'{pargs.domain.name}-A', f'{pargs.domain.name}-B'],
            serial_numbers              = pargs.domain.serial_numbers,
            snmp_policy                 = f'{pargs.domain.policies.prefix}snmp-domain',
            switch_control_policy       = f'{pargs.domain.policies.prefix}sw-ctrl',
            syslog_policy               = f'{pargs.domain.policies.prefix}syslog-domain',
            system_qos_policy           = f'{pargs.domain.policies.prefix}qos',
            vlan_policies               = f'{pargs.domain.policies.prefix}vlans',
        )
        if re.search('(fc|fc-nvme)', pargs.dtype):
            for i in pargs.domain.vsans:
                polVars.update({'vsan_policies': [
                    f'{pargs.domain.policies.prefix}vsan-{i}'
                ]})
        # Add Policy Variables to immDict
        kwargs['class_path'] = f'profiles,{self.type}'
        kwargs = ezfunctions.ez_append(polVars, **kwargs)
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - Build Policy - Ethernet Adapter
    #=============================================================================
    def ethernet_adapter(self, pargs, **kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        plist = ['16RxQs-4G', '16RxQs-5G', 'VMware', 'VMware-High-Trf']
        for i in plist:
            polVars = dict(
                adapter_template = i,
                description      = f'{pargs.domain.policies.prefix}{i} {descr} Policy',
                name             = f'{pargs.domain.policies.prefix}{i}',
            )

            # Add Policy Variables to immDict
            kwargs['class_path'] = f'policies,{self.type}'
            kwargs = ezfunctions.ez_append(polVars, **kwargs)
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - Build Policy - Ethernet Network Control
    #=============================================================================
    def ethernet_network_control(self, pargs, **kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        plist = ['cdp', 'cdp-lldp', 'lldp']
        for i in plist:
            if 'cdp' in i: cdpe = True
            else: cdpe = False
            if 'lldp' in i: lldpe = True
            else: lldpe = False
            polVars = dict(
                cdp_enable           = cdpe,
                description          = f'{pargs.domain.policies.prefix}{i} {descr} Policy',
                name                 = f'{pargs.domain.policies.prefix}{i}',
                lldp_receive_enable  = lldpe,
                lldp_transmit_enable = lldpe,
                mac_register_mode    = 'nativeVlanOnly',
                mac_security_forge   = 'allow',
            )

            # Add Policy Variables to immDict
            kwargs['class_path'] = f'policies,{self.type}'
            kwargs = ezfunctions.ez_append(polVars, **kwargs)
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - Build Policy - Ethernet Network Group
    #=============================================================================
    def ethernet_network_group(self, pargs, **kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        vlans = []
        for i in pargs.vlans: vlans.append(i['vlan_id'])
        for i in pargs.ranges:
            vrange = ezfunctions.vlan_list_full(i['vlan_list'])
            vlans.extend(vrange)
        pargs.vlan = DotMap()
        pargs.vlan.iscsi     = []
        pargs.vlan.mgmt      = ''
        pargs.vlan.migration = ''
        pargs.vlan.nfs       = ''
        pargs.vlan.nvme      = []
        pargs.vlan['all_vlans'] = ezfunctions.vlan_list_format(list(numpy.unique(numpy.array(vlans))))
        for i in pargs.vlans:
            i = DotMap(deepcopy(i))
            if   i.vlan_type == 'inband': pargs.vlan.mgmt = i.vlan_id
            elif i.vlan_type == 'iscsi': pargs.vlan.iscsi.append(i.vlan_id)
            elif i.vlan_type == 'migration': pargs.vlan.migration = i.vlan_id
            elif i.vlan_type == 'nfs': pargs.vlan.nfs = i.vlan_id
            elif i.vlan_type == 'nvme': pargs.vlan.nvme.append(i.vlan_id)
        if len(pargs.vlan.iscsi) == 2 and len(pargs.vlan.nvme) == 2:
            pargs.vlan.storage_a = ezfunctions.vlan_list_format(sorted(
                [pargs.vlan.nfs, pargs.vlan.iscsi[0], pargs.vlan.nvme[0]]))
            pargs.vlan.storage_b = ezfunctions.vlan_list_format(sorted(
                [pargs.vlan.nfs, pargs.vlan.iscsi[1], pargs.vlan.nvme[1]]))
        else:
            pargs.vlan.storage_a = pargs.vlan.nfs
            pargs.vlan.storage_b = pargs.vlan.nfs
        plist = ['mgmt', 'migration', 'storage-a', 'storage-b', 'all_vlans']
        for i in plist:
            if re.search('(mgmt|migration)', i) and len(str(pargs.vlan[i])) > 0: nvlan = pargs.vlan[i]
            elif 'storage-a' == i and len(pargs.vlan.iscsi) == 2:
                nvlan = pargs.vlan.iscsi[0]
            elif 'storage-b' == i and len(pargs.vlan.iscsi) == 2:
                nvlan = pargs.vlan.iscsi[1]
            else: nvlan = 1
            vlan_name = i.replace('-', '_')
            polVars = dict(
                allowed_vlans = f'{pargs.vlan[vlan_name]}',
                description   = f'{pargs.domain.policies.prefix}{i} {descr} Policy',
                name          = f'{pargs.domain.policies.prefix}{i}',
                native_vlan   = nvlan,
            )
            
            # Add Policy Variables to immDict
            kwargs['class_path'] = f'policies,{self.type}'
            kwargs = ezfunctions.ez_append(polVars, **kwargs)
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - Build Policy - Ethernet QoS
    #=============================================================================
    def ethernet_qos(self, pargs, **kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        plist = ['Best Effort', 'Bronze', 'Gold', 'Platinum', 'Silver']
        for i in plist:
            name = i.replace(' ', '-')
            polVars = dict(
                enable_trust_host_cos = False,
                burst        = 10240,
                description  = f'{pargs.domain.policies.prefix}{name} {descr} Policy',
                name         = f'{pargs.domain.policies.prefix}{name}',
                mtu          = 9000,
                priority     = i,
                rate_limit   = 0,
            )

            # Add Policy Variables to immDict
            kwargs['class_path'] = f'policies,{self.type}'
            kwargs = ezfunctions.ez_append(polVars, **kwargs)
        
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - Build Pools - WWNN/WWPN
    #=============================================================================
    def fc(self, pargs, **kwargs):
        # Build Dictionary
        polVars = dict(
            assignment_order = 'sequential',
            description      = f'{pargs.domain.policies.prefix}wwnn Pool',
            name             = f'{pargs.domain.policies.prefix}wwnn',
            id_blocks        = [{
                'from':f'20:00:00:25:B5:{pargs.domain.pools.prefix}:00:00',
                'size':1024
            }],
        )

        # Add Policy Variables to immDict
        kwargs['class_path'] = f'pools,wwnn'
        kwargs = ezfunctions.ez_append(polVars, **kwargs)

        # Loop through WWPN Pools
        flist = ['A', 'B']
        for i in flist:
            polVars.update(dict(
                description = f'{pargs.domain.policies.prefix}wwpn-{i.lower()} Pool',
                name        = f'{pargs.domain.policies.prefix}wwpn-{i.lower()}',
            ))
            polVars['id_blocks'][0].update({'from':f'20:00:00:25:B5:{pargs.domain.pools.prefix}:{i}0:00'})
            kwargs['class_path'] = f'pools,wwpn'
            kwargs = ezfunctions.ez_append(polVars, **kwargs)
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - Build Policy - FC Zone
    #=============================================================================
    def fc_zone(self, pargs, **kwargs):
        descr = (self.type.replace('_', ' ')).title()
        fabrics = ['a', 'b']
        pargs.fc_zone = []
        for x in range(0,len(fabrics)):
            if len(pargs.domain.vsans) == 2: vsan = pargs.domain.vsans[x]
            else: vsan = pargs.domain.vsans[0]
            name = f'{pargs.domain.policies.prefix}fabric-{fabrics[x]}-vsan-{vsan}'
            # Build Dictionary
            polVars = dict(
                description           = f'{name} {descr} Policy',
                fc_target_zoning_type = 'SIMT',
                name                  = name,
                targets               = [],
            )
            pargs.storage = DotMap(deepcopy(kwargs['immDict']['orgs'][kwargs['org']]['storage']))
            for k, v in pargs.storage.items():
                for e in v:
                    for i in e.wwpns[fabrics[x]]:
                        polVars['targets'].append(dict(
                            name      = e.svm + '-' + i.interface,
                            switch_id = (fabrics[x]).upper(),
                            vsan_id   = vsan,
                            wwpn      = i.wwpn
                        ))
                    pargs.fc_zone.append(polVars['name'])

            # Add Policy Variables to immDict
            kwargs['class_path'] = f'policies,{self.type}'
            kwargs = ezfunctions.ez_append(polVars, **kwargs)
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - Build Policy - Fibre-Channel Adapter
    #=============================================================================
    def fibre_channel_adapter(self, pargs, **kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        plist = ['VMware', 'FCNVMeInitiator']
        for i in plist:
            polVars = dict(
                adapter_template = i,
                description      = f'{pargs.domain.policies.prefix}{i} {descr} Policy',
                name             = f'{pargs.domain.policies.prefix}{i}',
            )

            # Add Policy Variables to immDict
            kwargs['class_path'] = f'policies,{self.type}'
            kwargs = ezfunctions.ez_append(polVars, **kwargs)
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - Build Policy - Fibre-Channel Network
    #=============================================================================
    def fibre_channel_network(self, pargs, **kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        for i in pargs.domain.vsans:
            polVars = dict(
                description = f'{pargs.domain.policies.prefix}vsan-{i} {descr} Policy',
                name        = f'{pargs.domain.policies.prefix}vsan-{i}',
                vsan_id     = i,
            )

            # Add Policy Variables to immDict
            kwargs['class_path'] = f'policies,{self.type}'
            kwargs = ezfunctions.ez_append(polVars, **kwargs)
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - Build Policy - Fibre-Channel QoS
    #=============================================================================
    def fibre_channel_qos(self, pargs, **kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        plist = ['fc-qos']
        for i in plist:
            polVars = dict(
                max_data_field_size = 2112,
                burst               = 10240,
                description         = f'{pargs.domain.policies.prefix}{i} {descr} Policy',
                name                = f'{pargs.domain.policies.prefix}{i}',
                rate_limit          = 0,
            )

            # Add Policy Variables to immDict
            kwargs['class_path'] = f'policies,{self.type}'
            kwargs = ezfunctions.ez_append(polVars, **kwargs)
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - Build Policy - Flow Control
    #=============================================================================
    def flow_control(self, pargs, **kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        polVars = dict(
            description = f'{pargs.domain.policies.prefix}flow-ctrl {descr} Policy',
            name        = f'{pargs.domain.policies.prefix}flow-ctrl',
        )

        # Add Policy Variables to immDict
        kwargs['class_path'] = f'policies,{self.type}'
        kwargs = ezfunctions.ez_append(polVars, **kwargs)
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - Build Policy - IMC Access
    #=============================================================================
    def imc_access(self, pargs, **kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        polVars = dict(
            description         = f'{pargs.domain.policies.prefix}kvm {descr} Policy',
            inband_ip_pool      = f'kvm-inband',
            inband_vlan_id      = pargs.inband.vlan_id,
            out_of_band_ip_pool = 'kvm-ooband',
            name                = f'{pargs.domain.policies.prefix}kvm',
        )

        # Add Policy Variables to immDict
        kwargs['class_path'] = f'policies,{self.type}'
        kwargs = ezfunctions.ez_append(polVars, **kwargs)
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - Build Pools - IP
    #=============================================================================
    def ip(self, pargs, **kwargs):
        pdns = pargs.dns_servers[0]
        sdns = ''
        if len(pargs.dns_servers) >= 2: sdns = pargs.dns_servers[1]
        # Build Dictionary
        for i in pargs.vlans:
            if re.search('(inband|iscsi|ooband)', i.vlan_type):
                if not pargs.pools.ip.get(i.vlan_type):
                    pargs.pools.ip[i.vlan_type] = []
                if re.search('inband|ooband', i.vlan_type):
                    name = f'{pargs.domain.policies.prefix}kvm-{i.vlan_type}'
                    pool_from = deepcopy(i.pool[0])
                    pool_to   = deepcopy(i.pool[-1])
                else:
                    name = f'{pargs.domain.policies.prefix}iscsi-vlan{i.vlan_id}'
                    pool_from = deepcopy(i.server[0])
                    pool_to   = deepcopy(i.server[-1])
                kwargs['defaultGateway'] = deepcopy(i.gateway)
                kwargs['subnetMask']     = deepcopy(i.netmask)
                kwargs['ip_version']     = 'v4'
                kwargs['pool_from']      = pool_from
                kwargs['pool_to']        = pool_to
                validating.error_subnet_check(**kwargs)
                size = int(ipaddress.IPv4Address(pool_to)) - int(ipaddress.IPv4Address(pool_from)) + 1
                polVars = dict(
                    assignment_order = 'sequential',
                    description      = f'{name} IP Pool',
                    name             = f'{name}',
                    ipv4_blocks      = [{
                        'from':pool_from,
                        'size':size
                    }],
                    ipv4_configuration = [dict(
                        gateway       = i.gateway,
                        netmask       = i.netmask,
                        primary_dns   = pdns,
                        secondary_dns = sdns
                    )],
                )
                pargs.pools.ip[i.vlan_type].append(polVars['name'])
                # Add Policy Variables to immDict
                kwargs['class_path'] = f'pools,{self.type}'
                kwargs = ezfunctions.ez_append(polVars, **kwargs)
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - Build Pools - IQN
    #=============================================================================
    def iqn(self, pargs, **kwargs):
        # Build Dictionary
        polVars = dict(
            assignment_order = 'sequential',
            description      = f'{pargs.domain.policies.prefix}iscsi IQN Pool',
            name             = f'{pargs.domain.policies.prefix}iscsi',
            prefix           = f'iqn.1984-12.com.cisco',
            iqn_blocks       = [{
                'from': 0,
                'size': 1024,
                'suffix': 'ucs-host'
            }],
        )

        # Add Policy Variables to immDict
        kwargs['class_path'] = f'pools,{self.type}'
        kwargs = ezfunctions.ez_append(polVars, **kwargs)
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - Build Policy - IPMI over LAN
    #=============================================================================
    def ipmi_over_lan(self, pargs, **kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        polVars = dict(
            description = f'{pargs.domain.policies.prefix}ipmi {descr} Policy',
            name        = f'{pargs.domain.policies.prefix}ipmi',
        )

        # Add Policy Variables to immDict
        kwargs['class_path'] = f'policies,{self.type}'
        kwargs = ezfunctions.ez_append(polVars, **kwargs)
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - Build Policy - iSCSI Adapter
    #=============================================================================
    def iscsi_adapter(self, pargs, **kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        polVars = dict(
            description            = f'{pargs.domain.policies.prefix}iadapter {descr} Policy',
            dhcp_timeout           = 60,
            name                   = f'{pargs.domain.policies.prefix}iadapter',
            lun_busy_retry_count   = 15,
            tcp_connection_timeout = 15,
        )

        # Add Policy Variables to immDict
        kwargs['class_path'] = f'policies,{self.type}'
        kwargs = ezfunctions.ez_append(polVars, **kwargs)
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - Build Policy - iSCSI Boot
    #=============================================================================
    def iscsi_boot(self, pargs, **kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        fabrics = ['a', 'b']
        list_of_list = []
        for i in range(0, len(pargs.iscsi.targets), 2): list_of_list.append(pargs.iscsi.targets[i:i+2])
        #half = pargs.iscsi.targets // 2
        pargs.a.targets  = list_of_list[0]
        pargs.b.targets  = list_of_list[1]
        pargs.iscsi.boot = []
        for x in range(0,len(fabrics)):
            pool = deepcopy(pargs.pools.ip['iscsi'][x])
            polVars = dict(
                description             = f'{pargs.domain.policies.prefix}{pool} {descr} Policy',
                initiator_ip_source     = 'Pool',
                initiator_ip_pool       = pargs.pools.ip['iscsi'][x], 
                iscsi_adapter_policy    = f'{pargs.domain.policies.prefix}iadapter',
                name                    = f'{pargs.domain.policies.prefix}{pool}',
                primary_target_policy   = pargs[fabrics[x]].targets[0],
                secondary_target_policy = pargs[fabrics[x]].targets[1],
                target_source_type      = f'Static',
            )
            pargs.iscsi.boot.append(polVars['name'])

            # Add Policy Variables to immDict
            kwargs['class_path'] = f'policies,{self.type}'
            kwargs = ezfunctions.ez_append(polVars, **kwargs)
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - Build Policy - iSCSI Target
    #=============================================================================
    def iscsi_static_target(self, pargs, **kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        pargs.iscsi.targets = []
        pargs.storage = DotMap(deepcopy(kwargs['immDict']['orgs'][kwargs['org']]['storage']))
        for k, v in pargs.storage.items():
            for e in v:
                for i in e['iscsi']['interfaces']:
                    i = DotMap(deepcopy(i))
                    name = e.svm + ':' + i.interface
                    polVars = dict(
                        description = f'{name} {descr} Policy',
                        ip_address  = i.ip_address,
                        luns        = [{
                            'bootable':True,
                            'lun_id':0
                        }],
                        name        = f'{name}',
                        port        = 3260,
                        target_name = v[0]['iscsi']['iqn'],
                    )
                    pargs.iscsi.targets.append(name)
                    
                    # Add Policy Variables to immDict
                    kwargs['class_path'] = f'policies,{self.type}'
                    kwargs = ezfunctions.ez_append(polVars, **kwargs)
       
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - Build Policy - LAN Connectivity
    #=============================================================================
    def lan_connectivity(self, pargs, **kwargs):
        # Build Dictionary
        vic_gen = []
        for k, v in pargs.servers.items(): vic_gen.append(f'{v.vic}')
        vic_gen = list(numpy.unique(numpy.array(vic_gen)))
        lan_policies = ['lcp']
        for i in pargs.vlans:
            i = DotMap(deepcopy(i))
            if i.vlan_type == 'iscsi':
                lan_policies.append('lcp-iscsi')
                break
        for g in vic_gen:
            for lcp in lan_policies:
                descr     = (self.type.replace('_', ' ')).title()
                pci_order = deepcopy(pargs.pci_order)
                polVars = dict(
                    description          = f'{pargs.domain.policies.prefix}vic-{g}-{lcp} {descr} Policy',
                    iqn_pool             = '',
                    name                 = f'{pargs.domain.policies.prefix}vic-{g}-{lcp}',
                    target_platform      = 'FIAttached',
                    vnics                = [],
                )
                if re.search('iscsi', lcp):
                    polVars['iqn_pool'] = f'{pargs.domain.policies.prefix}iscsi'
                else: polVars.pop('iqn_pool')
                plist = ['mgmt-Silver', 'migration-Bronze', 'storage-Platinum', 'dvs-Gold']
                vnic_count = 0
                for i in plist:
                    vname = i.split('-')[0]
                    pqos  = i.split('-')[1]
                    if 'dvs' in vname: pgroups = ['all_vlans']
                    elif 'storage' in vname: pgroups = [f'{vname}-a', f'{vname}-b']
                    else: pgroups = [vname]
                    if re.search('(dvs|migration)', i): adapter_policy = 'VMware-High-Trf'
                    elif 'storage' in i and g == 'gen4': adapter_policy = '16RxQs-4G'
                    elif 'storage' in i and g == 'gen5': adapter_policy = '16RxQs-5G'
                    else: adapter_policy = 'VMware'
                    polVars['vnics'].append(dict(
                        ethernet_adapter_policy         = adapter_policy,
                        ethernet_network_control_policy = 'cdp',
                        ethernet_network_group_policies = pgroups,
                        ethernet_qos_policy             = pqos,
                        iscsi_boot_policies             = [],
                        names                           = [f'{vname}-a', f'{vname}-b'],
                        mac_address_pools               = [f'{vname}-a', f'{vname}-b'],
                        placement_pci_order             = [pci_order, pci_order + 1],
                    ))
                    if 'storage' in vname and 'iscsi' in lcp:
                        polVars['vnics'][vnic_count].update({'iscsi_boot_policies': pargs.iscsi.boot})
                    else: polVars['vnics'][vnic_count].pop('iscsi_boot_policies')
                    pci_order += 2
                    vnic_count += 1
                
                # Add Policy Variables to immDict
                kwargs['class_path'] = f'policies,{self.type}'
                kwargs = ezfunctions.ez_append(polVars, **kwargs)
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        pargs.pci_order = pci_order
        return kwargs, pargs


    #=============================================================================
    # Function - Build Policy - Link Aggregation
    #=============================================================================
    def link_aggregation(self, pargs, **kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        polVars = dict(
            description = f'{pargs.domain.policies.prefix}link-agg {descr} Policy',
            name        = f'{pargs.domain.policies.prefix}link-agg',
        )

        # Add Policy Variables to immDict
        kwargs['class_path'] = f'policies,{self.type}'
        kwargs = ezfunctions.ez_append(polVars, **kwargs)
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - Build Policy - Link Control
    #=============================================================================
    def link_control(self, pargs, **kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        polVars = dict(
            description = f'{pargs.domain.policies.prefix}link-ctrl {descr} Policy',
            name        = f'{pargs.domain.policies.prefix}link-ctrl',
        )

        # Add Policy Variables to immDict
        kwargs['class_path'] = f'policies,{self.type}'
        kwargs = ezfunctions.ez_append(polVars, **kwargs)
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - Build Policy - Local User
    #=============================================================================
    def local_user(self, pargs, **kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        polVars = dict(
            description = f'{pargs.domain.policies.prefix}users {descr} Policy',
            name        = f'{pargs.domain.policies.prefix}users',
            users       = [dict(
                enabled  = True,
                password = 1,
                role     = 'admin',
                username = pargs.domain.policies.local_user
            )]
        )

        # Add Policy Variables to immDict
        kwargs['class_path'] = f'policies,{self.type}'
        kwargs = ezfunctions.ez_append(polVars, **kwargs)
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - Build Pools - MAC
    #=============================================================================
    def mac(self, pargs, **kwargs):
        # Build Dictionary
        flist = ['a', 'b']
        nlist = ['1-2-dvs', 'A-B-mgmt', 'C-D-migration', 'E-F-storage', ]
        for i in nlist:
            for x in range(0,len(flist)):
                n = i.split('-')
                pool = n[2]
                polVars = dict(
                    assignment_order = 'sequential',
                    description      = f'{pargs.domain.policies.prefix}{pool}-{flist[x]} Pool',
                    name             = f'{pargs.domain.policies.prefix}{pool}-{flist[x]}',
                    mac_blocks       = [{
                        'from':f'00:25:B5:{pargs.domain.pools.prefix}:{n[x]}0:00',
                        'size':1024
                    }],
                )

                # Add Policy Variables to immDict
                kwargs['class_path'] = f'pools,{self.type}'
                kwargs = ezfunctions.ez_append(polVars, **kwargs)
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - Build Policy - Multicast
    #=============================================================================
    def multicast(self, pargs, **kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        polVars = dict(
            description = f'{pargs.domain.policies.prefix}mcast {descr} Policy',
            name        = f'{pargs.domain.policies.prefix}mcast',
        )

        # Add Policy Variables to immDict
        kwargs['class_path'] = f'policies,{self.type}'
        kwargs = ezfunctions.ez_append(polVars, **kwargs)
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - Build Policy - Network Connectivity
    #=============================================================================
    def network_connectivity(self, pargs, **kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        polVars = dict(
            description    = f'{pargs.domain.policies.prefix}dns {descr} Policy',
            name           = f'{pargs.domain.policies.prefix}dns',
            dns_servers_v4 = pargs.dns_servers,
        )

        # Add Policy Variables to immDict
        kwargs['class_path'] = f'policies,network_connectivity'
        kwargs = ezfunctions.ez_append(polVars, **kwargs)
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - Build Policy - NTP
    #=============================================================================
    def ntp(self, pargs, **kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        polVars = dict(
            description = f'{pargs.domain.policies.prefix}ntp {descr} Policy',
            name        = f'{pargs.domain.policies.prefix}ntp',
            ntp_servers = pargs.ntp_servers,
            timezone    = pargs.timezone,
        )

        # Add Policy Variables to immDict
        kwargs['class_path'] = f'policies,ntp'
        kwargs = ezfunctions.ez_append(polVars, **kwargs)
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - Build Policy - Port
    #=============================================================================
    def port(self, pargs, **kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        ports = []
        for i in pargs.domain.eth_uplinks:
            ports.append({'port_id':int(i.split('/')[-1])})
        x = str(pargs.domain.eth_uplinks[0]).split('/')
        if len(x) == 3: pc_id = '1' + x[1] + x[2]
        else: pc_id = x[-1]
        pc_id = int(pc_id)
        polVars = dict(
            description  = f'{pargs.domain.name} {descr} Policy',
            device_model = pargs.domain.device_model,
            names        = [f'{pargs.domain.name}-A', f'{pargs.domain.name}-B'],
            port_channel_ethernet_uplinks = [dict(
                admin_speed                   = 'Auto',
                ethernet_network_group_policy = f'{pargs.domain.policies.prefix}all_vlans',
                flow_control_policy           = f'{pargs.domain.policies.prefix}flow-ctrl',
                interfaces                    = ports,
                link_aggregation_policy       = f'{pargs.domain.policies.prefix}link-agg',
                link_control_policy           = f'{pargs.domain.policies.prefix}link-ctrl',
                pc_ids                        = [pc_id, pc_id],
            )]
        )
        if re.search('(fc|fc-nvme)', pargs.dtype):
            ports= []
            x    = pargs.domain.fcp_uplink_ports[0].split('/')
            for i in pargs.domain.fcp_uplink_ports:
                ports.append({'port_id':int(i.split('/')[-1])})
            if pargs.swmode == 'end-host':
                if len(x) == 3: pc_id = '1' + x[1] + x[2]
                else: pc_id = x[-1]
                polVars.update(dict(
                    port_channel_fc_uplinks = [dict(
                        admin_speed  = pargs.domain.fcp_uplink_speed,
                        fill_pattern = 'Idle',
                        interfaces   = ports,
                        pc_ids       = [pc_id, pc_id],
                        vsan_ids     = pargs.domain.vsans
                    )]
                ))
                if len(x) == 3:
                    for i in polVars['port_channel_fc_uplinks']['interfaces']:
                        i.update({'breakout_port_id':x[2]})
            else:
                ports = x[-1]
                polVars.update(dict(
                    port_role_fc_storage = [dict(
                        admin_speed  = pargs.domain.fcp_uplink_speed,
                        port_list    = ports,
                        vsan_ids     = pargs.domain.vsans
                    )]
                ))
                if len(x) == 3:
                    polVars['port_role_fc_storage'].update({'breakout_port_id':x[2]})
            if len(x) == 3:
                port_start = int(pargs.domain.fcp_uplink_ports[0].split('/')[-2])
                port_end   = int(pargs.domain.fcp_uplink_ports[-1].split('/')[-2])
                polVars.update(dict(
                    port_modes = [dict(
                        custom_mode = f'BreakoutFibreChannel{pargs.breakout_speed.fc}',
                        port_list   = [port_start, port_end]
                    )]
                ))
            else:
                port_start = int(pargs.domain.fcp_uplink_ports[0].split('/')[-1])
                port_end   = int(pargs.domain.fcp_uplink_ports[-1].split('/')[-1])
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
        polVars.update({'port_role_servers':[]})
        for i in pargs.domain.profiles:
                if len(i.domain_ports[0].split('/')) == 3:
                    port_start= int(i.domain_ports[0].split('/'))[2]
                    port_end  = int(i.domain_ports[-1].split('/'))[2]
                    polVars['port_modes'].append(dict(
                        custom_mode = f'BreakoutEthernet{pargs.breakout_speed.eth}',
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

        # Add Policy Variables to immDict
        kwargs['class_path'] = f'policies,{self.type}'
        kwargs = ezfunctions.ez_append(polVars, **kwargs)
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - Build Policy - Power
    #=============================================================================
    def power(self, pargs, **kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        power_list = []
        for i in pargs.chassis:
            power_list.append(i)
        power_list.append('server')
        for i in power_list:
            polVars = dict(
                description      = f'{pargs.domain.policies.prefix}{i} {descr} Policy',
                name             = f'{pargs.domain.policies.prefix}{i}',
                power_allocation = 0,
                power_redundancy = 'Grid',
            )
            if i == 'server': polVars.update({'power_restore':'LastState'})
            if '9508' in i: polVars['power_allocation'] = 8400
            else: polVars.pop('power_allocation')

            # Add Policy Variables to immDict
            kwargs['class_path'] = f'policies,{self.type}'
            kwargs = ezfunctions.ez_append(polVars, **kwargs)
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - Build Policy - SAN Connectivity
    #=============================================================================
    def san_connectivity(self, pargs, **kwargs):
        # Build Dictionary
        descr     = (self.type.replace('_', ' ')).title()
        pci_order = pargs.pci_order
        polVars = dict(
            description          = f'{pargs.domain.policies.prefix}scp {descr} Policy',
            name                 = f'{pargs.domain.policies.prefix}scp',
            target_platform      = 'FIAttached',
            vhbas                = [],
            wwnn_allocation_type = 'POOL',
            wwnn_pool            = f'{pargs.domain.policies.prefix}wwnn',
        )
        ncount = 1
        if   pargs.dtype == 'fc': adapter_list = ['VMware']
        elif pargs.dtype == 'fc-nvme': adapter_list = ['VMware', 'FCNVMeInitiator']
        vcount = 0
        network_policies = []
        for v in pargs.domain.vsans:
            network_policies.append(f'vsan-{v}')
        vsans = pargs.domain.vsans
        for x in range(0,len(adapter_list)):
            polVars['vhbas'].append(dict(
                fc_zone_policies               = [],
                fibre_channel_adapter_policy   = adapter_list[x],
                fibre_channel_network_policies = network_policies,
                fibre_channel_qos_policy       = 'fc-qos',
                names                          = [f'vhba{ncount}', f'vhba{ncount + 1}'],
                placement_pci_order            = [pci_order, pci_order + 1],
                wwpn_allocation_type           = 'POOL',
                wwpn_pools                     = [f'wwpn-a', f'wwpn-b'],
            ))
            if 'switch' in pargs.domain.switch_mode:
                polVars['vhbas'][vcount].update({'fc_zone_policies': pargs.fc_zone})
            else: polVars['vhbas'][vcount].pop('fc_zone_policies')
            ncount += 2
            vcount += 1
            pci_order += 2
            
            # Add Policy Variables to immDict
            kwargs['class_path'] = f'policies,{self.type}'
            kwargs = ezfunctions.ez_append(polVars, **kwargs)
        
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - Build Policy - Serial over LAN
    #=============================================================================
    def serial_over_lan(self, pargs, **kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        polVars = dict(
            description = f'{pargs.domain.policies.prefix}sol {descr} Policy',
            name        = f'{pargs.domain.policies.prefix}sol',
        )

        # Add Policy Variables to immDict
        kwargs['class_path'] = f'policies,{self.type}'
        kwargs = ezfunctions.ez_append(polVars, **kwargs)
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - Build Profiles - Server
    #=============================================================================
    def server(self, pargs, **kwargs):
        #=====================================================
        # Server Profile IP settings Function
        #=====================================================
        def server_profile_networks(name, p, pargs):
            #=====================================================
            # Send Error Message if IP Range isn't long enough
            #=====================================================
            def error_ip_range(i):
                prRed(f'!!!ERROR!!!\nNot Enough IPs in Range {i.server} for {name}')
                sys.exit(1)

            #=====================================================
            # Send Error Message if Server Range is missing
            #=====================================================
            def error_server_range(i):
                prRed(f'!!!ERROR!!!\nDid Not Find Server IP Range defined for {i.vlan_type}:{i.name}:{i.vlan_id}')
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
            ipindex = pargs.inband.server.index(p.inband_start)
            if 'compute.Blade' in pargs.server_profiles[name].object_type:
                ipindex = ipindex + int(pargs.server_profiles[name].slot) - 1

            #=====================================================
            # Loop thru the VLANs
            #=====================================================
            for i in pargs.vlans:
                i = DotMap(deepcopy(i))
                if re.search('(inband|iscsi|migration|nfs|nvme)', i.vlan_type):
                    if not i.server: error_server_range(i)
                    if not len(i.server) >= ipindex: error_ip_range(i)
                if re.search('(iscsi|nvme)', i.vlan_type):
                    if not pargs.server_profiles[name].get(i.vlan_type):
                        pargs.server_profiles[name].update({i.vlan_type:[]})
                    idict = ipdict(i, ipindex)
                    pargs.server_profiles[name][i.vlan_type].append(idict)
                if re.search('(inband|migration|nfs)', i.vlan_type):
                    idict = ipdict(i, ipindex)
                    pargs.server_profiles[name][i.vlan_type] = idict
            return pargs
        
        #=====================================================
        # Build Server Profiles
        #=====================================================
        if 'fc' in pargs.dtype: t = 'fcp'
        else: t = 'iscsi'
        templates = []
        for k, v in pargs.servers.items():
            templates.append(v.template)
        templates = numpy.unique(numpy.array(templates))
        for template in templates:
            polVars = dict(
                action                     = 'Deploy',
                create_from_template       = True,
                targets                    = [],
                ucs_server_profile_template= template + f'-{t}'
            )
            for k,v in pargs.servers.items():
                if template == v.template:
                    if v.object_type == 'compute.Blade':
                        equipment_type= 'Chassis'
                        identifier    = v.chassis_id
                    else:
                        equipment_type= 'RackServer'
                        identifier    = v.server_id
                    for p in pargs.domain.profiles:
                        if equipment_type == p.equipment_type and int(identifier) == int(p.identifier):
                            if equipment_type == 'RackServer':
                                pstart = p.profile_start
                            else:
                                suffix = int(p.suffix_digits)
                                pprefix= p.profile_start[:-(suffix)]
                                pstart = int(p.profile_start[-(suffix):])
                            break
                    if equipment_type == 'RackServer': name = pstart
                    else: name = f"{pprefix}{str(pstart+v.slot-1).zfill(suffix)}"

                    if template == template:
                        polVars['targets'].append(dict(
                            description  = f"{name} Server Profile.",
                            name         = name,
                            serial_number= k
                        ))
                        pargs.server_profiles[name] = v
                        pargs = server_profile_networks(name, p, pargs)
                    
            polVars['targets']  = sorted(polVars['targets'], key=lambda item: item['name'])
            kwargs['class_path']= f'profiles,{self.type}'
            kwargs = ezfunctions.ez_append(polVars, **kwargs)
        
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - Build Policy - SNMP
    #=============================================================================
    def snmp(self, pargs, **kwargs):
        # Build Dictionary
        polVars = dict(
            description     = f'{pargs.domain.policies.prefix}snmp Policy',
            enable_snmp     = True,
            name            = f'{pargs.domain.policies.prefix}snmp',
            snmp_traps      = [],
            snmp_users      = [dict(
                auth_password    = 1,
                auth_type        = 'SHA',
                name             = pargs.domain.policies.snmp.username,
                privacy_password = 1,
                privacy_type     = 'AES',
                security_level   = 'AuthPriv'
            )],
            system_contact  = pargs.domain.policies.snmp.contact,
            system_location = pargs.domain.policies.snmp.location,
        )
        for i in pargs.domain.policies.snmp.servers:
            polVars['snmp_traps'].append(dict(
                destination_address = i,
                port                = 162,
                user                = pargs.domain.policies.snmp.username
            ))

        # Add Policy Variables to immDict
        kwargs['class_path'] = f'policies,snmp'
        kwargs = ezfunctions.ez_append(polVars, **kwargs)
        polVars.update({
            'description':f'{pargs.domain.policies.prefix}snmp-domain Policy',
            'name':f'{pargs.domain.policies.prefix}snmp-domain'
        })
        kwargs['class_path'] = f'policies,snmp'
        kwargs = ezfunctions.ez_append(polVars, **kwargs)
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - Build Policy - Storage
    #=============================================================================
    def storage(self, pargs, **kwargs):
        return kwargs, pargs
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        plist = ['9508', 'Server']
        for i in plist:
            polVars = dict(
                description      = f'{pargs.domain.policies.prefix}{i} {descr} Policy',
                name             = f'{pargs.domain.policies.prefix}{i}',
                power_allocation = 8400,
                power_redundancy = 'Grid',
            )
            if i == 'Server': polVars.update({'power_restore':'LastState'})

            # Add Policy Variables to immDict
            kwargs['class_path'] = f'policies,{self.type}'
            kwargs = ezfunctions.ez_append(polVars, **kwargs)
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - Build Policy - Switch Control
    #=============================================================================
    def switch_control(self, pargs, **kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        if 'fc' in pargs.dtype: switch_mode = pargs.domain.switch_mode
        else: switch_mode = 'end-host'
        polVars = dict(
            description       = f'{pargs.domain.policies.prefix}sw-ctrl {descr} Policy',
            fc_switching_mode = switch_mode,
            name              = f'{pargs.domain.policies.prefix}sw-ctrl',
            vlan_port_count_optimization = True,
        )

        # Add Policy Variables to immDict
        kwargs['class_path'] = f'policies,switch_control'
        kwargs = ezfunctions.ez_append(polVars, **kwargs)
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - Build Policy - Syslog
    #=============================================================================
    def syslog(self, pargs, **kwargs):
        # Build Dictionary
        polVars = dict(
            description = f'{pargs.domain.policies.prefix}syslog Policy',
            local_logging = dict(
                minimum_severity = 'warning',
            ),
            name            = f'{pargs.domain.policies.prefix}syslog',
            remote_logging      = [],
        )
        for i in pargs.domain.policies.syslog.servers:
            polVars['remote_logging'].append(dict(
                enable           = True,
                hostname         = i,
                minimum_severity = 'informational',
            ))

        # Add Policy Variables to immDict
        kwargs['class_path'] = f'policies,syslog'
        kwargs = ezfunctions.ez_append(polVars, **kwargs)
        polVars.update({
            'description':f'{pargs.domain.policies.prefix}syslog-domain Policy',
            'name':f'{pargs.domain.policies.prefix}syslog-domain'
        })
        kwargs['class_path'] = f'policies,syslog'
        kwargs = ezfunctions.ez_append(polVars, **kwargs)
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - Build Policy - System QoS
    #=============================================================================
    def system_qos(self, pargs, **kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        polVars = dict(
            description = f'{pargs.domain.policies.prefix}qos {descr} Policy',
            classes     = [],
            name        = f'{pargs.domain.policies.prefix}qos',
        )
        for k, v in kwargs['ezData']['ezimm']['allOf'][1]['properties']['systemQos'].items():
            cDict = {'priority':k}
            cDict.update(v)
            polVars['classes'].append(cDict)

        # Add Policy Variables to immDict
        kwargs['class_path'] = f'policies,{self.type}'
        kwargs = ezfunctions.ez_append(polVars, **kwargs)
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - Build Templates - Server
    #=============================================================================
    def templates(self, pargs, **kwargs):
        # Build Dictionary
        template_types = []
        server_profiles = []
        for k, v in pargs.servers.items(): server_profiles.append(v.template)
        server_profiles = list(numpy.unique(numpy.array(server_profiles)))
        if 'fc' in pargs.dtype: template_types.append('fcp')
        for i in pargs.vlans:
            i = DotMap(deepcopy(i))
            if i.vlan_type == 'iscsi':
                template_types.append('iscsi')
        template_types = list(numpy.unique(numpy.array(template_types)))
        for t in template_types:
            for p in server_profiles:
                bios_policy = p.split('-vic')[0] + '-virtual'
                bios_policy = bios_policy.replace('-tpm', '')
                if 'tpm' in p:
                    bios_policy = bios_policy + '-tpm'
                name = p + f'-{t}'
                if 'iscsi' in t: lcp = 'vic-' + p.split('vic-')[1] + f'-lcp-iscsi'
                else: lcp = 'vic-' + p.split('vic-')[1] + f'-lcp'
                polVars = dict(
                    bios_policy             = bios_policy,
                    boot_order_policy       = f'{pargs.domain.policies.prefix}{t}-boot',
                    description             = f'{name} Server Template',
                    imc_access_policy       = f'{pargs.domain.policies.prefix}kvm',
                    lan_connectivity_policy = f'{pargs.domain.policies.prefix}{lcp}',
                    local_user_policy       = f'{pargs.domain.policies.prefix}users',
                    name                    = name,
                    power_policy            = f'{pargs.domain.policies.prefix}server',
                    san_connectivity_policy = f'',
                    serial_over_lan_policy  = f'{pargs.domain.policies.prefix}sol',
                    snmp_policy             = f'{pargs.domain.policies.prefix}snmp',
                    syslog_policy           = f'{pargs.domain.policies.prefix}syslog',
                    uuid_pool               = f'{pargs.domain.policies.prefix}uuid',
                    virtual_kvm_policy      = f'{pargs.domain.policies.prefix}vkvm',
                    virtual_media_policy    = f'{pargs.domain.policies.prefix}vmedia',
                )
                if 'M5' in p: polVars.pop('power_policy')
                if 'fcp' in t: polVars.update({'san_connectivity_policy': f'{pargs.domain.policies.prefix}scp'})
                else: polVars.pop('san_connectivity_policy')
                
                # Add Policy Variables to immDict
                kwargs['class_path'] = f'{self.type},server'
                kwargs = ezfunctions.ez_append(polVars, **kwargs)
        
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - Build Policy - Thermal
    #=============================================================================
    def thermal(self, pargs, **kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        for i in pargs.chassis:
            polVars = dict(
                fan_control_mode = 'Balanced',
                description      = f'{pargs.domain.policies.prefix}{i} {descr} Policy',
                name             = f'{pargs.domain.policies.prefix}{i}',
            )

            # Add Policy Variables to immDict
            kwargs['class_path'] = f'policies,{self.type}'
            kwargs = ezfunctions.ez_append(polVars, **kwargs)
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - Build Pools - MAC
    #=============================================================================
    def uuid(self, pargs, **kwargs):
        # Build Dictionary
        polVars = dict(
            assignment_order = 'sequential',
            description      = f'{pargs.domain.policies.prefix}uuid Pool',
            name             = f'{pargs.domain.policies.prefix}uuid',
            prefix           = '000025B5-0000-0000',
            uuid_blocks      = [{
                'from':f'{pargs.domain.pools.prefix}00-000000000000',
                'size':1024
            }],
        )

        # Add Policy Variables to immDict
        kwargs['class_path'] = f'pools,{self.type}'
        kwargs = ezfunctions.ez_append(polVars, **kwargs)
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - Build Policy - Virtual KVM
    #=============================================================================
    def virtual_kvm(self, pargs, **kwargs):
        # Build Dictionary
        polVars = dict(
            allow_tunneled_vkvm = True,
            description         = f'{pargs.domain.policies.prefix}vkvm Virtual KVM Policy',
            name                = f'{pargs.domain.policies.prefix}vkvm',
        )

        # Add Policy Variables to immDict
        kwargs['class_path'] = f'policies,{self.type}'
        kwargs = ezfunctions.ez_append(polVars, **kwargs)
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - Build Policy - Virtual Media
    #=============================================================================
    def virtual_media(self, pargs, **kwargs):
        descr = (self.type.replace('_', ' ')).title()
        # Build Dictionary
        polVars = dict(
            description         = f'{pargs.domain.policies.prefix}vmedia {descr} Policy',
            name                = f'{pargs.domain.policies.prefix}vmedia',
        )

        # Add Policy Variables to immDict
        kwargs['class_path'] = f'policies,{self.type}'
        kwargs = ezfunctions.ez_append(polVars, **kwargs)
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - Build Policy - VLAN
    #=============================================================================
    def vlan(self, pargs, **kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).upper()
        polVars = dict(
            description = f'{pargs.domain.policies.prefix}vlans {descr} Policy',
            name        = f'{pargs.domain.policies.prefix}vlans',
            vlans       = [dict(
                auto_allow_on_uplinks = True,
                multicast_policy      = 'mcast',
                name                  = 'default',
                native_vlan           = True,
                vlan_list             = 1
            )]
        )
        for i in pargs.vlans:
            if not int(i['vlan_id']) == 1:
                polVars['vlans'].append(dict(
                    multicast_policy = 'mcast',
                    name             = i['name'],
                    vlan_list        = i['vlan_id']
                ))
        for i in pargs.ranges:
            vfull = ezfunctions.vlan_list_full(i['vlan_list'])
            if 1 in vfull: vfull.remove(1)
            vlan_list = ezfunctions.vlan_list_format(vfull)
            polVars['vlans'].append(dict(
                multicast_policy = 'mcast',
                name             = i['name'],
                vlan_list        = vlan_list
            ))
        # Add Policy Variables to immDict
        kwargs['class_path'] = f'policies,{self.type}'
        kwargs = ezfunctions.ez_append(polVars, **kwargs)
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - Build Policy - VSAN
    #=============================================================================
    def vsan(self, pargs, **kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).upper()
        if pargs.swmode == 'end-host': vsan_scope = 'Uplink'
        else: vsan_scope = 'Storage'
        for i in pargs.vsans:
            polVars = dict(
                description = f'{pargs.domain.policies.prefix}vsan-{i} {descr} Policy',
                name        = f'{pargs.domain.policies.prefix}vsan-{i}',
                vsans       = [dict(
                    fcoe_vlan_id = i,
                    name         = f'{pargs.domain.policies.prefix}vsan-{i}',
                    vsan_id      = i,
                    vsan_scope   = vsan_scope
                )]
            )

            # Add Policy Variables to immDict
            kwargs['class_path'] = f'policies,{self.type}'
            kwargs = ezfunctions.ez_append(polVars, **kwargs)
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


#=======================================================
# Wizard Class
#=======================================================
class wizard(object):
    def __init__(self, type):
        self.type = type

    #=============================================================================
    # Function - Converged Stack - Build IMM Domain Dictionaries
    #=============================================================================
    def build_imm_domain(self, pargs, **kwargs):
        #==================================
        # Configure Domain Policies
        #==================================
        policy_list = kwargs['ezData']['ezimm']['allOf'][1]['properties']['list_domains']['enum']
        policy_list.remove('domain')
        policy_list.insert(0, 'ethernet_network_group')
        policy_list.sort()
        if not re.search('fc(-nvme)?', pargs.dtype): policy_list.pop('vsan')
        for k, v in pargs.imm.domain.items():
            for i in policy_list:
                pargs.domain = v
                pargs.domain.name = k
                if pargs.domain.policies.prefix == None:
                    pargs.domain.policies.prefix = ''
                kwargs, pargs = eval(f'imm(i).{i}(pargs, **kwargs)')

        #==================================
        # Configure Domain Profiles
        #==================================
        kwargs, pargs = imm('domain').domain(pargs, **kwargs)

        #=====================================================
        # Return kwargs and pargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - Converged Stack - Build IMM Dictionaries
    #=============================================================================
    def build_imm_servers(self, pargs, **kwargs):
        #==================================
        # Configure IMM Pools
        #==================================
        pool_list = list(kwargs['ezData']['pools']['allOf'][1]['properties'].keys())
        pool_list.remove('resource')
        for k, v in pargs.imm.domain.items():
            for i in pool_list:
                pargs.domain = v
                pargs.domain.name = k
                if pargs.domain.policies.prefix == None:
                    pargs.domain.policies.prefix = ''
                kwargs, pargs = eval(f'imm(i).{i}(pargs, **kwargs)')

        #==================================
        # Modify the Policy List
        #==================================
        ezData = kwargs['ezData']['policies']['allOf'][1]['properties']
        policy_list = list(ezData.keys())
        ezData = kwargs['ezData']['ezimm']['allOf'][1]['properties']
        pop_list = ezData['converged.pop_list']['enum']
        for i in pop_list: policy_list.remove(i)
        pop_list = ezData['converged.fc_pop_list']['enum']
        if re.search('fc(-nvme)?', pargs.dtype):
            if pargs.sw_mode == 'end-host': policy_list.remove('fc_zone')
        else:
            for i in pop_list: policy_list.remove(i)

        if 'iscsi_boot' in policy_list:
            policy_list.remove('iscsi_static_target')
            policy_list.insert((policy_list.index('iscsi_boot') - 1), 'iscsi_static_target')
        pop_list = ['ethernet_network_group', 'snmp', 'syslog']
        for i in pop_list:
            if kwargs['immDict']['orgs'].get(kwargs['org']):
                if kwargs['immDict']['orgs'][kwargs['org']].get('policies'):
                    if kwargs['immDict']['orgs'][kwargs['org']]['policies'].get(i):
                        policy_list.remove(i)

        #==================================
        # Configure IMM Policies
        #==================================
        for k, v in pargs.imm.domain.items():
            pargs.domain = v
            pargs.domain.name = k
            if pargs.domain.policies.prefix == None:
                pargs.domain.policies.prefix = ''
            i = 'compute_environment'
            #kwargs, pargs = eval(f"imm(i).{i}(pargs, **kwargs)")
            #print(pargs.servers.toDict())
            #print(pargs.chassis.toDict())
            #exit()
            pargs.servers = DotMap({'FCH21427CHB': {'chassis_id': '1', 'chassis_moid': '63a1ec0d76752d31353e06dd', 'cpu': 'intel', 'domain': 'r142c', 'firmware': '5.1(0.230054)', 'gen': 'M5', 'moid': '63c64eeb76752d3135626948', 'model': 'UCSB-B200-M5', 'object_type': 'compute.Blade', 'serial': 'FCH21427CHB', 'server_id': 0, 'slot': 7, 'template': 'M5-intel-vic-gen4', 'tpm': '', 'vic': 'gen4'}, 'FCH213271VU': {'chassis_id': '1', 'chassis_moid': '63a1ec0d76752d31353e06dd', 'cpu': 'intel', 'domain': 'r142c', 'firmware': '5.1(0.230054)', 'gen': 'M5', 'moid': '63c6513e76752d313562f0cc', 'model': 'UCSB-B200-M5', 'object_type': 'compute.Blade', 'serial': 'FCH213271VU', 'server_id': 0, 'slot': 3, 'template': 'M5-intel-vic-gen4', 'tpm': '', 'vic': 'gen4'}, 'FCH222974YZ': {'chassis_id': '1', 'chassis_moid': '63a1ec0d76752d31353e06dd', 'cpu': 'intel', 'domain': 'r142c', 'firmware': '5.1(0.230054)', 'gen': 'M5', 'moid': '63c6559676752d313564167f', 'model': 'UCSB-B200-M5', 'object_type': 'compute.Blade', 'serial': 'FCH222974YZ', 'server_id': 0, 'slot': 2, 'template': 'M5-intel-vic-gen4', 'tpm': '', 'vic': 'gen4'}, 'FLM2509002F': {'chassis_id': '1', 'chassis_moid': '63a1ec0d76752d31353e06dd', 'cpu': 'intel', 'domain': 'r142c', 'firmware': '5.1(0.230054)', 'gen': 'M5', 'moid': '63c655c476752d31356420ff', 'model': 'UCSB-B200-M5', 'object_type': 'compute.Blade', 'serial': 'FLM2509002F', 'server_id': 0, 'slot': 8, 'template': 'M5-intel-vic-gen4', 'tpm': '', 'vic': 'gen4'}, 'FCH21427JG8': {'chassis_id': '1', 'chassis_moid': '63a1ec0d76752d31353e06dd', 'cpu': 'intel', 'domain': 'r142c', 'firmware': '5.1(0.230054)', 'gen': 'M5', 'moid': '63c65d7276752d313565f3bc', 'model': 'UCSB-B200-M5', 'object_type': 'compute.Blade', 'serial': 'FCH21427JG8', 'server_id': 0, 'slot': 5, 'template': 'M5-intel-vic-gen4', 'tpm': '', 'vic': 'gen4'}, 'FCH243974V2': {'chassis_id': '2', 'chassis_moid': '63a1ec1076752d31353e0780', 'cpu': 'intel', 'domain': 'r142c', 'firmware': '5.1(0.230054)', 'gen': 'M6', 'moid': '63a1ecb176752d31353e3720', 'model': 'UCSX-210C-M6', 'object_type': 'compute.Blade', 'serial': 'FCH243974V2', 'server_id': 0, 'slot': 8, 'template': 'M6-intel-tpm-vic-gen4', 'tpm': '-tpm', 'vic': 'gen4'}, 'FCH24397500': {'chassis_id': '2', 'chassis_moid': '63a1ec1076752d31353e0780', 'cpu': 'intel', 'domain': 'r142c', 'firmware': '5.1(0.230054)', 'gen': 'M6', 'moid': '63a1ecb276752d31353e377d', 'model': 'UCSX-210C-M6', 'object_type': 'compute.Blade', 'serial': 'FCH24397500', 'server_id': 0, 'slot': 7, 'template': 'M6-intel-tpm-vic-gen4', 'tpm': '-tpm', 'vic': 'gen4'}, 'FCH243974WZ': {'chassis_id': '2', 'chassis_moid': '63a1ec1076752d31353e0780', 'cpu': 'intel', 'domain': 'r142c', 'firmware': '5.1(0.230054)', 'gen': 'M6', 'moid': '63a1ed0476752d31353e4938', 'model': 'UCSX-210C-M6', 'object_type': 'compute.Blade', 'serial': 'FCH243974WZ', 'server_id': 0, 'slot': 6, 'template': 'M6-intel-tpm-vic-gen4', 'tpm': '-tpm', 'vic': 'gen4'}})
            pargs.chassis = DotMap({'ucsb-5108-ac2': [{'domain': 'r142c', 'identity': 1, 'serial': 'FOX2528PK0Z'}], 'ucsx-9508': [{'domain': 'r142c', 'identity': 2, 'serial': 'FOX2501P0BF'}]})
            pargs.pci_order = 0
            for i in policy_list:
                kwargs, pargs = eval(f'imm(i).{i}(pargs, **kwargs)')

        pargs.policy_list = policy_list
        #=====================================================
        # Configure Templates/Chassis/Server Profiles
        #=====================================================
        profiles_list = ['templates', 'chassis', 'server']
        for p in profiles_list:
            kwargs, pargs = eval(f'imm(p).{p}(pargs, **kwargs)')
        
        #=====================================================
        # Return kwargs and pargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - Converged Stack - Build Storage Dictionaries
    #=============================================================================
    def build_netapp(self, pargs, **kwargs):
        #=====================================================
        # Build NetApp Dictionaries
        #=====================================================
        plist = ['cluster', 'nodes', 'schedule', 'snmp', 'svm', 'volume']
        plist = ['cluster']
        for k,v in pargs.netapp.cluster.items():
            for i in plist:
                kwargs, pargs = eval(f'netapp.build(i).{i}(pargs, k, v, **kwargs)')
        #==================================
        # Configure NetApp
        #==================================
        plist= ['cluster']
        for i in plist:
            kwargs, pargs = eval(f'netapp.api(i).{i}(pargs, **kwargs)')

        # Add Policy Variables to immDict
        idict = pargs.storage.toDict()
        for k, v in idict.items():
            for a, b in v.items():
                kwargs['class_path'] = f'storage,appliances'
                kwargs = ezfunctions.ez_append(b, **kwargs)

        #=====================================================
        # Return kwargs and pargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - Converged Stack - Credentials - DHCP - DNS - NTP Attributes
    #=============================================================================
    def dns_ntp(self, pargs, **kwargs):
        #=====================================================
        # DHCP, DNS, NTP, Organization
        #=====================================================
        i = DotMap(kwargs['immDict']['wizard']['protocols'][0])
        pargs.dns_servers = i.dns_servers
        pargs.dns_domains = i.dns_domains
        pargs.ntp_servers = i.ntp_servers
        pargs.timezone    = i.timezone
        
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - Converged Stack - IMM Attributes
    #=============================================================================
    def imm(self, pargs, **kwargs):
        #=====================================================
        # Intersight Attributes
        #=====================================================
        for item in kwargs['immDict']['wizard']['intersight']:
            item = DotMap(item)
            pargs.dtype  = item.deployment_type
            pargs.org    = item.organization
            for i in item.domains:
                i = DotMap(i)
                pargs.imm.pool.prefix    = item.pools.prefix
                pargs.imm.policies       = item.policies
                pargs.imm.domain[i.name] = DotMap(
                    eth_breakout_speed = i.eth_breakout_speed,
                    eth_uplinks        = i.eth_uplink_ports,
                    organization       = item.organization,
                    policies           = item.policies,
                    pools              = item.pools,
                    profiles           = i.profiles,
                    serial_numbers     = i.serial_numbers,
                    tags               = kwargs['ezData']['tags']
                )
                #==================================
                # Build Domain Network Dictionary
                #==================================
                fabrics = ['A', 'B']
                for x in range(0,2):
                    pargs.network.imm[f'{i.name}-{fabrics[x]}'] = DotMap(
                        data_ports  = i.eth_uplink_ports,
                        data_speed  = i.eth_uplink_speed,
                        mgmt_port   = i.network.management,
                        network_port= i.network.data[x],
                        port_channel=True
                    )

                #==================================
                # Get Moids for Fabric Switches
                #==================================
                kwargs['org']      = pargs.org
                pargs.apiMethod    = 'get'
                pargs.policy       = 'serial_number'
                pargs.purpose      = 'domain'
                pargs.names        = pargs.imm.domain[i.name].serial_numbers
                kwargs      = isdk.api('serial_number').calls(pargs, **kwargs)
                serial_moids= kwargs['pmoids']
                serial      = pargs.imm.domain[i.name].serial_numbers[0]
                pargs.imm.domain[i.name].device_model     = serial_moids[serial]['model']
                pargs.imm.domain[i.name].registered_device= serial_moids[serial]['registered_device']

                #=====================================================
                # Confirm if Fibre-Channel is in Use
                #=====================================================
                if re.search('(fc|fc-nvme)', pargs.dtype):
                    pargs.imm.domain[i.name].fcp_uplink_ports= i.fcp_uplink_ports
                    pargs.imm.domain[i.name].fcp_uplink_speed= i.fcp_uplink_speed
                    pargs.imm.domain[i.name].switch_mode     = i.switch_mode
                    pargs.imm.domain[i.name].vsans           = i.vsans
        
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - Converged Stack - NetApp Attributes
    #=============================================================================
    def netapp(self, pargs, **kwargs):
        #==================================
        # Build Cluster Dictionary
        #==================================
        pargs.netapp = DotMap(cluster = DotMap())
        pargs.storage = DotMap()
        for item in kwargs['immDict']['wizard']['netapp']:
            item = deepcopy(DotMap(item))
            for i in item.clusters:
                pargs.storage[i.name][i.svm.name] = DotMap(
                    cluster= i.name,
                    name   = f"{i.name}:{i.svm.name}",
                    svm    = i.svm.name,
                    vendor = 'netapp'
                )
                cname = i.name
                sname = i.svm.name
                rootv = (i.svm.name).replace('-', '_').lower() + '_root'
                pargs.netapp.cluster[cname] = DotMap(
                    autosupport= item.autosupport,
                    banner     = item.login_banner,
                    host_prompt= r'[\w]+::>',
                    nodes      = i.nodes,
                    protocols  = pargs.protocols,
                    snmp       = item.snmp,
                    svm        = DotMap(
                        agg1     = i.nodes.node01.replace('-', '_').lower() + '_1',
                        agg2     = i.nodes.node02.replace('-', '_').lower() + '_1',
                        name     = i.svm.name,
                        m01      = rootv + '_m01',
                        m02      = rootv + '_m02',
                        protocols= pargs.protocols,
                        rootv    = rootv,
                        volumes  = i.svm.volumes
                    ),
                    username = item.username
                )
                pargs.netapp.cluster[cname].nodes.node_list = [i.nodes.node01, i.nodes.node02]
                #==================================
                # Build Cluster Network Dictionary
                #==================================
                nodes = pargs.netapp.cluster[cname].nodes.node_list
                for x in range(0,len(nodes)):
                    pargs.network.storage[nodes[x]] = DotMap(
                        data_ports  = i.nodes.data_ports,
                        data_speed  = i.nodes.data_speed,
                        mgmt_port   = i.nodes.network.management,
                        network_port= i.nodes.network.data[x],
                        port_channel=True
                    )
        
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - Build Server Identies for Zoning host/igroups
    #=============================================================================
    def server_identities(self, pargs, **kwargs):
        # Get Variables from Library
        smap = deepcopy(kwargs['immDict']['orgs'][kwargs['org']]['profiles']['server'])
        #=====================================================
        # Get Server Profile Names and Moids
        #=====================================================
        pargs.names = []
        for item in smap:
            for i in item['targets']: pargs.names.append(i['name'])
        pargs.names.sort()
        pargs.apiMethod = 'get'
        pargs.policy    = 'server'
        pargs.purpose   = 'server'
        kwargs = isdk.api('server').calls(pargs, **kwargs)
        pargs.sDict = kwargs['results']
        if 'fc' in pargs.dtype:
            #=====================================================
            # Get WWPN's for vHBAs and Add to Profile Map
            #=====================================================
            for k, v in kwargs['pmoids'].items():
                pargs.apiMethod = 'get'
                pargs.apiFilter  = f"Profile.Moid eq '{v['Moid']}'"
                pargs.policy    = 'vhbas'
                pargs.purpose   = 'vhbas'
                kwargs = isdk.api(pargs.policy).calls(pargs, **kwargs)
                r = kwargs['results']
                pargs.server_profiles[k]['wwpns'] = {}
                for s in r: pargs.server_profiles[k]['wwpns'].update({s['Name']:s['Wwpn']})
                pargs.policy    = 'vnics'
                pargs.purpose   = 'vnics'
                kwargs = isdk.api(pargs.policy).calls(pargs, **kwargs)
                r = kwargs['results']
                pargs.server_profiles[k]['macs'] = {}
                for s in r: pargs.server_profiles[k]['macs'].update({s['Name']:s['MacAddress']})
        elif re.search('(iscsi|nvme-tcp)', pargs.dtype):
            #=====================================================
            # Get WWPN's for vHBAs and Add to Profile Map
            #=====================================================
            for k, v in kwargs['pmoids'].items():
                pargs.apiMethod = 'get'
                pargs.apiFilter  = f"AssignedToEntity.Moid eq '{v['Moid']}'"
                pargs.policy    = 'iqn'
                pargs.purpose   = 'iqn'
                kwargs = isdk.api(pargs.policy).calls(pargs, **kwargs)
                r = kwargs['results']
                pargs.server_profiles[k].iqn = r['IqnId']
        pargs.pop('apiFilter')
        #=====================================================
        # Run Lun Creation Class
        #=====================================================
        netapp.build('lun').lun(pargs, **kwargs)
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - Converged Stack - VLAN Attributes
    #=============================================================================
    def vlans(self, pargs, **kwargs):
        protocols   = []
        pargs.vlans = []
        for i in kwargs['immDict']['wizard']['vlans']:
            #==================================
            # Add i.type to protocols
            #==================================
            i = DotMap(deepcopy(i))
            if re.search('(iscsi|nfs|nvme)', i.vlan_type):
                if 'nvme' in i.vlan_type: protocols.append('nvme_of')
                else: protocols.append(i.vlan_type)

            #==================================
            # Build VLAN Dictionary
            #==================================
            netwk = '%s' % ipaddress.IPv4Network(i.network, strict=False)
            vDict = DotMap(
                configure_l2= i.configure_l2,
                configure_l3= i.configure_l3,
                gateway     = i.network.split('/')[0],
                name        = i.name,
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
            pargs.vlans.append(vDict)

        #==================================
        # Build VLAN Ranges Dictionary
        #==================================
        pargs.ranges = []
        for i in kwargs['immDict']['wizard']['vlan_ranges']:
            i = DotMap(deepcopy(i))
            pargs.ranges.append(DotMap(
                configure_l2= i.configure_l2,
                name        = i.name_prefix,
                vlan_list   = i.vlan_range
            ))

        #==================================
        # Build inband|nfs|ooband Dict
        #==================================
        for i in pargs.vlans:
            if re.search('(inband|nfs|ooband)', i.vlan_type):
                pargs[i.vlan_type] = i

        #==================================
        # Build Protocols Dictionary
        #==================================
        if 'fc' in pargs.dtype: protocols.append('fcp')
        protocols = list(numpy.unique(numpy.array(protocols)))
        pargs.protocols = []
        for i in protocols: pargs.protocols.append(i)

        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


#=======================================================
# IMM Class
#=======================================================
class fw_os(object):
    def __init__(self, type):
        self.type = type

    #=============================================================================
    # Function - Build Policies - BIOS
    #=============================================================================
    def firmware(self, pargs, **kwargs):
        #=====================================================
        # Load Variables and Send Begin Notification
        #=====================================================
        validating.begin_section(self.type, 'Install')
        pargs.models = []
        for k,v in  pargs.server_profiles.items():
            pargs.models.append(v['model'])
        pargs.models = list(numpy.unique(numpy.array(pargs.models)))
        #==================================
        # Get CCO Password and Root
        #==================================
        kwargs['Variable'] = 'cco_password'
        kwargs = ezfunctions.sensitive_var_value(**kwargs)
        pargs.cco_password = kwargs['var_value']
        #==================================
        # Get Firmware Moids
        #==================================
        pargs.apiMethod = 'get'
        pargs.policy = 'distributables'
        pargs.purpose = self.type
        pargs.fw_version = '5.1(0.230054)'
        sw_moids = {}
        for m in pargs.models:
            pargs.apiFilter = f"Version eq '{pargs.fw_version}' and contains(SupportedModels, '{m}')"
            kwargs = isdk.api(self.type).calls(pargs, **kwargs)
            sw_moids.update({m:{'Moid':kwargs['results'][0]['Moid']}})
        pargs.pop('apiFilter')
        #==================================
        # Software Repository Auth
        #==================================
        pargs.apiBody = {
            'object_type': 'softwarerepository.Authorization',
            'password': pargs.cco_password,
            'repository_type': 'Cisco',
            'user_id': pargs.cco_user
        }
        pargs.apiMethod = 'create'
        pargs.policy    = 'auth'
        pargs.purpose   = 'firmware'
        kwargs = isdk.api(self.type).calls(pargs, **kwargs)
        #==================================
        # Software Eula
        #==================================
        pargs.apiMethod = 'by_moid'
        pargs.pmoid     = kwargs['results'][0]['AccountMoid']
        pargs.policy    = 'eula'
        pargs.purpose   = 'firmware'
        kwargs = isdk.api(self.type).calls(pargs, **kwargs)
        if not kwargs['results']:
            pargs.apiBody   = {'class_id': 'firmware.Eula', 'object_type': 'firmware.Eula'}
            pargs.apiMethod = 'create'
            kwargs = isdk.api(self.type).calls(pargs, **kwargs)
        #==================================
        # Upgrade Firmware
        #==================================
        for k,v in  pargs.server_profiles.items():
            v = DotMap(deepcopy(v))
            #==================================
            # Check Firmware Version
            #==================================
            if v.firmware == pargs.fw_version:
                print(f'Server Profile {k} - Server {v.serial} running Target Firmware {v.firmware}.')
            else:
                pargs.apiBody = {
                    'class_id': 'firmware.Upgrade',
                    'direct_download': {
                        'class_id': 'firmware.DirectDownload',
                        'object_type': 'firmware.DirectDownload',
                        'upgradeoption': 'upgrade_full'
                    },
                    'distributable': {
                        'class_id': 'mo.MoRef',
                        'moid': sw_moids[v.model]['Moid'],
                        'object_type': 'firmware.Distributable'
                    },
                    'network_share': {'object_type': 'firmware.NetworkShare'},
                    'object_type': 'firmware.Upgrade',
                    'server': {
                        'class_id': 'mo.MoRef',
                        'moid': v.moid,
                        'object_type': v.object_type
                    },
                    'upgrade_type': 'direct_upgrade',
                }
                #==================================
                # Upgrade Firmware
                #==================================
                pargs.apiMethod = 'create'
                pargs.policy = 'upgrade'
                pargs.server = k
                pargs.serial = v.serial
                pargs.purpose = self.type
                kwargs = isdk.api(self.type).calls(pargs, **kwargs)
                if kwargs['running']:
                    pargs.apiMethod = 'get'
                    pargs.apiFilter = f"Server.Moid eq '{v.moid}'"
                    pargs.srv_moid  = v.moid
                    kwargs = isdk.api(self.type).calls(pargs, **kwargs)
                    pargs.pop('apiFilter')
                    pargs.upgrade[k].moid   = kwargs['pmoids'][v.moid]['Moid']
                    pargs.upgrade[k].status = kwargs['pmoids'][v.moid]['UpgradeStatus']['Moid']
                else:
                    pargs.upgrade[k].moid   = kwargs['results']['Moid']
                    pargs.upgrade[k].status = kwargs['results']['UpgradeStatus']['Moid']
        #==================================
        # Power Cycle the Server
        #==================================
        #def power_cycle(v, pargs, **kwargs):
        #    pargs.apiMethod = 'get'
        #    pargs.apiFilter = f"Server.Moid eq '{v.moid}'"
        #    pargs.policy    = 'server_settings'
        #    pargs.purpose   = 'server'
        #    kwargs = isdk.api('server').calls(pargs, **kwargs)
        #    pmoid = kwargs['pmoid']
        #    pargs.pop('apiFilter')
        #    pargs.apiBody   = {'AdminPowerState': 'PowerCycle'}
        #    pargs.apiMethod = 'patch'
        #    kwargs = isdk.api('server').calls(pargs, **kwargs)
        #    return kwargs, pargs
        #=================================================
        # Monitor Firmware Upgrade until Complete
        #=================================================
        for k, v in  pargs.server_profiles.items():
            v = DotMap(deepcopy(v))
            if not v.firmware == pargs.fw_version:
                upgrade_complete = False
                while upgrade_complete == False:
                    pargs.apiMethod = 'by_moid'
                    pargs.pmoid     = pargs.upgrade[k].status
                    pargs.policy    = 'status'
                    pargs.purpose   = self.type
                    kwargs = isdk.api(self.type).calls(pargs, **kwargs)
                    if kwargs['results']['Overallstatus'] == 'success':
                        upgrade_complete = True
                        print(f'    - Completed Firmware Upgrade for {k}.')
                    elif kwargs['results']['Overallstatus'] == 'failed':
                        pargs.upgrade.failed.update({k:v.moid})
                        prRed(f'!!!FAILED!!! Firmware Upgrade for Server Profile {k}: Server {v.serial} failed.')
                        upgrade_complete = True
                    else: 
                        print(f'      * Firmware Upgrade still ongoing for {k}.  Waiting 120 seconds.')
                        time.sleep(120)

        #=====================================================
        # Send End Notification and return kwargs
        #=====================================================
        validating.end_section(self.type, 'Install')
        return kwargs, pargs

    #=============================================================================
    # Function - Build Policies - BIOS
    #=============================================================================
    def os_install(self, pargs, **kwargs):
        #=====================================================
        # Load Variables and Send Begin Notification
        #=====================================================
        validating.begin_section(self.type, 'Install')
        org_moid = kwargs['org_moids'][kwargs['org']]['Moid']
        pargs.models = []
        for k,v in  pargs.server_profiles.items():
            pargs.models.append(v['model'])
        pargs.models = list(numpy.unique(numpy.array(pargs.models)))
        pargs.repository_server = 'rdp1.rich.ciscolabs.com'
        pargs.repository_path = '/'
        pargs.scu_iso = 'ucs-scu-6.2.3b.iso'
        pargs.scu_version = (pargs.scu_iso.split('.iso')[0]).split('-')[2]
        pargs.os_iso = 'VMware-ESXi-7.0.3d-19482537-Custom-Cisco-4.2.2-a.iso'
        pargs.os_version = 'ESXi 7.0 U3'
        pargs.os_vendor  = 'VMware'
        #==================================
        # Get ESXi Root Password
        #==================================
        kwargs['Variable'] = 'esxi_password'
        kwargs = ezfunctions.sensitive_var_value(**kwargs)
        pargs.esxi_password = kwargs['var_value']
        #==================================
        # Get Org Software Repo
        #==================================
        pargs.apiMethod  = 'get'
        pargs.names      = ['user-catalog']
        pargs.policy     = 'org_repository'
        pargs.purpose    = 'software_repository'
        kwargs           = isdk.api(pargs.policy).calls(pargs, **kwargs)
        pargs.repository = kwargs['pmoids']['user-catalog']['Moid']
        #==================================
        # Get Existing SCU Repositories
        #==================================
        pargs.apiFilter   = f"Catalog.Moid eq '{pargs.repository}'"
        pargs.names       = [f'scu-{pargs.scu_version}']
        pargs.policy      = 'server_configuration_utility'
        kwargs            = isdk.api(pargs.policy).calls(pargs, **kwargs)
        #==================================
        # Create/Patch SCU Repo apiBody
        #==================================
        models = pargs.models.tolist()
        pargs.apiBody = {
            'catalog': {
                'class_id': 'mo.MoRef',
                'moid': pargs.repository,
                'object_type': 'softwarerepository.Catalog'
            },
            'class_id': 'firmware.ServerConfigurationUtilityDistributable',
            'description': f'scu-{pargs.scu_version} Server Configuration Utility',
            'name': f'scu-{pargs.scu_version}',
            'object_type': 'firmware.ServerConfigurationUtilityDistributable',
            'source': {
                'class_id': 'softwarerepository.HttpServer',
                'LocationLink': f'https://{pargs.repository_server}{pargs.repository_path}{pargs.scu_iso}',
                'object_type': 'softwarerepository.HttpServer',
            },
            'supported_models': models,
            'Vendor': 'Cisco',
            'Version': pargs.scu_version
        }
        if kwargs['pmoids'].get(pargs.apiBody['name']):
            pargs.apiMethod = 'patch'
            pargs.pmoid     = kwargs['pmoids'][pargs.apiBody['name']]['Moid']
        else: pargs.apiMethod = 'create'
        kwargs = isdk.api(self.type).calls(pargs, **kwargs)
        pargs.scu_moid = kwargs['pmoid']
        repo_url = f'https://{pargs.repository_server}{pargs.repository_path}{pargs.scu_iso}'
        try:
            r = requests.head(repo_url, allow_redirects=True, verify=False, timeout=10)
        except requests.RequestException as e:
            prRed(f"!!!ERROR!!!\n  Exception when calling {repo_url}:\n {e}\n")
            sys.exit(1)
        #size = r.headers.get('content-length', -1)
        #==================================
        # Confirm if OS Repo Exists
        #==================================
        pargs.apiMethod = 'get'
        pargs.names     = ['ESXi7.0U3']
        pargs.policy    = 'operating_system'
        kwargs          = isdk.api(pargs.policy).calls(pargs, **kwargs)
        pargs.pop('apiFilter')
        #==================================
        # Create/Patch OS Repo apiBody
        #==================================
        pargs.apiBody = {
            'catalog': {
                'class_id': 'mo.MoRef',
                'moid': pargs.repository,
                'object_type': 'softwarerepository.Catalog'
            },
            'class_id': 'softwarerepository.OperatingSystemFile',
            'description': f'{pargs.os_version} Server Configuration Utility',
            'name': pargs.os_version,
            'object_type': 'softwarerepository.OperatingSystemFile',
            'source': {
                'class_id': 'softwarerepository.HttpServer',
                'LocationLink': f'https://{pargs.repository_server}{pargs.repository_path}{pargs.os_iso}',
                'object_type': 'softwarerepository.HttpServer',
            },
            'Vendor': pargs.os_vendor,
            'Version': pargs.os_version
        }
        if kwargs['pmoids'].get(pargs.apiBody['name']):
            pargs.apiMethod = 'patch'
            pargs.pmoid     = kwargs['pmoids'][pargs.apiBody['name']]['Moid']
        else: pargs.apiMethod = 'create'
        kwargs = isdk.api(self.type).calls(pargs, **kwargs)
        pargs.os_moid = kwargs['pmoid']
        repo_url = f'https://{pargs.repository_server}{pargs.repository_path}{pargs.os_iso}'
        try:
            r = requests.head(repo_url, allow_redirects=True, verify=False, timeout=10)
        except requests.RequestException as e:
            prRed(f"!!!ERROR!!!\n  Exception when calling {repo_url}:\n {e}\n")
            sys.exit(1)
        #size = r.headers.get('content-length', -1)
        #==================================
        # Get OS Catalog
        #==================================
        pargs.apiFilter   = f"Name eq 'shared'"
        pargs.apiMethod   = 'get'
        pargs.policy      = 'os_catalog'
        pargs.purpose     = self.type
        kwargs            = isdk.api(pargs.policy).calls(pargs, **kwargs)
        pargs.os_catalog  = kwargs['pmoids']['shared']['Moid']
        #==================================
        # Get OS Configuration File
        #==================================
        pargs.apiFilter   = f"Catalog.Moid eq '{pargs.os_catalog}'"
        pargs.names       = ['ESXi7.0ConfigFile']
        pargs.policy      = 'os_configuration'
        kwargs            = isdk.api(pargs.policy).calls(pargs, **kwargs)
        pargs.os_config   = kwargs['pmoids']['ESXi7.0ConfigFile']['Moid']
        #==========================================
        # Deploy Operating System for each Profile
        #==========================================
        for k,v in pargs.netapp.wwpns.a[1].items(): san_target = v
        for k,v in pargs.server_profiles.items():
            v = DotMap(deepcopy(v))
            if re.search('(esx08)', k):
                fqdn = k + '.' + pargs.dns_domains[0]
                pargs.apiBody = {
                    'answers': {
                        'ClassId': 'os.Answers',
                        'Hostname': fqdn,
                        'IpConfigType': 'static',
                        'IpConfiguration': {
                            'ClassId': 'os.Ipv4Configuration',
                            'IpV4Config': {
                                'ClassId': 'comm.IpV4Interface',
                                'Gateway': v.inband.gateway,
                                'IpAddress': v.inband.ip,
                                'Netmask': v.inband.netmask,
                                'ObjectType': 'comm.IpV4Interface'
                            },
                            'ObjectType': 'os.Ipv4Configuration',
                        },
                        "IsRootPasswordCrypted": False,
                        'Nameserver': pargs.dns_servers[0],
                        'NetworkDevice': v.macs['mgmt-a'],
                        'ObjectType': 'os.Answers',
                        'RootPassword': pargs.esxi_password,
                        'Source': 'Template'
                    },
                    'configuration_file': {
                        'class_id': 'mo.MoRef',
                        'Moid': pargs.os_config,
                        'object_type': 'os.ConfigurationFile',
                    },
                    'image': {
                        'class_id': 'mo.MoRef',
                        'Moid': pargs.os_moid,
                        'object_type': 'softwarerepository.OperatingSystemFile',
                    },
                    'install_method': 'vMedia',
                    'install_target': {
                        'class_id': 'os.FibreChannelTarget',
                        'initiator_wwpn': v.wwpns['vhba1'],
                        'lun_id': 0,
                        'object_type': 'os.FibreChannelTarget',
                        'target_wwpn': san_target
                    },
                    'name': f'{k}-osinstall',
                    'object_type': 'os.Install',
                    'organization': {
                        'class_id': 'mo.MoRef',
                        'Moid': org_moid,
                        'object_type': 'organization.Organization',
                    },
                    'osdu_image': {
                        'class_id': 'mo.MoRef',
                        'Moid': pargs.scu_moid,
                        'object_type': 'firmware.ServerConfigurationUtilityDistributable',
                    },
                    'override_secure_boot': True,
                    'server': {
                        'class_id': 'mo.MoRef',
                        'moid': v.moid,
                        'object_type': v.object_type
                    },
                }
                pargs.apiMethod = 'create'
                pargs.policy  = self.type
                pargs.purpose = self.type
                print(f"      * host {k}: initiator: {v.wwpns['vhba1']}\n        target: {san_target}"\
                      f"\n        mac: {v.macs['mgmt-a']}")
                kwargs = isdk.api(self.type).calls(pargs, **kwargs)
                pargs.server_profiles[k]['os_install'] = {
                    'moid': kwargs['pmoid'],
                    'workflow': ''
                }
        time.sleep(60)
        #=================================================
        # Monitor OS Installation until Complete
        #=================================================
        for k, v in  pargs.server_profiles.items():
            if re.search('(esx03|esx08)', k):
                v = DotMap(deepcopy(v))
                pargs.apiFilter = f"Name eq '{k}-osinstall'"
                pargs.apiMethod = 'get'
                pargs.policy    = self.type
                pargs.purpose   = self.type
                kwargs = isdk.api(self.type).calls(pargs, **kwargs)
                pargs.pop('apiFilter')
                v.os_install.workflow = kwargs['results'][len(kwargs['results'])-1]['WorkflowInfo']['Moid']
                install_complete = False
                while install_complete == False:
                    pargs.apiMethod = 'by_moid'
                    pargs.pmoid     = v.os_install.workflow
                    pargs.policy    = 'workflow_info'
                    pargs.purpose   = self.type
                    kwargs = isdk.api(self.type).calls(pargs, **kwargs)
                    if kwargs['results']['Status'] == 'COMPLETED':
                        install_complete = True
                        print(f'    - Completed Operating System Installation for {k}.')
                    elif re.search('(FAILED|TERMINATED|TIME_OUT)', kwargs['results']['Status']):
                        pargs.upgrade.failed.update({k:v.moid})
                        prRed(f'!!!FAILED!!! Operating System Installation for Server Profile {k} failed.')
                        install_complete = True
                    else:
                        progress = kwargs['results']['Progress']
                        status = kwargs['results']['Status']
                        print(f'      * Operating System Installation for {k}.')
                        print(f'        Status is {status} Progress is {progress}, Waiting 120 seconds.')
                        time.sleep(120)
        #=====================================================
        # Send End Notification and return kwargs
        #=====================================================
        validating.end_section(self.type, 'Install')
        return kwargs, pargs

#=====================================================
# Print Color Functions
#=====================================================
def prCyan(skk): print("\033[96m {}\033[00m" .format(skk))
def prGreen(skk): print("\033[92m {}\033[00m" .format(skk))
def prLightPurple(skk): print("\033[94m {}\033[00m" .format(skk))
def prLightGray(skk): print("\033[97m {}\033[00m" .format(skk))
def prPurple(skk): print("\033[95m {}\033[00m" .format(skk))
def prRed(skk): print("\033[91m {}\033[00m" .format(skk))
def prYellow(skk): print("\033[93m {}\033[00m" .format(skk))
