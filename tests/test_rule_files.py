"""Integrity checks on the rule data itself."""

from datetime import date

import pytest

from lk_tax._core import COVERAGE_START, load_rules


def all_version_lists():
    yield "income_tax", load_rules("income_tax")["versions"]
    yield "vat", load_rules("vat")["versions"]
    yield "sscl", load_rules("sscl")["versions"]
    for key, spec in load_rules("wht").items():
        if not key.startswith("_"):
            yield f"wht.{key}", spec["versions"]


@pytest.mark.parametrize("name,versions", list(all_version_lists()))
def test_versions_are_ordered_and_start_at_coverage(name, versions):
    dates = [v["effective_from"] for v in versions]
    assert all(isinstance(d, date) for d in dates)
    assert dates == sorted(set(dates)), f"{name}: dates must be unique and ascending"
    assert dates[0] == COVERAGE_START, f"{name}: first version must start at coverage start"


@pytest.mark.parametrize("name,versions", list(all_version_lists()))
def test_every_version_cites_an_ird_source(name, versions):
    shared = load_rules("wht")["_sources"]
    for v in versions:
        assert v["sources"], f"{name} {v['effective_from']} has no source"
        for s in v["sources"]:
            url = shared[s]["url"] if isinstance(s, str) else s["url"]
            assert url.startswith("https://www.ird.gov.lk/"), url
