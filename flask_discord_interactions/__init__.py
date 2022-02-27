import warnings
from flask_discord_interactions.command import (
    Command,
    SlashCommandSubgroup,
    SlashCommandGroup,
)

from flask_discord_interactions.context import Context, AsyncContext

from flask_discord_interactions.models import (
    ApplicationCommandType,
    CommandOptionType,
    ChannelType,
    Permission,
    Member,
    User,
    Role,
    Channel,
    Message,
    ResponseType,
    Component,
    ActionRow,
    Button,
    ButtonStyles,
    TextInput,
    TextStyles,
    Modal,
    ComponentType,
    SelectMenu,
    SelectMenuOption,
    Autocomplete,
    AutocompleteResult,
    Option,
)

from flask_discord_interactions.discord import (
    InteractionType,
    DiscordInteractions,
    DiscordInteractionsBlueprint,
)

import flask_discord_interactions.models.embed as embed
from flask_discord_interactions.models import Embed

from flask_discord_interactions.client import Client


class Response(Message):
    def __init__(self, *args, **kwargs):
        warnings.warn(
            "Deprecated! As of v1.1.0, Response has been renamed to Message, "
            "as it can now represent the argument to a Message Command.",
            DeprecationWarning,
            stacklevel=2,
        )
        return super().__init__(*args, **kwargs)


InteractionResponse = Response


class SlashCommand(Command):
    def __init__(self, *args, **kwargs):
        warnings.warn(
            "Deprecated! As of v1.1.0, SlashCommand has been renamed to Command, "
            'as it can represent ChatInput ("slash") commands, '
            "user commands, and message commands.",
            DeprecationWarning,
            stacklevel=2,
        )
        return super().__init__(*args, **kwargs)


class InteractionContext(Context):
    def __init__(self, *args, **kwargs):
        warnings.warn(
            "Deprecated! As of v0.1.5, "
            "InteractionContext has been renamed to Context.",
            DeprecationWarning,
            stacklevel=2,
        )
        return super().__init__(*args, **kwargs)


__all__ = [
    "embed",
    "Command",
    "SlashCommand",
    "SlashCommandSubgroup",
    "SlashCommandGroup",
    "Context",
    "AsyncContext",
    "CommandOptionType",
    "ApplicationCommandType",
    "ChannelType",
    "Member",
    "User",
    "Role",
    "Channel",
    "InteractionType",
    "DiscordInteractions",
    "DiscordInteractionsBlueprint",
    "Message",
    "ResponseType",
    "Embed",
    "Component",
    "ComponentType",
    "ActionRow",
    "Button",
    "ButtonStyles",
    "TextInput",
    "TextStyles",
    "Modal",
    "SelectMenu",
    "SelectMenuOption",
    "Client",
    "Permission",
    "Autocomplete",
    "AutocompleteResult",
    "Response",
    "InteractionResponse",
    "InteractionContext",
    "Option",
]
