# performances/

The **Performances** page for peterkeane.com — songs Peter has performed live,
parsed from setlists in his @PeterKeaneMusic show video descriptions. Grouped by
show, reverse chronological, with a client-side song-title filter box.

Live at https://peterkeane.com/performances/. Migrated from the standalone
`music_and_memory` (github.com/pkeane/mm) project; only the active pipeline came
over.

## Layout

- `data/performances.json` — generated. One record per song performed.
- `scripts/snapshot_performances.py` — reads Google Takeout CSVs from
  `~/Downloads/Takeout*/YouTube and YouTube Music/video metadata/`, writes
  `data/performances.json`. Takeout includes Unlisted and Private videos that
  yt-dlp can't see, so it's strictly more comprehensive.
- `scripts/build_site.py` — reads `data/performances.json`, writes
  `performances/index.html` (i.e. this directory's `index.html`).
- `index.html` — generated build output, served directly by peterkeane.com's
  GitHub Pages deploy (main branch root).

Both scripts are stdlib-only; run them with `python3` (no venv).

## Workflow

```bash
# from peterkeane.com/performances/
python3 scripts/snapshot_performances.py   # when a new Takeout has arrived
python3 scripts/build_site.py              # rebuild index.html
```

Then commit and push peterkeane.com as usual — there's no separate deploy step.
(The old `mm` repo published `site/` to a `gh-pages` branch via `git subtree
split`; that mechanism is gone now that this lives inside peterkeane.com.)

## Setlist format (performance parser)

Setlists are parsed from descriptions on @PeterKeaneMusic videos. The parser
recognises both forms Peter uses:

```
00:00 Song Title
03:05 Next Song

Song Title 0:00
Next Song 3:05
```

Timestamp can be `M:SS`, `MM:SS`, or `H:MM:SS`. Lines that don't match are
ignored. Empty and prose-only descriptions yield no songs.

## Source files (not committed)

- `~/Downloads/Takeout*/YouTube and YouTube Music/video metadata/videos*.csv` —
  Google Takeout, *YouTube and YouTube Music → video metadata*. Contains every
  video Peter has uploaded (Public, Unlisted, Private) with original
  descriptions — more complete than yt-dlp can fetch from the public listing.
