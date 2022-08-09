from dataclasses import dataclass
from typing import Any, Optional, Union

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
    ATTACHMENT = 11


@dataclass
class Option:
    """
    Represents an option provided to a slash command.

    Parameters
    ----------
    name
        The name of the option.
    name_localizations
        A dict of localizations for the name of the option.
    type
        The type of the option. Provide either a value of
        :class:`.CommandOptionType` or a type (e.g. ``str``).
    description
        The description of the option. Defaults to "No description."
    description_localizations
        A dict of localizations for the description of the option.
    required
        Whether the option is required. Defaults to ``False``.
    options:
        A list of further options if the option is a subcommand or a subcommand group.
    choices
        A list of choices for the option.
    channel_types:
        A list of :class:`.ChannelType` for the option.
    min_value
        The minimum value of the option if the option is numeric.
    max_value
        The maximum value of the option if the option is numeric.
    min_length
        Minimum allowed length for string type options.
    max_value
        Maximum allowed length for string type options.
    autocomplete
        Whether the option should be autocompleted. Defaults to ``False``.
        Set to ``True`` if you have an autocomplete handler for this command.
    value
        Only present on incoming options passed to autocomplete objects. You
        shouldn't set this yourself. Represents the value that the user is
        currently typing.
    focused
        Only present on incoming options passed to autocomplete objects. True
        if the user is currently typing this option.
    """

    name: str
    type: int

    description: str = "No description"
    required: bool = False
    options: Optional[list] = None
    choices: Optional[list] = None
    channel_types: Optional[list] = None
    min_value: Optional[int] = None
    max_value: Optional[int] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    name_localizations: Optional[dict] = None
    description_localizations: Optional[dict] = None

    autocomplete: bool = False

    value: Any = None
    focused: Optional[bool] = None

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
    def from_data(cls, data: dict):
        """
        Load this option from incoming Interaction data.
        """
        return cls(
            name=data["name"],
            type=data["type"],
            value=data.get("value"),
            focused=data.get("focused"),
        )

    def dump(self):
        """
        Return this option as as a dict for registration with Discord.

        Returns
        -------
        dict
            A dict representing this option.
        """
        data = {
            "name": self.name,
            "name_localizations": self.name_localizations,
            "type": self.type,
            "description": self.description,
            "description_localizations": self.description_localizations,
            "required": self.required,
            "options": self.options,
            "channel_types": self.channel_types,
            "min_value": self.min_value,
            "max_value": self.max_value,
            "min_length": self.min_length,
            "max_length": self.max_length,
            "autocomplete": self.autocomplete,
        }
        if self.choices is not None:
            data["choices"] = [
                (c.dump() if isinstance(c, Choice) else c) for c in self.choices
            ]
        return data


@dataclass
class Choice:
    """
    Represents an option choice. These can be directly set in the command or returned as autocomplete results
    name
        Name of the choice
    value
        Value of the choice
    name_localizations
        A dict of localizations for the name of the choice.
    """

    name: str
    value: Union[str, int]
    name_localizations: Optional[dict] = None

    def dump(self):
        """
        Return this choice as a dict for registration with Discord.

        Returns
        -------
        dict
            A dict representing this choice.
        """
        data = {
            "name": self.name,
            "value": self.value,
            "name_localizations": self.name_localizations,
        }
        return data
