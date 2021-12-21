#______________________________________________
#
# Power Policy Variables
#______________________________________________

power_policies = {
  "5108" = {
    allocated_budget    = 0
    description         = "5108 Power Policy"
    power_profiling     = "Enabled"
    power_restore_state = "LastState"
    redundancy_mode     = "Grid"
    organization        = "dennis_demo"
    tags                = []
  }
  "9508" = {
    allocated_budget    = 5600
    description         = "9508 Power Policy"
    power_profiling     = "Enabled"
    power_restore_state = "LastState"
    redundancy_mode     = "Grid"
    organization        = "dennis_demo"
    tags                = []
  }
  "Server" = {
    allocated_budget    = 0
    description         = "Server Power Policy"
    power_profiling     = "Enabled"
    power_restore_state = "LastState"
    redundancy_mode     = "Grid"
    organization        = "dennis_demo"
    tags                = []
  }
}