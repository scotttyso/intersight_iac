#__________________________________________________________
#
# UCS Server Profile Outputs
#__________________________________________________________

output "moids" {
  value = {
    for v in sort(keys(module.ucs_server_profiles)) : v => module.ucs_server_profiles[v].moid
    if v != null
  }
}

output "ucs_server_profiles" {
  value = local.ucs_server_profiles
}

# output "ucs_server_profile_templates" {
#   value = local.ucs_server_profile_templates
# }
