from copy import deepcopy
import ezfunctions
import lansan
import policies
import pools
import re
import textwrap
import yaml

class MyDumper(yaml.Dumper):
    def increase_indent(self, flow=False, indentless=False):
        return super(MyDumper, self).increase_indent(flow, False)

class profiles(object):
    def __init__(self, name_prefix, org, type):
        self.name_prefix = name_prefix
        self.org = org
        self.type = type

    #==============================================
    # UCS Chassis Profile Module
    #==============================================
    def chassis(self, **kwargs):
        baseRepo       = kwargs['args'].dir
        configure_loop = False
        ezData         = kwargs['ezData']
        org            = self.org
        path_sep       = kwargs['path_sep']
        policy_type    = 'UCS Chassis Profile'
        yaml_file      = 'chassis'
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  This will create {policy_type}(s).  The Wizard will will first ask for the policies to')
            print(f'  assign.  Then you can assign multiple Names/Serials to the same Profile Policy.')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - {baseRepo}{path_sep}{org}{path_sep}{self.type}{path_sep}{yaml_file}.yaml')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure a {policy_type}?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                policy_loop = False
                while policy_loop == False:
                    #==============================================
                    # Prompt User for Policies to Assign
                    #==============================================
                    polVars = {}
                    kwargs['name'] = 'Chassis Profiles'
                    kwargs['allow_opt_out'] = True
                    policy_list = [
                        'policies.imc_access.imc_access_policy',
                        'policies.power.power_policy',
                        'policies.snmp.snmp_policy',
                        'policies.thermal.thermal_policy'
                    ]
                    for policy in policy_list:
                        kwargs['policy'] = policy
                        x = policy.split('.')[2]
                        kwargs = policy_select_loop(self, **kwargs)
                        if kwargs.get(x): polVars.update({f'{x}':kwargs[x]})
                    #==============================================
                    # Prompt User for Domain Profile
                    #==============================================
                    kwargs['allow_opt_out'] = False
                    kwargs['policy'] = 'profiles.domain.domain_profile'
                    kwargs = policy_select_loop(self, **kwargs)
                    #==============================================
                    # Prompt User for Action
                    #==============================================
                    kwargs['multi_select'] = False
                    jsonVars = ezData['ezimm']['allOf'][1]['properties']['profiles']
                    kwargs['jData'] = deepcopy(jsonVars['action'])
                    #kwargs['jData']['varType'] = 'Action'
                    #polVars['action'] = ezfunctions.variablesFromAPI(**kwargs)
                    #==============================================
                    # Assign Chassis Names to Profile
                    #==============================================
                    polVars['targets']    = []
                    domain_name           = kwargs['domain_profile']
                    inner_loop_count      = 1
                    sub_loop              = False
                    kwargs['device_type'] = 'Chassis'
                    kwargs['yaml_file']   = yaml_file
                    while sub_loop == False:
                        #==============================================
                        # Prompt User for Chassis Name
                        #==============================================
                        name        = ezfunctions.policy_name(f'{domain_name}-{inner_loop_count}', policy_type)
                        #==============================================
                        # Determine if Description Should be Configured
                        #==============================================
                        kwargs['jData'] = deepcopy({})
                        kwargs['jData']['default']      = True
                        kwargs['jData']['description']  = 'Chassis Description'
                        kwargs['jData']['varInput']     = f'Do you want to Assign a Description to the Chassis?'
                        kwargs['jData']['varName']      = 'Chassis Description'
                        question = ezfunctions.varBoolLoop(**kwargs)
                        if question == True: description = ezfunctions.policy_descr(name, policy_type)
                        else: description = ''
                        #==============================================
                        # Prompt User for Chassis Serial
                        #==============================================
                        serial      = ezfunctions.ucs_serial(**kwargs)
                        cprofile = {'name':name}
                        if not description == '':
                            cprofile.update({'description':description})
                        if not serial == '':
                            cprofile.update({'serial_number':serial})
                        #==============================================
                        # Print Policy and Prompt User to Accept
                        #==============================================
                        print(f'\n{"-"*91}\n')
                        print(textwrap.indent(yaml.dump(cprofile, Dumper=MyDumper, default_flow_style=False
                        ), ' '*4, predicate=None))
                        print(f'{"-"*91}\n')
                        valid_confirm = False
                        while valid_confirm == False:
                            confirm_config = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
                            if confirm_config == 'Y' or confirm_config == '':
                                pol_type = 'Chassis Name/Description/Serial'
                                polVars['targets'].append(cprofile)
                                #==============================================
                                # Create Additional Policy or Exit Loop
                                #==============================================
                                valid_exit = False
                                while valid_exit == False:
                                    loop_exit, sub_loop = ezfunctions.exit_default(pol_type, 'N')
                                    if loop_exit == False: inner_loop_count += 1; valid_confirm = True; valid_exit = True
                                    elif loop_exit == True: valid_confirm = True; valid_exit = True
                            elif confirm_config == 'N':
                                ezfunctions.message_starting_over(pol_type)
                                valid_confirm = True
                            else: ezfunctions.message_invalid_y_or_n('short')
                    
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(textwrap.indent(yaml.dump(polVars, Dumper=MyDumper, default_flow_style=False), ' '*4, predicate=None))
                    print(f'-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
                        if confirm_policy == 'Y' or confirm_policy == '':
                            #==============================================
                            # Add Policy Variables to immDict
                            #==============================================
                            kwargs['class_path'] = 'profiles,chassis'
                            kwargs = ezfunctions.ez_append(polVars, **kwargs)
                            #==============================================
                            # Create Additional Policy or Exit Loop
                            #==============================================
                            configure_loop, policy_loop = ezfunctions.exit_default(policy_type, 'N')
                            valid_confirm = True
                        elif confirm_policy == 'N':
                            ezfunctions.message_starting_over(policy_type)
                            valid_confirm = True
                        else: ezfunctions.message_invalid_y_or_n('short')
            elif configure == 'N': configure_loop = True
            else: ezfunctions.message_invalid_y_or_n('long')
        # Return kwargs
        return kwargs

    #==============================================
    # UCS Domain Profile Module
    #==============================================
    def domain(self, **kwargs):
        baseRepo       = kwargs['args'].dir
        configure_loop = False
        domain_prefix  = kwargs['domain_prefix']
        ezData         = kwargs['ezData']
        name_suffix    = 'ucs'
        org            = self.org
        path_sep       = kwargs['path_sep']
        policy_type    = 'UCS Domain Profile'
        yaml_file      = 'domain'
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  This will create {policy_type}(s).')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - {baseRepo}{path_sep}{org}{path_sep}{self.type}{path_sep}{yaml_file}.yaml')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure a {policy_type}?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                policy_loop = False
                while policy_loop == False:
                    polVars = {}
                    if not domain_prefix == '': name = '%s' % (domain_prefix, name_suffix)
                    else: name = f'{name_suffix}'

                    polVars['name']        = ezfunctions.policy_name(name, policy_type)
                    polVars['description'] = ezfunctions.policy_descr(polVars['name'], policy_type)
                    name = polVars['name']
                    kwargs['name'] = name
                    #==============================================
                    # Prompt User for Action
                    #==============================================
                    kwargs['multi_select'] = False
                    jsonVars = ezData['ezimm']['allOf'][1]['properties']['profiles']
                    kwargs['jData'] = deepcopy(jsonVars['action'])
                    #kwargs['jData']['varType'] = 'Action'
                    #polVars['action'] = ezfunctions.variablesFromAPI(**kwargs)
                    #==============================================
                    # Prompt User for Serials
                    #==============================================
                    polVars['serial_numbers'] = ezfunctions.ucs_domain_serials(**kwargs)

                    policy_list = [
                        'policies.network_connectivity.network_connectivity_policy',
                        'policies.ntp.ntp_policy',
                        'policies.snmp.snmp_policy',
                        'policies.switch_control.switch_control_policy',
                        'policies.syslog.syslog_policy',
                        'policies.system_qos.system_qos_policy'
                    ]
                    kwargs['allow_opt_out'] = True
                    for policy in policy_list:
                        kwargs['policy'] = policy
                        kwargs = policy_select_loop(self, **kwargs)
                        if not kwargs[f"{policy.split('.')[2]}"] == '':
                            polVars.update({f"{policy.split('.')[2]}":kwargs[f"{policy.split('.')[2]}"]})
                    polVars.update({'port_policies':[f'{name}-a', f'{name}-b']})
                    policy_list = [
                        'policies.vlan.vlan_policy',
                        'policies.vsan.vsan_policy'
                    ]
                    kwargs['allow_opt_out'] = False
                    for policy in policy_list:
                        ptype = policy.split('.')[1] + '_policies'
                        polVars[f'{ptype}'] = []
                        for fab in ['Fabric A', 'Fabric B']:
                            kwargs['policy'] = policy
                            policy_description = ezfunctions.mod_pol_description(policy.split('.')[2])
                            kwargs['optional_message'] = f'  !!! Select the {policy_description} for {fab} !!!'
                            kwargs = policy_select_loop(self, **kwargs)
                            polVars[f'{ptype}'].append(kwargs[f"{policy.split('.')[2]}"])
                        polVars[f'{ptype}'] = [*set(polVars[f'{ptype}'])]
                    kwargs.pop('optional_message')
                    #==============================================
                    # Print Policy and Prompt User to Accept
                    #==============================================
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(textwrap.indent(yaml.dump(polVars, Dumper=MyDumper, default_flow_style=False), ' '*4, predicate=None))
                    print(f'-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                        if confirm_policy == 'Y' or confirm_policy == '':
                            #==============================================
                            # Add Policy Variables to immDict
                            #==============================================
                            kwargs['class_path'] = 'profiles,domain'
                            kwargs = ezfunctions.ez_append(polVars, **kwargs)
                            #==============================================
                            # Create Additional Policy or Exit Loop
                            #==============================================
                            configure_loop, policy_loop = ezfunctions.exit_default(policy_type, 'N')
                            valid_confirm = True
                        elif confirm_policy == 'N':
                            ezfunctions.message_starting_over(policy_type)
                            valid_confirm = True
                        else: ezfunctions.message_invalid_y_or_n('short')
            elif configure == 'N': configure_loop = True
            else: ezfunctions.message_invalid_y_or_n('long')
        # Return kwargs
        return kwargs

    #==============================================
    # UCS Server Profile Module
    #==============================================
    def server(self, **kwargs):
        baseRepo        = kwargs['args'].dir
        configure_loop  = False
        ezData          = kwargs['ezData']
        jsonData        = kwargs['jsonData']
        name_prefix     = self.name_prefix
        name_suffix     = 'server'
        org             = self.org
        path_sep        = kwargs['path_sep']
        policy_type     = 'UCS Server Profile'
        target_platform = kwargs['target_platform']
        yaml_file       = 'servers'
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  This will create {policy_type}(s).  The Wizard will will first ask for the policies to')
            print(f'  assign.  Then you can assign multiple Names/Serials to the same Profile Policy.')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - {baseRepo}{path_sep}{org}{path_sep}{self.type}{path_sep}{yaml_file}.yaml')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            policy_loop = False
            while policy_loop == False:
                polVars = {}
                if target_platform == 'Standalone': polVars['target_platform'] = target_platform
                #==============================================
                # Get API Data
                #==============================================
                kwargs['allow_opt_out'] = False
                kwargs['multi_select'] = False
                jsonVars = ezData['ezimm']['allOf'][1]['properties']['profiles']
                kwargs['jData'] = deepcopy(jsonVars['action'])
                #kwargs['jData']['varType'] = 'Action'
                #polVars['action'] = ezfunctions.variablesFromAPI(**kwargs)
                jsonVars = jsonData['server.Profile']['allOf'][1]['properties']
                #==============================================
                # Prompt User for Server Assignment Mode
                #==============================================
                kwargs['jData'] = deepcopy(jsonVars['ServerAssignmentMode'])
                kwargs['jData']['default'] = 'Static'
                kwargs['jData']['varType'] = 'Server Assignment Mode'
                server_assignment_mode = ezfunctions.variablesFromAPI(**kwargs)
                #==============================================
                # Prompt User for Resource Pool if Mode is Pool
                #==============================================
                kwargs['name'] = 'Server Profiles'
                if server_assignment_mode == 'Pool':
                   kwargs['policy'] = 'pools.resource.resource_pool'
                   kwargs = policy_select_loop(self, **kwargs)
                   polVars.update({'resource_pool':kwargs['resource_pool']})
                #==============================================
                # Prompt User for Template Association
                #==============================================
                kwargs['jData'] = deepcopy({})
                kwargs['jData']['default']      = True
                kwargs['jData']['description']  = 'UCS Server Profile Template Association'
                kwargs['jData']['varInput']     = f'Do you want to Associate the profile(s) to a UCS Server Profile Template?'
                kwargs['jData']['varName']      = 'Server Profile Template'
                server_template = ezfunctions.varBoolLoop(**kwargs)
                if server_template == True:
                    kwargs['policy'] = 'templates.server.ucs_server_profile_template'
                    kwargs = policy_select_loop(self, **kwargs)
                    polVars.update({'ucs_server_profile_template':kwargs['ucs_server_profile_template']})
                else:
                    #==============================================
                    # Prompt User with Policies to Select
                    #==============================================
                    policy_list = [
                        #==============================================
                        # Compute Configuration
                        #==============================================
                        'policies.bios.bios_policy',
                        'policies.boot_order.boot_order_policy',
                        'policies.virtual_media.virtual_media_policy',
                        #==============================================
                        # Management Configuration
                        #==============================================
                        'policies.ipmi_over_lan.ipmi_over_lan_policy',
                        'policies.local_user.local_user_policy',
                        'policies.serial_over_lan.serial_over_lan_policy',
                        'policies.snmp.snmp_policy',
                        'policies.syslog.syslog_policy',
                        'policies.virtual_kvm.virtual_kvm_policy',
                        #==============================================
                        # Storage Configuration
                        #==============================================
                        'policies.sd_card.sd_card_policy',
                        'policies.storage.storage_policy',
                        #==============================================
                        # Network Configuration
                        #==============================================
                        'policies.lan_connectivity.lan_connectivity_policy',
                        'policies.san_connectivity.san_connectivity_policy',
                    ]
                    if target_platform == 'FIAttached':
                        policy_list.extend([
                            #==============================================
                            # Compute Configuration
                            #==============================================
                            'pools.uuid.uuid_pool',
                            'policies.certificate_management.certificate_management_policy',
                            'policies.power.power_policy',
                            #==============================================
                            # Management Configuration
                            #==============================================
                            'policies.imc_access.imc_access_policy',
                        ])
                    elif target_platform == 'Standalone':
                        policy_list.extend([
                            #==============================================
                            # Compute Configuration
                            #==============================================
                            'policies.persistent_memory.persistent_memory_policy',
                            #==============================================
                            # Management Configuration
                            #==============================================
                            'policies.device_connector.device_connector_policy',
                            'policies.ldap.ldap_policy',
                            'policies.network_connectivity.network_connectivity_policy',
                            'policies.ntp.ntp_policy',
                            'policies.smtp.smtp_policy',
                            'policies.ssh.ssh_policy',
                            #==============================================
                            # Network Configuration
                            #==============================================
                            'policies.adapter_configuration.adapter_configuration_policy',
                        ])
                    policy_list.sort()
                    kwargs['allow_opt_out'] = True
                    for policy in policy_list:
                        kwargs['policy'] = policy
                        kwargs = policy_select_loop(self, **kwargs)
                        ptype = policy.split('.')[2]
                        if not kwargs[ptype] == '':
                            polVars.update({f'{ptype}':kwargs[ptype]})
                #==============================================
                # Prompt User for Server Name Prefix
                #==============================================
                kwargs['jData'] = deepcopy({})
                kwargs['jData']['default']      = True
                kwargs['jData']['description']  = 'Server Name Prefix'
                kwargs['jData']['varInput']     = f'Do you want to use a Server Name Prefix for the Server Names?'
                kwargs['jData']['varName']      = 'Server Name Prefix'
                question = ezfunctions.varBoolLoop(**kwargs)
                if question == True:
                    if not name_prefix == '': name = f'{name_prefix}-{name_suffix}'
                    else: name = f'{name_suffix}'
                    server_prefix = ezfunctions.policy_name(name, policy_type)
                else: server_prefix = ''
                #==============================================
                # Assign Server Names to Profile
                #==============================================
                polVars['targets']    = []
                inner_loop_count      = 1
                sub_loop              = False
                kwargs['device_type'] = 'Server'
                kwargs['yaml_file']   = yaml_file
                while sub_loop == False:
                    #==============================================
                    # Prompt User for Server Name
                    #==============================================
                    if not server_prefix == '':
                        name    = ezfunctions.policy_name(f'{server_prefix}-{inner_loop_count}', policy_type)
                    else: name  = ezfunctions.policy_name(f'{name_prefix}-{inner_loop_count}', policy_type)
                    #==============================================
                    # Determine if Description Should be Configured
                    #==============================================
                    kwargs['jData'] = deepcopy({})
                    kwargs['jData']['default']      = True
                    kwargs['jData']['description']  = 'Server Description'
                    kwargs['jData']['varInput']     = f'Do you want to Assign a Description to the Server?'
                    kwargs['jData']['varName']      = 'Server Description'
                    question = ezfunctions.varBoolLoop(**kwargs)
                    if question == True: description = ezfunctions.policy_descr(name, policy_type)
                    else: description = ''
                    #==============================================
                    # Prompt User for Server Serial
                    #==============================================
                    serial      = ezfunctions.ucs_serial(**kwargs)
                    sprofile = {'name':name}
                    if not description == '':
                        sprofile.update({'description':description})
                    if not serial == '':
                        sprofile.update({'serial_number':serial})
                    #==============================================
                    # Print Policy and Prompt User to Accept
                    #==============================================
                    print(f'\n{"-"*91}\n')
                    print(textwrap.indent(yaml.dump(sprofile, Dumper=MyDumper, default_flow_style=False
                    ), ' '*4, predicate=None))
                    print(f'{"-"*91}\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_config = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
                        if confirm_config == 'Y' or confirm_config == '':
                            pol_type = 'Server Name/Description/Serial'
                            polVars['targets'].append(sprofile)
                            #==============================================
                            # Create Additional Policy or Exit Loop
                            #==============================================
                            valid_exit = False
                            while valid_exit == False:
                                loop_exit, sub_loop = ezfunctions.exit_default(pol_type, 'N')
                                if loop_exit == False: inner_loop_count += 1; valid_confirm = True; valid_exit = True
                                elif loop_exit == True: valid_confirm = True; valid_exit = True
                        elif confirm_config == 'N':
                            ezfunctions.message_starting_over(pol_type)
                            valid_confirm = True
                        else: ezfunctions.message_invalid_y_or_n('short')
                #==============================================
                # Print Policy and Prompt User to Accept
                #==============================================
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(textwrap.indent(yaml.dump(polVars, Dumper=MyDumper, default_flow_style=False), ' '*4, predicate=None))
                print(f'-------------------------------------------------------------------------------------------\n')
                valid_confirm = False
                while valid_confirm == False:
                    confirm_policy = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                    if confirm_policy == 'Y' or confirm_policy == '':
                        #==============================================
                        # Add Policy Variables to immDict
                        #==============================================
                        kwargs['class_path'] = 'profiles,server'
                        kwargs = ezfunctions.ez_append(polVars, **kwargs)
                        #==============================================
                        # Create Additional Policy or Exit Loop
                        #==============================================
                        configure_loop, policy_loop = ezfunctions.exit_default(policy_type, 'N')
                        valid_confirm = True
                    elif confirm_policy == 'N':
                        ezfunctions.message_starting_over(policy_type)
                        valid_confirm = True
                    else: ezfunctions.message_invalid_y_or_n('short')
        # Return kwargs
        return kwargs

    #==============================================
    # UCS Server Profile Template Module
    #==============================================
    def server_profile_templates(self, **kwargs):
        baseRepo        = kwargs['args'].dir
        configure_loop  = False
        name_prefix     = self.name_prefix
        name_suffix     = 'template'
        org             = self.org
        path_sep        = kwargs['path_sep']
        policy_type     = 'UCS Server Profile Template'
        target_platform = kwargs['target_platform']
        yaml_file       = 'servers'
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  This will create {policy_type}(s).')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - {baseRepo}{path_sep}{org}{path_sep}templates{path_sep}{yaml_file}.yaml')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure a {policy_type}?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                policy_loop = False
                while policy_loop == False:
                    polVars = {}
                    if target_platform == 'Standalone': polVars['target_platform'] = target_platform
                    #==============================================
                    # Prompt User for Template Profile
                    #==============================================
                    if not name_prefix == '': name = f'{name_prefix}-{name_suffix}'
                    else: name = f'{name_suffix}'
                    polVars['name']        = ezfunctions.policy_name(name, policy_type)
                    polVars['description'] = ezfunctions.policy_descr(polVars['name'], policy_type)
                    kwargs['name']         = polVars['name']
                    policy_list = [
                        #==============================================
                        # Compute Configuration
                        #==============================================
                        'policies.bios.bios_policy',
                        'policies.boot_order.boot_order_policy',
                        'policies.virtual_media.virtual_media_policy',
                        #==============================================
                        # Management Configuration
                        #==============================================
                        'policies.ipmi_over_lan.ipmi_over_lan_policy',
                        'policies.local_user.local_user_policy',
                        'policies.serial_over_lan.serial_over_lan_policy',
                        'policies.snmp.snmp_policy',
                        'policies.syslog.syslog_policy',
                        'policies.virtual_kvm.virtual_kvm_policy',
                        #==============================================
                        # Storage Configuration
                        #==============================================
                        'policies.sd_card.sd_card_policy',
                        'policies.storage.storage_policy',
                        #==============================================
                        # Network Configuration
                        #==============================================
                        'policies.lan_connectivity.lan_connectivity_policy',
                        'policies.san_connectivity.san_connectivity_policy',
                    ]
                    if target_platform == 'FIAttached':
                        policy_list.extend([
                            #==============================================
                            # Compute Configuration
                            #==============================================
                            'pools.uuid.uuid_pool',
                            'policies.certificate_management.certificate_management_policy',
                            'policies.power.power_policy',
                            #==============================================
                            # Management Configuration
                            #==============================================
                            'policies.imc_access.imc_access_policy',
                        ])
                    elif target_platform == 'Standalone':
                        policy_list.extend([
                            #==============================================
                            # Compute Configuration
                            #==============================================
                            'policies.persistent_memory.persistent_memory_policy',
                            #==============================================
                            # Management Configuration
                            #==============================================
                            'policies.device_connector.device_connector_policy',
                            'policies.ldap.ldap_policy',
                            'policies.network_connectivity.network_connectivity_policy',
                            'policies.ntp.ntp_policy',
                            'policies.smtp.smtp_policy',
                            'policies.ssh.ssh_policy',
                            #==============================================
                            # Network Configuration
                            #==============================================
                            'policies.adapter_configuration.adapter_configuration_policy',
                        ])
                    policy_list.sort()
                    kwargs['allow_opt_out'] = True
                    for policy in policy_list:
                        kwargs['policy'] = policy
                        kwargs = policy_select_loop(self, **kwargs)
                        ptype = policy.split('.')[2]
                        if kwargs.get(ptype):
                            polVars.update({f'{ptype}':kwargs[ptype]})
                    #==============================================
                    # Print Policy and Prompt User to Accept
                    #==============================================
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(textwrap.indent(yaml.dump(polVars, Dumper=MyDumper, default_flow_style=False), ' '*4, predicate=None))
                    print(f'-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                        if confirm_policy == 'Y' or confirm_policy == '':
                            #==============================================
                            # Add Policy Variables to immDict
                            #==============================================
                            kwargs['class_path'] = 'templates,server'
                            kwargs = ezfunctions.ez_append(polVars, **kwargs)
                            #==============================================
                            # Create Additional Policy or Exit Loop
                            #==============================================
                            configure_loop, policy_loop = ezfunctions.exit_default(policy_type, 'N')
                            valid_confirm = True
                        elif confirm_policy == 'N':
                            ezfunctions.message_starting_over(policy_type)
                            valid_confirm = True
                        else: ezfunctions.message_invalid_y_or_n('short')
            elif configure == 'N': configure_loop = True
            else: ezfunctions.message_invalid_y_or_n('long')
        # Return kwargs
        return kwargs

def policy_select_loop(self, **kwargs):
    ezData      = kwargs['ezData']
    policy      = kwargs['policy']
    name        = kwargs['name']
    name_prefix = self.name_prefix
    org         = kwargs['org']
    loop_valid  = False
    while loop_valid == False:
        create_policy = True
        kwargs['inner_policy'] = policy.split('.')[1]
        kwargs['inner_type']   = policy.split('.')[0]
        kwargs['inner_var']    = policy.split('.')[2]
        inner_policy = kwargs['inner_policy']
        inner_type   = kwargs['inner_type']
        inner_var    = kwargs['inner_var']
        policy_description = ezfunctions.mod_pol_description(inner_var)
        kwargs = ezfunctions.policies_parse(inner_type, inner_policy, **kwargs)
        if not len(kwargs['policies'][kwargs['inner_policy']]) > 0:
            valid = False
            while valid == False:
                policy_description = ezfunctions.mod_pol_description(inner_var)
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'   There was no {policy_description} found.')
                print(f'\n-------------------------------------------------------------------------------------------\n')
                if kwargs['allow_opt_out'] == True:
                    Question = input(f'Do you want to create a(n) {policy_description}?  Enter "Y" or "N" [Y]: ')
                    if Question == '' or Question == 'Y': create_policy = True; valid = True
                    elif Question == 'N': create_policy = False; valid = True; return kwargs
                else: create_policy = True; valid = True
        else:
            kwargs['name'] = name
            kwargs = ezfunctions.choose_policy(inner_policy, **kwargs)
            if kwargs['policy'] == 'create_policy': create_policy = True
            elif kwargs['policy'] == '' and kwargs['allow_opt_out'] == True:
                loop_valid = True
                create_policy = False
                kwargs[kwargs['inner_var']] = ''
                return kwargs
            elif not kwargs['policy'] == '':
                loop_valid = True
                create_policy = False
                kwargs[kwargs['inner_var']] = kwargs['policy']
                return kwargs

        # Simple Loop to show name_prefix in Use
        ncount = 0
        if ncount == 5: print(name_prefix)
        
        # Create Policy if Option was Selected
        if create_policy == True:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  Starting module to create {policy_description} in Organization {org}')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            list_lansan   = ezData['ezimm']['allOf'][1]['properties']['list_lansan']['enum']
            list_policies = ezData['ezimm']['allOf'][1]['properties']['list_policies']['enum']
            list_profiles = ezData['ezimm']['allOf'][1]['properties']['list_profiles']['enum']
            if inner_policy in list_lansan:
                kwargs = eval(f"lan.policies(name_prefix, org, inner_type).{inner_policy}(**kwargs)")
            elif re.search('pools$', inner_policy):
                kwargs = eval(f"pools.pools(name_prefix, org, inner_type).{inner_policy}(**kwargs)")
            elif inner_policy in list_policies:
                kwargs = eval(f"policies.policies(name_prefix, org, inner_type).{inner_policy}(**kwargs)")
            elif inner_policy in list_profiles:
                kwargs = eval(f"profiles(name_prefix, org, inner_type).{inner_policy}(**kwargs)")
    # Return kwargs
    return kwargs