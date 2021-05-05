from flask_discord_interactions import Response


def test_content(discord, client):
    @discord.command()
    def content(ctx):
        return "quality content"

    assert client.run("content").content == "quality content"


def test_embed(discord, client):
    embed = {
        "title": "My Cool Embed"
    }

    @discord.command()
    def embeddy(ctx):
        return Response(embed=embed)

    assert client.run("embeddy").embeds == [embed]

    @discord.command()
    def multiple(ctx):
        return Response(embeds=[embed, embed])

    assert client.run("multiple").embeds == [embed, embed]


def test_ephemeral(discord, client):
    @discord.command()
    def ephemeral(ctx):
        return Response("hi", ephemeral=True)

    assert client.run("ephemeral").content == "hi"
    assert client.run("ephemeral").flags == 64
