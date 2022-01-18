#_________________________________________________________________________
#
# Intersight SD Card Policies Variables
# GUI Location: Configure > Policies > Create Policy > SMTP > Start
#_________________________________________________________________________

variable "sd_card_policies" {
  default = {
    default = {
      description        = ""
      enable_diagnostics = false
      enable_drivers     = false
      enable_huu         = false
      enable_os          = false
      enable_scu         = false
      organization       = "default"
      tags               = []
    }
  }
  description = <<-EOT
  key - Name of the SD Card Policy.
  * description - Description to Assign to the Policy.
  * When two cards are present in the Cisco FlexFlash controller and Operating System is chosen in the SD card policy, the configured OS partition is mirrored. If only single card is available in the Cisco FlexFlash controller, the configured OS partition is non-RAID. The utility partitions are always set as non-RAID.
  * Note:
    - This policy is not supported on M6 servers.
    - You can enable up to two utility virtual drives on M5 servers, and any number of supported utility virtual drives on M4 servers.
    - Diagnostics is supported only for the M5 servers.
    - UserPartition drives can be renamed only on the M4 servers.
    - FlexFlash configuration is not supported on C460 M4 servers.
    - For the Operating System+Utility mode, the M4 servers require two FlexFlash cards, and the M5 servers require at least 1 FlexFlash + 1 FlexUtil card.
  * enable_diagnostics - Flag to Enable the Diagnostics Utility Partition.
  * enable_drivers - Flag to Enable the Drivers Utility Partition.
  * enable_huu - Flag to Enable the HostUpgradeUtility Utility Partition.
  * enable_os - Flag to Enable the OperatingSystem Partition.
  * enable_scu - Flag to Enable the ServerConfigurationUtility Utility Partition.
  * organization - Name of the Intersight Organization to assign this Policy to.
    - https://intersight.com/an/settings/organizations/
  * tags - List of Key/Value Pairs to Assign as Attributes to the Policy.
  EOT
  type = map(object(
    {
      description        = optional(string)
      enable_diagnostics = optional(bool)
      enable_drivers     = optional(bool)
      enable_huu         = optional(bool)
      enable_os          = optional(bool)
      enable_scu         = optional(bool)
      organization       = optional(string)
      tags               = optional(list(map(string)))
    }
  ))
}


#____________________________________________________________
#
# SD Card Policy
# GUI Location: Policies > Create Policy > SD Card
#____________________________________________________________

# module "sd_card_policies" {
#   depends_on = [
#     local.org_moids
#   ]
#   version = ">=0.9.6"
#   source  = "terraform-cisco-modules/imm/intersight//modules/sd_card_policies"
#   for_each = {
#     for k, v in local.sd_card_policies : k => v
#     if v.enable_os == true && (v.enable_diagnostics == true || v.enable_drivers == true || v.enable_huu == true || v.enable_scu == true)
#   }
#   description        = each.value.description != "" ? each.value.description : "${each.key} SD Card Policy."
#   enable_diagnostics = each.value.enable_diagnostics
#   enable_drivers     = each.value.enable_drivers
#   enable_huu         = each.value.enable_huu
#   enable_os          = each.value.enable_os
#   enable_scu         = each.value.enable_scu
#   name               = each.key
#   org_moid           = local.org_moids[each.value.organization].moid
#   tags               = length(each.value.tags) > 0 ? each.value.tags : local.tags
# }

# module "sd_card_policies_os" {
#   depends_on = [
#     local.org_moids
#   ]
#   version = ">=0.9.6"
#   source  = "terraform-cisco-modules/imm/intersight//modules/sd_card_policies_os"
#   for_each = {
#     for k, v in local.sd_card_policies : k => v
#     if v.enable_os == true && v.enable_diagnostics == false && v.enable_drivers == false && v.enable_huu == false && v.enable_scu == false
#   }
#   description = each.value.description != "" ? each.value.description : "${each.key} SD Card Policy."
#   name        = each.key
#   org_moid    = local.org_moids[each.value.organization].moid
#   tags        = length(each.value.tags) > 0 ? each.value.tags : local.tags
# }
# 
# module "sd_card_policies_utiity" {
#   depends_on = [
#     local.org_moids
#   ]
#   version = ">=0.9.6"
#   source  = "terraform-cisco-modules/imm/intersight//modules/sd_card_policies_utility"
#   for_each = {
#     for k, v in local.sd_card_policies : k => v
#     if v.enable_os == false && (v.enable_diagnostics == true || v.enable_drivers == true || v.enable_huu == true || v.enable_scu == true)
#   }
#   description        = each.value.description != "" ? each.value.description : "${each.key} SD Card Policy."
#   enable_diagnostics = each.value.enable_diagnostics
#   enable_drivers     = each.value.enable_drivers
#   enable_huu         = each.value.enable_huu
#   enable_scu         = each.value.enable_scu
#   name               = each.key
#   org_moid           = local.org_moids[each.value.organization].moid
#   tags               = length(each.value.tags) > 0 ? each.value.tags : local.tags
# }
