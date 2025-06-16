from django.urls import path
from util.util import add_std_to_paths
from . import views

app_name = "gas_filling"

urlpatterns = [
    path("", views.gas_filling, name="gas_filling"),
    path('all/', views.filling_table, name='gas_filling_all'),
    path("cylinder", views.cylinder_index, name="cylinder_index"),
    path("cylinder/<int:obj_id>", views.cylinder_view, name="cylinder_view"),
    path("cylinder/<int:obj_id>/edit", views.cylinder_edit, name="cylinder_edit"),
    path('table/', views.filling_table, name='filling_table'),

]

