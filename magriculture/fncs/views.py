from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.core.paginator import Paginator

from magriculture.fncs.models.actors import Farmer
from magriculture.fncs.utils import effective_page_range_for

@login_required
def home(request):
    return render_to_response('home.html', 
        context_instance=RequestContext(request))

@login_required
def farmers(request):
    paginator = Paginator(Farmer.objects.all(), 5)
    page = paginator.page(request.GET.get('p', 1))
    return render_to_response('farmers.html', {
        'paginator': paginator,
        'page': page
    }, context_instance=RequestContext(request))

@login_required
def farmer_add(request):
    return HttpResponse('ok')

@login_required
def farmer(request, pk):
    farmer = get_object_or_404(Farmer, pk=pk)
    return HttpResponse('ok')

def todo(request):
    """Anything that resolves to here still needs to be completed"""
    return HttpResponse("This still needs to be implemented.")
