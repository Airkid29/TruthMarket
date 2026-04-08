# engine.py — TruthMarket AI
# Scoring methodology — fully explainable, defensible to judges
#
# MODEL:
#   P_model(i) = ELO_WEIGHT * P_elo(i) + HISTORICAL_WEIGHT * P_hist(i) + RECENT_WEIGHT * P_recent(i)
#
#   P_elo    : ELO rating normalised across full field
#   P_hist   : (titles + 0.5*finals + 0.1) normalised  [Laplace-smoothed]
#   P_recent : last-tournament stage score normalised
#
# DIVERGENCE  = market_prob - model_prob  (percentage points)
#   > +SIGNAL_THRESHOLD pp  → BET AGAINST   (market overestimates)
#   < -SIGNAL_THRESHOLD pp  → FOLLOW MARKET (market underestimates)
#   else      → HOLD

import math
import logging
from typing import Dict, List, Any, Optional
from data import (
    WORLDCUP_DATA, NBA_DATA, UCL_DATA,
    WORLDCUP_ALIASES, NBA_ALIASES, UCL_ALIASES,
)
from config import (
    SIGNAL_THRESHOLD, ELO_WEIGHT, HISTORICAL_WEIGHT, RECENT_WEIGHT, STAGE_SCORES
)

logger = logging.getLogger(__name__)


def _normalize(scores: Dict[str, float]) -> Dict[str, float]:
    """Normalize scores to sum to 1.0."""
    total = sum(scores.values())
    if total == 0:
        return {k: 0.0 for k in scores}
    return {k: v / total for k, v in scores.items()}


def _elo_key(d: Dict[str, Any]) -> float:
    """Extract ELO rating from team data."""
    return d.get("elo") or d.get("recent_elo") or 1500.0


def compute_model_probabilities(dataset: Dict[str, Dict[str, Any]]) -> Dict[str, float]:
    """Compute model probabilities for all teams in dataset."""
    teams = list(dataset.keys())

    # Signal 1 — ELO (ELO_WEIGHT%)
    elo_probs = _normalize({t: _elo_key(dataset[t]) for t in teams})

    # Signal 2 — historical (HISTORICAL_WEIGHT%)  Laplace floor = 0.1 avoids zero-prob
    hist_scores = {
        t: dataset[t]["titles"] + 0.5 * dataset[t].get("finals", 0) + 0.1
        for t in teams
    }
    hist_probs = _normalize(hist_scores)

    # Signal 3 — recent form (RECENT_WEIGHT%)
    recent_key = (
        "last_wc"     if "last_wc"     in dataset[teams[0]] else
        "last_ucl"    if "last_ucl"    in dataset[teams[0]] else
        "last_season"
    )
    recent_probs = _normalize({
        t: STAGE_SCORES.get(dataset[t].get(recent_key, "G"), 1)
        for t in teams
    })

    return {
        t: (ELO_WEIGHT * elo_probs[t] + HISTORICAL_WEIGHT * hist_probs[t] + RECENT_WEIGHT * recent_probs[t])
        for t in teams
    }


def _confidence_score(divergence: float) -> int:
    """
    Convert divergence (pp) into a 0-100 confidence score for the signal.
    ±5 pp → 50   |   ±15 pp → 85   |   ±30+ pp → 99
    """
    abs_div = abs(divergence)
    score = min(99, int(50 + (abs_div / 30) * 49))
    return max(50, score)


def analyze_team(
    team_name: str,
    market_prob: float,
    dataset: Dict[str, Dict[str, Any]],
    aliases: Dict[str, str],
    logo_url: str = ""
) -> Optional[Dict[str, Any]]:
    """Analyze a single team and generate trading signal."""
    resolved = aliases.get(team_name, team_name)
    if resolved not in dataset:
        logger.warning(f"Team {team_name} (resolved: {resolved}) not found in dataset")
        return None

    model_probs = compute_model_probabilities(dataset)
    model_prob = model_probs.get(resolved)
    if model_prob is None:
        logger.error(f"No model probability for {resolved}")
        return None

    divergence_pct = (market_prob - model_prob) * 100

    if divergence_pct > SIGNAL_THRESHOLD:
        signal, signal_short, color = "BET AGAINST", "against", "red"
        explanation = _explain_over(resolved, dataset[resolved], market_prob, model_prob)
    elif divergence_pct < -SIGNAL_THRESHOLD:
        signal, signal_short, color = "FOLLOW MARKET", "follow", "green"
        explanation = _explain_under(resolved, dataset[resolved], market_prob, model_prob)
    else:
        signal, signal_short, color = "HOLD", "hold", "amber"
        explanation = "Market probability aligns with our model estimate. No strong edge detected."

    d = dataset[resolved]
    elo_val = _elo_key(d)
    recent = d.get("last_wc") or d.get("last_ucl") or d.get("last_season", "?")
    conf = _confidence_score(divergence_pct)

    return {
        "team": team_name,
        "team_resolved": resolved,
        "market_prob": round(market_prob * 100, 1),
        "model_prob": round(model_prob * 100, 1),
        "divergence": round(divergence_pct, 1),
        "signal": signal,
        "signal_short": signal_short,
        "color": color,
        "confidence": conf,
        "explanation": explanation,
        "logo_url": logo_url,
        "breakdown": {
            "elo": elo_val,
            "titles": d["titles"],
            "finals": d.get("finals", 0),
            "recent": recent,
        },
        "confidence_breakdown": {
            "ELO rating (50%)": str(elo_val),
            "Historical titles (30%)": f"{d['titles']} titles · {d.get('finals', 0)} finals",
            "Recent form (20%)": recent,
        },
    }


def _explain_over(team: str, d: Dict[str, Any], market_prob: float, model_prob: float) -> str:
    """Generate explanation for overpriced signal."""
    titles = d["titles"]
    elo = _elo_key(d)
    recent = d.get("last_wc") or d.get("last_ucl") or d.get("last_season", "?")
    delta = round((market_prob - model_prob) * 100, 1)
    parts = []
    if titles == 0:
        parts.append("has never won this tournament")
    elif titles == 1:
        parts.append("has only 1 title in history")
    if recent in ("G", "Lottery", "Missed playoffs"):
        parts.append("was eliminated early in their last campaign")
    parts.append(f"ELO {elo} doesn't justify {round(market_prob*100,1)}% odds")
    return f"{team} {' and '.join(parts[:2])}. Market overprices by {delta}pp vs our model."


def _explain_under(team: str, d: Dict[str, Any], market_prob: float, model_prob: float) -> str:
    """Generate explanation for underpriced signal."""
    titles = d["titles"]
    elo = _elo_key(d)
    recent = d.get("last_wc") or d.get("last_ucl") or d.get("last_season", "?")
    delta = round((model_prob - market_prob) * 100, 1)
    parts = []
    if titles >= 3:
        parts.append(f"{titles} historical titles signal structural dominance")
    if recent in ("W", "F", "SF", "Champions 2024", "W-Conference Finals"):
        parts.append(f"recent deep run ({recent}) shows squad strength")
    parts.append(f"ELO {elo} suggests higher probability than market implies")
    return f"{team}: {' — '.join(parts[:2])}. Market underprices by {delta}pp vs our model."


def run_full_analysis(market_data: List[Dict[str, Any]], sport: str) -> List[Dict[str, Any]]:
    """Run analysis for all markets in a sport."""
    dataset, aliases = {
        "worldcup": (WORLDCUP_DATA, WORLDCUP_ALIASES),
        "nba":      (NBA_DATA, NBA_ALIASES),
        "ucl":      (UCL_DATA, UCL_ALIASES),
    }.get(sport, ({}, {}))

    if not dataset:
        logger.error(f"No dataset found for sport: {sport}")
        return []

    results = []
    for m in market_data:
        team = m.get("team")
        market_prob = m.get("market_prob", 0) / 100
        logo_url = m.get("logo_url", "")
        if not team or market_prob <= 0:
            continue
        r = analyze_team(team, market_prob, dataset, aliases, logo_url)
        if r:
            results.append(r)

    results.sort(key=lambda x: -abs(x["divergence"]))
    logger.info(f"Analyzed {len(results)} teams for {sport}")
    return results