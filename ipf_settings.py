import json
from collections import OrderedDict

from ipfabric import IPFClient
from ipfabric.settings import Seeds, Attributes
from ipfabric.tools import RestoreIntents
from deepdiff import DeepDiff

PROMPT = 'Do you wish to COPY & REPLACE {0} to Target? (y/n): '


class IPFSettings:
    def __init__(self, base_url, token, api_version=None, verify=False):
        self.ipf = IPFClient(base_url, token=token, api_version=api_version, verify=verify)
        self.settings = self.sanitize_settings(self.ipf.get("settings").json())
        self.custom_ports = self.ipf.fetch_all('tables/settings/ports', snapshot=False)
        self.site_separation = self.settings["siteSeparation"]
        self.seed_list = self.settings["seedList"]
        self.sitename_attributes = self.ipf.fetch_all('tables/global-attributes', columns=["sn", "name", "value"],
                                                      filters={"name": ["eq", "siteName"]}, snapshot=False)
        self.oui = self.ipf.fetch_all('tables/reports/settings-oui', columns=["id", "vendor", "enabled"],
                                      snapshot=False)
        self.intents = self.ipf.get('reports').json()
        self.intent_groups = self.ipf.get('reports/groups').json()
        self.dashboard = json.loads(self.ipf.get('settings/dashboard').text, object_pairs_hook=OrderedDict)

    @staticmethod
    def sanitize_settings(settings):
        # Discovery
        if not settings["scanner"]["enabled"]:
            settings["scanner"] = {"enabled": False}
        # SSH/Telnet
        if not settings["cliSessionsLimit"]["enabled"]:
            settings["cliSessionsLimit"] = {"enabled": False}
        return settings

    def _push_oui(self, other):
        i = input(PROMPT.format('OUI Settings')).strip().lower()
        if i and 'y' not in i[0]:
            return False
        diff = DeepDiff({oui['id']: oui for oui in other.oui}, {oui['id']: oui for oui in self.oui})
        post_oui = [d.t1 for d in diff.tree['dictionary_item_removed']]
        patch_oui, put_oui = list(), list()
        for d in diff.tree['values_changed']:
            if isinstance(d.t1, str):
                put_oui.append(d.up.t1)
            else:
                patch_oui.append(d.up.t1)

        [o.pop('vendor', None) for o in patch_oui]
        res = self.ipf.patch('settings/oui', json=patch_oui)
        res.raise_for_status()

        for o in post_oui:
            res = self.ipf.post('settings/oui', json=o)
            res.raise_for_status()

        for o in put_oui:
            o_id = o.pop('id')
            res = self.ipf.put(f'settings/oui/{o_id}', json=o)
            res.raise_for_status()
        print("\n##INFO## Copied OUI Settings Completed.\n")

    def push_settings(self, other):
        i = input(PROMPT.format('Custom Site Name Attributes')).strip().lower()
        if i and 'y' in i[0]:
            attributes = Attributes(client=self.ipf)
            target_attributes = attributes.all()
            if target_attributes:
                attributes.delete_attribute_by_id(*[a['id'] for a in target_attributes])
            attributes.set_sites_by_sn(other.sitename_attributes)
            print("\n##INFO## Copied Custom Site Name Attributes Completed.\n")
        i = input(PROMPT.format('Site Separation Rules')).strip().lower()
        if i and 'y' in i[0]:
            res = self.ipf.put("settings/site-separation", json=other.site_separation)
            res.raise_for_status()
            print("\n##INFO## Copied Site Separation Rules Completed.\n")
        i = input(PROMPT.format('Seed List')).strip().lower()
        if i and 'y' in i[0]:
            Seeds(client=self.ipf).set_seeds(other.seed_list)
            print("\n##INFO## Copied Seed List Completed.\n")
        i = input('Do you wish to COPY Advanced Settings to Target? (y/n): ').strip().lower()
        if i and 'y' in i[0]:
            self._push_advanced(other)
            print("\n##INFO## Copied Advanced Settings Completed.\n")
        self._push_oui(other)
        i = input(PROMPT.format('ALL Intents, Intent Groups, and Dashboard')).strip().lower()
        if i and 'y' in i[0]:
            ri = RestoreIntents(self.ipf)
            ri.restore_from_dictionary(other.intents, other.intent_groups, other.dashboard)
            print("\n##INFO## Copied Intents, Intent Groups, and Dashboard Completed.\n")
        return True

    def _prompt_and_push(self, setting, data):
        i = input(f'Do you wish to COPY Advanced > {setting} Settings to Target? (y/n): ').strip().lower()
        if i and 'y' in i[0]:
            res = self.ipf.patch("settings", json=data)
            res.raise_for_status()
            print(f"\n##INFO## Copied Advanced > {setting} Settings Completed.\n")

    def _push_custom_ports(self, other):
        i = input('Do you wish to COPY and Replace Advanced > SSH/Telnet > '
                  'Custom SSH/Telnet Ports to Target? (y/n): ').strip().lower()
        if i and 'y' in i[0]:
            for p in self.custom_ports:
                self.ipf.delete(f'settings/ports/{p["id"]}')
            for p in other.custom_ports:
                p.pop('id', None)
                res = self.ipf.post("settings/ports", json=p)
                res.raise_for_status()
            print("\n##INFO## Copied Advanced > SSH/Telnet > Custom SSH/Telnet Ports Completed.\n")

    def _push_advanced(self, other):
        discovery = {k: other.settings[k] for k in other.settings.keys() &
                     {'fullBgpLimit', 'limitDiscoveryTasks', 'networks', 'resolveNames', 'scanner', 'traceroute'}}
        ssh = {k: other.settings[k] for k in other.settings.keys() &
               {'allowTelnet', 'cliRetryLimit', 'cliSessionsLimit', 'timeouts'}}
        self._prompt_and_push('Discovery', discovery)
        self._prompt_and_push('Discovery Tasks', {'discoveryTasks': other.settings['discoveryTasks']})
        self._prompt_and_push('SSH/Telnet', ssh)
        self._push_custom_ports(other)
