# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .base import FunctionalTest
from .input_field import InputField
from selenium.webdriver.support.ui import Select

from gissmo.models import Actor


class ActorTest(FunctionalTest):

    def get_actortype_choice_name(self, number):
        res = ''
        if not number or number > 7:
            return res
        for element in Actor.ACTOR_TYPE_CHOICES:
            if element[0] == number:
                res = element[1]
                break
        return res

    def test_actor_creation(self):
        """
        Check a simple actor creation
        """
        # @EOST a new actor comes. His name is: John Doe.
        # We enter him in the system and check we are redirect to actor list.
        # Then we check that John DOE appears in the given actor list.
        actor_type = InputField(
            name='actor_type',
            content=self.get_actortype_choice_name(Actor.INCONNU),
            _type=Select)
        actor_name = InputField(
            name='actor_name',
            content='John DOE',
            check=True)

        fields = [actor_type, actor_name]

        self.add_item_in_admin('actor/', fields, check=True)
