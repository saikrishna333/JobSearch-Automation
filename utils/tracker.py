"""
utils/tracker.py
Persists seen job IDs so the agent never sends you the same job twice.
"""
import json, os, logging

log = logging.getLogger(__name__)


def load_tracker(path: str) -> dict:
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                data = json.load(f)
                log.info(f"    Tracker loaded — {len(data.get('seen_ids', []))} seen jobs")
                return data
        except Exception as e:
            log.warning(f"    Could not load tracker ({e}), starting fresh")
    return {"seen_ids": [], "runs": []}


def save_tracker(tracker: dict, path: str) -> None:
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
    with open(path, "w") as f:
        json.dump(tracker, f, indent=2)
    log.info(f"    Tracker saved — {len(tracker.get('seen_ids', []))} total seen jobs")
