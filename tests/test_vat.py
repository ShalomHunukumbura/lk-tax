from decimal import Decimal

import pytest

from lk_tax import vat


@pytest.mark.parametrize("on,rate", [("2023-06-01", "0.15"), ("2023-12-31", "0.15"), ("2024-01-01", "0.18"), ("2026-09-30", "0.18")])
def test_standard_rate_history(on, rate):
    assert vat.rate(on) == Decimal(rate)


def test_financial_services_rate_rises_in_july_2026():
    assert vat.rate("2026-06-30", "financial_services") == Decimal("0.18")
    assert vat.rate("2026-07-01", "financial_services") == Decimal("0.205")


def test_add_and_extract_round_trip():
    added = vat.add(1_000, "2025-01-01")
    assert (added.vat, added.gross) == (Decimal("180.00"), Decimal("1180.00"))
    extracted = vat.extract(1_180, "2025-01-01")
    assert (extracted.net, extracted.vat) == (Decimal("1000.00"), Decimal("180.00"))


def test_extract_uses_the_tax_fraction():
    # 15% has a tax fraction of 3/23 (VAT Amendment Act No. 44 of 2022)
    assert vat.extract(2_300, "2023-06-01").vat == Decimal("300.00")


def test_registration_thresholds_by_date():
    assert vat.registration(turnover_12_months=70_000_000, on="2023-12-31").must_register is False
    assert vat.registration(turnover_12_months=70_000_000, on="2024-01-01").must_register is True


def test_2022_period_threshold_was_inclusive():
    assert vat.registration(period_turnover=20_000_000, on="2023-06-01").must_register is True
    assert vat.registration(period_turnover=15_000_000, on="2024-06-01").must_register is False
    assert vat.registration(period_turnover=15_000_001, on="2024-06-01").must_register is True


def test_threshold_unchanged_in_2026():
    r = vat.registration(turnover_12_months=50_000_000, on="2026-09-30")
    assert r.annual_threshold == 60_000_000 and not r.must_register


def test_registration_needs_a_figure():
    with pytest.raises(ValueError):
        vat.registration(on="2025-01-01")


def test_bad_supply():
    with pytest.raises(ValueError):
        vat.add(1, "2025-01-01", supply="luxury")
