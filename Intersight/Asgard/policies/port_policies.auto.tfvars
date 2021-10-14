#______________________________________________
#
# Port Policy Variables
#______________________________________________

port_policies = {
  "asgard-ucs_A" = {
    description  = "asgard-ucs Port Policy"
    device_model = "UCS-FI-64108"
    organization = "Asgard"
    port_channel_appliances = {}
    port_channel_ethernet_uplinks = {
      "97" = {
        admin_speed         = "Auto"
        flow_control_policy = "asgard-ucs_flow_ctrl"
        interfaces = [
          {
            port_id          = 97
            slot_id          = 1
          },
          {
            port_id          = 101
            slot_id          = 1
          },
        ]
        link_aggregation_policy = "asgard-ucs_link_agg"
        link_control_policy     = "asgard-ucs_link_ctrl"
      }
    }
    port_channel_fc_uplinks = {
      "1" = {
        admin_speed  = "32Gbps"
        fill_pattern = "Arbff"
        interfaces = [
          {
            port_id          = 1
            slot_id          = 1
          },
          {
            port_id          = 3
            slot_id          = 1
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
    port_role_appliances = {}
    port_role_ethernet_uplinks = {}
    port_role_fc_uplinks = {}
    port_role_fcoe_uplinks = {}
    port_role_servers = {
      "1" = {
        port_list           = "5-36"
        slot_id             = 1
      }
    }
    tags         = []
  }
  "asgard-ucs_B" = {
    description  = "asgard-ucs Port Policy"
    device_model = "UCS-FI-64108"
    organization = "Asgard"
    port_channel_appliances = {}
    port_channel_ethernet_uplinks = {
      "97" = {
        admin_speed         = "Auto"
        flow_control_policy = "asgard-ucs_flow_ctrl"
        interfaces = [
          {
            port_id          = 97
            slot_id          = 1
          },
          {
            port_id          = 101
            slot_id          = 1
          },
        ]
        link_aggregation_policy = "asgard-ucs_link_agg"
        link_control_policy     = "asgard-ucs_link_ctrl"
      }
    }
    port_channel_fc_uplinks = {
      "1" = {
        admin_speed  = "32Gbps"
        fill_pattern = "Arbff"
        interfaces = [
          {
            port_id          = 1
            slot_id          = 1
          },
          {
            port_id          = 3
            slot_id          = 1
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
    port_role_appliances = {}
    port_role_ethernet_uplinks = {}
    port_role_fc_uplinks = {}
    port_role_fcoe_uplinks = {}
    port_role_servers = {
      "1" = {
        port_list           = "5-36"
        slot_id             = 1
      }
    }
    tags         = []
  }
}