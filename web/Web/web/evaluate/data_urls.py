from django.urls import path

from web.evaluate import data_views

app_name = "evaluate"

urlpatterns = [

    # Ajax views
    path('user_reported_and_found_relevant_documents/',
         data_views.DataAJAXView.as_view(),
         name='user_reported_and_found_relevant_documents'),

]
