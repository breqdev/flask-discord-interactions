class PermissionType:
    ROLE = 1
    USER = 2
    CHANNEL = 3


class Permission:
    """
    An object representing a single permission overwrite.

    ``Permission(role='1234')`` allows users with role ID 1234 to use the
    command

    ``Permission(user='5678')`` allows user ID 5678 to use the command

    ``Permissoin(channel='9012')`` allows users in channel ID 9012 to use the command

    ``Permission(role='3456', allow=False)`` denies users with role ID 3456
    from using the command

    Parameters
    ----------
    role: str
        The role ID to apply the permission to.
    user: str
        The user ID to apply the permission to.
    channel: str
        The channel ID to apply the permission to.
    allow: bool
        Whether use of the command is allowed or denied for the specified criteria.
    """

    def __init__(self, role=None, user=None, channel=None, allow=True):
        if [bool(role), bool(user), bool(channel)].count(True) != 1:
            raise ValueError("specify only one of role, user, or channel")

        if role:
            self.type = PermissionType.ROLE
            self.id = role
        elif user:
            self.type = PermissionType.USER
            self.id = user
        elif channel:
            self.type = PermissionType.CHANNEL
            self.id = channel

        self.permission = allow

    def dump(self):
        """
        Returns a dict representation of the permission.

        Returns
        -------
        dict
            A dict representation of the permission.
        """
        return {"type": self.type, "id": self.id, "permission": self.permission}

    @classmethod
    def from_dict(cls, data: dict):
        """
        Returns a Permission object loaded from a dict.

        Parameters
        ----------
        data: dict
            A dict representation of the permission.
        """
        if data["type"] == PermissionType.ROLE:
            return cls(role=data["id"], allow=data["permission"])
        elif data["type"] == PermissionType.USER:
            return cls(user=data["id"], allow=data["permission"])
        elif data["type"] == PermissionType.CHANNEL:
            return cls(channel=data["id"], allow=data["permission"])
        else:
            raise ValueError("invalid permission type")
