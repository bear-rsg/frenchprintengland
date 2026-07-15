from django.urls import path
from . import views, apps

app_name = apps.app_name

urlpatterns = [
    # Texts
    path('texts/', views.TextListView.as_view(), name='text-list'),
    path('texts/<pk>/', views.TextDetailView.as_view(), name='text-detail'),
    # Export Data
    path('export/excel/', views.export_excel, name='export-excel'),
]
