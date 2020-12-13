from django.conf.urls import include
from django.urls import path

from web.evaluate import views

app_name = "evaluate"

urlpatterns = [
    path('', views.EvaluateMainView.as_view(),
         name='main'),

    path('data/', include('web.evaluate.data_urls', namespace='data')),
]
