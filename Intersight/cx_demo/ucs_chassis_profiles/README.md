# ucs_chassis_profiles - Intersight UCS Chassis Profiles Deployment Module

## Use this module to create UCS Chassis Profiles in Intersight

## Usage

```hcl
module "ucs_chassis_profiles" {

  source = "terraform-cisco-modules/easy-imm/intersight//modules/ucs_chassis_profiles"

  # omitted...
}
```

This module will create UCS Chassis Profiles in Intersight.  

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
| <a name="module_ucs_chassis_profiles"></a> [ucs\_chassis\_profiles](#module\_ucs\_chassis\_profiles) | terraform-cisco-modules/imm/intersight//modules/ucs_chassis_profiles | >=0.9.6 |

## Resources

| Name | Type |
|------|------|
| [intersight_equipment_chassis.chassis](https://registry.terraform.io/providers/CiscoDevNet/intersight/latest/docs/data-sources/equipment_chassis) | data source |
| [intersight_organization_organization.org_moid](https://registry.terraform.io/providers/CiscoDevNet/intersight/latest/docs/data-sources/organization_organization) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_apikey"></a> [apikey](#input\_apikey) | Intersight API Key. | `string` | n/a | yes |
| <a name="input_endpoint"></a> [endpoint](#input\_endpoint) | Intersight URL. | `string` | `"https://intersight.com"` | no |
| <a name="input_organizations"></a> [organizations](#input\_organizations) | Intersight Organization Names. | `set(string)` | <pre>[<br>  "default"<br>]</pre> | no |
| <a name="input_secretkey"></a> [secretkey](#input\_secretkey) | Intersight Secret Key. | `string` | n/a | yes |
| <a name="input_tags"></a> [tags](#input\_tags) | List of Key/Value Pairs to Assign as Attributes to the Policy. | `list(map(string))` | `[]` | no |
| <a name="input_ucs_chassis_profiles"></a> [ucs\_chassis\_profiles](#input\_ucs\_chassis\_profiles) | key - Name for the Chassis.<br>* action - Action to Perform on the Chassis Profile Assignment.  Options are:<br>  - Deploy<br>  - No-op<br>  - Unassign<br>* assign\_chassis - Set flag to True to Assign the Profile to a Physical Chassis Serial Number.<br>* description - Description for the Profile.<br>* imc\_access\_policy - Name of the IMC Access Policy to Assign.<br>* organization - Name of the Intersight Organization to assign this Profile to.  Default is default.<br>  -  https://intersight.com/an/settings/organizations/<br>* power\_policy - Name of the Power Policy to Assign.<br>* serial\_number - Serial Number of the Chassis to Assign.<br>* snmp\_policy - Name of the SNMP Policy to Assign.<br>* tags - List of Key/Value Pairs to Assign as Attributes to the Policy.<br>* target\_platform - The platform for which the chassis profile is applicable. It can either be a chassis that is operating in standalone mode or which is attached to a Fabric Interconnect managed by Intersight.<br>  - FIAttached - Chassis which are connected to a Fabric Interconnect that is managed by Intersight.<br>* thermal\_policy - Name of the Thermal Policy to Assign.<br>* wait\_for\_completion - | <pre>map(object(<br>    {<br>      action              = optional(string)<br>      assign_chassis      = optional(bool)<br>      description         = optional(string)<br>      imc_access_policy   = optional(string)<br>      organization        = optional(string)<br>      power_policy        = optional(string)<br>      serial_number       = optional(string)<br>      snmp_policy         = optional(string)<br>      target_platform     = optional(string)<br>      thermal_policy      = optional(string)<br>      tags                = optional(list(map(string)))<br>      wait_for_completion = optional(bool)<br>    }<br>  ))</pre> | <pre>{<br>  "default": {<br>    "action": "No-op",<br>    "assign_chassis": false,<br>    "description": "",<br>    "imc_access_policy": "",<br>    "organization": "default",<br>    "power_policy": "",<br>    "serial_number": "",<br>    "snmp_policy": "",<br>    "tags": [],<br>    "target_platform": "FIAttached",<br>    "thermal_policy": "",<br>    "wait_for_completion": false<br>  }<br>}</pre> | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_moids"></a> [moids](#output\_moids) | n/a |
| <a name="output_ucs_chassis_profiles"></a> [ucs\_chassis\_profiles](#output\_ucs\_chassis\_profiles) | n/a |
<!-- END OF PRE-COMMIT-TERRAFORM DOCS HOOK -->
