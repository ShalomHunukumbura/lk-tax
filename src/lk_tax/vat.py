"""Value Added Tax: adding and extracting VAT, and the registration test."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Literal

from ._core import Money, MoneyLike, Rule, as_date, cents, load_rules, money, select_version

Supply = Literal["standard", "financial_services"]


@dataclass(frozen=True)
class VatResult:
    supply: str
    rate: Decimal
    net: Money
    vat: Money
    gross: Money
    rule: Rule
    on: date


@dataclass(frozen=True)
class RegistrationResult:
    must_register: bool
    reasons: tuple[str, ...]
    period_threshold: Money
    annual_threshold: Money
    rule: Rule
    on: date


def rate(on: date | str | None = None, supply: Supply = "standard") -> Decimal:
    return _rate(_rule(as_date(on)), supply)


def add(net: MoneyLike, on: date | str | None = None, supply: Supply = "standard") -> VatResult:
    """VAT on a price that excludes VAT."""
    when = as_date(on)
    rule = _rule(when)
    r = _rate(rule, supply)
    value = money(net, "net")
    vat = cents(value * r)
    return VatResult(supply, r, cents(value), vat, cents(value) + vat, rule, when)


def extract(gross: MoneyLike, on: date | str | None = None, supply: Supply = "standard") -> VatResult:
    """The VAT inside a VAT-inclusive price, using the tax fraction rate / (1 + rate)."""
    when = as_date(on)
    rule = _rule(when)
    r = _rate(rule, supply)
    value = money(gross, "gross")
    vat = cents(value * r / (1 + r))
    return VatResult(supply, r, cents(value) - vat, vat, cents(value), rule, when)


def registration(
    *,
    period_turnover: MoneyLike | None = None,
    turnover_12_months: MoneyLike | None = None,
    on: date | str | None = None,
) -> RegistrationResult:
    """Must a person register for VAT? (Taxable supplies other than financial services.)

    period_turnover: taxable supplies in the taxable period (a quarter, or a
        month for monthly filers).
    turnover_12_months: taxable supplies in the 12 months then ending.
    """
    if period_turnover is None and turnover_12_months is None:
        raise ValueError("give period_turnover, turnover_12_months, or both")
    when = as_date(on)
    rule = _rule(when)
    data = rule.data
    period_limit = Decimal(data["period_threshold"])
    annual_limit = Decimal(data["annual_threshold"])
    reasons = []

    if period_turnover is not None:
        amount = money(period_turnover, "period_turnover")
        over = amount >= period_limit if data["period_threshold_inclusive"] else amount > period_limit
        if over:
            word = "reaches" if data["period_threshold_inclusive"] else "exceeds"
            reasons.append(f"Taxable supplies for the period {word} Rs. {period_limit:,}.")
    if turnover_12_months is not None:
        amount = money(turnover_12_months, "turnover_12_months")
        if amount > annual_limit:
            reasons.append(f"Taxable supplies for 12 months exceed Rs. {annual_limit:,}.")

    return RegistrationResult(bool(reasons), tuple(reasons), period_limit, annual_limit, rule, when)


def _rule(on: date) -> Rule:
    return select_version(load_rules("vat")["versions"], on)


def _rate(rule: Rule, supply: str) -> Decimal:
    if supply == "standard":
        return rule.data["standard_rate"]
    if supply == "financial_services":
        return rule.data["financial_services_rate"]
    raise ValueError(f"supply must be 'standard' or 'financial_services', not {supply!r}")
