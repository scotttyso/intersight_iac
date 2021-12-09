#______________________________________________
#
# IMC Access Policy Variables
#______________________________________________

imc_access_policies = {
  "cx_demo" = {
    description                = "cx_demo IMC Access Policy"
    inband_ip_pool             = "VMWare_KVM"
    inband_vlan_id             = 101
    ipv4_address_configuration = true
    ipv6_address_configuration = false
    organization               = "cx_demo"
    tags                       = []
  }
}