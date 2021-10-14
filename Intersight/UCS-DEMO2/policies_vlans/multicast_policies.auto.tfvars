#______________________________________________
#
# Multicast Policy Variables
#______________________________________________

multicast_policies = {
  "UCS-DEMO2" = {
    description             = ""
    organization            = "UCS-DEMO2"
    querier_ip_address      = ""
    querier_ip_address_peer = ""
    querier_state           = "Disabled"
    snooping_state          = "Enabled"
    tags                    = [
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
  "HyperFlex" = {
    description             = ""
    organization            = "UCS-DEMO2"
    querier_ip_address      = ""
    querier_ip_address_peer = ""
    querier_state           = "Disabled"
    snooping_state          = "Enabled"
    tags                    = [
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
  "multi_poli" = {
    description             = ""
    organization            = "UCS-DEMO2"
    querier_ip_address      = "10.1.0.1"
    querier_ip_address_peer = "10.2.0.1"
    querier_state           = "Enabled"
    snooping_state          = "Enabled"
    tags                    = [
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
  "test" = {
    description             = ""
    organization            = "UCS-DEMO2"
    querier_ip_address      = ""
    querier_ip_address_peer = ""
    querier_state           = "Disabled"
    snooping_state          = "Disabled"
    tags                    = [
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