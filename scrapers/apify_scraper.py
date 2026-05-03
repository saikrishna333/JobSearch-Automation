"""
scrapers/apify_scraper.py

Uses Apify free tier ($5 credit/month) to scrape LinkedIn jobs.
Cost per job: ~$0.001 → roughly 5,000 jobs free per month.
At 100 jobs/day × 30 days = 3,000 jobs → well within free tier.
"""

import requests, time, logging
from datetime import datetime, timezone, timedelta

log = logging.getLogger(__name__)

ACTOR    = "curious_coder~linkedin-jobs-scraper"
API_BASE = "https://api.apify.com/v2"


def scrape_jobs(queries: list, apify_token: str, hours_old: int = 26) -> list:
    """
    Runs the Apify LinkedIn scraper and returns normalised job dicts.
    Filters out jobs older than `hours_old` hours.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours_old)

    # Build LinkedIn search URLs with 24h filter (f_TPR=r86400)
    urls = []
    for q in queries:
        encoded = requests.utils.quote(q)
        urls.append(
            f"https://www.linkedin.com/jobs/search/"
            f"?keywords={encoded}&f_TPR=r86400&f_WT=2&pageNum=0"
            # f_WT=2 = Remote filter on LinkedIn
        )

    log.info(f"    Starting Apify run with {len(urls)} search URLs...")

    # ── Start actor run ──────────────────────────────────────────────────────
    resp = requests.post(
        f"{API_BASE}/acts/{ACTOR}/runs",
        params={"token": apify_token},
        json={
            "urls":          urls,
            "count":         25,      # jobs per search URL
            "scrapeCompany": False,   # faster + cheaper
        },
        headers={"Content-Type": "application/json"},
        timeout=30,
    )
    resp.raise_for_status()
    run_data   = resp.json()["data"]
    run_id     = run_data["id"]
    log.info(f"    Apify run started — ID: {run_id}")

    # ── Poll until done ──────────────────────────────────────────────────────
    for attempt in range(90):          # wait up to 7.5 minutes
        time.sleep(5)
        r = requests.get(
            f"{API_BASE}/acts/{ACTOR}/runs/{run_id}",
            params={"token": apify_token},
            timeout=15,
        )
        status = r.json()["data"]["status"]
        if status == "SUCCEEDED":
            dataset_id = r.json()["data"]["defaultDatasetId"]
            log.info(f"    Run succeeded. Dataset: {dataset_id}")
            break
        if status in ("FAILED", "ABORTED", "TIMED-OUT"):
            raise RuntimeError(f"Apify run ended with status: {status}")
    else:
        raise TimeoutError("Apify run timed out after 7.5 minutes")

    # ── Fetch results ────────────────────────────────────────────────────────
    r = requests.get(
        f"{API_BASE}/datasets/{dataset_id}/items",
        params={"token": apify_token, "limit": 500},
        timeout=30,
    )
    r.raise_for_status()
    raw = r.json()
    log.info(f"    Fetched {len(raw)} raw items")

    # ── Normalise ────────────────────────────────────────────────────────────
    jobs = []
    for item in raw:
        # Recency filter
        posted_str = item.get("postedAt", "")
        try:
            posted_dt = datetime.fromisoformat(posted_str.replace("Z", "+00:00"))
            if posted_dt < cutoff:
                continue
        except Exception:
            pass   # unparseable date → include anyway

        # Work mode
        wt = item.get("workplaceTypes", [])
        if isinstance(wt, str):
            wt = [wt]
        if "Remote" in wt:
            mode = "Remote"
        elif "Hybrid" in wt:
            mode = "Hybrid"
        else:
            mode = "On-site"

        jobs.append({
            "id":          str(item.get("id", "")),
            "title":       item.get("title", "").strip(),
            "company":     item.get("companyName", "").strip(),
            "location":    item.get("location", "").strip(),
            "work_mode":   mode,
            "posted_at":   posted_str,
            "url":         item.get("link", ""),
            "description": (item.get("descriptionText") or "")[:4000],
            "seniority":   item.get("seniorityLevel", ""),
            "emp_type":    item.get("employmentType", ""),
            "applicants":  item.get("applicantsCount", ""),
        })

    log.info(f"    After recency filter: {len(jobs)} jobs")
    return jobs
