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
import sys
import validating

sys.path.insert(0, './classes')
from classes import ezfunctions
from classes import netapp
from classes import nxos
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
        for i in pargs.server_settings:
            if re.search('M[5-9]', i.gen) and i.tpm == 'True': btemplates.append(f'{i.gen}-{i.cpu}-virtual-tpm')
            elif re.search('M[5-9]', i.gen): btemplates.append(f'{i.gen}-{i.cpu}-virtual')
        btemplates = numpy.unique(numpy.array(btemplates))
        for i in btemplates:
            polVars = dict(
                baud_rate           = 115200,
                bios_template       = i,
                console_redirection = f'serial-port-a',
                description         = f'{pargs.ppfx}{i} {descr} Policy',
                name                = f'{pargs.ppfx}{i}',
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
            if not i.type in ptypes and re.search('iscsi', i.type): ptypes.append(i.type)
        for i in ptypes:
            polVars = {
                "boot_devices": [{
                    "enabled": True,
                    "name": "kvm",
                    "object_type": "boot.VirtualMedia",
                    "sub_type": "kvm-mapped-dvd"
                }],
                "boot_mode": "Uefi",
                "description": f"{i} Boot Policy",
                "enable_secure_boot": True,
                "name": f"{i}-boot",
            }
            if 'fcp' in i:
                fabrics = ['a', 'b']
                for x in range(0,len(fabrics)):
                    for c in pargs.netapp.wwpns[fabrics[x]]:
                        for k,v in c.items():
                            polVars['boot_devices'].append({
                                "enabled": True,
                                "interface_name": f"vhba{x+1}",
                                "name": (pargs.netapp.data_svm) + '-' + k,
                                "object_type": "boot.San",
                                "slot":"MLOM",
                                "wwpn":v
                            })
            elif 'iscsi' in i:
                fabrics = ['a', 'b']
                for fab in fabrics:
                        polVars['boot_devices'].append({
                            "enabled": True,
                            "interface_name": f"storage-{fab}",
                            "name": f"storage-{fab}",
                            "object_type": "boot.Iscsi",
                            "slot":"MLOM"
                        })
            polVars['boot_devices'].append({
                "enabled": True,
                "name": "cimc",
                "object_type": "boot.VirtualMedia",
                "sub_type": "cimc-mapped-dvd"
            })
            polVars['boot_devices'].append({
                "enabled": True,
                "name": "uefishell",
                "object_type": "boot.UefiShell"
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
        models          = []
        pargs.apiMethod = 'get'
        pargs.apiQuery  = f"RegisteredDevice.Moid eq '{pargs.registered_device}'"
        pargs.policy    = 'serial_number'
        pargs.purpose   = 'chassis'
        kwargs          = isdk.api('serial_number').calls(pargs, **kwargs)
        pargs.chassis   = DotMap(deepcopy(kwargs['pmoids']))
        pargs.pop('apiQuery')
        for k ,v in pargs.chassis.items():
            models.append(v.model.split('-')[1])
        models = numpy.unique(numpy.array(models))
        for m in models:
            # Build Dictionary
            polVars = dict(
                action            = 'Deploy',
                imc_access_policy = f'{pargs.ppfx}kvm',
                power_policy      = f'{pargs.ppfx}{deepcopy(m)}',
                snmp_policy       = f'{pargs.ppfx}snmp',
                thermal_policy    = f'{pargs.ppfx}{deepcopy(m)}',
                targets           = [],
            )
            for k, v in pargs.chassis.items():
                if m in v.model:
                    polVars['targets'].append(dict(
                        description   = f"{pargs.name}-{v.id} Chassis Profile",
                        name          = f'{pargs.name}-{v.id}',
                        serial_number = k
                    ))
            # Add Policy Variables to immDict
            kwargs['class_path'] = f'profiles,{self.type}'
            kwargs = ezfunctions.ez_append(polVars, **kwargs)
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
            description                 = f"{pargs.name} Domain Profile",
            name                        = pargs.name,
            network_connectivity_policy = f'{pargs.ppfx}dns',
            ntp_policy                  = f'{pargs.ppfx}ntp',
            port_policies               = [f'{pargs.name}-A', f'{pargs.name}-B'],
            serial_numbers              = pargs.serials,
            snmp_policy                 = f'{pargs.ppfx}snmp-domain',
            switch_control_policy       = f'{pargs.ppfx}sw-ctrl',
            syslog_policy               = f'{pargs.ppfx}syslog-domain',
            system_qos_policy           = f'{pargs.ppfx}qos',
            vlan_policies               = f'{pargs.ppfx}vlans',
        )
        if re.search('(fc|fc-nvme)', pargs.dtype):
            polVars.update({'vsan_policies': [f'{pargs.ppfx}vsan-{pargs.vsans[0]}', f'{pargs.ppfx}vsan-{pargs.vsans[1]}']})
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
                description      = f'{pargs.ppfx}{i} {descr} Policy',
                name             = f'{pargs.ppfx}{i}',
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
                description          = f'{pargs.ppfx}{i} {descr} Policy',
                name                 = f'{pargs.ppfx}{i}',
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
        pargs.vlan = {}
        pargs.vlan['all_vlans'] = ezfunctions.vlan_list_format(numpy.unique(numpy.array(vlans)))
        for i in pargs.vlans:
            if   i['type'] == 'inband': pargs.vlan.update({'mgmt':i['vlan_id']})
            elif i['type'] == 'iscsi': pargs.vlan.update({'iscsi':i['vlan_id']})
            elif i['type'] == 'migration': pargs.vlan.update({'migration':i['vlan_id']})
            elif i['type'] == 'nfs': pargs.vlan.update({'nfs':i['vlan_id']})
            elif i['type'] == 'nvme': pargs.vlan.update({'nvme':i['vlan_id']})
        storage = []
        if pargs.vlan.get('iscsi'): storage.append(pargs.vlan['iscsi'])
        if pargs.vlan.get('nfs'): storage.append(pargs.vlan['nfs'])
        if pargs.vlan.get('nvme'): storage.append(pargs.vlan['nvme'])
        pargs.vlan['storage'] = ezfunctions.vlan_list_format(storage)
        plist = ['mgmt', 'migration', 'storage', 'all_vlans']
        for i in plist:
            if re.search('(mgmt|migration)', i): nvlan = pargs.vlan[i]
            elif 'storage' == i:
                if pargs.vlan.get('iscsi'): nvlan = pargs.vlan['iscsi']
            else: nvlan = 1
            polVars = dict(
                allowed_vlans = f'{pargs.vlan[i]}',
                description   = f'{pargs.ppfx}{i} {descr} Policy',
                name          = f'{pargs.ppfx}{i}',
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
        plist = ['Bronze', 'Gold', 'Platinum', 'Silver']
        for i in plist:
            polVars = dict(
                enable_trust_host_cos = False,
                burst        = 10240,
                description  = f'{pargs.ppfx}{i} {descr} Policy',
                name         = f'{pargs.ppfx}{i}',
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
            description      = f'{pargs.ppfx}wwnn Pool',
            name             = f'{pargs.ppfx}wwnn',
            id_blocks        = [{
                'from':f'20:00:00:25:B5:{pargs.pool_prefix}:00:00',
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
                description = f'{pargs.ppfx}wwpn-{i.lower()} Pool',
                name        = f'{pargs.ppfx}wwpn-{i.lower()}',
            ))
            polVars['id_blocks'][0].update({'from':f'20:00:00:25:B5:{pargs.pool_prefix}:{i}0:00'})
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
            # Build Dictionary
            polVars = dict(
                description           = f'{pargs.ppfx}vsan-{pargs.vsans[x]} {descr} Policy',
                fc_target_zoning_type = 'SIMT',
                name                  = f'{pargs.ppfx}vsan-{pargs.vsans[x]}',
                targets               = [],
            )
            for i in pargs.netapp.wwpns[fabrics[x]]:
                for k,v in i.items():
                    polVars['targets'].append(dict(
                        name      = pargs.netapp.data_svm + '-' + k,
                        switch_id = (fabrics[x]).upper(),
                        vsan_id   = pargs.vsans[x],
                        wwpn      = v
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
                description      = f'{pargs.ppfx}{i} {descr} Policy',
                name             = f'{pargs.ppfx}{i}',
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
        for i in pargs.vsans:
            polVars = dict(
                description = f'{pargs.ppfx}vsan-{i} {descr} Policy',
                name        = f'{pargs.ppfx}vsan-{i}',
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
                description         = f'{pargs.ppfx}{i} {descr} Policy',
                name                = f'{pargs.ppfx}{i}',
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
            description = f'{pargs.ppfx}flow-ctrl {descr} Policy',
            name        = f'{pargs.ppfx}flow-ctrl',
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
            description         = f'{pargs.ppfx}kvm {descr} Policy',
            inband_ip_pool      = f'kvm-inband',
            inband_vlan_id      = pargs.vlan['mgmt'],
            out_of_band_ip_pool = 'kvm-ooband',
            name                = f'{pargs.ppfx}kvm',
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
            i = DotMap(deepcopy(i))
            if re.search('(inband|iscsi|ooband)', i.type):
                if not pargs.pools.ip.get(i.type):
                    pargs.pools.ip[i.type] = []
                if re.search('inband|ooband', i.type):
                    name = f'{pargs.ppfx}kvm-{i.type}'
                    pool_from = deepcopy(i.pool[0])
                    pool_to   = deepcopy(i.pool[-1])
                else:
                    name = f'{pargs.ppfx}iscsi-vlan{i.vlan_id}'
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
                pargs.pools.ip[i.type].append(polVars['name'])
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
            description      = f'{pargs.ppfx}iscsi IQN Pool',
            name             = f'{pargs.ppfx}iscsi',
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
            description = f'{pargs.ppfx}ipmi {descr} Policy',
            name        = f'{pargs.ppfx}ipmi',
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
            description            = f'{pargs.ppfx}iadapter {descr} Policy',
            dhcp_timeout           = 60,
            name                   = f'{pargs.ppfx}iadapter',
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
                description             = f'{pargs.ppfx}{pool} {descr} Policy',
                initiator_ip_source     = 'Pool',
                initiator_ip_pool       = pargs.pools.ip['iscsi'][x], 
                iscsi_adapter_policy    = f'{pargs.ppfx}iadapter',
                name                    = f'{pargs.ppfx}{pool}',
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
        for item in kwargs['immDict']['orgs'][kwargs['org']]['netapp']['svm']:
            for i in item['data_interfaces']:
                i = DotMap(deepcopy(i))
                if 'iscsi' in i.name:
                    name = pargs.netapp.data_svm + ':' + i.name
                    polVars = dict(
                        description = f'{name} {descr} Policy',
                        ip_address  = deepcopy(i.ip.address),
                        luns        = [{
                            'bootable':True,
                            'lun_id':0
                        }],
                        name        = f'{name}',
                        port        = 3260,
                        target_name = pargs.netapp.iscsi.iqn,
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
        for i in pargs.server_settings: vic_gen.append(f'{i.vic_gen}')
        vic_gen = numpy.unique(numpy.array(vic_gen))
        lan_policies = ['lcp']
        for i in pargs.vlans:
            i = DotMap(deepcopy(i))
            if i.type == 'iscsi':
                lan_policies.append('lcp-iscsi')
                break
        for g in vic_gen:
            for lcp in lan_policies:
                descr     = (self.type.replace('_', ' ')).title()
                pci_order = deepcopy(pargs.pci_order)
                polVars = dict(
                    description          = f'{pargs.ppfx}vic-{g}-{lcp} {descr} Policy',
                    iqn_pool             = '',
                    name                 = f'{pargs.ppfx}vic-{g}-{lcp}',
                    target_platform      = 'FIAttached',
                    vnics                = [],
                )
                if re.search('iscsi', lcp):
                    polVars['iqn_pool'] = f'{pargs.ppfx}iscsi'
                else: polVars.pop('iqn_pool')
                plist = ['mgmt-Silver', 'migration-Bronze', 'storage-Platinum', 'dvs-Gold']
                vnic_count = 0
                for i in plist:
                    pname = i.split('-')[0]
                    pqos  = i.split('-')[1]
                    if 'dvs' in pname: pgroup = 'all_vlans'
                    else: pgroup = pname
                    if re.search('(dvs|migration)', i): adapter_policy = 'VMware-High-Trf'
                    elif 'storage' in i and g == 'gen4': adapter_policy = '16RxQs-4G'
                    elif 'storage' in i and g == 'gen5': adapter_policy = '16RxQs-5G'
                    else: adapter_policy = 'VMware'
                    polVars['vnics'].append(dict(
                        ethernet_adapter_policy         = adapter_policy,
                        ethernet_network_control_policy = 'cdp',
                        ethernet_network_group_policy   = pgroup,
                        ethernet_qos_policy             = pqos,
                        iscsi_boot_policies             = [],
                        names                           = [f'{pname}-a', f'{pname}-b'],
                        mac_address_pools               = [f'{pname}-a', f'{pname}-b'],
                        placement_pci_order             = [pci_order, pci_order + 1],
                    ))
                    if 'storage' in pname and 'iscsi' in lcp:
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
            description = f'{pargs.ppfx}link-agg {descr} Policy',
            name        = f'{pargs.ppfx}link-agg',
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
            description = f'{pargs.ppfx}link-ctrl {descr} Policy',
            name        = f'{pargs.ppfx}link-ctrl',
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
            description = f'{pargs.ppfx}users {descr} Policy',
            name        = f'{pargs.ppfx}users',
            users       = [dict(
                enabled  = True,
                password = 1,
                role     = 'admin',
                username = pargs.local_user
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
                    description      = f'{pargs.ppfx}{pool}-{flist[x]} Pool',
                    name             = f'{pargs.ppfx}{pool}-{flist[x]}',
                    mac_blocks       = [{
                        'from':f'00:25:B5:{pargs.pool_prefix}:{n[x]}0:00',
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
            description = f'{pargs.ppfx}mcast {descr} Policy',
            name        = f'{pargs.ppfx}mcast',
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
            description    = f'{pargs.ppfx}dns {descr} Policy',
            name           = f'{pargs.ppfx}dns',
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
            description = f'{pargs.ppfx}ntp {descr} Policy',
            name        = f'{pargs.ppfx}ntp',
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
        for i in (pargs.uplinks.split('/')[-1]).split('-'):
            ports.append({'port_id':int(i)})
        epc = int((pargs.uplinks.split('/')[-1]).split('-')[0])
        polVars = dict(
            description  = f'{pargs.name} {descr} Policy',
            device_model = pargs.device_model,
            names        = [f'{pargs.name}-A', f'{pargs.name}-B'],
            port_channel_ethernet_uplinks = [dict(
                admin_speed                   = 'Auto',
                ethernet_network_group_policy = 'all_vlans',
                flow_control_policy           = 'flow-ctrl',
                interfaces                    = ports,
                link_aggregation_policy       = 'link-agg',
                link_control_policy           = 'link-ctrl',
                pc_ids                        = [epc, epc],
            )]
        )
        configure_fc = False
        if re.search('(fc|fc-nvme)', pargs.dtype): configure_fc = True
        if configure_fc == True:
            ports = []
            x     = pargs.fcp_ports.split('/')
            for i in (x[-1]).split('-'):
                ports.append({'port_id':i})
            if pargs.swmode == 'end-host':
                fpc = int((x[-1]).split('-')[0])
                polVars.update(dict(
                    port_channel_fc_uplinks = [dict(
                        admin_speed  = pargs.fcp_speed,
                        fill_pattern = 'Idle',
                        interfaces   = ports,
                        pc_ids       = [fpc, fpc],
                        vsan_ids     = pargs.vsans
                    )]
                ))
                if len(x) == 3:
                    for i in polVars['port_channel_fc_uplinks']['interfaces']:
                        i.update({'breakout_port_id':x[2]})
            else:
                ports = x[-1]
                polVars.update(dict(
                    port_role_fc_storage = [dict(
                        admin_speed  = pargs.fcp_speed,
                        port_list    = ports,
                        vsan_ids     = pargs.vsans
                    )]
                ))
                if len(x) == 3:
                    polVars['port_role_fc_storage'].update({'breakout_port_id':x[2]})
            if len(x) == 3:
                polVars.update(dict(
                    port_modes = [dict(
                        custom_mode = f'BreakoutFibreChannel{pargs.breakout_speed.fc}',
                        port_list   = [35, 36]
                    )]
                ))
            else:
                ports = int(x[-1].split('-')[0])
                porte = int(x[-1].split('-')[1])
                if porte > 12: port_end = 16
                elif porte > 8: port_end = 12
                elif porte > 4: port_end = 8
                else: port_end = 4
                polVars.update(dict(
                    port_modes = [dict(
                        custom_mode = 'FibreChannel',
                        port_list   = [1, port_end]
                    )]
                ))
        polVars.update({'port_role_servers':[]})
        for i in pargs.server_settings:
            if len(i.ports.split('/')) == 3:
                bp = int(i.ports.split('/'))[2]
                polVars['port_modes'].append(dict(
                    custom_mode = f'BreakoutEthernet{pargs.breakout_speed.eth}',
                    port_list   = [bp, bp]
                ))
                polVars['port_role_servers'].append(dict(
                    breakout_port_id      = bp,
                    connected_device_type = i.equipement,
                    device_number         = i.identifier,
                    port_list             = i.ports.split('/')[-1]
                ))
            else:
                polVars['port_role_servers'].append(dict(
                    connected_device_type = i['equipment'],
                    device_number         = i['identifier'],
                    port_list             = i['ports'].split('/')[-1]
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
        plist = ['5108', '9508', 'server']
        for i in plist:
            polVars = dict(
                description      = f'{pargs.ppfx}{i} {descr} Policy',
                name             = f'{pargs.ppfx}{i}',
                power_allocation = 0,
                power_redundancy = 'Grid',
            )
            if i == 'server': polVars.update({'power_restore':'LastState'})
            if i == 9508: polVars['power_allocation'] = 8400
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
            description          = f'{pargs.ppfx}scp {descr} Policy',
            name                 = f'{pargs.ppfx}scp',
            target_platform      = 'FIAttached',
            vhbas                = [],
            wwnn_allocation_type = 'POOL',
            wwnn_pool            = f'{pargs.ppfx}wwnn',
        )
        ncount = 1
        if   pargs.dtype == 'fc': adapter_list = ['VMware']
        elif pargs.dtype == 'fc-nvme': adapter_list = ['VMware', 'FCNVMeInitiator']
        vcount = 0
        for x in range(0,len(adapter_list)):
            polVars['vhbas'].append(dict(
                fc_zone_policies               = [],
                fibre_channel_adapter_policy   = adapter_list[x],
                fibre_channel_network_policies = [f'vsan-{pargs.vsans[0]}', f'vsan-{pargs.vsans[1]}'],
                fibre_channel_qos_policy       = 'fc-qos',
                names                          = [f'vhba{ncount}', f'vhba{ncount + 1}'],
                placement_pci_order            = [pci_order, pci_order + 1],
                wwpn_allocation_type           = 'POOL',
                wwpn_pools                     = [f'wwpn-a', f'wwpn-b'],
            ))
            if 'switch' in pargs.swmode:
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
            description = f'{pargs.ppfx}sol {descr} Policy',
            name        = f'{pargs.ppfx}sol',
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
        pargs.ipcount = 0
        def server_profiles_dict(name, p, pargs, smap):
            pargs.server_profiles[name] = {
                'firmware': smap.Firmware,
                'model':  smap.Model,
                'moid': smap.Moid,
                'serial': smap.Serial,
                'slot': smap.SlotId,
                'object_type':smap.SourceObjectType
            }
            if smap.SourceObjectType == 'compute.Blade':
                pargs.server_profiles[name].update({
                    'chassis_id': p.identifier,
                    'chassis_moid': smap.Parent.Moid,
                })
            else:
                pargs.server_profiles[name].update({
                    'id': p.identifier
                })
            # Send Error Message if IP Range isn't long enough
            def error_ip_range(i):
                print(f'!!!ERROR!!!\nNot Enough IPs in Range {i.server} for {name}')
                sys.exit(1)
            # Send Error Message if Server Range is missing from VLAN
            def error_server_range(i):
                print(f'!!!ERROR!!!\nDid Not Find Server IP Range defined for {i.type}:{i.name}:{i.vlan_id}')
                sys.exit(1)
            # Dictionary of IP Settings for Server
            def ipdict(i, ipindex):
                idict = {
                    'gateway':i.gateway,
                    'ip':i.server[ipindex],
                    'netmask':i.netmask,
                    'prefix':i.prefix,
                    'vlan':i.vlan_id,
                    'vlan_name':i.name,
                }
                return idict
            if 'compupte.Blade' in smap.objectType:
                ipindex = (int(p.identifier) - 1) * 8 + int(smap.SlotId) - 1
            else: ipindex = int(p.identifier) + pargs.ipcount
            pargs.ipcount += 1
            print(pargs.ipcount)
            for i in pargs.vlans:
                i = DotMap(deepcopy(i))
                if re.search('(inband|iscsi|migration|nfs|nvme)', i.type):
                    if not i.server: error_server_range(i)
                    if not len(i.server) >= ipindex: error_ip_range(i)
                if re.search('(iscsi|nvme)', i.type):
                    if not pargs.server_profiles[name].get(i.type):
                        pargs.server_profiles[name].update({i.type:[]})
                    idict = ipdict(i, ipindex)
                    pargs.server_profiles[name][i.type].append(idict)
                if re.search('(inband|migration|nfs)', i.type):
                    idict = ipdict(i, ipindex)
                    pargs.server_profiles[name][i.type] = idict
            return pargs
        
        #=====================================================
        # Build Server Profiles
        #=====================================================
        if 'fc' in pargs.dtype: t = 'fcp'
        else: t = 'iscsi'
        rackServers = []
        for p in pargs.server_settings:
            if p.equipment == 'RackServer': rackServers.append(p.id)
        if len(rackServers) > 0:
            kwargs  = isdk.api('serial_number').calls(pargs, **kwargs)
            rackmap = DotMap(deepcopy(kwargs['results']))
        for p in pargs.server_settings:
            if 'True' in p.tpm:
                template = f'{p.gen}-{p.cpu}-tpm-vic-{p.vic_gen}-{t}'
            else: template = f'{p.gen}-{p.cpu}-vic-{p.vic_gen}-{t}'
            # Build Dictionary
            polVars = dict(
                action                      = 'Deploy',
                create_from_template        = False,
                targets                     = [],
                ucs_server_profile_template = template,
            )
            #=====================================================
            # Add Targets
            #=====================================================
            def profile_targets(name, smap):
                polVars['targets'].append(dict(
                    description   = f"{name} Server Profile",
                    name          = f'{name}',
                    serial_number = smap.Serial
                ))
                return polVars

            #=====================================================
            # If Chassis, Loop Through Blades/Nodes
            #=====================================================
            if p.equipment == 'Chassis':
                for k, v in pargs.chassis.items():
                    if v.id == p.identifier:
                        suffix = int(p.suffix)
                        pprefix = p.profile[:-(suffix)]
                        pstart  = int(p.profile[-(suffix):])
                        for x in range(0,len(v.blades)):
                            pargs.apiMethod = 'by_moid'
                            pargs.pmoid     = v.blades[x].moid
                            pargs.policy    = 'serial_number'
                            pargs.purpose   = 'server'
                            kwargs          = isdk.api('serial_number').calls(pargs, **kwargs)
                            smap = DotMap(deepcopy(kwargs['results']))
                            name = f'{pprefix}{str(pstart+smap.SlotId-1).zfill(suffix)}'
                            polVars = profile_targets(name, polVars, smap)
                            pargs   = server_profiles_dict(name, p, pargs, smap)
            elif p.equipment == 'RackServer':
                pargs.apiMethod = 'get'
                pargs.apiQuery  = f"RegisteredDevice.Moid eq '{pargs.registered_device}'"
                pargs.policy    = 'serial_number'
                pargs.purpose   = 'server'
                kwargs          = isdk.api('serial_number').calls(pargs, **kwargs)
                smap = DotMap(deepcopy(kwargs['results']))
                name = p.profile
                polVars = profile_targets(name, polVars, smap)

            ezfunctions.jprint(pargs.server_profiles)
            exit()
            # Add Policy Variables to immDict
            kwargs['class_path'] = f'profiles,{self.type}'
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
            description     = f'{pargs.ppfx}snmp Policy',
            enable_snmp     = True,
            name            = f'{pargs.ppfx}snmp',
            snmp_traps      = [],
            snmp_users      = [dict(
                auth_password    = 1,
                auth_type        = 'SHA',
                name             = pargs.snmp_user,
                privacy_password = 1,
                privacy_type     = 'AES',
                security_level   = 'AuthPriv'
            )],
            system_contact  = pargs.snmp_contact,
            system_location = pargs.snmp_location,
        )
        for i in pargs.snmp_servers:
            polVars['snmp_traps'].append(dict(
                destination_address = i,
                port                = 162,
                user                = pargs.snmp_user
            ))

        # Add Policy Variables to immDict
        kwargs['class_path'] = f'policies,snmp'
        kwargs = ezfunctions.ez_append(polVars, **kwargs)
        polVars.update({
            'description':f'{pargs.ppfx}snmp-domain Policy',
            'name':f'{pargs.ppfx}snmp-domain'
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
                description      = f'{pargs.ppfx}{i} {descr} Policy',
                name             = f'{pargs.ppfx}{i}',
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
        polVars = dict(
            description       = f'{pargs.ppfx}sw-ctrl {descr} Policy',
            fc_switching_mode = pargs.swmode,
            name              = f'{pargs.ppfx}sw-ctrl',
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
            description = f'{pargs.ppfx}syslog Policy',
            local_logging = dict(
                minimum_severity = 'warning',
            ),
            name            = f'{pargs.ppfx}syslog',
            remote_logging      = [],
        )
        for i in pargs.log_servers:
            polVars['remote_logging'].append(dict(
                enable           = True,
                hostname         = i,
                minimum_severity = 'informational',
            ))

        # Add Policy Variables to immDict
        kwargs['class_path'] = f'policies,syslog'
        kwargs = ezfunctions.ez_append(polVars, **kwargs)
        polVars.update({
            'description':f'{pargs.ppfx}syslog-domain Policy',
            'name':f'{pargs.ppfx}syslog-domain'
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
            description = f'{pargs.ppfx}qos {descr} Policy',
            classes     = [],
            name        = f'{pargs.ppfx}qos',
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
        for p in pargs.server_settings:
            if len(server_profiles) == 0:
                server_profiles.append(p)
            else:
                matched = True
                for i in server_profiles:
                    if not p.vic_gen == i.vic_gen: matched = False
                    elif not p.cpu == i.cpu: matched = False
                    elif not p.gen == i.gen: matched = False
                    elif not p.tpm == i.tpm: matched = False
                if matched == False: server_profiles.append(p)
        if 'fc' in pargs.dtype: template_types.append('fcp')
        for i in pargs.vlans:
            i = DotMap(deepcopy(i))
            if i.type == 'iscsi':
                template_types.append('iscsi')
        template_types = numpy.unique(numpy.array(template_types))
        for t in template_types:
            for p in server_profiles:
                bios_policy = f'{p.gen}-{p.cpu}-virtual'
                if 'True' in p.tpm:
                    bios_policy = bios_policy + '-tpm'
                    name = f'{p.gen}-{p.cpu}-tpm-vic-{p.vic_gen}-{t}'
                else: name = f'{p.gen}-{p.cpu}-vic-{p.vic_gen}-{t}'
                if 'iscsi' in t: lcp = f'vic-{p.vic_gen}-lcp-iscsi'
                else: lcp = f'vic-{p.vic_gen}-lcp'
                polVars = dict(
                    bios_policy             = bios_policy,
                    boot_order_policy       = f'{t}-boot',
                    description             = f"{name} Server Template",
                    imc_access_policy       = f'{pargs.ppfx}kvm',
                    lan_connectivity_policy = f'{pargs.ppfx}{lcp}',
                    local_user_policy       = f'{pargs.ppfx}users',
                    name                    = name,
                    power_policy            = f'{pargs.ppfx}server',
                    san_connectivity_policy = f'',
                    serial_over_lan_policy  = f'{pargs.ppfx}sol',
                    snmp_policy             = f'{pargs.ppfx}snmp',
                    syslog_policy           = f'{pargs.ppfx}syslog',
                    uuid_pool               = f'{pargs.ppfx}uuid',
                    virtual_kvm_policy      = f'{pargs.ppfx}vkvm',
                    virtual_media_policy    = f'{pargs.ppfx}vmedia',
                )
                if p.gen == 'M5': polVars.pop('power_policy')
                if 'fcp' in t: polVars.update({'san_connectivity_policy': 'scp'})
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
        plist = ['5108', '9508']
        for i in plist:
            polVars = dict(
                fan_control_mode = 'Balanced',
                description      = f'{pargs.ppfx}{i} {descr} Policy',
                name             = f'{pargs.ppfx}{i}',
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
            description      = f'{pargs.ppfx}uuid Pool',
            name             = f'{pargs.ppfx}uuid',
            prefix           = '000025B5-0000-0000',
            uuid_blocks      = [{
                'from':f'{pargs.pool_prefix}00-000000000000',
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
            description         = f'{pargs.ppfx}vkvm Virtual KVM Policy',
            name                = f'{pargs.ppfx}vkvm',
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
            description         = f'{pargs.ppfx}vmedia {descr} Policy',
            name                = f'{pargs.ppfx}vmedia',
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
            description = f'{pargs.ppfx}vlans {descr} Policy',
            name        = f'{pargs.ppfx}vlans',
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
                description = f'{pargs.ppfx}vsan-{i} {descr} Policy',
                name        = f'{pargs.ppfx}vsan-{i}',
                vsans       = [dict(
                    fcoe_vlan_id = i,
                    name         = f'{pargs.ppfx}vsan-{i}',
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
    # Function - Converged Stack - Build Dictionaries, Deploy Nexus, and Storage
    #=============================================================================
    def build(self, pargs, **kwargs):
        #==================================
        # Configure Nexus Devices
        #==================================
        #kwargs, pargs = nxos.nxos.config(self, pargs, **kwargs)
        #==================================
        # Configure NetApp
        #==================================
        pargs.configure_netapp = False
        pargs.configure_netapp_svm = False
        plist = ['autosupport', 'broadcast_domain', 'cluster', 'nodes', 'schedule', 'snmp', 'svm', 'volume']
        #plist = ['volume']
        for i in plist:
            kwargs, pargs = eval(f"netapp.build(i).{i}(pargs, **kwargs)")
        if pargs.configure_netapp_svm == False:
            pargs.netapp.wwpns.a    = [{'fcp-lif-01-1a':'20:0e:00:a0:98:aa:1c:8d'}, {'fcp-lif-02-1a':'20:0f:00:a0:98:aa:1c:8d'}]
            pargs.netapp.wwpns.b    = [{'fcp-lif-01-1c':'20:10:00:a0:98:aa:1c:8d'}, {'fcp-lif-02-1c':'20:11:00:a0:98:aa:1c:8d'}]
            pargs.netapp.iscsi.iqn  = 'iqn.1992-08.com.netapp:sn.57c603ffcc2811ed9ce100a098aa1c8d:vs.6'
            pargs.netapp.nvme.nqn   = 'nqn.1992-08.com.netapp:sn.57c603ffcc2811ed9ce100a098aa1c8d:discovery'
        #print(json.dumps(kwargs['immDict']['orgs'][kwargs['org']]['netapp'], indent=4))
        #exit()
        #==================================
        # Configure IMM Pools and Policies
        #==================================
        plist = list(kwargs['ezData']['pools']['allOf'][1]['properties'].keys())
        plist.remove('resource')
        plist.extend(list(kwargs['ezData']['policies']['allOf'][1]['properties'].keys()))
        pop_list = kwargs['ezData']['ezimm']['allOf'][1]['properties']['converged.pop_list']['enum']
        for i in pop_list: plist.remove(i)
        pop_list = kwargs['ezData']['ezimm']['allOf'][1]['properties']['converged.fc_pop_list']['enum']
        if re.search('fc(-nvme)?', pargs.dtype):
            if pargs.sw_mode == 'end-host': plist.remove('fc_zone')
        else:
            for i in pop_list: plist.remove(i)
        pargs.pci_order = 0
        if 'iscsi_boot' in plist:
            plist.remove('iscsi_static_target')
            plist.insert((plist.index('iscsi_boot') - 1), 'iscsi_static_target')
        for i in plist: kwargs, pargs = eval(f"imm(i).{i}(pargs, **kwargs)")
        #==================================
        # Configure Domain Profiles
        #==================================
        kwargs, pargs = imm('domain').domain(pargs, **kwargs)
        #=====================================================
        # Configure Templates/Chassis/Server Profiles
        #=====================================================
        profiles_list = ['templates', 'chassis', 'server']
        for p in profiles_list: kwargs, pargs = eval(f'imm(p).{p}(pargs, **kwargs)')
        #=====================================================
        # Return kwargs and pargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - Converged Stack - Credentials - DHCP - DNS - NTP Attributes
    #=============================================================================
    def dns_ntp(self, pargs, **kwargs):
        kwargs['deployment_type'] = 'converged'
        #=====================================================
        # Credentials
        #=====================================================
        jDict = kwargs['immDict']['wizard']['credentials'][0]
        pargs.nxosuser = jDict['nxos_username']
        pargs.stguser  = jDict['netapp_username']
        pargs.vctruser = jDict['vcenter_username']
        #=====================================================
        # DHCP, DNS, NTP, Organization
        #=====================================================
        jDict = kwargs['immDict']['wizard']['dhcp_dns_ntp'][0]
        pargs.dns_servers = [jDict['dns_server1']]
        pargs.dns_domains = jDict['dns_domains'].split(',')
        pargs.ntp_servers = [jDict['ntp_server1']]
        pargs.timezone    = jDict['timezone']
        if jDict.get('dhcp_server1'): pargs.dhcp_servers = [jDict['dhcp_server1']]
        if jDict.get('dhcp_server2'): pargs.dhcp_servers.append(jDict['dhcp_server2'])
        if jDict.get('dns_server2'): pargs.dns_servers.append(jDict['dns_server2'])
        if jDict.get('ntp_server2'): pargs.ntp_servers.append(jDict['ntp_server2'])
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
        jDict         = kwargs['immDict']['wizard']['imm_domain'][0]
        pargs.dtype   = jDict['deployment_type']
        pargs.name    = jDict['name']
        pargs.org     = jDict['organization']
        pargs.serials = [jDict['fabric_a_serial'], jDict['fabric_b_serial']]
        pargs.uplinks = jDict['uplink_ports']
        ports = jDict['uplink_ports'].split('/')[-1]
        if '-' in jDict['uplink_ports']:
            pstart = ports.split('-')[0]
            plast = ports.split('-')[1]
            plist = []
            for x in range(int(pstart),int(plast)+1):
                plist.append(x)
            pargs.uplink_list = plist
        else: pargs.uplink_list = ports.split(',')
        pargs.tags    = kwargs['ezData']['tags']
        kwargs['org'] = pargs.org
        if jDict.get('breakout_speed'): pargs.breakout_speed.eth = jDict['breakout_speed']
        else: pargs.breakout_speed.eth = '25G'
        #==================================
        # Get Moids for Fabric Switches
        #==================================
        pargs.apiMethod         = 'get'
        pargs.policy            = 'serial_number'
        pargs.purpose           = 'domain'
        pargs.names             = pargs.serials
        kwargs                  = isdk.api('serial_number').calls(pargs, **kwargs)
        pargs.serial_moids      = kwargs['pmoids']
        pargs.device_model      = pargs.serial_moids[pargs.serials[0]]['model']
        pargs.registered_device = pargs.serial_moids[pargs.serials[0]]['registered_device']
        #==================================
        # Management Protocols
        #==================================
        jDict = kwargs['immDict']['wizard']['mgmt'][0]
        pargs.log_servers   = [jDict['syslog_server1']]
        pargs.snmp_contact  = jDict['snmp_contact']
        pargs.snmp_location = jDict['snmp_location']
        pargs.snmp_servers  = [jDict['snmp_server1']]
        pargs.snmp_user     = jDict['username']
        if jDict.get('syslog_server2'): pargs.log_servers.append(jDict['syslog_server2'])
        if jDict.get('snmp_server2'): pargs.snmp_servers.append(jDict['snmp_server2'])
        #==================================
        # Pools and Policies
        #==================================
        jDict = kwargs['immDict']['wizard']['imm_policy'][0]
        pargs.local_user   = jDict['local_user']
        pargs.pool_prefix  = jDict['pool_id_prefix']
        if jDict.get('policy_prefix'): pargs.ppfx = jDict['policy_prefix']
        else: pargs.ppfx = ''
        #==================================
        # Server Profiles
        #==================================
        pargs.server_settings = []
        for i in kwargs['immDict']['wizard']['imm_profiles']:
            i = DotMap(deepcopy(i))
            pargs.server_settings.append(DotMap(
                cpu        = i.cpu_vendor,
                identifier = i.identifier,
                equipment  = i.equipment_type,
                gen        = i.generation,
                os_type    = i.os_type,
                ports      = i.domain_ports,
                profile    = i.profile_start,
                suffix     = i.suffix_digits,
                tpm        = i.tpm,
                vic_gen    = i.vic_generation,
            ))
        #=====================================================
        # Confirm if Fibre-Channel is in Use
        #=====================================================
        if re.search('(fc|fc-nvme)', pargs.dtype):
            jDict           = kwargs['immDict']['wizard']['imm_fc'][0]
            pargs.fcp_ports = jDict['fcp_ports']
            pargs.fcp_speed = jDict['fcp_speed']
            pargs.swmode    = jDict['switch_mode']
            pargs.vsans     = [jDict['vsan_a'], jDict['vsan_b']]
            if jDict.get('breakout_speed'): pargs.breakout_speed.fc = jDict['breakout_speed']
            else: pargs.breakout_speed.fc = '32G'
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - Converged Stack - NetApp Attributes
    #=============================================================================
    def netapp(self, pargs, **kwargs):
        #=====================================================
        # NetApp Cluster
        #=====================================================
        jDict      = DotMap(deepcopy(kwargs['immDict']['wizard']['ontap'][0]))
        pargs.netapp            = DotMap()
        pargs.netapp.user       = pargs.stguser
        pargs.netapp.hostPrompt = r'[\w]+::>'
        pargs.netapp.banner     = jDict.login_banner
        pargs.netapp.cluster    = jDict.cluster_name
        pargs.netapp.data_ports = deepcopy(jDict.data_ports).split(',')
        pargs.netapp.data_speed = jDict.data_speed
        pargs.netapp.data_svm   = deepcopy(jDict.data_svm)
        pargs.netapp.fcp_ports  = deepcopy(jDict.fcp_ports).split(',')
        pargs.netapp.fcp_speed  = jDict.fcp_speed
        pargs.netapp.node01     = jDict.node01
        pargs.netapp.node02     = jDict.node02
        pargs.netapp.node_list  = [deepcopy(jDict.node01), deepcopy(jDict.node02)]
        #=====================================================
        # Configure Aggregates, root volume and Mirrors
        #=====================================================
        pargs.netapp.agg1       = (deepcopy(jDict.node01).replace('-', '_')).lower() + '_1'
        pargs.netapp.agg2       = (deepcopy(jDict.node02).replace('-', '_')).lower() + '_1'
        pargs.netapp.rootv      = (deepcopy(jDict.data_svm).replace('-', '_')).lower() + '_root'
        pargs.netapp.m01        = deepcopy(pargs.netapp.rootv) + '_m01'
        pargs.netapp.m02        = deepcopy(pargs.netapp.rootv) + '_m02'
        pargs.netapp.protocols  = []
        for i in pargs.vlans:
            i = DotMap(deepcopy(i))
            if re.search('(iscsi|nfs|nvme)', i.type):
                if 'nvme' in i.type: pargs.netapp.protocols.append('nvme_of')
                else: pargs.netapp.protocols.append(i.type)
            if 'nfs' in i.type:
                pargs.netapp.nfs.network = i.network
        if 'fc' in pargs.dtype: pargs.netapp.protocols.append('fcp')
        pargs.netapp.protocols = numpy.unique(numpy.array(pargs.netapp.protocols))
        pargs.protocols = pargs.netapp.protocols
        pargs.host = deepcopy(pargs.netapp.node01)
        #==================================
        # Get Disk Information
        #==================================
        uri   = 'storage/disks'
        jData = netapp.get(uri, pargs, **kwargs)
        pargs.netapp.disk_count = jData['num_records'] - 1
        disk_name = jData['records'][0]['name']
        uri   = f'storage/disks/{disk_name}'
        jData = netapp.get(uri, pargs, **kwargs)
        pargs.netapp.disk_type = jData['type'].upper()
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
        pargs.profiles.server = DotMap()
        #=====================================================
        # Get Server Profile Names and Moids
        #=====================================================
        pargs.names = []
        for item in smap:
            for i in item['targets']: pargs.names.append(i['name'])
        pargs.names.sort()
        pargs.apiMethod = 'get'
        pargs.policy    = 'server'
        kwargs = isdk.api('server').calls(pargs, **kwargs)
        pargs.sDict = kwargs['results']
        if 'fc' in pargs.dtype:
            #=====================================================
            # Get WWPN's for vHBAs and Add to Profile Map
            #=====================================================
            for k, v in kwargs['pmoids'].items():
                pargs.apiMethod = 'get'
                pargs.apiQuery  = f"Profile.Moid eq '{v['Moid']}'"
                pargs.policy    = 'vhbas'
                pargs.purpose   = 'vhbas'
                kwargs = isdk.api(pargs.policy).calls(pargs, **kwargs)
                r = kwargs['results']
                pargs.profiles.server[k].wwpns = []
                for s in r: pargs.profiles.server[k].wwpns.append(s['Wwpn'])
        elif re.search('(iscsi|nvme-tcp)', pargs.dtype):
            #=====================================================
            # Get WWPN's for vHBAs and Add to Profile Map
            #=====================================================
            for k, v in kwargs['pmoids'].items():
                pargs.apiMethod = 'get'
                pargs.apiQuery  = f"AssignedToEntity.Moid eq '{v['Moid']}'"
                pargs.policy    = 'iqn'
                pargs.purpose   = 'iqn'
                kwargs = isdk.api(pargs.policy).calls(pargs, **kwargs)
                r = kwargs['results']
                pargs.profiles.server[k].iqn = r['IqnId']
        pargs.pop('apiQuery')
        #=====================================================
        # Run Lun Creation Class
        #=====================================================
        #netapp.build('lun').lun(pargs, **kwargs)
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - Wizard Worksheet Policy Settings
    #=============================================================================
    def settings(self, **kwargs):
        # Get Variables from Library
        kwargs['validateData'] = kwargs['ezData'][f'wizard.{self.type}']['allOf'][1]['properties']
        # Build Dictionary of Policy Variables
        polVars = ezfunctions.process_kwargs(**kwargs)

        # Add Policy Variables to immDict
        kwargs['class_path'] = f'{self.type}'
        kwargs = ezfunctions.ez_append_wizard(polVars, **kwargs)
        return kwargs


    #=============================================================================
    # Function - Converged Stack - VLAN Attributes
    #=============================================================================
    def vlans(self, pargs, **kwargs):
        #==================================
        # Build VLAN Dictionary
        #==================================
        pargs.vlans = []
        for i in kwargs['immDict']['wizard']['vlans']:
            i = DotMap(deepcopy(i))
            netwk = '%s' % ipaddress.IPv4Network(i.network, strict=False)
            vDict = dict(
                configure = i.configure_network,
                gateway   = i.network.split('/')[0],
                name      = i.name,
                netmask   = ((ipaddress.IPv4Network(netwk)).with_netmask).split('/')[1],
                network   = netwk,
                prefix    = i.network.split('/')[1],
                switch    = i.switch_type,
                type      = i.vlan_type,
                vlan_id   = i.vlan_id,
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
            if i.get('controller_range'): vDict.update({'controller':iprange(i.controller_range)})
            if i.get('pool_range') and re.search('(inband|ooband)', i.vlan_type):
                vDict.update({'pool':iprange(i.pool_range)})
            if i.get('server_range'): vDict.update({'server':iprange(i.server_range)})
            pargs.vlans.append(vDict)
        pargs.inband = DotMap()
        pargs.ooband = DotMap()
        for i in pargs.vlans:
            i = DotMap(deepcopy(i))
            if re.search('(inband|ooband)', i.type):
                pargs[i.type].update(i)
        pargs.ranges = []
        for i in kwargs['immDict']['wizard']['ranges']:
            i = DotMap(deepcopy(i))
            pargs.ranges.append(dict(
                configure = i.configure_network,
                name      = i.name_prefix,
                vlan_list = i.vlan_range
            ))
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
    def fw(self, pargs, **kwargs):
        # Build Dictionary
        #print(pargs.sDict)
        print(pargs.physical.servers)
        print('finished')
        exit()
        models = []
        for i in  pargs.physical.server:
            models.append('model')
        models = numpy.unique(numpy.array(models))
        swMoids = []
        pargs.apiMethod = 'get'
        pargs.policy = 'distributable'
        pargs.purpose = 'firmware'
        pargs.version = '4.2(3b)'
        for m in models:
            pargs.apiQuery = f"Version eq {pargs.fw_version} and contains(SupportedModels, '{m}')"
            kwargs = isdk.api(pargs.policy).calls(pargs, **kwargs)
            swMoid = kwargs['pmoids']
        descr = (self.type.replace('_', ' ')).upper()
        btemplates = []
        for i in pargs.server_settings:
            if re.search('M[5-9]', i.gen) and i.tpm == 'True': btemplates.append(f'{i.gen}-{i.cpu}-virtual-tpm')
            elif re.search('M[5-9]', i.gen): btemplates.append(f'{i.gen}-{i.cpu}-virtual')
        btemplates = numpy.unique(numpy.array(btemplates))
        for i in btemplates:
            polVars = dict(
                baud_rate           = 115200,
                bios_template       = i,
                console_redirection = f'serial-port-a',
                description         = f'{pargs.ppfx}{i} {descr} Policy',
                name                = f'{pargs.ppfx}{i}',
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


