from .context import InteractionContext, CommandOptionType


class SlashCommand:
    def __init__(self, command, name, description, options):
        self.command = command
        self.name = name
        self.description = description
        self.options = options

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

    def run(self, discord, app, data):
        context = InteractionContext(discord, app, data)
        args, kwargs = context.create_args(
            data["data"], resolved=data["data"].get("resolved"))
        return self.command(context, *args, **kwargs)

    def dump(self):
        return {
            "name": self.name,
            "description": self.description,
            "options": self.options
        }


class SlashCommandGroup(SlashCommand):
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.subcommands = {}

    def command(self, name=None, description=None, options=[]):
        "Decorator to create a subcommand"

        def decorator(func):
            nonlocal name, description, options
            subcommand = SlashCommand(func, name, description, options)
            self.subcommands[subcommand.name] = subcommand
            return func

        return decorator

    def run(self, discord, app, data):
        context = InteractionContext(discord, app, data)
        subcommands, kwargs = context.create_args(
            data["data"], resolved=data["data"].get("resolved"))

        return self.subcommands[subcommands[0]].command(
            context, *subcommands[1:], **kwargs)

    @property
    def options(self):
        options = []
        for command in self.subcommands.values():
            data = command.dump()
            data["type"] = CommandOptionType.SUB_COMMAND
            options.append(data)

        return options
