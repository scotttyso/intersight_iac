#_________________________________________________________________________
#
# Intersight iSCSI Boot Policy Variables
# GUI Location: Configure > Policies > Create Policy > iSCSI Boot
#_________________________________________________________________________

variable "iscsi_boot_password" {
  default     = ""
  description = "Password to Assign to the Policy if doing Authentication."
  sensitive   = true
  type        = string
}

variable "iscsi_boot_policies" {
  default = {
    default = {
      authentication      = ""
      dhcp_vendor_id_iqn  = ""
      description         = ""
      initiator_ip_pool   = ""
      initiator_ip_source = "Pool"
      initiator_static_ip_v4_config = {
        default_gateway = "If Configuring static field is **REQUIRED**"
        ip_address      = "If Configuring static field is **REQUIRED**"
        subnet_mask     = "If Configuring static field is **REQUIRED**"
        primary_dns     = ""
        secondary_dns   = ""
      }
      iscsi_adapter_policy    = ""
      password                = 0
      primary_target_policy   = ""
      organization            = "default"
      secondary_target_policy = ""
      target_source_type      = "Auto"
      tags                    = []
      username                = ""
    }
  }
  description = <<-EOT
  key - Name of the iSCSI Boot Policy.
  * Authentication - When using Authentication which type of authentication should be used.
    - chap - perform CHAP Authentication
    - mutual_chap - Perform Mutual CHAP Authentication.
  * chap - Defines the Authentication as CHAP Authentication
    - password - Chap Password Identifier. I.e. 1 would be for iscsi_boot_password.
    - user_id - Chap User Id, if doing chap authentication.
  * dhcp_vendor_id_iqn - Auto target interface that is represented via the Initiator name or the DHCP vendor ID. The vendor ID can be up to 32 alphanumeric characters.
  * description - Description to Assign to the Policy.
  * initiator_ip_pool - A reference to a ippoolPool resource.
  * initiator_ip_source - Default is Pool.  Source Type of Initiator IP Address - DHCP/Static/Pool.
    - DHCP - The IP address is assigned using DHCP, if available.
    - Static - Static IPv4 address is assigned to the iSCSI boot interface based on the information entered in this area.
    - Pool - An IPv4 address is assigned to the iSCSI boot interface from the management IP address pool.
  * initiator_static_ip_v4_config - When the Initiator IP source is Static, configure the Static IPv4 Parameters
    - default_gateway - IP address of the default IPv4 gateway.
    - ip_address -  Static IP address provided for iSCSI Initiator.
    - primary_dns - IP Address of the primary Domain Name System (DNS) server.
    - secondary_dns - IP Address of the secondary Domain Name System (DNS) server.
    - subnet_mask - A subnet mask is a 32-bit number that masks an IP address and divides the IP address into network address and host address.
  * iscsi_adapter_policy - The Name of the iSCSI Adapter Policy to Assign to the iSCSI Boot Policy.
  * mutual_chap - Defines the Authentication as CHAP Authentication
    - password - Mutual Chap Password Identifier. I.e. 1 would be for iscsi_boot_password.
    - user_id - Mutual Chap User Id.
  * organization - Name of the Intersight Organization to assign this Policy to.
    - https://intersight.com/an/settings/organizations/
  * password - If doing CHAP or Mutual Chap authentication set this to 1 and configure the iscsi_boot_password.
  * primary_target_policy - Name of the Primary iSCSI Static Target Policy to Associate to the iSCSI Boot Policy.
  * secondary_target_policy - Name of the Secondary iSCSI Static Target Policy to Associate to the iSCSI Boot Policy.
  * tags - List of Key/Value Pairs to Assign as Attributes to the Policy.
  * target_source_type - Default is Auto.  Source Type of Targets - Auto/Static.
    - Auto - Type indicates that the system selects the target interface automatically during iSCSI boot.
    - Static - Type indicates that static target interface is assigned to iSCSI boot.
  * username - username for either CHAP or Mutual Chap Authentication
  EOT
  type = map(object(
    {
      authentication      = optional(string)
      dhcp_vendor_id_iqn  = optional(string)
      description         = optional(string)
      initiator_ip_pool   = optional(string)
      initiator_ip_source = optional(string)
      initiator_static_ip_v4_config = optional(object(
        {
          default_gateway = string
          ip_address      = string
          subnet_mask     = string
          primary_dns     = optional(string)
          secondary_dns   = optional(string)
        }
      ))
      iscsi_adapter_policy    = optional(string)
      organization            = optional(string)
      password                = optional(number)
      primary_target_policy   = optional(string)
      secondary_target_policy = optional(string)
      tags                    = optional(list(map(string)))
      target_source_type      = optional(string)
      username                = optional(string)
    }
  ))
}


#_________________________________________________________________________
#
# iSCSI Boot Policies
# GUI Location: Configure > Policies > Create Policy > iSCSI Boot
#_________________________________________________________________________

module "iscsi_boot_policies" {
  depends_on = [
    data.terraform_remote_state.pools,
    local.org_moids,
    module.iscsi_adapter_policies,
    module.iscsi_static_target_policies,
  ]
  version                       = ">=0.9.6"
  source                        = "terraform-cisco-modules/imm/intersight//modules/iscsi_boot_policies"
  for_each                      = var.iscsi_boot_policies
  authentication                = each.value.authentication
  dhcp_vendor_id_iqn            = each.value.dhcp_vendor_id_iqn != null ? each.value.dhcp_vendor_id_iqn : ""
  description                   = each.value.description != null ? each.value.description : "${each.key} iSCSI Boot Policy."
  initiator_ip_source           = each.value.initiator_ip_source != null ? each.value.initiator_ip_source : ""
  initiator_static_ip_v4_config = each.value.initiator_static_ip_v4_config != null ? each.value.initiator_static_ip_v4_config : {}
  password                      = each.value.password == 1 ? var.iscsi_boot_password : ""
  username                      = each.value.username != null ? each.value.username : ""
  name                          = each.key
  primary_target_policy_moid = length(
    regexall("[a-zA-Z0-9]+", each.value.primary_target_policy)
  ) > 0 ? [module.iscsi_static_target_policies[each.value.primary_target_policy].moid] : []
  target_source_type = each.value.target_source_type != null ? each.value.target_source_type : "Auto"
  org_moid           = each.value.organization != null ? local.org_moids[each.value.organization].moid : local.org_moids["default"].moid
  tags               = each.value.tags != null ? each.value.tags : local.tags
  initiator_ip_pool = length(
    regexall("Pool", each.value.initiator_ip_source)
  ) > 0 ? [local.ip_pools[each.value.initiator_ip_pool]] : []
  iscsi_adapter_policy_moid = length(
    regexall("[a-zA-Z0-9]+", each.value.iscsi_adapter_policy)
  ) > 0 ? [module.iscsi_adapter_policies[each.value.iscsi_adapter_policy].moid] : []
  secondary_target_policy_moid = length(
    regexall("[a-zA-Z0-9]+", each.value.secondary_target_policy)
  ) > 0 ? [module.iscsi_static_target_policies[each.value.primary_target_policy].moid] : []
}
