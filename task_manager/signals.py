from django.db.models.signals import post_save
from django.dispatch import receiver

from task_manager.models import Task, NotificationType, Notification


def send_notification_to_assignees(
        task: Task,
        notification_type: NotificationType
):
    for user in task.assignees.all():
        Notification.objects.create(
            user=user,
            notification_type=notification_type,
            task=task
        )


@receiver(post_save, sender=Task)
def task_created(sender, instance: Task, created, **kwargs):
    if created:
        try:
            notification_type = NotificationType.objects.get(
                name="task_created"
            )
        except NotificationType.DoesNotExist:
            notification_type = NotificationType.objects.create(
                name="task_created",
                message_template=("{task.requester.first_name} "
                                  "{task.requester.last_name} "
                                  "created a new task \"{task.name}\"")
            )
        send_notification_to_assignees(instance, notification_type)


@receiver(post_save, sender=Task)
def task_updated(sender, instance, created, **kwargs):
    if not created and not instance.is_completed:
        try:
            notification_type = NotificationType.objects.get(
                name="task_updated"
            )
        except NotificationType.DoesNotExist:
            notification_type = NotificationType.objects.create(
                name="task_updated",
                message_template=("{task.requester.first_name} "
                                  "{task.requester.last_name} "
                                  "updated the task \"{task.name}\"")
            )
        send_notification_to_assignees(instance, notification_type)


@receiver(post_save, sender=Task)
def task_completed(sender, instance, created, **kwargs):
    if not created and instance.is_completed:
        try:
            notification_type = NotificationType.objects.get(
                name="task_completed"
            )
        except NotificationType.DoesNotExist:
            notification_type = NotificationType.objects.create(
                name="task_completed",
                message_template=("{task.requester.first_name} "
                                  "{task.requester.last_name} "
                                  "marked the task \"{task.name}\" "
                                  "as completed")
            )
        send_notification_to_assignees(instance, notification_type)
