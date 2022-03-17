#__________________________________________________________
#
# Local Variables Section
#__________________________________________________________

locals {
  # Intersight Organization Variable
  org_moid = data.intersight_organization_organization.org_moid.results[0].moid

  # Intersight Provider Variables
  endpoint = var.endpoint

  # Tags for Deployment
  tags = var.tags


  #______________________________________________
  #
  # IP Pools
  #______________________________________________
  ip_pools = {
    for k, v in var.ip_pools : k => {
      assignment_order = v.assignment_order != null ? v.assignment_order : "default"
      description      = v.description != null ? v.description : ""
      ipv4_blocks      = v.ipv4_blocks != null ? v.ipv4_blocks : {}
      ipv4_config      = v.ipv4_config != null ? v.ipv4_config : {}
      ipv6_blocks      = v.ipv6_blocks != null ? v.ipv6_blocks : {}
      ipv6_config      = v.ipv6_config != null ? v.ipv6_config : {}
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
      iqn_blocks       = v.iqn_blocks != null ? v.iqn_blocks : {}
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
      mac_blocks       = v.mac_blocks != null ? v.mac_blocks : {}
      tags             = v.tags != null ? v.tags : []
    }
  }


  #______________________________________________
  #
  # Resource Pools
  #______________________________________________
  resource_pools = {
    for k, v in var.resource_pools : k => {
      assignment_order   = v.assignment_order != null ? v.assignment_order : "default"
      description        = v.description != null ? v.description : ""
      pool_type          = v.pool_type != null ? v.pool_type : "Static"
      resource_type      = v.resource_type != null ? v.resource_type : "Server"
      serial_number_list = v.serial_number_list
      server_type        = v.server_type != null ? v.server_type : "Blades"
      tags               = v.tags != null ? v.tags : []
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
      tags             = v.tags != null ? v.tags : []
      uuid_blocks      = v.uuid_blocks != null ? v.uuid_blocks : {}
    }
  }


  #______________________________________________
  #
  # WWNN Pools
  #______________________________________________
  wwnn_pools = {
    for k, v in var.wwnn_pools : k => {
      assignment_order = v.assignment_order != null ? v.assignment_order : "default"
      description      = v.description != null ? v.description : ""
      id_blocks        = v.id_blocks != null ? v.id_blocks : {}
      tags             = v.tags != null ? v.tags : []
    }
  }


  #______________________________________________
  #
  # WWPN Pools
  #______________________________________________
  wwpn_pools = {
    for k, v in var.wwpn_pools : k => {
      assignment_order = v.assignment_order != null ? v.assignment_order : "default"
      description      = v.description != null ? v.description : ""
      id_blocks        = v.id_blocks != null ? v.id_blocks : {}
      tags             = v.tags != null ? v.tags : []
    }
  }
}
