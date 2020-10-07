from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()

class Category(models.Model):
    category_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.CharField(max_length=125)


class Question(models.Model):
    question_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_timestamp = models.DateTimeField(default=timezone.now, editable=False)
    updated_timestamp = models.DateTimeField(default=timezone.now, editable=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, editable=False, null=True)
    question_text = models.TextField()
    categories = models.ManyToManyField(Category, related_name='questions', blank=True)
    # answers


class Answer(models.Model):
    answer_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.ForeignKey(Question, related_name='answers', on_delete=models.CASCADE)
    created_timestamp = models.DateTimeField(auto_now_add=timezone.now)
    updated_timestamp = models.DateTimeField(auto_now=timezone.now)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    answer_text = models.TextField()


