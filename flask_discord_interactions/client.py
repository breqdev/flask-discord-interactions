from contextlib import contextmanager

from flask_discord_interactions.response import Response
from flask_discord_interactions.context import Context
from flask_discord_interactions.command import SlashCommandSubgroup


class Client:
    def __init__(self, discord):
        self.discord = discord
        self.current_context = Context(data={})

    @contextmanager
    def context(self, context=None):
        self.current_context = context
        try:
            yield self.current_context
        finally:
            self.current_context = Context(data={})

    def run(self, *names, **params):
        command = self.discord.discord_commands[names[0]]

        i = 1
        for i in range(1, len(names)):
            if not isinstance(command, SlashCommandSubgroup):
                break
            command = command.subcommands[names[i]]

        return Response.from_return_value(
            command.run(self.current_context, *names[i:], **params))
