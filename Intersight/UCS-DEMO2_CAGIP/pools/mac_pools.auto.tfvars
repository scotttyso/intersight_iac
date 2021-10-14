#______________________________________________
#
# MAC Pool Variables
#______________________________________________

mac_pools = {
  "MAC-OSB3-DID" = {
    mac_blocks       = [
      {
        from = "00:25:B5:BD:30:00"
        to = "00:25:B5:BD:31:FF"
      },
      {
        from = "00:25:B5:BD:32:00"
        to = "00:25:B5:BD:33:FF"
      },
    ]
    organization     = "UCS-DEMO2_CAGIP"
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