import os
import sys

from flask import Flask

# This is just here for the sake of examples testing
# to make sure that the imports work
# (you don't actually need it in your code)
sys.path.insert(1, ".")

from flask_discord_interactions import (DiscordInteractions,  # noqa: E402
                                        Response, ActionRow, Button,
                                        ButtonStyles, Embed, SelectMenu,
                                        SelectMenuOption)


app = Flask(__name__)
discord = DiscordInteractions(app)

app.config["DISCORD_CLIENT_ID"] = os.environ["DISCORD_CLIENT_ID"]
app.config["DISCORD_PUBLIC_KEY"] = os.environ["DISCORD_PUBLIC_KEY"]
app.config["DISCORD_CLIENT_SECRET"] = os.environ["DISCORD_CLIENT_SECRET"]


discord.update_commands()


# In reality, you'd store these values in a database
# For simplicity, we store them as globals in this example
# Generally, this is a bad idea
# https://stackoverflow.com/questions/32815451/
click_count = 0


# The handler edits the original response by setting update=True
# It sets the action for the button with custom_id
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


# The main command sends the initial Response
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


# You can also return a normal message
@discord.custom_handler()
def handle_upvote(ctx):
    return f"Upvote by {ctx.author.display_name}!"

@discord.custom_handler()
def handle_downvote(ctx):
    return f"Downvote by {ctx.author.display_name}!"


@discord.command()
def voting(ctx, question: str):
    "Vote on something!"

    return Response(
        content=f"The question is: {question}",
        components=[
            ActionRow(components=[
                Button(
                    style=ButtonStyles.SUCCESS,
                    custom_id=handle_upvote,
                    emoji={
                        "name": "⬆️"
                    }
                ),
                Button(
                    style=ButtonStyles.DANGER,
                    custom_id=handle_downvote,
                    emoji={
                        "name": "⬇️",
                    }
                )
            ])
        ]
    )


# Ephemeral messages and embeds work
@discord.custom_handler()
def handle_avatar_view(ctx):
    return Response(
        embed=Embed(
            title=f"{ctx.author.display_name}",
            description=f"{ctx.author.username}#{ctx.author.discriminator}"
        ),
        ephemeral=True
    )

@discord.command()
def username(ctx):
    "Show your username and discriminator"

    return Response(
        content="Show user info!",
        components=[
            ActionRow(components=[
                Button(
                    style=ButtonStyles.PRIMARY,
                    custom_id=handle_avatar_view,
                    label="View User!"
                )
            ])
        ]
    )


# Return nothing for no action
@discord.custom_handler()
def handle_do_nothing(ctx):
    print("Doing nothing...")

@discord.command()
def do_nothing(ctx):
    return Response(
        content="Do nothing",
        components=[
            ActionRow(components=[
                Button(
                    style=ButtonStyles.PRIMARY,
                    custom_id=handle_do_nothing,
                    label="Nothing at all!"
                )
            ])
        ]
    )


# Link buttons don't need a handler
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


# Use a list with the Custom ID to include additional state information
# Optionally specify the type (e.g. int) to automatically convert
@discord.custom_handler()
def handle_stateful(ctx, interaction_id, current_count: int):
    current_count += 1

    return Response(
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

    return Response(
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


discord.set_route("/interactions")
discord.update_commands(guild_id=os.environ["TESTING_GUILD"])


if __name__ == '__main__':
    # Disable threading because of global variables
    app.run(threaded=False)
