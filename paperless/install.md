---
title: Install Paperless-ngx
description: Paperless-ngx on Rocky Linux 10 with Docker Compose, HTTPS, backup and restore
published: true
date: 2026-10-21T11:54:50.000Z
tags: paperless, docker, rocky, backup
editor: markdown
dateCreated: 2026-10-21T11:54:50.000Z
---

# Paperless-ngx

## Outline

Single Rocky Linux 10 host, Docker Compose and local Paperless users. PostgreSQL stores metadata, Valkey handles the task queue, Tika extracts Office document content, and Gotenberg converts documents to PDF. nginx terminates HTTPS; Paperless listens on loopback only.

Reference versions: Paperless **3.3.3**, PostgreSQL **18**, Valkey **9-alpine**, Tika **3.3.1.0**, Gotenberg **8.37**. Use the official Compose files from the same Paperless release, not a mixture of release and development templates.

- Start with 4 vCPU, 8 GB RAM and at least 50 GB disk; size document storage separately.
- Local XFS or ext4 under `/srv/paperless`; keep adequate space for imports, PDF conversion and backups.
- Example hostname: `paperless.example.net`. Replace it throughout.
- Only HTTPS is exposed. No SSO or external database/broker ports.
- Commands below run as root. Take a VM snapshot before updating an existing host; do not overwrite an existing Paperless installation.

## Setup

### Docker and storage

Check OS, mounts and existing runtimes before installation:

```bash
hostname -f
cat /etc/os-release
findmnt -T /srv
df -hT /srv
rpm -q docker-ce podman

dnf update -y
dnf install -y dnf-plugins-core curl openssl tar nginx policycoreutils-python-utils
dnf config-manager --add-repo https://download.docker.com/linux/rhel/docker-ce.repo
dnf install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
systemctl enable --now docker
docker version
docker compose version

install -d -m 0750 /srv/paperless/{compose,data,media,consume,export,postgres,valkey}
chown 1000:1000 /srv/paperless/{data,media,consume,export}
# UID/GID used by the reference PostgreSQL image; verify when changing images.
chown 999:999 /srv/paperless/postgres
```

Resolve conflicting runtimes before proceeding. Verify Docker's repository signing key against its official installation documentation. Schedule any required reboot separately.

### Official Compose files

On a fresh installation:

```bash
cd /srv/paperless/compose
umask 077
VERSION=v3.3.3
BASE="https://raw.githubusercontent.com/paperless-ngx/paperless-ngx/$VERSION/docker/compose"
curl -fSL "$BASE/docker-compose.postgres-tika.yml" -o docker-compose.yml
curl -fSL "$BASE/docker-compose.env" -o docker-compose.env
curl -fSL "$BASE/.env" -o .env
printf '%s\n%s\n' "$VERSION" "$BASE" > INSTALLATION-VERSION.txt
```

Edit the downloaded template, keeping its service definitions and Gotenberg security options:

- Pin the webserver image to `ghcr.io/paperless-ngx/paperless-ngx:3.3.3`.
- Change the webserver port mapping to `127.0.0.1:8000:8000`.
- Replace `POSTGRES_PASSWORD: paperless` with `POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:?required}`.
- Replace the volume sources with the paths below; append `:Z` to each bind mount. Remove the unused top-level named `volumes` section.

| Service | Host path | Container path |
| --- | --- | --- |
| webserver | `/srv/paperless/data` | `/usr/src/paperless/data` |
| webserver | `/srv/paperless/media` | `/usr/src/paperless/media` |
| webserver | `/srv/paperless/consume` | `/usr/src/paperless/consume` |
| webserver | `/srv/paperless/export` | `/usr/src/paperless/export` |
| db | `/srv/paperless/postgres` | `/var/lib/postgresql` |
| broker | `/srv/paperless/valkey` | `/data` |

PostgreSQL 18 uses a versioned subdirectory beneath `/var/lib/postgresql`; do not substitute an older image's mount layout.

Generate secrets directly into the fresh environment files, without printing them:

```bash
python3 - <<'PY'
from pathlib import Path
import secrets
p = Path('docker-compose.env')
s = p.read_text()
assert 'PAPERLESS_SECRET_KEY=change-me' in s
password = secrets.token_hex(32)
s = s.replace('PAPERLESS_SECRET_KEY=change-me',
              'PAPERLESS_SECRET_KEY=' + secrets.token_hex(32))
s += '\nPAPERLESS_DBPASS=' + password + '\n'
p.write_text(s)
with Path('.env').open('a') as f:
    f.write('\nPOSTGRES_PASSWORD=' + password + '\n')
PY
chmod 0600 .env docker-compose.env
```

Set these additional values in `docker-compose.env`:

```ini
USERMAP_UID=1000
USERMAP_GID=1000
PAPERLESS_URL=https://paperless.example.net
PAPERLESS_TIME_ZONE=Europe/Zurich
PAPERLESS_OCR_LANGUAGE=deu+eng
```

The official Tika template already sets `PAPERLESS_TIKA_ENABLED`, `PAPERLESS_TIKA_ENDPOINT` and `PAPERLESS_TIKA_GOTENBERG_ENDPOINT`. Do not publish Tika or Gotenberg ports. Keep the template's Chromium JavaScript restriction and file-only allow-list.

```bash
docker compose config --quiet
docker compose pull
docker compose up -d --wait --wait-timeout 240
docker compose ps
docker compose exec webserver createsuperuser
```

Enter the administrator password interactively. Avoid plain `docker compose config` in logs: its rendered output contains secrets. Keep SELinux enforcing; investigate AVCs and bind-mount ownership if a service fails.

### HTTPS

Example: self-signed backend certificate for HAProxy re-encryption. Import the certificate into HAProxy's backend trust store and verify the backend hostname; do not use `verify none`. A ten-year certificate still needs expiry monitoring and planned rotation.

```bash
install -d -m 0700 /etc/pki/paperless
umask 077
openssl req -x509 -newkey rsa:3072 -sha256 -nodes -days 3652 \
  -keyout /etc/pki/paperless/server.key \
  -out /etc/pki/paperless/server.crt \
  -subj '/CN=paperless.example.net' \
  -addext 'subjectAltName=DNS:paperless.example.net'
```

Create `/etc/nginx/conf.d/paperless.conf`:

```nginx
server {
    listen 443 ssl;
    server_name paperless.example.net;
    ssl_certificate /etc/pki/paperless/server.crt;
    ssl_certificate_key /etc/pki/paperless/server.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    client_max_body_size 100m;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto https;
        proxy_set_header X-Forwarded-For $remote_addr;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 300s;
    }
}
```

Disable nginx's default port-80 server or bind it to loopback. The example deliberately does not trust incoming forwarded client-IP headers. If required, configure nginx real-IP handling only for the known HAProxy addresses.

```bash
setsebool -P httpd_can_network_connect on
restorecon -RF /etc/nginx /etc/pki/paperless
nginx -t
systemctl enable --now nginx
firewall-cmd --add-service=https
# Verify HTTPS from another host before persisting the firewall change.
firewall-cmd --permanent --add-service=https
curl --cacert /etc/pki/paperless/server.crt \
  --resolve paperless.example.net:443:127.0.0.1 -I https://paperless.example.net
```

A redirect to the local login page is expected. Then test browser login, PDF/image upload, OCR search and a DOCX import through `consume`. Confirm the original, PDF preview and thumbnail. Test a non-administrative user's permissions and repeat the checks after a controlled Compose restart.

## Maintenance

```bash
cd /srv/paperless/compose
docker compose ps
docker compose logs --since=1h --tail=100 webserver db broker tika gotenberg
df -h /srv/paperless
docker system df
```

For upgrades: read release notes, take and verify a backup, record current image digests, then pin the new Paperless release. Keep PostgreSQL major upgrades separate.

```bash
docker compose config --quiet
docker compose pull
docker compose up -d --wait --wait-timeout 240
```

Verify login, search, document preview and consumption. Rollback after a schema migration requires the matching database/files backup and old application image, not just changing the image tag. Never use `docker compose down -v`.

### Backup

Back up PostgreSQL, configuration and document files as one consistent set. Stop the webserver service briefly: it also runs the consumer and workers. Let current imports finish first. Valkey is not a substitute for the database backup.

Run this as a **saved Bash script**, not by piping it into an interactive remote shell:

```bash
#!/bin/bash
set -Eeuo pipefail
umask 077
cd /srv/paperless/compose
install -d -m 0700 /srv/backup
BACKUP=/srv/backup/paperless-$(date +%Y%m%d%H%M%S)
install -d -m 0700 "$BACKUP"
df -h /srv/backup
trap 'docker compose start webserver' EXIT
docker compose stop webserver
docker compose exec -T db pg_dump -U paperless -Fc paperless > "$BACKUP/database.dump"
tar --selinux --xattrs -czf "$BACKUP/files.tar.gz" -C /srv \
  paperless/compose paperless/data paperless/media paperless/consume paperless/export
docker compose exec -T db pg_restore --list < "$BACKUP/database.dump" > "$BACKUP/database-index.txt"
(cd "$BACKUP" && sha256sum database.dump files.tar.gz > SHA256SUMS)
docker compose start webserver
trap - EXIT
docker compose up -d --wait --wait-timeout 180
```

Protect the backup parent directory as root-only. The archive contains secrets and documents: use an approved encrypted backup destination with retention, access control and failure/age monitoring. `/srv/backup` is local staging, **not protection against disk loss**. Include nginx configuration and TLS material in the encrypted host backup.

For a separate portable document export:

```bash
docker compose exec -T webserver document_exporter ../export
```

This is an additional recovery route; validate its import independently. Do not assume it is equivalent to a full database/files restore, especially for deleted documents and application state.

### Restore

Use a fresh host with the same application images and PostgreSQL major version. Install Docker first. Do not restore over a running production instance.

1. Transfer the backup through an encrypted channel and check `sha256sum -c SHA256SUMS`.
2. Extract the archive under `/srv`, retaining ownership and permissions.
3. Create fresh PostgreSQL and Valkey directories.
4. Start PostgreSQL, restore the database, then start Paperless.

```bash
# BACKUP points to the transferred, verified backup directory.
tar --selinux --xattrs -xzf "$BACKUP/files.tar.gz" -C /srv
install -d -m 0750 -o 999 -g 999 /srv/paperless/postgres
install -d -m 0750 /srv/paperless/valkey
cd /srv/paperless/compose
```

**Before starting a test copy**, prevent it from reaching production mail servers, webhooks and external services. Change `PAPERLESS_URL` to the test URL and add this top-level Compose section:

```yaml
networks:
  default:
    internal: true
```

Pull images before starting the isolated stack. Do not connect another external Docker network. Check that no copied automation can act on production data.

```bash
docker compose config --quiet
docker compose pull
docker compose up -d db broker tika gotenberg
docker compose exec -T db pg_isready -U paperless
# Wait for PostgreSQL readiness before continuing.
docker compose exec -T db pg_restore -U paperless -d paperless \
  --exit-on-error < "$BACKUP/database.dump"
docker compose up -d --wait --wait-timeout 240
docker compose exec -T webserver document_index reindex
```

Verify users, tags, mail rules, document counts **including the trash**, and original/archive/thumbnail files. Check file hashes against the captured source manifest if available. Test real password login, document download, PDF preview and indexed search; repeat after restarting Paperless. Restore trash documents only in the test copy when needed for validation.

An internal Docker network may not expose the configured published port. Inspect the webserver container IP and tunnel directly to it:

```bash
docker inspect paperless-webserver-1 --format '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}'
# On your workstation, substitute the returned address:
ssh -N -L 8000:CONTAINER_IP:8000 root@restore.example.net
```

Open `http://localhost:8000` with that URL configured in the test environment. Retain the isolated VM until review is complete, then remove it and its copied credentials. A production recovery additionally requires restoring HTTPS configuration and validating the real access path.

## Hints and links

- `db:5432 - no response`: check database logs and PostgreSQL bind-directory ownership before blaming networking.
- SELinux failures: inspect `ausearch -m AVC -ts recent -i`; keep labels and policy correct rather than disabling enforcement.
- A healthy container or HTTP 302 does not prove login, OCR, search or restore correctness.
- Compare restores against the captured backup, not a source instance that is still receiving changes.
- Keep the public URL consistent through HAProxy, nginx and `PAPERLESS_URL`.

[Paperless setup](https://docs.paperless-ngx.com/setup/)
[Official Compose templates](https://github.com/paperless-ngx/paperless-ngx/tree/v3.3.3/docker/compose)
[Configuration](https://docs.paperless-ngx.com/configuration/)
[Administration, backup and updates](https://docs.paperless-ngx.com/administration/)
[Docker on RHEL](https://docs.docker.com/engine/install/rhel/)
