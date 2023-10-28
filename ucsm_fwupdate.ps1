<#

.SYNOPSIS
                This script automates the upgrade of UCS firmware

.DESCRIPTION
                This script logs into Cisco.com, download firmware bundles to a local working directory, upload bundles to the target UCS domain and walk through all steps of the upgrade

.PARAMETERSET
                hfp: To upgrade all components infra as well as servers
                infraOnly: To upgrade only infra component

.EXAMPLE
                ucsm_fwupdate.ps1 -y ucsm_fwupdate.yaml
                Upgrades all components of UCS
                -ucs -- UCS Manager IP -- Example: "1.2.3.4"
                -version -- UCS Manager version to upgrade
                -imagedir -- Path to download firmware bundle
                -hfp -- Firmware Host Pack. Values can be "all" or "default"
                All parameters are mandatory
                The prompts that will always be presented to the user will be for Username and Password for UCS and for cisco software image download


.EXAMPLE
                UCSMFirmwareUpdate.ps1 -ucs xx.xx.xx.xx -version 'x.x(xx)' -imagedir c:\work\images -infraOnly
                Upgrade Infrastructure only portion of UCSM
                -infraOnly -- Optional SwitchParameter when specified upgrades Infrastructure only

.NOTES
                Author: Eric Williams
                Email: ericwill@cisco.com
                Company: Cisco Systems, Inc.
                Version: v1.1
                Date: 06/05/2014
                Disclaimer: Code provided as-is.  No warranty implied or included.  This code is for example use only and not for production

.INPUTS
                UCSM IP Address
                UCS Manager version to upgrade
                Directory path to download firmware image bundles
                Switch Parameter to upgrade infrastructure only portion
                HFP Parameter specifies which HFP to be upgraded

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
    Write-Error $Message -ForegroundColor Red
    Disconnect-Ucs -ErrorAction Ignore | Out-Null
    Disconnect-VIServer -ErrorAction Ignore | Out-Null
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

function Connect-vCenter {
    # IP address and credentials to access the management server software that manages
    # firmware updates for the nodes of the solution.
    $vcenterConn = Connect-VIServer -Server ${vcenter} -Credential ${vcenterCred} -ErrorVariable errVar -ErrorAction SilentlyContinue
    if ($errVar) {
        Write-Log "Error attempting to connect to vCenter at $(${vcenter}). Details: $errVar"
        return $null
    } else {
        Write-Log "Connected to vCenter $(${vcenter})"
        return $vcenterConn
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

function Wait-UcsServersActivation {
    #Sleep for 15 seconds so that all the servers comes in upgrading state
    Start-Sleep -Seconds 15
    $count = 0

    #get all servers for which firmware status is not ready and not in error or faulty state.
    $moNotInReadyState = ${ServerProfileFwList} | ForEach-Object {Get-UcsFirmwareStatus -Dn $_ -Filter 'OperState -cne ready -and (OperState -cne "bad-image" -and OperState -cne failed -and OperState -cne "faulty-state")'}
    #$moNotInReadyState = Get-UcsServer | Get-UcsFirmwareStatus -Filter 'OperState -cne ready -and (OperState -cne "bad-image" -and OperState -cne failed -and OperState -cne "faulty-state")' | Get-UcsParent
    if ($moNotInReadyState.Count -gt 0) {
        Write-Log "Monitoring the state of below servers:"
        foreach ($mo in $moNotInReadyState) { Write-Log $mo.Dn }

        Write-Log "Sleeping for 3 minutes...";
        Start-Sleep -Seconds 180;
        do {
            $count++
            if ($count -eq 40) {
                Write-Log "Error servers activation is still not completed even after 2 hours. Exiting with error now."
                return $false
            }
            try {
                #Logs the operstate of all the servers.
                foreach($mo in ${ServerProfileFwList}) {
                    $tmpOperState = $mo | Get-UcsFirmwareStatus | Select-Object OperState
                    Write-Log "Server firmware activation for server: $($mo.Dn) is in progress: $tmpOperState"
                    if (!($tmpOperState -eq "ready")) {
                        Write-Log "Sleeping for 3 minutes...";
                        Start-Sleep -Seconds 180;
                    }
                }
                #exits from the monitoring if all the servers are in ready state.
                if (($moNotInReadyState | Get-UcsFirmwareStatus | Where-Object {$_.OperState -ne "ready"}).Count -eq 0) {
                    Write-Log "Server firmware activation is done";
                    return $true
                }
            } catch {
                Write-Log "Failed to get the status of the firmware update process. $_.Exception"
                throw $_.Exception
            }
        }
        while ($true)
    } else {
        Write-Log "No servers to Monitor. Please check server firmware status. Servers may be in 'ready', 'bad-image', 'failed' or 'faulty-state'."
    }
    return $true
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
# Begin Module
$module_names = @("Cisco.UcsManager", "Cisco.Ucs.Core", "powershell-yaml", "VMware.PowerCLI", "VMware.Vim")
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
    Write-Host "yaml_file: $y, does not exist.  Validate File and Path are Correct" -ForegroundColor Red
    Exit 1
}
$ydata = Get-Content -Path $y | ConvertFrom-Yaml

# Setup LogFilePath Location
${imageDir} = $ydata.upgrade.image_directory
Set-LogFilePath ${imageDir}


# Script only supports one UCS Domain update at a time
Set-UcsPowerToolConfiguration -SupportMultipleDefaultUcs $false | Out-Null
Set-PowerCLIConfiguration -InvalidCertificateAction Ignore -Confirm:$false | Out-Null

Try {
    ${Error}.Clear()
    # Get Home Path
    ${env_vars} = Get-Childitem -Path Env:* | Sort-Object Name
    $os = (${env_vars} | Where-Object {$_.Name -eq "OS"}).Value
    if ((${env_vars} | Where-Object {$_.Name -eq "OS"}).Value -eq "Windows_NT") {
        $homePath = (${env_vars} | Where-Object {$_.Name -eq "HOMEPATH"}).Value
    } else { $homePath = (${env_vars} | Where-Object {$_.Name -eq "HOME"}).Value }
    # Obtain UCS Manager Credentials
    if (Test-Path -Path "$homePath\ucsmpowercli.Cred") {
        Write-Log "Found Existing Credentials for UCS Manager."
        Write-Log ""
        ${ucsCred} = Import-CliXml -Path "$homePath\ucsmpowercli.Cred"
    } else {
        Write-Log "Enter Credentials of UCS Manager to be upgraded to version: '$($version)'"
        Write-Log ""
        ${ucsCred} = Get-Credential -Message "Enter Credentials of UCS Manager to be upgraded"
        ${ucsCred} | Export-CliXml -Path "$homePath\ucsmpowercli.Cred"
    }
    Write-Log "Logging into UCS Domain: '$(${ucs})'"
    Write-Log ""
    ${ucs} = $ydata.ucs_manager
    $ucsConnection = Connect-UcsManager
    #Setting the DefaultUcs so that we don't need to specify the handle for every method call
    $ExecutionContext.SessionState.PSVariable.Set("DefaultUcs", $ucsConnection)

    if (${Error})  {
        Write-Log "Error creating a session to UCS Manager Domain: '$($ucs)'"
        Write-Log "     Error equals: ${Error}"
        Write-Log "     Exiting"
        Exit 1
    }

    #Check What Generation the UCS FI Is.
    ${fi} = Get-UcsNetworkElement | Select-Object -First 1
    if ($fi.Model -cmatch "^UCS-FI-(?<modelNum>65\d\d).*$") { $FI6500 = $true
    } elseif ($fi.Model -cmatch "^UCS-FI-(?<modelNum>64\d\d).*$") { $FI6400 = $true
    } elseif ($fi.Model -cmatch "^UCS-FI-M-(?<modelNum>6324).*$") { $FI6324 = $true
    } elseif ($fi.Model -cmatch "^UCS-FI-(?<modelNum>63\d\d).*$") { $FI6300 = $true
    }

    $version = $ydata.upgrade.fw_version
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

    Write-Log "Starting Firmware download process to local directory: ${imageDir}"
    Write-Log ""

    if ($os -eq "Windows_NT") { $path_sep = "\"
    } else { $path_sep = "/"}
    foreach(${eachBundle} in ${bundle}) {
        ${fileName} = ${imageDir} +  $path_sep + ${eachBundle}
         if( Test-Path -Path ${fileName}) {
              Write-Log "Image File : '${eachBundle}' already exist in local directory: '${imageDir}'"
         } else {
              ${ccoImageList} += ${eachBundle}
         }
    }

    if(${ccoImageList} -ne ${null}) {
        # Obtain CCO Credentials
        if (Test-Path -Path "$homePath\ccopowercli.Cred") {
            Write-Log "Found Existing Credentials for Cisco.com (CCO) Credentials."
            Write-Log ""
            ${ccoCred} = Import-CliXml -Path "$homePath\ccopowercli.Cred"
        } else {
            Write-Log "Enter Cisco.com (CCO) Credentials"
            Write-Log ""
            ${ccoCred} = Get-Credential -Message "Enter Cisco.com (CCO) Credentials"
            ${ccoCred} | Export-CliXml -Path "$homePath\ccopowercli.Cred"
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
            $fileName = ${imageDir} +  "\" + ${image}
            if((Get-UcsFirmwareDownloader -FileName ${image} -TransferState failed).count -ne 0) {
                Write-ErrorLog "Image: '$($image)' already exists under Download Tasks in failed state. Exiting..."
            }
            Write-Log "Uploading image file: '$($image)' to UCS Domain: '$($ucs)'"
            Send-UcsFirmware -LiteralPath $fileName | Watch-Ucs -Property TransferState -SuccessValue downloaded -FailureValue failed -PollSec 30 -TimeoutSec 600 -ErrorAction SilentlyContinue | Out-Null
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

    # Check if the status of the firmware boot unit is ready before proceeding with the firmware update
    if (!(Get-UcsNetworkElement | Get-UcsMgmtController | Get-UcsFirmwareBootDefinition  | Get-UcsFirmwareBootUnit | Where-Object { $_.OperState -eq 'ready'})) {
        Write-ErrorLog "Fabric Interconnect is not in ready state. Can't proceed with Firmware update."
        Disconnect-Ucs
        Exit 1
    }

    # Start the Firmware Auto Install for the Infrastructure update. This will take care of updating the UCS Manager
    # both the Fabric Interconnects.
    $activatedVersion = Get-UcsMgmtController -Subject system | Get-UcsFirmwareRunning -Type system | Select-Object Version

    if ($activatedVersion.Version -ne $version -and $ydata.upgrade.fabric_interconnect -eq $true) {
        Write-Log "Triggering the auto install of the infrastructure firmware  to $aSeriesBundle"
        try {
            Start-UcsTransaction | Out-Null
            Get-UcsOrg -Level root | Get-UcsFirmwareInfraPack -Name "default" -LimitScope | Set-UcsFirmwareInfraPack -ForceDeploy "yes" -InfraBundleVersion ${infraVersionA} -Force | Out-Null
            Get-UcsSchedule -Name "infra-fw" | Get-UcsOnetimeOccurrence -Name "infra-fw" | Set-UcsOnetimeOccurrence -Date (Get-UcsTopSystem).CurrentTime -Force | Out-Null
            Complete-UcsTransaction -ErrorAction Stop | Out-Null
        } catch {
            Write-ErrorLog "Failed to start firmware auto install process. Details: $_.Exception"
        }

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

        if ($activatedVersion.Version -eq $version) {
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
    } else {
        Write-Log "UCS Manager is already at $activatedVersion version. Skipping FI upgrade..."
    }

    #=====================>>>>>>>>>>>Server Firmware Upgrade<<<<<<<<<<================================
    if ($ydata.upgrade.servers -eq $true -or $ydata.upgrade.vum_update -eq $true) {
        $Error.Clear()
        Disconnect-Ucs -ErrorAction Ignore | Out-Null
        $ucsConnection = Connect-UcsManager
        #Setting the DefaultUcs so that we don't need to specify the handle for every method call
        $ExecutionContext.SessionState.PSVariable.Set("DefaultUcs", $ucsConnection)
        # Obtain vCenter Credentials
        ${vcenter} = $ydata.vcenter.hostname
        if (Test-Path -Path "$homePath\vcenterpowercli.Cred") {
            Write-Log "Found Existing Credentials for vCenter '$(${vcenter})'."
            Write-Log ""
            ${vcenterCred} = Import-CliXml -Path "$homePath\vcenterpowercli.Cred"
        } else {
            Write-Log "Enter Credentials of vCenter: '$(${vcenter})'"
            Write-Log ""
            ${vcenterCred} = Get-Credential -Message "Enter Credentials for vCenter '$(${vcenter})'."
            ${vcenterCred} | Export-CliXml -Path "$homePath\vcenterpowercli.Cred"
        }
        Write-Log "Logging into vCenter: '$(${vcenter})'"
        Write-Log ""
        $vcenterConn = Connect-vCenter
        $ucs_servers = Get-UcsServer
        $fwPackList = @()
        $mntPolicyList = @()
        ${ServerProfileList} = @()
        $error_count = 0
        foreach ($cluster in $ydata.vcenter.clusters) {
            foreach ($vhost in $cluster.hosts) {
                try {
                    write-host "ESX host is $vhost"
                    $server = Get-EsxCli -VMHost $vhost
                    $serial = $server.hardware.platform.get().SerialNumber
                    $server_profile = ($ucs_servers | Where-Object {$_.Serial -eq $serial}).AssignedToDn
                    $sDict = New-Object PsObject -property @{name = $vhost; dn = ($ucs_servers | Where-Object {$_.Serial -eq $serial}).Dn}
                    ${ServerProfileList} += $sDict
                    $sprofile = Get-UcsServiceProfile -Dn $server_profile
                    $template = $False
                    if (!($null -eq $sprofile.OperSrcTemplName)) {
                        $stemplate = Get-UcsServiceProfile -Dn $sprofile.OperSrcTemplName
                        if ($stemplate.Type -eq "updating-template") { $template = $True
                        } else {
                            Write-Log "Service Profile $($server_profile) is Attached to $($stemplate.Dn)" -ForegroundColor Red
                            Write-Log "But the Template is not not an 'updating-template'" -ForegroundColor Red
                            Write-Log "Disconnect the Service Profile $($server_profile) from the Template."
                            Break
                        }
                    }
                    if ($template -eq $True) {
                        if (!($null -eq $stemplate.OperMaintPolicyName)) {
                            if (!($stemplate.OperMaintPolicyName -in $mntPolicyList)) {
                                $mntPolicyList += $stemplate.OperMaintPolicyName
                                $mPolicy = Get-UcsMaintenancePolicy -Dn $stemplate.OperMaintPolicyName
                                if (!($mPolicy.TriggerConfig -eq "on-next-boot")) {
                                    $mPolicy | Set-UcsMaintenancePolicy -TriggerConfig "on-next-boot" -Confirm:$False -Force:$True | Out-Null
                                }
                            }
                        } else {
                            Write-Log "$($stemplate.Dn) is not attached to a Host Firmware Policy." -ForegroundColor Red
                            $error_count += 1
                            Break
                        }
                    } else {
                        if (!($null -eq $sprofile.OperMaintPolicyName)) {
                            if (!($sprofile.OperMaintPolicyName -in $mntPolicyList)) {
                                $mntPolicyList += $sprofile.OperMaintPolicyName
                                $mPolicy = Get-UcsMaintenancePolicy -Dn $sprofile.OperMaintPolicyName
                                if (!($mPolicy.TriggerConfig -eq "on-next-boot")) {
                                    $mPolicy | Set-UcsMaintenancePolicy -TriggerConfig "on-next-boot" -Confirm:$False -Force:$True | Out-Null
                                }
                            }
                        } else {
                            Write-Log "$($sprofile.Dn) is not attached to a Host Firmware Policy." -ForegroundColor Red
                            $error_count += 1
                            Break
                        }
                    }
                    if ($template -eq $True) {
                        if (!($null -eq $stemplate.OperHostFwPolicyName)) {
                            if (!($stemplate.OperHostFwPolicyName -in $fwPackList)) { $fwPackList += $stemplate.OperHostFwPolicyName }
                        } else {
                            Write-Log "$($stemplate.Dn) is not attached to a Host Firmware Policy." -ForegroundColor Red
                            $error_count += 1
                            Break
                        }
                    } else {
                        if (!($null -eq $sprofile.OperHostFwPolicyName)) {
                            if (!($sprofile.OperHostFwPolicyName -in $fwPackList)) { $fwPackList += $sprofile.OperHostFwPolicyName }
                        } else {
                            Write-Log "$($sprofile.Dn) is not attached to a Host Firmware Policy." -ForegroundColor Red
                            $error_count += 1
                            Break
                        }
                    }
                    Write-Host $server_profile
                } catch {
                    Write-Error "Failed modifying Host Firmware Package Version=${version}" -ForegroundColor Red
                    Write-Log ${Error}
                    Disconnect-Ucs -ErrorAction Ignore | Out-Null
                    Disconnect-VIServer -ErrorAction Ignore -Confirm:$false | Out-Null
                    # Write-ErrorLog
                    Exit 1
                }
            }
        }
        if ($error_count -eq 0) {
            $fwCompHostPacks = $fwPackList | ForEach-Object {Get-UcsFirmwareComputeHostPack -Dn $_ -PolicyOwner local}
            $fwCompHostPacks | Set-UcsFirmwareComputeHostPack -BladeBundleVersion ${infraVersionB} -RackBundleVersion ${infraVersionC} -Force -ErrorAction Stop | Out-Null
        } else {
            Write-Error "Failed modifying Host Firmware Package Version=${version}" -ForegroundColor Red
            Write-Log "Failed modifying Host Firmware Package Version=${version}" -ForegroundColor Red
            Disconnect-Ucs -ErrorAction Ignore | Out-Null
            Disconnect-VIServer -ErrorAction Ignore -Confirm:$false | Out-Null
            # Write-ErrorLog
            Exit 1
        }
        foreach ($cluster in $ydata.vcenter.clusters) {
            #$cluster_compliance = Get-Compliance -Entity $cluster.name
            foreach ($vhost in $cluster.hosts) {
                try {
                    Write-Log "ESX host is $vhost"
                    $server = Get-EsxCli -VMHost $vhost
                    if (!($server.ConnectionState -eq "Maintenance")) {
                        $server | Set-VMHost -State Maintenance -RunAsync -Confirm:$false | Out-Null
                        if ($ydata.vcenter.license -eq "standard") {
                            #$cluster_hosts = Get-Cluster -Name DC-CCIE | Get-VMHost
                            Write-Host "Standard VMware License"
                        }
                    }
                    "$(($ucs_servers | Where-Object {$_.Serial -eq $serial}).Dn)/fw-status"
                    $server = Get-EsxCli -VMHost $vhost
                    Write-Log "Host $vhost ConnectionState is '$($server.ConnectionState)'" -ForegroundColor Cyan
                    Write-Log ""
                    ${ServerProfileFwList} = @((${ServerProfileList} | Where-Object {$_.name -eq $vhost}).dn)
                    Wait-UcsServersActivation
                    #if ($ydata.upgrade.vum_update -eq $true) {
                    #    $server | Test-Compliance -Entity $vhost | Out-Null
                    #    $compliance = Get-Compliance -Entity $vhost
                    #}
                } catch {

                }
            }
        }
    }
    #=====================>>>>>>>>>>>Server Firmware Upgrade<<<<<<<<<<================================
    Disconnect-Ucs -ErrorAction Ignore | Out-Null
    Write-Log "Firmware update process completed."
    Exit 0
}
Catch {
    if (${Error} -like "*In order to download software, you must accept the EULA*") {
        Write-Log "Error occurred in script:"
        Write-Log " In order to download software, you must accept the EULA. You will receive an email within 24 hours which will have details on accepting EULA.`
        Once you accept the EULA by following the instructions mentioned in the email, re-run this script to proceed."
        Disconnect-Ucs -ErrorAction Ignore | Out-Null
        Disconnect-VIServer -ErrorAction Ignore | Out-Null
        Exit 1
    } else {
        Write-Log "Error occurred in script:"
        Write-Log ${Error}
        Disconnect-Ucs -ErrorAction Ignore | Out-Null
        Disconnect-VIServer -ErrorAction Ignore | Out-Null
        Exit 1
    }
}
