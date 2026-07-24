from django.db import models

from apps.products.utils import generate_unique_slug
from .base import SoftDeleteModel
from .base import SoftDeleteManager
from .category import Category
from .tag import Tag
from django.utils.text import slugify

class Product(SoftDeleteModel):

    name = models.CharField(
        max_length=255,
    )

    slug = models.SlugField(
        max_length=280,
        unique=True,
        blank=True,
    )

    description = models.TextField(
        blank=True,
    )

    categories = models.ManyToManyField(
        Category,
        related_name="products",
        blank=True,
    )

    tags = models.ManyToManyField(
        Tag,
        related_name="products",
        blank=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    objects = SoftDeleteManager()

    all_objects = models.Manager()
    class Meta:
        verbose_name_plural = "Products"
    def __str__(self):

        return self.name
    def create(self, validated_data):
        # Automatically generate slug from name
        name = validated_data.get("name")
        if name:
            validated_data["slug"] = slugify(name)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Update slug if the name changes
        name = validated_data.get("name", instance.name)
        if name:
            validated_data["slug"] = generate_unique_slug(self, self.name)
        return super().update(instance, validated_data)
    def save(self, *args, **kwargs):
            # Auto-generate unique slug if it's empty or if the name changed
            if not self.slug:
                self.slug = generate_unique_slug(self, self.name)
                
            super().save(*args, **kwargs)
