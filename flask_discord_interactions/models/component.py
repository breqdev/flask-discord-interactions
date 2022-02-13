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
                return {k: filter_none(v) for k, v in d.items() if v is not None}
            elif isinstance(d, list):
                return [filter_none(v) for v in d if v is not None]
            else:
                return d

        return filter_none(asdict(self))


@dataclass
class CustomIdComponent:
    """
    Represents a Message Component with a Custom ID.

    Attributes
    ----------
    custom_id: str | List
        The custom ID of the component. Strings represent a single ID, lists
        take advantage of newlines to store state alongside the ID.
    """

    custom_id: Union[str, List] = None

    def __post_init__(self):
        if isinstance(self.custom_id, list) or isinstance(self.custom_id, tuple):
            self.custom_id = "\n".join(str(item) for item in self.custom_id)

        if self.custom_id and len(self.custom_id) > 100:
            raise ValueError("custom_id has maximum 100 characters")


@dataclass
class ActionRow(Component):
    """
    Represents an ActionRow message component.

    Attributes
    ----------
    components: List[Component]
        The message components to display in the action row.
        Limited to any of the following:
        - 5 Buttons
        - 1 Select Menu
    """

    components: List[Component] = None

    type: int = ComponentType.ACTION_ROW

    def __post_init__(self):
        if self.components:
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
                            "select menu must be the only child of action row"
                        )


class ButtonStyles:
    "Represents the styles that can be applied to Button message components."
    PRIMARY = 1
    SECONDARY = 2
    SUCCESS = 3
    DANGER = 4
    LINK = 5


@dataclass
class Button(CustomIdComponent):
    """
    Represents a Button message component.

    Attributes
    ----------
    style: int
        The style of the button (see :class:`ButtonStyles`).
    label: str
        The label displayed on the button.
    url: str
        For link buttons, the URL that the button links to.
    disabled: bool
        Whether the button is disabled.
    """

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

        if isinstance(self.custom_id, list) or isinstance(self.custom_id, tuple):
            self.custom_id = "\n".join(str(item) for item in self.custom_id)

        if self.custom_id and len(self.custom_id) > 100:
            raise ValueError("custom_id has maximum 100 characters")


@dataclass
class SelectMenuOption:
    """
    Represents an option in a SelectMenu message component.

    Attributes
    ----------
    label: str
        The label displayed on the option.
    value: str
        The value of the option passed to the custom ID handler.
    description: str
        The description displayed on the option.
    emoji: dict
        The emoji displayed on the option.
    default: bool
        Whether the option is the default option.
    """

    label: str
    value: str

    description: str = None
    emoji: dict = None
    default: bool = False


@dataclass
class SelectMenu(CustomIdComponent):
    """
    Represents a SelectMenu message component.

    Attributes
    ----------
    options: List[SelectMenuOption]
        The options to display in the select menu.
    placeholder: str
        The placeholder displayed when the select menu is empty.
    min_values: int
        The minimum number of options that must be selected.
    max_values: int
        The maximum number of options that can be selected.
    disabled: bool
        Whether the select menu is disabled.
    """

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
