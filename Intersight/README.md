<!-- BEGIN_TF_DOCS -->
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Developed by: Cisco](https://img.shields.io/badge/Developed%20by-Cisco-blue)](https://developer.cisco.com)

# Easy IMM - Comprehensive example for Intersight

## Environment Variables

### Terraform Cloud/Enterprise - Workspace Variables
- Add variable apikey with the value of [your-api-key]
- Add variable secretkey with the value of [your-secret-file-content]

### Linux and Windows
```bash
export TF_VAR_apikey="<your-api-key>"
export TF_VAR_secretkeyfile="<secret-key-file-location>"
```

## Environment Variable for Deploy Process

At this time the deploy process is separate from the profile creation process.  To accomplish deploy the script is using curl to deploy the profiles

### Linux
```bash
export TF_VAR_secretkey=`cat <your-secretkey-file>`
```
## Auto-completion Notes:

If you would like to enable Auto Completion in the Pools File for ip, mac, uuid, wwnn, and wwpn perform the following in Visual Studio Code.

### Install the YAML extension by Red Hat
`Extensions`: Search for YAML and Select the 'YAML Language Support by Red Hat'

### Add the YAML Schema's below to the Visual Studio Code Settings

`Settings` » `Settings`: Search for `YAML:Schemas`.

Click: `Edit in settings.json`

Configure the following in `yaml.schemas`
```bash
"https://raw.githubusercontent.com/terraform-cisco-modules/easy-imm-comprehensive-example/main/schemas/pools.json": "pools.yaml"
```

## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >=1.3.0 |
| <a name="requirement_intersight"></a> [intersight](#requirement\_intersight) | >=1.0.34 |
| <a name="requirement_utils"></a> [utils](#requirement\_utils) | >= 0.1.3 |
## Providers

| Name | Version |
|------|---------|
| <a name="provider_utils"></a> [utils](#provider\_utils) | 0.2.2 |
| <a name="provider_time"></a> [time](#provider\_time) | 0.9.1 |
| <a name="provider_intersight"></a> [intersight](#provider\_intersight) | 1.0.34 |
## Modules

| Name | Source | Version |
|------|--------|---------|
| <a name="module_pools"></a> [pools](#module\_pools) | ../../../../terraform-cisco-modules/terraform-intersight-pools | n/a |
| <a name="module_domain_profiles"></a> [domain\_profiles](#module\_domain\_profiles) | ../../../../terraform-cisco-modules/terraform-intersight-profiles-domain | n/a |
| <a name="module_policies"></a> [policies](#module\_policies) | ../../../../terraform-cisco-modules/terraform-intersight-policies | n/a |
| <a name="module_profiles"></a> [profiles](#module\_profiles) | ../../../../terraform-cisco-modules/terraform-intersight-profiles | n/a |

## NOTE:
**When the Data is merged from the YAML files, it will run through the modules using for_each loop(s).  Sensitive Variables cannot be added to a for_each loop, instead use the variables below to add sensitive values for policies.**

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_apikey"></a> [apikey](#input\_apikey) | Intersight API Key. | `string` | n/a | yes |
| <a name="input_deploy_profiles"></a> [deploy\_profiles](#input\_deploy\_profiles) | Flag to Determine if Profiles Should be deployed. | `string` | `false` | no |
| <a name="input_endpoint"></a> [endpoint](#input\_endpoint) | Intersight Endpoint Hostname. | `string` | `"intersight.com"` | no |
| <a name="input_moids_policies"></a> [moids\_policies](#input\_moids\_policies) | Flag to Determine if Policies Should be associated using resource or data object. | `bool` | `false` | no |
| <a name="input_moids_pools"></a> [moids\_pools](#input\_moids\_pools) | Flag to Determine if Pools Should be associated using data object or from var.pools. | `bool` | `false` | no |
| <a name="input_operating_system"></a> [operating\_system](#input\_operating\_system) | Type of Operating System.<br>* Linux<br>* Windows | `string` | `"Linux"` | no |
| <a name="input_organization"></a> [organization](#input\_organization) | Name of the default intersight Organization. | `string` | `"default"` | no |
| <a name="input_name_prefix"></a> [name\_prefix](#input\_name\_prefix) | Prefix to Add to Pools, Policies, and Profiles. | `string` | `""` | no |
| <a name="input_secretkey"></a> [secretkey](#input\_secretkey) | Intersight Secret Key. | `string` | `""` | no |
| <a name="input_secretkeyfile"></a> [secretkeyfile](#input\_secretkeyfile) | Intersight Secret Key File Location. | `string` | `"blah.txt"` | no |
| <a name="input_tags"></a> [tags](#input\_tags) | List of Key/Value Pairs to Assign as Attributes to the Policy. | `list(map(string))` | `[]` | no |
| <a name="input_base64_certificate_1"></a> [base64\_certificate\_1](#input\_base64\_certificate\_1) | The Server Certificate in Base64 format. | `string` | `""` | no |
| <a name="input_base64_certificate_2"></a> [base64\_certificate\_2](#input\_base64\_certificate\_2) | The Server Certificate in Base64 format. | `string` | `""` | no |
| <a name="input_base64_certificate_3"></a> [base64\_certificate\_3](#input\_base64\_certificate\_3) | The Server Certificate in Base64 format. | `string` | `""` | no |
| <a name="input_base64_certificate_4"></a> [base64\_certificate\_4](#input\_base64\_certificate\_4) | The Server Certificate in Base64 format. | `string` | `""` | no |
| <a name="input_base64_certificate_5"></a> [base64\_certificate\_5](#input\_base64\_certificate\_5) | The Server Certificate in Base64 format. | `string` | `""` | no |
| <a name="input_base64_private_key_1"></a> [base64\_private\_key\_1](#input\_base64\_private\_key\_1) | The Server Private Key in Base64 Format. | `string` | `""` | no |
| <a name="input_base64_private_key_2"></a> [base64\_private\_key\_2](#input\_base64\_private\_key\_2) | The Server Private Key in Base64 Format. | `string` | `""` | no |
| <a name="input_base64_private_key_3"></a> [base64\_private\_key\_3](#input\_base64\_private\_key\_3) | The Server Private Key in Base64 Format. | `string` | `""` | no |
| <a name="input_base64_private_key_4"></a> [base64\_private\_key\_4](#input\_base64\_private\_key\_4) | The Server Private Key in Base64 Format. | `string` | `""` | no |
| <a name="input_base64_private_key_5"></a> [base64\_private\_key\_5](#input\_base64\_private\_key\_5) | The Server Private Key in Base64 Format. | `string` | `""` | no |
| <a name="input_ipmi_key"></a> [ipmi\_key](#input\_ipmi\_key) | Encryption key 1 to use for IPMI communication. It should have an even number of hexadecimal characters and not exceed 40 characters. | `string` | `""` | no |
| <a name="input_iscsi_boot_password"></a> [iscsi\_boot\_password](#input\_iscsi\_boot\_password) | Password to Assign to the iSCSI Boot Policy if doing Authentication. | `string` | `""` | no |
| <a name="input_binding_parameters_password"></a> [binding\_parameters\_password](#input\_binding\_parameters\_password) | The password of the user for initial bind process with an LDAP Policy. It can be any string that adheres to the following constraints. It can have character except spaces, tabs, line breaks. It cannot be more than 254 characters. | `string` | `""` | no |
| <a name="input_local_user_password_1"></a> [local\_user\_password\_1](#input\_local\_user\_password\_1) | Password to assign to a Local User Policy -> user. | `string` | `""` | no |
| <a name="input_local_user_password_2"></a> [local\_user\_password\_2](#input\_local\_user\_password\_2) | Password to assign to a Local User Policy -> user. | `string` | `""` | no |
| <a name="input_local_user_password_3"></a> [local\_user\_password\_3](#input\_local\_user\_password\_3) | Password to assign to a Local User Policy -> user. | `string` | `""` | no |
| <a name="input_local_user_password_4"></a> [local\_user\_password\_4](#input\_local\_user\_password\_4) | Password to assign to a Local User Policy -> user. | `string` | `""` | no |
| <a name="input_local_user_password_5"></a> [local\_user\_password\_5](#input\_local\_user\_password\_5) | Password to assign to a Local User Policy -> user. | `string` | `""` | no |
| <a name="input_persistent_passphrase"></a> [persistent\_passphrase](#input\_persistent\_passphrase) | Secure passphrase to be applied on the Persistent Memory Modules on the server. The allowed characters are:<br>  - a-z, A-Z, 0-9 and special characters: \u0021, &, #, $, %, +, ^, @, \_, *, -. | `string` | `""` | no |
| <a name="input_access_community_string_1"></a> [access\_community\_string\_1](#input\_access\_community\_string\_1) | The default SNMPv1, SNMPv2c community name or SNMPv3 username to include on any trap messages sent to the SNMP host. The name can be 18 characters long. | `string` | `""` | no |
| <a name="input_access_community_string_2"></a> [access\_community\_string\_2](#input\_access\_community\_string\_2) | The default SNMPv1, SNMPv2c community name or SNMPv3 username to include on any trap messages sent to the SNMP host. The name can be 18 characters long. | `string` | `""` | no |
| <a name="input_access_community_string_3"></a> [access\_community\_string\_3](#input\_access\_community\_string\_3) | The default SNMPv1, SNMPv2c community name or SNMPv3 username to include on any trap messages sent to the SNMP host. The name can be 18 characters long. | `string` | `""` | no |
| <a name="input_access_community_string_4"></a> [access\_community\_string\_4](#input\_access\_community\_string\_4) | The default SNMPv1, SNMPv2c community name or SNMPv3 username to include on any trap messages sent to the SNMP host. The name can be 18 characters long. | `string` | `""` | no |
| <a name="input_access_community_string_5"></a> [access\_community\_string\_5](#input\_access\_community\_string\_5) | The default SNMPv1, SNMPv2c community name or SNMPv3 username to include on any trap messages sent to the SNMP host. The name can be 18 characters long. | `string` | `""` | no |
| <a name="input_snmp_auth_password_1"></a> [snmp\_auth\_password\_1](#input\_snmp\_auth\_password\_1) | SNMPv3 User Authentication Password. | `string` | `""` | no |
| <a name="input_snmp_auth_password_2"></a> [snmp\_auth\_password\_2](#input\_snmp\_auth\_password\_2) | SNMPv3 User Authentication Password. | `string` | `""` | no |
| <a name="input_snmp_auth_password_3"></a> [snmp\_auth\_password\_3](#input\_snmp\_auth\_password\_3) | SNMPv3 User Authentication Password. | `string` | `""` | no |
| <a name="input_snmp_auth_password_4"></a> [snmp\_auth\_password\_4](#input\_snmp\_auth\_password\_4) | SNMPv3 User Authentication Password. | `string` | `""` | no |
| <a name="input_snmp_auth_password_5"></a> [snmp\_auth\_password\_5](#input\_snmp\_auth\_password\_5) | SNMPv3 User Authentication Password. | `string` | `""` | no |
| <a name="input_snmp_privacy_password_1"></a> [snmp\_privacy\_password\_1](#input\_snmp\_privacy\_password\_1) | SNMPv3 User Privacy Password. | `string` | `""` | no |
| <a name="input_snmp_privacy_password_2"></a> [snmp\_privacy\_password\_2](#input\_snmp\_privacy\_password\_2) | SNMPv3 User Privacy Password. | `string` | `""` | no |
| <a name="input_snmp_privacy_password_3"></a> [snmp\_privacy\_password\_3](#input\_snmp\_privacy\_password\_3) | SNMPv3 User Privacy Password. | `string` | `""` | no |
| <a name="input_snmp_privacy_password_4"></a> [snmp\_privacy\_password\_4](#input\_snmp\_privacy\_password\_4) | SNMPv3 User Privacy Password. | `string` | `""` | no |
| <a name="input_snmp_privacy_password_5"></a> [snmp\_privacy\_password\_5](#input\_snmp\_privacy\_password\_5) | SNMPv3 User Privacy Password. | `string` | `""` | no |
| <a name="input_snmp_trap_community_1"></a> [snmp\_trap\_community\_1](#input\_snmp\_trap\_community\_1) | Community for a Trap Destination. | `string` | `""` | no |
| <a name="input_snmp_trap_community_2"></a> [snmp\_trap\_community\_2](#input\_snmp\_trap\_community\_2) | Community for a Trap Destination. | `string` | `""` | no |
| <a name="input_snmp_trap_community_3"></a> [snmp\_trap\_community\_3](#input\_snmp\_trap\_community\_3) | Community for a Trap Destination. | `string` | `""` | no |
| <a name="input_snmp_trap_community_4"></a> [snmp\_trap\_community\_4](#input\_snmp\_trap\_community\_4) | Community for a Trap Destination. | `string` | `""` | no |
| <a name="input_snmp_trap_community_5"></a> [snmp\_trap\_community\_5](#input\_snmp\_trap\_community\_5) | Community for a Trap Destination. | `string` | `""` | no |
| <a name="input_vmedia_password_1"></a> [vmedia\_password\_1](#input\_vmedia\_password\_1) | Password for a Virtual Media Policy -> mapping target. | `string` | `""` | no |
| <a name="input_vmedia_password_2"></a> [vmedia\_password\_2](#input\_vmedia\_password\_2) | Password for a Virtual Media Policy -> mapping target. | `string` | `""` | no |
| <a name="input_vmedia_password_3"></a> [vmedia\_password\_3](#input\_vmedia\_password\_3) | Password for a Virtual Media Policy -> mapping target. | `string` | `""` | no |
| <a name="input_vmedia_password_4"></a> [vmedia\_password\_4](#input\_vmedia\_password\_4) | Password for a Virtual Media Policy -> mapping target. | `string` | `""` | no |
| <a name="input_vmedia_password_5"></a> [vmedia\_password\_5](#input\_vmedia\_password\_5) | Password for a Virtual Media Policy -> mapping target. | `string` | `""` | no |
## Outputs

| Name | Description |
|------|-------------|
| <a name="output_domain_profiles"></a> [domain\_profiles](#output\_domain\_profiles) | Domain Profile Outputs: including cluster and switch Moids, policy assignments. |
| <a name="output_policies"></a> [policies](#output\_policies) | The Name of Each Policy Created with it's respective Moid. |
| <a name="output_pools"></a> [pools](#output\_pools) | The Name of Each Pool Created with it's respective Moid. |
| <a name="output_profiles"></a> [profiles](#output\_profiles) | The Name of Each Profile Created with it's respective Moid. |

# Sub Modules

If you want to see documentation on Variables for Submodules use the links below:

## Terraform Registry

### Policies

[*Policies*](https://registry.terraform.io/modules/terraform-cisco-modules/policies/intersight/latest)

### Pools

[*Pools*](https://registry.terraform.io/modules/terraform-cisco-modules/pools/intersight/latest)

### Profiles

[*Domain*](https://registry.terraform.io/modules/terraform-cisco-modules/profiles-domain/intersight/latest)

[*Chassis and Server*](https://registry.terraform.io/modules/terraform-cisco-modules/profiles/intersight/latest)
<!-- END_TF_DOCS -->