from polyhedge.market.snapshot import MarketSnapshot
from polyhedge.portfolio.position import InventoryBook, Side
from polyhedge.strategy.synthetic_hedge import SyntheticHedgeStrategy


def test_initial_seed_biases_toward_bullish_yes_side():
    strategy = SyntheticHedgeStrategy()
    book = InventoryBook()
    snap = MarketSnapshot(
        market_id="btc-updown",
        ts=1,
        yes_bid=0.58,
        yes_ask=0.60,
        no_bid=0.38,
        no_ask=0.40,
        signal_price=103,
        target_price=100,
        slope=1.2,
        volatility_score=0.2,
        seconds_to_close=600,
    )

    decisions = strategy.decide(book, snap)

    assert [(d.side, d.qty, d.limit_price, d.reason) for d in decisions] == [
        (Side.YES, 3, 0.60, "initial_bullish_seed"),
        (Side.NO, 2, 0.40, "initial_bullish_seed"),
    ]


def test_high_volatility_adds_crushed_side_without_increasing_imbalance():
    strategy = SyntheticHedgeStrategy(max_imbalance_ratio=2.0)
    book = InventoryBook()
    book.add(Side.YES, 3, 0.60)
    book.add(Side.NO, 2, 0.40)
    snap = MarketSnapshot(
        market_id="btc-updown",
        ts=2,
        yes_bid=0.18,
        yes_ask=0.20,
        no_bid=0.78,
        no_ask=0.80,
        signal_price=97,
        target_price=100,
        slope=-2.0,
        volatility_score=0.9,
        seconds_to_close=400,
    )

    decisions = strategy.decide(book, snap)

    assert len(decisions) == 1
    assert decisions[0].side == Side.YES
    assert decisions[0].qty == 1
    assert decisions[0].reason == "volatility_crushed_yes"


def test_late_window_goes_watch_only():
    strategy = SyntheticHedgeStrategy(min_seconds_to_close=90)
    snap = MarketSnapshot(
        market_id="btc-updown",
        ts=3,
        yes_bid=0.50,
        yes_ask=0.52,
        no_bid=0.47,
        no_ask=0.49,
        signal_price=100,
        target_price=100,
        slope=0,
        volatility_score=0.0,
        seconds_to_close=30,
    )

    assert strategy.decide(InventoryBook(), snap) == []
