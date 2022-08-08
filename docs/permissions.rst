Permissions
===========

Discord allows defining permissions for each application command in a specific
guild or at the global level. Global permissions, or *Default Member
Permissions*, control the permissions a guild member must have to execute the
command by default.

Guild-level permissions, or *Permission Overrides*, are used to further
customize command permissions on a per-guild basis. To set these overrides,
your bot needs a Bearer token with the
"applications.commands.permissions.update" OAuth2 scope from a user in the
guild with the "Manage Roles" and "Manage Guild" permissions. Handling this is
mostly outside the scope of this library, although a few helpers are provided.
Consult the `Discord documentation <https://discord.com/developers/docs/interactions/application-commands#permissions>`_ for more information.

Permissions can only be set on top-level commands. If you set a permission
on a command group, it will be applied to all subgroups and subcommands within.

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
   If you can, it's recommended to use the ``default_member_permissions`` field instead.

This library provides methods to get and set permission overwrites: :meth:`.DiscordInteractions.get_permission_overwrites` and :meth:`.DiscordInteractions.set_permission_overwrites`, respectively.

Setting the permission overwrites requires the application ID, guild ID, command ID, Bearer token, and relevant :class:`.Permission` list.
To accommodate a variety of application architectures, there are several ways to pass in these parameters.

- The Application ID can be either retrieved from a :class:`flask.Flask` object bound to the :class:`.DiscordInteractions` instance, the ``app`` parameter, or by manually providing ``application_id`` and ``base_url``.
- The Guild ID must be specified with ``guild_id``.
- The Command ID can be either retrieved from a :class:`.Command` or by manually providing ``command_id``.
- The Bearer token can be either provided with ``token``, or the bot's token can be used if the method has access to the :class:`flask.Flask` app. Note that there are some :ref:`caveats <overwrite-token-caveats>` to this.
- For the setting method, the :class:`.Permission` objects must be supplied with the ``permissions`` parameter.


.. code-block:: python

    # Without the app or instance, useful in a background worker
    DiscordInteractions.get_permission_overwrites(
        guild_id=...,
        command_id=...,
        token=...,
        application_id=...,
        base_url=...,
    )

    # With the instance and app passed in, useful in an app-factory project
    discord.get_permission_overwrites(
        guild_id=...,
        command=...,
        token=...,
        app=...,
    )

    # With the instance and a bound app, using an implicit token
    # useful in most small projects
    discord.get_permission_overwrites(
        guild_id=...,
        command=...,
    )

.. _overwrite-token-caveats:

Caveats of using the bot's own token for permission overwrites
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If the token is omitted, the bot's token will be used.
Note that this only works if the bot's developer account is an admin in the guild.
This is handy for small bots on your own servers, but you shouldn't rely on this for anything you want others to use in their servers.

You'll also need to explicitly add the ``applications.commands.permissions.update`` scope:

.. code-block:: python

    app.config[
        "DISCORD_SCOPE"
    ] = "applications.commands.update applications.commands.permissions.update"

Permission class
----------------

The :class:`.Permission` class accepts a role ID, user ID, or channel ID, and
represents a permissions override for that role, user, or channel.

.. autoclass:: flask_discord_interactions.Permission
    :members:
