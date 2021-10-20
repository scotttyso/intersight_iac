#_________________________________________________________________________
#
# Intersight Virtual Media Policies Variables
# GUI Location: Configure > Policies > Create Policy > Virtual Media
#_________________________________________________________________________

variable "virtual_media_policies" {
  default = {
    default = {
      description                     = ""
      enable_low_power_usb            = false
      enable_virtual_media            = true
      enable_virtual_media_encryption = true
      organization                    = "default"
      tags                            = []
      vmedia_mappings                 = {}
    }
  }
  description = <<-EOT
  key - Name of the Virtual Media Policy.
  * description - Description to Assign to the Policy.
  * enable_low_power_usb - Default is false.  If enabled, the virtual drives appear on the boot selection menu after mapping the image and rebooting the host.
  * enable_virtual_media - Default is true.  Flag to Enable or Disable the Policy.
  * enable_virtual_media_encryption - Default is true.  If enabled, allows encryption of all Virtual Media communications.
  * organization - Name of the Intersight Organization to assign this Policy to.
    - https://intersight.com/an/settings/organizations/
  * tags - List of Key/Value Pairs to Assign as Attributes to the Policy.
  * vmedia_mappings - Virtual Media Maps
    Key - Name of the Virtual Media Mount
    - authentication_protocol - Type of Authentication protocol when CIFS is used for communication with the remote server.
      * none - (Default) No authentication is used.
      * ntlm - NT LAN Manager (NTLM) security protocol. Use this option only with Windows 2008 R2 and Windows 2012 R2.
      * ntlmi - NTLMi security protocol. Use this option only when you enable Digital Signing in the CIFS Windows server.
      * ntlmv2 - NTLMv2 security protocol. Use this option only with Samba Linux.
      * ntlmv2i - NTLMv2i security protocol. Use this option only with Samba Linux.
      * ntlmssp - NT LAN Manager Security Support Provider (NTLMSSP) protocol. Use this option only with Windows 2008 R2 and Windows 2012 R2.
      * ntlmsspi - NTLMSSPi protocol. Use this option only when you enable Digital Signing in the CIFS Windows server.
    - device_type - Type of remote Virtual Media device.
      * cdd - (Default) Uses compact disc drive as the virtual media mount device.
      * hdd - Uses hard disk drive as the virtual media mount device.
    - file_location - The remote file location path for the virtual media mapping. Accepted formats are:
      * HDD for CIFS/NFS: hostname-or-IP/filePath/fileName.img
      * CDD for CIFS/NFS: hostname-or-IP/filePath/fileName.iso
      * HDD for HTTP/S: http[s]://hostname-or-IP/filePath/fileName.img
      * CDD for HTTP/S: http[s]://hostname-or-IP/filePath/fileName.iso
    - mount_options - Mount options for the Virtual Media mapping. The field can be left blank or filled in a comma separated list with the following options.
      * For NFS, supported options are:
        - ro
        - rw
        - nolock
        - noexec
        - soft
        - port=VALUE
        - timeo=VALUE
        - retry=VALUE
      * For CIFS, supported options are:
        - soft
        - nounix
        - noserverino
        - guest
        Note: For CIFS version less than 3.0, vers=VALUE is mandatory. e.g. vers=2.0
      * For HTTP/HTTPS, the only supported option is:
        - noauto
    - password - A Number used in the loop to point to the variable "vmedia_password_[1-5]".  So 1 would be vmedia_password_1.  Sensitive Values are not supported in a loop
    - protocol - Protocol to use to communicate with the remote server.
      * nfs - NFS protocol for vmedia mount.
      * cifs - CIFS protocol for vmedia mount.
      * http - HTTP protocol for vmedia mount.
      * https - HTTPS protocol for vmedia mount.
    - username - Username to log in to the remote server, if authentication is enabled.
  EOT
  type = map(object(
    {
      description                     = optional(string)
      enable_low_power_usb            = optional(bool)
      enable_virtual_media            = optional(bool)
      enable_virtual_media_encryption = optional(bool)
      organization                    = optional(string)
      tags                            = optional(list(map(string)))
      vmedia_mappings = optional(map(object(
        {
          authentication_protocol = optional(string)
          device_type             = optional(string)
          file_location           = string
          mount_options           = optional(string)
          password                = optional(number)
          protocol                = optional(string)
          username                = optional(string)
        }
      )))
    }
  ))
}

variable "vmedia_password_1" {
  default     = ""
  description = "Password for vMedia "
  sensitive   = true
  type        = string
}

variable "vmedia_password_2" {
  default     = ""
  description = "Password for vMedia "
  sensitive   = true
  type        = string
}

variable "vmedia_password_3" {
  default     = ""
  description = "Password for vMedia "
  sensitive   = true
  type        = string
}

variable "vmedia_password_4" {
  default     = ""
  description = "Password for vMedia "
  sensitive   = true
  type        = string
}

variable "vmedia_password_5" {
  default     = ""
  description = "Password for vMedia "
  sensitive   = true
  type        = string
}

#_________________________________________________________________________
#
# Virtual Media Policies
# GUI Location: Configure > Policies > Create Policy > Virtual Media
#_________________________________________________________________________

module "virtual_media_policies" {
  depends_on = [
    local.org_moids,
    local.merged_profile_policies,
  ]
  source                          = "terraform-cisco-modules/imm/intersight//modules/virtual_media_policies"
  for_each                        = local.virtual_media_policies
  description                     = each.value.description != "" ? each.value.description : "${each.key} Virtual Media Policy."
  enable_virtual_media            = each.value.enable_virtual_media
  enable_virtual_media_encryption = each.value.enable_virtual_media_encryption
  enable_low_power_usb            = each.value.enable_low_power_usb
  name                            = each.key
  org_moid                        = local.org_moids[each.value.organization].moid
  tags                            = length(each.value.tags) > 0 ? each.value.tags : local.tags
  vmedia_mappings                 = each.value.vmedia_mappings
  vmedia_password_1               = var.vmedia_password_1
  vmedia_password_2               = var.vmedia_password_2
  vmedia_password_3               = var.vmedia_password_3
  vmedia_password_4               = var.vmedia_password_4
  vmedia_password_5               = var.vmedia_password_5
  profiles = {
    for k, v in local.merged_profile_policies : k => {
      moid        = v.moid
      object_type = v.object_type
    }
    if local.merged_profile_policies[k].virtual_media_policy == each.key
  }
}
