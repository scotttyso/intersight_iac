from classes import ezfunctions
from classes import validating
from classes.vmw import datacenter
from dotmap import DotMap
import json
import requests
import sys
import time
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Log levels 0 = None, 1 = Class only, 2 = Line
log_level = 2

# Global options for debugging
print_payload = False
print_response_always = True
print_response_on_fail = True

#
context = {}
kwargs = {}
pargs = DotMap()
#=====================================================
# Function - API Authentication
#=====================================================
def auth(pargs, section='', **kwargs):
    def api_auth(pargs, url, **kwargs):
        user = pargs.vcenter.user
        kwargs['Variable'] = 'vcenter_password'
        kwargs = ezfunctions.sensitive_var_value(**kwargs)
        password = kwargs['var_value']
        auth = ''
        while auth == '':
            try:
                auth = requests.post(f"{url}/rest/com/vmware/cis/session", auth = (user, password), verify=False)
            except requests.exceptions.ConnectionError as e:
                print("Connection error, pausing before retrying. Error: %s" % (e))
                time.sleep(5)
            except Exception as e:
                print("Method %s Failed. Exception: %s" % (section[:-5], e))
                sys.exit(1)
        if auth.ok:
            pargs.vcenter_session_id = auth.json()['value']
        else:
            raise ValueError("Unable to retrieve a session ID.")
        return pargs
    
    url = f"https://{pargs.vcenter.server}"
    if pargs.get('vcenter_session_id') and pargs.get('vcenter_auth_time'):
            if time.time() - pargs.vcenter_auth_time > 599:
                pargs = api_auth(pargs, url, **kwargs)
    else:
        pargs = api_auth(pargs, url, **kwargs)
        pargs.vcenter_auth_time = time.time()
    return pargs, url

#=====================================================
# Function - API - get
#=====================================================
def get(uri, pargs, section='', **kwargs):
    pargs, url = auth(pargs, **kwargs)
    r = ''
    while r == '':
        try:
            r = requests.get(f'{url}/api/{uri}', verify=False, headers={
                'vmware-api-session-id':pargs.vcenter_session_id
            })
            if print_response_always:
                print(f"     * get: {r.status_code} success with {uri}")
                #print(r.text)
            if r.status_code == 200 or r.status_code == 404:
                return r.json()
            else: validating.error_request_netapp('get', r.status_code, r.text, uri)
        except requests.exceptions.ConnectionError as e:
            print("Connection error, pausing before retrying. Error: %s" % (e))
            time.sleep(5)
        except Exception as e:
            print("Method %s Failed. Exception: %s" % (section[:-5], e))
            sys.exit(1)

#=====================================================
# Function - API - get
#=====================================================
def post(uri, pargs, payload, section='', **kwargs):
    pargs, url = auth(pargs, **kwargs)
    r = ''
    while r == '':
        try:
            r = requests.post(f'{url}/api/{uri}', data=payload, verify=False,
                              headers={'vmware-api-session-id':pargs.vcenter_session_id,
                              'Content-type':'application/json'})
            if print_response_always:
                print(f"     * get: {r.status_code} success with {uri}")
            if r.status_code == 201:
                return r.json()
            else: validating.error_request_netapp('post', r.status_code, r.text, uri)
        except requests.exceptions.ConnectionError as e:
            print("Connection error, pausing before retrying. Error: %s" % (e))
            time.sleep(5)
        except Exception as e:
            print("Method %s Failed. Exception: %s" % (section[:-5], e))
            sys.exit(1)



def setup_datacenters(vsphere_client):
    """Create datacenters for running vcenter samples"""
    # Find a Folder in which to put the Datacenters
    folder_summaries = datacenter.folder_list_datacenter_folder(context)
    folder = folder_summaries[0].folder
names = set(['NETAPP'])
#print(pp(context.vsphere_client.vcenter.Datacenter.list(Datacenter.FilterSpec(names=names))))
uri = 'host'
uri = 'vcenter/folder?type=DATACENTER'
dcfolder = get(uri, pargs, **kwargs)

# Either Create or Get DataCenter
uri = "vcenter/datacenter"
apiBody = {
    'folder': dcfolder[0]['folder'],
    'name': 'NETAPP'
}
payload = json.dumps(apiBody)
if print_payload: print(json.dumps(apiBody, indent=4))
jData = get(uri, pargs, **kwargs)
index = [i for i, d in enumerate(jData) if apiBody['name'] in d.values()]
if len(index) == 0:
    moid = post(uri, pargs, payload, **kwargs)
else: moid = jData[index[0]]['datacenter']
print(moid)
exit()

