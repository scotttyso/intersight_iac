#______________________________________________
#
# SMTP Policy Variables
#______________________________________________

smtp_policies = {
  "Asgard_smtp" = {
    description               = "Asgard_smtp SMTP Policy"
    enable_smtp               = true
    mail_alert_recipients = [
        "rich-lab@cisco.com",
    ]
    minimum_severity          = "critical"
    organization              = "default"
    smtp_alert_sender_address = "rich-lab@cisco.com"
    smtp_port                 = 25
    smtp_server_address       = "mail.rich.ciscolabs.com"
    tags         = []
  }
}