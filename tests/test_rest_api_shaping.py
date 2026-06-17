"""Unit tests for the Spark-landing row shaping in rest_api_to_databricks.

These guard the dlt "raw contract": on Databricks serverless the Spark fallback must produce
exactly the snake_case columns (+ _dlt_load_id) that the dbt staging models read, so the fallback
and the real dlt destination stay schema-compatible. This is the drift that bit the live bundle run
(see updates/dlt.md), so it is worth pinning down.
"""

from rest_api_to_databricks import shape_comments, shape_posts


def test_shape_posts_maps_to_raw_contract():
    raw = [{"id": 1, "userId": 7, "title": "t", "body": "b", "ignored": "x"}]
    assert shape_posts(raw, load_id="123.45") == [
        {"id": 1, "user_id": 7, "title": "t", "body": "b", "_dlt_load_id": "123.45"}
    ]


def test_shape_comments_maps_to_raw_contract():
    raw = [{"id": 2, "postId": 1, "name": "n", "email": "e@x.com", "body": "b"}]
    assert shape_comments(raw, load_id="123.45") == [
        {
            "id": 2,
            "post_id": 1,
            "name": "n",
            "email": "e@x.com",
            "body": "b",
            "_dlt_load_id": "123.45",
        }
    ]


def test_shaping_is_empty_for_empty_input():
    assert shape_posts([], "1") == []
    assert shape_comments([], "1") == []
