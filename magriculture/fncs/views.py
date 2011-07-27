from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404

def index(request):
    return render_to_response('index.html', 
        context_instance=RequestContext(request))

def todo(request):
    """Anything that resolves to here still needs to be completed"""
    return HttpResponse("This still needs to be implemented.")
