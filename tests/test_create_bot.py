import re
from unittest.mock import Mock

import pytest

from aggregator.bot.create_bot import PostRequest, PostRequestError, get_request_pattern


def test_get_request_pattern():
    post_storage = Mock()
    post_storage.get_all_custom_channel_types = Mock(return_value=["type1", "type2"])

    res = get_request_pattern(post_storage)

    expected = re.compile(r"/(type1|type2|next)(\d{0,5})")

    assert res == expected


@pytest.mark.parametrize(
    ("type_", "amount", "expected"),
    (
        ("type1", "50", PostRequest("type1", 50)),
        ("type2", "104", PostRequest("type2", 100)),
        ("next", "1", PostRequest(None, 1)),
        ("type3", None, PostRequest("type3", 1)),
    ),
)
def test_post_request(type_, amount, expected):
    event = Mock()
    event.pattern_match.group = Mock(side_effect=lambda x: {1: type_, 2: amount}[x])

    res = PostRequest.from_event(event)

    assert res == expected


def test_post_request_bad_format():
    event = Mock()
    event.pattern_match.group = Mock(side_effect=lambda x: {1: None, 2: 10}[x])

    with pytest.raises(PostRequestError):
        PostRequest.from_event(event)
