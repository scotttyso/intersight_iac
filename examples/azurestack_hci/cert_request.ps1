Write-Host "Creating CertificateRequest(CSR) for $CertName `r "
#Invoke-Command -ComputerName testbox -ScriptBlock {
#$CertName = "r142c-2-8.rich.ciscolabs.com"
#$Certname = "HGS Signing Certificate"
$Certname = "HGS Encryption Certificate"
$CSRPath = "c:\temp\$($CertName)_.csr"
$INFPath = "c:\temp\$($CertName)_.inf"
$Signature = '$Windows NT$' 
$INF =
@"
[Version]
Signature= "$Signature" 
[NewRequest]
Subject = "CN=$CertName, OU=Richfield Lab, O=Cisco Systems, L=Richfield, S=Ohio, C=US"
KeySpec = 1
KeyLength = 4096
Exportable = TRUE
MachineKeySet = TRUE
SMIME = False
PrivateKeyArchive = FALSE
HashAlgorithm = SHA256
UserProtected = FALSE
UseExistingKeySet = FALSE
ProviderName = "Microsoft RSA SChannel Cryptographic Provider"
ProviderType = 12
RequestType = PKCS10
KeyUsage = 0xa0
[EnhancedKeyUsageExtension]
OID=1.3.6.1.5.5.7.3.1 
"@
write-Host "Certificate Request is being generated `r "
$INF | out-file -filepath $INFPath -force
certreq -new $INFPath $CSRPath
#}
write-output "Certificate Request has been generated"
