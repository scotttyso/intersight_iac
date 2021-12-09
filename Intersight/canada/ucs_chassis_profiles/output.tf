#__________________________________________________________
#
# UCS Chassis Profile Outputs
#__________________________________________________________

output "moids" {
  value = {
    for v in sort(keys(module.ucs_chassis_profiles)) : v => module.ucs_chassis_profiles[v].moid
    if v != null
  }
}

output "ucs_chassis_profiles" {
  value = local.ucs_chassis_profiles
}
