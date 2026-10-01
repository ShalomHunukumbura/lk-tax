import pytest
from fastapi.testclient import TestClient

from lk_tax.api import app

client = TestClient(app)


def test_calculator_page():
    r = client.get("/")
    assert r.status_code == 200 and "lk-tax" in r.text


def test_apit_endpoint_returns_amounts_as_strings_and_sources():
    body = client.get("/api/apit", params={"income": "350000", "on": "2026-09-30"}).json()
    assert body["tax"] == "32500.00"
    assert body["rule"]["effective_from"] == "2025-04-01"
    assert body["rule"]["sources"][0]["url"].startswith("https://www.ird.gov.lk/")
    assert "data" not in body["rule"]


def test_income_tax_endpoint():
    assert client.get("/api/income-tax", params={"income": "4000000", "year": "2025/26"}).json()["tax"] == "330000.00"


def test_wht_endpoint():
    body = client.get("/api/wht", params={"type": "service_fee", "amount": "190000", "payer_bears_tax": "true",
                                          "on": "2026-01-01"}).json()
    assert body["gross"] == "200000.00" and body["tax"] == "10000.00"


@pytest.mark.parametrize("mode,vat", [("add", "18.00"), ("extract", "15.25")])
def test_vat_endpoint(mode, vat):
    assert client.get("/api/vat", params={"amount": "100", "mode": mode, "on": "2025-01-01"}).json()["vat"] == vat


def test_sscl_endpoints():
    assert client.get("/api/sscl", params={"turnover": "1000000", "activity": "service", "on": "2025-01-01"}).json()["levy"] == "25000.00"
    reg = client.get("/api/sscl/registration", params={"quarter_turnover": "12000000", "on": "2026-07-01"}).json()
    assert reg["must_register"] is True


def test_lists_and_rules():
    assert "interest" in client.get("/api/wht/types").json()
    assert "manufacture" in client.get("/api/sscl/activities").json()
    assert set(client.get("/api/rules").json()) == {"income_tax", "wht", "vat", "sscl"}


@pytest.mark.parametrize("params,kind", [({"income": "abc"}, "invalid_input"), ({"income": "1", "on": "2020-01-01"}, "not_covered")])
def test_errors_are_readable(params, kind):
    r = client.get("/api/apit", params=params)
    assert r.status_code == 422 and r.json()["kind"] == kind and r.json()["error"]
