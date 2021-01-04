# Flask-Discord-Interactions

This is a Flask extension that lets you write Discord Slash Commands using a decorator syntax similarly to Flask's `@app.route()` or Discord.py's `@bot.command()`.

## Usage

Look in the examples directory for more detailed examples.

```
import os

from flask import Flask
from flask_discord_interactions import DiscordInteractions


app = Flask(__name__)
discord = DiscordInteractions(app)


app.config["DISCORD_CLIENT_ID"] = os.environ["DISCORD_CLIENT_ID"]
app.config["DISCORD_PUBLIC_KEY"] = os.environ["DISCORD_PUBLIC_KEY"]
app.config["DISCORD_CLIENT_SECRET"] = os.environ["DISCORD_CLIENT_SECRET"]


@discord.command()
def ping(ctx):
    "Respond with a friendly 'pong'!"
    return "Pong!"


discord.set_route("/interactions")


discord.clear_slash_commands(guild_id=os.environ["TESTING_GUILD"])
discord.register_slash_commands(guild_id=os.environ["TESTING_GUILD"])


if __name__ == '__main__':
    app.run()
```

## How is this different from `discord-py-slash-command`?

`Discord.py` and `discord-py-slash-command` use a bot user and a websocket to connect to Discord, just like a regular Discord bot. It's a nice way to add support for slash commands to an existing Discord bot, or if you need to use a bot user to manage channels, reactions, etc.

However, for simple bots, using webhooks instead of websockets can let your bot scale better and use less resources. You can deploy a webhook-based bot behind a load balancer and scale it up or down as needed without needing to worry about sharding or dividing up guilds between the app processes.
