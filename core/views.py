from django.shortcuts import render, redirect
#importing loading from django template  
from django.template import loader  
# Create your views here.  
from django.http import HttpResponse  
from core.models import *
from django.http import JsonResponse
import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
import base64
import pip._vendor.requests as requests
from django.http import JsonResponse
from django.conf import settings
from .forms import CreateUserForm
from .filters import ProductFilter
from django.db.models import Q

# Login View
def loginpage(request):
    form = CreateUserForm()
    context = { 'form':form }
    template = loader.get_template('login.html')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        print(username)
        print(password)

        if user is not None:
            login(request, user)
            return redirect('homepage')
        else:
            messages.success( request, 'incorrect usernmae or password')

    return HttpResponse(template.render(context, request))

#Logout View
def logoutuser(request):
    logout(request)
    return redirect('login')

# Register View
def register(request):
    form = CreateUserForm()
    context = { 'form':form }
    template = loader.get_template('register.html')

    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            user = form.cleaned_data.get('username')
            messages.success( request, 'Account was created for ' + user)
            return redirect('login')

    context = {'form':form}
    return HttpResponse(template.render(context, request))

# Account View
def account(request):

    user = request.user
    
    if request.user.is_authenticated:
        orders = Order.objects.filter(user=request.user) 
        context = {'user':user, 'orders':orders}
        
        template = loader.get_template('account.html')
        return HttpResponse(template.render(context, request))
    else:
        messages.success( request, 'login')
        return redirect('login')

    

# Homepage View
def homepage(request):
    # Start by getting all products
    products = Product.objects.all()

    # Get search query from the request (if any)
    search_query = request.GET.get('search', '')
    sort_by = request.GET.get('sort', 'price_asc')  # Default sort is by price (ascending)
    filters = request.GET.getlist('category')  # List of selected categories from the form

    # Apply search filter if there is a search query
    if search_query:
        products = products.filter(Q(name__icontains=search_query) | Q(description__icontains=search_query))

    # Apply category filter if any categories are selected
    if filters:
        products = products.filter(category__in=filters)

    # Sorting logic
    if sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')
    elif sort_by == 'name_asc':
        products = products.order_by('name')
    elif sort_by == 'name_desc':
        products = products.order_by('-name')

    # Create the ProductFilter object
    myFilter = ProductFilter(request.GET, queryset=products)

    context = {
        'products': myFilter.qs,  # Use the filtered and sorted products
        'myFilter': myFilter,
        'search_query': search_query,
        'sort_by': sort_by,
        'filters': filters,
    }

    return render(request, 'homepage.html', context)
# Product View
def prod(request, invID):
    products = Product.objects.get(id=invID)
    context = {
        'products':products 
    }
    template = loader.get_template('prod.html')
    return HttpResponse(template.render(context,request))

def add_to_cart(request):
    data = json.loads(request.body)
    product_id = data["id"]
    product = Product.objects.get(id=product_id)

    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user, completed=False)
        cartitem, created = CartItem.objects.get_or_create(cart=cart, product=product)
        cartitem.quantity += 1
        cartitem.save()
        print(cartitem)


    return JsonResponse("it is wroking", safe=False)
    

# Cart View
def cart(request):

    cart = None
    cartitems = []

    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user, completed=False)
        cartitems = cart.cartitems.all()
    context = {
        "cart":cart,
        "cartitems":cartitems
    }
    template = loader.get_template('cart.html')
    return HttpResponse(template.render(context, request))




def generate_payment_link(request):
    if request.method == "POST":
        # Step 1: Create Order and OrderItems from Cart
        user = request.user  # Get the logged-in user

        # Create an order from the cart
        order = create_order_from_cart(user)
        if not order:
            return JsonResponse({"error": "Your cart is empty or does not exist."}, status=400)

        # Step 2: Format PayMongo link payload
        description = "Order Details:\n"  # Initialize the description
        for item in order.orderitems.all():  # Access OrderItems through related name `orderitems`
            description += f"{item.quantity} x {item.product.name} - PHP {item.price:.2f}\n"

        payload = {
            "data": {
                "attributes": {
                    "amount": int(order.total_price * 100),  # Convert to cents
                    "currency": "PHP",
                    "description": description,
                    "remarks": f"Order #{order.id} by {user.username}"
                }
            }
        }

        # Step 3: Base64 encode the API secret key (the fix goes here)
        secret_key = settings.PAYMONGO_SECRET_KEY  # Get secret key from settings
        auth_value = base64.b64encode(f"{secret_key}:".encode("utf-8")).decode("utf-8")  # Base64 encode the key

        # Set up the authorization header using the encoded secret key
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Basic {auth_value}"  # Add Basic auth header
        }

        # Send the request to PayMongo
        url = "https://api.paymongo.com/v1/links"
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()  # Will raise an exception for 4xx/5xx HTTP status codes
        except requests.exceptions.RequestException as e:
            return JsonResponse({"error": f"Error occurred while creating payment link: {str(e)}"}, status=500)

        # Step 4: Handle response and return checkout URL
        if response.status_code == 200 or response.status_code == 201:
            data = response.json()
            checkout_url = data['data']['attributes']['checkout_url']
            return JsonResponse({"checkout_url": checkout_url})

        return JsonResponse({"error": response.json()}, status=response.status_code)

    return JsonResponse({"error": "Method not allowed"}, status=405)


        
def create_order_from_cart(user):
    # Retrieve the user's cart and cart items
    try:
        cart = Cart.objects.get(user=user, completed=False)
        cart_items = cart.cartitems.all()

        if not cart_items.exists():
            return None  # No items to process

        
        # Create an Order instance
        order = Order.objects.create(user=user)

        # Create OrderItems based on CartItems
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
            )

        # Mark the cart as completed
        cart.completed = True
        cart.save()

        return order

    except Cart.DoesNotExist:
        return None  # Handle the case where the cart doesn't exist


def update_cart(request):
    if request.method == "POST":
        user = request.user
        try:
            cart = Cart.objects.get(user=user, completed=False)
        except Cart.DoesNotExist:
            # If the user doesn't have a cart, redirect them
            return redirect('cart')

        # Loop through all cart items and update quantities
        for item in cart.cartitems.all():
            quantity = request.POST.get(f'quantity_{item.id}')  # Get the quantity from POST data
            if quantity:
                try:
                    quantity = int(quantity)
                    if quantity >= 1:  # Ensure quantity is a valid positive integer
                        item.quantity = quantity
                        item.save()  # Save the updated quantity
                except ValueError:
                    continue  # Skip if the quantity is not a valid number

        return redirect('cart')  # Redirect to the cart page after updating
    return redirect('cart')  # If the request is not POST, just redirect back to the cart