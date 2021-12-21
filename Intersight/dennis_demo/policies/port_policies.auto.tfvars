#______________________________________________
#
# Port Policy Variables
#______________________________________________

port_policies = {
  "dennis-ucs-a" = {
    description  = "dennis-ucs Port Policy"
    device_model = "UCS-FI-6454"
    organization = "dennis_demo"
    port_channel_appliances = {}
    port_channel_ethernet_uplinks = {
      "49" = {
        admin_speed                     = "Auto"
        ethernet_network_group_policy   = "dennis-ucs-vg"
        flow_control_policy             = "dennis-ucs"
        interfaces = [
          {
            port_id          = 49
            slot_id          = 1
          },
          {
            port_id          = 50
            slot_id          = 1
          },
        ]
        link_aggregation_policy = "dennis-ucs"
        link_control_policy     = "dennis-ucs"
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
            port_id          = 2
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
    port_role_fc_storage = {}
    port_role_fc_uplinks = {}
    port_role_fcoe_uplinks = {}
    port_role_servers = {
      "1" = {
        port_list           = "5-18"
        slot_id             = 1
      }
    }
    tags         = []
  }
  "dennis-ucs-b" = {
    description  = "dennis-ucs Port Policy"
    device_model = "UCS-FI-6454"
    organization = "dennis_demo"
    port_channel_appliances = {}
    port_channel_ethernet_uplinks = {
      "49" = {
        admin_speed                     = "Auto"
        ethernet_network_group_policy   = "dennis-ucs-vg"
        flow_control_policy             = "dennis-ucs"
        interfaces = [
          {
            port_id          = 49
            slot_id          = 1
          },
          {
            port_id          = 50
            slot_id          = 1
          },
        ]
        link_aggregation_policy = "dennis-ucs"
        link_control_policy     = "dennis-ucs"
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
            port_id          = 2
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
    port_role_fc_storage = {}
    port_role_fc_uplinks = {}
    port_role_fcoe_uplinks = {}
    port_role_servers = {
      "1" = {
        port_list           = "5-18"
        slot_id             = 1
      }
    }
    tags         = []
  }
}