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


@discord.command()
def click_counter(ctx):
    "Count the number of button clicks"

    count = 0

    return Response(
        content=f"The button has been clicked {count} times",
        components=[
            ActionRow(components=[
                Button(
                    style=ButtonStyles.PRIMARY,
                    custom_id="my_test_button",
                    label="Click Me!"
                )
            ])
        ]
    )


@discord.command()
def voting(ctx):
    "Count the number of button clicks"

    upvotes = 0
    downvotes = 0

    return Response(
        content=f"{upvotes} upvotes, {downvotes} downvotes",
        components=[
            ActionRow(components=[
                Button(
                    style=ButtonStyles.SUCCESS,
                    custom_id="voting_upvote",
                    emoji={
                        "name": "⬆️"
                    }
                ),
                Button(
                    style=ButtonStyles.DANGER,
                    custom_id="voting_downvote",
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
    app.run()
