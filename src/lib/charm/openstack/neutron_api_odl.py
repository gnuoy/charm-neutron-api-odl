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

def install():
    """Use the singleton from the DesignateCharm to install the packages on the
    unit

    @returns: None
    """
    NeutronAPIODLCharm.singleton.install()


def render_config(interfaces_list):
    NeutronAPIODLCharm.singleton.render_with_interfaces(interfaces_list)


class NeutronAPIODLCharm(charms_openstack.charm.OpenStackCharm):

    
    name = 'neutron-api-odl'
    packages = ['neutron-common', 'neutron-plugin-ml2']

    required_relations = ['neutron-plugin-api-subordinate', 'odl-controller']

    adapters_class = charms_openstack.adapters.OpenStackAPIRelationAdapters
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
