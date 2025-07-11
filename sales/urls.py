from django.urls import path

from util.util import add_std_to_paths

from . import views

urlpatterns = [
    path("zone/", views.zone_list, name="zone"),
    path("zone/<int:obj_id>", views.zone_detail, name="zone_detail"),
    path("zone/<int:obj_id>/create_customer", views.zone_create_customer, name="zone_create_customer"),
    path("customer/<int:obj_id>/create_order", views.customer_create_order, name="customer_create_order"),
    path("customer/<int:obj_id>/assign_specs", views.customer_assign_specs, name="customer_assign_specs"),
    path("customer/assigned_specs", views.customer_assigned_specs, name="customer_assigned_specs"),
    path("order/<int:obj_id>/pdf", views.order_pdf, name="order_pdf"),
    path("order/<int:obj_id>/finalise", views.order_finalise, name="order_finalise"),
]
add_std_to_paths(urlpatterns, views, ['customer', 'order'])