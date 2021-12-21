#______________________________________________
#
# IMC Access Policy Variables
#______________________________________________

imc_access_policies = {
  "dennis_demo" = {
    description                = "dennis_demo IMC Access Policy"
    inband_ip_pool             = "VMWare_KVM"
    inband_vlan_id             = 1
    ipv4_address_configuration = true
    ipv6_address_configuration = false
    organization               = "dennis_demo"
    tags                       = []
  }
}