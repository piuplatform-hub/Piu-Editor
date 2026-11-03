"""Restore optional reference source at pinned commits; never overwrite source.

Python 3.10+ and Git only. No dependencies, builds, submodules or LFS downloads.
Git metadata, staging directories and receipts stay in ignored .workspace/.
"""
import argparse
import datetime as dt
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import uuid

ROOT = Path(__file__).resolve().parents[1]


def inside(path):
    path = Path(path)
    if path.is_symlink() or not path.resolve().is_relative_to(ROOT.resolve()):
        raise ValueError(f"Unsafe workspace path: {path}")
    return path


def load_entries():
    manifest = json.loads((ROOT / "repo-manifest.json").read_text(encoding="utf-8-sig"))
    tools = json.loads((ROOT / "configs/tools.json").read_text(encoding="utf-8-sig"))["tools"]
    rows = manifest["repos"]
    folders = {row["folder"] for row in rows}
    if len(folders) != len(rows) or folders != {t["folder"] for t in tools}:
        raise ValueError("Registry and manifest folders differ or contain duplicates")
    by_folder = {t["folder"]: t for t in tools}
    for row in rows:
        tool = by_folder[row["folder"]]
        if not re.fullmatch(r"[0-9]{2}-[a-z0-9-]+", row["folder"]):
            raise ValueError("Invalid tool folder")
        if not re.fullmatch(r"[0-9a-f]{40}", row["commit"]):
            raise ValueError(f"Expected full commit SHA: {row['folder']}")
        if not re.fullmatch(r"https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", row["url"]):
            raise ValueError(f"Expected a GitHub HTTPS source URL: {row['folder']}")
        if row["url"] != tool["upstream"]:
            raise ValueError(f"Registry and manifest URL differ: {row['folder']}")
        for name in tool["readFirst"]:
            if Path(name).is_absolute() or ".." in Path(name).parts or "\\" in name:
                raise ValueError(f"Unsafe readFirst path: {name}")
        yield dict(row, id=tool["id"], readFirst=tool["readFirst"])


def git(*args, cwd=None):
    env = os.environ.copy()
    env["GIT_TERMINAL_PROMPT"] = "0"
    env["GIT_LFS_SKIP_SMUDGE"] = "1"
    for key in ["GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE"]:
        env.pop(key, None)
    result = subprocess.run(
        ["git", "-c", "core.longpaths=true", "-c", "core.symlinks=false",
         "-c", "filter.lfs.smudge=", "-c", "filter.lfs.required=false", *args],
        cwd=cwd, env=env, capture_output=True, text=True, encoding="utf-8",
        errors="replace", timeout=900,
    )
    if result.returncode:
        raise RuntimeError(result.stderr.strip()[-1800:] or f"Git failed: {args[0]}")
    return result.stdout.strip()


def has_source(dest):
    return dest.exists() and any(p.name not in {"AGENTS.md", ".gitkeep"} for p in dest.iterdir())


def restore(row):
    dest = inside(ROOT / "repos" / row["folder"])
    guide = dest / "AGENTS.md"
    if not guide.is_file() or guide.is_symlink():
        raise ValueError(f"Missing local guide: {guide}")
    if has_source(dest):
        print(f"SKIP {row['folder']}: existing source preserved; not reverified or updated", flush=True)
        return "skipped"

    stage_base = inside(ROOT / ".workspace" / "bootstrap")
    stage_base.mkdir(parents=True, exist_ok=True)
    stage = inside(stage_base / f"{row['folder']}-{uuid.uuid4().hex}")
    stage.mkdir()
    checkout = stage / "source"
    checkout.mkdir()
    print(f"FETCH {row['folder']} @ {row['commit'][:12]}", flush=True)
    git("init", str(checkout))
    git("fetch", "--no-tags", "--depth=1", row["url"] + ".git", row["commit"], cwd=checkout)
    git("checkout", "--detach", "FETCH_HEAD", cwd=checkout)
    actual = git("rev-parse", "HEAD", cwd=checkout)
    if actual != row["commit"]:
        raise ValueError(f"Commit mismatch: {row['folder']}")
    for name in row["readFirst"]:
        target = inside(checkout / name)
        if not target.is_file():
            raise ValueError(f"Missing downloaded entrypoint: {name}")

    upstream_guide = checkout / "AGENTS.md"
    if upstream_guide.is_symlink():
        raise ValueError("Refusing to replace an upstream AGENTS symlink")
    if upstream_guide.is_file():
        shutil.copy2(upstream_guide, stage / "AGENTS.upstream.md")
    upstream_guide.write_bytes(guide.read_bytes())
    if (dest / ".gitkeep").is_file():
        (checkout / ".gitkeep").write_bytes((dest / ".gitkeep").read_bytes())

    archives = inside(ROOT / ".workspace" / "upstream-git")
    archives.mkdir(parents=True, exist_ok=True)
    archive = inside(archives / f"{row['folder']}-{row['commit'][:12]}-{uuid.uuid4().hex[:8]}.git")
    inside(checkout / ".git").rename(archive)
    if has_source(dest):
        raise ValueError(f"Source appeared during fetch; preserved: {dest}")
    backup = inside(stage / "guides-before")
    dest.rename(backup)
    try:
        checkout.rename(dest)
    except OSError:
        backup.rename(dest)
        raise
    receipt = {
        "folder": row["folder"], "url": row["url"], "commit": actual,
        "restoredAt": dt.datetime.now(dt.timezone.utc).isoformat(),
        "gitMetadata": archive.relative_to(ROOT).as_posix(),
        "submodulesFetched": False, "lfsFetched": False,
    }
    (stage / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(f"OK {row['folder']}: pinned commit verified; local guide retained", flush=True)
    return "restored"


def main(argv=None):
    parser = argparse.ArgumentParser(description="Restore reference repos from pinned commits; preserve existing source.")
    parser.add_argument("--tool", action="append", default=[], help="Tool ID or folder; repeat to select several (default: all)")
    parser.add_argument("--list", action="store_true", help="List planned repos without downloading")
    args = parser.parse_args(argv)
    try:
        entries = list(load_entries())
        names = {r[key] for r in entries for key in ("id", "folder")}
        if set(args.tool) - names:
            raise ValueError(f"Unknown tools: {', '.join(sorted(set(args.tool) - names))}")
        selected = [r for r in entries if not args.tool or {r["id"], r["folder"]}.intersection(args.tool)]
        if args.list:
            for row in selected:
                print(f"{row['id']}: {row['url']} @ {row['commit']}")
            return 0
        if not shutil.which("git"):
            raise ValueError("Git is required in PATH")
        failed = 0
        for row in selected:
            try:
                restore(row)
            except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as error:
                print(f"ERROR {row['folder']}: {error}", file=sys.stderr, flush=True)
                failed += 1
        print(f"Checked {len(selected)} repos; {failed} failed. No packages installed; no manifest updated.")
        return 1 if failed else 0
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
