#______________________________________________
#
# MAC Pool Variables
#______________________________________________

mac_pools = {
  "ESX" = {
    mac_blocks       = [
      {
        from = "00:25:B5:04:00:00"
        to = "00:25:B5:04:00:7F"
      },
    ]
    organization     = "UCS-DEMO2_ClientA"
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
    mac_blocks       = [
      {
        from = "00:25:B5:03:00:00"
        to = "00:25:B5:03:00:7F"
      },
    ]
    organization     = "UCS-DEMO2_ClientA"
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
    mac_blocks       = [
      {
        from = "00:25:B5:01:00:00"
        to = "00:25:B5:01:00:7F"
      },
    ]
    organization     = "UCS-DEMO2_ClientA"
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
    mac_blocks       = [
      {
        from = "00:25:B5:02:00:00"
        to = "00:25:B5:02:00:7F"
      },
    ]
    organization     = "UCS-DEMO2_ClientA"
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
  "DEMO" = {
    mac_blocks       = [
      {
        from = "00:25:B5:11:C1:00"
        to = "00:25:B5:11:C1:FF"
      },
    ]
    organization     = "UCS-DEMO2_ClientA"
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