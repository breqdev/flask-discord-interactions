Message Components
==================


Message components allow you to include clickable buttons and dropdown menus
in messages from your bot. The documentation on
`Discord <https://discord.com/developers/docs/interactions/message-components>`_
covers their general use.

To use these components with Flask-Discord-Interactions, you can use the
:class:`.ActionRow`, :class:`.Button`, and :class:`.SelectMenu` classes.

Link Buttons
------------

Link buttons are the simplest example, as they don't require any special
handling. When the button is clicked, the user is sent to the link.

.. code-block:: python

    from flask_discord_interactions import Message, ActionRow, Button, ButtonStyles

    @discord.command()
    def google(ctx):
        return Message(
            content="search engine",
            components=[
                ActionRow(components=[
                    Button(
                        style=ButtonStyles.LINK,
                        url="https://www.google.com/",
                        label="Go to google"
                    )
                ])
            ]
        )

Link buttons require ``style`` to be set to :attr:`.ButtonStyles.LINK`.

Non-Link Buttons
----------------

Buttons can also send out additional Interactions when clicked. To handle these
additional interactions, Flask-Discord-Interactions requires defining handler
functions.

These handler functions return a :class:`.Message`, but this Message can also
have the ``update`` parameter set. With ``update=True``, the new Message will
replace the original message (the one with the button that triggered the
handler).

You can register a handler using the :meth:`.DiscordInteractions.custom_handler`
decorator, like so:

    In this example, a global variable is used to keep track of the count. This
    is a `bad idea <https://stackoverflow.com/questions/32815451/>`_. You would
    probably use a database for this instead.


.. code-block:: python

    click_count = 0

    @discord.custom_handler()
    def handle_click(ctx):
        global click_count
        click_count += 1

        return Message(
            content=f"The button has been clicked {click_count} times",
            components=[
                ActionRow(components=[
                    Button(
                        style=ButtonStyles.PRIMARY,
                        custom_id=handle_click,
                        label="Click Me!"
                    )
                ])
            ],
            update=True
        )

    @discord.command()
    def click_counter(ctx):
        "Count the number of button clicks"

        return Message(
            content=f"The button has been clicked {click_count} times",
            components=[
                ActionRow(components=[
                    Button(
                        style=ButtonStyles.PRIMARY,
                        custom_id=handle_click,
                        label="Click Me!"
                    )
                ])
            ]
        )

Select Menus
------------

Select Menus will sent an Interaction when a user makes a selection. They function
similarly to Buttons.

The Context object passed to your custom ID handler function will receive an
additional property: :attr:`.Context.values`. This property contains a list of
the values that the user chose.

Defining each individual option can get quite verbose, so an example of this
component is not provided here. However, one is provided in the
`Examples directory <https://github.com/Breq16/flask-discord-interactions/tree/main/examples/select_menus.py>`_.

.. _storing-state-custom-id:

Storing State
-------------

It's possible to include some state information inside the custom ID. This
is a good way to keep your application stateless, which helps with scaling.
However, the total length of the ID must be less than 100 characters, including
the actual handler ID and any additional state you pass along. If you find
yourself exceeding this limit, you should probably be storing that information
in a database.

The
`Discord docs <https://discord.com/developers/docs/interactions/message-components#custom-id>`_
state that:

    This field is a string of max 100 characters, and can be used flexibly to maintain state or pass through other important data.

Flask-Discord-Interactions provides a mechanism to uniquely identify custom
handlers while allowing additional state information to "come along for the
ride." Simply pass a list in for the ``custom_id`` field on the button object.

.. code-block:: python

    @discord.custom_handler()
    def handle_stateful(ctx, interaction_id, current_count: int):
        current_count += 1

        return Message(
            content=(f"This button has been clicked {current_count} times. "
                    "Try calling this command multiple times to see--each button "
                    "count is tracked separately!"),
            components=[
                ActionRow(components=[
                    Button(
                        style=ButtonStyles.PRIMARY,
                        custom_id=[handle_stateful, interaction_id, current_count],
                        label="Click Me!"
                    )
                ])
            ],
            update=True
        )

    @discord.command()
    def stateful_click_counter(ctx):
        "Count the number of button clicks for this specific button."

        return Message(
            content=f"Click the button!",
            components=[
                ActionRow(components=[
                    Button(
                        style=ButtonStyles.PRIMARY,
                        custom_id=[handle_stateful, ctx.id, 0],
                        label="Click Me!"
                    )
                ])
            ]
        )

This example passes two additional values as state: the ID of the interaction,
and the current count of the button.

All values will be converted to a string before including them in the custom
ID. However, to automatically convert them back to a bool or int, you can
include a type annotation in the handler function, such as in the example above
(``current_count: int``).

The `pagination example <https://github.com/Breq16/flask-discord-interactions/blob/main/examples/pagination.py>`_ demonstrates more sophisticated use of this technique to allow a user to jump between multiple pages.

Custom ID Internals
-------------------

Custom IDs are used to uniquely identify a button. Thus, when a web server
receives an incoming interaction, it can use the custom ID to determine what
button triggered it.

Discord allows Custom IDs to be any string that is 100 characters or less
(`relevant docs <https://discord.com/developers/docs/interactions/message-components#custom-id>`_).
However, you may have noticed that the snippets above do not explicitly specify
a custom ID string. Instead, the handler function *appears* to be passed
directly to the ``custom_id`` field. How is this possible?

The trick is, the :meth:`.DiscordInteractions.custom_handler` decorator will
actually generate a custom ID string (a :py:func:`uuid.uuid4`). It will return
this custom ID string in place of the function, after it adds it to the
internal :attr:`.DiscordInteractions.custom_id_handlers` attribute.
This means that the line ``custom_id=handle_click`` is actually passing a
string to the :class:`.Button` constructor.

The reason behind this trickery is to abstract away the details of custom IDs
from the developer. Buttons will just map directly to their handler functions.
However, if you want more control, there is an escape hatch: the
:meth:`.DiscordInteractions.custom_handler` decorator accepts a ``custom_id``
parameter which will override the ID given. Alternatively, you can use the
:meth:`.DiscordInteractions.add_custom_handler` function to avoid the decorator
syntax entirely.


.. warning::
    This strategy works great for development, but can lead to some frustrating
    behavior in production:

    - Every time your app is restarted, old custom handlers will no longer function. This is likely desirable in development, but can cause issues in production.
    - If you deploy multiple instances/workers of your application, then they will not share the same custom IDs. This can lead to many issues, such as failure for one worker to process Interactions related to messages sent on another worker.

    To avoid these issues, it is recommended that you specify a specific custom ID in these scenarios.


Additionally, Flask-Discord-Interactions needs to separate this handler ID
from any additional state that needs to be preserved in the custom ID. To
accomplish this, newlines are inserted into the custom ID string between
the handler and any subsequent values. Later, when the custom ID is received
in an incoming interaction, it is split on the newline character. The first
line is used as the ID, and any subsequent lines are taken as arguments to the
handler function.

Context Internals
-----------------

Just like commands, custom_id handlers are passed a :class:`.Context` object when invoked. This object will also have a :attr:`.Context.message` field containing the :class:`.Message` that contained the component.


Full API
--------

.. autoclass:: flask_discord_interactions.Component
    :members:

|

.. autoclass:: flask_discord_interactions.CustomIdComponent
    :show-inheritance:
    :members:

|

.. autoclass:: flask_discord_interactions.ComponentType
    :members:
    :undoc-members:
    :member-order: bysource

|

.. autoclass:: flask_discord_interactions.ActionRow(**kwargs)
    :show-inheritance:
    :members:
    :undoc-members:

|

.. autoclass:: flask_discord_interactions.Button(**kwargs)
    :show-inheritance:
    :members:
    :undoc-members:

|

.. autoclass:: flask_discord_interactions.ButtonStyles
    :members:
    :undoc-members:
    :member-order: bysource

|

.. autoclass:: flask_discord_interactions.SelectMenu(**kwargs)
    :show-inheritance:
    :members:
    :undoc-members:

|

.. autoclass:: flask_discord_interactions.SelectMenuOption(**kwargs)
    :show-inheritance:
    :members:
    :undoc-members:
