"""Unit tests for doctor.py pure helpers — no Databricks, network, or env files needed."""

import pytest
from doctor import is_placeholder, warehouse_id_from_values


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch):
    # warehouse_id_from_values reads os.getenv first; clear keys so tests are hermetic.
    for key in (
        "DATABRICKS_WAREHOUSE_ID",
        "DATABRICKS_HTTP_PATH",
        "DESTINATION__DATABRICKS__CREDENTIALS__HTTP_PATH",
    ):
        monkeypatch.delenv(key, raising=False)


def test_is_placeholder_detects_templates():
    assert is_placeholder(None)
    assert is_placeholder("")
    assert is_placeholder("YOUR_HOST.cloud.databricks.com")
    assert is_placeholder("https://YOUR_HOST.cloud.databricks.com")
    assert is_placeholder("warehouse-EXAMPLE")
    assert not is_placeholder("dbc-1234.cloud.databricks.com")


def test_warehouse_id_prefers_explicit_value():
    assert warehouse_id_from_values({"DATABRICKS_WAREHOUSE_ID": "abcd1234"}) == "abcd1234"


def test_warehouse_id_derived_from_http_path():
    values = {"DATABRICKS_HTTP_PATH": "/sql/1.0/warehouses/b8e5ba2ff75d1ce5"}
    assert warehouse_id_from_values(values) == "b8e5ba2ff75d1ce5"


def test_warehouse_id_ignores_placeholder_and_falls_back_to_http_path():
    values = {
        "DATABRICKS_WAREHOUSE_ID": "YOUR_WAREHOUSE_ID",
        "DATABRICKS_HTTP_PATH": "/sql/1.0/warehouses/realid123",
    }
    assert warehouse_id_from_values(values) == "realid123"


def test_warehouse_id_none_when_absent():
    assert warehouse_id_from_values({}) is None
