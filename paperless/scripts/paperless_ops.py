#!/usr/bin/env python3
"""Root-only operations for the single-host layout in ../install.md.

No third-party Python dependencies. Do not run with shell tracing enabled.
"""
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import tarfile
import time

ROOT = Path('/srv/paperless')
SERVICES = {'webserver', 'db', 'broker', 'tika', 'gotenberg'}
PARTS = ('compose', 'data', 'media', 'consume', 'export')
PAYLOADS = ('database.dump', 'files.tar.gz', 'images.json', 'media.json')


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def run(args, **kwargs):
    # Capture stderr: database/config errors can contain credentials. Do not log it.
    return subprocess.run(args, check=True, stderr=subprocess.PIPE, **kwargs)


def dc(*args, **kwargs):
    compose = ROOT / 'compose'
    primary = [compose / n for n in ('compose.yaml', 'compose.yml',
               'docker-compose.yaml', 'docker-compose.yml') if (compose / n).exists()]
    overrides = [compose / n for n in ('compose.override.yaml', 'compose.override.yml',
                 'docker-compose.override.yaml', 'docker-compose.override.yml') if (compose / n).exists()]
    require(len(primary) == 1 and len(overrides) <= 1, 'Ambiguous or missing Compose files')
    files = [item for path in primary + overrides for item in ('-f', str(path))]
    return run(['docker', 'compose', '--project-directory', str(compose),
                *files, *args], **kwargs)


def output(*args):
    return dc(*args, stdout=subprocess.PIPE).stdout.decode()


def config():
    value = json.loads(output('config', '--format', 'json'))
    require(set(value['services']) == SERVICES, 'Expected exactly the five documented services')
    volumes = value['services']['db'].get('volumes', [])
    require(any(v.get('type') == 'bind' and v.get('source') == str(ROOT / 'postgres')
                and v.get('target') == '/var/lib/postgresql' for v in volumes),
            'Expected PostgreSQL 18 bind layout')
    return value


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def save(path, data):
    path.write_text(json.dumps(data, indent=2) + '\n')


def save_compose(path, data):
    # Compose interpolates again on the next read: preserve literal dollar signs.
    path.write_text(json.dumps(data, indent=2).replace('$', '$$') + '\n')


def media_hashes():
    return {str(p.relative_to(ROOT / 'media')): digest(p)
            for p in sorted((ROOT / 'media').rglob('*')) if p.is_file()}


def free_space(path, needed):
    require(shutil.disk_usage(path).free >= needed, 'Insufficient free disk space')


def wait_stack():
    dc('up', '-d', '--no-recreate', '--wait', '--wait-timeout', '240',
       stdout=subprocess.DEVNULL, timeout=300)


def backup(destination):
    require(ROOT.is_dir(), 'Installation does not exist')
    destination = destination.resolve()
    require(not destination.is_relative_to(ROOT), 'Backup must be outside /srv/paperless')
    destination.mkdir(mode=0o700, parents=True, exist_ok=True)
    require(destination.stat().st_uid == 0 and destination.stat().st_mode & 0o077 == 0,
            'Backup parent must be root-owned and mode 0700')
    config()
    # Conservative bound: uncompressed files + twice current DB allocation + 1 GiB.
    size = sum(p.stat().st_size for part in (*PARTS, 'postgres')
               for p in (ROOT / part).rglob('*') if p.is_file())
    free_space(destination, size * 2 + 1024 ** 3)
    target = destination / time.strftime('paperless-%Y%m%dT%H%M%SZ', time.gmtime())
    target.mkdir(mode=0o700)  # Never overwrite an existing backup.
    images = {}
    for service in sorted(SERVICES):
        cid = output('ps', '-q', service).strip()
        require(cid and '\n' not in cid, 'Each service must have one running container')
        image_id = run(['docker', 'inspect', '--format', '{{.Image}}', cid],
                       stdout=subprocess.PIPE).stdout.decode().strip()
        refs = json.loads(run(['docker', 'image', 'inspect', '--format',
                               '{{json .RepoDigests}}', image_id],
                              stdout=subprocess.PIPE).stdout)
        require(refs, 'Running image lacks a repository digest')
        images[service] = refs[0]
    save(target / 'images.json', images)
    stopped = False
    try:
        # Set before stop: even a partial stop must trigger a restart attempt.
        stopped = True
        dc('stop', '-t', '120', 'webserver', stdout=subprocess.DEVNULL)
        with (target / 'database.dump').open('wb') as stream:
            dc('exec', '-T', 'db', 'pg_dump', '-U', 'paperless', '-Fc', 'paperless', stdout=stream)
        with (target / 'database.dump').open('rb') as stream:
            dc('exec', '-T', 'db', 'pg_restore', '--list', stdin=stream,
               stdout=subprocess.DEVNULL)
        run(['tar', '--selinux', '--xattrs', '-czf', str(target / 'files.tar.gz'),
             '-C', str(ROOT.parent), *['paperless/' + p for p in PARTS]], stdout=subprocess.DEVNULL)
        save(target / 'media.json', media_hashes())
        save(target / 'SHA256SUMS.json', {name: digest(target / name) for name in PAYLOADS})
    finally:
        if stopped:
            # Failure propagates; never report a successful backup on restart failure.
            dc('start', 'webserver', stdout=subprocess.DEVNULL, timeout=120)
            wait_stack()
    (target / 'SUCCESS').write_text('Backup completed; application restart passed.\n')
    print('Backup:', target)
    return target


def validate_backup(source):
    require((source / 'SUCCESS').is_file(), 'Backup has no SUCCESS marker')
    checks = json.loads((source / 'SHA256SUMS.json').read_text())
    require(set(checks) == set(PAYLOADS), 'Unexpected checksum manifest')
    for name in PAYLOADS:
        require(digest(source / name) == checks[name], 'Backup checksum mismatch: ' + name)
    images = json.loads((source / 'images.json').read_text())
    require(set(images) == SERVICES, 'Incomplete service-to-digest mapping')
    require(all(re.fullmatch(r'[a-zA-Z0-9./:_-]+@sha256:[a-f0-9]{64}', v)
                for v in images.values()), 'Invalid immutable image reference')
    require(images['db'].split('@')[0].split('/')[-1].split(':')[0] == 'postgres',
            'Expected PostgreSQL image')
    # Never extract special files, symlinks, hardlinks or paths outside the layout.
    with tarfile.open(source / 'files.tar.gz') as archive:
        members = archive.getmembers()
        for member in members:
            parts = Path(member.name).parts
            require(not member.name.startswith('/') and '..' not in parts and
                    len(parts) >= 2 and parts[0] == 'paperless' and parts[1] in PARTS and
                    (member.isfile() or member.isdir()), 'Unsafe archive member')
        return images, sum(m.size for m in members)


def restore(source, production, url):
    source = source.resolve()
    images, size = validate_backup(source)
    # Stronger than checking db alone: never overlay any existing installation.
    require(not ROOT.is_symlink() and (not ROOT.exists() or
            (ROOT.is_dir() and not any(ROOT.iterdir()))),
            'Restore requires absent or completely empty /srv/paperless (including db/postgres)')
    free_space(ROOT.parent, size * 2 + (source / 'database.dump').stat().st_size * 4 + 1024 ** 3)
    for image in images.values():
        run(['docker', 'pull', image], stdout=subprocess.DEVNULL)
    version = run(['docker', 'run', '--rm', '--network', 'none', '--entrypoint', 'postgres',
                   images['db'], '--version'], stdout=subprocess.PIPE).stdout.decode()
    require(re.search(r'PostgreSQL\) 18\.', version), 'This restore supports PostgreSQL 18 only')
    run(['tar', '--selinux', '--xattrs', '-xzf', str(source / 'files.tar.gz'),
         '-C', str(ROOT.parent)], stdout=subprocess.DEVNULL)
    started = False
    try:
        cfg = config()
        for name, service in cfg['services'].items():
            service['image'] = images[name]
            require(not service.get('network_mode') and not service.get('privileged'),
                    'Unsupported networking or privileged service')
            require(set(service.get('networks', {'default': None})) == {'default'},
                    'Only the default network is supported')
        require(set(cfg.get('networks', {})) == {'default'}, 'Unexpected networks')
        cfg['networks'] = {'default': {'internal': not production}}
        if not production:
            cfg['services']['webserver'].setdefault('environment', {})['PAPERLESS_URL'] = url
        # Rendered recovery config becomes the sole default config, with immutable images.
        # Preserve original files for diagnostics without allowing automatic override merging.
        compose = ROOT / 'compose'
        for name in ('compose.yaml', 'compose.yml', 'docker-compose.yaml', 'docker-compose.yml',
                     'compose.override.yaml', 'compose.override.yml',
                     'docker-compose.override.yaml', 'docker-compose.override.yml'):
            path = compose / name
            if path.exists():
                path.rename(compose / (name + '.pre-restore'))
        save_compose(compose / 'compose.yaml', cfg)  # JSON is valid YAML.
        require(not output('ps', '--all', '-q').strip(),
                'Recovery project already has containers; use a fresh host')
        for name, uid in (('postgres', 999), ('valkey', 0)):
            path = ROOT / name
            path.mkdir(mode=0o750)
            os.chown(path, uid, uid)
        require(media_hashes() == json.loads((source / 'media.json').read_text()),
                'Restored media hash inventory differs')
        started = True
        dc('up', '-d', 'db', 'broker', 'tika', 'gotenberg', stdout=subprocess.DEVNULL)
        for attempt in range(60):
            try:
                dc('exec', '-T', 'db', 'pg_isready', '-U', 'paperless',
                   stdout=subprocess.DEVNULL, timeout=5)
                break
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                time.sleep(2)
        else:
            raise RuntimeError('PostgreSQL readiness timeout')
        if not production:
            cid = output('ps', '-q', 'db').strip()
            networks = json.loads(run(['docker', 'inspect', '--format',
                '{{json .NetworkSettings.Networks}}', cid], stdout=subprocess.PIPE).stdout)
            require(len(networks) == 1, 'Unexpected attached networks')
            for network in networks:
                internal = run(['docker', 'network', 'inspect', '--format', '{{.Internal}}', network],
                               stdout=subprocess.PIPE).stdout.decode().strip()
                require(internal == 'true', 'Restore network is not internal')
        with (source / 'database.dump').open('rb') as stream:
            dc('exec', '-T', 'db', 'pg_restore', '-U', 'paperless', '-d', 'paperless',
               '--exit-on-error', stdin=stream, stdout=subprocess.DEVNULL)
        wait_stack()
        dc('exec', '-T', 'webserver', 'document_index', 'reindex', stdout=subprocess.DEVNULL)
    except BaseException:
        if started:
            try:
                dc('stop', stdout=subprocess.DEVNULL, timeout=150)
            except Exception:
                print('WARNING: stop failed; manually stop the recovery stack.', file=sys.stderr)
        print('Restore failed; files and database retained for diagnosis. Do not rerun over them.', file=sys.stderr)
        raise
    print('Restore completed. Application-level recovery checks are still required.')


def upgrade(version, destination):
    require(re.fullmatch(r'[0-9]+\.[0-9]+\.[0-9]+', version), 'Use an explicit stable version, e.g. 3.3.4')
    before = config()
    backup_path = backup(destination)
    image = 'ghcr.io/paperless-ngx/paperless-ngx:' + version
    run(['docker', 'pull', image], stdout=subprocess.DEVNULL)
    refs = json.loads(run(['docker', 'image', 'inspect', '--format', '{{json .RepoDigests}}', image],
                         stdout=subprocess.PIPE).stdout)
    require(refs, 'New image has no immutable digest')
    # Keep every setting unchanged except the Paperless image. Preserve the originals.
    compose = ROOT / 'compose'
    candidate = compose / 'upgrade-candidate.json'
    require(not candidate.exists(), 'Resolve existing upgrade-candidate.json before retrying')
    before['services']['webserver']['image'] = refs[0]
    save_compose(candidate, before)
    # Explicit file avoids automatic merging of the old overrides during this check.
    run(['docker', 'compose', '-f', str(candidate), 'config', '--quiet'], stdout=subprocess.DEVNULL)
    print('Recovery backup:', backup_path)
    try:
        run(['docker', 'compose', '-f', str(candidate), 'up', '-d', '--no-deps',
             '--wait', '--wait-timeout', '240', 'webserver'], stdout=subprocess.DEVNULL, timeout=300)
    except BaseException:
        print('Upgrade failed: do NOT roll back only the image after migrations. '
              'Restore the printed backup on a fresh host; candidate retained.', file=sys.stderr)
        raise
    for name in ('compose.yaml', 'compose.yml', 'docker-compose.yaml', 'docker-compose.yml',
                 'compose.override.yaml', 'compose.override.yml',
                 'docker-compose.override.yaml', 'docker-compose.override.yml'):
        path = compose / name
        if path.exists():
            path.rename(compose / (name + '.pre-upgrade-' + version))
    candidate.rename(compose / 'compose.yaml')
    print('Upgrade healthy; verify login, search, preview and consumption before accepting it.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='action', required=True)
    p = sub.add_parser('backup', help='Quiesce workers and save a consistent backup')
    p.add_argument('--destination', type=Path, default=Path('/srv/backup'))
    p = sub.add_parser('restore', help='Restore a trusted backup onto a fresh host')
    p.add_argument('backup', type=Path)
    p.add_argument('--trusted-backup', action='store_true', required=True,
                   help='Confirm provenance; checksums do not authenticate an archive')
    p.add_argument('--production', action='store_true', help='Allow external networking explicitly')
    p.add_argument('--test-url', default='http://localhost:8000')
    p = sub.add_parser('upgrade', help='Backup first, then change only the Paperless image')
    p.add_argument('version')
    p.add_argument('--destination', type=Path, default=Path('/srv/backup'))
    args = parser.parse_args()
    require(os.geteuid() == 0, 'Run as root')
    os.umask(0o077)
    def interrupted(signum, _frame):
        raise SystemExit(128 + signum)
    signal.signal(signal.SIGTERM, interrupted)
    signal.signal(signal.SIGHUP, interrupted)
    # Do not honor environment-based Compose file/project overrides.
    for name in tuple(os.environ):
        if name.startswith('COMPOSE_'):
            del os.environ[name]
    with open('/run/lock/paperless-operations.lock', 'w') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise RuntimeError('Another Paperless operation holds the lock') from None
        if args.action == 'backup':
            backup(args.destination)
        elif args.action == 'restore':
            restore(args.backup, args.production, args.test_url)
        else:
            upgrade(args.version, args.destination)


if __name__ == '__main__':
    try:
        main()
    except subprocess.SubprocessError:
        # Do not echo argv/stderr: rendered environment and DB errors may hold secrets.
        print('External command failed. Inspect local service state/logs privately.', file=sys.stderr)
        sys.exit(1)
    except (RuntimeError, OSError, ValueError, tarfile.TarError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
