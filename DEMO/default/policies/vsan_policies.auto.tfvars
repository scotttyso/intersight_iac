#______________________________________________
#
# VSAN Policy Variables
#______________________________________________

vsan_policies = {
  "demo-ucs-A" = {
    description     = "demo-ucs-A VSAN Policy"
    organization    = "default"
    uplink_trunking = false
    tags            = []
    vsans = {
      "1" = {
        fcoe_vlan_id = 100
        name         = "demo-ucs-a"
        vsan_id      = 100
      },
    }
  }
  "demo-ucs-B" = {
    description     = "demo-ucs-B VSAN Policy"
    organization    = "default"
    uplink_trunking = false
    tags            = []
    vsans = {
      "1" = {
        fcoe_vlan_id = 200
        name         = "demo-ucs-b"
        vsan_id      = 200
      },
    }
  }
}