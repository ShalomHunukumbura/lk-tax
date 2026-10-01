from decimal import Decimal

import pytest

from lk_tax import sscl


@pytest.mark.parametrize("activity,levy", [("import", "25000.00"), ("manufacture", "21250.00"), ("service", "25000.00"),
                                           ("distributor", "6250.00"), ("wholesale_retail", "12500.00")])
def test_liable_share_by_activity(activity, levy):
    assert sscl.levy(1_000_000, activity, "2025-01-01").levy == Decimal(levy)


def test_effective_rate():
    assert sscl.levy(1, "manufacture", "2025-01-01").effective_rate == Decimal("0.02125")


@pytest.mark.parametrize("on,quarter,annual", [("2023-06-01", 30_000_000, 120_000_000),
                                               ("2024-01-01", 15_000_000, 60_000_000),
                                               ("2026-06-30", 15_000_000, 60_000_000),
                                               ("2026-07-01", 9_000_000, 36_000_000)])
def test_threshold_history(on, quarter, annual):
    r = sscl.registration(quarter_turnover=1, on=on)
    assert (r.quarter_threshold, r.annual_threshold) == (quarter, annual)


def test_same_business_must_register_after_july_2026():
    assert not sscl.registration(quarter_turnover=12_000_000, on="2026-06-30").must_register
    assert sscl.registration(quarter_turnover=12_000_000, on="2026-07-01").must_register


def test_unknown_activity():
    with pytest.raises(ValueError, match="choose from"):
        sscl.levy(1, "mining", "2025-01-01")
