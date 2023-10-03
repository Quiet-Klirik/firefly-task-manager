from django.test import TestCase

from task_manager.models import Position


class ModelsTests(TestCase):
    def test_position_str(self):
        name = "Tester"
        position = Position.objects.create(name=name)
        self.assertEquals(str(position), name)
