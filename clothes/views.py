from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView
from .form import UserSignUpForm, AdminSignUpForm, CommentForm
from .models import User, Customer, Admin
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
import requests
from bs4 import BeautifulSoup
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from clothes.models import Product, Like, Comment
import os
import time
from django.db.models import Q
from .preprocessing import preprocess_text, preprocess_products
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test, login_required


#website views==================================================================
def home(request):
    return render(request, 'clothes/home.html')


def product_list(request):
    products = Product.objects.all()
    if request.user.is_authenticated:
        liked_products = Like.objects.filter(user=request.user).values_list('product', flat=True)
        products = products.annotate(liked=Q(pk__in=liked_products))
    else:
        liked_products = []
    return render(request, 'clothes/product_list.html', {'products': products, 'liked_products': liked_products})



def search(request):
    query = request.GET.get('query', '')
    if query:
        products = Product.objects.filter(Q(name__icontains=query) | Q(description__icontains=query))
    else:
        products = Product.objects.all()
    return render(request, 'clothes/search.html', {'products': products, 'query':query})


@csrf_exempt
def like_product(request, pk):
    #if like button pressed
    if request.method == 'POST' and request.user.is_authenticated:
        #get product based on id
        product = get_object_or_404(Product, pk=pk)
        like, created = Like.objects.get_or_create(user=request.user, product=product)
        #if item isnt liked
        if not created:
            like.delete()
            product.likes -= 1
            product.save()
            return JsonResponse({'status': 'unliked'})
        #if item is liked
        else:
            product.likes += 1
            product.save()
            return JsonResponse({'status': 'liked'})
    return JsonResponse({'status': 'login'})

@login_required(login_url='/login/')
def product_recommendations(request):
    #fetch products, and add to dataframe to preprocess
    products = Product.objects.all().values()
    products_df = pd.DataFrame.from_records(products)
    #print(products_df)  
    preprocessed_products = preprocess_products(products_df)
    #create a tfidf matrix
    tfidf_vectorizer = TfidfVectorizer()
    tfidf_matrix = tfidf_vectorizer.fit_transform(preprocessed_products['combined_features'])
    #calculate cosine similarity of all products
    similarity_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)

    #get products for user based on their liked products
    liked_products = Like.objects.filter(user=request.user).values_list('product_id', flat=True)
    recommendations = []
    for product_id in liked_products:
        #get 50 most similar products to the liked products
        product_index = products_df.loc[products_df['id'] == product_id].index[0]
        #remove the first item as it is always the item itself
        similar_products_index = np.argsort(similarity_matrix[product_index])[::-1][1:51]

        #loop through all rows in the similar products
        for index in similar_products_index:
            #get the products objects based on their id and add to a list
            recommended_product_id = products_df.loc[index, 'id']
            recommended_product = Product.objects.get(id=recommended_product_id)
            recommendations.append(recommended_product)
    #remove duplicates from list
    recommendations = list(set(recommendations))

    return render(request, 'clothes/recommendations.html', {'recommendations': recommendations})


def most_liked_products(request):
    products = Product.objects.order_by('-likes')[:50]
    context = {'products': products}
    return render(request, 'clothes/popular.html', context)



def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    comments = Comment.objects.filter(product=product).order_by('-created_at')
    
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.user = request.user
            new_comment.product = product
            new_comment.save()
            return redirect('product_detail', pk=pk)
    else:
        comment_form = CommentForm()
    return render(request, 'clothes/product_detail.html', {'product': product, 'comments': comments, 'comment_form': comment_form})


def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user == comment.user or request.user.is_admin:
        comment.delete()
    return redirect('product_detail', pk=comment.product.pk)


# Webscraping views==================================================================
def is_admin(user):
    return user.is_authenticated and user.is_admin

@user_passes_test(is_admin, login_url='/login/', redirect_field_name=None)
def scrape_website(request):
    if request.method == 'POST':

        delay = 4
        baseurl = "https://www.urbanoutfitters.com"
        header = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
        }

        page = requests.get('https://www.urbanoutfitters.com/en-gb/mens-clothing?availability=CURRENT_POOL', headers=header)
        doc = BeautifulSoup(page.content, 'html.parser')
        print(page.status_code)
        #getting number of pages
        page_text = doc.find(class_ = "o-pwa-pagination__page-total")
        pageno = str(page_text).split(">")[1].split("<")[0].strip()
        pageno = int(pageno)
        #print(pageno)  

        #going through all pages and saving all product links
        productlinks=[]
        for page in range(12, 18):
            page = requests.get(f"https://www.urbanoutfitters.com/en-gb/mens-clothing?availability=CURRENT_POOL&page={page}", headers=header)
            soup = BeautifulSoup(page.content, 'html.parser')
            productlist = soup.find_all('div', class_ ='c-pwa-tile-grid-inner')
            time.sleep(delay)
            for item in productlist:
                for link in item.find_all('a', href=True):
                    productlinks.append(baseurl + link['href'])
            #print(productlinks)

        #loop throgh all product links and webscrape the data 
        for productlink in productlinks:
            #visit the link
            page = requests.get(productlink, headers=header)
            soup = BeautifulSoup(page.content, 'html.parser')
            #webscrape the info
            temp_name = soup.find('h1', class_ ='c-pwa-product-meta-heading')
            name = str(temp_name).split('>')[1].split('<')[0].strip()
            print(name)

            #getting price
            temp_sale_price = soup.find('span', class_='c-pwa-product-price__current s-pwa-product-price__current c-pwa-product-price__current--sale-temporary')
            if temp_sale_price:
                # Extract the sale price if it exists
                price = str(temp_sale_price).split('£')[1].split('"')[0].strip()
            else:
                # Extract the regular price if the sale price element doesn't exist
                temp_price = soup.find('span', class_='c-pwa-product-price__current s-pwa-product-price__current')
                price = str(temp_price).split('£')[1].split('"')[0].strip()

            #end scraping if there exists the product already
            if Product.objects.filter(name=name, price=price).exists():
                break

            #description
            temp_description = soup.find('div', class_ ='s-pwa-cms c-pwa-markdown')
            try:
                description = str(temp_description).split('p>')[1].split('<')[0].strip()
            except:
                continue
            
            #materials
            try:
                materials = str(temp_description).split('p>')[3].split('/strong>')[1].split('<br/>- ')
            except:
                continue
            
            #getting image url
            temp_img_url = soup.find('div', class_='c-pwa-image-viewer__img-outer')
            image_url = str(temp_img_url).split('src="')[1].split('"')[0]

        
            #if not os.path.exists(f'media/{image_name}'):
            #    response = requests.get(image_url)
            #    image_name = image_url.split('/')[-1].split('_b')[0] + '.jpg'
            #    with open(f'media/{image_name}', 'wb') as f:
            #        f.write(response.content)
            #        print("finished writing")

            #creating product object and save to database
            product = Product(name=name, price=price, description=description, materials=materials, image_url=image_url, product_url=productlink, likes=0)
            product.save()
            #delay the scraping
            time.sleep(delay)
        
        #when we scrape finished
        return redirect('success_page')
    
    return render(request,'clothes/scrape.html')

@user_passes_test(is_admin, login_url='/login/', redirect_field_name=None)
def success_page(request):
    return render(request, 'clothes/scrape_success.html')



#authentication views==================================================================
class customer_register(CreateView):
    model = User
    form_class = UserSignUpForm
    template_name = 'clothes/register.html'
    success_url = reverse_lazy('login')

def login_request(request):
    if request.user.is_authenticated:
        return redirect('/')
    else:
        if request.method == "POST":
            form = AuthenticationForm(data=request.POST)
            if form.is_valid():
                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password')
                user = authenticate(username=username, password=password)
                if user is not None:
                    login(request,user)
                    return redirect('/')
                else:   
                    messages.error(request, "Invalid username or password")
            else:
                messages.error(request, "Invalid username or password")
        return render(request, 'clothes/login.html', context={'form' :AuthenticationForm()})

@login_required(login_url='/login/')
def logout_view(request):
    logout(request)
    return redirect('/')


