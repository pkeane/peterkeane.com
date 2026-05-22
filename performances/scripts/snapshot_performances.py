"""Parse setlists out of Peter's Google Takeout YouTube video metadata.

Reads the videos*.csv files from a Takeout export and writes
data/performances.json — a flat list of song-performance records, sorted
reverse-chronologically by show, then in setlist order within each show.

Why Takeout instead of yt-dlp?
- Takeout includes Unlisted and Private videos. yt-dlp can only see the
  Public channel listing, which misses ~half of Peter's shows.
- No rate limits, no 1000+ network calls.

Source layout (typical):
    ~/Downloads/Takeout 2/YouTube and YouTube Music/video metadata/
        videos.csv, videos(1).csv, ..., videos(9).csv

Each video has one row per metadata edit. We keep the row with the latest
"Video Create Timestamp" (which is really the metadata version timestamp).

Setlist parsing: same rules as before — lines that look like
"00:00 Song" or "Song 0:00", with M:SS / MM:SS / H:MM:SS timestamps.

Usage:
    ./venv/bin/python scripts/snapshot_performances.py [takeout_dir]

Default: latest matching ~/Downloads/Takeout*/YouTube and YouTube Music/video metadata/
"""
import csv
import glob
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "performances.json"

TS_LEADING = re.compile(r"^\s*(\d{1,2}(?::\d{2}){1,2})\s+(.+?)\s*$")
TS_TRAILING = re.compile(r"^\s*(.+?)\s+(\d{1,2}(?::\d{2}){1,2})\s*$")


def find_takeout_dir() -> Path:
    candidates = sorted(
        Path.home().glob("Downloads/Takeout*/YouTube and YouTube Music/video metadata"),
        key=lambda p: p.parent.parent.name,
    )
    if not candidates:
        sys.exit(
            "no Takeout YouTube metadata found under ~/Downloads. "
            "Pass the path explicitly as the first argument."
        )
    return candidates[-1]


def hms_to_seconds(ts: str) -> int:
    parts = [int(p) for p in ts.split(":")]
    if len(parts) == 2:
        return parts[0] * 60 + parts[1]
    return parts[0] * 3600 + parts[1] * 60 + parts[2]


def match_line(line: str):
    m = TS_LEADING.match(line)
    if m:
        return m.group(1), m.group(2)
    m = TS_TRAILING.match(line)
    if m:
        return m.group(2), m.group(1)
    return None


def parse_setlist(desc: str):
    if not desc:
        return
    for raw in desc.splitlines():
        hit = match_line(raw)
        if not hit:
            continue
        ts, title = hit
        title = title.strip().strip("-").strip()
        if not title:
            continue
        if title.lower() in {"intro", "outro", "tuning", "talk", "talking"}:
            continue
        yield ts, title


def main():
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else find_takeout_dir()
    if not src.exists():
        sys.exit(f"directory not found: {src}")

    by_id = defaultdict(list)
    for f in sorted(glob.glob(str(src / "videos*.csv"))):
        with open(f, newline='') as fh:
            for row in csv.DictReader(fh):
                by_id[row["Video ID"]].append(row)

    # Latest metadata version per video (descriptions can change over time).
    latest = {}
    for vid, rows in by_id.items():
        rows.sort(key=lambda r: r.get("Video Create Timestamp", ""))
        latest[vid] = rows[-1]

    perfs = []
    n_with_setlist = 0
    for vid, r in latest.items():
        desc = r.get("Video Description (Original)") or ""
        title = r.get("Video Title (Original)") or ""
        # Publish timestamp like "2025-12-21 03:25:42 UTC" or ISO-ish.
        pub = (r.get("Video Publish Timestamp") or r.get("Video Create Timestamp") or "")[:10]
        if not pub or pub == "":
            continue
        url = f"https://www.youtube.com/watch?v={vid}"

        had = False
        for ts, song in parse_setlist(desc):
            had = True
            perfs.append({
                "song": song,
                "date": pub,
                "video_id": vid,
                "video_title": title,
                "video_url": url,
                "timestamp": ts,
                "url": f"{url}&t={hms_to_seconds(ts)}s",
                "privacy": r.get("Privacy"),
            })
        if had:
            n_with_setlist += 1

    # Sort: show order (asc timestamp within a video), then by date desc.
    perfs.sort(key=lambda p: (p["video_id"], hms_to_seconds(p["timestamp"])))
    perfs.sort(key=lambda p: p["date"], reverse=True)

    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(perfs, ensure_ascii=False, indent=1))
    print(
        f"Read {len(latest)} videos from {src.parent.parent.name}; "
        f"{n_with_setlist} have setlists; {len(perfs):,} performances written to {OUT}"
    )


if __name__ == "__main__":
    main()
