${env_vars} = Get-Childitem -Path Env:* | Sort-Object Name
if ((${env_vars} | Where-Object {$_.Name -eq "OS"}).Value -eq "Windows_NT") {
    $homePath = (${env_vars} | Where-Object {$_.Name -eq "HOMEPATH"}).Value
} else { $homePath = (${env_vars} | Where-Object {$_.Name -eq "HOME"}).Value }
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
${vcenter} = "yourvcenter-ip"
${cluster} = "your-test-cluster"
Connect-VIServer -Server ${vcenter} -Credential ${vcenterCred}
Test-Compliance -Entity $Cluster