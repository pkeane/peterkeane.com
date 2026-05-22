# Performances

The Performances page for peterkeane.com — songs Peter has performed live,
parsed from timestamped setlists in the descriptions of his @PeterKeaneMusic
show videos. Grouped by show, reverse chronological, with a song-title filter.

Live at https://peterkeane.com/performances/.

## Adding a new performance

A new performance shows up once it's a YouTube video with a timestamped setlist
in its description. To pick it up:

1. **Request a Google Takeout** of your YouTube data — *YouTube and YouTube
   Music → "video metadata"* is enough (selecting all of YouTube also works).
2. **Unzip it into `~/Downloads/`**, so the path
   `~/Downloads/Takeout*/YouTube and YouTube Music/video metadata/videos*.csv`
   exists. The Takeout stays in Downloads — it does **not** go in this project.
   The script auto-picks the newest matching `Takeout*` folder.
3. **Run the pipeline** from this directory:
   ```bash
   python3 scripts/snapshot_performances.py   # rebuild data/performances.json from the CSV
   python3 scripts/build_site.py              # rebuild index.html
   ```
4. **Commit and push** peterkeane.com. That's the deploy — GitHub Pages serves
   the updated `index.html` automatically.

A Takeout is a full export, so step 3 rebuilds `performances.json` from scratch
every time. It's idempotent — re-running with the same Takeout changes nothing.

Why Takeout instead of scraping the channel: it includes Unlisted and Private
videos that yt-dlp can't see from the public listing, with original
descriptions, so it's strictly more complete.

## Setlist format

The parser reads timestamped setlists from video descriptions in either form:

```
00:00 Song Title          Song Title 0:00
03:05 Next Song           Next Song 3:05
```

Timestamps can be `M:SS`, `MM:SS`, or `H:MM:SS`. Lines that don't match are
ignored; empty or prose-only descriptions yield no songs.

## Files

- `data/performances.json` — generated; one record per song performed.
- `scripts/snapshot_performances.py` — Takeout CSV → `data/performances.json`.
- `scripts/build_site.py` — `data/performances.json` → `index.html`.
- `index.html` — generated build output, served by peterkeane.com's Pages deploy.

Both scripts are standard-library only — run them with `python3`, no venv needed.
