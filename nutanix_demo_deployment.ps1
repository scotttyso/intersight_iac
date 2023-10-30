<#

.SYNOPSIS
                This script automates the upgrade of UCS firmware

.DESCRIPTION
                This script logs into Cisco.com, download firmware bundles to a local working directory, upload bundles to the target UCS domain and walk through all steps of the upgrade

.EXAMPLE
                ucsm_fwupdate_vmware.ps1 -y ucsm_fwupdate.yaml
                Example YAML INPUT File:
                ---
                ucs_manager: myucs.example.com
                upgrade:
                  fabric_interconnect: true
                  fw_version: 4.3(2b)
                  image_directory: "IMAGES"
                  servers: true
                vcenter:
                  clusters:
                    - name: EXAMPLE_CLUSTER
                      hosts:
                        - server1.example.com
                        - server2.example.com
                  hostname: vcenter.example.com

.NOTES
                Author: Eric Williams & Tyson Scott
                Email: ericwill@cisco.com, tyscott@cisco.com
                Company: Cisco Systems, Inc.
                Versions: v1.1, v2.0
                Date: 06/05/2014, 10/28/2023
                Disclaimer: Code provided as-is.  No warranty implied or included.  This code is for example use only and not for production

.INPUTS
                YAML_FILE

.OUTPUTS
                None

.LINK
                https://communities.cisco.com/docs/DOC-36062

#>

param(
    [parameter(Mandatory=${true})][string]${y}=$(throw "-y <yaml_file> is required.")
)

function Set-LogFilePath($LogFile) {
    Write-Host "Creating log file under directory ${LogFile}\Logs\"
    $Global:LogFile = "$LogFile\Logs\Script.$(Get-Date -Format yyyy-MM-dd.hh-mm-ss).log"
    if([System.IO.File]::Exists($Global:LogFile) -eq $false) { $null = New-Item -Path $Global:LogFile -ItemType File -Force }
}

function Write-Log {
    [CmdletBinding()]
    param  (
        [Parameter(ValueFromPipeline=$true,ValueFromPipelineByPropertyName=$true)]
        [String] $Message
    )
    $lineNum = (Get-PSCallStack).ScriptLineNumber[1]
    $Message = "Line: $lineNum - $Message"

    $ErrorActionPreference = 'Stop'

    "Info: $(Get-Date -Format g): $Message" | Out-File $Global:LogFile -Append
    Write-Host $Message
}

function Write-ErrorLog {
    [CmdletBinding()]
    param (
        [Parameter(ValueFromPipeline=$true,ValueFromPipelineByPropertyName=$true)]
        [object] $Message
    )
    $lineNum = (Get-PSCallStack).ScriptLineNumber[1]
    $Message = "Line: $lineNum - $Message"

    "Error: $(Get-Date -Format g):" | Out-File $Global:LogFile -Append
    $Message | Out-File $LogFile -Append
    Write-Error $Message
    Disconnect-Ucs -ErrorAction Ignore | Out-Null
    Disconnect-VIServer -ErrorAction Ignore -Confirm:$False | Out-Null
    Exit 1
}

function Connect-UcsManager {
    # IP address and credentials to access the management server software that manages
    # firmware updates for the nodes of the solution.
    $ucsConnection = Connect-Ucs -Name ${ucs} -Credential ${ucsCred} -ErrorVariable errVar -ErrorAction SilentlyContinue
    if ($errVar) {
        Write-Log "Error attempting to connect to UCS Manager at $(${ucs}). Details: $errVar"
        return $null
    } else {
        Write-Log "Connected to Cisco UCS Manager $(${ucs})"
        return $ucsConnection
    }
}
function WaitUcsManagerActivation {
    $count = 0
    $ucsConnection = $null
    while ($null -eq $ucsConnection) {
        if ($count -eq 20) {
            Write-Log "Error creating a session to UCS Manager even after 20 attempts"
            return $null
        }
        Write-Log "Checking if UCS Manager $($Parameters.ManagementServerAddress) is reachable.."
        if ((Test-Connection -ComputerName ${ucs} -Quiet) -ne $true) {
            $count++
            Write-Log "UCS Manager is still not reachable.."
            Write-Log "Sleeping for 30 seconds.. "
            Start-Sleep -Seconds 30
            continue
        }
        $count++
        Write-Log "Attempt # $count - Trying to login to UCS Manager..."
        $ucsConnection = Connect-UcsManager
        if ($null -eq $ucsConnection) {
            Write-Log "Error creating a session to UCS Manager "
            Write-Log "Sleeping for 30 seconds..."
            Start-Sleep -Seconds 30
        } else {
            Write-Log "Successfully logged back into UCS Manager"
            return $ucsConnection
        }
    }
}

function Wait-UcsFabricInterconnectActivation($fiDetails) {
    $count = 0
    $isComplete = $false
    do {
        if ($count -eq 20) {
            Write-Log "Error FI activation is still not completed even after 20 minutes. Exiting with error now"
            return $false
        }
        $count++
        Write-Log "Getting the status of FI $($fiDetails.Id)..."
        try {
            $fwStatus = $fiDetails | Get-UcsFirmwareStatus -ErrorAction Stop| Select-Object OperState
            switch ($fwStatus.OperState) {
                { @("bad-image", "failed", "faulty-state") -contains $_ } { Write-Log "Firmware activation of the Fabric Interconnect $($fiDetails.Id) has failed. Status is $fwStatus"; $isComplete = $true; return $false }
                "ready" { Write-Log "Firmware activation of the Fabric Interconnect $($fiDetails.Id) is complete"; $isComplete = $true; return $true }
                { @("activating", "auto-activating", "auto-updating", "rebooting", "rebuilding", "scheduled", "set-startup", "throttled", "upgrading", "updating", "") -contains $_ }
                {
                    Write-Log "Firmware activation is in progress $fwStatus";
                    Write-Log "Sleeping for 1 minute...";
                    Start-Sleep -Seconds 60;
                    break
                }
            }
        } catch {
            Write-Log "Failed to get the status of the firmware update process. $_.Exception"
            throw $_.Exception
        }
    }
    while ($isComplete -eq $false)
}

function AckUcsFIRebootEvent {
    $count = 0
    while ($null -eq $fwAck) {
        $count++
        Write-Log "Checking if there is a Pending activity generated for the activation of the Primary FI"
        $fwAck = Get-UcsFirmwareAck -Filter 'OperState -ilike waiting-for-*'
        if ($null -eq $fwAck) {
            Write-Log "Pending activity is not generated yet sleeping for 1 minute and then retrying the operation.."
            Start-Sleep -Seconds 60
        }
        if ($count -ge 40) {
            Write-ErrorLog "Pending activity is not generated. This is an error case. Terminating firmware update"
        }
    }
    Write-Log "UCS Manager has generated a pending activity for primary FI reboot."
    Write-Log "Acknowledging the reboot of the primary FI now"
    Get-UcsFirmwareAck -Filter 'OperState -ilike waiting-for-*' | Set-UcsFirmwareAck -AdminState "trigger-immediate" -Force | Out-Null
    Write-Log "Activation of the primary FI has started"
    Write-Log "This will take few minutes. Sleeping for 5 minutes.."
    Start-Sleep -Seconds 300
}

function ActivateUcsPrimaryFI {
    $count = 0
    $isCompleted = $false
    $primaryFI = ""
    while (!$isCompleted) {
        $fwStatus = $null
        $count++
        if ($count -ge 20) {
            Write-ErrorLog "FI activation is still not completed even after 20 minutes. Exiting with error now"
        }
        if (Get-UcsStatus -ErrorAction SilentlyContinue -ErrorVariable errVar | Where-Object { $_.HaConfiguration -eq "cluster" }) {
            $primary = Get-UcsMgmtEntity -LeaderShip primary -ErrorAction SilentlyContinue -ErrorVariable errVar
            if($null -eq $primary) {
                $fwStatus = Get-UcsNetworkElement -Id $primary.Id -ErrorAction SilentlyContinue -ErrorVariable errVar | Get-UcsFirmwareStatus | Select-Object OperState
            }
        } else {
            $primary = Get-UcsNetworkElement -ErrorAction SilentlyContinue -ErrorVariable errVar
            if($null -eq $primary) {
                $fwStatus = Get-UcsNetworkElement -ErrorAction SilentlyContinue -ErrorVariable errVar | Get-UcsFirmwareStatus | Select-Object OperState
            }
        }

        if ( ($null -eq $fwStatus) -or ($null -eq $primary)) {
            Write-Log "UCS Manager is not reachable.. Details: $errVar"
            Write-Log "UCS Manager connection is reset. Reconnecting.."
            Disconnect-Ucs -ErrorAction Ignore | Out-Null
            $ucsConnection = WaitUcsManagerActivation
            if ($null -eq $ucsConnection) {
                Write-Log "ERROR: Unable to login back to the UCS Manager even after multiple retries."
                Write-Log "Terminating firmware update"
                Write-ErrorLog "Firmware Activation has failed"
            } else {
                #Setting the DefaultUcs so that we don't need to specify the handle for every method call
                $ExecutionContext.SessionState.PSVariable.Set("DefaultUcs", $ucsConnection)
                if (Get-UcsStatus | Where-Object { $_.HaConfiguration -eq "cluster" }) {
                    $primaryFI = Get-UcsNetworkElement -Id (Get-UcsMgmtEntity -Leadership primary).Id
                } else {
                    $primaryFI = Get-UcsNetworkElement
                }
                $primaryActivated = Wait-UcsFabricInterconnectActivation $primaryFI
                if (!$primaryActivated) {
                    Write-Log "ERROR: Activation of firmware faled on the $($subordFI.Id)"
                    Write-ErrorLog "Firmware Activation has failed"
                } else {
                    $updatedVersion = $primaryFI | Get-UcsMgmtController | Get-UcsFirmwareRunning -Deployment system | Select-Object PackageVersion
                    Write-Log "Activation of firmware on $($primaryFI.Id) is successful. Updated version is $($updatedVersion.PackageVersion)"
                    break
                }
            }
        } else {
            Write-Log "Activation of the primary FI is still in progress $($fwStatus.OperState)"
            Write-Log "Sleeping for a minute.."
            Start-Sleep -Seconds 60
        }
    }
    Disconnect-Ucs -ErrorAction Ignore | Out-Null
}

# Import Modules
$module_names = @("Cisco.UcsManager", "Cisco.Ucs.Core", "powershell-yaml")
foreach ($module in $module_names) {
    if (!(Get-MOdule -ListAvailable -Name $module)) {
        Write-Host "Installing Module: $($module)." -ForegroundColor Green
        Install-Module $module -AcceptLicense -AllowClobber -Confirm:$False -Force | Out-Null
        Import-Module $module | Out-Null
    } else {
        Write-Host "Loading Module: $($module)" -ForegroundColor Cyan
        Import-Module $module | Out-Null
    }
}

if (!(Test-Path -path $y)) {
    Write-Host "!!!! Error !!!!" -ForegroundColor Red
    Write-Host "yaml_file: $y, does not exist.  Validate File and Path are Correct." -ForegroundColor Red
    Exit 1
}
$ydata = Get-Content -Path $y | ConvertFrom-Yaml

# Setup LogFilePath Location
${imageDir} = $ydata.upgrade.image_directory
Set-LogFilePath ${imageDir}
    
# Script only supports one UCS Domain update at a time
Set-UcsPowerToolConfiguration -SupportMultipleDefaultUcs $false | Out-Null
Set-PowerCLIConfiguration -InvalidCertificateAction Ignore -Confirm:$false | Out-Null

# Get Home Path
${env_vars} = Get-Childitem -Path Env:* | Sort-Object Name
if ((${env_vars} | Where-Object {$_.Name -eq "OS"}).Value -eq "Windows_NT") {
    $homePath = (${env_vars} | Where-Object {$_.Name -eq "HOMEPATH"}).Value
    $pathSep  = "\"
} else {
    $homePath = (${env_vars} | Where-Object {$_.Name -eq "HOME"}).Value
    $pathSep  = "/"
}

# Global Variables
$WarningPreference = "SilentlyContinue"

Try {
    ${Error}.Clear()
    ########################################
    # UCS Manager Credentials
    ########################################
    $credPath = $homePath + $pathSep + "ucsmpowercli.Cred"
    if (Test-Path -Path $credPath) {
        Write-Log "Found Existing Credentials for UCS Manager."
        Write-Log ""
        ${ucsCred} = Import-CliXml -Path $credPath
    } else {
        Write-Log "Enter Credentials of UCS Manager to be upgraded to version: '$($version)'"
        Write-Log ""
        ${ucsCred} = Get-Credential -Message "Enter Credentials of UCS Manager to be upgraded"
        ${ucsCred} | Export-CliXml -Path $credPath
    }
    ########################################
    # Login to UCS Manager
    ########################################
    ${ucs} = $ydata.domain.hostname
    Write-Log "Logging into UCS Domain: '$(${ucs})'"
    Write-Log ""
    $ucsConnection = Connect-UcsManager
    #Setting the DefaultUcs so that we don't need to specify the handle for every method call
    $ExecutionContext.SessionState.PSVariable.Set("DefaultUcs", $ucsConnection)
    ########################################
    # UCS Firmware Image Definitions
    ########################################
    ${fi} = Get-UcsNetworkElement | Select-Object -First 1
    if ($fi.Model -cmatch "^UCS-FI-(?<modelNum>65\d\d).*$") { $FI6500 = $true
    } elseif ($fi.Model -cmatch "^UCS-FI-(?<modelNum>64\d\d).*$") { $FI6400 = $true
    } elseif ($fi.Model -cmatch "^UCS-FI-M-(?<modelNum>6324).*$") { $FI6324 = $true
    } elseif ($fi.Model -cmatch "^UCS-FI-(?<modelNum>63\d\d).*$") { $FI6300 = $true
    }
    ${version} = $ydata.upgrade.fw_version
    ${infraVersionA} = ${version} + 'A'
    ${infraVersionB} = ${version} + 'B'
    ${infraVersionC} = ${version} + 'C'
    ${versionBundle}  = ${version}.Replace("(", ".").Replace(")", ".")
    ${bundle} = @()
    ${ccoImageList} = @()
    if ($FI6500) { ${aSeriesBundle} = "ucs-6500-k9-bundle-infra." + ${versionBundle} + "A.bin"
    } elseif ($FI6400) { ${aSeriesBundle} = "ucs-6400-k9-bundle-infra." + ${versionBundle} + "A.bin"
    } elseif ($FI6324) { ${aSeriesBundle} = "ucs-mini-k9-bundle-infra." + ${versionBundle} + "A.bin"
    } elseif ($FI6300) { ${aSeriesBundle} = "ucs-6300-k9-bundle-infra." + ${versionBundle} + "A.bin"
    } else  { ${aSeriesBundle} = "ucs-k9-bundle-infra." + ${versionBundle} + "A.bin"
    }
    ${bSeriesBundle} = "ucs-k9-bundle-b-series." + ${versionBundle} + "B.bin"
    ${cSeriesBundle} = "ucs-k9-bundle-c-series." + ${versionBundle} + "C.bin"
    ${bundle} = @(${aSeriesBundle},${bSeriesBundle},${cSeriesBundle})
    ########################################
    # Check Local Directory for Existing Images
    ########################################
    Write-Log "Starting Firmware download process to local directory: ${imageDir}"
    Write-Log ""
    foreach(${eachBundle} in ${bundle}) {
        ${fileName} = ${imageDir} +  $pathSep + ${eachBundle}
         if( Test-Path -Path ${fileName}) {
              Write-Log "Image File : '${eachBundle}' already exist in local directory: '${imageDir}'"
         } else {
              ${ccoImageList} += ${eachBundle}
         }
    }
    ########################################
    # Download Firmware from Cisco.com
    ########################################
    if(${ccoImageList} -ne ${null}) {
        $credPath = $homePath + $pathSep + "ccopowercli.Cred"
        # Obtain CCO Credentials
        if (Test-Path -Path $credPath) {
            Write-Log "Found Existing Credentials for Cisco.com (CCO) Credentials."
            Write-Log ""
            ${ccoCred} = Import-CliXml -Path $credPath
        } else {
            Write-Log "Enter Cisco.com (CCO) Credentials"
            Write-Log ""
            ${ccoCred} = Get-Credential -Message "Enter Cisco.com (CCO) Credentials"
            ${ccoCred} | Export-CliXml -Path $credPath
        }
        foreach(${eachbundle} in ${ccoImageList}) {
            [array]${ccoImage} += Get-UcsSoftwareImageList -AllReleases -Credential ${ccoCred} -ErrorAction Stop | Where-Object { $_.ImageName -match ${eachbundle}}
            Write-Log "Preparing to download UCS Manager version '$($version)' bundle file: '$($eachbundle)'"
        }
        ${Error}.Clear()
        Write-Log  "Downloading UCS Manager version: '$($version)' bundles to local directory: $($imageDir)"
        ${ccoImage} | Get-UcsSoftwareImage -Path ${imageDir} -ErrorAction Stop
    }
    Write-Log "Firmware download process completed to local directory: ${imageDir}"
    Write-Log ""
    ########################################
    # Upload Images to Fabric Interconnects
    ########################################
    foreach (${image} in ${bundle}) {
        Write-Log "Checking if image file: '$($image)' is already uploaded to UCS Domain: '$($ucs)'"
        ${firmwarePackage} = Get-UcsFirmwarePackage -Name ${image}
        ${deleted} = $false
        if (${firmwarePackage}) {
               # Check if all the images within the package are present by looking at presence
            ${deleted} = ${firmwarePackage} | Get-UcsFirmwareDistImage | Where-Object { $_.ImageDeleted -ne ""}
        }
    
        if (${deleted} -or !${firmwarePackage}) {
            $Error.Clear()
            # If Image does not exist on FI, uplaod
            $fileName = ${imageDir} +  $pathSep + ${image}
            if((Get-UcsFirmwareDownloader -FileName ${image} -TransferState failed).count -ne 0) {
                Write-ErrorLog "Image: '$($image)' already exists under Download Tasks in failed state. Exiting..."
            }
            Write-Log "Uploading image file: '$($image)' to UCS Domain: '$($ucs)'"
            Send-UcsFirmware -LiteralPath $fileName | Watch-Ucs -Property TransferState -SuccessValue downloaded -FailureValue failed -PollSec 30 -TimeoutSec 1200 -ErrorAction SilentlyContinue | Out-Null
            if ($Error -ne "") {
                Write-ErrorLog "Error uploading image: '$($image)' to UCS Domain: '$($ucs)'. Please check Download Tasks for details."
            }
            Write-Log "Upload of image file: '$($image)' to UCS Domain: '$($ucs)' completed"
            Write-Log ""
        } else {
            Write-Log "Image file: '$($image)' is already uploaded to UCS Domain: '$($ucs)'"
            Write-Log ""
        }
    }
    ########################################
    # Install Infrastructure Firmware
    ########################################
    # Check if the status of the firmware boot unit is ready before proceeding with the firmware update
    if (!(Get-UcsNetworkElement | Get-UcsMgmtController | Get-UcsFirmwareBootDefinition  | Get-UcsFirmwareBootUnit | Where-Object { $_.OperState -eq 'ready'})) {
        Write-ErrorLog "Fabric Interconnect is not in ready state. Can't proceed with Firmware update."
        Disconnect-Ucs
        Exit 1
    }
    # Start the Firmware Auto Install for the Infrastructure update. This will take care of updating the UCS Manager
    # both the Fabric Interconnects.
    $activatedVersion = Get-UcsMgmtController -Subject system | Get-UcsFirmwareRunning -Type system | Select-Object Version
    if ($activatedVersion.Version -ne ${version} -and $ydata.upgrade.fabric_interconnect -eq $true) {
        Write-Log "Triggering the auto install of the infrastructure firmware to $aSeriesBundle"
        try {
            Start-UcsTransaction | Out-Null
            Get-UcsOrg -Level root | Get-UcsFirmwareInfraPack -Name "default" -LimitScope | Set-UcsFirmwareInfraPack -ForceDeploy "yes" -InfraBundleVersion ${infraVersionA} -Force | Out-Null
            Get-UcsSchedule -Name "infra-fw" | Get-UcsOnetimeOccurrence -Name "infra-fw" | Set-UcsOnetimeOccurrence -Date (Get-UcsTopSystem).CurrentTime -Force | Out-Null
            Complete-UcsTransaction -ErrorAction Stop | Out-Null
        } catch { Write-ErrorLog "Failed to start firmware auto install process. Details: $_.Exception" }
    
        Write-Log "Waiting until UCS Manager restarts"
        Disconnect-Ucs -ErrorAction Ignore | Out-Null
        Write-Log "Sleeping for 5 minutes ..."
        Start-Sleep -Seconds 300
        $ucsConnection = WaitUcsManagerActivation
        #Setting the DefaultUcs so that we don't need to specify the handle for every method call
        $ExecutionContext.SessionState.PSVariable.Set("DefaultUcs", $ucsConnection)
        #Check if UCSM got activated to the new version.
        Write-Log "Checking the status of the firmware installation"
        #---->
        $activatedVersion = Get-UcsMgmtController -Subject system | Get-UcsFirmwareRunning -Type system | Select-Object Version
    
        if ($activatedVersion.Version -eq ${version}) {
            Write-Log "UCS Manager is activated to the $activatedVersion successfully"
        } else {
            Write-Log "Activation has failed so terminating the update process"
            Write-ErrorLog "UCS Manager is at $activatedVersion version"
        }
    
        Start-Sleep -Seconds 60
        Write-Log "Checking the status of the FI activation"
        # Now check for the status of the FI activation. As part of the auto install first the secondary FI will be activated.
        if (Get-UcsStatus | Where-Object { $_.HaConfiguration -eq "cluster" }) {
            while ($null -eq $subordFIActivated)  {
                try {
                    $subordFI = Get-UcsNetworkElement -Id (Get-UcsMgmtEntity -Leadership subordinate -ErrorAction Stop).Id    -ErrorAction Stop
                    $subordFIActivated = Wait-UcsFabricInterconnectActivation $subordFI
                } catch {
                    Write-Log "Failed to get the status $_.Exception"
                    Disconnect-Ucs -ErrorAction Ignore | Out-Null
                    $ucsConnection = WaitUcsManagerActivation
                    if ($null -eq $ucsConnection) {
                        Write-ErrorLog "Unable to connect to the UCS Manager. Terminating the process.."
                    }
                    #Setting the DefaultUcs so that we don't need to specify the handle for every method call
                    $ExecutionContext.SessionState.PSVariable.Set("DefaultUcs", $ucsConnection)
                }
            }
            if (!$subordFIActivated) {
                Write-ErrorLog "Activation of firmware failed on the $($subordFI.Id)"
            } else {
                $updatedVersion = $subordFI | Get-UcsMgmtController | Get-UcsFirmwareRunning -Deployment system | Select-Object PackageVersion
                Write-Log "Activation of firmware on $($subordFI.Id) is successful."
                Start-Sleep -Seconds 30
                AckUcsFIRebootEvent
                ActivateUcsPrimaryFI
            }
        } else {
            AckUcsFIRebootEvent
            ActivateUcsPrimaryFI
        }
    } elseif ($ydata.upgrade.fabric_interconnect -eq $false) {
        Write-Log "Fabric Interconnect Upgrade set to False. Skipping FI upgrade..."
    } else { Write-Log "UCS Manager is already at $activatedVersion version. Skipping FI upgrade..." }
    
    ########################################
    # UCS Manager Organization
    ########################################
    if ($null -eq $ydata.domain.organization -or '' -eq $ydata.domain.organization) {
        $org_name = 'root'; $org_dn = 'org-root'
    } else { $org_name = $ydata.domain.organization; $org_dn = "org-root/org-$($ydata.domain.organization)" }
    if (!(Get-UcsOrg | Where-Object {$_.Dn -eq $org_dn })) {
        Write-Log "Adding Organization '$org_dn'."
        Write-Log ""
        Add-UcsOrg -Name $org_name | Out-Null
    } else {
        Write-Log "Organization '$org_dn' already exists."
        Write-Log ""
    }
    $name_prefix = $ydata.domain.name_prefix
    $vlans = $ydata.domain.vlans
    ########################################
    # IP POOLS
    ########################################
    $dns_servers = $ydata.dns_servers
    if ($dns_servers.length -gt 1) { $secondary = $dns_servers[1] } else { $secondary = "0.0.0.0" }
    $ip_pools = Get-UcsIpPool -Org $org_name
    Write-Log "UCS: Configuring IP Pools."
    foreach ($vlan in $vlans) {
        if ($vlan.type -eq "ooband") {
            $gateway = $vlan.gateway
            $netmask = $vlan.netmask
            $pool_name = "ooband"
            $ips = $vlan.pool.Split("-")
            if (!($ip_pools | Where-Object {$_.Name -eq $pool_name})) {
                Write-Log "UCS: Creating IP Pool: '$pool_name'."
                Start-UcsTransaction
                $pool = Add-UcsIpPool -Org $org_name -Name $pool_name -ModifyPresent -AssignmentOrder "sequential"
                $pool | Add-UcsIpPoolBlock -From $ips[0] -To $ips[1] -ModifyPresent | Out-Null
                Complete-UcsTransaction -Force | Out-Null
            } else { Write-Log "UCS: IP Pool: '$pool_name' already exists." }
        }
    }
    Write-Log "UCS: Completed IP Pool Configuration."
    Write-Log ""
    ########################################
    # MAC POOLS
    ########################################
    $fabrics = @("A", "B")
    $pool_identifier = $ydata.domain.pool_identifier
    $vnics = $ydata.domain.template.vnics
    $vnic_count = 0
    $mac_pools = Get-UcsMacPool -Org $org_name
    Write-Log "UCS: Configuring MAC Pools."
    foreach ($vnic in $vnics) {
        $mac = "00:25:B5:$($pool_identifier):$($vnic_count)#:"
        foreach ($fabric in $fabrics) {
            $pool_name = "$($vnic.name)-$($fabric.ToLower())"
            if (!($mac_pools | Where-Object {$_.Name -eq $pool_name})) {
                $from = $mac.Replace("#", $fabric) + "00"
                $to   = $mac.Replace("#", $fabric) + "FF"
                Write-Log "UCS: Creating MAC Pool: '$pool_name'."
                Start-UcsTransaction
                $pool = Add-UcsMacPool -Org $org_name -Name $pool_name -ModifyPresent -AssignmentOrder "sequential"
                $pool | Add-UcsMacMemberBlock -From $from -To $to -ModifyPresent | Out-Null
                Complete-UcsTransaction -Force | Out-Null
            } else { Write-Log "UCS: MAC Pool: '$pool_name' already exists." }
        }
        $vnic_count ++
    }
    Write-Log "UCS: Completed MAC Pool Configuration."
    Write-Log ""
    ########################################
    # UUID POOLS
    ########################################
    Write-Log "UCS: Configuring UUID Pool."
    $uuid_pools = Get-UcsUuidSuffixPool -Org $org_name
    $prefix = "0025B500-$($pool_identifier)$($pool_identifier)-$($pool_identifier)$($pool_identifier)"
    $from = "0000-000000000001"
    $to   = "0000-000000000256"
    $pool_name = "uuid"
    if (!($uuid_pools | Where-Object {$_.Name -eq $pool_name})) {
        Write-Log "UCS: Creating UUID Pool: '$pool_name'."
        Start-UcsTransaction
        $pool = Add-UcsUuidSuffixPool -Org $org_name -Name $pool_name -Prefix $prefix -ModifyPresent -AssignmentOrder "sequential"
        $pool | Add-UcsUuidSuffixBlock -From $from -To $to -ModifyPresent | Out-Null
        Complete-UcsTransaction -Force | Out-Null
    } else { Write-Log "UCS: UUID Pool: '$pool_name' already exists." }
    Write-Log "UCS: Completed UUID Pool Configuration."
    Write-Log ""
    ########################################
    # WWXN POOLS
    ########################################
    $configure_vsan = $False
    if ($ydata.domain.vsans) { if ($ydata.domain.vsans.Count -eq 2) { $configure_vsan = $True } }
    if ($configure_vsan -eq $True) {
        Write-Log "UCS: Configuring WWXN Pools."
        $wwxn_pools = Get-UcsWwnPool -Org $org_name
        $wwn = "20:00:00:25:B5:$($pool_identifier):0#:"
        $pool_name = "wwnn"
        if (!($wwxn_pools | Where-Object {$_.Name -eq $pool_name -and $_.Purpose -eq "node-wwn-assignment"})) {
            $from = $wwn.Replace("#", "0") + "00"
            $to   = $wwn.Replace("#", "0") + "FF"
            Write-Log "UCS: Creating WWNN Pool: '$pool_name'."
            Start-UcsTransaction
            $pool = Add-UcsWwnPool -Org $org_name -Name $pool_name -Purpose "node-wwn-assignment" -ModifyPresent -AssignmentOrder "sequential"
            $pool | Add-UcsWwnMemberBlock -From $from -To $to -ModifyPresent | Out-Null
            Complete-UcsTransaction -Force | Out-Null
        } else { Write-Log "UCS: WWNN Pool: '$pool_name' already exists." }
        foreach ($fabric in $fabrics) {
            $pool_name = "vhba-$($fabric.ToLower())"
            if (!($wwxn_pools | Where-Object {$_.Name -eq $pool_name -and $_.Purpose -eq "port-wwn-assignment"})) {
                $from  = $wwn.Replace("#", $fabric) + "00"
                $to   = $wwn.Replace("#", $fabric) + "FF"
                Write-Log "UCS: Creating WWPN Pool: '$pool_name'."
                Start-UcsTransaction
                $pool = Add-UcsWwnPool -Org $org_name -Name $pool_name  -Purpose "port-wwn-assignment" -ModifyPresent
                $pool | Add-UcsWwnMemberBlock -From $from -To $to -ModifyPresent | Out-Null
                Complete-UcsTransaction -Force | Out-Null
            } else { Write-Log "UCS: WWPN Pool: '$pool_name' already exists." }
        }
        Write-Log "UCS: Completed WWXN Pool Configuration."
        Write-Log ""
    }
    ########################################
    # BIOS
    ########################################
    ${policy_name} = "$($name_prefix)M5-intel-virtual"
    ${policy_descr} = "Recommended BIOS Policy for M5 Servers"
    Write-Log "UCS: Configuring Bios Policy: '$(${policy_name})'"
    Start-UcsTransaction
    $mo = Get-UcsOrg -Level root | Get-UcsOrg -Name $org_name -LimitScope | Add-UcsBiosPolicy -Name ${policy_name} -Descr ${policy_descr} -PolicyOwner "local" -RebootOnUpdate "yes" -ModifyPresent
    $mo | Set-UcsBiosVfAltitude -VpAltitude "auto" | Out-Null
    $mo | Set-UcsBiosVfConsoleRedirection -VpConsoleRedirection "serial-port-a" | Out-Null
    $mo | Set-UcsBiosVfCPUPerformance -VpCPUPerformance "hpc" | Out-Null
    $mo | Set-UcsBiosVfDirectCacheAccess -VpDirectCacheAccess "enabled" | Out-Null
    $mo | Set-UcsBiosVfIntelTrustedExecutionTechnology -VpIntelTrustedExecutionTechnologySupport "enabled" | Out-Null
    $mo | Set-UcsBiosVfIntelVirtualizationTechnology -VpIntelVirtualizationTechnology "enabled" | Out-Null
    $mo | Set-UcsBiosIntelDirectedIO -VpIntelVTDCoherencySupport "disabled" -VpIntelVTDInterruptRemapping "enabled" -VpIntelVTForDirectedIO "enabled" | Out-Null
    $mo | Set-UcsBiosVfMemoryMappedIOAbove4GB -VpMemoryMappedIOAbove4GB "enabled" | Out-Null
    $mo | Set-UcsBiosVfOutOfBandManagement -VpComSpcrEnable "enabled" | Out-Null
    $mo | Set-UcsBiosVfProcessorCState -VpProcessorCState "disabled" | Out-Null
    $mo | Set-UcsBiosVfProcessorC1E -VpProcessorC1E "disabled" | Out-Null
    $mo | Set-UcsBiosVfProcessorC3Report -VpProcessorC3Report "disabled" | Out-Null
    $mo | Set-UcsBiosVfProcessorC6Report -VpProcessorC6Report "disabled" | Out-Null
    $mo | Set-UcsBiosVfProcessorC7Report -VpProcessorC7Report "disabled" | Out-Null
    $mo | Set-UcsBiosVfProcessorEnergyConfiguration -VpEnergyPerformance "performance" -VpPowerTechnology "performance" | Out-Null
    $mo | Set-UcsBiosVfSerialPortAEnable -VpSerialPortAEnable "enabled" | Out-Null
    $mo | Set-UcsBiosVfTrustedPlatformModule -VpTrustedPlatformModuleSupport "enabled" | Out-Null
    Complete-UcsTransaction -Force | Out-Null
    ########################################
    # Boot Order
    ########################################
    ${policy_name} = "$($name_prefix)m2pch-legacy"
    ${policy_descr} = "Recommended Boot Policy for servers with M.2 PCH Controller - Legacy Mode"
    Write-Log "UCS: Configuring Boot Policy: '$(${policy_name})'"
    $mo = Add-UcsBootPolicy -Org $org_name -Name ${policy_name} -Descr ${policy_descr} -BootMode "legacy" -EnforceVnicName "yes" -PolicyOwner "local" -RebootOnUpdate "no" -ModifyPresent | Out-Null
    Start-UcsTransaction
    $mo | Add-UcsLsbootVirtualMedia -ModifyPresent -Access "read-only" -LunId "unspecified" -MappingName "" -Order 1 | Out-Null
    $mo | Add-UcsLsbootVirtualMedia -ModifyPresent -Access "read-only-remote-cimc" -LunId "unspecified" -MappingName "" -Order 2
    $mo | Add-UcsLsbootUsbFlashStorageImage -ModifyPresent -Order 4 | Out-Null
    $m2 = $mo | Add-UcsLsbootStorage -ModifyPresent -Order 3
    $m3 = $m2 | Add-UcsLsbootLocalStorage -ModifyPresent
    $m4 = $m3 | Add-UcsLsbootEmbeddedLocalDiskImage -ModifyPresent -Order 3
    $m4 | Add-UcsLsbootUEFIBootParam -ModifyPresent -BootDescription "ESXi Boot Loader" -BootLoaderName "BOOTx64.EFI" -BootLoaderPath "\EFI\BOOT\" | Out-Null
    #${policy_name} = "$($name_prefix)m2pch"
    #${policy_descr} = "Recommended Boot Policy for servers with M.2 PCH Controller"
    #Write-Log "UCS: Configuring Boot Policy: '$(${policy_name})'"
    #$mo = Add-UcsBootPolicy -Org $org_name -Name ${policy_name} -Descr ${policy_descr} -BootMode "uefi" -EnforceVnicName "yes" -PolicyOwner "local" -RebootOnUpdate "yes" -ModifyPresent | Out-Null
    #Start-UcsTransaction
    #$mo = Get-UcsBootPolicy -Org $org_name -Name ${policy_name}
    #$mo | Add-UcsLsbootBootSecurity -ModifyPresent -SecureBoot "yes" | Out-Null
    #$mo | Add-UcsLsbootVirtualMedia -ModifyPresent -Access "read-only" -LunId "unspecified" -MappingName "" -Order 1 | Out-Null
    #$mo | Add-UcsLsbootVirtualMedia -ModifyPresent -Access "read-only-remote-cimc" -LunId "unspecified" -MappingName "" -Order 2
    #$mo | Add-UcsLsbootEFIShell -ModifyPresent -Order 4 | Out-Null
    #$m2 = $mo | Add-UcsLsbootStorage -ModifyPresent -Order 3
    #$m3 = $m2 | Add-UcsLsbootLocalStorage -ModifyPresent
    #$m4 = $m3 | Add-UcsLsbootEmbeddedLocalDiskImage -ModifyPresent -Order 3
    #$m4 | Add-UcsLsbootUEFIBootParam -ModifyPresent -BootDescription "ESXi Boot Loader" -BootLoaderName "BOOTx64.EFI" -BootLoaderPath "\EFI\BOOT\" | Out-Null
    Complete-UcsTransaction -Force | Out-Null
    ########################################
    # Ethernet Adapter
    ########################################
    ${policy_name} = "$($name_prefix)vmware"
    ${policy_descr} = "Recommended Ethernet Adapter Policy for VMware Servers"
    Write-Log "UCS: Configuring Ethernet Adapter Policy: '$(${policy_name})'"
    Start-UcsTransaction
    $mo = Add-UcsEthAdapterPolicy -Org $org_name -Name ${policy_name} -Descr ${policy_descr} -ModifyPresent -PolicyOwner "local" -PooledResources "disabled" | Out-Null
    $mo | Set-UcsAdaptorAzureQosProfile -AdpAzureQos "disabled" | Out-Null
    $mo | Add-UcsAdaptorEthAdvFilterProfile -ModifyPresent -AdminState "disabled" | Out-Null
    $mo | Set-UcsAdaptorEthArfsProfile -AccelaratedRFS "disabled" | Out-Null
    $mo | Set-UcsAdaptorEthCompQueueProfile -Count 5 | Out-Null
    $mo | Set-UcsEthAdapterFailoverProfile -Timeout 60 | Out-Null
    $mo | Set-UcsAdaptorEthGENEVEProfile -Offload "disabled" | Out-Null
    $mo | Set-UcsEthAdapterInterruptProfile -CoalescingTime 125 -CoalescingType "min" -Count 8 -Mode "msi-x" | Out-Null
    $mo | Add-UcsAdaptorEthInterruptScalingProfile -ModifyPresent -AdminState "disabled" | Out-Null
    $mo | Set-UcsAdaptorEthNVGREProfile -AdminState "disabled" | Out-Null
    $mo | Set-UcsEthAdapterOffloadProfile -LargeReceive "enabled" -TcpRxChecksum "enabled" -TcpSegment "enabled" -TcpTxChecksum "enabled" | Out-Null
    $mo | Set-UcsEthAdapterReceiveQueueProfile -Count 4 -RingSize 4096 | Out-Null
    $mo | Set-UcsAdaptorEthRoCEProfile -AdminState "disabled" -Cos "platinum" -MemoryRegions 131072 -Prio "best-effort" -QueuePairs 256 -ResourceGroups 4 -V1 "disabled" -V2 "disabled" | Out-Null
    $mo | Set-UcsAdaptorEthVxLANProfile -AdminState "disabled" | Out-Null
    $mo | Set-UcsEthAdapterTransmitQueueProfile -Count 1 -RingSize 256 | Out-Null
    $mo | Set-UcsAdaptorPTP -AdminState "disabled" | Out-Null
    $mo | Set-UcsEthAdapterRssProfile -ReceiveSideScaling "enabled" | Out-Null
    Complete-UcsTransaction -Force | Out-Null
    ########################################
    # Network Control
    ########################################
    ${policy_name} = "$($name_prefix)both"
    ${policy_descr} = "Recommended Network Control Policy for Servers"
    Write-Log "UCS: Configuring Network Control Policy: '$(${policy_name})'"
    Start-UcsTransaction
    $mo = Add-UcsNetworkControlPolicy -Org $org_name -Name ${policy_name} -Descr ${policy_descr} -ModifyPresent -PolicyOwner "local" -Cdp "enabled" -LldpReceive "enabled" -LldpTransmit "enabled" -MacRegisterMode "only-native-vlan" | Out-Null
    $mo | Add-UcsPortSecurityConfig -ModifyPresent -Descr "" -Forge "allow" -Name "" -PolicyOwner "local" | Out-Null
    Complete-UcsTransaction -Force | Out-Null
    ########################################
    # Host Firmware Packages
    ########################################
    ${version} = $ydata.upgrade.fw_version
    ${policy_name} = "$($name_prefix)M5"
    ${policy_descr} = "Recommended Host Firmware Policy for M5 Servers"
    Write-Log "UCS: Configuring Host Firmware Policy: '$(${policy_name})'"
    Start-UcsTransaction
    $mo = Add-UcsFirmwareComputeHostPack -Org $org_name -Name ${policy_name} -Descr ${policy_descr} -ModifyPresent -PolicyOwner "local" -BladeBundleVersion ${infraVersionB} -IgnoreCompCheck "yes" -Mode "staged" -OverrideDefaultExclusion "yes" -RackBundleVersion ${infraVersionC} -ServicePackBundleVersion "" -StageSize 0 -UpdateTrigger "immediate" | Out-Null
    Complete-UcsTransaction -Force | Out-Null
    ########################################
    # Local Disk
    ########################################
    ${policy_name} = "$($name_prefix)flex-disabled"
    ${policy_descr} = "Local Disk Policy - Flex Disabled for Servers"
    Write-Log "UCS: Configuring Local Disk Policy: '$(${policy_name})'"
    Start-UcsTransaction
    $mo = Add-UcsLocalDiskConfigPolicy -Org $org_name -Name ${policy_name} -Descr ${policy_descr} -ModifyPresent -PolicyOwner "local" -FlexFlashRAIDReportingState "disable" -FlexFlashRemovableState "no-change" -FlexFlashState "disable" -Mode "any-configuration" -ProtectConfig "yes" | Out-Null
    Complete-UcsTransaction -Force | Out-Null
    ########################################
    # Maintenance
    ########################################
    ${policy_name} = "$($name_prefix)ack-on-reboot"
    ${policy_descr} = "Recommended Maintenance Policy for Servers"
    Write-Log "UCS: Configuring Maintenance Policy: '$(${policy_name})'"
    Start-UcsTransaction
    $mo = Add-UcsMaintenancePolicy -Org $org_name -Name ${policy_name} -Descr ${policy_descr} -ModifyPresent -PolicyOwner "local" -DataDisr "user-ack" -SchedName "" -SoftShutdownTimer "150-secs" -TriggerConfig "on-next-boot" -UptimeDisr "user-ack" | Out-Null
    Complete-UcsTransaction -Force | Out-Null
    ########################################
    # Placement
    ########################################
    ${policy_name} = "$($name_prefix)placement"
    ${policy_descr} = "Recommended Placement Policy for vNICs"
    Write-Log "UCS: Configuring Placement Policy: '$(${policy_name})'"
    Start-UcsTransaction
    $mo = Add-UcsPlacementPolicy -Org $org_name -Name ${policy_name} -Descr ${policy_descr} -ModifyPresent -PolicyOwner "local" -MezzMapping "round-robin" | Out-Null
    Complete-UcsTransaction -Force | Out-Null
    ########################################
    # Power
    ########################################
    ${policy_name} = "$($name_prefix)server"
    ${policy_descr} = "Recommended Power Policy for Servers"
    Write-Log "UCS: Configuring Power Policy: '$(${policy_name})'"
    Start-UcsTransaction
    $mo = Add-UcsPowerPolicy -Org $org_name -Name ${policy_name} -Descr ${policy_descr} -ModifyPresent -PolicyOwner "local" -AggressiveCooling "Disable" -FanSpeed "any" -Prio "no-cap" | Out-Null
    Complete-UcsTransaction -Force | Out-Null
    ########################################
    # QoS
    ########################################
    $qos_priorities = @("Best-Effort", "Bronze", "Gold", "Platinum", "Silver")
    foreach ($priority in $qos_priorities) {
        $pname = $priority.Replace("-", " ")
        $p = $priority.ToLower()
        ${policy_name} = "$($name_prefix)$($p)"
        ${policy_descr} = "$($pname) QoS Policy"
        Write-Log "UCS: Configuring QoS Policy: '$(${policy_name})'"
        Start-UcsTransaction
        $mo = Add-UcsQosPolicy -Org $org_name -Name ${policy_name} -Descr ${policy_descr} -ModifyPresent -PolicyOwner "local" | Out-Null
        $mo | Add-UcsVnicEgressPolicy -ModifyPresent -Burst 10240 -HostControl "none" -Name "" -Prio $p -Rate "line-rate" | Out-Null
        Complete-UcsTransaction -Force | Out-Null
    }
    ########################################
    # Serial over LAN
    ########################################
    ${policy_name} = "$($name_prefix)sol"
    ${policy_descr} = "Recommended Serial over LAN Policy for Servers"
    Write-Log "UCS: Configuring Serial over LAN Policy: '$(${policy_name})'"
    Start-UcsTransaction
    $mo = Add-UcsSolPolicy -Org $org_name -Name ${policy_name} -Descr ${policy_descr} -ModifyPresent -PolicyOwner "local" -AdminState "enable" -Speed "115200" | Out-Null
    Complete-UcsTransaction -Force | Out-Null
    ########################################
    # Virtual Media
    ########################################
    ${policy_name} = "$($name_prefix)vmedia"
    ${policy_descr} = "Recommended Virtual Media Policy for Servers"
    Write-Log "UCS: Configuring Virtual Media Policy: '$(${policy_name})'"
    Start-UcsTransaction
    $mo = Add-UcsVmediaPolicy -Org $org_name -Name ${policy_name} -Descr ${policy_descr} -ModifyPresent -PolicyOwner "local" -RetryOnMountFail "yes" | Out-Null
    Complete-UcsTransaction -Force | Out-Null
    Write-Log ""
    ########################################
    # VLANs
    ########################################
    Write-Log "UCS: Configuring VLANs."
    $ucs_vlans = Get-UcsVlan -cloud ethlan
    foreach ($vlan in $vlans) {
        if (!($vlan.type -eq "ooband")) {
            $id = [convert]::ToInt32($vlan.vlan_id, 10)
            if (!($ucs_vlans | Where-Object {$_.Id -eq $vlan.vlan_id -and $_.Name -eq $vlan.name})) {
                Write-Log "UCS: Creating VLAN Name $($vlan.name) with Id $($id)."
                Start-UcsTransaction
                $mo = Get-UcsLanCloud | Add-UcsVlan -ModifyPresent -Id $id -Name $vlan.name -PolicyOwner "local" | Out-Null
                Complete-UcsTransaction | Out-Null
            } else {
                Write-Log "UCS: VLAN Name $($vlan.name) with Id $($id) already exists."
            }
        }
    }
    Write-Log "UCS: Completed VLANs Configuration."
    Write-Log ""
    ########################################
    # VLAN Groups
    ########################################
    Write-Log "UCS: Configuring VLAN Groups."
    #$vlan_groups = Get-UcsFabricNetGroup
    foreach ($vnic in $vnics) {
        $vlan_members = @()
        $native_set = $False
        $native_vlan = ""
        $func_intf = $False
        if ("management" -in $vnic.data_types) {
            foreach ($vlan in $vlans) { if ($vlan.type -eq "management") { $vlan_name = $vlan.name } }
            $desc = "Management Vlan Group"
            $native_vlan = $vlan_name
            $vlan_members += $vlan_name
            $native_set = $True
            $func_intf = $True
        } 
        if ("migration" -in $vnic.data_types) {
            foreach ($vlan in $vlans) { if ($vlan.type -eq "migration") { $vlan_name = $vlan.name } }
            $vlan_members += $vlan_name
            $func_intf = $True
            if ($native_set -eq $False) {
                $desc = "Migration Vlan Group"
                $native_vlan = $vlan_name
                $native_set = $True
            }
        } 
        if ("storage" -in $vnic.data_types) {
            foreach ($vlan in $vlans) { if ($vlan.type -eq "storage") { $vlan_name = $vlan.name } }
            $vlan_members += $vlan_name
            $func_intf = $True
            if ($native_set -eq $False) {
                $desc = "Storage Vlan Group"
                $native_vlan = $vlan_name
                $native_set = $True
            }
        } 
        if ($func_intf -eq $False) {
            $desc = "Virtual Machine Vlan Group"
            foreach ($vlan in $vlans) {
                if (!($vlan.type -match "(management|migration|ooband|storage)")) {
                    $vlan_members += $vlan.name
                }
            }
        }
        Write-Log "UCS: Configuring VLAN Group '$($vnic.name)'."
        Start-UcsTransaction
        $mo = Get-UcsLanCloud | Add-UcsFabricNetGroup -ModifyPresent  -Descr $desc -Name $vnic.name -NativeNet $native_vlan -PolicyOwner "local" -Type "mgmt"
        foreach ($member in $vlan_members ) { $mo | Add-UcsFabricPooledVlan -ModifyPresent -Name $member | Out-Null }
        Complete-UcsTransaction | Out-Null
    }
    Write-Log "UCS: Completed VLAN Groups Configuration."
    Write-Log ""
   ########################################
    # VSANs
    ########################################
    if ($configure_vsan -eq $True) {
        Write-Log "UCS: Configuring VSANs."
        $vsans = $ydata.domain.vsans
        $vcount = 0
        $ucs_vsans = Get-UcsVSan
        foreach ($fabric in $fabrics) {
            $id = [convert]::ToInt32($vsans[$vcount], 10)
            $vname = "vsan-$($fabric.ToLower())"
            if (!($ucs_vsans | Where-Object {$_.Id -eq $id -and $_.Name -eq $vname -and $_.SwitchId -eq $fabric})) {
                Write-Log "UCS: Creating VSAN Name $($vname) with Id $($id)."
                Start-UcsTransaction
                $mo = Get-UcsSanCloud | Add-UcsVSan -ModifyPresent -FcoeVlan $id -Id $id -Name $vname -SwitchId $fabric -PolicyOwner "local" | Out-Null
                Complete-UcsTransaction | Out-Null
            } else { Write-Log "UCS: VSAN Name $($vname) with Id $($id) already exists." }
            $vcount ++
        }
        Write-Log "UCS: Completed VSANs Configuration."
        Write-Log ""
    }
    ########################################
    # LAN Connectivity & vNIC Templates
    ########################################
    Write-Log "UCS: Configuring LAN Connectivity and vNIC Templates."
    ${policy_name} = "$($name_prefix)lcp"
    ${policy_descr} = "Recommended LAN Connectivity Policy for Servers"
    Write-Log "UCS: Configuring LAN Connectivity Policy: '$(${policy_name})'"
    Start-UcsTransaction
    $mo = Add-UcsVnicLanConnPolicy -ModifyPresent -Org $org_name -Descr ${policy_descr} -Name ${policy_name} -PolicyOwner "local" | Out-Null
    Complete-UcsTransaction -Force | Out-Null
    $lcp = Get-UcsVnicLanConnPolicy -Org $org_name -Name ${policy_name}
    $pci_order = 0
    if ($ydata.domain.template.jumbo -eq $True) { $mtu = 9000 } else { $mtu = 1500 }
    foreach ($vnic in $vnics) {
        foreach ($fabric in $fabrics) {
            $name  = "$($vnic.name)-$($fabric.ToLower())"
            $descr = "$($name) vNIC Template"
            Write-Log "UCS: Configuring vNIC Template $($name)."
            Start-UcsTransaction
            if ($fabric -eq "A") {
                $peer = "$($vnic.name)-b"
                $redundancy = "primary"
                $mo = Add-UcsVnicTemplate -Org $org_name -ModifyPresent -Descr $descr -AdminCdnName "" -CdnSource "vnic-name" -IdentPoolName $name -Mtu $mtu -Name $name -NwCtrlPolicyName "$($name_prefix)both" -PeerRedundancyTemplName $peer -PinToGroupName "" -PolicyOwner "local" -QosPolicyName "$($name_prefix)best-effort" -RedundancyPairType $redundancy -StatsPolicyName "default" -SwitchId $fabric -Target "adaptor" -TemplType "updating-template" -XtraProperty @{QInQ="disabled"; } | Out-Null
            } else {
                $peer = "$($vnic.name)-a"
                $redundancy = "secondary"
                $mo = Add-UcsVnicTemplate -Org $org_name -ModifyPresent -Descr $descr -AdminCdnName "" -CdnSource "vnic-name" -IdentPoolName $name -Mtu $mtu -Name $name -PeerRedundancyTemplName $peer -PinToGroupName "" -PolicyOwner "local" -RedundancyPairType $redundancy -SwitchId $fabric -Target "adaptor" -XtraProperty @{QInQ="disabled"; } | Out-Null
            }
            $mo |  Add-UcsFabricNetGroupRef -ModifyPresent -Name $vnic.name
            $lcp | Add-UcsVnic -ModifyPresent -AdaptorProfileName "$($name_prefix)vmware" -Name $name -NwTemplName $name -Order "$($pci_order)" | Out-Null
            Complete-UcsTransaction | Out-Null
            $pci_order ++
        }
    }
    Write-Log "UCS: Completed vNIC Template Configuration."
    Write-Log ""
    ########################################
    # SAN Connectivity & vHBA Templates
    ########################################
    if ($configure_vsan -eq $True) {
        Write-Log "UCS: Configuring SAN Connectivity and vHBA Templates."
        ${policy_name} = "$($name_prefix)scp"
        ${policy_descr} = "Recommended SAN Connectivity Policy for Servers"
        Write-Log "UCS: Configuring SAN Connectivity Policy: '$(${policy_name})'"
        Start-UcsTransaction
        $mo = Add-UcsVnicSanConnPolicy -ModifyPresent -Org $org_name -Descr ${policy_descr} -Name ${policy_name} -PolicyOwner "local"
        $mo | Add-UcsVnicFcNode -ModifyPresent -Addr "pool-derived" -IdentPoolName "wwnn" | Out-Null
        Complete-UcsTransaction -Force | Out-Null
        $scp = Get-UcsVnicSanConnPolicy -Org $org_name -Name ${policy_name}
        foreach ($fabric in $fabrics) {
            $name  = "vhba-$($fabric.ToLower())"
            $descr = "$($name) vHBA Template Fabric $($fabric)"
            Write-Log "UCS: Configuring vHBA Template $($name)."
            Start-UcsTransaction
            Write-Host "Here 1"
            $vhba = Add-UcsVhbaTemplate -Org $org_name -ModifyPresent -Descr $descr -IdentPoolName $name -Name $name -PinToGroupName "" -PolicyOwner "local" -QosPolicyName "" -RedundancyPairType "none" -StatsPolicyName "default" -SwitchId $fabric -TemplType "updating-template"
            $vhba | Add-UcsVhbaInterface -ModifyPresent -Name $name | Out-Null
            Write-Host "Here 2"
            $scp | Add-UcsVhba -ModifyPresent -AdaptorProfileName "" -Name $name -NwTemplName $name -Order "$($pci_order)" | Out-Null
            Complete-UcsTransaction | Out-Null
            $pci_order ++
        }
        Write-Log "UCS: Completed vHBA Template Configuration."
        Write-Log ""
    }
    ########################################
    # Service Profile Template
    ########################################
    # Create Service Profile Template (using MAC, WWPN, Server Pools, VLANs, VSans, Boot Policy, etc. previously created steps) with desired power state to down
    Write-Log "UCS: Creating SP Template: 'Nutanix-SP-Template' in UCS org: $org_name"
    Start-UcsTransaction
    ${template_name} = "Nutanix-M5-m2pch"
    ${descr} = "Nutanix M5 M2PCH Service Profile Template"
    $np = $name_prefix
    Add-UcsServiceProfile -ModifyPresent -Org $org_name -Name ${template_name} -AgentPolicyName "" -BiosProfileName "$($np)M5-intel-virtual" -BootPolicyName "$($np)m2pch" -Descr ${descr} -DynamicConPolicyName "" -ExtIPPoolName "ooband" -ExtIPState "pooled" -GraphicsCardPolicyName "" -HostFwPolicyName "$($np)M5" -IdentPoolName "uuid" -KvmMgmtPolicyName "default" -LocalDiskPolicyName "$($np)flex-disabled" -MaintPolicyName "$($np)ack-on-reboot" -MgmtAccessPolicyName "" -MgmtFwPolicyName "" -PersistentMemoryPolicyName "" -PolicyOwner "local" -PowerPolicyName "$($np)server" -PowerSyncPolicyName "default" -SolPolicyName "$($np)sol" -StatsPolicyName "default" -Type "updating-template" -VconProfileName "$($name_prefix)placement" -VmediaPolicyName "$($name_prefix)vmedia" | Out-Null
    $sp_template = Get-UcsServiceProfile -Org $org_name -Name ${template_name}
    $sp_template | Add-UcsVnicConnDef -ModifyPresent -LanConnPolicyName "lcp" -SanConnPolicyName "scp" | Out-Null
    Complete-UcsTransaction
    ########################################
    # Service Profiles
    ########################################
    $sp_prefix = $ydata.domain.profiles.name_prefix
    $suffix_length   = $ydata.domain.profiles.suffix_length
    $suffix_start    = $ydata.domain.profiles.suffix_start
    $server_profiles = $ydata.domain.profiles.servers
    $existing_sp = Get-UcsServiceProfile -Org $org_name
    $suffix = "0" * $suffix_length
    foreach ($sp in $server_profiles) {
        $server = Get-UcsRackUnit -Serial $sp.serial
        $mgmt_ctrl = $server | Get-UcsMgmtController
        if (!($mgmt_ctrl | Get-UcsVnicIpV4StaticAddr)) {
            $mgmt_ctrl | Add-UcsVnicIpV4StaticAddr -ModifyPresent -Addr $sp.ip -DefGw $gateway -Subnet $netmask -PrimDns $dns_servers[0] -SecDns $secondary -Force | Out-Null
        } else {
            $mgmt_ctrl | Get-UcsVnicIpV4StaticAddr | Set-UcsVnicIpV4StaticAddr -Addr $sp.ip -DefGw $gateway -Subnet $netmask -PrimDns $dns_servers[0] -SecDns $secondary -Force | Out-Null
        }
        $replace = "0" * $suffix_start.Length
        $name = $sp_prefix + $suffix.Replace($replace, $suffix_start)
        Write-Log "UCS: Configuring Service Profile '$name' from SP Template: $(${sp_template})"
        $server = Get-UcsRackUnit -Serial $sp.serial
        if (!($existing_sp | Where-Object {$_.Name -eq $name})) {
            $mo = Add-UcsServiceProfile -Org $org_name -Name $name -SrcTemplName $sp_template.Name
        }
        $service_profile = Get-UcsServiceProfile -Org $org_name -Name $name
        if (!($service_profile.PnDn -eq $server.Dn)) {
            if (!("" -eq $server.AssignedToDn)) {
                Disconnect-UcsServiceProfile -ServiceProfile $server.AssignedToDn -Server $server | Out-Null
            }
            Connect-UcsServiceProfile -ServiceProfile $service_profile -RackUnit $server -Force | Out-Null
        }
        $suffix_start ++
    }
    foreach ($sp in $server_profiles) {
        # Monitor UCS SP Associate for completion
        $server_profile = Get-UcsServiceProfile -Dn (Get-UcsRackUnit -Serial $sp.serial).AssignedToDn
        Write-Host "UCS: Waiting for UCS SP: $($server_profile.name) to complete SP association process"
            do {
                if ( (Get-UcsManagedObject -Dn $server_profile.Dn).AssocState -ieq "associated") { break }
                Start-Sleep 40
            } until ((Get-UcsManagedObject -Dn $server_profile.Dn).AssocState -ieq "associated")
    }
            
    # Logout of UCS
    Write-Host "UCS: Logging out of UCS: $ucs"
    Disconnect-Ucs -ErrorAction Ignore | Out-Null

} Catch {
     Write-Log "Error occurred in script:"
     Write-Log ${Error}
     Disconnect-Ucs -ErrorAction Ignore | Out-Null
     Exit 1
}
Exit 0