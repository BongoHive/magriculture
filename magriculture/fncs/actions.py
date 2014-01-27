import csv
from django.http import HttpResponse


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
                field_obj = None
                # uses the "__" to separate into foreign keys
                if "__" in field_name:
                    field_obj = obj
                    for fk_field_name in field_name.split("__"):
                        if hasattr(field_obj, fk_field_name):
                            field_obj = getattr(field_obj, fk_field_name)
                        else:
                            field_obj = "ERROR!"
                            break
                else:
                    if hasattr(obj, field_name):
                        field_obj = getattr(obj, field_name)
                    else:
                        field_obj = "ERROR!"

                data.append(field_obj)
            data = [unicode(entry).encode('utf-8') for entry in data]
            writer.writerow(data)
        return response
