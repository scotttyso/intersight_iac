#!/usr/bin/env python3
import json
import lib_ucs
import subprocess
import sys
from pathlib import Path

org = 'default'
policy_type = 'policies'
policy_file = 'bios_policies.auto.tfvars'
cmd = 'json2hcl -reverse < ./Intersight/%s/%s/%s' % (org, policy_type, policy_file)
p = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
jsonResponse = json.loads(p.stdout.decode('utf-8'))
print(jsonResponse)
