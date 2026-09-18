from products.inventory import suggest_flight, upcoming_flights


def test_delhi_goa_uses_scheduled_catalog():
    flight = suggest_flight(origin="Delhi", destination="Goa", date="next Friday", passengers="2")
    assert flight.source == "scheduled"
    assert flight.flight == "SK-441"
    assert flight.origin == "Delhi"
    assert flight.destination == "Goa"
    assert "SK-441" in flight.href
    assert flight.href.startswith("/exit")


def test_unknown_route_is_random_not_ticketed():
    flight = suggest_flight(origin="Pune", destination="Kochi", date="tomorrow", passengers="1")
    assert flight.source == "random"
    assert flight.origin.lower() == "pune"
    assert flight.destination.lower() == "kochi"
    assert flight.flight


def test_upcoming_board_has_catalog_rows():
    board = upcoming_flights()
    assert len(board) >= 8
    assert any(row.flight == "SK-441" for row in board)
