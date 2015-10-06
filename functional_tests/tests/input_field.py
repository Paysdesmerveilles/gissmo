# -*- coding: utf-8 -*-


class InputField(object):
    """An element that gives informations about an Input field for Admin Forms.
    """

    def __init__(self, name, content, _type=None, check=False):
        self.name = name
        # WARNING: For _type == Select, content need to be a list [].
        self.content = content
        self._type = _type
        self.check = check
