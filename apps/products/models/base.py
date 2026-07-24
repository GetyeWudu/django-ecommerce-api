
from django.db import models


from django.utils import timezone


class SoftDeleteModel(models.Model):

    is_deleted = models.BooleanField(
        default=False,
    )

    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    def soft_delete(self):

        self.is_deleted = True

        self.deleted_at = timezone.now()

        self.save(
            update_fields=[
                "is_deleted",
                "deleted_at",
            ]
        )

    def restore(self):

        self.is_deleted = False

        self.deleted_at = None

        self.save(
            update_fields=[
                "is_deleted",
                "deleted_at",
            ]
        )

    class Meta:
        abstract = True

class SoftDeleteQuerySet(models.QuerySet):

    def active(self):
        return self.filter(
            is_deleted=False
        )

    def deleted(self):
        return self.filter(
            is_deleted=True
        )        
class SoftDeleteManager( models.Manager):

    def get_queryset(self):

        return super().get_queryset().filter(
            is_deleted=False
        )    