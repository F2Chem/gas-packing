from django.urls import path
#from util.util import add_std_to_paths
from . import views
from django.shortcuts import redirect


app_name = "gas_filling"


urlpatterns = [
    path('', lambda request: redirect('order/', permanent=True)),

    path('filling/<int:pk>/', views.gas_filling, name='gas_filling_filling'),
    path('filling/batch/<int:pk>/', views.gas_filling_batchnum, name='gas_filling_batchnum'),
    path('filling/recycle/<int:pk>/', views.gas_filling_recyclenum, name='gas_filling_recyclenum'),
    path('filling/heelweight/<int:pk>/', views.gas_filling_heelweight, name='gas_filling_heelweight'),
    path('filling/heelweight_b/<int:pk>/', views.gas_filling_heelweight_b, name='gas_filling_heelweight_b'),
    path('filling/connectionweight/<int:pk>/', views.gas_filling_connectionweight, name='gas_filling_connectionweight'),
    path('filling/endweight/<int:pk>/', views.gas_filling_endweight, name='gas_filling_endweight'),
    path('filling/pulledweight/<int:pk>/', views.gas_filling_pulledweight, name='gas_filling_pulledweight'),
    path('filling/finalweight/<int:pk>/', views.gas_filling_finalweight, name='gas_filling_finalweight'),
    path('filling/continue/<int:pk>/', views.continue_filling, name='continue_filling'),
    path('filling/getweight/', views.get_weight, name='get_weight'),
    path('filling/abandon/<int:pk>/', views.continue_filling, name='abandon'),  # TODO!!!!

    path('filling/table/', views.gas_filling_table, name='gas_filling_table'),
    path('filling/show/<int:pk>/', views.filling_show, name='filling_show'),
    path('filling/edit/<int:pk>/', views.filling_edit, name='filling_edit'),

    path('batch/new_batch/<int:pk>/<int:prev_batch>/', views.new_batch, name='gas_filling_newbatch'),
    path('batch/', views.batch_list, name='batch_list'),

    path('recycle/new_recycle/<int:pk>/<int:prev_recycle>/', views.new_recycle, name='gas_filling_newrecycle'),
    path('recycle/', views.recycle_list, name='recycle_list'),

    path('cylinder/', views.cylinder_list, name='cylinder_list'),
    path('cylinder/show/<int:pk>/', views.cylinder_show, name='cylinder_show'),
    path('cylinder/create/<str:barcode>/<int:orderline_id>/', views.cylinder_create, name='cylinder_create'),
    path('cylinder/edit/<int:pk>/', views.cylinder_edit, name='cylinder_edit'),

    path('order/', views.order_list, name='order_list'),
    path('order/create/', views.order_create, name='order_create'),
    path('order/<int:pk>/', views.order_show, name='order_show'),
    path('order/<int:pk>/edit/', views.order_edit, name='order_edit'),
    path('order/<int:pk>/status/', views.order_status, name='order_status'),
    path('order/new_orderline/<int:order_id>/', views.orderline_create, name='orderline_create'),
    path('order/edit_orderline/<int:orderline_id>/', views.orderline_edit, name='orderline_edit'),


    path('pdfcreate/', views.pdf_create, name='pdf_create'),


    
]


"""
urlpatterns = [
    path('orders/', views.order_test, name='order_test'),
]
"""