import os
import sys

from flask import Flask

sys.path.insert(1, ".")

from flask_discord_interactions import DiscordInteractions, Autocomplete


app = Flask(__name__)
discord = DiscordInteractions(app)

app.config["DISCORD_CLIENT_ID"] = os.environ["DISCORD_CLIENT_ID"]
app.config["DISCORD_PUBLIC_KEY"] = os.environ["DISCORD_PUBLIC_KEY"]
app.config["DISCORD_CLIENT_SECRET"] = os.environ["DISCORD_CLIENT_SECRET"]

discord.update_commands()


@discord.command()
def autocomplete_example(ctx, country: Autocomplete(str), city: Autocomplete(str)):
    return f"You selected **{city}, {country}**!"


COUNTRIES = ["Germany", "Canada", "United States", "United Kingdom"]
CITIES = {
    "Germany": ["Berlin", "Munich", "Frankfurt"],
    "Canada": ["Toronto", "Montreal", "Vancouver"],
    "United States": ["New York", "Chicago", "Los Angeles"],
    "United Kingdom": ["London", "Manchester", "Liverpool"],
}


def autocomplete_handler(ctx, country=None, city=None):
    if country.focused:
        return [c for c in COUNTRIES if c.lower().startswith(country.value.lower())]
    elif city.focused:
        if country.value in CITIES:
            return CITIES[country.value]
        else:
            return []


discord.add_autocomplete_handler(autocomplete_handler, "autocomplete_example")

discord.set_route("/interactions")
discord.update_commands(guild_id=os.environ["TESTING_GUILD"])


if __name__ == "__main__":
    app.run()
