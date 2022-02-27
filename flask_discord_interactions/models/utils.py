import inspect


class LoadableDataclass:
    @classmethod
    def from_dict(cls, data):
        """
        Construct the dataclass from a dictionary, skipping any keys
        in the dictionary that do not correspond to fields of the class.

        Parameters
        ----------
        data
            A dictionary of fields to set on the dataclass.
        """
        return cls(
            **{k: v for k, v in data.items() if k in inspect.signature(cls).parameters}
        )
