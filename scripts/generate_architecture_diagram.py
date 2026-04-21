#!/usr/bin/env python3
"""
Generate architecture diagram in Mermaid format for TruthMarket AI.
Usage:
    python scripts/generate_architecture_diagram.py
"""

from pathlib import Path


MERMAID = """flowchart TD
    U[User Browser] -->|GET /| A[Flask app.py]
    U -->|GET /api/analyze?sport=...| A
    A --> F[fetcher.py]
    A --> E[engine.py]
    F --> P[(Polymarket Gamma API)]
    E --> D[data.py datasets]
    E --> C[config.py]
    A --> L[Logos/ static assets]
    A --> T[templates/index.html]

    subgraph Client
        T --> UI[Theme toggle + compare/share UI]
    end

    subgraph Caching
        FC[Fetcher response cache TTL]
        AC[API analysis cache TTL]
    end

    F -.uses.-> FC
    A -.uses.-> AC
"""


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    out_dir = root / "docs"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "architecture.mmd"
    out_path.write_text(MERMAID, encoding="utf-8")
    print(f"Architecture diagram generated: {out_path}")


if __name__ == "__main__":
    main()
