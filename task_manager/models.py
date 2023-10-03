from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.text import slugify


class Position(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Worker(AbstractUser):
    position = models.ForeignKey(Position, on_delete=models.CASCADE)

    class Meta:
        ordering = ["position", "first_name", "last_name"]

    def __str__(self):
        return f"{self.position}: {self.first_name} {self.last_name}"


class Team(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True)
    members = models.ManyToManyField(Worker)

    class Meta:
        ordering = ["name"]

    def save(
            self,
            force_insert=False,
            force_update=False,
            using=None,
            update_fields=None
    ):
        if not self.slug:
            self.slug = slugify(self.name)
        super(Team, self).save(
            force_insert,
            force_update,
            using,
            update_fields
        )

    def __str__(self):
        return self.name
