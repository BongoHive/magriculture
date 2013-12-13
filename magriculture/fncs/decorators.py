# Python
from functools import wraps

# Django
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.contrib import messages


def extension_officer_required(function):
    @wraps(function)
    def decorated_function(request, *args, **kwargs):
        if request.user.is_authenticated:
            if not request.user.actor.as_extensionofficer():
                messages.error(request, "You need to be an extension officer to view that.")
                return redirect(reverse("login"))

        return function(request, *args, **kwargs)
    return decorated_function


def agent_required(function):
    @wraps(function)
    def decorated_function(request, *args, **kwargs):
        if request.user.is_authenticated:
            if not request.user.actor.is_agent():
                messages.error(request, "You need to be an extension officer to view that.")
                return redirect(reverse("fncs:home"))
        return function(request, *args, **kwargs)
    return decorated_function
