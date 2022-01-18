#______________________________________________
#
# Local User Policy Variables
#______________________________________________

local_user_policies = {
  "default" = {
    always_send_user_password = false
    description               = "default Local User Policy"
    enable_password_expiry    = false
    enforce_strong_password   = true
    grace_period              = 0
    notification_period       = 15
    organization              = "default"
    password_expiry_duration  = 90
    password_history          = 5
    local_users               = {}
    tags                      = []
  }
}