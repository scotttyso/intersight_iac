#______________________________________________
#
# SNMP Policy Variables
#______________________________________________

snmp_policies = {
  "UCS-DEMO2" = {
    description             = ""
    enable_snmp             = false
    organization            = "UCS-DEMO2"
    snmp_community_access   = ""
    snmp_engine_input_id    = ""
    snmp_port               = 161
    system_contact          = "Parlab Team (parlab@cisco.com)"
    system_location         = ""
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
    snmp_trap_destinations  = {}
    snmp_users              = {}
  }
}