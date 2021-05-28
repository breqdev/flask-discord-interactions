import os
import sys

from flask import Flask

# This is just here for the sake of examples testing
# to make sure that the imports work
# (you don't actually need it in your code)
sys.path.insert(1, ".")

from flask_discord_interactions import (DiscordInteractions,  # noqa: E402
                                        Response, ActionRow, Button,
                                        ButtonStyles)


app = Flask(__name__)
discord = DiscordInteractions(app)

app.config["DISCORD_CLIENT_ID"] = os.environ["DISCORD_CLIENT_ID"]
app.config["DISCORD_PUBLIC_KEY"] = os.environ["DISCORD_PUBLIC_KEY"]
app.config["DISCORD_CLIENT_SECRET"] = os.environ["DISCORD_CLIENT_SECRET"]


discord.update_slash_commands()


# In reality, you'd store these values in a database
# For simplicity, we store them as globals in this example
# Generally, this is a bad idea
# https://stackoverflow.com/questions/32815451/
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


discord.set_route("/interactions")
discord.update_slash_commands(guild_id=os.environ["TESTING_GUILD"])


if __name__ == '__main__':
    # Disable threading because of global variables
    app.run(threaded=False)
