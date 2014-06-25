from django.contrib.auth.backends import ModelBackend

from magriculture.fncs.models.actors import Identity

from magriculture.fncs import utils


class IdentityBackend(ModelBackend):

    def authenticate(self, username, password=None):
        try:
            normalised_username = utils.normalise_msisdn(username)
            identity = Identity.objects.get(msisdn=normalised_username)
            if identity.pin and identity.check_pin(password):
                return identity.actor.user
            return None
        except Identity.DoesNotExist:
            return None
