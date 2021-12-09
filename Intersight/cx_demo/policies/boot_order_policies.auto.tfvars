#______________________________________________
#
# Boot Order Policy Variables
#______________________________________________

boot_order_policies = {
  "VMware_M2" = {
    boot_mode          = "Uefi"
    description        = "VMware_M2 Boot Order Policy"
    enable_secure_boot = true
    organization       = "cx_demo"
    tags               = []
    boot_devices = {
      "KVM-DVD" = {
        enabled     = true
        object_type = "boot.VirtualMedia"
        Subtype     = "kvm-mapped-dvd"
      },
      "M2" = {
        bootloader_description = "UEFI Bootloader",
        bootloader_name        = "BOOTx64.EFI",
        bootloader_path        = "\\EFI\\BOOT\\",
        enabled                = true
        object_type            = "boot.LocalDisk"
        Slot                   = "MSTOR-RAID"
      },
      "PXE" = {
        enabled         = true
        InterfaceName   = "MGMT-A",
        InterfaceSource = "name",
        IpType          = "IPv4",
        MacAddress      = "",
        object_type     = "boot.Pxe"
        Port            = -1,
        Slot            = "MLOM"
      },
    }
  }
}