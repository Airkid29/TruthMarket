# data.py — TruthMarket AI
# Sources: FIFA World Rankings (April 2026), ELO ratings, official tournament records
# ELO ratings from eloratings.net (converted to win probability baseline)

# ─────────────────────────────────────────────
# WORLD CUP HISTORICAL DATA
# Source: FIFA official records 1930-2022 (22 editions)
# ELO rating converted to implied win prob via:
#   P(win) = 1 / (1 + 10^((elo_opponent - elo_team)/400))
#   We use tournament-adjusted ELO as of Jan 2026
# ─────────────────────────────────────────────

WORLDCUP_DATA = {
    # team_name: {
    #   titles: int,           # WC titles won
    #   finals: int,           # WC finals reached
    #   participations: int,   # WC participations
    #   elo: float,            # ELO rating Jan 2026 (source: eloratings.net)
    #   last_wc: str,          # last WC result (QF, SF, F, W = winner, G = group stage)
    # }
    "Spain":       {"titles": 1, "finals": 1, "participations": 16, "elo": 2085, "last_wc": "QF"},
    "France":      {"titles": 2, "finals": 3, "participations": 16, "elo": 2055, "last_wc": "F"},
    "Argentina":   {"titles": 3, "finals": 5, "participations": 18, "elo": 2140, "last_wc": "W"},
    "England":     {"titles": 1, "finals": 1, "participations": 16, "elo": 2010, "last_wc": "QF"},
    "Brazil":      {"titles": 5, "finals": 7, "participations": 22, "elo": 2060, "last_wc": "QF"},
    "Germany":     {"titles": 4, "finals": 8, "participations": 20, "elo": 1990, "last_wc": "G"},
    "Portugal":    {"titles": 0, "finals": 0, "participations": 8,  "elo": 2020, "last_wc": "QF"},
    "Netherlands": {"titles": 0, "finals": 3, "participations": 11, "elo": 1985, "last_wc": "SF"},
    "Morocco":     {"titles": 0, "finals": 0, "participations": 6,  "elo": 1900, "last_wc": "SF"},
    "Croatia":     {"titles": 0, "finals": 1, "participations": 6,  "elo": 1950, "last_wc": "3rd"},
    "Belgium":     {"titles": 0, "finals": 0, "participations": 14, "elo": 1960, "last_wc": "QF"},
    "Italy":       {"titles": 4, "finals": 6, "participations": 18, "elo": 1940, "last_wc": "G"},
    "Uruguay":     {"titles": 2, "finals": 3, "participations": 14, "elo": 1890, "last_wc": "G"},
    "USA":         {"titles": 0, "finals": 0, "participations": 11, "elo": 1870, "last_wc": "R16"},
    "Mexico":      {"titles": 0, "finals": 0, "participations": 17, "elo": 1850, "last_wc": "G"},
    "Colombia":    {"titles": 0, "finals": 0, "participations": 6,  "elo": 1870, "last_wc": "R16"},
    "Japan":       {"titles": 0, "finals": 0, "participations": 7,  "elo": 1890, "last_wc": "R16"},
    "Australia":   {"titles": 0, "finals": 0, "participations": 5,  "elo": 1810, "last_wc": "QF"},
    "Senegal":     {"titles": 0, "finals": 0, "participations": 3,  "elo": 1830, "last_wc": "R16"},
    "Ecuador":     {"titles": 0, "finals": 0, "participations": 4,  "elo": 1800, "last_wc": "G"},
    "Canada":      {"titles": 0, "finals": 0, "participations": 1,  "elo": 1790, "last_wc": "G"},
    "Switzerland": {"titles": 0, "finals": 0, "participations": 12, "elo": 1880, "last_wc": "QF"},
    "South Korea": {"titles": 0, "finals": 0, "participations": 10, "elo": 1840, "last_wc": "R16"},
    "Poland":      {"titles": 0, "finals": 0, "participations": 9,  "elo": 1820, "last_wc": "R16"},
    "Denmark":     {"titles": 0, "finals": 0, "participations": 5,  "elo": 1880, "last_wc": "R16"},
    "Ghana":       {"titles": 0, "finals": 0, "participations": 4,  "elo": 1780, "last_wc": "G"},
    "Cameroon":    {"titles": 0, "finals": 0, "participations": 8,  "elo": 1770, "last_wc": "G"},
    "Costa Rica":  {"titles": 0, "finals": 0, "participations": 6,  "elo": 1760, "last_wc": "G"},
    "Iran":        {"titles": 0, "finals": 0, "participations": 6,  "elo": 1770, "last_wc": "G"},
    "Tunisia":     {"titles": 0, "finals": 0, "participations": 6,  "elo": 1750, "last_wc": "G"},
    "Saudi Arabia":{"titles": 0, "finals": 0, "participations": 6,  "elo": 1760, "last_wc": "G"},
    "Wales":       {"titles": 0, "finals": 0, "participations": 2,  "elo": 1820, "last_wc": "G"},
    "Serbia":      {"titles": 0, "finals": 0, "participations": 5,  "elo": 1840, "last_wc": "G"},
    "Cameroon":    {"titles": 0, "finals": 0, "participations": 8,  "elo": 1770, "last_wc": "G"},
    "Qatar":       {"titles": 0, "finals": 0, "participations": 1,  "elo": 1720, "last_wc": "G"},
}

# ─────────────────────────────────────────────
# NBA HISTORICAL DATA
# Source: NBA official records 1946-2025
# recent_elo: aggregate team strength score based on
#   last 5 seasons win%, playoff appearances, roster rating
# ─────────────────────────────────────────────

NBA_DATA = {
    # Polymarket uses "the X" format — we store clean name, fetcher strips "the "
    "Oklahoma City Thunder": {"titles": 1, "finals": 3, "seasons": 17, "recent_elo": 1820, "last_season": "W-Conference Finals"},
    "Boston Celtics":        {"titles": 18,"finals": 22,"seasons": 79, "recent_elo": 1780, "last_season": "Champions 2024"},
    "Denver Nuggets":        {"titles": 1, "finals": 1, "seasons": 55, "recent_elo": 1740, "last_season": "R1 exit"},
    "San Antonio Spurs":     {"titles": 5, "finals": 6, "seasons": 49, "recent_elo": 1390, "last_season": "Lottery"},
    "Cleveland Cavaliers":   {"titles": 1, "finals": 1, "seasons": 55, "recent_elo": 1700, "last_season": "Conference SF"},
    "New York Knicks":       {"titles": 2, "finals": 2, "seasons": 79, "recent_elo": 1680, "last_season": "Conference SF"},
    "Detroit Pistons":       {"titles": 3, "finals": 3, "seasons": 68, "recent_elo": 1560, "last_season": "Playoffs R1"},
    "Minnesota Timberwolves":{"titles": 0, "finals": 0, "seasons": 36, "recent_elo": 1660, "last_season": "Conference Finals"},
    "Houston Rockets":       {"titles": 2, "finals": 2, "seasons": 55, "recent_elo": 1620, "last_season": "Playoffs R2"},
    "Golden State Warriors": {"titles": 7, "finals": 7, "seasons": 79, "recent_elo": 1610, "last_season": "Missed playoffs"},
    "Los Angeles Lakers":    {"titles": 17,"finals": 17,"seasons": 77, "recent_elo": 1600, "last_season": "Playoffs R1"},
    "Miami Heat":            {"titles": 3, "finals": 3, "seasons": 37, "recent_elo": 1580, "last_season": "Missed playoffs"},
    "Dallas Mavericks":      {"titles": 1, "finals": 2, "seasons": 45, "recent_elo": 1550, "last_season": "Missed playoffs"},
    "Atlanta Hawks":         {"titles": 1, "finals": 1, "seasons": 75, "recent_elo": 1540, "last_season": "Missed playoffs"},
    "Toronto Raptors":       {"titles": 1, "finals": 1, "seasons": 30, "recent_elo": 1510, "last_season": "Missed playoffs"},
    "Los Angeles Clippers":  {"titles": 0, "finals": 0, "seasons": 50, "recent_elo": 1520, "last_season": "Missed playoffs"},
    "Charlotte Hornets":     {"titles": 0, "finals": 0, "seasons": 34, "recent_elo": 1490, "last_season": "Missed playoffs"},
    "Phoenix Suns":          {"titles": 0, "finals": 2, "seasons": 57, "recent_elo": 1500, "last_season": "Missed playoffs"},
    "Orlando Magic":         {"titles": 0, "finals": 2, "seasons": 36, "recent_elo": 1530, "last_season": "Playoffs R1"},
    "Indiana Pacers":        {"titles": 0, "finals": 1, "seasons": 57, "recent_elo": 1540, "last_season": "Conference Finals"},
    "Philadelphia 76ers":    {"titles": 3, "finals": 3, "seasons": 76, "recent_elo": 1510, "last_season": "Missed playoffs"},
    "Milwaukee Bucks":       {"titles": 2, "finals": 2, "seasons": 57, "recent_elo": 1490, "last_season": "Missed playoffs"},
    "Sacramento Kings":      {"titles": 1, "finals": 1, "seasons": 75, "recent_elo": 1470, "last_season": "Missed playoffs"},
    "Portland Trail Blazers":{"titles": 1, "finals": 1, "seasons": 55, "recent_elo": 1420, "last_season": "Missed playoffs"},
    "New Orleans Pelicans":  {"titles": 0, "finals": 0, "seasons": 22, "recent_elo": 1380, "last_season": "Missed playoffs"},
    "Chicago Bulls":         {"titles": 6, "finals": 6, "seasons": 79, "recent_elo": 1360, "last_season": "Missed playoffs"},
    "Washington Wizards":    {"titles": 1, "finals": 1, "seasons": 66, "recent_elo": 1300, "last_season": "Lottery"},
    "Memphis Grizzlies":     {"titles": 0, "finals": 0, "seasons": 24, "recent_elo": 1350, "last_season": "Missed playoffs"},
    "Brooklyn Nets":         {"titles": 0, "finals": 0, "seasons": 50, "recent_elo": 1280, "last_season": "Lottery"},
    "Utah Jazz":             {"titles": 0, "finals": 2, "seasons": 50, "recent_elo": 1260, "last_season": "Lottery"},
}

# ─────────────────────────────────────────────
# UEFA CHAMPIONS LEAGUE DATA
# Source: UEFA official records 1955-2025
# recent_elo: squad quality score from
#   TransferMarkt squad value + UCL coefficient
# ─────────────────────────────────────────────

UCL_DATA = {
    "Real Madrid":   {"titles": 15, "finals": 17, "seasons": 70, "recent_elo": 2100, "last_ucl": "W"},
    "Bayern Munich": {"titles": 6,  "finals": 11, "seasons": 65, "recent_elo": 2020, "last_ucl": "SF"},
    "Barcelona":     {"titles": 5,  "finals": 11, "seasons": 68, "recent_elo": 1990, "last_ucl": "SF"},
    "Arsenal":       {"titles": 0,  "finals": 1,  "seasons": 20, "recent_elo": 1980, "last_ucl": "QF"},
    "Liverpool":     {"titles": 6,  "finals": 10, "seasons": 55, "recent_elo": 1970, "last_ucl": "R16"},
    "Chelsea":       {"titles": 2,  "finals": 3,  "seasons": 25, "recent_elo": 1920, "last_ucl": "QF"},
    "Man City":      {"titles": 1,  "finals": 2,  "seasons": 15, "recent_elo": 1960, "last_ucl": "SF"},
    "PSG":           {"titles": 0,  "finals": 1,  "seasons": 30, "recent_elo": 1950, "last_ucl": "QF"},
    "Atletico Madrid":{"titles": 0, "finals": 2,  "seasons": 25, "recent_elo": 1890, "last_ucl": "R16"},
    "Juventus":      {"titles": 2,  "finals": 9,  "seasons": 55, "recent_elo": 1870, "last_ucl": "R16"},
    "Dortmund":      {"titles": 1,  "finals": 3,  "seasons": 30, "recent_elo": 1880, "last_ucl": "F"},
    "Benfica":       {"titles": 2,  "finals": 8,  "seasons": 60, "recent_elo": 1850, "last_ucl": "QF"},
    "Inter Milan":   {"titles": 3,  "finals": 6,  "seasons": 50, "recent_elo": 1900, "last_ucl": "F"},
    "Porto":         {"titles": 2,  "finals": 2,  "seasons": 45, "recent_elo": 1840, "last_ucl": "R16"},
    "Ajax":          {"titles": 4,  "finals": 6,  "seasons": 55, "recent_elo": 1820, "last_ucl": "G"},
    "Nice":          {"titles": 0,  "finals": 0,  "seasons": 3,  "recent_elo": 1750, "last_ucl": "R16"},
    "Aston Villa":   {"titles": 1,  "finals": 1,  "seasons": 5,  "recent_elo": 1800, "last_ucl": "QF"},
    "Bayer Leverkusen":{"titles": 0,"finals": 1,  "seasons": 10, "recent_elo": 1860, "last_ucl": "QF"},
    "Feyenoord":     {"titles": 2,  "finals": 2,  "seasons": 20, "recent_elo": 1780, "last_ucl": "R16"},
    "Club Brugge":   {"titles": 0,  "finals": 0,  "seasons": 15, "recent_elo": 1720, "last_ucl": "G"},
}

# Polymarket name → our data key (handle abbreviations/nicknames)
WORLDCUP_ALIASES = {
    "England": "England",
    "United States": "USA",
    "United States of America": "USA",
    "South Korea": "South Korea",
    "Republic of Korea": "South Korea",
    "IR Iran": "Iran",
}

NBA_ALIASES = {
    "Oklahoma City Thunder": "Oklahoma City Thunder",
    "Boston Celtics": "Boston Celtics",
    "San Antonio Spurs": "San Antonio Spurs",
    "Golden State Warriors": "Golden State Warriors",
    "Los Angeles Lakers": "Los Angeles Lakers",
    "Los Angeles Clippers": "Los Angeles Clippers",
    "Philadelphia 76ers": "Philadelphia 76ers",
    "Portland Trail Blazers": "Portland Trail Blazers",
}

UCL_ALIASES = {
    "Real Madrid": "Real Madrid",
    "Bayern Munich": "Bayern Munich",
    "Barcelona": "Barcelona",
    "Arsenal": "Arsenal",
    "Liverpool": "Liverpool",
    "Chelsea": "Chelsea",
    "Man City": "Man City",
    "Manchester City": "Man City",
    "PSG": "PSG",
    "Paris Saint-Germain": "PSG",
    "Atletico": "Atletico Madrid",
    "Atletico Madrid": "Atletico Madrid",
    "Juventus": "Juventus",
    "Dortmund": "Dortmund",
    "Borussia Dortmund": "Dortmund",
    "Inter": "Inter Milan",
    "Inter Milan": "Inter Milan",
    "Leverkusen": "Bayer Leverkusen",
    "Bayer Leverkusen": "Bayer Leverkusen",
    "Aston Villa": "Aston Villa",
    "Benfica": "Benfica",
    "Ajax": "Ajax",
    "Porto": "Porto",
    "Feyenoord": "Feyenoord",
    "Nice": "Nice",
    "Club Brugge": "Club Brugge",
}