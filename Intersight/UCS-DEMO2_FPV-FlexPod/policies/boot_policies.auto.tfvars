#______________________________________________
#
# Boot Order Policy Variables
#______________________________________________

boot_policies = {
  "iSCSI-Boot" = {
    boot_mode          = "Legacy"
    enable_secure_boot = false
    description        = ""
    organization       = "UCS-DEMO2_FPV-FlexPod"
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
    boot_devices = {
      "1" = {
        enabled     = true
        object_type = "boot.LocalCdd"
      },
      "2_primary" = {
        enabled       = true
        InterfaceName = "iSCSI-Boot-A",
        Port          = 0,
        object_type   = "boot.Iscsi"
        Slot          = ""
      },
      "2_secondary" = {
        enabled       = true
        InterfaceName = "iSCSI-Boot-B",
        Port          = 0,
        object_type   = "boot.Iscsi"
        Slot          = ""
      },
    }
  }
}