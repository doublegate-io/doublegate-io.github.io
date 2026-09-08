#!/usr/bin/env python3
"""Generate assets/sky-data.js from sky-claims.txt.

The knowledge map on sky.html draws 20 constellations, one per category of
what an organization's agents learn, and 40 claims in each. The claims are
copy — a visitor reads them in the tooltip and the arrivals feed — so they are
authored in a plain text file where a reviewer can read them as prose, and
checked here with the same gates check.py runs on the pages: no internal
vocabulary, no phase language, no duplicates, every category linked to real
neighbours.

Run:  python3 sky-data.py          (writes assets/sky-data.js)
      python3 sky-data.py --check  (fails if the output is stale — check.py calls this)
      python3 sky-data.py --feed <notes.jsonl> [--out <file>]
                                   (the same assets/sky-data.js shape from an
                                    organization gate's published feed)

Two inputs, one output. The authored file is the demo sky. The feed is the real
one: an organization gate publishes one short note per claim it processes —
which claim, what happened, what kind, which space — and never the text. From
that, a constellation per space, a point per claim, an edge per relation. The
feed carries no prose, so the vocabulary gates cannot fail on it; they run
anyway, over the labels the map will show, so both inputs answer to one
contract. Nothing from a note but its labels reaches the output: not the
signer, not the id, not the note itself.

Source format, one block per category:

    ## <id> | <display name> | <related ids, comma-separated>
    <kind>|<claim text>
    ...

Kinds: m memory, s skill, f fact, p preference, c convention — the five shapes
of belief artifact the design names (glossary: memory, skill, extracted fact,
preference, summary; the map says "convention" for the team-rule shape because
that is the word the pages use).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "sky-claims.txt"
OUT = ROOT / "assets" / "sky-data.js"

CATEGORIES = 20
PER_CATEGORY = 40
KINDS = {"m": "memory", "s": "skill", "f": "fact", "p": "preference", "c": "convention"}

# Mirror of check.py's vocabulary and phase gates. Duplicated rather than
# imported because check.py is a script that runs its checks at import time.
LEAKS = {
    "component ID": r"\bC(?:1[01]|[1-9])\s*·",
    "tracker ID": r"\bFR-\d+",
    "store filename": r"\b(?:limbo|active|record|ledger|derivation)\.db\b",
    "invariant ID": r"\bI[1-7]\b(?!\w)",
    "ADR reference": r"ADR-\d{4}",
    "milestone code": r"\bM[0-5]\b(?!\w)",
    "trust class": r"\bT-[0-4]\b",
    "sub-level": r"\bL[0-3]b?\b(?!\w)",
    "jargon": r"\b(?:quorum|limbo|k-of-n|MCP|MemoryService|hybrid retrieval|FTS|rerank)\b",
}
PHASE_LANGUAGE = re.compile(
    r"design[- ]phase|\bnot (?:yet )?(?:shipped|built|running|implemented)\b"
    r"|\bnothing (?:is |here is )?(?:built|shipped|scheduled)\b|\bdoes not exist yet\b",
    re.I)
# Claims are fragments and start lowercase; a capital is allowed only on a name.
PROPER = {"Apple", "Android", "Spark", "Delta", "Windows", "Linux", "Safari", "Kubernetes",
          "Monday", "Tuesday", "Wednesday", "Friday", "Sunday", "March", "June"}


def parse(text: str) -> list[dict]:
    cats: list[dict] = []
    for ln, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#") and not line.startswith("## "):
            continue
        if line.startswith("## "):
            parts = [p.strip() for p in line[3:].split("|")]
            if len(parts) != 3:
                sys.exit(f"{SRC.name}:{ln}: header needs id | name | related")
            cid, name, related = parts
            cats.append({"id": cid, "name": name,
                         "related": [r.strip() for r in related.split(",") if r.strip()],
                         "claims": []})
            continue
        if not cats:
            sys.exit(f"{SRC.name}:{ln}: claim before any category header")
        kind, _, claim = line.partition("|")
        if kind not in KINDS or not claim.strip():
            sys.exit(f"{SRC.name}:{ln}: expected <kind>|<claim>, kinds {sorted(KINDS)}")
        cats[-1]["claims"].append({"k": kind, "t": claim.strip(), "line": ln})
    return cats


def validate(cats: list[dict]) -> list[str]:
    errors: list[str] = []
    ids = [c["id"] for c in cats]
    if len(cats) != CATEGORIES:
        errors.append(f"{len(cats)} categories, want {CATEGORIES}")
    if len(set(ids)) != len(ids):
        errors.append(f"duplicate category ids: {sorted({i for i in ids if ids.count(i) > 1})}")
    if not all(re.fullmatch(r"[a-z][a-z0-9-]*", i) for i in ids):
        errors.append("category ids are lowercase slugs")
    seen_text: dict[str, str] = {}
    for c in cats:
        if len(c["claims"]) != PER_CATEGORY:
            errors.append(f"{c['id']}: {len(c['claims'])} claims, want {PER_CATEGORY}")
        if not c["related"]:
            errors.append(f"{c['id']}: no related categories — an island cannot link")
        for r in c["related"]:
            if r not in ids:
                errors.append(f"{c['id']}: related id {r!r} is not a category")
            if r == c["id"]:
                errors.append(f"{c['id']}: relates to itself")
        kinds = {k["k"] for k in c["claims"]}
        if len(kinds) < 4:
            errors.append(f"{c['id']}: only kinds {sorted(kinds)} — each constellation mixes shapes")
        for cl in c["claims"]:
            t = cl["t"]
            key = re.sub(r"\W+", " ", t.lower()).strip()
            if key in seen_text:
                errors.append(f"{c['id']}:{cl['line']}: duplicate of {seen_text[key]}")
            seen_text[key] = f"{c['id']}:{cl['line']}"
            if len(t) < 40:
                errors.append(f"{c['id']}:{cl['line']}: too short to be a claim -> {t!r}")
            if len(t) > 190:
                errors.append(f"{c['id']}:{cl['line']}: {len(t)} chars, tooltip holds 190")
            if t[-1] in ".!?":
                errors.append(f"{c['id']}:{cl['line']}: claims are unpunctuated fragments -> …{t[-20:]}")
            first = t.split()[0]
            proper = first.rstrip("'s") in PROPER or first.split("'")[0] in PROPER or re.search(r"[A-Z0-9-]", first[1:])
            if t[0].isupper() and not proper:
                errors.append(f"{c['id']}:{cl['line']}: claims start lowercase (it is a fragment) -> {t[:30]!r}")
            for label, pat in LEAKS.items():
                if re.search(pat, t, re.I):
                    errors.append(f"{c['id']}:{cl['line']}: {label} leak -> {t[:60]!r}")
            if PHASE_LANGUAGE.search(t):
                errors.append(f"{c['id']}:{cl['line']}: phase language -> {t[:60]!r}")
    return errors


def render(cats: list[dict], *, source: str = "sky-claims.txt", note: str = "") -> str:
    data = {
        "kinds": KINDS,
        "categories": [
            {"id": c["id"], "name": c["name"], "related": c["related"],
             "claims": [[cl["k"], cl["t"]] for cl in c["claims"]]}
            for c in cats
        ],
    }
    if note:
        data["source"] = note
    body = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    n = sum(len(c["claims"]) for c in cats)
    if source == "sky-claims.txt":
        head = ("// GENERATED by sky-data.py from sky-claims.txt — edit the .txt, not this.\n"
                f"// {len(cats)} categories × {PER_CATEGORY} claims = {n}.\n")
    else:
        head = (f"// GENERATED by sky-data.py --feed from {source} — an organization gate's published notes.\n"
                f"// {len(cats)} spaces, {n} live claims. Labels only: kind, space, authority, outcome.\n")
    return head + f"window.SKY_DATA = {body};\n"


# ---- the real sky: an organization gate's published feed ------------------------
#
# One note per processed claim, CloudEvents 1.0, `data` a closed set of labels.
# The map reads five of them and nothing else.

FEED_TYPES = {                # note type → what the map does with it
    "io.doublegate.claim.countersigned": "point",
    "io.doublegate.claim.promoted": "point",
    "io.doublegate.claim.ratified": "point",
    "io.doublegate.claim.refused": "drop",
    "io.doublegate.claim.rejected": "drop",
    "io.doublegate.claim.demoted": "drop",
    "io.doublegate.claim.related": "edge",
}
# the gate's content types → the map's five shapes; anything else is "fact"
FEED_KINDS = {"memory": "m", "skill": "s", "derived_fact": "f", "extracted_fact": "f",
              "preference": "p", "summary": "f", "imported_document": "f", "prompt_template": "c",
              "convention": "c"}
# the map never shows more than one line per point; the authority class is that line
FEED_TRUST = {"T-0": "read as it arrived", "T-1": "durable, signed by its owner",
              "T-2": "shared inside one skill", "T-3": "shared across the organization",
              "T-4": "imported, countersigned", "T-5": "from a connector"}
FEED_LABEL_FIELDS = ("content_type", "space", "trust_class", "outcome")
#: Fields that would mean the note carries content or an excerpt of it. The
#: gate's own test forbids them at the source; this refuses them at the sink,
#: because a map that drew from a leaking feed would put the leak on a page.
#: (`identity` — the org's signer label — is a legitimate field the map does
#: not read; it is neither forbidden nor rendered.)
FEED_FORBIDDEN = {"content", "blob", "text", "body", "excerpt", "snippet", "title", "envelope",
                  "source", "source_uri", "summary_text"}


def read_feed(path: Path) -> tuple[list[dict], list[str]]:
    """Parse a jsonl feed into categories (one per space) with one point per
    live claim. Returns (categories, errors)."""
    errors: list[str] = []
    live: dict[str, dict] = {}            # artifact_id → {k, space, trust}
    relations: list[tuple[str, str]] = []  # (parent, child) — resolved after the whole file is read
    seen_ids: set[str] = set()
    for ln, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        try:
            note = json.loads(raw)
        except json.JSONDecodeError as e:
            errors.append(f"{path.name}:{ln}: not JSON ({e.msg})"); continue
        if note.get("id") in seen_ids:
            continue                      # at-least-once delivery: a redelivered note is the same note
        seen_ids.add(note.get("id"))
        data = note.get("data") or {}
        leaked = set(data) & FEED_FORBIDDEN
        if leaked:
            errors.append(f"{path.name}:{ln}: note carries {sorted(leaked)} — the feed is labels only; refusing the file")
            continue
        action = FEED_TYPES.get(str(note.get("type", "")))
        if action is None:
            continue                      # scans, signs, expiries: not on the map
        aid = str(note.get("subject") or data.get("artifact_id") or "")
        if not aid:
            errors.append(f"{path.name}:{ln}: note without a subject"); continue
        if action == "drop":
            live.pop(aid, None); continue
        if action == "edge":
            # a relation note's subject is the parent; `related_to` is the child.
            # Resolved once the file is read, because the child's own note may
            # come later in the same feed.
            child = data.get("related_to")
            if isinstance(child, str) and child:
                relations.append((aid, child))
            continue
        space = str(data.get("space") or "main")
        live[aid] = {"k": FEED_KINDS.get(str(data.get("content_type", "")), "f"),
                     "space": space,
                     "trust": FEED_TRUST.get(str(data.get("trust_class", "")), "authority not stated")}
    # an edge between two spaces, per relation whose both ends are live
    edges: dict[tuple[str, str], int] = {}
    for parent, child in relations:
        a, b = live.get(parent), live.get(child)
        if a and b and a["space"] != b["space"]:
            key = tuple(sorted((a["space"], b["space"])))
            edges[key] = edges.get(key, 0) + 1
    by_space: dict[str, list[dict]] = {}
    for aid, row in live.items():
        by_space.setdefault(row["space"], []).append(row)
    # related: the spaces this one shares a relation edge with, most edges first;
    # a space with no edges relates to the largest other space so it is not an island
    cats: list[dict] = []
    for space in sorted(by_space, key=lambda s: (-len(by_space[s]), s)):
        rel = sorted(((n, other) for (a, b), n in edges.items() for other in (a, b)
                      if space in (a, b) and other != space), reverse=True)
        related = [o for _, o in rel]
        if not related and len(by_space) > 1:
            related = [next(s for s in sorted(by_space, key=lambda s: (-len(by_space[s]), s)) if s != space)]
        claims = [{"k": r["k"], "t": r["trust"], "line": i + 1} for i, r in enumerate(by_space[space])]
        cats.append({"id": _slug(space), "name": space, "related": [_slug(r) for r in related], "claims": claims})
    return cats, errors


def _slug(space: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", space.lower()).strip("-")
    return s if s and s[0].isalpha() else f"s-{s or 'x'}"


def validate_feed(cats: list[dict]) -> list[str]:
    """The authored gates that apply to a map with no prose: ids are slugs, no
    islands, related ids exist, and every label the map will show passes the
    vocabulary and phase gates. Counts are whatever the organization has."""
    errors: list[str] = []
    ids = [c["id"] for c in cats]
    if not cats:
        errors.append("the feed holds no live claim — nothing to draw")
    if len(set(ids)) != len(ids):
        errors.append(f"duplicate category ids: {sorted({i for i in ids if ids.count(i) > 1})}")
    for c in cats:
        for r in c["related"]:
            if r not in ids:
                errors.append(f"{c['id']}: related id {r!r} is not a category")
        if len(cats) > 1 and not c["related"]:
            errors.append(f"{c['id']}: no related categories — an island cannot link")
        for text in [c["name"]] + [cl["t"] for cl in c["claims"]]:
            for label, pat in LEAKS.items():
                if re.search(pat, text, re.I):
                    errors.append(f"{c['id']}: {label} leak in a label -> {text[:60]!r}")
            if PHASE_LANGUAGE.search(text):
                errors.append(f"{c['id']}: phase language in a label -> {text[:60]!r}")
    return errors


def main() -> int:
    argv = sys.argv[1:]
    if "--feed" in argv:
        feed = Path(argv[argv.index("--feed") + 1])
        out = Path(argv[argv.index("--out") + 1]) if "--out" in argv else OUT
        cats, errors = read_feed(feed)
        errors += validate_feed(cats)
        if errors:
            print(f"{feed.name}: {len(errors)} problem(s)")
            for e in errors[:60]:
                print("  ·", e)
            return 1
        n = sum(len(c["claims"]) for c in cats)
        want = render(cats, source=feed.name, note="feed")
        if "--check" in argv:
            if not out.exists() or out.read_text(encoding="utf-8") != want:
                print(f"STALE: {out.name} — run python3 sky-data.py --feed {feed}")
                return 1
            print(f"{out.name} up to date ({len(cats)} spaces, {n} claims)")
            return 0
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(want, encoding="utf-8")
        print(f"wrote {out}: {len(cats)} spaces, {n} live claims, {len(want):,} bytes")
        return 0
    cats = parse(SRC.read_text(encoding="utf-8"))
    errors = validate(cats)
    if errors:
        print(f"sky-claims.txt: {len(errors)} problem(s)")
        for e in errors[:60]:
            print("  ·", e)
        return 1
    want = render(cats)
    if "--check" in sys.argv:
        if not OUT.exists() or OUT.read_text(encoding="utf-8") != want:
            print("STALE: assets/sky-data.js — run python3 sky-data.py")
            return 1
        print(f"sky-data.js up to date ({len(cats)} × {PER_CATEGORY})")
        return 0
    OUT.write_text(want, encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}: {len(cats)} categories, "
          f"{sum(len(c['claims']) for c in cats)} claims, {len(want):,} bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
