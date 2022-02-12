from typing import Union
from flask_discord_interactions.models.message import ResponseType


class Autocomplete:
    """
    Represents the type of an option that can be autocompleted.

    Attributes
    ----------
    t
        The underlying type of the option.
    """

    def __init__(self, t: type):
        self.t = t


class AutocompleteResult:
    """
    Represents the result of an autocomplete handler.

    Attributes
    ----------
    choices
        A dict mapping the displayed name of each choice to its value passed to
        your command.
    """

    def __init__(self, choices={}):
        self.choices = choices

    def dump(self):
        "Return this result as a complete interaction response."
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
    def from_return_value(value: Union[dict, list, "AutocompleteResult"]):
        """
        Converts the return value of an autocomplete handler to an
        AutocompleteResult.

        Paramters
        ---------
        value
            The return value of an autocomplete handler.

        Returns
        -------
        AutocompleteResult
            The AutocompleteResult that corresponds to the return value.
        """
        if isinstance(value, AutocompleteResult):
            return value
        elif isinstance(value, dict):
            return AutocompleteResult(value)
        elif isinstance(value, list):
            return AutocompleteResult({choice: choice for choice in value})
