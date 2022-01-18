#_________________________________________________________________________
#
# Intersight VSAN Policies Variables
# GUI Location: Configure > Policies > Create Policy > VSAN
#_________________________________________________________________________

variable "vsan_policies" {
  default = {
    default = {
      description     = ""
      organization    = "default"
      tags            = []
      uplink_trunking = false
      vsans = {
        default = {
          default_zoning       = "Disabled"
          fc_zone_sharing_mode = ""
          fcoe_vlan_id         = null
          name                 = "vsan"
          vsan_id              = null
          vsan_scope           = "Uplink"
        }
      }
    }
  }
  description = <<-EOT
  key - Name of the VSAN Policy.
  * description - Description to Assign to the Policy.
  * organization - Name of the Intersight Organization to assign this Policy to.
    - https://intersight.com/an/settings/organizations/
  * tags - List of Key/Value Pairs to Assign as Attributes to the Policy.
  * uplink_trunking - Default is false.  Enable or Disable Trunking on all of configured FC uplink ports.
  * vsans - List of VSANs to add to the VSAN Policy.
    - default_zoning - Enables or Disables the default zoning state.
      1. Enabled - Admin configured Enabled State.
      2. Disabled (Default) - Admin configured Disabled State.
    - fc_zone_sharing_mode - Logical grouping mode for fc ports.  Not used at this time.
    - fcoe_vlan_id - (REQUIRED).  FCoE VLAN Identifier to Assign to the VSAN Policy.
    - name - Name for the VSAN.
    - vsan_id - (REQUIRED).  VSAN Identifier to Assign to the VSAN Policy.
    - vsan_scope - Used to indicate whether the VSAN Id is defined for storage or uplink or both traffics in FI.
      * Uplink (Default) - Vsan associated with uplink network.
      * Storage - Vsan associated with storage network.
      * Common - Vsan that is common for uplink and storage network.
  EOT
  type = map(object(
    {
      description     = optional(string)
      organization    = optional(string)
      tags            = optional(list(map(string)))
      uplink_trunking = optional(bool)
      vsans = optional(map(object(
        {
          default_zoning       = optional(string)
          fc_zone_sharing_mode = optional(string)
          fcoe_vlan_id         = number
          name                 = string
          vsan_id              = number
          vsan_scope           = optional(string)
        }
      )))
    }
  ))
}


#_________________________________________________________________________
#
# VSAN Policies
# GUI Location: Configure > Policies > Create Policy > VSAN
#_________________________________________________________________________


resource "intersight_fabric_fc_network_policy" "vsan_policies" {
  depends_on = [
    local.org_moids,
    local.ucs_domain_policies
  ]
  for_each        = var.vsan_policies
  description     = each.value.description != "" ? each.value.description : "${each.key} VSAN Policy"
  enable_trunking = each.value.uplink_trunking
  name            = each.key
  organization {
    moid        = local.org_moids[each.value.organization].moid
    object_type = "organization.Organization"
  }
  dynamic "profiles" {
    for_each = { for k, v in local.ucs_domain_policies : k => v if local.ucs_domain_policies[k].vsan_policy == each.key }
    content {
      moid        = profiles.value.moid
      object_type = profiles.value.object_type
    }
  }
  dynamic "tags" {
    for_each = length(each.value.tags) > 0 ? each.value.tags : local.tags
    content {
      key   = tags.value.key
      value = tags.value.value
    }
  }
}


#______________________________________________
#
# Assign VSANs to VSAN Policies
#______________________________________________

resource "intersight_fabric_vsan" "vsans" {
  depends_on = [
    local.org_moids,
    intersight_fabric_fc_network_policy.vsan_policies
  ]
  for_each             = local.vsans
  default_zoning       = each.value.default_zoning
  fcoe_vlan            = each.value.fcoe_vlan_id
  fc_zone_sharing_mode = each.value.fc_zone_sharing_mode
  name                 = each.value.name
  vsan_id              = each.value.vsan_id
  vsan_scope           = each.value.vsan_scope
  fc_network_policy {
    moid = intersight_fabric_fc_network_policy.vsan_policies[each.value.vsan_policy].moid
  }
}
