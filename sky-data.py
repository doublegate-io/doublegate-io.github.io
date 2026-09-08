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


def render(cats: list[dict]) -> str:
    data = {
        "kinds": KINDS,
        "categories": [
            {"id": c["id"], "name": c["name"], "related": c["related"],
             "claims": [[cl["k"], cl["t"]] for cl in c["claims"]]}
            for c in cats
        ],
    }
    body = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    n = sum(len(c["claims"]) for c in cats)
    return (
        "// GENERATED by sky-data.py from sky-claims.txt — edit the .txt, not this.\n"
        f"// {len(cats)} categories × {PER_CATEGORY} claims = {n}.\n"
        f"window.SKY_DATA = {body};\n"
    )


def main() -> int:
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
