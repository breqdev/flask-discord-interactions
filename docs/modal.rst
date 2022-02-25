Modals
======

You can use modal forms as an alternative form to gather user input.
To do this, you have to return a :class:`.Modal` object instead of a string or a Message as the result of an interaction callback.

Constructing a Modal form
-------------------------

In order to show a Modal to an user, you must return either an instance of Modal class or subclass it yourself.
To construct them, you have to pass a Custom ID, the modal's Title
and the fields, which must be a list of :class:`.ActionRow` s.

.. code-block:: python

    @discord.command()
    def modal_example(ctx):
        fields = [
            ActionRow(
                TextInput(
                    "user_input_name",
                    "Enter your name"
                )
            )
        ]
        return Modal("example_modal", "Hello there", fields)


Defining a modal handler
------------------------

Modal handlers are callbacks that receive :class:`.Context` objects and
can return messages as usual. However, you cannot return another Modal
as the response for a Modal.

They are defined the same way you would register a callback for a Button or another component:

.. code-block:: python

    @discord.command()
    def modal_example(ctx):
        fields = [
            ActionRow(
                [
                    TextInput(
                        "user_input_name",
                        "Enter your name"
                    )
                ]
            )
        ]
        return Modal("example_modal", "Hello there", fields)


    @discord.custom_handler("example_modal")
    def modal_callback(ctx):
        components = ctx.components
        action_row = components[0]
        text_input = action_row["components"][0]
        name = text_input["value"]
        return f"Hello {name}!"

There is also a convenience method for getting a specified component based on the ID:

.. code-block:: python

    @discord.custom_handler("example_modal")
    def modal_callback(ctx):
        text_input = ctx.get_component("user_input_name")
        name = text_input["value"]
        return f"Hello {name}!"

Full API
--------

.. autoclass:: flask_discord_interactions.Modal
    :members:
.. autoclass:: flask_discord_interactions.TextInput
    :members:
