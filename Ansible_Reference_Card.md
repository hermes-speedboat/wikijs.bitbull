---
title: Ansible Reference Card
description: Reference and cheat sheet for Ansible and Ansible Navigator
published: true
date: 2026-01-07T00:00:00.000Z
tags: ansible, referencecards, automation, devops
editor: markdown
dateCreated: 2026-01-07T00:00:00.000Z
---

# Overview

## Ansible Navigator

| Ansible Command | Ansible Navigator Equivalent |
|---|---|
| **Inventory Commands** |  |
| `ansible-inventory -i inventory --list` | `ansible-navigator inventory -i inventory --list -m stdout` |
| `ansible-inventory -i inventory --graph` | `ansible-navigator inventory -i inventory --graph -m stdout` |
| **Vault Commands (Mostly Local, Remain the Same)** |  |
| `ansible-vault create secret.yml` | `ansible-vault create secret.yml` *(Remains the same)* |
| `ansible-vault encrypt secret.yml` | `ansible-vault encrypt secret.yml` *(Remains the same)* |
| `ansible-vault decrypt secret.yml` | `ansible-vault decrypt secret.yml` *(Remains the same)* |
| `ansible-vault view secret.yml` | `ansible-vault view secret.yml` *(Remains the same)* |
| **Playbook Commands** |  |
| `ansible-playbook playbook.yml` | `ansible-navigator run playbook.yml -m stdout` |
| `ansible-playbook -i inventory playbook.yml` | `ansible-navigator run -i inventory playbook.yml -m stdout` |
| `ansible-playbook -b playbook.yml` | `ansible-navigator run -b playbook.yml -m stdout` |
| `ansible-playbook -e "var=value" playbook.yml` | `ansible-navigator run -e "var=value" playbook.yml -m stdout` |
| **Ad-Hoc Commands** |  |
| `ansible all -m ping` | `ansible-navigator exec "ansible all -m ping" -m stdout` |
| `ansible localhost -m setup` | `ansible-navigator exec "ansible localhost -m setup" -m stdout`<br>`ansible-navigator exec "ansible localhost -m setup -a filter=*ipv4* webserver"` |
| `ansible webservers -a "df -h"` | `ansible-navigator exec "ansible webservers -a 'df -h'" -m stdout` |
| **Console Commands** |  |
| `ansible-console -b linux_servers` | `ansible-navigator exec "ansible-console -b linux_servers" -m stdout` |
| **Configuration and Documentation** |  |
| `ansible-config dump` | `ansible-navigator config -m stdout` |
| `ansible-doc -l` | `ansible-navigator doc -l -m stdout` |
| `ansible-doc -s module_name` | `ansible-navigator doc module_name -m stdout` |

### bashrc example with aliases

```bash
# Alias for ansible-playbook
alias nansible-playbook="ansible-navigator run -m stdout"

# Alias for ansible (Ad-Hoc Commands)
alias nansible="function _nansible() { ansible-navigator exec -m stdout \"ansible \$@\"; }; _nansible"

# Alias for ansible-inventory
alias nansible-inventory="ansible-navigator inventory -m stdout"

# Alias for ansible-config
alias nansible-config="ansible-navigator config -m stdout"

# Alias for ansible-doc
alias nansible-doc="ansible-navigator doc -m stdout"

# Alias for ansible-vault (Remains the same)
alias nansible-vault="ansible-vault"

# Alias for ansible-galaxy
alias nansible-galaxy="ansible-navigator galaxy -m stdout"

# Alias for ansible-test (if applicable)
alias nansible-test="ansible-navigator test -m stdout"
```

# Inventory

## Documentation

- show all inventory plugins  
  `ansible-doc -t inventory -l`
- show ini style inventory (default)  
  `ansible-doc -t inventory ini`
- adoc, documentation helper  
  ```bash
  curl -O $HOME/bin/adoc https://raw.githubusercontent.com/joe-speedboat/shell.scripts/master/adoc.sh
  chmod 755 $HOME/bin/adoc
  ```

## Export a uniq list of all hosts in inventory

```bash
ansible-inventory --list | jq -r '..|.hosts?|arrays|.[]' | sort | uniq
```

## Examples

`/etc/ansible/hosts`
```ini
[apache]
web[01:05] ansible_user=devops

[nginx]
web[10:12]
web13 ansible_port=222 has_java = False
10.0.1.[250:253]

[nginx:vars]
http_port=8080

[webservers:children]
nginx
apache
```

## Dynamic Inventory Example

`inventory/dynamic-inventory.sh`
```bash
#!/bin/bash
echo '{
   "web": ["www1", "www2", "www3"],
   "db": ["db1", "db2", "oracle1"]
}'
```

`inventory/hosts`
```ini
[sudo]
vm20 ansible_user=ansible
```

```bash
chmod 700 inventory/dynamic-inventory.sh
ls -l inventory/
# -rwxr-xr-x. 1 root root 94 Dec 14 15:01 dynamic-inventory.sh
# -rw-r--r--. 1 root root 34 Dec 14 15:03 hosts
```

```bash
[root@ansible lab]# ansible -i inventory/ --list-hosts web
  hosts (3):
    www1
    www2
    www3
[root@ansible lab]# ansible -i inventory/ --list-hosts sudo
  hosts (1):
    vm20
```

## Dynamic Inventory via DNS Zone Transfer

- https://github.com/joe-speedboat/shell.scripts/blob/master/ansible_dynamic_inventory_dns_zonetransfer.py

## Commands

- query inventory for specific hosts  
  `ansible web01 --list-hosts`
  `ansible 'all:!kvm' -i /etc/ansible/hosts --list-hosts`
- show host involved by playbook  
  `ansible-playbook --list-hosts tests/qa.yml`
- run module on specific host  
  `ansible vm06 -m setup`

## cmd export/import

```bash
ansible-inventory --list --export --yaml > i.yaml
ansible --list-hosts all -i i.yaml 
ansible -i i.yaml -m ping all
```

# Setup Ansible

## Install with pip

```bash
dnf -y remove ansible-collection-ansible-posix ansible
dnf -y install python38-pip python38 sshpass
su - $ANSIBLE_USER
python3.8 -m pip install --user ansible

echo '#ANSIBLE SETUP
PATH=$HOME/.local/bin:$HOME/bin:$HOME
' > $HOME/.bashrc
```

## Install with yum

```bash
curl -L ansible.bitbull.ch | bash
```

## Configure Ansible

- Order of config file sources  
  `ANSIBLE_CONFIG=/opt/ansible.cfg -> ./ansible.cfg -> $HOME/.ansible.cfg -> /etc/ansible/ansible.cfg`
- Config Sections  
  `egrep '^\['  /etc/ansible/ansible.cfg`
  ```
  [defaults]
  [privilege_escalation]
  [ssh_connection]
  [accelerate]
  [selinux]
  [colors]
  ```

### show non default values

`ansible-config dump --only-changed -t all`

### defaults

```
forks          = 5    # specify number of parallel processes to use
host_key_checking = True
vault_password_file = /path/to/vault_password_file
ansible_managed = Ansible managed: {file} on {host}
display_skipped_hosts = True
display_args_to_stdout = True
```

### privilege_escalation

```
become=True # to enable privilege escalation
```

#### Example

```bash
# define user in inventory on ansible host
vm20 ansible_user=ansible

# create and configure user on destination host
useradd ansible
 
su - ansible
mkdir .ssh
chmod 700 .ssh
vi .ssh/authorized_keys # add ansible host pub key 
chmod 600 .ssh/authorized_keys
 
echo 'ansible ALL=(ALL)NOPASSWD: ALL' > /etc/sudoers.d/ansible
visudo -cf /etc/sudoers.d/ansible

# verify configuration
[root@ansible lab]# ansible vm20 -m command -a w
vm20 | SUCCESS | rc=0 >>
 14:24:49 up 48 min,  2 users,  load average: 0.00, 0.01, 0.05
USER     TTY      FROM             LOGIN@   IDLE   JCPU   PCPU WHAT
root     pts/0    192.168.223.59   13:43    5:05   0.05s  0.00s tail -f /var/log/secure
ansible  pts/1    192.168.223.43   14:24    0.00s  0.10s  0.00s /bin/bash -c sudo -H -S -n -u root /bin/bash -c 'echo BECOME-SUCCESS-fwkpkpwhbtkkrxdktmuwvgjmi...
```

## vim settings

`$HOME/.vimrc`
```
set expandtab
set autoindent
set tabstop=2
set shiftwidth=2
set softtabstop=2
```

# Configure Cisco IOS devices

```yaml
ansible-galaxy collection install ansible.netcommon
```

*ios_playbook_example.yml*
```yaml
- hosts: switch-aa-325-06
  gather_facts: no
  vars:
    #### ansible v5
    #ansible_connection: ansible.netcommon.network_cli
    #ansible_network_os: cisco.ios.ios
    #### ansible v2.9
    ansible_connection: network_cli
    ansible_network_os: ios
    ansible_user: admin
    ansible_password: xxx
    ansible_become: yes
    ansible_become_method: enable
    ansible_become_password: xxx

  pre_tasks:
  - name: Gather facts
    ios_facts:
    when: ansible_network_os == 'ios'

  tasks:
  - name: run ios cmd
    ios_command:
      commands: show version
    register: version
  - name: print cmd output
    debug: 
      var: version
  - name: print all native facts
    debug:
      var: ansible_facts

  - name: backup config (ios)
    ios_config:
      backup_options:
        dir_path: /tmp/ios-backup
      backup: yes
    register: backup_ios_location
    when: ansible_network_os == 'ios'
  - name: print ios backup config
    debug:
      var: backup_ios_location
```

# Configure Fortigate devices

Note that forti modules are not really well maintained.  
It's always try and error, I succeeded only with ansible v5 for real world usage  
some of them use https connection, some only ssh!

```bash
ansible-galaxy collection install fortinet.fortimanager
ansible-galaxy collection install fortinet.fortios:1.1.7 #version depends on forti-os release!
```

### backup config

```yaml
- name: backup fortigate config
  hosts: fw01
  collections:
  - fortinet.fortios
  vars:
    vdom: "root"
    ansible_httpapi_use_ssl: yes
    ansible_httpapi_validate_certs: no
    ansible_httpapi_port: 8443
    # ansible_user: xxx
    # ansible_password: yyy
  connection: httpapi
  gather_facts: no
  tasks:
  - name: backup global or a_specific_vdom settings
    fortinet.fortios.fortios_system_config_backup_restore:
      config: "system config backup"
      host: "{{ inventory_hostname }}:{{ ansible_httpapi_port }}"
      username: "{{ ansible_user }}"
      password: "{{ ansible_password }}"
      https: "{{ ansible_httpapi_use_ssl }}"
      ssl_verify: "{{ ansible_httpapi_validate_certs }}"
      backup: yes
      scope: global
      vdom: "{{ vdom|default('root') }}"
      filename: "./{{ inventory_hostname }}.cfg"
```

### native cmd configuration

Since Fortigate Ansible modules do often not work as expected and are difficult to handle, we prefer native cmd configuration.  
This one is compatible with native target configuration, so you can use backup, facts, ... along with native cmd writing.

```yaml
- name: write cmds to fortigate devices with ansible
  hosts: fortifw01
  gather_facts: no
  vars:
    ansible_connection: httpapi
    ansible_httpapi_port: 844
    ansible_httpapi_use_ssl: true
    ansible_httpapi_validate_certs: false
    ansible_network_os: fortinet.fortios.fortios
    ansible_password: xxx
    ansible_user: forti-ops
    vdom: root

  pre_tasks:
  - name: gather facts for forti devices
    fortios_facts:
      vdom:  "{{ vdom|default('root') }}"
      gather_subset:
        - fact: system_current-admins_select
        - fact: system_firmware_select
        - fact: system_fortimanager_status
        - fact: system_ha-checksums_select
        - fact: system_interface_select
        - fact: system_status_select
        - fact: system_time_select
    when: ansible_network_os|lower == 'fortinet.fortios.fortios'

  tasks:
  - name: define fw config fact for bgp
    set_fact:
      target_cfg: |
        config vdom
        edit "{{ fw_vdom }}"
        config router bgp
         set as {{ fw_as }}
         set router-id {{ fw_if_v4 }}
         set ebgp-multipath enable
         set ibgp-multipath enable
         config neighbor
          edit "{{ sw_if_v4 }}"
           set activate6 disable
           set bfd enable
           set remote-as {{ as_fusion }}
          next
          edit "{{ sw_if_v6 }}"
           set activate disable
           set bfd enable
           set remote-as {{ as_fusion }}
         end
        end

  - name: verbose print target_cfg for firewall bgp fw_vdom={{ fw_vdom}} fw_as={{ fw_as }}
    debug:
      msg: "{{ target_cfg.split('\n') }}"

  - name: apply bgp config to fortigate device
    vars:
      ansible_connection: ssh
    raw: "{{ target_cfg }}"
    register: cmd
    failed_when: >
      ("Command fail" in cmd.stdout) or
      (cmd.rc > 0)

  - name: display output bgp fw_vdom={{ fw_vdom}} fw_as={{ fw_as }}
    debug:
      msg: |
        {{ cmd.stdout_lines }}
```

# Configure Watchguard devices

Watchguard devices have ssh service running at port 4118 by default, but sadly there are no ansible modules around.  
Do not try to solve this issue with "ansible raw module". It just does not work. It just logs-in to the watchguard, than it does not recognize the prompt and wait until timeout.  
So this is the "most lean" workaround I found for dropping a few lines to an Watchguard device, eg. kicking remote backup.

```yaml
---
- name: backup watchguard config
  hosts: nfw-x001-01
  gather_facts: no
  vars:
    ftp_user: ftp-backup-user
    ftp_password: yyy
    ftp_hostname: ftphost.domain.local
    #ansible_connection: local
    #ansible_password: xxx
    #ansible_port: 4118
    #ansible_user: status
  tasks:
  - name: raw local ftp backup kicking
    raw: | 
      sshpass -p '{{ ansible_password }}' \
        ssh -C \
          -o StrictHostKeyChecking=no \
          -o Port={{ ansible_port }} \
          -o User={{ ansible_user }} \
          -tt {{ inventory_hostname }} <<EOF
      export config to ftp://{{ ftp_user }}:{{ ftp_password }}@{{ ftp_hostname }}/{{ inventory_hostname }}.xml
      exit
      EOF
    register: cmd
    failed_when: >
      ("Invalid input detected at" in cmd.stdout) or not
      (cmd.stdout|regex_search("\\nWG.*>>"))
```

# Daily helpers

## play options

- run each task as fast as possible

```yaml
- hosts: all
  strategy: free
  remote_user: ansible-ops
  fact_gathering: no
  tasks:
```

## extended alive checking

```yaml
---
- name: check if host is online right now
  ping:
  register: ping
  failed_when: false

- name: wait for host to become online
  wait_for:
    port: "{{ (ansible_port|default(ansible_ssh_port))|default(22) }}"
    host: '{{ (ansible_ssh_host|default(ansible_host))|default(inventory_hostname) }}'
    search_regex: OpenSSH
    delay: 10  # do not check for at least 10 sec
  connection: local
  when: ping.failed == true

- name: finally, we decide to proceed or fail
  setup:
  when: ping.failed == false
```

## useful tasks and options

```yaml
- name: validate vni value
  fail:
    msg: vni must be greater than 5000
  when: vni|int <= 5000
---
- name: check if host is member of spine hostgroup
  set_fact:
    dev_type_inv: 'spine'
  when: "'spine' in group_names"
---
- name: verify mariadb root access
  command:  mysql -u root -ne "show databases;"
  register: mariadb_access_test
  notify: restart rsyslog
  no_log: True
  ignore_errors: True
  changed_when: False
  failed_when: false
```

## print multiline message

```yaml
- name: Print several lines of text
  vars:
    msg: |
         This is the first line.
         This is the second line with a variable like {{ inventory_hostname }}.
         And here could be more...
  debug:
    msg: "{{ msg.split('\n') }}"
```

# Working with Playbooks

## Loop examples

```yaml
---
- hosts: localhost
  vars:
    var1: this is one var
    array1: [aaa, bbb]
    array2:
      - ccc
      - ddd
    dictionary1: { key1: value1, key2: value2 }
    dictionary2:
      key3: value3
      key4: value4
    multi_array1:
      user1:
        name: bob
        nr: 123
      user2:
        name: mike
        nr: 456
  tasks:
  - name: show var1
    debug:
      msg: "{{ var1 }}"

  - name: loop array1
    debug:
      msg: "{{ item }}"
    with_items: "{{ array1 }}"

  - name: loop array2
    debug:
      msg: "{{ item }}"
    with_items: "{{ array2 }}"

  - name: loop dictionary1
    debug:
      msg: "{{ item.key }}: {{ item.value }}"
    with_dict: "{{ dictionary1 }}"

  - name: loop dictionary2
    debug:
      msg: "{{ item.key }}: {{ item.value }}"
    with_dict: "{{ dictionary2 }}"

  - name: "multi_array1['user1']['name']" 
    debug:
      msg: "multi_array1['user1']['name']: {{ multi_array1['user1']['name'] }}"
  - name: "multi_array1.user2'.name"
    debug:
      msg: "multi_array1.user2'.name: {{ multi_array1.user2.name }}"

  - name: multi_array1 loop with_dict
    debug: 
      msg: "User {{ item.key }} is {{ item.value.name }} with nr {{ item.value.nr }}"
    with_dict: '{{ multi_array1 }}'

  - name: loop with with_fileglob
    debug:
      msg: "/etc/ansible/{{item}}"
    with_fileglob: "/etc/ansible/*"
...
```

### Example Output

```text
PLAY [localhost] ******************************************************************************************************

TASK [Gathering Facts] ************************************************************************************************
ok: [localhost]

TASK [show var1] ******************************************************************************************************
ok: [localhost] => {
    "msg": "this is one var"
}

TASK [loop array1] ****************************************************************************************************
ok: [localhost] => (item=aaa) => {
    "item": "aaa", 
    "msg": "aaa"
}
ok: [localhost] => (item=bbb) => {
    "item": "bbb", 
    "msg": "bbb"
}

TASK [loop array2] ****************************************************************************************************
ok: [localhost] => (item=ccc) => {
    "item": "ccc", 
    "msg": "ccc"
}
ok: [localhost] => (item=ddd) => {
    "item": "ddd", 
    "msg": "ddd"
}

TASK [loop dictionary1] ***********************************************************************************************
ok: [localhost] => (item={'key': u'key2', 'value': u'value2'}) => {
    "item": {
        "key": "key2", 
        "value": "value2"
    }, 
    "msg": "key2: value2"
}
ok: [localhost] => (item={'key': u'key1', 'value': u'value1'}) => {
    "item": {
        "key": "key1", 
        "value": "value1"
    }, 
    "msg": "key1: value1"
}

TASK [loop dictionary2] ***********************************************************************************************
ok: [localhost] => (item={'key': u'key3', 'value': u'value3'}) => {
    "item": {
        "key": "key3", 
        "value": "value3"
    }, 
    "msg": "key3: value3"
}
ok: [localhost] => (item={'key': u'key4', 'value': u'value4'}) => {
    "item": {
        "key": "key4", 
        "value": "value4"
    }, 
    "msg": "key4: value4"
}

TASK [multi_array1['user1']['name']] **********************************************************************************
ok: [localhost] => {
    "msg": "multi_array1['user1']['name']: bob"
}

TASK [multi_array1.user2'.name] ***************************************************************************************
ok: [localhost] => {
    "msg": "multi_array1.user2'.name: mike"
}

TASK [multi_array1 loop with_dict] ************************************************************************************
ok: [localhost] => (item={'key': u'user2', 'value': {u'nr': 456, u'name': u'mike'}}) => {
    "item": {
        "key": "user2", 
        "value": {
            "name": "mike", 
            "nr": 456
        }
    }, 
    "msg": "User user2 is mike with nr 456"
}
ok: [localhost] => (item={'key': u'user1', 'value': {u'nr': 123, u'name': u'bob'}}) => {
    "item": {
        "key": "user1", 
        "value": {
            "name": "bob", 
            "nr": 123
        }
    }, 
    "msg": "User user1 is bob with nr 123"
}

TASK [loop with with_fileglob] ****************************************************************************************
ok: [localhost] => (item=/etc/ansible/hosts) => {
    "item": "/etc/ansible/hosts", 
    "msg": "/etc/ansible//etc/ansible/hosts"
}
ok: [localhost] => (item=/etc/ansible/ansible.cfg) => {
    "item": "/etc/ansible/ansible.cfg", 
    "msg": "/etc/ansible//etc/ansible/ansible.cfg"
}
ok: [localhost] => (item=/etc/ansible/ansible.cfg.rpmnew) => {
    "item": "/etc/ansible/ansible.cfg.rpmnew", 
    "msg": "/etc/ansible//etc/ansible/ansible.cfg.rpmnew"
}

PLAY RECAP ************************************************************************************************************
localhost                  : ok=10   changed=0    unreachable=0    failed=0   
```

## Merging Dictionaries, dynamic Variables

```yaml
- hosts: localhost
  vars:
    _default:
      name: chris
      name2: lompetier
    _custom1:
      name: calvin
      name2: hobbes
    _custom2:
      name: god

  tasks:
  - set_fact: {"{{ item.key }}":"{{ item.value }}"}
    with_dict:  "{{_default|combine(_custom1)|combine(_custom2)}}"
```

### Example Output

```text
PLAY [localhost] **************************************************************************************************************************************************************************************************

TASK [Gathering Facts] ********************************************************************************************************************************************************************************************
ok: [localhost]

TASK [set_fact] ***************************************************************************************************************************************************************************************************
ok: [localhost] => (item={'key': 'name', 'value': 'god'})
ok: [localhost] => (item={'key': 'name2', 'value': 'hobbes'})

PLAY RECAP ********************************************************************************************************************************************************************************************************
localhost                  : ok=4    changed=0    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0   
```

# Variables and Inclusions

## include_tasks vs. import_tasks

In Ansible, both `include_tasks` and `import_tasks` are used to include a set of tasks from another file into your playbook or role. However, they differ significantly in **when** and **how** they include these tasks, which affects their behavior regarding variables, loops, and conditionals.

### Key Differences

#### 1. Timing of Inclusion

- **`import_tasks`**: Includes tasks **statically at parse time**. This means Ansible reads and incorporates the tasks into the playbook **before** any plays or tasks are executed.
- **`include_tasks`**: Includes tasks **dynamically at runtime**. Ansible reads and executes these tasks **during** the playbook run, at the point where the `include_tasks` directive is called.

#### 2. Variable Evaluation

- **`import_tasks`**: Variables used in the imported tasks must be available at **parse time**. Runtime variables (those defined during the play) are **not** accessible.
- **`include_tasks`**: Can utilize variables that are defined or modified at **runtime**, allowing for dynamic task inclusion based on the current play context.

#### 3. Support for Loops and Conditionals

- **`import_tasks`**: Cannot be used with loops (`with_items`, `loop`) or conditionals that depend on runtime variables.
- **`include_tasks`**: Supports loops and conditionals, making it possible to include tasks multiple times or based on conditions evaluated during play execution.

### Examples

#### 1. Using `include_tasks` with a Loop and Runtime Variable

```yaml
- name: Dynamic Task Inclusion Example
  hosts: all
  vars:
    task_files:
      - setup.yml
      - install.yml
      - configure.yml
  tasks:
    - name: Include task files dynamically
      include_tasks: "{{ item }}"
      loop: "{{ task_files }}"
```

**Explanation**: Here, `include_tasks` is used within a loop to include multiple task files. The `task_files` variable can be modified at runtime, and the inclusion happens dynamically.

#### 2. Using `import_tasks` Statically

```yaml
- name: Static Task Inclusion Example
  hosts: all
  tasks:
    - name: Import common tasks
      import_tasks: common_tasks.yml
```

**Explanation**: `import_tasks` includes `common_tasks.yml` at parse time. All tasks in `common_tasks.yml` become part of the playbook before execution starts.

#### 3. Conditional Inclusion with `include_tasks`

```yaml
- name: Conditional Task Inclusion Example
  hosts: all
  vars:
    deploy_environment: "production"
  tasks:
    - name: Include production tasks
      include_tasks: production_tasks.yml
      when: deploy_environment == "production"

    - name: Include development tasks
      include_tasks: development_tasks.yml
      when: deploy_environment == "development"
```

**Explanation**: Based on the value of `deploy_environment`, different task files are included at runtime.

#### 4. Attempting to Use `import_tasks` with a Runtime Variable (Not Recommended)

```yaml
- name: Incorrect Usage of import_tasks
  hosts: all
  vars:
    task_file: "{{ 'tasks_' + environment + '.yml' }}"
    environment: "staging"
  tasks:
    - name: Import tasks based on environment
      import_tasks: "{{ task_file }}"
```

**Explanation**: This will fail because `import_tasks` cannot use variables that are defined at runtime (`environment` in this case) to determine which tasks to import.

### When to Use Which

- **Use `include_tasks` when**:
  - You need to include tasks based on variables or conditions that are only known at runtime.
  - You want to loop over task files or include them conditionally.
  - You require dynamic behavior in your playbook.

- **Use `import_tasks` when**:
  - You have a static set of tasks to include that do not depend on runtime variables.
  - You prefer all tasks to be known at parse time for clarity or for tooling that analyzes playbooks.
  - You want to ensure that any syntax errors in the included tasks are caught before execution.

### Summary

- **`import_tasks`** is for **static inclusion** at parse time, without support for runtime variables, loops, or dynamic conditions.
- **`include_tasks`** is for **dynamic inclusion** at runtime, supporting loops, conditionals, and runtime variables.

Understanding these differences helps you decide which directive to use based on the needs of your playbook. If you require flexibility and dynamic behavior, `include_tasks` is the appropriate choice. If your tasks are static and you want them included upfront, `import_tasks` is suitable.

**Additional Tip**: In newer versions of Ansible, the distinction between these two directives has become more pronounced, so it's good practice to choose the one that aligns with your playbook's requirements to avoid unexpected behaviors.

# Ansible variable precedence

[Ansible variable overriding documentation](http://docs.ansible.com/ansible/latest/playbooks_variables.html#variable-precedence-where-should-i-put-a-variable)

In 2.x, we have made the order of precedence more specific (with the last listed variables winning prioritization):

- role defaults [1]
- inventory file or script group vars [2]
- inventory group_vars/all
- playbook group_vars/all
- inventory group_vars/*
- playbook group_vars/*
- inventory file or script host vars [2]
- inventory host_vars/*
- playbook host_vars/*
- host facts
- play vars
- play vars_prompt
- play vars_files
- role vars (defined in role/vars/main.yml)
- block vars (only for tasks in block)
- task vars (only for the task)
- role (and include_role) params
- include params
- include_vars
- set_facts / registered vars
- extra vars (always win precedence)

Basically, anything that goes into “role defaults” (the defaults folder inside the role) is the most malleable and easily overridden. Anything in the vars directory of the role overrides previous versions of that variable in namespace. The idea here to follow is that the more explicit you get in scope, the more precedence it takes with command line -e extra vars always winning. Host and/or inventory variables can win over role defaults, but not explicit includes like the vars directory or an include_vars task.

# Task Control

## Parallel execution

```yaml
# playbook
- name: do not wait for tasks to finish on all hosts before proceed
  hosts: all
  strategy: free

# playbook
- name: do run 10 hosts at once
  hosts: all
  serial: 10

# playbook
- name: do run 1 host in first batch, then 10% on each of the next batches
  hosts: all
  serial:
  - 1
  - 10%

# task
- name: run this task one by one on each host
  command: /path/to/cpu_intensive_command
  throttle: 1

# task
- name: run this task only on one host in group
  file:
    path: /srv/backup
    state: directory
  run_once: True
  delegate_to: localhost
```

## shell

```yaml
- name: get list of services without Ansible warning
  shell: "service --status-all 2>&1 | awk {'print $4'}"
  args:
    warn: false # set warn=false to prevent warning
  register: services_list
- name: show results
  debug:
    var: services_list
```

## error handling

```yaml
- name: this will not be counted as a failure
  command: /bin/false
  ignore_errors: yes

- name: Fail task when the command error output prints FAILED
  command: /usr/bin/example-command -x -y -z
  register: command_result
  failed_when: "'FAILED' in command_result.stderr"

- name: Fail task when both files are identical
  raw: diff foo/file1 bar/file2
  register: diff_cmd
  failed_when: diff_cmd.rc == 0 or diff_cmd.rc >= 2

- name: Check if a file exists in temp and fail task if it does
  command: ls /tmp/this_should_not_be_here
  register: result
  failed_when:
    - result.rc == 0
    - '"No such" not in result.stdout'

- name: example of many failed_when conditions with OR
  shell: "./myBinary"
  register: ret
  failed_when: >
    ("No such file or directory" in ret.stdout) or
    (ret.stderr != '') or
    (ret.rc == 10)

- command: /bin/fake_command
  register: result
  ignore_errors: True
  changed_when:
    - '"ERROR" in result.stderr'
    - result.rc == 2
```

## conditions

| Operation | Example |
|---|---|
| Equal (value is a string) | `ansible_facts['machine'] == "x86_64"` |
| Equal (value is numeric) | `max_memory == 512` |
| Less than | `min_memory < 128` |
| Greater than | `min_memory > 256` |
| Less than or equal to | `min_memory <= 256` |
| Greater than or equal to | `min_memory >= 512` |
| Not equal to | `min_memory != 512` |
| Variable exists | `min_memory is defined` |
| Variable does not exist | `min_memory is not defined` |
| Boolean variable is true. The values of 1, True, or yes evaluate to true. | `memory_available` |
| Boolean variable is false. The values of 0, False, or no evaluate to false. | `not memory_available` |
| First variable's value is present as a value in second variable's list | `ansible_facts['distribution'] in supported_distros` |

```yaml
- name: Activate license
  uri:
    method: PUT 
    url: "{{ api_uri }}/{{ license_api }}?acknowledge=true"
    user: "{{ api_basic_auth_username  | default(omit)}}"
    password: "{{ api_basic_auth_password | default(omit)}}"
    body_format: json
    body: "{{ license }}"
    return_content: yes 
    force_basic_auth: yes 
    validate_certs: "{{ validate_certs }}"
  register: license_activated
  no_log: True
  failed_when: >
    license_activated.status != 200 or
    license_activated.json.license_status is not defined or
    license_activated.json.license_status != 'valid'

- name: verbose print target_cfg for firewall zone {{ fw_zone_name }}
  debug:
    msg: "{{ target_cfg.split('\n') }}"
  when: verbose_output|bool

- name: find hosts with ee_is_master=true in hostvars of inventory group elastic
  set_fact:
    elastic_masters: "{{ elastic_masters|default(['']) + [ hostvars[item]['inventory_hostname_short'] ]}}"
  with_items: "{{ groups['elastic'] }}"
  when: "hostvars[item]['ee_is_master']|default('true')|bool is true"

- name: define configuration string for AUTO mode
  set_fact:
    graylog_elasticsearch_hosts: "http://{{ elastic_masters|select()|unique|join(':9200,http://') }}:9200"
  when: (( ansible_play_hosts_all|length ) > 1 ) and graylog_elasticsearch_hosts == 'auto'
```

# Jinja2 Templates

# File Handling

# Working with Roles

# Optimizing Ansible

## ansible.cfg

```ini
[inventory]
enable_plugins = host_list, script, auto, yaml, ini, toml

[defaults]
inventory         = ./inventory
roles_path        = ./roles
collections_paths = ./collections
log_path          = ansible.log
deprecation_warnings = False
action_warnings = False
nocows = 1
force_color = True
host_key_checking = False
display_skipped_hosts = False
forks = 20
```

# Ansible Vault

## Set Variable with bad characters

```yaml
app_password: >-
  =aU"4'3/\fdgfs/¦
```

# Troubleshooting Ansible

## AWX Debugging

### CLI Ansible Debugging in CustomEE

```bash
grep ansible /proc/*/comm
/usr/bin/python3 /usr/local/bin/ansible -u deploy_awx_prod --become --become-method sudo --become-user root mytarget.domain.com -i /runner/inventory/hosts -e@/runner/env/extravars -m debug -a "var=ansible_python_interpreter"
```
