from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from task_manager.models import (
    Position,
    Task,
    NotificationType,
    Notification,
    Team
)


def on_transaction_commit(func):
    def inner(*args, **kwargs):
        transaction.on_commit(lambda: func(*args, **kwargs))
    return inner


@receiver(pre_delete, sender=Position)
def position_pre_delete(sender, instance: Position, **kwargs):
    instance.workers.update(position_id=Position.get_default_position().id)


@receiver(pre_delete, sender=get_user_model())
def user_pre_delete(sender, instance, **kwargs):
    for founded_team in instance.founded_teams.all():
        if founded_team.members:
            Team.objects.filter(pk=founded_team.pk).update(
                founder=founded_team.members.first()
            )
        else:
            founded_team.delete()
    deleted_user = get_user_model().get_deleted_user()
    for requested_task in instance.requested_tasks.all():
        Task.objects.filter(pk=requested_task.pk).update(
            requester=deleted_user
        )


@receiver(post_save, sender=get_user_model())
def user_post_save(sender, instance, **kwargs):
    if instance.position is None:
        get_user_model().objects.filter(pk=instance.pk).update(
            position_id=Position.get_default_position().id
        )


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
@on_transaction_commit
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
        if instance.assignees.all():
            send_notification_to_assignees(instance, notification_type)


@receiver(post_save, sender=Task)
@on_transaction_commit
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
