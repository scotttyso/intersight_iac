#__________________________________________________________
#
# Get outputs from the Terraform Workspaces
#__________________________________________________________

data "terraform_remote_state" "local_policies" {
  for_each = { for k, v in local.tfc_workspaces : k => v if v.backend == "local" }
  backend  = each.value.backend
  config = {
    path = "${each.value.profiles_dir}terraform.tfstate"
  }
}

data "terraform_remote_state" "local_pools" {
  for_each = { for k, v in local.tfc_workspaces : k => v if v.backend == "local" }
  backend  = each.value.backend
  config = {
    path = "${each.value.pools_dir}terraform.tfstate"
  }
}

data "terraform_remote_state" "remote_policies" {
  for_each = { for k, v in local.tfc_workspaces : k => v if v.backend == "remote" }
  backend  = each.value.backend
  config = {
    organization = each.value.tfc_organization
    workspaces = {
      name = each.value.policies_ws
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
# Chassis Moid Data Source
# GUI Location:
#   Operate > Chassis > Copy the Serial from the Column.
#____________________________________________________________

data "intersight_equipment_chassis" "chassis" {
  for_each = {
    for k, v in local.ucs_chassis_profiles : k => v
    if v.assign_chassis == true
  }
  serial = each.value.serial_number
}


#____________________________________________________________
#
# Fabric Interconnects Moid Data Source
# GUI Location:
#   Operate > Fabric Interconnects > Click the Desired Fabric
#   Interconnect > General Tab > Details Left Column > Serial
#____________________________________________________________

# Need to wait for a Bug fix to the API to Support Policy Buckets with Domain Profiles
# data "intersight_network_element_summary" "fis" {
#   for_each = {
#     for k, v in local.merged_ucs_switches : k => v
#     if v.assign_switches == true
#   }
#   serial = each.value.serial_number
# }


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
