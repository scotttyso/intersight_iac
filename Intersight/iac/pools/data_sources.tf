#____________________________________________________________
#
# Intersight Organization Data Source
# GUI Location: Settings > Settings > Organizations > Name
#____________________________________________________________

data "intersight_organization_organization" "org_moid" {
  name = var.organization
}
