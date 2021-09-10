from dataclasses import dataclass, asdict
from typing import List, Union

class ComponentType:
    ACTION_ROW = 1
    BUTTON = 2
    SELECT_MENU = 3


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
class CustomIdComponent:
    "Represents a Message Component with a Custom ID."

    custom_id: Union[str, List] = None

    def __post_init__(self):
        if (isinstance(self.custom_id, list)
                or isinstance(self.custom_id, tuple)):
            self.custom_id = "\n".join(str(item) for item in self.custom_id)

        if self.custom_id and len(self.custom_id) > 100:
            raise ValueError("custom_id has maximum 100 characters")


@dataclass
class ActionRow(Component):
    "Represents an ActionRow message component."
    components: List[Component] = None

    type: int = ComponentType.ACTION_ROW


    def __post_init__(self):
        if self.components:
            # Limited to any of the following:
            # - 5 Buttons
            # - 1 Select Menu

            if len(self.components) > 5:
                raise ValueError("ActionRow can have at most 5 components")

            for component in self.components:
                if component.type == ComponentType.ACTION_ROW:
                    raise ValueError("nested action rows not allowed")
                elif component.type == ComponentType.BUTTON:
                    pass
                elif component.type == ComponentType.SELECT_MENU:
                    if len(self.components) > 1:
                        raise ValueError(
                            "select menu must be the only child of action row")



class ButtonStyles:
    PRIMARY = 1
    SECONDARY = 2
    SUCCESS = 3
    DANGER = 4
    LINK = 5


@dataclass
class Button(CustomIdComponent):
    "Represents a Button message component."
    style: int = ButtonStyles.PRIMARY
    label: str = None

    emoji: dict = None
    url: str = None
    disabled: bool = False

    type: int = ComponentType.BUTTON

    def __post_init__(self):
        super().__post_init__()

        if self.style == ButtonStyles.LINK:
            if self.url is None:
                raise ValueError("Link buttons require a url")
        else:
            if self.custom_id is None:
                raise ValueError("Buttons require custom_id")

        if (isinstance(self.custom_id, list)
                or isinstance(self.custom_id, tuple)):
            self.custom_id = "\n".join(str(item) for item in self.custom_id)

        if self.custom_id and len(self.custom_id) > 100:
            raise ValueError("custom_id has maximum 100 characters")


@dataclass
class SelectMenuOption():
    label: str
    value: str

    description: str = None
    emoji: dict = None
    default: bool = False


@dataclass
class SelectMenu(CustomIdComponent):
    "Represents a SelectMenu component."
    options: List[SelectMenuOption] = None

    placeholder: str = None
    min_values: int = 1
    max_values: int = 1
    disabled: bool = False

    type: int = ComponentType.SELECT_MENU

    def __post_init__(self):
        super().__post_init__()

        if len(self.options) > 25:
            raise ValueError("Select is limited to 25 options")

        if len(self.placeholder) > 100:
            raise ValueError("Placeholder is max 100 characters")

        if self.min_values > self.max_values:
            raise ValueError("min_values must be less than or equal to max_values")

        if self.max_values > 25:
            raise ValueError("max_values is maximum 25")
