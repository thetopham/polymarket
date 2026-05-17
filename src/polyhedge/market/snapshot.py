from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MarketSnapshot:
    market_id: str
    ts: int
    yes_bid: float
    yes_ask: float
    no_bid: float
    no_ask: float
    signal_price: float
    target_price: float
    slope: float
    volatility_score: float
    seconds_to_close: int

    @property
    def spread(self) -> float:
        return max(0.0, self.yes_ask - self.yes_bid) + max(0.0, self.no_ask - self.no_bid)
