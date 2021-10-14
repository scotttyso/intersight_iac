#______________________________________________
#
# VSAN Policy Variables
#______________________________________________

vsan_policies = {
  "UCS-DEMO2-A" = {
    description     = ""
    organization    = "UCS-DEMO2"
    uplink_trunking = true
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
    vsans = {
      "1" = {
        fcoe_vlan_id   = 4048
        vsan_id        = 1
        name           = "default"
        default_zoning = "Disabled"
      },
      "2" = {
        fcoe_vlan_id   = 1010
        vsan_id        = 10
        name           = "PROD"
        default_zoning = "Disabled"
      },
      "3" = {
        fcoe_vlan_id   = 1020
        vsan_id        = 20
        name           = "BACKUP"
        default_zoning = "Disabled"
      },
    }
  }
  "UCS-DEMO2-B" = {
    description     = ""
    organization    = "UCS-DEMO2"
    uplink_trunking = false
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
    vsans = {
      "1" = {
        fcoe_vlan_id   = 4048
        vsan_id        = 1
        name           = "default"
        default_zoning = "Disabled"
      },
      "2" = {
        fcoe_vlan_id   = 1011
        vsan_id        = 11
        name           = "PROD"
        default_zoning = "Disabled"
      },
      "3" = {
        fcoe_vlan_id   = 1020
        vsan_id        = 20
        name           = "VSAN-20"
        default_zoning = "Disabled"
      },
      "4" = {
        fcoe_vlan_id   = 1021
        vsan_id        = 21
        name           = "BACKUP"
        default_zoning = "Disabled"
      },
    }
  }
}