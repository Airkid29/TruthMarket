# fetcher.py — TruthMarket AI
# Fetches live market data from Polymarket Gamma API
# API docs: https://docs.polymarket.com/
# No authentication required.

import requests
import json
import re
import logging
import time
from typing import List, Dict, Any, Optional
from config import (
    POLYMARKET_BASE_URL, REQUEST_TIMEOUT, RATE_LIMIT_DELAY,
    SPORT_SLUGS, CACHE_ENABLED, CACHE_TTL
)

logger = logging.getLogger(__name__)

# Simple cache for API responses
_cache: Dict[str, Dict[str, Any]] = {}


def _get_cache_key(url: str, params: Dict[str, Any]) -> str:
    """Generate a cache key from URL and params."""
    param_str = "&".join(f"{k}={v}" for k, v in sorted(params.items()))
    return f"{url}?{param_str}"


def _is_cache_valid(cache_entry: Dict[str, Any]) -> bool:
    """Check if cache entry is still valid."""
    if not CACHE_ENABLED:
        return False
    return time.time() - cache_entry["timestamp"] < CACHE_TTL


def _cached_get(url: str, params: Dict[str, Any] = None, **kwargs) -> requests.Response:
    """Make a GET request with caching."""
    params = params or {}
    cache_key = _get_cache_key(url, params)

    if cache_key in _cache and _is_cache_valid(_cache[cache_key]):
        logger.debug(f"Cache hit for {cache_key}")
        # Create a mock response object
        class MockResponse:
            def __init__(self, data):
                self._data = data
            def json(self):
                return self._data
            def raise_for_status(self):
                pass
            status_code = 200
        return MockResponse(_cache[cache_key]["data"])

    logger.debug(f"Cache miss for {cache_key}")
    resp = requests.get(url, params=params, **kwargs)
    resp.raise_for_status()

    if CACHE_ENABLED:
        _cache[cache_key] = {
            "data": resp.json(),
            "timestamp": time.time()
        }

    return resp


def _parse_prices(raw_prices: str, raw_outcomes: str) -> tuple[List[float], List[str]]:
    """Parse price and outcome data from Polymarket API."""
    try:
        prices = json.loads(raw_prices) if isinstance(raw_prices, str) else raw_prices
        outcomes = json.loads(raw_outcomes) if isinstance(raw_outcomes, str) else raw_outcomes
        return prices, outcomes
    except (json.JSONDecodeError, TypeError) as e:
        logger.warning(f"Failed to parse prices/outcomes: {e}")
        return [], []


def _extract_team_from_question(question: str, sport: str) -> Optional[str]:
    """Extract team name from Polymarket question text."""
    patterns = {
        "worldcup": [
            r"Will (.+?) win the 2026 FIFA World Cup\?",
            r"Will (.+?) win the FIFA World Cup 2026\?",
        ],
        "nba": [
            r"Will the (.+?) win the 2026 NBA Finals\?",
            r"Will the (.+?) win the NBA Championship\?",
        ],
        "ucl": [
            r"Will (.+?) win the 2025.26 Champions League\?",
            r"Will (.+?) win the UEFA Champions League\?",
            r"Will (.+?) win the 2025-26 Champions League\?",
        ],
    }

    for pattern in patterns.get(sport, []):
        match = re.search(pattern, question, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None


def fetch_sport_markets(sport: str) -> List[Dict[str, Any]]:
    """Fetch market data for a specific sport from Polymarket."""
    slug = SPORT_SLUGS.get(sport)
    if not slug:
        logger.error(f"Unknown sport: {sport}")
        return []

    try:
        logger.info(f"Fetching data for {sport}")
        resp = _cached_get(
            f"{POLYMARKET_BASE_URL}/events",
            params={"slug": slug},
            timeout=REQUEST_TIMEOUT
        )
        data = resp.json()
    except requests.RequestException as e:
        logger.error(f"Network error fetching {sport}: {e}")
        return []
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error for {sport}: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error fetching {sport}: {e}")
        return []

    if not data:
        logger.warning(f"No data returned for {sport}")
        return []

    event = data[0]
    markets = event.get("markets", [])
    results = []

    for market in markets:
        question = market.get("question", "")
        raw_prices = market.get("outcomePrices", "[]")
        raw_outcomes = market.get("outcomes", "[]")
        volume = float(market.get("volume", 0) or 0)
        active = market.get("active", False)
        closed = market.get("closed", False)
        logo_url = market.get("image") or market.get("icon") or ""

        if closed or not active:
            continue

        prices, outcomes = _parse_prices(raw_prices, raw_outcomes)
        if not prices or not outcomes:
            continue

        try:
            yes_idx = [o.lower() for o in outcomes].index("yes")
            market_prob = float(prices[yes_idx]) * 100
        except (ValueError, IndexError) as e:
            logger.warning(f"Failed to extract probability from market: {e}")
            continue

        if market_prob <= 0:
            continue

        team = _extract_team_from_question(question, sport)
        if not team:
            logger.warning(f"Could not extract team from question: {question}")
            continue

        results.append({
            "team": team,
            "market_prob": round(market_prob, 2),
            "volume": volume,
            "question": question,
            "logo_url": logo_url,
        })

        # Rate limiting
        time.sleep(RATE_LIMIT_DELAY)

    results.sort(key=lambda x: -x["market_prob"])
    logger.info(f"Found {len(results)} markets for {sport}")
    return results


def fetch_all_sports() -> Dict[str, List[Dict[str, Any]]]:
    """Fetch market data for all supported sports."""
    all_data = {}
    for sport in SPORT_SLUGS.keys():
        logger.info(f"Fetching {sport}...")
        all_data[sport] = fetch_sport_markets(sport)
        logger.info(f"→ {len(all_data[sport])} markets found")
    return all_data