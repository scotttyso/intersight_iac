#______________________________________________
#
# Ethernet Network Control Policy Variables
#______________________________________________

ethernet_network_control_policies = {
  "UCS-DEMO2_appliance" = {
    action_on_uplink_fail = "linkDown"
    cdp_enable            = false
    description           = ""
    lldp_enable_receive   = true
    lldp_enable_transmit  = true
    mac_register_mode     = "nativeVlanOnly"
    mac_security_forge    = "allow"
    organization          = "UCS-DEMO2"
    tags = [
      {
        key = "easyucs_origin",
        value = "convert",
      },
      {
        key = "easyucs_version",
        value = "0.9.8",
      },
    ]
  }
  "ncp-appliance_appliance" = {
    action_on_uplink_fail = "linkDown"
    cdp_enable            = true
    description           = ""
    lldp_enable_receive   = true
    lldp_enable_transmit  = true
    mac_register_mode     = "nativeVlanOnly"
    mac_security_forge    = "allow"
    organization          = "UCS-DEMO2"
    tags = [
      {
        key = "easyucs_origin",
        value = "convert",
      },
      {
        key = "easyucs_version",
        value = "0.9.8",
      },
    ]
  }
  "CDP-enable" = {
    action_on_uplink_fail = "linkDown"
    cdp_enable            = true
    description           = ""
    lldp_enable_receive   = false
    lldp_enable_transmit  = false
    mac_register_mode     = "nativeVlanOnly"
    mac_security_forge    = "allow"
    organization          = "UCS-DEMO2"
    tags = [
      {
        key = "easyucs_origin",
        value = "convert",
      },
      {
        key = "easyucs_version",
        value = "0.9.8",
      },
    ]
  }
  "CDP-LLDP-ENABLE" = {
    action_on_uplink_fail = "linkDown"
    cdp_enable            = true
    description           = ""
    lldp_enable_receive   = true
    lldp_enable_transmit  = true
    mac_register_mode     = "nativeVlanOnly"
    mac_security_forge    = "allow"
    organization          = "UCS-DEMO2"
    tags = [
      {
        key = "easyucs_origin",
        value = "convert",
      },
      {
        key = "easyucs_version",
        value = "0.9.8",
      },
    ]
  }
  "default" = {
    action_on_uplink_fail = "linkDown"
    cdp_enable            = false
    description           = ""
    lldp_enable_receive   = false
    lldp_enable_transmit  = false
    mac_register_mode     = "nativeVlanOnly"
    mac_security_forge    = "allow"
    organization          = "UCS-DEMO2"
    tags = [
      {
        key = "easyucs_origin",
        value = "convert",
      },
      {
        key = "easyucs_version",
        value = "0.9.8",
      },
    ]
  }
  "Enable-CDP-LLDP" = {
    action_on_uplink_fail = "linkDown"
    cdp_enable            = true
    description           = ""
    lldp_enable_receive   = true
    lldp_enable_transmit  = true
    mac_register_mode     = "nativeVlanOnly"
    mac_security_forge    = "allow"
    organization          = "UCS-DEMO2"
    tags = [
      {
        key = "easyucs_origin",
        value = "convert",
      },
      {
        key = "easyucs_version",
        value = "0.9.8",
      },
    ]
  }
}