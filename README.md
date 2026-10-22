# GitHub Notification AutoFix

Monitor GitHub notifications, diagnose actionable failures with Codex CLI, publish focused fixes, and mark notifications as Done after the current commit passes its GitHub checks.

Supports failing CI runs, pull requests with failing checks or requested changes, and issues identified as bugs. Repairs are limited to repositories and forks owned by `brunnojob` with write access. Protected branches, unavailable infrastructure, pending checks, and outstanding review requests remain unresolved and are recorded in local logs.

## Interactive demonstration

[Open the interactive demo](https://brunnojob.github.io/github-notification-autofix/)

Play a successful repair or inspect pending checks, a concurrent branch change and missing write permission. The page replays evidence generated during its GitHub Actions build. It shows the actual before/after output of three Python fixture tests and decisions made by the real monitor and SQLite state handling.

GitHub API responses, Codex repair and remote publishing are test doubles. The fixture repair is deterministic; the demo does not claim to execute Codex, access notifications or repair live repositories in the browser. Use the verification link and downloadable JSON on the page to inspect the exact source commit and recorded results.

Generate the recording locally with `python demo/record.py`, then serve `site/` through a local HTTP server. No account or credentials are needed for this demonstration. Append `?lang=pt` for Portuguese; English is the default.

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
