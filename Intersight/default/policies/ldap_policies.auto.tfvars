#______________________________________________
#
# LDAP Policy Variables
#______________________________________________

ldap_policies = {
  "Asgard_ldap" = {
    base_settings = {
      base_dn = "DC=rich,DC=ciscolabs,DC=com"
      domain  = "rich.ciscolabs.com"
      timeout = 0
    }
    binding_parameters = {
      bind_dn     = ""
      bind_method = "LoginCredentials"
    }
    description                = "Asgard_ldap LDAP Policy"
    enable_encryption          = true
    enable_group_authorization = true
    enable_ldap                = true
    ldap_groups = {
      "Lab Admin" = {
        role = "admin"
      },
    }
    ldap_servers = {
      "ad1.rich.ciscolabs.com" = {
        port = 636
      },
    }
    nested_group_search_depth = 128
    organization              = "default"
    search_parameters = {
      attribute       = "CiscoAvPair"
      filter          = "sAMAccountName"
      group_attribute = "memberOf"
    }
    tags         = []
    user_search_precedence = "LocalUserDb"
  }
}