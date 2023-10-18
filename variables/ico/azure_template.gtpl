---\n
{{$protocols := .global.workflow.input.protocols}}
{{$azurestack := .global.workflow.input.azurestack}}
{{$intersight := .global.workflow.input.intersight}}
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
azurestack:\n
  - active_directory:
      domain: {{if index $azurestack.active_directory "domain"}}{{$azurestack.active_directory.domain}}{{else}}example.com{{end}}\n
      administrator: {{if index $azurestack.active_directory "administrator"}}{{$azurestack.active_directory.administrator}}{{else}}administrator{{end}}\n
    azurestack_admin: {{if index $azurestack "azurestack_admin"}}{{$azurestack.azurestack_admin}}{{else}}hciadmin{{end}}\n
    azurestack_ou: {{if index $azurestack "azurestack_ou"}}{{$azurestack.azurestack_ou}}{{else}}AzureStack{{end}}\n
    azurestack_prefix: {{if index $azurestack "azurestack_prefix"}}{{$azurestack.azurestack_prefix}}{{else}}AzS{{end}}\n
    clusters:\n
{{range $i, $cluster := $azurestack.clusters}}
      - name: {{ if index $cluster "name" }}{{ $cluster.name }}{{else}}CLUSTER01{{ end  }}\n
        subscription: {{ if index $cluster "subscription" }}{{$cluster.subscription}}53614803-d327-4397-bf55-8dedcc24be0d{{end}}\n
        members:\n
{{range $e, $member := $cluster.members}}
          - cimc: {{ if index $member "cimc" }}{{ $cluster.cimc }}{{else}}198.18.1.1{{ end  }}\n
            hostname: {{ if index $member "hostname" }}{{$member.hostname}}{{end}}\n
            management: {{ if index $member "management" }}{{$member.management}}{{end}}\n
{{end}}
{{end}}
intersight:\n
  - organization: {{if index $intersight "organization"}}{{$intersight.organization}}{{end}}\n
    cimc_default: {{if index $intersight "cimc_default"}}{{$intersight.cimc_default}}{{else}}false{{end}}\n
    firmware:{{if index $intersight "firmware"}}{{$intersight.firmware}}{{end}}\n\n
    policies:\n
      boot_volume: {{ if index $intersight.policies "boot_volume" }}{{ $intersight.policies.boot_volume }}{{else}}m2{{ end }}\n
      local_user: {{if index $intersight.policies "local_user"}}{{$intersight.policies.local_user}}{{end}}\n
      prefix: {{if index $intersight.policies "prefix"}}{{$intersight.policies.prefix}}{{end}}\n
      snmp:\n
        contact: {{if index $intersight.policies.snmp "contact"}}{{$intersight.policies.snmp.contact}}{{else}}''{{end}}\n
        location: {{if index $intersight.policies.snmp "location"}}{{$intersight.policies.snmp.location}}{{else}}''{{end}}\n
        username: {{if index $intersight.policies.snmp "username"}}{{$intersight.policies.snmp.username}}{{else}}''{{end}}\n
{{if index $intersight.policies.snmp "snmp_servers"}}
        servers:\n
{{range $i, $snmp_servers := $intersight.policies.snmp.snmp_servers}}
          - {{$snmp_servers}}\n
{{end}}
{{else}}
        servers: []\n
{{end}}
      syslog:\n
{{if index $intersight.policies "syslog_servers"}}
        servers:\n
{{range $i, $syslog_servers := $intersight.policies.syslog_servers}}
          - {{$syslog_servers}}\n
{{end}}
{{else}}
        servers: []\n
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
    switch_type: {{if index $vlan "switch_type"}}{{$vlan.switch_type}}{{end}}\n
    ranges:\n
      server: {{if index $vlan "ranges_server"}}{{$vlan.ranges_server}}{{end}}\n
{{end}}
{{else}}
vlans: []\n
{{end}}