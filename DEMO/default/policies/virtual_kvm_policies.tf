#_________________________________________________________________________
#
# Intersight Virtual KVM Policies Variables
# GUI Location: Configure > Policies > Create Policy > Virtual KVM
#_________________________________________________________________________

variable "virtual_kvm_policies" {
  default = {
    default = {
      description               = ""
      enable_local_server_video = true
      enable_video_encryption   = true
      enable_virtual_kvm        = true
      maximum_sessions          = 4
      organization              = "default"
      remote_port               = 2068
      tags                      = []
    }
  }
  description = <<-EOT
  key - Name of the Virtual KVM Policy.
  * description - Description to Assign to the Policy.
  * enable_local_server_video - Default is true.  If enabled, displays KVM session on any monitor attached to the server.
  * enable_video_encryption - Default is true.  If enabled, encrypts all video information sent through KVM.
  * enable_virtual_kvm - Default is true.  Flag to Enable or Disable the Policy.
  * maximum_sessions - Default is 4.  The maximum number of concurrent KVM sessions allowed. Range is 1 to 4.
  * organization - Name of the Intersight Organization to assign this Policy to.
    - https://intersight.com/an/settings/organizations/
  * remote_port - Default is 2068.  The port used for KVM communication. Range is 1 to 65535.
  * tags - List of Key/Value Pairs to Assign as Attributes to the Policy.
  EOT
  type = map(object(
    {
      description               = optional(string)
      enable_local_server_video = optional(bool)
      enable_video_encryption   = optional(bool)
      enable_virtual_kvm        = optional(bool)
      maximum_sessions          = optional(number)
      organization              = optional(string)
      remote_port               = optional(number)
      tags                      = optional(list(map(string)))
    }
  ))
}


#_________________________________________________________________________
#
# Virtual KVM Policies
# GUI Location: Configure > Policies > Create Policy > Virtual KVM
#_________________________________________________________________________

resource "intersight_kvm_policy" "virtual_kvm_policies" {
  depends_on = [
    local.org_moids
  ]
  for_each                  = local.virtual_kvm_policies
  description               = each.value.description != "" ? each.value.description : "${each.key} Virtual KVM Policy"
  enable_local_server_video = each.value.enable_local_server_video
  enable_video_encryption   = each.value.enable_video_encryption
  enabled                   = each.value.enable_virtual_kvm
  maximum_sessions          = each.value.maximum_sessions
  name                      = each.key
  remote_port               = each.value.remote_port
  organization {
    moid        = local.org_moids[each.value.organization].moid
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
