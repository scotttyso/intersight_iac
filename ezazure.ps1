# sudo apt-get -y install gss-ntlmssp
# pwsh -Command 'Install-Module -Name PSWSMan'
#"""
#Script will complete host configuration after OS Installation.
#Includes All OS Customization of the AzureStack HCI Cisco Validated Design
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
$feature_list = ("Hyper-V", "Failover-Clustering", "Data-Center-Bridging", "Bitlocker" , "FS-FileServer",
    "FS-SMBBW", "Hyper-V-PowerShell", "RSAT-AD-Powershell", "RSAT-Clustering-PowerShell", "NetworkATC",
    "NetworkHUD", "FS-DATA-Deduplication")
$jdata = Get-Content -Path $j | ConvertFrom-Json
$username = $jdata.username
#=====================================================
# Start Log and Configure PowerCLI
#=====================================================
#Start-Transcript -Path ".\Logs\$(get-date -f "yyyy-MM-dd_HH-mm-ss")_$($env:USER).log" -Append -Confirm:$false

#=====================================================
# Setup Credentials and Login to Hosts
#=====================================================
$password = ConvertTo-SecureString $env:windows_administrator_password -AsPlainText -Force;
$credential = New-Object System.Management.Automation.PSCredential ($username,$password);
Get-PSSession | Remove-PSSession | Out-Null
foreach ($node in $jdata.node_list) {
    Write-Host "Logging into Host $($node)" -ForegroundColor Yellow
    New-PSSession -ComputerName $node -Credential $credential
    #New-PSSession -HostName $node -UserName $username
    #New-PSSession -HostName $node -UserName $username -KeyFilePath $env:HOME/.ssh/id_ed25519
}
$sessions = Get-PSSession
$sessions | Format-Table | Out-String|ForEach-Object {Write-Host $_}
$session_results = Invoke-Command $sessions -ScriptBlock {
    $jdata = $Using:jdata
    ##########
    Write-Host "$($env:COMPUTERNAME) Beginning time zone '$($jdata.timezone)' Configuration." -ForegroundColor Yellow
    $tz = Get-TimeZone
    if (!($tz.Id -eq $jdata.timezone)) {Set-Timezone $jdata.timezone}
    $tz = Get-TimeZone
    if ($tz.Id -eq $jdata.timezone) {
        Write-Host " * $($env:COMPUTERNAME) Successfully Set Timezone to '$($jdata.timezone)'." -ForegroundColor Green
    } else {
        Write-Host " * $($env:COMPUTERNAME) Failed to Set Timezone to '$($jdata.timezone)'.  Exiting..." -ForegroundColor Red
        Return New-Object PsObject -property @{Completed=$False}
    }
    Write-Host "$($env:COMPUTERNAME) Compeleted time zone '$($jdata.timezone)' Configuration." -ForegroundColor Yellow
    ##########
    Write-Host "$($env:COMPUTERNAME) Beginning Remote Desktop Network Firewall Rule(s) Configuration." -ForegroundColor Yellow
    $network_firewall = Get-NetFirewallRule -DisplayGroup "Remote Desktop"
    foreach ($item in $network_firewall) {
        if (!($item.Enabled -eq $true)) { Enable-NetFirewallRule -Name $item.Name }
    }
    $network_firewall = Get-NetFirewallRule -DisplayGroup "Remote Desktop"
    foreach ($item in $network_firewall) {
        if ($item.Enabled -eq $true) {
            Write-Host " * $($env:COMPUTERNAME) Successfully Configured Remote Desktop Network Firewall Rule $($item.Name)." -ForegroundColor Green
        } else {
            Write-Host " * $($env:COMPUTERNAME) Failed on Enabling Remote Desktop Network Firewall Rule $($item.Name).  Exiting..." -ForegroundColor Red
            Return New-Object PsObject -property @{Completed=$False}
        }
    }
    Write-Host "$($env:COMPUTERNAME) Completed Remote Desktop Network Firewall Rule(s) Configuration." -ForegroundColor Yellow
    ##########
    Write-Host "$($env:COMPUTERNAME) Beginning Check for Required Windows Features and Restarting Host." -ForegroundColor Yellow
    $new_list = [System.Collections.ArrayList]@()
    $reboot = $False
    $wf = Get-WindowsFeature | Select-Object *
    foreach ($item in $Using:feature_list) {
        if ($wf | Where-Object {$_.Name -eq $item}) {
            if (!(($wf | Where-Object {$_.Name -eq $item}).Installed -eq $true)) { $new_list.Add($item) }
        } else { Write-Host "$($env:COMPUTERNAME) Unknown Feature '$($item)'" -ForegroundColor Red
        }
    }
    if ($new_list.Length -gt 0) {
        Add-WindowsFeature -Name $new_list -IncludeAllSubFeature -IncludeManagementTools -Restart
        $reboot = $True
    }
    Write-Host "$($env:COMPUTERNAME) Completed Check for Required Windows Features and Restarted Host." -ForegroundColor Yellow
    Return New-Object PsObject -property @{Completed=$True;Reboot=$reboot}
}
#==============================================
# Setup Environment for Next Loop
#==============================================
#$session_results | Format-Table | Out-String|ForEach-Object {Write-Host $_}
$nodes = [System.Collections.ArrayList]@()
$reboot_count = 0
foreach ($result in $session_results) {
    if ($result.Completed -eq $True) { $nodes.Add($result.PSComputerName)}
    if ($result.Reboot -eq $True) { $reboot_count++ | Out-Null }
}
Get-PSSession | Remove-PSSession | Out-Null
#==============================================
# Confirm All Nodes Completed
#==============================================
if (!$nodes.Length -eq $original_nodes.Length) { Exit 1 }
#==============================================
# Sleep 10 Minutes if reboot_count gt 0
#==============================================
if ($reboot_count -gt 0) {
    Write-Host "Sleeping for 10 Minutes to Wait for Server Reboots." -ForegroundColor Yellow
    Start-Sleep -Seconds 600
}
foreach ($node in $nodes) {
    Write-Host "Logging into Host $($node)" -ForegroundColor Yellow
    New-PSSession -HostName $node -Credential $credential
}
$sessions = Get-PSSession
$sessions | Format-Table | Out-String|ForEach-Object {Write-Host $_}
$session_results = Invoke-WUJob -ComputerName $sessions -Script {
    Import-Module PSWindowsUpdate;
    Install-WindowsUpdate -MicrosoftUpdate -AcceptAll -AutoReboot
    Return New-Object PsObject -property @{Completed=$True;Reboot=$reboot}
} -RunNow -Confirm:$false | Out-File "\server\share\logs\$computer-$(Get-Date -f yyyy-MM-dd)-MSUpdates.log" -Force
#==============================================
# Setup Environment for Next Loop
#==============================================
$nodes = [System.Collections.ArrayList]@()
$reboot_count = 0
foreach ($result in $session_results) {
    if ($result.Completed -eq $True) { $nodes.Add($result.PSComputerName)}
    if ($result.Reboot -eq $True) { $reboot_count++ | Out-Null }
}
Get-PSSession | Remove-PSSession | Out-Null
#==============================================
# Confirm All Nodes Completed
#==============================================
if (!$nodes.Length -eq $jdata.node_list.Length) { Exit 1 }
#==============================================
# Sleep 10 Minutes if reboot_count gt 0
#==============================================
if ($reboot_count -gt 0) {
    Write-Host "Sleeping for 10 Minutes to Wait for Server Reboots." -ForegroundColor Yellow
    Start-Sleep -Seconds 600
}
foreach ($node in $jdata.node_list) {
    Write-Host "Logging into Host $($node)" -ForegroundColor Yellow
    New-PSSession -ComputerName $node -Credential $credential
}
$sessions = Get-PSSession
$sessions | Format-Table | Out-String|ForEach-Object {Write-Host $_}
$session_results = Invoke-Command $sessions -ScriptBlock {
    Function RegistryKey {
        Param([string]$registry_path, [object]$key)
        if(-not(Test-Path -path $registry_path)){ New-Item $registry_path | Out-Null }
        $reg = Get-ItemProperty -Path $registry_path
        if ($null -eq $reg.($key.name)) {
            $reg | New-Itemproperty -Name $key.name -Value $key.value -PropertyType $key.type | Out-Null
        } elseif (!($reg.($key.name) -eq $key.value)) {
            $reg | Set-ItemProperty -Name $key.name -Value $key.value | Out-Null
        }
        $reg = Get-ItemProperty -Path $registry_path
        if ($reg.($key.name) -eq $key.value) {
            Write-Host " * $($env:COMPUTERNAME) Successfully Set '$registry_path\$($key.name)' to '$($key.value)'." -ForegroundColor Green
        } else {
            Write-Host " * $($env:COMPUTERNAME) Failed to Set '$registry_path\$($key.name)' to '$($key.value)'." -ForegroundColor Red
            $exit_count++ | Out-Null
            Return New-Object PsObject -property @{Completed=$False}
        }
    }
    $jdata = $Using:jdata
    ##########
    Write-Host "$($env:COMPUTERNAME) Beginning Check for Windows Features..." -ForegroundColor Yellow
    $wf = Get-WindowsFeature | Select-Object *
    foreach ($item in $Using:feature_list) {
        if (!(($wf | Where-Object {$_.Name -eq $item}).Installed -eq $true)) {
            Write-Host "Failed on Enabling Windows Feature $item.  Exiting..." -ForegroundColor Red
            Return New-Object PsObject -property @{Completed=$False}
        }
    }
    Write-Host "$($env:COMPUTERNAME) Completed Check for Windows Features..." -ForegroundColor Yellow
    ##########
    Write-Host "$($env:COMPUTERNAME) Beginning Secure Boot State Check." -ForegroundColor Yellow
    $sb = Confirm-SecureBootUEFI
    if (!($sb -eq $true)) {
        Write-Host "$($env:COMPUTERNAME) Secure Boot State is not Enabled.  Exiting..." -ForegroundColor Red
        Return New-Object PsObject -property @{Completed=$False}
    }
    Write-Host "$($env:COMPUTERNAME) Completed Secure Boot State Check." -ForegroundColor Yellow
    ##########
    Write-Host "$($env:COMPUTERNAME) Beginning Remote Desktop Access Configuration." -ForegroundColor Yellow
    $registry_path = "HKLM:\System\CurrentControlSet\Control\Terminal Server"
    $key = New-Object PsObject -property @{name="fDenyTSConnections"; value=0; type="Dword" }
    RegistryKey $registry_path $key
    Write-Host "$($env:COMPUTERNAME) Completed Remote Desktop Access Configuration." -ForegroundColor Yellow
    ##########
    Write-Host "$($env:COMPUTERNAME) Beginning Memory Crashdump Registry settings Configuring." -ForegroundColor Yellow
    $keys = ("CrashDumpEnabled", "FilterPages")
    $registry_path = "HKLM:\System\CurrentControlSet\Control\CrashControl"
    foreach ($item in $keys) {
        $key = New-Object PsObject -property @{name=$item; value=1; type="Dword" }
        RegistryKey $registry_path $key
    }
    Write-Host "$($env:COMPUTERNAME) Completed Memory Crashdump Registry settings Configuring." -ForegroundColor Yellow
    ##########
    Write-Host "$($env:COMPUTERNAME) Beginning Windows Secure Core Configuration." -ForegroundColor Yellow
    $registry_path = "HKLM:\SYSTEM\CurrentControlSet\Control\DeviceGuard\Scenarios\HypervisorEnforcedCodeIntegrity"
    $key = New-Object PsObject -property @{name="Enabled"; value=1; type="Dword" }
    RegistryKey $registry_path $key
    $key = New-Object PsObject -property @{name="WasEnabledBy"; value=0; type="Dword" }
    RegistryKey $registry_path $key
    $registry_path = "HKLM:\SYSTEM\CurrentControlSet\Control\DeviceGuard\Scenarios\SystemGuard"
    $key = New-Object PsObject -property @{name="Enabled"; value=1; type="Dword" }
    RegistryKey $registry_path $key
    Write-Host "$($env:COMPUTERNAME) Completed Windows Secure Core Configuration." -ForegroundColor Yellow
    ###
    # MSINFo32.EXE on page 78
    Write-Host "$($env:COMPUTERNAME) Beginning Retrieval of physical NIC port names." -ForegroundColor Yellow
    $adapter_list = [System.Collections.ArrayList]@("SlotID 2 Port 1", "SlotID 2 Port 2")
    $gna = Get-NetAdapter
    foreach ($adapter in $adapter_list) {
        if ($gna | Where-Object {$_.Name -eq $adapter -and $_.Status -eq "Up" -and $_.LinkSpeed -eq "100 Gbps"}) {
            Write-Host " * $($env:COMPUTERNAME) Matched NetAdapter $adapter." -ForegroundColor Green
        } else {
            Write-Host " * $($env:COMPUTERNAME) Failed to Match NetAdapter '$adapter' with Status: 'Up', LinkSpeed: '100 Gbps'.  Exiting..." -ForegroundColor Red
            Get-NetAdapter | Format-Table Name, InterfaceDescription, Status, MacAddress, LinkSpeed
            Return New-Object PsObject -property @{Completed=$False}
        }
    }
    Write-Host "$($env:COMPUTERNAME) Completed Retrieval of physical NIC port names." -ForegroundColor Yellow
    Write-Host "$($env:COMPUTERNAME) Beginning Create and Deploy Standalone Network ATC Intent." -ForegroundColor Yellow
    # CONFIRM ITEMS
    # Variables for Storage VLANs
    # $jdata.storage_vlans[0].vlan_id
    # $jdata.storage_vlans[1].vlan_id
    $gnis = Get-NetIntentStatus
    Write-Host "$($env:COMPUTERNAME) Beginning Network ATC Intent Status Configuration." -ForegroundColor Yellow
    if (!($gnis | Where-Object {$_.IntentName -eq "mgmt_compute_storage" -and $_.ConfigurationStatus -eq "Success" -and $_.ProvisioningStatus -eq "Completed" -and $_.IsComputeIntentSet -eq $True -and $_.IsManagementIntentSet -eq $True -and $_.IsStorageIntentset -eq $True -and $_.IsStretchIntentSet -eq $True})) {
        $AdapterOverride = New-NetIntentAdapterPropertyOverrides
        $AdapterOverride.NetworkDirectTechnology = 4
        $AdapterOverride
        $QoSOverride = New-NetIntentQoSPolicyOverRides
        $QoSOverride.PriorityValue8021Action_SMB = 4
        $QoSOverride.PriorityValue8021Action_Cluster = 5
        $QoSOverride
        $StorageOverride = new-NetIntentStorageOverrides
        $StorageOverride.EnableAutomaticIPGeneration = $false
        $StorageOverride
        $null = Add-NetIntent -AdapterName $adapter_list -Management -Compute -Storage -StorageVlans $jdata.storage_vlans[0].vlan_id, $jdata.storage_vlans[1].vlan_id -QoSPolicyOverrides $QoSOverride -AdapterPropertyOverrides $AdapterOverride -StorageOverrides $Storageoverride -Name mgmt_compute_storage
    }
    $gnis = Get-NetIntentStatus
    if ($gnis | Where-Object {$_.IntentName -eq "mgmt_compute_storage" -and $_.ConfigurationStatus -eq "Success" -and $_.ProvisioningStatus -eq "Completed" -and $_.IsComputeIntentSet -eq $True -and $_.IsManagementIntentSet -eq $True -and $_.IsStorageIntentset -eq $True -and $_.IsStretchIntentSet -eq $True}) {
        Write-Host " * $($env:COMPUTERNAME) Matched Network ATC mgmt_compute_storage Settings." -ForegroundColor Green
    } else {
        Write-Host " * $($env:COMPUTERNAME) Failed to match NetAdapter '$adapter' with: `ConfigurationStatus: 'Success', `ProvisioningStatus: 'Completed', `IsComputeIntentSet: 'True', `IsManagementIntentSet: 'True', `IsStorageIntentset: 'True', `IsStretchIntentSet: 'True'.  `Exiting..." -ForegroundColor Red
        Get-netIntentStatus -ComputerName $node | Format-Table Host,IntentName,ConfigurationStatus,ProvisioningStatus,IsComputeIntentSet,IsManagementIntentSet,IsStorageIntentset,IsStretchIntentSet
        Return New-Object PsObject -property @{Completed=$False}
    }
    Write-Host "$($env:COMPUTERNAME) Verifying Management vNIC in parent partition." -ForegroundColor Yellow
    $gna = Get-netadapter
    $gna_count = 0
    if ($gna | Where-Object {$_.Name -eq "vManagement(mgmt_compute_storage)" -and $_.Status -eq "Up" -and $_.LinkSpeed -eq "100 Gbps"}) {
        $gna_count++ | Out-Null
    }
    if ($gna | Where-Object {$_.Name -eq "vSMB(mgmt_compute_storage#SlotID 2 Port 1)" -and $_.Status -eq "Up" -and $_.LinkSpeed -eq "100 Gbps"}) {
        $gna_count++ | Out-Null
    }
    if ($gna | Where-Object {$_.Name -eq "vSMB(mgmt_compute_storage#SlotID 2 Port 2)" -and $_.Status -eq "Up" -and $_.LinkSpeed -eq "100 Gbps"}) {
        $gna_count++ | Out-Null
    }
    if ($gna_count -eq 3) {
        Write-Host " * $($env:COMPUTERNAME) Verified Virtual NIC Creation." -ForegroundColor Green
    } else {
        Write-Host " * $($env:COMPUTERNAME) Failed to Match Virtual NIC Creation.  Expected:" -ForegroundColor Red
        Write-Host "   Name: vManagement(mgmt_compute_storage), with Status: 'Up', LinkSpeed: '100 Gbps'" -ForegroundColor Red
        Write-Host "   Name: vSMB(mgmt_compute_storage#SlotID 2 Port 1), with Status: 'Up', LinkSpeed: '100 Gbps'" -ForegroundColor Red
        Write-Host "   Name: vSMB(mgmt_compute_storage#SlotID 2 Port 2), with Status: 'Up', LinkSpeed: '100 Gbps'`Exiting..." -ForegroundColor Red
        Get-netadapter | Format-Table Name, InterfaceDescription, Status, MacAddress, LinkSpeed
        Return New-Object PsObject -property @{Completed=$False}
    }
    Write-Host "$($env:COMPUTERNAME) Verifying Virtual Switch." -ForegroundColor Yellow
    $gvsw = Get-VMSwitch
    if ($gvsw | Where-Object {$_.Name -eq "ConvergedSwitch(mgmt_compute_storage)" -and $_.SwitchType -eq "External" -and $_.NetAdapterInterfaceDescription -eq "Teamed-Interface"}) {
        Write-Host " * $($env:COMPUTERNAME) Matched Virtual Switch Settings." -ForegroundColor Green
    } else {
        Write-Host " * $($env:COMPUTERNAME) Failed to Match Virtual Switch Settings.  Expected:" -ForegroundColor Red
        Write-Host "   Name: 'ConvergedSwitch(mgmt_compute_storage)', `SwitchType: 'External', `NetAdapterInterfaceDescription: 'Teamed-Interface'.  `Exiting..." -ForegroundColor Red
        Get-VMSwitch | Format-Table Name, SwitchType, NetAdapterInterfaceDescription, NetAdapterInterfaceDescriptions
        Return New-Object PsObject -property @{Completed=$False}
    }
    Write-Host "$($env:COMPUTERNAME) Verifying SET Switch Load Balancing Algorithm." -ForegroundColor Yellow
    $gvsw = Get-VMSwitch | Get-VMSwitchTeam
    if ($gvsw | Where-Object {$_.Name -eq "ConvergedSwitch(mgmt_compute_storage)" -and $_.LoadBalancingAlgorithm -eq "HyperVPort"}) {
        Write-Host " * $($env:COMPUTERNAME) Matched SET Switch Load Balancing Algorithm." -ForegroundColor Green
    } else {
        Write-Host " * $($env:COMPUTERNAME) Failed to Match SET Switch Load Balancing Algorithm.  Expected: `Name: 'ConvergedSwitch(mgmt_compute_storage)', `LoadBalancingAlgorithm: 'HyperVPort'.  `Exiting..." -ForegroundColor Red
        Get-VMSwitch | Get-VMSwitchTeam | Format-List
        Return New-Object PsObject -property @{Completed=$False}
    }
    Write-Host "$($env:COMPUTERNAME) Completed Network ATC Intent Status Configuration." -ForegroundColor Yellow
    # CONFIRM ITEMS
    # Variables for Storage VLANs
    # $jdata.storage_vlans[0].gateway
    # $jdata.storage_vlans[1].gateway
    # Two Default Routes or One
    Write-Host "$($env:COMPUTERNAME) Beginning Configuring default route for Management NIC " -ForegroundColor Yellow
    $mgmt_route_count = 0
    $g_mgmt_route = Get-NetRoute | Where-Object {$_.-DestinationPrefix -eq "0.0.0.0/0"}
    if ($g_mgmt_route | Where-Object {$_.-DestinationPrefix -eq "0.0.0.0/0" -and $_.Gateway -eq $jdata.storage_vlans[0].gateway -and $_.Metric -eq 10}) {
        $mgmt_route_count++ | Out-Null
    }
    if ($g_mgmt_route | Where-Object {$_.-DestinationPrefix -eq "0.0.0.0/0" -and $_.Gateway -eq $jdata.storage_vlans[1].gateway -and $_.Metric -eq 10}) {
        $mgmt_route_count++ | Out-Null
    }
    if (!($mgmt_route_count -eq 2)) {
        $null = New-NetRoute -DestinationPrefix 0.0.0.0/0 -InterfaceAlias "vManagement(mgmt_compute_storage)” -NextHop $jdata.storage_vlans[0].gateway -RouteMetric 10
        $null = New-NetRoute -DestinationPrefix 0.0.0.0/0 -InterfaceAlias "vManagement(mgmt_compute_storage)” -NextHop $jdata.storage_vlans[1].gateway -RouteMetric 10
    }
    $mgmt_route_count = 0
    $g_mgmt_route = Get-NetRoute | Where-Object {$_.-DestinationPrefix -eq "0.0.0.0/0"}
    if ($g_mgmt_route | Where-Object {$_.-DestinationPrefix -eq "0.0.0.0/0" -and $_.Gateway -eq $jdata.storage_vlans[0].gateway -and $_.Metric -eq 10}) {
        $mgmt_route_count++ | Out-Null
    }
    if ($g_mgmt_route | Where-Object {$_.-DestinationPrefix -eq "0.0.0.0/0" -and $_.Gateway -eq $jdata.storage_vlans[1].gateway -and $_.Metric -eq 10}) {
        $mgmt_route_count++ | Out-Null
    }
    if ($mgmt_route_count -eq 2) {
        Write-Host " * $($env:COMPUTERNAME) Verified Default Route for Management NIC." -ForegroundColor Green
    } else {
        Write-Host " * $($env:COMPUTERNAME) Failed to Match Default Route for Management NIC.  Expected:" -ForegroundColor Red
        Write-Host "   -DestinationPrefix: 0.0.0.0/0, with Gateway: $($jdata.storage_vlans[0].gateway), Metric: '10'" -ForegroundColor Red
        Write-Host "   -DestinationPrefix: 0.0.0.0/0, with Gateway: $($jdata.storage_vlans[1].gateway), Metric: '10'" -ForegroundColor Red
        Get-NetRoute | Where-Object {$_.-DestinationPrefix -eq "0.0.0.0/0"}
        Return New-Object PsObject -property @{Completed=$False}
    }
    Write-Host "$($env:COMPUTERNAME) Completed Configuring default route for Management NIC " -ForegroundColor Yellow
    Return New-Object PsObject -property @{Completed=$True}
}
#==============================================
# Setup Environment for Next Loop
#==============================================
#$session_results | Format-Table | Out-String|ForEach-Object {Write-Host $_}
$nodes = [System.Collections.ArrayList]@()
foreach ($result in $session_results) {
    if ($result.Completed -eq $True) { $nodes.Add($result.PSComputerName)}
}
Get-PSSession | Remove-PSSession | Out-Null
#==============================================
# Confirm All Nodes Completed
#==============================================
if (!$nodes.Length -eq $original_nodes.Length) { Exit 1 }
$x = $jdata.storage_vlans[0] -split "/"
$y = $x -split "."
$PrefixLengthA = $x[1]
$IPStorageNetA = "$($y[0]).$($y[1]).$($y[2])"
$IPHostAddrA = $y[3]
$x = $jdata.storage_vlans[1] -split "/"
$y = $x -split "."
$PrefixLengthB = $x[1]
$IPStorageNetB = "$($y[0]).$($y[1]).$($y[2])"
$IPHostAddrB = $y[3]
$sessions = Get-PSSession
$sessions | Format-Table | Out-String|ForEach-Object {Write-Host $_}
foreach ($node in $jdata.node_list) {
    $session = New-CimSession -ComputerName $node -Credential $credential
    $gnic = Get-NetIPConfiguration -CimSession $session -InterfaceAlias vSMB*
    if (!($gnic | Where-Object {$_.InterfaceAlias -eq "vSMB(mgmt_compute_storage#SlotID 2 Port 1)" -and $_.IPAddress -eq ($IPStorageNetA+$IPHostAddrA.ToString()) -and $_.PrefixLength -eq $PrefixLengthA})) {
        New-NetIPAddress -CimSession $session -InterfaceAlias "vSMB(mgmt_compute_storage#SlotID 2 Port 1)" -IPAddress ($IPStorageNetA+$IPHostAddrA.ToString()) -PrefixLength $PrefixLengthA
    }
    if (!($gnic | Where-Object {$_.InterfaceAlias -eq "vSMB(mgmt_compute_storage#SlotID 2 Port 2)" -and $_.IPAddress -eq ($IPStorageNetB+$IPHostAddrB.ToString()) -and $_.PrefixLength -eq $PrefixLengthB})) {
        New-NetIPAddress -CimSession $session -InterfaceAlias "vSMB(mgmt_compute_storage#SlotID 2 Port 2)" -IPAddress ($IPStorageNetB+$IPHostAddrB.ToString()) -PrefixLength $PrefixLengthB
    }
    $gnic = Get-NetIPConfiguration -CimSession $session -InterfaceAlias vSMB*
    if ($gnic | Where-Object {$_.InterfaceAlias -eq "vSMB(mgmt_compute_storage#SlotID 2 Port 1)" -and $_.IPAddress -eq ($IPStorageNetA+$IPHostAddrA.ToString()) -and $_.PrefixLength -eq $PrefixLengthA}) {
        Write-Host " * $($env:COMPUTERNAME) Matched vSMB(mgmt_compute_storage#SlotID 2 Port 1)." -ForegroundColor Green
    } else {
        Write-Host " * $($env:COMPUTERNAME) Failed to Match vSMB(mgmt_compute_storage#SlotID 2 Port 1).  Expected: `Name: 'ConvergedSwitch(mgmt_compute_storage)', `LoadBalancingAlgorithm: 'HyperVPort'.  `Exiting..." -ForegroundColor Red
        Get-VMSwitch | Get-VMSwitchTeam | Format-List
        Return New-Object PsObject -property @{Completed=$False}
    }
    if ($gnic | Where-Object {$_.InterfaceAlias -eq "vSMB(mgmt_compute_storage#SlotID 2 Port 2)" -and $_.IPAddress -eq ($IPStorageNetB+$IPHostAddrB.ToString()) -and $_.PrefixLength -eq $PrefixLengthB}) {
        New-NetIPAddress -CimSession $session -InterfaceAlias "vSMB(mgmt_compute_storage#SlotID 2 Port 2)" -IPAddress ($IPStorageNetB+$IPHostAddrB.ToString()) -PrefixLength $PrefixLengthB
    }
    $IPHostAddrA++
    $IPHostAddrB++
    New-NetIPAddress -CimSession $session -InterfaceAlias "vSMB(mgmt_compute_storage#SlotID 2 Port 2)" -IPAddress ($IPStorageNetB+$IPHostAddr.ToString()) -PrefixLength 24
    Return New-Object PsObject -property @{Completed=$True}
}
Get-CimSession | Remove-CimSession
Remove-Variable session
#==============================================
# Setup Environment for Next Loop
#==============================================
$nodes = [System.Collections.ArrayList]@()
foreach ($result in $session_results) {
    if ($result.Completed -eq $True) { $nodes.Add($result.PSComputerName)}
}
#==============================================
# Confirm All Nodes Completed
#==============================================
if (!$nodes.Length -eq $jdata.node_list.Length) { Exit 1 }
#==============================================
# Log Into Nodes and Run Next Section
#==============================================
foreach ($node in $jdata.node_list) {
    Write-Host "Logging into Host $($node)" -ForegroundColor Yellow
    New-PSSession -ComputerName $node -Credential $credential
}
$sessions = Get-PSSession
$sessions | Format-Table | Out-String|ForEach-Object {Write-Host $_}
$session_results = Invoke-Command $sessions -ScriptBlock {
    Write-Host "Verifying Storage NIC IP Address " -ForegroundColor Yellow
    Get-NetIPConfiguration -InterfaceAlias vSMB* | Format-List InterfaceAlias, IPv4Address, IPv4DefaultGateway
    Write-Host "Removing DNS Restistration from Storage NICs " -ForegroundColor Yellow
    Set-DnsClient -InterfaceAlias "vSMB(mgmt_compute_storage#SlotID 2 Port 1)" -RegisterThisConnectionsAddress:$False
    Set-DnsClient -InterfaceAlias "vSMB(mgmt_compute_storage#SlotID 2 Port 2)" -RegisterThisConnectionsAddress:$False
    $g_dnsclient = Get-DnsClient -InterfaceAlias vSMB*
    
    Get-DnsClient -InterfaceAlias "vSMB(mgmt_compute_storage#SlotID 2 Port 1)"| Format-Table InterfaceAlias,RegisterThisConnectionsAddress
    Get-DnsClient -InterfaceAlias "vSMB(mgmt_compute_storage#SlotID 2 Port 2)"| Format-Table InterfaceAlias,RegisterThisConnectionsAddress
    Write-Host "Configure vSwitch to pass 802.1p priority marking " -ForegroundColor Yellow
    Set-VMNetworkAdapter -Name  “vManagement(mgmt_compute_storage)" -ManagementOS -IeeePriorityTag On
    Get-VMNetworkAdapter -ManagementOS | Format-Table Name,IeeePriorityTag
    Write-Host "Verify vNIC VLANs Configuration " -ForegroundColor Yellow
    Get-VMNetworkAdapter -ManagementOS | Get-VMNetworkAdapterIsolation | Format-Table IsolationMode, DefaultIsolationID, ParentAdapter -AutoSize
    Write-Host "Verifying NIC status " -ForegroundColor Yellow
    Get-NetAdapter | Sort-Object Name | Format-Table Name,InterfaceDescription,Status,MTUSize,LinkSpeed
    Write-Host "Verifying RDMA and RoCEv2 status on physical NICS " -ForegroundColor Yellow
    Get-NetAdapterAdvancedProperty -InterfaceDescription "Mellanox ConnectX*" -DisplayName "NetworkDirect*" | Format-Table Name, InterfaceDescription,DisplayName,DisplayValue
    Write-Host "Verifying that RDMA is enabled on the Storage vNICs" -ForegroundColor Yellow
    Get-NetAdapterRdma | Format-Table
    Write-Host "Verify Mapping of each storage vNIC to the respective fabric " -ForegroundColor Yellow
    Get-VMNetworkAdapterTeamMapping -ManagementOS | Format-Table ComputerName,NetAdapterName,ParentAdapter
    Write-Host "Verify Storage vNIC RDMA operational status " -ForegroundColor Yellow
    Get-SmbClientNetworkInterface | Format-Table FriendlyName, RDMACapable
    Write-Host " Verifing Traffic Class Configuration " -ForegroundColor Yellow
    Get-NetQosTrafficClass | Format-Table -AutoSize
    Write-Host "Verifying that DCBX is set to Not Willing mode" -ForegroundColor Yellow
    Get-netadapter | Get-NetQosDcbxSetting | Format-Table InterfaceAlias, PolicySet, Willing
    ### Storage Spaces Direct
    Write-Host "Preparing disk for Storage Spaces Direct" -ForegroundColor Yellow
    Write-Host "Cleaning Storage Drives...."
    #Remove Exisiting virtual disks and storage pools
    Update-StorageProviderCache
    Get-StoragePool | Where-Object IsPrimordial -eq $False | Set-StoragePool -IsReadOnly:$False -ErrorAction SilentlyContinue
    Get-StoragePool | Where-Object IsPrimordial -eq $False | Get-VirtualDisk | Remove-VirtualDisk -Confirm:$False -ErrorAction SilentlyContinue
    Get-StoragePool | Where-Object IsPrimordial -eq $False | Remove-StoragePool -Confirm:$False -ErrorAction SilentlyContinue
    Get-PhysicalDisk | Reset-PhysicalDisk -ErrorAction SilentlyContinue
    Get-Disk | Where-Object Number -ne $null | Where-Object IsBoot -ne $True | Where-Object IsSystem -ne $True | Where-Object PartitionStyle -ne RAW | ForEach-Object {
        $_ | Set-Disk -isoffline:$False
        $_ | Set-Disk -isreadonly:$False
        $_ | Clear-Disk -RemoveData -RemoveOEM -Confirm:$False
        $_ | Set-Disk -isreadonly:$True
        $_ | Set-Disk -isoffline:$True
    }
    #Inventory Storage Disks
    Get-Disk | Where-Object {Number -Ne $Null -and IsBoot -Ne $True -and IsSystem -Ne $True -and PartitionStyle -Eq RAW} | Group-Object -NoElement -Property FriendlyName | Format-Table
    #Get-Disk | Where-Object Number -Ne $Null | Where-Object IsBoot -Ne $True | Where-Object IsSystem -Ne $True | Where-Object PartitionStyle -Eq RAW | Group-Object -NoElement -Property FriendlyName | Format-Table
}

$CandidateClusterNode = "AzS-HCI1-N1"
Invoke-Command $CandidateClusterNode -Credential $Creds -scriptblock {
    write-host "Host Name:" $env:COMPUTERNAME -ForegroundColor Green
    Write-Host " Enabling CredSSP" -ForegroundColor Yellow
    $null = Enable-WSManCredSSP -Role Server -Force
}
Invoke-Command $CandidateClusterNode -Credential $Creds -authentication Credssp -scriptblock {
    write-host "Host Name:" $env:COMPUTERNAME -ForegroundColor Green
    $nodes = ("AzS-HCI1-N1", "AzS-HCI1-N2", "AzS-HCI1-N3", "AzS-HCI1-N4")
    Write-Host " Validating Cluster Nodes..." -ForegroundColor Yellow
    Test-Cluster -Node $nodes -Include "System Configuration",Networking,Inventory, “Storage Spaces Direct”
    Write-Host " Disabling CredSSP" -ForegroundColor Yellow
    Disable-WSManCredSSP -Role Server
    Write-Host " Verifying that CredSSP are disabled on target server..." -ForegroundColor Yellow
    Get-WSManCredSSP
}
$CandidateClusterNode = "AzS-HCI1-N1"
Invoke-Command $CandidateClusterNode -Credential $Creds -scriptblock {
    write-host "Host Name:" $env:COMPUTERNAME -ForegroundColor Green
    Write-Host " Enabling CredSSP" -ForegroundColor Yellow
    Enable-WSManCredSSP -Role Server -Force | Out-Null
}

Invoke-Command $CandidateClusterNode -Credential $Creds -authentication Credssp -scriptblock {
    write-host "Host Name:" $env:COMPUTERNAME -ForegroundColor Green
    $nodes = ("AzS-HCI1-N1", "AzS-HCI1-N2", "AzS-HCI1-N3", "AzS-HCI1-N4")
    Write-Host " Creating the cluster..." -ForegroundColor Yellow
    $Cluster = “AzS-HCI-M6-C1”
    New-Cluster -Name $Cluster -Node $nodes -StaticAddress 192.168.126.25 -NoStorage
    Get-Cluster | Format-Table Name, SharedVolumesRoot
    Write-Host " Disabling CredSSP" -ForegroundColor Yellow
    Disable-WSManCredSSP -Role Server
    Write-Host " Verifying that CredSSP are disabled on target server..." -ForegroundColor Yellow
    Get-WSManCredSSP
}
$Cluster = “AzS-HCI-M6-C1”
Invoke-Command  $Cluster -Credential $Creds -scriptblock {
    write-host "Host Name:" $env:COMPUTERNAME -ForegroundColor Green
    Write-Host " Enabling CredSSP" -ForegroundColor Yellow
    Enable-WSManCredSSP -Role Server -Force | Out-Null
}
Invoke-Command  $Cluster -Credential $Creds -authentication Credssp -scriptblock {
    $Cluster = “AzS-HCI-M6-C1”
    write-host "Host Name:" $env:COMPUTERNAME -ForegroundColor Green
    Write-Host " Checking cluster nodes..." -ForegroundColor Yellow
    Get-ClusterNode -Cluster $Cluster | Format-Table Name, State, Type
    Write-Host " Disabling CredSSP" -ForegroundColor Yellow
    Disable-WSManCredSSP -Role Server
    Write-Host " Verifying that CredSSP are disabled on target server..." -ForegroundColor Yellow
    Get-WSManCredSSP
}
$Cluster = “AzS-HCI-M6-C1”
$nodes = (Get-ClusterNode -Cluster $Cluster).Name
foreach ($node in $nodes) {
    Invoke-Command $node -scriptblock {
        write-host "Host Name:" $env:COMPUTERNAME -ForegroundColor Green
        Write-Host " Identifying and Removing Standalone Network ATC Intent." -ForegroundColor Yellow
        $intent = Get-NetIntent | Where-Object {$_.Scope -Like 'Host' -and $_.IntentName -EQ 'mgmt_compute_storage'}
        Write-Host "Removing Standalone Network ATC Intent $intent" -ForegroundColor Yellow
        Remove-NetIntent -Name $intent.IntentName
    }
}
$Cluster = “AzS-HCI-M6-C1”
Invoke-Command  $Cluster -Credential $Creds -scriptblock {
    write-host "Host Name:" $env:COMPUTERNAME -ForegroundColor Green
    Write-Host " Enabling CredSSP" -ForegroundColor Yellow
    Enable-WSManCredSSP -Role Server -Force | Out-Null
}
Invoke-Command $Cluster -Credential $Creds -authentication Credssp -scriptblock {
    write-host "Host Name:" $env:COMPUTERNAME -ForegroundColor Green
    Write-Host " Create and Deploy Clustered Network ATC Intent " -ForegroundColor Yellow
    #$ClusterName = Get-cluster
    $QoSOverride = New-NetIntentQoSPolicyOverRides
    $AdapterOverride = New-NetIntentAdapterPropertyOverrides
    $storageOverride = new-NetIntentStorageOverrides
    $QoSOverride.PriorityValue8021Action_SMB = 4
    $QoSOverride.PriorityValue8021Action_Cluster = 5
    $AdapterOverride.NetworkDirectTechnology = 4
    $storageOverride.EnableAutomaticIPGeneration = $false
    $QoSOverride
    $AdapterOverride
    $storageOverride
    Add-NetIntent -AdapterName "SlotID 2 Port 1", "SlotID 2 Port 2" -Management -Compute -Storage -StorageVlans 107, 207 -QoSPolicyOverrides $QoSOverride -AdapterPropertyOverrides $AdapterOverride -StorageOverrides $storageoverride -Name mgmt_compute_storage
    Write-Host " Disabling CredSSP" -ForegroundColor Yellow
    Disable-WSManCredSSP -Role Server
    Write-Host " Verifying that CredSSP are disabled on target server..." -ForegroundColor Yellow
    Get-WSManCredSSP
}
$Cluster = “AzS-HCI-M6-C1”
Invoke-Command  $Cluster -Credential $Creds -scriptblock {
    write-host "Host Name:" $env:COMPUTERNAME -ForegroundColor Green
    Write-Host " Enabling CredSSP" -ForegroundColor Yellow
    Enable-WSManCredSSP -Role Server -Force | Out-Null
}
Invoke-Command $Cluster -Credential $Creds -authentication Credssp -scriptblock {
    write-host "Host Name:" $env:COMPUTERNAME -ForegroundColor Green
    Write-Host "Verify Clustered Network ATC Intent Status" -ForegroundColor Yellow
    $ClusterName = (Get-cluster).Name
    Get-NetIntent -ClusterName $ClusterName| Select-Object IntentName,scope
    Get-NetIntentStatus -ClusterName $ClusterName | Select-Object Host, IntentName, ConfigurationStatus, ProvisioningStatus
    Write-Host " Disabling CredSSP" -ForegroundColor Yellow
    Disable-WSManCredSSP -Role Server
    Write-Host " Verifying that CredSSP are disabled on target server..." -ForegroundColor Yellow
    Get-WSManCredSSP
}
$nodes = (Get-ClusterNode -Cluster $Cluster).Name
foreach ($node in $nodes) {
    Invoke-Command $node -Credential $Creds -scriptblock {
        write-host "Host Name:" $env:COMPUTERNAME -ForegroundColor Green
        Write-Host " Enabling CredSSP" -ForegroundColor Yellow
        Enable-WSManCredSSP -Role Server -Force | Out-Null
        Write-Host "Verifying NIC Port Status " -ForegroundColor Yellow
        Get-netadapter | Format-Table Name, InterfaceDescription, Status, MTUSize, MacAddress, LinkSpeed
        Write-Host " Disabling CredSSP" -ForegroundColor Yellow
        Disable-WSManCredSSP -Role Server
        Write-Host " Verifying that CredSSP are disabled on target server..." -ForegroundColor Yellow
        Get-WSManCredSSP
    }
}
$Cluster = “AzS-HCI-M6-C1"
Invoke-Command $Cluster -Credential $Creds -scriptblock {
    write-host "Host Name:" $env:COMPUTERNAME -ForegroundColor Green
    Write-Host " Enabling CredSSP" -ForegroundColor Yellow
    Enable-WSManCredSSP -Role Server -Force | Out-Null
}
Invoke-Command $Cluster -Credential $Creds -authentication Credssp -scriptblock {
    write-host "Host Name:" $env:COMPUTERNAME -ForegroundColor Green
    Write-Host " Checking cluster networks " -ForegroundColor Yellow
    $ClusterName = (Get-cluster).Name
    Get-ClusterNetwork -Cluster $ClusterName | Format-Table name,address,state,role -autosize
    Write-Host " Disabling CredSSP" -ForegroundColor Yellow
    Disable-WSManCredSSP -Role Server
    Write-Host " Verifying that CredSSP are disabled on target server..." -ForegroundColor Yellow
    Get-WSManCredSSP
}
$Cluster = “AzS-HCI-M6-C1"
Invoke-Command $Cluster -Credential $Creds -scriptblock {
    write-host "Host Name:" $env:COMPUTERNAME -ForegroundColor Green
    Write-Host " Enabling CredSSP" -ForegroundColor Yellow
    Enable-WSManCredSSP -Role Server -Force | Out-Null
}
Invoke-Command $Cluster -Credential $Creds -authentication Credssp -scriptblock {
    write-host "Host Name:" $env:COMPUTERNAME -ForegroundColor Green
    Write-Host " Verifying cluster network interfaces " -ForegroundColor Yellow
    $ClusterName = (Get-cluster).Name
    Get-ClusterNetworkInterface -Cluster $ClusterName | Sort-Object Name | Format-Table Network, Name
    Write-Host " Disabling CredSSP" -ForegroundColor Yellow
    Disable-WSManCredSSP -Role Server
    Write-Host " Verifying that CredSSP are disabled on target server..." -ForegroundColor Yellow
    Get-WSManCredSSP
}
$Cluster = “AzS-HCI-M6-C1”
Invoke-Command  $Cluster -Credential $Creds -scriptblock {
    write-host "Host Name:" $env:COMPUTERNAME -ForegroundColor Green
    Write-Host " Enabling CredSSP" -ForegroundColor Yellow
    Enable-WSManCredSSP -Role Server -Force | Out-Null
}
Invoke-Command $Cluster -Credential $Creds -authentication Credssp -scriptblock {
    write-host "Host Name:" $env:COMPUTERNAME -ForegroundColor Green
    Write-Host " Checking Management cluster network settings " -ForegroundColor Yellow
    $ClusterName = (Get-cluster).Name
    Get-ClusterNetwork -Cluster $ClusterName -Name “mgmt_compute_storage(Management)” | Format-Table *
    Write-Host " Disabling CredSSP" -ForegroundColor Yellow
    Disable-WSManCredSSP -Role Server
    Write-Host " Verifying that CredSSP are disabled on target server..." -ForegroundColor Yellow
    Get-WSManCredSSP
}
$Cluster = “AzS-HCI-M6-C1"
Invoke-Command $Cluster -Credential $Creds -scriptblock {
    write-host "Host Name:" $env:COMPUTERNAME -ForegroundColor Green
    Write-Host " Enabling CredSSP" -ForegroundColor Yellow
    Enable-WSManCredSSP -Role Server -Force | Out-Null
}

Invoke-Command $Cluster -Credential $Creds -authentication Credssp -scriptblock {
    write-host "Host Name:" $env:COMPUTERNAME -ForegroundColor Green
    Write-Host " Verifying Management network exclusion from Live Migration Network list " -ForegroundColor Yellow
    $ClusterName = (Get-cluster).Name
    Get-ClusterResourceType -Cluster $ClusterName -Name "Virtual Machine" | Get-ClusterParameter -Name MigrationExcludeNetworks | Format-Table *
    Write-Host " Disabling CredSSP" -ForegroundColor Yellow
    Disable-WSManCredSSP -Role Server
    Write-Host " Verifying that CredSSP are disabled on target server..." -ForegroundColor Yellow
    Get-WSManCredSSP
}
$Cluster = “AzS-HCI-M6-C1"
$nodes = (Get-ClusterNode -Cluster $Cluster).Name
foreach ($node in $nodes) {
    Invoke-Command $node -scriptblock {
        write-host "Host Name:" $env:COMPUTERNAME -ForegroundColor Green
        Write-Host "Configuring Live Migration to use SMB protocol" -ForegroundColor Yellow
        Set-VMHost -VirtualMachineMigrationPerformanceOption SMB
        Get-VMHost | Format-Table VirtualMachineMigrationPerformanceOption
    }
}
$nodes = (Get-ClusterNode -Cluster $Cluster).Name
foreach ($node in $nodes) {
    Invoke-Command $node -scriptblock {
        write-host "Host Name:" $env:COMPUTERNAME -ForegroundColor Green
        Write-Host "Configuring Live Migration Bandwidth Limit: 3625MB" -ForegroundColor Yellow
        Set-SMBBandwidthLimit -Category LiveMigration -BytesPerSecond 3625MB
        Get-SMBBandwidthLimit -Category LiveMigration
    }
}
$nodes = (Get-ClusterNode -Cluster $Cluster).Name
foreach ($node in $nodes) {
    Invoke-Command $node -scriptblock {
        $MgmtBandwidthLimit = "10000000"
        write-host "Host Name:" $env:COMPUTERNAME -ForegroundColor Green
        Write-Host "Configuring management vNIC maximum bandwidth Limit: $MgmtBandwidthLimit" -ForegroundColor Yellow
        Set-VMNetworkAdapter -ManagementOS -Name "vManagement(mgmt_compute_storage)" -MaximumBandwidth $MgmtBandwidthLimit
        Write-Host "Verifying management vNIC maximum bandwidth Limit" -ForegroundColor Yellow
        (Get-VMNetworkAdapter -ManagementOS -Name "vManagement(mgmt_compute_storage)").BandwidthSetting | Format-Table ParentAdapter, MaximumBandwidth
    }
}
$FSW = “fsw01.ucs-spaces.lab”
#$FSWDomain = “ucs-spaces.lab”
$ShareName = "FSW-AzS-HCI-M6-C1"
$SharePath = "C:\FileShareWitness\FSW-AzS-HCI-M6-C1"
Invoke-Command -ComputerName $FSW -ScriptBlock {
    #Create Directory on File Share Witness
    Write-Host "Creating directory on files share witness"
    mkdir $Using:SharePath
    #Create file share on the file share witness
    Write-Host "Creating file share on file share witness"
    new-smbshare -Name $Using:ShareName -Path $Using:SharePath -FullAccess “ucs-spaces.lab\Domain Admins", "ucs-spaces.lab\AzS-HCI-M6-C1$", "ucs-spaces.lab\AzS-HCI1-N1$”, "ucs-spaces.lab\AzS-HCI1-N2$”, "ucs-spaces.lab\AzS-HCI1-N3$”, "ucs-spaces.lab\AzS-HCI1-N4$”
    #Verify file share on file share witness
    Write-Host "Verifying file share on file share witness"
    Get-SmbShare -Name $Using:ShareName | Format-Table name,path -AutoSize
    #Verify file share permissions on the file share witness
    Write-Host "Verifing file share permissions on the file share witness"
    Get-SmbShareAccess -Name $Using:ShareName | Format-Table -AutoSize
    #Set file level permissions on the file share directory that match the file share permissions
    Write-Host "Setting file level permissions on the file share directory that match the file share permissions"
    Set-SmbPathAcl -ShareName $Using:ShareName
    #Verify file level permissions on the file share
    Write-Host "Verifying file level permissions on the file share"
    Get-Acl -Path $Using:SharePath | Format-List
}
$Cluster = “AzS-HCI-M6-C1”
Get-ClusterResource -Cluster $Cluster -Name "File Share Witness" | Get-ClusterParameter -Name SharePath
$Cluster = “AzS-HCI-M6-C1"
Invoke-Command $Cluster -Credential $Creds -scriptblock {
    write-host "Host Name:" $env:COMPUTERNAME -ForegroundColor Green
    Write-Host " Enabling CredSSP" -ForegroundColor Yellow
    Enable-WSManCredSSP -Role Server -Force | Out-Null
}
Invoke-Command $Cluster -Credential $Creds -authentication Credssp -scriptblock {
    write-host "Host Name:" $env:COMPUTERNAME -ForegroundColor Green
    Write-Host " Configuring Cluster-Aware Updating ... " -ForegroundColor Yellow
    $ClusterName = (Get-cluster).Name
    Add-CauClusterRole -ClusterName $ClusterName -DaysOfWeek Tuesday,Saturday -IntervalWeeks 3 -MaxFailedNodes 1 -MaxRetriesPerNode 2 -EnableFirewallRules -Force
    Write-Host " Verifying Cluster-Aware Updating configuraiton " -ForegroundColor Yellow
    Get-CauClusterRole -ClusterName $ClusterName | Format-Table
    Write-Host " Disabling CredSSP" -ForegroundColor Yellow
    Disable-WSManCredSSP -Role Server
    Write-Host " Verifying that CredSSP are disabled on target server..." -ForegroundColor Yellow
    Get-WSManCredSSP
}
$Cluster = “AzS-HCI-M6-C1”
Invoke-Command $Cluster -Credential $Creds -scriptblock {
    write-host "Host Name:" $env:COMPUTERNAME -ForegroundColor Green
    Write-Host " Enabling CredSSP" -ForegroundColor Yellow
    Enable-WSManCredSSP -Role Server -Force | Out-Null
}

Invoke-Command $Cluster -Credential $Creds -authentication Credssp -scriptblock {
    write-host "Host Name:" $env:COMPUTERNAME -ForegroundColor Green
    $ClusterName = (Get-cluster).Name
    Write-Host " Configuring Kernel Soft Reboot  for Cluster Aware Updating ... " -ForegroundColor Yellow
    Get-Cluster -Name $ClusterName | Set-ClusterParameter -Name CauEnableSoftReboot -Value 1 -Create
    Write-Host " Verifying Kernel Soft Reboot configuraiton " -ForegroundColor Yellow
    Get-Cluster -Name $ClusterName | Get-ClusterParameter -Name CauEnableSoftReboot | Format-Table Name, Value
    Write-Host " Disabling CredSSP" -ForegroundColor Yellow
    Disable-WSManCredSSP -Role Server
    Write-Host " Verifying that CredSSP are disabled on target server..." -ForegroundColor Yellow
    Get-WSManCredSSP
}
$Cluster = “AzS-HCI-M6-C1"
Invoke-Command $Cluster -Credential $Creds -scriptblock {
    write-host "Host Name:" $env:COMPUTERNAME -ForegroundColor Green
    Write-Host " Enabling CredSSP" -ForegroundColor Yellow
    Enable-WSManCredSSP -Role Server -Force | Out-Null
}
Invoke-Command $Cluster -Credential $Creds -authentication Credssp -scriptblock {
    write-host "Host Name:" $env:COMPUTERNAME -ForegroundColor Green
    #$ClusterName = (Get-cluster).Name
    Write-Host " Enabling Storage Spaces Direct " -ForegroundColor Yellow
    Enable-ClusterStorageSpacesDirect -Confirm:$false
    Write-Host " Disabling CredSSP" -ForegroundColor Yellow
    Disable-WSManCredSSP -Role Server
    Write-Host " Verifying that CredSSP are disabled on target server..." -ForegroundColor Yellow
    Get-WSManCredSSP
}
$Cluster = “AzS-HCI-M6-C1"
Invoke-Command $Cluster -Credential $Creds -scriptblock {
    write-host "Host Name:" $env:COMPUTERNAME -ForegroundColor Green
    Write-Host " Enabling CredSSP" -ForegroundColor Yellow
    Enable-WSManCredSSP -Role Server -Force | Out-Null
}

Invoke-Command $Cluster -Credential $Creds -authentication Credssp -scriptblock {
    write-host "Host Name:" $env:COMPUTERNAME -ForegroundColor Green
    #$ClusterName = (Get-cluster).Name
    Write-Host " Verifying Storage Pools " -ForegroundColor Yellow
    Get-StoragePool | Format-Table friendlyname, OperationalStatus, HealthStatus, IsPrimordial, IsReadonly
    Write-Host " Verifying NVMe SSD Cache Tier " -ForegroundColor Yellow
    Get-PhysicalDisk | Where-Object Usage -eq "Journal" | Format-Table FriendlyName, CanPool, HealthStatus, Usage, Size
    Write-Host " Verifying Storage Tier configuration " -ForegroundColor Yellow
    Get-storagetier | Format-Table FriendlyName, ResiliencySettingName, MediaType, NumberOfDataCopies, PhysicalDiskRedundancy
    Write-Host " Disabling CredSSP" -ForegroundColor Yellow
    Disable-WSManCredSSP -Role Server
    Write-Host " Verifying that CredSSP are disabled on target server..." -ForegroundColor Yellow
    Get-WSManCredSSP
}
$Cluster = “AzS-HCI-M6-C1”
Invoke-Command $Cluster -Credential $Creds -scriptblock {
    write-host "Host Name:" $env:COMPUTERNAME -ForegroundColor Green
    Write-Host " Enabling CredSSP" -ForegroundColor Yellow
    Enable-WSManCredSSP -Role Server -Force | Out-Null
}
Invoke-Command $Cluster -Credential $Creds -authentication Credssp -scriptblock {
    write-host "Host Name:" $env:COMPUTERNAME -ForegroundColor Green
    #$ClusterName = (Get-cluster).Name
    Write-Host " Creating Virtual Disk " -ForegroundColor Yellow
    New-Volume -StoragePoolFriendlyName “S2D*” -FriendlyName VDisk01 -FileSystem CSVFS_ReFS -ResiliencySettingName Mirror -Size 4TB
    Write-Host " Disabling CredSSP" -ForegroundColor Yellow
    Disable-WSManCredSSP -Role Server
    Write-Host " Verifying that CredSSP are disabled on target server..." -ForegroundColor Yellow
    Get-WSManCredSSP
}
$cluster = "AzS-HCI-M6-C1"
Invoke-Command $cluster -scriptblock {Get-VirtualDisk}
Invoke-Command $cluster -scriptblock {Get-ClusterSharedVolume | Format-Table Name,SharedVolumeInfo,OwnerNode}
$Cluster = “AzS-HCI-M6-C1”
Invoke-Command $Cluster -Credential $Creds -scriptblock {
    write-host "Host Name:" $env:COMPUTERNAME -ForegroundColor Green
    Write-Host " Creating and verifying Storage Polices" -ForegroundColor Yellow
    New-StorageQoSPolicy -Name Copper -MinimumIops 50 -MaximumIops 100 -PolicyType Dedicated
    New-StorageQoSPolicy -Name Bronze -MinimumIops 100 -MaximumIops 250 -PolicyType Dedicated
    New-StorageQoSPolicy -Name Silver -MinimumIops 200 -MaximumIops 500 -PolicyType Dedicated
    New-StorageQoSPolicy -Name Gold -MinimumIops 500 -MaximumIops 5000 -PolicyType Dedicated
    New-StorageQoSPolicy -Name Platinum -MinimumIops 1000 -MaximumIops 10000 -PolicyType Dedicated
    Get-StorageQoSPolicy | Format-Table Name,Status, MinimumIops,MaximumIops,MaximumIOBandwidth,PolicyID
}
$Cluster = “AzS-HCI-M6-C1”
Invoke-Command $Cluster -Credential $Creds -scriptblock {
    write-host "Host Name:" $env:COMPUTERNAME -ForegroundColor Green
    Write-Host " Enabling CredSSP" -ForegroundColor Yellow
    Enable-WSManCredSSP -Role Server -Force | Out-Null
}
Invoke-Command $Cluster -Credential $Creds -authentication Credssp -scriptblock {
    write-host "Host Name:" $env:COMPUTERNAME -ForegroundColor Green
    $CSVPath = ((Get-ClusterSharedVolume).SharedVolumeInfo).FriendlyVolumeName
    $VHDPath = "$CSVPath\VM01-Disk01.vhdx"
    $VMSwitch = (Get-VMSwitch).Name
    $VMName = "VM01"
    $VMPath = "$CSVPath\VirtualMachines"
    $VMMemoryCapacity = 8GB
    Write-Host "Creating VHDX $VHDPath ..." -ForegroundColor Yellow
    New-VHD -Path $CSVPath\VM01-Disk01.vhdx -Fixed -SizeBytes 100GB
    Write-Host "Creating virtual machine $VMName with memory capacity $VMMemoryCapacity ... " -ForegroundColor Yellow
    New-VM -Name $VMName -Path $VMPath -MemoryStartupBytes $VMMemoryCapacity -VHDPath $VHDPath -Generation 2 -SwitchName $VMSwitch
    $BronzeStorageQoSPolicyID = (Get-StorageQosPolicy -Name Silver).PolicyId
    Write-Host "Setting QoS Plicy for virtual machine $VMName ..." -ForegroundColor Yellow
    Get-VM -VMName $VMName | Get-VMHardDiskDrive | Set-VMHardDiskDrive -QoSPolicyID $BronzeStorageQoSPolicyID
    Write-Host "Clustering the virtual machine $VMName ..." -ForegroundColor Yellow
    Get-VM -Name $VMName | Add-ClusterVirtualMachineRole -Name $VMName
    Write-Host " Disabling CredSSP" -ForegroundColor Yellow
    Disable-WSManCredSSP -Role Server
    Write-Host " Verifying that CredSSP are disabled on target server..." -ForegroundColor Yellow
    Get-WSManCredSSP
}
Exit 0