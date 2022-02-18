from dataclasses import dataclass, asdict
from typing import List

from flask_discord_interactions.models.utils import LoadableDataclass
from flask_discord_interactions.models.component import Component, ComponentType


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
        A list of :class:`Component` objects representing the elements of the form.
    """

    custom_id: str = None
    title: str = None
    components: List[Component] = None

    def __post_init__(self):
        if not (self.components and 1 <= len(self.components) <= 5):
            raise ValueError("Modal must have between 1 and 5 (inclusive) components that make up the modal")

        for component in self.components:
            if component.type != ComponentType.TEXT_INPUT:
                raise ValueError("Only Text Input components are supported")

    def dump(self):
        "Returns this Modal as a dictionary, removing fields which are None."

        def filter_none(d):
            if isinstance(d, dict):
                return {k: filter_none(v) for k, v in d.items() if v is not None}
            else:
                return d

        return filter_none(asdict(self))
