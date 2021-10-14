#______________________________________________
#
# VLAN Policy Variables
#______________________________________________

vlan_policies = {
  "asgard-ucs_vlans" = {
    description  = "asgard-ucs_vlans VLAN Policy"
    organization = "Asgard"
    tags            = []
    vlans = {
      "1" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1",
        multicast_policy      = "asgard-ucs_multicast",
        name                  = "default",
        native_vlan           = true
      },
      "2" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1-99,101-199,201-299",
        multicast_policy      = "asgard-ucs_multicast",
        name                  = "Asgard",
        native_vlan           = false
      },
    }
  }
}