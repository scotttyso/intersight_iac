#______________________________________________
#
# Ethernet Network Group Policy Variables
#______________________________________________

ethernet_network_group_policies = {
  "VG-ADMIN-SRV" = {
    allowed_vlans = "897"
    description   = ""
    organization  = "UCS-DEMO2_CAGIP"
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
  "CEPH_CEPH-BE" = {
    allowed_vlans = "756"
    description   = ""
    organization  = "UCS-DEMO2_CAGIP"
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
  "CEPH_CEPH-FE" = {
    allowed_vlans = "757"
    description   = ""
    organization  = "UCS-DEMO2_CAGIP"
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
  "CPTE_CEPH-FE" = {
    allowed_vlans = "757"
    description   = ""
    organization  = "UCS-DEMO2_CAGIP"
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
  "VG-SILCA" = {
    allowed_vlans = "1945"
    description   = ""
    organization  = "UCS-DEMO2_CAGIP"
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
  "CPTE_OS-PRIVATE" = {
    allowed_vlans = "7"
    description   = ""
    organization  = "UCS-DEMO2_CAGIP"
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