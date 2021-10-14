#______________________________________________
#
# Fibre Channel WWNN Pool Variables
#______________________________________________

wwnn_pools = {
  "ESX" = {
    id_blocks        = [
      {
        from = "20:10:AB:25:B5:04:00:00",
        to = "20:10:AB:25:B5:04:00:7F",
      },
    ]
    organization     = "UCS-DEMO2_ClientA"
    pool_purpose     = "WWNN"
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
  "HyperV" = {
    id_blocks        = [
      {
        from = "20:10:AB:25:B5:03:00:00",
        to = "20:10:AB:25:B5:03:00:7F",
      },
    ]
    organization     = "UCS-DEMO2_ClientA"
    pool_purpose     = "WWNN"
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
  "Linux" = {
    id_blocks        = [
      {
        from = "20:10:AB:25:B5:01:00:00",
        to = "20:10:AB:25:B5:01:00:7F",
      },
    ]
    organization     = "UCS-DEMO2_ClientA"
    pool_purpose     = "WWNN"
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
  "Windows" = {
    id_blocks        = [
      {
        from = "20:10:AB:25:B5:02:00:00",
        to = "20:10:AB:25:B5:02:00:7F",
      },
    ]
    organization     = "UCS-DEMO2_ClientA"
    pool_purpose     = "WWNN"
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