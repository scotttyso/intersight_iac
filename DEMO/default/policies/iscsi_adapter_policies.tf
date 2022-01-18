#_________________________________________________________________________
#
# Intersight iSCSI Adapter Policy Variables
# GUI Location: Configure > Policies > Create Policy > iSCSI Adapter
#_________________________________________________________________________

variable "iscsi_adapter_policies" {
  default = {
    default = {
      description            = ""
      dhcp_timeout           = 60
      lun_busy_retry_count   = 15
      organization           = "default"
      tags                   = []
      tcp_connection_timeout = 15
    }
  }
  description = <<-EOT
  key - Name of the iSCSI Adapter Policy.
  * description - Description to Assign to the Policy.
  * dhcp_timeout - Default is 60.  The number of seconds to wait before the initiator assumes that the DHCP server is unavailable.  Range is 60-300.
  * lun_busy_retry_count - Default is 15.  The number of times to retry the connection in case of a failure during iSCSI LUN discovery.  Range is 0-60.
  * organization - Name of the Intersight Organization to assign this Policy to.
    - https://intersight.com/an/settings/organizations/
  * tags - List of Key/Value Pairs to Assign as Attributes to the Policy.
  * tcp_connection_timeout - Default is 15.  The number of seconds to wait until Cisco UCS assumes that the initial login has failed and the iSCSI adapter is unavailable.  Range is 0-255.
  EOT
  type = map(object(
    {
      description            = optional(string)
      dhcp_timeout           = optional(number)
      lun_busy_retry_count   = optional(number)
      organization           = optional(string)
      tags                   = optional(list(map(string)))
      tcp_connection_timeout = optional(number)
    }
  ))
}


#_________________________________________________________________________
#
# iSCSI Adapter Policies
# GUI Location: Configure > Policies > Create Policy > iSCSI Adapter
#_________________________________________________________________________

resource "intersight_vnic_iscsi_adapter_policy" "iscsi_adapter_policies" {
  depends_on = [
    local.org_moids
  ]
  for_each             = var.iscsi_adapter_policies
  connection_time_out  = each.value.tcp_connection_timeout != null ? each.value.tcp_connection_timeout : 15
  description          = each.value.description != null ? each.value.description : "${each.key} iSCSI Adapter Policy"
  dhcp_timeout         = each.value.dhcp_timeout != null ? each.value.dhcp_timeout : 60
  lun_busy_retry_count = each.value.lun_busy_retry_count != null ? each.value.lun_busy_retry_count : 15
  name                 = each.key
  organization {
    moid        = each.value.organization != null ? local.org_moids[each.value.organization].moid : local.org_moids["default"].moid
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
