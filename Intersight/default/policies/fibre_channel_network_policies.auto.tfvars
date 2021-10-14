#______________________________________________
#
# Fibre-Channel Network Policy Variables
#______________________________________________

fibre_channel_network_policies = {
  "Asgard_A" = {
    default_vlan_id = 0
    description     = "Asgard_A Fibre-Channel Network Policy"
    organization    = "default"
    vsan_id         = 100
    tags            = []
  }
  "Asgard_B" = {
    default_vlan_id = 0
    description     = "Asgard_B Fibre-Channel Network Policy"
    organization    = "default"
    vsan_id         = 200
    tags            = []
  }
}