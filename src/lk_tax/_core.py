"""Shared plumbing: effective-dated rules, money and dates."""

from __future__ import annotations

import sys
from dataclasses import dataclass, field, fields, is_dataclass
from datetime import date
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from functools import cache
from importlib.resources import files
from typing import Any

if sys.version_info >= (3, 11):
    import tomllib
else:  # pragma: no cover
    import tomli as tomllib

Money = Decimal
MoneyLike = int | str | Decimal | float

# Nothing before this date is modelled: it's when the current income tax regime began.
COVERAGE_START = date(2023, 1, 1)


class NotCovered(ValueError):
    """The date or year falls outside the period lk-tax has rules for."""


@dataclass(frozen=True)
class Source:
    title: str
    url: str


@dataclass(frozen=True)
class Rule:
    """The version of a rule that was in force on the requested date."""

    effective_from: date
    effective_to: date | None  # last day in force, or None if still current
    sources: tuple[Source, ...]
    note: str | None = None
    data: dict[str, Any] = field(default_factory=dict, repr=False, compare=False)


@cache
def load_rules(name: str) -> dict[str, Any]:
    text = files("lk_tax.rules").joinpath(f"{name}.toml").read_text(encoding="utf-8")
    return tomllib.loads(text, parse_float=Decimal)


def select_version(
    versions: list[dict[str, Any]], on: date, shared_sources: dict[str, Any] | None = None
) -> Rule:
    """Pick the version whose effective period contains `on`."""
    if on < COVERAGE_START:
        raise NotCovered(f"lk-tax covers {COVERAGE_START.isoformat()} onwards, not {on.isoformat()}.")
    ordered = sorted(versions, key=lambda v: v["effective_from"])
    for i, version in enumerate(ordered):
        nxt = ordered[i + 1]["effective_from"] if i + 1 < len(ordered) else None
        if version["effective_from"] <= on and (nxt is None or on < nxt):
            effective_to = date.fromordinal(nxt.toordinal() - 1) if nxt else None
            return Rule(
                effective_from=version["effective_from"],
                effective_to=effective_to,
                sources=tuple(_source(s, shared_sources) for s in version["sources"]),
                note=version.get("note"),
                data=version,
            )
    raise NotCovered(f"No rule in force on {on.isoformat()}.")


def _source(raw: Any, shared: dict[str, Any] | None) -> Source:
    if isinstance(raw, str):  # a key into a file-level [_sources] table
        if not shared or raw not in shared:
            raise KeyError(f"unknown source reference {raw!r}")
        raw = shared[raw]
    return Source(title=raw["title"], url=raw["url"])


def money(value: MoneyLike, name: str = "amount") -> Money:
    """Convert user input to Decimal without float artefacts, and reject negatives."""
    if isinstance(value, bool):
        raise TypeError(f"{name} must be a number, not a bool")
    try:
        result = Decimal(str(value)) if isinstance(value, float) else Decimal(value)
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError(f"{name} must be a number, got {value!r}") from None
    if not result.is_finite():
        raise ValueError(f"{name} must be a finite number")
    if result < 0:
        raise ValueError(f"{name} cannot be negative")
    return result


def cents(value: Decimal) -> Money:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def as_date(value: date | str | None) -> date:
    if value is None:
        return date.today()
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(value)
    except ValueError:
        raise ValueError(f"dates must look like 2025-04-01, got {value!r}") from None


def year_start(year_of_assessment: str) -> date:
    """'2025/26' or '2025/2026' -> 2025-04-01 (a year of assessment runs April to March)."""
    try:
        first, second = year_of_assessment.split("/")
        start = int(first)
        end = int(second)
    except ValueError:
        raise ValueError(f"year of assessment must look like '2025/26', got {year_of_assessment!r}") from None
    if end % 100 != (start + 1) % 100:
        raise ValueError(f"{year_of_assessment!r} is not a valid year of assessment")
    return date(start, 4, 1)


def to_dict(obj: Any) -> Any:
    """JSON-friendly view of result objects: Decimals become strings, dates ISO."""
    if is_dataclass(obj) and not isinstance(obj, type):
        return {f.name: to_dict(getattr(obj, f.name)) for f in fields(obj) if f.name != "data"}
    if isinstance(obj, Decimal):
        return str(obj)
    if isinstance(obj, date):
        return obj.isoformat()
    if isinstance(obj, (list, tuple)):
        return [to_dict(v) for v in obj]
    if isinstance(obj, dict):
        return {k: to_dict(v) for k, v in obj.items()}
    return obj
