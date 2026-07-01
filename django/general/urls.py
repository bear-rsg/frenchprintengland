from django.urls import path
from . import views, apps

app_name = apps.app_name

urlpatterns = [
    path('', views.WelcomeTemplateView.as_view(), name='welcome'),
    path('about/', views.AboutTemplateView.as_view(), name='about'),
    path('transcriptions/', views.TranscriptionsTemplateView.as_view(), name='transcriptions'),
    path('resources/', views.ResourcesTemplateView.as_view(), name='resources'),
    path('accessibility/', views.AccessibilityTemplateView.as_view(), name='accessibility'),
    path('cookies/', views.CookiesTemplateView.as_view(), name='cookies'),
]
