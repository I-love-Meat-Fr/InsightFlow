# InsightFlow

Intelligent web scraper and data synthesizer: async crawling (httpx + Playwright), Pandas analysis with outlier detection, sentiment on reviews, LLM daily digest, PDF reports (ReportLab), and delivery via Telegram or email.

## 🚀 Features
  1. Smart Voucher AggregatorAutomated Multi-source Scraping: Efficiently extracts voucher data (code, discount value, expiry date) from various e-commerce platforms and coupon sites.
     Dynamic Target Configuration: Easily add or modify scraping targets via a simple YAML configuration file.
     Real-time Price Tracking: Monitors product prices and identifies price drops or outliers using the IQR (Interquartile Range) method.
  2. AI-Powered Analysis (Gemini Integration)Intelligent Digest Generation: Leverages the Google Gemini API to analyze raw voucher data and summarize the "Best Deals of the Day".
     Deal Scoring & Categorization: Automatically ranks vouchers based on their value and excludes expired or low-quality codes.
     Natural Language Reports: Converts complex data tables into easy-to-read executive summaries.
  3. Professional Reporting & NotificationAutomated PDF Generation: High-quality daily reports generated using the ReportLab library, featuring data visualizations and trend analysis.
     Multi-channel Delivery: (Coming Soon) Support for sending automated alerts via Telegram Bot and SMTP Email.
     Detailed Data Snapshots: Maintains a historical record of all scraped products and vouchers in .parquet or .csv format for future analysis.
  4. Developer-Friendly Environment
     WSL2 & Ubuntu Optimized: Fully tested and optimized for modern development environments.


Vibe-coding Ready: Clean architecture with built-in logging and rich terminal output (using Rich library) to ensure a smooth developer experience.

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
