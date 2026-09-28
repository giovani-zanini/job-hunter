from typing import Any, NamedTuple


class Association(NamedTuple):
    left_field_name: str
    left_field_value: Any
    right_field_name: str
    right_field_value: Any
    left_label: str
    right_label: str


class Message(NamedTuple):
    message: str
    meta: dict | None = None
