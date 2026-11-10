# jorgelillo7.github.io

Personal site of Jorge Lillo, served by GitHub Pages. Plain static HTML/CSS, no build step.

| Path | Content |
|---|---|
| `/` · `/en/` | Home in Spanish and English: pinned Android apps, about, experience, projects, education |
| `/privacy/<app>/` | Privacy policy for each Android app |
| `/t/` · `/p/` · `/c/` · `/q/` | Share-link landing pages: tournaments, impostor word packs, slipper challenges, polls (data in the link's `#`, never sent to the server) |
| `/stadium/events.json` | Feed of the "¿Hay jaleo? Metropolitano" app: upcoming events at the Riyadh Air Metropolitano, rebuilt daily by the **Stadium events** workflow (`tools/stadium_events.py`) from the stadium's agenda and Atlético de Madrid's fixtures. Don't edit it by hand |
| `assets/` | Shared stylesheet, favicons and app icons |

When the interactive fiction reader publishes a new story, add it to the list in the Historias card
of both `index.html` and `en/index.html`.

Keep `/privacy/<app>/` URLs stable: published Google Play listings and the apps link to them.

When adding an app: add its card to the Apps or Games tab (and its count) in both `index.html` and
`en/index.html`, its icon to `assets/apps/`, and its policy under `privacy/<app>/`.

Keep `/stadium/events.json` stable too: installed apps read it. If the workflow fails, a source page
changed its layout: fix `tools/stadium_events.py`, run `python3 tools/test_stadium_events.py`, and the
next run publishes again (the last good file stays meanwhile).

Preview locally: `python3 -m http.server 8765` and open http://127.0.0.1:8765/.
