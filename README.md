# Copy IP Fabric Settings to another instance

## Install
`pip install --pre -r requirements.txt`

## Notes
Initial testing was performed copying v4.4.3 -> pre-released v5.0.0 however more tests will need to be done.
Also this is using ipfabric==5.0.0b2 and will be updated once 5.0.0 is released and tested.

## Setup
You can manually set up the environment variables by copy `sample.env` to `.env` and editting the file.

Skipping this step will walk you through a guided setup which will ensure the file is correctly configured.

**Note: IPF_API_VERSION_SOURCE must be set to `v1` if using IP Fabric version 4.X.X.
If IPF version is v5.X then set to `v5`.**

## Running
`python3 main.py`

## Settings not copied
Due to passwords, scheduled tasks, and other issues the following settings are not copied.
These will need to be manually configured however re-running this script will not override or delete
any of these settings.

- Users (including LDAP/SSO)
- API Tokens
- Webhooks
- Device Auth
- Vendors API
- Backup Settings
- Jumphost Settings
- Config Backup Settings
- Automatic Snapshots
- SNMP

## Future Considerations
If you would like to add new features or make a suggestion for this project please open a GitHub issue.

## Example Output

```commandline
Using .env Configuration of:

SAVE_TO_FILE:	True

IPF_URL_SOURCE:	https://demo3.ipfabric.io
IPF_TOKEN_SOURCE:	XXXXXXXXXXXXXX
IPF_API_VERSION_SOURCE:	v1
IPF_VERIFY_SOURCE:	True

IPF_URL_TARGET:	https://192.168.0.100
IPF_TOKEN_TARGET:	XXXXXXXXXXXXXX
IPF_API_VERSION_TARGET:	v1
IPF_VERIFY_TARGET:	False

Do you accept the current configuration (y/n): y

##INFO## STARTING API script to push settings...

Do you wish to COPY source settings to Target? (y/n): y
Do you wish to COPY & REPLACE Custom Site Name Attributes to Target? (y/n): y

##INFO## Copied Custom Site Name Attributes Completed.

Do you wish to COPY & REPLACE Site Separation Rules to Target? (y/n): y

##INFO## Copied Site Separation Rules Completed.

Do you wish to COPY & REPLACE Seed List to Target? (y/n): y

##INFO## Copied Seed List Completed.

Do you wish to COPY Advanced Settings to Target? (y/n): y
Do you wish to COPY Advanced > Discovery Settings to Target? (y/n): y

##INFO## Copied Advanced > Discovery Settings Completed.

Do you wish to COPY Advanced > Discovery Tasks Settings to Target? (y/n): y

##INFO## Copied Advanced > Discovery Tasks Settings Completed.

Do you wish to COPY Advanced > SSH/Telnet Settings to Target? (y/n): y

##INFO## Copied Advanced > SSH/Telnet Settings Completed.

Do you wish to COPY and Replace Advanced > SSH/Telnet > Custom SSH/Telnet Ports to Target? (y/n): y

##INFO## Copied Advanced > SSH/Telnet > Custom SSH/Telnet Ports Completed.


##INFO## Copied Advanced Settings Completed.

Do you wish to COPY & REPLACE ALL Intents, Intent Groups, and Dashboard to Target? (y/n): y

DO YOU ACCEPT OVERRIDING ALL INTENTS, INTENT GROUPS, DASHBOARD SETTINGS? (y/n): y


##INFO## Execution completed!
##INFO## Copied Intents, Intent Groups, and Dashboard Completed.
```