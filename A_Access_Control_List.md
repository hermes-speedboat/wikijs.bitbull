---
title: Access Control List
description: Reference card for Linux ACLs
published: true
date: 2026-01-07T00:00:00.000Z
tags: referencecards, acl, linux
editor: markdown
dateCreated: 2026-01-07T00:00:00.000Z
---

# Install

## Software

**RedHat based System:**
```bash
yum install acl
```
**Debian based System:**
```bash
apt-get install acl
```

## File System

Edit `/etc/fstab`:
```bash
vi /etc/fstab
# Example entry:
# /dev/sdb1   /srv/nfs/data   ext4   rw,acl   1 2
```
Mount and verify:
```bash
mount -a
mount | grep acl
# /dev/sdb1 on /srv/nfs/data type ext4 (rw,acl)
```

# Understand ACLs

## Read ACL Rules

```bash
touch notes.txt
ls -l notes.txt
# -rw-r--r-- 1 root root 0 Jun 29 06:33 notes.txt
setfacl -m u:joe:r-- -m u:tom:rw- -m u:mike:r-- notes.txt
ls -l notes.txt
# -rw-rw-r--+ 1 root root 0 Jun 29 06:33 notes.txt
getfacl notes.txt
# file: notes.txt
# owner: root
# group: root
user::rw-
user:joe:r--
user:tom:rw-
user:mike:r--
group::r--
mask::rw-
other::r--
```

# Understand ACL Rules

## Access ACL

### Mask

This is the effective rights mask. This entry limits the effective rights granted to all ACL groups and ACL users. The traditional Unix User, Group, and Other entries are not affected. If the mask is more restrictive than the ACL permissions that you grant, then the mask takes precedence.

```bash
rm -f notes.txt
touch notes.txt
setfacl  -m u:tom:rwx  notes.txt
su tom -c "echo 12345678 > notes.txt"
getfacl notes.txt
# file: notes.txt
# owner: root
# group: root
user::rw-
user:tom:rwx
group::r--
mask::rwx
other::r--

setfacl -m mask::r-- notes.txt
su tom -c "echo 12345678 > notes.txt"
# bash: notes.txt: Permission denied
getfacl notes.txt
# file: notes.txt
# owner: root
# group: root
user::rw-
user:tom:rwx            #effective:r--
group::r--
mask::r--
other::r--
```

> **Note:** Whenever you change the permissions of a user or a group with setfacl, the mask is changed to match. Therefore, if you want a restrictive mask, it must be applied after the user and group permissions are modified.

# Default ACL

There is also another type of ACL, called the default ACL. The default ACL is only applied to directories, and it defines the permissions that a newly created file or directory inherits from its parent directory.

When you create a new directory inside a directory that already has a default ACL, the new directory inherits the default ACL both as its access ACL and its default ACL.

Here is an example of defining a default ACL for a directory, and what happens when files and directories are created underneath that directory:

```bash
mkdir secret
setfacl -m u:joe:rwx,u:chris:rwx,o::- secret
getfacl secret
# file: secret
# owner: root
# group: root
user::rwx
user:chris:rwx
user:joe:rwx
group::r-x
mask::rwx
other::---

echo "server1:admin:t0ta1." > secret/passwords-1.txt
getfacl secret/passwords-1.txt
# file: secret/passwords-1.txt
# owner: root
# group: root
user::rw-
group::r--
other::r--

setfacl -d -m u:joe:rwx,u:chris:rwx,o::- secret
getfacl secret
# file: secret
# owner: root
# group: root
user::rwx
user:chris:rwx
user:joe:rwx
group::r-x
mask::rwx
other::---
default:user::rwx
default:user:chris:rwx
default:user:joe:rwx
default:group::r-x
default:mask::rwx
default:other::---

echo "server1:admin:t0ta1." > secret/passwords-2.txt
getfacl secret/passwords-2.txt
# file: secret/passwords-2.txt
# owner: root
# group: root
user::rw-
user:chris:rwx            #effective:rw-
user:joe:rwx              #effective:rw-
group::r-x                #effective:r--
mask::rw-
other::---

mkdir secret/test
getfacl secret/test
# file: secret/test
# owner: root
# group: root
user::rwx
user:chris:rwx
user:joe:rwx
group::r-x
mask::rwx
other::---
default:user::rwx
default:user:chris:rwx
default:user:joe:rwx
default:group::r-x
default:mask::rwx
default:other::---
```

# Examples

- **Remove Specific Entries from an ACL**
    ```bash
    setfacl -x u:tom,u:joe notes.txt
    ```
- **Remove Entire ACL**
    ```bash
    setfacl -b notes.txt
    ```
- **Replace all existing ACL rules and apply this one**
    ```bash
    setfacl --set u:tom,u:joe notes.txt
    ```
- **Using setfacl Recursively**
    ```bash
    setfacl -PRx u:joe ./
    # -P -> don't follow SymLinks !!!
    ```
- **Backup/Restore ACL Rules**
    > May break sticky bit and set guid bit
    ```bash
    getfacl -R . >acl.txt
    setfacl --restore acl.txt
    getfacl -R $(ls -d /* | egrep -v 'dev|proc|selinux|sys|lost+') > /etc/acl.txt
    ```
- **Copy ACL's from existing file/directory**
    ```bash
    getfacl bingo.txt | setfacl --set-file=- test*
    ```
- **Backup/Restore data and ACL rules**
    ```bash
    star -Hexustar -acl -c f=Tree.star Tree
    star -acl -x f=Tree.star
    # rdiff-backup also supports ACL
    ```
