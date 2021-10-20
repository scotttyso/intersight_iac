#__________________________________________________________________________
#
# Intersight iSCSI Static Target Policy Variables
# GUI Location: Configure > Policies > Create Policy > iSCSI Static Target
#__________________________________________________________________________

variable "iscsi_static_target_policies" {
  default = {
    default = {
      description = ""
      ip_address  = "**REQUIRED**"
      lun = [
        {
          bootable = true
          lun_id   = null
        }
      ]
      organization = "default"
      port         = null
      tags         = []
      target_name  = "**REQUIRED**"
    }
  }
  description = <<-EOT
  key - Name of the iSCSI Adapter Policy.
  * description - Description to Assign to the Policy.
  * ip_address - Required Attribute.  The IPv4 address assigned to the iSCSI target.
  * lun - Required Attribute.  The LUN parameters associated with an iSCSI target. This complex property has following sub-properties:
    - bootable - Default is true.  Flag to specify if the LUN is bootable.
    - lun_id - The Identifier of the LUN.
  * organization - Name of the Intersight Organization to assign this Policy to.
    - https://intersight.com/an/settings/organizations/
  * port - Required Attribute.  The port associated with the iSCSI target.
  * tags - List of Key/Value Pairs to Assign as Attributes to the Policy.
  * target_name - Required Attribute.  Qualified Name (IQN) or Extended Unique Identifier (EUI) name of the iSCSI target.
  EOT
  type = map(object(
    {
      description = optional(string)
      ip_address  = string
      lun = list(object(
        {
          bootable = optional(bool)
          lun_id   = number
        }
      ))
      organization = optional(string)
      port         = number
      tags         = optional(list(map(string)))
      target_name  = string
    }
  ))
}


#__________________________________________________________________________
#
# iSCSI Static Target Policies
# GUI Location: Configure > Policies > Create Policy > iSCSI Static Target
#__________________________________________________________________________

module "iscsi_static_target_policies" {
  depends_on = [
    local.org_moids
  ]
  source      = "terraform-cisco-modules/imm/intersight//modules/iscsi_static_target_policies"
  for_each    = var.iscsi_static_target_policies
  description = each.value.description != "" ? each.value.description : "${each.key} iSCSI Adapter Policy."
  ip_address  = each.value.ip_address
  lun         = each.value.lun != null ? each.value.lun : []
  org_moid    = local.org_moids[each.value.organization].moid
  port        = each.value.port
  tags        = length(each.value.tags) > 0 ? each.value.tags : local.tags
  target_name = each.value.target_name
}
