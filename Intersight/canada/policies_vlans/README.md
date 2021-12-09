# Intersight UCS VLAN Policy Deployment Module

## Use this module to Assign VLANs to a VLAN Policy in Intersight

## Usage

```hcl
module "profiles_domains_vlans" {

  source = "terraform-cisco-modules/easy-imm/intersight//modules/profiles_domains_vlans"

  # omitted...
}
```

This module will Create a Multicast Policy and assign it to VLANs in a VLAN policy.  

<!-- BEGINNING OF PRE-COMMIT-TERRAFORM DOCS HOOK -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_intersight"></a> [intersight](#requirement\_intersight) | >=1.0.17 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_intersight"></a> [intersight](#provider\_intersight) | >=1.0.17 |
| <a name="provider_terraform"></a> [terraform](#provider\_terraform) | n/a |

## Modules

| Name | Source | Version |
|------|--------|---------|
| <a name="module_multicast_policies"></a> [multicast\_policies](#module\_multicast\_policies) | terraform-cisco-modules/imm/intersight//modules/multicast_policies | >=0.9.6 |
| <a name="module_vlan_policies"></a> [vlan\_policies](#module\_vlan\_policies) | terraform-cisco-modules/imm/intersight//modules/vlan_policies | >=0.9.6 |
| <a name="module_vlan_policies_add_vlans"></a> [vlan\_policies\_add\_vlans](#module\_vlan\_policies\_add\_vlans) | terraform-cisco-modules/imm/intersight//modules/vlan_policy_add_vlan_list | >=0.9.6 |

## Resources

| Name | Type |
|------|------|
| [intersight_organization_organization.org_moid](https://registry.terraform.io/providers/CiscoDevNet/intersight/latest/docs/data-sources/organization_organization) | data source |
| [terraform_remote_state.domain](https://registry.terraform.io/providers/hashicorp/terraform/latest/docs/data-sources/remote_state) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_apikey"></a> [apikey](#input\_apikey) | Intersight API Key. | `string` | n/a | yes |
| <a name="input_endpoint"></a> [endpoint](#input\_endpoint) | Intersight URL. | `string` | `"https://intersight.com"` | no |
| <a name="input_multicast_policies"></a> [multicast\_policies](#input\_multicast\_policies) | key - Name of the Multicast Policy.<br>* description - Description to Assign to the Policy.<br>* organization - Name of the Intersight Organization to assign this Policy to.<br>  - https://intersight.com/an/settings/organizations/<br>* querier\_ip\_address - IP Address of the IGMP Querier to Assign to the VLAN through this Policy.<br>* querier\_ip\_address\_peer - Used to define the IGMP Querier IP address of the peer switch.<br>* querier\_state - Administrative state of the IGMP Querier for the VLANs Assigned to this Policy.  Options are:<br>  - Disabled - (Default)<br>  - Enabled<br>* snooping\_state - Administrative State for Snooping for the VLANs Assigned to this Policy.<br>  - Disabled<br>  - Enabled - (Default)<br>* tags - List of Key/Value Pairs to Assign as Attributes to the Policy. | <pre>map(object(<br>    {<br>      description             = optional(string)<br>      organization            = optional(string)<br>      querier_ip_address      = optional(string)<br>      querier_ip_address_peer = optional(string)<br>      querier_state           = optional(string)<br>      snooping_state          = optional(string)<br>      tags                    = optional(list(map(string)))<br>    }<br>  ))</pre> | <pre>{<br>  "default": {<br>    "description": "",<br>    "organization": "default",<br>    "querier_ip_address": "",<br>    "querier_ip_address_peer": "",<br>    "querier_state": "Disabled",<br>    "snooping_state": "Enabled",<br>    "tags": []<br>  }<br>}</pre> | no |
| <a name="input_organizations"></a> [organizations](#input\_organizations) | Intersight Organization Names. | `set(string)` | <pre>[<br>  "default"<br>]</pre> | no |
| <a name="input_secretkey"></a> [secretkey](#input\_secretkey) | Intersight Secret Key. | `string` | n/a | yes |
| <a name="input_tags"></a> [tags](#input\_tags) | List of Key/Value Pairs to Assign as Attributes to the Policy. | `list(map(string))` | `[]` | no |
| <a name="input_tfc_organization"></a> [tfc\_organization](#input\_tfc\_organization) | Terraform Cloud Organization Name. | `string` | n/a | yes |
| <a name="input_vlan_policies"></a> [vlan\_policies](#input\_vlan\_policies) | key - Name of the VLAN Policy.<br>* description - Description to Assign to the Policy.<br>* organization - Name of the Intersight Organization to assign this Policy to.<br>  - https://intersight.com/an/settings/organizations/<br>* tags - List of Key/Value Pairs to Assign as Attributes to the Policy.<br>* vlans - List of VSANs to add to the VSAN Policy.<br>  - auto\_allow\_on\_uplinks - Default is false.  Used to determine whether this VLAN will be allowed on all uplink ports and PCs in this FI.<br>  - multicast\_policy - Name of the Multicast Policy to assign to the VLAN.<br>  - name - The 'name' used to identify this VLAN.  When configuring a single VLAN this will be used as the Name.  When configuring multiple VLANs in a list the name will be used as a Name Prefix.<br>  - native\_vlan - Default is false.  Used to define whether this VLAN is to be classified as 'native' for traffic in this FI.<br>  - vlan\_list - (REQUIRED).  The identifier for this Virtual LAN.  This can either be one vlan like "10" or a list of VLANs: "1,10,20-30". | <pre>map(object(<br>    {<br>      description  = optional(string)<br>      organization = optional(string)<br>      tags         = optional(list(map(string)))<br>      vlans = optional(map(object(<br>        {<br>          auto_allow_on_uplinks = optional(bool)<br>          multicast_policy      = string<br>          name                  = optional(string)<br>          native_vlan           = optional(bool)<br>          vlan_list             = string<br>        }<br>      )))<br>    }<br>  ))</pre> | <pre>{<br>  "default": {<br>    "description": "",<br>    "organization": "default",<br>    "tags": [],<br>    "vlans": {<br>      "default": {<br>        "auto_allow_on_uplinks": false,<br>        "multicast_policy": "",<br>        "name": "vlan-{vlan_id}",<br>        "native_vlan": false,<br>        "vlan_list": ""<br>      }<br>    }<br>  }<br>}</pre> | no |
| <a name="input_ws_ucs_domain_profiles"></a> [ws\_ucs\_domain\_profiles](#input\_ws\_ucs\_domain\_profiles) | Name of the UCS Domain Profiles workspace. | `string` | `"ucs_domain_profiles"` | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_merged_profile_policies"></a> [merged\_profile\_policies](#output\_merged\_profile\_policies) | n/a |
| <a name="output_ucs_domain_policies"></a> [ucs\_domain\_policies](#output\_ucs\_domain\_policies) | n/a |
| <a name="output_ucs_domain_switches"></a> [ucs\_domain\_switches](#output\_ucs\_domain\_switches) | n/a |
<!-- END OF PRE-COMMIT-TERRAFORM DOCS HOOK -->
