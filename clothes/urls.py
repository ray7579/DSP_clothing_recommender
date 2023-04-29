from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path
from . import views
from clothes.views import scrape_website

urlpatterns=[
    path('', views.home, name='home'),
    path('register/', views.customer_register.as_view(), name = 'user_register'),
    path('login/', views.login_request, name = 'login'),
    path('logout/', views.logout_view, name='logout'),
    path('scrape/', views.scrape_website, name='scrape_page'),
    path('scrape_success/', views.success_page, name='success_page'),
    path('products/', views.product_list, name='product_list'),
    path('products/<int:pk>/', views.product_detail, name='product_detail'),
    path('search/', views.search, name='search'),
    path('products/<int:pk>/like/', views.like_product, name='like_product'),
    path('recommendations/', views.product_recommendations, name='product_recommendations'),
    path('popular/', views.most_liked_products, name='popular'),
    path('delete_comment/<int:comment_id>/', views.delete_comment, name='delete_comment'),
]