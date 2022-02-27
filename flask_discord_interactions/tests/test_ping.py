def test_ping(discord, client):
    @discord.command()
    def ping(ctx, pong: str = "pong"):
        "Respond with a friendly 'pong'!"
        return f"Pong {pong}!"

    assert client.run("ping").content == "Pong pong!"
    assert client.run("ping", pong="sprong").content == "Pong sprong!"
