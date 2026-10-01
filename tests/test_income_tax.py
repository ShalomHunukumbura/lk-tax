from datetime import date
from decimal import Decimal

import pytest

from lk_tax import NotCovered, apit_monthly, income_tax_annual


# The IRD's own summary formulas, typed in from the Table No. 01 notes. They are
# an independent check on the band arithmetic in lk_tax.income_tax.
def ird_2526(m):
    for limit, rate, less in [(358_333, "0.36", 94_000), (316_667, "0.30", 72_500), (275_000, "0.24", 53_500),
                              (233_333, "0.18", 37_000), (150_000, "0.06", 9_000)]:
        if m > limit:
            return Decimal(rate) * m - less
    return Decimal(0)


def ird_2324(m):
    for limit, rate, less in [(308_333, "0.36", 73_500), (266_667, "0.30", 55_000), (225_000, "0.24", 39_000),
                              (183_333, "0.18", 25_500), (141_667, "0.12", 14_500), (100_000, "0.06", 6_000)]:
        if m > limit:
            return Decimal(rate) * m - less
    return Decimal(0)


@pytest.mark.parametrize("m", [0, 99_999, 150_000, 150_001, 200_000, 233_334, 250_000, 300_000, 350_000, 400_000, 2_000_000])
def test_exact_matches_ird_summary_formula_2025(m):
    assert apit_monthly(m, "2025-04-01").exact_tax == ird_2526(m).quantize(Decimal("0.01"))


@pytest.mark.parametrize("m", [0, 100_000, 100_001, 150_000, 190_000, 230_000, 280_000, 309_000, 500_000])
def test_exact_matches_ird_summary_formula_2023(m):
    assert apit_monthly(m, "2023-01-15").exact_tax == ird_2324(m).quantize(Decimal("0.01"))


def test_rules_switch_on_1_april_2025():
    assert apit_monthly(200_000, "2025-03-31").tax == 10_500  # 18% x 200,000 - 25,500
    assert apit_monthly(200_000, "2025-04-01").tax == 3_000   # 6% x 200,000 - 9,000


def test_annual_worked_example():
    # 4,000,000 - 1,800,000 relief = 2,200,000 taxable:
    # 1,000,000 x 6% + 500,000 x 18% + 500,000 x 24% + 200,000 x 30%
    r = income_tax_annual(4_000_000, "2025/26")
    assert r.tax == Decimal("330000.00")
    assert r.taxable_income == 2_200_000
    assert [b.rate for b in r.bands] == [Decimal("0.06"), Decimal("0.18"), Decimal("0.24"), Decimal("0.30")]
    assert r.effective_rate == Decimal("0.0825")


def test_annual_old_regime():
    # 3,000,000 - 1,200,000 = 1,800,000: 500k x (6+12+18)% + 300k x 24%
    assert income_tax_annual(3_000_000, "2024/2025").tax == Decimal("252000.00")


def test_annual_and_monthly_agree():
    for monthly in (160_000, 275_000, 333_333, 500_000):
        yearly = income_tax_annual(monthly * 12, "2026/27").tax
        assert apit_monthly(monthly, "2026-05-31").exact_tax * 12 == pytest.approx(yearly, abs=Decimal("0.12"))


def test_below_relief_pays_nothing():
    assert income_tax_annual(1_800_000, "2025/26").tax == 0
    assert income_tax_annual(0, "2025/26").effective_rate == 0


def test_result_cites_its_sources():
    r = apit_monthly(300_000, "2026-09-30")
    assert r.rule.effective_from == date(2025, 4, 1)
    assert r.rule.effective_to is None
    assert all(s.url.startswith("https://www.ird.gov.lk/") for s in r.rule.sources)
    assert apit_monthly(300_000, "2024-01-01").rule.effective_to == date(2025, 3, 31)


def test_coverage_limits():
    with pytest.raises(NotCovered):
        apit_monthly(300_000, "2022-12-31")
    with pytest.raises(NotCovered):
        income_tax_annual(3_000_000, "2022/23")


@pytest.mark.parametrize("bad", ["2025", "2025/27", "abc/de"])
def test_bad_year_label(bad):
    with pytest.raises(ValueError):
        income_tax_annual(1, bad)


def test_floats_do_not_leak_binary_errors():
    assert apit_monthly(200_000.10, "2025-04-01").exact_tax == Decimal("3000.01")


@pytest.mark.parametrize("bad", [-1, "lots", float("nan"), True])
def test_bad_amounts(bad):
    with pytest.raises((ValueError, TypeError)):
        apit_monthly(bad, "2025-04-01")
