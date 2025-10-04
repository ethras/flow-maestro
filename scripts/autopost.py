#!/usr/bin/env python3
"""Render Linear comment bodies from Flow Maestro macros."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MACRO_DIR = REPO_ROOT / "templates" / "linear-macros"


def load_template(name: str) -> dict[str, str]:
    path = MACRO_DIR / f"{name}.json"
    if not path.exists():
        raise SystemExit(f"Macro '{name}' not found under {MACRO_DIR}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if "template" not in data:
        raise SystemExit(f"Macro '{name}' is missing a 'template' field")
    return data


def render(template: str, values: dict[str, str]) -> str:
    pattern = re.compile(r"\{\{\s*(?P<key>[a-zA-Z0-9_]+)\s*\}\}")

    def repl(match: re.Match[str]) -> str:
        key = match.group("key")
        return values.get(key, f"{{{key}}}")

    return pattern.sub(repl, template)


def parse_assignments(assignments: list[str]) -> dict[str, str]:
    result: dict[str, str] = {}
    for item in assignments:
        if "=" not in item:
            raise SystemExit(f"Invalid assignment '{item}'. Use key=value format.")
        key, value = item.split("=", 1)
        result[key.strip()] = value.strip()
    return result


def build_args() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Render Flow Maestro Linear comment macros")
    parser.add_argument("macro", help="Macro name (e.g., progress-log)")
    parser.add_argument(
        "--set",
        dest="assignments",
        metavar="key=value",
        action="append",
        default=[],
        help="Placeholder substitutions (repeatable)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional file to write the rendered comment",
    )
    parser.add_argument(
        "--print-json",
        action="store_true",
        help="Emit JSON payload with 'body' field for direct create_comment_linear usage",
    )
    parser.add_argument(
        "--issue",
        help="Linear issue key (used only when --print-json is passed)",
    )
    return parser


def macro_choices() -> set[str]:
    return {p.stem for p in MACRO_DIR.glob("*.json")}


def main(argv: list[str] | None = None) -> int:
    choices = macro_choices()
    parser = build_args()
    args = parser.parse_args(argv)

    if args.macro not in choices:
        raise SystemExit(f"Macro '{args.macro}' not available. Choices: {sorted(choices)}")

    data = load_template(args.macro)
    subs = parse_assignments(args.assignments)

    comment = render(data["template"], subs)

    if args.output:
        args.output.write_text(comment, encoding="utf-8")
    if args.print_json:
        if not args.issue:
            raise SystemExit("--print-json requires --issue <ISSUE-KEY>")
        payload = {
            "issueId": args.issue,
            "body": comment,
            "meta": {"macro": args.macro, "assignments": subs},
        }
        sys.stdout.write(json.dumps(payload, indent=2))
        sys.stdout.write("\n")
    else:
        sys.stdout.write(comment)
        sys.stdout.write("\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
