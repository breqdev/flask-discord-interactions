Permissions
===========

Discord allows defining permissions for each application command in a specific guild
or at the global level. Flask-Discord-Interactions provides a Permission class
and two major ways of setting the permissions of a command.

Default member Permissions
--------------------------

This field represents a permission integer like it is used in channel overwrites and role permissions and
determines the permissions a guild member needs to have in order to execute that command.

Let's say you want to have a `/setup` command that is locked to members who have the permissions to manage channels and to manage roles.
The permission integer for this case would be ``268435472``.
A helping hand to calculate that permissions can be found `here <https://finitereality.github.io/permissions-calculator>`_.

By simply putting the number shown above into the ``default_member_permissions``, the command is locked.

.. code-block:: python

    @discord.command(default_member_permissions=268435472)
    def setup(ctx):
        "Only members with channel- and role-managament permissions can run this"

        return "You have the right permissions! Setting up now..."

Setting specific overwrites
---------------------------

.. warning::
   The methods below will require an extra oauth scope granted by a server admin as of discord's rewrite of slash command permissions.
   It's highly recommended to use the ``default_member_permissions`` field instead.

Permission class
^^^^^^^^^^^^^^^^

The :class:`.Permission` class accepts either a role ID or a user ID.

.. autoclass:: flask_discord_interactions.Permission
    :members:


Command constructor
^^^^^^^^^^^^^^^^^^^

You can define permissions when defining a command. These will be
registered immediately after your command is registered.

You can use the ``permissions`` parameter
to specify any overwrites.

.. code-block:: python

    @discord.command(default_permission=False, permissions=[
        Permission(role="786840072891662336")
    ])
    def command_with_perms(ctx):
        "You need a certain role to access this command"

        return "You have permissions!"

Subcommands and Command Groups
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Discord only supports attaching permissions overwrites to top-level commands.
Thus, there is no ``permissions`` parameter for the
:meth:`.SlashCommandGroup.command` decorator. However, you can still set
permissions for an entire tree of subcommands using the
:meth:`.DiscordInteractions.command_group` function.

.. code-block:: python

    group = discord.command_group("group", default_permission=False, permissions=[
        Permission(role="786840072891662336")
    ])

    @group.command()
    def locked_subcommand(ctx):
        "Locked subcommand"

        return "You have unlocked the secret subcommand!"

Context object
^^^^^^^^^^^^^^

You can also use the :meth:`.Context.overwrite_permissions` method to overwrite
the permissions for a command. By default, this is the command currently
invoked. However, you can specify a command name.

.. code-block:: python

    @discord.command(default_permission=False)
    def locked_command(ctx):
        "Secret command that has to be unlocked"

        return "You have unlocked the secret command!"


    @discord.command()
    def unlock_command(ctx):
        "Unlock the secret command"

        ctx.overwrite_permissions(
            [Permission(user=ctx.author.id)], "locked_command")

        return "Unlocked!"

