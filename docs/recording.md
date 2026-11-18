# Record a reproducible AutoFix demonstration

Open [recording mode](https://brunnojob.github.io/github-notification-autofix/?record=1#demo), use English or Portuguese, and capture a browser window at 1920 × 1080. Recording mode removes secondary sections and increases code/transcript text size. It changes presentation only, never permissions or verification outcomes.

## Suggested take

1. Select **Successful repair** and press **Play recording**. Keep the patch and test transcript visible. The fixture starts with three failing Python tests and finishes with three passing tests.
2. Show **Before**, **Patch** and **After** to explain the one-line arithmetic correction.
3. Show **Checks still running**: passing local tests do not permit Done while remote checks are pending.
4. Show **Late green for obsolete commit A**: successful old checks cannot verify a newer repair commit.
5. End on the result and **Done calls** counter. Use the gallery to choose the remaining scenarios.

For one continuous demonstration, press **Play guided tour**. It replays all five scenarios in order with a pause between their outcomes. Use **Stop tour**, **Pause**, **Reset** or the scenario selector to stop it. The speed button switches between 1× and 4×. Use the default speed for a narrated recording; use 4× to inspect all scenarios quickly.

The visible recording label and local/test-double disclosure remain on screen. The browser replays generated evidence; it does not run Codex, repair live repositories or access GitHub notifications. GitHub responses, the agent and publishing are test doubles. The actual monitor, fixture tests and SQLite handling execute during the Pages build. Read-only local monitor usage is separate: `python github_autofix.py --once`.

## Gallery and evidence

[Gallery](https://brunnojob.github.io/github-notification-autofix/#gallery) cards show the five recorded outcomes and allow each scenario to be opened in the player. Use **View verification run** and **Download evidence JSON** to inspect provenance. The README preview is a designed overview, not a screenshot of a live repair.

## Local preview

```sh
python demo/record.py
python demo/check_site.py
python -m http.server 8000 --directory site
```

Open `http://localhost:8000/?record=1`. No token or Codex login is needed for the recorded demo. For validation:

```sh
python -m unittest discover -s . -p "test_*.py"
node --check site/app.js
```

The **Verify** workflow tests Python on Linux and Windows and validates PowerShell syntax. **Publish verified demo** runs the real tests, generates evidence, validates static assets and deploys Pages. Publication happens only after the build succeeds.
