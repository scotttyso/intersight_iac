#______________________________________________
#
# System QoS Policy Variables
#______________________________________________

system_qos_policies = {
  "UCS-DEMO2" = {
    classes = {
      "Bronze" = {
        bandwidth_percent  = 0
        cos                = 1
        mtu                = 1500
        multicast_optimize = false
        packet_drop        = true
        state              = "Disabled"
        weight             = 7
      },
      "Gold" = {
        bandwidth_percent  = 0
        cos                = 4
        mtu                = 1500
        multicast_optimize = false
        packet_drop        = true
        state              = "Disabled"
        weight             = 9
      },
      "Platinum" = {
        bandwidth_percent  = 40
        cos                = 5
        mtu                = 2240
        multicast_optimize = false
        packet_drop        = false
        state              = "Enabled"
        weight             = 10
      },
      "Silver" = {
        bandwidth_percent  = 0
        cos                = 2
        mtu                = 1500
        multicast_optimize = false
        packet_drop        = true
        state              = "Disabled"
        weight             = 8
      },
      "FC" = {
        bandwidth_percent  = 40
        cos                = 3
        mtu                = 2240
        multicast_optimize = false
        packet_drop        = false
        state              = "Enabled"
        weight             = 10
      },
      "Best Effort" = {
        bandwidth_percent  = 20
        cos                = 255
        mtu                = 1500
        multicast_optimize = false
        packet_drop        = true
        state              = "Enabled"
        weight             = 5
      },
    }
    description  = ""
    organization = "UCS-DEMO2"
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