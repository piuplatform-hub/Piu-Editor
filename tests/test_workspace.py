"""Offline fixtures exercise pinned restore, clean clones and publish boundaries."""
import argparse
import contextlib
import importlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
bootstrap = importlib.import_module("bootstrap_repos")
studio = importlib.import_module("studio")
publish = importlib.import_module("check_publish")
WORKSPACE = SCRIPTS.parent


def git(*args, cwd):
    result = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True,
                            encoding="utf-8", errors="replace", check=True)
    return result.stdout.strip()


class RestoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.upstream = self.root / "upstream"
        self.upstream.mkdir()
        git("init", cwd=self.upstream)
        git("config", "user.name", "Fixture", cwd=self.upstream)
        git("config", "user.email", "fixture@example.invalid", cwd=self.upstream)
        (self.upstream / "README.md").write_text("pinned first version\n", encoding="utf-8")
        (self.upstream / "AGENTS.md").write_text("upstream guide\n", encoding="utf-8")
        git("add", ".", cwd=self.upstream)
        git("commit", "-m", "first", cwd=self.upstream)
        self.sha = git("rev-parse", "HEAD", cwd=self.upstream)
        (self.upstream / "README.md").write_text("newer HEAD must not be selected\n", encoding="utf-8")
        git("commit", "-am", "second", cwd=self.upstream)
        self.dest = self.root / "repos/01-fixture"
        self.dest.mkdir(parents=True)
        self.guide = "Hướng dẫn local giữ nguyên dấu.\n".encode("utf-8")
        (self.dest / "AGENTS.md").write_bytes(self.guide)
        self.row = {"folder": "01-fixture", "id": "fixture", "commit": self.sha,
                    "url": "https://github.com/example/fixture", "readFirst": ["README.md"]}
        self.real_git = bootstrap.git

    def local_git(self, *args, **kwargs):
        # Exercise the real init/fetch/checkout path against a local Git origin.
        args = tuple(str(self.upstream) if a == self.row["url"] + ".git" else a for a in args)
        return self.real_git(*args, **kwargs)

    def restore(self, row=None):
        with patch.object(bootstrap, "ROOT", self.root), patch.object(bootstrap, "git", self.local_git):
            return bootstrap.restore(row or self.row)

    def test_pinned_commit_guide_and_archive_survive_retry(self):
        self.assertEqual(self.restore(), "restored")
        self.assertEqual((self.dest / "README.md").read_text(), "pinned first version\n")
        self.assertEqual((self.dest / "AGENTS.md").read_bytes(), self.guide)
        self.assertFalse((self.dest / ".git").exists())
        receipts = list((self.root / ".workspace/bootstrap").glob("*/receipt.json"))
        self.assertEqual(len(receipts), 1)
        receipt = json.loads(receipts[0].read_text())
        archive = self.root / receipt["gitMetadata"]
        self.assertEqual(git("--git-dir=" + str(archive), "rev-parse", "HEAD", cwd=self.root), self.sha)
        (self.dest / "README.md").write_text("local changes\n", encoding="utf-8")
        self.assertEqual(self.restore(), "skipped")
        self.assertEqual((self.dest / "README.md").read_text(), "local changes\n")
        self.assertEqual(len(list((self.root / ".workspace/bootstrap").glob("*/receipt.json"))), 1)

    def test_failed_fetch_preserves_destination(self):
        with self.assertRaises(RuntimeError):
            self.restore(dict(self.row, commit="0" * 40))
        self.assertEqual([p.name for p in self.dest.iterdir()], ["AGENTS.md"])
        self.assertEqual((self.dest / "AGENTS.md").read_bytes(), self.guide)

    def test_wrong_entrypoint_does_not_install_partial_source(self):
        with self.assertRaises(ValueError):
            self.restore(dict(self.row, readFirst=["missing.md"]))
        self.assertFalse((self.dest / "README.md").exists())
        self.assertEqual((self.dest / "AGENTS.md").read_bytes(), self.guide)

    def test_refuse_escape_before_fetch(self):
        with self.assertRaises(ValueError):
            self.restore(dict(self.row, folder="../../../outside"))


class WorkspaceTests(unittest.TestCase):
    def test_boundary_canonicalizes_root_and_rejects_escape(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "alias").mkdir()
            # Equivalent roots must compare equally, including Windows 8.3 aliases.
            with patch.object(studio, "ROOT", root / "alias/.."):
                self.assertEqual(studio.inside(root / "projects/demo"), (root / "projects/demo").resolve())
                with self.assertRaises(ValueError):
                    studio.inside(root.parent / "outside-workspace")

    def test_new_project_unicode_and_empty_media_folders(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            shutil.copytree(WORKSPACE / "templates", root / "templates")
            with patch.object(studio, "ROOT", root):
                studio.create_project(argparse.Namespace(project_id="fixture-video", title='Chữ Việt "đủ dấu"'))
                data = studio.read_json(root / "projects/fixture-video/project.json")
                self.assertEqual(data["title"], 'Chữ Việt "đủ dấu"')
                for name in ["working", "previews", "public"]:
                    self.assertEqual((root / "projects/fixture-video" / name / ".gitkeep").read_bytes(), b"")
                self.assertTrue((root / "output/fixture-video/.gitkeep").is_file())
                self.assertEqual(data["status"], "intake")

    def test_git_ignore_blocks_new_media_but_keeps_folders(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            shutil.copy2(WORKSPACE / ".gitignore", root / ".gitignore")
            git("init", cwd=root)
            fixtures = ["Source/footage/new.mp4", "Source/documents/private.md",
                        "projects/demo/public/video/new.MOV", "projects/demo/working/log.json",
                        "repos/01-fixture/README.md", "output/demo/new.mp4", "docs/production/evidence/local.png"]
            keeps = ["Source/footage/.gitkeep", "projects/demo/public/.gitkeep",
                     "projects/demo/working/.gitkeep", "output/demo/.gitkeep", "repos/01-fixture/AGENTS.md"]
            for name in fixtures + keeps:
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.touch()
            eligible = set(git("ls-files", "--others", "--exclude-standard", cwd=root).splitlines())
            for name in fixtures:
                self.assertNotIn(name, eligible)
            for name in keeps:
                self.assertIn(name, eligible)

    def test_manifest_invalid_sha_url_or_folder_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "configs").mkdir()
            base = {"folder": "01-fixture", "commit": "1" * 40, "url": "https://github.com/example/repo"}
            tool = {"id": "fixture", "folder": base["folder"], "upstream": base["url"], "readFirst": ["README.md"]}
            (root / "configs/tools.json").write_text(json.dumps({"tools": [tool]}))
            for changes in [{"commit": "main"}, {"url": "file:///outside"}, {"folder": "../escape"}]:
                (root / "repo-manifest.json").write_text(json.dumps({"repos": [dict(base, **changes)]}))
                with patch.object(bootstrap, "ROOT", root), self.assertRaises(ValueError):
                    list(bootstrap.load_entries())

    def test_actual_index_rejects_force_added_media(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            git("init", cwd=root)
            (root / "README.md").write_text("fixture\n", encoding="utf-8")
            git("add", "README.md", cwd=root)
            with patch.object(publish, "ROOT", root):
                self.assertEqual(publish.audit(), 0)
            (root / "bad.mp4").write_bytes(b"\x00media")
            git("add", "-f", "bad.mp4", cwd=root)
            with patch.object(publish, "ROOT", root), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(publish.audit(), 1)

    def test_credentials_and_filled_placeholders_rejected(self):
        secret = ("ghp_" + "A" * 36).encode("ascii")
        self.assertTrue(publish.problems("README.md", "100644", secret))
        self.assertTrue(publish.problems("Source/.gitkeep", "100644", b"private input"))
        self.assertTrue(publish.problems("repos/01-fixture/README.md", "100644", b"upstream"))


if __name__ == "__main__":
    unittest.main()
