from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import (render_to_response, get_object_or_404, render,
                              redirect)
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from django.forms.widgets import HiddenInput
from datetime import datetime
import urllib

from magriculture.fncs.models.actors import Farmer, FarmerGroup, Agent
from magriculture.fncs.models.props import (Transaction, Crop, GroupMessage,
                                            CropUnit, Offer, CropReceipt,
                                            DirectSale)
from magriculture.fncs.models.geo import Market, Ward, District
from magriculture.fncs import forms
from magriculture.fncs.decorators import SpecificRightsRequired


@login_required
def home(request):
    return render_to_response('home.html',
                              context_instance=RequestContext(request))


@login_required
@SpecificRightsRequired(agent=True)
def farmers(request):
    actor = request.user.get_profile()
    agent = actor.as_agent()
    farmers = agent.farmers.all()
    q = request.GET.get('q', '')
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
@SpecificRightsRequired(agent=True)
def farmer_new(request):
    actor = request.user.get_profile()
    agent = actor.as_agent()
    if request.POST:
        form = forms.FarmerForm(request.POST)
        if form.is_valid():
            # msisdn = form.cleaned_data['msisdn']

            msisdns = [
                form.cleaned_data['msisdn1'],
                form.cleaned_data['msisdn2'],
                form.cleaned_data['msisdn3'],
            ]
            [msisdn1, msisdn2, msisdn3] = msisdns

            name = form.cleaned_data['name']
            surname = form.cleaned_data['surname']
            id_number = form.cleaned_data['id_number']
            markets = form.cleaned_data['markets']
            matched_farmer = form.cleaned_data['matched_farmer']
            gender = form.cleaned_data["gender"]

            if not id_number:
                id_number = None

            if matched_farmer:
                messages.info(request, 'Farmer added.')
                if agent:
                    for market in markets:
                        matched_farmer.operates_at(market, agent)
                farmer_url = reverse('fncs:farmer_edit', kwargs={
                    'farmer_pk': matched_farmer.pk,
                })
                return redirect(farmer_url)

            possible_matches = Farmer.match(msisdns=msisdns,
                                            id_number=id_number)
            if possible_matches:
                form.fields['matched_farmer'].queryset = possible_matches
                messages.info(request, "This farmer possibly already exists. "
                              "Please review the list of matched farmers to "
                              "avoid double registrations")
            else:
                farmer = Farmer.create(msisdn1, name, surname,
                                       id_number=id_number, gender=gender)
                farmer.actor.update_msisdns(msisdns)
                if agent:
                    for market in markets:
                        farmer.operates_at(market, agent)

                messages.success(request, "Farmer Created")
                return HttpResponseRedirect(
                    reverse("fncs:farmer_location_search", kwargs={
                            'farmer_pk': farmer.pk}))
    else:
        form = forms.FarmerForm()
        form.fields['matched_farmer'].widget = HiddenInput()
    return render_to_response('farmers/new.html', {
        'form': form
    }, context_instance=RequestContext(request))


@login_required
@SpecificRightsRequired(agent=True)
def farmer_location_search(request, farmer_pk):
    """Search for a farmer's location."""
    farmer = get_object_or_404(Farmer, pk=farmer_pk)
    location_form = None
    if request.method == "POST":
        search_form = forms.FarmerLocationSearchForm(request.POST)
        if search_form.is_valid():
            location_form = forms.FarmerLocationForm(
                initial={'search': search_form.cleaned_data['search']})
    else:
        search_form = forms.FarmerLocationSearchForm()
    return render_to_response('farmers/location.html', {
        'farmer': farmer,
        'search_form': search_form,
        'location_form': location_form,
    }, context_instance=RequestContext(request))


@login_required
@SpecificRightsRequired(agent=True)
def farmer_location_save(request, farmer_pk):
    """Set the location of a farmer."""
    farmer = get_object_or_404(Farmer, pk=farmer_pk)
    if request.method == "POST":
        location_form = forms.FarmerLocationForm(data=request.POST)
        if location_form.is_valid():
            location_form.save_location(farmer)
            return HttpResponseRedirect(
                reverse("fncs:farmer", kwargs={'farmer_pk': farmer.pk}))
        search_form = forms.FarmerLocationSearchForm(
            initial={'search': location_form.data.get('search')})
    else:
        search_form = forms.FarmerLocationSearchForm()
        location_form = None
    return render_to_response('farmers/location.html', {
        'farmer': farmer,
        'search_form': search_form,
        'location_form': location_form,
    }, context_instance=RequestContext(request))


@login_required
@SpecificRightsRequired(agent=True)
def farmer(request, farmer_pk):
    return HttpResponseRedirect(reverse('fncs:farmer_sales', kwargs={
        'farmer_pk': farmer_pk
    }))


@login_required
@SpecificRightsRequired(agent=True)
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
@SpecificRightsRequired(agent=True)
def farmer_sale(request, farmer_pk, sale_pk):
    farmer = get_object_or_404(Farmer, pk=farmer_pk)
    transaction = get_object_or_404(Transaction, crop_receipt__farmer=farmer,
                                    pk=sale_pk)
    return render_to_response('farmers/sale.html', {
        'farmer': farmer,
        'transaction': transaction,
    }, context_instance=RequestContext(request))


@login_required
@SpecificRightsRequired(agent=True)
def farmer_new_sale(request, farmer_pk):
    actor = request.user.get_profile()
    agent = actor.as_agent()

    farmer = get_object_or_404(Farmer, pk=farmer_pk)
    form = forms.SelectCropForm()
    form.fields['crop_receipt'].queryset = agent.cropreceipts_available_for(
        farmer)
    return render_to_response('farmers/new_sale.html', {
        'farmer': farmer,
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
@SpecificRightsRequired(agent=True)
def farmer_new_sale_detail(request, farmer_pk):
    crop_receipt = get_object_or_404(CropReceipt,
                                     pk=request.GET.get('crop_receipt'))
    farmer = get_object_or_404(Farmer, pk=farmer_pk)
    actor = request.user.get_profile()
    agent = actor.as_agent()

    redirect_to_farmer = HttpResponseRedirect(reverse('fncs:farmer', kwargs={
        'farmer_pk': farmer_pk
    }))
    if request.method == "POST":
        if 'cancel' in request.POST:
            return redirect_to_farmer
        else:
            form = forms.TransactionForm(request.POST)
            if form.is_valid():
                price = form.cleaned_data['price']
                amount = form.cleaned_data['amount']
                agent.register_sale(crop_receipt, price, amount)
                messages.success(request, "New sale registered and %s will be"
                                 " notified via SMS" % (farmer.actor.name,))
                return redirect_to_farmer

    else:
        form = forms.TransactionForm(initial={
            'crop_receipt': crop_receipt.pk,
            'created_at': datetime.now(),
        })

    return render_to_response('farmers/new_sale_detail.html', {
        'form': form,
        'crop_receipt': crop_receipt
    }, context_instance=RequestContext(request))


@login_required
@SpecificRightsRequired(agent=True)
def farmer_messages(request, farmer_pk):
    actor = request.user.get_profile()
    farmer = get_object_or_404(Farmer, pk=farmer_pk)
    paginator = Paginator(farmer.actor.receivedmessages_set
                          .filter(sender=actor), 5)
    page = paginator.page(request.GET.get('p', 1))
    return render_to_response('farmers/messages.html', {
        'farmer': farmer,
        'paginator': paginator,
        'page': page
    }, context_instance=RequestContext(request))


@login_required
@SpecificRightsRequired(agent=True)
def farmer_new_message(request, farmer_pk):
    actor = request.user.get_profile()
    agent = actor.as_agent()
    farmer = get_object_or_404(Farmer, pk=farmer_pk)
    redirect_to_farmer = HttpResponseRedirect(reverse('fncs:farmer', kwargs={
        'farmer_pk': farmer.pk
    }))
    if request.method == "POST":

        if 'cancel' in request.POST:
            messages.success(request, 'Message cancelled')
            return redirect_to_farmer

        form = forms.MessageForm(request.POST)
        if form.is_valid():
            agent.send_message_to_farmer(farmer, form.cleaned_data['content'])
            messages.success(request, 'The message has been sent to %s via SMS'
                             % farmer.actor.name)
            return redirect_to_farmer
    else:
        form = forms.MessageForm()
    return render_to_response('farmers/new_message.html', {
        'farmer': farmer,
        'form': form
    }, context_instance=RequestContext(request))


@login_required
@SpecificRightsRequired(agent=True)
def farmer_notes(request, farmer_pk):
    actor = request.user.get_profile()
    agent = actor.as_agent()
    farmer = get_object_or_404(Farmer, pk=farmer_pk)
    paginator = Paginator(agent.notes_for(farmer), 5)
    page = paginator.page(request.GET.get('p', 1))
    return render_to_response('farmers/notes.html', {
        'farmer': farmer,
        'paginator': paginator,
        'page': page,
    }, context_instance=RequestContext(request))


@login_required
@SpecificRightsRequired(agent=True)
def farmer_new_note(request, farmer_pk):
    actor = request.user.get_profile()
    agent = actor.as_agent()
    farmer = get_object_or_404(Farmer, pk=farmer_pk)
    redirect_to_farmer_notes = HttpResponseRedirect(
        reverse('fncs:farmer_notes', kwargs={'farmer_pk': farmer_pk}))

    if request.method == "POST":
        if 'cancel' in request.POST:
            return redirect_to_farmer_notes

        form = forms.NoteForm(request.POST)
        if form.is_valid():
            agent.write_note(farmer, form.cleaned_data['content'])
            messages.success(request, 'Note has been saved')
            return redirect_to_farmer_notes
    else:
        form = forms.NoteForm()
    return render_to_response('farmers/new_note.html', {
        'farmer': farmer,
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
@SpecificRightsRequired(agent=True)
def farmer_profile(request, farmer_pk):
    farmer = get_object_or_404(Farmer, pk=farmer_pk)
    return render_to_response('farmers/profile.html', {
        'farmer': farmer
    }, context_instance=RequestContext(request))


@login_required
@SpecificRightsRequired(agent=True)
def group_messages(request):
    actor = request.user.get_profile()
    paginator = Paginator(GroupMessage.objects.filter(sender=actor), 5)
    page = paginator.page(request.GET.get('p', 1))
    # import pdb; pdb.set_trace()
    return render_to_response('messages.html', {
        'paginator': paginator,
        'page': page
    }, context_instance=RequestContext(request))


@login_required
@SpecificRightsRequired(agent=True, ext_officer=True)
def group_message_new(request):
    actor = request.user.get_profile()
    agent = actor.as_agent() if actor.is_agent() else None

    choose_district = None  # Used to determine if render district field

    if request.method == "POST":
        if 'cancel' in request.POST:
            messages.success(request, 'Message Cancelled')
            return HttpResponseRedirect(reverse('fncs:messages'))
        else:
            form = forms.FarmerGroupCreateFilterForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                # The code below only gets triggered when district has been selected
                if data["district"]:
                    # Generating the list for url encode
                    district_list = [("district", d.id) for d in data["district"]]
                    url_list = [("crop", data["crop"].id)] + district_list
                    return HttpResponseRedirect('%s?%s' % (
                            reverse('fncs:group_message_write'),
                            urllib.urlencode(url_list)))


                # If the user is an agent dynamically generate select field.
                if actor.is_agent():
                    included = (Crop.objects.filter(farmer_crop__agent_farmer=agent).
                                all().distinct())

                    if data["crop"] not in included:
                        messages.error(request, 'Invalid crop, please select your crop.')
                        return HttpResponseRedirect(reverse('fncs:group_message_new'))

                    # Dynamically setting the district Choice field
                    form.fields["district"].queryset = (District.
                                                    objects.
                                                    filter(farmer_district__agent_farmer=agent).
                                                    filter(farmer_district__crops=data["crop"]).
                                                    all().
                                                    distinct())

                    # Setting the total cound of farmers in the District
                    form.fields["district"].label_from_instance = (lambda obj: "%s (%s)" %
                                                                   (obj.name,
                                                                    obj.get_farmer_count(agent,
                                                                                         data["crop"])))

                # If form.is_valid() first time round, hide the crop widget
                form.fields['crop'].widget = HiddenInput()
                choose_district = True
            else:
                # Dynamically setting the Crop queryset if form.is_invalid() if user is agent
                if actor.is_agent():
                    form.fields["crop"].queryset = (Crop.objects.
                                                    filter(farmer_crop__agent_farmer=agent).
                                                    all().
                                                    distinct())
                messages.error(request, 'There are some errors on the form')
    else:
        # If a get is done on the form render below
        form = forms.FarmerGroupCreateFilterForm()
        if actor.is_agent():
            form.fields["crop"].queryset = (Crop.objects.
                                            filter(farmer_crop__agent_farmer=agent).
                                            all().
                                            distinct())

    return render_to_response('group_messages_new.html', {
        'form': form,
        'choose_district': choose_district,
    }, context_instance=RequestContext(request))


@login_required
@SpecificRightsRequired(agent=True, ext_officer=True)
def group_message_write(request):
    actor = request.user.get_profile()

    crop = request.GET.getlist('crop')
    district = request.GET.getlist('district')

    if not crop or not district:
        raise Http404

    if request.method == "POST":

        if 'cancel' in request.POST:
            messages.success(request, 'The message has been cancelled')
            return HttpResponseRedirect(reverse('fncs:messages'))

        form = forms.GroupMessageForm(request.POST)
        if form.is_valid():
            content = form.cleaned_data['content']

            # Creating the farmer group model
            crop_obj = get_object_or_404(Crop, pk__in=crop)
            district_obj = District.objects.filter(pk__in=district).all()
            district_names = [obj.name for obj in district_obj]
            name = "%s farmers in %s " % (crop_obj.name, " & ".join(district_names))
            farmergroups = FarmerGroup(crop=crop_obj,
                                       actor=actor,
                                       name=name)
            farmergroups.save()

            # Adding District Obj to M2M field as *args
            farmergroups.district.add(*district_obj)

            actor.send_message_to_farmergroups(farmergroups, content)
            messages.success(request, 'The message has been sent to all group'
                             ' members via SMS')
            return HttpResponseRedirect(reverse('fncs:messages'))
        else:
            messages.error(request, 'There are some errors on the form')
    else:
        form = forms.GroupMessageForm()

    return render_to_response('group_messages_write.html', {
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
@SpecificRightsRequired(agent=True)
def sales(request):
    return render_to_response('sales.html', {
    }, context_instance=RequestContext(request))


@login_required
@SpecificRightsRequired(agent=True)
def sales_crops(request):
    agent = request.user.get_profile().as_agent()
    paginator = Paginator(agent.transactions(), 5)
    page = paginator.page(request.GET.get('p', 1))
    return render_to_response('sales_crops.html', {
        'sales': sales,
        'paginator': paginator,
        'page': page
    }, context_instance=RequestContext(request))


@login_required
@SpecificRightsRequired(agent=True)
def sales_agents(request):
    return render_to_response('sales_agents.html', {
    }, context_instance=RequestContext(request))


@login_required
@SpecificRightsRequired(agent=True)
def sales_agent_breakdown(request):
    return render_to_response('sales_agent_breakdown.html', {
    }, context_instance=RequestContext(request))


@login_required
@SpecificRightsRequired(agent=True)
def farmer_crops(request, farmer_pk):
    farmer = get_object_or_404(Farmer, pk=farmer_pk)
    if request.method == "POST":
        form = forms.CropsForm(request.POST)
        if form.is_valid():
            selected_crops = form.cleaned_data['crops']
            farmer.grows_crops_exclusively(selected_crops)
            messages.success(request, 'Crops have been updated')
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
@SpecificRightsRequired(agent=True)
def farmer_edit(request, farmer_pk):
    farmer = get_object_or_404(Farmer, pk=farmer_pk)
    actor = farmer.actor
    user = actor.user
    if request.method == "POST":
        form = forms.FarmerForm(request.POST)
        if form.is_valid():
            user.first_name = form.cleaned_data['name']
            user.last_name = form.cleaned_data['surname']
            user.username = form.cleaned_data['msisdn1']
            user.save()

            farmer.operates_at_markets_exclusively(
                form.cleaned_data['markets'])
            farmer.id_number = form.cleaned_data['id_number']
            farmer.gender = form.cleaned_data['gender']

            farmer.actor.update_msisdns([
                form.cleaned_data['msisdn1'],
                form.cleaned_data['msisdn2'],
                form.cleaned_data['msisdn3'],
            ])

            farmer.save()
            messages.success(request, "Farmer Profile has been updated")
            return HttpResponseRedirect(reverse('fncs:farmer_crops', kwargs={
                'farmer_pk': farmer.pk
            }))
    else:
        msisdns = actor.get_msisdns()
        form = forms.FarmerForm(initial={
            'name': user.first_name,
            'surname': user.last_name,
            'msisdn1': msisdns[0],
            'msisdn2': msisdns[1] if len(msisdns) >= 2 else None,
            'msisdn3': msisdns[2] if len(msisdns) >= 3 else None,
            'markets': farmer.markets.all(),
            'id_number': farmer.id_number,
            'gender': farmer.gender,
        })
    return render_to_response('farmers/edit.html', {
        'form': form,
        'farmer': farmer
    }, context_instance=RequestContext(request))


@login_required
@SpecificRightsRequired(agent=True)
def market_prices(request):
    return render_to_response('markets/prices.html', {
    }, context_instance=RequestContext(request))


@login_required
@SpecificRightsRequired(agent=True)
def market_sales(request):
    paginator = Paginator(Market.objects.all(), 5)
    page = paginator.page(request.GET.get('p', 1))
    return render_to_response('markets/sales.html', {
        'paginator': paginator,
        'page': page,
    }, context_instance=RequestContext(request))


@login_required
@SpecificRightsRequired(agent=True)
def market_sale(request, market_pk):
    market = get_object_or_404(Market, pk=market_pk)
    paginator = Paginator(market.crops(), 5)
    page = paginator.page(request.GET.get('p', 1))
    return render_to_response('markets/sale.html', {
        'market': market,
        'paginator': paginator,
        'page': page
    }, context_instance=RequestContext(request))


@login_required
@SpecificRightsRequired(agent=True)
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
@SpecificRightsRequired(agent=True)
def crop_unit(request, market_pk, crop_pk, unit_pk):
    market = get_object_or_404(Market, pk=market_pk)
    crop = get_object_or_404(Crop, pk=crop_pk)
    unit = get_object_or_404(CropUnit, pk=unit_pk)
    transactions = Transaction.objects.filter(
        crop_receipt__unit=unit, crop_receipt__crop=crop,
        crop_receipt__market=market)
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
@SpecificRightsRequired(ext_officer=True)
def market_new(request):
    actor = request.user.get_profile()
    ext_officer = actor.as_extensionofficer()

    if not ext_officer:
        messages.error(request, "You need to be an extension officer to add new market")
        return redirect(reverse("fncs:home"))

    if request.method == "POST":
        form = forms.MarketForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "A new market has been created.")
            return redirect(reverse("fncs:home"))
    else:
        form = forms.MarketForm()

    context = {"form": form}
    return render(request,
                  'markets/market_new.html',
                  context)


@login_required
@SpecificRightsRequired(ext_officer=True)
def market_view(request):
    paginator = Paginator(Market.objects.all(), 5)
    page = paginator.page(request.GET.get('p', 1))
    context = {'paginator': paginator,
               'page': page,}
    return render(request,
                  "markets/market_view.html",
                  context)

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
@SpecificRightsRequired(agent=True)
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
@SpecificRightsRequired(agent=True)
def offer(request, market_pk, crop_pk):
    market = get_object_or_404(Market, pk=market_pk)
    crop = get_object_or_404(Crop, pk=crop_pk)
    offers = Offer.objects.filter(market=market, crop=crop)
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
@SpecificRightsRequired(agent=True)
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
@SpecificRightsRequired(agent=True)
def market_new_offer(request, *args, **kwargs):
    paginator = Paginator(Market.objects.all(), 5)
    page = paginator.page(request.GET.get('p', 1))
    return render_to_response('offers/markets.html', {
        'paginator': paginator,
        'page': page
    }, context_instance=RequestContext(request))


@login_required
@SpecificRightsRequired(agent=True)
def market_register_offer(request, market_pk):
    actor = request.user.get_profile()
    marketmonitor = actor.as_marketmonitor()
    market = get_object_or_404(Market, pk=market_pk)
    if request.method == "POST":

        if 'cancel' in request.POST:
            return HttpResponseRedirect(reverse('fncs:market_new_offer'))

        form = forms.OfferForm(request.POST)
        if form.is_valid():
            crop = form.cleaned_data['crop']
            unit = form.cleaned_data['unit']
            price_floor = form.cleaned_data['price_floor']
            price_ceiling = form.cleaned_data['price_ceiling']
            market = form.cleaned_data['market']
            marketmonitor.register_offer(market, crop, unit, price_floor,
                                         price_ceiling)
            messages.success(request, 'Opening price has been registered')
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


@login_required
@SpecificRightsRequired(agent=True)
def inventory(request):
    actor = request.user.get_profile()
    agent = actor.as_agent()
    paginator = Paginator(agent.cropreceipts_available(), 5)
    page = paginator.page(request.GET.get('p', 1))
    return render(request, 'inventory.html', {
        'agent': agent,
        'paginator': paginator,
        'page': page,
    })


@login_required
@SpecificRightsRequired(agent=True)
def inventory_sale(request):
    actor = request.user.get_profile()
    agent = actor.as_agent()
    farmer_pk = request.GET.get('farmer')
    if farmer_pk:
        farmer = get_object_or_404(Farmer, pk=farmer_pk)
        form = forms.CropReceiptSaleStep1Form(initial={
            'farmer': farmer
        })
        form.fields['farmer'].widget = HiddenInput()
    else:
        form = forms.CropReceiptSaleStep1Form()
    form.fields['farmer'].queryset = agent.farmers.all()
    return render(request, 'inventory_sale.html', {
        'agent': agent,
        'form': form,
    })


@login_required
@SpecificRightsRequired(agent=True)
def inventory_sale_details(request):
    actor = request.user.get_profile()
    agent = actor.as_agent()
    farmer = get_object_or_404(Farmer, pk=request.REQUEST.get('farmer'))
    crop_receipts = agent.cropreceipts_available_for(farmer)
    if not crop_receipts.exists():
        messages.error(request, "You don't have any inventory to sell for %s"
                       % (farmer,))
        return redirect(reverse('fncs:inventory_sale'))
    if request.method == "POST":
        form = forms.CropReceiptSaleStep2Form(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            price = form.cleaned_data['price']
            crop_receipt = form.cleaned_data['crop_receipt']
            remaining_inventory = crop_receipt.remaining_inventory()
            if remaining_inventory < amount:
                messages.error(request, "Selling beyond inventory, you only"
                               " have %s left" % (crop_receipt,))
            else:
                agent.register_sale(crop_receipt, amount, price)
                messages.success(request, "Sale registered succesfully")
                return redirect(reverse('fncs:inventory'))
    else:
        form = forms.CropReceiptSaleStep2Form(initial={
            'agent': agent,
            'farmer': farmer,
        })
    form.fields['crop_receipt'].queryset = crop_receipts
    return render(request, 'inventory_sale_details.html', {
        'agent': agent,
        'farmer': farmer,
        'form': form,
    })


@login_required
@SpecificRightsRequired(agent=True)
def inventory_intake(request):
    actor = request.user.get_profile()
    agent = actor.as_agent()
    form = forms.CropReceiptStep1Form(initial={
        'agent': agent,
    })
    form.fields['market'].queryset = agent.markets.all()
    return render(request, 'inventory_intake.html', {
        'form': form,
    })


@login_required
@SpecificRightsRequired(agent=True)
def inventory_intake_details(request):
    actor = request.user.get_profile()
    agent = actor.as_agent()
    market = get_object_or_404(Market, pk=request.REQUEST.get('market'))
    crop = get_object_or_404(Crop, pk=request.REQUEST.get('crop'))
    if request.method == "POST":
        form = forms.CropReceiptStep2Form(request.POST)
        if form.is_valid():
            market = form.cleaned_data['market']
            farmer = form.cleaned_data['farmer']
            amount = form.cleaned_data['amount']
            crop_unit = form.cleaned_data['crop_unit']
            crop = form.cleaned_data['crop']
            quality = form.cleaned_data['quality']
            receipt = agent.take_in_crop(market, farmer, amount,
                                         crop_unit, crop, quality=quality)
            if 'direct_sale' in request.POST:
                messages.success(request, u'%s has been added to your'
                                 ' inventory' % receipt)
                return redirect(reverse('fncs:inventory_direct_sale', kwargs={
                    'receipt_pk': receipt.pk,
                }))
            else:
                messages.success(request, u'%s has been added to your'
                                 ' inventory' % receipt)
                return redirect(reverse('fncs:inventory'))

    else:
        form = forms.CropReceiptStep2Form(initial={
            'agent': agent,
            'crop': crop,
            'market': market,
        })

    form.fields['crop_unit'].queryset = crop.units.all()
    form.fields['farmer'].queryset = market.farmer_set.all()
    return render(request, 'inventory_intake_details.html', {
        'agent': agent,
        'form': form,
        'crop': crop,
        'market': market,
    })


@login_required
@SpecificRightsRequired(agent=True)
def inventory_direct_sale(request, receipt_pk):
    actor = request.user.get_profile()
    agent = actor.as_agent()
    crop_receipt = get_object_or_404(CropReceipt, pk=receipt_pk)
    if request.method == "POST":
        form = forms.DirectSaleForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            price = form.cleaned_data['price']
            transaction = agent.register_sale(crop_receipt, amount, price)
            DirectSale.objects.create(transaction=transaction)
            messages.success(request, u'%s have been captured as a direct sale'
                             % (amount,))
            return redirect(reverse('fncs:inventory'))
    else:
        form = forms.DirectSaleForm(initial={
            'crop_receipt': crop_receipt,
            'amount': crop_receipt.amount,
        })
    return render(request, 'inventory_direct_sale.html', {
        'agent': agent,
        'form': form,
        'crop_receipt': crop_receipt,
    })


def todo(request):
    """Anything that resolves to here still needs to be completed"""
    return render_to_response('todo.html', {

    }, context_instance=RequestContext(request))


def health(request):
    return HttpResponse('')

@SpecificRightsRequired(ext_officer=True, superuser=True)
def agents(request):
    agents = Agent.objects.all()
    q = request.GET.get('q', '')
    if q:
        agents = agents.filter(actor__name__icontains=q)
    paginator = Paginator(agents, 5)
    page = paginator.page(request.GET.get('p', 1))
    return render(request, 'agents/index.html', {
        'page': page,
        'q': q,
    })


@login_required
@SpecificRightsRequired(ext_officer=True, superuser=True)
def agent(request, agent_pk):
    agent = get_object_or_404(Agent, pk=agent_pk)
    actor = agent.actor
    user = actor.user
    if request.method == "POST":
        form = forms.AgentForm(request.POST)
        if form.is_valid():
            user.first_name = form.cleaned_data['name']
            user.last_name = form.cleaned_data['surname']
            user.username = form.cleaned_data['msisdn']
            user.save()

            agent.msisdn = form.cleaned_data['msisdn']
            agent.farmers = form.cleaned_data['farmers']
            agent.markets = form.cleaned_data['markets']
            agent.save()

            messages.success(request, "Agent Profile has been updated")
            return HttpResponseRedirect(reverse("fncs:agents"))
    else:
        form = forms.AgentForm(initial={
            'name': user.first_name,
            'surname': user.last_name,
            'msisdn': user.username,
            'farmers': agent.farmers.all(),
            'markets': agent.markets.all(),
        })

    return render(request, 'agents/edit.html', {
        'agent': agent,
        'form': form,
    })


@login_required
@SpecificRightsRequired(ext_officer=True, superuser=True)
def agent_new(request):
    if request.method == "POST":
        form = forms.AgentForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            surname = form.cleaned_data['surname']
            msisdn = form.cleaned_data['msisdn']
            farmers = form.cleaned_data['farmers']
            markets = form.cleaned_data['markets']

            possible_matches = Agent.match(msisdns=[msisdn])
            if possible_matches:
                messages.info(request, "This agent already exists.")
            else:
                Agent.create(msisdn, name, surname, farmers, markets)
                messages.success(request, "Agent Created")
                return HttpResponseRedirect(reverse("fncs:agents"))
    else:
        form = forms.AgentForm()

    return render(request, 'agents/new.html', {
        'form': form,
    })
