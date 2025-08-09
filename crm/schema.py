import re
import graphene
from django.db import transaction
from django.utils import timezone
from graphene_django.types import DjangoObjectType
from graphene import relay
from graphene_django.filter import DjangoFilterConnectionField
from .models import Customer, Product, Order
from .filters import CustomerFilter, ProductFilter, OrderFilter
# from crm.schema import

# Regex to validate phone formats like "+1234567890" or "123-456-7890"
PHONE_REGEX = re.compile(r'^(\+\d{10,15}|\d{3}-\d{3}-\d{4})$')

class CustomerNode(DjangoObjectType):
    class Meta:
        model = Customer
        interfaces = (relay.Node,)

class ProductNode(DjangoObjectType):
    class Meta:
        model = Product
        interfaces = (relay.Node,)

class OrderNode(DjangoObjectType):
    class Meta:
        model = Order
        interfaces = (relay.Node,)

# GraphQL types for your Django models
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer

class ProductType(DjangoObjectType):
    class Meta:
        model = Product

class OrderType(DjangoObjectType):
    class Meta:
        model = Order

# 1. CreateCustomer mutation
class CreateCustomer(graphene.Mutation):
    customer = graphene.Field(CustomerType)
    message = graphene.String()
    errors = graphene.List(graphene.String)

    class Arguments:
        name = graphene.String(required=True)
        email = graphene.String(required=True)
        phone = graphene.String()

    def mutate(self, info, name, email, phone=None):
        errors = []
        if Customer.objects.filter(email=email).exists():
            errors.append("Email already exists")
        if phone and not PHONE_REGEX.match(phone):
            errors.append("Invalid phone format")
        if errors:
            return CreateCustomer(errors=errors)

        c = Customer(name=name, email=email, phone=phone)
        c.save()
        return CreateCustomer(customer=c, message="Customer created successfully")

class CustomerInput(graphene.InputObjectType):
        name = graphene.String(required=True)
        email = graphene.String(required=True)
        phone = graphene.String()

# 2. BulkCreateCustomers mutation
class BulkCreateCustomers(graphene.Mutation):
    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    class Arguments:
        input = graphene.List(CustomerInput, required=True)

    def mutate(self, info, input):
        created = []
        errors = []
        with transaction.atomic():
            for idx, cust in enumerate(input, start=1):
                row_errors = []
                if Customer.objects.filter(email=cust.email).exists():
                    row_errors.append(f"Row {idx}: Email {cust.email} already exists")
                if cust.phone and not PHONE_REGEX.match(cust.phone):
                    row_errors.append(f"Row {idx}: Invalid phone format")
                if row_errors:
                    errors.extend(row_errors)
                else:
                    new = Customer(name=cust.name, email=cust.email, phone=cust.phone)
                    new.save()
                    created.append(new)
        return BulkCreateCustomers(customers=created, errors=errors)

# 3. CreateProduct mutation
class CreateProduct(graphene.Mutation):
    product = graphene.Field(ProductType)
    errors = graphene.List(graphene.String)

    class Arguments:
        name = graphene.String(required=True)
        price = graphene.Float(required=True)
        stock = graphene.Int()

    def mutate(self, info, name, price, stock=0):
        errors = []
        if price <= 0:
            errors.append("Price must be positive")
        if stock < 0:
            errors.append("Stock cannot be negative")
        if errors:
            return CreateProduct(errors=errors)

        p = Product.objects.create(name=name, price=price, stock=stock)
        return CreateProduct(product=p)

# 4. CreateOrder mutation
class CreateOrder(graphene.Mutation):
    order = graphene.Field(OrderType)
    errors = graphene.List(graphene.String)

    class Arguments:
        customer_id = graphene.ID(required=True)
        product_id = graphene.List(graphene.ID, required=True)
        order_date = graphene.DateTime()

    def mutate(self, info, customer_id, product_id, order_date=None):
        errors = []
        try:
            customer = Customer.objects.get(pk=customer_id)
        except Customer.DoesNotExist:
            errors.append("Invalid customer ID")

        products = list(Product.objects.filter(pk__in=product_id))
        if not product_id or len(products) != len(product_id):
            errors.append("One or more product IDs are invalid")
        if not products:
            errors.append("At least one product must be selected")

        if errors:
            return CreateOrder(errors=errors)

        total = sum(p.price for p in products)
        order = Order.objects.create(
            customer=customer,
            total_amount=total,
            order_date=order_date or timezone.now()
        )
        order.products.set(products)
        return CreateOrder(order=order)

# Mutation root to expose all mutation fields
class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
    
#class Query(graphene.ObjectType):
class Query(graphene.ObjectType):
    # query fields (or leave pass)
    all_customers = DjangoFilterConnectionField(CustomerNode, filterset_class=CustomerFilter)
    all_products = DjangoFilterConnectionField(ProductNode, filterset_class=ProductFilter)
    all_orders = DjangoFilterConnectionField(OrderNode, filterset_class=OrderFilter)
    ping = graphene.String(description="A simple health check field")

    def resolve_ping(self, info):
        return "pong"