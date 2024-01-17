from django.urls import path
from . import views

app_name = 'predict'

urlpatterns = [
    path('', views.prediction_page, name="prediction_page"),
    path('iris/', views.iris, name="iris"),
    path('results/', views.view_results, name='results'),
    path('life_style/', views.life_style_page, name="life_style_page"),
    path('life_style_predict/', views.life_style, name="life_style"),
]