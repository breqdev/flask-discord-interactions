import re
import enum
import inspect
import itertools

from flask_discord_interactions.context import (Context, CommandOptionType,
                                                User, Member, Channel, Role,
                                                AsyncContext)
from flask_discord_interactions.response import Response


class SlashCommand:
    """
    Represents a Slash Command.

    Attributes
    ----------
    command
        Function to call when the slash command is invoked.
    name
        Name for this command (appears in the Discord client). If omitted,
        infers the name based on the name of the function.
    description
        Description for this command (appears in the Discord client). If
        omitted, infers the description based on the docstring of the function,
        or sets the description to "No description".
    options
        Array of options that can be passed to this command. If omitted,
        infers the options based on the function parameters and type
        annotations.
    annotations
        Dictionary of descriptions for each option provided. Use this only if
        you want the options to be inferred from the parameters and type
        annotations. Do not use with ``options``. If omitted, and if
        ``options`` is not provided, option descriptions default to
        "No description".
    default_permission
        Whether the command is enabled by default. Default is True.
    permissions
        List of permission overwrites.
    """

    def __init__(self, command, name, description, options, annotations,
                 default_permission=True, permissions=None):
        self.command = command
        self.name = name
        self.description = description
        self.options = options
        self.annotations = annotations or {}
        self.default_permission = default_permission
        self.permissions = permissions or []

        if self.name is None:
            self.name = command.__name__
        if self.description is None:
            self.description = command.__doc__ or "No description"

        if not 1 <= len(self.name) <= 32:
            raise ValueError(
                f"Error adding command {self.name}: "
                "Command name must be between 1 and 32 characters.")
        if self.name != self.name.lower():
            raise ValueError(
                f"Error adding command {self.name}: "
                "Command name must be fully lowercase. "
                "No UPPERCASE or CamelCase names are allowed.")
        if not re.fullmatch(r"^[\w-]{1,32}$", self.name):
            raise ValueError(
                f"Error adding command {self.name}: "
                "Command name does not match regex. "
                "(Perhaps it contains an invalid character?)")
        if not 1 <= len(self.description) <= 100:
            raise ValueError(
                f"Error adding command {self.name}: "
                "Command description must be between 1 and 100 characters.")

        self.is_async = inspect.iscoroutinefunction(self.command)

        if self.options is None:
            sig = inspect.signature(self.command)

            self.options = []
            for parameter in itertools.islice(
                    sig.parameters.values(), 1, None):

                annotation = parameter.annotation

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
                        parameter.name, "No description"),
                    "type": ptype,
                    "required": (parameter.default == parameter.empty)
                }

                if issubclass(annotation, enum.Enum):
                    choices = []

                    if issubclass(annotation, enum.IntEnum):
                        value_type = int
                    else:
                        value_type = str

                    for name, member in annotation.__members__.items():
                        choices.append({
                            "name": name,
                            "value": value_type(member.value)
                        })

                    option["choices"] = choices

                self.options.append(option)

    def make_context_and_run(self, discord, app, data):
        """
        Creates the :class:`Context` object for an invocation of this slash
        command, then invokes itself.

        Parameters
        ----------
        discord
            The :class:`DiscordInteractions` object used to receive this
            interaction.
        app
            The Flask app used to receive this interaction.
        data
            The incoming interaction data.

        Returns
        -------
        Response
            The response by the command, converted to a Response object.
        """

        if self.is_async:
            context = AsyncContext.from_data(discord, app, data)
        else:
            context = Context.from_data(discord, app, data)
        args, kwargs = context.create_args()

        result = self.run(context, *args, **kwargs)

        return Response.from_return_value(result)

    def run(self, context, *args, **kwargs):
        """
        Invokes the function defining this slash command.

        Parameters
        ----------
        context
            The :class:`Context` object representing the current state.
        *args
            Any subcommands of the current command being called.
        **kwargs
            Any other options in the current invocation.
        """

        return self.command(context, *args, **kwargs)

    def dump(self):
        "Returns this command as a dict for registration with the Discord API."
        return {
            "name": self.name,
            "description": self.description,
            "options": self.options,
            "default_permission": self.default_permission
        }

    def dump_permissions(self):
        return [permission.dump() for permission in self.permissions]


class SlashCommandSubgroup(SlashCommand):
    """
    Represents a Subgroup of :class:`SlashCommand` s.

    Attributes
    ----------
    name
        The name of this subgroup, shown in the Discord client.
    description
        The description of this subgroup, shown in the Discord client.
    is_async
        Whether the subgroup should be considered async (if subcommands
        get an :class:`AsyncContext` instead of a :class:`Context`.)
    """

    def __init__(self, name, description, is_async=False):
        self.name = name
        self.description = description
        self.subcommands = {}

        self.is_async = is_async

    def command(self, name=None, description=None,
                options=None, annotations=None):
        """
        Decorator to create a new Subcommand of this Subgroup.

        Parameters
        ----------
        name
            The name of the command, as displayed in the Discord client.
        description
            The description of the command.
        options
            A list of options for the command, overriding the function's
            keyword arguments.
        annotations
            If ``options`` is not provided, descriptions for each of the
            options defined in the function's keyword arguments.
        """

        def decorator(func):
            nonlocal name, description, options, annotations
            subcommand = SlashCommand(
                func, name, description, options, annotations)
            self.subcommands[subcommand.name] = subcommand
            return func

        return decorator

    @property
    def options(self):
        """
        Returns an array of options that can be passed to this command.
        Computed based on the options of each subcommand or subcommand group.
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
        context
            The :class:`Context` object representing the current state.
        *args
            List of subcommands of the current command group being invoked.
        **kwargs
            Any other options in the current invocation.
        """
        return self.subcommands[subcommands[0]].run(
            context, *subcommands[1:], **kwargs)


class SlashCommandGroup(SlashCommandSubgroup):
    def subgroup(self, name, description="No description", is_async=False):
        """
        Create a new :class:`SlashCommandSubroup`
        (which can contain multiple subcommands)

        Parameters
        ----------
        name
            The name of the subgroup, as displayed in the Discord client.
        description
            The description of the subgroup. Defaults to "No description".
        is_async
            Whether the subgroup should be considered async (if subcommands
            get an :class:`AsyncContext` instead of a :class:`Context`.)
        """

        group = SlashCommandSubgroup(name, description, is_async)
        self.subcommands[name] = group
        return group
