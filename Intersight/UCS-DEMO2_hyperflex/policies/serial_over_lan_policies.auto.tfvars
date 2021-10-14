#______________________________________________
#
# Serial over LAN Policy Variables
#______________________________________________

serial_over_lan_policies = {
  "HyperFlex" = {
    baud_rate    = 115200
    com_port     = ""
    description  = "Recommended-Serial-over-LAN-policy-for-HyperFlex-servers"
    enabled      = true
    organization = "UCS-DEMO2_hyperflex"
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