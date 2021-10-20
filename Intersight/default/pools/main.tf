
#____________________________________________________________
#
# Intersight Pools Module
# GUI Location: Pools > Create Pool
#____________________________________________________________

#______________________________________________
#
# Fibre-Channel Pools
#______________________________________________

module "wwnn_pools" {
  depends_on = [
    local.org_moids
  ]
  source           = "terraform-cisco-modules/imm/intersight//modules/fc_pools"
  for_each         = local.wwnn_pools
  assignment_order = each.value.assignment_order
  description      = each.value.description != "" ? each.value.description : "${each.value.organization} ${each.key} ${each.value.pool_purpose} Pool."
  id_blocks        = each.value.id_blocks
  name             = each.key
  org_moid         = local.org_moids[each.value.organization].moid
  pool_purpose     = each.value.pool_purpose
  tags             = each.value.tags != [] ? each.value.tags : local.tags
}


module "wwpn_pools" {
  depends_on = [
    local.org_moids
  ]
  source           = "terraform-cisco-modules/imm/intersight//modules/fc_pools"
  for_each         = local.wwpn_pools
  assignment_order = each.value.assignment_order
  description      = each.value.description != "" ? each.value.description : "${each.value.organization} ${each.key} ${each.value.pool_purpose} Pool."
  id_blocks        = each.value.id_blocks
  name             = each.key
  org_moid         = local.org_moids[each.value.organization].moid
  pool_purpose     = each.value.pool_purpose
  tags             = each.value.tags != [] ? each.value.tags : local.tags
}


#______________________________________________
#
# IP Pools
#______________________________________________

module "ip_pools" {
  depends_on = [
    local.org_moids
  ]
  source           = "terraform-cisco-modules/imm/intersight//modules/ip_pools"
  for_each         = local.ip_pools
  assignment_order = each.value.assignment_order
  description      = each.value.description != "" ? each.value.description : "${each.value.organization} ${each.key} IP Pool."
  ipv4_block       = each.value.ipv4_block
  ipv4_config      = each.value.ipv4_config
  ipv6_block       = each.value.ipv6_block
  ipv6_config      = each.value.ipv6_config
  name             = each.key
  org_moid         = local.org_moids[each.value.organization].moid
  tags             = each.value.tags != [] ? each.value.tags : local.tags
}


#______________________________________________
#
# IQN Pools
#______________________________________________

module "iqn_pools" {
  depends_on = [
    local.org_moids
  ]
  source           = "terraform-cisco-modules/imm/intersight//modules/iqn_pools"
  for_each         = local.iqn_pools
  assignment_order = each.value.assignment_order
  description      = each.value.description != "" ? each.value.description : "${each.value.organization} ${each.key} IQN Pool."
  prefix           = each.value.prefix
  iqn_blocks       = each.value.iqn_blocks
  name             = each.key
  org_moid         = local.org_moids[each.value.organization].moid
  tags             = each.value.tags != [] ? each.value.tags : local.tags
}


#______________________________________________
#
# MAC Pools
#______________________________________________

module "mac_pools" {
  depends_on = [
    local.org_moids
  ]
  source           = "terraform-cisco-modules/imm/intersight//modules/mac_pools"
  for_each         = local.mac_pools
  assignment_order = each.value.assignment_order
  description      = each.value.description != "" ? each.value.description : "${each.value.organization} ${each.key} MAC Pool."
  mac_blocks       = each.value.mac_blocks
  name             = each.key
  org_moid         = local.org_moids[each.value.organization].moid
  tags             = each.value.tags != [] ? each.value.tags : local.tags
}


#______________________________________________
#
# UUID Pools
#______________________________________________

module "uuid_pools" {
  depends_on = [
    local.org_moids
  ]
  source           = "terraform-cisco-modules/imm/intersight//modules/uuid_pools"
  for_each         = local.uuid_pools
  assignment_order = each.value.assignment_order
  description      = each.value.description != "" ? each.value.description : "${each.value.organization} ${each.key} UUID Pool."
  name             = each.key
  org_moid         = local.org_moids[each.value.organization].moid
  prefix           = each.value.prefix
  tags             = each.value.tags != [] ? each.value.tags : local.tags
  uuid_blocks      = each.value.uuid_blocks
}
