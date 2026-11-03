"""Audit the actual Git index before commit/push. Never print file contents."""
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
ROOT_FILES = {".gitignore", ".gitattributes", "AGENTS.md", "README.md", "CONTRIBUTING.md",
              "CHANGELOG.md", "DANH-GIA-18-REPO.md", "download_repos.py",
              "repo-manifest.json", "review-evidence.json"}
CODE = {".py", ".cjs", ".mjs", ".js", ".jsx", ".ts", ".tsx", ".css", ".json", ".md"}
SECRET = re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|"
                    rb"(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{50,}|sk-proj-[A-Za-z0-9_-]{40,})")


def allowed(name):
    path = PurePosixPath(name)
    parts = path.parts
    if not parts or ".." in parts:
        return False
    if len(parts) == 1:
        return name in ROOT_FILES
    top = parts[0]
    if top == "repos":
        return len(parts) == 3 and parts[2] == "AGENTS.md"
    if top == "Source":
        return name == "Source/AGENTS.md" or path.name == ".gitkeep"
    if top in {"output", "temp"}:
        return path.name == ".gitkeep"
    if top == "configs":
        return name in {"configs/tools.json", "configs/upstream-submodules.json"}
    if top in {"scripts", "tests"}:
        return path.suffix == ".py" and "__pycache__" not in parts
    if top == ".github":
        return len(parts) == 3 and parts[1] == "workflows" and path.suffix == ".yml"
    if top == "docs":
        return path.suffix in {".md", ".json"}
    if top == "templates":
        return path.name == ".gitkeep" or path.suffix in {".md", ".json"}
    if top == "projects":
        if name in {"projects/AGENTS.md", "projects/.gitkeep"}:
            return True
        if len(parts) < 3:
            return False
        if len(parts) > 3 and parts[2] in {"public", "working", "previews"}:
            return path.name == ".gitkeep"
        if "node_modules" in parts or parts[2] in {"dist", "out"}:
            return False
        return path.name in {".gitkeep", ".gitignore"} or path.suffix in CODE
    return False


def problems(name, mode, content):
    issues = []
    if not allowed(name):
        issues.append("outside publish scope (media, upstream source or local state)")
    if mode not in {"100644", "100755"}:
        issues.append("symlink/submodule/non-file is not publishable")
    if len(content) > 2 * 1024 * 1024:
        issues.append("file exceeds 2 MiB source/document limit")
    if PurePosixPath(name).name == ".gitkeep" and content:
        issues.append("placeholder must be empty")
    try:
        content.decode("utf-8-sig")
        if b"\0" in content:
            issues.append("binary content")
    except UnicodeDecodeError:
        issues.append("non-UTF-8/binary content")
    if SECRET.search(content):
        issues.append("possible credential/private key")
    return issues


def audit():
    result = subprocess.run(["git", "ls-files", "--stage", "-z"], cwd=ROOT,
                            capture_output=True, check=True)
    entries = []
    for entry in result.stdout.split(b"\0"):
        if not entry:
            continue
        metadata, name = entry.split(b"\t", 1)
        mode, oid, stage = metadata.decode("ascii").split()
        if stage != "0":
            raise ValueError("Unresolved Git index conflict")
        entries.append((name.decode("utf-8"), mode, oid))
    if not entries:
        raise ValueError("Git index is empty; stage the intended files first")
    batch = subprocess.run(["git", "cat-file", "--batch"], cwd=ROOT,
                           input="".join(oid + "\n" for _, _, oid in entries).encode("ascii"),
                           capture_output=True, check=True).stdout
    offset, total, failures = 0, 0, 0
    for name, mode, oid in entries:
        end = batch.index(b"\n", offset)
        header = batch[offset:end].decode("ascii").split()
        if len(header) != 3 or header[0] != oid or header[1] != "blob":
            raise ValueError(f"Not a regular Git blob: {name}")
        size = int(header[2])
        content = batch[end + 1:end + 1 + size]
        offset = end + 1 + size + 1
        total += size
        for issue in problems(name, mode, content):
            print(f"ERROR: {name}: {issue}")
            failures += 1
    print(f"Publish audit: {len(entries)} files, {total / 1048576:.3f} MiB uncompressed, {failures} issues.")
    return 1 if failures else 0


if __name__ == "__main__":
    try:
        raise SystemExit(audit())
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1)
