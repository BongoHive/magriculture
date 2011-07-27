from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404

@login_required
def home(request):
    return render_to_response('home.html', 
        context_instance=RequestContext(request))

def todo(request):
    """Anything that resolves to here still needs to be completed"""
    return HttpResponse("This still needs to be implemented.")
