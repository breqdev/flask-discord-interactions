import json

from flask_discord_interactions import Context, Member

def test_context_parsing(discord):
    # Test data taken from
    # https://discord.com/developers/docs/interactions/receiving-and-responding#receiving-an-interaction

    data = json.loads("""
        {
            "type": 2,
            "token": "A_UNIQUE_TOKEN",
            "member": {
                "user": {
                    "id": "53908232506183680",
                    "username": "Mason",
                    "avatar": "a_d5efa99b3eeaa7dd43acca82f5692432",
                    "discriminator": "1337",
                    "public_flags": 131141
                },
                "roles": ["539082325061836999"],
                "premium_since": null,
                "permissions": "2147483647",
                "pending": false,
                "nick": null,
                "mute": false,
                "joined_at": "2017-03-13T19:19:14.040000+00:00",
                "is_pending": false,
                "deaf": false
            },
            "id": "786008729715212338",
            "guild_id": "290926798626357999",
            "data": {
                "options": [{
                    "name": "cardname",
                    "value": "The Gitrog Monster"
                }],
                "name": "cardsearch",
                "id": "771825006014889984"
            },
            "channel_id": "645027906669510667"
        }
    """)

    context = Context.from_data(data=data)

    assert context.token == "A_UNIQUE_TOKEN"
    assert context.author.id == "53908232506183680"
    assert context.author.roles == ["539082325061836999"]
    assert context.author.display_name == "Mason"
    assert context.command_name == "cardsearch"
    assert context.options[0]["value"] == "The Gitrog Monster"



def test_author(discord, client):
    @discord.command()
    def display_name(ctx):
        return ctx.author.display_name

    with client.context(Context(author=Member(username="Bob"))):
        assert client.run("display_name").content == "Bob"

    with client.context(Context(author=Member(nick="Dale"))):
        assert client.run("display_name").content == "Dale"


def test_ids(discord, client):
    @discord.command()
    def all_ids(ctx):
        return f"{ctx.author.id}/{ctx.channel_id}/{ctx.guild_id}"

    context = Context(author=Member(id="01"), channel_id="02", guild_id="2003")

    with client.context(context):
        assert client.run("all_ids").content == "01/02/2003"


def test_permissions(discord, client):
    @discord.command()
    def is_admin(ctx):
        return "Yes" if (ctx.author.permissions & 8) else "No"

    context = Context(author=Member(permissions="0"))

    with client.context(context):
        assert client.run("is_admin").content == "No"

    context = Context(author=Member(permissions="8"))

    with client.context(context):
        assert client.run("is_admin").content == "Yes"