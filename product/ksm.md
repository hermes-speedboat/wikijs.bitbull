---
title: ksm
description: 
published: true
date: 2026-02-01T09:19:40.093Z
tags: howto, ksm, kvm, setup
editor: markdown
dateCreated: 2026-02-01T09:16:53.394Z
---

## enable nested virtualization
### For AMD CPUs
```bash
[root@clue2 ~]# cat /sys/module/kvm_amd/parameters/nested
0

[root@clue2 ~]# echo "options kvm-amd nested=1" >> /etc/modprobe.d/dist.conf

[root@clue2 ~]# rmmod kvm-amd

[root@clue2 ~]# modprobe kvm-amd

[root@clue2 ~]# modinfo kvm_amd | grep -i nested
parm:           nested:int

[root@clue2 ~]# cat /sys/module/kvm_amd/parameters/nested
1
```

```bash
[root@clue2 ~]# virsh edit ov-compute1
---modify---
<cpu mode='host-passthrough'/>
---------
[root@clue2 ~]# virsh start ov-compute1
```

=For Intel CPUs=
```bash
clue1# cat /sys/module/kvm_intel/parameters/nested
N

clue1# rmmod kvm-intel
clue1# echo 'options kvm-intel nested=y' >> /etc/modprobe.d/dist.conf
clue1# modprobe kvm-intel

clue1# cat /sys/module/kvm_intel/parameters/nested
Y

clue1# modinfo kvm_intel | grep nested
parm:           nested:bool
```

```bash
clue1# virsh edit ov-compute1
---modify---
<cpu mode='host-passthrough'/>
---------
clue1# virsh start ov-compute1
```

## tuning
It is easy to enable kvm. However, the defaults are fairly conservative.

### howto enable
* `vi /etc/rc.local`

```bash
# ksm page merging, default 0
echo 1 > /sys/kernel/mm/ksm/run
# pages to scan on each run, default: 100
echo 1000 > /sys/kernel/mm/ksm/pages_to_scan
# time to sleep after each scan, default: 200
echo 20 > /sys/kernel/mm/ksm/sleep_millisecs
```
```bash
chmod +x /etc/rc.d/rc.local
```

### load tuning
```bash
free -t | grep ^Mem: | awk '{print $7/1024 " MB"}'
top # sort for cpu with "P" and look for ksmd
```