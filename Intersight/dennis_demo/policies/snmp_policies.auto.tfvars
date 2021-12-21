#______________________________________________
#
# SNMP Policy Variables
#______________________________________________

snmp_policies = {
  "dennis_demo" = {
    description             = "dennis_demo SNMP Policy"
    enable_snmp             = true
    organization            = "dennis_demo"
    snmp_community_access   = ""
    snmp_engine_input_id    = ""
    snmp_port               = 161
    system_contact          = "rich"
    system_location         = "rich"
    tags         = []
    snmp_trap_destinations  = {
      "198.18.0.1" = {
        enable           = true,
        port             = 162,
        trap_type        = "Trap",
        user             = "ciscosnmp",
      },
    }
    snmp_users = {
      "ciscosnmp" = {
        auth_password    = 1,
        auth_type        = "SHA",
        privacy_password = 1,
        privacy_type     = "AES",
        security_level   = "AuthPriv",
      },
    }
  }
}