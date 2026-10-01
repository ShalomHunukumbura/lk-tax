"""Withholding tax (WHT) / Advance Income Tax (AIT) deducted by the payer.

Rules from IRD circular SEC/2022/E/03 (effective 1 January 2023) and later
amendments:

- WHT is calculated on the gross amount *excluding VAT*.
- Service fees and rent to residents are only subject to WHT when the total
  paid to that person in the calendar month exceeds Rs. 100,000, and then it
  applies to the full payment.
- If the payer covers the WHT so the payee receives the full invoice amount,
  the invoice is the net amount and WHT is calculated on the grossed-up amount.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from ._core import Money, MoneyLike, Rule, as_date, cents, load_rules, money, select_version


@dataclass(frozen=True)
class WhtResult:
    payment_type: str
    payment_name: str
    gross: Money
    """The amount WHT is calculated on (excluding VAT)."""
    rate: Decimal
    tax: Money
    net_paid: Money
    """What the payee actually receives."""
    applies: bool
    reason: str
    covers: str | None
    rule: Rule
    on: date


def payment_types() -> dict[str, str]:
    """Supported payment types: key -> description."""
    return {key: spec["name"] for key, spec in _types().items()}


def calculate(
    payment_type: str,
    amount: MoneyLike,
    on: date | str | None = None,
    *,
    month_total: MoneyLike | None = None,
    payer_bears_tax: bool = False,
) -> WhtResult:
    """WHT on a single payment.

    amount: the payment excluding VAT (or the net invoice, with payer_bears_tax=True).
    month_total: for service fees and rent, the total paid to this person in the
        calendar month including this payment. Defaults to `amount`.
    payer_bears_tax: the payee receives `amount` in full and the payer pays the
        WHT on top, so WHT is worked out on the grossed-up amount.
    """
    types = _types()
    if payment_type not in types:
        raise ValueError(f"unknown payment type {payment_type!r}; choose from: {', '.join(sorted(types))}")
    spec = types[payment_type]
    when = as_date(on)
    rule = select_version(spec["versions"], when, load_rules("wht")["_sources"])
    rate: Decimal = rule.data["rate"]
    value = money(amount)

    gross = value / (1 - rate) if payer_bears_tax else value
    applies, reason = _applies(rule, gross, month_total, payer_bears_tax)

    if not applies:
        return WhtResult(payment_type, spec["name"], cents(value), rate, Decimal("0.00"), cents(value),
                         False, reason, rule.data.get("covers"), rule, when)

    tax = cents(gross * rate)
    gross = cents(gross)
    return WhtResult(
        payment_type=payment_type,
        payment_name=spec["name"],
        gross=gross,
        rate=rate,
        tax=tax,
        net_paid=gross - tax,
        applies=True,
        reason=reason,
        covers=rule.data.get("covers"),
        rule=rule,
        on=when,
    )


def _applies(rule: Rule, gross: Decimal, month_total: MoneyLike | None, grossed_up: bool) -> tuple[bool, str]:
    data = rule.data
    if "exempt_up_to" in data and gross <= data["exempt_up_to"]:
        return False, f"Exempt: gross amount is not more than Rs. {data['exempt_up_to']:,}."
    if "monthly_threshold" in data:
        threshold = Decimal(data["monthly_threshold"])
        total = gross if month_total is None else money(month_total, "month_total")
        if grossed_up and month_total is not None:
            total = max(total, gross)
        if total <= threshold:
            return False, (
                f"No WHT: total paid to this person this month (Rs. {total:,.2f}) "
                f"does not exceed Rs. {threshold:,}."
            )
        return True, f"Monthly total exceeds Rs. {threshold:,}, so WHT applies to the full payment."
    return True, "WHT applies to the full payment."


def _types() -> dict:
    return {k: v for k, v in load_rules("wht").items() if not k.startswith("_")}
