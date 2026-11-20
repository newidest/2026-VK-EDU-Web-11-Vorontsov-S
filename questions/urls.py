from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('hot/', views.hot, name='hot'),
    path('tag/<str:tag_name>/', views.tag, name='tag'),
    path('question/<int:question_id>/', views.question, name='question'),
    path('ask/', views.ask, name='ask'),
    path('mark_correct/<int:question_id>/<int:answer_id>/', views.mark_correct_answer, name='mark_correct_answer'),
    path('vote/question/<int:question_id>/<str:vote_type>/', views.vote_question, name='vote_question'),
    path('vote/answer/<int:answer_id>/<str:vote_type>/', views.vote_answer, name='vote_answer'),
]