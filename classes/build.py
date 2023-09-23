#=============================================================================
# Source Modules
#=============================================================================
def prRed(skk): print("\033[91m {}\033[00m" .format(skk))
import sys
try:
    from classes import ezfunctions, pcolor, validating, questions
    from copy import deepcopy
    from dotmap import DotMap
    from stringcase import snakecase
    import json, numpy, os, re, requests, time, urllib3
except ImportError as e:
    prRed(f'!!! ERROR !!!\n{e.__class__.__name__}')
    prRed(f" Module {e.name} is required to run this script")
    prRed(f" Install the module using the following: `pip install {e.name}`")
    sys.exit(1)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
#=======================================================
# Build IMM Policies
#=======================================================
class build_imm(object):
    def __init__(self, type):
        self.type = type

    #=================================================================
    # Function: Main Menu, Prompt User for Deployment Type
    #=================================================================
    def ezimm(self, kwargs):
        idata = deepcopy(DotMap(dict(pair for d in kwargs.ezdata[self.type].allOf for pair in d.properties.items())))
        if kwargs.build_type == 'Machine':
            if 'ip' in self.type: pop_list = ['assignment_order', 'description', 'name', 'reservations', 'tags']
            for p in pop_list: idata.pop(p)
        ptype = kwargs.ezdata[self.type].intersight_type

        kwargs.configure_more = True
        if kwargs.imm_dict[kwargs.org][ptype].get(self.type):
            kwargs = questions.existing_object(ptype, self.type, kwargs)
        if kwargs.configure_more == True:
            idict = DotMap()
            kwargs.loop_count = 0
            print('made it to here')
            if kwargs.build_type == 'Machine': config_object = True
            else: config_object = questions.prompt_user_to_configure(self.type, ptype, kwargs)
            while config_object == True:
                for k, v in idata.items():
                    if re.search('boolean|integer|string', v.type):
                        idict.update[k] = questions.prompt_user_item(k, v, kwargs)
                    elif v.type == 'array':
                        idict[k] = []
                        kwargs.inner_count = 0
                        if k in v.required: config_inner = True
                        else: config_inner = questions.prompt_user_for_sub_item(k, kwargs)
                        while config_inner == True:
                            edict = DotMap()
                            for a,b in v['items'].properties.items():
                                if re.search('boolean|integer|string', b.type):
                                    edict[a] = questions.prompt_user_item(a, b, kwargs)
                            accept = questions.prompt_user_to_accept(k, edict, kwargs)
                            additional = questions.promp_user_to_add(k, kwargs)
                            if accept == True: idict[k].append(edict)
                            if additional == False: config_inner = False
                            kwargs.inner_count += 1
                    elif v.type == 'object':
                        if k in v.required: config = True
                        else: config = questions.prompt_user_for_sub_item(k, kwargs)
                        while config == True:
                            edict = DotMap()
                            for a,b in v.properties.items():
                                if re.search('boolean|integer|string', b.type):
                                    edict[a] = questions.prompt_user_item(a, b, kwargs)
                            accept = questions.prompt_user_to_accept(k, edict, kwargs)
                            if accept == True: idict[k] = edict; config = False
                accept = questions.prompt_user_to_accept(self.type, idict, kwargs)
                additional = questions.promp_user_to_add(self.type, kwargs)
                if accept == True: idict[k] = edict
                if additional == False: config_object = False
                kwargs.loop_count += 1
        exit()
        return kwargs

