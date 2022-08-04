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

The :class:`.Permission` class accepts a role ID, user ID, or channel ID, and
represents a permissions override for that role, user, or channel.

.. autoclass:: flask_discord_interactions.Permission
    :members:
