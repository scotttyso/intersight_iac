#_________________________________________________________________________
#
# Intersight Syslog Policies Variables
# GUI Location: Configure > Policies > Create Policy > Syslog > Start
#_________________________________________________________________________

variable "syslog_policies" {
  default = {
    default = {
      description        = ""
      local_min_severity = "warning"
      organization       = "default"
      remote_clients     = []
      tags               = []
    }
  }
  description = <<-EOT
  key - Name of the Syslog Policy.
  * description - Description to Assign to the Policy.
  * local_min_severity - Lowest level of messages to be included in the local log.
    - warning - Use logging level warning for logs classified as warning.
    - emergency - Use logging level emergency for logs classified as emergency.
    - alert - Use logging level alert for logs classified as alert.
    - critical - Use logging level critical for logs classified as critical.
    - error - Use logging level error for logs classified as error.
    - notice - Use logging level notice for logs classified as notice.
    - informational - Use logging level informational for logs classified as informational.
    - debug - Use logging level debug for logs classified as debug.
  * organization - Name of the Intersight Organization to assign this Policy to.
    - https://intersight.com/an/settings/organizations/
  * remote_clients - Enables configuration lockout on the endpoint.
  * tags - List of Key/Value Pairs to Assign as Attributes to the Policy.
  EOT
  type = map(object(
    {
      description        = optional(string)
      local_min_severity = optional(string)
      organization       = optional(string)
      remote_clients     = optional(list(map(string)))
      tags               = optional(list(map(string)))
    }
  ))
}


#_________________________________________________________________________
#
# Syslog Policies
# GUI Location: Configure > Policies > Create Policy > Syslog > Start
#_________________________________________________________________________

module "syslog_policies" {
  depends_on = [
    local.org_moids,
    local.merged_profile_policies,
  ]
  version            = ">=0.9.6"
  source             = "terraform-cisco-modules/imm/intersight//modules/syslog_policies"
  for_each           = local.syslog_policies
  description        = each.value.description != "" ? each.value.description : "${each.key} Syslog Policy."
  name               = each.key
  org_moid           = local.org_moids[each.value.organization].moid
  remote_clients     = each.value.remote_clients
  local_min_severity = each.value.local_min_severity
  tags               = length(each.value.tags) > 0 ? each.value.tags : local.tags
  profiles = {
    for k, v in local.merged_profile_policies : k => {
      moid        = v.moid
      object_type = v.object_type
    }
    if local.merged_profile_policies[k].syslog_policy == each.key
  }
}
