"""Request trace ring buffer tests."""

from test_interface.app.trace import TracingSession


def test_trace_ring_buffer_cap(mocker):
    session = TracingSession(max_entries=2)
    response = mocker.Mock()
    response.status_code = 200
    mocker.patch.object(session.__class__.__bases__[0], "request", return_value=response)

    session.request("GET", "https://a")
    session.request("GET", "https://b")
    session.request("GET", "https://c")

    entries = session.get_trace()
    assert len(entries) == 2
    assert entries[0].url == "https://c"
    assert entries[1].url == "https://b"
