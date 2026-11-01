# Lead Triage Agent

Automates the first step of sales follow-up: reads incoming leads, labels them HOT / WARM / COLD
using urgency, intent and budget signals, and drafts a personalised reply for each.

## Features
- Rule-based scoring (easy to tune in `triage.py`)
- Optional Claude-written replies (set `ANTHROPIC_API_KEY`), template replies otherwise
- Saves results to CSV and SQLite

## Run
```bash
python triage.py
```
Edit `leads.csv` to try your own leads.

## Next steps
Trigger it from an n8n/Make workflow when a form is submitted and push results to a CRM or Google Sheet.
