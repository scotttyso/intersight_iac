#_________________________________________________________________________
#
# Intersight Storage Policy Variables
# GUI Location: Configure > Policies > Create Policy > Storage > Start
#_________________________________________________________________________

variable "storage_policies" {
  default = {
    default = {
      description                     = ""
      global_hot_spares               = ""
      m2_configuration                = {}
      organization                    = "default"
      single_drive_raid_configuration = {}
      tags                            = []
      unused_disks_state              = "NoChange"
      use_jbod_for_vd_creation        = false
      drive_group = {
        default = {
          automatic_drive_group = {}
          manual_drive_group    = {}
          raid_level            = "Raid1"
          virtual_drives        = {}
        }
      }
    }
  }
  description = <<-EOT
  key - Name for the Storage Policy.
  * description - Description to Assign to the Policy.
  * global_hot_spares - A collection of disks that is to be used as hot spares, globally, for all the RAID groups. Allowed value is a number range separated by a comma or a hyphen.
  * m2_configuration - Slot of the M.2 RAID controller for virtual drive creation.
    - controller_slot - Options are:
      * MSTOR-RAID-1 - Virtual drive will be created on the M.2 RAID controller in the first slot.
      * MSTOR-RAID-2 - Virtual drive will be created on the M.2 RAID controller in the second slot, if available.
      * MSTOR-RAID-1,MSTOR-RAID-2 - Virtual drive will be created on the M.2 RAID controller in both the slots, if available.
    - enable - If enabled, this will create a virtual drive on the M.2 RAID controller.
  * organization - Name of the Intersight Organization to assign this Policy to.
    - https://intersight.com/an/settings/organizations/
  * single_drive_raid_configuration - M.2 Virtual Drive Configuration.
    - access_policy - Access policy that host has on this virtual drive.
      * Default - Use platform default access mode.
      * ReadWrite - Enables host to perform read-write on the VD.
      * ReadOnly - Host can only read from the VD.
      * Blocked - Host can neither read nor write to the VD.
    - drive_cache - Disk cache policy for the virtual drive.
      * Default - Use platform default drive cache mode.
      * NoChange - Drive cache policy is unchanged.
      * Enable - Enables IO caching on the drive.
      * Disable - Disables IO caching on the drive.
    - drive_slots - The set of drive slots where RAID0 virtual drives must be created.
    - enable - If enabled, this will create a RAID0 virtual drive per disk and encompassing the whole disk.
    - read_policy - Read ahead mode to be used to read data from this virtual drive.
      * Default - Use platform default read ahead mode.
      * ReadAhead - Use read ahead mode for the policy.
      * NoReadAhead - Do not use read ahead mode for the policy.
    - strip_size - Desired strip size - Allowed values are 64KiB, 128KiB, 256KiB, 512KiB, 1024KiB.
      * 64KiB - Number of bytes in a strip is 64 Kibibytes.
      * 128KiB - Number of bytes in a strip is 128 Kibibytes.
      * 256KiB - Number of bytes in a strip is 256 Kibibytes.
      * 512KiB - Number of bytes in a strip is 512 Kibibytes.
      * 1MiB - Number of bytes in a strip is 1024 Kibibytes or 1 Mebibyte.
    - write_policy:(string) Write mode to be used to write data to this virtual drive.
      * Default - Use platform default write mode.
      * WriteThrough - Data is written through the cache and to the physical drives. Performance is improved, because subsequent reads of that data can be satisfied from the cache.
      * WriteBackGoodBbu - Data is stored in the cache, and is only written to the physical drives when space in the cache is needed. Virtual drives requesting this policy fall back to Write Through caching when the battery backup unit (BBU) cannot guarantee the safety of the cache in the event of a power failure.
      * AlwaysWriteBack - With this policy, write caching remains Write Back even if the battery backup unit is defective or discharged.
  * tags - List of Key/Value Pairs to Assign as Attributes to the Policy.
  * unused_disks_state - State to which disks, not used in this policy, are to be moved.
    - NoChange - (Default) Drive state will not be modified by Storage Policy.
    - UnconfiguredGood - Unconfigured good state -ready to be added in a RAID group.
    - Jbod - JBOD state where the disks start showing up to Host OS.
  * use_jbod_for_vd_creation - Default is false.  Disks in JBOD State are used to create virtual drives.


  * drive_group - Drive Group(s) to Assign to the Storage Policy.
    key - Name of the Drive Group.
    - automatic_drive_group - This drive group is created using automatic drive selection.  This complex property has following sub-properties:
      * drive_type - Type of drive that should be used for this RAID group.
        - Any - Any type of drive can be used for virtual drive creation.
        - HDD - Hard disk drives should be used for virtual drive creation.
        - SSD - Solid state drives should be used for virtual drive creation.
      * drives_per_span - Number of drives within this span group. The minimum number of disks needed in a span group varies based on RAID level. RAID0 requires at least one disk. RAID1 and RAID10 requires at least 2 and in multiples of . RAID5 and RAID50 require at least 3 disks in a span group. RAID6 and RAID60 require atleast 4 disks in a span.
      * minimum_drive_size - Minimum size of the drive to be used for creating this RAID group.
      * num_dedicated_hot_spares - Number of dedicated hot spare disks for this RAID group. Allowed value is a comma or hyphen separated number range.
      * number_of_spans - Number of span groups to be created for this RAID group. Non-nested RAID levels have a single span.
      * use_remaining_drives - This flag enables the drive group to use all the remaining drives on the server.
    - manual_drive_group - This drive group is created by specifying the drive slots to be used. This complex property has following sub-properties:
      * dedicated_hot_spares:(string) A collection of drives to be used as hot spares for this Drive Group.
      * slots:(string) Collection of local disks that are part of this span group. Allowed value is a comma or hyphen separated number range. The minimum number of disks needed in a span group varies based on RAID level.
        - RAID0 requires at least one disk,
        - RAID1 and RAID10 requires at least 2 and in multiples of 2,
        - RAID5 RAID50 RAID6 and RAID60 require at least 3 disks in a span group.
        - Enable - Enables IO caching on the drive.
        - NoChange - Drive cache policy is unchanged.
    - raid_level - The supported RAID level for the disk group.
      * Raid0 - RAID 0 Stripe Raid Level.
      * Raid1 - RAID 1 Mirror Raid Level.
      * Raid5 - RAID 5 Mirror Raid Level.
      * Raid6 - RAID 6 Mirror Raid Level.
      * Raid10 - RAID 10 Mirror Raid Level.
      * Raid50 - RAID 50 Mirror Raid Level.
      * Raid60 - RAID 60 Mirror Raid Level.
    - tags - List of Tag Attributes to Assign to the Policy.
    - virtual_drives - This complex property has following sub-properties:
      * boot_drive:(bool) This flag enables this virtual drive to be used as a boot drive.
      * expand_to_available:(bool) This flag enables the virtual drive to use all the space available in the disk group. When this flag is enabled, the size property is ignored.
      * name:(string) The name of the virtual drive. The name can be between 1 and 15 alphanumeric characters. Spaces or any special characters other than - (hyphen), _ (underscore), : (colon), and . (period) are not allowed.
      * size:(int) Virtual drive size in MebiBytes. Size is mandatory field except when the Expand to Available option is enabled.
      * access_policy:(string) Access policy that host has on this virtual drive.
        - Default - Use platform default access mode.
        - ReadWrite - Enables host to perform read-write on the VD.
        - ReadOnly - Host can only read from the VD.
        - Blocked - Host can neither read nor write to the VD.
      * drive_cache:(string) Disk cache policy for the virtual drive.
        - Default - Use platform default drive cache mode.
        - NoChange - Drive cache policy is unchanged.
        - Enable - Enables IO caching on the drive.
        - Disable - Disables IO caching on the drive.
      * read_policy:(string) Read ahead mode to be used to read data from this virtual drive.
        - Default - Use platform default read ahead mode.
        - ReadAhead - Use read ahead mode for the policy.
        - NoReadAhead - Do not use read ahead mode for the policy.
      * strip_size:(int) Desired strip size - Allowed values are 64KiB, 128KiB, 256KiB, 512KiB, 1024KiB.
        - 64KiB - Number of bytes in a strip is 64 Kibibytes.
        - 128KiB - Number of bytes in a strip is 128 Kibibytes.
        - 256KiB - Number of bytes in a strip is 256 Kibibytes.
        - 512KiB - Number of bytes in a strip is 512 Kibibytes.
        - 1MiB - Number of bytes in a strip is 1024 Kibibytes or 1 Mebibyte.
      * write_policy:(string) Write mode to be used to write data to this virtual drive.
        - Default - Use platform default write mode.
        - WriteThrough - Data is written through the cache and to the physical drives. Performance is improved, because subsequent reads of that data can be satisfied from the cache.
        - WriteBackGoodBbu - Data is stored in the cache, and is only written to the physical drives when space in the cache is needed. Virtual drives requesting this policy fall back to Write Through caching when the battery backup unit (BBU) cannot guarantee the safety of the cache in the event of a power failure.
        - AlwaysWriteBack - With this policy, write caching remains Write Back even if the battery backup unit is defective or discharged.
  EOT
  type = map(object(
    {
      description       = optional(string)
      global_hot_spares = optional(string)
      m2_configuration = optional(map(object(
        {
          controller_slot = string
          enable          = bool
        }
      )))
      organization = optional(string)
      single_drive_raid_configuration = optional(map(object(
        {
          access_policy = optional(string)
          drive_cache   = optional(string)
          drive_slots   = string
          enable        = bool
          read_policy   = optional(string)
          strip_size    = string
          write_policy  = optional(string)
        }
      )))
      tags                     = optional(list(map(string)))
      unused_disks_state       = optional(string)
      use_jbod_for_vd_creation = optional(bool)
      drive_group = map(object(
        {
          automatic_drive_group = optional(map(object(
            {
              drive_type               = string
              drives_per_span          = number
              minimum_drive_size       = number
              num_dedicated_hot_spares = optional(number)
              number_of_spans          = number
              use_remaining_drives     = optional(bool)
            }
          )))
          manual_drive_group = optional(map(object(
            {
              dedicated_hot_spares = optional(string)
              drive_array_spans = map(object(
                {
                  slots = string
                }
              ))
            }
          )))
          raid_level = optional(string)
          virtual_drives = optional(map(object(
            {
              access_policy       = optional(string)
              boot_drive          = optional(bool)
              disk_cache          = optional(string)
              expand_to_available = optional(bool)
              read_policy         = optional(string)
              size                = optional(number)
              strip_size          = optional(number)
              write_policy        = optional(string)
            }
          )))
        }
      ))
    }
  ))
}


#_________________________________________________________________________
#
# Intersight Storage Policies
# GUI Location: Configure > Policies > Create Policy > Storage > Start
#_________________________________________________________________________

resource "intersight_storage_storage_policy" "storage_policies" {
  depends_on = [
    local.org_moids
  ]
  for_each                 = local.storage_policies
  description              = each.value.description != "" ? each.value.description : "${each.key} Storage Policy"
  global_hot_spares        = each.value.global_hot_spares
  name                     = each.key
  unused_disks_state       = each.value.unused_disks_state
  use_jbod_for_vd_creation = each.value.use_jbod_for_vd_creation
  # retain_policy_virtual_drives = var.retain_policy
  organization {
    moid        = local.org_moids[each.value.organization].moid
    object_type = "organization.Organization"
  }
  dynamic "m2_virtual_drive" {
    for_each = each.value.m2_configuration
    content {
      controller_slot = m2_virtual_drive.value.controller_slot
      enable          = m2_virtual_drive.value.enable
      # additional_properties = ""
      # object_type           = "storage.DiskGroupPolicy"
    }
  }
  dynamic "raid0_drive" {
    for_each = each.value.single_drive_raid_configuration
    content {
      drive_slots = raid0_drive.value.drive_slots
      enable      = raid0_drive.value.enable
      object_type = "server.Profile"
      virtual_drive_policy = [
        {
          additional_properties = ""
          access_policy         = raid0_drive.value.access_policy
          class_id              = "storage.VirtualDriveConfig"
          drive_cache           = raid0_drive.value.drive_cache
          object_type           = "storage.VirtualDriveConfig"
          read_policy           = raid0_drive.value.read_policy
          strip_size            = raid0_drive.value.strip_size
          write_policy          = raid0_drive.value.write_policy
        }
      ]
    }
  }
  dynamic "tags" {
    for_each = length(each.value.tags) > 0 ? each.value.tags : local.tags
    content {
      key   = tags.value.key
      value = tags.value.value
    }
  }
}


#_________________________________________________________________________
#
# Intersight Storage Policies - Drive Group(s)
# GUI Location: Configure > Policies > Create Policy > Storage > Start
#_________________________________________________________________________

resource "intersight_storage_drive_group" "drive_group" {
  depends_on = [
    local.org_moids,
    intersight_storage_storage_policy.storage_policies
  ]
  for_each   = local.drive_group
  name       = each.key
  raid_level = each.value.raid_level
  storage_policy {
    moid = intersight_storage_storage_policy.storage_policies[each.value.storage_policy].moid
    # object_type = "organization.Organization"
  }
  dynamic "automatic_drive_group" {
    for_each = each.value.automatic_drive_group
    content {
      class_id                 = "storage.ManualDriveGroup"
      drives_per_span          = automatic_drive_group.value.drives_per_span
      drive_type               = automatic_drive_group.value.drive_type
      minimum_drive_size       = automatic_drive_group.value.minimum_drive_size
      num_dedicated_hot_spares = automatic_drive_group.value.num_dedicated_hot_spares != null ? automatic_drive_group.value.num_dedicated_hot_spares : 0
      number_of_spans          = automatic_drive_group.value.number_of_spans
      object_type              = "storage.ManualDriveGroup"
      use_remaining_drives     = automatic_drive_group.value.use_remaining_drives != null ? automatic_drive_group.value.use_remaining_drives : false
    }
  }
  dynamic "manual_drive_group" {
    for_each = each.value.manual_drive_group
    content {
      class_id             = "storage.ManualDriveGroup"
      dedicated_hot_spares = manual_drive_group.value.dedicated_hot_spares != null ? manual_drive_group.value.dedicated_hot_spares : ""
      object_type          = "storage.ManualDriveGroup"
      span_groups          = manual_drive_group.value.drive_array_spans
    }
  }
  dynamic "tags" {
    for_each = length(each.value.tags) > 0 ? each.value.tags : local.tags
    content {
      key   = tags.value.key
      value = tags.value.value
    }
  }
  dynamic "virtual_drives" {
    for_each = each.value.virtual_drives
    content {
      additional_properties = ""
      boot_drive            = virtual_drives.value.boot_drive
      class_id              = "storage.VirtualDriveConfiguration"
      expand_to_available   = virtual_drives.value.expand_to_available
      name                  = virtual_drives.key
      object_type           = "storage.VirtualDriveConfiguration"
      size                  = virtual_drives.value.size
      virtual_drive_policy = [
        {
          additional_properties = ""
          access_policy         = virtual_drives.value.access_policy
          class_id              = "storage.VirtualDrivePolicy"
          drive_cache           = virtual_drives.value.disk_cache
          object_type           = "storage.VirtualDrivePolicy"
          read_policy           = virtual_drives.value.read_policy
          strip_size            = virtual_drives.value.strip_size
          write_policy          = virtual_drives.value.write_policy
        }
      ]
    }
  }
}
