from django.core.management.base import BaseCommand
from optparse import make_option
import sys
import xlrd

def effective_page_range_for(page, paginator, delta=3):
    return [p for p in range(page.number - delta, page.number + delta + 1)
                if (p > 0 and p <= paginator.num_pages)]

def read_excel_sheet(filename):
    book = xlrd.open_workbook(filename, encoding_override="cp1252")
    # only using first sheet
    sheet = book.sheet_by_index(0)
    # assume the column names are the first row
    column_names = sheet.row_values(0)
    return [zip(column_names, sheet.row_values(row_index))
            for row_index in range(1, sheet.nrows)]

def read_excel_sheet_as_dict(filename):
    return [dict(row) for row in read_excel_sheet(filename)]

def normalise_msisdn(msisdn, country_code='+260'):
    # replace all '09....' numbers with '+2609....' numbers,
    # strip all spaces and add a '+' if missing from
    # international number
    msisdn = msisdn.replace(' ','')
    if msisdn[0:2] == '09':
        msisdn = country_code + msisdn[1:]
    elif msisdn[0:3] == '260':
        msisdn = '+' + msisdn
    return msisdn

class ImportCommand(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--filename', dest='filename', default='', type='str',
                        help='File to read'),
        make_option('--verbose', dest='verbose', default=False),
    )

    def handle(self, *args, **options):
        filename = options['filename']
        if not filename:
            sys.exit('Please provide --filename')
        print 'Reading from %s' % filename
        print '=' * 10
        print
        data = read_excel_sheet_as_dict(filename)
        for row in data:
            if options.get('verbose'):
                print row
            self.handle_row(row)
        print '... done'
        print
        print

    def handle_row(self, row):
        pass
