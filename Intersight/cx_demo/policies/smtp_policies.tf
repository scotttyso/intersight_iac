#_________________________________________________________________________
#
# Intersight SMTP Policies Variables
# GUI Location: Configure > Policies > Create Policy > SMTP > Start
#_________________________________________________________________________

variable "smtp_policies" {
  default = {
    default = {
      description               = ""
      enable_smtp               = true
      mail_alert_recipients     = []
      minimum_severity          = "critical"
      organization              = "default"
      smtp_alert_sender_address = ""
      smtp_port                 = 25
      smtp_server_address       = ""
      tags                      = []
    }
  }
  description = <<-EOT
  key - Name of the SMTP Policy.
  * description - Description to Assign to the Policy.
  * enable_smtp - If enabled, controls the state of the SMTP client service on the managed device.
  * mail_alert_recipients - List of Emails to send alerts to.
  * minimum_severity - Minimum fault severity level to receive email notifications. Email notifications are sent for all faults whose severity is equal to or greater than the chosen level.
    - critical - Minimum severity to report is critical.
    - condition - Minimum severity to report is informational.
    - warning - Minimum severity to report is warning.
    - minor - Minimum severity to report is minor.
    - major - Minimum severity to report is major.
  * organization - Name of the Intersight Organization to assign this Policy to.
    - https://intersight.com/an/settings/organizations/
  * smtp_alert_sender_address - The email address entered here will be displayed as the from address (mail received from address) of all the SMTP mail alerts that are received. If not configured, the hostname of the server is used in the from address field.
  * smtp_port - Port number used by the SMTP server for outgoing SMTP communication.  Valid range is between 1-65535.
  * smtp_server_address - IP address or hostname of the SMTP server. The SMTP server is used by the managed device to send email notifications.
  * tags - List of Key/Value Pairs to Assign as Attributes to the Policy.
  EOT
  type = map(object(
    {
      description               = optional(string)
      enable_smtp               = optional(bool)
      mail_alert_recipients     = optional(list(string))
      minimum_severity          = optional(string)
      organization              = optional(string)
      smtp_alert_sender_address = optional(string)
      smtp_port                 = optional(number)
      smtp_server_address       = optional(string)
      tags                      = optional(list(map(string)))
    }
  ))
}


#____________________________________________________________
#
# SMTP Policy
# GUI Location: Policies > Create Policy > SMTP
#____________________________________________________________

module "smtp_policies" {
  depends_on = [
    local.org_moids,
    local.merged_profile_policies,
  ]
  version                   = ">=0.9.6"
  source                    = "terraform-cisco-modules/imm/intersight//modules/smtp_policies"
  for_each                  = local.smtp_policies
  description               = each.value.description != "" ? each.value.description : "${each.key} SMTP Policy."
  enable_smtp               = each.value.enable_smtp
  mail_alert_recipients     = each.value.mail_alert_recipients
  minimum_severity          = each.value.minimum_severity
  name                      = each.key
  org_moid                  = local.org_moids[each.value.organization].moid
  smtp_alert_sender_address = each.value.smtp_alert_sender_address
  smtp_server_address       = each.value.smtp_server_address
  tags                      = length(each.value.tags) > 0 ? each.value.tags : local.tags
  profiles = {
    for k, v in local.merged_profile_policies : k => {
      moid        = v.moid
      object_type = v.object_type
    }
    if local.merged_profile_policies[k].smtp_policy == each.key
  }
}


