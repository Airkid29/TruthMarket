# app.py — TruthMarket AI  v2
# Flask web app with premium design, team logos, confidence gauge, sparklines
# Usage:  python app.py   →  http://localhost:5000
# API:    GET /api/analyze?sport=worldcup|nba|ucl

from flask import Flask, jsonify, render_template, request, url_for, send_from_directory
import datetime
import logging
import time
from fetcher import fetch_sport_markets
from engine import run_full_analysis
from config import SPORT_LABELS, FLASK_HOST, FLASK_PORT, FLASK_DEBUG

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder='templates')
ANALYSIS_CACHE = {}
ANALYSIS_CACHE_TTL_SECONDS = 120

# ── Fallback logo URLs (used when Polymarket image is missing) ──────────────
# World Cup: country flag from flagcdn.com (free, no auth)
# NBA: official NBA CDN
# UCL: Wikipedia commons (reliable public domain)

WC_FLAG_CODES = {
    "Spain":"es","France":"fr","Argentina":"ar","England":"gb-eng","Brazil":"br",
    "Germany":"de","Portugal":"pt","Netherlands":"nl","Morocco":"ma","Croatia":"hr",
    "Belgium":"be","Italy":"it","Uruguay":"uy","USA":"us","Mexico":"mx",
    "Colombia":"co","Japan":"jp","Australia":"au","Senegal":"sn","Ecuador":"ec",
    "Canada":"ca","Switzerland":"ch","South Korea":"kr","Poland":"pl","Denmark":"dk",
    "Ghana":"gh","Cameroon":"cm","Costa Rica":"cr","Iran":"ir","Tunisia":"tn",
    "Saudi Arabia":"sa","Wales":"gb-wls","Serbia":"rs","Qatar":"qa",
}

NBA_LOGOS = {
    "Oklahoma City Thunder":"https://upload.wikimedia.org/wikipedia/en/8/81/Oklahoma_City_Thunder_logo.svg",
    "Boston Celtics":"https://upload.wikimedia.org/wikipedia/en/8/8f/Boston_Celtics.svg",
    "Denver Nuggets":"https://upload.wikimedia.org/wikipedia/en/thumb/7/76/Denver_Nuggets.svg/1200px-Denver_Nuggets.svg.png",
    "San Antonio Spurs":"https://upload.wikimedia.org/wikipedia/en/a/a2/San_Antonio_Spurs.svg",
    "Cleveland Cavaliers":"https://upload.wikimedia.org/wikipedia/en/4/4d/Cleveland_Cavaliers_logo.svg",
    "New York Knicks":"https://upload.wikimedia.org/wikipedia/en/2/25/New_York_Knicks_logo.svg",
    "Detroit Pistons":"https://upload.wikimedia.org/wikipedia/en/b/b8/Detroit_Pistons_logo.svg",
    "Minnesota Timberwolves":"https://upload.wikimedia.org/wikipedia/en/c/c2/Minnesota_Timberwolves_logo.svg",
    "Houston Rockets":"https://upload.wikimedia.org/wikipedia/en/2/28/Houston_Rockets.svg",
    "Golden State Warriors":"https://upload.wikimedia.org/wikipedia/en/0/01/Golden_State_Warriors_logo.svg",
    "Los Angeles Lakers":"https://upload.wikimedia.org/wikipedia/commons/3/3c/Los_Angeles_Lakers.svg",
    "Miami Heat":"https://upload.wikimedia.org/wikipedia/en/3/34/Miami_Heat_logo.svg",
    "Dallas Mavericks":"https://upload.wikimedia.org/wikipedia/en/9/9b/Dallas_Mavericks_logo.svg",
    "Atlanta Hawks":"https://upload.wikimedia.org/wikipedia/en/f/fb/Atlanta_Hawks_logo.svg",
    "Toronto Raptors":"https://upload.wikimedia.org/wikipedia/en/3/36/Toronto_Raptors_logo.svg",
    "Los Angeles Clippers":"https://upload.wikimedia.org/wikipedia/en/9/92/LA_Clippers_logo.svg",
    "Charlotte Hornets":"https://upload.wikimedia.org/wikipedia/en/thumb/4/4d/Charlotte_Hornets_%282014%29.svg/1200px-Charlotte_Hornets_%282014%29.svg.png",
    "Phoenix Suns":"https://upload.wikimedia.org/wikipedia/en/d/dc/Phoenix_Suns_logo.svg",
    "Orlando Magic":"https://upload.wikimedia.org/wikipedia/en/1/10/Orlando_Magic_logo.svg",
    "Indiana Pacers":"https://upload.wikimedia.org/wikipedia/en/0/05/Indiana_Pacers.svg",
    "Philadelphia 76ers":"https://upload.wikimedia.org/wikipedia/en/0/0e/Philadelphia_76ers_logo.svg",
    "Milwaukee Bucks":"https://upload.wikimedia.org/wikipedia/en/e/e8/Milwaukee_Bucks_logo.svg",
    "Sacramento Kings":"https://upload.wikimedia.org/wikipedia/en/9/9d/Sacramento_Kings_logo.svg",
    "Portland Trail Blazers":"https://upload.wikimedia.org/wikipedia/en/2/21/Portland_Trail_Blazers_logo.svg",
    "New Orleans Pelicans":"https://upload.wikimedia.org/wikipedia/en/0/0d/New_Orleans_Pelicans_logo.svg",
    "Chicago Bulls":"https://upload.wikimedia.org/wikipedia/en/6/67/Chicago_Bulls_logo.svg",
    "Washington Wizards":"https://upload.wikimedia.org/wikipedia/en/0/0e/Washington_Wizards_logo.svg",
    "Memphis Grizzlies":"https://upload.wikimedia.org/wikipedia/en/f/f1/Memphis_Grizzlies_logo.svg",
    "Brooklyn Nets":"https://upload.wikimedia.org/wikipedia/en/4/44/Brooklyn_Nets_logo.svg",
    "Utah Jazz":"https://upload.wikimedia.org/wikipedia/en/1/1a/Utah_Jazz_logo_%282022%29.svg",
}

UCL_LOGOS = {
    "Real Madrid":    "Logos/real.png",
    "Bayern Munich":  "https://upload.wikimedia.org/wikipedia/en/d/d1/FC_Bayern_M%C3%BCnchen_logo_%282017%E2%80%93present%29.svg",
    "Barcelona":      "https://upload.wikimedia.org/wikipedia/en/4/47/FC_Barcelona_%28crest%29.svg",
    "Arsenal":        "https://upload.wikimedia.org/wikipedia/en/5/53/Arsenal_FC.svg",
    "Liverpool":      "https://upload.wikimedia.org/wikipedia/en/0/0c/Liverpool_FC.svg",
    "Chelsea":        "https://upload.wikimedia.org/wikipedia/en/c/cc/Chelsea_FC.svg",
    "Man City":       "https://upload.wikimedia.org/wikipedia/en/e/eb/Manchester_City_FC_badge.svg",
    "Manchester City":"https://upload.wikimedia.org/wikipedia/en/e/eb/Manchester_City_FC_badge.svg",
    "PSG":            "https://upload.wikimedia.org/wikipedia/en/a/a7/Paris_Saint-Germain_F.C..svg",
    "Paris SG":       "https://upload.wikimedia.org/wikipedia/en/a/a7/Paris_Saint-Germain_F.C..svg",
    "Atletico Madrid":"https://upload.wikimedia.org/wikipedia/en/f/f4/Atletico_Madrid_2017_logo.svg",
    "Juventus":       "https://upload.wikimedia.org/wikipedia/commons/d/d5/Juventus_F.C._%282012%29.svg",
    "Dortmund":       "https://upload.wikimedia.org/wikipedia/commons/6/67/Borussia_Dortmund_logo.svg",
    "Benfica":        "https://upload.wikimedia.org/wikipedia/en/a/a2/SL_Benfica_logo.svg",
    "Inter Milan":    "https://upload.wikimedia.org/wikipedia/commons/0/05/FC_Internazionale_Milano_2021.svg",
    "Porto":          "https://upload.wikimedia.org/wikipedia/en/3/36/FC_Porto.svg",
    "Ajax":           "https://upload.wikimedia.org/wikipedia/en/7/79/Ajax_Amsterdam.svg",
    "Aston Villa":    "https://upload.wikimedia.org/wikipedia/en/9/9f/Aston_Villa_FC_crest_%282016%29.svg",
    "Bayer Leverkusen":"https://upload.wikimedia.org/wikipedia/en/5/59/Bayer_04_Leverkusen_logo.svg",
    "Feyenoord":      "https://upload.wikimedia.org/wikipedia/commons/5/5e/Feyenoord.svg",
    "AC Milan":       "https://upload.wikimedia.org/wikipedia/en/d/d0/A.C._Milan.svg",
    "Roma":           "https://upload.wikimedia.org/wikipedia/en/f/f7/AS_Roma_2017_logo.svg",
    "Napoli":         "https://upload.wikimedia.org/wikipedia/en/2/2e/S.S.C._Napoli_logo.svg",
    "Tottenham":      "https://upload.wikimedia.org/wikipedia/en/b/b4/Tottenham_Hotspur.svg",
    "Manchester United":"https://upload.wikimedia.org/wikipedia/en/7/7a/Manchester_United_FC_badge.svg",
}

LOCAL_LOGO_FILES = {
    "Oklahoma City Thunder": "okc.png",
    "Boston Celtics": "celtics.png",
    "Denver Nuggets": "nuggets.png",
    "San Antonio Spurs": "spurs.png",
    "Cleveland Cavaliers": "cavaliers.png",
    "New York Knicks": "knicks.png",
    "Detroit Pistons": "pistons.png",
    "Minnesota Timberwolves": "timberwolves.png",
    "Houston Rockets": "rockets.svg",
    "Golden State Warriors": "warriors.png",
    "Los Angeles Lakers": "lakers.png",
    "Miami Heat": "heat.png",
    "Atlanta Hawks": "hawks.png",
    "Toronto Raptors": "raptors.png",
    "Los Angeles Clippers": "clippers.png",
    "Charlotte Hornets": "hornets.webp",
    "Phoenix Suns": "suns.png",
    "Orlando Magic": "orlando.png",
    "Philadelphia 76ers": "76ers.png",
    "Portland Trail Blazers": "blazers.png",
    "Bayern Munich": "Bayern.png",
    "Barcelona": "barca.png",
    "Arsenal": "arsenal.png",
    "Liverpool": "liverpool.svg",
    "PSG": "psg.jpeg",
    "Paris SG": "psg.jpeg",
    "Real Madrid": "real.png",
    "Atletico Madrid": "atletico.png",
    "Club Brugge": "brugge.png",
}

def get_logo_url(team_resolved: str, sport: str, polymarket_url: str = "") -> str:
    """Return best available logo URL for a team."""
    if polymarket_url and polymarket_url.startswith("http"):
        return polymarket_url

    local_file = LOCAL_LOGO_FILES.get(team_resolved)
    if local_file:
        return url_for("logo_file", filename=local_file)

    if sport == "worldcup":
        code = WC_FLAG_CODES.get(team_resolved, "")
        if code:
            return f"https://flagcdn.com/h40/{code}.png"
    elif sport == "nba":
        return NBA_LOGOS.get(team_resolved, "")
    elif sport == "ucl":
        return UCL_LOGOS.get(team_resolved, "")
    return ""

# ── Flask routes ─────────────────────────────────────────────────────────────

@app.route("/api/analyze")
def api_analyze():
    sport = request.args.get("sport", "worldcup")
    if sport not in ("worldcup", "nba", "ucl"):
        return jsonify({"error": "sport must be worldcup, nba, or ucl"}), 400

    cached = ANALYSIS_CACHE.get(sport)
    now = time.time()
    if cached and (now - cached["ts"]) < ANALYSIS_CACHE_TTL_SECONDS:
        return jsonify(cached["payload"])

    markets = fetch_sport_markets(sport)

    # Inject fallback logos where Polymarket didn't provide one
    for m in markets:
        if not m.get("logo_url"):
            m["logo_url"] = get_logo_url(m["team"], sport)

    results = run_full_analysis(markets, sport)

    # Ensure logo_url is in each result (engine propagates it from market data)
    for r in results:
        if not r.get("logo_url"):
            r["logo_url"] = get_logo_url(r.get("team_resolved", r.get("team","")), sport)

    payload = {
        "sport":         sport,
        "label":         SPORT_LABELS.get(sport, sport),
        "generated_at":  datetime.datetime.utcnow().isoformat() + "Z",
        "total_markets": len(markets),
        "analyzed":      len(results),
        "summary": {
            "bet_against":   sum(1 for r in results if r["signal"] == "BET AGAINST"),
            "follow_market": sum(1 for r in results if r["signal"] == "FOLLOW MARKET"),
            "hold":          sum(1 for r in results if r["signal"] == "HOLD"),
        },
        "results": results,
    }
    ANALYSIS_CACHE[sport] = {"ts": now, "payload": payload}
    return jsonify(payload)


@app.route("/logos/<path:filename>")
def logo_file(filename):
    return send_from_directory("Logos", filename)


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    logger.info("Starting TruthMarket AI Flask server")
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG)