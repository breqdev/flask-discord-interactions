class Permission:
    """
    An object representing a single permission overwrite.

    ``Permission(role='1234')`` allows users with role ID 1234 to use the
    command

    ``Permission(user='5678')`` allows user ID 5678 to use the command

    ``Permission(role='9012', allow=False)`` denies users with role ID 9012
    from using the command
    """

    def __init__(self, role=None, user=None, allow=True):
        if bool(role) == bool(user):
            raise ValueError("specify only one of role or user")

        self.type = 1 if role else 2
        self.id = role or user
        self.permission = allow

    def dump(self):
        "Returns a dict representation of the permission"
        return {"type": self.type, "id": self.id, "permission": self.permission}
