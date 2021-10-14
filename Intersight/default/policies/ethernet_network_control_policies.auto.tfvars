#______________________________________________
#
# Ethernet Network Control Policy Variables
#______________________________________________

ethernet_network_control_policies = {
  "Asgard_netwk_ctrl" = {
    action_on_uplink_fail = "linkDown"
    cdp_enable            = true
    description           = "Asgard_netwk_ctrl Ethernet Network Control Policy"
    lldp_enable_receive   = true
    lldp_enable_transmit  = true
    mac_register_mode     = "nativeVlanOnly"
    mac_security_forge    = "allow"
    organization          = "default"
    tags                  = []
  }
}