{{$input := .global.workflow.input}}
{{$protocols := .global.workflow.input.protocols}}
{{$netapp := .global.workflow.input.netapp}}
{{$imm := .global.workflow.input.imm}}
{{$nxos := .global.workflow.input.nxos}}
{{$vlans := .global.workflow.input.vlans}}
{{$vlan_ranges := .global.workflow.input.vlan_ranges}}
---
protocols:
{{if index $protocols "dhcp_servers"}}
  - dhcp_servers: 
  {{range $i, $dhcps := $protocols.dhcp_servers}}
      - {{$dhcps}}
  {{end}}
{{else}}
  - dhcp_servers: []
{{end}}
{{if index $protocols "dns_domains"}}
    dns_domains:
  {{range $i, $dnsdomains := $protocols.dns_domains}}
      - {{$dnsdomains}}
  {{end}}
{{else}}
    dns_domains: []
{{end}}
{{if index $protocols "dns_servers"}}
    dns_servers:
  {{range $i, $dnsservers := $protocols.dns_servers}}
      - {{$dnsservers}}
  {{end}}
{{else}}
    dns_servers: []
{{end}}
    timezone: {{if index $protocols "timezone"}}{{$protocols.timezone}}{{end}}
{{if index $protocols "ntp_servers"}}
    ntp_servers:
  {{range $i, $ntpservers := $protocols.ntp_servers}}
      - {{$ntpservers}}
  {{end}}
{{else}}
    ntp_servers: []
{{end}}
netapp:
  - username: {{if index $netapp "username"}}{{$netapp.username}}{{end}}
    autosupport:
{{if index $netapp.autosupport "mail_hosts"}}
      mail_hosts:
  {{range $i, $netapp_autosupport_mail_hosts := $netapp.autosupport.mail_hosts}}
        - {{$netapp_autosupport_mail_hosts}}
  {{end}}
{{else}}
      mail_hosts: []
{{end}}
      proxy_url: {{if index $netapp.autosupport "proxy_url" }}{{$netapp.autosupport.proxy_url}}{{end}}
      from_address: {{if index $netapp.autosupport "from_address"}}{{$netapp.autosupport.from_address}}{{end}}
{{if index $netapp.autosupport "to_addresses"}}
      to_addresses:
  {{range $i, $netapp_autosupport_to_address := $netapp.autosupport.to_addresses}}
        - {{$netapp_autosupport_to_address}}
  {{end}}
{{else}}
      to_addresses: []
{{end}}
    snmp:
      contact: {{if index $netapp.snmp "snmp_contact"}}{{$netapp.snmp.snmp_contact}}{{end}}
      location: {{if index $netapp.snmp "snmp_location"}}{{$netapp.snmp.snmp_location}}{{end}}
      username: {{if index $netapp.snmp "snmp_username"}}{{$netapp.snmp.snmp_username}}{{end}}
      trap_server: {{if index $netapp.snmp "trap_server"}}{{$netapp.snmp.trap_server}}{{end}}
    clusters:
{{range $i, $cluster := $netapp.clusters}}
      - login_banner: {{ if index $netapp "login_banner" }}{{ $cluster.login_banner }}{{ end  }}
        name: {{if index $cluster "cluster_name"}}{{$cluster.cluster_name}}{{end}}
        nodes:
          node01: {{if index $cluster.nodes "node01"}}{{$cluster.nodes.node01}}{{end}}
          node02: {{if index $cluster.nodes "node02"}}{{$cluster.nodes.node02}}{{end}}
  {{if index $cluster.nodes "data_ports"}}
          data_ports:
    {{range $i, $netapp_data_ports := $cluster.nodes.data_ports}}
            - {{$netapp_data_ports}}
    {{end}}
  {{else}}
          data_ports: []
  {{end}}
          data_speed: {{if index $cluster.nodes "data_speed"}}{{$cluster.nodes.data_speed}}{{end}}
  {{if index $cluster.nodes "fcp_ports"}}
          fcp_ports:
    {{range $i, $netapp_fcp_ports := $cluster.nodes.fcp_ports}}
            - {{$netapp_fcp_ports}}
    {{end}}
  {{else}}
          fcp_ports: []
  {{end}}
          fcp_speed: {{if index $cluster.nodes "fcp_speed"}}{{$cluster.nodes.fcp_speed}}{{end}}
          network:
  {{if index $cluster.nodes "network_data"}}
            data:
    {{range $i, $data := $cluster.nodes.network_data}}
              - {{$data}}
    {{end}}
  {{else}}
            data: []
  {{end}}
            management: {{if index $cluster.nodes "network_management"}}{{$cluster.nodes.network_management}}{{end}}

        svm:
          login_banner: {{ if index $netapp "login_banner" }}{{ $netapp.svm_login_banner }}{{ end }}
          name: {{if index $cluster "svm"}}{{$cluster.svm}}{{end}}
  {{if index $cluster "volumes"}}
          volumes:
    {{range $i, $volume := $cluster.volumes}}
            - name: {{if index $volume "name"}}{{$volume.name}}{{end}}
              os_type: {{if index $volume "os_type"}}{{$volume.os_type}}{{end}}
              protocol: {{if index $volume "protocol"}}{{$volume.protocol}}{{end}}
              size: {{if index $volume "size"}}{{$volume.size}}{{end}}
              volume_type: {{if index $volume "volume_type"}}{{$volume.volume_type}}{{end}}
    {{end}}
  {{else}}
          volumes: []
  {{end}}
{{end}}
intersight:
  - organization: {{if index $imm "organization"}}{{$imm.organization}}{{end}}
    cfg_qos_priorities: {{if index $imm "cfg_qos_priorities"}}{{$imm.cfg_qos_priorities}}{{else}}false{{end}}
    discovery_protocol: {{if index $imm "discovery_protocol"}}{{$imm.discovery_protocol}}{{end}}
{{if index $imm "domains"}}
    domains:
  {{range $i, $domain := $imm.domains}}
      - name: {{if index $domain "domain_name"}}{{$domain.domain_name}}{{end}}
        switch_mode: {{if index $domain "switch_mode"}}{{$domain.switch_mode}}{{end}}
    {{if index $domain "serial_numbers"}}
        serial_numbers:
      {{range $i, $serial := $domain.serial_numbers}}
          - {{$serial}}
      {{end}}
    {{else}}
        serial_numbers: []
    {{end}}
        eth_uplink_ports:
    {{range $i, $eth_uplink_ports := $domain.eth_uplink_ports}}
          - {{$eth_uplink_ports}}
    {{end}}
        eth_uplink_speed: {{if index $domain "eth_uplink_speed"}}{{$domain.eth_uplink_speed}}{{end}}
        eth_breakout_speed: {{if index $domain "eth_breakout_speed"}}{{$domain.eth_breakout_speed}}{{end}}
    {{if index $domain "fcp_ports"}}
        fcp_uplink_ports:
      {{range $i, $fcp_uplink_ports := $domain.fcp_ports}}
          - {{$fcp_uplink_ports}}
      {{end}}
    {{else}}
        fcp_uplink_ports: []
    {{end}}
        fcp_uplink_speed: {{if index $domain "fcp_breakout_speed"}}{{$domain.fcp_breakout_speed}}{{end}}
    {{if index $domain "vsans"}}
        vsans:
      {{range $i, $vsan := $domain.vsans}}
          - {{$vsan}}
      {{end}}
    {{else}}
        vsans: []
    {{end}}
        network:
    {{if index $domain "network_data"}}
          data:
      {{range $i, $data := $domain.network_data}}
            - {{$data}}
      {{end}}
    {{else}}
          data: []
    {{end}}
          management: {{if index $domain "network_management"}}{{$domain.network_management}}{{end}}
    {{if index $domain "profiles" }}
        profiles:
      {{range $i, $profile := $domain.profiles}}
          - equipment_type: {{if index $profile "equipment_type"}}{{$profile.equipment_type}}{{end}}
            identifier: {{if index $profile "identifier"}}{{$profile.identifier}}{{end}}
        {{if index $profile "domain_ports"}}
            domain_ports:
          {{range $i, $domain_ports := $profile.domain_ports}}
              - {{$domain_ports}}
          {{end}}
        {{else}}
            domain_ports: []
        {{end}}
            profile_start: {{if index $profile "profile_start"}}{{$profile.profile_start}}{{end}}
            suffix_digits: {{if index $profile "suffix_digits"}}{{$profile.suffix_digits}}{{end}}
            inband_start: {{if index $profile "inband_start"}}{{$profile.inband_start}}{{end}}
            os_type: {{if index $profile "os_type"}}{{$profile.os_type}}{{end}}
      {{end}}
    {{else}}
        profiles: []
    {{end}}
  {{end}}
{{else}}
    domains: []
{{end}}
    firmware:
      blades: {{if index $imm "firmware"}}{{$imm.firmware}}{{end}}
      rackmount: {{if index $imm "rack_firmware"}}{{$imm.rack_firmware}}{{end}}
    pools:
      prefix: {{if index $imm "pools_prefix"}}{{$imm.pools_prefix}}{{end}}
    policies:
      boot_volume: {{ if index $imm.policies "boot_volume" }}{{ $imm.policies.boot_volume }}{{ end }}
      prefix: {{if index $imm.policies "prefix"}}{{$imm.policies.prefix}}{{end}}
      local_user: {{if index $imm.policies "local_user"}}{{$imm.policies.local_user}}{{end}}
      snmp:
        contact: {{if index $imm.policies.snmp "contact"}}{{$imm.policies.snmp.contact}}{{end}}
        location: {{if index $imm.policies.snmp "location"}}{{$imm.policies.snmp.location}}{{end}}
        username: {{if index $imm.policies.snmp "username"}}{{$imm.policies.snmp.username}}{{end}}
{{if index $imm.policies.snmp "snmp_servers"}}
        servers:
  {{range $i, $snmp_servers := $imm.policies.snmp.snmp_servers}}
          - {{$snmp_servers}}
  {{end}}
{{else}}
        servers: []
{{end}}
      syslog: 
{{if index $imm.policies "syslog_servers"}}
        servers: 
  {{range $i, $syslog_servers := $imm.policies.syslog_servers}}
          - {{$syslog_servers}}
  {{end}}
{{else}}
        servers: []
{{end}}
    virtualization:
      - datacenter: {{if index $imm.virtualization "datacenter"}}{{$imm.virtualization.datacenter}}{{end}}
        license_type: {{if index $imm.virtualization "license_type"}}{{$imm.virtualization.license_type}}{{end}}
        name: {{if index $imm.virtualization "vcenter"}}{{$imm.virtualization.vcenter}}{{end}}
        type: {{if index $imm.virtualization "type"}}{{$imm.virtualization.type}}{{end}}
        username: {{if index $imm.virtualization "vcenter_username"}}{{$imm.virtualization.vcenter_username}}{{end}}
{{if index $imm.virtualization "virtual_switches"}}
        virtual_switches:
  {{range $i, $switch := $imm.virtualization.virtual_switches}}
    {{if index $switch "data_types"}}
          - data_types:
      {{range $i, $data_types := $switch.data_types}}
              - {{$data_types}}
      {{end}}
    {{else}}
          - data_types: []
    {{end}}
            name: {{if index $switch "name"}}{{$switch.name}}{{end}}
            type: {{if index $switch "type"}}{{$switch.type}}{{end}}
            alternate_name: {{if index $switch "alternate_name"}}{{$switch.alternate_name}}{{end}}
  {{end}}
{{else}}
        virtual_switches: []
{{end}}
{{if eq .global.workflow.input.config_nxos true}}
nxos:
  - username: {{if index .global.workflow.input.nxos "username"}}{{.global.workflow.input.nxos.username}}{{end}}
  {{if index .global.workflow.input.nxos "switches"}}
    switches:
    {{range $i, $switch := .global.workflow.input.nxos.switches}}
      - hostname: {{if index $switch "hostname"}}{{$switch.hostname}}{{end}}
        switch_type: {{if index $switch "switch_type"}}{{$switch.switch_type}}{{end}}
        configure: {{if index $switch "configure_l3"}}{{$switch.configure_l3}}{{else}}false{{end}}
        breakout_speed: {{if index $switch "breakout_speed"}}{{$switch.breakout_speed}}{{end}}
        vpc_config:
          domain_id: {{if index $switch "vpc_domain_id"}}{{$switch.vpc_domain_id}}{{end}}
          keepalive_ip: {{if index $switch "vpc_keepalive_ip"}}{{$switch.vpc_keepalive_ip}}{{end}}
      {{if index $switch "vpc_keepalive_ports"}}
          keepalive_ports:
        {{range $i, $vpc_keepalive_ports := $switch.vpc_keepalive_ports}}
            - {{$vpc_keepalive_ports}}
        {{end}}
      {{else}}
          keepalive_ports: []
      {{end}}
      {{if index $switch "vpc_peer_ports"}}
          peer_ports:
        {{range $i, $vpc_peer_ports := $switch.vpc_peer_ports}}
            - {{$vpc_peer_ports}}
        {{end}}
      {{else}}
          peer_ports: []
      {{end}}
  {{else}}
    switches: []
  {{end}}
  {{end}}
{{else}}
nxos: []
{{end}}
{{if index .global.workflow.input "vlans"}}
vlans:
  {{range $i, $vlan := .global.workflow.input.vlans}}
  - vlan_type: {{if index $vlan "vlan_type"}}{{$vlan.vlan_type}}{{end}}
    vlan_id: {{if index $vlan "vlan_id"}}{{$vlan.vlan_id}}{{end}}
    name: {{if index $vlan "name"}}{{$vlan.name}}{{end}}
    network: {{if index $vlan "network"}}{{$vlan.network}}{{end}}
    configure_l2: {{if index $vlan "configure_l2"}}{{$vlan.configure_l2}}{{else}}false{{end}}
    configure_l3: {{if index $vlan "configure_l3"}}{{$vlan.configure_l3}}{{else}}false{{end}}
    disjoint: {{if index $vlan "disjoint"}}{{$vlan.disjoint}}{{else}}false{{end}}
    native_vlan: {{if index $vlan "native_vlan"}}{{$vlan.native_vlan}}{{else}}false{{end}}
    switch_type: {{if index $vlan "switch_type"}}{{$vlan.switch_type}}{{end}}
    ranges:
      controller: {{if index $vlan "ranges_controller"}}{{$vlan.ranges_controller}}{{end}}
      pool: {{if index $vlan "ranges_pool"}}{{$vlan.ranges_pool}}{{end}}
      server: {{if index $vlan "ranges_server"}}{{$vlan.ranges_server}}{{end}}
  {{end}}
{{else}}
vlans: []
{{end}}
{{if index .global.workflow.input "vlan_ranges"}}
vlan_ranges:
  {{range $i, $vlan := .global.workflow.input.vlan_ranges}}
  - vlan_range: {{if index $vlan "vlan_range"}}{{$vlan.vlan_range}}{{end}}
    name_prefix: {{if index $vlan "name_prefix"}}{{$vlan.name_prefix}}{{end}}
    configure_l2: {{if index $vlan "configure_l2"}}{{$vlan.configure_l2}}{{else}}false{{end}}
    disjoint: {{if index $vlan "disjoint"}}{{$vlan.disjoint}}{{else}}false{{end}}
  {{end}}
{{else}}
vlan_ranges: []
{{end}}