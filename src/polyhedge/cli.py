from __future__ import annotations

import argparse
import json
from pathlib import Path

from polyhedge.config.settings import load_config


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="polyhedge")
    sub = parser.add_subparsers(dest="cmd", required=True)
    doctor = sub.add_parser("doctor", help="read-only config/environment check")
    doctor.add_argument("--config", required=True)
    args = parser.parse_args(argv)

    if args.cmd == "doctor":
        cfg = load_config(Path(args.config))
        payload = {
            "ok": True,
            "mode": cfg.mode,
            "safety_boundary": "paper_only_no_live_orders_no_relayer_wallet_batches",
            "deposit_wallet": cfg.deposit_wallet.safe_summary(),
        }
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0
    return 2
