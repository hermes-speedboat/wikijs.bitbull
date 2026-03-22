---
title: YubiKey 5 NFC
description: getting started and howto
published: true
date: 2026-03-22T08:45:16.572Z
tags: yubikey
editor: markdown
dateCreated: 2026-03-22T08:45:16.572Z
---

# 🛡️ YubiKey 5 NFC – Getting Started Guide for Linux Mint

WARNING: This is a WIP Document, created by AI, I need to reveiw and align, be aware of bugs and false infos

## 1. Prerequisites

### Hardware

* YubiKey 5 NFC (or YubiKey 5C NFC)
* USB port on your Linux Mint system
* Optional: NFC-enabled smartphone or tablet

### Software

* Linux Mint 21.x or 22.x (Ubuntu/Debian-based)
* Administrative privileges (`sudo`)
* Internet connection for package updates

## 2. Installing Required Tools
### 2.1 Update system

```bash
sudo apt update && sudo apt upgrade -y
```

### 2.2 Install YubiKey tools

** CLI (recommended)**

```bash
sudo apt install yubikey-manager yubikey-manager-qt -y
sudo apt install pcscd scdaemon libpam-yubico fido2-tools -y
sudo apt install yubico-piv-tool -y
```

### 2.3 Start required services

```bash
sudo systemctl enable pcscd
sudo systemctl start pcscd
systemctl status pcscd
```

### 2.4 Detect YubiKey

```bash
ykman info
pcsc_scan
```

Expected output:

```
YubiKey 5 NFC detected
Serial: XXXXXXXX
Firmware: X.X.X
```

## 3. Verifying the YubiKey

```bash
ykman info
ykman verify
```

Alternatively:
[https://www.yubico.com/genuine/](https://www.yubico.com/genuine/)

## 4. Configuring PIN and Management Key

### 4.1 Change default PIN (CRITICAL)

Default PIN: `123456`

```bash
ykman otp pin --new-pin=YourSecurePIN123
```

### 4.2 Remove Management Key (recommended)

```bash
ykman piv setup --pin=YourSecurePIN123
```

### 4.3 Change PUK (optional)

```bash
ykman piv change-puk --new-puk=YourPUK1234
```

---

## 5. SSH Keys on the YubiKey (PIV)

### 5.1 Generate key in slot 9a

```bash
ykman piv generate-key 9a ed25519
# or
ykman piv generate-key 9a rsa4096
```

### 5.2 Export public key

```bash
ykman piv export-public-key 9a > ~/.ssh/id_ed25519_yubikey.pub
```

### 5.3 Upload to server

```bash
ssh-copy-id -i ~/.ssh/id_ed25519_yubikey.pub user@server
```

### 5.4 Configure SSH

`~/.ssh/config`

```bash
Host *
    IdentityFile ~/.ssh/id_ed25519_yubikey
    IdentitiesOnly yes
    PKCS11Provider /usr/lib/x86_64-linux-gnu/opensc-pkcs11.so
```

### Alternative: ssh-agent

```bash
eval $(ssh-agent -s)
ssh-add -s /usr/lib/x86_64-linux-gnu/opensc-pkcs11.so
```

### 5.5 Test connection

```bash
ssh user@server
```

## 6. GPG/PGP Keys on the YubiKey

### 6.1 Generate GPG key

```bash
gpg --full-generate-key
```

Recommended:

* RSA 4096
* Usage: Sign, Encrypt, Authenticate

### 6.2 Prepare YubiKey

```bash
gpg --card-edit
```

Commands:

```
admin
reset   # WARNING: deletes all data
pin
quit
```

### 6.3 Move key to YubiKey

```bash
gpg --edit-key YOUR_EMAIL
```

Inside prompt:

```
keytocard
```

Select:

* 1 = Signature
* 2 = Encryption
* 3 = Authentication

### 6.4 Test operations

```bash
gpg --sign file.txt
gpg --encrypt --recipient YOUR_EMAIL file.txt
gpg --decrypt file.txt.gpg
```

## 7. Two-Factor Authentication (PAM)

### 7.1 Install module

```bash
sudo apt install libpam-yubico -y
```

### 7.2 Backup configuration

```bash
sudo cp /etc/pam.d/common-auth /etc/pam.d/common-auth.backup
```

### 7.3 Edit PAM config

```bash
sudo nano /etc/pam.d/common-auth
```

Add:

```
auth optional pam_yubico.so authfile=/etc/yubico/user-authfile id=1
```

### 7.4 Create auth file

```bash
sudo nano /etc/yubico/user-authfile
```

### 7.5 Register OTP

```bash
yubico-pam-configurator
```

Or manually:

```bash
yubico-client --device=/dev/hidraw0 --mode=otp
```

### 7.6 Test login

⚠️ Always test in a new session first:

```bash
Ctrl + Alt + F2
```

## 8. Testing NFC Functionality

### 8.1 Check NFC device

```bash
ls /dev/nfc*
sudo systemctl enable nfc
sudo systemctl start nfc
```

### 8.2 Smartphone test

1. Install:

   * Yubico Authenticator (Android/iOS)
2. Hold YubiKey near phone
3. Tap button
4. OTP should appear

### 8.3 Linux NFC test

```bash
pcsc_scan
```

## 9. Security Best Practices

### 🔐 PIN Security

* Never use default PIN
* 3 failed attempts → device locked
* PUK required to unlock

### 💾 Backups

Public key:

```bash
gpg --export YOUR_EMAIL > backup-public-key.asc
```

Private key:

```bash
gpg --armor --export-secret-keys YOUR_EMAIL > backup-secret-key.asc
chmod 600 backup-secret-key.asc
```

### 🔄 Reset YubiKey

```bash
ykman reset
```

⚠️ This deletes ALL data.

### 📱 Recovery Options

* Backup YubiKey (second device)
* Offline GPG key backup
* Multiple SSH key deployments

## ⚠️ Troubleshooting

### YubiKey not detected

```bash
sudo systemctl restart pcscd
```

### PIN forgotten

```bash
ykman piv change-pin --new-pin=NEWPIN --old-puk=12345678
```

### SSH issues

```bash
echo $SSH_AUTH_SOCK
ssh-add -l
ssh-add ~/.ssh/id_ed25519_yubikey
```

## 🎯 Summary

| Function         | Status | Command                    |
|------------------|:------:|----------------------------|
| Detect YubiKey   |   ✔    | `ykman info`              |
| Change PIN       |   ✔    | `ykman otp pin`           |
| SSH Keys         |   ✔    | `ykman piv generate-key`  |
| GPG Keys         |   ✔    | `gpg --card-edit`         |
| 2FA Login        |   ✔    | `pam_yubico`              |
| NFC Test         |   ✔    | Smartphone app            |


## 📚 Resources

* [https://developers.yubico.com/](https://developers.yubico.com/)
* [https://docs.yubico.com/software/yubikey/](https://docs.yubico.com/software/yubikey/)
* [https://forums.linuxmint.com/](https://forums.linuxmint.com/)
* [https://github.com/drduh/YubiKey-Guide](https://github.com/drduh/YubiKey-Guide)


## ⚡ Quick Reference

```bash
ykman info
ykman otp pin --new-pin=NEWPIN
ykman piv generate-key 9a ed25519
ykman piv export-public-key 9a > ~/.ssh/id_ed25519_yubikey.pub
gpg --card-edit
ykman reset
```
