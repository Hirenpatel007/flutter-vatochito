from celery import shared_task


@shared_task
def send_push_notification(message_id: int) -> None:
    # Placeholder for async push notification dispatch
    return None
