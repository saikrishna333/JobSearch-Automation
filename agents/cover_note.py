"""
agents/cover_note.py

Uses Claude API (claude-haiku — cheapest model) to write a
personalised cover note for each job.

FREE TIER:
  Anthropic gives $5 free credit when you sign up at console.anthropic.com
  Using claude-haiku: ~$0.001 per cover note
  → 5,000 cover notes free before you spend a single rupee
"""

import anthropic, logging

log = logging.getLogger(__name__)


def generate_cover_notes(jobs: list, profile: dict, api_key: str) -> None:
    """
    Generates cover notes in-place for each job dict.
    Adds job["cover_note"] and job["resume_bullets"] keys.
    """
    if not api_key:
        log.warning("    No ANTHROPIC_KEY set — skipping cover notes")
        for job in jobs:
            job["cover_note"]     = None
            job["resume_bullets"] = None
        return

    client = anthropic.Anthropic(api_key=api_key)

    for i, job in enumerate(jobs, 1):
        log.info(f"    [{i}/{len(jobs)}] {job['title']} @ {job['company']}")
        try:
            job["cover_note"], job["resume_bullets"] = _generate(client, job, profile)
        except Exception as e:
            log.warning(f"    Cover note failed: {e}")
            job["cover_note"]     = None
            job["resume_bullets"] = None


def _generate(client, job: dict, profile: dict):
    """Returns (cover_note_text, resume_bullets_text)"""

    highlights = "\n".join(f"- {h}" for h in profile.get("highlights", []))
    matched    = ", ".join(job.get("matched_skills", []))
    jd_snippet = (job.get("description") or "")[:1500]

    prompt = f"""You are a professional career coach helping {profile['name']} apply for a job.

CANDIDATE PROFILE:
- Current role: {profile['current_role']}
- Experience: {profile['experience_years']} years
- Education: {profile['education']}
- Key highlights:
{highlights}
- Skills matched to this JD: {matched}

JOB DETAILS:
- Title: {job['title']}
- Company: {job['company']}
- Location: {job['location']} ({job['work_mode']})
- JD excerpt:
{jd_snippet}

TASK: Write TWO things:

1. COVER_NOTE (3 short paragraphs, max 150 words total):
   - Para 1: Why you're excited about THIS specific company/role (1-2 sentences)
   - Para 2: Your 2-3 most relevant achievements from the highlights above
   - Para 3: One sentence closing with call to action
   Make it personal, confident, not generic. Reference the company name.

2. RESUME_BULLETS (3 bullet points):
   Rewrite 3 of the candidate's highlights to specifically match this JD's keywords.
   Each bullet: start with strong action verb, include a number/metric, end with impact.

FORMAT your response exactly like this:
COVER_NOTE:
[cover note text here]

RESUME_BULLETS:
[3 bullet points here]"""

    message = client.messages.create(
        model      = "claude-haiku-4-5-20251001",
        max_tokens = 600,
        messages   = [{"role": "user", "content": prompt}],
    )

    text = message.content[0].text

    # Parse the two sections
    cover_note     = ""
    resume_bullets = ""

    if "COVER_NOTE:" in text and "RESUME_BULLETS:" in text:
        parts          = text.split("RESUME_BULLETS:")
        cover_note     = parts[0].replace("COVER_NOTE:", "").strip()
        resume_bullets = parts[1].strip() if len(parts) > 1 else ""
    else:
        cover_note = text.strip()

    return cover_note, resume_bullets
