import enum

from flask_discord_interactions import Member, Channel, Role


def test_str(discord, client):
    @discord.command()
    def repeat(ctx, message: str):
        return message + " " + message

    assert client.run("repeat", message="meow").content == "meow meow"


def test_int(discord, client):
    @discord.command()
    def add_one(ctx, number: int):
        return str(number + 1)

    assert client.run("add_one", number=2).content == "3"


def test_bool(discord, client):
    @discord.command()
    def and_gate(ctx, a: bool, b: bool):
        return str(a and b)

    assert client.run("and_gate", a=True, b=False).content == "False"
    assert client.run("and_gate", a=True, b=True).content == "True"


def test_number(discord, client):
    @discord.command()
    def round_to_nearest(ctx, number: float):
        return str(round(number))

    assert client.run("round_to_nearest", number=1.5).content == "2"
    assert client.run("round_to_nearest", number=1.25).content == "1"


def test_default(discord, client):
    @discord.command()
    def square(ctx, number: int = 5):
        return str(number**2)

    assert client.run("square").content == "25"
    assert client.run("square", number=2).content == "4"


def test_falsy_or_none(discord, client):
    @discord.command()
    def falsy_or_none(ctx, arg: bool = None):
        if arg is None:
            return "None"
        elif arg:
            return "True"
        else:
            return "False"

    assert client.run("falsy_or_none").content == "None"
    assert client.run("falsy_or_none", arg=False).content == "False"
    assert client.run("falsy_or_none", arg=True).content == "True"


def test_str_enum(discord, client):
    class Animal(enum.Enum):
        Dog = "dog"
        Cat = "cat"

    @discord.command()
    def favorite(ctx, choice: Animal):
        return f"You chose {choice}!"

    assert client.run("favorite", choice="dog").content == "You chose dog!"


def test_int_enum(discord, client):
    class BigNumber(enum.IntEnum):
        thousand = 1_000
        million = 1_000_000
        billion = 1_000_000_000
        trillion = 1_000_000_000_000

    @discord.command()
    def big_number(ctx, number: BigNumber):
        return f"One more is {number+1}"

    assert client.run("big_number", number=1_000).content == "One more is 1001"


def test_role(discord, client):
    @discord.command()
    def role_id(ctx, role: Role):
        return role.id

    assert client.run("role_id", role=Role(id="1234")).content == "1234"


def test_channel(discord, client):
    @discord.command()
    def channel_name(ctx, channel: Channel):
        return channel.name

    assert (
        client.run("channel_name", channel=Channel(name="general")).content == "general"
    )


def test_member(discord, client):
    @discord.command()
    def ship_them(ctx, other: Member):
        return f"{ctx.author.display_name} <3 {other.display_name}"

    with client.context(author=Member(username="Romeo")):
        assert (
            client.run("ship_them", other=Member(username="Juliet")).content
            == "Romeo <3 Juliet"
        )

        assert (
            client.run("ship_them", other=Member(username="Juliet", nick="J")).content
            == "Romeo <3 J"
        )


def test_multiple(discord, client):
    @discord.command()
    def has_role(ctx, role: Role, user: Member = None):
        if user is None:
            user = ctx.author

        return str(role.id in user.roles)

    with client.context(author=Member(roles=["2", "4", "8", "16"])):
        assert client.run("has_role", role=Role(id="2")).content == "True"
        assert client.run("has_role", role=Role(id="7")).content == "False"

        user = Member(roles=["7"])
        assert client.run("has_role", user=user, role=Role(id="2")).content == "False"
        assert client.run("has_role", user=user, role=Role(id="7")).content == "True"
