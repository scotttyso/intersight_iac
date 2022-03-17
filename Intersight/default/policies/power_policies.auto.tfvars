#______________________________________________
#
# Power Policy Variables
#______________________________________________

power_policies = {
  "iac_9508" = {
    description               = "iac_9508 Power Policy"
    dynamic_power_rebalancing = Enabled
    power_allocation          = 5600
    power_priority            = "Low"
    power_profiling           = "Enabled"
    power_restore             = "LastState"
    power_redunancy           = "Grid"
    power_save_mode           = "Enabled"
    tags                      = []
  }
}