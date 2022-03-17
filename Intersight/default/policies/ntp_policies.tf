#_________________________________________________________________________
#
# Intersight NTP Policies Variables
# GUI Location: Configure > Policies > Create Policy > NTP > Start
#_________________________________________________________________________

variable "ntp_policies" {
  default = {
    default = {
      description = ""
      enabled     = true
      ntp_servers = ["time-a-g.nist.gov", "time-b-g.nist.gov"]
      tags        = []
      timezone    = "Etc/GMT"
    }
  }
  description = <<-EOT
  key - Name of the NTP Policy.
  * description - Description to Assign to the Policy.
  * enabled - Flag to Enable or Disable the Policy.
  * ntp_servers - List of NTP Servers to Assign to the Policy.
  * tags - List of Key/Value Pairs to Assign as Attributes to the Policy.
  * timezone - Timezone to Assign to the Policy.  Options Below.
    - Africa/Abidjan
    - Africa/Accra
    - Africa/Algiers
    - Africa/Bissau
    - Africa/Cairo
    - Africa/Casablanca
    - Africa/Ceuta
    - Africa/El_Aaiun
    - Africa/Johannesburg
    - Africa/Khartoum
    - Africa/Lagos
    - Africa/Maputo
    - Africa/Monrovia
    - Africa/Nairobi
    - Africa/Ndjamena
    - Africa/Tripoli
    - Africa/Tunis
    - Africa/Windhoek
    - America/Anchorage
    - America/Araguaina
    - America/Argentina/Buenos_Aires
    - America/Asuncion
    - America/Bahia
    - America/Barbados
    - America/Belem
    - America/Belize
    - America/Boa_Vista
    - America/Bogota
    - America/Campo_Grande
    - America/Cancun
    - America/Caracas
    - America/Cayenne
    - America/Cayman
    - America/Chicago
    - America/Costa_Rica
    - America/Cuiaba
    - America/Curacao
    - America/Danmarkshavn
    - America/Dawson_Creek
    - America/Denver
    - America/Edmonton
    - America/El_Salvador
    - America/Fortaleza
    - America/Godthab
    - America/Grand_Turk
    - America/Guatemala
    - America/Guayaquil
    - America/Guyana
    - America/Halifax
    - America/Havana
    - America/Hermosillo
    - America/Iqaluit
    - America/Jamaica
    - America/La_Paz
    - America/Lima
    - America/Los_Angeles
    - America/Maceio
    - America/Managua
    - America/Manaus
    - America/Martinique
    - America/Mazatlan
    - America/Mexico_City
    - America/Miquelon
    - America/Montevideo
    - America/Nassau
    - America/New_York
    - America/Noronha
    - America/Panama
    - America/Paramaribo
    - America/Phoenix
    - America/Port_of_Spain
    - America/Port-au-Prince
    - America/Porto_Velho
    - America/Puerto_Rico
    - America/Recife
    - America/Regina
    - America/Rio_Branco
    - America/Santiago
    - America/Santo_Domingo
    - America/Sao_Paulo
    - America/Scoresbysund
    - America/St_Johns
    - America/Tegucigalpa
    - America/Thule
    - America/Tijuana
    - America/Toronto
    - America/Vancouver
    - America/Whitehorse
    - America/Winnipeg
    - America/Yellowknife
    - Antarctica/Casey
    - Antarctica/Davis
    - Antarctica/DumontDUrville
    - Antarctica/Mawson
    - Antarctica/Palmer
    - Antarctica/Rothera
    - Antarctica/Syowa
    - Antarctica/Vostok
    - Asia/Almaty
    - Asia/Amman
    - Asia/Aqtau
    - Asia/Aqtobe
    - Asia/Ashgabat
    - Asia/Baghdad
    - Asia/Baku
    - Asia/Bangkok
    - Asia/Beirut
    - Asia/Bishkek
    - Asia/Brunei
    - Asia/Calcutta
    - Asia/Choibalsan
    - Asia/Colombo
    - Asia/Damascus
    - Asia/Dhaka
    - Asia/Dili
    - Asia/Dubai
    - Asia/Dushanbe
    - Asia/Gaza
    - Asia/Hong_Kong
    - Asia/Hovd
    - Asia/Irkutsk
    - Asia/Jakarta
    - Asia/Jayapura
    - Asia/Jerusalem
    - Asia/Kabul
    - Asia/Kamchatka
    - Asia/Karachi
    - Asia/Katmandu
    - Asia/Kolkata
    - Asia/Krasnoyarsk
    - Asia/Kuala_Lumpur
    - Asia/Macau
    - Asia/Magadan
    - Asia/Makassar
    - Asia/Manila
    - Asia/Nicosia
    - Asia/Omsk
    - Asia/Pyongyang
    - Asia/Qatar
    - Asia/Rangoon
    - Asia/Riyadh
    - Asia/Saigon
    - Asia/Seoul
    - Asia/Shanghai
    - Asia/Singapore
    - Asia/Taipei
    - Asia/Tashkent
    - Asia/Tbilisi
    - Asia/Tehran
    - Asia/Thimphu
    - Asia/Tokyo
    - Asia/Ulaanbaatar
    - Asia/Vladivostok
    - Asia/Yakutsk
    - Asia/Yekaterinburg
    - Asia/Yerevan
    - Atlantic/Azores
    - Atlantic/Bermuda
    - Atlantic/Canary
    - Atlantic/Cape_Verde
    - Atlantic/Faroe
    - Atlantic/Reykjavik
    - Atlantic/South_Georgia
    - Atlantic/Stanley
    - Australia/Adelaide
    - Australia/Brisbane
    - Australia/Darwin
    - Australia/Hobart
    - Australia/Perth
    - Australia/Sydney
    - Etc/GMT
    - Europe/Amsterdam
    - Europe/Andorra
    - Europe/Athens
    - Europe/Belgrade
    - Europe/Berlin
    - Europe/Brussels
    - Europe/Bucharest
    - Europe/Budapest
    - Europe/Chisinau
    - Europe/Copenhagen
    - Europe/Dublin
    - Europe/Gibraltar
    - Europe/Helsinki
    - Europe/Istanbul
    - Europe/Kaliningrad
    - Europe/Kiev
    - Europe/Lisbon
    - Europe/London
    - Europe/Luxembourg
    - Europe/Madrid
    - Europe/Malta
    - Europe/Minsk
    - Europe/Monaco
    - Europe/Moscow
    - Europe/Oslo
    - Europe/Paris
    - Europe/Prague
    - Europe/Riga
    - Europe/Rome
    - Europe/Samara
    - Europe/Sofia
    - Europe/Stockholm
    - Europe/Tallinn
    - Europe/Tirane
    - Europe/Vienna
    - Europe/Vilnius
    - Europe/Warsaw
    - Europe/Zurich
    - Indian/Chagos
    - Indian/Christmas
    - Indian/Cocos
    - Indian/Kerguelen
    - Indian/Mahe
    - Indian/Maldives
    - Indian/Mauritius
    - Indian/Reunion
    - Pacific/Apia
    - Pacific/Auckland
    - Pacific/Chuuk
    - Pacific/Easter
    - Pacific/Efate
    - Pacific/Enderbury
    - Pacific/Fakaofo
    - Pacific/Fiji
    - Pacific/Funafuti
    - Pacific/Galapagos
    - Pacific/Gambier
    - Pacific/Guadalcanal
    - Pacific/Guam
    - Pacific/Honolulu
    - Pacific/Kiritimati
    - Pacific/Kosrae
    - Pacific/Kwajalein
    - Pacific/Majuro
    - Pacific/Marquesas
    - Pacific/Nauru
    - Pacific/Niue
    - Pacific/Norfolk
    - Pacific/Noumea
    - Pacific/Pago_Pago
    - Pacific/Palau
    - Pacific/Pitcairn
    - Pacific/Pohnpei
    - Pacific/Port_Moresby
    - Pacific/Rarotonga
    - Pacific/Tahiti
    - Pacific/Tarawa
    - Pacific/Tongatapu
    - Pacific/Wake
    - Pacific/Wallis
  EOT
  type = map(object(
    {
      description = optional(string)
      enabled     = optional(bool)
      ntp_servers = optional(set(string))
      tags        = optional(list(map(string)))
      timezone    = optional(string)
    }
  ))
}


#_________________________________________________________________________
#
# NTP Policies
# GUI Location: Configure > Policies > Create Policy > NTP > Start
#_________________________________________________________________________

resource "intersight_ntp_policy" "ntp_policies" {
  depends_on = [
    local.org_moid,
    local.ucs_domain_policies
  ]
  for_each    = local.ntp_policies
  description = each.value.description != "" ? each.value.description : "${each.key} NTP Policy"
  enabled     = each.value.enabled
  name        = each.key
  ntp_servers = each.value.ntp_servers
  timezone    = each.value.timezone
  organization {
    moid        = local.org_moid
    object_type = "organization.Organization"
  }
  # dynamic "authenticated_ntp_servers" {
  #   for_each = each.value.authenticated_ntp_servers
  #   content {
  #     key_type      = "SHA1"
  #     object_type   = authenticated_ntp_servers.value.object_type
  #     server_name   = authenticated_ntp_servers.value.server_name
  #     sym_key_id    = authenticated_ntp_servers.value.sym_key_id
  #     sym_key_value = authenticated_ntp_servers.value.sym_key_value
  #   }
  # }
  dynamic "profiles" {
    for_each = { for k, v in local.ucs_domain_policies : k => v if local.ucs_domain_policies[k].ntp_policy == each.key }
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
