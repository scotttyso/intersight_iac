#__________________________________________________________
#
# UCS Chassis Profile Outputs
#__________________________________________________________

output "chassis_moids" {
  value = var.ucs_chassis_profiles != {} ? { for v in sort(
    keys(intersight_chassis_profile.ucs_chassis_profiles)
  ) : v => intersight_chassis_profile.ucs_chassis_profiles[v].moid } : {}
}

output "ucs_chassis_profiles" {
  value = local.ucs_chassis_profiles
}


#__________________________________________________________
#
# UCS Domain Profile Outputs
#__________________________________________________________

# Need to wait for a Bug fix to the API to Support Policy Buckets with Domain Profiles
# output "domain_moids" {
#   value = var.ucs_domain_profiles != {} ? { for v in sort(
#     keys(intersight_fabric_switch_profile.ucs_domain_switches)
#   ) : v => intersight_fabric_switch_profile.ucs_domain_switches[v].moid } : {}
# }

# Need to wait for a Bug fix to the API to Support Policy Buckets with Domain Profiles
# output "ucs_domain_profiles" {
#   value = local.merged_ucs_switches
# }


#__________________________________________________________
#
# UCS Server Profile Outputs
#__________________________________________________________

output "server_moids" {
  value = var.ucs_server_profiles != {} ? { for v in sort(
    keys(intersight_server_profile.ucs_server_profiles)
  ) : v => intersight_server_profile.ucs_server_profiles[v].moid } : {}
}

output "ucs_server_profiles" {
  value = local.ucs_server_profiles
}
