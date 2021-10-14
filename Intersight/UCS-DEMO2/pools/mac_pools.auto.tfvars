#______________________________________________
#
# MAC Pool Variables
#______________________________________________

mac_pools = {
  "DEMO" = {
    mac_blocks       = [
      {
        from = "00:25:B5:11:C1:00"
        to = "00:25:B5:11:C1:FF"
      },
    ]
    organization     = "UCS-DEMO2"
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
  "ISCSI-A" = {
    mac_blocks       = [
      {
        from = "00:25:B5:00:0A:08"
        to = "00:25:B5:00:0A:11"
      },
    ]
    organization     = "UCS-DEMO2"
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
  "ISCSI-B" = {
    mac_blocks       = [
      {
        from = "00:25:B5:00:0B:08"
        to = "00:25:B5:00:0B:11"
      },
    ]
    organization     = "UCS-DEMO2"
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
  "OCB-ESXi" = {
    mac_blocks       = [
      {
        from = "00:25:B5:00:00:00"
        to = "00:25:B5:00:01:F3"
      },
    ]
    organization     = "UCS-DEMO2"
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
  "test" = {
    mac_blocks       = [
      {
        from = "00:25:B5:FF:FF:00"
        to = "00:25:B5:FF:FF:03"
      },
    ]
    organization     = "UCS-DEMO2"
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