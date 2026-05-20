# Automated AI Report Generator

## What this does
A Python script that connects to your Airtable Leads table, reads all
client records, sends the data to Claude AI, and receives a clean written
report back. The report includes lead counts, urgency breakdowns, status
summaries, individual highlights, and recommended next actions. Saves
as a timestamped .txt file automatically.

## The problem it solves
Every business running automations needs to answer the same question: what
happened this week? Someone manually opens Airtable, counts records, pastes
data into a document, writes a summary, and sends it. For one client that
takes 30 minutes. For ten clients it takes half a day. This script does the
entire thing in under 10 seconds with no human involvement.

## Measurable result
- Processing time: under 10 seconds including Airtable fetch and Claude API call
- Manual equivalent: 30 minutes of opening Airtable, counting records,
  writing a summary, and formatting a report — done every week by hand
- Records read from Airtable: 2 leads
- Report sections generated: 5 (executive summary, urgency breakdown,
  status breakdown, lead highlights, next actions)
- Output: timestamped .txt file saved to reports/ folder
- Report successfully generated: yes
- Human involvement required: zero after setup

## Tech stack: 2026 versions
- Python 3.12.0
- Anthropic SDK 0.40+
- Claude claude-sonnet-4-6
- pyairtable 2.x
- python-dotenv

## Tools used and why

### Claude AI: the analyst
Claude reads the raw lead data and writes a human-readable narrative report.
Without Claude this would require manually writing logic to turn numbers into
sentences: a different rule for every possible combination of leads, statuses,
and urgency levels. Claude handles all of that in one prompt and produces
a report a manager can read and act on immediately.

### pyairtable: the data fetcher
Connects to Airtable via API and pulls every record from the Leads table as a
Python list. Without pyairtable we would need to manually export a CSV from
Airtable every time we want to generate a report.

### Counter from collections: the tallying tool
A built-in Python tool that counts how many times each value appears in a list.
Used to count leads by urgency level (High: 1, Low: 1) and by status (New: 2)
without writing a manual loop. Turns raw record data into the summary statistics
Claude uses to write the breakdown sections of the report.

### python-dotenv: the key manager
Loads API keys from the .env file so they are never hardcoded in the script.
Without this your Anthropic and Airtable credentials would be visible in the
code and exposed if you pushed to GitHub.

### pathlib Path: the file handler
Handles all file paths in a way that works on Windows, Mac, and Linux without
changes. Used to find the .env file, create the reports/ folder automatically
if it does not exist, and save each report with a unique timestamped filename
so old reports are never overwritten.

## How it works
1. Script connects to Airtable and fetches all records from the Leads table
2. Extracts key fields from each record: name, project type, urgency, status, budget
3. Counts leads by urgency level and status using Counter
4. Sends the structured summary to Claude with a reporting prompt
5. Claude writes a full narrative report with headings and recommendations
6. Report is saved as a timestamped .txt file in the reports/ folder
7. Report is printed to the terminal for immediate review

## Error handling
- 403 Forbidden from Airtable: token is missing data.records:read scope,
  go to airtable.com/create/tokens and add it
- AIRTABLE reads as None: check .env has no spaces around = signs and
  all four keys are present
- Found 0 leads: run Challenge 4 first to populate the Leads table
- UNKNOWN_FIELD_NAME: field names in code must match Airtable columns exactly
- AuthenticationError: check ANTHROPIC_API_KEY in .env is complete with
  no spaces
- Report looks wrong: add print(json.dumps(summary, indent=2)) before
  generate_report() to see what data Claude is receiving

## Screenshots

Terminal output showing successful run:
![Terminal output](https://i.imgur.com/adjth8f.png)

Airtable Leads table with records:
![Airtable records](https://i.imgur.com/FMBbdKG.png)

Generated report opened in VS Code:
![Report in VS Code](https://i.imgur.com/GzlpbG6.png)

