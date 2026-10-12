import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch
import github_autofix as m

THREAD = {'id': '100', 'updated_at': '2026-10-12T03:00:00Z', 'repository': {'full_name': 'brunnojob/demo'}, 'subject': {'type': 'CheckSuite', 'url': m.API + '/repos/brunnojob/demo/check-suites/1'}, 'reason': 'ci_activity'}
TARGET = {'repo': 'brunnojob/demo', 'branch': 'main', 'sha': 'a' * 40}
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
        g.get.return_value = {'statuses': []}
        self.assertFalse(m.checks(g, TARGET['repo'], TARGET['sha'])['green'])

    def test_pending_checks_not_green(self):
        g = Mock()
        g.pages.return_value = [{'status': 'in_progress', 'conclusion': None}]
        g.get.return_value = {'statuses': []}
        result = m.checks(g, TARGET['repo'], TARGET['sha'])
        self.assertFalse(result['green'])
        self.assertTrue(result['pending'])

    def test_absent_checks_not_green(self):
        g = Mock()
        g.pages.return_value = []
        g.get.return_value = {'statuses': []}
        self.assertFalse(m.checks(g, TARGET['repo'], TARGET['sha'])['green'])

    def test_success_checks_green(self):
        g = Mock()
        g.pages.return_value = [{'status': 'completed', 'conclusion': 'success'}]
        g.get.return_value = {'statuses': [{'state': 'success'}]}
        self.assertTrue(m.checks(g, TARGET['repo'], TARGET['sha'])['green'])

    def test_external_failure_blocks_done(self):
        g = Mock()
        g.pages.return_value = [{'status': 'completed', 'conclusion': 'success'}]
        g.get.return_value = {'statuses': [{'state': 'error'}]}
        self.assertFalse(m.checks(g, TARGET['repo'], TARGET['sha'])['green'])

    @patch.object(m, 'branch_head', return_value=TARGET['sha'])
    @patch.object(m, 'checks', return_value={'green': False})
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

    @patch.object(m, 'branch_head', return_value=TARGET['sha'])
    @patch.object(m, 'checks', return_value={'green': True})
    def test_all_green_marks_done(self, *_):
        g = Mock()
        self.assertTrue(m.verified_done(g, CONTEXT, TARGET))
        g.done.assert_called_once_with(THREAD)

    @patch.object(m, 'branch_head', return_value=TARGET['sha'])
    @patch.object(m, 'checks', return_value={'green': True})
    def test_requested_changes_prevent_done(self, *_):
        g = Mock()
        g.get.return_value = {'head': {'sha': TARGET['sha']}}
        g.pages.return_value = [{'user': {'login': 'maintainer'}, 'state': 'CHANGES_REQUESTED'}]
        self.assertFalse(m.verified_done(g, {**CONTEXT, 'pr_url': 'https://api.github.com/repos/brunnojob/demo/pulls/1'}, TARGET))
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


if __name__ == '__main__':
    unittest.main()
