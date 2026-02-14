---
title: Install Rundeck
description: Install Rundeck, Setup Ansible, Configure Mixed Node Inventory (Lin/Win)
published: true
date: 2026-02-14T09:05:06.054Z
tags: ansible, rundeck
editor: markdown
dateCreated: 2026-02-14T08:20:30.237Z
---

# Setup Rundeck
* Install Rocky Linux 9 Minimal
* 4vCPU
* 8 GB Memory
* 50 GB HDD

## Setup Ansible
```bash
curl -L ansible.bitbull.ch | bash

# needed to get rundeck repo signing working
update-crypto-policies --set DEFAULT:SHA1

reboot
```

## Install Rundeck
```bash
# notice the new ansible venv in /opt/ansible
cda
ansible-galaxy install joe-speedboat.virt_tools joe-speedboat.rundeck joe-speedboat.mariadb



```

### Prepare Ansible Setup
* `cda ; vim playbooks/install_rundeck.yml`
```
- hosts: localhost
  become: True
  vars:
    ansible_connection: local
    rundeck_install_ansible: False
    rundeck_admin_pass: ***
    mariadb_root_password: ***
    mariadb_user_password: ***
  roles:
  - role: joe-speedboat.rundeck
  - role: joe-speedboat.virt_tools
  tasks:
  - name: install firewalld
    yum:
      name: firewalld
      state: present
  - name: start firewalld
    service:
      name: firewalld
      enabled: yes
      state: started
  - name: open https port on firewalld
    firewalld:
      service: https
      permanent: true
      state: enabled
  - name: enable firewalld
    service:
      name: firewalld
      enabled: yes
      state: restarted
...

```
chmod 600 install_rundeck.yml
ansible-playbookinstall_rundeck.yml
```

* Now test rundeck login as admin with your WebBrowser

## General settings
* config helper
```bash
echo '#!/bin/sh
cp -av "$1" "$1.$(date +%Y%m%%dH%M%S)"
' > /usr/local/bin/backup
chmod 755 /usr/local/bin/backup
```
==Ansible configuration==
<pre>
# root user
dnf -y install git wget curl rsync vim sshpass

# root user
chown -R rundeck.rundeck /etc/ansible
chmod -R u+rwX,go-rwx /etc/ansible

# rundeck user
cd /etc/ansible
sed -i 's#^inventory=.*#inventory=/etc/ansible/inventory#' /etc/ansible/ansible.cfg
rm -f hosts
mkdir -p /etc/ansible/inventory/group_vars
vim /etc/ansible/inventory/group_vars/all.yml
----------
ansible_become: True
ansible_user: deploy_rundeck_prod
----------
</pre>





=Advanced Rundeck/Ansible config=

==Protect vars and ssh key==
<pre>
# root user
dnf -y install keyutils

# we do not start this services after reboot, we do this with vault unlock
systemctl disable rundeckd nginx

vim /usr/local/sbin/init-rundeck-and-ansible.sh
----------
#!/bin/bash
echo
echo Feed the ssh private key passphrase for rundeck
echo "Hashi Vault > linuxeng_kv > application_user > ansible_vault_pw@srundeck01.domain.local"

sudo -u rundeck --login echo
echo
echo INFO: re/starting rundeck + nginx service
systemctl restart rundeckd nginx
echo
echo
echo All done
echo Now login to rundeck webUI:
echo .Test the inventory 
echo .Test AdHoc command
----------
chmod 700 /usr/local/sbin/init-rundeck-and-ansible.sh

echo '
#FEED ANSIBLE VAULT AND SSH-KEY PASSWORD after reboot
   cmd: init-rundeck-and-ansible.sh
' >> /etc/motd

# rundeck user
cd
cp -av /etc/skel/.bash* .
chown rundeck.rundeck .bash*
chmod go-rwx .bash*

echo '. $HOME/bin/vault-unlock.sh -b' >> ~/.bashrc
echo 'export PATH=$PATH:$HOME/bin' >> ~/.bashrc
echo 'alias via="ansible-vault edit"' >> ~/.bashrc
echo 'alias cda="cd /etc/ansible"' >> ~/.bashrc

mkdir bin
curl https://raw.githubusercontent.com/joe-speedboat/linux.scripts/master/ansible/vault-unlock.sh > $HOME/bin/vault-unlock.sh
chown rundeck.rundeck $HOME/bin/vault-unlock.sh
chmod 700 $HOME/bin/vault-unlock.sh
sed -i "s#^.vault_password_file=.*#vault_password_file=$HOME/bin/vault-unlock.sh#" /etc/ansible/ansible.cfg

ssh-keygen -p #feed new passphrase, which is vault-pw as well
. ~/.bashrc
# feed password

# encrypt setup playbook
ansible-vault encrypt  /etc/ansible/playbooks/install_rundeck.yml
cat  /etc/ansible/playbooks/install_rundeck.yml # it is encrypted now
via  /etc/ansible/playbooks/install_rundeck.yml # you see it clear now
</pre>

* reboot and test unlock as mentioned in motd





=Additional Settings=
==FreeIPA Inventory==
<pre>
# rundeck user
curl https://raw.githubusercontent.com/joe-speedboat/linux.scripts/master/ansible/ansible_dynamic_inventory_freeipa_with_vars.py > inventory/freeipa.py
chmod 700 inventory/freeipa.py
python -m pip install --user python_freeipa

echo '# FreeIPA Ansible Inventory Auth
# FreeIPA Ansible Inventory Auth
export freeipaserver=freeipa01.domain.local
export freeipauser='svc_bind_rundeck_prod'
export freeipapassword='******'
' >> $HOME/.bashrc
</pre>

==Rundeck FreeIPA Auth==
<pre>

vim /etc/rundeck/multiauth.conf
--------------------------------
multiauth {

  com.dtolabs.rundeck.jetty.jaas.JettyCachingLdapLoginModule sufficient
    debug="true"
    contextFactory="com.sun.jndi.ldap.LdapCtxFactory"
    providerUrl="ldaps://freeipa01.domain.local:636 ldaps://freeipa02.domain.local:636"
    ldapsVerifyHostname="false"
    bindDn="uid=svc_bind_rundeck_prod,cn=users,cn=accounts,dc=domain,dc=local"
    bindPassword="******"
    authenticationMethod="simple"
    forceBindingLogin="true"
    userBaseDn="cn=users,cn=accounts,dc=domain,dc=local"
    userRdnAttribute="uid"
    userIdAttribute="uid"
    userPasswordAttribute="userPassword"
    userObjectClass="posixAccount"
    userLastNameAttribute="sn"
    userFirstNameAttribute="givenName"
    userEmailAttribute="mail"
    roleBaseDn="cn=groups,cn=accounts,dc=domain,dc=local"
    roleNameAttribute="cn"
    roleMemberAttribute="member"
    roleObjectClass="groupOfNames"
    cacheDurationMillis="300000"
    reportStatistics="true";

  org.eclipse.jetty.jaas.spi.PropertyFileLoginModule required
    debug="true"
    file="/etc/rundeck/realm.properties";
};
--------------------------------

chown root.rundeck /etc/rundeck/multiauth.conf
chmod 640 /etc/rundeck/multiauth.conf


vim /etc/rundeck/rundeck-config.properties
--------------------------------
rundeck.security.syncLdapUser=true
--------------------------------

vim /etc/sysconfig/rundeckd
--------------------------------
JAAS_LOGIN=true
LOGIN_MODULE=multiauth
JAAS_CONF=/etc/rundeck/multiauth.conf
--------------------------------



vim /etc/rundeck/ansibleadm.aclpolicy
-------------------------------
description: FreeIPA Rundeck Admin, all access.
context:
  project: '.*' # all projects
for:
  resource:
    - allow: '*' # allow read/create all kinds
  adhoc:
    - allow: '*' # allow read/running/killing adhoc jobs
  job: 
    - allow: '*' # allow read/write/delete/run/kill of all jobs
  node:
    - allow: '*' # allow read/run for all nodes
by:
  group: rundeckadm
---
description: FreeIPA Rundeck Admin, all access.
context:
  application: 'rundeck'
for:
  resource:
    - allow: '*' # allow create of projects
  project:
    - allow: '*' # allow view/admin of all projects
  project_acl:
    - allow: '*' # allow admin of all project-level ACL policies
  storage:
    - allow: '*' # allow read/create/update/delete for all /keys/* storage content
by:
  group: rundeckadm
-----------------------------
chown root.rundeck /etc/rundeck/ansibleadm.aclpolicy
chmod 640 /etc/rundeck/ansibleadm.aclpolicy

echo | openssl s_client -showcerts -connect freeipa01.domain.local:636 > /etc/rundeck/ssl/idm.pem
vim /etc/rundeck/ssl/idm.pem # remove comments
cp -av /etc/pki/ca-trust/extracted/java/cacerts /etc/pki/ca-trust/extracted/java/cacerts.orig
keytool -import -alias idm -file /etc/rundeck/ssl/idm.pem -keystore /etc/pki/ca-trust/extracted/java/cacerts -storepass changeit

keytool -import -alias idm -file /etc/rundeck/ssl/idm.pem -keystore /etc/rundeck/ssl/truststore -storepass adminadmin
chown rundeck.rundeck /etc/rundeck/ssl/*
</pre>

==Rundeck Ansible Project example==
<pre>
PROJECT: ansible
--------------------------------------------------------
Detail:
   Project Name: ansible
   Label: ansible_linux_ssh
Execution History Clean: 
   Enable: [X]
User Interface :
   Job Group Expansion Level: 9
Default Node Executor:
  Type: Ansible Ad-Hoc Node Executor
     Executable: /bin/bash
     Windows Executable: powershell.exe
     Ansible config file path: /etc/ansible/ansible.cfg
Default File Copier:
  Type: local
  We just use native ansible, this is not needed


PROJECT: ansible > Edit Nodes > Sources > Add
--------------------------------------------------------
Type: Ansible Resource Model Source
Ansible config file path: /etc/ansible/ansible.cfg
</pre>

=BUGS & FIXES=

* Error Msg: <tt>/bin/sh: /tmp/0-1-localhost-dispatch-script.tmp.sh: Permission denied</tt>
<pre>
echo '
# ----------------------------------------------------------------
# CUSTOM VALUES
# ----------------------------------------------------------------
framework.file-copy-destination-dir = ~/
' >> /etc/rundeck/framework.properties

systemctl restart rundeckd
</pre>

==service.log not rotated==
* Problem: /var/log/rundeck/service.log grows and get not rotated
<pre>
 cat << EOF > /etc/logrotate.d/rundeck_service
 /var/log/rundeck/service.log {
  su root root
  copytruncate
  daily
  missingok
  rotate 7
  compress
  delaycompress
  notifempty
  create 640 root adm
 }
 EOF

logrotate -fv /etc/logrotate.d/rundeck_service
</pre>

==gelf remote logging==
* https://github.com/tseeker/rundeck-gelf-plugin
<pre>
$ cd /var/lib/rundeck/libext
$ wget https://raw.githubusercontent.com/tseeker/rundeck-gelf-plugin/master/GelfPlugin.groovy
$ cd /etc/rundeck

# set values as default, since (by bug) framework.properties get not honored
$ grep default /var/lib/rundeck/libext/GelfPlugin.groovy
        host defaultValue:"syslog.domain.local", required:true, description: "Hostname to connect to"
        port defaultValue:2222, required:true, description: "Port to connect to", type: 'Integer'

$ grep Gelf rundeck-config.properties
rundeck.execution.logs.streamingWriterPlugins=GelfPlugin

</pre>

[[Category:Alma8]]
[[Category:Ansible]]
[[Category:Linux]]
