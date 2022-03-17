#______________________________________________
#
# VLAN Policy Variables
#______________________________________________

vlan_policies = {
  "iac" = {
    description = "iac VLAN Policy"
    tags        = []
    vlans = {
      "1" = {
        auto_allow_on_uplinks = false
        vlan_list             = "2-30",
        multicast_policy      = "iac",
        name                  = "iac",
        native_vlan           = false
      },
    }
  }
}