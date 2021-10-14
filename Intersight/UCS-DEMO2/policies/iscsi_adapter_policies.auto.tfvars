#______________________________________________
#
# iSCSI Adapter Policy Variables
#______________________________________________

iscsi_adapter_policies = {
  "default" = {
    description            = ""
    dhcp_timeout           = 60
    lun_busy_retry_count   = 0
    organization           = "UCS-DEMO2"
    tcp_connection_timeout = 0
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