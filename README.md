# jorgelillo7.github.io

Personal site of Jorge Lillo, served by GitHub Pages. Plain static HTML/CSS, no build step.

| Path | Content |
|---|---|
| `/` · `/en/` | Home in Spanish and English: pinned Android apps, about, experience, projects, education |
| `/privacy/<app>/` | Privacy policy for each Android app |
| `assets/` | Shared stylesheet, favicons and app icons |

Keep `/privacy/<app>/` URLs stable: published Google Play listings and the apps link to them.

When adding an app: add its card to the pinned "Apps" block in both `index.html` and
`en/index.html`, its icon to `assets/apps/`, and its policy under `privacy/<app>/`.

Preview locally: `python3 -m http.server 8765` and open http://127.0.0.1:8765/.
