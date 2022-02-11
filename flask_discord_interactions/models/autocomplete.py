from flask_discord_interactions.models.message import ResponseType


class Autocomplete:
    def __init__(self, t: type):
        self.t = t


class AutocompleteResult:
    def __init__(self, choices={}):
        self.choices = choices

    def dump(self):
        return {
            "type": ResponseType.APPLICATION_COMMAND_AUTOCOMPLETE_RESULT,
            "data": {
                "choices": [
                    {"name": choice, "value": value}
                    for choice, value in self.choices.items()
                ]
            },
        }

    @staticmethod
    def from_return_value(value):
        if isinstance(value, AutocompleteResult):
            return value
        elif isinstance(value, dict):
            return AutocompleteResult(value)
        elif isinstance(value, list):
            return AutocompleteResult({choice: choice for choice in value})
