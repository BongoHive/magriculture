from django.test import TestCase
from django.contrib.auth.models import User
from magriculture.fncs.models.actors import Actor

class ActorTestCase(TestCase):
    
    def setUp(self):
        pass
    
    def tearDown(self):
        pass
    
    def test_profile_create(self):
        user = User.objects.create_user('username', 'email@domain.com')
        actor = user.get_profile()
        self.assertTrue(isinstance(actor, Actor))