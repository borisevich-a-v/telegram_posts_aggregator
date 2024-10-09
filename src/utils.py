from telethon.tl.types import PeerChannel, PeerChat, PeerUser


def get_entity_id(entity: PeerChannel | PeerChat | PeerUser) -> int:
    match entity:
        case PeerChannel():
            return entity.channel_id
        case PeerChat():
            return entity.chat_id
        case PeerUser():
            return entity.user_id
        case _:
            raise TypeError("Not recognized entity type")
