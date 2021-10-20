#_________________________________________________________________________
#
# Intersight SSH Policies Variables
# GUI Location: Configure > Policies > Create Policy > SSH > Start
#_________________________________________________________________________

variable "ssh_policies" {
  default = {
    default = {
      description  = ""
      enable_ssh   = true
      organization = "default"
      ssh_port     = 22
      ssh_timeout  = 1800
      tags         = []
    }
  }
  description = <<-EOT
  key - Name of the SSH Policy.
  * description - Description to Assign to the Policy.
  * enable_ssh - State of SSH service on the endpoint.
  * organization - Name of the Intersight Organization to assign this Policy to.
    - https://intersight.com/an/settings/organizations/
  * ssh_port - Port used for secure shell access.  Valid range is between 1-65535.
  * ssh_timeout - Number of seconds to wait before the system considers a SSH request to have timed out.  Valid range is between 60-10800.
  * tags - List of Key/Value Pairs to Assign as Attributes to the Policy.
  EOT
  type = map(object(
    {
      description  = optional(string)
      enable_ssh   = optional(bool)
      organization = optional(string)
      ssh_port     = optional(number)
      ssh_timeout  = optional(number)
      tags         = optional(list(map(string)))
    }
  ))
}


#_________________________________________________________________________
#
# SSH Policies
# GUI Location: Configure > Policies > Create Policy > SSH > Start
#_________________________________________________________________________

module "ssh_policies" {
  depends_on = [
    local.org_moids,
    local.merged_profile_policies,
  ]
  source      = "terraform-cisco-modules/imm/intersight//modules/ssh_policies"
  for_each    = local.ssh_policies
  description = each.value.description != "" ? each.value.description : "${each.key} SNMP Policy."
  enable_ssh  = each.value.enable_ssh
  name        = each.key
  org_moid    = local.org_moids[each.value.organization].moid
  ssh_port    = each.value.ssh_port
  ssh_timeout = each.value.ssh_timeout
  tags        = length(each.value.tags) > 0 ? each.value.tags : local.tags
  profiles = {
    for k, v in local.merged_profile_policies : k => {
      moid        = v.moid
      object_type = v.object_type
    }
    if local.merged_profile_policies[k].ssh_policy == each.key
  }
}
