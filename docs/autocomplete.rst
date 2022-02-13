Autocomplete
============

You can use autocomplete to suggest options for your users while they are
typing a command. To do this, flag the option as an Autocomplete option, then
define an autocomplete handler to return the autocomplete results.

Marking an option as autocomplete
---------------------------------

If you're using type hints to define your options, you can use the
:class:`.Autocomplete` class to "wrap" the type of your option, like so:

.. code-block:: python

    @discord.command()
      def autocomplete_example(ctx, country: Autocomplete(str), city: Autocomplete(str)):
          return f"You selected **{city}, {country}**!"

Note that even though this is a type annotation, these are parenthesis, not
brackets. This is due to a limitation in Python.

Alternatively, if you're using the ``options=[]`` parameter, you can set
``autocomplete=True`` on the :class:`.Option` objects.

.. code-block:: python

    @discord.command(
        options=[
            Option(
                name="message",
                type=str,
                description="The message to repeat",
                required=True,
                autocomplete=True,
            ),
        ]
    )
    def repeat_many(ctx, message: string):
        return f"You said, {message}!"

Defining an autocomplete handler
--------------------------------

Autocomplete handlers are functions that take in :class:`.Option` objects and
return a list of autocomplete options. You can either provide a
:class:`.AutocompleteResult` object directly, or one will be generated for
you.

There are two ways to register an autocomplete handler. The simplest is to make use of the :meth:`.Command.autocomplete` decorator, like so:

.. code-block:: python

    @discord.command()
    def more_autocomplete(ctx, value: Autocomplete(int)):
        return f"Your number is **{value}**."


    @more_autocomplete.autocomplete()
    def more_autocomplete_handler(ctx, value=None):
        # Note that even though this option is an int,
        # the autocomplete handler still gets passed a str.
        try:
            value = int(value.value)
        except ValueError:
            return []

        return [i for i in range(value, value + 10)]

.. note::
    Make sure the arguments to your function are optional! If a user isn't
    finished typing a response, then some of the options might not be provided.

You can also use :meth:`.DiscordInteractionsBlueprint.add_autocomplete_handler`
and provide the name of the function you wish to autocomplete.

.. code-block:: python

    @discord.command()
    def autocomplete_example(ctx, country: Autocomplete(str), city: Autocomplete(str)):
        return f"You selected **{city}, {country}**!"


    COUNTRIES = ["Germany", "Canada", "United States", "United Kingdom"]
    CITIES = {
        "Germany": ["Berlin", "Munich", "Frankfurt"],
        "Canada": ["Toronto", "Montreal", "Vancouver"],
        "United States": ["New York", "Chicago", "Los Angeles"],
        "United Kingdom": ["London", "Manchester", "Liverpool"],
    }


    def autocomplete_handler(ctx, country=None, city=None):
        if country.focused:
            return [c for c in COUNTRIES if c.lower().startswith(country.value.lower())]
        elif city.focused:
            if country.value in CITIES:
                return CITIES[country.value]
            else:
                return []


    discord.add_autocomplete_handler(autocomplete_handler, "autocomplete_example")

In your autocomplete handler, you'll receive :class:`.Option` objects. Each one
will have a ``value`` attribute, containing what the user is currently typing,
as well as a ``focused`` attribute, which will be ``True`` for the option that
the user is currently typing in.

Full API
--------

.. autoclass:: flask_discord_interactions.AutocompleteResult
    :members:
