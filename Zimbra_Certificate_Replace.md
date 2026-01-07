---
title: Zimbra SSL Cert Replace
description: How to replace SSL certificates in Zimbra
published: true
date: 2026-01-07T00:00:00.000Z
tags: linux, zimbra
editor: markdown
dateCreated: 2026-01-07T00:00:00.000Z
---

# Zimbra SSL Cert Replace

## Links
- https://www.ssls.com/knowledgebase/how-to-install-an-ssl-certificate-on-zimbra/
- https://www.digicert.com/kb/csr-creation-ssl-installation-zimbra.htm
- https://www.digicert.com/kb/ssl-support/pem-ssl-creation.htm
- https://www.bitbull.ch/wiki/index.php/Openssl_Notes

## Download Certificate (just valid for acme)
- https://www.thesslstore.com/
- My Orders > Total Orders > "latest order with active status" > Download Certificate
- Server Platform: nginx / File Type: Individual .crts (zipped) -> star_acme.com.pem file

## Backup current certificates
```bash
backup /opt/zimbra/ssl/zimbra/commercial
'/opt/zimbra/ssl/zimbra/commercial' -> '/opt/zimbra/ssl/zimbra/commercial.202306110657'
'/opt/zimbra/ssl/zimbra/commercial/commercial_ca.crt' -> '/opt/zimbra/ssl/zimbra/commercial.202306110657/commercial_ca.crt'
'/opt/zimbra/ssl/zimbra/commercial/commercial.crt' -> '/opt/zimbra/ssl/zimbra/commercial.202306110657/commercial.crt'
'/opt/zimbra/ssl/zimbra/commercial/commercial.key' -> '/opt/zimbra/ssl/zimbra/commercial.202306110657/commercial.key'
'/opt/zimbra/ssl/zimbra/commercial/commercial.csr' -> '/opt/zimbra/ssl/zimbra/commercial.202306110657/commercial.csr'
```

## Verify current Certificate
```bash
/opt/zimbra/bin/zmcertmgr verifycrt comm
# Output:
# ** Verifying '/opt/zimbra/ssl/zimbra/commercial/commercial.crt' against '/opt/zimbra/ssl/zimbra/commercial/commercial.key'
# Certificate '/opt/zimbra/ssl/zimbra/commercial/commercial.crt' and private key '/opt/zimbra/ssl/zimbra/commercial/commercial.key' match.
# ** Verifying '/opt/zimbra/ssl/zimbra/commercial/commercial.crt' against '/opt/zimbra/ssl/zimbra/commercial/commercial_ca.crt'
# Valid certificate chain: /opt/zimbra/ssl/zimbra/commercial/commercial.crt: OK

openssl verify -CAfile /opt/zimbra/ssl/zimbra/commercial/commercial_ca.crt /opt/zimbra/ssl/zimbra/commercial/commercial.crt
# Output: /opt/zimbra/ssl/zimbra/commercial/commercial.crt: OK

cd /tmp
wget https://raw.githubusercontent.com/joe-speedboat/linux.scripts/master/shell/openssl_check_cert_chain.sh

bash openssl_check_cert_chain.sh /opt/zimbra/ssl/zimbra/commercial/commercial.crt 
# Output: (shows certificate chain and OK status)

openssl x509 -in /opt/zimbra/ssl/zimbra/commercial/commercial.crt -text -noout | head
# Output: Certificate details
```

## Prepare new Certificate
Create/Edit these three files:
- `/opt/zimbra/ssl/zimbra/commercial/commercial_ca.crt`  
  *ca chain without server certificate*
- `/opt/zimbra/ssl/zimbra/commercial/commercial.crt`  
  *server certificate (note that old certs above had ca included, which is wrong but no show stopper)*
- `/opt/zimbra/ssl/zimbra/commercial/commercial.key`  
  *private key*

## Verify new Certificate
```bash
bash /tmp/openssl_check_cert_chain.sh /opt/zimbra/ssl/zimbra/commercial/commercial_ca.crt 
# Output: (shows CA chain and OK status)

cat /opt/zimbra/ssl/zimbra/commercial/commercial.crt /opt/zimbra/ssl/zimbra/commercial/commercial_ca.crt > /tmp/tmp.crt
bash /tmp/openssl_check_cert_chain.sh /tmp/tmp.crt 
# Output: (shows full chain and OK status)

openssl x509 -in /opt/zimbra/ssl/zimbra/commercial/commercial.crt -text -noout | head
# Output: Certificate details

su - zimbra
cd /opt/zimbra/ssl/zimbra/commercial/
zmcertmgr verifycrt comm commercial.key commercial.crt commercial_ca.crt
# Output:
# ** Verifying 'commercial.crt' against 'commercial.key'
# Certificate 'commercial.crt' and private key 'commercial.key' match.
# ** Verifying 'commercial.crt' against 'commercial_ca.crt'
# Valid certificate chain: commercial.crt: OK
```

## Deploy new Certificates
```bash
su - zimbra
cd /opt/zimbra/ssl/zimbra/commercial/
zmcertmgr verifycrt comm commercial.key commercial.crt commercial_ca.crt
# Output: (see above)

zmcertmgr deploycrt comm commercial.crt commercial_ca.crt
# ...watch out for any errors

zmcertmgr viewdeployedcrt
# Output: Shows deployed certificates for imapd, ldap, mailboxd, mta, proxy, with notBefore/notAfter, subject, issuer, SubjectAltName

zmcontrol restart
# Output: Service restart output
```
