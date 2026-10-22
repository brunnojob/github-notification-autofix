# GitHub Notification AutoFix

Monitor GitHub notifications, diagnose actionable failures with Codex CLI, publish focused fixes, and mark notifications as Done after the current commit passes its GitHub checks.

Supports failing CI runs, pull requests with failing checks or requested changes, and issues identified as bugs. Repairs are limited to repositories and forks owned by `brunnojob` with write access. Protected branches, unavailable infrastructure, pending checks, and outstanding review requests remain unresolved and are recorded in local logs.

## Interactive demonstration

[Open the interactive demo](https://brunnojob.github.io/github-notification-autofix/)

Play a successful repair or inspect pending checks, a concurrent branch change, missing write permission, and a late green result for an obsolete commit. The page replays evidence generated during its GitHub Actions build. It shows the actual before/after output of three Python fixture tests and decisions made by the real monitor and SQLite state handling.

GitHub API responses, Codex repair and remote publishing are test doubles. The fixture repair is deterministic; the demo does not claim to execute Codex, access notifications or repair live repositories in the browser. Use the verification link and downloadable JSON on the page to inspect the exact source commit and recorded results.

Generate the recording locally with `python demo/record.py`, then serve `site/` through a local HTTP server. No account or credentials are needed for this demonstration. Append `?lang=pt` for Portuguese; English is the default.

## Verification boundary

A notification identifies work to inspect; it does not identify the commit that passed verification. Each repair stores its attempted SHA and expected workflow identities before waiting for remote results. Local tests and an agent's `fixed` report only permit publishing a candidate repair.

Before Done, the monitor:

- Reads the current branch and PR head, including the head repository and base branch.
- Reads required status checks from classic branch protection and active branch rulesets for the PR base branch (or repaired branch for non-PR work). Missing required checks keep the repair unverified. Permission errors block completion. Unsupported ruleset-required workflows block completion explicitly.
- Fetches all pages of check runs and commit statuses for the attempted SHA. It checks SHA and expected app identity, and correlates GitHub Actions checks with workflow runs from the same repository, SHA, workflow ID, path and triggering event. Workflows from the source notification remain required even when absent from the new head.
- Requires the expected workflows' latest attempts and all observed checks to pass, with no pending, missing, cancelled or failed check. Outstanding change requests keep the notification open.
- Reads the head again after reviewing results and immediately before the notification DELETE. A newer commit C invalidates B and schedules re-evaluation.

SQLite outcomes separately record `notification_handled` and `repair_verified`, the attempted SHA, required checks, workflow identities, check-run URLs and local test commands. Closing an issue/PR can handle its notification without verifying a repair. Existing databases migrate automatically; pending records without workflow identity must be re-evaluated.

The **Late green for obsolete commit A** demo records A failing, a repair publishing B, A's delayed green result, B still pending and then a required B check failing. The real monitor makes zero Done calls in both B states; the recorded JSON includes the attempted B SHA and check URLs. The tests also push C while B's evidence is being read and reject mismatched repositories, workflows and SHAs.

GitHub does not provide an atomic operation combining PR-head comparison and notification deletion. Repeated head reads narrow that race; the stored verification describes the head observed immediately before deletion, not a guarantee about future pushes. Review approvals, deployments and other non-check merge requirements are outside this check-verification boundary.

## Requirements

- Python 3.10 or later and Git.
- Codex CLI authenticated with `codex login`.
- A GitHub personal access token **classic** from the `brunnojob` account with `notifications` and `repo` scopes. Add `workflow` to publish workflow changes.
- Windows PowerShell 5.1 or later for automatic startup installation.

```powershell
npm install -g @openai/codex@0.162.1
codex login
```

## Windows installation

Clone the repository into a permanent directory, then run:

```powershell
git clone https://github.com/brunnojob/github-notification-autofix.git
cd github-notification-autofix
powershell -NoProfile -ExecutionPolicy RemoteSigned -File .\Install-GitHubAutoFix.ps1
```

The installer prompts for the token without displaying it, encrypts it with the current Windows user's DPAPI, verifies access, and starts the `BrunnoJob-GitHub-AutoFix` scheduled task. The task restarts at login. The computer must remain on with the Windows user logged in.

## Manual execution

Set `GH_TOKEN` in the process environment before running. Keep credentials outside source files.

```sh
python github_autofix.py --check-setup
python github_autofix.py --once
python github_autofix.py --apply
```

`--once` previews actionable notifications without publishing fixes or marking Done. `--apply` enables the repair loop. Polling defaults to 60 seconds and respects GitHub's required interval and rate limits.

Codex edits an isolated checkout and runs local verification inside the `workspace-write` sandbox. The monitor publishes without force-push and checks GitHub independently before Done. The GitHub token is excluded from the agent process. Ordinary notifications remain open; closed bug issues and pull requests can be marked Done based on their confirmed state.

## Logs and task control

Runtime data is stored in `data/`: `monitor.log`, `events.jsonl`, `state.sqlite3`, and per-job Codex logs and checkouts. This directory is excluded from Git.

```powershell
Stop-ScheduledTask -TaskName 'BrunnoJob-GitHub-AutoFix'
Start-ScheduledTask -TaskName 'BrunnoJob-GitHub-AutoFix'
Disable-ScheduledTask -TaskName 'BrunnoJob-GitHub-AutoFix'
```

Blocked operations are retried after one hour; new notification activity triggers re-evaluation. Repositories without GitHub checks remain open after local repair. Codex usage is subject to the authenticated account's limits.

## Validation

```sh
python -m unittest discover -s . -p "test_*.py"
python -m py_compile github_autofix.py test_autofix.py
```

The suite covers pagination, persistent state, read-only behavior, concurrent changes, permissions, and the conditions that prevent an incorrect Done action. Tests use mocked GitHub responses and agent interactions. A live repair requires local credentials, Codex authentication, and the project's development tools.

## License and credit

MIT licensed. Created and maintained by [BrunnoDev](https://brunnodev.store).
