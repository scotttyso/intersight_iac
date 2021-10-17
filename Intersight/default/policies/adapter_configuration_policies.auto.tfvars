#______________________________________________
#
# Adapter Configuration Policy Variables
#______________________________________________

adapter_configuration_policies = {
  "Asgard_adapter" = {
    description         = "Asgard_adapter Adapter Configuration Policy"
    enable_fip          = true
    enable_lldp         = true
    enable_port_channel = true
    fec_mode_1          = "cl91"
    fec_mode_2          = "cl91"
    fec_mode_3          = "cl91"
    fec_mode_4          = "cl91"
    organization        = "default"
    tags                = []
  }
}