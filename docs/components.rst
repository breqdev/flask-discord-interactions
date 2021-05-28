Message Components
==================


Message components allow you to include clickable buttons in messages from your
bot. The documentation on
`Discord <https://discord.com/developers/docs/interactions/message-components>`_
covers their general use.

To use these components with Flask-Discord-Interactions, you can use the
:class:`.ActionRow` and :class:`.Button` classes.

Link Buttons
------------

Link buttons are the simplest example, as they don't require any special
handling. When the button is clicked, the user is sent to the link.

.. code-block:: python

    from flask_discord_interactions import Response, ActionRow, Button

    @discord.command()
    def google(ctx):
        return Response(
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

These handler functions return a :class:`.Response`, but this response can also
have the ``update`` parameter set. With ``update=True``, the new Response will
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

        return Response(
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

        return Response(
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

Custom IDs
----------

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


Full API
--------

.. autoclass:: flask_discord_interactions.Component
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