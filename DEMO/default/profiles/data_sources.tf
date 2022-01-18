#__________________________________________________________
#
# Get outputs from the Policies and Pools Workspaces
#__________________________________________________________

# data "terraform_remote_state" "policies" {
#   backend = "local"
#   config = {
#     path = "../policies/terraform.tfstate"
#   }
# }

# data "terraform_remote_state" "pools" {
#   backend = "local"
#   config = {
#     path = "../pools/terraform.tfstate"
#   }
# }

data "terraform_remote_state" "policies" {
  backend = "remote"
  config = {
    organization = var.tfc_organization
    workspaces = {
      name = var.ws_policies
    }
  }
}

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
