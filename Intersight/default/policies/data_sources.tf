#__________________________________________________________
#
# Get outputs from the Terraform Workspaces
#__________________________________________________________

data "terraform_remote_state" "local_domain_profiles" {
  for_each = { for k, v in local.tfc_workspaces : k => v if v.backend == "local" }
  backend  = each.value.backend
  config = {
    path = "${each.value.domain_profiles_dir}terraform.tfstate"
  }
}

data "terraform_remote_state" "local_pools" {
  for_each = { for k, v in local.tfc_workspaces : k => v if v.backend == "local" }
  backend  = each.value.backend
  config = {
    path = "${each.value.pools_dir}terraform.tfstate"
  }
}

data "terraform_remote_state" "remote_domain_profiles" {
  for_each = { for k, v in local.tfc_workspaces : k => v if v.backend == "remote" }
  backend  = each.value.backend
  config = {
    organization = each.value.tfc_organization
    workspaces = {
      name = each.value.domain_profiles_ws
    }
  }
}

data "terraform_remote_state" "remote_pools" {
  for_each = { for k, v in local.tfc_workspaces : k => v if v.backend == "remote" }
  backend  = each.value.backend
  config = {
    organization = each.value.tfc_organization
    workspaces = {
      name = each.value.pools_ws
    }
  }
}


#____________________________________________________________
#
# Intersight Organization Data Source
# GUI Location: Settings > Settings > Organizations > Name
#____________________________________________________________

data "intersight_organization_organization" "org_moid" {
  name = var.organization
}


#____________________________________________________________
#
# Intersight User Roles Data Source
#____________________________________________________________

data "intersight_iam_end_point_role" "roles" {
  for_each = local.user_roles
  name     = each.value.role
  type     = "IMC"
}
