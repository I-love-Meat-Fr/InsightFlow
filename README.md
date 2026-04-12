# InsightFlow

Intelligent web scraper and data synthesizer: async crawling (httpx + Playwright), Pandas analysis with outlier detection, sentiment on reviews, LLM daily digest, PDF reports (ReportLab), and delivery via Telegram or email.

## Ethics

Respect each site’s `robots.txt`, terms of use, and rate limits. This project is intended for learning and authorized data collection only.

## Setup

```bash
cd InsightFlow
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .
playwright install chromium
```

Copy `.env.example` to `.env` and fill in API keys and delivery settings.

## Configuration

- **Targets:** edit [`config/targets.yaml`](config/targets.yaml) — URLs, `kind` (`httpx` or `playwright`), and CSS selectors.
- **Secrets:** `.env` — see `.env.example`.

## Run

```bash
insightflow run --config config/targets.yaml
insightflow run --config config/targets.yaml --no-send --no-llm
```

Outputs: `data/history/` (Parquet snapshots), `logs/insightflow.log`, and a dated PDF under `data/reports/`.

## LLM providers

- **OpenAI-compatible:** set `OPENAI_API_URL`, `OPENAI_API_KEY`, `LLM_MODEL`.
- **Ollama:** `OPENAI_API_URL=http://localhost:11434/v1`, `OPENAI_API_KEY=ollama`, and a local model name in `LLM_MODEL`.
