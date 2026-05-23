import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from wissenssystem.domain.namespace import build_namespace, parse_namespace

_SLUG_TEXT = st.text(
    alphabet="abcdefghijklmnopqrstuvwxyz0123456789- ",
    min_size=1,
    max_size=20,
).filter(lambda s: s.strip())


@given(
    manufacturer=_SLUG_TEXT,
    model_family=_SLUG_TEXT,
    sw_version=st.one_of(st.none(), _SLUG_TEXT),
    country=st.text(alphabet="abcdefghijklmnopqrstuvwxyz", min_size=2, max_size=2),
)
@settings(max_examples=20)
def test_roundtrip(manufacturer, model_family, sw_version, country):
    ns = build_namespace(manufacturer, model_family, sw_version, country)
    cfg = parse_namespace(ns)
    assert cfg.namespace == ns
    assert cfg.manufacturer == cfg.manufacturer
    assert cfg.country == cfg.country


@given(
    manufacturer=_SLUG_TEXT,
    model_family=_SLUG_TEXT,
    sw_version=st.one_of(st.none(), _SLUG_TEXT),
    country=st.text(alphabet="abcdefghijklmnopqrstuvwxyz", min_size=2, max_size=2),
)
@settings(max_examples=20)
def test_namespace_starts_with_cfg(manufacturer, model_family, sw_version, country):
    ns = build_namespace(manufacturer, model_family, sw_version, country)
    assert ns.startswith("cfg__")


@given(
    manufacturer=_SLUG_TEXT,
    model_family=_SLUG_TEXT,
    sw_version=st.one_of(st.none(), _SLUG_TEXT),
    country=st.text(alphabet="abcdefghijklmnopqrstuvwxyz", min_size=2, max_size=2),
)
@settings(max_examples=20)
def test_namespace_has_five_parts(manufacturer, model_family, sw_version, country):
    ns = build_namespace(manufacturer, model_family, sw_version, country)
    assert len(ns.split("__")) == 5


def test_known_example():
    ns = build_namespace("Bosch", "UI 800 9kw R290", "NF87.02", "DE")
    assert ns == "cfg__bosch__ui-800-9kw-r290__nf8702__de"
    cfg = parse_namespace(ns)
    assert cfg.manufacturer == "bosch"
    assert cfg.country == "de"


def test_none_sw_version():
    ns = build_namespace("Bosch", "UI 800", None, "DE")
    assert "__none__" in ns
    cfg = parse_namespace(ns)
    assert cfg.software_version is None


def test_parse_invalid_format():
    with pytest.raises(ValueError):
        parse_namespace("invalid-namespace")


def test_parse_wrong_prefix():
    with pytest.raises(ValueError):
        parse_namespace("ns__bosch__ui800__nf87__de")


def test_parse_too_few_parts():
    with pytest.raises(ValueError):
        parse_namespace("cfg__bosch__ui800")
