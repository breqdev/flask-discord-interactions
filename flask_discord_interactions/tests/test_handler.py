from flask_discord_interactions import Message, ActionRow, Button, ButtonStyles


def test_basic_handler(discord, client):
    click_count = 0

    @discord.custom_handler()
    def handle_click(ctx):
        nonlocal click_count
        click_count += 1

        return Message(
            content=f"The button has been clicked {click_count} times",
            components=[
                ActionRow(
                    components=[
                        Button(
                            style=ButtonStyles.PRIMARY,
                            custom_id=handle_click,
                            label="Click Me!",
                        )
                    ]
                )
            ],
            update=True,
        )

    # The main command sends the initial Response
    @discord.command()
    def click_counter(ctx):
        "Count the number of button clicks"

        return Message(
            content=f"The button has been clicked {click_count} times",
            components=[
                ActionRow(
                    components=[
                        Button(
                            style=ButtonStyles.PRIMARY,
                            custom_id=handle_click,
                            label="Click Me!",
                        )
                    ]
                )
            ],
        )

    client.run("click_counter")
    discord.custom_id_handlers[handle_click](None)
    assert click_count == 1


def test_stateful_handler(discord, client):
    @discord.custom_handler()
    def handle_click(ctx, click_count):
        click_count = int(click_count)
        click_count += 1

        return Message(
            content=f"{click_count} clicks",
            components=[
                ActionRow(
                    components=[
                        Button(
                            style=ButtonStyles.PRIMARY,
                            custom_id=[handle_click, click_count],
                            label="Click Me!",
                        )
                    ]
                )
            ],
            update=True,
        )

    # The main command sends the initial Response
    @discord.command()
    def click_counter(ctx):
        "Count the number of button clicks"

        return Message(
            content=f"The button has been clicked 0 times",
            components=[
                ActionRow(
                    components=[
                        Button(
                            style=ButtonStyles.PRIMARY,
                            custom_id=[handle_click, 0],
                            label="Click Me!",
                        )
                    ]
                )
            ],
        )

    client.run("click_counter")
    response = discord.custom_id_handlers[handle_click](None, 0)
    assert response.content == "1 clicks"
