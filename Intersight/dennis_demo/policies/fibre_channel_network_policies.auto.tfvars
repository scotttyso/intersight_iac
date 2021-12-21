#______________________________________________
#
# Fibre-Channel Network Policy Variables
#______________________________________________

fibre_channel_network_policies = {
  "Fabric-A" = {
    default_vlan_id = 0
    description     = "Fabric-A Fibre-Channel Network Policy"
    organization    = "dennis_demo"
    vsan_id         = 100
    tags            = []
  }
  "Fabric-B" = {
    default_vlan_id = 0
    description     = "Fabric-B Fibre-Channel Network Policy"
    organization    = "dennis_demo"
    vsan_id         = 200
    tags            = []
  }
}