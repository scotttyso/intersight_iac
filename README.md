# Intersight IaC Wizard

[![published](https://static.production.devnetcloud.com/codeexchange/assets/images/devnet-published.svg)](https://developer.cisco.com/codeexchange/github/repo/scotttyso/intersight_iac)

## Updates/News

03-08-2022
* Added Windows Support

* IMPORTANT - There is currently a bug with Policy Buckets for UCS Domain Profiles.  That is the only reason ucs_domain_profiles are not in the same folder as chassis and servers.  When this is fixed the ucs_domain_profiles folder will be merged with the profiles folder.  Because of this limitation at this time make sure to create a seperate policy for Domains of the following types:

- network_connectivity_policies - If Using Standalone Server Policies
- ntp_policies - If Using Standalone Server Policies
- snmp_policies
- syslog_policies

## Getting Started

## Install git

- Windows Download Here [Git](https://git-scm.com/download/win)
- Linux - Use the System Package Manager - apt/yum etc.

configure Git Credentials

```bash
git config --global user.name "<username>"   
git config --global user.email "<email>"
```
### Install json2hcl - Linux/OS-X

[json2hcl](https://github.com/kvz/json2hcl)

### Install the Go Compiler - Windows

[go](https://go.dev/dl/) - Download Here

- Add the Go Compiler to the System Path.

```powershell
$oldpath = (Get-ItemProperty -Path 'Registry::HKEY_LOCAL_MACHINE\System\CurrentControlSet\Control\Session Manager\Environment' -Name PATH).path
$newpath = "$oldpath;C:\Program Files\Go\bin"
Set-ItemProperty -Path 'Registry::HKEY_LOCAL_MACHINE\System\CurrentControlSet\Control\Session Manager\Environment' -Name PATH -Value $newpath
```

### Install hcl2json - Windows

```bash
$ git clone https://github.com/tmccombs/hcl2json
$ cd hcl2json
$ go build
```

- IMPORTANT - Make sure to add the hcl2json.exe file to a folder that is included in the system path.

## Python Requirements

- Windows Download Here [Python](https://www.python.org/downloads/) 
- Linux - Use the System Package Manager - apt/yum etc.
- Python 3.6 or Greater
- For Windows.  Make sure python.exe and pip.exe are available via the system path.
- Refer to requirements.txt for libraries needed to be installed or simply install the requirements file as shown below:

- Windows Example (The Folder Python310 would be according to the Python Release)

```powershell
$oldpath = (Get-ItemProperty -Path 'Registry::HKEY_LOCAL_MACHINE\System\CurrentControlSet\Control\Session Manager\Environment' -Name PATH).path
$newpath = "$oldpath;%USERPROFILE%\AppData\Local\Programs\Python\Python310\;%USERPROFILE%\AppData\Local\Programs\Python\Python310\Scripts\"
Set-ItemProperty -Path 'Registry::HKEY_LOCAL_MACHINE\System\CurrentControlSet\Control\Session Manager\Environment' -Name PATH -Value $newpath
```

* Install the Requirements File

```bash
pip install -r requirements.txt
```

### Terraform Requirements

The script utilizes features introduced in 0.14 of Terraform.  So we need 0.14 or preferrably >1.0

- Download Here [terraform](https://www.terraform.io/downloads.html) 
- For Windows Make sure it is in a Directory that is in the system path.

### Terraform Modules and Providers

This script will utilize the Intersight Terraform Provider and two modules built off of the Intersight Provider.

- [Intersight Provider](https://registry.terraform.io/providers/CiscoDevNet/intersight/latest)
- [IMM Module](https://registry.terraform.io/modules/terraform-cisco-modules/imm/intersight/latest)
- [Easy IMM](https://github.com/terraform-cisco-modules/terraform-intersight-easy-imm)

## Running the Wizard

- It is recommend to add the following secure variables to your environment before running the script

- Linux

```bash
## Intersight Variables
export TF_VAR_apikey="<your_intersight_api_key>"
export TF_VAR_secretkey=`cat ~/Downloads/SecretKey.txt` 
# The above example is based on the key being in your Downloads folder.  Correct for your environment

## Terraform Cloud Variables
export TF_VAR_terraform_cloud_token="<your_terraform_cloud_token>"
```

- Windows - First run the secret.cmd script in the directory which will echo the secret key to the window in the proper format.  Copy the PRIVATE KEY contents to the secretkey

```powershell
## Intersight Variables
$env:TF_VAR_apikey="<your_intersight_api_key>"
$env:TF_VAR_secretkey="<secret_key_from_secret.cmd_output>"
# The above example is based on the key being in your Downloads folder.  Correct for your environment

## Terraform Cloud Variables
$env:TF_VAR_terraform_cloud_token="<your_terraform_cloud_token>"
```

- Running the wizard to use a configuration migrated from UCS Manager using the IMM Transition Tool

```bash
./main.py -j {json_file_name.json}
```

- Running the Wizard to generate IaC through a Question and Answer Wizard

```bash
./main.py
```

- Help Information
```bash
./main.py -h

Intersight Easy IMM Deployment Module

optional arguments:
  -h, --help            show this help message and exit
  -a API_KEY_ID, --api-key-id API_KEY_ID
                        The Intersight API client key id for HTTP signature scheme
  -s API_KEY_FILE, --api-key-file API_KEY_FILE
                        Name of file containing The Intersight secret key for the HTTP signature scheme
  --api-key-v3          Use New API client (v3) key
  -d DIR, --dir DIR     The Directory to Publish the Terraform Files to.
  -i, --ignore-tls      Ignore TLS server-side certificate verification
  -j JSON_FILE, --json_file JSON_FILE
                        The IMM Transition Tool JSON Dump File to Convert to HCL.
  -u URL, --url URL     The Intersight root URL for the API endpoint. The default is https://intersight.com
```

## Terraform Plan and Apply

After the Script has generated the Terraform Directories and downloaded the resources from the Easy IMM Repository, the data will need to be pushed to Intersight using Terraform Cloud.  It is important to execute the Workspaces in the following Order:

1. pools and ucs_domain_profiles*
2. policies
3. profiles

* It doesn't matter if you run pools or ucs_domain_profiles first as there is no dependency between both of them.  Both Just need to be run before you run policies and profiles.

## Disclaimer

This code is provided as is.  No warranty, support, or guarantee is provided with this.  But in typical github fashion there is the opportunity to collaborate and share Bug's/Feedback/PR Requests.

## Synopsis

The purpose of this Python Tool is to deploy Policy/Profiles to Intersight using Infastructure as Code with Terraform.  The Wizard is a step for users to create and better understand how to utilize Terraform for managing infrastrudture.

The goal of this module is to begin to familiarize you with Terraform through the following steps:  

1. Begin to familiarize users with Terraform format and variable creation.  
2. Once a user feels conformatable with auto generated files, Transition towards writing your own modules to consume the IMM Modules.
3. And lastly build your confidence to write your own code as well.  

The wizard will show after each section what the Terraform code being generated will look like.  Point you to the directly where the code will be stored.  And lastly, publish the code to Terraform Cloud and when you are ready.

## Contents

- Use Cases
- Create Pools
- Create Policies
- Deploy UCS Domains in IMM Mode
- Create UCS Service Profiles and Templates

### Use Cases

- Create Pools
- Create Policies
- Create UCS Domain Profiles and attach Fabric Interconnects to the profiles
- Create Service Profiles and Templates and deploy physical infrastructure

### Intersight Pools

This set of modules support creating the following Pool Types:

- FC Pools
- IP Pools
- IQN Pools
- MAC Pools
- UUID Pools

### Intersight Policies

This set of modules support creating the following Policy Types:

- Adapter Configuration
- BIOS
- Boot Order
- Certificate Management
- Device Connector
- Ethernet Adapter
- Ethernet Network
- Ethernet Network Control
- Ethernet Network Group
- Ethernet QoS
- Fibre Channel Adapter
- Fibre Channel Network
- Fibre Channel QoS
- IMC Access
- Flow Control
- IPMI Over LAN
- iSCSI Adapter
- iSCSI Boot
- iSCSI Static Target
- LAN Connectivity
- LDAP
- Link Aggregation
- Link Control
- Local User
- Multicast
- Network Connectivity
- NTP
- Persistent Memory
- Port
- Power
- SAN Connectivity
- SD Card
- Serial over LAN
- SMTP
- SNMP
- SSH
- Storage
- Switch Control
- Syslog
- System QoS
- Thermal
- Virtual KVM
- Virtual Media
- VLAN
- VSAN

### Intersight Profiles and Templates

This set of modules support creating the following Profile Types:

- UCS Chassis Profile
- UCS Domain Profile
- UCS Server Profile
- UCS Server Template - Important Note.  The script only uses Server Templates for holding policies.  This allows for flexibility around allowing the script to override policies by assigning unique policies to servers that is not supported by standard templates.

To sum this up... the goal is to deploy the infrastructure using Terraform through an easy to consume wizard.

## Resources

Youtube Video's to follow.  This is still a work in progress
