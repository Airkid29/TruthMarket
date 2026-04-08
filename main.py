# main.py — TruthMarket AI
# Run this to fetch live data, analyze it, and save results.json
# Usage: python main.py

import json
import datetime
import logging
from fetcher import fetch_all_sports
from engine import run_full_analysis
from config import SPORT_SLUGS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

SPORT_LABELS = {
    "worldcup": "FIFA World Cup 2026",
    "nba":      "NBA Champion 2026",
    "ucl":      "UEFA Champions League 2025-26",
}

SPORT_ICONS = {
    "worldcup": "soccer",
    "nba":      "basketball",
    "ucl":      "trophy",
}


def main() -> None:
    """Main entry point for TruthMarket AI analysis."""
    print()
    print("=" * 65)
    print("  TRUTHMARKET AI — Sports Decision Engine")
    print("  Prediction markets vs historical reality")
    print("=" * 65)
    print()

    # 1. Fetch live Polymarket data
    logger.info("Fetching live Polymarket data...")
    print("[1/3] Fetching live Polymarket data...")
    raw_data = fetch_all_sports()

    # 2. Run analysis for each sport
    print()
    print("[2/3] Running analysis...")
    output = {
        "generated_at": datetime.datetime.utcnow().isoformat() + "Z",
        "sports": {}
    }

    for sport, markets in raw_data.items():
        print(f"\n  ── {SPORT_LABELS[sport]} ──")
        if not markets:
            logger.warning(f"No data available for {sport}")
            print("  No data available.")
            output["sports"][sport] = {"label": SPORT_LABELS[sport], "results": [], "summary": {}}
            continue

        results = run_full_analysis(markets, sport)

        # Summary stats
        against = [r for r in results if r["signal"] == "BET AGAINST"]
        follow = [r for r in results if r["signal"] == "FOLLOW MARKET"]
        hold = [r for r in results if r["signal"] == "HOLD"]

        logger.info(f"Analyzed {len(results)} teams for {sport}: {len(against)} against, {len(follow)} follow, {len(hold)} hold")
        print(f"  Analyzed: {len(results)} teams")
        print(f"  Signals  → BET AGAINST: {len(against)} | FOLLOW: {len(follow)} | HOLD: {len(hold)}")

        # Print top signals
        for r in results[:5]:
            arrow = "↑" if r["signal"] == "FOLLOW MARKET" else "↓" if r["signal"] == "BET AGAINST" else "→"
            print(f"    {arrow} {r['team_resolved']:25s} | Market {r['market_prob']:5.1f}% | Model {r['model_prob']:5.1f}% | {r['signal']}")

        output["sports"][sport] = {
            "label": SPORT_LABELS[sport],
            "icon": SPORT_ICONS[sport],
            "total_markets": len(markets),
            "analyzed": len(results),
            "summary": {
                "bet_against": len(against),
                "follow_market": len(follow),
                "hold": len(hold),
            },
            "results": results,
        }

    # 3. Save to results.json
    print()
    print("[3/3] Saving results.json...")
    try:
        with open("results.json", "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        logger.info("Results saved to results.json")
    except IOError as e:
        logger.error(f"Failed to save results.json: {e}")
        print(f"Error saving results: {e}")
        return

    print()
    print("=" * 65)
    print("  DONE. results.json ready.")

    # Print top opportunities across all sports
    all_against = []
    all_follow = []
    for sport, data in output["sports"].items():
        for r in data.get("results", []):
            r["_sport"] = SPORT_LABELS[sport]
            if r["signal"] == "BET AGAINST":
                all_against.append(r)
            elif r["signal"] == "FOLLOW MARKET":
                all_follow.append(r)

    all_against.sort(key=lambda x: -x["divergence"])
    all_follow.sort(key=lambda x: x["divergence"])

    if all_against:
        print()
        print("  TOP OVERPRICED (Bet Against):")
        for r in all_against[:3]:
            print(f"    ● {r['team_resolved']} ({r['_sport']}): market {r['market_prob']}% vs model {r['model_prob']}% (+{r['divergence']}pp)")

    if all_follow:
        print()
        print("  TOP UNDERPRICED (Follow Market):")
        for r in all_follow[:3]:
            print(f"    ● {r['team_resolved']} ({r['_sport']}): market {r['market_prob']}% vs model {r['model_prob']}% ({r['divergence']}pp)")

    print()
    print("  Run: python app.py  to launch the web interface")
    print("=" * 65)
    print()


if __name__ == "__main__":
    main()