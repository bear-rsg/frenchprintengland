from django.urls import path
from . import views, apps

app_name = apps.app_name

urlpatterns = [
    path('', views.WelcomeTemplateView.as_view(), name='welcome'),
    path('team/', views.TeamTemplateView.as_view(), name='team'),
    path('introduction/', views.IntroductionTemplateView.as_view(), name='introduction'),
    path('resources/', views.ResourcesTemplateView.as_view(), name='resources'),
    path('accessibility/', views.AccessibilityTemplateView.as_view(), name='accessibility'),
    path('cookies/', views.CookiesTemplateView.as_view(), name='cookies'),
]
