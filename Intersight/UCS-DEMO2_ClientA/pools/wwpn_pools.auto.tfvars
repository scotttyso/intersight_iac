#______________________________________________
#
# Fibre Channel WWPN Pool Variables
#______________________________________________

wwpn_pools = {
  "ESX-WWPN" = {
    id_blocks        = [
      {
        from = "20:20:AB:25:B5:04:00:00"
        to = "20:20:AB:25:B5:04:00:7F"
      },
    ]
    organization     = "UCS-DEMO2_ClientA"
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
  "HyperV-WWPN" = {
    id_blocks        = [
      {
        from = "20:20:AB:25:B5:03:00:00"
        to = "20:20:AB:25:B5:03:00:7F"
      },
    ]
    organization     = "UCS-DEMO2_ClientA"
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
  "Linux-WWPN" = {
    id_blocks        = [
      {
        from = "20:20:AB:25:B5:01:00:00"
        to = "20:20:AB:25:B5:01:00:7F"
      },
    ]
    organization     = "UCS-DEMO2_ClientA"
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
  "Windows-WWPN" = {
    id_blocks        = [
      {
        from = "20:20:AB:25:B5:02:00:00"
        to = "20:20:AB:25:B5:02:00:7F"
      },
    ]
    organization     = "UCS-DEMO2_ClientA"
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