#______________________________________________
#
# SNMP Policy Variables
#______________________________________________

snmp_policies = {
  "Asgard_snmp" = {
    description             = "Asgard_snmp SNMP Policy"
    enable_snmp             = true
    organization            = "Asgard"
    snmp_community_access   = "Disabled"
    snmp_engine_input_id    = ""
    snmp_port               = 161
    system_contact          = "UCS Admins"
    system_location         = "Richfield Lab"
    tags         = []
    snmp_trap_destinations  = {
      "lnx1.rich.ciscolabs.com" = {
        enable              = true,
        port                = 162,
        trap_type           = "Trap",
        user                = "cisco_user",
        snmp_version        = "V3",
      },
    }
    snmp_users = {
      "cisco_user" = {
        auth_password    = 1,
        auth_type        = "SHA",
        privacy_password = 1,
        privacy_type     = "AES",
        security_level   = "AuthPriv",
      },
    }
  }
}