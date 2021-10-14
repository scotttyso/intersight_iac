#______________________________________________
#
# Fibre Channel Network Policy Variables
#______________________________________________

fibre_channel_network_policies = {
  "ESXi-OCB_SAN-A" = {
    default_vlan_id = 1010
    description     = ""
    organization    = "UCS-DEMO2"
    vsan_id         = 10
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
  "ESXi-OCB_SAN-B" = {
    default_vlan_id = 1020
    description     = ""
    organization    = "UCS-DEMO2"
    vsan_id         = 20
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
  "TEST-PLACEMENT-TEMPLATE_SCP_vhba0" = {
    default_vlan_id = 4048
    description     = ""
    organization    = "UCS-DEMO2"
    vsan_id         = 1
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