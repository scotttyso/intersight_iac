#__________________________________________________________
#
# Get outputs from the domains Workspace
#__________________________________________________________

# data "terraform_remote_state" "domain" {
#   backend = "local"
#   config = {
#     path = "../ucs_domain_profiles/terraform.tfstate"
#   }
# }

data "terraform_remote_state" "domain" {
  backend = "remote"
  config = {
    organization = var.tfc_organization
    workspaces = {
      name = var.ws_ucs_domain_profiles
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
