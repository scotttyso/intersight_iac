#______________________________________________
#
# MAC Pool Variables
#______________________________________________

mac_pools = {
  "MAC-Pool-A" = {
    mac_blocks       = [
      {
        from = "00:25:B5:13:0A:00"
        to = "00:25:B5:13:0A:3F"
      },
    ]
    organization     = "UCS-DEMO2_FPV-FlexPod"
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
  "MAC-Pool-B" = {
    mac_blocks       = [
      {
        from = "00:25:B5:13:0B:00"
        to = "00:25:B5:13:0B:3F"
      },
    ]
    organization     = "UCS-DEMO2_FPV-FlexPod"
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