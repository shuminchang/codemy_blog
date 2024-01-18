from django.urls import path
from . import views

app_name = 'predict'

urlpatterns = [
    path('', views.prediction_page, name="prediction_page"),
    path('iris_predict/', views.iris_prediction_page, name="iris_prediction_page"),
    path('iris_results/', views.view_iris_results, name='iris_results'),
    path('iris_process/', views.iris_process, name="iris_process"),
    path('life_style_predict/', views.life_style_prediction_page, name="life_style_prediction_page"),
    path('life_style_process/', views.life_style_process, name="life_style_process"),
]