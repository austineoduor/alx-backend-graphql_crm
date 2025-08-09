from django.db import models
from django.db import models
from django.utils import timezone
import uuid

class Customer(models.Model):
    customer_id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True,editable=False)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=30, blank=True, null=True)

    def __str__(self):
        return f"{self.name} <{self.email}>"

class Product(models.Model):
    product_id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True,editable=False)
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.name} (${self.price})"

class Order(models.Model):
    order_id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True,editable=False)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    products = models.ManyToManyField(Product, through='OrderProduct', related_name='orders')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    order_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Order {self.pk} - {self.customer.name}"

    def update_total_amount(self):
        total = self.orderproduct_set.aggregate(
            sum=models.Sum(models.F('product__price') * models.F('quantity'))
        )['sum'] or 0
        self.total_amount = total
        self.save()

class OrderProduct(models.Model):
    orderProductid = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True,editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('order', 'product')