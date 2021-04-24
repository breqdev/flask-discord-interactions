from flask_discord_interactions.response import Response
from flask_discord_interactions.context import Context
from flask_discord_interactions.command import SlashCommandSubgroup


class Client:
    def __init__(self, discord):
        self.discord = discord

    def make_context(self):
        return Context(data={
            "id": 1,
            "channel_id": "",
            "guild_id": "",
            "token": "",
            "data": {
                "id": 1,
                "name": "ping",
                "options": [
                    {
                        "type": 1,
                        "name": "Pong"
                    }
                ]
            },
            "member": {
                "id": 1,
                "nick": "",
                "user": {
                    "id": 1,
                    "username": "test"
                }
            }
        })

    def run(self, *names, **params):
        command = self.discord.discord_commands[names[0]]

        i = 1
        for i in range(1, len(names)):
            if not isinstance(command, SlashCommandSubgroup):
                break
            command = command.subcommands[names[i]]

        return Response.from_return_value(
            command.run(self.make_context(), *names[i:], **params))
