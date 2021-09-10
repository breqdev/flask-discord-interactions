import os
import sys

from flask import Flask

sys.path.insert(1, ".")

from flask_discord_interactions import (DiscordInteractions,  # noqa: E402
                                        Response, ActionRow, Embed, SelectMenu,
                                        SelectMenuOption)


app = Flask(__name__)
discord = DiscordInteractions(app)

app.config["DISCORD_CLIENT_ID"] = os.environ["DISCORD_CLIENT_ID"]
app.config["DISCORD_PUBLIC_KEY"] = os.environ["DISCORD_PUBLIC_KEY"]
app.config["DISCORD_CLIENT_SECRET"] = os.environ["DISCORD_CLIENT_SECRET"]


discord.update_commands()


# In your actual app, use an actual database for this!
favorite_colors = {}

@discord.custom_handler()
def handle_favorite_color(ctx):
    favorite_colors[ctx.author.display_name] = ", ".join(ctx.values)
    return make_favorite_color_response(update=True)

def make_favorite_color_response(**kwargs):
    message_embed = Embed(
        title="What is your favorite color?",
        description=(
            "Favorite colors so far: \n" + (
                "\n".join(
                    f"{name}: {color}"
                    for name, color in favorite_colors.items()
                ) or "None yet -- be the first!"
            )
        )
    )

    menu = SelectMenu(
        placeholder="Choose your favorite!",
        custom_id=handle_favorite_color,
        options=[
            SelectMenuOption(
                label="Red",
                value="red",
                description="The color of stop signs 🛑",
                emoji={
                    "name": "🔴"
                }
            ),
            SelectMenuOption(
                label="Green",
                value="green",
                description="The color of plants 🌿",
                emoji={
                    "name": "🟢"
                }
            ),
            SelectMenuOption(
                label="Blue",
                value="blue",
                description="The color of the ocean 🌊",
                emoji={
                    "name": "🔵"
                }
            ),
        ],
        max_values = 2,
    )

    return Response(
        embed=message_embed,
        components=[
            ActionRow(
                components=[menu]
            )
        ],
        **kwargs
    )




@discord.command()
def favorite_color(ctx):
    "Choose your favorite color!"

    return make_favorite_color_response()


discord.set_route("/interactions")
discord.update_commands(guild_id=os.environ["TESTING_GUILD"])


if __name__ == '__main__':
    # Disable threading because of global variables
    app.run(threaded=False)