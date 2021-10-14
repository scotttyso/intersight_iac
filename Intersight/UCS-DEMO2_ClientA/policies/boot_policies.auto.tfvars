#______________________________________________
#
# Boot Order Policy Variables
#______________________________________________

boot_policies = {
  "default" = {
    boot_mode          = "Legacy"
    enable_secure_boot = false
    description        = ""
    organization       = "UCS-DEMO2_ClientA"
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
        object_type = "boot.LocalDisk"
        Slot        = ""
      },
      "2_primary" = {
        enabled         = true
        InterfaceName   = "default",
        InterfaceSource = "name",
        IpType          = "None",
        MacAddress      = "",
        object_type     = "boot.Pxe"
        Port            = -1,
        Slot            = ""
      },
      "3" = {
        enabled     = true
        object_type = "boot.LocalCdd"
      },
    }
  }
}