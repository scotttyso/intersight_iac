#__________________________________________________________
#
# IP Pool Outputs
#__________________________________________________________

output "ip_pools" {
  description = "moid of the IP Pools."
  value = var.ip_pools != {} ? { for v in sort(
    keys(intersight_ippool_pool.ip_pools)
  ) : v => intersight_ippool_pool.ip_pools[v].moid } : {}
}


#__________________________________________________________
#
# IQN Pool Outputs
#__________________________________________________________

output "iqn_pools" {
  description = "moid of the IQN Pools."
  value = var.iqn_pools != {} ? { for v in sort(
    keys(intersight_iqnpool_pool.iqn_pools)
  ) : v => intersight_iqnpool_pool.iqn_pools[v].moid } : {}
}


#__________________________________________________________
#
# MAC Pool Outputs
#__________________________________________________________

output "mac_pools" {
  description = "moid of the MAC Pools."
  value = var.mac_pools != {} ? { for v in sort(
    keys(intersight_macpool_pool.mac_pools)
  ) : v => intersight_macpool_pool.mac_pools[v].moid } : {}
}


#__________________________________________________________
#
# Resource Pool Outputs
#__________________________________________________________

output "resource_pools" {
  description = "moid of the UUID Pools."
  value = var.resource_pools != {} ? { for v in sort(
    keys(module.resource_pools)
  ) : v => module.resource_pools[v].moid } : {}
}


#__________________________________________________________
#
# UUID Pool Outputs
#__________________________________________________________

output "uuid_pools" {
  description = "moid of the UUID Pools."
  value = var.uuid_pools != {} ? { for v in sort(
    keys(intersight_uuidpool_pool.uuid_pools)
  ) : v => intersight_uuidpool_pool.uuid_pools[v].moid } : {}
}


#__________________________________________________________
#
# WWNN Pool Outputs
#__________________________________________________________

output "wwnn_pools" {
  description = "moid of the Fibre-Channel WWNN Pools."
  value = var.wwnn_pools != {} ? { for v in sort(
    keys(intersight_fcpool_pool.wwnn_pools)
  ) : v => intersight_fcpool_pool.wwnn_pools[v].moid } : {}
}


#__________________________________________________________
#
# WWPN Pool Outputs
#__________________________________________________________

output "wwpn_pools" {
  description = "moid of the Fibre-Channel WWPN Pools."
  value = var.wwpn_pools != {} ? { for v in sort(
    keys(intersight_fcpool_pool.wwpn_pools)
  ) : v => intersight_fcpool_pool.wwpn_pools[v].moid } : {}
}
