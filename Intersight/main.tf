#____________________________________________________________
#
# Moid Data Source
#____________________________________________________________

data "intersight_organization_organization" "orgs" {
}
#_________________________________________________________________________________________
#
# Data Model Merge Process - Merge YAML Files into HCL Format
#_________________________________________________________________________________________
data "utils_yaml_merge" "model" {
  input = concat([
    for file in fileset(path.module, "defaults/*.yaml") : file(file)], [
    for file in fileset(path.module, "policies/*.yaml") : file(file)], [
    for file in fileset(path.module, "pools/*.yaml") : file(file)], [
    for file in fileset(path.module, "profiles/*.yaml") : file(file)], [
    for file in fileset(path.module, "templates/*.yaml") : file(file)]
  )
  merge_list_items = false
}

locals {
  chassis = { for i in flatten([for key, value in module.profiles : [
    for k, v in value.chassis : {
      action          = v.action
      moid            = v.moid
      name            = k
      organization    = key
      serial_number   = v.serial_number
      target_platform = v.target_platform
    }
    ]
  ]) : "${i.organization}:${i.name}" => i }
  model = yamldecode(data.utils_yaml_merge.model.output)
  orgs  = { for k, v in data.intersight_organization_organization.orgs.results : v.name => v.moid }
  server = { for i in flatten([for key, value in module.profiles : [
    for k, v in value.server : {
      action               = v.action
      create_from_template = v.create_from_template
      moid                 = v.moid
      name                 = k
      organization         = key
      serial_number        = v.serial_number
      target_platform      = v.target_platform
    }
    ]
  ]) : "${i.organization}:${i.name}" => i }
  switch_profiles = { for i in flatten([for key, value in module.domain_profiles : [
    for k, v in value.switch_profiles : {
      action        = v.action
      domain_moid   = module.domain_profiles[key].domains[v.domain_profile]
      moid          = v.moid
      name          = k
      organization  = key
      serial_number = v.serial_number
    }
    ]
  ]) : "${i.organization}:${i.name}" => i }
  wait_for_domain = distinct(compact([for i in local.switch_profiles : i.action if i.action != "No-op"]))
  template = { for i in flatten([for key, value in module.profiles : [
    for k, v in value.template : {
      create_template = v.create_template
      moid            = v.moid
      name            = k
      organization    = key
      target_platform = v.target_platform
    }
    ]
  ]) : "${i.organization}:${i.name}" => i }
  create_template = [for v in local.template : true if v.create_template == true]
}

#_________________________________________________________________________________________
#
# Intersight:Pools
# GUI Location: Infrastructure Service > Configure > Pools
#_________________________________________________________________________________________
module "pools" {
  #source = "../../../../terraform-cisco-modules/terraform-intersight-pools"
  source       = "terraform-cisco-modules/pools/intersight"
  version      = "2.0.1"
  for_each     = { for i in sort(keys(local.model)) : i => lookup(local.model[i], "pools", {}) if i != "intersight" }
  defaults     = local.model.intersight.defaults.pools
  pools        = each.value
  organization = each.key
  orgs         = local.orgs
  tags         = var.tags
}

#_________________________________________________________________________________________
#
# Intersight:UCS Domain Profiles
# GUI Location: Infrastructure Service > Configure > Profiles : UCS Domain Profiles
#_________________________________________________________________________________________
module "domain_profiles" {
  #source = "../../../../terraform-cisco-modules/terraform-intersight-profiles-domain"
  source         = "terraform-cisco-modules/profiles-domain/intersight"
  version        = "2.0.1"
  for_each       = { for i in sort(keys(local.model)) : i => lookup(local.model[i], "profiles", {}) if i != "intersight" }
  defaults       = local.model.intersight.defaults.profiles
  moids_policies = var.moids_policies
  moids_pools    = var.moids_pools
  organization   = each.key
  orgs           = local.orgs
  profiles       = each.value
  tags           = var.tags
  #policies     = module.policies
}

#_________________________________________________________________________________________
#
# Intersight:Policies
# GUI Location: Infrastructure Service > Configure > Policies
#_________________________________________________________________________________________
module "policies" {
  #source = "../../../../terraform-cisco-modules/terraform-intersight-policies"
  source         = "terraform-cisco-modules/policies/intersight"
  version        = "2.0.1"
  for_each       = { for i in sort(keys(local.model)) : i => lookup(local.model[i], "policies", {}) if i != "intersight" }
  defaults       = local.model.intersight.defaults.policies
  domains        = module.domain_profiles
  moids_policies = var.moids_policies
  moids_pools    = var.moids_pools
  organization   = each.key
  orgs           = local.orgs
  policies       = each.value
  pools          = module.pools
  tags           = var.tags
  # Certificate Management Sensitive Variables
  base64_certificate_1 = var.base64_certificate_1
  base64_certificate_2 = var.base64_certificate_2
  base64_certificate_3 = var.base64_certificate_3
  base64_certificate_5 = var.base64_certificate_4
  base64_certificate_4 = var.base64_certificate_5
  base64_private_key_1 = var.base64_private_key_1
  base64_private_key_2 = var.base64_private_key_2
  base64_private_key_3 = var.base64_private_key_3
  base64_private_key_4 = var.base64_private_key_4
  base64_private_key_5 = var.base64_private_key_5
  # IPMI Sensitive Variables
  ipmi_key_1 = var.ipmi_key
  # iSCSI Boot Sensitive Variable
  iscsi_boot_password = var.iscsi_boot_password
  # LDAP Sensitive Variable
  binding_parameters_password = var.binding_parameters_password
  # Local User Sensitive Variables
  local_user_password_1 = var.local_user_password_1
  local_user_password_2 = var.local_user_password_2
  local_user_password_3 = var.local_user_password_3
  local_user_password_4 = var.local_user_password_4
  local_user_password_5 = var.local_user_password_5
  # Persistent Memory Sensitive Variable
  persistent_passphrase = var.persistent_passphrase
  # SNMP Sensitive Variables
  access_community_string_1 = var.access_community_string_1
  access_community_string_2 = var.access_community_string_2
  access_community_string_3 = var.access_community_string_3
  access_community_string_4 = var.access_community_string_4
  access_community_string_5 = var.access_community_string_5
  snmp_auth_password_1      = var.snmp_auth_password_1
  snmp_auth_password_2      = var.snmp_auth_password_2
  snmp_auth_password_3      = var.snmp_auth_password_3
  snmp_auth_password_4      = var.snmp_auth_password_4
  snmp_auth_password_5      = var.snmp_auth_password_5
  snmp_privacy_password_1   = var.snmp_privacy_password_1
  snmp_privacy_password_2   = var.snmp_privacy_password_2
  snmp_privacy_password_3   = var.snmp_privacy_password_3
  snmp_privacy_password_4   = var.snmp_privacy_password_4
  snmp_privacy_password_5   = var.snmp_privacy_password_5
  snmp_trap_community_1     = var.snmp_trap_community_1
  snmp_trap_community_2     = var.snmp_trap_community_2
  snmp_trap_community_3     = var.snmp_trap_community_3
  snmp_trap_community_4     = var.snmp_trap_community_4
  snmp_trap_community_5     = var.snmp_trap_community_5
  # Virtual Media Sensitive Variable
  vmedia_password_1 = var.vmedia_password_1
  vmedia_password_2 = var.vmedia_password_2
  vmedia_password_3 = var.vmedia_password_3
  vmedia_password_4 = var.vmedia_password_4
  vmedia_password_5 = var.vmedia_password_5
}

#_________________________________________________________________________________________
#
# Intersight: UCS Domain Profiles
# GUI Location: Infrastructure Service > Configure > Profiles : UCS Domain Profiles
#_________________________________________________________________________________________
resource "intersight_fabric_switch_profile" "switch_profiles" {
  depends_on = [
    module.policies
  ]
  for_each = local.switch_profiles
  action = length(regexall(
    "^[A-Z]{3}[2-3][\\d]([0][1-9]|[1-4][0-9]|[5][1-3])[\\dA-Z]{4}$", each.value.serial_number)
  ) > 0 ? each.value.action : "No-op"
  lifecycle {
    ignore_changes = [
      action_params,
      ancestors,
      assigned_switch,
      create_time,
      description,
      domain_group_moid,
      mod_time,
      owners,
      parent,
      permission_resources,
      policy_bucket,
      running_workflows,
      shared_scope,
      src_template,
      tags,
      version_context
    ]
  }
  name = each.value.name
  switch_cluster_profile {
    moid = each.value.domain_moid
  }
  wait_for_completion = local.switch_profiles[
    element(keys(local.switch_profiles), length(keys(local.switch_profiles)
  ) - 1)].name == each.value.name ? true : false
}

#_________________________________________________________________________________________
#
# Sleep Timer between Deploying the Domain and Waiting for Server Discovery
#_________________________________________________________________________________________
resource "time_sleep" "wait_for_server_discovery" {
  depends_on = [
    intersight_fabric_switch_profile.switch_profiles
  ]
  create_duration = length([
    for v in keys(local.switch_profiles) : 1 if local.switch_profiles[v
  ].action == "Deploy"]) > 0 ? "30m" : "1s"
  triggers = {
    always_run = length(local.wait_for_domain) > 0 ? "${timestamp()}" : 1
  }
}


#_________________________________________________________________________________________
#
# Intersight:UCS Chassis and Server Profiles
# GUI Location: Infrastructure Service > Configure > Profiles
#_________________________________________________________________________________________
module "profiles" {
  #source = "../../../../terraform-cisco-modules/terraform-intersight-profiles"
  source         = "terraform-cisco-modules/profiles/intersight"
  version        = "2.0.2"
  for_each       = { for i in sort(keys(local.model)) : i => local.model[i] if i != "intersight" }
  defaults       = local.model.intersight.defaults
  moids_policies = var.moids_policies
  moids_pools    = var.moids_pools
  organization   = each.key
  orgs           = local.orgs
  policies       = module.policies
  pools          = module.pools
  profiles       = each.value
  model          = local.model
  tags           = var.tags
  time_sleep     = time_sleep.wait_for_server_discovery.id
}

#_________________________________________________________________________________________
#
# Intersight: UCS Chassis Profiles
# GUI Location: Infrastructure Service > Configure > Profiles : UCS Chassis Profiles
#_________________________________________________________________________________________
resource "intersight_chassis_profile" "chassis" {
  depends_on = [
    module.profiles
  ]
  for_each = local.chassis
  action = length(regexall(
    "^[A-Z]{3}[2-3][\\d]([0][1-9]|[1-4][0-9]|[5][1-3])[\\dA-Z]{4}$", each.value.serial_number)
  ) > 0 ? each.value.action : "No-op"
  lifecycle {
    ignore_changes = [
      action_params,
      ancestors,
      create_time,
      description,
      domain_group_moid,
      mod_time,
      owners,
      parent,
      permission_resources,
      policy_bucket,
      running_workflows,
      shared_scope,
      src_template,
      tags,
      version_context
    ]
  }
  name            = each.value.name
  target_platform = each.value.target_platform
  organization {
    moid = local.orgs[each.value.organization]
  }
}

#_________________________________________________________________________________________
#
# Intersight: UCS Server Profiles
# GUI Location: Infrastructure Service > Configure > Profiles : UCS Server Profiles
#_________________________________________________________________________________________
resource "intersight_server_profile" "server" {
  depends_on = [
    module.profiles
  ]
  for_each = { for k, v in local.server : k => v if v.create_from_template == false }
  action = length(regexall(
    "^[A-Z]{3}[2-3][\\d]([0][1-9]|[1-4][0-9]|[5][1-3])[\\dA-Z]{4}$", each.value.serial_number)
  ) > 0 ? each.value.action : "No-op"
  lifecycle {
    ignore_changes = [
      action_params,
      ancestors,
      assigned_server,
      associated_server,
      associated_server_pool,
      create_time,
      description,
      domain_group_moid,
      mod_time,
      owners,
      parent,
      permission_resources,
      policy_bucket,
      reservation_references,
      running_workflows,
      server_assignment_mode,
      server_pool,
      shared_scope,
      src_template,
      tags,
      target_platform,
      uuid,
      uuid_address_type,
      uuid_lease,
      uuid_pool,
      version_context
    ]
  }
  name = each.value.name
  organization {
    moid = local.orgs[each.value.organization]
  }
}

