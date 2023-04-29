from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    is_user = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,primary_key=True)
    phone_no = models.CharField(max_length=100)
    dob = models.DateField(blank= True, null=True)

    def __str__(self):
        return self.user.username

class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,primary_key=True)
    phone_no = models.CharField(max_length=100)
    dob = models.DateField(blank= True, null=True)



class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    description = models.TextField()
    materials = models.CharField(max_length=400)
    image_url = models.URLField(blank= True, null=True)
    product_url = models.URLField(blank= True, null=True)
    likes = models.PositiveIntegerField(blank= True, null=True, default=0)

    def __str__(self):
        return self.name
    
class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.comment}"

