from polyhedge.portfolio.position import InventoryBook, Side


def test_inventory_book_tracks_average_prices_and_combined_basis():
    book = InventoryBook()

    book.add(Side.YES, qty=3, price=0.62)
    book.add(Side.NO, qty=2, price=0.35)
    book.add(Side.NO, qty=1, price=0.20)

    assert book.yes.qty == 3
    assert book.yes.avg_price == 0.62
    assert book.no.qty == 3
    assert round(book.no.avg_price, 4) == 0.3
    assert round(book.total_cost, 2) == 2.76
    assert round(book.paired_basis, 2) == 0.92


def test_inventory_book_reports_settlement_geometry_and_residual_exposure():
    book = InventoryBook()
    book.add(Side.YES, qty=4, price=0.55)
    book.add(Side.NO, qty=2, price=0.30)

    geometry = book.settlement_geometry()

    assert geometry.matched_pairs == 2
    assert geometry.residual_side == Side.YES
    assert geometry.residual_qty == 2
    assert round(geometry.pair_cost, 2) == 0.85
    assert round(geometry.locked_pair_edge, 2) == 0.30
    assert round(geometry.worst_case_pnl, 2) == -0.80


def test_mark_to_market_uses_bid_side_for_existing_inventory():
    book = InventoryBook()
    book.add(Side.YES, qty=2, price=0.40)
    book.add(Side.NO, qty=2, price=0.35)

    assert round(book.mark_to_market_pnl(yes_bid=0.48, no_bid=0.31), 2) == 0.08
