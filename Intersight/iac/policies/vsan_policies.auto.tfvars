#______________________________________________
#
# VSAN Policy Variables
#______________________________________________

vsan_policies = {
  "iac-A" = {
    description     = "iac-A VSAN Policy"
    uplink_trunking = false
    tags            = []
    vsans = {
      "1" = {
        fcoe_vlan_id = 100
        name         = "iac-a"
        vsan_id      = 100
      },
    }
  }
  "iac-B" = {
    description     = "iac-B VSAN Policy"
    uplink_trunking = false
    tags            = []
    vsans = {
      "1" = {
        fcoe_vlan_id = 200
        name         = "iac-b"
        vsan_id      = 200
      },
    }
  }
}