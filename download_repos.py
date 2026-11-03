"""Compatibility entrypoint for pinned source restore; see docs/GIT.md."""
from scripts.bootstrap_repos import main

if __name__ == '__main__':
    raise SystemExit(main())
