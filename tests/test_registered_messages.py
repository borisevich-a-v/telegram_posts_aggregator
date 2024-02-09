from copy import deepcopy
from random import randint
from unittest import mock

from src.registered_messages import RegisteredMessages


def get_test_messages(number: int) -> list[mock.Mock]:
    messages = []
    for _ in range(number):
        msg = mock.Mock()
        msg.id = randint(0, 10**10)
        msg.peer_id.channel_id = randint(0, 10 * 10)
        messages.append(msg)
    return messages


def get_test_message_with_id(id_: int, peer_id: int = 0) -> mock.Mock:
    message = mock.Mock()
    message.id = id_
    message.peer_id.channel_id = peer_id
    return message


def test_contains_same_peer_id():
    message = get_test_message_with_id(42)
    registered_messages = RegisteredMessages()

    registered_messages.add(message)

    assert message in registered_messages
    assert get_test_message_with_id(1337) not in registered_messages


def test_contains_same_id_different_peer_id():
    message_1 = get_test_message_with_id(42, 1)
    message_2 = get_test_message_with_id(42, 2)
    registered_messages = RegisteredMessages()

    registered_messages.add(message_1)

    assert message_1 in registered_messages
    assert message_2 not in registered_messages


def test_add_message():
    message = get_test_message_with_id(42)

    registered_messages = RegisteredMessages()

    registered_messages.add(message)

    assert message in registered_messages


def test_update():
    messages = get_test_messages(3)

    message_1, message_2, message_3 = deepcopy(messages)

    registered_messages = RegisteredMessages()

    registered_messages.update(messages)

    assert message_1 in registered_messages
    assert message_2 in registered_messages
    assert message_3 in registered_messages


def test_rotation():
    """
    Test that we store at least `MIN_NUMBER_OF_STORED_MESSAGE_IDS` and at most `2*MIN_NUMBER_OF_STORED_MESSAGE_IDS`
    """
    rotation_threshold = RegisteredMessages.MIN_NUMBER_OF_STORED_MESSAGE_IDS

    message_1 = get_test_message_with_id(1 * 10**7)
    message_2 = get_test_message_with_id(2 * 10**7)

    registered_messages = RegisteredMessages()

    registered_messages.add(message_1)
    registered_messages.update(get_test_messages(rotation_threshold - 2))
    registered_messages.add(message_2)

    assert message_1 in registered_messages and message_2 in registered_messages

    registered_messages.update(get_test_messages(rotation_threshold + 2))
    assert message_1 not in registered_messages and message_2 not in registered_messages
