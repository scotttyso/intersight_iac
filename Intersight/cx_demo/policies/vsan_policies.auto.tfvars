#______________________________________________
#
# VSAN Policy Variables
#______________________________________________

vsan_policies = {
  "asgard-ucs-A" = {
    description     = "asgard-ucs-A VSAN Policy"
    organization    = "cx_demo"
    uplink_trunking = false
    tags            = []
    vsans = {
      "1" = {
        fcoe_vlan_id = 100
        name         = "asgard-ucs-a"
        vsan_id      = 100
      },
    }
  }
  "asgard-ucs-B" = {
    description     = "asgard-ucs-B VSAN Policy"
    organization    = "cx_demo"
    uplink_trunking = false
    tags            = []
    vsans = {
      "1" = {
        fcoe_vlan_id = 200
        name         = "asgard-ucs-b"
        vsan_id      = 200
      },
    }
  }
}