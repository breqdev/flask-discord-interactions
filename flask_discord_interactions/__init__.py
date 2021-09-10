import warnings
from flask_discord_interactions.command import (
    Command,
    SlashCommandSubgroup,
    SlashCommandGroup
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
    ComponentType,
    SelectMenu,
    SelectMenuOption,
)

from flask_discord_interactions.discord import (
    InteractionType,
    DiscordInteractions,
    DiscordInteractionsBlueprint
)

import flask_discord_interactions.models.embed as embed
from flask_discord_interactions.models import Embed

from flask_discord_interactions.client import Client


# deprecated names
class Message(Message):
    def __init_subclass__(self):
        warnings.warn(
            "Deprecated! Response has been renamed to Message, "
            "as it can now represent the argument to a Message Command."
        )


class SlashCommand(Command):
    def __init_subclass__(self):
        warnings.warn(
            "Deprecated! SlashCommand has been renamed to Command, "
            "as it can represent ChatInput (\"slash\") commands, "
            "user commands, and message commands."
        )


InteractionResponse = Message
InteractionContext = Context


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
    "SelectMenu",
    "SelectMenuOption",
    "Client",
    "Permission",

    "Response",
    "InteractionResponse",
    "InteractionContext"
]
