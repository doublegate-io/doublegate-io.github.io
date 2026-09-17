# doublegate-site — the public site

`*.html` at the root is **generated**; `pages/*.html` is the source. Edit a page, run
`python3 build.py`, then `python3 check.py`. The working agreement for client-facing copy is
imported below; the design repo's `AGENTS.md` governs it and is read first when the copy itself
is the work. Workspace map and skills: `../CLAUDE.md`.

@AGENTS.md

Quick reference:

- Verify: `/dg-verify doublegate-site` (`build.py --check`, `check.py`, `api-sync.py --check`,
  `svg-routes.js`; the full run adds the five browser SVG checks and `overview-check.js`).
- `/dg-tone pages/<page>.html --client` for the tone audit and the vocabulary bar before a commit;
  `check.py` has no opinion on register.
- Assets from `doublegate-ui` are pinned by `python3 ui-sync.py`; `api/*.json` by
  `python3 api-sync.py` from the sibling gates. Both are checked, never hand-edited.
