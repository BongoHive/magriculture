from django.contrib.auth.backends import ModelBackend

from magriculture.fncs.models.actors import Identity


class IdentityBackend(ModelBackend):

    def authenticate(self, username, password=None):
        try:
            identity = Identity.objects.get(msisdn=username)
            if identity.pin and identity.check_pin(password):
                return identity.actor.user
            return None
        except Identity.DoesNotExist:
            return None
