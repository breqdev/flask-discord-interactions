import os
import sys

from flask import Flask

sys.path.insert(1, ".")

from flask_discord_interactions import (DiscordInteractions,  # noqa: E402
                                        Response, Member, Role, Channel)


app = Flask(__name__)
discord = DiscordInteractions(app)

app.config["DISCORD_CLIENT_ID"] = os.environ["DISCORD_CLIENT_ID"]
app.config["DISCORD_PUBLIC_KEY"] = os.environ["DISCORD_PUBLIC_KEY"]
app.config["DISCORD_CLIENT_SECRET"] = os.environ["DISCORD_CLIENT_SECRET"]

discord.update_slash_commands()


# For more complex responses, return an Response object
# You have to define the embed JSON manually for now (see API docs)
# The "ctx" parameter is an Context object
# it works similarly to Context in Discord.py
@discord.command()
def avatar(ctx):
    "Show your user info"
    return Response(embed={
        "title": ctx.author.display_name,
        "description": "Avatar Info",
        "fields": [
            {
                "name": "Member Since",
                "value": ctx.author.joined_at
            },
            {
                "name": "Username",
                "value": (f"**{ctx.author.username}**"
                          f"#{ctx.author.discriminator}")
            },
            {
                "name": "User ID",
                "value": ctx.author.id
            }
        ],
        "image": {"url": ctx.author.avatar_url}
    })


# For User, Channel, and Role options, your function is passed an object
# that provides information about the resource
# You can access data about users with the context object
@discord.command(annotations={"user": "The user to show information about"})
def avatar_of(ctx, user: Member):
    "Show someone else's user info"
    return Response(embed={
        "title": user.display_name,
        "description": "Avatar Info",
        "fields": [
            {
                "name": "Username",
                "value": (f"**{user.username}**"
                          f"#{user.discriminator}")
            },
            {
                "name": "User ID",
                "value": user.id
            }
        ],
        "image": {"url": user.avatar_url}
    })


@discord.command()
def has_role(ctx, user: Member, role: Role):
    if role.id in user.roles:
        return f"Yes, user {user.display_name} has role {role.name}."
    else:
        return f"No, user {user.display_name} does not have role {role.name}."


@discord.command()
def channel_info(ctx, channel: Channel):
    return Response(embed={
        "title": channel.name,
        "fields": [
            {
                "name": "Channel ID",
                "value": channel.id
            }
        ]
    })


discord.set_route("/interactions")
discord.update_slash_commands(guild_id=os.environ["TESTING_GUILD"])


if __name__ == '__main__':
    app.run()
