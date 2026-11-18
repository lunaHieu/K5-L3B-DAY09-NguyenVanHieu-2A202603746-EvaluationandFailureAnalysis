"""Replay a trace with the exact same claim and seed across two agent shapes."""

import pytest

from lab9.trace_case import investigate

pytestmark = pytest.mark.student


def test_ticket_delay_override_is_the_first_wrong_step():
    broken = investigate("seeded_regression", "C-002", 11)
    fixed = investigate("fixed", "C-002", 11)

    events = broken["trial"]["events"]
    assert [event["kind"] for event in events[:3]] == [
        "handoff", "investigator", "model_override"
    ]
    assert events[1]["payload"]["lookup_order"]["order"]["delay_days"] == 2
    assert events[2]["payload"]["delay_days"] == 5
    assert broken["trial"]["snapshot"]["refund_vnd"] == 20000
    assert broken["label"]["refund_vnd"] == 0
    assert broken["trial"]["lab8_pass"] is False

    assert not any(event["kind"] == "model_override" for event in fixed["trial"]["events"])
    assert fixed["trial"]["snapshot"]["refund_vnd"] == 0
    assert fixed["trial"]["lab8_pass"] is True
