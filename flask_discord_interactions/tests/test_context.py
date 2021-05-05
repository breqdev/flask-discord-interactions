from flask_discord_interactions import Context, Member


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
