#______________________________________________
#
# IPMI over LAN Policy Variables
#______________________________________________

ipmi_over_lan_policies = {
  "IPMI-OSB3-DID" = {
    description    = ""
    enabled        = true
    ipmi_key       = null
    organization   = "UCS-DEMO2_CAGIP"
    privilege      = "admin"
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