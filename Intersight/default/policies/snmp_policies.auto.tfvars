#______________________________________________
#
# SNMP Policy Variables
#______________________________________________

snmp_policies = {
  "Asgard_snmp" = {
    access_community_string = 1
    description             = "Asgard_snmp SNMP Policy"
    enable_snmp             = true
    organization            = "default"
    snmp_community_access   = ""
    snmp_engine_input_id    = ""
    snmp_port               = 161
    system_contact          = "UCS Admins"
    system_location         = "Data Center"
    trap_community_string   = 1
    tags         = []
    snmp_trap_destinations  = {
      "lnx1.rich.ciscolabs.com" = {
        enable              = true,
        port                = 162,
        trap_type           = "Trap",
        user                = "ciscouser",
        snmp_version        = "V3",
      },
    }
    snmp_users = {
      "ciscouser" = {
        auth_password    = 1,
        auth_type        = "SHA",
        privacy_password = 1,
        privacy_type     = "AES",
        security_level   = "AuthPriv",
      },
    }
  }
}