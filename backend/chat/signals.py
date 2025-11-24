from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Message, MessageReceipt


@receiver(post_save, sender=Message)
def create_sender_receipt(sender, instance, created, **kwargs):
    if created:
        MessageReceipt.objects.get_or_create(message=instance, user=instance.sender, defaults={"state": MessageReceipt.SENT})
