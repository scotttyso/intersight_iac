#______________________________________________
#
# VLAN Policy Variables
#______________________________________________

vlan_policies = {
  "dennis-ucs" = {
    description  = "dennis-ucs VLAN Policy"
    organization = "dennis_demo"
    tags            = []
    vlans = {
      "1" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1-99",
        multicast_policy      = "dennis-ucs",
        name                  = "dennis-ucs",
        native_vlan           = false
      },
    }
  }
}