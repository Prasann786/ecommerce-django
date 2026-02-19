

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




]













