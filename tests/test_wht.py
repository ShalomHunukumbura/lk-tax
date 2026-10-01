from decimal import Decimal

import pytest

from lk_tax import wht


def test_interest_rate_change_on_1_april_2025():
    assert wht.calculate("interest", 100_000, "2025-03-31").tax == Decimal("5000.00")
    r = wht.calculate("interest", 100_000, "2025-04-01")
    assert r.tax == Decimal("10000.00") and r.net_paid == Decimal("90000.00")
    assert "self-declaration" in r.rule.note


def test_service_fee_below_threshold_has_no_wht():
    r = wht.calculate("service_fee", 100_000, "2025-06-01")
    assert not r.applies and r.tax == 0 and r.net_paid == 100_000


def test_service_fee_above_threshold_taxes_the_full_payment():
    r = wht.calculate("service_fee", 100_001, "2025-06-01")
    assert r.applies and r.tax == Decimal("5000.05")


def test_monthly_total_decides_not_the_single_payment():
    # Third invoice of 40,000 in a month where 120,000 has now been paid.
    r = wht.calculate("service_fee", 40_000, "2025-06-01", month_total=120_000)
    assert r.applies and r.tax == Decimal("2000.00")


def test_rent_threshold():
    assert wht.calculate("rent_resident", 90_000, "2024-01-01").tax == 0
    assert wht.calculate("rent_resident", 150_000, "2024-01-01").tax == Decimal("15000.00")


def test_payer_bears_tax_grosses_up():
    # The payee must receive 190,000 in full, so gross = 190,000 / (1 - 5%) = 200,000.
    r = wht.calculate("service_fee", 190_000, "2025-06-01", payer_bears_tax=True)
    assert r.gross == Decimal("200000.00") and r.tax == Decimal("10000.00") and r.net_paid == Decimal("190000.00")


def test_small_lottery_winnings_are_exempt():
    assert not wht.calculate("winnings", 500_000, "2024-01-01").applies
    assert wht.calculate("winnings", 500_001, "2024-01-01").tax == Decimal("70000.14")


def test_service_fee_coverage_widened_in_june_2026():
    assert "photographers" not in wht.calculate("service_fee", 1, "2026-06-02").covers
    assert "photographers" in wht.calculate("service_fee", 1, "2026-06-03").covers


@pytest.mark.parametrize("key,rate", [("dividend", "0.15"), ("royalty", "0.14"), ("rent_non_resident", "0.14"),
                                      ("service_fee_non_resident", "0.14"), ("transport_non_resident", "0.02"),
                                      ("gem_auction", "0.025"), ("charge_or_premium", "0.14")])
def test_flat_rates(key, rate):
    assert wht.calculate(key, 1_000_000, "2026-01-01").rate == Decimal(rate)


def test_unknown_payment_type():
    with pytest.raises(ValueError, match="choose from"):
        wht.calculate("salary", 1, "2026-01-01")


def test_payment_types_listed():
    assert "interest" in wht.payment_types()
