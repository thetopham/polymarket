from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class Side(StrEnum):
    YES = "YES"
    NO = "NO"


@dataclass
class Position:
    qty: int = 0
    avg_price: float = 0.0

    @property
    def cost(self) -> float:
        return self.qty * self.avg_price

    def add(self, qty: int, price: float) -> None:
        if qty <= 0:
            raise ValueError("qty must be positive")
        if not 0 <= price <= 1:
            raise ValueError("price must be between 0 and 1")
        total_cost = self.cost + qty * price
        self.qty += qty
        self.avg_price = total_cost / self.qty


@dataclass(frozen=True)
class SettlementGeometry:
    matched_pairs: int
    residual_side: Side | None
    residual_qty: int
    pair_cost: float
    locked_pair_edge: float
    worst_case_pnl: float


@dataclass
class InventoryBook:
    yes: Position | None = None
    no: Position | None = None

    def __post_init__(self) -> None:
        if self.yes is None:
            self.yes = Position()
        if self.no is None:
            self.no = Position()

    @property
    def total_cost(self) -> float:
        return self.yes.cost + self.no.cost

    @property
    def total_qty(self) -> int:
        return self.yes.qty + self.no.qty

    @property
    def matched_pairs(self) -> int:
        return min(self.yes.qty, self.no.qty)

    @property
    def paired_basis(self) -> float:
        if self.matched_pairs == 0:
            return 0.0
        return self.yes.avg_price + self.no.avg_price

    def add(self, side: Side, qty: int, price: float) -> None:
        if side == Side.YES:
            self.yes.add(qty, price)
        elif side == Side.NO:
            self.no.add(qty, price)
        else:
            raise ValueError(f"unknown side: {side}")

    def side_qty(self, side: Side) -> int:
        return self.yes.qty if side == Side.YES else self.no.qty

    def projected_imbalance_ratio(self, side: Side, add_qty: int) -> float:
        yes_qty = self.yes.qty + (add_qty if side == Side.YES else 0)
        no_qty = self.no.qty + (add_qty if side == Side.NO else 0)
        smaller = min(yes_qty, no_qty)
        larger = max(yes_qty, no_qty)
        if smaller == 0:
            return float("inf") if larger else 0.0
        return larger / smaller

    def settlement_geometry(self) -> SettlementGeometry:
        pairs = self.matched_pairs
        residual_side: Side | None = None
        residual_qty = 0
        if self.yes.qty > self.no.qty:
            residual_side = Side.YES
            residual_qty = self.yes.qty - self.no.qty
        elif self.no.qty > self.yes.qty:
            residual_side = Side.NO
            residual_qty = self.no.qty - self.yes.qty

        pair_cost = self.paired_basis if pairs else 0.0
        locked_pair_edge = max(0.0, (1.0 - pair_cost) * pairs)
        yes_wins_pnl = self.yes.qty - self.total_cost
        no_wins_pnl = self.no.qty - self.total_cost
        return SettlementGeometry(
            matched_pairs=pairs,
            residual_side=residual_side,
            residual_qty=residual_qty,
            pair_cost=pair_cost,
            locked_pair_edge=locked_pair_edge,
            worst_case_pnl=min(yes_wins_pnl, no_wins_pnl),
        )

    def mark_to_market_pnl(self, yes_bid: float, no_bid: float) -> float:
        mark_value = self.yes.qty * yes_bid + self.no.qty * no_bid
        return mark_value - self.total_cost
