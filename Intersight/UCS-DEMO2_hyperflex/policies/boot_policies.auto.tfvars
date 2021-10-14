#______________________________________________
#
# Boot Order Policy Variables
#______________________________________________

boot_policies = {
  "hx-compute" = {
    boot_mode          = "Legacy"
    enable_secure_boot = false
    description        = "Recommended-boot-policy-for-HyperFlex-servers"
    organization       = "UCS-DEMO2_hyperflex"
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
      "2" = {
        enabled     = true
        object_type = "boot.LocalDisk"
        Slot        = ""
      },
    }
  }
  "hx-compute-m5" = {
    boot_mode          = "Legacy"
    enable_secure_boot = false
    description        = "Recommended-boot-policy-for-HyperFlex-servers"
    organization       = "UCS-DEMO2_hyperflex"
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
      "2" = {
        enabled     = true
        object_type = "boot.LocalDisk"
        Slot        = ""
      },
    }
  }
  "HyperFlex" = {
    boot_mode          = "Legacy"
    enable_secure_boot = false
    description        = "Recommended-boot-policy-for-HyperFlex-servers"
    organization       = "UCS-DEMO2_hyperflex"
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
      "2" = {
        enabled     = true
        Lun         = 0,
        object_type = "boot.SdCard"
        Subtype     = ""
      },
    }
  }
  "HyperFlex-m5" = {
    boot_mode          = "Legacy"
    enable_secure_boot = false
    description        = "Recommended-boot-policy-for-HyperFlex-servers"
    organization       = "UCS-DEMO2_hyperflex"
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
      "2" = {
        enabled     = true
        object_type = "boot.LocalDisk"
        Slot        = ""
      },
    }
  }
}