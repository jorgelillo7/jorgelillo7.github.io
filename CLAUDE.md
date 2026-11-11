# CLAUDE.md — jorgelillo7.github.io

The owner's personal site on GitHub Pages: plain static HTML and CSS, no build
step, published from `main` as it is. Read the [README](README.md) for what
each path serves.

The owner's habits that hold in every repo (language, git and PRs, comments,
working style) are personal rules in `~/.claude/rules/`, versioned in
lillorepo `system/rules/`; a session that cannot read `~/.claude/` reads them
there. This file holds only what is true of this repo.

## What depends on this site

The site is also infrastructure for the Android apps in `lillo-android-apps`.
A change that looks cosmetic here can break an installed app.

| Path | Who reads it | What breaks if it moves or changes shape |
|---|---|---|
| `/privacy/<app>/` | Google Play listings and each app's About sheet | The listing's policy link; Play can suspend the app |
| `/.well-known/assetlinks.json` | Android, to verify App Links | Shared links stop opening the app |
| `/t/` `/p/` `/c/` `/q/` | Links already shared by users (data in the `#` fragment) | Every link shared so far |
| `/stadium/events.json` | The installed "¿Hay jaleo? Metropolitano" app | The app's events, reminders and widget |

## Ground rules

- **Published URLs never move.** Add paths; do not rename or remove the ones
  in the table above.
- **`/stadium/events.json` is written by the workflow only.** Change
  `scripts/stadium_events.py`, never the JSON. Its fields are a contract with
  installed apps: add fields, never rename or drop one.
- **The home exists twice.** `index.html` (Spanish) and `en/index.html` change
  together, including the app counts on the tabs.
- **No build step, no dependencies.** Pages serves the tree as committed
  (`.nojekyll`); scripts use the Python standard library only.
- **A page that is not live yet stays out of `main`.** `q/` and its
  `assetlinks.json` entry wait for the group-polls app (lillo-android-apps
  `PENDING.md`).

## Commands

```bash
python3 -m http.server 8765              # preview at http://127.0.0.1:8765/
python3 scripts/test_stadium_events.py   # the feed's tests (what the workflow runs)
python3 scripts/stadium_events.py /tmp/events.json   # build the feed without touching the published one
gh workflow run "Stadium events"         # refresh the published feed now
```

## Pending work

Open work lives in `PENDING.md`, one line per item.
