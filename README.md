# Intersight Infrastructure as Code Wizard

- Terraform Intersight Provider

## Updates/News

TBD

## Synopsis

The purpose of these Terraform and Python scripts are to deploy Policy/Profiles to Intersight using Infastructure as Code.  The goal of the Wizard is to help customers create and better understand how to utilize Terraform for managing infrastrudture.

## Contents

- Use Cases
- Create Pools
- Create Policies
- Deploy UCS Domains in IMM Mode
- Create UCS Service Profiles and Templates

### Use Cases

- Create Pools: IP, IQN, MAC, WWNN, WWPN, and UUID.
- Create Policies: Domain Policies, Mgmt Policies, Server Policies
- Create UCS Domain Profiles and attach Fabric Interconnect clusters to the profiles.
- Create Service Profiles and Templates and deploy physical infrastructure.

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

- Kubernetes Cluster Profile
- UCS Chassis Profile
- UCS Domain Profile
- UCS Server Profile
- UCS Server Template - Important Note.  The script only uses Server Templates for holding policies.  This allows for flexibility around allowing the script to override policies by assigning unique policies to servers that is not supported by standard templates.

To sum this up... the goal is to deploy the infrastructure using infrastructure as code through an easy to consume wizard.

## Resources

Youtube Video's to follow.  This is still a work in progress

## Getting Started

### Install json2hcl

[json2hcl](https://github.com/kvz/json2hcl)

### Python Requirements

- We need Python 3.6 or Greater

[python](https://www.python.org/downloads/release/python-360/)

- Python 3.6+.  Refer to requirements.txt for modules needed to be installed

```bash
pip install -r requirements.txt
```

### Terraform Requirements

The script utilizes features introduced in 0.14 of Terraform so need 0.14 or preferrably greater

[terraform](https://www.terraform.io/downloads.html)

## Run the Wizard

- Running the wizard to use a configuration migrated from UCS Manager using the IMM Transition Tool

```bash
./main.py {json_file_name.json}
```

- Running the Wizard to generate IaC through a Question and Answer Wizard

```bash
./main.py
```

## Disclaimer

This code is provided as is.  No warranty, support, or guarantee is provided with this.
