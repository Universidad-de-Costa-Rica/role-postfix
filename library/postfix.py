#!/usr/bin/python
# -*- coding: utf-8 -*-

# Based on: https://gist.github.com/mgedmin/5f8ac034df0c371444be

# Make coding more python3-ish, this is required for contributions to Ansible
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
---
module: postfix
short_description: changes postfix configuration parameters
description:
  - The M(postfix) module changes postfix configuration by invoking 'postconf'.
    This is needed if you don't want to use M(template) for the entire main.cf,
    because M(lineinfile) cannot handle multi-line configuration values, and
    solutions involving M(command) are cumbersone or don't work correctly
    in check mode.
  - Be sure to run C(postfix reload) (or, for settings like inet_interfaces,
    C(service postfix restart)) afterwards.
options:
  name:
    description:
      - the name of the setting
    required: true
    default: null
    type: string
  value:
    description:
      - the value for that setting
    required: true
    default: null
    type: string
author:
  - Marius Gedminas <marius@pov.lt>
  - Manuel Delgado <manuel.delgado@ucr.ac.cr>
'''

EXAMPLES = '''
- postfix: name=myhostname value={{ ansible_fqdn }}
- postfix: name=mynetworks value="127.0.0.0/8, [::1]/128, 192.168.1.0/24"
- postfix: name={{ item.name }} value="{{ item.value }}"
  with_items:
    - { name: inet_interfaces, value: loopback-only }
    - { name: inet_protocols,  value: ipv4          }
'''

import subprocess
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_native, to_text


class TaskError(Exception):
    pass


def run(args, module):
    try:
        cmd = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = cmd.communicate()
        rc = cmd.returncode
    except (OSError, IOError) as e:
        module.fail_json(rc=e.errno, msg=str(e), cmd=args)
    if rc != 0 or err:
        module.fail_json(rc=rc, msg=err, cmd=args)
    return out


def main():
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(type='str', default='present', choices=['absent', 'present']),
            name=dict(type='str', required=True),
            value=dict(type='str', required=True),
            # master=dict(type='bool', default=False),
            # service_type=dict(type='str', default='inet'),
        ),
        supports_check_mode=True,
    )
    state = module.params['state']
    name = module.params['name']
    value = module.params['value'].strip()
    # master = module.params['master']
    # service_type = module.params['service_type']

    old_value = run(['postconf', '-h', name], module).decode("utf-8").strip()
    default_value = run(['postconf', '-dh', name], module).decode("utf-8").strip()
    exit_msg = ""
    changed = False
    diff = dict(
        before='',
        after='',
        before_header=to_text('postconf -h {}'.format(name)),
        after_header=to_text('postconf -h {}'.format(name)),
    )

    if state == 'present':
        if value != old_value and not module.check_mode:
            run(['postconf', '{}={}'.format(name, value)], module)
            exit_msg = "setting changed"
            changed = True
            diff['before'] = to_text(old_value + '\n')
            diff['after'] = to_text(value + '\n')
    if state == 'absent':
        if not module.check_mode:
            run(['postconf', '-X', '{}'.format(name)], module)
            exit_msg = "setting removed"
        # Mark not changed if removed value was default.
        if default_value != old_value:
            exit_msg = "setting removed"
            changed = True
            diff['before'] = to_text(old_value + '\n')
            diff['after'] = to_text(default_value + '\n')
            diff['after_header'] = to_text('postconf -dh {}'.format(name)),

    module.exit_json(
        msg=exit_msg,
        diff=diff,
        changed=changed,
    )


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        #  TODO: better Exception handling
        raise TaskError('Something happened, this was original exception: %s' % to_native(e))
