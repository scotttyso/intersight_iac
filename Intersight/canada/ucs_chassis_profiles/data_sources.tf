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
