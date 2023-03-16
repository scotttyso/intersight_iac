#!/bin/bash
# Intersight CURL
# Written by Brian Morrissey

if [ "$#" -lt 3 ]; then
    echo -e "Intersight CURL Example\n"
    echo -e "Usage: ./script.sh 'API Key ID' 'API Secretkey Filename' 'HTTP method [GET/POST/DELETE]' 'API Endpoint' 'Payload [Required only for POST]\n"
    echo -e "Example GET: ./script.sh '1111/2222/3333' 'SecretKey.txt' 'GET' '/api/v1/compute/PhysicalSummaries?\$top=1&\$select=Serial'\n"
    echo -e "Example DELETE: ./script.sh '1111/2222/3333' 'SecretKey.txt' 'DELETE' '/api/v1/vnic/LanConnectivityPolicies/60bfd0964fa6a1d629e66eb6'\n"
    echo -e "Example POST: ./script.sh '1111/2222/3333' 'SecretKey.txt' 'POST' '/api/v1/ntp/Policies' '{"Organization":{"ObjectType":"organization.Organization","Moid":"5ddea34a6972652d3353b462"},"Name":"myNtpPolicy","Enabled":true,"NtpServers":["1.1.1.1"]}'"
    echo -e "Example PATCH: ./script.sh '1111/2222/3333' 'SecretKey.txt' 'PATCH' '/api/v1/ntp/Policies/{Moid}' '{"NtpServers":["1.1.1.1", "1.1.1.2"]}'"
    exit 2
fi
hostName=$1
apiKey="$TF_VAR_apikey"
apiSecretKey="temp_key.key"
method=${2^^}
uri=$3
payload="{\"Action\":\"Deploy\"}"
printenv TF_VAR_secretkey > temp_key.key

apiTime="date: "$(date -u '+%a, %d %b %Y %T %Z')

#SHA256 digest of HTTP payload
apibodyDigest="digest: SHA-256="$(printf ''$payload'' | openssl dgst -sha256 -binary | base64)

#SHA256 digest of headers signed by private key file, header info must be in lower case for the digest
apiSignature=$(
printf "(request-target): %s %s
%s
%s
host: %s" "${method,,}" "${uri,,}" "$apiTime" "$apibodyDigest" "$hostName" | openssl dgst -sha256 -binary -sign "temp_key.key" | base64 -w 0)


if [ $method = "POST" ] || [ $method = "PATCH" ]
then
curl -X $method "https://"$hostName$uri \
-H 'Accept: "application/json"' \
-H 'Content-Type: application/json' \
-H 'Host: '$hostName -H "$apiTime" -H "$apibodyDigest" \
-H 'Authorization: Signature keyId="'"$apiKey"'",algorithm="rsa-sha256",headers="(request-target) date digest host",signature="'"$apiSignature"'"' \
-d $payload
elif [ $method = "GET" ] || [ $method = "DELETE" ]
then
curl -X $method "https://"$hostName$uri \
-H 'Accept: "application/json"' \
-H 'Host: '$hostName -H "$apiTime" -H "$apibodyDigest" \
-H 'Authorization: Signature keyId="'"$apiKey"'",algorithm="rsa-sha256",headers="(request-target) date digest host",signature="'"$apiSignature"'"'
fi

rm -rf temp_key.key