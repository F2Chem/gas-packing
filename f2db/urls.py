from django.contrib import admin
from django.urls import include, path

from . import views

urlpatterns = [
    path('computers/', include("computers.urls")),
    path('gas_filling/', include("gas_filling.urls")),
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path("index.html", views.home, name="home"),
    path("", views.home, name="home"),
]



"""
Note: accounts is built in and givs these URLs
accounts/ login/ [name='login']
accounts/ logout/ [name='logout']
accounts/ password_change/ [name='password_change']
accounts/ password_change/done/ [name='password_change_done']
accounts/ password_reset/ [name='password_reset']
accounts/ password_reset/done/ [name='password_reset_done']
accounts/ reset/<uidb64>/<token>/ [name='password_reset_confirm']
accounts/ reset/done/ [name='password_reset_complete']
"""