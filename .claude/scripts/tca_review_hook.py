"""PostToolUse review hook: the semantic tier, on sonnet.

The deterministic gate (tca_gate.py, PreToolUse) blocks the mechanical breaks before a
write lands. This runs after the write, on sonnet, for coverage of the semantic residue a
parser cannot decide: a vacuous name, a vocabulary that should be a scalar or has fused
axes, a union that is not disjoint, a construct that does not discharge its obligation. It
surfaces findings as context; it does not block, because the structural floor already held.
The same reviewer brain (tca-purity-review.md) runs here on sonnet and is invoked directly
on opus for a deep audit.
"""

import json
import os
import subprocess
import sys
from pathlib import Path


def _in_scope(file_path: str) -> bool:
    scope = os.environ.get("TCA_GATE_PATH_SUBSTR", "/tca/")
    return (
        file_path.endswith(".py")
        and scope in file_path
        and "/.claude/" not in file_path
        and not file_path.endswith("closure_linter.py")
        and "/tests/" not in file_path
    )


def main() -> None:
    event = json.loads(sys.stdin.read())
    file_path = event.get("tool_input", {}).get("file_path", "")
    if not _in_scope(file_path) or not Path(file_path).exists():
        return
    review_dir = Path(__file__).resolve().parent
    content = Path(file_path).read_text()
    proc = subprocess.run(
        [
            "claude", "-p",
            "--model", "claude-sonnet-4-6",
            "--system-prompt-file", str(review_dir / "tca-purity-review.md"),
            "--output-format", "json",
        ],
        input="Review this TCA source for purity. File: " + file_path + "\n\n" + content,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    if proc.returncode != 0:
        return  # reviewer infra issue; the deterministic gate already held the floor
    try:
        result_text = json.loads(proc.stdout).get("result", "")
        findings = json.loads(result_text).get("findings", [])
    except (json.JSONDecodeError, AttributeError, TypeError):
        return
    if not findings:
        return
    lines = [
        "- [" + str(f.get("break", "?")) + "/" + str(f.get("confidence", "?")) + "] "
        + str(f.get("rule", "")) + " at " + str(f.get("where", "")) + " -> " + str(f.get("fix", ""))
        for f in findings
    ]
    context = "TCA semantic review (sonnet, coverage) on " + file_path + ":\n" + "\n".join(lines)
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": context}}))


if __name__ == "__main__":
    main()
