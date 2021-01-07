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

    def create_kwargs(self, data):
        if "options" not in data["data"]:
            return {}

        kwargs = {}
        for option in data["data"]["options"]:
            kwargs[option["name"]] = option["value"]
        return kwargs

    def run(self, discord, app, data):
        context = InteractionContext(discord, app, data)
        return self.command(context, **self.create_kwargs(data))
