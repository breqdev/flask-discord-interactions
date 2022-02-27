import os
import sys

from flask import Flask

# This is just here for the sake of examples testing
# to make sure that the imports work
# (you don't actually need it in your code)
sys.path.insert(1, ".")

from flask_discord_interactions import (
    DiscordInteractions,
    Message,
    Modal,
    TextInput,
    TextStyles,
    ActionRow,
)

app = Flask(__name__)
discord = DiscordInteractions(app)

app.config["DISCORD_CLIENT_ID"] = os.environ["DISCORD_CLIENT_ID"]
app.config["DISCORD_PUBLIC_KEY"] = os.environ["DISCORD_PUBLIC_KEY"]
app.config["DISCORD_CLIENT_SECRET"] = os.environ["DISCORD_CLIENT_SECRET"]


discord.update_commands()


@discord.custom_handler("example_modal")
def modal_callback(ctx):
    msg = (
        f"Hello {ctx.get_component('name').value}! "
        f"So you are {ctx.get_component('age').value} years old "
        "and this is how you describe yourself: "
        f"{ctx.get_component('description').value}"
    )
    return Message(msg, ephemeral=True)


@discord.command(name="test_modal", description="Opens a Modal window")
def modal(ctx):
    fields = [
        ActionRow(
            [
                TextInput(
                    custom_id="name",
                    label="What's your name?",
                    placeholder="John Doe",
                    style=TextStyles.SHORT,
                    required=True,
                )
            ]
        ),
        ActionRow(
            [
                TextInput(
                    custom_id="age",
                    label="What's your age?",
                    style=TextStyles.SHORT,
                    min_length=1,
                    max_length=5,
                    required=False,
                )
            ]
        ),
        ActionRow(
            [
                TextInput(
                    custom_id="description",
                    label="Describe yourself:",
                    value="A very interesting person",
                    style=TextStyles.PARAGRAPH,
                    min_length=10,
                    max_length=2000,
                )
            ]
        ),
    ]
    return Modal("example_modal", "Tell me about yourself", fields)


discord.set_route("/interactions")
discord.update_commands(guild_id=os.environ["TESTING_GUILD"])


if __name__ == "__main__":
    app.run()
