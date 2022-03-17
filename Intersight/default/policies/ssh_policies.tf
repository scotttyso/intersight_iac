#_________________________________________________________________________
#
# Intersight SSH Policies Variables
# GUI Location: Configure > Policies > Create Policy > SSH > Start
#_________________________________________________________________________

variable "ssh_policies" {
  default = {
    default = {
      description = ""
      enable_ssh  = true
      ssh_port    = 22
      ssh_timeout = 1800
      tags        = []
    }
  }
  description = <<-EOT
  key - Name of the SSH Policy.
  * description - Description to Assign to the Policy.
  * enable_ssh - State of SSH service on the endpoint.
  * ssh_port - Port used for secure shell access.  Valid range is between 1-65535.
  * ssh_timeout - Number of seconds to wait before the system considers a SSH request to have timed out.  Valid range is between 60-10800.
  * tags - List of Key/Value Pairs to Assign as Attributes to the Policy.
  EOT
  type = map(object(
    {
      description = optional(string)
      enable_ssh  = optional(bool)
      ssh_port    = optional(number)
      ssh_timeout = optional(number)
      tags        = optional(list(map(string)))
    }
  ))
}


#_________________________________________________________________________
#
# SSH Policies
# GUI Location: Configure > Policies > Create Policy > SSH > Start
#_________________________________________________________________________

resource "intersight_ssh_policy" "ssh_policies" {
  depends_on = [
    local.org_moid
  ]
  for_each    = local.ssh_policies
  description = each.value.description != "" ? each.value.description : "${each.key} SSH Policy"
  enabled     = each.value.enable_ssh
  name        = each.key
  port        = each.value.ssh_port
  timeout     = each.value.ssh_timeout
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
