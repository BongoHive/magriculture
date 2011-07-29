from django.contrib import admin
from magriculture.fncs.models import actors, props, geo

admin.site.register(actors.Actor)
admin.site.register(actors.Farmer)
admin.site.register(actors.FarmerGroup)
admin.site.register(actors.ExtensionOfficer)
admin.site.register(actors.MarketMonitor)
admin.site.register(actors.Agent)

admin.site.register(props.Crop)
admin.site.register(props.CropUnit)
admin.site.register(props.Transaction)
admin.site.register(props.Offer)
admin.site.register(props.Message)
admin.site.register(props.GroupMessage)

admin.site.register(geo.Province)
admin.site.register(geo.RPIArea)
admin.site.register(geo.Zone)
admin.site.register(geo.District)
admin.site.register(geo.Ward)
admin.site.register(geo.Village)
admin.site.register(geo.Market)
