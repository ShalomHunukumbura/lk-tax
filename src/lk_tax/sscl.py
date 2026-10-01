"""Social Security Contribution Levy: 2.5% of liable turnover."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from ._core import Money, MoneyLike, Rule, as_date, cents, load_rules, money, select_version


@dataclass(frozen=True)
class LevyResult:
    activity: str
    activity_name: str
    turnover: Money
    liable_share: Decimal
    liable_turnover: Money
    rate: Decimal
    levy: Money
    effective_rate: Decimal
    """Levy as a share of total turnover (rate x liable share)."""
    rule: Rule
    on: date


@dataclass(frozen=True)
class RegistrationResult:
    must_register: bool
    reasons: tuple[str, ...]
    quarter_threshold: Money
    annual_threshold: Money
    rule: Rule
    on: date


def activities() -> dict[str, str]:
    """Supported activities: key -> description."""
    return {key: spec["name"] for key, spec in load_rules("sscl")["activities"].items()}


def levy(turnover: MoneyLike, activity: str, on: date | str | None = None) -> LevyResult:
    """SSCL on the turnover from one activity. `on` is a date in the quarter."""
    specs = load_rules("sscl")["activities"]
    if activity not in specs:
        raise ValueError(f"unknown activity {activity!r}; choose from: {', '.join(specs)}")
    when = as_date(on)
    rule = _rule(when)
    rate: Decimal = rule.data["rate"]
    share: Decimal = specs[activity]["share"]
    value = money(turnover, "turnover")
    liable = value * share
    return LevyResult(
        activity=activity,
        activity_name=specs[activity]["name"],
        turnover=cents(value),
        liable_share=share,
        liable_turnover=cents(liable),
        rate=rate,
        levy=cents(liable * rate),
        effective_rate=rate * share,
        rule=rule,
        on=when,
    )


def registration(
    *,
    quarter_turnover: MoneyLike | None = None,
    turnover_4_quarters: MoneyLike | None = None,
    on: date | str | None = None,
) -> RegistrationResult:
    """Must a person register for SSCL? Uses aggregate turnover, as the Act does."""
    if quarter_turnover is None and turnover_4_quarters is None:
        raise ValueError("give quarter_turnover, turnover_4_quarters, or both")
    when = as_date(on)
    rule = _rule(when)
    quarter_limit = Decimal(rule.data["quarter_threshold"])
    annual_limit = Decimal(rule.data["annual_threshold"])
    reasons = []
    if quarter_turnover is not None and money(quarter_turnover, "quarter_turnover") > quarter_limit:
        reasons.append(f"Turnover for the quarter exceeds Rs. {quarter_limit:,}.")
    if turnover_4_quarters is not None and money(turnover_4_quarters, "turnover_4_quarters") > annual_limit:
        reasons.append(f"Turnover for four consecutive quarters exceeds Rs. {annual_limit:,}.")
    return RegistrationResult(bool(reasons), tuple(reasons), quarter_limit, annual_limit, rule, when)


def _rule(on: date) -> Rule:
    return select_version(load_rules("sscl")["versions"], on)
