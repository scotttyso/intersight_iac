#_________________________________________________________________________
#
# Intersight Link Control Policies Variables
# GUI Location: Configure > Policy > Create Policy > Link Control
#_________________________________________________________________________

variable "link_control_policies" {
  default = {
    default = {
      admin_state = "Enabled"
      description = ""
      mode        = "normal"
      tags        = []
    }
  }
  description = <<-EOT
  key - Name of the Link Control Policy.
  * admin_state - Admin configured UDLD State for this port.
    - Disabled - Admin configured Disabled State.
    - Enabled - (Default) Admin configured Enabled State.
  * description - Description to Assign to the Policy.
  * mode - Admin configured UDLD Mode for this port.
    - normal - (Default) - Admin configured 'normal' UDLD mode.
    - aggressive - Admin configured 'aggressive' UDLD mode.
  * tags - List of Key/Value Pairs to Assign as Attributes to the Policy.
  EOT
  type = map(object(
    {
      admin_state = optional(string)
      description = optional(string)
      mode        = optional(string)
      tags        = optional(list(map(string)))
    }
  ))
}


#_________________________________________________________________________
#
# Link Control Policies
# GUI Location: Configure > Policy > Create Policy > Link Control
#_________________________________________________________________________

resource "intersight_fabric_link_control_policy" "link_control_policies" {
  depends_on = [
    local.org_moid
  ]
  for_each    = local.link_control_policies
  description = each.value.description != "" ? each.value.description : "${each.key} Link Control Policy"
  name        = each.key
  organization {
    moid        = local.org_moid
    object_type = "organization.Organization"
  }
  udld_settings {
    admin_state = each.value.admin_state
    mode        = each.value.mode
  }
  dynamic "tags" {
    for_each = length(each.value.tags) > 0 ? each.value.tags : local.tags
    content {
      key   = tags.value.key
      value = tags.value.value
    }
  }
}
