from django.contrib import admin
from magriculture.fncs.models import actors, props, geo
from magriculture.fncs.actions import export_select_fields_csv_action


class DownloadAsCSVActionAdmin(admin.ModelAdmin):
    actions = [export_select_fields_csv_action("Export selected objects as CSV file")]

# ==========================================================================
# Actors
# ==========================================================================
class ActorAdmin(DownloadAsCSVActionAdmin):
    list_display = ('user', 'name', 'gender')
    search_fields = ('name',)


class FarmerAdmin(DownloadAsCSVActionAdmin):
    list_display = ('__unicode__', 'actor')
    search_fields = ('actor__name',)


class AgentAdmin(DownloadAsCSVActionAdmin):
    list_display = ('__unicode__', 'actor')
    search_fields = ('actor__name',)


admin.site.register(actors.Actor, ActorAdmin)
admin.site.register(actors.Farmer, FarmerAdmin)
admin.site.register(actors.Agent, AgentAdmin)
admin.site.register(actors.FarmerGroup, DownloadAsCSVActionAdmin)
admin.site.register(actors.ExtensionOfficer, DownloadAsCSVActionAdmin)
admin.site.register(actors.MarketMonitor, DownloadAsCSVActionAdmin)
admin.site.register(actors.FarmerBusinessAdvisor, DownloadAsCSVActionAdmin)
admin.site.register(actors.Identity, DownloadAsCSVActionAdmin)

# ==========================================================================
# Props
# ==========================================================================
admin.site.register(props.Crop, DownloadAsCSVActionAdmin)
admin.site.register(props.CropUnit, DownloadAsCSVActionAdmin)
admin.site.register(props.Transaction, DownloadAsCSVActionAdmin)
admin.site.register(props.Offer, DownloadAsCSVActionAdmin)
admin.site.register(props.Message, DownloadAsCSVActionAdmin)
admin.site.register(props.GroupMessage, DownloadAsCSVActionAdmin)
admin.site.register(props.CropReceipt, DownloadAsCSVActionAdmin)

# ==========================================================================
# Geo
# ==========================================================================
admin.site.register(geo.Province, DownloadAsCSVActionAdmin)
admin.site.register(geo.RPIArea, DownloadAsCSVActionAdmin)
admin.site.register(geo.Zone, DownloadAsCSVActionAdmin)
admin.site.register(geo.District, DownloadAsCSVActionAdmin)
admin.site.register(geo.Ward, DownloadAsCSVActionAdmin)
admin.site.register(geo.Market, DownloadAsCSVActionAdmin)
