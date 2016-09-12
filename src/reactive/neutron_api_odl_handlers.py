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

import charms.reactive as reactive

# This charm's library contains all of the handler code associated with
# aodh
import charm.openstack.neutron_api_odl as neutron_api_odl


# Minimal inferfaces required for operation
MINIMAL_INTERFACES = [
    'controller-api.access.available',
]


@reactive.when_not('charm.installed')
def install_packages():
    neutron_api_odl.install()
    reactive.set_state('charm.installed')


@reactive.when('odl-controller.access.available')
def render_config(controller):
    neutron_api_odl.render_config(controller)

@reactive.when('neutron-plugin-api-subordinate.connected')
def configure_plugin(api_principle):
    neutron_api_odl.configure_plugin(api_principle)

@reactive.when_file_changed(neutron_api_odl.ML2_CONF)
@reactive.when('neutron-plugin-api-subordinate.connected')
def remote_restart(api_principle):
    api_principle.request_restart()


