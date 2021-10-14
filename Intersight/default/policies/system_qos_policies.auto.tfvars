#______________________________________________
#
# System QoS Policy Variables
#______________________________________________

system_qos_policies = {
  "asgard-ucs_qos" = {
    classes = {
      "Platinum" = {
        bandwidth_percent  = 20
        cos                = 5
        mtu                = 9216
        packet_drop        = false
        state              = "Enabled"
        weight             = 10
      },
      "Gold" = {
        bandwidth_percent  = 19
        cos                = 4
        mtu                = 9216
        packet_drop        = true
        state              = "Enabled"
        weight             = 9
      },
      "FC" = {
        bandwidth_percent  = 21
        cos                = 3
        mtu                = 2240
        packet_drop        = false
        state              = "Enabled"
        weight             = 10
      },
      "Silver" = {
        bandwidth_percent  = 16
        cos                = 2
        mtu                = 9216
        packet_drop        = true
        state              = "Enabled"
        weight             = 8
      },
      "Bronze" = {
        bandwidth_percent  = 14
        cos                = 1
        mtu                = 9216
        packet_drop        = true
        state              = "Enabled"
        weight             = 7
      },
      "Best Effort" = {
        bandwidth_percent  = 10
        cos                = 255
        mtu                = 9216
        packet_drop        = true
        state              = "Enabled"
        weight             = 5
      },
    }
    description  = ""
    organization = "default"
    tags         = []
  }
}