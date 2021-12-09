#_________________________________________________________________________
#
# Intersight SNNMP Policies Variables
# GUI Location: Configure > Policies > Create Policy > SNMP > Start
#_________________________________________________________________________

variable "access_community_string_1" {
  default     = ""
  description = "The default SNMPv1, SNMPv2c community name or SNMPv3 username to include on any trap messages sent to the SNMP host. The name can be 18 characters long."
  sensitive   = true
  type        = string
}

variable "access_community_string_2" {
  default     = ""
  description = "The default SNMPv1, SNMPv2c community name or SNMPv3 username to include on any trap messages sent to the SNMP host. The name can be 18 characters long."
  sensitive   = true
  type        = string
}

variable "access_community_string_3" {
  default     = ""
  description = "The default SNMPv1, SNMPv2c community name or SNMPv3 username to include on any trap messages sent to the SNMP host. The name can be 18 characters long."
  sensitive   = true
  type        = string
}

variable "access_community_string_4" {
  default     = ""
  description = "The default SNMPv1, SNMPv2c community name or SNMPv3 username to include on any trap messages sent to the SNMP host. The name can be 18 characters long."
  sensitive   = true
  type        = string
}

variable "access_community_string_5" {
  default     = ""
  description = "The default SNMPv1, SNMPv2c community name or SNMPv3 username to include on any trap messages sent to the SNMP host. The name can be 18 characters long."
  sensitive   = true
  type        = string
}

variable "snmp_auth_password_1" {
  default     = ""
  description = "SNMPv3 User Authentication Password."
  sensitive   = true
  type        = string
}

variable "snmp_auth_password_2" {
  default     = ""
  description = "SNMPv3 User Authentication Password."
  sensitive   = true
  type        = string
}

variable "snmp_auth_password_3" {
  default     = ""
  description = "SNMPv3 User Authentication Password."
  sensitive   = true
  type        = string
}

variable "snmp_auth_password_4" {
  default     = ""
  description = "SNMPv3 User Authentication Password."
  sensitive   = true
  type        = string
}

variable "snmp_auth_password_5" {
  default     = ""
  description = "SNMPv3 User Authentication Password."
  sensitive   = true
  type        = string
}

variable "snmp_privacy_password_1" {
  default     = ""
  description = "SNMPv3 User Privacy Password."
  sensitive   = true
  type        = string
}

variable "snmp_privacy_password_2" {
  default     = ""
  description = "SNMPv3 User Privacy Password."
  sensitive   = true
  type        = string
}

variable "snmp_privacy_password_3" {
  default     = ""
  description = "SNMPv3 User Privacy Password."
  sensitive   = true
  type        = string
}

variable "snmp_privacy_password_4" {
  default     = ""
  description = "SNMPv3 User Privacy Password."
  sensitive   = true
  type        = string
}

variable "snmp_privacy_password_5" {
  default     = ""
  description = "SNMPv3 User Privacy Password."
  sensitive   = true
  type        = string
}

variable "snmp_community_string_1" {
  default     = ""
  description = "SNMP Trap Destination Community."
  sensitive   = true
  type        = string
}

variable "snmp_community_string_2" {
  default     = ""
  description = "SNMP Trap Destination Community."
  sensitive   = true
  type        = string
}

variable "snmp_community_string_3" {
  default     = ""
  description = "SNMP Trap Destination Community."
  sensitive   = true
  type        = string
}

variable "snmp_community_string_4" {
  default     = ""
  description = "SNMP Trap Destination Community."
  sensitive   = true
  type        = string
}

variable "snmp_community_string_5" {
  default     = ""
  description = "SNMP Trap Destination Community."
  sensitive   = true
  type        = string
}

variable "snmp_trap_community_1" {
  default     = ""
  description = "Community for a Trap Destination."
  sensitive   = true
  type        = string
}

variable "snmp_trap_community_2" {
  default     = ""
  description = "Community for a Trap Destination."
  sensitive   = true
  type        = string
}

variable "snmp_trap_community_3" {
  default     = ""
  description = "Community for a Trap Destination."
  sensitive   = true
  type        = string
}

variable "snmp_trap_community_4" {
  default     = ""
  description = "Community for a Trap Destination."
  sensitive   = true
  type        = string
}

variable "snmp_trap_community_5" {
  default     = ""
  description = "Community for a Trap Destination."
  sensitive   = true
  type        = string
}

variable "trap_community_string_1" {
  default     = ""
  description = "The default SNMPv1, SNMPv2c community name or SNMPv3 username to include on any trap messages sent to the SNMP host. The name can be 18 characters long."
  sensitive   = true
  type        = string
}

variable "trap_community_string_2" {
  default     = ""
  description = "The default SNMPv1, SNMPv2c community name or SNMPv3 username to include on any trap messages sent to the SNMP host. The name can be 18 characters long."
  sensitive   = true
  type        = string
}

variable "trap_community_string_3" {
  default     = ""
  description = "The default SNMPv1, SNMPv2c community name or SNMPv3 username to include on any trap messages sent to the SNMP host. The name can be 18 characters long."
  sensitive   = true
  type        = string
}

variable "trap_community_string_4" {
  default     = ""
  description = "The default SNMPv1, SNMPv2c community name or SNMPv3 username to include on any trap messages sent to the SNMP host. The name can be 18 characters long."
  sensitive   = true
  type        = string
}

variable "trap_community_string_5" {
  default     = ""
  description = "The default SNMPv1, SNMPv2c community name or SNMPv3 username to include on any trap messages sent to the SNMP host. The name can be 18 characters long."
  sensitive   = true
  type        = string
}

variable "snmp_policies" {
  default = {
    default = {
      access_community_string = 0
      description             = ""
      enable_snmp             = true
      organization            = "default"
      snmp_community_access   = "Full"
      snmp_engine_input_id    = ""
      snmp_port               = 161
      snmp_trap_destinations  = {}
      snmp_users              = {}
      system_contact          = ""
      system_location         = ""
      tags                    = []
      trap_community_string   = 0
    }
  }
  description = <<-EOT
  key - Name of the SNMP Policy.
  * access_community_string - Default is 0.  A number Between 1-5 to denote to use one of the variables access_community_string_[1-5].  Any other number means no community string.
  * description - Description to Assign to the Policy.
  * enable_snmp - State of the SNMP Policy on the endpoint. If enabled, the endpoint sends SNMP traps to the designated host.
  * organization - Name of the Intersight Organization to assign this Policy to.
    - https://intersight.com/an/settings/organizations/
  * snmp_community_access - Controls access to the information in the inventory tables. Applicable only for SNMPv1 and SNMPv2c.
    - Disabled - (Defualt) - Blocks access to the information in the inventory tables.
    - Full - Full access to read the information in the inventory tables.
    - Limited - Partial access to read the information in the inventory tables.
  * snmp_engine_input_id - Unique string to identify the device for administration purpose. This is generated from the SNMP Input Engine ID if it is already defined, else it is derived from the BMC serial number.
  * snmp_port - Port on which Cisco IMC SNMP agent runs. Enter a value between 1-65535. Reserved ports not allowed (22, 23, 80, 123, 389, 443, 623, 636, 2068, 3268, 3269).  Default is 161.
  * snmp_trap_destinations - List of SNMP Trap Destinations to Assign to the Policy.
    key - SNMP Trap Destination Address
    - community_string - Default is 0.  A number Between 1-5 to denote to use one of the variables snmp_auth_password_[1-5].  Any other number means no community string.
    - enable - Default is true.  Enables/disables the trap on the server If enabled, trap is active on the server.
    - port - Default is 162.  Port used by the server to communicate with the trap destination. Enter a value between 1-65535. Reserved ports not allowed (22, 23, 80, 123, 389, 443, 623, 636, 2068, 3268, 3269).
    - trap_type - Type of trap which decides whether to receive a notification when a trap is received at the destination.
      1. Inform - Receive notifications when trap is sent to the destination. This option is valid only for SNMPv2.
      2. Trap - Do not receive notifications when trap is sent to the destination.
    - user - SNMP user for the trap. Applicable only to SNMPv3.
  * snmp_users - List of SNMP Users to Assign to the SNMP Policy.
    key - Name of the SNMP User.
    - auth_password - Default is 0.  A number Between 1-5 to denote to use one of the variables snmp_auth_password_[1-5].  Any other number means no authentication password.
    - auth_type - Authorization protocol for authenticating the user.  Currently Options are:
      1. MD5
      2. SHA (Default)
    - Note: In the future these options will be added.
      1. NA - Authentication protocol is not applicable.
      2. SHA-224 - SHA-224 protocol is used to authenticate SNMP user.
      3. SHA-256 - SHA-256 protocol is used to authenticate SNMP user.
      4. SHA-384 - SHA-384 protocol is used to authenticate SNMP user.
      5. SHA-512 - SHA-512 protocol is used to authenticate SNMP user.
    - privacy_password - Default is 0.  A number Between 1-5 to denote to use one of the variables snmp_privacy_password_[1-5].  Any other number means no Privacy password.
    - privacy_type - Privacy protocol for the user.
      1. AES - AES privacy protocol is used for SNMP user.
      2. DES - DES privacy protocol is used for SNMP user.
      3. NA - Privacy protocol is not applicable.
    - security_level - Security mechanism used for communication between agent and manager.
      1. AuthNoPriv - The user requires an authorization password but not a privacy password.
      2. AuthPriv (Default) - The user requires both an authorization password and a privacy password.
      3. NoAuthNoPriv - The user does not require an authorization or privacy password.
  * system_contact - Contact person responsible for the SNMP implementation. Enter a string up to 64 characters, such as an email address or a name and telephone number.
  * system_location - Location of the host on which the SNMP agent (server) runs.
  * tags - List of Key/Value Pairs to Assign as Attributes to the Policy.
  * trap_community_string - Default is 0.  A number Between 1-5 to denote to use one of the variables trap_community_string_[1-5].  Any other number means no community string.
  EOT
  type = map(object(
    {
      access_community_string = optional(number)
      description             = optional(string)
      enable_snmp             = optional(bool)
      organization            = optional(string)
      snmp_community_access   = optional(string)
      snmp_engine_input_id    = optional(string)
      snmp_port               = optional(number)
      snmp_trap_destinations = optional(map(object(
        {
          community_string = optional(number)
          enable           = optional(bool)
          port             = optional(number)
          trap_type        = optional(string)
          user             = optional(string)
        }
      )))
      snmp_users = optional(map(object(
        {
          auth_password    = optional(number)
          auth_type        = optional(string)
          privacy_password = optional(number)
          privacy_type     = optional(string)
          security_level   = optional(string)
        }
      )))
      system_contact        = optional(string)
      system_location       = optional(string)
      tags                  = optional(list(map(string)))
      trap_community_string = optional(number)
    }
  ))
}

#____________________________________________________________
#
# SNMP Policy
# GUI Location: Policies > Create Policy > SNMP
#____________________________________________________________

module "snmp_policies" {
  depends_on = [
    local.org_moids,
    local.merged_profile_policies,
  ]
  version  = ">=0.9.6"
  source   = "terraform-cisco-modules/imm/intersight//modules/snmp_policies"
  for_each = local.snmp_policies
  access_community_string = length(
    regexall("1", each.value.access_community_string)
    ) > 0 ? var.access_community_string_1 : length(
    regexall("2", each.value.access_community_string)
    ) > 0 ? var.access_community_string_2 : length(
    regexall("3", each.value.access_community_string)
    ) > 0 ? var.access_community_string_3 : length(
    regexall("4", each.value.access_community_string)
    ) > 0 ? var.access_community_string_3 : length(
    regexall("5", each.value.access_community_string)
  ) > 0 ? var.access_community_string_5 : ""
  description             = each.value.description != "" ? each.value.description : "${each.key} SNMP Policy."
  enable_snmp             = each.value.enable_snmp
  name                    = each.key
  org_moid                = local.org_moids[each.value.organization].moid
  snmp_auth_password_1    = var.snmp_auth_password_1
  snmp_auth_password_2    = var.snmp_auth_password_2
  snmp_auth_password_3    = var.snmp_auth_password_3
  snmp_auth_password_4    = var.snmp_auth_password_4
  snmp_auth_password_5    = var.snmp_auth_password_5
  snmp_community_access   = each.value.snmp_community_access != "" ? each.value.snmp_community_access : "Disabled"
  snmp_engine_input_id    = each.value.snmp_engine_input_id
  snmp_port               = each.value.snmp_port
  snmp_privacy_password_1 = var.snmp_privacy_password_1
  snmp_privacy_password_2 = var.snmp_privacy_password_2
  snmp_privacy_password_3 = var.snmp_privacy_password_3
  snmp_privacy_password_4 = var.snmp_privacy_password_4
  snmp_privacy_password_5 = var.snmp_privacy_password_5
  snmp_trap_community_1   = var.snmp_trap_community_1
  snmp_trap_community_2   = var.snmp_trap_community_2
  snmp_trap_community_3   = var.snmp_trap_community_3
  snmp_trap_community_4   = var.snmp_trap_community_4
  snmp_trap_community_5   = var.snmp_trap_community_5
  snmp_trap_destinations  = each.value.snmp_trap_destinations
  snmp_users              = each.value.snmp_users
  system_contact          = each.value.system_contact
  system_location         = each.value.system_location
  tags                    = length(each.value.tags) > 0 ? each.value.tags : local.tags
  trap_community_string = length(
    regexall("1", each.value.trap_community_string)
    ) > 0 ? var.trap_community_string_1 : length(
    regexall("2", each.value.trap_community_string)
    ) > 0 ? var.trap_community_string_2 : length(
    regexall("3", each.value.trap_community_string)
    ) > 0 ? var.trap_community_string_3 : length(
    regexall("4", each.value.trap_community_string)
    ) > 0 ? var.trap_community_string_3 : length(
    regexall("5", each.value.trap_community_string)
  ) > 0 ? var.trap_community_string_5 : ""
  v2_enabled = length(regexall("[1-5]", each.value.access_community_string)) > 0 ? true : false
  v3_enabled = length(each.value.snmp_users) > 0 ? true : false
  profiles = {
    for k, v in local.merged_profile_policies : k => {
      moid        = v.moid
      object_type = v.object_type
    }
    if local.merged_profile_policies[k].snmp_policy == each.key
  }
}
