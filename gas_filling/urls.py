from django.urls import path
#from util.util import add_std_to_paths
from . import views

#app_name = "gas_filling"


urlpatterns = [
    path('', views.gas_filling_home, name='gas_filling_home'),
    path('filling/<int:pk>/', views.gas_filling, name='gas_filling_filling'),
    path('filling/batch/<int:pk>/', views.gas_filling_batchnum, name='gas_filling_batchnum'),
    path('filling/tareweight/<int:pk>/', views.gas_filling_tareweight, name='gas_filling_tareweight'),
    path('filling/endweight/<int:pk>/', views.gas_filling_endweight, name='gas_filling_endweight'),
    path('fillings/<int:pk>/continue/', views.continue_filling, name='continue_filling'),


    path('list/', views.cylinder_list, name='cylinder_list'),
    path('show/<int:pk>/', views.cylinder_show, name='cylinder_show'),
    path('create/', views.cylinder_create, name='cylinder_create'),
    path('edit/<int:pk>/', views.cylinder_edit, name='cylinder_edit'),

    path('filling/table/', views.gas_filling_table, name='gas_filling_table'),

    path("cylinder/", views.cylinder_index, name="cylinder_index"),
    path("cylinder/<int:obj_id>/", views.cylinder_view, name="cylinder_view"),
    path("cylinder/<int:obj_id>/edit", views.cylinder_edit, name="cylinder_edit"),

    path('orders/', views.order_list, name='order_list'),
    path('orders/create/', views.order_create, name='order_create'),
    path('orders/<int:pk>/', views.order_show, name='order_show'),
    path('orders/<int:pk>/edit/', views.order_edit, name='order_edit'),

    path('filling/show/<int:pk>/', views.filling_show, name='filling_show'),
    path('filling/edit/<int:pk>/', views.filling_edit, name='filling_edit'),
]


"""
urlpatterns = [
    path('orders/', views.order_test, name='order_test'),
]
"""