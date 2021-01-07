import requests

from .response import InteractionResponse


class InteractionContext:
    class InteractionAuthor:
        def __init__(self, data=None):
            if data:
                self.id = data["user"]["id"]
                self.username = data["user"]["username"]
                self.discriminator = data["user"]["discriminator"]
                self.avatar_hash = data["user"]["avatar"]
                self.bot = data["user"].get("bot", False)
                self.system = data["user"].get("system", False)
                self.mfa_enabled = data["user"].get("mfa_enabled", False)
                self.locale = data["user"].get("locale")
                self.flags = data["user"].get("flags")
                self.premium_type = data["user"].get("premium_type")
                self.public_flags = data["user"].get("public_flags")

                self.nick = data["nick"]
                self.roles = data["roles"]
                self.joined_at = data["joined_at"]
                self.premium_since = data.get("premium_since")
                self.deaf = data["deaf"]
                self.mute = data["mute"]
                self.pending = data.get("pending")

        @property
        def display_name(self):
            return self.nick or self.username

        @property
        def avatar_url(self):
            return ("https://cdn.discordapp.com/avatars/"
                    f"{self.id}/{self.avatar_hash}.png")

    def __init__(self, discord, app, data=None):
        self.client_id = app.config["DISCORD_CLIENT_ID"]
        self.auth_headers = discord.auth_headers(app)

        if data:
            self.author = self.InteractionAuthor(data["member"])
            self.id = data["id"]
            self.token = data["token"]
            self.channel_id = data["channel_id"]
            self.guild_id = data["guild_id"]
            self.options = data["data"].get("options")
            self.command_name = data["data"]["name"]
            self.command_id = data["data"]["id"]

    def followup_url(self, message=None):
        url = ("https://discord.com/api/v8/webhooks/"
               f"{self.client_id}/{self.token}")
        if message is not None:
            url += f"/messages/{message}"

        return url

    def edit(self, response, message="@original"):
        response = InteractionResponse.from_return_value(response)

        response = requests.patch(
            self.followup_url(message),
            json=response.dump_followup(),
            headers=self.auth_headers
        )
        response.raise_for_status()

    def delete(self, message="@original"):
        response = requests.delete(
            self.followup_url(message),
            headers=self.auth_headers
        )
        response.raise_for_status()

    def send(self, response):
        response = InteractionResponse.from_return_value(response)

        response = requests.post(
            self.followup_url(),
            headers=self.auth_headers,
            **response.dump_multipart()
        )
        response.raise_for_status()
        return response.json()["id"]
