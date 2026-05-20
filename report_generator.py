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

# Connects to Airtable and retrieves all lead records as a clean list of field dictionaries


def fetch_leads():
    api = Api(AIRTABLE_TOKEN)
    table = api.table(AIRTABLE_BASE_ID, AIRTABLE_TABLE)
    records = table.all()
    return [r["fields"] for r in records]

# Takes the raw list of lead records and computes summary statistics — counts by urgency, status, and key highlights


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

# Sends the summary statistics to Claude and receives a fully written business insight report as a string


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

# Saves the generated report as a timestamped .txt file in the reports/ folder so nothing is ever overwritten


def save_report(report_text):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    reports_folder = Path(__file__).parent / "reports"
    reports_folder.mkdir(exist_ok=True)
    file = reports_folder / f"lead_report_{timestamp}.txt"
    file.write_text(report_text, encoding="utf-8")
    return file

# Orchestrates the full pipeline — fetch leads, build summary, generate report, save, and print to terminal


def run():
    # Step 1 — Fetch leads
    try:
        print("Fetching leads from Airtable...")
        leads = fetch_leads()
        print(f"Found {len(leads)} lead(s)\n")
    except Exception as e:
        print(f"ERROR fetching from Airtable: {e}")
        print("Check your AIRTABLE_TOKEN, AIRTABLE_BASE_ID, and token permissions.")
        return

    # Step 2 — Check we actually have leads
    if len(leads) == 0:
        print("No leads found in Airtable. Run Challenge 4 first to add records.")
        return

    # Step 3 — Build summary
    try:
        print("Building summary...")
        summary = build_summary(leads)
    except Exception as e:
        print(f"ERROR building summary: {e}")
        return

    # Step 4 — Generate report with Claude
    try:
        print("Generating report with Claude...")
        report = generate_report(summary)
    except Exception as e:
        print(f"ERROR calling Claude API: {e}")
        print("Check your ANTHROPIC_API_KEY in the .env file.")
        return

    # Step 5 — Save and print report
    try:
        print("Saving report...")
        file = save_report(report)
        print(f"\nReport saved to: {file}\n")
        print("=" * 60)
        print(report)
        print("=" * 60)
    except Exception as e:
        print(f"ERROR saving report: {e}")
        print("Check that the reports/ folder exists or can be created.")
        return


if __name__ == "__main__":
    run()
