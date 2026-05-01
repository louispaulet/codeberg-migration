#!/usr/bin/env python3

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


BASE_DIR = Path.home() / "codeberg-migration"
FAILURES_FILE = BASE_DIR / "clean_push_failures.txt"


def run(cmd: list[str], cwd: Path) -> tuple[int, str]:
    """
    Run a command and stream its output only if it fails.
    Returns: (returncode, combined_output)
    """
    proc = subprocess.run(
        cmd,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    return proc.returncode, proc.stdout


def progress_bar(current: int, total: int, repo_name: str, width: int = 30) -> None:
    ratio = current / total if total else 1
    filled = int(width * ratio)
    bar = "█" * filled + "░" * (width - filled)
    percent = int(ratio * 100)

    msg = f"\r[{bar}] {current}/{total} {percent:3d}%  {repo_name[:45]:45}"
    print(msg, end="", flush=True)


def main() -> int:
    codeberg_user = os.environ.get("CODEBERG_USER")
    codeberg_token = os.environ.get("CODEBERG_TOKEN")

    if not codeberg_user or not codeberg_token:
        print("Missing CODEBERG_USER or CODEBERG_TOKEN.")
        print()
        print("Set them first:")
        print('  export CODEBERG_USER="thefrenchartist"')
        print('  export CODEBERG_TOKEN="your_token_here"')
        return 1

    if not BASE_DIR.exists():
        print(f"Folder does not exist: {BASE_DIR}")
        return 1

    repo_dirs = sorted(p for p in BASE_DIR.glob("*.git") if p.is_dir())

    if not repo_dirs:
        print(f"No *.git mirror repositories found in {BASE_DIR}")
        return 1

    failures: list[str] = []
    logs_dir = BASE_DIR / "push_logs"
    logs_dir.mkdir(exist_ok=True)

    FAILURES_FILE.write_text("", encoding="utf-8")

    print(f"Found {len(repo_dirs)} mirror repositories.")
    print(f"Pushing branches and tags to Codeberg as {codeberg_user}.")
    print()

    for idx, repo_dir in enumerate(repo_dirs, start=1):
        repo_name = repo_dir.name.removesuffix(".git")
        progress_bar(idx - 1, len(repo_dirs), f"starting {repo_name}")

        remote_url = (
            f"https://{codeberg_user}:{codeberg_token}"
            f"@codeberg.org/{codeberg_user}/{repo_name}.git"
        )

        repo_log: list[str] = []
        ok = True

        commands = [
            ["git", "remote", "remove", "codeberg"],
            ["git", "remote", "add", "codeberg", remote_url],
            ["git", "push", "codeberg", "refs/heads/*:refs/heads/*"],
            ["git", "push", "codeberg", "refs/tags/*:refs/tags/*"],
        ]

        for cmd in commands:
            # Removing a missing remote is fine.
            returncode, output = run(cmd, cwd=repo_dir)

            if cmd[:4] == ["git", "remote", "remove", "codeberg"] and returncode != 0:
                repo_log.append("$ " + " ".join(cmd))
                repo_log.append(output.strip())
                repo_log.append("Ignored: codeberg remote probably did not exist yet.")
                continue

            repo_log.append("$ " + " ".join(cmd))
            repo_log.append(output.strip())

            if returncode != 0:
                ok = False

        if ok:
            progress_bar(idx, len(repo_dirs), f"OK {repo_name}")
        else:
            failures.append(repo_name)
            log_path = logs_dir / f"{repo_name}.log"
            log_path.write_text("\n\n".join(repo_log), encoding="utf-8")
            progress_bar(idx, len(repo_dirs), f"FAILED {repo_name}")

    print()
    print()

    if failures:
        FAILURES_FILE.write_text(
            "\n".join(f"{name} - clean push failed" for name in failures) + "\n",
            encoding="utf-8",
        )

        print(f"{len(failures)} repo(s) failed:")
        for name in failures:
            print(f"  - {name}")

        print()
        print(f"Failure list: {FAILURES_FILE}")
        print(f"Logs: {logs_dir}")
        return 1

    print("All repositories pushed successfully.")
    print(f"Failure list is empty: {FAILURES_FILE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
