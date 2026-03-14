from django.urls import path
from . import views

urlpatterns = [
    path('', views.send_view, name='send'), 
    # Yeni alıcı rotamız. <str:room_uuid> ile URL'deki odayı değişkene atıyoruz.
    path('al/<str:room_uuid>/', views.receive_view, name='receive'),
]