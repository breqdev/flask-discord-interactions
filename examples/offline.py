import os
import sys

from flask import Flask

# This is just here for the sake of examples testing
# to make sure that the imports work
# (you don't actually need it in your code)
sys.path.insert(1, ".")

from flask_discord_interactions import DiscordInteractions  # noqa: E402


app = Flask(__name__)
discord = DiscordInteractions(app)

# Find these in your Discord Developer Portal, store them as environment vars
app.config["DISCORD_CLIENT_ID"] = os.environ["DISCORD_CLIENT_ID"]
app.config["DISCORD_PUBLIC_KEY"] = os.environ["DISCORD_PUBLIC_KEY"]
app.config["DISCORD_CLIENT_SECRET"] = os.environ["DISCORD_CLIENT_SECRET"]

# Disable incoming message signature validation
app.config["DONT_VALIDATE_SIGNATURE"] = True
# Disable registering with Discord API
app.config["DONT_REGISTER_WITH_DISCORD"] = True


# Clear any existing global application commands
discord.update_commands()


# Simplest type of command: respond with a string
@discord.command()
def ping(ctx, pong: str = 'pong'):
    f"Respond with a friendly 'pong'!"
    return f"{pong} with no signature verification!"


# This is the URL that your app will listen for Discord Interactions on
# Put this into the developer portal
discord.set_route("/interactions")


# Note that with DONT_REGISTER_WITH_DISCORD set this method
# will return without registering with the Discord API
discord.update_commands(guild_id=os.environ["TESTING_GUILD"])


if __name__ == '__main__':
    app.run()
