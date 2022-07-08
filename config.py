from distutils.util import strtobool
from os import path
from collections import OrderedDict

from dotenv import dotenv_values

CONFIG_DEFAULT = OrderedDict([
    ('SAVE_TO_FILE', True),
    ('IPF_URL_SOURCE', None),
    ('IPF_TOKEN_SOURCE', None),
    ('IPF_API_VERSION_SOURCE', 'v1'),
    ('IPF_VERIFY_SOURCE', True),
    ('IPF_URL_TARGET', None),
    ('IPF_TOKEN_TARGET', None),
    ('IPF_API_VERSION_TARGET', 'v1'),
    ('IPF_VERIFY_TARGET', True),
])


def env_bool(k, v):
    if 'SAVE_TO_FILE' in k.upper() or 'IPF_VERIFY' in k.upper():
        return v if isinstance(v, bool) else bool(strtobool(v))
    else:
        return v


def create_env(config: dict = None):
    config = config if config else dict()
    for k, v in CONFIG_DEFAULT.items():
        print()
        if 'SAVE_TO_FILE' in k.upper() or 'IPF_VERIFY' in k.upper():
            print('Please enter True or False (t/f).')
        elif 'IPF_API_VERSION' in k.upper():
            print('If IP Fabric version is v4.X set to v1; else if IPF version is v5.X enter "v5".')

        if k in config:
            i = input(f'Enter value for {k} (Press enter to use current value "{config[k]}"): ').strip() or config[k]
        elif CONFIG_DEFAULT[k]:
            i = input(f'Enter value for {k} (Press enter to use default value "{CONFIG_DEFAULT[k]}"): ').strip() \
                or CONFIG_DEFAULT[k]
        else:
            i = input(f'Enter value for {k}: ').strip()
        config[k] = env_bool(k, i)
    with open('.env', 'w') as f:
        for k, v in config.items():
            f.write(f"{k}={v}\n")
    return config


def check_env(config):
    required = [k for k, v in CONFIG_DEFAULT.items() if not v]
    default = [k for k, v in CONFIG_DEFAULT.items() if v]
    if not all(r in config for r in required):
        print(f"All required environment variables are not present.\rRequired: {required}")
        config = check_env(create_env(config))
    for d in default:
        if d not in config:
            print(f"Using default value for {d} of {CONFIG_DEFAULT[d]}")
            config[d] = CONFIG_DEFAULT[d]
    return config


def check_dotenv():
    if path.exists('1.env'):
        config = dict()
        for k, v in dotenv_values(".env").items():
            config[k.upper()] = env_bool(k, v)
        config = check_env(config)
        print('Using .env Configuration of:\n')
        print(f"SAVE_TO_FILE:\t{config['SAVE_TO_FILE']}\n")
        [print(f"{k}:\t{v if 'TOKEN' not in k else 'XXXXXXXXXXXXXX'}") for k, v in config.items() if 'SOURCE' in k]
        print()
        [print(f"{k}:\t{v if 'TOKEN' not in k else 'XXXXXXXXXXXXXX'}") for k, v in config.items() if 'TARGET' in k]

        i = input('\nDo you accept the current configuration (y/n): ').strip().lower()
        if i and 'y' not in i[0]:
            config = create_env(config)
            check_dotenv()

    else:
        print('Creating .env file with configuration variables.')
        config = create_env()
        check_dotenv()
    print()
    return config