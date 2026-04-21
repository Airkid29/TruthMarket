# TruthMarket AI

TruthMarket AI is a sophisticated sports prediction engine that analyzes prediction market data from Polymarket and compares it against historical performance models. The system identifies overpriced and underpriced betting opportunities by calculating divergences between market probabilities and model estimates based on ELO ratings, historical success, and recent form.
 
## Project Overview

The application consists of several components:

- **Data Collection**: Fetches live market data from Polymarket's Gamma API
- **Historical Analysis**: Uses comprehensive historical data for World Cup, NBA, and UEFA Champions League
- **Model Calculation**: Computes fair probabilities using a weighted model (50% ELO, 30% historical titles, 20% recent form)
- **Signal Generation**: Identifies betting opportunities where market odds diverge significantly from model estimates
- **Web Interface**: Provides a modern, responsive dashboard to visualize results

## Key Features

- **Multi-Sport Support**: World Cup 2026, NBA Championship 2026, UEFA Champions League 2025-26
- **Explainable AI**: Every signal comes with detailed reasoning and confidence scores
- **Real-time Data**: Fetches live market data from Polymarket
- **Visual Dashboard**: Premium web interface with team logos, confidence gauges, and sparklines
- **API Endpoints**: RESTful API for programmatic access

## Architecture

```
truthmarket/
├── app.py          # Flask web application
├── main.py         # Command-line analysis runner
├── fetcher.py      # Polymarket API client
├── engine.py       # Analysis engine and modeling
├── data.py         # Historical sports data
└── results.json    # Generated analysis output
```

## Installation

### Prerequisites

- Python 3.8+
- pip package manager

### Setup

1. **Clone or download the project files**

2. **Install dependencies**
   ```bash
   pip install flask requests
   ```

   Or using requirements.txt (create if not present):
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify installation**
   ```bash
   python -c "import flask, requests; print('Dependencies installed successfully')"
   ```

## Usage

### Running the Analysis

1. **Execute the main analysis script**
   ```bash
   python main.py
   ```

   This will:
   - Fetch live market data from Polymarket for all supported sports
   - Run the analysis engine against historical data
   - Generate signals for overpriced/underpriced opportunities
   - Save results to `results.json`

2. **Expected output**:
   ```
   ===================================================================
     TRUTHMARKET AI — Sports Decision Engine
     Prediction markets vs historical reality
   ===================================================================

   [1/3] Fetching live Polymarket data...
     Fetching worldcup...
     → 32 markets found
     Fetching nba...
     → 30 markets found
     Fetching ucl...
     → 32 markets found

   [2/3] Running analysis...
     ── FIFA World Cup 2026 ──
     Analyzed: 32 teams
     Signals → BET AGAINST: 8 | FOLLOW: 12 | HOLD: 12

   [3/3] Saving results.json...
   ===================================================================
     DONE. results.json ready.
   ===================================================================
   ```

### Launching the Web Interface

1. **Start the Flask application**
   ```bash
   python app.py
   ```

2. **Open your browser** and navigate to:
   ```
   http://localhost:5000
   ```

3. **API Access**: The application also provides REST endpoints:
   ```
   GET /api/analyze?sport=worldcup|nba|ucl
   ```

## Data Sources

### Historical Data

- **World Cup**: FIFA official records (1930-2022), ELO ratings from eloratings.net
- **NBA**: Official NBA records (1946-2025), recent performance metrics
- **UEFA Champions League**: UEFA official records (1955-2025), squad valuations

### Market Data

- **Polymarket Gamma API**: Live prediction market odds
- **No authentication required** for public market data
- **Real-time updates** available

## Analysis Methodology

### Model Components

The fair probability model uses three weighted signals:

1. **ELO Rating (50%)**: Current team strength based on international football ratings
2. **Historical Success (30%)**: Tournament titles and final appearances (with Laplace smoothing)
3. **Recent Form (20%)**: Performance in the most recent tournament season

### Signal Generation

- **BET AGAINST**: Market probability > Model probability + 5 percentage points
- **FOLLOW MARKET**: Market probability < Model probability - 5 percentage points
- **HOLD**: Probabilities align within ±5 percentage points

### Confidence Scoring

Confidence scores (50-99) are calculated based on divergence magnitude:
- ±5pp → 50% confidence
- ±15pp → 85% confidence
- ±30pp+ → 99% confidence

## Configuration

### Sport Coverage

Currently supported sports and their Polymarket event slugs:

```python
SPORT_SLUGS = {
    "worldcup": "2026-fifa-world-cup-winner-595",
    "nba":      "2026-nba-champion",
    "ucl":      "uefa-champions-league-winner",
}
```

### Model Parameters

```python
SIGNAL_THRESHOLD = 5.0  # Percentage points for signal generation

# Model weights
ELO_WEIGHT = 0.50
HISTORICAL_WEIGHT = 0.30
RECENT_WEIGHT = 0.20
```

## Output Format

Results are saved to `results.json` with the following structure:

```json
{
  "generated_at": "2026-04-08T12:00:00Z",
  "sports": {
    "worldcup": {
      "label": "FIFA World Cup 2026",
      "total_markets": 32,
      "analyzed": 32,
      "summary": {
        "bet_against": 8,
        "follow_market": 12,
        "hold": 12
      },
      "results": [
        {
          "team": "Argentina",
          "team_resolved": "Argentina",
          "market_prob": 12.5,
          "model_prob": 18.2,
          "divergence": -5.7,
          "signal": "FOLLOW MARKET",
          "signal_short": "follow",
          "color": "green",
          "confidence": 65,
          "explanation": "Argentina: 3 historical titles signal structural dominance...",
          "logo_url": "https://flagcdn.com/h40/ar.png",
          "breakdown": {
            "elo": 2140,
            "titles": 3,
            "finals": 5,
            "recent": "W"
          }
        }
      ]
    }
  }
}
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure Flask and requests are installed
   ```bash
   pip install flask requests
   ```

2. **Network Errors**: Check internet connection for Polymarket API access

3. **Empty Results**: Verify Polymarket event slugs are current

4. **Web App Not Loading**: Ensure port 5000 is available

### Debug Mode

Enable debug logging by modifying print statements to use the logging module:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Future Enhancements

- **Additional Sports**: Expand to more leagues and tournaments
- **Advanced Modeling**: Incorporate player statistics, injuries, weather
- **Real-time Updates**: WebSocket connections for live market changes
- **Backtesting**: Historical validation of model performance
- **Machine Learning**: Neural networks for probability estimation
- **Mobile App**: React Native companion application

## New UX and Performance Updates

- **Dark/Light Theme**: Theme toggle in the header with local persistence.
- **Improved Sharing**: Signal-level sharing with native Web Share fallback to clipboard.
- **Comparison Sharing**: Select 2-4 teams across cards and share a consolidated comparison text.
- **Faster World Cup Load**:
  - Removed per-market artificial delay in fetch parsing.
  - Added API analysis response cache in `app.py` for repeated requests.
  - Staggered non-primary sport loads on frontend to prioritize first paint.

## CDC (Cahier des Charges)

An updated CDC is available here:

- `docs/CDC.md`

## Architecture Diagram Generation

Generate the architecture diagram (Mermaid format) with:

```bash
python scripts/generate_architecture_diagram.py
```

Output file:

- `docs/architecture.mmd`

## License

This project is for educational and research purposes. Please respect Polymarket's terms of service and applicable gambling regulations in your jurisdiction.

## Contributing

Contributions welcome! Areas for improvement:
- Additional data sources
- Model refinements
- UI/UX enhancements
- Test coverage
- Documentation

## Contact

For questions or feedback, please examine the code and analysis methodology in the source files.