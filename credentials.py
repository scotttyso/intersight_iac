import os
import datetime
import intersight
import stdiomask
from pathlib import Path

# This argument parser instance should be used within scripts where additional CLI arguments are required

def config_credentials(home, args):
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
            private_key_path=args.api_key_file,
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
