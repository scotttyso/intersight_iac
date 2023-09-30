# sudo apt-get -y install gss-ntlmssp
# pwsh -Command 'Install-Module -Name PSWSMan'
param (
    [string]$username=$(throw "-username is required."),
    [switch]$force
)
#=====================================================
# Setup Credentials
#=====================================================
#$password = ConvertTo-SecureString $env:windows_administrator_password -AsPlainText -Force;
#$credential = New-Object System.Management.Automation.PSCredential ($username,$password);

$nodes = ("tyscott-win22.rich.ciscolabs.com", "64.100.14.28")
Get-PSSession | Remove-PSSession | Out-Null
foreach ($node in $nodes) {
    Write-Host "Logging into Host $($node)" -ForegroundColor Yellow
    New-PSSession -HostName $node -UserName $username -KeyFilePath $env:HOME/.ssh/id_ed25519
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
    $feature_list = ("Hyper-V", "Failover-Clustering", "Data-Center-Bridging", "Bitlocker" , "FS-FileServer",
    "FS-SMBBW", "Hyper-V-PowerShell", "RSAT-AD-Powershell", "RSAT-Clustering-PowerShell", "NetworkATC", "NetworkHUD",
    "FS-DATA-Deduplication")
    $timezone = "Eastern Standard Time"
    ##########
    Write-Host "$($env:COMPUTERNAME) Beginning time zone '$timezone' Configuration." -ForegroundColor Yellow
    $tz = Get-TimeZone
    if (!($tz.Id -eq $timezone)) {Set-Timezone $timezone}
    $tz = Get-TimeZone
    if ($tz.Id -eq $timezone) {
        Write-Host " * $($env:COMPUTERNAME) Successfully Set Timezone to '$timezone'." -ForegroundColor Green
    } else {
        Write-Host " * $($env:COMPUTERNAME) Failed to Set Timezone to '$timezone'.  Exiting..." -ForegroundColor Red
        Return New-Object PsObject -property @{Completed=$False}
    }
    Write-Host "$($env:COMPUTERNAME) Compeleted time zone '$timezone' Configuration." -ForegroundColor Yellow
    ##########
    Write-Host "$($env:COMPUTERNAME) Beginning Remote Desktop Access Configuration." -ForegroundColor Yellow
    $registry_path = "HKLM:\System\CurrentControlSet\Control\Terminal Server"
    $key = New-Object PsObject -property @{name="fDenyTSConnections"; value=0; type="Dword" }
    RegistryKey $registry_path $key
    Write-Host "$($env:COMPUTERNAME) Completed Remote Desktop Access Configuration." -ForegroundColor Yellow
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
    Write-Host "$($env:COMPUTERNAME) Beginning Memory Crashdump Registry settings Configuring." -ForegroundColor Yellow
    $keys = ("CrashDumpEnabled", "FilterPages")
    $registry_path = "HKLM:\System\CurrentControlSet\Control\CrashControl"
    foreach ($item in $keys) {
        $key = New-Object PsObject -property @{name=$item; value=1; type="Dword" }
        RegistryKey $registry_path $key
    }
    Write-Host "$($env:COMPUTERNAME) Completed Memory Crashdump Registry settings Configuring." -ForegroundColor Yellow
    ##########
    Write-Host "$($env:COMPUTERNAME) Beginning Check for Required Windows Features and Restarting Host." -ForegroundColor Yellow
    $new_list = [System.Collections.ArrayList]@()
    $reboot = $False
    $wf = Get-WindowsFeature | Select-Object *
    foreach ($item in $feature_list) {
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
if ($nodes.Length -eq 0) { Exit 1 }
if ($reboot_count -gt 0) {
    Write-Host "Sleeping for 10 Minutes to Wait for Server Reboots." -ForegroundColor Yellow
    Start-Sleep -Seconds 600
}
foreach ($node in $nodes) {
    Write-Host "Logging into Host $($node)" -ForegroundColor Yellow
    New-PSSession -HostName $node -UserName RICH\tyscott -KeyFilePath $env:HOME/.ssh/id_ed25519
}
$sessions = Get-PSSession
$sessions | Format-Table | Out-String|ForEach-Object {Write-Host $_}
$session_results = Invoke-Command $session -ScriptBlock {
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
    $feature_list = ("Hyper-V", "Failover-Clustering", "Data-Center-Bridging", "Bitlocker" , "FS-FileServer",
    "FS-SMBBW", "Hyper-V-PowerShell", "RSAT-AD-Powershell", "RSAT-Clustering-PowerShell", "NetworkATC", "NetworkHUD",
    "FS-DATA-Deduplication")
    ##########
    Write-Host "$($env:COMPUTERNAME) Beginning Check for Windows Features..." -ForegroundColor Yellow
    $wf = Get-WindowsFeature | Select-Object *
    foreach ($item in $feature_list) {
        if (!(($wf | Where-Object {$_.Name -eq $item}).Installed -eq $true)) {
            Write-Host "Failed on Enabling Windows Feature $item.  Exiting..." -ForegroundColor Red
            $exit_count++
            Return New-Object PsObject -property @{Completed=$False}
        }
    }
    Write-Host "$($env:COMPUTERNAME) Completed Check for Windows Features..." -ForegroundColor Yellow
    ##########
    Write-Host "$($env:COMPUTERNAME) Beginning Secure Boot State Check." -ForegroundColor Yellow
    $sb = Confirm-SecureBootUEFI
    if (!($sb -eq $true)) {
        Write-Host "$($env:COMPUTERNAME) Secure Boot State is not Enabled.  Exiting..." -ForegroundColor Red
        $exit_count++
        Return New-Object PsObject -property @{Completed=$False}
    }
    Write-Host "$($env:COMPUTERNAME) Completed Secure Boot State Check." -ForegroundColor Yellow
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
}
Exit 0