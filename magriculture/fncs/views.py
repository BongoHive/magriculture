from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render_to_response, get_object_or_404
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from datetime import datetime
import urllib

from magriculture.fncs.models.actors import Farmer, FarmerGroup
from magriculture.fncs.models.props import (Transaction, Crop, GroupMessage,
                                            CropUnit, Offer)
from magriculture.fncs.models.geo import Market
from magriculture.fncs import forms

@login_required
def home(request):
    return render_to_response('home.html', 
        context_instance=RequestContext(request))

@login_required
def farmers(request):
    actor = request.user.get_profile()
    agent = actor.as_agent()
    farmers = agent.farmers.all()
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
def farmer_new(request):
    actor = request.user.get_profile()
    agent = actor.as_agent()
    if request.POST:
        form = forms.FarmerForm(request.POST)
        if form.is_valid():
            msisdn = form.cleaned_data['msisdn']
            name = form.cleaned_data['name']
            surname = form.cleaned_data['surname']
            farmergroup = form.cleaned_data['farmergroup']
            markets = form.cleaned_data['markets']
            farmer = Farmer.create(msisdn, name, surname, farmergroup)
            for market in markets:
                farmer.sells_at(market, agent)
            messages.add_message(request, messages.INFO, 
                "Farmer Created")
            return HttpResponseRedirect(reverse("fncs:farmer_crops", kwargs={
                'farmer_pk': farmer.pk
            }))
    else:
        form = forms.FarmerForm()
    return render_to_response('farmers/new.html', {
        'form': form
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
    agent = request.user.get_profile().as_agent()
    paginator = Paginator(agent.sales_for(farmer), 5)
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

@login_required
def farmer_new_sale(request, farmer_pk):
    farmer = get_object_or_404(Farmer, pk=farmer_pk)
    form = forms.SelectCropForm()
    return render_to_response('farmers/new_sale.html', {
        'farmer': farmer,
        'form': form,
    }, context_instance=RequestContext(request))

@login_required
def farmer_new_sale_detail(request, farmer_pk):
    crop = get_object_or_404(Crop, pk=request.GET.get('crop'))
    farmer = get_object_or_404(Farmer, pk = farmer_pk)
    actor = request.user.get_profile()
    agent = actor.as_agent()
    
    redirect_to_farmer = HttpResponseRedirect(reverse('fncs:farmer', kwargs={
        'farmer_pk': farmer_pk
    }))
    if request.POST:
        if 'cancel' in request.POST:
            return redirect_to_farmer
        else:
            form = forms.TransactionForm(request.POST)
            if form.is_valid():
                crop = form.cleaned_data['crop']
                unit = form.cleaned_data['unit']
                price = form.cleaned_data['price']
                amount = form.cleaned_data['amount']
                market = form.cleaned_data['market']
                agent.register_sale(market, farmer, crop, unit, price, amount)
                messages.add_message(request, messages.INFO, 
                    "New Sale Registered and %s will be notified via SMS" % (
                        farmer.actor.name,))
                return redirect_to_farmer
            
    else:
        form = forms.TransactionForm(initial={
            'crop': crop.pk,
            'created_at': datetime.now()
        })
    
    return render_to_response('farmers/new_sale_detail.html', {
        'form': form,
        'crop': crop
    }, context_instance=RequestContext(request))
    
@login_required
def farmer_messages(request, farmer_pk):
    actor = request.user.get_profile()
    farmer = get_object_or_404(Farmer, pk=farmer_pk)
    paginator = Paginator(farmer.actor.receivedmessages_set \
                                .filter(sender=actor), 5)
    page = paginator.page(request.GET.get('p',1))
    return render_to_response('farmers/messages.html', {
        'farmer': farmer,
        'paginator': paginator,
        'page': page
    }, context_instance=RequestContext(request))

@login_required
def farmer_new_message(request, farmer_pk):
    actor = request.user.get_profile()
    agent = actor.as_agent()
    farmer = get_object_or_404(Farmer, pk=farmer_pk)
    redirect_to_farmer = HttpResponseRedirect(reverse('fncs:farmer', kwargs={
        'farmer_pk': farmer.pk
    }))
    if request.POST:
        
        if 'cancel' in request.POST:
            messages.add_message(request, messages.INFO, 
                'Message cancelled')
            return redirect_to_farmer
        
        form = forms.MessageForm(request.POST)
        if form.is_valid():
            agent.send_message_to_farmer(farmer, form.cleaned_data['content'])
            messages.add_message(request, messages.INFO, 
                'The message has been sent to %s via SMS' % farmer.actor.name)
            return redirect_to_farmer
    else:
        form = forms.MessageForm()
    return render_to_response('farmers/new_message.html', {
        'farmer': farmer,
        'form': form
    }, context_instance=RequestContext(request))

@login_required
def farmer_notes(request, farmer_pk):
    actor = request.user.get_profile()
    agent = actor.as_agent()
    farmer = get_object_or_404(Farmer, pk=farmer_pk)
    paginator = Paginator(agent.notes_for(farmer), 5)
    page = paginator.page(request.GET.get('p',1))
    return render_to_response('farmers/notes.html', {
        'farmer': farmer,
        'paginator': paginator,
        'page': page,
    }, context_instance=RequestContext(request))

@login_required
def farmer_new_note(request, farmer_pk):
    actor = request.user.get_profile()
    agent = actor.as_agent()
    farmer = get_object_or_404(Farmer, pk=farmer_pk)
    redirect_to_farmer_notes = HttpResponseRedirect(reverse('fncs:farmer_notes', 
        kwargs={ 'farmer_pk': farmer_pk}))
    
    if request.POST:
        if 'cancel' in request.POST:
            return redirect_to_farmer_notes
        
        form = forms.NoteForm(request.POST)
        if form.is_valid():
            agent.write_note(farmer, form.cleaned_data['content'])
            messages.add_message(request, messages.INFO,
                'Note has been saved')
            return redirect_to_farmer_notes
    else:
        form = forms.NoteForm()
    return render_to_response('farmers/new_note.html', {
        'farmer': farmer,
        'form': form,
    }, context_instance=RequestContext(request))

@login_required
def farmer_profile(request, farmer_pk):
    farmer = get_object_or_404(Farmer, pk=farmer_pk)
    return render_to_response('farmers/profile.html', {
        'farmer': farmer
    }, context_instance=RequestContext(request))

@login_required
def group_messages(request):
    actor = request.user.get_profile()
    paginator = Paginator(GroupMessage.objects.filter(sender=actor), 5)
    page = paginator.page(request.GET.get('p',1))
    return render_to_response('messages.html', {
        'paginator': paginator,
        'page': page
    }, context_instance=RequestContext(request))

@login_required
def group_message_new(request):
    farmergroups = FarmerGroup.objects.all()
    if request.POST:
        if 'cancel' in request.POST:
            messages.add_message(request, messages.INFO,
                'Message Cancelled')
            return HttpResponseRedirect(reverse('fncs:messages'))
        else:
            return HttpResponseRedirect('%s?%s' % (
                reverse('fncs:group_message_write'),
                urllib.urlencode([('fg', fg_id) for fg_id 
                    in request.POST.getlist('fg')])
            ))
    return render_to_response('group_messages_new.html', {
        'farmergroups': farmergroups
    }, context_instance=RequestContext(request))

@login_required
def group_message_write(request):
    actor = request.user.get_profile()
    agent = actor.as_agent()
    
    farmergroups = FarmerGroup.objects.filter(pk__in=request.GET.getlist('fg'))
    if not farmergroups.exists():
        raise Http404
    
    if request.POST:
        
        if 'cancel' in request.POST:
            messages.add_message(request, messages.INFO,
                'The message has been cancelled')
            return HttpResponseRedirect(reverse('fncs:messages'))
        
        form = forms.GroupMessageForm(request.POST)
        if form.is_valid():
            content = form.cleaned_data['content']
            agent.send_message_to_farmergroups(farmergroups, content)
            messages.add_message(request, messages.INFO,
                'The message has been sent to all group members via SMS')
            return HttpResponseRedirect(reverse('fncs:messages'))
    else:
        form = forms.GroupMessageForm()
    
    return render_to_response('group_messages_write.html', {
        'form': form,
        'farmergroups': farmergroups
    }, context_instance=RequestContext(request))

@login_required
def sales(request):
    return render_to_response('sales.html', {
    }, context_instance=RequestContext(request))

@login_required
def sales_crops(request):
    agent = request.user.get_profile().as_agent()
    paginator = Paginator(agent.transaction_set.all(), 5)
    page = paginator.page(request.GET.get('p', 1))
    return render_to_response('sales_crops.html', {
        'sales': sales,
        'paginator': paginator,
        'page': page
    }, context_instance=RequestContext(request))

@login_required
def sales_agents(request):
    return render_to_response('sales_agents.html', {
    }, context_instance=RequestContext(request))

@login_required
def sales_agent_breakdown(request):
    return render_to_response('sales_agent_breakdown.html', {
    }, context_instance=RequestContext(request))


@login_required
def farmer_crops(request, farmer_pk):
    farmer = get_object_or_404(Farmer, pk=farmer_pk)
    if request.POST:
        form = forms.CropsForm(request.POST)
        if form.is_valid():
            selected_crops = form.cleaned_data['crops']
            farmer.grows_crops_exclusively(selected_crops)
            messages.add_message(request, messages.INFO, 
                'Crops have been updated'
            )
            return HttpResponseRedirect(reverse('fncs:farmer', kwargs={
                'farmer_pk': farmer_pk
            }))
    else:
        form = forms.CropsForm(initial={
            'crops': farmer.crops.all()
        })
    return render_to_response('farmers/crops.html', {
        'form': form,
        'farmer': farmer
    }, context_instance=RequestContext(request))

@login_required
def farmer_edit(request, farmer_pk):
    farmer = get_object_or_404(Farmer, pk=farmer_pk)
    actor = farmer.actor
    user = actor.user
    if request.POST:
        form = forms.FarmerForm(request.POST)
        if form.is_valid():
            user.first_name = form.cleaned_data['name']
            user.last_name = form.cleaned_data['surname']
            user.username = form.cleaned_data['msisdn']
            user.save()
            
            farmer.sells_at_markets_exclusively(form.cleaned_data['markets'])
            farmer.farmergroup = form.cleaned_data['farmergroup']
            farmer.save()
            messages.add_message(request, messages.INFO,
                "Farmer Profile has been updated")
            return HttpResponseRedirect(reverse('fncs:farmer_crops', kwargs={
                'farmer_pk': farmer.pk
            }))
    else:
        form = forms.FarmerForm(initial={
            'name': user.first_name,
            'surname': user.last_name,
            'msisdn': user.username,
            'farmergroup': farmer.farmergroup,
            'markets': farmer.markets.all(),
        })
    return render_to_response('farmers/edit.html', {
        'form': form,
        'farmer': farmer
    }, context_instance=RequestContext(request))

@login_required
def market_prices(request):
    return render_to_response('markets/prices.html', {
    }, context_instance=RequestContext(request))

@login_required
def market_sales(request):
    paginator = Paginator(Market.objects.all(), 5)
    page = paginator.page(request.GET.get('p', 1))
    return render_to_response('markets/sales.html', {
        'paginator': paginator,
        'page': page,
    }, context_instance=RequestContext(request))

@login_required
def market_sale(request, market_pk):
    market = get_object_or_404(Market, pk=market_pk)
    paginator = Paginator(market.crops(), 5)
    page = paginator.page(request.GET.get('p',1))
    return render_to_response('markets/sale.html', {
        'market': market,
        'paginator': paginator,
        'page': page
    }, context_instance=RequestContext(request))

@login_required
def crop(request, market_pk, crop_pk):
    market = get_object_or_404(Market, pk=market_pk)
    crop = get_object_or_404(Crop, pk=crop_pk)
    paginator = Paginator(crop.units.all(), 5)
    page = paginator.page(request.GET.get('p', 1))
    return render_to_response('crops/show.html', {
        'crop': crop,
        'market': market,
        'paginator': paginator,
        'page': page
    }, context_instance=RequestContext(request))

@login_required
def crop_unit(request, market_pk, crop_pk, unit_pk):
    market = get_object_or_404(Market, pk=market_pk)
    crop = get_object_or_404(Crop, pk=crop_pk)
    unit = get_object_or_404(CropUnit, pk=unit_pk)
    transactions = Transaction.objects.filter(unit=unit, crop=crop, 
                                                market=market)
    paginator = Paginator(transactions, 5)
    page = paginator.page(request.GET.get('p', 1))

    return render_to_response('crops/unit.html', {
        'crop': crop,
        'unit': unit,
        'market': market,
        'paginator': paginator,
        'page': page
    }, context_instance=RequestContext(request))

@login_required
def market_offers(request):
    market_ids = [offer.market_id for offer in Offer.objects.all()]
    markets = Market.objects.filter(pk__in=market_ids)
    paginator = Paginator(markets, 5)
    page = paginator.page(request.GET.get('p', 1))
    return render_to_response('markets/offers.html', {
        'paginator': paginator,
        'page': page
    }, context_instance=RequestContext(request))

@login_required
def market_offer(request, market_pk):
    market = get_object_or_404(Market, pk=market_pk)
    crops = [offer.crop for offer in Offer.objects.filter(market=market)]
    paginator = Paginator(crops, 5)
    page = paginator.page(request.GET.get('p', 1))
    return render_to_response('markets/offer.html', {
        'market': market,
        'paginator': paginator,
        'page': page
    }, context_instance=RequestContext(request))

@login_required
def offer(request, market_pk, crop_pk):
    market = get_object_or_404(Market, pk=market_pk)
    crop = get_object_or_404(Crop, pk=crop_pk)
    offers = Offer.objects.filter(market=market,crop=crop)
    units = list(set([offer.unit for offer in offers]))
    paginator = Paginator(units, 5)
    page = paginator.page(request.GET.get('p', 1))
    return render_to_response('offers/show.html', {
        'crop': crop,
        'market': market,
        'paginator': paginator,
        'page': page
    }, context_instance=RequestContext(request))
    
@login_required
def offer_unit(request, market_pk, crop_pk, unit_pk):
    market = get_object_or_404(Market, pk=market_pk)
    crop = get_object_or_404(Crop, pk=crop_pk)
    unit = get_object_or_404(CropUnit, pk=unit_pk)
    offers = Offer.objects.filter(unit=unit, crop=crop, 
                                                market=market)
    paginator = Paginator(offers, 5)
    page = paginator.page(request.GET.get('p', 1))

    return render_to_response('offers/unit.html', {
        'crop': crop,
        'unit': unit,
        'market': market,
        'paginator': paginator,
        'page': page
    }, context_instance=RequestContext(request))

@login_required
def market_new_offer(request, *args, **kwargs):
    paginator = Paginator(Market.objects.all(), 5)
    page = paginator.page(request.GET.get('p', 1))
    return render_to_response('offers/markets.html', {
        'paginator': paginator,
        'page': page
    }, context_instance=RequestContext(request))

@login_required
def market_register_offer(request, market_pk):
    actor = request.user.get_profile()
    marketmonitor = actor.as_marketmonitor()
    market = get_object_or_404(Market, pk=market_pk)
    if request.POST:
        
        if 'cancel' in request.POST:
            return HttpResponseRedirect(reverse('fncs:market_new_offer'))
        
        form = forms.OfferForm(request.POST)
        if form.is_valid():
            print form.cleaned_data
            crop = form.cleaned_data['crop']
            unit = form.cleaned_data['unit']
            price_floor = form.cleaned_data['price_floor']
            price_ceiling = form.cleaned_data['price_ceiling']
            market = form.cleaned_data['market']
            marketmonitor.register_offer(market, crop, unit, price_floor, 
                                            price_ceiling)
            messages.add_message(request, messages.INFO, 'Opening price has '
                'been registered')
            return HttpResponseRedirect(reverse('fncs:market_new_offer'))
    else:
        form = forms.OfferForm(initial={
            'created_at': datetime.now(),
            'market': market
        })
    return render_to_response('offers/register.html', {
        'form': form,
        'market': market
    }, context_instance=RequestContext(request))

def todo(request):
    """Anything that resolves to here still needs to be completed"""
    return render_to_response('todo.html', {
    
    }, context_instance=RequestContext(request))

