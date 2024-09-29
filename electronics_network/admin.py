from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.forms import ModelForm

from .models import Product, Supplier


class ProductInline(admin.TabularInline):
    model = Product
    extra = 1


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ("name", "supplier_type", "city", "country", "debt", "created_at", "level")
    list_filter = ("city",)
    search_fields = ("name", "city")

    inlines = [ProductInline]

    actions = ["clear_debt"]

    def clear_debt(self, request, queryset):
        queryset.update(debt=0.00)

    clear_debt.short_description = "Очистить задолженность перед поставщиком"

    def save_model(self, request, obj, form, change):
        try:
            obj.full_clean()
            super().save_model(request, obj, form, change)
        except ValidationError as e:
            self.message_user(request, f"Ошибка: {e}", level=messages.ERROR)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "model", "release_date", "supplier")
    search_fields = ("name", "model")


class SupplierAdminForm(ModelForm):
    class Meta:
        model = Supplier
        fields = "__all__"

    class Media:
        js = ("admin/js/supplier_admin.js",)
