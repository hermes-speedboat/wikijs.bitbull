---
title: ksm
description: 
published: true
date: 2026-02-01T09:26:45.687Z
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

### For Intel CPUs
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

## enable vm serial console
How to configure serial console for KVM vm. So virsh will have access:
```bash
virsh console <vm-name>
```

### Red Hat
* https://access.redhat.com/articles/7212
#### RHEL9
```bash
grubby --update-kernel=ALL --args="console=tty0 console=ttyS0,115200"
```
#### RHEL8
```bash
grub2-editenv - set "$(grub2-editenv - list | grep kernelopts) console=tty0 console=ttyS0,115200"
```


### ubuntu
```bash
systemctl enable serial-getty@ttyS0.service
systemctl start serial-getty@ttyS0.service
```

### alpine
* Enabling a login console
This is done in `/etc/inittab`. There is commented entry for `ttyS0`. Just enable it.
```bash
# Put a getty on the serial port
ttyS0::respawn:/sbin/getty -L ttyS0 115200 vt100
```

* To start the getty, restart init:
```bash
kill -HUP 1
```

* Enabling two consoles during boot

It's possible to output to both the serial and vga console during the system boot.

```bash
append "quiet console=ttyS0,9600 console=tty0"
```

Not known how to do the same thing in the extlinux menu. 
You might find a starting point in this thread: http://patchwork.openembedded.org/patch/45175/

* Add your serial console to the trusted local terminal list
If you face the problem that the login prompt always refuses your password when you use serial console, you missed this entry.

Add this to the `/etc/securetty` file:   
```bash
ttyS0
```
