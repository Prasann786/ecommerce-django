from django.shortcuts import render

from .models import Category, Product

from django.shortcuts import get_object_or_404

from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import ProductSerializer

#DB agreegation tools
from django.db.models import Avg, Max, Min, Count
#These are ORM database functions.


# Create your views here.
def store(request):
    all_products = Product.objects.all()
    context = {'my_products' : all_products}


    return render(request, 'store/store.html', context)


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












