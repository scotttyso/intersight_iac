#______________________________________________
#
# Ethernet Network Group Policy Variables
#______________________________________________

ethernet_network_group_policies = {
  "MGMT" = {
    allowed_vlans = "1"
    description   = "MGMT Ethernet Network Group Policy"
    native_vlan   = 1
    organization  = "dennis_demo"
    tags          = []
  }
  "VMOTION" = {
    allowed_vlans = "1"
    description   = "VMOTION Ethernet Network Group Policy"
    native_vlan   = 1
    organization  = "dennis_demo"
    tags          = []
  }
  "STORAGE" = {
    allowed_vlans = "1"
    description   = "STORAGE Ethernet Network Group Policy"
    native_vlan   = 1
    organization  = "dennis_demo"
    tags          = []
  }
  "DATA" = {
    allowed_vlans = "1-99"
    description   = "DATA Ethernet Network Group Policy"
    organization  = "dennis_demo"
    tags          = []
  }
}