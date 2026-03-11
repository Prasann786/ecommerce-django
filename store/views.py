from django.shortcuts import render, redirect

from .models import Category, Product, Address

from django.shortcuts import get_object_or_404

from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import ProductSerializer

#DB agreegation tools
from django.db.models import Avg, Max, Min, Count
#These are ORM database functions.


#delete from cart
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from .models import Cart, CartItem

#login/logout
from django.contrib.auth.decorators import login_required

from .models import Order, OrderItem

#razorpay
import razorpay
from django.conf import settings
from django.http import JsonResponse
import json



# Create your views here.
def store(request):

    query = request.GET.get('q')

    if query:
        products = Product.objects.filter(title__icontains=query)
    else:
        products = Product.objects.all()

    return render(request, "store/store.html", {
        "products": products
    })


def categories(request):
    all_categories = Category.objects.all()
    return {'all_categories': all_categories}


def list_category(request, category_slug=None):

    category = get_object_or_404(Category, slug=category_slug)

    products = Product.objects.filter(category=category)

    return render (request, 'store/list-category.html', {'category' : category, 'products': products} )






def product_info(request, product_slug):

    product = get_object_or_404(Product, slug=product_slug)

    context = { 'product' : product}

    return render(request, 'store/product-info.html', {'product': product})



@api_view(['GET']) #http://127.0.0.1:8000/api/products/
def api_products(request):
    products = Product.objects.all()
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)


@api_view(['POST']) #POST /api/products/create/

def api_create_product(request):

    serializer = ProductSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)

    return Response(serializer.errors, status=400)


#http://127.0.0.1:8000/api/products/1/update/
@api_view(['PUT'])

def api_update_product(request, id):

    product = get_object_or_404(Product, id=id)

    serializer = ProductSerializer(product, data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)

    return Response(serializer.errors)


#http://127.0.0.1:8000/api/products/1/delete/

@api_view(['DELETE'])
def api_delete_product(request, id):

    product = get_object_or_404(Product, id=id)

    product.delete()

    return Response({"message": "Product deleted successfully"})


#ORM (api/products/filter/?min_price=10&max_price=20)

@api_view(['GET'])
def api_products_by_price(request):

    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    products = Product.objects.filter(
        price__gte=min_price,
        price__lte=max_price
    )

    serializer = ProductSerializer(products, many=True)

    return Response(serializer.data)


#DB aggregation tools

@api_view(['GET'])
def api_product_stats(request):

    stats = Product.objects.aggregate(
        total_products=Count('id'),
        average_price=Avg('price'),
        max_price=Max('price'),
        min_price=Min('price')
    )

    return Response(stats)

@require_POST
def add_to_cart(request):
    product_id = request.POST.get('product_id')
    quantity = int(request.POST.get('quantity', 1))

    product = get_object_or_404(Product, id=product_id)

    if not request.session.session_key:
        request.session.create()

    session_id = request.session.session_key

    cart, created = Cart.objects.get_or_create(session_id=session_id)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product
    )

    if not created:
        cart_item.quantity += quantity
    else:
        cart_item.quantity = quantity

    cart_item.save()

    return JsonResponse({'message': 'Product added to cart'})

def cart_count(request):
    session_id = request.session.session_key
    count = 0

    if session_id:
        cart = Cart.objects.filter(session_id=session_id).first()
        if cart:
            count = sum(item.quantity for item in cart.items.all())

    return {'cart_count': count}


def view_cart(request):
    session_id = request.session.session_key
    items = []
    total = 0

    if session_id:
        cart = Cart.objects.filter(session_id=session_id).first()
        if cart:
            items = cart.items.all()
            total = sum(item.product.price * item.quantity for item in items)

    return render(request, 'store/cart.html', {
        'items': items,
        'total': total
    })


#delete from cart
@require_POST
def remove_from_cart(request):
    product_id = request.POST.get('product_id')

    session_id = request.session.session_key

    if not session_id:
        return JsonResponse({'error': 'No active session'}, status=400)

    cart = Cart.objects.filter(session_id=session_id).first()

    if not cart:
        return JsonResponse({'error': 'Cart not found'}, status=404)

    cart_item = CartItem.objects.filter(
        cart=cart,
        product_id=product_id
    ).first()

    if cart_item:
        cart_item.delete()

        # Recalculate cart total & count
        cart_total = sum(
            item.product.price * item.quantity
            for item in cart.items.all()
        )

        cart_count = sum(
            item.quantity for item in cart.items.all()
        )

        return JsonResponse({
            'message': 'Item removed successfully',
            'cart_total': float(cart_total),
            'cart_count': cart_count
        })

    return JsonResponse({'error': 'Item not found'}, status=404)

#increase and decrease items from cart
@require_POST
def update_cart_quantity(request):
    product_id = request.POST.get('product_id')
    action = request.POST.get('action')

    session_id = request.session.session_key
    cart = Cart.objects.filter(session_id=session_id).first()

    if not cart:
        return JsonResponse({'error': 'Cart not found'}, status=404)

    cart_item = CartItem.objects.filter(cart=cart, product_id=product_id).first()

    if not cart_item:
        return JsonResponse({'error': 'Item not found'}, status=404)

    if action == "increase":
        cart_item.quantity += 1

    elif action == "decrease":
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
        else:
            cart_item.delete()
            return JsonResponse({'deleted': True})

    cart_item.save()

    cart_total = sum(
        item.product.price * item.quantity
        for item in cart.items.all()
    )

    cart_count = sum(item.quantity for item in cart.items.all())

    return JsonResponse({
        'quantity': cart_item.quantity,
        'cart_total': float(cart_total),
        'cart_count': cart_count
    })





#checkout view

@login_required
def checkout(request):
    print("========== CHECKOUT START ==========")

    if not request.session.session_key:
        request.session.create()

    session_id = request.session.session_key

    cart = Cart.objects.filter(session_id=session_id).first()

    if not cart:
        return redirect('view-cart')

    cart_items = cart.items.all()

    total = sum(item.product.price * item.quantity for item in cart_items)

    client = razorpay.Client(
    auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
    )

    payment = client.order.create({
        "amount": int(total * 100),
        "currency": "INR",
        "payment_capture": 1
    })

    context = {
        "items": cart_items,
        "total": total,
        "payment": payment,
        "razorpay_key": settings.RAZORPAY_KEY_ID
    }

    return render(request, "store/checkout.html", context)

import json
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@login_required


def payment_success(request):

    print("PAYMENT SUCCESS API CALLED")

    data = json.loads(request.body)

    payment_id = data.get("razorpay_payment_id")
    order_id = data.get("razorpay_order_id")
    signature = data.get("razorpay_signature")

    client = razorpay.Client(
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
    )

    try:
        client.utility.verify_payment_signature({
            "razorpay_payment_id": payment_id,
            "razorpay_order_id": order_id,
            "razorpay_signature": signature
        })

        # get cart
        session_id = request.session.session_key

        cart = Cart.objects.filter(session_id=session_id).first()

        if not cart:
            return JsonResponse({"status": "failed", "message": "Cart not found"})

        cart_items = cart.items.all()

        total = sum(item.product.price * item.quantity for item in cart_items)

        # create order
        order = Order.objects.create(
            user=request.user,
            total_price=total
        )

        # create order items
        for item in cart_items:

            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
            price=item.product.price
            )

            # ⭐ reduce stock
            item.product.stock -= item.quantity
            item.product.save()

        # 🚨 DELETE CART
        cart_items.delete()
        cart.delete()

        print("CART DELETED SUCCESSFULLY")

        return JsonResponse({"status": "success"})

    except Exception as e:
        print("PAYMENT ERROR:", e)
        return JsonResponse({"status": "failed"})


#order success view
@login_required
def order_success(request):
    return render(request, "store/order-success.html")


#Myorders
from django.contrib.auth.decorators import login_required

@login_required
def my_orders(request):

    orders = Order.objects.filter(user=request.user).order_by('-created_at')

    return render(request, "store/my-orders.html", {
        "orders": orders
    })

@login_required
def order_detail(request, order_id):

    order = Order.objects.get(id=order_id, user=request.user)

    items = order.items.all()

    return render(request, "store/order-detail.html", {
        "order": order,
        "items": items
    })

@login_required
def address(request):

    if request.method == "POST":

        Address.objects.create(
            user=request.user,
            full_name=request.POST["full_name"],
            phone=request.POST["phone"],
            address_line=request.POST["address_line"],
            city=request.POST["city"],
            state=request.POST["state"],
            postal_code=request.POST["postal_code"]
        )

        return redirect("checkout")

    return render(request, "store/address.html")










