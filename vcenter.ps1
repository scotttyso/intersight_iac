#"""
#Script will complete host configuration after OS Installation.
#Includes, Managment vswitch conifg, vmotion, data switching and vnics plus esxi customizations.
#  * Jamy Smith 5/7/2018
#  * Tyson Scott 1/23/2022 - tyscott@cisco.com
#  * Tyson Scott 4/14/2023 - tyscott@cisco.com
#"""


#=============================================================================
# JSON File is a Required Parameter
# Pull in JSON Content
#=============================================================================
param (
    [string]$j,
    [switch]$force
    # $(throw "-j is required. It is the Source of Data for the Script.")
)
$jsonData = Get-Content -Path $j | ConvertFrom-Json

#=====================================================
# Start Log and Configure PowerCLI
#=====================================================
Start-Transcript -Path ".\Logs\$(get-date -f "yyyy-MM-dd_HH-mm-ss")_$($env:USER).log" -Append -Confirm:$false

#=====================================================
# Adds VMware PowerCLI snapin, sets global error
# action preference, sets PowerCLI Config to 
# ignore cert errors
#=====================================================
#Add-PsSnapin VMware.VimAutomation.Core -ErrorAction SilentlyContinue
$ErrorActionPreference = "SilentlyContinue"
Set-PowerCLIConfiguration -InvalidCertificateAction Ignore -Confirm:$false


#=====================================================
# Obtain Username and Password
#=====================================================
if (Test-Path -Path ${env:HOME}\powercli.Cred) {
    $credential = Import-CliXml -Path "${env:HOME}\powercli.Cred"
}
else {
    $credential = Get-Credential
    $credential | Export-CliXml -Path "${env:HOME}\powercli.Cred"
}

#=====================================================
# Build Hash Table for Identity Output
#=====================================================
$storageOutput = @{iscsi = @(); nvme = @()}

#=============================================================================
# Loop Through vCenters from JSON File
#=============================================================================
foreach($vcenter in $jsonData.vcenters) {
    Write-Host "Connect to vcenter $($vcenter.name)" -ForegroundColor Yellow
    # Login to vCenter
    if ($vcenter)  {
        try {
            if (Test-Path -Path ${env:HOME}\powercli.Cred) {
                $credential = Import-CliXml -Path "${env:HOME}\powercli.Cred"
                $null = Connect-VIServer $vcenter.name -Credential $credential
            } else {
                $null = Connect-VIServer $vcenter.name -User $vcenter.username -Password $env:vcenter_password
            }
        }
        catch {
            Write-Host "There was an issue with connecting to $($vcenter.name)"
            exit
        }
    } else {
        Write-Host "The vcenter switch is required to define target vcenter"
        exit
    }
    #=====================================================
    # Add Custom Attributes to vCenter - If Necessary
    #=====================================================
    #$customAttributes = New-Object System.Collections.ArrayList
    $cAttributes = Get-CustomAttribute
    Write-Host "Custom Attributes are $($customAttributes)"
    foreach ($attr in $customAttributes) {
        if (!($cAttributes | Where-Object { $attr -match $_ })) {
            Write-Host "Adding Custom Attribute $attr" -ForegroundColor Green
            New-CustomAttribute -Name $attr -TargetType VMHost
        }
    }

    #=====================================================
    # Create/Update Clusters
    #=====================================================
    $DataCenter = Get-Datacenter -Name $vcenter.datacenter
    Write-Host "Data Center is $($DataCenter)" -ForegroundColor Yellow
    $dcClusters = Get-Cluster -Location $DataCenter
    foreach ($cluster in $vcenter.clusters.PSObject.Properties) {
        Write-Host "Beginning Cluster '$($cluster.value.name)' in DataCenter '$($DataCenter)'" -ForegroundColor Blue
        if (!($dcClusters | Where-Object { $cluster.value.name -match $_})) {
            $dcCluster = New-Cluster -Name $cluster.value.name -Location $DataCenter -DRSEnabled -DRSAutomationLevel 'PartiallyAutomated' -HAEnabled -VMSwapfilePolicy InHostDatastore
            Write-Host "  * Added Cluster $($dcCluster) to DataCenter $($DataCenter)" -ForegroundColor Green
        } else {
            $dcCluster = Get-Cluster -Location $DataCenter -Name $cluster.value.name
            $dcCluster | Set-Cluster -DRSEnabled -DRSAutomationLevel 'PartiallyAutomated' -HAEnabled -VMSwapfilePolicy InHostDatastore -VC
            Write-Host "  * Found Existing Cluster $($dcCluster) in DataCenter $($DataCenter)" -ForegroundColor Magenta
        }
        Write-Host "Completed Cluster '$($cluster.value.name)' in DataCenter '$($DataCenter)'" -ForegroundColor Blue
        Write-Host ""
    }

    #=====================================================
    # Create/update Virtual Distributed Switches
    #=====================================================
    foreach ($sw in $vcenter.vswitches.PSObject.Properties) {
        if ($sw.value.type -eq "dvs") {
            Write-Host "Beginning DVSwitch '$($sw.value.name)' in DataCenter '$($DataCenter)'" -ForegroundColor Blue
            $checkDVS = Get-VDSwitch -Location $DataCenter
            if (-Not($checkDVS | Where-Object { $sw.value.name -match $_ })) {
                $newDVS = New-VDSwitch -Name $sw.value.name -Location $DataCenter -NumUplinkPorts 2 -Mtu $sw.value.mtu -LinkDiscoveryProtocol LLDP -LinkDiscoveryProtocolOperation Both
                Write-Host "  * Added DVSwitch $($newDVS) to DataCenter $($DataCenter)" -ForegroundColor Green
            } elseif ($checkDVS | Where-Object { $sw.value.name -match $_}) {
                $newDVS = Get-VDSwitch -Location $DataCenter -Name $sw.value.name
                Write-Host "  * Found Existing DVSwitch $($newDVS) in DataCenter $($DataCenter)" -ForegroundColor Magenta
            }
            #=====================================================
            # Configure Port Groups
            #=====================================================
            foreach ($pg in $sw.value.port_groups) {
                Write-Host "    Beginning Port-Group '$($pg.name)' on DVSwitch '$($newDVS)'" -ForegroundColor Blue
                $checkPG = Get-VDPortgroup -VDSwitch $newDVS
                if (-Not($checkPG | Where-Object { $pg.name -match $_})) {
                    if ($pg.vlan -is [int]) {
                        $newPG = New-VDPortgroup -Name $pg.name -VDSwitch $newDVS -VlanId $pg.vlan -NumPorts 8
                    } else { $newPg = New-VDPortgroup -Name $pg.name -VDSwitch $newDVS }
                    Write-Host "      * Created Port-Group '$($newPg)' on DVSwitch' $($newDVS)'" -ForegroundColor Green
                } else {
                    $newPG = Get-VDPortgroup -Name $pg.name -VDSwitch $newDVS
                    Write-Host "      * Found Existing Port-Group '$($newPg)' on DVSwitch '$($newDVS)'" -ForegroundColor Magenta
                }
                if ($pg.primary -eq $true -or $pg.secondary -eq $true) {
                    if ($pg.primary -eq $true) {
                        $activePorts = "dvUplink1"
                        $unusedPorts = "dvUplink2", "dvUplink3", "dvUplink4"
                    } elseif ($pg.secondary -eq $true) {
                        $activePorts = "dvUplink2"
                        $unusedPorts = "dvUplink1", "dvUplink3", "dvUplink4"
                    }
                    $newPG | Get-VDUplinkTeamingPolicy | Set-VDUplinkTeamingPolicy -ActiveUplinkPort $activePorts -UnusedUplinkPort $unusedPorts 
                }
                Write-Host "    Finished Port-Group '$($pg.name)'" -ForegroundColor Blue
            Write-Host "Completed DVSwitch '$($sw.value.name)' in DataCenter '$($DataCenter)'" -ForegroundColor Blue
            Write-Host ""
        }
        }
    }
    
    #=====================================================
    # Alarm Manager and Host Licenses
    #=====================================================
    $alarmMgr = Get-View AlarmManager
    $serviceInstance = Get-view serviceInstance
    $Licenses = Get-view ($serviceInstance.Content.LicenseManager) | Select-Object -ExpandProperty Licenses

    #=====================================================
    # Configure Each ESXi Host
    #=====================================================
    $esxHosts = Get-VMHost -Location $DataCenter
    foreach ($esx_host in $vcenter.servers) {
        foreach($nvme in $esx_host.nvme_adapters) {
            #---------------ConnectNvmeControllerEx_Task---------------
            $specCount = 0
            #$cLength = ($nvme.controllers).Length
            $connectSpec = New-Object VMware.Vim.HostNvmeConnectSpec[] ($cLength2)
            #Write-Host "$($nvme.controllers) $cLength"
        }
        Write-Host "Beginning Configuration for $($esx_host.name)" -ForegroundColor Blue
        #=====================================================
        # Register the Host if it is not Registered
        #=====================================================
        if (!($esxHosts | Where-Object { $esx_host.name -match $_})) {
            Write-Host " Adding $($esx_host.name) to Data Center $DataCenter" -ForegroundColor Green
            Add-VMHost -Location $DataCenter -Name $esx_host.name -User "root" -Password $env:esx_password -Force
            Write-Host "  * Sleeping 60 Seconds to wait for Host Inventory." -ForegroundColor Green
            Start-Sleep -Seconds 60
        } else {
            $esxHost = Get-VMHost -Name $esx_host.name
        }
        
        #=====================================================
        # General Host configuration section
        #=====================================================
        $EsxCli2  = Get-EsxCli -VMHost $esxHost.Name -V2
        $hostName = $esxHost.name.Split(".")[0]
        $hostvms  = 0
        $hostvms  = $esxHost | get-vm
        
        #=====================================================
        # Skip Host if it is Hosting Virtual Machines
        #=====================================================
        if(($hostvms.count -gt 1)) {
            Write-Host "  Host $($esxHost.Name) is Hosting $($hostvms.count) VMs.  Skipping Host." -ForegroundColor Red
            Break
        }
        
        #=====================================================
        # Configure Host License
        #=====================================================
        if ($esxHost.LicenseKey -eq "00000-00000-00000-00000-00000") {
            $esxVersion = $esxHost | Select-Object @{Label = "version"; Expression = {$_.version}}
            $licVersion = ($esxVersion.version).Split(".")[0]
            foreach ($License in $Licenses) {
                if ($esx_host.license_type -eq "enterprise") {
                    if ($License.Name | Select-String -Pattern "$licVersion Enterprise Plus") {
                        $LicAvail = $License.Total - $License.Used
                        if($LicAvail -ge $MostLicAvail) {
                            $MostLicAvail = $LicAvail
                            $LicToUse = $License.LicenseKey
                            Write-Host "  Assigning License to $($esx_host.name)" -ForegroundColor Green
                            Set-VMHost -VMHost $esxHost -LicenseKey $LicToUse 
                        }
                    }
                } elseif ($esx_host.license_type -eq "standard") {
                    if ($License.Name | Select-String -Pattern "$licVersion Standard") {
                        $LicAvail = $License.Total - $License.Used
                        if($LicAvail -ge $MostLicAvail) {
                            $MostLicAvail = $LicAvail
                            $LicToUse = $License.LicenseKey
                            Write-Host "  Assigning License to $($esx_host.name)" -ForegroundColor Green
                            Set-VMHost -VMHost $esxHost -LicenseKey $LicToUse 
                        }
                    }
                } elseif ($esx_host.license_type -eq "vdi") {
                    if ($License.Name | Select-String -Pattern $6DeskHost) {
                        $LicToUse = $License.LicenseKey
                        Write-Host "  Assigning License to $($esx_host.name)" -ForegroundColor Green
                        Set-VMHost -VMHost $esxHost -LicenseKey $LicToUse 
                    }
                }
            }
        }
        
        #=====================================================
        # Put host in Maint Mode and Disable Alarms
        #=====================================================
        Write-Host "  Host ConnectionState is '$($esxHost.ConnectionState)'" -ForegroundColor Green
        if (!($esxHost.ConnectionState -eq "Maintenance")) {
            $esxHost | Set-VMHost -State Maintenance -RunAsync -Confirm:$false
            #$esxHost | Set-VMHost -ConnectionState Maintenance -RunAsync -Confirm:$false
        }
        $alarmMgr.EnableAlarmActions($esxHost.ExtensionData.moRef,$false)            
        
        #=====================================================
        # Customer Expierence Program Opt In
        #=====================================================
        $optIn = $esxHost | Get-AdvancedSetting -Name UserVars.HostClientCEIPOptIn
        $optKey = $optIn.ToString().Split(":")[1]
        if (!($optKey -contains "2")) {
            Write-Host "  Configuring CEIP on $($esxHost.Name)" -ForegroundColor Green
            $esxHost | Set-AdvancedSetting -Name UserVars.HostClientCEIPOptIn -Value 2
        }
        
        #=====================================================
        # Set Power Policy to High Performance
        #=====================================================
        $pwrPolicy = $esxHost.ExtensionData.config.PowerSystemInfo.CurrentPolicy.Key
        if (!($pwrPolicy -eq 1)) {
            Write-Host "  Configure Power Policy to High Performance on $($esxHost.Name)" -ForegroundColor Magenta
            $view = (Get-VMHost $esxHost | Get-View)
            (Get-View $view.ConfigManager.PowerSystem).ConfigurePowerPolicy(1)
            $view = $null
        }
            
        #=====================================================
        # Configure Log Level
        #=====================================================
        $loglvl = "warning"
        Write-Host "  Configure Log Level on $($esxHost.Name)" -ForegroundColor Magenta
        $Logs = $esxHost | Get-AdvancedSetting -Name *.log.level | Set-AdvancedSetting -Value $loglvl -Confirm:$false
        $Logs = $esxHost | Get-AdvancedSetting -Name *.logLevel | Set-AdvancedSetting -Value $loglvl -Confirm:$false
        $Logs.value
        
        #=====================================================
        # Configure Syslog
        #=====================================================
        Write-Host "  Configure Syslog on $($esxHost.Name)" -ForegroundColor Magenta
        $Syslog = $esxHost | Get-AdvancedSetting -Name Syslog.global.logHost | Set-AdvancedSetting -Value $syslogconf -Confirm:$false
        $null = $EsxCli2.system.syslog.reload.Invoke() 
        $Syslog.Value
        
        #=====================================================
        # Configure Firewall Policies
        #=====================================================
        Write-Host "  Configure Firewall Policies on $($esxHost.Name)" -ForegroundColor Magenta
        Get-VMHostFirewallException -VMHost $esxHost | Where-Object {$_.Name.StartsWith('httpClient')} | Set-VMHostFirewallException -Enabled $true
        Get-VMHostFirewallException -VMHost $esxHost | Where-Object {$_.Name.StartsWith('syslog')} | Set-VMHostFirewallException -Enabled $true
        
        #=====================================================
        # Configure NTP Services
        #=====================================================
        Write-Host "  Configure NTP on $($esxHost.Name)" -ForegroundColor Magenta
        $tmpTime = $esxHost |  Get-VMHostNtpServer 
        ForEach ($ntP in $tmpTime) { Remove-VMHostNtpServer -NTPServer $ntP -VMHost $esxHost -Confirm:$false }
        $Null = $esxHost | Get-VMHostService | Where-Object{$_.key -eq "ntpd"} | Set-VMHostService -policy "on" -Confirm:$false
        $Null = $esxHost | Get-VMHostService | Where-Object{$_.key -eq "ntpd"} | Start-VMHostService -Confirm:$false
        foreach($ntpserver in $vcenter.ntp_servers) { Add-VMHostNtpServer -NtpServer $ntpserver -VMHost $esxHost }
        
        #=====================================================
        # Configure DNS Services
        #=====================================================
        Write-Host "  Configure DNS and Domain Name on $($esxHost.Name)" -ForegroundColor Magenta
        $domain = $vcenter.dns_domains[0]
        $domains = $vcenter.dns_domains -join ", "
        $dns = $vcenter.dns_servers -join ", "
        Get-VMHostNetwork -VMHost $esxHost | Set-VMHostNetwork -DomainName $domain -DNSAddress $dns -SearchDomain $domains -Confirm:$false
        $systemDNS = Get-VMHostNetwork -VMHost $esxHost
        Write-Host "    $($esxHost.Name) Domain is $($systemDNS.DomainName)" -ForegroundColor Green
        Write-Host "    $($esxHost.Name) DNS Servers are $($systemDNS.DNSAddress)" -ForegroundColor Green
        Write-Host "    $($esxHost.Name) Search Domains are $($systemDNS.SearchDomain)" -ForegroundColor Green
        
        #=====================================================
        # Disable autocreatedumpfile
        #=====================================================
        $autoDump = $esxHost | Get-AdvancedSetting -Name VMkernel.Boot.autoCreateDumpFile
        $dumpKey = $autoDump.ToString().Split(":")[1]
        if (!($dumpKey -match "False")) {
            Write-Host "  Disable autoCreateDumpFile on $($esxHost.Name)" -ForegroundColor Green
            $esxHost | get-AdvancedSetting -name VMkernel.Boot.autoCreateDumpFile | Set-AdvancedSetting -Value 0 -confirm:$false
        }
        
        #=====================================================
        # Enable SSH And ESX Shell and Disable Warning
        #=====================================================
        $esxHost | Get-VMHostService | Where-Object { $_.Key -eq "TSM" } | Set-VMHostService -Policy "On"
        $esxHost | Get-VMHostService | Where-Object { $_.Key -eq "TSM" } | Start-VMHostService 
        $esxHost | Get-VMHostService | Where-Object { $_.Key -eq "TSM-SSH" } | Set-VMHostService -Policy "On"
        $esxHost | Get-VMHostService | Where-Object { $_.Key -eq "TSM-SSH" } | Start-VMHostService 
        $shellWarn = $esxHost | Get-AdvancedSetting -Name UserVars.SuppressShellWarning
        $shellKey = $shellWarn.ToString().Split(":")[1]
        if (!($shellKey -match "1")) {
            Write-Host "  Disable Shell Warning on $($esxHost.Name)" -ForegroundColor Green
            $esxHost | Get-AdvancedSetting -name UserVars.SuppressShellWarning | Set-AdvancedSetting -Value 1 -confirm:$false
        }
        
        #=====================================================
        # Configure Misc.HppManageDegradedPaths
        #=====================================================
        $hppDp = $esxHost | Get-AdvancedSetting -Name Misc.HppManageDegradedPaths
        $hppDpKey = $hppDp.ToString().Split(":")[1]
        if (!($hppDpKey -match "0")) {
            Write-Host "  Configure HppManageDegradedPaths on $($esxHost.Name)" -ForegroundColor Green
            $esxHost | get-AdvancedSetting -name Misc.HppManageDegradedPaths | Set-AdvancedSetting -Value 0 -confirm:$false
        }
        
        #=====================================================
        # Obtain TPM Recovery Key
        #=====================================================
        $key = $EsxCli2.system.settings.encryption.recovery.list()
        if ($key) { Write-Host "  $($esxHost.Name);$($key.RecoveryId);$($key.Key)" -ForegroundColor Green }
        
        #=====================================================
        # ATS Heartbeating
        #=====================================================
        #if(($EsxCli2.system.settings.advanced.list($false, "/VMFS3/UseATSForHBOnVMFS5")).IntValue -eq "0") {
        #    Write-Host "    ATS Heartbeating already set to 0."
        #    Get-AdvancedSetting -entity $esxHost -Name VMFS3.UseATSForHBOnVMFS5 | Select-Object name, Value
        #} else {
        #    If ($esxHost.version -like "*6.0*") {
        #        Write-Host "    * Getting current ATS Heartbeating setting." -ForegroundColor Blue
        #        Get-AdvancedSetting -entity $esxHost -Name VMFS3.UseATSForHBOnVMFS5 | Select-Object name, Value
        #        Write-Host "    * Changing ATS Heartbeating setting to 0." -ForegroundColor Blue
        #        Get-AdvancedSetting -entity $esxHost -Name VMFS3.UseATSForHBOnVMFS5 | Set-AdvancedSetting -Value 0 -confirm:$false
        #    }
        #}
        
        #=====================================================
        # Set VMhost Name properly for Linux Licensing
        #=====================================================
        $shortCheck = $esxHost | Get-VMHostnetwork
        if (!($shortCheck.hostname -eq $hostName)) {
            $esxHost | Get-VMHostnetwork | Set-VMHostnetwork -hostname $hostName 
        }
        
        #=====================================================
        # Rename local Datastore if present
        #=====================================================
        $localDatastores = $esxHost | Get-Datastore | Where-Object {$_.name -match "^datastore1( \(\d+\))?$"}
        if ($localDatastores) {
            $counter = 1
            foreach($dataStore in $localDatastores) {
                $ldsFolder = Get-Folder -name "Local Datastores"
                if(!($ldsFolder)) {
                    # Create "Local Datastores" folder if not present
                    $dsFolder = get-folder -Type Datastore -Name "datastore"
                    $ldsfolder = new-folder -Location $dsFolder -name "Local Datastores"
                }
                $ldsName = $hostName + "-" + "ds$($counter)"
                $dataStore | set-datastore -name $ldsName -confirm:$false
                $dataStore | move-datastore -destination $ldsFolder
                $counter = $counter + 1
            }
        }
        
        #=====================================================
        # Add Custom Attributes to ESXi Host
        #=====================================================
        $esxHost | Set-Annotation -CustomAttribute "hostConfigured" -Value $true
        $esxHost | Set-Annotation -CustomAttribute "ucsDomain" -Value $vcenter.ucs_domain
        $esxHost | Set-Annotation -CustomAttribute "ucsDn" -Value $esx_host.server_dn
        $esxHost | Set-Annotation -CustomAttribute "ucsSerial" -Value $esx_host.serial
                
        #=====================================================
        # Configure Misc.HppManageDegradedPaths
        #=====================================================
        $hppDp = $esxHost | Get-AdvancedSetting -Name Misc.HppManageDegradedPaths
        $hppDpKey = $hppDp.ToString().Split(":")[1]
        if (!($hppDpKey -match "0")) {
            Write-Host "  Configure HppManageDegradedPaths on $($esxHost.Name)" -ForegroundColor Green
            $esxHost | get-AdvancedSetting -name Misc.HppManageDegradedPaths | Set-AdvancedSetting -Value 0 -confirm:$false
        }
        
        #=====================================================
        # Suppress HyperThreading Warning
        #=====================================================
        foreach ($hostissue in $esxHost.ExtensionData.ConfigIssue) {
            write-host "matched $($hostissue.FullFormattedMessage)"
            if ($hostissue.FullFormattedMessage | Select-String "This host is potentially") {
                write-host "matched"
                Get-AdvancedSetting -Entity $esxHost -Name UserVars.SuppressHyperthreadWarning | Set-AdvancedSetting -Value 1 -Confirm:$false
            }
        }
        
        #=====================================================
        # Configure Host Networking
        #=====================================================
        Write-Host "  Beginning Network Configuration for $($esxHost.Name)" -ForegroundColor Blue
        
        #=====================================================
        # Configure Management Networking
        #=====================================================
        $vmhostnet = Get-VMHostNetwork -VMHost $esxHost.Name
        # If Management VMK is DHCP configure as static
        $mgtVMK = $esxHost | Get-VMHostNetworkAdapter -VMKernel | Where-Object { $_.ManagementTrafficEnabled -eq $true -and $_.Dhcpenabled -eq $true}
        if($mgtVMK) {
            $domainname = $jsonData.servers.$vmhost.domain
            # Set Base IP Stack Items
            $vmhostnet | Set-VMHostNetwork -DnsFromDhcp $false -VMKernelGateway $vmhostnet.VMKernelGateway -DomainName $domainname -SearchDomain $domainname -DnsAddress $vmhostnet.DnsAddress[0],$vmhostnet.DnsAddress[1]
            # Set VMK0 IP Address, Mask
            $mgtVMK | Set-VMHostNetworkAdapter -IP $mgtVMK.IP -SubnetMask $mgtVMK.SubnetMask -Confirm:$false
        }
        $vnics = $esxHost | Get-VMHostNetworkAdapter -Physical
        $vdSwitches = $esxHost | Get-VDSwitch
        
        #=====================================================
        # Configure Each ESXi Host Virtual Switch
        #=====================================================
        $stdvswitches = $esxHost | Get-VirtualSwitch -Standard
        $vdSwitch = Get-VDSwitch -Name $vswitch.name -Location $vcenter.datacenter
        foreach($vswitch in $esx_host.vswitches) {
            $swname = $vswitch.name
            Write-Host "    Virtual Switch is $swname" -ForegroundColor Blue
            Write-Host "    Beginning Configuration for '$($vswitch.name)' on '$($esxHost.name)'" -ForegroundColor Blue
            $vnic1 = $vnics | Where-Object {$_.mac.ToUpper() -eq $vswitch.maca}
            $vnic2 = $vnics | Where-Object {$_.mac.ToUpper() -eq $vswitch.macb}
            Write-Host "    * vmnic1 is $($vnic1)" -ForegroundColor Blue
            Write-Host "    * vmnic2 is $($vnic2)" -ForegroundColor Blue
        
            #=====================================================
            # If Standard vSwitch Create on Host
            #=====================================================
            if ($vcenter.vswitches.$swname.type -eq "standard") {
                if (!($stdvswitches | Where-Object {$_.name -eq $vswitch.name})) {
                    Write-Host "  Configuring Virtual Switch $($vswitch.name) on $($esxHost)" -ForegroundColor Green
                    $stdvswitch = $esxHost | New-VirtualSwitch -Name $vswitch.name -Nic $vnic2 -Mtu $vcenter.vswitches.$swname.mtu
                } else {
                    Write-Host "  Found Existing Virtual Switch $($vswitch.name) on $($esxHost)" -ForegroundColor Blue
                    $stdvswitch = $stdvswitches | Where-Object {$_.name -eq $vswitch.name}
                }
                #=====================================================
                # Configure Standard vSwitch VMKs
                #=====================================================
                $vmks = $esxHost | Get-VMHostNetworkAdapter -VMKernel
                foreach($vmk in $vswitch.vmks) {
                    #=====================================================
                    # Configure Standard vSwitch Port Group for VMK
                    #=====================================================
                    $port_groups = $esxHost | Get-VirtualPortGroup -Standard
                    if (!($port_groups | Where-Object {$_.name -eq $vmk.port_group})) {
                        Write-Host "  Adding Port-Group $($vmk.port_group) to $($swname) on $($esxHost)" -ForegroundColor Green
                        $pg = $vcenter.vswitches.$swname.port_groups | Where-Object {$_.name -eq $vmk.port_group}
                        Write-Host "pg vlan is $($pg | Select-Object *)"
                        if ($pg.vlan -is [int]) {
                            $port_group = $stdvswitch | New-VirtualPortGroup -Name $vmk.port_group -VLanId $pg_vlan.vlan
                        } else { $port_group = $stdvswitch | New-VirtualPortGroup -Name $vmk.port_group }
                    } else {
                        Write-Host "  Found Existing Port-Group $($vmk.port_group) Assigned to $($swname) on $($esxHost)" -ForegroundColor Green
                        $port_group = $port_groups | Where-Object {$_.name -eq $vmk.port_group}
                    }
                    #=====================================================
                    # Configure Standard VMKernel Adapters
                    #=====================================================
                    if (!($vmks | Where-Object {$_.name -eq $vmk.name}) -and !($vmk.name -eq "vmk0")) {
                        Write-Host "      Beginning Configuration for VMKernel $($vmk.name) on host $($esxHost)" -ForegroundColor Green
                        $vmkernel = $port_group | New-VMHostNetworkAdapter -IP $vmk.ip -SubnetMask $vmk.netmask -Mtu $vcenter.vswitches.$swname.mtu
                    } elseif (!($vmkernel.PortGroupName -eq $vmk.port_group)) {
                        Write-Host "      Assigning VMKernel $($vmk.name) on host $($esxHost) to Port Group $($vmk.port_group)" -ForegroundColor Green
                        $vmkernel = $vmks | Where-Object {$_.name -eq $vmk.name}
                        $ArgsObj = $EsxCli2.network.ip.interface.add.CreateArgs()
                        $ArgsObj.interfacename = $vmk.name
                        $ArgsObj.PortGroupName = $port_group.Name
                        $EsxCli2.network.ip.interface.add.Invoke($ArgsObj)
                    } else {
                        Write-Host "      VMKernel $($vmk.name) on host $($esxHost) is Already assigned to Port Group $($vmk.port_group)" -ForegroundColor Blue
                        $vmkernel = $vmks | Where-Object {$_.name -eq $vmk.name}
                    }
                    if ($vmk.vmotion -eq "true") {
                        $esxHost | Get-VMHostNetworkAdapter -Name $vmk.name | Set-VMHostNetworkAdapter -VMotionEnabled $true
                    }
                }
                #=====================================================
                # Configure vNICs
                #=====================================================
                $stdvswitch = $esxHost | Get-VirtualSwitch -Standard -Name $vswitch.name
                $stdvswitch | Get-VirtualPortGroup | Where-Object {$_.Name -eq "VM Network"} | Remove-VirtualPortGroup -Confirm:$false
                if($stdvswitch.ExtensionData.Pnic.Count -lt 2) {
                    if($stdvswitch.ExtensionData.Pnic | Select-String $vnic1.Name) {
                        $stdvswitch | Add-VirtualSwitchPhysicalNetworkAdapter -VMHostPhysicalNic $vnic2 -Confirm:$false
                    } 
                    if ($stdvswitch.ExtensionData.Pnic | Select-String $vnic2.Name) {
                        $stdvswitch | Add-VirtualSwitchPhysicalNetworkAdapter -VMHostPhysicalNic $vnic1 -Confirm:$false
                    }
                    $stdvswitch | Get-NicTeamingPolicy | Set-NicTeamingPolicy -MakeNicActive $vnic1, $vnic2
                }
            
            #=====================================================
            # Configure DVS Switch
            #=====================================================
            } elseif ($vcenter.vswitches.$swname.type -eq "dvs")  {
                if($vdSwitches | Where-Object { $_.Name -eq $vswitch.name }) {
                    #=====================================================
                    # Host is already a member of the dvs confirm config
                    #=====================================================
                    Write-Host "    $($esxHost) is already a member of DVSwitch $($vdSwitch)" -ForegroundColor Blue
        
                    $uplinks = $vdSwitch | Get-VDPort -Uplink | Where-Object {$_.proxyhost.name -eq $esxHost.Name}
                    $vnic1found = $false
                    $vnic2found = $false
                    foreach($uplink in $uplinks) {
                        if($uplink | Select-String $vnic1.Name){$vnic1found = $true}
                        if($uplink | Select-String $vnic2.Name){$vnic2found = $true}
                    }
                    if (!($vnic1found -eq $true)) {
                        Add-VDSwitchPhysicalNetworkAdapter -VMHostPhysicalNic $vnic2 -DistributedSwitch $vdSwitch -VirtualNicPortgroup dvuplink2 -Up -Confirm:$false
                    }
                } else {
                    #=====================================================
                    # Host is not a member of the dvs - add host
                    #=====================================================
                    Write-Host "    * Adding $($esxHost) to DVSwitch $($vswitch.name)" -ForegroundColor Green
                    $vdSwitch | Add-VDSwitchVMHost -VMHost $esxHost
                    
                    #=====================================================
                    # Add second mgmt nic then move VMK
                    #=====================================================
                    Add-VDSwitchPhysicalNetworkAdapter -VMHostPhysicalNic $vnic2 -DistributedSwitch $vdSwitch -Confirm:$false
                }
                #=====================================================
                # Configure DVS VMK Interfaces
                #=====================================================
                foreach($vmk in $vswitch.vmks) {
                    Write-Host "      Beginning Configuration for VMKernel $($vmk.name) on host $($esxHost)" -ForegroundColor Blue
                    $dvsPg = Get-VDPortgroup -Name $vmk.port_group -VDSwitch $vdSwitch
                    $esxVmk = Get-VMHostNetworkAdapter -VMHost $esxHost -VMKernel -Name $vmk.name
                    if (!($vmkPg.Name -eq $esxVmk.PortGroupName)) {
                        if (!($esxVmk.Name)) {
                            $newVMK = New-VMHostNetworkAdapter -VMHost $esxHost -PortGroup $dvsPg -VirtualSwitch $vdSwitch -IP $vmk.ip -SubnetMask $vmk.netmask -Mtu $vcenter.vswitches.$swname.mtu -Confirm:$false
                        } else {
                            $esxVmk | Set-VMHostNetworkAdapter -PortGroup $dvsPg -VirtualSwitch $vdSwitch -IP $vmk.ip -SubnetMask $vmk.netmask -Mtu $vcenter.vswitches.$swname.mtu -Confirm:$false
                        }
                        if ($vmk.vmotion -eq $true) {
                            $esxHost | Get-VMHostNetworkAdapter -Name $vmk.name | Set-VMHostNetworkAdapter -VMotionEnabled $true -Confirm:$false 
                        }
                        if ($vmk.nvme -eq $true) {
                            $ArgsObj = $EsxCli2.network.ip.interface.tag.add.CreateArgs()
                            $ArgsObj.interfacename = $vmk.name
                            $ArgsObj.tagname = "NVMeTCP"
                            $EsxCli2.network.ip.interface.tag.add.Invoke($ArgsObj)
                        }
                    }
                    Write-Host "      Completed Configuration for VMKernel $($newVMK.Name) on host $($esxHost)" -ForegroundColor Blue
                }
                #=====================================================
                # Move 1st vNIC to the DVS
                #=====================================================
                $uplinks = $vdSwitch | Get-VDPort -Uplink | Where-Object {$_.proxyhost.name -eq $esxHost.Name}
                $vnic1found = $false
                $vnic2found = $false
                foreach($uplink in $uplinks) {
                    if($uplink | Select-String $vnic1.Name){$vnic1found = $true}
                    if($uplink | Select-String $vnic2.Name){$vnic2found = $true}
                }
                if (!($vnic1found -eq $true)) {
                    Add-VDSwitchPhysicalNetworkAdapter -VMHostPhysicalNic $vnic1 -DistributedSwitch $vdSwitch -VirtualNicPortgroup dvuplink1 -Confirm:$false
                }
                if (!($vnic2found -eq $true)) {
                    Add-VDSwitchPhysicalNetworkAdapter -VMHostPhysicalNic $vnic2 -DistributedSwitch $vdSwitch -VirtualNicPortgroup dvuplink2 -Confirm:$false
                }
            }
            Write-Host "    Completed Configuration for '$($vswitch.name)' on '$($esxHost.name)'" -ForegroundColor Blue
            Write-Host ""
        
        #=====================================================
        # Configure iSCSI Software Adapter
        #=====================================================
        foreach($iscsi in $esx_host.iscsi) {
            Write-Host "  Beginning Configuration for iSCSI Software Adapter on host $($esxHost)" -ForegroundColor Blue
            #Enable Software iSCSI Adapter
            $softAdapter = Get-VMHostStorage -VMHost $esxHost
            if (!($softAdapter.SoftwareIScsiEnabled -eq $true)) {
                #Bind the iSCSI VMKernel Adapter(s) to Software iSCSI Adapter (credit to Luc Dekens for this)
                $softAdapter | Set-VMHostStorage -SoftwareIScsiEnabled $True
                foreach($dvPg in $iscsi.port_groups) {
                    Write-Host "    Binding iSCSI Adapter to $dvPg" -ForegroundColor Green
                    $bind = @{
                        adapter = ($iscsiHBA = $esxHost | Get-VMHostHba -Type iScsi | Where-Object {$_.Model -eq "iSCSI Software Adapter"}).Device
                        force = $true
                        nic = $dvPg
                    }
                    $EsxCli2.iscsi.networkportal.add.Invoke($bind)
                }
                #Add Dynamic Discovery Target
                foreach($target in $iscsi.targets) {
                    Write-Host "    Adding Target $target" -ForegroundColor Green
                    $esxHost | Get-VMHostHba $iscsiHBA | New-IScsiHbaTarget -Address $target
                }
            }
            $iscsiName = $esxHost | Get-VMHostHba -Type iScsi | Where-Object {$_.Model -eq "iSCSI Software Adapter"}
            $storageOutput.iscsi += @(@{host = $hostName; iqn = $iscsiName.IScsiName})
            #Rescan Hba
            #Get-VMHostStorage -VMHost $esxHost -RescanAllHba
            Write-Host "  Completed Configuration for iSCSI Software Adapter on host $($esxHost)" -ForegroundColor Blue
            Write-Host ""
        }
        
        #=====================================================
        # Configure NFS Datastores
        #=====================================================
        $dataStores = $esxHost | Get-Datastore
        foreach ($dStore in $vcenter.datastores) {
            Write-Host "  Beginning Datastore $($dStore.name) configuration on $($esxHost)" -ForegroundColor Blue
            if (-Not($dataStores | Where-Object { $dStore.name -match $_})) {
                Write-Host "  * Adding Datastore $($dStore.name) to $($esxHost)" -ForegroundColor Green
                $dataStore = $esxHost | New-Datastore -Nfs -Name $dStore.name -Path $dStore.path -NfsHost $dStore.target
            } else {
                Write-Host "  * Datastore $($dStore.name) already exists on $($esxHost)" -ForegroundColor Blue
                $dataStore = $esxHost | Get-Datastore -Name $dStore.name
            }
            if ($Dstore.type -eq "swap") {
                if (!(($esxHost.VMSwapfileDatastore).toSTring() -eq ($dataStore.Name).toString())) {
                    Write-Host "    Configuring SWAP Location" -ForegroundColor Green
                    Get-VMHost $esxHost | Set-VMHost -VMSwapfileDatastore $dataStore
                }
            }
            Write-Host "  Completed Datastore $($dStore.name) configuration on $($esxHost)" -ForegroundColor Blue
            Write-Host ""
        }
        # Remove all standard vswitches that are not Configured in the JSON File.
        $unused_vsws = $esxHost | Get-VirtualSwitch -Standard
        foreach($vswitch in $unused_vsws) {
            if (!($esx_host.vswitches | Where-Object {$_.name -eq $vswitch.name})) {
                $unused_vsw = $unused_vsws | Where-Object {$_.name -eq $vswitch.name}
                $unused_vsw | Remove-VirtualSwitch -Confirm:$false
            }
        }

        #=====================================================
        # Configure NVMe Software Adapter(s)
        #=====================================================
        foreach($nvme in $esx_host.nvme_adapters) {
            Write-Host "  Beginning Configuration for NVMe Software Adapter(s) on host $($esxHost)" -ForegroundColor Blue
            #Enable Software NVMe Adapters
            $hostStorage = Get-VMHostStorage -VMHost $esxHost
            $hostView    = Get-View -Id $hostStorage.Id
            $physicalNic = $vnics | Where-Object {$_.mac.ToUpper() -eq $nvme.mac_address}
            Write-Host "    Physical NIC is $($physicalNic)" -ForegroundColor Green
            Write-Host "    $($esxHost) Storage ID is $($hostStorage.Id)" -ForegroundColor Green
            $nvmePnic = $hostView.StorageDeviceInfo.HostBusAdapter | Select-Object * | Where-Object {$_.AssociatedPnic -eq $physicalNic}
            if (!($nvmePnic)) {
                #---------------CreateSoftwareAdapter---------------
                $spec = New-Object VMware.Vim.HostTcpHbaCreateSpec
                $spec.Pnic = $physicalNic
                $hostView.CreateSoftwareAdapter($spec)
                Write-Host "    * Sleep For 5 Seconds to Wait for Software Adapter Creation." -ForegroundColor Green
                Start-Sleep -Seconds 5
                $hostView = Get-View -Id $hostStorage.Id
                $nvmePnic = $hostView.StorageDeviceInfo.HostBusAdapter | Select-Object * | Where-Object {$_.AssociatedPnic -eq $physicalNic}
                Write-Host "    * Added NVMe TcpHba on $($nvmePnic.Device)" -ForegroundColor Green
                exit
                
                #---------------ConnectNvmeControllerEx_Task---------------
                $specCount = 0
                #$cLength = ($nvme.controllers).Length
                $connectSpec = New-Object VMware.Vim.HostNvmeConnectSpec[] ($cLength2)
                foreach ($controller in $nvme.controllers) {
                    $connectSpec[$specCount] = New-Object VMware.Vim.HostNvmeConnectSpec
                    $connectSpec[$specCount].ControllerId = 65535
                    $connectSpec[$specCount].Subnqn = $nvme.subsystem_nqn
                    $connectSpec[$specCount].TransportParameters = New-Object VMware.Vim.HostNvmeOverTcpParameters
                    $connectSpec[$specCount].TransportParameters.Address = $controller
                    $connectSpec[$specCount].TransportParameters.DigestVerification = 'digestDisabled'
                    $connectSpec[$specCount].TransportParameters.PortNumber = 4420
                    $connectSpec[$specCount].HbaName = $($nvmePnic.Device)
                    $specCount = $specCount + 1
                }
                $hostView.ConnectNvmeControllerEx_Task($connectSpec)
                Write-Host "    * Added Discovery Controller $($nvme.controller)" -ForegroundColor Green
                Write-Host "    Triggered Discovery" -ForegroundColor Green
            } else {
                Write-Host "    Physical NIC Storage Device is $($nvmePnic.Device)" -ForegroundColor Magenta
                Write-Host "    NVMe Already Configured on $($nvmePnic.Device)" -ForegroundColor Magenta
            }
            Write-Host "  Completed Configuration for NVMe Software Adapter(s) on host $($esxHost)" -ForegroundColor Blue
            Write-Host ""
        }
        if ($esx_host.nvme_adapters) {
            $nvmeId = $EsxCli2.nvme.info.get.invoke()
            $storageOutput.nvme += @(@{host = $hostName; nqn = $nvmeId.HostNQN})
        }

        #=====================================================
        # Add Host to Cluster
        #=====================================================
        $cluster = $esxHost | Get-Cluster
        $model = $esxHost | Select-Object -Property Model
        Write-Host "  Add $($esxHost) to Cluster $($model.Model)." -ForegroundColor Blue
        if (-Not($cluster.Name -eq $model.Model)) {
            $cluster = Get-Cluster -Name $model.Model
            Write-Host "  * Adding $($esxHost) to Cluster $($cluster.name)." -ForegroundColor Green
            Move-VMHost $esxHost -Destination $cluster
        } else {
            Write-Host "  * Host $($esxHost) already a part of Cluster $($model.Model)" -ForegroundColor Blue
        }
        Write-Host "  Completed $($esxHost) Cluster Configuration." -ForegroundColor Blue
        Write-Host ""

        #=====================================================
        # Put host in Maint Mode and Disable Alarms
        #=====================================================
        Write-Host "  Host ConnectionState is '$($esxHost.ConnectionState)'" -ForegroundColor Green
        if (!($esxHost.ConnectionState -eq "Maintenance")) {
            $esxHost | Set-VMHost -ConnectionState Connected -RunAsync -Confirm:$false
        }
        Write-Host "Completed Configuration for $($esx_host.name)" -ForegroundColor Blue
        Write-Host ""
        }
    }
    
    #=====================================================
    # Configure vCLS Datastore for Pinning vCLS VMs
    #=====================================================
    $clusters = Get-Cluster -Location $DataCenter
    $dataStores = $esxHost | Get-Datastore
    foreach ($cluster in $clusters) {
        foreach ($dStore in $vcenter.datastores) {
            if ($dStore.type -eq "vcls") {
                $dataStore = Get-Datastore -Name $dStore.name
                $ds1 = $dataStore.Id.Split("-")[2]
                $dsId = "datastore-$($ds1)"
                $clsView = Get-View -Id $cluster.Id
                $dsAllow = $clsView.ConfigurationEx.SystemVMsConfig.AllowedDatastores
                if (!($dsAllow.Value.toString() -eq $dsId)) {
                    Write-Host "Setting Datastore $($dStore.name) for Cluster $($cluster.Name) vCLS VMs." -ForegroundColor Green
                    $spec = New-Object VMware.Vim.ClusterConfigSpecEx
                    $spec.DrsConfig = New-Object VMware.Vim.ClusterDrsConfigInfo
                    $spec.SystemVMsConfig = New-Object VMware.Vim.ClusterSystemVMsConfigSpec
                    $spec.SystemVMsConfig.AllowedDatastores = New-Object VMware.Vim.ClusterDatastoreUpdateSpec[] (1)
                    $spec.SystemVMsConfig.AllowedDatastores[0] = New-Object VMware.Vim.ClusterDatastoreUpdateSpec
                    $spec.SystemVMsConfig.AllowedDatastores[0].Datastore = New-Object VMware.Vim.ManagedObjectReference
                    $spec.SystemVMsConfig.AllowedDatastores[0].Datastore.Type = 'Datastore'
                    $spec.SystemVMsConfig.AllowedDatastores[0].Datastore.Value = $dsId
                    $spec.SystemVMsConfig.AllowedDatastores[0].Operation = 'add'
                    $spec.DpmConfig = New-Object VMware.Vim.ClusterDpmConfigInfo
                    $modify = $true
                    $clsView.ReconfigureComputeResource_Task($spec, $modify)
                }
            }
        }
    }
    
    # Close vCenter Connection
    $null = Disconnect-VIServer $vcenter -Force -Confirm:$false
    Write-Host "Completed vSphere configuration on $($vcenter.name).  Exiting Script."
    Write-Host ""
}
$storageOutput | ConvertTo-Json -depth 5 | Set-Content "esx_host_identifiers.json"

Stop-Transcript
Exit