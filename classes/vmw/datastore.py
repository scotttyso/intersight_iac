"""
* *******************************************************
* Copyright (c) VMware, Inc. 2016-2018. All Rights Reserved.
* SPDX-License-Identifier: MIT
* *******************************************************
*
* DISCLAIMER. THIS PROGRAM IS PROVIDED TO YOU "AS IS" WITHOUT
* WARRANTIES OR CONDITIONS OF ANY KIND, WHETHER ORAL OR WRITTEN,
* EXPRESS OR IMPLIED. THE AUTHOR SPECIFICALLY DISCLAIMS ANY IMPLIED
* WARRANTIES OR CONDITIONS OF MERCHANTABILITY, SATISFACTORY QUALITY,
* NON-INFRINGEMENT AND FITNESS FOR A PARTICULAR PURPOSE.
"""

__author__ = 'VMware, Inc.'

import pyVim.task
from com.vmware.vcenter_client import Host
from pyVmomi import vim # pyright: ignore


def detect_nfs_datastore_on_host(context, datastore_name, host_name, pargs):
    # Use vAPI find the Host managed identities
    host_summaries = context.client.vcenter.Host.list(
        Host.FilterSpec(names=set([host_name])))

    for host_summary in host_summaries:
        # Convert the host identifier into a ManagedObject
        host = host_summary.host
        host_mo = vim.HostSystem(host, context.soap_stub)

        for datastore_mo in host_mo.datastore:
            if (datastore_mo.name == datastore_name and
                datastore_mo.summary.type == 'NFS'):
                datastore = datastore_mo._moId
                print("Detected NFS Volume '{}' as {} on Host '{}' ({})".
                      format(datastore_name, datastore, host_name, host))
                pargs.esxhosts[host_name].datastores[datastore_name] = datastore
                return True, pargs

    print("NFS Volume '{}' missing on Host '{}'".format(datastore_name, host_name))
    return False, pargs


def cleanup_nfs_datastore(context):
    """Cleanup NFS datastore after running vcenter samples"""
    # Remove NFS datastore from each Host
    host1_name = context.testbed.config['ESX_HOST1']
    host2_name = context.testbed.config['ESX_HOST2']
    names = set([host1_name, host2_name])

    datastore_name = context.testbed.config['NFS_DATASTORE_NAME']

    # Use vAPI find the Host managed identities
    host_summaries = context.client.vcenter.Host.list(
        Host.FilterSpec(names=names))

    for host_summary in host_summaries:
        # Convert the host identifier into a ManagedObject
        host = host_summary.host
        host_mo = vim.HostSystem(host, context.soap_stub)

        for datastore_mo in host_mo.datastore:
            if datastore_mo.name == datastore_name:
                datastore_system = host_mo.configManager.datastoreSystem
                datastore_system.RemoveDatastore(datastore_mo)
                print("Removed NFS Volume '{}' ({}) from Host '{}' ({})".
                      format(datastore_name, datastore_mo._moId,
                             host_mo.name, host_mo._moId))

                # Remote NFS Datastore at the vCenter level
                # TODO Do we need to do this?


def setup_nfs_datastore_on_host(context, datastore_name, host_name, pargs):
    """Mount the NFS volume on one ESX hosts using the VIM API."""
    host    = pargs.esxhosts[host_name].moid
    host_mo = vim.HostSystem(host, context.soap_stub)

    datastore_system = host_mo.configManager.datastoreSystem
    try:
        datastore_mo = datastore_system.CreateNasDatastore(
            vim.host.NasVolume.Specification(remoteHost=pargs.netapp.nfs.ip,
                                             remotePath=f'/{datastore_name}',
                                             localPath=datastore_name,
                                             accessMode=vim.host.MountInfo.AccessMode.readWrite,
                                             type=vim.host.FileSystemVolume.FileSystemType.NFS))

        print("Added NFS Volume '{}' ({}) to Host '{}' ({})".
              format(datastore_name, datastore_mo._moId, host_name, host))
        return datastore_mo._moId
    except vim.fault.AlreadyExists as e:
        print("NFS Volume '{}' already exists on Host '{}' ({})".
              format(datastore_name, host_name, host))
        for datastore_mo in host_mo.datastore:
            info = datastore_mo.info
            if (isinstance(info, vim.host.NasDatastoreInfo) and
                           info.nas.remoteHost == pargs.netapp.nfs.ip and
                           info.nas.remotePath == f'/{datastore_name}'):
                if info.name == datastore_name:
                    print("Found NFS Volume '{}' ({}) on Host '{}' ({})".
                          format(datastore_name, datastore_mo._moId,
                                 host_name, host_mo._moId))
                    return datastore_mo._moId
                else:
                    print("Found NFS remote host '{}' and path '{}' on Host '{}' ({}) as '{}'".
                          format(pargs.netapp.nfs.ip, f'/{datastore_name}', host_name,
                                 host_mo._moId, info.name))

                    print("Renaming NFS Volume '{}' ({}) to '{}'".
                          format(info.name, datastore_mo._moId, datastore_name))
                    task = datastore_mo.Rename(datastore_name)
                    pyVim.task.WaitForTask(task)

        # TODO Find the datastore identifier for the NFS volume and return it
        return None


def detect_vmfs_datastore(context, host_name, datastore_name):
    """Find VMFS datastore given host and datastore names"""
    names = set([host_name])

    # Use vAPI find the Host managed identities
    host_summaries = context.client.vcenter.Host.list(
        Host.FilterSpec(names=names))

    for host_summary in host_summaries:
        # Convert the host identifier into a ManagedObject
        host = host_summary.host
        host_mo = vim.HostSystem(host, context.soap_stub)

        for datastore_mo in host_mo.datastore:
            if (datastore_mo.name == datastore_name and
                datastore_mo.summary.type == 'VMFS'):
                datastore = datastore_mo._moId
                print("Detected VMFS Volume '{}' as {} on Host '{}' ({})".
                      format(datastore_name, datastore, host_name, host))
                context.testbed.entities['HOST_VMFS_DATASTORE_IDS'][host_name] \
                    = datastore
                return True

    print("VMFS Volume '{}' missing on Host '{}'".
          format(datastore_name, host_name))
    return False


def create_vmfs_datastore(context, pargs):
    datastore_name = 'unknown'
    """Find VMFS datastore given host and datastore names"""
    #context.testbed.entities['HOST_VMFS_DATASTORE_IDS'] = {}
    for host_summary in pargs.host_summaries:
        # Convert the host identifier into a ManagedObject
        esx_host = host_summary.name
        host     = host_summary.host
        host_mo  = vim.HostSystem(host, context.soap_stub)

        hba_mo = host_mo.configManager.hbaSystem
        datastore_system = host_mo.configManager.datastoreSystem
        print(esx_host)
        print(host)
        print(host_mo)
        datastore_mo = datastore_system.CreateVmfsDatastore(
        )
        print('end of file')
        exit()
        datastore_name = esx_host.split('.')[0] + '-ds1'
        datastore_spec = vim.Datastore.ConfigSpecEx()
        vmfs_datastores = dict([(datastore_mo.name, datastore_mo)
                                for datastore_mo in host_mo.datastore
                                if datastore_mo.summary.type == 'VMFS'])
        print(vmfs_datastores)
        exit()
        # The VMFS volume exists.  No need to do anything
        if datastore_name in vmfs_datastores:
            datastore = vmfs_datastores[datastore_name]._moId
            print("Detected VMFS Volume '{}' as {} on Host '{}' ({})".
                format(datastore_name, datastore, esx_host, host))
            context.testbed.entities['HOST_VMFS_DATASTORE_IDS'][esx_host] \
                = datastore
            return True

        # Rename a VMFS datastore
        if len(vmfs_datastores) > 0:
            datastore_mo = list(vmfs_datastores.values())[0]
            datastore = datastore_mo._moId
            print("Renaming VMFS Volume '{}' ({}) on Host '{}' ({}) to '{}'".
                format(datastore_mo.name, datastore,
                        esx_host, host, datastore_name))
            task = datastore_mo.Rename(datastore_name)
            pyVim.task.WaitForTask(task)
            return True

        return False

def setup_vmfs_datastore(context, pargs):
    datastore_name = 'unknown'
    print(pargs.host_summaries)
    """Find VMFS datastore given host and datastore names"""
    #context.testbed.entities['HOST_VMFS_DATASTORE_IDS'] = {}
    for host_summary in pargs.host_summaries:
        # Convert the host identifier into a ManagedObject
        esx_host = host_summary.name
        host     = host_summary.host
        host_mo  = vim.HostSystem(host, context.soap_stub)

        vmfs_datastores = dict([(datastore_mo.name, datastore_mo)
                                for datastore_mo in host_mo.datastore
                                if datastore_mo.summary.type == 'VMFS'])
        print(vmfs_datastores)
        exit()
        # The VMFS volume exists.  No need to do anything
        if datastore_name in vmfs_datastores:
            datastore = vmfs_datastores[datastore_name]._moId
            print("Detected VMFS Volume '{}' as {} on Host '{}' ({})".
                format(datastore_name, datastore, esx_host, host))
            context.testbed.entities['HOST_VMFS_DATASTORE_IDS'][esx_host] \
                = datastore
            return True

        # Rename a VMFS datastore
        if len(vmfs_datastores) > 0:
            datastore_mo = list(vmfs_datastores.values())[0]
            datastore = datastore_mo._moId
            print("Renaming VMFS Volume '{}' ({}) on Host '{}' ({}) to '{}'".
                format(datastore_mo.name, datastore,
                        esx_host, host, datastore_name))
            task = datastore_mo.Rename(datastore_name)
            pyVim.task.WaitForTask(task)
            return True

        return False

