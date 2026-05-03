"""
agents/email_digest.py

Sends a beautiful HTML digest email to Sai's Gmail every morning.
Uses Gmail SMTP (free) with an App Password.
"""

import smtplib, logging
from email.mime.multipart import MIMEMultipart
from email.mime.text      import MIMEText
from datetime             import datetime

log = logging.getLogger(__name__)

DS_COLORS = {"HIGH": "#1a7a4a", "MEDIUM": "#c25c00", "LOW": "#666666"}
DS_BG     = {"HIGH": "#e6f4ed", "MEDIUM": "#fff3e0", "LOW": "#f5f5f5"}


def send_digest(jobs: list, profile: dict, gmail_user: str, gmail_pass: str) -> None:
    today     = datetime.now().strftime("%A, %d %b %Y")
    recipient = profile["email"]
    count     = len(jobs)

    subject = (
        f"🎯 {count} New Data Jobs Found — {today}"
        if count > 0
        else f"Job Agent Report — No new matches today ({today})"
    )

    html = _build_html(jobs, profile, today)
    text = _build_plain(jobs, today)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = gmail_user
    msg["To"]      = recipient
    msg.attach(MIMEText(text, "plain"))
    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(gmail_user, gmail_pass)
            server.sendmail(gmail_user, recipient, msg.as_string())
        log.info(f"    Email sent to {recipient}")
    except Exception as e:
        log.error(f"    Failed to send email: {e}")
        raise


def _score_color(score: int) -> str:
    if score >= 75: return "#1a7a4a"
    if score >= 55: return "#c25c00"
    return "#666666"


def _score_bg(score: int) -> str:
    if score >= 75: return "#e6f4ed"
    if score >= 55: return "#fff3e0"
    return "#f5f5f5"


def _build_html(jobs: list, profile: dict, today: str) -> str:
    name  = profile["name"].split()[0]
    count = len(jobs)

    # Header
    html = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<style>
  body {{ font-family: Arial, sans-serif; color: #333; margin: 0; padding: 0; background: #f9f9f9; }}
  .wrap {{ max-width: 680px; margin: 0 auto; background: #fff; }}
  .header {{ background: #1a3c5e; color: #fff; padding: 28px 32px; }}
  .header h1 {{ margin: 0; font-size: 22px; }}
  .header p {{ margin: 6px 0 0; font-size: 14px; color: #a8c8e8; }}
  .summary {{ background: #eef4fb; padding: 16px 32px; border-bottom: 1px solid #dce8f5; font-size: 14px; color: #1a3c5e; }}
  .job-card {{ border: 1px solid #e0e0e0; border-radius: 8px; margin: 16px 32px; padding: 20px; }}
  .job-title {{ font-size: 17px; font-weight: bold; color: #1a3c5e; margin: 0 0 4px; }}
  .job-meta {{ font-size: 13px; color: #777; margin: 0 0 12px; }}
  .badge {{ display: inline-block; padding: 3px 10px; border-radius: 12px; font-size: 12px; font-weight: bold; margin: 0 4px 8px 0; }}
  .skills {{ font-size: 12px; color: #555; margin: 10px 0; }}
  .cover {{ background: #f8f9ff; border-left: 3px solid #3b7dd8; padding: 12px 14px; margin: 12px 0; font-size: 13px; line-height: 1.6; color: #333; }}
  .bullets {{ background: #f6fff8; border-left: 3px solid #1a7a4a; padding: 12px 14px; margin: 12px 0; font-size: 13px; line-height: 1.7; color: #333; }}
  .apply-btn {{ display: inline-block; background: #1a3c5e; color: #fff !important; padding: 10px 22px; border-radius: 6px; text-decoration: none; font-size: 14px; font-weight: bold; margin-top: 12px; }}
  .footer {{ text-align: center; padding: 24px; font-size: 12px; color: #aaa; border-top: 1px solid #eee; }}
  .no-jobs {{ padding: 32px; text-align: center; color: #888; font-size: 15px; }}
</style></head><body><div class="wrap">

<div class="header">
  <h1>🎯 Your Daily Job Digest</h1>
  <p>Good morning, {name}! Here are your top {count} matches for {today}</p>
</div>

<div class="summary">
  <strong>{count} jobs matched</strong> your profile today &nbsp;|&nbsp;
  Roles: Data Analyst / Data Scientist / ML / AI &nbsp;|&nbsp;
  Mode: Remote &amp; Hybrid &nbsp;|&nbsp;
  Min score: {profile.get('min_score', 55)}
</div>
"""

    if not jobs:
        html += '<div class="no-jobs">No new matching jobs found today. The agent will check again tomorrow morning! 🌅</div>'
    else:
        for i, job in enumerate(jobs, 1):
            score      = job.get("score", 0)
            ds_path    = job.get("ds_path", "LOW")
            genai      = job.get("genai_bonus", False)
            has_ml     = job.get("has_ml", False)
            matched    = job.get("matched_skills", [])
            cover      = job.get("cover_note")
            bullets    = job.get("resume_bullets")
            url        = job.get("url", "#")
            applicants = job.get("applicants", "")

            sc = _score_color(score)
            sb = _score_bg(score)
            dc = DS_COLORS.get(ds_path, "#666")
            db = DS_BG.get(ds_path, "#f5f5f5")

            app_txt = f" · {applicants} applicants" if applicants else ""

            html += f"""
<div class="job-card">
  <div class="job-title">{i}. {job['title']}</div>
  <div class="job-meta">{job['company']} &nbsp;·&nbsp; {job['location']} &nbsp;·&nbsp; {job['work_mode']}{app_txt}</div>

  <span class="badge" style="background:{sb};color:{sc}">Score: {score}/100</span>
  <span class="badge" style="background:{db};color:{dc}">DS Path: {ds_path}</span>
  {'<span class="badge" style="background:#fff8dc;color:#7f4f00">⭐ GenAI Role</span>' if genai else ''}
  {'<span class="badge" style="background:#eef4fb;color:#1a3c5e">🤖 ML/AI Exposure</span>' if has_ml else ''}

  <div class="skills">
    <strong>Your matching skills:</strong> {', '.join(matched) if matched else 'General data skills match'}
  </div>
"""
            if cover:
                html += f'<div class="cover"><strong>📝 Cover note (ready to copy-paste):</strong><br><br>{cover.replace(chr(10), "<br>")}</div>'

            if bullets:
                html += f'<div class="bullets"><strong>📌 Resume bullets tailored for this JD:</strong><br><br>{bullets.replace(chr(10), "<br>")}</div>'

            html += f'<a href="{url}" class="apply-btn">Apply Now →</a>\n</div>\n'

    html += """
<div class="footer">
  Sent by your AI Job Hunt Agent · Running daily via GitHub Actions · Zero cost<br>
  To stop: disable the workflow in your GitHub repo
</div>
</div></body></html>"""

    return html


def _build_plain(jobs: list, today: str) -> str:
    lines = [f"Daily Job Digest — {today}", "=" * 50, ""]
    if not jobs:
        lines.append("No new matching jobs today. Agent will check again tomorrow.")
    else:
        for i, job in enumerate(jobs, 1):
            lines += [
                f"{i}. {job['title']}",
                f"   Company  : {job['company']}",
                f"   Location : {job['location']} ({job['work_mode']})",
                f"   Score    : {job.get('score', 0)}/100  |  DS Path: {job.get('ds_path','')}",
                f"   Apply    : {job.get('url', '')}",
                "",
            ]
    return "\n".join(lines)
