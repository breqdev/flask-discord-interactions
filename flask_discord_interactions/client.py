from contextlib import contextmanager

from flask_discord_interactions.response import Response
from flask_discord_interactions.context import Context
from flask_discord_interactions.command import SlashCommandSubgroup


class Client:
    """
    A class to represent a mock client that can be used to execute
    Slash Commands programatically without connecting to Discord.

    Attributes
    ----------
    discord
        The DiscordInteractions object to connect to.
    """
    def __init__(self, discord):
        self.discord = discord
        self.current_context = Context()

    @contextmanager
    def context(self, context=None, **kwargs):
        """
        Uses the specified context object for commands run. This is a context
        manager meant to be used with the ``with`` statement.

        Parameters
        ----------
        context
            The :class:`.Context` object to use.
        **kwargs
            Keyword arguments to use to construct the :class:`.Context` object.
        """
        if context:
            self.current_context = context
        elif kwargs:
            self.current_context = Context(**kwargs)
        else:
            self.current_context = Context()
        try:
            yield self.current_context
        finally:
            self.current_context = Context()

    def run(self, *names, **params):
        """
        Run a specified Slash Command.

        Parameters
        ----------
        *names
            The names of the command, subcommand group, and subcommand (if
            present). This may contain just one name (in the case of a
            root-level command), or up to three (for a subcommand inside a
            subcommand group).
        **params
            Options to pass to the command being called.
        """
        command = self.discord.discord_commands[names[0]]

        i = 1
        for i in range(1, len(names)):
            if not isinstance(command, SlashCommandSubgroup):
                break
            command = command.subcommands[names[i]]
        else:
            i += 1

        return Response.from_return_value(
            command.run(self.current_context, *names[i:], **params))
