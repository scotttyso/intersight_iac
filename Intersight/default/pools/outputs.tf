#__________________________________________________________
#
# Fibre-Channel Pool Outputs
#__________________________________________________________

output "wwnn_pools" {
  description = "moid of the Fibre-Channel WWNN Pools."
  value       = var.wwnn_pools != {} ? { for v in sort(keys(module.wwnn_pools)) : v => module.wwnn_pools[v].moid } : {}
}

output "wwpn_pools" {
  description = "moid of the Fibre-Channel WWPN Pools."
  value       = var.wwpn_pools != {} ? { for v in sort(keys(module.wwpn_pools)) : v => module.wwpn_pools[v].moid } : {}
}


#__________________________________________________________
#
# IP Pool Outputs
#__________________________________________________________

output "ip_pools" {
  description = "moid of the IP Pools."
  value       = var.ip_pools != {} ? { for v in sort(keys(module.ip_pools)) : v => module.ip_pools[v].moid } : {}
}


#__________________________________________________________
#
# IQN Pool Outputs
#__________________________________________________________

output "iqn_pools" {
  description = "moid of the IQN Pools."
  value       = var.iqn_pools != {} ? { for v in sort(keys(module.iqn_pools)) : v => module.iqn_pools[v].moid } : {}
}


#__________________________________________________________
#
# MAC Pool Outputs
#__________________________________________________________

output "mac_pools" {
  description = "moid of the MAC Pools."
  value       = var.mac_pools != {} ? { for v in sort(keys(module.mac_pools)) : v => module.mac_pools[v].moid } : {}
}


#__________________________________________________________
#
# UUID Pool Outputs
#__________________________________________________________

output "uuid_pools" {
  description = "moid of the UUID Pools."
  value       = var.uuid_pools != {} ? { for v in sort(keys(module.uuid_pools)) : v => module.uuid_pools[v].moid } : {}
}
