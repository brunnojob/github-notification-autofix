import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch
import github_autofix as m

THREAD = {'id': '100', 'updated_at': '2026-10-12T03:00:00Z', 'repository': {'full_name': 'brunnojob/demo'}, 'subject': {'type': 'CheckSuite', 'url': m.API + '/repos/brunnojob/demo/check-suites/1'}, 'reason': 'ci_activity'}
TARGET = {'repo': 'brunnojob/demo', 'branch': 'main', 'sha': 'a' * 40}
POLICY = {'check_repo': TARGET['repo'], 'pr_url': None, 'base_branch': 'main',
          'workflows': [{'id': 10, 'path': '.github/workflows/test.yml', 'event': 'push'}]}
TARGET['verification'] = POLICY
CONTEXT = {'thread': THREAD, 'target': TARGET, 'check_repo': 'brunnojob/demo'}


class Tests(unittest.TestCase):
    def test_state_deduplicates_and_detects_new_activity(self):
        with tempfile.TemporaryDirectory() as folder:
            s = m.State(Path(folder))
            self.assertIsNone(s.previous(THREAD))
            s.save(THREAD, 'done')
            self.assertEqual(s.previous(THREAD)['status'], 'done')
            self.assertIsNone(s.previous({**THREAD, 'updated_at': '2026-10-12T04:00:00Z'}))
            s.db.close()

    def test_pagination(self):
        g = m.GitHub('test')
        g.request = Mock(side_effect=[([{'id': 1}], {'Link': '<https://api.github.com/notifications?page=2>; rel="next"'}), ([{'id': 2}], {})])
        self.assertEqual(list(g.pages('/notifications')), [{'id': 1}, {'id': 2}])

    def test_foreign_origin_rejected(self):
        with self.assertRaises(m.Blocked):
            m.GitHub('test').get('https://evil.example/notifications')

    def test_only_done_mutation_allowed(self):
        for method, path in [('DELETE', '/repos/brunnojob/demo'), ('POST', '/notifications'), ('DELETE', '/notifications/threads/bad')]:
            with self.assertRaises(m.Blocked):
                m.GitHub('test').request(path, method)

    def test_done_requires_unchanged_notification(self):
        g = m.GitHub('test')
        g.get = Mock(return_value={**THREAD, 'updated_at': 'new'})
        g.request = Mock()
        with self.assertRaises(m.RetryLater):
            g.done(THREAD)
        g.request.assert_not_called()

    def test_done_uses_delete_thread(self):
        g = m.GitHub('test')
        g.get = Mock(return_value=THREAD)
        g.request = Mock()
        g.done(THREAD)
        g.request.assert_called_once_with('/notifications/threads/100', 'DELETE')

    def test_failed_checks_not_green(self):
        g = Mock()
        g.pages.return_value = [{'status': 'completed', 'conclusion': 'failure'}]
        runs = g.pages.return_value
        g.pages.side_effect = lambda path, key=None: [] if key == 'statuses' else runs
        self.assertFalse(m.checks(g, TARGET['repo'], TARGET['sha'])['green'])

    def test_pending_checks_not_green(self):
        g = Mock()
        g.pages.return_value = [{'status': 'in_progress', 'conclusion': None}]
        runs = g.pages.return_value
        g.pages.side_effect = lambda path, key=None: [] if key == 'statuses' else runs
        result = m.checks(g, TARGET['repo'], TARGET['sha'])
        self.assertFalse(result['green'])
        self.assertTrue(result['pending'])

    def test_absent_checks_not_green(self):
        g = Mock()
        g.pages.return_value = []
        runs = g.pages.return_value
        g.pages.side_effect = lambda path, key=None: [] if key == 'statuses' else runs
        self.assertFalse(m.checks(g, TARGET['repo'], TARGET['sha'])['green'])

    def test_success_checks_green(self):
        g = Mock()
        g.pages.return_value = [{'status': 'completed', 'conclusion': 'success'}]
        g.pages.side_effect = lambda path, key=None: [{'state': 'success'}] if key == 'statuses' else [{'status': 'completed', 'conclusion': 'success'}]
        self.assertTrue(m.checks(g, TARGET['repo'], TARGET['sha'])['green'])

    def test_external_failure_blocks_done(self):
        g = Mock()
        g.pages.return_value = [{'status': 'completed', 'conclusion': 'success'}]
        g.pages.side_effect = lambda path, key=None: [{'state': 'error'}] if key == 'statuses' else [{'status': 'completed', 'conclusion': 'success'}]
        self.assertFalse(m.checks(g, TARGET['repo'], TARGET['sha'])['green'])

    @patch.object(m, 'required_checks', return_value=[])
    @patch.object(m, 'branch_head', return_value=TARGET['sha'])
    @patch.object(m, 'checks', return_value={'green': False, 'check_run_urls': []})
    def test_unverified_correction_keeps_notification(self, *_):
        g = Mock()
        self.assertFalse(m.verified_done(g, CONTEXT, TARGET))
        g.done.assert_not_called()

    @patch.object(m, 'branch_head', return_value='b' * 40)
    def test_concurrent_commit_resets_pending(self, *_):
        g = Mock()
        with self.assertRaises(m.RetryLater) as caught:
            m.verified_done(g, CONTEXT, TARGET)
        self.assertTrue(caught.exception.reset_target)
        g.done.assert_not_called()

    @patch.object(m, 'required_checks', return_value=[])
    @patch.object(m, 'branch_head', return_value=TARGET['sha'])
    @patch.object(m, 'checks', return_value={'green': True, 'check_run_urls': []})
    def test_all_green_marks_done(self, *_):
        g = Mock()
        self.assertTrue(m.verified_done(g, CONTEXT, TARGET))
        self.assertEqual(g.done.call_args.args, (THREAD,))
        self.assertTrue(callable(g.done.call_args.kwargs['guard']))

    @patch.object(m, 'required_checks', return_value=[])
    @patch.object(m, 'branch_head', return_value=TARGET['sha'])
    @patch.object(m, 'checks', return_value={'green': True, 'check_run_urls': []})
    def test_requested_changes_prevent_done(self, *_):
        g = Mock()
        g.get.return_value = {'head': {'sha': TARGET['sha'], 'ref': 'main', 'repo': {'full_name': TARGET['repo']}},
                              'base': {'ref': 'main', 'repo': {'full_name': TARGET['repo']}}}
        g.pages.return_value = [{'user': {'login': 'maintainer'}, 'state': 'CHANGES_REQUESTED'}]
        self.assertFalse(m.verified_done(g, CONTEXT.copy(), {**TARGET, 'verification': {**POLICY, 'pr_url': m.API + '/repos/brunnojob/demo/pulls/1'}}))
        g.done.assert_not_called()

    @patch.object(m, 'verified_done', return_value=True)
    @patch.object(m, 'resolve_context')
    def test_resume_pending_checks_before_classifying(self, resolve, verified):
        with tempfile.TemporaryDirectory() as folder:
            state = m.State(Path(folder))
            state.save(THREAD, 'awaiting_checks', target=TARGET)
            m.handle(Mock(), state, THREAD, Mock(apply=True, account='brunnojob'))
            self.assertEqual(state.previous(THREAD)['status'], 'done')
            resolve.assert_not_called()
            state.db.close()

    @patch.object(m, 'resolve_context', return_value={'closed': True})
    def test_preview_does_not_mark_done(self, *_):
        with tempfile.TemporaryDirectory() as folder:
            state = m.State(Path(folder))
            g = Mock()
            m.handle(g, state, THREAD, Mock(apply=False, account='brunnojob'))
            g.done.assert_not_called()
            state.db.close()

    def test_no_write_permission_blocks(self):
        g = Mock()
        g.get.return_value = {'archived': False, 'permissions': {'push': False}, 'owner': {'login': 'brunnojob'}}
        with self.assertRaises(m.Blocked):
            m.writable_target(g, 'brunnojob/demo', 'main', 'brunnojob')

    def test_other_owner_blocks(self):
        g = Mock()
        g.get.return_value = {'archived': False, 'permissions': {'push': True}, 'owner': {'login': 'other'}}
        with self.assertRaises(m.Blocked):
            m.writable_target(g, 'other/demo', 'main', 'brunnojob')

    @patch.dict('os.environ', {'GH_TOKEN': 'secret'})
    def test_git_token_only_in_environment(self):
        env = m.git_environment('secret')
        self.assertNotIn('secret', env['GIT_CONFIG_VALUE_0'])
        self.assertTrue(env['GIT_CONFIG_VALUE_0'].startswith('AUTHORIZATION: basic '))
        self.assertEqual(env['GIT_TERMINAL_PROMPT'], '0')

    @patch.object(m, 'branch_head', return_value='b' * 40)
    @patch.object(m, 'command')
    def test_publish_race_does_not_commit(self, command, *_):
        with self.assertRaises(m.RetryLater):
            m.publish(Mock(), CONTEXT, Path('/unused'), {'status': 'fixed', 'tests': ['test']})
        command.assert_not_called()

    @patch.object(m, 'verified_done')
    def test_preview_cannot_complete_pending_repair(self, verified):
        with tempfile.TemporaryDirectory() as folder:
            state = m.State(Path(folder))
            state.save(THREAD, 'awaiting_checks', target=TARGET)
            m.handle(Mock(), state, THREAD, Mock(apply=False, account='brunnojob'))
            self.assertEqual(state.previous(THREAD)['status'], 'awaiting_checks')
            verified.assert_not_called()
            state.db.close()

    def test_rate_limit_signals_pause(self):
        self.assertTrue(m.RetryLater('rate limit', 60, pause_scan=True).pause_scan)
        self.assertFalse(m.RetryLater('pending', 60).pause_scan)

    def test_normal_closed_issue_not_done(self):
        g = Mock()
        g.get.return_value = {'state': 'closed', 'labels': []}
        t = {**THREAD, 'reason': 'subscribed', 'subject': {'type': 'Issue', 'title': 'General discussion', 'url': m.API + '/repos/brunnojob/demo/issues/1'}}
        self.assertTrue(m.resolve_context(g, t, 'brunnojob')['not_actionable'])


class VerificationBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.repo = TARGET['repo']
        self.sha = 'b' * 40
        self.pr_url = m.API + '/repos/' + self.repo + '/pulls/1'
        self.policy = {**POLICY, 'pr_url': self.pr_url}
        self.target = {**TARGET, 'sha': self.sha, 'verification': self.policy}
        self.context = {**CONTEXT, 'pr_url': self.pr_url}
        self.run = {'id': 1, 'name': 'test', 'head_sha': self.sha, 'status': 'completed', 'conclusion': 'success',
                    'app': {'id': 15368, 'slug': 'github-actions'}, 'check_suite': {'id': 20},
                    'html_url': 'https://github.com/' + self.repo + '/runs/1'}
        self.workflow = {'id': 30, 'workflow_id': 10, 'event': 'push', 'path': '.github/workflows/test.yml',
                         'head_sha': self.sha, 'repository': {'full_name': self.repo}, 'check_suite_id': 20,
                         'status': 'completed', 'conclusion': 'success'}
        self.runs = [self.run]
        self.workflows = [self.workflow]
        self.statuses = []
        self.rules = [{'context': 'test', 'app_id': 15368}]
        self.g = Mock()
        self.g.get.side_effect = self.get
        self.g.pages.side_effect = self.pages
        self.pr = {'head': {'sha': self.sha, 'ref': 'main', 'repo': {'full_name': self.repo}},
                   'base': {'ref': 'main', 'repo': {'full_name': self.repo}}}

    def get(self, path):
        if '/branches/main/protection/' in path:
            return {'checks': self.rules}
        if '/branches/' in path:
            return {'commit': {'sha': self.sha}}
        if path == self.pr_url:
            return self.pr
        raise AssertionError(path)

    def pages(self, path, key=None):
        if key == 'check_runs':
            return iter(self.runs)
        if key == 'statuses':
            return iter(self.statuses)
        if key == 'workflow_runs':
            return iter(self.workflows)
        if path.endswith('/reviews') or '/rules/branches/' in path:
            return iter([])
        raise AssertionError(path)

    def verify(self):
        return m.verified_done(self.g, self.context, self.target)

    def test_full_evidence_verifies_attempt_and_records_urls(self):
        self.assertTrue(self.verify())
        self.assertTrue(self.context['outcome']['repair_verified'])
        self.assertEqual(self.context['outcome']['attempted_sha'], self.sha)
        self.assertEqual(self.context['outcome']['check_run_urls'], [self.run['html_url']])

    def test_late_green_for_a_cannot_verify_b(self):
        self.runs[0] = {**self.run, 'head_sha': 'a' * 40}
        self.assertFalse(self.verify())
        self.g.done.assert_not_called()

    def test_one_green_workflow_does_not_replace_missing_required_check(self):
        self.rules.append({'context': 'security', 'app_id': 15368})
        self.assertFalse(self.verify())
        self.assertIn('security', self.context['outcome']['verification']['missing'])
        self.g.done.assert_not_called()

    def test_green_workflow_does_not_override_pending_or_failed_required_check(self):
        for conclusion, status in [(None, 'in_progress'), ('failure', 'completed'), ('cancelled', 'completed')]:
            with self.subTest(conclusion=conclusion):
                self.runs[0] = {**self.run, 'status': status, 'conclusion': conclusion}
                self.assertFalse(self.verify())
        self.g.done.assert_not_called()

    def test_wrong_repository_workflow_or_event_cannot_verify(self):
        for field, value in [('repository', {'full_name': 'other/demo'}), ('workflow_id', 99),
                             ('event', 'workflow_dispatch'), ('path', '.github/workflows/other.yml'),
                             ('head_sha', 'a' * 40)]:
            with self.subTest(field=field):
                self.workflows[0] = {**self.workflow, field: value}
                self.assertFalse(self.verify())
        self.g.done.assert_not_called()

    def test_wrong_required_app_cannot_satisfy_context(self):
        self.runs[0] = {**self.run, 'app': {'id': 999}}
        self.assertFalse(self.verify())

    def test_rerun_pending_supersedes_older_green(self):
        self.workflows.append({**self.workflow, 'run_attempt': 2, 'status': 'in_progress', 'conclusion': None})
        self.assertFalse(self.verify())

    def test_head_c_pushed_while_reading_checks_blocks_done(self):
        original = self.g.pages.side_effect
        def pages(path, key=None):
            if key == 'check_runs':
                self.pr['head']['sha'] = 'c' * 40
            return original(path, key)
        self.g.pages.side_effect = pages
        with self.assertRaises(m.RetryLater) as caught:
            self.verify()
        self.assertTrue(caught.exception.reset_target)
        self.g.done.assert_not_called()

    def test_same_sha_from_different_pr_repository_is_rejected(self):
        self.pr['head']['repo']['full_name'] = 'other/demo'
        with self.assertRaises(m.RetryLater):
            self.verify()
        self.g.done.assert_not_called()

    def test_final_guard_detects_push_after_notification_read(self):
        def done(thread, guard):
            self.pr['head']['sha'] = 'c' * 40
            guard()
        self.g.done.side_effect = done
        with self.assertRaises(m.RetryLater):
            self.verify()
        self.assertFalse(self.context['outcome']['repair_verified'])

    def test_pagination_of_statuses_and_sha_identity(self):
        self.statuses = [{'context': 'external', 'state': 'success',
                          'url': m.API + '/repos/' + self.repo + '/statuses/' + 'a' * 40}]
        self.assertFalse(self.verify())
        self.g.done.assert_not_called()

    def test_ruleset_required_check_is_enforced(self):
        original = self.g.pages.side_effect
        self.g.pages.side_effect = lambda path, key=None: iter([{'type': 'required_status_checks', 'parameters': {
            'required_status_checks': [{'context': 'security', 'integration_id': 15368}]}}]) if '/rules/branches/' in path else original(path, key)
        self.assertFalse(self.verify())

    def test_unreadable_requirements_never_assume_green(self):
        self.g.get.side_effect = m.Blocked('Forbidden')
        with self.assertRaises(m.Blocked):
            self.verify()
        self.g.done.assert_not_called()

    def test_old_database_migrates_and_preserves_attempt_after_done(self):
        import sqlite3
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            db = sqlite3.connect(root / 'state.sqlite3')
            db.execute('CREATE TABLE threads (id TEXT PRIMARY KEY, version TEXT NOT NULL, status TEXT NOT NULL, retry REAL NOT NULL, target TEXT)')
            db.commit()
            db.close()
            state = m.State(root)
            state.save(THREAD, 'awaiting_checks', target=self.target,
                       outcome={'local_tests': ['unittest'], 'attempted_sha': self.sha, 'repair_verified': False})
            self.assertTrue(self.verify())
            state.save(THREAD, 'done', outcome=self.context['outcome'])
            state.db.close()
            reopened = m.State(root)
            outcome = reopened.previous(THREAD)
            self.assertEqual(outcome['target']['sha'], self.sha)
            self.assertTrue(outcome['outcome']['notification_handled'])
            self.assertTrue(outcome['outcome']['repair_verified'])
            self.assertEqual(outcome['outcome']['local_tests'], ['unittest'])
            reopened.db.close()

    def test_source_workflow_is_kept_when_missing_from_new_head(self):
        source = {**self.workflow, 'workflow_id': 99, 'path': '.github/workflows/security.yml'}
        context = {**self.context, 'source_workflows': [source]}
        policy = m.verification_policy(self.g, context, self.target)
        self.assertIn({'id': 99, 'event': 'push', 'path': source['path']}, policy['workflows'])
        self.target['verification'] = policy
        self.assertFalse(self.verify())

    def test_legacy_attempt_without_workflow_identity_requires_reclassification(self):
        with self.assertRaises(m.RetryLater) as caught:
            m.verified_done(self.g, self.context, {k: v for k, v in self.target.items() if k != 'verification'})
        self.assertTrue(caught.exception.reset_target)
        self.g.done.assert_not_called()

    def test_concurrent_push_preserves_attempt_evidence(self):
        original = self.g.pages.side_effect
        def pages(path, key=None):
            if key == 'check_runs':
                self.pr['head']['sha'] = 'c' * 40
            return original(path, key)
        self.g.pages.side_effect = pages
        with tempfile.TemporaryDirectory() as folder:
            state = m.State(Path(folder))
            with self.assertRaises(m.RetryLater):
                m.record_verification(self.g, state, THREAD, self.context, self.target)
            outcome = state.previous(THREAD)['outcome']
            self.assertFalse(outcome['repair_verified'])
            self.assertEqual(outcome['check_run_urls'], [self.run['html_url']])
            state.db.close()

    def test_recorded_late_success_stays_open_after_b_fails(self):
        from demo.record import exercise
        result = exercise('late_green')
        self.assertEqual(result['done_calls'], 0)
        self.assertFalse(result['outcome']['repair_verified'])
        self.assertEqual(result['outcome']['attempted_sha'], 'b' * 40)
        self.assertEqual(result['result'], 'awaiting_checks')
        self.assertTrue(result['outcome']['verification']['failed'])


if __name__ == '__main__':
    unittest.main()
