terraform {
  experiments = [module_variable_optional_attrs]
}

#__________________________________________________________
#
# Intersight Provider Variables
#__________________________________________________________

variable "apikey" {
  description = "Intersight API Key."
  sensitive   = true
  type        = string
}

variable "endpoint" {
  default     = "https://intersight.com"
  description = "Intersight URL."
  type        = string
}

variable "secretkey" {
  description = "Intersight Secret Key."
  sensitive   = true
  type        = string
}


#__________________________________________________________
#
# Global Variables
#__________________________________________________________

variable "organizations" {
  default     = ["default"]
  description = "Intersight Organization Names to Apply Policy to.  https://intersight.com/an/settings/organizations/."
  type        = set(string)
}

variable "tags" {
  default     = []
  description = "Tags to be Associated with Objects Created in Intersight."
  type        = list(map(string))
}


#______________________________________________
#
# IP Pool Variables
#______________________________________________

variable "ip_pools" {
  default = {
    default = {
      assignment_order = "default"
      description      = ""
      ipv4_block       = []
      ipv4_config      = {}
      ipv6_block       = []
      ipv6_config      = {}
      organization     = "default"
      tags             = []
    }
  }
  description = <<-EOT
  key - Name of the IP Pool.
  * Assignment order decides the order in which the next identifier is allocated.
    - default - (Default) Assignment order is decided by the system.
    - sequential - Identifiers are assigned in a sequential order.
  * description - Description to Assign to the Pool.
  * ipv4_block - Map of Addresses to Assign to the Pool.
    - from - Starting IPv4 Address.
    - to - Ending IPv4 Address.
    - primary_dns = Primary DNS Server to Assign to the Pool
    - secondary_dns = Secondary DNS Server to Assign to the Pool
  * ipv4_config - IPv4 Configuration to assign to the ipv4_blocks.
    - gateway - Gateway to assign to the pool.
    - netmask - Netmask to assign to the pool.
  * ipv6_block - Map of Addresses to Assign to the Pool.
    - from - Starting IPv6 Address.
    - pool_size - Size of the IPv6 Address Block.
  * ipv6_config - IPv6 Configuration to assign to the ipv6_blocks.
    - gateway - Gateway to assign to the pool.
    - netmask - Netmask to assign to the pool.
    - primary_dns = Primary DNS Server to Assign to the Pool
    - secondary_dns = Secondary DNS Server to Assign to the Pool
  * organization - Name of the Intersight Organization to assign this pool to.  Default is default.
    - https://intersight.com/an/settings/organizations/
  * tags - List of Key/Value Pairs to Assign as Attributes to the Pool.
  EOT
  type = map(object(
    {
      assignment_order = optional(string)
      description      = optional(string)
      ipv4_block       = optional(list(map(string)))
      ipv4_config = optional(map(object(
        {
          gateway       = string
          netmask       = string
          primary_dns   = optional(string)
          secondary_dns = optional(string)
        }
      )))
      ipv6_block = optional(list(map(string)))
      ipv6_config = optional(map(object(
        {
          gateway       = string
          prefix        = number
          primary_dns   = optional(string)
          secondary_dns = optional(string)
        }
      )))
      organization = optional(string)
      tags         = optional(list(map(string)))
    }
  ))
}


#______________________________________________
#
# IQN Pool Variables
#______________________________________________

variable "iqn_pools" {
  default = {
    default = { # The Pool Name will be {each.key}.  In this case it would be default if left like this.
      assignment_order = "default"
      description      = ""
      prefix           = "iqn.1984-12.com.cisco"
      organization     = "default"
      tags             = []
      iqn_blocks = [
        {
          from   = 1
          size   = 255
          suffix = "ucs-host"
        }
      ]
    }
  }
  description = <<-EOT
  key - Name of the IQN Pool.
  * Assignment order decides the order in which the next identifier is allocated.
    - default - (Default) Assignment order is decided by the system.
    - sequential - Identifiers are assigned in a sequential order.
  * description - Description to Assign to the Pool.
  * iqn_blocks - Map of Addresses to Assign to the Pool.
    - pool_size - staring WWxN Address.  Default is 255.
    - starting_iqn - ending WWxN Address.  Default is 01.
    - suffix - Suffix to assign to the IQN Pool.  Default is "ucs-host".
  * organization - Name of the Intersight Organization to assign this pool to.  Default is default.
    - https://intersight.com/an/settings/organizations/
  * prefix - The prefix for IQN blocks created for this pool.  The default is "iqn.1984-12.com.cisco".
  * tags - List of Key/Value Pairs to Assign as Attributes to the Pool.
  EOT
  type = map(object(
    {
      assignment_order = optional(string)
      description      = optional(string)
      iqn_blocks       = optional(list(map(string)))
      organization     = optional(string)
      prefix           = optional(string)
      tags             = optional(list(map(string)))
    }
  ))
}


#______________________________________________
#
# MAC Pool Variables
#______________________________________________

variable "mac_pools" {
  default = {
    default = { # The Pool Name will be {each.key}.  In this case it would be default if left like this.
      assignment_order = "default"
      description      = ""
      organization     = "default"
      tags             = []
      mac_blocks = [
        {
          from = "00:25:B5:0a:00:00"
          to   = "00:25:B5:0a:00:ff"
        }
      ]
    }
  }
  description = <<-EOT
  key - Name of the MAC Pool.
  * Assignment order decides the order in which the next identifier is allocated.
    - default - (Default) Assignment order is decided by the system.
    - sequential - Identifiers are assigned in a sequential order.
  * description - Description to Assign to the Pool.
  * mac_blocks - Map of Addresses to Assign to the Pool.
    - from - staring MAC Address.  Default is "00:25:B5:0a:00:00".
    - to - ending MAC Address.  Default is "00:25:B5:0a:00:ff".
  * organization - Name of the Intersight Organization to assign this pool to.  Default is default.
    - https://intersight.com/an/settings/organizations/
  * tags - List of Key/Value Pairs to Assign as Attributes to the Pool.
  EOT
  type = map(object(
    {
      assignment_order = optional(string)
      description      = optional(string)
      mac_blocks       = optional(list(map(string)))
      organization     = optional(string)
      tags             = optional(list(map(string)))
    }
  ))
}


#______________________________________________
#
# UUID Pool Variables
#______________________________________________

variable "uuid_pools" {
  default = {
    default = { # The Pool Name will be {each.key}.  In this case it would be default if left like this.
      assignment_order = "default"
      description      = ""
      organization     = "default"
      prefix           = "000025B5-0000-0000"
      tags             = []
      uuid_blocks = [
        {
          from = "0000-000000000000"
          size = 1000
        }
      ]
    }
  }
  description = <<-EOT
  key - Name of the UUID Pool.
  * Assignment order decides the order in which the next identifier is allocated.
    - default - (Default) Assignment order is decided by the system.
    - sequential - Identifiers are assigned in a sequential order.
  * description - Description to Assign to the Pool.
  * prefix - Prefix to assign to the UUID Pool..  The default is "000025B5-0000-0000".
  * uuid_blocks - Map of Addresses to Assign to the Pool.
    - from - Starting UUID Address.  Default is "0000-000000000000".
    - size - Size of UUID Pool.  Default is "32768".
  * organization - Name of the Intersight Organization to assign this pool to.  Default is default.
    - https://intersight.com/an/settings/organizations/
  * tags - List of Key/Value Pairs to Assign as Attributes to the Pool.
  EOT
  type = map(object(
    {
      assignment_order = optional(string)
      description      = optional(string)
      organization     = optional(string)
      prefix           = optional(string)
      tags             = optional(list(map(string)))
      uuid_blocks      = optional(list(map(string)))
    }
  ))
}


#______________________________________________
#
# WWxN Pool Variables
#______________________________________________

variable "wwnn_pools" {
  default = {
    default = {
      assignment_order = "default"
      description      = ""
      organization     = "default"
      pool_purpose     = "WWNN"
      tags             = []
      id_blocks = [
        {
          from = "20:00:00:25:B5:00:00:00"
          to   = "20:00:00:25:B5:00:00:ff"
        }
      ]
    }
  }
  description = <<-EOT
  key - Name of the Fibre-Channel Pool.
  * Assignment order decides the order in which the next identifier is allocated.
    - default - Assignment order is decided by the system - Default value.
    - sequential - Identifiers are assigned in a sequential order.
  * description - Description to Assign to the Pool.
  * id_blocks - Map of Addresses to Assign to the Pool.
    - from - staring WWxN Address.  Default is "20:00:00:25:B5:0a:00:00".
    - to - ending WWxN Address.  Default is "20:00:00:25:B5:0a:00:ff".
  * pool_purpose - What type of Fiber-Channel Pool is this.  Options are:
    - WWNN - (Default)
    - WWPN
  * organization - Name of the Intersight Organization to assign this pool to.  Default is default.
    - https://intersight.com/an/settings/organizations/
  * tags - List of Key/Value Pairs to Assign as Attributes to the Pool.
  EOT
  type = map(object(
    {
      assignment_order = optional(string)
      description      = optional(string)
      id_blocks        = optional(list(map(string)))
      organization     = optional(string)
      pool_purpose     = optional(string)
      tags             = optional(list(map(string)))
    }
  ))
}

variable "wwpn_pools" {
  default = {
    default = {
      assignment_order = "default"
      description      = ""
      organization     = "default"
      pool_purpose     = "WWPN"
      tags             = []
      id_blocks = [
        {
          from = "20:00:00:25:B5:0a:00:00"
          to   = "20:00:00:25:B5:0a:00:ff"
        }
      ]
    }
  }
  description = <<-EOT
  key - Name of the Fibre-Channel Pool.
  * Assignment order decides the order in which the next identifier is allocated.
    - default - Assignment order is decided by the system - Default value.
    - sequential - Identifiers are assigned in a sequential order.
  * description - Description to Assign to the Pool.
  * id_blocks - Map of Addresses to Assign to the Pool.
    - from - staring WWxN Address.  Default is "20:00:00:25:B5:0a:00:00".
    - to - ending WWxN Address.  Default is "20:00:00:25:B5:0a:00:ff".
  * pool_purpose - What type of Fiber-Channel Pool is this.  Options are:
    - WWNN
    - WWPN - (Default)
  * organization - Name of the Intersight Organization to assign this pool to.  Default is default.
    - https://intersight.com/an/settings/organizations/
  * tags - List of Key/Value Pairs to Assign as Attributes to the Pool.
  EOT
  type = map(object(
    {
      assignment_order = optional(string)
      description      = optional(string)
      id_blocks        = optional(list(map(string)))
      organization     = optional(string)
      pool_purpose     = optional(string)
      tags             = optional(list(map(string)))
    }
  ))
}
