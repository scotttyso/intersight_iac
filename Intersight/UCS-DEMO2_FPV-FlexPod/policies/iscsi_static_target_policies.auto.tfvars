#______________________________________________
#
# iSCSI Static Target Policy Variables
#______________________________________________

iscsi_static_target_policies = {
  "iSCSI-Boot-A_iSCSI-Boot-A_1" = {
    description  = ""
    ip_address   = "192.168.10.202"
    port         = 3260
    lun = [
      {
        bootable = true
        lun_id   = 0
      }
    ]
    organization = "UCS-DEMO2_FPV-FlexPod"
    target_name  = "iqn.1992-08.com.netapp"
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
  "iSCSI-Boot-A_iSCSI-Boot-A_2" = {
    description  = ""
    ip_address   = "192.168.10.201"
    port         = 3260
    lun = [
      {
        bootable = true
        lun_id   = 0
      }
    ]
    organization = "UCS-DEMO2_FPV-FlexPod"
    target_name  = "iqn.1992-08.com.netapp"
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
  "iSCSI-Boot-A_iSCSI-Boot-B_1" = {
    description  = ""
    ip_address   = "192.168.10.202"
    port         = 3260
    lun = [
      {
        bootable = true
        lun_id   = 0
      }
    ]
    organization = "UCS-DEMO2_FPV-FlexPod"
    target_name  = "iqn.1992-08.com.netapp"
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
  "iSCSI-Boot-A_iSCSI-Boot-B_2" = {
    description  = ""
    ip_address   = "192.168.10.201"
    port         = 3260
    lun = [
      {
        bootable = true
        lun_id   = 0
      }
    ]
    organization = "UCS-DEMO2_FPV-FlexPod"
    target_name  = "iqn.1992-08.com.netapp"
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
  "TestB_iSCSI-Boot-A_1" = {
    description  = ""
    ip_address   = "192.168.10.202"
    port         = 3260
    lun = [
      {
        bootable = true
        lun_id   = 0
      }
    ]
    organization = "UCS-DEMO2_FPV-FlexPod"
    target_name  = "iqn.1992-08.com.netapp"
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
  "TestB_iSCSI-Boot-A_2" = {
    description  = ""
    ip_address   = "192.168.10.201"
    port         = 3260
    lun = [
      {
        bootable = true
        lun_id   = 0
      }
    ]
    organization = "UCS-DEMO2_FPV-FlexPod"
    target_name  = "iqn.1992-08.com.netapp"
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
  "TestB_iSCSI-Boot-B_1" = {
    description  = ""
    ip_address   = "192.168.10.202"
    port         = 3260
    lun = [
      {
        bootable = true
        lun_id   = 0
      }
    ]
    organization = "UCS-DEMO2_FPV-FlexPod"
    target_name  = "iqn.1992-08.com.netapp"
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
  "TestB_iSCSI-Boot-B_2" = {
    description  = ""
    ip_address   = "192.168.10.201"
    port         = 3260
    lun = [
      {
        bootable = true
        lun_id   = 0
      }
    ]
    organization = "UCS-DEMO2_FPV-FlexPod"
    target_name  = "iqn.1992-08.com.netapp"
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
  "testIscsi_iSCSI-Boot-A_1" = {
    description  = ""
    ip_address   = "192.168.10.202"
    port         = 3260
    lun = [
      {
        bootable = true
        lun_id   = 0
      }
    ]
    organization = "UCS-DEMO2_FPV-FlexPod"
    target_name  = "iqn.1992-08.com.netapp"
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
  "testIscsi_iSCSI-Boot-A_2" = {
    description  = ""
    ip_address   = "192.168.10.201"
    port         = 3260
    lun = [
      {
        bootable = true
        lun_id   = 0
      }
    ]
    organization = "UCS-DEMO2_FPV-FlexPod"
    target_name  = "iqn.1992-08.com.netapp"
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
  "testIscsi_iSCSI-Boot-B_1" = {
    description  = ""
    ip_address   = "192.168.10.202"
    port         = 3260
    lun = [
      {
        bootable = true
        lun_id   = 0
      }
    ]
    organization = "UCS-DEMO2_FPV-FlexPod"
    target_name  = "iqn.1992-08.com.netapp"
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
  "testIscsi_iSCSI-Boot-B_2" = {
    description  = ""
    ip_address   = "192.168.10.201"
    port         = 3260
    lun = [
      {
        bootable = true
        lun_id   = 0
      }
    ]
    organization = "UCS-DEMO2_FPV-FlexPod"
    target_name  = "iqn.1992-08.com.netapp"
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