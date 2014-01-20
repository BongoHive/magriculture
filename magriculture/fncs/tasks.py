# Python
from datetime import datetime, timedelta

# Project
from magriculture.fncs.models.actors import Farmer, FarmerGroup, Agent
from magriculture.fncs.models.props import CropReceipt

# Celery
from celery.decorators import task


@task
def query_crop_receipt_for_old_crops():
    """
    This will form the celery worker that will be run to query
    the crop reciept for old stock
    """
    days_3_ago = datetime.today() - timedelta(days=3)
    crop_receipts = (CropReciept.objects.
                    filter(reconciled=False).
                    filter(created_at__lt=days_3_ago).
                    all())

    for crop_receipt in crop_receipts:
        check_inventory_left(crop_receipt)



def check_inventory_left(crop_receipt):
    """
    Function that checks inventory to see if there
    is any inventory left
    """
    if crop_receipt.remaining_inventory() > 0:
        recipient = crop_receipt.farmer.actor
        message = "These crops were unable to be sold"
        crop_receipt.agent.actor.send_message(recipient, message)
        crop_receipt.reconciled = True
