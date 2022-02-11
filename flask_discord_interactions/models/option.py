from dataclasses import dataclass
from typing import Any

from flask_discord_interactions.models import User, Member, Channel, Role


class CommandOptionType:
    "Represents the different option type integers."
    SUB_COMMAND = 1
    SUB_COMMAND_GROUP = 2
    STRING = 3
    INTEGER = 4
    BOOLEAN = 5
    USER = 6
    CHANNEL = 7
    ROLE = 8
    MENTIONABLE = 9
    NUMBER = 10


@dataclass
class Option:
    name: str
    type: int

    description: str = "No description"
    required: bool = False
    autocomplete: bool = False

    value: Any = None
    focused: bool = None

    def __post_init__(self):
        if isinstance(self.type, type):
            if self.type == str:
                self.type = CommandOptionType.STRING
            elif self.type == int:
                self.type = CommandOptionType.INTEGER
            elif self.type == bool:
                self.type = CommandOptionType.BOOLEAN
            elif self.type in [User, Member]:
                self.type = CommandOptionType.USER
            elif self.type == Channel:
                self.type = CommandOptionType.CHANNEL
            elif self.type == Role:
                self.type = CommandOptionType.ROLE
            elif self.type == float:
                self.type = CommandOptionType.NUMBER
            else:
                raise ValueError(f"Unknown type {self.type}")

    @classmethod
    def from_data(cls, data):
        return cls(
            name=data["name"],
            type=data["type"],
            value=data.get("value"),
            focused=data.get("focused"),
        )

    def dump(self):
        data = {
            "name": self.name,
            "type": self.type,
            "description": self.description,
            "required": self.required,
            "autocomplete": self.autocomplete,
        }
        return data
