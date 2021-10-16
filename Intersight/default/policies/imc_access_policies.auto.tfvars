#______________________________________________
#
# IMC Access Policy Variables
#______________________________________________

imc_access_policies = {
  "Asgard_imc_access" = {
    description                = "Asgard_imc_access IMC Access Policy"
    inband_ip_pool             = "Asgard_ip_pool"
    inband_vlan_id             = 51
    ipv4_address_configuration = true
    ipv6_address_configuration = false
    organization               = "default"
    tags                       = []
  }
}