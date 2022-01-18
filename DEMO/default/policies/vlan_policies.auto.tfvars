#______________________________________________
#
# VLAN Policy Variables
#______________________________________________

vlan_policies = {
  "demo-ucs" = {
    description  = "demo-ucs VLAN Policy"
    organization = "default"
    tags            = []
    vlans = {
      "1" = {
        auto_allow_on_uplinks = 
        vlan_list             = "1",
        multicast_policy      = "demo-ucs",
        name                  = "default",
        native_vlan           = true
      },
      "2" = {
        auto_allow_on_uplinks = false
        vlan_list             = "2-99,101-199,201-299",
        multicast_policy      = "demo-ucs",
        name                  = "demo-ucs",
        native_vlan           = false
      },
    }
  }
}