#______________________________________________
#
# MAC Pool Variables
#______________________________________________

mac_pools = {
  "hv-mgmt-a" = {
    mac_blocks       = [
      {
        from = "00:25:B5:33:A1:01"
        to = "00:25:B5:33:A1:64"
      },
    ]
    organization     = "UCS-DEMO2_hyperflex"
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
  "hv-mgmt-b" = {
    mac_blocks       = [
      {
        from = "00:25:B5:33:B2:01"
        to = "00:25:B5:33:B2:64"
      },
    ]
    organization     = "UCS-DEMO2_hyperflex"
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
  "hv-vmotion-a" = {
    mac_blocks       = [
      {
        from = "00:25:B5:33:A7:01"
        to = "00:25:B5:33:A7:64"
      },
    ]
    organization     = "UCS-DEMO2_hyperflex"
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
  "hv-vmotion-b" = {
    mac_blocks       = [
      {
        from = "00:25:B5:33:B8:01"
        to = "00:25:B5:33:B8:64"
      },
    ]
    organization     = "UCS-DEMO2_hyperflex"
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
  "storage-data-a" = {
    mac_blocks       = [
      {
        from = "00:25:B5:33:A3:01"
        to = "00:25:B5:33:A3:64"
      },
    ]
    organization     = "UCS-DEMO2_hyperflex"
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
  "storage-data-b" = {
    mac_blocks       = [
      {
        from = "00:25:B5:33:B4:01"
        to = "00:25:B5:33:B4:64"
      },
    ]
    organization     = "UCS-DEMO2_hyperflex"
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
  "vm-network-a" = {
    mac_blocks       = [
      {
        from = "00:25:B5:33:A5:01"
        to = "00:25:B5:33:A5:64"
      },
    ]
    organization     = "UCS-DEMO2_hyperflex"
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
  "vm-network-b" = {
    mac_blocks       = [
      {
        from = "00:25:B5:33:B6:01"
        to = "00:25:B5:33:B6:64"
      },
    ]
    organization     = "UCS-DEMO2_hyperflex"
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