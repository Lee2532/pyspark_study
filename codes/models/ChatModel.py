from dataclasses import dataclass


@dataclass
class CHATMODEL:
    user_id: str
    nickname: str
    message: str
    channel: str
    create_time: str
