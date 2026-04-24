#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rdharness.environment import (  # noqa: E402
    available_environment_profiles,
    detect_environment_profile,
    resolve_install_plan,
    run_install_plan,
    shell_exports,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Create or update a lightweight repo venv using a pinned environment profile."
    )
    parser.add_argument(
        "--profile",
        default="auto",
        help="Environment profile from configs/environment (default: auto)",
    )
    parser.add_argument("--torch-profile", help="Override the torch profile from the environment config")
    parser.add_argument("--venv", help="Override the target virtualenv path")
    parser.add_argument("--no-dev", action="store_true", help="Skip pinned dev dependencies")
    parser.add_argument("--dry-run", action="store_true", help="Print commands without executing them")
    parser.add_argument("--json", action="store_true", help="Print the resolved plan as JSON")
    parser.add_argument(
        "--emit-shell",
        action="store_true",
        help="Print shell exports for the venv and recommended cache variables",
    )
    parser.add_argument(
        "--list-profiles",
        action="store_true",
        help="List available environment profiles and exit",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.list_profiles:
        print("auto")
        for profile in available_environment_profiles():
            print(profile)
        return 0

    profile_name = detect_environment_profile() if args.profile == "auto" else args.profile

    try:
        plan = resolve_install_plan(
            profile_name,
            torch_profile=args.torch_profile,
            include_dev=not args.no_dev,
            venv_path=args.venv,
        )
    except ValueError as exc:
        parser.error(str(exc))

    if args.json:
        print(json.dumps(plan, indent=2))
        return 0

    run_install_plan(plan, dry_run=args.dry_run)

    if args.emit_shell:
        print("\n".join(shell_exports(plan)))
        return 0

    print(f"Environment ready at {plan['venv_path']} using profile {profile_name} and torch profile {plan['torch_profile']}.")
    print(f"Activate with: . {plan['venv_path']}/bin/activate")
    for line in shell_exports(plan)[2:]:
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
