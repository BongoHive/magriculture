# Django
from django.contrib import admin

# Project
from magriculture.fncs.models import actors, props, geo
from magriculture.fncs.actions import ExportAsCSV, ExportAsCSVWithFK

# ==========================================================================
# Actors
# ==========================================================================
class ActorAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'gender')
    search_fields = ('name',)


class FarmerAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'actor')
    search_fields = ('actor__name',)


class AgentAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'actor')
    search_fields = ('actor__name',)


class TransactionAdmin(admin.ModelAdmin):
    def get_actions(self, request):
        actions = super(TransactionAdmin, self).get_actions(request)
        if "Export selected records as CSV file" in actions:
            # action in format described by django docs
            # `(function, name, short_description) tuple`
            fields = [("crop_receipt__farmer__actor__name", "Farmer Name"),
                      ("crop_receipt__farmer__gender", "Gender"),
                      ("crop_receipt__created_at", "Transaction Date"),
                      ("crop_receipt__crop", "Crop"),
                      ("crop_receipt__unit", "Unit"),
                      ("amount", "No of Units"),
                      ("total", "Total Price Achieved"),
                      ("crop_receipt__market", "Market"),
                      ("crop_receipt__agent__actor__name", "Agent"),
                      ("crop_receipt__agent__actor__gender", "Agent Gender")]
            actions["Export selected records as CSV file"] = (ExportAsCSVWithFK(fields=fields),
                                                             "Export selected records as CSV file",
                                                             "Export selected records as CSV file")
        return actions


admin.site.register(actors.Actor, ActorAdmin)
admin.site.register(actors.Farmer, FarmerAdmin)
admin.site.register(actors.Agent, AgentAdmin)
admin.site.register(actors.FarmerGroup)
admin.site.register(actors.ExtensionOfficer)
admin.site.register(actors.MarketMonitor)
admin.site.register(actors.FarmerBusinessAdvisor)
admin.site.register(actors.Identity)

# ==========================================================================
# Props
# ==========================================================================
admin.site.register(props.Crop)
admin.site.register(props.CropUnit)
admin.site.register(props.Transaction, TransactionAdmin)
admin.site.register(props.Offer)
admin.site.register(props.Message)
admin.site.register(props.GroupMessage)

# ==========================================================================
# Geo
# ==========================================================================
admin.site.register(geo.Province)
admin.site.register(geo.RPIArea)
admin.site.register(geo.Zone)
admin.site.register(geo.District)
admin.site.register(geo.Ward)
admin.site.register(geo.Market)

export_records_as_csv = ExportAsCSV()
admin.site.add_action(export_records_as_csv, "Export selected records as CSV file")
