# utils.py or apps/common/utils.py
from django.utils.text import slugify

def generate_unique_slug(instance, text_to_slug, slug_field_name="slug"):
    """
    Generates a unique slug for a model instance based on a provided text field.
    Automatically appends -1, -2, etc., if a collision is found.
    
    :param instance: The model instance (e.g., self)
    :param text_to_slug: The string to slugify (e.g., self.name or self.title)
    :param slug_field_name: The name of the slug field on the model (default: "slug")
    """
    if not text_to_slug:
        return ""

    base_slug = slugify(text_to_slug)
    slug = base_slug
    counter = 1
    
    # Get the model class dynamically from the instance
    model_class = instance.__class__
    
    # Query for existing slugs, excluding the current instance if it's being updated
    # Note: Use objects_all or default manager depending on your soft-delete setup
    queryset = model_class.objects.filter(**{slug_field_name: slug})
    if instance.pk:
        queryset = queryset.exclude(pk=instance.pk)

    while queryset.exists():
        slug = f"{base_slug}-{counter}"
        counter += 1
        queryset = model_class.objects.filter(**{slug_field_name: slug})
        if instance.pk:
            queryset = queryset.exclude(pk=instance.pk)

    return slug