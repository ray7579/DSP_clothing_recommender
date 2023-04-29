from django.contrib import admin
from .models import User, Customer, Admin, Product, Like, Comment
# Register your models here.

admin.site.register(Customer)
admin.site.register(User)
admin.site.register(Admin)
admin.site.register(Product)
admin.site.register(Like)
admin.site.register(Comment)