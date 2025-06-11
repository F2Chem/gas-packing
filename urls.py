#gasfilling

from django.urls import path
from util.util import add_std_to_paths
from . import views

urlpatterns = [
    path("", views.gas_filling, name="gas_filling"),
    path("cylinder", views.cylinder_index, name="cylinder_index"),
    path("cylinder/<int:obj_id>", views.cylinder_view, name="cylinder_view"),
    path("cylinder/<int:obj_id>/edit", views.cylinder_edit, name="cylinder_edit"),
    path("gas_filling/", views.gas_filling, name ='gas_filling'),
]

