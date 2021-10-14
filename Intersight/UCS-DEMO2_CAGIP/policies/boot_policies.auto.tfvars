#______________________________________________
#
# Boot Order Policy Variables
#______________________________________________

boot_policies = {
  "LOCAL" = {
    boot_mode          = "Uefi"
    enable_secure_boot = false
    description        = ""
    organization       = "UCS-DEMO2_CAGIP"
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
        bootloader_description = "UEFI Bootloader",
        bootloader_name        = "BOOTx64.EFI",
        bootloader_path        = "\\EFI\\BOOT\\",
        enabled                = true
        object_type            = "boot.LocalDisk"
        Slot                   = ""
      },
    }
  }
  "LOCAL-PXE" = {
    boot_mode          = "Uefi"
    enable_secure_boot = false
    description        = ""
    organization       = "UCS-DEMO2_CAGIP"
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
        bootloader_description = "UEFI Bootloader",
        bootloader_name        = "BOOTx64.EFI",
        bootloader_path        = "\\EFI\\BOOT\\",
        enabled                = true
        object_type            = "boot.LocalDisk"
        Slot                   = ""
      },
      "2_primary" = {
        enabled         = true
        InterfaceName   = "",
        InterfaceSource = "name",
        IpType          = "None",
        MacAddress      = "",
        object_type     = "boot.Pxe"
        Port            = -1,
        Slot            = ""
      },
    }
  }
}