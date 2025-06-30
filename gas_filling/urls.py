from django.urls import path
from util.util import add_std_to_paths
from . import views

app_name = "gas_filling"

urlpatterns = [
    path('', views.gas_filling_home, name='gas_filling_home'),
    path('filling/<int:pk>', views.gas_filling, name='gas_filling_filling'),
    #path('filling/order/', views.gas_filling_order, name='gas_filling_order'),
    path('filling/tareweight/<int:pk>/', views.gas_filling_tareweight, name='gas_filling_tareweight'),
    path('filling/endweight/<int:pk>/', views.gas_filling_endweight, name='gas_filling_endweight'),

    path('list/', views.gas_filling_list, name='gas_filling_list'),
    path('show/<int:pk>/', views.gas_filling_show, name='gas_filling_show'),
    path('create/', views.gas_filling_create, name='gas_filling_create'),
    path('edit/<int:pk>/', views.gas_filling_edit, name='gas_filling_edit'),
    path('filling/table/', views.gas_filling_table, name='gas_filling_table'),

    path("cylinder", views.cylinder_index, name="cylinder_index"),
    path("cylinder/<int:obj_id>", views.cylinder_view, name="cylinder_view"),
    path("cylinder/<int:obj_id>/edit", views.cylinder_edit, name="cylinder_edit"),

    path('orders/', views.order_list, name='order_list'),
    path('orders/create/', views.order_create, name='order_create'),
    path('orders/<int:pk>/', views.order_show, name='order_show'),
    path('orders/<int:pk>/edit/', views.order_edit, name='order_edit'),



]

