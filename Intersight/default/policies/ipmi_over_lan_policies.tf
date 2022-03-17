#_________________________________________________________________________
#
# Intersight IPMI over LAN Policies Variables
# GUI Location: Configure > Policies > Create Policy > IPMI over LAN
#_________________________________________________________________________

variable "ipmi_key_1" {
  default     = ""
  description = "Encryption key 1 to use for IPMI communication. It should have an even number of hexadecimal characters and not exceed 40 characters."
  sensitive   = true
  type        = string
}

variable "ipmi_over_lan_policies" {
  default = {
    default = {
      description = ""
      enabled     = true
      ipmi_key    = null
      privilege   = "admin"
      tags        = []
    }
  }
  description = <<-EOT
  key - Name of the IPMI over LAN Policy.
  * description - Description to Assign to the Policy.
  * enabled - Flag to Enable or Disable the Policy.
  * ipmi_key - If null then encryption will not be applied.  If the value is set to 1 it will apply the ipmi_key_1 value.
  * privilege - The highest privilege level that can be assigned to an IPMI session on a server.
    - admin - Privilege to perform all actions available through IPMI.
    - user - Privilege to perform some functions through IPMI but restriction on performing administrative tasks.
    - read-only - Privilege to view information throught IPMI but restriction on making any changes.
  * tags - List of Key/Value Pairs to Assign as Attributes to the Policy.
  EOT
  type = map(object(
    {
      description = optional(string)
      enabled     = optional(bool)
      ipmi_key    = optional(number)
      privilege   = optional(string)
      tags        = optional(list(map(string)))
    }
  ))
}


#_________________________________________________________________________
#
# IPMI over LAN Policies
# GUI Location: Configure > Policies > Create Policy > IPMI over LAN
#_________________________________________________________________________

resource "intersight_ipmioverlan_policy" "ipmi_over_lan_policies" {
  depends_on = [
    local.org_moid
  ]
  for_each       = local.ipmi_over_lan_policies
  description    = each.value.description != "" ? each.value.description : "${each.key} IPMI over LAN Policy"
  enabled        = each.value.enabled
  encryption_key = each.value.ipmi_key == 1 ? var.ipmi_key_1 : null
  name           = each.key
  privilege      = each.value.privilege
  organization {
    moid        = local.org_moid
    object_type = "organization.Organization"
  }
  dynamic "tags" {
    for_each = length(each.value.tags) > 0 ? each.value.tags : local.tags
    content {
      key   = tags.value.key
      value = tags.value.value
    }
  }
}
