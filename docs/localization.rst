Localization
============

Using localized commands, you can make your application accessible to more people speaking different languages.
You can localize names, descriptions, options, choices and your responses.

Defining a localized command
----------------------------

Commands and options can be localized via the ``name_localizations`` and ``description_localizations`` fields. For choices, only ``name_localizations`` is settable.

.. code-block:: python

    @discord.command(
        name_localizations={
            "de": "füttern",
            "fr": "nourrir"
        },
        description_localizations={
            "de": "Füttere ein Tier",
            "fr": "Nourrir un animal"
        }
        options=[
            Option(
                type=3,
                required=True
                name="animal"
                name_localizations={
                    "de": "tier",
                    "fr": "animal"
                },
                description="The animal to feed",
                description_localizations={
                    "de": "Das Tier, das gefüttert werden soll",
                    "fr": "L'animal qui sera nourri"
                }
                choices=[
                    Choice(
                        name="Cow",
                        value="cow",
                        name_localizations={
                            "de": "Kuh",
                            "fr": "Vache"
                        }
                    ),
                    Choice(
                        name="Dog",
                        value="dog",
                        name_localizations={
                            "de": "Hund",
                            "fr": "Chien"
                        }
                    ),
                ]
            )
        ]
    )
    def feed(ctx, animal: str):
        """Feed an animal"""
        ...


Localizing your respones
------------------------
You can also localize your respones to the interactions. The context object contains 2 fields for that.
Use ``locale`` and ``guild_locale`` to return your response in the appropriate language.


.. code-block:: python

    @discord.command(
        ...
    )
    def feed(ctx, animal:str):
        """Feed an animal"""
        responses_localized = {
            "de": "Ich habe {animal} gefüttert",
            "fr": "J'ai nourri {animal}"
        }
        return responses_localized.get(ctx.locale, __default=f"I have fed {animal}")

