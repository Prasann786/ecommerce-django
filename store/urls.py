

from django.urls import path

from . import views



urlpatterns = [

#store main page
    path('', views.store, name='store'),

#individual product

    path('product/<slug:product_slug>/', views.product_info, name= 'product-info'),

#individual category

    path('search/<slug:category_slug>/', views.list_category, name= 'list-category'),

    path('api/products/', views.api_products, name='api-products'),

    path('api/products/create/', views.api_create_product, name='api-create-product'),

    path('api/products/<int:id>/update/', views.api_update_product, name='api-update-product'),

    path(
    'api/products/<int:id>/delete/',
    views.api_delete_product,
    name='api-delete-product'
),

path(
    'api/products/filter/',
    views.api_products_by_price,
    name='api-products-filter'
),

path('api/products/stats/', views.api_product_stats),
#cart
path('add-to-cart/', views.add_to_cart, name='add-to-cart'),
path('cart/', views.view_cart, name='view-cart'),
#remove from cart
path('remove-from-cart/', views.remove_from_cart, name='remove-from-cart'),
#increase and decrease from cart
path('update-cart/', views.update_cart_quantity, name='update-cart'),

#checkout and success
path('checkout/', views.checkout, name='checkout'),
path('order-success/', views.order_success, name='order-success'),
path("payment-success/", views.payment_success, name="payment_success"),
path('my-orders/', views.my_orders, name='my-orders'),
path('order/<int:order_id>/', views.order_detail, name='order-detail'),
path('address/', views.address, name='address'),
]













