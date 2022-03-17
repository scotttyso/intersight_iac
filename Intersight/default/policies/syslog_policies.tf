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
  * remote_clients - Enables configuration lockout on the endpoint.
  * tags - List of Key/Value Pairs to Assign as Attributes to the Policy.
  EOT
  type = map(object(
    {
      description        = optional(string)
      local_min_severity = optional(string)
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

resource "intersight_syslog_policy" "syslog_policies" {
  depends_on = [
    local.org_moid,
    local.ucs_domain_policies
  ]
  for_each    = local.syslog_policies
  description = each.value.description != "" ? each.value.description : "${each.key} Syslog Policy"
  name        = each.key
  local_clients {
    min_severity = each.value.local_min_severity
    object_type  = "syslog.LocalFileLoggingClient"
  }
  organization {
    moid        = local.org_moid
    object_type = "organization.Organization"
  }
  dynamic "profiles" {
    for_each = { for k, v in local.ucs_domain_policies : k => v if local.ucs_domain_policies[k].syslog_policy == each.key }
    content {
      moid        = profiles.value.moid
      object_type = profiles.value.object_type
    }
  }
  dynamic "remote_clients" {
    for_each = each.value.remote_clients
    content {
      enabled      = remote_clients.value.enabled
      hostname     = remote_clients.value.hostname
      port         = remote_clients.value.port
      protocol     = remote_clients.value.protocol
      min_severity = remote_clients.value.min_severity
      object_type  = "syslog.RemoteLoggingClient"
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
