#"""
# Script to get Pure Storage FlashArray ApiToken.
#  * Tyson Scott 9/27/2023 - tyscott@cisco.com
#"""


#=============================================================================
# JSON File is a Required Parameter
# Pull in JSON Content
#=============================================================================
param (
    [string]$e=$(throw "-e 'endpoint' is required."),
    [string]$o=$(throw "-o 'ouptut_file' is required."),
    [string]$u=$(throw "-u 'username' is required."),
    [switch]$force
)

#=====================================================
# * Adds PureStoragePowerShellSDK2 snapin
# * Start Log and Configure PowerCLI
#=====================================================
Import-Module PureStoragePowerShellSDK2
Start-Transcript -Path ".\Logs\$(get-date -f "yyyy-MM-dd_HH-mm-ss")_$($env:USER).log" -Append -Confirm:$false

#=====================================================
# Login to Pure Array and get ApiVersion
#=====================================================
try {
    if (Test-Path -Path ${env:HOME}\pfapowercli.Cred) {
        $credential = Import-CliXml -Path "${env:HOME}\pfapowercli.Cred"
        $api_version = Connect-Pfa2Array -Endpoint $e -Credential $credential -IgnoreCertificateError
    } else {
        $password = ConvertTo-SecureString $env:pure_storage_password -AsPlainText -Force
        $api_version = Connect-Pfa2Array -Endpoint $e -User $u -Password $password -IgnoreCertificateError
    }
}
catch {
    Write-Host "There was an issue with connecting to $e"
    exit
}
#=====================================================
# Login to Pure Array and get AdminApiToken
#=====================================================
if (Test-Path -Path ${env:HOME}\pfapowercli.Cred) {
    $credential = Import-CliXml -Path "${env:HOME}\pfapowercli.Cred"
    $null = Connect-Pfa2Array -Endpoint $e -Credential $credential -IgnoreCertificateError
} else {
    $null = Connect-Pfa2Array -Endpoint $e -User $u -Password $password -IgnoreCertificateError
}
$api_token = Get-Pfa2AdminApiToken -ExposeApiToken $true
if (!($api_token.ApiToken.Token.Length -gt 34)) {
    $api_token = New-Pfa2AdminApiToken
}
Write-Host "Api Version is $($api_version.ApiVersion)"
if ($api_token.ApiToken.Token.Length -gt 34) {
    Write-Host "Obtained AdminApiToken"
}
#=====================================================
# Write Output to JSON File
#=====================================================
$pure_output = @(@{api_token = $api_token.ApiToken.Token; api_version = $api_version.ApiVersion})
Write-Host "Output File is '$($o)'"
$pure_output | ConvertTo-Json -depth 5 | Set-Content $o -Encoding UTF8
Stop-Transcript
exit
