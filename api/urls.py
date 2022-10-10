from django.urls import path

from . import views


app_name = 'diary'
urlpatterns = [
    path('ticker', views.ticker),
    path('exchanges',views.exchanges),
    path('chart',views.chart)
]
