import os
import sys

from flask import Flask

sys.path.insert(1, ".")

from flask_discord_interactions import DiscordInteractions


app = Flask(__name__)
discord = DiscordInteractions(app)

app.config["DISCORD_CLIENT_ID"] = os.environ["DISCORD_CLIENT_ID"]
app.config["DISCORD_PUBLIC_KEY"] = os.environ["DISCORD_PUBLIC_KEY"]
app.config["DISCORD_CLIENT_SECRET"] = os.environ["DISCORD_CLIENT_SECRET"]


answers_localized = {"de": "Welt", "fr": "monde", "da": "verden"}


@discord.command(
    name_localizations={"de": "hallo", "fr": "bonjour", "da": "hej"},
    description_localizations={
        "de": "Hallo Welt",
        "fr": "Bonjour le monde",
        "da": "Hej verden",
    },
)
def hello(ctx):
    """Hello world"""
    return answers_localized.get(ctx.locale, "World")


discord.set_route("/interactions")
discord.update_commands(guild_id=os.environ["TESTING_GUILD"])
if __name__ == "__main__":
    app.run()
