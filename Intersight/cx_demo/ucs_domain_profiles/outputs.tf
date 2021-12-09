#__________________________________________________________
#
# UCS Domain Profile Outputs
#__________________________________________________________

output "moids" {
  value = {
    for v in sort(keys(module.ucs_domain_switches)) : v => module.ucs_domain_switches[v].moid
    if v != null
  }
}

output "ucs_domain_profiles" {
  value = local.merged_ucs_switches
}
