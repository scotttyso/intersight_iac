#_______________________________________________________________________
#
# Terraform Required Parameters - Intersight Provider
# https://registry.terraform.io/providers/CiscoDevNet/intersight/latest
#_______________________________________________________________________

terraform {
  required_version = ">= 1.4.1"
  required_providers {
    intersight = {
      source  = "ciscodevnet/intersight"
      version = ">= 1.0.35"
    }
    utils = {
      source  = "netascode/utils"
      version = ">= 0.2.4"
    }
  }
}

provider "intersight" {
  apikey    = var.apikey
  endpoint  = "https://${var.endpoint}"
  secretkey = fileexists(var.secretkeyfile) ? file(var.secretkeyfile) : var.secretkey
  insecure  = true
}