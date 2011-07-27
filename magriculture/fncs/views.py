from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse

from magriculture.fncs.models.actors import Farmer
from magriculture.fncs.models.props import Transaction
from magriculture.fncs.utils import effective_page_range_for

@login_required
def home(request):
    return render_to_response('home.html', 
        context_instance=RequestContext(request))

@login_required
def farmers(request):
    farmers = Farmer.objects.all()
    q = request.GET.get('q','')
    if q:
        farmers = farmers.filter(actor__name__icontains=q)
    paginator = Paginator(farmers, 5)
    page = paginator.page(request.GET.get('p', 1))
    return render_to_response('farmers.html', {
        'paginator': paginator,
        'page': page,
        'q': q
    }, context_instance=RequestContext(request))

@login_required
def farmer_add(request):
    return HttpResponse('ok')

@login_required
def farmer(request, farmer_pk):
    return HttpResponseRedirect(reverse('fncs:farmer_sales', kwargs={
        'farmer_pk': farmer_pk
    }))

@login_required
def farmer_sales(request, farmer_pk):
    farmer = get_object_or_404(Farmer, pk=farmer_pk)
    paginator = Paginator(farmer.transactions(), 5)
    page = paginator.page(request.GET.get('p', 1))
    return render_to_response('farmers/sales.html', {
        'farmer': farmer,
        'paginator': paginator,
        'page': page,
    }, context_instance=RequestContext(request))
    
@login_required
def farmer_sale(request, farmer_pk, sale_pk):
    farmer = get_object_or_404(Farmer, pk=farmer_pk)
    transaction = get_object_or_404(Transaction, farmer=farmer, pk=sale_pk)
    return render_to_response('farmers/sale.html', {
        'farmer': farmer,
        'transaction': transaction,
    }, context_instance=RequestContext(request))

def todo(request):
    """Anything that resolves to here still needs to be completed"""
    return HttpResponse("This still needs to be implemented.")
