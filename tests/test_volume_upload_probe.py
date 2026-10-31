from probe_volume_upload import error_summary


def test_error_summary_redacts_signed_url_query_parameters():
    error = RuntimeError(
        "Connection refused with url: /api/files/rows.json?signature=private-value&userId=123 "
        "(storage gateway refused the connection)"
    )

    summary = error_summary(error)

    assert "private-value" not in summary
    assert "userId=123" not in summary
    assert "/api/files/rows.json?[redacted]" in summary
    assert "storage gateway refused the connection" in summary
