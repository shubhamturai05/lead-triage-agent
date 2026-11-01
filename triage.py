"""Lead Triage Agent
Reads leads.csv, scores each lead (HOT / WARM / COLD), drafts a personalised reply,
and saves results to triaged_leads.csv and leads.db (SQLite).
Uses Claude for the reply when ANTHROPIC_API_KEY is set; otherwise uses templates.
"""
import csv, os, sqlite3

HERE = os.path.dirname(__file__)
URGENT = ["urgent", "asap", "this week", "immediately", "today", "ready"]
INTENT = ["quote", "pricing", "price", "start", "need", "hire"]

def score(lead):
    text = lead["message"].lower()
    s = sum(2 for w in URGENT if w in text) + sum(1 for w in INTENT if w in text)
    b = float(lead["budget_usd"] or 0)
    s += 3 if b >= 1000 else 2 if b >= 500 else 0
    return "HOT" if s >= 6 else "WARM" if s >= 3 else "COLD"

TEMPLATES = {
    "HOT": "Hi {n}, thanks for reaching out! This looks like a great fit. Can we book a 15-minute call today or tomorrow to scope it?",
    "WARM": "Hi {n}, thanks for your interest! Here is a short overview of how we can help. Which day suits you for a quick call?",
    "COLD": "Hi {n}, thanks for getting in touch. I will share some useful resources and we can reconnect whenever you are ready.",
}

def draft(lead, label):
    first = lead["name"].split()[0]
    if os.getenv("ANTHROPIC_API_KEY"):
        import anthropic
        msg = anthropic.Anthropic().messages.create(
            model="claude-sonnet-4-6", max_tokens=200,
            messages=[{"role": "user", "content":
                f"Write a short, friendly 3-sentence reply to this {label} lead. "
                f"Name: {first}. Message: {lead['message']}"}])
        return msg.content[0].text
    return TEMPLATES[label].format(n=first)

def main():
    rows = list(csv.DictReader(open(os.path.join(HERE, "leads.csv"), encoding="utf-8")))
    con = sqlite3.connect(os.path.join(HERE, "leads.db"))
    con.execute("DROP TABLE IF EXISTS leads")
    con.execute("CREATE TABLE leads(name, email, label, reply)")
    for r in rows:
        r["label"] = score(r); r["reply"] = draft(r, r["label"])
        con.execute("INSERT INTO leads VALUES(?,?,?,?)", (r["name"], r["email"], r["label"], r["reply"]))
        print(f"[{r['label']}] {r['name']}: {r['reply']}")
    con.commit(); con.close()
    with open(os.path.join(HERE, "triaged_leads.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)

if __name__ == "__main__":
    main()
