# Generated by Django 4.2.5 on 2024-02-24 11:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("task_manager", "0003_alter_project_slug_alter_task_name_alter_team_slug"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="task",
            options={"ordering": ["is_completed", "-priority", "name"]},
        ),
    ]
