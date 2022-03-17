#______________________________________________
#
# Boot Order Policy Variables
#______________________________________________

boot_order_policies = {
  "iac-standalone_boot_order" = {
    boot_mode          = "Legacy"
    description        = "iac-standalone_boot_order Boot Order Policy"
    enable_secure_boot = false
    tags               = []
    boot_devices = {
      "LocalDisk" = {
        enabled     = true
        object_type = "boot.LocalDisk"
        Slot        = "SAS"
      },
      "VirtualMedia" = {
        enabled     = true
        object_type = "boot.VirtualMedia"
        Subtype     = "None"
      },
    }
  }
}