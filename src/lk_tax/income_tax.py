"""Personal income tax (annual) and APIT (the monthly deduction from salary).

The APIT deduction is derived from the annual rules rather than stored
separately: tax on a monthly salary m is the annual tax on 12 x m, divided by
12. That reproduces the IRD's own summary formulas exactly (for 2025/26, "6% of
monthly profits less Rs. 9,000", and so on) from one set of numbers.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import ROUND_CEILING, Decimal

from ._core import Money, MoneyLike, NotCovered, Rule, as_date, cents, load_rules, money, select_version, year_start

_HALF = Decimal("0.5")
_TWELVE = Decimal(12)


@dataclass(frozen=True)
class Band:
    """One slice of income and the tax charged on it."""

    rate: Decimal
    from_amount: Money
    to_amount: Money | None  # None for the open-ended top band
    taxable: Money
    tax: Money


@dataclass(frozen=True)
class IncomeTaxResult:
    year_of_assessment: str
    income: Money
    personal_relief: Money
    taxable_income: Money
    tax: Money
    effective_rate: Decimal
    bands: tuple[Band, ...]
    rule: Rule


@dataclass(frozen=True)
class ApitResult:
    monthly_income: Money
    tax: Money
    """What the official APIT Tax Table No. 01 deducts. Use this for payroll."""
    exact_tax: Money
    """The same formula without the table's whole-rupee steps, to the cent."""
    monthly_relief: Money
    bands: tuple[Band, ...]
    rule: Rule
    on: date


def _rule(on: date) -> Rule:
    return select_version(load_rules("income_tax")["versions"], on)


def _schedule(rule: Rule, scale: Decimal = Decimal(1)) -> tuple[Decimal, list[tuple[Decimal | None, Decimal]]]:
    """Relief and (band size, rate) pairs, scaled (1 for annual, 1/12 for monthly)."""
    data = rule.data
    bands: list[tuple[Decimal | None, Decimal]] = [
        (Decimal(b["size"]) * scale, b["rate"]) for b in data["bands"]
    ]
    bands.append((None, data["top_rate"]))
    return Decimal(data["personal_relief"]) * scale, bands


def _progressive(amount: Decimal, relief: Decimal, bands: list[tuple[Decimal | None, Decimal]]) -> list[Band]:
    result = []
    lower = relief
    remaining = max(amount - relief, Decimal(0))
    for size, rate in bands:
        taxable = remaining if size is None else min(remaining, size)
        upper = None if size is None else lower + size
        result.append(Band(rate=rate, from_amount=lower, to_amount=upper, taxable=taxable, tax=taxable * rate))
        remaining -= taxable
        if upper is not None:
            lower = upper
    return result


def _annual_tax(amount: Decimal, rule: Rule) -> Decimal:
    relief, bands = _schedule(rule)
    return sum((b.tax for b in _progressive(amount, relief, bands)), Decimal(0))


def annual(income: MoneyLike, year: str) -> IncomeTaxResult:
    """Income tax for a resident individual for a year of assessment, e.g. '2025/26'.

    `income` is the total assessable income for the year, before personal relief.
    """
    amount = money(income, "income")
    start = year_start(year)
    if start < date(2023, 4, 1):
        raise NotCovered(
            "Y/A 2022/23 was split across two regimes (rates changed on 1 January 2023); "
            "lk-tax covers annual tax from Y/A 2023/24."
        )
    rule = _rule(start)
    relief, schedule = _schedule(rule)
    bands = _progressive(amount, relief, schedule)
    tax = sum((b.tax for b in bands), Decimal(0))
    label = f"{start.year}/{(start.year + 1) % 100:02d}"
    return IncomeTaxResult(
        year_of_assessment=label,
        income=amount,
        personal_relief=relief,
        taxable_income=max(amount - relief, Decimal(0)),
        tax=cents(tax),
        effective_rate=(tax / amount).quantize(Decimal("0.0001")) if amount else Decimal(0),
        bands=tuple(_display(b) for b in bands if b.taxable),
        rule=rule,
    )


def apit_monthly(monthly_income: MoneyLike, on: date | str | None = None) -> ApitResult:
    """APIT to deduct from a month's regular employment income (Tax Table No. 01).

    Applies to resident employees, and non-resident employees who are Sri Lankan
    citizens, in their primary employment. `on` is the pay date (default: today).
    """
    income = money(monthly_income, "monthly_income")
    when = as_date(on)
    rule = _rule(when)
    exact = _monthly_exact(income, rule)
    relief, schedule = _schedule(rule, 1 / _TWELVE)

    return ApitResult(
        monthly_income=income,
        tax=_table_amount(income, rule),
        exact_tax=cents(exact),
        monthly_relief=cents(relief),
        bands=tuple(_display(b) for b in _progressive(income, relief, schedule) if b.taxable),
        rule=rule,
        on=when,
    )


def _monthly_exact(income: Decimal, rule: Rule) -> Decimal:
    return _annual_tax(income * _TWELVE, rule) / _TWELVE


def _table_amount(income: Decimal, rule: Rule) -> Decimal:
    """Reproduce the whole-rupee steps of the official Tax Table No. 01.

    The IRD builds each row by taking a whole-rupee tax T and ending the income
    range where the formula reaches T, rounded to the nearest rupee. For an
    income m that is the same as rounding the formula at (m - 0.5) up to the
    next rupee. Checked against every row of the 2023/24 and 2025/26 tables.
    Above the table's last row the IRD says "... + 36% of the excess", which is
    the exact formula.
    """
    if income > rule.data["apit_table_max_income"]:
        return cents(_monthly_exact(income, rule))
    if income <= Decimal(rule.data["personal_relief"]) / _TWELVE:
        return cents(Decimal(0))
    for override in rule.data.get("apit_table_overrides", []):
        if override["income_from"] <= income <= override["income_to"]:
            return cents(Decimal(override["tax"]))
    return cents(_monthly_exact(income - _HALF, rule).to_integral_value(rounding=ROUND_CEILING))


def _display(band: Band) -> Band:
    return Band(
        rate=band.rate,
        from_amount=cents(band.from_amount),
        to_amount=None if band.to_amount is None else cents(band.to_amount),
        taxable=cents(band.taxable),
        tax=cents(band.tax),
    )
