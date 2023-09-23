---\n
{{$protocols := .global.workflow.input.protocols}}
{{$netapp := .global.workflow.input.netapp}}
{{$imm := .global.workflow.input.imm}}
protocols:\n
{{if index $protocols "dhcp_servers"}}
  dhcp_servers:\n
{{range $i, $dhcps := $protocols.dhcp_servers}}
    - {{$dhcps}}\n
{{end}}
{{else}}
  dhcp_servers: []\n
{{end}}
{{if index $protocols "dns_domains"}}
  dns_domains:\n
{{range $i, $dnsdomains := $protocols.dns_domains}}
    - {{$dnsdomains}}\n
{{end}}
{{else}}
  dns_domains: []\n
{{end}}
{{if index $protocols "dns_servers"}}
  dns_servers:\n
{{range $i, $dnsservers := $protocols.dns_servers}}
    - {{$dnsservers}}\n
{{end}}
{{else}}
  dns_servers: []\n
{{end}}
  timezone: {{if index $protocols "timezone"}}{{$protocols.timezone}}{{else}}Etc/GMT{{end}}\n
{{if index $protocols "ntp_servers"}}
  ntp_servers:\n
{{range $i, $ntpservers := $protocols.ntp_servers}}
    - {{$ntpservers}}\n
{{end}}
{{else}}
  ntp_servers: []\n
{{end}}
netapp:\n
  - username: {{if index $netapp "username"}}{{$netapp.username}}{{else}}''{{end}}\n
    autosupport:\n
{{if index $netapp.autosupport "mail_hosts"}}
      mail_hosts:\n
{{range $i, $netapp_autosupport_mail_hosts := $netapp.autosupport.mail_hosts}}
        - {{$netapp_autosupport_mail_hosts}}\n
{{end}}
{{else}}
      mail_hosts: []\n
{{end}}
      proxy_url: {{if index $netapp.autosupport "proxy_url" }}{{$netapp.autosupport.proxy_url}}{{else}}''{{end}}\n
      from_address: {{if index $netapp.autosupport "from_address"}}{{$netapp.autosupport.from_address}}{{else}}admin@example.com{{end}}\n
{{if index $netapp.autosupport "to_addresses"}}
      to_addresses:\n
{{range $i, $netapp_autosupport_to_address := $netapp.autosupport.to_addresses}}
        - {{$netapp_autosupport_to_address}}\n
{{end}}
{{else}}
      to_addresses: []\n
{{end}}
    snmp:\n
      contact: {{if index $netapp.snmp "snmp_contact"}}{{$netapp.snmp.snmp_contact}}{{else}}''{{end}}\n
      location: {{if index $netapp.snmp "snmp_location"}}{{$netapp.snmp.snmp_location}}{{else}}''{{end}}\n
      username: {{if index $netapp.snmp "snmp_username"}}{{$netapp.snmp.snmp_username}}{{else}}''{{end}}\n
      trap_server: {{if index $netapp.snmp "trap_server"}}{{$netapp.snmp.trap_server}}{{else}}''{{end}}\n
    clusters:\n
{{range $i, $cluster := $netapp.clusters}}
      - login_banner: {{ if index $cluster "login_banner" }}{{ $cluster.login_banner }}{{else}}''{{ end  }}\n
        name: {{ if index $cluster "cluster_name" }}{{$cluster.cluster_name}}{{end}}\n
        nodes:\n
          node01: {{ if index $cluster.nodes "node01" }}{{$cluster.nodes.node01}}{{end}}\n
          node02: {{ if index $cluster.nodes "node02" }}{{$cluster.nodes.node02}}{{end}}\n
{{if index $cluster.nodes "data_ports"}}
          data_ports:\n
{{range $i, $netapp_data_ports := $cluster.nodes.data_ports}}
            - {{$netapp_data_ports}}\n
{{end}}
{{else}}
          data_ports: []\n
{{end}}
          data_speed: {{if index $cluster.nodes "data_speed"}}{{$cluster.nodes.data_speed}}{{else}}100{{end}}\n
{{if index $cluster.nodes "fcp_ports"}}
          fcp_ports:\n
{{range $i, $netapp_fcp_ports := $cluster.nodes.fcp_ports}}
            - {{$netapp_fcp_ports}}\n
{{end}}
{{else}}
          fcp_ports: []\n
{{end}}
          fcp_speed: {{if index $cluster.nodes "fcp_speed"}}{{$cluster.nodes.fcp_speed}}{{else}}32{{end}}\n
          network:\n
{{if index $cluster.nodes "network_data"}}
            data:\n
{{range $i, $data := $cluster.nodes.network_data}}
              - {{$data}}\n
{{end}}
{{else}}
            data: []\n
{{end}}
            management: {{if index $cluster.nodes "network_management"}}{{$cluster.nodes.network_management}}{{else}}''{{end}}\n
        svm:\n
          login_banner: {{ if index $cluster "svm_login_banner" }}{{ $cluster.svm_login_banner }}{{else}}''{{ end }}\n
          name: {{$cluster.svm}}\n
{{if index $cluster "volumes"}}
          volumes:\n
{{range $i, $volume := $cluster.volumes}}
            - name: {{$volume.name}}\n
              os_type: {{if index $volume "os_type"}}{{$volume.os_type}}{{else}}vmware{{end}}\n
              protocol: {{if index $volume "protocol"}}{{$volume.protocol}}{{else}}nfs{{end}}\n
              size: {{$volume.size}}\n
              volume_type: {{if index $volume "volume_type"}}{{$volume.volume_type}}{{else}}data{{end}}\n
{{end}}
{{else}}
          volumes: []\n
{{end}}
{{end}}
intersight:\n
  - organization: {{if index $imm "organization"}}{{$imm.organization}}{{end}}\n
    cfg_qos_priorities: {{if index $imm "cfg_qos_priorities"}}{{$imm.cfg_qos_priorities}}{{else}}false{{end}}\n
    discovery_protocol: {{if index $imm "discovery_protocol"}}{{$imm.discovery_protocol}}{{else}}cdp{{end}}\n
{{if index $imm "domains"}}
    domains:\n
{{range $i, $domain := $imm.domains}}
        switch_mode: {{if index $domain "switch_mode"}}{{$domain.switch_mode}}{{else}}end-host{{end}}\n
{{if index $domain "serial_numbers"}}
        serial_numbers:\n
{{range $i, $serial := $domain.serial_numbers}}
          - {{$serial}}\n
{{end}}
{{else}}
        serial_numbers: []\n
{{end}}
{{if index $domain "fcp_ports"}}
        eth_uplink_ports:\n
{{range $i, $eth_uplink_ports := $domain.eth_uplink_ports}}
          - {{$eth_uplink_ports}}\n
{{end}}
{{else}}
        eth_uplink_ports: []\n
{{end}}
        eth_uplink_speed: {{if index $domain "eth_uplink_speed"}}{{$domain.eth_uplink_speed}}{{else}}Auto{{end}}\n
        eth_breakout_speed: {{if index $domain "eth_breakout_speed"}}{{$domain.eth_breakout_speed}}{{else}}25G{{end}}\n
{{if index $domain "fcp_ports"}}
        fcp_uplink_ports:\n
{{range $i, $fcp_uplink_ports := $domain.fcp_ports}}
          - {{$fcp_uplink_ports}}\n
{{end}}
{{else}}
        fcp_uplink_ports: []\n
{{end}}
        fcp_uplink_speed: {{if index $domain "fcp_breakout_speed"}}{{$domain.fcp_breakout_speed}}{{else}}32G{{end}}\n
{{if index $domain "vsans"}}
        vsans:\n
{{range $i, $vsan := $domain.vsans}}
          - {{$vsan}}\n
{{end}}
{{else}}
        vsans: []\n
{{end}}
        network:\n
{{if index $domain "network_data"}}
          data:\n
{{range $i, $data := $domain.network_data}}
            - {{$data}}\n
{{end}}
{{else}}
          data: []\n
{{end}}
          management: {{if index $domain "network_management"}}{{$domain.network_management}}{{else}}''{{end}}\n
{{if index $domain "profiles" }}
        profiles:\n
{{range $i, $profile := $domain.profiles}}
          - equipment_type: {{if index $profile "equipment_type"}}{{$profile.equipment_type}}{{else}}Chassis{{end}}\n
            identifier: {{if index $profile "identifier"}}{{$profile.identifier}}{{else}}1{{end}}\n
{{if index $profile "domain_ports"}}
            domain_ports:\n
{{range $i, $domain_ports := $profile.domain_ports}}
              - {{$domain_ports}}\n
{{end}}
{{else}}
            domain_ports: []\n
{{end}}
            profile_start: {{if index $profile "profile_start"}}{{$profile.profile_start}}{{end}}\n
            suffix_digits: {{if index $profile "suffix_digits"}}{{$profile.suffix_digits}}{{else}}2{{end}}\n
            inband_start: {{if index $profile "inband_start"}}{{$profile.inband_start}}{{end}}\n
            os_type: {{if index $profile "os_type"}}{{$profile.os_type}}{{else}}VMware{{end}}\n
{{end}}
{{else}}
        profiles: []\n
{{end}}
{{end}}
{{else}}
    domains: []\n
{{end}}
    firmware:\n
      blades: {{if index $imm "firmware"}}{{$imm.firmware}}{{end}}\n
      rackmount: {{if index $imm "rack_firmware"}}{{$imm.rack_firmware}}{{end}}\n
    pools:\n
      prefix: {{if index $imm "pools_prefix"}}{{$imm.pools_prefix}}{{end}}\n
    policies:\n
      boot_volume: {{ if index $imm.policies "boot_volume" }}{{ $imm.policies.boot_volume }}{{else}}san{{ end }}\n
      prefix: {{if index $imm.policies "prefix"}}{{$imm.policies.prefix}}{{end}}\n
      local_user: {{if index $imm.policies "local_user"}}{{$imm.policies.local_user}}{{end}}\n
      snmp:\n
        contact: {{if index $imm.policies.snmp "contact"}}{{$imm.policies.snmp.contact}}{{else}}''{{end}}\n
        location: {{if index $imm.policies.snmp "location"}}{{$imm.policies.snmp.location}}{{else}}''{{end}}\n
        username: {{if index $imm.policies.snmp "username"}}{{$imm.policies.snmp.username}}{{else}}''{{end}}\n
{{if index $imm.policies.snmp "snmp_servers"}}
        servers:\n
{{range $i, $snmp_servers := $imm.policies.snmp.snmp_servers}}
          - {{$snmp_servers}}\n
{{end}}
{{else}}
        servers: []\n
{{end}}
      syslog:\n
{{if index $imm.policies "syslog_servers"}}
        servers:\n
{{range $i, $syslog_servers := $imm.policies.syslog_servers}}
          - {{$syslog_servers}}\n
{{end}}
{{else}}
        servers: []\n
{{end}}
    virtualization:\n
      - datacenter: {{if index $imm.virtualization "datacenter"}}{{$imm.virtualization.datacenter}}{{else}}flexpod{{end}}\n
        license_type: {{if index $imm.virtualization "license_type"}}{{$imm.virtualization.license_type}}{{else}}enterprise{{end}}\n
        name: {{if index $imm.virtualization "vcenter"}}{{$imm.virtualization.vcenter}}{{end}}\n
        type: {{if index $imm.virtualization "type"}}{{$imm.virtualization.type}}{{end}}\n
        username: {{if index $imm.virtualization "vcenter_username"}}{{$imm.virtualization.vcenter_username}}{{else}}administrator@vsphere.local{{end}}\n
{{if index $imm.virtualization "virtual_switches"}}
        virtual_switches:\n
{{range $i, $switch := $imm.virtualization.virtual_switches}}
{{if index $switch "data_types"}}
          - data_types:\n
{{range $i, $data_types := $switch.data_types}}
              - {{$data_types}}\n
{{end}}
{{else}}
          - data_types: []\n
{{end}}
            name: {{if index $switch "name"}}{{$switch.name}}{{end}}\n
            type: {{if index $switch "type"}}{{$switch.type}}{{else}}dvs{{end}}\n
            alternate_name: {{if index $switch "alternate_name"}}{{$switch.alternate_name}}{{else}}''{{end}}\n
{{end}}
{{else}}
        virtual_switches: []\n
{{end}}
nxos_configure: {{if index .global.workflow.input "config_nxos"}}{{.global.workflow.input.config_nxos}}{{else}}false{{end}}\n
{{if eq .global.workflow.input.config_nxos true}}
nxos:\n
  - username: {{if index .global.workflow.input.nxos "username"}}{{.global.workflow.input.nxos.username}}{{end}}\n
{{if index .global.workflow.input.nxos "switches"}}
    switches:\n
{{range $i, $switch := .global.workflow.input.nxos.switches}}
      - hostname: {{if index $switch "hostname"}}{{$switch.hostname}}{{end}}\n
        switch_type: {{if index $switch "switch_type"}}{{$switch.switch_type}}{{else}}network{{end}}\n
        configure: {{if index $switch "configure_l3"}}{{$switch.configure_l3}}{{else}}false{{end}}\n
        breakout_speed: {{if index $switch "breakout_speed"}}{{$switch.breakout_speed}}{{else}}25G{{end}}\n
        vpc_config:\n
          domain_id: {{if index $switch "vpc_domain_id"}}{{$switch.vpc_domain_id}}{{end}}\n
          keepalive_ip: {{if index $switch "vpc_keepalive_ip"}}{{$switch.vpc_keepalive_ip}}{{end}}\n
{{if index $switch "vpc_keepalive_ports"}}
          keepalive_ports:\n
{{range $i, $vpc_keepalive_ports := $switch.vpc_keepalive_ports}}
            - {{$vpc_keepalive_ports}}\n
{{end}}
{{else}}
          keepalive_ports: []\n
{{end}}
{{if index $switch "vpc_peer_ports"}}
          peer_ports:\n
{{range $i, $vpc_peer_ports := $switch.vpc_peer_ports}}
            - {{$vpc_peer_ports}}\n
{{end}}
{{else}}
          peer_ports: []\n
{{end}}
{{end}}
{{else}}
    switches: []\n
{{end}}
{{else}}
nxos: []\n
{{end}}
{{if index .global.workflow.input "vlans"}}
vlans:\n
{{range $i, $vlan := .global.workflow.input.vlans}}
  - vlan_type: {{if index $vlan "vlan_type"}}{{$vlan.vlan_type}}{{else}}vm{{end}}\n
    vlan_id: {{if index $vlan "vlan_id"}}{{$vlan.vlan_id}}{{end}}\n
    name: {{if index $vlan "name"}}{{$vlan.name}}{{end}}\n
    network: {{if index $vlan "network"}}{{$vlan.network}}{{end}}\n
    configure_l2: {{if index $vlan "configure_l2"}}{{$vlan.configure_l2}}{{else}}false{{end}}\n
    configure_l3: {{if index $vlan "configure_l3"}}{{$vlan.configure_l3}}{{else}}false{{end}}\n
    disjoint: {{if index $vlan "disjoint"}}{{$vlan.disjoint}}{{else}}false{{end}}\n
    native_vlan: {{if index $vlan "native_vlan"}}{{$vlan.native_vlan}}{{else}}false{{end}}\n
    switch_type: {{if index $vlan "switch_type"}}{{$vlan.switch_type}}{{end}}\n
    ranges:\n
      controller: {{if index $vlan "ranges_controller"}}{{$vlan.ranges_controller}}{{end}}\n
      pool: {{if index $vlan "ranges_pool"}}{{$vlan.ranges_pool}}{{end}}\n
      server: {{if index $vlan "ranges_server"}}{{$vlan.ranges_server}}{{end}}\n
{{end}}
{{else}}
vlans: []\n
{{end}}
{{if index .global.workflow.input "vlan_ranges"}}
vlan_ranges:\n
{{range $i, $vlan := .global.workflow.input.vlan_ranges}}
  - vlan_range: {{if index $vlan "vlan_range"}}{{$vlan.vlan_range}}{{end}}\n
    name_prefix: {{if index $vlan "name_prefix"}}{{$vlan.name_prefix}}{{end}}\n
    configure_l2: {{if index $vlan "configure_l2"}}{{$vlan.configure_l2}}{{else}}false{{end}}\n
    disjoint: {{if index $vlan "disjoint"}}{{$vlan.disjoint}}{{else}}false{{end}}\n
{{end}}
{{else}}
vlan_ranges: []\n
{{end}}