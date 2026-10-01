"""APIT must match the IRD's official Tax Table No. 01, row by row.

The fixtures are every row of the official 280-page PDFs, extracted with
scripts/extract_apit_table.py. Both ends of every income range are checked.
"""

import csv
import gzip
from decimal import Decimal
from pathlib import Path

import pytest

from lk_tax import apit_monthly

FIXTURES = Path(__file__).parent / "fixtures"

TABLES = [
    # fixture, a pay date inside its period, last listed income, tax at that income
    ("apit_table01_2324.csv.gz", "2024-06-30", 309_150, 37_794),
    ("apit_table01_2526.csv.gz", "2026-09-30", 366_100, 37_796),
]


def rows(name):
    with gzip.open(FIXTURES / name, "rt") as fh:
        return [(int(r["income_from"]), int(r["income_to"]), int(r["monthly_tax"])) for r in csv.DictReader(fh)]


@pytest.mark.parametrize("fixture,on,last_income,last_tax", TABLES)
def test_every_row_of_the_official_table(fixture, on, last_income, last_tax):
    table = rows(fixture)
    assert table[-1] == (table[-1][0], last_income, last_tax)
    mismatches = [
        (income, tax, apit_monthly(income, on).tax)
        for low, high, tax in table
        for income in (low, high)
        if apit_monthly(income, on).tax != tax
    ]
    assert mismatches == []


@pytest.mark.parametrize("fixture,on,last_income,last_tax", TABLES)
def test_above_the_table_is_last_row_plus_36_percent(fixture, on, last_income, last_tax):
    # The table's last line: "Rs. <last_tax> + 36% of the excess over Rs. <last_income>"
    for excess in (1, 1234, 100_000):
        expected = Decimal(last_tax) + Decimal("0.36") * excess
        assert apit_monthly(last_income + excess, on).tax == expected


def test_ird_table_quirk_at_275000_is_reproduced():
    # The 2025/26 table lists 275,001-275,006 -> 12,501 although the formula
    # already gives 12,502 at 275,005. `tax` follows the table, `exact_tax` the law.
    for income in range(275_001, 275_007):
        assert apit_monthly(income, "2025-04-01").tax == 12_501
    r = apit_monthly(275_005, "2025-04-01")
    assert r.exact_tax == Decimal("12501.20")
    assert apit_monthly(275_007, "2025-04-01").tax == 12_502
