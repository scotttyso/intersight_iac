#_________________________________________________________________________
#
# Intersight Link Control Policies Variables
# GUI Location: Configure > Policy > Create Policy > Link Control
#_________________________________________________________________________

variable "link_control_policies" {
  default = {
    default = {
      admin_state  = "Enabled"
      description  = ""
      mode         = "normal"
      organization = "default"
      tags         = []
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
  * organization - Name of the Intersight Organization to assign this Policy to.
    - https://intersight.com/an/settings/organizations/
  * tags - List of Key/Value Pairs to Assign as Attributes to the Policy.
  EOT
  type = map(object(
    {
      admin_state  = optional(string)
      description  = optional(string)
      mode         = optional(string)
      organization = optional(string)
      tags         = optional(list(map(string)))
    }
  ))
}


#_________________________________________________________________________
#
# Link Control Policies
# GUI Location: Configure > Policy > Create Policy > Link Control
#_________________________________________________________________________

module "link_control_policies" {
  depends_on = [
    local.org_moids
  ]
  source           = "terraform-cisco-modules/imm/intersight//modules/link_control_policies"
  for_each         = local.link_control_policies
  description      = each.value.description != "" ? each.value.description : "${each.key} Link Control Policy."
  name             = each.key
  org_moid         = local.org_moids[each.value.organization].moid
  tags             = length(each.value.tags) > 0 ? each.value.tags : local.tags
  udld_admin_state = each.value.admin_state
  udld_mode        = each.value.mode
}

