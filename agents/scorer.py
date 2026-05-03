"""
agents/scorer.py

Pure Python scoring engine — zero API cost.
Scores each job 0-100 against Sai's profile using keyword matching
and heuristics. Fast, free, and runs entirely locally.
"""

import re, logging

log = logging.getLogger(__name__)

# Keywords that strongly suggest ML/AI work (good for DS path)
ML_SIGNALS = [
    "machine learning", " ml ", "deep learning", "neural network",
    "scikit", "tensorflow", "pytorch", "xgboost", "lgbm",
    "nlp", "natural language", "llm", "large language model",
    "generative ai", "genai", "langchain", "openai", "gpt",
    "classification", "regression", "clustering", "feature engineering",
    "model training", "model deployment", "mlops", "pyspark mllib",
    "recommendation", "forecasting", "predictive model",
]

# Keywords that suggest GenAI/LLM roles (Sai's unique edge)
GENAI_SIGNALS = [
    "genai", "generative ai", "llm", "large language model",
    "langchain", "openai", "gpt", "claude", "mcp",
    "model context protocol", "rag", "vector", "embedding",
    "prompt engineering", "fine-tuning",
]

# Internship / entry-level signals to skip
SKIP_SIGNALS = [
    "intern", "internship", "trainee", "fresher",
    "0-1 year", "0 years experience", "no experience required",
]

# Seniority signals for 5+ year requirements (penalty)
OVERQUALIFIED_REQUIRED = [
    r"\b[6-9]\+?\s*years?\b",
    r"\b1[0-9]\+?\s*years?\b",
]


def score_and_filter(jobs: list, profile: dict, tracker: dict) -> list:
    """
    Returns jobs scoring >= min_score, sorted by score descending.
    Skips: already seen, excluded companies, internships.
    """
    seen_ids    = set(tracker.get("seen_ids", []))
    min_score   = profile.get("min_score", 55)
    excl        = [c.lower() for c in profile.get("exclude_companies", [])]
    skills      = [s.lower() for s in profile.get("skills", [])]
    target_roles= [r.lower() for r in profile.get("target_roles", [])]
    accept_modes= [m.lower() for m in profile.get("work_modes", ["remote", "hybrid"])]

    results = []

    for job in jobs:
        jid     = job.get("id", "")
        title   = job.get("title", "").lower()
        company = job.get("company", "").lower()
        desc    = job.get("description", "").lower()
        mode    = job.get("work_mode", "").lower()
        full    = f"{title} {desc}"

        # ── Hard filters (skip entirely) ─────────────────────────────────────
        if jid and jid in seen_ids:
            continue
        if any(ex in company for ex in excl):
            continue
        if any(s in full for s in SKIP_SIGNALS):
            continue

        # ── Scoring ──────────────────────────────────────────────────────────
        score = 0

        # 1. Work mode match (20 pts)
        if mode in accept_modes:
            score += 20
        elif mode == "on-site":
            score += 5    # still show on-site but lower score

        # 2. Role title match (20 pts)
        role_score = 0
        for role in target_roles:
            if role in title:
                role_score = 20
                break
            words = role.split()
            if sum(1 for w in words if w in title) >= len(words) * 0.6:
                role_score = max(role_score, 12)
        score += role_score

        # 3. Skills match (25 pts)
        matched = [s for s in skills if s.lower() in full]
        ratio   = len(matched) / max(len(skills), 1)
        score  += int(ratio * 25)
        job["matched_skills"] = matched[:10]
        job["skills_pct"]     = f"{int(ratio * 100)}%"

        # 4. ML/AI exposure (20 pts) — DS path value
        ml_hits = sum(1 for kw in ML_SIGNALS if kw in full)
        ml_pts  = min(ml_hits * 3, 20)
        score  += ml_pts
        job["has_ml"]      = ml_hits >= 2
        job["ml_score"]    = ml_pts

        # 5. GenAI bonus (15 pts) — Sai's unique edge
        genai_hits = sum(1 for kw in GENAI_SIGNALS if kw in full)
        job["genai_bonus"] = genai_hits > 0
        if genai_hits > 0:
            score += min(genai_hits * 5, 15)

        # ── Penalties ────────────────────────────────────────────────────────
        # Too many applicants = competitive
        try:
            applicants = int(re.sub(r"[^\d]", "", str(job.get("applicants", "0"))) or 0)
            if applicants > 400:
                score -= 8
            elif applicants > 200:
                score -= 4
        except Exception:
            pass

        # Requires 6+ years (Sai has 3)
        if any(re.search(p, desc) for p in OVERQUALIFIED_REQUIRED):
            score -= 12

        # ── Final score ───────────────────────────────────────────────────────
        job["score"] = max(0, min(score, 100))

        # DS path label
        if ml_pts >= 15 or genai_hits > 0:
            job["ds_path"] = "HIGH"
        elif ml_pts >= 8:
            job["ds_path"] = "MEDIUM"
        else:
            job["ds_path"] = "LOW"

        if job["score"] >= min_score:
            results.append(job)

    # Sort by score descending
    results.sort(key=lambda j: j["score"], reverse=True)

    log.info(f"    Scored {len(jobs)} → {len(results)} passed threshold {min_score}")
    return results
