#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright: (c) 2020, Radware LTD.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'certified'}

DOCUMENTATION = r'''
module: alteon_device_configuration
short_description: Download/Upload Alteon configuration
description:
  - Download/Upload Alteon configuration with or without crypto keys. 
  - the command expect src/dst file path
version_added: null
author: 
  - Leon Meguira (@leonmeguira)
options:
  provider:
    description:
      - Radware Alteon connection details.
    required: true
    suboptions:
      server:
        description:
          - Radware Alteon IP.
        required: true
        default: null
      user:
        description:
          - Radware Alteon username.
        required: true
        default: null
      password:
        description:
          - Radware Alteon password.
        required: true
        default: null
      validate_certs:
        description:
          - If C(no), SSL certificates will not be validated.
          - This should only set to C(no) used on personally controlled sites using self-signed certificates.
        required: true
        default: null
        type: bool
      https_port:
        description:
          - Radware Alteon https port.
        required: true
        default: null
      ssh_port:
        description:
          - Radware Alteon ssh port.
        required: true
        default: null
      timeout:
        description:
          - Timeout for connection.
        required: true
        default: null
  command:
    description:
      - Action to run.
    required: true
    default: null
    choices:
    - config_download
    - config_upload
  file_path:
    description:
      - path to configuration file
      - on download - .tgz file extension is appended if not specified 
    required: true
    default: null
    type: str
  passphrase:
    description:
      - passphrase for crypto keys encryption
    required: false
    default: null
    type: str
  include_keys:
    description:
      - download/upload configuration with crypto keys - passphrase is required for key mode
    required: false
    default: false
    type: bool
  vx_cfg_only:
    description:
      - download VX configuration without vADCs - applicable to VX form factor
    required: false
    default: false
    type: bool
notes:
  - Requires Radware alteon Python SDK.
requirements:
  - Radware alteon Python SDK.
'''

EXAMPLES = r'''
- name: alteon device configuration
  alteon_device_configuration:
    provider: 
      server: 192.168.1.1
      user: admin
      password: admin
      validate_certs: no
      https_port: 443
      ssh_port: 22
      timeout: 5
    command: config_download
    passphrase: radware
    include_keys: true
    file_path: /home/user/cfg/alteon_cfg.tgz
'''

RETURN = r'''
status:
  description: Message detailing run result
  returned: success
  type: str
  sample: Configuration Downloaded Successfully
'''

from ansible.module_utils.basic import AnsibleModule
import traceback

from ansible.module_utils.network.radware.common import RadwareModuleError
from ansible.module_utils.network.radware.alteon import AlteonManagementModule, AlteonManagementFunctionArgumentSpec
from radware.alteon.sdk.alteon_managment import AlteonMngOper


class ModuleManager(AlteonManagementModule):
    def __init__(self, **kwargs):
        super(ModuleManager, self).__init__(AlteonMngOper, **kwargs)


def main():
    spec = AlteonManagementFunctionArgumentSpec(AlteonMngOper.config_download, AlteonMngOper.config_upload)
    module = AnsibleModule(argument_spec=spec.argument_spec, supports_check_mode=spec.supports_check_mode)

    try:
        mm = ModuleManager(module=module)
        result = mm.exec_module()
        module.exit_json(**result)
    except RadwareModuleError as e:
        module.fail_json(msg=str(e), exception=traceback.format_exc())


if __name__ == '__main__':
    main()
