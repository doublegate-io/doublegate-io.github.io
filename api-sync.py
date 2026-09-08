#!/usr/bin/env python3
"""api-sync.py — the site's copy of the gate's machine-readable API (ADR-0044).

The code repositories render their surfaces to `docs/api/` from the tables the
daemons dispatch from, and their CI refuses drift. While those repositories
are private, this site is the only place an agent can scan — so the rendered
documents are published here, under `api/`, as a *snapshot* stamped with the
commit each came from. Nothing under `api/` is written by hand.

    python3 api-sync.py            # copy from ../doublegate and ../doublegate-org, stamp api/index.json
    python3 api-sync.py --check    # with the checkouts present: fail if the snapshot is behind them
                                   # without them (CI): fail only if the snapshot is malformed

Override the checkout locations with DOUBLEGATE_SRC / DOUBLEGATE_ORG_SRC.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
API = ROOT / "api"

# (site file, source repo, file inside that repo's docs/api/, one line for the manifest)
DOCUMENTS = [
    ("mcp-tools.json", "doublegate", "mcp-tools.json",
     "the tool schemas each tier serves over the agent-tool protocol — what tools/list answers — and the instructions paragraph the handshake carries"),
    ("daemon-rpc.json", "doublegate", "daemon-rpc.json",
     "every verb on the gate's local socket: parameters, role, the proof each needs; a running gate answers the same to dg.describe"),
    ("note.schema.json", "doublegate", "note.schema.json",
     "JSON Schema of a published note's data — the closed field set a subscriber or a knowledge map may rely on"),
    ("openapi.json", "doublegate-org", "openapi.json",
     "OpenAPI 3.1 for the organization gate's keyed HTTP surface; a running gate serves it at GET /openapi.json to any valid key"),
]

SOURCES = {
    "doublegate": Path(os.environ.get("DOUBLEGATE_SRC", ROOT.parent / "doublegate")),
    "doublegate-org": Path(os.environ.get("DOUBLEGATE_ORG_SRC", ROOT.parent / "doublegate-org")),
}


def head(repo: Path) -> str:
    return subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()


def sources_present() -> bool:
    return all((p / "docs" / "api").is_dir() for p in SOURCES.values())


def manifest(stamps: dict[str, str]) -> dict:
    return {
        "what": "doublegate's API as data — rendered from the code that serves it, checked against it in the code repositories' CI, published here as a snapshot",
        "rendered_from": {name: {"repository": f"https://github.com/doublegate-io/{name}", "commit": sha} for name, sha in stamps.items()},
        "documents": {site: {"from": f"{repo}/docs/api/{src}", "about": about} for site, repo, src, about in DOCUMENTS},
        "read_first": "https://doublegate-io.github.io/llms.txt",
    }


def render() -> dict[str, str]:
    """site path → content, from the checkouts. Deterministic: the manifest carries commits, not dates."""
    stamps = {name: head(path) for name, path in SOURCES.items()}
    out = {}
    for site, repo, src, _ in DOCUMENTS:
        text = (SOURCES[repo] / "docs" / "api" / src).read_text(encoding="utf-8")
        json.loads(text)                                   # the source must be JSON before it is copied
        out[site] = text
    out["index.json"] = json.dumps(manifest(stamps), indent=2, ensure_ascii=False) + "\n"
    return out


def check_shape() -> list[str]:
    """What CI can verify without the private checkouts: every document parses,
    the manifest names every file and only files that exist, and each commit is a sha."""
    bad = []
    if not (API / "index.json").exists():
        return ["api/index.json missing — run python3 api-sync.py"]
    try:
        idx = json.loads((API / "index.json").read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return [f"api/index.json is not JSON: {e}"]
    listed = set(idx.get("documents", {}))
    on_disk = {p.name for p in API.glob("*.json")} - {"index.json"}
    for name in sorted(listed - on_disk):
        bad.append(f"api/index.json names {name}, which is not in api/")
    for name in sorted(on_disk - listed):
        bad.append(f"api/{name} is not named in api/index.json")
    for name in sorted(on_disk):
        try:
            json.loads((API / name).read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            bad.append(f"api/{name} is not JSON: {e}")
    for repo, rec in idx.get("rendered_from", {}).items():
        sha = rec.get("commit", "")
        if len(sha) != 40 or any(c not in "0123456789abcdef" for c in sha):
            bad.append(f"api/index.json: {repo} commit is not a full sha: {sha!r}")
    return bad


def main(argv: list[str]) -> int:
    check = "--check" in argv
    bad = check_shape() if API.exists() else ["api/ missing — run python3 api-sync.py"]
    if check and not sources_present():
        for line in bad:
            print("api-sync:", line)
        print("api-sync: shape OK (source checkouts absent; drift is checked where they are present)" if not bad else "api-sync: FAIL")
        return 1 if bad else 0
    if not sources_present():
        missing = [f"{n}: {p}" for n, p in SOURCES.items() if not (p / "docs" / "api").is_dir()]
        print("api-sync: no docs/api in " + "; ".join(missing), file=sys.stderr)
        return 2
    want = render()
    if check:
        stale = [n for n, text in want.items() if not (API / n).exists() or (API / n).read_text(encoding="utf-8") != text]
        bad += [f"api/{n} is behind the checkout — run python3 api-sync.py" for n in stale]
        for line in bad:
            print("api-sync:", line)
        print("api-sync: FAIL" if bad else f"api-sync: OK — {len(want)} files equal the checkouts")
        return 1 if bad else 0
    API.mkdir(exist_ok=True)
    for n, text in want.items():
        (API / n).write_text(text, encoding="utf-8")
    stamps = json.loads(want["index.json"])["rendered_from"]
    print("api-sync: wrote " + ", ".join(sorted(want)) + " from " + ", ".join(f"{k}@{v['commit'][:7]}" for k, v in stamps.items()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
