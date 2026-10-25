"""Read-only status/CLI contract tests; Docker is mocked, never modified."""
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

from test_operations import ops


class Status(unittest.TestCase):
    def setUp(self):
        self.configured = set(ops.SERVICES)
        self.ids = {s: s.encode() for s in ops.SERVICES}
        self.states = {s: b'running absent' for s in ops.SERVICES}
        self.inject_failure = None
        self.pong = b'PONG\n'
        self.calls = []

    def fake(self, args, **kwargs):
        self.calls.append(args)
        self.assertEqual(kwargs['timeout'], 3)
        self.assertEqual(kwargs['stdin'], subprocess.DEVNULL)
        self.assertFalse(any(k.startswith('COMPOSE_') for k in kwargs['env']))
        if self.inject_failure:
            self.inject_failure(args)
        if args[:2] == ['docker', 'inspect']:
            data = self.states[args[-1]]
        elif args[:2] == ['docker', 'exec']:
            self.assertIn(args[3], ('pg_isready', 'valkey-cli', 'python3'))
            data = self.pong if 'valkey-cli' in args else b''
        elif args == ['config', '--services']:
            data = '\n'.join(sorted(self.configured)).encode()
        elif args[:3] == ['ps', '--all', '-q']:
            data = self.ids[args[-1]]
        else:
            self.fail_test(args)
        return subprocess.CompletedProcess(args, 0, data)

    def fail_test(self, args):
        self.fail('Unexpected/mutating command: ' + repr(args))

    def check(self, expected=1):
        output = io.StringIO()
        with patch.object(ops, 'dc', side_effect=lambda *a, **kw: self.fake(list(a), **kw)), \
                patch.object(ops, 'run', side_effect=self.fake), \
                patch.object(ops.sys, 'stdout', output), \
                patch.dict(os.environ, {'COMPOSE_FILE': '/not/used'}):
            self.assertEqual(ops.status(True, 3), expected)
        self.assertNotIn('PRIVATE_SECRET', output.getvalue())
        return json.loads(output.getvalue())

    def test_absent_healthcheck_requires_successful_probes(self):
        report = self.check(0)
        self.assertTrue(report['healthy'])
        self.assertEqual(len(self.calls), 16)
        self.assertTrue(all(s['docker_health'] == 'absent' and s['probe'] == 'passed'
                            for s in report['services'].values()))

    def test_docker_health_states(self):
        for health in ('healthy', 'unhealthy', 'starting', 'invalid'):
            with self.subTest(health=health):
                self.states['db'] = ('running ' + health).encode()
                self.check(0 if health == 'healthy' else 1)

    def test_stopped_paused_restarting_and_dead_not_probed(self):
        for state in ('exited', 'paused', 'restarting', 'dead', 'created'):
            with self.subTest(state=state):
                self.states['db'] = (state + ' absent').encode()
                report = self.check()
                self.assertEqual(report['services']['db']['probe'], 'not-run')

    def test_missing_and_multiple_containers(self):
        for ids, state in ((b'', 'missing'), (b'one\ntwo', 'multiple')):
            self.ids['db'] = ids
            self.assertEqual(self.check()['services']['db']['container'], state)

    def test_missing_or_extra_configured_services(self):
        self.configured.remove('db')
        report = self.check()
        self.assertFalse(report['services']['db']['configured'])
        self.assertEqual(report['configuration'], 'mismatch')
        self.configured = ops.SERVICES | {'unexpected'}
        self.assertEqual(self.check()['configuration'], 'mismatch')

    def test_config_errors_do_not_leak_or_probe(self):
        for error in (FileNotFoundError('PRIVATE_SECRET'), PermissionError('PRIVATE_SECRET'),
                      RuntimeError('PRIVATE_SECRET'),
                      subprocess.TimeoutExpired('PRIVATE_SECRET', 3),
                      subprocess.CalledProcessError(1, 'PRIVATE_SECRET', stderr=b'PRIVATE_SECRET')):
            self.calls = []
            def fail(_args):
                raise error
            self.inject_failure = fail
            report = self.check()
            self.assertEqual(len(self.calls), 1)
            self.assertIn(report['configuration'], ('unknown', 'timeout'))

    def test_inspect_timeout_and_malformed_response(self):
        def fail(args):
            if args[:2] == ['docker', 'inspect']:
                raise subprocess.TimeoutExpired(args, 3)
        self.inject_failure = fail
        self.assertEqual(self.check()['services']['db']['container'], 'timeout')
        self.inject_failure = None
        self.states['db'] = b'PRIVATE_SECRET'
        self.assertEqual(self.check()['services']['db']['container'], 'unknown')

    def test_probe_failure_timeout_and_missing_tool(self):
        for error, expected in ((subprocess.CalledProcessError(1, 'PRIVATE_SECRET'), 'failed'),
                                (subprocess.TimeoutExpired('PRIVATE_SECRET', 3), 'timeout'),
                                (FileNotFoundError('PRIVATE_SECRET'), 'unknown')):
            def fail(args):
                if args[:2] == ['docker', 'exec']:
                    raise error
            self.inject_failure = fail
            self.assertEqual(self.check()['services']['db']['probe'], expected)

    def test_valkey_requires_pong(self):
        self.pong = b'NOAUTH PRIVATE_SECRET'
        self.assertEqual(self.check()['services']['broker']['probe'], 'failed')

    def test_http_dependencies_unknown_without_webserver(self):
        self.ids['webserver'] = b''
        report = self.check()
        for name in ('tika', 'gotenberg'):
            self.assertEqual(report['services'][name]['probe'], 'unknown')

    def test_status_bypasses_root_lock_umask_and_mutation(self):
        with patch.object(ops.sys, 'argv', ['paperless', 'status', '--json']), \
                patch.object(ops, 'status', return_value=1) as status, \
                patch.object(ops.os, 'geteuid', side_effect=AssertionError('root check')), \
                patch.object(ops.os, 'umask', side_effect=AssertionError('umask')), \
                patch('builtins.open', side_effect=AssertionError('file open')), \
                patch.object(ops, 'backup', side_effect=AssertionError('backup')), \
                patch.object(ops, 'restore', side_effect=AssertionError('restore')), \
                patch.object(ops, 'upgrade', side_effect=AssertionError('upgrade')):
            self.assertEqual(ops.main(), 1)
            status.assert_called_once_with(True, 10)

    def test_help_without_root_or_subprocess(self):
        for command in ([], ['status'], ['backup'], ['restore'], ['upgrade']):
            with patch.object(ops.sys, 'argv', ['paperless', *command, '--help']), \
                    patch.object(ops.sys, 'stdout', io.StringIO()) as out, \
                    patch.object(ops.os, 'geteuid', side_effect=AssertionError('root check')), \
                    patch.object(ops, 'run', side_effect=AssertionError('subprocess')):
                with self.assertRaises(SystemExit) as result:
                    ops.main()
                self.assertEqual(result.exception.code, 0)
                self.assertIn('Exit', out.getvalue())
                self.assertIn('Example', out.getvalue())

    def test_mutating_commands_still_require_root(self):
        for command in (['backup'], ['restore', '/backup', '--trusted-backup'], ['upgrade', '3.3.4']):
            with patch.object(ops.sys, 'argv', ['paperless', *command]), \
                    patch.object(ops.os, 'geteuid', return_value=1000), \
                    patch('builtins.open', side_effect=AssertionError('file open')):
                with self.assertRaisesRegex(RuntimeError, 'Run as root'):
                    ops.main()

    def test_generated_http_probe_executes_and_rejects_errors_redirects(self):
        from http.server import BaseHTTPRequestHandler, HTTPServer
        import threading
        response = [200]
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(response[0])
                self.send_header('Location', 'http://should-not-be-followed.invalid/')
                self.end_headers()

            def log_message(self, format, *args):
                pass

        server = HTTPServer(('127.0.0.1', 0), Handler)
        worker = threading.Thread(target=server.serve_forever, daemon=True)
        worker.start()
        try:
            self.check(0)
            codes = [c[-1] for c in self.calls if c[:2] == ['docker', 'exec'] and 'python3' in c]
            self.assertEqual(len(codes), 3)
            for code in codes:
                import re
                local = re.sub(r'http://[^\x27]+',
                               f'http://127.0.0.1:{server.server_port}/probe', code)
                for http_status in (200, 302, 401, 500):
                    response[0] = http_status
                    result = subprocess.run([sys.executable, '-c', local], capture_output=True, timeout=5)
                    self.assertEqual(result.returncode, 0 if http_status == 200 else 1)
        finally:
            server.shutdown()
            server.server_close()
            worker.join(timeout=5)

    def test_missing_layout_json_and_text_no_writes(self):
        # A missing layout must yield a sanitized report, not a traceback or a lock.
        import tempfile
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as temp:
            with patch.object(ops, 'ROOT', Path(temp)), patch.object(ops.sys, 'stdout', io.StringIO()) as out:
                self.assertEqual(ops.status(True), 1)
                self.assertEqual(json.loads(out.getvalue())['configuration'], 'unknown')
            with patch.object(ops, 'ROOT', Path(temp)), patch.object(ops.sys, 'stdout', io.StringIO()) as out:
                self.assertEqual(ops.status(), 1)
                self.assertIn('unhealthy/unknown', out.getvalue())
            self.assertEqual(list(Path(temp).iterdir()), [])

    def test_invalid_timeout(self):
        for timeout in ('0', '-1', '61', 'abc'):
            with patch.object(ops.sys, 'argv', ['paperless', 'status', '--timeout', timeout]), \
                    patch.object(ops.sys, 'stderr', io.StringIO()):
                with self.assertRaises(SystemExit) as result:
                    ops.main()
                self.assertEqual(result.exception.code, 2)


if __name__ == '__main__':
    unittest.main()
