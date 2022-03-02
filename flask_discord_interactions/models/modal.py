from dataclasses import dataclass
from typing import List, Union

from flask_discord_interactions.models.utils import LoadableDataclass
from flask_discord_interactions.models.component import Component, ComponentType
from flask_discord_interactions.enums import ResponseType


@dataclass
class Modal(LoadableDataclass):
    """
    Represents a Modal form window.

    Attributes
    ----------
    custom_id
        The ID for Callbacks.
    title
        The title of the modal.
    components
        A list of :class:`ActionRow` objects representing the rows of the form.
        Must have at least 1 row, at most 5 rows.
    """

    custom_id: Union[str, list] = None
    title: str = None
    components: List[Component] = None

    def __post_init__(self):
        # Verify Custom ID
        if self.custom_id is None:
            raise ValueError("Modals require custom_id")

        if isinstance(self.custom_id, list) or isinstance(self.custom_id, tuple):
            self.custom_id = "\n".join(str(item) for item in self.custom_id)

        if len(self.custom_id) > 100:
            raise ValueError("custom_id has maximum 100 characters")

        # Verify Title
        if self.title is None:
            raise ValueError("Modals require title")

        # Verify Components
        if not (
            self.components
            and isinstance(self.components, (list, tuple, set))
            and 1 <= len(self.components) <= 5
        ):
            raise ValueError(
                "Modal must have between 1 and 5 (inclusive) components that make up the modal"
            )

        for component in self.components:
            if component.type != ComponentType.ACTION_ROW:
                raise ValueError("Only Action Row components are supported for Modals")

    def dump_components(self):
        "Returns the message components as a list of dicts."
        return [c.dump() for c in self.components]

    def dump(self):
        """
        Return this ``Modal`` as a dict to be sent in response to an
        incoming webhook.
        """
        return {
            "type": ResponseType.MODAL,
            "data": {
                "custom_id": self.custom_id,
                "title": self.title,
                "components": self.dump_components(),
            },
        }

    def dump_handler(self):
        "Return a modal in component handlers."
        return self.dump()
