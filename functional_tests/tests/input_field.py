# -*- coding: utf-8 -*-


class InputField(object):
    """An element that gives informations about an Input field for Admin Forms.
    """

    def __init__(self, name, content, _type=None, check=False):
        self.name = str(name)
        self.content = str(content)
        self._type = _type
        self.check = check
