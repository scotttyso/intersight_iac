#______________________________________________
#
# Local User Policy Variables
#______________________________________________

local_user_policies = {
  "Asgard_local_users" = {
    always_send_user_password = false
    description               = "Asgard_local_users Local User Policy"
    enable_password_expiry    = true
    enforce_strong_password   = true
    grace_period              = 0
    notification_period       = 15
    organization              = "default"
    password_expiry_duration  = 90
    password_history          = 5
    tags         = []
    local_users = {
      "ciscouser" = {
        enabled = true
        password = 1
        role     = "admin"
      },
    }
  }
}