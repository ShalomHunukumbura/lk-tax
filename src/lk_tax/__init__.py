"""Sri Lankan tax rules as code, effective-dated and sourced to the Inland Revenue Department.

    >>> import lk_tax
    >>> lk_tax.apit_monthly(350_000, on="2026-09-30").tax
    Decimal('32500.00')
"""

from . import income_tax, sscl, vat, wht
from ._core import COVERAGE_START, NotCovered, Rule, Source, to_dict
from .income_tax import annual as income_tax_annual
from .income_tax import apit_monthly

__version__ = "0.1.0"

__all__ = [
    "COVERAGE_START",
    "NotCovered",
    "Rule",
    "Source",
    "apit_monthly",
    "income_tax",
    "income_tax_annual",
    "sscl",
    "to_dict",
    "vat",
    "wht",
    "__version__",
]
