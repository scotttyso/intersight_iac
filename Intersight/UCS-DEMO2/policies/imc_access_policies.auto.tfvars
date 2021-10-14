#______________________________________________
#
# IMC Access Policiy Variables
#______________________________________________

imc_access_policies = {
  "ADMIN_inband" = {
    description                = ""
    inband_ip_pool             = "inband"
    inband_vlan_id             = 100
    ipv4_address_configuration = true
    ipv6_address_configuration = false
    organization               = "UCS-DEMO2"
    tags = [
      {
        key = "easyucs_origin",
        value = "convert",
      },
      {
        key = "easyucs_version",
        value = "0.9.8",
      },
    ]
  }
}