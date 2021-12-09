#______________________________________________
#
# Switch Control Policy Variables
#______________________________________________

switch_control_policies = {
  "asgard-ucs" = {
    description                  = ""
    mac_address_table_aging      = "Default"
    mac_aging_time               = 14500
    organization                 = "canada"
    udld_message_interval        = 15
    udld_recovery_action         = "reset"
    vlan_port_count_optimization = false
    tags                         = []
  }
}