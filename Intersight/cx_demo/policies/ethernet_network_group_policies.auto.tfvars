#______________________________________________
#
# Ethernet Network Group Policy Variables
#______________________________________________

ethernet_network_group_policies = {
  "MGMT" = {
    allowed_vlans = "101"
    description   = "MGMT Ethernet Network Group Policy"
    native_vlan   = 101
    organization  = "cx_demo"
    tags          = []
  }
  "VMOTION" = {
    allowed_vlans = "101"
    description   = "VMOTION Ethernet Network Group Policy"
    native_vlan   = 101
    organization  = "cx_demo"
    tags          = []
  }
  "STORAGE" = {
    allowed_vlans = "101"
    description   = "STORAGE Ethernet Network Group Policy"
    native_vlan   = 101
    organization  = "cx_demo"
    tags          = []
  }
  "DATA" = {
    allowed_vlans = "1-99,101-199,201-299"
    description   = "DATA Ethernet Network Group Policy"
    organization  = "cx_demo"
    tags          = []
  }
}