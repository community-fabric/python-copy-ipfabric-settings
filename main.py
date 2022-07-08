"""
This script will take the Settings and Attributes from one instance
of IP FABRIC (SOURCE) and store it in two files.
Afterwards, we load the files, and push that data into the TARGET
instance of IP FABRIC.
"""
import json
from os import path, makedirs

from config import check_dotenv
from ipf_settings import IPFSettings

CONFIG = check_dotenv()
SETTINGS = ['settings', 'sitename_attributes', 'intents', 'intent_groups', 'dashboard', 'custom_ports', 'oui']


def save_file(instance: str, client: IPFSettings):
    if not CONFIG["SAVE_TO_FILE"]:
        return False
    if not path.exists('backup_settings'):
        makedirs('backup_settings')
    for setting in SETTINGS:
        with open(f"backup_settings/{instance}_{setting}.json", "w") as json_file:
            json.dump(getattr(client, setting), json_file)
    return True


def main():
    """
    Main function
    """
    ipf_source = IPFSettings(
        base_url=CONFIG["IPF_URL_SOURCE"], token=CONFIG["IPF_TOKEN_SOURCE"],
        api_version=CONFIG["IPF_API_VERSION_SOURCE"], verify=CONFIG["IPF_VERIFY_SOURCE"]
    )
    save_file('source', ipf_source)

    ipf_target = IPFSettings(
        base_url=CONFIG["IPF_URL_TARGET"], token=CONFIG["IPF_TOKEN_TARGET"],
        api_version=CONFIG["IPF_API_VERSION_TARGET"], verify=CONFIG["IPF_VERIFY_TARGET"]
    )
    save_file('target', ipf_target)

    i = input('Do you wish to COPY source settings to Target? (y/n): ').strip().lower()
    if i and 'y' not in i[0]:
        if CONFIG['SAVE_TO_FILE']:
            exit("\n##INFO## Settings have been backed up to backup_settings directory!")
        else:
            exit("\n##INFO## Exiting before copying settings completed!")
    else:
        ipf_target.push_settings(ipf_source)
        exit("\n##INFO## Execution completed!")


if __name__ == "__main__":
    print("##INFO## STARTING API script to push settings...\n")
    main()
