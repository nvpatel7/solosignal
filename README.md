# SoloSignal — Daily Newsletter Agent

Scans Reddit and travel blogs daily, extracts solo traveler pain points, and emails you a formatted newsletter with product ideas. Runs free on GitHub Actions.

---

## Setup (15 minutes)

### 1. Create a GitHub repo

```bash
mkdir solosignal && cd solosignal
git init
# copy newsletter_agent.py, requirements.txt, and .github/workflows/daily.yml into this folder
git add .
git commit -m "init"
gh repo create solosignal --public --push  # or create manually on github.com
```

### 2. Get a Gmail App Password

You need an **App Password** — not your real Gmail password.

1. Go to your Google Account → Security → 2-Step Verification (must be on)
2. At the bottom: **App passwords**
3. Select app: Mail → Select device: Other → name it "SoloSignal"
4. Copy the 16-character password

### 3. Get your Anthropic API key

Go to https://console.anthropic.com → API Keys → Create key

### 4. Add GitHub Secrets

In your repo: **Settings → Secrets and variables → Actions → New repository secret**

Add these four secrets:

| Secret name | Value |
|---|---|
| `ANTHROPIC_API_KEY` | your Anthropic API key |
| `GMAIL_SENDER` | your Gmail address (e.g. you@gmail.com) |
| `GMAIL_APP_PASSWORD` | the 16-char app password from step 2 |
| `RECIPIENT_EMAIL` | where to send the newsletter (can be same as sender) |

### 5. Enable the workflow

Go to your repo → **Actions** tab → click "I understand my workflows" if prompted → the workflow is now live.

It runs every day at **8:00 AM CST**. To change the time, edit the cron line in `.github/workflows/daily.yml`:
```yaml
- cron: "0 13 * * *"   # UTC — 13:00 UTC = 8:00 AM CST
```

### 6. Test it manually

Actions tab → "SoloSignal Daily Newsletter" → "Run workflow" → Run

Check your inbox in ~60 seconds.

---

## File structure

```
solosignal/
├── newsletter_agent.py          # main script
├── requirements.txt
└── .github/
    └── workflows/
        └── daily.yml            # GitHub Actions scheduler
```

## Costs

- **GitHub Actions**: free (2,000 min/month on free tier — this uses ~1 min/day)
- **Anthropic API**: ~$0.01–0.03 per run (claude-sonnet-4-6 + web search)
- **Gmail**: free

~$0.30–0.90/month total.
