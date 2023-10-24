# Generated by Django 4.2.5 on 2023-10-23 21:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("task_manager", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="task",
            name="description",
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name="task",
            name="is_completed",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="task",
            name="priority",
            field=models.PositiveSmallIntegerField(
                choices=[
                    (6, "Critical"),
                    (5, "Urgent"),
                    (4, "High"),
                    (3, "Middle"),
                    (2, "Low"),
                    (1, "Optional"),
                    (0, "Unknown"),
                ],
                default=0,
            ),
        ),
        migrations.AlterField(
            model_name="task",
            name="tags",
            field=models.ManyToManyField(
                blank=True, related_name="tasks", to="task_manager.tag"
            ),
        ),
        migrations.AlterField(
            model_name="worker",
            name="position",
            field=models.ForeignKey(
                default=5,
                on_delete=django.db.models.deletion.SET_DEFAULT,
                related_name="workers",
                to="task_manager.position",
            ),
        ),
    ]
