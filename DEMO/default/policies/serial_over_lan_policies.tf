#_________________________________________________________________________
#
# Intersight Serial over LAN Policies Variables
# GUI Location: Configure > Policies > Create Policy > Serial over LAN
#_________________________________________________________________________

variable "serial_over_lan_policies" {
  default = {
    default = {
      baud_rate    = 115200
      com_port     = "com0"
      description  = ""
      enabled      = true
      organization = "default"
      ssh_port     = 2400
      tags         = []
    }
  }
  description = <<-EOT
  key - Name of the Serial over LAN Policy.
  * baud_rate - Baud Rate to Assign to the Policy.  Options are:
    - 9600
    - 19200
    - 38400
    - 57600
    - 115200
  * com_port - Communications Port to Assign to the Policy.  Options are:
    - com0
    - com1
  * description - Description to Assign to the Policy.
  * enabled - Flag to Enable or Disable the Policy.
  * organization - Name of the Intersight Organization to assign this Policy to.
    - https://intersight.com/an/settings/organizations/
  * ssh_port - SSH Port to Assign to the Policy.  Range is between 1024-65535.
  * tags - List of Key/Value Pairs to Assign as Attributes to the Policy.
  EOT
  type = map(object(
    {
      baud_rate    = optional(number)
      com_port     = optional(string)
      description  = optional(string)
      enabled      = optional(bool)
      organization = optional(string)
      ssh_port     = optional(number)
      tags         = optional(list(map(string)))
    }
  ))
}


#_________________________________________________________________________
#
# Serial over LAN Policies
# GUI Location: Configure > Policies > Create Policy > Serial over LAN
#_________________________________________________________________________

resource "intersight_sol_policy" "serial_over_lan_policies" {
  depends_on = [
    local.org_moids
  ]
  for_each    = local.serial_over_lan_policies
  baud_rate   = each.value.baud_rate
  com_port    = each.value.com_port
  description = each.value.description
  enabled     = each.value.enabled
  name        = each.key
  ssh_port    = each.value.ssh_port
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
