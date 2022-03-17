#______________________________________________
#
# VLAN Policy Variables
#______________________________________________

vlan_policies = {
  "iac_vlans" = {
    description = "2-30"
    tags        = []
    vlans = {
      "1" = {
        auto_allow_on_uplinks = false
        vlan_list             = "2-30",
        multicast_policy      = "iac_multicast",
        name                  = "iac",
        native_vlan           = false
      },
    }
  }
}