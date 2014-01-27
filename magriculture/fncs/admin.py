# Django
from django.contrib import admin

# Project
from magriculture.fncs.models import actors, props, geo
from magriculture.fncs.actions import ExportAsCSV, ExportAsCSVWithFK

# Setting the fields and ExportAsCSV Outside the class

fields = [("crop_receipt__farmer__actor__name", "Farmer Name"),
                  ("crop_receipt__farmer__gender", "Gender"),
                  ("created_at", "Transaction Date"),
                  ("crop_receipt__crop", "Crop"),
                  ("crop_receipt__unit", "Unit"),
                  ("amount", "No of Units"),
                  ("total", "Total Price Achieved"),
                  ("crop_receipt__market", "Market"),
                  ("crop_receipt__agent__actor__name", "Agent"),
                  ("crop_receipt__agent__actor__gender", "Agent Gender")]
farmer_export = ExportAsCSVWithFK(fields)

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
        if "export_csv" in actions:
            del actions["export_csv"]

        # action in format described by django docs
        # `(function, name, short_description) tuple`
        actions["farmer_export"] = (farmer_export,
                                    "farmer_export",
                                    farmer_export.short_description)
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
admin.site.register(props.CropReceipt)
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
admin.site.add_action(export_records_as_csv, "export_csv")
