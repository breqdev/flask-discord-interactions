import json

from flask_discord_interactions import Context, Member, Message, ApplicationCommandType


def test_context_parsing():
    # Test data taken from
    # https://discord.com/developers/docs/interactions/application-commands#slash-commands-example-interaction

    data = json.loads(
        """
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
    """
    )

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

    with client.context(
        Context(
            author=Member(
                username="Bob", id="1234", discriminator="1234", public_flags=0
            )
        )
    ):
        assert client.run("display_name").content == "Bob"

    with client.context(
        Context(
            author=Member(
                username="Bob",
                id="1234",
                discriminator="1234",
                public_flags=0,
                nick="Dale",
            )
        )
    ):
        assert client.run("display_name").content == "Dale"


def test_ids(discord, client):
    @discord.command()
    def all_ids(ctx):
        return f"{ctx.author.id}/{ctx.channel_id}/{ctx.guild_id}"

    context = Context(
        author=Member(id="01", username="Brooke", discriminator="1234", public_flags=0),
        channel_id="02",
        guild_id="2003",
    )

    with client.context(context):
        assert client.run("all_ids").content == "01/02/2003"


def test_permissions(discord, client):
    @discord.command()
    def is_admin(ctx):
        return "Yes" if (ctx.author.permissions & 8) else "No"

    context = Context(
        author=Member(
            permissions="0",
            id="01",
            username="Brooke",
            discriminator="1234",
            public_flags=0,
        )
    )

    with client.context(context):
        assert client.run("is_admin").content == "No"

    context = Context(
        author=Member(
            permissions="8",
            username="Bob",
            id="1234",
            discriminator="1234",
            public_flags=0,
        )
    )

    with client.context(context):
        assert client.run("is_admin").content == "Yes"


def test_user_command_context_parsing():
    # Test data taken from
    # https://discord.com/developers/docs/interactions/application-commands#user-commands-example-interaction

    data = json.loads(
        """
        {
            "application_id": "775799577604522054",
            "channel_id": "772908445358620702",
            "data": {
                "id": "866818195033292850",
                "name": "context-menu-user-2",
                "resolved": {
                    "members": {
                        "809850198683418695": {
                            "avatar": null,
                            "is_pending": false,
                            "joined_at": "2021-02-12T18:25:07.972000+00:00",
                            "nick": null,
                            "pending": false,
                            "permissions": "246997699136",
                            "premium_since": null,
                            "roles": []
                        }
                    },
                    "users": {
                        "809850198683418695": {
                            "avatar": "afc428077119df8aabbbd84b0dc90c74",
                            "bot": true,
                            "discriminator": "7302",
                            "id": "809850198683418695",
                            "public_flags": 0,
                            "username": "VoltyDemo"
                        }
                    }
                },
                "target_id": "809850198683418695",
                "type": 2
            },
            "guild_id": "772904309264089089",
            "id": "867794291820986368",
            "member": {
                "avatar": null,
                "deaf": false,
                "is_pending": false,
                "joined_at": "2020-11-02T20:46:57.364000+00:00",
                "mute": false,
                "nick": null,
                "pending": false,
                "permissions": "274877906943",
                "premium_since": null,
                "roles": ["785609923542777878"],
                "user": {
                    "avatar": "a_f03401914fb4f3caa9037578ab980920",
                    "discriminator": "6538",
                    "id": "167348773423415296",
                    "public_flags": 1,
                    "username": "ian"
                }
            },
            "token": "UNIQUE_TOKEN",
            "type": 2,
            "version": 1
        }
    """
    )

    context = Context.from_data(data=data)

    assert context.target.id == "809850198683418695"
    assert context.target.display_name == "VoltyDemo"


def test_message_command_context_parsing():
    # Test data taken from
    # https://discord.com/developers/docs/interactions/application-commands#message-commands-example-interaction

    data = json.loads(
        """
        {
            "application_id": "775799577604522054",
            "channel_id": "772908445358620702",
            "data": {
                "id": "866818195033292851",
                "name": "context-menu-message-2",
                "resolved": {
                    "messages": {
                        "867793854505943041": {
                            "attachments": [],
                            "author": {
                                "avatar": "a_f03401914fb4f3caa9037578ab980920",
                                "discriminator": "6538",
                                "id": "167348773423415296",
                                "public_flags": 1,
                                "username": "ian"
                            },
                            "channel_id": "772908445358620702",
                            "components": [],
                            "content": "some message",
                            "edited_timestamp": null,
                            "embeds": [],
                            "flags": 0,
                            "id": "867793854505943041",
                            "mention_everyone": false,
                            "mention_roles": [],
                            "mentions": [],
                            "pinned": false,
                            "timestamp": "2021-07-22T15:42:57.744000+00:00",
                            "tts": false,
                            "type": 0
                        }
                    }
                },
                "target_id": "867793854505943041",
                "type": 3
            },
            "guild_id": "772904309264089089",
            "id": "867793873336926249",
            "member": {
                "avatar": null,
                "deaf": false,
                "is_pending": false,
                "joined_at": "2020-11-02T20:46:57.364000+00:00",
                "mute": false,
                "nick": null,
                "pending": false,
                "permissions": "274877906943",
                "premium_since": null,
                "roles": ["785609923542777878"],
                "user": {
                    "avatar": "a_f03401914fb4f3caa9037578ab980920",
                    "discriminator": "6538",
                    "id": "167348773423415296",
                    "public_flags": 1,
                    "username": "ian"
                }
            },
            "token": "UNIQUE_TOKEN",
            "type": 2,
            "version": 1
        }
    """
    )

    context = Context.from_data(data=data)

    assert context.target.id == "867793854505943041"
    assert context.target.content == "some message"
    assert context.target.timestamp.day == 22
    assert context.target.author.display_name == "ian"


def test_user_command_argument(discord, client):
    @discord.command(type=ApplicationCommandType.MESSAGE)
    def greet(ctx, target):
        return f"Hello, {target.display_name}!"

    with client.context(
        Context(
            target=Member(
                username="Test User", id="1234", discriminator="1234", public_flags=0
            )
        )
    ):
        assert client.run("greet").content == "Hello, Test User!"


def test_message_command_argument(discord, client):
    @discord.command(type=ApplicationCommandType.MESSAGE)
    def repeat(ctx, target):
        return f"I repeat, {target.content.lower()}"

    with client.context(Context(target=Message(content="This is a test."))):
        assert client.run("repeat").content == "I repeat, this is a test."
