#__________________________________________________________
#
# Local Variables Section
#__________________________________________________________

locals {
  # Intersight Organization Variables
  organizations = var.organizations
  org_moids = {
    for v in sort(keys(data.intersight_organization_organization.org_moid)) : v => {
      moid = data.intersight_organization_organization.org_moid[v].results[0].moid
    }
  }
  # Intersight Provider Variables
  endpoint = var.endpoint

  # Tags for Deployment
  tags = var.tags

  #______________________________________________
  #
  # Fibre-Channel Pools
  #______________________________________________
  wwnn_pools = {
    for k, v in var.wwnn_pools : k => {
      assignment_order = v.assignment_order != null ? v.assignment_order : "default"
      description      = v.description != null ? v.description : ""
      id_blocks        = v.id_blocks != null ? v.id_blocks : [{ from = "20:00:00:25:B5:00:00:00", to = "20:00:00:25:B5:00:00:ff" }]
      organization     = v.organization != null ? v.organization : "default"
      pool_purpose     = v.pool_purpose != null ? v.pool_purpose : "WWPN"
      tags             = v.tags != null ? v.tags : []
    }
  }
  wwpn_pools = {
    for k, v in var.wwpn_pools : k => {
      assignment_order = v.assignment_order != null ? v.assignment_order : "default"
      description      = v.description != null ? v.description : ""
      id_blocks        = v.id_blocks != null ? v.id_blocks : [{ from = "20:00:00:25:B5:0a:00:00", to = "20:00:00:25:B5:0a:00:ff" }]
      organization     = v.organization != null ? v.organization : "default"
      pool_purpose     = v.pool_purpose != null ? v.pool_purpose : "WWPN"
      tags             = v.tags != null ? v.tags : []
    }
  }
  #______________________________________________
  #
  # IP Pools
  #______________________________________________
  ip_pools = {
    for k, v in var.ip_pools : k => {
      assignment_order = v.assignment_order != null ? v.assignment_order : "default"
      description      = v.description != null ? v.description : ""
      ipv4_block       = v.ipv4_block != null ? v.ipv4_block : []
      ipv4_config      = v.ipv4_config != null ? v.ipv4_config : {}
      ipv6_block       = v.ipv6_block != null ? v.ipv6_block : []
      ipv6_config      = v.ipv6_config != null ? v.ipv6_config : {}
      organization     = v.organization != null ? v.organization : "default"
      tags             = v.tags != null ? v.tags : []
    }
  }
  #______________________________________________
  #
  # IQN Pools
  #______________________________________________
  iqn_pools = {
    for k, v in var.iqn_pools : k => {
      assignment_order = v.assignment_order != null ? v.assignment_order : "default"
      description      = v.description != null ? v.description : ""
      prefix           = v.prefix != null ? v.prefix : "iqn.1984-12.com.cisco"
      iqn_blocks       = v.iqn_suffix_blocks != null ? v.iqn_suffix_blocks : []
      organization     = v.organization != null ? v.organization : "default"
      tags             = v.tags != null ? v.tags : []
    }
  }
  #______________________________________________
  #
  # MAC Pools
  #______________________________________________
  mac_pools = {
    for k, v in var.mac_pools : k => {
      assignment_order = v.assignment_order != null ? v.assignment_order : "default"
      description      = v.description != null ? v.description : ""
      mac_blocks       = v.mac_blocks != null ? v.mac_blocks : [{ from = "00:25:B5:0a:00:00", to = "00:25:B5:0a:00:ff" }]
      organization     = v.organization != null ? v.organization : "default"
      tags             = v.tags != null ? v.tags : []
    }
  }
  #______________________________________________
  #
  # UUID Pools
  #______________________________________________
  uuid_pools = {
    for k, v in var.uuid_pools : k => {
      assignment_order = v.assignment_order != null ? v.assignment_order : "default"
      description      = v.description != null ? v.description : ""
      prefix           = v.prefix != null ? v.prefix : "000025B5-0000-0000"
      organization     = v.organization != null ? v.organization : "default"
      tags             = v.tags != null ? v.tags : []
      uuid_blocks      = v.uuid_blocks != null ? v.uuid_blocks : [{ from = "0000-000000000000", size = 1000 }]
    }
  }
}
