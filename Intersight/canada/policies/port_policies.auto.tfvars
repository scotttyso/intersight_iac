#______________________________________________
#
# Port Policy Variables
#______________________________________________

port_policies = {
  "asgard-ucs-a" = {
    description             = "asgard-ucs Port Policy"
    device_model            = "UCS-FI-64108"
    organization            = "canada"
    port_channel_appliances = {}
    port_channel_ethernet_uplinks = {
      "97" = {
        admin_speed                   = "Auto"
        ethernet_network_group_policy = "asgard-ucs-vg"
        flow_control_policy           = "asgard-ucs"
        interfaces = [
          {
            port_id = 97
            slot_id = 1
          },
          {
            port_id = 98
            slot_id = 1
          },
        ]
        link_aggregation_policy = "asgard-ucs"
        link_control_policy     = "asgard-ucs"
      }
    }
    port_channel_fc_uplinks = {
      "1" = {
        admin_speed  = "Auto"
        fill_pattern = "Idle"
        interfaces = [
          {
            port_id = 1
            slot_id = 1
          },
          {
            port_id = 2
            slot_id = 1
          },
        ]
        vsan_id = "100"
      }
    }
    port_channel_fcoe_uplinks = {}
    port_modes = [
      {
        custom_mode = "FibreChannel"
        port_list   = [1, 4]
        slot_id     = 1
      }
    ]
    port_role_appliances       = {}
    port_role_ethernet_uplinks = {}
    port_role_fc_uplinks       = {}
    port_role_fcoe_uplinks     = {}
    port_role_servers = {
      "1" = {
        port_list = "5-36"
        slot_id   = 1
      }
    }
    tags = []
  }
  "asgard-ucs-b" = {
    description             = "asgard-ucs Port Policy"
    device_model            = "UCS-FI-64108"
    organization            = "canada"
    port_channel_appliances = {}
    port_channel_ethernet_uplinks = {
      "97" = {
        admin_speed                   = "Auto"
        ethernet_network_group_policy = "asgard-ucs-vg"
        flow_control_policy           = "asgard-ucs"
        interfaces = [
          {
            port_id = 97
            slot_id = 1
          },
          {
            port_id = 98
            slot_id = 1
          },
        ]
        link_aggregation_policy = "asgard-ucs"
        link_control_policy     = "asgard-ucs"
      }
    }
    port_channel_fc_uplinks = {
      "1" = {
        admin_speed  = "Auto"
        fill_pattern = "Idle"
        interfaces = [
          {
            port_id = 1
            slot_id = 1
          },
          {
            port_id = 2
            slot_id = 1
          },
        ]
        vsan_id = "200"
      }
    }
    port_channel_fcoe_uplinks = {}
    port_modes = [
      {
        custom_mode = "FibreChannel"
        port_list   = [1, 4]
        slot_id     = 1
      }
    ]
    port_role_appliances       = {}
    port_role_ethernet_uplinks = {}
    port_role_fc_uplinks       = {}
    port_role_fcoe_uplinks     = {}
    port_role_servers = {
      "1" = {
        port_list = "5-36"
        slot_id   = 1
      }
    }
    tags = []
  }
}