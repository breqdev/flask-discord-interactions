from flask_discord_interactions import CommandOptionType, Context, Member


def test_subcommand(discord, client):
    group = discord.command_group("group")

    @group.command()
    def sub_one(ctx):
        return "sub one"

    @group.command()
    def sub_two(ctx):
        return "sub two"

    assert client.run("group", "sub_one").content == "sub one"
    assert client.run("group", "sub_two").content == "sub two"


def test_subcommand_groups(discord, client):
    group = discord.command_group("group")

    subgroup_one = group.subgroup("sub_one")
    subgroup_two = group.subgroup("sub_two")

    @subgroup_one.command()
    def sub_one_one(ctx):
        return "one one"

    @subgroup_one.command()
    def sub_one_two(ctx):
        return "one two"

    @subgroup_two.command()
    def sub_two_one(ctx):
        return "two one"

    assert client.run("group", "sub_one", "sub_one_one").content == "one one"
    assert client.run("group", "sub_one", "sub_one_two").content == "one two"
    assert client.run("group", "sub_two", "sub_two_one").content == "two one"


def test_oldstyle_subcommand(discord, client):
    @discord.command(
        options=[
            {
                "name": "google",
                "description": "Search with Google",
                "type": CommandOptionType.SUB_COMMAND,
                "options": [
                    {
                        "name": "query",
                        "description": "Search query",
                        "type": CommandOptionType.STRING,
                        "required": True,
                    }
                ],
            },
            {
                "name": "bing",
                "description": "Search with Bing",
                "type": CommandOptionType.SUB_COMMAND,
                "options": [
                    {
                        "name": "query",
                        "description": "Search query",
                        "type": CommandOptionType.STRING,
                        "required": True,
                    }
                ],
            },
        ]
    )
    def search(ctx, subcommand, *, query):
        "Search the Internet!"
        if subcommand == "google":
            return f"https://google.com/search?q={query}"
        if subcommand == "bing":
            return f"https://bing.com/search?q={query}"

    assert (
        client.run("search", "google", query="hello").content
        == "https://google.com/search?q=hello"
    )
    assert (
        client.run("search", "bing", query="hello").content
        == "https://bing.com/search?q=hello"
    )


def test_context_with_subcommand(discord, client):
    group = discord.command_group("group")

    @group.command()
    def subcommand(ctx):
        return ctx.author.display_name

    context = Context(
        author=Member(username="Bob", id="8", discriminator="1234", public_flags=0)
    )

    with client.context(context):
        assert client.run("group", "subcommand").content == "Bob"
