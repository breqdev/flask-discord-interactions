import json

import pytest

from flask_discord_interactions import Message, ResponseType, Embed, embed


def test_content(discord, client):
    @discord.command()
    def content(ctx):
        return "quality content"

    assert client.run("content").content == "quality content"


def test_dict_embed(discord, client):
    my_embed = {"title": "My Cool Embed"}

    @discord.command()
    def embeddy(ctx):
        return Message(embed=my_embed)

    assert client.run("embeddy").dump_embeds() == [my_embed]

    @discord.command()
    def multiple(ctx):
        return Message(embeds=[my_embed, my_embed])

    assert client.run("multiple").dump_embeds() == [my_embed, my_embed]


def test_class_embed(discord, client):
    my_embed = Embed(title="My Cool Embed", image=embed.Media(url="https://google.com"))

    output = {"title": "My Cool Embed", "image": {"url": "https://google.com"}}

    @discord.command()
    def embeddy(ctx):
        return Message(embed=my_embed)

    assert client.run("embeddy").dump_embeds() == [output]

    @discord.command()
    def multiple(ctx):
        return Message(embeds=[my_embed, my_embed])

    assert client.run("multiple").dump_embeds() == [output, output]


def test_improper_immediate(discord, client):
    fp = open("README.md", "r")

    @discord.command()
    def improper_immediate(ctx):
        return Message(file=("README.md", fp, "text/markdown"))

    result = client.run("improper_immediate")

    with pytest.raises(ValueError):
        result.dump()

    fp.close()


def test_improper_followup(discord, client):
    @discord.command()
    def improper_followup(ctx):
        return Message("hi", ephemeral=True)

    result = client.run("improper_followup")

    with pytest.raises(ValueError):
        result.dump_followup()


def test_ephemeral(discord, client):
    @discord.command()
    def ephemeral(ctx):
        return Message("hi", ephemeral=True)

    assert client.run("ephemeral").content == "hi"
    assert client.run("ephemeral").flags == 64


def test_dump_immediate(discord, client):
    @discord.command()
    def use_response(ctx):
        return Message("hi", tts=True, embed=Embed(title="hello!"))

    expected = {
        "type": ResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
        "data": {
            "content": "hi",
            "embeds": [{"title": "hello!"}],
            "flags": 0,
            "tts": True,
            "allowed_mentions": {"parse": ["roles", "users", "everyone"]},
            "components": None,
        },
    }

    assert client.run("use_response").dump() == expected


def test_dump_followup():
    resp = Message(
        content="Followup",
        embed=Embed(title="hello!"),
    )

    expected = {
        "content": "Followup",
        "embeds": [{"title": "hello!"}],
        "tts": False,
        "allowed_mentions": {"parse": ["roles", "users", "everyone"]},
        "components": None,
    }

    assert resp.dump_followup() == expected


def test_dump_multipart():
    fp = open("README.md", "r")
    resp = Message(
        content="Followup",
        embed=Embed(title="hello!"),
        file=("README.md", fp, "text/markdown"),
    )

    expected = {
        "data": {
            "payload_json": json.dumps(
                {
                    "content": "Followup",
                    "tts": False,
                    "embeds": [{"title": "hello!"}],
                    "allowed_mentions": {"parse": ["roles", "users", "everyone"]},
                    "components": None,
                }
            )
        },
        "files": [("file", ("README.md", fp, "text/markdown"))],
    }

    try:
        assert resp.dump_multipart() == expected
    finally:
        fp.close()
