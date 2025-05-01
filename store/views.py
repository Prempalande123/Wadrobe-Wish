import re
from django.db.models import Q
from django.shortcuts import render, redirect
from django.http import JsonResponse
import json, datetime
from .models import *
from .utils import cookieCart, cartData, guestOrder
from django.contrib.auth.hashers import make_password, check_password
from django.views.decorators.csrf import csrf_exempt

# 🌐 Store view
def store(request):
    data = cartData(request)
    cartItems = data['cartItems']
    products = None
    categories = Category.get_all_categories()
    categoryID = request.GET.get('category')
    if categoryID:
        products = Product.get_all_products_by_category_id(categoryID)
    else:
        products = Product.objects.all()

    customer_name = request.session.get('customer_name', '')
    customer_id = request.session.get('customer_id')

    wishlist_products = []
    if customer_id:
        customer = Customer.objects.get(id=customer_id)
        wishlist_products = Wishlist.objects.filter(customer=customer).values_list('product_id', flat=True)

    context = {
        'categorys': categories,
        'products': products,
        'cartItems': cartItems,
        'customer_name': customer_name,
        'wishlist_products': wishlist_products
    }
    return render(request, 'store/store.html', context)

# 🛡 Validation logic for signup
def validateCustomer(customer):
    error_message = None
    if len(str(customer.phone)) != 10 or not str(customer.phone).isdigit():
        error_message = "Phone number must be 10 digits long!!"
    elif customer.isExists():
        error_message = "Email Address Already Registered!!"
    return error_message

# 📥 Register user
def registerUser(request):
    data = cartData(request)
    cartItems = data['cartItems']
    context = {'cartItems': cartItems}

    postData = request.POST
    name = postData.get('name')
    phone = postData.get('phone')
    email = postData.get('email')
    password = postData.get('password')
    values = {'name': name, 'phone': phone, 'email': email}
    customer = Customer(name=name, phone=phone, email=email, password=password)
    error_message = validateCustomer(customer)

    if not error_message:
        customer.password = make_password(customer.password)
        customer.register()
        request.session['customer_id'] = customer.id
        request.session['customer_name'] = customer.name
        return redirect('store')
    else:
        ct = {'error': error_message, 'context': context, 'values': values}
        return render(request, 'store/signup.html', ct)

# 📝 Signup view
def signup(request):
    data = cartData(request)
    cartItems = data['cartItems']
    context = {'cartItems': cartItems}

    if request.method == 'GET':
        return render(request, 'store/signup.html', context)
    else:
        return registerUser(request)

# 🔐 Login view
def login_view(request):
    data = cartData(request)
    cartItems = data['cartItems']
    context = {'cartItems': cartItems}
    if request.method == 'GET':
        return render(request, 'store/login.html', context)
    else:
        email = request.POST.get('email')
        password = request.POST.get('password')
        customer = Customer.get_customer_by_email(email)
        error_message = None
        if customer:
            flag = check_password(password, customer.password)
            if flag:
                request.session['customer_id'] = customer.id
                request.session['customer_name'] = customer.name
                return redirect('store')
            else:
                error_message = "Email or Password invalid!!"
        else:
            error_message = "Email or Password invalid!!"
        return render(request, 'store/login.html', {
            'error': error_message,
            'cartItems': cartItems
        })

# ❌ Logout
def logout(request):
    request.session.clear()
    return redirect('store')

# 🛒 Cart view
def cart(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
    customer_name = request.session.get('customer_name', '')
    context = {'items': items, 'order': order, 'cartItems': cartItems, 'customer_name': customer_name}
    return render(request, 'store/cart.html', context)

def checkout(request):
    if not request.session.get('customer_id'):
        return redirect('login')

    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
    customer_name = request.session.get('customer_name', '')

    context = {
        'items': items,
        'order': order,
        'cartItems': cartItems,
        'customer_name': customer_name
    }
    return render(request, 'store/checkout.html', context)

# 🔄 Add/Remove item
def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity += 1
    elif action == 'remove':
        orderItem.quantity -= 1
    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()
    return JsonResponse('Item was added', safe=False)

# 💳 Process order
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
    else:
        customer, order = guestOrder(request, data)

    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    if total == float(order.get_total_cart):
        order.complete = True
        order.save()

        subject = 'Order Confirmation'
        items = order.orderitem_set.all()
        message = render_to_string('store/email_template.html', {
            'customer': customer,
            'order': order,
            'items': items,
        })

        send_mail(subject, '', settings.EMAIL_HOST_USER, [customer.email], html_message=message)

    if order.shipping:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            zipcode=data['shipping']['zipcode'],
        )

    return JsonResponse('Payment Complete!', safe=False)

# 🔍 Product view
def viewProduct(request, pk):
    data = cartData(request)
    cartItems = data['cartItems']
    product = Product.objects.get(id=pk)
    customer_name = request.session.get('customer_name', '')

    customer_id = request.session.get('customer_id')
    is_wishlisted = False
    if customer_id:
        customer = Customer.objects.get(id=customer_id)
        is_wishlisted = Wishlist.objects.filter(customer=customer, product=product).exists()

    context = {
        'product': product,
        'cartItems': cartItems,
        'customer_name': customer_name,
        'is_wishlisted': is_wishlisted
    }
    return render(request, 'store/product.html', context)

# 🔎 Search
def search(request):
    data = cartData(request)
    cartItems = data['cartItems']
    search_term = request.GET.get('search')
    products = Product.objects.filter(Q(name__icontains=search_term) | Q(desc__icontains=search_term)).order_by('-id')
    customer_name = request.session.get('customer_name', '')
    context = {'products': products, 'cartItems': cartItems, 'customer_name': customer_name}
    return render(request, 'store/search.html', context)

# ❤️ Toggle Wishlist
@csrf_exempt
def toggle_wishlist(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        customer_id = request.session.get('customer_id')
        if not customer_id:
            return JsonResponse({'status': 'not_logged_in'})

        customer = Customer.objects.get(id=customer_id)
        product = Product.objects.get(id=product_id)

        wishlist_item, created = Wishlist.objects.get_or_create(customer=customer, product=product)
        if not created:
            wishlist_item.delete()
            return JsonResponse({'status': 'removed'})
        return JsonResponse({'status': 'added'})

# ❤️ View Wishlist
def wishlist_view(request):
    customer_id = request.session.get('customer_id')
    if not customer_id:
        return redirect('login')

    data = cartData(request)
    cartItems = data['cartItems']
    customer_name = request.session.get('customer_name', '')
    customer = Customer.objects.get(id=customer_id)

    wishlist_items = Wishlist.objects.filter(customer=customer)

    context = {
        'wishlist_items': wishlist_items,
        'cartItems': cartItems,
        'customer_name': customer_name
    }
    return render(request, 'store/wishlist.html', context)
