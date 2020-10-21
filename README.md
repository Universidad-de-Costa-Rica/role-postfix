Postfix
=========

Ansible role to install and configure Posfix 

Requirements
------------

- See [`requirements.txt`](requirements.txt)
- **It does not handle firewall or ports**
- **It does not manage SSL certs by itself**

Role Variables
--------------

- See [`defaults/main.yml`](defaults/main.yml).
- See also [`vars/`](vars/) for additional variables.


Example Playbook
----------------

```yaml
- hosts: postfix
  vars:
    postfix_domain: example.org
    postfix_main_cfg:
      mynetworks: "127.0.0.0/8 [::1]/128 192.168.1.0/24"
      recipient_delimiter: "+"
      unknown_local_recipient_reject_code: "550"
      owner_request_special: "no"
      alias_maps: hash:/etc/aliases
  roles:
    - ucr.postfix
```

License
-------

GPLv3

Author Information
------------------

Manuel Delgado López (@valarauco): manuel.delgado {at} ucr.ac.cr