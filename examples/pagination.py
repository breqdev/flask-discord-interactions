import os
import sys
import datetime

from flask import Flask

# This is just here for the sake of examples testing
# to make sure that the imports work
# (you don't actually need it in your code)
sys.path.insert(1, ".")

from flask_discord_interactions import (DiscordInteractions,  # noqa: E402
                                        Response, ActionRow, Button,
                                        ButtonStyles, Embed)


app = Flask(__name__)
discord = DiscordInteractions(app)

app.config["DISCORD_CLIENT_ID"] = os.environ["DISCORD_CLIENT_ID"]
app.config["DISCORD_PUBLIC_KEY"] = os.environ["DISCORD_PUBLIC_KEY"]
app.config["DISCORD_CLIENT_SECRET"] = os.environ["DISCORD_CLIENT_SECRET"]


discord.update_commands()


# STATIC PAGINATION

# You could put actual data here
# (help page about your bot, etc)
mock_page_data = [
    {
        "title": f"My Embed {i}",
        "description": f"This is embed number {i}."
    } for i in range(10)
]


# We use the same action rows in both the initial response and the subsequent
# edits. Thus, we can define a helper function to reduce code duplication
def get_page_buttons(*handler):
    # Split into two ActionRows because you can only have 5 buttons per row
    handler = list(handler)

    return [
        ActionRow(components=[
            Button(
                style=ButtonStyles.PRIMARY,
                custom_id=(handler + [i]),
                label=f"Page {i}"
            ) for i in range(5)
        ]),
        ActionRow(components=[
            Button(
                style=ButtonStyles.PRIMARY,
                custom_id=(handler + [i]),
                label=f"Page {i}"
            ) for i in range(5, 10)
        ])
    ]


@discord.custom_handler()
def handle_paginated_static(ctx, pageno: int):

    return Response(
        embed=Embed(**mock_page_data[pageno]),
        components=get_page_buttons(handle_paginated_static),
        update=True
    )


# The main command sends the initial Response
@discord.command()
def paginated_static(ctx):
    "A simple paginated menu with static data"

    return Response(
        embed=Embed(title="Click a button to jump to a page!"),
        components=get_page_buttons(handle_paginated_static)
    )



# DYNAMIC PAGINATION

# Here, you have to store each response on the server-side
# (it probably won't fit into the custom_id state)
response_data = {}

# This is a bad way to store server-side data, you should use an actual
# database, you *will* run into threading issues in production otherwise

@discord.custom_handler()
def handle_paginated_dynamic(ctx, id, pageno: int):
    global response_data

    return Response(
        embed=Embed(**response_data[id][pageno]),
        components=get_page_buttons(handle_paginated_dynamic, id),
        update=True
    )


# The main command sends the initial Response
@discord.command()
def paginated_dynamic(ctx):
    "A simple paginated menu with dynamic data"
    global response_data

    now = datetime.datetime.now()

    # You could put actual data here
    # (fetch user data from a database or API, etc)
    response = [
        {
            "title": f"Custom Response Page {i}",
            "description": (f"Fetched just for {ctx.author.display_name} "
                            f"at {now}!")
        } for i in range(10)
    ]

    response_data[ctx.id] = response

    return Response(
        embed=Embed(**response[0]),
        components=get_page_buttons(handle_paginated_dynamic, ctx.id)
    )


discord.set_route("/interactions")
discord.update_commands(guild_id=os.environ["TESTING_GUILD"])


if __name__ == '__main__':
    app.run(threaded=False)
