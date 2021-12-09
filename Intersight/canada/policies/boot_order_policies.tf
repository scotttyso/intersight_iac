#_________________________________________________________________________
#
# Intersight Boot Order Policies Variables
# GUI Location: Configure > Policies > Create Policy > Boot Order
#_________________________________________________________________________

variable "boot_order_policies" {
  default = {
    default = {
      boot_devices       = {}
      boot_mode          = "Uefi"
      description        = ""
      enable_secure_boot = false
      organization       = "default"
      tags               = []
    }
  }
  description = <<-EOT
  key - Name of the Boot Order Policy.
  * boot_devices - Map of Boot Devices and their Attributes to Assign to the Boot Policy.
    key - Name to Assign to the boot_device.
    * Bootloader Variables - These will be used when the system is running in Uefi Boot Mode.
      - bootloader_description - Description to Assign to Bootloader when running in Uefi Boot Mode.
      - bootloader_name - Typically this should be "BOOTX64.EFI".
      - bootloader_path - Typically this should be "\\EFI\\BOOT\\".
        * The Following Boot Order Types utilize Bootloader Configuration:
          - boot.Iscsi
          - boot.LocalDisk
          - boot.Nvme
          - boot.PchStorage
          - boot.San
          - boot.SdCard
    * enabled - Default is true.  Specifies if the boot device is enabled or disabled.
    * InterfaceName - The name of the underlying virtual ethernet interface used by the Boot Device.
      - The Following Boot Order Types utilize the InterfaceName Attribute:
        * boot.Iscsi
        * boot.Pxe
        * boot.San
    * InterfaceSource - Used only by boot.Pxe.  Lists the supported Interface Source for PXE device.
      - name - Use interface name to select virtual ethernet interface.
      - mac - Use MAC address to select virtual ethernet interface.
      - port - Use port to select virtual ethernet interface.
    * IpType - Used only by boot.Pxe.  The IP Address family type to use during the PXE Boot process.
      - None - Default value if IpType is not specified.
      - IPv4 - The IPv4 address family type.
      - IPv6 - The IPv6 address family type.
    * Lun - Default is 0.  The Logical Unit Number (LUN) of the device.
      - The Following Boot Order Types utilize the Lun Attribute:
        * boot.PchStorage
        * boot.San
        * boot.SdCard
    * MacAddress - Used only by boot.Pxe.  The MAC Address of the underlying virtual ethernet interface used by the PXE boot device.
    * object_type - The Boot Order Type to Assign to the Boot Device.  Allowed Values are:
      - boot.Iscsi
      - boot.LocalCdd
      - boot.LocalDisk
      - boot.Nvme
      - boot.PchStorage
      - boot.Pxe
      - boot.San
      - boot.SdCard
      - boot.UefiShell
      - boot.Usb
      - boot.VirtualMedia
    * Port -  Used by iSCSI and PXE.
        * boot.Iscsi - Default is 0.  Port ID of the ISCSI boot device.  Supported values are (0-255).
        * boot.Pxe - Default is -1.  The Port ID of the adapter on which the underlying virtual ethernet interface is present. If no port is specified, the default value is -1. Supported values are -1 to 255.
    * Slot - The PCIe slot ID of the adapter on which the underlying virtual ethernet interface is present.
      - The Following Boot Order Types utilize the Slot Attribute:
        * boot.Iscsi - Supported values are (1-255, MLOM, L, L1, L2, OCP).
        * boot.LocalDisk - Supported values are (1-205, M, HBA, SAS, RAID, MRAID, MRAID1, MRAID2, MSTOR-RAID).  Supported values for FI-attached servers are (1-205, MRAID, FMEZZ1-SAS, MRAID1 , MRAID2, MSTOR-RAID, MSTOR-RAID-1, MSTOR-RAID-2).
        * boot.Pxe - Supported values are (1-255, MLOM , L, L1, L2, OCP).
        * boot.San - Supported values are (1-255, MLOM, L1, L2).
    * Subtype - The subtype for the selected device type.
      - The Following Boot Order Types utilize the Subtype Attribute:
        * boot.SdCard - Below are the Supported Subtype Values:
          - None - No sub type for SD card boot device.
          - flex-util - Use of FlexUtil (microSD) card as sub type for SD card boot device.
          - flex-flash - Use of FlexFlash (SD) card as sub type for SD card boot device.
          - SDCARD - Use of SD card as sub type for the SD Card boot device.
        * boot.Usb - Below are the Supported Subtype Values:
          - None - No sub type for USB boot device.
          - usb-cd - Use of Compact Disk (CD) as sub-type for the USB boot device.
          - usb-fdd - Use of Floppy Disk Drive (FDD) as sub-type for the USB boot device.
          - usb-hdd - Use of Hard Disk Drive (HDD) as sub-type for the USB boot device.
        * boot.VirtualMedia - Below are the Supported Subtype Values:
          - None - No sub type for virtual media.
          - cimc-mapped-dvd - The virtual media device is mapped to a virtual DVD device.
          - cimc-mapped-hdd - The virtual media device is mapped to a virtual HDD device.
          - kvm-mapped-dvd - A KVM mapped DVD virtual media device.
          - kvm-mapped-hdd - A KVM mapped HDD virtual media device.
          - kvm-mapped-fdd - A KVM mapped FDD virtual media device.
    * Wwpn - The WWPN Address of the underlying fiber channel interface used by the SAN boot device. Value must be in hexadecimal format xx:xx:xx:xx:xx:xx:xx:xx.
  * boot_mode - Sets the BIOS boot mode. UEFI uses the GUID Partition Table (GPT) whereas Legacy mode uses the Master Boot Record (MBR) partitioning scheme. To apply this setting, Please reboot the server.
    - Legacy - Legacy mode refers to the traditional process of booting from BIOS. Legacy mode uses the Master Boot Record (MBR) to locate the bootloader.
    - Uefi - UEFI mode uses the GUID Partition Table (GPT) to locate EFI Service Partitions to boot from.
  * description - Description to Assign to the Policy.
  * enable_secure_boot - If UEFI secure boot is enabled, the boot mode is set to UEFI by default. Secure boot enforces that device boots using only software that is trusted by the Original Equipment Manufacturer (OEM).
  * organization - Name of the Intersight Organization to assign this Policy to.
    - https://intersight.com/an/settings/organizations/
  * tags - List of Key/Value Pairs to Assign as Attributes to the Policy.
  EOT
  type = map(object(
    {
      # boot_devices       = list(map(any))
      boot_devices = map(object(
        {
          bootloader_description = optional(string)
          bootloader_name        = optional(string)
          bootloader_path        = optional(string)
          enabled                = bool
          InterfaceName          = optional(string)
          InterfaceSource        = optional(string)
          IpType                 = optional(string)
          Lun                    = optional(number)
          MacAddress             = optional(string)
          object_type            = string
          Port                   = optional(number)
          Slot                   = optional(string)
          Subtype                = optional(string)
          Wwpn                   = optional(string)
        }
      ))
      boot_mode          = optional(string)
      description        = optional(string)
      enable_secure_boot = optional(bool)
      organization       = optional(string)
      tags               = optional(list(map(string)))
    }
  ))
}


#_________________________________________________________________________
#
# Boot Order Policies
# GUI Location: Configure > Policies > Create Policy > Boot Order
#_________________________________________________________________________

module "boot_order_policies" {
  depends_on = [
    local.org_moids,
    local.merged_profile_policies,
  ]
  version            = ">=0.9.6"
  source             = "terraform-cisco-modules/imm/intersight//modules/boot_order_policies"
  for_each           = local.formatted_boot_order_policies
  boot_devices       = each.value.boot_devices
  boot_mode          = each.value.boot_mode
  description        = each.value.description != "" ? each.value.description : "${each.key} Boot Order Policy."
  enable_secure_boot = each.value.enable_secure_boot
  name               = each.key
  org_moid           = local.org_moids[each.value.organization].moid
  tags               = length(each.value.tags) > 0 ? each.value.tags : local.tags
  profiles = {
    for k, v in local.merged_profile_policies : k => {
      moid        = v.moid
      object_type = v.object_type
    }
    if local.merged_profile_policies[k].boot_order_policy == each.key
  }
}
