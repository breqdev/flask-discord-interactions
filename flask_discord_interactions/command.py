import inspect
import itertools

from .context import (Context, CommandOptionType,
                      User, Member, Channel, Role)


class SlashCommand:
    def __init__(self, command, name, description, options, annotations):
        self.command = command
        self.name = name
        self.description = description
        self.options = options
        self.annotations = annotations or {}

        if self.name is None:
            self.name = command.__name__
        if self.description is None:
            self.description = command.__doc__ or "No description"

        if not 3 <= len(self.name) <= 32:
            raise ValueError(
                f"Error adding command {self.name}: "
                "Command name must be between 3 and 32 characters.")
        if not 1 <= len(self.description) <= 100:
            raise ValueError(
                f"Error adding command {self.name}: "
                "Command description must be between 1 and 100 characters.")

        if self.options is None:
            sig = inspect.signature(self.command)

            self.options = []
            for parameter in itertools.islice(
                    sig.parameters.values(), 1, None):

                if parameter.annotation == int:
                    ptype = CommandOptionType.INTEGER
                elif parameter.annotation == bool:
                    ptype = CommandOptionType.BOOLEAN
                elif parameter.annotation == str:
                    ptype = CommandOptionType.STRING
                elif parameter.annotation in [User, Member]:
                    ptype = CommandOptionType.USER
                elif parameter.annotation == Channel:
                    ptype = CommandOptionType.CHANNEL
                elif parameter.annotation == Role:
                    ptype = CommandOptionType.ROLE
                else:
                    raise ValueError(
                        f"Invalid type annotation {parameter.annotation}")

                option = {
                    "name": parameter.name,
                    "description": self.annotations.get(
                        parameter.name, "No description"),
                    "type": ptype,
                    "required": (parameter.default == parameter.empty)
                }
                self.options.append(option)

    def make_context_and_run(self, discord, app, data):
        context = Context(discord, app, data)
        args, kwargs = context.create_args(
            data["data"], resolved=data["data"].get("resolved"))
        return self.run(context, *args, **kwargs)

    def run(self, context, *args, **kwargs):
        return self.command(context, *args, **kwargs)

    def dump(self):
        return {
            "name": self.name,
            "description": self.description,
            "options": self.options
        }


class SlashCommandSubgroup(SlashCommand):
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.subcommands = {}

    def command(self, name=None, description=None,
                options=None, annotations=None):
        "Decorator to create a subcommand"

        def decorator(func):
            nonlocal name, description, options, annotations
            subcommand = SlashCommand(
                func, name, description, options, annotations)
            self.subcommands[subcommand.name] = subcommand
            return func

        return decorator

    @property
    def options(self):
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
        return self.subcommands[subcommands[0]].run(
            context, *subcommands[1:], **kwargs)


class SlashCommandGroup(SlashCommandSubgroup):
    def make_context_and_run(self, discord, app, data):
        context = Context(discord, app, data)
        subcommands, kwargs = context.create_args(
            data["data"], resolved=data["data"].get("resolved"))

        return self.run(context, *subcommands, **kwargs)

    def subgroup(self, name, description="No description"):
        group = SlashCommandSubgroup(name, description)
        self.subcommands[name] = group
        return group
