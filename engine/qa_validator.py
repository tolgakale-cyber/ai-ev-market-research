import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "outputs" / "iea_ev_sales.json"


def load_data():
    with open(DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def calculate_total(row):
    return round(
        row["cin_milyon"]
        + row["avrupa_milyon"]
        + row["abd_milyon"]
        + row["diger_dunya_milyon"],
        1,
    )


def find_year(data, year):
    for row in data["veriler"]:
        if row["yil"] == year:
            return row

    raise ValueError(f"{year} verisi bulunamadı.")


def run_source_checks(data):
    checks = []

    row_2025 = find_year(data, 2025)
    row_2026 = find_year(data, 2026)

    total_2025 = calculate_total(row_2025)
    total_2026 = calculate_total(row_2026)

    us_change_pct = round(
        (
            row_2026["abd_milyon"]
            - row_2025["abd_milyon"]
        )
        / row_2025["abd_milyon"]
        * 100,
        1,
    )

    row_change_pct = round(
        (
            row_2026["diger_dunya_milyon"]
            - row_2025["diger_dunya_milyon"]
        )
        / row_2025["diger_dunya_milyon"]
        * 100,
        1,
    )

    checks.append(
        {
            "kontrol": "2026 tahmin olarak işaretlenmiş",
            "beklenen": True,
            "gercek": row_2026["tahmin"],
            "durum": row_2026["tahmin"] is True,
        }
    )

    checks.append(
        {
            "kontrol": "2025 toplam EV hacmi",
            "beklenen": 20.9,
            "gercek": total_2025,
            "durum": total_2025 == 20.9,
        }
    )

    checks.append(
        {
            "kontrol": "2026 toplam EV hacmi",
            "beklenen": 23.4,
            "gercek": total_2026,
            "durum": total_2026 == 23.4,
        }
    )

    checks.append(
        {
            "kontrol": "2026 Çin hacmi",
            "beklenen": 14.3,
            "gercek": row_2026["cin_milyon"],
            "durum": row_2026["cin_milyon"] == 14.3,
        }
    )

    checks.append(
        {
            "kontrol": "2026 Avrupa hacmi",
            "beklenen": 5.0,
            "gercek": row_2026["avrupa_milyon"],
            "durum": row_2026["avrupa_milyon"] == 5.0,
        }
    )

    checks.append(
        {
            "kontrol": "2026 ABD hacmi",
            "beklenen": 1.2,
            "gercek": row_2026["abd_milyon"],
            "durum": row_2026["abd_milyon"] == 1.2,
        }
    )

    checks.append(
        {
            "kontrol": "2025→2026 ABD değişimi (%)",
            "beklenen": -20.0,
            "gercek": us_change_pct,
            "durum": us_change_pct == -20.0,
        }
    )

    checks.append(
        {
            "kontrol": "2025→2026 Rest of World değişimi (%)",
            "beklenen": 45.0,
            "gercek": row_change_pct,
            "durum": row_change_pct == 45.0,
        }
    )

    return checks


def scan_for_unsupported_causal_language(text):
    risky_phrases = [
        "policy-driven",
        "policy driven",
        "caused by",
        "caused",
        "because of",
        "due to",
        "driven by",
        "likely driver",
    ]

    findings = []

    lowered = text.lower()

    for phrase in risky_phrases:
        if phrase in lowered:
            findings.append(
                f"Kanıt gerektiren nedensellik ifadesi bulundu: '{phrase}'"
            )

    return findings


def build_qa_report(data, gemini_analysis, claude_analysis):
    checks = run_source_checks(data)

    failed_checks = [
        check for check in checks
        if not check["durum"]
    ]

    language_findings = []

    language_findings.extend(
        scan_for_unsupported_causal_language(
            gemini_analysis
        )
    )

    language_findings.extend(
        scan_for_unsupported_causal_language(
            claude_analysis
        )
    )

    lines = [
        "# Evidence / QA Validation Report",
        "",
        "## Source Data Checks",
        "",
    ]

    for check in checks:
        status = "PASS" if check["durum"] else "FAIL"

        lines.append(
            f"- **{status}** — {check['kontrol']} | "
            f"Beklenen: `{check['beklenen']}` | "
            f"Gerçek: `{check['gercek']}`"
        )

    lines.extend(
        [
            "",
            "## Model Output Warnings",
            "",
        ]
    )

    if language_findings:
        for finding in language_findings:
            lines.append(f"- **REVIEW** — {finding}")
    else:
        lines.append("- No risky causal-language patterns detected.")

    lines.extend(
        [
            "",
            "## QA Summary",
            "",
            f"- Source checks: {len(checks)}",
            f"- Failed source checks: {len(failed_checks)}",
            f"- Review warnings: {len(language_findings)}",
            "",
            "The validator checks source-grounded numerical facts "
            "deterministically. Language warnings require human/model review "
            "and are not automatically treated as factual errors.",
        ]
    )

    return "\n".join(lines)


def main():
    data = load_data()

    gemini_file = BASE_DIR / "reports" / "gemini_analysis.txt"
    claude_file = BASE_DIR / "reports" / "claude_analysis.txt"

    gemini_analysis = gemini_file.read_text(
        encoding="utf-8"
    )

    claude_analysis = claude_file.read_text(
        encoding="utf-8"
    )

    report = build_qa_report(
        data,
        gemini_analysis,
        claude_analysis,
    )

    output_file = BASE_DIR / "reports" / "qa_report.md"

    output_file.write_text(
        report,
        encoding="utf-8",
    )

    print(f"QA raporu oluşturuldu: {output_file}")


if __name__ == "__main__":
    main()