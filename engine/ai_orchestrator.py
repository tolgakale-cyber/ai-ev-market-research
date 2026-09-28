import json
import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from anthropic import Anthropic
from openai import OpenAI


BASE_DIR = Path(__file__).resolve().parent.parent

DATA_FILE = BASE_DIR / "outputs" / "iea_ev_sales.json"
REPORTS_DIR = BASE_DIR / "reports"

GEMINI_MODEL = "gemini-3.5-flash-lite"
CLAUDE_MODEL = "claude-sonnet-4-5"
OPENAI_MODEL = "gpt-5.6-luna"


def load_research_data():
    with open(DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def ask_gemini(data):
    client = genai.Client(
        api_key=os.getenv("GEMINI_API_KEY")
    )

    prompt = f"""
You are the market data analyst in a multi-model EV market research pipeline.

Analyze the following IEA electric car sales data.

Your role:
- Identify major market trends.
- Compare China, Europe, United States and Rest of world.
- Identify important changes between years.
- Clearly distinguish historical data from the 2026 estimate.
- Do not invent facts that are not supported by the data.
- Calculate simple percentage or absolute changes when useful.

Return a structured analytical text that another AI model can use for further strategic analysis.

DATA:
{json.dumps(data, ensure_ascii=False, indent=2)}
"""

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt
    )

    return response.text


def ask_claude(data, gemini_analysis):
    client = Anthropic(
        api_key=os.getenv("ANTHROPIC_API_KEY")
    )

    prompt = f"""
You are the risk, opportunity and strategy analyst in a multi-model
EV market research pipeline.

You have the original IEA data and the market analysis produced by Gemini.

Your role:
- Identify market opportunities.
- Identify risks and uncertainties.
- Examine regional differences.
- Discuss strategic implications.
- Pay special attention to the fact that 2026 is an estimate.
- Do not invent information outside the supplied data.
- Clearly separate observations from strategic interpretation.

ORIGINAL IEA DATA:
{json.dumps(data, ensure_ascii=False, indent=2)}

GEMINI MARKET ANALYSIS:
{gemini_analysis}
"""

    message = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=2000,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return message.content[0].text


def ask_openai(data, gemini_analysis, claude_analysis):
    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY")
    )

    prompt = f"""
You are the final research synthesis analyst in a multi-model EV market
research pipeline.

Create a concise but professional final market research report using:

1. The original IEA data.
2. Gemini's market trend analysis.
3. Claude's risk, opportunity and strategy analysis.

Your responsibilities:
- Synthesize the findings instead of simply repeating them.
- Highlight the most important market trends.
- Compare the major regions.
- Include important numerical findings.
- Clearly label 2026 values as estimates.
- Distinguish factual observations from interpretation.
- Mention important limitations caused by the small dataset.
- Do not invent facts.
- Do not claim that the data proves causation.

Use the following structure:

# Global EV Market Research

## Executive Summary

## Key Market Trends

## Regional Analysis

## Risks and Opportunities

## Strategic Implications

## Data Limitations

## Conclusion

ORIGINAL IEA DATA:
{json.dumps(data, ensure_ascii=False, indent=2)}

GEMINI ANALYSIS:
{gemini_analysis}

CLAUDE ANALYSIS:
{claude_analysis}
"""

    response = client.responses.create(
        model=OPENAI_MODEL,
        input=prompt
    )

    return response.output_text


def save_text(file_path, content):
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(content)


def main():
    load_dotenv(override=True)

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    print("1/4 - IEA verisi okunuyor...")
    data = load_research_data()

    print("2/4 - Gemini pazar analizi yapıyor...")
    gemini_analysis = ask_gemini(data)

    save_text(
        REPORTS_DIR / "gemini_analysis.txt",
        gemini_analysis
    )

    print("3/4 - Claude risk ve strateji analizi yapıyor...")
    claude_analysis = ask_claude(
        data,
        gemini_analysis
    )

    save_text(
        REPORTS_DIR / "claude_analysis.txt",
        claude_analysis
    )

    print("4/4 - ChatGPT final raporu oluşturuyor...")
    final_report = ask_openai(
        data,
        gemini_analysis,
        claude_analysis
    )

    save_text(
        REPORTS_DIR / "final_report.md",
        final_report
    )

    print()
    print("AI market research pipeline tamamlandı.")
    print()
    print("Oluşturulan dosyalar:")
    print("- reports/gemini_analysis.txt")
    print("- reports/claude_analysis.txt")
    print("- reports/final_report.md")


if __name__ == "__main__":
    main()