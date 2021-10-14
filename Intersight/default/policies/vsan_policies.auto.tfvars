#______________________________________________
#
# VSAN Policy Variables
#______________________________________________

vsan_policies = {
  "asgard-ucs_A" = {
    description     = "asgard-ucs_A VSAN Policy"
    organization    = "default"
    uplink_trunking = false
    tags            = []
    vsans = {
      "1" = {
        fcoe_vlan_id   = 100
        name           = "VSAN-A"
        vsan_id        = 100
      },
    }
  }
  "asgard-ucs_B" = {
    description     = "asgard-ucs_B VSAN Policy"
    organization    = "default"
    uplink_trunking = false
    tags            = []
    vsans = {
      "1" = {
        fcoe_vlan_id   = 200
        name           = "VSAN-B"
        vsan_id        = 200
      },
    }
  }
}