from datetime import date, datetime

from pipeline.clean_prices import entry_session

# Mon 2 Jun 2025 ... Fri 6 Jun, then Mon 9 Jun
DAYS = [date(2025, 6, 2), date(2025, 6, 3), date(2025, 6, 4),
        date(2025, 6, 5), date(2025, 6, 6), date(2025, 6, 9)]


def test_saturday_tip_uses_monday():
    # Sat 7 Jun 10:00 IST = 04:30 UTC
    assert entry_session(datetime(2025, 6, 7, 4, 30), DAYS) == date(2025, 6, 9)


def test_before_open_same_day():
    # Tue 3 Jun 08:00 IST = 02:30 UTC
    assert entry_session(datetime(2025, 6, 3, 2, 30), DAYS) == date(2025, 6, 3)


def test_during_market_hours_next_day():
    # Tue 3 Jun 11:00 IST = 05:30 UTC
    assert entry_session(datetime(2025, 6, 3, 5, 30), DAYS) == date(2025, 6, 4)


def test_after_close_next_day():
    # Tue 3 Jun 20:00 IST = 14:30 UTC
    assert entry_session(datetime(2025, 6, 3, 14, 30), DAYS) == date(2025, 6, 4)


def test_friday_after_close_uses_monday():
    # Fri 6 Jun 18:00 IST = 12:30 UTC
    assert entry_session(datetime(2025, 6, 6, 12, 30), DAYS) == date(2025, 6, 9)


def test_utc_ist_day_boundary():
    # Tue 3 Jun 23:00 UTC = Wed 4 Jun 04:30 IST, before open -> Wed
    assert entry_session(datetime(2025, 6, 3, 23, 0), DAYS) == date(2025, 6, 4)


def test_holiday_missing_from_calendar():
    days = [d for d in DAYS if d != date(2025, 6, 4)]
    assert entry_session(datetime(2025, 6, 3, 5, 30), days) == date(2025, 6, 5)


def test_no_later_day_returns_none():
    assert entry_session(datetime(2025, 6, 9, 14, 30), DAYS) is None