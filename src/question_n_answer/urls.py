from django.urls import path

from .views import AnswerDetail, AnswerList, QuestionDetail, QuestionList, FileList

urlpatterns = [
    path('questions/', QuestionList.as_view(), name='get_all_questions'),
    path('question/', QuestionList.as_view(), name='post_a_question'),
    path(
        'question/<question_id>/',
        QuestionDetail.as_view(),
        name='get_put_del_a_question'
    ),
    path(
        'question/<question_id>/answer/',
        AnswerList.as_view(),
        name='post_an_answer'
    ),
    path(
        'question/<question_id>/answer/<answer_id>/',
        AnswerDetail.as_view(),
        name='get_put_del_an_answer'
    ),
    path(
        'question/<question_id>/file/',
        FileList.as_view(),
        name='post_f_to_q'
    ),
    path(
        'question/<question_id>/file/<file_id>/',
        FileList.as_view(),
        name='del_f_from_q'
    ),
    path(
        'question/<question_id>/answer/<answer_id>/file/',
        FileList.as_view(),
        name='post_f_to_a'
    ),
    path(
        'question/<question_id>/answer/<answer_id>/file/<file_id>/',
        FileList.as_view(),
        name='post_f_from_a'
    ),
]
