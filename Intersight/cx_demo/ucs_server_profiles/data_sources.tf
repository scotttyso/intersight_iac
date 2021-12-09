#__________________________________________________________
#
# Get outputs from the Intersight Pools Workspace
#__________________________________________________________

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


#____________________________________________________________
#
# Intersight Organization Data Source
# GUI Location: Settings > Settings > Organizations > Name
#____________________________________________________________

data "intersight_organization_organization" "org_moid" {
  for_each = local.organizations
  name     = each.value
}

#____________________________________________________________
#
# Server Moid Data Source
# GUI Location:
#   Operate > Servers > Copy the Serial from the Column.
#____________________________________________________________

data "intersight_compute_physical_summary" "server" {
  for_each = {
    for k, v in local.ucs_server_profiles : k => v
    if v.serial_number != ""
  }
  serial = each.value.serial_number
}
