"""Unit tests for the Spark-landing row shaping in rest_api_to_databricks.

These guard the dlt "raw contract": on Databricks serverless the Spark fallback must produce
exactly the snake_case columns (+ _dlt_load_id) that the dbt staging models read, so the fallback
and the real dlt destination stay schema-compatible. This is the drift that bit the live bundle run
(see updates/dlt.md), so it is worth pinning down.
"""

import sys
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from rest_api_to_databricks import run_with_spark, shape_comments, shape_posts


def test_shape_posts_maps_to_raw_contract():
    raw = [{"id": 1, "userId": 7, "title": "t", "body": "b", "ignored": "x"}]
    (shaped,) = shape_posts(raw, load_id="123.45")
    row_id = shaped.pop("_dlt_id")
    assert row_id  # dlt bookkeeping column must exist so dlt-lane MERGEs stay compatible
    assert shaped == {"id": 1, "user_id": 7, "title": "t", "body": "b", "_dlt_load_id": "123.45"}


def test_shape_comments_maps_to_raw_contract():
    raw = [{"id": 2, "postId": 1, "name": "n", "email": "e@x.com", "body": "b"}]
    (shaped,) = shape_comments(raw, load_id="123.45")
    assert shaped.pop("_dlt_id")
    assert shaped == {
        "id": 2,
        "post_id": 1,
        "name": "n",
        "email": "e@x.com",
        "body": "b",
        "_dlt_load_id": "123.45",
    }


def test_shaping_is_empty_for_empty_input():
    assert shape_posts([], "1") == []
    assert shape_comments([], "1") == []


@pytest.mark.parametrize("fail_second_write", [False, True])
def test_spark_audits_only_after_both_tables_commit(monkeypatch, fail_second_write):
    spark = Mock()
    session = SimpleNamespace(builder=SimpleNamespace(getOrCreate=lambda: spark))
    monkeypatch.setitem(sys.modules, "pyspark.sql", SimpleNamespace(SparkSession=session))
    monkeypatch.setattr("rest_api_to_databricks.fetch_json", lambda _: [])
    writer = spark.createDataFrame.return_value.write.format.return_value
    writer = writer.mode.return_value.option.return_value
    if fail_second_write:
        writer.saveAsTable.side_effect = [None, RuntimeError("second table failed")]
        with pytest.raises(RuntimeError, match="second table failed"):
            run_with_spark("workspace", "raw")
    else:
        run_with_spark("workspace", "raw")

    assert [call.args[0] for call in writer.saveAsTable.call_args_list] == [
        "`workspace`.`raw`.`rest_posts`",
        "`workspace`.`raw`.`rest_comments`",
    ]
    statements = [call.args[0] for call in spark.sql.call_args_list]
    if fail_second_write:
        assert len(statements) == 1  # only CREATE SCHEMA ran
    else:
        assert statements[-1].startswith("INSERT INTO `workspace`.`raw`.ingestion_audit")
        assert "current_timestamp()" in statements[-1]
        assert spark.mock_calls[-1].args[0] == statements[-1]
