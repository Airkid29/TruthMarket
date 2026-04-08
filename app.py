# app.py — TruthMarket AI  v2
# Flask web app with premium design, team logos, confidence gauge, sparklines
# Usage:  python app.py   →  http://localhost:5000
# API:    GET /api/analyze?sport=worldcup|nba|ucl

from flask import Flask, jsonify, render_template, request
import datetime
import logging
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
    "Oklahoma City Thunder":"thunder","Boston Celtics":"celtics",
    "Denver Nuggets":"nuggets","San Antonio Spurs":"spurs",
    "Cleveland Cavaliers":"cavaliers","New York Knicks":"knicks",
    "Detroit Pistons":"pistons","Minnesota Timberwolves":"timberwolves",
    "Houston Rockets":"rockets","Golden State Warriors":"warriors",
    "Los Angeles Lakers":"lakers","Miami Heat":"heat",
    "Dallas Mavericks":"mavericks","Atlanta Hawks":"hawks",
    "Toronto Raptors":"raptors","Los Angeles Clippers":"clippers",
    "Charlotte Hornets":"hornets","Phoenix Suns":"suns",
    "Orlando Magic":"magic","Indiana Pacers":"pacers",
    "Philadelphia 76ers":"sixers","Milwaukee Bucks":"bucks",
    "Sacramento Kings":"kings","Portland Trail Blazers":"blazers",
    "New Orleans Pelicans":"pelicans","Chicago Bulls":"bulls",
    "Washington Wizards":"wizards","Memphis Grizzlies":"grizzlies",
    "Brooklyn Nets":"nets","Utah Jazz":"jazz",
}

UCL_LOGOS = {
    "Real Madrid":    "https://upload.wikimedia.org/wikipedia/en/5/56/Real_Madrid_CF.svg",
    "Bayern Munich":  "https://upload.wikimedia.org/wikipedia/commons/1/1b/FC_Bayern_M%C3%BCnchen_logo_%282002%E2%80%932017%29.svg",
    "Barcelona":      "https://upload.wikimedia.org/wikipedia/en/4/47/FC_Barcelona_%28crest%29.svg",
    "Arsenal":        "https://upload.wikimedia.org/wikipedia/en/5/53/Arsenal_FC.svg",
    "Liverpool":      "https://upload.wikimedia.org/wikipedia/en/0/0c/Liverpool_FC.svg",
    "Chelsea":        "https://upload.wikimedia.org/wikipedia/en/c/cc/Chelsea_FC.svg",
    "Man City":       "https://upload.wikimedia.org/wikipedia/en/e/eb/Manchester_City_FC_badge.svg",
    "PSG":            "https://upload.wikimedia.org/wikipedia/en/a/a7/Paris_Saint-Germain_F.C..svg",
    "Atletico Madrid":"https://upload.wikimedia.org/wikipedia/en/f/f4/Atletico_Madrid_2017_logo.svg",
    "Juventus":       "https://upload.wikimedia.org/wikipedia/commons/1/15/Juventus_FC_2017_icon_%28black%29.svg",
    "Dortmund":       "https://upload.wikimedia.org/wikipedia/commons/6/67/Borussia_Dortmund_logo.svg",
    "Benfica":        "https://upload.wikimedia.org/wikipedia/en/a/a2/SL_Benfica_logo.svg",
    "Inter Milan":    "https://upload.wikimedia.org/wikipedia/commons/0/05/FC_Internazionale_Milano_2021.svg",
    "Porto":          "https://upload.wikimedia.org/wikipedia/en/3/36/FC_Porto.svg",
    "Ajax":           "https://upload.wikimedia.org/wikipedia/en/7/79/Ajax_Amsterdam.svg",
    "Aston Villa":    "https://upload.wikimedia.org/wikipedia/en/9/9f/Aston_Villa_FC_crest_%282016%29.svg",
    "Bayer Leverkusen":"https://upload.wikimedia.org/wikipedia/en/5/59/Bayer_04_Leverkusen_logo.svg",
    "Feyenoord":      "https://upload.wikimedia.org/wikipedia/commons/5/5e/Feyenoord.svg",
}

def get_logo_url(team_resolved: str, sport: str, polymarket_url: str = "") -> str:
    """Return best available logo URL for a team."""
    if polymarket_url and polymarket_url.startswith("http"):
        return polymarket_url
    if sport == "worldcup":
        code = WC_FLAG_CODES.get(team_resolved, "")
        if code:
            return f"https://flagcdn.com/h40/{code}.png"
    elif sport == "nba":
        slug = NBA_LOGOS.get(team_resolved, "")
        if slug:
            return f"https://cdn.nba.com/logos/nba/1610612/{slug}/global/L/logo.svg"
    elif sport == "ucl":
        return UCL_LOGOS.get(team_resolved, "")
    return ""

# ── Flask routes ─────────────────────────────────────────────────────────────

@app.route("/api/analyze")
def api_analyze():
    sport = request.args.get("sport", "worldcup")
    if sport not in ("worldcup", "nba", "ucl"):
        return jsonify({"error": "sport must be worldcup, nba, or ucl"}), 400

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

    return jsonify({
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
    })


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    logger.info("Starting TruthMarket AI Flask server")
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG)