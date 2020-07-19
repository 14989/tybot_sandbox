from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name="landing_page"),
    path('change_table', views.change_table, name="change_table"),
    path('roadmap', views.roadmap, name="roadmap"),
    path('company', views.company, name="company"),
    path('country', views.country, name="country"),
    path('unknown', views.unknown, name="unknown"),
    path('lower', views.lower, name="lower"),
    path('broken', views.broken, name="broken"),
    path('all', views.all, name="all")
]