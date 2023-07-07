#"""
#  IMM Domain Power Check Script.
#  * Tyson Scott 6/30/2023 - tyscott@cisco.com
#"""

#=============================================================================
# YAML File is a Required Parameter
# Pull in YAML Content
#=============================================================================
param (
    [string]$y,
    [switch]$force
)
if (-not ($y)) {
    throw "Missing parameter -y {yaml_file}"
}
if (-not (Test-Path $y)) {
    throw "File $y doesn't exist."
}
Import-Module -Name Cisco.IMC
Import-Module -Name Cisco.UCSManager
Import-module -Name powershell-yaml

$yamlData = Get-Content -Path $y -Raw | ConvertFrom-Yaml
#$folder_path = Split-Path $y

$MenuList = @()
foreach ($item in $yamlData.cabinets) {
    foreach ($i in $item.GetEnumerator()) {
        $MenuList += $i.key
    }
}

Do {
    foreach ($MenuItem in $MenuList) {
        '{0} - {1}' -f ($MenuList.IndexOf($MenuItem) + 1), $MenuItem
    }
    $Choice = ''
    while ([string]::IsNullOrEmpty($Choice)) {
        Write-Host
        $Choice = Read-Host 'Please Select a Cabinet to check '
        if ($Choice -notin 1..$MenuList.Count) {
            [console]::Beep(1000, 300)
            Write-Warning ''
            Write-Warning ('    Your choice [ {0} ] is not valid.' -f $Choice)
            Write-Warning ('        The valid choices are 1 thru {0}.' -f $MenuList.Count)
            Write-Warning '        Please try again ...'
            pause

            $Choice = ''
        }
    }

    ''
    'You chose {0}' -f $MenuList[$Choice - 1]

    foreach ($domain in $yamlData.cabinets.$($MenuList[$Choice - 1]).domains) {
        if ($domain.type -eq "IMM") {
            If (Test-Path -Path $env:HOME\powercliIMM.Cred) {
                $credential = Import-CliXml -Path "$env:HOME\powercliIMM.Cred"
            } Else {
                $credential = Get-Credential
                $credential | Export-CliXml -Path "$env:HOME\powercliIMM.Cred"
            }
            $HostName ="$($domain.name)"
            $Password = ConvertFrom-SecureString -AsPlainText $credential.Password
            $JSON = @{User=$credential.UserName; Password=$Password}
            $null = Invoke-WebRequest -Uri "https://$HostName/Login" -Method POST -Body ($JSON | ConvertTo-Json) -SkipCertificateCheck -UseBasicParsing -SessionVariable cookie
            foreach($chassis in $domain.chassis) {
                Write-Host ""
                Write-Host "$($domain.name) Chassis $chassis Power Supplies."
                $io_card = 'IoCard-{0}-1' -f $chassis
                $headers = @{'inventory-type'='Chassis'; 'inventory-id'=$io_card}
                $power = Invoke-WebRequest -Uri "https://$HostName/api-explorer/resources/redfish/v1/Chassis/$chassis/Power" -Headers $headers -WebSession $cookie -SkipCertificateCheck 
                $power = $power.Content | ConvertFrom-Json
                $power.PowerSupplies | Add-Member -NotePropertyName Domain -NotePropertyValue $domain.name
                $power.PowerSupplies | Add-Member -NotePropertyName Chassis -NotePropertyValue $chassis
                $power.PowerSupplies | Format-Table Domain,Chassis,MemberId,Model,SerialNumber,Status
            }
        } elseif ($domain.type -eq "UCSM") {
            If (Test-Path -Path $env:HOME\powercliUCSM.Cred) {
                $credential = Import-CliXml -Path "$env:HOME\powercliUCSM.Cred"
            } Else {
                $credential = Get-Credential
                $credential | Export-CliXml -Path "$env:HOME\powercliUCSM.Cred"
            }
            $null = Connect-Ucs -Name $domain.name -Credential $credential
            foreach($chassis in $domain.chassis) {
                Write-Host ""
                Write-Host "$($domain.name) Chassis $chassis Power Supplies."
                $regex = 'chassis-{0}' -f $chassis
                Get-UcsPsu | Where-Object { $_.Dn -match $regex } | Format-Table Ucs,Dn,Model,Serial,OperState
            }
            if ($domain.rackmounts) {
                if ($domain.rackmounts -eq $true) {
                    Write-Host ""
                    Write-Host "$($domain.name) Rackmount Power Supplies."
                    $regex = 'sys/rackmount'
                    Get-UcsPsu | Where-Object { $_.Dn -match $regex } | Format-Table Ucs,Dn,Model,Serial,OperState
                }
            }
            Write-Host ""
            Write-Host "$($domain.name) Power Supplies."
            Get-UcsPsu | Where-Object { $_.Dn -match 'sys/switch' } | Format-Table Ucs,Dn,Model,Serial,OperState
            $null = Disconnect-Ucs
        }
    }
    if ($yamlData.cabinets.$($MenuList[$Choice - 1]).rackmounts) {
        foreach ($rackmount in $yamlData.cabinets.$($MenuList[$Choice - 1]).rackmounts) {
            If (Test-Path -Path $env:HOME\powercliIMC.Cred) {
                $credential = Import-CliXml -Path "$env:HOME\powercliIMC.Cred"
            } Else {
                $credential = Get-Credential
                $credential | Export-CliXml -Path "$env:HOME\powercliIMC.Cred"
            }
            $null = Connect-IMC -Name $rackmount.name -Credential $credential
            Write-Host ""
            Get-ImcPsu | Format-Table Imc,Dn,Pid,Serial,Operability
            $null = Disconnect-IMC
        }
    }
    $Answer = Read-Host "Press 1 to rerun the script and choose another cabinet Any other Key to exit."
}
Until ($answer -ne "1")
