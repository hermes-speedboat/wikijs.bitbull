---
title: Ascender Setup
description: Setup Ascender (AWX) on Rocky Linux 10
published: true
date: 2026-02-15T15:34:20.839Z
tags: ansible, awx, ascender, kubernetes
editor: markdown
dateCreated: 2026-02-15T15:06:49.959Z
---

Ascender provides a web-based user interface, REST API, and task engine built on top of Ansible. It is based off the upstream project of AWX.

# VM Setup

## VM requirements
Just setup a Rocky Linux 9 minimal VM with the following requirements
* CPU: 2
* MEM: 8GB (6 GB may work as well)
* DISK: 40G (7GB used on a fresh setup)

## Prepare OS
```bash
dnf -y upgrade
dnf -y install setroubleshoot-server curl lsof wget git bash-completion openssl

sed -i  '/swap/d' /etc/fstab
swapoff -a

firewall-cmd --permanent --zone=public --add-service=https
# firewall-cmd --zone=public --add-masquerade --permanent
firewall-cmd --reload
reboot
```



# Setup K3S
```bash
curl -sfL https://get.k3s.io | sh

cat /etc/systemd/system/k3s.service
systemctl status k3s

kubectl get nodes
# all pods in running state? fine!
kubectl get pods --all-namespaces
```

# Setup Ascender
```bash
APP_FQDN=$(hostname -f)

cd
mkdir git
cd git

openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -sha256 -days 3650 -nodes -subj "/C=CH/ST=SG/L=StGall/O=BITBULL/OU=IT/CN=$APP_FQDN"

APP_FQDN=ascender.app.bitbull.ch
git clone https://github.com/ctrliq/ascender-install.git

cd ascender-install

# we skip the installer config cmd, we already have our settings
# bash config_vars.sh

echo '---
k8s_platform: k3s
kube_install: false
k8s_offline: false
download_kubeconfig: true
k8s_lb_protocol: https
k3s_master_node_ip: "127.0.0.1"
use_etc_hosts: false
tls_crt_path: "~/git/cert.pem"
tls_key_path: "~/git/key.pem"
tmp_dir: "{{ playbook_dir}}/../ascender_install_artifacts"
ASCENDER_HOSTNAME: awx.sun.bitbull.ch
ASCENDER_NAMESPACE: ascender
ASCENDER_ADMIN_USER: admin
ASCENDER_ADMIN_PASSWORD: "ChangeMeNow."
ASCENDER_VERSION: 25.3.4       
ANSIBLE_OPERATOR_VERSION: 2.19.3
ascender_garbage_collect_secrets: false
ascender_replicas: 1
image_pull_policy: Always
ascender_setup_playbooks: false
LEDGER_INSTALL: false' > custom.config.yml
                                                                                                                                                                                              
sed -i "s/ASCENDER_HOSTNAME:.*/ASCENDER_HOSTNAME: $APP_FQDN/" custom.config.yml
bash ./setup.sh
 


```




=Fetch the secret and test the login=
 kubectl get secret bitbull-admin-password -o jsonpath='{.data.password}' | base64 --decode

 firefox https://fqdn.domain.com
* user: admin

=Links=
* https://rancher.com/docs/k3s/latest/en/quick-start/
* https://rancher.com/docs/k3s/latest/en/backup-restore/
* https://github.com/ansible/awx-operator

=Debug Notes=
==Open Node Port for direct access==
 PORT=$(kubectl describe svc awx-service | grep NodePort: | awk '{print $3}' | tr 'A-Z' 'a-z')
 echo PORT=$PORT
 firewall-cmd --zone=public --add-port=$PORT

==Disable SELinux==
 setenforce 0
 > /var/log/audit/audit.log 
 # do some bad things
 sealert -a /var/log/audit/audit.log

==Traefik Config==
- https://levelup.gitconnected.com/a-guide-to-k3s-ingress-using-traefik-with-nodeport-6eb29add0b4b
 kubectl -n kube-system edit cm traefik

==Jump into container for debugging==
 # get pods
 kubectl get pods
 # get containers inside of pods
 kubectl describe <pod-name>

 kubectl exec --stdin --tty <pod-name> -c <container-name> -- /bin/bash

=Notes=
==Backup==

 vim awx-backup.yml
<pre>
---
apiVersion: awx.ansible.com/v1beta1
kind: AWXBackup
metadata:
  name: awxbackup-20220311
  namespace: awx
spec:
  deployment_name: awx
...
</pre>

 oc apply -f awx-backup.yml

 oc get awxbackups awxbackup-20220311 -o yaml

<pre>
apiVersion: awx.ansible.com/v1beta1
kind: AWXBackup
...
name: awxbackup-20220311
...
status:
  backupClaim: awx-backup-claim
  backupDirectory: /backups/tower-openshift-backup-2022-03-11-05:45:56
  conditions:
  - lastTransitionTime: "2022-03-11T05:45:07Z"
    reason: Successful
    status: "True"
    type: Running
</pre>

Keep that as well for DR reason
 oc get awxbackups awxbackup-20220311 -o yaml > awxbackup-20220311.yml

<pre>
ll /srv/nfs/pv05/tower-openshift-backup-2022-03-11-05\:45\:56/
total 13072
-rw-r--r--. 1 1000680000 root      600 Mar 11 06:46 awx_object
-rw-r--r--. 1 1000680000 root      670 Mar 11 06:46 secrets.yml
-rw-------. 1 1000680000 root 13377441 Mar 11 06:46 tower.db
</pre>

==Restore==
 vim awx-restore.yml
<pre>
---
apiVersion: awx.ansible.com/v1beta1
kind: AWXRestore
metadata:
  name: awxrestore-20230221
  namespace: awx
spec:
  deployment_name: bitbull
  backup_pvc_namespace: awx
  backup_dir: /backups/tower-openshift-backup-2023-02-20-17:04:58
  backup_pvc: awx-backup-claim
...
</pre>

 oc apply -f awx-restore.yml

 oc get awxrestores -o yaml

[[Category:Ansible]]
[[Category:K3S]]
[[Category:OpenShift & K8S]]

==okd 4.10 instance template==
<pre>
apiVersion: awx.ansible.com/v1beta1
kind: AWX
metadata:
  name: bitbull
spec:
  ingress_type: route
  route_host: awx.domain.com
  route_tls_termination_mechanism: edge
</pre>





==AWX CLI==
* https://github.com/ansible/awx/blob/devel/INSTALL.md#installing-the-awx-cli
<pre>
pip3 install awxkit
export TOWER_HOST=https://awx.domain.com TOWER_USERNAME=admin TOWER_PASSWORD=xxx
awx login admin
awx export > export.json
</pre>

[[Category:Ansible]]
[[Category:K3S]]
[[Category:OpenShift & K8S]]
