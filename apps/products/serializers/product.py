from rest_framework import serializers
from apps.products.models.product import Product, Category, Tag
from .category import CategorySerializer, CategoryReadSerializer
from .tag import TagSerializer, TagReadSerializer
from .variant import ProductVariantReadSerializer
from .productImage import ProductImageSerializer


class ProductReadSerializer(serializers.ModelSerializer):
    categories = CategoryReadSerializer(many=True, read_only=True)
    tags = TagReadSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "categories",
            "tags",
            "is_active",
            "created_at",
            "updated_at",
        ]


class ProductDetailSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    variants = ProductVariantReadSerializer(many=True, read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "categories",
            "tags",
            "variants",
            "images",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ProductWriteSerializer(serializers.ModelSerializer):
    slug = serializers.CharField(read_only=True)
    categories = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), many=True, required=False
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True, required=False
    )

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "categories",
            "tags",
            "is_active",
        ]
        read_only_fields = ["id", "slug"]

    def validate_categories(self, categories):
        if not categories:
            raise serializers.ValidationError(
                "Product must belong to at least one category."
            )
        return categories

    def create(self, validated_data):
        categories = validated_data.pop("categories", [])
        tags = validated_data.pop("tags", [])
        product = super().create(validated_data)
        product.categories.set(categories)
        product.tags.set(tags)
        return product

    def update(self, instance, validated_data):
        categories = validated_data.pop("categories", None)
        tags = validated_data.pop("tags", None)
        product = super().update(instance, validated_data)
        if categories is not None:
            product.categories.set(categories)
        if tags is not None:
            product.tags.set(tags)
        return product


class ProductListSerializer(serializers.ModelSerializer):
    starting_price = serializers.SerializerMethodField()
    currency = serializers.SerializerMethodField()
    primary_image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "starting_price",
            "currency",
            "primary_image",
        ]

    def get_starting_price(self, obj):
        variant = min(
            obj.variants.all(),
            key=lambda v: v.price,
            default=None,
        )
        return variant.price if variant else None

    def get_currency(self, obj):
        variant = min(
            obj.variants.all(),
            key=lambda v: v.price,
            default=None,
        )
        return variant.currency if variant else None

    def get_primary_image(self, obj):
        image = obj.images.filter(is_primary=True).first()
        if not image:
            return None

        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(image.image.url)
        return image.image.url