#!/usr/bin/env python3
import json
import numpy
import pkg_resources
import requests
import sys
import time
import urllib3
import validating
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Global options for debugging
print_payload = True
print_response_always = True
print_response_on_fail = True

# Log levels 0 = None, 1 = Class only, 2 = Line
log_level = 2

# Global path to main Template directory
template_path = pkg_resources.resource_filename('netapp', 'templates/')

# Exception Classes
class InsufficientArgs(Exception): pass
class ErrException(Exception): pass
class InvalidArg(Exception): pass
class LoginFailed(Exception): pass

# NetApp - Policies
# Class must be instantiated with Variables
class netapp(object):
    def __init__(self):
        self.type = type
    #==============================================
    # NetApp Cluster Creation
    #==============================================
    def cluster(self, polVars, **kwargs):
        uri = 'cluster'
        polVars = dict(
            contact = 'rich-lab@cisco.com',
            dns_domains = ['rich.ciscolabs.com'],
            license = dict(keys = []),
            location = 'Cisco Labs, Richfield, Ohio USA - Cabinet 142B',
            management_interfaces = [
                dict(
                    name = "lif1",
                    ip = dict(
                        address = "192.168.64.25"
                ))
            ],
            name = 'r142b-netapp01', # Cluster Name
            name_servers = ['10.101.128.15','10.101.128.16'],
            ntp_servers = ['10.101.128.15','10.101.128.16'],
            timezone = 'America/New_York'
        )
        payload = json.dumps(polVars)
        if print_payload: print(payload)

        uri = 'cluster'
        uri = 'network/ethernet/ports'
        #uri = 'network/ip/interfaces'
        #uri = 'network/fc/ports'
        #uri = 'network/http-proxy'
        #uri = 'svm/svms'
        #uri = 'name-services/dns'
        #uri = 'network/fc/logins'
        #uri = 'storage/luns'
        #uri = 'protocols/cifs/shares'
        status,json_data = get(uri, **kwargs)
        #--------------------------------------------------------------
        # Parse the JSON Data to see if the Variable Exists or Not.
        #--------------------------------------------------------------
        if status == 200:
            print(json.dumps(json_data, indent=4))
            eth_interfaces = []
            for i in json_data['records']:
                eth_interfaces.append(i['name'])
            eth_interfaces = numpy.unique(numpy.array(eth_interfaces))
            print(eth_interfaces)



# Function to get contents from URL
def auth(section='', **kwargs):
    url = f"https://{kwargs['storage_host']}"
    user = kwargs['storage_user']
    password = kwargs['storage_password']
    s = requests.Session()
    s.auth = (user, password)
    auth = ''
    while auth == '':
        try:
            auth = s.post(url, verify=False)
        except requests.exceptions.ConnectionError as e:
            print("Connection error, pausing before retrying. Error: %s" % (e))
            time.sleep(5)
        except Exception as e:
            print("Method %s Failed. Exception: %s" % (section[:-5], e))
            sys.exit(1)
    return s, url

# Function to get contents from URL
def get(uri, section='', **kwargs):
    s, url = auth(**kwargs)
    r = ''
    while r == '':
        try:
            r = s.get(f'{url}/api/{uri}', verify=False)
            status = r.status_code
            if print_response_always:
                print(status)
                #print(r.text)
            if status == 200 or status == 404:
                json_data = r.json()
                return status,json_data
            else: validating.error_request(r.status_code, r.text)
        except requests.exceptions.ConnectionError as e:
            print("Connection error, pausing before retrying. Error: %s" % (e))
            time.sleep(5)
        except Exception as e:
            print("Method %s Failed. Exception: %s" % (section[:-5], e))
            sys.exit(1)

# Function to PATCH Contents to URL
def patch(uri, payload, section='', **kwargs):
    s, url = auth(**kwargs)
    r = ''
    while r == '':
        try:
            r = s.patch(f'{url}/api/{uri}', data=payload, verify=False)
            # Use this for Troubleshooting
            if print_response_always:
                print(r.status_code)
                #print(r.text)
            if r.status_code != 200: validating.error_request(r.status_code, r.text)
            json_data = r.json()
            return json_data
        except requests.exceptions.ConnectionError as e:
            print("Connection error, pausing before retrying. Error: %s" % (e))
            time.sleep(5)
        except Exception as e:
            print("Method %s Failed. Exception: %s" % (section[:-5], e))
            sys.exit(1)

# Function to POST Contents to URL
def post(uri, payload, section='', **kwargs):
    s, url = auth(**kwargs)
    r = ''
    while r == '':
        try:
            r = s.post(f'{url}/api/{uri}', data=payload, verify=False)
            # Use this for Troubleshooting
            if print_response_always:
                print(r.status_code)
                print(r.text)
            if r.status_code != 201: validating.error_request(r.status_code, r.text)
            json_data = r.json()
            return json_data
        except requests.exceptions.ConnectionError as e:
            print("Connection error, pausing before retrying. Error: %s" % (e))
            time.sleep(5)
        except Exception as e:
            print("Method %s Failed. Exception: %s" % (section[:-5], e))
            sys.exit(1)

def main():
    kwargs = dict(
        storage_host = "64.100.14.23",
        storage_password = "N3ptune!",
        storage_user = "admin"
    )
    polVars = {}
    netapp().cluster(polVars, **kwargs)
    #print(json.dumps(kwargs))
    #sys.exit(1)

if __name__ == '__main__':
    main()
