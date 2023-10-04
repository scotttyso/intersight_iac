#"""
# Script will Create Virtual Machine(s) within the AzureStack HCI Cluster.
#  * Bogna Trimouillat - btrimoui@cisco.com
#  * Tyson Scott 10/1/2023 - tyscott@cisco.com
#"""

#=============================================================================
# JSON File is a Required Parameter
# Pull in JSON Content
#=============================================================================
param (
    [switch]$force,
    [string]$j=$(throw "-j <json_file> is required.")
)
#=============================================================================
# Start Log, Configure PowerCLI, Setup Variables
#=============================================================================
Start-Transcript -Path ".\Logs\$(get-date -f "yyyy-MM-dd_HH-mm-ss")_$($env:USER).log" -Append -Confirm:$false
$jdata = Get-Content -Path $j | ConvertFrom-Json
#=============================================================================
# Obtain Username and Password
#=============================================================================
if (Test-Path -Path ${env:HOME}\powercli.Cred) {
    $credential = Import-CliXml -Path "${env:HOME}\powercli.Cred"
}
else {
    $credential = Get-Credential
    $credential | Export-CliXml -Path "${env:HOME}\powercli.Cred"
}
$cluster = $jdata.cluster
Write-Host "Beginning Process to Create Virtual Machines on Cluster: '$cluster'" -ForegroundColor Yellow
$results = Invoke-Command $cluster -Credential $credential -scriptblock {
    Write-Host "Enabling CredSSP on $($Using:cluster):" -ForegroundColor Green
    Enable-WSManCredSSP -Role Server -Force | Out-Null
    $wsman_creds =  Get-WSManCredSSP
    if ($wsman_creds -match "This computer is configured to receive credentials from a remote client computer") {
        Write-Host " * Successfully Enabled CredSSP." -ForegroundColor Cyan
    } else {
        Write-Host " * Failed to Enable CredSSP" -ForegroundColor Red
        Write-Host "   Use the command: Enable-WSManCredSSP -Role Server -Force" -ForegroundColor Red
        Write-Host "   To Determine Why the Cluster: '$($Using:cluster)' Failed to Enable CredSSP." -ForegroundColor Red
        Return New-Object PsObject -property @{Completed=$False}
    }
    Return New-Object PsObject -property @{Completed=$True}
}
if ($results.Completed -eq $True) { 
    $results = Invoke-Command $cluster -Credential $credential -authentication Credssp -scriptblock {
        $jdata     = $Using:jdata
        $csv_path  = ((Get-ClusterSharedVolume).SharedVolumeInfo).FriendlyVolumeName
        $vm_switch = (Get-VMSwitch).Name
        foreach ($vm in $jdata.virtual_machines) {
            $vm_name   = $vm.name
            $vm_path   = "$csv_path\VirtualMachines\$VMName"
            $vhd_path  = "$vm_path\$vm_name-Disk01.vhdx"
            $vm_memory = $vm.memory
            $vm_disk   = $vm.disk_size
            $vm_exist = Get-VM -Name $vm_name
            if (!($vm_exist)) {
                Write-Host " * Adding Virtual Machine '$vm_name' to Cluster: $($Using:cluster)" -ForegroundColor Green
                Write-Host " * Creating Virtual Machine $vm_name VHDX $vhd_path ..." -ForegroundColor Green
                New-VHD -Path $vhd_path -Fixed -SizeBytes "${vm_disk}GB"
                Write-Host " * Creating Virtual Machine $vm_name with memory capacity '$vm_memory ... " -ForegroundColor Green
                New-VM -Name $vm_name -Path $vm_path -MemoryStartupBytes "${vm_memory}GB" -VHDPath $vhd_path -Generation 2 -SwitchName $vm_switch
                $storage_policy_id = (Get-StorageQosPolicy -Name $jdata.storage_qos_policy).PolicyId
                Write-Host " * Setting QoS Policy for Virtual Machine $vm_name ..." -ForegroundColor Green
                Get-VM -VMName $vm_name | Get-VMHardDiskDrive | Set-VMHardDiskDrive -QoSPolicyID $storage_policy_id
                Write-Host " * Adding Virtual Machine $vm_name to Clustering..." -ForegroundColor Green
                Get-VM -Name $vm_name | Add-ClusterVirtualMachineRole -Name $vm_name
            } else {
                Write-Host " * Virtual Machine '$vm_name' in Cluster: $($Using:cluster), already exists." -ForegroundColor Cyan
            }
        }
        Write-Host "Disabling CredSSP" -ForegroundColor Yellow
        Disable-WSManCredSSP -Role Server
        Write-Host " * Verifying that CredSSP are disabled on target cluster server..." -ForegroundColor Yellow
        $wsman_creds =  Get-WSManCredSSP
        if ($wsman_creds -match "The machine is not configured") {
            Write-Host " * Successfully Disabled CredSSP." -ForegroundColor Yellow
        } else {
            Write-Host " * Failed to Disable CredSSP" -ForegroundColor Red
            Write-Host "   Use the command: Disable-WSManCredSSP -Role Server" -ForegroundColor Red
            Write-Host "   To Determine Why CredSSP Failed to Disable on Host: $($env:COMPUTERNAME)." -ForegroundColor Red
            Return New-Object PsObject -property @{Completed=$False}
        }
        Return New-Object PsObject -property @{Completed=$True}
    }
}
Stop-Transcript
if ($results.Completed -eq $True) { 
    Write-Host "Completed Process to Create Virtual Machines on Cluster: '$cluster'" -ForegroundColor Yellow
    Exit 0
} else {
    Write-Host "Failed to Complete the Process to Create Virtual Machines on Cluster: '$cluster'.  Review the Logs to Investigate." -ForegroundColor Red
    Exit 1
}
