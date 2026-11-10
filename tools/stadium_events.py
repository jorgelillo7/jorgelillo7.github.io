#!/usr/bin/env python3
"""Builds stadium/events.json, the feed of the "¿Hay jaleo? Metropolitano" Android app.

Reads two official pages and merges them:
  - the stadium's agenda (every event at the Riyadh Air Metropolitano: matches, concerts, finals),
  - Atlético de Madrid's full fixture list (kick-off times, and the day once LaLiga fixes it).

Standard library only, so the GitHub Actions job needs no installs. Exits with 1, without writing
anything, if a page can't be read or the stadium lists no events: the last good file stays.

  python3 tools/stadium_events.py stadium/events.json
"""

import html
import json
import re
import sys
import unicodedata
import urllib.request
from datetime import date, datetime, timedelta, timezone

STADIUM_URL = "https://www.riyadhairmetropolitano.com/"
CLUB_URL = "https://www.atleticodemadrid.com/calendario-completo-primer-equipo/"
USER_AGENT = "Mozilla/5.0 (compatible; jorgelillo7.github.io stadium-events feed; +https://jorgelillo7.github.io/)"
HOME_VENUE = "Metropolitano"

MONTHS = {
    "enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6, "julio": 7,
    "agosto": 8, "septiembre": 9, "setiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12,
}

CARD = re.compile(
    r'<div data-cat="(?P<cat>[^"]*)"[^>]*class="card_concierto">.*?'
    r'overlay_titulo">(?P<title>[^<]*)</h3>\s*<p class="overlay_fechas">(?P<dates>[^<]*)</p>.*?'
    r'data-ev-slug="1" class="dato-oculto">(?P<slug>[^<]*)<',
    re.S,
)
STADIUM_DATE = re.compile(r"(\d{1,2})(?:\s+O\s+(\d{1,2}))?\s*·\s*([A-ZÁÉÍÓÚa-záéíóú]+)\s*·\s*(\d{4})")

CLUB_ITEM = re.compile(r'<div class="calendar-item[^"]*">(.*?)(?=<div class="calendar-item|\Z)', re.S)
CLUB_DATE = re.compile(r"(\d{1,2})(?:\s+o\s+\w+\s+(\d{1,2}))?\s+de\s+([a-záéíóú]+)", re.I)


def fetch(url):
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept-Language": "es-ES"})
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read().decode("utf-8", errors="replace")


def text(fragment):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", fragment))).strip()


def parse_stadium(page):
    """Each card: its days, and whether it is one of them (LaLiga's "5 O 6") or all of them (a tour)."""
    events = []
    for card in CARD.finditer(page):
        days, either = [], False
        for first, second, month, year in STADIUM_DATE.findall(card["dates"]):
            m, y = MONTHS[month.lower()], int(year)
            days.append(date(y, m, int(first)))
            if second:
                days.append(date(y, m, int(second)))
                either = True
        if days:
            events.append({
                "slug": card["slug"].strip(),
                "title": text(card["title"]),
                "category": text(card["cat"]),
                "days": sorted(set(days)),
                "either": either,
            })
    return events


def year_for(month, day, today):
    """The club page has no years: the closest date to today that isn't long past."""
    candidate = date(today.year, month, day)
    return candidate if candidate >= today - timedelta(days=120) else date(today.year + 1, month, day)


def parse_club(page, today):
    """Home matches only, with their competition, day(s) and kick-off time (None if not fixed)."""
    matches = []
    for item in CLUB_ITEM.finditer(page):
        block = item.group(1)
        info = re.search(r'<div class="info-calendario">(.*?)</div>', block, re.S)
        teams = re.findall(r"<dt>([^<]*)</dt>", block)
        if not info or len(teams) < 2:
            continue
        spans = [text(s).rstrip(" -").strip() for s in re.findall(r"<span[^>]*>(.*?)</span>", info.group(1), re.S)]
        venue = spans[3] if len(spans) > 3 else ""
        if HOME_VENUE not in venue:
            continue
        found = CLUB_DATE.search(spans[1] if len(spans) > 1 else "")
        if not found:
            continue
        first, second, month = found.groups()
        m = MONTHS.get(month.lower())
        if not m:
            continue
        days = [year_for(m, int(first), today)] + ([year_for(m, int(second), today)] if second else [])
        kickoff = spans[2] if len(spans) > 2 and re.fullmatch(r"\d{1,2}:\d{2}", spans[2]) else None
        competition = re.search(r'<div class="competition">.*?title="([^"]*)"', block, re.S)
        matches.append({
            "home": text(teams[0]),
            "away": text(teams[1]),
            "competition": text(competition.group(1)) if competition else None,
            "days": days,
            "either": bool(second),
            "time": kickoff,
        })
    return matches


def kind_of(event):
    if event["category"].lower().startswith("m"):          # Música
        return "concert"
    if "final" in event["title"].lower():
        return "final"
    return "match"


def merge(stadium, club, today):
    """The stadium's list, refined with the club's kick-off times and fixed days."""
    used, events = set(), []
    for event in stadium:
        days, either, time, competition = event["days"], event["either"], None, None
        for i, match in enumerate(club):
            if i not in used and set(match["days"]) & set(days):
                used.add(i)
                competition = match["competition"]
                if not match["either"]:
                    days, either, time = match["days"], False, match["time"]
                break
        events.append(entry(event["slug"], event["title"], kind_of(event), days, either, time, competition,
                            STADIUM_URL + "eventos/" + event["slug"]))
    for i, match in enumerate(club):           # announced by the club, not yet on the stadium's page
        if i not in used:
            plain = unicodedata.normalize("NFKD", f"{match['home']} vs {match['away']}").encode("ascii", "ignore")
            slug = re.sub(r"[^a-z0-9]+", "-", plain.decode().lower()).strip("-")
            events.append(entry(slug, f"{match['home']} vs {match['away']}", "match", match["days"], match["either"],
                                match["time"], match["competition"], CLUB_URL))
    upcoming = [e for e in events if e["days"][-1] >= today.isoformat()]
    return sorted(upcoming, key=lambda e: (e["days"][0], e["id"]))


def entry(slug, title, kind, days, either, time, competition, url):
    return {
        "id": slug,
        "title": title,
        "kind": kind,                                 # match | final | concert
        "level": "max" if kind in ("concert", "final") else "busy",
        "days": [d.isoformat() for d in sorted(days)],
        "either": either,                             # True: on one of the days, not fixed yet
        "time": time,                                 # "21:00", or None when unknown
        "competition": competition,
        "url": url,
    }


def build(stadium_page, club_page, today):
    stadium = parse_stadium(stadium_page)
    if not stadium:
        raise ValueError("no events found on the stadium's page: its layout may have changed")
    events = merge(stadium, parse_club(club_page, today), today)
    return {
        "version": 1,
        "sources": [STADIUM_URL, CLUB_URL],
        "events": events,
    }


def main(out):
    madrid_today = (datetime.now(timezone.utc) + timedelta(hours=1)).date()
    try:
        feed = build(fetch(STADIUM_URL), fetch(CLUB_URL), madrid_today)
    except Exception as error:  # noqa: BLE001 - any failure keeps the last good file
        print(f"stadium-events: {error}", file=sys.stderr)
        return 1
    with open(out, "w", encoding="utf-8") as file:
        json.dump(feed, file, ensure_ascii=False, indent=1)
        file.write("\n")
    print(f"stadium-events: {len(feed['events'])} events written to {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "stadium/events.json"))
