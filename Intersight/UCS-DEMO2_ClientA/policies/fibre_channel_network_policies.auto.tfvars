#______________________________________________
#
# Fibre Channel Network Policy Variables
#______________________________________________

fibre_channel_network_policies = {
  "ESX_vfc0" = {
    default_vlan_id = 1011
    description     = ""
    organization    = "UCS-DEMO2_ClientA"
    vsan_id         = 11
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
  "ESX_vfc1" = {
    default_vlan_id = 1011
    description     = ""
    organization    = "UCS-DEMO2_ClientA"
    vsan_id         = 11
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