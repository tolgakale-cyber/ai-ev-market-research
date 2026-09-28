# AI EV Market Research

A multi-model AI market research pipeline that analyzes global electric vehicle market data using Gemini, Claude, ChatGPT, and deterministic Python-based QA validation.

The project transforms structured IEA data into a validated research workflow and presents the results through a public interactive dashboard.

## Live Demo

**GitHub Pages:**  
https://tolgakale-cyber.github.io/ai-ev-market-research/

## Project Overview

This project demonstrates a multi-stage AI research pipeline rather than relying on a single model response.

Each model has a dedicated responsibility:

- **Gemini** — market and trend analysis
- **Claude** — risk and strategy analysis
- **Deterministic QA Validator** — numerical and source-grounding checks
- **ChatGPT** — final research synthesis

The pipeline separates data processing, AI analysis, validation, and final synthesis to make the workflow easier to inspect and evaluate.

## Architecture

```text
IEA CSV
   |
   v
IEA Parser
   |
   v
Structured JSON
   |
   v
Gemini
Market & Trend Analysis
   |
   v
Claude
Risk & Strategy Analysis
   |
   v
Deterministic QA Validator
   |
   v
ChatGPT
Final Research Synthesis
   |
   v
Turkish Research Report
   |
   v
Interactive Portfolio Website
```

## Data Pipeline

The project uses electric vehicle sales data from the **International Energy Agency (IEA)**.

The dataset covers:

- China
- Europe
- United States
- Rest of World
- 2020–2026

The 2026 values are treated explicitly as **IEA estimates**, not realized sales.

Raw CSV data is parsed into structured JSON before being passed into the AI analysis pipeline.

## Evidence & QA Validation

AI-generated analysis is not accepted without additional validation.

A deterministic Python QA layer checks critical numerical claims against the structured source data, including:

- Global sales totals
- Regional sales values
- Year-over-year changes
- 2026 estimate status
- Source-grounded numerical claims

The current validation pipeline passes **8 / 8 numerical checks**.

The QA stage also flags potentially unsupported causal language for review before final synthesis.

## AI Orchestration

The models are intentionally assigned different roles instead of asking one model to perform the entire research process.

```text
Data -> Gemini -> Claude -> QA -> ChatGPT -> Final Report
```

This architecture helps separate:

1. Market analysis
2. Risk analysis
3. Evidence validation
4. Final synthesis

The final model receives the original structured data, model analyses, and QA results before generating the research report.

## Web Dashboard

The project includes a Turkish portfolio dashboard displaying:

- Global EV market growth
- Regional EV sales
- 2026 IEA estimates
- Regional growth rates
- AI pipeline architecture
- QA validation status
- AI-generated executive summary

The dashboard is deployed publicly through GitHub Pages.

## Project Structure

```text
ai-ev-market-research/
|
|-- engine/
|   |-- ai_orchestrator.py
|   |-- iea_parser.py
|   |-- iea_exporter.py
|   |-- qa_validator.py
|
|-- outputs/
|   |-- iea_ev_sales.json
|
|-- src/
|   |-- index.html
|   |-- style.css
|   |-- app.js
|   |-- final_report.md
|
|-- docs/
|   |-- index.html
|   |-- style.css
|   |-- app.js
|   |-- final_report.md
|   |-- iea_ev_sales.json
|
|-- README.md
|-- .gitignore
```

## Technology Stack

- Python
- Gemini API
- Claude API
- OpenAI API
- HTML
- CSS
- JavaScript
- Chart.js
- GitHub Pages

## Design Principles

The project follows several core principles:

- Separate generation from validation
- Keep source data structured
- Use deterministic checks for critical numerical claims
- Clearly distinguish estimates from realized values
- Avoid unsupported causal claims
- Preserve model outputs for inspection
- Keep API credentials outside version control

## Limitations

- The dataset covers global regional EV sales rather than individual vehicle models.
- 2026 values are estimates.
- The source dataset does not explain the causes behind market changes.
- AI-generated strategic interpretations should not be treated as investment advice.
- Deterministic QA validates defined numerical claims but does not guarantee that every natural-language statement is correct.

## Future Improvements

Potential extensions include:

- Additional EV datasets and market indicators
- Automated source ingestion
- More extensive claim-level validation
- Historical comparison tools
- Additional dashboard visualizations
- Automated report publishing

## Data Source

International Energy Agency (IEA) — Global EV Outlook 2026.

Dataset units: **million vehicles**.

Source data is subject to the IEA's applicable terms and licensing conditions.