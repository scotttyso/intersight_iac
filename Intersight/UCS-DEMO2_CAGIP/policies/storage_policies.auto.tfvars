#______________________________________________
#
# Storage Policy Variables
#______________________________________________

storage_policies = {
  "CEPH-BOOT" = {
    description              = ""
    global_hot_spares        = ""
    organization             = "UCS-DEMO2_CAGIP"
    unused_disks_state       = "NoChange"
    drive_group = {
      CEPH-BOOT = {
        raid_level = "Raid1"
        virtual_drives = {
          "BOOT" = {
              access_policy       = "Default"
              boot_drive          = false
              disk_cache          = "Default"
              expand_to_available = true
              read_policy         = "ReadAhead"
              size                = 0
              strip_size          = 64
              write_policy        = "WriteBackGoodBbu"
          }
        }
      },
    }
    m2_configuration         = {}
    single_drive_raid_configuration = {}
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