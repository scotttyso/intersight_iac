#______________________________________________
#
# Port Policy Variables
#______________________________________________

port_policies = {
  "UCS-DEMO2-A" = {
    description  = ""
    device_model = "UCS-FI-6454"
    organization = "UCS-DEMO2"
    port_channel_appliances = {
      "36" = {
        admin_speed                     = "40Gbps"
        ethernet_network_control_policy = "ncp-appliance_appliance"
        ethernet_network_group_policy   = "UCS-DEMO2-AppliancePortChannel-A-PC36"
        interfaces = [
          {
            port_id          = 36
            slot_id          = 1
          },
        ]
        mode     = "trunk"
        priority = "Gold"
      }
    }
    port_channel_ethernet_uplinks = {
      "1" = {
        admin_speed         = "Auto"
        flow_control_policy = "UCS-DEMO2"
        link_aggregation_policy = "UCS-DEMO2"
      }
      "13" = {
        admin_speed         = "10Gbps"
        flow_control_policy = "UCS-DEMO2"
        link_aggregation_policy = "UCS-DEMO2"
        link_control_policy     = "test"
      }
      "17" = {
        admin_speed         = "40Gbps"
        flow_control_policy = "UCS-DEMO2"
        link_aggregation_policy = "UCS-DEMO2"
        link_control_policy     = "test"
      }
      "24" = {
        admin_speed         = "40Gbps"
        flow_control_policy = "UCS-DEMO2"
        link_aggregation_policy = "UCS-DEMO2"
        link_control_policy     = "test"
      }
      "43" = {
        admin_speed         = "10Gbps"
        flow_control_policy = "UCS-DEMO2"
        link_aggregation_policy = "UCS-DEMO2"
        link_control_policy     = "test"
      }
      "45" = {
        admin_speed         = "10Gbps"
        flow_control_policy = "UCS-DEMO2"
        link_aggregation_policy = "UCS-DEMO2"
        link_control_policy     = "test"
      }
      "47" = {
        admin_speed         = "10Gbps"
        flow_control_policy = "UCS-DEMO2"
        link_aggregation_policy = "UCS-DEMO2"
        link_control_policy     = "test"
      }
      "53" = {
        admin_speed         = "10Gbps"
        flow_control_policy = "UCS-DEMO2"
        link_aggregation_policy = "lacp_pol"
        link_control_policy     = "test"
      }
      "119" = {
        admin_speed         = "40Gbps"
        flow_control_policy = "UCS-DEMO2"
        link_aggregation_policy = "UCS-DEMO2"
        link_control_policy     = "test"
      }
    }
    port_channel_fc_uplinks = {}
    port_channel_fcoe_uplinks = {
      "18" = {
        link_aggregation_policy = "UCS-DEMO2"
      }
      "33" = {
        interfaces = [
          {
            breakout_port_id = 1
            port_id          = 21
            slot_id          = 1
          },
          {
            breakout_port_id = 2
            port_id          = 21
            slot_id          = 1
          },
        ]
        link_aggregation_policy = "UCS-DEMO2"
      }
    }
    port_modes = [
      {
        port_list   = [1, 6]
        slot_id     = 1
      }
    ]
    port_role_appliances = {
      "1" = {
        admin_speed                     = "40Gbps"
        ethernet_network_control_policy = "UCS-DEMO2_appliance"
        ethernet_network_group_policy   = "UCS-DEMO2-AppliancePort-A-1-35"
        fec                             = "Auto"
        mode                            = "trunk"
        port_list                       = "35"
        priority                        = "Best Effort"
        slot_id                         = 1
      }
    }
    port_role_ethernet_uplinks = {
      "1" = {
        admin_speed         = "10Gbps"
        fec                 = "Auto"
        flow_control_policy = "UCS-DEMO2"
        link_control_policy = "UCS-DEMO2"
        port_list           = "9"
        slot_id             = 1
      }
      "2" = {
        admin_speed         = "10Gbps"
        fec                 = "Auto"
        flow_control_policy = "UCS-DEMO2"
        link_control_policy = "UCS-DEMO2"
        port_list           = "16"
        slot_id             = 1
      }
      "3" = {
        admin_speed         = "40Gbps"
        fec                 = "Auto"
        flow_control_policy = "UCS-DEMO2"
        link_control_policy = "UCS-DEMO2"
        port_list           = "19"
        slot_id             = 1
      }
      "4" = {
        admin_speed         = "40Gbps"
        fec                 = "Auto"
        flow_control_policy = "flow_ctrl"
        link_control_policy = "test"
        port_list           = "39"
        slot_id             = 1
      }
    }
    port_role_fc_uplinks = {
      "1" = {
        admin_speed      = "Auto"
        fill_pattern     = "Arbff"
        port_list        = "1"
        slot_id          = 1
        vsan_id          = "1"
      }
      "2" = {
        admin_speed      = "Auto"
        fill_pattern     = "Arbff"
        port_list        = "2"
        slot_id          = 1
        vsan_id          = "1"
      }
      "3" = {
        admin_speed      = "Auto"
        fill_pattern     = "Arbff"
        port_list        = "3"
        slot_id          = 1
        vsan_id          = "1"
      }
      "4" = {
        admin_speed      = "Auto"
        fill_pattern     = "Arbff"
        port_list        = "4"
        slot_id          = 1
        vsan_id          = "1"
      }
      "5" = {
        admin_speed      = "Auto"
        fill_pattern     = "Arbff"
        port_list        = "5"
        slot_id          = 1
        vsan_id          = "1"
      }
      "6" = {
        admin_speed      = "Auto"
        fill_pattern     = "Arbff"
        port_list        = "6"
        slot_id          = 1
        vsan_id          = "1"
      }
    }
    port_role_fcoe_uplinks = {
      "1" = {
        admin_speed         = "10Gbps"
        fec                 = "Auto"
        link_control_policy = "test"
        port_list           = "23"
        slot_id             = 1
      }
    }
    port_role_servers = {
      "1" = {
        port_list           = "7,8,10,11,12,13,17,18,20,22,24,25,26,27,28,29,30,31,32,33,34,37"
        slot_id             = 1
      }
    }
    tags = [
      {
        key = "easyucs_origin",
        value = "convert",
      },
      {
        key = "easyucs_version",
        value = "0.9.8",
      },
    ]
  }
  "UCS-DEMO2-B" = {
    description  = ""
    device_model = "UCS-FI-6454"
    organization = "UCS-DEMO2"
    port_channel_appliances = {}
    port_channel_ethernet_uplinks = {
      "1" = {
        admin_speed         = "Auto"
        flow_control_policy = "UCS-DEMO2"
        link_aggregation_policy = "UCS-DEMO2"
      }
      "14" = {
        admin_speed         = "10Gbps"
        flow_control_policy = "UCS-DEMO2"
        link_aggregation_policy = "UCS-DEMO2"
      }
      "18" = {
        admin_speed         = "40Gbps"
        flow_control_policy = "UCS-DEMO2"
        link_aggregation_policy = "UCS-DEMO2"
      }
      "24" = {
        admin_speed         = "40Gbps"
        flow_control_policy = "UCS-DEMO2"
        link_aggregation_policy = "UCS-DEMO2"
      }
      "53" = {
        admin_speed         = "10Gbps"
        flow_control_policy = "UCS-DEMO2"
        link_aggregation_policy = "UCS-DEMO2"
      }
      "120" = {
        admin_speed         = "40Gbps"
        flow_control_policy = "UCS-DEMO2"
        link_aggregation_policy = "UCS-DEMO2"
      }
    }
    port_channel_fc_uplinks = {}
    port_channel_fcoe_uplinks = {}
    port_modes = [
      {
        port_list   = [1, 6]
        slot_id     = 1
      }
    ]
    port_role_appliances = {}
    port_role_ethernet_uplinks = {
      "1" = {
        admin_speed         = "10Gbps"
        fec                 = "Auto"
        flow_control_policy = "UCS-DEMO2"
        link_control_policy = "UCS-DEMO2"
        port_list           = "16"
        slot_id             = 1
      }
    }
    port_role_fc_uplinks = {
      "1" = {
        admin_speed      = "Auto"
        fill_pattern     = "Arbff"
        port_list        = "1"
        slot_id          = 1
        vsan_id          = "1"
      }
      "2" = {
        admin_speed      = "Auto"
        fill_pattern     = "Arbff"
        port_list        = "2"
        slot_id          = 1
        vsan_id          = "1"
      }
      "3" = {
        admin_speed      = "Auto"
        fill_pattern     = "Arbff"
        port_list        = "3"
        slot_id          = 1
        vsan_id          = "1"
      }
      "4" = {
        admin_speed      = "Auto"
        fill_pattern     = "Arbff"
        port_list        = "4"
        slot_id          = 1
        vsan_id          = "1"
      }
      "5" = {
        admin_speed      = "Auto"
        fill_pattern     = "Arbff"
        port_list        = "5"
        slot_id          = 1
        vsan_id          = "1"
      }
      "6" = {
        admin_speed      = "Auto"
        fill_pattern     = "Arbff"
        port_list        = "6"
        slot_id          = 1
        vsan_id          = "1"
      }
    }
    port_role_fcoe_uplinks = {}
    port_role_servers = {
      "1" = {
        port_list           = "7,8,9,10,11,12,13,14,15,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34"
        slot_id             = 1
      }
    }
    tags = [
      {
        key = "easyucs_origin",
        value = "convert",
      },
      {
        key = "easyucs_version",
        value = "0.9.8",
      },
    ]
  }
}