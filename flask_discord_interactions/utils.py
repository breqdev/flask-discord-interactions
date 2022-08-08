import functools


class static_or_instance(object):
    """
    Decorator that allows a function to be called as either a static method
    or as an instance method (receiving the instance as the first argument).
    """

    def __init__(self, func):
        self.func = func

    def __get__(self, instance, owner):
        return functools.partial(self.func, instance)
