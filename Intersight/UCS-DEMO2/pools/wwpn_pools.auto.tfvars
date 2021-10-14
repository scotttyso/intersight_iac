#______________________________________________
#
# Fibre Channel WWPN Pool Variables
#______________________________________________

wwpn_pools = {
  "DEMO-SAN-A" = {
    id_blocks        = [
      {
        from = "20:00:00:25:B5:11:AA:00"
        to = "20:00:00:25:B5:11:AA:FF"
      },
    ]
    organization     = "UCS-DEMO2"
    pool_purpose     = "WWPN"
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
  "DEMO-SAN-B" = {
    id_blocks        = [
      {
        from = "20:00:00:25:B5:11:BB:00"
        to = "20:00:00:25:B5:11:BB:FF"
      },
    ]
    organization     = "UCS-DEMO2"
    pool_purpose     = "WWPN"
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
  "PN-ESXi-OCB-A" = {
    id_blocks        = [
      {
        from = "20:0A:00:25:B5:00:20:06"
        to = "20:0A:00:25:B5:00:20:FF"
      },
    ]
    organization     = "UCS-DEMO2"
    pool_purpose     = "WWPN"
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
  "PN-ESXi-OCB-B" = {
    id_blocks        = [
      {
        from = "20:0B:00:25:B5:00:20:06"
        to = "20:0B:00:25:B5:00:20:FF"
      },
    ]
    organization     = "UCS-DEMO2"
    pool_purpose     = "WWPN"
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