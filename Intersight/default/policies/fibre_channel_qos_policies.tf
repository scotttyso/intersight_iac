#____________________________________________________________
#
# Fibre Channel QoS Policy
# GUI Location: Policies > Create Policy > Fibre Channel QoS
#____________________________________________________________

variable "fibre_channel_qos_policies" {
  default = {
    default = {
      burst               = 1024
      cos                 = 3
      description         = ""
      max_data_field_size = 2112
      rate_limit          = 0
      tags                = []
    }
  }
  description = <<-EOT
  key - Name of the Ethernet QoS Policy
  * burst - Default is 1024.  The burst traffic, in bytes, allowed on the vHBA.  Value can be between 1024-1000000.
  * cos - Default is 3.  Class of Service to be associated to the traffic on the virtual interface.  Value can be between 0-6.
  * description - Description for the Policy.
  * max_data_field_size - Default is 2112.  The maximum size of the Fibre Channel frame payload bytes that the virtual interface supports.
  * rate_limit - Default is 0.  The value in Mbps (0-10G/40G/100G depending on Adapter Model) to use for limiting the data rate on the virtual interface. Setting this to zero will turn rate limiting off.  Range is between 0-100000.
  * tags - Default is [].  List of Key/Value Pairs to Assign as Attributes to the Policy.
  EOT
  type = map(object(
    {
      burst               = optional(number)
      cos                 = optional(number)
      description         = optional(string)
      max_data_field_size = optional(number)
      rate_limit          = optional(number)
      tags                = optional(list(map(string)))
    }
  ))
}

#_______________________________________________________________________________
#
# Fibre-Channel QoS Policies
# GUI Location: Configure > Policies > Create Policy > Fibre-Channel QoS
#_______________________________________________________________________________

resource "intersight_vnic_fc_qos_policy" "fibre_channel_qos_policies" {
  depends_on = [
    local.org_moid
  ]
  for_each            = local.fibre_channel_qos_policies
  burst               = each.value.burst # FIAttached
  cos                 = each.value.cos   # Standalone
  description         = each.value.description != "" ? each.value.description : "${each.key} vHBA QoS Policy"
  max_data_field_size = each.value.max_data_field_size # FIAttached and Standalone
  name                = each.key
  rate_limit          = each.value.rate_limit # FIAttached and Standalone
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
