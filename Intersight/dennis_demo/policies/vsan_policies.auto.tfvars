#______________________________________________
#
# VSAN Policy Variables
#______________________________________________

vsan_policies = {
  "dennis-ucs-A" = {
    description     = "dennis-ucs-A VSAN Policy"
    organization    = "dennis_demo"
    uplink_trunking = false
    tags            = []
    vsans = {
      "1" = {
        fcoe_vlan_id   = 100
        name           = "dennis-ucs-a"
        vsan_id        = 100
      },
    }
  }
  "dennis-ucs-B" = {
    description     = "dennis-ucs-B VSAN Policy"
    organization    = "dennis_demo"
    uplink_trunking = false
    tags            = []
    vsans = {
      "1" = {
        fcoe_vlan_id   = 200
        name           = "dennis-ucs-b"
        vsan_id        = 200
      },
    }
  }
}