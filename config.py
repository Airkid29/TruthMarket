"""
Configuration file for TruthMarket AI
"""

import os

# API Configuration
POLYMARKET_BASE_URL = "https://gamma-api.polymarket.com"
REQUEST_TIMEOUT = 10  # seconds
RATE_LIMIT_DELAY = 1  # seconds between API calls

# Sport Slugs
SPORT_SLUGS = {
    "worldcup": "2026-fifa-world-cup-winner-595",
    "nba":      "2026-nba-champion",
    "ucl":      "uefa-champions-league-winner",
}

# Model Parameters
SIGNAL_THRESHOLD = 5.0  # Percentage points for signal generation
ELO_WEIGHT = 0.50
HISTORICAL_WEIGHT = 0.30
RECENT_WEIGHT = 0.20

# Stage Scores for recent form
STAGE_SCORES = {
    "W": 10, "F": 7, "SF": 5, "3rd": 4,
    "QF": 3, "R16": 2, "G": 1, "Lottery": 0,
    "Missed playoffs": 0, "Champions 2024": 10,
    "W-Conference Finals": 5,
    "Conference Finals": 5, "Conference SF": 3,
    "Playoffs R1": 2, "Playoffs R2": 3,
}

# Flask Configuration
FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")
FLASK_PORT = int(os.getenv("FLASK_PORT", 5000))
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "False").lower() == "true"

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Sport Labels
SPORT_LABELS = {
    "worldcup": "World Cup 2026",
    "nba":      "NBA 2026",
    "ucl":      "Champions League",
}

# Cache Configuration
CACHE_ENABLED = True
CACHE_TTL = 300  # 5 minutes