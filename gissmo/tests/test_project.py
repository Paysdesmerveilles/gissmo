from __future__ import unicode_literals
from django.test import TestCase

from django.contrib.auth.models import User

from gissmo.models import Project


DEFAULT_ADMIN_LOGIN = 'admin'
DEFAULT_ADMIN_PASSWORD = 'admin'


class ProjectTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.superuser = User.objects.create_superuser(
            DEFAULT_ADMIN_LOGIN,
            'admin@mysite.com',
            DEFAULT_ADMIN_PASSWORD)
        cls.user = User.objects.create_user(
            'john',
            'john@mysite.com',
            'doe')

        cls.project_1 = Project.objects.create(
            name='ADEME',
            manager=cls.user)
        cls.project_2 = Project.objects.create(
            name='ALL',
            manager=cls.user)
        cls.project_3 = Project.objects.create(
            name='RAP',
            manager=cls.user)

    def test_delete_project(self):
        project_id = self.project_1.id
        self.project_1.delete()
        projects = Project.objects.all()
        project_ids = [x.id for x in projects]
        self.assertNotIn(
            project_id,
            project_ids,
            "Project not deleted!")

    def test_can_delete_project_called_ALL(self):
        project = Project.objects.filter(name='ALL').first()
        project_id = project.id
        project.delete()
        projects = Project.objects.all()
        project_ids = [x.id for x in projects]
        self.assertNotIn(
            project_id,
            project_ids,
            "Project not deleted!")
