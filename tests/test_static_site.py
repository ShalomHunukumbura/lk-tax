"""The static (in-browser) calculator must give the same answers as the HTTP API."""

import importlib.util
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from lk_tax.api import app

ROOT = Path(__file__).parent.parent
spec = importlib.util.spec_from_file_location("build_static", ROOT / "scripts" / "build_static.py")
build_static = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build_static)

router: dict = {}
exec(build_static.ROUTER, router)
client = TestClient(app)

REQUESTS = [
    ("/api/apit", {"income": "350000", "on": "2026-09-30"}),
    ("/api/income-tax", {"income": "4000000", "year": "2025/26"}),
    ("/api/wht", {"type": "service_fee", "amount": "190000", "payer_bears_tax": "true", "on": "2026-01-01"}),
    ("/api/wht", {"type": "interest", "amount": "100000", "payer_bears_tax": "false", "on": "2025-03-31"}),
    ("/api/wht/types", {}),
    ("/api/vat", {"amount": "118", "mode": "extract", "supply": "standard", "on": "2025-01-01"}),
    ("/api/vat/registration", {"turnover_12_months": "70000000", "on": "2024-01-01"}),
    ("/api/sscl", {"turnover": "1000000", "activity": "manufacture", "on": "2025-01-01"}),
    ("/api/sscl/activities", {}),
    ("/api/sscl/registration", {"quarter_turnover": "12000000", "on": "2026-07-01"}),
    ("/api/apit", {"income": "abc"}),
    ("/api/apit", {"income": "1", "on": "2020-01-01"}),
]


@pytest.mark.parametrize("path,params", REQUESTS)
def test_browser_router_matches_the_api(path, params):
    status, body = router["route"](path, list(params.items()))
    expected = client.get(path, params=params)
    assert status == expected.status_code
    assert json.loads(body) == expected.json()


def test_build_injects_the_shim(tmp_path):
    wheel = tmp_path / "lk_tax-0.0.0-py3-none-any.whl"
    wheel.write_bytes(b"not really a wheel")
    import sys
    sys.argv = ["build_static.py", str(wheel), str(tmp_path / "site")]
    build_static.main()
    page = (tmp_path / "site" / "index.html").read_text()
    assert "loadPyodide" in page and wheel.name in page
    assert 'href="/docs"' not in page
    assert (tmp_path / "site" / wheel.name).exists() and (tmp_path / "site" / ".nojekyll").exists()
