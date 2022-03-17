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
      port_channel_appliances       = {}
      port_channel_ethernet_uplinks = {}
      port_channel_fc_uplinks       = {}
      port_channel_fcoe_uplinks     = {}
      port_modes                    = []
      port_role_appliances          = {}
      port_role_ethernet_uplinks    = {}
      port_role_fc_storage          = {}
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
  * port_role_fc_storage - Use this Map to Configure Ports for FC Storage.
    key - Unique Identifier.
    - admin_speed - Admin configured speed for the port.
      * Auto - Admin configurable speed AUTO.
      * 8Gbps - Admin configurable speed 8Gbps.
      * 16Gbps - (default).  Admin configurable speed 16Gbps.
      * 32Gbps - Admin configurable speed 32Gbps.
    - breakout_port_id - Default is 0.  Breakout port Identifier of the Switch Interface.  When a port is not configured as a breakout port, the aggregatePortId is set to 0, and unused.  When a port is configured as a breakout port, the 'aggregatePortId' port number as labeled on the equipment, e.g. the id of the port on the switch.
    - port_list - Ports to Assign to the Fibre Channel Uplink Port Policy.
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
          ethernet_network_group_policy = optional(string)
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
          ethernet_network_group_policy = optional(string)
          fec                           = optional(string)
          flow_control_policy           = optional(string)
          link_control_policy           = optional(string)
          port_list                     = string
          slot_id                       = optional(number)
        }
      )))
      port_role_fc_storage = optional(map(object(
        {
          admin_speed      = optional(string)
          breakout_port_id = optional(number)
          port_list        = string
          slot_id          = optional(number)
          vsan_id          = number
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

resource "intersight_fabric_port_policy" "port_policies" {
  depends_on = [
    local.org_moid,
    local.ucs_domain_policies
  ]
  for_each     = local.port_policies
  description  = each.value.description != "" ? each.value.description : "${each.key} Port Policy"
  device_model = each.value.device_model
  name         = each.key
  organization {
    moid        = local.org_moid
    object_type = "organization.Organization"
  }
  dynamic "profiles" {
    for_each = { for k, v in local.ucs_domain_policies : k => v if local.ucs_domain_policies[k].port_policy == each.key }
    content {
      moid        = profiles.value.moid
      object_type = profiles.value.object_type
    }
  }
  dynamic "tags" {
    for_each = length(each.value.tags) > 0 ? each.value.tags : local.tags
    content {
      key   = tags.value.key
      value = tags.value.value
    }
  }
}


#_________________________________________________________________________
#
# Intersight Port Policies - Port Mode
# GUI Location: Configure > Policies > Create Policy > Port > Start
#_________________________________________________________________________

resource "intersight_fabric_port_mode" "port_modes" {
  depends_on = [
    local.org_moid,
    intersight_fabric_port_policy.port_policies
  ]
  for_each      = local.port_modes
  custom_mode   = each.value.custom_mode
  port_id_end   = element(each.value.port_list, 1)
  port_id_start = element(each.value.port_list, 0)
  slot_id       = each.value.slot_id
  port_policy {
    moid = intersight_fabric_port_policy.port_policies[each.value.port_policy].moid
  }
  dynamic "tags" {
    for_each = length(each.value.tags) > 0 ? each.value.tags : local.tags
    content {
      key   = tags.value.key
      value = tags.value.value
    }
  }
}


#_________________________________________________________________________
#
# Intersight Port Policies - Port Channels - Appliance
# GUI Location: Configure > Policies > Create Policy > Port > Start
#_________________________________________________________________________

resource "intersight_fabric_appliance_pc_role" "port_channel_appliances" {
  depends_on = [
    local.org_moid,
    intersight_fabric_eth_network_control_policy.ethernet_network_control_policies,
    intersight_fabric_eth_network_group_policy.ethernet_network_group_policies,
    intersight_fabric_port_policy.port_policies
  ]
  for_each    = local.port_channel_appliances
  admin_speed = each.value.admin_speed
  mode        = each.value.mode
  pc_id       = each.value.pc_id
  priority    = each.value.priority
  port_policy {
    moid = intersight_fabric_port_policy.port_policies[each.value.port_policy].moid
  }
  dynamic "eth_network_control_policy" {
    for_each = each.value.ethernet_network_control_policy != "" ? [
      intersight_fabric_eth_network_control_policy.ethernet_network_control_policies[
        each.value.ethernet_network_control_policy
      ].moid
    ] : []
    content {
      moid = eth_network_control_policy.value
    }
  }
  dynamic "eth_network_group_policy" {
    for_each = each.value.ethernet_network_group_policy != "" ? [
      intersight_fabric_eth_network_group_policy.ethernet_network_group_policies[
        each.value.ethernet_network_group_policy
      ].moid
    ] : []
    content {
      moid = eth_network_group_policy.value
    }
  }
  dynamic "ports" {
    for_each = each.value.interfaces
    content {
      aggregate_port_id = ports.value.breakout_port_id
      port_id           = ports.value.port_id
      slot_id           = ports.value.slot_id
    }
  }
  dynamic "tags" {
    for_each = length(each.value.tags) > 0 ? each.value.tags : local.tags
    content {
      key   = tags.value.key
      value = tags.value.value
    }
  }
}


#_________________________________________________________________________
#
# Intersight Port Policies - Port Channels - Ethernet Uplink
# GUI Location: Configure > Policies > Create Policy > Port > Start
#_________________________________________________________________________

resource "intersight_fabric_uplink_pc_role" "port_channel_ethernet_uplinks" {
  depends_on = [
    local.org_moid,
    intersight_fabric_eth_network_group_policy.ethernet_network_group_policies,
    intersight_fabric_flow_control_policy.flow_control_policies,
    intersight_fabric_link_aggregation_policy.link_aggregation_policies,
    intersight_fabric_link_control_policy.link_control_policies,
    intersight_fabric_port_policy.port_policies
  ]
  for_each    = local.port_channel_ethernet_uplinks
  admin_speed = each.value.admin_speed
  pc_id       = each.value.pc_id
  port_policy {
    moid = intersight_fabric_port_policy.port_policies[each.value.port_policy].moid
  }
  dynamic "eth_network_group_policy" {
    for_each = each.value.ethernet_network_group_policy != "" ? [
      intersight_fabric_eth_network_group_policy.ethernet_network_group_policies[
        each.value.ethernet_network_group_policy
      ].moid
    ] : []
    content {
      moid = eth_network_group_policy.value
    }
  }
  dynamic "flow_control_policy" {
    for_each = each.value.flow_control_policy != "" ? [
      intersight_fabric_flow_control_policy.flow_control_policies[
        each.value.flow_control_policy
      ].moid
    ] : []
    content {
      moid = flow_control_policy.value
    }
  }
  dynamic "link_aggregation_policy" {
    for_each = each.value.link_aggregation_policy != "" ? [
      intersight_fabric_link_aggregation_policy.link_aggregation_policies[
        each.value.link_aggregation_policy
      ].moid
    ] : []
    content {
      moid = link_aggregation_policy.value
    }
  }
  dynamic "link_control_policy" {
    for_each = each.value.link_control_policy != "" ? [
      intersight_fabric_link_control_policy.link_control_policies[
        each.value.link_control_policy
      ].moid
    ] : []
    content {
      moid = link_control_policy.value
    }
  }
  dynamic "ports" {
    for_each = each.value.interfaces
    content {
      aggregate_port_id = ports.value.breakout_port_id
      port_id           = ports.value.port_id
      slot_id           = ports.value.slot_id
    }
  }
  dynamic "tags" {
    for_each = length(each.value.tags) > 0 ? each.value.tags : local.tags
    content {
      key   = tags.value.key
      value = tags.value.value
    }
  }
}


#_________________________________________________________________________
#
# Intersight Port Policies - Port Channels - Fibre Channel Uplink
# GUI Location: Configure > Policies > Create Policy > Port > Start
#_________________________________________________________________________

resource "intersight_fabric_fc_uplink_pc_role" "port_channel_fc_uplinks" {
  depends_on = [
    local.org_moid,
    intersight_fabric_port_mode.port_modes,
    intersight_fabric_port_policy.port_policies
  ]
  for_each    = local.port_channel_fc_uplinks
  admin_speed = each.value.admin_speed
  pc_id       = each.value.pc_id
  vsan_id     = each.value.vsan_id
  port_policy {
    moid = intersight_fabric_port_policy.port_policies[each.value.port_policy].moid
  }
  dynamic "ports" {
    for_each = each.value.interfaces
    content {
      aggregate_port_id = ports.value.breakout_port_id
      port_id           = ports.value.port_id
      slot_id           = ports.value.slot_id
    }
  }
  dynamic "tags" {
    for_each = length(each.value.tags) > 0 ? each.value.tags : local.tags
    content {
      key   = tags.value.key
      value = tags.value.value
    }
  }
}


#_________________________________________________________________________
#
# Intersight Port Policies - Port Channels - FCoE Uplink
# GUI Location: Configure > Policies > Create Policy > Port > Start
#_________________________________________________________________________

resource "intersight_fabric_fcoe_uplink_pc_role" "port_channel_fcoe_uplinks" {
  depends_on = [
    local.org_moid,
    intersight_fabric_link_aggregation_policy.link_aggregation_policies,
    intersight_fabric_link_control_policy.link_control_policies,
    intersight_fabric_port_policy.port_policies
  ]
  for_each    = local.port_channel_fcoe_uplinks
  admin_speed = each.value.admin_speed
  pc_id       = each.value.pc_id
  port_policy {
    moid = intersight_fabric_port_policy.port_policies[each.value.port_policy].moid
  }
  dynamic "link_aggregation_policy" {
    for_each = each.value.link_aggregation_policy != "" ? [
      intersight_fabric_link_aggregation_policy.link_aggregation_policies[
        each.value.link_aggregation_policy
      ].moid
    ] : []
    content {
      moid = link_aggregation_policy.value
    }
  }
  dynamic "link_control_policy" {
    for_each = each.value.link_control_policy != "" ? [
      intersight_fabric_link_control_policy.link_control_policies[
        each.value.link_control_policy
      ].moid
    ] : []
    content {
      moid = link_control_policy.value
    }
  }
  dynamic "ports" {
    for_each = each.value.interfaces
    content {
      aggregate_port_id = ports.value.breakout_port_id
      port_id           = ports.value.port_id
      slot_id           = ports.value.slot_id
    }
  }
  dynamic "tags" {
    for_each = length(each.value.tags) > 0 ? each.value.tags : local.tags
    content {
      key   = tags.value.key
      value = tags.value.value
    }
  }
}


#_________________________________________________________________________
#
# Intersight Port Policies - Port Roles - Appliance
# GUI Location: Configure > Policies > Create Policy > Port > Start
#_________________________________________________________________________

resource "intersight_fabric_appliance_role" "port_role_appliances" {
  depends_on = [
    local.org_moid,
    intersight_fabric_eth_network_control_policy.ethernet_network_control_policies,
    intersight_fabric_eth_network_group_policy.ethernet_network_group_policies,
    intersight_fabric_port_policy.port_policies
  ]
  for_each          = local.port_role_appliances
  admin_speed       = each.value.admin_speed
  aggregate_port_id = each.value.breakout_port_id
  fec               = each.value.fec
  mode              = each.value.mode
  port_id           = each.value.port_id
  priority          = each.value.priority
  slot_id           = each.value.slot_id
  port_policy {
    moid = intersight_fabric_port_policy.port_policies[each.value.port_policy].moid
  }
  dynamic "eth_network_control_policy" {
    for_each = each.value.ethernet_network_control_policy != "" ? [
      intersight_fabric_eth_network_control_policy.ethernet_network_control_policies[
        each.value.ethernet_network_control_policy
      ].moid
    ] : []
    content {
      moid = eth_network_control_policy.value
    }
  }
  dynamic "eth_network_group_policy" {
    for_each = each.value.ethernet_network_group_policy != "" ? [
      intersight_fabric_eth_network_group_policy.ethernet_network_group_policies[
        each.value.ethernet_network_group_policy
      ].moid
    ] : []
    content {
      moid = eth_network_group_policy.value
    }
  }
  dynamic "tags" {
    for_each = length(each.value.tags) > 0 ? each.value.tags : local.tags
    content {
      key   = tags.value.key
      value = tags.value.value
    }
  }
}


#_________________________________________________________________________
#
# Intersight Port Policies - Port Roles - Ethernet Uplink
# GUI Location: Configure > Policies > Create Policy > Port > Start
#_________________________________________________________________________

resource "intersight_fabric_uplink_role" "port_role_ethernet_uplinks" {
  depends_on = [
    local.org_moid,
    intersight_fabric_eth_network_group_policy.ethernet_network_group_policies,
    intersight_fabric_flow_control_policy.flow_control_policies,
    intersight_fabric_link_control_policy.link_control_policies,
    intersight_fabric_port_policy.port_policies
  ]
  for_each          = local.port_role_ethernet_uplinks
  admin_speed       = each.value.admin_speed
  aggregate_port_id = each.value.breakout_port_id
  fec               = each.value.fec
  port_id           = each.value.port_id
  slot_id           = each.value.slot_id
  port_policy {
    moid = intersight_fabric_port_policy.port_policies[each.value.port_policy].moid
  }
  dynamic "eth_network_group_policy" {
    for_each = each.value.ethernet_network_group_policy != "" ? [
      intersight_fabric_eth_network_group_policy.ethernet_network_group_policies[
        each.value.ethernet_network_group_policy
      ].moid
    ] : []
    content {
      moid = eth_network_group_policy.value
    }
  }
  dynamic "flow_control_policy" {
    for_each = each.value.flow_control_policy != "" ? [
      intersight_fabric_flow_control_policy.flow_control_policies[
        each.value.flow_control_policy
      ].moid
    ] : []
    content {
      moid = flow_control_policy.value
    }
  }
  dynamic "link_control_policy" {
    for_each = each.value.link_control_policy != "" ? [
      intersight_fabric_link_control_policy.link_control_policies[
        each.value.link_control_policy
      ].moid
    ] : []
    content {
      moid = link_control_policy.value
    }
  }
  dynamic "tags" {
    for_each = length(each.value.tags) > 0 ? each.value.tags : local.tags
    content {
      key   = tags.value.key
      value = tags.value.value
    }
  }
}


#_________________________________________________________________________
#
# Intersight Port Policies - Port Roles - FC Storage
# GUI Location: Configure > Policies > Create Policy > Port > Start
#_________________________________________________________________________

resource "intersight_fabric_fc_storage_role" "port_role_fc_storage" {
  depends_on = [
    local.org_moid,
    intersight_fabric_port_mode.port_modes,
    intersight_fabric_port_policy.port_policies
  ]
  for_each          = local.port_role_fc_storage
  admin_speed       = each.value.admin_speed
  aggregate_port_id = each.value.breakout_port_id
  port_id           = each.value.port_id
  slot_id           = each.value.slot_id
  vsan_id           = each.value.vsan_id
  port_policy {
    moid = intersight_fabric_port_policy.port_policies[each.value.port_policy].moid
  }
  dynamic "tags" {
    for_each = length(each.value.tags) > 0 ? each.value.tags : local.tags
    content {
      key   = tags.value.key
      value = tags.value.value
    }
  }
}


#_________________________________________________________________________
#
# Intersight Port Policies - Port Roles - FC Uplink
# GUI Location: Configure > Policies > Create Policy > Port > Start
#_________________________________________________________________________

resource "intersight_fabric_fc_uplink_role" "port_role_fc_uplinks" {
  depends_on = [
    local.org_moid,
    intersight_fabric_port_mode.port_modes,
    intersight_fabric_port_policy.port_policies
  ]
  for_each          = local.port_role_fc_uplinks
  admin_speed       = each.value.admin_speed
  aggregate_port_id = each.value.breakout_port_id
  fill_pattern      = each.value.fill_pattern
  port_id           = each.value.port_id
  slot_id           = each.value.slot_id
  vsan_id           = each.value.vsan_id
  port_policy {
    moid = intersight_fabric_port_policy.port_policies[each.value.port_policy].moid
  }
  dynamic "tags" {
    for_each = length(each.value.tags) > 0 ? each.value.tags : local.tags
    content {
      key   = tags.value.key
      value = tags.value.value
    }
  }
}


#_________________________________________________________________________
#
# Intersight Port Policies - Port Roles - FCoE Uplink
# GUI Location: Configure > Policies > Create Policy > Port > Start
#_________________________________________________________________________

resource "intersight_fabric_fcoe_uplink_role" "port_role_fcoe_uplinks" {
  depends_on = [
    local.org_moid,
    intersight_fabric_link_control_policy.link_control_policies,
    intersight_fabric_port_policy.port_policies
  ]
  for_each          = local.port_role_fcoe_uplinks
  admin_speed       = each.value.admin_speed
  aggregate_port_id = each.value.breakout_port_id
  fec               = each.value.fec
  port_id           = each.value.port_id
  slot_id           = each.value.slot_id
  port_policy {
    moid = intersight_fabric_port_policy.port_policies[each.value.port_policy].moid
  }
  dynamic "link_control_policy" {
    for_each = each.value.link_control_policy != "" ? [
      intersight_fabric_link_control_policy.link_control_policies[
        each.value.link_control_policy
      ].moid
    ] : []
    content {
      moid = link_control_policy.value
    }
  }
  dynamic "tags" {
    for_each = length(each.value.tags) > 0 ? each.value.tags : local.tags
    content {
      key   = tags.value.key
      value = tags.value.value
    }
  }
}


#_________________________________________________________________________
#
# Intersight Port Policies - Port Roles - Server
# GUI Location: Configure > Policies > Create Policy > Port > Start
#_________________________________________________________________________

resource "intersight_fabric_server_role" "port_role_servers" {
  depends_on = [
    local.org_moid,
    intersight_fabric_port_policy.port_policies
  ]
  for_each          = local.port_role_servers
  aggregate_port_id = each.value.breakout_port_id
  port_id           = each.value.port_id
  slot_id           = each.value.slot_id
  port_policy {
    moid = intersight_fabric_port_policy.port_policies[each.value.port_policy].moid
  }
  dynamic "tags" {
    for_each = length(each.value.tags) > 0 ? each.value.tags : local.tags
    content {
      key   = tags.value.key
      value = tags.value.value
    }
  }
}
