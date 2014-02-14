# Django
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from datetime import datetime, timedelta
from StringIO import StringIO
from zipfile import ZipFile, ZIP_DEFLATED
from django.core.mail import EmailMessage
import csv

# Project
from magriculture.fncs.models.props import CropReceipt

# Celery
from celery.utils.log import get_task_logger
from celery.decorators import task

logger = get_task_logger(__name__)

@task
def query_crop_receipt_for_old_crops(days):
    """
    This will form the celery worker that will be run to query
    the crop reciept for old stock
    """
    logger.info("Performing query for old Receipts")
    days_ago = datetime.today() - timedelta(days=days)
    crop_receipts = (CropReceipt.objects.
                    filter(reconciled=False).
                    filter(created_at__lt=days_ago).
                    all())

    for crop_receipt in crop_receipts:
        check_inventory_left(crop_receipt)


def check_inventory_left(crop_receipt):
    """
    Function that checks inventory to see if there
    is any inventory left.
    """
    logger.info("Running the inventory checker and send message")

    # Assuming that something went wrong and Reciepts with 0 crops is not reconciled
    remaining = crop_receipt.remaining_inventory()

    if remaining > 0:
        recipient = crop_receipt.farmer.actor
        crop = crop_receipt.crop.name
        message = (_("Sorry but %(remaining)s %(units)s of %(crop)s have not been sold") %
                   {'remaining': remaining, 'units': crop_receipt.unit.name, 'crop': crop})
        crop_receipt.agent.actor.send_message(recipient, message, None)
        crop_receipt.reconciled = True
        crop_receipt.save()


def email_export(recipient, io):
    zipio = StringIO()
    zf = ZipFile(zipio, "a", ZIP_DEFLATED)
    zf.writestr("transactions-export.csv", io.getvalue())
    zf.close()

    email = EmailMessage(
        'LimaLinks Transaction export snapshot',
        'Please find the transactions attached.',
        settings.DEFAULT_FROM_EMAIL, [recipient])
    email.attach('transactions-export.zip', zipio.getvalue(), 'application/zip')
    email.send()


@task(ignore_result=True)
def export_transactions(field_names, labels, queryset, user):
    """
    Export the transactions in the system including related users info.

    :param list field_names:
        model field names
    :param list labels:
        headers for the csv
    :param object queryset:
        queryset from user select
    :param User user:
        logged in admin user
    """
    logger.info("Exporting transactions")
    recipient = user.email
    labels = [l.encode('utf-8') for l in labels]

    io = StringIO()
    writer = csv.writer(io)
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
    email_export(recipient, io)
