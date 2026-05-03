"""
╔══════════════════════════════════════════════════════════════════╗
║         SAI KRISHNA — AI JOB HUNT AGENT  v1.0                   ║
║         Free • Runs daily via GitHub Actions • Zero manual work  ║
╚══════════════════════════════════════════════════════════════════╝

FLOW:
  1. Apify scrapes LinkedIn, Naukri, Indeed (last 24 hrs)
  2. Python scores & filters against your profile
  3. Claude AI tailors resume bullet-points + writes cover note
  4. Gmail sends you a beautiful daily digest
  5. You open email, click apply link, hit Submit (2 min total)
"""

import os, logging
from datetime import datetime
from scrapers.apify_scraper  import scrape_jobs
from agents.scorer           import score_and_filter
from agents.cover_note       import generate_cover_notes
from agents.email_digest     import send_digest
from utils.tracker           import load_tracker, save_tracker

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(message)s",
    datefmt="%H:%M:%S"
)
log = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
#  YOUR PROFILE  ← Edit this section once with your details
# ─────────────────────────────────────────────────────────────────────────────
PROFILE = {
    "name":    "Allam Sai Krishna",
    "email":   "saikrishna33388@gmail.com",
    "phone":   "7337298330",
    "linkedin":"linkedin.com/in/saikrishna333",
    "github":  "github.com/saikrishna333",

    # All skills you have — used for matching
    "skills": [
        "Python", "SQL", "Pandas", "NumPy", "Scikit-learn",
        "PySpark", "Spark", "Hadoop",
        "Power BI", "Tableau", "Excel",
        "LangChain", "GenAI", "LLM", "MCP", "Claude AI", "OpenAI",
        "NLP", "Machine Learning", "Deep Learning",
        "Flask", "Streamlit", "FastAPI",
        "AWS", "Azure", "GCP",
        "PostgreSQL", "MySQL", "MongoDB",
        "EDA", "Data Visualization", "Statistics",
        "Control-M", "dbt", "Airflow",
    ],

    # Your strongest differentiators — used in cover notes
    "highlights": [
        "Built an end-to-end AI newsletter system using MCP + Claude AI (Oct–Dec 2025)",
        "Led CreditLens implementations for banks (Moody's Analytics credit risk platform)",
        "Built fraud detection ML model using PySpark MLlib with 18% performance improvement",
        "Reduced manual reporting effort by 80% using Python + SQL automation",
        "Built LangChain NLP document retrieval system (Chat With Document)",
        "Power BI dashboards reduced report generation time by 30%",
        "AWS CLF-02 Certified, Azure AZ-900 Certified",
        "3+ years hands-on: Python, SQL, Power BI, PySpark, ML, GenAI",
    ],

    "experience_years": 3,
    "current_role":     "Associate Consultant – Data Analytics & AI, Capgemini",
    "education":        "B.Tech Computer Engineering (Data Science), Presidency University 2022",

    # Roles you're targeting
    "target_roles": [
        "Data Analyst", "Senior Data Analyst",
        "Data Scientist", "ML Engineer",
        "AI Analyst", "Analytics Engineer",
        "Business Intelligence Analyst", "BI Developer",
        "Data Engineer", "ML Analyst",
    ],

    "work_modes":   ["Remote", "Hybrid"],   # Accept both
    "locations":    ["India"],

    # Score threshold — only include jobs at or above this score (0-100)
    "min_score": 55,

    # These companies will be skipped entirely
    "exclude_companies": [
        "capgemini", "infosys", "wipro", "tcs", "hcl",
        "accenture", "cognizant", "tech mahindra", "mphasis",
    ],
}

# Search queries sent to job portals
SEARCH_QUERIES = [
    "Data Analyst remote India",
    "Senior Data Analyst remote",
    "Data Scientist remote India",
    "ML Analyst remote India",
    "AI Analyst remote",
    "Analytics Engineer India remote",
    "Business Intelligence Analyst remote India",
    "Machine Learning Engineer remote India",
    "Python Data Analyst remote",
    "GenAI Data Analyst India",
]

MAX_COVER_NOTES = 10   # Generate AI cover notes for top N jobs only


# ─────────────────────────────────────────────────────────────────────────────
def run():
    log.info("=" * 60)
    log.info(f"  Job Hunt Agent — {datetime.now().strftime('%A %d %b %Y, %H:%M')}")
    log.info("=" * 60)

    # Load tracker so we never send you the same job twice
    tracker = load_tracker("output/tracker.json")

    # ── STEP 1: SCRAPE ───────────────────────────────────────────────────────
    log.info("\n📡  Scraping jobs...")
    raw_jobs = scrape_jobs(
        queries=SEARCH_QUERIES,
        apify_token=os.environ["APIFY_TOKEN"],
        hours_old=26,
    )
    log.info(f"    Raw results: {len(raw_jobs)} jobs")

    # ── STEP 2: SCORE & FILTER ───────────────────────────────────────────────
    log.info("\n🧠  Scoring jobs against your profile...")
    matched_jobs = score_and_filter(raw_jobs, PROFILE, tracker)
    log.info(f"    Matched (score ≥ {PROFILE['min_score']}): {len(matched_jobs)} jobs")

    if not matched_jobs:
        log.info("\n    No new matching jobs today — sending empty digest.")
        send_digest([], PROFILE,
                    os.environ["GMAIL_USER"],
                    os.environ["GMAIL_APP_PASS"])
        return

    # ── STEP 3: AI COVER NOTES ───────────────────────────────────────────────
    log.info(f"\n✍️   Writing AI cover notes for top {min(MAX_COVER_NOTES, len(matched_jobs))} jobs...")
    top_jobs = matched_jobs[:MAX_COVER_NOTES]
    generate_cover_notes(top_jobs, PROFILE, os.environ.get("ANTHROPIC_KEY", ""))

    # ── STEP 4: SEND DIGEST EMAIL ────────────────────────────────────────────
    log.info("\n📧  Sending daily digest to Gmail...")
    send_digest(
        jobs      = top_jobs,
        profile   = PROFILE,
        gmail_user= os.environ["GMAIL_USER"],
        gmail_pass= os.environ["GMAIL_APP_PASS"],
    )

    # ── STEP 5: UPDATE TRACKER ───────────────────────────────────────────────
    all_ids = [j.get("id", "") for j in matched_jobs if j.get("id")]
    tracker["seen_ids"] = list(set(tracker.get("seen_ids", []) + all_ids))[-3000:]
    tracker.setdefault("runs", []).append({
        "date":    datetime.now().isoformat(),
        "scraped": len(raw_jobs),
        "matched": len(matched_jobs),
        "digest":  len(top_jobs),
    })
    save_tracker(tracker, "output/tracker.json")

    log.info(f"\n✅  Done! Digest with {len(top_jobs)} jobs sent to {os.environ['GMAIL_USER']}")
    log.info("    Open your Gmail to review and apply.\n")


if __name__ == "__main__":
    run()
