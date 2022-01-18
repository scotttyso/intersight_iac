#______________________________________________
#
# Ethernet Network Group Policy Variables
#______________________________________________

ethernet_network_group_policies = {
  "demo-ucs" = {
    allowed_vlans = "1-99,101-199,201-299"
    description   = "demo-ucs Ethernet Network Group Policy"
    organization  = "default"
    tags          = []
  }
  "MGMT" = {
    allowed_vlans = "1"
    description   = "MGMT Ethernet Network Group Policy"
    native_vlan   = 1
    organization  = "default"
    tags          = []
  }
  "VMOTION" = {
    allowed_vlans = "2"
    description   = "VMOTION Ethernet Network Group Policy"
    native_vlan   = 2
    organization  = "default"
    tags          = []
  }
  "STORAGE" = {
    allowed_vlans = "3"
    description   = "STORAGE Ethernet Network Group Policy"
    native_vlan   = 3
    organization  = "default"
    tags          = []
  }
  "DATA" = {
    allowed_vlans = "1-99"
    description   = "DATA Ethernet Network Group Policy"
    organization  = "default"
    tags          = []
  }
}