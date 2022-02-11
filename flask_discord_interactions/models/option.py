class Option:
    def __init__(self, name, type, value=None, focused=None):
        self.name = name
        self.type = type
        self.value = value
        self.focused = focused

    @classmethod
    def from_data(cls, data):
        return cls(
            name=data["name"],
            type=data["type"],
            value=data.get("value"),
            focused=data.get("focused"),
        )
