# ucs_domain_profiles - Intersight UCS Domain Profiles Deployment Module

## Use this module to create UCS Domain Profiles in Intersight

## Usage

```hcl
module "ucs_domain_profiles" {

  source = "terraform-cisco-modules/easy-imm/intersight//modules/ucs_domain_profiles"

  # omitted...
}
```

This module will create UCS Domain Profiles in Intersight.  

<!-- BEGINNING OF PRE-COMMIT-TERRAFORM DOCS HOOK -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_intersight"></a> [intersight](#requirement\_intersight) | >=1.0.17 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_intersight"></a> [intersight](#provider\_intersight) | >=1.0.17 |

## Modules

| Name | Source | Version |
|------|--------|---------|
| <a name="module_ucs_domain_profiles"></a> [ucs\_domain\_profiles](#module\_ucs\_domain\_profiles) | terraform-cisco-modules/imm/intersight//modules/ucs_domain_profiles | >=0.9.6 |
| <a name="module_ucs_domain_switches"></a> [ucs\_domain\_switches](#module\_ucs\_domain\_switches) | terraform-cisco-modules/imm/intersight//modules/ucs_domain_switches | >=0.9.6 |

## Resources

| Name | Type |
|------|------|
| [intersight_network_element_summary.fis](https://registry.terraform.io/providers/CiscoDevNet/intersight/latest/docs/data-sources/network_element_summary) | data source |
| [intersight_organization_organization.org_moid](https://registry.terraform.io/providers/CiscoDevNet/intersight/latest/docs/data-sources/organization_organization) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_apikey"></a> [apikey](#input\_apikey) | Intersight API Key. | `string` | n/a | yes |
| <a name="input_endpoint"></a> [endpoint](#input\_endpoint) | Intersight URL. | `string` | `"https://intersight.com"` | no |
| <a name="input_organizations"></a> [organizations](#input\_organizations) | Intersight Organization Names. | `set(string)` | <pre>[<br>  "default"<br>]</pre> | no |
| <a name="input_secretkey"></a> [secretkey](#input\_secretkey) | Intersight Secret Key. | `string` | n/a | yes |
| <a name="input_tags"></a> [tags](#input\_tags) | List of Key/Value Pairs to Assign as Attributes to the Policy. | `list(map(string))` | `[]` | no |
| <a name="input_ucs_domain_profiles"></a> [ucs\_domain\_profiles](#input\_ucs\_domain\_profiles) | Intersight UCS Domain Profile Variable Map.<br>* action - Action to Perform on the Chassis Profile Assignment.  Options are:<br>  - Deploy<br>  - No-op<br>  - Unassign<br>* assign\_switches - Flag to define if the physical FI's should be assigned to the policy.  Default is false.<br>* description - Description to Assign to the Profile.<br>* device\_model - This field specifies the device model that this Port Policy is being configured for.<br>  - UCS-FI-6454 - (Default) - The standard 4th generation UCS Fabric Interconnect with 54 ports.<br>  - UCS-FI-64108 - The expanded 4th generation UCS Fabric Interconnect with 108 ports.<br>  - unknown - Unknown device type, usage is TBD.<br>* network\_connectivity\_policy - Name of the Network Connectivity Policy to assign to the Profile.<br>* ntp\_policy - Name of the Network Connectivity Policy to assign to the Profile.<br>* organization - Name of the Intersight Organization to assign this Policy to.<br>  - https://intersight.com/an/settings/organizations/<br>* port\_policy\_fabric\_a - Name of the Port Policy to assign to Fabric A.<br>* port\_policy\_fabric\_b - Name of the Port Policy to assign to Fabric B.<br>* snmp\_policy - Name of the SNMP Policy to assign to the Profile.<br>* serial\_number\_fabric\_a - Serial Number for Fabric Interconnect A.<br>* serial\_number\_fabric\_b - Serial Number for Fabric Interconnect B.<br>* switch\_control\_policy - Name of the Switch Control Policy to assign to the Profile.<br>* syslog\_policy - Name of the Syslog Policy to assign to the Profile.<br>* system\_qos\_policy - Name of the System QoS Policy to assign to the Profile.<br>* tags - List of Key/Value Pairs to Assign as Attributes to the Policy.<br>* vlan\_policy\_fabric\_a - Name of the VLAN Policy to assign to Fabric A.<br>* vlan\_policy\_fabric\_b - Name of the VLAN Policy to assign to Fabric B.<br>* vsan\_policy\_fabric\_a - Name of the VSAN Policy to assign to Fabric A.<br>* vsan\_policy\_fabric\_b - Name of the VSAN Policy to assign to Fabric B. | <pre>map(object(<br>    {<br>      action                      = optional(string)<br>      assign_switches             = optional(bool)<br>      description                 = optional(string)<br>      device_model                = optional(string)<br>      network_connectivity_policy = optional(string)<br>      ntp_policy                  = optional(string)<br>      organization                = optional(string)<br>      port_policy_fabric_a        = optional(string)<br>      port_policy_fabric_b        = optional(string)<br>      snmp_policy                 = optional(string)<br>      serial_number_fabric_a      = optional(string)<br>      serial_number_fabric_b      = optional(string)<br>      switch_control_policy       = optional(string)<br>      syslog_policy               = optional(string)<br>      system_qos_policy           = optional(string)<br>      tags                        = optional(list(map(string)))<br>      vlan_policy_fabric_a        = optional(string)<br>      vlan_policy_fabric_b        = optional(string)<br>      vsan_policy_fabric_a        = optional(string)<br>      vsan_policy_fabric_b        = optional(string)<br>    }<br>  ))</pre> | <pre>{<br>  "default": {<br>    "action": "No-op",<br>    "assign_switches": false,<br>    "description": "",<br>    "device_model": "UCS-FI-6454",<br>    "network_connectivity_policy": "",<br>    "ntp_policy": "",<br>    "organization": "",<br>    "port_policy_fabric_a": "",<br>    "port_policy_fabric_b": "",<br>    "serial_number_fabric_a": "",<br>    "serial_number_fabric_b": "",<br>    "snmp_policy": "",<br>    "switch_control_policy": "",<br>    "syslog_policy": "",<br>    "system_qos_policy": "",<br>    "tags": [],<br>    "vlan_policy_fabric_a": "",<br>    "vlan_policy_fabric_b": "",<br>    "vsan_policy_fabric_a": "",<br>    "vsan_policy_fabric_b": ""<br>  }<br>}</pre> | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_moids"></a> [moids](#output\_moids) | n/a |
| <a name="output_ucs_domain_profiles"></a> [ucs\_domain\_profiles](#output\_ucs\_domain\_profiles) | n/a |
<!-- END OF PRE-COMMIT-TERRAFORM DOCS HOOK -->
