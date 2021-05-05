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
