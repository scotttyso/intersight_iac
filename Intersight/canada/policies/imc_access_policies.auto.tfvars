#______________________________________________
#
# IMC Access Policy Variables
#______________________________________________

imc_access_policies = {
  "canada" = {
    description                = "canada IMC Access Policy"
    inband_ip_pool             = "VMWare_KVM"
    inband_vlan_id             = 1
    ipv4_address_configuration = true
    ipv6_address_configuration = false
    organization               = "canada"
    tags                       = []
  }
}