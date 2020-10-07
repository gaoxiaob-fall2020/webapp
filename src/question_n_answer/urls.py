from django.urls import path
from .views import QuestionList, QuestionDetail, AnswerList, AnswerDetail


urlpatterns = [
    path('questions/', QuestionList.as_view(), name='get_all_questions'),
    path('question/', QuestionList.as_view(), name='post_a_question'),
    path('question/<question_id>/', QuestionDetail.as_view(), name='get_put_del_a_question'),
    path('question/<question_id>/answer/', AnswerList.as_view(), name='post_an_answer'),
    path('question/<question_id>/answer/<answer_id>/', AnswerDetail.as_view(), name='get_put_del_an_answer'),
]