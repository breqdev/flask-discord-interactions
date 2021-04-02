import requests

from .response import Response


class CommandOptionType:
    SUB_COMMAND = 1
    SUB_COMMAND_GROUP = 2
    STRING = 3
    INTEGER = 4
    BOOLEAN = 5
    USER = 6
    CHANNEL = 7
    ROLE = 8


class ChannelType:
    GUILD_TEXT = 0
    DM = 1
    GUILD_VOICE = 2
    GROUP_DM = 3
    GUILD_CATEGORY = 4
    GUILD_NEWS = 5
    GUILD_STORE = 6


class User:
    def __init__(self, data=None):
        if data:
            self.id = data.get("id")
            self.username = data.get("username")
            self.discriminator = data.get("discriminator")
            self.avatar_hash = data.get("avatar")
            self.bot = data.get("bot", False)
            self.system = data.get("system", False)
            self.mfa_enabled = data.get("mfa_enabled", False)
            self.locale = data.get("locale")
            self.flags = data.get("flags")
            self.premium_type = data.get("premium_type")
            self.public_flags = data.get("public_flags")

    @property
    def display_name(self):
        return self.username

    @property
    def avatar_url(self):
        return ("https://cdn.discordapp.com/avatars/"
                f"{self.id}/{self.avatar_hash}.png")


class Member(User):
    def __init__(self, data=None):
        if data:
            super().__init__(data["user"])

            self.nick = data.get("nick")
            self.roles = data.get("roles")
            self.joined_at = data.get("joined_at")
            self.premium_since = data.get("premium_since")
            self.deaf = data.get("deaf")
            self.mute = data.get("mute")
            self.pending = data.get("pending")

    @property
    def display_name(self):
        return self.nick or self.username


class Channel:
    def __init__(self, data=None):
        if data:
            self.id = data.get("id")
            self.name = data.get("name")
            self.permissions = data.get("permissions")
            self.type = data.get("type")


class Role:
    def __init__(self, data=None):
        if data:
            self.id = data.get("id")
            self.name = data.get("name")
            self.color = data.get("color")
            self.hoist = data.get("hoist")
            self.position = data.get("position")
            self.permissions = data.get("permissions")
            self.managed = data.get("managed")
            self.mentionable = data.get("mentionable")
            self.tags = data.get("tags", {})


class Context:
    def __init__(self, discord, app, data=None):
        self.client_id = app.config["DISCORD_CLIENT_ID"]
        self.auth_headers = discord.auth_headers(app)

        if data:
            self.author = Member(data["member"])
            self.id = data["id"]
            self.token = data["token"]
            self.channel_id = data["channel_id"]
            self.guild_id = data["guild_id"]
            self.options = data["data"].get("options")
            self.command_name = data["data"]["name"]
            self.command_id = data["data"]["id"]

            self.parse_resolved(data["data"].get("resolved", {}))

    def parse_resolved(self, data):
        self.members = {}
        for id in data.get("members", {}):
            member_info = data["members"][id]
            member_info["user"] = data["users"][id]
            self.members[id] = Member(member_info)

        self.channels = {id: Channel(data)
                         for id, data in data.get("channels", {}).items()}

        self.roles = {id: Role(data)
                      for id, data in data.get("roles", {}).items()}

    def create_args(self, data, resolved):
        if "options" not in data:
            return [], {}

        args = []
        kwargs = {}
        for option in data["options"]:
            if option["type"] in [
                    CommandOptionType.SUB_COMMAND,
                    CommandOptionType.SUB_COMMAND_GROUP]:
                args.append(option["name"])
                sub_args, sub_kwargs = self.create_args(option, resolved)
                args += sub_args
                kwargs.update(sub_kwargs)
            elif option["type"] == CommandOptionType.USER:
                member_data = resolved["members"][option["value"]]
                member_data["user"] = resolved["users"][option["value"]]

                kwargs[option["name"]] = Member(member_data)
            elif option["type"] == CommandOptionType.CHANNEL:
                kwargs[option["name"]] = Channel(
                    resolved["channels"][option["value"]])
            elif option["type"] == CommandOptionType.ROLE:
                kwargs[option["name"]] = Role(
                    resolved["roles"][option["value"]])
            else:
                kwargs[option["name"]] = option["value"]

        return args, kwargs

    def followup_url(self, message=None):
        url = ("https://discord.com/api/v8/webhooks/"
               f"{self.client_id}/{self.token}")
        if message is not None:
            url += f"/messages/{message}"

        return url

    def edit(self, response, message="@original"):
        response = Response.from_return_value(response)

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
        response = Response.from_return_value(response)

        response = requests.post(
            self.followup_url(),
            headers=self.auth_headers,
            **response.dump_multipart()
        )
        response.raise_for_status()
        return response.json()["id"]
