from django.urls import path

from web.core import views

app_name = "core"

urlpatterns = [
    path('', views.Home.as_view(),
         name='home'),
    path('sessions/', views.SessionListView.as_view(),
         name='sessions'),
    path('practice/',
         views.PracticeView.as_view(),
         name='practice'),
    path('practice_complete/', views.PracticeCompleteView.as_view(),
         name='practice_complete'),

    # Ajax views
    path('post_ctrlf/', views.CtrlFAJAXView.as_view(),
         name='post_ctrlf'),
    path('post_find_keystroke/', views.FindKeystrokeAJAXView.as_view(),
         name='post_find_keystroke'),
    path('post_visit/', views.VisitAJAXView.as_view(),
         name='post_visit'),
    path('post_log/', views.MessageAJAXView.as_view(),
         name='post_log_msg'),
    path('get_single_doc/', views.GetDocAJAXView.as_view(),
         name='get_single_doc'),

    path('get_session_details/', views.SessionDetailsAJAXView.as_view(),
         name='get_session_details'),
    path('share_session_view/', views.SessionShareView.as_view(),
         name='share_session'),
]
