from __future__ import annotations

from dataclasses import dataclass

from polyhedge.market.snapshot import MarketSnapshot
from polyhedge.portfolio.position import InventoryBook, Side


@dataclass(frozen=True)
class Decision:
    side: Side
    qty: int
    limit_price: float
    reason: str


@dataclass(frozen=True)
class SyntheticHedgeStrategy:
    initial_trend_qty: int = 3
    initial_hedge_qty: int = 2
    crushed_price_threshold: float = 0.25
    volatility_threshold: float = 0.5
    max_imbalance_ratio: float = 3.0
    min_seconds_to_close: int = 60

    def decide(self, book: InventoryBook, snap: MarketSnapshot) -> list[Decision]:
        if snap.seconds_to_close < self.min_seconds_to_close:
            return []
        if book.total_qty == 0:
            return self._initial_seed(snap)
        return self._volatility_adds(book, snap)

    def _initial_seed(self, snap: MarketSnapshot) -> list[Decision]:
        if snap.signal_price > snap.target_price and snap.slope > 0:
            return [
                Decision(Side.YES, self.initial_trend_qty, snap.yes_ask, "initial_bullish_seed"),
                Decision(Side.NO, self.initial_hedge_qty, snap.no_ask, "initial_bullish_seed"),
            ]
        if snap.signal_price < snap.target_price and snap.slope < 0:
            return [
                Decision(Side.NO, self.initial_trend_qty, snap.no_ask, "initial_bearish_seed"),
                Decision(Side.YES, self.initial_hedge_qty, snap.yes_ask, "initial_bearish_seed"),
            ]
        return []

    def _volatility_adds(self, book: InventoryBook, snap: MarketSnapshot) -> list[Decision]:
        if snap.volatility_score < self.volatility_threshold:
            return []
        decisions: list[Decision] = []
        if snap.yes_ask <= self.crushed_price_threshold and self._can_add(book, Side.YES):
            decisions.append(Decision(Side.YES, 1, snap.yes_ask, "volatility_crushed_yes"))
        if snap.no_ask <= self.crushed_price_threshold and self._can_add(book, Side.NO):
            decisions.append(Decision(Side.NO, 1, snap.no_ask, "volatility_crushed_no"))
        return decisions

    def _can_add(self, book: InventoryBook, side: Side) -> bool:
        return book.projected_imbalance_ratio(side, 1) <= self.max_imbalance_ratio
