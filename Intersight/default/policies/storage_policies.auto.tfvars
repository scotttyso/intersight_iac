#______________________________________________
#
# Storage Policy Variables
#______________________________________________

storage_policies = {
  "default_storage" = {
    description              = "default_storage Storage Policy"
    drive_group = {}
    global_hot_spares        = ""
    m2_configuration = [
      {
        controller_slot = "MSTOR-RAID-1"
        enable          = true
      }
    ]
    single_drive_raid_configuration = [
      {
        access_policy = "Default"
        disk_cache    = "Default"
        drive_slots   = "1-2"
        enable        = true
        read_policy   = "Default"
        strip_size    = 64
        write_policy  = "Default"
      }
    ]
    unused_disks_state       = "NoChange"
    tags         = []
  }
}