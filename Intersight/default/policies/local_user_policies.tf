#_________________________________________________________________________
#
# Intersight Local User Policies Variables
# GUI Location: Configure > Policies > Create Policy > Local User > Start
#_________________________________________________________________________

variable "local_user_password_1" {
  default     = ""
  description = "Password to assign to a local user.  Sensitive Variables cannot be added to a for_each loop so these are added seperately."
  sensitive   = true
  type        = string
}

variable "local_user_password_2" {
  default     = ""
  description = "Password to assign to a local user.  Sensitive Variables cannot be added to a for_each loop so these are added seperately."
  sensitive   = true
  type        = string
}

variable "local_user_password_3" {
  default     = ""
  description = "Password to assign to a local user.  Sensitive Variables cannot be added to a for_each loop so these are added seperately."
  sensitive   = true
  type        = string
}

variable "local_user_password_4" {
  default     = ""
  description = "Password to assign to a local user.  Sensitive Variables cannot be added to a for_each loop so these are added seperately."
  sensitive   = true
  type        = string
}

variable "local_user_password_5" {
  default     = ""
  description = "Password to assign to a local user.  Sensitive Variables cannot be added to a for_each loop so these are added seperately."
  sensitive   = true
  type        = string
}

variable "local_user_policies" {
  default = {
    default = {
      always_send_user_password = false
      description               = ""
      enable_password_expiry    = false
      enforce_strong_password   = true
      grace_period              = 0
      notification_period       = 15
      organization              = "default"
      password_expiry_duration  = 90
      password_history          = 5
      tags                      = []
      users = {
        default = {
          enabled  = true
          password = 1
          role     = "admin"
        }
      }
    }
  }
  description = <<-EOT
  key - Name of the Local User Policy.
  * always_send_user_password - If the option is not set to true, user passwords will only be sent to endpoint devices for new users and if a user password is changed for existing users.
  * description - Description to Assign to the Policy.
  * enable_password_expiry - Enables password expiry on the endpoint.
  * enforce_strong_password - Enables a strong password policy. Strong password requirements:
    A. The password must have a minimum of 8 and a maximum of 20 characters.
    B. The password must not contain the User's Name.
    C. The password must contain characters from three of the following four categories.
      1. English uppercase characters (A through Z).
      2. English lowercase characters (a through z).
      3. Base 10 digits (0 through 9).
      4. Non-alphabetic characters (! , @, #, $, %, ^, &, *, -, _, +, =).
  * grace_period - Time, in days, after the password is expired that a user can continue to use their expired password.  The allowed grace period is between 0 to 5 days.  With 0 being no grace period.
  * notification_period - Number of days, between 0 to 15 (0 being disabled), that a user is notified to change their password before it expires.
  * organization - Name of the Intersight Organization to assign this Policy to.
    - https://intersight.com/an/settings/organizations/
  * password_expiry_duration - When Password Expiry is Enabled, this sets the duration of time (in days) a password may be valid.  The password expiry duration must be greater than notification period + grace period.  Range is 1-3650.
    Note:  The
  * password_history - Password change history. Specifies the number of previous passwords that are stored and compared to a new password.  Range is 0 to 5.
  * tags - List of Key/Value Pairs to Assign as Attributes to the Policy.
  * users - Map of users to add to the local user policy.
    - key - Username
    - enabled - Enables the user account on the endpoint.
    - password - This is a key to signify the variable "local_user_password_[key]" to be used.  i.e. 1 for variable "local_user_password_1".
    - role - The Role to Assign to the User.  Valid Options are {admin|readonly|user}.
  EOT
  type = map(object(
    {
      always_send_user_password = optional(bool)
      description               = optional(string)
      enable_password_expiry    = optional(bool)
      enforce_strong_password   = optional(bool)
      grace_period              = optional(number)
      notification_period       = optional(number)
      organization              = optional(string)
      password_expiry_duration  = optional(number)
      password_history          = optional(number)
      tags                      = optional(list(map(string)))
      users = optional(map(object(
        {
          enabled  = optional(bool)
          password = optional(number)
          role     = optional(string)
        }
      )))
    }
  ))
}


#_________________________________________________________________________
#
# Local User Policies
# GUI Location: Configure > Policies > Create Policy > Local User > Start
#_________________________________________________________________________

module "local_user_policies" {
  depends_on = [
    local.org_moids,
    local.merged_profile_policies,
  ]
  source                    = "terraform-cisco-modules/imm/intersight//modules/local_user_policies"
  for_each                  = local.local_user_policies
  always_send_user_password = each.value.always_send_user_password
  description               = each.value.description != "" ? each.value.description : "${each.key} Local User Policy."
  enable_password_expiry    = each.value.enable_password_expiry
  enforce_strong_password   = each.value.enforce_strong_password
  grace_period              = each.value.grace_period
  name                      = each.key
  notification_period       = each.value.notification_period
  org_moid                  = local.org_moids[each.value.organization].moid
  password_expiry_duration  = each.value.password_expiry_duration
  password_history          = each.value.password_history
  tags                      = length(each.value.tags) > 0 ? each.value.tags : local.tags
  profiles = {
    for k, v in local.merged_profile_policies : k => {
      moid        = v.moid
      object_type = v.object_type
    }
    if local.merged_profile_policies[k].local_user_policy == each.key
  }
}


#_________________________________________________________________________
#
# Local Users
# GUI Location: Configure > Policies > Create Policy > Local User > Start
#_________________________________________________________________________

module "local_users" {
  depends_on = [
    local.org_moids,
    module.local_user_policies
  ]
  for_each     = local.local_users.users
  source       = "terraform-cisco-modules/imm/intersight//modules/local_user_add_users"
  org_moid     = local.org_moids[each.value.organization].moid
  user_enabled = each.value.enabled
  user_password = length(
    regexall("^1$", each.value.password)
    ) > 0 ? var.local_user_password_1 : length(
    regexall("^2$", each.value.password)
    ) > 0 ? var.local_user_password_2 : length(
    regexall("^3$", each.value.password)
    ) > 0 ? var.local_user_password_3 : length(
    regexall("^4$", each.value.password)
  ) > 0 ? var.local_user_password_4 : var.local_user_password_5
  user_policy_moid = module.local_user_policies[each.value.policy].moid
  user_role        = each.value.role
  username         = each.value.username
}
