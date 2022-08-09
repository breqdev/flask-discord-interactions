import json
from typing import Union
from flask_discord_interactions.models.message import ResponseType
from flask_discord_interactions.models.option import Choice


class Autocomplete:
    """
    Represents the type of an option that can be autocompleted.

    Parameters
    ----------
    t
        The underlying type of the option.
    """

    def __init__(self, t: type):
        self.t = t


class AutocompleteResult:
    """
    Represents the result of an autocomplete handler.

    Parameters
    ----------
    choices
        A dict mapping the displayed name of each choice to its value passed to
        your command.
    """

    def __init__(self, choices=[]):
        self.choices = choices

    def encode(self):
        """
        Return this result as a complete interaction response.

        Returns
        -------
        str
            The encoded JSON object.
        str
            The mimetype of the response (``application/json``).
        """
        data = {
            "type": ResponseType.APPLICATION_COMMAND_AUTOCOMPLETE_RESULT,
            "data": {"choices": self.choices},
        }

        return json.dumps(data), "application/json"

    @staticmethod
    def from_return_value(value: Union[dict, list, "AutocompleteResult"]):
        """
        Converts the return value of an autocomplete handler to an
        AutocompleteResult.

        Parameters
        ----------
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
            return AutocompleteResult([value])
        elif isinstance(value, list) and all(
            isinstance(choice, dict) for choice in value
        ):
            return AutocompleteResult(value)
        elif isinstance(value, list) and all(
            isinstance(choice, Choice) for choice in value
        ):
            return AutocompleteResult([choice.dump() for choice in value])
        elif isinstance(value, list):
            return AutocompleteResult(
                [{"name": str(choice), "value": choice} for choice in value]
            )
