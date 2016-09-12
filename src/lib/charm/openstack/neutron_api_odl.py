# Copyright 2016 Canonical Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import charms_openstack.adapters
import charms_openstack.charm
import charmhelpers.contrib.openstack.utils as ch_utils

ML2_CONF = '/etc/neutron/plugins/ml2/ml2_conf.ini'
VLAN = 'vlan'
VXLAN = 'vxlan'
GRE = 'gre'
OVERLAY_NET_TYPES = [VXLAN, GRE]


def install():
    """Use the singleton from the NeutronAPIODLCharm to install the packages on the
    unit

    @returns: None
    """
    NeutronAPIODLCharm.singleton.install()

def configure_plugin(api_principle):
    NeutronAPIODLCharm.singleton.configure_plugin(api_principle)

def render_config(controller_interface):
    NeutronAPIODLCharm.singleton.render_with_interfaces([controller_interface])

class NeutronAPIODLConfigurationAdapter(charms_openstack.adapters.ConfigurationAdapter):

    @property
    def overlay_net_types(self):
        overlay_networks = self.overlay_network_type.split()
        for overlay_net in overlay_networks:
            if overlay_net not in OVERLAY_NET_TYPES:
                raise ValueError('Unsupported overlay-network-type %s'
                                 % overlay_net)
        return ','.join(overlay_networks)

class NeutronAPIODLAdapters(charms_openstack.adapters.OpenStackRelationAdapters):
    """
    Adapters class for the NeutronAPIODL charm.
    """

    def __init__(self, relations):
        super(NeutronAPIODLAdapters, self).__init__(
            relations,
            options_instance=NeutronAPIODLConfigurationAdapter())

class NeutronAPIODLCharm(charms_openstack.charm.OpenStackCharm):


    name = 'neutron-api-odl'
    packages = ['neutron-common', 'neutron-plugin-ml2']

    required_relations = ['neutron-plugin-api-subordinate', 'odl-controller']

    adapters_class = NeutronAPIODLAdapters
    restart_map = {ML2_CONF: []}
    release = 'icehouse'

    def __init__(self, release=None, **kwargs):
        """Custom initialiser for class
        If no release is passed, then the charm determines the release from the
        ch_utils.os_release() function.
        """
        if release is None:
            release = ch_utils.os_release('neutron-common')
        super(NeutronAPIODLCharm, self).__init__(release=release, **kwargs)

    @property
    def all_packages(self):
        """List of packages to be installed

        @return ['pkg1', 'pkg2', ...]
        """
        _packages = self.packages[:]
        if self.release >= 'kilo':
            _packages.extend(['python-networking-odl'])
        return _packages

    def configure_plugin(self, api_principle):
        # Add sections and tuples to insert values into neutron-server's
        # neutron.conf e.g.
        # principle_config = {
        #     "neutron-api": {
        #        "/etc/neutron/neutron.conf": {
        #             "sections": {
        #                 'DEFAULT': [
        #                     ('key1', 'val1')
        #                     ('key2', 'val2')
        #                 ],
        #                 'agent': [
        #                     ('key3', 'val3')
        #                 ],
        #             }
        #         }
        #     }
        # }

        inject_config = {
            "neutron-api": {
                "/etc/neutron/neutron.conf": {
                    "sections": {
                        'DEFAULT': [
                        ],
                    }
                }
            }
        }
        api_principle.configure_plugin(
            neutron_plugin='odl',
            core_plugin='neutron.plugins.ml2.plugin.Ml2Plugin',
            neutron_plugin_config='/etc/neutron/plugins/ml2/ml2_conf.ini',
            service_plugins='router,firewall,lbaas,vpnaas,metering',
            subordinate_configuration=inject_config)
