from .context import InteractionContext


class CommandOptionType:
    SUB_COMMAND = 1
    SUB_COMMAND_GROUP = 2
    STRING = 3
    INTEGER = 4
    BOOLEAN = 5
    USER = 6
    CHANNEL = 7
    ROLE = 8


class SlashCommand:
    def __init__(self, command, name, description, options):
        self.command = command
        self.name = name
        self.description = description
        self.options = options

    def create_args(self, data):
        if "options" not in data:
            return [], {}

        args = []
        kwargs = {}
        for option in data["options"]:
            if option["type"] in [
                    CommandOptionType.SUB_COMMAND,
                    CommandOptionType.SUB_COMMAND_GROUP]:
                args.append(option["name"])
                sub_args, sub_kwargs = self.create_args(option)
                args += sub_args
                kwargs.update(sub_kwargs)
            else:
                kwargs[option["name"]] = option["value"]

        return args, kwargs

    def run(self, discord, app, data):
        context = InteractionContext(discord, app, data)
        args, kwargs = self.create_args(data["data"])
        return self.command(context, *args, **kwargs)
