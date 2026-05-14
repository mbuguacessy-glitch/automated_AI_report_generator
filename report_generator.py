import os
import json
from datetime import datetime
from pathlib import Path
from collections import Counter
from dotenv import load_dotenv
import anthropic
from pyairtable import Api

load_dotenv(Path(__file__).parent / ".env")

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
AIRTABLE_TOKEN = os.getenv("AIRTABLE_TOKEN")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")
AIRTABLE_TABLE = os.getenv("AIRTABLE_TABLE_NAME", "Leads")


def fetch_leads():
    api = Api(AIRTABLE_TOKEN)
    table = api.table(AIRTABLE_BASE_ID, AIRTABLE_TABLE)
    records = table.all()
    return [r["fields"] for r in records]


def build_summary(leads):
    urgency_counts = Counter(l.get("Urgency Level", "Unknown") for l in leads)
    status_counts = Counter(l.get("Status", "Unknown") for l in leads)

    lead_list = []
    for l in leads:
        lead_list.append({
            "name":         l.get("Client Name", "Unknown"),
            "project_type": l.get("Project Type", "Unknown"),
            "urgency":      l.get("Urgency Level", "Unknown"),
            "status":       l.get("Status", "Unknown"),
            "budget":       l.get("Budget", 0),
            "timeline":     l.get("Timeline", "Unknown"),
        })

    return {
        "total_leads":     len(leads),
        "urgency_counts":  dict(urgency_counts),
        "status_counts":   dict(status_counts),
        "leads":           lead_list,
    }


def generate_report(summary):
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    prompt = f"""You are a business analyst writing a weekly lead pipeline report 
for an AI automation agency. Write a clear, professional report based on the 
data below. The report should include:

1. Executive summary (2-3 sentences on overall pipeline health)
2. Lead breakdown by urgency level
3. Lead breakdown by status
4. Individual lead highlights (name, project, urgency, budget)
5. Recommended next actions

Data:
{json.dumps(summary, indent=2)}

Write the report in plain English. Use clear headings. Be concise and actionable."""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}]
    )

    return message.content[0].text


def save_report(report_text):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    reports_folder = Path(__file__).parent / "reports"
    reports_folder.mkdir(exist_ok=True)
    file = reports_folder / f"lead_report_{timestamp}.txt"
    file.write_text(report_text, encoding="utf-8")
    return file


def run():
    print("Fetching leads from Airtable...")
    leads = fetch_leads()
    print(f"Found {len(leads)} lead(s)\n")

    print("Building summary...")
    summary = build_summary(leads)

    print("Generating report with Claude...")
    report = generate_report(summary)

    print("Saving report...")
    file = save_report(report)

    print(f"\nReport saved to: {file}\n")
    print("=" * 60)
    print(report)
    print("=" * 60)


if __name__ == "__main__":
    run()
