#_________________________________________________________________________
#
# Intersight LDAP Policies Variables
# GUI Location: Configure > Policies > Create Policy > LDAP > Start
#_________________________________________________________________________

variable "binding_parameters_password" {
  default     = ""
  description = "The password of the user for initial bind process. It can be any string that adheres to the following constraints. It can have character except spaces, tabs, line breaks. It cannot be more than 254 characters."
  sensitive   = true
  type        = string
}

variable "ldap_policies" {
  default = {
    default = {
      base_settings = {
        base_dn = "**REQUIRED**"
        domain  = "**REQUIRED**"
        timeout = 0
      }
      binding_parameters = {
        bind_dn     = ""
        bind_method = "LoginCredentials"
      }
      description                = ""
      enable_encryption          = false
      enable_group_authorization = false
      enable_ldap                = true
      ldap_from_dns              = {}
      ldap_groups                = {}
      ldap_servers               = {}
      nested_group_search_depth  = 128
      organization               = "default"
      search_parameters = {
        attribute       = "CiscoAvPair"
        filter          = "samAccountName"
        group_attribute = "memberOf"
      }
      tags                   = []
      user_search_precedence = "LocalUserDb"
    }
  }
  description = <<-EOT
  key - Name of the Persistent Memory Policy.
  * base_settings
    - base_dn - Base Distinguished Name (DN). Starting point from where server will search for users and groups.
    - domain - The LDAP Base domain that all users must be in.
    - timeout - LDAP authentication timeout duration, in seconds.  Range is 0 to 180.
  * binding_paramaters
    - bind_dn - Distinguished Name (DN) of the user, that is used to authenticate against LDAP servers.
    - bind_method - Authentication method to access LDAP servers.
      * Anonymous - Requires no username and password. If this option is selected and the LDAP server is configured for Anonymous logins, then the user gains access.
      * ConfiguredCredentials - Requires a known set of credentials to be specified for the initial bind process. If the initial bind process succeeds, then the distinguished name (DN) of the user name is queried and re-used for the re-binding process. If the re-binding process fails, then the user is denied access.
      * LoginCredentials - (Default) Requires the user credentials. If the bind process fails, then user is denied access.
  * description - Description to Assign to the Policy.
  * enable_encryption - If enabled, the endpoint encrypts all information it sends to the LDAP server.
  * enable_group_authorization - If enabled, user authorization is also done at the group level for LDAP users not in the local user database.
  * enable_ldap - Flag to Enable or Disable the Policy.
  * ldap_from_dns - This Array enabled the use of DNS for LDAP Server discovery.
    - enable - Enables DNS to access LDAP servers.
    - search_domain - Domain name that acts as a source for a DNS query.
    - search_forest - Forest name that acts as a source for a DNS query.
    - source - Specifies how to obtain the domain name used for the DNS SRV request. It can be one of the following:
      * Configured - specifies using the configured-search domain.
      * ConfiguredExtracted - specifies using the domain name extracted from the login ID than the configured-search domain.
      * Extracted - (Default) specifies using domain name extracted-domain from the login ID.
  * ldap_groups - Map of Groups and Attributes.
    - key - Name of the Group
    - role - Role to assign to the group.
      1. admin
      2. readonly
      3. user
  * ldap_servers - Map of LDAP Servers.
    Key - Name of the LDAP Server
    - port - Port to Assign to the LDAP Server.  Range is 1-65535.
  * nested_group_search_depth - Search depth to look for a nested LDAP group in an LDAP group map.  Range is 1 to 128.
  * organization - Name of the Intersight Organization to assign this Policy to.
    - https://intersight.com/an/settings/organizations/
  * search_parameters
    - attribute - Role and locale information of the user.
    - filter - Criteria to identify entries in search requests.
    - group_attribute - Groups to which an LDAP user belongs.
  * tags - List of Key/Value Pairs to Assign as Attributes to the Policy.
  * user_search_precedence - Search precedence between local user database and LDAP user database.
    - LocalUserDb - (Default) Precedence is given to local user database while searching.
    - LDAPUserDb - Precedence is given to LADP user database while searching.
  EOT
  type = map(object(
    {
      base_settings = object(
        {
          base_dn = string
          domain  = string
          timeout = optional(number)
        }
      )
      binding_parameters = object(
        {
          bind_dn     = optional(string)
          bind_method = optional(string)
        }
      )
      description                = optional(string)
      enable_encryption          = optional(bool)
      enable_group_authorization = optional(bool)
      enable_ldap                = optional(bool)
      ldap_from_dns = object(
        {
          enable        = optional(bool)
          search_domain = optional(string)
          search_forest = optional(string)
          source        = optional(string)
        }
      )
      ldap_groups = optional(map(object(
        {
          role = optional(string)
        }
      )))
      ldap_servers = optional(map(object(
        {
          port = optional(number)
        }
      )))
      nested_group_search_depth = optional(number)
      organization              = optional(string)
      search_parameters = object(
        {
          attribute       = optional(string)
          filter          = optional(string)
          group_attribute = optional(string)
        }
      )
      tags                   = optional(list(map(string)))
      user_search_precedence = optional(string)
    }
  ))
}


#_________________________________________________________________________
#
# LDAP Policies
# GUI Location: Configure > Policies > Create Policy > LDAP > Start
#_________________________________________________________________________

#______________________________________________
#
# LDAP Policy
#______________________________________________

resource "intersight_iam_ldap_policy" "ldap_policies" {
  depends_on = [
    local.org_moids
  ]
  for_each    = local.ldap_policies
  description = each.value.description != "" ? each.value.description : "${each.key} LDAP Policy"
  name        = each.key
  enabled     = each.value.enable_ldap
  base_properties {
    # Base Settings
    base_dn = each.value.base_settings.base_dn
    domain  = each.value.base_settings.domain
    timeout = each.value.base_settings.timeout != null ? each.value.base_settings.timeout : 0
    # Enable LDAP Encryption
    enable_encryption = each.value.enable_encryption
    # Binding Parameters
    bind_method = each.value.binding_parameters.bind_method
    bind_dn     = each.value.binding_parameters.bind_dn
    password    = var.binding_parameters_password
    # Search Parameters
    attribute       = each.value.search_parameters.attribute
    filter          = each.value.search_parameters.filter
    group_attribute = each.value.search_parameters.group_attribute
    # Group Authorization
    enable_group_authorization = each.value.enable_group_authorization
    nested_group_search_depth  = each.value.nested_group_search_depth
  }
  # Configure LDAP Servers
  enable_dns = each.value.ldap_from_dns.enable
  dns_parameters {
    nr_source     = each.value.ldap_from_dns.source
    search_domain = each.value.ldap_from_dns.search_domain
    search_forest = each.value.ldap_from_dns.search_forest
  }
  user_search_precedence = each.value.user_search_precedence
  organization {
    moid        = local.org_moids[each.value.organization].moid
    object_type = "organization.Organization"
  }
  dynamic "tags" {
    for_each = length(each.value.tags) > 0 ? each.value.tags : local.tags
    content {
      key   = tags.value.key
      value = tags.value.value
    }
  }
}


#______________________________________________
#
# LDAP Servers
#______________________________________________

resource "intersight_iam_ldap_provider" "ldap_servers" {
  depends_on = [
    local.org_moids,
    intersight_iam_ldap_policy.ldap_policies
  ]
  for_each = local.ldap_servers
  ldap_policy {
    moid = intersight_iam_ldap_policy.ldap_policies[each.value.policy].moid
  }
  port   = each.value.port
  server = each.value.server
}


#______________________________________________
#
# LDAP Groups
#______________________________________________

resource "intersight_iam_ldap_group" "ldap_group" {
  depends_on = [
    data.intersight_iam_end_point_role.roles,
    intersight_iam_ldap_policy.ldap_policies,
    local.org_moids
  ]
  for_each = local.ldap_groups
  domain   = each.value.domain
  name     = each.value.name
  end_point_role {
    moid        = data.intersight_iam_end_point_role.roles[each.value.role].results[0].moid
    object_type = "iam.EndPointRole"
  }
  ldap_policy {
    moid = intersight_iam_ldap_policy.ldap_policies[each.value.policy].moid
  }
}
