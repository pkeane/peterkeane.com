# peterkeane.com

Peter's musician site — hand-written static HTML/CSS, no build step, no framework.
Live at https://peterkeane.com (GitHub Pages, repo `pkeane/peterkeane.com`, served from
the **`main` branch root**; `CNAME` holds the custom domain).

## Layout
- `index.html` — the whole site: hero, bio, Listen Online (Spotify/Apple/Bandcamp),
  Albums, Performances. Sections are plain `<h2 class="section-title">` blocks.
- `css/style.css` — all styling.
- `birthday.html` — standalone 60th-birthday card-ideas page, not linked from the nav.
- `performances/` — **its own subproject with its own CLAUDE.md.** Read that before
  touching anything in it; `performances/index.html` is generated, not hand-edited.

## Working here
- Edit HTML/CSS directly. Deploy = commit and push to `main`; Pages does the rest.
- Standing permission to push (see global CLAUDE.md) — don't ask for routine content edits.
- Bio and blurb copy: matter-of-fact, no promotional adjectives.
