from django.urls import path
from util.util import add_std_to_paths
from . import views

app_name = "gas_filling"

urlpatterns = [
    path('', views.gas_filling_home, name='gas_filling_home'),
    path('filling/', views.gas_filling, name='gas_filling_filling'),
    path('list/', views.gas_filling_list, name='gas_filling_list'),
    path('show/', views.gas_filling_show, name='gas_filling_show'),

    path("cylinder", views.cylinder_index, name="cylinder_index"),
    path("cylinder/<int:obj_id>", views.cylinder_view, name="cylinder_view"),
    path("cylinder/<int:obj_id>/edit", views.cylinder_edit, name="cylinder_edit"),

    path('filling/table/', views.gas_filling_table, name='gas_filling_table'),


]

