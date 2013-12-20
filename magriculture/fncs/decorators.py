# Python
from functools import wraps

# Django
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.contrib import messages
from django.views.generic import TemplateView


class SpecificRightsRequired(TemplateView):
    """
    The purpose of this class decorator is to take variable arguments
    and determines if request.user has the rights to the function depending
     on the Object arguments and user status.
    """
    def __init__(self, agent=False, ext_officer=False, superuser=False):
        self.agent = agent
        self.ext_officer = ext_officer
        self.superuser = superuser

    def __call__(self, func):
        @wraps(func)
        def decorated_function(request, *args, **kwargs):
            true_agent = self.agent and request.user.actor.is_agent()
            true_ext_officer = self.ext_officer and request.user.actor.is_extensionofficer()
            true_superuser = self.superuser and request.user.is_superuser

            if request.user.is_authenticated:
                if true_agent or true_ext_officer or true_superuser:
                    return func(request, *args, **kwargs)

            messages.error(request, "Sorry you don't have rights to view this part of the system.")
            return redirect(reverse("fncs:home"))
        return decorated_function
