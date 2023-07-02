#Declare

Register-PSRepository -Name HITSPSGallery -SourceLocation '\\corefs.med.umich.edu\shared2\UMHS-IT-DR\WIN-NT\HITSPSGallery' -InstallationPolicy Trusted 
Install-Module -Name Intersight -Repository HITSPSGallery -AllowClobber
Import-module -name intersight


$BaseUrl = 'https://michmed.intersight.com'
$KeyID = '5c48a7d373766a3634283fdd/64933c4b756461330155f782/6493699d7564613201bb2170'
$KeyFilePath = "E:\Scripts\IMM_PSU\IntersightAPI.txt"

Set-IntersightConfiguration -BaseUrl $BaseUrl
Set-IntersightConfigurationHttpSigning -KeyId $KeyID -KeyFilePath $KeyFilePath -SignatureValidityPeriod 1800 -HttpSigningHeader '(request-target)', 'Host', 'Date', 'Digest'

$cabinet = @()

Write-Host 'Starting Intersight PSU script'

#Check Modules

#Menu of Cabinet list

function Show-Menu
{
     param (
           [string]$Title = 'Cabinet Selection'
     )
     clear-Host
     Write-Host "================ $Title ================"
     Write-Host "1: DD05"
     Write-Host "2: F09"
     Write-Host "3: FF22"
     Write-Host "4: G05"
     Write-Host "5: G09"
     Write-Host "6: H09"
     Write-Host "7: H18"
     Write-Host "8: HH22"
     Write-Host "9: J09"
     Write-Host "10: J18"
     Write-Host "11: J22"
     Write-Host "12: JJ09"
     Write-Host "13: JJ22"
     Write-Host "14: L05"
     Write-Host "15: L09"
     Write-Host "16: L22"
     Write-Host "17: M09"
     Write-Host "18: MM18"
     Write-Host "19: MM22"
     Write-Host "20: N09"
     Write-Host "21: N18"
     Write-Host "22: NN09"
     Write-Host "23: NN18"
     Write-Host "24: NN22"
     Write-Host "25: P09"
     Write-Host "26: P22"
     Write-Host "27: PP22"
     Write-Host "28: QQ09"
     Write-Host "29: R18"
     Write-Host "30: RR09"
     Write-Host "31: RR18"
     Write-Host "32: RR22"
     Write-Host "33: S05"
     Write-Host "34: S09"
     Write-Host "35: T09"
     Write-Host "36: T22"
     Write-Host "37: U22"

}



Do {
    Show-Menu
    $input = read-host 'Please Select a Cabinet to check'
    switch ($input) {
        1 { $cabinet = 'DD05';$Domains = 'NC-TEST-FI-1'; $Chassis = 'NC-TEST-FI-1-3'}
        2 { $cabinet = 'F09'; $Domains = 'NC-TEST-FI-1'; $Chassis = 'NC-QA-FI-2-2','NC-PG-4-1','NC-PG-4-2','NC-PG-4-3'}
        3 { $cabinet = 'FF22';$Domains = 'NC-TEST-FI-1'; $Chassis = 'NC-PG-FI-2-4','NC-PG-FI-2-8'}
        4 { $cabinet = 'G05'; $Domains = 'NC-TEST-FI-1'; $Chassis = 'NC-PG-FI-2-18','NC-SB-FI-1','NC-SB-FI-16'}
        5 { $cabinet = 'G09'; $Domains = 'NC-TEST-FI-1'; $Chassis = 'NC-QA-FI-2-3','NC-PG-4-4','NC-PG-4-8','NC-PG-4-15'}
        6 { $cabinet = 'H09'; $Domains = 'NC-TEST-FI-1'; $Chassis = 'NC-PG-4-9','NC-PG-4-11','NC-PG-4-12','NC-PG-4-13'}
        7 { $cabinet = 'H18'; $Domains = 'NC-TEST-FI-1'; $Chassis = 'NC-PG-FI-3-2','NC-PG-FI-3-3','NC-PG-FI-3-4'}
        8 { $cabinet = 'HH22';$Domains = 'NC-TEST-FI-1'; $Chassis = 'NC-PG-FI-2-16','NC-PG-FI-3-1','NC-PG-FI-3-12'}
        9 { $cabinet = 'J09'; $Domains = 'NC-TEST-FI-1'; $Chassis = 'NC-QA-FI-2-1','NC-PG-4-6','NC-PG-4-7','NC-PG-4-16'}
        10 {$cabinet = 'J18'; $Domains = 'NC-TEST-FI-1'; $Chassis = 'NC-PG-FI-3-5','NC-PG-FI-3-6','NC-PG-FI-3-10'}
        11 {$cabinet = 'J22'; $Domains = 'NC-TEST-FI-1'; $Chassis = 'NC-PG-FI-2-2'}
        12 {$cabinet = 'JJ09';$Domains = 'NC-TEST-FI-1'; $Chassis = 'NC-SB-2-4-X','NC-SB-FI-7'}
        13 {$cabinet = 'JJ22';$Domains = 'NC-TEST-FI-1'; $Chassis = 'NC-PG-FI-2-10','NC-QA-FI-7'}
        14 {$cabinet = 'L05'; $Domains = 'NC-TEST-FI-1'; $Chassis = 'NC-SB-2-5','NC-SB-FI-2'}
        15 {$cabinet = 'L09'; $Domains = 'NC-TEST-FI-1'; $Chassis = 'NC-PG-4-5','NC-PG-4-10','NC-PG-4-14','NC-PG-4-18-X'}
        16 {$cabinet = 'L22'; $Domains = 'NC-TEST-FI-1'; $Chassis = 'NC-PG-FI-2-3'}
        17 {$cabinet = 'M09'; $Domains = 'NC-TEST-FI-1'; $Chassis = 'NC-QA-FI-2-4','NC-TEST-FI-1-2'}
        18 {$cabinet = 'MM18';$Domains = 'NC-TEST-FI-1'; $Chassis = 'NC-PG-FI-2-9','NC-PG-FI-2-14'}
        19 {$cabinet = 'MM22';$Domains = 'NC-TEST-FI-1'; $Chassis = 'NC-PG-FI-2-5'}
        20 {$cabinet = 'N09'; $Domains = 'NC-TEST-FI-1'; $Chassis = 'NC-PG-4-17','NC-SB-FI-10'}
        21 {$cabinet = 'N18'; $Domains = 'NC-TEST-FI-1'; $Chassis = 'NC-PG-FI-3-7','NC-PG-FI-3-8','NC-PG-FI-3-9'}
        22 {$cabinet = 'NN09';$Domains = 'NC-TEST-FI-1'; $Chassis = 'NC-QA-FI-5','NC-SB-FI-11'}
        23 {$cabinet = 'NN18';$Domains = 'NC-TEST-FI-1'; $Chassis = 'NC-PG-FI-2-15','NC-PG-FI-2-19'}
        24 {$cabinet = 'NN22';$Domains = 'NC-TEST-FI-1'; $Chassis = 'NC-PG-FI-2-6','NC-PG-FI-2-13','NC-PG-FI-3-11'}
        25 {$cabinet = 'P09'; $Domains = 'NC-TEST-FI-1'; $Chassis = 'NC-SB-FI-9'}
        26 {$cabinet = 'P22'; $Domains = 'NC-TEST-FI-1'; $Chassis = 'NC-SB-FI-18'}
        27 {$cabinet = 'PP22';$Domains = 'NC-TEST-FI-1'; $Chassis = 'NC-SB-2-3','NC-PG-FI-2-7'}
        28 {$cabinet = 'QQ09';$Domains = 'NC-TEST-FI-1'; $Chassis = 'NC-SB-FI-8'}
        29 {$cabinet = 'R18'; $Domains = 'NC-TEST-FI-1'; $Chassis = 'NC-SB-2-8','NC-SB-2-9'}
        30 {$cabinet = 'RR09';$Domains = 'NC-TEST-FI-1'; $Chassis = 'NC-SB-2-8'}
        31 {$cabinet = 'RR18';$Domains = 'NC-TEST-FI-1'; $Chassis = 'NC-PG-FI-2-12'}
        32 {$cabinet = 'RR22';$Domains = 'NC-TEST-FI-1'; $Chassis = 'NC-PG-FI-2-11','NC-SB-FI-12','NC-SB-FI-13'}
        33 {$cabinet = 'S05'; $Domains = 'NC-TEST-FI-1'; $Chassis = 'NC-SB-2-6','NC-SB-2-7'} 
        34 {$cabinet = 'S09'; $Domains = 'NC-TEST-FI-1'; $Chassis = 'NC-QA-FI-6','NC-SB-FI-14','NC-SB-FI-17'}
        35 {$cabinet = 'T09'; $Domains = 'NC-TEST-FI-1'; $Chassis = 'NC-SB-FI-15'}
        36 {$cabinet = 'T22'; $Domains = 'NC-TEST-FI-1'; $Chassis = 'NC-PG-FI-7'}
        37 {$cabinet = 'U22'; $Domains = 'NC-TEST-FI-1'; $Chassis = 'NC-PG-FI-2-17'}       

        Default {Exit}
          
    }
    Write-host 'You chose Cabinet:' $cabinet
    Foreach ($immchassis in $chassis) {
        Write-Host 'Chassis: ' $immchassis
    }
    Write-Host "`nChecking PSU Status...."
    Foreach ($immchassis in $chassis) {
        $mychassis = (Get-IntersightEquipmentChassisList -Inlinecount allpages -Select 'Name,Moid,Serial' -VarFilter  "Name eq '$($immchassis)'")
        $chassispsu = $mychassis.actualInstance.Results | Select-Object -Property *, @{Name="PSUs";E={Get-IntersightEquipmentPsuList -select 'OperState,Dn' -VarFilter "EquipmentChassis.Moid eq '$($_.Moid)'" | select -Expand actualInstance | select -expand results}}
        $chassispsu | Select-Object -Property name,serial,@{N="PSU";E={$_.Psus | Select-Object dn,operstate | Format-Table -auto | Out-String}} | ft -auto -Wrap 
    }
    $Answer = Read-Host "Press 1 to rerun the script and choose another cabinet Any other Key to exit."
}
Until ($answer -ne "1")
Clear-Host