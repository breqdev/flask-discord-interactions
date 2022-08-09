import re
import enum
import inspect
import itertools

from typing import Callable, List, Dict, TYPE_CHECKING

from flask import Flask

from flask_discord_interactions.context import Context, AsyncContext
from flask_discord_interactions.models import (
    Message,
    Modal,
    CommandOptionType,
    ApplicationCommandType,
    User,
    Member,
    Channel,
    Role,
    Autocomplete,
    Option,
    Attachment,
)

if TYPE_CHECKING:
    from flask_discord_interactions.discord import DiscordInteractions

_type = type


class Command:
    """
    Represents an Application Command.

    Attributes
    ----------
    command: Callable
        Function to call when the command is invoked.
    name: str
        Name for this command (appears in the Discord client). If omitted,
        infers the name based on the name of the function.
    name_localizations: Dict[str, str]
        Localization dictionary for name field.
    description: str
        Description for this command (appears in the Discord client). If
        omitted, infers the description based on the docstring of the function,
        or sets the description to "No description", if ``ApplicationCommandType``
        is ``CHAT_INPUT``, else set description to ``None``.
    description_localizations: Dict[str, str]
        Localization dictionary for description field.
    options: List[Option]
        Array of options that can be passed to this command. If omitted,
        infers the options based on the function parameters and type
        annotations.
    annotations: Dict[str, str]
        Dictionary of descriptions for each option provided. Use this only if
        you want the options to be inferred from the parameters and type
        annotations. Do not use with ``options``. If omitted, and if
        ``options`` is not provided, option descriptions default to
        "No description".
    type: int
        Type for this command (depend on the action in the Discord client).
        The value is in ``ApplicationCommandType``. If omitted, set the default
        value to ``ApplicationCommandType.CHAT_INPUT``.
    default_member_permissions: int
        A permission integer defining the required permissions a user must have to run the command
    dm_permission: bool
        Indicates whether the command can be used in DMs
    discord: DiscordInteractions
        DiscordInteractionsBlueprint instance which this Command is associated
        with.
    """

    def __init__(
        self,
        command: Callable,
        name: str,
        description: str,
        *,
        options: List[Option],
        annotations: Dict[str, str],
        type: int = ApplicationCommandType.CHAT_INPUT,
        default_member_permissions: int = None,
        dm_permission: bool = None,
        name_localizations: Dict[str, str] = None,
        description_localizations: Dict[str, str] = None,
        discord: "DiscordInteractions" = None,
    ):
        self.command = command
        self.name = name
        self.description = description
        self.options = options
        self.annotations = annotations or {}
        self.type = type
        self.default_member_permissions = default_member_permissions
        self.dm_permission = dm_permission
        self.name_localizations = name_localizations
        self.description_localizations = description_localizations
        self.discord = discord
        self.id = None

        if self.name is None:
            self.name = command.__name__

        if not 1 <= len(self.name) <= 32:
            raise ValueError(
                f"Error adding command {self.name}: "
                "Command name must be between 1 and 32 characters."
            )

        if self.type is ApplicationCommandType.CHAT_INPUT:
            if self.description is None:
                self.description = command.__doc__ or "No description"
            if self.name != self.name.lower():
                raise ValueError(
                    f"Error adding command {self.name}: "
                    "Command name must be fully lowercase. "
                    "No UPPERCASE or CamelCase names are allowed."
                )
            if not re.fullmatch(r"^[\w-]{1,32}$", self.name):
                raise ValueError(
                    f"Error adding command {self.name}: "
                    "Command name does not match regex. "
                    "(Perhaps it contains an invalid character?)"
                )
            if not 1 <= len(self.description) <= 100:
                raise ValueError(
                    f"Error adding command {self.name}: "
                    "Command description must be between 1 and 100 characters."
                )
        else:
            self.description = None

        self.is_async = inspect.iscoroutinefunction(self.command)

        if self.options:
            self.options = [
                (o.dump() if isinstance(o, Option) else o) for o in self.options
            ]

        if self.type is ApplicationCommandType.CHAT_INPUT and self.options is None:
            sig = inspect.signature(self.command)

            self.options = []
            for parameter in itertools.islice(sig.parameters.values(), 1, None):

                annotation = parameter.annotation
                autocomplete = False

                if _type(annotation) == Autocomplete:
                    annotation = annotation.t
                    autocomplete = True

                # Primitive Types
                if annotation == int:
                    ptype = CommandOptionType.INTEGER
                elif annotation == bool:
                    ptype = CommandOptionType.BOOLEAN
                elif annotation == str:
                    ptype = CommandOptionType.STRING
                elif annotation == float:
                    ptype = CommandOptionType.NUMBER

                # Discord Models
                elif annotation in [User, Member]:
                    ptype = CommandOptionType.USER
                elif annotation == Channel:
                    ptype = CommandOptionType.CHANNEL
                elif annotation == Role:
                    ptype = CommandOptionType.ROLE
                elif annotation == Attachment:
                    ptype = CommandOptionType.ATTACHMENT

                # Enums (Used with choices)
                elif issubclass(annotation, enum.IntEnum):
                    ptype = CommandOptionType.INTEGER
                elif issubclass(annotation, enum.Enum):
                    ptype = CommandOptionType.STRING

                else:
                    raise ValueError(f"Invalid type annotation {annotation}")

                option = {
                    "name": parameter.name,
                    "description": self.annotations.get(
                        parameter.name, "No description"
                    ),
                    "type": ptype,
                    "required": (parameter.default == parameter.empty),
                    "autocomplete": autocomplete,
                }

                if issubclass(annotation, enum.Enum):
                    choices = []

                    if issubclass(annotation, enum.IntEnum):
                        value_type = int
                    else:
                        value_type = str

                    for name, member in annotation.__members__.items():
                        choices.append(
                            {"name": name, "value": value_type(member.value)}
                        )

                    option["choices"] = choices

                self.options.append(option)

    def make_context_and_run(
        self, *, discord: "DiscordInteractions", app: Flask, data: dict
    ):
        """
        Creates the :class:`Context` object for an invocation of this
        command, then invokes itself.

        Parameters
        ----------
        discord: DiscordInteractions
            The :class:`DiscordInteractions` object used to receive this
            interaction.
        app: Flask
            The Flask app used to receive this interaction.
        data: dict
            The incoming interaction data.

        Returns
        -------
        Message
            The response by the command, converted to a Message object.
        """

        if self.is_async:
            context = AsyncContext.from_data(discord, app, data)
        else:
            context = Context.from_data(discord, app, data)
        args, kwargs = context.create_args()

        result = self.run(context, *args, **kwargs)

        if isinstance(result, Modal):
            return result
        else:
            return Message.from_return_value(result)

    def run(self, context: Context, *args, **kwargs):
        """
        Invokes the function defining this command.

        Parameters
        ----------
        context: Context
            The :class:`Context` object representing the current state.
        *args
            Any subcommands of the current command being called.
        **kwargs
            Any other options in the current invocation.
        """

        return self.command(context, *args, **kwargs)

    def dump(self):
        "Returns this command as a dict for registration with the Discord API."
        data = {
            "type": self.type,
            "name": self.name,
            "description": self.description,
            "options": self.options,
            "name_localizations": self.name_localizations,
            "description_localizations": self.description_localizations,
        }

        if self.default_member_permissions is not None:
            data["default_member_permissions"] = str(self.default_member_permissions)

        if self.dm_permission is not None:
            data["dm_permission"] = self.dm_permission

        return data

    def autocomplete(self):
        """
        Register an autocomplete handler function for this command.

        Use as a decorator, e.g.

        .. code-block:: python

            @app.command("test")
            def test(ctx, value: str):
                return f"{value}!"

            @test.autocomplete()
            def autocomplete(ctx, value = None):
                return ["hello", "world"]

        """

        def wrapper(f):
            self.discord.add_autocomplete_handler(f, self.name)

        return wrapper


class SlashCommandSubgroup(Command):
    """
    Represents a Subgroup of slash commands.

    Attributes
    ----------
    name: str
        The name of this subgroup, shown in the Discord client.
    name_localizations: Dict[str, str]
        A dict of localized names for this subgroup.
    description: str
        The description of this subgroup, shown in the Discord client.
    description_localizations: Dict[str, str]
        A dict of localized descriptions for this subgroup.
    is_async: bool
        Whether the subgroup should be considered async (if subcommands
        get an :class:`AsyncContext` instead of a :class:`Context`.)
    """

    def __init__(
        self,
        name: str,
        description: str,
        *,
        name_localizations: Dict[str, str] = None,
        description_localizations: Dict[str, str] = None,
        is_async: bool = False,
    ):
        self.name = name
        self.description = description
        self.subcommands = {}
        self.type = ApplicationCommandType.CHAT_INPUT
        self.name_localizations = name_localizations
        self.description_localizations = description_localizations

        self.default_member_permissions = None
        self.dm_permission = None

        self.is_async = is_async

    def command(
        self,
        name: str = None,
        description: str = None,
        *,
        name_localizations: Dict[str, str] = None,
        description_localizations: Dict[str, str] = None,
        options: List[Option] = None,
        annotations: Dict[str, str] = None,
    ):
        """
        Decorator to create a new Subcommand of this Subgroup.

        Parameters
        ----------
        name: str
            The name of the command, as displayed in the Discord client.
        name_localizations: Dict[str, str]
            A dict of localized names for the command.
        description: str
            The description of the command.
        description_localizations: Dict[str, str]
            A dict of localized descriptions for the command.
        options: List[Option]
            A list of options for the command, overriding the function's
            keyword arguments.
        annotations: Dict[str, str]
            If ``options`` is not provided, descriptions for each of the
            options defined in the function's keyword arguments.
        """

        def decorator(func):
            subcommand = Command(
                func,
                name,
                description,
                name_localizations=name_localizations,
                description_localizations=description_localizations,
                options=options,
                annotations=annotations,
            )
            self.subcommands[subcommand.name] = subcommand
            return func

        return decorator

    @property
    def options(self):
        """
        Returns an array of options that can be passed to this command.
        Computed based on the options of each subcommand or subcommand group.

        Returns
        -------
        List[Option]
            The options for this command.
        """
        options = []
        for command in self.subcommands.values():
            data = command.dump()
            if isinstance(command, SlashCommandSubgroup):
                data["type"] = CommandOptionType.SUB_COMMAND_GROUP
            else:
                data["type"] = CommandOptionType.SUB_COMMAND
            options.append(data)

        return options

    def run(self, context, *subcommands, **kwargs):
        """
        Invokes the relevant subcommand for the given :class:`Context`.

        Parameters
        ----------
        context: Context
            The :class:`Context` object representing the current state.
        *args
            List of subcommands of the current command group being invoked.
        **kwargs
            Any other options in the current invocation.
        """
        return self.subcommands[subcommands[0]].run(context, *subcommands[1:], **kwargs)


class SlashCommandGroup(SlashCommandSubgroup):
    """
    Represents a Subgroup of slash commands.

    Attributes
    ----------
    name: str
        The name of this subgroup, shown in the Discord client.
    name_localizations: Dict[str, str]
        A dict of localized names for this subgroup.
    description: str
        The description of this subgroup, shown in the Discord client.
    description_localizations: Dict[str, str]
        A dict of localized descriptions for this subgroup.
    is_async: bool
        Whether the subgroup should be considered async (if subcommands
        get an :class:`AsyncContext` instead of a :class:`Context`.)
    default_member_permissions: int
        Permission integer setting permission defaults for a command
    dm_permission: int
        Indicates whether the command can be used in DMs
    """

    def __init__(
        self,
        name,
        description,
        *,
        is_async=False,
        default_member_permissions=None,
        dm_permission=None,
        name_localizations=None,
        description_localizations=None,
    ):
        self.name = name
        self.description = description
        self.subcommands = {}
        self.type = ApplicationCommandType.CHAT_INPUT

        self.default_member_permissions = default_member_permissions
        self.dm_permission = dm_permission
        self.name_localizations = name_localizations
        self.description_localizations = description_localizations

        self.is_async = is_async

    def subgroup(
        self,
        name: str,
        description: str = "No description",
        *,
        name_localizations: Dict[str, str] = None,
        description_localizations: Dict[str, str] = None,
        is_async: bool = False,
    ):
        """
        Create a new :class:`SlashCommandSubroup`
        (which can contain multiple subcommands)

        Parameters
        ----------
        name: str
            The name of the subgroup, as displayed in the Discord client.
        name_localizations: Dict[str, str]
            A dict of localized names for the subgroup.
        description: str
            The description of the subgroup. Defaults to "No description".
        description_localizations: Dict[str, str]
            A dict of localized descriptions for the subgroup.
        is_async: bool
            Whether the subgroup should be considered async (if subcommands
            get an :class:`AsyncContext` instead of a :class:`Context`.)
        """

        group = SlashCommandSubgroup(
            name,
            description,
            name_localizations=name_localizations,
            description_localizations=description_localizations,
            is_async=is_async,
        )
        self.subcommands[name] = group
        return group
