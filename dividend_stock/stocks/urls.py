from django.urls import path
from . import views

urlpatterns = [
    path('main/',views.main, name="main"),
    path('high/',views.high, name="high"),
    path('middle/',views.middle, name="middle"),
    path('<str:ticker>/',views.detail, name="detail"),
]