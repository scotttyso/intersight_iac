#______________________________________________
#
# VLAN Policy Variables
#______________________________________________

vlan_policies = {
  "asgard-ucs" = {
    description  = "asgard-ucs VLAN Policy"
    organization = "canada"
    tags         = []
    vlans = {
      "1" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1-99",
        multicast_policy      = "asgard-ucs",
        name                  = "asgard-ucs",
        native_vlan           = false
      },
    }
  }
}