"""Build a static version of the web calculator that runs lk-tax in the browser.

The calculator page (src/lk_tax/web/index.html) normally calls the FastAPI app
at /api/... . For static hosting (GitHub Pages) this script injects a small
shim that answers those same /api/... requests by calling lk-tax inside the
browser with Pyodide (Python compiled to WebAssembly). The page itself is not
changed, and nothing the user types is sent to a server.

Usage:
    uv build --wheel
    python scripts/build_static.py dist/lk_tax-<version>-py3-none-any.whl site/
"""

import shutil
import sys
from pathlib import Path

PYODIDE = "https://cdn.jsdelivr.net/pyodide/v314.0.7/full/pyodide.js"
ROOT = Path(__file__).resolve().parent.parent

# Mirrors the routes in lk_tax/api.py, without FastAPI.
ROUTER = r'''
import json
from lk_tax import NotCovered, income_tax, sscl, to_dict, vat, wht

def _flag(value):
    return str(value).lower() in ("1", "true", "yes")

def route(path, query):
    q = dict(query)
    try:
        if path == "/api/apit":
            result = income_tax.apit_monthly(q["income"], q.get("on"))
        elif path == "/api/income-tax":
            result = income_tax.annual(q["income"], q["year"])
        elif path == "/api/wht":
            result = wht.calculate(q["type"], q["amount"], q.get("on"), month_total=q.get("month_total"),
                                   payer_bears_tax=_flag(q.get("payer_bears_tax", "false")))
        elif path == "/api/wht/types":
            return 200, json.dumps(wht.payment_types())
        elif path == "/api/vat":
            fn = vat.add if q.get("mode", "add") == "add" else vat.extract
            result = fn(q["amount"], q.get("on"), q.get("supply", "standard"))
        elif path == "/api/vat/registration":
            result = vat.registration(period_turnover=q.get("period_turnover"),
                                      turnover_12_months=q.get("turnover_12_months"), on=q.get("on"))
        elif path == "/api/sscl":
            result = sscl.levy(q["turnover"], q["activity"], q.get("on"))
        elif path == "/api/sscl/activities":
            return 200, json.dumps(sscl.activities())
        elif path == "/api/sscl/registration":
            result = sscl.registration(quarter_turnover=q.get("quarter_turnover"),
                                       turnover_4_quarters=q.get("turnover_4_quarters"), on=q.get("on"))
        else:
            return 404, json.dumps({"error": f"unknown endpoint {path}"})
        return 200, json.dumps(to_dict(result))
    except KeyError as exc:
        return 422, json.dumps({"error": f"missing parameter {exc}", "kind": "invalid_input"})
    except (ValueError, TypeError) as exc:
        kind = "not_covered" if isinstance(exc, NotCovered) else "invalid_input"
        return 422, json.dumps({"error": str(exc), "kind": kind})
'''

SHIM = """<script src="{pyodide}"></script>
<script>
// Static build: answer the page's /api/... requests with lk-tax running in the
// browser (Pyodide). Nothing typed into the calculator leaves this device.
(() => {{
  const ready = (async () => {{
    // Fetch Pyodide and the wheel in parallel. A wheel is a zip of the package,
    // so unpacking it into site-packages is all "installing" needs here: no
    // micropip download, which roughly halves the first load.
    const [py, wheel] = await Promise.all([
      loadPyodide(),
      fetch(new URL("{wheel}", location.href)).then((r) => r.arrayBuffer()),
    ]);
    py.unpackArchive(wheel, "wheel");
    py.runPython({router});
    return py.globals.get("route");
  }})();
  ready.catch((err) => {{
    document.querySelectorAll(".card").forEach((card) => {{
      card.innerHTML = '<p class="error">Could not start the calculator: ' + String(err).replace(/</g, "&lt;") + "</p>";
    }});
  }});
  const realFetch = window.fetch.bind(window);
  window.fetch = async (input, init) => {{
    const url = new URL(typeof input === "string" ? input : input.url, location.href);
    const at = url.pathname.indexOf("/api/");
    if (url.origin !== location.origin || at === -1) return realFetch(input, init);
    const route = await ready;
    const result = route(url.pathname.slice(at), [...url.searchParams.entries()]);
    const reply = result.toJs();
    result.destroy();
    return new Response(reply[1], {{ status: reply[0], headers: {{ "Content-Type": "application/json" }} }});
  }};
  document.addEventListener("DOMContentLoaded", () => {{
    document.querySelectorAll(".card").forEach((card) => {{
      if (!card.innerHTML.trim()) card.innerHTML = '<p class="note">Loading the calculator. Python is starting in your browser; this takes a few seconds the first time.</p>';
    }});
  }});
}})();
</script>
"""


def main() -> None:
    wheel, out = Path(sys.argv[1]), Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    shutil.copy(wheel, out / wheel.name)

    page = (ROOT / "src" / "lk_tax" / "web" / "index.html").read_text(encoding="utf-8")
    shim = SHIM.format(pyodide=PYODIDE, wheel=wheel.name, router=repr(ROUTER).replace("</", "<\\/"))
    marker = "<script>\nconst $ ="
    if marker not in page:
        raise SystemExit("could not find the calculator script in index.html")
    page = page.replace(marker, shim + marker, 1)

    # There is no /docs API page on static hosting; point at the README instead.
    page = page.replace('<a href="/docs">API</a>', '<a href="https://github.com/ShalomHunukumbura/lk-tax#readme">Docs</a>')
    page = page.replace("Not tax advice.", "Runs entirely in your browser. Not tax advice.")

    (out / "index.html").write_text(page, encoding="utf-8")
    (out / ".nojekyll").write_text("")
    print(f"static site written to {out}/ (wheel: {wheel.name})")


if __name__ == "__main__":
    main()
