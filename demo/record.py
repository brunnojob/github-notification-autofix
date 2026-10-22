import contextlib
import difflib
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import github_autofix as monitor

BEFORE = 'def total_cents(price_cents, quantity):\n    return price_cents + quantity\n'
AFTER = 'def total_cents(price_cents, quantity):\n    return price_cents * quantity\n'
TEST = '''import unittest
from checkout_total import total_cents

class CheckoutTests(unittest.TestCase):
    def test_multiple_items(self):
        self.assertEqual(total_cents(1050, 3), 3150)
    def test_zero_quantity(self):
        self.assertEqual(total_cents(1050, 0), 0)
    def test_single_item(self):
        self.assertEqual(total_cents(1050, 1), 1050)

if __name__ == '__main__':
    unittest.main()
'''
THREAD = {'id': 'demo-100', 'updated_at': '2026-01-01T00:00:00Z',
          'repository': {'full_name': 'brunnojob/autofix-demo-fixture'},
          'subject': {'type': 'CheckSuite', 'url': monitor.API + '/repos/brunnojob/autofix-demo-fixture/check-suites/1'},
          'reason': 'ci_activity'}
BASE_SHA = 'a' * 40
FIX_SHA = 'b' * 40


class FixtureGitHub:
    def __init__(self, scenario, events):
        self.scenario = scenario
        self.events = events
        self.sha = BASE_SHA
        self.published = False
        self.done_calls = 0

    def get(self, path):
        if '/check-suites/' in path:
            return {'id': 1, 'conclusion': 'failure', 'head_branch': 'main'}
        if '/branches/' in path:
            return {'commit': {'sha': self.sha}}
        if '/commits/' in path and path.endswith('/status'):
            return {'statuses': []}
        if '/notifications/threads/' in path:
            return THREAD.copy()
        if path.startswith('/repos/'):
            return {'owner': {'login': 'brunnojob'}, 'archived': False,
                    'permissions': {'push': self.scenario != 'permission'}, 'default_branch': 'main'}
        raise AssertionError('Unexpected fixture request: ' + path)

    def pages(self, path, key=None):
        if '/actions/runs' in path:
            return iter([{'conclusion': 'failure', 'head_branch': 'main'}])
        if '/check-runs' in path:
            if not self.published:
                return iter([{'name': 'Python tests', 'status': 'completed', 'conclusion': 'failure'}])
            pending = self.scenario == 'pending'
            self.events.append({'step': 'verify', 'state': 'waiting' if pending else 'success',
                                'code': 'checks_pending' if pending else 'checks_green'})
            return iter([{'name': 'Python tests', 'status': 'in_progress' if pending else 'completed',
                          'conclusion': None if pending else 'success'}])
        raise AssertionError('Unexpected fixture pagination: ' + path)

    def request(self, path, method='GET'):
        assert method == 'DELETE' and path == '/notifications/threads/' + THREAD['id']
        self.done_calls += 1
        self.events.append({'step': 'done', 'state': 'success', 'code': 'marked_done'})
        return None, {}

    def done(self, thread):
        return monitor.GitHub.done(self, thread)


def exercise(scenario):
    events = [{'step': 'scan', 'state': 'success', 'code': 'notification_found'}]
    github = FixtureGitHub(scenario, events)
    fixture = {'before': '', 'after': '', 'before_exit': None, 'after_exit': None}
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        state = monitor.State(root / 'monitor')

        def repair(context, data_root, timeout):
            events.append({'step': 'diagnose', 'state': 'success', 'code': 'failure_confirmed'})
            checkout = root / 'checkout'
            checkout.mkdir()
            source = checkout / 'checkout_total.py'
            source.write_text(BEFORE, encoding='utf-8')
            (checkout / 'test_checkout.py').write_text(TEST, encoding='utf-8')
            command = [sys.executable, '-m', 'unittest', '-v']
            failed = subprocess.run(command, cwd=checkout, capture_output=True, text=True, timeout=30)
            assert failed.returncode != 0 and 'FAILED' in failed.stderr
            fixture.update(before=failed.stderr, before_exit=failed.returncode)
            events.append({'step': 'repair', 'state': 'success', 'code': 'fixture_patched'})
            source.write_text(AFTER, encoding='utf-8')
            for cached in checkout.glob('__pycache__/*.pyc'):
                cached.unlink()
            passed = subprocess.run(command, cwd=checkout, capture_output=True, text=True, timeout=30)
            assert passed.returncode == 0 and 'Ran 3 tests' in passed.stderr
            fixture.update(after=passed.stderr, after_exit=passed.returncode)
            events.append({'step': 'test', 'state': 'success', 'code': 'tests_passed'})
            return checkout, {'status': 'fixed', 'summary': 'Deterministic fixture repair; Codex is stubbed.',
                              'tests': ['python -m unittest -v (3 fixture tests)']}

        def publish(adapter, context, checkout, report):
            assert (checkout / 'checkout_total.py').read_text(encoding='utf-8') == AFTER
            adapter.published = True
            adapter.sha = 'c' * 40 if scenario == 'race' else FIX_SHA
            events.append({'step': 'publish', 'state': 'success', 'code': 'publish_stubbed'})
            return {**context['target'], 'sha': FIX_SHA}

        args = SimpleNamespace(apply=True, account='brunnojob', agent_timeout=60)
        output = io.StringIO()
        with contextlib.redirect_stdout(output), patch.object(monitor, 'agent_repair', repair), patch.object(monitor, 'publish', publish):
            try:
                monitor.handle(github, state, THREAD, args)
            except monitor.Blocked:
                assert scenario == 'permission'
                state.save(THREAD, 'blocked')
                events.append({'step': 'diagnose', 'state': 'blocked', 'code': 'permission_denied'})
            except monitor.RetryLater as error:
                assert scenario == 'race' and error.reset_target
                state.save(THREAD, 'retry')
                events.append({'step': 'verify', 'state': 'blocked', 'code': 'head_changed'})
        result = state.previous(THREAD)['status']
        expected = {'success': 'done', 'pending': 'awaiting_checks', 'race': 'retry', 'permission': 'blocked'}[scenario]
        assert result == expected, (scenario, result)
        assert github.done_calls == (1 if scenario == 'success' else 0)
        assert github.published == (scenario != 'permission')
        if scenario == 'pending':
            events.append({'step': 'done', 'state': 'waiting', 'code': 'kept_open'})
        if scenario in {'race', 'permission'}:
            events.append({'step': 'done', 'state': 'blocked', 'code': 'kept_open'})
        state.db.close()
        return {'id': scenario, 'result': result, 'done_calls': github.done_calls, 'events': events,
                'fixture': fixture, 'monitor_log': output.getvalue().splitlines()}


def record():
    scenarios = [exercise(key) for key in ('success', 'pending', 'race', 'permission')]
    report = {
        'schema': 1,
        'source_sha': os.environ.get('GITHUB_SHA', subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()),
        'source_hash': hashlib.sha256((ROOT / 'github_autofix.py').read_bytes()).hexdigest(),
        'workflow_url': ('https://github.com/' + os.environ['GITHUB_REPOSITORY'] + '/actions/runs/' + os.environ['GITHUB_RUN_ID']) if os.environ.get('GITHUB_RUN_ID') else None,
        'scope': 'Real Python monitor decisions, SQLite state and fixture tests. GitHub API responses, Codex repair and Git publishing are test doubles. Browser playback does not run the agent.',
        'diff': ''.join(difflib.unified_diff(BEFORE.splitlines(True), AFTER.splitlines(True), fromfile='a/checkout_total.py', tofile='b/checkout_total.py')),
        'before': BEFORE, 'after': AFTER, 'scenarios': scenarios,
        'assertions': 4,
    }
    path = ROOT / 'site' / 'evidence.json'
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('PASS: four recorded monitor scenarios; Done only after independent green checks; fixture fails before repair and passes afterward.')


if __name__ == '__main__':
    record()
