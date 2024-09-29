from datetime import date

from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .admin import SupplierAdmin
from .models import Product, Supplier
from .serializers import ProductSerializer, SupplierSerializer

User = get_user_model()


class SupplierModelTest(TestCase):
    def setUp(self):
        self.supplier = Supplier.objects.create(
            name="Test Supplier",
            email="test@example.com",
            country="Test Country",
            city="Test City",
            street="Test Street",
            house_number="123",
            supplier_type="factory",
        )

    def test_supplier_creation(self):
        self.assertTrue(isinstance(self.supplier, Supplier))
        self.assertEqual(self.supplier.__str__(), self.supplier.name)

    def test_supplier_level(self):
        self.assertEqual(self.supplier.level, 0)
        child_supplier = Supplier.objects.create(
            name="Child Supplier",
            email="child@example.com",
            country="Child Country",
            city="Child City",
            street="Child Street",
            house_number="456",
            supplier_type="retail",
            supplier=self.supplier,
        )
        self.assertEqual(child_supplier.level, 1)


class ProductModelTest(TestCase):
    def setUp(self):
        self.supplier = Supplier.objects.create(
            name="Test Supplier",
            email="test@example.com",
            country="Test Country",
            city="Test City",
            street="Test Street",
            house_number="123",
            supplier_type="factory",
        )
        self.product = Product.objects.create(
            name="Test Product", model="Test Model", release_date=date.today(), supplier=self.supplier
        )

    def test_product_creation(self):
        self.assertTrue(isinstance(self.product, Product))
        self.assertEqual(self.product.__str__(), f"{self.product.name} ({self.product.model})")


class SupplierViewSetTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass", is_active=True)
        self.client.force_authenticate(user=self.user)
        self.supplier = Supplier.objects.create(
            name="Test Supplier",
            email="test@example.com",
            country="Test Country",
            city="Test City",
            street="Test Street",
            house_number="123",
            supplier_type="factory",
        )
        self.assertTrue(self.user.is_authenticated)
        self.assertTrue(self.user.is_active)
        self.assertEqual(Supplier.objects.count(), 1)
        self.url = reverse("supplier-list")

    def test_get_suppliers(self):
        self.assertEqual(Supplier.objects.count(), 1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_supplier(self):
        data = {
            "name": "New Supplier",
            "email": "new@example.com",
            "country": "New Country",
            "city": "New City",
            "street": "New Street",
            "house_number": "789",
            "supplier_type": "retail",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Supplier.objects.count(), 2)

    def test_update_supplier(self):
        url = reverse("supplier-detail", kwargs={"pk": self.supplier.pk})
        data = {"name": "Updated Supplier"}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.supplier.refresh_from_db()
        self.assertEqual(self.supplier.name, "Updated Supplier")

    def test_delete_supplier(self):
        url = reverse("supplier-detail", kwargs={"pk": self.supplier.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Supplier.objects.count(), 0)


class SerializerTests(TestCase):
    def setUp(self):
        self.supplier_data = {
            "name": "Test Supplier",
            "email": "test@example.com",
            "country": "Test Country",
            "city": "Test City",
            "street": "Test Street",
            "house_number": "123",
            "supplier_type": "factory",
        }
        self.supplier = Supplier.objects.create(**self.supplier_data)
        self.product_data = {
            "name": "Test Product",
            "model": "Test Model",
            "release_date": date.today(),
            "supplier": self.supplier,
        }
        self.product = Product.objects.create(**self.product_data)

    def test_supplier_serializer(self):
        serializer = SupplierSerializer(instance=self.supplier)
        for key, value in self.supplier_data.items():
            self.assertEqual(serializer.data[key], value)

    def test_product_serializer(self):
        serializer = ProductSerializer(instance=self.product)
        for key, value in self.product_data.items():
            if key == "supplier":
                self.assertEqual(serializer.data[key], value.pk)
            elif key == "release_date":
                self.assertEqual(serializer.data[key], value.isoformat())
            else:
                self.assertEqual(serializer.data[key], value)


class SupplierFilterTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass", is_active=True)
        self.client.force_authenticate(user=self.user)
        self.supplier1 = Supplier.objects.create(
            name="Supplier 1",
            email="supplier1@example.com",
            country="Country 1",
            city="City 1",
            street="Street 1",
            house_number="123",
            supplier_type="factory",
        )
        self.supplier2 = Supplier.objects.create(
            name="Supplier 2",
            email="supplier2@example.com",
            country="Country 2",
            city="City 2",
            street="Street 2",
            house_number="456",
            supplier_type="retail",
        )
        self.url = reverse("supplier-list")

    def test_filter_by_country(self):
        response = self.client.get(self.url, {"country": "Country 1"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Supplier 1")


class SupplierHierarchyTest(TestCase):
    def setUp(self):
        self.factory = Supplier.objects.create(
            name="Factory",
            email="factory@example.com",
            country="Country",
            city="City",
            street="Street",
            house_number="123",
            supplier_type="factory",
        )
        self.retail = Supplier.objects.create(
            name="Retail",
            email="retail@example.com",
            country="Country",
            city="City",
            street="Street",
            house_number="456",
            supplier_type="retail",
            supplier=self.factory,
        )
        self.entrepreneur = Supplier.objects.create(
            name="Entrepreneur",
            email="entrepreneur@example.com",
            country="Country",
            city="City",
            street="Street",
            house_number="789",
            supplier_type="entrepreneur",
            supplier=self.retail,
        )

    def test_hierarchy_levels(self):
        self.assertEqual(self.factory.level, 0)
        self.assertEqual(self.retail.level, 1)
        self.assertEqual(self.entrepreneur.level, 2)


class APIAccessTest(APITestCase):
    def setUp(self):
        self.employee = User.objects.create_user(username="employee", password="employeepass", is_active=True)
        self.non_employee = User.objects.create_user(
            username="nonemployee", password="nonemployeepass", is_active=False
        )
        self.url = reverse("supplier-list")

    def test_employee_access(self):
        self.client.force_authenticate(user=self.employee)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_non_employee_access(self):
        self.client.force_authenticate(user=self.non_employee)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminActionsTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.site = AdminSite()
        self.admin = SupplierAdmin(Supplier, self.site)
        self.supplier = Supplier.objects.create(
            name="Test Supplier",
            email="test@example.com",
            country="Test Country",
            city="Test City",
            street="Test Street",
            house_number="123",
            supplier_type="factory",
            debt=0.00,
        )

    def test_clear_debt_action(self):
        queryset = Supplier.objects.all()
        self.admin.clear_debt(None, queryset)
        self.supplier.refresh_from_db()
        self.assertEqual(self.supplier.debt, 0.00)


class SupplierSerializerTest(TestCase):
    def setUp(self):
        self.supplier_data = {
            "name": "Test Supplier",
            "email": "test@example.com",
            "country": "Test Country",
            "city": "Test City",
            "street": "Test Street",
            "house_number": "123",
            "supplier_type": "factory",
            "debt": 0.00,
        }
        self.supplier = Supplier.objects.create(**self.supplier_data)
        self.serializer = SupplierSerializer(instance=self.supplier)

    def test_contains_expected_fields(self):
        data = self.serializer.data
        self.assertEqual(
            set(data.keys()),
            set(
                [
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
            ),
        )

    def test_debt_field_read_only(self):
        self.assertTrue(self.serializer.fields["debt"].read_only)


class ProductSerializerTest(TestCase):
    def setUp(self):
        self.supplier = Supplier.objects.create(
            name="Test Supplier",
            email="test@example.com",
            country="Test Country",
            city="Test City",
            street="Test Street",
            house_number="123",
            supplier_type="factory",
        )
        self.product_data = {
            "name": "Test Product",
            "model": "Test Model",
            "release_date": date.today(),
            "supplier": self.supplier,
        }
        self.product = Product.objects.create(**self.product_data)
        self.serializer = ProductSerializer(instance=self.product)

    def test_contains_expected_fields(self):
        data = self.serializer.data
        self.assertEqual(set(data.keys()), set(["id", "name", "model", "release_date", "supplier"]))


class SupplierViewSetPermissionTest(APITestCase):
    def setUp(self):
        self.employee = User.objects.create_user(username="employee", password="employeepass", is_active=True)
        self.non_employee = User.objects.create_user(
            username="nonemployee", password="nonemployeepass", is_active=False
        )
        self.supplier = Supplier.objects.create(
            name="Test Supplier",
            email="test@example.com",
            country="Test Country",
            city="Test City",
            street="Test Street",
            house_number="123",
            supplier_type="factory",
        )
        self.url = reverse("supplier-detail", kwargs={"pk": self.supplier.pk})

    def test_employee_can_update_supplier(self):
        self.client.force_authenticate(user=self.employee)
        response = self.client.patch(self.url, {"name": "Updated Supplier"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.supplier.refresh_from_db()
        self.assertEqual(self.supplier.name, "Updated Supplier")

    def test_non_employee_cannot_update_supplier(self):
        self.client.force_authenticate(user=self.non_employee)
        response = self.client.patch(self.url, {"name": "Updated Supplier"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.supplier.refresh_from_db()
        self.assertNotEqual(self.supplier.name, "Updated Supplier")
