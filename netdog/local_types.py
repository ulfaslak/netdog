from typing import TypedDict


class Tweet(TypedDict):
    author_id: int
    text: str
    id: int
    created_at: str  # ISO8601
