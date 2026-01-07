---
title: LVM Merkblatt für REL7 (LVM2)
description: Reference card for LVM management on REL7 systems
tags: referencecards, lvm, linux
---

# LVM nachträglich installieren
```bash
vgscan #lvm initialisieren
fdisk /dev/???
pvcreate /dev/hda3 /dev/hdb1 
vgcreate -s 16M vg0 /dev/hda3 /dev/hdb1
lvcreate -L 4G -n lv_var vg0
# partition mit mke2fs -j /dev/vg0/lv_var
```

# Logical ext Volumes vergrössern (online)
```bash
lvextend -L +800M /dev/vg0/lv_var #vergrössert das lv um 800MB
resize2fs /dev/vg0/lv_var #zieht die partitionsgrösse des ext dateisystems nach
```

# Logical xfs Volumes vergrössern (online)
```bash
lvextend -L +800M /dev/vg0/lv_var #vergrössert das lv um 800MB
xfs_growfs /dev/vg0/lv_var #zieht die partitionsgrösse des ext dateisystems nach
```

# Logical ext Volumes verkleinern (offline)
```bash
umount /dev/vg0/lv_var #verkleinern ist nur offline möglich
e2fsck -f /dev/vg0/lv_var  
resize2fs /dev/vg0/lv_var 600M #daten auf der partition zusammenschieben
lvreduce -L 600M /dev/vg0/lv_var #partition verkleinern
```

# Logical xfs Volumes verkleinern
Nicht möglich

# Pysical Volumes zu einer Volume Group hinzufügen
```bash
fdisk /dev/hdc (n,p,1,<ENTER>,<ENTER>,t,8e,p,w,<ENTER>)
pvcreate /dev/hdc1
vgextend vg0 /dev/hdc1
vgck vg0
```

# Physical Volumes aus einer Volume Group entfernen
```bash
pvmove /dev/hdb1 #um das physical volume leer zu machen
vgreduce vg0 /dev/hdb1 #um das physical volume aus vg0 zu entfernen
```

# LVM Snapshots erzeugen, daten sichern & aufräumen
```bash
lvcreate -L 500M --snapshot -n snap_var /dev/vg0/lv_var
mkdir -p /mnt/snap_var
mount /dev/vg0/snap_var /mnt/snap_var
tar vcfz /mnt/usbdisk/snap_var.tar.gz /mnt/snap_var/
umount /mnt/snap_var
lvremove /dev/vg0/snap_var # um den snapshot zu löschen
```
> Beachten Sie, dass auf dem Snapshot nur die Daten liegen, die sich seit Erzeugung des Snapshots auf dem zu sichernden LV verändert haben. Ändern sich auf dem zu sichernden LV mehr Daten als der Snapshot an Platz bietet, wird der Snapshot augenblicklich deaktiviert.

# lvm Physical Volume vergrössern
* Disk in Virtualisierung vergrössern

```bash
disk=sda
part=3
vg=myvg
lv=tmp

# scasi bus scannen
echo 1 > /sys/class/block/$disk/device/rescan
# partitions tabelle der physischen disk neu einlesen
partprobe -s

# disk partitionen anzeigen
fdisk -l /dev/$disk

# block devices auflisten
lsblk

# backup mbr
dd if=/dev/$disk of=/root/$disk.mbr bs=512 count=1

LV=/dev/$vg/$lv
parted /dev/$disk resizepart $part 100% 
pvresize /dev/${disk}${part} 
lvextend -l +100%FREE /dev/$vg/$lv 
# just use the one you need or do the dirty hack below :-)
xfs_growfs /dev/$vg/$lv  || resize2fs /dev/$vg/$lv

# vergrössere pv disk
pvs
pvresize /dev/${disk}${part}
pvs # ist jetzt vergrössert

# vergrössere lv
lvs
lvextend -L 100G /dev/$vg/$lv
lvs # ist jetzt vergrössert

# nachfolgend wird angenommen, das wir das /tmp dateisystem vergrössern wollen und es mit xfs formatiert ist
xfs_growfs /$lv

df -hP

# hier ein besipiel um /tmp sicher zu machen
sed -i "/$lv/s/defaults/defaults,noexec/" /etc/fstab

mount -o remount /var/tmp
mount -o remount /tmp
mount | grep tmp | grep exec

# test persistence
reboot
```

# Relevante Dateien und Befehle
```
/etc/fstab
vgscan
pvcreate
vgcreate
lvcreate
mke2fs
lvextend
lvreduce
resize2fs
xfs_growfs
vgextend
vgreduce
pvmove
pvdisplay
vgdisplay
lvdisplay
pvs
vgs
lvs
```
