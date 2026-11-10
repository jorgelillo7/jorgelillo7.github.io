#!/usr/bin/env python3
"""Tests for stadium_events.py on small copies of the two pages' markup.

  python3 tools/test_stadium_events.py
"""

import sys
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import stadium_events as feed  # noqa: E402

TODAY = date(2026, 11, 10)


def card(cat, title, dates, slug):
    return (f'<div role="listitem" class="u-display-contents w-dyn-item"><div data-cat="{cat}" data-venta="Disponible" '
            f'data-fecha="Confirmada" class="card_concierto"><img src="x.jpg"/><div class="card_overlay"><div class="card_panel">'
            f'<div class="overlay_texto"><h3 class="overlay_titulo">{title}</h3><p class="overlay_fechas">{dates}</p></div>'
            f'</div></div><div data-ev-slug="1" class="dato-oculto">{slug}</div></div></div>')


def club_match(home, away, day, kickoff, venue, competition="LaLiga"):
    return (f'<div class="calendar-item toggler-todos active"><div class="header-calendar no-result">'
            f'<div class="competition"><img src="c.jpg" alt="{competition} 2026" title="{competition}" /></div>'
            f'<ul class="marcador"><li class="local"><dl><dt>{home}</dt></dl></li>'
            f'<li class="visitante"><dl><dt>{away}</dt></dl></li></ul>'
            f'<div class="info-calendario"> <span>Jornada 5<i> -</i> </span> <span>{day}<i> -</i> </span> '
            f'<span class="black">{kickoff}<i> -</i> </span> <span class="black">{venue}</span> </div></div></div>')


STADIUM = "".join([
    card("Fútbol", "Atlético de Madrid vs Viking FK", "25 · NOVIEMBRE · 2026", "atletico-vs-viking"),
    card("Fútbol", "Atlético de Madrid vs Betis", "5 O 6 · DICIEMBRE · 2026", "atletico-vs-betis"),
    card("Fútbol", "Atlético de Madrid vs Racing", "9 O 10 · ENERO · 2027", "atletico-vs-racing"),
    card("Deporte", "2027 UEFA Champions League Final", "5 · JUNIO · 2027", "2027-uefa-champions-league-final"),
    card("Música", "Harry Styles", "30 · JULIO · 2027 | 31 · JULIO · 2027 | 2 · AGOSTO · 2027 ", "harry-styles"),
    card("Deporte", "España vs Inglaterra", "15 · NOVIEMBRE · 2026", "espana-vs-inglaterra"),
])

CLUB = "".join([
    club_match("Atlético de Madrid", "Bayern Munich", "Martes 3 de noviembre", "21:00", "Riyadh Air Metropolitano"),
    club_match("Getafe", "Atlético de Madrid", "Domingo 22 de noviembre", "21:00", "Estadio Coliseum"),
    club_match("Atlético de Madrid", "Viking", "Miércoles 25 de noviembre", "21:00", "Riyadh Air Metropolitano",
               "UEFA Champions League"),
    club_match("Atlético de Madrid", "Betis", "Sábado 5 o domingo 6 de diciembre", "Sin confirmar",
               "Riyadh Air Metropolitano"),
    club_match("Atlético de Madrid", "Real Racing Club", "Sábado 9 de enero", "18:30", "Riyadh Air Metropolitano"),
    club_match("Atlético de Madrid", "Real Oviedo", "Miércoles 13 de enero", "21:30", "Riyadh Air Metropolitano",
               "Copa del Rey"),
])


class StadiumEventsTest(unittest.TestCase):
    def setUp(self):
        self.events = {e["id"]: e for e in feed.build(STADIUM, CLUB, TODAY)["events"]}

    def test_fixed_match_takes_the_clubs_kick_off(self):
        viking = self.events["atletico-vs-viking"]
        self.assertEqual((viking["days"], viking["either"], viking["time"]), (["2026-11-25"], False, "21:00"))
        self.assertEqual(viking["competition"], "UEFA Champions League")
        self.assertEqual(viking["level"], "busy")

    def test_unfixed_match_keeps_both_days(self):
        betis = self.events["atletico-vs-betis"]
        self.assertEqual((betis["days"], betis["either"], betis["time"]), (["2026-12-05", "2026-12-06"], True, None))

    def test_club_fixing_the_day_wins_over_the_stadiums_either_or(self):
        racing = self.events["atletico-vs-racing"]
        self.assertEqual((racing["days"], racing["either"], racing["time"]), (["2027-01-09"], False, "18:30"))

    def test_concert_tour_lists_every_night(self):
        harry = self.events["harry-styles"]
        self.assertEqual(harry["days"], ["2027-07-30", "2027-07-31", "2027-08-02"])
        self.assertEqual((harry["either"], harry["kind"], harry["level"]), (False, "concert", "max"))

    def test_final_is_the_biggest_level(self):
        final = self.events["2027-uefa-champions-league-final"]
        self.assertEqual((final["kind"], final["level"]), ("final", "max"))

    def test_other_events_have_no_time(self):
        spain = self.events["espana-vs-inglaterra"]
        self.assertEqual((spain["kind"], spain["time"]), ("match", None))

    def test_home_match_only_on_the_club_page_is_added(self):
        cup = self.events["atletico-de-madrid-vs-real-oviedo"]
        self.assertEqual((cup["days"], cup["time"], cup["competition"]), (["2027-01-13"], "21:30", "Copa del Rey"))

    def test_away_and_past_matches_are_left_out(self):
        self.assertNotIn("getafe-vs-atletico-de-madrid", self.events)
        self.assertFalse(any("bayern" in key for key in self.events))

    def test_sorted_by_first_day(self):
        days = [e["days"][0] for e in feed.build(STADIUM, CLUB, TODAY)["events"]]
        self.assertEqual(days, sorted(days))

    def test_empty_stadium_page_fails_instead_of_publishing_nothing(self):
        with self.assertRaises(ValueError):
            feed.build("<html>new layout</html>", CLUB, TODAY)


if __name__ == "__main__":
    unittest.main()
