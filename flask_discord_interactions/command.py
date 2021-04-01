from .context import InteractionContext


class SlashCommand:
    def __init__(self, command, name, description, options):
        self.command = command
        self.name = name
        self.description = description
        self.options = options

    def run(self, discord, app, data):
        context = InteractionContext(discord, app, data)
        args, kwargs = context.create_args(
            data["data"], resolved=data["data"].get("resolved"))
        return self.command(context, *args, **kwargs)
