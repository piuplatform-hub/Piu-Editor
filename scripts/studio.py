"""Piu Editor workspace utilities (Python 3.10+, standard library only).

Manage projects and inputs; this is not a renderer. Paths in project JSON are
workspace-relative. Original media is never modified by these commands.
"""
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
INPUT_ROOTS = ["Source"]
INPUT_DIRS = ["Source", "Source/inbox", "Source/footage", "Source/images",
              "Source/music", "Source/audio", "Source/assets", "Source/documents"]
SHARED_GUIDES = ["Source/AGENTS.md", "projects/AGENTS.md"]
STATES = {"intake", "planning", "building", "preview", "rendering", "qa", "complete"}
ENGINES = {None, "ffmpeg", "remotion", "motion-canvas", "custom"}


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path, value):
    # Replace a temporary file in the same directory, avoiding partial JSON.
    temp = path.with_name(path.name + ".tmp")
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp.replace(path)


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def inside(path):
    resolved = path.resolve()
    if not resolved.is_relative_to(ROOT):
        raise ValueError(f"Path leaves workspace: {path}")
    return resolved


def relative_path(value):
    if not isinstance(value, str) or not value or Path(value).is_absolute() or "\\" in value:
        raise ValueError(f"Expected workspace-relative path using /: {value!r}")
    # Also reject Windows drive paths when running this utility on Unix.
    if re.match(r"^[A-Za-z]:", value) or ".." in Path(value).parts:
        raise ValueError(f"Invalid relative path: {value!r}")
    return inside(ROOT / value)


def project_path(project_id):
    reserved = {"con", "prn", "aux", "nul", *(f"com{i}" for i in range(1, 10)), *(f"lpt{i}" for i in range(1, 10))}
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,63}", project_id) or project_id in reserved:
        raise ValueError("Project ID: 1–64 ký tự a-z, 0-9, dấu -, không dùng tên hệ thống Windows.")
    return inside(ROOT / "projects" / project_id)


def load_project(project_id):
    path = project_path(project_id)
    data = read_json(path / "project.json")
    if data.get("id") != project_id:
        raise ValueError("Project ID does not match its folder")
    return path, data


def create_project(args):
    project = project_path(args.project_id)
    output = inside(ROOT / "output" / args.project_id)
    if project.exists() or output.exists():
        raise ValueError("Project/output đã tồn tại; chọn ID mới hoặc tiếp tục dự án cũ.")
    # Parse JSON as data before substituting strings, so quotes in titles are safe.
    created = now()
    values = {"{{PROJECT_ID}}": args.project_id, "{{TITLE}}": args.title or args.project_id,
              "{{CREATED_AT}}": created}

    def replace(value):
        if isinstance(value, str):
            for old, new in values.items():
                value = value.replace(old, new)
            return value
        if isinstance(value, list):
            return [replace(x) for x in value]
        if isinstance(value, dict):
            return {k: replace(v) for k, v in value.items()}
        return value

    template = ROOT / "templates/project"
    project.mkdir(parents=True)
    for source in sorted(template.rglob("*")):
        if not source.is_file():
            continue
        target = project / source.relative_to(template)
        target.parent.mkdir(parents=True, exist_ok=True)
        if source.suffix == ".json":
            write_json(target, replace(read_json(source)))
        else:
            target.write_text(replace(source.read_text(encoding="utf-8")), encoding="utf-8")
    for name in ["src", "working", "previews", "notes"]:
        (project / name).mkdir(exist_ok=True)
        (project / name / ".gitkeep").touch(exist_ok=True)
    (project / "public").mkdir(exist_ok=True)
    (project / "public/.gitkeep").touch(exist_ok=True)
    output.mkdir(parents=True)
    (output / ".gitkeep").touch(exist_ok=True)
    write_json(project / "assets.json", {"schemaVersion": 1, "projectId": args.project_id,
               "generatedAt": None, "sourceRoots": INPUT_ROOTS, "assets": []})
    print(f"Created projects/{args.project_id}/; output/{args.project_id}/")
    print("Khung dự án đã tạo; chưa cài renderer hoặc xuất video.")


def media_type(path):
    ext = path.suffix.lower()
    kinds = {
        "video": {".mp4", ".mov", ".mkv", ".webm", ".avi", ".m4v", ".mxf", ".mts", ".m2ts"},
        "image": {".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg", ".avif", ".heic", ".tif", ".tiff", ".bmp"},
        "audio": {".wav", ".mp3", ".aac", ".m4a", ".flac", ".ogg", ".opus", ".aiff"},
        "font": {".ttf", ".otf", ".woff", ".woff2"},
        "model": {".glb", ".gltf", ".obj", ".fbx", ".blend", ".stl", ".usd", ".usdz"},
        "animation": {".lottie"},
        "text": {".txt", ".md", ".srt", ".vtt", ".ass", ".csv", ".tsv"},
        "data": {".json", ".yaml", ".yml"},
    }
    return next((kind for kind, exts in kinds.items() if ext in exts), "other")


def hash_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def input_files(roots):
    seen = set()
    for name in roots:
        base = relative_path(name)
        if not base.is_dir() or (ROOT / name).is_symlink():
            continue
        for directory, dirs, names in os.walk(base, followlinks=False):
            dirs[:] = sorted(d for d in dirs if not d.startswith(".") and not (Path(directory) / d).is_symlink())
            for name in sorted(names):
                path = Path(directory) / name
                if name in {"AGENTS.md", ".gitkeep"} or path.is_symlink() or name.startswith("."):
                    continue
                path = inside(path)
                key = path.relative_to(ROOT).as_posix()
                if path.is_file() and key not in seen:
                    seen.add(key)
                    yield path, key


def inventory(args):
    project, data = load_project(args.project_id)
    roots = data.get("sourceRoots", INPUT_ROOTS)
    if not isinstance(roots, list) or not all(isinstance(x, str) for x in roots):
        raise ValueError("sourceRoots must be a list of workspace-relative directories")
    # Keep inventory in user input areas, excluding code, output and archives.
    for name in roots:
        relative_path(name)
        if Path(name).parts[0] not in INPUT_ROOTS:
            raise ValueError(f"sourceRoots must be Source/ or its subdirectories: {name}")
    manifest_path = project / "assets.json"
    old = read_json(manifest_path) if manifest_path.exists() else {"assets": []}
    previous = {row["path"]: row for row in old["assets"]}
    assets = []
    for path, key in input_files(roots):
        stat = path.stat()
        row = dict(previous.pop(key, {}))
        same = row.get("sizeBytes") == stat.st_size and row.get("mtimeNs") == stat.st_mtime_ns
        prior = bool(row)
        row.setdefault("selected", False)
        row.setdefault("role", "")
        row.setdefault("notes", "")
        row.update(path=key, mediaType=media_type(path), sizeBytes=stat.st_size,
                   mtimeNs=stat.st_mtime_ns, exists=True)
        if args.hash:
            new_hash = hash_file(path)
            changed = prior and (row["sha256"] != new_hash if row.get("sha256") is not None else not same)
            row["sha256"] = new_hash
        else:
            changed = prior and not same
            if not same:
                row["sha256"] = None
        row["changedSinceSelection"] = bool(row.get("changedSinceSelection", False) or (changed and row["selected"]))
        assets.append(row)
    for row in previous.values():
        row = dict(row)
        row["exists"] = False
        assets.append(row)
    result = dict(schemaVersion=1, projectId=args.project_id, generatedAt=now(),
                  sourceRoots=roots, assets=sorted(assets, key=lambda x: x["path"]))
    write_json(manifest_path, result)
    print(f"Inventory: {sum(r['exists'] for r in assets)} file hiện có, {sum(not r['exists'] for r in assets)} file mất/ngoài lần quét; originals unchanged.")
    print(f"Saved projects/{args.project_id}/assets.json; AI cần xem nội dung và chọn selected=true.")


def doctor(_args):
    print("Piu Editor: inventory/scaffold utilities; không phải renderer đã cài sẵn.")
    for name, flag in [("python", "--version"), ("git", "--version"), ("ffmpeg", "-version"),
                       ("ffprobe", "-version"), ("node", "--version"), ("npm", "--version"), ("bun", "--version")]:
        executable = shutil.which(name)
        if not executable:
            print(f"{name}: chưa thấy trong PATH")
            continue
        try:
            result = subprocess.run([executable, flag], capture_output=True, text=True,
                                    errors="replace", timeout=15)
            line = (result.stdout or result.stderr).splitlines()
            label = line[0] if line else f"exit={result.returncode}"
            print(f"{name}: {label} [{executable}]")
        except (OSError, subprocess.TimeoutExpired) as error:
            print(f"{name}: tìm thấy nhưng chưa xác nhận chạy được: {error}")
    print("FFmpeg/ffprobe cho cắt ghép; Node/package manager cho app JS. Bun chỉ cần khi dự án chọn dùng.")


def validate(args):
    errors, warnings = [], []
    check_sources = getattr(args, "sources", False)
    check_local = getattr(args, "local", False)
    catalog = read_json(ROOT / "configs/tools.json")
    tools = catalog["tools"]
    ids = {t["id"] for t in tools}
    if len(ids) != len(tools) or len({t['folder'] for t in tools}) != len(tools):
        errors.append("Duplicate tool ID/folder")
    required = ["AGENTS.md", "README.md", "docs/REPO-MAP.md", "docs/WORKFLOW.md", "docs/EXTENDING.md", "docs/GIT.md", "CONTRIBUTING.md", "docs/production/README.md",
                "templates/project/project.json", "templates/project/brief.md", "templates/project/STATUS.md", "repo-manifest.json",
                "configs/upstream-submodules.json", "scripts/bootstrap_repos.py", "scripts/check_publish.py"]
    required += SHARED_GUIDES
    for folder in INPUT_DIRS + ["projects", "output", "temp", "repos", "templates", "scripts"]:
        if not relative_path(folder).is_dir():
            errors.append(f"Missing workspace directory: {folder}")
    for tool in tools:
        path = f"repos/{tool['folder']}"
        required.append(f"{path}/AGENTS.md")
        if check_sources:
            required.extend(f"{path}/{entry}" for entry in tool["readFirst"])
        if (ROOT / path / ".git").exists():
            errors.append(f"Nested Git repository: {path}")
        for related in tool["related"]:
            if related not in ids:
                errors.append(f"Unknown related tool {related}")
        if tool.get("upstreamGuide"):
            required.append(tool["upstreamGuide"])
    for path in required:
        if not relative_path(path).is_file():
            errors.append(f"Missing required file: {path}")
    if not (ROOT / ".git").exists():
        errors.append("Missing root Git repository")
    from bootstrap_repos import load_entries
    # Share manifest validation with the downloader, including URLs and full SHAs.
    try:
        list(load_entries())
    except (OSError, ValueError, KeyError, TypeError) as error:
        errors.append(f"Invalid pinned sources: {error}")

    # Only scan workspace-authored guides/docs, not thousands of upstream links.
    docs = [ROOT / "AGENTS.md", ROOT / "README.md"]
    docs += [p for p in (ROOT / "docs").glob("*.md")]
    docs += sorted((ROOT / "docs/production").rglob("*.md"))
    docs += [ROOT / f"repos/{t['folder']}/AGENTS.md" for t in tools]
    docs += [ROOT / name for name in SHARED_GUIDES]
    for doc in docs:
        if not doc.exists():
            continue
        content = doc.read_text(encoding="utf-8")
        for target in re.findall(r"\]\(([^)]+)\)", content):
            if target.startswith(("http:", "https:", "#", "mailto:")) or "{{" in target:
                continue
            linked = inside(doc.parent / target.split("#", 1)[0])
            relative = linked.relative_to(ROOT).parts
            optional_source = (len(relative) > 2 and relative[0] == "repos"
                               and relative[1] in {t["folder"] for t in tools}
                               and relative[2:] != ("AGENTS.md",))
            if optional_source and not check_sources:
                continue
            if not linked.exists():
                errors.append(f"Broken link: {doc.relative_to(ROOT)} -> {target}")

    project_count = 0
    for project in sorted((ROOT / "projects").iterdir()):
        if not project.is_dir() or project.name.startswith("."):
            continue
        if project.is_symlink():
            warnings.append(f"Skipped symlink project: {project.name}")
            continue
        try:
            _, data = load_project(project.name)
            project_count += 1
            if data.get("schemaVersion") != 1 or data.get("status") not in STATES or data.get("engine") not in ENGINES:
                errors.append(f"Invalid schema/status/engine: {project.name}")
            if not set(data.get("selectedTools", [])).issubset(ids):
                errors.append(f"Unknown selectedTools: {project.name}")
            for name in data.get("sourceRoots", INPUT_ROOTS):
                relative_path(name)
                if Path(name).parts[0] not in INPUT_ROOTS:
                    errors.append(f"sourceRoots must be below Source/: {project.name}: {name}")
            preset = data["preset"]
            if any(not isinstance(preset[k], (int, float)) or isinstance(preset[k], bool) or preset[k] <= 0 for k in ["width", "height", "fps"]):
                errors.append(f"Invalid output dimensions/FPS: {project.name}")
            if preset.get("durationSeconds") is not None and preset["durationSeconds"] <= 0:
                errors.append(f"Invalid durationSeconds: {project.name}")
            for key in ["brief", "assetManifest"]:
                if not relative_path(data[key]).is_file():
                    errors.append(f"Missing {key}: {project.name}")
            for path in data["paths"].values():
                if not relative_path(path).is_dir():
                    errors.append(f"Missing project directory {path}")
            assets = read_json(relative_path(data["assetManifest"]))
            if assets.get("projectId") != project.name:
                errors.append(f"Asset manifest project mismatch: {project.name}")
            for row in assets["assets"]:
                relative_path(row["path"])
                if check_local and row.get("selected") and (row.get("exists") is False or not relative_path(row["path"]).is_file()):
                    errors.append(f"Selected input missing: {row['path']}")
                if row.get("selected") and row.get("changedSinceSelection"):
                    warnings.append(f"Selected input changed; inspect before reuse: {row['path']}")
            for entry in data.get("deliverables", []):
                deliverable = relative_path(entry)
                if check_local and not deliverable.is_file():
                    errors.append(f"Missing deliverable: {entry}")
            if data["status"] == "complete" and (not data.get("deliverables") or data.get("engine") is None):
                errors.append(f"Complete project has no engine/deliverables: {project.name}")
        except (ValueError, OSError, KeyError, TypeError) as error:
            errors.append(f"Invalid project {project.name}: {error}")
    for warning in warnings:
        print(f"WARN: {warning}")
    for error in errors:
        print(f"ERROR: {error}")
    print(f"Validated {len(tools)} tools, {project_count} projects: {len(errors)} errors, {len(warnings)} warnings.")
    print(f"Scope: repository structure; downloaded source={'checked' if check_sources else 'not checked'}; local inputs/output={'checked' if check_local else 'not checked'}.")
    return 1 if errors else 0


def main():
    parser = argparse.ArgumentParser(description="Piu Editor: quản lý hồ sơ và nguyên liệu, không phải renderer.")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("doctor", help="Kiểm tra công cụ, không cài đặt").set_defaults(func=doctor)
    val = sub.add_parser("validate", help="Kiểm tra bản đồ/thư mục/project; mặc định không cần media/source đã tải")
    val.add_argument("--sources", action="store_true", help="Yêu cầu đủ file đọc đầu tiên của 18 source tham khảo")
    val.add_argument("--local", action="store_true", help="Yêu cầu nguyên liệu đã chọn và output lịch sử hiện diện trên máy")
    val.set_defaults(func=validate)
    new = sub.add_parser("new", help="Tạo khung project")
    new.add_argument("project_id")
    new.add_argument("--title")
    new.set_defaults(func=create_project)
    inv = sub.add_parser("inventory", help="Liệt kê nguyên liệu, không sửa originals")
    inv.add_argument("--project", dest="project_id", required=True)
    inv.add_argument("--hash", action="store_true", help="Tính SHA256 toàn bộ file; có thể lâu với footage lớn")
    inv.set_defaults(func=inventory)
    args = parser.parse_args()
    try:
        return args.func(args) or 0
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
