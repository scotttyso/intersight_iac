#_________________________________________________________________________
#
# Intersight Port Policy Variables
# GUI Location: Configure > Policies > Create Policy > Port > Start
#_________________________________________________________________________

variable "port_policies" {
  default = {
    default = {
      description                   = ""
      device_model                  = "UCS-FI-6454"
      organization                  = "default"
      port_channel_appliances       = {}
      port_channel_ethernet_uplinks = {}
      port_channel_fc_uplinks       = {}
      port_channel_fcoe_uplinks     = {}
      port_modes                    = []
      port_role_appliances          = {}
      port_role_ethernet_uplinks    = {}
      port_role_fc_uplinks          = {}
      port_role_fcoe_uplinks        = {}
      port_role_servers             = {}
      tags                          = []
    }
  }
  description = <<-EOT
  key - Name for the Port Policy.
  * description - Description to Assign to the Policy.
  * device_model - This field specifies the device model template for the Port Policy.
    - UCS-FI-6454 - The standard 4th generation UCS Fabric Interconnect with 54 ports.
    - UCS-FI-64108 - The expanded 4th generation UCS Fabric Interconnect with 108 ports.
    - unknown - Unknown device type, usage is TBD.
  * organization - Name of the Intersight Organization to assign this Policy to.
    - https://intersight.com/an/settings/organizations/
  * port_channel_appliances - Use this Map to Configure Ports for Appliance Port-Channels.
    key - Port-Channel Identifier.
    - admin_speed - Admin configured speed for the port.
      * Auto - (Default) Admin configurable speed Auto.
      * 1Gbps - Admin configurable speed 1Gbps.
      * 10Gbps - Admin configurable speed 10Gbps.
      * 25Gbps - Admin configurable speed 25Gbps.
      * 40Gbps - Admin configurable speed 40Gbps.
      * 100Gbps - Admin configurable speed 100Gbps.
    - ethernet_network_control_policy - Name of the Ethernet Network Control policy.
    - ethernet_network_group_policy - Name of the Ethernet Network Group policy.
    interfaces - list of interfaces {breakout_port_id/port_id/slot_id} to assign to the Port-Channel Policy.
      - breakout_port_id - Default is 0.  Breakout port Identifier of the Switch Interface.  When a port is not configured as a breakout port, the aggregatePortId is set to 0, and unused.  When a port is configured as a breakout port, the 'aggregatePortId' port number as labeled on the equipment, e.g. the id of the port on the switch.
      - port_id - Port ID to Assign to the LAN Port-Channel Policy.
      - slot_id - Default is 1.  Slot Identifier of the Switch/FEX/Chassis Interface.
    - mode - Port mode to be set on the appliance Port-Channel.
      * access - Access Mode Switch Port Type.
      * trunk (default) - Trunk Mode Switch Port Type.
    - priority - The 'name' of the System QoS Class.
      * Best Effort - (Default).  QoS Priority for Best-effort traffic.
      * Bronze - QoS Priority for Bronze traffic.
      * FC - QoS Priority for FC traffic.
      * Gold - QoS Priority for Gold traffic.
      * Platinum - QoS Priority for Platinum traffic.
      * Silver - QoS Priority for Silver traffic.
  * port_channel_ethernet_uplinks - Use this Map to Configure Ports for Ethernet Port-Channels.
    key - Port-Channel Identifier.
    - admin_speed - Admin configured speed for the port.
      * Auto - (Default) Admin configurable speed Auto.
      * 1Gbps - Admin configurable speed 1Gbps.
      * 10Gbps - Admin configurable speed 10Gbps.
      * 25Gbps - Admin configurable speed 25Gbps.
      * 40Gbps - Admin configurable speed 40Gbps.
      * 100Gbps - Admin configurable speed 100Gbps.
    - ethernet_network_group_policy - Name of the Ethernet Network Group policy.
    - flow_control_policy - Name of the Flow Control policy.
    - interfaces - list of interfaces {breakout_port_id/port_id/slot_id} to assign to the Port-Channel Policy.
      - breakout_port_id - Default is 0.  Breakout port Identifier of the Switch Interface.  When a port is not configured as a breakout port, the aggregatePortId is set to 0, and unused.  When a port is configured as a breakout port, the 'aggregatePortId' port number as labeled on the equipment, e.g. the id of the port on the switch.
      - port_id - Port ID to Assign to the LAN Port-Channel Policy.
      - slot_id - Default is 1.  Slot Identifier of the Switch/FEX/Chassis Interface.
    - link_aggregation_policy - Name of the Link Aggregation policy.
    - link_control_policy - Name of the Link Control policy.
  * port_channel_fc_uplinks - Use this Map to Configure Ports for Fibre-Channel Port-Channels.
    key - Port-Channel Identifier.
    - admin_speed - Admin configured speed for the port.
      * Auto - Admin configurable speed AUTO.
      * 8Gbps - Admin configurable speed 8Gbps.
      * 16Gbps - (default).  Admin configurable speed 16Gbps.
      * 32Gbps - Admin configurable speed 32Gbps.
    - fill_pattern - Fill pattern to differentiate the configs in NPIV.
      * Arbff - Fc Fill Pattern type Arbff.
      * Idle - Fc Fill Pattern type Idle.
    interfaces - list of interfaces {breakout_port_id/port_id/slot_id} to assign to the Port-Channel Policy.
      - breakout_port_id - Default is 0.  Breakout port Identifier of the Switch Interface.  When a port is not configured as a breakout port, the aggregatePortId is set to 0, and unused.  When a port is configured as a breakout port, the 'aggregatePortId' port number as labeled on the equipment, e.g. the id of the port on the switch.
      - port_id - Port ID to Assign to the LAN Port-Channel Policy.
      - slot_id - Default is 1.  Slot Identifier of the Switch/FEX/Chassis Interface.
  * port_channel_fcoe_uplinks - Use this Map to Configure Ports for Appliance Port-Channels.
    key - Port-Channel Identifier.
    - admin_speed - Admin configured speed for the port.
      * Auto - (Default) Admin configurable speed Auto.
      * 1Gbps - Admin configurable speed 1Gbps.
      * 10Gbps - Admin configurable speed 10Gbps.
      * 25Gbps - Admin configurable speed 25Gbps.
      * 40Gbps - Admin configurable speed 40Gbps.
      * 100Gbps - Admin configurable speed 100Gbps.
    interfaces - list of interfaces {breakout_port_id/port_id/slot_id} to assign to the Port-Channel Policy.
      - breakout_port_id - Default is 0.  Breakout port Identifier of the Switch Interface.  When a port is not configured as a breakout port, the aggregatePortId is set to 0, and unused.  When a port is configured as a breakout port, the 'aggregatePortId' port number as labeled on the equipment, e.g. the id of the port on the switch.
      - port_id - Port ID to Assign to the LAN Port-Channel Policy.
      - slot_id - Default is 1.  Slot Identifier of the Switch/FEX/Chassis Interface.
    - link_aggregation_policy - Name of the Link Aggregation policy.
    - link_control_policy - Name of the Link Control policy.
  * port_modes - List of Ports to change the default Mode (Breakout Mode|Unified Mode).
    - custom_mode - Custom Port Mode specified for the port range.
        * FibreChannel - (Default).  Fibre Channel Port Types.
        * BreakoutEthernet10G - Breakout Ethernet 10G Port Type.  This is not yet supported.
        * BreakoutEthernet25G - Breakout Ethernet 25G Port Type.  This is not yet supported.
    - port_list - Default is [1, 4].  List of Ports to reconfigure the Port Mode for.  The list should be the begging port and the ending port.
    - slot_id - Default is 1.  Slot Identifier of the Switch/FEX/Chassis Interface.
  * port_role_appliances - Use this Map to Configure Ports for Appliances.
    key - Unique Identifier.
    - admin_speed - Admin configured speed for the port.
      * Auto - (Default) Admin configurable speed Auto.
      * 1Gbps - Admin configurable speed 1Gbps.
      * 10Gbps - Admin configurable speed 10Gbps.
      * 25Gbps - Admin configurable speed 25Gbps.
      * 40Gbps - Admin configurable speed 40Gbps.
      * 100Gbps - Admin configurable speed 100Gbps.
    - breakout_port_id - Default is 0.  Breakout port Identifier of the Switch Interface.  When a port is not configured as a breakout port, the aggregatePortId is set to 0, and unused.  When a port is configured as a breakout port, the 'aggregatePortId' port number as labeled on the equipment, e.g. the id of the port on the switch.
    - ethernet_network_control_policy - Name of the Ethernet Network Control policy.
    - ethernet_network_group_policy - Name of the Ethernet Network Group policy.
    - fec - Forward error correction configuration for the port.
      * Auto - (Default).  Forward error correction option 'Auto'.
      * Cl91 - Forward error correction option 'cl91'.
      * Cl74 - Forward error correction option 'cl74'.
    - mode - Port mode to be set on the appliance port.
      * access - Access Mode Switch Port Type.
      * trunk (default) - Trunk Mode Switch Port Type.
    - port_list - Default is [49, 50].  List of Ports to Assign to the Appliance Port Policy.
    - priority - The 'name' of the System QoS Class.
      * Best Effort - (Default).  QoS Priority for Best-effort traffic.
      * Bronze - QoS Priority for Bronze traffic.
      * FC - QoS Priority for FC traffic.
      * Gold - QoS Priority for Gold traffic.
      * Platinum - QoS Priority for Platinum traffic.
      * Silver - QoS Priority for Silver traffic.
    - slot_id - Default is 1.  Slot Identifier of the Switch/FEX/Chassis Interface.
  * port_role_ethernet_uplinks - Use this Map to Configure Ports for Ethernet Uplinks.
    key - Unique Identifier.
    - admin_speed - Admin configured speed for the port.
      * Auto - (Default) Admin configurable speed Auto.
      * 1Gbps - Admin configurable speed 1Gbps.
      * 10Gbps - Admin configurable speed 10Gbps.
      * 25Gbps - Admin configurable speed 25Gbps.
      * 40Gbps - Admin configurable speed 40Gbps.
      * 100Gbps - Admin configurable speed 100Gbps.
    - breakout_port_id - Default is 0.  Breakout port Identifier of the Switch Interface.  When a port is not configured as a breakout port, the aggregatePortId is set to 0, and unused.  When a port is configured as a breakout port, the 'aggregatePortId' port number as labeled on the equipment, e.g. the id of the port on the switch.
    - ethernet_network_group_policy - Name of the Ethernet Network Group policy.
    - fec - Forward error correction configuration for the port.
      * Auto - (Default).  Forward error correction option 'Auto'.
      * Cl91 - Forward error correction option 'cl91'.
      * Cl74 - Forward error correction option 'cl74'.
    - flow_control_policy - Name of the Flow Control policy.
    - link_control_policy - Name of the Link Control policy.
    - port_list - Ports to Assign to the Ethernet Uplink Port Policy.
    - slot_id - Default is 1.  Slot Identifier of the Switch/FEX/Chassis Interface.
  * port_role_fc_uplinks - Use this Map to Configure Ports for FC Uplinks.
    key - Unique Identifier.
    - admin_speed - Admin configured speed for the port.
      * Auto - Admin configurable speed AUTO.
      * 8Gbps - Admin configurable speed 8Gbps.
      * 16Gbps - (default).  Admin configurable speed 16Gbps.
      * 32Gbps - Admin configurable speed 32Gbps.
    - breakout_port_id - Default is 0.  Breakout port Identifier of the Switch Interface.  When a port is not configured as a breakout port, the aggregatePortId is set to 0, and unused.  When a port is configured as a breakout port, the 'aggregatePortId' port number as labeled on the equipment, e.g. the id of the port on the switch.
    - fill_pattern - Fill pattern to differentiate the configs in NPIV.
      * Arbff - Fc Fill Pattern type Arbff.
      * Idle - Fc Fill Pattern type Idle.
    - port_list - Ports to Assign to the Fibre Channel Uplink Port Policy.
    - slot_id - Default is 1.  Slot Identifier of the Switch/FEX/Chassis Interface.
  * port_role_fcoe_uplinks - Use this Map to Configure Ports for FCoE Uplinks.
    key - Unique Identifier.
    - admin_speed - Admin configured speed for the port.
      * Auto - (Default) Admin configurable speed Auto.
      * 1Gbps - Admin configurable speed 1Gbps.
      * 10Gbps - Admin configurable speed 10Gbps.
      * 25Gbps - Admin configurable speed 25Gbps.
      * 40Gbps - Admin configurable speed 40Gbps.
      * 100Gbps - Admin configurable speed 100Gbps.
    - breakout_port_id - Default is 0.  Breakout port Identifier of the Switch Interface.  When a port is not configured as a breakout port, the aggregatePortId is set to 0, and unused.  When a port is configured as a breakout port, the 'aggregatePortId' port number as labeled on the equipment, e.g. the id of the port on the switch.
    - fec - Forward error correction configuration for the port.
      * Auto - (Default).  Forward error correction option 'Auto'.
      * Cl91 - Forward error correction option 'cl91'.
      * Cl74 - Forward error correction option 'cl74'.
    - link_control_policy - Name of the Link Control policy.
    - port_list - Ports to Assign to the FCoE Uplink Port Policy.
    - slot_id - Default is 1.  Slot Identifier of the Switch/FEX/Chassis Interface.
  * port_role_servers - Use this Map to Configure Ports for Servers.
    key - Unique Identifier.
    - breakout_port_id - Default is 0.  Breakout port Identifier of the Switch Interface.  When a port is not configured as a breakout port, the aggregatePortId is set to 0, and unused.  When a port is configured as a breakout port, the 'aggregatePortId' port number as labeled on the equipment, e.g. the id of the port on the switch.
        - port_list - Ports to Assign to the Server Port Policy.
    - slot_id - Default is 1.  Slot Identifier of the Switch/FEX/Chassis Interface.
  * tags - List of Key/Value Pairs to Assign as Attributes to the Policy.
  EOT
  type = map(object(
    {
      description  = optional(string)
      device_model = optional(string)
      organization = optional(string)
      port_channel_appliances = optional(map(object(
        {
          admin_speed                     = optional(string)
          ethernet_network_control_policy = string
          ethernet_network_group_policy   = string
          interfaces = optional(list(object(
            {
              breakout_port_id = optional(number)
              port_id          = number
              slot_id          = number
            }
          )))
          mode     = optional(string)
          priority = optional(string)
        }
      )))
      port_channel_ethernet_uplinks = optional(map(object(
        {
          admin_speed                   = optional(string)
          ethernet_network_group_policy = string
          flow_control_policy           = optional(string)
          interfaces = optional(list(object(
            {
              breakout_port_id = optional(number)
              port_id          = number
              slot_id          = number
            }
          )))
          link_aggregation_policy = optional(string)
          link_control_policy     = optional(string)
        }
      )))
      port_channel_fc_uplinks = optional(map(object(
        {
          admin_speed  = optional(string)
          fill_pattern = optional(string)
          interfaces = optional(list(object(
            {
              breakout_port_id = optional(number)
              port_id          = number
              slot_id          = number
            }
          )))
          vsan_id = number
        }
      )))
      port_channel_fcoe_uplinks = optional(map(object(
        {
          admin_speed = optional(string)
          interfaces = optional(list(object(
            {
              breakout_port_id = optional(number)
              port_id          = number
              slot_id          = number
            }
          )))
          link_aggregation_policy = optional(string)
          link_control_policy     = optional(string)
        }
      )))
      port_modes = optional(list(object(
        {
          custom_mode = optional(string)
          port_list   = list(number)
          slot_id     = optional(number)
        }
      )))
      port_role_appliances = optional(map(object(
        {
          admin_speed                     = optional(string)
          breakout_port_id                = optional(number)
          ethernet_network_control_policy = string
          ethernet_network_group_policy   = string
          fec                             = optional(string)
          mode                            = optional(string)
          port_list                       = string
          priority                        = optional(string)
          slot_id                         = optional(number)
        }
      )))
      port_role_ethernet_uplinks = optional(map(object(
        {
          admin_speed                   = optional(string)
          breakout_port_id              = optional(number)
          ethernet_network_group_policy = string
          fec                           = optional(string)
          flow_control_policy           = optional(string)
          link_control_policy           = optional(string)
          port_list                     = string
          slot_id                       = optional(number)
        }
      )))
      port_role_fc_uplinks = optional(map(object(
        {
          admin_speed      = optional(string)
          breakout_port_id = optional(number)
          fill_pattern     = optional(string)
          port_list        = string
          slot_id          = optional(number)
          vsan_id          = number
        }
      )))
      port_role_fcoe_uplinks = optional(map(object(
        {
          admin_speed         = optional(string)
          breakout_port_id    = optional(number)
          fec                 = optional(string)
          link_control_policy = optional(string)
          port_list           = string
          slot_id             = optional(number)
        }
      )))
      port_role_servers = optional(map(object(
        {
          breakout_port_id = optional(number)
          port_list        = string
          slot_id          = optional(number)
        }
      )))
      tags = optional(list(map(string)))
    }
  ))
}


#_________________________________________________________________________
#
# Intersight Port Policies
# GUI Location: Configure > Policies > Create Policy > Port > Start
#_________________________________________________________________________

module "port_policies" {
  depends_on = [
    local.org_moids,
    local.merged_profile_policies
  ]
  source       = "terraform-cisco-modules/imm/intersight//modules/port_policies"
  for_each     = local.port_policies
  description  = each.value.description != "" ? each.value.description : "${each.key} Port Policy."
  device_model = each.value.device_model
  name         = each.key
  org_moid     = local.org_moids[each.value.organization].moid
  tags         = length(each.value.tags) > 0 ? each.value.tags : local.tags
  profiles = {
    for k, v in local.merged_profile_policies : k => {
      moid        = v.moid
      object_type = v.object_type
    }
    if local.merged_profile_policies[k].vsan_policy == each.key
  }
}

#_________________________________________________________________________
#
# Intersight Port Policies - Port Mode
# GUI Location: Configure > Policies > Create Policy > Port > Start
#_________________________________________________________________________

module "port_modes" {
  depends_on = [
    local.org_moids,
    module.port_policies
  ]
  source           = "terraform-cisco-modules/imm/intersight//modules/port_modes"
  for_each         = local.port_modes
  custom_mode      = each.value.custom_mode
  port_list        = each.value.port_list
  port_policy_moid = module.port_policies[each.value.port_policy].moid
  slot_id          = each.value.slot_id
  tags             = length(each.value.tags) > 0 ? each.value.tags : local.tags
}

#_________________________________________________________________________
#
# Intersight Port Policies - Port Channels - Appliance
# GUI Location: Configure > Policies > Create Policy > Port > Start
#_________________________________________________________________________

module "port_channel_appliances" {
  depends_on = [
    local.org_moids,
    module.ethernet_network_control_policies,
    module.ethernet_network_group_policies,
    module.port_policies
  ]
  source           = "terraform-cisco-modules/imm/intersight//modules/port_channel_appliances"
  for_each         = local.port_channel_appliances
  admin_speed      = each.value.admin_speed
  interfaces       = each.value.interfaces
  pc_id            = each.value.pc_id
  mode             = each.value.mode
  port_policy_moid = module.port_policies[each.value.port_policy].moid
  priority         = each.value.priority
  tags             = length(each.value.tags) > 0 ? each.value.tags : local.tags
  ethernet_network_control_policy_moid = each.value.ethernet_network_control_policy != "" ? [
    module.ethernet_network_control_policies[each.value.ethernet_network_control_policy].moid
  ] : []
  ethernet_network_group_policy_moid = each.value.ethernet_network_group_policy != "" ? [
    module.ethernet_network_group_policies[each.value.ethernet_network_group_policy].moid
  ] : []
}


#_________________________________________________________________________
#
# Intersight Port Policies - Port Channels - Ethernet Uplink
# GUI Location: Configure > Policies > Create Policy > Port > Start
#_________________________________________________________________________

module "port_channel_ethernet_uplinks" {
  depends_on = [
    local.org_moids,
    module.flow_control_policies,
    module.link_aggregation_policies,
    module.link_control_policies,
    module.port_policies
  ]
  source           = "terraform-cisco-modules/imm/intersight//modules/port_channel_ethernet_uplinks"
  for_each         = local.port_channel_ethernet_uplinks
  admin_speed      = each.value.admin_speed
  interfaces       = each.value.interfaces
  pc_id            = each.value.pc_id
  port_policy_moid = module.port_policies[each.value.port_policy].moid
  tags             = length(each.value.tags) > 0 ? each.value.tags : local.tags
  ethernet_network_group_policy_moid = each.value.ethernet_network_group_policy != "" ? [
    module.ethernet_network_group_policies[each.value.ethernet_network_group_policy].moid
  ] : []
  flow_control_policy_moid = each.value.flow_control_policy != "" ? [
    module.flow_control_policies[each.value.flow_control_policy].moid
  ] : []
  link_aggregation_policy_moid = each.value.link_aggregation_policy != "" ? [
    module.link_aggregation_policies[each.value.link_aggregation_policy].moid
  ] : []
  link_control_policy_moid = each.value.link_control_policy != "" ? [
    module.link_control_policies[each.value.link_control_policy].moid
  ] : []
}


#_________________________________________________________________________
#
# Intersight Port Policies - Port Channels - Fibre Channel Uplink
# GUI Location: Configure > Policies > Create Policy > Port > Start
#_________________________________________________________________________

module "port_channel_fc_uplinks" {
  depends_on = [
    local.org_moids,
    module.port_modes,
    module.port_policies
  ]
  source           = "terraform-cisco-modules/imm/intersight//modules/port_channel_fc_uplinks"
  for_each         = local.port_channel_fc_uplinks
  admin_speed      = each.value.admin_speed
  fill_pattern     = each.value.fill_pattern
  interfaces       = each.value.interfaces
  pc_id            = each.value.pc_id
  port_policy_moid = module.port_policies[each.value.port_policy].moid
  tags             = length(each.value.tags) > 0 ? each.value.tags : local.tags
  vsan_id          = each.value.vsan_id
}


#_________________________________________________________________________
#
# Intersight Port Policies - Port Channels - FCoE Uplink
# GUI Location: Configure > Policies > Create Policy > Port > Start
#_________________________________________________________________________

module "port_channel_fcoe_uplinks" {
  depends_on = [
    local.org_moids,
    module.link_aggregation_policies,
    module.link_control_policies,
    module.port_policies
  ]
  source           = "terraform-cisco-modules/imm/intersight//modules/port_channel_fcoe_uplinks"
  for_each         = local.port_channel_fcoe_uplinks
  admin_speed      = each.value.admin_speed
  interfaces       = each.value.interfaces
  pc_id            = each.value.pc_id
  port_policy_moid = module.port_policies[each.value.port_policy].moid
  tags             = length(each.value.tags) > 0 ? each.value.tags : local.tags
  link_aggregation_policy_moid = each.value.link_aggregation_policy != "" ? [
    module.link_aggregation_policies[each.value.link_aggregation_policy].moid
  ] : []
  link_control_policy_moid = each.value.link_control_policy != "" ? [
    module.link_control_policies[each.value.link_control_policy].moid
  ] : []
}


#_________________________________________________________________________
#
# Intersight Port Policies - Port Roles - Appliance
# GUI Location: Configure > Policies > Create Policy > Port > Start
#_________________________________________________________________________

module "port_role_appliances" {
  depends_on = [
    local.org_moids,
    module.ethernet_network_control_policies,
    module.ethernet_network_group_policies,
    module.port_policies
  ]
  source           = "terraform-cisco-modules/imm/intersight//modules/port_role_appliances"
  for_each         = local.port_role_appliances
  admin_speed      = each.value.admin_speed
  breakout_port_id = each.value.breakout_port_id
  fec              = each.value.fec
  mode             = each.value.mode
  port_list        = each.value.port_list
  port_policy_moid = module.port_policies[each.value.port_policy].moid
  priority         = each.value.priority
  slot_id          = each.value.slot_id
  tags             = length(each.value.tags) > 0 ? each.value.tags : local.tags
  ethernet_network_control_policy_moid = each.value.ethernet_network_control_policy != "" ? [
    module.ethernet_network_control_policies[each.value.ethernet_network_control_policy].moid
  ] : []
  ethernet_network_group_policy_moid = each.value.ethernet_network_group_policy != "" ? [
    module.ethernet_network_group_policies[each.value.ethernet_network_group_policy].moid
  ] : []
}


#_________________________________________________________________________
#
# Intersight Port Policies - Port Roles - Ethernet Uplink
# GUI Location: Configure > Policies > Create Policy > Port > Start
#_________________________________________________________________________

module "port_role_ethernet_uplinks" {
  depends_on = [
    local.org_moids,
    module.flow_control_policies,
    module.link_control_policies,
    module.port_policies
  ]
  source           = "terraform-cisco-modules/imm/intersight//modules/port_role_ethernet_uplinks"
  for_each         = local.port_role_ethernet_uplinks
  admin_speed      = each.value.admin_speed
  breakout_port_id = each.value.breakout_port_id
  fec              = each.value.fec
  port_list        = each.value.port_list
  port_policy_moid = module.port_policies[each.value.port_policy].moid
  slot_id          = each.value.slot_id
  tags             = length(each.value.tags) > 0 ? each.value.tags : local.tags
  ethernet_network_group_policy_moid = each.value.ethernet_network_group_policy != "" ? [
    module.ethernet_network_group_policies[each.value.ethernet_network_group_policy].moid
  ] : []
  flow_control_policy_moid = each.value.flow_control_policy != "" ? [
    module.flow_control_policies[each.value.flow_control_policy].moid
  ] : []
  link_control_policy_moid = each.value.link_control_policy != "" ? [
    module.link_control_policies[each.value.link_control_policy].moid
  ] : []
}


#_________________________________________________________________________
#
# Intersight Port Policies - Port Roles - FC Uplink
# GUI Location: Configure > Policies > Create Policy > Port > Start
#_________________________________________________________________________

module "port_role_fc_uplinks" {
  depends_on = [
    local.org_moids,
    module.port_policies
  ]
  source           = "terraform-cisco-modules/imm/intersight//modules/port_role_fc_uplinks"
  for_each         = local.port_role_fc_uplinks
  admin_speed      = each.value.admin_speed
  breakout_port_id = each.value.breakout_port_id
  fill_pattern     = each.value.fill_pattern
  port_list        = each.value.port_list
  port_policy_moid = module.port_policies[each.value.port_policy].moid
  slot_id          = each.value.slot_id
  tags             = length(each.value.tags) > 0 ? each.value.tags : local.tags
  vsan_id          = each.value.vsan_id
}


#_________________________________________________________________________
#
# Intersight Port Policies - Port Roles - FCoE Uplink
# GUI Location: Configure > Policies > Create Policy > Port > Start
#_________________________________________________________________________

module "port_role_fcoe_uplinks" {
  depends_on = [
    local.org_moids,
    module.link_control_policies,
    module.port_policies
  ]
  source           = "terraform-cisco-modules/imm/intersight//modules/port_role_fcoe_uplinks"
  for_each         = local.port_role_fcoe_uplinks
  admin_speed      = each.value.admin_speed
  breakout_port_id = each.value.breakout_port_id
  fec              = each.value.fec
  port_list        = each.value.port_list
  port_policy_moid = module.port_policies[each.value.port_policy].moid
  slot_id          = each.value.slot_id
  tags             = length(each.value.tags) > 0 ? each.value.tags : local.tags
  link_control_policy_moid = each.value.link_control_policy != "" ? [
    module.link_control_policies[each.value.link_control_policy].moid
  ] : []
}


#_________________________________________________________________________
#
# Intersight Port Policies - Port Roles - Server
# GUI Location: Configure > Policies > Create Policy > Port > Start
#_________________________________________________________________________

module "port_role_servers" {
  depends_on = [
    local.org_moids,
    module.port_policies
  ]
  source           = "terraform-cisco-modules/imm/intersight//modules/port_role_servers"
  for_each         = local.port_role_servers
  breakout_port_id = each.value.breakout_port_id
  port_list        = each.value.port_list
  port_policy_moid = module.port_policies[each.value.port_policy].moid
  slot_id          = each.value.slot_id
  tags             = length(each.value.tags) > 0 ? each.value.tags : local.tags
}
