import csv
from collections import defaultdict
from django.http import HttpResponse

from magriculture.fncs.tasks import export_transactions


class ExportAsCSV(object):
    """
    This Class returns an export csv action

    'fields' is a list of tuples denoting the field and label to be exported. Labels
    make up the header row of the exported file if header=True.

        fields=[
                ('field1', 'label1'),
                ('field2', 'label2'),
                ('field3', 'label3'),
            ]

    'exclude' is a flat list of fields to exclude. If 'exclude' is passed,
    'fields' will not be used. Either use 'fields' or 'exclude.'

        exclude=['field1', 'field2', field3]

    'header' is whether or not to output the column names as the first row

    Based on: http://djangosnippets.org/snippets/2020/
    """
    short_description = "Export selected records as CSV file"

    def __init__(self, description="Export selected records as CSV file", fields=None, exclude=None, header=True):
        self.description = description
        self.fields = fields
        self.exclude = exclude
        self.header = header

    def __call__(self, modeladmin, request, queryset):
        """
        Generic csv export admin action.
        based on http://djangosnippets.org/snippets/1697/
        """
        opts = modeladmin.model._meta
        field_names = [field.name for field in opts.fields]
        labels = []
        if self.exclude:
            field_names = [v for v in field_names if v not in self.exclude]
        elif self.fields:
            field_names = [k for k, v in self.fields if k in field_names]
            labels = [v for k, v in self.fields if k in field_names]

        response = HttpResponse(mimetype='text/csv')
        response['Content-Disposition'] = ('attachment; filename=%s.csv'
                                           % unicode(opts).replace('.', '_'))

        writer = csv.writer(response)
        if self.header:
            if labels:
                writer.writerow(labels)
            else:
                writer.writerow(field_names)
        for obj in queryset:
            writer.writerow([unicode(getattr(obj, field)).encode('utf-8')
                            for field in field_names])
        return response


class ExportAsCSVWithFK(object):
    short_description = "Export selected records as CSV file"

    def __init__(self, fields, header=True):
        self.fields = fields
        self.header = header

    def __call__(self, modeladmin, request, queryset):
        """
        Generic csv export admin action.
        based on http://djangosnippets.org/snippets/1697/
        """
        opts = modeladmin.model._meta

        field_names = [k for k, v in self.fields]
        labels = [v for k, v in self.fields]

        response = HttpResponse(mimetype='text/csv')
        response['Content-Disposition'] = ('attachment; filename=%s.csv'
                                           % unicode(opts).replace('.', '_'))

        writer = csv.writer(response)
        if self.header:
            writer.writerow(labels)

        for obj in queryset:
            data = []
            for field_name in field_names:
                field_obj = obj
                for name in field_name.split("__"):
                    if hasattr(field_obj, name):
                        field_obj = getattr(field_obj, name)
                    else:
                        field_obj = "ERROR!"
                        break

                data.append(field_obj)
            data = [unicode(entry).encode('utf-8') for entry in data]
            writer.writerow(data)
        return response


class ExportAsCSVWithFKTask(object):
    short_description = "Export selected records as CSV file via Email"

    def __init__(self, fields, header=True):
        self.fields = fields
        self.header = header

    def __call__(self, modeladmin, request, queryset):
        """
        Fires off to celery for long running exports
        """

        field_names = [k for k, v in self.fields]
        labels = [v for k, v in self.fields]
        modeladmin.message_user(
            request, "Exporting records, will be sent via email to shortly")

        return export_transactions.delay(
            field_names, labels, queryset, request.user)


class ExportFarmersAsCSV(object):
    """
    Return a custom exporter for farmers that includes:

    * The farmer ID
    * The actor ID
    * The actor name
    * The first MSISDN associated with the farmer
    * The number of MSISDNs associated with the farmer
    * The first markets associated with the farmer
    * The number of markets associated with the farmer
    * The ID and name of the crop which the farmer has sold the most often.
    """
    short_description = "Custom export of selected farmers as CSV file"

    def _get_most_sold_crop(self, farmer):
        """
        Find the crop the farmer has sold the most often.
        """
        crops_sold = defaultdict(int)
        most_sold_crop = None
        most_amount_sold = 0

        for receipt in farmer.cropreceipt_set.all():
            crop = receipt.crop
            crops_sold[crop.id] += 1
            if crops_sold[crop.id] > most_amount_sold:
                most_sold_crop = crop
                most_amount_sold = crops_sold[crop.id]

        return most_amount_sold, most_sold_crop

    def __call__(self, modeladmin, request, queryset):
        """
        Export farmer records as CSV.
        """
        response = HttpResponse(mimetype='text/csv')
        response['Content-Disposition'] = (
            'attachment; filename=fncs_farmer.csv')

        writer = csv.writer(response)
        writer.writerow([
            'FarmerID', 'ActorID', 'Farmer Name',
            'First MSISDN', 'Number of MSISDNs',
            'First Market', 'Number of Markets',
            'Best CropID', 'Best Crop Name', 'Best Crop Amount',
        ])
        for farmer in queryset:
            row = [farmer.id, farmer.actor.id, farmer.actor.name]
            msisdns = farmer.actor.get_msisdns()
            msisdn = msisdns[0] if msisdns else ''
            row += [msisdn, len(msisdns)]
            markets = farmer.markets.all()
            market = markets[0].name if markets else ''
            row += [market, len(markets)]
            amount, crop = self._get_most_sold_crop(farmer)
            if crop:
                row += [crop.id, crop.name, amount]
            else:
                row += ['', '', 0]

            writer.writerow([
                unicode(value).encode('utf-8') for value in row])
        return response
