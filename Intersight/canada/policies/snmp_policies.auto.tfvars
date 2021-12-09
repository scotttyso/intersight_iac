#______________________________________________
#
# SNMP Policy Variables
#______________________________________________

snmp_policies = {
  "canada" = {
    description           = "canada SNMP Policy"
    enable_snmp           = true
    organization          = "canada"
    snmp_community_access = ""
    snmp_engine_input_id  = ""
    snmp_port             = 161
    system_contact        = "rich-lab@cisco.com"
    system_location       = "Rack 143D"
    tags                  = []
    snmp_trap_destinations = {
      "198.18.0.1" = {
        enable    = true,
        port      = 162,
        trap_type = "Trap",
        user      = "admin",
      },
    }
    snmp_users = {
      "admin" = {
        auth_password    = 1,
        auth_type        = "SHA",
        privacy_password = 1,
        privacy_type     = "AES",
        security_level   = "AuthPriv",
      },
    }
  }
}