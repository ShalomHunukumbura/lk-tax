"""HTTP API and web calculator. Install with `pip install "lk-tax[api]"`, run with
`uvicorn lk_tax.api:app`.
"""

from __future__ import annotations

from importlib.resources import files
from typing import Literal

try:
    from fastapi import FastAPI, Query, Request
    from fastapi.responses import HTMLResponse, JSONResponse
except ImportError as exc:  # pragma: no cover
    raise ImportError('The lk-tax API needs extra packages: pip install "lk-tax[api]"') from exc

from . import __version__, income_tax, sscl, vat, wht
from ._core import NotCovered, load_rules, to_dict

app = FastAPI(
    title="lk-tax",
    version=__version__,
    description="Sri Lankan tax rules as code. Every answer cites the Inland Revenue Department source it used.",
)

Day = Query(None, description="Date the rules apply to, e.g. 2025-04-01. Defaults to today.")


@app.exception_handler(ValueError)
async def _bad_input(request: Request, exc: ValueError) -> JSONResponse:
    kind = "not_covered" if isinstance(exc, NotCovered) else "invalid_input"
    return JSONResponse(status_code=422, content={"error": str(exc), "kind": kind})


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def calculator() -> str:
    return files("lk_tax.web").joinpath("index.html").read_text(encoding="utf-8")


@app.get("/api/apit", summary="Monthly APIT on regular employment income")
def apit(income: str, on: str | None = Day):
    return to_dict(income_tax.apit_monthly(income, on))


@app.get("/api/income-tax", summary="Annual personal income tax")
def annual(income: str, year: str = Query(..., examples=["2025/26"])):
    return to_dict(income_tax.annual(income, year))


@app.get("/api/wht", summary="Withholding tax on a payment")
def withholding(
    type: str,
    amount: str,
    on: str | None = Day,
    month_total: str | None = None,
    payer_bears_tax: bool = False,
):
    return to_dict(wht.calculate(type, amount, on, month_total=month_total, payer_bears_tax=payer_bears_tax))


@app.get("/api/wht/types", summary="Supported WHT payment types")
def withholding_types():
    return wht.payment_types()


@app.get("/api/vat", summary="Add VAT to, or extract VAT from, an amount")
def value_added(
    amount: str,
    mode: Literal["add", "extract"] = "add",
    supply: Literal["standard", "financial_services"] = "standard",
    on: str | None = Day,
):
    fn = vat.add if mode == "add" else vat.extract
    return to_dict(fn(amount, on, supply))


@app.get("/api/vat/registration", summary="Is VAT registration required?")
def vat_registration(period_turnover: str | None = None, turnover_12_months: str | None = None, on: str | None = Day):
    return to_dict(vat.registration(period_turnover=period_turnover, turnover_12_months=turnover_12_months, on=on))


@app.get("/api/sscl", summary="SSCL on turnover from one activity")
def levy(turnover: str, activity: str, on: str | None = Day):
    return to_dict(sscl.levy(turnover, activity, on))


@app.get("/api/sscl/activities", summary="Supported SSCL activities")
def levy_activities():
    return sscl.activities()


@app.get("/api/sscl/registration", summary="Is SSCL registration required?")
def sscl_registration(quarter_turnover: str | None = None, turnover_4_quarters: str | None = None, on: str | None = Day):
    return to_dict(sscl.registration(quarter_turnover=quarter_turnover, turnover_4_quarters=turnover_4_quarters, on=on))


@app.get("/api/rules", summary="Every rule version, with effective dates and sources")
def rules():
    return {name: to_dict(load_rules(name)) for name in ("income_tax", "wht", "vat", "sscl")}
