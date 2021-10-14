#______________________________________________
#
# NTP Policy Variables
#______________________________________________

ntp_policies = {
  "UCS-DEMO2" = {
    description  = ""
    enabled      = true
    organization = "UCS-DEMO2"
    timezone     = "Europe/Paris"
    ntp_servers = [
      "ntp.esl.cisco.com",
    ]
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