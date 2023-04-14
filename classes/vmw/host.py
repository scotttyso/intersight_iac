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
from com.vmware.vcenter_client import (Folder, Host)
from pyVmomi import vim # pyright: ignore


#=====================================================
# Function - Create Host
#=====================================================
def create_host_vapi(context, esx_host, pargs):
    """
    Adds a single Host to the vCenter inventory under the named Datacenter
    using vAPI.
    """
    create_spec = Host.CreateSpec(
        hostname =esx_host,
        user_name=pargs.esx.username,
        password =pargs.esx.password,
        folder   =pargs.vcenter.host.folder,
        thumbprint_verification=Host.CreateSpec.ThumbprintVerification.NONE)
    host = context.client.vcenter.Host.create(create_spec)
    pargs.esxhosts[esx_host].moid = host
    print(f"\nCreated Host '{host}' ({esx_host})")
    return pargs


#=====================================================
# Function - Detect Existing Host
#=====================================================
def detect_host(context, host_name, pargs):
    """Find host based on host name"""
    names = set([host_name])

    host_summaries = context.client.vcenter.Host.list(
        Host.FilterSpec(names=names))
    if len(host_summaries) > 0:
        host = host_summaries[0].host
        print("Detected Host '{}' as {}".format(host_name, host))
        context.testbed.entities['HOST_IDS'][host_name] = host
        return True
    else:
        print("Host '{}' missing".format(host_name))
        return False


#=====================================================
# Function - Detect Existing Hosts
#=====================================================
def detect_hosts(context, esx_hosts, pargs):
    """Find hosts based on hostnames"""
    pargs.host_summaries = context.client.vcenter.Host.list(
        Host.FilterSpec(names=set(esx_hosts)))
    if len(pargs.host_summaries) > 0:
        print(f'\n{"-"*91}\n')
        for i in pargs.host_summaries:
            print(f"Detected Host '{i.name}' as {i.host}")
        print(f'\n{"-"*91}\n')
        return pargs
    else: return pargs


#=====================================================
# Function - Get Moid for Host Folder in Cluster
#=====================================================
def host_folders(context, pargs):
    """Define Cluster Host Folder"""
    folder_summaries = context.client.vcenter.Folder.list(
        Folder.FilterSpec(type=Folder.Type.HOST, datacenters=set([pargs.vcenter.datacenter.moid])))
    print(folder_summaries)
    pargs.vcenter.host.folder = folder_summaries[0].folder
    for i in folder_summaries:
        print(f"\nDetected Host Folder '{i.name}' as {i.folder}")
    return pargs


#=====================================================
# Function - Move Host into Cluster
#=====================================================
def move_host_into_cluster_vim(context, cluster_name, esx_host, pargs):
    """Use vim api to move host to another cluster"""
    TIMEOUT = 30  # sec

    host         = pargs.esxhosts[esx_host].moid
    host_mo      = vim.HostSystem(host, context.soap_stub)

    # Move the host into the cluster
    if not host_mo.runtime.inMaintenanceMode:
        task = host_mo.EnterMaintenanceMode(TIMEOUT)
        pyVim.task.WaitForTask(task)
    print(f"\nHost '{host}' ({esx_host}) in maintenance mode")

    cluster = pargs.vcenter.cluster[cluster_name].moid
    cluster_mo = vim.ClusterComputeResource(cluster, context.soap_stub)
    print(cluster_mo)
    task = cluster_mo.MoveInto([host_mo])
    pyVim.task.WaitForTask(task)
    print(f"\nHost '{host}' ({esx_host}) moved into Cluster {cluster} ({cluster_name})")

    task = host_mo.ExitMaintenanceMode(TIMEOUT)
    pyVim.task.WaitForTask(task)
    print(f"\nHost '{host}' ({esx_host}) out of maintenance mode")


#=====================================================
# Function - Remove Hosts
#=====================================================
def remove_hosts(context):
    """Delete hosts after sample run"""
    host1_name = context.testbed.config['ESX_HOST1']
    host2_name = context.testbed.config['ESX_HOST2']
    names = set([host1_name, host2_name])

    host_summaries = context.client.vcenter.Host.list(
        Host.FilterSpec(names=names))
    print('Found {} Hosts matching names {}'.
          format(len(host_summaries), ', '.
                 join(["'{}'".format(n) for n in names])))

    for host_summary in host_summaries:
        host = host_summary.host
        print("Deleting Host '{}' ({})".format(host_summary.name, host))
        context.client.vcenter.Host.delete(host)

