# Pending work

The index of what is still open. **One line per item.** If it needs more than a
line, the reasoning lives where it belongs (the README, a PR, `git log`) and
this file links to it. Lines are pruned as items ship.

**👤 needs you** · **⏳ waiting on a trigger or on data** · **🔨 ready to pick up**

---

| | What is missing | Waiting on |
|---|---|---|
| ⏳ | Publish `/q/` (the polls landing page, written and kept local) and add group-polls to `/.well-known/assetlinks.json` | The group-polls app having its Firebase project and Play signing key · lillo-android-apps `PENDING.md` |
| ⏳ | Confirm the **Stadium events** workflow runs on its schedule, not only by hand: its first scheduled run was due 2026-11-11 05:00 UTC and had not appeared five hours later | `gh run list --workflow "Stadium events"` showing a `schedule` event; then drop this line |
| ⏳ | GitHub turns off a scheduled workflow after 60 days without repository activity, and this one commits only when the events change | A quiet summer: if the stadium's agenda stays still for two months, the feed stops refreshing with no error · a monthly check, or an alert from the app's side when the feed is old |
