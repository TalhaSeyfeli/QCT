from django.urls import path
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    path('', views.send_view, name='send'), 
    # Yeni alıcı rotamız. <str:room_uuid> ile URL'deki odayı değişkene atıyoruz.
    path('al/<str:room_uuid>/', views.receive_view, name='receive'),
    # PWA Dosyalarını Kök Dizinden (Root) Servis Etme Ayarları
    path('manifest.json', TemplateView.as_view(template_name="qct_app/manifest.json", content_type='application/json'), name='manifest'),
    path('service-worker.js', TemplateView.as_view(template_name="qct_app/service-worker.js", content_type='application/javascript'), name='service-worker'),
]