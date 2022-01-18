#_________________________________________________________________________
#
# Intersight NTP Policies Variables
# GUI Location: Configure > Policies > Create Policy > NTP > Start
#_________________________________________________________________________

variable "ntp_policies" {
  default = {
    default = {
      description  = ""
      enabled      = true
      ntp_servers  = ["time-a-g.nist.gov", "time-b-g.nist.gov"]
      organization = "default"
      tags         = []
      timezone     = "Etc/GMT"
    }
  }
  description = <<-EOT
  key - Name of the NTP Policy.
  * description - Description to Assign to the Policy.
  * enabled - Flag to Enable or Disable the Policy.
  * ntp_servers - List of NTP Servers to Assign to the Policy.
  * organization - Name of the Intersight Organization to assign this Policy to.
    - https://intersight.com/an/settings/organizations/
  * tags - List of Key/Value Pairs to Assign as Attributes to the Policy.
  * timezone - Timezone to Assign to the Policy.  For a List of supported timezones see the following URL.
    - https://github.com/terraform-cisco-modules/terraform-intersight-imm/blob/master/modules/policies_ntp/README.md.
  EOT
  type = map(object(
    {
      description  = optional(string)
      enabled      = optional(bool)
      ntp_servers  = optional(set(string))
      organization = optional(string)
      tags         = optional(list(map(string)))
      timezone     = optional(string)
    }
  ))
}


#_________________________________________________________________________
#
# NTP Policies
# GUI Location: Configure > Policies > Create Policy > NTP > Start
#_________________________________________________________________________

resource "intersight_ntp_policy" "ntp_policies" {
  depends_on = [
    local.org_moids,
    local.ucs_domain_policies
  ]
  for_each    = local.ntp_policies
  description = each.value.description != "" ? each.value.description : "${each.key} NTP Policy"
  enabled     = each.value.enabled
  name        = each.key
  ntp_servers = each.value.ntp_servers
  timezone    = each.value.timezone
  organization {
    moid        = local.org_moids[each.value.organization].moid
    object_type = "organization.Organization"
  }
  # dynamic "authenticated_ntp_servers" {
  #   for_each = each.value.authenticated_ntp_servers
  #   content {
  #     key_type      = "SHA1"
  #     object_type   = authenticated_ntp_servers.value.object_type
  #     server_name   = authenticated_ntp_servers.value.server_name
  #     sym_key_id    = authenticated_ntp_servers.value.sym_key_id
  #     sym_key_value = authenticated_ntp_servers.value.sym_key_value
  #   }
  # }
  dynamic "profiles" {
    for_each = { for k, v in local.ucs_domain_policies : k => v if local.ucs_domain_policies[k].ntp_policy == each.key }
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
