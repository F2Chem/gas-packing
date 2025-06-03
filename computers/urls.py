from django.urls import path

from util.util import add_std_to_paths

from . import views

urlpatterns = [
    path("pdf", views.pdf_test, name="pdf_test"),
    path("device/all", views.device_list_all, name="device_list_all"),
    path("computer/all", views.computer_list_all, name="computer_list_all"),

    path("cyber_notes/", views.cyber_notes, name="cyber_notes"),
    path("cra/pdf", views.cra_pdf, name="cra_pdf"),
    path("cra/<int:obj_id>/clone", views.cra_clone, name="cra_clone"),
    path("cra/<int:obj_id>/next", views.cra_next, name="cra_next"),
    path("cra/<int:obj_id>/edit_next", views.cra_edit_next, name="cra_edit_next"),
    #path("cra/int", views.cra_interpolate, name="cra_interpolate"),
]

add_std_to_paths(urlpatterns, views, ['target', 'static', 'device', 'computer', 'cra'])
