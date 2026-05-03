# 🎯 AI Job Hunt Agent — Setup Guide for Sai Krishna

Runs every morning at 8am IST automatically.
Scrapes jobs → scores them → writes cover notes → emails you a digest.
**Total cost: ₹0**

---

## What you get in your Gmail every morning

- Top 10–15 matching Data Analyst / Data Scientist / ML / AI roles
- Each job scored out of 100 against your profile
- AI-written cover note (copy-paste ready)
- Resume bullets tailored to that specific JD
- One-click Apply link per job

---

## ⏱️ Setup Time: ~20 minutes (one time only)

---

## STEP 1 — Get your free Apify API token (5 minutes)

1. Go to **https://apify.com** → click **Sign Up** (free)
2. Use your Google account to sign up (fastest)
3. After signup, go to **https://console.apify.com/account/integrations**
4. Copy your **Personal API token** (looks like: `apify_api_xxxxxxxxxxxx`)
5. Save it somewhere — you'll need it in Step 4

> Free tier gives you $5 credit/month → enough for ~5,000 job results per month

---

## STEP 2 — Get your free Anthropic API key (5 minutes)

1. Go to **https://console.anthropic.com** → click **Sign Up** (free)
2. Verify your email
3. Go to **https://console.anthropic.com/settings/keys**
4. Click **Create Key** → name it "job-agent" → copy the key
5. Save it — looks like: `sk-ant-api03-xxxxxxxxxx`

> Free $5 credit on signup → enough for ~5,000 cover notes at $0.001 each

---

## STEP 3 — Set up Gmail App Password (5 minutes)

> This is NOT your normal Gmail password. It's a special password just for apps.

1. Go to **https://myaccount.google.com/security**
2. Make sure **2-Step Verification is ON** (enable it if not)
3. Go to **https://myaccount.google.com/apppasswords**
4. Click **Create** → name it "job-agent" → click **Create**
5. Copy the 16-character password shown (like: `abcd efgh ijkl mnop`)
6. Remove spaces when saving it: `abcdefghijklmnop`

---

## STEP 4 — Upload code to GitHub (5 minutes)

1. Go to **https://github.com** → click **New repository**
2. Name it: `job-hunt-agent`
3. Set it to **Private** (important — keeps your secrets safe)
4. Click **Create repository**
5. Upload all the files from this folder:
   - Drag and drop the entire folder contents into GitHub
   - OR use GitHub Desktop app (download from desktop.github.com)
   - Make sure the folder structure looks like this:
     ```
     job-hunt-agent/
     ├── .github/
     │   └── workflows/
     │       └── daily_job_hunt.yml
     ├── scrapers/
     │   ├── __init__.py
     │   └── apify_scraper.py
     ├── agents/
     │   ├── __init__.py
     │   ├── scorer.py
     │   ├── cover_note.py
     │   └── email_digest.py
     ├── utils/
     │   ├── __init__.py
     │   └── tracker.py
     ├── agent.py
     ├── requirements.txt
     └── .gitignore
     ```

---

## STEP 5 — Add your secrets to GitHub (3 minutes)

1. In your GitHub repo, go to **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret** for EACH of these:

| Secret Name     | Value                          | Where you got it |
|----------------|-------------------------------|-----------------|
| `APIFY_TOKEN`   | `apify_api_xxxxxxxxxxxx`      | Step 1          |
| `ANTHROPIC_KEY` | `sk-ant-api03-xxxxxxxxxx`     | Step 2          |
| `GMAIL_USER`    | `saikrishna33388@gmail.com`   | Your Gmail      |
| `GMAIL_APP_PASS`| `abcdefghijklmnop`            | Step 3          |

> ⚠️ Add them one by one. Click "New repository secret", type the name, paste the value, click "Add secret".

---

## STEP 6 — Test it manually right now (1 minute)

1. In your GitHub repo, click **Actions** tab
2. Click **Daily Job Hunt Agent** on the left
3. Click **Run workflow** → **Run workflow** (green button)
4. Wait 3–5 minutes
5. Check your Gmail — you should get the digest!

If it worked → 🎉 Done! It will now run every morning at 8am IST automatically.

---

## 🔧 Customising the agent

Edit `agent.py` to change:
- `"min_score": 55` → raise to 70 if you want fewer, higher-quality matches
- `"work_modes": ["Remote", "Hybrid"]` → change to `["Remote"]` for remote only
- `SEARCH_QUERIES` → add/remove job titles to search for
- `"exclude_companies"` → add more companies you don't want

---

## ❓ Troubleshooting

**No email received?**
- Check GitHub Actions logs: Actions tab → click the latest run → see errors
- Verify your Gmail App Password is correct (no spaces)
- Check Gmail spam folder

**Apify error?**
- Verify your APIFY_TOKEN secret is correct
- Check Apify console: console.apify.com to see if run happened

**"Module not found" error?**
- Make sure all files are uploaded including `__init__.py` files in scrapers/, agents/, utils/

---

## 📊 What you do every morning (5 minutes)

1. Open Gmail → find email from yourself with subject "🎯 X New Data Jobs Found"
2. Read through the top jobs
3. For any job you like → click **Apply Now →** button
4. LinkedIn Easy Apply opens → review the pre-filled fields → click **Submit**
5. Done!

The agent does the searching, scoring, and writing. You just decide which ones to apply to.

---

## 💰 Running costs

| Tool           | Cost              |
|---------------|-------------------|
| GitHub Actions | FREE (2,000 min/month free) |
| Apify          | ~$1.50/month (100 jobs/day × 30 days × $0.001) |
| Claude API     | ~$0.30/month (10 cover notes/day × 30 days × $0.001) |
| Gmail          | FREE |
| **Total**      | **~$1.80/month** after free credits run out |

> Free credits (Apify $5 + Anthropic $5) last approximately 3 months of daily runs.
