from dataclasses import dataclass, asdict
from typing import List

class ComponentType:
    ACTION_ROW = 1
    BUTTON = 2


class Component:
    "Represents a Message Component."

    def dump(self):
        "Returns this Component as a dictionary, removing fields which are None."
        def filter_none(d):
            if isinstance(d, dict):
                return {
                    k: filter_none(v) for k, v in d.items() if v is not None
                }
            elif isinstance(d, list):
                return [filter_none(v) for v in d if v is not None]
            else:
                return d

        return filter_none(asdict(self))


@dataclass
class ActionRow(Component):
    "Represents an ActionRow message component."
    components: List[Component] = None

    type: int = ComponentType.ACTION_ROW


class ButtonStyles:
    PRIMARY = 1
    SECONDARY = 2
    SUCCESS = 3
    DANGER = 4
    LINK = 5


@dataclass
class Button(Component):
    "Represents a Button message component."
    style: int
    custom_id: str
    label: str = None

    emoji: dict = None
    url: str = None
    disabled: bool = False

    type: int = ComponentType.BUTTON
