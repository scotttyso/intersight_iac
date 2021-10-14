#______________________________________________
#
# Ethernet Network Group Policy Variables
#______________________________________________

ethernet_network_group_policies = {
  "Asgard_Management" = {
    allowed_vlans = "2"
    description   = "Asgard_Management Ethernet Network Group Policy"
    native_vlan   = 2
    organization  = "default"
    tags          = []
  }
  "Asgard_Migration" = {
    allowed_vlans = "3"
    description   = "Asgard_Migration Ethernet Network Group Policy"
    organization  = "default"
    tags          = []
  }
  "Asgard_Storage" = {
    allowed_vlans = "4"
    description   = "Asgard_Storage Ethernet Network Group Policy"
    native_vlan   = 4
    organization  = "default"
    tags          = []
  }
  "Asgard_VMs" = {
    allowed_vlans = "5-99,101-199"
    description   = "Asgard_VMs Ethernet Network Group Policy"
    organization  = "default"
    tags          = []
  }
}