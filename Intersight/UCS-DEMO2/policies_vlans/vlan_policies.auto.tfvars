#______________________________________________
#
# VLAN Policy Variables
#______________________________________________

vlan_policies = {
  "UCS-DEMO2-A" = {
    description  = ""
    organization = "UCS-DEMO2"
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
    vlans = {
      "1" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1",
        multicast_policy      = "UCS-DEMO2",
        name                  = "default",
        native_vlan           = true
      },
      "2" = {
        auto_allow_on_uplinks = true
        vlan_list             = "2",
        multicast_policy      = "UCS-DEMO2",
        name                  = "hx-inband-mgmt",
        native_vlan           = false
      },
      "3" = {
        auto_allow_on_uplinks = true
        vlan_list             = "3",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-3",
        native_vlan           = false
      },
      "4" = {
        auto_allow_on_uplinks = true
        vlan_list             = "4",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-4",
        native_vlan           = false
      },
      "5" = {
        auto_allow_on_uplinks = true
        vlan_list             = "5",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-5",
        native_vlan           = false
      },
      "6" = {
        auto_allow_on_uplinks = true
        vlan_list             = "6",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-6",
        native_vlan           = false
      },
      "7" = {
        auto_allow_on_uplinks = true
        vlan_list             = "7",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-7",
        native_vlan           = false
      },
      "8" = {
        auto_allow_on_uplinks = true
        vlan_list             = "8",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-8",
        native_vlan           = false
      },
      "9" = {
        auto_allow_on_uplinks = true
        vlan_list             = "9",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-9",
        native_vlan           = false
      },
      "10" = {
        auto_allow_on_uplinks = true
        vlan_list             = "10",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-10",
        native_vlan           = false
      },
      "11" = {
        auto_allow_on_uplinks = true
        vlan_list             = "11",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-11",
        native_vlan           = false
      },
      "12" = {
        auto_allow_on_uplinks = true
        vlan_list             = "12",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-12",
        native_vlan           = false
      },
      "13" = {
        auto_allow_on_uplinks = true
        vlan_list             = "13",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-13",
        native_vlan           = false
      },
      "14" = {
        auto_allow_on_uplinks = true
        vlan_list             = "14",
        multicast_policy      = "UCS-DEMO2",
        name                  = "TOTO12345",
        native_vlan           = false
      },
      "15" = {
        auto_allow_on_uplinks = true
        vlan_list             = "14",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-14",
        native_vlan           = false
      },
      "16" = {
        auto_allow_on_uplinks = true
        vlan_list             = "15",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-15",
        native_vlan           = false
      },
      "17" = {
        auto_allow_on_uplinks = true
        vlan_list             = "16",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-16",
        native_vlan           = false
      },
      "18" = {
        auto_allow_on_uplinks = true
        vlan_list             = "17",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-17",
        native_vlan           = false
      },
      "19" = {
        auto_allow_on_uplinks = true
        vlan_list             = "18",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-18",
        native_vlan           = false
      },
      "20" = {
        auto_allow_on_uplinks = true
        vlan_list             = "19",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-19",
        native_vlan           = false
      },
      "21" = {
        auto_allow_on_uplinks = true
        vlan_list             = "20",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-20",
        native_vlan           = false
      },
      "22" = {
        auto_allow_on_uplinks = true
        vlan_list             = "21",
        multicast_policy      = "UCS-DEMO2",
        name                  = "vSAN",
        native_vlan           = false
      },
      "23" = {
        auto_allow_on_uplinks = true
        vlan_list             = "22",
        multicast_policy      = "UCS-DEMO2",
        name                  = "NSX-T_Host_Overlay",
        native_vlan           = false
      },
      "24" = {
        auto_allow_on_uplinks = true
        vlan_list             = "23",
        multicast_policy      = "UCS-DEMO2",
        name                  = "NSX-T_Edge_Uplink1",
        native_vlan           = false
      },
      "25" = {
        auto_allow_on_uplinks = true
        vlan_list             = "24",
        multicast_policy      = "UCS-DEMO2",
        name                  = "NSX-T_Edge_Uplink2",
        native_vlan           = false
      },
      "26" = {
        auto_allow_on_uplinks = true
        vlan_list             = "25",
        multicast_policy      = "UCS-DEMO2",
        name                  = "NSX-T_Edge_Overlay",
        native_vlan           = false
      },
      "27" = {
        auto_allow_on_uplinks = true
        vlan_list             = "26",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-26",
        native_vlan           = false
      },
      "28" = {
        auto_allow_on_uplinks = true
        vlan_list             = "27",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-27",
        native_vlan           = false
      },
      "29" = {
        auto_allow_on_uplinks = true
        vlan_list             = "28",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-28",
        native_vlan           = false
      },
      "30" = {
        auto_allow_on_uplinks = true
        vlan_list             = "29",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-29",
        native_vlan           = false
      },
      "31" = {
        auto_allow_on_uplinks = true
        vlan_list             = "30",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-30",
        native_vlan           = false
      },
      "32" = {
        auto_allow_on_uplinks = true
        vlan_list             = "31",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ISCSI",
        native_vlan           = false
      },
      "33" = {
        auto_allow_on_uplinks = true
        vlan_list             = "32",
        multicast_policy      = "UCS-DEMO2",
        name                  = "NFS",
        native_vlan           = false
      },
      "34" = {
        auto_allow_on_uplinks = true
        vlan_list             = "33",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-33",
        native_vlan           = false
      },
      "35" = {
        auto_allow_on_uplinks = true
        vlan_list             = "34",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-34",
        native_vlan           = false
      },
      "36" = {
        auto_allow_on_uplinks = true
        vlan_list             = "35",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-35",
        native_vlan           = false
      },
      "37" = {
        auto_allow_on_uplinks = true
        vlan_list             = "36",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-36",
        native_vlan           = false
      },
      "38" = {
        auto_allow_on_uplinks = true
        vlan_list             = "37",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-37",
        native_vlan           = false
      },
      "39" = {
        auto_allow_on_uplinks = true
        vlan_list             = "38",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-38",
        native_vlan           = false
      },
      "40" = {
        auto_allow_on_uplinks = true
        vlan_list             = "39",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-39",
        native_vlan           = false
      },
      "41" = {
        auto_allow_on_uplinks = true
        vlan_list             = "40",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-40",
        native_vlan           = false
      },
      "42" = {
        auto_allow_on_uplinks = true
        vlan_list             = "41",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-41",
        native_vlan           = false
      },
      "43" = {
        auto_allow_on_uplinks = true
        vlan_list             = "42",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-42",
        native_vlan           = false
      },
      "44" = {
        auto_allow_on_uplinks = true
        vlan_list             = "43",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-43",
        native_vlan           = false
      },
      "45" = {
        auto_allow_on_uplinks = true
        vlan_list             = "44",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-44",
        native_vlan           = false
      },
      "46" = {
        auto_allow_on_uplinks = true
        vlan_list             = "45",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-45",
        native_vlan           = false
      },
      "47" = {
        auto_allow_on_uplinks = true
        vlan_list             = "46",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-46",
        native_vlan           = false
      },
      "48" = {
        auto_allow_on_uplinks = true
        vlan_list             = "47",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-47",
        native_vlan           = false
      },
      "49" = {
        auto_allow_on_uplinks = true
        vlan_list             = "48",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-48",
        native_vlan           = false
      },
      "50" = {
        auto_allow_on_uplinks = true
        vlan_list             = "49",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-49",
        native_vlan           = false
      },
      "51" = {
        auto_allow_on_uplinks = true
        vlan_list             = "50",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-50",
        native_vlan           = false
      },
      "52" = {
        auto_allow_on_uplinks = true
        vlan_list             = "51",
        multicast_policy      = "UCS-DEMO2",
        name                  = "hx-storage-data",
        native_vlan           = false
      },
      "53" = {
        auto_allow_on_uplinks = true
        vlan_list             = "52",
        multicast_policy      = "UCS-DEMO2",
        name                  = "hx-vmotion",
        native_vlan           = false
      },
      "54" = {
        auto_allow_on_uplinks = true
        vlan_list             = "53",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-53",
        native_vlan           = false
      },
      "55" = {
        auto_allow_on_uplinks = true
        vlan_list             = "54",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-54",
        native_vlan           = false
      },
      "56" = {
        auto_allow_on_uplinks = true
        vlan_list             = "55",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-55",
        native_vlan           = false
      },
      "57" = {
        auto_allow_on_uplinks = true
        vlan_list             = "56",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-56",
        native_vlan           = false
      },
      "58" = {
        auto_allow_on_uplinks = true
        vlan_list             = "57",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-57",
        native_vlan           = false
      },
      "59" = {
        auto_allow_on_uplinks = true
        vlan_list             = "58",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-58",
        native_vlan           = false
      },
      "60" = {
        auto_allow_on_uplinks = true
        vlan_list             = "59",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-59",
        native_vlan           = false
      },
      "61" = {
        auto_allow_on_uplinks = true
        vlan_list             = "60",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-60",
        native_vlan           = false
      },
      "62" = {
        auto_allow_on_uplinks = true
        vlan_list             = "61",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-61",
        native_vlan           = false
      },
      "63" = {
        auto_allow_on_uplinks = true
        vlan_list             = "62",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-62",
        native_vlan           = false
      },
      "64" = {
        auto_allow_on_uplinks = true
        vlan_list             = "63",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-63",
        native_vlan           = false
      },
      "65" = {
        auto_allow_on_uplinks = true
        vlan_list             = "64",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-64",
        native_vlan           = false
      },
      "66" = {
        auto_allow_on_uplinks = true
        vlan_list             = "65",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-65",
        native_vlan           = false
      },
      "67" = {
        auto_allow_on_uplinks = true
        vlan_list             = "66",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-66",
        native_vlan           = false
      },
      "68" = {
        auto_allow_on_uplinks = true
        vlan_list             = "67",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-67",
        native_vlan           = false
      },
      "69" = {
        auto_allow_on_uplinks = true
        vlan_list             = "68",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-68",
        native_vlan           = false
      },
      "70" = {
        auto_allow_on_uplinks = true
        vlan_list             = "69",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-69",
        native_vlan           = false
      },
      "71" = {
        auto_allow_on_uplinks = true
        vlan_list             = "70",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-70",
        native_vlan           = false
      },
      "72" = {
        auto_allow_on_uplinks = true
        vlan_list             = "71",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-71",
        native_vlan           = false
      },
      "73" = {
        auto_allow_on_uplinks = true
        vlan_list             = "72",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-72",
        native_vlan           = false
      },
      "74" = {
        auto_allow_on_uplinks = true
        vlan_list             = "73",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-73",
        native_vlan           = false
      },
      "75" = {
        auto_allow_on_uplinks = true
        vlan_list             = "74",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-74",
        native_vlan           = false
      },
      "76" = {
        auto_allow_on_uplinks = true
        vlan_list             = "75",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-75",
        native_vlan           = false
      },
      "77" = {
        auto_allow_on_uplinks = true
        vlan_list             = "76",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-76",
        native_vlan           = false
      },
      "78" = {
        auto_allow_on_uplinks = true
        vlan_list             = "77",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-77",
        native_vlan           = false
      },
      "79" = {
        auto_allow_on_uplinks = true
        vlan_list             = "78",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-78",
        native_vlan           = false
      },
      "80" = {
        auto_allow_on_uplinks = true
        vlan_list             = "79",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-79",
        native_vlan           = false
      },
      "81" = {
        auto_allow_on_uplinks = true
        vlan_list             = "80",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-80",
        native_vlan           = false
      },
      "82" = {
        auto_allow_on_uplinks = true
        vlan_list             = "81",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-81",
        native_vlan           = false
      },
      "83" = {
        auto_allow_on_uplinks = true
        vlan_list             = "82",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-82",
        native_vlan           = false
      },
      "84" = {
        auto_allow_on_uplinks = true
        vlan_list             = "83",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-83",
        native_vlan           = false
      },
      "85" = {
        auto_allow_on_uplinks = true
        vlan_list             = "84",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-84",
        native_vlan           = false
      },
      "86" = {
        auto_allow_on_uplinks = true
        vlan_list             = "85",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-85",
        native_vlan           = false
      },
      "87" = {
        auto_allow_on_uplinks = true
        vlan_list             = "86",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-86",
        native_vlan           = false
      },
      "88" = {
        auto_allow_on_uplinks = true
        vlan_list             = "87",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-87",
        native_vlan           = false
      },
      "89" = {
        auto_allow_on_uplinks = true
        vlan_list             = "88",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-88",
        native_vlan           = false
      },
      "90" = {
        auto_allow_on_uplinks = true
        vlan_list             = "89",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-89",
        native_vlan           = false
      },
      "91" = {
        auto_allow_on_uplinks = true
        vlan_list             = "90",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-90",
        native_vlan           = false
      },
      "92" = {
        auto_allow_on_uplinks = true
        vlan_list             = "91",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-91",
        native_vlan           = false
      },
      "93" = {
        auto_allow_on_uplinks = true
        vlan_list             = "92",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-92",
        native_vlan           = false
      },
      "94" = {
        auto_allow_on_uplinks = true
        vlan_list             = "93",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-93",
        native_vlan           = false
      },
      "95" = {
        auto_allow_on_uplinks = true
        vlan_list             = "94",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-94",
        native_vlan           = false
      },
      "96" = {
        auto_allow_on_uplinks = true
        vlan_list             = "95",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-95",
        native_vlan           = false
      },
      "97" = {
        auto_allow_on_uplinks = true
        vlan_list             = "96",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-96",
        native_vlan           = false
      },
      "98" = {
        auto_allow_on_uplinks = true
        vlan_list             = "97",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-97",
        native_vlan           = false
      },
      "99" = {
        auto_allow_on_uplinks = true
        vlan_list             = "98",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-98",
        native_vlan           = false
      },
      "100" = {
        auto_allow_on_uplinks = true
        vlan_list             = "99",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-99",
        native_vlan           = false
      },
      "101" = {
        auto_allow_on_uplinks = true
        vlan_list             = "100",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ADMIN",
        native_vlan           = false
      },
      "102" = {
        auto_allow_on_uplinks = true
        vlan_list             = "101",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ESX-101",
        native_vlan           = false
      },
      "103" = {
        auto_allow_on_uplinks = true
        vlan_list             = "102",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ESX-102",
        native_vlan           = false
      },
      "104" = {
        auto_allow_on_uplinks = true
        vlan_list             = "103",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ESX-103",
        native_vlan           = false
      },
      "105" = {
        auto_allow_on_uplinks = true
        vlan_list             = "104",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ESX-104",
        native_vlan           = false
      },
      "106" = {
        auto_allow_on_uplinks = true
        vlan_list             = "105",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ESX-105",
        native_vlan           = false
      },
      "107" = {
        auto_allow_on_uplinks = true
        vlan_list             = "106",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ESX-106",
        native_vlan           = false
      },
      "108" = {
        auto_allow_on_uplinks = true
        vlan_list             = "107",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ESX-107",
        native_vlan           = false
      },
      "109" = {
        auto_allow_on_uplinks = true
        vlan_list             = "108",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ESX-108",
        native_vlan           = false
      },
      "110" = {
        auto_allow_on_uplinks = true
        vlan_list             = "109",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ESX-109",
        native_vlan           = false
      },
      "111" = {
        auto_allow_on_uplinks = true
        vlan_list             = "110",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ESX-110",
        native_vlan           = false
      },
      "112" = {
        auto_allow_on_uplinks = true
        vlan_list             = "123",
        multicast_policy      = "UCS-DEMO2",
        name                  = "Test123",
        native_vlan           = false
      },
      "113" = {
        auto_allow_on_uplinks = true
        vlan_list             = "213",
        multicast_policy      = "UCS-DEMO2",
        name                  = "IB-MGMT",
        native_vlan           = false
      },
      "114" = {
        auto_allow_on_uplinks = true
        vlan_list             = "321",
        multicast_policy      = "UCS-DEMO2",
        name                  = "appl321",
        native_vlan           = false
      },
      "115" = {
        auto_allow_on_uplinks = true
        vlan_list             = "456",
        multicast_policy      = "UCS-DEMO2",
        name                  = "TOTOCAGIP",
        native_vlan           = false
      },
      "116" = {
        auto_allow_on_uplinks = true
        vlan_list             = "756",
        multicast_policy      = "UCS-DEMO2",
        name                  = "CEPH-BE",
        native_vlan           = false
      },
      "117" = {
        auto_allow_on_uplinks = true
        vlan_list             = "757",
        multicast_policy      = "UCS-DEMO2",
        name                  = "CEPH-FE",
        native_vlan           = false
      },
      "118" = {
        auto_allow_on_uplinks = true
        vlan_list             = "837",
        multicast_policy      = "HyperFlex",
        name                  = "primary",
        native_vlan           = false
      },
      "119" = {
        auto_allow_on_uplinks = true
        vlan_list             = "838",
        multicast_policy      = "UCS-DEMO2",
        name                  = "isolated",
        native_vlan           = false
      },
      "120" = {
        auto_allow_on_uplinks = true
        vlan_list             = "897",
        multicast_policy      = "UCS-DEMO2",
        name                  = "AdminCAGIP-OSB3-897",
        native_vlan           = false
      },
      "121" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1101",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1101",
        native_vlan           = false
      },
      "122" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1102",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1102",
        native_vlan           = false
      },
      "123" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1103",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1103",
        native_vlan           = false
      },
      "124" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1104",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1104",
        native_vlan           = false
      },
      "125" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1105",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1105",
        native_vlan           = false
      },
      "126" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1106",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1106",
        native_vlan           = false
      },
      "127" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1107",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1107",
        native_vlan           = false
      },
      "128" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1108",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1108",
        native_vlan           = false
      },
      "129" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1109",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1109",
        native_vlan           = false
      },
      "130" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1110",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1110",
        native_vlan           = false
      },
      "131" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1111",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1111",
        native_vlan           = false
      },
      "132" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1112",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1112",
        native_vlan           = false
      },
      "133" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1113",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1113",
        native_vlan           = false
      },
      "134" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1114",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1114",
        native_vlan           = false
      },
      "135" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1115",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1115",
        native_vlan           = false
      },
      "136" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1116",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1116",
        native_vlan           = false
      },
      "137" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1117",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1117",
        native_vlan           = false
      },
      "138" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1118",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1118",
        native_vlan           = false
      },
      "139" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1119",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1119",
        native_vlan           = false
      },
      "140" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1120",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1120",
        native_vlan           = false
      },
      "141" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1121",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1121",
        native_vlan           = false
      },
      "142" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1122",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1122",
        native_vlan           = false
      },
      "143" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1123",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1123",
        native_vlan           = false
      },
      "144" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1124",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1124",
        native_vlan           = false
      },
      "145" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1125",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1125",
        native_vlan           = false
      },
      "146" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1126",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1126",
        native_vlan           = false
      },
      "147" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1127",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1127",
        native_vlan           = false
      },
      "148" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1128",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1128",
        native_vlan           = false
      },
      "149" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1129",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1129",
        native_vlan           = false
      },
      "150" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1130",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1130",
        native_vlan           = false
      },
      "151" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1131",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1131",
        native_vlan           = false
      },
      "152" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1132",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1132",
        native_vlan           = false
      },
      "153" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1133",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1133",
        native_vlan           = false
      },
      "154" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1134",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1134",
        native_vlan           = false
      },
      "155" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1135",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1135",
        native_vlan           = false
      },
      "156" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1136",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1136",
        native_vlan           = false
      },
      "157" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1137",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1137",
        native_vlan           = false
      },
      "158" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1138",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1138",
        native_vlan           = false
      },
      "159" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1139",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1139",
        native_vlan           = false
      },
      "160" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1140",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1140",
        native_vlan           = false
      },
      "161" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1141",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1141",
        native_vlan           = false
      },
      "162" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1142",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1142",
        native_vlan           = false
      },
      "163" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1143",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1143",
        native_vlan           = false
      },
      "164" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1144",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1144",
        native_vlan           = false
      },
      "165" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1145",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1145",
        native_vlan           = false
      },
      "166" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1146",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1146",
        native_vlan           = false
      },
      "167" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1147",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1147",
        native_vlan           = false
      },
      "168" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1148",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1148",
        native_vlan           = false
      },
      "169" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1149",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1149",
        native_vlan           = false
      },
      "170" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1150",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1150",
        native_vlan           = false
      },
      "171" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1945",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ProdCAGIP-CAGIP-1945",
        native_vlan           = false
      },
      "172" = {
        auto_allow_on_uplinks = true
        vlan_list             = "3110",
        multicast_policy      = "UCS-DEMO2",
        name                  = "iSCSI-A",
        native_vlan           = false
      },
      "173" = {
        auto_allow_on_uplinks = true
        vlan_list             = "3120",
        multicast_policy      = "UCS-DEMO2",
        name                  = "iSCSI-B",
        native_vlan           = false
      },
    }
  }
  "UCS-DEMO2-B" = {
    description  = ""
    organization = "UCS-DEMO2"
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
    vlans = {
      "1" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1",
        multicast_policy      = "UCS-DEMO2",
        name                  = "default",
        native_vlan           = true
      },
      "2" = {
        auto_allow_on_uplinks = true
        vlan_list             = "2",
        multicast_policy      = "UCS-DEMO2",
        name                  = "hx-inband-mgmt",
        native_vlan           = false
      },
      "3" = {
        auto_allow_on_uplinks = true
        vlan_list             = "3",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-3",
        native_vlan           = false
      },
      "4" = {
        auto_allow_on_uplinks = true
        vlan_list             = "4",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-4",
        native_vlan           = false
      },
      "5" = {
        auto_allow_on_uplinks = true
        vlan_list             = "5",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-5",
        native_vlan           = false
      },
      "6" = {
        auto_allow_on_uplinks = true
        vlan_list             = "6",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-6",
        native_vlan           = false
      },
      "7" = {
        auto_allow_on_uplinks = true
        vlan_list             = "7",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-7",
        native_vlan           = false
      },
      "8" = {
        auto_allow_on_uplinks = true
        vlan_list             = "8",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-8",
        native_vlan           = false
      },
      "9" = {
        auto_allow_on_uplinks = true
        vlan_list             = "9",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-9",
        native_vlan           = false
      },
      "10" = {
        auto_allow_on_uplinks = true
        vlan_list             = "10",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-10",
        native_vlan           = false
      },
      "11" = {
        auto_allow_on_uplinks = true
        vlan_list             = "11",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-11",
        native_vlan           = false
      },
      "12" = {
        auto_allow_on_uplinks = true
        vlan_list             = "12",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-12",
        native_vlan           = false
      },
      "13" = {
        auto_allow_on_uplinks = true
        vlan_list             = "13",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-13",
        native_vlan           = false
      },
      "14" = {
        auto_allow_on_uplinks = true
        vlan_list             = "14",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-14",
        native_vlan           = false
      },
      "15" = {
        auto_allow_on_uplinks = true
        vlan_list             = "15",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-15",
        native_vlan           = false
      },
      "16" = {
        auto_allow_on_uplinks = true
        vlan_list             = "16",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-16",
        native_vlan           = false
      },
      "17" = {
        auto_allow_on_uplinks = true
        vlan_list             = "17",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-17",
        native_vlan           = false
      },
      "18" = {
        auto_allow_on_uplinks = true
        vlan_list             = "18",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-18",
        native_vlan           = false
      },
      "19" = {
        auto_allow_on_uplinks = true
        vlan_list             = "19",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-19",
        native_vlan           = false
      },
      "20" = {
        auto_allow_on_uplinks = true
        vlan_list             = "20",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-20",
        native_vlan           = false
      },
      "21" = {
        auto_allow_on_uplinks = true
        vlan_list             = "21",
        multicast_policy      = "UCS-DEMO2",
        name                  = "vSAN",
        native_vlan           = false
      },
      "22" = {
        auto_allow_on_uplinks = true
        vlan_list             = "22",
        multicast_policy      = "UCS-DEMO2",
        name                  = "NSX-T_Host_Overlay",
        native_vlan           = false
      },
      "23" = {
        auto_allow_on_uplinks = true
        vlan_list             = "23",
        multicast_policy      = "UCS-DEMO2",
        name                  = "NSX-T_Edge_Uplink1",
        native_vlan           = false
      },
      "24" = {
        auto_allow_on_uplinks = true
        vlan_list             = "24",
        multicast_policy      = "UCS-DEMO2",
        name                  = "NSX-T_Edge_Uplink2",
        native_vlan           = false
      },
      "25" = {
        auto_allow_on_uplinks = true
        vlan_list             = "25",
        multicast_policy      = "UCS-DEMO2",
        name                  = "NSX-T_Edge_Overlay",
        native_vlan           = false
      },
      "26" = {
        auto_allow_on_uplinks = true
        vlan_list             = "26",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-26",
        native_vlan           = false
      },
      "27" = {
        auto_allow_on_uplinks = true
        vlan_list             = "27",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-27",
        native_vlan           = false
      },
      "28" = {
        auto_allow_on_uplinks = true
        vlan_list             = "28",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-28",
        native_vlan           = false
      },
      "29" = {
        auto_allow_on_uplinks = true
        vlan_list             = "29",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-29",
        native_vlan           = false
      },
      "30" = {
        auto_allow_on_uplinks = true
        vlan_list             = "30",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-30",
        native_vlan           = false
      },
      "31" = {
        auto_allow_on_uplinks = true
        vlan_list             = "31",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ISCSI",
        native_vlan           = false
      },
      "32" = {
        auto_allow_on_uplinks = true
        vlan_list             = "32",
        multicast_policy      = "UCS-DEMO2",
        name                  = "NFS",
        native_vlan           = false
      },
      "33" = {
        auto_allow_on_uplinks = true
        vlan_list             = "33",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-33",
        native_vlan           = false
      },
      "34" = {
        auto_allow_on_uplinks = true
        vlan_list             = "34",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-34",
        native_vlan           = false
      },
      "35" = {
        auto_allow_on_uplinks = true
        vlan_list             = "35",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-35",
        native_vlan           = false
      },
      "36" = {
        auto_allow_on_uplinks = true
        vlan_list             = "36",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-36",
        native_vlan           = false
      },
      "37" = {
        auto_allow_on_uplinks = true
        vlan_list             = "37",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-37",
        native_vlan           = false
      },
      "38" = {
        auto_allow_on_uplinks = true
        vlan_list             = "38",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-38",
        native_vlan           = false
      },
      "39" = {
        auto_allow_on_uplinks = true
        vlan_list             = "39",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-39",
        native_vlan           = false
      },
      "40" = {
        auto_allow_on_uplinks = true
        vlan_list             = "40",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-40",
        native_vlan           = false
      },
      "41" = {
        auto_allow_on_uplinks = true
        vlan_list             = "41",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-41",
        native_vlan           = false
      },
      "42" = {
        auto_allow_on_uplinks = true
        vlan_list             = "42",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-42",
        native_vlan           = false
      },
      "43" = {
        auto_allow_on_uplinks = true
        vlan_list             = "43",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-43",
        native_vlan           = false
      },
      "44" = {
        auto_allow_on_uplinks = true
        vlan_list             = "44",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-44",
        native_vlan           = false
      },
      "45" = {
        auto_allow_on_uplinks = true
        vlan_list             = "45",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-45",
        native_vlan           = false
      },
      "46" = {
        auto_allow_on_uplinks = true
        vlan_list             = "46",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-46",
        native_vlan           = false
      },
      "47" = {
        auto_allow_on_uplinks = true
        vlan_list             = "47",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-47",
        native_vlan           = false
      },
      "48" = {
        auto_allow_on_uplinks = true
        vlan_list             = "48",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-48",
        native_vlan           = false
      },
      "49" = {
        auto_allow_on_uplinks = true
        vlan_list             = "49",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-49",
        native_vlan           = false
      },
      "50" = {
        auto_allow_on_uplinks = true
        vlan_list             = "50",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-50",
        native_vlan           = false
      },
      "51" = {
        auto_allow_on_uplinks = true
        vlan_list             = "51",
        multicast_policy      = "UCS-DEMO2",
        name                  = "hx-storage-data",
        native_vlan           = false
      },
      "52" = {
        auto_allow_on_uplinks = true
        vlan_list             = "52",
        multicast_policy      = "UCS-DEMO2",
        name                  = "hx-vmotion",
        native_vlan           = false
      },
      "53" = {
        auto_allow_on_uplinks = true
        vlan_list             = "53",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-53",
        native_vlan           = false
      },
      "54" = {
        auto_allow_on_uplinks = true
        vlan_list             = "54",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-54",
        native_vlan           = false
      },
      "55" = {
        auto_allow_on_uplinks = true
        vlan_list             = "55",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-55",
        native_vlan           = false
      },
      "56" = {
        auto_allow_on_uplinks = true
        vlan_list             = "56",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-56",
        native_vlan           = false
      },
      "57" = {
        auto_allow_on_uplinks = true
        vlan_list             = "57",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-57",
        native_vlan           = false
      },
      "58" = {
        auto_allow_on_uplinks = true
        vlan_list             = "58",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-58",
        native_vlan           = false
      },
      "59" = {
        auto_allow_on_uplinks = true
        vlan_list             = "59",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-59",
        native_vlan           = false
      },
      "60" = {
        auto_allow_on_uplinks = true
        vlan_list             = "60",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-60",
        native_vlan           = false
      },
      "61" = {
        auto_allow_on_uplinks = true
        vlan_list             = "61",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-61",
        native_vlan           = false
      },
      "62" = {
        auto_allow_on_uplinks = true
        vlan_list             = "62",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-62",
        native_vlan           = false
      },
      "63" = {
        auto_allow_on_uplinks = true
        vlan_list             = "63",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-63",
        native_vlan           = false
      },
      "64" = {
        auto_allow_on_uplinks = true
        vlan_list             = "64",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-64",
        native_vlan           = false
      },
      "65" = {
        auto_allow_on_uplinks = true
        vlan_list             = "65",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-65",
        native_vlan           = false
      },
      "66" = {
        auto_allow_on_uplinks = true
        vlan_list             = "66",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-66",
        native_vlan           = false
      },
      "67" = {
        auto_allow_on_uplinks = true
        vlan_list             = "67",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-67",
        native_vlan           = false
      },
      "68" = {
        auto_allow_on_uplinks = true
        vlan_list             = "68",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-68",
        native_vlan           = false
      },
      "69" = {
        auto_allow_on_uplinks = true
        vlan_list             = "69",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-69",
        native_vlan           = false
      },
      "70" = {
        auto_allow_on_uplinks = true
        vlan_list             = "70",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-70",
        native_vlan           = false
      },
      "71" = {
        auto_allow_on_uplinks = true
        vlan_list             = "71",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-71",
        native_vlan           = false
      },
      "72" = {
        auto_allow_on_uplinks = true
        vlan_list             = "72",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-72",
        native_vlan           = false
      },
      "73" = {
        auto_allow_on_uplinks = true
        vlan_list             = "73",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-73",
        native_vlan           = false
      },
      "74" = {
        auto_allow_on_uplinks = true
        vlan_list             = "74",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-74",
        native_vlan           = false
      },
      "75" = {
        auto_allow_on_uplinks = true
        vlan_list             = "75",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-75",
        native_vlan           = false
      },
      "76" = {
        auto_allow_on_uplinks = true
        vlan_list             = "76",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-76",
        native_vlan           = false
      },
      "77" = {
        auto_allow_on_uplinks = true
        vlan_list             = "77",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-77",
        native_vlan           = false
      },
      "78" = {
        auto_allow_on_uplinks = true
        vlan_list             = "78",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-78",
        native_vlan           = false
      },
      "79" = {
        auto_allow_on_uplinks = true
        vlan_list             = "79",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-79",
        native_vlan           = false
      },
      "80" = {
        auto_allow_on_uplinks = true
        vlan_list             = "80",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-80",
        native_vlan           = false
      },
      "81" = {
        auto_allow_on_uplinks = true
        vlan_list             = "81",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-81",
        native_vlan           = false
      },
      "82" = {
        auto_allow_on_uplinks = true
        vlan_list             = "82",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-82",
        native_vlan           = false
      },
      "83" = {
        auto_allow_on_uplinks = true
        vlan_list             = "83",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-83",
        native_vlan           = false
      },
      "84" = {
        auto_allow_on_uplinks = true
        vlan_list             = "84",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-84",
        native_vlan           = false
      },
      "85" = {
        auto_allow_on_uplinks = true
        vlan_list             = "85",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-85",
        native_vlan           = false
      },
      "86" = {
        auto_allow_on_uplinks = true
        vlan_list             = "86",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-86",
        native_vlan           = false
      },
      "87" = {
        auto_allow_on_uplinks = true
        vlan_list             = "87",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-87",
        native_vlan           = false
      },
      "88" = {
        auto_allow_on_uplinks = true
        vlan_list             = "88",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-88",
        native_vlan           = false
      },
      "89" = {
        auto_allow_on_uplinks = true
        vlan_list             = "89",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-89",
        native_vlan           = false
      },
      "90" = {
        auto_allow_on_uplinks = true
        vlan_list             = "90",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-90",
        native_vlan           = false
      },
      "91" = {
        auto_allow_on_uplinks = true
        vlan_list             = "91",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-91",
        native_vlan           = false
      },
      "92" = {
        auto_allow_on_uplinks = true
        vlan_list             = "92",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-92",
        native_vlan           = false
      },
      "93" = {
        auto_allow_on_uplinks = true
        vlan_list             = "93",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-93",
        native_vlan           = false
      },
      "94" = {
        auto_allow_on_uplinks = true
        vlan_list             = "94",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-94",
        native_vlan           = false
      },
      "95" = {
        auto_allow_on_uplinks = true
        vlan_list             = "95",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-95",
        native_vlan           = false
      },
      "96" = {
        auto_allow_on_uplinks = true
        vlan_list             = "96",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-96",
        native_vlan           = false
      },
      "97" = {
        auto_allow_on_uplinks = true
        vlan_list             = "97",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-97",
        native_vlan           = false
      },
      "98" = {
        auto_allow_on_uplinks = true
        vlan_list             = "98",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-98",
        native_vlan           = false
      },
      "99" = {
        auto_allow_on_uplinks = true
        vlan_list             = "99",
        multicast_policy      = "UCS-DEMO2",
        name                  = "OCB-99",
        native_vlan           = false
      },
      "100" = {
        auto_allow_on_uplinks = true
        vlan_list             = "100",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ADMIN",
        native_vlan           = false
      },
      "101" = {
        auto_allow_on_uplinks = true
        vlan_list             = "101",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ESX-101",
        native_vlan           = false
      },
      "102" = {
        auto_allow_on_uplinks = true
        vlan_list             = "102",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ESX-102",
        native_vlan           = false
      },
      "103" = {
        auto_allow_on_uplinks = true
        vlan_list             = "103",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ESX-103",
        native_vlan           = false
      },
      "104" = {
        auto_allow_on_uplinks = true
        vlan_list             = "104",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ESX-104",
        native_vlan           = false
      },
      "105" = {
        auto_allow_on_uplinks = true
        vlan_list             = "105",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ESX-105",
        native_vlan           = false
      },
      "106" = {
        auto_allow_on_uplinks = true
        vlan_list             = "106",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ESX-106",
        native_vlan           = false
      },
      "107" = {
        auto_allow_on_uplinks = true
        vlan_list             = "107",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ESX-107",
        native_vlan           = false
      },
      "108" = {
        auto_allow_on_uplinks = true
        vlan_list             = "108",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ESX-108",
        native_vlan           = false
      },
      "109" = {
        auto_allow_on_uplinks = true
        vlan_list             = "109",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ESX-109",
        native_vlan           = false
      },
      "110" = {
        auto_allow_on_uplinks = true
        vlan_list             = "110",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ESX-110",
        native_vlan           = false
      },
      "111" = {
        auto_allow_on_uplinks = true
        vlan_list             = "123",
        multicast_policy      = "UCS-DEMO2",
        name                  = "Test123",
        native_vlan           = false
      },
      "112" = {
        auto_allow_on_uplinks = true
        vlan_list             = "213",
        multicast_policy      = "UCS-DEMO2",
        name                  = "IB-MGMT",
        native_vlan           = false
      },
      "113" = {
        auto_allow_on_uplinks = true
        vlan_list             = "321",
        multicast_policy      = "UCS-DEMO2",
        name                  = "appl321",
        native_vlan           = false
      },
      "114" = {
        auto_allow_on_uplinks = true
        vlan_list             = "456",
        multicast_policy      = "UCS-DEMO2",
        name                  = "TOTOCAGIP",
        native_vlan           = false
      },
      "115" = {
        auto_allow_on_uplinks = true
        vlan_list             = "756",
        multicast_policy      = "UCS-DEMO2",
        name                  = "CEPH-BE",
        native_vlan           = false
      },
      "116" = {
        auto_allow_on_uplinks = true
        vlan_list             = "757",
        multicast_policy      = "UCS-DEMO2",
        name                  = "CEPH-FE",
        native_vlan           = false
      },
      "117" = {
        auto_allow_on_uplinks = true
        vlan_list             = "837",
        multicast_policy      = "HyperFlex",
        name                  = "primary",
        native_vlan           = false
      },
      "118" = {
        auto_allow_on_uplinks = true
        vlan_list             = "838",
        multicast_policy      = "UCS-DEMO2",
        name                  = "isolated",
        native_vlan           = false
      },
      "119" = {
        auto_allow_on_uplinks = true
        vlan_list             = "897",
        multicast_policy      = "UCS-DEMO2",
        name                  = "AdminCAGIP-OSB3-897",
        native_vlan           = false
      },
      "120" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1101",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1101",
        native_vlan           = false
      },
      "121" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1102",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1102",
        native_vlan           = false
      },
      "122" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1103",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1103",
        native_vlan           = false
      },
      "123" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1104",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1104",
        native_vlan           = false
      },
      "124" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1105",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1105",
        native_vlan           = false
      },
      "125" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1106",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1106",
        native_vlan           = false
      },
      "126" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1107",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1107",
        native_vlan           = false
      },
      "127" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1108",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1108",
        native_vlan           = false
      },
      "128" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1109",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1109",
        native_vlan           = false
      },
      "129" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1110",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1110",
        native_vlan           = false
      },
      "130" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1111",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1111",
        native_vlan           = false
      },
      "131" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1112",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1112",
        native_vlan           = false
      },
      "132" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1113",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1113",
        native_vlan           = false
      },
      "133" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1114",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1114",
        native_vlan           = false
      },
      "134" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1115",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1115",
        native_vlan           = false
      },
      "135" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1116",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1116",
        native_vlan           = false
      },
      "136" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1117",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1117",
        native_vlan           = false
      },
      "137" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1118",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1118",
        native_vlan           = false
      },
      "138" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1119",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1119",
        native_vlan           = false
      },
      "139" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1120",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1120",
        native_vlan           = false
      },
      "140" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1121",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1121",
        native_vlan           = false
      },
      "141" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1122",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1122",
        native_vlan           = false
      },
      "142" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1123",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1123",
        native_vlan           = false
      },
      "143" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1124",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1124",
        native_vlan           = false
      },
      "144" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1125",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1125",
        native_vlan           = false
      },
      "145" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1126",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1126",
        native_vlan           = false
      },
      "146" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1127",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1127",
        native_vlan           = false
      },
      "147" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1128",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1128",
        native_vlan           = false
      },
      "148" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1129",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1129",
        native_vlan           = false
      },
      "149" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1130",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1130",
        native_vlan           = false
      },
      "150" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1131",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1131",
        native_vlan           = false
      },
      "151" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1132",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1132",
        native_vlan           = false
      },
      "152" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1133",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1133",
        native_vlan           = false
      },
      "153" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1134",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1134",
        native_vlan           = false
      },
      "154" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1135",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1135",
        native_vlan           = false
      },
      "155" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1136",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1136",
        native_vlan           = false
      },
      "156" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1137",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1137",
        native_vlan           = false
      },
      "157" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1138",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1138",
        native_vlan           = false
      },
      "158" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1139",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1139",
        native_vlan           = false
      },
      "159" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1140",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1140",
        native_vlan           = false
      },
      "160" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1141",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1141",
        native_vlan           = false
      },
      "161" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1142",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1142",
        native_vlan           = false
      },
      "162" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1143",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1143",
        native_vlan           = false
      },
      "163" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1144",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1144",
        native_vlan           = false
      },
      "164" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1145",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1145",
        native_vlan           = false
      },
      "165" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1146",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1146",
        native_vlan           = false
      },
      "166" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1147",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1147",
        native_vlan           = false
      },
      "167" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1148",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1148",
        native_vlan           = false
      },
      "168" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1149",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1149",
        native_vlan           = false
      },
      "169" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1150",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ACI-VMM-1150",
        native_vlan           = false
      },
      "170" = {
        auto_allow_on_uplinks = true
        vlan_list             = "1945",
        multicast_policy      = "UCS-DEMO2",
        name                  = "ProdCAGIP-CAGIP-1945",
        native_vlan           = false
      },
      "171" = {
        auto_allow_on_uplinks = true
        vlan_list             = "3110",
        multicast_policy      = "UCS-DEMO2",
        name                  = "iSCSI-A",
        native_vlan           = false
      },
      "172" = {
        auto_allow_on_uplinks = true
        vlan_list             = "3120",
        multicast_policy      = "UCS-DEMO2",
        name                  = "iSCSI-B",
        native_vlan           = false
      },
    }
  }
}