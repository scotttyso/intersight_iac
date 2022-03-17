#____________________________________________________________________________
#
# Intersight Certificate Management Policies Variables
# GUI Location: Configure > Policies > Create Policy > Certificate Management
#____________________________________________________________________________

variable "base64_certificate_1" {
  default     = ""
  description = "The Server Certificate in Base64 format."
  sensitive   = true
  type        = string
}

variable "base64_certificate_2" {
  default     = ""
  description = "The Server Certificate in Base64 format."
  sensitive   = true
  type        = string
}

variable "base64_certificate_3" {
  default     = ""
  description = "The Server Certificate in Base64 format."
  sensitive   = true
  type        = string
}

variable "base64_certificate_4" {
  default     = ""
  description = "The Server Certificate in Base64 format."
  sensitive   = true
  type        = string
}

variable "base64_certificate_5" {
  default     = ""
  description = "The Server Certificate in Base64 format."
  sensitive   = true
  type        = string
}

variable "base64_private_key_1" {
  default     = ""
  description = "Private Key in Base64 Format."
  sensitive   = true
  type        = string
}

variable "base64_private_key_2" {
  default     = ""
  description = "Private Key in Base64 Format."
  sensitive   = true
  type        = string
}

variable "base64_private_key_3" {
  default     = ""
  description = "Private Key in Base64 Format."
  sensitive   = true
  type        = string
}

variable "base64_private_key_4" {
  default     = ""
  description = "Private Key in Base64 Format."
  sensitive   = true
  type        = string
}

variable "base64_private_key_5" {
  default     = ""
  description = "Private Key in Base64 Format."
  sensitive   = true
  type        = string
}

variable "certificate_management_policies" {
  default = {
    default = {
      certificate = 1
      description = ""
      enabled     = true
      private_key = 1
      tags        = []
    }
  }
  description = <<-EOT
  key - Name of the Adapter Configuration Policy.
  * certificate - The Number of the base64_certificate Variable.  i.e. 1 = base64_certificate_1.
  * description - Description to Assign to the Policy.
  * enabled - "Enable/Disable the Certificate Management policy.
  * private_key - The Number of the base64_private_key Variable.  i.e. 1 = base64_private_key_1.
  * tags - List of Key/Value Pairs to Assign as Attributes to the Policy.
  EOT
  type = map(object(
    {
      certificate = number
      description = optional(string)
      enabled     = optional(bool)
      private_key = number
      tags        = optional(list(map(string)))
    }
  ))
}


#_________________________________________________________________________
#
# Certificate Management Policies
# GUI Location: Configure > Policies > Create Policy > Certificate Management
#_________________________________________________________________________

resource "intersight_certificatemanagement_policy" "certificate_management_policies" {
  depends_on = [
    local.org_moid
  ]
  for_each    = local.certificate_management_policies
  description = each.value.description != "" ? each.value.description : "${each.key} Certificate Management Policy."
  name        = each.key
  organization {
    moid        = local.org_moid
    object_type = "organization.Organization"
  }
  certificates {
    certificate {
      pem_certificate = length(
        regexall("1", each.value.certificate)
        ) > 0 ? var.base64_certificate_1 : length(
        regexall("2", each.value.certificate)
        ) > 0 ? var.base64_certificate_2 : length(
        regexall("3", each.value.certificate)
        ) > 0 ? var.base64_certificate_3 : length(
        regexall("4", each.value.certificate)
        ) > 0 ? var.base64_certificate_4 : length(
        regexall("5", each.value.certificate)
      ) > 0 ? var.base64_certificate_5 : null
    }
    enabled = each.value.enabled
    privatekey = length(
      regexall("1", each.value.private_key)
      ) > 0 ? var.base64_private_key_1 : length(
      regexall("2", each.value.private_key)
      ) > 0 ? var.base64_private_key_2 : length(
      regexall("3", each.value.private_key)
      ) > 0 ? var.base64_private_key_3 : length(
      regexall("4", each.value.private_key)
      ) > 0 ? var.base64_private_key_4 : length(
      regexall("5", each.value.private_key)
    ) > 0 ? var.base64_private_key_5 : null
  }
  dynamic "tags" {
    for_each = length(each.value.tags) > 0 ? each.value.tags : local.tags
    content {
      key   = tags.value.key
      value = tags.value.value
    }
  }
}
