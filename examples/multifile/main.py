import os
import sys

from flask import Flask, send_file

sys.path.insert(1, ".")

from flask_discord_interactions import DiscordInteractions  # noqa: E402


app = Flask(__name__)
discord = DiscordInteractions(app)

app.config["DISCORD_CLIENT_ID"] = os.environ["DISCORD_CLIENT_ID"]
app.config["DISCORD_PUBLIC_KEY"] = os.environ["DISCORD_PUBLIC_KEY"]
app.config["DISCORD_CLIENT_SECRET"] = os.environ["DISCORD_CLIENT_SECRET"]

discord.update_slash_commands()


from echo import bp as echo_bp  # noqa: E402
from reverse import bp as reverse_bp  # noqa: E402


discord.register_blueprint(echo_bp)
discord.register_blueprint(reverse_bp)


discord.set_route("/interactions")
discord.update_slash_commands(guild_id=os.environ["TESTING_GUILD"])


# Normal Flask routes work too!
@app.route("/")
def index():
    return send_file("../../LICENSE", mimetype="text/html")


if __name__ == '__main__':
    app.run()
