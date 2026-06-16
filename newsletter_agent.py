import anthropic
import smtplib
import os
import json
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# ── Config (set these as GitHub Actions secrets) ──────────────────────────────
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
GMAIL_SENDER      = os.environ["GMAIL_SENDER"]      # your Gmail address
GMAIL_APP_PASSWORD = os.environ["GMAIL_APP_PASSWORD"] # Gmail app password (not your real password)
RECIPIENT_EMAIL   = os.environ["RECIPIENT_EMAIL"]    # where to send the newsletter

SOURCES = [
    "r/solotravel",
    "r/travel",
    "r/digitalnomad",
    "Hostelworld blog",
    "Nomadic Matt blog",
]

PROMPT = f"""You are a research agent for a solo travel startup newsletter called SoloSignal.

Today is {datetime.now().strftime("%A, %B %d, %Y")}.

Search the web for recent posts and discussions from: {", ".join(SOURCES)}.

Find 5 real, recurring pain points solo travelers are experiencing RIGHT NOW. Focus only on problems that could realistically be solved with a well-designed app or website.

Respond ONLY with valid JSON — no markdown, no backticks, no explanation. Use this exact shape:
{{
  "intro": "2-sentence intro summarizing today's findings",
  "problems": [
    {{
      "title": "short problem title",
      "source": "community or site this came from",
      "signal": "how widespread this seems (e.g. '3 threads this week, 200+ upvotes')",
      "description": "2-3 sentences describing the problem with specific detail and examples",
      "solution": {{
        "name": "product concept name",
        "type": "Mobile app | Web platform | Browser extension | AI chatbot",
        "description": "2 sentences: what it does and its core value prop"
      }},
      "tags": ["tag1", "tag2", "tag3"]
    }}
  ]
}}"""


def run_agent() -> dict:
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{"role": "user", "content": PROMPT}],
    )
    text = "".join(b.text for b in response.content if hasattr(b, "text"))
    clean = text.replace("```json", "").replace("```", "").strip()
    start = clean.find("{")
    if start != -1:
        clean = clean[start:]
    return json.loads(clean)


def build_html(data: dict) -> str:
    today = datetime.now().strftime("%A, %B %d, %Y")
    colors = [
        {"bg": "#E1F5EE", "border": "#0F6E56", "text": "#085041", "num": "#1D9E75", "num_text": "#fff", "tag_bg": "#9FE1CB"},
        {"bg": "#EEEDFE", "border": "#534AB7", "text": "#26215C", "num": "#7F77DD", "num_text": "#fff", "tag_bg": "#CECBF6"},
        {"bg": "#FAECE7", "border": "#993C1D", "text": "#4A1B0C", "num": "#D85A30", "num_text": "#fff", "tag_bg": "#F5C4B3"},
        {"bg": "#E6F1FB", "border": "#185FA5", "text": "#042C53", "num": "#378ADD", "num_text": "#fff", "tag_bg": "#B5D4F4"},
        {"bg": "#FBEAF0", "border": "#993556", "text": "#4B1528", "num": "#D4537E", "num_text": "#fff", "tag_bg": "#F4C0D1"},
    ]

    problems_html = ""
    for i, p in enumerate(data.get("problems", [])[:5]):
        c = colors[i % len(colors)]
        tags = "".join(
            f'<span style="display:inline-block;margin:3px 4px 0 0;padding:3px 10px;border-radius:99px;font-size:11px;background:{c["tag_bg"]};color:{c["text"]};border:1px solid {c["border"]};">{t}</span>'
            for t in p.get("tags", [])
        )
        sol = p.get("solution", {})
        problems_html += f"""
        <div style="margin-bottom:20px;border:1px solid #e5e7eb;border-radius:12px;overflow:hidden;">
          <div style="padding:16px 20px;display:flex;align-items:flex-start;gap:12px;">
            <div style="min-width:26px;height:26px;border-radius:50%;background:{c["num"]};color:{c["num_text"]};display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:600;flex-shrink:0;margin-top:1px;">{str(i+1).zfill(2)}</div>
            <div>
              <p style="margin:0 0 4px;font-size:15px;font-weight:600;color:#111;">{p.get("title","")}</p>
              <p style="margin:0;font-size:12px;color:#888;">📍 {p.get("source","")} &nbsp;·&nbsp; {p.get("signal","")}</p>
            </div>
          </div>
          <div style="padding:0 20px 16px 20px;">
            <p style="margin:0 0 14px;font-size:13px;color:#444;line-height:1.7;">{p.get("description","")}</p>
            <div style="background:{c["bg"]};border:1px solid {c["border"]};border-radius:8px;padding:14px 16px;">
              <p style="margin:0 0 4px;font-size:10px;letter-spacing:.07em;text-transform:uppercase;color:{c["border"]};font-weight:600;">Suggested product</p>
              <p style="margin:0 0 6px;font-size:13px;font-weight:600;color:{c["text"]};">{sol.get("name","")} <span style="font-weight:400;font-size:12px;opacity:.7;">— {sol.get("type","")}</span></p>
              <p style="margin:0;font-size:12px;color:{c["text"]};line-height:1.6;opacity:.85;">{sol.get("description","")}</p>
            </div>
            {f'<div style="margin-top:10px;">{tags}</div>' if tags else ""}
          </div>
        </div>"""

    return f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#f3f4f6;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">
  <div style="max-width:620px;margin:32px auto;background:#fff;border-radius:16px;overflow:hidden;border:1px solid #e5e7eb;">

    <div style="padding:24px 28px;border-bottom:1px solid #e5e7eb;display:flex;align-items:center;justify-content:space-between;">
      <div>
        <p style="margin:0 0 2px;font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:#aaa;">Daily intelligence</p>
        <p style="margin:0;font-size:20px;font-weight:700;color:#111;">📍 SoloSignal</p>
      </div>
      <p style="margin:0;font-size:12px;color:#aaa;">{today}</p>
    </div>

    <div style="padding:24px 28px;">
      <p style="margin:0 0 24px;font-size:14px;color:#555;line-height:1.7;padding-bottom:20px;border-bottom:1px solid #e5e7eb;">{data.get("intro","")}</p>
      {problems_html}
    </div>

    <div style="padding:16px 28px;border-top:1px solid #e5e7eb;text-align:center;font-size:11px;color:#bbb;">
      Scanned: {" · ".join(SOURCES)} &nbsp;|&nbsp; Generated by SoloSignal Agent
    </div>
  </div>
</body>
</html>"""


def send_email(html: str, subject: str):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = GMAIL_SENDER
    msg["To"]      = RECIPIENT_EMAIL
    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_SENDER, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_SENDER, RECIPIENT_EMAIL, msg.as_string())


def main():
    print("Running SoloSignal agent...")
    data = run_agent()
    print(f"Found {len(data.get('problems', []))} problems.")
    html = build_html(data)
    subject = f"SoloSignal — {datetime.now().strftime('%b %d')}: {len(data.get('problems',[]))} pain points worth building for"
    send_email(html, subject)
    print(f"Newsletter sent to {RECIPIENT_EMAIL} ✓")


if __name__ == "__main__":
    main()
