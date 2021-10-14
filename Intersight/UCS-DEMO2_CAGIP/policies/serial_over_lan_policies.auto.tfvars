#______________________________________________
#
# Serial over LAN Policy Variables
#______________________________________________

serial_over_lan_policies = {
  "SOL-ENABLE" = {
    baud_rate    = 9600
    com_port     = ""
    description  = ""
    enabled      = true
    organization = "UCS-DEMO2_CAGIP"
    ssh_port     = 2400
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