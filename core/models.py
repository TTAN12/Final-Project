from django.db import models
from django.contrib.auth.models import User
import uuid

class Customer(models.Model):
    name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    password = models.CharField(max_length=100)

    def __str__(self):
        return (self.name)
    
class Product(models.Model):
    CATEGORY_CHOICES = [
        ('Tools', 'Tools'),
        ('Materials', 'Materials'),
        ('Electrical', 'Electrical'),
    ]
    
    name = models.CharField(max_length=255)
    price = models.DecimalField(decimal_places=2, max_digits=12)
    thumbnail = models.ImageField()
    description = models.TextField()
    category = models.CharField(max_length=255, choices=CATEGORY_CHOICES)

    def __str__(self):
        return self.name

class Cart(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False) 

    def __str__(self):
        return str(self.id)    
    
    @property
    def total_price(self):
        cartitems = self.cartitems.all()
        total = sum([ item.price for item in cartitems])
        return total


class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='items')
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="cartitems")
    quantity = models.IntegerField(default=0)

    def __str__(self):
        return self.product.name
    
    @property
    def price(self):
        new_price = self.product.price * self.quantity
        return new_price
    
class Order(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Order {self.id} by {self.user.username}"
    
    @property
    def items(self):
        return self.orderitems.all()
    
    @property
    def total_price(self):
        # Calculate the total price dynamically from order items
        return sum(item.price for item in self.orderitems.all())
    

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='orderitems')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(decimal_places=2, max_digits=12)  # Price at the time of order

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in {self.order.id}"
    @property
    def price(self):
        new_price = self.product.price * self.quantity
        return new_price