from django.forms import ValidationError
from rest_framework import serializers

from .models import Product, Supplier


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name", "model", "release_date", "supplier"]


class SupplierSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)

    class Meta:
        model = Supplier
        fields = [
            "id",
            "name",
            "email",
            "country",
            "city",
            "street",
            "house_number",
            "products",
            "supplier",
            "supplier_type",
            "debt",
            "created_at",
        ]
        read_only_fields = ["debt", "created_at"]

    def validate(self, data):
        instance = self.instance if self.instance else Supplier(**data)

        for attr, value in data.items():
            setattr(instance, attr, value)

        try:
            instance.clean()
        except ValidationError as e:
            raise serializers.ValidationError(str(e))

        return data
