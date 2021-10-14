#______________________________________________
#
# Storage Policy Variables
#______________________________________________

storage_policies = {
  "sd" = {
    description              = ""
    global_hot_spares        = ""
    organization             = "UCS-DEMO2_FPV-FlexPod"
    unused_disks_state       = "NoChange"
    drive_group = {}
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