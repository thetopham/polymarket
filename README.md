# Polymarket Hedge Bot

Paper-first Polymarket inventory hedge/replay project.

Safety boundary for v0:

- Read-only market discovery and public CLOB data are allowed.
- Paper/replay fills only.
- No live order placement, cancellation, relayer wallet batches, on-chain approvals, or balance sync commands are implemented.
- Deposit-wallet/API fields are configuration metadata only until explicit approval to build live trading.

The strategy shape mirrors the Kalshi synthetic hedge idea, adapted to Polymarket binary YES/NO outcome token markets: build small two-sided inventory, bias toward a signal only as an inventory seed, add the crushed side during volatility, and measure blended basis, worst-case settlement, residual exposure, and mark-to-market PnL.

Quick start:

```bash
cd /home/matt/workspace/polymarket-hedge-bot
python3 -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
pytest -q
polyhedge doctor --config configs/paper.example.toml
```
