#__________________________________________________________
#
# UCS Domain Profile Outputs
#__________________________________________________________

output "moids" {
  value = var.ucs_domain_profiles != {} ? { for v in sort(
    keys(intersight_fabric_switch_profile.ucs_domain_switches)
  ) : v => intersight_fabric_switch_profile.ucs_domain_switches[v].moid } : {}
}

output "ucs_domain_profiles" {
  value = local.merged_ucs_switches
}
