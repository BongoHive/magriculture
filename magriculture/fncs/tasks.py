# Django
from django.utils.translation import ugettext_lazy as _
from datetime import datetime, timedelta

# Project
from magriculture.fncs.models.actors import Farmer, FarmerGroup, Agent
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
    days_3_ago = datetime.today() - timedelta(days=days)
    crop_receipts = (CropReceipt.objects.
                    filter(reconciled=False).
                    filter(created_at__lt=days_3_ago).
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
