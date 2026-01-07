---
title: Apache Reverse Proxy with Basic Auth
description: Apache 2.4 configuration example for Webmin behind a reverse proxy with Basic Auth
published: true
tags: security
editor: markdown
dateCreated: 2026-01-07
---

* Apache 2.4
* Webmin behind reverse proxy

Edit `/etc/httpd/conf.d/webmin.conf`:

```apache
Listen 443 https

SSLPassPhraseDialog exec:/usr/libexec/httpd-ssl-pass-dialog
SSLSessionCache         shmcb:/run/httpd/sslcache(512000)
SSLSessionCacheTimeout  300
SSLRandomSeed startup file:/dev/urandom  256
SSLRandomSeed connect builtin
SSLCryptoDevice builtin

<VirtualHost _default_:50443>
DocumentRoot /srv/www/html
ServerName www.domain.com

<Proxy *>
    AuthType Basic
    AuthName "Restricted Access"
    AuthBasicProvider file
    AuthUserFile "/srv/www/htpasswd"
    Require valid-user
</Proxy>

ErrorLog /srv/www/logs/ssl_error_log
TransferLog /srv/www/logs/ssl_access_log
LogLevel warn
SSLEngine on
ProxyPreserveHost On
ProxyRequests Off
SSLProxyEngine On
SSLProxyCheckPeerCN off
SSLProxyCheckPeerName off
SSLProtocol all -SSLv2
SSLCipherSuite HIGH:MEDIUM:!aNULL:!MD5:!SEED:!IDEA
SSLCertificateFile /etc/pki/tls/certs/localhost.crt
SSLCertificateKeyFile /etc/pki/tls/private/localhost.key
    ProxyPass / https://localhost:10000/
    ProxypassReverse / https://localhost:10000/
</VirtualHost>
```
