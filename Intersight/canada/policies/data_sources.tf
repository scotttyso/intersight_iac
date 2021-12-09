#__________________________________________________________
#
# Get outputs from the Intersight Pools Workspace
#__________________________________________________________

# data "terraform_remote_state" "ucs_chassis_profiles" {
#   backend = "local"
#   config = {
#     path = "../ucs_chassis_profiles/terraform.tfstate"
#   }
# }
#
# data "terraform_remote_state" "ucs_domain_profiles" {
#   backend = "local"
#   config = {
#     path = "../ucs_domain_profiles/terraform.tfstate"
#   }
# }
#
# data "terraform_remote_state" "ucs_server_profiles" {
#   backend = "local"
#   config = {
#     path = "../ucs_server_profiles/terraform.tfstate"
#   }
# }
#
# data "terraform_remote_state" "pools" {
#   backend = "local"
#   config = {
#     path = "../pools/terraform.tfstate"
#   }
# }

data "terraform_remote_state" "pools" {
  backend = "remote"
  config = {
    organization = var.tfc_organization
    workspaces = {
      name = var.ws_pools
    }
  }
}

data "terraform_remote_state" "ucs_chassis_profiles" {
  backend = "remote"
  config = {
    organization = var.tfc_organization
    workspaces = {
      name = var.ws_ucs_chassis_profiles
    }
  }
}

data "terraform_remote_state" "ucs_domain_profiles" {
  backend = "remote"
  config = {
    organization = var.tfc_organization
    workspaces = {
      name = var.ws_ucs_domain_profiles
    }
  }
}

data "terraform_remote_state" "ucs_server_profiles" {
  backend = "remote"
  config = {
    organization = var.tfc_organization
    workspaces = {
      name = var.ws_ucs_server_profiles
    }
  }
}


#____________________________________________________________
#
# Intersight Organization Data Source
# GUI Location: Settings > Settings > Organizations > Name
#____________________________________________________________

data "intersight_organization_organization" "org_moid" {
  for_each = local.organizations
  name     = each.value
}
