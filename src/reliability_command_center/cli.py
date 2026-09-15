from __future__ import annotations

import argparse
import json
from pathlib import Path

from reliability_command_center.engine import decide, decision_dict, render_metrics


def main() -> int:
    parser = argparse.ArgumentParser(description="Create an approval-gated incident decision record.")
    parser.add_argument("--incident", type=Path, required=True)
    parser.add_argument("--decision", type=Path, required=True)
    parser.add_argument("--metrics", type=Path, required=True)
    args = parser.parse_args()
    decision = decide(json.loads(args.incident.read_text(encoding="utf-8")))
    args.decision.parent.mkdir(parents=True, exist_ok=True)
    args.metrics.parent.mkdir(parents=True, exist_ok=True)
    args.decision.write_text(
        json.dumps(decision_dict(decision), indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    args.metrics.write_text(render_metrics(decision), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
