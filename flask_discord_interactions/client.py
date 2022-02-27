import copy
from contextlib import contextmanager
from flask_discord_interactions.models.command import ApplicationCommandType

from flask_discord_interactions.models import Message
from flask_discord_interactions.context import Context
from flask_discord_interactions.command import SlashCommandSubgroup


class Client:
    """
    A class to represent a mock client that can be used to execute
    Application Commands programatically without connecting to Discord.

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
        Run a specified Application Command.

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

        if command.type == ApplicationCommandType.CHAT_INPUT:
            i = 1
            for i in range(1, len(names)):
                if not isinstance(command, SlashCommandSubgroup):
                    break
                command = command.subcommands[names[i]]
            else:
                i += 1

            return Message.from_return_value(
                command.run(self.current_context, *names[i:], **params)
            )

        return Message.from_return_value(
            command.run(self.current_context, self.current_context.target)
        )

    def run_handler(self, custom_id, *args):
        """
        Run a specified custom ID handler.

        Parameters
        ----------
        custom_id
            The ID of the handler function to run.
        *args
            Options to pass to the handler being called.
        """

        new_context = copy.deepcopy(self.current_context)

        new_context.custom_id = "\n".join((custom_id, *args))
        new_context.parse_custom_id()

        handler = self.discord.custom_id_handlers[new_context.primary_id]

        args = new_context.create_handler_args(handler)

        response = handler(new_context, *args)
        return Message.from_return_value(response)
