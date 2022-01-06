import os
import datetime
import intersight
import stdiomask
from pathlib import Path

# This argument parser instance should be used within scripts where additional CLI arguments are required

def config_credentials(home, args):
    if args.api_key_id == None:
        key_loop = False
        while key_loop == False:
            question = stdiomask.getpass(f'API Key was not entered as a command line option.\n'\
                'Please enter the Version 2 Intersight API key to use: ')

            if len(question) == 74:
                args.api_key_id = question
                key_loop = True
            else:
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'  Error!! Invalid Value.  The API key length should be 74 characters.  Please Re-Enter.')
                print(f'\n-------------------------------------------------------------------------------------------\n')

    secret_loop = False
    while secret_loop == False:
        if '~' in args.api_key_file:
            secret_path = os.path.expanduser(args.api_key_file)
        else:
            secret_path = args.api_key_file
        if not os.path.isfile(secret_path):
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  Error!! api_key_file not found.')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            args.api_key_file = input(f'Please Enter the Path to the File containing the Intersight API Secret: ')
        else:
            secret_file = open(secret_path, 'r')
            if 'RSA PRIVATE KEY' in secret_file.read():
                secret_loop = True
            else:
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'  Error!! api_key_file does not seem to contain the Private Key.')
                print(f'\n-------------------------------------------------------------------------------------------\n')


    
    # HTTP signature scheme.
    if args.api_key_v3:
        signing_scheme = intersight.signing.SCHEME_HS2019
        signing_algorithm = intersight.signing.ALGORITHM_ECDSA_MODE_FIPS_186_3
    else:
        signing_scheme = intersight.signing.SCHEME_RSA_SHA256
        signing_algorithm = intersight.signing.ALGORITHM_RSASSA_PKCS1v15


    configuration = intersight.Configuration(
        host=args.url,
        signing_info=intersight.HttpSigningConfiguration(
            key_id=args.api_key_id,
            private_key_path=secret_path,
            signing_scheme=signing_scheme,
            signing_algorithm=signing_algorithm,
            hash_algorithm=intersight.signing.HASH_SHA256,
            signed_headers=[intersight.signing.HEADER_REQUEST_TARGET,
                            intersight.signing.HEADER_CREATED,
                            intersight.signing.HEADER_EXPIRES,
                            intersight.signing.HEADER_HOST,
                            intersight.signing.HEADER_DATE,
                            intersight.signing.HEADER_DIGEST,
                            'Content-Type',
                            'User-Agent'
                            ],
            signature_max_validity=datetime.timedelta(minutes=5)
        )
    )

    # if args.ignore_tls:
    configuration.verify_ssl = False

    configuration.proxy = os.getenv('https_proxy')
    api_client = intersight.ApiClient(configuration)
    api_client.set_default_header('referer', args.url)
    api_client.set_default_header('x-requested-with', 'XMLHttpRequest')
    api_client.set_default_header('Content-Type', 'application/json')

    return api_client


if __name__ == "__main__":
    config_credentials()
