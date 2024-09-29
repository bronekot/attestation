from django.core.exceptions import ValidationError
from django.db import models


class Supplier(models.Model):
    SUPPLIER_TYPE_CHOICES = [
        ("factory", "Завод"),
        ("retail", "Розничная сеть"),
        ("entrepreneur", "Индивидуальный предприниматель"),
    ]

    name = models.CharField(max_length=255, verbose_name="Название")
    email = models.EmailField()
    country = models.CharField(max_length=255, verbose_name="Страна")
    city = models.CharField(max_length=255, verbose_name="Город")
    street = models.CharField(max_length=255, verbose_name="Улица")
    house_number = models.CharField(max_length=10, verbose_name="Номер дома")

    supplier = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True, related_name="clients", verbose_name="Поставщик"
    )
    debt = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Задолженность")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    supplier_type = models.CharField(
        max_length=20, choices=SUPPLIER_TYPE_CHOICES, default="retail", verbose_name="Тип поставщика"
    )

    @property
    def level(self):
        if self.supplier is None:
            return 0
        return self.supplier.level + 1

    def clean(self):
        if self.supplier_type == "factory" and self.supplier is not None:
            raise ValidationError("Завод не может иметь поставщика.")
        if self.supplier_type == "factory" and self.debt != 0.00:
            raise ValidationError("У завода не может быть задолженности.")
        if self.level == 0 and self.debt != 0.00:
            raise ValidationError("У нулевого уровня не может быть задолженности.")
        if self.debt < 0:
            raise ValidationError("Задолженность не может быть отрицательной.")
        if self.supplier == self:
            raise ValidationError("Поставщик не может ссылаться сам на себя.")
        super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Поставщик"
        verbose_name_plural = "Поставщики"


class Product(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название")
    model = models.CharField(max_length=255, verbose_name="Модель")
    release_date = models.DateField(verbose_name="Дата выпуска")
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name="products", verbose_name="Поставщик")

    def __str__(self):
        return f"{self.name} ({self.model})"

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
