"""Build the static site.

Outputs:
- performances/index.html — Performances: songs performed live, grouped by
  show, reverse chronological, with a song-title search box. Lives at
  peterkeane.com/performances/.
"""
import html
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT_DIR = ROOT

CSS = """
:root {
  --bg: #fefdf9;
  --fg: #1f1c18;
  --muted: #6b6760;
  --rule: #e6e0d4;
  --accent: #a8431f;
}
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; background: var(--bg); color: var(--fg); }
body {
  font-family: "Iowan Old Style", "Palatino Linotype", Palatino, Georgia, serif;
  font-size: 17px;
  line-height: 1.5;
}
main { max-width: 760px; margin: 0 auto; padding: 3rem 1.5rem 6rem; }
header { border-bottom: 1px solid var(--rule); margin-bottom: 1.5rem; padding-bottom: 1rem; }
h1 { font-size: 1.6rem; margin: 0 0 0.25rem; font-weight: 600; }
header p { color: var(--muted); margin: 0; font-size: 0.95rem; }
.search { margin: 0 0 1.5rem; }
.search input {
  width: 100%;
  font: inherit;
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--rule);
  border-radius: 4px;
  background: #fff;
  color: var(--fg);
}
.search input:focus { outline: none; border-color: var(--accent); }
h2.date {
  font-size: 1rem;
  font-variant: small-caps;
  letter-spacing: 0.04em;
  color: var(--accent);
  margin: 2rem 0 0.5rem;
  font-weight: 600;
}
ul { list-style: none; margin: 0; padding: 0; }
li { padding: 0.15rem 0; }
.title { font-style: italic; }
.meta, time { color: var(--muted); font-size: 0.9rem; }
time { display: inline-block; min-width: 3.5em; }
a { color: var(--accent); text-decoration: none; }
a:hover { text-decoration: underline; }
.show[hidden], li[hidden] { display: none; }
#empty { color: var(--muted); margin-top: 2rem; }
footer { color: var(--muted); font-size: 0.85rem; margin-top: 3rem; padding-top: 1rem; border-top: 1px solid var(--rule); }
"""

JS = """
(function () {
  var box = document.getElementById('q');
  var shows = Array.prototype.slice.call(document.querySelectorAll('.show'));
  var empty = document.getElementById('empty');
  function apply() {
    var q = box.value.trim().toLowerCase();
    var anyShow = false;
    shows.forEach(function (show) {
      var anyItem = false;
      Array.prototype.forEach.call(show.querySelectorAll('li'), function (li) {
        var match = !q || li.getAttribute('data-song').indexOf(q) !== -1;
        li.hidden = !match;
        if (match) anyItem = true;
      });
      show.hidden = !anyItem;
      if (anyItem) anyShow = true;
    });
    empty.hidden = anyShow;
  }
  box.addEventListener('input', apply);
})();
"""


def fmt_date(iso: str) -> str:
    return date.fromisoformat(iso).strftime("%A, %B %-d, %Y")


def page(title: str, body: str) -> str:
    return (
        "<!doctype html>"
        f'<html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        f"<title>{html.escape(title)}</title>"
        f"<style>{CSS}</style></head><body><main>{body}</main>"
        f"<script>{JS}</script></body></html>"
    )


def build_index() -> None:
    f = DATA / "performances.json"
    rows = json.loads(f.read_text())

    n_shows = len({(r["date"], r["video_id"]) for r in rows})
    parts = [
        "<header><h1>Performances</h1>",
        f"<p>{len(rows):,} songs performed across {n_shows} shows. "
        "Setlists parsed from descriptions on @PeterKeaneMusic show videos.</p>",
        "</header>",
        '<div class="search">'
        '<input id="q" type="search" placeholder="Filter by song title…" '
        'autocomplete="off" autocapitalize="off" spellcheck="false"></div>',
    ]

    last_show = None
    for r in rows:
        show = (r["date"], r["video_id"])
        if show != last_show:
            if last_show is not None:
                parts.append("</ul></section>")
            parts.append(
                '<section class="show">'
                f'<h2 class="date">{fmt_date(r["date"])} '
                f'<span class="meta">· <a href="{html.escape(r["video_url"])}">'
                f'{html.escape(r["video_title"])}</a></span></h2>'
            )
            parts.append("<ul>")
            last_show = show
        parts.append(
            f'<li data-song="{html.escape(r["song"].lower(), quote=True)}">'
            f'<time>{html.escape(r["timestamp"])}</time> '
            f'<a class="title" href="{html.escape(r["url"])}">{html.escape(r["song"])}</a></li>'
        )
    if last_show is not None:
        parts.append("</ul></section>")

    parts.append('<p id="empty" hidden>No songs match.</p>')
    parts.append("<footer>Source: setlists in YouTube descriptions on @PeterKeaneMusic.</footer>")
    out = OUT_DIR / "index.html"
    out.write_text(page("Performances — Peter Keane", "".join(parts)))
    print(f"Wrote {out} ({out.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    OUT_DIR.mkdir(exist_ok=True)
    build_index()
